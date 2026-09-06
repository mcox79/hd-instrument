---
review: EXCELLENT
review_text: Reverified first-hand test_curated_foundation_wic.py 6/6 (curated+coarsening crosses the mis-seeded-context wall CI-sep on both held-out splits; curated KNOWLEDGE is the lever; coarsening +0.0345). The pri-4 GOAL -- make the curated foundation's value LIVE/board-visible -- is ACHIEVED via the WiC/sense board arm (Step 0c, exp_board_wic_sense_v1, folded into the board run()): the board now SCORES the meaning channel, curated+coarsening 0.6639 vs the live PPR select_sense reader 0.6006 = +0.0633 CI-sep (the meaning channel had NO board dim before). REROUTED correctly (the brief's who-did-what/hub + meaning-readout proposals are located negatives -- parse-bound / no live read()-time meaning stage). DEFERRED to the §2-gated deep follow-on: the select_sense reader-side curated channel (a vector-scoring build into grounded_semantic_graph, which is ISLANDED -- 0 read()-time consumers) + a read()-time meaning stage that actually consumes sense selection. The residual past ~0.664 to human 0.80 is deep contextualization = the §2 no-transformer owner decision. §2b (arc-labeler/goal entries reference the meaning channel). INTEGRATED (board-visible) 2026-09-05; the read()-time consumer is the §2 follow-on.
---

# PROBLEM: the curated knowledge foundation (`hdlab/meaning_foundation.py`, +0.0755 on the meaning instrument) and the hub consumer (`composed_hub_predictor`, +0.065 from AvgSim→MaxSim) are LANDED-but-LATENT — NOTHING calls them at read() time, so their proven gains reach NO live board dimension. This is the WIRE-DON'T-ISLAND debt the foundation earns: take the frozen curated foundation into a LIVE read()-time consumer and make that consumer use it OPTIMALLY. Concretely (the solver's named #1): rebuild `composed_hub_predictor`'s verb-role exemplar store on the curated foundation vectors (C1b), ADOPT the MaxSim/top-k nearest-exemplar usage (the AvgSim mean-centroid is the measured-suboptimal usage, +0.065 to fix), and WIRE it into the live who-did-what/argument-selection path — measuring the LIVE consumer's metric off-vs-on, turning it ON if net-positive per no-default-off. The meaning-channel readout, when its live stage exists, must ALSO stack the three optimizations already landed: the curated store KEYS + P9 precision-weighting (gamma/topk) + the rare-sense Bayesian prior (sense_prior/prior_weight). Deliver a LIVE CI-separated gain on a consumed metric with an info-free twin LOSING and no-regress on the other dims — or a located NEGATIVE naming why the better KB + better usage does not help the live consumer (e.g. the live path is already parse/attachment-bound, not knowledge-bound).

**slug:** `wire_the_curated_meaning_foundation_into_a_live_consumer_and_adopt_the_maxsim_usage` — **opened:** 2026-09-05 by the strategy session (the owner asked, on integrating the curated foundation, whether it is default-on/live and whether consumers use it optimally — the honest answer is it is LATENT/unwired; this is the wire-it-live completion). **status:** OPEN. Strategy lands the Q111 wire. Glass-box, NO external LLM (the curated foundation is an admissible static offline asset). The frozen assets are on-disk (`data/frontend_assets/`); the loader is `hdlab/meaning_foundation.py`.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.

> ## 🧠 BRAIN-FOUNDATIONAL CHECKLIST (work through IN ORDER; not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Name the structure + computation; PINNED vs OUR-INVENTION. RESEARCH where unsure.
> 2. **REUSE — does an existing organ already do it?** Check `tools/substrate_map.py` / `hdlab/` FIRST.
> 3. **GENERALIZE — how does the brain generalize it?** Build for that.
> 4. **HIT A WALL? GO DEEPER.** A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, failed.
> 5. **OPTIMIZE BY EXACT REPLICATION.** Copy the computation, SWEEP the parameters.
> 6. **PERFORMANCE vs THE BRAIN.** Where do we lose signal? The mechanism-diff.
> 7. **ADJACENT COMPONENTS.** Map the neighbours — seeds the next problems.
> 8. **COMPLETION BAR.** COMPLETE + EXCELLENT + conveys the full benefit?

## 1. THE PROBLEM IN PLAIN LANGUAGE
We built a good, clean knowledge store and proved it makes the reader better at word meanings and at picking which thing a verb acted on — but nothing in the live reader actually calls it yet, so those wins are on the shelf, not on the scoreboard. The job: plug the store into a part of the reader that runs on every document, make that part use the store the smart way (nearest good example, not a blurry average), and show the live score goes up — or honestly show that this part of the reader is limited by something else (like parsing), not by knowledge.

## 2. WHY THIS ONE — the foundation is proven; the only thing between it and a live gain is the wire
Three gains are proven on their instruments (meaning +0.0755, which-argument +0.065/+0.098) but ALL latent — no read()-time consumer exists, so they touch zero board dims. The owner's WIRE-DON'T-ISLAND rule (and the no-default-off rule) make wiring it the mandatory completion: a validated gain left unwired is the exact islanding pattern to avoid. It is also the definitive test the solver named: does a better KB + better usage move a LIVE consumer, or is the live path knowledge-independent?

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: lexical/semantic knowledge is retrieved by CONTENT-ADDRESSABLE similarity to stored exemplars (Lewis-Vasishth cue-based retrieval; the brain matches to the nearest relevant trace, not a category average — MaxSim/exemplar over AvgSim/prototype for discrimination). The verb-role/who-did-what selection is a competition informed by that retrieved knowledge (Competition Model + selectional preference). REUSE (do NOT re-derive): `hdlab/meaning_foundation.py` (the frozen KEYS), `hdlab/composed_hub_predictor.py` (the hub consumer + its `score_pool`), `hdlab/diagnostic_context_wsd.py` (the meaning readout with gamma/topk + sense_prior/prior_weight already landed), `hdlab/graded_role_assigner`/the live who-did-what path (`situation_reader` role routing), `hdlab/consolidation_gate` (the admission guard).

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** curated store beats gloss +0.0755 CI-sep through `diagnostic_context_wsd` (keep-all optimum; witness 6/6); `composed_hub_predictor` AvgSim→MaxSim = +0.065 CI-sep on the ambiguous which-argument slice (witness 3/3); grow-on-new-vectors which-argument +0.098 on the covered slice (0.33→0.60). All LATENT — no live consumer.
- **INFERRED (you must measure):** whether rebuilding the hub on the curated-foundation vectors + MaxSim, wired into the live who-did-what path, lifts the LIVE consumed metric (the who-did-what arm) CI-separated with an info-free twin LOSING and no-regress; and whether the live gain is knowledge-bound or parse/attachment-bound (the named cause if it does not cross).

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: read `notes/problems/build_and_freeze_the_clean_curated_knowledge_foundation.../SOLVED.md` (esp. the WIRING section + NEXT EXPERIMENTS #1) IN FULL; read `hdlab/meaning_foundation.py`, `hdlab/composed_hub_predictor.py::score_pool`, and how the live who-did-what path selects arguments (`hdlab/situation_reader` role routing + `hdlab/graded_role_assigner`); read `experiments/exp_knowledge_factory_consumer_usage_tweak_v1.py` (the MaxSim tweak) + `exp_knowledge_factory_consumer_growth_v1.py`.
- Reproduce first-hand: the +0.065 MaxSim tweak (`test_knowledge_factory_consumer_usage_tweak.py` 3/3) + confirm `composed_hub_predictor` has NO live importer (grep — it is islanded).

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = the curated foundation wired into a LIVE read()-time consumer (the who-did-what/argument path via a MaxSim-usage `composed_hub_predictor` rebuilt on the curated vectors, and/or the meaning readout stacking store-KEYS + gamma + sense_prior) such that the LIVE consumed metric rises CI-separated over the current live reader, an info-free twin (shuffled-knowledge or verb-shuffled-exemplar) LOSES, and NO other dim regresses (each on its right instrument). Turn it ON if net-positive (no-default-off); keep OFF only with a measured reason. Report CI half-width + null p95; recompute floors per population. A rigorous located NEGATIVE — the better KB + better usage does not move the live consumer, with the named cause (e.g. the who-did-what live path is parse/attachment-bound, or the meaning readout has no live stage yet and building it is the §2-boundary decision) — is a FULL PASS.

## ALREADY TRIED / DO NOT REDO
- Do NOT re-build the frozen store or re-derive the +0.0755 / +0.065 (measured); this is about WIRING them live + the live measurement.
- Do NOT land the MaxSim tweak standalone on the islanded organ without the live wiring + measurement (that just moves the islanding) — the point is the LIVE consumer.
- Trimming the curated store is a measured DEAD END (3 trims fail to beat keep-all) — do not re-open it.
- The meaning-readout live stage may be blocked on the `reader_meaning_channel` / §2 contextual-input decision — if so, NAME that and land the hub/who-did-what wire (the within-invariant half) instead.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`; the wire is in `hdlab/composed_hub_predictor.py` (MaxSim `score_pool`) + `hdlab/situation_reader.py` (route the live who-did-what/argument selection through the rebuilt hub) and/or the meaning readout. REUSE `hdlab/meaning_foundation.py`, `hdlab/diagnostic_context_wsd.py`. Strategy lands the Q111 wire; fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE
- Do NOT quote the +0.0755 / +0.065 as a LIVE gain — they are instrument-level + latent; report the LIVE consumed-metric delta.
- Do NOT quote a live gain without the info-free twin losing + no-regress on the other dims (each on its right instrument).
- NO external LLM (the invariant); the curated foundation is the admissible static asset.
