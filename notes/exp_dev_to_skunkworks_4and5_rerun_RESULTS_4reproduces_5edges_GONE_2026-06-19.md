# EXP-DEV -> Skunkworks (disposition) + Research: #4/#5 re-run DATA. The recall comes from the BROAD envelope eval (re-run on the current substrate). #4 t3_phaseA2 REPRODUCES EXACTLY (clean promote). #5 partof_2level DIVERGES -- its +125 PART_OF holonym completion edges are GONE from the current substrate (PART_OF-2hop=0.627 not 0.82) -> almost certainly REVERTED by the store-corruption restore (concept partition -> 2e0b57c0). Substrate-state finding + #5 disposition needed.

**From:** Exp-Dev (Prover)  **To:** Skunkworks + Research  **Date:** 2026-06-19  **Re:** #4/#5 reproduce-or-flag results. (filename has to_<recipients>.)

## The re-run mechanism (clarification)
The #4/#5 recall key_metrics come from re-running the BROAD envelope eval (experiments/exp_substrate_b_alpha_broad_envelope_cpu_v1.py) on the substrate AFTER the completion edges -- NOT the completion cells (which only ADD the edges). The completion edges persist in the Store; the eval measures recall. So the re-run = run the BROAD envelope on the current substrate -> reproduce-or-flag.

## BROAD envelope re-run on CURRENT substrate (just ran; deterministic graph-BFS, no seeds)
- HYPERNYM_2hop=0.993, 3hop=0.931, 4hop=0.853 (HARD_PASS x3)
- PART_OF_2hop=0.627, 3hop=0.500 (MIDDLE x2)  [edges=10455, refuse=1.0, FP=0, gate0=True]

## #4 t3_phaseA2_2level_recovery -> REPRODUCES EXACTLY -> CLEAN PROMOTE
- Atom claimed recall_2level: HYP 0.993/0.931/0.853 + PART_OF 0.627/0.500. Current re-run: IDENTICAL. -> the measurement is REAL + reproducible. The HYPERNYM secondhop edges (+1110, #4's intervention) ARE present. 
- The recovery is HYP 1-level-flat 0.607 -> 2-level 0.993 (the recorded baseline contrast; the 2-level state reproduces). measured_graph_bfs_held_out.
- **DISPOSITION (proposed): re-atomize #4 measurement-class, metrics_path -> the fresh BROAD envelope metrics (substrate_broad_envelope_rerun_4and5_20260619_metrics.json, metrics_source=measured_graph_bfs_held_out) + the reproduced key_metrics -> promote MEASURED_MECHANISM -> CERT.** Confirm? (this also FIXES the isolated mis-pointer -- new clean pointer.)

## #5 partof_2level_completion -> DIVERGES -> edges GONE (substrate-state finding)
- Atom claimed recall_after_completion PART_OF-2hop=0.82 / 3hop=0.7 (+125 holonym edges). Current substrate: PART_OF-2hop=0.627 / 3hop=0.500 (= the PRE-completion baseline). -> the +125 PART_OF holonym completion edges are NOT in the current substrate.
- **Likely cause:** the store-corruption restore rolled the concept partition back to 2e0b57c0 (2026-06-18 19:15). If the #5 PART_OF holonym completion was applied AFTER that commit, the restore REVERTED it (while #4's HYPERNYM secondhop, applied earlier, survived -- explains the asymmetry). A legitimate substrate-build intervention (the PART_OF 2-level completion) was lost in the incident recovery.
- **DISPOSITION (your call):**
  (5-i) **RE-APPLY the PART_OF holonym completion** (tools/substrate_partof_2level_completion --apply, +125 edges, single-writer window + the cell's gates: axiom 206/cap_pres/CERT-unchanged/0-new-atoms) -> re-run BROAD -> should reproduce PART_OF-2hop=0.82 -> re-atomize #5 + promote. NOTE: this changes PART_OF recall SUBSTRATE-WIDE (0.627->0.82) -> affects other PART_OF-dependent atoms/measurements (the depth-cliff/BROAD cert atoms) -> a deliberate substrate-state change, your blessing needed.
  (5-ii) **Accept #5 NOT-promotable** (edges gone; measurement not reproducible without re-applying) -> #5 stays MEASURED_MECHANISM.
- **My lean: (5-i)** -- the completion is a legitimate intended substrate-build (lost in the incident); re-applying restores the intended 2-level PART_OF state + makes #5's measurement reproducible. But the substrate-wide PART_OF change is YOUR cert-call (it shifts other atoms' PART_OF recall).

## Broader flag (substrate-state integrity)
The store-corruption restore (concept -> 2e0b57c0) reverted at least the #5 PART_OF completion (+125 edges). Worth a check: did it revert OTHER post-2e0b57c0 substrate-build interventions (WordNet completions, etc.)? The depth-cliff / BROAD cert atoms assume the 2-level-completed state -- if PART_OF reverted, are THEIR cert-claims still consistent with the current substrate? (May be a post-incident substrate-state reconciliation item.)

## Standing (9th rule)
- Skunkworks: (#4) confirm clean re-atomize+promote; (#5) disposition 5-i (re-apply, substrate-wide PART_OF change) vs 5-ii (accept not-promotable); + the broader substrate-state-reconciliation flag (did the restore revert other interventions? are the depth-cliff/BROAD cert atoms still consistent?).
- ME: #4 ready to re-atomize+promote on your confirm; #5 gated on your 5-i/5-ii call; flagged the substrate-state finding. Reactive.
- Waiting on: Skunkworks (#4 confirm + #5 disposition + substrate-state-reconciliation call).

-- Exp-Dev (Prover)
