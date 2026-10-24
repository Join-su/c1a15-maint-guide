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


def r12_inbox(env=os.environ) -> str | None:
    """R12 받은 편지 폴더(EV-001 CH-23): C1A15_R12_INBOX — 없으면 None(쓰지 않음 = 지금 동작). 절대 경로만."""
    folder = env.get("C1A15_R12_INBOX", "")
    if not folder:
        return None
    if not os.path.isabs(folder):
        raise ConfigError(f"C1A15_R12_INBOX 는 절대 경로: {folder!r}")
    return folder


def pack_settings(env=os.environ, dockerenv: str = "/.dockerenv") -> dict:
    """Pack을 부르는 길(EV-001 CH-15): 판정 C1A15_JUDGE = inproc(기본) | deploy, 알람 C1A15_ALARM = boundary(기본) | ml.

    deploy 길은 배포 서버 주소 C1A15_DEPLOY_URL(맥 http://127.0.0.1:<port>만)이 필요하고, 컨테이너 안에서는 켜지 않는다
    (127.0.0.1이 컨테이너 자신 — 이 판의 deploy 길 앱 서버는 맥 host 직접 실행). ml 알람은 deploy 길에서만.
    어긋나면 ConfigError — 서버 시작을 거절한다.
    """
    from c1a15.deploy.client import check_url  # 주소 규칙 한 곳

    judge = env.get("C1A15_JUDGE", "") or "inproc"
    alarm = env.get("C1A15_ALARM", "") or "boundary"
    if judge not in ("inproc", "deploy"):
        raise ConfigError(f"C1A15_JUDGE 는 inproc | deploy: {judge!r}")
    if alarm not in ("boundary", "ml"):
        raise ConfigError(f"C1A15_ALARM 은 boundary | ml: {alarm!r}")
    if alarm == "ml" and judge != "deploy":
        raise ConfigError("C1A15_ALARM=ml 은 C1A15_JUDGE=deploy 에서만(앱 안 ML 길은 만들지 않음)")
    url = None
    if judge == "deploy":
        if os.path.exists(dockerenv):
            raise ConfigError("C1A15_JUDGE=deploy 는 맥 host 직접 실행에서만(컨테이너 안 127.0.0.1은 컨테이너 자신)")
        try:
            url = check_url(env.get("C1A15_DEPLOY_URL", ""))
        except ValueError as e:
            raise ConfigError(str(e)) from e
    return {"judge": judge, "alarm": alarm, "deploy_url": url}
