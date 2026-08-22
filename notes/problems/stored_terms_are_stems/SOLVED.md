---
problem: stored_terms_are_stems
status: PARTIAL
bar: NAME the call that emits `analysi`; FIX it so a non-lemma word is left alone not truncated; SHOW the true-stem drop on a freshly built store (same population, same round-trip detector, before/after); PROVE inflection is not broken vs the gold the 2026-08-13 repair used (53.50% -> 99.03%).
result: Fresh store built on HEAD = 0/141 distinct subjects = 0.00% true stems (reading:simplewiki 0/49, substrate_seed 0/92); stale v2_qualityfix = 119/1512 = 7.87% (reading sources 8.70-16.73%). Lemmatizer over 93,338 Lancaster+Brysbaert+WordNet forms: pre-01093ac1f lemma_verb = 8,692 non-words, HEAD = 0. Inflection preserved: verb gold 53.50%->99.03% (git 7d6036bca; witness block B passes), dogs->dog, arteries->artery, walked->walk.
floor: Detector both controls PASS. Negative control (16 real words incl. function words) = 0 false positives ONLY after excluding function words (before that it false-flagged and->andes etc, inflating the raw rate 8.40%->7.87%); positive control = 7/7 known chops flagged. The detector scores the stale store at 7.87% and the pre-fix function at 8,692/93,338, so 0.00% on the fresh store is a measured AFTER, not a detector that cannot fire (information-free arm loses).
controls: (1) detector NEGATIVE control caught a function-word false-positive: fresh substrate_seed 10/92 were all real stopwords (and->andes, with->withe), corrected to 0/92 by adding a function-word list; (2) detector POSITIVE control = 7 known chops all flagged; (3) inflection POSITIVE control (verb gold + dogs->dog) proves the fix did not disable normalization; (4) end-to-end fresh build rules out hypothesis (d) corpus-origin stems: reading:simplewiki = 0/49 excluded.
files_changed: notes/problems/stored_terms_are_stems/probe_stem_diagnosis.py, notes/problems/stored_terms_are_stems/measure_before_after.py, notes/problems/stored_terms_are_stems/build_fresh_store_and_measure.py. NO hdlab change: the fix already landed on HEAD (commits 01093ac1f + 7d6036bca).
reverify: cd d:/AI/hd-instrument && .venv/Scripts/python.exe notes/problems/stored_terms_are_stems/measure_before_after.py
---

## What this turned out to be

**The chopping call is named, and it was already fixed on 2026-08-13 — nine days before this
store was built is wrong; the store was built the day BEFORE the fix.** The owner's observation is
real (the store genuinely holds `analysi`, `cigarett`, `apoptosi`, `christma`), but there is **no
live chopping bug to stop** — the damage is a stale data artifact.

- **The call:** `normalize_lemma` ([hdlab/reading_grounding_loop.py:230](../../../hdlab/reading_grounding_loop.py#L230))
  — the single chokepoint for every stored subject, used both by the reading path and by
  `seed_known_words` ([reading_grounding_loop.py:1247](../../../hdlab/reading_grounding_loop.py#L1247)).
  Before commit `01093ac1f` it resolved to the **unguarded `lemma_verb` suffix stripper**
  ([hdlab/thematic_role_labeler.py](../../../hdlab/thematic_role_labeler.py)), which strips terminal
  `-s`/`-e`/`-es` with no check. Runtime evidence, not grep: run against the 93,338-form
  Lancaster+Brysbaert+WordNet dictionary, that pre-fix function turns **8,692** words into non-words
  — a number that reproduces the repair commit `7d6036bca`'s own "8,692 -> 0" headline exactly.
- **The fix (already on HEAD):** commits `01093ac1f` (guarded `lemma_word`) and `7d6036bca` (guarded
  `lemma_verb`) added a `is_known_word(residue)` gate to every suffix rule — strip only if what
  remains is a real word. HEAD produces **0** non-words over the same dictionary. Direct runtime
  test on all 13 owner-cited words: none is chopped (`analysis->analysis`, `cigarette->cigarette`,
  `arteries->artery`).
- **The drop, on a freshly built store:** a fresh `Substrate` read on HEAD scores **0.00%** true
  stems (both seed and reading) against the stale store's **7.87%**, same round-trip detector.
- **Inflection is not broken:** the verb gold holds (53.50%->99.03%, git-corroborated; witness
  block B passes), and `dogs->dog`, `arteries->artery`, `walked->walk` all still normalize.

## Brain-faithfulness (the north star)

The fix is not a convenient tool — it happens to implement the brain's own mechanism. The
masked-priming literature (Rastle & Davis; Marslen-Wilson) shows morphological decomposition is a
two-stage process: an early, blind, form-based parse (`corner`->`corn`) that is then **lexically
gated** — the residue must be an independently valid lexical unit (and, later, semantically
related) or the word reverts to a whole. **The brain never settles on a non-word residue like
`analysi`.** The old stripper was the blind stage with no gate; the HEAD guard IS the lexical
gate. One place HEAD is *less* faithful: its out-of-WordNet fallback checks lexical validity but
not semantic relatedness, so a rare `corner->corn`-type false-merge is possible for out-of-WordNet
terms (WordNet-morphy-first prevents it for in-dictionary words). That is a future refinement, not
the stem bug.

## What I did NOT establish

- **I did not rebuild the CANONICAL foundation.** `data/foundation/` is read-only/owner-gated, so
  the fresh store is a *new* store on a *different* corpus (simplewiki), not a byte-for-byte rebuild
  of the bio/ele/adv textbook segments. The same-corpus gap is covered by the 93,338-form
  dictionary sweep (population-independent: HEAD emits 0 non-words on *any* word), but the
  fresh-vs-stale stores are same-metric/same-detector, not same-corpus.
- I did not locate the exact original build cell or the 878-word `seed_base_vocabulary` surface
  list; not needed once the sweep shows the lemmatizer is clean on the whole dictionary.

## What I would withdraw first if wrong

The claim that the fresh reading path is "0 chops on any corpus." It is 0 on simplewiki (49
subjects) and 0 over the 93,338-form dictionary; a pathological corpus of out-of-WordNet inflected
technical terms could in principle hit a fallback-rule edge the sweep did not contain — though the
sweep includes technical vocabulary and found none.

## Why PARTIAL, and the one remaining action (out of the solver's lane)

The code-level bar is fully met: the call is named, it is fixed, the drop is shown (7.87%->0.00%),
inflection is preserved. But the **live system still stores stems today**, because the canonical
foundation everything reads (`reading_grounding_v2_qualityfix`) is the pre-fix store. Making the
running system clean requires **rebuilding and repointing the foundation with HEAD code** — a
store-write to `data/foundation/` that is read-only and owner-gated, and a strategy-session
decision, not a solver write. That is the single step between this diagnosis and the owner's
stored terms actually being whole.
