"""장면 장식 오브젝트: 건물 외관·출입구·상인 (이미지 + 좌표 드로우)."""
from pico2d import get_time, load_image

import camera
import game_state


class Building:
    def __init__(self, image_path, x, y=325):
        self.image = load_image(image_path)
        self.x = x
        self.y = y

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x - camera.x, self.y - camera.y)


class MineExit:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        if MineExit.image is None:
            MineExit.image = load_image("assets/buildings/mine_exit.png")

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x - camera.x, self.y - camera.y)


class TunnelExit:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        if TunnelExit.image is None:
            TunnelExit.image = load_image("assets/buildings/tunnel_exit.png")

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x - camera.x, self.y - camera.y)


FARM_EXIT_DRAW = (300, 158)


class FarmExit:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        if FarmExit.image is None:
            FarmExit.image = load_image("assets/buildings/farm_exit.png")
        self.image = FarmExit.image

    def update(self):
        pass

    def draw(self):
        self.image.draw(
            self.x - camera.x,
            self.y - camera.y,
            *FARM_EXIT_DRAW,
        )


class MineMerchant:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.frame_timer = 0
        if MineMerchant.image is None:
            MineMerchant.image = load_image(
                "assets/npc/mine_merchant_idle.png"
            )

    def update(self):
        self.frame_timer += 1
        if self.frame_timer >= 12:
            self.frame = (self.frame + 1) % 4
            self.frame_timer = 0

    def draw(self):
        self.image.clip_composite_draw(
            self.frame * 64,
            0,
            64,
            64,
            0,
            "",
            self.x - camera.x,
            self.y - camera.y,
            56,
            64,
        )


class RanchExit:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        if RanchExit.image is None:
            RanchExit.image = load_image("assets/buildings/ranch_exit.png")

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x - camera.x, self.y - camera.y)


# ranch_shopkeeper.png: 균일 4프레임 64x64 아이들 시트
RANCH_MERCHANT_FRAMES = (
    (0, 0, 64, 64),
    (64, 0, 64, 64),
    (128, 0, 64, 64),
    (192, 0, 64, 64),
)
RANCH_MERCHANT_FRAME_DURATION = 0.25


class RanchMerchant:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.frame_timer = 0.0
        self.last_update_time = get_time()
        if RanchMerchant.image is None:
            RanchMerchant.image = load_image("assets/npc/ranch_shopkeeper.png")
        self.image = RanchMerchant.image

    def update(self):
        current_time = get_time()
        delta_time = max(0.0, current_time - self.last_update_time)
        self.last_update_time = current_time
        self.frame_timer += delta_time
        while self.frame_timer >= RANCH_MERCHANT_FRAME_DURATION:
            self.frame = (self.frame + 1) % len(RANCH_MERCHANT_FRAMES)
            self.frame_timer -= RANCH_MERCHANT_FRAME_DURATION

    def draw(self):
        left, bottom, width, height = RANCH_MERCHANT_FRAMES[self.frame]
        self.image.clip_composite_draw(
            left,
            bottom,
            width,
            height,
            0,
            "",
            self.x - camera.x,
            self.y - camera.y,
            width,
            height,
        )


# 교배 전문가 (breeder_idle.png 균일 4프레임 64x64 — 보유 시에만 표시)
class Breeder:
    image = None

    def __init__(self, animal, x, y):
        self.animal = animal
        self.x = x
        self.y = y
        self.frame = 0
        self.frame_timer = 0.0
        self.last_update_time = get_time()
        if Breeder.image is None:
            Breeder.image = load_image("assets/npc/breeder_idle.png")
        self.image = Breeder.image

    def update(self):
        if not game_state.breeders.get(self.animal):
            return
        current_time = get_time()
        delta_time = max(0.0, current_time - self.last_update_time)
        self.last_update_time = current_time
        self.frame_timer += delta_time
        while self.frame_timer >= 0.25:
            self.frame = (self.frame + 1) % 4
            self.frame_timer -= 0.25

    def draw(self):
        if not game_state.breeders.get(self.animal):
            return
        self.image.clip_composite_draw(
            self.frame * 64,
            0,
            64,
            64,
            0,
            "",
            self.x - camera.x,
            self.y - camera.y,
            64,
            64,
        )


# farm_merchant_idle.png 4프레임 아이들 시트 (left, bottom, width, height)
FARM_MERCHANT_FRAMES = (
    (0, 0, 161, 230),
    (169, 0, 156, 230),
    (331, 0, 154, 230),
    (493, 0, 156, 230),
)
FARM_MERCHANT_FRAME_DURATION = 0.25
FARM_MERCHANT_DRAW_HEIGHT = 90


class FarmMerchant:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.frame_timer = 0.0
        self.last_update_time = get_time()
        if FarmMerchant.image is None:
            FarmMerchant.image = load_image("assets/npc/farm_merchant_idle.png")
        self.image = FarmMerchant.image

    def update(self):
        current_time = get_time()
        delta_time = max(0.0, current_time - self.last_update_time)
        self.last_update_time = current_time
        self.frame_timer += delta_time
        while self.frame_timer >= FARM_MERCHANT_FRAME_DURATION:
            self.frame = (self.frame + 1) % len(FARM_MERCHANT_FRAMES)
            self.frame_timer -= FARM_MERCHANT_FRAME_DURATION

    def draw(self):
        left, bottom, width, height = FARM_MERCHANT_FRAMES[self.frame]
        self.image.clip_composite_draw(
            left,
            bottom,
            width,
            height,
            0,
            "",
            self.x - camera.x,
            self.y - camera.y,
            width * FARM_MERCHANT_DRAW_HEIGHT / height,
            FARM_MERCHANT_DRAW_HEIGHT,
        )
