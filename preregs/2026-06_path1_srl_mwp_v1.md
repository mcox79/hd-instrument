# Prereg: path1_srl_mwp_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research GREEN-LIT Path 1 SRL targeted operand-selection test (8th-rule empirical test).
Trained schema-classifier (count-NB cues->schema->op) + role-labeler (averaged-perceptron number-context->arg_role) on Research's 30
MWP-SRL examples; applied to ASDiv-1op with schema role-template operand-selection (CHANGE_SUB initial-given, SHARE total-recipients).
HARD-PASS acc>=0.45 (+0.06; targeted-is-lever VALIDATED). MIDDLE 0.43-0.45. HARD-FAIL <0.43 (6th angle; targeted-minimal insufficient -> Phase-6).
