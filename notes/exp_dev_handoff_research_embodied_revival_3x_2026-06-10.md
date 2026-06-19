# exp_dev hand-off -- research: embodied cognition revival 3x

**Filed:** 2026-06-10 by research sub-agent.

**Trigger:** Research note at `notes/research_drill_embodied_revival_3x_2026-06-10.md` -- embodied cognition 3-stream drill completed. Boundary-probe finding (P=0.55 image-schema codebook, not true embodiment) has been resolved into 8 concrete mechanism proposals with 5 laptop-testable falsifiers. Three proposals have P_deflated >= 0.30 and are ready for empirical test within one exp_dev cycle.

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters for the run.

---

## Anchor candidates (rank-ordered)

### Anchor 1: IMAGE-SCHEMA-ODE (highest priority)

**Anchor pointer:** Section D2.1 of `notes/research_drill_embodied_revival_3x_2026-06-10.md`

**Substrate-product reading:** Image schemas (CONTAINER, PATH, FORCE, BALANCE, LINK, CENTER-PERIPHERY, UP-DOWN) implemented as ODE attractor basins in VSA state space. Test whether substrate geometry supports dynamic schema convergence. This is the decisive test for whether the substrate can implement Johnson's (1987) grounded schemas as attractors rather than static codebook entries. A pass here would be the first demonstration of dynamic schema grounding in a VSA system.

**Tier hint:** LOCAL CPU (N=1024, 200 queries, <2 minutes). No GPU required. Euler integration over VSA state space.

**Why now:** The boundary-probe (P=0.55 static codebook) explicitly identified this as the next gate. The ODE version tests whether the *dynamic* structure is achievable -- the static version is already known to be partial. The test costs ~2 hours total including implementation.

**Pre-registered falsifier bands:**
- HARD-PASS: >80% of in-basin queries converge to correct schema attractor in <50 integration steps
- MIDDLE BAND: 50-80% convergence; indicates N is too small or basin design needs tuning
- HARD-FAIL: <50% convergence OR step divergence in >10% of queries

---

### Anchor 2: ACTIVE-INFERENCE-LITE (second priority)

**Anchor pointer:** Section D2.3 of `notes/research_drill_embodied_revival_3x_2026-06-10.md`

**Substrate-product reading:** Minimal sensorimotor prediction-error loop over substrate embeddings. Implements toy version of Friston FEP: substrate maintains generative model G(s,a)->predicted_o, computes free energy F at each step, selects actions to minimize expected F. Tests whether VSA binding is expressive enough to represent a generative model at toy scale (4 states, 2 actions). Related to prior Friston FEP probe (exp_dev_handoff_research_friston_fep_substrate_2026-06-04.md) -- read that note for prior findings before implementing.

**Tier hint:** LOCAL CPU (N=512, 4-state world, 1000 steps, <1 minute). No GPU required.

**Why now:** If IMAGE-SCHEMA-ODE passes, ACTIVE-INFERENCE-LITE is the natural next test -- it adds the sensorimotor closure loop that schemas alone do not provide. Both tests together would confirm that the substrate has the two core components of embodied cognition (schema structure + sensorimotor loop).

**Pre-registered falsifier bands:**
- HARD-PASS: free energy decreases monotonically for in-distribution sequences; action entropy decreases over 100 steps
- MIDDLE BAND: free energy decreases but noisily; action selection better than random but not clearly improving
- HARD-FAIL: free energy oscillates or increases; action selection indistinguishable from uniform random

---

### Anchor 3: TOOL-EXTENDED-SUBSTRATE (third priority, easiest to implement)

**Anchor pointer:** Section D2.8 of `notes/research_drill_embodied_revival_3x_2026-06-10.md`

**Substrate-product reading:** Maravita-Iriki (2004) body-tool integration in the substrate. Tools dynamically incorporated into body-state vector B(t) during use. Tests whether body-state modulation of retrieval produces the tool-extension effect observed in primates and humans. Easiest implementation: 5-line modification to current retrieval loop. If this passes, it constitutes a substrate analog of one of the most empirically robust body-schema phenomena in the literature.

**Tier hint:** LOCAL CPU (500 items, 10 tools, <30 seconds). Trivial runtime.

**Why now:** Cheapest implementation of the three. Run first if the other two are queued. If it fails, the failure mode (B(t) modulation too weak) informs N choices for the other two tests.

**Pre-registered falsifier bands:**
- HARD-PASS: recall@5 for tool-contextual queries improves >10% with B_extended vs B(t); non-tool queries unchanged
- MIDDLE BAND: delta 5-10%; marginal, needs larger N or stronger beta
- HARD-FAIL: delta <5%, not statistically significant at 500 items

---

### Anchor 4: INTEROCEPTION-AS-PRIOR (fourth priority, lowest implementation cost)

**Anchor pointer:** Section D2.2 of `notes/research_drill_embodied_revival_3x_2026-06-10.md`

**Substrate-product reading:** Running body-state vector B(t) that modulates all queries, updated via exponential decay of retrieval history. Tests whether temporal autocorrelation of B(t) produces measurable drift in query routing distribution. This is the minimal possible embodiment: one additional vector + one update rule. If it fails (routing unchanged), then B(t) modulation is genuinely ineffective at current substrate N and all other body-state proposals are suspect.

**Tier hint:** LOCAL CPU (200 steps, negligible runtime). This should run as a smoke test before committing to the other anchors.

**Pre-registered falsifier bands:**
- HARD-PASS: KL divergence between routing distributions in steps 1-50 vs 151-200 exceeds 0.1 nats; shuffled control KL < 0.02
- MIDDLE BAND: KL 0.02-0.1; weak effect, suggestive but not decisive
- HARD-FAIL: KL indistinguishable from shuffled control (p > 0.1, permutation test)

---

## Context pointers (file paths)

- Research note (primary): `d:/AI/hd-instrument/notes/research_drill_embodied_revival_3x_2026-06-10.md`
- Prior Friston FEP probe: `d:/AI/hd-instrument/notes/exp_dev_handoff_research_friston_fep_substrate_2026-06-04.md`
- Prior small-brain template: `d:/AI/hd-instrument/notes/exp_dev_handoff_research_small_brain_substrate_template_2026-06-04.md`
- Prior biological precedents: `d:/AI/hd-instrument/notes/exp_dev_handoff_research_biological_precedents_animal_scales_2026-06-04.md`
- Prior multimodal primitives: `d:/AI/hd-instrument/notes/exp_dev_handoff_research_multimodal_substrate_primitives_2026-06-04.md`
- Substrate v3.0 compositional cliff note: `d:/AI/hd-instrument/memory/substrate_v3_compositional_cliff_crossed.md`

---

## Contract

Research proposes mechanism + falsifier. Exp_dev designs the implementation, chooses N/seed/threshold, routes to queue, ships, reads verdict. Research does not specify numerical parameters, queue tier, or implementation details.

## Autonomy declaration

exp_dev has full autonomy to: (a) order these anchors differently from the ranking above based on current queue state, (b) combine anchors 3+4 into a single cell (both are trivially fast), (c) reject any anchor if the smoke test fails and refactor before full dispatch, (d) adjust N up or down based on current substrate capacity.
