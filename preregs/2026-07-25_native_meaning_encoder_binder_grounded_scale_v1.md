# Pre-reg: native meaning encoder @scale -- BINDER-GROUNDED primary + distributional baseline

anchor(primary, PENDING DATA): `native_meaning_encoder_binder_grounded_v1`
anchor(baseline, BUILT+SMOKED): `native_meaning_encoder_scale_v1`
date: 2026-07-25
author: exp_dev
status: DESIGN-GATE (baseline smoked HARD_PASS; primary blocked on Binder dataset fetch -> Director)

## Pivot (Director REDIRECT, USER steer "use the correct brain-aligned meaning that already exists")
The distributional text-prediction objective risks re-deriving thin native GloVe (= the meaning wall).
Ground the encoder in a BRAIN-DERIVED feature space (Binder experiential feature norms = operationalized
Barsalou grounding, 65 attributes with known neural correlates) instead. Distributional-text-prediction
is RETAINED as a baseline arm (already built + smoked) so we can show grounded > distributional (or not,
honestly).

## Grounded design (primary)
1. GROUNDED CORE (supplied axiom; allowed foundation-from-vetted-tool, NOT a borrowed distributional
   encoder): Binder et al. 2016 experiential semantic feature norms -- 535 concepts x 65 human-rated
   (0-6) experiential attributes grouped in 14 brain-system domains (Vision/Somatic/Audition/Gustation/
   Olfaction/Motor/Spatial/Temporal/Causal/Social/Cognition/Emotion/Drive/Attention). These human-rated
   vectors ARE the grounded meaning.
2. EARNED EXTENSION (brain's way, error-driven; the GPU-scale job): the substrate LEARNS to predict a
   NEW concept's 65-dim Binder vector FROM ITS RELATIONS (WorldTree typed relations) + context
   (ARC_Corpus), by error-driven differentiation (Rogers-McClelland). HARD CONSTRAINT: earn the
   extension from RELATIONS/context, do NOT Feature2Vec-project it from GloVe/BERT (that reintroduces
   borrowed distributional meaning and defeats the point). Feature2Vec (arxiv 1908.11439) is a METHOD
   reference only.
3. ENCODE the 65-dim grounded feature vectors into HD substrate codes.
4. YARDSTICK: the v2 property-discrimination held-out task (exp_composed_differentiation_loop_v2). Does
   GROUNDED-feature meaning beat distributional frozen-GloVe (0.554) on held-out property discrimination,
   AND does the earned extension GENERALIZE to held-out concepts (what distributional AND binding both
   failed at)?

## Brain-consistency (carried in prereg)
Binder features = operationalized Barsalou grounding (brain-system-grounded; the phase-committed piece).
Supplied grounded core = axioms (allowed). Earned extension via error-driven differentiation over
relations = the brain's learning (Rogers-McClelland). NO borrowed distributional encoder inside the
learned representation.

## Arms (cos-pick held-out + in-vocab, IDENTICAL v2 items/split/candidates/gold_pos)
- chance ~0.21 (reference floor)
- native_untrained (random init) -- thin floor reference (atom-29562 native ~0.211)
- glove_zerofit -- frozen-GloVe distributional CEILING reference ~0.554 (borrowed; eval-only, never in codes)
- native_distributional (BASELINE, BUILT+SMOKED): tied-table SGNS context(ARC)+relation(WorldTree)
  error-driven encoder -- the "earn-it-like-GloVe distributionally, natively" arm
- binder_grounded_direct (PRIMARY, in-vocab): concepts WITH a Binder vector encoded to HD, cos-pick
- binder_grounded_earned (PRIMARY, HELD-OUT generalization): held-out concepts get a PREDICTED Binder
  vector from their relations/context (error-driven extension), cos-pick -- the generalization test

## Bands (a priori; can-fail; gates apply to the grounded PRIMARY arms; baselines are references)
- HARD-PASS = grounded-feature meaning held-out BEATS GloVe 0.554 AND the earned extension GENERALIZES
  to held-out concepts (held-out grounded > native_distributional held-out AND > native_untrained by a
  real margin, wilson-CI-lower above the GloVe ceiling for the direct arm).
- HARD-FAIL = grounded does NOT beat native ~0.211 / no held-out generalization (honest: even
  brain-grounded features + relation-learning do not crack held-out property discrimination here).
- MIDDLE = partial (grounded beats distributional/native but not the GloVe 0.554 ceiling, OR direct
  grounding works but the earned extension does not generalize).
- Scaling: earned-extension held-out at FULL must exceed at SMOKE (more concepts/relations -> better).

## Can-fail / design gate
Can-fail: the earned extension CAN fail to generalize (land at ~native floor). Difficulty on
(held-out-BY-CONCEPT, freq-matched distractors, gold randomized). Real baselines recomputed inline
(untrained floor, distributional arm, GloVe ceiling). ONE variable per contrast (grounded vs
distributional; earned-extension vs direct-grounding). LOCAL SMOKE before any GPU FULL spend.

## Reuse
FRESH native objective; REUSE encoder-migration GPU scaffolding PATTERNS (torch.cuda batched training,
warmup+cosine LR, chunked loop, _seed_checkpoint write_metrics, error-checking template). NOT the
teacher-distillation core (that distills borrowed BGE = the shortcut refused).

## Baseline status (native_meaning_encoder_scale_v1 -- BUILT + SMOKED)
experiments/exp_native_meaning_encoder_scale_v1.py. SMOKE (local, CPU, 211s) = HARD_PASS on its OWN
distributional bands:
  native_learned held-out = 0.369 (Wilson CI 0.319-0.422)  MEASURED@data/exp_native_meaning_encoder_scale_v1_smoke/metrics.json
  native_context_only held-out = 0.2321 ; native_untrained floor = 0.2738 ; chance = 0.1935
  gap(learned-untrained) = +0.0952 ; discriminator_fires + arms_differ + baseline_in_band + not_saturated = all True
  in-vocab native_learned = 0.9413
  glove ceiling = CITED 0.554 (gensim absent locally; FULL is gensim-free/portable)
Finding at smoke scale: the RELATION channel carries the held-out signal; the CONTEXT (distributional)
channel needs the full corpus. This is exactly why the pivot matters -- and this arm is retained as the
distributional baseline to beat.

## DATA DEPENDENCY (Director to fetch; headless web-auth/JS limits)
PRIMARY grounded core needed: Binder et al. 2016 experiential feature norms -- 535 concepts x 65
features (0-6), one concept/row, 65 feature columns. Canonical home: Medical College of Wisconsin
Language Imaging Lab "Semantic Representations" resource (https://www.neuro.mcw.edu/index.php/resources
-> "Semantic Representations"); the file is an .xlsx (WordSet ratings). Drop to
data/corpora/binder/binder2016_ratings.(xlsx|csv).
NOTE: NOVA-786 (arxiv 2505.10718, github Knowledge-and-Concepts-Lab/llm-norms-cogsci2025,
verified_matrix_cogsci2025.csv) is 787 concepts x 8202 LLM-generated properties -- NOT the 65-dim
brain-grounded Binder space; it does NOT serve as the grounded core (LLM-generated features also
reintroduce the borrowed-meaning concern). Recommend the original Binder-65.

## Contract
prereg + self-test + LOCAL SMOKE; FULL to overnight_queue (GPU) via queue_add ONLY after grounded-primary
smoke clears; metrics.json; commit cell+prereg by explicit path; NO atom banking (skunkworks owns VET);
no borrowed distributional encoder in learned codes; ASCII-only; VET-PENDING.
