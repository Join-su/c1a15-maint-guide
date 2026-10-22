"""EV-001 CH-05 · CH-08: ingest — 원문(이력 · 매뉴얼) → 조각 → 임베딩 → hash 고정 data release.

순수 함수만(DB는 ingest.store). 이 판의 임베딩은 가짜(fake-hash-bigram-v1, 외부 호출 0) — 실제 임베딩은 다음 판(NX-04).
기본 이력 recipe = '1건 1조각'(기록 서술 전체가 조각 하나, 겹침 0) — 지금 1건 1벡터와 같은 단위라
검색 결과가 같다(VC-11). release_id · release_sha256은 recipe · 임베딩 모델 · 조각(ID · 문서 · 원문 위치 ·
본문 hash · 임베딩)으로만 정해진다(같은 입력 → 같은 판, VC-08).
"""

import hashlib
import json

from c1a15.db.models import EMBEDDING_DIM
from c1a15.loader.embedding import FAKE_MODEL, fake_embedding

HISTORY_RECIPE = {"split_by": "record", "chunk_chars": None, "overlap": 0, "metadata": ["record_id", "symptom_group"]}
MANUAL_RECIPE = {"split_by": "section", "chunk_chars": None, "overlap": 0, "metadata": ["section", "kind", "group"]}
MANUAL_DOC = "MG-MM"
DIRECTIONS = ("경계 아래", "경계 위")
GROUP_NAME = {
    "TW": "공구 마모 경고",
    "PW": "출력 이탈",
    "CL": "온도 차 저하",
    "LD": "토크 과부하",
}  # = api.sessions.GROUP_NAME(시험으로 묶음)


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def vec_text(vec: list[float]) -> str:
    """DB에 넣는 모양(소수 8자리) — hash도 이 모양으로 계산한다."""
    return "[" + ",".join(f"{v:.8f}" for v in vec) + "]"


def embed(text: str) -> list[float]:
    return fake_embedding(text)


def history_chunks(records: list[dict]) -> list[dict]:
    """records: record_id · symptom_group(코드) · narrative. 기본 recipe '1건 1조각'."""
    out = []
    for r in records:
        text = r["narrative"]
        out.append(
            {
                "chunk_id": f"{r['record_id']}#0",
                "doc": "history",
                "locator": {"record_id": r["record_id"], "char_start": 0, "char_end": len(text)},
                "text": text,
                "metadata": {"record_id": r["record_id"], "symptom_group": r["symptom_group"]},
                "embedding": embed(text),
            }
        )
    return out


def manual_chunks(manual_md: str, sections: list[dict]) -> list[dict]:
    """절 단위 조각(검색 평가 전용, CH-07). 원문 위치 = MG-MM.md 안 글자 범위
    — 본문이 없는 조치 절(상위 점검 절 안)은 뺀다.
    """
    out, pos = [], 0
    for s in sections:
        text = s.get("text")
        if not text:
            continue
        start = manual_md.find(text, pos)  # 절 차례대로 — 앞 절과 본문이 같아도 뒤 위치를 잡음
        if start < 0:
            raise ValueError(f"매뉴얼 원문에서 절 본문을 찾지 못함: {s['id']}")
        pos = start + len(text)
        out.append(
            {
                "chunk_id": f"{MANUAL_DOC}#{s['id']}",
                "doc": MANUAL_DOC,
                "locator": {"doc": MANUAL_DOC, "section": s["id"], "char_start": start, "char_end": start + len(text)},
                "text": text,
                "metadata": {"section": s["id"], "kind": s.get("kind"), "group": s.get("group")},
                "embedding": embed(text),
            }
        )
    return out


def queries(group_names: dict[str, str]) -> dict[str, str]:
    """질의 임베딩 미리 계산(Q-2): 증상군 이름 × 알람 방향
    — 세션 시작 질의(retrieval.search.query_text, 결과 없음)와 같은 글.
    """
    from c1a15.retrieval.search import query_text

    return {
        q: vec_text(embed(q)) for name in group_names.values() for d in DIRECTIONS for q in [query_text(name, d, [])]
    }


def release(
    kind: str, recipe: dict, chunks: list[dict], source: dict, parent: str | None = None, qs: dict | None = None
) -> dict:
    body = sorted(
        [c["chunk_id"], c["doc"], c["locator"], sha256(c["text"].encode("utf-8")), vec_text(c["embedding"])]
        for c in chunks
    )
    rsha = sha256(
        canonical(
            {
                "kind": kind,
                "recipe": recipe,
                "model": FAKE_MODEL,
                "dim": EMBEDDING_DIM,
                "chunks": body,
                "queries": qs or {},
            }
        )
    )
    return {
        "release_id": f"{kind}-{rsha[:16]}",
        "kind": kind,
        "recipe": recipe,
        "recipe_sha256": sha256(canonical(recipe)),
        "embedding_model": FAKE_MODEL,
        "embedding_dim": EMBEDDING_DIM,
        "source": source,
        "parent_release_id": parent,
        "release_sha256": rsha,
        "queries": qs or {},
        "chunks": chunks,
    }


def locate(chunk: dict, original: str) -> str:
    """원문 위치로 조각 되찾기(VC-09): 원문[char_start:char_end]."""
    loc = chunk["locator"]
    return original[loc["char_start"] : loc["char_end"]]
