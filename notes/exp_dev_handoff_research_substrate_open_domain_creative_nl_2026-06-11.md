# exp_dev hand-off -- research: substrate-only OPEN-DOMAIN CREATIVE NL (2x DEEP drill)

Filed-by: research:opus
Date: 2026-06-11
Trigger: 2x DEEP drill on substrate-only open-domain creative NL identified 3 untested substrate-only paths that are mathematically reachable per Frady 2020 / Stochastic-HD literature / substrate-CRF semiring. Pre-1x-drill ceiling was honest BUT did not exhaust path inventory.

Research note: d:/AI/hd-instrument/notes/research_drill_substrate_open_domain_creative_nl_2x_2026-06-11.md

Pause state: respect data/orchestrator_paused.flag. If flag present, this hand-off goes onto exp_dev's hand-off queue for pickup when pause lifts. Per [[feedback-no-experiment-design-in-prompts]] this file states ANCHORS and POINTERS; experiment design (HP details / smoke recipe / queue routing) is exp_dev's autonomy.

## Anchor candidates (rank-ordered)

### Anchor 1: PILOT-CREATIVE-1 -- substrate-only bounded-creative on TinyStories (tier hint: Tier-2 PILOT, CPU-only, 4-8 hours)

- Pointer: research note section (b) PILOT-CREATIVE-1 + sections (c) PREDICTION-1, PREDICTION-2, PREDICTION-3, PREDICTION-5.
- Substrate-product reading: validates / refutes "bounded-creative-NLG substrate-only" cap_map row -- i.e., the deterministic + calibrated formulator product surface for kids-story / poetry / structured-narrative.
- Why-now: 1x drill on NL synthesis showed structured-NLG viable; the 2x drill identifies 3 untested paths that could lift substrate from structured-only to bounded-creative. Cheap CPU test, no GPU, no large corpus, reuses primitives already validated this morning (CRF semiring + bigram cleanup + role-binding + stochastic-HD noise-injection).
- Pipeline summary (research-side; exp_dev owns engineering): substrate-stored 200-500 narrative-arc templates + Tier-2 substrate-bundled 4-gram conditional + resonator-network role-filler decode + noise-injected unbinding sampling + trajectory-association token emit + resonator-CFG grammaticality enforcement.
- HARD-PASS: PP / TinyStories-10M-transformer-PP <= 2.0 AND distinct-2 >= 0.40 AND coherence >= 0.60.
- HARD-FAIL: PP-ratio > 4.0 OR distinct-2 < 0.20 OR coherence < 0.30.
- P_deflated: 0.30.

### Anchor 2: PILOT-CREATIVE-2 -- substrate-stochastic-sampling diversity floor (tier hint: Tier-3 SMOKE, CPU-only, 1-2 hours)

- Pointer: research note section (b) PILOT-CREATIVE-2 + section (c) PREDICTION-2.
- Substrate-product reading: validates / refutes the substrate.generation.StochasticSampler primitive (noise-injected unbinding as substrate-side temperature-sampling). Cross-cutting infrastructure -- if PASS, the primitive is reusable across all substrate-generation surfaces.
- Why-now: Stochastic-HD literature directly motivates the mechanism but it has NOT been exercised for generation-diversity. The substrate's robustness-mode noise-injection is the same operator under a different objective. Cheap, mechanistic check; informs PILOT-CREATIVE-1 design.
- HARD-PASS: distinct-2 ratio (substrate vs neural at matched PP) >= 0.70.
- HARD-FAIL: distinct-2 ratio < 0.30 OR PP penalty > 4x greedy.
- P_deflated: 0.45.

### Anchor 3: substrate-CRF beam-search decode on TinyStories (tier hint: Tier-2 PILOT, CPU-only, 4 hours)

- Pointer: research note section (c) PREDICTION-5.
- Substrate-product reading: substrate-native CRF semiring (already validated this morning for structured prediction) used in REVERSE as a generative decoder. Lifts substrate-only TinyStories coherence above greedy 4-gram baseline.
- Why-now: substrate-CRF was just validated at POS-0.906 this morning; same machinery runs in reverse. Composition test.
- HARD-PASS: coherence lift >= 0.10 absolute, PP regression <= 1.2x.
- HARD-FAIL: lift <= 0.03 OR PP regression > 1.5x.
- P_deflated: 0.40.

### Anchor 4 (follow-on if 1-3 PASS): substrate-Kanerva-Machine-style adaptive memory for text (tier hint: Tier-1 DRILL, CPU-only, 1-2 days)

- Pointer: research note section (f) Path 5.
- Substrate-product reading: Kanerva-Machine generative-memory precedent (Omniglot/CIFAR) extended to text. Could lift bounded-creative ceiling further by adding online substrate-memory-update during generation.
- Why-now: HOLD pending Anchors 1-3 outcome. If Anchor 1 PASSES, this is the next push to broaden the substrate-creative surface.

### Anchor 5 (follow-on if 1-3 FAIL): codebook-capacity audit for bounded-creative conditional distribution (tier hint: Tier-1 DRILL, CPU-only, 1 day)

- Pointer: research note section (h) NEXT-DRILL CANDIDATE (failure branch).
- Substrate-product reading: closed-form Marchenko-Pastur bound on substrate-N required for bounded-creative distribution. If N > 1e6, substrate is bounded BELOW TinyStories-10M and the honest-ceiling claim becomes near-unconditional.
- Why-now: HOLD pending Anchors 1-3 outcome.

## Context pointers

- d:/AI/hd-instrument/notes/research_drill_substrate_open_domain_creative_nl_2x_2026-06-11.md (this 2x drill, full theory + capacity math)
- d:/AI/hd-instrument/notes/research_drill_substrate_only_nl_synthesis_2x_2026-06-11.md (1x drill; structured-NLG pilots PILOT-NLG-1 / -2)
- d:/AI/hd-instrument/notes/research_drill_code_synthesis_substrate_feasibility_2x_2026-06-11.md (companion structural-synthesis drill same morning)
- Memory: substrate_only_NL_pos_tagger_validated_2026-06-11 (POS-0.906 substrate-only baseline)
- Memory: substrate_classical_NLP_methods_outperform_phasor_2026-06-11 (substrate-classical NL primitives pattern)
- Memory: substrate_LLM_boundary_decomposition_2026-06-10 (boundary memory now needs 4th revision per this drill)

## Contract

This file is a HAND-OFF: research delivered the path inventory + decisive test + HP/HF thresholds + capacity math. exp_dev OWNS:
- Smoke gate (composition-matched smoke per [[feedback-smoke-test-methodology]]).
- Queue routing (CPU queue; cpu_runner_local or laptop).
- Pre-reg per envelope-fail-bands.
- REMOTE VERIFY post-ship.
- Method-overclaim lift check per [[feedback-method-overclaim-lift-validation]] (verify any rescue methods improve >= 2*SE, not just absolute threshold).

## Autonomy declaration

exp_dev decides experiment design including: which anchor to ship first (recommend Anchor 2 first as cheapest mechanistic check), substrate-N, codebook-size M, template count, sampling temperature schedule, beam-width. Research's role ends at PATH-INVENTORY + THRESHOLDS. Do not parrot research's recipe; design the experiment.
