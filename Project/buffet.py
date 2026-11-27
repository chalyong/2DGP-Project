# 뷔페 레이아웃 (뷔페_PRD 3.1)
# 좌표는 pico2d 기준(원점 좌측 하단, y 위쪽 증가), 배경 이미지(1243x1228)를 월드에 맞춰 스케일
SIZE = 880
EXIT = (440, 70)  # 하단 중앙 입구 (뷔페_PRD 3.1)
PLAYER_SPAWN = (440, 170)

# 구역 직사각형 (x0, y0, x1, y1) — 배경 이미지의 바닥 색 경계 실측 (뷔페_PRD 3.1)
ZONES = {
    "entrance": (0, 0, 880, 117),  # 하단 입구 (빨간 매트)
    "dining": (0, 117, 880, 458),  # 식사 공간 — 갈색 나무 마루
    "counter": (0, 458, 880, 590),  # 계산대 — 회색 타일
    "kitchen": (0, 590, 880, 880),  # 주방 — 밝은 회색 타일
}


def zone_at(x, y):
    """좌표가 속한 구역 이름. 범위 밖이면 None."""
    for name, (x0, y0, x1, y1) in ZONES.items():
        if x0 <= x < x1 and y0 <= y < y1:
            return name
    return None

