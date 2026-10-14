# Verification Matrix 수동 검토 7건 결과 (S-06 끝, 마지막 batch 통합 검토 1차 B2 반영)

| 수동 검토(Matrix manual_reviews) | 결과 | 증거 |
| --- | --- | --- |
| CO-38 표시 조정 ③(T15 / check_b 1080 × 740) | 통과. 지난 화면 본문 548px로 넘침 없음, 체크 행 20px · 글자 14px(S-05) | ../../S-05/evidence/co38-metrics.json |
| CO-39 지난 화면 '그대로' 칩 대 G2B 흰 칩 | 사용자에게 보고함. Prototype 호박색으로 구현했고 모양이 다르다(S-05 cycle decision) | ../../S-05/evidence/screens/CO-39-chips.png |
| CO-31 ① B 시작 전 확인 화면, 절차 4단계 이상 행 간격 실제 높이(P-08) | 이번에 확인(마지막 빌드, T06 / b_precheck 4.3 B, 절차 4단계 + 체크 3행, 1080 × 740). 절차 행 36px · 간격 6px · 글자 15px · 체크 행 32px로 부록 template(절차 3단계)과 같다. 본문은 17px 넘쳐(637 / 620) 본문 안에서 스크롤된다. 페이지 넘침은 없고, 결과 입력 칸(오른쪽 카드) · 판정 기준 · 근거는 모두 닿는다. template(3단계)은 넘침 없음. 화면을 줄이는 일은 승인 시각 규칙 밖 변경(표시 조정 — G3 · 사용자 결정 몫)이라 하지 않고 보고한다 | manual-review/manual-review-metrics.json · CO-31-T06-b_precheck.png · CO-31-T06-b_precheck-template.png |
| OOS-01 T04 / first_call 구현을 Prototype과 나란히 보고(P-08) | 이번에 확인. 마지막 빌드 앱 T04 / first_call과 packet 부록 template(같은 앱 CSS)을 나란히 캡처했다. 영역 · 순서 · 다음 점검 카드('파트장 호출 필요' · C 승인 필요 · 매뉴얼 절 · 호출 이유 · '점검 시작' 호출 경고 토큰 warnb)가 같고 값만 데이터(각본 · 등급표)다. PBC 이전 v17 캡처는 G4 ~ G7 규칙으로 다시 읽지 않고 부록 template으로 대신했다. 구조 대조 T04--first_call 영역은 미분류 0 | manual-review/OOS-01-T04-first_call-side-by-side.png · manual-review-metrics.json · prototype-structure-checklist.json |
| CO-40 Prototype v17 문서 문구의 결함 복사본 조작 점검 수 | 대조표 값을 실제 값으로 적는다. 결함 복사본 10개(Z-3 포함), 새 결함 Z-1 ~ Z-5(plan v11 carryover CO-40 resolution 원문). Prototype 문서 문구라 구현 대상이 아니다. 이 run의 구조 대조는 이 값을 쓰지 않는다 | ../../../coding-plan/v11/coding-plan.json(CO-40) |
| 팀원 Windows compose up · 시연 1건(P-17) | 미확인(사용자 결정 020 ⑨). 실행 안내를 남겼다 | windows-run-guide.md |
| 마지막 batch 통합 검토(S-06 끝) | critics/G6-FINAL-review.json(1차 revise — 이 표 · 색인 v2로 처리), 2차 검토 | ../../../critics/ |
