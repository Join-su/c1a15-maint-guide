# Change summary: PBC4-A1 → PBC4-A2 (plan v1 → v2)

부모 attempt `PBC4-A1`: critic `critics/PBC4-1-review.json` revise. 사용자 결정: `coding-plan/v2/decisions/pbc4-a2-user-decisions.md`. 제품 계약(AC · 흐름 · 권한 · 데이터 · 화면)은 바꾸지 않았다. 바꾼 것은 PBC machine artifact뿐이다.

| 지적 | 원인 | v2에서 바꾼 것 | 위치 |
| --- | --- | --- | --- |
| ISS-001 계약 본문 미렌더 변수 | 생성 스크립트에서 일부 문자열 조각이 f-string이 아니었음 | 모든 조각을 실제 값으로 생성하고, 생성 때 미렌더 변수 정규식 검사(있으면 실패). 별도 승인 행동은 Matrix `live_actions_requiring_separate_approval` 하나를 정본으로 두고 proposal · 계약 본문이 같은 목록 · 같은 수를 쓴다(시험 DB 컨테이너 실행을 Matrix에 넣음). consistency check를 새 hash로 다시 만듦 | `prebuild/v2/prebuild-contract.md`, `prebuild/v2/pbc-consistency-check.json`, `coding-plan/v2/verification-matrix.json` |
| ISS-002 AC-03 · AC-42 L3 연결 item | 호출 요약 화면(T10)은 P-10(S-03), '승인 후 진행' 답은 P-11 · P-12(S-04)인데 완료 item이 앞 slice | AC-03 item에 P-09 · P-10, 완료 P-10(S-03). AC-42 item에 P-08 · P-10 · P-11 · P-12 · P-13, 완료 P-13(S-04 교차 E2E). 첫 end-to-end 결과는 S-02에서 판정 가능한 지시 경로(4.3 확인 불가 → 4.5 지시)로, 호출 경로는 S-03 L3로 | `coding-plan/v2/coding-plan.json` items · first_end_to_end_flow, Matrix AC-03 · AC-04 · AC-42 |
| ISS-003 surface 핵심 Scenario | 승인 Prototype UI surface coverage(tech SC-06, lead SC-35)를 따르지 않음 | tech: SC-06 · S-03 · B-01 → B-04 · AC-07 · AC-33 L3. lead: SC-35 · S-04 · B-02 → B-01 · AC-11 · AC-24 L3(교차 E2E ④, 완료 P-13). P-12 · P-13에 AC-11, P-13에 AC-24 | ui_surface_delivery, P-12 · P-13, Matrix AC-07 · AC-11 · AC-24 · AC-33 |
| ISS-004 OOS-01 멈춤 지점 · 결정 전 동작 | 멈추는 slice와 결정 전 동작이 없음 | stop_point: S-02, P-03 완료 뒤 · P-08 T04 구현 전 무조건 멈춤. 결정 전: 이 경로를 앱에 넣지 않음, 시연 · E2E · 대조는 첫 판정이 지시인 경로만. 영향 AC-02 · AC-16 · AC-17. P-03 verifier에 첫 판정 계산표, P-08 precondition · stop, Matrix 수동 검토 | out_of_scope_contract_changes[OOS-01], P-03 · P-08, Matrix manual_reviews |
| 비차단 1 AC-06-C1 화면 | 화면 item 미연결 | P-08 · P-10에 AC-06, Matrix AC-06 L3 visual(AC-31 L3와 같은 실행) | P-08 · P-10, Matrix AC-06 |
| 비차단 2 CO-39 출처 | 출처 미기재 | carryover_resolution CO-39에 기준 안 출처(slice AC-41 coverage 행 · Component foundation) | carryover_resolution |
| 비차단 3 SEL-SUBAGENT · Windows | item 연결 · 처리 미정 | SEL-SUBAGENT plan_item_ids = independent_critic item 7개 + P-17. Windows 실행 확인은 협조를 못 받으면 멈추지 않고 '미확인'으로 기록 · 보고 | selection-register v2, Matrix manual_reviews |

바뀌지 않은 것: plan item 17개 · slice 6개 · 경계 12개 · 252 Region 연결 · Selection 결정(채택 21 · 제외 6) · feasibility probe v1(item ID 같음) · 결함 주입 9건 · 실행 mode `per_slice_gated`.
