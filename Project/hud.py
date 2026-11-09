from pico2d import load_font

import game_state


class Hud:
    font = None

    def __init__(self):
        if Hud.font is None:
            Hud.font = load_font(r"C:\Windows\Fonts\consolab.ttf", 22)

    def update(self):
        pass

    def draw(self):
        amount = f"$ {game_state.money:,}"
        self.font.draw(20, 570, amount, (255, 239, 177))
