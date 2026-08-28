---
priority: 6
review:
review_text:
---

# PROBLEM: the reader can COMPARE two things on a scale (p1) but cannot REASON over comparisons — build transitive-comparison / ordering (read pairwise "A > B, B > C" from text, build the magnitude ORDERING, answer the UN-STATED "A vs C"), the first REASONING operation, validated CI-separated over a no-ordering floor with an info-free twin losing

**slug:** `transitive_comparison_reasoning_over_the_magnitude_ordering` — **opened:** 2026-08-28 by the strategy session.
**status:** OPEN — **PROPOSED, owner steers.** The comprehension baseline is established (each reader axis validated + entity+meaning
compose + p1 comparison); this is the FIRST measurement/build of the NEXT phase (comprehension → REASONING). Owner decides whether
to open the reasoning phase now (vs after the in-flight learner/foraging/phase-diagram/ToM-reeval clear) and whether transitive
comparison is the right first operation. You build + validate in `experiments/`; strategy lands any hdlab change (Q111).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `6` (back of the queue, PROPOSED) — it opens a NEW phase, so
> it should not jump the in-flight work. It builds directly on the LANDED p1 ruler + the situation register. Re-rank / redirect per the owner.

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
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch (the parietal magnitude system; hippocampal
> relational/transitive inference); inherit its PINNED/INVENTED verdicts; put a short **AUDIT UPDATE** in your submission.

## 1. THE PROBLEM IN PLAIN LANGUAGE

We just gave the reader a "ruler" — it can compare two things on a scale ("which is more X?"). But reasoning needs more than one
comparison at a time: if a story says "the whale is bigger than the shark" and "the shark is bigger than the tuna," a reader should
know **the whale is bigger than the tuna** — even though the story never said so. That's *transitive inference*: read the pairwise
comparisons, build a single mental **ordering**, and answer the comparisons that were never stated. It's the first real step from
*comparing* to *reasoning*, and it's a capability young children and animals have that a lookup-only system does not.

## 2. WHY THIS ONE

It is the first genuine REASONING operation (not a re-run of the broad comprehension skills), it builds directly on the LANDED p1
ruler (the magnitude place code IS what an ordering is read from), and it is brain-foundational and cleanly testable. It also connects
two landed systems: the parietal magnitude code (p1) and the hippocampal RELATIONAL memory that supports transitive inference — a
chance to test whether the substrate's register can hold a transitive ordering.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)

- **PINNED — transitive inference is RELATIONAL memory + a magnitude ORDERING.** The hippocampus supports transitive inference by
  binding overlapping pairs into a unified relational structure (Dusek & Eichenbaum 1997; Zeithamova & Preston) — you don't store
  "A>B, B>C" as isolated facts, you INTEGRATE them into one ordering A>B>C. The parietal magnitude system represents the ordering as
  a POSITION on a mental line (the symbolic-distance effect: the farther apart on the order, the FASTER/easier the judgment — the same
  Moyer distance effect p1 already showed for adjectives). So the read-out is: place each item on ONE magnitude axis, compare positions.
- **PINNED — the integration is by OVERLAP, not by explicit logic.** The shared middle term (B) is what lets A and C be related; the
  brain does this by the overlapping bindings sharing a component, not by a symbolic transitivity rule. Our substrate's binding/register
  is the candidate mechanism (bind each item to its ordinal position; overlapping comparisons constrain the positions).
- **OUR-INVENTION-UNDER-TEST:** the exact mechanism to build the ordering from pairwise text comparisons (a magnitude-code placement,
  a relational-register integration, or a graded settling). COPY the computation (integrate overlapping pairs → one ordering →
  position-compare), SWEEP the parameters. Do NOT hard-code a symbolic sort and call it brain-faithful — the test is whether a
  substrate-native mechanism (magnitude placement / relational binding) produces the ordering + the distance effect.

## 4. MEASURED vs INFERRED
- **MEASURED (p1, landed):** the ruler compares TWO items on a scale (adjective comparison 0.758 vs incumbent 0.552; the Moyer distance
  effect +0.34). It does NOT build an ordering from multiple comparisons or answer un-stated pairs.
- **INFERRED (to test):** a brain-faithful mechanism reads pairwise comparisons from text, integrates them into ONE magnitude ordering,
  and answers UN-STATED transitive pairs (A vs C) CI-separated over a no-integration floor, showing the symbolic-distance effect
  (far pairs easier than near pairs). UNPROVEN — could be null (the substrate can't hold a transitive ordering) — a valid PASS.

## 5. ALREADY TRIED / DO NOT RE-RUN
- p1's two-item comparison (the ruler) is the BUILDING BLOCK, not the target — do not rebuild it; build the ORDERING + transitive query ON it.
- Do NOT re-open the within-pair comparison or the adjective-magnitude channel (p1 did those).

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/scalar_adjective_operation.py` (the p1 ruler: `oriented_position`/`compare` — the magnitude place code you build the
  ordering from) + the p1 SOLVED (the distance effect + congruity).
- Read `hdlab/situation_model_accumulate.py` + `hdlab/binding.py` (the relational register / binding, the candidate integration mechanism).
- Read `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (magnitude system; relational memory).

## 7. THE BAR
PASSES only with ALL of:
1. **Answers UN-STATED transitive pairs CI-separated over a no-integration floor:** read pairwise comparisons (from text or a controlled
   set), build the ordering, and predict the sign of UN-STATED pairs (A vs C, never compared directly) better than a floor that only
   uses the STATED pairs (no integration) — recompute the floor; info-free twin (shuffled comparisons / random ordering) LOSES CI-sep;
   report CI half-width + null p95. NO number crosses populations/scorers.
2. **Brain-faithful mechanism:** the ordering is built by INTEGRATING overlapping comparisons into one magnitude structure (place-code
   placement or relational binding), NOT a hard-coded symbolic sort. State the operation. Show the SYMBOLIC-DISTANCE EFFECT (far
   un-stated pairs answered better/more-confidently than near ones) — the signature that it's a magnitude ordering, not pair lookup.
3. **Substrate-native:** built on the LANDED p1 ruler + the register/binding (COPY the computation, SWEEP the params).
4. **Propose the exact hdlab diff** (the ordering-builder + transitive read-out) for strategy to land, default-off.
A rigorous NEGATIVE — a faithfully-built substrate mechanism CANNOT hold a transitive ordering / does not beat the no-integration floor —
is a FULL PASS, localising why (the register can't bind ordinal positions / the magnitude code doesn't integrate overlapping pairs).

## 8. FILES AND ENTRY POINTS
- Building block: `hdlab/scalar_adjective_operation.py` (the ruler), `hdlab/situation_model_accumulate.py` + `hdlab/binding.py` (relational integration).
- Gold: a controlled transitive-comparison set (pairwise comparisons + held-out un-stated transitive pairs); optionally mine comparative
  sentences ("bigger/faster/older than") from a corpus. Absolute-magnitude norms can anchor a real-world ordering.
- **Route heavy runs to the REMOTE GPU box** (`tools/queue_add.py`).
- Audit: `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (magnitude system; relational memory).

## DO NOT QUOTE / DO NOT REDO
p1's two-item comparison (0.758) is the building block, not a result to reproduce. Do NOT hard-code a symbolic sort and call it
brain-faithful — the test is a substrate-native ordering (magnitude placement / relational binding) with the distance effect. Strategy
owns the hdlab landing — you propose the diff, you do not write `hdlab/`.
