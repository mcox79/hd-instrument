# exp_dev hand-off — research: nonlinear-readout frontier

**Filed:** 2026-06-17 by Research sub-agent.
**Parent research note:** `notes/research_nonlinear_readout_frontier_2026-06-17.md`
**Trigger:** scope-coverage survey of nonlinear-readout families relative to current roadmap (linear / softmax-Hopfield / Willshaw). Survey identified five out-of-scope families with credible capacity-recovering claims in the literature.
**Pause state:** check `data/orchestrator_paused.flag` before queue-add. If paused, file as TIER-2-CANDIDATE not as immediate ship.

Per [[feedback-no-experiment-design-in-prompts]]: this handoff lists ANCHOR CANDIDATES with pointers and pre-registered bands; exp_dev owns N, corpus, seed count, anchor naming, queue choice.

Per [[feedback-research-can-be-wrong-only-proven-fully-believed-trust-tier]]: all claims below are T2 (lit-supported, NOT load-bearing) until cert-grade substrate cell confirms.

---

## Anchor candidates (rank-ordered)

### Candidate 1: sparse-Hopfield-entmax readout vs softmax baseline
- **Why now:** cheapest test (one hyper-param sweep); Hu 2023 (NeurIPS) provides tighter closed-form bound under sparse-pattern regime; substrate-untested on FHRR codes.
- **Anchor pointer:** entmax-alpha readout at alpha in {1.0, 1.5, 2.0} (softmax / 3/2-entmax / sparsemax); single readout-layer swap from existing softmax-Hopfield baseline.
- **Substrate-product reading:** if sparse readout matches or beats softmax recall at lower compute, the substrate gets a cheaper retrieval kernel without re-architecting; if it fails, the closed-form lit bound is shown not to transfer to structured HD codes (genuine substrate-novel negative finding).
- **Tier hint:** TIER-1 cheap (~1 day local CPU; N=1024; M sweep 0.1 to 16).
- **Pre-registered bands:** HARD-PASS recall >= 0.95 at M/N >= 8 with FLOPs < softmax. HARD-FAIL recall < 0.50 at M/N = 2. MIDDLE-BAND recall 0.50-0.95 at M/N=2 or compute parity.

### Candidate 2: random-features Dense AM (Hoover NeurIPS 2024)
- **Why now:** structurally important property - DECOUPLES parameter count from stored M (substrate growth without weight-explosion). No substrate cell has tested this.
- **Anchor pointer:** random-feature projection phi: R^N -> R^D with D in {N, 2N, 4N, 8N}; approximates exp-DAM energy via inner product in feature space; memories added by weight update not by concatenation.
- **Substrate-product reading:** if random-features beats softmax at fixed param count, this is a load-bearing growth mechanism for the substrate. If it fails, softmax remains the strict ceiling per generic family.
- **Tier hint:** TIER-1 cheap-to-medium (~1-2 days local CPU + small GPU for D=8N).
- **Pre-registered bands:** HARD-PASS recall >= 0.90 at M/N >= 4 with parameter count <= 4N. HARD-FAIL recall < 0.50 at M/N = 2. MIDDLE-BAND between.

### Candidate 3: Epanechnikov compact-support kernel energy (Pham 2025)
- **Why now:** unique property among the family - finite-radius basins predict ZERO crosstalk outside support radius. Softmax does not have this. Easy to falsify the crosstalk claim.
- **Anchor pointer:** replace softmax energy E = -log-sum-exp with Epanechnikov compact-support kernel; sweep radius r.
- **Substrate-product reading:** if compact-support delivers the predicted no-crosstalk-outside-r property AND maintains capacity, this is a NOVEL retrieval property the substrate currently lacks (clean rejection of out-of-pool queries).
- **Tier hint:** TIER-1 cheap (~1 day local CPU).
- **Pre-registered bands:** HARD-PASS recall >= 0.95 at M/N >= 2 AND measured crosstalk = 0 for queries at distance > r. HARD-FAIL either recall < 0.50 at M/N=1 OR nonzero crosstalk outside r (refutes Pham 2025 transfer).

### Candidate 4: predictive-coding inference readout (Salvatori 2021, BayesPCN Yoo 2022)
- **Why now:** iterative inference readout has different compute profile (T steps x N) but BayesPCN reports continual-learning regime that softmax-Hopfield does not address. Tests whether substrate gets continual-learning property "for free" via readout swap.
- **Anchor pointer:** 2-layer PC net atop existing substrate storage; readout = iterative inference.
- **Substrate-product reading:** if PC readout matches softmax on capacity AND adds continual-learning property, this is a meaningful capability expansion. If it adds neither, kill.
- **Tier hint:** TIER-2 (~2-3 days; iterative inference adds compute).
- **Pre-registered bands:** HARD-PASS recall >= 0.90 at M/N >= 4. HARD-FAIL recall < 0.50 at M/N=2 OR per-query compute > 10x softmax. MIDDLE-BAND with continual-learning bonus measured separately.

### Candidate 5: OMP / LASSO readout as compressed-sensing recovery
- **Why now:** classical CS guarantees k-sparse recovery from O(k log N) measurements; the linear-pseudoinverse readout the substrate currently uses as baseline fails at high load while OMP should not. Provides a clean compressed-sensing comparison axis.
- **Anchor pointer:** OMP readout with sparsity k swept in {N/4, N/2, N}; baseline = linear pseudoinverse readout.
- **Substrate-product reading:** if OMP beats linear pseudoinverse at high load AND matches softmax at low load, the substrate has a cheaper readout for sparse-payload regimes. Mostly a NEGATIVE-RESULT-VALUE candidate (likely too sparse-assumption-dependent).
- **Tier hint:** TIER-1 cheap (~1 day local CPU).
- **Pre-registered bands:** HARD-PASS recall >= 0.95 at M/N >= 2 with sparsity k <= N/2. HARD-FAIL recall < linear-pseudoinverse baseline at all M/N (substrate codes too dense for CS).

---

## Context pointers

- Parent research note: `notes/research_nonlinear_readout_frontier_2026-06-17.md`
- Recent substrate session arc (HALT + ARCH-A/B + capability-ceiling confirmations): see MEMORY.md entry "session_arc_2026-06-17_substrate_HALT_healing_recapture_global_verification.md"
- Prior recapture program note: `notes/project_recapture_program_ARCH_A_resume_state_2026-06-17.md`
- Cap_map: `notes/substrate_capability_map.md` (find rows under nonlinear-readout / heteroassociative-recall question for current state)
- USER compute policy: heavy runs -> REMOTE desktop; super-fast -> laptop (per `feedback_compute_remote_for_heavy_laptop_for_superfast_C0_cost_underestimate_USER_2026-06-16.md`)
- Audit discipline: USER-LOCKED negativity-bias rule and symmetric-verify (read ACTUAL not BAR; verify both directions)

---

## Contract

**Deliverable shape (per candidate that exp_dev decides to ship):**
1. Anchor entry in `data/<queue>.jsonl` with rank-ordered priority field.
2. Smoke gate pass before promote to graded.
3. Per-cell recall, FLOPs, parameter count metrics.
4. Verdict against pre-registered HARD-PASS / HARD-FAIL / MIDDLE-BAND bands above.
5. Status_log entry on completion (event_kind="experiment_result", importance=HIGH).
6. Entry in `exp_dev_decisions_<date>.md`.
7. Self-test per formula-selftests.

**Cost ceiling:** each Candidate 1, 3, 5 cell should fit in ~1 day local CPU at N=1024. Candidate 2 may need small GPU at D=8N. Candidate 4 may need 2-3 days for iterative-inference convergence sweeps. Per USER compute policy: heavy ones go to REMOTE.

---

## Autonomy

Exp_dev decides:
- Which candidate(s) to ship and in what order (suggested rank: 1 > 3 > 2 > 5 > 4 based on cost/clarity, but exp_dev's call).
- Exact N (CPU-feasibility dominated; N=1024 default).
- Exact corpus / pattern distribution (recommend matching ARCH-A and ARCH-B test conditions for direct comparison).
- M sweep granularity.
- Seed count (minimum 2 for variance).
- Anchor naming.
- Queue choice (local CPU vs remote GPU per USER compute policy).
- Whether to ship multiple candidates as a single parallel batch or sequentially.
- Whether to defer any candidate as TIER-2-CANDIDATE if pause flag is set or queue is full.

---

**End handoff.**
