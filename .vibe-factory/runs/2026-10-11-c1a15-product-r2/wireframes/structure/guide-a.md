# G2A Reference-backed Candidate guide-a: 사용 가이드 화면 그대로

## Target actor and task

- 정비자(태블릿): 알람 1건을 점검 하나씩 따라 원인 확정 · 조치 · 보고서 확정까지 끝낸다. 혼자 할 수 없으면 호출하거나 인계한다.
- 파트장(PC): 보고서 승인 · 수정 후 승인 · 반려, 호출 답하기, 등급 설정, 감사 기록 조회를 한다.
- 구조는 사용 가이드 v1.0 4~17쪽 화면 그대로다(D1, D17). 값은 `wireframes/samples/review-sample.json`(data/ 에서 계산)이다.

## Reference patterns

| Reference ID | Product and specific screen/pattern | URL | Observed at | Task fit | Borrowed structural principle | Explicitly not borrowed |
| --- | --- | --- | --- | --- | --- | --- |
| RP-01 | Linear · 작업 공간 왼쪽 내비게이션 + 본문 목록(Projects · Active) | https://www.saasui.design/pattern/dashboard/linear | 2026-10-11T21:05:00+09:00 | 파트장 앱: 승인 대기 · 호출 · 권한 등급 · 감사 기록 사이를 오가는 반복 업무 | 고정된 왼쪽 내비와 넓은 본문 하나, 현재 위치 강조 | 프로젝트·로드맵·이슈 기능, 타임라인 화면 |
| RP-02 | Linear · 프로젝트 상세 + 오른쪽 속성 패널(Properties · Milestones) | https://www.saasui.design/pattern/dashboard/linear | 2026-10-11T21:05:00+09:00 | 보고서 검토(L03), 호출 답하기(L04), 진단(T04)의 '내용 + 옆 판단 패널' | 본문 옆에 같은 대상의 속성·결정 영역을 나란히 둠 | 보드 열, 마일스톤·멤버 개념 |
| RP-03 | Linear · 설정 · Preferences 행(이름 + 설명 + 오른쪽 조작) | https://www.saasui.design/pattern/settings/linear | 2026-10-11T21:05:00+09:00 | 권한 등급 설정(L05), 보고서 8항목 행(T09) | 한 행 = 항목 이름 + 값/설명 + 오른쪽 끝 조작 | 토글·테마 같은 개인 설정 의미 |
| RP-04 | Front · 관리 · Message templates 표(이름 · 미리보기 · 열 · 오른쪽 안내) | https://www.saasui.design/pattern/table/front | 2026-10-11T21:05:00+09:00 | 처리할 호출 목록(L04), 감사 기록(L06) | 왼쪽 관리 내비 + 열이 정해진 표 + 표 옆 짧은 안내 | 템플릿·받은편지함 기능 |
| RP-05 | Dropbox Sign · Documents 표(상태 열 · 상태 필터 · 행별 Edit 버튼) | https://www.saasui.design/pattern/table/dropbox-sign-formerly-hellosign | 2026-10-11T21:05:00+09:00 | 승인 대기 목록(L02), 정비자 홈 알람 목록(T02) | 행 안에 상태를 보이고 행 끝에 처리 버튼 하나 | 서명·대량 발송 기능, 요금 안내 |
| RP-06 | Linear · 작업 공간 만들기(가운데 단일 입력 카드 + 주 버튼 하나) | https://www.saasui.design/pattern/onboarding/linear | 2026-10-11T21:05:00+09:00 | 로그인(T01, L01) | 가운데 한 장의 카드에 필드와 주 버튼 하나만 둠 | 회사 규모·역할 질문, 가입 흐름 |
| RP-07 | Linear · Invite people 모달(현재 화면 위 확인 창) | https://www.saasui.design/pattern/modal/linear | 2026-10-11T21:05:00+09:00 | 확인 질문 · 맞지 않는 소견(T07) | 현재 작업 화면을 흐리게 두고 위에 작은 확인 창, 두 버튼 | 초대·팀 배정 기능 |
| RP-08 | DocuSign · 봉투 만들기(순서 있는 단계 섹션 + 아래 고정 Next) | https://www.saasui.design/pattern/form/docusign | 2026-10-11T21:05:00+09:00 | 정비자 앱 단계 진행(알람 → 보고서), 점검 지시 · 체크리스트(T06, T08) | 정해진 순서의 단계와 한 번에 하나의 주 행동 | 문서 업로드·수신자 기능, 고급 옵션 |

## Reference surface and discovery route

- Page group / Page IDs: `tech-workflow` T01~T11, `lead-workflow` L01~L06
- Classification (`game_ui | marketing_site | interactive_site | workflow_product | general_utility`): 둘 다 `workflow_product`
- Workflow signals observed: 지속 기록(세션 · 보고서 · 호출 · 등급), 대기열 · 상태 · 필터, 여러 단계 반복 작업, 역할 · 권한 · 인계, 여러 화면을 오가는 운영 작업
- Why this route fits this candidate's work model: 두 앱 모두 반복 업무 화면이라 SaaSUI 업무 화면 경로가 맞다. 가이드 화면의 각 영역이 실제 제품의 어느 원리와 같은지만 확인했다.
- Discovery source or open-search rationale: SaaSUI SaaS Design(https://www.saasui.design/saas-design)과 list-detail 글(https://www.saasui.design/blog/saas-list-detail-master-detail-ux-patterns)에서 시작해, 경로 안의 제품 화면 페이지(`/pattern/...`)만 봤다. 경로 밖 조사는 하지 않았다.

## Candidate work model

| Structural axis | This candidate's explicit choice | Why it fits the target task |
| --- | --- | --- |
| First view | 정비자: 내 알람 대기열(홈) / 파트장: 승인 대기 목록 | 가이드 4쪽 · 15쪽 |
| Navigation | 정비자: 알람 → 진단 → 점검 → 조치 → 보고서 단계 이동(상단 진행 표시) / 파트장: 왼쪽 고정 메뉴 4개 사이 이동 | 가이드 5~12쪽 진행 표시, 15~17쪽 메뉴 |
| Layout topology | 정비자: 단계형 화면 · 좌우 2열(판단 정보 | 지금 할 행동) / 파트장: 왼쪽 메뉴 + 목록 · 상세 2열 | 태블릿 한 화면에 판단 정보와 행동을 함께 |
| Primary information unit | 정비자: 점검 1개(지시 카드)와 원인 후보 행 / 파트장: 보고서 · 호출 · 등급 행 | 한 번에 점검 하나(AC-35) |
| Primary action surface | 정비자: 오른쪽 열의 큰 주 버튼 하나(점검 시작 · 결과 보내기 · 재가동 · 확정 · 호출) / 파트장: 상세 오른쪽 결정 패널 | 장갑 낀 손으로 누르기 쉬운 큰 버튼 하나 |
| Interaction mode | 결과 버튼(정상·이상·확인 불가) + 메모 폼, 확인 질문 모달, 체크리스트 확인 뒤 열리는 버튼 | 결과 버튼이 판정, 메모는 보조(D11) |
| Information exposure | 한 대상에 집중: 한 번에 점검 하나만 보이고, 순위·과거 기록·점검 경로는 같은 화면 왼쪽에 함께 보임 | 다음 할 일 하나에 집중 |
| State and feedback placement | 상단 알람 표시줄과 진행 단계, 화면 안 상태 배너(근거 적음·원문 대체·호출 상태), 점검 경로 타임라인, 파트장 목록의 상태 칩 | 멈춤·대체·호출 상태를 화면 안에서 바로 보임 |

후보가 하나뿐이라 후보 쌍 비교는 없다. 예외 사유는 아래 Gate Brief와 `candidate_count_exception_reason`에 있다.

## Candidate viability

| Scenario refs | Critical path and required information | Additional cost | Compensating benefit | Result |
| --- | --- | --- | --- | --- |
| SC-01, SC-07, SC-18, SC-50, SC-51 | 홈 대기열에서 새 알람 '점검 시작', 진행 중 '이어서 하기', 반려 사유 확인 후 '이어서 하기' / 알람 상태 점 · 시각 · 진행 단계, 반려 사유 | none | 가이드 4쪽 그대로라 추가 이동이 없다 | supports |
| SC-02, SC-09, SC-52, SC-53 | 알람 화면 → 진단 한 화면에서 순위 · 과거 기록 · 다음 점검을 함께 보고 '점검 시작' / 순위 %, 근거 n, 과거 기록 3건, 등급 · 절 · 분, 근거 적음 | none | 판단 정보와 행동이 한 화면에 있어 다시 찾아 들어가지 않는다 | supports |
| SC-03, SC-10 | 잠금 화면에서 '잠금 완료' 뒤에만 사전 확인과 지시가 열림 / 1.2절 절차, 가려진 지시 | 잠금 확인 한 단계(약 2분) | 안전 규칙(R1)이며 생략할 수 없다 | supports |
| SC-04, SC-08, SC-13, SC-17, SC-21 | 지시 1개를 보고 결과 버튼 + 메모 → 확인 질문 또는 소견 안내 → 다음 단계 / 절차 · 판정 기준 · 원문 · 근거, 원문 대체 · 실패 배너 | 애매한 메모일 때만 확인 창 한 번 | 잘못된 순위 변경을 막는다(R7) | supports |
| SC-05, SC-14, SC-15 | 원인 확정 → A 조치 완료 / B 체크리스트 → 재가동 체크리스트 → 경계 이내/여전히 밖 선택 / 원인 · 근거, 등급, 체크리스트, 현재 값 · 경계, 점검 경로 | 체크리스트 확인 | B등급 안전 확인이며 생략하지 않는다 | supports |
| SC-06, SC-16 | 보고서 8항목 확인 · 연필로 수정 → 확정 전 확인 3항목 통과 → 확정 / 8항목 · 출처, 확정 전 확인 | none | 확정 전 확인이 잘못된 보고서의 이력 유입을 막는다 | supports |
| SC-11, SC-12, SC-19 | 지시 대신 호출 요약 → 호출 또는 대기 → 같은 화면에서 답 상태 확인 / C 점검 · 남은 후보 % · 요약 · 답 | none | C · D 작업을 지시하지 않는 권한 경계를 화면으로 보인다 | supports |
| SC-20, SC-30 | 각 앱 로그인 카드에서 ID · 비밀번호 입력 / 역할 불일치 오류 | none | 가이드에 없는 화면이지만 같은 시각 언어로 한 장 | supports |
| SC-31, SC-32, SC-33, SC-34, SC-35 | 승인 대기 목록 → 검토 → 결정 저장 / 요약 타일, 행 상태, 보고서 내용, 결정 3개, 검사 결과 | none | 목록과 검토가 같은 메뉴 안에 있다 | supports |
| SC-36, SC-37 | 호출 목록 → 답하기 → 답 저장 / 유형 · 요약 · 필요한 작업 · 답 선택지 | none | 승인 대기와 같은 목록 → 상세 방식이라 새로 배울 것이 없다 | supports |
| SC-38 | 등급 표에서 행의 등급 선택 → 낮춤이면 경고 확인 → 저장 / 현재 등급, 경고, 변경 기록 | 낮출 때만 경고 확인 한 번 | 야간 단독 작업 확대를 막는다 | supports |
| SC-39 | 감사 기록 표 위 필터 3개 / 시각 · 사용자 · 앱 · 행동 · 대상 | none | 가이드에 없는 화면을 승인 대기와 같은 표 형식으로 만든다(S11 기본안) | supports |

## Product-specific adaptations

| Adaptation ID | Reference principle | Preserved | Changed for this product | Newly designed domain behavior | Use Case / AC boundary |
| --- | --- | --- | --- | --- | --- |
| AD-01 | RP-08 | 정해진 순서의 단계, 한 번에 하나의 주 행동 | 단계 이름을 알람·진단·점검·조치·보고서로 고정, 상단 진행 표시 | 점검 반복(점검 → 입력 → 재순위)은 같은 단계 안에서 돈다 | SC-01~06, AC-17 |
| AD-02 | RP-02 | 본문 옆 같은 대상의 판단 패널 | 왼쪽 = 원인 후보 순위 · 과거 기록 3건, 오른쪽 = 다음 점검 1개 강조 카드 | 순위 %, 근거 n, 등급 배지, 고른 이유는 제품 규칙(R4·R5)으로 설계 | SC-02, SC-09, AC-03, AC-04, AC-29 |
| AD-03 | — | (직접 차용 없음) | — | 잠금 전에는 지시 내용을 흐리게 가리고 잠금 완료 버튼만 연다(R1) | SC-03, SC-10, AC-01 |
| AD-04 | RP-07 | 작업 화면 위 작은 확인 창, 두 버튼 | 확인 질문과 맞지 않는 소견 안내를 같은 창 형식으로 | '네'일 때만 순위 반영, '아니요'면 다시 입력, 소견 안내는 인계/계속 선택(R7) | SC-08, SC-13, AC-05, AC-20 |
| AD-05 | — | (직접 차용 없음) | — | 다음 점검이 C·D면 지시 대신 호출 요약 · 남은 후보 · 호출/대기 버튼(R5, S5) | SC-11, SC-12, SC-19, AC-02, AC-08, AC-23, AC-30 |
| AD-06 | RP-03 | 행 = 이름 + 값 + 오른쪽 조작 | 보고서 8항목 행에 출처 칩과 연필, 등급표 행에 등급 선택 | 확정 전 확인 3항목, 실패 행 강조, 확정 뒤 연필 제거(R8, R10) | SC-06, SC-16, SC-38, AC-07, AC-25, AC-33 |
| AD-07 | RP-01 | 왼쪽 고정 내비 + 넓은 본문 | 메뉴 4개(승인 대기 · 호출 · 권한 등급 · 감사 기록) | 메뉴 구성은 가이드 15~17쪽 그대로 | SC-31~39, AC-17 |
| AD-08 | RP-05 | 행 안 상태 + 행 끝 처리 버튼 | 승인 대기 행의 근거 적음 · 권한 위반 칩과 '검토', 홈 알람 행의 상태 점과 '점검 시작/이어서 하기' | 요약 타일 3개(승인 대기 · 처리할 호출 · 권한 위반) | SC-01, SC-07, SC-31, SC-32, AC-27 |
| AD-09 | RP-02 | 본문 옆 결정 패널 | 보고서 내용 | 결정 3개 + 메모 + 저장 | 수정 후 승인은 왼쪽 항목 직접 편집 + 근거 검사, 반려는 사유 필수(D18, R8) | SC-33~35, AC-06, AC-10, AC-24 |
| AD-10 | RP-04 | 열이 정해진 관리 표 | 호출 목록 · 감사 기록 표, 감사 기록 위 필터 3개 | 호출 유형 칩(파트장 호출 · 숙련자 인계), D등급에는 '승인 후 진행' 없음 | SC-36, SC-37, SC-39, AC-23, AC-26 |
| AD-11 | RP-06 | 가운데 단일 카드 + 주 버튼 | ID · 비밀번호 · 로그인 | 앱별 역할 불일치 오류, 정비자 앱 로그인 뒤 화면 한 번 누름 안내(D9) | SC-20, SC-30, AC-12 |
| AD-12 | — | (직접 차용 없음) | — | 멈춤 화면(숙련자 인계 · 이상 없음 · 감시 · 확인 불가 반복)과 원문 대체 · LLM 실패 배너(S6, 8장) | SC-13~15, SC-17, SC-21, AC-19, AC-21, AC-22, AC-31 |

## Decision screens

| Page ID / State | Candidate screen path | Scenario refs | What a user does here | Observable difference from the other candidates |
| --- | --- | --- | --- | --- |
| T04 / default | wireframes/structure/guide-a/T04--default.html | SC-02 | 순위 · 과거 기록을 보고 다음 점검 하나를 시작 | 후보 하나(D17) — 가이드 6쪽과 같은 영역 · 순서, 값만 데이터 |
| T10 / summary | wireframes/structure/guide-a/T10--summary.html | SC-11 | C등급 점검 대신 호출 요약을 확인하고 호출 | 후보 하나(D17) — 가이드 13쪽과 같은 영역 · 순서 |
| L03 / review | wireframes/structure/guide-a/L03--review.html | SC-33 | 보고서를 읽고 결정 3개 중 하나를 저장 | 후보 하나(D17) — 가이드 16쪽과 같은 영역 · 순서 |

## Candidate page evidence

| Page ID | States | Actor / object / primary action | Completion judgment / required information | Match type | Reference IDs / borrowed principle | Adaptation IDs | Scenario / AC refs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T01 | default, role_error | 정비자 / 정비자 계정 / 로그인 | 정비자 홈이 열림, 역할이 다르면 오류 / ID · 비밀번호 · 역할 오류 문구 | principle | RP-06 / 가운데 단일 입력 카드와 주 버튼 하나 | AD-11 | SC-20 |
| T02 | empty, new_alarm, in_progress, rejected | 정비자 / 내 알람 · 최근 내 보고서 / 새 알람 점검 시작 / 진행 중 이어서 하기 / 반려 확인 | 세션이 열림 / 알람별 설비 · 증상 · 시각 · 상태, 교대 현황, 반려 사유 | principle | RP-05 / 행 안 상태 표시와 행 끝 처리 버튼 | AD-08 | SC-01, SC-07, SC-18, SC-50, SC-51 |
| T03 | default | 정비자 / 알람 1건 / 증상 확인 후 진단 보기 | 진단 화면으로 넘어감 / 증상군, 이탈 센서와 경계, 직전 12회 추이, AI 해석 | contract_designed | — / 알람 해석 화면(증상군 · 센서 표 · 추이 · AI 해석)은 가이드 5쪽과 SC-01이 영역·순서를 정한 제품 고유 화면이다. | AD-01 | SC-01 |
| T04 | default, low_evidence | 정비자 / 원인 후보 · 다음 점검 / 다음 점검과 이유 확인 후 점검 시작 | 잠금 확인으로 넘어감 / 순위 % · 근거 n, 과거 기록 3건, 등급 · 절 · 분, 고른 이유, 근거 적음 | principle | RP-02 / 본문 옆 같은 대상의 판단 패널 | AD-01, AD-02 | SC-02, SC-09, SC-52, SC-53 |
| T05 | before_lock, locked | 정비자 / 잠금 · 사전 확인 / 잠금 완료, 사전 확인 기록 | 지시된 점검이 열림 / 1.2절 절차, 잠금 시각, 가려진 지시 | contract_designed | — / 잠금 게이트는 R1(API 수준 차단)과 가이드 7쪽이 정한 안전 규칙이라 외부 화면에서 빌려 올 수 없다. | AD-03 | SC-03, SC-10 |
| T06 | default, fallback, unable_next, llm_repeat | 정비자 / 지시된 점검 1개 / 절차대로 점검하고 결과 + 메모 보내기 | 순위 갱신 뒤 다음 단계 / 절차, 판정 기준, 원문 · 근거, 점검 n / 최대 m, 원문 대체 표시 | principle | RP-08 / 순서 있는 단계와 아래 고정 주 행동 | AD-01, AD-12 | SC-04, SC-13, SC-17, SC-21 |
| T07 | confirm_question, out_of_scope | 정비자 / 메모 해석 / 확인 질문 답 / 인계 또는 계속 선택 | 순위 반영 또는 다시 입력 / 인계 / 내 메모, AI의 이해, 두 선택지 | principle | RP-07 / 작업 화면 위 작은 확인 창과 두 버튼 | AD-04 | SC-08, SC-13 |
| T08 | action_a, checklist_b, restart_check | 정비자 / 확정 원인 · 조치 / 조치 진행, 체크리스트 확인, 재가동, 경계 확인 입력 | 보고서로 또는 숙련자 인계 / 원인 · 근거, 조치 등급, 체크리스트, 현재 값 · 경계, 점검 경로 | principle | RP-08 / 단계 완료 전에는 다음 행동을 잠금 | AD-01, AD-06 | SC-05, SC-15 |
| T09 | draft, check_failed, confirmed | 정비자 / 보고서 8항목 / 항목 확인 · 수정 후 확정 | 승인 대기 / 8항목 · 출처, 확정 전 확인 3항목 | principle | RP-03 / 행 = 이름 + 값 + 오른쪽 조작 | AD-06 | SC-06, SC-16 |
| T10 | summary, waiting, sent, ans_approved, ans_daytime, ans_direct | 정비자 / 파트장 호출 / 요약 확인 · 수정 후 호출 또는 대기, 답 확인 | 답에 따라 지시 열림 · 감시 · 대기 / C 점검 · 절 · 분, 지금까지 점검, 남은 후보 %, 요약, 답 상태 | contract_designed | — / C·D등급 호출 판정과 요약은 R5·S5가 정한 권한 경계라 외부 화면을 빌려 오지 않는다. | AD-05 | SC-11, SC-12, SC-19 |
| T11 | expert_handover, monitor_close, unable_repeat | 정비자 / 멈춤 / 숙련자 인계 / 감시 마감 | 인계 요약 전송 또는 보고서 작성 / 멈춘 이유, 요약, 점검 경로, 확정 원인 표기 | contract_designed | — / 멈춤 상황 네 가지는 S6과 가이드 14쪽이 정한 제품 고유 상태다. | AD-12 | SC-13, SC-14, SC-15 |
| L01 | default, role_error | 파트장 / 파트장 계정 / 로그인 | 승인 대기 화면이 열림, 역할이 다르면 오류 / ID · 비밀번호 · 역할 오류 문구 | principle | RP-06 / 가운데 단일 입력 카드와 주 버튼 하나 | AD-11 | SC-30 |
| L02 | list, empty | 파트장 / 승인 대기 보고서 / 검토할 보고서 고르기 | 검토 화면으로 / 요약 타일 3개, 행별 설비 · 원인 · 작성자 · 시각 · 근거 · 근거 적음 · 권한 | direct | RP-05, RP-01 / 행 안 상태 열과 행 끝 처리 버튼, 왼쪽 고정 내비 | AD-07, AD-08 | SC-31, SC-32 |
| L03 | review, edit, edit_failed, reject | 파트장 / 보고서 1건 / 그대로 승인 / 수정 후 승인 / 반려 | 이력 추가 또는 작성자에게 반환 / 보고서 내용, 결정 3개, 메모 · 사유, 근거 검사 결과 | principle | RP-02 / 본문 옆 결정 패널 | AD-07, AD-09 | SC-33, SC-34, SC-35 |
| L04 | list, call_detail, handover_detail | 파트장 / 호출 · 인계 / 답과 처리 메모 저장 | 정비자 앱과 보고서에 반영 / 유형, 요약, 필요한 작업, 답 선택지 | principle | RP-04, RP-02 / 열이 정해진 표와 상세 옆 답하기 패널 | AD-07, AD-10 | SC-36, SC-37 |
| L05 | default, lower_warning | 파트장 / 절별 등급 / 등급 변경 | 다음 판정부터 적용, 변경 기록 / 절 · 작업 · 현재 등급, 낮춤 경고, 변경 기록 | principle | RP-03 / 행 = 이름 + 오른쪽 조작 | AD-07, AD-06 | SC-38, SC-53 |
| L06 | default, filtered | 파트장 / 감사 기록 / 설비 · 사용자 · 기간으로 거르기 | 조건에 맞는 기록이 시간순 / 시각 · 사용자 · 앱 · 행동 · 대상 | principle | RP-04 / 열이 정해진 관리 표 | AD-07, AD-10 | SC-39 |

## Observable differences from other candidates

다른 후보가 없다(D17). 대신 가이드와의 차이를 적는다. 구조 차이는 없고 다음만 다르다.
- 값: 가이드 예시 값(M-07, 55%, H-0347, 7.9 K 등) 대신 data/ 에서 계산한 값을 쓴다(D1).
- 문구: 추이 제목을 "최근 30분"에서 "최근 12회 측정"으로 바꿨다(D12). 등급표는 "24절 중 6절"이 아니라 실제 절 수를 쓴다.
- 확인 질문: 결과 버튼 없이 메모만 보낸 경우로 보였다. 가이드 10쪽은 버튼 '이상'과 메모가 같은 뜻인데도 질문하지만, D11에 따라 질문은 메모가 버튼과 어긋나거나 버튼이 없을 때만 나온다.
- 가이드에 없는 상태는 같은 class와 배치 규칙으로 추가했다. 로그인, 반려 보고서, 맞지 않는 소견, 재가동 후 값 확인, 호출 답 3종, 원문 대체, 문장 생성 3회 실패, 수정 후 승인 편집 · 검사 실패, 반려 사유, 호출 상세 2종, 낮춤 경고, 감사 기록이 그렇다(spec 7장).

## Strengths

- 승인된 가이드와 같은 화면이라 팀 · 사용자에게 새로 설명할 것이 없다.
- 한 번에 점검 하나, 큰 주 버튼 하나라 지시 건너뛰기 · 권한 밖 작업이 화면에서 막힌다.

## Trade-offs and likely failure points

- 태블릿 2열 배치라 과거 기록 카드가 좁다. 설비 번호 · 유사도가 길면 줄이 바뀔 수 있다(G2B에서 밀도 조정).
- 파트장 앱의 보고서 검토는 목록과 검토가 다른 화면이라, 여러 건을 연속 검토할 때 목록으로 돌아가야 한다(가이드 15~16쪽 그대로).

## Page inventory coverage

| Page ID | State | Exact renderable path | Scenario covered |
| --- | --- | --- | --- |
| T01 | default | wireframes/structure/guide-a/T01--default.html | SC-20 |
| T01 | role_error | wireframes/structure/guide-a/T01--role_error.html | SC-20 |
| T02 | empty | wireframes/structure/guide-a/T02--empty.html | SC-01 |
| T02 | new_alarm | wireframes/structure/guide-a/T02--new_alarm.html | SC-01 |
| T02 | in_progress | wireframes/structure/guide-a/T02--in_progress.html | SC-07 |
| T02 | rejected | wireframes/structure/guide-a/T02--rejected.html | SC-18 |
| T03 | default | wireframes/structure/guide-a/T03--default.html | SC-01 |
| T04 | default | wireframes/structure/guide-a/T04--default.html | SC-02 |
| T04 | low_evidence | wireframes/structure/guide-a/T04--low_evidence.html | SC-09 |
| T05 | before_lock | wireframes/structure/guide-a/T05--before_lock.html | SC-03, SC-10 |
| T05 | locked | wireframes/structure/guide-a/T05--locked.html | SC-03 |
| T06 | default | wireframes/structure/guide-a/T06--default.html | SC-04 |
| T06 | fallback | wireframes/structure/guide-a/T06--fallback.html | SC-17, SC-21 |
| T06 | unable_next | wireframes/structure/guide-a/T06--unable_next.html | SC-13 |
| T06 | llm_repeat | wireframes/structure/guide-a/T06--llm_repeat.html | SC-17 |
| T07 | confirm_question | wireframes/structure/guide-a/T07--confirm_question.html | SC-08 |
| T07 | out_of_scope | wireframes/structure/guide-a/T07--out_of_scope.html | SC-13 |
| T08 | action_a | wireframes/structure/guide-a/T08--action_a.html | SC-05 |
| T08 | checklist_b | wireframes/structure/guide-a/T08--checklist_b.html | SC-05 |
| T08 | restart_check | wireframes/structure/guide-a/T08--restart_check.html | SC-05, SC-15 |
| T09 | draft | wireframes/structure/guide-a/T09--draft.html | SC-06 |
| T09 | check_failed | wireframes/structure/guide-a/T09--check_failed.html | SC-16 |
| T09 | confirmed | wireframes/structure/guide-a/T09--confirmed.html | SC-06 |
| T10 | summary | wireframes/structure/guide-a/T10--summary.html | SC-11 |
| T10 | waiting | wireframes/structure/guide-a/T10--waiting.html | SC-19 |
| T10 | sent | wireframes/structure/guide-a/T10--sent.html | SC-11 |
| T10 | ans_approved | wireframes/structure/guide-a/T10--ans_approved.html | SC-12 |
| T10 | ans_daytime | wireframes/structure/guide-a/T10--ans_daytime.html | SC-12 |
| T10 | ans_direct | wireframes/structure/guide-a/T10--ans_direct.html | SC-12 |
| T11 | expert_handover | wireframes/structure/guide-a/T11--expert_handover.html | SC-13, SC-15 |
| T11 | monitor_close | wireframes/structure/guide-a/T11--monitor_close.html | SC-14 |
| T11 | unable_repeat | wireframes/structure/guide-a/T11--unable_repeat.html | SC-13 |
| L01 | default | wireframes/structure/guide-a/L01--default.html | SC-30 |
| L01 | role_error | wireframes/structure/guide-a/L01--role_error.html | SC-30 |
| L02 | list | wireframes/structure/guide-a/L02--list.html | SC-31 |
| L02 | empty | wireframes/structure/guide-a/L02--empty.html | SC-32 |
| L03 | review | wireframes/structure/guide-a/L03--review.html | SC-33 |
| L03 | edit | wireframes/structure/guide-a/L03--edit.html | SC-34 |
| L03 | edit_failed | wireframes/structure/guide-a/L03--edit_failed.html | SC-34 |
| L03 | reject | wireframes/structure/guide-a/L03--reject.html | SC-35 |
| L04 | list | wireframes/structure/guide-a/L04--list.html | SC-36 |
| L04 | call_detail | wireframes/structure/guide-a/L04--call_detail.html | SC-36 |
| L04 | handover_detail | wireframes/structure/guide-a/L04--handover_detail.html | SC-37 |
| L05 | default | wireframes/structure/guide-a/L05--default.html | SC-38 |
| L05 | lower_warning | wireframes/structure/guide-a/L05--lower_warning.html | SC-38 |
| L06 | default | wireframes/structure/guide-a/L06--default.html | SC-39 |
| L06 | filtered | wireframes/structure/guide-a/L06--filtered.html | SC-39 |

## Evidence and Use Case links

- Use Case v2(승인): `use-case/v2/use-case-packet.md`, `use-case/v2/scenario-coverage.json`, `use-case/v2/acceptance-criteria.json`
- 화면 상태 목록 근거: 구현 명세 7장(Context Packet 002), 사용 가이드 글자 추출본 `sources/task/T01-user-guide-text.txt`
- sample: `wireframes/samples/review-sample.json`

## Human Gate G2A decision

`decisions/G2A-wireframe-structure.json`에 기록한다.
