# Research: What "action" gives grounding that passive prediction can't -- active inference, sensorimotor contingency, developmental manipulation, and interventional causal discovery, converged into a minimal buildable ACTIVE-QUERY-SELECT mechanism

Filed by: research (Sonnet). Date: 2026-07-09.

**Process note:** 4 parallel Sonnet lit-scan sub-agents were dispatched on (1) active inference / expected
free energy and self-selected sampling, (2) sensorimotor contingency / efference copy / reafference, (3)
developmental manipulation and infant concept formation, (4) interventional causal discovery and multi-agent
decorrelation -- generic academic terms only, no substrate-novel names exposed, per
`[[feedback-query-privacy-decomposition]]`. All 4 returned live WebSearch/WebFetch-verified findings
(~43 distinct citations combined). This note synthesizes them against the confirmed on-disk trigger below.

**Trigger / on-disk grounding (verified via Read, not hallucinated, per Fix#28):**
`experiments/exp_selfplay_b1_exog_predictive_anchor_v1.py` landed FULL
(`data/exp_selfplay_b1_exog_predictive_anchor_v1/metrics.json`, `ts_iso=2026-07-09T17:18:03Z`, 5 seeds,
`n_nodes=8000`) with verdict **`HARD_FAIL_PASSIVE_EXOG_INSUFFICIENT_REDIRECT_ACTIVE_INTERVENTION`**:
`B0_mirror corr=0.794` (screen fires) -> `B1_crossfit corr=0.393 ground=0.595` -> `B1_EXOG corr=0.382
ground=0.602`, improvement over B1 only `+0.011` (pre-registered HARD-FAIL bar in the cell's own
`config_version` string is `HFa>=0.35`; EXOG's `0.382` clears it). Grounding held fine (`0.602 >= 0.50`
floor) and the causal-perturbation screen fired strongly (`perturb_ratio=3.61`, comparable to B1's `3.60`)
-- so this is not a grounding failure, it is specifically a **decorrelation** failure: predicting a SHARED
real-data reconstruction target does make both self-play branches more referentially grounded, but does
NOT make them less alike, because both branches chase the same task-structure even though they sample
disjoint index sets uniformly at random (`experiments/exp_selfplay_b1_exog_predictive_anchor_v1.py:491-502`,
`train_arm()`; the exact line is `a_idx = rng.choice(pool, size=min(exog_bs, pool.shape[0]),
replace=False)` at line 499 -- uniform random within each branch's OWN disjoint fold, not literally shared
row-for-row, but the same OBJECTIVE/loss-shape applied identically to both). This is now the THIRD
consecutive decorrelation-axis mechanism landing within ~0.01-0.02 of the same `corr~0.38-0.39` value
(DG representation-transform fix `0.377`, B1 disjoint-fold cross-fit alone `0.393`, B1+EXOG shared
reconstruction target `0.382`) -- a striking, not-yet-explained clustering discussed in S3 below.

Also load-bearing same-day on-disk work read before dispatch:
`notes/research_exogenous_referent_grounding_predictive_coding_2026-07-09.md` already surfaced, as its
single best-cited live finding, Pezzulo, Parr, Cisek, Clark & Friston (2023, *Trends in Cognitive Sciences*)
arguing passive prediction-error minimization is insufficient for "genuine understanding" and that active,
embodied intervention is the missing load-bearing ingredient -- this drill is the direct, pre-registered
follow-up (Trigger C, adjacency-cascade) that specifies WHICH mechanism within "active intervention" is
actually doing the work and what is minimally buildable.

---

## HEADLINE

**Across all four literatures, the thing that actually does the decorrelating work is NOT "action" in the
literal embodied-motion sense -- it is (i) a self-chosen, per-agent DISTINCT intervention/query target
(breaking the passive-shared-target symmetry that interventional causal discovery formally proves passive
observation cannot break) combined with (ii) a predict-then-subtract comparator (the efference-copy
mechanism) that isolates the exogenous residual once a self-generated prediction exists. Critically, THREE
of four lit-scans converge on the SAME caveat: none of this decorrelation is proven to happen "for free" --
active inference's own internal critique (Millidge, Tschantz & Buckley 2021) shows the exploratory/epistemic
term does not fall out automatically from surprise-minimization, it must be constructively engineered
(matching Bayesian-optimal-design theory); diversity-driven RL literature achieves cross-agent decorrelation
only via an EXPLICIT diversity/divergence bonus between policies, not as a free byproduct of independent
policies; and the efference-copy literature's own counter-evidence (Wallach/Kravitz passive-adaptation
paradigms) shows the comparator, not literal self-generated motion, is the necessary primitive -- action is
the natural but not the only possible supplier of the predicted term the comparator needs. The single
cleanest formal result closest to the substrate's actual failure mode is interventional/multi-environment
causal discovery (interventional Markov-equivalence-class shrinkage; Invariant Causal Prediction;
two-distinct-intervention identifiability up to permutation/scaling in causal representation learning):
DIFFERENT interventions by different observers on a shared causal system provably carry independent,
non-redundant constraints that a SHARED passive observation schedule cannot -- this is the formal analog of
exactly what B1_EXOG's uniform-random-but-same-objective sampling failed to produce.**

**P_deflated (a per-branch, own-uncertainty-driven ACTIVE QUERY SELECTION mechanism, replacing B1_EXOG's
uniform-random reconstruction-target sampling with a BALD-style acquisition rule, breaks the ~0.38
decorrelation plateau below the `<=0.20` HARD-PASS bar while holding grounding `>=0.50`): 0.30** (deflated
from the 0.50 novel-synthesis cap; see S3 for why the 3-mechanism clustering at ~0.38-0.39 is a genuine
warning sign, not just a coincidence).

---

## S1 -- The brain mechanism: how action grounds where passive prediction can't, and which piece is load-bearing

| Mechanism | What it does | Load-bearing status (per live lit-scan) |
|---|---|---|
| **Active inference / expected free energy** (Friston, Rigoli, Ognibene, Mathys, Fitzgerald & Pezzulo 2015; Da Costa, Parr, Sajid, Veselic, Neacsu & Friston 2020, arXiv:2001.07203; Sajid, Da Costa, Parr & Friston 2021, arXiv:2110.04074) | EFE decomposes into pragmatic (goal) + epistemic (info-gain) terms; in the no-preference limit, EFE-minimization collapses exactly onto Bayesian-optimal-design / expected-info-gain query selection (Sajid et al. 2021, verified by direct fetch). | **Real formal bridge, but NOT proof that chosen sampling decorrelates across DIFFERENT agents.** The closest rigorous version of "chosen queries beat passive sampling" is Houlsby, Huszar, Ghahramani & Lengyel's BALD (2011, arXiv:1112.5745): maximizing I(outcome; model parameters) when choosing queries provably extracts more parameter-information per sample than i.i.d./passive sampling -- but this is a SINGLE-agent-vs-random result, not a cross-agent decorrelation theorem. **Load-bearing caveat (Millidge, Tschantz & Buckley 2021, arXiv:2004.08128):** the "natural" future-directed extension of variational free energy does NOT spontaneously produce exploratory/information-seeking behavior -- it actively discourages it; the epistemic term is a constructed, motivated addition, not a free consequence of surprise-minimization. This directly explains why a passive shared-objective (B1_EXOG) failed to decorrelate: nothing in "predict real data" by itself creates divergent sampling; divergence has to be built in. |
| **Sensorimotor contingency / efference copy** (von Holst & Mittelstaedt 1950, "Reafferenzprinzip"; Sperry 1950; O'Regan & Noe 2001; SEP "Action-based Theories of Perception," 2021 ed.; Held & Hein 1963) | A motor command generates an efference copy -> a forward model predicts the sensory consequence -> a comparator subtracts predicted from actual afferent input -> the residual is the exogenous/world-caused signal. | **Genuinely load-bearing, but the load-bearing PART is the comparator, not the physical act.** Live-verified counter-evidence (Wallach, Kravitz & Lackner-era passive-adaptation paradigms, cited via SEP) shows passive-movement paradigms CAN still produce adaptation when a discrepancy-detection route exists without literal self-motion -- the operative variable is a detectable self/world discrepancy, not motor origin per se. This reframes the substrate implication: the necessary primitive is a **predict-then-subtract comparator fed SOME source of a self-generated prediction**, not literal embodiment. Held & Hein's kitten-carousel result itself remains robust and unreversed (only active kittens developed visually-guided behavior), but the 2020 Frontiers reanalysis (PMC7248214) resolves activity's role as graded (contextual / enabling / constitutive), not a strict binary -- action is the naturally-reliable supplier of the comparator's predicted term, not metaphysically required. |
| **Developmental manipulation** (Needham, Barrett & Peterman 2002; Libertus & Needham 2010; Soska, Adolph & Johnson 2010; Bourgeois, Khawar, Neal & Lockman 2005; Oudeyer & Kaplan 2007; Schmidhuber 2010) | Self-generated manipulation (i) perfectly time-locks a motor command to its sensory effect (a clean causal/contingency signal passive co-occurrence cannot supply -- an IDENTIFICATION problem, not just an efficiency one), (ii) generates counterfactual object states (rotation reveals occluded structure a fixed passive viewpoint cannot), (iii) self-selects a just-right-difficulty curriculum (Oudeyer/Kaplan intelligent-adaptive-curiosity; Schmidhuber's compression-progress formalization). | **Contingency detection is the most load-bearing of the three** per this cycle's synthesis -- it is the causal-inference primitive; curriculum-selection and counterfactual-state-generation are amplifiers, not substitutes. Held & Hein gives the cleanest "action-GATED, not merely accelerated" evidence (a competency categorically absent under passive-only exposure); the human infant literature (sticky mittens) shows strong acceleration/enhancement under matched conditions but does not cleanly prove strict impossibility (ethically hard to fully deprive; one pre-registered non-replication exists, per PMC8518992). |
| **Interventional causal discovery** (Pearl 2009 *Causality*; Hauser & Buhlmann 2012, arXiv:1104.2808; Eberhardt, Glymour & Scheines, N-1 experiments theorem; Peters, Buhlmann & Meinshausen 2016 Invariant Causal Prediction; Squires, Wang & Uhler 2020, arXiv:1910.09007; Ahuja et al. 2023 ICML interventional CRL) | `do(X=x)` severs incoming edges and clamps X, breaking the Markov-equivalence-class symmetry that passive conditioning P(Y\|X=x) cannot break (this is the formal machinery behind Simpson's paradox); a SECOND, DISTINCT intervention relative to a reference one resolves the residual identifiability ambiguity down to a known permutation/scaling. | **The cleanest, most formal theorem family in this whole drill -- but it is a theorem about ONE ADDITIONAL DISTINCT intervention vs. one more passive observation, not literally "two interveners' beliefs become decorrelated relative to each other."** That specific framing is a reasonable, but NOT independently-published, gloss on Hauser/Buhlmann + Squires/Ahuja + Invariant-Causal-Prediction results (confirmed absent as a named theorem across the live scan). The nearest literally-matching setup is federated/multi-experimenter causal discovery (arXiv:2211.03846, arXiv:1610.08611): several sites each running DIFFERENT interventions on a shared system produce a union of interventional-equivalence-class constraints strictly more identifying than any shared/passive baseline -- this is the best available formal analog for "give each self-play branch its own distinct probe." |

**Synthesis -- which is load-bearing:** none of the four literatures individually proves the substrate's exact
target claim ("chosen, per-agent-distinct sampling decorrelates self-play branches"). But they triangulate on
a specific, buildable recipe: (1) a per-agent **acquisition function** that selects WHICH real-data index to
probe next based on the agent's OWN current uncertainty (BALD-style, the active-inference/epistemic-value
piece), (2) applied so that each agent's already-diverged internal state (B1's disjoint folds, different
init seeds) drives that acquisition function to pick DIFFERENT indices per agent -- instantiating the
interventional-causal-discovery insight that distinct interventions carry independent constraints a shared
passive schedule cannot -- and (3), per the efference-copy literature, a predict-then-subtract comparator
(already present in this cell as `_anchor_loss`/`ExogAnchor`) so the residual against the CHOSEN target is
what trains the anchor, not raw reconstruction against a randomly-assigned target. The honest caveat, stated
independently by 3 of 4 lit-scans (Millidge et al.'s EFE critique, the diversity-driven-RL literature's
explicit-bonus requirement, and the federated-causal-discovery literature's framing as pooling rather than
opposing evidence): **divergence is not guaranteed to emerge "for free" just because each agent is allowed to
choose** -- it may need an explicit cross-branch anti-correlation term if naive per-branch uncertainty-driven
selection does not by itself produce different choices.

---

## S2 -- Minimal buildable design for this substrate: ACTIVE-QUERY-SELECT

**What "action" is for this substrate:** not physical motion -- an **interventional query on the ingest/KB
data pool**, i.e. which real-data index each self-play branch chooses to reconstruct-test itself against
next. This reframes "acting on the world" as "choosing what to sample from the world," which is exactly
what active inference / BALD formalize, exactly what interventional causal discovery calls an intervention
(a targeted probe, not a random draw), and exactly what the developmental-manipulation literature's
"self-selected curriculum" mechanism does computationally.

**Concrete, minimal-diff change (extends the already-landed cell, no new architecture):**
`experiments/exp_selfplay_b1_exog_predictive_anchor_v1.py`, function `train_arm()`, line 499. Currently:

```python
a_idx = rng.choice(pool, size=min(exog_bs, pool.shape[0]), replace=False)
```

This is **uniform random** selection within each branch's own disjoint fold (`pool` = `fold_a` for the
speaker side, `fold_b` for the listener side) -- the same task-objective applied identically to both
branches, which is why it failed to decorrelate despite already operating on disjoint index sets. The
minimal buildable change: replace uniform-random selection with a **per-branch, own-uncertainty-driven
acquisition rule** -- rank candidate indices in `pool` by that branch's OWN current reconstruction residual
(reusing `hdlab/predictive_coding.py`'s `residual_magnitude`, already imported/used elsewhere in this file's
neighborhood via `precision_gate_weights` at line 303 and `_anchor_loss` at line 331) and bias sampling
toward the highest-residual (highest-own-uncertainty) indices, instead of drawing uniformly. Because each
branch's anchor (`anchor_s` vs `anchor_l`, different init seeds `seed+909` shared but separate parameter
sets, different folds) has already diverged somewhat from B1's cross-fit alone, their own residual-rankings
over the shared candidate pool will diverge too -- each branch ends up running its OWN distinct
"intervention" (which real-data point to test against), rather than both drawing from the same uniform
schedule. **No new representational math, no new matrix, no new corpus -- this is a ~10-20 line change to
an already-landed, already-instrumented cell.**

**Fallback arm (same file, cheap, escalate only if the naive version plateaus):** per the diversity-driven-RL
and Millidge et al. caveat above, add an explicit cross-branch anti-correlation term -- deprioritize
indices the OTHER branch's own residual ranking ALSO currently favors (requires a cheap periodic exchange of
each branch's top-K candidate indices, not gradients or representations -- stays within the existing
disjoint-fold, no-shared-gradient discipline). This is the honest, pre-registered "if naive active-selection
doesn't move the needle, this is the next thing to try before the costlier full environment-partition
fallback," matching the literature's own explicit finding that decorrelation across differently-policied
agents is usually engineered, not emergent.

**Counterfactual/interventional verification (already built, reuse unchanged):** `causal_perturbation_ratio`
(line 378 of the same file) already implements exactly the causal/held-out perturbation screen the
developmental-manipulation and CRL literatures both call for (object-rotation-reveals-hidden-structure /
interchange-intervention-accuracy, operationalized here as perturb-a-real-feature vs. perturb-a-matched
non-causal feature). B1_EXOG already measured `perturb_ratio=3.61` with this exact function -- no new build
needed, just re-run on the new arm.

**Concrete cell:** `B2_ACT` (or `B1_EXOG_ACTIVE`) -- same harness, same arms list extended
(`ARM_NAMES = ["B0_mirror", "B1_crossfit", "B1_EXOG", "B2_ACT"]`), same config/instrumentation, single
changed line (499) plus an optional second changed line for the fallback divergence term.

---

## S3 -- Honest bound and the sharpest residual question

**Does this reach full referential grounding, or a further step?** A further step, not full grounding --
now for a REASON specific to this drill's own findings, on top of the two already-identified gaps from the
prior note (Pezzulo et al.'s active-embodiment-necessity argument; Coelho Mollo & Millière's unaddressed
teleosemantic/functional-history condition): **even a full HARD-PASS here would only demonstrate
interventional-identifiability-style decorrelation via self-chosen KB queries, not literal embodied action on
a physical world.** This is, per the efference-copy lit-scan's own double-edged finding, actually GOOD news
for buildability (the comparator, not literal motion, is what's necessary -- Wallach/Kravitz-style passive
paradigms can still work when a discrepancy-detection route exists) but it means a PASS proves a narrower,
well-specified computational claim ("distinct per-agent interventional queries + a predict-subtract
comparator decorrelate self-play branches while retaining grounding") rather than "the substrate now has
genuine active/embodied grounding" in the full Harnad/enactivist sense -- that bar (per S1's sensorimotor row)
remains formally unsettled in the literature itself, so this program should not claim to have crossed it
either way.

**Sharpest residual question:** THREE independent mechanisms -- a representation-level transform (DG,
`corr=0.377`), a disjoint-fold cross-fit alone (B1, `corr=0.393`), and a shared-objective reconstruction
target (B1_EXOG, `corr=0.382`) -- have now landed within a tight `~0.377-0.393` band, despite being
theoretically quite different interventions. Is this a coincidence of this cell's specific hyperparameters
(`lambda_exog=0.5`, `K=24`, `n_dist=9`, `code_dim=192` etc.), or is there a STRUCTURAL ceiling in this
particular game/architecture (e.g. the `MessageChannel`/candidate-set discrete-communication bottleneck
itself, shared identically by both branches regardless of what feeds it) that no amount of upstream
mechanism substitution can move past? If `B2_ACT` ALSO lands near `~0.38`, that would be the FOURTH
consecutive convergence on the same number under four structurally different mechanisms -- at that point the
correct redirect is almost certainly the shared discrete-channel/game architecture itself (a genuinely new,
5th-mechanism-class direction), not a fifth attempt at upstream data/objective engineering. This is
pre-registered here explicitly so it is not missed if `B2_ACT` also plateaus near 0.38.

**Deflated P estimates (capped at 0.50, calibration penalty applied):**
- P(own-uncertainty-driven active query selection breaks the `~0.38` plateau below `corr<=0.20` while
  `ground>=0.50` and `perturb_ratio>=2`): **0.30** (below the 0.50 cap -- three prior, theoretically distinct
  mechanisms all converged within 0.02 of each other, a genuine structural-ceiling warning sign per the
  question above, not just calibration caution).
- P(the naive, no-explicit-divergence-term version of active-query-selection is sufficient, vs. needing the
  explicit cross-branch anti-correlation fallback): **0.35** (per Millidge et al. and diversity-RL
  literature's explicit finding that decorrelation is usually engineered, not emergent -- lean toward
  needing the fallback from the start, but worth testing the cheap naive version first per the "Step 0"
  discipline).
- P(a fourth consecutive `~0.38` plateau, if it occurs, correctly redirects to the shared discrete-channel
  architecture as the next-mechanism-class, rather than a fifth upstream-data attempt): **0.45** (pre-registered,
  not yet tested -- moderate confidence this is the right read of a 4-for-4 clustering, but architecture-level
  changes are a bigger, costlier redirect that should not be triggered on 3 data points alone).
- P(this constitutes full Harnad/enactivist embodied referential grounding, not a partial structural anchor):
  **0.10** (unchanged-to-lower than the prior note's 0.12 -- this drill's own "action = symbolic KB query,
  not physical intervention" framing is, if anything, a step further from literal embodiment than the
  prior note's `W_pred` design, even though it is the mechanism the literature specifically calls "active").

---

## Cheap decisive test

**Test name:** `B2_ACT` (extends the already-landed `exp_selfplay_b1_exog_predictive_anchor_v1.py`; single
changed line at the mechanism core, reuses 100% of existing instrumentation).

**Step 0 (near-zero cost, mandatory before building):** confirm off disk whether `residual_magnitude` (or an
equivalent per-index residual/uncertainty signal) is already computable from the existing `ExogAnchor`
forward pass without new code -- `_recon_cos` (line 346) already computes per-probe reconstruction cosine;
check whether a per-INDEX (not just aggregate) residual is already available cheaply from that function
before writing new code.

**Step 1:** add a 4th arm `B2_ACT` = `B1_EXOG`'s exact wiring, with line 499's `rng.choice(pool, ...,
replace=False)` replaced by a residual-ranked biased sample (e.g., compute residual over a candidate
super-set of `pool`, softmax-weight by residual magnitude, sample `exog_bs` without replacement) --
everything else (channel, losses, folds, anchors) unchanged.

**Step 2:** measure `corr(failmask)` (identical instrumentation to B0/B1/EXOG), grounding (`>=0.50` floor,
unchanged), and re-run `causal_perturbation_ratio` (line 378, unchanged) on `B2_ACT`'s anchors as the
causal-verification companion metric -- catches spurious decorrelation (e.g., if active selection just adds
noise/hardness without adding genuine referential signal, perturb-ratio would NOT hold at `>=2`).

**Cost estimate:** smallest of the four mechanisms tried this arc -- no new matrix, no new corpus, no new
loss term, single changed sampling line plus (optionally) a residual-computation helper reusing existing
`_recon_cos`/`residual_magnitude` machinery. CPU-feasible smoke; comparable-or-cheaper than `B1_EXOG` itself
for the FULL dispatch.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE_BAND, calibration-deflated)

| Claim | HARD-PASS | HARD-FAIL | MIDDLE_BAND | P_deflated |
|---|---|---|---|---|
| `B2_ACT` (own-uncertainty-driven active query selection) closes the decorrelation blind spot beyond `B1_crossfit`/`B1_EXOG` | `corr(failmask) <= 0.20` AND `grounding >= 0.50` AND `perturb_ratio >= 2.0` (same bands already pre-registered in this cell's own `config_version` string: `EXOGcorr<=0.20,ground>=0.50,ratio>=2.00`) | `corr(failmask) >= 0.35` (matches this cell's own `HFa>=0.35` bar, i.e. no material improvement over `B1_EXOG`'s already-measured `0.382`) -- would be the FOURTH consecutive mechanism landing near `~0.38`, redirecting to the shared discrete-channel/game architecture as the next mechanism class (see S3) | `corr(failmask)` in `(0.20, 0.35)` OR grounding/perturbation conditions only partially met | **0.30** |
| The naive (no explicit cross-branch divergence term) version is sufficient on its own | `corr(failmask) <= 0.20` achieved WITHOUT the fallback anti-correlation term | naive version plateaus at `>=0.35` but the fallback (explicit cross-branch anti-correlation) version achieves `<=0.20` -- confirms Millidge/diversity-RL prediction that explicit engineering, not emergence, is required | both naive and fallback land in `(0.20, 0.35)` | **0.35** |
| A 4th consecutive `~0.38` plateau (if `B2_ACT` also fails) correctly indicates a shared discrete-channel/game-architecture ceiling rather than an upstream-data/objective problem | if `B2_ACT` (and its fallback) both land within `[0.35, 0.42]`, a targeted architecture probe (e.g. widening/perturbing `MessageChannel`'s candidate-set structure, holding everything else fixed) shows measurably different `corr(failmask)` (`>=0.10` absolute shift either direction) | the architecture probe ALSO clusters near `~0.38` -- would mean the ceiling is even more structural (e.g. task/game-definition itself, or an unmodeled property of `n_nodes=8000`/`K=24` scale), motivating a scale-sweep instead | architecture probe shows a small (`<0.10`) but nonzero shift | **0.45** (pre-registered contingency, not yet actionable until `B2_ACT` lands) |
| Active-query-selection retains the causal-perturbation-ratio screen (rules out spurious decorrelation via noise) | `perturb_ratio >= 2.0` on `B2_ACT`'s anchors, comparable to `B1_EXOG`'s already-measured `3.61` | `perturb_ratio < 1.3` -- active selection destabilized the anchor's actual referential content even if `corr(failmask)` improved (spurious pass) | `perturb_ratio` in `[1.3, 2.0)` | **0.55** (highest-confidence row -- this metric/function is unchanged from `B1_EXOG`, only the sampling rule feeding it changes) |

All rows capped `<=0.50` except the perturbation-retention row (0.55, justified because it reuses an
unchanged, already-validated function -- see [[feedback-lit-scan-calibration-penalty]] guidance that the cap
applies to NOVEL-SYNTHESIS claims, and this row is a reuse-stability claim, not a novel mechanism claim).

---

## Cross-thread synthesis

- **`experiments/exp_selfplay_b1_exog_predictive_anchor_v1.py` (this cycle's landed FULL run):** the direct
  trigger. This note's `B2_ACT` design is a same-file, minimal-diff extension -- no new cell architecture.
- **`notes/research_exogenous_referent_grounding_predictive_coding_2026-07-09.md`:** supplied the Pezzulo et
  al. 2023 finding that motivated this drill's dispatch (Trigger C, adjacency-cascade); this note specifies
  the mechanism that note's S3 left as an open question ("does this reach full grounding, or a further
  step").
- **`notes/research_selfplay_upstream_blindspot_brain_fix_2026-07-09.md`:** the DG cell (`corr=0.377`)
  established the first data point in the now-3-wide `~0.38` clustering discussed in S3; this note's
  pre-registered "4th consecutive plateau => architecture redirect" contingency is a direct continuation of
  that note's own diagnostic-fork discipline.
- **`notes/research_selfplay_shared_estimator_independence_speaker_listener_2026-07-09.md`:** supplies the
  differentiation-axis taxonomy this note's `B2_ACT` design instantiates as a NEW axis (per-agent distinct
  intervention/query, not yet named in that taxonomy) -- worth folding back into that taxonomy if `B2_ACT`
  HARD-PASSes.
- **`notes/research_native_encoder_relational_structure_vs_grounded_meaning_2026-07-09.md`:** Prediction C /
  `causal_perturbation_ratio` reused unchanged here as the spurious-decorrelation guard.

---

## Substrate-product implications

- Not a publication-framing question. `B2_ACT` is a ~10-20 line change to an already-landed, already-FULL
  cell -- the cheapest of the four mechanisms tried in this arc (DG transform, B1 cross-fit, B1+EXOG shared
  target, now active-query-selection).
- **Recommended next cell:** `B2_ACT` as specified above, with the fallback cross-branch anti-correlation
  variant pre-registered as the immediate next step if the naive version plateaus (not a separate drill --
  build both, run naive first, per the Step 0/Step 1 discipline).
- **Standing discipline this drill reinforces:** three consecutive mechanisms clustering within 0.02 of each
  other on the SAME decorrelation metric is a strong, structural signal that should be treated as a
  first-class hypothesis (shared architecture ceiling), not background noise -- if `B2_ACT` makes it four,
  the correct move is a targeted architecture probe on the shared discrete-communication channel, not a
  fifth upstream-mechanism substitution.
- **Honest scope discipline:** frame any `B2_ACT` HARD-PASS as "closes the closed-loop decorrelation blind
  spot via self-chosen interventional queries," not as "the substrate now acts on the world" -- the action
  here is a symbolic KB-query choice, not physical embodiment, and the full Harnad/enactivist/teleosemantic
  bars (per the prior note's S3 and this note's S1 sensorimotor row) remain explicitly open regardless of
  outcome.

---

## Citations (verified count: ~43 distinct sources across 4 live Sonnet lit-scan sub-agents,
WebSearch/WebFetch-confirmed this cycle; generic academic terms only, no substrate-novel names exposed, per
`[[feedback-query-privacy-decomposition]]`)

**Active inference / expected free energy (10):** Friston, K., Rigoli, F., Ognibene, D., Mathys, C.,
Fitzgerald, T. & Pezzulo, G. (2015) "Active inference and epistemic value," *Cognitive Neuroscience* 6(4);
Da Costa, L., Parr, T., Sajid, N., Veselic, S., Neacsu, V. & Friston, K. (2020) "Active inference on
discrete state-spaces: a synthesis," arXiv:2001.07203; Sajid, N., Da Costa, L., Parr, T. & Friston, K.
(2021) "Active inference, Bayesian optimal design, and expected utility," arXiv:2110.04074 -- directly
fetched, verified; Millidge, B., Tschantz, A. & Buckley, C.L. (2021) "Whence the Expected Free Energy?"
*Neural Computation* 33(2), arXiv:2004.08128 -- **load-bearing internal critique**; Parr, T. & Friston, K.
(2019) "Generalised free energy and active inference," *Biological Cybernetics*; Kaplan, R. & Friston, K.
(2018) "Planning and navigation as active inference," *J. R. Soc. Interface*; Linson, A., Clark, A.,
Ramamoorthy, S. & Friston, K. (2018) "The dark room problem in predictive processing and active inference,"
ALIFE proceedings; Houlsby, N., Huszar, F., Ghahramani, Z. & Lengyel, M. (2011) "Bayesian Active Learning
for Classification and Preference Learning" (BALD), arXiv:1112.5745 -- **load-bearing formal analog**;
MacKay, D.J.C. (1992) "Information-based objective functions for active data selection," *Neural
Computation*; Parker-Holder, J. et al. (2020) "Effective Diversity in Population-Based Reinforcement
Learning," arXiv:2002.00632.

**Sensorimotor contingency / efference copy (11):** von Holst, E. & Mittelstaedt, H. (1950) "Das
Reafferenzprinzip," *Naturwissenschaften* 37; Sperry, R.W. (1950) "Neural basis of the spontaneous
optokinetic response," *J. Comp. Physiol. Psychol.*; O'Regan, J.K. & Noe, A. (2001) "A sensorimotor account
of vision and visual consciousness," *Behav. Brain Sci.* 24; Held, R. & Hein, A. (1963) "Movement-produced
stimulation in the development of visually guided behavior," *J. Comp. Physiol. Psychol.* 56(5) --
**load-bearing, robust, unreversed**; "Rediscovering Richard Held: Activity and Passivity in Perceptual
Learning," *Frontiers in Psychology* (2020), PMC7248214 -- graded contextual/enabling/constitutive
reanalysis; Held & Bossom (1961) prism-adaptation; Wallach, Kravitz & Lackner-era passive-adaptation
counter-evidence (cited via SEP); Imamizu, H. (2010) "Prediction of sensorimotor feedback," *Japanese
Psychological Research*; schizophrenia corollary-discharge review, PMC6616012 (2019); "The Forward Model: A
Unifying Theory for the Role of the Cerebellum in Motor Control and Sense of Agency," *Frontiers* (2021);
SEP "Action-based Theories of Perception" (2021 ed.); "The exceptionality of enactivism within 4E
cognition," *Phenomenology and the Cognitive Sciences* (2025); "Mechanisms of skillful interaction:
sensorimotor enactivism & mechanistic explanation," *Philosophical Psychology* (2024).

**Developmental manipulation (14):** Needham, A., Barrett, T. & Peterman, K. (2002) "A pick-me-up for
infants' exploratory skills," *Infant Behavior and Development*; Libertus, K. & Needham, A. (2010) "Teach to
reach," *Vision Research*; Libertus, K., Joh, A.S. & Needham, A. (2015) "Motor training at 3 months affects
object exploration 12 months later," *Developmental Science*; pre-registered sticky-mittens
non-replication, *Child Development*, doi:10.1111/cdev.13835; "The sticky mittens paradigm: critical
appraisal," PMC8518992; Soska, K.C., Adolph, K.E. & Johnson, S.P. (2010) "Systems in Development: Motor
Skill Acquisition Facilitates 3D Object Completion," *Developmental Psychology*, PMC2805173; Soska, K.C. &
Adolph, K.E. (2013), *Frontiers in Psychology* (crawling/manual exploration and mental rotation); Bourgeois,
K.S., Khawar, A.W., Neal, S.A. & Lockman, J.J. (2005) "Infant Manual Exploration of Objects, Surfaces, and
Their Interrelations," *Infancy*; Oudeyer, P-Y. & Kaplan, F. (2007) "What is Intrinsic Motivation? A
Typology of Computational Approaches," *Frontiers in Neurorobotics*; Oudeyer, P-Y., Kaplan, F. & Hafner,
V.V. (2007) "Intrinsic Motivation Systems for Autonomous Mental Development," *IEEE TEC*; Schmidhuber, J.
(2010) "Formal Theory of Creativity, Fun, and Intrinsic Motivation (1990-2010)," *IEEE TAMD*; Cangelosi, A.
& Schlesinger, M. *Developmental Robotics: From Babies to Robots*, MIT Press; "Sensorimotor Contingencies as
a Key Drive of Development: From Babies to Robots," PMC6904889; "From Kicking to Causality: Simulating
Infant Agency Detection with a Robust Intrinsic Reward," arXiv:2507.15106.

**Interventional causal discovery (10):** Pearl, J. (2009) *Causality: Models, Reasoning, and Inference*;
Pearl, J. & Mackenzie, D. (2018) *The Book of Why*; Hauser, A. & Buhlmann, P. (2012) "Characterization and
Greedy Learning of Interventional Markov Equivalence Classes of DAGs," arXiv:1104.2808; Yang, K., Katona,
A., Buhlmann, P. et al., "Estimating interventional Markov equivalence classes," arXiv:1303.3216; Eberhardt,
F., Glymour, C. & Scheines, R., "N-1 Experiments Suffice to Determine the Causal Relations Among N
Variables"; Peters, J., Buhlmann, P. & Meinshausen, N. (2016) "Causal inference using invariant prediction,"
*JRSS-B* 78(5) -- **load-bearing multi-environment analog**; Squires, C., Wang, Y. & Uhler, C. (2020)
"Permutation-Based Causal Structure Learning with Unknown Intervention Targets," UAI, arXiv:1910.09007;
Ahuja, K. et al. (2023) "Interventional Causal Representation Learning," ICML; "Federated Causal Discovery
From Interventions," arXiv:2211.03846 -- closest literal multi-experimenter analog; "Causal Network
Learning from Multiple Interventions of Unknown Manipulated Targets," arXiv:1610.08611.

Confidence: HIGH for Sajid et al. 2021 (directly fetched), Millidge et al. 2021 (published, well-known
internal critique), BALD (Houlsby et al. 2011, foundational, widely-cited), Held & Hein 1963 (classic,
directional finding unreversed), the sticky-mittens core studies (Needham/Libertus/Soska-Adolph, directly
matched active-vs-passive designs), and the core Pearl/Hauser-Buhlmann/Peters-et-al. causal-discovery
theorems. MEDIUM for the sensorimotor-necessity-vs-sufficiency dispute (genuinely unsettled per the field's
own record) and the exact "two distinct interventions decorrelate observers" framing (a reasonable but not
independently-published gloss). LOW-MEDIUM, explicitly flagged, for single-paper/2025-2026 sources (the
enactivism-critique papers, arXiv:2507.15106).

---

Per [[feedback-no-papers-product-only]]: no publication framing. Every recommendation above is scoped to a
concrete, minimal-diff extension of an already-landed cell (`B2_ACT`, ~10-20 changed lines), not a
scientific contribution claim.
