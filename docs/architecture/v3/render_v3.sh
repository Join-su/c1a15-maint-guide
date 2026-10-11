#!/bin/zsh
# v3 렌더: Chrome headless로 PNG(2배) · PDF · 검사 결과(?qa, --dump-dom) 생성. 임시 프로필은 v3/.chrome-tmp 에 두고 끝나면 지움.
set -e
cd "${0:A:h}"
C="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
U="--user-data-dir=$PWD/.chrome-tmp"
python3 build_architecture_v3.py
"$C" --headless=new --disable-gpu "$U" --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=1600,900 --screenshot="$PWD/시스템-아키텍처-v3.png" "file://$PWD/시스템-아키텍처-v3.html" 2>/dev/null
"$C" --headless=new --disable-gpu "$U" --no-pdf-header-footer \
  --print-to-pdf="$PWD/시스템-아키텍처-v3.pdf" "file://$PWD/시스템-아키텍처-v3.html" 2>/dev/null
"$C" --headless=new --disable-gpu "$U" --window-size=1600,900 --dump-dom "file://$PWD/시스템-아키텍처-v3.html?qa" 2>/dev/null \
  | python3 -c "import sys,re,html,json;m=re.search(r'<pre id=\"qa\" hidden=\"\">(.*?)</pre>',sys.stdin.read(),re.S);print(json.dumps(json.loads(html.unescape(m.group(1))),ensure_ascii=False,indent=1) if m else 'QA 없음')"
rm -rf .chrome-tmp
pdfinfo 시스템-아키텍처-v3.pdf | grep -E 'Pages|Page size'
sips -g pixelWidth -g pixelHeight 시스템-아키텍처-v3.png | tail -2
