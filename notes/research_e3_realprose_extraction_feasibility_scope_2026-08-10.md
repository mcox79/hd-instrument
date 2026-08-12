# Research: E3 Scoping -- The Binding-Constraint Attack (Real-Prose Extraction Feasibility) (2026-08-10)

Filed by: research (Sonnet, foreground, no nested sub-agents). Dispatched to scope the highest-value
question in the program: the barrier map (`notes/research_comprehension_barrier_map_brain_foundational_
2026-08-10.md`) named the binding constraint as the prose -> structured-situation-model READ (B5
event/outcome-span extraction feeding B1 grounding), and asked for E3's precise scope + first cheap
can-fail gate. This is a feasibility/scoping drill, not a build: no production files were edited; the
only new artifact is this note plus two throwaway trace scripts in the session scratchpad (not committed).

KB-CHECK DONE FIRST (mandatory dedup): `substrate_query.sh` on the exact prompt (top hits were the
situation-model STRUCTURE/FUNCTION lit notes and the goal/outcome dimension prereg -- confirmed this is
new ground, not a rediscovery); then read the barrier map end-to-end (the authoritative frame for this
drill) plus, on disk, the four organs the map names as the encode-path core: `hdlab/situation_model_
accumulate.py`, `hdlab/event_bundle.py`, `hdlab/situation_focus.py`, `hdlab/outcome_event_extraction.py`,
`hdlab/situation_reader.py`, `hdlab/mcscript_extraction.py`, and the Stage-2A loop cell
(`experiments/exp_focus_pullin_causal_stage2a_multihop_loop_v1.py`) that is the loop's actual consumer.
Then traced the owned encode path LIVE against the real MCScript2.0 dev set on disk
(`data/corpora/mcscript2/extracted/dev-data.xml`, 355 real crowd-sourced narratives) -- this is the
load-bearing empirical part of the drill (Section 3), not a synthetic illustration.

---

## HEADLINE

**The binding constraint decomposes into THREE independently-broken, independently-fixable sub-breaks
when actually traced on real prose -- not one diffuse "extraction is hard" problem.** (1) A genuine
STRUCTURAL gap: the ONE organ that produces the loop's actual target shape (`situation_reader.py`) has
never been run on raw prose at all -- it hard-requires LitBank CoNLL gold (pre-tokenized, pre-annotated
coref spans), so its B4/B6 machinery is currently unreachable from any real un-annotated corpus,
including MCScript2.0. (2) A measured, narrow, cheap-to-fix COVERAGE gap in B5's event segmenter: on a
60-instance / 545-sentence live scan of real MCScript2.0 dev text, the per-clause event extractor
(`experiments/_temporal_ordering.extract_events`, the organ `situation_reader.py` depends on) returns
**zero events on 67.0% (61/91) of present-tense sentences** -- not degraded recall, structurally zero,
because its tense taxonomy has no branch for VBP/VBZ at all (it was built against LitBank's past-tense
literary register). (3) The deepest, most damning break, independently corroborated by the MCScript2.0
arc's own Stage-1b/1c numbers: even where extraction DOES fire, `event_bundle.py`'s symbol layer binds
every new filler string to a FRESH, semantically-arbitrary random hypervector
(`_bipolar_random` per novel surface string) -- so on real retellings of the "same" scripted event,
synonymous phrasings ("cracked" vs "broke") get ~0 cosine overlap by construction, and a fully-structured
FHRR event register discriminates same-scenario from different-scenario real narratives WORSE (gap
0.028) than an ungrounded bag-of-words vector over the SAME text (gap 0.153, 5.5x larger). **Structure
without grounding is actively worse than no structure at all on real prose** -- this is the sharpest,
most falsifiable finding of this drill, and it directly explains why the loop, which is toy-validated on
planted deterministic-overlap relations, cannot yet be handed real MCScript2/DesireDB text and expected
to work: its target representation's SYMBOL LAYER carries no semantic geometry, so cosine-gated retrieval
has no signal to find even when everything else (parsing, segmentation, causal facts) is correct.

None of these three breaks is a "45-year field problem" like B1's open-vocab grounding wall. All three
are BUILD/WIRE-tractable: (1) is a composition task (route a raw-text mention detector into
`situation_reader`'s entity path instead of requiring gold CoNLL); (2) is a narrow code addition (two new
tense branches, mirroring the five that already exist); (3) is a REUSE task (the substrate already owns
graded concept-similarity machinery -- `lexical_similarity.concept_similarity`, `concept_encoder.py`,
`ppmi_sparse_encoder.py` -- and `outcome_event_extraction.py`'s own CH_C channel already demonstrates the
exact wiring pattern needed; it has just never been plumbed into `event_bundle.EventBundleCodec`'s symbol
codebook). This is a materially BETTER position than the DesireDB/B1 grounding wall: none of these three
sub-breaks requires new science, and Section 4 designs a single cheap experiment that tests the highest-
leverage one (grounding) directly against the two real baselines the MCScript2.0 arc already measured.

P_deflated = **0.45** for "this three-way decomposition + the E3 gate below is the correct next attack"
(novel-synthesis cap 0.50; not fully at cap because (2) and (3) are disk-measured this cycle, not
extrapolated, but the GATE's predicted outcome in Section 4 is genuinely open). P for "the grounded-
symbol E3 gate HARD-PASSes as designed" specifically: **~0.40** (deflated, per lit-scan/novel-synthesis
calibration discipline) -- carried consistent with the barrier map's own P~0.40 for Phase 2's extraction
gate; this note sharpens WHAT that gate should measure but does not resolve the underlying uncertainty.

---

## 1. THE TARGET REPRESENTATION (what the loop actually consumes)

Read directly from `hdlab/situation_model_accumulate.py`, `hdlab/event_bundle.py`,
`hdlab/situation_focus.py`, and their one real consumer,
`experiments/exp_focus_pullin_causal_stage2a_multihop_loop_v1.py` (the validated retrieve-validate-
advance loop, HARD_PASS 5/5). The loop needs exactly this, no more and no less:

1. **A monotonically-growing CODEBOOK of event vectors**, each row an `EventBundleCodec.encode_event
   (role_fillers)` bipolar bundle: `quantize(sum_r bind(role_key[r], filler_vec[r]))` over roles
   `(PRED, AGENT, PATIENT, TENSE)` (production default, `event_bundle.DEFAULT_ROLES`). Each event is
   addressed by a stable INTEGER INDEX into this codebook -- that index, not a string or a text span, is
   the event's identity everywhere downstream (`CausalLinkRegister`, `pull_in`, the focus).
2. **AGENT/PATIENT filler symbols must be COREFERENCE-CANONICALIZED entity IDs**, stable across the
   whole passage, not raw surface tokens. Without this, "she picked up THE EGG" (event 3) and "she
   cracked IT" (event 5) can never be linked by any bind/unbind operation, no matter how good grounding
   or extraction is otherwise -- the codebook has no notion that "the egg" and "it" name the same thing.
3. **PRED/filler symbols should be GROUNDED (concept-space-derived), not raw strings.** `pull_in`
   (`hdlab/cleanup_family.py::iterative_attractor` wrapped by `pull_in_multi_exclude`) admits a candidate
   by RAW COSINE against a calibrated `GATE_THRESH` (0.28-0.32 across the validated cells). Cosine
   between two event bundles is driven entirely by shared/near-shared filler vectors. If filler vectors
   for synonymous real-world phrasings do not overlap, cosine has structurally nothing to find.
4. **A `CausalLinkRegister`** (`situation_model_accumulate.py`, the production promotion of the Stage-1/
   2A `BipolarCausalRegister`) populated via `add_causal_link(cause_idx, effect_idx)` -- CAUSE/EFFECT
   meta-role bindings BETWEEN two event indices in the SAME codebook. `query_effect_of` / `query_cause_of`
   decode by unbind + cleanup-argmax over the `idx_vecs` vocabulary. This is what the VALIDATE step
   checks a `pull_in` candidate against (Stage-2A's core, HARD_PASS-proven mechanism: VALIDATE arrests
   multiplicative per-hop error, NO_VALIDATE degrades).
5. Everything must be reachable from "now" (the most recent event) by `pull_in` against the WHOLE
   accumulated codebook (toy scale) or the WIRED store (X1, production scale) at a fixed, pre-calibrated
   `GATE_THRESH` -- the threshold is NOT re-tuned per document; it is fixed before the run.

**The one-sentence spec:** the loop needs a growing, integer-indexed sequence of `{PRED, AGENT, PATIENT,
TENSE}` role-slot-bound event bundles, whose AGENT/PATIENT fillers are coreference-canonicalized entity
IDs and whose PRED/filler vectors carry real semantic-similarity geometry, plus a parallel CAUSE/EFFECT
edge set between those same integer indices. Nothing else in the loop's design (Stage-1, Stage-1.5,
Stage-2A) depends on anything beyond this. Section 3 traces exactly which piece of this five-part spec
breaks first on real prose, and how badly.

---

## 2. OWNED ENCODE-ORGAN INVENTORY (B1-B5) -- what each actually produces, disk-read

**B1 Lexical access + concept grounding.** `hdlab/vwfa.py`, `hdlab/concept_encoder.py`,
`hdlab/ppmi_sparse_encoder.py`, `hdlab/lexical_similarity.py` (exposes `concept_similarity(a, b)` and a
calibrated `SIMILARITY_LINK_THRESHOLD`, already used by `outcome_event_extraction.graded_relation_
channel`), `hdlab/wordnet_polarity_propagation.py`. PRODUCES: a graded similarity score or embedding for
a KNOWN-vocabulary word pair; CSKG (1.24M edges) as backing content. MISSING to reach the target rep:
none of these are wired INTO `event_bundle.EventBundleCodec`'s symbol codebook -- `_sym_vec` (event_
bundle.py line ~112-117) draws a fresh `_bipolar_random` vector for any string it has not seen before,
with zero reference to `concept_encoder`/`lexical_similarity` at all. The grounding MECHANISM exists; it
is simply not plumbed into the event-bundle symbol layer that the loop actually reads.

**B2 Syntactic structure-building.** `hdlab/pos_tagger.py`, `hdlab/arc_parser.py`, exposed together via
`hdlab/candidate_generator.CandidateGenerator` (persisted UPOS + hashed arc-factored perceptron
checkpoints, `data/frontend_assets/`). PRODUCES: tokens, UPOS tags, a head-index dependency arc for every
token, from ANY raw text string -- no gold annotation required. This is the one B-regime organ MEASURED
robust on real prose already: the MCScript2.0 Stage-1 probe found root-verb-lemma extraction fires on
150/150 sampled dev instances (100%); this cycle's own scan (Section 3) confirms `root_fire_rate` >= 0.9
on 7/8 traced instances. MISSING: nothing structural -- B2 is not the wall.

**B3 Thematic-role assignment.** `hdlab/thematic_role_labeler.py` (`frame_slot_role`, `lemma_verb`,
`STRICTLY_INTRANSITIVE_VERBS` arity gate), `hdlab/frame_induction.py` (OOV construction->frame
induction, held-out subj-axis acc 0.833), `hdlab/animacy_lexicon.py`. PRODUCES: given a verb lemma and a
syntactic slot (subj/obj), a frame-licensed role label, and a POSITIONAL subj/obj pick from an arc
parse (`mcscript_extraction.extract_args`: pre-verbal nominal head with the verb as its dependency head
= subject; post-verbal = object). MISSING: this only produces a role for the ONE head token nearest the
verb per clause, reduced across a WHOLE narrative to a single most-frequent-vote SUBJ/OBJ in the MCScript
front end (`extract_instance_tuple`) -- not a per-CLAUSE typed role for every event in sequence, which is
what the target representation (Section 1, point 1) needs. `situation_reader._assign_roles` DOES do the
correct per-event version, but only when fed pre-segmented mention structure (see B4 below).

**B4 Coreference / entity-identity tracking.** `hdlab/coreference_resolver.py` (canonical MATCH-OR-
ALLOCATE, Binding Principle B, strict-Cb Centering, registry status WIRED_AND_PIPELINE_USED),
`hdlab/coref.py`, `hdlab/scene_segment.py`. PRODUCES: given a stream of MENTION dicts (head token,
sentence index, gender/number, is-pronoun flag, cluster id) and PRONOUN TARGETS to resolve, a resolved
antecedent cluster per pronoun. MISSING, concretely: it has NEVER been invoked anywhere in the MCScript2.0
pipeline (confirmed by reading `hdlab/mcscript_extraction.py` and the three `exp_mcscript2_*` cells --
zero references to `coreference_resolver`/`coref`/mention detection). The reason is structural, not a
priority choice: `coreference_resolver`'s callers all expect a MENTION STREAM, and the only mention-
stream builder on disk (`hdlab.coref.parse_litbank_conll`) reads a coref-COLUMN-annotated CoNLL file --
i.e. gold mention spans supplied by the corpus, not detected from raw text. There is no raw-text mention
DETECTOR on disk today (a nominal-POS-tag scan, as `mcscript_extraction.extract_args` already does for
subj/obj, would suffice as a first cut, but it does not exist as a general mention-stream builder).

**B5 Event segmentation + event-span encoding.** Two DIFFERENT, never-composed organs:
(a) `experiments/_temporal_ordering.extract_events(text)` -- takes RAW text directly (no CoNLL
requirement), tags it, and returns `Event(lemma, idx, pos, tense)` for every VBD / VBN(+had/+be/
+coordination) / VB(+modal) / VBG(participial) token. This is what `situation_reader._read_events` calls
per sentence to build the actual per-clause `EventBundleCodec` bundles. PRODUCES exactly the per-clause
typed-event sequence the target representation needs, in principle. MISSING (Section 3 quantifies): zero
coverage for simple-present-tense (VBP/VBZ) predicates -- not in its tense taxonomy at all.
(b) `hdlab/outcome_event_extraction.py::extract_outcome_event` -- takes a raw `(desire, outcome)` pair,
parses `outcome` via `CandidateGenerator` (the SAME robust real-prose front end as B2), segments it into
clauses, and picks the ONE clause whose nominal tokens link to the desire's referent. PRODUCES a single
best-clause span, not a sequence of typed events -- it is a goal-outcome-specific extractor (DesireDB),
not a general narrative event segmenter, and has no notion of TENSE, AGENT/PATIENT roles, or multiple
events per narrative. It is the right SHAPE of solution (glass-box, real-prose-robust, referent-linked)
but the wrong SCOPE for the loop's target representation, which needs every event in sequence, not one.

---

## 3. TRACE THE BREAK ON REAL PROSE (empirical, MCScript2.0 dev, 60 instances / 545 sentences)

Used `data/corpora/mcscript2/extracted/dev-data.xml` (real, already-downloaded MCScript2.0 dev split,
355 crowd-sourced first-person narratives across 162 scenarios -- the SAME corpus the MCScript2.0 arc
validated against). Parsed with `hdlab.mcscript_extraction.parse_mcscript_xml` (unmodified, reused). Ran
the owned front ends LIVE against 60 real dev instances (545 sentences) this cycle; numbers below are
measured this cycle, not cited from the prior arc.

**(i) B2/root-verb extraction: confirmed robust, not the wall.** Replicated the Stage-1 finding: root-
verb fire rate >= 0.9 on 7/8 traced instances (1.0 on 6/8), matching the prior 100%-on-150 result.

**(ii) B5 event segmentation: a sharp, measured, tense-register coverage gap.** Live scan, 545 real
sentences:
- 545 total sentences; 105 (19.3%) get ZERO events from `extract_events`; 102 of those 105 (18.7% of
  all sentences) have a verifiable finite verb present (POS-confirmed) that the segmenter simply has no
  branch for.
- 91 sentences (16.7% of all) are simple-present-tense (VBP/VBZ present, no VBD) -- and of those, **61
  (67.0%) get zero events**, not degraded recovery, exactly zero, because `extract_events`'s tense
  taxonomy (SIMPLE_PAST / PAST_PERFECT / PASSIVE / MODAL_SUBORDINATE / PARTICIPIAL) has no SIMPLE_PRESENT
  branch at all.
- 1 of 60 sampled instances (dev id=2, scenario "serving a drink") is written ENTIRELY in present tense
  and yields literally zero events across all 6 traced sentences despite every sentence containing a
  clear action ("I check that he is of age", "I then go to the beer cooler ... and fill it up with
  beer", "I place a napkin down and set the beer on top").
- Concrete failing examples (present tense, POS-confirmed finite verb, zero events extracted):
  `"I have a guest sit at the bar"` (POS: PRP VBP DT NN NN IN DT NN); `"I check that he is of age"`
  (PRP VBP ...); `"He then places his cash with the receipt"` (PRP RB VBZ ...). Contrast: the SAME
  extractor on a past-tense instance (dev id=1, "drying clothes") recovers 14 events across the same 6
  sentences -- the mechanism works, the coverage gate is purely morphosyntactic-tense-keyed.
- This is a clean, cheap-to-name failure mode: `extract_events` was built against LitBank (19th-century
  literary narrative, near-universally past tense); MCScript2.0 is present-day first-person crowd-sourced
  narrative, where present-tense procedural retelling ("I go... I grab... I fill it...") is common. The
  register mismatch, not extraction difficulty per se, is the immediate cause.

**(iii) The structural incompatibility: `situation_reader.py` cannot run on this corpus at all.**
`situation_reader.read(conll_path)` calls `hdlab.coref.parse_litbank_conll` (requires a coref-annotated
CoNLL file) and `hdlab.scene_segment.parse_conll_sentences` (requires the same). MCScript2.0's XML has no
coref annotation and is not CoNLL-formatted. This means the ONE organ that actually assembles the target
representation's shape (per-clause typed events into a Cowan-4 focus, entity tracking via the coref
backbone, causal links via `_causal_network`) has literally never been exercised on this or any other
raw, un-annotated real corpus -- its entire real-prose validation to date is on LitBank gold. The
MCScript2.0 arc worked around this by using a DIFFERENT, narrower front end (`mcscript_extraction.py`)
that bypasses `situation_reader` entirely and reduces each whole narrative to ONE flat 4-tuple
(trigger-verb, consequent-verb, most-frequent-agent, most-frequent-patient) -- never producing a
sequence of typed per-clause events, never populating a `CausalLinkRegister`, never calling coreference
resolution at all.

**(iv) The grounding-interface break: structure is measurably WORSE than no structure, on this exact
corpus.** This is not new to this cycle (the MCScript2.0 arc's own Stage-1b/1c measured it), but this
cycle localizes WHY by reading `event_bundle.py` line-by-line: `_sym_vec` draws
`_bipolar_random((n_dim,), self._gen)` for any never-before-seen filler string, with NO reference to any
grounding organ. Stage-1b's own numbers (72 registers / 12 scenarios, `build_instance_register`'s narrow
4-role FHRR tuple): matched-pair (same-scenario) mean cosine 0.1555 vs wrong-pair 0.1275, a weak 0.028
gap, heavy overlap (p10 matched = -0.010 < p90 wrong = 0.228). Stage-1c's control (the SAME 72 instances,
scored instead by `grounding_acquisition_loop.context_vector`, an UNSTRUCTURED bag-of-content-words
bipolar bundle over the whole narrative): matched-pair 0.1905 vs wrong-pair 0.0379, a 0.153 gap -- 5.5x
larger than the structured register's. **The structured, role-typed representation the loop is built to
consume discriminates real narrative content WORSE than throwing the roles away entirely and just
bundling the words**, because its symbol layer cannot recognize that two different real retellings used
different words for the same referent/event. This is the single most load-bearing finding for the
binding-constraint diagnosis: it is not merely that extraction "sometimes misses a span" -- it is that
even successful, on-target extraction currently produces a REPRESENTATION with less usable signal than
an untyped baseline, on real (non-templated) text.

**(v) Coreference load and causal-connective sparsity, quantified (context for Phase 2/3 sizing).** Same
60-instance / 545-sentence sample: 201 raw "it"/"them" tokens, a rate of 0.369 per sentence -- a heavy
anaphora load that AGENT/PATIENT canonicalization (point 2 of Section 1) must resolve for the causal
register to ever link the right events. Explicit causal connectives (`_causal_network`'s known set:
because/so/since/thus/hence/therefore/consequently/accordingly) appear in only 71/545 sentences (13.0%)
-- meaning even a working causal-link extractor wired onto this corpus would directly cover only ~1 in 8
sentences; the other ~87% of procedural-sequence causal structure is IMPLICIT (temporal adjacency
standing in for causality), which `situation_reader`'s own docstring already discloses its
`_causal_network` mechanism cannot genuinely distinguish from mere adjacency.

**Summary of the trace:** the break is not one thing. In order of how early each would block a real
end-to-end run: (1) `situation_reader` cannot ingest this corpus at all (structural/composition gap,
Section 5 route = BUILD a raw-text mention-stream adapter); (2) even a raw-text-capable per-clause
segmenter loses ~19% of sentences to a narrow, named tense-coverage hole (Section 5 route = BUILD, cheap);
(3) even where segmentation and roles are correct, the symbol layer that feeds the loop's cosine-gated
retrieval has no semantic geometry, and this is EMPIRICALLY WORSE than doing nothing structural at all
(Section 5 route = REUSE existing grounding organs, wire them into `event_bundle`'s symbol codebook).

---

## 4. THE CHEAP CAN-FAIL FEASIBILITY GATE (E3, design only, not run)

**Name:** `exp_focus_encode_grounded_event_discrimination_realprose_v1` (proposed anchor; not yet
authored -- this is a design, per the task scope, for exp_dev/strategy to pick up).

**What it measures:** whether GROUNDING the event-bundle symbol layer (the single highest-leverage fix
identified in Section 3(iv), reusing already-owned organs) recovers loop-consumable discrimination on
real MCScript2.0 dev text -- i.e., whether a properly-grounded, per-clause-typed event representation
beats both the ungrounded-structured baseline AND the unstructured bag-of-words baseline the prior arc
already measured. This directly tests the binding-constraint's most tractable sub-break first, cheaply,
before committing to the (also-needed, but more expensive) `situation_reader` raw-text adapter build.

**Design (reuses almost entirely owned infra -- no training, no GPU, small sample):**
- Sample: 40-60 real MCScript2.0 dev instances across >=12 distinct scenarios (matches the prior arc's
  own tractable sample size; same corpus, held-out from anything used to calibrate thresholds).
- Pipeline under test ("GROUNDED" arm): `CandidateGenerator` arc-parse (owned, real-prose-robust, B2) ->
  `extract_events` PATCHED with a SIMPLE_PRESENT branch for VBP/VBZ (the Section 3(ii) fix; mirrors the
  five existing branches, same shape, no new mechanism) -> positional AGENT/PATIENT per clause (mirrors
  `mcscript_extraction.extract_args`, reused unmodified) -> for each filler string, source its
  `EventBundleCodec` symbol vector from `hdlab.lexical_similarity`/`concept_encoder` grounded space
  (nearest-known-concept snap or blended embedding) INSTEAD of `_bipolar_random` on first sight -> one
  `EventBundleCodec.encode_event` bundle per clause -> per-instance aggregate (sum/bundle across the
  narrative's events, or `situation_focus.ChunkedFocus` if event count exceeds capacity=4).
- Real baseline 1 (REUSE, not re-run): Stage-1c's unstructured bag-of-content-words `context_vector` gap
  = 0.153 (same 72-instance measurement basis; the gate should also re-measure it on the NEW 40-60
  instance sample for an apples-to-apples comparison, since it is cheap to recompute).
- Real baseline 2 (REUSE): Stage-1b's ungrounded-structured register gap = 0.028 (same logic -- the
  UNGROUNDED arm of the SAME pipeline above, i.e. leave `_sym_vec` on `_bipolar_random`, is the direct,
  one-variable ablation control, not just a cited number).
- Discriminator: matched-pair (same-scenario) mean cosine minus wrong-pair (different-scenario) mean
  cosine, exactly the prior arc's own metric (a real, previously-validated, can-fail measure -- it has
  already discriminated a true positive at 0.153 and a true near-null at 0.028 on this corpus).
- Scramble control (mandatory, per META_RULE_AF-style arms-must-differ discipline): permute which
  grounded filler vector is bound to which role within each event (role<->filler binding destroyed,
  `event_bundle.encode_scrambled_event` already exists for exactly this). The gap must collapse.
- ONE variable held constant across the primary ablation: grounding on/off. Tense-fix is applied in
  BOTH arms (so the ablation isolates grounding specifically, not "more events fired"); tense-fix's own
  effect can be reported as a secondary, non-primary diagnostic (event-count recall before/after).

**Pre-registered HARD-PASS / HARD-FAIL bands:**
- **HARD-PASS:** grounded-structured gap >= 0.153 (matches or beats the real bag-of-words baseline) AND
  grounded-structured gap >= 3x the ungrounded-structured gap (>= 0.084, i.e. the lift is attributable to
  grounding specifically, not just to more events firing after the tense fix) AND scramble-control gap
  <= 0.02 (near-zero, proving the gap is genuinely role-structural, not an artifact of vocabulary overlap
  alone). If this fires, grounding the symbol layer is the correct, sufficient next build step and Phase
  2/3 of the barrier map's plan can proceed on the current representation shape.
- **HARD-FAIL:** grounded-structured gap < 0.05 (no material improvement over the ungrounded 0.028
  baseline) OR scramble-control gap > 0.5x the real gap (the discriminator does not actually depend on
  role structure). If this fires, the problem is NOT (only) missing grounding content -- the role-slot
  HD-binding representation itself may be the wrong shape for real, lexically-diverse narrative content,
  and Phase 2 of the barrier map needs to reconsider the representation before investing further in this
  encode path (a materially more serious, structural finding, and the honest place to learn it cheaply).
- **MIDDLE_BAND:** between the two bands -- grounding helps but not enough to fully recover the bag-of-
  words baseline; likely diagnosis is that word-level grounding is necessary but not sufficient without
  ALSO fixing the coreference/entity-canonicalization gap (Section 3(v)), which would motivate sequencing
  the `situation_reader` raw-text adapter (Section 3(iii)) as the very next step rather than a nice-to-have.

This gate is cheap (40-60 short real narratives, no GPU, reuses `CandidateGenerator` + `lexical_
similarity` + `EventBundleCodec`, all already loaded/persisted), can-fail (a real, previously-measured
baseline it must beat, not a vacuous strawman), one-variable (grounding on/off, tense-fix held fixed
across arms), and glass-box (every bound vector, every cosine, every scramble is inspectable). It is
explicitly narrower than the full Phase-2 gate the barrier map already sketched (which targets outcome/
event-span extraction specifically) -- this gate targets the SYMBOL-GROUNDING sub-break first because
Section 3(iv)'s finding (structure-worse-than-no-structure) is the sharpest, cheapest-to-test, and most
likely to be the dominant lever, per the measured 5.5x gap.

---

## 5. BRAIN-FIDELITY ON THE BREAK

**B5 tense-coverage gap.** BRAIN: the event-segmentation network (Zacks-Speer-Reynolds SEM; Baldassano
2018) segments continuous experience at PREDICTION-ERROR spikes over the SITUATION MODEL -- a change in
action, goal, or location -- regardless of how the language surface marks tense/aspect. SHAPE: continuous
PE-magnitude monitoring; POSITION: every moment; METRIC: prediction-error magnitude. Our `extract_events`
instead keys segmentation on a CLOSED SURFACE-MORPHOLOGY LOOKUP TABLE (which verbal inflection/aux
pattern appears) -- a shallow proxy that happens to correlate with event boundaries in past-tense literary
prose but has no principled reason to generalize, and measurably does not (Section 3(ii)). GAP CLASS: two
routes, not one. Cheap route = BUILD-primitive (add a SIMPLE_PRESENT branch for VBP/VBZ, same shape as
the five existing branches -- ships now, closes the measured 67% hole). Principled route = REUSE-organ:
the substrate already owns `hdlab/predictive_coding.py` (a Friston/Rao-Ballard PE gate) per the barrier
map's own B5 entry, and it is NOT currently used for segmentation at all -- routing event-boundary
detection through an actual PE signal (over a lexical/semantic prediction stream) instead of a POS-tag
lookup table would be the brain-faithful fix and would generalize past tense-register brittleness for
free. Recommend shipping the cheap fix now (unblocks E3) and filing the PE-gate reuse as a disclosed
follow-on, not a silent substitute.

**Structural incompatibility (`situation_reader` requires gold CoNLL).** BRAIN: there is no analog --
human comprehension is one continuous process from perceptual input to situation model; there is no
"annotated mode" vs "raw mode" split. This gap is a pure ENGINEERING/composition artifact, not a missing
brain mechanism. ROUTE: BUILD (a thin adapter: a raw-text mention-stream builder using the SAME
NOMINAL-POS-tag technique `mcscript_extraction.extract_args` already uses for subj/obj, generalized into
the mention-dict shape `coreference_resolver`'s callers expect) + WIRE (compose it into `situation_
reader._read_entities`/`_read_events` in place of `parse_litbank_conll`). This single adapter unlocks
BOTH the B4 coref gap and the B6 assembly gap in one build, since both currently fail for the identical
reason (no mention stream from raw text).

**Grounding-interface gap (`event_bundle` symbol vectors).** BRAIN: VWFA -> posterior MTG/STG -> ATL
hub-and-spoke lexical access (Cohen-Dehaene; Hickok-Poeppel; Lambon-Ralph) is inherently GRADED: every
word form activates a distributed similarity-preserving pattern in the SAME semantic space, so synonyms
share substantial activation overlap purely from meaning. SHAPE: distributed graded activation with
spreading pre-activation. Our `event_bundle._sym_vec` does the structural opposite: a fresh, independent,
semantically-arbitrary random vector per new surface string, so two synonyms have ~0 EXPECTED cosine.
This is the single sharpest SHAPE mismatch found this cycle -- not a missing feature so much as an
inverted design choice at exactly the interface the barrier map names as binding. ROUTE: REUSE-organ.
The substrate already owns graded concept-similarity machinery (`lexical_similarity.concept_similarity`,
`concept_encoder.py`, `ppmi_sparse_encoder.py`) and `outcome_event_extraction.graded_relation_channel`
already demonstrates the exact wiring pattern (route a lexical comparison through `concept_similarity`
instead of literal string/synset match) for a narrower use case. The fix is to source `EventBundleCodec`
symbol vectors from this existing grounded space rather than `_bipolar_random` -- a REUSE + WIRE task,
not a new mechanism, not a fact-supply problem, and (per Section 4) directly testable cheaply.

**Coreference unattempted on real narrative prose / heavy anaphora load.** BRAIN: hippocampal relational
binding + antecedent retrieval (the standing MEMORY anchor: coreference == hippocampal relational
antecedent-retrieval). `coreference_resolver.py` is itself a mature, WIRED_AND_PIPELINE_USED organ --
the gap is purely that it has never been fed a real-text mention stream (same root cause, same fix, as
the structural-incompatibility item above). ROUTE: REUSE-organ (coreference_resolver.py) + BUILD (the
same raw-text mention-stream adapter closes this too).

**Causal-connective sparsity / dominant implicit causality.** BRAIN: Trabasso & van den Broek's causal
network is NOT purely connective-triggered -- humans infer causal links via world-knowledge PLAUSIBILITY
and counterfactual-necessity testing even absent an explicit connective (this is exactly why FORWARD
inference is effortful/non-automatic while BACKWARD bridging is fast, per McKoon-Ratcliff and Baggett-
Graesser). Our owned `_causal_network.py` mechanism is explicitly self-disclosed (in `situation_reader`'s
own docstring, carried from the 07-30 assessment) as "REDUCIBLE to connective-else-most-recent... the
plausibility/force-dynamics component is NOT isolated" -- a shallow surface-marker proxy for the brain's
genuine knowledge-query process, and on this real corpus that proxy directly covers only 13.0% of
sentences (Section 3(v)). ROUTE: SUPPLY-fact (query the owned CSKG 1.24M-edge causal knowledge store for
plausible cause-candidates among temporally-adjacent event pairs, rather than pattern-matching a fixed
connective word list) + LEARN-rule (calibrate an acceptance threshold on the query result). This is
genuinely the hardest of the five sub-breaks -- closer to real science than the other four -- and should
be sequenced AFTER the grounding/segmentation/structural fixes above, since it needs correctly-typed,
correctly-grounded events to query against in the first place (it presupposes Sections 3(i)-(iv) fixed).

---

## 6. HONEST DEFLATED GRADE + CREDIT + WIRE-DEBT

**Credit, explicit.** The MCScript2.0 arc (`hdlab/mcscript_extraction.py`, `preregs/2026-08-09_
mcscript2_real_benchmark_validation_v1.md`) established B2 real-prose robustness (100% root-verb fire
rate) and FIRST surfaced the grounding-interface finding this note builds on (Stage-1b's weak 0.028
structured-register gap vs Stage-1c's 0.153 bag-of-words gap) -- this drill's contribution is (a)
localizing WHY at the source-code level (`event_bundle._sym_vec`'s `_bipolar_random` call, no grounding
reference anywhere in the symbol path), (b) discovering the SEPARATE, previously-undocumented B5
tense-register coverage gap via a fresh 545-sentence live scan (67% present-tense zero-recall was not
previously measured or reported anywhere on disk), (c) discovering that `situation_reader.py` -- the
organ the barrier map credits as "BUILT" for Regime B -- has never actually been run on any raw,
un-annotated real corpus, a scope limit not previously disclosed in its own docstring or the barrier map,
and (d) quantifying the coref/causal-connective real-prose load (0.369 it/them per sentence; 13.0%
causal-connective coverage) needed to size Phase 2/3 of the barrier map's plan. `outcome_event_
extraction.py` (2026-08-09) established the METHOD this note's E3 gate design inherits directly: glass-
box `CandidateGenerator`-front-ended extraction with an honest-abstain discipline and a real-baseline
ablation control.

**Wire-don't-island debt found this cycle:** `hdlab/mcscript_extraction.py` and `hdlab/outcome_event_
extraction.py` are BOTH absent from `data/capability_registry.jsonl` (confirmed by direct query this
cycle), despite each being a real, disk-validated organ (mcscript_extraction: Stage-1 100%-fire real-
benchmark result; outcome_event_extraction: self-tested, composes four already-registered organs). Flag
for registration alongside the barrier map's Phase-1 wire-the-islands work; neither blocks E3 but both
should not remain unregistered indefinitely.

**Deflated grade.** The Section 3 empirical trace (tense-coverage numbers, structural-incompatibility
finding, grounding-interface localization) is HIGH confidence -- directly measured this cycle against
real, on-disk MCScript2.0 data, not extrapolated from literature or prior claims (P ~0.85 these numbers
reproduce on a different 60-instance sample; the mechanism-level explanations, e.g. "no VBP/VBZ branch,"
are read directly from source, not inferred). The Section 4 gate's PREDICTED OUTCOME is genuinely open
and deflated per the standing lit-scan/novel-synthesis calibration discipline: P(grounded-structured gate
HARD-PASSes as designed) ~ 0.40 -- carried consistent with, not overriding, the barrier map's own P~0.40
for Phase 2's extraction-feasibility gate. This note narrows WHAT that gate should measure (grounding
specifically, isolated as a one-variable ablation against two real, previously-measured baselines) but
does not resolve whether grounding alone suffices, or whether the MIDDLE_BAND/HARD-FAIL branch (route to
the entity-canonicalization/`situation_reader`-adapter build first) will be needed.

---

## Cheap decisive test

Section 4's `exp_focus_encode_grounded_event_discrimination_realprose_v1`: on 40-60 real MCScript2.0 dev
narratives (>=12 scenarios), does routing `EventBundleCodec`'s symbol layer through the owned grounded-
concept space (instead of `_bipolar_random`) recover or beat the real bag-of-words baseline (0.153
matched-vs-wrong-pair cosine gap, Stage-1c) while beating the ungrounded-structured baseline by >=3x
(0.028 -> >=0.084), with a role-scramble control collapsing the gap to near-zero? Cheap (no GPU, reuses
persisted checkpoints + owned grounding organs), can-fail (two real, previously-measured baselines it
must beat, not a strawman), one-variable (grounding on/off; tense-fix and sample held fixed across arms).

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

- **HARD-PASS:** grounded-structured gap >= 0.153 AND >= 3x the ungrounded-structured gap (>= 0.084) AND
  scramble-control gap <= 0.02. Grounding the symbol layer is sufficient to make the representation
  loop-consumable on this dimension; Phase 2/3 of the barrier map can proceed on the current
  representation shape. Predicted P ~ 0.40 (genuinely open, deflated per calibration discipline).
- **HARD-FAIL:** grounded-structured gap < 0.05 (no material lift over the 0.028 ungrounded baseline) OR
  scramble-control gap > 0.5x the real gap. The role-slot HD-binding representation itself, not just
  missing grounding content, may be the wrong shape for lexically-diverse real narrative -- routes to a
  representation-shape reconsideration before further encode-path investment, the correct place to learn
  this cheaply rather than after a full Phase-2/3/4 build.
- **MIDDLE_BAND:** grounding helps materially but does not fully close the gap to the bag-of-words
  baseline -- routes to sequencing the `situation_reader` raw-text mention-adapter (Section 3(iii),
  which also closes B4 coreference) as the next build, on the diagnosis that entity-canonicalization is
  the co-binding constraint alongside symbol grounding, not a separable nice-to-have.
- **Independent, already-decided finding (not gated on E3):** the B5 tense-coverage gap (67% zero-recall
  on present-tense sentences, Section 3(ii)) is real, measured, and cheap to fix regardless of E3's
  outcome -- it should ship as a small patch to `extract_events` (a SIMPLE_PRESENT branch) independent of
  and prior to E3, since E3's own design (Section 4) requires it to isolate grounding as the one variable.

## Cross-thread synthesis

- Directly extends `notes/research_comprehension_barrier_map_brain_foundational_2026-08-10.md`'s Section
  3 binding-constraint diagnosis and Section 4 Phase-2 plan: that map named the binding constraint at the
  regime level (B5 extraction feeding B1 grounding) and sketched ONE feasibility gate (event/outcome-span
  extraction beats BoW/first-last on MCScript2 dev). This note decomposes that single named constraint
  into three independently-tractable sub-breaks via live code+data tracing, and designs a narrower, cheaper
  FIRST gate (symbol grounding specifically) that can run before the map's own broader Phase-2 gate,
  because Section 3(iv)'s finding (structure-worse-than-no-structure) suggests grounding is the dominant,
  cheapest lever to test first.
- Extends the MCScript2.0 real-benchmark arc (`preregs/2026-08-09_mcscript2_real_benchmark_validation_
  v1.md`, `hdlab/mcscript_extraction.py`, Stage 0/1/1b/1c): reuses its dataset, its front end, its two
  discrimination numbers as real baselines, and its Stage-1b/1c ablation methodology directly as the E3
  gate's template -- this is a continuation of that arc's own logic applied to the loop's actual target
  representation (a per-clause typed event sequence) rather than the arc's own narrower single-tuple
  reduction.
- Extends `hdlab/outcome_event_extraction.py`'s 2026-08-09 build rationale (the DesireDB finding that
  named "outcome extraction," not grounding quality, as the blocker): this note's Section 3 finds a
  RELATED but DISTINCT blocker on a different corpus (MCScript2.0) -- grounding-interface quality, not
  extraction firing -- suggesting the binding constraint is not one single failure mode across corpora
  but a small set of co-occurring, corpus-dependent sub-breaks that need to each be tested and fixed.
- Confirms `notes/how_the_brain_reads_comprehension_target_audit_2026-07-28.md`'s central claim (deep
  situation-model comprehension requires more than surface extraction) with a new, sharper piece of
  evidence: even STRUCTURALLY CORRECT extraction is insufficient without grounded symbol geometry, which
  is a more precise statement than "extraction is the blocker" alone.

## Substrate-product implications

This scoping converts a program-level diagnosis ("the encode path is the wall") into three independently
shippable, cheap builds, ranked by leverage-per-cost: (1) the tense-coverage patch (hours, unblocks ~19%
of real sentences immediately, needed as a precondition for E3 itself); (2) the grounded-symbol wire
(Section 4's E3 gate, days, tests the highest-measured-leverage fix against two real baselines before
committing further); (3) the raw-text mention-stream adapter (unblocks both B4 coreference and the B6
`situation_reader` assembly on any real corpus, larger build, MIDDLE_BAND-gated by E3's outcome). None of
these three requires new science or external content acquisition -- they are composition and wiring of
organs the substrate already owns, which is a materially better risk profile than the B1 open-vocab
grounding wall the DesireDB arc hit. The commercial/scientific risk this note narrows is specifically
whether grounding the symbol layer is SUFFICIENT (HARD-PASS, cheap path forward) or whether the
representation itself needs rethinking (HARD-FAIL, a more expensive pivot) -- E3 is designed to surface
that answer before either the full Phase-2 extraction build or further loop/store investment.

## Citations (verified count)

This is primarily an on-disk empirical drill (code + real corpus data), not a literature lit-scan; no
external search was performed (correctly, per scope -- a code-tracing/feasibility-scoping task). Brain-
system citations in Section 5 are CARRIED, not re-derived, from the barrier map's own verified citation
base (Zacks & Franklin / Kurby & Zacks 2008 event-segmentation PE; Baldassano-Hasson-Norman 2018;
Friston/Rao-Ballard predictive coding; Cohen-Dehaene VWFA; Hickok-Poeppel; Lambon-Ralph hub-and-spoke;
Trabasso & van den Broek 1985; McKoon-Ratcliff 1992; Baggett-Graesser backward-bridging automaticity;
the standing MEMORY anchor for coreference == hippocampal relational antecedent-retrieval) -- none
fabricated or re-asserted from memory here; all six citations above are already independently verified
in the barrier map's own citations section, credited there. ON-DISK VERIFIED THIS CYCLE (read directly,
executed against real data, not from memory): `hdlab/situation_model_accumulate.py`, `hdlab/event_
bundle.py`, `hdlab/situation_focus.py`, `hdlab/outcome_event_extraction.py`, `hdlab/situation_reader.py`
(full 900+ line read), `hdlab/mcscript_extraction.py`, `experiments/exp_focus_pullin_causal_stage2a_
multihop_loop_v1.py`, `experiments/_temporal_ordering.py` (`extract_events` source);
`data/capability_registry.jsonl` (registry query); `data/corpora/mcscript2/extracted/dev-data.xml` (60
real instances / 545 real sentences parsed and traced live this cycle via two throwaway scratchpad
scripts, not committed to the repo); `data/orchestrator_status_log.jsonl` (last-5 research_delivery
dedup check).
