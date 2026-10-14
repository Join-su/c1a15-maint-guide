"""고정 validator 파일은 고치지 않고, verification_plan이 참조하지만 정의하지 않은 세 이름만
coding_plan()과 같은 방법으로 계산해 모듈 전역에 넣은 뒤 원래 main()을 실행한다. 실행: python3 shim.py <run-dir>"""
import importlib.util, json, sys
from pathlib import Path
run = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("va", run / "factory-profile/snapshot/skill/scripts/validate_artifacts.py")
va = importlib.util.module_from_spec(spec); spec.loader.exec_module(va)
state = json.load(open(run / "run-state.json"))
plan = json.load(open(run / state["artifacts"]["coding_plan"]["path"]))
va.surface_delivery = plan["implementation_design"]["ui_surface_delivery"]   # coding_plan() 582행과 같은 값
va.plan_item_slice = {i["id"]: i["slice_id"] for i in plan["items"]}           # coding_plan() 583행과 같은 값
va.ui_surfaces = va.approved_ui_surfaces(state, run)                            # coding_plan() 581행과 같은 값
sys.argv = ["validate_artifacts.py", str(run)]
sys.exit(va.main())
