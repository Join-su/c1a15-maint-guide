# ruff: noqa: F811, E501 — test_api · test_deploy_path · test_ml_demo_path의 fixture를 이름으로 쓴다, 시험 설명 문장은 길이 제한 밖
"""EV-009(D-444 #18 · D-446 ⑤ · 001-58 (가)): 파트장 '사람 판단' — ML 길에서 알람 없이 남은 후보(확신 낮음 · RNF · 예측 실패).

목록(판단 전 · 평가 아님) → [알람으로 올림] = 지금 알람과 같은 배정 · 새 Run 0 / [문제없음]. 두 번 = 409 · 정비자 403.
경계 안 후보를 올리면 경계 칸을 지어내지 않는다: origin lead · crossed false · 화면 글은 '경계 안 · 파트장이 올림' · Pack 질의 방향 null.
"""

import json
import math

import pytest
from sqlalchemy import text

import fake_deploy
from c1a15.api import deps
from c1a15.engine import alarm_rules
from test_api import LEAD_PW, TECH_PW, api, db, login  # noqa: F401
from test_deploy_path import deploy, register_sc, reset_ops, scenarios  # noqa: F401
from test_ml_demo_path import ml  # noqa: F401

pytestmark = pytest.mark.db
NORMAL = {
    "air_temperature_k": 300.0,
    "process_temperature_k": 310.0,
    "rotational_speed_rpm": 1500.0,
    "torque_nm": 40.0,
    "tool_wear_min": 100.0,
}


def derived(s5):
    return {
        "power_w": round(s5["torque_nm"] * s5["rotational_speed_rpm"] * 2 * math.pi / 60),
        "temp_diff_k": round(s5["process_temperature_k"] - s5["air_temperature_k"], 1),
    }


def pack_candidate(monkeypatch, sc, reason, top_k, s5):
    """가짜 Pack alarm 출력을 '후보'로 — 그 시연 행(udi)만."""
    out = {
        "alarm": False,
        "group": None,
        "group_source": None,
        "alarm_block": None,
        "sensor_derived": derived(s5),
        "ml": {"model_release": "c1a15-ml@test", "risk": 0.62, "threshold": 0.5},
        "candidate": {
            "reason": reason,
            "risk": 0.62,
            "top_k": top_k,
            "boundary_crossed": alarm_rules.detect({**s5, **derived(s5)}, deps.alarm_table()) is not None,
            "model_release": "c1a15-ml@test",
        },
    }
    real = fake_deploy.ml_alarm_outputs

    monkeypatch.setattr(fake_deploy, "ml_alarm_outputs", lambda path=None: {**real(path), str(sc["udi"]): out})


def candidate_via_ml(api, monkeypatch, reason="low_confidence", top_k=None, s5=None):
    sc = next(s for s in scenarios() if s["scenario_id"] == "DEMO-01")
    s5 = s5 or NORMAL
    top_k = (
        top_k
        if top_k is not None
        else [
            {"type": "HDF", "probability": 0.41, "group_suggestion": "CL"},
            {"type": "OSF", "probability": 0.12, "group_suggestion": "LD"},
        ]
    )
    pack_candidate(monkeypatch, sc, reason, top_k, s5)
    r = register_sc(api, sc, sensor_snapshot=s5)
    assert r.status_code == 200 and r.json()["candidate_id"], r.text
    return r.json()["candidate_id"]


def insert_candidate(db, reason="model_failure", s5=None, sensor_derived=True, status="needs_human", eval_mode=False):
    s5 = s5 or NORMAL
    event = {
        "event_id": "evt-test",
        "sensor_snapshot": s5,
        **({"sensor_derived": derived(s5)} if sensor_derived else {}),
    }
    with db.begin() as c:
        return c.execute(
            text(
                "insert into ops.alarm_candidates (equipment_id, reason, risk, top_k, boundary_crossed, model_release, "
                "sensor_snapshot, event, status, eval_mode, event_id) values ('M-01', :r, null, '[]'::jsonb, :x, null, "
                "cast(:s as jsonb), cast(:e as jsonb), :st, :ev, 'evt-test') returning candidate_id"
            ),
            {
                "r": reason,
                "x": alarm_rules.detect({**s5, **derived(s5)}, deps.alarm_table()) is not None,
                "s": json.dumps(s5),
                "e": json.dumps(event),
                "st": status,
                "ev": eval_mode,
            },
        ).scalar_one()


def one(db, sql, **kw):
    with db.connect() as c:
        return c.execute(text(sql), kw).one()._mapping


def runs_of(fake):
    return [p for p in fake.posts() if p["path"] == "/runs"]


def lead_client(api):
    return login(api, "lead", "lead.park", LEAD_PW)[0]


def test_candidate_keeps_pack_derived_sensors(api, db, ml, monkeypatch):
    """후보 기록에 Pack이 계산한 칸(출력 · 온도 차)도 남김 — 올릴 때 앱이 다시 계산하지 않게."""
    reset_ops(db)
    cid = candidate_via_ml(api, monkeypatch)
    row = one(db, "select event, status from ops.alarm_candidates where candidate_id = :c", c=cid)
    assert row["event"]["sensor_derived"] == derived(NORMAL) and row["status"] == "needs_human"


def test_list_only_open_non_eval(api, db, ml, monkeypatch):
    reset_ops(db)
    login(api, "tech", "tech.kim", TECH_PW)
    cid = candidate_via_ml(api, monkeypatch)
    insert_candidate(db, eval_mode=True)
    insert_candidate(db, status="dismissed")
    got = lead_client(api).get("/api/lead/candidates").json()
    rows = got["rows"]
    assert [r["candidate_id"] for r in rows] == [cid] and [g["value"] for g in got["groups"]] == [
        "TW",
        "PW",
        "CL",
        "LD",
    ]
    r = rows[0]
    assert r["reason"] == "low_confidence" and r["equipment_id"] == "M-01" and not r["boundary_crossed"]
    assert r["group_suggestion"] == "CL" and r["group_fixed"] is False
    assert r["top"] == {"type": "HDF", "probability": 0.41} and r["risk"] == 0.62
    assert "1,500 rpm" in r["sensors_text"]


def test_promote_not_crossed_no_made_up_boundary(api, db, ml, monkeypatch):
    """경계 안 확신 낮음 → 올림: ML 1위 증상군 · origin lead · crossed false · 배정 · 새 Run 0 · 화면 글 · 질의 방향 null."""
    reset_ops(db)
    tech, _ = login(api, "tech", "tech.kim", TECH_PW)
    cid = candidate_via_ml(api, monkeypatch)
    before = len(runs_of(ml))
    lead = lead_client(api)
    r = lead.post(f"/api/lead/candidates/{cid}/decision", json={"decision": "promote"})
    assert r.status_code == 200, r.text
    aid = r.json()["alarm_id"]
    assert len(runs_of(ml)) == before  # 올림은 새 Run을 부르지 않음
    a = one(
        db,
        "select symptom_group, alarm, assigned_to, sensor_snapshot, event_id from ops.alarms where alarm_id = :a",
        a=aid,
    )
    assert a["symptom_group"] == "CL" and a["assigned_to"] == "tech.kim" and a["event_id"]
    assert a["alarm"]["origin"] == "lead" and a["alarm"]["crossed"] is False and a["alarm"]["value"] == 10.0
    assert a["sensor_snapshot"]["temp_diff_k"] == 10.0  # Pack 계산 칸
    st = one(db, "select status from ops.alarm_candidates where candidate_id = :c", c=cid)["status"]
    assert st == "promoted"
    assert one(db, "select count(*) n from ops.audit_log where action = 'candidate_promote'")["n"] == 1
    assert aid in [x["alarm_id"] for x in tech.get("/api/tech/home").json()["alarms"]]
    r = tech.post(f"/api/tech/alarms/{aid}/session")
    assert r.status_code == 200, r.text
    s = r.json()
    assert "경계 안 · 파트장이 올림" in s["alarm"]["ai_reading"]["text"]
    start = [p for p in runs_of(ml) if p["body"].get("kind") == "start"][-1]
    assert start["body"]["query"]["direction"] is None  # 넘지 않은 경계 방향을 Pack에 보내지 않음


def test_rnf_needs_group_then_promotes(api, db, ml, monkeypatch):
    reset_ops(db)
    login(api, "tech", "tech.kim", TECH_PW)
    cid = candidate_via_ml(
        api, monkeypatch, reason="rnf", top_k=[{"type": "RNF", "probability": 0.55, "group_suggestion": None}]
    )
    lead = lead_client(api)
    assert lead.get("/api/lead/candidates").json()["rows"][0]["group_suggestion"] is None
    r = lead.post(f"/api/lead/candidates/{cid}/decision", json={"decision": "promote"})
    assert r.status_code == 422 and r.json()["detail"] == "group_required"
    r = lead.post(f"/api/lead/candidates/{cid}/decision", json={"decision": "promote", "group": "TW"})
    assert r.status_code == 200
    assert (
        one(db, "select symptom_group from ops.alarms where alarm_id = :a", a=r.json()["alarm_id"])["symptom_group"]
        == "TW"
    )


def test_crossed_candidate_uses_boundary(api, db, deploy):
    """경계를 넘은 후보(예측 실패)는 경계 판정 그대로 — 지금 알람과 같은 경계 칸(origin 없음)."""
    reset_ops(db)
    login(api, "tech", "tech.kim", TECH_PW)
    s5 = {
        k: v
        for k, v in next(s for s in scenarios() if s["scenario_id"] == "DEMO-01")["sensor_snapshot"].items()
        if k in NORMAL
    }
    cid = insert_candidate(db, s5=s5)
    r = lead_client(api).post(f"/api/lead/candidates/{cid}/decision", json={"decision": "promote", "group": "TW"})
    assert r.status_code == 200, r.text
    a = one(db, "select symptom_group, alarm from ops.alarms where alarm_id = :a", a=r.json()["alarm_id"])
    assert a["symptom_group"] == "CL" and a["alarm"]["direction"] == "경계 아래" and "origin" not in a["alarm"]


def test_dismiss_then_twice_409_and_tech_forbidden(api, db, deploy):
    reset_ops(db)
    tech, _ = login(api, "tech", "tech.kim", TECH_PW)
    cid = insert_candidate(db)
    lead = lead_client(api)
    assert lead.post(f"/api/lead/candidates/{cid}/decision", json={"decision": "dismiss"}).status_code == 200
    assert one(db, "select status from ops.alarm_candidates where candidate_id = :c", c=cid)["status"] == "dismissed"
    r = lead.post(f"/api/lead/candidates/{cid}/decision", json={"decision": "promote", "group": "CL"})
    assert r.status_code == 409 and r.json()["detail"] == "already_decided"
    assert lead.get("/api/lead/candidates").json()["rows"] == []
    assert tech.get("/api/lead/candidates").status_code in (401, 403)


def test_no_derived_sensors_409(api, db, deploy):
    """Pack 계산 칸이 없는 옛 후보는 올리지 않음(앱이 계산하지 않음)."""
    reset_ops(db)
    login(api, "tech", "tech.kim", TECH_PW)
    cid = insert_candidate(db, sensor_derived=False)
    r = lead_client(api).post(f"/api/lead/candidates/{cid}/decision", json={"decision": "promote", "group": "CL"})
    assert r.status_code == 409 and r.json()["detail"] == "no_derived_sensors"
