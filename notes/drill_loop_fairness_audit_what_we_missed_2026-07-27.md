# Drill: self-learning loop (v1/v2/v3) fairness audit — was it fair, what did we miss (2026-07-27)

## HEADLINE
The loop (v1/v2/v3) was never a fair test of comprehension-learning. It is a fair, honestly-measured test
of a *different, narrower* claim: "does repeated exposure that mean-pools a frozen encoder's per-sentence
embeddings and averages them into a per-concept vector nudge that vector toward its true relational
neighbour." The answer to THAT question is a real, leak-proof, modest yes (+0.024 on the LOW-exposure
slice). But every element that would make it a comprehension test — a structured extraction pathway, a
content-discriminating control, a plasticity channel beyond pooling arithmetic, and a metric that rewards
the SPECIFIC relation taught rather than any generic drift toward the graph-truth neighbourhood — is
either absent or too weak. Biggest single finding: **`hdlab/situation_reader.py` (the module that actually
extracts subject-relation-object structure) is never imported by any of the four loop cells.** The loop's
own docstring calls the frozen encoder's mean-pooled embedding "the comprehension/extraction engine" — that
label is the root of the over-read. There is no extraction anywhere in this pipeline; there is pooling.

## Cheap decisive test (falls out of the audit — see section 3)
Re-run the SAME LOW-exposure slice, SAME leak-proof relational-neighbour probe, but add ONE new arm:
`STRUCTURED_EXTRACT` — for each mention sentence, call `SituationReader`-style role extraction (predicate +
agent + patient; the codebase already has this banked, e.g. `_assign_roles` / `EventBundleCodec` in
`hdlab/situation_reader.py`, `hdlab/event_bundle.py`) and write the extracted (concept, relation, filler)
triple into a structured per-concept fact slot (reuse `ChunkedFocus`/`EventBundleCodec` role-query
unbind), IN ADDITION to (not instead of) the existing pooled-mean arm. Compare against a
`CONTENT_SWAP` control (see below) instead of `SCRAMBLED`. If `STRUCTURED_EXTRACT` shows a gain that
`CONTENT_SWAP` does NOT reproduce, that is the first honest evidence of comprehension-driven learning in
this codebase's loop family. This is a half-day cell, not a new research program — every component
(reader, codec, focus, MDL gate) is already banked; the missing piece is WIRING them into the loop instead
of the pooled-average path.

## 1. FAIRNESS AUDIT — element-by-element (brain-fidelity style)

| Element | Verdict | Why |
|---|---|---|
| METRIC (relational-neighbour cosine AUC) | **UNFAIR for comprehension, FAIR for "did the vector move"** | `V2.relational_eval` ranks a held concept's TRUE foundation-neighbour vs degree-matched non-neighbours by cosine of the concept's consolidated rep. This is leak-proof and legitimate as a "did the representation improve" metric. But it is agnostic to WHY the rep moved — any process that nudges the mean toward the neighbourhood (more samples -> less noisy centroid, lexical co-occurrence overlap with neighbour-describing text, etc.) scores exactly like genuine relational understanding would. v3's own result proves this: SCRAMBLED text moved the metric AS MUCH as coherent text (+0.029 vs +0.024). A metric that a word-order-destroying control satisfies just as well is not discriminating comprehension. |
| UPDATE MECHANISM (mean-pool mention reps -> plain average / precision-Kalman fold / common-mode-subtract / CA3-complete) | **UNFAIR — structurally incapable of comprehension by construction, not by a tunable parameter** | Every one of these is an operation on a *single vector per concept*, built by averaging (weighted or plain) per-sentence pooled reps across mentions. Averaging is a symmetric, order-blind operation over the *set* of mention reps: whatever information the per-sentence encoder captured about word order or sentence structure is intact only until pooled across many DIFFERENT mentions, at which point it collapses to "the typical context flavor of this concept." Kalman weighting changes step size (how much a new mention perturbs the running mean) but the artifact being updated is still a mean. Common-mode subtraction and CA3-style completion post-process that mean (denoise/complete it) — same object, same ceiling. None of these mechanisms can represent "concept C stands in relation R to filler F" as a retrievable structured fact; they can only represent "concept C's rep is now centered slightly differently." This is a distributional/statistical estimator, not an extraction-and-store pathway, no matter how the averaging is weighted. |
| ENCODER PLASTICITY | **UNFAIR — the only component with any capacity for order/relation-sensitive computation is fully frozen** | `_encode_sentences` runs the loaded v2 checkpoint under `torch.no_grad()`, `model.eval()`. No backward pass, no fine-tuning, ever, across any loop cycle. The trained transformer (which *could* in principle represent relational structure via attention) is frozen at pretraining's terminal state; the ONLY thing that changes cycle-over-cycle is the pooled-vector-averaging arithmetic sitting on top of it. So "learning" in this loop is entirely learning-by-reweighting-an-average, never learning-by-updating-a-representation-function. |
| READING (4-16 real mentions/cycle, real ARC prose) | **PARTIALLY FAIR** | Sentences are real (not templated) — good. But the loop never PARSES them: `_encode_sentences` -> `model.pooled(ids)` is embed-and-mean-pool over token positions, full stop. No sentence is ever decomposed into subject/predicate/object. Reading amount is adequate for accumulating a distributional signal (v1/v2 up to 96 mentions/concept; v3 deliberately thinned to 20 so low-exposure concepts qualify) but is not evaluated against what a "did you learn THIS specific fact" probe would need (a handful of assertions, tracked individually) — the loop only ever asks a population-level neighbour-ranking question. |
| CONTROL (word-order scramble, `_scramble_words`) | **UNFAIR — too weak, and this is now empirically proven, not just argued** | `_scramble_words` permutes word ORDER within a sentence; it does NOT change WHICH words appear. Mean-pooling over token embeddings (and even an attention-based per-sentence rep, once further mean-pooled across many mentions) retains most of its signal from lexical CONTENT/co-occurrence, not word order — this is exactly the classical bag-of-words/distributional-semantics result (word2vec/GloVe-style signal survives shuffled windows). The v3 finding that SCRAMBLED gained AS MUCH as coherent text is the direct, measured confirmation: the control never tested whether MEANING/relational content drove the gain, only whether syntax/order did. A fair control needs to swap CONTENT (wrong concept's sentences, or the same concept paired with a false/wrong relation), not just order. |
| CONCEPT SET (v1/v2: unstratified, median 655 mentions; v3: LOW/MID/HIGH exposure terciles) | **v1/v2 UNFAIR (ceiling/saturation confound); v3 FIX WAS CORRECT IN INTENT** | v1/v2 held concepts were pretraining-saturated — the frozen encoder already "knew" them from the 237M-token MLM pretrain, so there was nothing left for exposure-driven averaging to move; near-zero measured gain there is uninformative (could be a true null OR a saturated-ceiling artifact — the two are indistinguishable in that design). v3's stratification-by-ARC-mention-count is the right instinct (isolate the under-known slice) and IS a genuine improvement. |
| SATURATION vs HEADROOM | **PARTIALLY CONTROLLED, and the residual confound is instructive, not fatal** | Because v3 compares MAIN_precision vs SCRAMBLED *within the same LOW slice* (same concepts, same baseline AUC, same headroom), the headroom confound is actually held constant across that specific comparison — both arms start from an identical low baseline with identical room to rise. So the "SCRAMBLED ties/beats coherent" result is NOT a headroom artifact; it is a real demonstration that the pipeline cannot tell coherent from word-salad text, i.e. the CONTROL was the correctly-isolated variable, but the wrong control was chosen (order-destroying instead of content-destroying). Headroom is still a live confound WHEN COMPARING ACROSS SLICES (LOW vs HIGH gain-contrast is exactly a "more headroom = more measured gain" hazard) — that cross-slice contrast_ok check should be treated as weak evidence, not decisive, until content-swap controls exist at each slice separately. |

## 2. WHAT WE MISSED (the big one) — situation_reader was never wired in

Grep across all four loop cells (`exp_unified_self_learning_loop_v1.py`, `_v2.py`, `_v3.py`, `_v4.py`)
for `situation_reader`: zero hits. The only imports the loop family uses are:
`experiments.exp_scale_meaning_learn_arc_heldout_v2` (encoder + relational probe + data prep),
`hdlab.clarify_gate.ClarifyGate` (confidence-threshold flag), and `hdlab.learner.core.per_cluster_gate`
(MDL compression-ratio gate on the running mean). `hdlab/situation_reader.py` — the module that composes
the banked coref backbone (`EventCentralityReader`), the event/role extractor (`_assign_roles`, predicate +
agent + patient via `_temporal_ordering`), the Cowan-4 role-slot memory (`EventBundleCodec` +
`ChunkedFocus`), the timeline reconstructor, and the causal-link extractor — is imported by a *different*
family of experiment cells entirely (`exp_read_events_*`, `exp_arc_reasoner_*`,
`exp_intrinsic_foundation_loop_tie_gaps_*`, `exp_situation_reader_multisent_demo_v1.py`). None of those are
in the self-learning-loop call graph.

So the honest description of what the loop's docstrings call "comprehension" is: a frozen transformer
produces a mean-pooled sentence embedding (`model.pooled(ids)`), and `hdlab.learner`'s MDL gate decides
whether the *statistical coherence* of a cluster of such embeddings (are the mention-reps for this concept
tightly clustered? is there "enough" evidence by count?) is sufficient to commit a new running-mean as the
concept's foundation rep. That gate operates on **rep-cluster coherence**, never on **relation content** —
it cannot ask "does this sentence assert concept C bears relation R to filler F," because nothing in the
pipeline ever extracts R or F. The v1 docstring's line "the trained encoder... COMPREHENDS each real ARC
mention-sentence... This is the comprehension/extraction engine" is the mislabeling that let 4 prior
over-reads through this session (per the Director's own note in `WHERE_WE_ARE_NOW_2026-07-26.md`): calling
a pooled embedding "comprehension/extraction" primed every subsequent read of the AUC curve to be
interpreted as "the substrate is understanding what it reads," when the mechanism on the page never had a
channel for that. situation_reader is not vestigial in the codebase — it is fully built, self-tested, and
used elsewhere — it is vestigial **specifically inside the self-learning loop**, which bypassed it and did
distributional rep-pooling instead.

## 3. Given the audit: was the loop ever a fair test? What is the minimum fair test?

**Was it fair?** No, not as a test of "does the substrate learn comprehension from reading." It was a fair
(leak-proof, honestly controlled within its own terms) test of "does mean-pooled-embedding averaging drift
a concept's rep toward its true relational neighbour, and is that drift bigger under low pretraining
exposure." That narrower question got an honest, deflated answer: modest real drift (+0.024, LOW slice),
substantially explained by distributional sample-accumulation rather than content-specific comprehension
(scrambled control ties it). Nothing here is invalid science — it is correctly-scoped, correctly-labeled
(post-VET) evidence about a mechanism that was never going to comprehend, because it was never built to
extract structure.

**Minimum fair test of comprehension-learning** (all pieces already exist in this codebase; this is a
wiring task, not a research gap):

1. **Structured-extraction write path.** For each real mention sentence read in a cycle, run it through the
   extraction machinery already in `hdlab/situation_reader.py` (`_assign_roles` for agent/patient,
   `_temporal_ordering.extract_events` for the predicate) — or a lighter subject-relation-object extractor
   if full coref/timeline/causal machinery is overkill for single-sentence mentions — and commit the
   extracted (concept, relation, filler) tuple into a structured per-concept slot store (reuse
   `EventBundleCodec` + `ChunkedFocus` role-query unbind, banked and self-tested). This runs ALONGSIDE the
   existing pooled-mean arm, not instead of it, so the comparison is apples-to-apples on the same reads.
2. **Content-swap / wrong-relation control**, replacing (or supplementing) word-order scramble. Two
   variants, either sufficient: (a) feed the target concept's read slots with real, coherent sentences
   about a DIFFERENT, unrelated concept (same length/frequency profile, same real English) — tests whether
   the SPECIFIC subject of the text matters, not just "some real text was read"; (b) feed the SAME concept
   but with a deliberately WRONG relation/filler asserted — tests whether the specific relation taught is
   what gets learned, not just general engagement with real prose. Both survive intact whatever the current
   scramble control conflates (order vs content); a comprehension-driven pipeline must show a gain gap
   between coherent-and-correct vs either control, while a bag-of-words pipeline (like the current one)
   would not.
3. **Fact-specific metric.** In addition to the existing leak-proof relational-neighbour AUC (keep it —
   it's a legitimate distributional-quality metric), add a **specific-fact-acquired probe**: after N cycles,
   query the structured slot store via role-unbind ("what relation does concept C hold to filler F") for
   the EXACT relation asserted in the mentions just read, and score exact/near-match retrieval — not cosine
   rank against a whole graph. This is the difference between "did the neighbourhood get statistically
   closer" and "did the substrate come to hold the specific proposition it was just told."
4. **Keep what was right:** LOW-exposure/novelty stratification (v3's core idea), leak-proof edge
   disjointness (confirmed clean across v1-v3 VETs), sleep-fires-every-cycle + retention checks, and
   `ClarifyGate`'s under-known flagging as the reading-priority signal. None of that needs to change.

HARD-PASS for the next loop iteration built this way: `STRUCTURED_EXTRACT` arm's fact-specific-probe
accuracy on LOW-exposure concepts exceeds both `CONTENT_SWAP` controls by a margin (propose >=0.10
absolute, pre-registered before running) AND the existing pooled-mean arm continues to behave exactly as
this drill characterizes it (real but content-insensitive distributional drift) — i.e., the two arms should
DISSOCIATE, one comprehension-sensitive, one not. HARD-FAIL: `STRUCTURED_EXTRACT`'s fact-probe accuracy is
statistically indistinguishable from both content-swap controls — meaning even explicit extraction plus
structured storage does not yield content-specific learning, which would point the failure mode at the
EXTRACTOR's accuracy ceiling (situation_reader's role-reader is F1~0.64 on McGuffey gold per its own
docstring — extraction noise itself could wash out a small effect) rather than at the "loop never tried
extraction" gap this audit identifies.

## Cross-thread synthesis
This audit converges with, and sharpens, `notes/research_fast_concept_learning_informs_selflearning_loop_2026-07-27.md`'s
CLS-based diagnosis (fast hippocampal write vs slow cortical nudge) — that note correctly flagged "the
update mechanism may still be wrong even on low-exposure concepts" and "a coarse relational-AUC bump may
under-measure real fast-learning." This drill supplies the missing structural confirmation: it is not just
that averaging-into-the-slow-rep is the wrong CLS analogy, it is that the pipeline never had an extraction
step at all, so there was never any structured content for a fast store to hold in the first place. The
loop-v4 CLS-faithful direction that note recommends (episodic/context-addressed rep for new concepts) and
the structured-extraction wiring this drill recommends are the same fix approached from two angles
(memory-systems theory vs implementation trace) and should be merged into one loop-v4/v5 design rather than
pursued separately.

## Substrate-product implications
A user-facing "the substrate reads and learns from text" claim is NOT currently supportable — what is
supportable is "the substrate's distributional representations sharpen with reading, more so for
under-known concepts" (a real, useful, but narrower capability: representation refinement, not fact
acquisition). Shipping comprehension-learning as a product capability requires the structured-extraction
loop above; until then, any user-visible claim should be scoped to representation quality improvement, and
any "the substrate learned X from reading Y" framing should be held pending the fact-specific probe.

## Citations (verified count)
0 external citations — this is an internal code + result audit (all claims verified against file contents
read directly: `experiments/exp_unified_self_learning_loop_v1.py`, `_v2.py`, `_v3.py`;
`hdlab/situation_reader.py`; `hdlab/clarify_gate.py`; `hdlab/learner/core.py`;
`notes/WHERE_WE_ARE_NOW_2026-07-26.md`; `notes/research_fast_concept_learning_informs_selflearning_loop_2026-07-27.md`;
plus a grep confirming zero `situation_reader` imports across the loop-cell family).
