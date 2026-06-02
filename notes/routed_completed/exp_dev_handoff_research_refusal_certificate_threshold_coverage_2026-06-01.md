# exp_dev hand-off -- research: refusal-certificate and threshold-coverage

**Filed:** 2026-06-01 by research sub-agent.

**Trigger:** Research delivery on refusal-certificate and threshold-coverage design space for additive Hebbian binary associative memory. Overlap-based mechanism identified as algebraically dominant. PP-31c precision-coverage knee MIDDLE_BAND (avg_knee=0.740, 2/5 seeds) -- open empirical question requiring calibration at N=8192, M=50-500.

**Pause state:** check `data/orchestrator_paused.flag` before dispatching.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, seeds, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke/FULL profiles. Orchestrator does NOT specify numerical parameters beyond what is structurally required for the question.

**Source note:** research synthesis delivered inline in research sub-agent session 2026-06-01 (this conversation).

---

## Anchor candidates (rank-ordered)

### 1. PP-31c precision-coverage knee calibration at production N

- **Anchor pointer:** PP31-2A MIDDLE_BAND 2/5 seeds (avg_knee=0.740) -- knee detection exists but threshold-sensitivity is seed-dependent; question is whether knee is stable at N=8192 with M in {50, 100, 200, 500}.
- **Substrate-product reading:** If the knee stabilizes at N=8192 (knee_std < 0.05 across seeds), refusal-certificate has a product-grade calibration protocol. If knee location is seed-dependent (high variance), refusal-certificate requires per-deployment calibration -- important for FDA SaMD / EU AI Act Art 14 compliance narratives.
- **Tier hint:** CPU (N=8192 is manageable; 5 seeds x 4 M-values = 20 cells). Remote CPU if local is busy.
- **Why now:** PP-31c is the last PENDING sub-property of PP-31. Its MIDDLE_BAND status is the blocking item for PP-31 row promotion. Cheap decisive test: measure knee location across seeds at N=8192.

### 2. Overlap-vs-energy mechanism comparison smoke

- **Anchor pointer:** Research delivery 2026-06-01 identifies overlap-based (max_mu |<q, xi_mu>|/N < tau_o) as algebraically cleaner than energy-based (-(1/2) q^T W q > tau_E) for threshold-coverage trade-off. These mechanisms are NOT equivalent when M is large (M/N > 0.05): energy conflates sum-of-overlaps with max-overlap. Empirical test: at fixed FPR target, which mechanism achieves higher true-positive rate?
- **Substrate-product reading:** If overlap-based dominates energy-based at matched FPR, substrate's refusal mechanism should canonicalize on overlap score -- product-relevant because overlap score is already computed as part of retrieval (zero extra cost). If energy-based is competitive, the energy landscape framing (OOD detection literature NeurIPS 2024 / AAAI 2025) directly applies.
- **Tier hint:** CPU smoke. Vary M/N ratio from 0.01 to 0.10, measure FPR vs TPR for both mechanisms, compare ROC-AUC.
- **Why now:** This comparison determines which mechanism becomes the canonical product API. Open design question before any hardening.

### 3. Deletion-refusal composition verification

- **Anchor pointer:** Research delivery 2026-06-01 derives that after W_new = W - xi*xi^T, the overlap score for xi drops algebraically: <xi, W_new xi>/N = <xi, W xi>/N - 1 (exactly 1.0 drop in overlap, deterministic). The composition should be empirically verifiable: delete xi, then query xi via refusal mechanism, confirm refuse signal. This is a zero-extra-cost property test.
- **Substrate-product reading:** If composition is clean (refusal triggers 100% of the time after deletion), deletion-certificate + refusal-certificate compose into a single audit primitive with two outputs: (a) "fact was stored here" and (b) "fact is no longer retrievable." This is the GDPR Art 17 / EU AI Act narrative crystallized -- algebraically certified erasure with algebraic retrievability proof.
- **Tier hint:** CPU analytical check; likely <60s. Can be attached to existing TCFT deletion-cert anchor or run standalone.
- **Why now:** Cheapest and highest-product-impact composition test. If it passes, a single paragraph in any compliance document covers both write and erase certification.

### 4. Adversarial evasion lower-bound probe (N-scaling)

- **Anchor pointer:** Research delivery 2026-06-01 derives adversary lower bound: constructing a query that evades overlap-based refusal requires finding q with |<q, xi_mu>|/N >= tau_o for some mu, where q is not a stored pattern. At tau_o = alpha_c (capacity-critical threshold), this is equivalent to solving a random k-XOR-like system, with expected sample complexity Omega(N^(1/2)) under random pattern geometry.
- **Substrate-product reading:** If the N-scaling of adversarial sample complexity is confirmed empirically (e.g., measure how many random queries are needed to find a false negative as N varies from 1024 to 8192), the substrate has a quantitative robustness guarantee for the refusal mechanism -- directly relevant to adversarial-robustness narrative.
- **Tier hint:** CPU sweep over N; measure fraction of random queries that evade refusal vs N; should scale as N^(-1/2). Local CPU.
- **Why now:** N-scaling is a structural prediction derivable from the theory; cheap to test; opens adversarial-robustness characterization that currently has no empirical anchor.

---

## Context pointers

- Research synthesis: inline in research sub-agent session output 2026-06-01
- PP-31 calibrated confidence row: `notes/substrate_capability_map.md` (v321 state -- PP-31a EMPIRICAL VALIDATED, PP-31b EMPIRICAL VALIDATED, PP-31c PENDING MIDDLE_BAND)
- PP-31 experiments already run: `experiments/exp_pp31_2a_precision_coverage_v1.py`, `experiments/exp_pp31_2d_refusal_cert_v1.py`, `experiments/exp_pp31_4a_per_hop_independence_v1.py`
- Deletion certificate (TCFT) row: cap_map v321 -- 88-96% green
- Modern Hopfield OOD literature: arxiv 2405.08766 (Hopfield Boosting NeurIPS 2024), arxiv 2502.14003 (Rectified Lagrangian AAAI 2025)
- Conformal prediction + reject option: arxiv 2506.21802 (distribution-free error guarantees via CP, 2025)
- Machine unlearning verification: arxiv 2003.04247 (probabilistic verification of machine unlearning)
- Field advisor: `tools/orchestrator/research_field_advisor.py`

---

## Contract

exp_dev is authorized to:
- Design and queue PP-31c knee-calibration smoke (Anchor 1) as a CPU-tier anchor targeting N=8192
- Design and queue the overlap-vs-energy ROC comparison (Anchor 2) as a CPU smoke
- Design the deletion-refusal composition check (Anchor 3) as a local CPU analytical probe
- Sequence anchors cheapest-first (PROT-004): Anchor 3 (pure analysis, <60s) -> Anchor 1 (knee calibration) -> Anchor 2 (mechanism comparison) -> Anchor 4 (adversarial N-scaling, deferred if queue is full)
- Promote any anchor to GPU if N>4096 multi-seed sweep is needed for the question to be decisive

exp_dev is NOT authorized to:
- Commit cap_map changes (those go to orchestrator after verdict)
- Modify PP-31 row bands without a verdict event routed through verdict_handler
- Add product-positioning narrative to experiment scripts

## Autonomy declaration

exp_dev has full autonomy to determine: anchor names, N, M, seeds, threshold sweep points, pre-reg HP/MID/HF bands, queue assignment, wall_s estimate, and sequencing within the 4-anchor budget above. No further approval needed for any anchor in this list.

Acted-on 2026-06-02: refusal cert PP-31 work covered v327+ pp31c near-capacity rescue partially worked
