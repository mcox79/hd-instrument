---
priority: 2
review:
review_text:
---

# PROBLEM: specific-rare-sense selection is capped at a_s ~0.33-0.35 by the CONTEXTUAL INPUT ENCODING — one sense-conflated vector per surface form. The ceiling is triangulated (a small glass-box encoder on FROZEN w2v scores BELOW the parameter-free bag; static multi-sense embeddings are a brain-unfaithful dead-end). Build a genuinely CONTEXTUAL, glass-box, self-supervised input encoder (a scale-trained BiLSTM-LM / context2vec / ELMo-style contextual lexical representation — OUR model, trained offline, NO external LLM at inference) and prove it raises a_s CI-separated over the parameter-free bag (0.28) and the diagnostic-context readout (~0.33) on strict document-disjoint SemCor, with a shuffled-context twin LOSING — or a rigorous located NEGATIVE that names the residual and forces the invariant fork.

**slug:** `break_the_contextual_input_encoding_ceiling_for_specific_sense_selection` — **opened:** 2026-09-03 by the strategy session (OWNER-directed: "launch a project specifically to optimize this"), the ceiling fork of the owner-DONE north-star continuation `build_sg_lite_self_supervised_scale_generative_sense_predictor`. **status:** OPEN. Strategy lands any hdlab wire (Q111, default-off, witnessed). **⚠️ INVARIANT-SENSITIVE (owner decision embedded — see §3/THE FORK): a glass-box BiLSTM-LM/context2vec encoder is our own offline-trained model and is WITHIN the no-external-LLM invariant; a transformer/BEM-class encoder crosses an architecture the project has otherwise avoided and is an EXPLICIT owner call, NOT to be taken silently.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** The mission is the most brain-faithful substrate.
> **🧠 OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN do THIS?** Name the structure + computation, replicate that OPERATION as exactly as you can — the FIRST move. Mark each choice PINNED vs OUR-INVENTION.
> **🚀 EXPLORE FAR + WIDE for the mechanism**; if a MORE brain-foundational method conflicts with this brief, submit THAT (say why).
> **🧱 A SHARED WALL = GO DEEPER, not stop.** A rigorous located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`**; inherit its PINNED/INVENTED verdicts; add an AUDIT UPDATE for any deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
To pick a word's specific rare meaning, the model compares the word's context to dictionary senses. We proved the readout for that comparison is now near its best (biased competition). The thing still holding it back is UPSTREAM: every word is fed in as ONE fixed vector regardless of context, so a word used in a rare sense looks the same as when it's used in its common sense — the input has already blurred the distinction before any readout runs. We proved you cannot fix this by bolting a small network onto those fixed vectors (it scores worse than not bolting anything), and that pre-baking a separate vector per sense is a brain-unfaithful dead-end. The brain does NOT store one vector per word; it computes a context-SHAPED representation on the fly. The job: build that — a glass-box, self-supervised model that reads the sentence and produces a context-shaped vector for the target word — trained on our own text, no outside AI, and prove it picks the specific rare sense better than the current best.

## 2. WHY THIS ONE — the ceiling is triangulated, and the owner asked to optimize it
From the parent (3 research drills + 5 prototypes, strict document-disjoint SemCor, subordinate senses, n=2676): a_s is ~0.33 via the diagnostic-context readout; the covered-sense supervised bound is 0.35; a small glass-box bi-encoder (BiGRU context + gloss, BEM-lite) on FROZEN w2v scores 0.227-0.253 — BELOW the parameter-free bag 0.283, because the shortfall is the FROZEN INPUT (one sense-conflated vector per surface form), not tuning; a design-validation drill shows contextual+subword input alone (BERT-no-gloss 0.737 vs MFS 0.655) is ~HALF the total gap to SOTA. So the single highest-yield lever above the knowledge/consolidation lever is a genuinely CONTEXTUAL input encoder. Estimated: a scale-trained glass-box BiLSTM-LM contextual encoder reaches ~0.40 (the one untested glass-box route); a transformer reaches ~0.53 (SOTA-LFS) but crosses the invariant boundary.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: lexical meaning is CONTEXT-SHAPED at access — the same word form is represented differently by its sentential context (predictive coding over the unfolding sentence; the N400 is graded by contextual fit — Kutas-Federmeier; contextual lexical processing in temporal cortex is dynamic, not a fixed lookup). A recurrent language model that predicts the word from its bidirectional context and exposes its hidden state as the word's contextual representation (context2vec, Melamud 2016; ELMo, Peters 2018 — both PRE-transformer, glass-box, unsupervised) is the faithful glass-box analog. OUR-INVENTION-under-test: the exact encoder class / scale / objective + how its contextual vector feeds the diagnostic-context readout (sweep). Mark PINNED vs OUR-INVENTION. **THE FORK (name it explicitly, do NOT silently cross it): if the glass-box recurrent encoder caps materially below target, the transformer/BEM-class encoder is an OWNER decision — surface it with the measured glass-box ceiling, do not build a transformer without that decision.**

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive — from the parent):** a_s ~0.33 (diagnostic readout) / 0.283 (bag); BEM-lite bi-encoder on frozen w2v 0.227-0.253 (< bag — the frozen-input proof); contextual+subword input ~half the gap to SOTA; static per-synset sense embeddings a brain-unfaithful dead-end (circular). (Sources: `exp_sg_lite_context_encoder_wsd_v1/v2`; `notes/research_wsd_*_2026-09-03.md`.)
- **INFERRED (you must measure):** whether a scale-trained glass-box CONTEXTUAL encoder (BiLSTM-LM / context2vec / ELMo-style, self-supervised on ~277M tokens, its contextual state feeding the diagnostic-context readout) raises a_s CI-separated over the bag (0.283) AND the diagnostic readout (~0.33) on strict document-disjoint SemCor, shuffled-context twin LOSING; the glass-box ceiling + its named cause; whether it forces the transformer fork (with the number).

## VERIFY BEFORE YOU START (the disk outranks this brief)
- **FIRST STEPS:** (1) understand ALL organs — `python tools/substrate_map.py`, `python tools/reader_capabilities.py`, skim `hdlab/`; (2) read IN FULL the parent `notes/problems/build_sg_lite_self_supervised_scale_generative_sense_predictor/SOLVED.md` (the HOW-FAR-CAN-WE-GO ceiling section) + the three `notes/research_wsd_*_2026-09-03.md` notes (they detail the contextual-encoding arms + the design-validation calibration); (3) `python tools/before_you_start.py "contextual input encoder BiLSTM context2vec ELMo sense selection"`.
- Reproduce on your own recompute: BEM-lite bi-encoder on frozen w2v 0.227-0.253 < bag 0.283 (the can-fail frozen-input proof the contextual encoder must beat).
- Inspect what you will REUSE: `hdlab/diagnostic_context_wsd.py` (the a_s READOUT instrument — the encoder feeds it), `experiments/exp_sg_lite_context_encoder_wsd_v1/v2.py` (the frozen-input BEM-lite prototypes), `experiments/exp_sg_lite_sense_gestalt_v1.py` (the w2v/gestalt build), the WordNet/SemCor/gloss + the ~277M reading corpus. Heavy training → REMOTE GPU (needs gensim/torch on the runner).

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a self-supervised glass-box CONTEXTUAL input encoder (BiLSTM-LM/context2vec/ELMo-class; OUR model, persisted as a static asset, NO external LLM at inference) whose contextual target representation, fed to the diagnostic-context readout, raises a_s CI-separated over BOTH the parameter-free bag (0.283) AND the diagnostic-context readout on frozen w2v (~0.33) on strict document-disjoint SemCor (subordinate senses), with a shuffled-context twin LOSING CI-separated and NO net regression over MFS. Report CI half-width + null p95; strict document-disjoint is MANDATORY. A rigorous located NEGATIVE — the glass-box contextual encoder does NOT cross the frozen-input ceiling, with the named cause + number + the transformer-fork it forces — is a FULL PASS. Strategy lands any Q111 wire (default-off, witnessed).

## ALREADY TRIED / DO NOT REDO
- BEM-lite bi-encoder on FROZEN w2v — located NEGATIVE (< bag; the frozen input is the cap). The lever is a TRAINED CONTEXTUAL input, not a network on frozen vectors.
- Static per-synset / multi-prototype sense embeddings — research dead-end (circular, brain-unfaithful for topic-overlapping polysemy).
- The event/role-filler target + the role-specific selectional-fit (rmax) readout — BOTH located negatives (rmax −0.0247 CI-sep below mean); NOT this problem.
- Knowledge growth / consolidation — the SEPARATE `build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner` (priority 1, the near-term lever to ~0.35). THIS problem is the ceiling ABOVE that.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE `hdlab/diagnostic_context_wsd.py` (the a_s instrument), `exp_sg_lite_context_encoder_wsd_v1/v2.py`, `exp_sg_lite_sense_gestalt_v1.py`, the corpus/WordNet/SemCor assets. Heavy training → REMOTE GPU. Strategy lands any hdlab wire (Q111, default-off, witnessed). Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE / DO NOT DO
- Do NOT quote leave-one-DOCUMENT-out a_s — it leaks; STRICT disjoint-document is the honest measure.
- Do NOT build or fine-tune an EXTERNAL LLM, and do NOT build a transformer encoder WITHOUT the explicit owner fork decision (surface the glass-box ceiling first). An offline self-supervised glass-box recurrent encoder is admissible.
- Do NOT re-open the readout (biased competition is the best glass-box readout, wired) or the event/role target (exhausted).
