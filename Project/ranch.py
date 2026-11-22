# 목장 레이아웃과 동물 구역 (목장_PRD 3.1 / 3.2)
# 좌표는 pico2d 기준(원점 좌측 하단, y 위쪽 증가), 농사지와 동일 스케일 880x880
from pico2d import get_time, load_font, load_image
from sdl2 import SDL_KEYDOWN, SDLK_SPACE

import auto_npc
import camera
import game_state

SIZE = 880
EXIT = (440, 790)  # 중앙 상단
MERCHANT = (120, 680)  # 좌측 상단 (구매)
SELL_MERCHANT = (120, 555)  # 구매 상인 아래 (판매)
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
COOLDOWN_SECONDS = 120  # 자원 재획득 쿨다운 (목장_PRD 3.7 확정)
BREEDER_POSITION = (440, 440)  # 구역 사이 중앙 (보유 시에만 표시)

# 동물 -> 획득 자원 (목장_PRD 3.2)
RESOURCE = {
    "chicken": "egg",
    "cow": "milk",
    "pig": "mushroom",
}
# 동물 -> 사냥 시 획득하는 고기 (목장_PRD 3.4)
MEAT = {
    "chicken": "chicken",
    "cow": "beef",
    "pig": "pork",
}


def cooldown_remaining(animal):
    """남은 재획득 시간(초). 준비됐으면 0 이하."""
    last = game_state.animal_cooldowns.get(animal)
    if last is None:
        return 0.0
    return COOLDOWN_SECONDS - (get_time() - last)


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


def fence_blocked(x, y):
    """좌표가 울타리 줄 위면 True. 하단 중앙 게이트 구간은 통과 허용."""
    side_half = RanchZone.FENCE_SIDE_WIDTH / 2
    rail_half = RanchZone.RAIL_HEIGHT / 2
    gate_half = RanchZone.GATE_HALF_WIDTH
    for animal in ZONES:
        x0, y0, x1, y1 = zone_rect(animal)
        cx = (x0 + x1) / 2
        # 세로 줄(좌우): 코너에서 가로 조각 높이만큼 위아래로 이어짐
        if (y0 - rail_half) <= y <= (y1 + rail_half) and (
            abs(x - x0) <= side_half or abs(x - x1) <= side_half
        ):
            return True
        # 가로 줄: 좌우 세로 조각 폭까지 이어짐
        if (x0 - side_half) <= x <= (x1 + side_half):
            if abs(y - y1) <= rail_half:
                return True  # 상단은 봉쇄
            if abs(y - y0) <= rail_half and abs(x - cx) > gate_half:
                return True  # 하단은 게이트만 통과
    return False


class RanchZone:
    """동물 구역: 울타리(가로·세로 조각 + 게이트)와 동물·타이머 렌더링."""

    fence_image = None  # 세로 조각 (fence_tile_length 콘텐츠)
    fence_rail = None  # 가로 조각 (fence_tile_width 콘텐츠)
    gate_image = None
    font = None
    manager_images = {}

    # 원본 이미지 여백 제외 콘텐츠 클립 (left, bottom, width, height)
    FENCE_VERTICAL_CLIP = (17, 32, 1170, 1203)
    FENCE_HORIZONTAL_CLIP = (1, 1, 62, 37)
    FENCE_SIDE_WIDTH = 48  # 세로 조각 표시 폭
    RAIL_HEIGHT = 29  # 가로 조각 표시 높이
    TILE_COUNT = 5  # 가로 조각 개수(폭/5)
    VERTICAL_TILE_COUNT = 3  # 세로 조각 개수(높이/3)
    GATE_HALF_WIDTH = 32  # 게이트 통과 구간(반쪽)

    def __init__(self, animal, player):
        self.animal = animal
        self.player = player
        self.sheet = None
        self.pending = None
        self.notification = None
        self.notification_started = 0
        if RanchZone.fence_image is None:
            RanchZone.fence_image = load_image(
                "assets/buildings/fence_tile_length.png"
            )
            RanchZone.fence_rail = load_image(
                "assets/buildings/fence_tile_width.png"
            )
            RanchZone.gate_image = load_image("assets/buildings/fence_gate.png")
        if RanchZone.font is None:
            RanchZone.font = load_font(r"C:\Windows\Fonts\consolab.ttf", 14)
        for key, path in (
            ("idle", "assets/npc/ranch_manager_idle.png"),
            ("walk", "assets/npc/ranch_manager_walk.png"),
            ("harvest", "assets/npc/ranch_manager_harvest.png"),
        ):
            if key not in RanchZone.manager_images:
                RanchZone.manager_images[key] = load_image(path)
        self.sheet = load_image(f"assets/npc/animal_{animal}.png")

    def handle_event(self, event):
        """구역 안 Space: 2초 작업 모션 후 자원 획득 (목장_PRD 3.3/3.7)."""
        if event.type != SDL_KEYDOWN or event.key != SDLK_SPACE:
            return
        if self.player.movement_locked or self.player.farm_work:
            return
        if not zone_at(self.animal, self.player.x, self.player.y):
            return
        if self.pending is not None:
            return
        if game_state.animal_counts[self.animal] <= 0:
            return  # 동물 0마리 구역은 무응답
        if cooldown_remaining(self.animal) > 0:
            return  # 재획득 전 중복 획득 불가
        now = get_time()
        # 칼 보유 시 사냥(자원+고기), 없으면 자원만 획득
        kind = "hunt" if game_state.hunting_knives > 0 else "collect"
        if not self.player.start_farm_work(auto_npc.MOTION_SECONDS):
            return
        self.pending = (kind, now + auto_npc.MOTION_SECONDS)

    def update(self):
        # 관리인 자동 수확 이벤트 -> 구역 알림
        now = get_time()
        mine = [e for e in game_state.ranch_events if e[0] == self.animal]
        if mine:
            game_state.ranch_events[:] = [
                e for e in game_state.ranch_events if e[0] != self.animal
            ]
            _, resource, amount = mine[-1]
            self.notification = f"{resource.upper()} * {amount}"
            self.notification_started = now
        if self.pending is None:
            return
        kind, done_at = self.pending
        now = get_time()
        if now < done_at:
            return
        self.pending = None
        if kind not in ("collect", "hunt"):
            return
        amount = game_state.animal_counts[self.animal]
        if amount <= 0:
            return
        resource = RESOURCE[self.animal]
        game_state.collected_items[resource] += amount
        game_state.animal_cooldowns[self.animal] = now
        note = f"{resource.upper()} * {amount}"
        # 모션 종료 시점에 칼이 남아있으면 사냥 처리 (칼 1개 + 동물 1마리 감소)
        if kind == "hunt" and game_state.hunting_knives > 0:
            game_state.hunting_knives -= 1
            meat = MEAT[self.animal]
            game_state.collected_items[meat] += 1
            game_state.animal_counts[self.animal] -= 1
            auto_npc.remove_animal(self.animal)
            note += f" + {meat.upper()}"
        self.notification = note
        self.notification_started = now

    def draw(self):
        self._draw_fence()
        self._draw_animals()
        self._draw_managers()
        self._draw_cooldown_timer()
        self._draw_notification()

    def _draw_fence(self):
        """세로 조각(좌우) + 가로 조각 타일(상단·하단) + 하단 중앙 게이트."""
        x0, y0, x1, y1 = zone_rect(self.animal)
        cx, cy = ZONES[self.animal]
        gate_cx = (x0 + x1) / 2
        # 세로 조각: 좌·우측면에 3개씩 스택 (길게 늘리지 않고 반복 배치)
        segment_height = ZONE_HEIGHT / RanchZone.VERTICAL_TILE_COUNT
        for side_x in (x0, x1):
            for index in range(RanchZone.VERTICAL_TILE_COUNT):
                sy = y1 - segment_height / 2 - index * segment_height
                RanchZone.fence_image.clip_composite_draw(
                    *RanchZone.FENCE_VERTICAL_CLIP,
                    0,
                    "",
                    side_x - camera.x,
                    sy - camera.y,
                    RanchZone.FENCE_SIDE_WIDTH,
                    segment_height,
                )
        # 가로 조각: 상단 전부 / 하단은 게이트 칸 제외
        step = ZONE_WIDTH / RanchZone.TILE_COUNT
        for index in range(RanchZone.TILE_COUNT):
            tx = x0 + step / 2 + index * step
            RanchZone.fence_rail.clip_composite_draw(
                *RanchZone.FENCE_HORIZONTAL_CLIP,
                0,
                "",
                tx - camera.x,
                y1 - camera.y,
                step,
                RanchZone.RAIL_HEIGHT,
            )
            if abs(tx - gate_cx) >= RanchZone.GATE_HALF_WIDTH:
                RanchZone.fence_rail.clip_composite_draw(
                    *RanchZone.FENCE_HORIZONTAL_CLIP,
                    0,
                    "",
                    tx - camera.x,
                    y0 - camera.y,
                    step,
                    RanchZone.RAIL_HEIGHT,
                )
        # 게이트: 하단 중앙 (마지막에 그려 위로 올라옴)
        RanchZone.gate_image.draw(gate_cx - camera.x, y0 - camera.y, 64, 64)

    def _draw_managers(self):
        now = get_time()
        for m in auto_npc.manager_states:
            if m["animal"] != self.animal:
                continue
            delta = max(0.0, now - m.setdefault("anim_time", now))
            m["anim_time"] = now
            in_motion = now < m["motion_until"]
            frame_duration = (
                auto_npc.MOTION_SECONDS / 4 if in_motion else 0.15
            )
            m["frame_timer"] += delta
            while m["frame_timer"] >= frame_duration:
                m["frame"] = (m["frame"] + 1) % 4
                m["frame_timer"] -= frame_duration
            if in_motion:
                image = RanchZone.manager_images["harvest"]
            elif m["moving"]:
                image = RanchZone.manager_images["walk"]
            else:
                image = RanchZone.manager_images["idle"]
            flip = "h" if m["facing"] == "left" else ""
            image.clip_composite_draw(
                m["frame"] * 64,
                0,
                64,
                64,
                0,
                flip,
                m["x"] - camera.x,
                m["y"] - camera.y,
                56,
                64,
            )

    def _draw_cooldown_timer(self):
        """구역 우측 하단 내측에 남은 재획득 시간(MM:SS) 표시 (노란색 — 회색은 안 보임)."""
        remaining = cooldown_remaining(self.animal)
        if remaining <= 0:
            return
        minutes, seconds = divmod(int(remaining + 0.999), 60)
        x0, y0, x1, y1 = zone_rect(self.animal)
        RanchZone.font.draw(
            x1 - 55 - camera.x,
            y0 + 8 - camera.y,
            f"{minutes:02d}:{seconds:02d}",
            (255, 224, 120),
        )

    def _draw_notification(self):
        if not self.notification:
            return
        elapsed = get_time() - self.notification_started
        duration = 1.0
        if elapsed >= duration:
            self.notification = None
            return
        progress = elapsed / duration
        rise = 30 * progress
        # 목장 글자는 노란색 계열 유지 (회색 페이드아웃은 안 보임)
        start_color = (255, 239, 177)
        end_color = (255, 170, 60)
        color = tuple(
            int(start + (end - start) * progress)
            for start, end in zip(start_color, end_color)
        )
        RanchZone.font.draw(
            self.player.x - camera.x - 30,
            self.player.y - camera.y + 45 + rise,
            self.notification,
            color,
        )

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
