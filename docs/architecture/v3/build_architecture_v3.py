"""아키텍처 그림 v3 생성 스크립트 — source/build_architecture.py 복사본에서 출력 경로를 v3/로 바꾸고, 명령서(C1-a15-아키텍처-그리기-명령.md) 3장의 구성 요소 · 연결 13개에 맞춤.
그림 우선 형식(기기 · 서버 랙 · 원통 DB · 구름 LLM · 공식 로고, 글은 이름만). 1600x900 SVG → 시스템-아키텍처-v3.html.
아이콘 · 로고는 ../source/icons, ../source/logos 를 읽기만 함. ?qa 로 열면 검사 결과를 숨은 <pre id="qa">에 씀."""
import pathlib, re
D = pathlib.Path(__file__).resolve().parent
SRC = D.parent / 'source'
LU = SRC / 'icons'
LG = SRC / 'logos'


def logo(name, x, y, s, color):
    """Simple Icons 로고를 (x,y)에 s 크기로."""
    p = (LG / f'{name}.svg').read_text()
    d = re.search(r' d="([^"]+)"', p).group(1)
    return f'<g transform="translate({x} {y}) scale({s / 24})"><path d="{d}" fill="{color}"/></g>'


def ic(name, x, y, s, color, sw=2):
    t = (LU / f'{name}.svg').read_text()
    inner = t[t.index('>', t.index('<svg')) + 1:t.rindex('</svg>')]
    inner = re.sub(r'<!--.*?-->', '', inner, flags=re.S)
    return f'<g transform="translate({x} {y}) scale({s / 24})" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{inner}</g>'


INK, SUB, MUT, LN = '#141a26', '#5b6475', '#8b93a3', '#e3e7ee'
PRI, OK, WARN = '#2457f5', '#0e9f6e', '#d97706'
G = []


def T(x, y, s, txt, w=700, c=INK, a='middle', cls=''):
    G.append(f'<text x="{x}" y="{y}" font-size="{s}" font-weight="{w}" fill="{c}" text-anchor="{a}" class="{cls}">{txt}</text>')


def name(x, y, n, sub=None):
    T(x, y, 20, n, 800)
    if sub:
        T(x, y + 22, 14, sub, 500, SUB)


# ── 영역 ──
G.append('<rect x="318" y="180" width="1122" height="508" rx="24" fill="#eef6fd" stroke="#b9dbf7" stroke-width="2"/>')
G.append(logo('docker', 340, 194, 30, '#2496ED'))
T(378, 216, 16, 'Docker Compose', 800, '#1d6fb8', 'start')
G.append('<rect x="40" y="712" width="1540" height="150" rx="20" fill="#f4f6f9" stroke="#d5dbe4" stroke-width="1.5" stroke-dasharray="7 6"/>')
T(62, 738, 15, '운영 밖에서 실행', 800, SUB, 'start')
for x, w in [(60, 520), (620, 488), (1180, 380)]:
    G.append(f'<rect x="{x}" y="750" width="{w}" height="104" rx="14" fill="#fff" stroke="#d5dbe4" stroke-width="1.5"/>')

# ── L1 정비자: 태블릿 ──
G.append('<rect x="62" y="206" width="176" height="120" rx="16" fill="#1f2937"/><rect x="74" y="216" width="152" height="100" rx="6" fill="#fff"/>')
G.append('<rect x="82" y="224" width="136" height="12" rx="3" fill="#fdf1de"/><rect x="82" y="242" width="88" height="8" rx="3" fill="#e3e7ee"/><rect x="82" y="256" width="110" height="8" rx="3" fill="#e3e7ee"/>')
G.append('<rect x="82" y="288" width="64" height="20" rx="5" fill="#d97706"/>')
G.append(logo('react', 172, 266, 38, '#149ECA'))
name(150, 356, '정비자', '설비 앞 태블릿 · 정비자 앱')
# ── L1 파트장: 모니터 ──
G.append('<rect x="62" y="398" width="176" height="110" rx="10" fill="#1f2937"/><rect x="72" y="406" width="156" height="92" rx="4" fill="#fff"/>')
G.append('<rect x="80" y="414" width="140" height="12" rx="3" fill="#fdf1de"/><rect x="80" y="434" width="70" height="40" rx="4" fill="#e3e7ee"/><rect x="156" y="434" width="64" height="18" rx="4" fill="#e3e7ee"/>')
G.append('<path d="M138 508 L132 528 H168 L162 508 Z" fill="#374151"/><rect x="118" y="526" width="64" height="7" rx="3" fill="#374151"/>')
G.append(logo('react', 176, 452, 34, '#149ECA'))
name(150, 560, '정비 파트장', '사무실 PC · 파트장 앱')

# ── L2 웹 서버: 랙 ──
G.append('<rect x="348" y="232" width="156" height="200" rx="14" fill="#fff" stroke="#c9d3e3" stroke-width="2"/>')
for i in range(3):
    y = 248 + i * 40
    G.append(f'<rect x="362" y="{y}" width="128" height="30" rx="6" fill="#f4f6f9" stroke="#e3e7ee"/><circle cx="374" cy="{y + 15}" r="4" fill="#0e9f6e"/><rect x="384" y="{y + 12}" width="56" height="6" rx="3" fill="#d5dbe4"/>')
G.append(logo('nginx', 404, 374, 44, '#009639'))
name(426, 462, '웹 서버', '앱 파일 · /api 중계')

# ── L2 알람 발생기 ──
G.append('<rect x="348" y="516" width="156" height="104" rx="14" fill="#fff" stroke="#c9d3e3" stroke-width="2"/>')
G.append(ic('sheet', 364, 540, 44, SUB, 1.8))
G.append(f'<path d="M414 562 H438" stroke="{INK}" stroke-width="2.5" marker-end="url(#ah)"/>')
G.append(ic('bell', 444, 536, 48, WARN, 2))
name(426, 648, '알람 발생기', 'AI4I CSV 행 → 알람')

# ── L3 API 서버 ──
G.append(f'<rect x="566" y="214" width="538" height="440" rx="20" fill="#fff" stroke="{PRI}" stroke-width="2.5"/>')
G.append(ic('server', 586, 226, 26, PRI, 2)); T(620, 246, 18, 'API 서버', 800, PRI, 'start'); T(706, 246, 13.5, '컨테이너 1개 · 프로세스 1개', 500, SUB, 'start')
# FastAPI 계층
G.append('<rect x="586" y="268" width="168" height="366" rx="16" fill="#f0faf8" stroke="#bfe6df" stroke-width="1.5"/>')
G.append(logo('fastapi', 632, 286, 76, '#009688'))
T(670, 392, 20, 'FastAPI', 800)
for i, (icn, t) in enumerate([('route', '라우터'), ('user-check', '로그인 · 역할'), ('braces', 'schema')]):
    y = 418 + i * 64
    G.append(f'<rect x="598" y="{y}" width="144" height="50" rx="10" fill="#fff" stroke="#d6eee9"/>')
    G.append(ic(icn, 610, y + 13, 24, '#009688', 2)); T(644, y + 31, 14.5, t, 700, INK, 'start')
# agent 패키지
G.append('<rect x="826" y="268" width="262" height="366" rx="16" fill="#eef3ff" stroke="#c4d3fb" stroke-width="1.5"/>')
G.append(logo('langgraph', 842, 282, 26, '#1C3C3C')); T(876, 302, 18, 'agent 패키지', 800, INK, 'start')
# 미니 LangGraph (HITL 승인 대기 노드)
ND = [(862, 372, 'n'), (918, 352, 'n'), (974, 372, 'n'), (1030, 352, 'p'), (1058, 404, 'n')]
for (x1, y1, _), (x2, y2, _) in zip(ND, ND[1:]):
    G.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#7c93d8" stroke-width="2.5"/>')
for x, y, k in ND:
    if k == 'p':
        G.append(f'<circle cx="{x}" cy="{y}" r="15" fill="#fdf1de" stroke="{WARN}" stroke-width="2.5"/><rect x="{x - 6}" y="{y - 6}" width="4" height="12" fill="{WARN}"/><rect x="{x + 2}" y="{y - 6}" width="4" height="12" fill="{WARN}"/>')
    else:
        G.append(f'<circle cx="{x}" cy="{y}" r="11" fill="#fff" stroke="{PRI}" stroke-width="2.5"/>')
T(1030, 328, 12.5, '승인 대기', 700, WARN)
for i, (icn, t, c) in enumerate([('lock', '잠금 확인', PRI), ('shield-check', '권한 등급', PRI), ('file-search', '근거 검사', PRI), ('search', '검색', PRI), ('sparkles', 'LLM Adapter', PRI), ('database', 'DB 접근', PRI)]):
    x = 836 + (i % 2) * 124; y = 432 + (i // 2) * 64
    G.append(f'<rect x="{x}" y="{y}" width="118" height="50" rx="10" fill="#fff" stroke="#d5def8"/>')
    G.append(ic(icn, x + 9, y + 14, 22, c, 2)); T(x + 35, y + 31, 12 if len(t) > 8 else 13.5, t, 700, INK, 'start')


# ── L4 DB 원통 ──
def cyl(x, y, w, h, col, light):
    ry = 18
    G.append(f'<path d="M{x} {y + ry} V{y + h - ry} A{w / 2} {ry} 0 0 0 {x + w} {y + h - ry} V{y + ry}" fill="{light}" stroke="{col}" stroke-width="2.5"/>')
    G.append(f'<ellipse cx="{x + w / 2}" cy="{y + ry}" rx="{w / 2}" ry="{ry}" fill="#fff" stroke="{col}" stroke-width="2.5"/>')


cyl(1188, 222, 196, 186, OK, '#e9f7f1')
G.append(logo('postgresql', 1232, 229, 22, '#4169E1')); T(1300, 246, 17, '운영 DB', 800, INK)
for i, (icn, t) in enumerate([('history', '세션 상태'), ('file-text', '보고서 · 승인'), ('scroll-text', '감사 로그'), ('shield-check', '권한 등급표')]):
    y = 270 + i * 32
    G.append(f'<rect x="1210" y="{y}" width="152" height="26" rx="6" fill="#fff" stroke="#bfe6d5"/>')
    G.append(ic(icn, 1218, y + 5, 16, OK, 2)); T(1242, y + 18, 12.5, t, 700, INK, 'start')
cyl(1188, 466, 196, 172, OK, '#e9f7f1')
G.append(logo('postgresql', 1226, 473, 22, '#4169E1')); T(1300, 490, 17, '벡터 DB', 800, INK)
SH = ['#0e9f6e', '#5bc79a', '#a6e3c9', '#2fb383', '#cdeee0', '#7fd3ae']
for i, (icn, t) in enumerate([('book-open', '매뉴얼 절'), ('history', '정비 이력'), ('file-check-2', '승인 보고서')]):
    y = 514 + i * 34
    G.append(f'<rect x="1206" y="{y}" width="160" height="28" rx="6" fill="#fff" stroke="#bfe6d5"/>')
    G.append(ic(icn, 1213, y + 6, 16, OK, 2)); T(1236, y + 19, 12.5, t, 700, INK, 'start')
    for k in range(5):
        G.append(f'<rect x="{1306 + k * 11}" y="{y + 8}" width="9" height="12" rx="2" fill="{SH[(i * 2 + k) % 6]}"/>')
T(1286, 628, 12, '원문 + 임베딩 벡터', 600, SUB)

# ── L5 외부 LLM: 구름 ──
G.append('<path d="M1488 352 H1572 A30 30 0 0 0 1566 294 A40 40 0 0 0 1494 276 A34 34 0 0 0 1462 322 A26 26 0 0 0 1488 352 Z" fill="#f4f6f9" stroke="#8b93a3" stroke-width="2.5"/>')
G.append(ic('sparkles', 1500, 292, 40, '#6b4fd8', 2))
T(1520, 232, 18, '외부 LLM API', 800); T(1520, 252, 12.5, '이후 sLLM으로 교체', 500, SUB)

# ── 아래 줄: 운영 외 작업 ──
G.append(ic('file-code', 76, 762, 50, WARN, 1.8))
for i, (n, c) in enumerate([('react', '#149ECA'), ('typescript', '#3178C6'), ('vite', '#646CFF')]):
    G.append(logo(n, 140 + i * 40, 774, 28, c))
T(80, 838, 17, '프론트엔드 코드', 800, INK, 'start'); T(232, 838, 13, '정비자 앱 · 파트장 앱 · 공통 UI 패키지', 500, SUB, 'start')
G.append(ic('flask-conical', 640, 762, 50, '#6b4fd8', 1.8))
for i in range(3):
    G.append(f'<rect x="{712 + i * 8}" y="{772 - i * 6}" width="60" height="40" rx="7" fill="#fff" stroke="#c9d3e3" stroke-width="1.5"/>')
T(756, 800, 18, '30', 800, '#6b4fd8')
T(640, 838, 17, '평가 실행기', 800, INK, 'start'); T(736, 838, 13, '분리 실행 · 평가 카드 30건 · API만 호출', 500, SUB, 'start')
for i in range(3):
    G.append(f'<rect x="{1198 + i * 7}" y="{770 - i * 5}" width="38" height="46" rx="6" fill="#fff" stroke="#c9d3e3" stroke-width="1.5"/>')
G.append(ic('file-text', 1216, 776, 24, SUB, 1.8))
G.append(f'<path d="M1258 790 H1290" stroke="{INK}" stroke-width="2.5" marker-end="url(#ah)"/>')
cyl(1296, 766, 50, 48, OK, '#e9f7f1')
T(1198, 838, 17, '데이터 적재 스크립트', 800, INK, 'start'); T(1366, 838, 13, '한 번 실행 · 300건', 500, SUB, 'start')

# ── 연결선 13개 (명령서 3장 표 순서) ──
A = []


def ar(cid, pts, lab, lp, dash=False, both=False, num=None, npos=None, a='middle'):
    """단방향은 시작점 검은 점, 양쪽(both)은 점 없이 양 끝 화살촉. lab의 '\\n'은 줄바꿈."""
    d = 'M' + ' L'.join(f'{x} {y}' for x, y in pts)
    pj = ';'.join(f'{x},{y}' for x, y in pts)
    A.append(f'<path class="w" data-id="{cid}" data-pts="{pj}" d="{d}" fill="none" stroke="{INK}" stroke-width="{2.2 if dash else 3}"{" stroke-dasharray=" + chr(34) + "7 6" + chr(34) if dash else ""} marker-end="url(#ah)"{" marker-start=" + chr(34) + "url(#as)" + chr(34) if both else ""}/>')
    if not both:
        A.append(f'<circle cx="{pts[0][0]}" cy="{pts[0][1]}" r="4.5" fill="{INK}"/>')
    for k, line in enumerate(lab.split('\n')):
        A.append(f'<text x="{lp[0]}" y="{lp[1] + k * 17}" font-size="13.5" font-weight="800" fill="{SUB}" text-anchor="{a}" class="lb" data-id="{cid}">{line}</text>')
    if num:
        A.append(f'<circle class="nb" cx="{npos[0]}" cy="{npos[1]}" r="14" fill="{PRI}" stroke="#fff" stroke-width="3"/><text x="{npos[0]}" y="{npos[1] + 5}" font-size="14" font-weight="800" fill="#fff" text-anchor="middle" class="nbt">{num}</text>')


ar(1, [(238, 266), (348, 266)], 'HTTP', (293, 256), both=True, num='1', npos=(293, 284))          # 정비자 ↔ 웹 서버
ar(2, [(238, 420), (348, 420)], 'HTTP', (293, 410), both=True)                                     # 파트장 ↔ 웹 서버
ar(3, [(504, 320), (586, 320)], '/api', (545, 308), both=True, num='2', npos=(545, 340))           # 웹 서버 ↔ FastAPI
ar(4, [(504, 584), (586, 584)], 'HTTP', (545, 572))                                                 # 알람 발생기 → FastAPI
ar(5, [(754, 372), (826, 372)], '함수 호출\n(import)', (790, 340), num='3', npos=(790, 398))       # FastAPI → agent
ar(6, [(1088, 330), (1188, 330)], 'SQL', (1138, 318), num='4', npos=(1138, 352))                   # agent → 운영 DB
ar(7, [(1088, 556), (1188, 556)], '검색 · 추가', (1138, 544))                                       # agent → 벡터 DB
ar(8, [(1060, 268), (1060, 152), (1446, 152), (1446, 318), (1462, 318)], 'HTTPS · 문장 생성 · 임베딩', (1250, 142), num='5', npos=(1060, 190))  # agent → 외부 LLM
ar(9, [(300, 750), (300, 500), (356, 500), (356, 432)], '빌드', (309, 706), dash=True, a='start')  # 프론트엔드 코드 → 웹 서버
ar(10, [(700, 750), (700, 654)], 'HTTP', (709, 706), dash=True, a='start')                         # 평가 실행기 → API 서버
ar(11, [(1286, 750), (1286, 638)], '적재', (1295, 706), dash=True, a='start')                      # 적재 스크립트 → 벡터 DB
ar(12, [(1420, 750), (1420, 300), (1384, 300)], '초기 등급표', (1429, 706), dash=True, a='start')  # 적재 스크립트 → 운영 DB
ar(13, [(1520, 750), (1520, 352)], '임베딩', (1529, 706), dash=True, a='start')                    # 적재 스크립트 → 외부 LLM

DEFS = (f'<defs><marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{INK}"/></marker>'
        f'<marker id="as" viewBox="0 0 10 10" refX="1.5" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M10 0 L0 5 L10 10 z" fill="{INK}"/></marker></defs>')
HEAD = (f'<text x="40" y="66" font-size="32" font-weight="800" fill="{INK}">정비 길잡이 시스템 아키텍처</text>'
        f'<circle cx="54" cy="104" r="12" fill="{PRI}"/><text x="54" y="109" font-size="13" font-weight="800" fill="#fff" text-anchor="middle">1</text>'
        f'<text x="72" y="109" font-size="15" font-weight="500" fill="{SUB}">→</text><circle cx="100" cy="104" r="12" fill="{PRI}"/><text x="100" y="109" font-size="13" font-weight="800" fill="#fff" text-anchor="middle">5</text>'
        f'<text x="122" y="109" font-size="15" font-weight="500" fill="{SUB}">정비자 요청 한 건</text>'
        f'<path d="M1180 60 H1222" stroke="{INK}" stroke-width="3" marker-end="url(#ah)"/><text x="1232" y="65" font-size="14" font-weight="600" fill="{SUB}">운영 중 호출</text>'
        f'<path d="M1340 60 H1382" stroke="{INK}" stroke-width="2.2" stroke-dasharray="7 6" marker-end="url(#ah)"/><text x="1392" y="65" font-size="14" font-weight="600" fill="{SUB}">한 번 · 분리 실행</text>'
        f'<text x="1580" y="109" font-size="13.5" font-weight="600" fill="{SUB}" text-anchor="end">앱은 브라우저에서 실행되고 DB에 직접 붙지 않음 · 모든 데이터는 nginx → API 서버를 거침</text>')
FOOT = (f'<text id="foot" x="1580" y="888" font-size="12.5" font-weight="500" fill="{MUT}" text-anchor="end">※ 기준: C1-a15 제안서 · 정비 길잡이 사용 가이드 v1.0 · 2026-10-09 결정'
        '(화면 React 앱 2개 + 공통 UI 패키지 · nginx가 앱 파일 제공과 /api 중계 · FastAPI가 agent 패키지를 import · DB 용도별 2개 · BM25는 agent 패키지 안)</text>')
FONT = "'Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif"
SVG = f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" font-family="{FONT}">{DEFS}<rect width="1600" height="900" fill="#fff"/>{HEAD}{"".join(G)}{"".join(A)}{FOOT}</svg>'

# 검사: 가이드 9장 1번 넘침 검사 + 선-글자 · 선-선 교차 + 캔버스 밖 글자. ?qa 로 열 때만 실행하고 결과를 숨은 <pre id="qa">에 씀(--dump-dom 으로 읽음).
QA = r"""<script>
if (location.search.indexOf('qa') >= 0) {
const R=[...document.querySelectorAll('svg rect')].map(r=>r.getBBox()).filter(r=>r.width<700);
const o=[];document.querySelectorAll('svg text').forEach(t=>{const b=t.getBBox();
 const c=R.filter(r=>b.x>=r.x-1&&b.y>=r.y-1&&b.x<=r.x+r.width&&b.y<=r.y+r.height&&b.y+b.height<=r.y+r.height+8);
 if(!c.length)return;c.sort((a,b)=>a.width*a.height-b.width*b.height);const r=c[0];
 if(b.x+b.width>r.x+r.width-3||b.y+b.height>r.y+r.height)o.push(t.textContent);});
const W=[...document.querySelectorAll('path.w')].map(p=>({id:p.dataset.id,pts:p.dataset.pts.split(';').map(s=>s.split(',').map(Number))}));
const S=[];W.forEach(w=>{for(let i=0;i<w.pts.length-1;i++)S.push({id:w.id,a:w.pts[i],b:w.pts[i+1]});});
const hit=(s,b,m)=>{const x1=Math.min(s.a[0],s.b[0])-1.5,x2=Math.max(s.a[0],s.b[0])+1.5,y1=Math.min(s.a[1],s.b[1])-1.5,y2=Math.max(s.a[1],s.b[1])+1.5;
 return x1<b.x+b.width-m&&x2>b.x+m&&y1<b.y+b.height-m&&y2>b.y+m;};
const lt=[];document.querySelectorAll('svg text').forEach(t=>{if(t.classList.contains('nbt'))return;const b=t.getBBox();S.forEach(s=>{if(hit(s,b,0))lt.push(s.id+' x '+t.textContent.slice(0,24));});});
const ll=[];for(let i=0;i<S.length;i++)for(let j=i+1;j<S.length;j++){const p=S[i],q=S[j];if(p.id===q.id)continue;
 const px1=Math.min(p.a[0],p.b[0]),px2=Math.max(p.a[0],p.b[0]),py1=Math.min(p.a[1],p.b[1]),py2=Math.max(p.a[1],p.b[1]);
 const qx1=Math.min(q.a[0],q.b[0]),qx2=Math.max(q.a[0],q.b[0]),qy1=Math.min(q.a[1],q.b[1]),qy2=Math.max(q.a[1],q.b[1]);
 if(px1<=qx2&&qx1<=px2&&py1<=qy2&&qy1<=py2)ll.push(p.id+' x '+q.id);}
const nb=[];document.querySelectorAll('circle.nb').forEach(c=>{const b=c.getBBox();document.querySelectorAll('svg text').forEach(t=>{if(t.classList.contains('nbt'))return;const tb=t.getBBox();
 if(b.x<tb.x+tb.width&&b.x+b.width>tb.x&&b.y<tb.y+tb.height&&b.y+b.height>tb.y)nb.push(t.textContent.slice(0,20));});});
const out=[];document.querySelectorAll('svg text').forEach(t=>{const b=t.getBBox();if(b.x<0||b.y<0||b.x+b.width>1600||b.y+b.height>900)out.push(t.textContent.slice(0,20));});
const BR=[...document.querySelectorAll('svg rect')].map(r=>r.getBBox()).filter(r=>r.width>=700&&r.width<1600);const bt=[];document.querySelectorAll('svg text').forEach(t=>{const b=t.getBBox();BR.forEach(r=>{const cx=e=>b.x<e&&b.x+b.width>e&&b.y+b.height>r.y&&b.y<r.y+r.height,cy=e=>b.y<e&&b.y+b.height>e&&b.x+b.width>r.x&&b.x<r.x+r.width;if(cx(r.x)||cx(r.x+r.width)||cy(r.y)||cy(r.y+r.height))bt.push(t.textContent.slice(0,20));});});
const f=document.getElementById('foot').getBBox();
const lb=[...document.querySelectorAll('text.lb')].map(t=>{const b=t.getBBox();return t.dataset.id+':'+t.textContent+' ['+Math.round(b.x)+','+Math.round(b.y)+','+Math.round(b.x+b.width)+','+Math.round(b.y+b.height)+']';});
const q=document.createElement('pre');q.id='qa';q.hidden=true;
q.textContent=JSON.stringify({overflow:o,wire_text:lt,wire_wire:ll,badge_text:nb,border_text:bt,outside:out,foot_x:[Math.round(f.x),Math.round(f.x+f.width)],wires:W.length,labels:lb,font:getComputedStyle(document.querySelector('svg text')).fontFamily});
document.body.appendChild(q);
}
</script>"""

html = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>정비 길잡이 시스템 아키텍처</title>'
        '<style>@page { size: 1600px 900px; margin: 0; } html,body{margin:0;background:#fff;font-family:' + FONT.replace("'", '"') + '} .pg{width:1600px;height:900px;overflow:hidden} '
        '.lb{paint-order:stroke;stroke:#fff;stroke-width:6px;stroke-linejoin:round}</style></head>'
        f'<body><div class="pg">{SVG}</div>{QA}</body></html>')
(D / '시스템-아키텍처-v3.html').write_text(html, encoding='utf-8')
print('ok')
