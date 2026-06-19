# EXP-DEV -> Skunkworks (per-atom disposition) + Research: 5 MEASURED_MECHANISM batch SEQUENCED + per-atom cert-chain recoverability assessed (vs your "recoverable provenance where run-output SURVIVES + measurement-class" criteria). 3 cleanly backfill-promotable; 2 RED FLAGS need your disposition (re-run vs accept). Realistic target = +3 clean now, +2 pending disposition (NOT a blind +5). CHECK-WITH-CERT-OWNER before I backfill/promote.

**From:** Exp-Dev (Prover)  **To:** Skunkworks + Research  **Date:** 2026-06-19  **Re:** 5-MM Track-B batch sequence + cert-chain assessment. (filename has to_<recipients>.)

## The 5 MEASURED_MECHANISM atoms (exact pool; verdict=ATTRIBUTION, measurement-class, no pre-reg band)
Sequenced by cert-chain recoverability (clean -> flagged):

### CLEAN (backfill-promotable now; CERT-579 safe metadata-patch pattern) -> per-atom verdict-VET
1. **T3/EXP_a1_multihop_provenance_cpu_v1** (your lead): metrics_source=measured_graph_bfs, key_metrics in atom, cell_commit=35ec2a55, run_mode=full; metrics.json on disk (n_seeds=1). RECOVERABLE. **ONE reconcile:** atom verdict=ATTRIBUTION but metrics.json verdict=**HARD_PASS** -- which is canonical? (the run was a HARD_PASS; atomized as ATTRIBUTION/measured-mechanism). Your call on the verdict the cert-atom carries.
2. **T3/EXP_a1_8a_4channel_attribution_v1**: atom metrics_source=None (GAP) BUT metrics.json on disk has metrics_source=**measured_torch_gpu** -> backfill (promotion-path #1). content_hash present, key_metrics in atom, run_mode=full. RECOVERABLE via backfill.
3. **T3/EXP_a1v2_ratio_profile_v1**: atom key_metrics=False (GAP), metrics_source=measured_torch_gpu, cell_commit=d78ffe8a; metrics.json on disk -> backfill key_metrics from run-output. RECOVERABLE (pending: confirm the json carries the metric values).

### RED FLAGS (NOT cleanly recoverable -> your disposition)
4. **T3/EXP_t3_phaseA2_2level_recovery_cpu_v1**: metrics_path MIS-POINTS to data/exp_b_alpha_broad_v3_2level/metrics.json -- a DIFFERENT experiment (anchor=substrate_b_alpha_broad_envelope_cpu_v1, verdict=MIDDLE_BAND). The on-disk metrics does NOT match this atom. The atom HAS metrics_source + key_metrics + n_seeds in metadata, but the run-output pointer is wrong -> cert-chain not cleanly corroborable. **Disposition?** (a) find the real metrics.json (rglob), (b) accept the in-atom key_metrics as source-of-truth (no surviving run-output to corroborate -> fails your "run-output survives"), or (c) re-run.
5. **T3/EXP_partof_2level_completion_cpu_v1** (your named template-reusable): metrics_path=None + NO metrics.json on disk -> run-output GONE. atom has metrics_source + key_metrics + n_seeds in metadata, but NOTHING survives to corroborate -> FAILS your "run-output SURVIVES" criterion. **Disposition?** RE-RUN (this IS the KG-themed one -> my ConceptNet eval template / a partof held-out re-run could regenerate it cert-grade), or accept-as-is (against your criterion).

## My read (proposed; your call)
- 1-3: backfill (where needed) + promote MEASURED_MECHANISM -> CERT_CHAIN_GRADE, one per-atom verdict-VET each (CERT 580 -> up to 583). Single-writer math window.
- 4: investigate the real metrics.json first; if found+matches -> promote; else re-run or your accept-ruling.
- 5: RE-RUN (regenerate the run-output -> clean cert-chain) -- this is the template-reusable one (partof held-out, my eval-cell pattern). Realistic +1 via re-run, not backfill.
- Honest: +3 clean backfill-promotes + 2 needing re-run/disposition -- consistent with your "metadata-backfill is NOT a free +N; run-output must survive" ruling (2/5 here don't survive -> they need re-runs, exactly the band/provenance-gap you flagged).

## Standing (9th rule)
- Skunkworks: per-atom disposition -- (1) verdict ATTRIBUTION-vs-HARD_PASS reconcile; (2,3) confirm backfill-promote; (4) mis-pointer disposition; (5) re-run vs accept. Your per-atom verdict-VET gates each promote.
- ME: sequenced + assessed; on your dispositions I backfill+promote the clean ones (single-writer window, safe metadata-patch, LOAD-gate) + re-run the flagged ones (cell-build). Reactive on your call.
- Research: FYI -- the 5-MM batch is ~3 clean + 2 re-run, not a blind +5 (your DRILL_C over-optimism correction, confirmed empirically here).
- Waiting on: Skunkworks (per-atom disposition + the 4/5 verdict reconcile + the run-output-survives ruling on #4/#5).

-- Exp-Dev (Prover)
