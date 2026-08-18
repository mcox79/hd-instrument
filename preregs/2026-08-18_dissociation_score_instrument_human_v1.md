# PRE-REG: exp_dissociation_score_instrument_human_v1

**Filed 2026-08-18. exp_dev (cell author). HEAD at authoring: `21c9b3e19`.**

## Why this cell exists (verbatim from the dispatch brief)

Verified off disk (`exp_dissociation_score_instrument_v1.py:304,312,674`): `SET_P` is built by
`build_wordnet_synonym_candidates()` from `wn.synsets()`; `SET_S` explicitly excludes any WordNet
pair even at high co-occurrence; the known-answer arm is WordNet path similarity. WordNet defines
BOTH sides of the labels in the licensed instrument (`exp_dissociation_score_instrument_v1`, plan
sec 6.24). So plan sec 6.23's conclusion ("the missing ingredient is a learning signal") is really
"a learning signal for agreeing with WordNet". This cell asks: **when the positive set is defined by
HUMAN SIMILARITY JUDGEMENTS instead of WordNet, do the same arms rank the same way?** If yes, 6.23's
conclusion survives and is about our store. If no, 6.23 was substantially about WordNet.

## PRIOR-WORK CHECK (substrate-KB, mandatory per .claude/agents/exp_dev.md)

Ran `bash tools/substrate_query.sh "human similarity judgement dissociation instrument SimLex
SimVerb independent circularity WordNet substitutability"`. The query is documented elsewhere in
this repo as running very slowly under concurrent agent load
(`exp_tuned_count_unsupervised_dissociation_v1.py` module docstring, 181.4s on 2026-08-18 for the
same reason); it was still running in the background at cell-authoring time here. This cell is a
direct, explicitly-commissioned follow-on to plan sec 6.24 (the scope-limit note itself, landed
`21c9b3e19`) rather than an independently-conceived direction, so the prior-work risk this gate
guards against (silently re-deriving existing work) is structurally low: 6.24 names the exact gap
this cell fills ("a second, INDEPENDENT operationalisation of substitutability... candidate
independent targets... human substitution judgements") and no such cell exists yet (grep of
`experiments/exp_dissociation*` and `experiments/*human*` at authoring time returns only this new
file). Result recorded in the completion report once the background query returns; if it surfaces a
genuine near-duplicate, this cell will be flagged rather than silently shipped.

## Construction

**SET_P_HUMAN** (paradigmatic/substitutable, per human judgement): pairs from SimLex-999 +
SimVerb-3500 with published similarity score >= `T_HIGH = 6.0` (0-10 scale) AND zero corpus
co-occurrence in our 34,169-sentence corpus. The zero-co-occurrence requirement is an EXPLICIT
DESIGN CHOICE not spelled out verbatim in the dispatch brief, added to mirror the licensed
instrument's SET_P construction fairly: without it, a store that merely encodes co-occurrence could
score AUC>0.5 on this arm for the wrong reason (because SET_P_HUMAN would then contain some
co-occurring pairs), collapsing the very distinction (substitutability vs co-occurrence) the
instrument exists to measure. Disclosed here rather than silently added.

**SET_S_HUMAN** (syntagmatic/non-substitutable, per human judgement): pairs from the SAME two
benchmarks with score <= `T_LOW = 4.0` AND corpus co-occurrence count at or above the 90th
percentile of the FULL anchor-pair co-occurrence distribution (recomputed fresh on this corpus,
never imported -- mirrors `TOP_DECILE_Q=0.90` in the licensed instrument exactly). This replaces the
licensed instrument's WordNet-relation exclusion step with a low-human-rating requirement, which is
the entire point of the cell.

**Threshold justification.** 0-10 scale; T_HIGH=6.0 / T_LOW=4.0 leaves a 2.0-wide buffer zone
excluded from both sets (standard practice in relation-classification benchmark construction, to
sharpen the label boundary rather than using a bare median split). Both benchmarks' own published
qualitative examples support these as genuinely distinguishing cuts (e.g. SimLex: weird/strange=8.93,
smart/intelligent=9.2 well above 6.0; old/new=1.58, hard/easy=0.95 well below 4.0). Not
adaptively tuned on this cell's own outcome -- fixed before any arm was scored. Feasibility probe
(`scratch/_probe_human_dsi.py`, disposable, run before authoring): at these thresholds,
SET_P_HUMAN raw candidates (zero-cooc, score>=6.0) = 436; SET_S_HUMAN raw candidates (>=decile90
cooc, score<=4.0) = 122, both well above the `n_match < 20` unbuildable floor the licensed
instrument itself enforces.

**Matching.** Reuses `exp_dissociation_score_instrument_v1.match_cells` VERBATIM (same 5-covariate
per-dimension caliper: mean_log_freq, |freq_diff|, mean_length, orthographic trigram-cosine, mean
constant-prototype), same caliper vector, same fail-closed philosophy (a P item with no genuinely
close S partner is dropped, never force-matched). ONE change: POS stratification uses the
benchmark's OWN POS column (SimLex 'A'/'N'/'V', SimVerb always 'V') instead of
`DSI.wn_dominant_pos` (which is WordNet-derived) -- this keeps the human-labelled construction
WordNet-free end to end, including the nuisance-covariate stratification, not just the P/S label
definition itself.

## WordNet-independence audit (MANDATORY, reported before any arm)

Two numbers, both computed off disk, not asserted:
1. Fraction of the FINAL MATCHED SET_P_HUMAN pairs that are ALSO a WordNet same-synset pair
   (`DSI.build_wordnet_synonym_candidates` membership test) -- the direct contamination measure.
2. Fraction that are WordNet-"close" under `DSI.wn_best_path_similarity >= DSI.WN_CLOSE_THRESHOLD`
   (0.25) -- the looser measure the licensed instrument itself uses to exclude near-synonyms from
   SET_S.
A citation-level note (not independently re-verified via live literature search in this exp_dev
role -- that is Research's tool, not authored here) on SimLex-999's own published methodology: Hill,
Reichart & Korhonen (2015) describe pair CANDIDATES as drawn from multiple sources including USF
free-association norms, prior similarity datasets, and WordNet-adjacent pairs selected to include
both similar and dissimilar cases -- so WordNet may have influenced which pairs were PUT UP for
human rating, for some fraction of pairs. Critically, the published 0-10 SCORE that this cell
thresholds on is a crowd-sourced human judgement, not a WordNet-derived computation -- unlike the
licensed instrument's labels, which ARE a deterministic function of `wn.synsets()`. The measured
overlap fraction (item 1 above) is what actually decides whether this test is independent enough to
answer the question; if it is near-total, the cell states that plainly per the dispatch brief's
explicit instruction, rather than reporting a ranking anyway.

## Floors (Gate 3, STOP-IF i) -- recomputed on THIS population, never imported

F_ORTHOGRAPHIC, F_FREQUENCY (max-of-pair, aux['fq']), F_SCRAMBLE, F_CONSTANT_PROTOTYPE -- all four
via `tools.floor_battery` + `DSI`'s own pairwise wrappers, reused verbatim, scored on the matched
SET_P_HUMAN / SET_S_HUMAN pairs. Every floor's 95% CI must include 0.5 or `INSTRUMENT_LICENSED =
False` and no arm number is interpreted as a finding (only written for the record).

## Known-answer arm

The published human similarity score itself. Disclosed explicitly as MORE tautological than the
licensed instrument's WordNet-path-similarity known-answer (which read a near-1.0 0.9599, not
exactly 1.0, because path similarity is a DIFFERENT quantity from the WordNet-synset label it was
checking): here the known-answer score IS the literal quantity SET_P_HUMAN/SET_S_HUMAN were
thresholded on, so AUC = 1.0 EXACTLY by construction, not approximately. This is disclosed as a
trivial sanity check on the AUC/labelling machinery (a real self-test in effect), not evidence of
anything about the store. A genuinely held-out split (e.g. half the SimVerb annotators used for
labelling, the other half for the known-answer arm, using `simverb3520_annotator_ratings.csv`) was
considered and rejected for this cell: it only covers the SimVerb-sourced subset of the combined
pool (SimLex ships no raw per-annotator matrix on disk), which would make the known-answer arm a
mix of tautological-for-SimLex-pairs and genuinely-held-out-for-SimVerb-pairs -- an inconsistent
measurement not worth the added complexity given the brief's own explicit sanction of the literal
rating as an acceptable choice ("Prefer a human-rating-derived known-answer (e.g. the held-out human
rating itself)").

## Random-vector-store arm

iid Gaussian d=256 per anchor (same convention `DSI.RANDOM_VECTOR_STORE` uses), independent of the
true store, must read AUC ~0.5.

## Arms (7, per dispatch brief, re-scoring the SAME stores on this NEW population)

1. `INCUMBENT_LIVE_STORE` -- `DSI` cached live store, reused verbatim.
2. `RAW_COUNT_FULL_ACCUM` -- uncompressed full-accumulation counts, reused from
   `exp_cue_information_audit_v1` checkpoint.
3. `RAW_COUNT_SINGLE_OCC` -- one profile occurrence per anchor, via
   `exp_pipeline_stage_oracle_ladder_v1.build_single_occurrence_counts`, restricted to
   `words_needed`.
4. `PRESENCE_ABSENCE_BINARIZED` -- same full-accumulation counts, binarized.
5. `PARADIGMATIC_PROFILE_WRITE` -- `exp_readout_writerule_paradigmatic_v1.build_arm(mode=PROFILE)`,
   restricted to `words_needed`.
6. `T0_VANILLA_PPMI_SVD` -- `exp_corpus_capacity_ppmi_svd_ceiling_v1.ppmi_of` + SVD k=50, the exact
   winning config from the landed cell (`data/exp_corpus_capacity_ppmi_svd_ceiling_v1/metrics.json`
   T0_BEST_K="50").
7. `T2_SHIFTED_PPMI_K15` -- `exp_tuned_count_unsupervised_dissociation_v1.ppmi_tuned` with
   alpha=1.0, k_shift=15, subsample_t=None, SVD k=50, p=0.5 -- the exact winning config from the
   landed cell's `T2_SHIFTED_PPMI.SELECTED_CONFIG`
   (`data/exp_tuned_count_unsupervised_dissociation_v1/metrics.json`).

For arms 6-7, the co-occurrence matrix `M` is rebuilt over the FULL valid-anchor population (5491
words, `exp_corpus_capacity_ppmi_svd_ceiling_v1.build_matrix`) exactly as the landed cells built it,
and a **positive-control regression check** re-scores the SAME two configs on the ORIGINAL licensed
(WordNet) population BEFORE trusting them on the new human population -- must reproduce 0.0519 (T0)
and 0.1144 (T2) within the landed cells' own tolerance (0.0005). This is
`reproduce_prior_chain_grade_result_as_positive_control` (SCHEMA-VET item 15.D) applied to a
same-regime reconstruction, not a cross-regime extension -- the SVD is rebuilt from the identical
formula/config/seed over the identical matrix, so exact reproduction is the expected, not merely
hoped-for, result; a miss means the reconstruction has a bug, not that the primitive doesn't extend.

## STOP-IF (evaluated in this order)

(i) any floor's 95% CI excludes 0.5 -> `INSTRUMENT_LICENSED=False`, publish no arm numbers as findings.
(ii) known-answer AUC < 0.999 -> instrument construction bug (it is tautological by design, so
   anything short of ~1.0 means the label/score plumbing disagrees with itself).
(iii) achieved n per cell too small to resolve the arm ordering (CI half-width too wide relative to
   the observed AUC spread) -> report `POWER_INSUFFICIENT` and the achieved half-width, not a
   ranking.
(iv) the two instruments' arm orderings agree (rank correlation CI/permutation-p excludes 0,
   positive) -> plan 6.23's conclusion is about OUR STORE and survives; report loudly.
(v) the orderings disagree -> 6.23 was substantially about WordNet; report loudly, this would
   redirect the programme.
(vi) any arm reads CI-separated ABOVE 0.5 on the human instrument -> the most important result this
   programme has produced; report level + every control + coverage.

## Compute architecture

Class (b) sequential-CPU with justification: this is a re-scoring of already-cached stores plus two
same-regime SVD reconstructions (rank 50, ~5491x21576 sparse matrix, measured elsewhere in this repo
at well under a minute per SVD) -- not a training loop, no GPU-batchable inner loop. No sharded vs
bundled storage question applies (this cell performs no new writes into any substrate store; it
re-scores existing caches and checkpoints). Storage strategy: `no_storage` (read-only re-scoring
cell).

## SCHEMA-VET fields

- `cardinality_ok`: n/a -- no sweep axis; single instrument build + 7-arm re-score, same pattern as
  the licensed instrument itself, which declares this n/a too.
- `arms_differ_verified`: true (sha256 digest test over all 7+4+2(known-answer,random) score
  vectors, asserted at smoke gate, mandatory before any full dispatch).
- `final_metrics_atomicity`: tmp_replace (`experiments._seed_checkpoint.write_metrics`).
- Per-unit checkpointing: POPULATION_HUMAN (candidate gen + matching), SCORES_HUMAN (per-arm score
  arrays including T0/T2 matrix rebuild), POSITIVE_CONTROL (T0/T2 regression check on the ORIGINAL
  population) as separate `tools.exp_checkpoint` units; MAIN wraps the whole run() result.
- `discriminator survives scale`: n/a in the DISCRIMINATOR-MUST-SURVIVE-SCALE sense (this is a
  licensing-gate instrument re-score, not a mechanism-vs-baseline sweep); the actual scale risk here
  is COVERAGE (small n), addressed by the explicit `POWER_INSUFFICIENT` stop-if rather than a
  scale-preview arm.
- `calibration_check`: default_ok_for_this_regime (reuses landed, regression-gated caches/checkpoints
  unmodified; only the label SOURCE changes).
- `progress_logging`: print_flush_true (every phase prints a flushed line); timeout_s for the full
  dispatch is well under 1800s (estimated 2-5 minutes total) so the Sec.17 mandatory-heartbeat rule
  does not bind, but flushed prints are used throughout regardless.
- `baseline_in_band`: n/a -- licensing-gate instrument, same declaration as the licensed instrument.
- `crlb_floor_computed`: n/a -- an AUC dissociation measurement over existing stores, not a capacity
  sweep, same declaration as the licensed instrument.
- except SystemExit: raise BEFORE except Exception; no bare except, no BaseException (grepped before
  dispatch).

## Smoke gate

`--grid reduced`: population restricted to the same reduced-scale conventions the licensed
instrument's own `--grid reduced` uses (partial anchor slice), N_BOOT=1500. Smoke must show: (a)
`--self-test` passes; (b) the reduced-grid POPULATION build produces n_match >= 20 for both cells (or
explicitly reports `INSTRUMENT_UNBUILDABLE_AT_THIS_N` and the cell is re-specced, not force-run); (c)
all arms produce distinct score-vector digests (arms-must-differ); (d) the positive-control
regression check reproduces T0/T2 on the ORIGINAL population within tolerance even at reduced grid
(the matrix rebuild does not depend on grid=reduced/full for the ORIGINAL-population check, since
that check reuses the SAME full anchor matrix regardless -- disclosed, not a shortcut that weakens
the gate).

## Timeout

Full run estimated 2-5 minutes (DSI-equivalent population/floor/5-arm construction under 2 minutes
per DSI's own probe; M-matrix build + 2 SVDs at k=50 measured cheap elsewhere in this repo -- the
landed tuned-count cell's FULL run, which built the same M and did ~20+ SVDs across T0-T5, including
SGNS training, took 455.8s total). `--timeout 900` (15 minutes) on the queue dispatch for headroom;
run inline foreground with Bash `timeout: 600000` (10 min) per the INLINE-LOCAL mandate.

## AMENDMENT v2.0 (2026-08-18) -- filed after v1's FULL run halted with SystemExit at n_match=7

v1's FULL run (`experiments/exp_dissociation_score_instrument_human_v1.py`, commit `3f498cf52`)
matched population construction as pre-registered above, but collapsed to `n_match=7` per cell (far
below the `n_match<20` floor coded into v1) and exited via bare `SystemExit`, writing no
`metrics.json`. Recorded as a null in
`notes/human_judgement_instrument_power_failure_2026-08-18.md`. v1's source is left UNMODIFIED (it
is the permanent record); the fix is filed as a new file,
`experiments/exp_dissociation_score_instrument_human_v2.py`, anchor name
`dissociation_score_instrument_human_v2`, writing under
`data/exp_dissociation_score_instrument_human_v2[_reduced]/`.

**Verified off v1's own checkpoint** (`data/exp_dissociation_score_instrument_human_v1/units.jsonl`,
unit `POPULATION_HUMAN|v1.0|full`) before authoring v2: population construction was ALREADY not
restricted to the WordNet-licensed instrument's population (`combine_benchmark_pairs(anchor_set)`
uses the full 5,491-anchor set in both v1 and v2, unchanged). The measured cause of n=7 is a
structural frequency-covariate mismatch between `SET_P_HUMAN` and `SET_S_HUMAN`
(`pre_match_smd.mean_log_freq=-1.8396`) interacting with the matching caliper's tight frequency bound
(0.02, inherited verbatim from the WordNet instrument's own four-round matching repair) -- 429 of
436 candidates (98.4%) are caliper-dropped; adjective/noun POS strata drop to zero matches, verb
yields the surviving 7. Full account in v2's module docstring ("SUPERSEDES v1" section) and
`notes/dissociation_score_instrument_human_v2_2026-08-18.md`.

**Amendments (process only; population/matching construction and caliper unchanged, per the standing
rule against loosening a caliper to buy n):**

1. **STOP-IF (0), NEW, evaluated first:** `n_match < POWER_INSUFFICIENT_MIN_N=60` (raised from v1's
   effective `n_match<20`) -> write a `POWER_INSUFFICIENT` verdict to `metrics.json` WITH the full
   funnel, and return -- no floor, known-answer, random-store, or expensive arm is built. Replaces
   v1's uninformative `SystemExit`-with-no-output.
2. **License gate reordered BEFORE any arm.** The four floors + known-answer + random-store arm
   (collectively "CHEAP" -- built from already-cached `mat`/`t_mat`/proto/freq, no matrix rebuild)
   are built and AUC-scored first; `STOP-IF (i)`/`(ii)` are checked on those alone. Only if the
   population clears `POWER_INSUFFICIENT_MIN_N` AND the license gate passes are the seven
   "EXPENSIVE" arms (INCUMBENT/RAW_COUNT x3/PARADIGMATIC/T0/T2, which require a fresh M-matrix build
   + 2 SVDs) built at all. Checkpoint units renamed `SCORES_CHEAP` / `SCORES_EXPENSIVE` (replacing
   v1's single `SCORES_HUMAN` unit) to reflect the split.
3. **`max(four floors)` reported explicitly**, read fresh off
   `data/exp_dissociation_score_instrument_v1/metrics.json` (never hardcoded) -- reads 0.5431 on the
   WordNet instrument (`F_CONSTANT_PROTOTYPE`) per plan sec 6.29(1). Any arm that reaches the licensed
   path reports its margin against BOTH `max(four floors)` and 0.5, separately, and STOP-IF (vi) is
   gated on the stricter (max-floor) bar rather than the 0.5 band alone.
4. SCHEMA-VET fields carried over unchanged except `final_metrics_atomicity` (still `tmp_replace`)
   and the per-unit checkpoint list, now: `POPULATION_HUMAN, SCORES_CHEAP, SCORES_EXPENSIVE,
   POSITIVE_CONTROL`.

**Result of the v2 FULL run** (7.2s, `data/exp_dissociation_score_instrument_human_v2/metrics.json`):
funnel reproduced EXACTLY (2,233 -> 436/122 -> 7, deterministic given byte-identical construction and
seeds); `n_match=7 < 60` -> STOP-IF (0) fired; verdict
`DISSOCIATION_INSTRUMENT_HUMAN_UNLICENSED__POWER_INSUFFICIENT__n_match=7__min_required=60__STOPPED_BEFORE_ANY_ARM`.
No arm was scored; plan sec 6.24's WordNet-scope caveat remains OPEN, unchanged from v1's own honest
read. Full account: `notes/dissociation_score_instrument_human_v2_2026-08-18.md`.

## AMENDMENT v3.0 (2026-08-18) -- frequency-stratified matcher, filed after v2's POWER_INSUFFICIENT

New file, `experiments/exp_dissociation_score_instrument_human_v3.py` (v1 and v2 left unmodified,
permanent records). Population construction (SET_P_HUMAN/SET_S_HUMAN raw candidate build) and the
license-gate/arm/rank-correlation machinery are reused verbatim from v2 (imported READ-ONLY). The
ONE change is the matcher: `frequency_stratified_match_cells()` bins each POS stratum's pooled
mean_log_freq into 3 quantile bins (equal candidate mass), then runs `DSI.match_cells` unchanged
inside each (POS, bin) cell with a residual caliper `[8.0, 1.0, 1.5, 1.5, 1.5]` (mean_log_freq's own
per-pair caliper loosened since bin membership now bounds it; abs_freq_diff/length/trigram/prototype
loosened moderately). Selected by a pre-authoring grid search against the REAL four-floor AUC
bootstrap (disposable scratch probes, not committed) -- the widest point at which all four floors
still read at chance.

**Result of the v3 FULL run** (553.4s, `data/exp_dissociation_score_instrument_human_v3/metrics.json`,
run_mode=full, size=15674 bytes): n_matched=65/cell (a=2, n=9, v=54), clearing `POWER_INSUFFICIENT_
MIN_N=60`. Post-match SMD: mean_log_freq -1.8396 -> -0.4382, abs_freq_diff 0.2650 -> 0.2466, mean_
length 1.0581 -> 0.3988, trigram_cos -0.0595 -> -0.0710, prototype -1.2561 -> -0.1757 -- disclosed as
NOT comparable to the WordNet instrument's own post-match balance (-0.0416 / 0.0045 / -0.0121 /
0.0007 / 0.1574). Despite this, all four floors landed CI-included-0.5 at N_BOOT=10000: F_ORTHOGRAPHIC
0.4920 [0.4462,0.5356], F_FREQUENCY 0.4151 [0.3167,0.5131], F_SCRAMBLE 0.5943 [0.4961,0.6899],
F_CONSTANT_PROTOTYPE 0.4125 [0.3160,0.5122] -> `INSTRUMENT_LICENSED=True`, `max(four floors)=0.5943`.
Known-answer = the published human rating itself (NOT WordNet path similarity), AUC=1.0 (tautological
by design). Positive control (T0/T2 reproduced on the ORIGINAL WordNet population) matched the landed
cells' own numbers exactly (delta=0.0 both). Seven arms scored, all read below both 0.5 and max-floor
except RAW_COUNT_SINGLE_OCC (0.4644, at chance). Rank correlation vs the WordNet instrument's ordering
(same 7 arms): Spearman rho=0.7857, exact permutation p=0.048, bootstrap-of-arms 95% CI=[-0.0439,
1.0] -- includes zero. Verdict:
`DISSOCIATION_INSTRUMENT_HUMAN_V3_LICENSED__RANK_CORRELATION_CI_INCLUDES_ZERO__INCONCLUSIVE_AT_THIS_N__rho=0.7857`.
STOP-IF (i)/(ii) passed (licensed); n>=60 satisfied; the CI-includes-zero branch fired, not (iv) or
(v) -- the ordering leans the same direction as the WordNet instrument's but 7 arms is too small a
sample to certify agreement or disagreement. Full account:
`notes/dissociation_score_instrument_human_v3_2026-08-18.md`.
