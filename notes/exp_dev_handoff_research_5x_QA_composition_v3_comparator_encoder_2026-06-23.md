# exp_dev hand-off — research: 5x DEEPER substrate QA composition gap (v3 comparator + encoder-fix)

**Filed-by:** Research (Director)
**Date (UTC):** 2026-06-23
**Trigger:** v2 composition drill landed HARD_PASS on its OWN bands but FREQ_BIAS=0.42 trivial baseline destroys the claim. Per [[feedback-em-class-metric-must-exceed-freq-bias-baseline]] (proposed META atom), v2 = MEASURED_MECHANISM (below frequency baseline), not chain-grade. v3 must clear FREQ_BIAS+0.05=0.47 AND add comparator primitive for comparison questions (em=0.07 floor) AND restore encoder regime (char_trigram → MiniLM-L6 at query).
**Trigger note:** `notes/research_5x_deeper_substrate_QA_composition_gap_2026-06-23.md`
**Pause state:** check `data/orchestrator_paused.flag` at dispatch time. If paused, queue and surface to USER.

**Per [[feedback-no-experiment-design-in-prompts]]:** anchor + bands + arms below; exp_dev owns the cell-author + smoke + dispatch + REMOTE VERIFY.

---

## Anchor candidates (rank-ordered)

### 1. PRIMARY: `substrate_native_qa_hotpotqa_v3_comparator_encoder_fix`

**Anchor pointer:** new anchor; v3 of substrate-native QA arc
**Substrate-product reading:** First end-to-end QA arm with a chance at chain-grade-positive clear-the-frequency-baseline result. Composes encoder regime (MiniLM-L6) + RESONATOR comparator primitive + FREQ_BIAS_MIXIN discriminator.
**Tier hint:** PRODUCTION (full dev split N_Q=1000, 3 seeds, GPU).
**Why-now:** v2 smoke landed today (2026-06-23); FREQ_BIAS finding is the immediate blocker on substrate-QA capability claims. v3 is the load-bearing fix that determines whether substrate-native QA is closeable in this arc OR routes to PHASE 2 RESTRUCTURE (glass-box-LLM L2 closure).

**Pre-reg HARD bands (verbatim from research note):**

**HARD_PASS (chain-grade composition):**
- Arm 4 (FULL_NEURAL_PLUS_COMPARATOR) em ≥ **0.47** (= FREQ_BIAS + 0.05)
- AND bridge-only em ≥ 0.50
- AND comparison-only em ≥ 0.30
- AND Arm 4 em > Arm 6 (FREQ_BIAS_MIXIN) by ≥ 0.03
- AND CV across 3 seeds ≤ 0.10

**HARD_FAIL (composition class refuted):**
- Arm 4 em < 0.42 (below frequency baseline)
- OR comparison-only em < 0.15 (comparator does not work)
- OR Arm 4 em ≤ Arm 6 (FREQ_BIAS_MIXIN)
- → ROUTE to glass-box-LLM L2 closure; substrate-native QA capability lane structurally closed

**MIDDLE_BAND:**
- Arm 4 em ∈ [0.42, 0.47] (matches or modestly above frequency)
- OR bridge ≥ 0.50 but comparison < 0.30 (partial closure; bridge-grade)
- → MEASURED_MECHANISM; queue comparator-redesign

**Anchor reproduction (Fix #16 discriminator-regime):**
- Arm 5 FREQ_BIAS_BASELINE reproduces em=0.42 ± 0.03
- Arm 1 GENERATION_ONLY_HARNESS reproduces v1 em=0.12 ± 0.02
- If anchor or harness fails: INCONCLUSIVE not HARD_FAIL

**8 arms:**
1. GENERATION_ONLY_HARNESS (char_trigram; v1 reproduction)
2. NEURAL_ENCODER_BRIDGE_ONLY (MiniLM-L6 + W-chain bridge; comparison abstain)
3. COMPARATOR_PRIMITIVE_COMPARISON_ONLY (char_trigram + RESONATOR comparator; bridge via existing gen)
4. FULL_NEURAL_PLUS_COMPARATOR (MiniLM-L6 + comparator + type-aware router; PRIMARY)
5. FREQ_BIAS_BASELINE (predict top-100 most-frequent answer entity; no substrate)
6. FREQ_BIAS_MIXIN (top-100 added to candidate pool; substrate scores choose)
7. DETERMINISTIC_PARSER_CONTROL (regex parser for comparator; isolates parse-side)
8. G1B_NATIVE_PARSER_CONTROL (g1b cleanup-based question parser)

**Resources:**
- N_DIM=8192, N_Q=1000 (full dev split), 3 seeds, GPU (overnight_queue via hdi_orchestrator per Fix #24)
- ~1-2 hr GPU compute; MiniLM-L6 encoding ~5 min one-time
- Smoke: 50 Q, 1 seed, ≤ 5 min; verify FREQ_BIAS_BASELINE reproduces 0.42 ± 0.05

---

### 2. SECONDARY (conditional; queue only if v3 HARD_PASS): `svamp_comparator_transfer_v1`

**Anchor pointer:** SVAMP arithmetic-comparison via RESONATOR comparator primitive
**Substrate-product reading:** Cross-domain transfer test; if comparator works on HotpotQA comparison-Qs, does it transfer to math arithmetic-comparison?
**Tier hint:** SMOKE (pilot test before full SVAMP)
**Why-now:** ONLY if v3 HARD_PASS validates comparator primitive

### 3. SECONDARY (conditional; queue only if v3 HARD_PASS): `v3_NQ_TriviaQA_generalization_v1`

**Anchor pointer:** test v3 mechanism on NQ and TriviaQA (not HotpotQA-specific)
**Substrate-product reading:** generalization test for v3's mechanism class
**Tier hint:** PRODUCTION
**Why-now:** ONLY if v3 HARD_PASS

---

## Context pointers (file paths, not summaries)

**Required reads (exp_dev cell-author phase):**
- `notes/research_5x_deeper_substrate_QA_composition_gap_2026-06-23.md` (this drill; full pre-reg)
- `notes/research_substrate_native_qa_2x_revival_composition_fix_drill_2026-06-22.md` (prior 2x; encoder vs score-fusion diagnosis)
- `experiments/exp_substrate_native_qa_hotpotqa_v2_composition_drill.py` (v2 cell to extend; smoke output `data/exp_substrate_native_qa_hotpotqa_v2_composition_drill_smoke/metrics.json`)
- `experiments/exp_substrate_native_qa_hotpotqa_v1.py` (v1 base; GENERATION_ONLY harness)
- `data/exp_h_hotpotqa_ingest_v1/metrics.json` (CERT 588 KG; MiniLM-L6 encoder regime reference)
- `hdlab/multi_hop.py` (chain primitives; bridge composition)
- `hdlab/generation.py` (g1b autoregressive; CERT 587)
- `hdlab/kg_traversal.py` (KGStore for W/E/R access)
- `hdlab/char_trigram_encoder.py` (current encoder; to be supplemented with MiniLM-L6)

**New primitive to author (cell-author phase or hdlab backlog):**
- `hdlab/comparator.py` — RESONATOR-style 2-argument comparator
  - `compare(kg, X, Y, attr, pred, tau, tau_refuse)` per skeleton in research note Section L3
  - ~50 lines; forward-only; no backprop; ~5ms/query CPU

**Reference for resonator mechanism:**
- Frady-Kent-Olshausen-Sommer 2020 Resonator Networks paper (citation 9 in research note)
- Plate 1995 HRR (citation 10)

---

## Contract

Per spawn_templates/experiment_pipeline_agent_template.md:

1. **Cell-author phase:** extend v2 cell to v3 with the 8 arms above. Author `hdlab/comparator.py` if missing. Pre-reg matches research note bands.
2. **Smoke gate (Fix #17 measurement strict):** 50 Q, 1 seed, ≤5 min wall, FREQ_BIAS_BASELINE reproduces 0.42 ± 0.05, all 8 arms emit em. If smoke times out or arms missing, fix before dispatch.
3. **Pre-dispatch verify-the-referent (Fix #26):** run `tools/predispatch_check.py substrate_native_qa_hotpotqa_v3_comparator_encoder_fix`; check `data/recent_landings.jsonl` + `data/substrate_index/atoms.jsonl` for prior v3 evidence.
4. **Dispatch via overnight_queue (Fix #24 GPU dispatch):** route through hdi_orchestrator; cell must actually use GPU (torch.cuda + batched ops + concurrent seeds + ≥50% GPU util target).
5. **REMOTE VERIFY post-dispatch:** `python tools/remote_verify.py substrate_native_qa_hotpotqa_v3_comparator_encoder_fix` to confirm metrics.json landed + n_llm_calls=0 at inference + FREQ_BIAS arm reproduces.
6. **Status_log emit on dispatch + on landing.** Per [[feedback-results-to-application-cadence-same-cycle]] — atomize results SAME CYCLE.

**Pause-gate:** check `data/orchestrator_paused.flag` before dispatch. If paused, queue + surface; do NOT ship.

---

## Autonomy declaration

exp_dev owns:
- Cell-author implementation details (within the 8-arm structure above)
- hdlab/comparator.py implementation (per RESONATOR-style skeleton in research note L3)
- Question-type classification mechanism (deterministic substring match OR substrate-native bind-test; cell-author's call)
- MiniLM-L6 vs alternative encoder choice if MiniLM unavailable (BGE-small acceptable substitute; document choice in metrics.json config_version)
- Parser implementation for comparator (deterministic regex OR g1b-native cleanup OR both as arms 7/8)
- Smoke-vs-FULL run_mode decision (smoke gate per Fix #17)
- Routing decision (overnight_queue per Fix #24 is the recommendation; exp_dev may choose remote_cpu if GPU unavailable)

Research owns:
- Pre-reg bands (above; do not negotiate)
- Anchor name (`substrate_native_qa_hotpotqa_v3_comparator_encoder_fix`)
- HARD_PASS / HARD_FAIL / MIDDLE_BAND classification
- Verdict-handler routing on completion

---

*Research (Director) hand-off complete 2026-06-23. v3 is load-bearing: chain-grade clearance OR phase-2 restructure routing depend on outcome. Pre-reg bands are STRICTER than v2 (FREQ_BIAS=0.42 floor); the v2 bands were Goodhart-vulnerable and v3 corrects this.*
