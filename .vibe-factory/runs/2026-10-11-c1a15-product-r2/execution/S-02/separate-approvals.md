# S-02 별도 승인 · 결정 기록 (2026-10-13)

| 대상 | 사용자 답 | 범위(질문에 함께 보인 문장) |
| --- | --- | --- |
| 새 패키지 설치 | "네 개 모두 허용 (권장)" | langgraph · langgraph-checkpoint-postgres(판정 엔진 중단 · 재개 틀), hypothesis(개발용 property 시험), openai(LLM Adapter live 코드 — 호출은 하지 않고 live 호출은 승인 뒤). 저장소 안 uv 환경에만 설치하고 uv.lock에 고정. openai는 fixture 모드에서 불러오지 않고, 외부 호출 정적 검사는 LLM Adapter의 live 파일 하나만 예외 |
| P-07 시연 각본 방식 | "검사 전용 스크립트만 UDI 읽기 (권장)" | 각본을 만드는 일회용 스크립트와 분리 검사 스크립트(scripts/)만 eval/cards/card_udi_map.json에서 행 번호를 읽는다. 카드 내용 · 정답 · 원인 비율표는 읽지 않는다. 제품 코드(서버 · 앱 · 적재기 · 색인)는 읽지 않고 정적 검사로 확인. CSV(../manifact_10/data/raw/ai4i2020.csv)는 읽기만, 각본 파일(data/demo/scenarios.json)에 센서 값과 추이 12회를 함께 남긴다 |
| 시험 컨테이너 · uv 부트스트랩 | S-01 승인 범위 그대로 | execution/S-01/separate-approvals.md |
