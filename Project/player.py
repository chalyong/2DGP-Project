from pico2d import get_time, load_image
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT
from transitions import Machine

import camera

SPRITE_FRAME_SIZE = 64
MINING_FRAME_COUNT = 7
SPRITE_DRAW_WIDTH = 56
SPRITE_DRAW_HEIGHT = 64
PLAYER_HEIGHT_METERS = SPRITE_DRAW_HEIGHT * camera.METERS_PER_PIXEL
WALK_SPEED_KMH = 10
SPRITE_TRAVEL_METERS = 1.2
RUN_FRAME_COUNT = 4
WALK_SPEED_METERS_PER_SECOND = WALK_SPEED_KMH / 3.6
WALK_SPEED_PIXELS_PER_SECOND = (
    WALK_SPEED_METERS_PER_SECOND * camera.PIXELS_PER_METER
)
RUN_FRAME_DURATION_SECONDS = (
    SPRITE_TRAVEL_METERS
    / WALK_SPEED_METERS_PER_SECOND
    / RUN_FRAME_COUNT
)
IDLE_FRAME_DURATION_SECONDS = 0.12
MINING_DURATION_SECONDS = 1.0
MINING_FRAME_DURATION_SECONDS = MINING_DURATION_SECONDS / MINING_FRAME_COUNT


class Player:
    idle_image = None
    run_image = None
    mining_image = None

    def __init__(self):
        self.x = 64
        self.y = 300
        self.speed = WALK_SPEED_PIXELS_PER_SECOND
        self.frame = 0
        self.frame_timer = 0.0
        self.last_update_time = get_time()
        self.direction = "right"
        self.pressed_keys = set()
        self.movement_locked = False
        if Player.idle_image is None:
            Player.idle_image = load_image("assets/player/player_idle_right.png")
        if Player.run_image is None:
            Player.run_image = load_image("assets/player/player_walk_right.png")
        if Player.mining_image is None:
            Player.mining_image = load_image(
                "assets/player/player_mining_right.png"
            )
        self.idle_image = Player.idle_image
        self.run_image = Player.run_image
        self.mining_image = Player.mining_image
        self.mining_frame_width = self.mining_image.w // MINING_FRAME_COUNT
        self.mining = False
        self.mining_frame = 0
        self.mining_frame_timer = 0.0
        self.machine = Machine(
            model=self,
            states=["IDLE", "RUN"],
            initial="IDLE",
            auto_transitions=False,
        )
        self.machine.add_transition("start_running", "IDLE", "RUN")
        self.machine.add_transition("stop_running", "RUN", "IDLE")

    def handle_event(self, event):
        if self.movement_locked:
            self.pressed_keys.clear()
            self._update_state()
            return

        if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            self.pressed_keys.add(event.key)
        elif event.type == SDL_KEYUP and event.key in (SDLK_LEFT, SDLK_RIGHT):
            self.pressed_keys.discard(event.key)

        self._update_state()

    def start_mining(self):
        if self.mining:
            return
        self.mining = True
        self.mining_frame = 0
        self.mining_frame_timer = 0.0
        self.pressed_keys.clear()
        self._update_state()

    def _update_state(self):
        is_running = bool(self.pressed_keys)
        if is_running and self.state == "IDLE":
            self.start_running()
        elif not is_running and self.state == "RUN":
            self.stop_running()

    def update(self):
        current_time = get_time()
        delta_time = max(0.0, current_time - self.last_update_time)
        self.last_update_time = current_time

        if self.movement_locked:
            self.pressed_keys.clear()
            self._update_state()

        if self.mining:
            self.mining_frame_timer += delta_time
            while (
                self.mining
                and self.mining_frame_timer >= MINING_FRAME_DURATION_SECONDS
            ):
                self.mining_frame += 1
                self.mining_frame_timer -= MINING_FRAME_DURATION_SECONDS
                if self.mining_frame >= MINING_FRAME_COUNT:
                    self.mining = False
                    self.mining_frame = 0
            return

        if self.state == "RUN":
            if SDLK_LEFT in self.pressed_keys:
                self.x = max(32, self.x - self.speed * delta_time)
                self.direction = "left"
            elif SDLK_RIGHT in self.pressed_keys:
                self.x = min(
                    camera.WORLD_WIDTH - 32, self.x + self.speed * delta_time
                )
                self.direction = "right"

        self.frame_timer += delta_time
        frame_duration = (
            RUN_FRAME_DURATION_SECONDS
            if self.state == "RUN"
            else IDLE_FRAME_DURATION_SECONDS
        )
        while self.frame_timer >= frame_duration:
            self.frame = (self.frame + 1) % 4
            self.frame_timer -= frame_duration

    def set_movement_locked(self, locked):
        self.movement_locked = locked
        if locked:
            self.pressed_keys.clear()
            self._update_state()

    def draw(self):
        if self.mining:
            self.mining_image.clip_composite_draw(
                self.mining_frame * self.mining_frame_width,
                0,
                self.mining_frame_width,
                self.mining_image.h,
                0,
                "h" if self.direction == "left" else "",
                self.x - camera.x+4,
                self.y - camera.y+ 8,
                SPRITE_DRAW_WIDTH + 28,
                SPRITE_DRAW_HEIGHT + 20,
            )
            return

        image = self.run_image if self.state == "RUN" else self.idle_image
        flip = "h" if self.direction == "left" else ""
        image.clip_composite_draw(
            self.frame * SPRITE_FRAME_SIZE,
            0,
            SPRITE_FRAME_SIZE,
            SPRITE_FRAME_SIZE,
            0,
            flip,
            self.x - camera.x,
            self.y - camera.y,
            SPRITE_DRAW_WIDTH,
            SPRITE_DRAW_HEIGHT,
        )
