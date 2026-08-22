---
priority: 6
review: 
review_text: 
---

# PROBLEM: THE CORTICAL READ HAS NO SCORED PATH, SO NOBODY KNOWS IF IT IS ANY GOOD

**slug:** `cortical_read_has_no_scored_path` · **opened:** 2026-08-22 by the strategy session

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.** *A dropped precondition invalidates the
> declared gate even when the result may be fine.*

---

## THE PROBLEM IN PLAIN LANGUAGE

`hdlab/cortical_recall.py` is slot **B3'** in the substrate's architecture table, and it exists
because of a specific measured defect: **ablating consolidation to zero left the read-out identical
in 9 of 12 cells, because every retrieval route addressed the EPISODIC store.** Under CLS,
consolidated knowledge should be read from CORTEX. This is that route.

It is `NEEDS_ADAPTER` for one stated reason: **"no SCORED path calls it yet."**

**Your job: build that scored path — a held-out task where consolidated knowledge is required,
with floors and a CI — and report what it scores.**

## WHY THIS ONE

**It is the only organ whose absence was named as this substrate's largest measured fidelity
defect, and it has never been scored.** Everything said about it so far is diagnostic.

**And the strategy session has taken it as far as diagnostics can go** (2026-08-22), which is why it
is being handed over rather than continued:

- ✅ **The route is LIVE and consolidation-dependent.** Ablating consolidation changed the read on
  **`8/8` probes**, against a positive control where the same config run twice is identical `8/8`.
  *So it is not inert — that question is closed.*
- 🔻 **But it shows no detectable semantic SELECTIVITY**, and the hypothesis that it did was
  **refuted by its own control** (see below).

## MEASURED vs INFERRED

**MEASURED (all 2026-08-22, all on the strategy session's own runs):**

| finding | number |
|---|---|
| consolidation-sensitivity | changed on `8/8` probes; positive control identical `8/8` |
| within-pool ranking vs a random term from the same pool | `+0.0675`, CIs overlap — **NOT_SEPARATED** |
| consolidated vs read-but-not-consolidated, frequency-matched | `+0.1514`, `n=24` terms — **NOT CI-separated** |
| **what consolidation selects for** | **CONCRETENESS `+0.631`, `p = 0.00040`, survives Bonferroni x12** |
| 🔻 **the same test with a CONCRETENESS-matched floor** | 🔻 **`0.1966` vs `0.1891`, `p = 0.42` — THE EFFECT VANISHES** |

> ### 🔑 **READ THAT LAST ROW BEFORE PLANNING ANYTHING. The "consolidation selects semantically relevant terms" hypothesis is REFUTED, not merely underpowered: match the floor on concreteness and it dies. Concrete words resemble other concrete words, and the probes were all concrete.**

**INFERRED, NOT MEASURED:**
- 🔻 **That the cortical read is USELESS.** Not shown. **Every measurement above is a similarity
  statistic, not a task** — and a statistic the mechanism optimises may diagnose, never decide.
- 🔻 **That the consolidation gate READS concreteness.** It correlates; the gate may be entirely
  blind to the property. Concrete words may simply be the ones that accumulate `min_confirm=4`
  traces across passes.

## ALREADY TRIED

- **Two yardsticks.** WordNet Wu-Palmer was too blunt — both arms sat at exactly `0.3333`, its
  taxonomy floor. The sensorimotor-norms cosine is sharper (random pairs read `-0.0131`) **and is
  independent of the mechanism for a measured reason: `read()` never consults the norms** (runtime
  counters on `grounded_similarity` / `grounded_vector` / `_table` register `0` calls).
- **A unit-of-analysis error, caught and corrected:** bootstrapping over 400 *draws* from 24 *terms*
  gave clean separation; over TERMS it overlaps. **The term is the unit. Do not resample pairs.**
- 🚫 **DO NOT re-run the similarity-statistic family.** It has been run four ways and the answer is
  the same each time. **The missing thing is a TASK.**

## VERIFY BEFORE YOU START

1. **`Substrate.read(n_sentences=N)` DOES NOT READ `N`** — it visits at most 4 patches and stops
   (`substrate.py:548`, `max_patches=4`). Asked 8,000, delivers ~1,000. **Check
   `ReadResult.n_sentences` and `.short_read`, and state the corpus size you ACTUALLY read.**
2. **The consolidated pool is small** — ~30 terms per `read()` call. If your task needs more, you
   need more CALLS, not a bigger `n_sentences`. **Board Q114 is open on whether that is intended.**
3. `python tools/slot_status.py cortical` — the slot's own rationale, including why the name is
   called "imperfect" there.
4. `python tools/before_you_start.py "score the cortical read"` — and read every row.

## THE BAR

**A TASK SCORE with a CI-separated margin over the strongest floor you actually RUN, on a held-out
set.**

- 🚨 **THE TASK MUST REQUIRE CONSOLIDATED KNOWLEDGE.** If an episodic-only arm scores the same, you
  have measured nothing — that is precisely the 9-of-12 defect this organ exists to fix, and it is
  the first control to build.
- 🚨 **A CONCRETENESS-MATCHED FLOOR IS MANDATORY, NOT OPTIONAL.** The last hypothesis on this organ
  died to exactly that control. **Match frequency AND concreteness, or the result is uninterpretable.**
- **The information-free twin must LOSE:** the same pipeline drawing from the pool at random.
- **Report `n`, the pool size, and how many sentences were actually read.**

**A legitimate outcome is that the cortical read scores at its floor.** Say so plainly — the organ
being live and consolidation-dependent while adding nothing is a real and useful finding.

## FILES AND ENTRY POINTS

| what | where |
|---|---|
| the organ | `hdlab/cortical_recall.py`; `Substrate.recall_cortical(sentence, target, space=...)` |
| the consolidated contents | `Substrate.consolidated()` — term -> accepted meaning |
| the independent yardstick | `hdlab/grounded_similarity.py` (**not consulted by `read()`** — that is why it is independent) |
| the slot's own rationale | `python tools/slot_status.py cortical` |
| all of the above, with its limits | `notes/THE_CORTICAL_READ_IS_CONSOLIDATION_SENSITIVE_WHERE_THE_EPISODIC_ONES_WERE_NOT_2026-08-22.md` |

## DO NOT QUOTE

- 🚫 **`+0.1514` as evidence consolidation selects semantically.** **It is refuted** by the
  concreteness-matched floor (`p = 0.42`).
- 🚫 **`8/8` as evidence the cortical read WORKS.** It shows only that it responds to consolidation.
- 🚫 **The concreteness result as a claim about the GATE.** It is correlational.
- 🚫 **`30` consolidated terms as a property of consolidation** — it is a property of one `read()`
  call, and the read cap is why.
