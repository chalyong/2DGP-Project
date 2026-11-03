from pico2d import load_image
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT
from transitions import Machine


class Player:
    def __init__(self):
        self.x = 400
        self.y = 300
        self.speed = 3
        self.frame = 0
        self.frame_timer = 0
        self.direction = "right"
        self.pressed_keys = set()
        self.idle_image = load_image("assets/player/player_idle_right.png")
        self.run_image = load_image("assets/player/player_walk_right.png")
        self.machine = Machine(
            model=self,
            states=["IDLE", "RUN"],
            initial="IDLE",
            auto_transitions=False,
        )
        self.machine.add_transition("start_running", "IDLE", "RUN")
        self.machine.add_transition("stop_running", "RUN", "IDLE")

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            self.pressed_keys.add(event.key)
        elif event.type == SDL_KEYUP and event.key in (SDLK_LEFT, SDLK_RIGHT):
            self.pressed_keys.discard(event.key)

        self._update_state()

    def _update_state(self):
        is_running = bool(self.pressed_keys)
        if is_running and self.state == "IDLE":
            self.start_running()
        elif not is_running and self.state == "RUN":
            self.stop_running()

    def update(self):
        if self.state == "RUN":
            if SDLK_LEFT in self.pressed_keys:
                self.x -= self.speed
                self.direction = "left"
            elif SDLK_RIGHT in self.pressed_keys:
                self.x += self.speed
                self.direction = "right"

        self.frame_timer += 1
        frame_interval = 6 if self.state == "RUN" else 12
        if self.frame_timer >= frame_interval:
            self.frame = (self.frame + 1) % 4
            self.frame_timer = 0

    def draw(self):
        image = self.run_image if self.state == "RUN" else self.idle_image
        flip = "h" if self.direction == "left" else ""
        image.clip_composite_draw(
            self.frame * 64,
            0,
            64,
            64,
            0,
            flip,
            self.x,
            self.y,
        )
