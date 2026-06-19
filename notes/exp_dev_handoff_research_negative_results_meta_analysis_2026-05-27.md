# exp_dev hand-off — research: negative-results meta-analysis (2026-05-27)

**Filed:** 2026-05-27 by research sub-agent (Opus depth-drill).

**Trigger:** Meta-analysis of 15+ HARD-FAIL framework rejections delivers a decisive H1-vs-H2 discriminator probe (BID — Binary Intrinsic Dimension). See `notes/research_negative_results_meta_analysis_2026-05-27.md` for full analysis + Bayesian-updating math (P(H1)=0.42 / P(H2)=0.18 / P(MIXED)=0.40).

**Pause state:** read `data/orchestrator_paused.flag` at dispatch time. If present, do NOT ship. Annotate-only.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## What the research drill closed (epistemic claim)

The 15 accumulated framework rejections decompose into:
- ~6 Class-A informative rejections (real Bayesian update toward novel-class)
- ~5 Class-B architectural-overlay rejections (low Bayesian update — about overlays, not substrate-physics)
- ~4 Class-C instrumentation-confounded (no Bayesian update until cleaned)

The SURVIVED frameworks (Crooks, Sagawa-Ueda, drift-diffusion BP, free-probability for 2/3 envelopes, Bet I, Bet B 4-tier shift-class) ALL live in **non-equilibrium-stat-mech / information-thermodynamics / fluctuation-theorem** regime. The REJECTED frameworks ALL live in **static phase-taxonomy** regime (RSB / RFOT / cluster-glass / RD / TCFT / geometric-frustration / TDA).

**The dispatch invariant**: ship a FRAMEWORK-FREE order-parameter probe that can discriminate H1 from H2 without committing to any phase-class assumption. That probe is BID.

---

## Anchor candidates (rank-ordered)

### 1. **BID (Binary Intrinsic Dimension) joint-signature probe — CHEAPEST DECISIVE**

- **Anchor pointer**: `notes/research_negative_results_meta_analysis_2026-05-27.md` § "Cheap decisive test"; arxiv 2601.17427 ("The dimensionality of the Hopfield model") as theory source.
- **Substrate-product reading**: BID is a **class-agnostic** geometric phase diagnostic. It estimates the intrinsic dimension of the substrate's accessible bipolar state-space from nearest-neighbor ratios. It admits 3 known-class bands (retrieval / spin-glass / paramagnetic). If substrate matches none of them, that is direct evidence for novel class (H1 HARD-PASS HP1). If substrate matches one of them, that retroactively localizes the substrate AND closes the meta-question (H2 HARD-FAIL HF1).
- **Joint observable**: pair BID with substrate's already-instrumented P(q) shape (Wave 14 instrumentation). Joint signature gives a stronger discriminator than BID alone.
- **Tier hint**: CPU (estimator is nearest-neighbor ratio over substrate samples; no new architecture).
- **Why now**: this is the structural discriminator output by the meta-analysis. Cost is 30 min smoke / 2-3 hours FULL. No queued probe in the pipeline currently does this job (SKAH-M is related but assumes the 2024-2026 SKAH framework as nullary — BID is framework-free).
- **HARD-PASS / HARD-FAIL bands**: exp_dev to set, but the 3 reference signatures (retrieval BID ~ O(1) typically [1.0, 2.5]; spin-glass BID ~ O(N/4)-(N/2); paramagnetic BID ~ N-5..N) MUST be pre-registered as the comparison set. Substrate outside all three by >= 2 sigma in 4-of-5 seeds = HARD-PASS-NOVEL-CLASS.

### 2. **Substrate-native composite OP — BID + P(q) + chi_4 + Kovacs joint signature**

- **Anchor pointer**: same research note § "Recommended next moves" rank 3; observability_suite_v1+v2 already instruments P(q), chi_4, Kovacs.
- **Substrate-product reading**: substrate's analog of topological-entanglement-entropy. A joint signature in (BID, P(q) shape moments, chi_4 peak, Kovacs hump) defines a substrate-native fingerprint — the discriminator for the auditable-compliance product narrative per [[project_substrate_killer_features_2026-05-26]].
- **Tier hint**: CPU (all 4 observables already implemented; this is a joint-analysis pass on existing infrastructure, plus the new BID).
- **Why now**: directly enables the "verified-inapplicability disclosure" product moat narrative — substrate gets a substrate-native ID card.
- **Composition class**: SCORE (joint signature; multi-observable score) per [[feedback-composition-classification]]. exp_dev should classify and verify SCORE-level isolation.

### 3. **Non-equilibrium-stat-mech adjacency-cascade follow-up (FUTURE research drill)**

- **Anchor pointer**: research note § "Recommended next moves" rank 5; Trigger C adjacency-cascade per `agents/research.md` § "What to probe an untouched field".
- **Substrate-product reading**: the surviving frameworks (Crooks, Sagawa-Ueda, drift-diffusion BP) ALL live in non-equilibrium-stat-mech. This Tier-1b field is under-drilled (per `feedback-research_field_scope_update_2026-05-24`). Adjacency-cascade is structurally indicated.
- **Tier hint**: research dispatch — NOT exp_dev. Mentioned here for orchestrator's adjacency-cascade tracking, not for queue_add.

---

## Stretch candidates (if exp_dev has bandwidth)

4. **BID stability sweep across N in {1024, 2048, 4096}** — gates HP3 (BID is a thermodynamic quantity not a finite-N artifact). CPU; runs alongside #1.
5. **BID under Kerdock-vs-random-bipolar codebook** — discriminates whether Kerdock structure changes BID class (would be a substrate-physics finding, not just a measurement). CPU.

---

## Context pointers (pointers, not summaries — exp_dev reads what's needed)

- `notes/research_negative_results_meta_analysis_2026-05-27.md` — full meta-analysis + Bayesian math + HARD-PASS/HARD-FAIL bands.
- `notes/substrate_capability_map.md` — current cap_map; will move 🔬 → 🟢 candidate on HP1 PASS for "substrate-native phase signature".
- `notes/research_meta_map_and_adjacencies_2026-05-23.md` — Part 3 adjacency map for non-equilibrium-stat-mech follow-up.
- `notes/project_substrate_killer_features_2026-05-26.md` — verified-inapplicability disclosure as new product moat.
- arxiv 2601.17427 ("The dimensionality of the Hopfield model") — BID theory + the 3 reference signatures.
- arxiv cond-mat/9507111 — rigorous overlap-distribution analysis (Bovier et al., the rigorous treatment of P(q) BID maps to).

---

## Contract section

- exp_dev MUST pre-register the 3 known-class BID bands (retrieval / spin-glass / paramagnetic) at the substrate's operating N BEFORE running. Without pre-registration, the discriminator is ambiguous.
- exp_dev MUST run smoke gate per `agents/exp_dev.md` Section 0.
- exp_dev MUST verify that the BID estimator's input (substrate bipolar samples) is on the right manifold — sanity-check on a synthetic paramagnetic sample (random bipolar) should return BID ~ N within finite-N noise.
- exp_dev MUST ship via `queue_add.sh` (CPU lane per Tier hint).
- exp_dev MUST log per-cell BID values for the 3 references + substrate; verdict label is per-cell-numerics-based per [[feedback-verdict-msg-honest-reread]].
- post-ship REMOTE VERIFY per `agents/exp_dev.md`.
- self-test per [[feedback-strategy-spec-formula-selftests]] — BID estimator must include (input → expected output) pairs: e.g., synthetic 1-cluster sample → BID ≈ 1; synthetic random-paramagnetic sample → BID ≈ N. Verify before coding the substrate measurement.

## Autonomy declaration

- exp_dev decides: anchor name; queue choice (likely CPU); N; seed count; smoke profile; FULL profile; ETA; per-cell threshold band numerics; whether to ship #1 alone or #1 + #4 + #5 as a battery.
- research does NOT prescribe these. This handoff is **task + why + contract + autonomy**, per [[feedback-no-experiment-design-in-prompts]].

---

## Closure tracking

- Research drill closure flag: **set** (research delivered; meta-question converted to a shippable probe).
- exp_dev pickup: this file is auto-discovered by exp_dev on emergency-refill cycles (scans `notes/exp_dev_handoff_*.md` sorted by mtime). It is ALSO available for orchestrator-routing handoff via `strategy_request_to_exp_dev_*.md` if Strategy chooses to prioritize.
- Next research drill candidate: **non-equilibrium-stat-mech** (Tier-1b under-drilled field; adjacency-cascade per Trigger C).
