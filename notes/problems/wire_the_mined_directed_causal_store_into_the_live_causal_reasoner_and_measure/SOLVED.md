---
problem: wire_the_mined_directed_causal_store_into_the_live_causal_reasoner_and_measure
status: REFUTED
bar: "Wire the mined directed causal store into `hdlab/causal_reasoner._graph()` as a default-off structural-prior arm (byte-identical when off/absent), and DELIVER a MEASURED number: does the +0.139 transfer to the reader's OWN extracted-from-prose causal necessity read (on the necessity instrument + held-out simplewiki), with the shuffled-store twin LOSING CI-separated? Plus a coverage-optimization result (Rhea/BioModels or commonsense-corpus scale-up -> the direction/coverage number). OR a rigorous LOCATED NEGATIVE naming exactly why it does not transfer (coverage on prose concepts / the ~0.61 direction cap / link-sparsity), with the number."
result: "RIGOROUS LOCATED NEGATIVE (a full pass per the bar's located-negative provision), plus a disk-outranks-brief correction to the store's OWN +0.139 headline, plus a constructive positive on the read that DOES work. (1) The +0.139 does NOT transfer to the reader's extracted-from-prose necessity read: wired into the live sm.causal_reasoner()._graph() over the reader's actual single-verb-lemma nodes it moves the necessity read +0.0002 (n=5005; the graph is empty -- 2.2 nodes / 0.0 causal edges on process prose, single-lemma store coverage 1.4% vs 12.6% concept). (2) Even with a concept-bound upstream fix (one event node per step bound to its verb+noun concepts), the store's rung-2 reachability does NOT beat a topicality baseline (map_only 0.762 > store 0.743, paired -0.0196) and is inert-to-harmful in direction (undirected 0.759 > directed 0.743; direction-scramble reproduces it) -- because the EFFECT-vs-NO_EFFECT axis is direction-insensitive by construction and reachability over a dense concept set collapses to association. (3) The brief's OWN +0.139 was itself a DENSITY ARTIFACT of the global-shuffle twin (which is ~15x sparser per item: 29.0 vs 2.0 edges): against the honest density-matched twin it is +0.0026 CI[-0.011,0.016], NOT CI-separated. (4) The read that WOULD work -- direction-DISCRIMINATION 2AFC where association is pinned at chance -- the store's direction transfers CI-sep: BCOPA-CE +0.031 CI[0.009,0.053], e-CARE-direction +0.042 CI[0.023,0.061] over the shuffled twin, and fwd beats REVERSE-direction +0.10 on covered pairs; but the gain is SMALL (~0.55 on 2AFC = the ~0.61 intrinsic text-direction ceiling) and coverage buys only ~+0.02-0.03."
floor: "STRONGEST floors actually run, per axis. NECESSITY axis (where the store is claimed to help): the map_only TOPICALITY baseline 0.762 and UNDIRECTED-connectivity 0.759 -- BOTH BEAT the store's directed rung-2 read 0.743 (n=5005). The density-matched topology twin (causal_reasoner's own CausalGraph.shuffled) storeonly-vs-twin +0.0026 (n.s.). DIRECTION axis (where the store does help): shuffled-store twin 0.498-0.499 and REVERSE-direction 0.445-0.473 -- both LOSE to forward direction 0.526-0.541 CI-sep; association/lexical floors pinned at 0.50 by construction on BCOPA-CE."
controls: "DENSITY-MATCHED TOPOLOGY TWIN (CausalGraph.shuffled: same nodes + same edge count, random acyclic rewire) -- excludes the per-item DENSITY artifact that inflated the global-shuffle twin's +0.139/+0.223 (real 29 edges/item vs global-twin 2). UNDIRECTED-CONNECTIVITY ablation -- excludes DIRECTION being load-bearing on the existence axis (undirected >= directed). DIRECTION-SCRAMBLE null (skeleton fixed, orientations randomized) -- excludes direction-CORRECTNESS (the small residual is direction-COHERENCE). MAP_ONLY topicality baseline (effect iff both endpoints appear, no edges) -- excludes the store adding over association/co-occurrence. REVERSE-DIRECTION control (score the store backwards) on the 2AFC -- confirms DIRECTION (not association) is the signal (fwd-rev +0.10 on covered). SHUFFLED-STORE TWIN -- the info-free twin, loses on the 2AFC. Byte-identical-off invariant stated for the proposed wire (default-off flag, lazy)."
files_changed: "experiments/exp_causal_store_wire_transfer_v1.py (the transfer instrument + full control battery), experiments/exp_causal_direction_grounded_intervention_v1.py (THE BIGGER LEVER prototyped: grounded interventional direction-recovery past the ~0.61 text ceiling), experiments/exp_causal_direction_grounded_generalization_v1.py (generalization + brain-comparison: data-efficiency curve, functional forms incl. MI readout, confounder robustness), experiments/exp_causal_direction_active_selection_v1.py (the last lever: active few-shot intervention selection), experiments/exp_grounded_causal_learner_organ_v1.py (GroundedCausalLearner -- the hardened-toward-an-organ unified learner), experiments/exp_causal_store_prior_plus_intervention_v1.py (the store's rehabilitated role: a directional prior bootstrapping intervention), verification/test_causal_store_wire_transfer.py (witness 9/9), verification/test_causal_direction_grounded_intervention.py (witness 5/5), verification/test_grounded_causal_learner_organ.py (witness 5/5), notes/problems/wire_the_mined_directed_causal_store_into_the_live_causal_reasoner_and_measure/{FINDINGS_control_battery.md,SOLVED.md}. NO hdlab write (Q111 -- proposed diff below). Re-ran (read-only) experiments/exp_causal_directional_score_v1.py (the direction anchor)."
reverify: ".venv/Scripts/python.exe verification/test_causal_store_wire_transfer.py && .venv/Scripts/python.exe verification/test_causal_direction_grounded_intervention.py"
---

# Wiring the mined directed causal store into the live causal reasoner -- a located negative that corrects the brief's own premise

**Status: REFUTED (a first-class outcome; the bar makes a numbered located negative a full pass).** The brief's
inferred claim -- that the store's +0.139 transfers to the reader's extracted-from-prose causal necessity read -- is
refuted with numbers, AND the +0.139 headline is itself shown to be a density artifact of the wrong info-free twin.
The refutation is principled (not just an empirical miss) and I went past it to identify + measure the read the store
DOES help (direction discrimination), and to locate the only bigger lever (grounded interventional experience, unbuilt).

## What I built (glass-box, NO external LLM, NO spaCy)
1. **The transfer instrument** (`experiments/exp_causal_store_wire_transfer_v1.py`): builds the necessity graph from the
   reader's OWN extraction (`hdlab.causal_network.build_causal_edges` = the exact `sm.causal_links` mechanism), reads
   necessity as a PURE rung-2 do-simulation (reachability over the graph, no direct-store-edge fallback), and adds the
   mined store's directed edges (`edge_condXasym > thr`) as candidate bypasses -- exactly the register #6 wire spec.
   Arms: live lemma-node (base / +store / +twin), concept-bound step nodes (the upstream fix), and a full CONTROL
   BATTERY (density-matched topotwin, undirected ablation, direction-scramble, map_only, reverse-direction).
2. **The witness** (`verification/test_causal_store_wire_transfer.py`, 9/9): reproduces the located negative + the
   direction positive scaffold-free.
3. Re-ran the direction anchor (`exp_causal_directional_score_v1.py`) + a coverage decomposition probe.

## What I measured (n=5005 WIQA necessity unless noted)
- **LIVE-WIRE transfer = +0.0002.** Into the live `sm.causal_reasoner()._graph()` over the reader's single-verb-lemma
  nodes, the store moves the necessity read +0.0002. WHY, with numbers: the reader extracts 2.2 event nodes / **0.0
  causal edges** on WIQA process prose (6 connectives + a 36-word hard-coded force-dynamics bridge fire on none of it),
  and single-verb-lemma nodes get **1.4%** store coverage vs **12.6%** over concept sets -> store cross-edges attach to
  ~3% of items and change no answer.
- **Concept-bound upstream fix does not rescue it.** Binding each event node to its verb+noun concept set (the phase-
  diagram node-granularity move; the situation-model instantiation the grow-causal chain-trace named MISSING) lifts the
  store's apparent necessity to 0.743, but: it LOSES to a `map_only` topicality baseline (0.762, paired -0.0196), UNDIRECTED
  connectivity beats it (0.759, paired -0.0168), and a direction-scramble reproduces it (+0.005). The EFFECT-vs-NO_EFFECT
  axis is direction-insensitive by construction (both orientations -> EFFECT) and reachability over a dense concept set
  degenerates to undirected connectivity = association.
- **The brief's +0.139 is a density artifact.** The store-only KNOWLEDGE regime (the +0.139 harness) beats the global-
  shuffle twin +0.150/+0.139 ONLY because that twin is ~15x sparser per item (29.0 vs 2.0 edges -- `shuffle_store`
  permutes the effect vocabulary GLOBALLY, so shuffled targets rarely land inside an item's small concept set). Against
  the honest density-matched twin (`CausalGraph.shuffled`), storeonly-vs-twin is **+0.0026 CI[-0.011,0.016], not CI-sep**.
- **The read that WOULD work (direction discrimination).** On BCOPA-CE (association pinned at chance by construction) the
  store's direction beats the shuffled twin **+0.031 CI[0.009,0.053]**; on e-CARE-direction **+0.042 CI[0.023,0.061]**;
  and forward beats REVERSE-direction **+0.10 on covered pairs** -- direction, not association, is the signal. But the
  gain is SMALL: ~0.55 on a 2AFC = the ~0.61 intrinsic single-direction ceiling, and coverage buys only ~+0.02-0.03
  (covered-accuracy 0.553-0.555 ~= overall; coverage scales HOW MANY pairs, not reliability).

## THE BIGGER LEVER, PROTOTYPED FROM EXISTING PARTS (owner: "can you prototype it from these parts and build it?")
The store's asset is DIRECTION, capped at ~0.61 by text. The route past it is grounded INTERVENTION -- built here as
`experiments/exp_causal_direction_grounded_intervention_v1.py` (witness `test_causal_direction_grounded_intervention.py`
5/5), the DIRECTION analogue of the proven SIGN prototype, reusing its grounded micro-world (`make_scm`/`sample`, with a
shared confounder = the topic/script analogue) + `hdlab.causal_reasoner`. The brain's mechanism (Pearl do-operator;
Gopnik blicket-detector covariation learning): orient a->b by the INTERVENTIONAL ASYMMETRY -- |influence of do(a) on b|
vs |do(b) on a| (do(cause) shifts the effect; do(effect) cannot shift the cause).
**MEASURED (150 worlds, 2671 directed pairs):**
- **DIRECTION RECOVERY: grounded intervention 0.993 CI[0.990,0.996]** vs observational text-analog 0.313 (ANM residual
  asymmetry -- at/below chance UNDER THE CONFOUNDER, exactly why text co-occurrence caps out) vs random twin 0.485;
  paired(grounded-obs) **+0.680 CI[0.662,0.698]**, (grounded-twin) **+0.508 CI[0.488,0.528]**, both CI-sep. Grounded
  BEATS the ~0.61 text-store ceiling by **+0.383**.
- **CAUSE SELECTION through the LIVE `causal_reasoner`: grounded-directed graph 0.980** vs observational-directed 0.034
  (paired **+0.946 CI[0.929,0.961]**) -- correct edge orientation lets `ultimate_cause` find the true root; mis-oriented
  observational edges essentially never do. Same undirected skeleton both arms -> DIRECTION is the only difference.
So the mechanism that breaks the wall is real and composes into the existing reasoner: interventional experience
recovers direction (0.99) and lifts cause selection (0.03->0.98) where text/observation (rung-1, confounded) cannot.

**GENERALIZATION + PERFORMANCE VS THE BRAIN** (`exp_causal_direction_grounded_generalization_v1.py`):
- **DATA EFFICIENCY (the brain axis -- few-shot):** accuracy by #interventions = {3:0.66, 5:0.75, 10:0.85, 25:0.93,
  100:0.98}. Clears the 0.61 text ceiling from **3 interventions**; human-level 0.90 at **~25**. At the brain's few-shot
  budget (~10; Gopnik toddlers / Bramley 2017 adults) we are at **0.85** -- already past text's whole-corpus ceiling.
- **FUNCTIONAL FORM:** linear 0.978, monotone-nonlinear tanh **0.915** (generalizes); NON-monotone quad degrades the
  signed-cov readout to 0.688, a magnitude/dependence readout recovers 0.765 -- a NAMED residual (non-monotone couplings
  need a richer dependence measure, e.g. mutual information / distance correlation).
- **CONFOUNDER robustness:** grounded holds 0.99->0.81 as confounder strength 0->4x (which drives observation far below
  chance) -- intervention breaks confounding by construction.
- **VS THE BRAIN, honestly:** brain-COMPETITIVE on direction (0.85-0.93 few-shot, robust).

**THE LAST LEVER -- ACTIVE SELECTION + THE ORGAN (built this submission; owner: "prototype the last lever, harden to an
organ, right not easy"):**
- **ACTIVE intervention selection** (`exp_causal_direction_active_selection_v1.py`; Bramley 2017 / Coenen 2015 info-greedy
  ~= minimum vertex cover, since one do(node) orients every incident edge): reaches **0.90 edge-orientation in 5
  interventions** (the brain few-shot band ~<=10) while RANDOM plateaus ~0.71 and NEVER reaches 0.90. So the data-efficiency
  gap to the brain is CLOSED by choosing informative interventions -- not by more data.
- **NON-MONOTONE generalization CLOSED:** the mutual-information interventional readout orients ANY functional form --
  quadratic (non-monotone) 0.688 (signed-cov) -> **0.930 (MI)**.
- **THE ORGAN** (`exp_grounded_causal_learner_organ_v1.py`, `GroundedCausalLearner`, witness 5/5): unifies interventional
  direction+sign (MI readout) + active few-shot selection + Rescorla-Wagner ONLINE PLASTIC update + `to_causal_graph()`
  composition into `causal_reasoner`. MEASURED: **4.9 active interventions**, direction **0.86**, cause-selection 0.70
  through the reasoner, online refresh does not degrade (plastic). BF STATUS: **BF_SPIRIT** (operation PINNED -- Pearl
  do-operator / Gopnik covariation / Bramley active / Rescorla-Wagner; OUR-INVENTION-UNDER-TEST -- the MI readout + greedy
  selection heuristic; input = micro-world stand-in). Raise to BF when the grounding bridge feeds real grounded/simulated
  experience AND the audit verifies it -- NOT before (mislabelling is barred).
HONEST BOUND: this is a grounded MICRO-WORLD (the substrate has no embodiment). The remaining real gap -- and it is the
large one -- is the GROUNDING BRIDGE: mapping narrative quantities to a grounded dynamical model so intervention is
*available* at read-time. That bridge is the generative world-model main event, not a store-wire; this cell proves the
downstream mechanism is ready for it.

## THE STORE'S REHABILITATED ROLE -- a directional PRIOR that bootstraps intervention (constructive, this submission)
The store is refuted as a SCORER, but its correct brain-foundational role is a testimony-derived directional PRIOR
(Harris-Koenig 2006) that bootstraps grounded intervention (Gopnik/Bramley: learners carry priors and refine them by
intervention). MEASURED (`exp_causal_store_prior_plus_intervention_v1.py`, a prior calibrated to the store's 0.61
direction accuracy + active few-shot intervention):
- **HEAD START at 0 interventions +0.118** (0.61 vs 0.49 no-prior); lifts the whole low-budget curve (1 int: 0.74 vs
  0.67; 2: 0.82 vs 0.78; 3: 0.88 vs 0.85).
- **But saves 0 interventions to 0.90** (both reach it at 4) -- grounded intervention is efficient enough to overtake
  the prior, whose edge WASHES OUT by ~4 interventions.
So the store's value is REAL but FRONT-LOADED: it matters in the ZERO-to-FEW-intervention regime -- which IS the reading
regime (a reader gets only a handful of simulated interventions per narrative event). The brain's testimony+intervention
combination; the store is the prior, grounded intervention the refinement.

## THE FULL-STACK-UPSTREAM TRACE (owner directive: trace where the signal is lost, and whether upstream is BF)
The END component (rung-2 do-sim necessity, `causal_reasoner`, BF_SPIRIT-verified) is sound. Its INPUT signal is lost
at three upstream points, all MEASURED:
1. **Event detection** (`temporal_model.extract_events`, tense-gated, on the NOT_BF frozen `pos_tagger`): 2.2 events/item
   on present-tense process prose -> almost no nodes.
2. **Causal-link extraction** (`hdlab.causal_network`): 6 connectives + a **36-word hard-coded FORCE_ACTION/RESULT_STATE
   bridge lexicon** (fires only on physical-accident prose) + adjacency fallback -> **0.0 edges** on unmarked process
   prose. That hand-curated lexicon is the NON-BF cheap stand-in for the brain's vast causal-testimony knowledge.
3. **Node granularity** (single verb lemma): 1.4% store coverage vs 12.6% concept -> even a perfect store can't attach.
The brief's implied fix -- the store REPLACES the 36-word bridge as the candidate-edge source (Harris-Koenig testimony)
-- is brain-foundational in spirit, and I built + measured it. But it does not rescue the NECESSITY read, because that
read is the wrong axis for the store's asset (direction). Fixing the upstream extraction would let the store DENSIFY the
graph, but densification helps only a direction-sensitive read, not the existence axis.

## Why this is principled, not a one-off miss
Corrected from the CHT framing (research-verified): the Causal Hierarchy Theorem does NOT say reachability is rung-1;
it says the opposite (rungs don't collapse generically). The collapse here is TASK/TOPOLOGY-specific: "is there any
effect" is a coarsened rung-2 query that maps both orientations to one label (direction-insensitive by construction),
and forward-reachability over a small dense concept set degenerates to undirected connectivity. So a directed causal
source cannot beat an association baseline on this axis; its direction content is exercised ONLY by direction-
discrimination. This exactly reproduces the grow_the_causal_mechanism SOLVED's four prior WIQA rung-2 negatives.

## What I did NOT establish (withdraw-first if wrong)
1. I would withdraw first any claim that the store is a LARGE live lever anywhere. The direction positive is real and
   CI-separated but small (~+0.03-0.04 on 2AFC, at the intrinsic ceiling).
2. I did NOT run the LIVE `SituationReader().read()` per WIQA item at full scale for the transfer arm (I used
   `causal_network.build_causal_edges` = the identical extraction mechanism behind `sm.causal_links`, plus a small-sample
   live-reader probe confirming the empty-graph result). The +0.0002 is over the exact live extraction rule.
3. I did NOT test store-densified MULTI-HOP cause SELECTION on a position-controlled prose gold at scale (TellMeWhy
   non-adjacent) -- the grow SOLVED already found TMW position-confounded and the store at chance there; a clean
   multi-hop selection gold does not exist. Flagged as a candidate follow-on, not claimed.

## KEY REALIZATIONS
1. **The surprising "+0.22 store transfer" was two stacked confounds, not a result.** (a) The global-shuffle twin is
   ~15x sparser per item (a per-item DENSITY artifact); against a density-matched twin the gap falls to +0.13. (b) The
   residual is a topicality baseline: `map_only` (predict effect iff both concepts appear, NO edges) scores 0.762 >
   store 0.743. The enabling move was building the causal_reasoner's OWN `CausalGraph.shuffled` (density-matched) twin
   and the map_only degenerate -- the global vocab-permutation twin is the WRONG null for a per-item edged graph.
2. **The brief's own +0.139 headline did not survive its own honest twin** (+0.0026 n.s.) -- the disk outranked the brief
   on the number the brief was built on.
3. **The store's asset is DIRECTION, and the necessity axis never uses it.** Undirected connectivity >= directed
   reachability on the existence axis; scoring the store BACKWARD drops it below chance on a 2AFC. The right instrument
   is a direction-discrimination 2AFC where association is pinned at chance by construction.
4. **We are AT the intrinsic text-direction ceiling (~0.55 on 2AFC / ~0.61 single).** Coverage scales how many pairs are
   answered, not reliability; the only route past ~0.61 is grounded interventional experience, which the substrate has
   only as an experiments/ prototype.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md + KNOWLEDGE_ASSET_REGISTER #6)
- **KNOWLEDGE_ASSET_REGISTER #6 (`store_v1.json`):** the "+0.139 CI-sep" figure should be CAVEATED as an artifact of the
  global-shuffle twin; against a density-matched twin it is +0.0026 (n.s.). The store's LOAD-BEARING, twin-losing win is
  on the DIRECTION-discrimination axis (BCOPA-CE +0.031, e-CARE +0.042 CI-sep), NOT the necessity/existence axis. Its
  correct live role is a rung-1.5 DIRECTIONAL prior, not a necessity/reachability prior.
- **`hdlab.causal_network` (BF_SPIRIT):** the BRIDGING mechanism is a 36-word hard-coded FORCE_ACTION/RESULT_STATE
  lexicon that fires on ~none of modern process/unmarked prose -> `sm.causal_links` is empty there. This is a NON-BF
  cheap stand-in for causal-testimony knowledge; it is the primary reason the reasoner has nothing to walk. Candidate
  upstream fix (its own problem): replace with a mined/learned causal-edge source, but NOT into `sm.causal_links` (the
  connective causal QA gold IS the positional rule; a plausibility selector there regresses -0.2079 -- already located).
- **`causal_reasoner` necessity read:** confirmed BF_SPIRIT (rung-2 do-surgery); the residual is that it reasons over a
  DISCRETE extracted graph, and on the existence axis reachability = association (not a defect of the reasoner -- a
  property of the axis).

## PROPOSED hdlab CHANGE (Q111 -- strategy lands; NOT landed here)
The brief's literal wire (store bypass edges into `_graph()` as a necessity prior) is measured INERT-to-noisy and should
NOT be landed as such -- it is an AS-DURABLE-NEGATIVE. If the store is wired live at all, wire its PROVEN asset:
1. **`sm.causal_direction(a, b)`** -- a default-off read (`CAPABILITY_FLAGS`, lazy, byte-identical off) returning the
   store's directed score `edge_condXasym(store, a, b)` vs its reverse, over the reader's extracted concepts. This is the
   rung-1.5 directional prior that is CI-sep on direction-discrimination.
2. **`board_causal_direction_dimension`** (reuse `exp_causal_directional_score_v1` on BCOPA-CE/e-CARE) -- the store's win
   is board-invisible; a board-invisible proven win needs its own instrument-arm. Gate it on the density-matched twin
   AND the reverse-direction control (NOT the global-shuffle twin).
3. Do NOT add the store to `sm.causal_links` (regresses the connective causal QA) and do NOT wire it as a necessity/
   reachability prior (inert). Byte-identical-off invariant: both reads behind default-off flags, lazy-built.

## SUBSTRATE INCORPORATION MANIFEST
- **INCORPORATE:** `sm.causal_direction` (the rung-1.5 directional prior, default-off) + `board_causal_direction_dimension`
  gated on the density-matched twin + reverse-direction control. The transfer instrument + control battery as the
  reusable causal-graph twin methodology (density-matched `CausalGraph.shuffled` + map_only + undirected + reverse-dir).
  THE GROUNDED-INTERVENTION DIRECTION prototype (`exp_causal_direction_grounded_intervention_v1.py`) -- the proven
  mechanism (0.993 direction, cause-selection 0.03->0.98 through causal_reasoner) for the direction source past the text
  ceiling; promote alongside the grounded SIGN prototype into a grounded-causal-learning organ.
- **AS-DURABLE-NEGATIVE:** the store as a NECESSITY/reachability prior into `_graph()` (inert, +0.0002 live / loses to
  topicality). The +0.139 headline against the global-shuffle twin (density artifact). The global vocabulary-permutation
  twin as the null for a per-item edged graph (wrong null -- changes per-item density).
- **DO-NOT:** re-run the store on the WIQA necessity/existence axis; ingest encyclopedic corpora for coverage (the disk:
  98% of misses are commonsense/procedural link-sparsity); expect a big lever from text-mined direction (~0.61 capped).

## ADJACENT COMPONENTS / CROSS-SOLUTION MAP inputs
- **CONSUMED INPUTS:** `hdlab.causal_network` (the causal-link extractor), `temporal_model.extract_events` (event
  detection), `pos_tagger` (the frozen parse spine), `edge_condXasym`/`store_v1.json`.
- **FLAGGED UPSTREAM WALLS (reopen these when they improve):** (1) `causal_network`'s 36-word hard-coded bridge lexicon
  (unmarked-causation extraction is empty on modern prose); (2) `pos_tagger`/`extract_events` (tense-gated, under-fires
  on present-tense process prose); (3) THE BIGGER LEVER -- grounded interventional experience: NO landed organ; the only
  artifact is the PROVEN prototype `experiments/exp_causal_sign_grounded_ddyn_v1.py` (grounded Delta-Delta 0.999 vs text
  0.745), blocked on the "grounding bridge" (map narrative quantities -> a grounded dynamical model) = the generative
  world-model main event. That is where causal direction/sign past the ~0.61 text ceiling lives.

---

## TLDR (plain English)
We had a big table of "X causes Y" facts mined from language, and a lab result saying it helps the reader tell a real
cause from a coincidence by 0.139. This problem was to plug it into the live reader and see if that gain shows up on
real reading. It does not -- and the deeper finding is that the original 0.139 was mostly a measurement mistake: the
"scrambled" comparison it was measured against accidentally had ~15x fewer connections, so beating it mostly proved
"more connections win," not "smarter knowledge wins." When we use a fair comparison with the same number of
connections, the gain is basically zero. The reason is that the reader's test only asks "is there any effect at all?",
and that question doesn't care which way the arrow points -- so the one genuinely useful thing this table knows (the
direction of causation) is never used. On a fair, different test that DOES ask about direction ("does A cause B or B
cause A?"), the table genuinely helps -- but only a little (about 3-4 points), because language itself can only pin down
causal direction about 61% of the time no matter how much we mine. Getting past that needs a different kind of knowledge
-- learning cause and effect by watching what happens when you change things -- which we have only as a small
proof-of-concept, not a built part of the reader.

## QUESTIONS
None blocking. One decision for the strategy session at integration: whether to land `sm.causal_direction` +
`board_causal_direction_dimension` now (the store's small-but-real, twin-losing directional prior gets a live consumer +
a board arm), or leave the store LATENT until the grounded-interventional program raises direction past ~0.61. My
recommendation: land the direction read + board arm (the win is real, bankable and currently board-invisible), and do
NOT land the necessity-prior wire (measured inert).

## NEXT STEPS
1. **Land `sm.causal_direction` + `board_causal_direction_dimension`** (Q111, strategy) -- the store's proven directional
   prior, gated on the density-matched twin + reverse-direction control. Do NOT land the necessity-prior wire.
2. **Fix the upstream causal-link extractor** (its own problem): the 36-word hard-coded bridge lexicon yields empty
   `sm.causal_links` on modern unmarked prose -> the reasoner has nothing to walk. A learned/mined unmarked-causation
   edge source, kept OUT of `sm.causal_links` (into the reasoner graph only), is the brain-foundational replacement.
3. **Coverage (small lever, disk-prescribed):** ingest COMMONSENSE/PROCEDURAL/how-to corpora (NOT encyclopedic, NOT Rhea
   -- Rhea is the SIGN channel's corpus) to raise direction coverage; measured headroom only ~+0.02-0.03.
4. **THE BIGGER LEVER (the main event) -- PROTOTYPED + HARDENED (this submission):** grounded interventional DIRECTION
   (0.993, +0.383 over the text ceiling; cause-selection 0.03->0.98 through causal_reasoner), generalized (MI readout for
   any functional form; robust to confounding), made FEW-SHOT (active selection 0.90 in ~5 interventions), and unified
   into `GroundedCausalLearner` (organ prototype, plastic, BF_SPIRIT). Remaining: the GROUNDING BRIDGE -- concrete
   handoff-ready design in `BRIDGE_DESIGN_next_problem.md` (science-slice-first via `causal_sign_channel`'s formal-model
   dynamics, then the general bridge = the meaning-channel-gated main event), then LAND `GroundedCausalLearner` as
   `hdlab/grounded_causal_learner.py` (Q111) once the bridge feeds real experience -> raise BF_SPIRIT to BF.
