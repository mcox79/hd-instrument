# CATALOG — live non-brain-foundational stand-ins in the GROUNDING-ACQUISITION subsystem

**Slug:** `audit_the_grounding_acquisition_subsystem_for_non_brain_faithful_stand_ins` · **solver session, 2026-09-09.**
**The SECOND live entry point** the reader-audit (`audit_the_live_substrate_for_non_brain_faithful_stand_ins_and_name_replacements`,
owner-DONE) explicitly excluded and handed off. This audit's denominator is that subsystem's own live import+call
closure — **NOT** `situation_reader.read()` (the reader-audit's denominator; the two pipelines are disjoint).

**Denominator (enumeration, not comment-grep).** Derived by a runtime **import trace + settrace call trace** over the
subsystem's live entry point `hdlab.substrate.Substrate.read()` (which builds a REAL `GapDetector`, calls
`process_sentence` on the bag-of-words default, runs a live `extract_definitions` side-channel, and consolidates)
**plus** a direct grounding-core run (`seed_known_words → process_sentence → checkpoint`, default flags).
`experiments/exp_audit_grounding_subsystem_v1.py` classifies every hdlab module in the closure:

| class | count | meaning |
|---|---|---|
| **LIVE-CALLED** | 16 | ≥1 function executes on the default live path |
| **LIVE-IMPORTED-INERT** | 23 | imported by a live entry but 0 functions execute on default (a parallel/inert organ) |
| **DORMANT-ISLANDED-ONLY** | 6 | reachable ONLY via an orchestrator the live `read()` never invokes |

**Positive control (the tracer fired):** it caught `reading_grounding_loop.process_sentence` on the live path
(`positive_control_tracer_fired=True`), and the twelve targeted probes reproduce every live/dormant claim below.
**Witness:** `verification/test_audit_grounding_subsystem.py` re-derives the classification + the landed numbers from disk.

**Legend.** BF = brain-foundational. PINNED = the brain's computation is fixed by evidence; OUR-INVENTION = a
placeholder we chose. Each entry carries the five fields **(a)** brain structure+computation, **(b)** why the code is
not it (file:line), **(c)** BF replacement, **(d)** blast + live-status with the consuming file:line, **(e)** fix class.

---

## TOP-K (ranked by blast × severity)

| # | stand-in | live? | blast | fix class |
|---|----------|-------|-------|-----------|
| **1** | **G1** bag-of-content-words CO-OCCURRENCE comparator (`canonicalize` + `context_vector` + `schema_consistency_split_half`) — the meaning read-out + grounding decision variable | **LIVE-CALLED** | **CRITICAL** — loses to word-counting on the loop's OWN metric (0.016–0.030 < 0.048–0.065); caps the quality of EVERY grounded concept | RE-ARCH (grounded/conceptual input + meaning objective) |
| **2** | **G2** the GROUNDED input channel is IMPORTED-BUT-INERT (`grounded_similarity` funcs=0); the BF conceptual/ATL channel is live only for explicit genus statements (`definitional_extraction`) | **LIVE-IMPORTED-INERT** / partial | **HIGH** — the one representation that carries grounded meaning is not fed to the comparator | LOCAL-FIX (wire the grounded/conceptual channel) + RE-ARCH (objective) |
| **3** | **C7** attractor-as-RANKER in the gap gate (`gap_detector.ca3_match_score` → `cleanup_family.iterative_attractor` settled argmax) | **LIVE-CALLED** (bounded) | **MEDIUM** — selects WHICH codebook row the honest CA1 margin is measured against; can drift to hubs | RE-ARCH (graded population read) — **filed pri-5** |
| **4** | **C8** `hd_fact_store` SOURCE-TRUST-only ingest vetting (no correctness/quality gate in the store) | **LIVE-CALLED** | **LOW/FLEET** — correctness/tautology is gated UPSTREAM at `_make_grounding_gate` (remediated) | LOCAL-FIX (mostly remediated) |
| — | **N1** dependency-STRUCTURED encoder (`StructuralEncoder` + `pos_tagger`/`arc_parser`/`arc_labeler`) | DORMANT | the "structure" input fix is an island **and** a landed CI-sep NEGATIVE | do-not-rebuild (fair-test caveat) |
| — | **N2** VWFA `form_identity_vector` form-code | DORMANT (recognition-only) | form invariance cannot buy meaning (landed null) | correct-as-is |
| — | **N3** `three_tier_loop` / `gap_driven_reader` / `gather_reason` / `kg_traversal` / `prelim_tier` / `script_grain_acquisition_loop` | DORMANT-ISLANDED | the orchestrators + their unique organs are NOT on the live read path — do NOT rank as live defects | adjacent-fidelity seeds |

Entries **N1–N3** are located negatives / corrections (flagged, then shown dormant or refuted on deeper reading —
the bar credits these when the deeper reading is shown). **G1–C8** are the four LIVE stand-ins.

---

## G1 — the bag-of-content-words CO-OCCURRENCE comparator — the #1 blast (localized separately)
**(a) Brain structure+computation.** PINNED: word-meaning is grown in the **anterior-temporal semantic hub**, an amodal
convergence zone that integrates **sensorimotor spokes** + **verbal/definitional experience** into a GROUNDED,
distinctive-feature representation (hub-and-spoke: Lambon Ralph, Jefferies, Patterson & Rogers 2017; Rogers & McClelland
2004; Binder & Desai 2011). Distributional statistics DO shape it (Firth 1957) — but over grounded, structured concepts,
not over raw word-token co-occurrence.
**(b) Why the code is not it (file:line).** The live grounding decision variable is a cosine over a **bag of nearby
content-word codes**, at three coupled sites, all on the default path:
- `reading_grounding_loop.canonicalize` (`:872–911`): `new_bundle = np.sign(new_raw_sum)` then argmax cosine over anchor
  bundles — the nearest-anchor SENSE assignment. It is the decision for BOTH banking and meaning (`_make_grounding_gate:1469`;
  `checkpoint:1732`).
- `grounding_acquisition_loop.context_vector` (`:117`) / `reading_grounding_loop.context_vector_masked` (`:239`): the
  encoder is a sum of `symbol_vector`s = **sha256-seeded random bipolar draws** (`:297–310`) — ungrounded word identities,
  superposed into d=256. The one-variable `_encode` is the bag by default (`process_sentence:1345–1350`, `encoder=None`).
- `grounding_acquisition_loop.schema_consistency_split_half` (`:414–462`): the coherence gate is a cosine of two halves'
  summed context bags. Co-occurrence, again.
This is the classic distributional CONVENIENCE (a bag of co-occurring tokens), not the hub's grounded+structured code.
Measured character: the read-out hand-scored **3 MEANINGFUL / 19 RELATED / 78 NOISE** (`data/exp_grounding_quality_readout_v1/_joined_verdicts.json`).
**(c) BF replacement.** A GROUNDED/CONCEPTUAL input channel + a MEANING objective — the ATL conceptual channel
(`hdlab.grounded_similarity` spoke; the `definitional_extraction` WordNet-gloss distinctive-feature representation,
`exp_conceptual_meaning_channel_v1`), which separates grounded meaning where co-occurrence cannot. **This is the #1 item;
its full-stack-upstream localization is `experiments/exp_ground_readout_localization_v1.py` and `SOLVED.md`.**
**(d) Blast / live.** LIVE-CALLED (`canonicalize_live`/`context_vector_live`/`schema_consistency_split_half_live` all True
in the trace). On the loop's OWN metric it LOSES to word-counting: landed `SUBSTRATE 0.0159/0.0302/0.0272 < TOP_COOCCURRENT
0.0476/0.0653/0.0590` (`data/exp_meaning_readout_own_metric_v1/metrics.json`, verdict
`READOUT_TIES_OR_LOSES_COUNTING_ON_OWN_METRIC`, disk-verified). Blast = the quality of every grounded concept the whole
subsystem produces — the entire learn-by-reading output.
**(e) RE-ARCHITECTURE.** Not a better cosine: two prior drills refuted better inputs over the same bag (STRUCTURE hurts;
GROUNDING ties — see N1 and the localization). The fix couples a grounded input channel with a meaning objective.

## G2 — the GROUNDED meaning channel is imported but INERT; the BF conceptual channel is coverage-bound
**(a) Brain structure+computation.** PINNED (same hub-and-spoke as G1): the comparator's INPUT should be the grounded
representation the ATL supplies (sensorimotor spoke + verbal/definitional spoke), not a co-occurrence bag.
**(b) Why the code is not it (file:line).** `hdlab.grounded_similarity` — the grounded sensorimotor-spoke channel — is
in the live import closure but **executes ZERO functions** on the default path (trace class `LIVE-IMPORTED-INERT`,
funcs=0). The conceptual/definitional channel IS partially live — `substrate.py:718–719/744–745` passes `definition_map`
into `checkpoint`, and `_make_definitional_gate` (`reading_grounding_loop.py:1640–1649`) banks the definition phrase
BYPASSING the bag cosine — but ONLY when the extractor found an explicit genus statement (`definition_map.get(lemma)`),
i.e. a small subset; the general case (a new word learned from ordinary context) still rides the G1 bag. Runtime
evidence the definitional gate fires: 212/402 provenance rows carry `meaning_source=DEFINITIONAL_EXTRACTION`
(`reading_grounding_loop.py:1602–1605`).
**(c) BF replacement.** Wire `grounded_similarity` (and/or the conceptual distinctive-feature vector) as the comparator's
input for words WITHOUT an on-page definition, so the grounded channel is fed to `canonicalize`/`schema` rather than
imported and discarded. (The channel that separates grounded meaning: conceptual SimLex ρ 0.521 vs 0.29 grounded-as-wired
vs 0.37 GloVe, `exp_conceptual_meaning_channel_v1` — disk-verified.)
**(d) Blast / live.** `grounded_similarity` LIVE-IMPORTED-INERT (funcs=0, trace). Definitional channel LIVE but
coverage-bound (genus-only). Blast = HIGH: the one grounded input the comparator needs is present in the process and not
consumed by the decision — the reader-audit's C5/C6 "computed-and-discarded" shape, here applied to the INPUT.
**(e) LOCAL-FIX (wire the channel) + RE-ARCH (objective).** Wiring is mechanical; but per the localization, wiring alone
is insufficient without also changing the co-occurrence-shaped objective (see SOLVED.md).

## C7 — attractor-as-RANKER in the gap gate — LIVE but BOUNDED (refines the reader-audit's flag)
**(a) Brain structure+computation.** PINNED: attractor dynamics are for pattern-completion / RECOGNITION (Hopfield 1982;
Marr 1971; Treves & Rolls CA3), not for producing a graded similarity RANKING; a familiarity margin wants a graded
population read (CA1 match/mismatch).
**(b) Why the code is not it (file:line).** `gap_detector.ca3_match_score` (`:111–118`) calls
`cleanup_family.iterative_attractor` and takes `idx = diag["final_argmax_idx"]` — and that argmax is read off the
**SETTLED** state after softmax-attractor iterations (`iterative_attractor.py:125–126`: `final_scores = state @ cb.T`),
NOT the raw query. So the attractor IS the live ranker that selects which codebook row is the match; the softmax basin can
drift to high-degree hubs.
**(c) BF replacement.** A graded population read for the row-selection; reserve the attractor for the recognition/recall
step. (Filed as **pri-5** `replace_the_attractor_as_ranker_with_a_graded_population_read_in_the_grounding_loop`.)
**(d) Blast / live.** LIVE-CALLED (`gap_detector_ca3_match_live` + `iterative_attractor_live` both True) via
`is_gap` (`reading_grounding_loop.py:1302`) → `familiarity` (`gap_detector.py:171`). **BOUNDED, and this is the
disk-verified refinement:** the gap DECISION variable is `is_gap = margin < floor` where `margin` is the **RAW CA1
pre-settle cosine** to the attractor-picked row (`gap_detector.py:114–117`), which is an HONEST comparator. So the harm is
confined to row-SELECTION drift (the attractor may point the honest margin at a hub instead of the true nearest neighbour),
not to a settled-activation-as-confidence readout. Blast = novelty/gap decisions in the grounding loop, MEDIUM.
**(e) RE-ARCHITECTURE** (swap the ranker; keep the attractor for recognition). Do not duplicate — pri-5 owns it.

## C8 — `hd_fact_store` SOURCE-TRUST-only vetting — LIVE, correctness gated UPSTREAM (mostly remediated)
**(a) Brain structure+computation.** PINNED: semantic memory admits VETTED propositions (a consolidation/quality gate;
CLS, McClelland-McNaughton-O'Reilly 1995), not tautologies/junk.
**(b) Why the code is not it (file:line).** `hd_fact_store.store` (`:323`) vets by SOURCE-TRUST only, NOT correctness —
its own docstring says so (`:28–32`: "INGEST-VET is SOURCE-TRUST vetting, NOT correctness vetting"). The 66%-junk the
reader-audit flagged was what got PROMOTED, not what the store itself refuses.
**(c) BF replacement.** A correctness/quality gate at admission — which now EXISTS upstream: `_make_grounding_gate`
refuses self-tautologies (`REFUSAL_TAUTOLOGY`, `reading_grounding_loop.py:1471–1477`) and closed-class before a fact is
promoted; the problem `the_knowledge_store_has_no_correctness_or_consistency_cleanup` is INTEGRATED.
**(d) Blast / live.** LIVE-CALLED (`hd_fact_store_live=True`). But the tautology/quality gate is remediated at the
grounding gate (default `refuse_non_groundings=True`, `checkpoint:1674`), so the residual is LOW/FLEET — the store admits
by trust, correctness is enforced before it. Re-verified: the live path refuses tautologies (the grounding gate returns
False on `canon_obj == lemma`).
**(e) LOCAL-FIX** (largely done; residual is store-side quality telemetry, not a live decision defect).

---

## LOCATED NEGATIVES / CORRECTIONS

### N1 — the dependency-STRUCTURED encoder is DORMANT and a landed NEGATIVE (do not rebuild)
`StructuralEncoder` (`reading_grounding_loop.py:378–513`) + `structural_vector_masked` (`:516–520`) bind dependency-role
codes instead of a flat bag — the obvious "add structure" fix. Trace: **DORMANT** (`structural_encoder_dormant=True`;
`parser_assets_dormant=True` — `pos_tagger`/`arc_parser`/`arc_labeler` never execute). And it is a **CI-separated landed
NEGATIVE**: on the live read-out it scores hit@1 0.03675 vs the bag 0.0480, `STRUCTURE_HURTS` −0.0113 CI[−0.0195,−0.0030]
(`data/exp_structured_code_vs_flat_bag_c3_v1/metrics.json`), and a blind hand-score of the grounding loop was worse
(RELATED 3/50 vs 12/50, Fisher p=0.0113, `data/exp_structured_comparator_v1/`). Root cause named on disk: feature
starvation (~2.8 features/encoding vs ~11 for the bag) + an OOD parser. **Located negative:** re-proposing the on-disk
structured encoder re-derives this loss; the only unclosed door is a *non-starved, in-domain* structured encoder (a
fair-test escape hatch, not this one).

### N2 — the VWFA form-code is DORMANT and correctly recognition-only (a checked watch condition)
`form_identity_vector` (`reading_grounding_loop.py:317–359`) is a case/inflection-invariant word-FORM code. Trace:
DORMANT in the meaning path (`vwfa_form_code_dormant=True`). Its own docstring records the watch condition FIRED —
form invariance inside the meaning bag reads ρ +0.0573 INSIDE its null p95 0.0716, and the PERFECT version
(lemmatisation) is also a null (`notes/FORM_INVARIANCE_CANNOT_BUY_MEANING…_2026-08-22.md`). Legitimate consumers are
recognition/index sites only. **Located negative:** correctly kept out of the meaning path; not a live defect.

### N3 — the four orchestrators + their unique organs are DORMANT-ISLANDED (do not rank as live defects)
`three_tier_loop`, `gap_driven_reader`, `gather_reason`, `kg_traversal`, `prelim_tier`, `script_grain_acquisition_loop`
are all **DORMANT-ISLANDED-ONLY** in the trace (funcs=0): the live `Substrate.read()` never invokes them; they are
reachable only via their own harnesses. The reader-audit correctly warned "LIVE has three failure modes"; these are the
third (built, not on the live path). **Adjacent-fidelity note (follow-on seeds, not live defects):** `three_tier_loop`
(HARD_PASS concept-coherence in its own harness) is the multi-source three-tier design; `gather_reason` uses the same
`cleanup_family` attractor as C7 (would inherit the C7 fix); `prelim_tier` is the independence-weighted confirmation
tier. If any is wired live later, re-audit it then.

---

## ADMISSIBLE — checked and deliberately NOT flagged (the do-not-over-fire discipline)
Every LIVE-CALLED organ below was scanned for stand-in signatures (fitted-at-inference weights, surface-only decisions,
hand-lexicon-as-decision, external tool at inference) and cleared:
- **`information_foraging`** (LIVE, 27 funcs): optimal-foraging / Marginal Value Theorem patch-leaving (Charnov 1976;
  ACC foraging value) — a PINNED computation, softmax-stochastic with an argmax control. Not a fitted stand-in.
- **`hippocampal_encoder`** (LIVE, 10 funcs): CA3 auto-associator `sign(W @ cue)` one-step completion — the CORRECT use
  of an attractor (recognition/recall, Marr/Treves-Rolls), not a ranker. Admissible.
- **`event_bundle`** / **`role_slot_summarizer`** (LIVE): the owner-locked FHRR bind/bundle/cleanup-argmax algebra
  (UNPINNED-OK per the reader-audit); the attractor argmax here is RECALL (unbind a slot), the correct use.
- **`definitional_extraction`** (LIVE, 7 funcs): the ATL verbal/definitional spoke — `nltk.corpus.wordnet` LOOKUP
  (admissible static FOUNDATION supply, exactly as the reader-audit cleared the FrameNet/WordNet/VerbNet lookups) + the
  owned in-substrate `pos_tagger` perceptron. Not an external tool DOING inference; a knowledge lookup.
- **`corpus_registry`** (LIVE, 23 funcs): corpus file handles (data supply). **`closed_class_lexicon`** (function-word
  supply). **`thematic_role_labeler.lemma_word`** (glass-box suffix→lemma normalizer). **`self_improving_loop.decide_keep_or_revert`**
  (a threshold vote, not a learned gate). All admissible supply / deterministic rules.

## COMPLETENESS — the LIVE-IMPORTED-INERT set (23), scanned
The 23 imported-but-inert modules (`animacy_lexicon`, `atoms`, `binding`, `bundling`, `consequence_learning_loop`,
`coreference_resolver`, `frame_induction`, `goal_typing`, `grounded_similarity`, `learner`(+core+registry),
`lexical_similarity`, `memory`, `modulators`, `semantic`, `situation_model_accumulate`, `snapshots`, `state_of_mind`,
`tracing`, `verb_lexical_similarity`, `working_memory`, `ablation`) were checked: none executes a decision on the default
path. The load-bearing one is **`grounded_similarity`** (catalogued as G2 — the grounded input channel imported and not
consumed). The rest are re-export / infra / off-default-feature imports (not decision-standing). So the four LIVE stand-ins
(G1, G2, C7, C8) + three corrections (N1–N3) are the full set on the grounding-acquisition live path.

## POSITIVE CONTROL
The enumeration recovers the two items the reader-audit named for this subsystem (C7 `cleanup_family`/`iterative_attractor`,
C8 `hd_fact_store`) — both confirmed LIVE-CALLED here — and it ADDS the higher-blast G1 (bag comparator) and G2 (inert
grounded channel) the reader-scoped audit could not see. The tracer's positive control fired (`process_sentence` caught on
the live path). No named item silently dropped.
