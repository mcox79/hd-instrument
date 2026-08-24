---
priority: 3
review:
review_text:
---

# PROBLEM: we concluded we must BUY a meaning resource, but we never tried letting the one we own TEACH the one we built

## THE PROBLEM IN PLAIN LANGUAGE

We have two sources of word meaning:

- **a hand-rated table** of what words feel like physically (bright, heavy, loud). We own it. It is
  accurate but only covers some words.
- **a text-statistics model** we build ourselves by reading. It covers every word we have ever read,
  but on its own it is close to useless -- on one test it scored *backwards*.

A recent piece of work asked whether our system can recognise a word in a kind of text it has never
seen. The answer came back: **nothing we build ourselves can do it, so we need to buy a big supplied
text-statistics model.** That conclusion was carefully controlled and the measurement is sound.

**But it only ever tried the two sources side by side -- glued together and used at once.** It never
tried the other thing you can do with two sources: **let the good-but-narrow one TEACH the
broad-but-useless one.**

That matters, because on a *different* test the same day, teaching worked dramatically when gluing
did not. The hand-rated table taught a direction through the text-statistics model, and the result
scored far better than either source alone -- the hand-rated one was at chance, the text-statistics
one was backwards, and their *agreement* carried it.

**So: does teaching also rescue the recognition task? If yes, we do not need to buy anything.**

**And be clear about the honest doubt, because it is real.** Teaching was demonstrated on a
different question -- *"can this word replace that one"* -- not on *"which word fills this gap"*.
The original submission's own best point is that those two are not the same thing. So this could
genuinely fail. **A clean, well-powered failure is a full PASS for this brief** -- it would close
the do-it-ourselves route properly and make the case for buying honestly, instead of by never having
tried.

## WHY THIS ONE

It decides a purchase. If teaching works, the "supply a distributional spoke" dependency disappears
and the system stays self-built. If it does not, we stop guessing and buy with evidence.

It is also the same shape as a redirect that already paid off this week: Phase 1 of the long-term
plan wanted to buy 14,704 more hand-rated words, and the measured answer was that projecting the
norms we already own covers the gap instead. **Twice now the reflex has been to buy more; once it
has been checked, and buying was not needed. This checks it the second time.**

## MEASURED vs INFERRED

**MEASURED:**
- `BOTH` in `experiments/solverB_cortical_paradigmatic_generalization_v1.py` is a **concatenation** --
  line 36 reads `BOTH  context+spoke concat`. The strings `distil`, `teach`, `taught` and `orient`
  do not occur anywhere in that file. The taught combination was never run there.
- On the retrieval task, every self-built arm loses: `CTX_RAW 0.029`, `CTX_PROF 0.020` (at the
  info-free twins, `RANDOM 0.040`), `SPOKE 0.083`, `BOTH 0.092`, `LSA_FULL(20k) 0.052` -- all at or
  below the concreteness floor `0.115` (hit@10). Supplied GloVe clears CI-separated 3/3.
- Its witness passes 6/6 scaffold-free, exit 0. I re-ran it myself.
- On the SUBSTITUTABILITY task, teaching works:
  `exp_crossmodal_distillation_substitutability_v1` reads **`0.8388` CI `[0.8031,0.8720]`**, beating
  its info-free twin's MAXIMUM over 200 draws, with **grounded alone at chance `0.5513`** and
  **distributional alone INVERTED `0.0285`**.
- That result is **not** carried by the words the hand-rated table covers: split by coverage it
  reads `0.8263` covered vs `0.8669` CI `[0.8062,0.9220]` uncovered, and both hub-BLIND controls are
  flat across the split (`-0.0051`, `+0.0166`).
  Reproduce: `python tools/split_distillation_by_hub_coverage.py`.
- The orientation in that cell comes from the hub's OWN ranking on unlabelled pairs, never from
  gold. I read the code; that is why its null p95 is `0.68` rather than `0.50`.

**INFERRED, NOT MEASURED -- do not inherit these:**
- **Whether teaching transfers from substitutability to retrieval. Nobody knows. That is the brief.**
  No number crosses tasks.
- I have not checked whether the teaching construction can even be applied to this cell's retrieval
  space without modification. Assume it needs work.
- I have not estimated how much of the GloVe advantage teaching could close, and I am deliberately
  not guessing.

## ALREADY TRIED

- **Concatenating the two channels -- DONE, FAILED.** `BOTH 0.092`, below the `0.115` floor. Do not
  re-run it as though it were new.
- **A second-order/paradigmatic retrieval cue -- DONE, FAILED, TWICE.** `CTX_PROF 0.020 <= CTX_RAW
  0.029`, reproducing the landed `exp_readout_second_order_v1`
  (`SYNTAGMATIC_CONFIRMED / NEW_READOUT_CLEARS_FLOOR_NO`). **That lever is closed. Do not re-propose
  a retrieval-rule tweak.**
- **A self-built distributional space at our full corpus scale -- DONE, FAILED.** `LSA_FULL(20k)
  0.052`. The corpus shortfall (~`1,000x` vs GloVe) was enumerated from the corpora, not estimated,
  so "just read more" is closed too.
- **The sensorimotor asset alone -- DONE, FAILED.** `SPOKE 0.083`, below the concreteness floor, and
  confirmed to BE the project's meaning asset (`cos=1.000` against `grounded_vector`). It carries
  similarity, not retrieval association.
- **A relational knowledge-graph route -- explored and unpromising.**
  `exp_arc_fact_retrieval_semantic_kb_climb_v1` landed `KB_BELOW_FLOOR`, and a circular WordNet
  oracle reads `0.0365` under a partial cue.
- **Weighting sources in general -- refuted across four instruments.** A perfect router scores
  EXACTLY the channel (`0.4811`), so no monotone blend has headroom. **This is the strongest reason
  to try teaching rather than another combination rule, and the strongest reason not to bother with
  a fifth weighting scheme.**

## VERIFY BEFORE YOU START

1. `.venv/Scripts/python.exe verification/solverB_verify_paradigmatic_generalization.py` -- expect
   6/6 PASS, exit 0. That is the task harness you are extending.
2. `python tools/split_distillation_by_hub_coverage.py` -- expect the covered/uncovered table above.
3. Read the orientation code in `exp_crossmodal_distillation_substitutability_v1` and satisfy
   yourself the sign comes from the hub's own ranking and never from gold. **If you cannot confirm
   that, stop and say so** -- the whole mechanism rests on it.
4. Re-read `notes/problems/cortical_read_never_tested_where_it_matters/SOLVED.md`, including the
   `INTEGRATED_BY_STRATEGY` section, which is where this gap was identified.

## THE BAR

**A TASK SCORE ON THE SAME UNSEEN-CO-OCCURRENCE POPULATION, WITH AT LEAST 200 SUCH ITEMS, AND A
CI-SEPARATED MARGIN OVER THE STRONGEST FLOOR YOU ACTUALLY RUN ON THAT POPULATION.** Reuse the
existing floors (`CONC 0.115` is the one that matters) -- recompute them, do not quote mine.

To succeed:

1. Build a **taught** arm: the grounded/sensorimotor source teaches a direction over the self-built
   distributional space, then that direction scores the retrieval task. Orientation must come from
   an unlabelled signal, **never from the gold**.
2. Score it against **the same floors, the same items, the same pool, both tie conventions**, with
   `tools/rank_with_ties.py`. Report CI half-width and null p95 beside every margin.
3. **An info-free twin of the taught arm**, oriented identically -- this is non-negotiable, because
   orientation alone lifts a null (it is why the substitutability null sits at `0.68`, not `0.50`).
   If your taught arm does not beat its own oriented twin's MAXIMUM, it has not cleared anything.
4. Keep `GLOVE` in as the ceiling/could-it-succeed control, and `BOTH` in as the concatenation
   reference, so the taught-vs-glued comparison is direct and on one population.
5. Save the scored population (`scored_population` beside the score) so the next question is a
   re-analysis rather than a re-run. This has cost us multi-hour re-runs three times.
6. Multi-seed via `tools/replication_gate.py`; quote the verdict string.

**If teaching is refuted, do not stop at "refuted."** Say what was tested, what the strongest
brain-faithful version of the idea would be, and test THAT -- then solve the problem a different way
if you can. A refutation plus a working alternative is worth far more than a refutation alone.

**Brain framing, and answer it explicitly.** Hub-and-spoke (Lambon Ralph; ATL integration) is the
PINNED structure here. The live question is what the hub actually DOES to its spokes: our system has
only ever **concatenated or weighted** them, and the brain plainly does something stronger --
cross-modal experience *shapes* each modality's representation rather than sitting beside it. Say
which of your choices are PINNED-BY-EVIDENCE and which are OUR-INVENTION-UNDER-TEST. Inventing is
fine; mislabelling is what is barred.

## FILES AND ENTRY POINTS

| path | what it is |
|---|---|
| `experiments/solverB_cortical_paradigmatic_generalization_v1.py` | **the task harness to extend.** `BOTH` = concat at line 36; arms at 119; scoring at ~474 |
| `verification/solverB_verify_paradigmatic_generalization.py` | its scaffold-free witness, 6/6 PASS |
| `experiments/exp_crossmodal_distillation_substitutability_v1.py` | **the teaching mechanism to port.** Read its orientation code first |
| `data/exp_crossmodal_distillation_substitutability_v1/scored_population.json` | its saved population |
| `tools/split_distillation_by_hub_coverage.py` | the coverage split, with its difficulty controls |
| `tools/rank_with_ties.py` | mandatory for any rank comparison; there is no bare-rank call signature |
| `tools/replication_gate.py` | mandatory for any cross-seed claim |
| `data/solverB_cortical_paradigmatic_generalization_v1/metrics.json` | the floors and arm scores above |

**Constraints.** Never edit `preregs/**` or any `arm_key*` file -- harness-denied deliberately. If
the only move left is to weaken a gate, stop and say so rather than doing it. Never bundle a
deletion (`rm`) with real work in one call: it is auto-denied and destroys the bundled work too.
Do not write to `hdlab/` -- integration is the strategy session's (board Q111).

**If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
and do not silently proceed without the denied step.** A dropped precondition invalidates the
declared gate even when the result may be fine -- that is not yours to judge silently. Disclose it.

## DO NOT QUOTE

- **`0.8388`** -- that is SUBSTITUTABILITY, a different task and a different population. It is the
  reason to run this experiment; it is **not** evidence about retrieval. Never carry it across.
- **`0.115`, `0.029`, `0.052`, `0.083`, `0.092`** -- recompute every floor and arm on your own run.
  No number crosses populations, and these came from a different seed set than yours will.
- **`+0.0410`** (the covered-vs-uncovered difference) -- its CI `[-0.0353,+0.1091]` SPANS ZERO. It is
  a "not worse", never a gain. Do not quote it as an improvement.
- **`A5_STRINGCTRL 0.0870`** -- ~78% morphological leakage; never quote it as a spelling floor.
- Do not quote any margin without its CI half-width and the null p95 beside it.
- Do not describe the supplied hand-rated table as "label-free but free" -- it is **label-free, not
  resource-free**, and that limit travels with every number derived from it.
