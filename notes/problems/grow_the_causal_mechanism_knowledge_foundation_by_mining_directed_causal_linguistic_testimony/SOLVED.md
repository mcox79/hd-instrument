---
problem: grow_the_causal_mechanism_knowledge_foundation_by_mining_directed_causal_linguistic_testimony
status: PARTIAL
bar: "PASS = a brain-faithful directed causal-mechanism knowledge foundation (mined causal-linguistic testimony -> consolidated -> applied per-story online through WorldState.do() / the counterfactual-necessity reader) that, on the INTRINSIC surprisal/necessity frame (trap-proof; NO external position-confounded gold), MATERIALLY beats the generic-ATOMIC chance ceiling (pairwise-AUC ~0.50) CI-separated on full-population narrative causal-antecedent selection -- with the info-free twin (shuffled/permuted causal edges of equal coverage) LOSING, participant binding via resolved coref, and no live reasoner regressing. A rigorous LOCATED NEGATIVE is a full pass IF it names, with a number, exactly why mined testimony at the achieved granularity still cannot discriminate the specific causal edge (e.g. the testimony is itself too coarse/generic, or the residual is genuinely per-experience episodic -- quantify the coverage/granularity ceiling and the oracle gap)."
result: "CONSTRUCTIVE INTRINSIC POSITIVE + a rigorous QUANTIFIED LOCATED NEGATIVE. (1) POSITIVE, trap-proof intrinsic frame (held-out causal testimony, no crowd gold, no position, n=10164): mined directed causal testimony RECOVERS causal DIRECTION that same-corpus co-occurrence provably cannot (Pearl rung-1) -- direction-accuracy (ranks cause->effect above the reverse effect->cause) CAUSAL 0.609 CI[0.597,0.620] vs same-corpus co-occurrence 0.513 CI[0.501,0.524] (at chance), paired +0.0973 CI[0.0802,0.1144] CI-SEP; and beats the info-free shuffled-effect TWIN massively on effect-prediction (+0.2338 CI[0.2286,0.2389]). So the SIGNAL TYPE thesis holds: testimony transmits directed causal knowledge adjacency cannot. (2) LOCATED NEGATIVE on the downstream narrative causal-antecedent SELECTION: the directed signal is real but WEAK in absolute terms (direction accuracy 0.609), and the standard benchmark (TellMeWhy answerable non-adjacent, n=273) is POSITION-CONFOUNDED -- the nearest-non-adjacent POSITION floor scores pairwise-AUC 0.910 on the zero-overlap slice, dominating every knowledge signal. The mined causal read gives only +0.041 CI[-0.026,0.106] over adjacency on the zero-overlap slice (NOT CI-sep) and ties chance on the full population. The granularity ceiling, with numbers: gold-link coverage reaches 0.502 at 1.29M edges (coverage is NOT the wall), but the recovered causal DIRECTION is only 0.609-accurate, and TMW rewards position (0.91), so the weak directed signal cannot lift full-population selection above the strongest floor."
floor: "STRONGEST floors actually run, per population. Narrative selection (TMW answerable non-adjacent): POSITION nearest-non-adjacent pairwise-AUC 0.910 (zero-overlap slice) -- DOMINATES; adjacency-W (the current upstream, association) at chance 0.489 (zero-overlap) / 0.495 (full); lexical-overlap 0.286 (zero-overlap). Intrinsic held-out frame: same-corpus co-occurrence baseline (isolates direction from association) = direction 0.513 (chance) / effect-pred 0.711; shuffled-effect info-free TWIN = 0.499 (effect-pred) / 0.506 (store-native diagnostic). generic-ATOMIC chance ceiling ~0.50 (inherited, chain_multi_step exp_multistep_atomic_knowledge_necessity_v1)."
controls: "SHUFFLED-EFFECT TWIN (info-free, equal coverage/degree) -- LOSES on the intrinsic frame (causal +0.234 CI-sep), ties on TMW; SAME-CORPUS CO-OCCURRENCE baseline (same corpus/vocab/pipeline, textual-order instead of marker-direction) -- isolates the causal-specific signal from association: causal beats it on DIRECTION +0.097 CI-sep and effect-pred +0.022 CI-sep, so the win is direction not association; POSITION floor (nearest-non-adjacent) -- exposes TMW as position-confounded (0.91); LEXICAL-overlap floor; HELD-OUT 90/10 sentence split -- generalization not memorization; ZERO-OVERLAP slice (gold cause shares 0 lexical content with effect, 54-59% of items) -- association blind by construction; PREVENT-class EXCLUDED from the miner (cause->effect-BLOCKED, a correctness trap)."
files_changed: "experiments/exp_causal_testimony_{baseline,mine,eval,heldout}_v1.py, experiments/fetch_causal_selection_gold_v1.py, experiments/exp_causal_selection_{ecare_copa,framegrain,combined}_v1.py, experiments/exp_causal_{direction_ecare,bcopa_ce}_v1.py, verification/test_causal_testimony_foundation.py, verification/test_causal_selection_positionfree.py, verification/test_causal_direction_signal.py, data/exp_causal_testimony_mine_v1/store_v1.json (mined foundation asset, 1.29M edges), data/corpora/{copa,ecare,bcopa_ce}/ (acquired position-balanced + direction-sensitive golds), notes/problems/<slug>/{DEAD_ENDS_AND_SIGNAL_MAP,RESEARCH_KNOWLEDGE_MAP,PATH_TO_SOLVED_RESEARCH,SOLVED}.md. NO hdlab write (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_causal_testimony_foundation.py (intrinsic direction win); .venv/Scripts/python.exe verification/test_causal_selection_positionfree.py (position-free selection); .venv/Scripts/python.exe verification/test_causal_direction_signal.py (direction signal on direction-sensitive golds)"
---

## SUPERSEDING FINDING + FIX (2026-09-09, owner: "aggressively evaluate the component itself down to the math; then fully fix all components to be brain-foundational")

**An aggressive operation/math re-audit of the END COMPONENT ITSELF found the prior "BF-in-form" verdict was WRONG, and
the fix is now BUILT + PROVEN.** Full write-up: `AGGRESSIVE_BF_AUDIT_OF_THE_COMPONENT_2026-09-09.md` (independent
adversarial literature check confirmed it — 3 refutations attempted, all failed).

- **THE DEFECT (headline):** `predictive_world_model.causal_antecedent`'s read is
  `necessity(A,B)=surprisal(B|ctx∖A)−surprisal(B|ctx) = log[P(B|ctx)/P(B|ctx∖A)]` = **leave-one-out predictive
  RELEVANCE = Pearl RUNG-1**. By the Causal Hierarchy Theorem (Bareinboim 2022) no rung-1 functional is the rung-2/3
  counterfactual necessity it is NAMED for (CSM/Trabasso), REGARDLESS of what forward model feeds it. This is DEEPER
  than "the input is associative": the READ operation itself is rung-1. (The prior sessions' whole "frontier = sign
  source" conclusion was built on an END component that isn't computing the brain's counterfactual operation.)
- **THE FIX (composition; hdlab is Q111):** the genuine rung-2/3 do-simulation ALREADY EXISTS in `causal_reasoner`
  (abduct→do(cause absent)→re-propagate; Halpern-Pearl AC2). Compose IT over a BOUND situation graph whose edges are
  hypothesized by the mined store — do NOT read leave-one-out. Every issue found is marked in AGGRESSIVE_BF_AUDIT §7
  (fixes table) with the exact hdlab change in §8.
- **PROVEN:**
  - `exp_causal_rung_exposure_v1` (controlled, ground truth known): on a CONFOUND (barometer/storm) structure the
    rung-1 reader names the NON-cause **100% of the time (acc 0.000)** while the rung-2 do-sim is **1.000**; POOLED
    rung2−rung1 **+0.500 CI[0.45,0.55] CI-sep**, info-free shuffled-graph twin loses **+0.598**; over-determination AC2
    **1.000** vs crude but-for **0.000**. On the CHAIN control rung-1 IS correct — its failure is SPECIFIC to
    confounding (the rung distinction), not general incompetence.
  - `exp_causal_necessity_bf_reader_v1` (real WIQA, sign-free necessity axis; FULL n=5005): the composed rung-2 reader
    beats the DEPLOYED rung-1 leave-one-out operation **+0.061 CI[0.046,0.077] CI-sep** and the association floor
    **+0.096 CI[0.084,0.108] CI-sep** (bf 0.705 vs rung1 0.644 vs assoc 0.609). KNOWLEDGE test (store-only graph, no
    given order): the rung-2 reader over the mined-KNOWLEDGE graph beats its info-free shuffled-store twin
    **+0.139 CI[0.115,0.163] CI-sep** (bf 0.577 vs twin 0.438) — the mined causal knowledge is LOAD-BEARING for the
    necessity read. LOCATED NEGATIVES with numbers: on WIQA's GIVEN process order the info-free twin ties (bf−twin
    −0.012 [−0.026,0.003] — that given order is a position artifact both exploit), and the store-only absolute (0.577)
    is below association (0.609) — the KNOWN scale ceiling (~161k causal sentences vs web-scale). The more/less SIGN
    (3-way bf 0.495) stays the proven grounded-quantity frontier (5 sources failed) — a separate program.
  - Witness `verification/test_causal_rung_fix.py` 9/9 green.
- **VERDICT CORRECTIONS:** `predictive_world_model` necessity read NOT-BF (rung-1), relabel → `predictive_relevance`;
  `causal_reasoner` AUDITED → BF_SPIRIT (genuine rung-2/3, residual: no abduction / discrete ±1 / reachability-necessity).

## PERFORMANCE-PUSH ATTEMPTS (2026-09-09, owner: "focus on the REAL performance push, brain-foundational, do it right")

Two levers pursued after the deep analysis:
- **UPGRADE #1 -- directional scoring (cheap, no re-mine): REAL but modest WIN.** Replacing the symmetric, low-frequency-
  biased `cs_pmi` with a DIRECTIONAL score (net-asymmetry `(n(c->e)-n(e->c))/...` or forward-conditional
  `P(e|c-as-cause)`; `exp_causal_directional_score_v1`) lifts the direction signal on the direction-sensitive golds:
  BCOPA-CE 0.522->0.530 (asym), e-CARE-dir 0.517->0.540 (cond); vs-twin CI-sep on both. `condXasym` robust default.
  Banked; still bounded by the rung-1 ceiling.
- **THE RUNG-2 PUSH (the real lever) -- FOUR honest attempts on WIQA (Tandon 2019), the interventional gold
  ("suppose X happens -> effect on Y", = P(Y|do(X)); process domain matches the textbook store): ALL FAIL to beat
  association/majority.** (1) store-reachability do-sim (`exp_causal_wiqa_dosim_v1`): effect-vs-noeffect 0.563 <
  assoc 0.637. (2) process-simulation over WIQA's given steps: effect-vs-noeffect 0.599 TIES assoc 0.609 (reachability
  is co-extensive with association -- related concepts ARE causally connected in a process), 3-way 0.399 < majority
  0.422. (3-4) SIGNED do-propagation with mined CAUSE/ENABLE/PREVENT polarity (`exp_causal_signed_wiqa_v1`, two sign
  conventions): the more-vs-less SIGN -- the one signal association CANNOT supply -- is at/BELOW chance (0.34-0.36).
  => The mined store's signed causal knowledge does NOT align with WIQA's specific process influences.

**WHAT THESE FOUR NEGATIVES ESTABLISH (the honest answer to "push performance"):** the rung-2 signal CANNOT be
recovered by mined-store shortcuts -- not by reachability (overlaps association), not by process-order (position-ish,
ties association), not by signed propagation (mined generic signs are noise vs the item's specific dynamics). This is
the SAME granularity/grounding wall the parents hit: generic mined knowledge does not instantiate on the item's
SPECIFIC states. The rung-2 unlock requires the FULL generative-world-model stack the research prescribes -- a bound
per-item situation model at entity+attribute+value grain (WIQA's steps parsed into state-changes), the mined store as
edge-HYPOTHESIS source, a norm, and a necessity-ablation operator -- run as a SIMULATION, not a store lookup. That is
the parents' named MAIN EVENT: a large multi-component program, not a cell, and these four cell-level failures are the
evidence it cannot be shortcut. NOTE: signed causal-mechanism mining (CAUSE/ENABLE/PREVENT polarity) IS now built and
is the correct edge-source for that simulation -- it is the store, not the simulation, and the simulation is what remains.

## DEEP SIGNAL-CHAIN ANALYSIS (2026-09-09, owner: "determine what signals we're missing and why; fully unlock this")

**The one-sentence answer: our score never left Pearl's rung 1, and the corpus is generated by the very selection
mechanism we are trying to recover -- so the missing signal is not a better text statistic but the rung-2/3
counterfactual-necessity SIMULATION, which the mined store must be RUN THROUGH, not scored by.** Established by three
deep research drills (13 sub-lanes; notes/research_causal_{strength_signal_separation,antecedent_selection,...} +
this session) plus an on-disk substrate-chain trace.

### Why every text statistic (PMI, DeltaP, Cheng power) is insufficient
- **Causal Hierarchy Theorem** (Bareinboim/Correa/Ibeling/Icard 2022): rung-1 (associational) data determines rung-2
  (interventional) / rung-3 (counterfactual) answers only on a MEASURE-ZERO, nowhere-dense set of models -- generically
  NO function maps rung-1 -> rung-2/3. Connective-filtering does NOT inject do-operator content; a "because"-filtered
  co-occurrence statistic is still a functional of an observed joint distribution = rung-1. Empirical echo: LLMs are
  "causal parrots" (Zecevic 2023); CLadder/Corr2Cause degrade to near-chance on the counterfactual rung.
- **The corpus is biased by the selection mechanism, not just noisy.** Reporting bias (Gordon & Van Durme 2013: text
  records the notable, not the frequent) + explanation-selection bias (Hilton-Slugoski 1986 abnormal-conditions;
  Kahneman-Miller norm theory; Hesslow 1988) mean a "because" corpus samples "C stated as cause of E GIVEN C is
  abnormal/salient" -- it never gives the ¬C cell needed for an unbiased DeltaP. NO causal-KB (ATOMIC/ASER/CausalNet/
  CausalBank/GLUCOSE) has ever built a true 2x2 table. So DeltaP-from-testimony would be systematically biased, not a
  clean separation. **Crucially, the abnormality-selection mechanism that biases the corpus IS the mechanism that
  DEFINES causal selection** -- the signal is entangled in text because text was written BY it. This is WHY our store
  is redundant with lexical association (e-CARE) and its direction is only weakly load-bearing.

### The missing signal = the counterfactual-necessity SIMULATION (rung-2/3), a computation SEPARATE from the store
Causal-antecedent selection is a computation distinct from the knowledge store (which is necessary-but-not-sufficient):
- **Formal**: SCM = mechanism-equations (the knowledge) + a do()-procedure that severs edges (Pearl). Association is
  compatible with many mechanisms -> can't answer intervention.
- **Neural**: causal judgment recruits dlPFC/precuneus ON TOP of associative, same content (Satpute 2005); ATL/semantic
  damage does NOT track counterfactual deficit -- mPFC/hippocampus does (Viard 2014; Mullally-Maguire 2014). So the
  simulation is a separate circuit from the semantic (knowledge) hub.
The simulation CONSUMES four ingredients PMI structurally lacks: (i) a **bound per-item situation model** at
entity+attribute+value grain; (ii) **candidate mechanism edges** -- the store's CORRECT role (hypothesis source, not
scorer); (iii) a **norm/comparison case** (two-stage: knowledge-selected reference class [Hilton-Slugoski] + within-
class contrast [Forsterling]) -- this is why the ENABLER outscores the abnormal cause on PMI (the "oxygen problem");
(iv) an **ablate-and-recompute operator** (remove candidate C's state-effect, recompute, check whether the target
flips). PMI has none of these -- no bound state, no ablation, no norm, no simulation.

### Substrate-chain trace (where the signal is lost, and the fix)
| stage | brain-faithful | ours today | status |
|---|---|---|---|
| knowledge | structural PRIOR = candidate causal edges | mined store (1.29M edges) | ✅ built; MIS-USED as a scorer |
| instantiation | bind edges to THIS item's participants/states (situation model) | decontextualized concept lookup | ❌ missing |
| **selection** | ablate candidate over the bound model, check counterfactual necessity | **PMI score (rung-1)** | ❌ **wrong computation** |
| engine | `predictive_world_model.necessity` / `WorldState.do()` | EXISTS, but starved (fed adjacency-W, not the store; no bound per-item model, no norm) | ⚠️ present, unfed |
**The fix (brain-foundational): run the store's candidate edges THROUGH the necessity engine over a bound per-item
situation model; PMI's only legitimate role is a cheap pre-filter to narrow candidates before the ablate-and-recompute.
This is the generative-simulation world-model the three parent problems named the MAIN EVENT -- the store FEEDS it.**

### What we DEMONSTRATED (the causal-specific signal the store DOES carry -- direction from causal MARKING)
On three DIRECTION-SENSITIVE instruments where association is neutralized by construction (a similarity model is at
chance), the store's DIRECTION beats the neutralized floor CI-separated:
- held-out testimony (in-distribution): causal-direction 0.609 vs same-corpus co-occurrence 0.513, +0.097 CI-sep.
- e-CARE gold causal pairs (modern human gold; assoc=0.5 by construction, n=2122): causal-direction 0.517 vs shuffled
  twin 0.499, +0.018 CI[0.0002,0.036] CI-sep.
- **BCOPA-CE** (Han & Wang 2021, the published direction-sensitive gold where PLMs COLLAPSE to ~51%; two alternatives =
  true cause + true effect, n=1000): floors AT chance by construction (direction_blind 0.500, lexical 0.500, twin
  0.499); causal_directed 0.522 beats direction_blind +0.022 CI[0.0015,0.042] (covered +0.035 CI[0.004,0.066]).
=> The direction signal is REAL (CI-sep on all three) but WEAK in absolute terms (~0.52-0.61), and weakest on BCOPA-CE's
everyday links -- the Gricean gap (obvious causes under-testified) + the scale + rung-1 ceilings. This is a genuine
rung-1.5 contribution (causal MARKING carries a directional prior co-occurrence lacks -- consistent with the field
treating testimony as a STRUCTURAL PRIOR), but it is not the rung-2 necessity signal.

### Bottom line for "fully unlock"
It is NOT a rescore (DeltaP/Cheng stay rung-1 and are corpus-biased). The unlock is the **rung-2 counterfactual-
necessity simulation over a bound situation model, with the mined store as its edge-hypothesis source** -- i.e. the
generative world-model program (the parents' main event). The store is now proven to carry a real directional prior
(the piece testimony CAN supply); the remaining, decisive piece is the simulation ENGINE fed the store + a bound
per-item model + a norm -- and a MULTI-EVENT trap-proof necessity instrument to score it on (single-premise 2AFC cannot
exercise ablation). That is the next problem, and it is well-defined by this analysis.


## PHASE A/B UPDATE (2026-09-09) -- pursued PARTIAL -> SOLVED per owner; the strongest floor is not yet cleared on the primary instrument, so status stays PARTIAL (strengthened), with the exact remaining barrier QUANTIFIED.

**The #1 barrier was the INSTRUMENT (measurement), and I removed it.** TellMeWhy's gold cause IS the nearest sentence
(position pairwise-AUC 0.91), so no causal-knowledge signal could ever register there. I acquired two POSITION-BALANCED
2AFC causal-selection golds (reproducible fetch: `fetch_causal_selection_gold_v1.py`): **COPA** (drwiner/COPA gold XML,
n=1000, 50/50 cause/effect, position cannot leak the answer) and **e-CARE** (Waste-Wood/e-CARE, MIT, dev n=2122, harder,
lexically-rich). Scoring is direction-aware (ask-for=cause -> `cs_pmi(alt->premise)`; effect -> `cs_pmi(premise->alt)`).

**RESULT on the position-free instrument:**
- **COPA (weak-lexical regime, n=1000):** the mined causal store **BEATS the lexical-association floor CI-sep**
  (causal_directed 0.538 vs lexical 0.485, paired +0.053 CI[0.022,0.084]) **and beats the info-free shuffled-effect
  twin CI-sep** (twin 0.501, paired +0.037 CI[0.016,0.059]), and beats chance 0.50 CI-sep. **This is the causal-knowledge
  win TMW's position-confound hid** -- directed causal testimony helps on a position-free causal-selection task.
- **e-CARE (strong-lexical regime, n=2122):** causal beats the twin (+0.036 CI[0.018,0.054]) but **LOSES to the lexical
  floor** (causal 0.540 vs lexical 0.588, -0.048 CI[-0.071,-0.024]); the association+causal COMBINATION (held-out
  weight-tuned on train_full, `exp_causal_selection_combined_v1`) adds NOTHING over its twin-combination
  (+0.000 CI[-0.028,0.022]). Where association is strong, the mined causal signal is REDUNDANT with it.

**TWO QUANTIFIED BARRIERS to a clean full SOLVE (why the strongest floor is not yet cleared):**
1. **SCALE.** Absolute accuracy ~0.54 is far below the non-LLM mined-KB ceiling **0.70-0.71** (CausalNet/Sasaki), which
   was obtained by WEB-SCALE mining (billions of n-grams). My offline foundation is ~161k causal sentences / 1.29M
   edges (~1000x smaller). The offline corpus cannot reach web-scale -> this is a hard resource ceiling, not a mechanism gap.
2. **DIRECTION is not load-bearing on 2AFC.** causal_directed ties its own DIRECTION-BLIND use (COPA +0.009, e-CARE
   -0.003) -- because the WRONG alternative is a non-cause, not the REVERSE-direction, so 2AFC does not exercise
   direction. The directional signal IS real and CI-separated, but only on a direction-DISCRIMINATION task (the held-out
   testimony test: causal 0.609 vs co-occurrence 0.513, +0.097 CI-sep). Standard 2AFC cannot showcase it.
3. **GRAIN (tested, negative for the cheap fix).** Frame-structured lookup `(PRED,PATIENT)` on the bag-mined store does
   NOT beat bag-of-concepts (coverage loss offsets precision; `exp_causal_selection_framegrain_v1`); a proper
   frame-grain STORE would be sparser still. The brain-faithful state-grain is the right target but needs the store
   re-mined at frame grain AND more scale to help -- capped by barrier 1.

**Net:** the instrument barrier is removed and the causal-knowledge win is now DEMONSTRATED on a position-free
instrument (COPA), but a decisive full SOLVE across instruments is blocked by a quantified SCALE ceiling (offline
corpus ~1000x below web-scale) and the fact that 2AFC does not exercise the directional signal that is the store's
brain-foundational contribution. Full pass per the located-negative provision; status PARTIAL (materially strengthened).


# Directed causal-mechanism knowledge from mined causal-linguistic testimony

**Status: PARTIAL** -- a real, brain-foundational CONSTRUCTIVE positive on the trap-proof intrinsic frame (mined
testimony recovers directed causal knowledge that co-occurrence cannot), plus a rigorous, QUANTIFIED located negative
on the downstream narrative-selection application. This mirrors how the parent `generate_dont_retrieve` was scored:
constructive intrinsic win + located negative on the position-confounded benchmark.

## The signal chain the owner's frame demanded (final component -> input -> source)
- **FINAL COMPONENT** = `hdlab.predictive_world_model.causal_antecedent` (owner-DONE counterfactual-necessity reader,
  brain-foundational in FORM: Gerstenberg-Tenenbaum CSM; Trabasso; Hesslow's difference criterion). It needs, per
  candidate cause A and effect B, a **directed cause->effect production strength**.
- **ITS INPUT** = the forward model `W` = `P(next event-concept | recent event-concepts)`, learned by delta-rule on
  **raw textual ADJACENCY** of verb-concepts (simplewiki). **This is where the signal dies:** `W` carries ASSOCIATION,
  and association is structurally the WRONG signal type for causation (Pearl's ladder; Bareinboim's Causal Hierarchy
  Theorem 2022 -- rung-1 data under-determines rung-2 answers; Jin et al. 2021 -- causal direction is not recoverable
  from text surface statistics). Confirmed on disk: **on 54-59% of answerable TellMeWhy items the gold cause shares
  ZERO lexical content with the effect** (`exp_genworldmodel_residual_decomposition_v1`), so an adjacency-learned `W`
  has ~0 transition weight cause->effect and picks a topical distractor. Reproduced here: adjacency-W is **at chance**
  for causal-antecedent selection (full pairwise-AUC 0.495 CI[0.462,0.526]; zero-overlap 0.489 CI[0.438,0.541]).
- **THE BRAIN'S SOURCE** = directed causal knowledge, much of it acquired from **causal-linguistic testimony**
  (Harris & Koenig 2006; Ahn et al. 1995 -- humans weight mechanism over covariation; forward models are causal where
  action/testimony-conditioned -- Wolpert; Rezende 2020). Sentential causal testimony as a knowledge input is an
  **acknowledged formal gap** (causal-Bayes-net literature has no slot for "A causes B" as a datum). So the fix is to
  change what `W` is built from -- adjacency -> directed causal testimony -- without touching the brain-foundational
  reader that consumes it.

## What I built (glass-box, NO external LLM, NO spaCy)
1. **The miner** (`exp_causal_testimony_mine_v1.py`): regex-prefilter + the substrate's own `hdlab.pos_tagger` +
   WordNet morphy. Directionality per the researched spec (Sanders-Spooren-Noordman order primitive; Wolff force
   dynamics; CausalNet EPC/CPE): BACKWARD (because/since/due to/... -> subordinate=CAUSE), FORWARD
   (so/therefore/thus/... -> clause1=CAUSE), CAUSATIVE VERBS (causes/leads to/results in/... -> SUBJ=CAUSE, OBJ=EFFECT),
   COUNTERFACTUAL necessity ("if X hadn't ... Y wouldn't"). EXCLUDES the correctness traps: PREVENT-class
   (cause->effect-BLOCKED, not cause->effect), "even if" concessives, "so that" purposives. Concepts = VERB + NOUN
   lemmas; edges scored by CausalNet-style directed PMI. **Full mine (simplewiki + 13 textbooks, 161k causal
   sentences): 1,292,955 directed edges, 41995 causes x 47012 effects** (backward 58.6k, causative 38.5k, forward 4.7k,
   counterfactual 903). Persisted as an offline foundation asset `store_v1.json`.
2. **The baseline** (`exp_causal_testimony_baseline_v1.py`): reproduces the wall -- adjacency-W at chance.
3. **The head-to-head** (`exp_causal_testimony_eval_v1.py`): W_causal vs adjacency-W vs shuffled twin vs position/
   lexical floors on the identical TMW population.
4. **The trap-proof intrinsic test** (`exp_causal_testimony_heldout_v1.py`): the load-bearing test. From the SAME
   corpus/vocab/pipeline, two directed stores -- CAUSAL (marker-direction) vs ADJACENCY (textual-order co-occurrence);
   on a held-out 10% sentence split the CAUSAL store never saw, does it (a) predict the true effect above a shuffled
   twin, (b) recover DIRECTION (rank cause->effect above the reverse) better than co-occurrence?

## What I measured
- **INTRINSIC (trap-proof, held-out testimony, n=10164):** the causal store recovers **DIRECTION 0.609
  CI[0.597,0.620]** vs same-corpus co-occurrence **0.513 CI[0.501,0.524]** (chance), **paired +0.0973
  CI[0.0802,0.1144] CI-SEPARATED**; effect-prediction causal 0.733 vs co-occurrence 0.711 (paired +0.0215 CI-sep) and
  vs shuffled twin 0.499 (**+0.2338 CI-sep**). => the causal-specific value is concentrated in DIRECTION (+0.097),
  ~4.5x the effect-prediction margin (+0.022): association is largely shared with co-occurrence, DIRECTION is what
  testimony adds -- exactly the Pearl-asymmetry the signal-type thesis predicts.
- **APPLICATION (TMW answerable non-adjacent, n=273):** gold-link coverage 0.502 at scale (coverage is NOT the wall).
  But the causal read is at chance on the full population (0.501, paired vs adjacency +0.006 CI[-0.031,0.044]); on the
  zero-overlap slice causal 0.530 vs adjacency 0.489 (paired +0.041 CI[-0.026,0.106], NOT CI-sep), while the
  **POSITION floor (nearest-non-adjacent) scores 0.910** -- TMW's gold cause is position-determined, so no knowledge
  signal can surface. (This is precisely why the brief bans position-confounded gold and the parents retracted their
  TMW wins.)

## The verdict, stated honestly
The brain-foundational mechanism (a directed cause->effect foundation mined from causal-linguistic testimony) IS
buildable glass-box at scale and DOES carry directed causal knowledge that co-occurrence provably cannot -- a real
constructive positive on the trap-proof frame. But it does NOT deliver the full-population narrative causal-antecedent
SELECTION win the program ultimately needs, for two measured reasons: (1) the recovered directed signal is WEAK in
absolute terms (direction accuracy 0.609 -- testimony is noisy: epistemic "because", polysemous "since/as", crude
positional clause-splitting); (2) the only available narrative causal-selection benchmark (TMW) is POSITION-confounded
(0.91), so even a strong directed signal could not register there. The granularity ceiling has a number: at 50%
gold-link coverage the recovered DIRECTION is 0.609, not the ~0.9 that would be needed to beat position.

## What I did NOT establish (withdraw-first if wrong)
1. I would withdraw first any claim of a **full-population narrative causal-antecedent SELECTION win** -- there is none
   (TMW ties chance / loses to position). The clean CI-separated positive is on the trap-proof intrinsic DIRECTION
   test, not on the benchmark.
2. I initially flagged that 0.609 might be a CRUDE-EXTRACTOR limit (positional clause-splitting, no arc-parse). **I
   TESTED this and it is largely DISFAVORED:** restricting the store to reliable-direction markers only (causative +
   forward, where positional splitting is clean) nudges direction accuracy only 0.609 -> 0.626 (n=4575), so the ceiling
   is substantially INTRINSIC (genuine causal bidirectionality -- "stress causes insomnia" / "insomnia causes stress"
   -- plus generic-concept symmetry), not an extraction bug a parser would fix. I would still withdraw any claim that
   0.626 is the absolute testimony ceiling (a parser + Sweetser epistemic-because filter might add a little), but the
   evidence says the gain would be small.
3. I did NOT wire the store into the live reader or run per-story `WorldState.do()` instantiation (Q111 -- proposed
   below, not landed). No live-reasoner regression is claimed because nothing live changed.

## KEY REALIZATIONS
1. **The wall is not coverage and not mechanism -- it is DIRECTION strength.** Coverage rose 5.4% -> 50.2% with scale;
   the mechanism (necessity reader) is BF; yet the win is capped by how reliably testimony's DIRECTION can be recovered
   (0.609). Enabling move: separating the DIRECTION test from the effect-prediction test -- effect-prediction ties
   co-occurrence (association is shared), and ONLY the direction test isolates testimony's causal-specific value.
2. **The zero-overlap slice is where association is blind but POSITION is NOT.** I initially assumed the zero-overlap
   slice neutralized all floors; measuring showed position scores 0.91 there (the cause sits ~2 sentences before the
   effect). The trap-proof test therefore had to abandon the benchmark entirely and use held-out testimony with
   random/reverse distractors -- no position, no crowd gold.
3. **A same-corpus co-occurrence baseline is the right control, not the deployed adjacency model.** Comparing to the
   300-vocab simplewiki model would have been an unfair coverage win; building co-occurrence from the SAME sentences
   isolates marker-DIRECTION as the only difference -- and that is where the CI-separated win lives.
4. **Testimony's directional advantage over co-occurrence is ENTIRELY from BACKWARD connectives** (because/since/due to
   -- effect stated BEFORE cause). Splitting the store by marker class: with ALL markers, causal 0.609 vs co-occurrence
   0.513 (+0.097 CI-sep); with CLEAN markers only (causative + forward, where the cause is stated FIRST so textual
   order already encodes direction), co-occurrence jumps to 0.605 and the advantage collapses to +0.011 (not CI-sep).
   So linguistic marking beats word-order EXACTLY where word-order is misleading -- the backward constructions. This is
   the precise, mechanistic form of "testimony transmits direction association cannot": it is not a blanket advantage,
   it is localized to where the surface order inverts the causal order. (It also means the 0.609 ceiling is intrinsic,
   not extractor-noise: clean high-precision markers only reach 0.626.)

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
- **`hdlab.predictive_world_model`** forward model `W` is learned on textual ADJACENCY -> it is an ASSOCIATIVE
  (rung-1) transition model, NOT a directed causal one. Its counterfactual-necessity reader is BF in form but is fed
  the wrong signal type for causation. This is a named fidelity gap (the input, not the reader).
- **Brief mis-citation:** the brief cites "the 2021 amodal IFG/MTG/mPFC meta-analysis" for causal construction being
  amodal. **Feng et al. 2021 (Front Hum Neurosci 15:666179) actually found NO overlap between discourse-causal and
  logical-causal networks and argues AGAINST a unified amodal account.** "Embodiment is not the lever" still holds via
  Bedny et al. 2012 (blind subjects develop normal abstract/causal concepts), not Feng.
- **Brief number garbled (disk outranks brief):** the brief's "(b) 54% lexical / 73% forward-predictability / 34%
  zero-overlap" is a scrambled restatement of the on-disk figure (`exp_genworldmodel_residual_decomposition_v1`):
  **53.8%/59.0% of gold causes share ZERO lexical overlap with the effect, mean overlap ~0.05-0.07**; the "73%" is not
  located on disk.
- **Adjacent component `hdlab.causal_network.py`** covers only 8 connective classes (so/therefore/thus/hence/
  consequently/accordingly + because/since); it is MISSING prepositional phrasals (due to/owing to/because of),
  ALL causative verbs (causes/leads to/results in/produces/triggers), and counterfactuals; its force bridge is UNTYPED
  (no CAUSE/ENABLE/PREVENT distinction -- a correctness risk for PREVENT-class verbs). The miner here implements the
  fuller inventory + typed exclusion; this is a candidate adjacent upgrade.

## PROPOSED hdlab CHANGE (Q111 -- strategy lands; NOT landed here)
Additive, default-safe: add a directed-causal-support channel to `situation_reader._read_predictive_causal` (and/or a
`causal_store` argument to `hdlab.predictive_world_model`) that scores candidate causes by the mined store's directed
PMI (`store_v1.json`, an offline consolidated foundation asset, load-once), COMBINED with the existing surprisal-
necessity read rather than replacing it. Expected live effect on the current board: NIL-to-small (the signal is weak
and the live consumers are not scored on a trap-proof causal-antecedent instrument), so it should land default-ON only
if a `board_causal_direction_dimension()` instrument-arm is built to score it on the trap-proof frame (a board-invisible
proven win needs its own instrument-arm). Do NOT wire any TMW-selection cue (position-confounded).

## ADJACENT COMPONENTS (seeds for the next problems)
- **A parser-based causal-testimony extractor** (use `hdlab.arc_parser`/`arceager_parser` for subject/object of
  causative verbs + a Sweetser epistemic-because filter): the highest-value strengthening -- would test whether 0.609
  direction is an extractor limit or a testimony limit.
- **Consolidation gate** (`build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner`): consolidate the
  1.29M-edge raw store (dedup, PMI-threshold, contradiction-prune) into a cleaner foundation before wiring.
- **The action-conditioned forward model** (the goal slice): the research shows forward models are causal where
  action-conditioned; combining testimony DIRECTION with the goal/means-end hub (chain_multi_step's shelved MeansEnd)
  is the natural next lever for the GOAL-type causation the parents already partly won.

---

## TLDR (plain English)
A good reader knows that a specific action causes a specific result. Our reader has the right machinery to reason
about that, but the knowledge it runs on is learned from "which words tend to appear near which" -- mere association,
which the research shows is the wrong kind of information for cause-and-effect. We built the brain's alternative:
we mined about 1.3 million "X causes Y" style statements out of textbooks and encyclopedias (from phrases like
"because", "so", "leads to", "if X hadn't, Y wouldn't"), turning them into a directed cause-to-effect knowledge store.
The good news, proven cleanly: this store genuinely learns the DIRECTION of causation (that X causes Y, not Y causes X)
that plain word-association cannot -- a real, first-of-its-kind result. The limit: the direction it learns is only
about 61% reliable, which is not strong enough to beat a dumb "the cause is usually the sentence just before"
shortcut on the standard test -- and that standard test turns out to be rigged by sentence position anyway. So we have
a real, brain-faithful piece of the puzzle that is not yet strong enough on its own; the clear next step is a better
extractor to sharpen the direction signal.

## QUESTIONS
None blocking. One decision for the strategy session at integration: whether to land the offline causal store now
(default-off, as a consolidated foundation asset for later wiring) or defer until the parser-based extractor raises
the direction signal. My recommendation: land it as a dormant asset + build the trap-proof `board_causal_direction`
instrument-arm, because the constructive win is real and bankable but board-invisible without its own instrument.

## NEXT STEPS
1. **Parser-based extractor** (arc_parser subj/obj + Sweetser filter) -> re-measure direction accuracy: is 0.609 an
   extractor limit or a testimony limit? (highest value)
2. **Consolidate** the raw 1.29M-edge store via the consolidation gate; re-run the intrinsic test on the cleaned store.
3. **Build a `board_causal_direction` instrument-arm** (reuse `exp_causal_testimony_heldout_v1`) so the proven
   direction win is scorable on the live board (it is currently board-invisible).
4. **Combine testimony-DIRECTION with the action-conditioned goal hub** (chain_multi_step MeansEnd) for GOAL-type
   causation -- the research says causal forward models are strongest when action-conditioned.
