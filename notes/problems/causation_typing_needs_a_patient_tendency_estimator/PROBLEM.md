---
priority: 7
review:
review_text:
---

# PROBLEM: the integrated force-dynamic causal typer (`hdlab/force_dynamics_typer.py`) reads CAUSE/ENABLE/PREVENT from the VERB's force class — but for TENDENCY-AMBIGUOUS verbs (open/move/turn/roll…) the class is NOT in the verb: "the key opened the gate" is ENABLE (the key permits; the gate was disposed to open) while "the wind opened the gate" is CAUSE (the wind overcame the gate's disposition to stay shut) — SAME verb, opposite type. Wolff's truth-table needs a third input the typer currently lacks: does the PATIENT tend toward the outcome on its own? The causation integration MEASURED that a verb lexicon is capped at 0.500 there (vs a tendency-oracle 1.000) AND PROVED a glass-box recovery: Wolff's force ARITHMETIC reads patient-tendency from the AFFECTOR MAGNITUDE already in the sentence — a WEAK affector that still succeeds (a nudge, a breeze) means the patient contributed → ENABLE; a STRONG affector (a winch, a heave) means it overcame the patient → CAUSE — lifting 0.500 → 1.000 with the magnitude-shuffle twin at chance and generalization to held-out affectors (a mechanism DEMONSTRATION, not the full organ). Build the full PATIENT-TENDENCY estimator — affector-magnitude (proven first term) + patient-affordance + directional cues → a glass-box patient-tends-yes/no signal feeding the Wolff typer — and validate it types CAUSE-vs-ENABLE for tendency-ambiguous verbs CI-separated over the lexicon-only floor (0.500) toward the oracle (1.000) with the info-free (magnitude/affordance-shuffle) twin losing.

**slug:** `causation_typing_needs_a_patient_tendency_estimator` — **opened:** 2026-08-29 by the strategy session (the #1
HIGH-leverage adjacency named by the integrated `causation_has_no_force_dynamic_typing`, owner-DONE/EXCELLENT: it PROVED
the affector-magnitude mechanism recovers the one tendency-ambiguous wall 0.500→1.000 as a demo and scoped the full
estimator as the next build). **status:** OPEN — a MECHANISM + BUILD problem (extends the integrated causation typer). You
build + validate in `experiments/`; strategy lands any hdlab change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `7` — a de-risked DEEPENING of the just-integrated
> CAUSATION dimension (the affector-magnitude first term is already PROVEN; this builds it out with patient-affordance +
> directional cues). It closes the ONE measured wall in the causation typer (tendency-ambiguous verbs, capped at 0.500 by
> a lexicon). Ranked below the new-dimension/composition builds (belief-timeline, entity-state) because it deepens an
> existing organ rather than adding a capability, but it is the highest-value causation follow-on and the mechanism is
> already demonstrated. **Dependency web:** extends `force_dynamics_typer`; consumes the (agent→affector, patient)
> extraction. **Re-rank per the owner.**

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
The causation reader can tell "caused" from "enabled" from "prevented" — from the verb. But some verbs are genuinely
ambiguous: "the key opened the gate" vs "the wind opened the gate" use the same word yet mean different things. In the
first, the key just *lets* the (already openable) gate open — enable. In the second, the wind *forces* the gate open
against its tendency to stay shut — cause. The difference is whether the thing being acted on would tend toward the outcome
on its own, and how strong the actor is. The causation work already proved you can read this from the actor's strength: a
gentle push that still works means the thing was disposed to happen anyway (enable); a hard shove means the actor overcame
resistance (cause). Build the full "does the patient tend toward this outcome?" estimator so the reader handles these
ambiguous cases, not just the ones where the verb settles it.

## 2. WHY THIS ONE
It closes the ONE measured wall in the just-integrated causation typer, and the mechanism is already proven (a
demonstration lifted the ambiguous cases from coin-flip to perfect). It is the causation solver's explicitly named #1
follow-on, de-risked, and it makes the causation dimension genuinely robust rather than lexicon-limited. Cheap-to-wrong
alternatives (a bigger verb list) are already ruled out — patient-tendency is not in the verb.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** Wolff's force theory (Wolff 2007; Wolff & Song 2003) — CAUSE/ENABLE/PREVENT depend on
  (patient-tendency, affector-patient concordance, endstate). The verb supplies concordance; PATIENT-TENDENCY is world-
  knowledge that is PARTLY LINGUISTICALLY CONSTRUCTED (Kuhnmünch & Beller 2005) and READABLE from the sentence via force
  arithmetic: a WEAK affector that still reaches the endstate implies the patient contributed (tends → ENABLE); a STRONG
  affector implies it overcame patient resistance (does not tend → CAUSE). Patient-affordance (is the patient the kind of
  thing that tends toward this?) and directional/aspectual cues refine it.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the affector-MAGNITUDE estimator (proven first term), the patient-
  AFFORDANCE lexicon, and the combination weights/threshold. **Copy the COMPUTATION** (Wolff's force arithmetic: patient-
  tendency from affector-magnitude + affordance + directional cues → feed the truth-table); the causation solver's
  affector-magnitude term is PROVEN — build on it, add patient-affordance + directional; SWEEP the lexicon + weights.
- **NOT brain-faithful:** a bigger verb LEXICON (measured dead — patient-tendency is NOT in the verb, capped at 0.500); a
  do-calculus/interventional estimator (HARD_FAILED); an external LLM (the invariant); adopting the proven affector-magnitude
  demo AS-IS without building the full estimator (it is a first term, not the whole signal).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** the causation integration (`causation_has_no_force_dynamic_typing`,
  `exp_causal_tendency_recovery_v1.py`): a verb lexicon caps CAUSE-vs-ENABLE on tendency-ambiguous verbs at 0.500 (vs a
  tendency-oracle 1.000); the affector-MAGNITUDE first term lifts it 0.500→1.000, the magnitude-shuffle twin stays at
  chance, and it GENERALIZES to held-out affectors. The Wolff typer (`hdlab/force_dynamics_typer.py`, landed) consumes the
  tendency bit.
- **INFERRED (to prove):** that a FULL patient-tendency estimator (affector-magnitude + patient-affordance + directional
  cues) types CAUSE-vs-ENABLE on tendency-ambiguous verbs CI-separated over the lexicon-only floor (0.500) toward the oracle
  (1.000), with the info-free twin (shuffled magnitude/affordance) LOSING — OR a rigorous reason the added terms don't
  improve over the proven affector-magnitude alone (a measured bound that the first term is most of the signal).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT rebuild the Wolff force typer (integrated — EXTEND it with the tendency input via `force_dynamics_typer`). Do NOT
  grow the verb lexicon to fix tendency-ambiguous verbs (measured dead — patient-tendency is not in the verb). Do NOT build
  do-calculus (HARD_FAILED). Do NOT re-derive the affector-magnitude first term (PROVEN — build ON it). REUSE the
  (agent→affector, patient) extraction.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `causation_has_no_force_dynamic_typing/SOLVED.md` (the tendency wall + the affector-magnitude proof) +
  `experiments/exp_causal_tendency_recovery_v1.py` (the demo: 0.500→1.000, the twin, held-out generalization) +
  `hdlab/force_dynamics_typer.py` (the typer that consumes the tendency bit) + its research note. Run
  `tools/experiment_index.py query "tendency"` / `"affector"` / `"causal"` / `"force"` (SINGLE keywords). Audit: the newest
  §2b CAUSATION entry (the tendency OUR-INVENTION-with-a-measured-bound). **Mind the CORPUS-AGE confound** (archaic affector
  descriptions).

## 7. THE BAR
PASSES only with ALL of:
1. **A glass-box PATIENT-TENDENCY estimator** (built in `experiments/`): affector-MAGNITUDE (the proven first term) +
   patient-AFFORDANCE (an affectedness lexicon) + directional/aspectual cues → a patient-tends {yes,no} signal fed into the
   `force_dynamics_typer` truth-table. Copy Wolff's force arithmetic; SWEEP the affordance lexicon + weights. NO do-calculus,
   NO external LLM.
2. **Types CAUSE-vs-ENABLE for tendency-ambiguous verbs CI-separated over the lexicon-only floor (0.500)** toward the
   tendency-oracle (1.000) — on a tendency-ambiguous population (open/move/turn/roll… with the outcome held constant so the
   contrast isolates tendency, as the demo did); the **info-free twin** (shuffled affector-magnitude / affordance) LOSES
   CI-separated; report CI half-width + null p95; no number crosses populations. A **POSITIVE control** the metric can move
   (a minimal pair — key vs wind — the estimator gets and the lexicon-only typer cannot).
3. **Generalizes** (held-out affectors, as the first term did) — not fit to the construction set.
4. **One-screen summary:** the tendency terms → floor (0.500) → twin → CAUSE-vs-ENABLE lift toward oracle → verdict. Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "affector-magnitude alone is most of the signal; patient-affordance + directional
add X < CI over it, so the full estimator ≈ the proven first term — a measured bound, with the key-vs-wind control confirming
the mechanism").

## 8. FILES AND ENTRY POINTS
- **Motivation + proven mechanism (REUSE, build on):** `causation_has_no_force_dynamic_typing/{SOLVED.md,
  research_force_dynamics_brain_mechanism_2026-08-29.md}`; `experiments/exp_causal_tendency_recovery_v1.py` (the
  0.500→1.000 demo + the twin + held-out generalization).
- **Extend:** `hdlab/force_dynamics_typer.py` (the Wolff typer that consumes the tendency bit); the (agent→affector,
  patient) extraction. Audit + heavy→REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
The 0.500→1.000 affector-magnitude demo is the PROVEN first term + the MOTIVATION, not your full result — the deliverable is
the FULL patient-tendency estimator (magnitude + affordance + directional) validated over the lexicon-only floor with
held-out generalization. Do NOT grow the verb lexicon, build do-calculus, or re-derive the first term. Strategy owns any
hdlab landing.
