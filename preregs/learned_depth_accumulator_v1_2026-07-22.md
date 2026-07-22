# Pre-registration: exp_agreement_learned_depth_accumulator_v1 (2026-07-22)

## Question
Can a LEARNED, glass-box, sequential subject-selector that maintains an incremental embedding-DEPTH
register (function-word -> depth update LEARNED, not hand-coded) DISCOVER the depth-opening role of
closed-class function words from the agreement signal alone, GENERALIZE to held-out-lexeme buried
subjects, BEAT the positional shortcut, and APPROACH the deterministic 0.759 ceiling (atom 29450)?

This is the LEARNED counterpart of the deterministic depth rule (29450). It fixes why every prior
inducer (29448/29449 TEM-on-VSA + attractor-select) tied majority ~0.63: those had N_STRUCT=10 LOCAL
features + a linear readout, which STRUCTURALLY cannot compute a running cumulative accumulation.

## Testbed
data/corpora/agreement/agreement_word_cache_v1.json.gz (Linzen-Dupoux-Goldberg 2016; 14761 items;
6425 buried). BURIED == subj_pos != 0. Held-out-lexeme split (disjoint subject-word pools; fixed
sha256 hash, TEST_HASH_MOD=5 cut 2 => ~40% held out). Same split family as 29443/29448/29449/29450.

## Mechanism (glass-box; build-time gradient MANUAL numpy; runtime = HARD argmin, NO autograd)
- Learn delta[w] for every closed-class candidate token (top MAX_VOCAB=160 non-noun TRAIN tokens,
  freq>=20). Nouns/content excluded (delta=0). Random init; NOTHING told about which are openers.
- Cumulative depth AT noun k = sum of delta over function-word tokens strictly before noun k
  (LINEAR in delta; depth = A @ delta). Selection score = -beta*depth + EPS_POS*pos (beta softplus,
  learned; EPS_POS=0.30 fixed tie-break toward verb-adjacent). At delta=0 defaults to nearest_noun.
- Build-time: masked-softmax select -> read number (soft) -> BCE vs label -> closed-form numpy grad
  (finite-difference-verified in self-test). Number NEVER in the selection score.
- Runtime: HARD rightmost-argmin over learned depth register, read number after. Pure numpy.

## Arms (held-out-lexeme BURIED agreement accuracy)
1. learned_depth (mechanism)  2. local_bag (SAME pipeline, the failed method's 10 LOCAL features;
ONE VARIABLE)  3. fixed_random (MUST-FAIL control: fixed-random deltas, no training)  4. nearest_noun
5. first_noun  6. deterministic_depth (0.759 positive control at test regime; Gate D)  7. majority.

## Bands (pre-registered BEFORE full; shortcut_best = max(nearest_noun, first_noun, local_bag))
HARD_PASS (ALL): (a) learned_depth - shortcut_best >= 0.05; (b) learned_depth >= 0.70;
  (c) fixed_random <= shortcut_best + 0.02 (control must-fail); (d) scramble_drop >= 0.10.
HARD_FAIL (ANY): (i) learned_depth - shortcut_best <= 0.02 (real bound: LEARNING of depth is the wall);
  (ii) fixed_random - shortcut_best > 0.05 (confound); (iii) scramble_drop < 0.05 (position all along).
MIDDLE = between (beats shortcut but < 0.70, or partial scramble).

## Discriminator-fires / fairness (all verified at smoke)
- ANTI-CHEAT depth-scramble: permute LEARNED per-noun depths (preserve multiset + positions); accuracy
  must collapse toward nearest_noun (mirrors 29450's 0.759->0.53).
- MUST-FAIL: fixed-random deltas must NOT beat the shortcut.
- number-flip invariance: selection unchanged when numbers flipped (=0.0); number read AFTER select.
- baseline_in_band (META_RULE_AG): majority + shortcuts in (0.05, 0.95).
- arms_differ (META_RULE_AF): distinct buried prediction vectors.

## Compute architecture
Class (b) sequential-CPU with justification: ~160-param linear-in-delta model; full-batch Adam,
manual numpy gradient (no torch/autograd). Smoke (3500-item slice, 2 seeds, 1500 epochs) = 16.75s.
FULL (14761 items, 5 seeds) est ~5 min. No GPU speedup (tiny model, matmul-light); GPU batching N/A.
Storage: no_storage / no_composition. Runtime is inherently sequential (incremental register) but
build-time is small matmul; wall << 10 min so sequential-CPU is the cheapest decisive method.

## Discriminator-survives-scale
Option A+B: smoke slice is a representative STRIDE sample of the full-corpus buried distribution; the
deterministic_depth positive control reproduces the 0.759 full-N ceiling (structure present at scale).
Smoke learned_depth=0.7549 already at the slice ceiling; full adds training data -> holds or improves.

## SMOKE RESULT (MEASURED@data/exp_agreement_learned_depth_accumulator_v1/metrics.json, run_mode=smoke)
learned_depth=0.7549(+-0.0000) vs shortcut_best=0.5682 (lift=+0.1867) vs deterministic_ceiling=0.7744;
local_bag=0.4513; fixed_random=0.5373 (control fails, cond_c ok); majority=0.6672;
scramble_drop=+0.2362 (change_frac=0.709); number_flip_change=0.0000; vocab=68 (slice);
learned delta of=+0.6912 that=+0.3152 comma=-0.2512 the=-0.0748 (openers POSITIVE, closer NEGATIVE:
the model discovered the depth structure). Smoke verdict = HARD_PASS_LEARNED_DEPTH_GENERALIZES.

## FULL dispatch
queue: remote_cpu_queue; timeout: 1800s (progress_logging present: per-VAL_EVERY val_buried prints +
_heartbeat.jsonl during training). anchor: exp_agreement_learned_depth_accumulator_v1.
If HARD_PASS at full multi-seed: FIRST learned structural-generalization result on real text that beats
the buried-subject wall -> HARDEST skunkworks-VET (learned depth vs disguised position; held-out pool
representativeness; SGD memorization check).
