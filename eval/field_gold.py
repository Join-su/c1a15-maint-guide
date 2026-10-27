#!/usr/bin/env python3
"""현장 정답 줄(EV-004 FG-01 · FG-02, D-408 · D-412 결정 7): 앱 사람 체크 기록 한 장 → 그 Run이 찾은 벡터 DB 판 기준 정답 줄.

- 입력: 앱 체크 기록 문서(`c1a15.check-record.v1`, c1a15-app EV-006) · 그 Run이 찾은 history · manual release 폴더(chunks.jsonl) ·
  history release의 corpus(생성 이력 전체 기록 — `outcome.type`이 여기만 있음). 망 · DB 0, 파일만 읽음.
- 규칙: 정답 카드와 같은 규칙(EV-003 CC-02 — make_gold의 manual_evidence · history_evidence를 그대로 부름, 두 벌 금지).
  카드의 숨은 원인 자리에 '사람이 확정한 원인'(outcome — 파트장 수정 뒤)을 넣는다.
- 문(G1 ~ G5): 파트장 결정(approve · edit) · 평가 실행 아님 · start Run 있음 · 결과 셋 중 하나 · 원인 확정이면 재가동 within(해결됨).
  하나라도 아니면 정답 줄 없음(개선 신호만).
- history: 그 release 조각 중 같은 증상군 · 같은 결과(· 같은 원인). 생성 이력 H-는 corpus에서 결과를 읽고, 승인 이력 R-는
  metadata `outcome_type`이 있으면 그것, 없으면 cause가 있을 때만 '원인 확정'으로 봄(cause 없는 R-는 이상 없음 · 원인 미상
  정답에서 빠짐 — excluded_unknown_outcome). 그 세션 자신의 승인 이력(R-<보고서 번호>)은 뺌.
- manual: 그 release 절 글이 매뉴얼 정의(data/manuals · scripts/manual_spec.py 판)와 같을 때만 — 다르면 멈춤.
- 출력: LLMOps CHG-266a inline expected 한 줄 `{"nodes": {<node>: [{"evidence": [...]}]}}`(store = Pack 이름) + 머리.
  정답 카드와 섞지 않음 · test 확인 suite에 넣지 않음.

실행: python3 eval/field_gold.py --record <체크 기록.json> --history-release <폴더> --manual-release <폴더>
        [--history-corpus <maintenance_history.jsonl>] [--manual-root <저장소 뿌리>] [--out <파일.json>]
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("make_gold", HERE / "make_gold.py")
mg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mg)

SCHEMA = "c1a15.check-record.v1"
OUT_SCHEMA = "c1a15.field-gold.v1"
TYPE_OF = {"원인 확정": "manual_cause", "이상 없음·감시": "none", "원인 미상·숙련자 인계": "out_of_graph"}
NODES = {"history": ("retrieve_history", "history"), "manual": ("retrieve_manual", "manuals")}   # gold store → (Pack node, Pack store)


class FieldError(Exception):
    pass


def gates(rec: dict) -> list[str]:
    """문 G1 ~ G5 — 어긴 문 이름 목록(비면 통과)."""
    failed = []
    lead, runs, out = rec.get("lead") or {}, rec.get("runs") or {}, rec.get("outcome") or {}
    if lead.get("decision") not in ("approve", "edit"):
        failed.append("G1 파트장 승인 아님")
    if rec.get("eval_mode") or (rec.get("session") or {}).get("eval_mode"):
        failed.append("G2 평가 실행")
    if not runs.get("start"):
        failed.append("G3 start Run 없음")
    if out.get("type") not in TYPE_OF:
        failed.append("G4 결과 종류 밖")
    elif out["type"] == "원인 확정" and (not out.get("cause_code") or out.get("restart") != "within"):
        failed.append("G5 해결 안 됨(재가동 within 아님)")
    return failed


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def history_from_release(release: Path, corpus: Path | None) -> tuple[list[dict], list[str]]:
    """release 조각 → make_gold.history_evidence가 읽는 모양. 결과를 모르는 R-는 type 'unknown'."""
    full = {r["record_id"]: r for r in read_jsonl(corpus)} if corpus else {}
    out, unknown = [], []
    for c in read_jsonl(release / "chunks.jsonl"):
        rid, md = c["locator"]["record_id"], c.get("metadata") or {}
        if rid in full:
            r = full[rid]
            if r["symptom_group"]["code"] != md.get("symptom_group"):
                raise FieldError(f"corpus와 release의 증상군이 다름: {rid}")
            out.append({"record_id": rid, "symptom_group": r["symptom_group"], "outcome": r["outcome"]})
            continue
        if rid.startswith("H-"):
            raise FieldError(f"생성 이력 {rid}가 corpus에 없음 — --history-corpus 확인")
        otype = md.get("outcome_type") or ("원인 확정" if md.get("cause") else None)
        if otype is None:
            unknown.append(rid)
        out.append({"record_id": rid, "symptom_group": {"code": md.get("symptom_group")},
                    "outcome": {"type": otype or "unknown", "cause_code": md.get("cause")}})
    return out, unknown


def manual_for_release(release: Path, root: Path) -> "mg.Manual":
    """매뉴얼 정의(root의 data/manuals)와 release 절 글이 같은지 대조한 뒤 정의를 돌려줌."""
    secs = json.loads((root / "data/manuals/manual_sections.json").read_text(encoding="utf-8"))
    man = mg.Manual((root / "data/manuals/MG-MM.md").read_text(encoding="utf-8"), secs)
    text = {s["id"]: s.get("text") or "" for s in secs}
    for c in read_jsonl(release / "chunks.jsonl"):
        loc = c["locator"]
        if text.get(loc.get("section")) != c.get("text") or loc.get("char_start") != 0:
            raise FieldError(f"release 절 글이 매뉴얼 정의와 다름: {loc.get('section')} — 그 판의 --manual-root가 필요")
    return man


def field_gold(rec: dict, history_release: Path, manual_release: Path, corpus: Path | None, manual_root: Path) -> dict:
    if rec.get("schema") != SCHEMA:
        raise FieldError(f"체크 기록 schema가 {SCHEMA}가 아님")
    key = rec.get("record_key") or ""
    if not key.startswith("CR-") or not key[3:].isdigit():
        raise FieldError("record_key가 CR-<보고서 번호>가 아님")
    out, sess = rec.get("outcome") or {}, rec.get("session") or {}
    head = {"schema": OUT_SCHEMA, "case_id": f"F-{key}", "source": "field", "record_key": key,
            "signals": [s.get("id") for s in rec.get("signals") or []],
            "provenance": {"start_run_id": (rec.get("runs") or {}).get("start"), "report_run_id": (rec.get("runs") or {}).get("report"),
                           "approval_mode": (rec.get("lead") or {}).get("decision"), "history_release": history_release.name,
                           "manual_release": manual_release.name, "rules": "EV-003 CC-02", "tool_sha256": mg.sha256(Path(__file__).read_bytes())}}
    failed = gates(rec)
    if failed:
        return {**head, "gate": {"ok": False, "failed": failed}, "expected": None, "negatives": []}
    group = sess.get("symptom_group") or ((rec.get("field_truth") or {}).get("query") or {}).get("symptom_group")
    if group not in ("TW", "PW", "CL", "LD"):
        raise FieldError("증상군을 알 수 없음")
    hidden = {"type": TYPE_OF[out["type"]]}
    if hidden["type"] == "manual_cause":
        hidden["code"] = out["cause_code"]
    man = manual_for_release(manual_release, manual_root)
    history, unknown = history_from_release(history_release, corpus)
    own = f"R-{int(key[3:]):04d}"   # 이 보고서로 생긴 승인 이력(lead.history_record와 같은 셈) — 그 Run 뒤에 들어온 기록
    hist = sorted((loc["record_id"], rule) for rule, loc in mg.history_evidence(history, group, hidden) if loc["record_id"] != own)
    manual = sorted(mg.manual_evidence(man, group, hidden), key=lambda e: man.doc_pos(e[1]))
    ev = {"history": [{"store": NODES["history"][1], "locator": {"record_id": rid}, "rule": rule} for rid, rule in hist],
          "manual": [{"store": NODES["manual"][1], "locator": loc, "rule": rule} for rule, loc in manual]}
    gold_sections = {e["locator"]["section"] for e in ev["manual"]}
    negatives = sorted({s["section"] for s in rec.get("steps") or [] if s.get("kind") == "check" and s.get("result") == "정상"
                        and not s.get("void") and s.get("section") not in gold_sections})
    nodes = {NODES[k][0]: [{"evidence": v}] for k, v in ev.items() if v}
    empty = [NODES[k][0] for k, v in ev.items() if not v]
    unknown_same_group = [rid for rid in unknown if next(r for r in history if r["record_id"] == rid)["symptom_group"]["code"] == group and rid != own]
    head["provenance"].update({"excluded_unknown_outcome": len(unknown_same_group) if hidden["type"] != "manual_cause" else 0,
                               "self_excluded": own if any(r["record_id"] == own for r in history) else None, "empty_store": empty})
    return {**head, "gate": {"ok": True, "failed": []}, "confirmed": hidden, "expected": {"nodes": nodes}, "negatives": [{"section": s} for s in negatives]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--record", type=Path, required=True)
    ap.add_argument("--history-release", type=Path, required=True)
    ap.add_argument("--manual-release", type=Path, required=True)
    ap.add_argument("--history-corpus", type=Path, default=HERE.parent / "data/history/maintenance_history.jsonl")
    ap.add_argument("--manual-root", type=Path, default=HERE.parent, help="매뉴얼 정의 판의 저장소 뿌리(data/manuals)")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    try:
        res = field_gold(json.loads(a.record.read_text(encoding="utf-8")), a.history_release, a.manual_release, a.history_corpus, a.manual_root)
    except (FieldError, mg.GoldError) as e:
        print(f"[현장 정답] 오류: {e}", file=sys.stderr)
        return 2
    data = (json.dumps(res, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    if a.out:
        mg.write_atomic(a.out, data)
    n = {k: len(v[0]["evidence"]) for k, v in (res["expected"] or {}).get("nodes", {}).items()}
    print(f"[현장 정답] {res['case_id']} · 문 {'통과' if res['gate']['ok'] else '막힘 ' + ' · '.join(res['gate']['failed'])} · 원소 {n} · sha256 {hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
