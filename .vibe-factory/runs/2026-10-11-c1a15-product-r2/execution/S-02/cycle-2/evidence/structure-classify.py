"""Prototype 구조 대조 차이 분류: 규칙은 영역(region) · 차이 방향(+ 앱에만 / - template에만) · 줄 모양으로 좁게 건다.
분류된 줄 아래 더 깊은 자식 줄(b · span · li · div · svg)은 그 부모의 분류를 따른다. 남는 줄은 unclassified(= 구조 결함 후보)."""
import json, re, sys, collections
from html.parser import HTMLParser
rows = json.load(open(sys.argv[1])); DOM = sys.argv[3] if len(sys.argv) > 3 else None
# (id, 영역(None = 모두), 방향(None = 둘 다), 줄 패턴, 설명)
RULES = [
  ("I-1 진행 표시 pick", {"R-STEP"}, None, r"div\.done(\.pick)?\.sp$", "완료 단계의 지난 화면(T15)은 S-05(P-15)에서 연결 — 그 전에는 누를 수 있는 표시(pick)를 붙이지 않는다"),
  ("I-2 입력 칸 textarea", None, None, r"(div\.memo|span\.cur|textarea\.memo)$", "Prototype의 contentEditable 메모 칸을 실제 입력 칸(textarea.memo)으로 — 같은 .memo 토큰"),
  ("I-3 입력 전 잠김 토큰", None, None, r"span\.btn(\.dis)?\.full\.lg$|span\.btn(\.dis)?\.warnb$", "보낼 것이 없거나(결과 · 로그인 칸 빈 상태) 다음 slice 화면(숙련자 인계, S-03)이면 승인 잠김 토큰 .dis"),
  ("D-1 S-03 · S-04 데이터 없음", {"R-SHIFT", "R-ALARMS", "R-HOMEBG", "R-NOTIFY"}, None, r"(div\.rl|span\.amber\.ch|span\.ch\.green|span\.dot\.green|div\.grp|div\.nt-item|div\.al|div\.empty|svg\.ic\.lucide\.lucide-file-text)$", "보고서 · 완료 알람 · 호출 답 · 반려는 S-03(P-09 · P-10) · S-04(P-11 · P-12)에서 생긴다 — 그 전에는 빈 목록 안내"),
  ("R-1 잠금 전 가린 자리", {"R-MASK"}, "-", r"(ol\.proc|^\d+:li)$", "R1: 잠금 전에는 지시 내용을 내려받지 않으므로 가린 자리는 내용 없는 줄(개수는 모름)"),
  ("I-4 근거 기록 번호 누름 자리", {"R-INSTR", "R-BG"}, "+", r"^[23]:span$|^[34]:span$", "'근거 H-… · H-…'의 기록 번호마다 누르는 자리(span) — 같은 .lk 안(앱 DOM에서 .refs .lk 안 span으로 확인)"),
  ("D-3 종 숫자 값", {"R-TOP"}, None, r"^2:i$", "종 숫자 = 지금 배정된 새 알람 수(AC-13). 세션을 연 알람은 진행 중이라 세지 않는다 — Prototype 예시 화면의 '1'은 예시 값"),
  ("D-2 데이터 값 차이", {"R-INSTR", "R-BG"}, None, r"(^\d+:li$|span\.lk$|div\.banner\.warn$)", "절차 단계 수 · 근거 기록 유무 · 앞선 확인 불가 배너는 세션 데이터(Prototype 예시 값 아님, AC-17-C2)"),
]
def lk_has_span(key):
    if not DOM: return False
    s = open(f"{DOM}/{key}.html").read()
    i = s.find('class="refs"'); return i >= 0 and '<span role="button"' in s[i:i + 3000]
out = []
for r in rows:
    if r["status"] != "diff":
        out.append({**r, "classes": []}); continue
    key = f"{r['page_id']}--{r['state']}"
    cats, unknown, stack = set(), [], []  # stack: 분류된 조상 줄 (깊이, 분류, 방향)
    for d in r["diff"]:
        sign, ln = d[0], d[2:]
        depth = int(ln.split(":", 1)[0])
        hit = None
        for name, regs, sg, pat, _ in RULES:
            if (regs is None or r["region_id"] in regs) and (sg is None or sg == sign) and re.search(pat, ln):
                if name.startswith("I-4") and not lk_has_span(key):
                    continue
                hit = name; break
        while stack and stack[-1][0] >= depth:
            stack.pop()
        if hit is None and stack and stack[-1][2] == sign and re.search(r":(b|span|li|div|svg)", ln):
            hit = stack[-1][1]
        if hit:
            cats.add(hit); stack.append((depth, hit, sign))
        else:
            unknown.append(d)
    out.append({**r, "classes": sorted(cats), "unclassified": unknown})
json.dump({"rules": [{"id": n, "regions": sorted(g) if g else "all", "sign": s or "±", "pattern": p, "explanation": e} for n, g, s, p, e in RULES], "regions": out}, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
c = collections.Counter(x["status"] for x in out); print(dict(c))
print("unclassified:", [(x["page_id"], x["state"], x["region_id"], x["unclassified"]) for x in out if x.get("unclassified")])
print(collections.Counter(cl for x in out for cl in x["classes"]))
