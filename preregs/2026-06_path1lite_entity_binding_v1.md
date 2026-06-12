# Prereg: path1lite_entity_binding_mwp_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research operand-selection drill Path-1-LITE probe (no CoNLL-2005).
Heuristic entity-quantity binding (number -> nearest name + next noun; question-object selects operands; op from cue). Tests the SRL
linguistic angle cheaply to inform the full-Path-1 (CoNLL-2005, 3-5d) decision. HARD-PASS acc>=0.49. MIDDLE 0.43-0.49 (full SRL warranted).
HARD-FAIL <0.43 (5th triangulation angle -> operand-selection corpus-bound; full SRL likely plateaus -> defer Phase-6).
