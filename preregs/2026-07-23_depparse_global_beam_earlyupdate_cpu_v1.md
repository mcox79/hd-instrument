# Pre-registration: exp_depparse_global_beam_earlyupdate_cpu_v1

Filed by: exp_dev (cell author). 2026-07-23. Design source:
`notes/parser_global_beam_training_break_local_saturation_2026-07-23.md`.
Prior-work check (substrate_query "global beam training structured perceptron early-update transition
parser dependency"): top hit cosine=0.3037 = a CRF BIO-transition-feature ablation note (NER tagger,
different task/decomposition); no prior arc-eager GLOBAL-beam-training cell at cosine>0.30. GENUINELY
NOVEL on this substrate (29451 has beam DECODE but only LOCAL training; this adds GLOBAL training).

## Question (ONE variable = training regime; features held BIT-IDENTICAL)
Does GLOBAL structured-perceptron training (beam + EARLY-UPDATE; Collins-Roark 2004, Zhang-Clark 2008)
break the LOCAL-argmax saturation of the glass-box arc-eager transition parser (atom 29451, dev UAS
0.8109), so that beam decode HELPS instead of HURTS? The single variable is the TRAINING REGIME; the
feature function is 29451's exact `_config_feats` (copied verbatim) across every arm, and the dev eval
split is identical. If global-beam training with the SAME features does not beat local greedy by a
clean +0.03, that is an EARNED BOUND (saturation deeper than decode; lever is richer features).

## Arms (identical features + identical dev split; ONE variable = training regime)
- ARM_LOCAL       -- 29451 baseline: dynamic-oracle LOCAL greedy training, greedy decode. In-run
                     positive control (Gate D: reproduce 0.8109 at MAXLEN=50). Expect ~0.81.
- ARM_LOCAL_BEAM  -- CONTROL: SAME local-trained weights, BEAM decode (width B). Must REPRODUCE the
                     beam-hurts anomaly (29451 beam_uas 0.7528 << 0.8109). Isolates: decode alone does
                     not help; if the GLOBAL arm (same beam width) wins, the lever is TRAINING.
- ARM_GLOBAL_BEAM -- MECHANISM: GLOBAL beam + early-update training, BEAM decode (same width B).
                     HYPOTHESIS: beam now HELPS -> UAS toward 0.85-0.88.

## Compute architecture
Class (b) sequential-CPU with justification: the transition parser + beam search have genuine
sequential dependencies (config/beam state at step N depends on step N-1; early-update stops at the
first gold-off-beam step) -- this IS the mechanism under validation, not a batchable phase sweep.
Averaged perceptron over crc32-hashed features (numpy fromiter); NO gradient/autograd. Glass-box: each
beam item is an explicit `_Hyp(stack, bptr, heads, score)` with a feature-id backpointer. no_storage;
no bind/unbind chains; persists NO substrate atoms/frontend asset. MEASURED scale probe: global train
= 1.66 ms/sent/epoch at beam 8 -> full 12329 sents x 6 epochs ~= 123 s/seed. FULL wall estimate ~14 min
(3 seeds: local dynamic-10ep + global-beam-6ep + beam/greedy dev evals + global learning-curve).

## Baselines (real, same-split, in-band)
- ARM_LOCAL greedy = 29451 dynamic UAS 0.8109. MEASURED@data/exp_depparse_transition_arceager_cpu_v1/metrics.json:dynamic_uas_mean
- 29451 beam-decode-on-local = 0.7528 (beam-hurts). MEASURED@same:beam_uas
- classical arc-eager lit UD-EWT dev 0.86-0.89. CITED@notes/parser_global_beam_training_break_local_saturation_2026-07-23.md
- baseline_in_band: local UAS ~0.81 in (0.05, 0.95). SMOKE-verified local=0.72 (300 train, 3 ep).

## Pre-registered bands (PASS + FAIL documented BEFORE full)
- HARD_PASS = global_uas_mean_minus_2se >= local_uas_mean + 0.03 (clean +0.03, approaching lit)
              AND beam_hurts_reproduced (local_uas - local_beam_uas >= 0.01; isolates TRAINING)
              AND learning-curve RISES (global UAS frac 1.0 - frac 0.1 >= 0.02).
- HARD_FAIL (must be possible) = global_uas_mean <= local_uas_mean -> EARNED BOUND: search does not
              help this feature set; saturation is deeper than decode.
- MIDDLE_BAND = global beats local by a positive margin but < clean +0.03 (2SE), OR isolation not clean
              (beam did not hurt local), OR learning curve did not rise.
- UNKNOWN = corpus load fails OR global arm produced no parses.
- crlb_n/a: discrete argmax parse accuracy; no CRLB noise floor.

## Discriminator-must-survive-scale (option B analytical justification)
At smoke (300 train, 3 ep, beam 6) global (0.684) sits just below local greedy (0.720): global-beam's
advantage over local greedy is expected to GROW with training data + epochs (globally-trained scorers
exploit search; local greedy converges faster on tiny data). Both arms are far from ceiling and clearly
separable (NOT saturated: neither arm >= 0.95), so the discriminator is live. The FULL-scale question
(does global training close and overtake the gap by +0.03) is genuinely open in BOTH directions -- a
valid full dispatch. Smoke's role (satisfied): cell runs, global training BOOTSTRAPS (updates fire:
244/477/701 across 3 epochs; not the degenerate zero-update tie-collapse), arms differ, control
reproduces beam-hurts direction.

## FAIR / leak / determinism
- FAIR: identical `_config_feats` features + identical dev eval split across arms; ONE variable =
  training regime; report uas_all + uas_nopunct + hard-attachment (distance-bucket 1/2/3-6/7+)
  breakdown per arm; buried-subject-id secondary readout; real UD-EWT (2001 dev sents, MAXLEN 50).
- No gold-structure leak: features read only form/POS (sent[k][1], sent[k][2]); oracle/gold used only
  for TRAINING targets, never as decode-time features.
- Deterministic seeding: fixed int seeds (1,2,3; LC 999), numpy default_rng, crc32 hash; NO hash()-
  seeded RNG, NO list(set()) ordering.

## Smoke (PASS, local, 2026-07-23)
MEASURED@data/exp_depparse_global_beam_earlyupdate_cpu_v1_smoke/metrics.json:
verdict HARD_FAIL (expected at smoke scale); local_greedy=0.7200, local+beam=0.6873 (beam-hurts
reproduced, delta +0.0327), global_beam=0.6840 (bootstraps: updates 701); arms_differ_verified=True
(weights + heads); cardinality_ok=True; final_metrics_atomicity=tmp_replace; elapsed 5.3s; size 6312B.
Self-test PASS: gold-derivation reachable+replays to gold tree; early-update fires under adversarial
weights; no spurious update when gold is top; loader parity (2001 sents).

## Cell-template compliance
except SystemExit: raise BEFORE except Exception (no BaseException); atomic tmp_replace metrics;
start-marker + crash-diagnostic + heartbeat; arms_differ (weights + heads); MEASURED/CITED tags;
progress_logging print_flush_true (per-epoch flush); crlb_n/a declared. NO LLM, NO torch, NO nltk;
numpy + pure-python only; ASCII-only.

## Dispatch
Target queue: remote_cpu_queue (FULL; local = smoke-only per USER lock). timeout 3600 s (est ~14 min
+ headroom for slower remote CPU / pure-Python variance). NO origin push by exp_dev; orchestrator ships.
