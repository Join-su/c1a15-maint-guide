"""P-05 LLM Adapter 시험: fixture 문장 · R7 단어 규칙 · R8 근거 검사와 원문 대체 · 3회 연속 실패 · ADV-05."""

import socket

import pytest

from c1a15.llm import adapter_for_mode, grounding
from c1a15.llm.base import AdapterError, Draft, Facts
from c1a15.llm.fixture import FixtureAdapter

G = grounding.Grounding(
    frozenset({"4.3", "4.4", "4.5", "4.6"}), grounding.numbers_in("50 3 28 5 11 4"), frozenset({"H-0299"})
)


class NetworkGuard:
    """시험 안에서 소켓 연결을 막고 센다(외부 DNS · 인터넷 차단)."""

    def __init__(self, monkeypatch):
        self.calls = []
        real = socket.socket.connect

        def guarded(sock, address):
            self.calls.append(address)
            raise OSError("network blocked in test")

        monkeypatch.setattr(socket.socket, "connect", guarded)
        self.real = real


def test_fixture_reason_is_grounded_and_mode_default(monkeypatch):
    monkeypatch.delenv("APP_MODE", raising=False)
    adapter = adapter_for_mode()
    assert adapter.mode == "fixture"
    facts = Facts(
        "reason",
        "4.3",
        {
            "cause_name": "냉각 필터 막힘",
            "probability": 50,
            "minutes": 3,
            "grade": "A",
            "alternatives": [{"section": "4.4", "grade": "C"}],
        },
    )
    out = grounding.checked(lambda: adapter.write(facts), G, "4.3 흡기 필터 육안 점검")
    assert not out.fallback and "50%" in out.text


def test_r7_fixture_signals():
    f = FixtureAdapter()
    assert f.memo_signal(
        "4.3", "기름때·먼지가 덮으면 이상", "필터에 기름때가 많음", "정상"
    ).conflicts_with_button  # (a)
    sig = f.memo_signal("4.3", "", "깨끗함", None)
    assert sig.interpretation == "정상" and not sig.conflicts_with_button  # (b)
    assert f.memo_signal("4.3", "", "타는 냄새가 남", "정상").out_of_scope_finding  # (c)
    assert f.memo_signal("4.3", "", "깨끗함", "정상") is None  # 버튼과 같은 뜻이면 신호 없음


def test_r8_ungrounded_rewrite_then_fallback():
    calls = []

    def bad():
        calls.append(1)
        return Draft("4.7절에서 99% 확인", sections=("4.7",))

    out = grounding.checked(bad, G, "4.3 흡기 필터 육안 점검 원문")
    assert (
        out.fallback and out.label == "원문으로 대체됨" and len(calls) == 2
    )  # 1회 다시 작성 뒤 대체(AC-06-C1 판정 부분)
    assert not grounding.is_grounded(Draft("H-9999 기록 참고"), G)  # 상위 10건 밖 사례 ID


def test_provider_error_falls_back_and_three_in_a_row_recommends_handover():  # AC-31-C2
    def boom():
        raise AdapterError("provider down")

    out = grounding.checked(boom, G, "원문")
    assert out.fallback  # AC-31-C1 판정 부분: 원문 대체로 계속
    assert grounding.should_recommend_handover([True, True, True]) and not grounding.should_recommend_handover(
        [True, False, True, True]
    )


def test_live_requires_key_and_model(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(AdapterError):
        adapter_for_mode("live")


def test_adv05_fixture_makes_no_external_call_and_guard_catches_faulty_provider(monkeypatch):
    """ADV-05: (a) fixture 경로는 소켓 연결 0건, 네트워크를 시도하는 가짜 provider는 차단되고 카운터가 1이 된다.
    (b) 근거 없는 문장을 내는 가짜 provider의 문장은 원문 대체된다. 대상은 127.0.0.1 임시 listener."""
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    try:
        port = listener.getsockname()[1]
        guard = NetworkGuard(monkeypatch)
        f = FixtureAdapter()
        f.write(Facts("instruction", "4.3", {"procedure": "1. 측면 냉각 커버의 고정 나사 2개를 푼다."}))
        f.memo_signal("4.3", "", "깨끗", "정상")
        assert guard.calls == []  # fixture 외부 호출 0(AC-16-C2 판정 부분)

        class FaultyProvider:
            mode = "faulty"

            def write(self, facts):
                socket.create_connection(("127.0.0.1", port), timeout=1)  # 외부 주소 대용
                return Draft("4.3 확인")

        out = grounding.checked(lambda: _wrap(FaultyProvider().write, Facts("reason", "4.3")), G, "원문")
        assert len(guard.calls) == 1 and out.fallback
        out = grounding.checked(lambda: Draft("4.8절 기준 77%"), G, "원문")
        assert out.fallback and out.text == "원문"
    finally:
        listener.close()


def _wrap(fn, facts):
    try:
        return fn(facts)
    except OSError as exc:
        raise AdapterError(str(exc)) from exc
