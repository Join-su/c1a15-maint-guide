# Change summary: PBC4-A2 → PBC4-A3 (plan v2 → v3)

부모 attempt `PBC4-A2`: critic `critics/PBC4-2-review.json` revise(막는 지적 1건). 사용자 결정: `coding-plan/v3/decisions/pbc4-a3-user-decisions.md`. 제품 계약은 바꾸지 않았다. PBC4-A1 대비 변경(`prebuild/v2/change-summary.md`)은 v3에 그대로 남아 있다.

| 지적 | 원인 | v3에서 바꾼 것 | 위치 |
| --- | --- | --- | --- |
| A2-ISS-001 consistency check의 surface 판정 문장이 v1 값 | 생성 스크립트가 logical_flow_compilation 판정 문장을 고정 문장으로 넣음 | 판정 문장을 현재 Coding Plan의 ui_surface_delivery · first_end_to_end_flow와 Matrix 완료 item에서 생성한다. 통합 slice에 진입 · 다시 읽기 경계 item이 없거나 그 slice에서 끝나는 L3가 없으면 생성이 실패한다 | `prebuild/v3/pbc-consistency-check.json` |
| 비차단 1 승인 범위 | P-08 이후는 OOS-01 결정 뒤 새 plan이 필요 | implementation_authorization_proposal.allowed_plan_item_ids = P-01 ~ P-07(사용자 결정). 계약 Authority 절에 P-08 이후는 화면 결정 뒤 새 plan version · 새 authorization이라고 적음 | `prebuild/v3/prebuild-contract.md`, run-state proposal |
| 비차단 2 OOS-01 줄 중복 · 멈춤 시점 | 머리말 · 문장 중복, 구간 표현 | Out of scope 줄은 OOS-01 원문 한 번 + 영향 AC. 멈춤 시점 'P-03 완료 즉시 묻기(무조건), 기다리는 동안 P-04 ~ P-07 계속, P-08 시작 안 함' | Coding Plan out_of_scope_contract_changes · P-08, Matrix manual_reviews, 계약 |
| 비차단 3 v1 표기 | AC-35 · AC-09 L3와 S-04 결과 문장에 '핵심 journey(SC-04 · SC-33)' | '첫 end-to-end 대표 journey(SC-04 · S-02)' · '승인 되먹임 대표 journey(SC-33 · S-04)', S-04 결과 문장에 lead 핵심 Scenario SC-35 반려 다시 읽기 | Matrix AC-35 · AC-09, Coding Plan slice S-04 |

바뀌지 않은 것: plan item 17개 · slice 6개 · 경계 12개 · 252 Region 연결 · AC 연결 · Selection 결정 · feasibility probe v1 · 결함 주입 9건 · 실행 mode `per_slice_gated`.
