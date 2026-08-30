---
priority: 8
review:
review_text:
---

# PROBLEM: the integrated force-dynamic typer (`hdlab/force_dynamics_typer.py`) types causation ONE CLAUSE at a time (a single agent/patient/verb/outcome → CAUSE/ENABLE/PREVENT) — but the causation integration MEASURED that this covers only a slice: "most narrative causation is connective-linked clause PAIRS (the Trabasso NETWORK level), which force dynamics LABELS but a verb lexicon doesn't type." Real stories carry causation ACROSS sentences: "The dam broke. The village flooded." / "He studied hard, so he passed." — an event→event causal LINK, not a single verb, and the reader's causal NETWORK (`experiments/_causal_network.py` — the live placeholder that links by connective + most-recent adjacency) does NOT type its edges CAUSE/ENABLE/PREVENT. The brain builds a causal NETWORK of the discourse's events (Trabasso & van den Broek 1985: events are nodes, causal links are edges weighted by "necessity in the circumstances"; more causally-connected events are read faster + recalled more) and force dynamics LABELS those edges. Build the causal-network edge typer — construct the event causal network (connectives + temporal precedence + counterfactual necessity), type EACH edge CAUSE/ENABLE/PREVENT by composing the landed force typer with the outcome/endstate — and validate it types discourse-level causal links CI-separated over the connective/adjacency PLACEHOLDER with the info-free (edge-type-shuffle) twin losing.

**slug:** `causation_is_typed_per_clause_not_across_the_causal_network` — **opened:** 2026-08-29 by the strategy session (the
"unbuilt §3 synthesis" named by the integrated `causation_has_no_force_dynamic_typing`, owner-DONE/EXCELLENT: it typed
single-clause causation but MEASURED that connective-linked clause pairs — the NETWORK level — are where most narrative
causation lives and are untyped). **status:** OPEN — a MECHANISM + BUILD problem (extends causation to the discourse level).
You build + validate in `experiments/`; strategy lands any hdlab change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `8` — HIGH-value extension of the just-integrated
> CAUSATION dimension from single-clause to DISCOURSE (where the causation solver measured most narrative causation
> actually lives), reusing the landed force typer + the TIME precedence gate. Reader-INDEPENDENT: it operates on the causal
> network + the typer in `experiments/`, NOT the live reader's role path — so it runs safely in parallel with the assembly
> (p3). Ranked at `8` (a discourse extension of an existing dimension, below the new-dimension/composition builds). **Re-rank per the owner.**

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
The reader can now judge causation inside a single sentence ("the rain swelled the river"). But most causation in a story
runs *across* sentences: "The dam broke. The village flooded." — two separate events, one causing the other, with no single
causal verb. The reader has a rough map that links events by cue-words and nearness, but it doesn't say what KIND of link
each is — did the first event cause, merely enable, or prevent the second? The brain builds a causal *network* of the
story's events and labels each link. Build that: connect the events into a causal network, and type each link
cause/enable/prevent using the causation judgment we already built — so the reader understands the causal chain of a whole
passage, not just one clause.

## 2. WHY THIS ONE
The causation integration explicitly MEASURED that single-clause verb typing covers only a slice — the bulk of narrative
causation is connective-linked clause pairs at the discourse-network level, which it labelled its applicability bound and
its "unbuilt next synthesis." So this is where most of the causation signal in real stories actually is. It reuses two
integrated pieces (the force typer + the TIME precedence gate) and is reader-independent, so it advances the CAUSATION
dimension without touching the assembly.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** the discourse CAUSAL NETWORK (Trabasso & van den Broek 1985; Trabasso & Sperry 1985) —
  events are nodes; a causal edge exists where the earlier event is "necessary in the circumstances" for the later; causally
  central events are read faster and recalled more. Edge DIRECTION is gated by temporal precedence (cause precedes effect —
  the integrated TIME register). Force dynamics LABELS each edge CAUSE/ENABLE/PREVENT (Wolff — the same truth-table, now
  over the two linked events' force configuration rather than one clause's verb).
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the edge-construction rule (which event pairs get a causal edge —
  connective cue + precedence + a counterfactual-necessity check) and the mapping from a clause-pair to the force typer's
  (affector, patient, endstate) inputs. **Copy the COMPUTATION** (build the Trabasso network; type each edge via the landed
  force typer + the outcome endstate; precedence gates direction). The network↔force-dynamics COMPOSITION is OUR-SYNTHESIS
  (Trabasso gives the network, Wolff gives edge labels; their combination is not a single published result — LABEL it).
  SWEEP the edge-construction thresholds.
- **NOT brain-faithful:** the connective + most-recent-ADJACENCY placeholder (untyped, order-agnostic, links by nearness);
  do-calculus / interventional network inference (HARD_FAILED); an external LLM; typing an edge without the temporal
  precedence gate (the post-hoc fallacy).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** the causation integration (`causation_has_no_force_dynamic_typing`) —
  verb typing beats the placeholder on single clauses, but connective-linked clause pairs (the NETWORK level) are the
  measured applicability bound and are untyped; ENABLE is barely lexicalized. `hdlab/force_dynamics_typer.py` (the landed
  edge-labeller). `experiments/_causal_network.py` (the connective/adjacency network placeholder). The TIME register
  (integrated — precedence gate, 1.000 vs 0.000 on flashback-causal direction).
- **INFERRED (to prove):** that a Trabasso causal network with force-dynamically-TYPED edges beats the connective/adjacency
  placeholder CI-separated on a discourse-level causal population (connective-linked clause pairs + multi-event chains):
  "what kind of link is this — cause/enable/prevent?" and/or "is B causally necessary given A?"; the info-free twin
  (shuffled edge types / shuffled network) LOSES — OR a rigorous reason the clause-pair→force-typer mapping caps it (a
  measured bound, e.g. cross-clause affector/patient extraction is the bottleneck).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT rebuild the force typer (integrated — REUSE it to LABEL edges) or the TIME register (REUSE its precedence). Do NOT
  build do-calculus (HARD_FAILED). Do NOT use connective + most-recent-adjacency as the typing mechanism (that IS the
  placeholder floor to beat). Do NOT re-type single clauses (done — this is the CROSS-event network level). REUSE
  `_causal_network.py` (the network scaffold) + the (agent→affector, patient, outcome) extraction per event.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `causation_has_no_force_dynamic_typing/SOLVED.md` (the applicability bound — the network level as the untyped bulk)
  + `hdlab/force_dynamics_typer.py` (the edge-labeller to reuse) + `experiments/_causal_network.py` (the network placeholder)
  + the TIME register (precedence). Run `tools/experiment_index.py query "causal"` / `"network"` / `"trabasso"` /
  `"necessity"` (SINGLE keywords). Audit: the newest §2b CAUSATION + TIME entries. **Mind the CORPUS-AGE confound** (archaic
  connectives / clause structure on real narrative).

## 7. THE BAR
PASSES only with ALL of:
1. **A causal-network edge typer** (built in `experiments/`): construct the Trabasso event network (edges by connective cue
   + temporal precedence + a counterfactual-necessity check), type EACH edge CAUSE/ENABLE/PREVENT by composing
   `force_dynamics_typer` over the two linked events + the outcome endstate; precedence GATES edge direction (reuse TIME).
   Copy the computation; SWEEP the edge-construction thresholds. NO do-calculus, NO external LLM.
2. **Types discourse-level causal links CI-separated over the connective/adjacency placeholder** — a discourse causal
   population (connective-linked clause pairs + multi-event chains: "what kind of link?" / "is B causally necessary given
   A?"); the placeholder (`_causal_network`'s untyped connective+adjacency link) recomputed on the same population = the
   floor; the **info-free twin** (shuffled edge types / shuffled network structure) LOSES CI-separated; report CI half-width
   + null p95; no number crosses populations. A **POSITIVE control** the metric can move (a clause-pair whose type the
   network typer gets and the placeholder cannot — e.g. a PREVENT link across sentences, or a cause≠most-recent case).
3. **Isolates the network typing from single-clause typing** — show the lift is the CROSS-event edge structure + typing, not
   just re-running the verb typer (an ablation to per-clause typing without the network edges).
4. **One-screen summary:** network construction → placeholder floor → twin → edge-typing lift → verdict. Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "force-typed network edges beat the placeholder on clause pairs with an explicit
connective, but cross-clause affector/patient extraction caps multi-event chains at X — a measured bound, with the
across-sentence PREVENT control confirming the mechanism").

## 8. FILES AND ENTRY POINTS
- **Motivation + reuse (do not rebuild):** `causation_has_no_force_dynamic_typing/SOLVED.md` (the network-level applicability
  bound); `hdlab/force_dynamics_typer.py` (the edge-labeller); `experiments/_causal_network.py` (the network placeholder);
  the TIME register (precedence). Audit + heavy→REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
The single-clause typing win is the INGREDIENT, not your result — the deliverable is the CROSS-event causal-network edge
typing over the connective/adjacency placeholder floor. Do NOT rebuild the force typer or TIME register, re-type single
clauses, or build do-calculus. Strategy owns any hdlab landing.
