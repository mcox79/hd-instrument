---
problem: route_the_redundant_nltk_perceptron_tagger_through_the_fast_hdlab_tagger
status: SOLVED
bar: "PASS = the affect/valence path tags via the hdlab fast tagger + the shared cache, with BYTE-IDENTICAL affect output (feel-category + valence) on a held-out doc set and the NLTK tagger no longer called, with the measured read-time cut. A located NEGATIVE — the hdlab tagger cannot reproduce the NLTK tags the affect path relies on (a named tagset/behaviour difference) — is a FULL PASS."
result: "VALENCED affect output (feel-category + valence = HARM/HELP) BYTE-IDENTICAL under the fully-optimized readout: 0 valenced flips / 8947 _assign_affect calls across 40 held-out LitBank docs (the single HARM instance in the corpus preserved); witness 6/6. TWO independent optimizations, both byte-identical on the valenced output: (1) DROP THE REDUNDANT NLTK TAGGER — nltk tagger calls/read 195->12, affect nltk time 2.487s/10docs (~0.25-0.28s/read) removed; (2) SKIP THE DISCARDED VALENCE — _assign_affect never reads result['valence'] yet score_item runs valence_for_type (2 torch matmuls/event); skipping it removes 0.950s/8docs (~0.12s/read). Combined ~0.37s/read off the affect path; measured wall-clock read cut median 0.35s (11.5%, 10 docs, noisy at doc level). NAMED RESIDUAL (located-negative sub-finding, itself a full pass per the bar): the affect FIELD's None<->NA firing-provenance bit differs on 9.0% of events (raw UD UPOS) / 7.5% (reconciled) — hdlab UD-EWT and NLTK perceptron are different statistical models disagreeing on ~9% of governor/patient tags; INERT (no production consumer branches on None vs NA, enumerated repo-wide) and hdlab tags often MORE correct."
floor: "info-free shuffled-tag twin (real UD tag multiset, deranged onto tokens) diverges from the NLTK route on 228/784 affect calls (29%) vs the rerouted hdlab route's 85/784 (11%) — the affect output IS tag-sensitive, so hdlab's close agreement is non-vacuous (a random tagger loses 2.7x). Valenced-output floor = the NLTK incumbent itself: 0 tolerated valenced changes, hit exactly (0/8947)."
controls: "(1) info-free shuffled-tag twin LOSES (228 vs 85 divergences) — excludes 'any tagger reproduces it' (tag-insensitivity); (2) tokenizer control — NLTK tags on the READER's tokens vs NLTK's own re-tokenization diverge 3/8947 — excludes tokenization as the cause, isolates the tagger as the only changed variable; (3) valenced-flip counter over all 8947 calls incl. the 1 HARM — excludes a silent change to the situation-model-consumed signal; (4) reader self-test preserved (battered->HARM, saw->None) under the reroute — excludes breaking the one place HARM is exercised; (5) nltk.pos_tag/word_tokenize monkeypatched to raise, rerouted readout still completes — excludes a hidden residual NLTK call."
files_changed: "experiments/exp_affect_nltk_profile_v1.py, experiments/exp_affect_reroute_byteident_v1.py, experiments/exp_affect_reroute_speedup_v1.py, experiments/exp_affect_reroute_speedup_v2.py, experiments/exp_affect_optimized_full_v1.py, experiments/exp_arc_labeler_fastpath_v1.py, verification/test_affect_reroute_hdlab_tagger.py, verification/test_arc_labeler_fastpath.py, notes/problems/route_the_redundant_nltk_perceptron_tagger_through_the_fast_hdlab_tagger/SOLVED.md (NO hdlab/ writes — proposed diffs below, strategy lands per Q111)"
reverify: ".venv/Scripts/python.exe verification/test_affect_reroute_hdlab_tagger.py"
---

## INTEGRATED_BY_STRATEGY (2026-09-05) — EXCELLENT
Landed: `hdlab/situation_reader._assign_affect` reroutes through the shared `_load_frontend` UD-EWT tagger (one category system, no NLTK); `hdlab/context_grounded_valence.score_item` gains `need_valence` (default True = byte-identical) so the affect wire skips the discarded torch valence. Valenced output byte-identical (witness `test_affect_reroute_landing.py`: 0 flips / 1124, NLTK-free, skip-valence byte-identical); the pre-land witness `test_affect_reroute_hdlab_tagger.py` is 6/6 (its C4 is a stale NLTK-tokenizer control post-land). ~0.37s/read. Follow-on filed: the arc-labeler fast-path (`_FastLabelPlan`, built + witnessed, ready). §2b folded.

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

**Read-time cut — TRUE LANDED (shared `_cached_tag`), 10 docs, warm, 2 reps** (`exp_affect_reroute_speedup_v2.py`, which instruments every NLTK `PerceptronTagger.tag` call): NLTK tagger calls/read drop **195 → 12**; the affect tagger (`_tokenize_and_tag`) footprint of **2.487s / 10 docs (~0.25–0.28s/read, 1823 calls)** is eliminated. Wall-clock cut median 0.35s/read (11.5%, mean 0.33s) — but noisy at the doc level (−0.76s to +1.04s), so the **directly-measured NLTK time removed (~0.28s/read)** is the number to trust, not the jittery wall-clock. (v1's `exp_affect_reroute_speedup_v1.py` gave a per-read-cache lower bound of 0.40s; v2 supersedes it with the true shared-cache behaviour.)

**Second, independent optimization — SKIP THE DISCARDED VALENCE** (`exp_affect_optimized_full_v1.py`): `_assign_affect` returns `to_ternary(result["predicted_type"])` and **never reads `result["valence"]`**, yet `score_item` unconditionally runs `valence_for_type` (two torch theta matmuls per event). Stopping after `combine_biased_competition` is **valenced-byte-identical** (0 flips / 1821 calls) and removes **0.950s / 8 docs (1434 calls, ~0.12s/read)** of pure discarded torch work. Composed with the tagger reroute, the affect path sheds **~0.37s/read** and is left with only the governor perceptron + animacy lookup it actually needs.

**Witness — `verification/test_affect_reroute_hdlab_tagger.py`, 6/6 PASS:** C1 valenced byte-identity (0 flips), C2 self-test survives, C3 NLTK dropped (readout completes with `nltk.pos_tag`/`word_tokenize` disabled), C4 tokenizer inert (0/409), C5 info-free tag twin loses (hdlab 85 vs shuffled-tag twin 228 over 784 calls), C6 skip-valence valenced-byte-identical + lite path never calls `valence_for_type`.

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
   Give it a `need_valence=False` fast exit so the affect wire skips the discarded torch valuation:
   ```python
   def score_context_grounded_valence_pretagged(target_word, tokens, pos, *, seed=0,
                                                n_train_theta=FULL_N_TRAIN_THETA, need_valence=False):
       tw = target_word.lower()
       target_idx = next((i for i, t in enumerate(tokens) if t.lower() == tw), None)
       if target_idx is None:
           raise ValueError(f"target_word {target_word!r} not in tokens")
       r = score_item(list(tokens), list(pos), target_idx, target_word, seed=seed,
                      n_train_theta=n_train_theta, need_valence=need_valence)   # score_item skips valence_for_type when False
       return r
   ```
   (equivalently, add a `winner`-first early return inside `score_item` before `valence_for_type` when a `need_valence=False` flag is set — byte-identical, since `to_ternary(final_type)` never uses valence).
2. `hdlab/situation_reader.py` — make `_assign_affect` a reader method that tags via the shared cache and skips the discarded valence:
   ```python
   def _assign_affect(self, patient, toks):
       if patient in (None, "?"):
           return None
       pos = self._cached_tag(list(toks))     # hdlab UD UPOS via the shared per-read cache — no NLTK
       try:
           result = score_context_grounded_valence_pretagged(patient, list(toks), pos)  # need_valence=False
       except ValueError:
           return None
       return to_ternary(result["predicted_type"]) if result["stage"] == "event" else None
   ```
   and update the two call sites (1287, 1466) from `_assign_affect(patient, text)` to `self._assign_affect(patient, toks)` (`toks` is already in scope). `_assign_affect` is the ONLY production caller of `score_context_grounded_valence` (grep-verified), so this fully removes the NLTK perceptron tagger from the read path's affect portion. **Note:** `score_item`'s certified public signature stays unchanged (the `need_valence` flag defaults to today's behaviour — valence computed); only the affect wire opts out.

**Post-land re-verify:** `verification/test_affect_reroute_hdlab_tagger.py` (5/5) + the reader's own `_selftest_affect_wiring` (`hdlab/situation_reader.py:2252`; asserts battered→HARM, saw→None — both confirmed to hold under the reroute).

## KEY REALIZATIONS
- **Decompose the output, not the tags.** Byte-identity of *tags* is impossible between two different statistical taggers; byte-identity of the *affect output* is the real bar, and it splits into valenced content (byte-identical, load-bearing) vs an `NA<->None` provenance bit (divergent, inert). Measuring the split is what turned an apparent "can't reproduce" into a clean pass.
- **Enumerate the consumers before calling a difference a regression.** The 7.5–9% field divergence looked fatal until I grep-enumerated every `.affect` reader and found none branch on `None` vs `NA`.
- **The info-free twin proves the win is real.** A shuffled-tag route diverges 2.7× more — without it, "0 valenced flips" could have meant the wire is just tag-insensitive.
- **The convenient tool was the bug.** The whole problem existed because a second, off-the-shelf tagger was reachable; the brain-foundational "one category system" both removes the cost and *improves* correctness (contextual AUX, native PROPN).
- **Follow the value the caller actually reads.** Profiling the *affect wire* (not just the tagger) surfaced a second waste: `score_item` computes a torch valence the caller discards. Auditing "what does `_assign_affect` actually consume from the result?" (`stage` + `predicted_type`, never `valence`) turned one optimization into two — ~0.12s/read for free, byte-identical.

## ADDITIONAL INEFFICIENCIES ADDRESSED (owner asked "resolve those fully", 2026-09-05)

**(I) RESOLVED — the arc-labeler naive scoring loop (the single biggest read-time lever, ~10× larger than the affect tagger).** `hdlab/arc_labeler.py::ArcLabeler._predict_label` runs default-on via entity-states (`bind_entity_states`) and scores each arc by, for EVERY one of 36 labels, summing `w.get(f + "~" + lab)` over the arc's 25 features — **900 string-concat dict lookups per arc, ~75k `_score` calls/read**. The reader's POS tagger already replaced this exact pattern with a byte-identical `_FastEmissionPlan`; the labeler never got it. I built the analogous plan (precompute `feat → [(label_idx, weight)]` by splitting each key on the LAST `~`; accumulate present weights per-label lane in FEATURE order; argmax in LABEL order → identical float sums, identical tie-break). Measured (`exp_arc_labeler_fastpath_v1.py`, witness `verification/test_arc_labeler_fastpath.py` 3/3):
- **Byte-identical: 0 label mismatches / 5975 real arcs; `sm.entity_states` byte-identical on every doc.**
- **Micro-speedup 9.81×** (3.017s → 0.308s on the labeler scoring); **end-to-end read cut median 0.87s (13.9%), up to +2.10s** on a large doc.
- Info-free control: a weights-shuffled plan diverges (identity is non-vacuous).
- **Proposed hdlab diff:** add `_FastLabelPlan` to `hdlab/arc_labeler.py` and build it lazily in `label()` (mirroring `PosTagger._ensure_fast`), so inference uses the fast path and training stays on the reference. **This deserves its own filed problem** (a different organ from the NLTK reroute); mechanism + witness are ready for strategy to land.

**(II) NOT fully resolved — the `tag_punct` NLTK tagger is a scoped LOCATED NEGATIVE for a UPOS reroute.** `experiments/_temporal_ordering_multiframe.tag_punct` is the ONLY NLTK tagger left after the affect fix (~0.08s/read, 133 calls, NLTK calls/read 195→12 all from here). It cannot route through the hdlab UPOS tagger byte-identically because the entire temporal/timeline tense subsystem keys on **Penn Treebank fine tags — VBD (finite past) vs VBN (participle) + had/be lookback** — a distinction UD **UPOS structurally cannot represent** (both are `VERB`), and the substrate has **no Penn tagger asset** (every frontend asset is UPOS/UD). Two real resolution paths, each a separate problem: **(a)** build a substrate XPOS tagger from the UD-EWT XPOS column (present on disk: `data/corpora/ud_english_ewt/en_ewt-ud-train.conllu`) and route the whole tense subsystem through it (measure timeline-output preservation, exactly like the affect path — the tags won't be byte-identical to NLTK's Penn model); **(b)** the deeper fix — have the timeline register consume the reader's already-computed `EventRecord.tense` instead of re-extracting events from a second Penn tagger. Building/validating either is out of scope for "reroute the tagger" and I did not do it; I verified the XPOS corpus exists so path (a) is credible.

## ADJACENT COMPONENTS (seeds for the next problems)
1. **The arc PARSER (`hdlab/arc_parser.py`, ~2.7s/read) is already fast-pathed** (FeatCache + CRC integer feature IDs), so — correcting my earlier "parser+labeler" framing — the LABELER was the naive one, now resolved above; the parser is not low-hanging.
2. **The grounded-valence affect wire is near-dormant on real narrative** (1 valenced firing / 8947 events). It is tuned to the certified animacy-axis construction (direct-object patient + force-capable verb), rare in 19c literary prose. Worth evaluating whether the valence channel needs a broader, brain-faithful firing mechanism (OCC appraisal over the causation/goal registers — the explicit-vs-inferred split flagged in `affect_register.py`), or whether the affect_register emotion dimension already covers the load. Brain-fidelity + yield question.
3. **The affect governor is re-derived by `nearest_verb_idx` over a fresh tagging**, but the reader already knows the event's predicate index (`e.idx`). Feeding the event's own predicate as the governor would use the parse once (more brain-foundational) and could shrink the `NA<->None` divergence further. Adjacent optimization.

## AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md`, strategy folds in)
The affect/valence path (`context_grounded_valence` reached from `situation_reader._assign_affect`) ran a **second POS tagger** (NLTK averaged-perceptron) redundant with the reader's one hdlab UD front end — an un-brain-foundational two-category-system deviation, now measured and removable byte-identically on the valenced output. Also: the grounded-valence wire is **near-dormant on real narrative** (1 valenced firing / 8947 events) — a fidelity/coverage note for the affect dimension entry. Perf (byte-identical, not a fidelity change): the arc-labeler (`hdlab/arc_labeler.py`) still uses the naive per-label string-concat scoring the POS tagger already retired; a `_FastLabelPlan` gives 9.8× on the labeler / ~0.87s/read, entity-states byte-identical. And the timeline/temporal subsystem still depends on an NLTK **Penn** tagger (`tag_punct`) because no substrate XPOS asset exists — a named gap.

## What I did NOT establish
- Strict `EventRecord.affect` FIELD byte-identity (the `None/NA` bit differs 7.5–9%); I established valenced (feel-category + valence) byte-identity + inertness of the residual.
- A low-variance *wall-clock* speedup. The wall-clock read cut is noisy (10 docs, median 0.35s but −0.76s to +1.04s per doc). The robust, directly-measured claim is "the affect NLTK tagger's ~0.25–0.28s/read is removed (NLTK calls 195→12), plus ~0.12s/read of discarded torch valence."
- Whether a HARM/HELP-dense corpus could surface a valenced-sensitive case; only 1 HARM appeared in 40 docs and it did not flip, and the event-stage firing showed 0 valenced flips across all 8947 calls.

## What I would withdraw first if wrong
The **wall-clock "11.5% read-time cut"** — it is doc-noisy. I would fall back to the directly-instrumented NLTK time removed (2.487s / 10 docs, ~0.25–0.28s/read; calls 195→12) plus the measured discarded-valence 0.12s/read, which do not depend on wall-clock jitter. The byte-identity and NLTK-dropped results are robust (8947 calls, 6/6 witness) and would stand.

## TLDR (plain language)
The reader was accidentally running two different part-of-speech taggers — its own fast one everywhere, and a slower off-the-shelf one hidden in the emotion-scoring path, doing the same job on sentences already tagged. Switching the emotion path to the fast tagger (using tags already computed) gives the **same emotional read** — the actual "this character is harmed/helped" signal is identical on 40 books' worth of text (8,947 checks, zero changes). Pushing further, I found a second waste in the same path: it was running an expensive scoring step and then throwing the result away, so I skip it. Together these trim the emotion path from about nine-tenths of a second to under two-tenths, and drop the off-the-shelf tagger's calls from ~195 to ~12 per read. On roughly 8% of events a purely internal bookkeeping flag flips between "no emotion" and "neutral emotion"; those mean the same thing to everything downstream, and I confirmed nothing reads that flag. The fast tagger is also simply more accurate on names and helper verbs.

## QUESTIONS
None.

## NEXT STEPS (priority)
1. **Strategy lands the affect optimizations** (raw UD UPOS reroute + `need_valence=False`); witness `test_affect_reroute_hdlab_tagger.py` 6/6 + the reader self-test. ~0.37s/read off the affect path, byte-identical; NLTK calls/read 195→12.
2. **File + land the arc-labeler fast path** (Additional Inefficiency I) — the biggest lever here: **~0.87s/read median, byte-identical** (`test_arc_labeler_fastpath.py` 3/3, `_FastLabelPlan` diff ready). A separate organ from the NLTK reroute, so it wants its own problem entry, but the mechanism is proven and landing-ready.
3. **File the `tag_punct` / temporal-tense problem** (Additional Inefficiency II) — a substrate XPOS tagger (UD-EWT XPOS is on disk) to reach **zero** NLTK taggers in a read, or route the timeline through the reader's own `EventRecord.tense`. Located-negative today (UPOS can't carry VBD/VBN).
4. **Evaluate the grounded-valence wire's near-dormancy** (adjacent #2) — OCC-appraisal firing vs the affect_register dimension.
