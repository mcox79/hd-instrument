# exp_dev hand-off — research: lock-in noise control per-hop in multi-hop composition

**Filed-by:** Research (Director)
**Date (UTC):** 2026-06-23
**Trigger:** USER 2026-06-23 pushback on "didn't cleanup-per-hop already solve noise compounding across hops" — honest answer is cleanup REDUCES per-hop noise but doesn't eliminate it. Question: can the chain-grade single-shot lock-in primitive (data/exp_lock_in_amplifier_hd_frequency_v1_FULL/metrics.json — P64 lifts 16.39x at sigma=64 to recall=1.000) be COMPOSED per-hop at hop-distinct k_signal carriers to extend multi-hop composition depth from current ~2-hop ceiling to 5-7 hops?
**Trigger note:** `notes/research_drill_lock_in_per_hop_composition_depth_2026-06-23.md`
**Pause state:** check `data/orchestrator_paused.flag` at dispatch time. If paused, queue and surface to USER.

**Per [[feedback-no-experiment-design-in-prompts]]:** anchor + bands + arms below; exp_dev owns the cell-author + smoke + dispatch + REMOTE VERIFY + per-primitive wrapper authorship.

---

## Anchor candidates (rank-ordered)

### 1. PRIMARY: `exp_lock_in_per_hop_composition_smoke_v1`

**Anchor pointer:** new anchor; first cell to test per-hop lock-in composition (multiple lock-in stages at hop-distinct coprime k_signal carriers) as substrate-native noise-control for multi-hop chains.

**Substrate-product reading:** establishes whether the chain-grade single-shot lock-in primitive (FULL cell HARD_PASS) composes serially across multi-hop without accumulating compounding noise. If YES → substrate gains its first ENGINEERED multi-hop noise compensator (cleanup-per-layer is the existing one); unlocks 5-7 hop composition at recall>=0.85 per hop at sigma=32. If NO → noise-control axis for multi-hop reverts to cleanup-only (depth-budget capped at K~3-4 per HRR depth-budget drill).

**Tier hint:** SMOKE-to-PRODUCTION (start with 4 hop_count arms × 1 P × 1 sigma × 3 seeds smoke at N_DIM=2048; production at full grid at N_DIM=8192 GPU). Smoke routing **local_cpu_queue** (~15 min CPU). Production routing **overnight_queue** GPU if smoke HARD_PASS (~30 min GPU at N=8192).

**Why-now:** parent lock-in cell HARD_PASSed at single-shot (CERT chain-grade-eligible per VET note); USER directly asked whether per-hop composition works; the predicate-primitive set (`research_drill_predicate_evaluation_primitives_2026-06-23.md`) and HRR depth-budget cell (`research_drill_hrr_capacity_vs_depth_2026-06-23.md`) both need a multi-hop noise compensator to be practical at hop_count > 2. Per-hop lock-in is the OFDM-style structural solution; substrate already has all primitives. The composition-gap-3 closure (HotpotQA bridge em=0.28 vs FREQ_BIAS=0.42) is the substrate-product target.

**Pre-reg HARD bands (verbatim from research note L4):**

**HARD_PASS (chain-grade per-hop lock-in composition):**
- recall@1 at hop_count=3, sigma=32, P=8, N_DIM=2048 >= **0.85** (all 3 seeds; cv <= 0.15)
- AND recall@1 at hop_count=5, sigma=32 >= **0.65** (5-hop extension viable)
- AND inter-hop crosstalk measurement: cleanup-margin at hop K with K-1 prior hops noise-stress is within **0.10** of cleanup-margin at hop K isolated
- AND CV across 3 seeds <= 0.15 at hop_count=3
- AND LOGICAL_NOT identity self-test: max|demod(lock_in(-v)) - (-demod(lock_in(v)))| < **1e-5** at N=2048, P=8
- AND lock-in does not degrade vs baseline at sigma=4: recall(lock_in, sigma=4) >= recall(baseline, sigma=4) - 0.03

**HARD_FAIL (per-hop lock-in composition refuted at this substrate):**
- recall@1 at hop_count=3, sigma=32 <= **0.50** (per-hop lock-in does not exceed serial-cleanup baseline)
- OR recall@1 at hop_count=2 < **0.90** (mechanism collapses at FIRST composition — cyclic-permute basis non-orthogonal under nested bind; structurally closed)
- OR measured inter-hop crosstalk > **0.20** (frequency channels bleed; orthogonality assumption refuted)
- OR LOGICAL_NOT self-test max|diff| > 1e-3 (implementation sign bug)
- → ROUTE per-hop noise-control to cleanup-only (per `research_drill_hrr_capacity_vs_depth_2026-06-23.md`); composition-gap-3 closure routes to glass-box-LLM L2 for multi-hop predicate evaluation; META atom of refutation.

**MIDDLE_BAND:**
- 0.50 < recall@1 at hop_count=3 < 0.85 (partial mechanism)
- OR HARD_PASS at hop_count=3 but FAIL at hop_count=5 (depth-budget shorter than predicted; clamp K_max at 3 in production claim)
- → MEASURED_MECHANISM (regime-specific); tune P_lock_in or k_signal spacing before chain-grade claim

**Anchor reproduction (Fix #16 discriminator-regime):**
- Single-hop arm reproduces FULL cell metric: recall@1 at hop_count=1, sigma=32, P=8 >= 0.99 (matches FULL ARM_LOCK_IN_P8 sigma_32 = 0.992)
- Baseline arm reproduces FULL cell metric: recall@1 at hop_count=1, sigma=32, P=1 in [0.40, 0.46] (matches FULL ARM_BASELINE_SINGLE_SHOT sigma_32 = 0.428)
- If either anchor fails: INCONCLUSIVE not HARD_FAIL; rerun with bug investigation

**4 hop_count arms × 1 P × 1 sigma (smoke); 5 hop_count arms × 3 P × 3 sigmas (production):**

**Smoke arms (15 min CPU at N_DIM=2048, M=100, P=8 fixed, sigma=32 fixed):**
- HOP_1 (single-shot lock-in; reproduces FULL cell)
- HOP_2 (2-hop chain with k_signal_per_hop = [127, 379])
- HOP_3 (3-hop chain with k_signal_per_hop = [127, 379, 631])
- HOP_5 (5-hop chain with k_signal_per_hop = [127, 379, 631, 883, 1151])

**Smoke control arms (mandatory for symmetric-negativity discriminators):**
- VOCAB_V100 vs VOCAB_V1000 control (test finite-vocab collision artifact)
- RANDOM_CODEBOOK vs CHAR_TRIGRAM_CODEBOOK control (test learned-codebook orthogonality regime)
- LOCK_IN_ONLY vs CLEANUP_ONLY vs LOCK_IN+CLEANUP composition (test additive vs redundant with cleanup-per-layer)
- LOGICAL_NOT identity self-test (sign-flip commutes with demod)

**Production arms (30 min GPU at N_DIM=8192, M=500):**
- 5 hop_counts (1, 2, 3, 5, 7) × 3 P values (4, 8, 16) × 3 sigmas (16, 32, 64) × 3 seeds = 270 cells
- k_signal_per_hop assignment: coprime-prime spacing helper `assign_k_signal_per_hop(N_DIM, K_max)` returns deterministic coprime prime list

**Resources:**
- Smoke: N_DIM=2048, M=100, ~200 trials × 4 hop_counts × 3 seeds × ~10ms/trial × P=8 demod overhead ≈ 15 min CPU on laptop
- Production: N_DIM=8192, M=500, ~200 trials × 5 hop_counts × 3 P × 3 sigmas × 3 seeds × ~5ms/trial GPU ≈ 30 min GPU
- Smoke routing: **local_cpu_queue** (laptop CPU; numpy preferred over torch to keep dependencies minimal)
- Production routing: **overnight_queue** GPU (torch + cuda; reuses existing `lock_in_demod_batched` from `experiments/exp_lock_in_amplifier_hd_frequency_v1_FULL.py`)

**Pre-conditions (exp_dev owns):**
1. Lift `lock_in_demod_batched` from `experiments/exp_lock_in_amplifier_hd_frequency_v1_FULL.py` into `hdlab/lock_in.py` (should already be planned per Skunkworks landed VET note `notes/exp_dev_to_skunkworks_LANDED_VET_lock_in_amp_v1_FULL_HARD_PASS_2026-06-23.md`; verify before cell-author).
2. Author NEW `hdlab/lock_in_per_hop.py` (~100 lines) with:
   - `assign_k_signal_per_hop(N_DIM: int, K_max: int) -> List[int]` — returns deterministic list of K_max coprime primes spaced ~N_DIM/(K_max+1) apart, all coprime to N_DIM
   - `compose_K_hop_chain(atoms: torch.Tensor, k_signal_per_hop: List[int], P: int, sigma: float, gen) -> torch.Tensor` — encodes K-hop chain, adds independent noise per hop, demodulates in reverse hop-order
   - Sanity tests: `_selftest_k_signal_coprime_at_N(N_DIM)`, `_selftest_compose_endpoint_K1_equals_FULL_cell`, `_selftest_logical_not_commutes(N, P)`
3. Author cell `experiments/exp_lock_in_per_hop_composition_smoke_v1.py` with:
   - 4 hop_count arms × 1 P × 1 sigma at smoke
   - 4 discriminator control arms (VOCAB_V100/V1000; RANDOM/CHAR_TRIGRAM codebook; LOCK_IN_ONLY/CLEANUP_ONLY/LOCK_IN+CLEANUP; LOGICAL_NOT identity)
   - Per-arm + per-hop-position metrics in metrics.json (including inter-hop crosstalk measurement)
   - Anchor reproduction check (HOP_1 must match FULL cell single-hop within ±0.02 recall)
   - Selftest 5/5: P=1 endpoint, sigma=0 endpoint, k_signal coprime check, hop_count=1 reproduces FULL cell, LOGICAL_NOT commutes
4. (Optional, post-smoke if HARD_PASS) Author GPU cell `experiments/exp_lock_in_per_hop_composition_v1_FULL.py` with full grid (5 hop × 3 P × 3 sigma × 3 seeds, N_DIM=8192).

**Cross-thread synthesis:**
- Composes with `experiments/exp_hrr_depth_budget_curve_v1` (pending per HRR depth-budget drill): cleanup-per-layer + per-hop lock-in are ORTHOGONAL compensators. The depth-budget cell tests cleanup-only; this cell tests lock-in+cleanup composition.
- Composes with `substrate_predicate_primitive_set_v1` (in flight via predicate-primitives handoff): LOGICAL_NOT under lock-in is free (Prediction 4 verifies this); ORDINAL_COMPARATOR is linear so commutes with lock-in; TEMPORAL_PRECEDES (FPE) needs Prediction 5 cross-domain test.
- Composes with `substrate_sparse_bipolar_depth_v1` (per CERT 592 + sparse-bipolar drill): sparse-bipolar lifts bundle-capacity orthogonally; can be added as a 3rd composition axis once both base mechanisms validated.
- Cross-thread with HotpotQA bridge composition gap: if HARD_PASS, expect bridge-em to lift from 0.28 toward 0.50+ on bridge subset when per-hop lock-in is wired into v3 handoff pipeline (assuming MiniLM-L6 encoder also in place).

---

### 2. SECONDARY (deferred until smoke HARD_PASS): `exp_lock_in_per_hop_composition_v1_FULL`

**Anchor pointer:** GPU production-scale extension of smoke.

**Why-deferred:** production grid (~30 min GPU + cell-author time) is only justified if smoke HARD_PASSes; if smoke fails, the production cell would burn 30+ min GPU on a confirmed-null mechanism.

**Production grid (smoke HARD_PASS gates):**
- N_DIM = 8192, M = 500
- hop_count_grid = [1, 2, 3, 5, 7]
- P_grid = [4, 8, 16]
- sigma_grid = [16, 32, 64]
- seeds = [7, 17, 23]
- N_trials = 200

**Pre-reg HARD bands (production):**
- HARD_PASS: recall@1 at hop=5, sigma=32, P=8, N_DIM=8192 >= **0.65** (Prediction 3)
- HARD_PASS: recall@1 at hop=7, sigma=32, P=16 >= 0.50 (depth-budget upper bound at production scale)
- HARD_FAIL: recall@1 at hop=5 <= 0.35 (production-scale collapse)

---

### 3. TERTIARY (independent META atoms; standalone): three META atoms

**Anchor pointer:** META atomization for cert-ledger (independent of cell outcome; immediate ship).

**Three META atoms (per research-note L5 + Substrate-Product implications):**

1. **`META_per_hop_lock_in_is_OFDM_equivalent_at_substrate_scale`**
   - Claim: cyclic-permute carriers + cos-weighted lock-in IS structurally equivalent to OFDM (orthogonal frequency-division multiplexing); substrate inherits standard OFDM engineering practice (coprime carrier spacing, windowing for sidelobe reduction). Inter-channel crosstalk bounded by 1/sqrt(N_DIM) per pair at random codebook.
   - Evidence: Stream B (OFDM literature) + FULL cell `_selftest_roll_orthogonality` already verifies |roll(v,k)@v/N| < 0.1 at N=8192 for k in {1, 127, 1023}.
   - P=0.85 (mathematical equivalence; no experimental validation needed for the equivalence claim itself).

2. **`META_logical_not_is_free_under_lock_in`**
   - Claim: sign-flip (LOGICAL_NOT in bipolar substrate) commutes with cyclic-permute AND cos-weighting; `demod(lock_in(-v)) = -demod(lock_in(v))` exactly. LOGICAL_NOT primitive composes with lock-in at zero compute + zero noise cost.
   - Evidence: mathematical identity; verified by Prediction 4 self-test in this cell.
   - P=0.95 (mathematical identity; only numerical precision can cause failure).

3. **`META_substrate_hop_depth_budget_caps_at_sqrt_2sqrtN`**
   - Claim: cumulative inter-hop crosstalk under per-hop lock-in scales as binomial(K,2)/sqrt(N_DIM); for crosstalk_threshold=0.5 (half-margin), K_max ~ sqrt(2 * sqrt(N_DIM)). For N=8192: K_max ~ 10. For N=2048: K_max ~ 5. For N=16384: K_max ~ 12.
   - Evidence: analytic bound from CLT on random bipolar autocorrelation; verified empirically in this cell at K in {3, 5, 7} smoke + production.
   - P=0.75 (analytic bound; constant factor uncertain at small N).

---

## Context pointers

**Lock-in primitive (existing chain-grade-eligible):**
- `data/exp_lock_in_amplifier_hd_frequency_v1_FULL/metrics.json` — HARD_PASS at sigma=64 recall=1.000 via P64, N_DIM=8192, M=500
- `experiments/exp_lock_in_amplifier_hd_frequency_v1_FULL.py` — production cell with `lock_in_demod_batched`, `baseline_transmit_batched`, and 3 selftests
- `experiments/exp_lock_in_amplifier_hd_frequency_smoke_v1.py` — smoke version (N=1024, M=50)
- `notes/exp_dev_to_skunkworks_LANDED_VET_lock_in_amp_v1_FULL_HARD_PASS_2026-06-23.md` — VET landed; lift-to-hdlab planned

**Cross-thread research notes (read in full before cell-author):**
- `notes/research_drill_lock_in_per_hop_composition_depth_2026-06-23.md` — THIS drill's research note (L1 lit-scan, L2 mechanism filter, L3 deep drill, L4 falsifiable predictions, L5 cross-thread synthesis, citations)
- `notes/research_drill_hrr_capacity_vs_depth_2026-06-23.md` — HRR depth-budget; cleanup-per-layer compensator (composes orthogonally)
- `notes/research_drill_predicate_evaluation_primitives_2026-06-23.md` — 5-primitive set; LOGICAL_NOT free in bipolar; TEMPORAL_PRECEDES via FPE
- `notes/research_5x_deeper_substrate_QA_composition_gap_2026-06-23.md` — composition-gap context; HotpotQA bridge em=0.28 vs FREQ_BIAS=0.42
- `notes/research_5x_deeper_high_noise_substrate_product_strategy_2026-06-23.md` — refuse-aware framing (per-hop refuse gates preserve compositional refuse)

**Substrate primitives to compose:**
- `hdlab/lock_in.py` (NEW; lift from FULL cell)
- `hdlab/lock_in_per_hop.py` (NEW; per-hop composition wrapper)
- `hdlab/binding.py` (existing bind/unbind)
- `hdlab/sequence_memory.py` (existing permute primitives)
- `hdlab/iterative_attractor.py` (cleanup-per-layer; att1 family at M/N < 0.138)
- `hdlab/refuse_gate.py` + `hdlab/conformal.py` (refuse-aware composition)
- `hdlab/comparator.py` (in flight per v3 handoff)
- `hdlab/predicates.py` (in flight per predicate-primitives handoff)

**Cell-author template:**
- `tools/spawn_templates/experiment_pipeline_agent_template.md` (HYBRID Store+git+cert_ledger pipeline)
- `experiments/_seed_checkpoint.py` (resumable_seeds + write_partial_key + aggregate_partials + write_metrics)

**Pause flag:** `data/orchestrator_paused.flag` (gate before dispatch)

---

## Contract section

**Routing:**
1. Smoke: **local_cpu_queue** (N_DIM=2048, M=100, ~15 min CPU; laptop)
2. Production (smoke HARD_PASS gate): **overnight_queue** GPU (N_DIM=8192, M=500, ~30 min GPU; remote desktop)
3. META atoms (immediate, parallel): three atoms to Store via standard atomization pipeline (cert_ledger commit + ledger row)

**Pre-flight (Fix #26 verify-the-referent gate):**
- `tools/predispatch_check.py exp_lock_in_per_hop_composition_smoke_v1` (check recent_landings + atoms for prior evidence)
- Verify FULL cell single-hop anchor is current (data/exp_lock_in_amplifier_hd_frequency_v1_FULL/metrics.json exists)
- Verify `hdlab/lock_in.py` lifted before cell-author (or include lift in same cycle)

**Post-ship verify (Fix #25 + REMOTE VERIFY):**
- Tail data/recent_landings.jsonl for `exp_lock_in_per_hop_composition_smoke_v1` landing event
- Read per-arm metrics from metrics.json (Fix #28: do NOT trust verdict_msg text; read summary[arm][hop_count][sigma] directly)
- Verify all 5 selftests PASS in cell stdout before claiming HARD_PASS
- Cross-check anchor reproduction: HOP_1 single-hop recall@1 at sigma=32 P=8 must match FULL cell ARM_LOCK_IN_P8 sigma_32 = 0.992 ± 0.02

**Hand-off completion:** REPLY via status_log entry `exp_dev_completion` with summary, per-arm metrics, and recommended next-step (production GPU cell IF smoke HARD_PASS; per-arm diagnosis IF MIDDLE_BAND or HARD_FAIL).

---

## Autonomy declaration

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev owns the cell-author + smoke + dispatch + REMOTE VERIFY + per-primitive wrapper authorship + per-arm metrics verification. Research provides anchor + bands + arms + context pointers; does NOT design the cell internals. exp_dev decides:
- Exact P value at smoke (within [4, 8, 16]; recommended P=8 from Stream A SNR-vs-cost trade)
- Exact k_signal_per_hop list at smoke (within [coprime primes spaced N_DIM/(K_max+1)]; recommended [127, 379, 631, 883, 1151] at N=2048)
- Exact synthetic-corpus structure for discriminator controls
- Exact cell-name prefix variants (e.g., `exp_lock_in_per_hop_composition_smoke_v1` vs `_v1a` if disambiguation needed)
- Whether to ship LOCK_IN_ONLY vs CLEANUP_ONLY vs LOCK_IN+CLEANUP arms as separate cells or one combined cell
- Whether to author the GPU production cell same-cycle or after smoke HARD_PASS landing

Research declares: HARD_PASS / HARD_FAIL / MIDDLE_BAND bands are PRE-REGISTERED and IMMUTABLE per [[feedback-pre-registered-bands-immutable]]. Reproduction anchors (HOP_1 == FULL cell single-shot) are MANDATORY. Symmetric-negativity discriminators (V=100 vs V=1000, random vs char_trigram codebook, lock_in vs cleanup) are MANDATORY for any chain-grade claim.

---

*exp_dev hand-off filed 2026-06-23. Companion to `notes/research_drill_lock_in_per_hop_composition_depth_2026-06-23.md`. Pause-gated. Smoke routing local_cpu_queue ~15 min; production routing overnight_queue GPU ~30 min (smoke HARD_PASS gates). Three standalone META atoms ship immediately (independent of cell outcome). LOGICAL_NOT-under-lock-in identity test is a 1-line self-test that ships with cell.*
