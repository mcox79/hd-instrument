

## pasted by the owner 2026-09-13 12:26 (raw; strategy reads this)

SUBMISSION — problem: coordination_is_parallel_structure_not_a_convention_the_coordinator_predicts_a_like_conjunct

STATUS: SOLVED (primary target CI-separated; two honest secondaries reported as negatives).

RESULT (UD-EWT test 700, gold categories, cap 6000): conj recall 0.300 → 0.391 map1
(paired Δ +0.090, CI [0.0515, 0.133]) and 0.300 → 0.373 incr (CI [0.034, 0.112]) —
CI-separated under BOTH decodes. UAS 0.6034 → 0.6055 (up). Robust across prediction
strength (gamma 2→8 all CI-separated, no cliff).

MECHANISM (both halves treebank-free, brain-foundational): coordination = parallel-
structure prediction (Frazier/Munn/Taft&Clifton 2000; Levy 2008; Lewis&Vasishth 2005).
The wall was UPSTREAM and non-BF: the acquisition teacher was coordination-blind (0.054
posterior mass on gold conj arcs). Fix = (1) parallel-structure prediction added to the
teacher (parallelism_boost), (2) corrected read-time construction that identifies the
parallel HEADS (coord_sites). Knowledge in counts, online-observable (plastic).

CONTROLS: scramble twin (parallelism removed) 0.197 — BELOW base; shuffled-strengths
twin at chance; ablation constr_only 0.322 / teach_only 0.335 / full 0.391 (superadditive).

RIGOROUS NEGATIVES (the "right not easy" pursuit): NEAR conj at structural ceiling
(0.535); FAR conj (9+ tokens, 26% of all conj) at ~0.016, unreachable by any positional
rule — LOCATED at the MEANING CHANNEL. Five bounded meaning-free levers tested, none
reaches far: skip-PP L, chain-top L, slot-sharing, coordinator hold-conditioning,
distance-invariant decode bonus. cc secondary: +0.059, NOT CI-separated (withdraw-first).

PROPOSED hdlab CHANGE (Q111 — strategy lands): hdlab/attachment_arm.py coord_arcs +
parallelism_boost (diff in notes/problems/<slug>/attachment_arm_patch.diff) + one line
in tools/build_attachment_validities.py; then rebuild attachment_validities_v1.json.
Do NOT wire slot-sharing (refuted). Open owner decision: accept the nsubj −0.017
give-back (recommend yes, per repair-don't-revert).

PRIORITY NEXT STEPS: (1) HIGH — file FAR coordination as a meaning-channel problem
(co-argument grounding); (2) MED — re-check coref / who-did-what on the rebuilt asset;
(3) LOW — reading-induced CCONJ (pri-15) for the zero-foundation-seed path only.

REVERIFY: .venv/Scripts/python.exe verification/test_attachment_coordination.py  (6/6)
FILES: experiments/exp_attachment_coordination_v1.py, verification/test_attachment_
coordination.py, notes/problems/<slug>/{SOLVED.md, FINDINGS_signal_trace.md,
attachment_arm_patch.diff, AUDIT_UPDATE.md}
