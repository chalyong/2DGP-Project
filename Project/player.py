from pico2d import load_image


class Player:
    def __init__(self):
        self.x = 400
        self.y = 300
        self.image = load_image("assets/player/player_front_right.png")

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x, self.y)
