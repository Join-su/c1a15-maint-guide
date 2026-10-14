"""시연 각본 10건의 첫 판정(진단 화면 미리보기와 같은 계산: 검색 상위 10 → fold(잠금 · 사전 확인) → decide, 초기 등급표)."""
import json
from pathlib import Path
from c1a15.api.sessions import GROUP_NAME
from c1a15.engine import alarm_rules, knowledge, rules, session
from c1a15.loader import core
from c1a15.loader.embedding import fake_embedding
from c1a15.retrieval import search

D = Path("../data")
k = knowledge.from_sections(core.read_manual(D))
gr = core.grade_rows(core.read_manual(D))
g, mins = {r["section_id"]: r["grade"] for r in gr}, {r["section_id"]: r["minutes"] for r in gr}
docs = [search.HistoryDoc(h["record_id"], h["symptom_group"]["code"], h["narrative"], h["sensor_snapshot"],
        h["outcome"].get("cause_code"), tuple(fake_embedding(h["narrative"]))) for h in core.read_history(D)]
idx = search.Index(docs); stats = search.sensor_stats(docs)
table = alarm_rules.load(D / "alarm_rules.json")
print("| 각본 | 설비 | 증상군 | 알람 값 | 유사 기록 원인(상위 10) | 확률 | 첫 판정 |")
print("| --- | --- | --- | --- | --- | --- | --- |")
for s in json.loads((D / "demo/scenarios.json").read_text())["scenarios"]:
    hit = alarm_rules.detect(s["sensor_snapshot"], table); grp = hit["group"]
    qtext = search.query_text(GROUP_NAME[grp], hit["alarm"]["direction"], [])
    pool = [d for d in docs if d.symptom_group == grp]
    top = search.similar_records({"symptom_group": grp}, qtext, s["sensor_snapshot"], docs, idx.bm25,
                                 search.cosine_rank(fake_embedding(qtext), pool), stats)
    sim = [rules.Similar(t.record_id, t.cause, t.score) for t in top]
    st = session.fold(k, grp, sim, [{"type": "lock"}, {"type": "precheck_done"}])
    d = session.decide(st, k, g, mins)
    causes = {}
    for t in top: causes[t.cause] = causes.get(t.cause, 0) + 1
    probs = session.probabilities(st)
    a = hit["alarm"]
    print(f"| {s['scenario_id']} | {s['equipment_id']} | {grp} | {a['sensor']} {a['value']}{a['unit']} ({a['direction']} {a['boundary']}) | "
          f"{' · '.join(f'{c} {n}' for c, n in sorted(causes.items(), key=lambda x: str(x[0])))} | "
          f"{' · '.join(f'{c} {p}%' for c, p in probs.items())} | {d['kind']} {d.get('section')} ({d.get('grade')}){' ' + d['reason'] if d.get('reason') else ''} |")
