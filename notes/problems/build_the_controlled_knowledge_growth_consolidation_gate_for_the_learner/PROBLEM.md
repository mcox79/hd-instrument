---
priority: 1
review:
review_text:
---

# PROBLEM: knowledge growth is the BIGGEST lever on specific-sense selection (gloss→rich a_s +0.081 CI-sep) BUT raw/organic growth REGRESSES it (−0.015) — only CONSOLIDATED SyntagNet-quality knowledge helps. Build the CONTROLLED knowledge-growth / CONSOLIDATION gate: extract syntagmatic associations from the reader's own reading, CONSOLIDATE them (dedup / confidence-filter / cross-situational verify) to clean high-confidence associations, and prove that ADMITTING the consolidated knowledge to the sense signatures RAISES a_s CI-separated over gloss-only, with the RAW-ungated twin LOSING (it regresses). This IS "the clean foundation before learner-on," now a measured REQUIREMENT.

**slug:** `build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner` — **opened:** 2026-09-03 by the strategy session, the OWNER-FLAGGED top follow-on of the owner-DONE north-star continuation `build_sg_lite_self_supervised_scale_generative_sense_predictor` (which located this lever with numbers). **status:** OPEN. Strategy lands any hdlab wire (Q111, default-off, witnessed). Glass-box, NO external LLM at inference (the invariant); an offline self-supervised consolidation built as a static asset is admissible.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** The mission is the most brain-faithful substrate.
> **🧠 OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN do THIS?** Name the structure + computation, replicate that OPERATION as exactly as you can — the FIRST move. Mark each choice PINNED vs OUR-INVENTION.
> **🚀 EXPLORE FAR + WIDE for the mechanism**; if a MORE brain-foundational method conflicts with this brief, submit THAT (say why).
> **🧱 A SHARED WALL = GO DEEPER, not stop.** A rigorous located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`**; inherit its PINNED/INVENTED verdicts; add an AUDIT UPDATE for any deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The single biggest thing that improves picking a word's specific meaning is giving the model MORE world knowledge about which words go with which senses. But there's a catch we just measured: if the model grows that knowledge the naive way — by soaking up raw word co-occurrences from reading — the score gets WORSE, because raw co-occurrence is noisy. When the SAME kind of knowledge is CLEANED first (deduplicated, high-confidence associations only, of the sort a curated resource contains), it helps a lot. The brain has exactly this: it does not dump every experience straight into long-term semantic memory; it CONSOLIDATES slowly, replaying and cross-checking, keeping the reliable regularities and discarding noise. The job: build that consolidation gate — take the associations the reader extracts from its own reading, clean them to high-confidence syntagmatic associations, and prove that feeding the CLEANED knowledge in raises specific-sense accuracy while feeding the RAW knowledge in does not. This is the gate that must exist before we can safely "turn the learner on."

## 2. WHY THIS ONE — it is the measured requirement under the whole learner-on north star
From the parent (`exp_sg_lite_knowledge_growth_diagnostic_v1`, strict document-disjoint SemCor, subordinate senses, n=2676, through the winning biased-competition readout): gloss-only 0.239 → +WordNet-relations 0.284 → +SyntagNet (curated syntagmatic) 0.309 → +ConceptNet 0.320 (**gloss→rich +0.081 CI-sep [+0.046,+0.085]**, larger than any readout tweak) BUT **+ORGANIC raw w2v-NN 0.305 (−0.015)** — the same regression as the graph organ's raw `learn_from_text` co-occurrence (0.274→0.267). So the learner CAN grow this knowledge from reading, but ONLY through a consolidation/quality gate; uncontrolled growth is NEGATIVE, not neutral. This is the concrete, numbered form of the project's "clean foundation before learner-on" — the gate is the prerequisite for the entire learner-on programme.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: Complementary Learning Systems slow consolidation (McClelland, McNaughton & O'Reilly 1995) — the hippocampus fast-binds episodes; the neocortex SLOWLY extracts the reliable statistical structure, interleaving to avoid catastrophic noise; schema-consistent knowledge consolidates faster (Tse et al. 2007). Cross-situational statistical learning keeps regularities that recur across contexts and discards one-off co-occurrences (Yu & Smith 2007). So the gate = extract candidate associations from reading → keep only those that RECUR / are high-confidence / are cross-situationally verified (schema-gated) → admit. OUR-INVENTION-under-test: the exact confidence/recurrence/dedup criteria + the admission threshold (sweep). Mark PINNED vs OUR-INVENTION.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive — from the parent):** gloss→rich +0.081 CI-sep; SyntagNet +0.025..+0.058; RAW organic −0.015; raw `learn_from_text` co-occurrence 0.274→0.267 (flat-to-down). (Sources: `exp_sg_lite_knowledge_growth_diagnostic_v1`; `hdlab/grounded_semantic_graph.learn_from_text`.)
- **INFERRED (you must measure):** whether a glass-box consolidation gate over the reader's OWN extracted associations (extract → dedup/confidence-filter/cross-situational-verify → admit to the sense signatures) RAISES a_s CI-separated over gloss-only through the diagnostic-context readout, with the RAW-ungated twin LOSING CI-separated (it must reproduce the −0.015 regression), approaching the curated-SyntagNet ceiling (+0.058); the residual gap to curated + its named cause (extraction quality vs consolidation vs coverage).

## VERIFY BEFORE YOU START (the disk outranks this brief)
- **FIRST STEPS:** (1) understand ALL organs — `python tools/substrate_map.py`, `python tools/reader_capabilities.py`, skim `hdlab/`; (2) read IN FULL the parent `notes/problems/build_sg_lite_self_supervised_scale_generative_sense_predictor/SOLVED.md` (the KNOWLEDGE-GROWTH section + `exp_sg_lite_knowledge_growth_diagnostic_v1`); (3) `python tools/before_you_start.py "controlled knowledge growth consolidation gate learner"`.
- Reproduce on your own recompute: raw-organic −0.015 vs +SyntagNet +0.025..+0.058 through the diagnostic readout (the can-fail contrast — raw must hurt, clean must help).
- Inspect what you will REUSE: `hdlab/diagnostic_context_wsd.py` (the JUST-PROMOTED a_s readout instrument — score with this), `hdlab/grounded_semantic_graph.py` (`learn_from_text` = the RAW growth that regresses; the augmentable synset graph), SyntagNet (`data/syntagnet/…` = the clean-quality target), `hdlab/reading_grounding_loop.py` (the reader's separable co-occurrence store = the raw source), the sense-signature build. Heavy training → REMOTE GPU.

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a glass-box consolidation gate (extract → consolidate → admit; persisted as a static asset, NO external LLM) such that admitting the CONSOLIDATED knowledge raises a_s CI-separated over gloss-only on strict document-disjoint SemCor (subordinate senses, the diagnostic-context readout), with the RAW-ungated twin LOSING CI-separated (it must regress, reproducing −0.015) and NO net regression over MFS. Report CI half-width + null p95; strict document-disjoint is MANDATORY. A rigorous located NEGATIVE — no glass-box consolidation of reading-derived associations reaches curated quality, with the named ceiling + number — is a FULL PASS. Strategy lands any Q111 wire (default-off, witnessed).

## ALREADY TRIED / DO NOT REDO
- RAW `learn_from_text` co-occurrence growth — located NEGATIVE (regresses); the whole point is the CONSOLIDATION gate that raw growth lacks.
- The event/role-filler prediction TARGET — located NEGATIVE in the parent (4 tests); not this problem.
- The contextual-encoder ceiling fork (past ~0.35) — a SEPARATE owner decision, NOT this near-term lever; this problem is the knowledge lever (room to ~0.35).

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE `hdlab/diagnostic_context_wsd.py` (the a_s instrument), `hdlab/grounded_semantic_graph.py`, `hdlab/reading_grounding_loop.py`, SyntagNet. Heavy runs go REMOTE GPU. Strategy lands any hdlab wire (Q111, default-off, witnessed). Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE
- Do NOT quote leave-one-DOCUMENT-out a_s numbers — they leak; STRICT disjoint-document is the honest measure.
- Do NOT claim a knowledge-growth gain without showing the RAW-ungated twin REGRESSES on the same items (the whole result is that consolidation is REQUIRED, not that knowledge helps).
- Do NOT use an external LLM to consolidate or to score (the invariant); an offline glass-box consolidation asset is admissible.
