# Prototype Slice: {{version}}

## Selected G2A structure and G2B visual design decisions

승인된 구조·디자인을 Prototype Bundle 안에서 구현 가능한 수준으로 보존한다.

- All approved pages and state inventory:
- Approved G2A structure-render baseline lineage (path and hash):
- Approved G2A blueprint lineage (path and hash):
- Approved G2A selected structure contract lineage (path and hash):
- Approved G2B selected visual rules lineage (path and hash):
- Page/state → scenario / AC mapping:
- Selected structure-contract region → prototype mapping:
- Navigation and interaction rules:
- Visual design rules (type, color/state, density, controls):
- Renderable prototype paths and hash:

## Compiled approved page structure

승인 청사진에서 아래 표를 내용 변경 없이 복사한다. 이 표는 PBC가 G2A 문서를 다시 열지 않고도 구조를 이해하기 위한 Prototype Bundle 내부의 제품 계약이다.

| Page ID | State | Region ID | Selected structure | Content composition | Interaction or state rule | Explicitly excluded alternative |
| --- | --- | --- | --- | --- | --- |

## Compiled selected visual rules

Copy the approved `selected-visual-rules.md` table without changing its rules. This is the complete visual contract for pages and states outside the G2B representative screens.

| Visual axis | Global rule | Preserve from G2A |
| --- | --- | --- |

## Component foundation

Copy the approved `selected-visual-rules.md` **Component foundation** table without changing its rules. G3 must not create a separate visual system for these repeated elements.

| Element | States and form | Token or rule | Intentional exception |
| --- | --- | --- | --- |
| | | | |

## UI surface adaptation

When applicable, copy the approved `selected-visual-rules.md` UI-surface adaptation rows without changing them.

| UI surface ID | Preserved global rule | Surface-specific application | Reason from actor/device/task |
| --- | --- | --- | --- |
| | | | |

## Primary path

## Clickable transitions

## Fixture data

- Fixture / live boundary:
- Data values that alter visible behavior:

## State coverage

- Default:
- Loading, if relevant:
- Empty:
- Error or permission:
- Success:

## UI surface coverage

When the approved Use Case declares multiple product UI surfaces, show each surface's critical Scenario, Page/State evidence, and Acceptance Criteria. These are all required product interfaces, not alternative prototypes.

| UI surface | Critical Scenario | Page / State evidence | Acceptance Criteria |
| --- | --- | --- | --- |

## Derived states outside the approved screen inventory

승인된 Use Case·AC가 요구하지만 G2A 선택 화면에 없던 상태만 기록한다. 원본 Page/State의 구조·탐색·작업 순서·핵심 Region을 유지해야 한다. 새 영역·탐색·작업 순서·제어 방식이 필요하면 이 표를 쓰지 않고 G2A로 돌아간다.

| Added Page ID / State | Source approved Page ID / State | Scenario / AC basis | Preserved structure | Added state expression | Prototype path |
| --- | --- | --- | --- | --- | --- |

## Acceptance Criterion and verification coverage

`prototype-coverage.json`을 참조한다. 모든 G1 AC는 covered 또는 deferred여야 하며, deferred는 G3 Gate Decision의 excluded scope와 일치해야 한다.

`compiled_structure_contract`와 `structure_coverage`는 G2A가 고정한 모든 핵심 결정 Region을 `Page / State / Region` 단위로 정확히 한 번 연결한다. 제목·구분선·보조 문구 같은 장식 요소는 G2A structure contract에 넣지 않는다.

## Gate Brief

`gate-brief.md`를 참조한다.

## Expected user decision / next action

## What is deliberately not represented

## Completeness check

- [ ] Every approved page and state can be located in this bundle.
- [ ] The compiled approved page structure contains every approved page/state and key decision region.
- [ ] The approved G2A structure-render baseline is the primary structural reference; the selected G2B global visual rules and Component foundation are the primary visual reference.
- [ ] A developer can implement the approved visual and interaction rules without reopening G2A/G2B.
- [ ] Every G1 AC is linked to covered or deferred Prototype evidence.
- [ ] Every derived state has an approved Use Case / AC basis and preserves its source page structure.
- [ ] Deferred scope and its reason are explicit.

## Human Gate G3 decision
