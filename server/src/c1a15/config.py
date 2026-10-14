"""실행 설정은 환경 변수로만 받는다. 비밀값(비밀번호 · 키)은 저장소에 두지 않는다(AC-36)."""

import os


class ConfigError(RuntimeError):
    pass


def require_env(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise ConfigError(f"환경 변수 {name} 가 필요합니다")
    return value


def database_url() -> str:
    return require_env("DATABASE_URL")
