"""장면 장식 오브젝트: 건물 외관·출입구·상인 (이미지 + 좌표 드로우)."""
from pico2d import get_time, load_font, load_image

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


class BuffetExit:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        if BuffetExit.image is None:
            BuffetExit.image = load_image("assets/buildings/buffet_exit.png")

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x - camera.x, self.y - camera.y)


# 상인 공통: 균일 4프레임 64x64 아이들 시트 (목장·뷔페 공용)
MERCHANT_IDLE_FRAMES = (
    (0, 0, 64, 64),
    (64, 0, 64, 64),
    (128, 0, 64, 64),
    (192, 0, 64, 64),
)
MERCHANT_IDLE_FRAME_DURATION = 0.25


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
        while self.frame_timer >= MERCHANT_IDLE_FRAME_DURATION:
            self.frame = (self.frame + 1) % len(MERCHANT_IDLE_FRAMES)
            self.frame_timer -= MERCHANT_IDLE_FRAME_DURATION

    def draw(self):
        left, bottom, width, height = MERCHANT_IDLE_FRAMES[self.frame]
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


class BuffetShopkeeper:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.frame_timer = 0.0
        self.last_update_time = get_time()
        if BuffetShopkeeper.image is None:
            BuffetShopkeeper.image = load_image("assets/npc/buffet_shopkeeper.png")
        self.image = BuffetShopkeeper.image

    def update(self):
        current_time = get_time()
        delta_time = max(0.0, current_time - self.last_update_time)
        self.last_update_time = current_time
        self.frame_timer += delta_time
        while self.frame_timer >= MERCHANT_IDLE_FRAME_DURATION:
            self.frame = (self.frame + 1) % len(MERCHANT_IDLE_FRAMES)
            self.frame_timer -= MERCHANT_IDLE_FRAME_DURATION

    def draw(self):
        left, bottom, width, height = MERCHANT_IDLE_FRAMES[self.frame]
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


# buffet_chef.png: 균일 4프레임 64x64 아이들 시트 (상인과 동일 레이아웃)
class BuffetChef:
    image = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.frame_timer = 0.0
        self.last_update_time = get_time()
        if BuffetChef.image is None:
            BuffetChef.image = load_image("assets/npc/buffet_chef.png")
        self.image = BuffetChef.image

    def update(self):
        current_time = get_time()
        delta_time = max(0.0, current_time - self.last_update_time)
        self.last_update_time = current_time
        self.frame_timer += delta_time
        while self.frame_timer >= MERCHANT_IDLE_FRAME_DURATION:
            self.frame = (self.frame + 1) % len(MERCHANT_IDLE_FRAMES)
            self.frame_timer -= MERCHANT_IDLE_FRAME_DURATION

    def draw(self):
        left, bottom, width, height = MERCHANT_IDLE_FRAMES[self.frame]
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


class KitchenDishes:
    """주방 요리 공간: 제작 성공분을 아이콘+수량으로 진열 (뷔페_PRD 3.3)."""

    SPOTS = ((150, 650), (260, 650), (370, 650), (480, 650), (590, 650))
    ICON_SIZE = 48

    count_font = None

    def __init__(self):
        if KitchenDishes.count_font is None:
            KitchenDishes.count_font = load_font(
                r"C:\Windows\Fonts\consolab.ttf", 16
            )

    def update(self):
        pass

    def draw(self):
        import shop

        for (name, _), (x, y) in zip(game_state.RECIPES, self.SPOTS):
            count = game_state.cooked_items.get(name, 0)
            if count <= 0:
                continue
            shop.draw_item_icon(
                name,
                x - camera.x,
                y - camera.y,
                size=self.ICON_SIZE,
                prefer_item=True,
            )
            KitchenDishes.count_font.draw(
                x - camera.x + 26,
                y - camera.y - 30,
                f"x {count}",
                (255, 224, 120),
            )


class DiningFurniture:
    """식사 공간: 구매한 식탁·의자를 맵에 배치 (뷔페_PRD 3.2).

    식탁당 의자 2개를 좌우에 붙인다 (식탁 구매 규칙상 항상 식탁이 먼저 확보된다).
    """

    TABLE_SPOTS = ((200, 350), (440, 350), (680, 350), (320, 210), (560, 210))
    CHAIR_OFFSET = 56
    MAX_TABLES = len(TABLE_SPOTS)
    MAX_CHAIRS = MAX_TABLES * 2

    table_image = None
    chair_image = None

    def __init__(self):
        if DiningFurniture.table_image is None:
            DiningFurniture.table_image = load_image(
                "assets/buildings/buffet_table.png"
            )
        if DiningFurniture.chair_image is None:
            DiningFurniture.chair_image = load_image(
                "assets/buildings/buffet_chair.png"
            )

    def update(self):
        pass

    def draw(self):
        tables = min(
            game_state.buffet_facilities.get("table", 0),
            self.MAX_TABLES,
        )
        chairs = min(
            game_state.buffet_facilities.get("chair", 0),
            self.MAX_CHAIRS,
        )
        for index in range(tables):
            tx, ty = self.TABLE_SPOTS[index]
            DiningFurniture.table_image.draw(tx - camera.x, ty - camera.y)
        for chair_index in range(chairs):
            table_index = chair_index // 2
            tx, ty = self.TABLE_SPOTS[table_index]
            side = -1 if chair_index % 2 == 0 else 1
            DiningFurniture.chair_image.draw(
                tx + side * self.CHAIR_OFFSET - camera.x,
                ty - camera.y,
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
