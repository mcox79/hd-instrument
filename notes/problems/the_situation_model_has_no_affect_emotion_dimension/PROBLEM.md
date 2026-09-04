---
priority: 11
review:
review_text:
---

# PROBLEM: the reader now tracks the five classic Zwaan-Radvansky dimensions (time/space/causation/protagonist+belief/intentionality) — but NOT how characters FEEL. Narrative comprehension monitors each character's EMOTIONAL STATE (Gernsbacher-Goldsmith-Robertson 1992: readers infer + update character emotion; de Vega 1996; Gygax 2004), a distinct appraisal system (amygdala/vmPFC/insula), NOT mentalizing (goal/belief = dmPFC/TPJ) and NOT physical causation. Build a per-character AFFECT REGISTER — like the just-landed goal register — from the reader's OWN extraction: explicit emotion constructions ("was afraid", "felt joy", "angrily", "to her delight") bound to the resolved character, carrying valence (+/−) and (where recoverable) the emotion category, answering "how does X feel" + "how did X feel about Y" off the accumulated model. Prove it CI-separated over a most-recent-emotion-word floor with a shuffled-character info-free twin LOSING — or a located negative naming why explicit narrative affect cannot be bound glass-box.

**slug:** `the_situation_model_has_no_affect_emotion_dimension` — **opened:** 2026-09-04 by the strategy session, the natural completion the owner-DONE `the_situation_model_has_no_goal_intention_dimension` earned (the reader now has 5 of the classic dimensions; affect is the well-attested remaining one). **status:** OPEN. Strategy lands any hdlab wire (Q111, witnessed). Glass-box, NO external LLM.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** The mission is the most brain-faithful substrate. A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.

> ## 🧠 BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar — work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure — do not build the tractable thing and cite neuroscience after.
> 2. **REUSE — does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST; extend a matching organ rather than re-deriving it.
> 3. **GENERALIZE — does this need to generalize, and HOW does the brain generalize it?** Build for that (register / novelty / transfer), not for the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. If the brain can do it, it IS possible and we can too, once we understand it. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed (fair test: can-fail, one-variable, real baseline).
> 5. **OPTIMIZE BY EXACT REPLICATION.** Evaluate aggressively, with great precision, EXACTLY how the brain does it, and replicate it exactly — copy the computation, SWEEP (never adopt) the parameters. No half-effort: the closer we are, the better we do.
> 6. **PERFORMANCE vs THE BRAIN.** How does our performance compare to a competent brain/reader on this task? WHERE ALONG THE CHAIN do we lose signal? What EXACTLY differs between our implementation and the brain's mechanism (an itemized mechanism-diff)?
> 7. **ADJACENT COMPONENTS.** Map the capabilities, limitations, opportunities, and brain-foundational status of the adjacent components — that seeds the next problems to address.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem? Is it FULLY brain-foundational, conveying ALL the benefits of the brain function we replicate? If not, keep pushing toward a fully complete, exceptional solution.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader can now track what happened, who did it, when, where, what caused what, what characters believed, and what they were trying to do — but not how they FELT. Feeling is a core part of following a story: readers continuously infer and update each character's emotional state, and it drives what they expect to happen next. The job: add a per-character "feelings" tracker that reads the plain emotional cues in the text ("was afraid", "felt a rush of joy", "angrily", "to her relief") and ties each to the right character, records whether it's positive or negative (and which emotion where possible), and answers "how does X feel / how did X feel about Y" — built the same way as the goal tracker we just added, on the reader's own extraction, no external AI.

## 2. WHY THIS ONE — it completes the classic situation-model dimensions, on a proven pattern
The goal-dimension landing (owner-DONE) gave the reader the 5th Zwaan-Radvansky dimension and, with it, a PROVEN pattern: a per-character register over the reader's own extraction (explicit constructions → coref-bound agent → status), additive + default-on, with a board arm. Affect is the best-attested remaining narrative dimension (Gernsbacher 1992 emotion-inference is robust; readers keep a running character-emotion model) and it REUSES that whole machinery (the coref canonicalizer, the extraction pattern, the register/query shape). It is a clean, high-value capability completion — and character affect is an input the goal/belief dimensions and next-mention prediction can compose with.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: emotion is a DISTINCT appraisal/affect system (amygdala/vmPFC/insula; Barrett's constructed-emotion — valence+arousal core affect conceptualized into categories), SEPARATE from mentalizing (goal/belief) and physical causation; narrative emotion is tracked as an updated character STATE (Gernsbacher-Goldsmith-Robertson 1992; de Vega 1996 — readers infer emotion even when not stated, but the RELIABLE anchor is the explicit emotion construction, mirroring the goal register's Tier-1). The reliable explicit anchors: emotion-predicate constructions (be/feel + emotion adj/noun: afraid/angry/glad/sad…), emotion verbs (fear/love/hate/rejoice…), and affective adverbs/"to X's N" (angrily; to her delight). VALENCE from a curated affect lexicon (NRC/Warriner valence norms = an admissible static offline asset; folded to category where the lexicon supports it). OUR-INVENTION-under-test: the cue set, the character-attachment rule (experiencer vs stimulus — "X feared Y": X is the experiencer), the valence/category mapping, the update/decay rule. Sweep, do not adopt. LOCATED-NEGATIVE tier: INFERRED (unstated) emotion ("she slammed the door" → anger) needs the world-knowledge/meaning channel — the same explicit-vs-inferred split the goal dimension found.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** the reader has all 5 Zwaan dimensions after the goal landing; the per-character-register pattern is proven (goal register: WANT-explicit CI-separated, agent-bound, additive default-on); the coref canonicalizer + extraction machinery is landed (`hdlab/goal_register.py`).
- **INFERRED (you must measure):** whether a glass-box per-character AFFECT register over explicit emotion constructions, bound to the resolved character (experiencer), answers "how does X feel" CI-separated over a most-recent-emotion-word floor with a shuffled-character info-free twin LOSING; extraction precision vs a reference; the valence accuracy; the explicit-vs-inferred residual + its named cause.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: `python tools/substrate_map.py`, `python tools/reader_capabilities.py`; read `hdlab/goal_register.py` IN FULL (the extractor + `make_canonicalizer` + `bind_agents` + `GoalRegister` + `track_status` + the reader `_read_goals` wire) — this is the template to MIRROR; read `hdlab/situation_reader.py` (`_read_goals`/`_read_belief`, the dimension block + flags) and the board arm pattern in `experiments/exp_situation_model_qa_v1.py` (the `goal` arm).
- Check for an existing affect/valence lexicon organ before building one (`tools/substrate_map.py`; grep `hdlab/` for valence/affect/sentiment).

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a glass-box per-character AFFECT register (explicit emotion constructions → coref-bound experiencer → valence[/category]; NO LLM) wired additive + default-on (mirroring the goal/belief/state dims; byte-identical to the OFF reader on the other dimensions) such that "how does X feel" scores CI-separated over a most-recent-emotion-word floor with a shuffled-character info-free twin LOSING, valence accuracy reported, no regression on the other dimensions. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE — explicit narrative affect cannot be bound glass-box (with the named cause), or inferred affect needs the meaning channel (the explicit-vs-inferred split) — is a FULL PASS. Strategy lands the Q111 wire + the board `affect` arm.

## ALREADY TRIED / DO NOT REDO
- The goal register (owner-DONE) is the TEMPLATE — REUSE its canonicalizer + register/query shape + the additive default-on wire; do not re-derive them. This is a SEPARATE dimension (affect ≠ intention; distinct brain system), not a goal-register tweak.
- The belief dimension (`track_belief`) handles what a character KNOWS, not how they FEEL — do not fold affect into belief (distinct appraisal system).
- Do NOT take a trained sentiment classifier / external LLM (the invariant) — valence from a curated static norm lexicon (an admissible offline foundation asset) + glass-box construction rules.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE `hdlab/goal_register.py` (the template), `hdlab/situation_reader.py` (mirror `_read_goals` for `_read_affect` + a `track_affect` flag), `experiments/exp_situation_model_qa_v1.py` (add the `affect` board arm). A valence norm lexicon is an admissible offline asset (ship to `data/frontend_assets/`). Strategy lands the Q111 wire. Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE
- Do NOT quote a score without the shuffled-character twin losing (else it is emotion-word recency, not character-bound affect).
- Do NOT claim the INFERRED (unstated) emotion slice without the meaning channel — anchor the pass on the explicit constructions (the reliable tier), like the goal dimension.
- Do NOT use an external LLM / trained classifier (the invariant).
