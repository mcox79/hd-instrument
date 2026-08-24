---
review: EXCELLENT
review_text: "Witness 5/5 scaffold-free including a check named sibling_number_did_not_cross_harnesses -- it built a control for the exact trap the brief warned about, and named what it would withdraw first. Measured the floor IN-harness at 0.0195 CI [0.01525,0.024] and PROVED harness identity (A1_BASE 0.04575, self_retrieval 0.755853 to 1e-9) before accepting a value that coincides with the sibling. All three hunks landed. It also disproved my brief: the two harnesses are the SAME population (n_items=4000/n_anchors=5491), which I asserted otherwise without checking. Headline: on the honest floor the read-out WINS 0.04575 vs 0.0195, where on the leaky floor it lost."
---

# PROBLEM: one of our two pass/fail gates cannot measure its own floor, so it now refuses to grade anything

## THE PROBLEM IN PLAIN LANGUAGE

When we claim our system understood something, we check it against a deliberately stupid baseline
that only compares spelling. If a spell-checker can do it, we have not shown understanding. That
spelling baseline is the single number most of our recent work is graded against.

It turned out to be unfair. The answer key was largely built from pairs that share a word stem --
"nation" and "national" -- and a system that only compares spelling gets those right while knowing
nothing. Strip the stem-sharing pairs out and the spelling baseline collapses to about a fifth of
its old score, which is no better than random noise.

The owner ruled on this (board Q117): *"why not fix the bar, and re run the past results. let's do
this right."*

**We have two tools that grade against that baseline. One was fixed. One cannot fix itself.**

The tool that was fixed owns its own copy of the spelling baseline, so it simply re-measured it on
the cleaned-up answer key and carried on. The second tool never had one -- it only ever borrowed the
number. So it now has no honest floor to grade against, and rather than grade against a number known
to be wrong, it **stops and refuses to issue a verdict**.

**Your job is to give it the ability to measure its own floor, and then re-grade the past results
against it.**

The tempting shortcut is to paste the first tool's new number into the second one. **That is wrong
and it is the main thing to avoid.** The two tools build their test items differently and score them
differently, so a floor measured in one is not the floor of the other. A number that is right in one
place and wrong in another is worse than a missing number, because it looks finished.

## WHY THIS ONE

This blocks grading. Until it is done, one of the two gates produces no verdict at all, and the
results that were previously graded through it carry a grade computed against a baseline we now know
was inflated by roughly a factor of four. Every claim that leaned on it is unresolved -- not wrong,
**unknown**, which is worse to leave sitting.

It is also the second half of a direct owner instruction that is currently half-done. The first half
(fix the bar in the tool that could fix itself) landed 2026-08-24. This is the rest of it.

## MEASURED vs INFERRED

**MEASURED:**
- The spelling floor falls `0.0867 -> 0.0193` when stem-sharing pairs are removed from the gold, and
  the stripped floor's CI `[0.0153,0.0238]` **overlaps its own information-free shuffled twin**
  `[0.0135,0.0213]`. So the stripped floor is not distinguishable from noise.
  Source: `data/exp_c3_surprise_weighted_vs_bundling_v1/metrics.json`, run_mode full, n=4000.
- `tools/score_space_gain_and_topk_ci_v1.py` re-measured its OWN floor in its OWN harness on
  stripped gold and reads `0.019500` CI `[0.015250, 0.024000]`, n_items=4000 / n_anchors=5491.
- `tools/per_row_gain_c3_vet_v1.py` has **no `A6_TRIGRAM_ONLY` arm**. Verified by reading the file:
  the only occurrences of `ORTHO_BAR` are the constant, the gate comparison, and a field it copies
  into `metrics.json`. It never computed the floor.
- That tool now refuses to gate. Confirmed by running `--smoke`: it prints
  `[BAR NOT CALIBRATED FOR THIS GOLD -- NO GATE VERDICT ISSUED]` and returns 3.
- Nothing imports or invokes `per_row_gain_c3_vet_v1.py`. Enumerated by grepping
  `tools/ experiments/ verification/ hdlab/`; all hits are docstrings citing its `metrics.json`.
- `hdlab/char_trigram_encoder.py` exists and is promoted -- you should not need to write a trigram
  encoder from scratch.

**INFERRED, NOT MEASURED -- check these yourself, do not take them from me:**
- I have **not** measured what the trigram floor reads in `per_row_gain`'s harness. It could land
  near `0.0195` or nowhere near it; the whole point of this brief is that I do not know.
- I have **not** verified that `exp_coherence_final_pick_transfer_v1.py`'s `A6_TRIGRAM_ONLY`
  construction is the right one to copy. It is the nearest implementation I found, not a vetted
  choice.
- I have **not** determined how many past results need re-grading. "Re run the past results" is the
  owner's instruction; scoping it is part of this job.

## ALREADY TRIED

- **Lowering the constant on my own analysis -- deliberately NOT done, twice.** A gate is never
  weakened by the session whose results it constrains. It was filed to the owner as Q117 and left
  untouched until they ruled. Do not treat the ruling as licence to pick a convenient number; it is
  licence to **measure** an honest one.
- **Fixing the sibling tool -- DONE, landed 2026-08-24.** `USE_MORPH_STRIPPED_GOLD = True`, gold
  stripped via `hdlab/morphology_leakage.py`, floor re-measured in-harness. Read that file first;
  it is the worked example of what this brief asks for, including the `void_plumbing` guard that
  recomputes the floor and requires it to equal the constant exactly.
- **Copying `0.019500` across -- considered and rejected.** No number crosses scorers or
  populations. The refusal message in the code says so explicitly so nobody undoes it by accident.
- **A morphology check already exists and is promoted:** `hdlab/morphology_leakage.py`
  (`shares_stem` / `strip_gold`), self-tested both ways -- it catches `nation/national` and does NOT
  catch `car/automobile`. Reuse it; do not write a second stemmer.

## VERIFY BEFORE YOU START

Numbers go stale here within hours. Re-establish these before relying on them:

1. `python tools/per_row_gain_c3_vet_v1.py --smoke` -- confirm it still refuses and returns 3.
2. Read `tools/score_space_gain_and_topk_ci_v1.py` lines 58-90 for the worked fix and the reasoning.
3. `python -c "from hdlab.morphology_leakage import strip_gold, shares_stem; print(shares_stem('nation','national'), shares_stem('car','automobile'))"` -- expect `True False`.
4. Check whether `data/exp_per_row_gain_c3_vet_v1/metrics.json` still carries the old `0.0870` in its
   `bar` field. If so, that recorded verdict is one of the "past results" in scope.

## THE BAR

**A clear, well-controlled failure is an explicit PASS for this brief.** If the honest floor turns
out to be so noisy that this gate cannot separate anything, say that and show it -- that is a real
answer and it changes what we build next.

To succeed:

1. `per_row_gain_c3_vet_v1.py` measures its floor **in its own harness, on its own items, against
   its own stripped gold**, and gates on what it measures.
2. A guard that **recomputes the floor and refuses if it disagrees with the constant**, mirroring
   the sibling's `void_plumbing`. A constant nobody re-derives drifts silently.
3. **A positive control on the guard: make it fire.** Set the constant wrong on purpose, show the
   refusal, restore. A guard nobody has seen fire is untested.
4. **An information-free twin of the trigram arm**, scored the same way. If the floor cannot be
   separated from its own shuffled version, report that -- it is the most important thing you could
   find, and it is what the stripped floor already did once.
5. The past results re-graded against the honest floor, with **both numbers reported side by side**
   (old leaky grade, new honest grade). Do not quietly replace one with the other.
6. Report the CI half-width and the null p95 beside every margin. A width is not an effect.

**If your first approach is refuted, do not stop at "refuted."** Work the problem a different way
and solve it -- a refutation plus a working alternative is worth far more than a refutation alone.
Say plainly which parts you measured and which you inferred.

**Ask which brain structure this corresponds to, and whether we are replicating it or substituting
something convenient.** A grading floor is measurement hygiene rather than a brain mechanism, so the
honest answer here may be "neither, this is bookkeeping" -- say so rather than inventing a
neuroscience justification. But the thing being graded (retrieving a word's meaning from a
distributed representation) very much is a brain question, and if the honest floor changes what that
readout looks like, that is the finding.

## FILES AND ENTRY POINTS

| path | what it is |
|---|---|
| `tools/per_row_gain_c3_vet_v1.py` | **the tool to fix.** Q117 block at the top; refusal at the gate |
| `tools/score_space_gain_and_topk_ci_v1.py` | **the worked example.** Already fixed; lines 58-90 |
| `hdlab/morphology_leakage.py` | `shares_stem` / `strip_gold`, promoted and self-tested |
| `hdlab/char_trigram_encoder.py` | promoted trigram encoder -- reuse, do not rewrite |
| `experiments/exp_coherence_final_pick_transfer_v1.py` | an `A6_TRIGRAM_ONLY` construction, lines 168-201 (nearest example, NOT vetted) |
| `experiments/exp_grounding_readout_known_answer_v1.py` | `C3` -- builds corpus/buckets/space/items/gold |
| `data/exp_per_row_gain_c3_vet_v1/metrics.json` | the recorded verdict carrying the old bar |
| `verification/test_removing_the_bundle_helps_it_just_does_not_help_enough.py` | the existing witness |

**Constraints.** Never edit `preregs/**` or any `arm_key*` file -- harness-denied deliberately. If
the only move left is to weaken a gate, stop and say so rather than doing it. Never bundle a
deletion (`rm`) with real work in one call: it is auto-denied and it destroys the bundled work too.

**If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
and do not silently proceed without the denied step.** A dropped precondition invalidates the
declared gate even when the result may be fine -- that is not yours to judge silently. Disclose it.

## DO NOT QUOTE

- **`A5_STRINGCTRL = 0.0870`** -- never quote this as "what a spell-checker scores". It is ~78%
  morphological leakage. Stem-stripped it falls to `0.0193` and overlaps its own info-free twin.
- **`0.019500`** -- belongs to `score_space_gain_and_topk_ci_v1.py`'s harness only. Do not carry it
  into `per_row_gain`, and do not quote it as "the spelling floor" without naming the harness.
- **`0.048`** (the C3 headline) -- computed on **unstripped** gold. It is not comparable to anything
  measured on stripped gold, and the cross-check that asserted it is now correctly disabled when
  stripping is on.
- **The smoke arm numbers I printed while testing the refusal** (`A1_BASE 0.055000` etc.) -- n=200
  smoke, not a result, not a verdict. Do not cite them.
- Do not quote any margin without its CI half-width and the null p95 beside it.
