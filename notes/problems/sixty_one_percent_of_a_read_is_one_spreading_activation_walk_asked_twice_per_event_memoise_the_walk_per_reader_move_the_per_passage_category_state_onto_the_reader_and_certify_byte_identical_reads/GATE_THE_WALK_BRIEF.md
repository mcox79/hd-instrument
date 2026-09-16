# BRIEF-READY TEXT (from pri 146, phase 7B) — GATE THE SPREADING-ACTIVATION WALK: IT ONLY MATTERS WHEN THE RESTING LEVEL DOES NOT ALREADY DECIDE

> **PROBLEM: the graph walk that costs 61% of a read is one term beside the verb's sense-frequency resting
> level, and on 89% of the occasions it runs it cannot change the answer that level already gives — the brain
> does not recruit context for a sense whose base rate has already won.**

## THE MEASUREMENT THAT SIZES IT (pri 146, `experiments/exp_ppr_memo_v1.py --consumers --docs 12`, `data/exp_ppr_memo_v1/consumers.json`)

12 GUM **TEST** documents, 12 genres, 817 sentences, 1,753 events.

| the chain | count | share |
|---|---|---|
| walks entering the blend `argmax[ log P_freq + lam·log PPR ]` (`grounded_semantic_graph.py:248`) | **844** | — |
| …on which the walk **overturns the frequency argmax** | **91** | **10.8%** (0–21.6% per document) |
| sense verdicts `(sign, affecting)` that move when every walk is permuted | 25 / 841 | 3.0% |
| `sense_posterior_in_context` argmaxes that move | 363 / 864 | **42.0%** |
| **recorded affect fields that move** | **5 / 1,753** | **0.29%** |

**THE GATE, SIZED ON THE SAME RUN.** The barrier a walk must overcome is
`log(pf_top1) − log(pf_top2)` on the normalised frequency prior. Skip the walk when that barrier is already
≥ tau:

| tau | walks skipped | share skipped | argmax changes lost | share of changes lost |
|---|---|---|---|---|
| 0.5 | 518 | 61.4% | 5 | 5.5% |
| **1.0** | **404** | **47.9%** | **0** | **0.0%** |
| 2.0 | 113 | 13.4% | 0 | 0.0% |

**Every one of the 91 walks that overturned the prior had a barrier below 1.0 nat** (exactly 5 of them lay in
[0.5, 1.0), the rest below 0.5). ⚠️ **These 12 documents are the TEST split, so tau = 1.0 is a SIZING, not a
fitted parameter** — the brief must sweep tau on a TRAIN split (even-index GUM documents) and report on TEST.

## HOW THE BRAIN DOES THIS — PINNED, not our invention

**Reordered access / the subordinate-bias effect.** For a BALANCED ambiguous word (two senses of similar
frequency) a disambiguating context measurably changes and speeds the read; for a BIASED one (a dominant
sense) prior context produces no comparable effect unless it is strong enough to overcome the dominance —
Duffy, Morris & Rayner (1988), *Lexical ambiguity and fixation times in reading*; Rayner & Frazier (1989);
Binder & Rayner (1998). That is exactly a **barrier gate**: context is recruited where the resting levels are
close and not where one already dominates. **The COMPUTATION is pinned** ("spread only when the base rate has
not already decided"); **the THRESHOLD is OUR PARAMETER** and must be swept, never adopted.

The same shape appears in the retrieval model this substrate already uses: ACT-R resolves a retrieval when one
chunk's base-level activation dominates, and recruits further cues only under competition.

## THE BAR (can-fail; the gate is certified by IDENTITY, like pri 146)

1. **LOSSLESS ON THE ARGMAX PATH, OR THE LOSS IS COUNTED.** With the gate on, the situation model must be
   **byte-identical** on every document (the pri 146 identity harness runs as-is: a fresh reader per document,
   full-field comparison). Any difference is the gate's own loss and must be reported per event, not averaged.
2. **THE DISTRIBUTION PATH NEEDS ITS OWN BAR AND IT IS NOT THE ARGMAX.** `sense_posterior_in_context` hands a
   whole distribution to `harm_help_arithmetic`, and its argmax moves on **42%** of calls when the walk is
   destroyed — so "the prior already decides" is NOT a sufficient test there. Measure at the CONSUMER: does
   `harm_help_arithmetic`'s output change? (Downstream it evidently barely does — 0.29% of recorded fields —
   but that must be shown for the gate, not assumed from the twin.)
3. **THE INFO-FREE TWIN: a gate that skips the SAME NUMBER of walks at random must LOSE.** At tau = 1.0 the
   real gate loses 0 of 91 argmax changes; a random gate skipping 47.9% of walks should lose ≈ 44 of them
   (10.8% × the skipped share, 3 seeds). A gate that cannot be beaten by its random twin is not a gate.
4. **THE SAVING, TIMED THE PRI 146 WAY** — paired, alternating, in one process, stable pairs only, the
   discarded pairs named. Expected from the shares: the walk is 61% of a read, the gate removes ~48% of walk
   **invocations**, and the pri 146 memo removes 44% of them as repeats. **How the two compose in SECONDS is
   NOT known** — the join between "skipped by the gate" and "would have been a memo hit" was not measured, and
   measuring it is step 1 of the brief.
5. **NOTHING ABOUT THE WALK CHANGES.** Not the damping, not the 30 iterations, not the graph, not the blend's
   lam. The gate changes *when* the operation runs, never what it computes.

## ENTRY POINTS

- `hdlab/grounded_semantic_graph.py:248 _blend_pick(ppr, prior, lam, alpha=0.1, eps=1e-6)` — the barrier is
  computable from `prior` alone, **before** the walk is requested; `:414 select_sense_blended` is where the
  request is made.
- `hdlab/force_dynamics_valence.py:718 context_sense_sign` (the argmax path) and `:688
  sense_posterior_in_context` (the distribution path, lam = `affect_lexicon.SENSE_LAM` = 4.0).
- `hdlab/force_dynamics_valence.py:844-895 force_dynamics_event_type` — the three gates the sense choice must
  survive to reach the record: `affecting is False` → abstain; the sign is used only as an `override` when the
  word-level cascade has none; the posterior is one term in `harm_help_arithmetic`. Then
  `situation_reader._assign_affect` reports nothing unless `stage == "event"`.
- The harness: `experiments/exp_ppr_memo_v1.py` (`--consumers` records the barrier per call; `--identity` is
  the certifier; `--timing` is the honest clock).

## WHAT THIS BRIEF MUST NOT CONCLUDE

That the walk is useless. It is consumed (permuting it moves the sense verdict on 3.0% of verdicts and the
recorded field on 0.29% of events), and 91 real sense decisions on 12 documents depend on it. **The finding is
that it is asked 89% of the time in positions where it cannot matter** — that is a gating defect, not an
argument for deleting a pinned brain operation.
