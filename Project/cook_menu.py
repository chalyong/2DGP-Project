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
from rhythm import RhythmGame


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
        self.quantities = {}  # 레시피명 -> 요청 수량 (페이지를 넘어 유지)
        self.rhythm = None  # 제작 요청 시 열리는 리듬게임 (rhythm.RhythmGame)
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
        if self.rhythm is not None:
            self.rhythm.handle_event(event)
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
                self.quantities.clear()
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
            if 300 <= x < 520 and 110 <= y <= 150:
                self._submit()
                return
            rows = list(game_state.RECIPES)
            start = self.page * self.ITEMS_PER_PAGE
            for index, (name, groups) in enumerate(
                rows[start : start + self.ITEMS_PER_PAGE]
            ):
                row_y = self.ROW_Y0 - index * self.ROW_SPACING
                if not row_y - 40 <= y <= row_y + 20:
                    continue
                quantity = self.quantities.get(name, 0)
                if 430 <= x < 465:
                    self.quantities[name] = max(0, quantity - 1)
                    return
                if 500 <= x < 535:
                    self.quantities[name] = quantity + 1
                    return
                if 545 <= x < 610:
                    self.quantities[name] = self._max_quantity(groups)
                    return

    def _max_quantity(self, groups):
        """현재 재료로 만들 수 있는 최대 수량."""
        limit = None
        for group in groups:
            available = sum(
                game_state.collected_items.get(key, 0) for key in group
            )
            limit = available if limit is None else min(limit, available)
        return max(0, limit or 0)

    def _submit(self):
        """요청 수량만큼 제작 (뷔페_PRD 3.3): 전량 검증 후 소비, 부족분은 오류 표시."""
        requests = [
            (name, quantity)
            for name, quantity in self.quantities.items()
            if quantity > 0
        ]
        if not requests:
            self.message = "SET QUANTITY FIRST"
            self.message_time = get_time()
            return
        cooked = []
        failed = []
        for name, quantity in requests:
            ok, detail = game_state.consume_ingredients(name, quantity)
            if ok:
                cooked.append((name, quantity))
            elif detail not in failed:
                failed.append(detail)
        if failed:
            # 오류 상태 우선 표시 (PRD: 부족한 요리는 제작되지 않음)
            self.message = " / ".join(failed)
        else:
            self.message = "REQUESTED " + ", ".join(
                f"{name} x{quantity}" for name, quantity in cooked
            )
        self.message_time = get_time()
        if cooked:
            # 리듬게임 판으로 이어감 (b9: 표시·낙하, b10: 판정·보상)
            self.rhythm = RhythmGame(cooked, failed)
            self.open = False
            self.player.set_movement_locked(False)
            self.page = 0
            self.quantities.clear()

    def _page_count(self):
        return max(
            1,
            (len(game_state.RECIPES) + self.ITEMS_PER_PAGE - 1)
            // self.ITEMS_PER_PAGE,
        )

    def update(self):
        if self.message and get_time() - self.message_time >= 1.5:
            self.message = None
        if self.rhythm is not None:
            self.rhythm.update()
            if self.rhythm.done:
                self.rhythm = None

    def draw(self):
        if self.open:
            self._draw_panel()
        if self.rhythm is not None:
            self.rhythm.draw()

    def _draw_panel(self):
        self.page = min(self.page, self._page_count() - 1)
        self.panel.draw_to_origin(40, 100)
        self.title_font.draw(
            300,
            455,
            f"COOKING  {self.page + 1}/{self._page_count()}",
            (255, 239, 177),
        )

        rows = list(game_state.RECIPES)
        start = self.page * self.ITEMS_PER_PAGE
        for index, (name, groups) in enumerate(
            rows[start : start + self.ITEMS_PER_PAGE]
        ):
            y = self.ROW_Y0 - index * self.ROW_SPACING
            shop.draw_item_icon(name, 120, y, prefer_item=True)
            self.item_font.draw(165, y, name, (235, 235, 235))
            ingredients = " + ".join(
                "/".join(key.upper() for key in group) for group in groups
            )
            self.description_font.draw(165, y - 20, ingredients, (180, 190, 205))
            quantity = self.quantities.get(name, 0)
            quantity_color = (255, 224, 120) if quantity else (140, 150, 165)
            self.item_font.draw(440, y, "-", (235, 235, 235))
            self.item_font.draw(470, y, str(quantity), quantity_color)
            self.item_font.draw(510, y, "+", (235, 235, 235))
            self.description_font.draw(550, y, "MAX", (180, 190, 205))
            cooked = game_state.cooked_items.get(name, 0)
            self.item_font.draw(640, y, f"x {cooked}", (255, 224, 120))

        if self.message:
            self.item_font.draw(300, 170, self.message, (255, 150, 120))
        total = sum(self.quantities.values())
        cook_color = (255, 224, 120) if total else (140, 150, 165)
        self.item_font.draw(340, 128, f"[ COOK x{total} ]", cook_color)
        self.detail_font.draw(110, 128, "SPACE: CLOSE", (180, 190, 205))
