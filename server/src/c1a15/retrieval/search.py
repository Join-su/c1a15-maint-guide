"""R3 검색: 같은 증상군 필터 → BM25 + 의미 검색 → RRF(k=60) 상위 10건 → 센서 거리로 다시 정렬 · score.

숫자(RRF k · 상위 k · 재정렬 가중 · BM25 k1 · b · 의미 후보 수 · 센서 칸)는 리트리버 설정 파일에서 읽는다
(data/retriever.json, retrieval.settings). 아래 상수는 그 기본값과 같은 값(메모리 시험용). EV-001 CH-06.

원인 필드(확정 원인 · outcome)는 검색 조건 · 순위 입력에 쓰지 않는다(AC-15-C3, EP-PACK-DATA-002).
결과의 원인은 R4 점수 계산을 위해 검색이 끝난 뒤에만 붙인다.
"""

import math
from dataclasses import dataclass

from c1a15.engine.rules import Similar
from c1a15.retrieval.bm25 import BM25
from c1a15.retrieval.settings import Settings

DEFAULT = Settings()

RRF_K = 60
TOP_N = 10
SENSOR_KEYS = (
    "air_temperature_k",
    "process_temperature_k",
    "rotational_speed_rpm",
    "torque_nm",
    "tool_wear_min",
    "temp_diff_k",
    "power_w",
)
ALLOWED_FILTERS = {"symptom_group"}
ANSWER_FIELDS = {"cause", "cause_code", "outcome", "confirmed_cause"}


class LeakageError(ValueError):
    pass


@dataclass(frozen=True)
class HistoryDoc:
    record_id: str
    symptom_group: str
    narrative: str
    sensor: dict
    cause: str | None
    embedding: tuple[float, ...]
    source: str = "generated"


@dataclass(frozen=True)
class SimilarRecord:
    record_id: str
    cause: str | None
    rrf: float
    distance: float
    score: float

    @property
    def percent(self) -> int:
        return round(self.score * 100)  # 유사도 % = score × 100(반올림)

    def as_similar(self) -> Similar:
        return Similar(self.record_id, self.cause, self.score)


def check_filters(filters: dict) -> None:
    """누수 검사: 검색 조건에는 증상군만 둘 수 있다."""
    bad = set(filters) & ANSWER_FIELDS or set(filters) - ALLOWED_FILTERS
    if bad:
        raise LeakageError(f"검색 조건에 쓸 수 없는 필드: {sorted(bad)}")


def sensor_stats(docs: list[HistoryDoc]) -> dict[str, tuple[float, float]]:
    """학습용(train) 행 생성 이력의 평균 · 표준편차(R3 정규화 기준)."""
    base = [d for d in docs if d.source == "generated"]
    stats = {}
    for key in SENSOR_KEYS:
        values = [float(d.sensor[key]) for d in base]
        mean = sum(values) / len(values)
        std = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values)) or 1.0
        stats[key] = (mean, std)
    return stats


def sensor_distance(
    a: dict, b: dict, stats: dict[str, tuple[float, float]], keys: tuple[str, ...] = SENSOR_KEYS
) -> float:
    return math.sqrt(sum(((float(a[k]) - float(b[k])) / stats[k][1]) ** 2 for k in keys))


def cosine_rank(query_vec: list[float], docs: list[HistoryDoc]) -> list[str]:
    """의미 검색 순위(메모리 · 시험용). DB에서는 pgvector `<=>`(cosine distance)가 같은 순서를 낸다."""
    sims = {d.record_id: sum(x * y for x, y in zip(query_vec, d.embedding, strict=True)) for d in docs}
    return sorted(sims, key=lambda rid: (-sims[rid], rid))


def rrf(rank_lists: list[list[str]], k: int = RRF_K) -> dict[str, float]:
    fused: dict[str, float] = {}
    for ranks in rank_lists:
        for i, rid in enumerate(ranks, start=1):
            fused[rid] = fused.get(rid, 0.0) + 1.0 / (k + i)
    return fused


def similar_records(
    filters: dict,
    query_text: str,
    query_sensor: dict,
    docs: list[HistoryDoc],
    bm25: BM25,
    vector_ranks: list[str],
    stats: dict[str, tuple[float, float]],
    cfg: Settings = DEFAULT,
) -> list[SimilarRecord]:
    """R3 상위 10건(score 순). RRF정규화 = RRF ÷ 상위 10건 최댓값, d정규화 = d ÷ 상위 10건 최댓값(L0 정의)."""
    check_filters(filters)
    pool = [d for d in docs if d.symptom_group == filters["symptom_group"]]
    ids = {d.record_id for d in pool}
    semantic = [r for r in vector_ranks if r in ids][: cfg.semantic_candidates]
    fused = rrf([bm25.rank(query_text, sorted(ids)), semantic], k=cfg.rrf_k)
    top = sorted(fused, key=lambda r: (-fused[r], r))[: cfg.top_k]
    by_id = {d.record_id: d for d in pool}
    dist = {r: sensor_distance(query_sensor, by_id[r].sensor, stats, cfg.sensor_keys) for r in top}
    max_rrf, max_d = max(fused[r] for r in top) if top else 1.0, (max(dist.values()) if dist else 0.0) or 1.0
    out = [
        SimilarRecord(
            r,
            by_id[r].cause,
            fused[r],
            dist[r],
            cfg.w_rrf * (fused[r] / max_rrf) + cfg.w_sensor * (1 - dist[r] / max_d),
        )
        for r in top
    ]
    return sorted(out, key=lambda s: (-s.score, s.record_id))


def query_text(group_name: str, direction: str, results: list[dict]) -> str:
    """R3 질의: 증상군 · 알람 값 방향 · 이번 세션의 점검 결과 · 메모."""
    parts = [group_name, direction] + [
        f"{r.get('section', '')} {r.get('value', '')} {r.get('memo', '')}" for r in results
    ]
    return " ".join(p for p in parts if p)


class Index:
    """BM25 메모리 색인 + 문서 목록. R12: 승인 보고서를 추가(평가 모드에서는 하지 않음)."""

    def __init__(
        self,
        docs: list[HistoryDoc],
        cfg: Settings = DEFAULT,
        release_id: str | None = None,
        queries: dict | None = None,
    ):
        self.docs = list(docs)
        self.cfg, self.release_id, self.queries = (
            cfg,
            release_id,
            queries or {},
        )  # 이력 release(EV-001 CH-06) · 미리 계산한 질의 벡터
        self.bm25 = BM25(cfg.bm25_k1, cfg.bm25_b)
        for d in self.docs:
            self.bm25.add(d.record_id, d.narrative)

    def add_approved(self, doc: HistoryDoc, *, eval_mode: bool) -> bool:
        if eval_mode:  # R12: 평가 모드에서는 이력에 넣지 않는다(AC-09-C2)
            return False
        if doc.source != "approved_report":
            raise ValueError("승인 보고서만 이력 색인에 추가한다")
        self.docs.append(doc)
        self.bm25.add(doc.record_id, doc.narrative)
        return True
