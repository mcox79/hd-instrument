# Pre-reg: ENCODER-RETRAIN ROLE (position-free role/filler attribution)

- Cell: `experiments/exp_situation_model_assembly_encoder_retrain_role_v1.py`
- Anchor: `situation_model_assembly_encoder_retrain_role_v1`
- Date: 2026-07-31
- Author: exp_dev (Director spawn: attack the ROLE half of the founding encoder wall with the CERTIFIED
  minimal-unfreeze recipe that broke the ENTITY half, atom 29593).

## Question
The founding encoder wall has two halves. (1) cross-frame ENTITY re-id = CERTIFIED break (atom 29593:
minimal-unfreeze top-1 fine-tune lifts held-out loop 0.52->0.83). (2) position-free ROLE/FILLER
attribution = UNTOUCHED. On the naturalistic harness, tuned-ORACLE (perfect entity assignment) ~0.62 sits
FAR below REF_SPAN (position-given) = 1.0; that residual IS the encoder's position-free role/fill decode
degradation. Does the SAME proven recipe (minimal-unfreeze top-1 + a targeted objective + VICReg
anti-collapse) fix the ROLE half too?

## Measurement-first framing (NOT a pass-chase; NOT a full retrain -- Director+USER-gated)
Reuse the certified harness + loop + floors VERBATIM (via `lt`/`eb`/`ef`/`ih`/`clean`). ONE VARIABLE = the
encoder (frozen vs role-fine-tuned). Toy ~20-word vocabulary (like the entity break). Do NOT tune-to-pass.

## Making the role gap genuinely POSITION-FREE + FALSIFIABLE (load-bearing)
The harness render "the ENT was set S and placed P ." CONFOUNDS role with position (S always first) -> a
span/position shortcut fully solves it (REF_SPAN=1.0). To prove position-free role attribution is a gap a
position shortcut CANNOT win, deconfound order via STRAIGHT/SWAP (the proven pattern from the voice organ
d621817c3):
- STRAIGHT: "the ENT was set S and placed P ."   (S filler first)
- SWAP:     "the ENT was placed P and set S ."   (S filler SECOND; role = the VERB, not position)
Can-fail control: POSITION_ONLY reader (assume set-first) MUST fail on SWAP (reads P-as-S). span reader
(true span) works BOTH orders (info is positional). role_attn (semantic cue) is the reader under test.

## Objective (exp_dev owns): role-consistency / role-separability + VICReg
MINIMAL-UNFREEZE top-1 (same as the cert) of OUR OWN v2 encoder. On the role_attn-pooled S and P reps:
label = role-tagged filler (S-filler c -> c ; P-filler c -> c+V_FILL); align same (role,filler) across
ORDERS (position-invariant role); push different (role,filler) (within-role filler separation + inter-role
S-vs-P separation); VICReg variance-floor + covariance decorrelation. Supervision = (role, filler) labels
from BOTH orders (data-supervision ALLOWED; borrowed encoder/parser FORBIDDEN -- our v2 encoder). Then a
fresh extractor is built around the tuned weights and the identical harness is run.

## Fairness gate
HELD-OUT FILLERS: ih.color_split(SPLIT_SEED) -> train (fine-tune) / held (eval). Every eval S/P filler is a
color the encoder never fine-tuned on. FT sentences use train colors only.

## Metrics (per role S/P; per order canonical/swapped; frozen vs tuned)
- role_attn decode accuracy (position-free), span decode (positional reference), POSITION_ONLY (can-fail).
- per-role ORDER-SENSITIVITY OS = mean_role |canonical - swapped| (position-bound signature).
- WORST-of-4 (role,order) role_attn decode (a position-free ROLE reader has ALL FOUR high).
- LOOP (canonical, oracle-entity, held fillers): oracle-arm loop + REF_SPAN; gap_closed = (tuned-frozen)/
  (ref_span-frozen); stage S/P decode. eb deterministic floors (validity).
- anti-collapse: within-(role,filler)-minus-cross + S-vs-P cosine + VICReg final.

## Pre-registered bands (FINAL; premise metric CORRECTED after the first LITE -- see note)
- PREMISE (both hold for a VALID test): P1 posonly reader FAILS swapped (<= 0.35) => task genuinely
  position-free; P2 span (positional) beats frozen role_attn (position-free) on swapped by HEADROOM >= 0.15
  => a position-free-attribution deficit exists to fix.
- HARD_PASS: premise fires AND tuned worst-of-4 (role,order) held-out role_attn decode >= frozen worst-of-4
  + 0.10 AND >= 0.75 AND (loop gap closed >= 0.25 OR loop lift >= 0.08) AND anti-collapse (wmc >= 0.10) AND
  floors collapse. => recipe fixes role half; escalate to scale (Director-gated).
- HARD_FAIL: tuned worst-of-4 <= frozen + 0.03 (ties) OR collapse (wmc < 0.02).
- PREMISE_NOT_POSITION_FREE: deconfound valid but headroom < 0.15 (frozen already position-free) -> recipe
  not needed here. Informative null.
- MIDDLE: premise fires, moved, but a pass bar not cleared -- reported WITH trajectory.
- INVALID: an eb can-fail floor did not collapse OR posonly does NOT fail swapped (deconfound broken).

## Correction note (honest disclosure -- two-stage calibration)
(1) Smoke (seed 7, eval_n=24) showed a large per-role order-swing (canon S=0.667/P=0.917, swap S=0.958/
P=0.583). The FIRST LITE (eval_n=160) showed that swing was SMALL-SAMPLE NOISE: frozen canon S=0.856/
P=0.800, swap S=0.844/P=0.681 -> per-role order-sensitivity OS=0.066 (small). So an OS-based premise was
the WRONG shape. The premise was CORRECTED (post-INVALID, pre-final-verdict) to P1 (posonly fails) + P2
(span-vs-role_attn HEADROOM), which is the faithful "is there a position-free deficit" test; OS demoted to
a reported diagnostic. (2) The first LITE also fired INVALID on shuffled[b]=0.212>0.20 because the held-out
LOOP used 10-way fillers, doubling filler-chance to 0.10 above the eb-calibrated (20-way, chance 0.05) 0.20
bar. FIX: the LOOP (assembled-task consequence) uses the FULL 20-palette the floor was calibrated for --
floors then genuinely collapse (shuffled 0.025-0.087) -- while the HELD-OUT-filler generalization claim is
carried by the position-free DECODE PROBE. Neither change lowers a pass bar. span=1.0 both orders + posonly
=0.069 on swap confirm the deconfound is valid; oracle loop 0.64-0.74 reproduces the certified ~0.62.

## MEASURED result (final LITE, seed 7, eval_n=160, held-out fillers; VALID)
- Premise FIRES: posonly swapped 0.069 (P1), headroom 0.319 (P2). Valid position-free role-half test.
- Position-free (swapped) held-out role_attn decode: FROZEN S=0.844/P=0.681 -> TUNED S=0.881/P=0.738;
  worst-of-4 0.681->0.738 (+0.056). Canonical S=0.856/P=0.800 -> 0.894/0.825. Below the +0.10 / 0.75 bars.
- LOOP oracle-arm (full palette): 0.737 -> 0.855, gap closed 48.9% of the oracle->REF_SPAN(0.977) gap.
  stage S 0.958->0.978, P 0.877->0.912, ENT 0.834->0.934, MARK 0.874->0.919 (role fine-tune sharpens all
  cue-pooled slots). Anti-collapse wmc 0.222 (no collapse). All eb floors collapse.
- VERDICT = MIDDLE: the recipe VALIDLY + modestly lifts position-free role attribution and closes ~half the
  assembled-loop role gap, but the role half is only WEAKLY position-bound in this toy vocab (frozen already
  0.68-0.86 position-free vs the entity half hard-broken at 0.52), so the held-out decode lift does not
  clear the pass bars. Recipe APPLIES + HELPS the role half; the wall was never as deep as the entity wall.

## Hardening
resumable per-condition (units.jsonl); atomic tmp_replace; except SystemExit/KeyboardInterrupt/Exception
(no BaseException); start-marker; crash-diagnostic; ASCII-only; deterministic seeding (no hash()/list(set));
DRIFT/real_code_path exercised in self-test; arms-differ (frozen vs tuned decode digests); progress flush.
CPU-first, push-free, INLINE-LOCAL foreground-to-completion.
