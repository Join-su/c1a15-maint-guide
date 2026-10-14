# G2B Design Playbook

> Curated: 2026-10-01. This is a compact, reusable visual-design input for G2B—not a product specification and not a requirement to browse the linked sites on every run.

## Purpose and boundary

Use this Playbook after G2A to generate design hypotheses that make an approved structure easier to read, operate, and distinguish. It may change visual language and item/control form. It may not change a Use Case, Acceptance Criterion, authority, data meaning, required information unit, navigation, task order, or region containment decided at G2A.

For each G2B direction, cite only the principle IDs that actually shaped it. Do not apply every principle or imitate a source product's brand. If none of these principles address a needed visual question, ask the user before researching outside this Playbook.

## Curated source roles

| Source | Why it is included | Use as | Do not use as |
| --- | --- | --- | --- |
| [Fluent 2](https://fluent2.microsoft.design/get-started/design) | Productivity software's coherent tokens and code-aligned components | A baseline for focused work surfaces, clear actions, and consistent state | A mandate to make every product look like Microsoft |
| [Carbon](https://carbondesignsystem.com/) | Enterprise-ready foundations, data visualization, and AI patterns | A baseline for dense data, status hierarchy, and operational clarity | A visual theme to copy wholesale |
| [Atlassian Design](https://atlassian.design/) | Collaboration, work tracking, and AI-assisted product patterns | A check on team context, progress, and navigation clarity | A generic gallery of finished screen designs |
| [Primer](https://primer.style/) | Developer-tool Product UI, primitives, and accessibility | A check on technical information readability and composable controls | A default brand for non-developer products |
| [Polaris](https://polaris.shopify.com/) | Task-focused administration, form, and feedback patterns | A check on guided input, validation, and operational feedback | A reason to impose commerce conventions on another domain |

The first two are primary visual-system sources. Atlassian, Primer, and Polaris are selective secondary sources: use their relevant principle only when the product's work resembles their domain.

## Principle catalogue

| ID | Principle | Apply when | Guardrail |
| --- | --- | --- | --- |
| FL-01 | Make the current task and primary action immediately scannable through deliberate type, spacing, and emphasis. | A productivity or editor surface has competing controls. | Do not hide a required secondary action or alter task order. |
| FL-02 | Use a small, coherent token set for color, spacing, radius, stroke, and size. | Multiple screens or states need a unified visual language. | Token consistency must not flatten meaningful state distinctions. |
| CA-01 | Give dense data and operational states a clear visual hierarchy before adding decoration. | Tables, inspectors, dashboards, run histories, or monitoring views. | Do not reduce necessary detail merely to create whitespace. |
| CA-02 | Encode status with redundant cues: label/icon/placement as well as color. | Errors, risk, progress, approval, or asynchronous work is present. | Preserve approved status meanings and accessible contrast. |
| AT-01 | Make shared context, handoffs, and progress legible at the point of work. | Collaboration, review, assignment, or AI-assisted workflows. | Do not add collaboration features that G1 did not approve. |
| PR-01 | Treat technical labels, code-like data, and control states as first-class reading material. | Developer tools, LLMOps, infrastructure, or configuration screens. | Do not apply developer-tool density to an audience that needs guided service. |
| PO-01 | Put validation, consequences, and recovery next to the input or decision that caused them. | Forms, setup, request, approval, or destructive-action flows. | Do not add new confirmation steps or authority checks. |
| EX-01 | Reserve expressive form for the product's focal work area; keep chrome and routine controls calm. | A graph, canvas, editor, interactive visualizer, or key empty state benefits from character. | Expression cannot obscure data, reduce affordance, or override the product's purpose. |

## Producing diverse directions efficiently

1. Reuse the approved G2A region tree, fixture data, state names, and interaction hooks. Treat the G2A render's aesthetic tokens as replaceable.
2. Select the relevant principle IDs, then define 4–6 hypotheses. A hypothesis states the intended work experience, its chosen principles, and its visual contrast from the other directions.
3. Render only the same three representative pages for every direction. Build one shared structural source and apply each direction through a visual layer; do not hand-rebuild every page.
4. Make each pair of directions differ on at least three of: type/density, color/state language, surface/hierarchy, item/control form, emphasis/reading order.
5. In the review board, show every direction at a readable size and one compact visual-delta table. Review each direction against the fixed G2A contract; do not compare every pair exhaustively.

## Craft floor before the Human Gate

Direction diversity is not proof that any direction is ready for a person to choose. Before the board, record a compact Component foundation for only the repeated elements actually present in the representative screens. Then run one separate pass over the rendered screens. It checks alignment, repeated-component consistency, surface/edge quality, typography/density, and state clarity; it does not decide product structure or aesthetic preference.

The pass may use an available design skill only when it can inspect the actual render. Review all directions together, make at most one direction-level visual-layer repair, and exclude a direction that remains visibly unfinished. Do not add a critic, a Human Gate, a score, page-by-page repair loops, or a second Craft Review. The board must show that each displayed direction is craft-ready and link to its direction brief.

## Example hypothesis shapes

These are patterns, not required labels or a fixed candidate set.

| Hypothesis | Likely principles | Visual choice | Best fit |
| --- | --- | --- | --- |
| Operational precision | FL-01, CA-01, CA-02 | Compact type, disciplined surfaces, explicit status bands | Monitoring, data, review work |
| Guided clarity | FL-01, PO-01 | Larger decision hierarchy, local validation, restrained grouping | Setup, request, approval work |
| Focused canvas | EX-01, CA-02 | Calm application chrome with a distinct but legible graph/editor work area | Diagram, graph, media, spatial interaction |

## Maintenance

Refresh this file only when a G2B run reveals a concrete missing visual decision or when a cited source materially changes. Record the source, changed principle, and reason for the update. Do not expand it into a copied design-system manual.
