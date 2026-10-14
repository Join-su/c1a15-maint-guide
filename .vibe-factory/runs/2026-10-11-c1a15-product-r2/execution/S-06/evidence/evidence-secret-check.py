"""증거 폴더 비밀값 검사(G6-S02C2-2 B2): ① 저장소 secret_scan 패턴 ② 시험 비밀값 원문(이번 실행 env) ③ 비밀번호 칸 value
④ token_urlsafe(16) 꼴(22자) 문자열 목록(화면 상태 ID 꼴은 뺌) — 0건이어야 한다. 사용: python3 evidence_secret_check.py <evidence_dir> (env에 시험 비밀값)."""
import os, re, subprocess, sys
from pathlib import Path
root = Path(sys.argv[1]); repo = Path('/Users/insujo/Documents/repo/c1a15-maint-guide')
out = []
r = subprocess.run(['python3', str(repo / 'scripts/secret_scan.py'), str(root)], capture_output=True, text=True)
out.append(f'① secret_scan 패턴: {r.stdout.strip().splitlines()[-1]} (exit {r.returncode})')
vals = [os.environ[k] for k in ('POSTGRES_PASSWORD', 'C1A15_TECH_PASSWORD', 'C1A15_LEAD_PASSWORD', 'C1A15_INTERNAL_TOKEN') if os.environ.get(k)]
hits2, hits3, hits4 = [], [], []
STATE_ID = re.compile(r'^[A-Z]\d{2}--[a-z_]+$')  # 화면 상태 ID(T10--summary_corrected 등)는 구조 이름이라 뺀다(S-05)
tok = re.compile(r'(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{22}(?![A-Za-z0-9_-])')
for f in sorted(root.rglob('*')):
    if not f.is_file() or f.suffix in {'.png'}: continue
    t = f.read_text(encoding='utf-8', errors='ignore'); rel = f.relative_to(root)
    hits2 += [str(rel) for v in vals if v in t]
    hits3 += [str(rel) for m in re.finditer(r'<input[^>]*type="password"[^>]*>', t) if re.search(r'value="[^"]+"', m.group(0))]
    hits4 += [f'{rel}: {m.group(0)}' for m in tok.finditer(t) if re.search(r'\d', m.group(0)) and re.search(r'[A-Z]', m.group(0)) and re.search(r'[a-z]', m.group(0)) and not STATE_ID.match(m.group(0))]
out.append(f'② 시험 비밀값 원문(env {len(vals)}개): {len(hits2)}건 {hits2}')
out.append(f'③ 비밀번호 칸 value: {len(hits3)}건 {hits3}')
out.append(f'④ 22자 무작위 토큰 꼴: {len(hits4)}건 {hits4[:10]}')
print('\n'.join(out)); sys.exit(1 if (r.returncode or hits2 or hits3 or hits4) else 0)
