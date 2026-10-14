# G2 Wireframe Structure and Visual Design Review Bundle

G2는 순차적인 두 Human Gate다. G2A는 실제 제품의 검증된 작업 패턴을 현재 Use Case에 맞게 재구성해 구조를 결정하고, G2B는 선택된 화면의 구조를 보존한 채 시각적 완성도와 조작 편의를 결정한다. 어느 단계도 승인된 기능·시나리오·AC·권한을 추가하거나 바꾸지 않는다.

## G2A — reference-backed structure comparison

G1 scenario에서 공통 `page-inventory.json`을 만든다. 이 inventory가 모든 페이지·비교 상태의 기준이다. 오류·권한·빈 상태의 모든 조합을 기계적으로 늘리라는 뜻이 아니라, 각 페이지에서 비교가 필요한 상태를 명시한다. `scenario_handoffs`는 승인된 G1 scenario를 정확히 한 번 `page_state`(하나 이상의 `Page:State`) 또는 `non_ui`(화면으로 표현하지 않는 이유)로 닫는다. 따라서 다음 Gate가 이전 대화 문맥 없이도 어떤 scenario가 어느 화면 상태에서 다뤄지는지 확인할 수 있다.

조사 전에 후보가 될 작업 모델을 먼저 적는다. 작업 모델은 사용자가 일을 시작·판단·완료하는 구조이며, 다음 여덟 축으로 표현한다.

| 구조 축 | 기록할 값의 뜻 |
| --- | --- |
| 첫 화면 | 사용자가 처음 보는 작업 단위: 전체 현황, 처리 대기열, 특정 대상의 상세, 단계별 작업 등 |
| 탐색 방식 | 목록-상세, 단계 이동, 분할 화면, drill-down 등 |
| 화면 토폴로지 | 캔버스, 목록-상세, 보드, 단계형 화면, 단일 집중 화면처럼 작업 단위가 배치되는 방식 |
| 핵심 정보 단위 | 노드, 행, 카드, 타임라인 항목, 장면처럼 사용자가 읽고 선택하는 기본 단위 |
| 주요 조작 위치 | 목록에서 바로 처리, 상세에서 처리, 전용 작업 공간에서 처리 등 |
| 상호작용 방식 | 직접 조작, 명령/폼, inspector, drag-and-drop처럼 핵심 행동을 수행하는 방식 |
| 정보 노출 방식 | 여러 대상을 나란히 비교, 한 대상에 집중, 필요한 정보를 단계적으로 열기 등 |
| 상태·피드백 위치 | 정보 단위 안, 연결/관계 위, 상세 inspector, 활동 이력 등 상태와 결과를 확인하는 위치 |

후보는 모든 축이 달라야 하는 것이 아니다. 단, 적합성 검사를 통과한 후보 쌍마다 `화면 토폴로지`·`핵심 정보 단위`·`상호작용 방식` 중 적어도 하나와 **총 세 축**이 달라야 한다. 이 규칙은 같은 화면에 카드·색·여백만 달리한 변주를 막는다. 노드·카드·행의 색, 테두리, 서체, 그림자 같은 최종 시각 표현은 G2B의 영역이며 여기서 차이로 세지 않는다. 각 후보의 작업 모델을 먼저 정한 뒤, 그 모델을 뒷받침할 화면 근거를 찾는다. 검색 결과의 상위 세 화면을 그대로 후보로 삼지 않는다.

그 다음 핵심 사용자 작업에 맞는 **실제 출시 제품** 화면과 패턴을 찾는다. 예를 들어 목록에서 대상을 찾아 세부 내용을 비교하는 작업에는 list-detail/master-detail 패턴을, 단계별 완료가 중요한 작업에는 workflow/wizard 패턴을 찾는다. 다음은 근거가 될 수 없다.

- Balsamiq 같은 와이어프레임 제작 도구, UI kit, 단순 템플릿
- 제품과 무관한 예쁜 이미지나 generic dashboard gallery
- 현재 Use Case에 없는 기능·권한·data meaning을 끌어오는 외부 제품의 화면

### 목적 기반 discovery route

제품 전체 이름이 아니라, **각 Page ID가 사용자를 위해 수행하는 주된 일**로 route를 고른다. 공개 홈페이지와 로그인 후 업무 화면이 함께 있으면 하나로 뭉뚱그리지 않고 Page ID 그룹별로 각각 분류한다. `reference_strategy`에는 모든 Page ID의 분류·근거·source route를 남긴다.

조사 시작 전에 `reference_strategy.research_scope`를 잠근다. 이 값에는 `public_web_research_authorized`, 허용된 공개 URL, user-provided URL, 열린 조사가 허용된 surface ID, 그리고 route 밖·로그인/유료/비공개 자료가 필요할 때의 `ask_user` 정책을 기록한다. 공개 웹 조사 권한이 확인되지 않았고 제공된 자료만으로 충분하지 않으면, 검색 전에 한 번만 확인한다. 권한이 있는 경우에도 route 밖 조사는 자동으로 확대하지 않는다.

| 분류 | 선택 기준 | 우선 discovery source | 사용 경계 |
| --- | --- | --- | --- |
| `game_ui` | 플레이어의 실시간 조작·HUD·메뉴·인벤토리·퀘스트·피드백이 주된 일 | [Game UI Database](https://www.gameuidatabase.com/) | 아트, 캐릭터, 게임 IP는 복제하지 않고 정보 우선순위·피드백·조작 원리만 참고 |
| `marketing_site` | 가입·문의·구매·브랜드 이해가 주 목적이고, 로그인 후 반복 업무가 주된 일이 아님 | [Lapa Ninja](https://www.lapa.ninja/) | hero·CTA·신뢰 요소·섹션 순서를 참고하되, 템플릿과 장식 이미지는 제품 구조 근거로 쓰지 않음 |
| `interactive_site` | 브랜드 탐색·콘텐츠 경험·프로모션·포트폴리오의 몰입형 상호작용이 주 목적 | [Awwwards](https://www.awwwards.com/websites/) | 모션·서사·시각 표현의 참고용이며, 접근성·성능·정보 구조의 정답으로 취급하지 않음 |
| `workflow_product` | 아래 업무 흐름 신호가 둘 이상인 경우: (1) 여러 지속 데이터/항목을 관리, (2) 대기열·상태·필터·비교를 사용, (3) 여러 단계의 반복 작업을 완료, (4) 역할·권한·인수인계가 있음, (5) 여러 화면/작업 공간을 넘나드는 운영 작업 | [SaaSUI SaaS Design](https://www.saasui.design/saas-design), [SaaSUI list-detail/master-detail](https://www.saasui.design/blog/saas-list-detail-master-detail-ux-patterns) | SaaS인지, 유료인지, 웹 배포인지와 무관하다. 이 신호를 만족하면 업무 화면 route를 사용 |
| `general_utility` | 위 어떤 분류에도 해당하지 않고 업무 흐름 신호가 둘 미만인, 한 사용자의 좁고 직접적인 작업을 끝내는 프로그램 | 고정 source 없음. 실제 출시된 유사 제품을 열린 검색으로 조사 | 기능·플랫폼·입력 방식이 가까운 제품만 고르고, 검색 결과 상위 화면이나 예쁜 gallery를 근거로 쓰지 않음 |

`general_utility`는 “SaaS가 아니다”라는 이유로 선택할 수 없다. 예를 들어 설치형 프로그램이라도 여러 기록·상태·대기열·역할을 관리하면 `workflow_product`다. 반대로 구독형 제품이라도 한 사용자가 단일 입력·계산·변환을 끝내는 화면이라면 `general_utility`가 될 수 있다.

후보 record의 `product`, `screen_or_pattern`, `url`에는 실제 관찰한 제품·화면을 적고, 위 library는 발견 경로일 경우에만 optional `discovery_source`로 남긴다. 후보 수를 세기 전에 모든 대응 scenario의 핵심 경로, 필요한 정보 가시성, 추가 비용, 그 비용을 보상하는 편익을 적합성 검사한다. 승인 Use Case·AC·권한·data meaning을 훼손하거나 편익 없는 이동·재입력·맥락 전환을 만드는 후보는 제외한다. 위험 작업에서는 빠름을 이유로 필요한 확인 단계를 제거하지 않는다. 선택한 source에서 같은 작업 모델만 반복되거나 적합한 구조가 더 없으면 세 번째 후보를 억지로 만들지 않는다. 남은 후보가 둘 또는 하나일 때는 제외한 구조와 비적합 사유를 기록한다.

직접 대응 화면이 없다는 것은 중단 사유가 아니다. 각 후보·페이지는 아래 셋 중 하나를 택한다.

| `match_type` | 계속 진행할 수 있는 조건 | 필수 기록 |
| --- | --- | --- |
| `direct` | 참조 화면의 보이는 구조와 작업이 페이지 작업에 직접 대응 | reference ID, 화면에서 실제로 확인한 구조·상태 |
| `principle` | 가까운 화면이 같은 작업 원리를 제공하며, 제품 고유 기능은 승인 Use Case·AC로 설계 가능 | reference ID, 차용 원리, adaptation ID, scenario link |
| `contract_designed` | 외부 화면을 직접 차용하는 것이 부적절하지만 승인 Use Case·AC가 페이지의 행동·완료 기준을 충분히 제공 | 직접 차용이 부적절한 이유, adaptation ID, scenario link |

route 안에 `principle`로 쓸 작업 원리도 없고 `contract_designed`를 뒷받침할 승인 기준도 없을 때만, 열린 조사 권한 또는 사용자 참고 자료를 요청한다. 제품 계약을 새로 만들거나 바꿔야 하는 경우에는 route 밖 조사로 해결하지 않고 멈춘다.

실제 출시 제품의 screenshot은 `visible_structure`와 `visible_state`의 근거가 될 수 있다. screenshot만으로 숨은 interaction, authority, responsive behavior를 확인했다고 주장할 수는 없다. reference record에는 `evidence_modality: screenshot | interactive | documented_flow`와 실제로 확인한 `verified_observables`를 기록한다.

외부 제품은 복제 대상이 아니다. 현재 제품의 사용자·fixture·용어·제약에 맞는 후보를 판단하기 위한 구조 근거다. 참조 화면에 직접 존재하지 않는 제품 고유 기능은 참조 패턴을 그대로 흉내 내지 말고, 승인 Use Case가 요구하는 전용 영역·상태·조작으로 설계해 붙인다. `reference-board.html`에는 reference ID, 제품, 실제 screen/pattern, URL, 확인 시각, 맞는 사용자 작업, 빌려 올 원리, 빌려 오지 않을 제품 결정을 보인다. 신뢰할 수 있는 화면을 직접 확인할 수 없으면 URL이나 설명을 꾸며 내지 않고 G2A를 멈춰 사용자에게 reference 또는 조사 권한을 요청한다.

예시는 하나의 도메인에 편향되지 않게 세 종류를 함께 고려한다. 실행 흐름 화면은 workflow 판단 원리만 참고하고 연결·상태·재시도 조작을 새로 설계할 수 있다. 여러 대상을 비교하는 화면은 list-detail 탐색 원리만 참고하고 비교 기준·일괄 작업을 새로 설계할 수 있다. 검토·승인 화면은 review queue의 우선순위 표현만 참고하고 승인 조건·이력·되돌리기 범위를 새로 설계할 수 있다. 세 경우 모두 외부 제품의 기능·권한·data meaning은 가져오지 않는다.

```text
wireframes/
├── page-inventory.json
├── reference-board.html             # 출시 제품의 화면·패턴 근거
├── structure-review.html            # decision view + coverage view
├── candidates.md
├── structure/
│   ├── candidate-a/P01--default.html
│   ├── candidate-a/P02--empty.html
│   ├── candidate-a.md               # reference·작업 방식·차이 설명
│   ├── candidate-b/...
│   ├── candidate-c/...
│   ├── selected/P01--default.html   # 선택/결합 결과의 실제 화면
│   ├── selected.md                  # 선택 화면에서 추출한 사람이 읽는 구조 청사진
│   ├── selected-structure-contract.json # 핵심 Page/State/Region의 machine-readable 구조 계약
│   └── selected-visual-baseline.json
├── flows/
└── samples/review-sample.json
```

후보는 기본으로 최대 3개의 **적합한** 선택지다. 둘 또는 하나만 남는 경우에는 `run-state.json`의 `candidate_count_exception_reason`과 G2A Gate Brief에, 제외한 구조와 비적합 사유를 기록한다. reference는 개수가 아니라 후보의 작업 모델을 실제로 바꾸는 적합성으로 고른다. 후보 쌍은 핵심 구조 축 하나와 총 세 축 이상에서 달라야 한다. 색상·카드 모양·여백만 달라서는 안 된다.

각 후보는 inventory의 모든 `Page ID / comparison state`에 대해 실제 renderable HTML/CSS 또는 동등한 이미지의 **정확한 경로**를 제공한다. 후보 문서에는 reference pattern, 어떤 작업 방식을 택했는지, 참조 원리에서 보존한 것·현재 기능 때문에 변경한 것·새로 설계한 것을, 다른 후보와 비교한 관찰 가능한 차이, 장점·trade-off와 함께 기록한다. 후보 문서는 화면을 만드는 청사진이 아니다. 먼저 화면을 만든다.

`candidate_page_evidence`는 후보와 Page ID의 교차 전체를 빠짐없이 기록한다. 각 행은 상태 목록, `actor / object / primary_action / completion_judgment / required_information`으로 정의한 page task, match type, **승인 G1 scenario ID** link, adaptation link를 갖는다. 모든 후보가 모든 승인 scenario를 빠짐없이 다뤄야 한다. `candidate_viability`는 이 scenario link 전체를 대상으로 후보가 핵심 경로를 효율적·안전하게 지원하는지 기록한다. 이렇게 하면 실행 흐름·비교·승인 밖의 페이지도 먼저 “사용자가 어떤 일을 끝내는가”로 분류한 뒤 맞는 원리를 찾는다.

`structure-review.html`에는 다음 두 보기가 있어야 한다.

- `decision view` (기본): 후보 차이가 가장 분명한 1~3개 핵심 `Page ID / State`를 큰 크기로 보여 준다. 같은 화면 상태의 A/B/C만 나란히 보여 주고, 사용자가 실제로 무엇을 다르게 하게 되는지와 핵심 scenario의 추가 비용·보상 편익을 명시한다.
- `coverage view`: inventory 전체의 모든 후보·페이지·상태를 감사용으로 보여 준다. 기본 보기에 수십 개의 축소 화면을 모두 쌓아 판단을 어렵게 만들지 않는다.

### 가벼운 검토 상호작용

보드는 정적 HTML/CSS와 작은 vanilla JavaScript만 사용한다. framework, server, 외부 script, 후보 화면의 HTML 복제는 넣지 않는다. 후보 화면은 기존 renderable path를 iframe 또는 동등한 참조로 보여 주고, coverage view의 화면은 `loading="lazy"` 또는 동등한 지연 로딩을 사용한다.

- 각 preview는 hover와 keyboard focus에서 원본 경로의 확대 preview를 띄운다. 확대는 viewport overlay 또는 겹침 레이어로 제공해 주변 카드의 위치를 밀지 않고, pointer/focus가 끝나면 닫힌다.
- 각 `Page ID / State`의 후보 카드에는 명확한 클릭 선택 control을 둔다. 선택 상태는 화면별로 하나여야 하며, 선택 요약에는 아직 선택하지 않은 페이지·상태도 보인다.
- `복사`와 `다운로드` control은 현재 선택을 `g2a-page-state-selection.json`으로 내보낸다. 다운로드는 browser `Blob`만 사용하고, 복사는 Clipboard API를 쓸 수 없을 때 같은 JSON을 화면의 read-only text area로 보여 준다. 이 HTML은 로컬 파일에 직접 쓰지 않는다.
- 내보낸 JSON은 다음 Gate의 입력 기록이다. Human Gate 승인 전에는 구현 또는 G2B로 진행하지 않는다. 사용자는 선택을 바꾸거나 custom 재정의를 Gate note에 남길 수 있다.

```json
{
  "run_id": "{{run_id}}",
  "artifact": "wireframe_structure",
  "artifact_version": "{{version}}",
  "source_board": "wireframes/structure-review.html",
  "selections": [
    {
      "page_id": "P01",
      "state": "default",
      "selected_candidate_id": "candidate-a",
      "source_path": "wireframes/structure/candidate-a/P01--default.html",
      "note": ""
    }
  ]
}
```

각 후보×페이지×상태는 보드에 실제 화면과 정확히 일치하는 marker를 남긴다.

```html
<article
  data-cell="candidate-a:P01:default|wireframes/structure/candidate-a/P01--default.html"
  data-preview-cell="candidate-a:P01:default|wireframes/structure/candidate-a/P01--default.html"
  data-selection-cell="candidate-a:P01:default|wireframes/structure/candidate-a/P01--default.html">
```

G2A Gate에서 선택·결합·재정의한 결과는 `structure/selected/`에 먼저 실제 화면으로 렌더한다. 그 뒤 화면에서 `selected.md`를 추출한다. 이 문서에는 페이지·상태별 핵심 `Region ID`, 역할, 하나의 구조 방식, 내용 구성, 행동/상태 규칙, 명시적 제외안을 기록한다. `표/카드`처럼 여러 구조를 함께 허용하지 않는다. 청사진은 G3가 구조를 바꾸지 않도록 지키는 계약이며, 화면을 다시 그리는 생성 지시문이 아니다.

`selected-visual-baseline.json`은 선택 화면마다 실제 path와 SHA-256을 잠근다. 이후 G2B와 G3는 이 기준선을 읽는다.

`run-state.json`의 `wireframe_structure` record 예시는 다음과 같다.

```json
{
  "reference_patterns": [
    {
      "id": "RP-01",
      "product": "{{shipped product}}",
      "screen_or_pattern": "{{specific screen or pattern}}",
      "url": "https://...",
      "discovery_source": "SaaSUI SaaS Design | SaaSUI master-detail | direct",
      "evidence_modality": "screenshot | interactive | documented_flow",
      "verified_observables": ["visible_structure", "visible_state"],
      "observed_at": "{{ISO-8601 timestamp}}",
      "task_fit": "{{approved scenario task this supports}}",
      "borrow": "{{structural principle only}}",
      "do_not_borrow": "{{feature, authority, or data decision excluded}}"
    }
  ],
  "reference_board": "wireframes/reference-board.html",
  "reference_strategy": {
    "research_scope": {
      "public_web_research_authorized": true,
      "permitted_public_source_urls": ["https://www.saasui.design/saas-design"],
      "user_provided_source_urls": [],
      "open_discovery_surface_ids": [],
      "outside_route_policy": "ask_user",
      "restricted_access_policy": "ask_user"
    },
    "surfaces": [
      {
        "id": "public-entry",
        "page_ids": ["P01"],
        "classification": "workflow_product",
        "workflow_signals": ["persistent_records", "queue_state_filter_compare"],
        "classification_evidence": ["{{why this page group's primary purpose has this classification}}"],
        "discovery_mode": "curated",
        "source_guides": ["https://www.saasui.design/saas-design"]
      }
    ]
  },
  "candidate_pages": {
    "candidate-a": {"P01": {"default": "wireframes/structure/candidate-a/P01--default.html"}},
    "candidate-b": {"P01": {"default": "wireframes/structure/candidate-b/P01--default.html"}},
    "candidate-c": {"P01": {"default": "wireframes/structure/candidate-c/P01--default.html"}}
  },
  "candidate_briefs": {
    "candidate-a": "wireframes/structure/candidate-a.md",
    "candidate-b": "wireframes/structure/candidate-b.md",
    "candidate-c": "wireframes/structure/candidate-c.md"
  },
  "candidate_reference_ids": {
    "candidate-a": ["RP-01"],
    "candidate-b": ["RP-01"],
    "candidate-c": ["RP-01"]
  },
  "candidate_page_evidence": {
    "candidate-a": {
      "P01": {
        "states": ["default"],
        "page_task": {
          "actor": "{{actor}}",
          "object": "{{object}}",
          "primary_action": "{{action}}",
          "completion_judgment": "{{what completion looks like}}",
          "required_information": "{{what must be visible to decide}}"
        },
        "match_type": "direct | principle | contract_designed",
        "reference_ids": ["RP-01"],
        "borrowed_principle": "{{required for principle}}",
        "contract_design_reason": "{{required for contract_designed}}",
        "adaptation_ids": ["AD-01"],
        "scenario_refs": ["S-01"]
      }
    }
  },
  "candidate_viability": {
    "candidate-a": {
      "status": "viable",
      "scenario_assessments": [
        {
          "scenario_refs": ["S-01"],
          "critical_path": "{{how the candidate completes this approved scenario}}",
          "required_information": "{{information visible when the user decides}}",
          "additional_cost": "{{none, or the cost introduced}}",
          "compensating_benefit": "{{why that cost is justified, or why none exists}}",
          "result": "supports"
        }
      ]
    }
  },
  "candidate_work_models": {
    "candidate-a": {
      "first_view": "{{explicit first work unit}}",
      "navigation": "{{explicit navigation model}}",
      "layout_topology": "{{canvas, board, list-detail, wizard, or another structure}}",
      "primary_information_unit": "{{node, row, card, timeline item, or another unit}}",
      "primary_action_surface": "{{explicit action location}}",
      "interaction_mode": "{{direct manipulation, form, inspector, or another interaction}}",
      "information_exposure": "{{explicit information exposure model}}",
      "state_feedback_placement": "{{where status and result feedback appears}}"
    },
    "candidate-b": {
      "first_view": "{{explicit first work unit}}",
      "navigation": "{{explicit navigation model}}",
      "layout_topology": "{{canvas, board, list-detail, wizard, or another structure}}",
      "primary_information_unit": "{{node, row, card, timeline item, or another unit}}",
      "primary_action_surface": "{{explicit action location}}",
      "interaction_mode": "{{direct manipulation, form, inspector, or another interaction}}",
      "information_exposure": "{{explicit information exposure model}}",
      "state_feedback_placement": "{{where status and result feedback appears}}"
    },
    "candidate-c": {
      "first_view": "{{explicit first work unit}}",
      "navigation": "{{explicit navigation model}}",
      "layout_topology": "{{canvas, board, list-detail, wizard, or another structure}}",
      "primary_information_unit": "{{node, row, card, timeline item, or another unit}}",
      "primary_action_surface": "{{explicit action location}}",
      "interaction_mode": "{{direct manipulation, form, inspector, or another interaction}}",
      "information_exposure": "{{explicit information exposure model}}",
      "state_feedback_placement": "{{where status and result feedback appears}}"
    }
  },
  "decision_screens": ["P01:default"],
  "board": "wireframes/structure-review.html",
  "selected_pages": {"P01": {"default": "wireframes/structure/selected/P01--default.html"}},
  "selected_visual_baseline": "wireframes/structure/selected-visual-baseline.json",
  "selected_blueprint": "wireframes/structure/selected.md",
  "selected_structure_contract": "wireframes/structure/selected-structure-contract.json"
}
```

## G2B — design refinement lock

G2A 승인 후 `selected-visual-baseline.json`의 `semantic_alias: selected_structure_render_baseline`과 선택 화면을 **구조·작업 흐름 기준선**으로 먼저 읽고, [Design Playbook](07-design-playbook.md)을 주입한다. 기준선의 화면은 Region, information unit, navigation, task order, required metadata, status meaning, action affordance를 보존하기 위한 것이다. G2A render의 palette, typography, spacing, surface, elevation, corner radius, decorative illustration, item silhouette은 G2B의 잠정 표현이므로 그대로 복제하지 않는다. 단, 특정 모양이 status·port·connection·control affordance처럼 승인된 의미나 조작을 전달한다면 그 의미와 조작은 보존한다.

Playbook은 여러 공개 design system에서 미리 정제한 원칙의 짧은 내부 기준이다. 매 run마다 원문 사이트를 탐색하는 지침이 아니며, Use Case·AC·권한·data meaning을 다시 해석하는 근거도 아니다. Playbook에 없는 시각 문제가 있어 외부 조사가 필요하면 먼저 사용자에게 범위와 이유를 요청한다.

`page-inventory.json`에서 대표 화면 3개를 고른다. 페이지가 3개 미만이면 모든 페이지를 쓴다. 각 화면은 `Page ID / State`를 함께 고정하며, 서로 다른 핵심 작업·위험 또는 상태 언어를 보여야 한다. 선택 이유를 기록한다.

```text
wireframes/design/
├── design-review.html
├── directions.md
├── direction-a/P01.html
├── direction-a/P05.html
├── direction-b/P01.html
├── direction-c/P01.html
└── direction-d/P01.html
```

`run-state.json`의 `visual_design` record는 G2A 기준선과 방향별 before/after 설명을 함께 잠근다. 4~6개 방향이 기본이며, 1~3개인 경우에는 `direction_count_exception_reason`이 필요하다.

```json
{
  "structure_version": "{{approved G2A version}}",
  "selected_visual_baseline": "wireframes/structure/selected-visual-baseline.json",
  "representative_page_ids": ["P01"],
  "representative_page_states": {"P01": "default"},
  "design_playbook": "references/07-design-playbook.md",
  "board": "wireframes/design/design-review.html",
  "directions": {
    "direction-a": {"P01": "wireframes/design/direction-a/P01.html"},
    "direction-b": {"P01": "wireframes/design/direction-b/P01.html"},
    "direction-c": {"P01": "wireframes/design/direction-c/P01.html"},
    "direction-d": {"P01": "wireframes/design/direction-d/P01.html"}
  },
  "direction_briefs": {
    "direction-a": "wireframes/design/direction-a.md",
    "direction-b": "wireframes/design/direction-b.md",
    "direction-c": "wireframes/design/direction-c.md",
    "direction-d": "wireframes/design/direction-d.md"
  },
  "visual_signatures": {
    "direction-a": {
      "typography_density": "compact operational hierarchy",
      "color_state": "high-contrast semantic status bands",
      "surface_hierarchy": "flat grouped work surfaces",
      "item_control_form": "precise rectangular controls",
      "emphasis_reading_order": "status-first scan"
    },
    "direction-b": {
      "typography_density": "generous guided hierarchy",
      "color_state": "restrained contextual status accents",
      "surface_hierarchy": "layered decision surfaces",
      "item_control_form": "soft grouped controls",
      "emphasis_reading_order": "decision-first scan"
    },
    "direction-c": {
      "typography_density": "editorial explanatory hierarchy",
      "color_state": "neutral base with high-attention exception states",
      "surface_hierarchy": "calm continuous workspace",
      "item_control_form": "distinctive but explicit work-area forms",
      "emphasis_reading_order": "context-first scan"
    },
    "direction-d": {
      "typography_density": "balanced workspace hierarchy",
      "color_state": "signal-led operational palette",
      "surface_hierarchy": "high-contrast functional grouping",
      "item_control_form": "compact utility controls",
      "emphasis_reading_order": "action-first scan"
    }
  }
}
```

G2B의 후보는 선택 화면을 버리고 새 화면을 상상하는 design 방향이 아니라 **design refinement**다. 기본 4~6개 방향은 대표 화면의 before/after를 실제 렌더 가능한 HTML/CSS 또는 동등한 이미지로 제공한다. 후보를 늘린다고 화면 구조·fixture·상태를 매번 다시 만들지 않는다. 같은 구조 renderable과 fixture를 공유하고, 방향별 visual layer만 달리해 생성 시간과 구조 drift를 제한한다.

각 방향은 단순한 강도 단계(`quiet / balanced / expressive`)가 아니라 독립된 design hypothesis다. 이름은 후보의 시각 원리를 설명해야 하며, 강도는 필요할 때만 그 가설의 한 축으로 기록한다. `visual_signatures`에는 각 방향의 다섯 축 실제 선택값을 적는다. 모든 후보 쌍은 아래 다섯 축 중 적어도 세 값이 달라야 한다.

| 시각 축 | 바꿀 수 있는 것 | 보존할 것 |
| --- | --- | --- |
| 서체·밀도 | type scale, line length, whitespace, scan density | information unit와 필수 정보 |
| 색·상태 언어 | palette, contrast, status encoding, emphasis | status meaning과 required state visibility |
| 표면·위계 | border/elevation, grouping, background, depth | Region의 역할과 containment 관계 |
| item silhouette·control form | node/card/control의 shape, radius, weight, affordance styling | item meaning, required metadata, interaction/connection affordance |
| 강조·읽기 순서 | focal point, label hierarchy, visual rhythm | navigation, user task order, 기능·권한·AC |

각 방향에서 아래를 명시한다.

| 항목 | 기록할 내용 |
| --- | --- |
| 유지한 구조 | G2A 화면의 layout, navigation, task order, 기능/권한/AC 중 바꾸지 않은 것 |
| 바꾼 표현 | 적용한 Playbook 원칙과 서로 다른 시각 가설; 서체, hierarchy, density, color/state, spacing, surface, item/control form, accessibility 표현 |
| 기대 편익 | 더 빨리 읽기, 상태 오해 감소, 조작 용이성 등 화면에서 관찰 가능한 결과 |
| Trade-off | 밀도, 브랜드 톤, 학습 비용, 강조 충돌 등 |

카드/표의 정보 단위, 영역 배치, 탐색 방식, 사용자의 작업 순서, 새 기능·권한·AC는 G2B에서 바꾸지 않는다. 그런 변경이 실제로 필요하면 G2A로 돌아간다. `design-review.html`은 모든 방향×대표 화면을 확대 가능한 실제 크기 preview로 보여 주고, 방향별 다섯 시각 축의 실제 값을 한 표로 함께 보여 준다. 현재 환경에 검증된 design ideation 또는 UI guideline skill이 있으면, render 뒤 접근성·가독성·조작 편의 검토에만 사용할 수 있다. 이 도구의 제안은 승인된 제품 계약을 바꾸지 않는다.

각 board cell에는 실제 렌더와 연결된 아래 marker를 남긴다. 비교 board가 디자인 후보를 생략하거나 가짜 thumbnail만 보여 주지 않는지 확인하기 위한 것이다.

```html
<article data-design-cell="direction-a:P01:default|wireframes/design/direction-a/P01.html">
```

Human Gate G2B 승인 후에는 선택된 direction을 `wireframes/design/selected-visual-rules.md`로 한 번만 컴파일한다. 이 문서는 대표 화면 밖의 모든 승인 페이지·상태에 적용할 전역 규칙이며, G3는 이 문서를 시각 기준으로 사용한다. Gate Decision에는 선택한 `selected_direction_id`와 이 문서의 `selected_visual_rules_path`를 기록한다.

## Fidelity boundary

- G2A: reference-backed, mid-to-high fidelity의 실제 화면 후보로 구조·흐름·상태를 비교
- G2B: 선택 G2A 화면의 구조를 유지한 final visual refinement 결정
- G3: G2A 구조·작업 흐름 기준선과 G2B 최종 시각 표현을 이용한 clickable flow·상태 검증
