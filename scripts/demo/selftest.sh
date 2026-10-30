#!/usr/bin/env bash
# 시연 스택 도구(scripts/demo) 자기 시험 — Docker · 스택 손 0(띄우지 않고 멈춤 길 · 꼴만 봄). check-fast가 부름.
#   1 쓰임 글에 backup · rebuild · rollback · up · down
#   2 모르는 스택 이름 · 상태 폴더 없음 → 멈춤(1)
#   3 인자 빠짐 → 멈춤: backup <폴더> · rollback <꼬리표> · ROLLBACK_TREE · 트리와 꼬리표 다름
#   4 up이 app_rev(되돌릴 꼬리표)를 남김
#   5 scripts/demo 안 사용자 홈 아래 절대 경로(맥 · 리눅스) 0
# 상태 폴더는 가짜 TMPDIR — 진짜 $TMPDIR/c1a15-demo-* 손 0.
set -u
H=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$H/../.." && pwd)
S="$H/stack.sh"
FAKE=$(mktemp -d "${TMPDIR:-/tmp}/demo-selftest.XXXXXX")
trap 'rm -rf "${FAKE:?}"' EXIT
fail=0
ok() { echo "○ $*"; }
no() { echo "× $*"; fail=1; }
run() { TMPDIR="$FAKE/" bash "$S" "$@" 2>&1; }

[ -f "$S" ] || { echo "× stack.sh 없음"; echo "demo selftest: FAIL"; exit 1; }
u=$(run 2>&1 || true)
for c in up backup rebuild rollback down; do echo "$u" | grep -q "^#   $c" && ok "쓰임에 $c" || no "쓰임에 $c 없음"; done
out=$(run prod up); [ $? -ne 0 ] && echo "$out" | grep -q "스택 이름" && ok "모르는 스택 이름 → 멈춤" || no "모르는 스택 이름 '$out'"

for k in real copy; do
  for c in "backup $FAKE/b" rebuild "rollback 88e0d06" info check; do
    out=$(ROLLBACK_TREE="$ROOT" run $k $c); rc=$?
    [ $rc -ne 0 ] && echo "$out" | grep -q "스택 없음" && ok "$k $c → 스택 없음 멈춤" || no "$k $c → rc=$rc '$out'"
  done
  st=c1a15-demo-$k
  mkdir -p "$FAKE/$st"; printf 'POSTGRES_PASSWORD=x\n' > "$FAKE/$st/stack.env"
  out=$(run $k backup); [ $? -ne 0 ] && echo "$out" | grep -q "백업 폴더" && ok "$k backup 폴더 빠짐 → 멈춤" || no "$k backup 폴더 빠짐 '$out'"
  out=$(run $k rollback); [ $? -ne 0 ] && echo "$out" | grep -q "꼬리표" && ok "$k rollback 꼬리표 빠짐 → 멈춤" || no "$k rollback 꼬리표 빠짐 '$out'"
  out=$(TMPDIR="$FAKE/" env -u ROLLBACK_TREE bash "$S" $k rollback 88e0d06 2>&1); [ $? -ne 0 ] && echo "$out" | grep -q "ROLLBACK_TREE" && ok "$k rollback 트리 빠짐 → 멈춤" || no "$k rollback 트리 빠짐 '$out'"
  out=$(ROLLBACK_TREE="$FAKE" run $k rollback 0000000); [ $? -ne 0 ] && echo "$out" | grep -q "아님" && ok "$k rollback 트리 · 꼬리표 다름 → 멈춤" || no "$k rollback 트리 · 꼬리표 다름 '$out'"
  rm -rf "${FAKE:?}/$st"
done

awk '/^  up\)/,/;;/' "$S" | grep -q 'app_rev' && ok "up → app_rev" || no "up이 app_rev를 남기지 않음"
HOME_PAT='/U''sers/|/h''ome/'  # 이 파일 자신이 걸리지 않게 낱말을 나눠 씀
hits=$(grep -rlE "$HOME_PAT" "$H" || true)
[ -z "$hits" ] && ok "scripts/demo 맥 절대 경로 0" || no "맥 절대 경로: $hits"

[ $fail -eq 0 ] && echo "demo selftest: pass" || { echo "demo selftest: FAIL"; exit 1; }
