---
owner_verdict: DONE
---

SUBMISSION — aimed_reading_is_built_and_the_reader_never_calls_it
Status: REFUTED (on the brief's literal bar) — with a resolved, verified reframe that is the real payload.

What was asked
The organ that chooses what to read next (hdlab/information_foraging.py, Charnov's marginal-value theorem) is built and witnessed but the reading loop never calls it. The one run that had tested it reported a pass while actually losing to the fixed 4-corpus schedule under an uncontrolled 7.6× register bias. The bar: aimed reading must beat the fixed schedule — not just random — on held-out coverage, on a live call site, with the register bias controlled and an information-free twin losing.

Verdict on the literal bar — REFUTED, and now seed-robust
Wiring the built forager (surprise / learning-progress currency) into the reading loop does not beat the fixed schedule on register-controlled held-out coverage. FROZEN 0.0510; the forager loses on 3 of 3 seeds (−0.0103, −0.0331, −0.0277; REPLICATED, no info-free control reproduces half the effect). The learning-progress signal is inert (ties a random target). The bottleneck is grounding depth, not source choice: the fixed schedule reads a few corpora deeply so words repeat enough to ground; every aimed reader spreads thin.

One genuine positive on coverage (separate finding, not the forager): a different chooser — a comprehensible/learnable-input reader (v6) — beats the fixed schedule on register-controlled coverage on 3 of 3 seeds (+0.0405, +0.0397, +0.0286; REPLICATED, twin loses). It does not satisfy the literal bar (it isn't the forager the brief is about), but it is a real replicated capability and it motivated the reframe below.

The reframe (owner-driven) and its resolution — the real payload
Coverage is the wrong objective. Grounding more words is not understanding more meaning. So we asked whether reading produces meaning at all, and by what mechanism. This produced a clean, independently verified answer:

Reading alone produces real word-meaning. A reader's own distributional embedding (PPMI+SVD over its co-occurrence) scores WordSim-353 Spearman ~0.34 once it has read ~10k sentences. (A low-data "smoke" that suggested otherwise was a starvation artifact and was retracted.)

The brain's way to add grounding is integration, not substitution — and it works. Our shipped "distillation" operator trained the reading channel to mimic the grounded sensorimotor hub, discarding reading's own signal; it scored below raw reading everywhere (down to −0.24). That was the bug. Replacing it with complementary equal-weight fusion of the reading spoke (~0.34) and the sensorimotor grounding spoke (~0.40) yields ~0.45–0.49 — above both spokes (CI-separated over the stronger spoke in 2/3 readers, point-wise above both in 3/3), with the shuffled-grounding twin losing CI-separated in 3/3. This is the hub-and-spoke prediction holding: two modalities, each contributing complementary information.

The simple operator is the right one — confirmed by two failed attempts to beat it. A concreteness-gated fusion does not beat uniform (L2); a learned CCA/PCA hub does not beat fixed equal-weight fusion and is sometimes worse (L3) — CCA chases the shared subspace and discards the complementary information fusion preserves. Three convergent results validate: fixed equal-weight complementary fusion is the sufficient, brain-faithful meaning operator at this scale.

Optimization ceiling (asked: "fully optimize") — measured and VET-confirmed
Swapping the thin 12-dim sensorimotor hub for a CSKG commonsense-graph embedding (built here: 4.63M English edges, PPMI+SVD, 100% benchmark coverage) lifts WordSim to ~0.65 and SimLex from ~0.15 to ~0.30 in all three readers. Independent landed-VET confirmed the numbers are clean (exact recompute, no label leak, twin collapses, positive control passes). But the audit refuted the synergy framing: GROUNDED_CSKG alone ≥ FUSION_CSKG ≥ FUSION_3WAY in all six cells — the graph subsumes reading and the hub rather than complementing them (cross-validated tuning zeros the hub weight). So this is a foundation-quality win — a better single relational channel — not multi-modal spoke synergy. On standard lexical benchmarks, ~0.65–0.70 is the ceiling and nothing adds to the graph.

PINNED vs OURS
PINNED: meaning = a hub integrating modality spokes complementarily (hub-and-spoke; Patterson, Lambon Ralph); combined ≥ either spoke — confirmed. Distributional semantics for the reading spoke (Harris). Charnov MVT leave rule (kept exactly). Spacing effect for the depth lever.
OURS-UNDER-TEST: that equal-weight z-fusion is the faithful software form of hub integration — validated as sufficient (nothing beat it), not proven optimal. The trace-coherence learning-progress proxy (refuted). Calling the CSKG relational graph "grounding" — not defensible per VET; it is a better distributional channel.
What would withdraw / honest caveats
The concreteness-localization story (grounding helps concrete words more) is suggestive but underpowered (abstract strata n=30–36; one reader reverses) — not claimed.
The meaning results are point estimates with bootstrap CIs on the key deltas; no cross-scorer transfer (WordSim and SimLex reported separately).
The CSKG lift is real but is not grounding-synergy; do not atomize it as such.
The one open brain-foundational frontier
Does a sensorimotor/perceptual spoke add on top of the CSKG relational channel — on a task where perception is decisive? Lexical relatedness benchmarks may structurally hide grounding's contribution. This needs a non-circular perceptual benchmark (cannot ground and score with the same norms), which is a scoping decision, not a quick drill.

Proposed hdlab change (NOT landed — strategy lands it, board Q111)
Wire the corpus chooser into substrate.read() (replace the rotated order, keeping the pinned Charnov leave rule) — as correctness, not a performance lever (it does not move coverage; depth is upstream). Higher-value: give the live reader a separable co-occurrence store (the reading spoke) fused with grounded_similarity at query time — the standing PRIORITY-2 problem, now motivated: the raw store is itself meaning (~0.34), and fusing it with grounding gives ~0.45+.

Reproduction
Coverage + replication: verification/test_aimed_reading_learnable_input.py; experiments/exp_aimed_reading_seed_replication_v4.py (metrics_frequency.json, metrics_learnable.json).
Meaning: experiments/exp_reader_meaning_integration_diag_v1.py (L1), ..._gated_v1.py (L2), ..._learned_v1.py (L3), ..._teacher_optimization_v1.py (L4 + CSKG cache).
Narrative + evidence: notes/problems/aimed_reading_is_built_and_the_reader_never_calls_it/{SOLVED.md, FORWARD_WORK.md, INTEGRATION_INVESTIGATION_PLAN.md}. Ledger: python tools/problem_ledger.py --check → exit 0.
TLDR
The piece that picks what to read next is built but unplugged. Plugged in, it does not beat the old fixed reading list at learning everyday words — depth of reading matters more than cleverly choosing sources. But the deeper question we chased is the real result: reading really does build word-meaning, and combining it with hands-on (sensorimotor) grounding the brain's way — letting each add what it uniquely knows — beats either alone, with a scrambled control failing to prove it's real. Pushing for the highest score, a giant commonsense knowledge graph wins outright (~0.65), but an independent audit showed it wins by being a better single source, not by combining senses. The only thing still open is a harder question needing a different test: does perceptual grounding add anything once you already have that graph?
