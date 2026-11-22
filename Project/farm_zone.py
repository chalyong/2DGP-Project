from pico2d import get_time, load_font, load_image
from sdl2 import SDL_KEYDOWN, SDLK_SPACE

import camera
import farm
import game_state


class FarmZone:
    plow_image = None
    locked_image = None
    sprinkler_image = None
    crop_images = {}
    font = None

    def __init__(self, crop, player):
        self.crop = crop
        self.player = player
        self.notification = None
        self.notification_started = 0
        if FarmZone.plow_image is None:
            FarmZone.plow_image = load_image("assets/farm_tile/plow.png")
            FarmZone.locked_image = load_image("assets/farm_tile/locked_plow.png")
            FarmZone.sprinkler_image = load_image("assets/farm_tile/sprinkler.png")
        if FarmZone.font is None:
            FarmZone.font = load_font(r"C:\Windows\Fonts\consolab.ttf", 14)
        if crop not in FarmZone.crop_images:
            FarmZone.crop_images[crop] = load_image(
                f"assets/farm_tile/crop_{crop}.png"
            )
        self.crop_image = FarmZone.crop_images[crop]

    def handle_event(self, event):
        if event.type != SDL_KEYDOWN or event.key != SDLK_SPACE:
            return
        if not game_state.farm_unlocked[self.crop]:
            return
        index = farm.cell_at(self.crop, self.player.x, self.player.y)
        if index is None or index == farm.SPRINKLER_CELL:
            return
        key = (self.crop, index)
        now = get_time()
        slot = game_state.crop_slots.get(key)
        if slot is None:
            game_state.crop_slots[key] = {
                "planted_at": now,
                "harvested_at": None,
            }
            return
        if farm.crop_stage(slot, now) == farm.READY_STAGE:
            game_state.collected_items[self.crop] += 1
            slot["harvested_at"] = now
            self.notification = f"{self.crop.upper()} * 1"
            self.notification_started = now

    def update(self):
        pass

    def draw(self):
        cx, cy = farm.ZONES[self.crop]
        if game_state.farm_unlocked[self.crop]:
            image = FarmZone.plow_image
        else:
            image = FarmZone.locked_image
        image.draw(
            cx - camera.x,
            cy - camera.y,
            farm.PLOW_WIDTH,
            farm.PLOW_HEIGHT,
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
        self._draw_notification()

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
        for (crop, index), slot in game_state.crop_slots.items():
            if crop != self.crop:
                continue
            stage = farm.crop_stage(slot, now)
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
