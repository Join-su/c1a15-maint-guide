"""응답 본문(OpenAPI 정본의 출력 스키마, P-19: 화면 값 API). 앱 타입은 이 정본에서 생성한다(EP-C1-APITYPE-001).

서버가 만든 값은 정해진 필드만(extra = forbid). 정비 이력 원본을 그대로 넘기는 객체(점검 경로 · 결과)는 extra = allow.
"""

from pydantic import BaseModel, ConfigDict


class _Out(BaseModel):
    model_config = ConfigDict(extra="forbid")


class _Passthrough(BaseModel):
    model_config = ConfigDict(extra="allow")


class TrendPoint(_Out):
    at: str
    value: int | float


class AlarmValue(_Out):
    sensor: str
    value: int | float
    unit: str
    boundary: int | float
    direction: str
    trend_title: str | None = None
    origin: str | None = None  # EV-009: "lead" = 경계 안 후보를 파트장이 올림
    crossed: bool | None = None


class Progress(_Out):
    check_no: int
    check_max: int


# ---------------------------------------------------------------- 홈 · 종(T02 · T12)


class AlarmMl(_Out):
    """D-546 U5 화면 칸: 알람 행에 저장한 Pack ML 값 중 예측 유형(확률 1위) · 위험도."""

    type: str | None
    type_name: str | None
    risk: float | None


class AlarmRow(_Out):
    alarm_id: int
    equipment_id: str
    symptom_group: str
    group_name: str
    system: str | None = None
    alarm: AlarmValue
    sensor_snapshot: dict[str, int | float]
    trend: list[TrendPoint]
    occurred_at: str
    status: str
    change_seq: int
    session_id: int | None
    progress: Progress | None
    report_status: str | None
    report_session_id: int | None
    ml: AlarmMl | None = None


class RecentReport(_Out):
    report_id: int
    session_id: int
    equipment_id: str
    system: str | None = None
    cause: str
    confirmed_at: str | None
    status: str
    reject_reason: str | None = None
    rejected_by_name: str | None = None
    rejected_at: str | None = None


class InProgress(_Out):
    session_id: int
    alarm_id: int
    progress: Progress


class Shift(_Out):
    label: str
    start: str
    end: str
    start_text: str
    end_text: str
    done: int
    in_progress: int
    calls: int


class ToolCaution(_Out):
    """D-546 U6 공구 교체 주의(알람 아님): 설비마다 확인 전 최근 값 하나."""

    caution_id: int
    equipment_id: str
    tool_wear_min: float
    at: str


class ToolCautionAck(_Out):
    caution_id: int
    equipment_id: str


class Home(_Out):
    alarms: list[AlarmRow]
    new_since: list[AlarmRow]
    in_progress: list[InProgress]
    change_seq: int
    shift: Shift
    recent_reports: list[RecentReport]
    cautions: list[ToolCaution]


class NotifyItem(_Out):
    kind: str
    alarm_id: int
    session_id: int | None = None
    equipment_id: str | None = None
    group_name: str | None = None
    occurred_at: str | None = None
    progress: Progress | None = None
    call_section: str | None = None
    call_title: str | None = None
    call_grade: str | None = None
    answer: str | None = None
    answered_by: str | None = None
    answered_by_name: str | None = None
    answered_at: str | None = None
    report_cause: str | None = None
    reject_reason: str | None = None
    rejected_by_name: str | None = None
    rejected_at: str | None = None


class Notifications(_Out):
    items: list[NotifyItem]
    empty: bool


# ---------------------------------------------------------------- 세션(T03 ~ T07)


class SensorRow(_Out):
    key: str
    name: str
    value: int | float
    unit: str
    value_text: str
    range_text: str
    status: str
    is_alarm_sensor: bool
    out_of_range: bool


class Reading(_Out):
    text: str
    fallback: bool
    label: str | None


class AlarmBlock(_Out):
    alarm_id: int
    equipment_id: str
    equipment_type: str
    occurred_at: str
    symptom_group: str
    group_name: str
    system: str
    alarm: AlarmValue
    boundary_text: str
    out_of_range_count: int
    trend: list[TrendPoint]
    trend_title: str | None
    sensors: list[SensorRow]
    ai_reading: Reading
    similar_count: int
    ml: AlarmMl | None = None


class RecordCard(_Out):
    record_id: str
    equipment_id: str
    month: int
    similarity_pct: int
    outcome_type: str
    cause_code: str | None
    outcome_label: str
    action_name: str
    downtime_min: int | float


class ResultRow(_Out):
    seq: int | None
    section: str | None
    value: str | None
    memo: str | None


class Step(_Out):
    kind: str | None
    section: str | None
    grade: str | None
    cause: str | None
    reason: str | None
    unable_before: int | None
    interpretation: str | None
    quote: str | None
    outcome: str | None
    call_status: str | None
    corrected: bool | None = None  # S-05: 조치 뒤 정정 호출(T10 / summary_corrected)


class PathEntry(_Out):
    at: str | None
    title: str
    detail: str
    status: str


class ActionBlock(_Out):
    cause_code: str
    cause_name: str
    evidence_record_ids: list[str]
    section: str
    title: str
    verb: str
    grade: str | None
    minutes: int | None
    done_at: str | None
    checklist: list[str]
    checklist_done: bool
    steps: list[str]  # 조치 절의 절차(매뉴얼 번호 줄 그대로 · D-530 답장 001-zzy)


class RestartValue(_Out):
    sensor: str
    value: int | float
    value_text: str
    boundary_text: str
    rule_text: str
    basis: str


class RestartBlock(_Out):
    section: str
    title: str
    grade: str | None
    checklist: list[str]
    restarted_at: str | None
    outcome: str | None
    value: RestartValue | None = None


class MonitorBlock(_Out):
    section: str
    title: str
    grade: str | None
    closed: bool


class CheckDone(_Out):
    section: str
    title: str
    value: str
    note: str | None = None  # 정정된 결과: '정정 n회, 원래 …'(T10 / summary_corrected)


class CallCorrection(_Out):
    """정정 호출을 연 정정(조치 뒤 결과 정정, AC-47-C1)."""

    section: str | None
    title: str | None
    before: str | None
    after: str | None
    reason: str | None
    at: str | None


class ActionDone(_Out):
    section: str
    title: str
    at: str | None


class Candidate(_Out):
    code: str
    name: str
    pct: int


class CallAnswer(_Out):
    answer: str | None
    by: str | None
    by_name: str | None
    at: str | None
    note: str | None


class ExceptionGuideNext(_Out):
    section: str
    title: str


class ExceptionGuideSource(_Out):
    """출처 한 줄 = 앱 원본(승인 이력)의 예외 상황 기록."""

    record_id: str
    equipment_id: str
    occurred_at: str
    situation: str


class ExceptionGuide(_Out):
    """D-543 예외 안내(호출 단계) = 약속 v8 결과 exception_guide 칸 그대로 + 출처(앱 원본) · 원래 순서 다음(null)."""

    section: str
    relation_id: str
    grade: str | None
    title: str | None
    text: str | None
    steps: list[str]
    criteria: str | None
    basis: list[str]
    source: ExceptionGuideSource | None
    next: ExceptionGuideNext | None


class CallBlock(_Out):
    kind: str
    reason: str | None
    head: str | None
    section: str | None
    title: str | None
    grade: str | None
    minutes: int | None
    checks_done: list[CheckDone]
    candidates: list[Candidate]
    summary: Reading
    status: str
    waiting_at: str | None
    sent_at: str | None
    answer: CallAnswer | None
    correction: CallCorrection | None = None
    actions_done: list[ActionDone] = []
    exception_guide: ExceptionGuide | None = None


class ReportField(_Out):
    key: str
    label: str
    source: str
    text: str
    edited: bool
    ok: bool
    unsupported_numbers: list[str]
    fallback: bool | None = None  # 원인 · 조치만: 원문으로 대체됨(EV-001 CH-21)


class ReportCheck(_Out):
    key: str
    label: str
    ok: bool


class Rejection(_Out):
    reason: str | None
    by: str | None
    by_name: str | None
    at: str | None


class ExceptionPrev(_Out):
    record_id: str
    occurred_at: str
    outcome: str | None  # 확정 원인, 없으면 결과 종류
    action: str | None


class ExceptionCheck(_Out):
    section: str
    title: str


class ExceptionContext(_Out):
    """D-538 자동 정보 여덟 — 데이터에 없는 칸은 null(지어내기 0)."""

    equipment_id: str
    symptom_group: dict[str, str]
    occurred_at: str
    sensor_values: dict
    previous_maintenance: ExceptionPrev | None
    ai_first_check: ExceptionCheck | None
    confirmed_cause: str
    report_id: int | None


class ExceptionDraft(_Out):
    """D-543 「노하우 등록」 초안 — 보고서 '예외 상황 기록' 칸에 채워짐."""

    situation: str
    action: str


class ExceptionNote(_Out):
    """D-543 참고 알림: 같은 설비 · 같은 증상군의 승인된 예외 상황 기록."""

    record_id: str
    occurred_at: str
    situation: str
    action: str


class ExceptionRecord(_Out):
    situation: str  # 어떤 상황이었나
    action: str  # 무엇을 했나
    context: ExceptionContext


class ReportBlock(_Out):
    status: str
    report_id: int | None = None
    rejection: Rejection | None = None
    fields: list[ReportField]
    checks: list[ReportCheck]
    messages: list[str]
    can_confirm: bool
    confirmed_at: str | None
    exception_record: ExceptionRecord | None = None  # D-538: 마지막 확정 때 함께 보낸 예외 상황 기록
    exception_draft: ExceptionDraft | None = None  # D-543: 「노하우 등록」 초안(마지막 확정 뒤)
    low_evidence: bool


class Correction(_Out):
    section: str
    title: str
    at: str | None
    before: str | None
    after: str | None


class LockInstruction(_Out):
    section: str
    title: str
    grade: str | None
    minutes: int | None
    steps: list[str]


class Unable(_Out):
    section: str
    title: str
    count: int


class Instruction(_Out):
    section: str
    title: str
    text: str
    checklist: list[str]
    checklist_done: bool
    checklist_common: bool
    grade: str | None
    minutes: int | None
    steps: list[str]
    fallback: bool
    fallback_label: str | None
    original: str | None
    criterion: str | None
    check_no: int
    check_max: int
    evidence_record_ids: list[str]
    unable: list[Unable]


class Preview(_Out):
    kind: str
    section: str | None
    grade: str | None
    cause: str | None
    title: str | None = None
    minutes: int | None = None
    call_reason: str | None = None
    reason: str | None = None
    reason_fallback: bool | None = None
    reason_label: str | None = None


class SessionView(_Out):
    session_id: int
    alarm_id: int
    status: str
    locked: bool
    lock_at: str | None
    alarm_ack_at: str | None = None  # EV-007: 알람 화면 확인 시각(없으면 잠금 거절)
    probabilities: dict[str, int]
    evidence: dict[str, int]
    low_evidence: bool
    top_records: list[str]
    similar_basis: str
    cause_names: dict[str, str]
    similar_cards: list[RecordCard]
    alarm: AlarmBlock
    results: list[ResultRow]
    step: Step
    last_seq: int
    recommend_handover: bool
    lock_instruction: LockInstruction | None = None
    instruction: Instruction | None = None
    path: list[PathEntry] = []
    action: ActionBlock | None = None
    restart: RestartBlock | None = None
    monitor: MonitorBlock | None = None
    call: CallBlock | None = None
    report: ReportBlock | None = None
    correction: Correction | None = None
    exception_draft: ExceptionDraft | None = None  # D-543 「노하우 등록」 초안
    exception_notes: list[ExceptionNote] = []  # D-543 참고 알림(같은 설비 · 같은 증상군 승인 예외 기록)


class SessionWithPreview(SessionView):
    preview: Preview


# ---------------------------------------------------------------- 과거 기록(T13)


class Approval(_Passthrough):
    status: str
    by: str | None = None
    at: str | None = None


class RecordStepOut(_Passthrough):
    kind: str
    name: str | None = None
    section: str | None = None
    result: str | None = None


class Record(_Out):
    record_id: str
    equipment_id: str
    equipment_type: str | None
    approval: Approval | None
    source: str
    provenance: str
    occurred_at: str
    symptom: dict
    alarm: dict
    sensor_snapshot: dict[str, int | float]
    steps: list[RecordStepOut]
    outcome: dict
    downtime_min: int | float
    narrative: str


# ---------------------------------------------------------------- 파트장 앱(L02 ~ L06, P-11)


class LeadTiles(_Out):
    awaiting: int
    calls_open: int
    violations: int


class LeadReportRow(_Out):
    report_id: int
    session_id: int
    equipment_id: str
    group_name: str
    cause: str
    author_name: str
    confirmed_at: str | None
    evidence_count: int
    low_evidence: bool
    violations: int


class LeadOverview(_Out):
    now: str
    tiles: LeadTiles
    rows: list[LeadReportRow]


class LeadField(_Out):
    key: str
    label: str
    text: str


class LeadReport(_Out):
    report_id: int
    session_id: int
    status: str
    equipment_id: str
    group_name: str
    occurred_at: str | None
    author_name: str
    low_evidence: bool
    fields: list[LeadField]
    violations: int


class FinalDecision(_Out):
    kind: str
    by_name: str
    at: str | None
    memo: str | None = None


class FinalSensor(_Out):
    name: str
    value_text: str
    range_text: str
    status: str
    out_of_range: bool


class FinalCause(_Out):
    name: str
    probability: int
    evidence: int
    result: str
    confirmed: bool


class FinalCauseBasis(_Out):
    section: str
    title: str
    value: str
    memo: str | None


class FinalStep(_Out):
    at: str
    who: str
    text: str
    section: str | None
    grade: str | None


class FinalReport(_Out):
    """보고서 최종본(D-528 · 부록 5): 구역 1 ~ 5 값 — 두 앱이 같은 문서 화면(FinalReport.tsx)으로 그린다."""

    report_id: int
    session_id: int
    status: str
    equipment_id: str
    equipment_type: str
    group_name: str
    occurred_at: str
    confirmed_at: str | None
    author_name: str
    author_role: str  # 작성 근무(가이드 20쪽 '(야간 정비)')
    lock_at: str | None
    rejected_before: bool
    decision: FinalDecision | None
    sensors: list[FinalSensor]
    sensor_evidence: str
    causes: list[FinalCause]
    cause: str
    cause_basis: FinalCauseBasis | None  # 확정 근거(가이드 20쪽) — 확정 원인 없으면 없음
    check_path: str
    evidence_records: str
    timeline: list[FinalStep]
    action: str
    restart: str | None
    downtime: str
    grade_use: dict[str, int]
    unresolved: str
    exception_record: ExceptionRecord | None  # D-538: 6. 예외 상황 기록(보기만)


class ExceptionRecordItem(_Out):
    record_id: str
    report_id: int
    approved_at: str | None
    exception_record: ExceptionRecord


class ExceptionRecordList(_Out):
    """D-538: 승인된 예외 상황 기록(정비 이력 원본 층) — LLMOps ⑥이 읽음."""

    items: list[ExceptionRecordItem]


class EditCheckField(_Out):
    key: str
    ok: bool
    unsupported_numbers: list[str]


class EditCheck(_Out):
    fields: list[EditCheckField]
    ok: bool
    messages: list[str]


class DecisionResult(_Out):
    status: str
    history_record_id: str | None = None


class LeadCallRow(_Out):
    call_id: int
    kind: str
    equipment_id: str
    group_name: str
    sent_at: str | None
    need: str
    sender_name: str


class LeadCalls(_Out):
    now: str
    rows: list[LeadCallRow]


class LeadSessionHold(_Out):
    kind: str
    label: str
    since: str | None
    minutes: int | None
    call_id: int | None


class LeadSessionRow(_Out):
    session_id: int
    alarm_id: int
    equipment_id: str
    group_code: str
    group_name: str
    technician_name: str
    stage: str
    stage_label: str
    step_no: int | None
    step_kind: str | None
    section: str | None
    section_title: str | None
    grade: str | None
    check_no: int
    check_max: int
    hold: LeadSessionHold | None
    alarm_at: str | None
    started_at: str | None
    last_input_at: str | None
    elapsed_min: int
    report_rejected: bool


class LeadSessions(_Out):
    now: str
    counts: dict[str, int]
    rows: list[LeadSessionRow]


class AnswerOption(_Out):
    value: str
    label: str
    hint: str


class LeadCall(_Out):
    call_id: int
    kind: str
    equipment_id: str
    group_name: str
    sent_at: str | None
    section: str | None
    grade: str | None
    summary: str
    sender_name: str | None = None
    options: list[AnswerOption]
    answered: bool
    answer: dict | None
    need: str
    corrections: list["CallCorrectionBox"] = []


class CallCorrectionBox(_Out):
    """L04 / call_corrected '보낸 뒤 정비자 정정' 상자 한 줄."""

    at: str | None
    section: str | None
    title: str | None
    before: dict | None
    after: dict | None
    reason: str | None


class AnswerResult(_Out):
    status: str
    answer: str


class GradeRow(_Out):
    section: str
    title: str
    grade: str
    label: str


class GradeChangeRow(_Out):
    section: str
    title: str
    before: str
    after: str
    by_name: str
    at: str | None


class LeadGrades(_Out):
    now: str
    total: int
    rows: list[GradeRow]
    changes: list[GradeChangeRow]


class GradeWarning(_Out):
    direction: str
    head: str
    body: str


class GradeResult(_Out):
    section: str
    before: str
    after: str


class AuditRow(_Out):
    audit_id: int
    at: str
    user_id: str | None
    user_name: str
    app: str
    action: str
    target: str
    equipment_id: str | None
    report_id: int | None = None  # D-528 승인 대기 '오늘 기록' 「보고서 보기」(보고서 확정 · 결정 행)


class AuditUser(_Out):
    user_id: str
    name: str


class AuditOptions(_Out):
    equipment: list[str]
    users: list[AuditUser]


class AuditFilters(_Out):
    equipment: str | None
    user_id: str | None


class LeadAudit(_Out):
    now: str
    date: str
    filters: AuditFilters
    options: AuditOptions
    rows: list[AuditRow]


# ---------------------------------------------------------------- S-05(P-14): 세션 단계 기록(T15 지난 화면)


class PastCorrection(_Out):
    at: str | None
    before: dict | None
    after: dict | None
    reason: str | None


class PastNote(_Out):
    at: str | None
    memo: str | None


class PastBox(_Out):
    """보낸 뒤 정비자 정정(호출 기록에 붙은 것)."""

    at: str | None
    section: str | None
    title: str | None
    before: dict | None
    after: dict | None
    reason: str | None


class PastRestart(_Out):
    section: str
    title: str
    grade: str | None
    at: str | None
    checklist: list[str]


class PastRecord(_Out):
    """지난 화면 한 장: 기록 종류와 그때 화면 값.

    종류 = alarm · diagnosis · lock · precheck · check · call · action · restart · monitor_close.
    정정 · 메모 덧붙이기 가능 여부 · 정정 이력 · 덧붙인 메모 · 무효는 서버가 정한다.
    """

    seq: int
    kind: str
    at: str | None
    band: str
    position: str
    void: bool
    correctable: bool
    notable: bool
    corrections: list[PastCorrection]
    notes: list[PastNote]
    section: str | None = None
    title: str | None = None
    grade: str | None = None
    minutes: int | None = None
    steps: list[str] | None = None
    record: str | None = None
    values: str | None = None
    lock_at: str | None = None
    criterion: str | None = None
    evidence_record_ids: list[str] | None = None
    check_no: int | None = None
    check_max: int | None = None
    value: str | None = None
    memo: str | None = None
    b_checklist: list[str] | None = None
    b_checklist_common: bool | None = None
    call_kind: str | None = None
    summary: str | None = None
    box: list[PastBox] | None = None
    cause_name: str | None = None
    restart: PastRestart | None = None
    checklist: list[str] | None = None
    alarm: AlarmBlock | None = None
    probabilities: dict[str, int] | None = None
    evidence: dict[str, int] | None = None
    cause_names: dict[str, str] | None = None
    similar_cards: list[RecordCard] | None = None
    low_evidence: bool | None = None
    next: Preview | None = None


class PastStep(_Out):
    no: int
    name: str
    records: list[PastRecord]


class SessionPast(_Out):
    session_id: int
    closed: bool
    closed_at: str | None
    closed_note: str | None
    steps: list[PastStep]
