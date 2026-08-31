---
priority:
review: STRONG
review_text: A covariation causal-graph organ (Cheng power + a hierarchical type-role schema) types CAUSE-vs-PRECONDITION on held-out MAVEN-ERE (n=9698, coverage 1.0) at balanced 0.772 vs the adjacency/precedence structural floor 0.546 (+0.226 CI-sep) and raw +0.058 over majority -- the bar MET with power. Reverified 16/16 FIRST-HAND (recomputes from MAVEN-ERE source): info-free permuted-label twin loses, it GENERALIZES to UNSEEN type-pairs (schema 0.581 vs memorized-lookup chance 0.500 -- a schema, not memorization), survives 20% type-noise, and covariation dominates linguistic cues (+0.226 vs <0.02). Graded STRONG not EXCELLENT: single-corpus (MAVEN-ERE); the mechanism is PHYSICAL-causation only (phys-AUC 0.684 vs intentional 0.570); and OPEN-TEXT/cross-genre transfer is a RIGOROUS NEGATIVE, honestly diagnosed (covariation needs OBSERVED CONTINGENCY -- it does NOT beat the structural floor on unseen pairs, 0.671 vs 0.705). Exemplary honesty: WITHDREW its own earlier over-claimed cross-genre negative as instrument-confounded and re-tested cleanly. NO live-reader landing earned: the reader operates on SINGLE documents where cross-document contingency is absent, so wiring it into the "why?" QA would not help; the organ's home is CORPUS-level causal knowledge (the knowledge-store / learner), not the reader.
---

> ## ✅ SOLVER REVIEW -- STRONG (integrated by strategy 2026-08-31)
> **Why STRONG, specifically:** it met the letter of the bar with power and unusually strong controls -- the
> covariation typer beats BOTH the majority-class AND an adjacency/precedence STRUCTURAL floor CI-separated
> (+0.226 balanced), at coverage 1.0 (it fires on every relation, unlike the force typer's 16%), and the win is
> covariation-driven, not discourse-position (the structural floor isolates that) and not linguistic-cue-driven
> (cues add <0.02). The decisive generalization control is the seen-vs-UNSEEN type-pair split: the hierarchical
> schema still types unseen pairs (+0.08) while a memorized lookup collapses to chance -- so it learned a schema,
> not a lookup table. It survives 40% type-noise / 21-bucket coarsening (not dependent on gold 168-way typing).
> **Reproduced under my check:** I re-ran `verification/test_narrative_causal_graph_organ.py` -- 16/16 PASS,
> scaffold-free; balanced 0.772, +0.226 over structural (lo 0.2096), permuted-label twin loses (+0.186), unseen-pair
> schema 0.581 vs lookup 0.500, detection +0.0462, physical>intentional (+0.114), all reproduce from MAVEN-ERE source.
> **The honesty that earns the grade (and caps it):** the solver asked the owner's actual question -- does it work on
> OPEN text? -- and reported a RIGOROUS NEGATIVE, DIAGNOSED: covariation needs OBSERVED CONTINGENCY, so it fails on
> never-co-observed pairs (the honest within-witness bound: organ 0.671 < structural 0.705 on unseen pairs) and on
> cross-genre narrative. It even WITHDREW an earlier cross-genre negative it had over-claimed, on finding the probe
> was instrument-confounded (matrix-verb extraction / explicit-connective pairs), and re-tested within-MAVEN cleanly.
> A rigorous negative is a pass; the physical-only boundary + single-corpus scope + open-text negative are why this is
> STRONG, not EXCELLENT.
> **What I landed vs did NOT (the disciplined call):** NO live-reader landing. The reader reads SINGLE documents,
> where the cross-document co-occurrence contingency this organ needs does not exist -- so wiring `CovariationModel`/
> `HierarchicalTyper` into the reader's "why?" QA would ride the open-text negative, not a win (this mirrors the
> integrated `causation_is_typed_per_clause_not_across_the_causal_network` no-landing). The organ stays experiment-side
> as a validated capability for CONTINGENCY-OBSERVABLE input; its real future home is CORPUS-level causal knowledge
> (the knowledge-store consistency-cleanup p4 / the learner), which sees the whole corpus. Recorded in WIRING_MAP as a
> correct no-reader-landing with that seed. NO hdlab file changed.

# PROBLEM: real narrative causation is a whole-event CAUSAL-GRAPH inference the reader cannot do — the force-dynamic typer we built is aimed at the wrong ~16% of it. The generalization stress-test (`stress_test_which_organ_wins_actually_generalize_on_held_out_text`, integrated) reran `force_dynamics_typer` on real MAVEN-ERE (n=9,698 annotated causal relations) and found it FIRES on only 16.1% of them, and where it fires its force signal is INDISTINGUISHABLE from a shuffled-lexicon twin (+0.018 NOT_SEP) — it loses the population to the majority floor by −0.679 (the constructed win was 0.929/1.000 on n=42/40 minimal pairs). The diagnosis is not a broken typer: it is aimed at explicit PHYSICAL predication, but real narrative causation is overwhelmingly IMPLICIT and MENTAL/event-level — "he studied, so he passed" — a covariation-based causal-GRAPH inference over event TYPES, a different, PINNED brain system (Trabasso & van den Broek; Kintsch; Kuperberg 2011 N400; Feng et al. 2021 ALE — left IFG/MTG + rostral mPFC; force-dynamic verbs have a VERIFIED ABSENCE of any neural study). The stress-test already GATE-CLEARED the successor: a glass-box event-type COVARIATION scorer beats its shuffled twin +0.094 and beats the majority floor +0.056 (clears the pre-registered +0.05 HARD-PASS) on the 83.9% subset the typer never fires. Build the full narrative causal-graph implicit-inference organ that covers that ~84%.

**slug:** `narrative_causal_graph_missing_implicit_inference_organ` — **opened:** 2026-08-30 by the strategy session (the
generalization stress-test's gate-cleared causation successor). **status:** OPEN — a MECHANISM + BUILD problem. You build +
validate in `experiments/`; strategy lands any hdlab change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `5` — HIGH. It is the CORRECT causation capability for real
> narrative (the covariation causal-graph route), gate-cleared by the stress-test, and it COMPLEMENTS the in-flight causation
> wiring (p2 `wire_the_causation_typer_into_the_live_reader`): p2 wires the force typer for the ~16% EXPLICIT-PHYSICAL subset
> (narrow, per this audit), THIS organ covers the ~84% IMPLICIT/mental subset the typer structurally cannot reach. ⚠️ The
> stress-test found the force typer does NOT generalize on real causation — so this, not the force typer, is the real-text
> causation lever. **Re-rank per the owner.** ⚠️ HONEST: the gate is CLEARED but the FULL organ is ~P=0.50 until built.

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
When a story says one thing led to another, most of the time it's NOT physical force ("the wind opened the gate") — it's
"he studied hard, so he passed," "the drought ruined the harvest, so the village starved." Understanding those means knowing
which KINDS of events tend to cause which — a learned sense of "studying leads to passing" — not a physics engine. We built
the physics engine; on real stories it only applies to about one causal link in six, and even there it's basically guessing.
The right mechanism is the one the brain actually uses for this: judge how strongly one event-type predicts another from how
often they co-occur, the way people learn cause from experience. Build that.

## 2. WHY THIS ONE
The generalization audit proved our current causation typer does not generalize on real causal relations, and it pre-tested
the fix and it cleared the bar. This is the real-text causation capability — it turns the QA capstone's "why?" NEGATIVE
(which the force typer cannot fix) into a candidate win, and it covers the 84% of real causation the typer structurally
misses. It is also brain-grounded where force dynamics is not (force-dynamic verbs have no neural literature; covariation
causal inference has an ALE meta-analysis).

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate):** causal inference in discourse is COVARIATION-BASED — how reliably event-type A precedes/predicts
  event-type B (Cheng's causal-power / power-PC; Griffiths & Tenenbaum causal graphs = a likelihood over observed covariation;
  Trabasso & van den Broek causal network; Kintsch construction-integration; Kuperberg 2011 N400 causal-relatedness; Feng et
  al. 2021 ALE — left IFG/MTG + rostral mPFC). NOT mechanism/force-based. A dual-route account (covariation vs mechanism) makes
  the force typer the minority mechanism route.
- **OUR-INVENTION (flag + sweep):** the event-TYPE abstraction (how you cluster events into types to count covariation over —
  Chambers & Jurafsky narrative-chain precedent, Hu & Walker), the covariation estimator + its discounting of alternative
  causes (Cheng power-PC), thresholds. Glass-box, no external LLM, no external causal KB at inference.

## 4. MEASURED vs INFERRED
- **MEASURED (the gate is CLEARED):** on the MAVEN-ERE valid split, a glass-box event-type covariation scorer on the UNFIRED
  83.9% subset beats its shuffled twin +0.094 AND beats the majority-class floor +0.056 — a REAL signal (unlike force dynamics'
  +0.018 NOT_SEP), clearing the pre-registered +0.05 HARD-PASS. So the covariation route carries genuine causal signal on real
  relations.
- **INFERRED (you build + measure):** whether the FULL organ (event-type abstraction + covariation estimate + alternative-cause
  discounting) types CAUSE-vs-PRECONDITION on held-out MAVEN-ERE CI-separated over the majority + adjacency floors, twin losing,
  coverage-weighted across the ~84% subset.

## 5. ALREADY TRIED / DO NOT RE-RUN
- `force_dynamics_typer` (integrated; explicit-physical only) — this organ COMPLEMENTS it (the 84% it misses); do NOT rebuild it.
- `causation_is_typed_per_clause_not_across_the_causal_network` (integrated NEGATIVE) — cross-sentence FORCE typing is dead;
  this is NOT that (it is covariation over event TYPES, a different primitive that the stress-test showed CARRIES signal).
- The stress-test's covariation GATE cell (`exp_generalize_causation_implicit_covariation_gate_v1`) is the de-risk PoC — build
  the full organ ON it; do not just re-run the gate.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read the stress-test's causation research note (`research_causation_typer_wall_implicit_and_mental_causation_2026-08-30.md`)
  + the gate cell — the PINNED covariation architecture + the pre-registered P1/P2/P3 gates + the 83.9% unfired subset definition.
- Read `hdlab/force_dynamics_typer.py` (the complementary 16% route) and MAVEN-ERE on the shelf. Confirm the covariation gate
  reproduces (+0.094 twin, +0.056 majority) before building.

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
On held-out MAVEN-ERE causal relations (the ~84% subset the force typer does not fire on; a pre-existing annotated corpus):
- **PASS =** the covariation causal-graph organ types CAUSE-vs-PRECONDITION beating BOTH the majority-class floor AND the
  adjacency/precedence-only floor, CI-separated (bootstrap; CI half-width + null p95), coverage-weighted lift ≥ +0.05, with the
  info-free shuffled-covariation twin LOSING. Report cross-corpus (not just within-MAVEN train→valid) if a 2nd causal corpus is
  reachable (the gate was within-MAVEN — a noted bound to push).
- **A rigorous NEGATIVE is a full PASS:** if the full organ cannot beat the floors coverage-weighted (e.g. covariation needs
  more data than a single narrative supplies, or the event-type abstraction leaks), name why, enumerated.

## 8. FILES AND ENTRY POINTS
- Consumes: the stress-test's gate cell + causation research note; `hdlab/force_dynamics_typer.py`; MAVEN-ERE (`data/corpora/`).
- Build + validate in `experiments/`; witness recomputes from source on the held-out subset. Fold an **AUDIT UPDATE** into
  `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the CAUSATION dual-route: force = explicit-physical 16%, covariation-graph = implicit 84%).
- Coordinate: p2 (force-typer wiring, the 16%) + the QA measurement instrument (re-measure "why?" QA with this organ wired).


## DO NOT QUOTE / DO NOT REDO
- 🚫 This problem is INTEGRATED — the honest result + caveats are in `review_text` (frontmatter) and `INTEGRATED_BY_STRATEGY` (SOLVED.md). Do NOT quote its numbers across a different scorer / population / representation (standing rule: no number crosses scorers or populations); recompute every floor on the target item's own population.
- 🚫 The direction is CLOSED for re-derivation — build ON it, do not re-run it.
