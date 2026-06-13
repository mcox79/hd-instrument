# exp_dev hand-off — research: INV-1 authoring-blind null methodology for load-bearing-axis audit

Filed-by: research sub-agent (Opus)
Date: 2026-06-13
Trigger: notes/research_DRILL_authoring_blind_null_methodology_for_load_bearing_axis_audit_skunkworks_INV1_support_2026-06-13.md
Pause state: respect data/orchestrator_paused.flag — if present, file as queued anchor only; do not ship.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off provides anchor candidates, substrate-product reading, tier hint, and why-now. It does NOT inline experiment design; exp_dev owns design autonomy per role contract.

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY): INV-1 cell — authoring-blind load-bearing-axis re-validation

- Anchor pointer: notes/research_DRILL_authoring_blind_null_methodology_for_load_bearing_axis_audit_skunkworks_INV1_support_2026-06-13.md (section "Recommended INV-1 cell design")
- Substrate-product reading: this is a FALSIFICATION gate on the substrate-product positioning artifact that load-bearing axis exists independent of curator authoring. HARD-PASS strengthens the categorical claim; HARD-FAIL forces an honest footnote on the 3-axis-orthogonal capstone.
- Tier hint: TIER-1. Closes a skunkworks-flagged confound on a CRITICAL capstone result.
- Why-now: three "independent" tests (PROVISIONAL 1.33x, INTRINSIC 3/3, DEFINITIVE 2.34x p=0.0005) all measured on the same authored graph; the DEFINITIVE null controls degree only, not edge-set authoring. Skunkworks INV-1 is the cheapest decisive test of whether the three results are one confound.
- Cost: ~2-4 hrs local CPU on existing atom bodies. No GPU. No new ingest required.
- Pre-reg per envelope-fail-bands: HARD-PASS / HARD-FAIL / MIDDLE-BAND defined in anchor doc.
- 3x3 arm-null tensor: arm_C1 operator-cooccurrence Jaccard, arm_C2 bge-cosine on definition text with stop-phrase mask, arm_C3 shared-symbol overlap; nulls A degree-aware label perm, B configuration model, C DC-SBM.

### Anchor 2 (secondary, gated on INV-1 outcome): C1/C2/C3 sensitivity decomposition

- Substrate-product reading: which body-text features carry the axis signal? This is itself a substrate-product claim ("axis is readable from operator surface alone" vs "axis requires definition prose").
- Tier hint: TIER-2 if INV-1 passes; SHELVED if INV-1 fails.
- Why-now: only after INV-1 returns a verdict; running it in parallel wastes CPU on a possibly-moot decomposition.

## Context pointers

- Research note (anchor): notes/research_DRILL_authoring_blind_null_methodology_for_load_bearing_axis_audit_skunkworks_INV1_support_2026-06-13.md
- Prior DEFINITIVE test (target of audit): grep cap_map + recent verdicts for "DEFINITIVE 2.34x" or "load-bearing axis".
- 3-axis-orthogonal capstone (downstream artifact under audit): MEMORY index entry "Architecture 3-axis EMPIRICALLY ORTHOGONAL Cell #3 + KP P6 HARD-PASS USER craftsman VERBATIM corroborated 13th rule 2nd appearance 2026-06-13".
- 13th methodology rule (tools-vs-materials) 1st + 2nd appearance memos (per MEMORY index).
- Standard null-model literature: Farine 2017 (Methods Ecol Evol), Fosdick/Larremore block-constrained configuration model (Springer Applied Network Science 2019), Hart et al PMC 2022.

## Contract

- exp_dev executes per its own role contract (verification/, smoke gate, REMOTE VERIFY, atomic queue_add, status_log entry).
- Pre-registration of HARD-PASS / HARD-FAIL fail bands MUST occur before any rebuilt-graph metric is computed (anchor doc gives the bands).
- The C3 arm is the gate: shared-symbol overlap edges (sparsest, lowest power, most authoring-blind) must show z >= 2.0 for HARD-PASS.
- No curator-applied tool/material tag may be read by any C1/C2/C3 edge generator. Tags are stripped at ingest. Verification: emit a one-line audit that arm code reads only `body`, `symbols`, `definition_text` fields.

## Autonomy declaration

exp_dev has full design autonomy on:
- Implementation language and library choice for C1/C2/C3 edge generators
- Resample count for null distributions (N_null >= 1000 recommended; exp_dev may raise)
- bge model variant selection for arm_C2
- Stop-phrase mask vocabulary for arm_C2 (suggested seed list: "operator", "function", "tensor", "vector", "represents", "maps", "denotes", "defines"; exp_dev may extend)
- Which downstream load-bearing metric M variant to use (must match DEFINITIVE test for comparability; if multiple variants exist, run all)
- Order of arm execution (C3 first is recommended — cheapest + highest information per CPU)

exp_dev does NOT have autonomy on:
- The HARD-PASS / HARD-FAIL fail bands (pre-registered in anchor doc)
- The principle that no curator tag may be read by any arm
- The C3-as-gate requirement
