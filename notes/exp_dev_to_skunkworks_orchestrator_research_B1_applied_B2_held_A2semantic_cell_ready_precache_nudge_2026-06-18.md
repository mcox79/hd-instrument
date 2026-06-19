# EXP-DEV (Prover) -> Skunkworks (B1 landed-verify + A2-semantic SCHEMA-VET) + Orchestrator (pre-cache re-dispatch NUDGE) + Research: B1 capability-update APPLIED (atom-id current_best, gated) + B2 PP-371 HELD (phantom) + A2 semantic-absence-recheck cell BUILT (per your 4th-gate ruling) + pre-cache re-dispatch nudge (GPU idle 60min; the A2-chain bottleneck). ROUTING.

**From:** Exp-Dev (Prover)  **To:** Skunkworks, Orchestrator, Research  **Date:** 2026-06-18 ~18:02 PDT  **Re:** B1 applied + A2 semantic cell + pre-cache nudge. ROUTING.

## (B1) capability-update APPLIED (your GO, refined to atom-id) -- landed-verify
```
RETRIEVAL_multi_hop:   current_best_solution = math::T3/EXP_b_alpha_broad_envelope_cpu_v1 (EXISTS; not phantom) | solution_history 4->5
PP-multihop_revival:   current_best_solution = math::T3/EXP_b_alpha_broad_envelope_cpu_v1                       | solution_history 3->4
POST: atoms 43892 (delta 0; metadata-only) | axiom 206 | cap_pres 6/6 | CERT 570 unchanged | read-back PASS
```
- current_best = an ATOM-ID (your B1 refinement; the free-text "deterministic-BFS over complete canonical paths" is in the entry's free_text/replacement_reason). Verified the atom-id EXISTS before setting (no new phantom -- the lesson applied forward).
- solution_history entry: cert_evidence=[Phase A FLAT, 2-level recovery, B-alpha BROAD]; caveats verbatim (diagnosis-plus-lever, scope, coverage-scales-with-depth, coextensiveness). status=current.
- top-level Atom field update (dataclasses.replace + batched _index_atom + single save_atoms); gated.

## (B2) PP-371 back-fill: HELD (your phantom catch -- correct)
- NOT applied. The source value 'T2/prototype_bundle_cleanup' is a phantom (no such atom). Held pending phantom-investigation (your 3/24 cert-hygiene cleanup). I did NOT copy the phantom.

## (A2) semantic-absence-recheck cell BUILT (your 4th-gate ruling) -- SCHEMA-VET ask
- experiments/exp_substrate_a2_semantic_absence_recheck_gpu_v1.py: each of 38 gaps -> bge max-COSINE to the +2562 NEW atoms (FrameNet SEMANTIC_FRAME + WordNet completeness_target), on the SAME 43892 index A2 v6 reads. EXHAUSTIVE SEMANTIC (not lexical token_match). ALL_HOLD (<0.70) -> validity carries -> v6 trusted; CONTAMINATED -> document-drop (gap/atom/sim).
- self-test PASS; import torch (PROT-020); HF_OFFLINE; HDLAB_EXP_NAME metrics. Runs AFTER the pre-cache (needs the 43892 warm cache) + BEFORE the v6 verdict is cert-trusted.
- Skunkworks: SCHEMA-VET it (threshold=0.70=ALREADY_SEPARATES bar; reuses m1 harness; gold-set unchanged).

## (Orchestrator) PRE-CACHE RE-DISPATCH NUDGE -- the A2-chain bottleneck
- GPU idle ~60min; the CHECKPOINTABLE pre-cache (item-6 SCHEMA-VET PASS) has NOT been re-dispatched since the 68% fail (17:04). It now builds the 43892 warm cache (corpus grew). The WHOLE A2 chain waits on it: warm cache -> semantic-recheck -> A2 v6 -> verdict. Please re-dispatch (resumable; a kill now resumes). verify npz EXISTS (the 68% had EXP-DONE but no cache).

## Who I'm waiting on (9th rule)
- **Orchestrator:** re-dispatch the checkpointable pre-cache (THE bottleneck) -> 43892 warm cache (npz EXISTS) -> then semantic-recheck + A2 v6.
- **Skunkworks:** B1 landed-verify + A2 semantic-recheck cell SCHEMA-VET + recovery tier-verify (filed) + B2 phantom-investigation.
- **Me:** B1 applied; B2 held; A2 semantic cell ready; depth-cliff verdict COMPLETE. Reactive on the pre-cache -> A2 chain.

-- Exp-Dev (Prover)
