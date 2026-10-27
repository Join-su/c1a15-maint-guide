"""eval/field_gold.py 시험(EV-004 FG-01 · VF-1 · VF-2 · VF-3 · VF-5) — 실제 이력 · 매뉴얼 사본 + 가상 카드(EC-X..)로 만든 가짜 체크 기록.

실제 val · test 카드 · 운영 기록은 읽지 않는다.
실행: python3 -m unittest discover -s eval/tests -v
"""
import importlib.util
import json
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
fg = load("field_gold", "eval/field_gold.py")
tg = load("test_make_gold", "eval/tests/test_make_gold.py")
OUTCOME = {"manual_cause": "원인 확정", "none": "이상 없음·감시", "out_of_graph": "원인 미상·숙련자 인계"}


def record(n, group, hidden, **over):
    """가짜 체크 기록(c1a15.check-record.v1 칸 중 규칙이 읽는 것만)."""
    rec = {"schema": "c1a15.check-record.v1", "record_key": f"CR-{n:06d}",
           "session": {"pack_session_id": f"S-A{n}", "symptom_group": group, "scenario_id": None},
           "runs": {"deployment_id": "c1a15@test", "start": f"run_start_{n}", "report": f"run_report_{n}"},
           "lead": {"decision": "approve", "edits": [], "cause_text_changed": False, "rejects": []},
           "outcome": {"type": OUTCOME[hidden["type"]], "cause_code": hidden.get("code"), "restart": "within" if hidden["type"] == "manual_cause" else None},
           "steps": [], "signals": []}
    for k, v in over.items():
        rec[k] = {**rec[k], **v} if isinstance(v, dict) and isinstance(rec.get(k), dict) else v
    return rec


class FieldGoldTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        hist = [json.loads(l) for l in (ROOT / "data/history/maintenance_history.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        cls.corpus = ROOT / "data/history/maintenance_history.jsonl"
        cls.hrel = cls.tmp / "ir-history-test"
        cls.hrel.mkdir()
        (cls.hrel / "chunks.jsonl").write_text("".join(json.dumps(
            {"id": f"{r['record_id']}#0", "locator": {"doc": r["record_id"], "record_id": r["record_id"], "char_start": 0, "char_end": len(r["narrative"])},
             "metadata": {"symptom_group": r["symptom_group"]["code"], "cause": r["outcome"].get("cause_code"), "source": "generated", "evidence_type": "history"},
             "text": r["narrative"]}, ensure_ascii=False) + "\n" for r in hist), encoding="utf-8")
        secs = json.loads((ROOT / "data/manuals/manual_sections.json").read_text(encoding="utf-8"))
        cls.mrel = cls.tmp / "ir-manuals-test"
        cls.mrel.mkdir()
        (cls.mrel / "chunks.jsonl").write_text("".join(json.dumps(
            {"id": f"MG-MM#{s['id']}", "locator": {"doc": "MG-MM", "section": s["id"], "char_start": 0, "char_end": len(s["text"])},
             "metadata": {"evidence_type": "manual"}, "text": s["text"]}, ensure_ascii=False) + "\n" for s in secs if s.get("text")), encoding="utf-8")
        # 카드 정답(비교 기준): 가상 카드로 make_gold build
        cls.groot = cls.tmp / "goldroot"
        for rel in ("data/history/maintenance_history.jsonl", "data/manuals/MG-MM.md", "data/manuals/manual_sections.json"):
            (cls.groot / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, cls.groot / rel)
        d = cls.groot / "eval/cards/val"
        d.mkdir(parents=True)
        cls.cards, cls.inputs = tg.fake_cards()
        (d / "cards.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cls.cards), encoding="utf-8")
        (d / "card_inputs.json").write_text(json.dumps(cls.inputs, ensure_ascii=False), encoding="utf-8")
        mg.cmd_build(cls.groot, "val")
        cls.card_gold = {r["card_id"]: r for r in map(json.loads, (d / "gold.jsonl").read_text(encoding="utf-8").splitlines())}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def run_fg(self, rec, hrel=None, mrel=None, root=ROOT):
        return fg.field_gold(rec, hrel or self.hrel, mrel or self.mrel, self.corpus, root)

    def test_vf1_cards_same_as_card_gold(self):   # VF-1 카드 흉내 = 카드 정답(유형 셋 모두)
        for n, (card, info) in enumerate(zip(self.cards, self.inputs), 1):
            res = self.run_fg(record(n, info["symptom_group"]["code"], card["hidden_cause"]))
            self.assertTrue(res["gate"]["ok"], card["card_id"])
            gold = self.card_gold[card["card_id"]]["evidence"]
            want_h = [{"record_id": e["locator"]["record_id"]} for e in gold if e["store"] == "history"]
            want_m = [(e["locator"], e["rule"]) for e in gold if e["store"] == "manual"]
            nodes = res["expected"]["nodes"]
            got_h = [e["locator"] for e in nodes.get("retrieve_history", [{"evidence": []}])[0]["evidence"]]
            got_m = [(e["locator"], e["rule"]) for e in nodes["retrieve_manual"][0]["evidence"]]
            self.assertEqual((got_h, got_m), (want_h, want_m), card["card_id"])
            self.assertTrue(all(e["store"] == "manuals" for e in nodes["retrieve_manual"][0]["evidence"]))
            self.assertEqual(res["source"], "field")

    def test_vf2_gates(self):   # VF-2 문 G1 ~ G5 — 하나씩 어기면 정답 없음
        h = {"type": "manual_cause", "code": "CL-1"}
        bad = [record(1, "CL", h, lead={"decision": None}), record(1, "CL", h, eval_mode=True), record(1, "CL", h, runs={"start": None}),
               record(1, "CL", h, outcome={"type": "기타"}), record(1, "CL", h, outcome={"restart": "outside"}), record(1, "CL", h, outcome={"restart": None})]
        for n, rec in enumerate(bad, 1):
            res = self.run_fg(rec)
            self.assertFalse(res["gate"]["ok"], n)
            self.assertIsNone(res["expected"])
            self.assertEqual(len(res["gate"]["failed"]), 1, res["gate"]["failed"])
        self.assertTrue(self.run_fg(record(1, "CL", {"type": "none"}))["gate"]["ok"])   # 이상 없음은 재가동 칸을 보지 않음

    def test_vf3_edit_self_and_negatives(self):   # VF-3 파트장 수정 뒤 원인 · 자기 승인 이력 빼기 · 헛걸음
        rec = record(42, "CL", {"type": "manual_cause", "code": "CL-1"}, lead={"decision": "edit", "cause_text_changed": True},
                     steps=[{"kind": "check", "section": "4.5", "result": "정상"}, {"kind": "check", "section": "4.3", "result": "이상"}])
        hrel = self.tmp / "ir-history-self"
        shutil.copytree(self.hrel, hrel)
        with open(hrel / "chunks.jsonl", "a", encoding="utf-8") as f:
            for rid, cause in (("R-0042", "CL-1"), ("R-0043", "CL-1")):
                f.write(json.dumps({"id": f"{rid}#0", "locator": {"doc": rid, "record_id": rid, "char_start": 0, "char_end": 5},
                                    "metadata": {"symptom_group": "CL", "cause": cause, "source": "approved_report", "evidence_type": "history"}, "text": "x"}) + "\n")
        res = self.run_fg(rec, hrel=hrel)
        ids = [e["locator"]["record_id"] for e in res["expected"]["nodes"]["retrieve_history"][0]["evidence"]]
        self.assertIn("R-0043", ids)        # 다른 승인 이력은 같은 원인이면 정답
        self.assertNotIn("R-0042", ids)     # 자기 기록은 뺌
        self.assertEqual(res["provenance"]["self_excluded"], "R-0042")
        self.assertEqual(res["negatives"], [{"section": "4.5"}])   # 정상으로 끝난 점검 중 정답 절이 아닌 것
        self.assertEqual(res["provenance"]["approval_mode"], "edit")
        self.assertEqual(res["confirmed"], {"type": "manual_cause", "code": "CL-1"})

    def test_vf5_unknown_outcome_r(self):   # VF-5 결과를 모르는 승인 이력(cause null)은 이상 없음 · 원인 미상 정답에서 빠짐
        hrel = self.tmp / "ir-history-unknown"
        shutil.copytree(self.hrel, hrel)
        with open(hrel / "chunks.jsonl", "a", encoding="utf-8") as f:
            for rid, cause, ot in (("R-0100", None, None), ("R-0101", None, "이상 없음·감시")):
                md = {"symptom_group": "PW", "cause": cause, "source": "approved_report", "evidence_type": "history", **({"outcome_type": ot} if ot else {})}
                f.write(json.dumps({"id": f"{rid}#0", "locator": {"doc": rid, "record_id": rid, "char_start": 0, "char_end": 1}, "metadata": md, "text": "x"}) + "\n")
        res = self.run_fg(record(7, "PW", {"type": "none"}), hrel=hrel)
        ids = [e["locator"]["record_id"] for e in res["expected"]["nodes"]["retrieve_history"][0]["evidence"]]
        self.assertNotIn("R-0100", ids)
        self.assertIn("R-0101", ids)        # outcome_type 칸이 오면(GAP-F4 뒤) 그 유형대로
        self.assertEqual(res["provenance"]["excluded_unknown_outcome"], 1)

    def test_release_must_match_manual_definition(self):   # 판이 다르면 멈춤(규칙을 다시 쓰지 않음)
        mrel = self.tmp / "ir-manuals-other"
        mrel.mkdir()
        rows = [json.loads(l) for l in (self.mrel / "chunks.jsonl").read_text(encoding="utf-8").splitlines()]
        rows[0]["text"] += " 덧"
        (mrel / "chunks.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        with self.assertRaises(fg.FieldError):
            self.run_fg(record(1, "CL", {"type": "manual_cause", "code": "CL-1"}), mrel=mrel)

    def test_cli_and_no_card_files(self):   # CLI · 카드 파일을 열지 않음
        rec = self.tmp / "rec.json"
        rec.write_text(json.dumps(record(5, "CL", {"type": "manual_cause", "code": "CL-1"}), ensure_ascii=False), encoding="utf-8")
        out = self.tmp / "out.json"
        p = subprocess.run([sys.executable, "-I", "-B", str(ROOT / "eval/field_gold.py"), "--record", str(rec), "--history-release", str(self.hrel),
                            "--manual-release", str(self.mrel), "--out", str(out)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("문 통과", p.stdout)
        self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["schema"], "c1a15.field-gold.v1")
        src = (ROOT / "eval/field_gold.py").read_text(encoding="utf-8")
        for word in ("eval/cards", "cards.jsonl", "card_udi_map", "generation/"):
            self.assertNotIn(word, src)


if __name__ == "__main__":
    unittest.main()
