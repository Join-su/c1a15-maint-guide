"""P-04 검색 시험: 토큰 · RRF · 고정 질의 상위 10건 · 누수 음성(ADV-04) · 평가 모드 제외."""

import pytest

from c1a15.loader import core
from c1a15.loader.embedding import fake_embedding
from c1a15.retrieval import search
from c1a15.retrieval.tokens import tokenize


@pytest.fixture(scope="module")
def docs(data_dir_module):
    return [
        search.HistoryDoc(
            h["record_id"],
            h["symptom_group"]["code"],
            h["narrative"],
            h["sensor_snapshot"],
            h["outcome"].get("cause_code"),
            tuple(fake_embedding(h["narrative"])),
        )
        for h in core.read_history(data_dir_module)
    ]


def run_query(docs, text, sensor, group="CL", search_fn=search.similar_records):
    index = search.Index(docs)
    qv = fake_embedding(text)
    pool = [d for d in docs if d.symptom_group == group]
    return search_fn(
        {"symptom_group": group},
        text,
        sensor,
        docs,
        index.bm25,
        search.cosine_rank(qv, pool),
        search.sensor_stats(docs),
    )


QUERY = "온도 차 저하 경계 아래 4.2 고온부 확인"
SENSOR = {
    "air_temperature_k": 302.5,
    "process_temperature_k": 310.4,
    "rotational_speed_rpm": 1500,
    "torque_nm": 40.0,
    "tool_wear_min": 100,
    "temp_diff_k": 7.9,
    "power_w": 6283,
}


def test_tokenize_words_and_hangul_bigrams():
    assert tokenize("냉각수 수위 MIN") == ["냉각수", "냉각", "각수", "수위", "min"]


def test_rrf_formula():
    fused = search.rrf([["a", "b"], ["b", "a"]])
    assert fused["a"] == pytest.approx(1 / 61 + 1 / 62) and fused["a"] == fused["b"]


def test_fixed_query_top10_is_deterministic_and_same_group(docs):
    first = run_query(docs, QUERY, SENSOR)
    assert [s.record_id for s in first] == [s.record_id for s in run_query(docs, QUERY, SENSOR)]
    assert len(first) == 10 and all(
        d.symptom_group == "CL" for d in docs if d.record_id in {s.record_id for s in first}
    )
    assert all(0 <= s.score <= 1 for s in first) and [s.score for s in first] == sorted(
        (s.score for s in first), reverse=True
    )
    assert first[0].percent == round(first[0].score * 100)


def test_adv04_cause_filter_is_caught(docs, monkeypatch):
    """ADV-04: 검색 결함 사본이 원인 필드로 거르면 누수 검사가 실패를 낸다."""
    with pytest.raises(search.LeakageError):
        search.check_filters({"symptom_group": "CL", "cause": "CL-1"})
    original = search.similar_records

    def leaky(filters, *args):
        return original({**filters, "cause": "CL-1"}, *args)

    with pytest.raises(search.LeakageError):
        run_query(docs, QUERY, SENSOR, search_fn=leaky)


def test_approved_report_added_but_not_in_eval_mode(docs):
    index = search.Index(docs)
    new = search.HistoryDoc(
        "R-0001",
        "CL",
        "흡기 필터 기름때 막힘 확인 후 교체",
        docs[0].sensor,
        "CL-1",
        tuple(fake_embedding("흡기 필터")),
        "approved_report",
    )
    assert not index.add_approved(new, eval_mode=True) and "R-0001" not in index.bm25.docs  # AC-09-C2 판정 부분
    assert index.add_approved(new, eval_mode=False) and "R-0001" in index.bm25.docs  # AC-09-C1 판정 부분
    assert "R-0001" in {d.record_id for d in index.docs}  # 벡터 쪽 문서 목록에도


def test_approved_report_becomes_search_candidate_except_eval_mode(docs):
    """P-04 verifier · AC-09(검색 부분): 승인 뒤 같은 증상군 재검색 상위 10건에 들고, 평가 모드에서는 들지 않는다.

    DB 저장 · 승인 흐름(P-13)은 이 시험 밖."""

    def search_with(index):
        pool = [d for d in index.docs if d.symptom_group == "CL"]
        top = search.similar_records(
            {"symptom_group": "CL"},
            QUERY,
            SENSOR,
            index.docs,
            index.bm25,
            search.cosine_rank(fake_embedding(QUERY), pool),
            search.sensor_stats(docs),
        )
        return [r.record_id for r in top]

    report = search.HistoryDoc("R-0002", "CL", QUERY, SENSOR, "CL-1", tuple(fake_embedding(QUERY)), "approved_report")
    evaluated = search.Index(docs)
    evaluated.add_approved(report, eval_mode=True)
    assert "R-0002" not in search_with(evaluated)  # AC-09-C2
    approved = search.Index(docs)
    approved.add_approved(report, eval_mode=False)
    assert "R-0002" in search_with(approved)  # AC-09-C1
