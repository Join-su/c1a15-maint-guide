"""리트리버 설정 파일(data/retriever.json, EV-001 CH-06): 검색 숫자를 코드 상수 대신 여기서 읽는다.

리트리버 node 옵션만 둔다(분류표 (가)). 사용자 설정 숫자는 넣지 않는다 — 이름이 들어오면 읽기를 거절한다(PR-09 · VC-24).
상위 k는 이 판에서 10 고정(R4 · R6 입력 · AC-40 문구가 묶여 있음, 바꾸는 것은 다음 판 NX-02).
"""

import json
from dataclasses import dataclass
from pathlib import Path

USER_SETTING_NAMES = {
    "alpha",
    "call_threshold",
    "low_evidence",
    "low_evidence_score",
    "ml_alarm_threshold",
    "unable_repeat",
    "llm_failure_limit",
}
FIXED_TOP_K = 10


@dataclass(frozen=True)
class Settings:
    rrf_k: int = 60
    top_k: int = FIXED_TOP_K
    w_rrf: float = 0.5
    w_sensor: float = 0.5
    metadata_filter: tuple[str, ...] = ("symptom_group",)
    bm25_k1: float = 1.5
    bm25_b: float = 0.75
    semantic_candidates: int = 300
    sensor_keys: tuple[str, ...] = (
        "air_temperature_k",
        "process_temperature_k",
        "rotational_speed_rpm",
        "torque_nm",
        "tool_wear_min",
        "temp_diff_k",
        "power_w",
    )
    similarity_threshold: float | None = None


def load(path: Path) -> Settings:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    bad = USER_SETTING_NAMES & set(d) | USER_SETTING_NAMES & set(d.get("search", {}))
    if bad:
        raise ValueError(f"리트리버 설정에 사용자 설정 숫자 이름: {sorted(bad)}")
    if d["top_k"] != FIXED_TOP_K:
        raise ValueError(f"상위 k는 이 판에서 {FIXED_TOP_K} 고정(받은 값 {d['top_k']})")
    if d.get("similarity_threshold") is not None:
        raise ValueError("유사도 임계값은 이 판에서 없음(null) — 켜는 것은 retrieve@2 node와 함께(NX-02)")
    s = d["search"]
    return Settings(
        rrf_k=d["rrf_k"],
        top_k=d["top_k"],
        w_rrf=d["rerank_weights"]["rrf"],
        w_sensor=d["rerank_weights"]["sensor"],
        metadata_filter=tuple(d["metadata_filter"]),
        bm25_k1=s["bm25"]["k1"],
        bm25_b=s["bm25"]["b"],
        semantic_candidates=s["semantic_candidates"],
        sensor_keys=tuple(d["sensor_keys"]),
        similarity_threshold=d.get("similarity_threshold"),
    )
