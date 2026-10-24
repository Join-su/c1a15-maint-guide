#!/usr/bin/env python3
"""리트리버 평가 정답 후보(EV-003 · 약속 F): 카드마다 정답 근거의 원문 위치를 규칙으로 뽑는다.

- 정답 = 원문 위치(D-250 (2)): 이력 `{record_id}` · 매뉴얼 `{doc, section, char_start, char_end}` — 글자 위치는 **섹션 처음부터**
  (질문 001-05 · change-contract-v5 CC-01): 섹션 = manual_sections.json 그 절 text(`### x.y` 줄 첫 글자 = 0), text[char_start:char_end] = 정답 줄.
  한 절이 여러 조각이어도 조각마다 0부터가 아니라 절 첫 글자부터. 절 본문은 MG-MM.md 안에 차례대로 있어야 한다(앱 ingest.manual_chunks와 같은 확인). 청크 번호가 아니라서 청크 크기 · 오버랩이 바뀌어도 같은 정답으로 채점된다.
- 규칙(change-contract-v3 CC-02): manual_cause → H-1 · M-1 · M-2 · M-3 / none → H-2 · M-4 / out_of_graph → H-3 · M-5.
  센서 거리 · 알람 방향 · 리트리버 결과는 쓰지 않는다(바퀴 손잡이와 무관하게).
- 읽는 것: eval/cards/<set>/cards.jsonl(hidden_cause) · card_inputs.json(증상군) · data/history · data/manuals.
  generation/ · 카드 ↔ 원본 행 대응 · 원본 CSV는 읽지 않는다.
- 만드는 것: eval/cards/<set>/gold.jsonl(auto, 만든 뒤 고치지 않음) · gold-meta.json. 규칙이 하나라도 어긋나면 쓰지 않고 끝난다.
- test는 숨김(약속 F): 화면에는 줄 수 · sha256만 낸다.

- 사람 표본(CC-03, val만): sample → eval/cards/val/human-sample.json · review-html → 확인 화면 한 장(저장소 밖 경로에 씀).

실행: python3 eval/make_gold.py build --set val|test   ·   python3 eval/make_gold.py check --set val|test
      python3 eval/make_gold.py sample --set val   ·   python3 eval/make_gold.py review-html --set val --out <파일.html>
"""
import argparse
import hashlib
import json
import os
import random
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

MANUAL_DOC = "MG-MM"
TYPES = ("manual_cause", "none", "out_of_graph")
OUTCOME = {"none": "이상 없음·감시", "out_of_graph": "원인 미상·숙련자 인계"}
HISTORY_RULE = {"manual_cause": "H-1", "none": "H-2", "out_of_graph": "H-3"}
SEED = "2026-gold-human"
QUOTA = {"CL": 5, "PW": 7, "TW": 5, "LD": 3}
GROUP_ORDER = ("CL", "PW", "TW", "LD")
SCREENING = ("PW-2", "LD-2")
TEMPLATE = Path(__file__).resolve().parent / "gold_review_template.html"
NOTE = "줄 원소의 store · rule은 F 채점 주인(llmops 리드) 확인 중 — 바뀔 수 있음(답장 001-03 3). locator 모양은 약속 F 그대로"


class GoldError(Exception):
    pass


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical_lines(rows: list[dict]) -> bytes:
    return "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows).encode("utf-8")


class Manual:
    """절 범위 = 절 본문을 차례대로 찾은 자리(ingest.manual_chunks와 같음, 본문 없는 조치 절은 뺌)."""

    def __init__(self, md: str, sections: list[dict]):
        self.md, self.sections, self.span = md, sections, {}
        pos = 0
        for s in sections:
            text = s.get("text")
            if not text:
                continue
            start = md.find(text, pos)
            if start < 0:
                raise GoldError(f"매뉴얼 원문에서 절 본문을 찾지 못함: {s['id']}")
            pos = start + len(text)
            self.span[s["id"]] = (start, pos)

    def line(self, sid: str, pattern: str) -> dict:
        """절 범위 안에서 pattern에 맞는 줄이 정확히 한 번이어야 한다."""
        if sid not in self.span:
            raise GoldError(f"매뉴얼 절 없음: {sid}")
        a, b = self.span[sid]
        hits = [m for m in re.finditer(r"^.*$", self.md[a:b], re.M) if re.search(pattern, m.group(0))]
        if len(hits) != 1:
            raise GoldError(f"규칙 줄이 {len(hits)}번 찾힘: 절 {sid} · {pattern}")
        m = hits[0]
        return {"doc": MANUAL_DOC, "section": sid, "char_start": m.start(), "char_end": m.end()}

    def doc_pos(self, loc: dict) -> int:
        """정렬용: 문서 안 자리(절 시작 + 섹션 기준 위치)."""
        return self.span[loc["section"]][0] + loc["char_start"]

    def cut(self, loc: dict) -> str:
        a, _ = self.span[loc["section"]]
        return self.md[a + loc["char_start"] : a + loc["char_end"]]

    def chapter(self, group: str) -> str:
        ids = [s["id"] for s in self.sections if s.get("group") == group and s.get("kind") == "info" and s["id"].endswith(".1")]
        if len(ids) != 1:
            raise GoldError(f"증상군 개요 절을 하나로 못 정함: {group}")
        return ids[0]

    def checks(self, group: str, code: str, confirms: bool) -> list[str]:
        return [
            s["id"]
            for s in self.sections
            if s.get("kind") == "check" and s.get("group") == group and s.get("cause") == code and bool(s.get("confirms")) == confirms
        ]


def manual_evidence(man: Manual, group: str, hidden: dict) -> list[tuple[str, dict]]:
    x1 = man.chapter(group)
    kind = hidden.get("type")
    if kind == "manual_cause":
        code = hidden.get("code")
        if not any(s.get("cause") == code for s in man.sections):
            raise GoldError(f"정답 원인이 매뉴얼에 없음: {code}")
        confirm = man.checks(group, code, True)
        if len(confirm) != 1:
            raise GoldError(f"확정형 점검 절이 하나가 아님(증상군 · 원인 장 확인): {group} {code}")
        out = [("M-1", man.line(x1, r"^\| " + re.escape(code) + r" \|"))]
        out += [("M-2", man.line(confirm[0], r"^\*\*권한 등급\*\*.*\*\*연결 원인\*\*")), ("M-2", man.line(confirm[0], r"^\*\*판정 기준\*\*"))]
        out += [("M-3", man.line(sid, r"^\*\*판정 기준\*\*")) for sid in man.checks(group, code, False)]
        return out
    if kind == "none":
        return [("M-4", man.line(x1, r"^\*\*이상 없음 기준\*\*")), ("M-4", man.line("6.2", r"^1\. "))]
    if kind == "out_of_graph":
        return [("M-5", man.line(x1, r"^\*\*호출\*\*")), ("M-5", man.line("1.4", r"^- 숙련자 인계:"))]
    raise GoldError(f"정답 유형이 셋 밖: {kind}")


def history_evidence(history: list[dict], group: str, hidden: dict) -> list[tuple[str, dict]]:
    kind = hidden["type"]
    if kind == "manual_cause":
        hit = [r for r in history if r["outcome"].get("type") == "원인 확정" and r["outcome"].get("cause_code") == hidden["code"]]
    else:
        hit = [r for r in history if r["outcome"].get("type") == OUTCOME[kind]]
    return [(HISTORY_RULE[kind], {"record_id": r["record_id"]}) for r in hit if r["symptom_group"]["code"] == group]


class Inputs:
    def __init__(self, root: Path, sname: str):
        self.root, self.sname = root, sname
        self.dir = root / "eval/cards" / sname
        self.paths = {
            "cards": self.dir / "cards.jsonl",
            "card_inputs": self.dir / "card_inputs.json",
            "history": root / "data/history/maintenance_history.jsonl",
            "manual_md": root / "data/manuals/MG-MM.md",
            "manual_sections": root / "data/manuals/manual_sections.json",
        }
        self.cards = [json.loads(line) for line in self.paths["cards"].read_text(encoding="utf-8").splitlines() if line.strip()]
        self.groups = {c["card_id"]: c["symptom_group"]["code"] for c in json.loads(self.paths["card_inputs"].read_text(encoding="utf-8"))}
        self.history = [json.loads(line) for line in self.paths["history"].read_text(encoding="utf-8").splitlines() if line.strip()]
        self.manual = Manual(self.paths["manual_md"].read_text(encoding="utf-8"), json.loads(self.paths["manual_sections"].read_text(encoding="utf-8")))

    def hashes(self) -> dict:
        return {k: sha256(p.read_bytes()) for k, p in self.paths.items()}


def build_rows(inp: Inputs) -> list[dict]:
    if [c["card_id"] for c in inp.cards] != list(inp.groups):
        raise GoldError("cards.jsonl과 card_inputs.json의 카드 순서가 다름")
    rows = []
    for card in inp.cards:
        group, hidden = inp.groups[card["card_id"]], card["hidden_cause"]
        manual = manual_evidence(inp.manual, group, hidden)
        hist = sorted(history_evidence(inp.history, group, hidden), key=lambda e: e[1]["record_id"])
        seen, evidence = set(), []
        for store, items in (("history", hist), ("manual", sorted(manual, key=lambda e: inp.manual.doc_pos(e[1])))):
            for rule, loc in items:
                key = json.dumps(loc, sort_keys=True)
                if key not in seen:
                    seen.add(key)
                    evidence.append({"store": store, "locator": loc, "rule": rule})
        rows.append({"card_id": card["card_id"], "set": inp.sname, "evidence": evidence, "source": "auto"})
    return rows


def verify(inp: Inputs, rows: list[dict]) -> list[str]:
    """VC-G1 · VC-G3: auto 원소를 원문으로 되짚고 규칙 · 건수를 다시 본다. 오류 글에 정답 내용은 넣지 않는다(test 숨김)."""
    errors = []
    by_id = {r["record_id"]: r for r in inp.history}
    expected = {c["card_id"]: c for c in inp.cards}
    if [r["card_id"] for r in rows] != [c["card_id"] for c in inp.cards] or len(rows) != 30:
        errors.append("gold 줄 수 · 카드 순서가 카드 묶음과 다름")
    types = Counter(c["hidden_cause"]["type"] for c in inp.cards)
    if types != Counter({"manual_cause": 22, "none": 5, "out_of_graph": 3}):
        errors.append("정답 유형 건수가 22 · 5 · 3이 아님")
    for n, row in enumerate(rows, 1):
        if set(row) != {"card_id", "set", "evidence", "source"} or row.get("set") != inp.sname:
            errors.append(f"{n}번째 줄: 칸 · set 값이 CC-01과 다름")
        keys = [json.dumps(e.get("locator"), sort_keys=True) for e in row.get("evidence", [])]
        order = [(e.get("store") != "history", e["locator"].get("record_id", "") if e.get("store") == "history" else (inp.manual.doc_pos(e["locator"]) if e["locator"].get("section") in inp.manual.span else -1)) for e in row.get("evidence", [])]
        if len(keys) != len(set(keys)) or order != sorted(order) or any(set(e) != {"store", "locator", "rule"} for e in row.get("evidence", [])):
            errors.append(f"{n}번째 줄: 원소 중복 · 순서 · 칸이 CC-01과 다름")
        card = expected.get(row["card_id"])
        if card is None or row["source"] != "auto" or not row["evidence"]:
            errors.append(f"{n}번째 줄: 카드 · source · 정답 1건 이상 중 어긋남")
            continue
        group, hidden = inp.groups[row["card_id"]], card["hidden_cause"]
        try:
            want = {json.dumps(loc, sort_keys=True): rule for rule, loc in manual_evidence(inp.manual, group, hidden)}
        except GoldError:
            errors.append(f"{n}번째 줄: 규칙 줄을 다시 찾지 못함")
            continue
        want_hist = {e[1]["record_id"] for e in history_evidence(inp.history, group, hidden)}
        got_hist = {e["locator"]["record_id"] for e in row["evidence"] if e["store"] == "history"}
        if got_hist != want_hist or any(by_id[r]["symptom_group"]["code"] != group for r in got_hist if r in by_id) or not got_hist <= set(by_id):
            errors.append(f"{n}번째 줄: 이력 정답이 규칙 · 증상군과 다름")
        got_man = {}
        for e in row["evidence"]:
            if e["store"] != "manual":
                continue
            loc = e["locator"]
            a, b = inp.manual.span.get(loc["section"], (0, -1))
            if not (0 <= loc["char_start"] < loc["char_end"] <= b - a) or "\n" in inp.manual.cut(loc) or loc["doc"] != MANUAL_DOC:
                errors.append(f"{n}번째 줄: 매뉴얼 위치가 절 범위 · 한 줄을 벗어남")
            got_man[json.dumps(loc, sort_keys=True)] = e["rule"]
        if got_man != want:
            errors.append(f"{n}번째 줄: 매뉴얼 정답이 규칙과 다름")
    return errors


def write_atomic(path: Path, data: bytes) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def cmd_build(root: Path, sname: str) -> int:
    inp = Inputs(root, sname)
    rows = build_rows(inp)
    errors = verify(inp, rows)
    if errors:
        raise GoldError("검사 실패 — 파일을 쓰지 않음: " + " / ".join(errors if sname == "val" else [f"{len(errors)}건"]))
    data = canonical_lines(rows)
    rules = Counter(e["rule"] for r in rows for e in r["evidence"])
    meta = {
        "artifact": "retriever_gold_meta",
        "set": sname,
        "evolution": "EV-003-retriever-gold",
        "tool_sha256": sha256(Path(__file__).read_bytes()),
        "inputs_sha256": inp.hashes(),
        "gold_sha256": sha256(data),
        "cards": len(rows),
        "evidence_by_rule": dict(sorted(rules.items())),
        "cards_without_history": [r["card_id"] for r in rows if not any(e["store"] == "history" for e in r["evidence"])],
        "contract": "약속 F(records/contract-locked-2026-10-24.md) · change-contract-v3 CC-01 · CC-02",
        "note": NOTE,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    write_atomic(inp.dir / "gold.jsonl", data)
    write_atomic(inp.dir / "gold-meta.json", (json.dumps(meta, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    if sname == "val":
        print(f"[val] gold {len(rows)}줄 · 규칙별 {dict(sorted(rules.items()))} · 이력 정답 없음 {len(meta['cards_without_history'])}장 · sha256 {meta['gold_sha256']}")
    else:
        print(f"[{sname}] gold {len(rows)}줄 · sha256 {meta['gold_sha256']}")
    return 0


def cmd_check(root: Path, sname: str) -> int:
    inp = Inputs(root, sname)
    gold = inp.dir / "gold.jsonl"
    rows = [json.loads(line) for line in gold.read_text(encoding="utf-8").splitlines() if line.strip()]
    errors = verify(inp, rows)
    meta = json.loads((inp.dir / "gold-meta.json").read_text(encoding="utf-8"))
    if meta.get("gold_sha256") != sha256(gold.read_bytes()):
        errors.append("gold-meta의 sha256이 gold.jsonl과 다름")
    if errors:
        print(f"[{sname}] 실패 {len(errors)}건" + (": " + " / ".join(errors) if sname == "val" else ""))
        return 1
    print(f"[{sname}] 통과: 원문 위치 되짚기 · 규칙 · 증상군 · 건수 · sha256")
    return 0


def pick_sample(cards: list[dict], groups: dict, rows: list[dict]) -> dict:
    """CC-03 고르는 차례: 반드시 넣기 → 증상군 몫(넘친 만큼 여유 큰 쪽부터 1씩 줄임) → seed 표본."""
    rng = random.Random(SEED)
    order = [c["card_id"] for c in cards]
    by_id = {c["card_id"]: c for c in cards}
    hist_n = {r["card_id"]: sum(e["store"] == "history" for e in r["evidence"]) for r in rows}
    must: dict[str, list[str]] = {
        "screening_cause": [i for i in order if by_id[i]["hidden_cause"].get("code") in SCREENING],
        "history_le_3": [i for i in order if hist_n[i] <= 3],
    }
    picked = set(must["screening_cause"]) | set(must["history_le_3"])
    for reason, test in (
        ("none", lambda c: c["hidden_cause"]["type"] == "none"),
        ("out_of_graph", lambda c: c["hidden_cause"]["type"] == "out_of_graph"),
        ("ambiguous", lambda c: c.get("memo_style") == "ambiguous"),
    ):
        pool = [i for i in order if test(by_id[i])]
        need = max(0, min(2, len(pool)) - len([i for i in pool if i in picked]))
        add = sorted(rng.sample([i for i in pool if i not in picked], need), key=order.index)
        must[reason] = add
        picked |= set(add)
    if len(picked) > 20:
        raise GoldError(f"반드시 넣기만으로 {len(picked)}장 — 20을 넘음")
    must_g = {g: sum(groups[i] == g for i in picked) for g in GROUP_ORDER}
    quota = {g: max(QUOTA[g], must_g[g]) for g in GROUP_ORDER}
    while sum(quota.values()) > 20:
        slack = {g: quota[g] - must_g[g] for g in GROUP_ORDER}
        g = max(GROUP_ORDER, key=lambda k: (slack[k], -GROUP_ORDER.index(k)))
        if slack[g] <= 0:
            raise GoldError("몫을 줄일 증상군이 없음")
        quota[g] -= 1
    for g in GROUP_ORDER:
        pool = [i for i in order if groups[i] == g and i not in picked]
        need = quota[g] - must_g[g]
        if need > len(pool):
            raise GoldError(f"증상군 {g} 카드가 몫보다 적음")
        picked |= set(rng.sample(pool, need))
    return {
        "artifact": "retriever_gold_human_sample",
        "set": "val",
        "seed": SEED,
        "quota": QUOTA,
        "adjusted_quota": quota,
        "must_include": must,
        "cards": [i for i in order if i in picked],
        "rule": "change-contract-v3 CC-03",
    }


def cmd_sample(root: Path, sname: str) -> int:
    if sname != "val":
        raise GoldError("사람 표본은 val에서만(약속 F)")
    inp = Inputs(root, sname)
    gold = inp.dir / "gold.jsonl"
    rows = [json.loads(line) for line in gold.read_text(encoding="utf-8").splitlines() if line.strip()]
    if verify(inp, rows):
        raise GoldError("gold.jsonl 검사 실패 — 먼저 build · check")
    sample = pick_sample(inp.cards, inp.groups, rows)
    sample["gold_sha256"] = sha256(gold.read_bytes())
    write_atomic(inp.dir / "human-sample.json", (json.dumps(sample, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    print(f"[val] 표본 {len(sample['cards'])}장 · 증상군 {sample['adjusted_quota']} · sha256 {sha256((inp.dir / 'human-sample.json').read_bytes())}")
    return 0


def review_data(inp: Inputs) -> dict:
    """확인 화면에 넣을 자료 — 표본 20장만. 비교 기록 · 보일 이력 3건은 카드마다 seed(센서 거리 안 씀)."""
    sample_path = inp.dir / "human-sample.json"
    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    rows = {json.loads(line)["card_id"]: json.loads(line) for line in (inp.dir / "gold.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()}
    if sample.get("gold_sha256") != sha256((inp.dir / "gold.jsonl").read_bytes()):
        raise GoldError("human-sample.json이 지금 gold.jsonl과 짝이 아님")
    raw = {c["card_id"]: c for c in json.loads(inp.paths["card_inputs"].read_text(encoding="utf-8"))}
    cards = {c["card_id"]: c for c in inp.cards}
    hist = {r["record_id"]: r for r in inp.history}
    man = inp.manual
    titles = {s["id"]: s.get("title", "") for s in man.sections}
    out = []
    for cid in sample["cards"]:
        card, info, row, group = cards[cid], raw[cid], rows[cid], inp.groups[cid]
        rng = random.Random(f"{SEED}:{cid}")
        gold_hist = [e["locator"]["record_id"] for e in row["evidence"] if e["store"] == "history"]
        shown = sorted(rng.sample(gold_hist, min(3, len(gold_hist))))
        others = sorted(r["record_id"] for r in inp.history if r["symptom_group"]["code"] == group and r["record_id"] not in set(gold_hist))
        compare = sorted(rng.sample(others, min(2, len(others))))
        chapter = man.chapter(group).split(".")[0]
        sections = [
            {"id": sid, "title": titles.get(sid, ""), "char_start": 0, "char_end": b - a}
            for sid, (a, b) in man.span.items()
            if sid.split(".")[0] in (chapter, "1", "6")
        ]
        out.append(
            {
                "card_id": cid,
                "group": group,
                "group_name": info["symptom_group"]["name"],
                "alarm": info["alarm"],
                "sensors": info["sensor_snapshot"],
                "hidden": card["hidden_cause"],
                "memo_style": card.get("memo_style"),
                "history_rule": next((e["rule"] for e in row["evidence"] if e["store"] == "history"), HISTORY_RULE[card["hidden_cause"]["type"]]),
                "history_count": len(gold_hist),
                "history_shown": [{"record_id": i, "narrative": hist[i]["narrative"], "outcome": hist[i]["outcome"]} for i in shown],
                "compare": [{"record_id": i, "narrative": hist[i]["narrative"], "outcome": hist[i]["outcome"]} for i in compare],
                "manual": [
                    {"rule": e["rule"], **e["locator"], "title": titles.get(e["locator"]["section"], ""), "text": man.cut(e["locator"])}
                    for e in row["evidence"]
                    if e["store"] == "manual"
                ],
                "manual_sections": sections,
                "group_record_ids": sorted(r["record_id"] for r in inp.history if r["symptom_group"]["code"] == group),
            }
        )
    return {"sample_sha256": sha256(sample_path.read_bytes()), "gold_sha256": sample["gold_sha256"], "cards": out}


def cmd_review_html(root: Path, sname: str, out: Path) -> int:
    if sname != "val":
        raise GoldError("확인 화면은 val에서만(약속 F)")
    data = review_data(Inputs(root, sname))
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/null", blob)
    write_atomic(out, html.encode("utf-8"))
    print(f"[val] 확인 화면 {len(data['cards'])}장 → {out} · sample sha256 {data['sample_sha256']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=("build", "check", "sample", "review-html"))
    ap.add_argument("--set", required=True, choices=("val", "test"))
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="저장소 뿌리(시험용 사본)")
    ap.add_argument("--out", type=Path, help="review-html이 쓸 파일")
    args = ap.parse_args()
    try:
        if args.command == "review-html":
            if args.out is None:
                raise GoldError("--out 필요")
            return cmd_review_html(args.root, args.set, args.out)
        return {"build": cmd_build, "check": cmd_check, "sample": cmd_sample}[args.command](args.root, args.set)
    except GoldError as e:
        print(f"[{args.set}] 오류: {e if args.set == 'val' else '규칙 · 입력 어긋남(test는 내용 숨김)'}", file=sys.stderr)
        return 2
    except Exception as e:  # test는 예상 밖 오류도 내용 · 소스 줄 없이(정답 숨김)
        if args.set == "val":
            raise
        print(f"[{args.set}] 예상 밖 오류({type(e).__name__}) — test는 내용 숨김", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
