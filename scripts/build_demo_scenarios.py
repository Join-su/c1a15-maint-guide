#!/usr/bin/env python3
"""시연 각본 10건(명세 R11)을 만든다. 일회용 생성 스크립트(제품 코드 아님).

- 원본: AI4I 2020 CSV(읽기만, 라벨 열은 build_data.load_rows가 읽자마자 버림). 행 배치 · 알람 판정은 build_data와 같은 규칙.
- 10 ~ 12월 행(이력에 쓰지 않은 행)에서 온도 차 저하 5 · 출력 이탈 2 · 공구 마모 2 · 토크 과부하 1을 시간순으로 고른다.
- 평가 카드와 겹치지 않게 eval/cards/card_udi_map.json의 행 번호(UDI)만 읽어 뺀다(사용자 결정 2026-10-13). 카드 내용 · 정답은 읽지 않는다.
- 각본에는 숨은 원인을 적지 않는다. 화면 추이는 같은 설비의 알람 행 이전 측정 12회(알람 센서 값).
- 각본 행 = 센서 값 · 추이만. 경계 판정 · 증상군은 서버(engine/alarm_rules.py)가 data/alarm_rules.json으로 정한다(FLOW-01).
실행: python3 scripts/build_demo_scenarios.py [--csv PATH]
"""

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("build_data", ROOT / "scripts" / "build_data.py")
bd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bd)

COUNTS = {"CL": 5, "PW": 2, "TW": 2, "LD": 1}
TREND_N = 12


def eval_udis() -> set[str]:
    return set(json.loads((ROOT / "eval" / "cards" / "card_udi_map.json").read_text(encoding="utf-8")).values())


def num(v: float) -> float | int:
    return int(v) if float(v).is_integer() else round(float(v), 1)


def snapshot(r: dict) -> dict:
    return {"air_temperature_k": r["air"], "process_temperature_k": r["proc"], "rotational_speed_rpm": r["rpm"], "torque_nm": r["torque"],
            "tool_wear_min": r["wear"], "temp_diff_k": r["temp_diff"], "power_w": r["power"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(bd.DEFAULT_CSV))
    args = ap.parse_args()
    rows = bd.load_rows(args.csv)
    placed, _ = bd.place_rows(rows)
    th = bd.thresholds([r for r in placed if r["at"] < bd.HISTORY_END])
    excluded = eval_udis()
    history_udis = {json.loads(line)["source"]["udi"] for line in (ROOT / "data/history/maintenance_history.jsonl").read_text().splitlines() if line.strip()}
    chosen, by_group = [], dict.fromkeys(COUNTS, 0)
    for r in placed:
        if r["at"] < bd.HISTORY_END or r["udi"] in excluded or r["udi"] in history_udis:
            continue
        hits = bd.detect(r, th)
        if not hits:
            continue
        hit = hits[0]
        g = hit["group"]
        if by_group[g] >= COUNTS[g]:
            continue
        prior = [p for p in placed if p["equipment_id"] == r["equipment_id"] and p["pos"] < r["pos"]][-TREND_N:]
        by_group[g] += 1
        chosen.append({
            "scenario_id": f"DEMO-{len(chosen) + 1:02d}", "udi": r["udi"], "equipment_id": r["equipment_id"],
            "sensor_snapshot": snapshot(r),
            "trend": [{"at": bd.iso(p["at"]), "value": num(p[hit["key"]])} for p in prior],
        })
        if by_group == COUNTS:
            break
    if by_group != COUNTS:
        raise SystemExit(f"각본 후보 부족: {by_group}")
    out = {"source": {"name": "UCI AI4I 2020", "sha256": hashlib.sha256(Path(args.csv).read_bytes()).hexdigest(), "period": "2026-10 ~ 12월 배치 행"},
           "rule": "R11: 증상군별 시간순 첫 알람 행(평가 카드 · 이력 행 제외), 숨은 원인 없음", "scenarios": chosen}
    (ROOT / "data" / "demo" / "scenarios.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"scenarios={len(chosen)} by_group={by_group}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
