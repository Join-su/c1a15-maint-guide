#!/usr/bin/env python3
"""리트리버 정답 자동 일관성 검사(EV-003 ES-04 · change-contract-v7 CC-05, D-384 — 사람 확인 20장 대신).

- 기준 = 생성 원본 scripts/manual_spec.py(매뉴얼 · 이력 생성기가 함께 읽는 정의: CAUSES · SECTIONS · CAUSE_ACTION · GRADES)를 정의로만 읽는다.
  함께 읽는 것: data/manuals · data/history · eval/cards/<set>(cards · card_inputs · gold.jsonl). generation/ · 카드 ↔ 원본 행 대응 · 원본 CSV · 망 · LLM은 쓰지 않는다.
- K1 카드 ↔ 원인 표 · K2 매뉴얼 정답 줄 ↔ 정의의 원인 · 점검 글(빠짐 · 남음 0) · K3 이력 ↔ 원인 · 점검 · 서술(규칙에 맞는 이력 빠짐 0) · K4 어긋남 목록.
  x.1 '이상 없음 기준' · '호출' 줄은 정의에 글이 없어(생성기 글) 절 · 머리 표지만 본다. K3 '소견' = '이상' 점검 단계의 note 칸.
  보증 범위는 '생성 원본과의 일관성'까지다(현장 타당성은 보증하지 않음, 보존 계약 v3 GAP-02).
- test는 숨김(약속 F): 화면 · 보고에 건수 · by_check · sha256만. 어긋남이 있으면 종료 1로 멈춘다(오케 판단).
- --emit-result(val만): 표본 20장 결과를 확인 화면 결과와 같은 모양(CC-03)으로 — make_gold.py apply-human 입력.

실행: python3 eval/check_gold.py --set val|test [--out <보고.json>] [--emit-result <결과.json>]
"""
import argparse
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True  # 정의 · 도구를 불러와도 저장소에 __pycache__를 쓰지 않음(VC-G11)
_spec = importlib.util.spec_from_file_location("make_gold", HERE / "make_gold.py")
mg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mg)

OUTCOME = {"manual_cause": "원인 확정", "none": "이상 없음·감시", "out_of_graph": "원인 미상·숙련자 인계"}
CHECKS = ("K1", "K2", "K3")


def load_definition(root: Path):
    """생성 원본 정의(값만 있는 모듈 — VC-G11이 import · 파일 열기 0을 확인)."""
    spec = importlib.util.spec_from_file_location("manual_spec", root / "scripts/manual_spec.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Definition:
    def __init__(self, m):
        self.m = m
        self.sections = {s["id"]: s for s in m.SECTIONS}
        self.chapter = {g["code"]: g["chapter"] for g in m.GROUPS}

    def checks(self, group: str, code: str, confirms: bool) -> list[dict]:
        return [
            s
            for s in self.m.SECTIONS
            if s.get("kind") == "check" and s.get("group") == group and s.get("cause") == code and bool(s.get("confirms")) == confirms
        ]

    def expected_manual(self, group: str, hidden: dict) -> list[tuple[str, str, str]]:
        """(rule, 절, 정의로 기대하는 줄 글). 머리글만 정하는 줄은 끝을 '…'로."""
        x1 = f"{self.chapter[group]}.1"
        if hidden["type"] == "manual_cause":
            code = hidden["code"]
            name, desc = self.m.CAUSES[code]
            conf = self.checks(group, code, True)[0]
            g = conf["grade"]
            out = [
                ("M-1", x1, f"| {code} | {name} | {desc} | {conf['id']} |"),
                ("M-2", conf["id"], f"**권한 등급** {g} {self.m.GRADES[g][0]} · **소요** 약 {conf['minutes']}분 · **연결 원인** {code} {name}(확정)"),
                ("M-2", conf["id"], f"**판정 기준** {conf['abnormal']}"),
            ]
            return out + [("M-3", s["id"], f"**판정 기준** {s['abnormal']}") for s in self.checks(group, code, False)]
        if hidden["type"] == "none":
            return [("M-4", x1, "**이상 없음 기준**…"), ("M-4", "6.2", f"1. {self.sections['6.2']['steps'][0]}")]
        return [("M-5", x1, "**호출**…"), ("M-5", "1.4", "- " + next(b for b in self.sections["1.4"]["body"] if b.startswith("숙련자 인계:")))]


def line_matches(want: str, got: str) -> bool:
    return got.startswith(want[:-1]) if want.endswith("…") else got == want


def history_problem(d: Definition, r: dict, group: str, hidden: dict) -> str | None:
    kind, o, nar, steps = hidden["type"], r["outcome"], r["narrative"], r["steps"]
    if r["symptom_group"]["code"] != group:
        return "이력 증상군이 카드와 다름"
    if o.get("type") != OUTCOME[kind]:
        return "이력 결과 유형이 정답 유형과 다름"
    abnormal = [s for s in steps if s["kind"] == "check" and s.get("result") == "이상"]
    if kind == "manual_cause":
        code = hidden["code"]
        name = d.m.CAUSES[code][0]
        if o.get("cause_code") != code or o.get("cause_name") != name:
            return "이력 원인 코드 · 이름이 정의와 다름"
        if d.checks(group, code, True)[0]["id"] not in [s["section"] for s in abnormal]:
            return "확정 점검 절 단계가 '이상'이 아님"
        if {s["section"] for s in steps if s["kind"] == "action"} != {d.m.CAUSE_ACTION[code]}:
            return "조치 단계 절이 정의의 원인 조치와 다름"
        if name not in nar or any(s["name"] not in nar or s.get("note", "") not in nar for s in abnormal):
            return "서술에 원인 이름 · '이상' 점검 이름 · 소견이 없음"
        return None
    if kind == "none":
        if abnormal:
            return "이상 없음 이력에 '이상' 점검이 있음"
        if not any(s["kind"] == "close" and s["section"] == "6.2" for s in steps) or "감시로 마감" not in nar:
            return "6.2 감시 마감 단계 · 서술이 없음"
        return None
    if not any(s["kind"] == "call" and s.get("call_type") == "숙련자 인계" for s in steps) or "숙련자 인계" not in nar:
        return "숙련자 인계 단계 · 서술이 없음"
    return None


def check_card(d: Definition, inp, card: dict, row: dict) -> list[dict]:
    cid, group, hidden = card["card_id"], inp.groups[card["card_id"]], card["hidden_cause"]

    def bad(k, loc, why):
        return {"card_id": cid, "check": k, "locator": loc, "why": why}

    kind = hidden.get("type")
    # K1 카드 ↔ 원인 표
    if kind not in OUTCOME or group not in d.chapter:
        return [bad("K1", None, "숨은 원인 유형 · 증상군이 정의 밖")]
    if kind == "manual_cause":
        code = hidden.get("code")
        if code not in d.m.CAUSES:
            return [bad("K1", None, "원인 코드가 정의 원인 표에 없음")]
        if code.split("-")[0] != group or len(d.checks(group, code, True)) != 1:
            return [bad("K1", None, "원인 코드가 카드 증상군 장의 원인이 아니거나 확정 점검 절이 하나가 아님")]
    out = []
    # K2 매뉴얼 정답 줄 ↔ 정의 글
    want, used = d.expected_manual(group, hidden), set()
    for e in (e for e in row["evidence"] if e["store"] == "manual"):
        loc = e["locator"]
        text = inp.manual.cut(loc) if loc.get("section") in inp.manual.span else None
        hit = next(
            (i for i, (rule, sid, w) in enumerate(want) if i not in used and rule == e["rule"] and sid == loc.get("section") and text is not None and line_matches(w, text)),
            None,
        )
        if hit is None:
            out.append(bad("K2", loc, "정답 줄이 정의의 원인 · 점검 글과 맞지 않음"))
        else:
            used.add(hit)
    out += [bad("K2", {"section": sid}, f"정의에 있는 {rule} 줄이 정답에 없음") for i, (rule, sid, _) in enumerate(want) if i not in used]
    # K3 이력 ↔ 원인 · 점검 · 서술
    hist = {r["record_id"]: r for r in inp.history}
    gold_ids = [e["locator"]["record_id"] for e in row["evidence"] if e["store"] == "history"]
    for rid in gold_ids:
        why = "이력에 없는 record_id" if rid not in hist else history_problem(d, hist[rid], group, hidden)
        if why:
            out.append(bad("K3", {"record_id": rid}, why))
    want_ids = {loc["record_id"] for _, loc in mg.history_evidence(inp.history, group, hidden)}
    out += [bad("K3", {"record_id": rid}, "규칙에 맞는 이력이 정답에 없음") for rid in sorted(want_ids - set(gold_ids))]
    return out


def run(root: Path, sname: str) -> dict:
    inp = mg.Inputs(root, sname)
    d = Definition(load_definition(root))
    gold_path = inp.dir / "gold.jsonl"
    rows = {r["card_id"]: r for r in (json.loads(line) for line in gold_path.read_text(encoding="utf-8").splitlines() if line.strip())}
    if [c["card_id"] for c in inp.cards] != list(rows):
        raise mg.GoldError("gold.jsonl 카드 차례가 cards.jsonl과 다름")
    mism, per = [], {}
    for card in inp.cards:
        m = check_card(d, inp, card, rows[card["card_id"]])
        mism += m
        per[card["card_id"]] = {"elements": len(rows[card["card_id"]]["evidence"]), "mismatches": len(m)}
    h = lambda p: mg.sha256(p.read_bytes())
    return {
        "artifact": "retriever_gold_check",
        "set": sname,
        "contract": "change-contract-v7 CC-05",
        "tool_sha256": h(Path(__file__)),
        "basis": {"manual_spec_sha256": h(root / "scripts/manual_spec.py"), "gold_sha256": h(gold_path), **{k + "_sha256": v for k, v in inp.hashes().items()}},
        "summary": {"cards": len(inp.cards), "elements": sum(p["elements"] for p in per.values()), "mismatches": len(mism),
                    "by_check": {k: sum(x["check"] == k for x in mism) for k in CHECKS}},
        "mismatches": mism,
        "cards": per,
    }


def emit_result(root: Path, report: dict) -> dict:
    """표본 20장 → 확인 화면 결과 모양(CC-03): rule_ok = K1 · remove = K2 · K3 어긋난 auto 원소 · add = 규칙에 맞는데 빠진 이력."""
    vdir = root / "eval/cards/val"
    sample_path = vdir / "human-sample.json"
    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    gold = {r["card_id"]: r for r in (json.loads(line) for line in (vdir / "gold.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())}
    cards = {}
    for cid in sample["cards"]:
        ms = [m for m in report["mismatches"] if m["card_id"] == cid]
        have = [e["locator"] for e in gold[cid]["evidence"]]
        remove = [
            {"store": "history", "record_id": m["locator"]["record_id"]}
            if "record_id" in m["locator"]
            else {"store": "manual", "section": m["locator"]["section"], "char_start": m["locator"]["char_start"]}
            for m in ms
            if m["check"] in ("K2", "K3") and m["locator"] in have
        ]
        add = [{"store": "history", "record_id": m["locator"]["record_id"]} for m in ms if m["check"] == "K3" and m["why"] == "규칙에 맞는 이력이 정답에 없음"]
        cards[cid] = {"reviewed": True, "rule_ok": not any(m["check"] == "K1" for m in ms), "remove": remove, "add": add,
                      "memo": " / ".join(f"{m['check']} {m['why']}" for m in ms)}
    return {"reviewer": "auto-consistency", "saved_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "sample_sha256": mg.sha256(sample_path.read_bytes()), "gold_sha256": sample["gold_sha256"], "check_tool_sha256": report["tool_sha256"], "cards": cards}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--set", required=True, choices=("val", "test"))
    ap.add_argument("--root", type=Path, default=HERE.parent, help="저장소 뿌리(시험용 사본)")
    ap.add_argument("--out", type=Path, help="보고 json(test는 건수 · sha만)")
    ap.add_argument("--emit-result", type=Path, help="val 표본 20장 결과 json(apply-human 입력)")
    args = ap.parse_args()
    try:
        if args.emit_result and args.set != "val":
            raise mg.GoldError("결과 내기는 val에서만(약속 F)")
        rep = run(args.root, args.set)
        if args.set == "test":  # 숨김: 내용 칸을 빼고 건수만
            rep = {k: v for k, v in rep.items() if k not in ("mismatches", "cards")}
        data = (json.dumps(rep, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
        if args.out:
            mg.write_atomic(args.out, data)
        s = rep["summary"]
        print(f"[{args.set}] 자동 일관성 검사 — 카드 {s['cards']} · 원소 {s['elements']} · 어긋남 {s['mismatches']} ({' · '.join(f'{k} {v}' for k, v in s['by_check'].items())}) · 보고 sha256 {mg.sha256(data)}")
        if args.set == "val":
            for m in rep["mismatches"]:
                print(f"  {m['card_id']} {m['check']} {json.dumps(m['locator'], ensure_ascii=False)} — {m['why']}")
            if args.emit_result:
                res = emit_result(args.root, rep)
                mg.write_atomic(args.emit_result, (json.dumps(res, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
                print(f"[val] 결과 {len(res['cards'])}장 → {args.emit_result}")
        return 1 if s["mismatches"] else 0
    except mg.GoldError as e:
        print(f"[{args.set}] 오류: {e if args.set == 'val' else '규칙 · 입력 어긋남(test는 내용 숨김)'}", file=sys.stderr)
        return 2
    except Exception as e:  # test는 예상 밖 오류도 내용 · 소스 줄 없이(정답 숨김)
        if args.set == "val":
            raise
        print(f"[{args.set}] 예상 밖 오류({type(e).__name__}) — test는 내용 숨김", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
