# Content-sourcing drill: causal + associative world-knowledge for the focus (2026-08-09)

Content pillar of the grounded self-growing narrative-comprehension program. USER framing: the
focus/state-of-mind simulation "needs enough info to PULL IN things that are CLOSE to what it
builds, with CAUSAL INFERENCE on what things lead to what things." Method: on-disk verification of
every existing hdlab organ + data artifact touching this question (read, not assumed), plus 2
parallel live Sonnet lit-scans (generic public terms only, no substrate-novel names off-platform)
on the two angles the standing prior-art drill did NOT already cover (free-association norms;
large-codebook VSA/HDC cleanup capacity). Cross-references
`notes/research_prior_art_narrative_schema_learning_2026-08-09.md` (causal-KG ratings, already
live-verified there and reused here without re-drilling) and
`notes/research_script_half_synthesis_2026-08-09.md` (ATOMIC-as-lookup, already flagged as the
concrete OOV/non-VerbNet fallback).

## HEADLINE

**The causal half of this drill is not a sourcing gap, it is a WIRING gap** — and the wiring gap is
smaller than it looks. `experiments/exp_cskg_foundation_v1.py` already landed, on
2026-07-26, a **HARD_PASS-certified** (`data/exp_cskg_foundation_v1/metrics.json`:
`real=0.6961 vs shuffled=0.2368 vs base=0.2591`) spine-filtered slice of the full CSKG (Ilievski,
Szekely, Zhang 2021 — merges ConceptNet + ATOMIC + FrameNet + Roget + Visual Genome + Wikidata-CS +
WordNet) sitting on disk at `data/cskg_foundation_v1/` as 482,588 nodes / 1,238,686 typed
causal-inferential edges, already in `hdlab/hd_fact_store.py`'s exact field schema (symbolic JSONL,
not yet vectorized), already dominated by ATOMIC's if-then relations (`at:xEffect`=100,303,
`at:xIntent`=57,685, `at:xNeed`=96,103, `at:oEffect`=35,344, etc. — 711,428 AT-sourced edges total)
plus ConceptNet's `Causes`/`HasSubevent`/`HasFirstSubevent`/`HasLastSubevent`/`MotivatedByGoal`
(measured: Causes=17,249, HasSubevent=25,369, MotivatedByGoal=9,474). `hdlab/kg_traversal.py`'s
`KGStore` (Hebbian (s,p,o) triple bind/retrieve, CERT 585: 2-hop substrate=0.426 vs
frozen-encoder-baseline=0.012, 36.49x ratio, refuse-OOD=0.999) is the ALREADY-VALIDATED retrieval
mechanism this data slots into. `hdlab/situation_focus.py` — the exact Cowan-4 focus this drill was
asked about — is registered `SHELVE` in `data/capability_registry.jsonl` with revival criteria
**"revive when a narrative/multi-sentence reading pipeline is built"**, which is the program
currently underway. None of these three pieces currently talk to each other: `situation_focus.py`
has zero references to `hd_fact_store` or `kg_traversal` anywhere in its source. **The genuine
novel-synthesis work is a `pull_in()` hook connecting three already-validated, already-on-disk
pieces, not a new data-acquisition program.** The associative half is a real, separate sourcing
gap: the CSKG spine filter EXPLICITLY DROPPED `RelatedTo` as "lexical/taxonomic dilution" (locked
decision, `preregs/2026-07-26_cskg_foundation_v1.md`), and no SWOW/USF free-association norms are
anywhere on disk. Live lit-scan surfaced BEAGLE (Jones & Mewhort 2007) as a direct, glass-box,
non-neural VSA precedent for reconstructing 80% of USF norm asymmetries from raw holographic
co-occurrence accumulation — validating that the associative signal does not require borrowed
embeddings, only a graded (weighted-bundle) extension of the bind/bundle primitives already owned.

## 1. Causal knowledge: rating + what is already on disk

| Resource | Coverage (measured where possible) | Suppliability | Verdict here |
|---|---|---|---|
| **CSKG spine (already landed)** | 482,588 nodes / 1,238,686 typed edges; AT(ATOMIC)=711,428 edges (dominant), CN(ConceptNet)=219,637, VG(VisualGenome, mostly spatial not causal)=265,865, WN/WD/FN minor | **SUPPLIABLE, ALREADY ON DISK, ALREADY GATE-PASSED** | Primary seed. Zero new sourcing cost. |
| ATOMIC / ATOMIC-2020 (if-then if-then triples) | 877K-1.33M tuples (per prior-art note, live-verified there) | SUPPLIABLE (static TSV; COMET generator is the only reference-only half) | Already IS the majority of the CSKG spine's edge mass — do not re-source separately |
| ConceptNet causal subset (`Causes`/`HasSubevent`/`HasFirstSubevent`/`HasLastSubevent`/`MotivatedByGoal`/`UsedFor`/`CapableOf`) | measured in the landed run (table above) — real but comparatively SPARSE next to ATOMIC (~90K edges vs ATOMIC's 711K) | SUPPLIABLE | Already included in the CSKG spine — do not re-source separately |
| GLUCOSE (~670K causal statements + general rules, ROCStories-grounded) | not yet on disk | SUPPLIABLE (per prior-art note, live-verified there) | Scale-up option #1 if the CSKG seed proves insufficient on STORY-register text (GLUCOSE is narrative-grounded where CSKG/ATOMIC is template-grounded — see section 5) |
| ASER (194M-648M eventualities depending on release; fully automatic dependency-pattern extraction) | not yet on disk | SUPPLIABLE, and the CONSTRUCTION METHOD is itself glass-box-reimplementable (no neural step) | Scale-up option #2 — highest raw volume, noisiest (reporting-bias, co-occurrence-weighted not crowd-validated) |
| CausalBank (314M cause/effect sentence pairs, Common Crawl connective-template mining) | not yet on disk | SUPPLIABLE | Scale-up option #3 — precision bounded by explicit-connective coverage (misses implicit causality) |

**Ranking for this drill's purpose**: wire the already-landed CSKG spine FIRST (section 6's cheap
decisive test). GLUCOSE/ASER/CausalBank are real, rated, ready-to-pull options — but per the
section 5 honest-coverage read, they would mostly extend GENERIC-scenario causal coverage further,
not close the STORY-SPECIFIC causal gap that no static resource can close (only the acquisition
loop, section 4, can).

## 2. Associative knowledge: rating (live-verified this cycle)

Live Sonnet lit-scan (2 sub-agents this cycle; see Citations) confirmed:

| Resource | Scale | License / suppliability | Verdict |
|---|---|---|---|
| **SWOW-EN2018** (De Deyne, Navarro, Perfors, Brysbaert, Storms 2019, *Behavior Research Methods* 51(3)) | 12,292 cue words, >90,000 participants, >3M raw responses; balanced subset = 300 associations/cue (R1/R2/R3); released BOTH as raw response triplets AND an aggregated cue->response conditional-probability (association-strength) table | **CC BY-NC-ND 3.0** — non-commercial, NO DERIVATIVES/redistribution without permission. Usable in-place for research; NOT freely re-shippable as a repackaged artifact | SUPPLIABLE for in-place research use; a real legal constraint if the goal is to redistribute a derived substrate artifact built from it — verify before any external release |
| **USF Free Association Norms** (Nelson, McEvoy, Schreiber 2004, *Behavior Research Methods, Instruments & Computers* 36(3)) | 5,019 normed cues, ~72,000 cue-target pairs, forward/backward strength + competitor counts + frequency | No comparable ND-clause flagged this cycle (license text not independently re-verified — mark UNVERIFIED, but no red flag found) | SUPPLIABLE; recommended FALLBACK if SWOW's ND clause blocks a planned redistribution |
| Raw distributional co-occurrence (PMI, no training) | n/a (self-computable from any corpus) | Fully SUPPLIABLE (zero external license) | Weaker predictor of free-association strength specifically than trained embeddings per the general pattern in this literature (Mandera/Keuleers/Brysbaert 2015 found skip-gram beats raw counts by a wide margin on psycholinguistic-norm prediction broadly); the field's OWN best specific PMI-vs-association-probability correlation number could not be verified this cycle (UNVERIFIED gap) — do not oversell this path on its own |
| **BEAGLE** (Jones & Mewhort 2007, *Psychological Review* 114(1)) | n/a (a MECHANISM, not a static dataset) | REFERENCE mechanism but SUPPLIABLE-COMPATIBLE: random-vector accumulation over raw co-occurrence + circular-convolution (HRR) order composition — no gradient training, no borrowed embeddings | **The direct, verified VSA precedent this drill needed**: a choice-rule over BEAGLE's holographic composite vectors reproduced 80% of the strong forward/backward asymmetries in the USF norms. This is proof that a glass-box, weighted holographic-bundle accumulation over raw co-occurrence (no trained embedding) captures real associative structure, not just noise |
| CSKG's own `RelatedTo` edges (already downloaded, already on disk in `cskg.tsv.gz`, just excluded by the spine filter) | part of the 79.1% the spine filter dropped; exact `RelatedTo` edge count not yet re-measured this cycle | SUPPLIABLE, **ZERO NEW DOWNLOAD** — same file already on disk | Cheapest possible associative seed: a second cskg_foundation-style pass re-including `RelatedTo` (or a companion pass restricted to it) costs no new acquisition, only a second run of the already-built pipeline |

No paper was found (2 independent live searches, generic-terms only) that builds a WEIGHTED
associative graph as bound/bundled hypervectors with cleanup/resonator retrieval validated against
SWOW or USF norms specifically — this is a genuine, confirmed-by-search gap, matching the standing
"don't dismiss without dispatch" discipline: it was searched, not assumed absent.

## 3. Representation + retrieval: how the store sits so the focus can PULL IN content

**Causal link encoding** (direct answer to the task's proposed scheme, corrected against what is
already built — this matters, see note below): the task's proposed
`bind(CAUSE_ROLE, cause) + bind(EFFECT_ROLE, effect)` is not a design to invent, it is
**already implemented, verbatim, as `CausalLinkRegister` in `hdlab/situation_model_accumulate.py`**
(built 2026-08-02, genuine complex64 FHRR, extends the validated `AccumulateRegister` organ,
atom 29609): `add_causal_link(cause_idx, effect_idx)` binds `CAUSE_ROLE`/`EFFECT_ROLE` exactly as
proposed, and `query_cause_of`/`query_effect_of` decode by unbind + cleanup-argmax over an
event-index vocabulary — the exact retrievable-by-unbind contract the task asked for. **Its scope
today is EVENT-to-EVENT links within one text's `max_event_slots`, not links to an external
knowledge store** — this is the concrete, narrow, already-scoped extension this drill's wiring
plan needs: generalize `CausalLinkRegister`'s event-index vocabulary so one side of a link can be a
CSKG concept-atom (from section 1's seed) instead of only an in-text event slot, rather than
building a second, parallel causal-link mechanism. Separately, `hdlab/hd_fact_store.py`'s
`FactRecord` implements the SAME bind-then-bundle recipe one level more general (bipolar, not
complex64) for the CSKG-SCALE store itself — it binds `REL` + `ARG0` (subject/cause) + `ARG1`
(object/effect) + `SOURCE` + `TRUST` into one bundle, with **provenance and trust natively bound
in**, not side metadata:

```
fact_vec = quantize(bind(REL, causal_relation) + bind(ARG0, cause) + bind(ARG1, effect)
                     + bind(SOURCE, "ATOMIC"|"ConceptNet"|...) + bind(TRUST, trust_level))
effect_hat = cleanup_OBJECT(unbind(fact_vec, ARG1))     # glass-box: never reads a plaintext copy
source_hat = cleanup_SOURCE(unbind(fact_vec, SOURCE))   # auditability: "why do you believe this"
```

`hdlab/kg_traversal.py`'s `KGStore` is the SIBLING mechanism for bulk Hebbian traversal instead of
individual fact records: `key = E[s] * R[p] * sqrt(D)`, `scores = E @ (W @ key)`, CERT-585-validated
for 1-2 hop chains (`predict_one_hop`, `predict_two_hop`, `predict_n_hop` — the last explicitly
documented as "empirically open" and MIDDLE_BAND past K=2, an honest existing capacity ceiling, not
a new one this drill discovered). Either primitive already implements the task's proposed
bind-then-unbind causal-link scheme; the missing piece is a QUERY HOOK from `situation_focus.py`
into one of them.

**Associative "closeness" WITHOUT borrowed embeddings**: extend the bind/bundle primitives already
owned to a WEIGHTED bundle — a direct, glass-box generalization, not a new mechanism:

```
assoc_vec(cue) = quantize( sum_i  strength_i * atom_vec(response_i) )
```

where `strength_i` is SWOW/USF's measured conditional response probability (or, per section 2's
zero-cost fallback, a raw PMI/co-occurrence count over CSKG's own `RelatedTo` edges or the
substrate's own reading corpus). This is literally BEAGLE's validated mechanism (weighted
accumulation of co-occurring/associated atoms into one holographic composite, no gradient training)
reused verbatim, not invented for this drill. Retrieval: cleanup/resonator lookup of `assoc_vec`
against the SAME concept codebook the causal store uses returns the nearest associates — this is
architecturally IDENTICAL to a causal-relation query, just with `REL = "AssociatedWith"` and a
graded (not binary) SOURCE weight, so it can live in the SAME `HDFactStore`/`KGStore` schema rather
than a separate mechanism (one store, two relation families).

**Capacity-aware retrieval at focus scale**: live lit-scan on VSA/HDC cleanup-memory capacity found
two distinct, honestly-different regimes that matter here and should not be conflated (a
mis-citation risk this drill specifically checked and avoided): (a) SINGLE-ITEM cleanup (nearest-
neighbor lookup of one probe against a codebook) scales roughly EXPONENTIALLY in dimension D per
secondary sources citing Plate/Frady-Kleyko-Sommer theory (exact closed-form not independently
re-derived from a primary source this cycle — flagged UNVERIFIED-exact-formula, but the qualitative
direction, that large codebooks (100K-1M items) remain discriminable at substrate dimensionalities
already in use, is corroborated by this project's OWN measured result: the 482,588-node CSKG spine
already HARD_PASSED a relation-reconstruction gate); (b) SUPERPOSITION/bundle capacity (how many
items can be recovered from ONE summed vector) is the DIFFERENT, sparser, compressed-sensing-like
regime this project's own capacity-cliff work (K/N percolation-class results, cited in the field
advisor's cap_map) already characterizes — this is the regime `situation_focus.ChunkedFocus`
already manages via chunking, and it is the regime that matters for HOW MANY pulled-in items can be
added to one focus chunk, not for how many items the BACKGROUND STORE can hold. No VSA/HDC paper
was found (confirmed absence via live search, not assumed) reporting real bind/bundle/cleanup
accuracy+latency at a 100K-1M-symbol real KG scale — meaning this project's own cskg_foundation_v1
result, ONCE actually vectorized (it is currently symbolic JSONL, not yet bound hypervectors) and
queried, would be at or past the published frontier for this specific claim; treat any such claim
with the standard novel-synthesis calibration discipline (section 7), not as an already-settled win.
Brain-fidelity note (directly actionable): Collins & Loftus (1975) spreading activation and
ACT-R's retrieval-threshold/fan-effect (Anderson) both independently establish that human semantic
retrieval is BOUNDED and DECAYING with distance, never an exhaustive lexicon search — this licenses
(and brain-motivates) a **top-K, threshold-gated `pull_in()`**, not a full-store scan, matching both
the capacity concern above and the standing brain-foundational-first discipline.

**Concrete `pull_in()` design** (the missing hook, not yet built anywhere): add a method to
`ChunkedFocus` that (1) takes the focus's current entity/event atom(s) as a probe, (2) queries the
causal/associative store (KGStore Hebbian traversal or HDFactStore role-query, relation-conditioned)
for its top-K neighbors above a confidence threshold (bounded, per the brain-fidelity note), (3)
`push()`es each retrieved item into the SAME chunking machinery already built (`_Entry`,
`slot_keys`, `inner_keys`) but tagged via a NEW `PULLED_IN` role distinct from directly-read `EVENT`
entries, so a downstream query can always distinguish "the text said this" from "the store inferred
this," and can unbind `SOURCE`/`TRUST` on request for a full provenance trace. **Open, unresolved
design decision this drill surfaces rather than papers over**: `situation_focus.py`,
`event_bundle.py`, `hd_fact_store.py`, and `kg_traversal.py` are all BIPOLAR/BSC (`{-1,+1}` real,
elementwise-multiply bind), while `CausalLinkRegister`/`situation_model_accumulate.py` (the
already-built intra-text causal-chaining primitive identified above, also reused by the just-landed
`quality_relation.py`) is genuine complex64 FHRR (`hdlab/binding.py`'s dtype-dispatched
`bind`/`unbind`). The task's stated invariant is "FHRR representation," and the field's OWN
already-built causal-chaining primitive is the complex64 FHRR one — but the actually-shelved Cowan-4
focus this task named (`situation_focus.py`) is bipolar, and the CSKG-scale store
(`hd_fact_store`/`kg_traversal`) is bipolar too. This is a genuine three-way reconciliation the
wiring build must resolve, not a detail to gloss over: either (a) port `CausalLinkRegister`'s
pattern onto bipolar vectors to match the focus and the store (loses nothing mechanically —
bind/bundle/cleanup-argmax is dtype-symmetric per `hdlab.binding`'s own dispatch design), or (b)
port `situation_focus`/`hd_fact_store` to complex64 to match `CausalLinkRegister`. Recommend (a):
the CSKG seed (section 1) is already landed in the bipolar `hd_fact_store` schema by design
(`preregs/2026-07-26_cskg_foundation_v1.md` locked this), so porting the smaller, newer
`CausalLinkRegister` to match the larger, already-gated store is less work than the reverse — and
either way, build against `hdlab.binding.bind`/`unbind` (the canonical dtype-dispatching primitive)
rather than a hardwired per-module `_bipolar_bind`, so the choice stays a one-line dtype swap, not a
rewrite.

## 4. Bootstrap + grow plan

**SEED** (highest coverage-per-effort, ranked): (1) vectorize the ALREADY-LANDED CSKG spine
(`data/cskg_foundation_v1/`, 482,588 nodes / 1,238,686 edges, HARD_PASS-gated) into an actual
`HDFactStore` or `KGStore` instance — pure engineering, zero new data acquisition, zero new
literature risk. (2) Re-run the (already-built) `exp_cskg_foundation_v1.py` pipeline with
`RelatedTo` re-included (or a companion pass restricted to it) for the zero-new-download associative
seed. (3) Layer SWOW-EN2018 (in-place research use; note the ND-license constraint before any
redistribution) as the graded-strength enrichment once (2)'s raw coverage is measured; USF Nelson as
a license-safer fallback/cross-check.

**GROW**: `hdlab/grounding_acquisition_loop.py` — built and self-tested THIS SAME 2026-08-09 date —
is already the exact FLAG -> LIBRARY -> CONSOLIDATE("sleep") -> GUARD -> BANK acquisition loop the
task asks about. It currently keys on outcome-VERB lemmas (reusing
`hdlab.consequence_learning_loop`'s credit-scan domain) with a schema-consistency split-half guard
(Warren et al. 2014's same-circuit-manufactures-false-memories finding — vote agreement ALONE never
banks anything). This is a DIRECT, already-validated reuse target for causal/associative-EDGE
acquisition one level up: flag a candidate causal or associative link encountered during reading
that is NOT yet in the seeded store; accumulate independent context traces (never folded/averaged at
intake, per Trueswell propose-verify); gate BANK on the split-half schema-consistency score (not
vote-margin alone); write the newly-grounded edge into the SAME `HDFactStore`/`KGStore` with
`SOURCE="learned"` and a `TRUST` level scaled by confidence — giving every self-acquired edge the
SAME provenance-auditability as a crowdsourced ATOMIC/ConceptNet edge, distinguishable on query.
This is "seed + grow," explicitly NOT batch-ingest-everything: the CSKG seed supplies generic
world-knowledge; the acquisition loop is the ONLY mechanism that can ever extend coverage to
story-specific content (section 5), and it is REUSED infrastructure, not a new build.

**Ordering** (each step independently testable, matching the prior-art note's own "only the
combination is novel" calibration discipline): (1) vectorize + wire the CSKG seed into a queryable
store [cheapest, most precedent] -> (2) build the `pull_in()` hook on `ChunkedFocus` + run section 6
[the one genuinely new composition] -> (3) re-point `grounding_acquisition_loop.py` at edge-level
(not just verb-level) flagging, once (1)-(2) demonstrate the store is worth growing.

## 5. Honest coverage read

CSKG's causal spine is real and HARD_PASS-validated, but its coverage is structurally bounded by
WHAT crowdsourcing produces: ATOMIC's ~24,313 base events (per the prior-art note) are a fixed,
closed set of short `PersonX does Y` templates, not open-vocabulary arbitrary narrative sentences;
ConceptNet's causal subset is comparatively sparse (measured: `Causes`=17,249, `HasSubevent`=25,369,
`MotivatedByGoal`=9,474 edges vs ATOMIC's 711,428-edge dominance in the same landed run). This means
causal coverage is STRONG for generic human-activity commonsense (the kind of thing that fills in
"why would someone plausibly do X") and STRUCTURALLY ABSENT for story-specific causal chains — no
static resource will ever contain "why did THIS character in THIS book do THIS specific thing,"
because that information does not exist outside the book. This matches the field's own documented
reporting-bias/closed-vocabulary limitation (already flagged for ATOMIC/ASER in the prior-art note)
and is not a new finding, only a re-confirmation applied to the specific already-landed artifact.
For associative coverage, SWOW (12,292 cues) and USF (5,019 cues) together concentrate on
common/mid-frequency English vocabulary — real coverage for everyday words, near-zero for proper
nouns, invented terms, or a specific narrative's low-frequency vocabulary. **This drill could NOT
verify an exact measured overlap percentage between CSKG/ATOMIC's lemma vocabulary and any
MCScript-style narrative-comprehension benchmark's own vocabulary** — reporting a specific coverage
percentage here would be fabricated precision; the honest answer is "unmeasured, and cheaply
measurable" (a lemma-set intersection against the 482,588-node spine, exactly the mandatory
vocabulary pre-check already built into section 6's falsifiable-prediction bands below). **Net
read, and this is the load-bearing interpretive point**: this coverage gap is not a blocker to the
near-term wiring plan — it is evidence the external store's PROPER role is background world-knowledge
that fills INFERENTIAL GAPS the text leaves implicit (an ATOMIC-style "if X wanted Y, they probably
did Z" default), not a replacement for text-derived content. The focus should keep extracting
story-specific content from the text itself (`event_bundle.py`/`coreference_resolver.py`); the
causal/associative store's job is only to supply the commonsense scaffolding AROUND what the text
states, which is exactly the architecture section 3's `pull_in()` design implements (a bounded,
tagged ADDITION to the focus, never a replacement for its text-derived contents).

## 6. Cheap decisive test

Vectorize the dense-core band of the already-landed CSKG spine (`kcore>=12`, 24,336 nodes,
avg-degree 39.18 — the smallest well-connected slice, per the already-measured k-core table in
`data/exp_cskg_foundation_v1/metrics.json`) into a real `KGStore` (or `HDFactStore`) instance. Build
the `pull_in()` hook (section 3) on `ChunkedFocus`. On a small set of hand-authored or DesireDB-slice
narrative snippets where a character's stated action has an ATOMIC/ConceptNet-coverable IMPLICIT
cause or effect that the text itself never states (e.g. "Nell had not eaten all day" -> implicit
`at:xWant`/`at:xEffect` = "eat"), query `pull_in()` with the focus's current entity/event atom and
check whether the recovered filler matches the CSKG-attested plausible inference. Compare against
TWO controls, reusing `exp_cskg_foundation_v1.py`'s OWN already-pre-registered can-fail-gate
methodology one level up (retrieval-into-focus accuracy, not just relation-label reconstruction):
(i) a RELATION-SHUFFLED store (same nodes/edges, relation labels permuted) and (ii) a FREQUENCY
baseline (always pull in the globally most-common effect/associate for that relation type,
regardless of the probe entity — per the prior-art note's own "must beat frequency, not just
chance" bar).

## 7. Falsifiable predictions

**Mandatory pre-check before accepting either band below** (per standing "flat result = broken
experiment, not a ceiling" discipline, and per section 5's own honest coverage-gap flag — this
pre-check is a REAL risk here, not boilerplate, given ATOMIC's closed event-template vocabulary):
confirm the probe snippets' entities actually canon()-match >= 50% coverage against the dense-core
node vocabulary FIRST. A flat result driven by near-zero vocabulary overlap between probe text and
the store's lemma set is a coverage/harness issue, not a mechanism verdict.

**HARD-PASS** (both required):
- `pull_in()` recovers the correct (or a CSKG-attested plausible) filler on >= 100 held-out probe
  events, beating the frequency baseline by >= 10 percentage points (same calibration bar the
  prior-art note set for its own chain-induction test, applied here for consistency across this
  program's two content-facing drills).
- Relation-shuffled-store accuracy degrades by >= 8 percentage points relative to the true-relation
  store (the pairscramble-must-collapse analog for this mechanism — confirms genuine
  relation-conditioned retrieval, not "any concept vaguely near the entity").

**HARD-FAIL** (either triggers, subject to the mandatory pre-check above):
- `pull_in()` accuracy is within 3 percentage points of the frequency baseline on >= 100 probes.
- Shuffled-relation accuracy is statistically indistinguishable from true-relation accuracy
  (relation-blind retrieval).

## 8. Cross-thread synthesis

**This is the CONTENT-sourcing pillar of a same-day 4-pillar drill program** (discovered on write,
not before dispatch — a KB-check-before-drilling gap this note flags against itself): three sibling
notes filed the SAME 2026-08-09, on the SAME `situation_focus.py`/pull-in/causal-inference question,
from three OTHER angles, all independently verified on read (not just title-matched) to be
non-duplicative: `notes/research_brain_focus4_simulation_inference_mechanics_2026-08-09.md`
(MECHANICS pillar — the exact 3-layer Ericsson-Kintsch/Oberauer/McElree retrieve-check-advance
architecture, P_deflated=0.44); `notes/research_brain_situation_model_simulation_pullin_causal_2026-08-09.md`
(BRAIN-SHAPE pillar — retrieval-and-recombine vs trained-forward-regression, converging with an
on-disk `MECHANISM_FALSIFIED` negative on trained SR-TD prediction, P_deflated=0.38);
`notes/research_substrate_design_focus_simulation_2026-08-09.md` (BUILD pillar — names
`CausalLinkRegister` sitting unused since 2026-08-02, `iterative_attractor` wired only into offline
cells not the live focus, and the `exp_mcscript2_script_chain_predict_gap_fill_v1` MIDDLE_BAND
negative on bare-BoW chaining with no role structure). This note is the fourth: WHAT causal/
associative content to source and HOW to represent+retrieve it, distinct from those three's WHY
(brain-shape), EXACTLY-HOW (mechanics), and WITH-WHICH-OWNED-ORGANS (build-sequencing) angles. The
build-pillar note's finding that `CausalLinkRegister` exists but is "not yet pointed at a real
content store" is the EXACT gap section 3 of this note closes: `CausalLinkRegister` is the retrieval
primitive, `hd_fact_store`/`kg_traversal` (this note, section 1) is the content it should be pointed
at, and the dtype reconciliation named in section 3 is the concrete blocker between them.

Directly answers the "grounded causal/intentional CONTENT" half of the standing USER reframe (the
state_of_mind bundle IS the situation-model representation; the gap is grounded content + a chaining
step, grown via a CLS/sleep acquisition loop, not batch-ingest). This drill supplies the CONTENT
half concretely (sections 1-2, both rated, one already on disk and gate-passed); the CHAINING half is
partially already built too — `KGStore.predict_n_hop`/`predict_two_hop` (CERT 585) is exactly a
causal-chain traversal primitive, and the prior-art note's section 1a/4 already named
`SequenceMatrix.chain_predict` (within-script scene order) and a "CausalLinkRegister-pattern"
(recursive goal-respawn chaining) as the two chaining mechanisms for the schema-bundle layer above
single causal links — this drill's `pull_in()` design is the missing CONNECTOR between that chaining
layer and the Cowan-4 focus, not a fourth new mechanism. Extends
`notes/research_prior_art_narrative_schema_learning_2026-08-09.md` (which rated ATOMIC/ConceptNet/
GLUCOSE/ASER/CausalBank for the SCHEMA-INDUCTION use case) by re-rating the causal subset
specifically for the FOCUS-RETRIEVAL use case and discovering the already-landed, already-gated CSKG
artifact that note did not surface (it was scoped to induction methods, not to auditing existing
data artifacts on disk). Extends `notes/research_script_half_synthesis_2026-08-09.md`'s recommendation
to "fuse ATOMIC xEffect for OOV/non-VerbNet verbs" by confirming that fusion source is not a future
sourcing task but an ALREADY-LANDED artifact needing only vectorization. Complements
`notes/research_psych_acquisition_consolidation_loop_2026-08-09.md`'s design (referenced directly by
`grounding_acquisition_loop.py`'s own docstring) by naming the concrete NEW keying domain (causal/
associative EDGES, not just outcome-verb lemmas) that engine should grow next, per section 4.

## 9. Substrate-product implications

If the section 6 test clears, the focus gains the ability to fill inferential gaps the text leaves
implicit — "why would this character do that" — from a store whose EVERY answer is traceable to a
specific source edge (unbind `SOURCE`/`TRUST` on any pulled-in item recovers "ATOMIC `at:xWant`,
TRUST_MID" or "self-acquired via the consolidation loop, TRUST_LOW-scaled-by-confidence"), with the
pulled-in content tagged distinctly from text-derived content so a user can always ask "did the text
say this or did the model infer it, and from where." This is categorically unavailable from any
LLM-based commonsense augmentation (COMET, ATOMIC-10X's generation pipeline, GPT-prompted
schema induction — all already confirmed reference-only in the prior-art note): those systems can be
asked to explain themselves but the explanation is itself a generated (possibly confabulated) text,
not a structural pointer to a specific stored edge. This extends the same auditability differentiator
already identified as the substrate's defensible edge (goal-achievement arc, schema-induction drill)
to the world-knowledge-grounding layer specifically — arguably the layer where an opaque system's
hallucination risk is highest (commonsense "facts" are exactly the kind of confident-sounding wrong
answer an LLM produces), making the auditability edge most valuable here.

## Calibration (per [[feedback-lit-scan-calibration-penalty]])

Two live Sonnet lit-scans completed this cycle (free-association norms; large-codebook cleanup
capacity), both incorporated above with explicit UNVERIFIED flags where a primary-source number
could not be independently confirmed (Plate/Frady-Kleyko-Sommer exact capacity formula; the specific
PMI-vs-free-association-probability correlation number; USF-vs-SWOW head-to-head coverage
comparison). This is a genuine mixed-regime bet: the DATA half (section 1, section 6's seed) is
essentially de-risked — it is already on disk and already independently HARD_PASS-gated by its own
pre-registered can-fail test, not a literature promise. The WIRING half (`pull_in()`, section 3) has
no direct precedent (situation_focus has never queried an external store; this exact composition —
Hebbian KG traversal probed FROM a bounded working-memory focus — was not found in the literature
scan either, a genuine novel-for-the-field combination, not just novel-for-us). **P(section 6 clears
its HARD-PASS bands) = 0.48** — raw estimate ~0.65 (both underlying pieces individually strong:
CERT 585's 36.49x margin, cskg_foundation_v1's own 0.696-vs-0.237 gate-pass gap), deflated per the
mandatory penalty for the untested NEW composition and the section-5-confirmed vocabulary-coverage
risk (ATOMIC's closed event-template set vs open narrative-snippet probes), capped at the
novel-synthesis ceiling of 0.50 minus a small margin for the mandatory-pre-check risk specifically.
The associative half (section 2) is less risky mechanically (BEAGLE is direct, verified precedent)
but has NOT been run as a can-fail test in this drill — no P estimate offered for it beyond the
data-rating table; that is a section-6-style test still to be designed, explicitly deferred rather
than guessed.

## 10. Recommended next build (ranked; folded into this deliverable per no-routing-files discipline)

1. **Cheapest, highest-confidence-precedent**: vectorize the already-landed CSKG dense-core band
   (24,336 nodes) into a real `KGStore`/`HDFactStore` instance. Zero new sourcing risk — the data is
   on disk, gate-passed, and the target schema (`hd_fact_store` field contract) was chosen for this
   exact purpose per the pre-reg.
2. **Second**: build the `pull_in()` hook on `ChunkedFocus` (section 3), resolving the
   bipolar-vs-complex64 reconciliation by porting `CausalLinkRegister`'s pattern onto bipolar vectors
   (section 3's recommendation (a)) so it can query the bipolar CSKG store directly rather than
   building a second causal-chaining mechanism; then run the section 6 cheap decisive test. This is
   the one genuinely untested composition in this whole plan — treat it with full calibration
   discipline (section 9's 0.48), not as a foregone conclusion just because its input pieces are each
   separately validated.
3. **Third, parallel/low-cost, zero new download**: re-run `exp_cskg_foundation_v1.py` with
   `RelatedTo` re-included (or a companion pass) as the associative seed; independent of (1)-(2).
4. **Fourth, if (1)-(2) clear**: layer SWOW-EN2018 (research-use-clear; flag the CC BY-NC-ND
   redistribution constraint before any external release) as the graded-strength associative
   enrichment on top of (3)'s raw `RelatedTo` seed; USF Nelson as the license-safer fallback.
5. **Fifth, only after (1)-(4) establish the store is worth growing**: re-point
   `grounding_acquisition_loop.py` at edge-level (causal/associative link) flagging alongside its
   existing verb-lemma flagging — reuse, not a new mechanism, per section 4's ordering discipline.
6. **Deferred, scale-up only if (1)-(5)'s coverage proves insufficient on real narrative text**:
   GLUCOSE (highest-priority scale-up, narrative-grounded unlike CSKG/ATOMIC's template grounding),
   then ASER, then CausalBank, in that order per the prior-art note's own ranking (reused, not
   re-derived).

## Citations (verified count = 2 completed live Sonnet lit-scans this cycle, 16 + 15 tool-uses
respectively; plus direct on-disk verification of 8 hdlab modules/artifacts and their measured
metrics.json/capability_registry.jsonl entries — not from-memory claims)

**Live-verified this cycle**: De Deyne, Navarro, Perfors, Brysbaert, Storms 2019, *Behavior Research
Methods* 51(3) 987-1006 (SWOW-EN2018); Nelson, McEvoy, Schreiber 2004, *Behavior Research Methods,
Instruments & Computers* 36(3) 402-407 (USF norms); Jones & Mewhort 2007, *Psychological Review*
114(1) 1-37 (BEAGLE); Mandera, Keuleers, Brysbaert 2015 (skip-gram vs co-occurrence on psycholinguistic
norms); Recchia & Louwerse 2015, *Journal of Cognition* (PPMI-weighted co-occurrence, affect norms —
adjacent not direct); Collins & Loftus 1975 (spreading activation theory); Anderson ACT-R
fan-effect/retrieval-threshold literature; Frady, Kleyko, Sommer et al. arXiv:2208.12880 / Renner et
al. resonator-network visual-scene factorization; Hersche et al. 2023/2024 arXiv:2303.13957
(block-code factorizers); Frady, Kleyko, Sommer 2018 *Neural Computation* (sequence-indexing/
working-memory capacity theory, cited not independently re-derived).

**On-disk verified this cycle (not from memory)**: `data/exp_cskg_foundation_v1/metrics.json`
(landed HARD_PASS run); `data/cskg_foundation_v1/nodes.jsonl` + `edges_shard_*.jsonl` (482,588 nodes
confirmed via `wc -l`); `preregs/2026-07-26_cskg_foundation_v1.md`; `data/grounding_testbed/
PROVENANCE_cskg.md` (Ilievski, Szekely, Zhang, "CSKG: The CommonSense Knowledge Graph," arXiv:2012.11490,
ESWC 2021); `hdlab/hd_fact_store.py`; `hdlab/kg_traversal.py` (CERT 585 numbers from its own module
docstring); `hdlab/situation_focus.py`; `hdlab/grounding_acquisition_loop.py`;
`hdlab/situation_model_accumulate.py`; `hdlab/binding.py`; `data/capability_registry.jsonl` (6 rows
inspected: `hd_fact_store`, `working_overlay_situation_reader`, `cskg_foundation_v1`, `kg_ingest`,
`sequence_binding`, `quality_relation_two_channel_opposition`).

Reused without re-verification this cycle (already live-verified in the cited prior notes):
ATOMIC (Sap et al. 2019 AAAI); ATOMIC-2020 (Hwang et al. 2021 AAAI); ConceptNet 5.5 (Speer, Chin,
Havasi 2017 AAAI); GLUCOSE (Mostafazadeh et al. 2020 EMNLP); ASER (Zhang et al. 2020 WWW,
arXiv:1905.00270); CausalBank (Li, Ding, Liu 2020 IJCAI) — all per
`notes/research_prior_art_narrative_schema_learning_2026-08-09.md` section 2.
