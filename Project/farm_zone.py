from pico2d import load_image

import camera
import farm
import game_state


class FarmZone:
    plow_image = None
    locked_image = None
    sprinkler_image = None

    def __init__(self, crop):
        self.crop = crop
        if FarmZone.plow_image is None:
            FarmZone.plow_image = load_image("assets/farm_tile/plow.png")
            FarmZone.locked_image = load_image("assets/farm_tile/locked_plow.png")
            FarmZone.sprinkler_image = load_image("assets/farm_tile/sprinkler.png")

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
        # 스프링클러: 구역 중앙 칸 (잠긴 구역에도 시설은 존재)
        x0, y0, x1, y1 = farm.sprinkler_rect(self.crop)
        FarmZone.sprinkler_image.draw(
            (x0 + x1) / 2 - camera.x,
            (y0 + y1) / 2 - camera.y,
            54,
            70,
        )
