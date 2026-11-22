# 농부 고용 데이터와 배치
# 이동 속도는 플레이어 속도 기반 (농장_PRD 4절: 자동 NPC = 플레이어, 동물 = 그 절반)
import math
import random

from pico2d import get_time

import farm
import game_state
from player import WALK_SPEED_PIXELS_PER_SECOND

MAX_PER_ZONE = 3
SPEED_RATIO = 1.0  # 플레이어 속도 대비 배율 (동물은 0.5)
HARVEST_POSE_SECONDS = 0.5

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


def update():
    """무작위 이동 + 발밑의 성숙 작물 자동 수확 (장면 밖에서도 진행)."""
    now = get_time()
    for f in states:
        delta = max(0.0, now - f["last_update"])
        f["last_update"] = now
        if now < f["harvest_until"]:
            f["moving"] = False
            continue
        _try_harvest(f, now)
        if now < f["harvest_until"]:
            f["moving"] = False
            continue
        dx = f["tx"] - f["x"]
        dy = f["ty"] - f["y"]
        distance = math.hypot(dx, dy)
        step = speed() * delta
        if distance <= step:
            f["x"], f["y"] = f["tx"], f["ty"]
            f["moving"] = False
            f["tx"], f["ty"] = _random_spot(f["crop"])
        else:
            f["x"] += dx / distance * step
            f["y"] += dy / distance * step
            f["moving"] = True
            f["facing"] = "left" if dx < 0 else "right"


def _try_harvest(f, now):
    index = farm.cell_at(f["crop"], f["x"], f["y"])
    if index is None or index == farm.SPRINKLER_CELL:
        return
    slot = game_state.crop_slots.get((f["crop"], index))
    if slot is None:
        return
    stage_seconds = game_state.crop_stage_seconds(farm.STAGE_SECONDS)
    if farm.crop_stage(slot, now, stage_seconds) != farm.READY_STAGE:
        return
    game_state.collected_items[f["crop"]] += 1
    slot["harvested_at"] = now
    f["harvest_until"] = now + HARVEST_POSE_SECONDS


def _random_spot(crop):
    left, bottom, right, top = farm.plow_rect(crop)
    while True:
        x = random.uniform(left + 16, right - 16)
        y = random.uniform(bottom + 16, top - 16)
        if farm.cell_at(crop, x, y) != farm.SPRINKLER_CELL:
            return x, y
