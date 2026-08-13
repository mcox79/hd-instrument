# Shared-flaw invisibility: when the checker shares a defect with the thing it checks

2026-08-13. Cross-cutting pattern, recorded because it produced **three independent false-clean
results in a single night**, each found by a different investigation, each verified on disk.

---

## The rule

> **When a checker shares a flaw with the thing it checks, the flaw is invisible and everything looks
> consistent.**

Consistency is not evidence. Two components that share a defect *agree* -- and agreement is exactly
the signal we read as "verified". The failure is silent by construction: there is no error, no
disagreement, no anomaly to notice. It only becomes visible when one of the two sides is changed,
at which point the previously-clean system appears to *regress* -- which is the moment the pattern is
most likely to be misread as "the fix broke it" and reverted.

The three instances below are the same shape at three different layers of the stack.

**Addendum (added after first writing).** Everything above and through instance 3 was written at
02:10, 23 minutes before `notes/uncollected_witness_audit_2026-08-13.md` landed at 02:33. That audit
produced a **fourth** instance -- recorded below as instance 4 -- which is the most consequential of
the four, and two further practices (P5, P6). The counts "three" above are left as written; read them
as "three at first writing".

---

## Instance 1 -- Propose and verify share one metric

Source: `notes/brain_fidelity_audit_readout_2026-08-13.md` (sections at `:26-57`).

`propose_fn` and `verify_fn` are both `canonicalize_fast`. The proposal
(`:684-688`) returns the cosine-argmax winner over bags of nearby content words; the verification
(`:690-694`) re-runs the *identical cosine argmax* on a fresh encounter and checks
`encounter_best == hypothesis.obj`. The audit's own words: "Every step that decides *what a word
means* ... routes through one function, `canonicalize_fast`, whose decision variable is cosine
similarity between two bags-of-nearby-content-words." The PBV machinery layered on top
(`pbv_update_strength :218-226`, abandon-and-repropose `:306-321`) and the field-relative z-score
(`_readout_statistic :46-49`) rescale the *same cosine array*; "neither changes what the decision
variable is."

**Consequence:** any systematic bias in the cosine-over-bag-of-words metric is *structurally
undetectable by the verification step*. Verification can only ever confirm that the metric agrees
with itself. A hypothesis that is wrong because the metric is wrong verifies at exactly the same rate
as a hypothesis that is right.

## Instance 2 -- Store and classifier share one stemmer

Source: `notes/measurement_layer_drift_2026-08-13.md` (`:127-136`).

The foundation store's object strings were minted by the OLD `lemma_verb` (`called -> cal`,
`apples -> appl`, `babies -> babi`, `apparatus -> apparatu`, `alleles -> allel`). The closed-class
lookup table used to *classify* those objects was built with the same stemmer, so both sides landed on
the same key: the store's `appl` found a table entry for `appl`. Everything matched. Roughly 10% of
the store was literal non-words and this was invisible for as long as both sides were corrupt
identically.

The corruption only became visible when **one side** was fixed: the new lemmatiser produces
`apples -> apple`, so the keys `appl` / `babi` / `apparatu` / `allel` / `cal` ceased to exist in the
table, while the store's object is still `appl` and stays `appl` under re-normalisation. The audit's
framing (`:130-136`) is exactly the pattern: matching keys proved nothing about correctness, only
about shared provenance.

## Instance 3 -- Certification and code share one bug

Source: this night's `notes/false_certification_goal_typing_2026-08-13.md`.

`verification/verify_goal_typing.py` asserted `explicit_psych` 18/18, `action_implied` 10/10, and a
clean 0/6 aspectual precision guard. It passed only because `lemma_verb("missed")` returned the
non-word `mis`. `miss` is in `PSYCH_VERBS` (`hdlab/thematic_role_labeler.py:68`) and `missed`/`miss`
are in `V2_OUTCOME_UNMET` (`hdlab/goal_typing.py:192-194`) -- both true at the certification commit
`5da76bf34` -- so the outcome clause was always going to mint a spurious GOAL bound to the candidate's
own outcome entity, degenerating `directed_goal_outcome_score` to a constant 1.0. The truncation was
the only thing keeping the two lexicons apart.

Single-variable control, recomputed today: restoring **only** `missed -> mis` returns 18/18, 10/10,
0/6, and 48/48 across four separate certifications. True values with the corrected stemmer: **16/18,
9/10, 1/6 false GOAL, 46/48**.

An additional invisibility sat on top: `run_certification.py:21-25` runs `pytest verification/` and
`pyproject.toml:59` sets `python_files = ["test_*.py"]`, so `verify_goal_typing.py` was **never
collected by the certification sweep at all**. The witness that would have caught this was not wired
into the thing that runs witnesses.

## Instance 4 -- The test suite and its witnesses share a naming blind spot

Source: `notes/uncollected_witness_audit_2026-08-13.md` (confirmed on disk; sections `:6-41`,
`:60-103`, `:217-262`).

This is the same shape one level up: not a shared normaliser and not a shared decision variable, but
a shared **convention**. The collector believes a witness is named `test_*`; 27 witness files are
named `verify_*` / `witness_*`. Neither side is wrong on its own terms, and because neither side ever
disagrees with the other, the gate reports success by never looking.

`pyproject.toml:57-59` sets `testpaths = ["verification"]` and `python_files = ["test_*.py"]`;
`verification/run_certification.py:23` shells plain `pytest verification/` with no `--override-ini`
and no alternate config path, so certification inherits that glob verbatim. No competing config
exists -- no `conftest.py`, `pytest.ini`, `setup.cfg`, or `tox.ini` anywhere outside `.venv/`.

**Consequence: 27 witnesses (25 `verify_*.py` + 2 `witness_*.py`) were NEVER collected, at any
commit, ever.** `git show 721e4215c:pyproject.toml` -- the initial scaffold, 2026-05-16 -- already
carries the glob, and it has not changed since; the glob predates every `verify_*.py` file in the
repo. The receipt is on disk: `data/certification.md` (exit 0, "260 passed, 3 skipped") contains
**zero** occurrences of the string `verify_`. **9 of the 27 fail when finally run directly.**

**And the obvious fix reproduces the pattern.** Widening the glob to `["test_*.py", "verify_*.py"]`
collects +53 tests from exactly **9 files -- all of which already pass**. The other 18 expose *zero*
pytest-collectable items, because their real work sits behind `if __name__ == "__main__":`, which
pytest never executes -- and **all 9 of the failures are in that zero-item group**. The split is
exact, with no overlap. The repair would make the suite **greener** while executing none of the real
failures: a second false-green, generated by fixing the first. That is the pattern eating its own
remedy, and it is the reason this instance is the most consequential of the four -- the shared flaw
had shaped what "fixing it" even looks like.

The real repair does not widen a pattern, it runs the code:
`verification/test_all_witnesses_exit_clean.py` -- named `test_*` so it *is* collected, discovers
witnesses at runtime by glob, runs each as a **subprocess**, and asserts exit code 0, with one
parametrized test id per witness so a red result names *which* witness broke. It carries a
self-check (`test_discovery_is_not_vacuous`) asserting discovery `>= 25`, so a future rename or
directory move cannot silently discover zero and pass vacuously -- i.e. it refuses to re-enter the
failure mode it was written to remove.

One compounding detail, worth stating because it is easy to file this whole instance under "config
bug": certification was **already red on a *collected* test** before any config change --
`verification/test_goal_owner_select.py::test_full_fair_instrument_48_of_48` (`select_outcome_owner`
48/48 -> 46/48). The CLAUDE.md invariant "`python verification/run_certification.py` must pass on
`main`" was violated independently of the glob; the newest certification report on disk
(2026-08-12T01:01:20, exit 0) is simply stale with respect to it.

---

## What the three have in common

| | shared component | what it made invisible | what exposed it |
|---|---|---|---|
| 1 | `canonicalize_fast` cosine metric | systematic metric bias | nothing yet -- still open |
| 2 | `lemma_verb` stemmer | ~10% non-word store objects | fixing **one** side |
| 3 | `lemma_verb` stemmer | a degenerate goal-owner scorer | fixing **one** side |
| 4 | the `test_*` naming convention | 27 never-executed witnesses, 9 of them red | running them **outside** the collector |

Instances 2 and 3 share a literal component (`lemma_verb`), which is itself the point: **one shared
primitive can silently certify unrelated subsystems.** Instance 1 shows the same shape with no shared
code at all -- only a shared *decision variable*. The pattern is about shared flaws, not shared
imports.

Instance 4 extends the range further still: what is shared there is neither code nor a decision
variable but a **naming convention** -- and the "exposure" column is the tell. Instances 2 and 3 were
exposed by fixing one side; instance 1 is still unexposed; instance 4 was exposed only by running the
witnesses *outside* the collector entirely. Nothing internal to the suite could have surfaced it,
because inside the suite there was never a disagreement to notice -- only an empty set that nobody
counted. The escalation across the four is: shared function -> shared metric -> shared convention,
with the invisibility identical at every level.

Note also that the fix's own gold set is the counter-example that proves the rule: the lemma-fix gold
set of 26,868 verb-inflection pairs was built **independently of morphy**, which is precisely why it
could measure the fix (53.50% -> 99.03%). A gold set built with morphy would have scored the broken
stemmer and the fixed one against a ruler that shared their bias, and would have shown a much smaller
and uninterpretable delta.

---

## Concrete, checkable practices derived from this

### P1 -- Verification must use an independently-sourced instrument

A check is only informative to the extent its decision path is disjoint from the thing checked.
Before landing a witness, write down the components it shares with the organ under test. If
`propose_fn` and `verify_fn` resolve to the same function (instance 1), or if the store and the
classifier were built by the same normaliser (instance 2), the witness measures agreement, not
correctness.

*Checkable form:* every `verification/` witness carries an explicit **SHARED-COMPONENT DECLARATION**
naming the modules/primitives it shares with the organ, and an argument for why the shared parts
cannot manufacture the result. Zero-shared-component is the target; a non-empty list is a caveat that
must appear next to the number, not in a footnote. Mechanically greppable: if the witness's import
set intersects the organ's import set on a *decision-making* primitive (a normaliser, a similarity
function, a lexicon), that intersection must be named.

### P2 -- A gold set must be built without the component under test

The lemma fix could be measured because its gold was independent of morphy. The goal-typing
certification could not be measured because its "gold" (the assertion `acc == 1.0`) was a value
recorded from a run of the very code being certified.

*Checkable form:* a certified number must be traceable to an **externally-sourced ground truth**
(hand-scored, published corpus, independent tool) -- never to "what this code printed the day it
landed". A witness whose expected value was harvested from its own subject is a **regression pin**,
not a certification, and must be labelled as such. Note the second-order case in instance 3: the
`test_goal_achievement` expectation `channel == 'majority'` was itself an artifact of `met` not
lemmatising; the verdict was always correct and only the pinned channel label was wrong. Regression
pins are useful -- they must simply not be counted as evidence of correctness.

### P3 -- Measurement scripts must be versioned and committed

Two audits run the same night over the same store with the same ruler disagreed:
proper-noun 265 vs 270, union 384 vs 389, unclassified 821 vs 816
(`notes/measurement_layer_drift_2026-08-13.md:93, :98-99` -- "Same ruler, same store, different
throwaway scripts"; and per `:93` **neither original script survives**). The five-fact discrepancy is
small and none of the headline claims moved, but the discrepancy is *unresolvable* because the
instruments are gone.

*Checkable form:* any script that produces a number that enters a note, a registry row, or a verdict
is committed to the repo under a stable path, and the number is reported with the script path plus
commit hash. Throwaway `-c` one-liners are fine for exploration and **never** for a number that gets
written down. A number whose instrument cannot be re-run is not reproducible, and two such numbers
cannot be reconciled -- only re-derived from scratch.

### P4 (corollary) -- A "regression" caused by fixing one side is the finding, not the bug

Instances 2 and 3 both surfaced as apparent regressions the moment one side was corrected. The
reflex to revert the fix and restore the green number is exactly wrong: it restores the shared flaw
and re-hides the defect.

*Checkable form:* when a landed fix breaks a certification, the required first step is a
**single-variable control** -- restore *only* the specific old behaviour and confirm the check passes
again. If it does, the burden of proof flips: the certification is presumed to have depended on the
defect until shown otherwise, and the correct action is to re-baseline the certification, not revert
the fix. (This is what was done for instance 3 and is why the ruling was "the 18/18 was never real",
not "the lemma fix regressed goal typing".)

### P5 -- A check must be demonstrated able to FAIL

A check that has never been observed failing may be **inert**, and an inert check is
indistinguishable from a passing one -- from the outside both emit "OK". Instance 4 is the extreme
case: 27 witnesses "passed" for months by never running at all. The absence of a red result is not
evidence; it is the same absence you get from a check that is not wired up.

*Checkable form:* before a check is trusted, it must be shown to go red on a case that *should* be
red. The registry witness-citation check added tonight
(`check_registry_witnesses` in `tools/capability_registry_audit.py:919+`, `witness_missing` /
`witness_not_collected` / `witness_failing` / `witness_status_unknown`) was proven can-fail by
feeding it a synthetic registry row citing a known-failing witness: it yielded 1 entry and exited
`rc=1`. Record that demonstration next to the check. A check landed green with no can-fail
demonstration is an assertion about the author's intent, not about the system. (The can-fail run is
reported by the agent that landed the check; it was not re-executed here -- measurement freeze. The
check's code path was confirmed present on disk.)

### P6 -- Prefer a driver that asserts an exit code over a collection pattern that assumes discovery

A discovery rule -- a glob, a naming convention, an auto-registry scan -- can silently match nothing,
or match only the healthy subset, and still report success. Instance 4 is both failures in sequence:
the original glob matched none of the 27, and the near-miss repair would have matched exactly the 9
that were already passing. An explicit per-item runner cannot do either: it enumerates, it executes,
and it asserts a status per item, so "found nothing" and "everything is fine" stop being the same
output.

*Checkable form:* where a gate depends on discovery, the discovery itself must be asserted
(`test_discovery_is_not_vacuous`: `len(WITNESSES) >= 25`), and each discovered item must produce its
own pass/fail id rather than folding into an aggregate. Prefer "run it and check `returncode == 0`"
over "trust that the collector picked it up". If a gate cannot say *how many* things it checked, it
cannot distinguish zero from all.

---

## Not the same failure mode as measurement-layer drift

To keep the two 2026-08-13 pattern notes from being conflated:
**a shared flaw HIDES a real error -- everything looks consistent, and the result is a *false green*;
a measurement racing a concurrent edit produces a result that describes NO single state of the repo,
and the result is an *incoherent green*.** In the first, the number is well-defined and wrong; in the
second, the number is not well-defined at all (`notes/measurement_layer_drift_2026-08-13.md`
sec. 8, esp. `:288-295`).

*Cross-link status:* one-way from here. The drift note's `:288-295` already states this distinction
and already names this file, so the link is effectively bidirectional in content -- but its
parenthetical at `:294-295` ("As of this writing `notes/shared_flaw_invisibility_2026-08-13.md` does
not exist on disk") is now **stale**: this file does exist. That parenthetical was deliberately left
uncorrected, because a concurrent agent may hold that file open and an edit there risks exactly the
racing-write class the note itself documents. Correcting it is a one-line follow-up for whoever owns
that file next.

---

## Sources (all verified on disk this session)

- `notes/brain_fidelity_audit_readout_2026-08-13.md` -- propose/verify share `canonicalize_fast`.
- `notes/measurement_layer_drift_2026-08-13.md` -- store and closed-class table share `lemma_verb`;
  also the 265/384/821 vs 270/389/816 unversioned-audit disagreement.
- `notes/false_certification_goal_typing_2026-08-13.md` -- `verify_goal_typing` 18/18 depended on
  `missed -> mis`; single-variable control; true scores 16/18, 9/10, 1/6, 46/48.
- `notes/uncollected_witness_audit_2026-08-13.md` -- `python_files = ["test_*.py"]` since the
  2026-05-16 scaffold; 27 witnesses never collected, 9 failing; widening the glob adds 53 tests from
  the 9 already-passing files and executes none of the 9 failures; certification already red on the
  collected `test_goal_owner_select.py::test_full_fair_instrument_48_of_48`.

Also confirmed directly on disk this session (read-only, no execution): `pyproject.toml:57-59`
(`testpaths`/`python_files` exactly as quoted), `verification/run_certification.py:23` (plain
`pytest verification/`), `verification/test_all_witnesses_exit_clean.py` (subprocess driver,
`MIN_EXPECTED_WITNESSES = 25`, per-witness parametrized ids), and the witness-citation section of
`tools/capability_registry_audit.py`.
