# Pre-registration: exp_propara_decisive_inference_arm1_decompose_v2

**Filed by:** exp_dev, 2026-08-10. **Task source:** coordinator follow-up to
`exp_propara_decisive_inference_arm1_oracle_v1` (landed HARD_FAIL, commit 6a749aba9): the
+0.306 official-metric win over baselines was largely ORDER-INVARIANT under scramble
(reasoning official F1 0.737 -> scramble 0.706-0.727 = barely drops), so most of it is
structural-prior, NOT content-based temporal composition. This cell DECOMPOSES the win.

## Prior-work check (SUBSTRATE-KB)
Same arc as v1 (`substrate_query.sh "ProPara participant state tracking cross-step inference
situation model"` top hit cosine 0.3096 FrameNet, no prior arc cell > 0.30). This v2 is a
direct decomposition follow-up on v1's own landed result; novelty inherited.

## The four questions (coordinator follow-up)
1. **PRIORS-ONLY ablation arm:** monotonicity (CREATE-idx < DESTROY-idx window) + the oracle
   event-COUNT grant, ZERO content/BoW retrieve signal. Content-blind placement: CREATE at the
   earliest feasible step, DESTROY at the latest feasible step, MOVEs spread deterministically
   across the remaining middle steps (`_assign_events_priors_only`). Scramble-invariant by
   construction (no text read). Measured on official F1 + focus macro-F1.
2. **Genuine-content delta = reasoning - priors_only.** Is there a real, positive, SCRAMBLE-CLEAN
   increment the content/order signal adds ON TOP of the priors? Its own scramble control:
   `content_delta_scramble[seed] = reasoning_scramble[seed] - priors_only` (priors_only is
   scramble-invariant), `content_delta_retained_frac[seed] = content_delta_scramble /
   content_delta_natural`. Collapse (-> ~0) across seeds = genuine order-sensitive content.
3. **Oracle-grant audit:** `_audit_oracle_grant` asserts on disk that the oracle hands ONLY the
   per-(paragraph,participant) event-COUNT multiset (order-free CREATE/MOVE/DESTROY totals) +
   the participant list = events + entities, and NEVER a per-step state / location / step index.
   **Confirmed: it is already events+entities-only; there is NO per-step-state leak** (the
   reasoning MUST infer localization). No harder events-only arm is needed -- the v1/v2 arm is
   already the events-only comprehension task with the state grid withheld.
4. **10 scramble seeds** (7,17,29,41,53,71,83,97,101,113) on TEST -- n=3 in v1 was too thin.
   Report the full distribution of `content_delta_retained_frac`.

## New arm (vs v1)
`PRIORS_ONLY` -- identical oracle event-multiset grant to the reasoning arm, identical
monotonicity VALIDATE window, but the within-window RETRIEVE reads no text. Wired through the
SAME per-paragraph `AccumulateRegister` decode path as reasoning (equal FHRR-decode footing).
Baselines (majority / bow_singlestep / bagstates) and the natural + scramble reasoning arms are
reused verbatim from v1 (imported, not re-transcribed).

## Metrics (both axes, every arm)
OFFICIAL ProPara metric (`propara_official_eval.corpus_evaluation`, the bit-exact port validated
in v1 against the official repo's own fixtures: testfiles-1/2/3 F1 = 0.545/1.000/0.686) on the
full participant set; AND the trap-check unmentioned-subset 4-way macro-F1 proxy (FOCUS metric).
Headline decomposition quantities: `priors_captures_frac` (official + focus) = (priors -
best_baseline) / (reasoning - best_baseline); `content_delta` (official + focus) = reasoning -
priors; `content_delta_retained_frac` distribution over the scramble seeds.

## Decomposition-outcome classification (diagnostic thresholds; stated here, NOT tuned)
- `CONTENT_DELTA_MIN_POSITIVE = 0.02`: content_delta (focus macro-F1) must exceed this to count
  as a real increment (below = the content signal adds essentially nothing over priors).
- `CONTENT_DELTA_SCRAMBLE_COLLAPSE_FRAC = 0.50`: a seed's `content_delta_retained_frac` <= 0.50
  counts as "collapsed" (the content increment lost >= half its value under that permutation).
- `CONTENT_DELTA_COLLAPSE_SEED_MAJORITY = 0.70`: >= 70% of the scramble seeds must collapse for
  the content-delta to be called "scramble-clean" (consistent order-sensitivity, not a lucky
  permutation).
- **GENUINE_CONTENT_SIGNAL (HARD_PASS)** iff content_delta >= 0.02 AND scramble-clean across the
  seed majority -> the real signal to push into ARM 2.
- **PRIOR_CONFOUNDED (HARD_FAIL)** iff content_delta < 0.02 OR not scramble-clean -> the oracle
  arm's win is prior-driven; honest read = structural comprehension over gold structure does NOT
  yet produce a content-driven win here (a real, publishable negative).
- Infra gates (HARD_FAIL_INFRA if any fail, regardless of science): arms_differ (priors_only vs
  reasoning MUST differ), oracle_grant_audit (no state leak), decode_fidelity >= 0.99 both arms.

## HP_SCOPE
`{content_delta: [content_delta_positive, content_delta_scramble_clean_across_seeds]}`. The
baselines and priors_only arm are decomposition references, not claims under a HARD_PASS gate.

## Cell-template mandates
- arms_differ (META_RULE_AF): majority/bow_singlestep/bagstates/priors_only/reasoning grids
  hash-differ; asserted in self-test AND recorded in the full run.
- final_metrics_atomicity: tmp_replace (single-shot; the scramble seeds are a fast inner loop
  over ONE fitted model, no per-seed crash-resume needed -- whole run is ~seconds).
- except SystemExit: raise before except Exception (grep-verified; the only `except:` textual
  hit is in a comment, not code).
- crlb_n/a (F1-comparison decomposition; no noise-floor threshold).
- calibration_check: default_ok_for_this_regime (diagnostic thresholds stated above, not tuned).
- deterministic_seeding: true (AccumulateRegister torch.Generator + scramble permutation seeded
  via hashlib.sha256 digests, never Python hash() / list(set())).
- progress_logging: print_flush_true.

## Compute architecture
Sequential-CPU, justified (same as v1): light TF-IDF+LogisticRegression fit + discrete greedy
assignment + FHRR decode at d=512 over <=16-event registers; no batching opportunity. MEASURED
smoke wall time 2.19s (dev, 2 seeds); TEST + 10 seeds expected ~10-20s. Run INLINE/LOCALLY to
completion (foreground), not queued.

## Smoke findings (DEV, 2 scramble seeds)
**MEASURED@data/exp_propara_decisive_inference_arm1_decompose_v2_smoke/metrics.json (dev, 43
paragraphs, elapsed 2.19s):**
- OFFICIAL metric: best_baseline 0.553, **priors_only 0.721**, reasoning 0.771 ->
  **priors_captures_frac_official = 0.771** (priors-only alone captures 77% of the official win;
  content_delta_official = only +0.050).
- FOCUS (unmentioned macro-F1): best_baseline 0.242, priors_only 0.299, reasoning 0.417 ->
  **priors_captures_frac_focus = 0.325** (priors capture only ~32% of the focus-subset win;
  content_delta_focus = +0.118 -- the content signal is CONCENTRATED in the unmentioned subset,
  as expected: that is exactly where lexical/text signal must do the localization work).
- Scramble (content-delta collapse): 1/2 seeds collapsed, median retained_frac 0.408 -- n=2 is
  too thin to conclude; the 10-seed TEST run is the decisive measurement.
- Oracle-grant audit: events+entities-only, no state leak (confirmed). arms_differ True.
  decode_fidelity 1.0 both arms.

DEV verdict: HARD_FAIL_PRIOR_CONFOUNDED under the (deliberately strict) 70%-seed-collapse bar at
n=2. This is a DIAGNOSTIC classification, not a capability failure -- the decisive question (is
the +0.118 focus content-delta scramble-clean across MANY seeds?) is answered by --full on TEST.
Thresholds pinned here BEFORE --full touches TEST.

## Full findings (TEST, 10 scramble seeds) -- DECISIVE
**MEASURED@data/exp_propara_decisive_inference_arm1_decompose_v2/metrics.json (test split, 54
paragraphs, 10 scramble seeds, elapsed 5.77s). Verdict: HARD_FAIL_PRIOR_CONFOUNDED.**

**(1) Priors-only captures almost the ENTIRE official win.** OFFICIAL overall F1: best_baseline
0.431, **priors_only 0.716**, reasoning 0.737 -> **priors_captures_frac_official = 0.931**
(monotonicity + oracle event-count alone, ZERO text, reproduces 93% of the reasoning arm's
official win). content_delta_official = only **+0.021**.

**(2) The oracle event-COUNT grant TRIVIALLY answers the existence categories.** Per-category
official F1 (the smoking gun): priors_only scores **inputs=1.000, outputs=1.000** -- PERFECT on
the two existence-only ProPara categories, with zero reasoning, because Inputs (destroyed-and-
never-recreated) and Outputs (created-and-never-destroyed) are fully determined by the order-
free event-COUNT multiset the oracle hands over. Those categories dominate the overall F1, so the
"official win" is even more prior-confounded than the overall number suggested. Reasoning adds a
genuine increment ONLY in the localization-dependent categories: conversions 0.312->0.340, moves
0.327->0.439. That is the real (small) content contribution -- and it is exactly where the next
question bites.

**(3) The genuine-content delta is real-but-small and NOT scramble-clean.** FOCUS (unmentioned
macro-F1): priors_only 0.299, reasoning 0.382 -> content_delta_focus = **+0.083** (> 0.02, so a
real increment; and priors capture only 39% of the focus win, consistent with the content signal
living in the unmentioned subset). BUT the content-delta does NOT collapse consistently under
scramble: `content_delta_retained_frac` across the 10 seeds = **[0.018, 1.092, 0.832, 0.042,
-0.061, 0.427, 0.581, 0.622, 0.539, 0.595]**, median **0.560**, mean 0.469, only **4/10 seeds
collapsed** (<= 0.50) -- far below the 70% majority bar. Critically, v1's seed7 (retained 0.018)
was a LUCKY LOW permutation; the bulk of seeds cluster at 0.5-0.6 retained, and seed17 actually
INVERTS (retained 1.092 -- scramble slightly beats natural). So v1's "clean collapse at seed7"
was permutation luck, not consistent order-sensitivity.

**(4) Oracle-grant audit:** confirmed events+entities-only, no per-step-state leak (the arm is
already the events-only task with the state grid withheld -- no harder arm needed).

**HONEST READ (the publishable negative):** the ProPara oracle arm is PRIOR-CONFOUNDED. The
large official-metric win is almost entirely (93%) the monotonicity prior + the oracle event-
count grant (which by itself perfectly answers the existence categories), NOT content-driven
temporal composition. The genuine content increment that survives on top of the priors is small
(+0.021 official / +0.083 focus, concentrated in Moves) and, decisively, does NOT collapse
scramble-clean across seeds (median retained 0.56, only 40% collapse). **Structural comprehension
over gold structure does NOT yet produce a content-driven, scramble-clean win on real prose.**
This does NOT invalidate the reasoning organs -- it says the ProPara oracle-structure grant is
too generous a confound to be the ARM-1 vehicle for a comprehension claim: the oracle event
counts hand over most of the answer before any reasoning runs. A cleaner ARM-1 vehicle would
withhold the event-COUNT multiset too (give only entities + text, infer BOTH counts and
localization) -- but that is then ARM-2-like (extraction re-enters). Recommendation to the
coordinator: do NOT push this content-delta into ARM 2 as a "genuine signal"; treat this as a
decisive negative on the oracle-structure ARM-1 framing and re-scope what "oracle structure"
should withhold.
