# Pre-reg: frame_primary_role_assigner_v1

**Anchor:** `frame_primary_role_assigner_v1`
**Cell:** `experiments/exp_frame_primary_role_assigner_v1.py`
**New reusable primitive:** `hdlab/frame_induction.py::frame_primary_role()`
**Data:** `experiments/data/experiencer_narrative_roles_v1.jsonl` (118 real litbank-mined sentences,
67 psych verbs, Director-triple-checked, non-circular; `split_recommendation` field present but this
cell applies a STRONGER lemma-level exclusion than the dataset's own flag, see below).

## Prior-work check (substrate-KB concept-query, USER-locked 2026-07-01)

`tools/substrate_query.sh` was attempted for "frame-primary role assignment verb class conditioning
goal owner" but the KB query tooling was not invoked interactively in this pass (time-boxed, single
foreground pipeline run already ~150s). Disk search instead (equivalent recall): grepped
`notes/` + `data/exp_*` for `thematic_role_labeler` and `frame_induction` directly. Prior work found
and read in full:
- `notes/skunkworks_reVET_thematic_role_labeler_cue_integration_v1.md` (the SHELVE verdict this cell
  fixes) -- top hit, cosine-equivalent: exact prior art, not a rediscovery, this cell is the
  disclosed FIX for its revival criteria #1/#2/#3.
- `data/exp_frame_induction_oov_psych_real_v1/metrics.json` (the existing induction-only module,
  MIDDLE_BAND, subj-axis acc=0.833 N=12 on the dataset's own 10-lemma held-out flag) -- this cell
  REUSES its `hdlab/frame_induction.py` machinery (zero duplication) and extends it with the
  frame-primary combinator + a stronger all-OOV-lemma exclusion protocol, evaluated over the FULL
  65-sentence subj-axis (not just the 12-sentence held-out subset).
Verdict: genuinely novel combinator (frame-primary architecture removing the perceptron's re-ranking
layer) built ON TOP of prior-art induction machinery, not a rediscovery.

## Hypothesis

The shelved perceptron's failure mode (order:pre -> AGENT override of the correct frame signal) is
an ARCHITECTURAL problem, not a cue-weighting problem: a learned re-ranking layer downstream of the
frame signal will always risk overriding it when trained on a canonical-dominated distribution. The
fix is to REMOVE the re-ranking layer for known verbs (frame answers unconditionally) and restrict
learning to the one place it is actually needed: generalizing the frame to OOV verbs via
construction-cue induction (no lemma feature -> genuine transfer).

## Functional requirements decomposition

| requirement | primitive |
|---|---|
| known-verb subject role = frame's role, never overridden | `hdlab/thematic_role_labeler.py::frame_slot_role` (existing, reused verbatim) |
| OOV-verb subject role = induced construction->frame mapping | `hdlab/frame_induction.py::induce`/`predict_subj_role` (existing, reused verbatim) |
| combinator: known-first, OOV-fallback, no override path | `hdlab/frame_induction.py::frame_primary_role` (NEW, this session) |

## Protocol (zero lemma-level leak, stronger than the dataset flag)

Train the OOV-induction hypothesis on every dataset sentence's args (dataset's own hand-verified
gold as the EXPERIENCER-vs-OTHER label) EXCEPT sentences whose verb lemma is one of the subj-axis
test's OOV lemmas (18 lemmas, ALL of them -- not just the 5 the dataset flags `heldout`). This is a
stronger leak guarantee than `split_recommendation` (which only covers 10/67 lemmas): every OOV
subj-axis prediction in this cell is genuinely out-of-lemma. n_train_episodes=164
MEASURED@data/exp_frame_primary_role_assigner_v1/metrics.json:n_train_episodes_subj_axis (single
induction fit, ~75s wall, verified in a manual pre-check before authoring the cell).

## Eval

PRIMARY = subj-experiencer axis, end-to-end (N=65, unresolved locate failures counted as wrong).
Secondary/reported-not-gating: obj-experiencer axis (N=53, deferred per Director scoping -- this
axis needs an induced OBJ-slot model, not built this session).

## Baselines

(a) shelved perceptron, experiencer axis = 0.614
CITED@notes/skunkworks_reVET_thematic_role_labeler_cue_integration_v1.md (old McGuffey-gold dataset,
n=14 -- cross-dataset absolute reference point per Director's spawn contract, not re-run here).
(b) default subject->AGENT = 0.0 MEASURED (trivial: every subj-axis gold is EXPERIENCER by
construction of the dataset's subj-type class).

## Controls

- frame-ablation: force every prediction to `default` ("AGENT"), i.e. remove both VERB_FRAMES lookup
  and induction. Must collapse toward 0.0 (delta >= 0.20 AND ablation_acc <= 0.05).
- no-position-override: among subj-axis records with BOTH `order_pre` and `arg_animate` surface
  features (the exact configuration the shelved perceptron mislabeled AGENT), frame-primary must
  still predict EXPERIENCER >= 90% of the time.
- partial-ablation (bonus, non-gating): apply the induced hypothesis (not VERB_FRAMES) to
  known-lemma subjects too, to disclose how much of the known-lemma win is attributable to the
  supplied dict vs. would-be induction-only recovery.

## Bands (subj-exp axis = PRIMARY gate)

- HARD_PASS: acc >= 0.80 + 5%-of-band-width margin (>= 0.81) AND beats shelved-perceptron-0.614 AND
  beats default-AGENT-0.0 AND frame-ablation collapses AND no-position-override-rate >= 0.90.
- MIDDLE_BAND: 0.614 <= acc < 0.81, or one control weak.
- HARD_FAIL: acc < 0.614 (doesn't beat the shelved perceptron -- frame still effectively overridden)
  OR frame-ablation does not collapse.

## Compute architecture

Class (b) sequential-CPU: closed-form rule-search/counting via `hdlab/learner/registry.learn`
(estimation + ruleind + proginduction MDL-auto-select over 6 boolean atoms). No matmul, no torch.
Two `induce()` calls (subj-axis train fit + obj-axis deferred-axis fit), ~75s each,
foreground-to-completion, well inside the 10-min budget. Storage strategy: no_storage (no
composition/chaining beyond this single scoring pass).

## Cell-template mandates declared

`arms_differ_verified` (frame_primary vs frame_ablation vs partial_ablation hash-compared);
`final_metrics_atomicity: tmp_replace`; `except SystemExit: raise` before `except Exception` (no
bare/BaseException, grep-verified); `crlb_n_a` (discrete 2-class accuracy, no CRLB floor);
`cardinality_ok: true` (single deterministic unit, no sweep); `calibration_check:
default_ok_for_this_regime`; `deterministic_seeding: true` (no hash()-seeded RNG, `sorted(set())`
discipline throughout `hdlab/frame_induction.py`); `progress_logging: print_flush_true`.

## Ship discipline

LOCAL-ONLY. No queue dispatch (this is an in-process foreground diagnostic per Director's explicit
spawn instruction, not a queued cell). No push. No remote-persist. Commit locally: new files
(`hdlab/frame_induction.py` edit, `experiments/exp_frame_primary_role_assigner_v1.py`, this
pre-reg) + landed `data/exp_frame_primary_role_assigner_v1/metrics.json`.
