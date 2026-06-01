# exp_dev hand-off: Bet N — self-supervised atom discovery (Tier-1 substrate-augmentation, third-axis triad)

**Filed:** 2026-05-25 by Research sub-agent (depth drill per orchestrator strategic intent — pre-positioning a Tier-1 probe for ship when SSH-to-remote returns).
**Status:** READY for exp_dev pickup. Companion to `notes/research_bet_n_design_readiness_2026-05-25.md`.
**Routing schema:** Schema A (single anchor with multi-arm cells). Two arms: ARM_A_LEARNED (competitive-WTA atoms) + ARM_B_SIMCLR_DENSE (negative control, no sparsity).
**Dependencies:** NONE on alpha_c audit gate (Bet N operates on atom basis, orthogonal to MoE rebuild's W-layer). Can ship in parallel with MoE rebuild.
**Discipline:** per [[feedback-envelope-expansion-fail-bands]] all bands pre-registered before run; per [[feedback-no-experiment-design-in-prompts]] exp_dev OWNS the final anchor naming, seed counts, queue-tier selection, ETA estimate, hyperparameter sweeps, and any wallclock-driven scope adjustments — this handoff specifies the WHAT and WHY, exp_dev specifies the HOW.

---

## WHAT (task statement)

Build and ship the first empirical test of "Bet N" — whether substrate-internal atoms discovered via competitive-WTA self-supervised learning on byte-n-gram pairs (a) match the substrate's hand-crafted PPMI atom basis in associative-memory capacity, and (b) demonstrably specialize across domains (Python source code vs English text vs random bytes corpora).

Two arms:
- **ARM_A_LEARNED** — Cao 2023 style competitive-WTA atom discovery + downstream substrate binding/cleanup at matched (N, M_stored, k_active).
- **ARM_B_SIMCLR_DENSE** — InfoNCE contrastive learning without sparsity constraint; same downstream evaluation. Negative control predicted to TANK; confirms sparsity gate is load-bearing.

---

## WHY (live context pointers, not summaries)

- **Self-discovered Bet N framing:** see `notes/research_bet_n_design_readiness_2026-05-25.md` Section 0 — Bet N is the third Tier-1 path (atom-layer) orthogonal to MoE-rebuild (expert-layer) and SSM-HiPPO (depth-layer). v200 cap_map row names the triad but does not re-define Bet N; this drill ratifies "self-supervised atom discovery" as the operative framing.
- **Literature precedent:** Cao et al. 2023 "Competitive learning to generate sparse representations for associative memory" (Neural Networks 168, arXiv:2301.02196) — competitive-WTA codes come close to optimal-random-code capacity at Willshaw log-sparse regime. Substrate operates at this regime (Frady-Sommer ~350K bundle headroom per cap_map v2). Direct precedent.
- **Codebook-collapse anti-pattern:** SimVQ 2024 (arXiv:2411.02038), FSQ 2023, NS-VQ 2024, Beyond-Stationarity 2026 (arXiv:2602.18896) all show naive learned codebooks collapse without entropy regularization. P1 utilization-gate pre-reg is the structural defense.
- **Substrate alpha_c headroom:** see `notes/research_substrate_alpha_c_anomaly_2026-05-24.md` — substrate at alpha_c=0.39 vs textbook BSC [0.08, 0.25] gives learned atoms 30-60% per-item capacity safety margin before falling below PPMI baseline.
- **Cross-pollination with MoE drill:** `notes/research_mesoscopic_transport_moe_2026-05-25.md` provides `compute_dmpk_signature` SVD spectrum block — reuse it in Bet N as a free mechanism-level confirmation atop the coarser P1 utilization gate.
- **Triad context:** MoE rebuild already drilled today (mesoscopic-xtalk diagnostic in flight); SSM-HiPPO has R-PRIME-5 placeholder + 15-angle triage A1 (script needs redesign per orchestrator strategic intent); Bet N had not been drilled today — this handoff closes that gap.
- **15-angle triage A3 entry:** `notes/research_15_angles_triage_2026-05-24.md` line ~33-39 — flagged "NOT in current queue", "no script on disk", P=0.40 BEFORE this depth drill. This handoff is the dispatch into A3.
- **Pause state:** check `data/orchestrator_paused.flag` BEFORE shipping. If paused, exp_dev refuses (defense-in-depth). If active, ship via standard queue_add.

---

## CONTRACT (deliverable shape)

### Pre-registered three-verdict band matrix (HARD constraints — exp_dev MUST honor)

**P1 — Sparsity-regime soundness (gate; computed BEFORE downstream metrics):**
- HARD-PASS: `effective_utilization := H(usage_dist) / log(K) >= 0.70` AND `mean(atom_sparsity_per_input) in [0.8 · k_active, 1.2 · k_active]`
- HARD-FAIL: `effective_utilization < 0.30` OR `mean(atom_sparsity_per_input) outside [0.5 · k_active, 2.0 · k_active]`
- MIDDLE: in between bands

**P2 — Associative-memory capacity vs PPMI baseline (load-bearing comparison):**
- Setup: `N=4096, M_stored ∈ {500, 1000, 2000, 4000}, k_active=12, eval-pairs from held-out byte-n-gram split`
- Metric: `cleanup_acc_ratio(M=2000) := cleanup_acc_LEARNED(M=2000) / cleanup_acc_PPMI(M=2000)` at the M=2000 row (matches existing MoE smoke setup; M=2000 is the most-tested operating point in current pipeline)
- HARD-PASS: `cleanup_acc_ratio(M=2000) >= 1.10`
- HARD-FAIL: `cleanup_acc_ratio(M=2000) <= 0.80`
- MIDDLE: `cleanup_acc_ratio(M=2000) in (0.80, 1.10)`

**P3 — Substrate-product distinctiveness (corpus-adaptive claim):**
- Setup: train atoms on three corpora separately — `corpus_PY` (Python source), `corpus_EN` (English text), `corpus_RND` (random bytes baseline)
- Metric A: `mean_pairwise_cosine_distance(centroids(Phi_PY), centroids(Phi_EN), centroids(Phi_RND))`
- Metric B: `cross_corpus_retrieval_gap := min over (c1, c2): cleanup_acc(corpus_c1_eval, atoms_c1) - cleanup_acc(corpus_c1_eval, atoms_c2)` for c1 ≠ c2
- HARD-PASS: `cosine_distance >= 0.85` AND `cross_corpus_retrieval_gap >= 0.05`
- HARD-FAIL: `cosine_distance < 0.40`
- MIDDLE: intermediate or one-of-two thresholds met

### Compound row-state decision matrix (Research-prescribed; verdict_handler follows on the verdict)

| P1 | P2 | P3 | Row-state move | Portfolio count change |
|---|---|---|---|---|
| HARD-PASS | HARD-PASS | HARD-PASS | 🔬 → ✅ Tier-1 promotion (NEW row "self-supervised atom discovery") | 13 → 14 demonstrated |
| HARD-PASS | HARD-PASS | MIDDLE | 🔬 → 🟢 PARTIAL "atom discovery with caveats" | 13 + new 🟢 row |
| HARD-PASS | MIDDLE | * | 🔬 → 🟢 PARTIAL "atom-mode flexibility" (Tier-2) | 13 + new 🟢 row |
| HARD-PASS | HARD-FAIL | * | 🔬 → ❌ PROVISIONAL Bet N CLOSED-at-substrate-domain (5 rescue sketches MANDATORY per [[feedback-rehabilitation-after-rejection]]) | 13 + new ❌ row |
| HARD-FAIL | * | * | INSTRUMENTATION_FAIL — rescue via SimVQ-style entropy regularizer; re-queue (NOT a Bet N closure verdict) | no row change |

### Verdict tag taxonomy (exp_dev emits these in verdict_msg)

- `BET_N_TIER1_PROMOTION` — all three P1/P2/P3 HARD-PASS
- `BET_N_PARTIAL_TIER2` — P1+P2 HARD-PASS but P3 MIDDLE
- `BET_N_ATOM_MODE_FLEXIBILITY` — P1 HARD-PASS, P2 MIDDLE
- `BET_N_CLOSED_AT_DOMAIN` — P1 HARD-PASS, P2 HARD-FAIL (filing 5 rescue sketches REQUIRED)
- `BET_N_INSTRUMENTATION_FAIL` — P1 HARD-FAIL (mode-collapse; not Bet N closure)
- `BET_N_MIDDLE_BAND` — any other combination

Per-cell metrics must include the 5 named bands `effective_utilization, atom_sparsity_avg, cleanup_acc_ratio_at_M2000, cosine_distance_centroids, cross_corpus_retrieval_gap` to enable honest re-read per [[feedback-verdict-msg-honest-reread]].

### Discipline constraints

- ASCII-only in `print()` and `verdict_msg` per [[feedback-ascii-only-in-scripts]] — Windows cp1252 will crash on emoji/em-dash. Pre-flight grep `🔬|🟢|🟡|✅|❌|—|–` before queueing.
- Self-test cells per [[feedback-strategy-spec-formula-selftests]]: include at least one (input → expected output) pair for `compute_effective_utilization`, `competitive_wta_step`, and `cleanup_acc_ratio` BEFORE main loop. The L1 lock added at v203 (end-to-end smoke against production code path) REQUIRES the first cell run against the production substrate API — do NOT defer to spec-only validation.
- Decision-log append via `tools/orchestrator/append_decision_log.py` per [[feedback-decision-log-eol-handling]].
- ASCII bracketing in routing-file Schema A header (see existing handoff samples).
- For You status_log entry on completion (importance=HIGH if any HARD-PASS or HARD-FAIL; MEDIUM if MIDDLE-only; LOW if INSTRUMENTATION_FAIL with clean recovery path).

### Pre-flight verification (per [[feedback-ship-before-dependency-verified]])

Before queue_add.sh:
1. Confirm `data/byte_ngram_pairs.{pkl,npy}` (or equivalent prepared corpus pairs) EXISTS in the data dir; if not, generate from existing wave14 corpus prep scripts FIRST.
2. Confirm PPMI baseline atoms `data/atoms_ppmi_N4096.{pkl,npy}` (or equivalent) EXISTS; if not, regenerate before ship.
3. Confirm anchor name does not collide with completed entries via `python tools/orchestrator/state_check.py | grep -i bet_n` per [[feedback-ship-name-collision]].
4. Post-ship REMOTE VERIFY on `queue.json` (queue depth incremented; anchor present by name).

---

## AUTONOMY DECLARATION

**exp_dev OWNS:**
- Final anchor name (suggested family: `wave14e_bet_n_*` — 15-angle triage A3 reborn; exp_dev picks variant)
- Final seed count (Research recommends ≥ 5; exp_dev decides based on wallclock budget)
- Final queue-tier choice (Research recommends remote_cpu_queue at 30-90 min per arm × 2 arms = ≤ 3h; exp_dev may split arms across queues or escalate to overnight_queue if necessary)
- Final ETA estimate (Research provides 30-90 min CPU per arm as upper-bound; exp_dev refines after smoke)
- Hyperparameter SWEEP design (suggested defaults: K=128, k_active=12, eta=0.01, rho=0.05, n_epochs=5; exp_dev may sweep K ∈ {64, 128, 256} OR k_active ∈ {8, 12, 16, 24} as a single-axis sweep if smoke clears)
- WTA-bias schedule (Research suggests winner-fatigue activity-dependent bias per Cao 2023; exp_dev decides on specific implementation — Cao uses `bias += rho · (mask - k/K)`; SimVQ uses entropy-regularizer; either is acceptable)
- Smoke-mode parameters (N=512 reasonable starting smoke; exp_dev may shrink further for first-cell sanity)
- Whether to ship ARM_B_SIMCLR_DENSE in same anchor or separate anchor (single-anchor multi-arm is preferred for fair comparison; exp_dev decides)
- Whether to include the optional Dorokhov-SVD spectrum band (Research recommends YES — free additional mechanism-level confirmation; cost ~3% wallclock; reuses `compute_dmpk_signature` from MoE handoff; but exp_dev owns the decision)
- Whether to add cleanup_acc evaluation at additional M_stored points beyond {500, 1000, 2000, 4000} if smoke wallclock budget allows
- Final verdict-tag mapping if compound results land in an edge case the matrix above does not cover (e.g., P1 PASS + P2 HARD-PASS + P3 HARD-FAIL — Research-suggested tag would be `BET_N_PARTIAL_NO_CORPUS_ADAPT`; exp_dev confirms or revises)

**Research SPECIFIES (HARD — exp_dev MUST honor):**
- Three-verdict band structure P1/P2/P3 with bands as stated
- Compound row-state decision matrix
- ASCII-only / self-test / decision-log discipline citations
- Mode-collapse defense (some form of WTA activity-bias or entropy-regularizer) is REQUIRED; bare-Hebbian-without-anti-collapse is a known failure mode
- ARM_B_SIMCLR_DENSE negative control (sparsity-gate load-bearing test)
- Effective_utilization computed BEFORE downstream metrics (P1 is the gate)

---

## Sketch — minimal viable script structure (250 lines target)

```python
# experiments/exp_wave14e_bet_n_<exp_dev_picks_name>.py
# ASCII-only print() and verdict_msg.
# Per [[feedback-ascii-only-in-scripts]] do NOT include emoji or em-dash.

import torch, json, sys, math
from pathlib import Path

# --- self-test cells (per L1 lock) ---
def selftest_effective_utilization():
    # uniform usage over K=4 should give H/log K = 1.0
    usage = torch.tensor([0.25, 0.25, 0.25, 0.25])
    assert abs(compute_effective_utilization(usage) - 1.0) < 1e-6
    # mode-collapsed (one bin) should give 0.0
    usage = torch.tensor([1.0, 0.0, 0.0, 0.0])
    assert abs(compute_effective_utilization(usage)) < 1e-6

def selftest_competitive_wta_step():
    # 2-codeword codebook, k=1, deterministic input -> winner should be argmax
    # ... (exp_dev fills in 5-line sanity check)
    pass

def selftest_cleanup_acc_ratio():
    # identical atoms (learned = ppmi) should give ratio = 1.0 ± 1e-3
    pass

# --- core mechanism (Cao 2023 style with WTA activity-bias) ---
def competitive_wta_atom_discovery(byte_pairs, N, K, k_active, n_epochs, eta, rho, seed):
    # bipolar init, WTA + Hebbian outer-product, winner-fatigue anti-collapse bias
    # returns (K, N) bipolar atom matrix Phi
    pass

def simclr_dense_atom_discovery(byte_pairs, N, K, n_epochs, temperature, seed):
    # InfoNCE on dense continuous codes; no sparsity. Negative control.
    pass

# --- evaluation (reuse existing substrate primitives) ---
def cleanup_acc_at_M(Phi, eval_pairs, M_stored, k_active, seed):
    # store M_stored pairs into substrate W via outer-product, eval cleanup acc
    pass

def compute_effective_utilization(usage_dist):
    # H(p) / log(K)
    pass

def compute_dmpk_signature(W_per_atom_or_global):
    # reuse from notes/exp_dev_handoff_research_mesoscopic_xtalk_diagnostic_2026-05-25.md
    pass

# --- per-cell harness ---
def run_arm_a_learned(corpus, N, K, k_active, M_grid, seed):
    Phi_learned = competitive_wta_atom_discovery(corpus.pairs, N, K, k_active, ...)
    return {
        'effective_utilization': compute_effective_utilization(...),
        'atom_sparsity_avg': ...,
        'cleanup_acc_at_M': {M: cleanup_acc_at_M(Phi_learned, ..., M, ...) for M in M_grid},
        'centroids': Phi_learned.mean(0).tolist(),  # for P3
        # optional Dorokhov band
        'dmpk_bimodality_ratio': compute_dmpk_signature(...),
    }

def run_arm_b_simclr(corpus, N, K, M_grid, seed):
    # mirrors arm A but with dense SimCLR atoms; predicted to UNDERPERFORM PPMI
    pass

def run_ppmi_baseline(corpus, N, M_grid, seed):
    # uses existing PPMI atom path
    pass

# --- main: 3 corpora x 2 arms + baseline, multi-seed ---
def main(config):
    results = {}
    for corpus_name in ['PY', 'EN', 'RND']:
        for arm in ['A_LEARNED', 'B_SIMCLR', 'PPMI_BASELINE']:
            for seed in range(config['n_seeds']):
                results[(corpus_name, arm, seed)] = ...

    # compute P1 / P2 / P3 from results aggregations
    p1_pass, p1_fail, p1_label = evaluate_p1(results)
    p2_pass, p2_fail, p2_label = evaluate_p2(results)
    p3_pass, p3_fail, p3_label = evaluate_p3(results)
    verdict_tag = compose_verdict_tag(p1_label, p2_label, p3_label)

    metrics = {
        'effective_utilization': ...,
        'atom_sparsity_avg': ...,
        'cleanup_acc_ratio_at_M2000': ...,
        'cosine_distance_centroids': ...,
        'cross_corpus_retrieval_gap': ...,
    }
    verdict_msg = f"P1={p1_label} P2={p2_label} P3={p3_label} ratio_M2000={...} util={...} corp_gap={...}"
    Path('metrics.json').write_text(json.dumps({'verdict': verdict_tag, 'verdict_msg': verdict_msg, 'metrics': metrics, 'config': config}))

if __name__ == '__main__':
    # run self-tests first
    selftest_effective_utilization()
    selftest_competitive_wta_step()
    selftest_cleanup_acc_ratio()
    # then main
    config = json.loads(sys.argv[1]) if len(sys.argv) > 1 else default_config()
    main(config)
```

Self-tests are non-negotiable per the v203 L1 lock (Alt 3 + Pred-4 both crashed at production code path despite passing spec-level tests).

---

## ETA + budget envelope (Research estimate; exp_dev refines)

- Smoke at N=512, M_stored=200, K=32, k_active=4, 1 seed, 1 corpus: **~3-5 min CPU**, mainly to verify pipeline + self-tests + first-cell production API hit
- Full at N=4096, M_grid={500,1000,2000,4000}, K=128, k_active=12, 5 seeds, 3 corpora, 2 arms + baseline: **~3-8 hours remote_cpu** (single thread); GPU acceleration possible but not required (Hebbian outer-product is embarrassingly parallel and CPU-friendly)
- If wallclock pressure: prioritize 5-seed × M=2000 single-point P2 over the {500..4000} sweep — P2 is the load-bearing comparison; the sweep is for envelope characterization

---

## Triage flag for exp_dev cycle start

**Bet N is the LOWEST-DEPENDENCY Tier-1 path right now:**
- MoE rebuild is GATED on alpha_c calibration anomaly (v203 — see `notes/exp_dev_handoff_research_alpha_c_recalibration_2026-05-24.md`)
- SSM-HiPPO has the closed-form-task-cleanup-already-perfect issue from 15-angle triage A1 smoke (`research_15_angles_triage_2026-05-24.md` line ~139 — script needs redesign for noisy/vocab-cleanup variant)
- Bet N has NO outstanding dependency gate AND has direct literature precedent

When SSH-to-remote returns, ship Bet N FIRST among Tier-1 paths.

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
