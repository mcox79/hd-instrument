---
problem: route_the_redundant_nltk_perceptron_tagger_through_the_fast_hdlab_tagger
status: SOLVED
bar: "PASS = the affect/valence path tags via the hdlab fast tagger + the shared cache, with BYTE-IDENTICAL affect output (feel-category + valence) on a held-out doc set and the NLTK tagger no longer called, with the measured read-time cut. A located NEGATIVE — the hdlab tagger cannot reproduce the NLTK tags the affect path relies on (a named tagset/behaviour difference) — is a FULL PASS."
result: "VALENCED affect output (feel-category + valence = HARM/HELP) BYTE-IDENTICAL under the hdlab reroute: 0 valenced flips / 8947 _assign_affect calls across 40 held-out LitBank docs (the single HARM instance in the corpus preserved); NLTK perceptron tagger + tokenizer no longer called during a read; median read-time cut 0.40s/read (18.9%, mean 0.45s, 6 docs, warm) — a LOWER BOUND since the landed wire shares the reader's already-warm _cached_tag. NAMED RESIDUAL (the located-negative sub-finding, itself a full pass per the bar): the affect FIELD's None<->NA firing-provenance bit differs on 9.0% of events (raw UD UPOS) / 7.5% (reconciled) because the hdlab UD-EWT tagger and NLTK's perceptron are different statistical models disagreeing on ~9% of governor/patient tags — INERT (no production consumer branches on None vs NA, enumerated repo-wide) and the hdlab tags are often MORE correct."
floor: "info-free shuffled-tag twin (real UD tag multiset, deranged onto tokens) diverges from the NLTK route on 228/784 affect calls (29%) vs the rerouted hdlab route's 85/784 (11%) — the affect output IS tag-sensitive, so hdlab's close agreement is non-vacuous (a random tagger loses 2.7x). Valenced-output floor = the NLTK incumbent itself: 0 tolerated valenced changes, hit exactly (0/8947)."
controls: "(1) info-free shuffled-tag twin LOSES (228 vs 85 divergences) — excludes 'any tagger reproduces it' (tag-insensitivity); (2) tokenizer control — NLTK tags on the READER's tokens vs NLTK's own re-tokenization diverge 3/8947 — excludes tokenization as the cause, isolates the tagger as the only changed variable; (3) valenced-flip counter over all 8947 calls incl. the 1 HARM — excludes a silent change to the situation-model-consumed signal; (4) reader self-test preserved (battered->HARM, saw->None) under the reroute — excludes breaking the one place HARM is exercised; (5) nltk.pos_tag/word_tokenize monkeypatched to raise, rerouted readout still completes — excludes a hidden residual NLTK call."
files_changed: "experiments/exp_affect_nltk_profile_v1.py, experiments/exp_affect_reroute_byteident_v1.py, experiments/exp_affect_reroute_speedup_v1.py, verification/test_affect_reroute_hdlab_tagger.py, notes/problems/route_the_redundant_nltk_perceptron_tagger_through_the_fast_hdlab_tagger/SOLVED.md (NO hdlab/ writes — proposed diff below, strategy lands per Q111)"
reverify: ".venv/Scripts/python.exe verification/test_affect_reroute_hdlab_tagger.py"
---

# Route the redundant NLTK perceptron tagger through the fast hdlab tagger — SOLVED

## What the disk says (it outranks the brief on two points)

**The single production NLTK perceptron-tagger call in the affect path is `hdlab/context_grounded_valence.py:325` `nltk.pos_tag(tokens, tagset="universal")`, inside `_tokenize_and_tag`, reached from `hdlab/situation_reader.py::_assign_affect` (lines 1287 + 1466) via `score_context_grounded_valence`.** Every other `nltk` reference in the affect files is `from nltk.corpus import wordnet` (a static lexical asset, not the tagger). Confirmed first-hand by grep + a warm-read `cProfile`.

Two brief statements the disk corrects (I say so per the protocol):
1. **The brief attributes the cost to `track_affect` (+0.807s).** On disk, `_assign_affect` (the NLTK caller) is in `_read_events`/`_read_events_wired` and is **NOT gated by `track_affect`** — it runs on every read regardless. The separate `track_affect`-gated dimension (`_read_affect`, the affect_register) already uses the shared `_cached_tag` (no NLTK). So the redundant tagger is the grounded-valence wire, always paid, not the emotion dimension.
2. **The brief frames the target as byte-identical tags.** The two taggers are different statistical models; the tags are *not* reproducible token-for-token. The right target — and the one that matters — is byte-identical **affect output**, which decomposes cleanly (below).

Warm-read profile (`105_persuasion`, 190 events): `_assign_affect` = **0.911s**, of which `_tokenize_and_tag` (NLTK) = **0.656s** (`nltk.pos_tag` 0.580s + `word_tokenize` 0.061s); the kept scorer `score_item` = 0.248s. The same sentences were **already tagged** by the events/roles path via `_cached_tag`, so rerouting turns those 164 NLTK calls into cache hits.

## The mechanism, brain-foundationally

**One lexical-category system, not two — PINNED.** The brain has a single category inference; the reader's `hdlab/pos_tagger.py` (UD-EWT structured perceptron, the front end for events/roles/entity-states/causal) *is* that system. The NLTK averaged-perceptron tagger buried in the affect path is a **second, off-the-shelf** category system — precisely the "reach for the convenient tool" pattern this project is built to avoid. The affect field on an event was being computed from a *different* POS analysis than the event's own agent/patient/predicate. The fix removes that inconsistency; the tagger model is unchanged (PINNED), only the routing is OUR-INVENTION.

The affect output depends on `pos` through exactly three narrow tests — `nearest_verb_idx` (`== "VERB"`), `adjmod_idx` (`== "ADJ"` / `!= "DET"`), and the patient's own tag gating the animacy lookup path (`PRON`/`PROPN`/`NOUN`). The hdlab UD tagger produces those distinctions **natively and more faithfully** than the NLTK route: it tags copulas/auxiliaries `AUX` *contextually* ("had a book"→VERB possession vs "have eaten"→AUX), where the NLTK route hard-codes every `be/have/do`→AUX; and it emits `PROPN` natively, where the NLTK universal tagset has no PROPN and sends proper-noun patients to `NOUN` (misrouting animacy).

## What I measured

**Byte-identity — 40 held-out LitBank docs, 8947 `_assign_affect` calls** (`exp_affect_reroute_byteident_v1.py`):

| comparison | divergence | reading |
|---|---|---|
| **VALENCED affect (HARM/HELP)** | **0 / 8947** | the situation-model-consumed signal is byte-identical (raw AND reconciled); the sole HARM in the corpus preserved |
| tokenizer (reader tokens vs `nltk.word_tokenize`) | 3 / 8947 | tokenization is inert — switching to the reader's own tokens is safe |
| affect FIELD, raw UD UPOS | 801 / 8947 (9.0%) | all `NA<->None`; genuine tagger disagreement on the firing-provenance bit |
| affect FIELD, reconciled (AUX-split + PROPN→NOUN) | 669 / 8947 (7.5%) | closer to legacy but less correct (see recommendation) |

Affect distribution of the NLTK output over 40 docs: `{None: 6346, NA: 2600, HARM: 1, HELP: 0}`. **The grounded-valence affect wire is near-dormant on real narrative** — it fires a *valenced* value once in 8947 events (0.01%); otherwise it abstains (None) or returns neutral (NA). `None` and `NA` are affect-equivalent (both = "no HARM/HELP signal"), and **no production code branches on the distinction** — I enumerated every `.affect` consumer repo-wide: only the reader's own self-test (constructs its sentence; HARM preserved) and one profiling tuple. So the 7.5–9% field divergence is behaviorally inert.

**Read-time cut — 6 docs, warm, 3 reps** (`exp_affect_reroute_speedup_v1.py`): **median 0.40s/read (18.9%), mean 0.45s**, range −0.05s to +0.93s. This is a **lower bound**: the A/B route uses its own per-read tag cache, whereas the landed wire shares `self._cached_tag`, which the events/roles path has already populated for every sentence → pure cache hits.

**Witness — `verification/test_affect_reroute_hdlab_tagger.py`, 5/5 PASS:** C1 valenced byte-identity (0 flips), C2 self-test survives, C3 NLTK dropped (readout completes with `nltk.pos_tag`/`word_tokenize` disabled), C4 tokenizer inert (0/409), C5 info-free tag twin loses (hdlab 85 vs shuffled-tag twin 228 divergences over 784 calls).

## Verdict

The bar's own wording — "byte-identical affect output (**feel-category + valence**)" — is **met**: the feel-category and valence (HARM/HELP) are byte-identical (0/8947), the NLTK tagger is dropped, and the read-time cut is real. `NA` and `None` carry *no* feel-category and *no* valence, so their boundary is not part of "feel-category + valence" — but I foreground it as a **named located-negative sub-finding** (which the brief says is itself a full pass): the hdlab UD-EWT and NLTK perceptron taggers are different statistical models that disagree on ~9% of affect-relevant governor/patient tags, flipping the inert `NA<->None` provenance bit. Strict `EventRecord.affect` FIELD byte-identity is therefore **not** achievable without keeping NLTK — and should not be, because the hdlab tags are the substrate's one consistent, and often more correct, category system.

## PROPOSED hdlab CHANGE (strategy lands, Q111; I did not touch `hdlab/`)

**Recommend RAW UD UPOS** (no reconcile): one category system consistent with every other organ; native contextual AUX; native PROPN → *correct* proper-noun animacy. Reconciling PROPN→NOUN would reintroduce a two-tagset inconsistency and degrade animacy; its only merit is 1.5pp-closer-to-legacy on an inert bit.

1. `hdlab/context_grounded_valence.py` — add a pre-tagged entrypoint (skips `_tokenize_and_tag`, i.e. NLTK):
   ```python
   def score_context_grounded_valence_pretagged(target_word, tokens, pos, *, seed=0, n_train_theta=FULL_N_TRAIN_THETA):
       tw = target_word.lower()
       target_idx = next((i for i, t in enumerate(tokens) if t.lower() == tw), None)
       if target_idx is None:
           raise ValueError(f"target_word {target_word!r} not in tokens")
       return score_item(list(tokens), list(pos), target_idx, target_word, seed=seed, n_train_theta=n_train_theta)
   ```
   Keep `_tokenize_and_tag` / `score_context_grounded_valence` (the NLTK convenience entrypoint) for standalone use — the reader no longer calls them, so no NLTK during a read.
2. `hdlab/situation_reader.py` — make `_assign_affect` a reader method that tags via the shared cache:
   ```python
   def _assign_affect(self, patient, toks):
       if patient in (None, "?"):
           return None
       pos = self._cached_tag(list(toks))     # hdlab UD UPOS via the shared per-read cache — no NLTK
       try:
           result = score_context_grounded_valence_pretagged(patient, list(toks), pos)
       except ValueError:
           return None
       return to_ternary(result["predicted_type"]) if result["stage"] == "event" else None
   ```
   and update the two call sites (1287, 1466) from `_assign_affect(patient, text)` to `self._assign_affect(patient, toks)` (`toks` is already in scope). `_assign_affect` is the ONLY production caller of `score_context_grounded_valence` (grep-verified), so this fully removes the NLTK perceptron tagger from the read path's affect portion.

**Post-land re-verify:** `verification/test_affect_reroute_hdlab_tagger.py` (5/5) + the reader's own `_selftest_affect_wiring` (`hdlab/situation_reader.py:2252`; asserts battered→HARM, saw→None — both confirmed to hold under the reroute).

## KEY REALIZATIONS
- **Decompose the output, not the tags.** Byte-identity of *tags* is impossible between two different statistical taggers; byte-identity of the *affect output* is the real bar, and it splits into valenced content (byte-identical, load-bearing) vs an `NA<->None` provenance bit (divergent, inert). Measuring the split is what turned an apparent "can't reproduce" into a clean pass.
- **Enumerate the consumers before calling a difference a regression.** The 7.5–9% field divergence looked fatal until I grep-enumerated every `.affect` reader and found none branch on `None` vs `NA`.
- **The info-free twin proves the win is real.** A shuffled-tag route diverges 2.7× more — without it, "0 valenced flips" could have meant the wire is just tag-insensitive.
- **The convenient tool was the bug.** The whole problem existed because a second, off-the-shelf tagger was reachable; the brain-foundational "one category system" both removes the cost and *improves* correctness (contextual AUX, native PROPN).

## ADJACENT COMPONENTS (seeds for the next problems)
1. **A SECOND redundant NLTK perceptron tagger: `experiments/_temporal_ordering_multiframe.tag_punct`** (reached from the temporal-ordering path; 27 calls/read on `105_persuasion`, ~0.19s). Same class of fix, but it uses the **Penn Treebank** tagset (not universal), so the reconcile is harder — a distinct follow-on. Brain-fidelity: OUR-INVENTION placeholder (an off-the-shelf tagger); should route through the same one category system.
2. **The grounded-valence affect wire is near-dormant on real narrative** (1 valenced firing / 8947 events). It is tuned to the certified animacy-axis construction (direct-object patient + force-capable verb), rare in 19c literary prose. Worth evaluating whether the valence channel needs a broader, brain-faithful firing mechanism (OCC appraisal over the causation/goal registers — the explicit-vs-inferred split flagged in `affect_register.py`), or whether the affect_register emotion dimension already covers the load. Brain-fidelity + yield question.
3. **The affect governor is re-derived by `nearest_verb_idx` over a fresh tagging**, but the reader already knows the event's predicate index (`e.idx`). Feeding the event's own predicate as the governor would use the parse once (more brain-foundational) and could shrink the `NA<->None` divergence further. Adjacent optimization.

## AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md`, strategy folds in)
The affect/valence path (`context_grounded_valence` reached from `situation_reader._assign_affect`) ran a **second POS tagger** (NLTK averaged-perceptron) redundant with the reader's one hdlab UD front end — an un-brain-foundational two-category-system deviation, now measured and removable byte-identically on the valenced output. Also: the grounded-valence wire is **near-dormant on real narrative** (1 valenced firing / 8947 events) — a fidelity/coverage note for the affect dimension entry.

## What I did NOT establish
- Strict `EventRecord.affect` FIELD byte-identity (the `None/NA` bit differs 7.5–9%); I established valenced (feel-category + valence) byte-identity + inertness of the residual.
- The speedup beyond 6 docs (median 0.40s; per-doc variance is high — one doc read −1.7%, timing noise). The robust claim is "the NLTK tagger's ~0.4–0.9s/read affect cost is removed."
- Whether a HARM/HELP-dense corpus could surface a valenced-sensitive case; only 1 HARM appeared in 40 docs and it did not flip, and the event-stage firing showed 0 valenced flips across all 8947 calls.

## What I would withdraw first if wrong
The **"18.9% read-time cut"** headline number — timing is noisy at 2–3s/read. I would fall back to the profile-measured `_tokenize_and_tag` = 0.656s (of a 0.911s `_assign_affect`) on `105_persuasion` and re-run the A/B on more docs. The byte-identity and NLTK-dropped results are robust (8947 calls, 5/5 witness) and would stand.

## TLDR (plain language)
The reader was accidentally running two different part-of-speech taggers — its own fast one everywhere, and a slower off-the-shelf one hidden in the emotion-scoring path, doing the same job on sentences already tagged. Switching the emotion path to the fast tagger (using tags already computed) gives the **same emotional read** — the actual "this character is harmed/helped" signal is identical on 40 books' worth of text (8,947 checks, zero changes) — while cutting about a fifth off each read. On roughly 8% of events a purely internal bookkeeping flag flips between "no emotion" and "neutral emotion"; those mean the same thing to everything downstream, and I confirmed nothing reads that flag. The fast tagger is also simply more accurate on names and helper verbs.

## QUESTIONS
None.

## NEXT STEPS (priority)
1. **Strategy lands the reroute** (the diff above; raw UD UPOS) and runs the witness + the reader self-test. The +0.4s/read cut is free and byte-identical on the meaningful output.
2. **File the temporal-path twin** (`tag_punct`, adjacent #1) — a second redundant NLTK perceptron tagger, same fix modulo the Penn→UD tagset reconcile.
3. **Evaluate the grounded-valence wire's near-dormancy** (adjacent #2) — decide whether the valence channel needs a broader OCC-appraisal firing mechanism or whether the affect_register dimension already carries the emotion load.
