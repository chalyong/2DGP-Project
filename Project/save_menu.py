# 집 앞 저장·불러오기 메뉴 (PRD 9단계 UI)
from pico2d import get_time, load_font, load_image

import camera
import game_state


class SaveMenu:
    """SAVE/LOAD/DELETE 모드의 슬롯 목록 메뉴.

    조작: 모드 버튼 클릭 -> 슬롯 클릭. SAVE는 이름 입력 후 ENTER 확정,
    DELETE/덮어쓰기는 한 번 더 클릭으로 확인. ESC는 닫기(main이 처리).
    """

    panel = None
    title_font = None
    item_font = None
    detail_font = None

    ROW_Y0 = 380
    ROW_SPACING = 60
    # 모드 버튼 (x 범위, y: 410..445)
    MODE_BUTTONS = (
        ("save", "SAVE", 120, 215),
        ("load", "LOAD", 240, 335),
        ("delete", "DELETE", 360, 490),
        ("close", "CLOSE", 520, 625),
    )

    def __init__(self):
        self.open = False
        self.mode = "save"
        self.typing = False
        self.slot = None
        self.pending = None  # 덮어쓰기/삭제 두 번째 클릭 확인
        self.input_name = ""
        self.message = None
        self.message_time = -10.0
        self.on_load = None  # 로드 성공 콜백 (main.reload_current_scene)

    def _ensure_assets(self):
        """캔버스 오픈 이후에 에셋 로드 (임포트 시점에는 renderer가 없음)."""
        if SaveMenu.panel is None:
            SaveMenu.panel = load_image("assets/ui/shop_panel.png")
            SaveMenu.title_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 28)
            SaveMenu.item_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 20)
            SaveMenu.detail_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 16)

    # --- lifecycle ---

    def open_menu(self, player):
        self.open = True
        self.typing = False
        self.pending = None
        self.message = None
        player.set_movement_locked(True)

    def close(self, player):
        self.open = False
        self.typing = False
        self.pending = None
        player.set_movement_locked(False)

    def _notify(self, message):
        self.message = message
        self.message_time = get_time()

    # --- input ---

    def handle_event(self, event, player):
        from sdl2 import SDL_KEYDOWN, SDL_MOUSEBUTTONDOWN, SDLK_BACKSPACE, SDLK_RETURN

        if not self.open:
            return

        if event.type == SDL_KEYDOWN and self.typing:
            if event.key == SDLK_RETURN:
                name = self.input_name.strip()
                if not name:
                    self._notify("NAME REQUIRED")
                    return
                ok, msg = game_state.save_game(self.slot, name)
                self._notify(msg)
                if ok:
                    self.typing = False
                    self.slot = None
            elif event.key == SDLK_BACKSPACE:
                self.input_name = self.input_name[:-1]
            elif len(self.input_name) < 12 and 32 <= event.key < 127:
                self.input_name += chr(event.key).upper()
            return

        if event.type == SDL_MOUSEBUTTONDOWN and getattr(event, "button", 1) == 1:
            x = event.x
            y = camera.SCREEN_HEIGHT - event.y
            if 410 <= y <= 448:
                for mode, _label, x0, x1 in self.MODE_BUTTONS:
                    if x0 <= x < x1:
                        if mode == "close":
                            self.close(player)
                        else:
                            self.mode = mode
                            self.typing = False
                            self.pending = None
                        return
            if self.typing:
                return
            for index in range(5):
                row_y = self.ROW_Y0 - index * self.ROW_SPACING
                if 100 <= x < 700 and row_y - 25 <= y <= row_y + 25:
                    self._click_slot(index + 1, player)
                    return

    def _click_slot(self, slot, player):
        name = dict(game_state.list_saves()).get(slot)

        if self.mode == "load":
            if name is None:
                self._notify(f"EMPTY SLOT {slot}")
                return
            ok, msg = game_state.load_game(slot)
            self._notify(msg)
            if ok:
                self.close(player)
                if self.on_load:
                    self.on_load()
            return

        if self.mode == "delete":
            if name is None:
                self._notify(f"EMPTY SLOT {slot}")
                return
            if self.pending != slot:
                self.pending = slot
                self._notify(f"DELETE SLOT {slot}? CLICK AGAIN")
                return
            ok, msg = game_state.delete_save(slot)
            self._notify(msg)
            self.pending = None
            return

        # save: 빈 슬롯 -> 이름 입력, 찬 슬롯 -> 두 번째 클릭으로 덮어쓰기
        if name is not None and self.pending != slot:
            self.pending = slot
            self._notify(f"SLOT {slot} OCCUPIED - CLICK AGAIN TO OVERWRITE")
            return
        self.typing = True
        self.slot = slot
        self.pending = None
        self.input_name = name or ""
        self._notify(f"TYPE NAME - ENTER: SAVE / ESC: CANCEL")

    # --- draw ---

    def draw(self):
        if not self.open:
            return
        self._ensure_assets()

        self.panel.draw_to_origin(40, 100)
        self.title_font.draw(270, 455, "SAVE / LOAD", (255, 239, 177))

        for mode, label, x0, _x1 in self.MODE_BUTTONS:
            color = (255, 224, 120) if mode == self.mode else (180, 190, 205)
            self.item_font.draw(x0 + 8, 422, label, color)

        saves = dict(game_state.list_saves())
        for index in range(5):
            slot = index + 1
            y = self.ROW_Y0 - index * self.ROW_SPACING
            name = saves.get(slot)
            highlight = self.pending == slot
            if name is None:
                slot_color = (120, 120, 130)
                label = "--- EMPTY"
            else:
                slot_color = (255, 150, 120) if highlight else (235, 235, 235)
                label = name
            self.item_font.draw(115, y, f"SLOT {slot}", (180, 190, 205))
            self.item_font.draw(260, y, label, slot_color)
            if self.mode == "load" and name is None:
                self.detail_font.draw(560, y, "EMPTY", (120, 120, 130))

        if self.typing:
            cursor = "_" if int(get_time() * 2) % 2 == 0 else " "
            self.item_font.draw(
                115, 115, f"NAME: {self.input_name}{cursor}", (255, 224, 120)
            )
        elif self.message and get_time() - self.message_time < 2.0:
            self.item_font.draw(115, 115, self.message, (255, 150, 120))
