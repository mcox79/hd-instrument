---
priority: 5
review:
review_text:
---

# PROBLEM: WE JUDGED THE "SETTLED KNOWLEDGE" READER ON THE ONE TASK IT IS WORST SUITED FOR

**slug:** `cortical_read_never_tested_where_it_matters` - **opened:** 2026-08-22 by the strategy session
**status:** OPEN - **this brief exists because the PREVIOUS solver said it should, and said so while
their own result looked like a clean negative.** That is the recommendation to trust.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**
> *Reason, so you do not self-negotiate it: a dropped precondition invalidates the declared gate even
> when the result may be fine. "The number probably didn't change" is not yours to decide silently.*

---

## 1. THE PROBLEM IN PLAIN LANGUAGE

The system has two ways of remembering. One keeps individual experiences. The other slowly builds up
settled, general knowledge out of many experiences - the thing you know about dogs, as opposed to the
particular dog you met on Tuesday.

We finally tested the settled-knowledge reader last night. The test was: hide a word in a sentence
the system had never read, and ask the settled store to guess it. **It lost to simply counting which
words tend to turn up near each other.** Not by a little - counting won at every setting, on every
run.

**But that test rewards exactly the wrong thing.** The hidden word sits in a sentence surrounded by
words it commonly appears with, so "which words go together" is close to the ideal strategy. Settled
general knowledge is not for that. Its distinctive job is the opposite: recognising something in a
situation you have *never seen it in before*.

**The previous solver saw this and tried to test it properly. Only 43 usable questions existed.**
That is far too few to conclude anything, and they said so rather than reporting it as a result.

**So we do not currently know whether this component is useless or whether we tested it in the one
regime where it could not win.** Those call for completely different responses, and nothing on disk
distinguishes them.

## 2. WHY THIS ONE

- **It is the only test that can turn a negative into a decision.** Right now the component sits in a
  "built but not connected" state with a note saying it lost to counting. If it also fails the test
  it is *for*, that is a real dead end and the retrieval space needs rebuilding. If it wins there,
  the earlier loss was a badly chosen task and the component has a job.
- **The recommendation comes from the person whose own result it might overturn.** The solver who
  produced the negative named this as "the single most useful follow-up" and flagged their own
  generalisation null as the first thing they would withdraw. *That is the opposite of defending a
  finding, and it is why this is ranked where it is.*
- 🔑 **THE OBVIOUS CHEAP VERSION IS ALREADY RULED OUT, SO DO NOT REPEAT IT.** Stratifying the
  existing task into "cue and answer have co-occurred" versus "have not" gives only **9-17 unseen
  items per run**. At 16,600 sentences read, nearly every settled term has already co-occurred with
  its cue words. **The scarcity is structural: you cannot fix it by re-running the same design.**

## 3. MEASURED vs INFERRED

**MEASURED** - `data/solverB_cortical_scored_path_v1/metrics.json`, 3 seeds, n=300 items/seed, clean
held-out split, verified by the strategy session on the artifact:

| arm | hit@1 | hit@50 | median rank |
|---|---|---|---|
| **co-occurrence COUNTING floor (strongest)** | **0.090 / 0.103 / 0.097** | **0.71 / 0.75 / 0.70** | **22 / 20 / 24** |
| best cortical arm (context+sensorimotor) | 0.057 / 0.043 / 0.043 | 0.37 / 0.36 / 0.33 | 71 / 70 / 87 |
| concreteness-prior floor | 0.000 | 0.12 / 0.10 / 0.11 | 228 / 282 / 237 |
| scrambled cue (information-free) | 0.000 / 0.000 / 0.003 | 0.11 / 0.18 / 0.12 | 212 / 197 / 222 |
| random twin (information-free) | 0.003 / 0.007 / 0.000 | 0.11 / 0.07 / 0.13 | 238 / 229 / 201 |
| episodic route, same candidate set | 0.000 (surfaced 300/300) | -- | -- |

- **The component is NOT inert and NOT a concreteness artifact.** It beats a scrambled cue, a random
  ranker and a concreteness prior, and it beats the episodic route at hit@1. *That small difference
  is real, is consistent with the theory, and is buried under counting.*
- **It clears the strongest floor in 0 of 15 seed-by-k cells.** At k=50 the gap is CI-separated.
- **The clean split is genuinely clean:** measured directly, the corpus cursor advances by exactly
  what the reader delivers, gap `0` at three settings.

**INFERRED, NOT MEASURED:**

- 🔻 **That the component has no generalisation ability.** Pooled `n=43` across 3 seeds, below the
  stated `n>=30` per-seed gate. On those items the cortical arms sit near the middle of the pool,
  indistinguishable from scramble, frequency and random. **A DIRECTION. NOT A VERDICT.**
- 🔻 **That a powered version would come out the same way.** Nothing on disk speaks to this.

## 4. ALREADY TRIED

- **Scoring it on the natural cloze: DONE, and it lost.** Do not redo it. `solverB_cortical_scored_path_v1`.
- **Stratifying that same task by co-occurrence: DONE, and it is structurally underpowered** (9-17
  items per seed). *Do not redo this either - the design cannot produce enough items.*
- **The earlier scoring (`exp_cortical_read_consolidated_v1`, 2026-08-19) is NOT usable as evidence:**
  298-300 of its 300 test sentences had already been read. The leak favoured the component and it
  lost anyway.

## 5. VERIFY BEFORE YOU START

1. **Re-read `notes/problems/cortical_read_has_no_scored_path/SOLVED.md` in full** - it is the
   immediate predecessor, it is thorough, and its harness is reusable. *Its control machinery is
   witnessed scaffold-free in `verification/solverB_verify_cortical_scored_path.py`.*
2. `python tools/before_you_start.py "test whether consolidated knowledge generalises"` and read
   every row returned, not the first.
3. `python tools/slot_status.py cortical` - the slot note now carries the scored verdict and the
   revival criterion this brief is written against.
4. **Check the co-occurrence scarcity yourself before designing around it.** It is the constraint
   that killed the cheap version.

## 6. THE BAR

**A TASK SCORE ON ITEMS WHERE COUNTING CANNOT HELP, WITH AT LEAST 200 SUCH ITEMS, AND A
CI-SEPARATED MARGIN OVER THE STRONGEST FLOOR YOU ACTUALLY RUN ON THAT POPULATION.**

- 🚨 **THE FLOOR IS NOT "co-occurrence scores zero here".** By construction it does - that is what
  makes the population interesting, and it is NOT a floor that anything clears by default. **Run the
  frequency floor, the concreteness floor, a scrambled cue and a random twin ON THE UNSEEN
  POPULATION, and gate on the strongest one's UPPER bound.** A component that beats an absent
  baseline has beaten nothing.
- **BUILD THE ITEMS SO THEY EXIST.** Two routes are named and neither is validated: hold back a whole
  domain or corpus so its vocabulary is never read, or read sparsely against a large candidate pool
  so co-occurrence stays thin. **Say which you chose and why the items you get are fair** - an item
  is only "unseen" if the cue words and the answer genuinely never co-occurred in what was read, and
  that must be MEASURED per item, not assumed from the construction. *This project has a standing
  incident where a "held-out" set built by construction overlapped its training pool 600 of 600.*
- **REPORT BOTH TIE CONVENTIONS.** Ranking over a sparse space ties heavily, and a strict inequality
  counts every tie as beaten - which makes an emptier representation score better. Use
  `tools/rank_with_ties.py`; there is no call signature that returns a bare rank.
- **BUILD THE INFORMATION-FREE TWIN AND CHECK IT LOSES.** If a random ranker does well on your
  unseen population, the metric cannot fail safely there and no number from it means anything.
- **A NULL IS A REAL ANSWER HERE, AND IT IS WORTH AS MUCH AS A WIN** - provided it is powered. Say
  which it is.

## 7. FILES AND ENTRY POINTS

| what | where |
|---|---|
| the predecessor's harness and controls | `experiments/solverB_cortical_scored_path_v1.py` |
| its scaffold-free witness | `verification/solverB_verify_cortical_scored_path.py` |
| the numbers above | `data/solverB_cortical_scored_path_v1/metrics.json` |
| the organ under test | `hdlab/cortical_recall.py` - retrieval RULE and SPACE are OURS-under-test |
| the retrieval space, if the answer is "rebuild it" | `build_cortical_index` |
| the slot note carrying the verdict | `hdlab/substrate.py`, slot `B3'` |
| corpora | `hdlab/corpus_registry.py` - 28 corpora, needed for the held-back-domain route |

## 8. DO NOT QUOTE

- 🚫 **The `n=43` generalisation null as evidence the component cannot generalise.** It is a
  direction. Quoting it as a finding is the error this brief exists to prevent.
- 🚫 **Anything from `exp_cortical_read_consolidated_v1` (2026-08-19)** - 298-300 of 300 items were
  already read.
- 🚫 **"It beats the episodic route" as a capability claim.** True, tiny, and sits far below counting.
- 🚫 **Numbers from the co-occurrence-SEEN population beside numbers from the UNSEEN one.** Different
  populations; no number crosses between them.

## 9. WHAT THE BRAIN SAYS, AND WHERE WE ARE INVENTING

**PINNED:** that consolidated knowledge is read from cortex rather than from the hippocampal store is
the standard complementary-learning-systems account (McClelland, McNaughton & O'Reilly 1995). The
*existence* of this organ is not what is under test.

**OURS-UNDER-TEST, and `hdlab/cortical_recall.py` says so in its own docstring:** the retrieval RULE
and the retrieval SPACE. *There is no pinned equation for cortical semantic retrieval.* So testing
them and finding them wanting is fair - **but it means a failure here indicts OUR retrieval space,
not the CLS account.** Do not report a null as evidence against the brain model.

**THE REVIVAL CRITERION IS BRAIN-FRAMED ON PURPOSE, NOT PERFORMANCE-FRAMED:** the component earns a
live connection only if its retrieval space beats counting *in the regime counting cannot reach*.
"It got better at the cloze" would not qualify.
