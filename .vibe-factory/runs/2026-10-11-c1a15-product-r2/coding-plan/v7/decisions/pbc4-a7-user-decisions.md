# PBC4-A7 사용자 결정과 A8로 다시 하는 이유 (2026-10-13)

## PBC4-A7 Human Gate 답(AskUserQuestion, 선택지 원문)

- 구현 승인: "승인 (권장)" — plan v7 P-08 ~ P-19, per_slice_gated
- PW 센서 표: "알람 센서 + 4개로 5행 (권장)" — 알람 센서(기계 출력)를 맨 위에, 이어서 회전 속도 · 회전력 · 공구 마모 · 공기 온도(온도 차는 이 화면에서 빠짐)
- 나머지 비차단 의견: "이 해석대로 (권장)" — ② data/alarm_rules.json · data/manifest.json · server/openapi.json hash 변경을 S-02 2차 cycle 증거와 cycle decision에 'P-19의 예상 변경'으로 적고 S-03 G4 기준선 재확인 때 대조 / ③ 홈 recent_reports · 교대 '처리 완료' · '파트장 호출' 값 채우기 확인을 S-03 slice execution packet에 / 화면에 쓰지 않는 값(공정 온도 normal_range, 기록 조회 source)은 응답에만 두고 실행 기록에

## 기록하지 못한 이유

승인을 `decisions/PBC-4-prebuild-contract.json`에 적자 산출물 검사가 'change explanation artifact hash does not match'로 실패했다. v7 consistency check(`prebuild/v7/pbc-consistency-check.json`)의 change_artifacts가 그 파일(당시 v6 승인 결정, 승인 때마다 바뀌는 경로)을 hash로 묶었기 때문이다(생성기 실수). v6 결정 내용은 `decisions/history/PBC-4-prebuild-contract-v6.json`에 같은 bytes로 있다. 검사 파일을 고치면 critic 기록 `critics/PBC4-7-review.json`의 hash가 깨진다.

## 사용자 결정

"경로만 고친 PBC4-A8 (권장)" — consistency check가 바뀌지 않는 history 사본을 가리키게 고친다. plan · 시험 · 계약 내용은 v7 그대로. 새 승인 시도 PBC4-A8로 독립 검토를 한 번 더 받고, 같은 내용인지 확인한 뒤 승인을 다시 묻는다. 위 A7 답(선택 두 가지 포함)은 A8로 옮긴다. 기록하지 못한 A7 승인 결정 초안(참고, approved_at 2026-10-13T14:06:41+09:00): 이 문서의 위 절.
