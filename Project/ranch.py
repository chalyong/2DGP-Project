# 목장 레이아웃과 동물 구역 (목장_PRD 3.1 / 3.2)
# 좌표는 pico2d 기준(원점 좌측 하단, y 위쪽 증가), 농사지와 동일 스케일 880x880
from pico2d import get_time, load_image

import auto_npc
import camera

SIZE = 880
EXIT = (440, 790)  # 중앙 상단
MERCHANT = (120, 680)  # 좌측 상단
PLAYER_SPAWN = (440, 690)

ZONE_WIDTH = 240
ZONE_HEIGHT = 258

# 동물 1~3은 티어 순서대로: 닭(우상), 소(좌하), 돼지(우하)
ZONES = {
    "chicken": (705, 615),  # 동물 1 - 우상단
    "cow": (215, 235),  # 동물 2 - 좌하단
    "pig": (665, 235),  # 동물 3 - 우하단
}

ANIMAL_ORDER = ("chicken", "cow", "pig")
ANIMAL_FRAME_DURATION = 0.2


def zone_rect(animal):
    cx, cy = ZONES[animal]
    return (
        cx - ZONE_WIDTH / 2,
        cy - ZONE_HEIGHT / 2,
        cx + ZONE_WIDTH / 2,
        cy + ZONE_HEIGHT / 2,
    )


def zone_at(animal, x, y):
    """좌표가 해당 동물 구역 안이면 True."""
    x0, y0, x1, y1 = zone_rect(animal)
    return x0 <= x < x1 and y0 <= y < y1


class RanchZone:
    """동물 구역: 울타리와 게이트 렌더링 (이후 동물·타이머 렌더 확장)."""

    fence_image = None
    gate_image = None

    def __init__(self, animal):
        self.animal = animal
        self.sheet = None
        if RanchZone.fence_image is None:
            RanchZone.fence_image = load_image(
                "assets/buildings/fence_tile_length.png"
            )
            RanchZone.gate_image = load_image("assets/buildings/fence_gate.png")
        self.sheet = load_image(f"assets/npc/animal_{animal}.png")

    def update(self):
        pass

    def draw(self):
        x0, y0, x1, y1 = zone_rect(self.animal)
        cx, cy = ZONES[self.animal]
        RanchZone.fence_image.draw(
            cx - camera.x,
            cy - camera.y,
            ZONE_WIDTH,
            ZONE_HEIGHT,
        )
        # 게이트: 구역 하단 중앙 (들어오는 방향)
        RanchZone.gate_image.draw(
            (x0 + x1) / 2 - camera.x,
            y0 - camera.y,
            64,
            64,
        )
        self._draw_animals()

    def _draw_animals(self):
        now = get_time()
        for a in auto_npc.animals:
            if a["animal"] != self.animal:
                continue
            delta = max(0.0, now - a.setdefault("anim_time", now))
            a["anim_time"] = now
            a["frame_timer"] += delta
            while a["frame_timer"] >= ANIMAL_FRAME_DURATION:
                a["frame"] = (a["frame"] + 1) % 4
                a["frame_timer"] -= ANIMAL_FRAME_DURATION
            flip = "h" if a["facing"] == "left" else ""
            self.sheet.clip_composite_draw(
                a["frame"] * 64,
                0,
                64,
                64,
                0,
                flip,
                a["x"] - camera.x,
                a["y"] - camera.y,
                56,
                64,
            )
