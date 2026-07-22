# Pre-reg: reader_image_word_grounding_v1

**Date:** 2026-07-21
**Anchor:** reader_image_word_grounding_v1
**Cell:** experiments/exp_reader_image_word_grounding_v1.py
**Class:** per-instance PERCEPTION grounding brick (word <-> image-referent). LOCAL only, no bank.

## Question (measured, not asserted)
Can encoded McGuffey First Reader illustrations be told apart enough to ground DIFFERENT
words to DIFFERENT images? Report the honest discrimination bound. Raw-pixel HD (rung-1) vs
glass-box Sobel edge (rung-2) vs Otsu ink (rung-2b). The recon (_probe_hd_encoder_woodcuts.json)
measured rung-1 inter-image cosine 0.34-0.53 (MEASURED@ that file) = background-domination ->
expect rung-1 discrimination WEAK; does edge/ink isolation help?

## Compute architecture
- class: sequential-CPU with justification (numpy record-encode + PIL/scipy front-ends).
- wall time: < 60s total (59 imgs x 3 rungs x 5 seeds; ~2.5M mults/encode). LIGHT cell.
- storage strategy: no_composition single-hop associative retrieval; additive superposition
  memory (bundle of binds) is the grounding store. Load sweep isolates capacity from separability.
- routing: LOCAL foreground to completion (task = LOCAL only, no push/persist). Not remote.

## Design gate (verified at self-test / smoke)
- REAL baseline: chance = 1/N_img (~0.017) + SCRAMBLE control (permuted word<->image pairing).
- CAN-FAIL: discrimination at chance = raw-pixel grounding does NOT work = honest negative
  (-> rung-2 / better encoder needed). Either direction is a valid landing.
- ONE variable: image front-end (raw / edge / ink); positions, levels, words, store, retrieval
  all identical across rungs.
- MULTI-SEED: 5 seeds over (encoder position/level base seed, word-HD seed).
- discriminating band: LOAD SWEEP P in {8,16,32,64,all}; low-load P=8 has minimal crosstalk so
  a rung failing at P=8 = pure separability bound; passing at P=8 but failing at all = capacity.

## Bands (HYPOTHESIZED)
- GROUND_ACC1_MIN = 0.20  (word->image acc@1 for a rung to count as "grounding works"; >11x chance)
- GROUND_ACC3_MIN = 0.35
- SCR_DELTA_MIN = 0.10    (true acc@1 - scramble acc@1; a "works" rung MUST clear this -> real assoc)
- CHANCE_EPS = 0.05
- SEP_COS_TARGET = 0.20   (image-codebook mean off-diag cosine for "separable"; recon rung-1 ~0.4)

## Verdict logic
- rung_works(r) = (w2i_acc1_mean >= GROUND_ACC1_MIN) AND (scramble_delta >= SCR_DELTA_MIN)
- PASS_GROUNDING if any rung works (report best rung + rung2-rung1 delta)
- HONEST_NEGATIVE_AT_CHANCE if all rungs w2i_acc1 <= chance + CHANCE_EPS (raw+edge grounding at
  chance -> which ladder rung does woodcut grounding need? report the bound)
- MIDDLE_BAND otherwise (above chance, below works threshold)

The SCRAMBLE control is the must-fail discipline: it PREVENTS a false PASS (a rung that scores
via base-rate keeps accuracy under scramble; a real-association rung collapses to chance).

## Self-test asserts
- bind/unbind involution exact (bsc self-inverse)
- encode_record bit-identical to hdlab.binding.bsc_bind/bsc_bundle
- rung-2 edge front-end SPECIFIED-not-learned: Sobel of flat bg == 0 (bg suppressed); bright
  square -> edge energy on BORDER not interior; deterministic (two calls identical)
- round-trip grounding works on separable synthetic set; SCRAMBLE collapses it
- arms differ (raw vs edge level grids)
- no-nondeterministic-seeding static scan of source

## Schema-vet fields
- arms_differ_verified: true
- final_metrics_atomicity: tmp_replace
- crlb_n/a: discrimination is retrieval-vs-chance + scramble delta, no analytic noise-floor cap
- deterministic_seeding: true (fixed int seeds; no hash()/list(set()))
- progress_logging: print_flush_true
- cardinality_ok: n_units = n_seeds; per-rung load-sweep counts surfaced in metrics
- baseline_in_band: chance floor 0.017; scramble is the fire gate (AG-style)

## Pairing
Source: data/exp_textbook_extract_mcguffey_v1/mcguffey_first_structured.json (kind==illustration).
nearby_text (rel above/below/overlap) -> content words -> concrete-object nouns via WordNet
lexname filter (glass-box). Clean pairs = words appearing in exactly one image. Probe counts
(MEASURED@ inline probe 2026-07-21): n_img=59, n_word=190, n_clean_pairs=112, chance_w2i=0.0169.

## SMOKE-DRIVEN DESIGN ADDENDUM (2026-07-21, in-flight correction)
Smoke revealed keyed word->image retrieval SATURATES for ALL rungs (w2i@1 ~1.0). Root cause:
unique orthogonal word-keys isolate the retrieval by KEY, so image separability (the recon's
background-domination concern) barely bites -- retrieval only breaks if inter-image cosine
approaches ~1.0, but woodcuts top out at ~0.5. So keyed retrieval is ENCODER-INSENSITIVE and the
rung discriminator does NOT fire on it (DISCRIMINATOR-MUST-SURVIVE-SCALE / META_RULE_AG). Full N=10000
keyless noise-discrim (bit-flip to f=0.45) ALSO saturates (offdiag cosine <=~0.5 is ~50-sigma at
N=10000). ADDED a DIMENSIONALITY-STRESS discriminator (STRESS_N in {125,250,500,1000}, corruption
f=0.40): shrinking N raises confusion so the rung with the LOWEST off-diagonal cosine sustains the
lowest N. This is the fire gate + true-separability ranking. Fire condition: spread across rungs at
lowest N >= 0.05. This addition is exactly what the smoke gate is for -- caught a vacuous saturated
discriminator before treating it as the answer.

Reported metrics separate: (1) keyed grounding round-trip = the "does it recall" headline (PASS);
(2) full-N keyless noise-discrim + off-diagonal cosine = separability; (3) N-stress = the fired
discriminator ranking the rungs. Honest either way per the task.

LOCAL ONLY: commit cell + metrics locally, NO push / persist / bank. Skunkworks VETs on land.
