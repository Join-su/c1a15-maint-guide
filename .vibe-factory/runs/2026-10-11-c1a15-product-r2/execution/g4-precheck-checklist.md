# G4 전 대조 점검표(S-05부터 매 slice)

S-01 ~ S-04에서 되돌아간 일(L1 amendment · G5 중단 · G6 revise)의 원인을 점검 항목으로 바꾼 것이다. 각 slice G4에서 packet을 확정하기 전에 모든 항목을 확인하고, 결과를 packet `precheck`에 남긴다. 정의가 없으면 구현 전에 사용자에게 묻는다.

| # | 점검 | 근거(되돌아간 일) | 확인 방법 |
| --- | --- | --- | --- |
| C1 | 이 slice에서 끝나는 AC의 모든 관찰 조건 · 수준(L1 ~ L3)을 이 slice item으로 확인할 수 있는가(뒤 slice item에 기대지 않음) | LR-05(A-05 AC-37 완료 slice) | Matrix entry별 completion item slice ≥ 기대 증거에 나오는 item slice |
| C2 | 계약의 상태 전이 문장이 기대는 입력 · 기록을 만드는 item이 같은 slice이거나 앞인가 | LR-06(A-06 정정 호출 이어 가기) | compiled_product_contract 전이 문장마다 '그 기록을 만드는 item' 대조 |
| C3 | 기대 증거가 순위 · 상위 n건 · 유사도 · 비율처럼 데이터에 달린 결과면 결정적으로 보장되는가. 아니면 대상 포함 · 전후 대조로 확인 문장을 바꾸는 결정이 있는가 | LR-07(A-07 AC-09) | 기대 증거 낱말(순위 · 상위 · 유사 · % · 목표 · n건) 검색 |
| C4 | 구조 대조 기준이 packet 부록뿐이고, 부록에 이 slice 상태 + Prototype 파생 상태 + 사용자 결정으로 생기거나 바뀌는 상태가 모두 있는가 | DEV-24(017 ③) · G6-S04 B3 | prototype_refs ∪ coverage derived_states(source가 이 slice 상태) ∪ 결정 파생 → 부록 states · derived_states |
| C5 | 화면 template에 보이는 값마다 계약 · API 정의가 있는가. 앞 slice에서 생긴 동작(반려 · 답 대기 · 이력 변환 등)과 만나는 지점의 흐름이 정해졌는가 | 결정 015 · 017 · 018 · 019 | template 보이는 글자 추출 → 값 · 흐름 대조표 |
| C6 | G5 중 사용자 결정이 AC 판정 방식을 정하면 G6 전에 packet 실행 해석으로 싣는가(packet 판 올림) | G6-S04 B1(018 ⑥) | G5 결정 기록 → packet 판 · 실행 해석 |
| C7 | 새 시험이 틀린 구현에서 실패하는가(판별력) — 전체를 돌려받는 순위 · 늘 참인 포함 검사 금지, 전 · 후 대조 | G6-S04 B1(cosine_rank) · B2(AC-25-C4) | 시험마다 '무엇이 틀리면 실패하나' 한 줄 |
| C8 | 이전 승인 · cycle decision의 이어받을 일 · '다음 plan 판에서' 항목이 packet carried_tasks에 모두 있는가 | PBC4-A9 ~ A11 실행 해석 · G6 비차단 의견 | 승인 기록 approved_scope · cycle decision Carried tasks 대조 |
| C9 | 증거 위생: E2E 보고서 이미지 본문은 screens 경로로 바꾼 뒤 비밀값 검사, `playwright test --list`는 보고서 복사 뒤, dev 스택은 verify-e2e 전에 내림, hash 예상 변경 표 | S-04 G5 · G6 수리 | evidence 생성 스크립트 순서 |
| C10 | critic 묶음: subject = 정식 보고서 경로, 비교 자료 = history 사본, 보고서에 independent_critic_review 먼저, 비차단 의견 최대 3, hash로 묶인 change artifact는 승인 뒤에도 고치지 않음 | S-03 G6 3차 · S-04 A-07 | 묶음 생성 스크립트 |
| C11 | packet adversarial_cases와 item verifier 문장을 한 줄씩 시험 대응표로 만들었는가(대응 시험이 없으면 G5 계획에 넣음) | S-05 UF-S05-08 · 12(ADV-08 · 기록 종류 7 × 상태 누락 — validator · 다시 검토에서 발견) | packet `verifier_test_map` |
| C12 | 구조 대조에서 부록 상태마다 대조 영역 수를 세고 0인 상태가 없는가(영역 목록 없는 파생 상태는 기준 상태 selector) | S-05 UF-S05-10(Prototype 파생 3상태가 아무 말 없이 빠짐) | 대조 스크립트 상태별 수 · 0이면 실패 |
