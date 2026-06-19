# exp_dev hand-off -- research: free-probability F4 substrate-novel observability

Filed-by: research sub-agent (Opus) 2026-06-11
Trigger: 3x DEEP research drill delivered at notes/research_drill_free_probability_F4_substrate_observability_3x_2026-06-11.md
Pause state: RUNNING (orchestrator_paused.flag absent at filing time; honor live flag at exp_dev wake)

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off provides pointers and anchor candidates only. exp_dev owns experiment design, smoke gate, queueing, REMOTE VERIFY, self-test. Pre-registration bands and HARD-PASS / HARD-FAIL thresholds are in the research note section (c); do not re-design them inline.

---

## Anchor candidates (rank-ordered)

### Anchor 1 -- F4-OBS-E1 -- heavy-tailed prior detection
- Anchor pointer: research note section (c) Prediction P1.
- Substrate-product reading: substrate operator gains a single-scalar non-Gaussian-structure index (kappa_4_rect) with a principled semicircle null. This is the cheapest of the five sub-experiments.
- Tier hint: Tier-B observability primitive validation (single-snapshot check across three reference codebooks; no kb-size or N-sweep yet).
- Why now: P1 is the gating check for the whole framework. If C_iid does not pass semicircle null, the kappa_4 estimator is biased and the other four sub-experiments cannot be interpreted. Run this first.
- Cost: ~5-10 min CPU.

### Anchor 2 -- F4-OBS-E5 -- v4.0 triangle separation (FHRR / GHRR / hybrid)
- Anchor pointer: research note section (c) Prediction P5.
- Substrate-product reading: substrate operator gains a quantitative classifier for which substrate family a deployed codebook sits in. Directly substrate-distinctive vs LLM observability.
- Tier hint: Tier-B observability primitive + v4.0 triangle quantitative grounding.
- Why now: highest substrate-product distinctive value; R-transform additivity check is theoretically rigorous so a clean PASS would validate v4.0 triangle math.
- Cost: ~10-15 min CPU.

### Anchor 3 -- F4-OBS-E3 -- atom-isolation margin kappa_4 vs recall@1
- Anchor pointer: research note section (c) Prediction P3.
- Substrate-product reading: single-scalar retrieval-quality predictor from cleanup-margin distribution structure; gives capacity-headroom warning before recall@1 degrades.
- Tier hint: Tier-A capability-relevant observability (correlated with deployed retrieval quality).
- Why now: this is the prediction most directly tied to substrate retrieval product behavior. Requires 1000-query sample which exists in existing eval infra.
- Cost: ~10-15 min CPU.

### Anchor 4 -- F4-OBS-E2 -- N-sweep plateau detector
- Anchor pointer: research note section (c) Prediction P2.
- Substrate-product reading: verifies substrate's deployed N is in the free-prob asymptotic regime; gives a principled answer to "is our N big enough."
- Tier hint: Tier-B observability + asymptotic-regime sanity check.
- Why now: depends on E1 PASS (asymptotic regime requires unbiased estimator). Run after E1.
- Cost: ~10 min CPU.

### Anchor 5 -- F4-OBS-E4 -- capacity-saturation across kb-size
- Anchor pointer: research note section (c) Prediction P4.
- Substrate-product reading: continuous capacity-headroom signal that precedes recall@1 cliff by at least one M-decade; gives operator early-warning.
- Tier hint: Tier-A capacity-monitoring deployable.
- Why now: most expensive of the five (requires sub-codebook builds at kb-size sweep); run last after E1-E3 validate the primitive.
- Cost: ~15-20 min CPU plus dependency on kb-size sub-codebooks (may reuse existing PP-225 / kb50K artifacts).

---

## Context pointers (file paths; no summaries)

- notes/research_drill_free_probability_F4_substrate_observability_3x_2026-06-11.md (this drill's research note; all pre-reg bands and code sketches)
- notes/research_drill_free_probability_substrate_framework_3x_2026-06-11.md (prior 3x DEEP free-prob framework -- Layer 2 v1 primitive)
- notes/research_drill_rmt_beyond_free_probability_2x_2026-06-11.md (2x RMT-beyond-FP extension -- DBM + operator-valued + universality class)
- notes/research_drill_free_probability_family_tag_2x_2026-06-11.md (2x F4 + family-tag combined drill -- kappa_4_rect implementation sketch)
- notes/research_drill_layer4_dialectic_methodology_2x_2026-06-11.md (Layer 4 BOCPD surprise-channel host for kappa_4 trajectory feed)
- C:\Users\marsh\.claude\projects\d--AI\memory\substrate_v32_engineered_wrapper_2026-06-11.md (wrapper architecture compatibility frame)

---

## Contract

exp_dev:
- Build the kappa_4_rect + kappa_4_by_partition + kappa_4_margin primitive from the research note section (d) D.2 code sketch.
- Smoke-gate each anchor (composition-matched smoke per feedback-smoke-test-methodology; CI-band rule; multi-seed at HP boundary).
- Queue via queue_add to local_cpu_queue or home-CPU lane (NOT GPU; pure-numpy CPU).
- REMOTE VERIFY after ship.
- Self-test per formula-selftests (each kappa_4_rect call verified against centered semicircle null returning < 0.10 * m_2^2).
- Pause-gated: honor data/orchestrator_paused.flag at wake; do not ship while paused.

Research: maintains the pre-registration bands. If exp_dev needs HP threshold reinterpretation, escalate via strategy_request_to_research_*.md.

---

## Autonomy declaration

exp_dev owns: experiment file naming, runner choice (local_cpu_queue vs home-CPU), smoke composition, multi-seed count, sub-codebook source (re-build vs reuse PP-225 artifacts), order of anchor execution within the gating constraint (E1 first, E4 last).

research is hands-off after this hand-off file is filed unless exp_dev raises a HP-band design question.

---
