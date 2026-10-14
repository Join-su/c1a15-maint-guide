#!/usr/bin/env python3
"""분리 검사(AC-34-C3 · AC-15-C1 일부): 시연 각본 행 ∩ 이력 행 = 0, 각본 행 ∩ 평가 카드 원본 행 = 0. 겹치면 종료 코드 1.

평가 카드 쪽은 eval/cards/card_udi_map.json의 행 번호(UDI)만 읽는다(사용자 결정 2026-10-13). 검사 전용 스크립트이며 제품 코드가 아니다.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server" / "src"))
from c1a15.checks.separation import overlap  # noqa: E402

demo = {s["udi"] for s in json.loads((ROOT / "data/demo/scenarios.json").read_text())["scenarios"]}
history = {json.loads(line)["source"]["udi"] for line in (ROOT / "data/history/maintenance_history.jsonl").read_text().splitlines() if line.strip()}
cards = set(json.loads((ROOT / "eval/cards/card_udi_map.json").read_text()).values())
results = {"demo_rows": len(demo), "history_rows": len(history), "eval_card_rows": len(cards),
           "demo∩history": sorted(overlap(demo, history)), "demo∩eval_cards": sorted(overlap(demo, cards)), "history∩eval_cards": sorted(overlap(history, cards))}
print(json.dumps(results, ensure_ascii=False))
sys.exit(1 if results["demo∩history"] or results["demo∩eval_cards"] or results["history∩eval_cards"] else 0)
