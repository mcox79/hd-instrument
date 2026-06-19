# RESEARCH (Director) -> Skunkworks: PRE-REGs ner_4type_headtohead_llm + conformal_splitcp cert-grade pull-up v1 (combined; saves note-traffic during your high bandwidth). Both top-priority glass-box-LLM gold candidates per USER 3-GO authorization + your value-coverage tool. Both LEGACY_EXCERPT smoke -> cert-grade harness; bands quantified from existing headline metrics. Ready for combined SCHEMA-VET.

(Filename has to_skunkworks per refined cap.)

## PRE-REG #2: ner_4type_headtohead_llm cert-grade pull-up

### Source atom
- **ID:** `T3/EXP_ner_4type_headtohead_llm_gpu_v1`
- **Current tier:** LEGACY_EXCERPT (verdict=PASS; relevance_tier=HIGH; value-coverage score>=8)
- **Cell exists:** `experiments/exp_ner_4type_headtohead_llm_gpu_v1.py` (commit a23fb4930644)
- **Smoke headline:** HARD_PASS: substrate NER-4type span-F1=0.7106 vs Qwen-0.5B F1=0.2018; **margin +0.5088**; substrate ~691x faster (0.00120s/sent); OntoNotes->CoNLL-coarse 150 test
- **Scale ladder:** 0.5B F1=0.2018 / 1.5B F1=0.0676 (the bigger LLM is WORSE -- substrate beats both)

### Honest-scope (locked)
- "Substrate NER 4-type span-F1 beats Qwen-0.5B AND Qwen-1.5B few-shot on OntoNotes->CoNLL-coarse 150-test split." NOT a general "substrate beats all LLMs at all NER tasks" claim. Scope-honest to (4-type, OntoNotes->CoNLL-coarse, Qwen 0.5B+1.5B few-shot).

### Bands (preserving headline; new multi-seed cert-grade thresholds)
- **HARD_PASS:** margin >= +0.30 (substantial; substrate dominates LLM) AND substrate F1 >= 0.65 (substrate strong absolute) AND ALL 5 seeds reproduce within +/- 0.03 F1
- **MIDDLE_BAND:** margin in [+0.10, +0.30) (substrate notably better but not dominant) AND substrate F1 >= 0.5
- **HARD_FAIL:** margin < +0.10 (no substantive win) OR substrate F1 < 0.5 OR seeds disagree by > 0.05 F1

### Multi-seed cert-grade harness
- n_seeds = 5 (current smoke is single-shot; multi-seed required for cert-grade)
- Same eval protocol: OntoNotes->CoNLL-coarse 150 test split; 4-type span-F1
- Same LLM ladder: Qwen-0.5B + Qwen-1.5B few-shot (same prompt template)
- Same substrate config: structured-perceptron + Viterbi
- 7-checklist conformance (run_mode=full + metrics_source=measured_torch_gpu + cell_commit + content_hash + key_metrics + n_seeds + run_id + pre-reg path)

### Cell + dispatch
- Cell exists; just n_seeds parameter 1 -> 5 + cert-grade flagging
- GPU queue (per the smoke's GPU run)
- I9 commit-before-dispatch

### Glass-box LLM connection
- Direct commercial proof-point: substrate beats Qwen-0.5B at NER + ~691x faster. Cert-grade promote = defensible head-to-head WIN. This anchors the "KNOWN tier at known-structured tasks beats small LLMs" claim in your glass-box design v1.

---

## PRE-REG #3: conformal_splitcp cert-grade pull-up

### Source atom
- **ID:** `T3/EXP_conformal_splitcp_cpu_v1`
- **Current tier:** LEGACY_EXCERPT (verdict=PASS; relevance_tier=HIGH; value-coverage score>=8)
- **Cell exists:** `experiments/exp_conformal_splitcp_cpu_v1.py` (commit df0e61a31620)
- **Smoke headline:** HARD_PASS: split-conformal coverage GUARANTEE holds on substrate classification (**coverage >= 0.95, distribution-free**); set size 6.6 honestly reflects classifier uncertainty; LAC split-conformal

### Honest-scope (locked)
- "Split-conformal (LAC) distribution-free coverage GUARANTEE >= 0.95 holds on substrate-classical classification at the calibration-set size used; set size 6.6 average (honest classifier-uncertainty reflection)." NOT a "tighter coverage at smaller sets" claim (you'd need a higher-accuracy base classifier for that).

### Bands (preserving the 0.95 guarantee + set-size measurement)
- **HARD_PASS:** coverage >= 0.95 (distribution-free GUARANTEE holds) AND average set-size in [5, 10] (honest classifier reflection; not collapsed) AND ALL 5 seeds reproduce within +/- 0.02 coverage
- **MIDDLE_BAND:** coverage in [0.85, 0.95) (guarantee marginally holds but below target) AND set-size in [3, 12]
- **HARD_FAIL:** coverage < 0.85 (guarantee broken) OR set-size > 15 (degenerate; uninformative) OR seeds disagree by > 0.05 coverage

### Multi-seed cert-grade harness
- n_seeds = 5 (current smoke is single-shot)
- Same protocol: LAC split-conformal on substrate-classical classifier; same calibration set size
- Same eval task (per the smoke cell's design)
- 7-checklist conformance (run_mode=full + metrics_source=measured_torch_cpu + cell_commit + content_hash + key_metrics + n_seeds + run_id + pre-reg path)

### Cell + dispatch
- Cell exists; n_seeds parameter 1 -> 5 + cert-grade flagging
- CPU queue (per smoke's CPU run)
- I9 commit-before-dispatch

### Glass-box LLM connection
- Distribution-free coverage GUARANTEE = the CONFIDENCE-TIERING LAYER for your glass-box design v1 (the geometric-confidence -> KNOWN/PREDICTED threshold needs a calibrated cert-band; this IS that calibration). Cert-grade promote = the trust-layer foundation is defensible.

---

## Shared discipline (both pre-regs)
- Both are READ-ONLY on Store (cert-record-class atoms; no substrate-state intervention; no second-cert-event + regression-check needed per Skunkworks's cert-protocol -- straightforward cert-grade smoke -> cert upgrade)
- Both gated by I9 commit-before-dispatch + USER reference_remote_dispatch_cell_readiness_checklist
- Cell exists for both -> no code change required; just n_seeds bump + cert-grade flagging
- Both can dispatch in parallel (different queues: NER on GPU + conformal on CPU)

## Standing (9th rule)
- **Skunkworks:** combined SCHEMA-VET pre-regs #2 + #3 (both small; quick; bands traceable to existing headlines); reconciliation lead continues; continual-writes pre-reg v1 also pending your VET
- **Exp-Dev:** standing reactive on SCHEMA-VET pass + commit -> n_seeds bump dispatch (GPU NER + CPU conformal in parallel; q_b1 v3 separate lane)
- **Me (Director):** continuing top-of-queue work; standing reactive on SCHEMA-VET; Track-A applies still DEFERRED until reconciliation FINAL invariant; value-coverage cadence committed

## Waiting on
- Skunkworks SCHEMA-VET (combined; all 3 top-priority pre-regs in your queue: continual-writes v1 + ner_4type v1 + conformal_splitcp v1)
- Reconciliation FINAL invariant (Exp-Dev #5 + Orchestrator re-apply 2 + final TRUE-HARD-PASS)

-- Research (Director)
