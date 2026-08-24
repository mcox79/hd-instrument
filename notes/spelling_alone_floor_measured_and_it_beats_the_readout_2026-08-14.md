# The spelling-alone floor is measured, and it beats our read-out

> ## 🔴 **SUPERSEDED 2026-08-24 — THE HEADLINE AND THIS FILE'S OWN NAME ARE NOW FALSE. THE READ-OUT WINS.**
> **The `0.0870` floor below is `~78%` MORPHOLOGICAL LEAKAGE** — the WordNet gold was largely built
> from stem-sharing pairs (`nation`/`national`), which a character-trigram arm gets right while
> representing nothing. **Strip stem-sharing gold and the floor falls to `0.0195` CI
> `[0.01525, 0.024]`, while the live read-out reads `0.04575`. So the read-out BEATS the honest
> spelling floor; it lost only to the leaky one.**
> Owner ruling, board Q117: *"why not fix the bar, and re run the past results. let's do this
> right."* Re-measured IN-HARNESS by
> `experiments/exp_per_row_gain_trigram_floor_calibration_v1.py`, which proved harness identity
> first (`A1_BASE 0.04575`, `self_retrieval 0.755853`, both to 1e-9).
> ⚠️ **THIS FILE IS KEPT, NOT DELETED, AND ITS NAME IS DELIBERATELY UNCHANGED** — the measurement
> was competently done and honestly reported; the GOLD was the defect, not this work. Renaming it
> would break every citation and erase the record of what we believed. **But the name is what gets
> read in a directory listing without opening the file, so: do not cite this title as a finding.**
> ⚠️ **AND DO NOT OVER-CORRECT: `0.04575` is a weak reader in absolute terms. "Beats spelling" must
> never travel as "reads meaning well".**
> Full correction: `notes/ORGAN_MAP.md` §10.1.

2026-08-14. Cell `exp_orthographic_floor_vet_v1`. Script `tools/orthographic_floor_vet_v1.py`
(promoted out of `scratch/` because a durable result now cites it).

**Supersedes the "NOT established" verdict in
`notes/orthographic_floor_vet_and_rebaseline_2026-08-14.md` (`9ca1cffa2`).** That note was right
that the arm it examined had been misidentified. It was wrong to leave the question open in our
favour.

---

## What was measured

A "floor" is a method with no understanding in it. If a floor scores as well as the system, the
system's score is not evidence of understanding. Until today the strongest floor we could name was
word frequency ("always guess the commonest word"), at 0.0185.

The obvious stronger floor -- **compare two words by their spelling and nothing else** -- had never
been run. The arm previously described as a spelling control, `A5_STRINGCTRL`, is
`z(base) + w * z(trigram)`: our substrate score *plus* spelling. That is a decomposition of our
system, not a floor, so it could not settle the question either way.

`A6_TRIGRAM_ONLY` settles it. The arm is literally `t_mat[sel] @ tq` -- cosine between character-
trigram vectors, no substrate vector anywhere in it -- scored on the same items, the same eligible
candidate pool `sel`, and the same gold set as the base arm.

## The numbers

n = 4000 items, 5491 anchors, 5000-sample bootstrap, seed 20260819.

| arm | what it is | hit@1 | 95% CI |
|---|---|---|---|
| `A1_BASE` | our substrate read-out | **0.0480** | [0.0413, 0.0548] |
| `A6_TRIGRAM_ONLY` | character-trigram spelling, zero substrate | **0.0870** | [0.0783, 0.0960] |
| `A7_PREFIX_ONLY` | longest shared prefix, length-normalised | 0.0588 | [0.0515, 0.0660] |
| `A8_MAXORTHO` | both orthographic attacks blended | 0.0610 | [0.0537, 0.0685] |

Paired deltas against base, all with CIs excluding zero:
`A6 - BASE = +0.0390` [0.0283, 0.0500]; `A7 - BASE = +0.0108` [0.0005, 0.0205];
`A8 - BASE = +0.0130` [0.0030, 0.0230].

**Spelling alone outscores the read-out by a factor of 1.8, and the confidence intervals do not
overlap.** Even the crudest attack -- match the first few letters -- beats us.

## Why the harness is trustworthy

The metrics file records `a1_base_reproduces_c3_headline_exactly: true`, and the assertion behind
it is a hard equality: `abs(acc - 0.048) < 1e-9`. The base arm re-derived inside this cell lands on
the published C3 headline to the ninth decimal. That rules out the failure mode that has burned us
repeatedly -- comparing two arms across different runs, pools, or item sets. Same loop, same `sel`,
same gold, same items; only the scoring function differs between arms.

Item construction is recorded rather than assumed: 5491 anchors -> 4603 candidate items -> capped
at 4000, with removals itemised (404 lemma not in WordNet, 484 no gold anchor, 53 foil-direction
fallback). All 4000 have a held-out sentence.

## What the shortcut actually exploits

Read the arms' example picks and the mechanism is visible. `A6_TRIGRAM_ONLY` returns
`capability` / `capable`, `absence` / `absent`, `absorption` / `solute` -- it is finding
**morphological relatives of the target word inside the gold definition**. `A7_PREFIX_ONLY` returns
`abbey`, `able`, `abiotic`, `above`, `about` for early-alphabet targets: it is matching the target's
own first letters.

Neither has any access to meaning. Both beat us. That is a statement about the task's leakage as
much as about our system -- and it is exactly why a floor is run before a score is believed.

## What this changes

1. **The C3 orthographic floor is 0.0870, and we are below it, CI-separated.** Under the standing
   gate rule -- a gate is a CI-separated margin above `max(orthographic, frequency, scramble)` on
   the identical scorer, n, pool and gold -- C3 does not merely fail to pass. The system scores
   *worse* than a method that cannot represent meaning at all.
2. **"We underperform a spell-checker" is now established** and may be propagated. `STATUS.md`
   previously said the opposite; corrected in the same commit as this note.
3. **The 2.6x-over-frequency framing is dead.** Beating the weakest available floor is not
   evidence when a stronger floor was sitting unmeasured.
4. **It does NOT invalidate the growth machinery.** No-leak violations 0, scramble ratio 0.077,
   and bit-identical persistence round-trips measure whether grounding tracks real reading context
   rather than shuffled text. Spelling overlap cannot touch that claim. Keep the questions separate:
   whether the plumbing is sound, and whether the meanings are right, have always been different
   questions with different evidence.

## What this is NOT

**This is not a reason to wire spelling into anything.** Recorded because the instinct already
occurred once and was barred by the owner on the same day:

> "the way we lose is by trying fancy available tools. The way we win is by understanding exactly
> how the brain does it (which is NOT necessarily a trigram encoder), and replicating it as exactly
> as we can."

A floor exists to be *cleared by understanding*, not adopted. Bolting the shortcut on would raise
the number and destroy its meaning -- which is precisely how the old ">= 10%" gate came to be
retired. The correct response is the one already written into `notes/PLAN_NEXT_12H.md`: find out
how the brain separates near-identical concepts, and replicate that.

## Provenance and disclosure

Run by a subagent that hit one auto-deny and disclosed it verbatim, per the standing rule:
`Permission to use Bash with command rm -f .../scratch/ortho_floor_vet_trigram_only.py has been
denied.` No variant was retried. The consequence is benign and stated for the record: the stale
draft still sits in `scratch/`, and the promoted copy at `tools/orthographic_floor_vet_v1.py` is
the one this note cites. That agent was terminated by a weekly API usage limit before it could
write up the result or run `tools/c3_gate.py`; the metrics file survived on disk and was verified
independently in the main thread by reading the arm's scoring code directly.

**Still open:** `tools/c3_gate.py` has not been re-run against the new orthographic floor, so the
per-arm verdict deltas across all 13 arms are not yet recomputed. The headline conclusion does not
depend on it -- the base arm is below the floor with non-overlapping CIs -- but the gate's arm
table is stale until that runs.
