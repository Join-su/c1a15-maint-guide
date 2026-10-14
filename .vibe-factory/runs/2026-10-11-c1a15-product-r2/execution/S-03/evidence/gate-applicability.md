# S-03 자동 gate 적용 범위 (packet v1, plan v9 — P-09 · P-10) · v2(G6 1차 revise 반영)

결과 'pass'는 아래 범위에 대한 판정이며 부풀리지 않는다.

| Gate | 이 slice에서 실제로 확인한 것 | 증거 |
| --- | --- | --- |
| scope_traceability | 바뀐 파일 전부가 P-09 · P-10 중 하나에 묶임(ledger changed_files). G5 중 사용자 결정 016(네 가지) · G6 1차 revise 결정(../g6-revise-decision.md), hash 예상 변경 표(OpenAPI 정본 하나), G5 중 Prototype 원본 재열람 대조 기록(prototype-reread-check.json — UF-S03-05) | ledger · hash-changes.json · ../../../sources/intent/016.md |
| ac_verifier | item verifier 문장마다 시험: P-09 상태 전이 · 음성 시험(체크리스트 전 진행 · 확정 뒤 수정 · 실패 항목 있는 확정 · D 승인 답에도 C 지시 안 열림), 감사 행, 보고서 근거 검사 음성 시험, 첫 판정 호출 요약('점검 전'), 거부 감사가 rollback 뒤에도 남음(S02-G6-1) · 업무 규칙 거부 전부 감사, 종 목록 '답이 온 호출' · '반려된 보고서'(AC-37 A-05), 반려 → 재개 · 수정 → 다시 확정(FLOW-06 · AC-11 L2, 시험 DB 반려 기록). P-10 component 22(S-03) · E2E 9(S-03) · 구조 대조 | check-fast · verify-db · verify-e2e · *-test-list |
| static_check | ruff format · lint(서버 · 시험), OpenAPI 재생성 diff 0, 외부 호출 정적 검사 | check-fast.txt |
| typecheck | packages/ui · apps/tech · apps/lead tsc(생성 타입 schema.d.ts · 시험 파일 포함) | check-fast.txt |
| unit_and_property | 서버 unit 71(S-02와 같음, 판정 규칙 · property 시험 그대로 통과), 화면 component 46(S-03 새 시험 22 — 실제 API 응답 fixture 24개) | unit-test-list.txt · component-test-list.txt |
| api_negative_authority | S-03 음성 시험: 조치 전 재가동 409 · 재가동 체크리스트 부족 409 · B 조치 체크리스트 전 409 · 근거 없는 수치 확정 409(precheck_failed) · 확정 뒤 수정 409(session_closed) · 같은 호출 두 번 409 · D 점검 결과 409 · 인계 권함 없을 때 인계 요청 409 · 반려 뒤 다시 확정한 세션 입력 409, 이 거부들과 잠금 전 · 확인할 것 없음 · B 체크리스트 거부의 감사 행(test_s03_business_rejections_are_audited, 재전송 seq 충돌 stale_seq는 감사하지 않음), 실제 nginx 경유 권한 경계(verify-e2e ADV-06 단계 그대로) | verify-db.txt · db-test-list.txt · verify-e2e.txt |
| integration_real_postgres | 시험 DB(pgvector) API 통합 40(S-03 새 시험 13, migration 0003은 기존 migration 왕복 시험이 함께 확인) | verify-db.txt · db-test-list.txt |
| e2e_surface_journey | Playwright 1.63.0(로컬 chromium, 내려받기 없음)로 compose(nginx 8081 · api · PostgreSQL · 알람 발생기) 정비자 journey 15(S-02 6 + S-03 9). 파트장 답 · 정정 기록은 시험 DB 시뮬레이션(e2e/sim_lead_answer.py · e2e/sim_correction.py, 판정 엔진 함수 그대로 사용). AC-03 L3는 진단 화면 순위 50 · 28 · 11 · 11부터 확인(G6 1차 B1, T04-r5_example.png). 시험마다 외부 요청 차단 · 0건, 콘솔 오류 0건 | verify-e2e.txt · e2e-report.json · screens/ |
| prototype_structure_checklist | S-03 template 상태(T08 · T09 · T10 · T11) 영역 68개를 마지막 빌드의 앱 DOM(dev 스택에서 그 상태까지 움직여 받음)과 태그 · class 구조로 대조: 일치 28, 차이 36, 이 slice 밖 4(T10 / summary_corrected — 사용자 결정 016 ③으로 S-05 P-14). 차이는 S-02 규칙 I-1(진행 표시 pick, S-05) · D-3(종 숫자 값)과 새 규칙 D-4(점검 경로 줄 수 · 점 색 = 세션 데이터)로 모두 분류, 분류 안 된 차이 0 | prototype-structure-checklist.json · structure-dom/ · structure-*.mjs/py |
| secret_scan | ① 저장소 secret_scan 0건 ② 이 slice 증거 폴더 전용 검사(evidence-secret-check.py) 0건 — 결함 주입(가짜 비밀번호 칸)에서 ③이 잡음. ②의 원문 대조는 dev 스택 시험 비밀값으로 함(verify-e2e는 실행마다 새로 만든 값을 쓰고 남기지 않음 — ④ 22자 토큰 꼴 검사가 그 값 꼴을 봄). 첫 검사에서 화면 캡처 이름 하나가 ④ 꼴(22자)로 잡혀 시험의 캡처 이름을 바꾸고 E2E를 다시 돌림(증거를 손으로 고치지 않음). fixture JSON · 증거에 비밀번호 · 토큰 없음 | check-fast.txt · evidence-secret-check.txt · secret-check-fault-injection.txt |
| external_call_zero_in_fixture | 정적: 기준 0건(S-02 결함 주입 검사기 그대로). 실행: E2E 15개 전부 외부 요청 0 | check-fast.txt · e2e-report.json |
| leakage_check | 제품 코드의 eval · generation 참조 0(scripts/forbidden_paths_check.py — 검사 대상은 제품 코드 폴더, e2e/는 대상 밖이라 새 시험 도구 e2e/sim_*.py는 grep으로 따로 확인 0건), 각본 ∩ 이력 · 평가 카드 = 0, data 파일 hash 그대로 | check-fast.txt · hash-changes.json |

시간에 따라 달라지는 값: 교대 '처리 완료 · 파트장 호출' 수와 홈 완료 행은 결정 014 ④ 교대 창 안의 것만 센다(사용자 결정 016 ② 그대로 유지). API 시험과 홈 fixture는 '지금이 야간 교대 안'으로 둔 시험 조건에서 0이 아닌 값을 확인했고, 낮에 돈 E2E는 최근 보고서 목록(교대 창과 무관)만 확인한다.
