# Research drill: the brain mechanism for automatic within-clause causative extraction, force-role binding, and endstate reading

**Date:** 2026-08-30 · **Drill type:** literature (neuroscience / psycholinguistics), LEAD-WITH-BIOLOGY · **For problem:** `wire_the_causation_typer_into_the_live_reader`
**Prior-work check (results archive):** `experiment_index.py query "causative event extraction force dynamics"` → 0 cells; `"thematic role binding verb"` → 0 cells. This is a mechanism drill, not a re-run of a landed experiment. The two integrated CAUSATION SOLVEDs (`causation_has_no_force_dynamic_typing`, `causation_is_typed_per_clause_not_across_the_causal_network`) are respected as hard constraints, not re-tread.
**Calibration:** lit-scan penalty applied — verdicts below are mechanism-class reads, not effect-size promises; where I would be tempted to over-claim I say "predominantly" / "at the margins".

---

## Bottom line (verdict first)

Robust, automatic **within-clause** causative extraction + force-role binding + endstate reading is **predominantly (a) a core, robust brain operation** — so a weak within-clause extractor is **mostly OUR fidelity gap to build across**, NOT a brain limit. The brain's operation is fragile only **at two specific margins**, and — importantly — those two margins are **exactly where the project already has an integrated negative**:

1. **Non-canonical / role-reversed / implausible** argument configurations (good-enough processing; the N400 is often insensitive to thematic-role reversals). Degradation here is partly a genuine brain limit; do not over-engineer against it.
2. **Cross-clause / cross-sentence causal bridging** is only *minimally* and *automatically* computed — and only when local coherence + semantic associates support it (McKoon & Ratcliff minimalist hypothesis). This is a knowledge-heavy, effortful, frequently-skipped inference in the brain — which independently explains why the project's **cross-sentence causal-network typer measured dead** and validates scoping the win to the within-clause domain.

So the split the project already made (within-clause = the typer's real domain and where the win lives; cross-sentence = the known integrated negative) **is the same split the brain makes** between fast verb-driven local causation and slow knowledge-driven discourse causation. That is a strong external endorsement of the scoping, not just a convenience.

---

## RQ1 — How the brain SEGMENTS / DETECTS a within-clause causative event; is it distinct from general event segmentation; what signals completion?

**Within-clause causative detection is a DISTINCT, faster, more automatic operation than discourse event segmentation.** Two levels must not be conflated:

- **Discourse level (situation-model segmentation).** Event Segmentation Theory (Zacks, Speer, Swallow, Braver & Reynolds 2007) places event boundaries where **prediction error** spikes; the Event Indexing Model (Zwaan & Radvansky 1998) tracks five indices — space, time, protagonist/entity, intentionality/goal, and **causality** — and a disruption in the **causal flow** is one of the strongest boundary cues. Speer, Zacks & Reynolds (2007, *Psychological Science*, fMRI) found boundary-locked transient activity tracking changes in characters' **goals and causes**. The Event Horizon Model (Radvansky & Zacks) stores **causal relations among events** as a retrieval structure. **But this operates BETWEEN events** — it is the cross-sentence causal-network level, which the project already found dead on real text.
- **Clause level (the project's target).** Within-clause causation ("the wind opened the gate") is **not** read off a boundary detector. It is **lexically/constructionally triggered at the verb** — the verb's argument structure plus its force-dynamic lexical semantics announce "caused change" essentially at the verb. This is fast and automatic and does **not** wait for a prediction-error boundary.

**Implication for the wire:** the within-clause causative detector should be **verb-/construction-triggered** (fire on a causal-verb-lexicon hit or a caused-change argument-structure construction), NOT a port of an event-boundary detector. Do not reach for Baldassano/Zacks boundary machinery for the clause-internal job — wrong grain.

**Completion / telicity (the "endstate-reached" bit).** This is computed online from **aspectual composition**, not free: verb lexical aspect + bounded object + particles ("up", "out") + resultative phrase determine telicity (Piñango, Zurif & Jackendoff 1999; Todorova, Straub, Badecker & Frank 2000). **Aspectual coercion** (forcing a telic verb atelic, or vice versa) carries a measurable processing cost detectable ~250 ms after it is licensed (Piñango et al.; MEG / self-paced reading — results mixed but the online computation is real). **Telicity (has an inherent endpoint) is separable from culmination (that endpoint was actually reached)** — culmination is defeasible by "almost", "tried to", the progressive, and by negation/prevention. The reader must read culmination, not just telicity.

---

## RQ2 — How the brain BINDS the two force roles (affector=antagonist/causer, patient=agonist/affectee) online; is it fast/automatic or fragile?

**Role binding is FAST, INCREMENTAL, and largely AUTOMATIC for canonical configurations — and this maps directly onto the force-dynamic affector role.**

- The **extended Argument Dependency Model (eADM)** (Bornkessel-Schlesewsky & Schlesewsky 2006, *Cognition*/*Brain & Language*) is built around **actor-centrality**: it rapidly identifies the **Actor** (≈ the force-dynamic affector / antagonist / causer) from prominence cues — animacy, case, word order, agreement — with an **"actor-first" / "agent-first" default** that appears cross-linguistically. The complement is the **Undergoer** (≈ patient / agonist / affectee). **This is the pinnable mechanism for role binding:** affector = the highest-prominence Actor, patient = the Undergoer.
- **N400 / P600 evidence on robustness/fragility.** The **P600** flags when a **non-canonical** assignment needs **revision** (passives, object-first, garden paths) — role revision is a distinct, effortful operation. Critically, the **N400 is often INSENSITIVE to thematic-role reversals** (e.g. "the dog was bitten by the man"): plausibility and lexical association can override the actual syntactic assignment. This is **Ferreira's "good-enough" processing** (Ferreira 2003; Ferreira, Bailey & Ferraro 2002) and Kim & Osterhout's "semantic attraction".

**Verdict for RQ2 (bears directly on OUR-gap vs brain-limit):**
- Binding is **robust + automatic + cheap for canonical within-clause causatives** (SVO, animate agent, plausible). A weak binder on THOSE = **OUR fidelity gap** — the brain does it robustly, so we should be able to replicate it.
- Binding is **genuinely fragile for non-canonical / reversed / implausible** configurations (good-enough processing). Degradation there is **partly a brain limit** to respect — do not treat a reversed/garden-path miss as an implementation failure to hammer.

---

## RQ3 — GENERALIZATION across constructions; is there a construction-general representation?

**Yes — there is a construction-general representation, and it is the exact target the typer should key on. Two convergent routes recover the SAME force-dynamic triple from different surface forms.**

**Route A — Construction grammar (Goldberg 1995, *Constructions*; 2006, *Constructions at Work*).** Argument-structure constructions **carry causal meaning independently of the verb**:
- **Caused-motion**: "X causes Y to move Z" — [Subj V Obj Obl] ("Pat kicked the ball into the net").
- **Resultative**: "X causes Y to become Z" — [Subj V Obj Xcomp] ("hammered it flat", "kicked Bob black and blue").
- **Transitive lexical causative**: "break/open/melt" used transitively.
- Goldberg's key result: the **resultative is a metaphorical extension of caused-motion** (Change-of-State AS Change-of-Location). So the **SAME CAUSE type is recognized across lexical-causative, resultative, and caused-motion because the CONSTRUCTION supplies the caused-change schema and binds the roles** — even when the bare verb ("hammer") is not itself causal. This is the construction-general representation the RQ asks for.

**Route B — Stored causal-verb lexicon (periphrastic causatives).** Periphrastic causatives map cleanly onto the **three force-dynamic categories** (Wolff & Song 2003; Wolff 2007; Cao, Kominsky et al. 2023, Stanford CICL, "A Semantics for Causing, Enabling, and Preventing Verbs"):
- **CAUSE** = {cause, force, get, make, set, stimulate}
- **ENABLE** = {allow, enable, help, leave, let, permit}
- **PREVENT** = {block, hinder, hold, impede, keep, prevent, protect, restrain, stop}
- Here the **verb's stored lexical semantics already encode the force configuration** — no construction inference needed. (Note: `make` takes a bare complement "made X happen"; most others take a `to`-complement "caused X to V" or a `from`-adjunct "kept X from Ving".)

**The generalization PRINCIPLE to replicate (PINNED):** surface form → force-dynamic roles by **construction-carries-meaning (Goldberg) + a stored 3-category causal-verb lexicon (Wolff/Cao)**. Both routes converge on the same **(affector concord/oppose, patient tendency, endstate reached)** triple — and *that triple IS the construction-general representation*. The typer already consumes exactly this triple, so the generalization is: recover the triple by **either** construction recognition (for lexical/resultative/caused-motion) **or** lexicon lookup (for periphrastic). The `force_dynamics_typer`'s FrameNet Causation-family lexicon already covers Route B and part of A; the **construction route for bare-verb lexical causatives + resultatives is where the front-end gap is**.

---

## RQ4 — TELICITY / ENDSTATE reading, especially PREVENT (a never-realized outcome)

**Force dynamics is UNIQUELY able to represent a never-realized outcome — this is the discriminating positive control, and the neuroscience backs it.**

- **Why only force dynamics can do PREVENT** (Wolff 2007; Wolff & Barbey 2015, "Causal reasoning with forces", *Frontiers*; Barbey & Wolff 2007). Force dynamics represents **tendencies and opposing forces**, not just realized state changes. PREVENT = the affector **opposes** a patient that **TENDS toward** the endstate, and the endstate is **NOT reached**. A purely state-change / covariation account (Cheng-style, or an untyped "A→B" link) **cannot represent an outcome that never happened** — it has nothing to point at. This is why the untyped/majority-CAUSE reader structurally fails the prevented-endstate case, and it is the project's stated positive control. Wolff & Barbey extend this to **double prevention / causation-by-omission** ("removing the jack prevented the force that had prevented the car from falling") — the same machinery represents chains of never-realized forces.
- **Reading the "not reached" bit online — negation as simulation** (Kaup, Yaxley, Madden, Zwaan & Lüdtke 2007; Kaup et al. 2006). The **Two-Step Simulation Hypothesis**: comprehenders first simulate the **affirmative** (the endstate happening) and then represent it as **negated / prevented**. Measured: after "no eagle in the sky", the *affirmative* (eagle) is briefly activated then suppressed. Prediction for the reader: on "the bar kept the gate from opening", the comprehender transiently simulates the gate opening, then sets **endstate_reached = FALSE**. This is a real two-stage online cost, not a static flag.
- **Non-prevention culmination defeat.** Even without a prevention verb, culmination is defeasible by aspect: progressive ("was opening"), "almost", "tried to / failed to". Telicity/aspect processing (Piñango; Todorova) supplies this. So `endstate_reached` should be set FALSE for **both** (i) PREVENT verbs/constructions and (ii) defeated culmination (progressive / "almost" / "failed to").

---

## Neural substrate (converging evidence that causal typing is a real, localizable operation)

- **Middle / medial frontal cortex** is repeatedly implicated in causal inference from words and sentences (Kranjec & Chatterjee; Kranjec et al.), distinct from perceptual launching-event causation. Causal-verb evaluation recruits frontal-parietal regions beyond non-causal verbs. tDCS work: frontal stimulation reduces causal perception of time; parietal reduces causal perception of space. Force dynamics' CAUSE/ENABLE/PREVENT are explicitly named as the lexicalized causal-verb semantics in this literature — i.e. the brain treats the three types as a real semantic distinction, not a philosopher's taxonomy.
- **mPFC / structured event complexes** support counterfactual (never-realized) representations for planning (Barbey et al. 2009) — consistent with force dynamics' never-realized-force representation for PREVENT.

---

## DELIVERABLE: the three sub-step mechanisms to replicate + PINNED/OUR-INVENTION flags

| sub-step | brain mechanism to replicate | verdict | PINNED vs OUR-INVENTION |
|---|---|---|---|
| **DETECT** (within-clause causative event) | **Verb-/construction-triggered** detection: fire on (i) causal-verb lexicon membership (3-category periphrastic + lexical causatives) OR (ii) caused-change argument-structure construction (transitive causative, caused-motion, resultative). NOT a discourse boundary detector — wrong grain. | Core robust operation → **weak detector = OUR gap** | **PINNED:** force-type-from-verb; construction-carries-meaning (Goldberg). **OUR-INVENTION:** the parse→tuple front-end glue. |
| **BIND ROLES** (affector=Actor/causer, patient=Undergoer/affectee) | **Actor-centric assignment (eADM):** affector = highest-prominence Actor (animacy/subjecthood/agent-first default); patient = Undergoer. | Robust+automatic for **canonical** → **OUR gap there**; genuinely fragile for **reversed/non-canonical** → **partly a brain limit, respect it** | **PINNED:** actor-first prominence binding (eADM); good-enough fallback for non-canonical. **OUR-INVENTION:** dependency-parse→role heuristics. |
| **READ ENDSTATE** (culmination / prevented outcome) | **Telicity/culmination via aspectual composition + prevention-as-negation:** endstate_reached=FALSE for PREVENT verbs/constructions AND for defeated culmination (progressive/"almost"/"failed to"); TRUE for telic-completed. Force dynamics natively represents the never-reached endstate. | Core operation; PREVENT is the **discriminating positive control** → **weak reader = OUR gap** | **PINNED:** never-realized-endstate via opposing tendencies (Wolff, Wolff & Barbey); two-step negation simulation (Kaup). **OUR-INVENTION:** the aspect/negation/prevention cue detector. |

**Generalization principle (PINNED):** map surface → force-dynamic roles by **construction-carries-meaning (Goldberg) + a stored 3-category causal-verb lexicon (Wolff/Cao)**; both routes recover the same **(affector concord/oppose, patient tendency, endstate reached)** triple, which is itself the construction-general representation the typer already consumes.

**One caveat that constrains the headline honestly:** the brain's within-clause causative extraction is robust for *canonical, lexically/constructionally marked* clauses. If the wired reader's within-clause detector is weak on those, that is squarely OUR gap. If it is weak on **role-reversed / heavily non-canonical** clauses or on **cross-clause bridging**, that is at least partly a brain-faithful limit — and the cross-sentence part is already the project's integrated negative. So a rigorous negative on the *canonical within-clause* slice would be a real fidelity gap to build across; a negative on the *margins* is brain-faithful and should be reported as such, not hammered.

---

## Key citations
- Talmy (1988) *Force dynamics in language and cognition*, Cognitive Science. — the pinned force-dynamic frame.
- Wolff (2007) *Representing causation*, JEP:General; Wolff & Song (2003) *Models of causation and the semantics of causal verbs*, Cognitive Psychology. — CAUSE/ENABLE/PREVENT truth-table + 3-category verb lexicon.
- Wolff & Barbey (2015) *Causal reasoning with forces*, Frontiers in Human Neuroscience; Barbey & Wolff (2007). — prevention, double-prevention, never-realized forces.
- Cao, Kominsky et al. (2023) *A semantics for causing, enabling, and preventing verbs* (Stanford CICL). — the 3-category periphrastic lexicon the typer uses.
- Goldberg (1995) *Constructions*; (2006) *Constructions at Work*. — caused-motion / resultative / construction-carries-meaning generalization.
- Zwaan & Radvansky (1998) *Situation models*, Psych Bulletin (Event Indexing, causality as one of five indices); Zacks, Speer, Swallow, Braver & Reynolds (2007) EST; Speer, Zacks & Reynolds (2007) fMRI narrative event boundaries; Radvansky & Zacks Event Horizon Model. — discourse-level segmentation (the cross-sentence level, distinct from clause-internal).
- Bornkessel-Schlesewsky & Schlesewsky (2006) *extended Argument Dependency Model (eADM)*. — actor-centric online role binding.
- Ferreira (2003) "good-enough" processing; Kim & Osterhout — N400 role-reversal insensitivity / semantic attraction. — fragility at the non-canonical margin.
- Piñango, Zurif & Jackendoff (1999); Todorova et al. (2000) — aspectual coercion / telicity computed online.
- Kaup, Yaxley, Madden, Zwaan & Lüdtke (2007) *Experiential simulations of negated text information* — Two-Step Simulation Hypothesis (prevented/negated outcome).
- McKoon & Ratcliff (1992) *Inference during reading* (minimalist hypothesis) — cross-sentence causal bridging is only minimally/automatically inferred (validates the cross-sentence negative).
- Kranjec & Chatterjee; Kranjec et al. — frontal/parietal neural substrate of causal-verb comprehension.
