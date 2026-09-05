---
owner_verdict: DONE
---

SUBMISSION — grow_broad_coverage_correctly_resolved_rare_sense_experience_the_meaning_channel_learner_on
status: PARTIAL (WIP until owner_verdict: DONE). Glass-box, NO external LLM/transformer/training at inference.
NO hdlab written (Q111 — strategy lands the wire). Ledger malformed/incomplete: 0.
reverify: .venv/Scripts/python.exe verification/test_rare_sense_episodic_coverage_growth.py   # 26/26, deterministic
scorer/pop: subject-weighted a_s on strict document-disjoint SemCor SUBORDINATE senses, n=2676, via the wired
hdlab/diagnostic_context_wsd, frozen 200-dim w2v.

THE WINNER (the landable deliverable) — the IDEAL brain-foundational readout, assembled from every component that
proved to help, each stage the brain's actual operation:
  S1 ATL hub-and-spoke keys 0.314 → S2 LIFG/pMTG precision retrieval 0.336 → S3 BAYESIAN competition 0.387 [PEAK]
  → S4 +CLS episodic memory 0.379 (REDUNDANT, −0.008 n.s.).
  S3 = argmax(log P(sense) + w·precision_weighted_context): frequency enters as a DECAYING RESTING BIAS (regularizes
  implausible ultra-rare senses), STRONG CONTEXT decides — the brain's frequency-modulated competition (MacDonald 1994
  / McRae competition-integration), linearized. Dev-selected (gamma=2.0, top-k=0, w=5.0 on EVEN docs), ODD test:
  rare-sense a_s 0.316 (wired) → 0.387, +0.065–0.072 CI-sep; coarse 0.49 → 0.57; shuffled-context twin LOSES; strict
  PARETO win over the wired readout (all-pop 0.456 → 0.629, no regression). Bigger than P9's precision-weighting
  (+0.023) and STACKS with it.

GENERALIZES (FROZEN SemCor weights, ZERO re-tune) — Bayesian>wired holds CI-separated 6/6: NOUN +0.052, VERB +0.047,
high-skew-freq +0.059, low-skew +0.041, a FRESH mod-3 document split +0.037, ALL +0.050. Not a tuned-split artifact.
(Caveat: all within SemCor/one inventory; cross-corpus WiC/SemEval is the one untested axis.)

THE BAR's OWN VERDICT (separate from the winner) — a full-pass LOCATED NEGATIVE. Following the owner's principle
("when all are brain-faithful the capability emerges"), every component was made faithful: episodic MINERVA-2 max-echo
(hippocampal single-trace) beats prototype-averaging (twin +0.038 CI-sep); online PBV-v2 (grounding-anchored propose +
cross-encounter Bush-Mosteller verify + prioritized replay + consolidation gate) makes clean traces (covered pure
0.763 vs twin 0.707); reading grows coverage 0.14→0.47 (lemmatized). But the deployed rare-sense a_s does NOT robustly
cross the fine bar even fully faithful. NAMED CAUSE (triangulated 4 ways: P9 chain + all-faithful build + literature
scan + polysemy/homonymy decomposition; and disk-exhausted — AutoExtend/DeConf-PPR/recurrent-settling all located
negatives): the residual is the FROZEN INPUT REPRESENTATION — every glass-box operation (readout, memory, coverage)
reads the SAME thin w2v context, so the readout IS the ceiling; the faithful fix is a contextual per-occurrence
encoder = the §2 invariant boundary.

MORE-HUMAN-LIKE (the brain's own grain): coarse/supersense scoring (humans agree ~0.90 vs ~0.72 fine) → the SAME
mechanism reaches ~0.50 on rare senses (coarse R3 beats coarse-MFS +0.204 CI-sep, coarse-random +0.134 CI-sep).
Decomposed by the brain's polysemy/homonymy split: 71% genuine HOMONYMY (a real ~11-way task; the residual), 29%
POLYSEMY (the brain's graded core — near-solved, coarse 0.848; fine "error" there is the split the brain does not make).

CONTROLS (each excluded a rival; several caught false leads): shuffled-context / shuffled-trace / shuffled-role twins
(all lose CI-sep on the arms that carry signal); count-normalized echo beats raw-summed MINERVA-2 +0.096 (Zipf-swamp);
strict INDUCTIVE (external growth corpus test-disjoint); coverage-aware vs NAIVE deploy (isolates the uncovered-
competitor contamination); cls_growth.rollback_gate ACCEPTs safe growth / ROLLs-BACK naive (random control
unprotected); MFS no-regression on the full head+tail population; DEV-SELECTED weights (no test-tuning), reproduced
on a fresh split.

RESEARCHED LOCATED-NEGATIVES / SKIPS (do NOT reinvest): selectional/thematic-role prior HURTS (dominant-biased;
shuffled-role twin beats it); syntactic-frame cue = verb-only <1%-aggregate scalpel, our target is 60% nouns → SKIP;
true nonlinear recurrence over-competes (worse than the linearized Bayesian); episodic-in-the-recurrent-loop
over-amplifies noise; the glass-box contextual-re-representation routes (AutoExtend, DeConf/PPR, recurrent settling)
are disk-exhausted.

FILES: experiments/exp_rare_sense_{episodic_vs_prototype, propose_verify_episodic, pbv_v2_brain_faithful,
coverage_growth, all_brain_faithful, full_chain_signal_loss, polysemy_homonymy, selectional_pruning,
recurrent_competition, best_readout, ideal_full_solution, ideal_generalization, cls_rollback_safety,
trace_sharpening}_v1.py ; verification/test_rare_sense_episodic_coverage_growth.py (26/26). AUDIT UPDATE folded for
BRAIN_FOUNDATIONAL_AUDIT §2b (the WSD input needs a CLS PAIR — hippocampal episodic + neocortical prototype — over a
re-computed input; the substrate had only the prototype half).

FOR STRATEGY (Q111): LAND the winner — add `sense_prior` + `prior_weight` to hdlab/diagnostic_context_wsd (default
prior_weight=0 = byte-identical); combine in log-space with the precision-weighted context. Dev-select w on a
held-out split. Verdict-independent, generalizing, MFS-safe. DO NOT land the episodic/coverage machinery (redundant
over the readout until the input is richer) or any dominant-biased prior.

NEXT STEPS FOR OPTIMIZATION (ranked):
  1. LAND the Bayesian+precision readout (immediate, verdict-independent).
  2. CROSS-CORPUS generalization: adapt the frozen-weight readout to WiC / SemEval all-words (the one untested axis).
  3. §2 INPUT-REPRESENTATION DECISION: the readout is the glass-box ceiling; the only path past it is a richer
     per-occurrence input (a contextual encoder = the invariant boundary). If relaxed, the shelf-ready CLS episodic +
     coverage-growth machinery becomes non-redundant.
  4. ADOPT the coarse/polysemy-merged grain as the meaning channel's evaluation (fine understates comprehension ~0.18,
     no neural grounding); keep fine only for the homonymy subset.

DO NOT QUOTE: the episodic/coverage deploy as a bar-crosser (it does not robustly cross fine); the coarse ~0.50 as a
fine-grained number; "~half the wall is inventory artifact" (corrected — 71% is real homonymy); 0.53/0.72 (transformer
LFS / human ITA) as achievable glass-box fine-grained.

TLDR (plain English): We built the best brain-faithful way to pick a word's meaning in a sentence and one piece won:
combine a meaning's base rate gently with strong sentence clues (the brain's way), which lifts rare-meaning accuracy
from 0.32 to 0.39 — and to 0.57 at the level people actually distinguish meanings, with closely-related meanings
nearly solved (0.85). It generalizes: with settings locked it improves nouns and verbs, common and rare words, and
documents it never tuned on — six for six. A clarifying surprise: the "memory of past uses" adds nothing once the
read-out is done right, because both read the same fixed word-vector — which is the one real bottleneck. So the
read-out is now as good as it gets without a big context model; the only thing left is that fixed word-vector, which
is your call.

QUESTIONS: one, the owner's — hold the no-transformer invariant (the read-out is the proven glass-box ceiling; the
rare-sense capability is real and human-like at the right grain) or relax it for one offline contextual input encoder
to push the fine number toward ~0.53? Optional: want the WiC cross-corpus generalization test?

NEXT STEPS: (1) land the readout win. (2) your §2 decision. (3) optional cross-corpus (WiC). (4) adopt the
coarse/polysemy-aware evaluation grain.
