#!/usr/bin/env python3
"""ingest 도구(Pack 밖, EV-001 CH-05): 적재 자료(data/)에서 이력 · 매뉴얼 data release를 DB 없이 다시 만들어 판 ID · hash · 조각 수를 낸다.

앱 적재기(python -m c1a15.loader)와 R12가 쓰는 같은 라이브러리(server/src/c1a15/ingest)를 부른다 — 같은 입력이면 같은 판(VC-08).
이 판의 임베딩은 가짜(외부 호출 0). 원문 위치(locator)는 검색 평가 정답 근거와 같은 모양(ES-05 recall@k).
실행: cd server && uv run --frozen python ../tools/ingest/build.py [--data ../data] [--out 파일.json]   (server 환경 — 라이브러리가 pgvector · sqlalchemy 모델을 씀)
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "server" / "src"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data"))
    ap.add_argument("--out")
    a = ap.parse_args()
    from c1a15 import ingest
    from c1a15.loader import core

    data = Path(a.data)
    history = core.read_history(data)
    hist = ingest.release(
        "history", ingest.HISTORY_RECIPE,
        ingest.history_chunks([{"record_id": h["record_id"], "symptom_group": h["symptom_group"]["code"], "narrative": h["narrative"]} for h in history]),
        {"file": "history/maintenance_history.jsonl", "sha256": ingest.sha256((data / "history" / "maintenance_history.jsonl").read_bytes())},
        qs=ingest.queries(ingest.GROUP_NAME),
    )
    md = (data / "manuals" / "MG-MM.md").read_text(encoding="utf-8")
    man = ingest.release("manual", ingest.MANUAL_RECIPE, ingest.manual_chunks(md, core.read_manual(data)),
                         {"file": "manuals/MG-MM.md", "sha256": ingest.sha256(md.encode("utf-8"))})
    out = {r["kind"]: {"release_id": r["release_id"], "release_sha256": r["release_sha256"], "recipe": r["recipe"], "recipe_sha256": r["recipe_sha256"],
                       "embedding": {"model": r["embedding_model"], "dim": r["embedding_dim"]}, "chunks": len(r["chunks"]), "queries": len(r["queries"]),
                       "locators": [{"chunk_id": c["chunk_id"], **c["locator"]} for c in r["chunks"]]} for r in (hist, man)}
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if a.out:
        Path(a.out).write_text(text + "\n", encoding="utf-8")
    print(json.dumps({k: {kk: v[kk] for kk in ("release_id", "chunks", "queries")} for k, v in out.items()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
