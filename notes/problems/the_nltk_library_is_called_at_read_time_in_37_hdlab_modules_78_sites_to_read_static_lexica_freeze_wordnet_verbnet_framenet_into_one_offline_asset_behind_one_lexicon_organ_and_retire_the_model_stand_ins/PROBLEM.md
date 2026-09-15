---
priority: 127
slug: the_nltk_library_is_called_at_read_time_in_37_hdlab_modules_78_sites_to_read_static_lexica_freeze_wordnet_verbnet_framenet_into_one_offline_asset_behind_one_lexicon_organ_and_retire_the_model_stand_ins
status: OPEN
review:
review_text:
---

# PROBLEM: 37 modules under `hdlab/` call the NLTK library at read time (78 import sites: WordNet in 33 modules, VerbNet in 3, FrameNet in 5, opinion_lexicon / stopwords in 2, plus two MODEL stand-ins -- `nltk.tag.PerceptronTagger` in `temporal_model.py:126` and `nltk.stem.PorterStemmer` in `morphology_leakage.py:29`), about 20 of them imported directly by `situation_reader.py`; the lexica are admissible foundation supply but the library reader is an external tool on the inference path (each module re-implements its own lookup, the lookups are not frozen, the dependency is undeclared, and a missing corpus download silently degrades a read) -- freeze every lexicon read the live path makes into ONE offline asset served by ONE hdlab lexicon organ, and remove the two model stand-ins from the live path.

**slug:** `the_nltk_library_is_called_at_read_time_in_37_hdlab_modules_78_sites_to_read_static_lexica_freeze_wordnet_verbnet_framenet_into_one_offline_asset_behind_one_lexicon_organ_and_retire_the_model_stand_ins` -- **opened:** 2026-09-15 by strategy from the external substrate evaluation (E12: `nltk` undeclared in `pyproject.toml`; the sense reader's lazy WordNet import) and strategy's own enumeration (`grep -n "^\s*(from|import)\s+nltk" hdlab/*.py`: 78 sites / 37 modules; the per-module table is in `notes/INTEGRATION_LEDGER.md` 2026-09-15).

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** The brain has no library call: lexical knowledge (senses, supersenses, argument frames, polarity) is STORED in the anterior-temporal hub and its spokes and is retrieved by content-addressed lookup at read time; acquisition happened offline (development). Our equivalent is a frozen foundation asset built ONCE from the vetted lexica (WordNet 3.0, VerbNet, FrameNet -- admissible static supply, owner 08-16 / 09-08) and served by one organ at read time with no external library in the call chain.
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- spaCy, GLUCOSE, MAVEN and ANY off-the-shelf parser/dataset/model are NOT brain-foundational; a vetted static offline FOUNDATION asset is admissible SUPPLY; an external tool AT INFERENCE is a DEFECT THAT BLOCKS. The two MODEL uses (the NLTK perceptron tagger, the Porter stemmer) are stand-ins: the perceptron is already off the live default (`HDLAB_TEMPORAL_TAGGER=counts_penn`, guarded 2026-09-15), the stemmer sits in a leakage test helper -- confirm neither is reachable on the default read and say so with the call graph.
> **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS:** `hdlab/meaning_foundation.py` is the curated hub (senses -> signatures). The frozen lexicon index is an ARM of it (or of `lexical_utils`), not a 38th private lookup: `synset -> lexname`, `lemma|pos -> ordered synsets`, `synset -> hypernym chain / lemmas / gloss` (only the relations the live path actually reads -- enumerate them), VerbNet `lemma -> classes / thematic roles`, FrameNet `lemma -> frames / core elements`, the opinion lexicon, stopwords. Every one of the 78 sites becomes a call into that organ.
> **BYTE-FAITHFUL FREEZE:** the organ must reproduce the NLTK answer the live path gets today on the live path's own queries (order of synsets included; NLTK's `synsets()` applies morphy -- the frozen form uses the exact-form index plus the WordNet exception lists plus OUR morphology organ's lemma, and the parity witness measures the disagreement with counts).
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md` and `notes/HOW_WALLS_WERE_BROKEN_2026-09-12.md` before writing wall / ceiling / negative.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** (a) Instrument the 78 sites: run the live reader over the 16-doc modern harness (pri 116's `exp_case_through_the_reader_v1.py`) and the full GUM test split with a recording shim on `nltk.corpus.wordnet/verbnet/framenet` (monkeypatch at the module attribute, read-only) to log every (module, function, corpus, query) actually made on the DEFAULT read; publish the table (sites reached / not reached; queries per document; relations used). (b) Build `tools/build_lexicon_foundation_index.py` -> `data/frontend_assets/lexicon_foundation_index_v1.json` (or .npz / sqlite if > 20 MB; the entity-type spoke uses sqlite already) covering exactly the relations logged in (a) plus the full synset->lexname and lemma->synsets tables (117,659 synsets, 147,306 lemmas, 45 lexnames). (c) One organ, `hdlab/lexicon_foundation.py` (or an arm on `meaning_foundation`), lazy-loaded, with the query functions the sites need; NO nltk import anywhere in hdlab/ on the live path afterwards (build tool only). (d) Rewire every reached site to the organ; unreached sites are rewired too or documented as dead with the call graph. (e) Parity witness: for every query logged in (a), organ answer == NLTK answer (report the count and the disagreements; morphy cases listed). (f) Declare the remaining build-time dependency in `pyproject.toml` under an optional `foundation-build` extra; the runtime extra must not require nltk.
> 2. **REUSE.** `hdlab/meaning_foundation.py` (the hub loader, `_load`, `sense_signatures`), `hdlab/lexical_utils.py:137`, `hdlab/underspecified_sense_reader.py` (`coarse_cluster`, `select_sense`), `hdlab/morphology.py` (our lemma), `data/frontend_assets/knowledge_foundation_manifest.json` (the asset manifest convention), `data/frontend_assets/entity_type_spoke_v1.sqlite` (the sqlite-asset convention), the 2026-09-05 rerouting of the perceptron tagger (owner-DONE `route_the_redundant_nltk_perceptron_tagger_through_the_fast_hdlab_tagger`), `tools/substrate_health.py`.
> 3. **GENERALIZE.** `verification/test_no_nltk_on_the_live_path.py`: (i) static -- no `nltk` import in hdlab/ except behind an explicit `_BUILD_ONLY` guard; (ii) dynamic -- the default read of the 16-doc harness with `sys.modules["nltk"]` poisoned (an import raises) completes byte-identically to the unpoisoned read.
> 4. **WALL -> DEEPER.** If a site needs a relation the frozen index does not carry (e.g. a similarity walk over the hypernym graph), freeze that relation too; the wall is never 'keep the library for this one'.
> 5. **OPTIMIZE BY EXACT REPLICATION;** nothing to sweep.
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** Byte-identity of the default read before/after on the 16-doc harness and the GUM test split (events, entities, states, senses, timeline); read time per document before/after (the frozen index should be faster than NLTK's lazy corpus reader); the full board, both arms in one process (must be identical); asset size and load time.
> 7. **ADJACENT.** pri 125 + 122 (running; do not touch `referent_per_np.py`, `situation_reader.py` `read()`/`_cm_agent_candidates`, `coref.py`, or `exp_situation_model_qa_modern_v1.py` -- if a rewired site lives in `situation_reader.py`, ship it as a separate hunk strategy applies after they land), the meaning-foundation program (`notes/KNOWLEDGE_LEVER_MAP_AND_LEARNER_STRATEGY_2026-09-04.md`).
> 8. **COMPLETION BAR.** Zero nltk imports on the live path (static + poisoned-import witness green); parity on every logged query (disagreements counted and explained); the default read byte-identical; the board identical; the dependency declared build-only -- OR a numbered located negative naming the site that cannot be frozen and why.

**(PHASE DIAGRAM.)** Nothing to sweep.
**(FULL-STACK UPSTREAM.)** Not a read-path change in substance; a supply-path change (library -> frozen asset).

## 1. THE PROBLEM IN PLAIN LANGUAGE
Thirty-seven parts of the reader open a dictionary through an outside software library every time they read. The dictionaries themselves are fine to use (they were built by people, offline); the library call at reading time is not, and each part does its own lookup its own way. Copy the parts of the dictionaries the reader actually uses into one frozen file served by one organ, prove the answers are the same, and make sure no outside library is called while reading.

## 2. WHY THIS ONE
The outside review flagged the undeclared dependency; strategy's count showed it is not one module but thirty-seven. It is the last broad class of external-tool-at-inference in the package, it is mechanical, and it makes the system installable and replayable.

## 3. MEASURED vs INFERRED
MEASURED: 78 import sites in 37 modules (grep, 2026-09-15); ~20 of those modules imported directly by the reader; the temporal tagger's live default is the organ's own Penn arm. INFERRED: which sites are reached on the default read (item 1a decides) and the asset size.

## 4. ALREADY TRIED / DO NOT REDO
Rerouting one site at a time (2026-09-05 did the perceptron; 36 modules remain); keeping the library 'because it is only a dictionary'.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
(1) `python tools/substrate_map.py`; (2) re-run the grep above and read every site in context; (3) read `hdlab/meaning_foundation.py`, `hdlab/lexical_utils.py`, `hdlab/underspecified_sense_reader.py`, `hdlab/temporal_model.py:120-190`, `pyproject.toml`; (4) `notes/SUBSTRATE_EVALUATION.md` E12.

## 6. THE BAR (can-fail)
See checklist item 8.

## 7. FILES AND ENTRY POINTS
Write ONLY: `tools/build_lexicon_foundation_index.py` (NEW), the asset under `data/frontend_assets/`, `hdlab/lexicon_foundation.py` (NEW), `verification/test_no_nltk_on_the_live_path.py` (NEW), `experiments/exp_lexicon_foundation_parity_v1.py` (your cell; `get_output_dir` per Q115), `notes/problems/<slug>/{SOLVED.md, lexicon_foundation_patch.diff}` (a unified diff for every EXISTING hdlab/ file you rewire; never edit existing hdlab/ files directly), `pyproject.toml` as a hunk in the same diff.

## 8. DO NOT QUOTE / DO NOT REDO
Retired figures: `notes/reference_retired_claims_never_requote.md`. 19c numbers are informational only.
