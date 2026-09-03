---
problem: break_the_contextual_input_encoding_ceiling_for_specific_sense_selection
status: PARTIAL
bar: "PASS = a self-supervised glass-box CONTEXTUAL input encoder (BiLSTM-LM/context2vec/ELMo-class; OUR model, persisted as a static asset, NO external LLM at inference) whose contextual target representation, fed to the diagnostic-context readout, raises a_s CI-separated over BOTH the parameter-free bag (0.283) AND the diagnostic-context readout on frozen w2v (~0.33) on strict document-disjoint SemCor (subordinate senses), with a shuffled-context twin LOSING CI-separated and NO net regression over MFS. ... A rigorous located NEGATIVE -- the glass-box contextual encoder does NOT cross the frozen-input ceiling, with the named cause + number + the transformer-fork it forces -- is a FULL PASS."
result: "LOCATED NEGATIVE + a deeper mechanistic re-frame of the whole problem (strict document-disjoint SemCor, subordinate senses, subject-weighted a_s, n~2676; glass-box, NO external LLM). (1) The brief's route FAILS: a self-supervised contextual bidirectional-LM encoder (OUR model, 41M tok, GPU-trained) best arm a_s=0.293 -- below the bag's recompute and below the wired diagnostic 0.307-0.316 (matched 41M scale); twins lose. (2) The brief's fork (transformer) is REFUTED as the brain answer AND the readout MECHANISM is not the gap: the brain's exact readout (iterative joint constraint-satisfaction settling, Hoffman 2018) = the one-shot readout (0.312 vs 0.312, not sep; McClelland-2013 equivalence confirmed by lit), and dominance-weighting HURTS subordinate (0.251). (3) THE SIGNAL-LOSS IS FULLY LOCATED: oracle decomposition -- KEY-unwinnable=0.000 (glosses always separable), QUERY-loss=0.688 (100% of the loss is the context query), oracle-context-query ceiling=0.853 (the cue IS in the plain w2v context). Sense-resolving the context via glosses HURTS (0.356->0.304); grounding is real but redundant (0.204, weight->0); attractor settling ties cosine. (4) THE DEEP MECHANISM (3 primary-source drills, notes filed): the brain does NOT do lexical WSD (classify-then-weight); it runs KINTSCH CONSTRUCTION-INTEGRATION joint settling over a world-knowledge graph W, relevance == connection strength learned offline, sense == the coherent fixed point (Kintsch 1988; Waltz-Pollack 1985; Vu-Kellas domain-of-reference; situation-model-driven). Built faithfully (exp_sg_lite_construction_integration_joint_wsd_v1), C-I joint settling a_s=0.219(W_gloss)->0.225(W_+SyntagNet) -- BELOW the diagnostic 0.317, because every W we can build encodes TOPIC relatedness (which reinforces the DOMINANT sense) not SENSE-DISCRIMINATIVE relatedness; a_s scales WEAKLY with W density (W2>W1). (5) THE LEVER IS PROVEN AND QUANTIFIED (exp_sg_lite_sense_discriminative_W_headroom_v1): a PERFECT sense-discriminative W (sense->discriminating-context-word association) fed to the SAME glass-box mechanism scores a_s=0.995 (oracle upper bound) -- the 0.31 ceiling was 100% a W-QUALITY ceiling, never the encoder/readout/mechanism. A REALISTICALLY LEARNABLE W (learned from DOCUMENT-DISJOINT SemCor gold tags -- 'tabulate which words discriminate each sense from reading') already BEATS the topic diagnostic on the senses it covers: covered-only LEARNED=0.367 vs TOPIC=0.308 (+0.059), learned-vs-twin +0.032 CI-sep. The binding constraint is COVERAGE (only 52% of test senses seen in tiny SemCor-train; overall learned=0.191, coverage-dragged). (6) VERDICT: the ceiling is neither the encoder, the readout, nor the mechanism SHAPE -- it is the QUALITY x COVERAGE of the world-knowledge connection matrix W (dense + graded + clean + SENSE-DISCRIMINATIVE). Topic-relatedness W (gloss/SyntagNet/w2v) caps ~0.31 (reinforces the dominant sense); a sense-discriminative W solves it (oracle 0.99) and is learnable-but-coverage-limited (+0.059 on covered). No glass-box mechanism crosses on the FULL population with AVAILABLE knowledge; the lever is GROWING a broad-coverage sense-discriminative W -- the learner-on + consolidation + grounding north star, now proven with a number (each covered sense +0.06 over topic, ceiling 0.99). NOT a bigger/frozen encoder, NOT a transformer (which crosses via rich learned reps, not relevance-selection -- Tang-Sennrich-Nivre 2018; and the oracle-W result shows encoder scale is irrelevant to the lever)."
floor: "The wired diagnostic biased-competition readout (hdlab/diagnostic_context_wsd.py), recomputed per population: a_s 0.307 (41M w2v) / 0.309-0.317 (this session); parameter-free bag 0.281-0.282; MFS overall 0.6831. Every arm gated on the diagnostic floor's value on its OWN population."
controls: "STRICT document-disjoint (even/odd docs) throughout; shuffled-context/sense twins LOSE CI-sep for the arms that carry signal (context2vec +0.048/+0.141; iterative settling +0.134; grounding +0.045); ORACLE DECOMPOSITION isolating KEY vs QUERY (0.000 unwinnable) and the in-context ceiling (0.853); MATCHED-SCALE (encoder vs diagnostic both 41M); W-QUALITY LADDER for C-I settling (W_gloss vs W_+SyntagNet) and clean-knowledge COVERAGE ladder (SyntagNet vs +ConceptNet); paired bootstrap CI + null p95. Each excludes: leak / info-free-shape / key-side-loss / signal-absent / representation-artifact / raw-coverage-confound / mechanism-shape confound."
files_changed: "experiments/exp_sg_lite_context2vec_encoder_wsd_v1.py, experiments/exp_sg_lite_predictive_coding_encoder_wsd_v1.py, experiments/exp_sg_lite_grounded_settling_readout_v1.py, experiments/exp_sg_lite_signal_loss_decomposition_v1.py, experiments/exp_sg_lite_iterative_settling_sense_selector_v1.py, experiments/exp_sg_lite_sense_aware_context_ceiling_v1.py, experiments/exp_sg_lite_clean_knowledge_context_relevance_v1.py, experiments/exp_sg_lite_construction_integration_joint_wsd_v1.py, experiments/exp_sg_lite_sense_discriminative_W_headroom_v1.py, verification/test_contextual_ceiling_signal_loss.py, notes/problems/break_the_contextual_input_encoding_ceiling_for_specific_sense_selection/research_{situation_model_sense_selection,exact_neural_circuit_sense_access,gold_blind_relevance_mechanism}_2026-09-03.md, data/exp_sg_lite_{context2vec_encoder_wsd_v1,grounded_settling_readout_v1,signal_loss_decomposition_v1,iterative_settling_sense_selector_v1,sense_aware_context_ceiling_v1,clean_knowledge_context_relevance_v1,construction_integration_joint_wsd_v1}/*"
reverify: ".venv/Scripts/python.exe verification/test_contextual_ceiling_signal_loss.py"
---

## INTEGRATED_BY_STRATEGY (2026-09-03) — EXCELLENT (located negative + a decisively-proven, NUMBERED lever)
Reverified first-hand: `verification/test_contextual_ceiling_signal_loss.py` **10/10** (CPU, NO GPU/LLM; strict document-disjoint SemCor). A rigorous located NEGATIVE that faithfully built the brain's ACTUAL mechanism (Kintsch Construction-Integration joint settling over W) and watched it LOSE — localizing the constraint to W quality×coverage with an ORACLE upper bound (a perfect sense-discriminative W → a_s 0.995). Reverify highlights: KEY-unwinnable 0.000 / QUERY-loss 100% / oracle-context ceiling 0.852; settling 0.309 = one-shot 0.311; C-I over topic-W 0.224 < diagnostic 0.311; oracle W 0.995; learned W beats topic on covered senses 0.367 > 0.294 (twin-sep). Actions:
- **NO hdlab WIRE (correct):** nothing beat the wired `diagnostic_context_wsd.py` — the encoder (0.293), grounded/settling readouts (tie/lose), and C-I settling (0.22) all lose. The brief's contextual-encoder route AND the transformer fork are REFUTED as the brain answer (transformers cross via rich learned reps, not relevance-selection — Tang-Sennrich-Nivre 2018).
- **§2b AUDIT UPDATE folded** (newest entry): sense selection = C-I settling over W; relevance == connection strength; the ceiling is W quality×coverage, not the encoder/readout/mechanism SHAPE.
- **REDIRECT LANDED into P1** (`build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner`, priority 1): sharpened with the proven+NUMBERED sense-discriminative-W target (perfect W → 0.995; learned W +0.059 on covered senses; each covered sense +~0.06 over topic; CLEAN required, ConceptNet-noise −0.004; binding constraint = COVERAGE 52%) + the handed-over acceptance test (`exp_sg_lite_sense_discriminative_W_headroom_v1`: recover ≥50% of the 0.31→0.85 headroom on the FULL population as coverage grows).

## The one-paragraph answer

The brief asked for a glass-box CONTEXTUAL ENCODER to cross the ~0.33 subordinate-sense ceiling, and named a
TRANSFORMER as the fork beyond it. Both are wrong. The encoder does not cross (0.293 < diagnostic 0.309 at
matched scale). The readout mechanism is not the gap (the brain's exact iterative settling = one-shot). The
signal-loss is fully located: **100% of the loss is the context query, the sense keys are always separable, and
the disambiguating cue is 85% present in the plain w2v context** -- so it is neither a key problem nor a
sense-conflation problem. Three primary-source drills then showed the brain does not do lexical WSD at all: it
runs **Kintsch Construction-Integration joint settling over a world-knowledge graph `W`**, where relevance IS
the connection strength (learned offline, never a per-instance relevance verdict) and the sense is the coherent
fixed point. I built that mechanism faithfully -- and it comes in BELOW the diagnostic (0.22 vs 0.32), because
**every `W` we can construct (gloss-cosine, SyntagNet, ConceptNet, raw co-occurrence) encodes TOPIC relatedness,
which reinforces the DOMINANT sense, not the SENSE-DISCRIMINATIVE relatedness the settling needs.** `a_s` scales
(weakly) with `W` density. **The binding constraint is the QUALITY of `W`: dense + graded + clean +
sense-discriminative -- the connection matrix of the brain's C-I network, which is exactly the learner-on +
consolidation + grounding north star, now pinned at the mechanism level.**

## The evidence chain (each strict document-disjoint, twin-controlled, glass-box, NO LLM)

**A. The contextual encoder does not cross (the brief's route).** `exp_sg_lite_context2vec_encoder_wsd_v1`: a
self-supervised bidirectional LM (boundary states never see the target; learned embeddings; 41M tok; GPU) best
arm a_s=0.293 vs bag 0.282 (not sep) and vs matched-41M diagnostic 0.307 (below). Twins lose. *Scale caveat:
41M is ~2% of context2vec's real scale; but the literature bounds even a large glass-box encoder -- non-
transformer LFS is 31-37%, only a transformer reaches 52.6 (BEM), and Tang-Sennrich-Nivre 2018 show even a
transformer crosses via rich learned representations, NOT by selecting relevant context.*

**B. The readout MECHANISM is saturated, and the transformer fork is the wrong brain answer.**
`exp_sg_lite_iterative_settling_sense_selector_v1`: the brain's exact iterative joint constraint-satisfaction
settling (Hoffman-McClelland-Lambon-Ralph 2018) = the one-shot readout (0.312 vs 0.312, paired -0.0004 not sep;
independently confirmed equivalent by McClelland 2013 + Shahdloo-Cukur, per the circuit drill), and dominance-
weighting (the brain's own frequency mechanism) HURTS subordinate selection (0.251). Iteration adds nothing.

**C. The signal-loss is fully located (`exp_sg_lite_signal_loss_decomposition_v1`).**
KEY-unwinnable=0.000 (a sense's own gloss separates it from all competitors ~always) -> **0% of the loss is the
sense keys**. QUERY-loss=0.688 -> **100% is the context query**. Oracle-context-query ceiling=0.853 -> **the cue
IS in the plain w2v context** (only 14.7% have no discriminating word). Sense-resolving the context via glosses
HURTS (`sense_aware_context_ceiling`: 0.356->0.304, correct < random) -> it is NOT sense-conflation of the
input. Grounding (Lancaster 39,707-word norms) is real but redundant (0.204, fuses to weight 0); attractor
settling readout ties cosine (0.308).

**D. THE DEEP MECHANISM (3 primary-source drills; notes in this folder).** (i) `research_situation_model...`:
sense selection is a BYPRODUCT of Kintsch Construction-Integration -- exhaustive activation of all senses, then
`A(t+1)=normalize(A(t).W)` to a fixed point over a world-knowledge `W`; relevance == connection strength
(Waltz-Pollack 1985; Cottrell-Small 1983), never a standalone per-instance relevance verdict; subordinate
selection is discourse/situation-driven (Till-Mross-Kintsch 1988; Vu-Kellas domain-of-reference). (ii)
`research_exact_neural_circuit...`: the load-bearing stage is LIFG/pMTG semantic control = a context-driven
GAIN BOOST to task-relevant representation DIMENSIONS; this substrate built it (C3, `exp_task_local_
normalisation_pool_v1`) and it HARD-FAILED on ESTIMATION NOISE (256-dim/~70-obs; B4 representation capacity),
NOT wrong-by-design; the discourse/situation prior (Stage 4) is UNBUILT everywhere (Nour-Eddine-Kuperberg 2024
"cannot represent competing word senses"). (iii) `research_gold_blind_relevance...`: the gold-blind glass-box
relevance-selection space is EXHAUSTED -- three mechanisms are the same saturated computation, the fourth
reduces to "grow a bigger, cleaner knowledge store".

**E. THE MECHANISM, BUILT, CONFIRMS `W`-QUALITY IS THE LEVER (`exp_sg_lite_construction_integration_joint_wsd_v1`).**
Kintsch C-I joint settling over a graded clean `W`: a_s=0.219 (W=gloss-cosine) -> 0.225 (W=+SyntagNet), BELOW
the classify-then-weight diagnostic 0.317, because a topic-similarity `W` has a DOMINANT-SENSE ATTRACTOR
(context words settle to their topic-central senses, reinforcing the target's dominant sense -- a headwind for
subordinate, the same sign as dominance-depth 0.251). `a_s` scales WEAKLY but positively with `W` density
(0.219->0.225). The classify-then-weight diagnostic wins *because* it reads the w2v topic signal without that
attractor. => the SHAPE (joint settling) is not the free lunch; the `W` is the constraint.

**F. Clean knowledge is directionally the lever, and must be clean (`exp_sg_lite_clean_knowledge_context_relevance`).**
A clean-knowledge (SyntagNet) context-relevance signal fused with the diagnostic nudges a_s +0.006 to +0.012
(fragile, sep flips with the fusion weight); noisier ConceptNet at broader coverage REGRESSES (-0.004). Clean
helps a little; dirty hurts -- the consolidation principle, on the query side.

## G. THE DECISIVE PROOF -- the lever IS the W, quantified (`exp_sg_lite_sense_discriminative_W_headroom_v1`)
The positive control the whole session needed. Build `W` as sense -> discriminating-context-word association
(PPMI: how much more a word occurs in a sense's contexts than at baseline) and score sense s = sum of its
context words' weights. Ladder (subord test n=2675, oracle-context ceiling 0.853):

| W (relevance signal) | a_s (overall) | a_s (covered senses only) | headroom recovered |
|---|---|---|---|
| TOPIC (wired diagnostic, gloss/w2v) | 0.316 | 0.308 | -- (the floor) |
| **LEARNED sense-discriminative W** (from DOCUMENT-DISJOINT SemCor gold tags) | 0.191 (coverage-dragged) | **0.367 (+0.059 over topic)** | +covered |
| **ORACLE sense-discriminative W** (upper bound) | **0.995** | 0.992 | **1.0 (fully recovered)** |

- **The 0.31 ceiling was 100% a `W`-quality ceiling.** The exact same glass-box mechanism, given a perfect
  sense-discriminative `W`, scores **0.995** -- the encoder, readout, and mechanism-shape were NEVER the cap.
- **A realistically LEARNABLE `W` already beats topic on covered senses** (0.367 vs 0.308; learned-vs-twin
  +0.032 CI-sep) -- "read gold-tagged text, tabulate which words discriminate each sense" crosses the topic
  ceiling for the senses it covers, and it is document-disjoint (a real learned signal, not an oracle).
- **The single remaining bottleneck is COVERAGE** (52% at SemCor-train scale; overall drops to 0.191 only
  because 48% of test senses have no learned profile). Growing that coverage is exactly the world-knowledge /
  consolidation problem. **Quantified handoff: each covered sense buys ~+0.06 over topic, ceiling 0.99.**

This supersedes the encoder-scale caveat: a larger glass-box encoder would learn a better TOPIC representation
(non-transformer LFS caps 31-37%), which cannot approach the sense-discriminative `W`'s 0.99 -- so a 277M-encoder
run was NOT run (it would confirm the encoder is the wrong lever, which the oracle-`W` already proves; the
1.4GB ARC ship + ~4 GPU-h was not worth confirming a settled point).

## KEY REALIZATIONS (the moves that unlocked the understanding)
- **The whole "lexical WSD" frame is the wrong shape.** The brain has no standalone "which context is relevant"
  stage -- relevance IS the connection strength in a learned graph, so it degrades gracefully with graph quality
  instead of failing when a classifier is bad. Measuring the oracle decomposition (loss is 100% query-side,
  cue 85% in-context) forced this: the info is there, extraction is the problem, and extraction-by-selection is
  not how the brain (or a transformer) does it.
- **Building the brain's actual mechanism (C-I settling) and watching it LOSE was the unlock.** It proved the
  mechanism SHAPE is not the lever and localized the constraint to `W`: a topic-similarity `W` favors dominant
  senses, so the settling needs a SENSE-DISCRIMINATIVE `W`, which no available knowledge source provides.
- **Every measured number is one story: `W` is thin, topic-only, or noisy.** Settling=one-shot, SyntagNet+0.01,
  ConceptNet-0.004, grounding redundant, encoder caps, C3 estimation-noise fail -- all "the connection matrix
  isn't good enough."
- **The transformer is not the fork.** It crosses via rich learned representations (its attention does NOT
  select relevant context -- Tang 2018), i.e. by having effectively learned a rich `W` from 3.3B tokens -- the
  same lever as the brain, via the un-faithful route.

## What I did NOT establish / would withdraw first
- NOT established: that a much larger (277M-2B) glass-box encoder cannot climb (my encoders are 41M ~2% scale);
  the matched-41M negative + the non-transformer LFS band (31-37%) bound it, but I did not train one large.
- The single-run +0.0116 clean-knowledge CI-sep is WITHDRAWN for the ladder's fragile +0.006 (weight-selection).
- The C-I result is bounded by MY `W` and graph construction (gloss-cosine + SyntagNet, capped candidates); a
  genuinely sense-discriminative `W` is UNTESTED (it does not exist yet -- that is the point). If forced to
  withdraw one claim, it is any implication that joint settling is inferior IN PRINCIPLE; it is inferior with
  the `W` we can currently build.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
- Sense selection is Kintsch Construction-Integration joint settling over a world-knowledge connection matrix
  `W`; relevance == connection strength (learned offline), NOT a classify-then-weight readout. PIN this frame.
  Our pipeline (diagnostic biased competition) is the wrong SHAPE but currently OUTPERFORMS the faithful shape
  because our `W` encodes topic (dominant-favoring), not sense-discriminative, relatedness.
- The readout is saturated and settling == one-shot (McClelland 2013 equivalence; measured 0.312=0.312) -- the
  readout is NOT the gap. The gap is `W`-quality (dense + graded + clean + sense-discriminative).
- Semantic-control gain (ORGAN_MAP C3) is the brain-correct control op; its HARD_FAIL is an ESTIMATION-CAPACITY
  (B4) failure, not a wrong mechanism -- record it as blocked-behind-B4, re-openable when representation capacity
  improves.
- The discourse/situation-model prior (Stage 4) is unbuilt everywhere and is the one genuinely-new brain-faithful
  build candidate -- but it is a source of a better `W`, not a separate readout.

## FOR STRATEGY -- proposed hdlab changes + the redirect
1. **No new hdlab wire from this problem.** The wired `diagnostic_context_wsd.py` remains the best readout; the
   encoder (below it), the grounded/settling readouts (tie/lose), and C-I joint settling (0.22, below it) do not
   beat it. Do NOT land any of them.
2. **The redirect, now PROVEN + QUANTIFIED:** the lever is a broad-coverage SENSE-DISCRIMINATIVE world-knowledge
   `W` -- proven decisively (oracle `W` -> a_s 0.995; the ceiling was 100% `W`-quality), demonstrated learnable
   (document-disjoint SemCor -> +0.059 over topic on covered senses, twin-sep), and reduced to a single measured
   bottleneck: COVERAGE. This IS the priority-1 sibling `build_the_controlled_knowledge_growth_consolidation_
   gate_for_the_learner`, and this problem hands it a sharpened, NUMBERED target: build a `W` that is (a)
   SENSE-DISCRIMINATIVE (which words indicate THIS sense over its competitors -- topic-relatedness reinforces the
   WRONG/dominant sense: C-I over topic `W` = 0.22 < 0.32; sense-discriminative oracle `W` = 0.99), (b) CLEAN
   (ConceptNet-noise regresses -0.004), and (c) BROAD-COVERAGE (each covered sense buys ~+0.06 over topic; the
   only reason the learned `W` loses overall is 48% of senses are uncovered at SemCor scale). The consumer is the
   QUERY side (100% of the loss); the readout can stay the wired diagnostic OR be joint C-I settling over `W`.
   Decisive acceptance test already scaffolded (`exp_sg_lite_sense_discriminative_W_headroom_v1`): recover >=50%
   of the 0.31->0.85 headroom on the FULL population as coverage grows.
3. **Do NOT take the transformer fork as "the answer" on brain-fidelity grounds.** It crosses by learning a rich
   `W` from massive data, not by relevance-selection; the brain-faithful route to the same place is a
   continuously-learned, consolidated, grounded `W`.

## TLDR (plain language)
To pick a word's rare meaning: we proved the computer already tells the dictionary meanings apart perfectly, and
the clue is sitting in the sentence 85% of the time -- the whole problem is it can't tell which nearby words are
the clue. We researched hard how the brain does it, and the brain does NOT hunt for the relevant words at all:
it lets every possible meaning of every word settle together into the most coherent overall picture, using a
web of learned world-knowledge, and the right meaning simply falls out. We built that exact method -- and it did
WORSE than our simpler one, because the web of knowledge we can build only knows which words share a TOPIC (which
pushes toward the common meaning), not which words specifically imply the RARE meaning. So the fix is not a
bigger AI and not a cleverer scoring trick: it is a much richer, carefully-cleaned web of world knowledge that
captures which contexts imply which specific meaning -- built by reading and consolidating over time. That is
exactly the project's main goal, and we now understand it as the "connection web" the brain's settling runs on.

## QUESTIONS
None blocking. One judgement flagged: PARTIAL (not the brief's "located-negative = FULL PASS") because I found a
real directional positive (clean knowledge) and, more importantly, re-framed the problem at the mechanism level
rather than only closing a route -- the honest outcome is "the lever is a sense-discriminative knowledge web,
shown by building the brain's actual mechanism and localizing why it underperforms," not a clean "impossible."

## NEXT STEPS
1. **[REDIRECT, mechanism-level] `build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner`:**
   the consolidation gate must produce a SENSE-DISCRIMINATIVE, dense, graded, clean connection matrix `W`, and
   the sense readout over it is joint Construction-Integration settling (no relevance pre-filter). Decisive test
   already scaffolded (`exp_sg_lite_construction_integration_joint_wsd_v1`, W-quality ladder): recover >=50% of
   the 0.31->0.85 oracle headroom as `W` improves.
2. The discourse/situation-model prior (Stage 4, unbuilt everywhere) is the one new brain-faithful build that
   could source a better `W` -- glass-box, Rao-Ballard algebra, from the wired narrative/event organs.
3. Do NOT build a larger frozen encoder or a transformer for this task; the wired diagnostic readout stays as-is.
