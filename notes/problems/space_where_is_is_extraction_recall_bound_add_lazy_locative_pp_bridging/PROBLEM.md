---
status: INTEGRATED
review: EXCELLENT
review_text: "EXCELLENT PARTIAL, INTEGRATED_BY_STRATEGY 2026-09-06. Disk-outranks-brief: the lazy locative-PP bridge is a LOCATED NEGATIVE (recall 0.444->0.889 moves where_is only +0.064); the real lever is NAMED-GROUND BINDING (Talmy Figure/Ground + VerbNet Goal gate + Figure-Ground compound head + closed-class partitive + GRADED ConceptNet-AtLocation functional-locus typing, no hand list). Modern where_is 0.319->0.468 (+0.149; beats floor + shuffled-ground twin CI-sep; precision 0.571->0.702); LIVE read() 0.277->0.447 (+0.170). WIRE LANDED default-on in prior_ext (conservative=True only; aggressive + anticipatory paths are located negatives, kept off) VERBATIM into experiments/_space_reader.py; additive-safe (who-did-what byte-identical). Graded on MODERN per the owner no-19c directive (the n=606 19c corpus is banned; the +0.149 is under-powered over the current chain at n=47 -> the modern-gold expansion must close the power gap). Witness verification/test_space_ground_binding.py 5/5. Follow-ons filed: Ground-aware goal-PP attachment; fold Ground typing into the shared role router (coordinate w/ p3); a modern where_is board arm. See BRAIN_FOUNDATIONAL_AUDIT.md 2b (2026-09-06)."
---

# PROBLEM: the SPACE dimension loses ~everything at motion-event extraction RECALL — it fires a location update only on a closed motion-verb lexicon, where the brain updates a persistent WHERE-state from ANY location-entailing predicate (lazy locative-PP bridging); a brain-foundational bridge is PROTOTYPED (recall 0.444→0.889) and the rest of the fix is REUSE.

**slug (proposed):** `space_where_is_is_extraction_recall_bound_add_lazy_locative_pp_bridging` — **candidate follow-on filed by the solver** of `consolidate_the_arceager_and_arc_double_parse...` (the signal-loss ladder localized the space loss to extraction recall; the owner asked to diagnose it, find the brain mechanism, and prototype the fix — done). **status:** CANDIDATE (strategy files + prioritizes). Glass-box, NO external LLM. Strategy lands any hdlab wire (Q111).

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** Iterate to the OPTIMAL brain-foundational solution; do NOT submit the first thing that clears. The OPENING MOVE is "how does the BRAIN actually do this?" — name the structure/circuit + replicate the OPERATION. A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed. Run a 30-min deepening cron; cancel + submit only when the brain-mechanism bar is met AND nothing more of value remains.

> ## 🧠 BRAIN-FOUNDATIONAL CHECKLIST (work through IN ORDER; not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Name the structure + computation; PINNED vs OUR-INVENTION. RESEARCH where unsure.
> 2. **REUSE — does an existing organ already do it?** Check `tools/substrate_map.py` / `hdlab/` FIRST.
> 3. **GENERALIZE — how does the brain generalize it?** Build for that.
> 4. **HIT A WALL? GO DEEPER.** A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, failed.
> 5. **OPTIMIZE BY EXACT REPLICATION.** Copy the computation, SWEEP the parameters.
> 6. **PERFORMANCE vs THE BRAIN.** Where do we lose signal? The mechanism-diff.
> 7. **ADJACENT COMPONENTS.** Map the neighbours — seeds the next problems.
> 8. **COMPLETION BAR.** COMPLETE + EXCELLENT + conveys the full benefit?

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader can sometimes say where a character is, but it misses most of the moves. It only notices a location change when a sentence uses an explicit "moving" verb (go, walk, come). But stories put people places without a moving verb all the time — "she waited on the platform," "he found a desk on the third floor," "he stayed there." People track where everyone is continuously, updating from *any* sentence that implies a place, not just moving verbs. The job: make the reader do that.

## 2. WHY THIS ONE — the space dimension is recall-capped, and the fix is mostly REUSE
A signal-loss ladder on the SPACE chain (modern gold) localized the loss precisely: the register/read-out is near-lossless (ceiling ~0.79 given perfect extraction) and it is parse-quality-independent (arc-eager == base parser for recall) — the ENTIRE loss is motion-event EXTRACTION RECALL (0.444: the chain detects <half of gold location changes). The biggest new lever is prototyped and works; the rest is wiring organs that already exist.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED (research `notes/research_spatial_recall_beyond_motion_verbs_2026-09-05.md`): the reader maintains a persistent **protagonist-anchored WHERE-state**, updated from ANY location-entailing predicate via **lazy locative-PP bridging** — an on-demand inference that resolves a locative phrase to the entity's current place (McKoon & Ratcliff 1992 on-demand inference; the Basic Locative Construction; Zwaan & Radvansky 1998 event-indexing SPACE; Rinck & Bower protagonist-anchored spatial access) — NOT a closed motion-verb lexicon. Honest temper: spatial updating is partly attention/strategy-gated, not purely obligatory-continuous.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** the space loss is extraction RECALL, not register/read-out (ceiling 0.79) and not parse quality (arc-eager==base recall 0.444). Miss taxonomy (modern 7 + 19c 15): ~⅓ coref/mover-tracking, ~⅓ node/timing/complex, ~13% narrow motion lexicon, ~13% stative/deictic. Gates are NOT the cause (toggle = +0.000 recall); naive fire-on-any-goal-role HURTS (−0.074). **PROTOTYPED (`experiments/exp_space_recall_brainfoundational_v1.py`): a lazy locative-PP bridge + WordNet place-taxonomy typing lifts motion-event recall 0.444→0.889 at HIGHER precision (0.571→0.739) and end where_is 0.319→0.383, shuffled-place twin loses (+0.128 where_is over twin — the place CONTENT is load-bearing).**
- **INFERRED (you must measure):** does landing the bridge into the live `_space_reader`/`decide_motion` hold the gain end-to-end on the board? does reusing `EntityBinder` recover the ~⅓ coref misses? does `grounded_semantic_graph` ConceptNet AtLocation type the world-knowledge places ("board"→plane) the WordNet taxonomy misses? the final where_is CI-margin over floors + twin.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `experiments/exp_space_recall_brainfoundational_v1.py` (the working prototype), `experiments/_diagnose_space_recall.py` (the miss taxonomy), and `notes/research_spatial_recall_beyond_motion_verbs_2026-09-05.md`.
- Read the space chain IN FULL: `experiments/_space_reader.py` (`decide_motion`, `extract_events_in_substrate`, `fold_tracker`, `_node_from_token`), `hdlab/location_register.py`. Understand ALL organs first: `python tools/substrate_map.py`; skim the REUSE organs below.
- Reproduce: run the prototype; confirm recall 0.444→0.889 + the twin-separation.

## THE BAR (a real, brain-foundational recall recovery)
PASS = where_is on the MODERN space gold CI-separated over BOTH the current motion-lexicon chain AND the strongest stateless floor (last-mention), with the info-free shuffled-place twin LOSING, motion-event recall materially recovered, and NO precision regression — landed through the LIVE reader (not just the prototype harness). A rigorous located NEGATIVE (the brain's on-demand locative bridging, faithfully built, does not hold end-to-end, with the exact stage that eats the gain named) is a FULL PASS. Report the recall + where_is deltas with CIs + the twin.

## REUSE FIRST (ingredients already on the shelf — none wired to space)
- **Mover-coref (~⅓ of misses):** `hdlab/world_state_entity_binding.EntityBinder` — the Stage-1 reference→canonical-entity dispatcher, ALREADY wired for the possession dimension (`densify_world_state`); reuse it for space movers. Also `hdlab/scene_segment` (per-scene protagonist coref) for same-gender-competitor misses.
- **World-knowledge places (the WordNet taxonomy misses some):** `hdlab/grounded_semantic_graph` carries ConceptNet **AtLocation** (+IsA/PartOf) edges — type "board→plane", "berth", "radiology" as places / at-locations.
- **Deixis / here-center:** `hdlab/perceptual_access_ledger` (DEIXIS_AWAY/TOWARD — the space lexicon already borrows it); **goal→destination:** `hdlab/goal_register`.
- **The one genuinely-NEW piece is PROTOTYPED here:** the lazy locative-PP bridge (`experiments/exp_space_recall_brainfoundational_v1.py`). Land it; then layer the reuse organs.

## FILES AND ENTRY POINTS
Prototype + diagnosis: `experiments/exp_space_recall_brainfoundational_v1.py`, `experiments/_diagnose_space_recall.py`, `experiments/exp_space_modern_brainfoundational_v1.py` (the signal-loss ladder). The wire (if landed) is in `experiments/_space_reader.py` (`decide_motion`/`extract_events_in_substrate`) + `hdlab/situation_reader._read_space`; strategy lands the Q111 wire. Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md`.

## ALREADY TRIED / DO NOT REDO
- The refuted EASY fixes are located negatives ON DISK — do NOT re-run: toggling the noisy-channel gates (+0.000 recall) and naive fire-on-any-goal-role broadening (−0.074 recall). The lever is NOT a gate toggle or a blanket broadening — it is the lazy locative-PP bridge over location-entailing predicates.
- Parse QUALITY is a located negative for space recall — arc-eager == base parser recall (0.444). Do NOT chase the parser (the double-parse consolidation is now landed; arc-eager is the sole read-path parse); the lever is the extraction TRIGGER.
- The one genuinely-new mechanism (lazy locative-PP bridge, recall 0.444→0.889) IS prototyped — build ON it, do not re-derive it.

## COORDINATION (does NOT conflict with the in-flight substrate streamlining)
This rides on top of the just-landed parser CONSOLIDATION (single arc-eager parse) — space recall is parse-INDEPENDENT, so the consolidation neither helps nor hurts it. It REUSES `grounded_semantic_graph` (ConceptNet AtLocation) — the SAME module the curated-meaning wire touches, but a DIFFERENT function (AtLocation vs `select_sense`); strategy lands both wires, no collision. Prototype in `experiments/`; strategy lands the Q111 wire. No live-code overlap with the pass.

## DO NOT QUOTE
- Do NOT quote a where_is gain without the shuffled-place twin LOSING (the twin fires at the same rate; only the place CONTENT may carry signal).
- Do NOT chase parse QUALITY for space recall — it is parse-independent (arc-eager==base recall). The lever is the extraction TRIGGER (location-entailing predicates), not the parser.
- NO external LLM (the invariant); place-typing is WordNet/ConceptNet taxonomy, glass-box.
