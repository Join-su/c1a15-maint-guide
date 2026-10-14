#!/usr/bin/env python3
"""Validate the v0.8.20 G0-G7, logical-flow, multi-UI, PBC, and batch rules."""
from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

GATES = ("G0", "G1", "G2A", "G2B", "G3", "PBC-0", "PBC-1", "PBC-2", "PBC-3", "PBC-4", "G4", "G5", "G6", "G7")
REQUIRED = {"run_id", "project_id", "skill_version", "work_type", "risk_level", "phase", "current_gate", "status", "artifacts", "next_action"}
ARTIFACT_STATUSES = {"draft", "critic_passed", "approved", "rejected", "superseded"}
DECISIONS = {
    "G1": "use_case",
    "G2A": "wireframe_structure",
    "G2B": "visual_design",
    "G3": "prototype",
    "PBC-4": "prebuild_contract",
}
SCENARIO_TYPES = {
    "happy_path", "alternate", "failure", "cancel", "empty_no_result",
    "permission_authority", "external_dependency_failure", "timeout_expiry",
}
PBC_CRITIC_CATEGORIES = {"missing-traceability", "plan-contract-mismatch", "scope-creep", "unjustified-complexity", "unverifiable-plan", "unsafe-authorization", "baseline-drift"}
SAFE_ADVERSARIAL_TARGET_KINDS = {"in_memory_fixture", "temporary_local_file", "isolated_process", "loopback_listener", "local_test_listener"}
SELECTION_CATEGORIES = {"harness", "loop", "graph", "workflow", "subagent", "hook", "mcp", "worktree", "test", "state_data", "resilience_ops", "frontend", "skill", "model_product", "model_development"}
WORK_MODEL_FIELDS = (
    "first_view",
    "navigation",
    "layout_topology",
    "primary_information_unit",
    "primary_action_surface",
    "interaction_mode",
    "information_exposure",
    "state_feedback_placement",
)
FOUNDATIONAL_WORK_MODEL_FIELDS = {"layout_topology", "primary_information_unit", "interaction_mode"}
REFERENCE_SURFACE_CLASSES = {"game_ui", "marketing_site", "interactive_site", "workflow_product", "general_utility"}
WORKFLOW_SIGNALS = {"persistent_records", "queue_state_filter_compare", "repeated_multistep_work", "role_authority_handoff", "multi_workspace_operation"}
EVIDENCE_MODALITIES = {"screenshot", "interactive", "documented_flow"}
REFERENCE_OBSERVABLES = {"visible_structure", "visible_state", "interaction_behavior", "authority_behavior", "responsive_behavior"}
VISUAL_SIGNATURE_FIELDS = (
    "typography_density",
    "color_state",
    "surface_hierarchy",
    "item_control_form",
    "emphasis_reading_order",
)
STRUCTURE_RENDER_BASELINE_ROLE = "structure_workflow_only"
STRUCTURE_RENDER_BASELINE_ALIAS = "selected_structure_render_baseline"
CURATED_ROUTE_GUIDES = {
    "game_ui": {"https://www.gameuidatabase.com/"},
    "marketing_site": {"https://www.lapa.ninja/"},
    "interactive_site": {"https://www.awwwards.com/websites/"},
    "workflow_product": {"https://www.saasui.design/saas-design", "https://www.saasui.design/blog/saas-list-detail-master-detail-ux-patterns"},
}
BUNDLE_CONTENT_ROLES = {
    "use_case_bundle": {"use_case_packet", "use_case_map", "scenario_coverage", "acceptance_criteria", "logical_system_contract"},
    "prototype_bundle": {"prototype_slice", "prototype_renderable", "prototype_coverage", "variation_evidence", "execution_evidence"},
}
CRITIC_REFERENCE_REQUIREMENTS = {
    "G0": {"context_packet", "source_manifest"},
    "G1": {"evidence_pack"},
    "G3": {"use_case_bundle", "wireframe_structure", "visual_design"},
    "PBC-4": {"use_case_bundle", "prototype_bundle", "coding_plan", "verification_plan", "selection_register", "pbc_consistency_check", "prebuild_contract"},
    "G6": {"slice_execution_packet", "implementation_contract", "execution_ledger", "verification_report"},
}
CRITIC_SUBJECT_ARTIFACTS = {
    "G0": "evidence_pack",
    "G1": "use_case",
    "G3": "prototype",
    "PBC-4": "prebuild_contract",
    "G6": "verification_report",
}
PROFILE_RUNTIME_PATHS = {
    "skill_entry": "factory-profile/snapshot/skill/SKILL.md",
    "validator": "factory-profile/snapshot/skill/scripts/validate_artifacts.py",
    "critic_protocol": "factory-profile/snapshot/critic/03-critic-protocols.md",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def read_json(path: Path, label: str) -> dict:
    if not path.is_file():
        fail(f"{label} is required: {path.name}")
    try:
        value = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.name}: {exc}")
    if not isinstance(value, dict):
        fail(f"{label} must be a JSON object: {path.name}")
    return value


def run_path(run_dir: Path, relative_path: str, label: str) -> Path:
    if not isinstance(relative_path, str) or not relative_path:
        fail(f"{label} requires a non-empty relative path")
    path = run_dir / relative_path
    resolved_run_dir = run_dir.resolve()
    resolved_path = path.resolve()
    if resolved_path != resolved_run_dir and resolved_run_dir not in resolved_path.parents:
        fail(f"{label} must remain inside the run directory")
    return path


def fixed_external_reference(path_value: str, label: str) -> Path:
    if not isinstance(path_value, str) or not path_value:
        fail(f"{label} requires a non-empty absolute path")
    path = Path(path_value)
    if not path.is_absolute() or not path.is_file():
        fail(f"{label} must be an existing absolute file path")
    return path


def image_path(run_dir: Path, relative_path: str, label: str) -> None:
    path = run_path(run_dir, relative_path, label)
    if path.suffix.lower() not in {".svg", ".png", ".jpg", ".jpeg", ".webp", ".html"} or not path.is_file():
        fail(f"{label} must point to an existing renderable image or HTML file")


def required_file(run_dir: Path, relative_path: str, label: str) -> Path:
    path = run_path(run_dir, relative_path, label)
    if not path.is_file():
        fail(f"{label} must point to an existing file")
    return path


def non_empty_strings(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value)


def required_labeled_values(text: str, heading: str, labels: tuple[str, ...], label: str) -> None:
    """Require non-empty values for the named labels in one Markdown section."""
    section = text.split(heading, 1)[1].split("\n## ", 1)[0] if heading in text else ""
    for item in labels:
        line = next((line.strip() for line in section.splitlines() if line.strip().startswith(item)), "")
        if not line or not line[len(item):].strip():
            fail(f"{label} requires a non-empty value for: {item}")


def requires_runtime_profile(state: dict) -> bool:
    try:
        return tuple(int(part) for part in state.get("skill_version", "").split(".")) >= (0, 8, 10)
    except ValueError:
        return False


def factory_profile(state: dict, run_dir: Path) -> str:
    """Verify the run-local Factory runtime; old runs remain explicitly legacy."""
    if not requires_runtime_profile(state):
        return "legacy"
    record = state.get("factory_profile")
    if not isinstance(record, dict) or not all(isinstance(record.get(field), str) and record[field] for field in {"path", "sha256", "skill_version"}):
        fail("v0.8.10+ runs require a complete factory_profile record")
    profile_path = required_file(run_dir, record["path"], "factory profile")
    if hashlib.sha256(profile_path.read_bytes()).hexdigest() != record["sha256"]:
        fail("factory profile hash does not match")
    profile = read_json(profile_path, "factory profile")
    if profile.get("format_version") != 2 or profile.get("skill_name") != "vibe-coding-factory" or profile.get("skill_version") != state["skill_version"] or record["skill_version"] != state["skill_version"]:
        fail("factory profile must match this run's Vibe Coding Factory version")
    runtime = profile.get("runtime")
    if runtime != PROFILE_RUNTIME_PATHS:
        fail("factory profile must declare the canonical snapshot runtime paths")
    files = profile.get("files")
    if not isinstance(files, list) or not files:
        fail("factory profile requires snapshotted runtime files")
    files_by_role: dict[str, dict] = {}
    for item in files:
        if not isinstance(item, dict) or not all(isinstance(item.get(field), str) and item[field] for field in {"role", "snapshot_path", "sha256"}):
            fail("factory profile file entries are incomplete")
        snapshot = required_file(run_dir, item["snapshot_path"], "factory profile snapshot")
        if hashlib.sha256(snapshot.read_bytes()).hexdigest() != item["sha256"]:
            fail("factory profile snapshot hash does not match")
        if item["role"] in PROFILE_RUNTIME_PATHS:
            if item["role"] in files_by_role or item["snapshot_path"] != PROFILE_RUNTIME_PATHS[item["role"]]:
                fail("factory profile runtime entries must be unique and use canonical paths")
            files_by_role[item["role"]] = item
    if set(files_by_role) != set(PROFILE_RUNTIME_PATHS):
        fail("factory profile must snapshot the skill entry, validator, and critic protocol")
    expected_validator = required_file(run_dir, PROFILE_RUNTIME_PATHS["validator"], "factory profile validator").resolve()
    if Path(__file__).resolve() != expected_validator:
        fail(f"v0.8.10+ run must use its Factory Profile validator: {PROFILE_RUNTIME_PATHS['validator']}")
    return "pinned_snapshot"


def expected_critic_subject(state: dict, run_dir: Path, gate: str) -> dict:
    artifact_name = CRITIC_SUBJECT_ARTIFACTS[gate]
    record = state["artifacts"].get(artifact_name)
    if not isinstance(record, dict) or not isinstance(record.get("version"), str) or not record["version"]:
        fail(f"{gate} critic subject requires the current {artifact_name} artifact version")
    path_value = record.get("path")
    subject_path = required_file(run_dir, path_value, f"{gate} current critic subject")
    return {
        "artifact": artifact_name,
        "path": path_value,
        "version": record["version"],
        "sha256": hashlib.sha256(subject_path.read_bytes()).hexdigest(),
    }


def critic_references(review: dict, gate: str, run_dir: Path, state: dict | None = None) -> None:
    """Require an auditable record of the fixed comparison inputs a critic actually read."""
    verdict = review.get("verdict")
    issues = review.get("blocking_issues")
    issue_fields = {"id", "category", "subject_location", "comparison_location", "why_not_mechanical", "minimum_resolution"}
    if not isinstance(issues, list) or any(
        not isinstance(issue, dict)
        or issue_fields - set(issue)
        or not all(isinstance(issue[field], str) and issue[field].strip() for field in issue_fields)
        for issue in issues
    ):
        fail(f"{gate} critic blocking issues must identify the semantic comparison and minimum resolution")
    if verdict == "pass" and issues:
        fail(f"{gate} passing critic review must not contain blocking issues")
    if verdict == "revise" and not issues:
        fail(f"{gate} revise critic review requires one or more blocking issues")
    notes = review.get("non_blocking_notes")
    if not isinstance(notes, list) or len(notes) > 3:
        fail(f"{gate} critic review allows at most three non-blocking notes")
    references = review.get("reference_artifacts")
    if not isinstance(references, list) or not references:
        fail(f"{gate} critic review requires reference_artifacts")
    names: set[str] = set()
    for reference in references:
        required = {"artifact", "path", "version", "sha256"}
        if not isinstance(reference, dict) or required - set(reference) or not all(isinstance(reference[field], str) and reference[field] for field in required):
            fail(f"{gate} critic reference requires artifact, path, version, and sha256")
        reference_path = required_file(run_dir, reference["path"], f"{gate} critic reference")
        if hashlib.sha256(reference_path.read_bytes()).hexdigest() != reference["sha256"]:
            fail(f"{gate} critic reference hash does not match: {reference['artifact']}")
        names.add(reference["artifact"])
    if not CRITIC_REFERENCE_REQUIREMENTS[gate] <= names:
        fail(f"{gate} critic review is missing one or more required comparison references")
    if state is not None and requires_runtime_profile(state):
        bundle_record = review.get("input_bundle")
        if not isinstance(bundle_record, dict) or not all(isinstance(bundle_record.get(field), str) and bundle_record[field] for field in {"path", "sha256"}):
            fail(f"{gate} critic review requires its input_bundle path and hash")
        bundle_path = required_file(run_dir, bundle_record["path"], f"{gate} critic input bundle")
        if hashlib.sha256(bundle_path.read_bytes()).hexdigest() != bundle_record["sha256"]:
            fail(f"{gate} critic input bundle hash does not match")
        bundle = read_json(bundle_path, f"{gate} critic input bundle")
        subject = bundle.get("subject")
        if bundle.get("gate") != gate or not isinstance(subject, dict) or not all(isinstance(subject.get(field), str) and subject[field] for field in {"artifact", "path", "version", "sha256"}) or bundle.get("comparison_sources") != references:
            fail(f"{gate} critic input bundle must exactly declare the reviewed subject and comparison sources")
        subject_path = required_file(run_dir, subject["path"], f"{gate} critic input subject")
        if hashlib.sha256(subject_path.read_bytes()).hexdigest() != subject["sha256"]:
            fail(f"{gate} critic input subject hash does not match")
        if subject != expected_critic_subject(state, run_dir, gate):
            fail(f"{gate} critic input subject must be the current official {CRITIC_SUBJECT_ARTIFACTS[gate]} artifact")


def simple_record(state: dict, run_dir: Path, name: str) -> tuple[dict, Path]:
    record = state["artifacts"].get(name)
    if not isinstance(record, dict) or not isinstance(record.get("version"), str) or not record["version"]:
        fail(f"{name} requires a non-empty version")
    path = required_file(run_dir, record.get("path"), name)
    return record, path


def approved_acceptance_ids(state: dict, run_dir: Path) -> set[str]:
    use_case = artifact(state, run_dir, "use_case", {"approved"})
    coverage = read_json(run_path(run_dir, use_case.get("coverage"), "use_case coverage"), "use_case coverage")
    scenarios = coverage.get("scenarios")
    scenario_ids = {item.get("id") for item in scenarios if isinstance(item, dict) and isinstance(item.get("id"), str)} if isinstance(scenarios, list) else set()
    return set(acceptance_criteria(run_dir, use_case.get("acceptance_criteria"), use_case.get("version"), scenario_ids))


def ui_surface_contract(coverage: dict, scenarios: list[dict]) -> dict[str, dict]:
    """Return declared product UI surfaces; only multi-surface products need IDs."""
    mode = coverage.get("interaction_surface_mode")
    surfaces = coverage.get("ui_surfaces")
    if mode not in {"single", "multiple", "non_ui"} or not isinstance(surfaces, list):
        fail("use_case coverage requires an interaction_surface_mode and ui_surfaces list")
    if mode != "multiple":
        if surfaces:
            fail("single or non_ui products may not declare multi-UI surface records")
        return {}
    fields = {"id", "label", "primary_actor", "device_or_context", "required_scenario_ids"}
    scenario_ids = {scenario.get("id") for scenario in scenarios if isinstance(scenario, dict)}
    records: dict[str, dict] = {}
    declared_scenarios: set[str] = set()
    for surface in surfaces:
        if not isinstance(surface, dict) or set(surface) != fields or not all(isinstance(surface.get(field), str) and surface[field].strip() for field in fields - {"required_scenario_ids"}):
            fail("each multi-UI surface requires an ID, label, actor, device/context, and scenarios")
        surface_id = surface["id"]
        scenario_refs = surface["required_scenario_ids"]
        if surface_id in records or not isinstance(scenario_refs, list) or not scenario_refs or len(set(scenario_refs)) != len(scenario_refs) or any(ref not in scenario_ids or ref in declared_scenarios for ref in scenario_refs):
            fail("multi-UI surfaces require unique IDs and non-overlapping approved scenario IDs")
        records[surface_id] = surface
        declared_scenarios.update(scenario_refs)
    if len(records) < 2:
        fail("interaction_surface_mode multiple requires at least two product UI surfaces")
    assigned_scenarios: set[str] = set()
    for scenario in scenarios:
        surface_id = scenario.get("ui_surface_id")
        if surface_id is None:
            continue
        if not isinstance(surface_id, str) or surface_id not in records or scenario["id"] not in records[surface_id]["required_scenario_ids"]:
            fail("scenario ui_surface_id must match its declared multi-UI surface")
        assigned_scenarios.add(scenario["id"])
    if assigned_scenarios != declared_scenarios:
        fail("every declared product UI-surface scenario requires exactly one matching ui_surface_id")
    return records


def approved_ui_surfaces(state: dict, run_dir: Path) -> dict[str, dict]:
    use_case = artifact(state, run_dir, "use_case", {"approved"})
    coverage = read_json(run_path(run_dir, use_case.get("coverage"), "use_case coverage"), "use_case coverage")
    scenarios = coverage.get("scenarios")
    if not isinstance(scenarios, list):
        fail("approved Use Case requires scenario coverage")
    return ui_surface_contract(coverage, scenarios)


def logical_system_contract(
    state: dict,
    run_dir: Path,
    use_case: dict,
    scenario_ids: set[str],
    acceptance_ids: set[str],
) -> dict:
    """Validate the optional-in-substance, always-recorded G1 system-flow contract."""
    path = run_path(run_dir, use_case.get("logical_system_contract"), "logical system contract")
    contract = read_json(path, "logical system contract")
    required = {"run_id", "artifact", "use_case_version", "applicability", "not_applicable_reason", "flows", "human_views"}
    if required - set(contract) or contract.get("run_id") != state["run_id"] or contract.get("artifact") != "logical_system_contract" or contract.get("use_case_version") != use_case.get("version") or contract.get("applicability") not in {"required", "not_applicable"}:
        fail("logical_system_contract must match the Use Case version and declare applicability")
    views = contract["human_views"]
    if not isinstance(views, dict) or set(views) != {"system_overview", "scenario_flow"}:
        fail("logical_system_contract requires both named human-view records")
    for name, view in views.items():
        if contract["applicability"] == "not_applicable":
            if view is not None:
                fail("not_applicable logical_system_contract may not require human-view diagrams")
            continue
        if not isinstance(view, dict) or set(view) != {"path", "sha256"} or not all(isinstance(view[field], str) and view[field] for field in view):
            fail("applicable logical_system_contract requires locked human-view diagrams")
        view_path = required_file(run_dir, view["path"], f"logical system {name} diagram")
        if view_path.suffix.lower() != ".svg" or "<svg" not in view_path.read_text() or hashlib.sha256(view_path.read_bytes()).hexdigest() != view["sha256"]:
            fail("logical-system human-view diagram must be an SVG with a matching hash")
    flows = contract["flows"]
    if contract["applicability"] == "not_applicable":
        if flows != [] or not isinstance(contract["not_applicable_reason"], str) or not contract["not_applicable_reason"].strip():
            fail("not_applicable logical_system_contract requires an empty flow list and a reason")
        return contract
    if not isinstance(contract["not_applicable_reason"], str) or contract["not_applicable_reason"].strip() or not isinstance(flows, list) or not flows:
        fail("applicable logical_system_contract requires flows and no not-applicable reason")
    flow_ids: set[str] = set()
    covered_scenarios: set[str] = set()
    fields = {"id", "scenario_refs", "entry_surface", "trigger", "logical_responsibilities", "state", "external_dependencies", "success_outcome", "failure_cancel_retry_outcome", "acceptance_refs"}
    for flow in flows:
        if not isinstance(flow, dict) or fields - set(flow) or not isinstance(flow.get("id"), str) or not flow["id"] or flow["id"] in flow_ids:
            fail("logical_system_contract flows require unique IDs and complete records")
        if flow["entry_surface"] not in {"ui", "cli", "webhook", "worker", "scheduled_job"} or not all(isinstance(flow[field], str) and flow[field].strip() for field in {"trigger", "success_outcome", "failure_cancel_retry_outcome"}):
            fail("logical flow requires a valid entry surface and explicit outcomes")
        if not non_empty_strings(flow["scenario_refs"]) or len(set(flow["scenario_refs"])) != len(flow["scenario_refs"]) or any(ref not in scenario_ids or ref in covered_scenarios for ref in flow["scenario_refs"]):
            fail("logical flows must cover each approved scenario exactly once")
        if not non_empty_strings(flow["logical_responsibilities"]) or not isinstance(flow["external_dependencies"], list) or not non_empty_strings(flow["acceptance_refs"]) or any(ref not in acceptance_ids for ref in flow["acceptance_refs"]):
            fail("logical flows require responsibilities, valid AC references, and an external dependency list")
        state_record = flow["state"]
        if not isinstance(state_record, dict) or set(state_record) != {"ownership", "durability", "readback_expectation"} or state_record.get("durability") not in {"ephemeral", "durable", "not_applicable"} or not all(isinstance(state_record[field], str) and state_record[field].strip() for field in state_record):
            fail("logical flow state requires ownership, durability, and readback expectation")
        flow_ids.add(flow["id"])
        covered_scenarios.update(flow["scenario_refs"])
    if covered_scenarios != scenario_ids:
        fail("logical_system_contract must cover every approved scenario")
    return contract


def approved_logical_system_contract(state: dict, run_dir: Path) -> dict:
    use_case = artifact(state, run_dir, "use_case", {"approved"})
    coverage = read_json(run_path(run_dir, use_case.get("coverage"), "use_case coverage"), "use_case coverage")
    scenario_ids = {item.get("id") for item in coverage.get("scenarios", []) if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"]}
    return logical_system_contract(state, run_dir, use_case, scenario_ids, approved_acceptance_ids(state, run_dir))


def pbc_input_lock(state: dict, run_dir: Path) -> None:
    for gate in ("G1", "G3"):
        approved_decision(state, run_dir, gate)
    record, path = simple_record(state, run_dir, "approved_inputs")
    locked = read_json(path, "approved inputs")
    if locked.get("run_id") != state["run_id"] or locked.get("artifact") != "approved_inputs" or locked.get("version") != record["version"] or locked.get("product_lock") is not True:
        fail("approved_inputs must be a locked manifest for this run and version")
    inputs = locked.get("inputs")
    bundle_sources = {"use_case_bundle": "use_case", "prototype_bundle": "prototype"}
    expected = set(bundle_sources)
    if not isinstance(inputs, list) or {item.get("artifact") for item in inputs if isinstance(item, dict)} != expected:
        fail("approved_inputs must list exactly the approved Use Case and Prototype bundles")
    for item in inputs:
        required = {"artifact", "version", "manifest_path", "content_sha256", "gate_decision_path"}
        if not isinstance(item, dict) or required - set(item) or not all(isinstance(item[field], str) and item[field] for field in required):
            fail("each approved input requires artifact, version, manifest_path, content_sha256, and gate_decision_path")
        source_record = state["artifacts"].get(bundle_sources[item["artifact"]])
        if not isinstance(source_record, dict) or source_record.get("version") != item["version"]:
            fail("approved bundle version must match its approved source artifact in run-state")
        manifest_path = required_file(run_dir, item["manifest_path"], "approved input manifest")
        actual_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        if actual_hash != item["content_sha256"]:
            fail("approved input manifest hash does not match the locked input")
        bundle = read_json(manifest_path, "approved bundle manifest")
        contents = bundle.get("contents")
        required_roles = BUNDLE_CONTENT_ROLES[item["artifact"]]
        roles = {entry.get("role") for entry in contents if isinstance(entry, dict)} if isinstance(contents, list) else set()
        if bundle.get("run_id") != state["run_id"] or bundle.get("artifact") != item["artifact"] or bundle.get("version") != item["version"] or not required_roles <= roles:
            fail("approved bundle manifest must identify its version and every required bundle content role")
        for entry in contents:
            if not isinstance(entry, dict) or not all(isinstance(entry.get(field), str) and entry[field] for field in {"role", "path", "sha256"}):
                fail("approved bundle manifest contents require role, path, and sha256")
            content_path = required_file(run_dir, entry["path"], "approved bundle content")
            if hashlib.sha256(content_path.read_bytes()).hexdigest() != entry["sha256"]:
                fail("approved bundle manifest content hash does not match")
        if item["artifact"] == "use_case_bundle":
            source_record = state["artifacts"]["use_case"]
            logical_path = source_record.get("logical_system_contract")
            logical_entry = next((entry for entry in contents if isinstance(entry, dict) and entry.get("role") == "logical_system_contract"), None)
            if not isinstance(logical_entry, dict) or logical_entry.get("path") != logical_path:
                fail("Use Case Bundle must lock the current logical_system_contract")
    if not non_empty_strings(locked.get("preservation_promises")):
        fail("approved_inputs requires one or more preservation_promises")
    baseline_record, baseline_path = simple_record(state, run_dir, "planning_baseline")
    baseline = read_json(baseline_path, "planning baseline")
    required = {"run_id", "artifact", "version", "repository_revision", "dependency_revision", "environment_facts", "recorded_at", "revalidate_before_implementation_when"}
    if required - set(baseline) or baseline.get("run_id") != state["run_id"] or baseline.get("artifact") != "planning_baseline" or baseline.get("version") != baseline_record["version"]:
        fail("planning_baseline is incomplete or does not match this run")
    if not isinstance(baseline["repository_revision"], str) or not isinstance(baseline["dependency_revision"], str) or not isinstance(baseline["environment_facts"], list) or not non_empty_strings(baseline["revalidate_before_implementation_when"]):
        fail("planning_baseline requires revisions, environment facts, and revalidation triggers")


def engineering_discovery(state: dict, run_dir: Path) -> None:
    _, path = simple_record(state, run_dir, "engineering_discovery")
    text = path.read_text()
    headings = ("## Repository and environment facts", "## Requirement signals and cheapest verifiers", "## Candidate methods and evidence", "## Spike decision", "## Coupled-control feasibility", "## Revalidation triggers")
    if any(heading not in text for heading in headings):
        fail("engineering_discovery is missing a required PBC-1 section")


def feasibility_preflight(state: dict, plan: dict, run_dir: Path, plan_item_ids: set[str]) -> dict:
    """Validate the conditional, auditable proof that coupled runtime controls work together."""
    preflight = plan.get("feasibility_preflight")
    required = {"status", "rationale", "basis", "probe"}
    if not isinstance(preflight, dict) or required - set(preflight) or preflight.get("status") not in {"not_required", "verified"} or not isinstance(preflight.get("rationale"), str) or not preflight["rationale"].strip():
        fail("coding_plan requires a complete feasibility_preflight")
    basis = preflight["basis"]
    if not isinstance(basis, dict) or set(basis) != {"kind", "evidence"} or basis.get("kind") not in {"single_control", "existing_observed_evidence", "internal_compatibility_probe"}:
        fail("feasibility_preflight requires a valid basis")

    if preflight["status"] == "not_required":
        if preflight["probe"] is not None or basis["kind"] not in {"single_control", "existing_observed_evidence"}:
            fail("a not_required feasibility_preflight may not include a probe")
        if basis["kind"] == "single_control":
            if basis["evidence"] is not None:
                fail("a single-control feasibility basis must not claim unrelated evidence")
            return preflight
        pointer = basis["evidence"]
        if not isinstance(pointer, dict) or set(pointer) != {"artifact", "path", "version", "sha256"} or pointer.get("artifact") not in {"planning_baseline", "selection_register"} or not all(isinstance(pointer[field], str) and pointer[field] for field in {"path", "version", "sha256"}):
            fail("an observed-evidence feasibility basis requires a current PBC artifact pointer")
        expected_path = None
        if pointer["artifact"] == "planning_baseline":
            baseline_record, baseline_path = simple_record(state, run_dir, "planning_baseline")
            expected_path, expected_version = str(baseline_path.relative_to(run_dir)), baseline_record["version"]
        else:
            register_path = required_file(run_dir, plan.get("selection_register"), "selection register")
            expected_path, expected_version = str(register_path.relative_to(run_dir)), read_json(register_path, "selection register").get("version")
        evidence_path = required_file(run_dir, pointer["path"], "observed feasibility evidence")
        if pointer["path"] != expected_path or pointer["version"] != expected_version or hashlib.sha256(evidence_path.read_bytes()).hexdigest() != pointer["sha256"]:
            fail("observed feasibility evidence must point to the current declared PBC artifact")
        return preflight

    if preflight["probe"] is None or basis["kind"] != "internal_compatibility_probe" or basis["evidence"] is not None:
        fail("a verified feasibility_preflight requires an internal compatibility probe")
    pointer = preflight["probe"]
    if not isinstance(pointer, dict) or set(pointer) != {"artifact", "path", "version", "sha256"} or pointer.get("artifact") != "feasibility_probe" or not all(isinstance(pointer[field], str) and pointer[field] for field in {"path", "version", "sha256"}):
        fail("a verified feasibility preflight requires a feasibility_probe pointer")
    probe_path = required_file(run_dir, pointer["path"], "feasibility probe")
    probe = read_json(probe_path, "feasibility probe")
    if probe.get("run_id") != state["run_id"] or probe.get("artifact") != "feasibility_probe" or probe.get("version") != pointer["version"] or hashlib.sha256(probe_path.read_bytes()).hexdigest() != pointer["sha256"]:
        fail("feasibility probe must match its declared pointer")
    checks = probe.get("checks")
    if not isinstance(checks, list) or not checks:
        fail("a verified feasibility preflight requires one or more probe checks")
    seen = set()
    fields = {"id", "plan_item_ids", "assumption", "coupled_controls", "material_to", "temporary_isolation", "command_summary", "prohibited_actions", "allows_external_connection", "allows_product_or_dependency_source_change", "allows_live_or_sensitive_data", "expected_observation", "observed_result", "result", "evidence_paths", "cleanup"}
    for check in checks:
        if not isinstance(check, dict) or fields - set(check) or not isinstance(check.get("id"), str) or not check["id"] or check["id"] in seen or check.get("material_to") not in {"authority_boundary", "verifier", "recovery"} or check.get("result") != "pass":
            fail("feasibility probe checks require unique IDs, a valid materiality, and pass")
        if not isinstance(check["plan_item_ids"], list) or not check["plan_item_ids"] or len(set(check["plan_item_ids"])) != len(check["plan_item_ids"]) or any(identifier not in plan_item_ids for identifier in check["plan_item_ids"]) or not isinstance(check["coupled_controls"], list) or len(check["coupled_controls"]) < 2 or not non_empty_strings(check["coupled_controls"]) or not isinstance(check["prohibited_actions"], list) or not non_empty_strings(check["prohibited_actions"]) or not isinstance(check["evidence_paths"], list) or not check["evidence_paths"]:
            fail("feasibility probe checks require linked plan items, two controls, prohibited actions, and evidence")
        if any(check[field] is not False for field in {"allows_external_connection", "allows_product_or_dependency_source_change", "allows_live_or_sensitive_data"}):
            fail("a feasibility probe may not allow external, source-changing, live, or sensitive actions")
        if not all(isinstance(check[field], str) and check[field].strip() for field in {"assumption", "temporary_isolation", "command_summary", "expected_observation", "observed_result", "cleanup"}):
            fail("feasibility probe checks require an explicit safe probe record")
        for evidence_path in check["evidence_paths"]:
            required_file(run_dir, evidence_path, "feasibility-probe evidence")
        seen.add(check["id"])
    return preflight


def approved_prototype_structure_regions(state: dict, run_dir: Path) -> set[tuple[str, str, str]]:
    """Return the UI decision regions that PBC must carry into the implementation plan.

    PBC reads only the approved Prototype for product/UI truth.  The Prototype has
    already copied and validated the selected G2A contract, so this preserves the
    G3-to-PBC boundary rather than reopening G2A artifacts here.
    """
    prototype = artifact(state, run_dir, "prototype", {"approved"})
    verification = read_json(
        run_path(run_dir, prototype.get("verification"), "prototype coverage"),
        "prototype coverage",
    )
    entries = verification.get("compiled_structure_contract")
    if not isinstance(entries, list) or not entries:
        fail("approved prototype must contain a compiled selected structure contract")
    keys: set[tuple[str, str, str]] = set()
    required = {"page_id", "state", "region_id", "selected_structure", "content_composition", "interaction_or_state_rule", "excluded_alternative"}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != required:
            fail("approved prototype compiled structure contract is incomplete")
        key = (entry["page_id"], entry["state"], entry["region_id"])
        if not all(isinstance(value, str) and value.strip() for value in key) or key in keys:
            fail("approved prototype compiled structure contract has invalid Page / State / Region keys")
        keys.add(key)
    return keys


def coding_plan(state: dict, run_dir: Path) -> tuple[dict, set[str]]:
    record, path = simple_record(state, run_dir, "coding_plan")
    plan = read_json(path, "coding plan")
    if plan.get("run_id") != state["run_id"] or plan.get("artifact") != "coding_plan" or plan.get("version") != record["version"]:
        fail("coding_plan must match this run and artifact version")
    mode = plan.get("plan_mode")
    if mode not in {"compact", "standard", "high_risk"} or (state["risk_level"] == "high" and mode != "high_risk"):
        fail("coding_plan requires a valid plan_mode; high-risk runs require high_risk mode")
    _, input_path = simple_record(state, run_dir, "approved_inputs")
    if plan.get("approved_input_manifest") != str(input_path.relative_to(run_dir)):
        fail("coding_plan must reference the locked approved input manifest")
    director_review_path = run_path(run_dir, plan.get("director_review"), "coding plan director-review target")
    if director_review_path.suffix.lower() != ".md":
        fail("coding_plan director_review target must be a Markdown path")
    items = plan.get("items")
    acceptance_ids = approved_acceptance_ids(state, run_dir)
    use_case = artifact(state, run_dir, "use_case", {"approved"})
    coverage = read_json(run_path(run_dir, use_case.get("coverage"), "use_case coverage"), "use_case coverage")
    scenarios = coverage.get("scenarios")
    ui_surfaces = ui_surface_contract(coverage, scenarios) if isinstance(scenarios, list) else {}
    criteria_source = read_json(run_path(run_dir, use_case.get("acceptance_criteria"), "approved acceptance criteria"), "approved acceptance criteria")
    criterion_scenarios = {
        item.get("id"): set(item.get("scenario_refs", []))
        for item in criteria_source.get("criteria", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    logical_contract = approved_logical_system_contract(state, run_dir)
    ui_surfaces = approved_ui_surfaces(state, run_dir)
    surface_delivery = plan["implementation_design"]["ui_surface_delivery"]
    plan_item_slice = {item["id"]: item["slice_id"] for item in plan["items"]}
    logical_flows = {flow["id"]: flow for flow in logical_contract["flows"]}
    prototype_region_keys = approved_prototype_structure_regions(state, run_dir)
    if not isinstance(items, list) or not items:
        fail("coding_plan requires at least one plan item")
    seen_ids, covered_ids = set(), set()
    execution_policy = plan.get("execution_policy")
    policy_fields = {"mode", "automatic_quality_gates", "critic_trigger_categories", "stop_conditions"}
    if not isinstance(execution_policy, dict) or policy_fields - set(execution_policy) or execution_policy["mode"] not in {"continuous_batch", "per_slice_gated"} or not all(non_empty_strings(execution_policy[field]) for field in policy_fields - {"mode"}):
        fail("coding_plan requires an explicit execution mode, automatic gates, critic triggers, and stop conditions")
    if len(set(execution_policy["automatic_quality_gates"])) != len(execution_policy["automatic_quality_gates"]):
        fail("coding_plan automatic_quality_gates must be unique")
    implementation_design = plan.get("implementation_design")
    required_design = {"overview", "boundaries", "slice_sequence", "first_end_to_end_flow", "ui_surface_delivery", "delivery_and_recovery"}
    if not isinstance(implementation_design, dict) or required_design - set(implementation_design) or not isinstance(implementation_design["overview"], str) or not implementation_design["overview"] or not isinstance(implementation_design["delivery_and_recovery"], str) or not implementation_design["delivery_and_recovery"]:
        fail("coding_plan requires an implementation_design overview and delivery/recovery plan")
    boundaries = implementation_design["boundaries"]
    boundary_fields = {"id", "responsibility", "interfaces", "state_data_boundary", "external_action_boundary", "logical_flow_refs", "runtime_mode", "state_ownership", "failure_recovery", "operational_readiness", "plan_item_ids", "depends_on"}
    if not isinstance(boundaries, list) or not boundaries:
        fail("implementation_design requires one or more responsibility boundaries")
    boundary_ids = {item.get("id") for item in boundaries if isinstance(item, dict)}
    if len(boundary_ids) != len(boundaries) or None in boundary_ids or any(not isinstance(item, dict) or boundary_fields - set(item) or not all(isinstance(item[field], str) and item[field] for field in {"id", "responsibility", "state_data_boundary", "external_action_boundary", "state_ownership", "failure_recovery", "operational_readiness"}) or item.get("runtime_mode") not in {"internal", "adapter", "fixture", "external", "not_applicable"} or not isinstance(item["interfaces"], list) or not isinstance(item["plan_item_ids"], list) or not isinstance(item["depends_on"], list) or not isinstance(item["logical_flow_refs"], list) or len(set(item["logical_flow_refs"])) != len(item["logical_flow_refs"]) or any(ref not in logical_flows for ref in item["logical_flow_refs"]) for item in boundaries):
        fail("implementation_design boundaries are incomplete")
    if any(any(dependency not in boundary_ids or dependency == item["id"] for dependency in item["depends_on"]) for item in boundaries):
        fail("implementation_design boundary dependencies must name another declared boundary")
    slices = implementation_design["slice_sequence"]
    slice_fields = {"slice_id", "plan_item_ids", "depends_on", "expected_outcome"}
    if not isinstance(slices, list) or not slices:
        fail("implementation_design requires a slice sequence")
    slice_ids = {item.get("slice_id") for item in slices if isinstance(item, dict)}
    if len(slice_ids) != len(slices) or None in slice_ids or any(not isinstance(item, dict) or slice_fields - set(item) or not isinstance(item["slice_id"], str) or not item["slice_id"] or not isinstance(item["plan_item_ids"], list) or not isinstance(item["depends_on"], list) or not isinstance(item["expected_outcome"], str) or not item["expected_outcome"] for item in slices):
        fail("implementation_design slices are incomplete")
    if any(any(dependency not in slice_ids or dependency == item["slice_id"] for dependency in item["depends_on"]) for item in slices):
        fail("implementation_design slice dependencies must name another declared slice")
    first_flow = implementation_design["first_end_to_end_flow"]
    first_fields = {"status", "logical_flow_id", "scenario_id", "slice_id", "boundary_path", "expected_outcome", "readback_expectation", "not_applicable_reason"}
    if not isinstance(first_flow, dict) or first_fields - set(first_flow) or first_flow.get("status") not in {"required", "not_applicable"} or not isinstance(first_flow.get("boundary_path"), list):
        fail("implementation_design requires an explicit first_end_to_end_flow record")
    if logical_contract["applicability"] == "not_applicable":
        if first_flow["status"] != "not_applicable" or first_flow["logical_flow_id"] or first_flow["scenario_id"] or first_flow["slice_id"] or first_flow["boundary_path"] or first_flow["expected_outcome"] or first_flow["readback_expectation"] or not isinstance(first_flow["not_applicable_reason"], str) or not first_flow["not_applicable_reason"].strip():
            fail("a non-applicable logical contract requires a closed first_end_to_end_flow record")
    else:
        flow_id = first_flow.get("logical_flow_id")
        if first_flow["status"] != "required" or flow_id not in logical_flows or first_flow.get("scenario_id") not in logical_flows[flow_id]["scenario_refs"] or first_flow.get("slice_id") not in slice_ids or not non_empty_strings(first_flow["boundary_path"]) or any(boundary not in boundary_ids for boundary in first_flow["boundary_path"]) or not all(isinstance(first_flow[field], str) and first_flow[field].strip() for field in {"expected_outcome", "readback_expectation"}) or first_flow.get("not_applicable_reason"):
            fail("applicable logical contract requires a complete first end-to-end flow")
        if any(flow_id not in next(boundary["logical_flow_refs"] for boundary in boundaries if boundary["id"] == boundary_id) for boundary_id in first_flow["boundary_path"]):
            fail("every first end-to-end boundary must implement its declared logical flow")
    surface_delivery = implementation_design["ui_surface_delivery"]
    if not isinstance(surface_delivery, list):
        fail("implementation_design requires a ui_surface_delivery list")
    if not ui_surfaces:
        if surface_delivery:
            fail("single or non_ui products may not add ui_surface_delivery records")
    else:
        fields = {"ui_surface_id", "critical_scenario_id", "integrated_slice_id", "entry_boundary_id", "result_readback_boundary_id", "verification_acceptance_ids"}
        seen_surface_ids: set[str] = set()
        if len(surface_delivery) != len(ui_surfaces):
            fail("multi-UI plans require one delivery record for every product UI surface")
        for delivery in surface_delivery:
            if not isinstance(delivery, dict) or set(delivery) != fields:
                fail("multi-UI ui_surface_delivery records are incomplete")
            surface_id = delivery["ui_surface_id"]
            scenario_id = delivery["critical_scenario_id"]
            acceptance_refs = delivery["verification_acceptance_ids"]
            if not isinstance(surface_id, str) or surface_id not in ui_surfaces or surface_id in seen_surface_ids or not isinstance(scenario_id, str) or scenario_id not in ui_surfaces[surface_id]["required_scenario_ids"] or delivery.get("integrated_slice_id") not in slice_ids or delivery.get("entry_boundary_id") not in boundary_ids or delivery.get("result_readback_boundary_id") not in boundary_ids or not isinstance(acceptance_refs, list) or not acceptance_refs or len(set(acceptance_refs)) != len(acceptance_refs) or any(acceptance_id not in acceptance_ids or scenario_id not in criterion_scenarios.get(acceptance_id, set()) for acceptance_id in acceptance_refs):
                fail("multi-UI delivery must connect every surface to its scenario, boundaries, slice, and AC")
            if logical_contract["applicability"] == "required":
                scenario_flow_id = next(flow_id for flow_id, flow in logical_flows.items() if scenario_id in flow["scenario_refs"])
                delivery_boundaries = [boundary for boundary in boundaries if boundary["id"] in {delivery["entry_boundary_id"], delivery["result_readback_boundary_id"]}]
                if any(scenario_flow_id not in boundary["logical_flow_refs"] for boundary in delivery_boundaries):
                    fail("multi-UI delivery boundaries must implement the surface scenario's logical flow")
            seen_surface_ids.add(surface_id)
    diagrams = plan.get("diagram_paths")
    if not isinstance(diagrams, dict) or {"traceability", "roadmap", "implementation_design", "runtime_sequence"} - set(diagrams) or not all(isinstance(value, str) for value in diagrams.values()):
        fail("coding_plan requires traceability, roadmap, implementation-design, and runtime-sequence diagram paths")
    fields = {"id", "selection_refs", "boundary_refs", "logical_flow_refs", "slice_id", "acceptance_ids", "prototype_refs", "compiled_product_contract", "status", "requirement_signal", "selected_approach", "rejected_approaches", "trigger", "non_trigger", "preconditions", "authority_boundary", "verifier", "review_requirement", "review_rationale", "stop_or_escalation", "revalidation_trigger"}
    covered_prototype_regions: set[tuple[str, str, str]] = set()
    for item in items:
        if not isinstance(item, dict) or fields - set(item) or not isinstance(item["id"], str) or not item["id"] or item["id"] in seen_ids:
            fail("each coding plan item requires a unique complete record")
        if item["status"] not in {"decided", "provisional"} or item["review_requirement"] not in {"automatic", "independent_critic"} or not isinstance(item["acceptance_ids"], list) or not item["acceptance_ids"] or any(identifier not in acceptance_ids for identifier in item["acceptance_ids"]):
            fail("coding plan items require valid acceptance IDs, status, and review requirement")
        text_fields = fields - {"id", "selection_refs", "boundary_refs", "logical_flow_refs", "acceptance_ids", "prototype_refs", "compiled_product_contract", "status", "rejected_approaches", "preconditions"}
        if not all(isinstance(item[field], str) and item[field] for field in text_fields) or not non_empty_strings(item["selection_refs"]) or not non_empty_strings(item["boundary_refs"]) or any(reference not in boundary_ids for reference in item["boundary_refs"]) or not isinstance(item["logical_flow_refs"], list) or len(set(item["logical_flow_refs"])) != len(item["logical_flow_refs"]) or any(reference not in logical_flows for reference in item["logical_flow_refs"]) or not isinstance(item["rejected_approaches"], list) or not isinstance(item["preconditions"], list) or item["slice_id"] not in slice_ids:
            fail("coding plan item selection details must be explicit")
        product_contract = item["compiled_product_contract"]
        if not isinstance(product_contract, dict) or set(product_contract) != {"behavior", "ui_state_interaction", "authority_data", "logical_flow_behavior"} or not all(isinstance(value, str) and value for value in product_contract.values()):
            fail("coding plan items must carry complete compiled behavior, UI/state/interaction, authority/data, and logical-flow requirements")
        boundary_flow_refs = {flow_ref for boundary in boundaries if boundary["id"] in item["boundary_refs"] for flow_ref in boundary["logical_flow_refs"]}
        if any(flow_ref not in boundary_flow_refs for flow_ref in item["logical_flow_refs"]):
            fail("coding plan logical-flow refs must be implemented by a referenced boundary")
        prototype_refs = item["prototype_refs"]
        if not isinstance(prototype_refs, list) or not prototype_refs:
            fail("coding plan items require one or more approved Prototype Page / State / Region references")
        item_region_refs: set[tuple[str, str, str]] = set()
        for prototype_ref in prototype_refs:
            if not isinstance(prototype_ref, dict) or set(prototype_ref) != {"page_id", "state", "region_id"}:
                fail("coding plan prototype_refs require exactly page_id, state, and region_id")
            region_key = (prototype_ref["page_id"], prototype_ref["state"], prototype_ref["region_id"])
            if not all(isinstance(value, str) and value for value in region_key) or region_key not in prototype_region_keys or region_key in item_region_refs:
                fail("coding plan prototype_refs must name an approved Prototype Page / State / Region")
            item_region_refs.add(region_key)
            covered_prototype_regions.add(region_key)
        seen_ids.add(item["id"])
        covered_ids.update(item["acceptance_ids"])
    if covered_ids != acceptance_ids:
        fail("coding_plan must connect every approved acceptance criterion to a plan item")
    if logical_contract["applicability"] == "required" and {flow_id for item in items for flow_id in item["logical_flow_refs"]} != set(logical_flows):
        fail("coding_plan must connect every applicable logical flow to one or more plan items")
    if logical_contract["applicability"] == "required":
        flow_id = first_flow["logical_flow_id"]
        first_slice_items = {
            item["id"] for item in items
            if item["slice_id"] == first_flow["slice_id"] and flow_id in item["logical_flow_refs"]
        }
        if not first_slice_items or any(
            not any(item_id in boundary["plan_item_ids"] for item_id in first_slice_items)
            for boundary in boundaries if boundary["id"] in first_flow["boundary_path"]
        ):
            fail("the first end-to-end slice must contain a plan item for every declared boundary")
    if ui_surfaces:
        for delivery in surface_delivery:
            integrated_items = {
                item["id"] for item in items
                if item["slice_id"] == delivery["integrated_slice_id"]
            }
            delivery_boundary_ids = {delivery["entry_boundary_id"], delivery["result_readback_boundary_id"]}
            if not integrated_items or any(
                not integrated_items & set(boundary["plan_item_ids"])
                for boundary in boundaries
                if boundary["id"] in delivery_boundary_ids
            ):
                fail("each multi-UI delivery slice must contain work for its entry and readback boundaries")
    if logical_contract["applicability"] == "not_applicable" and (any(item["logical_flow_refs"] for item in items) or any(boundary["logical_flow_refs"] for boundary in boundaries)):
        fail("not_applicable logical contracts may not be referenced by plan items or boundaries")
    if not prototype_region_keys <= covered_prototype_regions:
        fail("coding_plan must connect every approved Prototype Page / State / Region to one or more plan items")
    if {plan_item for boundary in boundaries for plan_item in boundary["plan_item_ids"]} != seen_ids or any(any(plan_item not in seen_ids for plan_item in boundary["plan_item_ids"]) for boundary in boundaries):
        fail("implementation_design boundaries must cover every coding-plan item exactly through declared boundaries")
    if {plan_item for slice_record in slices for plan_item in slice_record["plan_item_ids"]} != seen_ids or any(any(plan_item not in seen_ids for plan_item in slice_record["plan_item_ids"]) for slice_record in slices):
        fail("implementation_design slice sequence must cover every coding-plan item")
    feasibility_preflight(state, plan, run_dir, seen_ids)
    selection_register(state, run_dir, plan, seen_ids)
    policy = plan.get("amendment_policy")
    if not isinstance(policy, dict) or set(policy) != {"l0", "l1", "out_of_scope_contract_change"} or not all(isinstance(value, str) and value for value in policy.values()):
        fail("coding_plan requires an explicit L0/L1/out-of-scope amendment policy")
    return plan, seen_ids


def selection_register(state: dict, run_dir: Path, plan: dict, plan_item_ids: set[str]) -> None:
    register = read_json(run_path(run_dir, plan.get("selection_register"), "selection register"), "selection register")
    if register.get("run_id") != state["run_id"] or register.get("artifact") != "selection_register" or not isinstance(register.get("version"), str) or not register["version"]:
        fail("selection_register must match this run and have a version")
    available = register.get("available_skills")
    if not isinstance(available, list) or any(not isinstance(item, dict) or not all(isinstance(item.get(key), str) and item[key] for key in {"name", "source", "verified_at"}) for item in available):
        fail("selection_register available_skills must be an environment-verified inventory")
    available_names = {item["name"] for item in available}
    playbook = register.get("engineering_playbook")
    required_playbook = {"path", "version", "content_sha256", "reviewed_at"}
    if not isinstance(playbook, dict) or required_playbook - set(playbook) or not all(isinstance(playbook[field], str) and playbook[field] for field in required_playbook):
        fail("selection_register requires a complete engineering_playbook reference")
    playbook_path = fixed_external_reference(playbook["path"], "engineering_playbook")
    if hashlib.sha256(playbook_path.read_bytes()).hexdigest() != playbook["content_sha256"]:
        fail("engineering_playbook hash does not match")
    playbook_text = playbook_path.read_text()
    records = register.get("records")
    not_applicable = register.get("not_applicable_categories")
    if not isinstance(records, list) or not records or not isinstance(not_applicable, list) or len(set(not_applicable)) != len(not_applicable) or any(category not in SELECTION_CATEGORIES for category in not_applicable):
        fail("selection_register requires records and valid unique not_applicable_categories")
    record_categories = {item.get("category") for item in records if isinstance(item, dict)}
    if any(category not in SELECTION_CATEGORIES for category in record_categories):
        fail("selection_register records must use valid engineering, skill, or model-role categories")
    if plan.get("plan_mode") == "compact":
        if record_categories & set(not_applicable) or record_categories | set(not_applicable) != SELECTION_CATEGORIES:
            fail("compact selection_register must account for every category through a record or not_applicable_categories")
    elif set(not_applicable) or record_categories != SELECTION_CATEGORIES:
        fail("standard and high-risk selection_registers must review every engineering, skill, and model-role category")
    ids = set()
    for item in records:
        required = {"id", "category", "decision", "requirement_signals", "candidates", "decision_reason", "usage", "plan_item_ids", "trigger", "non_trigger", "preconditions", "authority_boundary", "verifier", "limit_or_stop", "playbook_refs", "currentness", "product_behavior_change"}
        if not isinstance(item, dict) or required - set(item) or not isinstance(item["id"], str) or not item["id"] or item["id"] in ids or item["decision"] not in {"selected", "excluded"} or item["product_behavior_change"] not in {"none", "outside_factory_scope"} or not all(isinstance(item[key], list) for key in {"requirement_signals", "candidates", "plan_item_ids", "preconditions", "playbook_refs"}) or not item["playbook_refs"] or not all(isinstance(reference, str) and reference and reference in playbook_text for reference in item["playbook_refs"]) or any(identifier not in plan_item_ids for identifier in item["plan_item_ids"]) or not isinstance(item["decision_reason"], str) or not item["decision_reason"] or not isinstance(item["currentness"], dict) or not all(isinstance(item["currentness"].get(key), str) and item["currentness"][key] for key in {"verified_at", "version_or_environment"}):
            fail("selection-register records are incomplete")
        if item["decision"] == "selected" and (not all(isinstance(item[key], str) and item[key] for key in {"usage", "trigger", "non_trigger", "authority_boundary", "verifier", "limit_or_stop"}) or not item["plan_item_ids"]):
            fail("selected selection-register records require execution details and plan-item links")
        if item["decision"] == "excluded" and (not isinstance(item["non_trigger"], str) or not item["non_trigger"] or not isinstance(item["limit_or_stop"], str) or not item["limit_or_stop"]):
            fail("excluded selection-register records require non-trigger and revalidation details")
        if item["category"] == "skill" and item["decision"] == "selected" and any(name not in available_names for name in item["candidates"]):
            fail("selected skills must exist in the environment-verified skill inventory")
        ids.add(item["id"])
    selected_ids = {item["id"] for item in records if item["decision"] == "selected"}
    if any(any(ref not in selected_ids for ref in item["selection_refs"]) for item in plan["items"]):
        fail("every coding-plan selection_ref must exist and be selected in the selection register")


def verification_plan(state: dict, run_dir: Path, plan: dict) -> None:
    plan_item_ids = {item["id"] for item in plan["items"]}
    record, path = simple_record(state, run_dir, "verification_plan")
    matrix = read_json(path, "verification plan")
    if matrix.get("run_id") != state["run_id"] or matrix.get("artifact") != "verification_plan" or matrix.get("version") != record["version"]:
        fail("verification_plan must match this run and artifact version")
    acceptance_ids = approved_acceptance_ids(state, run_dir)
    use_case = artifact(state, run_dir, "use_case", {"approved"})
    source = read_json(run_path(run_dir, use_case.get("acceptance_criteria"), "approved acceptance criteria"), "approved acceptance criteria")
    source_criteria = {item.get("id"): item for item in source.get("criteria", []) if isinstance(item, dict)}
    logical_contract = approved_logical_system_contract(state, run_dir)
    first_flow = plan["implementation_design"]["first_end_to_end_flow"]
    first_flow_plan_items = {
        item["id"] for item in plan["items"]
        if first_flow["status"] == "required" and first_flow["logical_flow_id"] in item["logical_flow_refs"]
    }
    entries = matrix.get("acceptance_criteria")
    if not isinstance(entries, list) or len(entries) != len(acceptance_ids):
        fail("verification_plan must include every acceptance criterion exactly once")
    seen = set()
    has_l3_first_flow = False
    has_l3_surface_delivery = {delivery["ui_surface_id"]: False for delivery in surface_delivery}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("acceptance_id"), str) or entry["acceptance_id"] not in acceptance_ids or entry["acceptance_id"] in seen:
            fail("verification plan has invalid or duplicate acceptance IDs")
        if entry.get("acceptance_criterion") != source_criteria.get(entry["acceptance_id"]):
            fail("verification plan must copy each approved acceptance criterion and observable conditions exactly")
        if not isinstance(entry.get("plan_item_ids"), list) or not entry["plan_item_ids"] or any(identifier not in plan_item_ids for identifier in entry["plan_item_ids"]) or entry.get("completion_plan_item_id") not in entry["plan_item_ids"]:
            fail("verification plan must reference approved coding plan items")
        checks = entry.get("verification")
        if not isinstance(checks, list) or not checks:
            fail("each verification-plan entry requires a verification method")
        levels = set()
        for check in checks:
            if not isinstance(check, dict) or check.get("level") not in {"L1", "L2", "L3", "L4"} or check.get("method") not in {"unit", "contract", "integration", "e2e", "visual", "manual"} or not isinstance(check.get("fixture_or_live_boundary"), str) or not check["fixture_or_live_boundary"] or not isinstance(check.get("expected_evidence"), str) or not check["expected_evidence"]:
                fail("verification methods require a valid method, fixture/live boundary, and expected evidence")
            levels.add(check["level"])
            if check["level"] == "L3" and entry["completion_plan_item_id"] in first_flow_plan_items:
                has_l3_first_flow = True
            if check["level"] == "L3":
                for delivery in surface_delivery:
                    if entry["acceptance_id"] in delivery["verification_acceptance_ids"] and plan_item_slice[entry["completion_plan_item_id"]] == delivery["integrated_slice_id"]:
                        has_l3_surface_delivery[delivery["ui_surface_id"]] = True
        if "L4" not in levels:
            fail("every acceptance criterion requires an L4 product-evidence trace")
        seen.add(entry["acceptance_id"])
    if logical_contract["applicability"] == "required" and not has_l3_first_flow:
        fail("the declared first end-to-end logical flow requires L3 evidence")
    if logical_contract["applicability"] == "required" and ui_surfaces and not all(has_l3_surface_delivery.values()):
        fail("every multi-UI delivery requires L3 evidence in its integrated slice")
    adversarial = matrix.get("adversarial_cases")
    if not isinstance(adversarial, list):
        fail("verification_plan adversarial_cases must be a list")
    if state["risk_level"] == "high" and not adversarial:
        fail("high-risk verification_plan requires one or more adversarial_cases")
    seen_adversarial = set()
    slice_by_item = {
        item_id: slice_record["slice_id"]
        for slice_record in plan["implementation_design"]["slice_sequence"]
        for item_id in slice_record["plan_item_ids"]
    }
    dependencies = {
        slice_record["slice_id"]: set(slice_record["depends_on"])
        for slice_record in plan["implementation_design"]["slice_sequence"]
    }

    def available_by(candidate_slice: str, completion_slice: str) -> bool:
        if candidate_slice == completion_slice:
            return True
        pending = list(dependencies[completion_slice])
        visited = set()
        while pending:
            current = pending.pop()
            if current in visited:
                continue
            if current == candidate_slice:
                return True
            visited.add(current)
            pending.extend(dependencies[current])
        return False

    fields = {"id", "plan_item_ids", "completion_plan_item_id", "risk", "injection", "safe_target_kind", "safe_target_reference", "containment", "prohibited_real_actions", "allows_external_network", "allows_live_service", "allows_secret_or_sensitive_data", "fail_closed_assertion", "cleanup"}
    for case in adversarial:
        if not isinstance(case, dict) or fields - set(case) or not isinstance(case.get("id"), str) or not case["id"] or case["id"] in seen_adversarial or case.get("safe_target_kind") not in SAFE_ADVERSARIAL_TARGET_KINDS:
            fail("adversarial cases require unique IDs and an explicit safe target kind")
        if not isinstance(case["plan_item_ids"], list) or not case["plan_item_ids"] or len(set(case["plan_item_ids"])) != len(case["plan_item_ids"]) or any(identifier not in plan_item_ids for identifier in case["plan_item_ids"]) or not isinstance(case.get("completion_plan_item_id"), str) or case["completion_plan_item_id"] not in case["plan_item_ids"] or not isinstance(case["prohibited_real_actions"], list) or not non_empty_strings(case["prohibited_real_actions"]):
            fail("adversarial cases require linked plan items, a completion item, and prohibited real actions")
        completion_slice = slice_by_item[case["completion_plan_item_id"]]
        if any(not available_by(slice_by_item[item_id], completion_slice) for item_id in case["plan_item_ids"]):
            fail("an adversarial case may complete only after every linked plan item is available")
        if any(case[field] is not False for field in {"allows_external_network", "allows_live_service", "allows_secret_or_sensitive_data"}):
            fail("an adversarial case may not allow real external, live, or sensitive actions")
        if not all(isinstance(case[field], str) and case[field].strip() for field in {"risk", "injection", "safe_target_reference", "containment", "fail_closed_assertion", "cleanup"}):
            fail("adversarial cases require an explicit safe fault-injection contract")
        seen_adversarial.add(case["id"])


def implementation_authorization_proposal(record: dict, plan: dict, plan_item_ids: set[str]) -> dict:
    proposal = record.get("implementation_authorization_proposal")
    required = {"allowed_plan_version", "allowed_plan_item_ids", "execution_mode", "stop_conditions", "prohibited_actions", "separate_approval_required_for", "approver_role"}
    policy = plan["execution_policy"]
    if not isinstance(proposal, dict) or required - set(proposal) or proposal["allowed_plan_version"] != plan["version"] or proposal["execution_mode"] != policy["mode"] or not isinstance(proposal["allowed_plan_item_ids"], list) or any(identifier not in plan_item_ids for identifier in proposal["allowed_plan_item_ids"]) or not non_empty_strings(proposal["stop_conditions"]) or set(proposal["stop_conditions"]) != set(policy["stop_conditions"]) or not non_empty_strings(proposal["prohibited_actions"]) or not non_empty_strings(proposal["separate_approval_required_for"]) or not isinstance(proposal["approver_role"], str) or not proposal["approver_role"]:
        fail("implementation_authorization_proposal is incomplete or does not match the approved plan")
    return proposal


def pbc_consistency_check(state: dict, run_dir: Path, record: dict, plan: dict, plan_item_ids: set[str]) -> Path:
    """Require a current, bounded self-check before the single PBC critic invocation."""
    check_path = required_file(run_dir, record.get("consistency_check"), "PBC consistency check")
    check = read_json(check_path, "PBC consistency check")
    if check.get("run_id") != state["run_id"] or check.get("artifact") != "pbc_consistency_check" or check.get("plan_version") != plan["version"]:
        fail("PBC consistency check must match this run and coding-plan version")
    _, coding_plan_path = simple_record(state, run_dir, "coding_plan")
    _, verification_path = simple_record(state, run_dir, "verification_plan")
    preflight = feasibility_preflight(state, plan, run_dir, plan_item_ids)
    expected_artifacts = [
        ("coding_plan", coding_plan_path),
        ("selection_register", required_file(run_dir, plan.get("selection_register"), "selection register")),
        ("verification_plan", verification_path),
        ("prebuild_contract", required_file(run_dir, record.get("path"), "pre-build contract")),
    ]
    if preflight["status"] == "verified":
        expected_artifacts.append(("feasibility_probe", required_file(run_dir, preflight["probe"]["path"], "feasibility probe")))
    elif preflight["basis"]["kind"] == "existing_observed_evidence" and preflight["basis"]["evidence"]["artifact"] == "planning_baseline":
        expected_artifacts.append(("planning_baseline", required_file(run_dir, preflight["basis"]["evidence"]["path"], "observed feasibility evidence")))
    expected_records = [
        {"artifact": name, "path": str(path.relative_to(run_dir)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for name, path in expected_artifacts
    ]
    if check.get("checked_artifacts") != expected_records:
        fail("PBC consistency check must hash the current coding plan, register, matrix, and contract exactly")
    checks = check.get("checks")
    expected_ids = {"selected_vs_rejected", "plan_vs_verification", "logical_flow_compilation", "change_representation", "feasibility_preflight"}
    if not isinstance(checks, list) or {item.get("id") for item in checks if isinstance(item, dict)} != expected_ids or len(checks) != len(expected_ids):
        fail("PBC consistency check requires each canonical consistency check exactly once")
    acceptance_ids = approved_acceptance_ids(state, run_dir)
    logical_contract = approved_logical_system_contract(state, run_dir)
    logical_flow_ids = {flow["id"] for flow in logical_contract["flows"]}
    for item in checks:
        if not isinstance(item, dict) or item.get("status") != "pass" or not isinstance(item.get("scope_ids"), list) or not item["scope_ids"] or not all(isinstance(value, str) and value for value in item["scope_ids"]) or not isinstance(item.get("finding"), str) or not item["finding"].strip():
            fail("every PBC consistency check requires a passing result, scope, and finding")
        scope = set(item["scope_ids"])
        if item["id"] == "selected_vs_rejected" and not plan_item_ids <= scope:
            fail("selected_vs_rejected must cover every plan item")
        if item["id"] == "plan_vs_verification" and not (plan_item_ids | acceptance_ids) <= scope:
            fail("plan_vs_verification must cover every plan item and acceptance criterion")
        if item["id"] == "logical_flow_compilation" and not (plan_item_ids | acceptance_ids | logical_flow_ids) <= scope:
            fail("logical_flow_compilation must cover every applicable flow, plan item, and criterion")
        if item["id"] == "feasibility_preflight" and not plan_item_ids <= scope:
            fail("feasibility_preflight must cover every plan item")
        if item["id"] == "change_representation":
            artifacts = item.get("change_artifacts")
            if not isinstance(artifacts, list):
                fail("change_representation requires a change_artifacts list")
            if record.get("parent_approval_attempt_id") and not artifacts:
                fail("a revised PBC approval attempt must check its change explanation artifacts")
            for artifact in artifacts:
                if not isinstance(artifact, dict) or not all(isinstance(artifact.get(field), str) and artifact[field] for field in {"path", "sha256"}):
                    fail("change explanation artifacts require path and sha256")
                artifact_path = required_file(run_dir, artifact["path"], "change explanation artifact")
                if hashlib.sha256(artifact_path.read_bytes()).hexdigest() != artifact["sha256"]:
                    fail("change explanation artifact hash does not match")
    for item in plan["items"]:
        selected = " ".join(item["selected_approach"].lower().split())
        if any(selected == " ".join(rejected.lower().split()) for rejected in item["rejected_approaches"] if isinstance(rejected, str)):
            fail("a coding-plan selected approach cannot also be listed as rejected")
    return check_path


def pbc_critic_sources(review: dict, state: dict, run_dir: Path, plan: dict) -> None:
    """Bind PBC critic labels to the immutable inputs and machine artifacts they name."""
    references = review.get("reference_artifacts", [])
    paths = {item.get("artifact"): item.get("path") for item in references if isinstance(item, dict)}
    if len(paths) != len(references):
        fail("PBC-4 critic references must not repeat artifact names")
    _, inputs_path = simple_record(state, run_dir, "approved_inputs")
    inputs = read_json(inputs_path, "approved inputs").get("inputs", [])
    input_paths = {
        item.get("artifact"): item.get("manifest_path")
        for item in inputs
        if isinstance(item, dict)
    }
    _, coding_plan_path = simple_record(state, run_dir, "coding_plan")
    _, verification_path = simple_record(state, run_dir, "verification_plan")
    contract = state["artifacts"].get("prebuild_contract", {})
    expected = {
        "use_case_bundle": input_paths.get("use_case_bundle"),
        "prototype_bundle": input_paths.get("prototype_bundle"),
        "coding_plan": str(coding_plan_path.relative_to(run_dir)),
        "verification_plan": str(verification_path.relative_to(run_dir)),
        "selection_register": plan.get("selection_register"),
        "pbc_consistency_check": contract.get("consistency_check") if isinstance(contract, dict) else None,
        "prebuild_contract": contract.get("path") if isinstance(contract, dict) else None,
    }
    preflight = plan["feasibility_preflight"]
    if preflight["status"] == "verified":
        expected["feasibility_probe"] = preflight["probe"]["path"]
    elif preflight["basis"]["kind"] == "existing_observed_evidence" and preflight["basis"]["evidence"]["artifact"] == "planning_baseline":
        expected["planning_baseline"] = preflight["basis"]["evidence"]["path"]
    if set(paths) != set(expected):
        fail("PBC-4 critic may read only the declared PBC sources and conditional feasibility evidence")
    for artifact_name, expected_path in expected.items():
        if not isinstance(expected_path, str) or not expected_path or paths.get(artifact_name) != expected_path:
            fail(f"PBC-4 critic must reference the current {artifact_name} artifact path")


def prebuild_contract(state: dict, run_dir: Path, plan: dict, plan_item_ids: set[str]) -> None:
    record = artifact(state, run_dir, "prebuild_contract", {"draft", "critic_passed", "approved"})
    contract_path = required_file(run_dir, record.get("path"), "pre-build contract")
    if "## Implementation authorization proposal" not in contract_path.read_text():
        fail("pre-build contract must contain an implementation authorization proposal section")
    implementation_authorization_proposal(record, plan, plan_item_ids)
    pbc_consistency_check(state, run_dir, record, plan, plan_item_ids)
    review_path = record.get("critic_review")
    attempts = record.get("critic_attempts", 0)
    if not isinstance(attempts, int) or attempts not in {0, 1}:
        fail("PBC-4 allows at most one critic invocation per approval attempt")
    if not isinstance(review_path, str) or not review_path:
        if record.get("status") == "draft":
            return
        fail("critic-passed or approved pre-build contract requires a PBC-4 critic review")
    review = read_json(run_path(run_dir, review_path, "PBC-4 critic review"), "PBC-4 critic review")
    if attempts != 1:
        fail("a recorded PBC-4 critic review requires critic_attempts=1")
    if not isinstance(record.get("approval_attempt_id"), str) or not record["approval_attempt_id"]:
        fail("a recorded PBC-4 critic review requires an approval_attempt_id")
    if review.get("gate") != "PBC-4" or review.get("verdict") not in {"pass", "revise", "ask-user"}:
        fail("PBC-4 critic review must have a pass, revise, or ask-user verdict")
    critic_references(review, "PBC-4", run_dir, state)
    pbc_critic_sources(review, state, run_dir, plan)
    if record.get("status") in {"critic_passed", "approved"} and review.get("verdict") != "pass":
        fail("critic-passed or approved pre-build contract requires a passing PBC-4 critic review")
    issues = review.get("blocking_issues")
    if not isinstance(issues, list) or any(not isinstance(issue, dict) or issue.get("category") not in PBC_CRITIC_CATEGORIES for issue in issues):
        fail("PBC-4 critic may report only plan-alignment blocking categories")
    questions = review.get("questions")
    if not isinstance(questions, list) or len(questions) > 3:
        fail("PBC-4 critic questions must be a list of at most three items")
    if review.get("verdict") == "ask-user":
        if not questions or any(not isinstance(question, dict) or question.get("why_it_changes") not in {"implementation_authority", "L1_plan_decision"} for question in questions):
            fail("PBC-4 ask-user questions may address only implementation authority or an L1 plan decision")
    if record.get("status") in {"critic_passed", "approved"}:
        director_path = required_file(run_dir, plan.get("director_review"), "director review")
        director_text = director_path.read_text()
        required_sections = ("## 한눈에 보기", "## 사용자 기대와 계획의 대응", "## Implementation design", "## Engineering, skills, and model roles", "## 승인자에게 요청할 결정")
        if any(section not in director_text for section in required_sections):
            fail("approved PBC review bundle is missing its required human-review sections")
        diagrams = plan.get("diagram_paths")
        if not isinstance(diagrams, dict) or set({"traceability", "roadmap"}) - set(diagrams):
            fail("approved PBC review bundle requires traceability and roadmap diagrams")
        for kind in ("traceability", "roadmap"):
            image_path(run_dir, diagrams[kind], f"coding plan {kind} diagram")
        boundaries = plan.get("implementation_design", {}).get("boundaries", [])
        if len(boundaries) > 1:
            design_path = diagrams.get("implementation_design")
            if not isinstance(design_path, str) or not design_path:
                fail("a multi-boundary coding plan requires an implementation-design diagram")
            image_path(run_dir, design_path, "coding plan implementation-design diagram")
        if approved_logical_system_contract(state, run_dir)["applicability"] == "required":
            sequence_path = diagrams.get("runtime_sequence")
            if not isinstance(sequence_path, str) or not sequence_path:
                fail("an applicable logical system contract requires a runtime-sequence diagram")
            image_path(run_dir, sequence_path, "coding plan runtime-sequence diagram")


def slice_execution_packet(state: dict, run_dir: Path, plan: dict, plan_item_ids: set[str]) -> tuple[set[str], Path]:
    record, path = simple_record(state, run_dir, "slice_execution_packet")
    packet = read_json(path, "slice execution packet")
    if packet.get("run_id") != state["run_id"] or packet.get("artifact") != "slice_execution_packet" or packet.get("version") != record["version"] or packet.get("plan_version") != plan["version"] or not isinstance(packet.get("slice_id"), str) or not packet["slice_id"]:
        fail("slice_execution_packet must match this run, artifact version, plan version, and slice")
    selected = packet.get("plan_item_ids")
    if not isinstance(selected, list) or not selected or len(set(selected)) != len(selected) or any(identifier not in plan_item_ids for identifier in selected):
        fail("slice_execution_packet requires valid unique plan_item_ids")
    selected_ids = set(selected)
    expected_items = {item["id"]: item for item in plan["items"] if item["id"] in selected_ids}
    packet_items = packet.get("plan_items")
    if not isinstance(packet_items, list) or {item.get("id") for item in packet_items if isinstance(item, dict)} != selected_ids or any(not isinstance(item, dict) or item != expected_items.get(item.get("id")) for item in packet_items):
        fail("slice_execution_packet must copy every selected coding-plan item exactly")

    expected_ac_ids = {acceptance for item in expected_items.values() for acceptance in item["acceptance_ids"]}
    _, matrix_path = simple_record(state, run_dir, "verification_plan")
    matrix = read_json(matrix_path, "verification plan")
    expected_verification = {entry["acceptance_id"]: entry for entry in matrix.get("acceptance_criteria", []) if isinstance(entry, dict) and entry.get("acceptance_id") in expected_ac_ids}
    expected_criteria = {entry["acceptance_id"]: entry["acceptance_criterion"] for entry in expected_verification.values()}
    packet_criteria = packet.get("acceptance_criteria")
    if not isinstance(packet_criteria, list) or {entry.get("id") for entry in packet_criteria if isinstance(entry, dict)} != expected_ac_ids or any(not isinstance(entry, dict) or entry != expected_criteria.get(entry.get("id")) for entry in packet_criteria):
        fail("slice_execution_packet must copy every linked acceptance criterion from the approved verification plan exactly")
    packet_verification = packet.get("verification_entries")
    if not isinstance(packet_verification, list) or {entry.get("acceptance_id") for entry in packet_verification if isinstance(entry, dict)} != expected_ac_ids or any(not isinstance(entry, dict) or entry != expected_verification.get(entry.get("acceptance_id")) for entry in packet_verification):
        fail("slice_execution_packet must copy every linked verification entry exactly")
    expected_adversarial = [
        case for case in matrix.get("adversarial_cases", [])
        if isinstance(case, dict) and case.get("completion_plan_item_id") in selected_ids
    ]
    if packet.get("adversarial_cases") != expected_adversarial:
        fail("slice_execution_packet must copy every applicable adversarial case exactly")

    authorization = approved_implementation_authorization(state, run_dir, plan, plan_item_ids)
    if packet.get("implementation_authorization") != authorization or set(packet.get("automatic_quality_gates", [])) != set(plan["execution_policy"]["automatic_quality_gates"]) or set(packet.get("stop_conditions", [])) != set(plan["execution_policy"]["stop_conditions"]):
        fail("slice_execution_packet must preserve the approved authorization, gates, and stop conditions")
    _, baseline_path = simple_record(state, run_dir, "planning_baseline")
    baseline = read_json(baseline_path, "planning baseline")
    if packet.get("planning_baseline") != baseline:
        fail("slice_execution_packet must copy the approved planning baseline exactly")
    revalidation = packet.get("baseline_revalidation")
    required_revalidation = {"checked_at", "repository_revision", "dependency_revision", "environment_facts", "result", "evidence_paths"}
    if not isinstance(revalidation, dict) or required_revalidation - set(revalidation) or not all(isinstance(revalidation[field], str) and revalidation[field] for field in {"checked_at", "repository_revision", "dependency_revision"}) or not isinstance(revalidation["environment_facts"], list) or revalidation["result"] != "pass" or not isinstance(revalidation["evidence_paths"], list) or not revalidation["evidence_paths"]:
        fail("slice_execution_packet requires a passing, evidenced planning-baseline revalidation")
    for evidence_path in revalidation["evidence_paths"]:
        required_file(run_dir, evidence_path, "planning-baseline revalidation evidence")
    expected_review = "independent_critic" if any(item["review_requirement"] == "independent_critic" for item in expected_items.values()) else "automatic"
    if packet.get("review_requirement") != expected_review:
        fail("slice_execution_packet review requirement must match selected plan items")

    if packet.get("unresolved_questions") != [] or packet.get("missing_information") != [] or not isinstance(packet.get("expansion_rule"), str) or not packet["expansion_rule"]:
        fail("slice_execution_packet must be complete before implementation; missing PBC contract information requires L1 or out-of-scope handling")
    return selected_ids, path


def implementation_contract(state: dict, run_dir: Path, plan: dict, plan_item_ids: set[str], packet_items: set[str], packet_path: Path) -> set[str]:
    record, path = simple_record(state, run_dir, "implementation_contract")
    contract = path.read_text()
    required_rows = ("Plan version / authorized item IDs / batch", "Baseline revalidation result", "AC and expected slice outcome", "Allowed changes / prohibited actions", "Commands and AC verifier", "Required automatic quality gates", "Review requirement and rationale", "Loop cap / stop or escalation condition")
    if "# Slice Execution Card" not in contract or "| Field | Record |" not in contract or any(row not in contract for row in required_rows):
        fail("implementation_contract must be the required compact G4 execution card")
    selected = record.get("plan_item_ids")
    authorization = approved_implementation_authorization(state, run_dir, plan, plan_item_ids)
    if not isinstance(selected, list) or not selected or len(set(selected)) != len(selected) or set(selected) != packet_items or any(identifier not in plan_item_ids for identifier in selected):
        fail("implementation_contract requires valid unique plan_item_ids")
    if not isinstance(authorization, dict) or authorization.get("authorized") is not True or record.get("plan_version") != plan["version"] or any(identifier not in authorization.get("allowed_plan_item_ids", []) for identifier in selected):
        fail("implementation_contract must use only PBC-authorized plan items and version")
    if record.get("baseline_revalidated") is not True:
        fail("implementation_contract requires a completed planning-baseline revalidation")
    packet = read_json(packet_path, "slice execution packet")
    if packet.get("baseline_revalidation", {}).get("result") != "pass":
        fail("implementation_contract requires a passing baseline revalidation in its execution packet")
    if record.get("execution_packet") != str(packet_path.relative_to(run_dir)) or record.get("execution_packet_sha256") != hashlib.sha256(packet_path.read_bytes()).hexdigest():
        fail("implementation_contract must point to the exact validated slice execution packet")
    return set(selected)


def execution_ledger(state: dict, run_dir: Path, plan: dict, selected_items: set[str]) -> None:
    _, path = simple_record(state, run_dir, "execution_ledger")
    ledger = read_json(path, "execution ledger")
    if ledger.get("run_id") != state["run_id"] or ledger.get("artifact") != "execution_ledger" or ledger.get("plan_version") != plan["version"] or set(ledger.get("plan_item_ids", [])) != selected_items:
        fail("execution_ledger must match this run, plan version, and G4 selected items")
    entries = ledger.get("entries")
    if not isinstance(entries, list) or len(entries) != len(selected_items) or {entry.get("plan_item_id") for entry in entries if isinstance(entry, dict)} != selected_items:
        fail("execution_ledger requires one entry for every selected plan item")
    for entry in entries:
        required = {"plan_item_id", "changed_files", "commands", "automatic_quality_gates", "verifier_result", "evidence_paths", "l0_decisions"}
        if not isinstance(entry, dict) or required - set(entry) or entry["verifier_result"] not in {"pass", "fail", "blocked"} or not all(isinstance(entry[field], list) for field in {"changed_files", "commands", "automatic_quality_gates", "evidence_paths", "l0_decisions"}):
            fail("execution-ledger entries are incomplete")
        for evidence in entry["evidence_paths"]:
            required_file(run_dir, evidence, "execution evidence")
        if entry["verifier_result"] == "pass" and not entry["evidence_paths"]:
            fail("a passing execution-ledger entry requires evidence")
        gates = entry["automatic_quality_gates"]
        expected_gates = set(plan["execution_policy"]["automatic_quality_gates"])
        if {gate.get("name") for gate in gates if isinstance(gate, dict)} != expected_gates:
            fail("execution-ledger entries must record every planned automatic quality gate")
        for gate in gates:
            if not isinstance(gate, dict) or gate.get("result") not in {"pass", "fail", "blocked"} or not isinstance(gate.get("evidence_paths"), list):
                fail("automatic quality gates require a result and evidence paths")
            for evidence in gate["evidence_paths"]:
                required_file(run_dir, evidence, "automatic quality-gate evidence")
            if gate["result"] == "pass" and not gate["evidence_paths"]:
                fail("a passing automatic quality gate requires evidence")
    unexpected_facts = ledger.get("unexpected_facts")
    if not isinstance(unexpected_facts, list):
        fail("execution_ledger requires an unexpected_facts list")
    fact_ids = set()
    required_fact = {"id", "observation", "evidence_paths", "affected_plan_item_ids", "affected_assumptions_or_controls", "impact", "recheck_result", "rationale"}
    for fact in unexpected_facts:
        if not isinstance(fact, dict) or required_fact - set(fact) or not isinstance(fact.get("id"), str) or not fact["id"] or fact["id"] in fact_ids or fact.get("impact") not in {"none", "L0", "L1", "out_of_scope_contract_change"} or fact.get("recheck_result") not in {"pass", "amendment_required", "blocked"}:
            fail("unexpected facts require a unique ID, valid impact, and recheck result")
        if not isinstance(fact["evidence_paths"], list) or not fact["evidence_paths"] or not isinstance(fact["affected_plan_item_ids"], list) or not fact["affected_plan_item_ids"]:
            fail("unexpected facts require evidence and a valid affected-plan-item list")
        if any(identifier not in {item["id"] for item in plan["items"]} for identifier in fact["affected_plan_item_ids"]) or not isinstance(fact["affected_assumptions_or_controls"], list) or not all(isinstance(value, str) and value for value in fact["affected_assumptions_or_controls"]) or not all(isinstance(fact[field], str) and fact[field].strip() for field in {"observation", "rationale"}):
            fail("unexpected facts must identify affected plans, assumptions or controls, and rationale")
        if fact["impact"] in {"none", "L0"} and fact["recheck_result"] != "pass":
            fail("a none or L0 unexpected fact must have a passing recheck")
        if fact["impact"] == "L1" and fact["recheck_result"] != "amendment_required":
            fail("an L1 unexpected fact must require an amendment")
        if fact["impact"] == "out_of_scope_contract_change" and fact["recheck_result"] != "blocked":
            fail("an out-of-scope unexpected fact must block the run")
        for evidence_path in fact["evidence_paths"]:
            required_file(run_dir, evidence_path, "unexpected-fact evidence")
        fact_ids.add(fact["id"])
    loop = ledger.get("loop")
    if not isinstance(loop, dict) or not isinstance(loop.get("used"), bool) or not isinstance(loop.get("cap"), str) or not isinstance(loop.get("outcome"), str) or (loop["used"] and (not loop["cap"] or not loop["outcome"])):
        fail("execution_ledger requires a bounded-loop record")


def verification_report(state: dict, run_dir: Path, plan: dict, selected_items: set[str]) -> None:
    _, path = simple_record(state, run_dir, "verification_report")
    report = read_json(path, "verification report")
    expected_ac = {acceptance for item in plan["items"] if item["id"] in selected_items for acceptance in item["acceptance_ids"]}
    if report.get("run_id") != state["run_id"] or report.get("artifact") != "verification_report" or report.get("plan_version") != plan["version"]:
        fail("verification_report must match this run and plan version")
    criteria = report.get("criteria")
    expected_review = "independent_critic" if any(item["id"] in selected_items and item["review_requirement"] == "independent_critic" for item in plan["items"]) else "automatic"
    if report.get("review_requirement") != expected_review or not isinstance(report.get("review_rationale"), str) or not report["review_rationale"]:
        fail("verification_report review requirement must match the selected plan items and explain why")
    if not isinstance(criteria, list) or len(criteria) != len(expected_ac) or {item.get("acceptance_id") for item in criteria if isinstance(item, dict)} != expected_ac:
        fail("verification_report must cover every AC in the implemented slice")
    _, matrix_path = simple_record(state, run_dir, "verification_plan")
    matrix = read_json(matrix_path, "verification plan")
    completion_by_ac = {entry.get("acceptance_id"): entry.get("completion_plan_item_id") for entry in matrix.get("acceptance_criteria", []) if isinstance(entry, dict)}
    for item in criteria:
        completion = completion_by_ac.get(item.get("acceptance_id")) if isinstance(item, dict) else None
        if not isinstance(item, dict) or item.get("result") not in {"pass", "fail", "blocked", "deferred"} or item.get("completion_plan_item_id") != completion or not isinstance(item.get("plan_item_ids"), list) or not item["plan_item_ids"] or any(identifier not in selected_items for identifier in item["plan_item_ids"]) or not isinstance(item.get("assertion_summary"), str) or not item["assertion_summary"] or not isinstance(item.get("evidence_paths"), list):
            fail("verification-report criteria are incomplete")
        for evidence in item["evidence_paths"]:
            required_file(run_dir, evidence, "verification evidence")
        if item["result"] in {"pass", "deferred"} and not item["evidence_paths"]:
            fail("a passing or deferred verification-report criterion requires evidence")
        if item["result"] == "deferred" and completion in selected_items:
            fail("a criterion cannot be deferred in its assigned completion slice")
    expected_adversarial = [
        case for case in matrix.get("adversarial_cases", [])
        if isinstance(case, dict) and case.get("completion_plan_item_id") in selected_items
    ]
    results = report.get("adversarial_results")
    if not isinstance(results, list) or {result.get("id") for result in results if isinstance(result, dict)} != {case["id"] for case in expected_adversarial}:
        fail("verification-report must cover every applicable adversarial case exactly once")
    expected_cases = {case["id"]: case for case in expected_adversarial}
    for result in results:
        expected_case = expected_cases.get(result.get("id")) if isinstance(result, dict) else None
        if not isinstance(result, dict) or expected_case is None or result.get("plan_item_ids") != expected_case["plan_item_ids"] or result.get("result") not in {"pass", "fail", "blocked"} or not isinstance(result.get("assertion_summary"), str) or not result["assertion_summary"] or not isinstance(result.get("evidence_paths"), list):
            fail("adversarial verification results are incomplete or do not match the approved case")
        for evidence_path in result["evidence_paths"]:
            required_file(run_dir, evidence_path, "adversarial verification evidence")
        if result["result"] == "pass" and not result["evidence_paths"]:
            fail("a passing adversarial verification result requires evidence")
    review_path = report.get("independent_critic_review")
    if expected_review == "independent_critic":
        review = read_json(run_path(run_dir, review_path, "G6 critic review"), "G6 critic review")
        if review.get("gate") != "G6" or review.get("verdict") != "pass":
            fail("an independent-critic slice requires a passing G6 critic review")
        critic_references(review, "G6", run_dir, state)
    elif review_path is not None:
        fail("an automatic slice must not require an independent G6 critic review")


def cycle_decision(state: dict, run_dir: Path, plan: dict, selected_items: set[str]) -> None:
    record, path = simple_record(state, run_dir, "cycle_decision")
    text = path.read_text()
    headings = ("## Verified result", "## Decision", "## Evidence and remaining plan items", "## Mismatch classification", "## Unexpected-fact impact check", "## Required next action", "## Final Integration Critic Review", "## Batch Evidence Index")
    if any(heading not in text for heading in headings):
        fail("cycle_decision is missing a required G7 section")
    decision = record.get("decision")
    mismatch = record.get("mismatch_classification")
    if decision not in {"next_slice", "complete", "repair", "amendment", "blocked"} or mismatch not in {"none", "L0", "L1", "out_of_scope_contract_change"}:
        fail("cycle_decision requires a valid decision and mismatch classification")
    if decision == "amendment" and mismatch != "L1":
        fail("an amendment decision requires an L1 mismatch")
    if decision == "blocked" and mismatch != "out_of_scope_contract_change":
        fail("a blocked decision requires an out-of-scope contract change")
    _, verification_path = simple_record(state, run_dir, "verification_report")
    verification = read_json(verification_path, "verification report")
    _, ledger_path = simple_record(state, run_dir, "execution_ledger")
    ledger = read_json(ledger_path, "execution ledger")
    fact_impacts = {fact.get("impact") for fact in ledger.get("unexpected_facts", []) if isinstance(fact, dict)}
    if "L1" in fact_impacts and (mismatch != "L1" or decision != "amendment"):
        fail("an L1 unexpected fact requires an amendment cycle decision")
    if "out_of_scope_contract_change" in fact_impacts and (mismatch != "out_of_scope_contract_change" or decision != "blocked"):
        fail("an out-of-scope unexpected fact requires a blocked cycle decision")
    if decision in {"next_slice", "complete"} and any(result.get("result") != "pass" for result in verification.get("adversarial_results", []) if isinstance(result, dict)):
        fail("next_slice or complete requires every current-slice adversarial verifier to pass")
    if decision == "next_slice":
        if any(item.get("result") not in {"pass", "deferred"} for item in verification.get("criteria", []) if isinstance(item, dict)):
            fail("next_slice requires every current-slice criterion to pass or be assigned to a later completion slice")
        for entry in ledger.get("entries", []):
            if not isinstance(entry, dict) or entry.get("verifier_result") != "pass" or any(not isinstance(gate, dict) or gate.get("result") != "pass" for gate in entry.get("automatic_quality_gates", [])):
                fail("next_slice requires passing verifier and automatic quality gates")
        authorization = approved_implementation_authorization(
            state, run_dir, plan, {item["id"] for item in plan["items"]}
        )
        if authorization.get("execution_mode") == "continuous_batch" and not selected_items <= set(authorization.get("allowed_plan_item_ids", [])):
            fail("continuous batch next_slice requires PBC-authorized items")
    if decision == "complete":
        batch_evidence_index(state, run_dir, plan, selected_items, record)
        final_review = read_json(run_path(run_dir, record.get("final_integration_critic_review"), "final integration critic review"), "final integration critic review")
        if final_review.get("gate") != "G6" or final_review.get("verdict") != "pass":
            fail("complete requires a passing final integration critic review")
        critic_references(final_review, "G6", run_dir, state)
    if mismatch == "L1":
        required_file(run_dir, record.get("learning_record"), "plan learning record")
    if mismatch == "out_of_scope_contract_change":
        contract_change = required_file(run_dir, record.get("out_of_scope_contract_change"), "out-of-scope contract-change record")
        headings = ("# Out-of-scope Contract Change", "## Observed evidence", "## Conflicting approved contract", "## Required later decision", "## Factory boundary")
        if any(heading not in contract_change.read_text() for heading in headings):
            fail("out-of-scope contract-change record is missing required sections")


def batch_evidence_index(state: dict, run_dir: Path, plan: dict, selected_items: set[str], decision: dict) -> None:
    index = read_json(run_path(run_dir, decision.get("batch_evidence_index"), "batch evidence index"), "batch evidence index")
    if index.get("run_id") != state["run_id"] or index.get("artifact") != "batch_evidence_index" or not isinstance(index.get("version"), str) or not index["version"] or index.get("plan_version") != plan["version"]:
        fail("batch_evidence_index must match this run and approved plan version")
    scope = index.get("scope_plan_item_ids")
    if not isinstance(scope, list) or not scope or len(set(scope)) != len(scope) or any(identifier not in {item["id"] for item in plan["items"]} for identifier in scope) or not selected_items <= set(scope):
        fail("batch evidence index must declare a valid scope including the final slice")
    authorization = approved_implementation_authorization(
        state, run_dir, plan, {item["id"] for item in plan["items"]}
    )
    if authorization.get("execution_mode") == "continuous_batch" and set(scope) != set(authorization.get("allowed_plan_item_ids", [])):
        fail("continuous-batch evidence index must cover every PBC-authorized batch item")
    slices = index.get("slices")
    if not isinstance(slices, list) or not slices:
        fail("batch evidence index requires one or more completed slice records")
    covered, slice_ids = set(), set()
    for slice_record in slices:
        if not isinstance(slice_record, dict) or not isinstance(slice_record.get("slice_id"), str) or not slice_record["slice_id"] or slice_record["slice_id"] in slice_ids:
            fail("batch evidence index requires unique slice IDs")
        item_ids = slice_record.get("plan_item_ids")
        if not isinstance(item_ids, list) or not item_ids or len(set(item_ids)) != len(item_ids) or any(identifier not in scope for identifier in item_ids):
            fail("batch evidence index slice items must be within the declared scope")
        slice_ids.add(slice_record["slice_id"])
        covered.update(item_ids)
        for artifact_key, expected_artifact in (("execution_packet", "slice_execution_packet"), ("execution_ledger", "execution_ledger"), ("verification_report", "verification_report")):
            pointer = slice_record.get(artifact_key)
            if not isinstance(pointer, dict) or not isinstance(pointer.get("path"), str) or not pointer["path"] or not isinstance(pointer.get("sha256"), str) or not pointer["sha256"]:
                fail("batch evidence index artifact pointers require path and sha256")
            path = required_file(run_dir, pointer["path"], f"batch {artifact_key}")
            if hashlib.sha256(path.read_bytes()).hexdigest() != pointer["sha256"]:
                fail("batch evidence index artifact hash does not match")
            artifact_data = read_json(path, f"batch {artifact_key}")
            if expected_artifact == "verification_report":
                artifact_item_ids = {
                    identifier
                    for criterion in artifact_data.get("criteria", [])
                    if isinstance(criterion, dict)
                    for identifier in criterion.get("plan_item_ids", [])
                    if isinstance(identifier, str)
                }
            else:
                artifact_item_ids = set(artifact_data.get("plan_item_ids", []))
            if artifact_data.get("run_id") != state["run_id"] or artifact_data.get("artifact") != expected_artifact or artifact_data.get("plan_version") != plan["version"] or artifact_data.get("slice_id") != slice_record["slice_id"] or artifact_item_ids != set(item_ids):
                fail("batch evidence index artifact does not match its slice scope")
    if covered != set(scope):
        fail("batch evidence index must cover every declared plan item")


def acceptance_criteria(run_dir: Path, relative_path: str, version: str, scenario_ids: set[str]) -> dict[str, set[str]]:
    criteria_file = read_json(run_path(run_dir, relative_path, "acceptance criteria"), "acceptance criteria")
    if criteria_file.get("artifact") != "use_case" or criteria_file.get("artifact_version") != version:
        fail("acceptance criteria must match the use_case version")
    criteria = criteria_file.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        fail("acceptance criteria requires at least one criterion")
    condition_ids: dict[str, set[str]] = {}
    for criterion in criteria:
        required = {"id", "statement", "scenario_refs", "observable_conditions"}
        if not isinstance(criterion, dict) or required - set(criterion):
            fail("each acceptance criterion requires id, statement, scenario_refs, and observable_conditions")
        criterion_id = criterion["id"]
        if not isinstance(criterion_id, str) or not criterion_id or criterion_id in condition_ids:
            fail("acceptance criterion IDs must be non-empty and unique")
        scenario_refs = criterion["scenario_refs"]
        if not isinstance(scenario_refs, list) or not scenario_refs or any(ref not in scenario_ids for ref in scenario_refs):
            fail("acceptance criterion scenario_refs must name existing scenarios")
        conditions = criterion["observable_conditions"]
        if not isinstance(conditions, list) or not conditions:
            fail("each acceptance criterion requires observable conditions")
        ids = set()
        for condition in conditions:
            if not isinstance(condition, dict) or not isinstance(condition.get("id"), str) or not condition["id"] or not isinstance(condition.get("expected"), str) or not condition["expected"]:
                fail("each observable condition requires a non-empty id and expected result")
            if condition["id"] in ids:
                fail("observable condition IDs must be unique within an acceptance criterion")
            ids.add(condition["id"])
        condition_ids[criterion_id] = ids
    return condition_ids


def risk_controls(run_dir: Path, relative_path: str, version: str, acceptance_ids: set[str]) -> None:
    controls = read_json(run_path(run_dir, relative_path, "risk controls"), "risk controls")
    if controls.get("artifact") != "use_case" or controls.get("artifact_version") != version:
        fail("risk controls must match the use_case version")
    failure_controls = controls.get("failure_controls")
    if not isinstance(failure_controls, list) or not failure_controls:
        fail("high-risk use cases require failure controls")
    for item in failure_controls:
        ids = item.get("acceptance_ids") if isinstance(item, dict) else None
        if not isinstance(item, dict) or not isinstance(item.get("failure_cost"), str) or not item["failure_cost"] or not isinstance(item.get("mitigation"), str) or not item["mitigation"] or not isinstance(ids, list) or not ids or any(identifier not in acceptance_ids for identifier in ids):
            fail("each failure control requires failure_cost, mitigation, and valid acceptance_ids")
    authority = controls.get("development_authority")
    required = {"external_calls", "secrets", "cost_limit", "irreversible_actions"}
    if not isinstance(authority, dict) or required - set(authority) or any(not isinstance(authority[field], str) or not authority[field] for field in required):
        fail("high-risk use cases require complete development_authority controls")


def page_inventory_details(
    run_dir: Path,
    relative_path: str,
    version: str,
    approved_scenario_ids: set[str] | None = None,
    logical_flows: dict[str, set[str]] | None = None,
    ui_surfaces: dict[str, dict] | None = None,
) -> dict[str, list[str]]:
    """Return the page/state inventory and, when available, close every G1 scenario."""
    inventory = read_json(run_path(run_dir, relative_path, "page inventory"), "page inventory")
    if inventory.get("artifact") != "wireframe_structure" or inventory.get("artifact_version") != version:
        fail("page inventory must match the wireframe_structure version")
    pages = inventory.get("pages")
    if not isinstance(pages, list) or not pages:
        fail("page inventory requires at least one page")
    page_states: dict[str, list[str]] = {}
    page_scenario_refs: dict[str, set[str]] = {}
    for page in pages:
        required = {"id", "title", "scenario_refs", "logical_flow_refs", "ui_surface_ids", "comparison_states"}
        if not isinstance(page, dict) or required - set(page):
            fail("each page inventory entry requires id, title, scenario_refs, and comparison_states")
        if not isinstance(page["id"], str) or not page["id"] or page["id"] in page_states:
            fail("page inventory IDs must be non-empty and unique")
        if not isinstance(page["scenario_refs"], list) or not page["scenario_refs"]:
            fail("each page inventory entry requires scenario_refs")
        if approved_scenario_ids is not None and (
            any(not isinstance(ref, str) or ref not in approved_scenario_ids for ref in page["scenario_refs"])
        ):
            fail("page inventory scenario_refs must name approved G1 scenarios")
        if not isinstance(page["ui_surface_ids"], list) or len(set(page["ui_surface_ids"])) != len(page["ui_surface_ids"]):
            fail("page inventory ui_surface_ids must be a unique list")
        if ui_surfaces:
            expected_surface_ids = {
                surface_id
                for surface_id, surface in ui_surfaces.items()
                if set(page["scenario_refs"]) & set(surface["required_scenario_ids"])
            }
            if not page["ui_surface_ids"] or any(surface_id not in ui_surfaces for surface_id in page["ui_surface_ids"]) or set(page["ui_surface_ids"]) != expected_surface_ids:
                fail("multi-UI pages must name exactly the surfaces of their scenarios")
        elif ui_surfaces is not None and page["ui_surface_ids"]:
            fail("single or non_ui products may not add page ui_surface_ids")
        if not isinstance(page["logical_flow_refs"], list) or len(set(page["logical_flow_refs"])) != len(page["logical_flow_refs"]):
            fail("page inventory logical_flow_refs must be a unique list")
        if logical_flows is not None:
            if any(ref not in logical_flows for ref in page["logical_flow_refs"]):
                fail("page inventory logical_flow_refs must name approved logical flows")
            expected_flows = {flow_id for flow_id, scenarios in logical_flows.items() if scenarios & set(page["scenario_refs"])}
            if set(page["logical_flow_refs"]) != expected_flows:
                fail("page inventory must map each page scenario to its applicable logical flow")
        if not isinstance(page["comparison_states"], list) or not page["comparison_states"] or not all(isinstance(state, str) and state for state in page["comparison_states"]) or len(set(page["comparison_states"])) != len(page["comparison_states"]):
            fail("each page inventory entry requires comparison_states")
        page_states[page["id"]] = page["comparison_states"]
        page_scenario_refs[page["id"]] = set(page["scenario_refs"])
    if approved_scenario_ids is not None:
        handoffs = inventory.get("scenario_handoffs")
        if not isinstance(handoffs, list) or len(handoffs) != len(approved_scenario_ids):
            fail("page inventory requires exactly one scenario_handoff for every approved G1 scenario")
        seen_scenarios: set[str] = set()
        page_state_scenarios: set[str] = set()
        for handoff in handoffs:
            required = {"scenario_id", "representation", "page_state_refs", "logical_flow_refs", "reason"}
            if not isinstance(handoff, dict) or required - set(handoff):
                fail("each scenario_handoff requires scenario, representation, page/state refs, and reason")
            scenario_id = handoff["scenario_id"]
            representation = handoff["representation"]
            refs = handoff["page_state_refs"]
            flow_refs = handoff["logical_flow_refs"]
            reason = handoff["reason"]
            if not isinstance(scenario_id, str) or scenario_id not in approved_scenario_ids or scenario_id in seen_scenarios:
                fail("scenario_handoffs must name every approved G1 scenario exactly once")
            if representation not in {"page_state", "non_ui"} or not isinstance(refs, list) or not isinstance(flow_refs, list) or not isinstance(reason, str):
                fail("scenario_handoffs has an invalid representation, page/state refs, or reason")
            if logical_flows is not None:
                expected_flows = {flow_id for flow_id, scenarios in logical_flows.items() if scenario_id in scenarios}
                if set(flow_refs) != expected_flows:
                    fail("scenario_handoffs must map each scenario to its applicable logical flow")
            elif flow_refs:
                fail("not_applicable logical system contracts may not add page-inventory flow refs")
            if representation == "page_state":
                valid_refs = {f"{page_id}:{state}" for page_id, states in page_states.items() for state in states}
                if not refs or len(set(refs)) != len(refs) or any(not isinstance(ref, str) or ref not in valid_refs for ref in refs):
                    fail("page_state scenario_handoffs require valid unique inventory Page:State references")
                if any(scenario_id not in page_scenario_refs[ref.split(":", 1)[0]] for ref in refs):
                    fail("page_state scenario_handoffs must agree with the referenced page scenario_refs")
                if reason.strip():
                    fail("page_state scenario_handoffs must not carry a non-UI reason")
                page_state_scenarios.add(scenario_id)
            elif refs or not reason.strip():
                fail("non_ui scenario_handoffs require no page/state refs and a reason")
            seen_scenarios.add(scenario_id)
        if seen_scenarios != approved_scenario_ids:
            fail("scenario_handoffs must cover every approved G1 scenario")
        if set().union(*page_scenario_refs.values()) != page_state_scenarios:
            fail("page inventory scenario_refs must exactly match page_state scenario_handoffs")
    return page_states


def page_inventory(run_dir: Path, relative_path: str, version: str) -> list[str]:
    return list(page_inventory_details(run_dir, relative_path, version))


def page_ui_surface_ids(run_dir: Path, relative_path: str, version: str) -> dict[str, set[str]]:
    inventory = read_json(run_path(run_dir, relative_path, "page inventory"), "page inventory")
    if inventory.get("artifact") != "wireframe_structure" or inventory.get("artifact_version") != version:
        fail("page inventory must match the wireframe_structure version")
    pages = inventory.get("pages")
    if not isinstance(pages, list):
        fail("page inventory requires pages")
    return {
        page["id"]: set(page.get("ui_surface_ids", []))
        for page in pages
        if isinstance(page, dict) and isinstance(page.get("id"), str) and isinstance(page.get("ui_surface_ids", []), list)
    }


def blueprint_document(run_dir: Path, relative_path: str, page_states: dict[str, list[str]], name: str) -> None:
    document = required_file(run_dir, relative_path, name)
    text = document.read_text()
    for heading in ("## Page blueprints", "## Rendering rule"):
        if heading not in text:
            fail(f"{name} is missing required section: {heading}")
    for page_id, states in page_states.items():
        for state in states:
            if f"### {page_id} / {state}" not in text:
                fail(f"{name} must contain a page blueprint for {page_id} / {state}")


def candidate_brief_document(run_dir: Path, relative_path: str, name: str) -> None:
    document = required_file(run_dir, relative_path, name)
    text = document.read_text()
    for heading in ("## Reference patterns", "## Reference surface and discovery route", "## Candidate work model", "## Candidate viability", "## Product-specific adaptations", "## Decision screens", "## Candidate page evidence", "## Observable differences from other candidates", "## Page inventory coverage"):
        if heading not in text:
            fail(f"{name} is missing required section: {heading}")


def reference_strategy(record: dict, page_states: dict[str, list[str]]) -> None:
    strategy = record.get("reference_strategy")
    surfaces = strategy.get("surfaces") if isinstance(strategy, dict) else None
    if not isinstance(surfaces, list) or not surfaces:
        fail("wireframe_structure requires a reference_strategy for every page group")
    research_scope = strategy.get("research_scope") if isinstance(strategy, dict) else None
    scope_required = {"public_web_research_authorized", "permitted_public_source_urls", "user_provided_source_urls", "open_discovery_surface_ids", "outside_route_policy", "restricted_access_policy"}
    if not isinstance(research_scope, dict) or scope_required - set(research_scope):
        fail("reference_strategy requires a complete research_scope before G2A investigation")
    if not isinstance(research_scope["public_web_research_authorized"], bool) or research_scope["outside_route_policy"] != "ask_user" or research_scope["restricted_access_policy"] != "ask_user":
        fail("research_scope requires explicit web authority and ask-user expansion policies")
    for field in ("permitted_public_source_urls", "user_provided_source_urls", "open_discovery_surface_ids"):
        if not isinstance(research_scope[field], list) or len(set(research_scope[field])) != len(research_scope[field]):
            fail(f"research_scope {field} must be a unique list")
    if any(not isinstance(url, str) or not url.startswith(("https://", "http://")) for field in ("permitted_public_source_urls", "user_provided_source_urls") for url in research_scope[field]):
        fail("research_scope source URLs must be absolute HTTP(S) URLs")
    if not research_scope["public_web_research_authorized"] and research_scope["permitted_public_source_urls"]:
        fail("public source investigation requires explicit public web research authority")
    expected_page_ids = set(page_states)
    seen_page_ids: set[str] = set()
    seen_surface_ids: set[str] = set()
    required = {"id", "page_ids", "classification", "workflow_signals", "classification_evidence", "discovery_mode", "source_guides"}
    for surface in surfaces:
        if not isinstance(surface, dict) or required - set(surface):
            fail("each reference surface requires ID, pages, classification, signals, evidence, mode, and source guides")
        page_ids = surface["page_ids"]
        classification = surface["classification"]
        signals = surface["workflow_signals"]
        evidence = surface["classification_evidence"]
        guides = surface["source_guides"]
        if not isinstance(surface["id"], str) or not surface["id"] or surface["id"] in seen_surface_ids:
            fail("reference surface IDs must be non-empty and unique")
        if not isinstance(page_ids, list) or not page_ids or len(set(page_ids)) != len(page_ids) or any(not isinstance(page_id, str) or page_id not in expected_page_ids or page_id in seen_page_ids for page_id in page_ids):
            fail("reference surface page IDs must be non-empty, valid, and assigned once")
        if classification not in REFERENCE_SURFACE_CLASSES or surface["discovery_mode"] not in {"curated", "open"}:
            fail("reference surface has an invalid classification or discovery mode")
        if not isinstance(signals, list) or len(set(signals)) != len(signals) or any(signal not in WORKFLOW_SIGNALS for signal in signals):
            fail("reference surface workflow_signals must use known unique values")
        if not isinstance(evidence, list) or not evidence or not all(isinstance(item, str) and item.strip() for item in evidence):
            fail("reference surface requires non-empty classification evidence")
        if not isinstance(guides, list) or not all(isinstance(url, str) and url.startswith(("https://", "http://")) for url in guides):
            fail("reference surface source_guides must be absolute HTTP(S) URLs")
        if classification == "workflow_product" and len(signals) < 2:
            fail("workflow_product requires at least two observed workflow signals")
        if classification == "general_utility" and len(signals) >= 2:
            fail("general_utility is unavailable when two or more workflow signals are present")
        if classification == "general_utility" and surface["discovery_mode"] != "open":
            fail("general_utility must use open discovery rather than a fixed source route")
        if classification != "general_utility" and (surface["discovery_mode"] != "curated" or not guides):
            fail("game, marketing, interactive, and workflow surfaces require a named curated source route")
        if classification != "general_utility" and not CURATED_ROUTE_GUIDES[classification] & set(guides):
            fail("reference surface must include the curated source guide for its classification")
        allowed_sources = set(research_scope["permitted_public_source_urls"]) | set(research_scope["user_provided_source_urls"])
        if classification != "general_utility" and not set(guides) <= allowed_sources:
            fail("reference surface source guides must be inside the recorded research scope")
        seen_surface_ids.add(surface["id"])
        seen_page_ids.update(page_ids)
    if seen_page_ids != expected_page_ids:
        fail("reference_strategy must classify every page inventory ID exactly once")
    surface_ids = seen_surface_ids
    if any(not isinstance(identifier, str) or identifier not in surface_ids for identifier in research_scope["open_discovery_surface_ids"]):
        fail("research_scope open discovery IDs must name classified surfaces")
    general_surface_ids = {surface["id"] for surface in surfaces if surface["classification"] == "general_utility"}
    if set(research_scope["open_discovery_surface_ids"]) != general_surface_ids:
        fail("research_scope open discovery IDs must be exactly the general_utility surfaces")
    if general_surface_ids and not research_scope["public_web_research_authorized"]:
        fail("general_utility cannot begin open discovery without explicit public web research authority")


def candidate_work_models(record: dict, candidates: dict) -> None:
    """Require viable candidate pairs to differ in structural, not decorative, ways."""
    models = record.get("candidate_work_models")
    if not isinstance(models, dict) or set(models) != set(candidates):
        fail("wireframe_structure requires one explicit work model for every structure candidate")
    normalized: dict[str, tuple[str, ...]] = {}
    for candidate_id, model in models.items():
        if not isinstance(model, dict) or set(model) != set(WORK_MODEL_FIELDS):
            fail(f"structure candidate {candidate_id} work model requires exactly the eight structural axes")
        if not all(isinstance(model[field], str) and model[field].strip() for field in WORK_MODEL_FIELDS):
            fail(f"structure candidate {candidate_id} work model requires non-empty structural axes")
        normalized[candidate_id] = tuple(model[field].strip().casefold() for field in WORK_MODEL_FIELDS)
    candidate_ids = list(normalized)
    for index, left in enumerate(candidate_ids):
        for right in candidate_ids[index + 1:]:
            differences = {field for field, left_value, right_value in zip(WORK_MODEL_FIELDS, normalized[left], normalized[right]) if left_value != right_value}
            if len(differences) < 3 or not differences & FOUNDATIONAL_WORK_MODEL_FIELDS:
                fail(f"structure candidates {left} and {right} must differ on one foundational and three total structural axes")


def candidate_page_evidence(
    run_dir: Path,
    record: dict,
    candidates: dict,
    page_states: dict[str, list[str]],
    approved_scenario_ids: set[str],
    reference_ids: set[str],
    briefs: dict,
) -> dict[str, set[str]]:
    evidence_map = record.get("candidate_page_evidence")
    if not isinstance(evidence_map, dict) or set(evidence_map) != set(candidates):
        fail("wireframe_structure requires candidate_page_evidence for every candidate")
    task_fields = {"actor", "object", "primary_action", "completion_judgment", "required_information"}
    scenario_refs_by_candidate: dict[str, set[str]] = {}
    for candidate_id in candidates:
        pages = evidence_map[candidate_id]
        if not isinstance(pages, dict) or set(pages) != set(page_states):
            fail(f"candidate_page_evidence must cover every page for {candidate_id}")
        brief_text = required_file(run_dir, briefs[candidate_id], f"structure candidate {candidate_id} brief").read_text()
        scenario_refs_by_candidate[candidate_id] = set()
        for page_id, states in page_states.items():
            item = pages[page_id]
            required = {"states", "page_task", "match_type", "reference_ids", "borrowed_principle", "contract_design_reason", "adaptation_ids", "scenario_refs"}
            if not isinstance(item, dict) or required - set(item):
                fail(f"candidate_page_evidence {candidate_id} / {page_id} is incomplete")
            if not isinstance(item["states"], list) or set(item["states"]) != set(states) or len(item["states"]) != len(states):
                fail(f"candidate_page_evidence {candidate_id} / {page_id} must cover exactly every comparison state")
            task = item["page_task"]
            if not isinstance(task, dict) or set(task) != task_fields or not all(isinstance(task[field], str) and task[field].strip() for field in task_fields):
                fail(f"candidate_page_evidence {candidate_id} / {page_id} requires a complete page task")
            match_type = item["match_type"]
            reference_refs = item["reference_ids"]
            adaptation_ids = item["adaptation_ids"]
            scenario_refs = item["scenario_refs"]
            if match_type not in {"direct", "principle", "contract_designed"}:
                fail(f"candidate_page_evidence {candidate_id} / {page_id} has an invalid match_type")
            if not isinstance(reference_refs, list) or len(set(reference_refs)) != len(reference_refs) or any(not isinstance(ref, str) or ref not in reference_ids for ref in reference_refs):
                fail(f"candidate_page_evidence {candidate_id} / {page_id} has invalid reference IDs")
            if not isinstance(adaptation_ids, list) or not adaptation_ids or any(not isinstance(identifier, str) or not identifier or identifier not in brief_text for identifier in adaptation_ids):
                fail(f"candidate_page_evidence {candidate_id} / {page_id} requires adaptation IDs recorded in its brief")
            if not isinstance(scenario_refs, list) or not scenario_refs or any(not isinstance(ref, str) or ref not in approved_scenario_ids for ref in scenario_refs):
                fail(f"candidate_page_evidence {candidate_id} / {page_id} requires approved G1 scenario references")
            scenario_refs_by_candidate[candidate_id].update(scenario_refs)
            if match_type == "direct" and not reference_refs:
                fail(f"direct candidate_page_evidence {candidate_id} / {page_id} requires a reference ID")
            if match_type == "principle" and (not reference_refs or not isinstance(item["borrowed_principle"], str) or not item["borrowed_principle"].strip()):
                fail(f"principle candidate_page_evidence {candidate_id} / {page_id} requires a reference and borrowed principle")
            if match_type == "contract_designed" and (not isinstance(item["contract_design_reason"], str) or not item["contract_design_reason"].strip()):
                fail(f"contract-designed candidate_page_evidence {candidate_id} / {page_id} requires a contract design reason")
    return scenario_refs_by_candidate


def candidate_viability(record: dict, candidates: dict, scenario_refs_by_candidate: dict[str, set[str]]) -> None:
    """Reject structurally varied candidates that do not support the approved work."""
    viability = record.get("candidate_viability")
    if not isinstance(viability, dict) or set(viability) != set(candidates):
        fail("wireframe_structure requires one candidate_viability record for every candidate")
    required = {"status", "scenario_assessments"}
    assessment_required = {"scenario_refs", "critical_path", "required_information", "additional_cost", "compensating_benefit", "result"}
    for candidate_id in candidates:
        item = viability[candidate_id]
        if not isinstance(item, dict) or required - set(item) or item["status"] != "viable":
            fail(f"structure candidate {candidate_id} must be explicitly viable before diversity comparison")
        assessments = item["scenario_assessments"]
        if not isinstance(assessments, list) or not assessments:
            fail(f"structure candidate {candidate_id} requires scenario viability assessments")
        assessed_scenarios: set[str] = set()
        for assessment in assessments:
            if not isinstance(assessment, dict) or assessment_required - set(assessment):
                fail(f"structure candidate {candidate_id} has an incomplete viability assessment")
            scenario_refs = assessment["scenario_refs"]
            if not isinstance(scenario_refs, list) or not scenario_refs or any(not isinstance(ref, str) or not ref for ref in scenario_refs):
                fail(f"structure candidate {candidate_id} viability assessment requires scenario references")
            if assessment["result"] != "supports" or not all(isinstance(assessment[field], str) and assessment[field].strip() for field in ("critical_path", "required_information", "additional_cost", "compensating_benefit")):
                fail(f"structure candidate {candidate_id} viability assessment requires a supported path, cost, and benefit")
            assessed_scenarios.update(scenario_refs)
        if assessed_scenarios != scenario_refs_by_candidate[candidate_id]:
            fail(f"structure candidate {candidate_id} viability assessments must cover exactly its candidate-page scenarios")


def g2a_selection_export(
    run_dir: Path,
    decision: dict,
    version: str,
    candidates: dict,
    page_states: dict[str, list[str]],
) -> None:
    relative_path = decision.get("selection_export_path")
    export_path = required_file(run_dir, relative_path, "G2A page/state selection export")
    selection = read_json(export_path, "G2A page/state selection export")
    required = {"run_id", "artifact", "artifact_version", "source_board", "selections"}
    if required - set(selection) or selection["run_id"] != decision["run_id"] or selection["artifact"] != "wireframe_structure" or selection["artifact_version"] != version:
        fail("G2A page/state selection export does not match the approved wireframe structure")
    if not isinstance(selection["source_board"], str) or not selection["source_board"]:
        fail("G2A page/state selection export requires its source_board")
    expected_cells = {(page_id, state) for page_id, states in page_states.items() for state in states}
    entries = selection["selections"]
    if not isinstance(entries, list) or len(entries) != len(expected_cells):
        fail("G2A page/state selection export must select every inventory page/state exactly once")
    seen: set[tuple[str, str]] = set()
    for entry in entries:
        required_entry = {"page_id", "state", "selected_candidate_id", "source_path", "note"}
        if not isinstance(entry, dict) or required_entry - set(entry):
            fail("every G2A page/state selection requires page, state, candidate, source path, and note")
        page_id, state = entry["page_id"], entry["state"]
        candidate_id, source_path = entry["selected_candidate_id"], entry["source_path"]
        cell = (page_id, state)
        if cell not in expected_cells or cell in seen or candidate_id not in candidates:
            fail("G2A page/state selection has an invalid, duplicate, or unknown candidate cell")
        if source_path != candidates[candidate_id][page_id][state]:
            fail("G2A page/state selection source_path must match the selected candidate render path")
        if not isinstance(entry["note"], str):
            fail("G2A page/state selection note must be a string")
        seen.add(cell)


def labeled_value(text: str, heading: str, label: str, name: str) -> str:
    section = text.split(heading, 1)[1].split("\n## ", 1)[0] if heading in text else ""
    line = next((line.strip() for line in section.splitlines() if line.strip().startswith(label)), "")
    value = line[len(label):].strip() if line else ""
    if not value:
        fail(f"{name} requires a non-empty value for: {label}")
    return value


def markdown_section(text: str, heading: str, name: str) -> str:
    if heading not in text:
        fail(f"{name} is missing required section: {heading}")
    return text.split(heading, 1)[1].split("\n## ", 1)[0]


def markdown_table_rows(section: str, header_name: str, width: int, name: str) -> list[tuple[str, ...]]:
    rows: list[tuple[str, ...]] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = tuple(cell.strip() for cell in stripped.strip("|").split("|"))
        if len(cells) != width:
            continue
        if cells[0] == header_name or all(cell and set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append(cells)
    return rows


def component_foundation_rows(text: str, name: str) -> list[tuple[str, ...]]:
    section = markdown_section(text, "## Component foundation", name)
    rows = markdown_table_rows(section, "Element", 4, name)
    if not rows or any(not all(cell for cell in row) for row in rows):
        fail(f"{name} requires one or more complete Component foundation rows")
    return rows


def ui_surface_adaptation_rows(text: str, name: str, expected_surface_ids: set[str]) -> list[tuple[str, ...]]:
    if not expected_surface_ids:
        return []
    section = markdown_section(text, "## UI surface adaptation", name)
    rows = markdown_table_rows(section, "UI surface ID", 4, name)
    if not rows or any(not all(cell for cell in row) for row in rows) or {row[0] for row in rows} != expected_surface_ids:
        fail(f"{name} requires one complete UI surface adaptation row for every product UI surface")
    return rows


def visual_craft_review(text: str, name: str, expected_render_paths: list[str]) -> None:
    section = markdown_section(text, "## Visual Craft Review", name)
    mode = labeled_value(text, "## Visual Craft Review", "- Review mode:", name)
    if mode not in {"`independent_visual_pass`", "`external_design_skill`", "independent_visual_pass", "external_design_skill"}:
        fail(f"{name} requires an independent or external-design-skill Craft Review mode")
    reviewed_paths = labeled_value(text, "## Visual Craft Review", "- Reviewed render paths:", name)
    if any(path not in reviewed_paths for path in expected_render_paths):
        fail(f"{name} Craft Review must name every representative render path")
    repair_count = labeled_value(text, "## Visual Craft Review", "- Direction-level repair count (0 or 1):", name)
    if repair_count not in {"0", "1"}:
        fail(f"{name} Craft Review allows at most one direction-level repair")
    if labeled_value(text, "## Visual Craft Review", "- Outcome:", name) not in {"`ready`", "ready"}:
        fail(f"{name} Craft Review outcome must be ready for a displayed direction")
    if labeled_value(text, "## Visual Craft Review", "- G2A structure changed:", name) not in {"`no`", "no"}:
        fail(f"{name} Craft Review must not change the G2A structure")
    rows = markdown_table_rows(section, "Check", 3, name)
    expected_checks = {"Alignment", "Repeated components", "Surface and edges", "Typography and density", "State clarity"}
    checks = {row[0] for row in rows}
    if checks != expected_checks:
        fail(f"{name} Craft Review requires exactly the five required checks")
    for check, result, note in rows:
        if result not in {"pass", "repaired"} or not note:
            fail(f"{name} Craft Review requires a pass/repaired result and observed note for {check}")
    if repair_count == "0" and any(result == "repaired" for _, result, _ in rows):
        fail(f"{name} Craft Review repair count conflicts with repaired checks")
    if repair_count == "1" and not any(result == "repaired" for _, result, _ in rows):
        fail(f"{name} Craft Review repair count requires a repaired check")


def design_direction_document(run_dir: Path, relative_path: str, name: str, expected_render_paths: list[str], ui_surface_ids: set[str]) -> tuple[str, str]:
    document = required_file(run_dir, relative_path, name)
    text = document.read_text()
    for heading in ("## G2A structural baseline", "## Design hypothesis and Playbook inputs", "## Visual distinction", "## Representative screens: before and after", "## Refinement impact", "## Design choices and trade-offs", "## Structure preservation check"):
        if heading not in text:
            fail(f"{name} is missing required section: {heading}")
    required_labeled_values(
        text,
        "## G2A structural baseline",
        ("- Selected structure version:", "- Selected structure-render baseline path / SHA-256:", "- Structure preserved from this baseline:", "- Non-binding G2A visual treatment replaced here:"),
        name,
    )
    hypothesis = labeled_value(text, "## Design hypothesis and Playbook inputs", "- Visual hypothesis:", name)
    labeled_value(text, "## Design hypothesis and Playbook inputs", "- Design Playbook version:", name)
    labeled_value(text, "## Design hypothesis and Playbook inputs", "- Applied Playbook principle IDs:", name)
    labeled_value(text, "## Design hypothesis and Playbook inputs", "- Intended work experience:", name)
    contrast = labeled_value(text, "## Design hypothesis and Playbook inputs", "- Contrast from the other directions:", name)
    axes = labeled_value(text, "## Visual distinction", "- Distinct visual axes (at least 3; comma-separated: typography_density, color_state, surface_hierarchy, item_control_form, emphasis_reading_order):", name)
    allowed_axes = {"typography_density", "color_state", "surface_hierarchy", "item_control_form", "emphasis_reading_order"}
    selected_axes = {axis.strip() for axis in axes.split(",") if axis.strip()}
    if len(selected_axes) < 3 or not selected_axes <= allowed_axes:
        fail(f"{name} requires at least three valid distinct visual axes")
    component_foundation_rows(text, name)
    ui_surface_adaptation_rows(text, name, ui_surface_ids)
    visual_craft_review(text, name, expected_render_paths)
    return hypothesis, contrast


def selected_visual_rules_document(run_dir: Path, relative_path: object, selected_direction_id: str, source_direction_brief: str, ui_surface_ids: set[str]) -> tuple[Path, str]:
    path = required_file(run_dir, relative_path, "selected global visual rules")
    text = path.read_text()
    for heading in ("## Source direction", "## Global visual rules", "## Structure protection"):
        if heading not in text:
            fail(f"selected global visual rules is missing required section: {heading}")
    if labeled_value(text, "## Source direction", "- Selected direction ID:", "selected global visual rules") != selected_direction_id:
        fail("selected global visual rules must identify the G2B-approved direction")
    if labeled_value(text, "## Source direction", "- Source direction brief:", "selected global visual rules") != source_direction_brief:
        fail("selected global visual rules must identify the selected direction brief")
    required_labeled_values(text, "## Source direction", ("- Design Playbook version:", "- Applied Playbook principle IDs:"), "selected global visual rules")
    for axis in ("Typography and density", "Color and state language", "Surface and hierarchy", "Item silhouette and control form", "Emphasis and reading order"):
        row = next((line.strip() for line in text.splitlines() if line.strip().startswith(f"| {axis} |")), "")
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) != 3 or not all(cells):
            fail(f"selected global visual rules is missing global rule axis: {axis}")
    component_foundation_rows(text, "selected global visual rules")
    ui_surface_adaptation_rows(text, "selected global visual rules", ui_surface_ids)
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def visual_signatures(record: dict, directions: dict) -> None:
    signatures = record.get("visual_signatures")
    if not isinstance(signatures, dict) or set(signatures) != set(directions):
        fail("visual_design requires one visual_signature for every design direction")
    for direction_id, signature in signatures.items():
        if not isinstance(signature, dict) or set(signature) != set(VISUAL_SIGNATURE_FIELDS):
            fail(f"design direction {direction_id} must define every visual signature axis")
        if not all(isinstance(value, str) and value.strip() for value in signature.values()):
            fail(f"design direction {direction_id} visual signature values must be non-empty")
    direction_ids = list(directions)
    for index, first_id in enumerate(direction_ids):
        for second_id in direction_ids[index + 1:]:
            changed_axes = sum(
                signatures[first_id][axis] != signatures[second_id][axis]
                for axis in VISUAL_SIGNATURE_FIELDS
            )
            if changed_axes < 3:
                fail(f"design directions {first_id} and {second_id} must differ on at least three visual signature axes")


def renderable_page_map(run_dir: Path, pages: object, page_states: dict[str, list[str]], label: str) -> None:
    if not isinstance(pages, dict) or set(pages) != set(page_states):
        fail(f"{label} must provide exactly every page inventory ID")
    for page_id, states in page_states.items():
        paths = pages.get(page_id)
        if not isinstance(paths, dict) or set(paths) != set(states):
            fail(f"{label} must provide exactly every comparison state for {page_id}")
        for state, relative_path in paths.items():
            image_path(run_dir, relative_path, f"{label} page {page_id} state {state}")


def selected_visual_baseline(run_dir: Path, relative_path: str, selected_pages: object) -> tuple[Path, str]:
    baseline_path = required_file(run_dir, relative_path, "selected visual baseline")
    baseline = read_json(baseline_path, "selected visual baseline")
    if baseline.get("baseline_role") != STRUCTURE_RENDER_BASELINE_ROLE or baseline.get("semantic_alias") != STRUCTURE_RENDER_BASELINE_ALIAS:
        fail("selected visual baseline must declare itself as the structure-only render baseline")
    pages = baseline.get("pages")
    if not isinstance(pages, dict) or not isinstance(selected_pages, dict) or set(pages) != set(selected_pages):
        fail("selected visual baseline must cover exactly the approved selected pages")
    for page_id, states in selected_pages.items():
        baseline_states = pages.get(page_id)
        if not isinstance(baseline_states, dict) or set(baseline_states) != set(states):
            fail(f"selected visual baseline must cover exactly the approved states for {page_id}")
        for state, relative_path in states.items():
            item = baseline_states.get(state)
            if not isinstance(item, dict) or item.get("path") != relative_path or not isinstance(item.get("sha256"), str):
                fail(f"selected visual baseline requires exact path and hash for {page_id} / {state}")
            page_path = required_file(run_dir, relative_path, f"selected visual baseline page {page_id} state {state}")
            if hashlib.sha256(page_path.read_bytes()).hexdigest() != item["sha256"]:
                fail(f"selected visual baseline hash does not match: {page_id} / {state}")
    return baseline_path, hashlib.sha256(baseline_path.read_bytes()).hexdigest()


def selected_structure_contract(
    run_dir: Path,
    relative_path: str,
    run_id: str,
    structure_version: str,
    selected_pages: object,
) -> tuple[Path, str, list[dict], set[tuple[str, str, str]]]:
    """Validate the compact, selected G2A structure that G3 must compile verbatim."""
    path = required_file(run_dir, relative_path, "selected structure contract")
    contract = read_json(path, "selected structure contract")
    if (
        contract.get("run_id") != run_id
        or contract.get("artifact") != "selected_structure_contract"
        or contract.get("structure_version") != structure_version
    ):
        fail("selected structure contract must match this run and wireframe structure version")
    if not isinstance(selected_pages, dict):
        fail("selected structure contract requires approved selected pages")
    entries = contract.get("entries")
    if not isinstance(entries, list) or not entries:
        fail("selected structure contract requires one or more key decision-region entries")
    required = {
        "page_id",
        "state",
        "region_id",
        "selected_structure",
        "content_composition",
        "interaction_or_state_rule",
        "excluded_alternative",
    }
    keys: set[tuple[str, str, str]] = set()
    covered_page_states: set[tuple[str, str]] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != required:
            fail("selected structure contract entries require exactly the key Region decision fields")
        values = tuple(entry[field] for field in required)
        if not all(isinstance(value, str) and value.strip() for value in values):
            fail("selected structure contract entries require non-empty decision values")
        page_id, state, region_id = entry["page_id"], entry["state"], entry["region_id"]
        key = (page_id, state, region_id)
        if page_id not in selected_pages or state not in selected_pages[page_id] or key in keys:
            fail("selected structure contract entries require unique approved Page / State / Region keys")
        keys.add(key)
        covered_page_states.add((page_id, state))
    expected_page_states = {(page_id, state) for page_id, states in selected_pages.items() for state in states}
    if covered_page_states != expected_page_states:
        fail("selected structure contract must include one or more key Regions for every selected Page / State")
    return path, hashlib.sha256(path.read_bytes()).hexdigest(), entries, keys


def artifact(state: dict, run_dir: Path, name: str, allowed_statuses: set[str]) -> dict:
    record = state["artifacts"].get(name)
    if not isinstance(record, dict):
        fail(f"{name} must be an object with version, status, and manifest")
    version = record.get("version")
    status = record.get("status")
    manifest_name = record.get("manifest")
    if not isinstance(version, str) or not version:
        fail(f"{name} requires a non-empty version")
    if status not in ARTIFACT_STATUSES or status not in allowed_statuses:
        fail(f"{name} must have one of: {', '.join(sorted(allowed_statuses))}")
    if not isinstance(manifest_name, str) or not manifest_name:
        fail(f"{name} requires a manifest path")
    manifest_path = run_path(run_dir, manifest_name, f"{name} manifest")
    manifest = read_json(manifest_path, f"{name} manifest")
    if manifest.get("run_id") != state["run_id"] or manifest.get("artifact") != name:
        fail(f"{name} manifest run_id/artifact does not match run-state")
    if manifest.get("version") != version or manifest.get("status") != status:
        fail(f"{name} manifest version/status does not match run-state")
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources or any(not isinstance(item, dict) or not item.get("path") or not item.get("reason") for item in sources):
        fail(f"{name} manifest requires at least one source with path and reason")
    if name in {"use_case", "wireframe_structure", "visual_design", "prototype", "prebuild_contract"}:
        brief_path = record.get("brief")
        brief_text = required_file(run_dir, brief_path, f"{name} gate brief").read_text()
        if "## 이번에 결정할 것" not in brief_text or "## Human decision" not in brief_text:
            fail(f"{name} gate brief must contain decision and human decision sections")
    if name == "context_packet":
        intent_sources = [item for item in sources if item.get("context_role") == "intent"]
        if not intent_sources:
            fail("context_packet manifest requires at least one intent source")
        if any(item.get("content_mode") != "full_document" for item in intent_sources):
            fail("every context_packet intent source must use content_mode=full_document")
        packet_path = run_path(run_dir, record.get("path"), "context_packet")
        if not packet_path.is_file():
            fail("context_packet path must point to an existing file")
        packet_text = packet_path.read_text()
        if "## Full Intent Context" not in packet_text:
            fail("context_packet must contain a Full Intent Context section")
        for source in intent_sources:
            snapshot_path = run_path(run_dir, source.get("snapshot_path"), "intent source snapshot")
            expected_hash = source.get("content_sha256")
            if not snapshot_path.is_file() or not isinstance(expected_hash, str):
                fail("intent source requires an existing snapshot_path and content_sha256")
            snapshot_text = snapshot_path.read_text()
            actual_hash = hashlib.sha256(snapshot_text.encode()).hexdigest()
            if actual_hash != expected_hash:
                fail(f"intent source snapshot hash does not match: {source.get('path')}")
            if source.get("path") not in packet_text or snapshot_text not in packet_text:
                fail(f"context_packet does not embed the full intent source: {source.get('path')}")
    if name == "evidence_pack":
        attempts = record.get("critic_attempts")
        reviews = record.get("critic_reviews")
        evidence_ids = record.get("evidence_ids")
        if not isinstance(attempts, int) or not 1 <= attempts <= 3:
            fail("evidence_pack requires critic_attempts from 1 to 3")
        if not isinstance(reviews, list) or len(reviews) != attempts:
            fail("evidence_pack critic_reviews must match critic_attempts")
        if not isinstance(evidence_ids, list) or not evidence_ids or any(not isinstance(item, str) or not item for item in evidence_ids):
            fail("evidence_pack requires stable evidence_ids")
        if len(set(evidence_ids)) != len(evidence_ids):
            fail("evidence_pack evidence_ids must be unique")
        verdicts = []
        for review_name in reviews:
            review = read_json(run_path(run_dir, review_name, "G0 critic review"), "G0 critic review")
            if review.get("gate") != "G0" or review.get("verdict") not in {"pass", "revise", "ask-user", "insufficient-evidence"}:
                fail("G0 critic review has invalid gate or verdict")
            critic_references(review, "G0", run_dir, state)
            verdicts.append(review["verdict"])
        if verdicts[-1] != "pass" or "pass" in verdicts[:-1]:
            fail("a critic-passed evidence_pack requires one final pass and no earlier pass")
    if name == "use_case":
        packet_path = run_path(run_dir, record.get("path"), "use_case packet")
        diagram_path = run_path(run_dir, record.get("diagram"), "use_case diagram")
        coverage_path = run_path(run_dir, record.get("coverage"), "use_case coverage")
        if not packet_path.is_file() or not diagram_path.is_file():
            fail("use_case requires existing packet and SVG diagram files")
        packet_text = packet_path.read_text()
        for heading in ("## 한눈에 보기", "### 쉬운 설명", "## 사용자 이야기", "## Use Case 그림", "## Product constraints", "## Unresolved assumptions", "## Scenario coverage", "## Product UI surfaces", "## Logical system connections"):
            if heading not in packet_text:
                fail(f"use_case packet is missing required section: {heading}")
        required_labeled_values(
            packet_text,
            "## Product constraints",
            (
                "- Problem / success outcome:",
                "- Known decisions to preserve:",
                "- Authority boundary (who may do what):",
                "- Data meaning and sensitivity:",
                "- External-action boundary:",
                "- Failure cost and required safe outcome:",
            ),
            "use_case product constraints",
        )
        required_labeled_values(
            packet_text,
            "## Unresolved assumptions",
            ("- Blocking product unknowns:",),
            "use_case unresolved assumptions",
        )
        if diagram_path.suffix.lower() != ".svg" or "<svg" not in diagram_path.read_text():
            fail("use_case diagram must be an SVG")
        coverage = read_json(coverage_path, "use_case coverage")
        if coverage.get("run_id") != state["run_id"] or coverage.get("artifact") != "use_case" or coverage.get("artifact_version") != version:
            fail("use_case coverage does not match this run and artifact version")
        if not isinstance(coverage.get("feature_id"), str) or not coverage["feature_id"]:
            fail("use_case coverage requires a stable feature_id")
        scenarios = coverage.get("scenarios")
        if not isinstance(scenarios, list) or not scenarios:
            fail("use_case coverage requires at least one scenario")
        scenario_ids = set()
        scenario_types = {}
        diagram_text = diagram_path.read_text()
        required_scenario_fields = {"id", "feature", "type", "trigger", "expected_outcome", "use_case_section", "diagram_ref", "evidence_refs"}
        evidence_record = state["artifacts"].get("evidence_pack")
        valid_evidence_ids = set(evidence_record.get("evidence_ids", [])) if isinstance(evidence_record, dict) else set()
        for scenario in scenarios:
            if not isinstance(scenario, dict) or required_scenario_fields - set(scenario):
                fail("each use_case scenario requires id, feature, type, trigger, expected_outcome, use_case_section, diagram_ref, and evidence_refs")
            string_fields = required_scenario_fields - {"evidence_refs"}
            if scenario["type"] not in SCENARIO_TYPES or not all(isinstance(scenario[field], str) and scenario[field] for field in string_fields):
                fail("use_case scenario has an invalid type or empty required field")
            if not isinstance(scenario["evidence_refs"], list) or not scenario["evidence_refs"] or any(ref not in valid_evidence_ids for ref in scenario["evidence_refs"]):
                fail("use_case scenario requires valid evidence_refs from the Evidence Pack")
            if scenario["id"] in scenario_ids:
                fail("use_case scenario IDs must be unique")
            if scenario["diagram_ref"] not in diagram_text:
                fail(f"use_case diagram does not contain scenario reference: {scenario['diagram_ref']}")
            scenario_ids.add(scenario["id"])
            scenario_types[scenario["id"]] = scenario["type"]
        ui_surface_contract(coverage, scenarios)
        coverage_items = coverage.get("coverage")
        if not isinstance(coverage_items, dict) or set(coverage_items) != SCENARIO_TYPES:
            fail("use_case coverage must declare every required scenario type")
        for category, item in coverage_items.items():
            if not isinstance(item, dict) or item.get("status") not in {"covered", "not_applicable"}:
                fail(f"use_case coverage has invalid status for {category}")
            covered_ids = item.get("scenario_ids")
            reason = item.get("reason")
            if not isinstance(covered_ids, list) or not isinstance(reason, str):
                fail(f"use_case coverage requires scenario_ids and reason for {category}")
            if item["status"] == "covered":
                if not covered_ids or any(identifier not in scenario_ids for identifier in covered_ids):
                    fail(f"covered {category} requires existing scenario IDs")
                if any(scenario_types[identifier] != category for identifier in covered_ids):
                    fail(f"covered {category} must reference scenarios of the same type")
            elif not reason.strip():
                fail(f"not_applicable {category} requires a reason")
        readiness = coverage.get("handoff_readiness")
        if (
            not isinstance(readiness, dict)
            or set(readiness) != {"blocking_product_unknowns"}
            or not isinstance(readiness["blocking_product_unknowns"], list)
            or readiness["blocking_product_unknowns"]
        ):
            fail("use_case handoff_readiness requires an empty blocking_product_unknowns list before G1 approval")
        criterion_conditions = acceptance_criteria(run_dir, record.get("acceptance_criteria"), version, scenario_ids)
        logical_system_contract(state, run_dir, record, scenario_ids, set(criterion_conditions))
        if state["risk_level"] == "high":
            risk_controls(run_dir, record.get("risk_controls"), version, set(criterion_conditions))
        reviews = record.get("critic_reviews")
        if not isinstance(reviews, list) or not 1 <= len(reviews) <= 2:
            fail("use_case requires one critic review, or revise followed by one confirmation review")
        verdicts = []
        for review_name in reviews:
            review = read_json(run_path(run_dir, review_name, "G1 critic review"), "G1 critic review")
            if review.get("gate") != "G1" or review.get("verdict") not in {"pass", "revise", "ask-user", "insufficient-evidence"}:
                fail("G1 critic review has invalid gate or verdict")
            critic_references(review, "G1", run_dir, state)
            verdicts.append(review["verdict"])
        if verdicts[-1] != "pass" or (len(verdicts) == 2 and verdicts[0] != "revise"):
            fail("use_case must end with a pass; a second review is only the confirmation after revise")
    if name == "wireframe_structure":
        use_case = artifact(state, run_dir, "use_case", {"approved"})
        use_case_coverage = read_json(run_path(run_dir, use_case.get("coverage"), "use_case coverage"), "use_case coverage")
        approved_scenario_ids = {
            item.get("id")
            for item in use_case_coverage.get("scenarios", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"]
        }
        if not approved_scenario_ids:
            fail("wireframe_structure requires approved G1 scenarios")
        ui_surfaces = ui_surface_contract(use_case_coverage, use_case_coverage.get("scenarios", []))
        logical_contract = approved_logical_system_contract(state, run_dir)
        logical_flows = None if logical_contract["applicability"] == "not_applicable" else {
            flow["id"]: set(flow["scenario_refs"]) for flow in logical_contract["flows"]
        }
        page_states = page_inventory_details(
            run_dir, record.get("page_inventory"), version, approved_scenario_ids, logical_flows, ui_surfaces
        )
        page_surfaces = page_ui_surface_ids(run_dir, record.get("page_inventory"), version)
        reference_strategy(record, page_states)
        candidates = record.get("candidate_pages")
        briefs = record.get("candidate_briefs")
        reference_patterns = record.get("reference_patterns")
        if not isinstance(candidates, dict) or len(candidates) not in {1, 2, 3}:
            fail("wireframe_structure requires one to three viable candidate page maps")
        if len(candidates) < 3:
            exception_reason = record.get("candidate_count_exception_reason")
            if not isinstance(exception_reason, str) or not exception_reason.strip():
                fail("fewer than three viable structure candidates require candidate_count_exception_reason")
            brief_text = required_file(run_dir, record.get("brief"), "wireframe structure gate brief").read_text()
            if exception_reason not in brief_text:
                fail("G2A gate brief must include the candidate_count_exception_reason")
        required_reference_fields = {"id", "product", "screen_or_pattern", "url", "observed_at", "task_fit", "borrow", "do_not_borrow", "evidence_modality", "verified_observables"}
        if not isinstance(reference_patterns, list) or not reference_patterns:
            fail("wireframe_structure requires one or more actually observed shipped-product reference patterns")
        reference_ids = set()
        for pattern in reference_patterns:
            string_fields = required_reference_fields - {"verified_observables"}
            if not isinstance(pattern, dict) or required_reference_fields - set(pattern) or not all(isinstance(pattern[field], str) and pattern[field] for field in string_fields):
                fail("each reference pattern requires identity, task fit, modality, and verified observables")
            if not pattern["url"].startswith(("https://", "http://")) or pattern["id"] in reference_ids:
                fail("reference pattern ids must be unique and URLs must be absolute HTTP(S) URLs")
            observables = pattern["verified_observables"]
            if pattern["evidence_modality"] not in EVIDENCE_MODALITIES or not isinstance(observables, list) or not observables or len(set(observables)) != len(observables) or any(observable not in REFERENCE_OBSERVABLES for observable in observables):
                fail("reference pattern modality and verified observables are invalid")
            if pattern["evidence_modality"] == "screenshot" and not set(observables) <= {"visible_structure", "visible_state"}:
                fail("a screenshot reference may only support visible structure or state claims")
            reference_ids.add(pattern["id"])
        reference_board = required_file(run_dir, record.get("reference_board"), "wireframe reference board")
        if reference_board.suffix.lower() != ".html":
            fail("wireframe reference board must be an HTML file")
        reference_board_text = reference_board.read_text()
        for pattern in reference_patterns:
            if f'data-reference="{pattern["id"]}|{pattern["url"]}"' not in reference_board_text:
                fail(f"reference board is missing reference marker: {pattern['id']}")
        if not isinstance(briefs, dict) or set(briefs) != set(candidates):
            fail("wireframe_structure requires one candidate brief for every structure candidate")
        candidate_work_models(record, candidates)
        candidate_reference_ids = record.get("candidate_reference_ids")
        if not isinstance(candidate_reference_ids, dict) or set(candidate_reference_ids) != set(candidates):
            fail("wireframe_structure requires one or more reference pattern IDs for every structure candidate")
        for candidate_id, pages in candidates.items():
            if not isinstance(candidate_id, str) or not candidate_id:
                fail("every structure candidate requires a non-empty ID")
            renderable_page_map(run_dir, pages, page_states, f"structure candidate {candidate_id}")
            candidate_brief_document(run_dir, briefs[candidate_id], f"structure candidate {candidate_id} brief")
            candidate_refs = candidate_reference_ids[candidate_id]
            if not isinstance(candidate_refs, list) or not candidate_refs or any(reference_id not in reference_ids for reference_id in candidate_refs):
                fail(f"structure candidate {candidate_id} requires valid reference pattern IDs")
        scenario_refs_by_candidate = candidate_page_evidence(
            run_dir, record, candidates, page_states, approved_scenario_ids, reference_ids, briefs
        )
        if any(refs != approved_scenario_ids for refs in scenario_refs_by_candidate.values()):
            fail("each structure candidate must provide page evidence for every approved G1 scenario")
        candidate_viability(record, candidates, scenario_refs_by_candidate)
        decision_screens = record.get("decision_screens")
        valid_decision_screens = {f"{page_id}:{state}" for page_id, states in page_states.items() for state in states}
        max_decision_screens = max(3, len(ui_surfaces)) if ui_surfaces else 3
        if not isinstance(decision_screens, list) or not 1 <= len(decision_screens) <= max_decision_screens or len(set(decision_screens)) != len(decision_screens) or any(item not in valid_decision_screens for item in decision_screens):
            fail("wireframe_structure requires valid unique decision_screens")
        if ui_surfaces and not set(ui_surfaces) <= set().union(*(page_surfaces[item.split(":", 1)[0]] for item in decision_screens)):
            fail("multi-UI decision_screens must include at least one screen from every product UI surface")
        board_path = record.get("board")
        board = required_file(run_dir, board_path, "wireframe structure comparison board")
        if board.suffix.lower() != ".html":
            fail("wireframe structure comparison board must be an HTML file")
        board_text = board.read_text()
        for candidate_id, pages in candidates.items():
            for page_id, states in pages.items():
                for page_state, relative_path in states.items():
                    marker = f'data-cell="{candidate_id}:{page_id}:{page_state}|{relative_path}"'
                    if marker not in board_text:
                        fail(f"comparison board is missing candidate/page/state cell: {candidate_id} / {page_id} / {page_state}")
                    preview_marker = f'data-preview-cell="{candidate_id}:{page_id}:{page_state}|{relative_path}"'
                    selection_marker = f'data-selection-cell="{candidate_id}:{page_id}:{page_state}|{relative_path}"'
                    if preview_marker not in board_text or selection_marker not in board_text:
                        fail(f"comparison board is missing preview or click-selection control: {candidate_id} / {page_id} / {page_state}")
        if "g2a-page-state-selection.json" not in board_text or "navigator.clipboard" not in board_text or "Blob" not in board_text:
            fail("comparison board must provide browser-only copy and download of the G2A page/state selection JSON")
    if name == "visual_design":
        structure = state["artifacts"].get("wireframe_structure")
        if not isinstance(structure, dict):
            fail("visual_design requires a wireframe_structure artifact")
        structure_version = record.get("structure_version")
        if structure_version != structure.get("version"):
            fail("visual_design must name the approved wireframe_structure version")
        baseline_path, _ = selected_visual_baseline(
            run_dir, structure.get("selected_visual_baseline"), structure.get("selected_pages")
        )
        if record.get("selected_visual_baseline") != str(baseline_path.relative_to(run_dir)):
            fail("visual_design must reference the exact approved selected visual baseline")
        page_ids = page_inventory(run_dir, structure.get("page_inventory"), structure_version)
        page_states = page_inventory_details(run_dir, structure.get("page_inventory"), structure_version)
        ui_surfaces = approved_ui_surfaces(state, run_dir)
        page_surfaces = page_ui_surface_ids(run_dir, structure.get("page_inventory"), structure_version)
        representatives = record.get("representative_page_ids")
        expected_count = min(len(page_ids), max(3, len(ui_surfaces))) if ui_surfaces else min(3, len(page_ids))
        if not isinstance(representatives, list) or len(representatives) != expected_count or len(set(representatives)) != expected_count or any(page_id not in page_ids for page_id in representatives):
            fail("visual_design requires the required number of unique representative page IDs")
        if ui_surfaces and not set(ui_surfaces) <= set().union(*(page_surfaces[page_id] for page_id in representatives)):
            fail("visual_design representatives must include every product UI surface")
        representative_states = record.get("representative_page_states")
        if not isinstance(representative_states, dict) or set(representative_states) != set(representatives) or any(
            not isinstance(representative_states[page_id], str) or representative_states[page_id] not in page_states[page_id]
            for page_id in representatives
        ):
            fail("visual_design requires one approved G2A state for every representative page")
        if record.get("design_playbook") != "references/07-design-playbook.md":
            fail("visual_design must identify the injected G2B Design Playbook")
        directions = record.get("directions")
        if not isinstance(directions, dict) or len(directions) not in {1, 2, 3, 4, 5, 6}:
            fail("visual_design requires four to six design refinements, or a documented one-to-three-direction exception")
        if len(directions) < 4:
            exception_reason = record.get("direction_count_exception_reason")
            if not isinstance(exception_reason, str) or not exception_reason.strip():
                fail("fewer than four design refinements require direction_count_exception_reason")
            brief_text = required_file(run_dir, record.get("brief"), "visual design gate brief").read_text()
            if exception_reason not in brief_text:
                fail("G2B gate brief must include the direction_count_exception_reason")
        visual_signatures(record, directions)
        direction_briefs = record.get("direction_briefs")
        if not isinstance(direction_briefs, dict) or set(direction_briefs) != set(directions):
            fail("visual_design requires one direction brief for every design refinement")
        board = required_file(run_dir, record.get("board"), "visual design comparison board")
        if board.suffix.lower() != ".html":
            fail("visual design comparison board must be an HTML file")
        board_text = board.read_text()
        hypotheses: set[str] = set()
        contrasts: set[str] = set()
        for direction_id, pages in directions.items():
            if not isinstance(direction_id, str) or not direction_id or not isinstance(pages, dict) or set(pages) != set(representatives):
                fail("every design direction must provide every representative page")
            for page_id, relative_path in pages.items():
                image_path(run_dir, relative_path, f"design direction {direction_id} page {page_id}")
                marker = f'data-design-cell="{direction_id}:{page_id}:{representative_states[page_id]}|{relative_path}"'
                if marker not in board_text:
                    fail(f"visual design comparison board is missing design direction cell: {direction_id} / {page_id}")
            hypothesis, contrast = design_direction_document(
                run_dir,
                direction_briefs[direction_id],
                f"design direction {direction_id} brief",
                list(pages.values()),
                set(ui_surfaces),
            )
            if hypothesis in hypotheses or contrast in contrasts:
                fail("every design direction requires a distinct visual hypothesis and contrast statement")
            hypotheses.add(hypothesis)
            contrasts.add(contrast)
            craft_marker = f'data-design-craft="{direction_id}|ready"'
            if craft_marker not in board_text:
                fail(f"visual design comparison board is missing visible Craft Review status: {direction_id}")
    if name == "prototype":
        use_case = state["artifacts"].get("use_case")
        if not isinstance(use_case, dict):
            fail("prototype requires a use_case artifact")
        prototype_path = run_path(run_dir, record.get("path"), "prototype slice")
        prototype_text = prototype_path.read_text()
        for heading in ("## Selected G2A structure and G2B visual design decisions", "## Compiled approved page structure", "## Compiled selected visual rules", "## Component foundation", "## UI surface adaptation", "## State coverage", "## UI surface coverage", "## Derived states outside the approved screen inventory", "## Acceptance Criterion and verification coverage", "## Completeness check"):
            if heading not in prototype_text:
                fail(f"prototype slice is missing required section: {heading}")
        required_labeled_values(
            prototype_text,
            "## Selected G2A structure and G2B visual design decisions",
            (
                "- All approved pages and state inventory:",
                "- Approved G2A structure-render baseline lineage (path and hash):",
                "- Approved G2A blueprint lineage (path and hash):",
                "- Approved G2A selected structure contract lineage (path and hash):",
                "- Approved G2B selected visual rules lineage (path and hash):",
                "- Page/state → scenario / AC mapping:",
                "- Selected structure-contract region → prototype mapping:",
                "- Navigation and interaction rules:",
                "- Visual design rules (type, color/state, density, controls):",
                "- Renderable prototype paths and hash:",
            ),
            "prototype structure and design decisions",
        )
        coverage = read_json(run_path(run_dir, use_case.get("coverage"), "use_case coverage"), "use_case coverage")
        scenarios = coverage.get("scenarios")
        scenario_ids = {item.get("id") for item in scenarios if isinstance(item, dict) and isinstance(item.get("id"), str)} if isinstance(scenarios, list) else set()
        conditions_by_criterion = acceptance_criteria(run_dir, use_case.get("acceptance_criteria"), use_case.get("version"), scenario_ids)
        verification = read_json(run_path(run_dir, record.get("verification"), "prototype coverage"), "prototype coverage")
        if verification.get("artifact") != "prototype" or verification.get("artifact_version") != version or verification.get("use_case_version") != use_case.get("version"):
            fail("prototype coverage must match the prototype and use_case versions")
        structure = state["artifacts"].get("wireframe_structure")
        if not isinstance(structure, dict) or not isinstance(structure.get("selected_blueprint"), str):
            fail("prototype requires an approved selected G2A blueprint")
        selected_blueprint = structure["selected_blueprint"]
        selected_blueprint_path = required_file(run_dir, selected_blueprint, "approved selected G2A blueprint")
        selected_blueprint_hash = hashlib.sha256(selected_blueprint_path.read_bytes()).hexdigest()
        selected_pages = structure.get("selected_pages")
        selected_contract_path, selected_contract_hash, selected_contract_entries, selected_contract_keys = selected_structure_contract(
            run_dir,
            structure.get("selected_structure_contract"),
            state["run_id"],
            structure.get("version"),
            selected_pages,
        )
        visual_baseline_path, visual_baseline_hash = selected_visual_baseline(
            run_dir, structure.get("selected_visual_baseline"), selected_pages
        )
        structure_source = verification.get("structure_source")
        if not isinstance(structure_source, dict) or structure_source.get("path") != selected_blueprint or structure_source.get("sha256") != selected_blueprint_hash:
            fail("prototype structure_source must match the approved selected G2A blueprint path and hash")
        contract_source = verification.get("structure_contract_source")
        selected_contract_relative_path = str(selected_contract_path.relative_to(run_dir))
        if not isinstance(contract_source, dict) or contract_source.get("path") != selected_contract_relative_path or contract_source.get("sha256") != selected_contract_hash:
            fail("prototype structure_contract_source must match the approved selected G2A structure contract path and hash")
        if verification.get("compiled_structure_contract") != selected_contract_entries:
            fail("prototype must copy the approved selected structure contract verbatim")
        structure_render_source = verification.get("structure_render_source")
        baseline_relative_path = str(visual_baseline_path.relative_to(run_dir))
        if not isinstance(structure_render_source, dict) or structure_render_source.get("path") != baseline_relative_path or structure_render_source.get("sha256") != visual_baseline_hash:
            fail("prototype structure_render_source must match the approved selected G2A structure-render baseline path and hash")
        selected_visual_rules_path, selected_visual_rules_hash = approved_visual_design(state, run_dir)
        selected_visual_rules_relative_path = str(selected_visual_rules_path.relative_to(run_dir))
        design_source = verification.get("design_source")
        if not isinstance(design_source, dict) or design_source.get("path") != selected_visual_rules_relative_path or design_source.get("sha256") != selected_visual_rules_hash:
            fail("prototype design_source must match the approved selected G2B visual rules path and hash")
        if component_foundation_rows(prototype_text, "prototype slice") != component_foundation_rows(
            selected_visual_rules_path.read_text(), "selected global visual rules"
        ):
            fail("prototype must copy the approved selected Component foundation exactly")
        ui_surfaces = ui_surface_contract(coverage, scenarios) if isinstance(scenarios, list) else {}
        if ui_surfaces:
            if ui_surface_adaptation_rows(prototype_text, "prototype slice", set(ui_surfaces)) != ui_surface_adaptation_rows(
                selected_visual_rules_path.read_text(), "selected global visual rules", set(ui_surfaces)
            ):
                fail("prototype must copy the approved UI surface adaptations exactly")
            page_surfaces = page_ui_surface_ids(run_dir, structure.get("page_inventory"), structure.get("version"))
            criteria_source = read_json(
                run_path(run_dir, use_case.get("acceptance_criteria"), "approved acceptance criteria"),
                "approved acceptance criteria",
            )
            criterion_scenarios = {
                item.get("id"): set(item.get("scenario_refs", []))
                for item in criteria_source.get("criteria", [])
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            }
            surface_coverage = verification.get("ui_surface_coverage")
            if not isinstance(surface_coverage, list) or len(surface_coverage) != len(ui_surfaces):
                fail("multi-UI prototype coverage requires one record for every product UI surface")
            seen_surface_ids: set[str] = set()
            valid_page_states = {f"{page_id}:{state_name}" for page_id, states in selected_pages.items() for state_name in states}
            for item in surface_coverage:
                fields = {"ui_surface_id", "critical_scenario_id", "page_state_refs", "acceptance_ids"}
                if not isinstance(item, dict) or set(item) != fields:
                    fail("multi-UI prototype coverage records are incomplete")
                surface_id = item["ui_surface_id"]
                scenario_id = item["critical_scenario_id"]
                refs = item["page_state_refs"]
                acceptance_ids = item["acceptance_ids"]
                if not isinstance(surface_id, str) or surface_id not in ui_surfaces or surface_id in seen_surface_ids or not isinstance(scenario_id, str) or scenario_id not in ui_surfaces[surface_id]["required_scenario_ids"] or not isinstance(refs, list) or not refs or len(set(refs)) != len(refs) or any(not isinstance(ref, str) or ref not in valid_page_states or surface_id not in page_surfaces[ref.split(":", 1)[0]] for ref in refs) or not isinstance(acceptance_ids, list) or not acceptance_ids or len(set(acceptance_ids)) != len(acceptance_ids) or any(acceptance_id not in conditions_by_criterion or scenario_id not in criterion_scenarios.get(acceptance_id, set()) for acceptance_id in acceptance_ids):
                    fail("multi-UI prototype coverage must connect each surface to its scenario, page/state, and AC")
                seen_surface_ids.add(surface_id)
        derived_states = verification.get("derived_states")
        if not isinstance(derived_states, list):
            fail("prototype coverage requires a derived_states list")
        seen_derived_states = set()
        for derived in derived_states:
            required = {"page_id", "state", "source_page_id", "source_state", "scenario_refs", "acceptance_refs", "preserved_structure", "added_state_expression", "prototype_path", "evidence_paths"}
            if not isinstance(derived, dict) or required - set(derived):
                fail("each derived state requires source, contract basis, preservation, and evidence")
            page_id, derived_state = derived["page_id"], derived["state"]
            source_page_id, source_state = derived["source_page_id"], derived["source_state"]
            key = (page_id, derived_state)
            if not all(isinstance(value, str) and value for value in (page_id, derived_state, source_page_id, source_state)) or key in seen_derived_states or page_id != source_page_id or page_id not in selected_pages or source_state not in selected_pages[page_id] or derived_state in selected_pages[page_id]:
                fail("a derived state must be a new state of one approved source page")
            if not isinstance(derived["scenario_refs"], list) or not derived["scenario_refs"] or any(ref not in scenario_ids for ref in derived["scenario_refs"]):
                fail("derived states require approved Use Case scenario references")
            if not isinstance(derived["acceptance_refs"], list) or not derived["acceptance_refs"] or any(ref not in conditions_by_criterion for ref in derived["acceptance_refs"]):
                fail("derived states require approved Acceptance Criterion references")
            if derived["preserved_structure"] is not True or not isinstance(derived["added_state_expression"], str) or not derived["added_state_expression"].strip():
                fail("derived states must explicitly preserve structure and describe only the added state")
            image_path(run_dir, derived["prototype_path"], "derived state prototype")
            evidence_paths = derived["evidence_paths"]
            if not isinstance(evidence_paths, list) or not evidence_paths:
                fail("derived states require verification evidence")
            for evidence_path in evidence_paths:
                required_file(run_dir, evidence_path, "derived state evidence")
            if f"{page_id} / {derived_state}" not in prototype_text:
                fail("prototype slice must describe every derived state")
            seen_derived_states.add(key)
        covered_criteria = verification.get("criteria")
        if not isinstance(covered_criteria, list) or len(covered_criteria) != len(conditions_by_criterion):
            fail("prototype coverage must account for every acceptance criterion exactly once")
        deferred_ids = []
        seen = set()
        for item in covered_criteria:
            if not isinstance(item, dict) or not isinstance(item.get("acceptance_id"), str) or item["acceptance_id"] not in conditions_by_criterion or item["acceptance_id"] in seen:
                fail("prototype coverage has an invalid or duplicate acceptance_id")
            seen.add(item["acceptance_id"])
            status = item.get("status")
            if status not in {"covered", "deferred"}:
                fail("prototype coverage status must be covered or deferred")
            if status == "deferred":
                if not isinstance(item.get("reason"), str) or not item["reason"].strip():
                    fail("deferred acceptance criteria require a reason")
                deferred_ids.append(item["acceptance_id"])
                continue
            asserted = item.get("asserted_condition_ids")
            if not isinstance(asserted, list) or set(asserted) != conditions_by_criterion[item["acceptance_id"]]:
                fail("covered acceptance criteria must assert every observable condition exactly")
            checks = item.get("checks")
            if not isinstance(checks, list) or not checks:
                fail("covered acceptance criteria require one or more checks")
            for check in checks:
                if not isinstance(check, dict) or check.get("method") not in {"automated", "manual"} or not isinstance(check.get("assertion"), str) or not check["assertion"]:
                    fail("each prototype check requires a method and assertion")
                evidence_paths = check.get("evidence_paths")
                if not isinstance(evidence_paths, list) or not evidence_paths:
                    fail("each prototype check requires execution evidence")
                for evidence_path in evidence_paths:
                    required_file(run_dir, evidence_path, "prototype check evidence")
        axes = verification.get("interaction_axes")
        if not isinstance(axes, list):
            fail("prototype coverage requires interaction_axes")
        for axis in axes:
            if not isinstance(axis, dict) or not isinstance(axis.get("id"), str) or not axis["id"]:
                fail("each interaction axis requires an id")
            values = axis.get("values_checked")
            observations = axis.get("changed_observations")
            evidence_paths = axis.get("evidence_paths")
            if not isinstance(values, list) or len(values) < 2 or not isinstance(observations, list) or not observations or not isinstance(evidence_paths, list) or not evidence_paths:
                fail("each interaction axis requires two values, changed observations, and evidence")
            for evidence_path in evidence_paths:
                required_file(run_dir, evidence_path, "interaction axis evidence")
        structure_coverage = verification.get("structure_coverage")
        if not isinstance(structure_coverage, list) or not structure_coverage:
            fail("prototype coverage requires one or more selected structure-contract coverage records")
        seen_regions = set()
        contract_by_key = {
            (entry["page_id"], entry["state"], entry["region_id"]): entry
            for entry in selected_contract_entries
        }
        for item in structure_coverage:
            required = {"page_id", "state", "region_id", "selected_structure", "prototype_path", "assertion", "evidence_paths"}
            if not isinstance(item, dict) or required - set(item):
                fail("each structure coverage record requires page_id, state, region_id, selected_structure, prototype_path, assertion, and evidence_paths")
            page_id = item["page_id"]
            state_name = item["state"]
            region_id = item["region_id"]
            key = (page_id, state_name, region_id)
            if not all(isinstance(value, str) and value for value in key) or key not in selected_contract_keys or key in seen_regions:
                fail("structure coverage requires each selected Page / State / Region exactly once")
            if not all(isinstance(item[field], str) and item[field] for field in ("selected_structure", "prototype_path", "assertion")):
                fail("structure coverage requires non-empty structure, prototype path, and assertion")
            if item["selected_structure"] != contract_by_key[key]["selected_structure"]:
                fail("structure coverage selected_structure must match the approved selected structure contract")
            evidence_paths = item["evidence_paths"]
            if not isinstance(evidence_paths, list) or not evidence_paths:
                fail("structure coverage requires evidence paths")
            for evidence_path in evidence_paths:
                required_file(run_dir, evidence_path, "structure coverage evidence")
            seen_regions.add(key)
        if seen_regions != selected_contract_keys:
            fail("prototype structure_coverage must cover every selected structure-contract Region exactly once")
        review = read_json(run_path(run_dir, record.get("critic_review"), "G3 critic review"), "G3 critic review")
        if review.get("gate") != "G3" or review.get("verdict") != "pass":
            fail("prototype requires a passing G3 verification critic review")
        critic_references(review, "G3", run_dir, state)
        review_references = review.get("reference_artifacts", [])
        if not any(
            isinstance(reference, dict)
            and reference.get("artifact") == "wireframe_structure"
            and reference.get("path") == selected_blueprint
            and reference.get("sha256") == selected_blueprint_hash
            for reference in review_references
        ):
            fail("G3 critic must reference the approved selected G2A blueprint path and hash")
        if not any(
            isinstance(reference, dict)
            and reference.get("artifact") == "wireframe_structure"
            and reference.get("path") == selected_contract_relative_path
            and reference.get("sha256") == selected_contract_hash
            for reference in review_references
        ):
            fail("G3 critic must reference the approved selected G2A structure contract path and hash")
        if not any(
            isinstance(reference, dict)
            and reference.get("artifact") == "wireframe_structure"
            and reference.get("path") == baseline_relative_path
            and reference.get("sha256") == visual_baseline_hash
            for reference in review_references
        ):
            fail("G3 critic must reference the approved selected G2A structure-render baseline path and hash")
        if not any(
            isinstance(reference, dict)
            and reference.get("artifact") == "visual_design"
            and reference.get("path") == selected_visual_rules_relative_path
            and reference.get("sha256") == selected_visual_rules_hash
            for reference in review_references
        ):
            fail("G3 critic must reference the approved selected G2B visual rules path and hash")
        record["deferred_acceptance_ids"] = deferred_ids
    return record


def approved_decision(state: dict, run_dir: Path, gate: str) -> dict:
    name = DECISIONS[gate]
    record = artifact(state, run_dir, name, {"approved"})
    decision = read_json(run_dir / "decisions" / f"{gate}-{name.replace('_', '-')}.json", f"{gate} decision")
    required = {"run_id", "gate", "artifact", "artifact_version", "decision", "approved_scope", "excluded_scope", "reviewer_note"}
    if required - set(decision):
        fail(f"{gate} decision missing fields: {', '.join(sorted(required - set(decision)))}")
    if decision["run_id"] != state["run_id"] or decision["gate"] != gate or decision["artifact"] != name:
        fail(f"{gate} decision does not match this run/gate/artifact")
    if decision["artifact_version"] != record["version"] or decision["decision"] != "approved":
        fail(f"{gate} decision must approve the current {name} version")
    if not isinstance(decision["approved_scope"], list) or not isinstance(decision["excluded_scope"], list) or not isinstance(decision["reviewer_note"], str):
        fail(f"{gate} decision has invalid scope or reviewer note")
    return decision


def approved_implementation_authorization(state: dict, run_dir: Path, plan: dict, plan_item_ids: set[str]) -> dict:
    """Return the Human-Gate authorization only when it exactly accepts the reviewed proposal."""
    decision = approved_decision(state, run_dir, "PBC-4")
    record = state["artifacts"].get("prebuild_contract")
    if not isinstance(record, dict):
        fail("PBC-4 implementation authorization requires a pre-build contract")
    proposal = implementation_authorization_proposal(record, plan, plan_item_ids)
    authorization = decision.get("implementation_authorization")
    required = {"authorized", "allowed_plan_version", "allowed_plan_item_ids", "execution_mode", "stop_conditions", "prohibited_actions", "separate_approval_required_for", "approver_role", "approved_by", "approved_at"}
    if not isinstance(authorization, dict) or required - set(authorization) or authorization.get("authorized") is not True or not isinstance(authorization["allowed_plan_item_ids"], list) or not authorization["allowed_plan_item_ids"] or not all(isinstance(authorization[field], str) and authorization[field] for field in {"allowed_plan_version", "execution_mode", "approver_role", "approved_by", "approved_at"}) or not non_empty_strings(authorization["stop_conditions"]) or not non_empty_strings(authorization["prohibited_actions"]) or not non_empty_strings(authorization["separate_approval_required_for"]):
        fail("PBC-4 Gate Decision requires a complete explicit implementation authorization")
    for field in ("allowed_plan_version", "allowed_plan_item_ids", "execution_mode", "stop_conditions", "prohibited_actions", "separate_approval_required_for", "approver_role"):
        if authorization[field] != proposal[field]:
            fail(f"PBC-4 implementation authorization must match the critic-reviewed proposal: {field}")
    return authorization


def approved_visual_design(state: dict, run_dir: Path) -> tuple[Path, str]:
    """Validate the one visual direction and global rules chosen at G2B."""
    decision = approved_decision(state, run_dir, "G2B")
    record = state["artifacts"]["visual_design"]
    directions = record.get("directions")
    selected_direction_id = decision.get("selected_direction_id")
    if not isinstance(directions, dict) or not isinstance(selected_direction_id, str) or selected_direction_id not in directions:
        fail("G2B decision must select exactly one offered design direction")
    direction_briefs = record.get("direction_briefs")
    if not isinstance(direction_briefs, dict) or not isinstance(direction_briefs.get(selected_direction_id), str):
        fail("selected G2B direction requires a direction brief")
    ui_surfaces = approved_ui_surfaces(state, run_dir)
    rules_path, rules_hash = selected_visual_rules_document(
        run_dir, decision.get("selected_visual_rules_path"), selected_direction_id, direction_briefs[selected_direction_id], set(ui_surfaces)
    )
    selected_foundation = component_foundation_rows(rules_path.read_text(), "selected global visual rules")
    direction_foundation = component_foundation_rows(
        required_file(run_dir, direction_briefs[selected_direction_id], "selected G2B direction brief").read_text(),
        f"design direction {selected_direction_id} brief",
    )
    if selected_foundation != direction_foundation:
        fail("selected global visual rules must copy the approved direction Component foundation exactly")
    if ui_surface_adaptation_rows(rules_path.read_text(), "selected global visual rules", set(ui_surfaces)) != ui_surface_adaptation_rows(
        required_file(run_dir, direction_briefs[selected_direction_id], "selected G2B direction brief").read_text(),
        f"design direction {selected_direction_id} brief",
        set(ui_surfaces),
    ):
        fail("selected global visual rules must copy the approved UI surface adaptations exactly")
    return rules_path, rules_hash


def approved_wireframe_selection(state: dict, run_dir: Path) -> None:
    """Validate G2A's selected screens after its artifact and gate decision are fixed."""
    decision = approved_decision(state, run_dir, "G2A")
    record = state["artifacts"]["wireframe_structure"]
    page_states = page_inventory_details(run_dir, record.get("page_inventory"), record["version"])
    candidates = record.get("candidate_pages")
    if not isinstance(candidates, dict):
        fail("approved wireframe structure requires candidate page maps")
    g2a_selection_export(run_dir, decision, record["version"], candidates, page_states)
    selected_pages = record.get("selected_pages")
    renderable_page_map(run_dir, selected_pages, page_states, "approved selected structure")
    selected_visual_baseline(run_dir, record.get("selected_visual_baseline"), selected_pages)
    blueprint_document(run_dir, record.get("selected_blueprint"), page_states, "approved structure blueprint")
    selected_structure_contract(
        run_dir,
        record.get("selected_structure_contract"),
        state["run_id"],
        record["version"],
        selected_pages,
    )


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_artifacts.py <run-dir>")
        return 2
    run_dir = Path(sys.argv[1])
    state_path = run_dir / "run-state.json"
    source_path = run_dir / "source-manifest.json"
    if not state_path.is_file() or not source_path.is_file():
        fail("run-state.json and source-manifest.json are required")
    try:
        state = json.loads(state_path.read_text())
        source = json.loads(source_path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON: {exc}")
    missing = REQUIRED - set(state)
    if missing:
        fail(f"run-state missing fields: {', '.join(sorted(missing))}")
    if state["current_gate"] not in GATES:
        fail("invalid current_gate")
    if state["phase"] != "prebuild" and state["current_gate"] in {"G0", "G1", "G2A", "G2B", "G3"}:
        fail("G0-G3 must use phase=prebuild")
    if state["phase"] != "prebuild_contract" and state["current_gate"] in {"PBC-0", "PBC-1", "PBC-2", "PBC-3", "PBC-4"}:
        fail("PBC-0 through PBC-4 must use phase=prebuild_contract")
    if state["phase"] != "build" and state["current_gate"] in {"G4", "G5"}:
        fail("G4 and G5 must use phase=build")
    if state["phase"] != "verification" and state["current_gate"] in {"G6", "G7"}:
        fail("G6 and G7 must use phase=verification")
    if not isinstance(state["artifacts"], dict):
        fail("artifacts must be an object")
    runtime_mode = factory_profile(state, run_dir)
    if runtime_mode == "legacy":
        print("LEGACY: this run predates the pinned runtime; resume it only with its original runtime or start a new run")
        return 2
    if state["work_type"] != "new_flow" or state["risk_level"] not in {"standard", "high"}:
        fail("work_type or risk_level is invalid")
    if source.get("run_id") != state["run_id"]:
        fail("source manifest run_id must match run-state")
    if not isinstance(source.get("sources"), list) or not isinstance(source.get("excluded_sources"), list):
        fail("source manifest requires sources and excluded_sources arrays")
    read_json(run_dir / "repository-snapshot.json", "repository snapshot")

    gate_rank = GATES.index(state["current_gate"])
    if gate_rank >= GATES.index("G1"):
        artifact(state, run_dir, "context_packet", {"critic_passed", "approved"})
        artifact(state, run_dir, "evidence_pack", {"critic_passed", "approved"})
        intent_sources = [item for item in source["sources"] if isinstance(item, dict) and item.get("context_role") == "intent"]
        if not intent_sources:
            fail("source manifest requires at least one intent source before G1")
        if any(item.get("content_mode") != "full_document" for item in intent_sources):
            fail("source manifest intent sources must use content_mode=full_document")
    if gate_rank >= GATES.index("G2A") or (state["current_gate"] == "G1" and state["status"] == "awaiting_human_gate"):
        artifact(state, run_dir, "use_case", {"critic_passed", "approved"})
    if gate_rank >= GATES.index("G2A"):
        approved_decision(state, run_dir, "G1")
    if state["current_gate"] == "G2A" and state["status"] == "awaiting_human_gate":
        artifact(state, run_dir, "wireframe_structure", {"draft", "critic_passed", "approved"})
    if gate_rank >= GATES.index("G2B"):
        approved_wireframe_selection(state, run_dir)
    if state["current_gate"] == "G2B" and state["status"] == "awaiting_human_gate":
        artifact(state, run_dir, "visual_design", {"draft", "critic_passed", "approved"})
    if gate_rank >= GATES.index("G3"):
        approved_decision(state, run_dir, "G2B")
        artifact(state, run_dir, "prototype", {"draft", "critic_passed", "approved"})
    if state["current_gate"] == "G3" and state["status"] == "approved":
        g3_decision = approved_decision(state, run_dir, "G3")
        prototype = artifact(state, run_dir, "prototype", {"approved"})
        if not set(prototype.get("deferred_acceptance_ids", [])).issubset(set(g3_decision["excluded_scope"])):
            fail("G3 decision excluded_scope must include every deferred acceptance criterion")

    if gate_rank >= GATES.index("PBC-0"):
        g3_decision = approved_decision(state, run_dir, "G3")
        prototype = artifact(state, run_dir, "prototype", {"approved"})
        if not set(prototype.get("deferred_acceptance_ids", [])).issubset(set(g3_decision["excluded_scope"])):
            fail("G3 decision excluded_scope must include every deferred acceptance criterion")
        pbc_input_lock(state, run_dir)
    if gate_rank >= GATES.index("PBC-1"):
        engineering_discovery(state, run_dir)
    if gate_rank >= GATES.index("PBC-2"):
        plan, plan_item_ids = coding_plan(state, run_dir)
    else:
        plan, plan_item_ids = None, set()
    if gate_rank >= GATES.index("PBC-3"):
        verification_plan(state, run_dir, plan)
    if gate_rank >= GATES.index("PBC-4"):
        prebuild_contract(state, run_dir, plan, plan_item_ids)
    if state["current_gate"] == "PBC-4" and state["status"] == "approved":
        approved_implementation_authorization(state, run_dir, plan, plan_item_ids)

    if gate_rank >= GATES.index("G4"):
        approved_implementation_authorization(state, run_dir, plan, plan_item_ids)
        packet_items, packet_path = slice_execution_packet(state, run_dir, plan, plan_item_ids)
        selected_items = implementation_contract(state, run_dir, plan, plan_item_ids, packet_items, packet_path)
    else:
        selected_items = set()
    if gate_rank >= GATES.index("G5"):
        execution_ledger(state, run_dir, plan, selected_items)
    if gate_rank >= GATES.index("G6"):
        verification_report(state, run_dir, plan, selected_items)
    if gate_rank >= GATES.index("G7"):
        cycle_decision(state, run_dir, plan, selected_items)

    print(f"PASS: {run_dir} at {state['current_gate']} / {state['status']} [{runtime_mode}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
