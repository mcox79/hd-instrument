# BRAIN-DRILL: FORK-C (compounding + end-to-end-in-substrate) — the integrated comprehension-memory
loop, what's LEARNED vs GIVEN in it, and the first buildable component

**Date:** 2026-07-19. **Filed by:** research (2 parallel Sonnet lit-scans — native-binding-acquisition /
predictive-coding; Zacks Event Segmentation Theory / hippocampal-boundary / indexing / prioritized-replay —
synthesized by director against three same-day sibling notes, NOT re-derived). **Trigger:** USER "A then C"
brain-drill-first directive for FORK-C: the integrated comprehend->structure->consolidate->use-as-prior loop,
AND how that loop is learned/improves, synthesized into a concrete C design + first buildable component +
design-gated can-fail. Brain-led; outcome NOT pre-assumed.

**Composes with, does not re-derive, three same-day notes (read, not re-run):**
`research_situation_model_guided_comprehension_loop_compress_and_carry_2026-07-19.md` (CCL: topical carry
HARD_FAILED both axes — hurts precision, and its apparent compounding was a generic order-effect artifact;
VET's own redirect: the carry must be STRUCTURED role/event binding, not topical, or it re-hits the wall);
`research_cross_document_compounding_consolidation_viability_2026-07-19.md` (cross-doc: real but 3-condition-
gated — correctness, decorrelated filter, threshold; cheap decisive test already run: coherence-gate
confidence-correctness correlation = 0.139, just under the 0.15 HARD-PASS bar = safe-but-sub-usable;
objecthood second-view candidate failed decorrelation = self-training-unsafe; redundancy second-view
candidate measures 0.244 correlation with correctness but its DECORRELATION-from-coherence-gate check
(Prediction B) is still untested); `vsa_core_ops_empirical_envelope_bind_bundle_unbind_2026-07-19.md`
(measured envelope: bind/unbind lossless O(N); bundle degrades gracefully to a real m~24-32/N=256 and
128/N=2048 ceiling; shard before saturation, cross-shard merge must be discrete list-merge, never joint
vector ops; 7 named GAPS including incremental bundling, repeated unbind, consolidation-over-time fidelity).

---

## HEADLINE

**The brain's integrated loop is real and well-documented across four convergent literatures already
catalogued in the sibling notes (Kintsch CI, van Dijk macrostructure, Zwaan/Gernsbacher discontinuity,
Ericsson-Kintsch LTWM) — this drill's two NEW angles sharpen exactly the two open questions FORK-C asked
about, and BOTH resolve in ways that were not assumed going in.**

**(1) On "how is binding kept structured, not a topical bag" and "does the brain learn to FORM structured
bindings natively" (the reader-forms-HD-natively candidate) — the honest literature answer is: NO clean
mechanism exists, anywhere, for a biologically-grounded system LEARNING the binding OPERATOR itself.**
Binding-by-synchrony (von der Malsburg) has a plasticity story for grouping already-active features, not
for acquiring a compositional role-filler operator. Every serious brain-level VSA/HRR/tensor-product/SPA
model (Smolensky, Plate, Eliasmith's Spaun) treats the binding algebra (circular convolution / phasor
multiplication / outer product) as a GIVEN, fixed operation and only learns the CONTENT vectors bound by it
— the one partial counterexample (Gosmann & Eliasmith's Vector-Derived Transformation Binding, 2019) learns
a *transformation applied via* binding, not the operator's existence. A 2025 preprint shows predictive-
objective training can make compositional structure emerge in RNNs, but has not been connected to role-
filler thematic binding specifically. **This is a genuine, load-bearing finding, not a search failure: it
means "the reader learns to form HD bindings natively" has no brain precedent to build toward, and — because
our own Stage-1 bridge already gives a lossless, zero-training FHRR encode of role-filler tuples
(bridge_fidelity_single=0.0) — there is no capability gap this thrust would close.** The honest
recommendation is to DEPRIORITIZE bridge-internalization as a build target and treat the FHRR bind/bundle/
unbind operator as GIVEN (matching both the best brain-model literature and our own already-validated
zero-training bridge), concentrating all "learning" at the content-selection / scoring / consolidation-
policy layer — which is exactly where the sibling LCCP/coherence-gate/consolidation-filter designs already
put it. This is the C-fork answer to drill-4, arrived at honestly rather than assumed.

**(2) On event-boundary detection and what/how consolidation happens — Zacks' Event Segmentation Theory and
hippocampal-boundary/indexing/replay-priority literature CONVERGE with, and sharpen, the sibling notes'
existing PE-triggered MAP/SHIFT + LTWM-cue design**, but with two honest caveats not previously flagged:
prediction-error-specifically (vs. generic contextual-discontinuity) as the boundary-detection mechanism is
an ACTIVE, not fully settled, debate in the current literature; and Mattar & Daw's gain x need prioritized-
replay account, while a strong, well-established RL/hippocampal result at the level of individual memories,
has NOT been demonstrated in the literature at event-segment granularity — extending it there is this
drill's own untested synthesis, not an imported finding.

**Ranked brain mechanism for FORK-C (name it): FIXED-OPERATOR, LEARNED-POLICY STRUCTURED COMPREHENSION-
CONSOLIDATION LOOP** — an unchanging compositional binding algebra (matches both biology's best formal models
and the substrate's own validated bridge) wrapped by a fully learned/tunable selection-scoring-consolidation
policy (cue-competition weights, coherence-gate score, redundancy-decorrelation filter, boundary-triggered
compression, gain x need consolidation priority) operating over a PE-gated MAP/SHIFT event-segmented carry
that compresses to sparse indexed pointers (not raw content) at each boundary. Deflated **P=0.30** for the
composed FORK-C design (composes four already-capped novel-synthesis components: WSM 0.40, coherence-gate
<=0.50, LCCP 0.35-0.45, cross-doc consolidation 0.22 — plus this drill's own two new, partially-untested
bridges: the Mattar-Daw event-granularity extension and the fixed-operator recommendation itself, which,
while well-supported as a NEGATIVE result for operator-learning, is a POSITIVE recommendation not yet built
or tested).

---

## Angle 1 — THE ONLINE MAP-BUILD (established, composes with sibling CCL note, not re-derived)

Kintsch's Construction-Integration (1988) generates an over-inclusive candidate set with no context-gating
at construction, then settles via a constraint-satisfaction network biased by the currently-active context;
van Dijk & Kintsch's macrorules (deletion/generalization/construction) compress settled microstructure into
a gist hierarchy; Zwaan/Gernsbacher's event-indexing/structure-building gives the MAP-(routine continuation,
cheap in-place fold) vs. SHIFT-(multi-dimension discontinuity, checkpoint-and-open-fresh) trigger; Ericsson &
Kintsch's Long-Term Working Memory (1995) explains how the carried state stays bounded — true active buffer
holds only the current cycle plus a small leading-edge carry, with durable extension via small retrieval
CUES/pointers into long-term store, not raw accretion. **All of this is already fully catalogued in the CCL
note (Angles 1 and 4) and is not re-derived here.** What this drill adds is the explicit FORK-C reading: this
online loop is the SAME machinery whether the carried structure lives as a symbolic proposition-connectivity
network (as in the human-comprehension literature) or as an FHRR bind/bundle map (the substrate's Stage-1
bridge target) — the mechanism-level claims (over-inclusive construction, context-biased settling, leading-
edge/macrorule compression, cue-addressable durable extension) are representation-agnostic, which is exactly
why the CCL note's design and this note's FHRR-native design can share one mechanism-level template while
differing only in what medium the carried structure is stored in.

**Citations (reused from CCL note, not re-verified again this session):** Kintsch 1988; Kintsch & van Dijk
1978; van Dijk & Kintsch 1983; Ericsson & Kintsch 1995; Zwaan, Langston & Graesser 1995; Gernsbacher 1990/1995.

---

## Angle 2 — WHAT IS "LEARNED" IN THE LOOP: the binding-operator-vs-content honesty check (NEW this drill)

**Mechanism (deflated per lit-scan calibration; confidence levels stated inline, not smoothed).**

Binding-by-synchrony (von der Malsburg & Schneider 1986; STDP-style plasticity precursor already in von der
Malsburg 1973) gives a genuine, medium-high-confidence account of how correlated firing GROUPS already-
active feature detectors into one bound percept — but this explains segregation/grouping of features, not
the acquisition of an abstract, reusable role-filler binding OPERATOR that can compose arbitrary new
role/filler pairs. Greff, van Steenkiste & Schmidhuber's 2020 survey ("On the Binding Problem in Artificial
Neural Networks," arXiv:2012.05208) names this gap explicitly across the modern connectionist literature.

Every serious formal brain-level hypothesis for compositional binding treats the operator as a GIVEN
mathematical primitive: Smolensky's tensor-product representations (1990, outer product), Plate's
Holographic Reduced Representations (1994/95, circular convolution), Eliasmith's Semantic Pointer
Architecture / Spaun (circular convolution as the default SPA bind operation, per the NengoSPA
documentation) — content vectors are learned/optimized (via NEF-style decoders in SPA's case), the binding
ALGEBRA is not. The single partial counterexample located, Gosmann & Eliasmith's Vector-Derived
Transformation Binding (*Neural Computation*, 2019), pairs a supervised rule with a spiking BCM-like
unsupervised rule to LEARN A TRANSFORMATION applied via binding — this is the closest the literature gets to
"binding is learned," and even there the operator's existence/algebra is assumed, only the specific mapping
is acquired. Confidence: **high** that this asymmetry (content learned, operator given) accurately
characterizes the current state of brain-model VSA literature.

A 2025 bioRxiv preprint ("Predictive learning enables compositional representations") shows RNNs trained
purely on next-observation prediction spontaneously develop modular, recombinable structure with no
hand-specified binding operator — the most direct evidence found that predictive-coding-style error-driven
learning CAN acquire compositional structure from scratch. Confidence: **medium** — single recent preprint,
not yet independently replicated as far as this scan found, on RNNs not spiking/biological models, and not
demonstrated for role-filler thematic binding specifically (the exact case FORK-C needs).

Developmental literature (Halford's relational-complexity theory: 2-relation integration rises from ~20%
at age 4 to ~57% at age 6; Gentner's relational-shift work: children move from feature-similarity to
genuine structural/relational matching with age and relational-vocabulary exposure) shows relational-binding
CAPACITY clearly increases with experience — but this is standardly framed as growing processing
resources/capacity, not as literally acquiring the binding mechanism via a plasticity rule comparable to
STDP. Confidence: **medium-high** on the phenomenon, **low** on it answering the operator-acquisition
question directly.

**Honest gap, stated plainly (this is the drill's main deliverable for Angle 2):** no literature found gives
a clean, unified, biologically-grounded account of the binding OPERATOR ITSELF (as distinct from its
content, or from downstream capacity/resource growth) being learned from scratch. This is a real gap in the
cognitive-science/computational-neuroscience literature, not a failure of this search.

**Implication for FORK-C (the load-bearing design decision this angle contributes):** because (a) no brain
precedent exists for learning the binding operator, and (b) the substrate's own Stage-1 bridge already gives
a validated, zero-training, lossless FHRR encode of role-filler tuples, the "reader-forms-HD-natively
bridge-internalization" candidate is not solving an open capability gap — it would be reinventing, via a
speculative and unprecedented learning mechanism, something the substrate can already do exactly by
construction. **Recommendation: keep the FHRR bind/bundle/unbind operator FIXED (as given); put all of
FORK-C's "learning" at the selection/scoring/consolidation-policy layer.** This is a genuine brain-check
outcome not assumed going in — the task explicitly asked not to pre-judge this, and the honest literature
answer redirects away from the naively-attractive "learn everything end to end" framing toward a more
precisely-scoped "learn the policy, not the algebra" framing, which happens to match this arc's already-built
components (LCCP cue-weights are learned; coherence-gate scoring is learned; the FHRR bind operation itself
is not and does not need to be).

**Citations:** von der Malsburg & Schneider (1986); von der Malsburg (1973, precursor plasticity account);
Scholarpedia "Binding by synchrony"; Greff, van Steenkiste & Schmidhuber (2020, arXiv:2012.05208); Smolensky
(1990, tensor-product representations); Plate (1994/95, Holographic Reduced Representations); Eliasmith
(Spaun / Semantic Pointer Architecture, NengoSPA docs); Gosmann & Eliasmith (2019, *Neural Computation*,
Vector-Derived Transformation Binding); a 2025 bioRxiv preprint, "Predictive learning enables compositional
representations" (not independently replicated, flagged); Halford (relational complexity theory); Gentner
et al. (1995, relational-similarity development; 2011, *Child Development*).

---

## Angle 3 — CONSOLIDATION: event boundaries, hippocampal indexing, and replay priority (NEW this drill,
sharpens but does not contradict the 07-18 Tse/McClelland-CLS note and the sibling CCL/cross-doc notes)

**Mechanism.** Zacks & Swallow's Event Segmentation Theory (Zacks, Speer, Swallow, Braver & Reynolds 2007,
*Psychological Bulletin*; Zacks & Swallow 2007, *Current Directions in Psychological Science*) formalizes
exactly the MAP-vs-SHIFT trigger the sibling notes already wire to the ingest-gate's PE/unexpectedness
signal: a maintained "event model" generates ongoing predictions; a transient prediction-error spike flags
the model stale and triggers an update/replacement, experienced as a segmentation boundary; interior-of-event
stability (not continuous rebuilding) is explicit and load-bearing in the theory (Zacks et al. 2011's
computational model of PE-driven segmentation matches human boundary placement). Confidence: **medium-high**
on the theory's core mechanism and its broad citation base. **Honest caveat (new this drill, not previously
flagged in the sibling notes):** whether prediction-error SPECIFICALLY (vs. a more generic contextual-
discontinuity-detection account) is the necessary mechanism is an ACTIVE, unresolved debate — a Columbia-lab
paper ("Generating event boundaries in memory without prediction error") and a 2025 *Psychonomic Bulletin &
Review* paper argue boundaries can arise from contextual-stability shifts without an explicit PE computation.
Confidence: **medium**, not high, that PE-specifically (rather than a broader discontinuity metric) is the
uniquely correct formalization — this doesn't change the sibling notes' MAP/SHIFT design (PE/unexpectedness
is still the dominant, best-cited account and the substrate's own ingest-gate signal already exists and is
VET'd) but tempers confidence that this is the ONLY correct trigger formalization, worth flagging honestly.

Separately, and with stronger empirical support: hippocampal activity shows a robust, well-replicated
boundary-locked surge (Ben-Yakov & Dudai 2011; Ben-Yakov, Dudai & Mayseless 2013; Ben-Yakov & Henson's
"Hippocampal Film Editor," 2018, *J. Neurosci*; Baldassano et al. 2017 and Chen et al. 2017's neural
event-segmentation work), scaling with boundary salience and predicting subsequent recall — direct,
convergent evidence that boundaries specifically are WHEN durable encoding/consolidation is registered, not
merely when perception updates. Confidence: **high** — this is the best-replicated of the four sub-threads
this drill scanned.

Teyler & DiScenna's hippocampal indexing theory (1986, updated 2007) holds that what the hippocampus stores
at these moments is a sparse POINTER/INDEX into distributed cortical activity, not the content itself —
retrieval is index-triggered cortical pattern completion. This composes with, and is broadly treated as
complementary to (not competing with), standard Complementary Learning Systems (McClelland/McNaughton/
O'Reilly 1995, already the primary citation in the 07-18 sibling note) — CLS explains WHY a fast sparse
system is needed (avoiding catastrophic interference in overlapping distributed cortical codes); indexing
theory specifies WHAT FORM the fast trace takes (a pointer, not a full copy). Confidence: **high** on
indexing theory as a standard framework; **medium** that its formal composition with CLS's learning-rate
dynamics is literature-demonstrated rather than a reasonable, widely-assumed inference — I found no paper
that rigorously integrates the two into one model.

Mattar & Daw's (2018, *Nature Neuroscience*) gain-x-need account of hippocampal replay prioritization is a
strong, well-established result at the level of individual memories/states: replay priority = gain (value of
updating that state) x need (successor-representation-weighted expected future relevance) — not a flat or
uniform consolidation schedule. Confidence: **high** on the core result. **Honest gap (new this drill):** no
paper was found that reformulates gain x need at the granularity of whole EVENT SEGMENTS (as opposed to
individual states/memories) — extending it to "which structured event-chunks get consolidated first" is this
drill's OWN untested bridge, not a documented finding. Confidence: **low** on this specific extension.

**Implication for FORK-C.** The PE-triggered MAP/SHIFT + LTWM-cue design already specified in the sibling
CCL note is independently reinforced by a FOURTH and FIFTH distinct literature (event-segmentation/
hippocampal-boundary neuroscience; hippocampal-indexing theory) — this is the SEVENTH time across this
arc's notes that the same architectural shape (graded/situation-conditioned processing, compress-to-pointer
at a detected discontinuity, cheap-buffer-first with costly-reinstatement-on-demand) has been independently
re-derived from a different source literature, further reinforcing it as a real convergent principle rather
than a citation-selection artifact. The two NEW, actionable refinements this angle contributes: (1) an
honest tempering of confidence in PE-specifically as the boundary trigger (worth a footnote in the eventual
build, not a design change — the substrate's PE/unexpectedness signal remains the best available, already-
built, already-VET'd option); (2) a genuinely new, principled candidate for RANKING which structured
tuples get promoted to Tier-3 first when consolidation capacity is limited — Mattar-Daw's gain x need,
reframed at the tuple/event-chunk level as (gain = how surprising+important the tuple was, reusing the
already-established "surprise = unexpectedness x importance" ingest signal) x (need = how likely the
tuple is to be queried again, reusable via the cross-doc note's still-untested REDUNDANCY signal — same-
document corroboration count as a proxy for future relevance) — this is a genuinely new synthesis, capped
P<=0.50, not an imported finding, but it gives a principled alternative to a flat consolidation threshold
that composes directly with machinery already on the substrate (the ingest-gate's surprise decomposition,
the cross-doc note's redundancy candidate).

**Citations:** Zacks, Speer, Swallow, Braver & Reynolds (2007, *Psychological Bulletin*); Zacks & Swallow
(2007, *Current Directions in Psychological Science*); Zacks et al. (2011, computational model of PE-driven
segmentation); a Columbia-lab counter-paper, "Generating event boundaries in memory without prediction
error"; a 2025 *Psychonomic Bulletin & Review* paper on contextual-stability vs. PE; Ben-Yakov & Dudai
(2011); Ben-Yakov, Dudai & Mayseless (2013); Ben-Yakov & Henson (2018, *J. Neurosci*, "Hippocampal Film
Editor"); Baldassano et al. (2017); Chen et al. (2017); a 2019 *J. Neurosci* paper on rapid memory
reactivation at movie event boundaries; Teyler & DiScenna (1986, hippocampal indexing theory; 2007 update);
McClelland, McNaughton & O'Reilly (1995, CLS, already cited in the 07-18 sibling note); Mattar & Daw (2018,
*Nature Neuroscience*, gain x need prioritized replay).

---

## Angle 4 — KNOWLEDGE-GUIDED COMPREHENSION AND ITS HONEST BOUND (established, composes with cross-doc
note, not re-derived)

Bransford & Johnson (1972): a relevant schema must be active DURING encoding, not merely available at
retrieval, to raise comprehension. Stanovich's Matthew effect (1986): a reciprocal cross-session
knowledge-comprehension loop, developmental-grain, empirically mixed support for the fan-spread pattern.
Kendeou & van den Broek (2005/2007): ERRONEOUS prior knowledge actively HURTS subsequent comprehension
relative to no-knowledge — the decisive reason consolidation must FILTER, not accumulate unconditionally.
O'Reilly, Wang & Sabatini (2019, n=3,534): a measured background-knowledge THRESHOLD (~59% correct) below
which knowledge and comprehension are uncorrelated. **All fully catalogued in the cross-doc sibling note,
not re-derived here.** This drill's only addition: the co-training/self-training decorrelation requirement
(also already established in the cross-doc note) is the SAME structural concern as this drill's own Angle-3
finding about Mattar-Daw's gain x need needing a genuinely independent NEED signal (redundancy, not a
feature derived from the same coherence-gate family) — reinforcing that whichever ranking/filtering
mechanism FORK-C uses for consolidation-eligibility, it must be checked for decorrelation from the
extractor's own error mode before being trusted, a requirement that recurs across both literatures
(comprehension-consolidation and ML self-training theory) independently.

---

## Angle 5 — STRUCTURAL VERDICT + THE FORK-C LOOP DESIGN

**Ranked brain mechanism, restated:** FIXED-OPERATOR, LEARNED-POLICY STRUCTURED COMPREHENSION-CONSOLIDATION
LOOP. The binding algebra (FHRR bind/bundle/unbind) is GIVEN, matching both biology's best formal models and
the substrate's own already-validated, zero-training Stage-1 bridge. Everything "learned" lives in the
policy wrapped around it: which candidate role-fillers to construct (LCCP, unchanged), how to score them
against local + document-scope + cross-document context (coherence gate + CCL's untested structured
document-coherence feature), when to checkpoint/compress (PE-triggered MAP/SHIFT, tempered-confidence per
Angle 3), what to keep vs. discard at a checkpoint (macrorule-style compression to LTWM/hippocampal-index-
style cue pointers, not raw content), and what to consolidate first when capacity is limited (gain x need,
this drill's new but capped-P bridge).

### The C representation, concretely

**The SAME live-accumulating FHRR hypervector map is the carried structure at every scale** — this directly
answers the USER framing (sentences=reasoning-maps; C's representation = the same FHRR hypervector, bind +
bundle + unbind, as a live accumulating map): a Tier-2 "current event" bundle built by binding each clause's
role-fillers and bundling across clauses within the current PE-detected event segment; at a SHIFT boundary,
macrorule-compress (keep only redundancy/schema-fit-corroborated role-fillers per the cross-doc note's
double-filter) and commit the compressed result as a small set of Tier-3 retrieval CUES (hippocampal-index-
style pointers, not the raw bundle) into the durable, cross-document Frontier-2 foundation. Both the
within-document Tier-2 carry and the cross-document Tier-3 consolidation target are the SAME representation
class (FHRR bind/bundle), differing only in scope and compression level — this is the structural answer to
why FORK-C is one loop, not two separate mechanisms bolted together.

**Sharding discipline (per the measured envelope):** the Tier-2 bundle is capped well inside the measured
~24-32/N=256 or 128/N=2048 bundled-relation ceiling; at a SHIFT boundary the bundle is not merely compressed
but effectively SHARDED into a fresh Tier-2 bundle for the new event, with the just-closed bundle's compressed
cues committed to Tier-3 — this IS the envelope note's "shard before the bundle saturates" discipline,
applied at the natural PE-detected discontinuity points rather than an arbitrary capacity trigger. Cross-shard
(cross-event, cross-document) merges at query time must be discrete list/score merges over independently
decoded candidates, never a joint vector operation — both on-substrate attempts at joint cross-shard vector
ops have HARD_FAILED (per the envelope note).

### The FIRST buildable component

Two candidates remain live after this drill (reader-forms-HD-natively is explicitly DEPRIORITIZED per Angle
2's brain-check). Recommend building **in this order, both cheap, sequenced not parallel-blocking:**

**Step 0 (do first, near-zero-cost, already half-run):** compute the redundancy-signal decorrelation check
(the cross-doc note's own Prediction B) on existing eval data — whether the redundancy/cross-mention-
corroboration signal's errors are measurably LESS correlated with the coherence gate's own errors than the
coherence gate is with itself. This is the single cheapest, most decisive unblocking test on the table:
coherence-gate-alone confidence is already measured at 0.139 (borderline-below the 0.15 HARD-PASS bar,
Prediction A) and objecthood already failed decorrelation (self-training-unsafe); redundancy's raw
correlation with correctness (0.244) clears Prediction A's bar on its own, but its DECORRELATION from the
coherence gate — the actual requirement — is the one still-open, cheap, zero-new-compute check. This gates
whether ANY cross-document consolidation (the compounding payoff) is safe to build at all, independent of
which representation format (topical, symbolic, or FHRR-structured) is used to carry it.

**Step 1 (the actual first BUILD, valuable regardless of Step 0's outcome):** build the **structured
within-document role/event FHRR carry** — the CCL note's own explicitly-named non-closed, untested variant.
Concretely: replace CCL's HARD-FAILED topical-centroid Step-2b feature with a literal FHRR bind(role_i,
filler_i) + bundle-across-clauses Tier-2 map (using the Stage-1 bridge's already-validated, zero-training
encode), PE-triggered MAP (fold new clause into current bundle) vs. SHIFT (macrorule-compress + commit
compressed cues to Tier-3, per Angle 3's hippocampal-indexing-style discipline), scored into the LCCP's
existing Step-3 linear scorer as one more weighted feature (per CCL's own Angle-2 finding: integrated in
parallel, not a late rerank). This is valuable independent of Step 0 because it is the actual REPRESENTATION
that would ALSO need to exist for cross-document consolidation to have anything structured to consolidate —
building it now de-risks both threads with one artifact, and it directly exercises 3 of the envelope note's
named GAPS (incremental/streaming bundling as the document is read one clause at a time; repeated unbind
against the same live, evolving bundle; consolidation-over-time fidelity as bundles are checkpointed and
moved to Tier-3) that no cell on disk has yet tested.

---

## Cheap decisive test

**Step 0** (described above) is genuinely free — a correlation computation on already-collected eval data,
zero new compute, already partially run (coherence-gate and objecthood done; redundancy's raw correlation
done; only the redundancy-vs-coherence-gate decorrelation number is missing).

**Step 1's** cheap decisive test reuses the CCL note's ALREADY-SPECIFIED harness (same held-out (verb,
construction) split, same document-position-binned instrumentation, same 3-arm structure) with ONE
substitution: Arm 3 (previously "topical + compression") becomes "FHRR structured bind/bundle + PE-triggered
MAP/SHIFT compression," using the Stage-1 bridge's existing encode/decode primitives — zero new
infrastructure beyond wiring the bridge's already-validated encode call into the existing harness's Step 2b
hook point.

---

## Falsifiable predictions — HARD-PASS / HARD-FAIL

**Prediction 1 (precision raise on the targeted failure class, structured-FHRR feature vs. sentence-local
baseline).** P=0.30 (deflated; composes four already-capped novel-synthesis components, same order as the
CCL note's own Prediction 1, but now testing the STRUCTURED variant CCL itself flagged as untested rather
than the already-refuted topical variant). HARD-PASS: on the CCL note's curated within-frame-coherent-but-
document-incoherent mis-attachment subset, the FHRR-structured Arm 3 reduces the FP rate by >=15 points vs.
the LCCP sentence-local-only baseline (Arm 1), replicating CCL's own bar. HARD-FAIL: <5-point reduction —
would mean even a STRUCTURED (non-topical) situation-model signal is too weak/noisy relative to local cue
features in the LCCP's Step-3 competition; the honest fallback is the same one CCL already named (a small
spot-checked gold seed set as an auxiliary signal, rather than any purely-derived situation-model coherence
feature).

**Prediction 2 (compounding, with the CCL-lesson bar raised, not just "positive slope").** P=0.20 (deflated
BELOW the CCL note's own Prediction 2 of 0.25, because CCL's own arm-A control already demonstrated that a
naive positive slope is insufficient evidence — order effects alone produced +0.189 — so this drill's bar is
explicitly harder). HARD-PASS: Arm 3 (FHRR-structured carry) shows a document-position slope that beats
CCL's own already-measured arm-A order-effect-only slope (+0.189) by a real margin (not merely nominally
positive), replicating the arm-A control from the SAME harness run alongside it. HARD-FAIL: Arm 3's slope
does not clear the +0.189 order-effect floor — meaning the within-document compounding claim fails a SECOND
time even with a genuinely structured (non-topical) carry, which would be a strong, informative negative:
within-document compounding via ANY currently-available carry mechanism is not supported, and further
investment should move fully to the cross-document consolidation thread (gated by Step 0 above) rather than
retrying within-document variants.

**Prediction 3 (compression specifically, not just "having a structured carry," drives any compounding
found — isolates the compression mechanism, same dissociation design as CCL's own Prediction 3).** P=0.25
(deflated). Arm 2 = FHRR structured feature WITHOUT PE-triggered compression (bundle accretes flat/
uncompressed until a hard truncation); Arm 3 = full PE-triggered MAP/SHIFT compression + Tier-3 cue commit.
HARD-PASS: Arm 3 beats Arm 2 specifically on LONG documents (where the uncompressed bundle approaches/
exceeds the measured 24-32/N=256 or 128/N=2048 ceiling), with Arm 2 ~= Arm 3 on short documents. HARD-FAIL:
Arm 2 and Arm 3 perform identically regardless of length — the compression machinery is not load-bearing
(a cruder "any structured carry" design might still work, a separate, less interesting finding); this would
also mean the envelope note's GAP 1 (incremental bundling) and GAP 3 (consolidation-over-time fidelity) are
not yet biting at the tested document lengths, worth re-testing at longer lengths before concluding
compression is unnecessary.

---

## FAIR can-fail test (full specification, Step 1)

**Real baseline:** the LCCP exactly as pre-registered (Arm 1, sentence-local only) — unchanged from CCL.

**Can-fail (both directions):** an over-weighted FHRR structured-coherence feature can suppress a TRUE
candidate representing a legitimate scene-change (same risk CCL already flagged for its topical version, now
tested on the structured version); an under-compressed or mistimed MAP/SHIFT checkpoint could let stale
Tier-2 content bias scoring after a real scene change (the false-continuity error, same failure class CCL
named, now on FHRR bundles specifically, which adds the NEW risk that renormalization/rounding drift across
many incremental FHRR adds could itself degrade fidelity in ways a symbolic bag-of-features carry cannot —
this is exactly the envelope note's GAP 1, untested anywhere on disk, and this cell is the first direct test
of it).

**One variable per arm (reused structure from CCL, ONE substitution):**
- Arm 1: LCCP baseline, sentence-local only (unchanged).
- Arm 2: + FHRR structured bind/bundle feature, no compression/checkpointing (isolates the structured-
  situation-model feature alone, and directly tests envelope GAP 1: incremental/streaming bundle-add
  without any compression discipline, the harshest test of accumulation drift).
- Arm 3: + PE-triggered MAP/SHIFT compression and Tier-3 LTWM-cue carry (isolates the compress-and-carry
  discipline specifically, and directly tests envelope GAP 3: consolidation-over-time fidelity across
  repeated checkpoint events).

**Held-out and measurement:** identical to the CCL note's specification (reused verbatim) — (verb,
construction) split crossed with a multi-scene document corpus carrying independent human-placed scene-
boundary labels; report precision/recall on the curated failure-class subset specifically (not overall,
since a gain there could mask a loss elsewhere); the document-position-binned learning curve required for
Prediction 2; MAP-vs-SHIFT trigger agreement with human-placed boundaries (informs whether Prediction 3's
dissociation is even measurable, and gives a live, cheap read on Angle 3's PE-vs-generic-discontinuity
honesty caveat — if trigger agreement is poor, that is itself evidence toward the "PE alone is not the
whole boundary-detection story" literature debate flagged above, worth reporting either way).

---

## Brain-check (outcome NOT pre-assumed — stated explicitly per task requirement)

**The integrated online-map-build -> consolidate -> use-as-prior loop is a real, well-established brain
capability** (Kintsch CI, Zwaan/Gernsbacher event models, Ericsson-Kintsch LTWM, Stanovich's Matthew effect,
Zacks EST, hippocampal-boundary encoding, Teyler-DiScenna indexing, Mattar-Daw prioritized replay) — this is
not a case of the brain lacking the loop, and every piece of it composes cleanly with what the sibling notes
already designed.

**Where the brain-check reveals a genuine SAME-LIMIT bound (accept, don't chase past it):** the carry-
forward bound is *relocated onto small cues*, never lifted (Ericsson-Kintsch LTWM; Teyler-DiScenna
indexing) — our own Tier-2 bundle is subject to the same measured N/log(N)-scaled crosstalk ceiling; there is
no free substrate-native escape from bounded working capacity, only faster/more-precise compression at the
boundary (a plausible substrate-native edge over biological schema-compression, untested).

**Where the brain-check redirects the design AWAY from a naively-attractive thrust (the genuinely open
question this drill was asked to resolve, not pre-assumed):** "learn to form HD bindings natively" has NO
brain-model precedent — every serious formal hypothesis for compositional binding in the brain-modeling
literature (synchrony, VSA/HRR/SPA, tensor-product) treats the binding operator as given and learns only
content or, in one recent case, a transformation applied via it. Because the substrate's own Stage-1 bridge
already supplies a validated, zero-training, lossless version of exactly this operator, there is no capability
gap here to close by learning it — attempting to would be chasing an unprecedented mechanism to solve an
already-solved problem. This redirects FORK-C's learning effort entirely toward the selection/scoring/
consolidation POLICY layer, which is both where the sibling notes already put it and where the brain's own
literature places all of ITS learning too (cue-weight tuning, schema-fit scoring, replay prioritization) —
a genuine convergence, not a coincidence of design choice.

**Where a literature debate remains genuinely open (flag, don't resolve by fiat):** PE-specifically (vs. a
broader contextual-discontinuity account) as the boundary-detection mechanism is actively contested; Mattar-
Daw's gain x need has not been extended to event-segment granularity in the literature — both are honestly
flagged above as this drill's OWN untested bridges, not imported findings, and both are cheaply checkable
inside the Step-1 FAIR test's own instrumentation (trigger-agreement metric; gain x need as an optional
consolidation-ranking ablation, not required for the core HARD-PASS/HARD-FAIL calls above).

---

## Cross-thread synthesis

This drill sits directly on top of, and resolves two of the open questions explicitly left by, the same-day
CCL and cross-doc notes: CCL's own text names "the STRUCTURED within-doc role/event carry" as the "NON-
CLOSED, UNTESTED variant" after topical carry HARD-FAILED — this drill supplies the concrete representation
(FHRR bind/bundle via the already-validated Stage-1 bridge) and reuses CCL's own harness/arm structure with
one substitution, rather than re-deriving a new test design. The cross-doc note's own Angle-4 decisive fact
(coherence-gate confidence 0.139, objecthood self-training-unsafe, redundancy 0.244-but-undecorrelated) is
carried forward as this drill's Step 0 — the single cheapest, most consequential open action item on the
whole arc, gating whether the compounding payoff (cross-document consolidation) is buildable at all
independent of representation format. The envelope note's 7 named GAPS are mapped explicitly onto this
drill's proposed FAIR test (Arms 2/3 directly exercise GAPs 1 and 3; the reader-noise and N-scaling GAPs
remain open for a later drill). This drill's own two new contributions — the binding-operator-vs-content
honesty finding (Angle 2, a genuine redirect away from a previously-open candidate) and the Mattar-Daw
gain x need consolidation-ranking bridge (Angle 3, a new but capped-P refinement) — are additive to, not
replacements for, the sibling notes' designs.

## Substrate-product implications

Not a publication angle — a build-priority and honesty angle. If Step 0 shows redundancy is genuinely
decorrelated from the coherence gate (clears Prediction B), that is the single cheapest green light this
whole arc has produced — it unblocks the cross-document consolidation build (the bigger compounding payoff)
at near-zero cost, before any new representation work is needed. If Step 1's Prediction 1 HARD-PASSes, the
product gains the same document-level-consistency claim CCL already targeted, now on a representation
(FHRR structured bind/bundle) that is inspectable at the vector level (every committed Tier-3 cue traces to
a specific role-filler binding, not an opaque topical score) — a stronger auditability story than a topical
centroid could ever support, independent of whether compounding (Prediction 2) also lands. If Prediction 2
HARD-FAILs even for the structured variant (a real, non-strawman possible outcome per its own bar), the
honest product fallback is: within-document compounding is not supported by ANY carry mechanism tried so far,
and the "gets better as it reads" story should rest entirely on the cross-document/consolidation thread
(gated by Step 0) rather than a within-document claim. If Angle 2's operator-vs-policy redirect is taken
seriously (recommended), the product gets a cleaner, more honest architecture story: "the substrate's core
binding operation is a fixed, mathematically-verified primitive (zero training, lossless); everything that
IMPROVES with experience is the policy around it" — a more defensible, more inspectable claim than "the whole
thing learns end to end," and one that matches the best available brain-model literature rather than
overreaching past it.

## Calibration reasoning

Raw confidence in the DIRECT CITATIONS is high (~0.55-0.75) for established components across both new
lit-scan lanes: binding-by-synchrony's plasticity account, the VSA/HRR/SPA operator-vs-content asymmetry
(the single most load-bearing NEW claim, cross-checked as a "high confidence this characterization is
accurate" by the lit-scan), Zacks EST's core PE-driven mechanism, the hippocampal-boundary-encoding
literature (the best-replicated of the four Angle-3 sub-threads), Teyler-DiScenna indexing theory, and
Mattar-Daw's core gain x need result. Two things are honestly flagged as MEDIUM/contested rather than
settled: PE-specifically-vs-generic-discontinuity as the boundary trigger (active debate, both sides cited),
and the CLS/indexing-theory formal composition (widely assumed, not rigorously co-modeled in a paper found
this session). Two things are this drill's OWN NEW, capped-P<=0.50 synthesis, not imported findings: the
recommendation to keep the binding operator fixed and route all learning to the policy layer (well-supported
as a NEGATIVE finding about operator-learning, but a novel POSITIVE architectural recommendation, untested
until Step 1 is built); and the Mattar-Daw event-granularity consolidation-ranking bridge (explicitly flagged
LOW confidence by the lit-scan itself, no literature precedent at that granularity). Composing across the
four already-capped sibling-note components (WSM 0.40, coherence-gate <=0.50, LCCP 0.35-0.45, cross-doc
0.22) plus these two new bridges, the overall FORK-C design sits at **P_deflated = 0.30**, with individual
predictions at **P=0.30 / 0.20 / 0.25** for Predictions 1/2/3 (Prediction 2 deflated below even CCL's own
already-low 0.25, because the bar is now explicitly "beat a known +0.189 order-effect floor," not merely
"positive slope" — a harder, more honest bar given what CCL already taught us).

## Citations (verified count)

**2 parallel Sonnet lit-scan lanes this drill, ~26 distinct external primary/secondary sources** (several
flagged inline as single-preprint, secondary-sourced, or contested rather than settled — not suppressed):
von der Malsburg & Schneider (1986); von der Malsburg (1973); Scholarpedia "Binding by synchrony"; Greff,
van Steenkiste & Schmidhuber (2020, arXiv:2012.05208); Smolensky (1990); Plate (1994/95); Eliasmith/NengoSPA
docs (Spaun/SPA); Gosmann & Eliasmith (2019, *Neural Computation*); a 2025 bioRxiv preprint on predictive
learning and compositional representations; Halford (relational complexity theory); Gentner et al.
(1995; 2011 *Child Development*); Zacks, Speer, Swallow, Braver & Reynolds (2007, *Psychological Bulletin*);
Zacks & Swallow (2007, *Current Directions in Psychological Science*); Zacks et al. (2011); a Columbia-lab
counter-paper on event boundaries without prediction error; a 2025 *Psychonomic Bulletin & Review* paper;
Ben-Yakov & Dudai (2011); Ben-Yakov, Dudai & Mayseless (2013); Ben-Yakov & Henson (2018, *J. Neurosci*);
Baldassano et al. (2017); Chen et al. (2017); a 2019 *J. Neurosci* memory-reactivation-at-boundaries paper;
Teyler & DiScenna (1986; 2007 update); Mattar & Daw (2018, *Nature Neuroscience*). Combined with the ~30 +
~30 = ~60 sources already cited across the two same-day sibling notes (CCL, cross-doc) and the ~25+ from the
07-18 consolidation note, this drill's total evidentiary base for the FORK-C thread is **~110+ distinct
sources** across the full comprehension/consolidation/binding literature.

---

## Status

Written per research-agent contract. USER-locked discipline applied: **no `exp_dev_handoff_*.md` or
`strategy_request_to_*.md` routing files written** (ferry mechanism deprecated per current session
instructions) — every actionable pointer is inline above (Angle 5's concrete C representation + sequenced
Step 0/Step 1 build order, cheap decisive test, FAIR can-fail test with arms/thresholds, cross-thread
synthesis pointing at exactly which sibling-note open questions this resolves). No cap_map or strategy files
modified. No atoms banked (research/synthesis drill only, per task contract).
