"""Prototype 구조 대조 차이 분류(S-05: S-02 ~ S-04 규칙 + I-6 · D-9 ~ D-13 · X-3 · X-4(Prototype 파생 상태 대조를 더하며), I-2 · I-4 · D-4 범위 넓힘, I-1은 뺌 — 지난 화면 pick을 S-05에서 연결): 규칙은 영역(region) · 차이 방향(+ 앱에만 / - template에만) · 줄 모양으로 좁게 건다.
분류된 줄 아래 더 깊은 자식 줄(b · span · li · div · svg · s)은 그 부모의 분류를 따른다. 남는 줄은 unclassified(= 구조 결함 후보)."""
import json, re, sys, collections
from html.parser import HTMLParser
rows = json.load(open(sys.argv[1])); DOM = sys.argv[3] if len(sys.argv) > 3 else None
# (id, 영역(None = 모두), 방향(None = 둘 다), 줄 패턴, 설명)
RULES = [
  ("I-2 입력 칸 textarea", None, None, r"(div\.memo(\.req|\.sm3)?|span\.cur|textarea\.memo(\.req|\.sm3)?)$", "Prototype의 contentEditable 메모 칸을 실제 입력 칸(textarea.memo)으로 — 같은 .memo 토큰"),
  ("I-3 입력 전 잠김 토큰", None, None, r"span\.btn(\.dis)?\.full\.lg$|span\.btn(\.dis)?\.warnb$", "보낼 것이 없거나(결과 · 로그인 칸 빈 상태) 다음 slice 화면(숙련자 인계, S-03)이면 승인 잠김 토큰 .dis"),
  ("D-1 홈 · 종 목록 항목 데이터", {"R-SHIFT", "R-ALARMS", "R-HOMEBG", "R-NOTIFY"}, None, r"(div\.rl|span\.amber\.ch|span\.ch\.green|span\.dot\.green|div\.grp|div\.nt-item|div\.al|div\.empty|svg\.ic\.lucide\.lucide-file-text)$", "홈 알람 · 최근 보고서 · 종 목록의 항목 수와 상태 점 · 칩은 그 시점 데이터(S-02는 기록이 없어 빈 목록, S-04는 반려 · 답 · 진행 중 세션 수에 따름 — AC-17-C2)"),
  ("R-1 잠금 전 가린 자리", {"R-MASK"}, "-", r"(ol\.proc|^\d+:li)$", "R1: 잠금 전에는 지시 내용을 내려받지 않으므로 가린 자리는 내용 없는 줄(개수는 모름)"),
  ("I-4 근거 기록 번호 누름 자리", {"R-INSTR", "R-BG", "R-PASTVIEW"}, "+", r"^[23]:span$|^[34]:span$", "'근거 H-… · H-…'의 기록 번호마다 누르는 자리(span) — 같은 .lk 안(앱 DOM에서 .refs .lk 안 span으로 확인)"),
  ("D-3 종 숫자 값", {"R-TOP"}, None, r"^2:i$", "종 숫자 = 지금 배정된 새 알람 수(AC-13). 세션을 연 알람은 진행 중이라 세지 않는다 — Prototype 예시 화면의 '1'은 예시 값"),
  ("D-4 점검 경로 줄 수 · 점 색", {"R-PATH"}, None, r"^0:div\.((ok|bad|now)\.tli|tli\.void)$", "점검 경로 줄 = 그 세션의 업무 기록(점검 수 · 결과 · 확인 불가 반복은 데이터, AC-17-C2) — 줄 구조(tt · td · b · span)는 template과 같음"),
  ("I-5 파트장 입력 칸 textarea", {"R-DECISION", "R-CALLS", "R-REPORTVIEW"}, None, r"(div\.memo\.sm3|textarea\.memo\.sm3|span\.edit-in\.rv2|textarea\.edit-in\.rv2)$", "Prototype의 contentEditable 메모 · 고치는 행을 실제 입력 칸(textarea)으로 — 같은 .memo · .edit-in 토큰(S-02 I-2와 같은 처리)"),
  ("D-5 목록 · 표 행 수 · 순서 · 상태 칩(데이터)", {"R-TABLE", "R-CALLS", "R-AUDIT", "R-ALARMS", "R-SHIFT", "R-HOMEBG", "R-NOTIFY"}, None, r"^\d+:(tr(\.\w+)?|td|div\.al|div\.al-m|div\.rl|div\.nt-item|span\.amber\.ch|span\.ch\.(red|green)|span\.(amber|green|red)\.dot|span\.dot\.(green|red|amber)|span\.btn\.ghost(\.sm2)?|span\.amber\.ch)$", "승인 대기 · 호출 · 감사 · 홈 알람 · 최근 보고서 · 종 목록의 행 수 · 행 순서 · 행 상태 칩/점은 그 시점 데이터(AC-17-C2) — 행 구조(td · b · span · 버튼)는 template과 같음"),
  ("D-6 권한 등급 표 행 수(결정 018 ②)", {"R-GRADES"}, "+", r"^\d+:(tr|td(\.pos-r)?|b|span\.g[A-D]\.gb|svg\.ic\.lucide\.lucide-arrow-right\.rot)$", "등급표에 있는 절 전부(사용자 결정 018 ②, 시제품 예시는 7절) — 늘어난 행은 같은 행 구조"),
  ("D-7 현재 알람 표시줄(데이터)", {"R-TOP"}, None, r"^0:div(\.muted)?\.tb-ctx$|^1:span\.dot\.red$", "진행 중인 알람이 있으면 표시줄에 그 알람, 없으면 '진행 중인 알람 없음'(T02 / rejected 예시는 진행 중 알람 없음 — 반려되면 그 세션이 진행 중으로 돌아감)"),
  ("D-8 종 목록 뒤 홈의 반려 배너(데이터)", {"R-HOMEBG"}, "+", r"^\d+:(div\.bad\.banner|svg\.ic\.lucide\.lucide-rotate-ccw|div|b|span\.btn\.full\.ghost)$", "종 목록(T12 / list)을 연 홈에 반려된 보고서가 있으면 T02 / rejected와 같은 반려 사유 배너 · '이어서 하기'가 뒤에 보인다(4종류를 모두 만든 시험 상태)"),
  ("X-1 결정 018 ③ 직접 확인 처리 결과 뒤 보고서 작성", {"R-CALLACT"}, None, r"^0:span\.note$|^0:span\.btn\.full\.lg$|^1:svg\.ic\.lucide\.lucide-file-text$", "직접 확인 답(처리 메모)이 오면 답 대기 안내(note) 자리에 '보고서 작성' 버튼(사용자 결정 018 ③, 부록 v2 derived_states) — T10 / ans_direct에만"),
  ("X-2 결정 018 ④ · 7 인계 보냄 · 답 대기", {"R-STOP"}, None, r"^0:div\.banner\.info$|^1:svg\.ic\.lucide\.lucide-send$|^0:span\.btn\.full\.lg\.warnb$|^1:svg\.ic\.lucide\.lucide-phone-call$|^0:span\.note$", "숙련자 인계를 보내면 T11 같은 틀에서 '인계 보내기' 버튼 자리가 보냄 배너 · 답 대기 안내로 바뀜(사용자 결정 018 ④ · 7 정정, 부록 v2 derived_states) — T11 / handover_sent에만"),
  ("I-6 끝 기록의 이전 · 다음 잠김", {"R-PASTBAR"}, None, r"^1:span\.btn(\.dis)?\.ghost\.sm2$", "첫 · 마지막 기록에서는 넘길 기록이 없어 '이전' · '다음'에 승인 잠김 토큰 .dis(I-3과 같은 처리) — 버튼 자리 · 순서는 template 그대로"),
  ("D-9 보내지 않은 입력 '그대로' 칩(데이터)", {"R-PASTBAR", "R-CORRECT"}, "+", r"^0:span\.amber\.ch$", "지금 지시에 보내지 않은 입력(기기)이 있으면 띠에 '지금 n.n 입력(보내지 않음)은 그대로' 칩(T15 / check_current · correct와 같은 칩) — 없으면 없음"),
  ("D-10 진행 표시 현재 단계(세션 데이터)", {"R-STEP"}, None, r"^\d+:(div\.(done\.pick\.sp(\.view)?|on\.sp|sp)|span\.(done\.)?spl|span\.spn|svg\.ic\.lucide\.lucide-check)$", "진행 표시의 현재 단계 · 완료 단계 수는 그 세션이 지금 어디에 있느냐(데이터) — 지난 화면은 어느 단계에서나 열 수 있다(template 예시는 조치 단계)"),
  ("D-11 정정 이력(데이터)", {"R-PASTVIEW"}, "+", r"^\d+:(span\.amber\.ch|div\.corr-list|span\.ch\.gray)$", "(G6-S05 비차단 ①로 좁힘: 정정 이력 요소 자체만 — 그 안의 div · span.tt · s · b는 부모를 따름) 그 기록이 정정됐으면 '정정 n회' 칩 · 이전 값 목록(T15 / corrected와 같은 구조), 정정으로 무효면 회색 칩 — 기록마다 데이터"),
  ("D-12 지금까지 점검 · 조치 줄(데이터)", {"R-CALLHEAD"}, None, r"^\d+:(span|svg\.(bad\.|ok\.|na\.)?ic\.lucide\.lucide-circle-(alert|check|help)(\.ok|\.bad|\.na)?)$", "정정 호출 요약의 지금까지 점검 · 조치 줄 수와 결과 아이콘은 그 세션 기록(데이터) — 줄 구조는 template과 같음"),
  ("D-13 그때 등급 배지(데이터)", {"R-PASTVIEW"}, None, r"^\d+:span\.g[A-D]\.gb$", "지난 화면 지시 카드의 등급 배지 = 그 기록을 지시할 때의 등급(B 점검 기록이면 B) — T15 / check_b template은 T15 / check 예시의 'A' 배지를 그대로 둠(같은 배지 자리 · 토큰, 값만 다름)"),
  ("X-3 호출 기록에 붙은 정정 상자(데이터)", {"R-PASTVIEW"}, "+", r"^2:div\.corr-box$", "보낸 호출에 정정이 붙으면(AC-47-C2 · 결정 019 ②) 지난 화면 호출 기록에 '보낸 뒤 정비자 정정' 상자 — 부록 T15 / call 파생 규칙의 값 '붙은 정정 수'를 보이는 자리, 구조는 부록 L04 / call_corrected template의 .corr-box와 같음(차이 0). template 예시는 붙은 정정 0 — T15 / call에만"),
  ("X-4 측정값 정정 창 뒤 화면 = 그 기록", {"R-PASTVIEW"}, None, r".", "측정값 정정 창은 사전 확인 기록의 지난 화면에서 연다 — 창 뒤 화면은 정정하는 그 기록(T15 / precheck). 부록 T15 / correct_value template은 창만 바꾸고 뒤 화면은 T15 / correct(4.3 점검 기록) 예시를 그대로 둠. 앱 영역 = 부록 T15 / precheck template 영역(차이 0, alt_compare) — T15 / correct_value에만, alt_compare 차이 0일 때만"),
  ("D-2 데이터 값 차이", {"R-INSTR", "R-BG"}, None, r"(^\d+:li$|span\.lk$|div\.banner\.warn$)", "절차 단계 수 · 근거 기록 유무 · 앞선 확인 불가 배너는 세션 데이터(Prototype 예시 값 아님, AC-17-C2)"),
]
def lk_has_span(key):
    if not DOM: return False
    s = open(f"{DOM}/{key}.html").read()
    i = s.find('class="refs"'); return i >= 0 and '<span role="button"' in s[i:i + 3000]
X_STATES = {"X-1": {"T10--ans_direct", "T10--corrected_ans_direct"}, "X-2": {"T11--handover_sent"}, "X-3": {"T15--call"}, "X-4": {"T15--correct_value"}}
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
                if name.startswith("X-") and key not in X_STATES[name[:3]]:
                    continue
                if name.startswith("X-4") and (r.get("alt_compare") or {}).get("diff") != []:
                    continue
                hit = name; break
        while stack and stack[-1][0] >= depth:
            stack.pop()
        if hit is None and stack and stack[-1][2] == sign and re.search(r":(b|span|li|div|svg|s)(\.|$)", ln):
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
