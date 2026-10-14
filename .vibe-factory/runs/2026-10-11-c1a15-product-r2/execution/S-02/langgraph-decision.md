# S-02 사용자 결정: LangGraph를 API 경로에 연결 (2026-10-13, G5 중)

발견: 명세 002 §API 서버("FastAPI 계층이 agent 패키지(LangGraph 그래프 HITL …)를 import")와 Playbook EP-C1-HITL-001("LangGraph interrupt·checkpoint를 PostgreSQL에 저장, 세션마다 thread ID")이 정한 방식이 API 요청 경로에 연결되어 있지 않았다. graph(`engine/graph.py`)와 시험(InMemorySaver · PostgresSaver 재개)은 있었다. 그러나 API는 업무 기록 fold만으로 다음 단계를 정했다.

| 질문 | 사용자 답 | 선택지 설명(질문에 함께 보인 문장) |
| --- | --- | --- |
| API가 LangGraph graph를 쓰지 않고 업무 기록 fold로만 재개하는 지금 상태를 어떻게 할까요? | "S-02 안에서 API에 연결 (권장)" | 승인 명세 · Playbook대로 진단 세션마다 thread ID(세션 ID)를 둔다. 입력을 저장한 뒤 PostgresSaver graph를 resume해 다음 단계를 받는다. 업무 기록(event)은 그대로 정본이고 checkpoint는 재개 장치다. API 재시작 뒤 같은 단계에서 재개되는지 checkpoint 경로로 다시 확인한 뒤 G6 critic으로 간다. |

선택하지 않은 선택지: 'fold 방식으로 L1 계획 수정' · '지금 상태로 critic에 맡김'.

반영(같은 slice 안에서 승인 방식으로 되돌림):
- `engine/checkpoint.py`: PostgresSaver, thread = `session-{세션 ID}`, init 단계에서 표를 만든다.
- `api/sessions._graph_decision`: 다음 단계를 graph resume으로 받는다. checkpoint가 업무 기록과 어긋나면(새 세션 · checkpoint만 앞섬 · 없음) 업무 기록으로 thread를 다시 세운다. 어느 경로였는지는 `step_opened.via`(resume | rebuild)에 남긴다.
- 시험: `test_api`의 재시작 흉내 뒤 via = resume, thread 삭제 뒤 via = rebuild. `verify-e2e`에서 api 컨테이너 재시작 뒤 같은 단계 · 순위 · 잠금 시각, 다음 단계 via = resume(L3).
