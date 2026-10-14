# S-02 2차 cycle 자동 gate 적용 범위 (packet v4, plan v8 — P-08 · P-18 · P-19) · v3(G6 1차 · 2차 revise 반영)

결과 'pass'는 아래 범위에 대한 판정이며 부풀리지 않는다. 이 cycle에서 처음으로 화면 gate(e2e_surface_journey · prototype_structure_checklist)가 실제 대상(정비자 앱)을 가진다.

| Gate | 이 cycle에서 실제로 확인한 것 | 증거 |
| --- | --- | --- |
| scope_traceability | 바뀐 파일 전부가 P-08 · P-18 · P-19 중 하나에 묶임(ledger changed_files). G5 중단 2번과 L1 A-03 · A-04 · PBC-4 v8 · v9 승인, 별도 승인(npm 네 묶음), hash 예상 변경 표 | ledger · hash-changes.json · ../g5-stop.md · ../g5-stop-2.md · ../separate-approvals.md |
| ac_verifier | item verifier 문장마다 시험: P-18 미리보기 호출 값 · 입력 검증 · 재전송, P-19 화면 값(교대 경계 시각 · 진행 n / m · alarm 블록 · 센서 표 PW · AI 해석 R8 · 기록 카드 = 이력 값 · 잠금 절차 1.2만 · 근거 기록 · 원인 이름 = 원인 표 · 승인 · 출처 · 지시문 원문 대체 · data 재생성 diff · OpenAPI 재생성 diff 0), P-08 component 24 · E2E 6 · 구조 대조 · 외부 호출 정적 검사 보강 결함 주입 · 콘솔 오류 0 | check-fast · verify-db · verify-e2e · *-test-list |
| static_check | ruff format · lint, OpenAPI 재생성 diff 0, 외부 호출 정적 검사 | check-fast.txt |
| typecheck | packages/ui · apps/tech · apps/lead tsc(생성 타입 schema.d.ts 포함, 시험 파일 포함) | check-fast.txt |
| unit_and_property | 서버 unit 71 passed(test_screen 포함, hypothesis property 2), 화면 component 24(실제 API 응답 fixture 23 + 세션 동작 1 — 확인 질문 아니요 → 메모 되돌림, 결함 주입으로 실패 확인) | unit-test-list.txt · component-test-list.txt |
| api_negative_authority | 잠금 전 다른 절 원문 409 · 지시되지 않은 절 409 · 서버 전용 필드 422 · 필수 필드 422 · 재전송 일부 필드 409, 실제 nginx 경유 권한 경계(verify-e2e ADV-06 단계 그대로) | verify-db.txt · verify-e2e.txt |
| integration_real_postgres | 시험 DB(pgvector) API 통합 27(P-19 4개 · P-18 2개 · AC-05 확인 질문 2개 — 확정형 · 선별형 — 포함) | verify-db.txt · db-test-list.txt |
| e2e_surface_journey | Playwright 1.63.0(로컬 chromium, 내려받기 없음)로 compose(nginx 8081 · api · PostgreSQL · 알람 발생기) 정비자 journey 6: 첫 end-to-end(새로고침 · api 재시작 뒤 같은 단계) · 새 알람 5초 · 종 목록 · 다시 열기 · 첫 판정 호출 → 잠금 · LLM 실패 시뮬레이션 · 역할 거부. 시험마다 외부 요청 차단 · 0건, 콘솔 오류 0건(역할 거부 403만 예외) | verify-e2e.txt · e2e-report.json · screens/ |
| prototype_structure_checklist | regions.json의 정비자 상태 · 영역과 파생 상태 2개(T04 / first_call ← T04 / default, T06 / second_check ← T06 / unable_next 영역)를 합한 84개(이 slice 밖 3)를 마지막 빌드의 앱 DOM(dev 스택에서 그 상태까지 움직여 받음)과 template의 태그 · class 구조로 대조: 일치 36, 차이 48. 차이는 영역 · 방향(+/−) · 줄 모양으로 좁힌 규칙(I-1 ~ I-4 · D-1 ~ D-3 · R-1)과 조상 줄 상속으로 모두 분류, 분류 안 된 차이 0. T04 / first_call은 진행 표시 pick 하나만 다름. 대조 중 찾은 차이 4건은 고침(UF-C2-06) | prototype-structure-checklist.json · structure-dom/ · structure-*.mjs/py |
| secret_scan | ① 저장소 secret_scan(scripts/secret_scan.py, run 폴더는 검사하지 않음) 0건 ② 이 cycle 증거 폴더 전용 검사(evidence-secret-check.py: 저장소 패턴 · 이번 실행 시험 비밀값 원문 · 비밀번호 칸 value · 22자 무작위 토큰 꼴) 0건 — 결함 주입(가짜 비밀번호 칸)에서 ③ · ④가 잡음. fixture JSON · 증거에 비밀번호 · 토큰 없음. G6 2차 B2: 구조 대조 DOM(T01 / role_error)에 시험용 파트장 비밀번호 원문이 저장됐던 것을 찾아 값 제거 · 캡처 수정(저장 전 비밀번호 칸 비움) · 다시 받음, 그 값을 쓰던 dev 스택은 down -v, 다음 실행 비밀값 새로 생성(UF-C2-09) | check-fast.txt · evidence-secret-check.txt · secret-check-fault-injection.txt |
| external_call_zero_in_fixture | 정적: 기준 0건, 위반 9종(urllib3 · http.client · socket · WebSocket · XMLHttpRequest · sendBeacon · 외부 주소) 주입 시 각각 exit 1, 정리 뒤 0. 실행: E2E 6개 전부 외부 요청 0, 화면은 Google Fonts를 불러오지 않음 | external-call-fault-injection.txt · e2e-report.json |
| leakage_check | 제품 코드의 eval · generation 참조 0, 각본 ∩ 이력 · 평가 카드 = 0, data 재생성은 normal_ranges · manifest hash만 바뀜(이력 · 매뉴얼 · 경계 그대로) | check-fast.txt · data-regenerate.txt |

개발 중 실행 구성 관찰(UF-C2-08): `docker compose up api --build`는 적재된 DB에 init을 다시 돌려 실패하고 api 재생성 뒤 nginx가 옛 주소를 가리켰다. 시험 · E2E 스크립트는 매번 새 스택(down -v)이라 영향이 없다.
