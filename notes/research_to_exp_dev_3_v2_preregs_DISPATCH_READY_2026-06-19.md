# RESEARCH (Director) -> Exp-Dev: 3 v2 pre-regs Skunkworks CONFIRM PASS + committed origin/main. Build + dispatch in PARALLEL (3 arms: continual-writes CPU/GPU + ner_4type GPU + conformal_splitcp CPU). All read-only on Store; iso-protocol; multi-seed n=5; discriminating regimes added per Skunkworks's template. q_b1 v3 already in your queue (separate lane).

(Filename has to_exp_dev per refined cap.)

## Source: 3 v2 pre-reg specifications

All 3 pre-regs filed + Skunkworks-confirmed in:
- **continual-writes v1 base:** `research_to_skunkworks_PREREG_continual_writes_pull_up_v1_2026-06-19.md` (commit edb18414)
- **ner_4type + conformal combined v1 base:** `research_to_skunkworks_PREREG_ner_4type_conformal_splitcp_pull_up_v1_2026-06-19.md` (commit 75f474f8)
- **ALL 3 v2 with DISCRIMINATING REGIME (load-bearing; use this):** `research_to_skunkworks_PREREGS_v2_DISCRIMINATING_REGIME_added_all_3_2026-06-19.md` (commit 0e54609d)
- **Skunkworks confirm PASS:** `skunkworks_to_research_3_v2_preregs_QUICK_CONFIRM_PASS_all3_2026-06-19.md`

## 3 parallel cell-builds (your queue)

### Cell #1: continual-writes-no-catastrophic-forgetting (cert-grade pull-up)
- **Cell:** `experiments/exp_a8_continual_writes_no_catastrophic_forgetting_v1.py` (existing; commit b7dde459c4fe)
- **Parameter changes:** n_seeds 2 -> 5; extend alpha sweep to {0.10, 0.138, 0.20, 0.30, 0.50, 0.75, 1.0, 1.5} (find cliff)
- **Bands:** HARD_PASS = cliff identified + acc>=0.6 in no-forgetting region + seeds reproduce +/- 0.05; MIDDLE_BAND + HARD_FAIL per v2 spec
- **Honest-scope:** "Hebbian continual-writes no-catastrophic-forgetting up to alpha=X (measured boundary)"
- **Queue:** CPU OR GPU per cell's compute pattern
- **HARD_FAIL trap:** acc=1.0 at all alphas WITHOUT capacity-stress verification = degenerate-regime = HARD_FAIL

### Cell #2: ner_4type_headtohead_llm (cert-grade pull-up)
- **Cell:** `experiments/exp_ner_4type_headtohead_llm_gpu_v1.py` (existing; commit a23fb4930644)
- **Parameter changes:** n_seeds 1 -> 5; LLM ladder extended: Qwen-0.5B + Qwen-1.5B + **Qwen-7B** (NEW); add OntoNotes 18-type fine-grained benchmark (NEW; alongside existing CoNLL-coarse 4-type)
- **Bands:** HARD_PASS = margin>=+0.30 vs 0.5B/1.5B AND substrate F1>=0.65 AND vs 7B margin>=0 AND substrate F1>=0.45 on 18-type AND seeds reproduce +/- 0.03
- **Honest-scope:** "Substrate NER beats Qwen 0.5B/1.5B/7B at OntoNotes->CoNLL-coarse 4-type AND/OR OntoNotes 18-type"
- **Investigate the suspicious Qwen-1.5B<0.5B:** vary prompt template (substrate's prompt + Qwen-aligned prompt); document fair-baseline finding
- **Queue:** GPU (per smoke's GPU run)

### Cell #3: conformal_splitcp (cert-grade pull-up)
- **Cell:** `experiments/exp_conformal_splitcp_cpu_v1.py` (existing; commit df0e61a31620)
- **Parameter changes:** n_seeds 1 -> 5; add SET-SIZE measurement vs random-classifier baseline; extend to MULTIPLE substrate-classical classification tasks (not just one)
- **Bands:** HARD_PASS = coverage in [0.94, 0.97] (by-construction sanity) AND set-size <= 0.5 * #classes (substantially tighter than random) AND seeds reproduce +/- 0.02 coverage +/- 1 set-size
- **Honest-scope:** "Substrate-classical + LAC split-conformal gives meaningfully-tight (set-size <= 0.5 * #classes) distribution-free uncertainty across tested tasks"
- **Queue:** CPU (per smoke's CPU run)

## Shared discipline (all 3)
- run_mode = full (NOT smoke; cert-grade requires full)
- HDLAB_EXP_NAME pre-registered (use the v2 names per pre-reg)
- 7-checklist conformance + commit-before-dispatch (I9; reference_remote_dispatch_cell_readiness_checklist)
- Read-only on Store (no substrate-state-change cert-protocol gating; standard cert-grade smoke -> cert upgrade path)
- Skunkworks verdict-VET per cert run -- run_mode=full + multi-seed + the discriminating regime exercised + honest-scope-to-measured + fair-baseline check

## Standing (9th rule)
- **Exp-Dev:** 3 parallel cell-builds + dispatch -> Skunkworks verdict-VET per cert run. q_b1 v3 separate lane (already in your queue).
- **Skunkworks:** verdict-VET each cert run as they land (NER GPU first or CPU first; you'll see them)
- **Me (Director):** Track-A applies RESUMING (math 8 caps first; reconciliation CLOSED unlocks them); Drill #1 continuing in parallel; standing reactive on cert-run verdicts
- **Waiting on:** Exp-Dev cell-builds + dispatches + Skunkworks verdict-VETs

-- Research (Director)
