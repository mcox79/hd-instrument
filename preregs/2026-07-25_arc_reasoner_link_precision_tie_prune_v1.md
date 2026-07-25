# Pre-registration: arc_reasoner_link_precision_tie_prune_v1

Filed 2026-07-25 (exp_dev). INLINE-LOCAL foreground-to-completion; NO push/remote-persist; VET-PENDING
(skunkworks owns landed-VET); NO atom banking. Bands fixed BEFORE the run; reported STRAIGHT, NOT tuned.

## Question (the LAST untested structural lever)

VET 29569 (capstone, cell `arc_reasoner_symbolic_tiebreak_v1`) MEASURED, on the 206 questions the composed
DerivationReasoner derives at `link_mode=lemma_syn`:
- gold_only  26 @ 1.00 (mechanism perfect)
- TIE        66 @ 0.3636 (gold AND >=1 distractor both derive; symbolic tie-break d_tie=0.0 -> EXHAUSTED)
- dist_only 114 @ 0.00 (gold unreachable)

The symbolic tie-break is EXHAUSTED (d=0). The remaining untested structural lever: some TIEs may be
SPURIOUS -- a distractor co-derives only because the entity-linking bridge (lemma_syn WordNet-synonym
expansion) mapped a distractor word onto a rule-entity LOOSELY, not because it is a genuine competing
answer. HYPOTHESIS: tightening entity-link PRECISION prunes the distractor's spurious derivation PRE-tie,
converting TIE -> gold_only -> the reasoner then picks gold clean (gold_only is 1.00 by construction).

## Lever (one variable = entity-link precision)

Reuse `hdlab/reasoner.py` DerivationReasoner UNCHANGED (opt-in `link_mode`; graph/search/CI/decision
identical; `tiebreak_mode=legacy` fixed across the sweep). Entity-link precision sweep (loose -> tight):
- `lemma_syn` (LOOSE, the VET baseline; defines the 66 ties): glove UNION lemma-exact UNION WordNet single-token synonyms
- `lemma`     (MID; drops the WordNet-synonym bridge): glove UNION lemma-exact
- `glove`     (TIGHT; drops the whole symbolic lemma bridge): glove cos>=tau_unify only

Rationale: the synonym bridge (lemma_syn-only) is the loosest hop and the prime suspect for spurious
distractor links. `lemma` isolates "drop synonyms" (keep lemma-exact); `glove` is the strictest control.
`link_mode` is a per-instance attribute used only at query time; ONE reasoner instance, flip the mode,
caches correctly keyed by mode -> genuine one-variable sweep, no graph rebuild (rule graph is mode-independent).

## Per-question instrument (the decisive novel measurement)

Baseline = `lemma_syn`. Compute the derived partition; the TIE qids are the 66 ties. For each tighter
config T in {lemma, glove}, re-evaluate ALL test questions and cross-tabulate each baseline-tie qid's new
subset:
- new == gold_only   -> CONVERTED  (spurious tie pruned; distractor derivation removed, gold kept)  [GOOD]
- new == tie         -> GENUINE    (both still derive; meaning-bound)
- new == dist_only   -> BROKE_GOLD (gold derivation pruned, distractor survives)                     [BAD]
- new == not_derived -> BROKE_BOTH (both pruned; gold-coverage lost)                                  [BAD]
BROKE = BROKE_GOLD + BROKE_BOTH (any gold-derivation lost).

## Guardrail (non-negotiable)

- gold_only@1.00 preserved: of the baseline 26 gold_only questions, accuracy under T must stay >= 0.95
  (`GOLD_ONLY_FLOOR`). (Tightening can only drop a gold_only Q to not_derived; a drop that flips the answer
  wrong breaks the guardrail.)
- gold-coverage must NOT collapse: `gold_cov_ratio[T] = n_gold_derivable_valid[T] / n_gold_derivable_valid[base]`
  must stay >= 0.90 (`GOLD_COV_FLOOR`) for T's conversions to count as a clean structural gain. Over-tightening
  that prunes GOLD chains = trading coverage for false precision = NOT a win.

## Pre-registered bands (fixed thresholds)

- `CONV_PASS   = 10`   (>= 10 of 66 ties CONVERTED at a gold-coverage-preserving config = prunable/spurious)
- `CONV_STUCK  = 5`    (< 5 CONVERTED at every gold-cov-preserving config = ties genuine)
- `BROKE_MAX_RATIO = 0.5` (BROKE <= 0.5 * CONVERTED for the config to count as clean)
- `GOLD_COV_FLOOR   = 0.90`
- `GOLD_ONLY_FLOOR  = 0.95`
- `DERIVED_ACC_RISE  = 0.05` (config derived-acc >= baseline lemma_syn derived-acc + 0.05)
- `CHANCE = 0.25` (fixed reference; config derived-acc must exceed chance)

Evaluate on the BEST config that passes the gold-coverage + gold_only guardrails.

## Verdict logic (can-fail, pre-registered)

- PRECISION-CONVERTS-TIES-functional: exists T with gold_cov_ratio>=0.90 AND gold_only_preserved>=0.95 AND
  CONVERTED[T] >= CONV_PASS AND BROKE[T] <= BROKE_MAX_RATIO*CONVERTED[T] AND
  derived_acc[T] >= base_derived_acc + DERIVED_ACC_RISE AND derived_acc[T] > CHANCE. => real structural gain.
- HONEST-NEG-ties-genuine-meaning-bound: for ALL T, EITHER CONVERTED[T] < CONV_STUCK at every
  gold-cov-preserving config (ties genuine) OR every config with CONVERTED>=CONV_STUCK violates the
  gold-coverage guardrail (any real conversion requires breaking gold-coverage). => both structural doors
  measured shut; grounded meaning is the lever.
- MIDDLE: partial (some conversion, sub-threshold, or gains marginal / guardrail borderline).

## Compute architecture

Sequential-CPU, justified: the reasoner is a symbolic graph search over ~215 nodes / ~209 typed edges with a
thin-cosine encoder query; no matmul-heavy phase grid. Precedent: symbolic_tiebreak_v1 ran full 1172-Q test
in 92.9s for 2 modes. This cell = 3 link modes over the same instance ~= 150-200s. Wall < 10 min foreground.
Storage: no_storage (no substrate item storage; rule graph in memory). progress_logging: print_flush_true.

## SCHEMA-VET fields

- discriminator: PARTITION-CONVERSION count (per-tie CONVERTED/GENUINE/BROKE), telemetry-sensitive (not
  analytically pinned; measured off the real rule graph + real ARC test). can_fail: yes (aggregate hints
  gold-coverage 108->73 at lemma => guardrail may bite => HONEST-NEG plausible).
- baseline_in_band: baseline derived-acc 0.2427 ~ chance (measurable band; the whole point is whether
  precision moves it up).
- arms_differ: link modes produce DIFFERENT node-link sets (self-test asserts distractor pruned lemma_syn->lemma).
- final_metrics_atomicity: tmp_replace. crash_diagnostic_present: yes. start_marker_written: yes.
  heartbeat_present: yes. deterministic_seeding: fixed SEED, numpy default_rng, sorted iteration.
- crlb_n/a: no quantitative noise floor; discriminator is a discrete partition-conversion count.
- calibration_check: default_ok_for_this_regime (thresholds inherited UNCHANGED from the reasoner; precision
  is swept, not tuned to labels).
- positive_control: baseline lemma_syn reproduces the VET partition (26/66/114) within tolerance as arm 0.
- real_code_path: self-test builds the REAL DerivationReasoner over a hand rule-set (FakeBase, GloVe-free)
  with a PLANTED spurious tie (distractor links only via WN synonym) + a genuine tie + a broke-gold case;
  asserts the cross-tab classifies all three correctly and the sweep prunes the spurious distractor.
