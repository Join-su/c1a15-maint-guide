"""판정 엔진(P-03, B-05): 명세 4장 R1 · R2 · R4 · R5 · R6 · R7 · R9 · R13을 LLM · DB · 네트워크 없이 계산하는 순수 함수.

판정은 코드가 하고 LLM은 문장만 쓴다(Authority boundary). LangGraph는 중단 · 재개 껍데기로만 쓴다(graph.py).
"""
