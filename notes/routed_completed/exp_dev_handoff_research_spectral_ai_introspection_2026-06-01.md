# exp_dev hand-off -- research: spectral AI introspection

**Filed:** 2026-06-01 by research sub-agent.

**Trigger:** Research delivery on spectral AI introspection -- substrate as third-party algebraic auditor of external AI system activation streams. GO verdict. Monitoring overhead 0.73% of LLM inference. Unique capability vs EigenTrack/SIGMA: cumulative history + third-party isolation. Actionable probe: synthetic LLM activation stream with controlled rho injection, verify Z-statistic flags at predicted k_crit.

**Pause state:** check `data/orchestrator_paused.flag` before dispatching.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, seeds, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke/FULL profiles. Orchestrator does NOT specify numerical parameters beyond what is structurally required for the question.

**Source note:** inline in research sub-agent output 2026-06-01 (spectral AI introspection drill).

---

## Anchor candidates (rank-ordered)

### 1. Z-statistic sensitivity validation -- controlled rho injection

- **Anchor pointer:** Research delivery 2026-06-01; prediction k_crit = 3 * N^(1/3) near-duplicate activations before Z flags (at N=8192: k_crit ~ 60). Test by generating synthetic activation stream: (M - k) independent random +-1 vectors + k near-duplicate vectors with pairwise rho=1. Write all M into substrate W. Measure Z-statistic (lambda_max - MP_bulk_edge) / TW_scale. Verify Z > 3 first occurs at k >= k_crit.
- **Substrate-product reading:** Confirms the spectral Z-stat is the correct sensor for activation concentration. If HP, substrate has a derived sensitivity bound deployable in a product audit API. If HF, the BBP-derivation model is wrong (possibly finite-N corrections dominate at relevant M; need to check BBP formula vs exact Tracy-Widom at substrate N).
- **Tier hint:** Local CPU smoke. Synthetic activations -- no LLM needed. N in {1024, 4096, 8192}. Sweep k from 0 to k_crit*2. Check Z vs theoretical prediction. Very fast: O(M * N^2) total write cost, O(N^2) spectral check.
- **Why now:** Cheapest decisive test for the entire GO hypothesis. If this fails, the GO verdict must be revised before any product framing.

### 2. Advance-warning window measurement -- partial correlation ramp

- **Anchor pointer:** Research delivery 2026-06-01; for partial correlation (rho_dup < 1 between near-duplicate outputs), k_detect scales as k_crit / rho_dup. Test: inject activations with pairwise rho in {0.2, 0.5, 0.8, 0.95} at varying k. Measure empirical k_detect (first Z > 3 crossing). Compare to theoretical curve k_detect(rho) = 3*N^(1/3) / rho.
- **Substrate-product reading:** The advance-warning window relative to output-level detection depends on rho_dup. If rho=0.5 (plausible for LLM mode-collapse), substrate flags at k~120 while output KL divergence would need k~200+ (prior GAN mode-collapse literature baseline). If curves cross early (substrate flags later than output divergence), the third-party auditor framing weakens.
- **Tier hint:** Local CPU. Extends Anchor 1 experiment by sweeping rho_dup. No additional infrastructure needed.
- **Why now:** Quantifies the advance-warning claim that is the product differentiation story.

### 3. Third-party isolation audit -- information leakage bound

- **Anchor pointer:** Research delivery 2026-06-01; set-algebra privacy property: tr(W1 W2) reveals HOW MANY shared activations, not WHICH. Verify that from W alone (not the individual activation vectors), an adversary cannot reconstruct which LLM outputs were correlated. Test: given W and a known probe activation xi_probe, can an adversary recover which of the M stored activations matched xi_probe? The answer should be: only the count (tr(W * xi_probe xi_probe^T) / N = approximate match count), not the identities.
- **Substrate-product reading:** If the isolation property holds algebraically (it should from the outer-product structure), then substrate can serve as a COMPLIANCE AUDITOR that a regulated entity runs on its AI system -- the auditor sees the count, not the data. This is a product differentiator no existing spectral monitoring system (EigenTrack, SIGMA) provides.
- **Tier hint:** Analytical verification + brief CPU test. The algebraic argument is already in Round 6 drill (set-algebra trace identity). The audit here is implementing a realistic adversary and verifying they cannot recover more than count information.
- **Why now:** Required for the third-party auditor product framing. Without this, the privacy-preserving audit claim is unverified.

---

## Context pointers

- Research synthesis: inline in research sub-agent session output 2026-06-01
- Prior free-probability drill: `notes/research_free_probability_substrate_2026-05-26.md` (spectral Z-stat derivation, MP bulk, TW edge)
- Round 6 set-algebra primitives: `notes/research_round6_10_drills_broad_exploration_2026-06-01.md` (Axis 4, trace identity; Axis 2, Query-DP)
- EigenTrack lit precedent: arXiv:2509.15735 (temporal spectral analysis, AUROC 0.82-0.94)
- SIGMA lit precedent: arXiv:2601.03385 (Gram matrix sub-sample log-det for collapse detection)
- Field advisor: `tools/orchestrator/research_field_advisor.py` -- free-probability F2 (Tracy-Widom) top-5
- SKAH-M class: `notes/project_substrate_skahm_class_confirmed_2026-05-27.md`

---

## Contract

exp_dev is authorized to:
- Design and queue Anchor 1 (Z-stat sensitivity) as a local CPU smoke anchor
- Design and queue Anchor 2 (partial rho sweep) as a local CPU anchor riding same experiment
- Treat Anchor 3 as an analytical check before writing any implementation
- Sequence anchors: Anchor 1+2 combined (same sweep), then Anchor 3 as analytical follow-on
- Promote to GPU if N=16384 is needed for the BBP finite-N correction region

exp_dev is NOT authorized to:
- Modify cap_map rows without orchestrator approval
- Pre-specify HP/MID/HF numerical bounds (exp_dev derives from k_crit formula + formula-selftests)
- Frame results as "AI monitoring product" -- frame as capability characterization only

## Autonomy declaration

Per [[feedback-no-experiment-design-in-prompts]]: all anchor specifications (N, M, K, seeds, thresholds, queue routing, anchor names, ETAs) are exp_dev's design decisions. This hand-off provides the WHAT and WHY; exp_dev provides the HOW.

<!-- routing-completed: Acted-on 2026-06-01: handoff to Round 10 dispatch -->
