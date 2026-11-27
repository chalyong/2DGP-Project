# 요리사 제작 메뉴 (뷔페_PRD 3.3)
# b6: 상호작용으로 메뉴 진입 (임시: 클릭 즉시 제작 — b7~b10에서 수량 설정 + 리듬게임으로 교체)
from pico2d import get_time, load_font, load_image
from sdl2 import (
    SDL_KEYDOWN,
    SDL_MOUSEBUTTONDOWN,
    SDL_MOUSEWHEEL,
    SDLK_SPACE,
)

import camera
import game_state
import shop


class CookMenu:
    panel = None
    title_font = None
    item_font = None
    description_font = None
    detail_font = None

    ITEMS_PER_PAGE = 3
    ROW_Y0 = 360
    ROW_SPACING = 80

    def __init__(self, player, chef):
        self.player = player
        self.chef = chef
        self.open = False
        self.page = 0
        self.page_change_time = -0.2
        self.message = None
        self.message_time = -2.0
        if CookMenu.panel is None:
            CookMenu.panel = load_image("assets/ui/shop_panel.png")
        if CookMenu.title_font is None:
            CookMenu.title_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 28)
        if CookMenu.item_font is None:
            CookMenu.item_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 20)
        if CookMenu.description_font is None:
            CookMenu.description_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 14)
        if CookMenu.detail_font is None:
            CookMenu.detail_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 16)

    def handle_event(self, event):
        if (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and abs(self.player.x - self.chef.x) <= 40
            and abs(self.player.y - self.chef.y) <= 40
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
        elif (
            event.type == SDL_MOUSEBUTTONDOWN
            and self.open
            and getattr(event, "button", 1) == 1
        ):
            x = event.x
            y = camera.SCREEN_HEIGHT - event.y
            rows = list(game_state.RECIPES)
            start = self.page * self.ITEMS_PER_PAGE
            for index, (name, groups) in enumerate(
                rows[start : start + self.ITEMS_PER_PAGE]
            ):
                row_y = self.ROW_Y0 - index * self.ROW_SPACING
                if 100 <= x < 700 and row_y - 40 <= y <= row_y + 20:
                    ok, message = game_state.cook(name)
                    self.message = message
                    self.message_time = get_time()
                    return

    def _page_count(self):
        return max(
            1,
            (len(game_state.RECIPES) + self.ITEMS_PER_PAGE - 1)
            // self.ITEMS_PER_PAGE,
        )

    def update(self):
        if self.message and get_time() - self.message_time >= 1.5:
            self.message = None

    def draw(self):
        if not self.open:
            return

        self.page = min(self.page, self._page_count() - 1)
        self.panel.draw_to_origin(40, 100)
        self.title_font.draw(300, 455, "COOKING", (255, 239, 177))

        rows = list(game_state.RECIPES)
        start = self.page * self.ITEMS_PER_PAGE
        for index, (name, groups) in enumerate(
            rows[start : start + self.ITEMS_PER_PAGE]
        ):
            y = self.ROW_Y0 - index * self.ROW_SPACING
            shop.draw_item_icon(name, 120, y, prefer_item=True)
            self.item_font.draw(165, y, name, (235, 235, 235))
            cooked = game_state.cooked_items.get(name, 0)
            self.item_font.draw(600, y, f"x {cooked}", (255, 224, 120))
            ingredients = " + ".join(
                "/".join(key.upper() for key in group) for group in groups
            )
            self.description_font.draw(165, y - 20, ingredients, (180, 190, 205))

        if self.message:
            self.item_font.draw(300, 170, self.message, (255, 150, 120))
        self.detail_font.draw(300, 130, "SPACE: CLOSE", (180, 190, 205))
        if self._page_count() > 1:
            self.detail_font.draw(
                640, 130, f"{self.page + 1}/{self._page_count()}", (180, 190, 205)
            )
