from pico2d import get_time, load_font, load_image
from sdl2 import (
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDL_MOUSEBUTTONDOWN,
    SDL_MOUSEWHEEL,
    SDLK_LSHIFT,
    SDLK_RSHIFT,
    SDLK_SPACE,
)

import os

import camera
import game_state
import farmer
import miner


MAX_MINERS_PER_ZONE = 10

# ore selling (sell merchant): unit price, click sells 1, shift+click sells all
ORE_SELL_PRICES = {
    "stone": 5,
    "coal": 20,
    "iron": 60,
    "gold": 200,
}
SELL_PAGES = (
    ("stone", "coal", "iron"),
    ("gold",),
)

# 농사지 상점 상품 (F4에서 항목을 순차 추가)
FARM_SHOP_PAGES = [
    (
        ("STONE HOE", 200, "wheat+2", ("stone", 10), "farm_tool", None),
        ("IRON HOE", 600, "wheat+3, potato+2", ("iron", 10), "farm_tool", None),
        (
            "GOLD HOE",
            1500,
            "wheat+5, potato+3, strawberry+2",
            ("gold", 10),
            "farm_tool",
            None,
        ),
    ),
    (
        ("FERTILIZER", 300, "growth time -50%", None, "farm_tool", None),
        ("POTATO UNLOCK", 400, "potato zone open", None, "farm_unlock", "potato"),
        (
            "STRAWBERRY UNLOCK",
            800,
            "strawberry zone open",
            None,
            "farm_unlock",
            "strawberry",
        ),
    ),
    (
        ("WHEAT FARMER", 500, "wheat auto harvest", None, "farmer", "wheat"),
        ("POTATO FARMER", 800, "potato auto harvest", None, "farmer", "potato"),
        (
            "STRAWBERRY FARMER",
            1200,
            "strawberry auto harvest",
            None,
            "farmer",
            "strawberry",
        ),
    ),
]

# name, price, description, required ore (name, count) or None, kind, kind target
ITEM_PAGES = (
    (
        ("WOOD PICKAXE", 100, "stone+2", None, "tool", None),
        ("STONE PICKAXE", 300, "stone+3, coal+2", ("stone", 10), "tool", None),
        ("IRON PICKAXE", 800, "stone+5, coal+3, iron+2", ("coal", 10), "tool", None),
    ),
    (
        ("GOLD PICKAXE", 1500, "stone+10, coal+5, iron+3, gold+2", ("iron", 10), "tool", None),
        ("STONE MINER", 1000, "stone miner+1", None, "miner", "stone"),
        ("COAL MINER", 2500, "coal miner+1", None, "miner", "coal"),
    ),
    (
        ("IRON MINER", 5000, "iron miner+1", None, "miner", "iron"),
        ("GOLD MINER", 10000, "gold miner+1", None, "miner", "gold"),
        ("COAL TUNNEL PASS", 500, "coal mine open", None, "pass", "coal"),
    ),
    (
        ("IRON TUNNEL PASS", 1200, "iron mine open", None, "pass", "iron"),
        ("GOLD TUNNEL PASS", 3000, "gold mine open", None, "pass", "gold"),
    ),
)

# 상품명 -> 설명 (인벤토리 등 다른 화면에서 재사용)
ITEM_DESCRIPTIONS = {
    item[0]: item[2]
    for pages in (ITEM_PAGES, FARM_SHOP_PAGES)
    for page in pages
    for item in page
}

# 크롭 시트의 ready 프레임 / 농부 idle 첫 프레임
CROP_READY_CLIP = (3 * 48, 0, 48, 48)
FARMER_IDLE_CLIP = (0, 0, 64, 64)
# 인벤토리 작물용 item 에셋 (생성되지 않은 작물은 farm_tile 크롭 시트로 대체)
CROP_ITEM_ASSETS = {
    name: f"assets/item/{name}.png"
    for name in ("wheat", "potato", "strawberry")
    if os.path.exists(f"assets/item/{name}.png")
}
_icon_cache = {}
ICON_WIDTH = 42
ICON_MAX_HEIGHT = 60  # 세로로 긴 아이콘(광부 등)의 최대 높이


def item_image(name):
    """상품/아이템명에 해당하는 (이미지 경로, 크롭 좌표 or None)."""
    upper = name.upper()
    if upper.endswith("PICKAXE"):
        return "assets/item/pickaxe.png", None
    if upper.endswith("HOE"):
        return "assets/item/hoe.png", None
    if upper == "FERTILIZER":
        return "assets/item/fertilizer.png", None
    if "TUNNEL PASS" in upper:
        ore = upper.split()[0].lower()
        return f"assets/item/ore_{ore}.png", None
    if "UNLOCK" in upper:
        crop = upper.split()[0].lower()
        if crop in CROP_ITEM_ASSETS:
            return CROP_ITEM_ASSETS[crop], None
        return f"assets/farm_tile/crop_{crop}.png", CROP_READY_CLIP
    if "MINER" in upper:
        return "assets/npc/mine_miner_mining.png", miner.FRAMES[0]
    if "FARMER" in upper:
        return "assets/npc/farmer_idle.png", FARMER_IDLE_CLIP
    if upper.lower() in CROP_ITEM_ASSETS:
        return CROP_ITEM_ASSETS[upper.lower()], None
    if upper in ("WHEAT", "POTATO", "STRAWBERRY"):
        return f"assets/farm_tile/crop_{upper.lower()}.png", CROP_READY_CLIP
    if upper in ("STONE", "COAL", "IRON", "GOLD"):
        return f"assets/item/ore_{upper.lower()}.png", None
    return None, None


def draw_item_icon(name, x, y, size=ICON_WIDTH):
    """상품/아이템 아이콘을 (x, y) 중앙에 원본 비율 유지로 그린다.

    가로는 size, 세로는 ICON_MAX_HEIGHT 안에서 원본 종횡비를 맞춘다.
    (정사각 아이콘은 그대로 sizexsize, 세로로 긴 광부는 세로를 길게)
    """
    path, clip = item_image(name)
    if path is None:
        return False
    image = _icon_cache.get(path)
    if image is None:
        image = load_image(path)
        _icon_cache[path] = image
    if clip is None:
        source_width, source_height = image.w, image.h
    else:
        source_width, source_height = clip[2], clip[3]
    scale = min(size / source_width, ICON_MAX_HEIGHT / source_height)
    draw_width = source_width * scale
    draw_height = source_height * scale
    if clip is None:
        image.draw(x, y, draw_width, draw_height)
    else:
        image.clip_composite_draw(*clip, 0, "", x, y, draw_width, draw_height)
    return True


class Shop:
    panel = None
    title_font = None
    item_font = None
    description_font = None
    ore_images = {}

    def __init__(self, player, merchant, mode="buy", pages=None, title="MINING SHOP"):
        self.player = player
        self.merchant = merchant
        self.mode = mode
        self.pages = ITEM_PAGES if pages is None else pages
        self.title = title
        self.open = False
        self.page = 0
        self.page_change_time = -0.2
        self.message = None
        self.message_time = 0
        self.shift_held = False
        if Shop.panel is None:
            Shop.panel = load_image("assets/ui/shop_panel.png")
        if Shop.title_font is None:
            Shop.title_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 28)
        if Shop.item_font is None:
            Shop.item_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 18)
        if Shop.description_font is None:
            Shop.description_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 14)
        if not Shop.ore_images:
            for name in ("stone", "coal", "iron", "gold"):
                Shop.ore_images[name] = load_image(
                    f"assets/item/ore_{name}.png"
                )

    def handle_event(self, event):
        if (
            event.type == SDL_KEYDOWN
            and event.key in (SDLK_LSHIFT, SDLK_RSHIFT)
        ):
            self.shift_held = True
            return
        if (
            event.type == SDL_KEYUP
            and event.key in (SDLK_LSHIFT, SDLK_RSHIFT)
        ):
            self.shift_held = False
            return
        if (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and abs(self.player.x - self.merchant.x) <= 40
            and abs(self.player.y - self.merchant.y) <= 40
        ):
            self.open = not self.open
            self.player.set_movement_locked(self.open)
            if not self.open:
                self.page = 0
        elif (
            event.type == SDL_MOUSEWHEEL
            and self.open
            and get_time() - self.page_change_time >= 0.2
        ):
            if self._page_count() == 0:
                return
            if event.y < 0:
                self.page = min(self.page + 1, self._page_count() - 1)
            elif event.y > 0:
                self.page = max(self.page - 1, 0)
            else:
                return
            self.page_change_time = get_time()
        elif (
            event.type == SDL_MOUSEBUTTONDOWN
            and self.open
            and getattr(event, "button", 1) == 1
        ):
            y = camera.SCREEN_HEIGHT - event.y
            if self.mode == "sell":
                ores = SELL_PAGES[self.page]
                for index, ore in enumerate(ores):
                    row_y = 360 - index * 80
                    if 100 <= event.x < 700 and row_y - 40 <= y <= row_y + 20:
                        self._sell(ore, sell_all=self.shift_held)
                        break
            else:
                items = (
                    self.pages[self.page]
                    if self.page < len(self.pages)
                    else ()
                )
                for index, item in enumerate(items):
                    item_y = 360 - index * 80
                    if 100 <= event.x < 700 and item_y - 40 <= y <= item_y + 20:
                        self._buy(item)
                        break

    def _page_count(self):
        if self.mode == "sell":
            return len(SELL_PAGES)
        return len(self.pages)

    def _sell(self, ore, sell_all=False):
        owned = game_state.collected_items[ore]
        if owned <= 0:
            self.message = f"NO {ore.upper()}"
            self.message_time = get_time()
            return
        count = owned if sell_all else 1
        total = count * ORE_SELL_PRICES[ore]
        game_state.collected_items[ore] = owned - count
        game_state.money += total
        self.message = f"SOLD {ore.upper()} x{count}  +$ {total:,}"
        self.message_time = get_time()

    def _buy(self, item):
        name, price, description, requirement, kind, target = item
        if kind == "tool" and name in game_state.tools:
            self.message = "ALREADY OWNED"
            self.message_time = get_time()
            return
        if kind == "miner" and not game_state.open_tunnels[target]:
            self.message = f"OPEN {target.upper()} TUNNEL FIRST"
            self.message_time = get_time()
            return
        if (
            kind == "miner"
            and game_state.miners[target] >= MAX_MINERS_PER_ZONE
        ):
            self.message = (
                f"{target.upper()} MINER LIMIT "
                f"({MAX_MINERS_PER_ZONE})"
            )
            self.message_time = get_time()
            return
        if kind == "pass" and game_state.open_tunnels[target]:
            self.message = "ALREADY OPEN"
            self.message_time = get_time()
            return
        if kind == "farm_tool":
            if name in game_state.farm_tools:
                self.message = "ALREADY OWNED"
                self.message_time = get_time()
                return
            if name in game_state.HOE_LEVELS:
                position = game_state.HOE_LEVELS.index(name)
                if position > 0:
                    required = game_state.HOE_LEVELS[position - 1]
                    if required not in game_state.farm_tools:
                        self.message = f"BUY {required} FIRST"
                        self.message_time = get_time()
                        return
        if kind == "farm_unlock":
            if game_state.farm_unlocked[target]:
                self.message = "ALREADY OPEN"
                self.message_time = get_time()
                return
            if target == "strawberry" and not game_state.farm_unlocked["potato"]:
                self.message = "UNLOCK POTATO FIRST"
                self.message_time = get_time()
                return
        if kind == "farmer":
            if not game_state.farm_unlocked[target]:
                self.message = f"UNLOCK {target.upper()} ZONE FIRST"
                self.message_time = get_time()
                return
            if farmer.at_limit(target):
                self.message = (
                    f"{target.upper()} FARMER LIMIT ({farmer.MAX_PER_ZONE})"
                )
                self.message_time = get_time()
                return
        if game_state.money < price:
            self.message = "NOT ENOUGH MONEY"
            self.message_time = get_time()
            return
        if requirement:
            ore, count = requirement
            if game_state.collected_items[ore] < count:
                self.message = f"NEED {ore.upper()} x{count}"
                self.message_time = get_time()
                return
            game_state.collected_items[ore] -= count
        game_state.money -= price
        if kind == "tool":
            game_state.tools.append(name)
        elif kind == "miner":
            game_state.miners[target] += 1
        elif kind == "pass":
            game_state.open_tunnels[target] = True
            game_state.passes.append(f"{target.upper()} TUNNEL PASS")
        elif kind == "farm_tool":
            game_state.farm_tools.append(name)
        elif kind == "farm_unlock":
            game_state.farm_unlocked[target] = True
            game_state.passes.append(f"{target.upper()} UNLOCK")
        elif kind == "farmer":
            farmer.hire(target)
        self.message = f"PURCHASED {name}"
        self.message_time = get_time()

    def update(self):
        if self.message and get_time() - self.message_time >= 1.5:
            self.message = None

    def draw(self):
        if not self.open:
            return
        self.panel.draw_to_origin(40, 100)
        if self.mode == "sell":
            self._draw_sell_page()
        else:
            self._draw_buy_page()
        if self.message and get_time() - self.message_time < 1.5:
            self.item_font.draw(300, 170, self.message, (255, 150, 120))
        self.item_font.draw(150, 130, "MOUSE WHEEL: CHANGE PAGE", (180, 190, 205))
        self.item_font.draw(480, 130, "SPACE: CLOSE", (180, 190, 205))

    def _draw_sell_page(self):
        page_count = len(SELL_PAGES)
        self.title_font.draw(
            300,
            440,
            f"ORE MARKET  {self.page + 1}/{page_count}",
            (255, 239, 177),
        )
        for index, ore in enumerate(SELL_PAGES[self.page]):
            price = ORE_SELL_PRICES[ore]
            y = 360 - index * 80
            count = game_state.collected_items[ore]
            self.ore_images[ore].draw(120, y + 6, 32, 32)
            self.item_font.draw(165, y, ore.upper(), (235, 235, 235))
            self.item_font.draw(400, y, f"x {count}", (255, 224, 120))
            self.item_font.draw(560, y, "sell x1", (255, 224, 120))
            self.description_font.draw(
                520, y-20, 
                "shift+click: sell all", 
                (180, 190, 205))
            self.description_font.draw(
                165, y - 20,
                f"$ {price} / 1",
                (180, 190, 205),
            )

    def _draw_buy_page(self):
        page_count = len(self.pages)
        title = f"{self.title}  {self.page + 1}/{max(page_count, 1)}"
        self.title_font.draw(260, 440, title, (255, 239, 177))
        items = self.pages[self.page] if self.page < page_count else ()
        for index, (name, price, description, requirement, kind, target) in enumerate(
            items
        ):
            y = 360 - index * 80
            draw_item_icon(name, 120, y)
            self.item_font.draw(165, y, name, (235, 235, 235))
            self.item_font.draw(600, y, f"$ {price:,}", (255, 224, 120))
            if requirement:
                ore, count = requirement
                image = self.ore_images[ore]
                image.draw(450, y + 6, 32, 32)
                self.item_font.draw(480, y, f"x{count}", (255, 224, 120))
            if kind == "miner":
                owned = game_state.miners[target]
                count_color = (
                    (255, 224, 120)
                    if owned < MAX_MINERS_PER_ZONE
                    else (255, 150, 120)
                )
                self.item_font.draw(
                    450,
                    y,
                    f"{owned}/{MAX_MINERS_PER_ZONE}",
                    count_color,
                )
            if kind == "farmer":
                owned = farmer.count(target)
                count_color = (
                    (255, 224, 120)
                    if owned < farmer.MAX_PER_ZONE
                    else (255, 150, 120)
                )
                self.item_font.draw(
                    450,
                    y,
                    f"{owned}/{farmer.MAX_PER_ZONE}",
                    count_color,
                )
            if description:
                self.description_font.draw(
                    165, y - 20, description, (180, 190, 205)
                )

