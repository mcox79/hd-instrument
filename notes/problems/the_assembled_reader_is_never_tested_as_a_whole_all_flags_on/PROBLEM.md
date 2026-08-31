---
priority: 4
review:
review_text:
---

# PROBLEM: we have never tested the ASSEMBLED reader as a WHOLE. Each validated dimension is wired into `hdlab.situation_reader` behind a DEFAULT-OFF flag (`tense_agnostic_events`, `causation_typed`, `timeline_register`, `role_route`, …) and each is verified ONLY in ISOLATION (equivalence to its own validated organ, byte-identical when off). NOTHING turns them ALL on together and measures the reader end-to-end — and the QA capstone (`exp_situation_model_qa_v1`), our supposed end-to-end instrument, runs `SituationReader(gaz=gaz)` = the DEFAULT reader with every capability OFF. So (a) we have validated the PARTS but never the WHOLE, (b) flag INTERACTIONS are entirely unmeasured (does tense-agnostic detection change causation's inputs? does the whole compose or interfere?), and (c) every solver who measures a floor/baseline against "the reader" is measuring the artificially-WEAK default. Build the full-system end-to-end harness: run the reader with ALL validated dimension flags ON, on real narrative, measure each dimension WITH the others live, quantify the interactions, and establish the FULLY-ON reader as a measured, validated whole — the actual "complete substrate."

**slug:** `the_assembled_reader_is_never_tested_as_a_whole_all_flags_on` — **opened:** 2026-08-31 by the strategy
session (owner questions: "do solvers understand the substrate on/off states? are we testing the full system end to
end yet?" — answer to the latter was NO). **status:** OPEN — a HARNESS + MEASUREMENT problem (build the end-to-end
test; strategy owns any hdlab default-flip Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `4` — HIGH. It is the VALIDATION GATE for the
> whole assembly program: every dimension we land (causation + time done; belief/space/state/roles queued) is
> unproven AS A WHOLE until this exists, and it directly de-risks EVERY other solver's baselines (they should
> measure against the correct reader state — see `python tools/reader_capabilities.py`). Ranked below the learner-on
> capstone (p1) + the parser (p2) but it is a prerequisite to trusting the assembled reader the learner grows on.
> ⚠️ It is verdict-INDEPENDENT and safe to start now. Re-rank per the owner.

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
We have been adding abilities to the reader one at a time, each behind an off-by-default switch, and testing each one
by itself. We have never turned them all ON at once and read a story with the whole thing running. So we do not
actually know that the finished reader works — only that each part works alone. Worse, whenever anyone measures "how
good is the reader," they measure the default reader with everything switched OFF, which is the weakest possible
version. Build the test that turns everything on, reads real stories, checks that each ability still works with the
others running (and does not quietly break another), and reports how good the WHOLE reader is. If turning things on
together makes something worse, that is a real and important finding — say exactly what interferes with what.

## 2. WHY THIS ONE
It is the validation gate for the entire assembly program. We are landing dimension after dimension on the promise
of "an ever more complete substrate," but "complete" is unproven until the complete thing is measured. It is also a
correctness lever for every other problem: solvers currently measure against the wrong (default) reader; a measured,
documented FULLY-ON reader gives everyone the right baseline. And the learner-on capstone will grow the reader's
knowledge — we must know the reader it grows on actually holds together.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate):** comprehension is a SINGLE integrated situation model with multiple simultaneously-active
  dimensions — WHO/WHAT/WHEN/WHERE/WHY/BELIEF are bound into one evolving representation, not computed in isolated
  passes (Zwaan & Radvansky 1998 event-indexing situation model; the dimensions co-constrain each other online).
  The right test of a multi-dimensional model is JOINT, not per-dimension. Interactions are the POINT: e.g. better
  event detection (WHO/WHAT) should feed causation (WHY) and time (WHEN); if it does not, that is a wiring gap.
- **OUR-INVENTION (this harness):** the specific joint-measurement design (which real corpus, which per-dimension
  golds run simultaneously, the interaction/ablation matrix), the "fully-on" flag configuration, and the aggregate
  comprehension score. Do NOT re-derive the per-dimension numbers — INHERIT each dimension's own validated result
  and re-measure it WITH the others on.

## 4. MEASURED vs INFERRED
- **MEASURED (in isolation — the parts):** each dimension flag has a passing witness proving it reproduces its
  validated organ when turned on ALONE, byte-identical when off (`tense_agnostic_events` recall 0.33→0.95;
  `causation_typed` AUTO 0.833; `timeline_register` == the register's order; `role_route` who-did-what +0.253). See
  `python tools/reader_capabilities.py` for the live flag/default manifest.
- **INFERRED (you must measure — the whole):** whether, with ALL flags ON on real narrative, (a) each dimension
  still reproduces (within CI) its isolated result — NO cross-dimension REGRESSION; (b) the interactions are as
  predicted (better extraction feeds causation/time); (c) an aggregate comprehension score (e.g. the QA capstone
  re-run FULLY-ON vs the default reader) improves CI-separated; (d) any interference is named and localized.

## 5. ALREADY TRIED / DO NOT RE-RUN
- The per-dimension witnesses (`test_tense_agnostic_events_organ`, `test_causation_typed_landing_organ`,
  `test_timeline_register_landing_organ`, the role_route / QA capstone cells) — INHERIT their isolated results; do
  NOT re-derive them. This problem is the JOINT run.
- The QA capstone (`exp_situation_model_qa_v1`) — it currently runs the DEFAULT reader; RE-RUN it FULLY-ON as the
  aggregate instrument (do not rebuild it from scratch).

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Run `python tools/reader_capabilities.py` (the flag/default manifest) and `--enable` (the fully-on kwargs). Confirm
  on disk which flags exist + their defaults by reading `hdlab/situation_reader.py::__init__`.
- Read the per-dimension witnesses (the isolated results to inherit) + `exp_situation_model_qa_v1` (the aggregate
  instrument to re-run fully-on). MIND: `role_route`'s ON value is a string — verify the accepted value.

## 7. THE BAR (can-fail; a rigorous NEGATIVE is a full PASS)
On real narrative (LitBank; add a modern held-out set if reachable), with the reader built FULLY-ON:
- **PASS =** (1) NO-REGRESSION — each dimension, measured WITH all flags on, reproduces its isolated validated result
  within CI (no CI-separated drop vs its solo witness); (2) AGGREGATE — the FULLY-ON reader beats the DEFAULT reader
  on an end-to-end comprehension score (the QA capstone re-run) CI-separated, with the info-free control (a
  flags-on-but-shuffled variant) not helping; (3) INTERACTION MAP — a flag-ablation matrix (each flag on/off) that
  quantifies the marginal + joint contribution and NAMES any interference; report CI half-width + null p95, no
  number crossing populations.
- **A rigorous NEGATIVE is a full PASS:** if turning flags on together REGRESSES a dimension or the whole is not
  better than the parts, report exactly which flags interfere and why (the wiring gap) — that is the single most
  important thing this test can find, and it tells the assembly what to fix before landing more dimensions or
  flipping any default ON.

## 8. FILES AND ENTRY POINTS
- Build the harness in `experiments/`: construct the FULLY-ON `SituationReader(...)` (see `tools/reader_capabilities.py
  --enable`), read real docs, run each dimension's scorer + the QA capstone jointly, emit the interaction matrix.
  Witness recomputes the no-regression + aggregate + interaction results from source. Fold an **AUDIT UPDATE** into
  `BRAIN_FOUNDATIONAL_AUDIT.md` §2b. If the whole holds, strategy uses the evidence to consider flipping validated
  flags ON by default (Q111, a measured decision, not automatic). This is the assembly's validation gate + the
  correct-baseline reference for every other problem.


## DO NOT QUOTE / DO NOT REDO
- 🚫 No result yet — OPEN. Do NOT quote any per-dimension isolated number as the WHOLE-reader result (that is exactly what this problem exists to measure). Inherit each dimension's isolated witness; do not re-derive it. Recompute floors on the item's own population.
