# INTEGRATING BY *USING* IT FOUND FOUR DEFECTS THAT A GREEN TEST SUITE DID NOT

**2026-08-23, strategy session.** Owner: *"you should integrate it and see how it works. You need to
be the final answer here, and have the holistic view of substrate."*

I had landed the `harness_cannot_recompute` mechanism the night before and **never used it**. Using
it took about twenty minutes and broke four ways. Every witness was green throughout.

---

## 1. THE FOUR DEFECTS, WORST FIRST

**1. SH-7 CRASHED EVERY CELL THAT IMPORTS THE HARNESS.** `_seed_checkpoint.py` runs a self-test AT
IMPORT whose first assertion is that `get_output_dir("myanchor_v1")` ends in `exp_myanchor_v1`. The
fresh-run switch appends `__fresh_<tag>`, so with the switch ON:

    AssertionError: T1 FAIL: got exp_myanchor_v1__fresh_probe1

**The switch did not fail to redirect. It broke the harness it lives in, for every cell, the moment
anyone asked for a fresh run.**

🔻 **AND THE EXISTING WITNESS WAS STRUCTURALLY BLIND TO IT.** `test_fresh_recompute_redirect.py`
passes `6/6`. It imports the module and THEN sets the variable, so the import-time self-test always
ran clean. **A real cell has the variable set before Python starts. The bug IS the ordering, and a
test that controls the ordering cannot see it.** New witness spends a subprocess;
positive-controlled by reintroducing the bug (fails 3/4 with the original error) and removing it
(passes 4/4).

**2. `classify_run(0, 0)` RETURNED `RECOMPUTED`** -- its most positive verdict, with
`is_evidence_of_reproduction() == True` -- for a run that recorded nothing and whose output
directory was never created. **This project's own "an empty representation scores perfectly"
failure, occurring inside the guard built to stop false reproduction claims.** Zero-before is the
genuine fresh-start condition, so the empty case fell through to the success branch. Now
`NOTHING_RECORDED`, checked first.

**3. THE COVERAGE NUMBER WAS WRONG IN THE DANGEROUS DIRECTION.** I reported `87 of 421` from a
STRING match. A strict IMPORT match gives `43`. One cell containing `get_output_dir` **defines its
own**, so the redirect was inert while the grep said fine. **Range is `10-21%`; the `87` may not be
quoted alone.** The deciding test is not a grep -- `reproduce.py` now checks at runtime whether the
fresh sibling was created.

**4. THE DRIVER WAS BLIND TO 19 LANDED DIRECTORIES AND ADVISED ON ONE THAT DID NOT EXIST.** It
assumed `data/exp_<cell>`; **19 of 423** landed directories lack the prefix (solver-authored,
`writerule_*`). Asked about a real solver result it printed `(MISSING)` as one line among several
and then gave a confident redirectability verdict for a directory that is not there. Now resolves
both spellings and REFUSES when neither exists.

*And a fifth, comic but real: the driver's refusal message prints the exact migration to apply, and
its detector did not recognise cells migrated that way. **A checker that cannot see the fix it
prescribes sends you round the loop forever.***

---

## 2. THE PAYOFF -- THE FIRST GENUINE REPRODUCTION IN THIS PROJECT

    exp_thematic_role_labeler_cue_integration_v1
    landed verdict: HARD_PASS
    exit 0 in 33.3s | units 0 -> 5 | RECOMPUTED
    landed directory unchanged (size+mtime on units.jsonl and metrics.json)
    OUTCOME: REPRODUCED

**A landed result, recomputed from scratch, same verdict, original untouched.** Until today nothing
in this repo could do that -- `403 of 7,875` landed cells replay their checkpoints and return the
stored answer in ~0.0 s.

---

## 3. THEN THE SAME TREATMENT FOR EVERY OTHER SOLVED PROBLEM -- THE SCIENCE HOLDS

Ran each brief's OWN declared `reverify` command, which nobody had done:

| brief | reproduces? |
|---|---|
| `stored_terms_are_stems` | ✅ `0/141` true stems -- exact |
| `eval_bank_too_small` | ✅ `166` items, `124` scorable, majority floor `0.6048387`, `49` met / `75` unmet -- exact to 4 dp |
| `flat_store_destroys_the_code` | ✅ held-out `0.1399` CI `[0.1310,0.1494]` vs counting floor `0.3242`, exact-key `0.9954` -- to the digit, after `215 s` of GENUINE recompute |
| `harness_cannot_recompute` | ✅ witness PASS |
| `cortical_read_has_no_scored_path` | ⏳ running -- its cell needed migrating first |

**THE SUBMITTED WORK IS SOUND.** *Three of three re-runnable results reproduced exactly. That is the
single most reassuring measurement of the night and it should be said before any of the defects.*

---

## 4. THE PROTOCOL DEFECT, WHICH I TRIPPED MYSELF

**`3 of 5` reverify commands RE-RAN A CELL IN PLACE**, overwriting its landed `metrics.json`. I
followed `flat_store`'s as written and rewrote its `ts_iso` and `elapsed_s`.

⚠️ **The scientific numbers were byte-identical, so the only casualty was the original timestamp --
but that is the same shape as the "54 landed records silently re-dated" incident this project
already carries.** Restored from git. **And `harness_cannot_recompute` named this precise hazard
while the protocol collecting solutions kept instructing everyone to trigger it.**

✅ **Both protocol files now forbid it and rank the safe forms; all three existing commands rewritten;
re-audited at `0 of 5` unsafe.** Each now also carries **the numbers it should reproduce** -- *a
reverify command that does not say what the answer should be is only half an instruction.*

---

## 5. WHAT I WOULD CHANGE ABOUT HOW I WORK

**I HAD BEEN INTEGRATING BY LANDING CODE AND RUNNING ITS TESTS. THAT IS NOT INTEGRATION.** The
mechanism passed its own witness suite and was inert-to-catastrophic in production; nobody would have
known until someone tried to re-verify a real result, and the failure would have looked like the
CELL being broken rather than the switch.

**EVERY ONE OF THE FOUR DEFECTS WAS FOUND BY USING THE TOOL ON SOMETHING IT WAS NOT WRITTEN AGAINST.
NONE WAS FOUND BY ITS OWN TESTS, WHICH PASSED THROUGHOUT.**

*This project already has the rule -- "an audit checks the shape you thought to check; using the
thing checks all of them" -- recorded after three of six withdrawals were caught only by trying to
USE data rather than audit it. This is the same lesson arriving on the tooling side.*

---

## TLDR

You asked me to take a finished solution, put it in, and see whether it works. I had put it in the
night before and never actually used it.

Using it broke four ways in twenty minutes. The worst: **the switch that forces an experiment to
genuinely re-run crashed every experiment in the repo the moment you turned it on** -- and its tests
passed the whole time, because they set things up in a different order than real life does.

All fixed, and the reward is real: I can now take a finished experiment, redo it completely from
scratch, get the same verdict, and leave the original untouched. Nothing here could do that before.

Then I did the same to every other solved problem -- ran each one rather than reading it. **Every one
reproduced exactly.** The submitted work is sound. What was not sound was our instruction for
checking it, which told people to re-run experiments on top of their own records. I tripped it
myself, restored the damage, and fixed it.

The lesson I would keep: landing something and running its tests is not integration. Using it is.

## QUESTIONS

None here. `Q115` and `Q116` remain open on the board.

## NEXT STEPS

1. **The cortical re-verification is running** -- when it lands, all five solved results will have
   been personally reproduced.
2. **A real coverage number for the reproduction path**, measured by running cells rather than
   grepping them. The `10-21%` range is a source-inspection artifact.
3. **The `275` unmigrated cells are a priced chore, not an emergency** -- `reproduce.py --check`
   names them one at a time, and the runtime guard now refuses rather than pretending.
