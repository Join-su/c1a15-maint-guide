"""eval/make_gold.py 시험(EV-003 ES-01 · VC-G1 ~ G5) — 실제 이력 · 매뉴얼 사본 + 가상 카드(EC-X..)만 쓴다.

실제 val · test 카드는 읽지 않는다(test 숨김 · 시험 출력에 정답 내용 0).
실행: python3 -m unittest discover -s eval/tests -v
"""
import importlib.util
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("make_gold", ROOT / "eval/make_gold.py")
mg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mg)

CAUSES = {"CL": ["CL-1", "CL-2", "CL-3", "CL-4"], "PW": ["PW-1", "PW-2", "PW-3"], "TW": ["TW-1", "TW-2", "TW-3", "TW-4"], "LD": ["LD-1", "LD-2", "LD-3"]}
NAMES = {"CL": "온도 차 저하", "PW": "출력 이탈", "TW": "공구 마모 경고", "LD": "토크 과부하"}


def fake_cards():
    """정답 유형 22 · 5 · 3(README와 같은 몫)의 가상 카드 30장."""
    plan = [(g, {"type": "manual_cause", "code": c}) for g, cs in CAUSES.items() for c in cs]  # 14
    plan += [(g, {"type": "manual_cause", "code": c}) for g, c in [("CL", "CL-1"), ("PW", "PW-1"), ("PW", "PW-2"), ("LD", "LD-2"), ("TW", "TW-1"), ("CL", "CL-2"), ("PW", "PW-3"), ("LD", "LD-3")]]  # 22
    plan += [(g, {"type": "none"}) for g in ("CL", "PW", "TW", "LD", "PW")]
    plan += [(g, {"type": "out_of_graph"}) for g in ("CL", "TW", "LD")]
    cards = [{"card_id": f"EC-X{n:02d}", "hidden_cause": h} for n, (_, h) in enumerate(plan, 1)]
    alarm = {"sensor": "가상", "value": 1, "unit": "-", "boundary": 0, "direction": "경계 위"}
    inputs = [{"card_id": f"EC-X{n:02d}", "symptom_group": {"code": g, "name": NAMES[g]}, "alarm": alarm, "sensor_snapshot": {"torque_nm": 1}} for n, (g, _) in enumerate(plan, 1)]
    return cards, inputs


class GoldTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for rel in ("data/history/maintenance_history.jsonl", "data/manuals/MG-MM.md", "data/manuals/manual_sections.json"):
            (self.tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, self.tmp / rel)
        d = self.tmp / "eval/cards/val"
        d.mkdir(parents=True)
        cards, inputs = fake_cards()
        (d / "cards.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cards), encoding="utf-8")
        (d / "card_inputs.json").write_text(json.dumps(inputs, ensure_ascii=False), encoding="utf-8")
        self.dir = d

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def rows(self):
        return [json.loads(line) for line in (self.dir / "gold.jsonl").read_text(encoding="utf-8").splitlines()]

    def test_build_check_and_relocate(self):  # VC-G1 · VC-G3
        self.assertEqual(mg.cmd_build(self.tmp, "val"), 0)
        self.assertEqual(mg.cmd_check(self.tmp, "val"), 0)
        inp = mg.Inputs(self.tmp, "val")
        rows = self.rows()
        self.assertEqual(len(rows), 30)
        for row in rows:
            self.assertEqual(row["source"], "auto")
            stores = [e["store"] for e in row["evidence"]]
            self.assertEqual(stores, sorted(stores, key=lambda s: s != "history"))  # 이력 → 매뉴얼
            for e in row["evidence"]:
                if e["store"] == "manual":
                    cut = inp.manual.md[e["locator"]["char_start"] : e["locator"]["char_end"]]
                    self.assertTrue(cut and "\n" not in cut)
                else:
                    self.assertEqual(set(e["locator"]), {"record_id"})

    def test_rules(self):  # CC-02
        mg.cmd_build(self.tmp, "val")
        inp = mg.Inputs(self.tmp, "val")
        rows = {r["card_id"]: r for r in self.rows()}
        hist = {r["record_id"]: r for r in inp.history}
        cards, inputs = fake_cards()
        for card, info in zip(cards, inputs):
            row, hidden, group = rows[card["card_id"]], card["hidden_cause"], info["symptom_group"]["code"]
            for e in row["evidence"]:
                if e["store"] == "history":
                    r = hist[e["locator"]["record_id"]]
                    self.assertEqual(r["symptom_group"]["code"], group)
                    if hidden["type"] == "manual_cause":
                        self.assertEqual((e["rule"], r["outcome"].get("cause_code")), ("H-1", hidden["code"]))
            manual = [(e["rule"], e["locator"]["section"]) for e in row["evidence"] if e["store"] == "manual"]
            if hidden["type"] == "manual_cause":
                self.assertEqual([m for m in manual if m[0] == "M-1"][0][1][-2:], ".1")
                self.assertEqual(len([m for m in manual if m[0] == "M-2"]), 2)
                self.assertEqual(any(m[0] == "M-3" for m in manual), hidden["code"] in ("PW-2", "LD-2"))
            elif hidden["type"] == "none":
                self.assertEqual(sorted(s for _, s in manual)[-1], "6.2")
            else:
                self.assertIn("1.4", [s for _, s in manual])

    def test_same_hash_twice(self):  # VC-G2
        mg.cmd_build(self.tmp, "val")
        first = (self.dir / "gold.jsonl").read_bytes()
        mg.cmd_build(self.tmp, "val")
        self.assertEqual(first, (self.dir / "gold.jsonl").read_bytes())

    def assert_refuses(self):
        with self.assertRaises(mg.GoldError):
            mg.cmd_build(self.tmp, "val")
        self.assertFalse((self.dir / "gold.jsonl").exists())

    def test_fault_line_removed(self):  # VC-G5 규칙 줄 0번
        md = self.tmp / "data/manuals/MG-MM.md"
        text = md.read_text(encoding="utf-8")
        md.write_text(text.replace("**이상 없음 기준**", "이상 없음 기준", 1), encoding="utf-8")
        sec = self.tmp / "data/manuals/manual_sections.json"
        secs = json.loads(sec.read_text(encoding="utf-8"))
        for s in secs:
            if s.get("text") and "**이상 없음 기준**" in s["text"]:
                s["text"] = s["text"].replace("**이상 없음 기준**", "이상 없음 기준", 1)
                break
        sec.write_text(json.dumps(secs, ensure_ascii=False), encoding="utf-8")
        self.assert_refuses()

    def test_fault_line_doubled(self):  # VC-G5 규칙 줄 2번
        sec = self.tmp / "data/manuals/manual_sections.json"
        md = self.tmp / "data/manuals/MG-MM.md"
        secs = json.loads(sec.read_text(encoding="utf-8"))
        s = next(s for s in secs if s["id"] == "1.4")
        line = next(l for l in s["text"].splitlines() if l.startswith("- 숙련자 인계:"))
        new = s["text"] + "\n" + line
        md.write_text(md.read_text(encoding="utf-8").replace(s["text"], new, 1), encoding="utf-8")
        s["text"] = new
        sec.write_text(json.dumps(secs, ensure_ascii=False), encoding="utf-8")
        self.assert_refuses()

    def test_fault_unknown_code(self):  # VC-G5 정답 code가 매뉴얼에 없음 · 증상군과 원인 장 다름
        for bad in ({"type": "manual_cause", "code": "CL-9"}, {"type": "manual_cause", "code": "PW-1"}, {"type": "other"}):
            cards = [json.loads(l) for l in (self.dir / "cards.jsonl").read_text(encoding="utf-8").splitlines()]
            cards[0]["hidden_cause"] = bad  # 첫 카드 증상군 = CL
            (self.dir / "cards.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cards), encoding="utf-8")
            self.assert_refuses()

    def test_check_detects_tamper(self):  # 만든 뒤 바뀌면 check 실패
        mg.cmd_build(self.tmp, "val")
        rows = self.rows()
        rows[0]["evidence"] = rows[0]["evidence"][1:]
        (self.dir / "gold.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        self.assertEqual(mg.cmd_check(self.tmp, "val"), 1)

    def test_history_rules_complete(self):  # 규칙을 도구 밖에서 다시 셈(H-1 ~ H-3 빠짐없음, review R-2)
        mg.cmd_build(self.tmp, "val")
        hist = [json.loads(l) for l in (self.tmp / "data/history/maintenance_history.jsonl").read_text(encoding="utf-8").splitlines()]
        rows = {r["card_id"]: r for r in self.rows()}
        cards, inputs = fake_cards()
        for card, info in zip(cards, inputs):
            g, h = info["symptom_group"]["code"], card["hidden_cause"]
            want = {
                r["record_id"]
                for r in hist
                if r["symptom_group"]["code"] == g
                and (
                    (h["type"] == "manual_cause" and r["outcome"]["type"] == "원인 확정" and r["outcome"].get("cause_code") == h["code"])
                    or (h["type"] == "none" and r["outcome"]["type"] == "이상 없음·감시")
                    or (h["type"] == "out_of_graph" and r["outcome"]["type"] == "원인 미상·숙련자 인계")
                )
            }
            got = {e["locator"]["record_id"] for e in rows[card["card_id"]]["evidence"] if e["store"] == "history"}
            self.assertEqual(got, want)

    def test_check_detects_shape_change(self):  # review R-3: 순서 · 중복 · 칸 — meta sha까지 맞춰도 잡음
        mg.cmd_build(self.tmp, "val")
        for bad in ("reverse", "dup", "extra"):
            rows = self.rows()
            ev = rows[0]["evidence"]
            rows[0]["evidence"] = ev[::-1] if bad == "reverse" else ev + ev[:1] if bad == "dup" else ev
            if bad == "extra":
                rows[0]["cause"] = "x"
            data = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode("utf-8")
            (self.dir / "gold.jsonl").write_bytes(data)
            meta = json.loads((self.dir / "gold-meta.json").read_text(encoding="utf-8"))
            meta["gold_sha256"] = mg.sha256(data)
            (self.dir / "gold-meta.json").write_text(json.dumps(meta), encoding="utf-8")
            self.assertEqual(mg.cmd_check(self.tmp, "val"), 1, bad)

    def test_test_set_output_hides_answers(self):  # VC-G4 · review R-4: test 묶음 출력(정상 · 규칙 오류 · 예상 밖 오류)에 정답 내용 0
        import subprocess
        tdir = self.tmp / "eval/cards/test"
        shutil.copytree(self.dir, tdir)
        cards = [json.loads(l) for l in (tdir / "cards.jsonl").read_text(encoding="utf-8").splitlines()]
        inputs = json.loads((tdir / "card_inputs.json").read_text(encoding="utf-8"))
        for c, i in zip(cards, inputs):
            c["card_id"] = i["card_id"] = c["card_id"].replace("EC-X", "EC-T")
        (tdir / "card_inputs.json").write_text(json.dumps(inputs, ensure_ascii=False), encoding="utf-8")

        def run(*args):
            (tdir / "cards.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cards), encoding="utf-8")
            p = subprocess.run([sys.executable, "-I", str(ROOT / "eval/make_gold.py"), *args, "--set", "test", "--root", str(self.tmp)], capture_output=True, text=True)
            return p.returncode, p.stdout + p.stderr

        outs = [run("build"), run("check")]
        cards[0]["hidden_cause"] = {"type": "manual_cause", "code": "CL-9"}
        outs.append(run("build"))
        cards[0]["hidden_cause"] = {"type": "manual_cause"}  # code 없음 → 예상 밖 오류 길
        outs.append(run("build"))
        self.assertEqual([c for c, _ in outs], [0, 0, 2, 2])
        for _, out in outs:
            self.assertIsNone(re.search(r"H-\d{4}|EC-T|section|Traceback|(CL|PW|TW|LD)-\d", out), out)

    def test_sample_rules(self):  # VC-G6: 반드시 넣기 · 몫 · seed 재현 · val만
        mg.cmd_build(self.tmp, "val")
        self.assertEqual(mg.cmd_sample(self.tmp, "val"), 0)
        first = (self.dir / "human-sample.json").read_bytes()
        mg.cmd_sample(self.tmp, "val")
        self.assertEqual(first, (self.dir / "human-sample.json").read_bytes())
        s = json.loads(first)
        cards, inputs = fake_cards()
        by = {c["card_id"]: c for c in cards}
        grp = {i["card_id"]: i["symptom_group"]["code"] for i in inputs}
        pick = set(s["cards"])
        self.assertEqual(len(pick), 20)
        self.assertTrue({i for i, c in by.items() if c["hidden_cause"].get("code") in ("PW-2", "LD-2")} <= pick)
        for t in ("none", "out_of_graph"):
            self.assertGreaterEqual(sum(by[i]["hidden_cause"]["type"] == t for i in pick), 2)
        counts = {g: sum(grp[i] == g for i in pick) for g in ("CL", "PW", "TW", "LD")}
        self.assertEqual(counts, s["adjusted_quota"])
        self.assertEqual(sum(s["adjusted_quota"].values()), 20)
        with self.assertRaises(mg.GoldError):
            mg.cmd_sample(self.tmp, "test")

    def test_quota_overflow(self):  # CC-03 2: 넘친 증상군은 두고 여유 큰 증상군부터 줄임
        cards, inputs = fake_cards()
        grp = {i["card_id"]: i["symptom_group"]["code"] for i in inputs}
        rows = [{"card_id": c["card_id"], "evidence": [{"store": "history"}] * 1} for c in cards]  # 모두 이력 1건 → 30장 반드시 넣기
        with self.assertRaises(mg.GoldError):
            mg.pick_sample(cards, grp, rows)
        rows = [{"card_id": c["card_id"], "evidence": [{"store": "history"}] * (1 if grp[c["card_id"]] == "LD" else 9)} for c in cards]
        s = mg.pick_sample(cards, grp, rows)  # 가상 LD 7장 모두 반드시 → LD 7, 몫 3에서 넘친 4만큼 다른 증상군 줄임
        n_ld = sum(g == "LD" for g in grp.values())
        self.assertEqual((n_ld, s["adjusted_quota"]["LD"]), (7, 7))
        self.assertEqual(sum(s["adjusted_quota"].values()), 20)

    def test_review_html_self_contained(self):  # VC-G7 일부: 외부 자원 0 · 표본 20장 · val만
        mg.cmd_build(self.tmp, "val")
        mg.cmd_sample(self.tmp, "val")
        out = self.tmp / "review.html"
        self.assertEqual(mg.cmd_review_html(self.tmp, "val", out), 0)
        html = out.read_text(encoding="utf-8")
        self.assertNotIn("http", html)
        self.assertNotIn("/*__DATA__*/null", html)
        self.assertEqual(html.count('"card_id"'), 20)

    def test_tool_reads_no_answer_sources(self):  # VC-G4
        src = (ROOT / "eval/make_gold.py").read_text(encoding="utf-8")
        for word in ("generation", "card_udi_map", "ai4i2020"):
            self.assertNotIn(word, src.replace("generation/ · 카드 ↔ 원본 행 대응 · 원본 CSV는 읽지 않는다", ""))


if __name__ == "__main__":
    unittest.main()
