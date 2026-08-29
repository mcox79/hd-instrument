---
priority: 4
review:
review_text:
---

# PROBLEM: the reader's CAUSATION dimension (Zwaan event-indexing) is a PLACEHOLDER — `situation_reader._read_causation` / `experiments/_causal_network.py` link events by causal CONNECTIVES (because/since/so) + naive most-recent ADJACENCY + a COARSE "agonist force → result change-of-state" heuristic, and its own docstring admits the adjacency baseline "FAILS where cause ≠ most-recent". It cannot TYPE a causal relation (CAUSE vs ENABLE vs PREVENT), and it cannot represent a PREVENTED (counterfactual, never-happened) endstate at all. The brain types causation by FORCE DYNAMICS (Talmy 1988; Wolff 2007) — CAUSE/ENABLE/PREVENT fall out of a small DISCRETE truth-table over the affector/patient force configuration, LABELLING the edges of a causal network (Trabasso & van den Broek), with temporal precedence GATING (the just-integrated TIME register) and world-knowledge VALIDATING. Build the force-dynamic causal TYPER over the existing (agent, patient, predicate) extraction + a substrate-native force-dynamic verb lexicon, and validate it types CAUSE/ENABLE/PREVENT CI-separated over BOTH the connective/adjacency placeholder AND precedence-only, with the info-free (force-class-shuffled) twin losing.

**slug:** `causation_has_no_force_dynamic_typing` — **opened:** 2026-08-29 by the strategy session (the fully-scoped +
de-risked #1 next problem surfaced by the integrated `situation_model_has_no_tested_temporal_order_comprehension`,
owner-DONE/EXCELLENT — its TIME register handed causation the precedence gate it was missing, and a built probe already
shows the mechanism fires). **status:** OPEN — a MECHANISM + BUILD problem (the CAUSATION dimension of the situation
model). You build + validate in `experiments/`; strategy lands any hdlab change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `4` — HIGH leverage: of Zwaan's five event-indexing
> dimensions, CAUSATION is the LEAST genuinely built (SPACE + TIME are now real organs; causation is a connective/adjacency
> placeholder), and the TIME integration just handed it its missing ingredient (the precedence gate). It is de-risked (a
> built probe: the PREVENT-killer 1.000 vs placeholder 0.000; CAUSE-vs-ENABLE 1.000 where a verb-shuffle twin is at chance)
> and brain-foundational (force dynamics is the pinned mechanism; the wholesale-do-calculus route already HARD_FAILED).
> **Dependency web:** reuses the TIME before/after register (precedence gate) + the (agent, patient, predicate) extraction;
> a per-entity resultant-STATE register (the dropped "had been X" channel) is a sibling follow-on. **Re-rank per the owner.**

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
When a story says "the rain swelled the river, and the village flooded" vs "the open gates let the river through" vs "the
sandbags prevented the flood," a reader understands three DIFFERENT causal relations — the rain CAUSED the flood, the gates
merely ENABLED it, the sandbags PREVENTED it (and in the last case the flood NEVER HAPPENED). Our reader can't tell these
apart: it links events by cue words (because/so) and by "what came just before," and it has no way to represent an outcome
that was stopped from happening. The brain does this with FORCE DYNAMICS — it reads each event as a little contest of
forces (does the thing tend toward the outcome on its own? do the forces push together or against each other? did the
outcome actually happen?) and reads CAUSE / ENABLE / PREVENT straight off that. Build that force-dynamic causal typer.

## 2. WHY THIS ONE
Of the five things a situation model tracks (Zwaan: time, space, causation, goals, entities), CAUSATION is the LEAST
genuinely built — SPACE and TIME are now real, tested organs; causation is still a connective + most-recent-adjacency
placeholder whose own docstring says it "fails where cause ≠ most-recent." The just-integrated TIME register handed it the
missing ingredient (temporal precedence, which fixes causal direction: 1.000 vs 0.000 on flashback-causal). It is
de-risked — a built probe already shows the force-dynamic mechanism fires where the placeholder is at chance — and it is
brain-foundational, where the tempting wholesale-do-calculus route already HARD_FAILED once. This is the highest-leverage
next dimension.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation), three dissociable levels** (research drill; Kang et al. 2021 meta-analysis = left IFG + left
  MTG + bilateral mPFC):
  - **FORCE DYNAMICS (clause/lexical, the online cue)** — Talmy 1988; Wolff 2007. CAUSE/ENABLE/PREVENT fall out of a small
    DISCRETE truth-table over 3 (mostly binary) dims: (1) does the PATIENT tend toward the endstate on its own? (2) do
    affector & patient forces CONCUR or OPPOSE? (3) is the endstate REACHED? **CAUSE = (no, oppose, yes); ENABLE = (yes,
    concur, yes); PREVENT = (yes, oppose, NO endstate).**
  - **CAUSAL NETWORK (discourse)** — Trabasso & van den Broek 1985: events = nodes, edges = "necessity in the circumstances";
    force dynamics LABELS the edges (the network↔force-dynamics composition is OUR-SYNTHESIS — label it, not published).
  - **Precedence GATES; force dynamics TYPES; world-knowledge VALIDATES.** Precedence alone is the post-hoc fallacy.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the force-dynamic verb LEXICON coverage and the endstate-polarity
  threshold. **Copy the COMPUTATION** (the 3-dim force-dynamic truth-table over affector←agent / patient←patient); the
  verb's force class comes from a SUBSTRATE-NATIVE static lexicon (VerbNet → Event Force Dynamics, Kalm et al. 2019;
  FrameNet Causation family: Causation / Preventing_or_letting / Thwarting / Enabling); the endstate bit from narrative
  outcome polarity. SWEEP the lexicon + threshold; COPY the truth-table.
- **NOT brain-faithful:** the current connective + most-recent-adjacency + coarse heuristic placeholder (order-agnostic,
  cannot type, cannot represent a PREVENTED endstate); formal Pearl DO-CALCULUS routing (`exp_arc_schema_routing_do_calculus_v1`
  HARD_FAILED — importing statistical-interventional machinery wholesale already failed once); covariation (belongs to the
  OFF learner, needs repetition, not the online organ); an external LLM (the invariant).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** the live causal organ is a PLACEHOLDER (its docstring: adjacency
  "FAILS where cause ≠ most-recent"; grep-confirmed NO CAUSE/ENABLE/PREVENT typing exists). The TIME serve fixes causal
  DIRECTION (1.000 vs 0.000 on flashback-causal). The de-risking probe (`exp_causal_force_dynamics_probe_v1.py`):
  the PREVENT-killer 1.000 vs placeholder 0.000; CAUSE-vs-ENABLE 1.000 where a verb-shuffle twin is at chance. Prior
  landings: `exp_causal_correlational_disambig_v1` HARD_PASS (SIGN, not TYPE), `exp_causal_bitemporal_composition_v1`
  HARD_PASS (the TIME×causal composition reuse precedent), `exp_arc_schema_routing_do_calculus_v1` HARD_FAIL (do-calculus).
- **INFERRED (to prove):** that a force-dynamic typer beats BOTH the connective/adjacency placeholder AND precedence-only,
  CI-separated, on 3-way CAUSE/ENABLE/PREVENT typing — with the force-class-shuffle twin losing — OR a rigorous reason the
  force-dynamic lexicon's coverage/noise on narrative verbs caps it (a measured coverage bound, not asserted).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT build formal Pearl DO-CALCULUS routing (`exp_arc_schema_routing_do_calculus_v1` HARD_FAILED — the more
  brain-faithful force-dynamic route is the bet). Do NOT rebuild the TIME before/after register (REUSE it as the precedence
  gate). Do NOT use connective + most-recent adjacency as the mechanism (it IS the placeholder floor to beat). Do NOT build
  a covariation learner (wrong system — needs repetition, belongs to the OFF learner). REUSE the (agent, patient, predicate)
  extraction + a static force-dynamic verb lexicon (foundation-is-free-to-build).

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `situation_model_has_no_tested_temporal_order_comprehension/next_problem_scoping_causation_force_dynamics_2026-08-29.md`
  (the full scoping — truth-table, Set A/B/C, controls, gate, reuse/risk) + `exp_causal_force_dynamics_probe_v1.py` (the
  de-risking probe) + the research drill. Read `experiments/_causal_network.py` / `situation_reader._read_causation` (the
  placeholder), the TIME register (precedence gate) + `exp_causal_bitemporal_composition_v1` (the composition precedent).
  Run `tools/experiment_index.py query "causal"` / `"force"` / `"causation"` / `"prevent"` (SINGLE keywords). Audit: the
  newest §2b TIME + causal entries. **Mind the CORPUS-AGE confound** (archaic narrative verbs may not be in the force lexicon).

## 7. THE BAR
PASSES only with ALL of:
1. **A force-dynamic causal TYPER** (built in `experiments/`): the 3-dim truth-table (patient-tendency, concur/oppose,
   endstate-reached) → CAUSE/ENABLE/PREVENT, over the (agent→affector, patient) extraction + a substrate-native force-dynamic
   verb lexicon (VerbNet/FrameNet Causation family). Copy the computation; SWEEP the lexicon coverage + polarity threshold.
   NO do-calculus, NO external LLM.
2. **CI-separated 3-way accuracy over BOTH the placeholder AND precedence-only** (gated on the placeholder's upper CI, on the
   gold's own population) across: **Set A** — CAUSE/ENABLE/PREVENT connective-neutral minimal pairs; **Set B** — causal vs
   merely-sequential (connective-stripped, temporally-ordered); **Set C** — the PREVENT KILLER (the endstate never happens;
   requires a small NEGATION/polarity detector IN SCOPE, else Set C can't be scored). The **info-free twin** (shuffled verb
   force-classes) LOSES CI-separated; report CI half-width + shuffle-null p95; no number crosses populations.
3. **Controls (falsifiers):** FD-label SHUFFLE (permute force-classes → accuracy must fall to the placeholder, else it rode
   connective/order leakage); PRECEDENCE-ONLY (the TIME organ alone → force dynamics must ADD over it); frequency-matched
   random-label (≈ the placeholder — the typer must beat it CI-sep on Set A + Set C).
4. **One-screen summary:** force-classes → Set A/B/C floors → twin → 3-way lift → verdict. Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "a faithful force-dynamic typer beats the placeholder on Set A/C but the narrative
force-lexicon covers only X% of real verbs, capping it at Y — a measured coverage bound, with the PREVENT-killer confirming
the mechanism represents a prevented endstate the placeholder structurally cannot").

## 8. FILES AND ENTRY POINTS
- **Scoping + de-risk (REUSE, do not redo):** `situation_model_has_no_tested_temporal_order_comprehension/{next_problem_scoping_causation_force_dynamics_2026-08-29.md,
  adjacent_components_brain_fidelity_map_2026-08-29.md}`; `experiments/exp_causal_force_dynamics_probe_v1.py`;
  `experiments/exp_causal_bitemporal_composition_v1.py` (the TIME×causal reuse precedent).
- **Build over:** `experiments/_causal_network.py` / `situation_reader._read_causation` (the placeholder floor), the TIME
  before/after register (precedence gate), the (agent, patient, predicate) extraction; a static force-dynamic verb lexicon.
  Audit + heavy→REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
The probe numbers (PREVENT-killer 1.000 vs 0.000) are the de-risking MOTIVATION, not your result — build the full 3-way
typer and recompute the placeholder floor on YOUR population. Do NOT build do-calculus (HARD_FAILED) or re-solve the TIME
register. Strategy owns any hdlab landing — you propose the typer, you do not write `hdlab/`.
