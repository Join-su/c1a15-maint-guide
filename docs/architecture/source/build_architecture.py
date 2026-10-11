"""아키텍처 그림 생성 스크립트 — 그림 우선 형식(기기 · 서버 랙 · 원통 DB · 구름 LLM · 공식 로고, 글은 이름만). 1600x900 SVG → architecture.html. 규칙은 ../아키텍처-그림-작성-가이드.md"""
import pathlib, re
D = pathlib.Path(__file__).resolve().parent
LU = D / 'icons'
LG = D / 'logos'


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

# ── 정비자: 태블릿 ──
G.append('<rect x="62" y="206" width="176" height="120" rx="16" fill="#1f2937"/><rect x="74" y="216" width="152" height="100" rx="6" fill="#fff"/>')
G.append('<rect x="82" y="224" width="136" height="12" rx="3" fill="#fdf1de"/><rect x="82" y="242" width="88" height="8" rx="3" fill="#e3e7ee"/><rect x="82" y="256" width="110" height="8" rx="3" fill="#e3e7ee"/>')
G.append('<rect x="82" y="288" width="64" height="20" rx="5" fill="#d97706"/>')
G.append(logo('react', 172, 266, 38, '#149ECA'))
name(150, 356, '정비자', '설비 앞 태블릿')
# ── 파트장: 모니터 ──
G.append('<rect x="62" y="398" width="176" height="110" rx="10" fill="#1f2937"/><rect x="72" y="406" width="156" height="92" rx="4" fill="#fff"/>')
G.append('<rect x="80" y="414" width="140" height="12" rx="3" fill="#fdf1de"/><rect x="80" y="434" width="70" height="40" rx="4" fill="#e3e7ee"/><rect x="156" y="434" width="64" height="18" rx="4" fill="#e3e7ee"/>')
G.append('<path d="M138 508 L132 528 H168 L162 508 Z" fill="#374151"/><rect x="118" y="526" width="64" height="7" rx="3" fill="#374151"/>')
G.append(logo('react', 176, 452, 34, '#149ECA'))
name(150, 560, '정비 파트장', '사무실 PC')

# ── 웹 서버: 랙 ──
G.append('<rect x="378" y="232" width="156" height="200" rx="14" fill="#fff" stroke="#c9d3e3" stroke-width="2"/>')
for i in range(3):
    y = 248 + i * 40
    G.append(f'<rect x="392" y="{y}" width="128" height="30" rx="6" fill="#f4f6f9" stroke="#e3e7ee"/><circle cx="404" cy="{y + 15}" r="4" fill="#0e9f6e"/><rect x="414" y="{y + 12}" width="56" height="6" rx="3" fill="#d5dbe4"/>')
G.append(logo('nginx', 434, 374, 44, '#009639'))
name(456, 462, '웹 서버', '앱 파일 · /api 중계')

# ── 알람 발생기 ──
G.append('<rect x="378" y="532" width="156" height="104" rx="14" fill="#fff" stroke="#c9d3e3" stroke-width="2"/>')
G.append(ic('sheet', 394, 556, 44, SUB, 1.8))
G.append(f'<path d="M444 578 H468" stroke="{INK}" stroke-width="2.5" marker-end="url(#ah)"/>')
G.append(ic('bell', 474, 552, 48, WARN, 2))
name(456, 664, '알람 발생기', 'CSV 행 → 알람')

# ── API 서버 ──
G.append(f'<rect x="596" y="214" width="508" height="440" rx="20" fill="#fff" stroke="{PRI}" stroke-width="2.5"/>')
G.append(ic('server', 616, 226, 26, PRI, 2)); T(650, 246, 18, 'API 서버', 800, PRI, 'start'); T(736, 246, 13.5, '컨테이너 1개', 500, SUB, 'start')
# FastAPI
G.append('<rect x="616" y="268" width="168" height="366" rx="16" fill="#f0faf8" stroke="#bfe6df" stroke-width="1.5"/>')
G.append(logo('fastapi', 662, 286, 76, '#009688'))
T(700, 392, 20, 'FastAPI', 800)
for i, (icn, t) in enumerate([('route', '라우터'), ('user-check', '로그인 · 역할'), ('braces', 'schema')]):
    y = 418 + i * 64
    G.append(f'<rect x="628" y="{y}" width="144" height="50" rx="10" fill="#fff" stroke="#d6eee9"/>')
    G.append(ic(icn, 640, y + 13, 24, '#009688', 2)); T(674, y + 31, 14.5, t, 700, INK, 'start')
# agent
G.append('<rect x="826" y="268" width="262" height="366" rx="16" fill="#eef3ff" stroke="#c4d3fb" stroke-width="1.5"/>')
G.append(logo('langgraph', 842, 282, 26, '#1C3C3C')); T(876, 302, 18, 'agent 패키지', 800, INK, 'start')
# 미니 LangGraph
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


# ── DB 원통 ──
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

# ── 외부 LLM: 구름 ──
G.append('<path d="M1488 352 H1572 A30 30 0 0 0 1566 294 A40 40 0 0 0 1494 276 A34 34 0 0 0 1462 322 A26 26 0 0 0 1488 352 Z" fill="#f4f6f9" stroke="#8b93a3" stroke-width="2.5"/>')
G.append(ic('sparkles', 1500, 292, 40, '#6b4fd8', 2))
T(1520, 232, 18, '외부 LLM API', 800); T(1520, 252, 12.5, '이후 sLLM으로 교체', 500, SUB)

# ── 아래 띠 ──
G.append(ic('file-code', 76, 762, 50, WARN, 1.8))
for i, (n, c) in enumerate([('react', '#149ECA'), ('typescript', '#3178C6'), ('vite', '#646CFF')]):
    G.append(logo(n, 140 + i * 40, 774, 28, c))
T(80, 838, 17, '프론트엔드 코드', 800, INK, 'start'); T(232, 838, 13, '정비자 앱 · 파트장 앱 · 공통 UI', 500, SUB, 'start')
G.append(ic('flask-conical', 640, 762, 50, '#6b4fd8', 1.8))
for i in range(3):
    G.append(f'<rect x="{712 + i * 8}" y="{772 - i * 6}" width="60" height="40" rx="7" fill="#fff" stroke="#c9d3e3" stroke-width="1.5"/>')
T(756, 800, 18, '30', 800, '#6b4fd8')
T(640, 838, 17, '평가 실행기', 800, INK, 'start'); T(736, 838, 13, '평가 카드 30건 · API만 호출', 500, SUB, 'start')
for i in range(3):
    G.append(f'<rect x="{1198 + i * 7}" y="{770 - i * 5}" width="38" height="46" rx="6" fill="#fff" stroke="#c9d3e3" stroke-width="1.5"/>')
G.append(ic('file-text', 1216, 776, 24, SUB, 1.8))
G.append(f'<path d="M1258 790 H1290" stroke="{INK}" stroke-width="2.5" marker-end="url(#ah)"/>')
cyl(1296, 766, 50, 48, OK, '#e9f7f1')
T(1198, 838, 17, '데이터 적재 스크립트', 800, INK, 'start'); T(1366, 838, 13, '한 번 실행', 500, SUB, 'start')

# ── 연결선 ──
A = []


def ar(pts, lab=None, lp=None, dash=False, both=False, num=None, npos=None, dot=False):
    d = 'M' + ' L'.join(f'{x} {y}' for x, y in pts)
    A.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{2.2 if dash else 3}"{" stroke-dasharray=" + chr(34) + "7 6" + chr(34) if dash else ""} marker-end="url(#ah)"{" marker-start=" + chr(34) + "url(#as)" + chr(34) if both else ""}/>')
    if dot:
        A.append(f'<circle cx="{pts[0][0]}" cy="{pts[0][1]}" r="4.5" fill="{INK}"/>')
    if lab:
        A.append(f'<text x="{lp[0]}" y="{lp[1]}" font-size="13.5" font-weight="800" fill="{SUB}" text-anchor="middle" class="lb">{lab}</text>')
    if num:
        A.append(f'<circle cx="{npos[0]}" cy="{npos[1]}" r="14" fill="{PRI}" stroke="#fff" stroke-width="3"/><text x="{npos[0]}" y="{npos[1] + 5}" font-size="14" font-weight="800" fill="#fff" text-anchor="middle">{num}</text>')


ar([(238, 266), (378, 266)], 'HTTP', (308, 256), both=True, num='1', npos=(308, 284))
ar([(238, 420), (378, 420)], 'HTTP', (308, 410), both=True)
ar([(534, 320), (616, 320)], '/api', (575, 308), both=True, num='2', npos=(575, 340))
ar([(534, 584), (616, 584)], 'HTTP', (575, 572), dot=True)
ar([(784, 372), (826, 372)], 'import', (805, 400), dot=True, num='3', npos=(805, 346))
ar([(1088, 330), (1188, 330)], 'SQL', (1138, 318), dot=True, num='4', npos=(1138, 352))
ar([(1088, 556), (1188, 556)], '검색 · 추가', (1138, 544), both=True)
ar([(1060, 268), (1060, 152), (1446, 152), (1446, 318), (1462, 318)], 'HTTPS · 문장 생성 · 임베딩', (1250, 142), dot=True, num='5', npos=(1060, 190))
ar([(300, 750), (300, 500), (386, 500), (386, 432)], '빌드', (330, 712), dash=True, dot=True)
ar([(700, 750), (700, 634)], 'HTTP', (726, 700), dash=True, dot=True)
ar([(1286, 750), (1286, 638)], '적재', (1310, 700), dash=True, dot=True)
ar([(1420, 750), (1420, 300), (1384, 300)], None, dash=True, dot=True)
ar([(1520, 750), (1520, 352)], '임베딩', (1550, 560), dash=True, dot=True)

DEFS = (f'<defs><marker id="ah" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{INK}"/></marker>'
        f'<marker id="as" viewBox="0 0 10 10" refX="1.5" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M10 0 L0 5 L10 10 z" fill="{INK}"/></marker></defs>')
HEAD = (f'<text x="40" y="66" font-size="32" font-weight="800" fill="{INK}">정비 길잡이 시스템 아키텍처</text>'
        f'<circle cx="54" cy="104" r="12" fill="{PRI}"/><text x="54" y="109" font-size="13" font-weight="800" fill="#fff" text-anchor="middle">1</text>'
        f'<text x="72" y="109" font-size="15" font-weight="500" fill="{SUB}">→</text><circle cx="100" cy="104" r="12" fill="{PRI}"/><text x="100" y="109" font-size="13" font-weight="800" fill="#fff" text-anchor="middle">5</text>'
        f'<text x="122" y="109" font-size="15" font-weight="500" fill="{SUB}">점검 결과를 입력했을 때 요청이 지나는 순서</text>'
        f'<path d="M1180 60 H1222" stroke="{INK}" stroke-width="3" marker-end="url(#ah)"/><text x="1232" y="65" font-size="14" font-weight="600" fill="{SUB}">운영 중 호출</text>'
        f'<path d="M1340 60 H1382" stroke="{INK}" stroke-width="2.2" stroke-dasharray="7 6" marker-end="url(#ah)"/><text x="1392" y="65" font-size="14" font-weight="600" fill="{SUB}">한 번 · 분리 실행</text>')
FOOT = f'<text x="1580" y="888" font-size="12.5" font-weight="500" fill="{MUT}" text-anchor="end">앱은 DB에 직접 붙지 않고 모든 데이터는 nginx → API 서버를 거침 · 기준: C1-a15 제안서 · 정비 길잡이 사용 가이드 v1.0 · 2026-10-09 결정</text>'
SVG = f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" font-family="Noto Sans KR, Apple SD Gothic Neo, sans-serif">{DEFS}<rect width="1600" height="900" fill="#fff"/>{HEAD}{"".join(G)}{"".join(A)}{FOOT}</svg>'
html = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>정비 길잡이 시스템 아키텍처</title>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@500;600;700;800&display=swap">'
        '<style>html,body{margin:0;background:#fff} .pg{width:1600px;height:900px} .lb{paint-order:stroke;stroke:#fff;stroke-width:6px;stroke-linejoin:round}</style></head>'
        f'<body><div class="pg">{SVG}</div></body></html>')
(D / 'architecture.html').write_text(html, encoding='utf-8')
print('ok')
