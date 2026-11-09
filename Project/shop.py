from pico2d import load_font, load_image
from sdl2 import SDL_KEYDOWN, SDLK_SPACE


class Shop:
    panel = None
    title_font = None
    item_font = None

    def __init__(self, player, merchant):
        self.player = player
        self.merchant = merchant
        self.open = False
        if Shop.panel is None:
            Shop.panel = load_image("assets/ui/shop_panel.png")
        if Shop.title_font is None:
            Shop.title_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 28)
        if Shop.item_font is None:
            Shop.item_font = load_font(r"C:\Windows\Fonts\consolab.ttf", 18)

    def handle_event(self, event):
        if (
            event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
            and abs(self.player.x - self.merchant.x) <= 100
            and abs(self.player.y - self.merchant.y) <= 80
        ):
            self.open = not self.open

    def update(self):
        pass

    def draw(self):
        if not self.open:
            return
        self.panel.draw_to_origin(40, 100)
        self.title_font.draw(310, 440, "MINING SHOP", (255, 239, 177))
        self.item_font.draw(100, 360, "WOOD PICKAXE", (235, 235, 235))
        self.item_font.draw(600, 360, "$ 100", (255, 224, 120))
        self.item_font.draw(100, 280, "STONE PICKAXE", (235, 235, 235))
        self.item_font.draw(600, 280, "$ 300", (255, 224, 120))
        self.item_font.draw(100, 200, "IRON PICKAXE", (235, 235, 235))
        self.item_font.draw(600, 200, "$ 800", (255, 224, 120))
        self.item_font.draw(300, 130, "SPACE: CLOSE", (180, 190, 205))
