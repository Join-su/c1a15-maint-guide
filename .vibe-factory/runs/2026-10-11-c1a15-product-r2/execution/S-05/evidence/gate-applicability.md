# S-05 자동 gate 적용 범위 (packet v3, plan v11 — P-14 · P-15)

결과 'pass'는 아래 범위에 대한 판정이며 부풀리지 않는다.

| Gate | 이 slice에서 실제로 확인한 것 | 증거 |
| --- | --- | --- |
| scope_traceability | 바뀐 파일 전부가 P-14 · P-15 중 하나에 묶임(ledger changed_files). G4 전 대조 점검표 C1 ~ C10(packet precheck)과 사용자 결정 019(① ~ ⑨, ⑨는 G5 중 — packet v3). 정정 기록을 읽는 기존 코드(보고서 · 감사 · 호출 상세 · 이력 변환 · 점검 n / m)의 수정은 FLOW-14 '다시 읽기'(점검표 C2). hash 예상 변경 표(OpenAPI 정본 하나) | ledger · hash-changes.json · ../../../sources/intent/019.md |
| ac_verifier | item verifier 문장마다 시험: P-14 API 음성 시험(기록 종류 7 — 잠금 · 조치 · 재가동 · 재가동 경계 확인 · 파트장 호출 · 확인 질문 답 · B 시작 전 체크 · 숙련자 인계 — × 세션 상태 진행 · 승인 대기 · 반려로 다시 열림 · 승인: 진행 · 반려는 정정 거부 · 메모 덧붙이기 됨, 승인 대기 · 승인은 둘 다 거부(test_non_correctable_kinds_by_session_state, 결함 주입으로 판별 확인 — test-fault-injection.txt). 단계 기록(step_opened) 거부 · 결과 · 측정값 확정 세션 거부도 따로), 사유 없는 저장 거부, 덧붙임 · 감사 5항목, 재판정 = R4 · R5를 정정한 결과로 처음부터 다시 적용한 값(같은 기록을 새로 만든 판정과 비교), 조치 뒤 → 정정 호출, 보낸 호출 · 숙련자 인계 뒤 → 새 호출 없음 · 상자, 답한 호출 뒤 → 기록만, 무효 기록은 LLM 실패 수에서 뺌(S02-G6-4), 정정 호출 답 승인 → 하던 단계(A-06). P-15 component 정비자 15 · 파트장 4(T15 상태 12 + Prototype 파생 3 + 결정 파생 + 숙련자 인계 기록), tech E2E(정정 → 다시 판정 → 뒤 기록 무효 → 보고서 초안 반영), 교차 E2E(보낸 호출 뒤 정정 → L04 정정 상자 · L06 정정 행, 조치 뒤 정정 호출 → 승인 → 하던 단계), 구조 대조(표시 조정 ③ · CO-39 포함) | check-fast · verify-db · verify-e2e · *-test-list · test-fault-injection.txt |
| static_check | ruff format · lint(서버 · 시험), OpenAPI 재생성 diff 0, 외부 호출 정적 검사 | check-fast.txt |
| typecheck | packages/ui · apps/tech · apps/lead tsc(생성 타입 schema.d.ts · 시험 파일 포함) | check-fast.txt |
| unit_and_property | 서버 unit 71(정정 반영 방식 단위 시험을 sessions.logical 기준으로 고침 — 다시 판정 · 메모만 · 조치 뒤 · 보낸 호출 · 답한 호출 · 정정 불가 · 무효 기록 정정 불가), 화면 component 정비자 65 · 파트장 19 | unit-test-list.txt · component-test-list-*.txt |
| api_negative_authority | 정정 거부: reason_required · not_correctable(잠금 · 조치 · 재가동 · 재가동 후 값 · 파트장 호출 · 확인 질문 답 · B 시작 전 체크 · 숙련자 인계 · 단계 기록) · session_closed(승인 대기 · 승인 세션의 결과 · 측정값 · 잠금) · no_change · invalid_value · no_record, 메모 덧붙이기 거부: memo_required · not_note_target(결과) · session_closed(승인 대기 · 승인 세션의 기록 종류 7 전부), 확인 없이 열린 지시를 바꾸는 정정 409 confirm_required(거부 아님 — 감사하지 않고 아무것도 바꾸지 않음), 반려로 다시 열린 세션은 다시 정정 · 덧붙이기(AC-48-C3). ADV-08(packet 적대 사례): 위 거부 시험 + 원래 값 덮어쓰기 결함 사본(정정을 덧붙이지 않고 원래 업무 기록을 고쳐 쓰게 저장 함수를 바꿈)에서 '원래 값 남음' 검사가 실패를 잡고, 지금 저장 계층에서는 통과(test_adv08_overwrite_defect_is_caught, 시험 DB만). 거부 감사 행은 별도 transaction(S02-G6-1). 실제 nginx 경유 권한 경계(verify-e2e ADV-06 단계 그대로) | verify-db.txt · db-test-list.txt · verify-e2e.txt |
| integration_real_postgres | 시험 DB(pgvector) API 통합 65(정정 · 지난 화면 새 시험 9 — ADV-08 포함). migration 0005(ops.calls.correction · corrections)는 기존 migration 왕복 시험이 함께 확인 | verify-db.txt · db-test-list.txt |
| e2e_surface_journey | Playwright 1.63.0(로컬 chromium, 내려받기 없음)로 compose 두 browser context journey 27(S-02 6 + S-03 9 + S-04 6 + S-05 6). 정정 · 메모 덧붙이기 · 파트장 답은 모두 화면 조작(S-03 정정 시뮬레이션 도구 e2e/sim_correction.py는 걷어 냄 — T08 / corrected_path 시험은 정정 API). 시험마다 외부 요청 차단 · 0건, 콘솔 오류 0건(역할 거부 화면의 403 · 정정 확인 창을 여는 409 응답만 허용 목록) | verify-e2e.txt · e2e-report.json · screens/ |
| prototype_structure_checklist | 기준은 packet 부록 v2(execution/S-05/prototype-appendix — 결정 017 ③ · 점검표 C4)만. S-05 상태 19(T15 15 · T08 / corrected_path · T10 / summary_corrected · L04 / call_corrected · L06 / correction, Prototype 파생 T15 / check_b · call · correct_value 포함) + 결정 파생 5(L04 / handover_corrected · correction_call_detail · T09 / draft_corrected · T10 / corrected_ans_daytime · direct) = 24 상태를 마지막 빌드 앱 DOM(dev 스택에서 그 상태까지 움직여 받음)과 태그 · class 구조로 대조: 영역 104 — 일치 43, 차이 61(모두 분류), 기준 전용 14(파생 기준 4 상태), 분류 안 된 차이 0. Prototype 파생 3상태(T15 / check_b · call · correct_value)는 부록 regions.json에 영역이 없어(자기 template만) 첫 대조에서 아무 말 없이 빠졌다 — G6 전 다시 검토에서 찾아 기준 상태(T15 / check · lock · correct)의 영역 selector로 자기 template과 대조하도록 고침(영역 15 더함). 새 규칙 I-6(끝 기록 이전 · 다음 잠김) · D-9(보내지 않은 입력 칩) · D-10(진행 표시 현재 단계) · D-11(정정 이력) · D-12(지금까지 점검 · 조치 줄) · D-13(그때 등급 배지 — check_b template이 예시 'A'를 그대로 둠) · X-3(T15 / call에 붙은 정정 상자 — 부록 L04 / call_corrected .corr-box와 구조 차이 0) · X-4(T15 / correct_value 창 뒤 화면 = 정정하는 사전 확인 기록 — 부록 T15 / precheck 영역과 차이 0, alt_compare), I-2 · I-4 · D-4 범위 넓힘, I-1은 뺌(지난 화면 pick을 이 slice에서 연결). CO-38: T15 / check_b 실제 화면 1080 × 740 틀에서 지난 화면 본문 548px · 넘침 없음 · 체크 행 20px · 글자 14px · 절차 줄 높이 1.3(co38-metrics.json). CO-39: 지난 화면 칩(Prototype 호박색 .ch.amber)과 G2B '수정 가능' 흰 칩 토큰(.hist-row.unsent .ch.amber)을 같은 화면에 나란히 캡처(screens/CO-39-chips.png) — 모양이 다름, Prototype대로 구현 | prototype-structure-checklist.json · structure-dom/ · structure-*.mjs/py · co38-metrics.json · screens/CO-39-chips.png · screens/T15-check_b.png |
| secret_scan | ① 저장소 secret_scan 0건 ② 이 slice 증거 폴더 전용 검사(evidence-secret-check.py, S-04와 같음) 0건 — 결함 주입(가짜 비밀번호 칸)에서 ③이 잡음. e2e-report.json의 화면 캡처 본문은 screens/ 경로로 바꾼 뒤 검사(점검표 C9). DOM 저장은 비밀번호 칸 값을 지움 | check-fast.txt · evidence-secret-check.txt · secret-check-fault-injection.txt |
| external_call_zero_in_fixture | 정적: 기준 0건. 실행: E2E 27개 전부 외부 요청 0 | check-fast.txt · e2e-report.json |
| leakage_check | 제품 코드의 eval · generation 참조 0(scripts/forbidden_paths_check.py), 각본 ∩ 이력 · 평가 카드 = 0, data 파일 hash 그대로. 정정 기록 · 이력 변환은 업무 기록만 읽음 | check-fast.txt · hash-changes.json |

G6-S05 1차 revise 수리(execution/S-05/g6-revise-decision.md):
- B1 AC-44-C3: E2E에 'B 시작 전 체크 일부 · 결과 · 메모를 넣고 홈 이어서 하기 · 종 목록 진행 중 항목 두 경로로 돌아와 그대로' 시험을 더했다.
- B2 AC-41-C4: 현재 단계로 돌아온 뒤 결과 버튼 잠김이 없고, 결과 · 메모를 바꾸면 바뀐 값이 보이고, 홈을 다녀와도 그 값이 그대로임을 단언했다.
- 비차단 ① 구조 규칙 D-11을 정정 이력 요소 자체만 잡게 좁혔다. 자식 줄 상속에 s 태그를 더했다. T15 / call 영역은 X-3 하나로 분류되고 미분류는 0이다.
- 비차단 ② 결정 019 ① '직접 확인' 답 뒤 보고서 필드를 서버 시험에 더했다.
- 비차단 ③ component에 조치 · 재가동 · 숙련자 인계 기록의 '메모 덧붙이기'만을 직접 단언했다. 숙련자 인계 지난 화면 fixture는 dev 스택 실제 API로 받았다(fixture-capture-handover.py).
- 수리 뒤 check-fast · verify-db 65 · verify-e2e 27을 다시 돌리고, E2E 증거와 목록을 C9 순서로 다시 받았다. 비밀값 검사는 마지막이다.

AC-48-C1 화면 범위(사용자 결정 019 ⑨): 확인 질문 답 · B 시작 전 체크의 '메모 덧붙이기'는 서버 API까지 확인했다. 화면은 승인 Prototype대로 B 체크를 점검 기록 안 읽기 전용 패널(T15 / check_b)로 보이고, 확인 질문 답은 지난 화면 기록으로 보이지 않는다 — 이 두 기록의 화면 메모 버튼은 없다.

시험 다시 실행(G6 전 다시 검토): test_non_correctable_kinds_by_session_state · test_adv08_overwrite_defect_is_caught와 E2E 확인 창 취소 뒤 기기 입력 단언(AC-46-C4)을 더한 뒤 check-fast · verify-db · verify-e2e를 다시 돌리고 E2E 증거를 같은 순서(점검표 C9)로 다시 받았다. 제품 코드는 바뀌지 않아(결함 주입 파일은 cmp로 되돌림 확인) 구조 대조 DOM은 그 전 캡처 그대로이고, 구조 대조 · 분류만 같은 DOM으로 다시 돌렸다(Prototype 파생 3상태 추가). 비밀값 검사는 마지막에 다시.

시간에 따라 달라지는 값: 정정 · 지난 화면 값은 교대 창과 무관하다.
