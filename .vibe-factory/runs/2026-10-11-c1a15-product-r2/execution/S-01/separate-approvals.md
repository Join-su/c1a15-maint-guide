# S-01 별도 승인 기록 (2026-10-13)

PBC-4 authorization의 separate_approval_required_for 가운데 S-01에 필요한 세 가지를 실행 직전에 물었다. 사용자 답은 선택지 원문이다.

| 승인 대상 | 사용자 답 | 범위(질문에 함께 보인 문장) |
| --- | --- | --- |
| 패키지 설치 · Python 3.12 내려받기 | "허용 (권장)" | uv: Python 3.12 내려받기, fastapi · uvicorn · sqlalchemy · alembic · psycopg · pgvector · argon2-cffi · pytest · ruff. npm: react · react-dom · vite · @vitejs/plugin-react · typescript. 설치한 판은 uv.lock · package-lock.json에 고정. 환경은 저장소 안(.venv · node_modules)만, 전역 설치 없음. 다음 slice 패키지(LangGraph · Playwright 등)는 그때 다시 묻는다 |
| Docker image pull | "python:3.12-slim pull 허용 (권장)" | Docker Hub 공식 image 하나. image 안에서는 같은 uv.lock으로 설치 |
| 시험 컨테이너 실행 | "허용 (권장)" | 시험 DB(pgvector) · nginx(8081 · 8082) · API · 적재기. 포트는 127.0.0.1에만, API 포트는 밖에 열지 않음, 끝나면 compose down -v. 계정 비밀번호는 시험용 값을 환경 변수로만 |
| 추가 개발용 패키지 | "허용 (권장)" | @types/react · @types/react-dom(TypeScript 타입 검사), httpx(FastAPI TestClient). 개발 · 시험 의존성으로만, lock 파일에 고정 |
| uv 부트스트랩 설치(서버 image build의 `pip install uv==0.12.17`) | "1. uv 설치 승인"(2026-10-13, G6-S01 2차 비차단 의견에 대한 확인) | PyPI에서 uv 0.12.17 하나. image 안 패키지는 uv.lock으로만 |
