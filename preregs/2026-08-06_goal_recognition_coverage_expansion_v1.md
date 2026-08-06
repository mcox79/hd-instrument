# Pre-reg: goal-recognition coverage expansion (CONATIVE + INTENTION pass-classes + bouletic extension)

Date: 2026-08-06. Status: **PRE-REGISTERED, NOT YET EXECUTED** (spec-only cycle; a cell-author builds and
runs this later). Companion spec: `notes/formalize_goal_recognition_coverage_expansion_conative_intention_
2026-08-06.md` (read first -- has the owned-detector coverage map, the corrected 19/44 true baseline, the
brain-mechanism map, and the full genuinely-out-of-scope list). This EXTENDS `hdlab/goal_typing.py`
(1200 lines, production, cert-covered) -- a small, targeted taxonomy fix, not a new module.

Task: close the upstream goal-RECOGNITION coverage gap that caps every downstream organ gated on
`find_desired_state`/`has_goal` (outcome-valence congruence, goal-owner selection, the word-acquisition
Channel-B adapter). Root cause (confirmed by reading the code, not inferred): `try` is misfiled into
`ASPECTUAL_STOP` and `decide`/`determine` are unclassified/misfiled into `OTHER_STOP_UNCHANGED`, even
though all three take the identical infinitival-CONTROL/ECM shape the module already parses for
`want`/`hope`. This is a category-conflation bug (conative ATTEMPT and intention/DECISION verbs wrongly
grouped with pure-aspectual verbs), not a threshold-tuning gap.

## What is being built (delta, all edits confined to `hdlab/goal_typing.py`)

1. **New set `CONATIVE_PASS = {"try","tries","tried","trying"}`** (ATTEMPT class, Talmy 1988
   force-dynamics AGONIST-exertion -- goal recognized regardless of attempt success/failure).
2. **New set `INTENTION_PASS = {"decide","decides","decided","deciding","determine","determines",
   "determined","determining"}`** (DECISION/COMMITMENT class, Bratman 1987 intention-vs-desire).
3. **Extend `DESIDERATIVE_PASS`** with bouletic-preference verbs `like`/`love` (base+3sg+past+gerund:
   `like, likes, liked, liking, love, loves, loved, loving`) -- same semantic class as want/wish/hope, not
   a new category.
4. **Extend `DESIDERATIVE_PASS`'s existing 10 bases with gerund forms** (currently absent for ALL of
   them): `wanting, wishing, hoping, meaning, planning, intending, aiming, longing, yearning, desiring`.
   Bundled because it is the same mechanism class (literal-set membership) and cheap, but reported as a
   SEPARATE row in the results table (Gate 0 below) so its contribution is not conflated with the new
   pass-classes' contribution.
5. **Remove `try/tries/tried/trying` from `ASPECTUAL_STOP`; remove `decide/decides/decided` from
   `OTHER_STOP_UNCHANGED`.** `determine*` requires no removal (was in neither set). **This removal and
   the additions in (1)-(2) MUST land in the same edit** -- `assert DESIDERATIVE_PASS.isdisjoint
   (PARTITIONED_STOP)` (L317) will `AssertionError` at import time otherwise, a hard crash, not a silent
   partial-fix.
6. **Both `find_desired_state`'s `dv_idx` gate (L718) and `_control_verb_is_aspectual_like`'s Tier-1
   checks (L337-340) must test the union** `GOAL_GOVERNING_PASS = DESIDERATIVE_PASS | CONATIVE_PASS |
   INTENTION_PASS` (name/exact refactor shape at implementer's discretion; the union coverage at BOTH
   call sites is the load-bearing requirement, not the variable name).
7. **RECOMMENDED, not gated:** remove `"try"` from `_GOAL_ASPECT_SEED_LEMMAS` (L322-323, Tier-2 seed pool
   for `action_frame_feats`'s OOV fallback) so future OOV conative siblings (`attempt`, `endeavor`,
   `strive`) are not biased toward the wrong (aspectual-suppress) pool via similarity. Zero eval items
   depend on this; it is a coherence fix for future OOV verbs, may be skipped without affecting this
   pre-reg's gates.

## Held-out set / test bed

`experiments/data/goal_bearing_modern_eval_v1.jsonl` (44 items, `notes/research_goal_bearing_modern_eval_
2026-08-06.md`). All 44 items are in scope for the primary coverage metric (unlike increment-1b's 36-item
outcome-verb subset, this metric is about `find_desired_state` firing on the `goal_text` field, which
every item has).

## Baselines (re-derived directly this cycle, superseding the Director's proxy estimate)

- **TRUE current baseline: 19/44 = 0.4318** (`find_desired_state` on unmodified `DESIDERATIVE_PASS`
  against all 44 `goal_text` fields, measured this cycle -- NOT the `goal_verb_lemma`-distribution-based
  estimate of 22/44, which over/under-counts in both directions; see companion spec "Corrected baseline"
  section for the itemized reconciliation).
- **Simulated post-fix ceiling (production `find_desired_state`, only `DESIDERATIVE_PASS` monkeypatched,
  no other code touched): 33/44 = 0.75** (19 baseline + 13 from CONATIVE_PASS/INTENTION_PASS/like/love +
  1 from the gerund-form bonus). This is the number the real edit should reproduce; a material
  undershoot signals an implementation divergence from this spec, not a re-measurement of the ceiling.

## Precision-guard control set (bare-transitive + negation + aspectual-unaffected)

Measured THIS cycle against the full combined patch (production `find_desired_state`, `DESIDERATIVE_PASS`
monkeypatched to include all of items 1-4 above):

| Tag | Sentence | Required verdict | Measured this cycle |
|---|---|---|---|
| bare_transitive | "She tried the cake before dinner." | must NOT fire | not fired (confirmed) |
| bare_transitive | "He decided the matter without delay." | must NOT fire | not fired (confirmed) |
| bare_transitive | "She liked the cake very much." | must NOT fire | not fired (confirmed) |
| bare_transitive | "He loved the old garden behind the house." | must NOT fire | not fired (confirmed) |
| bare_transitive | "The judges determined the outcome of the contest." | must NOT fire | not fired (confirmed) |
| bare_transitive | "They tried the door but it was locked." | must NOT fire | not fired (confirmed) |
| aspectual_unaffected | "Dawn began to open the gate." | must NOT fire | not fired (confirmed) |
| aspectual_unaffected | "Fay started to close the shop." | must NOT fire | not fired (confirmed) |
| aspectual_unaffected | "He managed to escape the room." | must NOT fire | not fired (confirmed) |
| gerund_noun_phrase | "She was hoping for rain." | must NOT fire (PP complement, not infinitival) | not fired (confirmed) |
| gerund_noun_phrase | "He was wanting attention all day." | must NOT fire (PP/NP complement, not infinitival) | not fired (confirmed) |

**Result this cycle: 0/11 false fires.** This IS the mandatory precision guard the Director's brief named
("try/decide/beg express a goal ONLY with an infinitival/clausal complement... not as bare transitives")
-- the `to`-token-anchored scan structurally protects against bare-transitive over-firing for every verb
in every set, old or new, by construction (there is no `to VP` for the scan to find). The `try`/`decide`
family's precision safety is not a new property being asserted, it is inherited unmodified from the
mechanism `want`/`hope` already rely on.

**Known, PRE-EXISTING, explicitly NOT gated this increment (negation-scope, reported for visibility):**

| Tag | Sentence | Naive expectation | Measured this cycle |
|---|---|---|---|
| negation (pre-existing) | "She did not try to escape from the tower." | should NOT fire (intent disclaimed) | **fires** (referent="not", garbage) |
| negation (pre-existing) | "He never decided to leave the village." | should NOT fire | **fires** |
| negation (pre-existing) | "She did not mean to intoxicate Diana." | should NOT fire | **fires** (confirmed pre-existing today, `mean` unmodified) |
| negation (pre-existing) | "He did not like to disturb her." | should NOT fire | **fires** |

This bug predates this increment (`"did not mean to..."` already false-fires against unmodified,
unpatched `DESIDERATIVE_PASS` on disk today) and is the Director's own already-named next roadmap item
("negation-scope"). Adding `try`/`decide`/`like` widens the SURFACE AREA of this pre-existing bug (more
verbs now sit behind the same unguarded gate) without being its cause. **Report the negation false-fire
rate in the landed-VET writeup; it does not gate PASS/FAIL for this increment**, and must not be silently
dropped from the record.

## Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE-BAND)

**Primary metric:** `coverage` = fraction of the 44 eval items where `find_desired_state(item["goal_
text"])` returns non-`None`, measured against the LIVE, edited `hdlab/goal_typing.py` (not a
monkeypatched simulation -- the real file edit).

**HARD-PASS** (ALL of the following):
1. `coverage >= 30/44` (0.682, a +0.25 absolute lift over the verified 19/44 baseline -- set with slack
   below the simulated 33/44 ceiling to absorb small implementation deviations, e.g. tokenization
   differences between the scratch simulation and the landed code).
2. `precision_control_false_fires == 0/11` on the exact bare-transitive/aspectual/gerund-noun-phrase
   control set above (verbatim reuse -- do not substitute different control sentences).
3. `import hdlab.goal_typing` succeeds with no `AssertionError` (the `DESIDERATIVE_PASS.isdisjoint
   (PARTITIONED_STOP)` load-bearing check, item 5 of "what is being built").
4. `python verification/run_certification.py` (via `.venv/Scripts/python.exe`) reproduces the pre-edit
   baseline of 220 passed / 3 skipped, unchanged. If any existing test fails, trace it by hand against
   `verification/` before treating this as a HARD-FAIL trigger -- confirm the failure is a genuine
   regression from THIS edit (e.g. a self_test assertion that implicitly depended on `try`/`decide` being
   suppressed) rather than an unrelated flake.
5. `try_family_true_positive_recall`: at least 6/8 of the eval's `try`-labeled items fire (measured
   ceiling this cycle: 7/8 -- `agg_gilbert_pond_rescue_friendship_plea_ch28` is a confirmed mislabel with
   no literal `try` token in `goal_text`, out of scope by construction; expect exactly this one to miss).
6. `decide_determine_true_positive_recall`: at least 3/5 of the eval's `decide`/`determine`-labeled items
   fire (measured ceiling this cycle: 4/5 -- `agg_matthew_puffed_sleeves_dress_ch25` is a confirmed finite
   that-clause complement, out of scope by construction; expect exactly this one to miss).

**HARD-FAIL** (ANY of the following):
- `coverage <= 22/44` (0.5 -- does not clear even the Director's original, since-corrected estimate).
- `precision_control_false_fires >= 1/11` -- a bare-transitive or aspectual-unaffected control produces a
  false GOAL fire (this would mean the `to`-token infinitival gate itself broke, not just a class-
  membership tuning issue -- treat as a structural regression, stop and re-diagnose before re-running).
- `AssertionError` at import (the disjointness invariant broke -- the removal-half of item 5 in "what is
  being built" was skipped or landed separately from the addition-half).
- Cert regresses below 220 passed / 3 skipped for a reason traced to this edit.
- `try_family_true_positive_recall <= 2/8` OR `decide_determine_true_positive_recall <= 1/5` -- would mean
  the new pass-classes are not actually reaching the infinitival scan (e.g. the union-set refactor in
  item 6 of "what is being built" was applied to only one of the two call sites, or a tokenization
  mismatch between this pre-reg's simulation and the landed code).

**MIDDLE-BAND**: `coverage` in `(22/44, 30/44)`, OR gate 1 clears but `try_family_true_positive_recall` or
`decide_determine_true_positive_recall` land below their HARD-PASS floor without tripping the HARD-FAIL
floor, OR cert shows a traced-but-unresolved discrepancy. Report per this module's own MIDDLE_BAND
precedent (`hdlab/goal_typing.py` module docstring, outcome-valence promotion) -- do not force a label
either direction.

## Diagnostic predictions (informational, pre-registered, not gating)

1. **Negation false-fire rate** on the 4-item negation control set above -- expected 4/4 fires (matching
   this cycle's simulation) given the mechanism is unmodified w.r.t. negation; report as visibility into
   the pre-existing bug's surface area, feeding the Director's separately-named negation-scope increment.
2. **Per-item breakdown of the two confirmed-miss items** (`agg_gilbert_pond_rescue_friendship_plea_
   ch28`, `agg_matthew_puffed_sleeves_dress_ch25`) -- confirm they remain non-firing on the live edit for
   the SAME reason identified this cycle (mislabel / finite-clause), not a new, different failure mode.
3. **Gerund-form contribution isolated**: report `coverage` with gerund forms OFF (should reproduce
   32/44) vs ON (should reproduce 33/44) as two separate numbers, not just the combined 33/44, so the
   two independent fixes (class-taxonomy vs inflection-enumeration) are each auditable.

## Compute architecture

Sequential-CPU, negligible cost. This is a set-membership edit to already-loaded module-level constants
plus a 44-item + 11-item + 4-item string-matching pass through an existing O(sentence-length) function --
no new tensor ops, no FHRR calls, no training. Expected wall time: sub-second for the full eval +
control-set pass. `crlb_n/a`: not a capacity/noise-floor cell.

## Cardinality / discriminator / atomicity gates (SCHEMA-VET checklist)

- `cardinality_ok`: `EXPECTED_N_UNITS` = 44 (primary coverage) + 11 (precision controls) + 4 (negation
  diagnostic) + 1 (cert re-run) + 1 (gerund-isolated ablation) = 61 units; trivially fast, resumability
  via `tools/exp_checkpoint.py` is a formality here (no unit takes more than milliseconds) but still
  required per the mandatory multi-unit-cell convention.
- `discriminator_reachability`: TRUE -- 44-item binary (fired/not-fired) coverage metric, floor 19/44
  (0.432), simulated ceiling 33/44 (0.75), not saturated by construction (18/44 items are confirmed,
  named, out-of-scope non-firers that this fix structurally cannot reach -- see companion spec).
- `baseline_in_band`: N/A -- direct measurement against fixed gold (`goal_text` presence of a governing
  verb + infinitival), both baselines (19/44, control-set 0/11) are REAL, measured off the live eval file
  and live module state this cycle, not assumed or back-computed.
- `arms_differ_verified`: pre-edit vs post-edit `DESIDERATIVE_PASS`/`CONATIVE_PASS`/`INTENTION_PASS`
  set contents must hash-differ (trivial: the sets are literally different by construction of the edit).
- `final_metrics_atomicity`: `tmp_replace`.
- `deterministic_seeding`: N/A -- no RNG anywhere in this mechanism (pure string/set membership).
- `progress_logging`: not required (sub-second total runtime).

## Cert gate (MANDATORY -- touches production `hdlab/goal_typing.py`)

`python verification/run_certification.py` via `.venv/Scripts/python.exe` BEFORE and AFTER the edit;
baseline to reproduce: 220 passed, 3 skipped (this module's own documented baseline as of the 2026-08-06
outcome-valence promotion, unchanged by that promotion's own MIDDLE_BAND verdict since the promotion
proceeded on strict-ADD + zero-regression strength). Must stay 220/3. Per the "what is being built" item
5 disjointness-assertion note: if cert fails at IMPORT (not at a specific test), check
`DESIDERATIVE_PASS.isdisjoint(PARTITIONED_STOP)` FIRST before any deeper diagnosis -- it is the single
most likely, cheapest-to-diagnose failure mode of this specific edit.

## Files to be touched

- `hdlab/goal_typing.py` (EDIT) -- `CONATIVE_PASS`/`INTENTION_PASS` new sets; `DESIDERATIVE_PASS`
  extension (like/love + gerund forms); removal of `try*`/`decide*` from `ASPECTUAL_STOP`/`OTHER_STOP_
  UNCHANGED`; `GOAL_GOVERNING_PASS` union referenced by both `find_desired_state` and
  `_control_verb_is_aspectual_like`; OPTIONAL `_GOAL_ASPECT_SEED_LEMMAS` cleanup (item 7).
- `verification/` -- add at least one decisive self-test assertion pair, mirroring the existing pattern
  at `hdlab/goal_typing.py` `self_test()` L1084-1090 (`"Beth hoped to win..."` fires /
  `"Dawn began to open..."` does not): e.g. `has_goal("Tom tried to steal sugar under his aunt's nose.",
  "tom")` must be `True`; `has_goal("She tried the cake before dinner.", "she")` must be `False` (this is
  the module's OWN convention for decisive-case regression protection, should be added not just relied
  on via this pre-reg's external harness).
- `experiments/exp_goal_recognition_coverage_expansion_v1.py` (NEW, if a standalone experiment cell is
  wanted for the landed-VET record) -- reproduces the coverage table above against the live edited
  module; resumable + atomic-write + self-test per the mandates. Given the near-zero compute cost, this
  could alternatively be folded directly into `hdlab/goal_typing.py`'s own `self_test()` as new decisive
  assertions rather than a separate experiment cell -- implementer's call, document which.
- `experiments/data/goal_bearing_modern_eval_v1.jsonl` -- LEFT UNTOUCHED (source-of-truth convention;
  this pre-reg reads it, does not modify it).

## Prior-work check (per exp_dev standing discipline)

Direct prior-art: `hdlab/goal_typing.py`'s own `DESIDERATIVE_PASS`/`ASPECTUAL_STOP`/`OTHER_STOP_UNCHANGED`
partition (commit `5da76bf34` lineage, module docstring L19-27) already established the precedent that
control-verb classes gate the purpose-infinitival construction differently by intentional-state type --
this pre-reg extends that SAME partition with two classes the original partition's own comments (L301-302,
L310-311) flagged as unclassified/placeholder, not proposing a new mechanism. The Tier-2 open-vocab
`_control_verb_is_aspectual_like` fallback (`_GOAL_ASPECT_SEED_LEMMAS`/`_GOAL_DESID_SEED_LEMMAS`,
`preregs/2026-08-06_verb_class_openvocab_similarity_v1.md`) is the only existing OOV-generalization
mechanism for this gate; item 7 above is the minimal coherence fix so it does not fight the Tier-1
reclassification. No existing finite-clause-complement parser exists anywhere in `hdlab/` (checked: no hit
for `complementizer`/`finite_clause`/`that_clause`-adjacent naming) -- confirmed as genuinely new future
work, not something already built and merely unwired.
