# False certification: `verify_goal_typing` 18/18 rested on a broken stemmer (2026-08-13)

STATUS: investigation only. **No fix applied to `hdlab/goal_typing.py` or `hdlab/goal_owner_select.py`
in this dispatch.** `hdlab/thematic_role_labeler.py` (the correct lemma fix) is NOT reverted and must
not be. Every number below was recomputed in-process off disk today; the tool invocations are named
so each is re-runnable.

---

## 1. What was certified

`verification/verify_goal_typing.py` is the WIRE-DON'T-ISLAND promotion witness for
`hdlab/goal_typing.py`. It asserts three things about the promoted organ:

| check | claim | asserted at |
|---|---|---|
| (1) `explicit_psych` | owner-selection accuracy **18/18 = 1.0**, all 3 seeds, on the recency-trap divergent subset of `experiments/data/goal_owner_fair_v1.jsonl` | `verify_goal_typing.py:98` (`assert acc == 1.0`), declared `:10-14`, `:156` |
| (2) `action_implied` | **10/10 = 1.0**, all 3 seeds, same harness | `verify_goal_typing.py:98`, `:157` |
| (3) aspectual precision probe | **0/6** false GOAL on the genuinely-aspectual items, 3 seeds | `verify_goal_typing.py:131` |

The same numbers are asserted in the organ's own docstring (`hdlab/goal_typing.py:29-31`) and in the
capability registry (`data/capability_registry.jsonl` line 66).

## 2. The certification depended on a bug

`hdlab/thematic_role_labeler.py::lemma_verb` was an unguarded suffix stripper. On `missed` it hit the
double-consonant branch: `w[:-2] == "miss"`, `base[-1] == base[-2] == "s"` -> return `base[:-1]` ->
**`mis`**. Verified on disk at the certification commit itself:
`git show 5da76bf34:hdlab/thematic_role_labeler.py`.

`miss` is listed in `PSYCH_VERBS` (`hdlab/thematic_role_labeler.py:68`), i.e. `subj=EXPERIENCER`. That
listing was ALSO present at `5da76bf34` (verified, same `git show`, line 57 of that revision). So the
two ingredients of the defect were both in place at certification time; the truncation `missed -> mis`
(and `mis -> mi`, role `AGENT`) was the only thing keeping them apart.

With the 2026-08-13 fix, `lemma_verb("missed") == "miss"` and
`frame_primary_role("miss", [], 0, None, "subj") == "EXPERIENCER"`.

### Single-variable control (recomputed today, not inherited)

Patch **only** `lemma_verb("missed") -> "mis"`, leave the entire rest of the corrected lemmatiser and
all organ code untouched:

```
CONTROL(missed->mis) explicit_psych seed 0/1/2  acc 1.0  misses []
CONTROL(missed->mis) action_implied seed 0/1/2  acc 1.0  misses []
CONTROL(missed->mis) verification/test_goal_owner_select.py::check_full_instrument_48_of_48  PASSES
CONTROL(missed->mis) test_outcome_valence_goal_congruence::backward_compat_owner_48_of_48  PASSES
```

One token restores every failing goal-family certification. **The 18/18 was never a property of the
mechanism; it was a property of the corruption.**

Note for scope: 21 of the 281 tokens in the bank + probe vocabulary lemmatise differently under the
old vs new stemmer (`appl->apple`, `hop->hope`, `manag->manage`, `ceas->cease`, ...). Only `missed`
is behaviourally load-bearing on these banks -- established by the control above, not assumed.

## 3. The defect the fix exposed: self-satisfying GOAL evidence

Chain, with file:line:

1. `hdlab/goal_typing.py:269-273` -- `c3_has_desire` walks every token of the sentence, lemmatises it
   and fires on any `EXPERIENCER` verb. On the **outcome** sentence `"Kept from the gate, she missed
   her turn and was sorry."` it now returns `True` via `missed -> miss -> EXPERIENCER`.
2. `hdlab/goal_typing.py:297-298` -- `type_sentence_events_c3` therefore appends `(subject, R_GOAL)`,
   where `subject` is whatever entity the CALLER passed for that sentence.
3. `experiments/exp_c5_real_coref_endtoend_purpose_infinitival_v1.py:305-307` (`build_role_seq`, the
   second loop, reused verbatim by `verify_goal_typing.run_item_promoted:61-66`) -- for the final
   sentence the caller passes **the candidate's own outcome entity**. So the fabricated GOAL is bound
   to the very entity the candidate is proposing.
4. `hdlab/goal_owner_select.py:149-153` -- `directed_goal_outcome_score` returns `1.0` iff the entity
   at `outcome_pos` also carries a GOAL **in the same register**. Because step 3 minted that GOAL from
   the outcome sentence and bound it to that same entity, the test is now satisfied *by construction*,
   for **every** candidate. The score's entire documented discriminative power -- "a candidate that
   binds the outcome to a goal-less entity scores 0.0 while one that binds it to the true goal-holder
   scores 1.0" (`:143-146`) -- is destroyed.
5. `verify_goal_typing.py:78-81` -- `score_c - score_b == 1.0 - 1.0 == 0.0`, inside
   `ABSTAIN_BAND_DEFAULT = 0.02`, so `decide_keep_or_revert` returns `None` -> `adopt != "content"` ->
   `final_owner = cluster_ids_b[outcome_pos]` = the **recency positional baseline** = the foil.

Measured trace, `t03_beth_fair_foil_ruth`, seed 0:

```
gold=beth  baseline(recency)=ruth  coref=beth
role_seq_b ['GOAL','GOAL','OUTCOME_UNMET'] ids ['beth','ruth','ruth']   score_b 1.0
role_seq_c ['GOAL','GOAL','OUTCOME_UNMET'] ids ['beth','beth','beth']   score_c 1.0
adopt None -> final_owner ruth -> WRONG
```

The middle `GOAL` in each sequence is the fabricated one. Contrast `t12_jo_garden_foil_ruth`, whose
outcome sentence says `reached` (`reach -> AGENT`, no fabricated GOAL): `score_b 0.0`, `score_c 1.0`,
`adopt content`, correct.

### Is this a ranking/selection defect, or bad test items?

**A real ranking/selection defect.** Evidence:

- **Predictive, not post-hoc.** Across both banks, exactly 3 of the 28 divergent items have an outcome
  sentence that itself mints a GOAL (`c3_has_desire(last_sentence) == True`):
  `t03_beth_fair_foil_ruth`, `t04_meg_market_foil_amy`, `t20_ann_apples_foil_jo`. Those are **exactly**
  the 3 items that now fail, and the only ones. The condition predicts the failure set with no
  residual.
- **The failure mode is degeneracy, not a wrong answer.** The scorer does not prefer the wrong
  candidate; it becomes *unable to distinguish any candidate* (all score 1.0) and the abstain band
  silently converts "no information" into "keep the recency baseline". A discriminator whose evidence
  can be minted by the candidate under test is not a discriminator.
- **The items are sound.** `t03`/`t04`/`t20` have correct gold, a real recency trap, and are the exact
  construction the bank was built to probe. `t03` was in fact PRE-REGISTERED as an expected miss in the
  original cell (`exp_c5_real_coref_endtoend_purpose_infinitival_v1.py:81-82`, "HYPOTHESIZED@... stays
  at 16/18, NOT 18/18"); it was only "recovered" by the 2026-08-06 desiderative partition.
- **The module already knows `miss` is an outcome word.** `miss`/`missed` are in `V2_OUTCOME_UNMET`
  (`hdlab/goal_typing.py:192-194`) and in `FAIL_LOSE` (`:633`). The same token is simultaneously
  consumed as OUTCOME evidence and as GOAL evidence in the same clause. That is an internal
  contradiction in the organ, independent of any test item.
- **The mirror-image guard already exists.** `_goal_complement_verb_indices`
  (`hdlab/goal_typing.py:441-459`, the 2026-08-06 "bystander mis-bind fix") exists precisely to stop a
  GOAL clause's own complement verb being read as an OUTCOME. The reverse direction -- an OUTCOME
  clause's own verb being read as a GOAL -- has no guard. The defect sits in the acknowledged gap of an
  already-recognised problem class.

There is a secondary, genuine word-sense issue: `"missed her turn"` / `"missed her footing"` /
`"missed it"` are the FAIL-TO-ATTAIN sense, not the psych-longing sense. `frame_primary_role` has no
sense disambiguation (`hdlab/frame_induction.py`, `if lemma in VERB_FRAMES: return
frame_slot_role(lemma, slot)` unconditionally). But the sense error is not load-bearing for the fix:
even a legitimately-detected GOAL in the outcome clause would still degenerate the directed score by
step 3-4.

## 4. The honest baseline

All figures MEASURED today, working tree (`hdlab/thematic_role_labeler.py` modified, uncommitted),
3 seeds, deterministic and identical across seeds.

| check | certified claim | **true value now** | failing items |
|---|---|---|---|
| `explicit_psych` divergent | 18/18 = 1.0 | **16/18 = 0.8889** | `t03_beth_fair_foil_ruth`, `t04_meg_market_foil_amy` |
| `action_implied` divergent | 10/10 = 1.0 | **9/10 = 0.90** | `t20_ann_apples_foil_jo` |
| aspectual precision probe | 0/6 false GOAL | **1/6 false GOAL** | `p04_liv_fence_foil_mae` |
| `select_outcome_owner` full instrument | 48/48 | **46/48** | `p04_meg_market_foil_amy`, `t04_meg_market_foil_amy` |
| outcome-valence backward-compat | 48/48 | **46/48** | same two |

The `action_implied` 10/10 -> 9/10 and the aspectual-probe 0/6 -> 1/6 regressions were **not** named in
the dispatch brief; they are the same single root cause and were found by running checks (2) and (3),
which the original run never reached because check (1) aborts first.

Every failing item's outcome sentence contains `missed`:

- `t03`: "Kept from the gate, she **missed** her turn and was sorry."
- `t04`: "Too late at the gate, she **missed** it and was sorry."
- `t20`: "Left at the bottom alone, she **missed** her footing and was sorry."
- `p04`: "Too late at the gate, she **missed** it and was sorry."

### What the score would have been historically

Had the stemmer never been broken, **`explicit_psych` would have been 16/18 at certification time,
not 18/18** -- the two ingredients (`miss` in `PSYCH_VERBS`, `missed` in `V2_OUTCOME_UNMET`) are both
present in the `5da76bf34` tree, so the fabricated-GOAL path would have fired then exactly as it does
now. This is a strong inference from disk-verified source, NOT a re-execution: I did not check out
`5da76bf34` and re-run its harness (the organ has since gained the 2026-08-06 coverage expansion and
the Tier-2/Tier-3 similarity layers). Flagged as unverified in section 7.

## 5. Collateral, same root cause

`pytest verification/test_goal_owner_select.py test_outcome_valence_goal_congruence.py
test_goal_achievement.py test_parse_goal_extraction.py test_selection_weighted_sharded_typer.py -q`
-> **4 failed, 21 passed**.

- `test_goal_owner_select::test_full_fair_instrument_48_of_48` -- 46/48. Control-confirmed
  `missed -> mis` dependence.
- `test_outcome_valence_goal_congruence::test_backward_compat_owner_48_of_48` -- same, control-confirmed.
- `test_goal_achievement::test_mechanism_fires` / `::test_self_test_passes` -- a **different** token,
  same class. `lemma_verb("met")` was `met`, is now `meet`, so the goal-verb recurrence channel now
  actually fires: `("I wanted to meet my friend.", "I met up with my friend.")` returns
  `channel='relation:recur'` where the test pins `'majority'`. **The verdict is unchanged and correct
  (`Fulfilled`); only the channel label moved, and it moved to the more informative channel.** The
  pinned expectation was itself an artifact of `met` not lemmatising. This one is a test-expectation
  correction, not a mechanism defect.

## 6. Scoped (NOT implemented here) -- the fix and its can-fail discriminator

**Proposed fix (structural, one variable, brain-foundational).** Mirror the existing
`_goal_complement_verb_indices` guard in the opposite direction: a token that is consumed as OUTCOME
evidence in a clause must not also mint GOAL evidence for that clause's subject. Concretely, add an
OUTCOME-clause exclusion to `type_sentence_events_c3` (`hdlab/goal_typing.py:277-303`) so
`c3_has_desire`'s EXPERIENCER hit is suppressed when the same token drives `has_unmet`/`has_met`.
This is symmetric to the guard already at `:441-459`, adds no lexicon, and is not tuned to `miss`.

A second, deeper option to evaluate alongside it (they are not exclusive): make
`directed_goal_outcome_score` (`hdlab/goal_owner_select.py:137-153`) require the GOAL event to come
from a clause **other than** the outcome clause -- i.e. the evidence must be non-self-supplied. This
addresses the degeneracy directly rather than the lexical trigger, and would also catch future
same-clause GOAL/OUTCOME collisions from verbs other than `miss`.

**Explicitly rejected as a band-aid:** deleting `miss` from `PSYCH_VERBS`. It suppresses these 4 items
without touching the degeneracy, and `miss` genuinely *is* a psych verb in its other sense.

**Can-fail discriminator (pre-registerable):**

1. **Primary, with the corrected lemmatiser in force and no stemmer patching:**
   `explicit_psych` 16/18 -> **18/18**, `action_implied` 9/10 -> **10/10**, aspectual probe 1/6 ->
   **0/6**, `select_outcome_owner` 46/48 -> **48/48**. Any of these short of target = FAIL.
2. **Zero-regression:** the other 25 divergent items and all 21 currently-passing tests in the goal
   family must be **bit-identical** before/after. Any change = FAIL.
3. **Scramble must still collapse:** with the GOAL owner relabelled to the item's foil
   (`build_role_seq(..., scramble_goal_to_foil=foil)`), accuracy must still drop to the recency floor.
   If the fix restores accuracy on the scrambled bank too, it is not reading goal-ownership = FAIL.
4. **The generalisation control that separates fix from band-aid (load-bearing).** Author held-out
   items whose outcome sentence uses a *different* verb that is simultaneously an outcome word and a
   `PSYCH_VERBS` member -- e.g. `forget`/`regret`/`expect`, or `lost`/`failed`/`fell` paired with a
   psych reading. The structural fix must handle those; the lexical band-aid must **fail** them. If
   both pass or both fail, the discriminator did not discriminate and the run is void.
5. **Negative control on the scorer option:** if the `directed_goal_outcome_score` variant is taken,
   an artificial item where the GOAL genuinely *is* in the last sentence and belongs to the outcome
   entity must still be scored correctly -- the guard must exclude self-supplied evidence, not all
   last-sentence evidence.

## 7. What needs re-certifying / correcting

Locations claiming the false numbers (exact claim text quoted; nothing edited by this dispatch,
registry untouched):

| location | claim text |
|---|---|
| `data/capability_registry.jsonl` line 66, id `goal_typing_desiderative_purpose_infinitival`, field `current_best_for` | "explicit_psych GOAL-typing recovery on the recency-trap divergent subset (18/18=1.0, was 0.8889 under EXPERIENCER-frame alone) + action_implied telos-without-goal-word typing (10/10=1.0) + clean aspectual precision guard (false_goal_count=0/7 across 3 seeds, no false GOAL on began/started/tried/failed/managed/ceased/continued)." |
| `verification/verify_goal_typing.py:11` | "owner-selection accuracy must be 18/18 (1.0) across all 3 seeds" |
| `verification/verify_goal_typing.py:15` | "action_implied: same harness, N=10 divergent, must be 10/10 (1.0) across all 3 seeds" |
| `verification/verify_goal_typing.py:18-19` | "the promoted organ must fire GOAL on 0/7 items, all 3 seeds (precision guard ...)" |
| `verification/verify_goal_typing.py:87` (comment) | "(1)+(2) explicit_psych 18/18 and action_implied 10/10, off the promoted organ" |
| `verification/verify_goal_typing.py:159-160` | "[ALL CHECKS PASS] hdlab/goal_typing.py reproduces the certified end-to-end pattern (explicit_psych 18/18, action_implied 10/10, clean aspectual precision probe)." |
| `hdlab/goal_typing.py:29-31` | "VALIDATED NUMBERS this module reproduces ... explicit_psych divergent 18/18 (1.0), action_implied divergent 10/10 (1.0), aspectual-precision-probe false_goal_count=0 across 7 verbs x 3 seeds" |
| `hdlab/goal_typing.py:98-99` | "backward-compat hdlab.goal_owner_select.select_outcome_owner stays 48/48 on experiments/data/goal_owner_fair_v1.jsonl" (now 46/48) |
| `verification/test_goal_owner_select.py:85-87` | "select_outcome_owner (promoted, with tie-break) must be 48/48" |
| `notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md:156` | "c3_only 0.8889 -> partitioned **1.0 (18/18)**, t03/t12 BOTH RECOVERED" |
| `notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md:164` | "The goal-owner organ is now MEASURED END-TO-END ON REAL COREF at **18/18 explicit_psych + 10/10 action_implied**" |
| `notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md:195, :204, :208, :212` | "(owner is event-central -> 18/18)"; "the 18/18+10/10 recency-trap end-to-end is REAL"; "re-confirm recency-trap stays 18/18+10/10"; "Recency-trap HELD: explicit 18/18 (1.0) + action_implied 9/10 (0.9)" |
| `notes/drill_brain_outcome_valence_goal_congruence_2026-08-06.md:155` | "`DESIDERATIVE_PASS`, `ASPECTUAL_STOP` (18/18 + 10/10 clean HARD_PASS, commit `5da76bf34`)" |
| `notes/drill_brain_outcome_valence_goal_congruence_2026-08-06.md:308` | "structural pattern as the desiderative/aspectual partition's clean 18/18+10/10 HARD_PASS" |
| `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md:518, :726, :740` | narrative resting on the same certification (goal-owner arc) |

Checked and **NOT** in scope (different subject, same digits): `notes/capability_scorecard.md:357`,
`notes/substrate_capability_map.md` (KF-1 / real-encoder 18/18 cells), `notes/substrate_capability_map_history.md`,
`notes/research_anchor_propagate_oov_outcome_verb_valence_2026-08-06.md:268,281` (an 18/18 *eligible-subset
split* of 36 items, unrelated), all `preregs/` hits (cardinality / arms-differ counts), `tools/` atomizers,
and a sympy test fixture.

**Needs re-certifying after the fix lands:** `verify_goal_typing.py` (all 3 checks),
`verification/test_goal_owner_select.py`, `verification/test_outcome_valence_goal_congruence.py`,
`verification/test_goal_achievement.py` (expectation correction, see sec. 5), registry row 66, and the
`hdlab/goal_typing.py` docstring.

### Separate finding: the witness was never in the certification sweep

`verification/run_certification.py:21-25` runs `pytest verification/`; `pyproject.toml:59` sets
`python_files = ["test_*.py"]`. **`verify_goal_typing.py` does not match that glob and is therefore
never collected.** The 18/18 witness has to be invoked by hand. "Certification green" never covered
it. This is an independent invisibility on top of the shared-flaw one -- the check that would have
caught this was not wired into the thing that runs checks.

## 8. What I could NOT verify

- That the `5da76bf34`-era code with a correct stemmer scores exactly 16/18. Inferred from
  disk-verified source (`miss` in `PSYCH_VERBS` at that revision; the old `lemma_verb` truncation
  reproduced from that revision), NOT re-executed. The organ has changed since.
- Whether the `t20` / `p04` / `48-item` regressions have any additional cause beyond `missed`. The
  single-variable control clears all of them, which is strong but does not prove no second latent
  interaction exists among the other 20 changed lemmas.
- The `hdlab/goal_achievement.py` channel change was traced to `met -> meet` and its verdict confirmed
  correct, but I did not audit the rest of that module's pinned channel expectations for the same
  class of artifact.
- No git history exists for the working-tree lemma fix beyond commit `01093ac1f`; the current
  `hdlab/thematic_role_labeler.py` is modified-uncommitted, so these numbers are against the working
  tree, not a commit.
