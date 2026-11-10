from pico2d import get_time, load_font, load_image
from sdl2 import SDL_MOUSEBUTTONDOWN, SDL_KEYDOWN, SDLK_e

import camera
import game_state


class Inventory:
    panel = None
    title_font = None
    tab_font = None
    item_font = None
    detail_font = None
    item_images = {}

    TABS = ("ASSETS", "COLLECTIBLES", "COOKING", "TOOLS")

    def __init__(self, player):
        self.player = player
        self.open = False
        self.tab = 0
        if Inventory.panel is None:
            Inventory.panel = load_image("assets/ui/shop_panel.png")
        if Inventory.title_font is None:
            Inventory.title_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 28)
        if Inventory.tab_font is None:
            Inventory.tab_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 16)
        if Inventory.item_font is None:
            Inventory.item_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 20)
        if Inventory.detail_font is None:
            Inventory.detail_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 16)
        if not Inventory.item_images:
            for name in ("stone", "coal", "iron", "gold"):
                Inventory.item_images[name] = load_image(
                    f"assets/ore/ore_{name}.png"
                )

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_e:
            self.open = not self.open
            self.player.set_movement_locked(self.open)
            if not self.open:
                self.tab = 0
            return

        if (
            event.type == SDL_MOUSEBUTTONDOWN
            and self.open
            and getattr(event, "button", 1) == 1
        ):
            x = event.x
            y = camera.SCREEN_HEIGHT - event.y
            if 80 <= x < 720 and 390 <= y <= 450:
                self.tab = min((x - 80) // 160, len(self.TABS) - 1)

    def update(self):
        pass

    def draw(self):
        if not self.open:
            return

        self.panel.draw_to_origin(40, 100)
        self.title_font.draw(300, 455, "INVENTORY", (255, 239, 177))

        for index, name in enumerate(self.TABS):
            left = 80 + index * 160
            color = (255, 224, 120) if index == self.tab else (180, 190, 205)
            self.tab_font.draw(left + 28, 425, name, color)

        if self.tab == 0:
            self._draw_assets()
        elif self.tab == 1:
            self._draw_items(game_state.collected_items)
        elif self.tab == 2:
            self._draw_items(game_state.cooked_items)
        else:
            self._draw_tools()

        self.detail_font.draw(300, 135, "E: CLOSE", (180, 190, 205))

    def _draw_assets(self):
        elapsed = max(0, int(get_time() - game_state.play_start_time))
        minutes, seconds = divmod(elapsed, 60)
        self.item_font.draw(110, 350, f"MONEY   $ {game_state.money:,}", (235, 235, 235))
        self.item_font.draw(
            110,
            295,
            f"PLAY TIME   {minutes:02d}:{seconds:02d}",
            (235, 235, 235),
        )

    def _draw_items(self, items):
        visible_items = list(items.items())
        if not visible_items:
            self.detail_font.draw(285, 290, "EMPTY", (180, 190, 205))
            return

        for index, (name, count) in enumerate(visible_items):
            y = 350 - index * 65
            image = self.item_images.get(name)
            if image is not None:
                image.draw(120, y, 42, 42)
            self.item_font.draw(165, y - 6, name.upper(), (235, 235, 235))
            self.item_font.draw(570, y - 6, f"x {count}", (255, 224, 120))

    def _draw_tools(self):
        if not game_state.tools:
            self.detail_font.draw(275, 290, "NO TOOLS", (180, 190, 205))
            return

        for index, tool in enumerate(game_state.tools):
            self.item_font.draw(120, 350 - index * 55, tool, (235, 235, 235))
