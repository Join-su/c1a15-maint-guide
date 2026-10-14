# S-06 자동 gate 적용 범위 (packet v2, plan v11 — P-16 · P-17, 마지막 slice)

결과 'pass'는 아래 범위에 대한 판정이며 부풀리지 않는다.

| Gate | 이 slice에서 실제로 확인한 것 | 증거 |
| --- | --- | --- |
| scope_traceability | 바뀐 파일 전부가 P-16 · P-17 또는 앞 slice 결함 수리(사용자 결정 020 ④ ⑬ ⑮ ⑯ ⑰ — packet front_slice_repairs) 중 하나에 묶임(ledger changed_files). G4 전 대조 점검표 C1 ~ C12(packet precheck), 사용자 결정 020 ① ~ ⑰(⑩ ~ ⑰은 G5 중 — ⑬ 이후는 사용자 위임 '권장안'), hash 예상 변경 표(OpenAPI 정본 하나) | ledger · hash-changes.json · ../../../sources/intent/020.md |
| ac_verifier | verifier 시험 대응표(packet verifier_test_map) 줄마다 시험: P-16 — 평가 출력 schema(지표 6 · 목표 · 미달 표시) · 지표 계산(손으로 정한 정답 기록) · 등급 위반 집계(평가 30건 결과 0) · 정적 검사 · 누수 음성(분리 0 · 이력 행 수 불변). P-17 — 시연 10건 E2E(입력표 그대로, 끝 모양 원인 확정 4 · 승인 뒤 확정 1 · 주간 처리 1 · 감시 2 · 인계 2) · 외부 호출 0 · 전 화면 252영역 대조 · 재시작 재개(DEMO-07 잠금 뒤 api 재시작). ADV-09(정적 · 실행 감시 결함 사본). 결정 020 ④ 감사 중복 · S-05 이어받은 체크리스트 E2E | check-fast · verify-db · verify-e2e · eval-run · *-test-list · test-fault-injection.txt |
| static_check | ruff format · lint(서버 · 시험), OpenAPI 재생성 diff 0, 외부 호출 정적 검사 | check-fast.txt |
| typecheck | packages/ui · apps/tech · apps/lead tsc(생성 타입 · 시험 파일 포함) | check-fast.txt |
| unit_and_property | 서버 unit 80(평가 지표 8 · 알람 발생기 표준 입력 1 포함), 화면 component 정비자 66 · 파트장 19 | unit-test-list.txt · component-test-list-*.txt |
| api_negative_authority | 내부 알람 등록의 eval_mode도 nginx 경유(X-App)는 403, 평가 모드는 내부 토큰 경로만. 기존 권한 경계(ADV-06) 그대로 다시 통과 | verify-db.txt · db-test-list.txt · verify-e2e.txt |
| integration_real_postgres | 시험 DB(pgvector) API 통합 70(이 slice 새 시험 5 — eval_mode 등록 · commit 시점 · 감사 중복 · 두 번째 호출 · ADV-09 실행 감시) | verify-db.txt · db-test-list.txt |
| e2e_surface_journey | Playwright 1.63.0(로컬 chromium, 내려받기 없음)로 compose 두 browser context journey 40(S-02 6 + S-03 9 + S-04 6 + S-05 6 + 시연 11 + S-06 2). 시연 · 파트장 답 · 보고서 확정은 화면 조작. 시험마다 외부 요청 차단 · 0건, 콘솔 오류 0건(허용: 역할 거부 403 · 정정 확인 창 409 · DEMO-07 api 재시작 중 502) | verify-e2e.txt · e2e-report.json · screens/ |
| prototype_structure_checklist | 기준은 packet 부록(execution/S-06/prototype-appendix — 결정 017 ③ · 020 ①)만. 마지막 빌드 앱 DOM 83상태(영역 상태 69 + Prototype 파생 8 + 결정 파생 6, 앞 slice 캡처 도구 4개를 마지막 빌드에 다시 실행 — S-03 도구의 정정 시뮬레이션 단계는 S-05 도구가 정정 API로 받음)를 대조: Prototype 252영역(정비자 206 · 파트장 46) 일치 141 · 분류된 차이 111, 파생 포함 306 대조 일치 172 · 분류된 차이 134, 미분류 0, 대조 수 0인 상태 0(C12). 분류 규칙은 S-05 묶음 그대로(I-2 ~ I-6 · D-1 ~ D-13 · R-1 · X-1 ~ X-4, 규칙마다 근거 결정 · 설명이 checklist rules에). 가이드 예시 값 하드코딩 0건(AC-17-C2, 결함 주입에서 잡음) | prototype-structure-checklist.json · structure-compare-result.json · structure-dom/ · structure-dom-capture/ · structure-*.mjs/py · example-value-check.txt |
| secret_scan | ① 저장소 secret_scan 0건 ② 이 slice 증거 폴더 전용 검사(evidence-secret-check.py, S-05와 같음) 0건 — 결함 주입에서 잡음. E2E 보고서 이미지 본문은 screens/ 경로로 바꾼 뒤 검사(C9). 평가 실행 · 시연은 무작위 비밀값 격리 스택. 도구 실패 메시지는 요청 본문을 찍지 않음 | check-fast.txt · evidence-secret-check.txt · secret-check-fault-injection.txt |
| external_call_zero_in_fixture | 정적: 기준 0건. 실행: E2E 40개 전부 외부 요청 0, api 컨테이너 fixture 모드 · 키 환경 변수 없음(verify-e2e), 평가 실행도 fixture 격리 스택 | check-fast.txt · e2e-report.json · verify-e2e.txt · eval-run.txt |
| leakage_check | 제품 코드의 eval · generation 참조 0(forbidden_paths_check), 평가 실행 중 api 컨테이너 정답 자료 파일 열기 0(감시 켜짐 확인), 이력 원본 행 ∩ 평가 카드 행 = 0, 평가 뒤 이력 300 → 300, 평가 카드 · data hash 그대로 | check-fast.txt · eval-report.json(isolation) · hash-changes.json |

평가 지표(fixture, 카드 30건 · 실패 0 · 호출 22 · 기대 결과 일치 27): 유사 사례 Top-3 45.5%(목표 80, 미달) · 원인 Top-3 90.9%(80, 달성) · 점검 소요 분 단축률 −6.5%(20, 미달) · 인용 절 일치율 100%(95, 달성) · 날조 원인 0(0, 달성) · 등급 위반 0(0, 달성). AC-18은 '목표와 함께 보고(미달도 결과)'라 미달 값도 그대로 보고한다.

수동 검토 7건 결과는 manual-reviews.md(CO-31 ① · OOS-01 · CO-40은 마지막 통합 검토 1차 B2로 이번에 확인 · 기록, 팀원 Windows는 '미확인' — 결정 020 ⑨, 안내 windows-run-guide.md). 마지막 통합 검토 1차 revise 처리 뒤(g7-final-review-revise-decision.md) check-fast · verify-db · 평가 · verify-e2e를 다시 돌리고 증거를 C9 순서로 다시 받았다.
