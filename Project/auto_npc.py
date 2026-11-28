# 자동화 NPC: 광부(광산 시각·알림)와 농부(재배 자동화) 통합 모듈
# 농부 이동 속도는 플레이어 속도 기반 (농장_PRD 4절)
import math
import random

from pico2d import get_time, load_font, load_image

import camera
import farm
import game_state
import ranch
from player import WALK_SPEED_PIXELS_PER_SECOND


# frames inside mine_miner_mining.png (left, bottom, width, height)
FRAMES = (
    (69, 0, 214, 660),
    (370, 0, 226, 660),
    (684, 0, 223, 660),
    (981, 0, 315, 660),
    (1296, 0, 256, 660),
    (1624, 0, 258, 660),
    (1941, 0, 225, 660),
)
CYCLE_SECONDS = 2.0
FRAME_DURATION = CYCLE_SECONDS / len(FRAMES)
REF_HEIGHT = 588
DRAW_HEIGHT_SCALE = 1.3
DRAW_HEIGHT = 96 * DRAW_HEIGHT_SCALE


class Miner:
    image = None
    font = None

    def __init__(self, x, y, ore_name):
        self.x = x
        self.y = y
        self.ore_name = ore_name
        self.frame = 0
        self.frame_timer = 0.0
        self.last_update_time = get_time()
        self.last_cycle = game_state.miner_cycle_count
        self.notification = None
        self.notification_started = 0
        if Miner.image is None:
            Miner.image = load_image("assets/npc/mine_miner_mining.png")
        if Miner.font is None:
            Miner.font = load_font(r"C:\Windows\Fonts\consolab.ttf", 10)
        self.image = Miner.image

    def update(self):
        current_time = get_time()
        delta_time = max(0.0, current_time - self.last_update_time)
        self.last_update_time = current_time
        self.frame_timer += delta_time
        while self.frame_timer >= FRAME_DURATION:
            self.frame = (self.frame + 1) % len(FRAMES)
            self.frame_timer -= FRAME_DURATION
        if game_state.miner_cycle_count != self.last_cycle:
            self.last_cycle = game_state.miner_cycle_count
            self.notification = f"{self.ore_name.upper()} * 1"
            self.notification_started = current_time

    def draw(self):
        left, bottom, width, height = FRAMES[self.frame]
        scale = DRAW_HEIGHT / REF_HEIGHT
        draw_width = width * scale
        draw_height = height * scale
        # keep feet on the same ground line for every frame
        py = self.y + (draw_height - DRAW_HEIGHT) / 2
        self.image.clip_composite_draw(
            left,
            bottom,
            width,
            height,
            0,
            "",
            self.x - camera.x,
            py - camera.y,
            draw_width,
            draw_height,
        )
        self._draw_notification()

    def _draw_notification(self):
        if not self.notification:
            return
        elapsed = get_time() - self.notification_started
        duration = 1.0
        if elapsed >= duration:
            self.notification = None
            return
        progress = elapsed / duration
        rise = 18 * progress
        start_color = (255, 239, 177)
        end_color = (95, 95, 95)
        color = tuple(
            int(start + (end - start) * progress)
            for start, end in zip(start_color, end_color)
        )
        Miner.font.draw(
            self.x - camera.x - 24,
            self.y + 62 - camera.y + rise,
            self.notification,
            color,
        )


# 농부 고용 데이터와 배치
# 이동 속도는 플레이어 속도 기반 (농장_PRD 4절: 자동 NPC = 플레이어, 동물 = 그 절반)


MAX_PER_ZONE = 3
SPEED_RATIO = 0.5  # 플레이어 속도의 절반 (동물도 동일 배율)
MOTION_SECONDS = 2.0  # 수확·심기 동작 모션 전체 시간 (스프라이트 4프레임과 동일)

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
            "motion_until": 0.0,
            "action": None,
            "last_update": get_time(),
        }
    )
    game_state.npc_farmer_counts[crop] = count(crop)
    return True


def sync_hires():
    """저장값과 고용 직원 상태를 맞춘다 (로드 후 복원·슬롯 간 재설정)."""
    crops = {f["crop"] for f in states} | set(game_state.npc_farmer_counts)
    for crop in crops:
        target = game_state.npc_farmer_counts.get(crop, 0)
        while count(crop) > target:
            for index, f in enumerate(states):
                if f["crop"] == crop:
                    del states[index]
                    break
        while count(crop) < target and hire(crop):
            pass
    zones = {m["animal"] for m in manager_states} | set(
        game_state.npc_manager_counts
    )
    for animal in zones:
        target = game_state.npc_manager_counts.get(animal, 0)
        while count_managers(animal) > target:
            for index, m in enumerate(manager_states):
                if m["animal"] == animal:
                    del manager_states[index]
                    break
        while count_managers(animal) < target and hire_manager(animal):
            pass


def update():
    """무작위 이동 + 발밑 작물 관리 (심기·수확은 모션 후 결과 적용).

    장면 밖에서도 진행된다.
    """
    now = get_time()
    ensure_animal_population()
    _update_animals(now)
    _update_managers(now)
    _update_breeder(now)
    for f in states:
        delta = max(0.0, now - f["last_update"])
        f["last_update"] = now
        if now < f["motion_until"]:
            f["moving"] = False
            continue
        if f["action"] is not None:
            _apply_action(f, now)
            f["action"] = None
            f["moving"] = False
            continue
        index = farm.cell_at(f["crop"], f["x"], f["y"])
        if (
            index is not None
            and index != farm.SPRINKLER_CELL
            and not _cell_busy(f["crop"], index, f)
        ):
            slot = game_state.crop_slots.get((f["crop"], index))
            stage_seconds = game_state.crop_stage_seconds(farm.STAGE_SECONDS)
            stage = (
                farm.crop_stage(slot, now, stage_seconds)
                if slot is not None
                else None
            )
            if stage is None:
                #빈 칸이거나 수확 직후 재성장 대기 칸 → 다시 심는다
                _start_motion(f, now, ("plant", index))
                continue
            if stage == farm.READY_STAGE:
                _start_motion(f, now, ("harvest", index))
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


def _cell_busy(crop, index, worker):
    """다른 농부가 같은 칸을 작업 중이면 True."""
    for other in states:
        if other is worker or other["crop"] != crop:
            continue
        if other["action"] is not None and other["action"][1] == index:
            return True
    return False


def _start_motion(f, now, action):
    """동작 모션을 시작한다. 결과는 모션이 끝난 뒤 적용된다."""
    f["action"] = action
    f["motion_until"] = now + MOTION_SECONDS
    f["moving"] = False
    f["frame"] = 0
    f["frame_timer"] = 0.0


def _apply_action(f, now):
    """모션 종료 시점에 심기/수확 결과를 적용한다 (상태 재검증은 공통 함수가 수행)."""
    kind, index = f["action"]
    game_state.apply_farm_work(f["crop"], kind, index, now)


def _random_spot(crop):
    left, bottom, right, top = farm.plow_rect(crop)
    while True:
        x = random.uniform(left + 16, right - 16)
        y = random.uniform(bottom + 16, top - 16)
        if farm.cell_at(crop, x, y) != farm.SPRINKLER_CELL:
            return x, y


# --- 목장 동물 (울타리 안 자유 이동, 속도 = 플레이어의 절반) ---

animals = []
# --- 목장 관리인 (구역 자동 수확 — 목장_PRD 3.6) ---

MAX_MANAGERS = 1  # 구역당 최대 (목장_PRD 3.7)
MANAGER_INTERVAL = 5.0  # 자동 수확 주기(초)
BREEDER_INTERVAL = 60.0  # 교배 주기(초 — 목장_PRD 3.7)
manager_states = []
breeder_timers = {"chicken": 0.0, "cow": 0.0, "pig": 0.0}  # 구역별 교배 주기
_breeder_last = get_time()


def _random_animal_spot(animal):
    left, bottom, right, top = ranch.zone_rect(animal)
    return (
        random.uniform(left + 16, right - 16),
        random.uniform(bottom + 16, top - 16),
    )


def spawn_animal(animal):
    x, y = _random_animal_spot(animal)
    animals.append(
        {
            "animal": animal,
            "x": x,
            "y": y,
            "tx": x,
            "ty": y,
            "facing": "right",
            "moving": False,
            "frame": 0,
            "frame_timer": 0.0,
            "last_update": get_time(),
        }
    )


def count_animals(animal):
    return sum(1 for a in animals if a["animal"] == animal)


def remove_animal(animal):
    for index, a in enumerate(animals):
        if a["animal"] == animal:
            del animals[index]
            return True
    return False


def ensure_animal_population():
    """game_state.animal_counts만큼 동물 상태를 채운다 (시작 배치·구매 반영)."""
    for animal in game_state.animal_counts:
        while count_animals(animal) < game_state.animal_counts[animal]:
            spawn_animal(animal)


def count_managers(animal):
    return sum(1 for m in manager_states if m["animal"] == animal)


def at_manager_limit(animal):
    return count_managers(animal) >= MAX_MANAGERS


def hire_manager(animal):
    """구역 관리인 고용. 구역당 1명 초과 시 False."""
    if at_manager_limit(animal):
        return False
    x, y = _random_animal_spot(animal)
    manager_states.append(
        {
            "animal": animal,
            "x": x,
            "y": y,
            "tx": x,
            "ty": y,
            "facing": "right",
            "moving": False,
            "frame": 0,
            "frame_timer": 0.0,
            "last_update": get_time(),
            "work_timer": 0.0,
            "action": None,
            "motion_until": 0.0,
        }
    )
    game_state.npc_manager_counts[animal] = count_managers(animal)
    return True


def _apply_manager_collect(m, now):
    """관리인 수확 결과 적용 (재검증 후 지급 + 이벤트 통보)."""
    animal = m["animal"]
    amount = game_state.animal_counts[animal]
    if amount <= 0:
        return
    if ranch.cooldown_remaining(animal) > 0:
        return
    resource = ranch.RESOURCE[animal]
    game_state.collected_items[resource] += amount
    game_state.animal_cooldowns[animal] = now
    game_state.ranch_events.append((animal, resource, amount))


def _update_breeder(now):
    """교배 전문가: 구역별 1명, 담당 구역 동물만 주기마다 +1 (상한 준수)."""
    global _breeder_last
    delta = max(0.0, now - _breeder_last)
    _breeder_last = now
    for animal in ranch.ANIMAL_ORDER:
        if not game_state.breeders.get(animal):
            breeder_timers[animal] = 0.0
            continue
        breeder_timers[animal] += delta
        if breeder_timers[animal] < BREEDER_INTERVAL:
            continue
        breeder_timers[animal] = 0.0
        count = game_state.animal_counts[animal]
        if 2 <= count < game_state.ANIMAL_LIMIT_PER_ZONE:
            game_state.animal_counts[animal] += 1


def _update_managers(now):
    for m in manager_states:
        delta = max(0.0, now - m["last_update"])
        m["last_update"] = now
        if now < m["motion_until"]:
            m["moving"] = False
            continue
        if m["action"] is not None:
            _apply_manager_collect(m, now)
            m["action"] = None
            m["work_timer"] = 0.0
            m["moving"] = False
            continue
        # 울타리 안 무작위 이동 (동물과 동일)
        dx = m["tx"] - m["x"]
        dy = m["ty"] - m["y"]
        distance = math.hypot(dx, dy)
        step = speed() * delta
        if distance <= step:
            m["x"], m["y"] = m["tx"], m["ty"]
            m["moving"] = False
            m["tx"], m["ty"] = _random_animal_spot(m["animal"])
        else:
            m["x"] += dx / distance * step
            m["y"] += dy / distance * step
            m["moving"] = True
            m["facing"] = "left" if dx < 0 else "right"
        # 주기 체크: 준비됐으면 2초 모션 -> 결과 적용
        m["work_timer"] += delta
        if m["work_timer"] >= MANAGER_INTERVAL:
            if (
                game_state.animal_counts[m["animal"]] > 0
                and ranch.cooldown_remaining(m["animal"]) <= 0
            ):
                m["action"] = "collect"
                m["motion_until"] = now + MOTION_SECONDS
                m["moving"] = False
                m["frame"] = 0
                m["frame_timer"] = 0.0


def _update_animals(now):
    for a in animals:
        delta = max(0.0, now - a["last_update"])
        a["last_update"] = now
        dx = a["tx"] - a["x"]
        dy = a["ty"] - a["y"]
        distance = math.hypot(dx, dy)
        step = speed() * delta
        if distance <= step:
            a["x"], a["y"] = a["tx"], a["ty"]
            a["moving"] = False
            a["tx"], a["ty"] = _random_animal_spot(a["animal"])
        else:
            a["x"] += dx / distance * step
            a["y"] += dy / distance * step
            a["moving"] = True
            a["facing"] = "left" if dx < 0 else "right"
