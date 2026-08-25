---
priority: 2
review:
review_text:
---

# PROBLEM: the meaning wins are on BORROWED scorers -- do they beat plain counting on the substrate's OWN metric, where the stage is actually broken?

## 1. THE PROBLEM IN PLAIN LANGUAGE

This week two ways of judging word meaning beat their controls: one tells true synonyms from mere
associates, one combines "reading" and "hands-on feel" for general similarity. But both were scored
on BORROWED yardsticks (a standard synonym set; a standard similarity set). The substrate's meaning
step is declared BROKEN on a DIFFERENT, home-grown yardstick -- assigning the right meaning to a word
it just read -- where plain word-counting still beats us. Nobody has checked whether the new
read-outs beat plain counting on THAT home yardstick. No number crosses yardsticks, so we do NOT yet
know whether the wins fix the thing that is actually broken.

## 2. WHY THIS ONE

Stage 2 ("decide what words mean") is the one stage that decides whether the system understands what
it read -- nine of ten others do not change that answer. We now have candidate fixes proven on
borrowed tests. This gates two things: (a) declaring stage 2 fixed, and (b) the wiring decision -- if
a read-out beats counting on our OWN metric, wire it into the live reader; if it ties or loses
counting there, we have improved a different task and must NOT claim the wall is down.

## 3. HOW THE BRAIN DOES THIS (frame + discipline, not a new mechanism)

This is a discipline check, not a new organ. The brain's semantic hub integrates modality spokes
(PINNED; Patterson, Lambon Ralph); the question is whether that integration, measured on OUR
assignment task, beats the simplest text summary (co-occurrence counting). Copy the OPERATION
(integrate spokes / apply the taught direction) exactly; do NOT import a number from another task.
This is the project's "no number crosses scorers" rule turned into an experiment.

## 4. MEASURED vs INFERRED

MEASURED: on the substrate's OWN meaning-assignment / grounding-precision metric, plain first-order
co-occurrence COUNTING scores ~0.048-0.065 and our live meaning step scores ~0.016-0.030 (counting
wins 2-3x, 3 seeds; exp_grounding_precision_gold_v1). The fusion read-out scores ~0.45 on WordSim
SIMILARITY (meaning_fusion); the taught direction scores ~0.84 on the licensed SUBSTITUTABILITY set
(distributional_meaning_channel). These are DIFFERENT scorers.
INFERRED (the open question, fair game to overturn): that the fusion read-out and/or the taught
direction beats counting on the OWN metric. Plausibly it does NOT transfer -- substitutability is
near-opposite to relatedness, and the own metric is neither.

## 5. ALREADY TRIED (do not re-run)

- The LIVE write rule vs counting on the own metric -- measured (counting wins). Do NOT re-measure the
  live rule; measure the NEW read-outs.
- The fusion / taught-direction read-outs on WordSim / substitutability -- they win THERE. Do NOT
  re-run those; the question is TRANSFER to the own metric.
Query `experiment_index.py query "grounding"`, `query "precision"`, and check the ledger first.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Read `data/exp_grounding_precision_gold_v1/` and confirm the counting floor and the live-rule number
  on the own metric, on its own population (recompute the floor there; do not paste).
- Confirm the read-outs exist and self-test: `hdlab/meaning_fusion.py`,
  `hdlab/distributional_meaning_channel.py`.

## 7. THE BAR

On the substrate's OWN meaning-assignment / grounding-precision instrument (same population and scorer
as the 0.016-0.065 numbers above): a read-out (fusion of reading+grounded, and/or the taught
direction), applied through the read-out path, must beat first-order co-occurrence COUNTING
CI-separated over that floor's UPPER bound, with an information-free twin (shuffled grounding / random
direction) LOSING. Save the scored population. HOW WE WOULD KNOW IT FAILED: it ties or loses counting
on the own metric -- then the borrowed-scorer wins do not fix the broken stage, and that is the
(valuable) result to report.

## 8. FILES AND ENTRY POINTS

- `data/exp_grounding_precision_gold_v1/` -- the own-metric instrument and the counting floor.
- `hdlab/meaning_fusion.py`, `hdlab/distributional_meaning_channel.py` -- the read-outs to score.
- Prove in `experiments/` + `verification/`; propose any hdlab wiring in `SOLVED.md` (strategy lands
  it, board Q111). Do NOT write `hdlab/`.

## DO NOT QUOTE / DO NOT REDO

- Do NOT quote the WordSim ~0.45 or the substitutability ~0.84 as if they apply to the own metric --
  different scorers, the whole point of this problem.
- Do NOT re-measure the live write rule vs counting (already done); measure the NEW read-outs.
