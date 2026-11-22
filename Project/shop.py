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

import camera
import game_state


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


class Shop:
    panel = None
    title_font = None
    item_font = None
    description_font = None
    ore_images = {}

    def __init__(self, player, merchant, mode="buy"):
        self.player = player
        self.merchant = merchant
        self.mode = mode
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
                for index, item in enumerate(ITEM_PAGES[self.page]):
                    item_y = 360 - index * 80
                    if 100 <= event.x < 700 and item_y - 40 <= y <= item_y + 20:
                        self._buy(item)
                        break

    def _page_count(self):
        if self.mode == "sell":
            return len(SELL_PAGES)
        return len(ITEM_PAGES)

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
        page_count = len(ITEM_PAGES)
        title = f"MINING SHOP  {self.page + 1}/{page_count}"
        self.title_font.draw(260, 440, title, (255, 239, 177))
        for index, (name, price, description, requirement, kind, target) in enumerate(
            ITEM_PAGES[self.page]
        ):
            y = 360 - index * 80
            self.item_font.draw(100, y, name, (235, 235, 235))
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
            if description:
                self.description_font.draw(
                    100, y - 20, description, (180, 190, 205)
                )

