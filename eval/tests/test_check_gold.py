"""eval/check_gold.py 시험(EV-003 ES-04 · VC-G9 · G10 · G11) — 실제 이력 · 매뉴얼 · 생성 정의 사본 + 가상 카드(EC-X..)만 쓴다.

실제 val · test 카드는 읽지 않는다. 잘못 주입은 사본에서만 하고, 주입마다 기대 check id · card_id가 보고에 나와야 한다.
실행: python3 -m unittest discover -s eval/tests -v
"""
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


mg = load("make_gold", "eval/make_gold.py")
cg = load("check_gold", "eval/check_gold.py")
tg = load("test_make_gold", "eval/tests/test_make_gold.py")   # 가상 카드 30장(같은 몫)
CARD = {"CL-1": "EC-X01", "PW-2": "EC-X06", "LD-2": "EC-X13", "none_CL": "EC-X23", "oog_CL": "EC-X28"}

AUDIT = r"""
import os, runpy, sys
log = open(sys.argv[1], "w", encoding="utf-8")
seen = []
def hook(ev, args):
    if ev == "open":
        seen.append((str(args[0]), str(args[1]), args[2] if len(args) > 2 else 0))
sys.addaudithook(hook)
sys.argv = sys.argv[2:]
try:
    runpy.run_path(sys.argv[0], run_name="__main__")
except SystemExit:
    pass
finally:
    for p, mode, flags in seen:
        log.write(f"{p}\t{mode}\t{flags}\n")
    log.close()
"""


class CheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Path(tempfile.mkdtemp())
        for rel in ("data/history/maintenance_history.jsonl", "data/manuals/MG-MM.md", "data/manuals/manual_sections.json", "scripts/manual_spec.py"):
            (cls.base / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, cls.base / rel)
        d = cls.base / "eval/cards/val"
        d.mkdir(parents=True)
        cards, inputs = tg.fake_cards()
        (d / "cards.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cards), encoding="utf-8")
        (d / "card_inputs.json").write_text(json.dumps(inputs, ensure_ascii=False), encoding="utf-8")
        mg.cmd_build(cls.base, "val")
        mg.cmd_sample(cls.base, "val")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base)

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(self.base, self.tmp, dirs_exist_ok=True)
        self.dir = self.tmp / "eval/cards/val"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    # ── 사본 고치는 도구
    def rows(self):
        return {r["card_id"]: r for r in map(json.loads, (self.dir / "gold.jsonl").read_text(encoding="utf-8").splitlines())}

    def write_rows(self, rows):
        (self.dir / "gold.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows.values()), encoding="utf-8")

    def edit_cards(self, cid, hidden):
        cards = [json.loads(l) for l in (self.dir / "cards.jsonl").read_text(encoding="utf-8").splitlines()]
        next(c for c in cards if c["card_id"] == cid)["hidden_cause"] = hidden
        (self.dir / "cards.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cards), encoding="utf-8")

    def edit_manual(self, sid, old, new):
        """절 본문 글을 같은 길이로 바꿈(md · sections 둘 다 — 뒤 위치가 밀리지 않게)."""
        self.assertEqual(len(old), len(new))
        secs = json.loads((self.tmp / "data/manuals/manual_sections.json").read_text(encoding="utf-8"))
        s = next(s for s in secs if s["id"] == sid)
        self.assertEqual(s["text"].count(old), 1)
        md = (self.tmp / "data/manuals/MG-MM.md").read_text(encoding="utf-8")
        (self.tmp / "data/manuals/MG-MM.md").write_text(md.replace(s["text"], s["text"].replace(old, new), 1), encoding="utf-8")
        s["text"] = s["text"].replace(old, new)
        (self.tmp / "data/manuals/manual_sections.json").write_text(json.dumps(secs, ensure_ascii=False), encoding="utf-8")

    def edit_history(self, rid, fn):
        p = self.tmp / "data/history/maintenance_history.jsonl"
        hs = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        fn(next(h for h in hs if h["record_id"] == rid))
        p.write_text("".join(json.dumps(h, ensure_ascii=False) + "\n" for h in hs), encoding="utf-8")

    def gold_history(self, cid):
        return [e["locator"]["record_id"] for e in self.rows()[cid]["evidence"] if e["store"] == "history"]

    def found(self):
        return {(m["card_id"], m["check"]) for m in cg.run(self.tmp, "val")["mismatches"]}

    # ── VC-G9
    def test_clean_is_zero_and_stable(self):
        a, b = cg.run(self.tmp, "val"), cg.run(self.tmp, "val")
        self.assertEqual(a["summary"]["mismatches"], 0)
        self.assertEqual(a, b)

    def test_k1(self):
        for cid, hidden in ((CARD["CL-1"], {"type": "other"}), (CARD["CL-1"], {"type": "manual_cause", "code": "CL-9"}), (CARD["CL-1"], {"type": "manual_cause", "code": "PW-1"})):
            with self.subTest(hidden=hidden):
                self.setUp()
                self.edit_cards(cid, hidden)
                self.assertIn((cid, "K1"), self.found())
        self.setUp()   # 정의 사본에서 CL-2 확정 절을 CL-1로 → CL-1 확정 절 2개
        spec = self.tmp / "scripts/manual_spec.py"
        src = spec.read_text(encoding="utf-8")
        old = '"minutes": 10,\n     "cause": "CL-2", "confirms": True,'
        self.assertEqual(src.count(old), 1)
        spec.write_text(src.replace(old, old.replace("CL-2", "CL-1")), encoding="utf-8")
        self.assertIn((CARD["CL-1"], "K1"), self.found())

    def test_k2_lines(self):
        cases = [
            ("M-1 줄", CARD["CL-1"], lambda: self.edit_manual("4.1", "| CL-1 | 냉각 필터 막힘 |", "| CL-1 | 냉각 필터 막혀 |")),
            ("M-2 머리 줄", CARD["CL-1"], lambda: self.edit_manual("4.3", "CL-1 냉각 필터 막힘(확정)", "CL-1 냉각 필터 막힘(선별)")),
            ("M-2 판정 줄", CARD["CL-1"], lambda: self.edit_manual("4.3", "필터 표면의 절반", "필터 표면의 전부")),
            ("M-3 판정 줄", CARD["PW-2"], lambda: self.edit_manual("3.5", "2회 이상이면", "3회 이상이면")),
            ("M-4 x.1 줄", CARD["none_CL"], lambda: self.edit_manual("4.1", "**이상 없음 기준**", "**이상 없는 기준**")),
            ("M-4 6.2 줄", CARD["none_CL"], lambda: self.edit_manual("6.2", "1. 빠르게", "1. 느리게")),
            ("M-5 x.1 줄", CARD["oog_CL"], lambda: self.edit_manual("4.1", "**호출**", "**요청**")),
            ("M-5 1.4 줄", CARD["oog_CL"], lambda: self.edit_manual("1.4", "주간 정비 엔지니어", "야간 정비 엔지니어")),
        ]
        for name, cid, inject in cases:
            with self.subTest(name):
                self.setUp()
                inject()
                self.assertIn((cid, "K2"), self.found())

    def test_k2_missing_and_extra(self):
        rows = self.rows()
        cid = CARD["CL-1"]
        rows[cid]["evidence"] = [e for e in rows[cid]["evidence"] if e["rule"] != "M-1"]
        self.write_rows(rows)
        ms = cg.run(self.tmp, "val")["mismatches"]
        self.assertTrue(any(m["card_id"] == cid and m["check"] == "K2" and "정답에 없음" in m["why"] for m in ms))
        self.setUp()
        rows = self.rows()
        inp = mg.Inputs(self.tmp, "val")
        rows[cid]["evidence"].append({"store": "manual", "locator": inp.manual.line("4.1", r"^\| CL-2 \|"), "rule": "M-1"})
        self.write_rows(rows)
        ms = cg.run(self.tmp, "val")["mismatches"]
        self.assertTrue(any(m["card_id"] == cid and m["check"] == "K2" and m["locator"].get("section") == "4.1" and "맞지 않음" in m["why"] for m in ms))

    def test_k3_manual_cause(self):
        cid = CARD["CL-1"]
        rid = self.gold_history(cid)[0]
        other = next(r["record_id"] for r in mg.Inputs(self.tmp, "val").history if r["symptom_group"]["code"] == "PW")

        def step(kind, fn):
            return lambda h: [fn(s) for s in h["steps"] if s["kind"] == kind and (kind != "check" or s.get("result") == "이상")]

        cases = [
            ("원인 이름", lambda: self.edit_history(rid, lambda h: h["outcome"].update(cause_name="냉각 팬 열화"))),
            ("확정 점검 정상", lambda: self.edit_history(rid, step("check", lambda s: s.update(result="정상")))),
            ("조치 절", lambda: self.edit_history(rid, step("action", lambda s: s.update(section="4.4.2")))),
            ("서술 원인 이름", lambda: self.edit_history(rid, lambda h: h.update(narrative=h["narrative"].replace("냉각 필터 막힘", "")))),
            ("서술 점검 이름", lambda: self.edit_history(rid, lambda h: h.update(narrative=h["narrative"].replace("흡기 필터 육안 점검", "")))),
            ("다른 증상군 이력", lambda: self.write_rows({**self.rows(), cid: {**self.rows()[cid], "evidence": [{"store": "history", "locator": {"record_id": other}, "rule": "H-1"}] + self.rows()[cid]["evidence"]}})),
        ]
        for name, inject in cases:
            with self.subTest(name):
                self.setUp()
                inject()
                self.assertIn((cid, "K3"), self.found())
        self.setUp()   # 규칙에 맞는 이력이 정답에서 빠짐
        rows = self.rows()
        rows[cid]["evidence"] = [e for e in rows[cid]["evidence"] if e["locator"] != {"record_id": rid}]
        self.write_rows(rows)
        ms = cg.run(self.tmp, "val")["mismatches"]
        self.assertIn({"card_id": cid, "check": "K3", "locator": {"record_id": rid}, "why": "규칙에 맞는 이력이 정답에 없음"}, ms)

    def test_k3_none_and_out_of_graph(self):
        nid, oid = CARD["none_CL"], CARD["oog_CL"]
        rn, ro = self.gold_history(nid)[0], self.gold_history(oid)[0]
        cases = [
            (nid, lambda: self.edit_history(rn, lambda h: next(s for s in h["steps"] if s["kind"] == "check").update(result="이상"))),
            (nid, lambda: self.edit_history(rn, lambda h: h.update(steps=[s for s in h["steps"] if s["kind"] != "close"]))),
            (nid, lambda: self.edit_history(rn, lambda h: h.update(narrative=h["narrative"].replace("감시로 마감", "")))),
            (oid, lambda: self.edit_history(ro, lambda h: h.update(steps=[s for s in h["steps"] if s.get("call_type") != "숙련자 인계"]))),
            (oid, lambda: self.edit_history(ro, lambda h: h.update(narrative=h["narrative"].replace("숙련자 인계", "")))),
        ]
        for n, (cid, inject) in enumerate(cases):
            with self.subTest(n):
                self.setUp()
                inject()
                self.assertIn((cid, "K3"), self.found())

    # ── VC-G10
    def test_emit_matches_report_and_apply(self):
        sample = json.loads((self.dir / "human-sample.json").read_text(encoding="utf-8"))["cards"]
        a, b = sample[0], sample[1]
        ra = self.gold_history(a)[0]
        self.edit_history(ra, lambda h: h.update(narrative=h["narrative"].replace(h["outcome"].get("cause_name") or "감시로 마감", "")))
        hidden = {c["card_id"]: c["hidden_cause"] for c in map(json.loads, (self.dir / "cards.jsonl").read_text(encoding="utf-8").splitlines())}
        self.edit_cards(b, {"type": "manual_cause", "code": "XX-1"})
        out, res = self.tmp / "rep.json", self.tmp / "res.json"
        p = subprocess.run([sys.executable, "-I", str(ROOT / "eval/check_gold.py"), "--set", "val", "--root", str(self.tmp), "--out", str(out), "--emit-result", str(res)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 1, p.stderr)
        rep, r = json.loads(out.read_text(encoding="utf-8")), json.loads(res.read_text(encoding="utf-8"))
        self.assertEqual((r["reviewer"], list(r["cards"]), r["gold_sha256"]), ("auto-consistency", sample, mg.sha256((self.dir / "gold.jsonl").read_bytes())))
        for cid, c in r["cards"].items():
            ms = [m for m in rep["mismatches"] if m["card_id"] == cid]
            self.assertEqual(c["rule_ok"], not any(m["check"] == "K1" for m in ms))
            want = [m["locator"] for m in ms if m["check"] in ("K2", "K3") and m["why"] != "규칙에 맞는 이력이 정답에 없음"]
            got = [{"record_id": x["record_id"]} if x["store"] == "history" else x for x in c["remove"]]
            self.assertEqual(len(got), len(want), cid)
            self.assertTrue(c["reviewed"])
        self.assertEqual(r["cards"][a]["remove"], [{"store": "history", "record_id": ra}])
        self.assertFalse(r["cards"][b]["rule_ok"])
        self.edit_cards(b, hidden[b])   # apply-human은 카드 원인을 다시 읽지 않지만 사본을 원래대로
        self.assertEqual(mg.cmd_apply_human(self.tmp, "val", res), 0)
        gh = {x["card_id"]: x for x in map(json.loads, (self.dir / "gold-human.jsonl").read_text(encoding="utf-8").splitlines())}
        self.assertNotIn({"record_id": ra}, [e["locator"] for e in gh[a]["evidence"]])
        self.assertFalse(any(e["store"] == "history" for e in gh[b]["evidence"]))

    def test_test_set_hidden(self):
        tdir = self.tmp / "eval/cards/test"
        shutil.copytree(self.dir, tdir)
        for f in ("cards.jsonl", "card_inputs.json", "gold.jsonl"):
            (tdir / f).write_text((tdir / f).read_text(encoding="utf-8").replace("EC-X", "EC-T"), encoding="utf-8")

        def run(*extra):
            p = subprocess.run([sys.executable, "-I", str(ROOT / "eval/check_gold.py"), "--set", "test", "--root", str(self.tmp), *extra], capture_output=True, text=True)
            return p.returncode, p.stdout + p.stderr

        outs = [run("--out", str(self.tmp / "t.json"))]
        rep = json.loads((self.tmp / "t.json").read_text(encoding="utf-8"))
        self.assertEqual(set(rep), {"artifact", "set", "contract", "tool_sha256", "basis", "summary"})
        rid = next(e["locator"]["record_id"] for e in json.loads((tdir / "gold.jsonl").read_text(encoding="utf-8").splitlines()[0])["evidence"] if e["store"] == "history")
        self.edit_history(rid, lambda h: h["outcome"].update(cause_name="x"))
        outs.append(run())
        cards = (tdir / "cards.jsonl").read_text(encoding="utf-8").splitlines()
        (tdir / "cards.jsonl").write_text("\n".join(cards[1:]) + "\n", encoding="utf-8")
        outs.append(run())
        outs.append(run("--emit-result", str(self.tmp / "r.json")))
        self.assertEqual([c for c, _ in outs], [0, 1, 2, 2])
        for _, out in outs:
            self.assertIsNone(re.search(r"H-\d{4}|EC-T|section|Traceback|(CL|PW|TW|LD)-\d|record_id", out), out)

    # ── VC-G11
    def test_definition_isolation(self):
        src = (ROOT / "scripts/manual_spec.py").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"\bimport\b|open\(|generation|card_udi_map|ai4i2020", src))
        tool = (ROOT / "eval/check_gold.py").read_text(encoding="utf-8")
        for word in ("generation/", "card_udi_map", "ai4i2020"):
            self.assertNotIn(word, tool.replace("generation/ · 카드 ↔ 원본 행 대응 · 원본 CSV · 망 · LLM은 쓰지 않는다", ""))
        log, hook = self.tmp / "open.log", self.tmp / "hook.py"
        hook.write_text(AUDIT, encoding="utf-8")
        out, res = self.tmp / "o.json", self.tmp / "e.json"
        subprocess.run([sys.executable, "-I", str(hook), str(log), str(ROOT / "eval/check_gold.py"), "--set", "val", "--root", str(self.tmp), "--out", str(out), "--emit-result", str(res)], check=True)
        allowed = {self.tmp / r for r in ("scripts/manual_spec.py", "data/manuals/MG-MM.md", "data/manuals/manual_sections.json", "data/history/maintenance_history.jsonl",
                                           "eval/cards/val/cards.jsonl", "eval/cards/val/card_inputs.json", "eval/cards/val/gold.jsonl", "eval/cards/val/human-sample.json")}
        allowed |= {ROOT / "eval/check_gold.py", ROOT / "eval/make_gold.py"}
        writes = {out, out.with_name(out.name + ".tmp"), res, res.with_name(res.name + ".tmp")}
        stdlib = (Path(sys.base_prefix).resolve(), Path(sys.prefix).resolve())
        reads, wrote = set(), set()
        for line in log.read_text(encoding="utf-8").splitlines():
            path, mode, flags = line.split("\t")
            p = Path(path).resolve() if path and not path.isdigit() else None
            if p is None or any(str(p).startswith(str(s)) for s in stdlib):
                continue
            is_write = any(ch in mode for ch in "wax+") or (flags.isdigit() and int(flags) & 3)
            if "__pycache__" in p.parts and not is_write:
                continue   # 이미 있는 pyc 읽기는 허용 · 쓰기는 잡음(A7 N-2)
            (wrote if is_write else reads).add(p)
        self.assertTrue(reads <= {a.resolve() for a in allowed}, sorted(map(str, reads - {a.resolve() for a in allowed})))
        self.assertTrue(wrote <= {w.resolve() for w in writes}, sorted(map(str, wrote)))
        self.assertTrue(wrote)


if __name__ == "__main__":
    unittest.main()
