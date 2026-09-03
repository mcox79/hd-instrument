---
problem: break_the_contextual_input_encoding_ceiling_for_specific_sense_selection
status: PARTIAL
bar: "PASS = a self-supervised glass-box CONTEXTUAL input encoder (BiLSTM-LM/context2vec/ELMo-class; OUR model, persisted as a static asset, NO external LLM at inference) whose contextual target representation, fed to the diagnostic-context readout, raises a_s CI-separated over BOTH the parameter-free bag (0.283) AND the diagnostic-context readout on frozen w2v (~0.33) on strict document-disjoint SemCor (subordinate senses), with a shuffled-context twin LOSING CI-separated and NO net regression over MFS. ... A rigorous located NEGATIVE -- the glass-box contextual encoder does NOT cross the frozen-input ceiling, with the named cause + number + the transformer-fork it forces -- is a FULL PASS."
result: "LOCATED NEGATIVE + corrected direction (strict document-disjoint SemCor, subordinate senses, subject-weighted a_s, n~2676). (1) A self-supervised glass-box CONTEXTUAL encoder does NOT cross: context2vec-style bidirectional LM (OUR model, 41M tokens, 256-d, GPU-trained, no LLM) best arm a_s=0.293 -- BELOW the parameter-free bag's own recompute here (0.282) is not cleared CI-sep, and BELOW the wired diagnostic readout 0.307-0.316 (matched 41M scale); shuffled-context twins LOSE (+0.048/+0.141). (2) The brief's named fork (transformer) is REFUTED as the brain-faithful answer: the brain's EXACT mechanism -- iterative joint constraint-satisfaction settling (Hoffman-McClelland-Lambon-Ralph 2018), glass-box, NO frozen encoder -- gives a_s=0.312, IDENTICAL to the one-shot readout (paired -0.0004, not sep), and the brain's dominance/frequency mechanism HURTS subordinate selection (0.251). The readout MECHANISM is saturated. (3) WHERE the signal is lost, measured by oracle decomposition: KEY-unwinnable=0.000 (sense glosses are always separable), QUERY-loss=0.688 (100% of the loss is the context query), and the disambiguating cue IS in the local w2v context (oracle-context-query ceiling=0.853) -- the wall is GOLD-BLIND RELEVANCE WEIGHTING, not sense-conflation of the input (sense-resolving context via glosses HURTS: 0.356->0.304). (4) The real, brain-faithful lever = CLEAN structured knowledge guiding biased competition: a SyntagNet context-relevance signal nudges a_s directionally +0.006 to +0.012 (fragile, edge of significance), and noisier ConceptNet REGRESSES it (-0.004) -- growth must be consolidated, not merely larger. So the ceiling is NOT crossable by a bigger/frozen encoder; the lever is clean-knowledge richness AT SCALE (the learner-on + grounding + consolidation north star)."
floor: "The wired diagnostic biased-competition readout (hdlab/diagnostic_context_wsd.py), recomputed per population: a_s 0.307 (41M w2v) / 0.309-0.316 (this session's recomputes); parameter-free bag 0.281-0.282; MFS overall 0.6831. Every arm gated on the diagnostic floor's value on its OWN population."
controls: "STRICT document-disjoint (even/odd docs) throughout; shuffled-context twins LOSE CI-sep (context2vec +0.048/+0.141; settling +0.134; grounding real-vs-twin +0.045); shuffled-sense / shuffled-clean-score twins; ORACLE DECOMPOSITION (oracle-query isolates the KEY side = 0.000 unwinnable; oracle-context-query isolates the in-context ceiling = 0.853); MATCHED-SCALE comparison (encoder vs diagnostic both at 41M); COVERAGE LADDER (lift vs clean-knowledge coverage, SyntagNet vs +ConceptNet); paired bootstrap with CI + null p95. Each excludes: leak / info-free-shape / key-side-loss / signal-absent / representation-artifact / raw-coverage-confound."
files_changed: "experiments/exp_sg_lite_context2vec_encoder_wsd_v1.py, experiments/exp_sg_lite_predictive_coding_encoder_wsd_v1.py, experiments/exp_sg_lite_grounded_settling_readout_v1.py, experiments/exp_sg_lite_signal_loss_decomposition_v1.py, experiments/exp_sg_lite_iterative_settling_sense_selector_v1.py, experiments/exp_sg_lite_sense_aware_context_ceiling_v1.py, experiments/exp_sg_lite_clean_knowledge_context_relevance_v1.py, verification/test_contextual_ceiling_signal_loss.py, data/exp_sg_lite_context2vec_encoder_wsd_v1/*, data/exp_sg_lite_grounded_settling_readout_v1/*, data/exp_sg_lite_signal_loss_decomposition_v1/*, data/exp_sg_lite_iterative_settling_sense_selector_v1/*, data/exp_sg_lite_sense_aware_context_ceiling_v1/*, data/exp_sg_lite_clean_knowledge_context_relevance_v1/*"
reverify: ".venv/Scripts/python.exe verification/test_contextual_ceiling_signal_loss.py"
---

## What was asked, and what the disk says

The brief: build a self-supervised glass-box CONTEXTUAL input encoder (context2vec/ELMo-style) and prove it
raises `a_s` (accuracy on the SPECIFIC subordinate sense) CI-separated over the bag (0.283) and the wired
biased-competition readout (~0.33); the brief's hypothesised fork past the glass-box ceiling was a TRANSFORMER.

**The disk says the encoder does NOT cross, the transformer fork is the WRONG brain-faithful answer, and the
real lever is CLEAN KNOWLEDGE AT SCALE.** All numbers strict document-disjoint SemCor, subordinate senses,
subject-weighted `a_s`, glass-box, NO external LLM.

## 1. The contextual encoder does not cross (matched scale) -- the located negative

`exp_sg_lite_context2vec_encoder_wsd_v1` -- a genuinely contextual, self-supervised **bidirectional LM**
(OUR model; forward+backward LSTM whose boundary states never consume the target token; learned input+target
embeddings; negative-sampling cloze objective; 41M tokens; GPU-trained; persisted static asset; no LLM). Best
arm `a_s = 0.293` vs the parameter-free bag 0.282 (+0.012, NOT CI-sep) and vs the wired diagnostic readout at
matched 41M scale 0.307 (**-0.014, below**). Shuffled-context twins LOSE CI-sep (+0.048 within-sentence,
+0.141 cross-item) -- the ~0.29 is real structure, but it does not beat the readout. `C2V=0.276`,
`diag_C2V=0.289`, `bag_C2V=0.293`, `leak=0.283` (reading the target token, the v2-failure mode, ties the bag).

**Honest scale caveat (do not overclaim):** 41M tokens is ~2% of context2vec's real training scale (ukWaC
~2B) and rare-sense accuracy is the most scale-sensitive dimension (Zhang et al. 2021; BabyLM). So this is a
MATCHED-41M negative (encoder < diagnostic at the same scale), NOT a proof that a much larger glass-box encoder
could not climb -- but the literature bounds even that: the non-transformer LFS band is 31-37% (BEM Table 2:
EWISE 31.2, frozen-BERT-baseline 37.0), and only a transformer reaches 52.6. Our 0.31 sits squarely in the
glass-box band. (The predictive-coding encoder run, `exp_sg_lite_predictive_coding_encoder_wsd_v1`, was killed
mid-training as an inefficient config; it is not needed -- see section 2, which supersedes the whole
frozen-encoder route.)

## 2. The brain's EXACT mechanism is saturated -- the transformer fork is refuted as the brain answer

The frozen query-key encoder (context2vec) is un-faithful on two axes: the brain does not encode context into a
query and cosine-match a fixed sense-list, and the brain does not freeze. Its actual mechanism (ORGAN_MAP F5;
Hoffman, McClelland & Lambon-Ralph 2018, Psychol Rev, primary-verified) is **iterative joint constraint
satisfaction**: the word's dominant-biased representation is RESHAPED by context via recurrent settling over one
continuous distributed space; context is fed back as a constraint; the hub settles into the region fitting BOTH
word and context; dominance = attractor-basin depth. Built faithfully, glass-box, no frozen encoder
(`exp_sg_lite_iterative_settling_sense_selector_v1`):

| arm (n=2675 subord test) | a_s | vs one-shot readout |
|---|---|---|
| one-shot biased competition (the wired readout) | 0.312 | -- |
| **iterative joint settling (K=8, context constraint fed back)** | **0.312** | **-0.0004, NOT sep** |
| + word-anchor (start from the word's lexical rep) | 0.313 | neutral |
| + dominance-depth (frequency baked into basin depth -- the brain's own mechanism) | **0.251** | **HURTS** |

The info-free (shuffled-context) twin LOSES CI-sep (+0.134), so the mechanism is real -- it just extracts no
more than one pass. **Iteration adds nothing; the brain's dominance mechanism actively HURTS subordinate
selection** (dominance is a headwind -- subordinate senses are hard for the brain's mechanism too; the human
least-frequent-sense ceiling is unmeasured and plausibly <=60%, far below the pooled 67-80% WSD ITA). The
readout mechanism is saturated; a transformer would cross by LEARNING the gold-blind weighting from billions of
tokens, but that is scaling an ML tool, not the brain's mechanism -- and it is not needed to locate the lever.

## 3. WHERE the signal is lost (oracle decomposition; `exp_sg_lite_signal_loss_decomposition_v1`)

| measurement (subord test, n=2675) | value | what it isolates |
|---|---|---|
| a_s (wired diagnostic) | 0.312 | the operating point |
| **KEY-unwinnable** (oracle-query = a sense's own gloss still fails) | **0.000** | the sense keys are ALWAYS separable -- 0% of the loss is the key side |
| **QUERY-loss** (oracle-separable but the real context query mis-points) | **0.688** | **100% of the loss is the context query** |
| **oracle-context-query ceiling** (best weighting of the ACTUAL w2v context words toward gold) | **0.853** | the disambiguating cue IS in the local context (only 14.7% have no discriminating word) |
| gloss separation of rare vs dominant twin (1-cos) | 0.115 | genuine topic twins (cos~0.885) |
| supervised context-usage key | 0.212 | a topic-blur usage key is WORSE than the zero-shot gloss |

**The entire loss is the context query, the sense keys are perfect, and the cue is 85% present in the plain
w2v context.** The wall is GOLD-BLIND RELEVANCE WEIGHTING -- finding WHICH context words bear on the true sense
without the answer -- not sense-conflation of the input: `exp_sg_lite_sense_aware_context_ceiling_v1` shows
that REPLACING context words with their gold-sense glosses HURTS (0.356->0.304) and correct-sense is worse than
random-sense, i.e. the plain w2v already carries the info better than any sense-resolved gloss. Grounding
(`exp_sg_lite_grounded_settling_readout_v1`, Lancaster 39,707-word sensorimotor norms) is real but redundant
(grounded-only 0.204, beats its twin +0.045, but fuses to weight 0); attractor-settling readout
(`iterative_attractor`, `modern_hopfield_readout`) ties cosine (0.308).

## 4. The brain-faithful lever: CLEAN knowledge guiding biased competition (`exp_sg_lite_clean_knowledge_context_relevance_v1`)

The brain's biased competition is guided by WORLD KNOWLEDGE -- the candidate meanings direct attention to the
discriminating context features. Supplying that as a CLEAN, high-precision relevance signal (does a candidate
sense's known clean collocate literally appear in the context?) feeds the wired mechanism the signal
w2v-variance misses:

| level (n=2675 subord test) | clean-knowledge coverage | a_s (fused with diagnostic) | lift vs diagnostic |
|---|---|---|---|
| diagnostic only (wired) | -- | 0.316 | -- |
| + SyntagNet + WordNet relations (curated) | 0.52 | 0.322 | **+0.006 to +0.012** (directional; fragile, edge of sig) |
| + ConceptNet (broader, noisier) | 0.76 | 0.312 | **-0.004 (REGRESSES)** |

**Clean knowledge is directionally the lever; noisy knowledge regresses it.** A single favorable-weight run
gave +0.0116 CI-sep with the twin losing, but the cleaner coverage-ladder recompute gives +0.006 not-separated
-- so the honest claim is a MARGINAL, FRAGILE directional lift, and broader-but-dirtier knowledge HURTS. This
is the parent's consolidation finding, re-derived on the QUERY side: growth must be CLEAN. Crossing the ceiling
decisively needs much richer, consolidated, clean world knowledge -- a program (learner-on + grounding +
consolidation), not a readout-side fix.

## KEY REALIZATIONS
- **The loss is 100% the query, 0% the keys, and the cue is 85% in-context** (oracle decomposition). This turns
  "contextual input encoding is the ceiling" from a slogan into a measured fact and kills the sense-embedding /
  grounding / key-side directions in one shot.
- **The brain's EXACT mechanism (iterative joint settling) equals the one-shot readout, and its dominance
  mechanism HURTS subordinate senses.** The readout machinery is saturated -- the enabling move was building
  the brain-faithful settling with NO frozen encoder and measuring it, rather than assuming a fancier readout
  or a transformer would help.
- **Sense-resolving the context via glosses HURTS (correct < random).** The plain w2v context already carries
  the info; the wall is gold-blind RELEVANCE, not representation. This refuted my own "sense-conflation is the
  ceiling" hypothesis by measurement.
- **Clean knowledge nudges up; noisy knowledge regresses.** The lever is consolidated-knowledge richness, and
  scaling it DIRTY backfires -- which is exactly why the consolidation gate is the real next build.

## What I did NOT establish / would withdraw first
- **NOT established: that a much larger (277M-2B) glass-box contextual encoder cannot climb.** My encoders are
  41M (~2% of context2vec). The MATCHED-41M negative + the literature LFS band (non-transformer 31-37%) bound
  it, but I did not train a large glass-box encoder. If forced to withdraw one claim, it is any implication
  that scale is fully ruled out for the encoder route.
- The single-run +0.0116 CI-sep clean-knowledge lift is WITHDRAWN in favour of the ladder's +0.006 not-sep
  (train-selected weight fragility). The robust claim is "marginal, directional; must be clean."
- The predictive-coding encoder (PC-SG) full number was not obtained (config killed for inefficiency); it is
  not load-bearing (section 2 supersedes the frozen-encoder route).

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
- The sense readout is at its information ceiling: iterative joint constraint-satisfaction settling (Hoffman
  2018, the brain's exact mechanism) = one-shot biased competition on subordinate a_s (0.312 vs 0.312), and
  dominance-weighting (attractor-basin depth) HURTS subordinate selection. Record biased competition as PINNED
  and SATURATED for this task; the residual is NOT a readout/mechanism gap.
- The ceiling is the FOUNDATION, not the encoder or the readout: 100% of the loss is gold-blind query relevance
  over a thin distributional foundation; the cue is 85% in-context. `predictive_coding.py` / `n400_coherence_
  monitor.py` embody the running-state error mechanism but are not the lever here.
- Grounding (Lancaster) is a real but redundant channel for topic-overlapping polysemy (static per-word norms
  are sense-blind by construction -- Trott & Bergen 2022); contextual grounding is the untested variant.

## FOR STRATEGY -- proposed hdlab changes + the redirect
1. **No new hdlab wire from this problem.** The wired `diagnostic_context_wsd.py` is already the saturated best
   readout; nothing here beats it robustly. Do NOT land the contextual encoder (below the readout) or the
   grounded/settling readouts (tie or lose).
2. **The redirect (the real deliverable): the lever is CLEAN-KNOWLEDGE RICHNESS AT SCALE, applied to the QUERY
   side.** This is the priority-1 sibling `build_the_controlled_knowledge_growth_consolidation_gate_for_the_
   learner`. This problem adds a NEW, measured requirement to it: the consolidation gate must feed clean
   relevance not only into sense SIGNATURES (keys, already saturated) but into CONTEXT relevance (the query --
   where 100% of the loss is), and it must be CLEAN (ConceptNet-noise regresses -0.004; SyntagNet-clean nudges
   +0.006 to +0.012).
3. **Do NOT take the transformer fork as "the answer."** It would cross by scaling an ML tool; the brain-
   faithful route to the same in-context 0.85 ceiling is a richer, consolidated, continuously-learned world-
   knowledge foundation -- the project's own north star.

## TLDR (plain language)
To pick a word's rare meaning, we proved the computer already knows the dictionary meanings apart perfectly and
that the clue is sitting right there in the sentence 85% of the time -- the whole problem is that it can't tell
WHICH surrounding words are the clue without already knowing the answer. We built the brain's actual method for
this (letting the meaning settle under the pressure of the surrounding words) and it did no better than the
simple one-shot method -- and the brain's habit of favouring a word's common meaning actually makes rare
meanings HARDER, for us and for people. The one thing that helped at all was giving it clean, curated facts
about which words go with which meaning -- a small, shaky improvement -- and giving it MESSIER facts made it
WORSE. So the fix is not a bigger AI model; it's a much richer, carefully-cleaned store of world knowledge,
grown by reading -- which is exactly the project's main goal already.

## QUESTIONS
None blocking. One judgement flagged: I mark this PARTIAL rather than the brief's "located-negative = FULL PASS"
because I found a real (if marginal) positive direction (clean knowledge) and did not train a large-scale glass-
box encoder -- so it is an honest "the lever is elsewhere, shown directionally," not a clean "impossible."

## NEXT STEPS
1. **[REDIRECT] Fold the finding into `build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner`:**
   the consolidation gate must supply CLEAN CONTEXT-RELEVANCE knowledge (the query side, 100% of the loss), and
   must reject noisy knowledge (measured: ConceptNet regresses). That is the brain-faithful lever.
2. Do NOT build a larger frozen encoder or a transformer for this task on brain-fidelity grounds; if scale is
   ever tested, it is an ML-baseline curiosity, not the north star.
3. The wired diagnostic readout stays as-is (saturated best).
