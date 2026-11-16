from pico2d import get_time, load_font, load_image
from sdl2 import SDL_KEYDOWN, SDL_MOUSEBUTTONDOWN, SDL_MOUSEWHEEL, SDLK_SPACE

import camera
import game_state


# name, price, description, required ore (name, count) or None, kind, kind target
ITEM_PAGES = (
    (
        ("WOOD PICKAXE", 100, "stone+2", None, "tool", None),
        ("STONE PICKAXE", 300, "stone+3, coal+2", ("stone", 10), "tool", None),
        ("IRON PICKAXE", 800, "stone+5, coal+3, iron+2", ("iron", 10), "tool", None),
    ),
    (
        ("GOLD PICKAXE", 1500, "stone+10, coal+5, iron+3, gold+2", ("gold", 10), "tool", None),
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

    def __init__(self, player, merchant):
        self.player = player
        self.merchant = merchant
        self.open = False
        self.page = 0
        self.page_change_time = -0.2
        self.message = None
        self.message_time = 0
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
                    f"assets/ore/ore_{name}.png"
                )

    def handle_event(self, event):
        if (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and abs(self.player.x - self.merchant.x) <= 50
            and abs(self.player.y - self.merchant.y) <= 80
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
                self.page = min(self.page + 1, 3)
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
            for index, item in enumerate(ITEM_PAGES[self.page]):
                item_y = 360 - index * 80
                if 100 <= event.x < 700 and item_y - 40 <= y <= item_y + 20:
                    self._buy(item)
                    break

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
        self.message = f"PURCHASED {name}"
        self.message_time = get_time()

    def update(self):
        if self.message and get_time() - self.message_time >= 1.5:
            self.message = None

    def draw(self):
        if not self.open:
            return
        self.panel.draw_to_origin(40, 100)
        title = f"MINING SHOP  {self.page + 1}/4"
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
            if description:
                self.description_font.draw(
                    100, y - 20, description, (180, 190, 205)
                )
        if self.message and get_time() - self.message_time < 1.5:
            self.item_font.draw(300, 170, self.message, (255, 150, 120))
        self.item_font.draw(150, 130, "MOUSE WHEEL: CHANGE PAGE", (180, 190, 205))
        self.item_font.draw(480, 130, "SPACE: CLOSE", (180, 190, 205))
