---
priority: 1
review:
review_text:
---

# PROBLEM: TURN THE LEARNER ON — and prove, deeply and methodically, that letting the reader grow its own knowledge by reading makes it measurably better at COMPREHENSION without corrupting what it already had right. The learner has been deliberately OFF because the foundation was too noisy. That objection is now removed: BOTH clean-foundation halves are solved and integrated — extraction-IN (`the_extraction_front_end…`, EXCELLENT, LANDED: event recall 0.33→0.95) and consistency-of-STORED (`the_knowledge_store_has_no_correctness_or_consistency_cleanup`, EXCELLENT: schema-congruence cleanup detects wrong facts the source-trust gate cannot). And the SAFE-GROWTH mechanism is already VALIDATED (`optimize_and_validate_the_learner_before_it_grows_the_foundation`, EXCELLENT: naive growth corrupts ~25.6% of correct answers, but a CLS keep-both-stores ensemble cuts that to 7.85% while keeping 71% of a +0.078 downstream comprehension gain). This problem is the CAPSTONE: wire the safe-growth switch onto the CLEAN foundation, turn it ON behind the safety gate, and VERIFY end-to-end — with the full control suite, honest corruption accounting, generalization, and a rollback gate — that the on-state is BOTH safe AND beneficial. A rigorous NEGATIVE (it is NOT yet net-beneficial or NOT yet safe on the real clean foundation) is a FULL PASS: it says "not yet — and precisely which sub-condition failed, and why."

**slug:** `turn_on_the_learner_and_verify_safe_growth_on_the_clean_foundation` — **opened:** 2026-08-31 by the strategy
session (owner directive: "create a problem to specifically turn on the learner, test it, verify it deeply and
methodically"). **status:** OPEN — the North-Star CAPSTONE (a wire + deep-verify problem, not a from-scratch build:
the pieces are validated; this is turning them on TOGETHER on the clean foundation and proving the on-state). You
build + validate in `experiments/`; strategy lands the hdlab change (Q111, default-off until the evidence says flip).
NO external LLM at inference (the invariant). The learner UPDATE stays glass-box.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `1` — this is the mission's payoff. Everything the
> substrate does (clean extraction, consistency cleanup, the assembly) has been in service of a reader that gets
> smarter by reading. The foundation gate is now cleared, so this is the highest-value open problem. ⚠️ It is
> RESPONSIBLE-by-construction: the growth switch stays DEFAULT-OFF; you produce the EVIDENCE that justifies flipping
> it, and the safety gate (bounded corruption + rollback) is part of the deliverable, not an afterthought.
> ⚠️ PARTIAL PREREQUISITE (does NOT block starting): the structured-context learner channel is gated on parse
> quality; `wire_the_incremental_parser…` (p2, SOLVED, awaiting owner review) will improve it. Start with the current
> parser (`arc_parser`), report the number, and note it will rise with the better parser — do NOT wait.

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
We have always wanted a reader that gets smarter by reading. We proved it can learn, and we found a safe way to let
it learn without forgetting (keep the old memory alongside the new one). We kept the switch OFF on purpose, because
the facts it would learn from were too messy. We have now cleaned both the way facts come IN and the facts already
STORED. So it is time to actually flip the switch — carefully. Turn on "grow by reading," run it on the clean
foundation, and prove two things at once, deeply: (1) SAFE — it does not wreck things it already knew (measure the
exact fraction it breaks, and be able to roll back a bad update); (2) BETTER — it measurably improves the reader's
comprehension, and that improvement is real learning, not just "more words seen" (the fake-growth controls must not
help). If it is not yet safe-and-better on the real clean foundation, say so and say exactly why — that is a full
pass and tells us what still has to change.

## 2. WHY THIS ONE
It is the mission's payoff and the foundation gate is finally cleared. Every prior piece was in service of this:
clean extraction (so it learns from correct events), consistency cleanup (so it does not learn contradictions), the
safe-growth mechanism (so it does not forget). Turning it on — responsibly, with proof — is the point of the whole
program. And doing it DEEPLY matters: an under-verified "it works" here would be the worst possible false positive,
because it would let a self-modifying store corrupt the foundation everything else stands on.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate):** COMPLEMENTARY LEARNING SYSTEMS (McClelland, McNaughton & O'Reilly 1995; Kumaran, Hassabis
  & McClelland 2016): a fast hippocampal store learns specifics quickly; a slow neocortical store integrates them
  GRADUALLY via INTERLEAVED REPLAY, which is precisely what prevents catastrophic forgetting. Growing the slow store
  by reading must be SLOW + REPLAY-INTERLEAVED + KEEP-BOTH-STORES, not a wholesale overwrite. Systems consolidation
  over-writes toward the schema/gist, protecting consistent knowledge (Winocur & Moscovitch) — which is exactly the
  consistency-cleanup organ (p4) acting as the schema gate on what may consolidate. The learner's UPDATE lever is
  the CONTEXT it learns over (grammatical relations), not the update rule (SGNS==shifted-PPMI; online==batch — a
  proven equivalence, do NOT re-litigate it).
- **OUR-INVENTION (sweep, don't adopt):** the keep-both-stores fusion rule (ENSEMBLE_MEAN vs rate-limited gradual
  blend α), the growth rate / replay schedule, the rollback/consolidation-eligibility gate (which reads may consolidate
  — a natural home for the p4 consistency score + the prediction-error/novelty gate), and the comprehension metric.

## 4. MEASURED vs INFERRED
- **MEASURED (the validated pieces you build ON — do NOT re-derive):** from `optimize_and_validate…` (owner-DONE,
  EXCELLENT): (a) the dependency-typed structured-context learner beats the ±2-window PPMI-SVD baseline on SIMILARITY
  CI-separated (SimLex 0.2699 vs 0.2102, +0.0598; SimVerb 0.1186 vs 0.0844), ~2.5× data-efficient; (b) growing the
  reader's meaning by reading 5M→15M tokens improves downstream LitBank who-did-what comprehension 0.0714→0.1494
  (+0.078 CI-sep) and it is REAL structure (info-free growth controls — full-corpus shuffle 0.0112, filler-shuffle
  0.0166 — fall BELOW baseline); (c) NAIVE growth corrupts ~25.6% of previously-correct answers (uniform across
  confidence = genuine knowledge loss); (d) a CLS keep-both-stores ENSEMBLE_MEAN cuts corruption to 7.85% (−0.177
  CI-sep) keeping 71% of the gain, and a rate-limited gradual blend (α=0.25) keeps 84% at 18.5% corruption —
  accuracy saturates at α=0.25 while corruption climbs monotonically toward the naive value (the CLS signature). And
  from p1 (extraction recall 0.33→0.95, landed) + p4 (consistency cleanup, schema-congruence) — the foundation is now
  demonstrably cleaner both in and stored.
- **INFERRED (you must measure — the on-state on the CLEAN foundation):** whether growth ON, behind the CLS
  keep-both-stores gate, run on the NOW-CLEAN foundation (fed by the landed tense-agnostic extraction; the p4
  consistency score gating consolidation eligibility), yields a downstream comprehension gain CI-separated over
  growth-OFF, WITH corruption bounded below an explicit, pre-registered acceptable rate, AND the info-free growth
  twin not helping, AND a working rollback on a regressing update. Does cleaning the foundation (vs the noisy store
  the safe-growth work used) CHANGE the corruption/gain tradeoff — ideally lowering corruption further?

## 5. ALREADY TRIED / DO NOT RE-RUN
- `optimize_and_validate_the_learner_before_it_grows_the_foundation` (owner-DONE, EXCELLENT) — the safe-growth
  mechanism + the structured-context learner + the corruption/gain tradeoff are PROVEN there. BUILD ON it (import its
  cells: `exp_growth_cls_ensemble_v1`, `exp_learner_safety_gate_v1`, `exp_structured_context_learner_v1`). Do NOT
  re-derive online==batch (SGNS==shifted-PPMI, Levy & Goldberg 2014 — a landed negative) or re-run the naive-overwrite
  baseline as if it were new.
- The consolidation READ-OUT / replay-schedule negatives (`the_consolidated_cortical_store_is_written_but_never_read`;
  `one_store_does_two_jobs…` — selective replay does not beat uniform) — inherit their verdicts; the lever is
  keep-both-stores + sparse coding, not a cleverer replay schedule.
- The equal-weight meaning fusion (a landed HARM) — if you fuse the learned channel, use RELIABILITY/precision-
  weighting (the validated combiner), never equal-weight.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `notes/LEARNER_ON_ROADMAP.md` (the whole chain + the safety gate) and the `optimize_and_validate…` SOLVED
  (the validated numbers + the BAR-5 proposed hdlab diff). Read the p4 SOLVED (the consistency score you can use as
  the consolidation-eligibility gate) and confirm p1's tense-agnostic extraction is the feed.
- Confirm on disk which pieces are hdlab vs experiment (the safe-growth mechanism landed NO hdlab change — it is a
  proposed diff; the structured-context channel + reliability fusion are the meaning-fusion extension).

## 7. THE BAR (can-fail; deep + methodical; a rigorous NEGATIVE is a full PASS)
Turn the learner ON (CLS keep-both-stores growth, default-off switch) on the CLEAN foundation and PROVE, end-to-end:
- **PASS =** ALL of: (1) BENEFICIAL — a DOWNSTREAM comprehension score (who-did-what and/or a second held-out
  comprehension task, NOT just intrinsic word-similarity) improves growth-ON vs growth-OFF, CI-separated (bootstrap;
  CI half-width + null p95); (2) REAL — the info-free growth twin (grow on token-shuffled / non-text / random
  co-occurrence) does NOT help (ideally hurts), CI-separated; (3) SAFE — the corruption rate (fraction of
  previously-CORRECT answers flipped wrong by growth) is measured with a CI and stays below an explicit,
  PRE-REGISTERED acceptable bound, and it is NOT confidence-separable churn (report the confidence split); (4)
  ROLLBACK — a regressing update can be detected against a held-out probe and rolled back (the safety gate is real,
  not decorative); (5) CLEAN-FOUNDATION EFFECT — report whether the clean foundation (p1 extraction + p4 consistency
  gating consolidation eligibility) changes the gain/corruption tradeoff vs the noisy-store baseline from
  `optimize_and_validate` (the hoped-for result: lower corruption at equal gain). NO number crosses tasks/scorers;
  every floor recomputed per population.
- **A rigorous NEGATIVE is a full PASS:** if turning it on is NOT yet net-beneficial (the gain does not survive on
  the clean foundation) OR NOT yet safe (corruption cannot be held below an acceptable bound without killing the
  gain), report it precisely — which of (1)–(5) failed, the measured tradeoff curve, and the specific missing
  mechanism — so the safety gate stays OFF for a named reason. That is the responsible outcome and a full pass.

## 8. FILES AND ENTRY POINTS
- Build in `experiments/` on top of the validated cells (`exp_growth_cls_ensemble_v1`, `exp_learner_safety_gate_v1`,
  `exp_structured_context_learner_v1`); feed from the landed tense-agnostic extraction; gate consolidation eligibility
  with the p4 consistency score. Witness recomputes the gain + corruption + twin + rollback from source. Fold an
  **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b. Strategy lands the hdlab change (Q111): the CLS keep-both-
  stores safe-growth switch + the reliability-weighted meaning-fusion extension + the structured-context channel,
  ALL DEFAULT-OFF, with the flip-on evidence in hand — coordinate with the learner-on landing program (a large
  coordinated diff; see the roadmap). This is Link 5 (SAFE GROWTH) of the learner-on chain — the capstone.
