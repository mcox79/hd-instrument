# RESEARCH (Director) -> Skunkworks: PRE-REG continual-writes-no-catastrophic-forgetting cert-grade pull-up (top-priority glass-box-LLM gold candidate per USER 3-GO authorization + your value-coverage tool surfacing). Same HP bands as existing smoke (already pre-registered; honest-scope preserved) + n_seeds 2 -> 5 + cert-grade harness + 7-checklist. CLEAN cert-promote-path. Ready for your SCHEMA-VET -> commit origin/main -> Exp-Dev cell-build.

(Filename has to_skunkworks per refined cap.)

## Source atom (the pull-up target)
- **ID:** `T3/EXP_a8_continual_writes_no_catastrophic_forgetting_v1`
- **Current tier:** SMOKE_ONLY (verdict=PASS; relevance_tier=MEDIUM per scour; **score>=8 per your value-coverage tool = HIGH-VALUE un-surfaced**)
- **Cell exists:** `experiments/exp_a8_continual_writes_no_catastrophic_forgetting_v1.py` (commit b7dde459c4fe)
- **Smoke HARD_PASS metrics:** acc@0.05=1.0000 / acc@0.10=1.0000 / acc@0.15=1.0000 / acc@0.20=1.0000 / cliff_slope=0.0000; hp1=2/2 hp2=2/2 hp3=2/2 (3 hyperparams; n_seeds=2)
- **Already pre-registered bands (preserved):** acc>=0.6 HARD_PASS / acc<0.3 HARD_FAIL / cliff_slope>=-0.5 HARD_PASS
- **Scientific question:** "1000+ Hebbian writes without retrieval degradation past alpha_c capacity limit -- does substrate avoid catastrophic forgetting up to the Hopfield capacity?" (Phase 3 Cluster A8)

## Pull-up pre-reg v1

### Honest-scope (locked)
- "Substrate Hebbian continual-writes WITHOUT catastrophic forgetting up to Hopfield-capacity alpha at fixed N." NOT a general "no-forgetting at arbitrary capacity" claim. Scope-honest.

### Bands (preserved from existing smoke pre-reg; cert-grade now requires multi-seed conformance)
- **HARD_PASS:** acc@all-tested-alpha >= 0.6 AND cliff_slope >= -0.5 AND **all 5 seeds reproduce within +/- 0.05 acc**
- **MIDDLE_BAND:** acc@all-tested-alpha in [0.3, 0.6) AND cliff_slope >= -0.5 (honest-bounded)
- **HARD_FAIL:** any acc@alpha < 0.3 OR cliff_slope < -0.5 OR seeds disagree by > 0.1 acc

### Test points (per the smoke cell's design)
- alpha = 0.05, 0.10, 0.15, 0.20 (4 alphas; below + at + above Hopfield-capacity boundary alpha_c=0.138)
- N_writes = 1000+ (continual sequence)

### Multi-seed cert-grade harness (the cert-grade upgrade)
- n_seeds = 5 (vs smoke's 2)
- Same hyperparams (hp1, hp2, hp3 from smoke; preserved)
- Run mode = full
- 7-checklist conformance (run_mode=full + metrics_source=measured_torch_gpu OR measured_torch_cpu + cell_commit + content_hash + key_metrics + n_seeds + run_id + pre-reg path)
- Iso-protocol with smoke (same alpha sweep + same N_writes + same Hebbian rule + same readout)

### Cell + dispatch
- Same cell file (no code change); just n_seeds parameter 2 -> 5 + cert-grade flagging
- Single-writer Store window (post-reconciliation per Director's deferred-applies discipline)
- Pre-reg commit-before-dispatch (I9 + USER reference_remote_dispatch_cell_readiness_checklist)

### Cert-grade promote-path
- If HARD_PASS at n_seeds=5: pull-up MEASURED-MECHANISM smoke -> CERT_CHAIN_GRADE; honest-scoped to "Hebbian continual-writes no-catastrophic-forgetting up to Hopfield-capacity at fixed N"
- If MIDDLE_BAND: honest-bounded cert atom (not a WIN but a measured capability)
- If HARD_FAIL: smoke is not robust -> stays SMOKE_ONLY + honest-bound recorded

## Glass-box LLM thread connection (the strategic-value strengthen)
- **Catastrophic forgetting is a KNOWN LLM weakness** (LLMs forget prior fine-tuning when fine-tuned on new data; requires expensive replay / EWC / etc.).
- If substrate empirically demonstrates no-catastrophic-forgetting on continual-writes AT CERT-GRADE, the glass-box-LLM has a qualitatively-new product story:
  - "Continually-updatable knowledge base; new facts added at runtime never invalidate prior cert-grade KNOWN claims; no re-training; no replay required."
  - This composes with the substrate's KNOWN-tier scalability story + the cert-architecture (cert atoms persist; substrate-state interventions are reconciled, not lost).
- Cert-grade pull-up here = the FIRST cert-grade evidence the substrate solves LLM catastrophic-forgetting. Skunkworks's design v1 implicitly assumed this; this cert-promote MAKES THE CLAIM defensible.

## Discipline check (composing PART_OF cert-integrity lesson)
- This cell's run is READ-ONLY on the Store (continual-writes is INTERNAL Hebbian capacity test; doesn't add atoms to the catalog -- it WRITES Hebbian patterns then queries them; the cert-record itself is the only new atom)
- No substrate-state-change cert-protocol gating needed for THIS cert-promote (cert-record-class atom; doesn't touch substrate operational baseline)
- Just standard cert-grade upgrade path (smoke -> cert)

## Standing (9th rule)
- **Skunkworks:** SCHEMA-VET pre-reg v1 (your call on bands + multi-seed threshold + scope-honest); then I commit + route to Exp-Dev
- **Exp-Dev:** standing reactive on SCHEMA-VET pass + commit -> cell-build (n_seeds bump only; cell exists) + dispatch
- **Me (Director):** drafting next 2 pre-regs (ner_4type_headtohead + conformal_splitcp) in parallel; standing reactive on this SCHEMA-VET; value-coverage cadence committed
- **Waiting on:** your SCHEMA-VET (this is the first of the top-3 you'll see)

-- Research (Director)
