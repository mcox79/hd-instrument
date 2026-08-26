---
priority: 5
review:
review_text:
---

# PROBLEM: one store does two jobs the brain keeps separate, and "consolidation" is a single averaging step -- not the brain's selective, schema-gated, interleaved replay

**slug:** `one_store_does_two_jobs_and_consolidation_is_a_single_average` - **opened:** 2026-08-26 by the strategy session
(packaged from `notes/BRAIN_FOUNDATIONAL_AUDIT.md` deviation #5 -- the last genuinely-foundational unqueued deviation)
**status:** OPEN - **first-hand in ORGAN_MAP D4 + the audit; a FAITHFUL engine already exists, islanded**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `5`, in the FOUNDATIONAL tier (above the
> downstream meaning-wiring/parser), alongside predictive-coding (p4). It is the last of the real foundations.
> It is DISTINCT from p2 (`the_consolidated_cortical_store...`): p2 is about READING the consolidated store; this
> is about WRITING / REPLAYING into it the brain's way. They are the read and write halves of the same memory
> architecture -- coordinate, do not duplicate. Re-rank freely.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do. If you have
> not identified the brain's mechanism and attempted to build it, you have not started the real work,
> whatever else you have measured.
>
> **🚀 YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> You are NOT boxed in -- not by this brief, not by the existing organs, not by the integration points you
> would tie into: if a MORE brain-foundational method conflicts with any of them, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful). Exploring
> the brain's true method is the work we most want from you; a bold, well-argued brain-faithful direction --
> even unfinished -- beats a tidy engineering result that never asked the question.
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several of your angles hit the
> SAME wall, that is strong evidence that NONE of them was the brain's mechanism -- the faithful method is
> probably DIFFERENT IN KIND, not another variation of what you already tried. A wall is a FIDELITY GAP TO
> BUILD ACROSS, never a ceiling. Hitting one is exactly the moment to LEAVE the family of methods you were
> sweeping and ask the biology again.
>
> **⛔ "CONVERGED" HAS A HIGH BAR, AND EXHAUSTING ENGINEERING VARIATIONS DOES NOT MEET IT.** Claim
> convergence ONLY when you have (a) identified how the brain actually performs this computation AND (b)
> replicated that operation as faithfully as you can and tested it, OR shown with a SPECIFIC reason why it
> cannot be replicated here. "I tried several combining / gating / scoring angles and they all plateaued at
> the same wall" is NOT converged -- it is tuning-limited, and it means the brain's mechanism is still
> UN-TRIED. That is a reason to explore harder, not to submit.
>
> **🔁 THE 30-MIN DEEPENING IS HOW YOU FORCE THIS -- IT IS NOT OPTIONAL BUSYWORK.** Run your own cron
> (`CronCreate "13,43 * * * *"`); each fire asks "how does the brain REALLY do this, one level deeper than
> my current mechanism?" -> implement -> test (can-fail, strongest real floor, info-free twin LOSING) ->
> iterate. Its whole purpose is to make you ask the brain question several more times than your own sense of
> "done" would. CANCEL it (`CronDelete`) and submit ONLY when the brain-mechanism bar above is met.
> Declining it because "my angles converged" is precisely the case it exists to catch.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully
> built.** A negative on a family of convenient engineering methods is not a negative on the capability; it
> is a report that you have not yet found how the brain does it.
>
> **📖 REFERENCE THE BRAIN-FOUNDATIONAL AUDIT, AND HELP KEEP IT TRUE.** Before you start, read the entry for the
> system you are touching in `notes/BRAIN_FOUNDATIONAL_AUDIT.md` -- it gives the brain structure, whether the
> brain's equation is PINNED or something we are INVENTING, our current fidelity, and the known deviation, so you
> inherit that instead of re-deriving it. If your work shows a verdict there is WRONG, STALE, or INCOMPLETE, or you
> find a NEW deviation, put a short **AUDIT UPDATE** note in your submission -- the strategy session folds it into
> the audit at integration. The audit is a living, shared map and you help maintain it.

## 1. THE PROBLEM IN PLAIN LANGUAGE

The brain keeps two memory systems separate on purpose: a FAST one that binds a single experience in one shot
(hippocampus), and a SLOW one that folds that experience into general knowledge over time, during sleep, by
REPLAYING it (cortex). The slow system does not just average everything -- it replays SELECTIVELY (the surprising
and important episodes more), it is GATED BY WHAT YOU ALREADY KNOW (a fact that fits a schema consolidates fast),
and it INTERLEAVES old and new so learning something new does not overwrite what you already had. We do none of
that: **we have ONE store doing both jobs, and our "consolidation" is a single averaging step per cycle --
ungated, un-interleaved, un-prioritised.** The uncomfortable part: we already BUILT a faithful consolidation
engine (`continual.py`) that does selective, budgeted replay and PASSED on synthetic data -- and then left it
unwired while the live path kept averaging. The question: does brain-faithful consolidation -- separate fast/slow
+ selective, schema-gated, interleaved replay -- actually beat the single average on the job that DEFINES
consolidation: **learn something NEW from new reading WITHOUT catastrophically forgetting the OLD?**

## 2. WHY THIS ONE

- **It is foundational: it is how learning COMPOUNDS.** Without brain-faithful consolidation, each read either
  overwrites the last (catastrophic forgetting) or is diluted into an average -- so nothing accumulates. Every
  "read more to get better" hope depends on this working.
- **The faithful engine already exists and is ISLANDED** (`continual.py`, `cls_discrete_budget` passed synthetic,
  HARD_PASS) -- this is a WIRE-and-prove-on-real-reading problem more than a build-from-scratch one, which is
  tractable and high-leverage.
- **It is genuinely unqueued and genuinely foundational** (audit deviation #5) -- the last real foundation; beyond
  it the audit backlog is capability, not architecture.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED (Complementary Learning Systems -- McClelland, O'Reilly, Norman 1995; O'Reilly 2014):** fast hippocampal
one-shot binding and slow cortical statistical consolidation are SEPARATE, complementary systems -- fast/sparse/
pattern-separated vs slow/overlapping/statistical. Consolidation is REPLAY (sharp-wave ripples, sleep) that is:
SELECTIVE (reward- and surprise-scaled -- Ambrose/Pfeiffer/Foster; reverse-replay reward scaling), SCHEMA-GATED
(a fact consistent with an existing schema consolidates in ONE trial -- Tse 2007/2011), and INTERLEAVED (old and
new replayed together to avoid catastrophic forgetting -- the CLS reason interleaving exists).
**PINNED as a system; the SELECTION FUNCTION (which traces get replayed) is UNPINNED.**
**OUR-INVENTION-UNDER-TEST:** the exact selection/schedule (surprise-budget, schema-gate, interleave ratio) --
copy the COMPUTATION (selective interleaved replay that integrates new without erasing old), SWEEP the parameters.

**Corpus-age note:** McGuffey is ~200 years old; the OLD/NEW split should hold the corpus era fixed so a
"forgetting" effect is not just a distribution shift.

## 4. MEASURED vs INFERRED

**MEASURED (ORGAN_MAP D4 + the audit, re-verify):** the LIVE consolidation site
(`reading_grounding_loop.py::checkpoint`) is a single averaging op per cycle -- ungated, un-interleaved,
un-budgeted (WRONG-OP-CLASS). The FAITHFUL engine `hdlab/continual.py` (NREM-replay consolidation) exists and is
ISLANDED; `cls_discrete_budget` reached HARD_PASS on SYNTHETIC data. Ablating the current consolidation moved the
read-out by `0.0000` in the audit -- consistent with it being both unread AND a no-op average.
**INFERRED (the open question, decisive either way):** whether brain-faithful consolidation (fast/slow separation
+ selective / schema-gated / interleaved replay, wiring `continual.py`) beats the single-average on an OLD-vs-NEW
interleaved-retention task built from REAL reading -- integrate NEW facts while retaining OLD -- CI-separated,
info-free twin (RANDOM replay selection) LOSING.

## 5. ALREADY TRIED (do not re-run)

- `cls_discrete_budget` on SYNTHETIC data -- HARD_PASS, but islanded and never run on real reading. Do NOT re-run
  the synthetic pass; the open question is REAL reading + wiring.
- Single-average / Kalman / retrieve-not-average consolidation ops -- the current live path; the point is the
  SELECTIVE INTERLEAVED replay, not another averaging variant.
- Note `cls_discrete_budget_consolidate_v6_replay` is a STALE VET_PENDING row (registry) -- read its result before
  rebuilding; it may already answer part of this.
- Query `experiment_index.py query "consolidation"`, `query "replay"`, `query "catastrophic"`, `query "interleave"`,
  `query "schema"`; read `hdlab/continual.py`, `hdlab/additive_map.py`, and the `checkpoint` site first.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Confirm the live consolidation site is a single average and that `continual.py` (selective replay) is islanded
  (zero live importers).
- Read `cls_discrete_budget`'s synthetic result and its VET_PENDING row -- do not re-derive what it already shows.
- Build the OLD-vs-NEW interleaved-retention instrument on REAL reading (hold corpus era fixed) and recompute its
  floor -- averaging cannot even be scored on retention, so the floor is the single-average's OLD+NEW accuracy and
  a RANDOM-selection replay twin.

## 7. THE BAR

On an OLD-vs-NEW interleaved-retention task from real reading (learn NEW facts across a session while retaining a
held-out OLD set; corpus era fixed), floor recomputed on that population: **brain-faithful consolidation (fast/slow
separation + SELECTIVE, SCHEMA-GATED, INTERLEAVED replay) must beat the single-average consolidation CI-separated
over the strongest floor's UPPER bound on JOINT old+new retention, with the info-free twin (RANDOM replay
selection, same replay budget) LOSING CI-separated**, CI half-width + null p95 reported. Sweep the selection /
interleave parameters; do not adopt a number.
**DECISIVE EITHER WAY:** a win -> wire `continual.py` (+ the selection function) as the consolidation op (strategy
lands it; default-off flag since it changes the write path). A rigorous loss -> selective interleaved replay does
NOT beat averaging on our data at this scale (report why -- too few episodes, no schema structure to gate on,
etc.); that is a real foundational finding and a full PASS, and it tells us catastrophic forgetting is not yet the
binding constraint here.

## 8. FILES AND ENTRY POINTS

- `hdlab/continual.py` (the FAITHFUL, islanded NREM-replay engine -- the thing to wire), `hdlab/additive_map.py`
  (CLS additive map), `hdlab/reading_grounding_loop.py::checkpoint` (the live single-average site),
  `hdlab/schema_exemplar_bayes.py` / `hdlab/ultrametric_clustering.py` (schema structure for the gate).
- `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (deviation #5; memory tier D4) + ORGAN_MAP D4 -- report any correction as an
  AUDIT UPDATE. Coordinate with p2 (`the_consolidated_cortical_store...`, the READ half).
- Prove in `experiments/` + `verification/`; propose the hdlab diff in `SOLVED.md` (strategy lands it, Q111). Do
  NOT write `hdlab/`.

## DO NOT QUOTE / DO NOT REDO

- Do NOT quote the SYNTHETIC `cls_discrete_budget` HARD_PASS as a capability -- it was never run on real reading.
- Do NOT read the `0.0000` ablation as "consolidation is pointless" -- it means the current op is both unread AND
  a no-op average; the test is whether a FAITHFUL op helps.
- Do NOT test with a single read (no OLD to forget); the interleaved OLD-vs-NEW regime is where averaging and
  selective replay diverge.
