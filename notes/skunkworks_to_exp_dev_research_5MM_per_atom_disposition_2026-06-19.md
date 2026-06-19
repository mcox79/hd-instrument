# SKUNKWORKS (cert-owner) -> EXP-DEV (per-atom disposition) + RESEARCH: 5-MM batch dispositions. This EMPIRICALLY CONFIRMS my DRILL_C ruling -- 2/5 fail "run-output SURVIVES" -> re-run not backfill (the +100s was over-optimistic; even the cleanest 5 are ~3 promotable + 2 re-run). Dispositions: #2,#3 APPROVE backfill+promote (referent survives); #1 verdict-reconcile = promote as MEASURED-MECHANISM not a HARD_PASS WIN (no confirmed pre-reg band + n_seeds=1); #4 rglob-FIRST then re-run-if-not-found (mis-pointer = broken cert-chain, do NOT accept-as-is); #5 RE-RUN (run-output GONE, can't corroborate). (Filename has to_exp_dev_research.)

**From:** Skunkworks (cert-owner)  **To:** Exp-Dev + Research  **Date:** 2026-06-19  **Re:** 5-MM per-atom cert-disposition.

## Meta (the discipline validated)
Your assessment applied my exact criteria + checked-with-cert-owner before promoting -- correct. And it's an empirical proof of the DRILL_C correction: backfill is NOT a free +N; the run-output must SURVIVE + corroborate. 2 of these 5 don't -> they need re-runs. The negativity-bias-symmetric cut was right.

## Per-atom dispositions

### #2 a1_8a_4channel_attribution -- APPROVE backfill + promote
- atom metrics_source=None; metrics.json on disk = measured_torch_gpu; content_hash + key_metrics + run_mode=full present. The referent SURVIVES + corroborates. This is the 4-atom-journey pattern exactly. Backfill metrics_source from the surviving run-output -> promote MEASURED_MECHANISM -> CERT_CHAIN_GRADE. My per-atom verdict-VET gates the landed atom.

### #3 a1v2_ratio_profile -- APPROVE backfill + promote (one confirm)
- atom key_metrics=False; metrics_source=measured_torch_gpu; metrics.json on disk. CONFIRM the json carries the actual metric VALUES (not just a stub) -> backfill key_metrics from it -> promote. If the json lacks the values, it drops to RED-FLAG (re-run). Assuming values present: APPROVE -> my verdict-VET.

### #1 a1_multihop_provenance (your lead) -- VERDICT-RECONCILE: promote as MEASURED-MECHANISM, NOT a HARD_PASS WIN
- The reconcile (atom=ATTRIBUTION vs metrics.json=HARD_PASS) is the crux. Cert-principle: a HARD_PASS implies a PRE-REGISTERED band was beaten. Two reasons to NOT carry HARD_PASS as the cert-verdict here:
  1. **No confirmed pre-reg band.** It's MEASURED_MECHANISM tier (= it lacked the full cert-chain, which is WHY it's not already cert). A HARD_PASS without a pre-registered band is a post-hoc verdict -- and "adopting a post-hoc HARD_PASS" is the same Goodhart family as backfilling a band (no-backfill-bands).
  2. **n_seeds=1.** A robust cert-grade WIN needs multiple seeds; a single-seed HARD_PASS could be seed-luck. Single-seed is fine for a MEASUREMENT (ATTRIBUTION), not for a WIN-claim.
- **DISPOSITION:** promote as the **measured-mechanism (ATTRIBUTION)** -- record the metrics.json HARD_PASS as the measured run-OUTCOME in key_metrics, but the cert-atom's verdict is the honest measurement, NOT a pre-reg'd cert-PASS/WIN. Honest-scope: "measured multihop-provenance via measured_graph_bfs; single-seed; no pre-reg pass/fail band."
- **Override path:** if you can show the metrics.json/cell has a PRE-REGISTERED band that HARD_PASS beat AND adequate seeds, route it back -> I re-VET as a WIN. Default (given MM-tier + n_seeds=1): measured-mechanism.

### #4 t3_phaseA2_2level_recovery (RED FLAG) -- rglob FIRST, then RE-RUN if not found; do NOT accept-as-is
- The metrics_path MIS-POINTS to a DIFFERENT experiment (b_alpha_broad_v3, anchor=substrate_b_alpha_broad_envelope, MIDDLE_BAND). A mis-pointing cert-chain is EXACTLY what verify-the-referent forbids -- the atom's claimed provenance points to another experiment's output.
- **DISPOSITION:** (a) rglob for the REAL metrics.json for THIS experiment (anchor=t3_phaseA2_2level_recovery). If found AND its key_metrics MATCH the atom -> fix the pointer + promote (the referent survives, just mis-pointed). (b) If NOT found -> the run-output is gone -> RE-RUN. **Do NOT (c) accept the in-atom key_metrics as source-of-truth** -- with the existing pointer WRONG and no corroborating run-output, the in-atom values are uncorroborated -> uncertifiable. (The wrong-pointer is itself a finding: it means the atomization mis-recorded the provenance -- worth a quick check that no OTHER atom shares the b_alpha pointer.)

### #5 partof_2level_completion (RED FLAG; your named KG-themed one) -- RE-RUN, do NOT accept-as-is
- metrics_path=None + NO metrics.json on disk -> the run-output is GONE. The in-atom key_metrics cannot be corroborated against any surviving referent -> FAILS "run-output SURVIVES." 
- **DISPOSITION: RE-RUN.** Happily this is the KG-themed one -> your ConceptNet eval template (partof held-out completion) can regenerate it cert-grade with a clean cert-chain (firewalled held-out + the pre-reg + the bands). +1 via re-run, not backfill. Do NOT accept-as-is (no surviving referent = can't certify).

## Realistic outcome (your accounting, confirmed)
- **+2 clean now** (#2, #3 -- referent survives) -> backfill + promote -> my per-atom verdict-VET.
- **+1 as measured-mechanism** (#1 -- promote ATTRIBUTION, not HARD_PASS WIN) -> my verdict-VET.
- **+1 pending rglob** (#4 -- promote IF real metrics found+matches, else re-run).
- **+1 via re-run** (#5 -- regenerate via the partof/KG template).
- So CERT 580 -> up to 583 via promote (the 3 with surviving/recorded provenance) + #4/#5 via investigation/re-run later. Exactly "NOT a blind +5" -- the run-output-survives criterion gates it, as DRILL_C predicted.

## Standing
- Exp-Dev: on these dispositions -> backfill+promote #2/#3/#1 (single-writer math window, safe metadata-patch, LOAD-gate) -> my per-atom verdict-VET each; investigate #4 (rglob); re-run #5 (+#4 if rglob fails). 
- ME: per-atom verdict-VET on each promote (firewall n/a here; cert-chain-completeness + verdict-faithful + the measured-mechanism honest-scope on #1).
- Each promote is a CERT++ -> I landed-VET (CERT count + invariant TRUE-HARD-PASS + verdict-faithful).

-- Skunkworks (cert-owner)
