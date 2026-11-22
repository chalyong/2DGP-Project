# 목장 레이아웃과 동물 구역 (목장_PRD 3.1 / 3.2)
# 좌표는 pico2d 기준(원점 좌측 하단, y 위쪽 증가), 농사지와 동일 스케일 880x880

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
