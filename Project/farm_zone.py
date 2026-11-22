from pico2d import get_time, load_font, load_image
from sdl2 import SDL_KEYDOWN, SDLK_SPACE

import camera
import farm
import farmer
import game_state

FARMER_FRAME_DURATION = 0.15
# 심기·수확 모션은 전체 3초 동안 1사이클 (4프레임 × 0.75초)
FARMER_HARVEST_FRAME_DURATION = farmer.MOTION_SECONDS / 4


class FarmZone:
    plow_image = None
    locked_image = None
    sprinkler_image = None
    crop_images = {}
    font = None
    farmer_idle = None
    farmer_walk = None
    farmer_harvest = None

    def __init__(self, crop, player):
        self.crop = crop
        self.player = player
        self.pending = None
        self.notification = None
        self.notification_started = 0
        if FarmZone.plow_image is None:
            FarmZone.plow_image = load_image("assets/farm_tile/plow.png")
            FarmZone.locked_image = load_image("assets/farm_tile/locked_plow.png")
            FarmZone.sprinkler_image = load_image("assets/farm_tile/sprinkler.png")
        if FarmZone.font is None:
            FarmZone.font = load_font(r"C:\Windows\Fonts\consolab.ttf", 14)
        if FarmZone.farmer_idle is None:
            FarmZone.farmer_idle = load_image("assets/npc/farmer_idle.png")
            FarmZone.farmer_walk = load_image("assets/npc/farmer_walk_right.png")
            FarmZone.farmer_harvest = load_image("assets/npc/farmer_harvest.png")
        if crop not in FarmZone.crop_images:
            FarmZone.crop_images[crop] = load_image(
                f"assets/farm_tile/crop_{crop}.png"
            )
        self.crop_image = FarmZone.crop_images[crop]

    def handle_event(self, event):
        if event.type != SDL_KEYDOWN or event.key != SDLK_SPACE:
            return
        if self.player.movement_locked or self.player.farm_work:
            return
        if not game_state.farm_unlocked[self.crop]:
            return
        index = farm.cell_at(self.crop, self.player.x, self.player.y)
        if index is None or index == farm.SPRINKLER_CELL:
            return
        if self.pending is not None:
            return
        key = (self.crop, index)
        now = get_time()
        slot = game_state.crop_slots.get(key)
        stage_seconds = game_state.crop_stage_seconds(farm.STAGE_SECONDS)
        if slot is None:
            kind = "plant"
        elif farm.crop_stage(slot, now, stage_seconds) == farm.READY_STAGE:
            kind = "harvest"
        else:
            return
        # 플레이어도 농부와 같은 작업 모션을 먼저 재생한다
        if not self.player.start_farm_work(farmer.MOTION_SECONDS):
            return
        self.pending = (kind, index, now + farmer.MOTION_SECONDS)

    def update(self):
        if self.pending is None:
            return
        kind, index, done_at = self.pending
        now = get_time()
        if now < done_at:
            return
        self.pending = None
        amount = game_state.harvest_yield(self.crop)
        applied = game_state.apply_farm_work(self.crop, kind, index, now)
        if applied and kind == "harvest":
            self.notification = f"{self.crop.upper()} * {amount}"
            self.notification_started = now

    def draw(self):
        if game_state.farm_unlocked[self.crop]:
            image = FarmZone.plow_image
        else:
            image = FarmZone.locked_image
        # 5x5 각 칸에 개별 경작지, 해금 전 구역은 locked_plow
        for index in range(farm.GRID * farm.GRID):
            x0, y0, x1, y1 = farm.cell_rect(self.crop, index)
            image.draw(
                (x0 + x1) / 2 - camera.x,
                (y0 + y1) / 2 - camera.y,
                farm.CELL_WIDTH,
                farm.CELL_HEIGHT,
            )
        self._draw_crops()
        # 스프링클러: 구역 중앙 칸 (잠긴 구역에도 시설은 존재)
        x0, y0, x1, y1 = farm.sprinkler_rect(self.crop)
        FarmZone.sprinkler_image.draw(
            (x0 + x1) / 2 - camera.x,
            (y0 + y1) / 2 - camera.y,
            54,
            70,
        )
        self._draw_farmers()
        self._draw_notification()

    def _draw_farmers(self):
        now = get_time()
        for f in farmer.states:
            if f["crop"] != self.crop:
                continue
            delta = max(0.0, now - f.setdefault("anim_time", now))
            f["anim_time"] = now
            in_motion = now < f.get("motion_until", 0.0)
            frame_duration = (
                FARMER_HARVEST_FRAME_DURATION if in_motion else FARMER_FRAME_DURATION
            )
            f["frame_timer"] += delta
            while f["frame_timer"] >= frame_duration:
                f["frame"] = (f["frame"] + 1) % 4
                f["frame_timer"] -= frame_duration
            if in_motion:
                image = FarmZone.farmer_harvest
            elif f["moving"]:
                image = FarmZone.farmer_walk
            else:
                image = FarmZone.farmer_idle
            flip = "h" if f["facing"] == "left" else ""
            image.clip_composite_draw(
                f["frame"] * 64,
                0,
                64,
                64,
                0,
                flip,
                f["x"] - camera.x,
                f["y"] - camera.y,
                56,
                64,
            )

    def _draw_notification(self):
        if not self.notification:
            return
        elapsed = get_time() - self.notification_started
        duration = 1.0
        if elapsed >= duration:
            self.notification = None
            return
        progress = elapsed / duration
        rise = 30 * progress
        start_color = (255, 239, 177)
        end_color = (95, 95, 95)
        color = tuple(
            int(start + (end - start) * progress)
            for start, end in zip(start_color, end_color)
        )
        FarmZone.font.draw(
            self.player.x - camera.x - 30,
            self.player.y - camera.y + 45 + rise,
            self.notification,
            color,
        )

    def _draw_crops(self):
        now = get_time()
        stage_seconds = game_state.crop_stage_seconds(farm.STAGE_SECONDS)
        for (crop, index), slot in game_state.crop_slots.items():
            if crop != self.crop:
                continue
            stage = farm.crop_stage(slot, now, stage_seconds)
            if stage is None:
                continue
            x0, y0, x1, y1 = farm.cell_rect(crop, index)
            self.crop_image.clip_composite_draw(
                stage * 48,
                0,
                48,
                48,
                0,
                "",
                (x0 + x1) / 2 - camera.x,
                (y0 + y1) / 2 - camera.y,
                44,
                44,
            )
