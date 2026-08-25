---
priority: 1
review: EXCELLENT
review_text: EXCELLENT PARTIAL. DEPTH half robustly solved (stay-until-grounded/spaced grounds +250-351 words every seed, twin loses, brain-pinned); COMPREHENSION half is an honest budget TRADEOFF (breadth vs richness; volume is the unlock). Re-verified 78/78. I DEFERRED landing the proposed read-loop changes (core behavior change, needs flag-gating).
---

> ## SOLVER REVIEW -- EXCELLENT (accepted PARTIAL, integrated by strategy 2026-08-25)
> **Why it is excellent (grading on quality, not the verdict):** it solved the DEPTH half robustly and
> brain-foundationally -- stay-until-grounded / spaced / develop-past-grounding beat the fixed schedule
> CI-separated on ALL THREE seeds (+250 / +351 / +74-163), the info-free revisit-at-random twin LOSES
> CI-separated every seed, and a RANDTARGET control (revisit a RANDOM pending word) grounds the MOST yet
> does not separate comprehension -- so the depth win is specifically about revisiting-by-grounding-STATE,
> not just revisiting. Pinned to the spacing effect / criterion learning / CLS. Rigorous where it
> mattered: SIGN-ROBUST separability (the read-out sign is transductive and flipped for one arm), a
> neighbour-richness COUNT that cannot share the AUC's sign blind spot, and a 3-seed replication that
> CORRECTED a single-seed HARD_PASS into an honest tradeoff. It volunteered what it did not establish.
> **The decisive finding:** depth and comprehension TRADE OFF at fixed reading budget -- you buy breadth
> (ground many words) OR richness (deep vectors for fewer), because a reader blind to the eval spends each
> exposure either starting a new word or deepening an old one. The unlock is reading VOLUME (the same
> lever the distributional-channel result landed on).
> **Reproduced under my check:** re-ran `verification/test_depth_grounding_revisit.py` -- WITNESS PASSED,
> 78 checks reproduce independently. DEVELOP_vs_FROZEN comprehension = +0.0495 sep / +0.0479 not-sep /
> -0.0156 not-sep (1/3), and every depth CI-separation matches.
> **Integration:** I did NOT land the proposed read-loop changes this round. They change what EVERY
> read() grounds (a core selection-policy change affecting other running sessions) and broaden
> co-occurrence tracking to ALL lemmas (a large memory increase) -- both warrant flag-gating and a
> deliberate landing, not an hourly commit, especially as the depth win does not move the wall
> (comprehension) at this budget. Recorded PROVEN-FOR-DEPTH, proposed; ready to wire when a deliberate
> read-loop update is scheduled.

# PROBLEM: the reader reads a little of everything and never reads any one thing enough times to learn it

## 1. THE PROBLEM IN PLAIN LANGUAGE

Learning a word from reading -- grounding it -- takes roughly four coherent encounters of that word.
Our reader spreads its attention across many sources and reads each one shallowly, so most words are
seen once or twice and never ground. A plain FIXED reading list beats every "smart" reader we have --
not because it is clever, but because it reads a few sources deeply enough that words repeat and
stick. **The bottleneck is DEPTH of repetition, not which source to open next.**

## 2. WHY THIS ONE

It is the upstream bottleneck that two separate results now converge on:
- `aimed_reading_is_built_and_the_reader_never_calls_it` (REFUTED 2026-08-24): every aimed reader
  loses to the fixed schedule because it spreads thin; the diagnosis is depth, not source choice.
- `the_live_meaning_organ_has_no_distributional_channel_to_be_taught_by` (SOLVED, landed 2026-08-24):
  the new meaning organ needs enough word-neighbour counts to work, and those counts come from depth.
Fixing depth unblocks both. Wiring either organ into the live loop is premature until depth lands --
depth is the lead.

## 3. HOW THE BRAIN DOES THIS (replicate the OPERATION; do not reach for the convenient tool)

**PINNED-BY-EVIDENCE.** The SPACING EFFECT / distributed practice (Ebbinghaus; Cepeda et al. 2006):
memories consolidate by REVISITING an item over time, not by seeing it once. And criterion/mastery
learning: stay with material until it is actually learned. The brain does not read a corpus once and
move on; it returns to what is not yet consolidated.
**The operation to replicate:** revisit a not-yet-grounded word until it grounds (a criterion), and/or
space its repetitions. This is a BUILD of the revisit/spacing operation -- NOT a reweighting of source
choice (refuted) and NOT a convenient scheduler picked because it is available. Mark each choice
PINNED vs OUR-INVENTION-UNDER-TEST.

## 4. MEASURED vs INFERRED

**MEASURED:** depth is the bottleneck -- ~4 coherent encounters to ground; the fixed schedule wins by
reading a few corpora deeply (2,500 sentences each) so words repeat; aimed readers ground each word
too few times (`aimed_reading` SOLVED.md, reproduced by strategy). The register bias is real but is
NOT the cause of the loss.
**INFERRED (fair game to overturn -- overturning it is a result):** that a depth fix
(stay-until-grounded / spaced repetition) will actually raise grounding AND downstream comprehension;
that coverage is even the right thing to raise (see THE BAR -- it probably is not, alone).

## 5. ALREADY TRIED (do not re-run these)

- SOURCE CHOICE (which corpus to open next) -- REFUTED in three forms (surprise, learning-progress
  target, full learning-progress currency). DO NOT re-open source choice.
- The learning-progress TARGET is INERT at this scale (ties a random target, CI spans 0).
Query first: `tools/experiment_index.py query "grounding"`, `query "spacing"`, `query "depth"`,
`query "repetition"`. Then `tools/before_you_start.py "<what you are about to do>"`.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- `.venv/Scripts/python.exe verification/test_aimed_reading_learning_progress.py` and read
  `notes/problems/aimed_reading_is_built_and_the_reader_never_calls_it/SOLVED.md` -- confirm the depth
  diagnosis and the ~4-encounter grounding criterion still hold at HEAD.
- Confirm the grounding criterion in the live loop (`hdlab/grounding_acquisition_loop.py`,
  `MIN_CONFIRM`) before you build a mechanism that targets it.

## 7. THE BAR

Beat the incumbent FIXED 4-corpus schedule (FROZEN) CI-separated over the strongest floor actually
run, with an information-free twin LOSING, on BOTH:
- (a) a grounding/DEPTH metric (words grounded per sentence read), AND
- (b) a DOWNSTREAM COMPREHENSION signal -- because a general-vocabulary COVERAGE probe structurally
  favors a general-register fixed list, and `aimed_reading`'s single biggest caveat is that coverage
  may be the wrong yardstick. A depth fix that raises coverage but not comprehension is only half an
  answer; state which you cleared.
- **Info-free twin:** revisit-at-random (same number of revisits, chosen without regard to grounding
  state). If it matches your mechanism, the revisit signal carries no information -- report that.
**How we would know it failed:** stay-until-grounded / spacing TIES FROZEN on both metrics, or the
revisit-at-random twin reproduces it.

## 8. FILES AND ENTRY POINTS

- `hdlab/substrate.py::read()` -- opens corpora in a FIXED rotated order; keep the pinned Charnov leave
  rule exactly. The gap is WHAT to revisit and WHEN to move on, tied to grounding state.
- `hdlab/grounding_acquisition_loop.py` -- the grounding criterion (~encounters to confirm).
- `hdlab/information_foraging.py` -- the forager (leave-timing), already pinned. Prove your mechanism
  in `experiments/` + `verification/`; propose the `hdlab/` change in `SOLVED.md` (the strategy session
  lands it, board Q111).

## DO NOT QUOTE / DO NOT REDO

- Do NOT quote `aimed_reading`'s coverage numbers as if they measure comprehension.
- Do NOT re-open source choice or the learning-progress target -- both are closed with evidence.
