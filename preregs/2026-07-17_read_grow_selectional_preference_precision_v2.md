# Prereg: read_grow_selectional_preference_precision_v2

**Filed:** 2026-07-17. **Cell:** `experiments/exp_read_grow_selectional_preference_precision_v2.py`.
**Revival of:** v1 (`exp_read_grow_selectional_preference_precision_v1.py`, commits bc1246773+a91a8780c),
HARD_FAIL, redesigned per skunkworks VET finding that v1 did not isolate signal from integration (drop
pattern statistically indistinguishable from random, z=+1.21; the +0.135 ARM_SELECTIONAL-vs-ARM_SURFACE gap
was confounded by a scoring-FUNCTION difference, not a meaning-vs-frequency difference).
**Full rationale:** see the cell's own module docstring (load-bearing source; this file summarizes bands/
gates for SCHEMA-VET, not a restatement to be trusted independently of it).

## Question
Does a glass-box, non-neural, SOFT selectional-preference rerank -- applied at genuine near-tie ROLE-
ASSIGNMENT decision points inside the trained transition parser's (74f8de97a) own arc-eager decoding, scored
by a WSD-based (NLTK Lesk) verb x argument-CLASS PPMI table learned from TRAIN -- raise relation-extraction
PRECISION on the held-out UD-EWT TEST slice over (a) the unmodified BASE parser, (b) a meaning-blind
apples-to-apples surface-frequency control (IDENTICAL scoring function, token-keyed instead of class-keyed),
and (c) a must-fail RANDOM-NULL control (identical near-tie mechanics, random choice instead of plausibility)?

## Four mandatory fixes vs v1 (verbatim mapping, see module docstring for full detail)
1. SOFT integration at near-tie decision points (SoftGatedTransitionParser rerank), not a hard post-hoc gate.
2. WSD-based (NLTK Lesk) argument class, not v1's first-synset heuristic.
3. Apples-to-apples surface control: IDENTICAL PPMI-with-floor formula for both class and surface tables.
4. Larger N (EVAL_N=500 vs v1's 210) + an explicit ARM_RANDOM_NULL must-fail control for the decomposition,
   with power reasoning stated (see module docstring COMPUTE + `power_reasoning` prereg field).

## Arms
- `BASE_main`: unmodified `FixedTransitionParser` (74f8de97a), decoded via the token-based eval harness (this
  cell's own `make_row_extractor`, sourcing decoder input from the corpus's own token list, not a re-
  tokenization of raw text -- see module docstring COMPUTE for why this alignment fix was needed for the
  decomposition). Comparison floor for the other 3 arms.
- `ARM_RANDOM_NULL`: `SoftGatedTransitionParser` with `plausibility_fn=None`, `rng=Random(12345)` -- identical
  near-tie detection (same TAU) and identical competing-candidate set as the other 2 gated arms, but chooses
  uniformly at random among the competing role-assigning candidates instead of scoring them. The must-fail
  null the mechanism has to beat, not just BASE.
- `ARM_SURFACE`: `SoftGatedTransitionParser` with `plausibility_fn` = PPMI-with-floor over a verb x argument-
  TOKEN (surface lemma) table. Meaning-blind, apples-to-apples fairness control.
- `ARM_SELECTIONAL`: `SoftGatedTransitionParser` with `plausibility_fn` = PPMI-with-floor over a verb x
  argument-CLASS (NLTK Lesk WSD -> WordNet lexname) table. Meaning-conditioned, the actual build.

`ARM_RANDOM_NULL`/`ARM_SURFACE`/`ARM_SELECTIONAL` share IDENTICAL near-tie mechanics: SAME TAU (calibrated
from the ACTUAL trained model's own margin distribution, P50/MEDIAN percentile of the "top choice is a role-
assigning arc with >=1 competing role-assigning alternative" margin distribution, measured on a disjoint
CALIB_SEED=97 sample), SAME LAMBDA (`1.5*TAU/PLAUS_CLIP`), SAME MIN_CTX_EVIDENCE=2 evidence floor, SAME
PLAUS_CLIP=3.0. They differ ONLY in what selects among the competing candidates: nothing (random) vs surface
frequency vs meaning-conditioned class.

## Regime chosen AFTER a measured diagnostic sweep (design-gate: difficulty-on, not p-hacked)
The initial tight regime (min_ev=3, tau=P25) fired the discriminator too rarely to test. A MEASURED sweep
this cycle (4000-sentence-trained model, 100 real UD-EWT TEST sentences) found, per 100 sentences:
`min_ev=3/tau_P25`: 44 near-tie events, 7 with any selectional evidence, 0 flips; `min_ev=2/tau_P50`: 103
events, 21 scored, 1 flip; and appreciable flips (23) required an INDEFENSIBLE regime (min_ev=1 single-count
trust, tau=P90 perturbing ~90% of decisions, lambda 5x) -- that would be p-hacking, not signal. The
registered regime (min_ev=2 = standard PMI count-floor; tau=P50 = the MEDIAN near-tie margin = genuinely
coin-flip-competitive decisions; lambda 1.5x = a max-plausibility candidate overturns exactly the median
near-tie margin with 50% headroom) is the MOST GENEROUS still-principled setting. If the discriminator does
not fire/help here, that is an honest finding (the signal is REDUNDANT with the trained lexicalized parser's
own lemma features -- see completion report mechanism localization), NOT a threshold artifact. This is the
"difficulty-on + one-variable + can-fail" design gate satisfied by MEASURED sweep evidence, not assertion.

## Bands (declared before viewing the FULL outcome; smoke used only for TAU/LAMBDA calibration verification
and mechanism-fires checks, per the SAME discipline v1's own prereg used)
- `margin_required = max(0.05, 1.5*sqrt(base_p*(1-base_p)/n_emitted_base))` -- noise-floor-derived.
- Decomposition: two-proportion z-test on per-FLIP-event gold-participant-pair-agreement rate,
  `z_class_vs_random = two_proportion_z(class_flip_correct, class_flips, random_flip_correct, random_flips)`.
- `gate_fires = (n_neartie_events >= 100) AND (n_flips_class >= 30) AND (n_flips_random >= 30)`.
- HARD-PASS: `(sel_p-base_p)>=margin_required AND (sel_p-surf_p)>=margin_required AND
  (sel_p-random_p)>=margin_required AND z_class_vs_random>=1.645 (one-sided, alpha=0.05) AND gate_fires AND
  arms_differ_verified AND positive_control_reproduced` (Gate-D, tolerance 0.02 vs 74f8de97a's own numbers).
- HARD-FAIL: `sel_p<=base_p OR (sel_p-surf_p)<0.02 OR (sel_p-random_p)<0.02 OR z_class_vs_random<0 OR
  NOT gate_fires OR NOT arms_differ_verified OR NOT positive_control_reproduced`.
- MIDDLE_BAND: otherwise (e.g. precision gain clears margin vs base/surface but z is between 0 and 1.645 --
  directionally suggestive, not significant; or z clears but the raw precision gain does not).
- HP_SCOPE: the precision comparison + decomposition gates apply to ARM_RANDOM_NULL/ARM_SURFACE/
  ARM_SELECTIONAL; BASE_main is scored as the comparison floor + the Gate-D positive-control target (via
  74f8de97a's own TEXT-based harness, reused unmodified, SEEDS_FULL=[7,13,19]/N_PER_SEED=70).
- Gate-D repro regime: ALWAYS the full pooled 3-seed regime compared against 74f8de97a's full-pooled prior
  (0.3472/0.3095), regardless of this cell's run_mode (base parser is full-corpus-trained in both smoke and
  full, so the repro regime is run_mode-invariant -- fixes v1's iteration-1 smoke-vs-pooled-prior bug).

## Power / N reasoning (criterion 4, mandatory)
Two-proportion sample-size formula: `n_per_arm = (z_a/2+z_b)^2*(p1(1-p1)+p2(1-p2))/(p1-p2)^2`. At
p1=0.35/p2=0.50 (a plausible baseline flip-correctness range), alpha=0.05 one-sided, 80% power: n~=166
FLIP events per arm needed to detect a 15-point gap. A standalone MEASURED calibration probe this cycle
(3000-sentence-trained model, 40 real UD-EWT TEST sentences, 943 total parse steps) found 83 "top choice is
a role-assigning arc with a competing alternative" events (~2.07/sentence) -- projecting to ~1000 candidate
near-tie events at EVAL_N=500 (vs v1's 34 sentence-level "drops"), ample headroom for the decomposition
PROVIDED the flip rate (fraction of near-tie events where evidence exists AND changes the ranking) clears a
low bar. The ACTUAL measured `n_neartie_events`/`n_flips` are reported in metrics, not assumed; `gate_fires`
is the pre-registered floor (100 events, 30 flips/arm) below which the cell honestly reports HARD_FAIL
(insufficient power to run the test) rather than a false MIDDLE_BAND comfort read.

## Self-test / smoke status
Self-test (SELFTEST_N_TRAIN=500, 10-sentence real TEST slice): PASS -- real train, real Lesk-based table
build (n_joint=1708, 27 classes, 712 surface keys), real Lesk WSD call confirmed ("dog" in context ->
noun.animal), real calibration pass (tau=1.432 from 21 margin samples), real 4-arm decode+score end to end,
guard sentences + OOS control pass on BASE. ARMS-MUST-DIFFER is INFORMATIONAL at this tiny self-test scale
(2/4 distinct digests at n=10 sentences/SELFTEST_N_TRAIN=500 -- expected at tiny-N per the evidence floor;
this is a SMOKE-gate hard requirement, not a self-test requirement, per THREE DISCIPLINE PATTERNS).
Smoke (eval_n=60, calib_n=20, FULL training corpus per discriminator-survives-scale Option A): status +
numbers reported in the completion report (this file is filed before smoke completes; smoke is a
calibration/mechanism-fires check only, per the declared discipline -- FULL bands above are NOT touched by
smoke's outcome).

## Compute / timeout
`--timeout 1800` (measured components: train ~150-400s host-contention variance; table-build ~33s projected
from a 2000-sentence Lesk timing probe (5.19s -> 32.6s at 12544 sentences); calibration ~2s; 4-arm EVAL_N=500
decode ~50-80s; Gate-D repro decode ~5s; total measured/projected <=550s; 1800s retains >=3.2x safety margin).
Sequential-CPU, local, run INLINE/foreground (local_cpu_queue runner intentionally down this cycle). No
GPU/atoms/push/remote-persist. Storage: no_storage.

## Deferred
Error-driven surprisal-scaled update loop (Chang/Dell/Bock; McClosky self-training) -- explicitly gated
behind this cell demonstrating independent signal, per the research note's own sequencing discipline (same
deferral v1 declared).

## Prior-work check
`bash tools/substrate_query.sh` run before authoring this cycle: top hits at cosine<=0.3398 were generic/
unrelated (substrate-architecture integration note, distillation-ratio routing note, FrameNet
Transition_to_a_situation frame, an unrelated task-selection prereg) -- none are prior selectional-preference
arc cells. Confirms this is a genuine revival/redesign of v1, not a rediscovery.
