# exp_dev hand-off — research: math/social/abstract grounding core-expansion

**Filed by:** research sub-agent. **Trigger:** `notes/research_math_social_abstract_grounding_core_expansion_2026-07-10.md` — brain-first drill on why the spanning grounded core (grounding-kernel + NSM primes + Lancaster sensorimotor norms) failed to cosine-reach MATHEMATICAL (-0.43) and barely reached SOCIAL (+0.015) domains, while EMOTIONAL (+0.48) and PHYSICAL (+0.27) reached fine. Literature converges: math/social/abstract grounding is a STRUCTURALLY DIFFERENT mechanism from sensorimotor grounding (magnitude sense, social-relational power x affiliation coordinate, metaphor structure-mapping, introspective/affective simulation) — a sensorimotor-only core has no channel for these to load onto. Fix is core-expansion (new channels + a metaphor-structural bridge), not a decoder fix — the decoder was already proven healthy per the dispatch context.

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time. All three anchors below involve new data joins / new channels — pause-gated under standard exp_dev discipline. No zero-dispatch analysis-only anchor exists this cycle (unlike some prior hand-offs) because the fix requires new attribute data, not re-scoring of existing data.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names ANCHOR + POINTERS + the falsifiable predictions from the research note only. exp_dev designs ALL of: exact join/pipeline implementation, N, seed count, threshold implementation detail, queue choice, smoke profile, FULL profile.

---

## Anchor candidates (rank-ordered)

1. **MAGNITUDE/ORDINALITY channel + re-run MATHEMATICAL-domain grounding-reach test**
   - Anchor pointer: `notes/research_math_social_abstract_grounding_core_expansion_2026-07-10.md`, Section 2 ("MATH") + Section 4 HARD-PASS items 1/3/4 + HARD-FAIL item 1.
   - Substrate-product reading: add two sub-sources as one MAGNITUDE/ORDINALITY exterior channel — (a) a formally-computed magnitude/ordinal-rank value for the numeral/quantity sub-vocabulary (seven, dozen, million, first, second — near-zero cost, no norm study needed, definitional); (b) Troche/Crutch/Reilly Abstract Conceptual Feature (ACF) "quantity" ratings (~400 words, 7-point Likert "size, amount, or scope") for the broader abstract vocabulary. Fuse into the existing hub-and-spoke / late-fusion architecture (same pattern as the Lancaster/VAD channels), then re-run the identical per-domain cosine grounding-reach test on MATHEMATICAL, held out from whatever fit the channel.
   - Tier: local/CPU smoke first (small matched probe subset) before FULL dispatch on the complete MATHEMATICAL probe set.
   - Why now: this is the domain with the largest, cleanest gap (-0.43, the only ANTI-grounded domain) and the cheapest data acquisition path (numeral magnitude is computable, not elicited) — highest expected-value-per-cost anchor in this hand-off.

2. **SOCIAL-RELATIONAL (power x affiliation) channel + re-run SOCIAL-domain grounding-reach test, WITH mandatory affect-ablation**
   - Anchor pointer: same research note, Section 2 ("SOCIAL") + Section 4 HARD-PASS items 2/4 + HARD-FAIL items 2/4.
   - Substrate-product reading: add a 2D SOCIAL-RELATIONAL channel (power/dominance x affiliation/warmth) sourced from Interpersonal-Circumplex-style trait ratings (IPIP-IPC or equivalent) or, if that proves impractical to acquire quickly, Binder et al.'s Social/Human feature dimensions (535 concepts) as a fallback proxy. Fuse via the same late-fusion architecture. **Mandatory companion step**: per HARD-PASS item 4, run a per-channel ablation zeroing the new social-relational channel alone while KEEPING any existing/planned affective (VAD) channel, to confirm SOCIAL's reach gain is not just relabeled EMOTIONAL reach (affect and social-relational content are known to correlate per Binder's own social/emotion covariance finding).
   - Tier: local/CPU smoke first; note the current SOCIAL reach (+0.015) is barely above zero, so even a modest, correctly-ablated gain would be a meaningful result here.
   - Why now: SOCIAL is the domain closest to the pass bar already (+0.015 vs the target ~+0.15) — plausibly the cheapest domain to flip, but ONLY if the ablation confirms genuine social-relational content rather than affect bleed-through (this is the single most likely way this anchor could produce a fake-looking pass).

3. **Metaphor-structural-bridge scoping pass (mechanism B) — gated on Anchors 1/2's residual, do NOT build ahead of the residual being known**
   - Anchor pointer: same research note, Section 3 "(B) METAPHOR/ANALOGY STRUCTURAL BRIDGE" + Section 4 HARD-FAIL item 1 + CORE-EXPANSION RECOMMENDATION item 3.
   - Substrate-product reading: only after Anchors 1/2 land and their HARD-PASS/HARD-FAIL is known, scope a new graph edge type (concept --GROUNDED_VIA_METAPHOR--> image-schema node: PATH, CONTAINER, FORCE, COLLECTION) seeded from Lakoff/Nunez's 4 arithmetic-grounding metaphors, for whatever MATH/ABSTRACT residual remains ungrounded by the scalar channels. This reuses existing diffusion machinery per the companion ATL-hub note's "literal hub node" option — new edges, not new architecture.
   - Tier: design/scoping only until Anchor 1's residual is measured; do not pre-build.
   - Why now (deferred): per the research note's own falsifiability logic, building this before knowing Anchor 1's residual risks solving a gap that scalar channels already closed, or under-scoping a bridge for a residual that turns out larger than expected. Sequence strictly behind 1/2.

---

## Context pointers (file paths, not summaries)

- `notes/research_math_social_abstract_grounding_core_expansion_2026-07-10.md` — this drill's full note (HEADLINE, all 4 questions answered with citations, CORE-EXPANSION RECOMMENDATION, fair-test HARD-PASS/HARD-FAIL bands).
- `notes/research_multi_attribute_grounding_fusion_ATL_hub_2026-07-10.md` — same-day companion note establishing the hub-and-spoke / late-fusion architecture (recommended order: separate per-attribute diffusion, reliability-weighted late combination) and the mandatory pre-flight pairwise-correlation gate + per-attribute scrambled-control fairness gate that both new channels in this hand-off must pass.
- `notes/research_deliberate_ingest_spec_spanning_grounded_core_2026-07-10.md` — establishes grounding-reach as the PRIMARY core-acceptance criterion (Section 3 of that note) that this hand-off's fair test extends.
- `notes/substrate_capability_map.md` — current cap_map; the grounding-core / spanning-basis row this thread affects.
- Whatever file holds the original per-domain cosine VET results (EMOTIONAL +0.48 / PHYSICAL +0.27 / SOCIAL +0.015 / MATHEMATICAL -0.43) and the existing grounding-reach test implementation — exp_dev should locate this via the grounding-kernel / NSM-primes / Lancaster-norms cell history (not independently re-derived by research this cycle; the numbers were supplied directly in the dispatch context).

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands are already specified in the research note Section 4; exp_dev may sharpen implementation detail but the bands themselves came from research and should not be loosened.
- Self-test per [[feedback-formula-selftests]].
- Both Anchor 1 and Anchor 2 REQUIRE the scrambled-attribute-must-fail control (per the existing grounding-reach test's own discipline, and per the companion ATL-hub note's Pitfall #3) — a channel that produces a positive-cosine gain under a scrambled/permuted control has not demonstrated genuine grounding signal.
- Anchor 2 REQUIRES the affect-ablation check before any SOCIAL-domain pass is reported (see Anchor 2 above) — this is not optional given the documented social/emotion feature covariance.
- Multi-seed FULL on smoke clearance for both Anchor 1 and Anchor 2; report median-seed result, not mean-only, per the seed-fragility discipline established in the companion ATL-hub note.
- status_log entry per anchor with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: exact join/pipeline implementation for the magnitude and social-relational channels, which specific norm dataset/instrument to acquire for the SOCIAL channel (Interpersonal-Circumplex-style vs. Binder Social/Human fallback) if acquisition cost differs from expectation, N, M, K, seed count, precise threshold implementation (the bands are pre-specified in the research note; exp_dev implements them), queue choice (Tier A/B/C), ETA, smoke profile, FULL profile, and whether to run Anchors 1 and 2 in parallel or sequentially. If exp_dev judges that Interpersonal-Circumplex-style word/trait ratings cannot be acquired within a reasonable cycle budget, falling back to Binder et al. Social/Human features alone for Anchor 2 is exp_dev's call to make, not pre-baked here — flag the substitution in the delivery note if made. Anchor 3 (metaphor bridge) is explicitly NOT to be started until Anchor 1's residual is measured; that sequencing constraint is not exp_dev's to override without flagging back to research/strategy.

---

## Filed by

Research sub-agent, 2026-07-10, brain-first grounding-core-expansion drill (Director-requested). Hand-off ready for exp_dev pickup on next queue-refill or dedicated dispatch cycle.
