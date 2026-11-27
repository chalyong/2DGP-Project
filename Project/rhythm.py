# 4노트 리듬게임 판 (뷔페_PRD 3.3)
# b9: 판 표시와 노트 낙하 / b10: 판정(D/F/J/K)과 보상
import random

from pico2d import get_time, load_font, load_image
from sdl2 import SDL_KEYDOWN, SDLK_d, SDLK_f, SDLK_j, SDLK_k

import game_state
import shop

PANEL_CENTER_X = 400
PANEL_WIDTH = 340
PANEL_HEIGHT = 530
LANE_COUNT = 4
LANE_KEYS = (SDLK_d, SDLK_f, SDLK_j, SDLK_k)  # 레인 0~3 키
SPAWN_MIN_SECONDS = 0.5  # 시작 등장 간격(하한)
SPAWN_MAX_SECONDS = 1.0  # 시작 등장 간격(상한)
SPAWN_FLOOR_SECONDS = 0.2  # 시간이 지날수록 이 값까지 빨라짐 (노트 등장 속도)
SPAWN_RAMP_SECONDS = 30.0  # 시작 간격 -> 0.2초까지 감소하는 데 걸리는 시간
MAX_ACTIVE_NOTES = 2  # 시작 동시 노트 상한
MAX_ACTIVE_RAMP = 10  # 램프 동안 추가되는 상한 (2 -> 12)
FALL_SECONDS = 2.0  # 패널 상단 -> 히트라인 낙하 시간 (속도는 불변)
NOTE_LINGER_SECONDS = 0.35  # 히트라인 통과 후 제거 대기
PERFECT_WINDOW = 0.05  # 히트라인 ±초: PERFECT -> 2개 제작
GOOD_WINDOW = 0.30  # 히트라인 ±초: GOOD -> 1개 제작
NOTE_FRAME_SIZE = 52  # 노트 = 리듬 프레임 + 그 위 요리 아이콘
NOTE_ICON_SIZE = 30
HIT_RATIO = 0.16  # 패널 하단 기준 히트라인 높이


class RhythmGame:
    panel = None
    hitline = None
    frame = None
    error_font = None

    def __init__(self, requests, errors=()):
        if RhythmGame.panel is None:
            RhythmGame.panel = load_image("assets/ui/buffet_rhythm_panel.png")
            RhythmGame.hitline = load_image("assets/ui/buffet_rhythm_hitline.png")
            RhythmGame.frame = load_image("assets/ui/buffet_rhythm_frame.png")
            RhythmGame.error_font = load_font(
                r"C:\Windows\Fonts\consolab.ttf", 16
            )
        queue = []
        for name, quantity in requests:
            queue.extend([name] * quantity)
        random.shuffle(queue)
        self.queue = queue
        self.active = []  # {"name", "lane", "spawned_at"}
        self.errors = list(errors)
        self.started_at = get_time()
        self.next_spawn_at = get_time() + SPAWN_MIN_SECONDS
        self.last_label = None  # 판정 피드백 ("PERFECT +2" 등)
        self.last_label_time = -2.0

    def _progress(self, now):
        """난이도 진행도 0~1 (시작 후 SPAWN_RAMP_SECONDS까지 1)."""
        return min(1.0, (now - self.started_at) / SPAWN_RAMP_SECONDS)

    def spawn_interval_range(self, progress):
        """현재 진행도의 등장 간격 (min, max) — progress 1에서 0.2~0.2초."""
        low = SPAWN_MIN_SECONDS + (
            SPAWN_FLOOR_SECONDS - SPAWN_MIN_SECONDS
        ) * progress
        high = SPAWN_MAX_SECONDS + (
            SPAWN_FLOOR_SECONDS - SPAWN_MAX_SECONDS
        ) * progress
        return low, high

    def max_active(self, progress):
        """현재 진행도의 동시 노트 상한 — progress 1에서 12개."""
        return MAX_ACTIVE_NOTES + int(progress * MAX_ACTIVE_RAMP)

    def handle_event(self, event):
        """레인키 판정: 히트라인 창 안의 노트를 성공 처리하고 요리를 지급한다."""
        if event.type != SDL_KEYDOWN or event.key not in LANE_KEYS:
            return
        lane = LANE_KEYS.index(event.key)
        now = get_time()
        best = None
        best_delta = None
        for note in self.active:
            if note["lane"] != lane:
                continue
            delta = abs(now - (note["spawned_at"] + FALL_SECONDS))
            if delta <= GOOD_WINDOW and (
                best_delta is None or delta < best_delta
            ):
                best = note
                best_delta = delta
        if best is None:
            return
        self.active.remove(best)
        award = 2 if best_delta <= PERFECT_WINDOW else 1
        game_state.award_dish(best["name"], award)
        self.last_label = (
            f"PERFECT +{award}" if award == 2 else f"GOOD +{award}"
        )
        self.last_label_time = now

    @property
    def done(self):
        return not self.queue and not self.active

    @property
    def panel_left(self):
        return PANEL_CENTER_X - PANEL_WIDTH // 2

    @property
    def panel_bottom(self):
        return 300 - PANEL_HEIGHT // 2

    @property
    def hit_y(self):
        return self.panel_bottom + int(PANEL_HEIGHT * HIT_RATIO)

    def lane_x(self, lane):
        lane_width = PANEL_WIDTH / LANE_COUNT
        return self.panel_left + lane_width * (lane + 0.5)

    def update(self):
        now = get_time()
        progress = self._progress(now)
        if (
            self.queue
            and len(self.active) < self.max_active(progress)
            and now >= self.next_spawn_at
        ):
            name = self.queue.pop(0)
            self.active.append(
                {
                    "name": name,
                    "lane": random.randrange(LANE_COUNT),
                    "spawned_at": now,
                }
            )
            low, high = self.spawn_interval_range(progress)
            self.next_spawn_at = now + random.uniform(low, high)
        self.active = [
            note
            for note in self.active
            if now - note["spawned_at"] <= FALL_SECONDS + NOTE_LINGER_SECONDS
        ]

    def draw(self):
        top = self.panel_bottom + PANEL_HEIGHT
        hit_y = self.hit_y
        RhythmGame.panel.draw(
            PANEL_CENTER_X,
            self.panel_bottom + PANEL_HEIGHT // 2,
            PANEL_WIDTH,
            PANEL_HEIGHT,
        )
        # 히트라인: 노랑 선은 이미지 수직 중앙 (판정선 위에는 프레임을 그리지 않음)
        hit_height = int(230 * PANEL_WIDTH / 381)
        RhythmGame.hitline.draw(
            PANEL_CENTER_X, hit_y, PANEL_WIDTH, hit_height
        )
        # 낙하 노트: 리듬 프레임 위에 요리 아이콘을 얹어 내려옴
        now = get_time()
        for note in self.active:
            ratio = min((now - note["spawned_at"]) / FALL_SECONDS, 1.0)
            y = int(top - (top - hit_y) * ratio)
            x = int(self.lane_x(note["lane"]))
            RhythmGame.frame.draw(x, y, NOTE_FRAME_SIZE, NOTE_FRAME_SIZE)
            shop.draw_item_icon(
                note["name"],
                x,
                y,
                size=NOTE_ICON_SIZE,
                prefer_item=True,
            )
        # 레인키 안내와 판정 피드백
        for lane in range(LANE_COUNT):
            label = ("D", "F", "J", "K")[lane]
            RhythmGame.error_font.draw(
                int(self.lane_x(lane)) - 4,
                self.panel_bottom + 22,
                label,
                (200, 205, 215),
            )
        if self.last_label and now - self.last_label_time < 0.6:
            color = (255, 224, 120) if "PERFECT" in self.last_label else (235, 235, 235)
            RhythmGame.error_font.draw(
                400, hit_y + 70, self.last_label, color
            )
        if self.errors:
            RhythmGame.error_font.draw(
                400, 578, " / ".join(self.errors), (255, 150, 120)
            )
