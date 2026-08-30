---
priority: 4
review:
review_text:
---

# PROBLEM: the reader tracks WHO believes WHAT (theory-of-mind: `hdlab/belief_partition.py`, integrated — an agent's belief state + the observation cue that updates it) AND it orders events in TIME (the integrated `temporal_order_register`: before/after, flashbacks) — but it does NOT COMPOSE them into a BELIEF TIMELINE: it cannot answer "what did agent A know AT THIS POINT in the story?" A belief is a function of what an agent has OBSERVED BY a given time; a FALSE belief is a belief formed before an unobserved change ("Sally thinks the ball is in the basket, because she left the room BEFORE it was moved to the box"). Without composing belief-updates with the event ORDER, the reader can hold a single current belief per agent but cannot reason about a STALE belief, dramatic irony, or deception — the core of narrative theory-of-mind. Build a per-agent BELIEF TIMELINE — each agent's knowledge state over reading-time, updated when (and only when) that agent OBSERVES an event, ordered by the temporal-order register — and validate it answers "where does A think X is?" / "does A hold a false belief here?" on false-belief-over-time narrative CI-separated over a TIMELINE-AGNOSTIC belief floor (current-belief-only) with the info-free twin (shuffled observation order) losing.

**slug:** `the_reader_has_no_belief_timeline_what_an_agent_knew_when` — **opened:** 2026-08-29 by the strategy session (the
GOALS/ToM × TIME composition gap named in the integrated `situation_model_has_no_tested_temporal_order_comprehension`'s
5-dimension map: "compose the TIME register with the belief timeline — what an agent knew at time T"). **status:** OPEN — a
MECHANISM + BUILD problem (composes two integrated organs). You build + validate in `experiments/`; strategy lands any
hdlab change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `4` — HIGH value and de-risked: it COMPOSES two
> already-integrated organs (belief_partition ToM + the temporal-order register) into the core narrative theory-of-mind
> reasoning capability (false belief, dramatic irony, deception — all "what did A know WHEN"), which prior ToM work
> proved only as a SINGLE current belief, not over time. A reasoning-frontier capability that generalises far beyond
> Sally-Anne. Ranked with the other dimension-composition builds, below the in-flight assembly (p3). **Dependency web:**
> consumes `belief_partition` (the observation cue) + the TIME register (event order); composes with the ENTITY /
> location dimensions (belief is often about WHERE something is). **Re-rank per the owner.**

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
Understanding a story means tracking not just what's true, but what each character *thinks* is true — and that changes as
they see (or miss) things happen. "Sally puts the ball in the basket and leaves. While she's gone, Anne moves it to the
box. Sally comes back — where does she look?" A reader knows Sally looks in the basket, because she believes what was true
*when she last saw it*, and she missed the change. Our reader can track a character's current belief and it can order the
events in time, but it can't put those together — it can't say "what did Sally know *at this point*?" So it can't handle a
stale belief, dramatic irony ("the reader knows, but the character doesn't"), or deception. Build a per-character *belief
timeline* — what each character knows across the story, updated only when they actually witness something — and show it
answers "where does she think it is / does she have a false belief here?" that a reader without the timeline gets wrong.

## 2. WHY THIS ONE
It is the named GOALS/ToM × TIME composition gap: both ingredients are already integrated organs, and prior ToM work
established only a SINGLE current belief, explicitly flagging "what an agent knew WHEN" as uncomposed. False-belief-over-
time is the canonical theory-of-mind reasoning task (Sally-Anne, Wimmer & Perner 1983) and it generalises to dramatic
irony, surprise, and deception — a broad reasoning capability, not a narrow patch. It also composes with the ENTITY/SPACE
dimensions (a belief is usually about WHERE something is), so it strengthens the whole situation model.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** the brain represents others' knowledge states and updates them by OBSERVATION over time
  (theory-of-mind — Baron-Cohen; Wimmer & Perner 1983 false belief; Apperly & Butterfill two-systems). An agent's belief
  about a fact is set by what they OBSERVED and PERSISTS (possibly stale) until they observe a change; a FALSE belief is a
  belief formed BEFORE an unobserved change — the "when did they last witness it" computation over the event order (the TPJ
  for belief attribution; the situation model's ENTITIES-over-time bookkeeping). Observation-gating is the crux: an agent
  only updates on events they were present for.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the belief-timeline REPRESENTATION (per-agent belief intervals) and
  any staleness/confidence threshold. **Copy the COMPUTATION** (per-agent belief updated ONLY on observed events, ordered
  by the temporal-order register; a false belief = last-observed-value ≠ current-true-value); **reuse** `belief_partition`
  (the observation cue that says whether an agent witnessed an event) + the `temporal_order_register` (the event order);
  SWEEP the representation + threshold.
- **NOT brain-faithful:** a single timeline-agnostic "current belief" per agent (no staleness — the current floor); a belief
  that updates on events the agent did NOT observe (omniscient — the failure mode false belief exposes); an external LLM.

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** `belief_partition` (ToM, integrated from
  `theory_of_mind_residual_is_the_observation_cue_front_end` + `theory_of_mind_is_proven_only_in_a_synthetic_microworld`) —
  the observation cue + belief partition; the `temporal_order_register` (integrated,
  `situation_model_has_no_tested_temporal_order_comprehension`, EXCELLENT) — before/after + flashback ordering. The 5-dim
  map names this composition as unbuilt.
- **INFERRED (to prove):** that composing them into a per-agent belief timeline (observation-gated updates ordered by the
  register) answers false-belief-over-time queries CI-separated over a timeline-agnostic current-belief floor, with the
  info-free twin (shuffled observation/event order) LOSING — OR a rigorous reason the composition doesn't help on real
  narrative (e.g. explicit false-belief scenes are rare — quantify the incidence).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT rebuild `belief_partition` (ToM, integrated — REUSE its observation cue) or the temporal-order register (integrated
  — REUSE its ordering). Do NOT validate ONLY on the synthetic microworld (prior ToM work already did — this problem's
  point is the TIME composition on narrative false-belief). Do NOT let an agent update on unobserved events (the omniscient
  bug false belief is designed to catch). REUSE both organs; the deliverable is the COMPOSITION + its measurement.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/belief_partition.py` + `theory_of_mind_residual_is_the_observation_cue_front_end/SOLVED.md` (the observation
  cue) + `theory_of_mind_is_proven_only_in_a_synthetic_microworld/SOLVED.md` (the ToM population + its single-belief limit)
  + the `temporal_order_register` (integrated) + `situation_model_has_no_tested_temporal_order_comprehension/adjacent_components_brain_fidelity_map_2026-08-29.md`
  (the GOALS/ToM × TIME gap). Run `tools/experiment_index.py query "belief"` / `"falsebelief"` / `"theoryofmind"` /
  `"observation"` (SINGLE keywords). Audit: the newest §2b ToM + TIME entries. **Mind the CORPUS-AGE confound** on any
  real-narrative false-belief population.

## 7. THE BAR
PASSES only with ALL of:
1. **A per-agent BELIEF TIMELINE** (built in `experiments/`): each agent's belief about a tracked fact (e.g. an object's
   location) over reading-time, updated ONLY on events the agent OBSERVED (via `belief_partition`'s observation cue),
   ordered by the `temporal_order_register`; a false belief = last-observed-value ≠ current-true-value. Copy the
   computation; SWEEP the representation + threshold. NO external LLM.
2. **Answers false-belief-over-time queries CI-separated over the timeline-agnostic floor** — a false-belief population
   (Sally-Anne-style constructed pairs AND/OR real narrative false-belief scenes): "where does A think X is?" / "does A
   hold a false belief here?"; the floor = a timeline-agnostic CURRENT-belief tracker (or last-mention) recomputed on the
   same population. The **info-free twin** (shuffled observation/event order — so the "when they last saw it" signal is
   destroyed) LOSES CI-separated; report CI half-width + null p95; no number crosses populations. A **POSITIVE control** the
   metric can move (a scene where A's belief is stale because A left BEFORE the change, which the current-belief floor misses).
3. **Isolates the TIME composition** — hold the belief-partition/observation cue fixed and show the lift is the TIMELINE
   (order-aware) part, not a better observation cue (an ablation to the timeline-agnostic tracker with the SAME cue).
4. **One-screen summary:** population → floor → twin → false-belief lift → incidence on real narrative → verdict. Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "the belief timeline recovers X of false-belief scenes CI-sep over the current-
belief floor on constructed pairs, but explicit false-belief scenes occur Y times in real narrative, bounding the aggregate
lift — with the positive control confirming the mechanism").

## 8. FILES AND ENTRY POINTS
- **Compose (integrated — REUSE, do not rebuild):** `hdlab/belief_partition.py` (the observation cue + belief partition);
  the `temporal_order_register` (integrated). **Motivation:** `situation_model_has_no_tested_temporal_order_comprehension/adjacent_components_brain_fidelity_map_2026-08-29.md`
  (the GOALS/ToM × TIME gap); the two ToM SOLVEDs (the single-belief limit). Audit + heavy→REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
The integrated ToM + TIME wins are the INGREDIENTS, not your result — the deliverable is the COMPOSITION (the belief
timeline) and its false-belief-over-time measurement over the current-belief floor. Do NOT rebuild belief_partition or the
temporal-order register, or validate only on the synthetic microworld. Strategy owns any hdlab landing.
