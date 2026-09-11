---
priority: 12
slug: the_lemmatizer_is_wordnet_morphy_at_inference_not_a_glass_box_morphological_decomposition
status: OPEN
review:
review_text:
---

# PROBLEM: the substrate's lemmatizer — the rung EVERY meaning channel, the grounding loop, coref keys and the causal/definitional readers pass through — calls WordNet `morphy` through nltk AT READ-TIME in ~10 organs (`thematic_role_labeler.lemma_word`, `lexical_utils.concept_lemma`, `causation_typing`, `definitional_extraction`, `definitional_predicate_v61`, `event_type`, `generalized_event_knowledge`, …). The COMPUTATION (morphological decomposition: strip affixes, check the stem against a lexicon; Rastle & Davis 2008) is brain-foundational; the IMPLEMENTATION is an external tool at inference, which violates THE invariant. Replace it with ONE glass-box morphology organ whose output is BYTE-IDENTICAL to today's, built from an offline foundation asset, and repoint every call site.

**slug:** `the_lemmatizer_is_wordnet_morphy_at_inference_not_a_glass_box_morphological_decomposition` — **opened:** 2026-09-11 by strategy (found by the pri-5 solver's FULL_CHAIN_BF_AUDIT, rung 1, as "the deepest residual"; confirmed by strategy at integration: with the fused sense-assignment read landed, this is the LAST non-glass-box rung on the meaning chain from raw text to the sense decision). **status:** OPEN.

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate, not the fastest green check.
> **THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure / circuit and the computation it performs, and replicate that OPERATION as exactly as you can — the FIRST move, not a tiebreaker.
> **YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE.** Read the neuroscience; cross domains; if a MORE brain-foundational structure than this brief names emerges, submit THAT instead (say what is incompatible and why yours is more faithful).
> **A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
> **"CONVERGED" HAS A HIGH BAR.** Claim it only when you have (a) identified how the brain performs this computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL, and spaCy/GLUCOSE/MAVEN + any off-the-shelf parser/dataset/model are NOT brain-foundational — never reach for a convenient/easy tool without careful consideration** (a vetted static offline FOUNDATION asset — WordNet's exception lists and word-form index EXPORTED ONCE at build time — is admissible SUPPLY; nltk/WordNet called AT INFERENCE is the DEFECT this problem removes).
> **🧩 ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS (owner 2026-09-10):** morphological decomposition is ONE structure — deliver ONE organ (`hdlab/morphology.py` or an arm of `lexical_utils`) with POS-specific arms, and make `lemma_word` / `concept_lemma` / the per-organ `wn.morphy` calls DELEGATE to it. Do not leave two lemmatizers. Consult `BRAIN_STRUCTURE_CONSOLIDATION_AUDIT.md` before adding anything.
> **A rigorous negative is a PASS** — but only if what failed was the brain's actual mechanism, faithfully built.
> **REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale.

> ## BRAIN-FOUNDATIONAL CHECKLIST (work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Visual word recognition decomposes a written form into stem + affix EARLY and form-based (Rastle & Davis 2008 "morpho-orthographic" segmentation: `corner`→`corn+er` fires too), then checks the candidate stem against the lexicon (lexical-decision/priming evidence; Taft 1979 affix-stripping). Irregulars (`went`→`go`) are STORED whole (dual-route: Pinker-Ullman words-and-rules). Replicate exactly that: an exception STORE + affix-detachment RULES + a lexical CHECK. That is what `morphy` computes; build the computation, not the tool.
> 2. **REUSE + ONE-STRUCTURE-ONE-ORGAN** — REUSE `thematic_role_labeler.lemma_word`'s existing irregular table + guarded suffix fallback and `lexical_utils.concept_lemma`'s contract (non-alpha-safe, never `""`); EXPORT WordNet's `*.exc` exception lists + the word-form index ONCE into a static asset under `data/frontend_assets/` (offline foundation; build script committed, asset gitignored or small enough to commit — state which). No nltk import on any read path.
> 3. **GENERALIZE — does it need to, and how does the brain?** Serve the POS-specific arms every call site uses today (`n` / `v` / `a` / `r` / POS-generic noun-first), out-of-lexicon coinages (keep the surface form, as today), and proper nouns.
> 4. **HIT A WALL → GO DEEPER, don't stop.** If byte-identity to `morphy` fails on some slice (e.g. multi-candidate ambiguity `axes`→`axe`/`axis`), name the slice with a count and either make the tie-break the brain's (frequency / lexical-decision) or document the exact divergence set — never approximate silently.
> 5. **OPTIMIZE BY EXACT REPLICATION** — copy morphy's detachment rules and exception handling exactly; SWEEP nothing that changes outputs (this is a fidelity port, not a tuning problem).
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM** — the bar is BYTE-IDENTICAL output to the current path on every call site's real input distribution (the reading-grounding curriculum, UD-EWT/GUM tokens, WiC/SimLex vocab) PLUS the downstream witnesses unchanged: `test_fused_sense_ranker_live.py`, `test_meaning_fusion_live_coverage.py`, `test_cn_conceptkey_binding.py`, the board `--self-test` AGG (0.6313 standing). Load time ≤ the current nltk path.
> 7. **ADJACENT COMPONENTS.** WordNet TAXONOMY reads (`typed_spokes` is-a, `coarse_cluster`, `animacy_lexicon`, `conceptual_meaning`) are a SEPARATE question (a curated taxonomy foundation asset read at inference is admissible supply per the owner; the taxonomy is NOT this problem) — do not scope-creep into them, but LIST every remaining `nltk` import on the read path in your submission so the next problem can be posted precisely.
> 8. **COMPLETION BAR.** One glass-box morphology organ, no nltk on the read path of any organ that lemmatizes, byte-identical lemmas on the real input distributions (with the divergence set, if any, enumerated and counted), all named witnesses green, registry tags + §2b AUDIT UPDATE — OR a rigorous located negative naming exactly which slice cannot be made glass-box and why.
>
> **(PHASE DIAGRAM.)** Nothing here is a swept parameter; the operating point is fixed by fidelity to the current output.
> **(FULL-STACK UPSTREAM.)** Repoint EVERY call site (grep `morphy` in `hdlab/`), run every downstream witness, and ACCEPT that a divergence set, if found, changes downstream numbers — report them, do not hide them.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Before the reader can look a word up, it has to turn "dogs" into "dog" and "went" into "go". Today it asks an outside dictionary tool to do that every time it reads. The way the brain does it is well understood (peel the ending, check the stem is a real word, and keep a short list of exceptions), and we can build exactly that ourselves from a one-time export of the dictionary — so nothing external runs while the reader reads. The output must be identical to today's, so nothing downstream changes.

## 2. WHY THIS ONE — the deep root, under the HARD 100%-BF gate
The owner's invariant is "no external tool at inference". With the fused sense-assignment read landed (2026-09-11), every other rung from raw text to the sense decision is the brain's computation; this rung is the one external call left, and it sits under EVERY meaning channel, the grounding loop, common-noun coref keys, event typing and the definitional/causal readers. It is small, well-defined, witnessable by byte-identity, and removes a pipeline-wide defect.

## 3. MEASURED vs INFERRED
- **MEASURED (on disk):** `grep -n morphy hdlab/*.py` → ~10 organs call `wn.morphy` at read-time; `lemma_word` order is irregular table → morphy(n,v,a,r) → guarded suffix rules; the pri-5 FULL_CHAIN_BF_AUDIT rung 1 records this as the deepest residual (computation BF, implementation external, non-circular w.r.t. similarity golds, changes no measured number).
- **INFERRED (to prove WITH A NUMBER):** that a glass-box export + rules + lexical check reproduces morphy byte-for-byte on the real input distributions (report the divergence count, target 0), at no load-time cost.

## 4. ALREADY TRIED / DO NOT REDO
- Do NOT replace the lemmatizer with a trained model (a fitted stand-in is a defect) or with a crude regex (the pre-2026-09-10 `head_lemma` regex empty-collapsed redactions and over-stripped `-us/-es` — a documented defect that `concept_lemma` fixed).
- Do NOT touch WordNet TAXONOMY consumers (separate problem; list them).
- Do NOT import nltk anywhere on a read path; an offline BUILD script may.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Understand ALL existing organs first: `python tools/substrate_map.py`; read `hdlab/thematic_role_labeler.py::lemma_word`, `hdlab/lexical_utils.py::concept_lemma`, and every `morphy` call site (`grep -rn morphy hdlab/`). Read IN FULL: `notes/problems/measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage/FULL_CHAIN_BF_AUDIT.md` (rung 1 + its correction) and the `concept_lemma` section of `notes/problems/the_common_noun_binder_is_string_identity_not_the_brains_content_addressable_typed_coref/SOLVED.md`. Check `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (2026-09-11 pri-5 entry) for the recorded deviation.

## 6. THE BAR (can-fail; a rigorous located-negative naming the exact ceiling WITH a number is a full pass)
One glass-box morphology organ (exception store + affix-detachment rules + lexical check, from a one-time offline export), every read-path `morphy` call repointed, BYTE-IDENTICAL lemmas on the real input distributions (divergence set enumerated, target 0), all named downstream witnesses + the board self-test unchanged, no nltk on the read path — OR a numbered located negative naming the slice that cannot be made glass-box and why.

## 7. FILES AND ENTRY POINTS
`hdlab/thematic_role_labeler.py` (`lemma_word`, `_IRREGULAR_LEMMA`, `_wordnet()`), `hdlab/lexical_utils.py` (`concept_lemma`), `hdlab/causation_typing.py`, `hdlab/definitional_extraction.py`, `hdlab/definitional_predicate_v61.py`, `hdlab/event_type.py`, `hdlab/generalized_event_knowledge.py` (call sites); `hdlab/reading_grounding_loop.py::normalize_lemma` (the grounding loop's entry); `data/frontend_assets/` (where the exported asset lives); witnesses `verification/test_fused_sense_ranker_live.py`, `verification/test_meaning_fusion_live_coverage.py`, `verification/test_cn_conceptkey_binding.py`; the board `experiments/exp_situation_model_qa_modern_v1.py --self-test`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT re-introduce the crude `head_lemma` regex. Do NOT use spaCy / any external LLM / nltk at inference. Do NOT scope-creep into WordNet taxonomy consumers (list them instead). Do NOT approximate silently — enumerate any divergence from today's output.
