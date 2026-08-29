---
priority: 4
review:
review_text:
---

# PROBLEM: tense/aspect is EXTRACTED (situation_reader parses VBD / VBN+had / VBN+be) and STORED (event_bundle has a TENSE slot), and the memory store has a "when" clock (graded_temporal_context) — but the reader has NO tested TEMPORAL-ORDER COMPREHENSION: nothing composes tense + aspect + temporal connectives into a per-event ORDER model that answers "did event X happen before event Y?" when narration order ≠ event order (past-perfect FLASHBACK "she had left before he arrived"; "meanwhile"; "after he ate, he slept"). This is the Zwaan & Radvansky event-indexing TIME dimension — the sibling of the just-built SPACE dimension. Build the composition — a per-event temporal-order register from the already-extracted tense/aspect + explicit connectives — and validate it answers before/after on real narrative CI-separated over the NARRATION-ORDER floor with the info-free twin losing. A rigorous NEGATIVE (narration order already suffices, or temporal comprehension is not the cap) is a full pass

**slug:** `situation_model_has_no_tested_temporal_order_comprehension` — **opened:** 2026-08-29 by the strategy session
(the TIME dimension of the situation model — the direct sibling of the integrated `situation_model_has_no_spatial_location_dimension`,
owner-DONE/EXCELLENT, which built the SPACE dimension). **status:** OPEN — a COMPOSITION + MEASUREMENT problem (the
tense-extraction components EXIST; the temporal-order comprehension is untested). You build + validate in `experiments/`;
strategy lands any hdlab change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `4` — a genuinely MISSING situation-model DIMENSION
> (like SPACE was, the highest-leverage kind), but HONESTLY SCOPED: the tense signals are already extracted + stored, so
> this is the COMPOSITION into tested temporal-order comprehension, not a from-scratch build. Temporal order is core to
> reading (flashbacks, sequence, "before/after"). **Re-rank per the owner.**

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau — it is the FIRST thing you do.
>
> **🚀 YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **⛔ "CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **🔁 THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) — RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one — and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps — AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) — that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When you read "She had already left when he arrived," you know she left FIRST — even though "arrived" is the main verb and
comes later in the sentence. Readers build a mental TIMELINE of when each event happened, separate from the order the
sentences are told in (flashbacks, "meanwhile", "before he ate, he prayed"). This is one of the five core dimensions of
the mental model of a situation (Zwaan's event-indexing: time, space, causation, goals, entities). Our reader has the raw
material — it already reads a verb's tense (past "left" vs past-perfect "had left") and stores a TENSE slot per event, and
the memory has a temporal-context clock — but NOTHING composes those into a tested TIMELINE: there is no organ that
answers "did event X happen before event Y?" when the telling order differs from the happening order. The task: build that
composition — a per-event temporal-ORDER register from the already-extracted tense/aspect plus explicit temporal
connectives (before/after/when/meanwhile/then) — and validate it answers before/after on real narrative, beating the
naive "narration order = event order" floor, with the info-free twin losing. A rigorous NEGATIVE (the narration-order
floor already suffices on real prose, so temporal comprehension is not a current cap) is a full pass — it closes the
question of whether the TIME dimension needs building.

## 2. WHY THIS ONE
It is a genuinely absent, PINNED situation-model DIMENSION — the sibling of the SPACE dimension whose build was the
highest-leverage integration. Temporal order is shared by many reading capabilities: sequence/plot comprehension,
flashback handling, causal inference (a cause precedes its effect — the temporal order CONSTRAINS causation), and the
ToM/belief timeline (what an agent knew WHEN). And it is HONESTLY scoped: the components exist, so this is a composition +
measurement, not a speculative from-scratch build — a clean can-fail question.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the dimension + the cues):** the **event-indexing TIME dimension** of the situation model (Zwaan & Radvansky
  1998; Zwaan 1996 — a temporal shift is an event boundary and costs reading time). The reader recovers event order from
  **grammatical tense/aspect** — Reichenbach's (1947) E/R/S model: past perfect ("had left") places the event BEFORE the
  reference time, simple past AT it — and from **explicit temporal connectives** (before/after/when/while/meanwhile/then;
  Bestgen & Vonk 2000). Neural: the hippocampal–entorhinal system encodes temporal context / sequence (time cells,
  Eichenbaum 2014; the same event-indexing machinery as SPACE). The default is narration-order = event-order, OVERRIDDEN
  by tense/aspect + connectives.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the exact representation of the order register (a magnitude line via
  the LANDED `transitive_ordering`? interval bookkeeping like the location register? a per-event order index?) and the
  threshold for an aspect/connective override. Copy the COMPUTATION (default narration order, overridden by tense/aspect +
  connectives → a per-event order model); SWEEP the representation. REUSE the extracted TENSE (event_bundle/situation_reader)
  + `transitive_ordering` (order primitive) + `graded_temporal_context` (the store clock) rather than re-parsing.
- **NOT brain-faithful:** assuming narration order == event order (ignores flashbacks/aspect — the thing to beat); a fixed
  tense→time lookup ignoring the reference-time context; an external LLM at inference (the invariant).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** `hdlab/situation_reader.py` parses VBD / VBN+had / VBN+be tense
  markers; `hdlab/event_bundle.py` encodes a per-event (PRED, AGENT, PATIENT, **TENSE**) tuple; `hdlab/graded_temporal_context.py`
  is the store's temporal-context clock (event-boundary drift); `hdlab/transitive_ordering.py` (LANDED this session) is a
  magnitude-line ORDER primitive. The COMPONENTS exist; grep finds NO organ that composes them into a temporal-order
  query ("before/after") or handles narration-order ≠ event-order.
- **INFERRED (to prove):** that composing the extracted tense/aspect + connectives into a per-event order register answers
  "before/after" on real narrative above the narration-order floor — OR that narration order already suffices (a rigorous
  negative closing whether the TIME dimension is a current cap).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-extract tense (situation_reader already parses VBD/VBN+had/VBN+be) or rebuild the event register. Do NOT
  rebuild the store clock (`graded_temporal_context`) or the order primitive (`transitive_ordering`) — REUSE them. Do NOT
  use an external LLM/temporal parser at inference. This is the COMPOSITION + the before/after TEST, not a new parser.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/situation_reader.py` (the VBD/VBN+had tense branches), `hdlab/event_bundle.py` (the TENSE slot),
  `hdlab/graded_temporal_context.py` (the clock), `hdlab/transitive_ordering.py` (the order primitive), and the SPACE
  organ (`situation_model_has_no_spatial_location_dimension` SOLVED — the sibling dimension's build pattern:
  construction-gold-isolates-the-mechanism + a real-prose serve). `tools/experiment_index.py query "tense"` / `"temporal"`
  / `"before"` / `"event order"`. Audit: the situation-model + event-indexing entries. **Mind the CORPUS-AGE confound**
  (archaic tense usage in LitBank/McGuffey; the sibling archaic-prose parse-check brief p8).
- Gold: a before/after event-order gold — a construction gold (real tense/connectives, by-construction order, incl.
  narration-order≠event-order cases) that ISOLATES the mechanism, PLUS a real-prose serve (mined past-perfect/connective
  cases; state how built + verified), mirroring the SPACE organ's triangulation.

## 7. THE BAR
PASSES only with ALL of:
1. **A per-event temporal-ORDER register** (built in `experiments/`): default narration order, OVERRIDDEN by the extracted
   tense/aspect + explicit connectives, answering `before(x, y)` / `order()`. Copy the computation; SWEEP the
   representation (reuse `transitive_ordering` / interval bookkeeping).
2. **Answers "did X happen before Y?" CI-separated over the NARRATION-ORDER floor** (assume telling order = event order,
   recomputed on the same population), on real narrative (or a construction gold that isolates the mechanism + a real-prose
   serve, like the SPACE organ). The **info-free twin** (shuffled tense labels / random order) LOSES CI-separated; report
   CI half-width + null p95; no number crosses populations. A **POSITIVE control** the floor CANNOT get: a past-perfect
   FLASHBACK ("she had left before he arrived") where narration order ≠ event order.
3. **SERVES or COMPOSES:** show the order model is real on prose (a mined past-perfect/connective serve) OR that it
   constrains a downstream inference (e.g. a cause must precede its effect) — wire-don't-island, not a second island.
4. **One-screen summary:** representation → narration-order floor → twin → before/after accuracy + the flashback control →
   verdict. Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "narration order == event order on ~99% of real prose; past-perfect flashbacks
are rare, so the TIME dimension is not a current cap" — with the flashback positive control confirming the metric can
move — closes whether to build it).

## 8. FILES AND ENTRY POINTS
- Reuse: `hdlab/situation_reader.py` (tense), `hdlab/event_bundle.py` (TENSE slot), `hdlab/graded_temporal_context.py`
  (clock), `hdlab/transitive_ordering.py` (order primitive). Pattern-from: the SPACE organ
  (`situation_model_has_no_spatial_location_dimension`). Data: LitBank / narrative corpora; a before/after gold. Audit +
  heavy→REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
The tense-extraction + TENSE slot + the store clock are EXISTING components to COMPOSE + credit, not to rebuild. The SPACE
organ is the sibling BUILD PATTERN to follow, not to reproduce. Strategy owns any hdlab landing — you propose the
temporal-order register + the before/after test, you do not write `hdlab/`.
