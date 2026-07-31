# Pre-reg: continuous_curriculum_learn_as_you_go_v1

Filed 2026-07-31 (exp_dev). Cell: `experiments/exp_continuous_curriculum_learn_as_you_go_v1.py`.
USER directive (commit 950bef5d1): STOP artificial train-on-a-batch / test-on-a-FROZEN-fixed-probe
experiments. BUILD the continuous read-the-curriculum-and-learn-as-you-go loop -- read a GRADED stream, learn
from each chunk ONLINE, comprehension GROWS, test-as-you-go on held-ahead material, anti-forgetting is the key
risk. Measurement-first FIRST-CUT (scale = USER's call).

## The system (not another batch probe)
- GRADED STREAM: grades g=1..G of increasing SURFACE-FORM difficulty, via a graded modifier-pool size n_mods
  (each ENT mention rendered "the <MOD> <color> ..."; n_mods=1 => same modifier every frame => cross-frame
  surface CONSISTENT = easy; n_mods=8 => query modifier usually DIFFERS from statement modifier => cross-frame
  surface MISMATCH = hard; n_mods=8 reproduces hc's VET'd hard renders bit-for-bit). Grades both the online
  training texts AND the held-ahead eval passages identically; chance = 1/V_FILL FIXED (answers are fillers).
  LITE hardness = (1,3,8); SMOKE = (1,8).
- ONLINE / CONTINUAL: read grades sequentially; after each grade's chunk run STEPS_PER_GRADE online SGD steps on
  the encoder top-1 layer with the CERTIFIED 3-term objective (cross-mention consistency + inter-entity push +
  VICReg -- atom 29593, reused VERBATIM; only the DATA SCHEDULE differs from the batch cert). Weights + optimizer
  persist across grades (continual). Anti-forgetting = a rehearsal reservoir (replay) mixing earlier grades.
- READER / co-train (honesty): the reader is the PARAMETER-FREE FHRR situation-model loop (content-gated WM +
  competitive coref); there are NO learned reader params in the certified path (learned-reader bolt-ons
  HARD_FAILED 4x). "Co-train encoder AND reader" is realized as: the online objective shapes the encoder
  representation the fixed reader consumes. Stated for the USER as a scope/design decision.
- TEST-AS-YOU-GO / CLIMB CURVE: at each grade boundary t=0..G snapshot the encoder + score held-ahead
  comprehension = FHRR loop acc on FIXED NOVEL-entity passages at the HARDEST grade (n_mods=8). curve[t] vs t.

## Arms (per seed; learner identical across online arms; only the DATA SCHEDULE differs = one-variable-family)
- BASE (frozen, no update): frozen held-ahead loop (flat no-learning control), the FROZEN GRADED PROFILE (loop
  at each grade hardness -- must DECLINE = genuinely graded), the 6 can-fail floors, POOLED, MOST_RECENT, wc.
- GRADED: online, graded order (n_mods 1->..->8), WITH replay. THE SYSTEM.
- SHUFFLED: online, shuffled grade order (same content, not simple->complex), WITH replay. (curriculum-order value)
- NOREPLAY: online, graded order, NO replay. (anti-forgetting ablation / forgetting check)

## Pre-registered bands (fixed BEFORE running)
climb = curve_target(t=G) - curve_target(t=0) [== beat-frozen, since curve[0] is the untrained encoder].
- HARD_PASS (learn-as-you-go works): climb >= CLIMB_MIN (0.05) AND min-seed climb > 0 AND monotone within
  TIE_BAND (0.02) AND forgetting_graded (easy@t1 - easy@tG) <= FORGET_MAX (0.10) AND collapse-guard HOLDS at
  t=G AND (validity) FROZEN GRADED PROFILE declines >= PROFILE_DECLINE_MIN (0.03) AND floors collapse AND
  POOLED < PROVEN_MIN.
- HARD_FAIL (broken loop, NOT a capability): guard C1 cratered at t=G (online update destroys the reader) OR
  base reading fails at t=G (oracle < chance + BASE_READING_MARGIN=0.20).
- FLAT / MIDDLE (climb <= TIE_BAND): DO NOT conclude a ceiling (USER flat=fix). DIAGNOSE (a) NOT-LEARNING
  (weights barely moved OR online loss did not descend OR objective did not fit train entities), (b)
  NO-NEW-CONTENT (frozen graded profile FLAT -> higher grades not actually harder), (c) UNDERPOWERED (MDE >
  CLIMB_MIN). Learning + graded + powered + still flat => CLEAN_DESIGN_LIMIT (design fix -- more unfreeze /
  harder negatives / more steps / a second difficulty axis -- NOT a ceiling).
- INVALID: a floor did not collapse OR POOLED reservoir-decodable OR FROZEN GRADED PROFILE does not decline
  (stream not genuinely graded -> fix grading first) OR held not disjoint from train.

## Compute architecture
Mixed: top-1-layer ONLINE SGD (batched fwd+bwd, CPU) + closed-form FHRR eval loop with batched frozen-encoder
forwards at each checkpoint. Storage strategy: no_storage. crlb_n/a (climb-slope discriminator; bands on the
curve). progress_logging: print_flush_true. Resumable per-unit (units.jsonl). cardinality_ok:
EXPECTED_N_UNITS = n_seeds * (1 base + 3 online arms). deterministic seeding (numpy default_rng + torch
manual_seed; no hash()/list(set())). CPU-first, push-free, INLINE-LOCAL foreground, --budget-sec < 10 min.

## Scope / honesty
Surface-hardness difficulty axis on the certified 20-color harness. Competing-entity count (K_TRACK), context
length, and real-noun BREADTH are ORTHOGONAL difficulty axes, DEFERRED (USER-strategic). This isolates the
CURRICULUM / CONTINUAL variable from vocab-breadth (which the diversity probe e90f7fbb7 showed saturates).
FIRST-CUT: single-seed LITE for throughput; 2-seed replication is the labeled escalation step.
