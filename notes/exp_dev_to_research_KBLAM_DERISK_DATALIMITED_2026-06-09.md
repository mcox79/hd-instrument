# Exp-Dev -> Research: KBLaM de-risk INCONCLUSIVE (data-limited) -- NOT an architecture rejection; need discriminative facts

**From:** Exp-Dev  **Date:** 2026-06-09  **Re:** Path B Week-1 architecture de-risk (t5c_factkb_kblam_heldout)

## Result (read carefully -- the auto-verdict text is misleading)
HARD_FAIL on the absolute bar: held-out recall 0.049, train recall 0.060, best 0.060, gate|mean| 0.37, CE 9.8 -> ~3.0.
The verdict template said "still memorizes" -- that is WRONG. The data shows the OPPOSITE of memorization:
- train (0.060) ~= held-out (0.049): NO memorization gap (contrast Flamingo: train 1.0 / held 0.0).
- BUT train recall is ALSO ~0.06, and final CE ~3.0 ~= random over the 40-answer pool (ln 40 = 3.69; random recall = 0.025).
=> The model is not retrieving EVEN TRAIN facts. It is not memorizing or generalizing -- it is failing to RETRIEVE at all.

## Diagnosis: my de-risk DATA was inadequate, not the architecture
I used synthetic subjects = "adj + noun" combos ("crimson falcon", "ancient harbor") in identical "The secret code of the X is"
templates. Frozen bge-large embeds these near-identically (the template dominates; adj+noun barely move the CLS vector) -> ~2000
indistinguishable keys -> softmax attention can't isolate the right fact -> no retrieval, even for train. This is exactly why
KBLaM uses DBpedia ENTITIES (highly distinct, real semantic content) for discriminative keys. My synthetic keys lack that.

## Conclusion + recommendation
The de-risk is INCONCLUSIVE on the architecture's generalization -- it was bottlenecked by non-discriminative synthetic keys,
not by memorization. The architecture (every-layer rectangular + frozen-encoder W_k/W_v + answer-token CE) is implemented and
RUNS cleanly; it just had nothing discriminative to retrieve on. Two options:
1. Cheap re-de-risk: rebuild facts with DISCRIMINATIVE subjects (real DBpedia entities, or distinct multi-word names/numbers that
   bge-large embeds distinctly) at ~2000-5000 scale, re-run. If held-out climbs with train -> architecture validated cheaply.
2. Go straight to the full Path B per your spec: DBpedia 50K-100K facts + 50/50 + the 6 PRESERVE tests (Week 1-4).
My lean: option 1 first (a discriminative-data re-de-risk is ~1 GPU-hr and directly tests whether retrieval works before the 50K
engineering). Holding for your call on which. Lesson logged: de-risk data must have DISCRIMINATIVE encoder keys, or it tests nothing.
