# HARVEST TABLE 스프라이트·이미지 제작 PRD

## 1. 문서 목적

이 문서는 [PRD.md](./PRD.md)의 개발 순서에 맞춰 게임에 필요한 이미지와 스프라이트를 정의한다.

- 우선순위가 높은 이미지부터 제작한다.
- 초기에는 임시 도형과 색상으로 대체할 수 있다.
- 실제 스프라이트로 교체해도 충돌 영역과 상호작용 영역은 유지한다.
- 모든 이미지의 크기, 방향, 애니메이션 프레임은 구현 과정에서 조정할 수 있다.

## 2. 공통 제작 기준

### 2.1 파일 형식

| 항목 | 기준 |
| --- | --- |
| 파일 형식 | PNG |
| 배경 | 투명 배경 |
| 색상 | RGB 또는 RGBA |
| 픽셀 아트 | nearest-neighbor 방식으로 확대 |
| 파일명 | 영문 소문자와 언더스코어 사용 |
| 스프라이트 시트 | 같은 종류의 프레임을 가로 또는 격자 형태로 배치 |

### 2.2 권장 기준 크기

| 용도 | 기준 크기 |
| --- | --- |
| 소형 아이콘 | 32×32 |
| 아이템·작물 아이콘 | 48×48 |
| 플레이어·손님 | 64×64 |
| 동물·직원 | 64×64 또는 96×96 |
| 건물·시설 | 128×128 이상 |
| 배경 타일 | 32×32 또는 64×64 |
| UI 패널 | 9-slice 또는 충분한 여백의 PNG |

정확한 표시 크기는 게임 창 해상도와 실제 타일 크기를 정한 뒤 확정한다.

## 3. 제작 우선순위

### 1순위: 게임 실행에 필요한 이미지

- 플레이어
- 기본 맵 바닥과 건물
- 건물 입구
- 광산 채굴 공간
- 농사지 재배 칸
- 목장 울타리
- 뷔페 입구·계산대·식탁·의자

### 2순위: 핵심 상호작용 이미지

- 광물
- 작물
- 동물
- 요리
- 상인·요리사·손님
- 곡괭이·괭이·비료·사냥용 칼

### 3순위: 자동화와 피드백 이미지

- 광부·농부·관리인·직원
- 채굴·수확·요리·결제 이펙트
- 해금·잠금·업그레이드 표시
- 손님 상태 표시

### 4순위: 장식과 완성도 보강

- 건물 외관 변화
- 뷔페 장식
- 환경 오브젝트
- 결과 화면 장식
- 추가 애니메이션과 파티클

## 4. 기본 공통 스프라이트

### 4.1 플레이어

| 파일명 예시 | 내용 | 필수 프레임 |
| --- | --- | --- |
| `player_front.png` | 정면 기본 자세 | 1 |
| `player_walk_side.png` | 좌우 이동 | 대기 1, 이동 4 |
| `player_walk_top.png` | `top view` 이동 | 상·하·좌·우 각 4 |
| `player_interact.png` | `Space` 상호작용 | 2 |
| `player_tool.png` | 도구 사용 자세 | 도구별 2~4 |

### 4.2 공통 타일

| 파일명 예시 | 내용 |
| --- | --- |
| `ground_tile.png` | 기본 맵 바닥 |
| `path_tile.png` | 건물 사이 이동 경로 |
| `wall_tile.png` | 건물 벽과 경계 |
| `water_tile.png` | 물 또는 장식용 지형 |
| `blocked_tile.png` | 이동 불가 영역 |
| `interaction_marker.png` | 상호작용 가능 표시 |

### 4.3 공통 상태 표시

| 파일명 예시 | 내용 |
| --- | --- |
| `locked_overlay.png` | 잠긴 시설 표시 |
| `unlock_effect.png` | 해금 효과 |
| `item_count_icon.png` | 수량 표시 보조 아이콘 |
| `money_icon.png` | 돈 아이콘 |
| `success_effect.png` | 성공 피드백 |
| `failure_effect.png` | 실패 피드백 |

## 5. 기본 맵 이미지

### 5.1 배경과 건물

| 파일명 예시 | 내용 | 우선순위 |
| --- | --- | --- |
| `world_background.png` | 좌우로 긴 기본 맵 배경 | 1 |
| `house_exterior.png` | 집 외관 | 1 |
| `farm_exterior.png` | 농사지 외관 | 1 |
| `ranch_exterior.png` | 목장 외관 | 1 |
| `mine_exterior.png` | 광산 외관 | 1 |
| `buffet_exterior.png` | 뷔페 외관 | 1 |
| `building_door.png` | 건물 입구 | 1 |
| `building_signs.png` | 건물 이름 표지판 | 2 |

### 5.2 기본 맵 환경

- 나무, 돌, 풀, 꽃
- 길과 표지판
- 카메라 이동 시 반복 가능한 배경 타일
- 건물별 외부 장식
- 플레이어가 화면 밖으로 나가지 않도록 표시하는 경계

## 6. 광산 스프라이트

### 6.1 광산 외부

| 파일명 예시 | 내용 |
| --- | --- |
| `mine_entrance.png` | 광산 출입구 |
| `mine_shopkeeper.png` | 광산 상인 |
| `tunnel_entrance_coal.png` | 석탄 땅굴 입구 |
| `tunnel_entrance_iron.png` | 철 땅굴 입구 |
| `tunnel_entrance_gold.png` | 금 땅굴 입구 |
| `tunnel_locked_board.png` | 잠긴 땅굴의 X자 나무판자 |

### 6.2 광산 내부

| 파일명 예시 | 내용 |
| --- | --- |
| `mine_wall_tile.png` | 광산 벽 |
| `mine_floor_tile.png` | 광산 바닥 |
| `ore_mining_spot.png` | 플레이어 채굴 공간 |
| `ore_mining_highlight.png` | 채굴 공간 강조 표시 |
| `mine_exit.png` | 광산 내부 출구 |

### 6.3 광물과 도구

| 파일명 예시 | 내용 |
| --- | --- |
| `ore_coal.png` | 석탄 |
| `ore_iron.png` | 철 |
| `ore_gold.png` | 금 |
| `pickaxe_wood.png` | 나무 곡괭이 |
| `pickaxe_stone.png` | 돌 곡괭이 |
| `pickaxe_iron.png` | 철 곡괭이 |
| `mining_effect.png` | 곡괭이질 이펙트 |
| `ore_success_effect.png` | 채굴 성공 이펙트 |
| `ore_failure_effect.png` | 채굴 실패 이펙트 |

### 6.4 광부

- `miner_idle.png`: 대기
- `miner_work.png`: 곡괭이질
- `miner_walk.png`: 이동
- `miner_tool.png`: 광부가 사용하는 곡괭이
- 광부 1·2는 색상 또는 장비 차이로 구분할 수 있다.

## 7. 농사지 스프라이트

### 7.1 공간과 시설

| 파일명 예시 | 내용 |
| --- | --- |
| `farm_ground_tile.png` | 농사지 바닥 |
| `farm_entrance.png` | 농사지 입구 |
| `farm_shopkeeper.png` | 농사지 상인 |
| `crop_plot_locked.png` | 잠긴 재배 공간 |
| `crop_plot_tile.png` | 재배 칸 |
| `sprinkler.png` | 중앙 스프링클러 |
| `sprinkler_effect.png` | 물 공급 이펙트 |

### 7.2 작물 성장 단계

각 작물은 `seed`, `sprout`, `growing`, `ready` 4단계를 우선 제작한다.

| 작물 | 파일명 예시 |
| --- | --- |
| 밀 | `crop_wheat_seed.png`, `crop_wheat_ready.png` |
| 감자 | `crop_potato_seed.png`, `crop_potato_ready.png` |
| 딸기 | `crop_strawberry_seed.png`, `crop_strawberry_ready.png` |

### 7.3 농기구와 농부

- `hoe.png`: 괭이
- `fertilizer.png`: 비료
- `farmer_idle.png`: 농부 대기
- `farmer_walk_top.png`: 농부 이동
- `farmer_harvest.png`: 농부 수확
- `harvest_effect.png`: 수확 이펙트

## 8. 목장 스프라이트

### 8.1 공간과 시설

| 파일명 예시 | 내용 |
| --- | --- |
| `ranch_ground_tile.png` | 목장 바닥 |
| `ranch_entrance.png` | 목장 입구 |
| `ranch_shopkeeper.png` | 목장 상인 |
| `fence_tile.png` | 울타리 |
| `fence_gate.png` | 울타리 문 |
| `animal_feed.png` | 동물 먹이 또는 보조 오브젝트 |

### 8.2 동물

| 동물 | 필수 프레임 |
| --- | --- |
| 닭 | 대기, 이동, 자원 획득 |
| 소 | 대기, 이동, 자원 획득 |
| 돼지 | 대기, 이동, 자원 획득, 사냥 대상 |

파일명 예시:

- `animal_chicken.png`
- `animal_cow.png`
- `animal_pig.png`
- `animal_resource_effect.png`
- `hunting_knife.png`
- `meat_obtain_effect.png`

### 8.3 목장 관리 인력

- `ranch_manager_idle.png`
- `ranch_manager_walk.png`
- `ranch_manager_harvest.png`
- `breeder_idle.png`
- `breeding_effect.png`

## 9. 뷔페 스프라이트

### 9.1 공간과 시설

| 파일명 예시 | 내용 |
| --- | --- |
| `buffet_floor_tile.png` | 뷔페 바닥 |
| `buffet_entrance.png` | 뷔페 입구 |
| `cashier_counter.png` | 계산대 |
| `cash_register.png` | 포스기 또는 금고 |
| `buffet_shopkeeper.png` | 뷔페 상인 |
| `chef.png` | 요리사 |
| `cooking_area.png` | 요리 공간 |
| `dish_display.png` | 요리 진열 공간 |
| `table.png` | 식탁 |
| `chair.png` | 의자 |
| `decoration_basic.png` | 기본 장식 |

### 9.2 식탁과 의자 상태

- `table_empty.png`: 빈 식탁
- `table_occupied.png`: 손님이 사용하는 식탁
- `chair_empty.png`: 빈 의자
- `chair_occupied.png`: 손님이 앉은 의자
- `table_upgrade_01.png`: 식탁 업그레이드 단계
- `chair_upgrade_01.png`: 의자 업그레이드 단계

## 10. 요리와 재료 이미지

### 10.1 재료 아이콘

| 파일명 예시 | 내용 |
| --- | --- |
| `ingredient_wheat.png` | 밀 |
| `ingredient_potato.png` | 감자 |
| `ingredient_strawberry.png` | 딸기 |
| `ingredient_egg.png` | 달걀 |
| `ingredient_milk.png` | 우유 |
| `ingredient_mushroom.png` | 버섯 |
| `ingredient_meat.png` | 고기 |

### 10.2 요리 아이콘과 진열 스프라이트

| 요리 | 파일명 예시 |
| --- | --- |
| 감자튀김 | `dish_french_fries.png` |
| 계란빵 | `dish_egg_bread.png` |
| 딸기 디저트 | `dish_strawberry_dessert.png` |
| 버섯 수프 | `dish_mushroom_soup.png` |
| 고기 스테이크 | `dish_meat_steak.png` |

각 요리는 다음 상태를 지원한다.

- 제작 전 아이콘
- 요리 공간에 배치된 상태
- 손님이 선택하는 상태
- 품절 또는 비활성 상태
- 판매·소비 피드백

## 11. 손님과 직원 스프라이트

### 11.1 손님

- `customer_walk_side.png`: 기본 맵 이동
- `customer_walk_top.png`: 뷔페 내부 이동
- `customer_waiting.png`: 입장·결제 대기
- `customer_order.png`: 요리 선택
- `customer_eating.png`: 식사
- `customer_sitting.png`: 착석
- `customer_leave.png`: 퇴장

손님은 여러 명이 동시에 등장할 수 있으므로 색상·헤어·의상 차이를 최소 3종 제공한다.

### 11.2 직원

- `staff_idle.png`
- `staff_walk_top.png`
- `staff_receive_customer.png`
- `staff_checkout.png`

직원은 손님 응대와 계산을 자동으로 수행한다.

## 12. UI 이미지

### 12.1 기본 HUD

- `hud_panel.png`
- `hud_money.png`
- `hud_inventory.png`
- `hud_time.png`
- `hud_goal.png`
- `hud_staff_count.png`

### 12.2 상점과 제작 UI

- `shop_window.png`
- `shop_slot.png`
- `shop_buy_button.png`
- `shop_locked_slot.png`
- `recipe_window.png`
- `recipe_slot.png`
- `craft_button.png`
- `insufficient_materials.png`

### 12.3 저장과 결과 화면

- `save_window.png`
- `save_slot_empty.png`
- `save_slot_used.png`
- `save_delete_confirm.png`
- `ending_window.png`
- `result_panel.png`
- `result_highlight.png`

## 13. 애니메이션 및 이펙트

### 13.1 필수 애니메이션

- 플레이어 이동과 상호작용
- 채굴과 광물 획득
- 작물 성장과 수확
- 동물 이동과 자원 획득
- 요리 제작
- 손님 걷기·착석·식사·퇴장
- 직원 자동 응대와 계산

### 13.2 공통 이펙트

- `effect_coin.png`: 돈 획득
- `effect_item_gain.png`: 아이템 획득
- `effect_upgrade.png`: 업그레이드
- `effect_unlock.png`: 해금
- `effect_cooking.png`: 요리 제작
- `effect_smoke.png`: 조리 연출
- `effect_water.png`: 스프링클러
- `effect_heart.png`: 손님 만족도

## 14. 개발 단계별 제작 순서

| 개발 단계 | 먼저 필요한 이미지 | 이후 제작 이미지 |
| --- | --- | --- |
| 0단계 | 임시 플레이어, 테스트 타일 | 공통 이펙트 |
| 1단계 | 기본 맵, 건물 외관, 입구 | 환경 장식 |
| 2단계 | 자원 아이콘, 돈 아이콘, HUD | 상세 인벤토리 UI |
| 3단계 | 광산, 땅굴, 광물, 곡괭이 | 광부 애니메이션, 채굴 이펙트 |
| 4단계 | 농사지, 재배 칸, 작물 성장 단계 | 농부, 수확 이펙트 |
| 5단계 | 울타리, 닭·소·돼지, 자원 아이콘 | 관리인, 교배·사냥 이펙트 |
| 6단계 | 뷔페 시설, 식탁·의자, 요리사, 요리 아이콘 | 시설 업그레이드 외형 |
| 7단계 | 손님, 계산대, 대기 줄 표시 | 식사·결제 애니메이션 |
| 8단계 | 광부·농부·관리인·직원 | 자동화 상태 이펙트 |
| 9단계 | 저장 UI | 삭제 확인과 오류 표시 |
| 10단계 | 엔딩·결과 UI, 통계 아이콘 | 결과 화면 장식 |
| 11단계 | 누락 이미지 보완 | 최종 배경·장식·연출 |

## 15. 임시 이미지 사용 기준

실제 리소스가 준비되지 않은 경우 다음 순서로 대체한다.

1. 색상 사각형으로 충돌과 위치를 검증한다.
2. 텍스트 라벨로 오브젝트 종류를 표시한다.
3. 단색 아이콘으로 자원과 요리를 구분한다.
4. 핵심 흐름이 완성된 뒤 최종 스프라이트로 교체한다.

임시 이미지 사용은 기능 미완료를 의미하지 않으며, 최종 제출 전 핵심 오브젝트는 실제 이미지로 교체한다.

## 16. 제작 완료 기준

- 모든 필수 오브젝트에 투명 배경 PNG가 있다.
- 스프라이트의 기준점과 표시 크기가 통일되어 있다.
- 같은 오브젝트의 방향과 애니메이션 프레임 수가 일관된다.
- 잠금·선택·사용·품절 상태가 시각적으로 구분된다.
- 이미지 교체 후에도 충돌과 상호작용 위치가 어긋나지 않는다.
- 광산부터 엔딩까지 모든 핵심 장면에서 필요한 리소스가 누락되지 않는다.

## 17. pixelfx 활용 가능 목록

참고 저장소: [patch-gg/pixelfx](https://github.com/patch-gg/pixelfx)

pixelfx는 코드로 생성되는 픽셀 아트 이펙트·애니메이션 라이브러리다. 저장소 README 기준으로 244개의 이펙트를 제공하며, 필요한 이펙트를 JavaScript에서 실행하거나 스프라이트 시트로 내보내 다른 엔진에서 사용할 수 있다. pico2d에서는 JavaScript 코드를 직접 불러오기보다 PNG 스프라이트 시트로 export한 뒤 사용하는 방식을 적용한다.

### 17.1 게임에 활용할 우선 목록

| 게임 용도 | pixelfx 카테고리 | 활용 가능한 이펙트 예시 |
| --- | --- | --- |
| 광산 채굴 성공·실패 | `impacts`, `nature`, `spawn & death` | blunt hit, hit flash, dirt explosion, poof |
| 곡괭이질·도구 충돌 | `melee`, `impacts` | hammer smash, heavy landing, ground slam |
| 광물·보석 획득 | `pickups`, `ui` | crystal shard, gem spin, collect burst, coin collect |
| 땅굴·시설 해금 | `transitions`, `ui` | iris, diamond wipe, achievement, confetti |
| 농사지 물 공급 | `water`, `weather` | fountain, geyser, rain splash, ripples |
| 작물 수확 | `nature`, `pickups` | healing bloom, leaf storm, collect burst |
| 동물 교배·부화 | `spawn & death`, `nature` | egg hatch, poof, healing bloom |
| 사냥용 칼·고기 획득 | `melee`, `impacts`, `spawn & death` | dagger flurry, critical hit, hit flash, coin drop |
| 요리 제작 | `fire`, `smoke` 대체 연출 | campfire, candle, fire ring, poof |
| 손님 결제·수익 | `ui`, `pickups` | coin collect, coin spin, achievement, confetti |
| 손님 만족도·상태 | `status`, `ui`, `holy` | charmed, heal, heart pickup, achievement |
| 엔딩·결과 화면 | `ui`, `transitions`, `holy` | achievement, confetti, iris, healing ring |
| 화면 전환 | `transitions` | blinds, burn away, crt off, glitch wipe, iris |

`smoke`는 README의 독립 카테고리로 확인되지 않으므로, 요리 연출에는 `fire`의 campfire·candle·fire ring과 `spawn & death`의 poof를 우선 검토한다.

### 17.2 카테고리별 제공 목록

저장소 README에 명시된 카테고리와 개수는 다음과 같다.

| 카테고리 | 개수 | 대표 목록 |
| --- | ---: | --- |
| `moves` | 12 | arrow shot, dash strike, earth stomp, fireball throw |
| `fire` | 12 | brazier, campfire, candle, fire breath |
| `explosions` | 12 | barrel explosion, big explosion, cartoon pow, dirt explosion |
| `water` | 12 | bubbles, drip, fountain, geyser |
| `ice` | 10 | blizzard vortex, freeze, frost breath, ice crystal |
| `lightning` | 11 | ball lightning, chain lightning, charge up, plasma ball |
| `sci-fi` | 12 | emp blast, energy core, force field, hologram |
| `melee` | 12 | claw swipe, dagger flurry, double slash, hammer smash |
| `impacts` | 11 | blunt hit, bullet impact, critical hit, ground slam |
| `projectiles` | 13 | arrow, bullet tracer, cannon shot, energy disc |
| `spawn & death` | 10 | coin drop, disintegrate, egg hatch, poof |
| `arcane` | 12 | arcane beam, arcane missiles, arcane orb, magic circle cast |
| `holy` | 10 | blessing, divine shield, heal, healing ring |
| `shadow` | 12 | black hole, curse, dark explosion, eclipse |
| `status` | 13 | bleeding, burning, charmed, confused, frozen |
| `nature` | 13 | acid splash, boulder, earth spike, healing bloom |
| `weather` | 12 | aurora, blizzard, cherry blossoms, falling leaves |
| `ui` | 12 | achievement, coin collect, combo counter, confetti |
| `pickups` | 11 | chest open, coin spin, collect burst, crystal shard |
| `transitions` | 10 | blinds, burn away, crt off, diamond wipe |
| `critters` | 12 | bat, bird, butterfly, fish school |

전체 파일은 저장소의 `src/fx/<category>/<name>.js` 구조로 제공되며, 정확한 이펙트 이름과 전체 목록은 저장소의 [CATALOG.md](https://github.com/patch-gg/pixelfx/blob/main/docs/CATALOG.md)에서 확인한다.

### 17.3 적용 방법과 제한

1. 필요한 이펙트의 JavaScript 파일과 라이선스 상태를 확인한다.
2. pixelfx의 갤러리 또는 export 기능으로 스프라이트 시트를 생성한다.
3. PNG 시트의 프레임 순서와 프레임 시간을 기록한다.
4. pico2d에서 프레임 단위로 잘라 애니메이션 객체에 연결한다.
5. 실제 게임 화면에서 크기·색상·재생 속도를 조정한다.

- pixelfx는 캐릭터·건물·광물·작물·요리 등의 본체 스프라이트를 제공하는 목록이 아니다.
- 본체 스프라이트와 게임 전용 UI는 별도로 제작한다.
- README 기준 라이선스는 MIT이며, 저장소의 `NOTICE.md`와 라이선스 문구를 프로젝트 배포물에 함께 반영한다.
- pixelfx의 JavaScript 코드를 pico2d에서 직접 import하지 않는다.
