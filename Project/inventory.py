from pico2d import get_time, load_font, load_image
from sdl2 import (
    SDL_KEYDOWN,
    SDL_MOUSEBUTTONDOWN,
    SDL_MOUSEWHEEL,
    SDLK_e,
)

import camera
import game_state
import shop


class Inventory:
    panel = None
    title_font = None
    tab_font = None
    item_font = None
    detail_font = None
    description_font = None

    TABS = ("ASSETS", "COLLECTIBLES", "COOKING", "TOOLS", "PASSES")
    TAB_START = 76
    TAB_WIDTH = 128
    ITEMS_PER_PAGE = 3
    # 상점 행 레이아웃 기준 (첫 행 y=360, 행 간격 80, 설명은 이름 아래 20px)
    ROW_Y0 = 360
    ROW_SPACING = 80
    PRICE_X = 600

    def __init__(self, player):
        self.player = player
        self.open = False
        self.tab = 0
        self.page = 0
        self.page_change_time = -0.2
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
        if Inventory.description_font is None:
            Inventory.description_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 14)

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_e:
            self.open = not self.open
            self.player.set_movement_locked(self.open)
            if not self.open:
                self.tab = 0
                self.page = 0
            return

        if (
            event.type == SDL_MOUSEBUTTONDOWN
            and self.open
            and getattr(event, "button", 1) == 1
        ):
            x = event.x
            y = camera.SCREEN_HEIGHT - event.y
            if self.TAB_START <= x < self.TAB_START + len(self.TABS) * self.TAB_WIDTH and 390 <= y <= 450:
                self.tab = min(
                    (x - self.TAB_START) // self.TAB_WIDTH,
                    len(self.TABS) - 1,
                )
                self.page = 0
            return

        if (
            event.type == SDL_MOUSEWHEEL
            and self.open
            and get_time() - self.page_change_time >= 0.2
        ):
            page_count = self._page_count()
            if page_count <= 1:
                return
            if event.y < 0:
                self.page = min(self.page + 1, page_count - 1)
            elif event.y > 0:
                self.page = max(self.page - 1, 0)
            else:
                return
            self.page_change_time = get_time()

    def _tool_list(self):
        # mine tools + farm tools (incl. fertilizer) + hunting knife (보유 수량 표시)
        return game_state.tools + game_state.farm_tools + ["HUNTING KNIFE"]

    def _page_count(self):
        if self.tab == 0:
            return 1
        if self.tab == 1:
            count = len(game_state.collected_items)
        elif self.tab == 2:
            count = len(game_state.cooked_items)
        elif self.tab == 3:
            count = len(self._tool_list())
        else:
            count = len(game_state.passes)
        return max(1, (count + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE)

    def _page_slice(self, sequence):
        start = self.page * self.ITEMS_PER_PAGE
        return sequence[start : start + self.ITEMS_PER_PAGE]

    def update(self):
        pass

    def draw(self):
        if not self.open:
            return

        self.page = min(self.page, self._page_count() - 1)
        self.panel.draw_to_origin(40, 100)
        self.title_font.draw(300, 455, "INVENTORY", (255, 239, 177))

        for index, name in enumerate(self.TABS):
            left = self.TAB_START + index * self.TAB_WIDTH
            color = (255, 224, 120) if index == self.tab else (180, 190, 205)
            self.tab_font.draw(left + 16, 425, name, color)

        if self.tab == 0:
            self._draw_assets()
        elif self.tab == 1:
            self._draw_items(game_state.collected_items)
        elif self.tab == 2:
            self._draw_items(game_state.cooked_items)
        elif self.tab == 3:
            self._draw_tools()
        else:
            self._draw_passes()

        self.detail_font.draw(300, 130, "E: CLOSE", (180, 190, 205))
        if self.tab != 0 and self._page_count() > 1:
            self.detail_font.draw(
                640,
                130,
                f"{self.page + 1}/{self._page_count()}",
                (180, 190, 205),
            )

    def _draw_assets(self):
        elapsed = max(0, int(get_time() - game_state.play_start_time))
        minutes, seconds = divmod(elapsed, 60)
        self.item_font.draw(
            110,
            self.ROW_Y0,
            f"MONEY   $ {game_state.money:,}",
            (235, 235, 235),
        )
        self.item_font.draw(
            110,
            self.ROW_Y0 - self.ROW_SPACING,
            f"PLAY TIME   {minutes:02d}:{seconds:02d}",
            (235, 235, 235),
        )

    def _draw_items(self, items):
        all_items = list(items.items())
        if not all_items:
            self.detail_font.draw(285, 290, "EMPTY", (180, 190, 205))
            return

        for index, (name, count) in enumerate(self._page_slice(all_items)):
            y = self.ROW_Y0 - index * self.ROW_SPACING
            shop.draw_item_icon(name, 120, y)
            self.item_font.draw(165, y - 6, name.upper(), (235, 235, 235))
            self.item_font.draw(
                self.PRICE_X,
                y - 6,
                f"x {count}",
                (255, 224, 120),
            )

    def _draw_tools(self):
        # 광산 도구(곡괭이) + 농사지 도구(낫 곡괭이·비료)
        tools = self._tool_list()
        if not tools:
            self.detail_font.draw(275, 290, "NO TOOLS", (180, 190, 205))
            return

        for index, tool in enumerate(self._page_slice(tools)):
            y = self.ROW_Y0 - index * self.ROW_SPACING
            shop.draw_item_icon(tool, 120, y)
            self.item_font.draw(165, y, tool, (235, 235, 235))
            if tool == "HUNTING KNIFE":
                self.item_font.draw(
                    self.PRICE_X,
                    y,
                    f"x {game_state.hunting_knives}",
                    (255, 224, 120),
                )
            description = shop.ITEM_DESCRIPTIONS.get(tool, "")
            if description:
                self.description_font.draw(
                    165, y - 20, description, (180, 190, 205)
                )

    def _draw_passes(self):
        if not game_state.passes:
            self.detail_font.draw(280, 290, "NO PASSES", (180, 190, 205))
            return

        for index, name in enumerate(self._page_slice(game_state.passes)):
            y = self.ROW_Y0 - index * self.ROW_SPACING
            shop.draw_item_icon(name, 120, y)
            self.item_font.draw(165, y, name, (235, 235, 235))
