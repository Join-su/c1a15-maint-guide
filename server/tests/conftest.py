from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def data_dir() -> Path:
    return REPO / "data"


@pytest.fixture(scope="module")
def data_dir_module() -> Path:
    return REPO / "data"


@pytest.fixture(scope="session", autouse=True)
def deploy_path_everywhere():
    """C1A15_TEST_DEPLOY=1이면 모든 시험을 deploy 길(가짜 배포 서버 + 앱 engine 계산)로 — EV-001 VC-34 두 길 대조."""
    import os

    if os.environ.get("C1A15_TEST_DEPLOY") != "1":
        yield None
        return
    from c1a15.deploy import runs
    from fake_deploy import FakeDeploy, engine_answer

    with FakeDeploy() as fake:
        fake.default = engine_answer
        os.environ["C1A15_JUDGE"], os.environ["C1A15_DEPLOY_URL"] = "deploy", fake.url
        runs.settings.cache_clear()
        runs.client.cache_clear()
        yield fake
        evidence = os.environ.get("C1A15_DEPLOY_EVIDENCE")  # 받은 본문 · 돌려준 응답 → VC-35 schema 검사
        if evidence:
            import json
            from pathlib import Path

            with Path(evidence).open("a", encoding="utf-8") as f:
                for r in fake.posts():
                    f.write(json.dumps({"request": r["body"]}, ensure_ascii=False) + "\n")
                for rec in fake.keys.values():
                    if rec["status"] in (200, 201):
                        f.write(json.dumps({"response": rec["payload"]["result"]["output"]}, ensure_ascii=False) + "\n")


@pytest.fixture
def inproc_path(monkeypatch):
    """앱 임시 리트리버를 부르는 기본 길(inproc) 전용 시험 — deploy 길 묶음에서도 inproc로(EV-001 ES-15).

    deploy 길은 상위 10을 Pack 리트리버가 고르므로 앱 리트리버를 부르지 않음.
    ES-16에서 inproc가 빠질 때 이 시험들을 고침.
    """
    from c1a15.deploy import runs

    monkeypatch.setenv("C1A15_JUDGE", "inproc")
    runs.settings.cache_clear()
    yield
    runs.settings.cache_clear()
