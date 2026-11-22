# 농사지 레이아웃과 재배 구역 기하학
# 좌표는 pico2d 기준(원점 좌측 하단, y 위쪽 증가), 스케일 40px/m

SIZE = 880
EXIT = (440, 790)
MERCHANT = (120, 680)
PLAYER_SPAWN = (440, 690)

GRID = 5
PLOW_WIDTH = 240
PLOW_HEIGHT = 258
CELL_WIDTH = PLOW_WIDTH / GRID
CELL_HEIGHT = PLOW_HEIGHT / GRID

# 작물 -> 재배 구역 중심 (우상단, 좌하단, 우하단)
ZONES = {
    "wheat": (705, 615),
    "potato": (215, 235),
    "strawberry": (665, 235),
}
SPRINKLER_CELL = 12  # 5x5 중앙 칸

# 성장·재성장 시간 (개발 중 결정값, PRD 7장 참조)
STAGE_SECONDS = 20  # 단계당 시간 -> 씨앗에서 ready까지 60초
REGROW_SECONDS = 120  # 수확 후 다시 성장하기까지 2분
READY_STAGE = 3


def plow_rect(crop):
    cx, cy = ZONES[crop]
    return (
        cx - PLOW_WIDTH / 2,
        cy - PLOW_HEIGHT / 2,
        cx + PLOW_WIDTH / 2,
        cy + PLOW_HEIGHT / 2,
    )


def cell_rect(crop, index):
    """칸 인덱스(0~24, 위쪽 왼쪽부터 가로 방향)의 (x0, y0, x1, y1)."""
    left, bottom, right, top = plow_rect(crop)
    col = index % GRID
    row = index // GRID
    x0 = left + col * CELL_WIDTH
    y1 = top - row * CELL_HEIGHT
    return (x0, y1 - CELL_HEIGHT, x0 + CELL_WIDTH, y1)


def cell_at(crop, x, y):
    """좌표가 속한 칸 인덱스, 구역 밖이면 None."""
    left, bottom, right, top = plow_rect(crop)
    if not (left <= x < right and bottom <= y < top):
        return None
    col = int((x - left) // CELL_WIDTH)
    row = int((top - y) // CELL_HEIGHT)
    col = min(col, GRID - 1)
    row = min(row, GRID - 1)
    return row * GRID + col


def sprinkler_rect(crop):
    return cell_rect(crop, SPRINKLER_CELL)


def is_sprinkler_hit(crop, x, y):
    x0, y0, x1, y1 = sprinkler_rect(crop)
    return x0 <= x < x1 and y0 <= y < y1


def crop_stage(slot, now, stage_seconds=None):
    """작물 성장 단계(0=seed ~ 3=ready). 아직 없는 상태면 None.

    slot: {"planted_at": 시각, "harvested_at": 시각 or None}
    수확 후 REGROW_SECONDS가 지나면 다시 씨앗부터 자란다.
    """
    if stage_seconds is None:
        stage_seconds = STAGE_SECONDS
    planted = slot["planted_at"]
    harvested = slot["harvested_at"]
    if harvested is not None:
        if now - harvested < REGROW_SECONDS:
            return None
        planted = harvested + REGROW_SECONDS
    return min(int((now - planted) // stage_seconds), READY_STAGE)
