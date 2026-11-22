# 농부 고용 데이터와 배치
# 이동 속도는 플레이어 속도 기반 (농장_PRD 4절: 자동 NPC = 플레이어, 동물 = 그 절반)
import random

from pico2d import get_time

import farm
from player import WALK_SPEED_PIXELS_PER_SECOND

MAX_PER_ZONE = 3
SPEED_RATIO = 1.0  # 플레이어 속도 대비 배율 (동물은 0.5)

states = []


def speed():
    return WALK_SPEED_PIXELS_PER_SECOND * SPEED_RATIO


def count(crop):
    return sum(1 for f in states if f["crop"] == crop)


def at_limit(crop):
    return count(crop) >= MAX_PER_ZONE


def hire(crop):
    """농부 고용. 제한 초과 시 False."""
    if at_limit(crop):
        return False
    x, y = _random_spot(crop)
    states.append(
        {
            "crop": crop,
            "x": x,
            "y": y,
            "tx": x,
            "ty": y,
            "facing": "right",
            "moving": False,
            "frame": 0,
            "frame_timer": 0.0,
            "harvest_until": 0.0,
            "last_update": get_time(),
        }
    )
    return True


def _random_spot(crop):
    left, bottom, right, top = farm.plow_rect(crop)
    while True:
        x = random.uniform(left + 16, right - 16)
        y = random.uniform(bottom + 16, top - 16)
        if farm.cell_at(crop, x, y) != farm.SPRINKLER_CELL:
            return x, y
