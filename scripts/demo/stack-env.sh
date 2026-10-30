# 시연 스택 이름별 칸(stack.sh · reload-manual.sh가 source) — 맥 절대 경로 0: 저장소 뿌리는 이 파일 자리로 셈.
#   real = 시연 앱(c1a15-demo-real · 정비자 8081 · 파트장 8082 · DB 55437 · 맥 배포 서버 8796 · 이 저장소 트리)
#   copy = 사본(c1a15-demo-copy · 18181 · 18182 · DB 55440 · deploy 사본 DEPLOY_PORT(기본 18796) · APP_TREE(기본 이 트리))
DEMO_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$DEMO_DIR/../.." && pwd)
case "${1:-}" in
  real)
    R=$REPO_ROOT; DP=8796; TECH_PORT=8081; LEAD_PORT=8082
    export COMPOSE_PROJECT_NAME=c1a15-demo-real COMPOSE_FILE=docker-compose.yml DB_HOST_PORT=55437 ;;
  copy)
    R=${APP_TREE:-$REPO_ROOT}; DP=${DEPLOY_PORT:-18796}; TECH_PORT=18181; LEAD_PORT=18182  # D-465: APP_TREE = 빌드할 작업 트리
    export COMPOSE_PROJECT_NAME=c1a15-demo-copy COMPOSE_FILE="docker-compose.yml:$DEMO_DIR/ports-copy.yml" DB_HOST_PORT=55440 ;;
  *) echo "스택 이름은 real | copy"; exit 1 ;;
esac
ST=${TMPDIR:-/tmp}/$COMPOSE_PROJECT_NAME
PORT=$TECH_PORT
