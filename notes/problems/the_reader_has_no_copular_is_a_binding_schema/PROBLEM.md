---
priority: 4
review:
review_text:
---

# PROBLEM: the reader detects copular events ("X was a doctor", "the house was empty") but has NO is-a BINDING SCHEMA that attaches the predicate complement to the subject ENTITY as a category/attribute — the base reader answers 0/376 (0/120 on the clean subset) on "what/who is X" over clean predicate complements, a register-INDEPENDENT representation gap covering ~23% of the population; build the attributive/identificational binding readout that answers what an entity IS / what property it HAS, CI-separated over a floor with the info-free twin LOSING — or a located negative naming why predication resists a role-filler binding.

**slug:** `the_reader_has_no_copular_is_a_binding_schema` — **opened:** 2026-09-02 by the strategy session, lifted from the owner-DONE located-negative `register_native_parse_and_pos_training_data_for_pp_attachment_and_robust_tagging` (which located this as a real, SEPARATE, register-independent gap — base reader 0/376 on predicate complements — and recommended filing it separately). **status:** OPEN — a small FRONT-END/situation-model representation build (a missing schema), NOT a parser or register-data task. Strategy lands any hdlab wire (Q111, default-off, witnessed). Glass-box, NO external LLM at inference (the invariant).

> **PRIORITY NOTE:** filed at `4` — a real gap (~23% of the population, register-independent, cleanly located) but narrower and more self-contained than the who-did-what selection cap at 2 or the coherence prior at 3; a good bounded build.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** The mission is the most brain-faithful substrate.
> **🧠 OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN do THIS?** Name the structure + the computation, replicate that OPERATION as exactly as you can. It is the FIRST thing you do, not a tiebreaker.
> **🚀 EXPLORE FAR + WIDE for the mechanism** — read the neuroscience, cross domains; if a MORE brain-foundational method conflicts with this brief, submit THAT instead (say why it is more faithful).
> **🧱 A SHARED WALL = GO DEEPER, not stop.** A wall is a fidelity gap to BUILD ACROSS, never a ceiling.
> **⛔ "CONVERGED" HAS A HIGH BAR** — claim it only with (a) the brain's mechanism identified AND (b) replicated + tested, or a SPECIFIC reason it cannot be.
> **🔁 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`):** each fire — gather a high-value control/curve/ablation/2nd-gold; enumerate what's LEFT + do it; MAP adjacent bottlenecks + EVALUATE each for brain-fidelity + optimization; a wall → a FINER research drill, never stop. Implement → test (can-fail, strongest real floor, twin LOSING) → iterate.
> **A rigorous negative is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.**
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`**; inherit its PINNED/INVENTED verdicts; add an AUDIT UPDATE for any deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
A huge amount of what a story tells you is not an action but a STATE-OF-BEING: "Ahab was a captain", "the room was cold", "she became his wife". These sentences say what someone or something IS, or what property it HAS. The reader currently notices that such a sentence happened but does not RECORD the fact onto the character/object — ask it "what was Ahab?" and it has nothing, because there is no schema that binds the after-the-verb description ("a captain") to the entity ("Ahab") as a category or attribute. On a clean test of these sentences the reader scores zero. This is not an old-prose problem (it fails the same way on modern text); it is a missing piece of the situation model. The job is to build that binding — attach the predicate description to the entity as an is-a / has-property fact the reader can read back.

## 2. WHY THIS ONE — a cleanly-located, register-independent situation-model gap
The register-native located negative isolated this while ruling out the parse/POS story: base reader 0/376 on predicate complements (0/120 on the clean subset), ~23% of the 19c population, and it reproduces on modern text — so it is a genuine representation gap, not a register artifact. It composes directly with the situation model's entity/state dimensions already built (`state_register`, `world_state_register`): those track open/closed and possession; this adds the is-a/attribute relation the copula asserts. Copular events are already DETECTED (the detector problem landed); what is missing is the BINDING + read-back.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: the copula BE encodes PREDICATION/IDENTIFICATION — it asserts a property of, or category membership / identity for, the subject (predicational vs identificational vs specificational copular clauses; Higgins 1979; the semantics of BE). Comprehension binds that property/category to the entity NODE in the situation model (attribute/role-filler binding; van Dijk & Kintsch 1983 the propositional textbase; property attribution to a discourse referent — Gernsbacher structure-building). Category membership is an is-a link into semantic memory (the taxonomic hierarchy; the ATL hub), so "X is a doctor" both attributes a property to X and links X into the DOCTOR category. Mark PINNED vs OUR-INVENTION: predication binds the complement to the subject entity = PINNED; the specific attribute/is-a slot representation and the predicational/identificational split handling = OUR-INVENTION-under-test.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive — from the parent):** base reader is-a/attribute read = 0/376 on predicate complements, 0/120 on the clean predicate-complement subset (`verification/test_register_native_located_negative.py` W5); ~23% of the 19c population is copular predication; register-INDEPENDENT (fails on modern too). Copular EVENT DETECTION already exists (`the_event_detector_misses_copular_and_nominal_predication_events`, integrated) — detection is not the gap, BINDING + read-back is.
- **INFERRED (you must measure):** does an is-a/attribute BINDING readout — attaching the predicate complement (nominal "a captain" / adjectival "cold" / identity "his wife") to the subject entity node — let the reader answer "what/who is X" and "what property does X have" CI-separated over a floor (e.g. most-recent-noun / string-overlap) on a clean predicate-complement gold, with an info-free binding-shuffle twin LOSING; does distinguishing predicational (property) from identificational (entity=entity) matter; does it compose with the existing entity/state registers without regressing them.

## ALREADY TRIED / DO NOT REDO (check `experiment_index` first)
- **Copular/nominal EVENT DETECTION** — DONE (`the_event_detector_misses_copular_and_nominal_predication_events`, integrated). This problem is NOT detection; reuse the detector and add the BINDING/read-back.
- **Treating the complement as a normal PATIENT** — wrong type: "a captain" is not the thing acted upon, it is a predicated property/identity; the positional/thematic role path does not bind it (that is exactly why the base reader is 0/376).
- Do NOT re-open register/parse data — the parent proved this gap is register-independent.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- **FIRST STEPS:** (1) understand ALL organs — `python tools/substrate_map.py`, `python tools/reader_capabilities.py`, skim `hdlab/`; (2) read IN FULL the parent `notes/problems/register_native_parse_and_pos_training_data_for_pp_attachment_and_robust_tagging/SOLVED.md` (the 0/376 localization) AND `the_event_detector_misses_copular_and_nominal_predication_events/SOLVED.md` (the detector you build on); (3) `python tools/before_you_start.py "copular is-a binding schema predication"`.
- Reproduce on your own recompute: the base reader 0/120 on the clean predicate-complement subset (the can-fail floor).
- Inspect what you will REUSE: the copular event detector, `hdlab/state_register.py` + `hdlab/world_state_register.py` (the entity-state schema pattern to extend with an is-a/attribute relation), `hdlab/situation_reader.py` (where a default-off attribute-binding read would land).

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = an is-a/attribute binding readout (glass-box, NO LLM) that, on a clean predicate-complement gold (nominal + adjectival + identity copular clauses), answers "what/who is X" and "what property does X have" CI-separated over the strongest simple floor (e.g. most-recent-noun, string-overlap) with an info-free binding-SHUFFLE twin LOSING CI-separated, AND does not regress the existing entity/state registers (an explicit no-regression check). Report CI half-width + null p95; recompute the floor on the same population. A rigorous located NEGATIVE — predication cannot be bound above the floor by a faithful role-filler schema, with the reason — is a FULL PASS.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE (do not reinvent): the copular event detector (from `the_event_detector_misses_copular_and_nominal_predication_events`), `hdlab/state_register.py` + `hdlab/world_state_register.py` (extend the entity-state schema with an is-a/attribute relation), `hdlab/situation_reader.py` (a default-off attribute-binding read on the entity dimension), the clean predicate-complement gold used by `verification/test_register_native_located_negative.py` (W5). Strategy lands any hdlab wire (Q111, default-off, witnessed). Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (predication is an is-a/attribute binding to the entity node, distinct from patient role assignment).

## DO NOT QUOTE
- Do NOT quote the copular EVENT-DETECTION result as solving this — detection landed; the gap is BINDING + read-back.
- Do NOT quote this as an old-prose/register problem — it is register-independent (fails on modern too).
- Do NOT treat the predicate complement as a patient — it is a predicated property/identity, a different binding.
- Do NOT use an external LLM to bind or read the attribute (the invariant); a glass-box schema is the deliverable.
