from pico2d import get_time, load_font, load_image
from sdl2 import SDL_KEYDOWN, SDL_MOUSEWHEEL, SDLK_SPACE


class Shop:
    panel = None
    title_font = None
    item_font = None

    def __init__(self, player, merchant):
        self.player = player
        self.merchant = merchant
        self.open = False
        self.page = 0
        self.page_change_time = -0.2
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
            self.player.set_movement_locked(self.open)
            if not self.open:
                self.page = 0
        elif (
            event.type == SDL_MOUSEWHEEL
            and self.open
            and get_time() - self.page_change_time >= 0.2
        ):
            if event.y < 0:
                self.page = min(self.page + 1, 1)
            elif event.y > 0:
                self.page = max(self.page - 1, 0)
            else:
                return
            self.page_change_time = get_time()

    def update(self):
        pass

    def draw(self):
        if not self.open:
            return
        self.panel.draw_to_origin(40, 100)
        title = f"MINING SHOP  {self.page + 1}/2"
        self.title_font.draw(260, 440, title, (255, 239, 177))
        items = (
            (
                ("WOOD PICKAXE", "$ 100"),
                ("STONE PICKAXE", "$ 300"),
                ("IRON PICKAXE", "$ 800"),
            ),
            (
                ("COAL TUNNEL PASS", "$ 500"),
                ("IRON TUNNEL PASS", "$ 1,200"),
                ("GOLD TUNNEL PASS", "$ 3,000"),
            ),
        )[self.page]
        for index, (name, price) in enumerate(items):
            y = 360 - index * 80
            self.item_font.draw(100, y, name, (235, 235, 235))
            self.item_font.draw(600, y, price, (255, 224, 120))
        self.item_font.draw(150, 130, "MOUSE WHEEL: CHANGE PAGE", (180, 190, 205))
        self.item_font.draw(480, 130, "SPACE: CLOSE", (180, 190, 205))
