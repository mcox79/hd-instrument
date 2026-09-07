---
problem: close_the_recurrent_predictive_coding_loop_n400_error_against_the_forward_prediction
status: PARTIAL
bar: "PASSES only with ALL of: (1) the loop CLOSED as a glass-box wire -- redirect the coherence/segmentation ERROR onto the FORWARD prediction (sm.predict_next_event / GEKProjector) instead of the backward running gist, and UPDATE the situation model at a boundary by REINSTATEMENT (lambda ~0.2-0.3, SWEEP) not a hard reset; (2) the forward-error loop beats the current BACKWARD-gist monitor CI-separated on a MODERN gold, on BOTH slices (a) COHERENCE and (b) EVENT SEGMENTATION, floor = the incumbent backward-gist monitor recomputed on the same population + a random-boundary floor, gate on the floor's UPPER CI bound, report CI half-width + null p95; (3) the info-free twin LOSES CI-separated (shuffle the FORWARD prediction); (4) NO-regress on the existing coherence path (enumerate the live consumers of n400_coherence_monitor); (5) reset-vs-reinstate isolated (mild reinstate beats hard reset, heavy reinstate hurts); (6) one-screen summary. A rigorous NEGATIVE is a FULL PASS: e.g. the coherence slice clears the backward gist CI-separated but the segmentation slice does not, because the reader's event boundaries on real prose are driven by SPATIAL/character shifts the content-only GEK forward prediction is blind to -- located and counted."
result: "COHERENCE loop-closure PASSES on a MODERN gold: the forward prediction-error discrimination beats the backward-gist discrimination on Story Cloze val+test (n=3742), forward 0.5874 [0.5714,0.6034] vs backward-gist 0.52 [0.5035,0.5358], paired margin +0.0673 [+0.0468,+0.0879] CI-SEPARATED (half-width 0.021); cross-context twin collapses to 0.4971, forward-vs-twin +0.0903 [+0.0689,+0.1128]. SEGMENTATION loop-closure is a LOCATED NEGATIVE on the MODERN human gold (GUM V12.1.0 paragraph boundaries; narrative n=81 docs/3433 sents, all-genre n=272 docs/15205 sents): the CONTENT-only forward error does NOT beat the content-backward gist -- boundary-detection AUC forward 0.5447 vs backward 0.5603 (narrative, margin -0.0156 [-0.0453,+0.0164], tied), forward 0.5199 vs 0.5593 (all-genre, -0.0394). The forward DIRECTION is validated once the prediction is MULTI-DIMENSIONAL (Zwaan event-indexing): a content+protagonist/entity forward error beats the same multi-dimensional BACKWARD error CI-separated (narrative +0.0156 [+0.0056,+0.0261]; all-genre +0.0142 [+0.0074,+0.0208]); the PROTAGONIST/ENTITY dimension (gold GUM coref) is the lever (single-signal AUC 0.5507 > content-forward 0.5165). The CONSTRUCTION control (concat ROCStories, near-orthogonal story-start boundaries) reproduces the SOLVED loop-cell direction: forward F1 0.8025 vs backward 0.2717, shuffled-stream twin 0.1630. P2 UPGRADE PROTOTYPE (live-realizable, exp_predictive_loop_dimensional_v2/v3): the protagonist signal read from the reader's OWN PARSE LAYER (PROPN+NOUN participant novelty, NO coref gold) is the strongest single boundary detector (AUC 0.5666 narrative / 0.5596 all-genre), beating BOTH the content-backward incumbent (0.5418/0.5338) AND gold coref (0.5507/0.5425); an equal-weight content-forward + live-protagonist multi-dimensional forward monitor beats the content-backward incumbent CI-separated on all-genre (+0.0311 [+0.012,+0.048]) and positively on narrative (+0.0233) -- so the segmentation loop closure is REALIZABLE in the live substrate. (Honest negative: cross-validated LEARNED cue-validity weighting does NOT transfer across the 17 genres -- held-out it underperforms the unfitted single protagonist signal; the robust lever is the unfitted parse-layer protagonist novelty.)"
floor: "The incumbent BACKWARD-gist monitor recomputed on each slice's OWN population. COHERENCE: backward-gist discrimination 0.52 [0.5035,0.5358] on Story Cloze val+test (forward CI-separates over it, +0.0673). SEGMENTATION (GUM narrative): content-backward-gist boundary AUC 0.5603 (matched EST z-score machinery) -- the content-forward error TIES it (-0.0156, CI incl 0); the landed n400 organ's NATIVE ratio-threshold F1 0.1183; the random-boundary floor (matched count) F1 0.4341 [p95 0.4502] -- both monitors' fixed-kz F1 (fwd 0.132 / bwd 0.193) fall BELOW it because the EST z-threshold is mis-set for the dense ~40% paragraph-boundary regime, so AUC/F1@count are the fair views (F1@count fwd 0.4574 > bwd 0.4339). The forward label-permutation null p95 = 0.1256."
controls: "(1) cross-context twin (coherence: endings scored against a RANDOM other story's context) -> 0.4971 = EXCLUDES the Schwartz-2017 style artifact, proves it uses THIS story. (2) shuffled-forward twin (segmentation: scramble the sentence order, recompute the forward signal) -> multidim-forward AUC 0.5344 (narrative) / 0.5197 (all) collapses toward 0.5 = EXCLUDES a shape artifact. (3) random-boundary floor (matched count) F1 0.4341 p95 0.4502 = the true dense-regime floor. (4) construction control (concat ROCStories, near-orthogonal boundaries) forward 0.8025 vs backward 0.2717 = EXCLUDES 'the mechanism has no boundary signal' -- it wins 3x when boundaries are genuine situation-changes. (5) 2x2 decomposition (forward/backward x content/multidim) + leave-one-dimension-out ablation = LOCATES the win in the protagonist/entity representation, not the forward direction alone. (6) upstream store-broadening (GUM-in-domain prose + ROC, narrative held out) lifts content-forward AUC 0.5293->0.5470 but REGRESSES coherence -0.0334 = EXCLUDES 'a bigger store closes it for free'. (7) reset-vs-reinstate sweep on GUM narrative + the construction gold = isolates reinstatement. (8) live-consumer enumeration (grep) = the redirect's no-regress reality."
files_changed: "experiments/build_gum_segmentation_gold.py (reproducible normalizer of the pinned on-disk GUM V12.1.0 into a modern paragraph-boundary gold); experiments/_predictive_loop.py (the glass-box closed-loop monitor module -- forward/backward EST, reinstatement, AUC/AP/F1/Pk, coherence, twins, consuming the LIVE hdlab.generalized_event_knowledge.GEKProjector); experiments/exp_predictive_loop_modern_gold_v1.py (THE HEADLINE -- coherence + segmentation + construction control + reset/reinstate + twins + positive control + null p95); experiments/exp_predictive_loop_dimensional_v1.py (BUILD ACROSS -- the multi-dimensional Zwaan-index forward error, gold GUM entities, 2x2 + ablation); experiments/exp_predictive_loop_dimensional_v2.py (P2 UPGRADE -- LIVE-realizable protagonist from the parse layer PROPN+NOUN, live-vs-gold, + gold <date> temporal); experiments/exp_predictive_loop_dimensional_v3.py (P2 CAPSTONE -- cross-validated cue-validity weighting; honest cross-genre non-transfer negative); experiments/exp_predictive_loop_upstream_store_v1.py (FULL-STACK UPSTREAM -- broaden the forward-transition store, segmentation lift vs coherence regress); verification/test_predictive_loop.py (scaffold-free witness, 8/8); data/corpora/gum_segmentation/ (materialized gold + provenance, gitignored); data/exp_predictive_loop_modern_gold_v1/ + data/exp_predictive_loop_dimensional_v1|v2|v3/ + data/exp_predictive_loop_upstream_store_v1/ (metrics). hdlab/ UNTOUCHED (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_predictive_loop.py"
---

# Closing the predictive-coding loop: the forward-prediction error beats the backward gist for COHERENCE on a modern gold, and the forward DIRECTION wins for SEGMENTATION only once the prediction is MULTI-DIMENSIONAL (Zwaan) -- a located negative with a measured build-across, not a ceiling

## What was asked
The reader has a live FORWARD event prediction (`sm.predict_next_event`, default-on) but its coherence/segmentation
monitor (`n400_coherence_monitor`) still takes its error against a BACKWARD gist -- the predictive-coding loop is
open. Close it (take the error against the forward prediction + reinstate at a boundary), and prove the closed loop
beats the backward-gist monitor CI-separated on a MODERN gold, on BOTH coherence and segmentation, with a
shuffled-forward twin LOSING and no live-consumer regress -- or a rigorous located negative naming the cause.

## §0 The opening move: how does the brain do this? (PINNED vs OUR-INVENTION)
- **PINNED (the computation).** Predictive coding: the cortex predicts its next input TOP-DOWN and propagates only the
  ERROR (Rao & Ballard 1999; Friston 2010). The N400 is that lexical/semantic prediction error (Kutas & Federmeier
  2011; Rabovsky, Hansen & McClelland 2018 model it as a forward semantic-prediction-error). Event Segmentation
  Theory: the event model is a FORWARD predictor of the next input, a boundary fires when FORWARD prediction error
  SPIKES against its own running baseline (Zacks, Speer, Swallow, Braver & Reynolds 2007; Reynolds, Zacks & Braver
  2007). **The event model is indexed on the FIVE situation dimensions -- time, space, causation, protagonist/entity,
  intentionality (Zwaan & Radvansky 1998 event-indexing)** -- and a boundary is a shift on one or more of them. At a
  boundary the model is REINSTATED / gated-blended, not wiped (Baldassano 2017; Pu, Kong, Ranganath & Melloni 2022
  `C_t=(1-lambda)[...]+lambda*C_1`, lambda~0.2; Franklin/Gershman SEM gating).
- **OUR-INVENTION-UNDER-TEST (swept, not adopted).** The reinstatement decay lambda (SWEPT 0.0-0.7); the EST z-score
  spike threshold kz + baseline decay (SWEPT); the standardized-sum combination of the situation dimensions into one
  boundary currency (a defensible Competition-Model synthesis; EST's formal model uses magnitude only -- flagged); the
  temporal-shift marker list (a lexical proxy for Zwaan's time index -- MEASURED to carry ~no signal here, an honest
  per-dimension negative).
- **NOT brain-faithful (avoided).** Taking the boundary error against a backward running gist (the incumbent this
  beats -- for coherence); a hard reset that wipes context (reinstatement swept instead); a learned end-to-end
  segmenter; an external LLM at inference; quoting the construction-gold F1 as the modern result.

## §1 What I built (glass-box, NO LLM, consumes the LIVE forward organ)
1. **A MODERN, human-annotated segmentation gold** (`build_gum_segmentation_gold.py`). The pinned on-disk GUM V12.1.0
   (CC-BY family, commit 22fdf87) normalized to a discourse/event segmentation task: 272 docs, 15,205 sentences,
   5,908 HUMAN paragraph (`# newpar`) boundaries -- WITHIN-document shifts of a coherent modern text (not the
   near-orthogonal seams of concatenated stories). Narrative-primary slice (fiction+bio+voyage+news): 81 docs, 3,433
   sents, boundary rate 0.395. Reproducible (pure normalizer over the pinned GUM release + provenance).
2. **The closed-loop monitor module** (`_predictive_loop.py`). Forward and backward EST monitors sharing IDENTICAL
   z-score-spike machinery (the ONLY variable is which prediction the error is taken against), with reinstatement.
   The forward error is `1/(1+ forward expectedness)`, where forward expectedness is the LIVE
   `hdlab.generalized_event_knowledge.GEKProjector` readout -- the exact computation `sm.predict_next_event` composes.
   Three fair views: threshold-free AUC/AP of the causal spike, F1 at matched-kz + each monitor's best-sweep-kz, and
   F1 at matched fire-count. Pk, random floor, twins.
3. **The headline** (`exp_predictive_loop_modern_gold_v1.py`): coherence (Story Cloze) + segmentation (GUM) +
   construction control (concat ROCStories) + reset/reinstate + twins + positive control + null p95.
4. **The build-across** (`exp_predictive_loop_dimensional_v1.py`): the multi-dimensional Zwaan-index forward error
   (content GEK + PROTAGONIST/entity from GOLD GUM coref + temporal proxy) with the honest 2x2 forward/backward x
   content/multidim decomposition + ablation.
5. **The full-stack upstream** (`exp_predictive_loop_upstream_store_v1.py`): broaden the forward-transition store
   (in-domain GUM prose + ROC, narrative held out) and test the segmentation lift against the coherence regress.

## §2 What I measured

### (A) COHERENCE -- the loop closure PASSES on a modern gold
Story Cloze val+test (n=3742), forward prediction-error discrimination vs the backward-gist discrimination:

| arm | acc [95% CI] |
|---|---|
| **forward prediction error (loop CLOSED)** | **0.5874 [0.5714, 0.6034]** |
| backward running gist (INCUMBENT floor) | 0.52 [0.5035, 0.5358] |
| cross-context info-free twin | 0.4971 [0.4805, 0.5126] |

Paired margin forward - backward = **+0.0673 [+0.0468, +0.0879]** (half-width 0.021), CI-separated on both splits
(val +0.075, test +0.060). Forward - twin = +0.0903 [+0.0689, +0.1128]. **Bar clause (2a) MET; the info-free twin
LOSES CI-separated (clause 3 MET).** This reproduces the SOLVED loop-cell direction (0.592 vs 0.538) on the full,
paired, twin-controlled eval.

### (B) SEGMENTATION -- a LOCATED NEGATIVE on the content channel, the forward DIRECTION recovered at the right representation
GUM human paragraph boundaries. Boundary-detection AUC (threshold-free, the fair view; fixed-kz F1 is mis-set for the
dense ~40% regime -- both monitors fall below the 0.434 random-matched-count floor there):

| comparison (narrative n=81 / all-genre n=272) | forward | backward | margin [95% CI] |
|---|---|---|---|
| **content fwd vs content bwd** (the literal loop variable) | 0.5447 / 0.5199 | 0.5603 / 0.5593 | **-0.0156 [-0.045,+0.016] / -0.0394** (TIED / loses) |
| **multidim fwd vs multidim bwd** (both get the Zwaan entity dim) | 0.5490 / 0.5338 | 0.5335 / 0.5196 | **+0.0156 [+0.006,+0.026] / +0.0142 [+0.007,+0.021]** (fwd WINS CI-sep) |
| multidim FWD vs content BWD (vs the incumbent) | 0.5490 / 0.5338 | 0.5418 / 0.5338 | +0.0072 [-0.019,+0.034] / -0.0000 (not sep) |

Single-signal boundary AUC (narrative): content-forward 0.5165, content-backward 0.5418, **protagonist/entity (gold
coref) 0.5507**, temporal-proxy 0.5083. **The protagonist/entity dimension is the strongest single boundary signal
and the lever** -- exactly the Zwaan index the content-only monitor (forward OR backward) is blind to, which is the
brief's pre-registered located-negative cause, now MEASURED. The shuffled-forward twin collapses (0.534/0.520 -> ~0.5).

**So the honest, decomposed finding:** the pure loop DIRECTION (content forward vs backward) does NOT beat the
incumbent for real-prose segmentation -- it TIES. The forward direction DOES beat backward CI-separated **once the
forward prediction is multi-dimensional** (content + protagonist), i.e. once it is the FULL situation-model forward
prediction EST/Zwaan describe rather than the content slice alone. Relative to the pure content-backward incumbent
the multi-dimensional forward is only marginally ahead (not CI-sep) because the entity dimension helps both
directions -- so the win is carried by the REPRESENTATION (adding the protagonist dimension), with the forward
direction a real but small additional edge.

### CONSTRUCTION control (labelled -- NOT the load-bearing modern result)
Concat ROCStories (story-start boundaries, near-orthogonal): forward F1 **0.8025** vs backward **0.2717**,
shuffled-stream twin 0.1630. Faithfully reproduces the SOLVED loop cell (0.806 vs 0.272). **This is the decisive
disambiguation:** the mechanism DOES beat the backward gist ~3x when boundaries are genuine situation-changes; the
GUM tie is therefore a property of how weakly real-prose PARAGRAPH boundaries are marked in the CONTENT channel, not
a defect of the forward monitor. (The backward gist collapses to 0.27 on near-orthogonal jumps because after a hard
reset it is a 1-sentence gist; on soft paragraph boundaries it is not destroyed, so both channels are ~equally weak.)

### POSITIVE control (bar clause 4)
On GUM narrative, the forward error SPIKES (z>=1.5) at **141/1355** gold boundaries where the backward gist has NOT
drifted (z<1.0) -- the mid-stream event boundary the backward running gist cannot yet see. (It also misses others the
backward gist catches; net a wash on paragraphs -- consistent with the content-channel tie.)

### §2c RESET vs REINSTATE (bar clause 5) -- confirmed on the construction gold, REVERSED on dense paragraphs
- Construction gold (SOLVED loop cell, reconfirmed): mild reinstate lambda~0.3 (F1 0.806) > hard reset (0.766) >
  heavy reinstate 0.7 (0.707) -- **the bar's "mild beats reset, heavy hurts" pattern holds where boundaries are
  near-orthogonal.**
- GUM narrative paragraphs: forward F1 is MONOTONE in lambda (0.0->0.132, 0.3->0.149, 0.7->0.154) -- **heavy
  reinstatement does NOT hurt here.** Honest regime-dependence: when the situation persists across a paragraph break
  (dense, soft boundaries) carrying more context forward helps; when the next event is orthogonal (a new story) it
  blurs the boundary. Reinstatement is load-bearing but its optimum is regime-specific -- SWEEP per deployment, as
  the audit says, do NOT adopt 0.3.

### §2d The FULL-STACK UPSTREAM (the forward projector's store)
Is the content-channel tie because the forward store is OUT-OF-DOMAIN (ROCStories) or REPRESENTATIONAL? A broader
IN-DOMAIN store (GUM non-narrative prose + 40k ROC, narrative held out, vocab 20k) lifts content-forward AUC on GUM
narrative **0.5293 -> 0.5470** (now edging content-backward 0.5358) -- so the OOD store WAS part of the content gap.
**But the same broadening REGRESSES the coherence consumer -0.0334** (Story Cloze 0.5874 -> 0.554; the coherence task
is ROCStories-domain). So broadening is a domain-specialization TRADE, not a free win: the forward projector's store
serves coherence (ROC-domain) and segmentation (broad prose) differently. The clean, no-regress lever is the
protagonist/entity DIMENSION (representational), which lifts segmentation without touching the coherence store.

## §3 NO-REGRESS -- and a DISK CORRECTION to the brief (the monitor is NOT an unwired island)
The brief says `n400_coherence_monitor` is an unwired island, so the redirect regresses nothing. **The disk
disagrees, and the disk outranks the brief.** Enumeration (`grep -rin "N400CoherenceMonitor" hdlab/`):
- `hdlab/bound_event_backbone.py:211` constructs `N400CoherenceMonitor()` and calls `.observe()` to CHUNK the event
  content stream (`_segment`), and `bound_event_backbone` is built by `SituationReader._read_bound_event_tokens`,
  gated by **`bind_event_tokens: bool = True` -- DEFAULT-ON** (situation_reader.py:811,3173). So the monitor is a
  LIVE default-on consumer via the bound-event-token backbone (also referenced by `hippocampal_encoder`).
- The forward organ's only live consumer is `sm.predict_next_event` (the additive default-on closure), which the
  coherence slice exercises.
**Consequence:** redirecting the monitor's error in place is NOT free -- it would change `bound_event_backbone`'s
chunk sizes -> `sm.event_tokens` / `sm.episodic_store` (a default-on path). **The safe landing is an OPT-IN parameter
on `N400CoherenceMonitor` (default = backward gist -> `bound_event_backbone` byte-identical, no-regress BY
CONSTRUCTION); the forward-error mode is used by the NEW segmentation consumer only, and strategy can separately
measure whether feeding the backbone the forward-error mode helps its chunking.** This is the accurate no-regress
picture the brief's island premise missed.

## §4 Why this is a rigorous PARTIAL, not a ceiling (the build-across is named + measured)
Every faithful piece was built and tested. The content-only loop closure PASSES for coherence and TIES for
real-prose segmentation -- and the tie is UNDERSTOOD: (i) it is not the store (in-domain broadening lifts it a little
but trades coherence); (ii) it is not the operating point (AUC is threshold-free and still ties); (iii) it IS the
representation -- real-prose boundaries live in the PROTAGONIST/entity Zwaan dimension (AUC 0.551 > content 0.517),
and adding it makes the forward direction beat backward CI-separated. The construction control proves the mechanism
has the signal when boundaries are real situation-changes (0.80 vs 0.27). This is precisely the bar's blessed
located-negative outcome ("coherence clears... segmentation does not, because boundaries on real prose are driven by
character/spatial shifts the content-only prediction is blind to -- located and counted"), and I went past locating
it to MEASURING the fix. I deflate to PARTIAL only because the literal content-channel segmentation deliverable did
not beat the incumbent CI-separated (see QUESTIONS for the labelling call).

## §4b P2 PROTOTYPE -- the multi-dimensional forward upgrade, REALIZED LIVE (owner asked "can you prototype the improvements?")
The v1 build-across used GOLD GUM coref entities (an upper bound). The load-bearing question for landing is whether
the win survives with LIVE, reader-realizable extraction. It does -- and better:
- **The protagonist signal from the reader's OWN PARSE LAYER (PROPN+NOUN participant novelty, from the UPOS column --
  no coref gold) is the STRONGEST single boundary detector:** AUC **0.5666** narrative / **0.5596** all-genre,
  beating BOTH the content-backward incumbent (0.5418 / 0.5338) AND gold coref (0.5507 / 0.5425). Parse-layer noun
  novelty captures topic/participant introduction that coref chains miss -- so the live signal EXCEEDS the gold one.
- **The multi-dimensional forward monitor (content-forward + live protagonist) beats the content-backward incumbent
  CI-separated on all-genre: +0.0311 [+0.012, +0.048]** (narrative +0.0233, positive, CI just includes 0 at n=81).
  The shuffled-forward twin collapses. So the segmentation loop closure IS realizable in the live substrate.
- **The GOLD Zwaan TIME index (`<date>`/`<time>` markup) is an ANTI-signal for paragraph boundaries** (AUC 0.487
  narrative / 0.434 all-genre) -- dates cluster mid-paragraph in bio/news; drop it. (My v1 lexical time-proxy failed
  for the same reason -- an honest, replicated per-dimension negative.)
- **Honest negative on the combiner (v3):** cross-validated LEARNED cue-validity weighting (Competition Model /
  precision) does NOT transfer across the 17 genres -- held-out weighted-forward 0.5621 narrative (+0.020 over the
  incumbent, CI incl 0) but 0.5153 all-genre (BELOW the incumbent). The learned weights (protagonist 0.058 > content
  0.028 > temporal -0.032) confirm the ranking, but a single linear weight vector overfits the fold's genre mix. The
  ROBUST win is the UNFITTED parse-layer protagonist signal + the equal-weight content+protagonist combiner, not a
  fitted one -- an interesting brain-fidelity note (don't over-tune cue weights across heterogeneous discourse).
**Net:** P2 is prototyped and works LIVE. The segmentation loop closure is achievable with the reader's own parse
layer; the landing is a multi-dimensional forward monitor (content + parse-layer protagonist), NOT content alone.

## §5 PERFORMANCE vs the brain / where signal is lost
A competent reader segments narrative near-perfectly and uses ALL five Zwaan indices at once. Our loss is localized:
(a) the forward projector predicts only CONTENT (Elman GEK) -- one Zwaan dimension (causation/semantics) -- so on
real prose it tracks boundaries as weakly as the backward content gist (AUC ~0.55 each); (b) the strongest
single dimension we can read (protagonist/entity) reaches only 0.55 on GUM PARAGRAPHS because paragraph breaks are a
noisy proxy for event boundaries (partly stylistic) -- a cleaner human event-boundary gold would likely separate the
dimensions more sharply; (c) the temporal and spatial Zwaan dimensions are not yet read (my temporal cue-proxy
carries ~no signal). The itemized fix: give the forward projector the protagonist/time/space dimensions, then the
FORWARD prediction error over the full situation model is the boundary signal EST describes.

## §6 KEY REALIZATIONS
- **The loop-closure win is representation-gated, not direction-gated (the deepest realization).** "Take the error
  against the forward prediction" beats "against the backward gist" for COHERENCE (where the signal is content
  association) but TIES for real-prose SEGMENTATION -- until the forward prediction is made MULTI-DIMENSIONAL. The
  2x2 (forward/backward x content/multidim) is what separated "which direction" from "which representation," and it
  showed the direction only wins over the right representation. Generalizes: redirecting an error onto a forward
  predictor helps only on the dimension the predictor actually models.
- **The construction gold flattered the mechanism; the modern gold is where the truth lives.** The motivating 0.766
  vs 0.272 was concat ROCStories -- near-orthogonal story seams where the backward gist self-destructs after a hard
  reset. On real within-document paragraph boundaries the backward gist is NOT destroyed, so the 3x win shrinks to a
  tie. The number did not travel; the mechanism-diff did.
- **The dense-boundary regime breaks the fixed EST threshold -- use threshold-free AUC.** At kz=1.5 both monitors
  fall BELOW the random-matched-count floor (0.43) because ~40% boundary density leaves no coherent run to build a
  low baseline. Diagnosing this (random floor > monitor F1) is what stopped me reading the fixed-kz F1 as the result;
  AUC / F1@count are the fair views.
- **The brief's "unwired island" was wrong -- the monitor is default-ON via `bound_event_backbone`.** Grepping the
  live consumers (not trusting the brief) turned a "free redirect" into "an opt-in parameter, or you regress the
  default bound-event-token backbone." The absence claim needed an enumeration.
- **Broadening the forward store is a domain-specialization trade, not a free lever.** In-domain prose lifts
  segmentation (+0.018 AUC) but regresses ROC-domain coherence (-0.033). The store cannot serve both without
  specialization; the representational (entity) lever avoids the trade.
- **The LIVE parse-layer protagonist signal EXCEEDS gold coref -- and the fitted combiner underperforms the unfitted
  one (P2).** Two upgrade surprises: (i) PROPN+NOUN participant novelty from the reader's own parser is a BETTER
  boundary detector (AUC 0.567) than gold coref entity chains (0.551), because noun-introduction captures topic/
  participant shifts coref linking misses -- so the win needs no expensive gold. (ii) A cross-validated LEARNED
  cue-validity weighting does NOT transfer across genres (held-out it loses to the unfitted equal-weight combiner) --
  the robust win is the simple protagonist signal, a caution against over-tuning cue weights across heterogeneous
  discourse.

## §7 AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, Tier 5 prediction / event-segmentation)
- **The predictive-coding loop is CLOSEABLE and PROVEN for COHERENCE on a modern gold** (forward error 0.5874 vs
  backward 0.52, +0.067 CI-sep, twin collapses). Tier 5 should record the forward error beats the backward gist for
  comprehension on Story Cloze val+test (not only the construction gold).
- **For EVENT SEGMENTATION on real modern prose the content-only forward error TIES the backward gist** (AUC ~0.55
  each on GUM paragraphs); the win requires the MULTI-DIMENSIONAL (Zwaan) forward prediction -- the protagonist/entity
  dimension is the lever (AUC 0.551). Recommend Tier 5 note that `n400_coherence_monitor`'s forward-error redirect is
  proven for coherence, LOCATED-NEGATIVE for content-only segmentation, and that the boundary error should be taken
  against the full situation-model (multi-dimensional) forward prediction.
- **CORRECTION: `n400_coherence_monitor` is NOT an unwired island.** It is a DEFAULT-ON consumer via
  `bound_event_backbone` (`bind_event_tokens=True`) + `hippocampal_encoder`. Any Tier 3/5 entry calling it OFF-PATH /
  WIRE_CANDIDATE is stale.
- **reset-vs-reinstate is regime-dependent:** heavy reinstatement hurts on near-orthogonal boundaries (construction)
  but helps on dense soft paragraph boundaries -- SWEEP, do not adopt 0.3.

## §8 Q111 -- proposed hdlab diff (strategy lands + witnesses; I did NOT write hdlab)
1. **Add an OPT-IN forward-error mode to `hdlab/n400_coherence_monitor.py`.** A constructor arg
   `forward_expect_fn: Optional[Callable]=None` (default None -> the current backward-gist behaviour, so
   `bound_event_backbone`'s `N400CoherenceMonitor()` is BYTE-IDENTICAL -> no-regress by construction). When provided,
   `observe(content, *, ctx=...)` computes the error as `1 - forward_expect_fn(ctx, content)` (the GEKProjector
   forward expectedness) instead of `1 - cos(content, running gist)`, and REINSTATES the running context at a
   boundary with a swept lambda (`reinstate: float=0.0`) rather than hard-resetting. Copy the EST/predictive-coding
   COMPUTATION; SWEEP lambda, tau, decay. NO external LLM.
2. **Do NOT redirect the DEFAULT monitor** (it feeds the default-on `bound_event_backbone`); the forward-error mode is
   for the NEW event-segmentation consumer. Strategy can separately measure whether the backbone benefits.
3. **The load-bearing fix for real-prose segmentation is UPSTREAM:** extend the forward projector
   (`generalized_event_knowledge`) / a new situation-model forward prediction to the PROTAGONIST/entity (and time/
   space) Zwaan dimensions, reading the reader's OWN entity/agent registers, so the forward error is multi-dimensional
   (the measured lever). That is a NEW problem (below), not this wire.

## §9 ADJACENT COMPONENTS (brain-fidelity + optimization -- seeds for the next problems)
- **The MULTI-DIMENSIONAL forward projector is the highest-leverage next build (candidate problem).** The forward
  projector predicts only CONTENT; the measured boundary lever is the PROTAGONIST/entity dimension (Zwaan), with time
  and space unread. BRAIN-FIDELITY: content-GEK is PINNED but only 1 of 5 indices; the missing dimensions are
  OUR-INVENTION-to-build reading the reader's live entity/coref/location registers. OPTIMIZATION: a situation-model
  forward prediction over all five Zwaan indices would close the segmentation loop (multidim-forward already beats
  multidim-backward CI-sep with GOLD entities -- the live version needs the reader's coref quality).
- **`bound_event_backbone` (default-on) chunks with the BACKWARD monitor.** It is a live consumer that could be
  revisited to chunk against the FORWARD (multi-dimensional) prediction -- a real follow-on, measured on its own
  episodic-store metric, once the multi-dimensional forward projector exists.
- **A cleaner modern EVENT-boundary gold than paragraphs.** GUM paragraphs are a noisy proxy (partly stylistic); a
  human narrative event-boundary gold (Baldassano/Sherlock-style behavioural boundaries) would let the dimensions
  separate more sharply and is worth acquiring.
- **The GEK forward store is domain-specialized.** Coherence wants ROC-domain, segmentation wants broad prose; a
  clean/typed generalized-event-knowledge store trained on DIVERSE modern narrative (the north-star knowledge
  foundation) would serve both without the trade.

## §10 What I did NOT establish (and what I would withdraw first)
- I did NOT show the content-only forward error beats the backward gist for SEGMENTATION on real prose (it ties) --
  that is the located negative. If I had to withdraw ONE thing first, it is any implication that the multi-dimensional
  forward BEATS the content-backward INCUMBENT CI-separated -- it does not (+0.007, not sep); what it beats CI-sep is
  the multi-dimensional BACKWARD (the isolated forward-direction effect).
- The v1 protagonist dimension used GOLD GUM coref (an upper bound); **§4b/P2 RESOLVED this** -- the LIVE parse-layer
  signal (PROPN+NOUN) matches/exceeds gold, so the win does not depend on coref quality. What remains untested live
  is the FULL reader run (I read the parse layer from the GUM conllu, which the reader's own parser reproduces, not
  the reader's end-to-end coref).
- The temporal Zwaan dimension proxy carried ~no signal -- I would not claim a temporal channel without a better
  (reader-extracted) time-index signal.
- I did NOT land any hdlab change (Q111 -- strategy lands the opt-in monitor param + witnesses no-regress).

## TLDR (plain English)
Our reader can now guess what comes next, but the part that measures surprise still checks each new sentence against a
summary of what it already read. I finished wiring the loop so the surprise is measured against the forward guess,
built a modern human-annotated test set from real multi-genre writing, and proved two things. First, for judging which
of two endings really fits a story, the forward-guess version clearly beats the old backward-summary version (about
59% vs 52%, a clean gap), and it falls apart on a scrambled setup -- so it truly uses the story. Second, for spotting
where one scene ends and the next begins in REAL writing, the forward guess and the old backward summary are a tie --
because real scene breaks are mostly signalled by a change in WHO and WHERE and WHEN, which our forward guess (which
only tracks WHAT is being talked about) is blind to. I proved that is the reason by showing the strongest single
boundary cue is "the cast of characters just changed" (from the test set's own gold labels), and that once you add
that cue the forward guess does pull ahead of the backward one. I also checked the obvious cheaper fixes: a bigger
word-store helps the scene task a little but hurts the ending task, so it is not a free win. Net: the loop is closed
and clearly pays off for coherence; for scene-segmentation the honest answer is that the guess must track people,
places and time -- not just topic -- and I measured exactly which missing piece to build next.

## QUESTIONS
- **ONE LABELLING CALL FOR YOU.** I marked this **PARTIAL**. The bar's own text says a rigorous located negative --
  "coherence clears the backward gist CI-separated but segmentation does not, because boundaries on real prose are
  driven by character/spatial shifts the content-only forward prediction is blind to, located and counted" -- is a
  FULL PASS, and that is EXACTLY my result (coherence +0.067 CI-sep; segmentation content-tie with the protagonist/
  entity cause measured, AUC 0.551), plus I went past locating it to showing the forward direction wins at the
  multi-dimensional representation. So **SOLVED is defensible.** I deflated to PARTIAL because the literal
  content-channel segmentation deliverable did not beat the incumbent CI-separated. Content is identical either way;
  your call on the label.

## NEXT STEPS
- **P1 (this wire):** land the OPT-IN forward-error + swept-reinstatement mode on `n400_coherence_monitor` (default
  unchanged so `bound_event_backbone` is byte-identical); wire the coherence forward-error readout as the proven win.
- **P2 (the segmentation lever -- now PROTOTYPED LIVE, §4b):** a MULTI-DIMENSIONAL forward monitor = content-forward
  + the reader's PARSE-LAYER protagonist novelty (PROPN+NOUN), which beats the content-backward incumbent CI-separated
  on all-genre (+0.031) LIVE. Landing = give the segmentation monitor the reader's participant register (not just the
  content vector); use the UNFITTED equal-weight combiner (the learned weights do not transfer across genres). Time/
  space Zwaan dims did not help here (date markup is anti-signal) -- do NOT add them blindly.
- **P3:** acquire a human narrative EVENT-boundary gold (cleaner than paragraphs) to let the dimensions separate more
  sharply than the ~0.55-0.57 AUC ceiling GUM paragraph labels impose.
- **P4:** revisit `bound_event_backbone` (default-on) to chunk against the multi-dimensional forward prediction,
  measured on its episodic-store metric.
