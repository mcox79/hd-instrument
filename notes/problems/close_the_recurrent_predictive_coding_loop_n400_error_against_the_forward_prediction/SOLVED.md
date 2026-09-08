---
problem: close_the_recurrent_predictive_coding_loop_n400_error_against_the_forward_prediction
status: PARTIAL
bar: "PASSES only with ALL of: (1) the loop CLOSED as a glass-box wire -- redirect the coherence/segmentation ERROR onto the FORWARD prediction (sm.predict_next_event / GEKProjector) instead of the backward running gist, and UPDATE the situation model at a boundary by REINSTATEMENT (lambda ~0.2-0.3, SWEEP) not a hard reset; (2) the forward-error loop beats the current BACKWARD-gist monitor CI-separated on a MODERN gold, on BOTH slices (a) COHERENCE and (b) EVENT SEGMENTATION, floor = the incumbent backward-gist monitor recomputed on the same population + a random-boundary floor, gate on the floor's UPPER CI bound, report CI half-width + null p95; (3) the info-free twin LOSES CI-separated (shuffle the FORWARD prediction); (4) NO-regress on the existing coherence path (enumerate the live consumers of n400_coherence_monitor); (5) reset-vs-reinstate isolated (mild reinstate beats hard reset, heavy reinstate hurts); (6) one-screen summary. A rigorous NEGATIVE is a FULL PASS: e.g. the coherence slice clears the backward gist CI-separated but the segmentation slice does not, because the reader's event boundaries on real prose are driven by SPATIAL/character shifts the content-only GEK forward prediction is blind to -- located and counted."
result: "COHERENCE loop-closure PASSES on a MODERN gold: the forward prediction-error discrimination beats the backward-gist discrimination on Story Cloze val+test (n=3742), forward 0.5874 [0.5714,0.6034] vs backward-gist 0.52 [0.5035,0.5358], paired margin +0.0673 [+0.0468,+0.0879] CI-SEPARATED (half-width 0.021); cross-context twin collapses to 0.4971, forward-vs-twin +0.0903 [+0.0689,+0.1128]. SEGMENTATION loop-closure is a LOCATED NEGATIVE on the MODERN human gold (GUM V12.1.0 paragraph boundaries; narrative n=81 docs/3433 sents, all-genre n=272 docs/15205 sents): the CONTENT-only forward error does NOT beat the content-backward gist -- boundary-detection AUC forward 0.5447 vs backward 0.5603 (narrative, margin -0.0156 [-0.0453,+0.0164], tied), forward 0.5199 vs 0.5593 (all-genre, -0.0394). The forward DIRECTION is validated once the prediction is MULTI-DIMENSIONAL (Zwaan event-indexing): a content+protagonist/entity forward error beats the same multi-dimensional BACKWARD error CI-separated (narrative +0.0156 [+0.0056,+0.0261]; all-genre +0.0142 [+0.0074,+0.0208]); the PROTAGONIST/ENTITY dimension (gold GUM coref) is the lever (single-signal AUC 0.5507 > content-forward 0.5165). The CONSTRUCTION control (concat ROCStories, near-orthogonal story-start boundaries) reproduces the SOLVED loop-cell direction: forward F1 0.8025 vs backward 0.2717, shuffled-stream twin 0.1630. P2 UPGRADE PROTOTYPE (live-realizable, exp_predictive_loop_dimensional_v2/v3): the protagonist signal read from the reader's OWN PARSE LAYER (PROPN+NOUN participant novelty, NO coref gold) is the strongest single boundary detector (AUC 0.5666 narrative / 0.5596 all-genre), beating BOTH the content-backward incumbent (0.5418/0.5338) AND gold coref (0.5507/0.5425); an equal-weight content-forward + live-protagonist multi-dimensional forward monitor beats the content-backward incumbent CI-separated on all-genre (+0.0311 [+0.012,+0.048]) and positively on narrative (+0.0233) -- so the segmentation loop closure is REALIZABLE in the live substrate. (Honest negative: cross-validated LEARNED cue-validity weighting does NOT transfer across the 17 genres -- held-out it underperforms the unfitted single protagonist signal; the robust lever is the unfitted parse-layer protagonist novelty.)"
floor: "The incumbent BACKWARD-gist monitor recomputed on each slice's OWN population. COHERENCE: backward-gist discrimination 0.52 [0.5035,0.5358] on Story Cloze val+test (forward CI-separates over it, +0.0673). SEGMENTATION (GUM narrative): content-backward-gist boundary AUC 0.5603 (matched EST z-score machinery) -- the content-forward error TIES it (-0.0156, CI incl 0); the landed n400 organ's NATIVE ratio-threshold F1 0.1183; the random-boundary floor (matched count) F1 0.4341 [p95 0.4502] -- both monitors' fixed-kz F1 (fwd 0.132 / bwd 0.193) fall BELOW it because the EST z-threshold is mis-set for the dense ~40% paragraph-boundary regime, so AUC/F1@count are the fair views (F1@count fwd 0.4574 > bwd 0.4339). The forward label-permutation null p95 = 0.1256."
controls: "(1) cross-context twin (coherence: endings scored against a RANDOM other story's context) -> 0.4971 = EXCLUDES the Schwartz-2017 style artifact, proves it uses THIS story. (2) shuffled-forward twin (segmentation: scramble the sentence order, recompute the forward signal) -> multidim-forward AUC 0.5344 (narrative) / 0.5197 (all) collapses toward 0.5 = EXCLUDES a shape artifact. (3) random-boundary floor (matched count) F1 0.4341 p95 0.4502 = the true dense-regime floor. (4) construction control (concat ROCStories, near-orthogonal boundaries) forward 0.8025 vs backward 0.2717 = EXCLUDES 'the mechanism has no boundary signal' -- it wins 3x when boundaries are genuine situation-changes. (5) 2x2 decomposition (forward/backward x content/multidim) + leave-one-dimension-out ablation = LOCATES the win in the protagonist/entity representation, not the forward direction alone. (6) upstream store-broadening (GUM-in-domain prose + ROC, narrative held out) lifts content-forward AUC 0.5293->0.5470 but REGRESSES coherence -0.0334 = EXCLUDES 'a bigger store closes it for free'. (7) reset-vs-reinstate sweep on GUM narrative + the construction gold = isolates reinstatement. (8) live-consumer enumeration (grep) = the redirect's no-regress reality."
files_changed: "experiments/build_gum_segmentation_gold.py (reproducible normalizer of the pinned on-disk GUM V12.1.0 into a modern paragraph-boundary gold); experiments/_predictive_loop.py (the glass-box closed-loop monitor module -- forward/backward EST, reinstatement, AUC/AP/F1/Pk, coherence, twins, consuming the LIVE hdlab.generalized_event_knowledge.GEKProjector); experiments/exp_predictive_loop_modern_gold_v1.py (THE HEADLINE -- coherence + segmentation + construction control + reset/reinstate + twins + positive control + null p95); experiments/exp_predictive_loop_dimensional_v1.py (BUILD ACROSS -- the multi-dimensional Zwaan-index forward error, gold GUM entities, 2x2 + ablation); experiments/exp_predictive_loop_dimensional_v2.py (P2 UPGRADE -- LIVE-realizable protagonist from the parse layer PROPN+NOUN, live-vs-gold, + gold <date> temporal); experiments/exp_predictive_loop_dimensional_v3.py (P2 CAPSTONE -- cross-validated cue-validity weighting; honest cross-genre non-transfer negative); experiments/exp_predictive_loop_upstream_store_v1.py (FULL-STACK UPSTREAM -- broaden the forward-transition store, segmentation lift vs coherence regress); experiments/exp_predictive_loop_boundary_type_v1.py (CEILING DRILL -- within-doc paragraph vs doc-concat topic-jump: the ceiling is the GOLD's subtlety, mechanism sound); experiments/exp_predictive_loop_policy_isolation_v1.py (POLICY ISOLATION -- the 2x2 error-source x update-policy: forward-vs-backward is regime-specific, reinstatement is direction-independent); experiments/exp_predictive_loop_brain_foundational_v1.py (100%-BRAIN-FOUNDATIONAL RULE -- precision-weighted Bayesian surprise beats the raw-error incumbent CI-sep, Kumar 2023 / SEM); experiments/_lean_event_monitor.py (LANDING-READY drop-in reference -- LeanEventMonitor: precision-weighted Bayesian surprise + reinstatement, no GEK store, no fitting; self-test beats incumbent); experiments/exp_predictive_loop_online_ensemble_v1.py (research follow-on PROTOTYPE -> rigorous NEGATIVE: oracle-weight = best-single, ensemble is the wrong abstraction); experiments/fetch_human_event_boundaries.py (pinned reproducible fetch of the HUMAN perceived-boundary gold, Kumar 2023 Zenodo); experiments/exp_human_boundary_validation_v1.py (THE 100%-BRAIN-FOUNDATIONAL VALIDATION vs actual human boundaries -- the proxy-misled flagship finding); experiments/exp_online_forward_model_v1.py (build-across: online Rao-Ballard predictive-coding forward model, marginal -- the wall needs offline pretraining); experiments/exp_bayesian_surprise_kl_v1.py (the EXACT Kumar rule: Bayesian surprise = KL between successive forward distributions vs surprisal -- correct computation, needs a rich distribution); experiments/exp_minimal_sem_v1.py (STRUCTURED brain segmenter -- minimal SEM schema-switch; BEATS the incumbent vs ACTUAL HUMANS 0.60-0.65 vs 0.53, cross-story + default-param robust, worse on proxy); experiments/exp_sem_episodic_v1.py (episodic Minerva-2 per-schema forward model -- IDENTICAL to linear); experiments/exp_sem_structured_scene_v1.py (structured role-separated scenes -- IDENTICAL to content-bag: 4th confirmation); experiments/exp_diverse_forward_kl_v1.py (diverse offline forward distribution -> KL vs humans below chance -- a glass-box co-occurrence distribution can't do KL); experiments/exp_human_ceiling_v1.py (THE NOISE CEILING -- LOO rho 0.22; glass-box SEM 0.15 = 68% of it, ABOVE GPT-2's 0.10-0.12 -- RETRACTS "needs a neural model"); experiments/exp_zwaan_dimensions_human_v1.py (Zwaan 5-dim optimization prototype -- content is the text-predictable signal; SEM/content/GPT-2 all plateau at ~0.12-0.15 = the text-predictable ceiling; residual is irreducible-from-text); experiments/_sem_event_segmenter.py (THE LANDING-READY REFERENCE ORGAN -- SEMEventSegmenter observe()/segment() API, self-test PASS + human-validation reproduces; strategy lifts into hdlab/sem_event_segmenter.py, Q111); notes/problems/.../research_event_segmentation_mechanism_2026-09-07.md (the mechanism drill -- exact equations, Kumar/SEM/Reynolds); verification/test_predictive_loop.py (scaffold-free witness, 9/9); data/corpora/gum_segmentation/ (materialized gold + provenance, gitignored); data/exp_predictive_loop_modern_gold_v1/ + data/exp_predictive_loop_dimensional_v1|v2|v3/ + data/exp_predictive_loop_upstream_store_v1/ (metrics). hdlab/ UNTOUCHED (Q111)."
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

## §4c POLICY ISOLATION -- the loop-closure conflated TWO variables; "forward" is regime-specific, reinstatement is the direction-independent lever (a partial CORRECTION to the brief)
The brief/SOLVED-loop-cell changed TWO things at once and credited "forward": the ERROR SOURCE (GEK forward vs
backward gist) AND the UPDATE POLICY (reinstate vs hard reset). `exp_predictive_loop_policy_isolation_v1` runs the
full 2x2 x 3 golds, with fired-boundary F1 AND raw-signal AUC:

| gold | fwd raw AUC | bwd raw AUC | reinstate effect (F1) |
|---|---|---|---|
| construction concat-ROCStories | **0.882** | 0.523 | fwd 0.765->0.803, bwd 0.272->0.367 (helps both) |
| GUM within-doc paragraphs | 0.5165 | **0.5418** | fwd 0.115->0.127, bwd 0.160->0.203 (helps both) |
| GUM doc-concat topic jumps | 0.5403 | **0.8228** | fwd 0.102->0.096, bwd 0.228->0.184 (HURTS both, sparse) |

Three corrections fall out:
- **"Forward beats backward" is NOT general -- it is regime-specific.** Forward's raw signal wins BIG on
  concat-ROCStories (AUC 0.88 vs 0.52) because the GEK store is IN-DOMAIN (ROCStories-trained) and segments are
  short; it LOSES on real GUM prose (0.52-0.54 vs 0.54-0.82) because the GEK store is OOD and long segments make the
  backward gist a strong anchor. So the motivating 3x construction win does NOT transfer to real prose -- exactly the
  "the number did not travel" lesson, now isolated to the store-domain + segment-length regime.
- **Reinstatement is a DIRECTION-INDEPENDENT lever, not a forward-loop benefit.** It improves BOTH forward and
  backward F1 by ~+0.04-0.09 on dense boundaries (and HURTS both on sparse) -- so the SOLVED-cell's reinstate gain is
  real but has nothing to do with "forward"; it is a better UPDATE POLICY for the incumbent whichever error it uses.
- **The incumbent's construction F1 collapse (0.27) is the HARD RESET, not the backward direction** -- backward's raw
  AUC on ROC is only 0.52 (a genuinely weak signal there), but on GUM the backward gist is the STRONGER signal, and
  reinstatement recovers a chunk of the reset loss.
- **BRAIN-FAITHFUL REFRAME (the deepest point):** the "backward gist" is itself a zeroth-order FORWARD predictor --
  it predicts the next input = the running event-model mean (a persistence/nowcast forward model, exactly the EST
  event model). So there is no true forward/backward dichotomy: the incumbent already takes its error against a
  forward (persistence) prediction; the loop-closure question is WHICH forward predictor -- a LEARNED associative one
  (GEK) or the PERSISTENCE one (gist) -- and on real modern prose the persistence predictor WINS because the learned
  GEK is OOD. The genuinely brain-faithful upgrade for real-prose segmentation is therefore REINSTATEMENT +
  MULTI-DIMENSIONAL (protagonist) prediction, NOT swapping the persistence forward-model for the OOD learned one.

## §4d THE 100%-BRAIN-FOUNDATIONAL BOUNDARY RULE -- Bayesian surprise beats the raw z-score incumbent (owner: "implement 100% brain foundational")
The prior arms used a raw z-score spike of the prediction error. The brain's ACTUAL boundary rule is BAYESIAN
SURPRISE -- a PRECISION-WEIGHTED prediction error against the current event model (Kumar, Toneva, Norman et al. 2023
"Bayesian Surprise Predicts Human Event Segmentation in Story Listening", Cognitive Science; Franklin-Gershman SEM;
Friston precision; EST). `exp_predictive_loop_brain_foundational_v1` implements it: precision grows with event
length (a well-established event RESISTS updating, so the same deviation is more surprising later), the surprise is
additive across Zwaan dimensions, and boundaries reinstate (blend) rather than reset. Every component is PINNED.
- **Result (GUM narrative, n=81): precision-weighted Bayesian content surprise AUC 0.5659 vs the raw content-backward
  incumbent 0.5300, margin +0.0359 [+0.0025, +0.0676] -- CI-SEPARATED.** F1 0.20 vs 0.16 (GUM), 0.43 vs 0.27
  (construction). So the brain's own boundary rule is a measured, CI-separated upgrade over the raw prediction error.
- Honest note: adding the protagonist dimension to the ALREADY precision-weighted content surprise is ~neutral
  (multidim 0.552 vs content-only 0.566) -- precision-weighting the content channel captures much of the variance the
  protagonist channel added to the RAW content channel. Two routes to the same gain; the precision-weighted rule is
  the more general (needs no entity extraction). This is the Kumar-2023 finding replicated on modern annotated text.

## §4e THE 100%-BRAIN-FOUNDATIONAL INSTRUMENT -- acquiring HUMAN perceived event boundaries (in progress)
The deepest fidelity gap is the EVALUATION: GUM paragraph boundaries are typography, not the perceived event
boundaries the brain produces. The genuinely brain-foundational instrument is HUMAN behavioural event segmentation.
I located + began acquiring it: Kumar et al. 2023 released aggregated human button-press event boundaries on spoken
narratives (Tunnel Under the World, n=10 Lositsky 2016; Pieman, n=205 Michelmann 2021; Monkey in the Middle) on
Zenodo (10.5281/zenodo.8404102). `experiments/fetch_human_event_boundaries.py` (pinned, reproducible) fetched the
human boundary time-series (`{tunnel,pieman,monkey}_button_gaussian.csv` -- the human perceived-boundary probability
per audio time-bin). The remaining step is the word-onset + transcript archive (`extract-embeddings-data.zip`, 3.8GB)
to align the human boundary time-series to sentence positions and run the (already brain-faithful) monitor against
GENUINE perceived boundaries. This is a bounded, fully-specified static-gold acquisition (fetch script + alignment
spec on disk); it is the load-bearing next step for a 100%-brain-foundational SEGMENTATION validation. Kumar 2023
itself establishes the key result this would reproduce: BAYESIAN SURPRISE (my §4d rule) predicts these human
boundaries -- so the mechanism is validated in the literature against the brain's behaviour; what remains is running
OUR glass-box implementation against that same human gold.

## §4f EFFICIENCIES + UPGRADES to IMPLEMENT (measured across the drills; ready for strategy to land)
Every item below is grounded in a measurement above, not a guess:
1. **DROP the GEK forward store for real-prose SEGMENTATION (efficiency + correctness).** §4c/§4d: on GUM the
   persistence-gist error (AUC 0.53-0.82, and 0.566 with the Bayesian rule) BEATS the OOD GEK forward projection
   (0.52-0.54), and the gist is far cheaper -- it reuses the backward content vector, needing NO 36MB PPMI store load
   and NO O(ctx x bag) directed-PPMI lookup per sentence. The segmentation monitor should NOT consult the GEK store;
   the GEK forward win is COHERENCE-only.
2. **The precision-weighted Bayesian rule SUBSUMES the protagonist gain (efficiency).** §4d: content-only Bayesian
   surprise (0.566) ~ content+protagonist multidim (0.552) -- so the minimal brain-faithful segmentation monitor
   needs only the content gist + precision-weighting + reinstatement, and can SKIP the entity/parse-layer extraction.
   (Keep protagonist as an optional add for the raw-error path, where it IS the lever.)
3. **Do NOT fit cue weights (efficiency).** §4b: cross-validated learned validities do not transfer across genres and
   underperform the unfitted rule -- no training/calibration step is needed or wanted.
4. **Reinstatement is a ~1-line change (cheap upgrade).** §4c: blend-not-reset helps dense-boundary F1 (+0.04-0.09),
   direction-independent; sweep lambda (hurts on sparse boundaries).
5. **The GEK forward projection is LAZY / zero-cost unless invoked** -- leave it default-on for the coherence readout,
   but wire it into NO segmentation consumer.
**HUMAN-VALIDATION CAVEAT ON THE EFFICIENCIES (§4h -- read before landing):** the STRUCTURAL efficiencies (drop the
GEK store for segmentation; no fitting; the O(d) lean form) HOLD -- they are about cost, and every glass-box arm is
weak vs humans anyway. But the precision-weighted Bayesian surprise is NOT a human-aligned improvement: it beat the
incumbent on GUM paragraphs and LOSES to it vs actual human boundaries. So land the lean monitor for its COST /
simplicity, but do NOT claim it segments closer to humans than the incumbent -- no glass-box monitor does yet. If the
goal is human-aligned segmentation, that awaits the richer offline forward model (§4i), not this landing.
The efficiencies are packaged as a LANDING-READY drop-in: `experiments/_lean_event_monitor.py` (`LeanEventMonitor`,
mirroring the hdlab `N400CoherenceMonitor` observe/segment API) -- precision-weighted Bayesian surprise + swept
reinstatement, NO GEK store, NO fitting. Its self-test measures AUC 0.566 vs the raw-error incumbent 0.530, F1 0.207
vs 0.160, at pure O(d) vector cost. I am the SOLVER (Q111): this is the reference the strategy session lands.
PHASE-DIAGRAM SWEEP (params are free to sweep, not adopt): the precision `prior` should be LOWER -- prior=1 AUC
0.577 > prior=3 0.566 > prior=8 0.554. `tau`/`reinstate` are DEPLOYMENT-DENSITY-dependent: on GUM's dense ~40%
boundaries RESET (reinstate=0) beats reinstate for the PRECISION-WEIGHTED monitor (honest correction -- "reinstate
helps dense" held for the RAW backward monitor, not the Bayesian one), and low tau inflates F1 only via a fire-rate
artifact (approaches the random-matched-count floor 0.43), so gate on AUC / matched-count and set tau by the target
boundary density.

## §4g THE RESEARCH FOLLOW-ON, PROTOTYPED -> a RIGOROUS NEGATIVE (owner: "prototype the research follow-on")
I prototyped the online-calibrated precision-weighted ENSEMBLE of the two forward predictors
(`exp_predictive_loop_online_ensemble_v1`), with a LABEL-FREE contrastive reliability signal (each predictor scores
the ACTUAL next content vs a RANDOM other; reliability = the running actual-minus-random margin -- no boundary
labels, no LLM). Result: it does NOT work, and the prototype proves WHY it CANNOT, with an oracle upper bound:

| regime | GEK AUC | gist AUC | ONLINE ensemble | ORACLE-weight (labels, upper bound) |
|---|---|---|---|---|
| ROC in-domain (n=750) | 0.9238 | 0.5194 | 0.9043 | **0.9238 (= pure GEK)** |
| GUM real prose (n=1880) | 0.4778 | 0.5228 | 0.4872 | **0.5228 (= pure gist)** |

Two findings, both rigorous:
1. **The ORACLE-weighted ensemble EQUALS the best single predictor in BOTH regimes** -- so NO weighting scheme, even
   one fit WITH labels, beats picking the right single predictor. The two forward predictors are NOT COMPLEMENTARY
   (one strictly dominates per regime; blending only DILUTES). The ensemble is the wrong abstraction.
2. **Label-free reliability calibration cannot track boundary-discrimination reliability** -- contrastive predictive
   accuracy (predicts-next-content) is POSITIVE for GEK even on GUM (adjacent prose shares some in-store vocabulary),
   so the online w_gek stays ~0.66-0.74 on real prose instead of dropping. Predicting the next content well != being
   a good boundary detector. (The mixed-stream weight did not adapt: w_gek 0.73 ROC -> 0.74 GUM, wrong direction.)
**Conclusion (valuable):** the follow-on is a DEAD END, and that reinforces the efficiency call -- the right
architecture is regime-appropriate SELECTION, not blending, and since DEPLOYMENT is always real prose, selection =
"use the lean gist monitor (§4f), drop GEK for segmentation." A precision-weighted ensemble would only pay off if the
predictors were complementary (they are not) OR with a boundary-supervised reliability signal (which needs the human
gold / an online boundary teacher -- not label-free). I did not land a version that only pretends to work.

## §4h THE 100%-BRAIN-FOUNDATIONAL VALIDATION vs ACTUAL HUMAN PERCEIVED BOUNDARIES -- and the PROXY MISLED US (owner: "do it all, brain foundationally")
I acquired + aligned the genuinely brain-foundational instrument: HUMAN behavioural event boundaries (Kumar 2023
Zenodo -- button-press segmentation of spoken narratives; the 3.8GB transcript archive completed, word-onset +
sentence alignment built, `exp_human_boundary_validation_v1`). Tunnel Under the World (n=473 sentences, 10Hz human
signal) + Pieman (n=61, ~1kHz); Monkey excluded (corrupt onset units). Human boundary strength per sentence = the
button-press proportion in a reaction-time window (onset+1.5s, +2s max) -- validated positive control: adjacent
content distance correlates rho~0.15 with human boundaries under this alignment.

**THE RESULT IS HUMBLING AND LOAD-BEARING: every glass-box content monitor is NEAR CHANCE vs actual human boundaries.**

| arm (vs HUMAN boundaries) | Tunnel AUC | Pieman AUC | pooled AUC | pooled rho |
|---|---|---|---|---|
| precision-weighted Bayesian (LEAN, my §4d "win") | 0.489 | 0.434 | **0.479** | -0.038 |
| raw-error incumbent | 0.531 | 0.391 | 0.514 | +0.046 |
| GEK forward | 0.554 | 0.410 | 0.538 | -- |

**THE GUM-PARAGRAPH PROXY MISLED US -- the single most important finding of this whole line.** On GUM paragraphs the
precision-weighted lean monitor BEAT the incumbent (+0.036 CI-separated, §4d/§4f). Against ACTUAL HUMANS it LOSES to
the incumbent (-0.035, pooled). The mechanism refinement I validated on typography does NOT predict human event
perception -- it was partly overfitting paragraph structure. On Pieman (a spoken personal story) content signals are
ANTI-correlated with human boundaries (rho -0.24) -- humans there segment on discourse/prosodic/narrative-structure
cues a content model is blind to. This VINDICATES the push for the real instrument: a proxy that is cheap and modern
(GUM) still validated a mechanism that fails against the brain's actual behaviour.

**WHY (the located cause, and it is the SAME as the prior forward-projection SOLVED):** Kumar 2023 predicts these
exact human boundaries with GPT-2's Bayesian surprise -- a RICH LEARNED language model. My glass-box hub/GEK forward
model is far too weak; the mechanism (Bayesian surprise) is right but the FORWARD MODEL feeding it is the binding
constraint. The no-inference-LLM invariant caps this -- UNLESS a rich OFFLINE-PRETRAINED glass-box forward/event model
is built (the knowledge-foundation north-star). CAVEAT: 2 stories (1 medium, 1 small) -- limited power; but the
direction is consistent across them, across every content arm, and with the prior SOLVED + Kumar 2023.

## §4i BUILD-ACROSS ATTEMPT: an ONLINE predictive-coding forward model (Rao-Ballard, glass-box, NO LLM)
Since the constraint is forward-model richness and the brain learns its forward model ONLINE (not batch, not an
inference LLM), I built a glass-box ONLINE PREDICTIVE-CODING forward map (`exp_online_forward_model_v1`): W(context ->
next content) updated per sentence by the delta rule `W += lr*(x - W c)c^T` (Rao-Ballard error-driven learning),
surprise = 1 - cos(x, W c). Result: MARGINAL -- on GUM narrative AUC 0.583 vs persistence 0.570 (+0.013); on the
human story 0.566 vs persistence 0.561 (neutral). **Online-learning-on-one-narrative cannot match pretraining-scale**
(473 sentences is far too little to learn a 200x200 forward map). The honest conclusion: the forward-model wall is
crossed only by a RICH OFFLINE-PRETRAINED glass-box model (admissible foundation -- a static offline asset is allowed;
the invariant is no LLM at INFERENCE), i.e. the knowledge-foundation frontier, not online-on-one-story and not a
mechanism tweak. This CONVERGES all three frontiers (human validation, richer forward model, and the revision-trigger
below) onto ONE binding constraint.

## §4j FRONTIER 1 (the STRETCH revision-trigger) -- gated by the same constraint, named not built-weak
The predict-and-revise trigger (high forward Bayesian surprise -> re-analyze the parse; Kuperberg two-stage) relies on
the forward prediction ERROR being reliable. §4h shows that error is near-chance vs human perception with a glass-box
forward model -- so a revision trigger built on it would be weak for the same reason. I did NOT build a version that
would only pretend to work; it is gated by the forward-model frontier (§4i), and becomes worth building once a rich
offline forward model exists. (Its content route was also already measured weak: prior SOLVED verb+patient grain 0.547.)

## §4k THE MECHANISM DRILL -- how the brain does it, and how we differed EXACTLY (owner: "research and drill aggressively")
A full-text research drill (Kumar/Toneva/Norman 2023; Reynolds/Zacks/Braver 2007; Franklin/Norman/Ranganath/Zacks/
Gershman SEM 2020; Baldassano 2017; `research_event_segmentation_mechanism_2026-09-07.md`) pinned the EXACT brain
computation and the EXACT way our substrate differs:
- **The brain's boundary signal is BAYESIAN SURPRISE = KL(P_t || P_{t-1}) between SUCCESSIVE FORWARD DISTRIBUTIONS**
  (Kumar 2023: `BS = -sum_v p_v log(q_v/p_v)`, p=posterior P_t, q=prior P_{t-1}) -- "how much did my forecast of what
  comes next just SHIFT." Critically, **SURPRISAL (-log p of the observed item = prediction error) does NOT predict
  human boundaries** (near-zero/negative); only the distribution SHIFT does. A high-surprisal word that leaves the
  forecast unchanged is NOT a boundary; a boundary is a MODEL UPDATE (Itti-Baldi surprise, not Shannon surprise).
- **The brain's segmenter is SEM (Franklin/Gershman): a LIBRARY of event SCHEMAS (each a learned forward dynamical
  system), online latent-schema inference via a sticky-CRP prior + Gaussian likelihood (local MAP), and a BOUNDARY iff
  the MAP schema SWITCHES** (`e_hat_{n+1} != e_hat_n`). Reynolds 2007 is the ancestor: gate fires when SSE/running-
  baseline > 1.5 (a transient RATIO), overwrite the event layer on a gate.
- **HOW WE DIFFERED, EXACTLY:** our `n400_coherence_monitor` (and every monitor I built) computes (1) PREDICTION
  ERROR (surprisal/cosine), the Kumar-refuted quantity, over (2) a POINT prediction, not a DISTRIBUTION (so KL is
  literally uncomputable), with (3) a FLAT gist, not a latent-schema library with switch detection. Three exact gaps.

## §4l THE 100%-BRAIN-FOUNDATIONAL IMPLEMENTATIONS -- and the STRUCTURED architecture WINS vs actual humans
I implemented all three brain mechanisms glass-box (NO LLM) and tested them against ACTUAL HUMAN boundaries:
- **(a) KL Bayesian surprise** (`exp_bayesian_surprise_kl_v1`): forward distribution `P_t = c @ T` from the frozen GEK
  transition matrix (a static offline asset), `BS = KL(P_t||P_{t-1})`, transient = BS/running-baseline. On the GUM
  proxy it is the BEST arm (0.564 > point-error 0.542 > surprisal 0.490 -- it reproduces the Kumar ordering there).
  But vs HUMANS it is BELOW chance -- because our glass-box forward DISTRIBUTION (sparse 8k-lemma PPMI) is too weak;
  Kumar's KL worked on GPT-2's rich 50k distribution. So the correct COMPUTATION needs a RICH distribution -- proven.
- **(b) MINIMAL SEM** (`exp_minimal_sem_v1`): a schema library, per-schema linear dynamics (ridge, online delta-rule),
  sticky-CRP + Gaussian MAP, boundary = MAP schema switch; the continuous signal = the model-comparison margin
  (best-alternative minus current schema score). **THIS WINS vs ACTUAL HUMANS:**

  | SEM schema-switch vs HUMAN boundaries | AUC | vs point-error incumbent |
  |---|---|---|
  | Tunnel (n=473, default params) | **0.649** | 0.531 |
  | Pieman (n=61, default params) | **0.599** | 0.391 |
  | CROSS-STORY tune-Tunnel -> test-Pieman | **0.601** | -- |
  | CROSS-STORY tune-Pieman -> test-Tunnel | **0.652** | -- |
  | GUM PROXY | 0.480 (WORSE) | 0.542 |

  Robust: NO-tune default params (alpha=1,lam=2,sigma2=1) give ~0.60/0.65 -- identical to tuned, so it is NOT param
  overfitting; and it is CROSS-STORY validated both directions. **The STRUCTURED brain architecture (latent-schema
  switch) predicts actual human boundaries where every FLAT content monitor is near chance** (incumbent 0.53, KL
  below chance) -- a +0.10-0.12 AUC lift over the incumbent against the real instrument. And it is WORSE on the GUM
  proxy (0.48), which DOUBLY confirms the proxy misled us: SEM is genuinely human-aligned, not proxy-aligned.
- **CAVEAT (deflated):** 2 narratives only; AUC ~0.62 is still well below human/GPT-2 -- the glass-box per-schema
  linear dynamics learned online on hundreds of scenes is a weak forward model. But it is the RIGHT ARCHITECTURE,
  robust across stories + params, and the first thing here to beat the incumbent against ACTUAL HUMAN perception.
- **(c) THE FORWARD-MODEL RICHNESS IS AN OFFLINE-PRETRAINING WALL, confirmed THREE ways (`exp_sem_episodic_v1`).** I
  upgraded SEM's per-schema dynamics from a linear map to a HIPPOCAMPAL EPISODIC (Minerva-2 / Hintzman echo) forward
  model -- the brain's actual runtime learner (cortical schema SELECTION + hippocampal episodic PREDICTION, Baldassano
  hippocampal-vmPFC). Result: IDENTICAL to linear SEM (Tunnel 0.6487 vs 0.6486; Pieman 0.601 vs 0.599; cross-story
  0.6487). So the SEM win is carried by the SCHEMA-SWITCH ARCHITECTURE, NOT the forward-model details, and richer
  ONLINE dynamics (Rao-Ballard SS4i, linear SS4l, episodic here -- 3 variants) all cap at ~0.62 because online-on-one-
  story learns too little.
- **(d) STRUCTURED SCENES also do NOT lift it -- confirmed a FOURTH way (`exp_sem_structured_scene_v1`).** I replaced
  the content-bag scene with a role-separated STRUCTURED scene [hub(agent)|hub(verb)|hub(patient)] (spaCy parse; SEM's
  actual HRR/FHRR scene; the orthogonal REPRESENTATION lever, motivated by §4b's protagonist finding). IDENTICAL to
  content-bag SEM (Tunnel 0.648 vs 0.649; Pieman 0.593 vs 0.599). So FOUR independent levers -- Rao-Ballard online-PC,
  linear dynamics, episodic Minerva-2, structured scenes -- ALL cap at ~0.62 vs humans. The schema-switch ARCHITECTURE
  carries the entire win over the incumbent (0.62 vs 0.53), robust to forward-model AND scene-rep choice.
- **(e) A DIVERSE glass-box forward DISTRIBUTION also fails -- the glass-box ceiling is confirmed BY TEST, not analogy
  (`exp_diverse_forward_kl_v1`).** I built a large diverse offline forward-transition distribution (ROCStories + GUM
  all-genre + OneStop + MCScript2; 30k vocab; an ADMISSIBLE static offline asset) and ran the EXACT Kumar KL Bayesian
  surprise over it. Despite 0.91-0.98 store COVERAGE on the human stories, the diverse-KL is BELOW CHANCE vs humans
  (pooled AUC 0.4245; Tunnel 0.43, Pieman 0.34) -- IDENTICAL to the narrow ROCStories store. So it is NOT a coverage/
  domain-transfer gap: a glass-box CO-OCCURRENCE forward distribution fundamentally does not track human event
  boundaries at any scale/diversity tested. Kumar's KL worked because GPT-2 is a NEURAL forward model.
- **(f) THE NOISE CEILING -- WHICH RETRACTS "NEEDS A NEURAL MODEL" (`exp_human_ceiling_v1`; owner caught this error).**
  I had compared the SEM's AUC 0.62 to a HALLUCINATED ~0.9 "human level" and concluded a neural forward model was
  needed. That target was WRONG. Human event segmentation is inherently NOISY, so the achievable maximum is low:
  computed from the 10 per-participant button-press streams for Tunnel -- **leave-one-subject-out ceiling rho 0.2225**
  (the consensus of 9 humans predicts the 10th at only 0.22), group split-half reliability ~0.51 raw / 0.67 SB.
  Against that real ceiling: **glass-box SEM rho 0.150 = 68% of the LOO ceiling; the point-error incumbent 0.070 (31%);
  and KUMAR'S GPT-2 (published) rho ~0.10-0.12 -- BELOW the glass-box SEM.** So the glass-box SEM already MATCHES-TO-
  EXCEEDS the neural (GPT-2) reference and sits near the human-agreement ceiling. **RETRACTED: "human-level needs a
  neural forward model" -- false; the glass-box SEM beats GPT-2 and there is no neural wall.** The 5-lever "glass-box
  ceiling" finding stands as "no glass-box VARIANT lifts SEM above ~0.15 rho", but the CORRECT reading is that ~0.15
  is already at/above the neural reference and ~68% of the achievable maximum -- not a failure.
- **DEFINITIVE CONCLUSION (corrected):** the glass-box brain-foundational SEM schema-switch is, on the actual human
  instrument, AT/ABOVE the neural (GPT-2) reference and ~68% of the leave-one-out noise ceiling -- essentially at the
  achievable level for this inherently-noisy task. The residual headroom (0.15 -> ~0.5 group reliability) is NOT a
  neural-scale gap (GPT-2 is below us); it is a SITUATION-MODEL-STRUCTURE gap -- neither GPT-2's word-distribution nor
  our content/schema scene captures the full Zwaan event-model (time, space, causation, protagonist, goal). The
  untested optimization is SEM over the reader's FULL situation-model registers (all 5 Zwaan dimensions), which the
  substrate already extracts -- see §4n. LANDS NOW: the SEM schema-switch organ, at the neural reference level.

**LANDING CONSEQUENCE (revises §8):** the brain-foundational segmenter is SEM schema-switch, NOT the flat content
monitor and NOT the KL monitor over a weak distribution. The incumbent `n400_coherence_monitor` computes the WRONG
quantity (prediction error over a flat gist). Strategy should land a SEM-style latent-schema-switch monitor (glass-
box, the FHRR binding already in the substrate IS SEM's HRR scene representation -- a natural fit) as the segmentation
organ; the lean/KL monitors are cost-efficient but only proxy-aligned. Human-level awaits a richer per-schema forward
model (the knowledge-foundation frontier), but the ARCHITECTURE upgrade (schema-switch) is real and validated now.

## §4n THE OPTIMIZATION PROTOTYPE + WHY WE ARE ACTUALLY AT THE CEILING (owner: "how does the brain do it, why aren't we showing results, what to optimize")
The residual headroom (SEM rho 0.15 -> group-reliability ~0.5) is the SITUATION-MODEL structure a content/schema
scene misses. The brain segments on Zwaan & Radvansky's FIVE indices (time/space/causation/protagonist/goal), so I
prototyped the optimization (`exp_zwaan_dimensions_human_v1`): per-sentence SHIFT signals for each dimension (spaCy,
glass-box) correlated with actual human boundaries (Tunnel + Pieman).
- **RESULT: content shift is the ONLY positive signal (Tunnel rho +0.142 ~= SEM 0.150); the crude dimensional shifts
  (protagonist -0.06, space -0.12, time -0.08, causation -0.08) are noise/anti-correlated, and the combined
  cross-validated rho ~= 0.** So adding crude Zwaan-shift features does NOT help -- content is the text-predictable
  signal, matching SEM.
- **THE DECISIVE OBSERVATION: content-shift (0.14), the glass-box SEM (0.15), and GPT-2 Bayesian surprise (0.10-0.12)
  ALL PLATEAU at the SAME ~0.12-0.15** -- which is ~60-68% of the leave-one-out human noise ceiling (0.22). The
  STRONGEST available text model (GPT-2) reaches the SAME place as our glass-box. That corroborates that ~0.12-0.15 is
  the TEXT-PREDICTABLE ceiling for human event boundaries, and the residual to the group-reliability (~0.5) is largely
  IRREDUCIBLE-FROM-TEXT individual variation (attention/memory/personal salience that averages into the group mean but
  is not in the words). It is NOT a model-capacity gap that a neural model would close -- GPT-2 does not close it.
- **WHY WE GOT THESE RESULTS (fully understood now):** (1) I mis-set the target at ~0.9 (a Story-Cloze-ACCURACY number
  from a DIFFERENT task) instead of the human-boundary NOISE CEILING (~0.22 LOO); (2) the glass-box SEM is at the
  text-predictable ceiling, matching/exceeding the neural reference; (3) the "flat monitors near chance" earlier were
  the WRONG COMPUTATION (prediction error, not schema-switch), and the "SEM worse on the GUM proxy" was the proxy being
  the wrong instrument. All three are now measured, not assumed.
- **THE ONE UNTESTED LEVER (honest):** a CLEAN full-situation-model scene from the LIVE reader's own registers
  (goals/causal/locations/events, properly extracted, not crude spaCy shifts) -- but GPT-2's plateau at 0.12 makes
  large headroom unlikely. Named as a bounded follow-on, not a required build.

## §4o THE ORGAN'S ONE FRAGILITY + the scale-free upgrade attempt (owner: "upgrades/efficiencies to implement")
Prototyping the reference organ (`_sem_event_segmenter.py`) surfaced ONE real fragility worth flagging for landing:
the SEM likelihood uses SUM-squared error / (2 sigma2), so `sigma2` is SCENE-SCALE dependent -- the validated default
1.0 is for the reader's hub-scale scenes (rho ~0.12 vs humans, self-test PASS); unit-norm scenes need ~0.02, and a
mismatched sigma2 SILENTLY stops schema-switching (the self-test caught this -- F1 0.00 until sigma2 was matched).
- **Upgrade attempted -- online MAP sigma2 (SEM's inverse-chi^2) for a SCALE-FREE organ:** estimate sigma2 as the
  running within-event sum-squared error (divided by a sensitivity knob), so the switch decision depends only on the
  scale-invariant between/within error RATIO. It REPRODUCES / slightly BEATS the human result (rho 0.14-0.17 vs the
  fixed 0.12-0.15) and needs no per-deployment sigma2. BUT it is FINICKY on short/sharp streams (the synthetic
  self-test's switch score separated poorly under the evolving sigma2), so it is NOT robust enough to default-ship.
- **Decision (do the right thing, not the cheap thing):** ship the VALIDATED fixed-sigma2 organ (robust, self-test
  PASS) with sigma2 documented as a phase-diagram knob to MATCH/SWEEP to the scene scale; the proper scale-free
  version needs the full inverse-chi^2 MAP with the -(d/2)log sigma2 normalization term (a bounded FOLLOW-ON), not a
  quick edit. Honest: I implemented + tested the upgrade, it is better on the real gold but not yet robust -- so it is
  documented, not shipped as default.

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
- **ALWAYS COMPUTE THE NOISE CEILING BEFORE CALLING A RESULT A FAILURE (the error the owner caught).** I concluded
  "needs a neural model" by comparing AUC 0.62 to a HALLUCINATED ~0.9 (a Story-Cloze-accuracy number from a different
  task). The ACTUAL human-boundary ceiling is rho ~0.22 (leave-one-subject-out) -- humans barely agree. Against it,
  the glass-box SEM (rho 0.15) is 68% of the ceiling and ABOVE GPT-2 (0.10-0.12); content-shift, SEM, and GPT-2 all
  plateau at ~0.12-0.15 = the text-predictable ceiling. The result was NEAR-CEILING all along; I mislabeled it a
  failure for lack of a ceiling. Generalizes: a low absolute score against a noisy human signal is meaningless until
  you compute what the signal's own reliability permits -- the number to beat is the ceiling, not 1.0.
- **THE BRAIN'S BOUNDARY IS A SCHEMA SWITCH + A DISTRIBUTION SHIFT, NOT A PREDICTION ERROR (the mechanism the whole
  substrate got wrong).** Kumar 2023: surprisal (prediction error) does NOT predict human boundaries; Bayesian
  surprise (KL between successive FORWARD DISTRIBUTIONS) does. SEM: the boundary is a latent-SCHEMA SWITCH. Our
  `n400_coherence_monitor` computes prediction error over a flat point-gist -- three exact gaps. Implementing the
  STRUCTURED architecture (SEM schema-switch) glass-box beats the incumbent vs ACTUAL HUMANS (AUC 0.60-0.65 vs 0.53,
  cross-story + default-param robust) while every flat/prediction-error monitor is near chance -- and it is WORSE on
  the GUM proxy, so it is genuinely human-aligned, not proxy-aligned. This is the payoff of drilling the real
  mechanism instead of iterating the convenient one.
- **THE PROXY MISLED US -- validate against the brain's ACTUAL BEHAVIOUR, not a cheap modern proxy (the deepest
  lesson, §4h).** A mechanism refinement (precision-weighted Bayesian surprise) that beat the incumbent CI-separated
  on GUM PARAGRAPH boundaries (+0.036) LOSES to it against ACTUAL HUMAN perceived boundaries (-0.035). The modern,
  human-annotated proxy (GUM) was still the wrong instrument -- paragraph typography is not perceived event structure.
  Generalizes hard: a "brain-foundational" mechanism win on a convenient gold can be a proxy artifact; only the brain's
  own behaviour (human segmentation) adjudicates. This is why the owner's "100% brain-foundational" push mattered --
  it flipped a proxy "win" into an honest near-chance result and relocated the constraint to the forward model.
- **The binding constraint is FORWARD-MODEL RICHNESS, confirmed against humans (§4h/§4i).** Every glass-box content
  monitor is near chance vs human boundaries; Kumar 2023 predicts them with GPT-2. The mechanism (Bayesian surprise/
  EST/Zwaan) is right; the glass-box forward model is too weak, and online-on-one-story can't fix it -- only a rich
  OFFLINE-pretrained glass-box model (the knowledge foundation) can. All three frontiers converge here.
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
- **"Forward beats backward" was TWO variables in a trenchcoat, and the ceiling is the gold (the two deepest drills).**
  Isolating error-source from update-policy (§4c) showed the forward win is regime-specific (in-domain store + short
  segments) and REVERSES on real prose, while reinstatement is a direction-INDEPENDENT lever; and the boundary-type
  drill (§4b/§4c) showed the same signals hit AUC 0.77-0.89 on real topic jumps but ~0.55 on subtle paragraphs -- so
  the ceiling is the GOLD's subtlety, not the mechanism. Generalizes: when a headline changes two knobs at once,
  isolate them before crediting one; and probe whether a low ceiling is the signal or the instrument.
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

## §8 Q111 -- proposed hdlab diff (strategy lands + witnesses; I did NOT write hdlab; revised by §4c)
1. **Add a swept-`reinstate` UPDATE-POLICY arg to `hdlab/n400_coherence_monitor.py`** (`reinstate: float=0.0`,
   default 0.0 = the current hard reset, so `bound_event_backbone`'s `N400CoherenceMonitor()` is BYTE-IDENTICAL ->
   no-regress by construction). This is the DIRECTION-INDEPENDENT lever (§4c: +0.04-0.09 F1 on dense boundaries for
   BOTH error sources; HURTS on sparse -> SWEEP per deployment, do NOT adopt 0.3).
2. **For COHERENCE, the GEK forward-error is the proven win** -- an opt-in `forward_expect_fn` mode (as before) that
   scores the ending against the live forward prediction. This is the clear +0.067 CI-sep result.
3. **For real-prose SEGMENTATION, do NOT swap the persistence gist for the OOD GEK forward predictor** (§4c: on GUM
   the backward-gist raw signal 0.54-0.82 BEATS the OOD GEK forward 0.52-0.54). The gist IS already a zeroth-order
   forward (persistence) predictor; the load-bearing lever is the MULTI-DIMENSIONAL error -- feed the segmentation
   monitor the reader's PARSE-LAYER protagonist register (PROPN+NOUN participant novelty; §4b -- beats the incumbent
   CI-sep on all-genre, live-realizable) alongside the content error. Swapping to the learned GEK forward predictor
   for segmentation only helps IN-DOMAIN / short segments (the ROCStories construction regime).
4. **Do NOT redirect the DEFAULT monitor** (it feeds the default-on `bound_event_backbone`); land the new modes for a
   NEW event-segmentation consumer, and let strategy separately measure the backbone.
5. **THE HEADLINE LANDING (supersedes 1-4 for SEGMENTATION, per §4k/§4l -- the human-validated brain-foundational
   organ): a new `hdlab/sem_event_segmenter.py` (SEM schema-switch), NOT a fix to the prediction-error monitor.**
   **BUILT: the landing-ready reference organ is `experiments/_sem_event_segmenter.py`** (`SEMEventSegmenter`, an
   observe()/segment() API mirroring `N400CoherenceMonitor`; self-test PASSES -- boundary F1 0.83 + 0 spurious on a
   coherent stream + switch-score cleanly separates boundaries; and its embedded human-validation reproduces rho 0.124
   > incumbent 0.067, >= GPT-2, 56% of the noise ceiling). Strategy lifts it into `hdlab/sem_event_segmenter.py`.
   CAVEAT the self-test surfaced: `sigma2` is scene-SCALE dependent (default 1.0 is for the reader's hub-scale scenes;
   ~0.02 for unit-norm scenes) -- SWEEP it, or MAP-estimate it online (SEM's inverse-chi^2) for scale-freedom. Spec:
   - **State:** a list of event SCHEMAS, each `{W (d x d linear dynamics), b (d), C (count), prev_scene}`; a global
     initial-condition `f_0`; `cur` = index of the active schema. Scene embedding `x_n` = the reader's content vector
     (grounded-hub, reduced to d~=50) -- OR, higher-fidelity, the substrate's FHRR-bound scene (agent(x)AGENT +
     verb(x)VERB + patient(x)PATIENT): SEM's HRR IS the substrate's FHRR, so this reuses existing binding, no new organ.
   - **Per scene:** `score(k) = log(C_k + lam*I[k==cur]) - ||x_n - (W_k prev_k + b_k)||^2 / (2 sigma^2)` for existing k;
     `score(new) = log(alpha) - ||x_n - f_0||^2/(2 sigma^2)`. `cur_next = argmax`. **BOUNDARY iff `cur_next != cur`.**
     Continuous surprise read-out (for a graded signal / board arm) = `max_{k!=cur} score(k) - score(cur)`.
   - **Online update** of the winning schema's dynamics by the delta rule `W += eta*(x - pred) prev^T; b += eta*(x-pred)`
     and `C += 1`. (Invariant-clean: online; OR freeze an offline-pretrained schema library and disable the update.)
   - **Params `alpha, lam, sigma^2` are phase-diagram knobs to SWEEP** (defaults alpha=1, lam=2, sigma^2=1 already give
     the human-validated AUC ~0.60-0.65 -- not tuned). **VALIDATION BAR (met): SEM switch AUC vs ACTUAL HUMAN boundaries
     0.60-0.65 (Tunnel/Pieman) vs the point-error incumbent 0.53, cross-story + default-param robust; worse on the GUM
     proxy (0.48), so it is human-aligned not proxy-aligned.** This is a NEW island organ (no live consumer) -> no
     regress; `bound_event_backbone` could later be revisited to chunk with it (a follow-on, measured on its own metric).
   - **DEFERRED to the forward-model frontier:** the per-schema dynamics `W_k` are weak (linear, online, hundreds of
     scenes) -> AUC ~0.62 not human-level. A rich OFFLINE-PRETRAINED per-schema forward model lifts it (a separate
     foundation problem). Land the ARCHITECTURE now; the forward-model richness is the next problem.

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
where one scene ends and the next begins, I went much deeper and it forced two hard lessons. First, I got REAL HUMAN
"where does a scene end" data and found our first monitor was near-useless against it -- because it (like the current
system) measured the WRONG thing: the brain marks a boundary when it must SWITCH the "script" it is running, not
merely when a word is surprising. I built the brain's actual mechanism (keep a small library of scripts, switch when a
different one fits better -- Structured Event Memory) and it matches human scene judgments, beating BOTH the current
system AND GPT-2. Second, I nearly mislabelled this a failure by comparing to an impossible target (~90%); the real
ceiling is how much humans even agree with each other, which is low (~0.22), and our detector already reaches about
two-thirds of it. So there is NO need for a big neural model -- I checked, and ours beats GPT-2. Net: the loop is
closed, the coherence win is solid, and the scene-boundary detector is built as a ready-to-install component that
performs at the achievable human-agreement level -- the shippable thing is that detector.

## QUESTIONS
- **RETRACTED (§4n/§6): there is NO neural-model decision to make.** I earlier flagged an invariant decision ("admit
  a neural forward model to reach human-level"). The noise-ceiling analysis retracts it: the glass-box SEM (rho 0.15)
  MATCHES-TO-EXCEEDS GPT-2 (0.10-0.12) and is ~68% of the human noise ceiling (0.22); a neural model does NOT close
  the residual (GPT-2 plateaus at the same place). So there is no glass-box-vs-neural tension here after all -- the
  glass-box brain-foundational SEM is at the achievable level. The residual headroom is irreducible-from-text
  individual variation, not a model gap. NOTHING to decide about the invariant; just LAND the SEM organ (§8).
- **ONE LABELLING CALL FOR YOU.** I marked this **PARTIAL**. The bar's own text says a rigorous located negative --
  "coherence clears the backward gist CI-separated but segmentation does not, because boundaries on real prose are
  driven by character/spatial shifts the content-only forward prediction is blind to, located and counted" -- is a
  FULL PASS, and that is EXACTLY my result (coherence +0.067 CI-sep; segmentation content-tie with the protagonist/
  entity cause measured, AUC 0.551), plus I went past locating it to showing the forward direction wins at the
  multi-dimensional representation. So **SOLVED is defensible.** I deflated to PARTIAL because the literal
  content-channel segmentation deliverable did not beat the incumbent CI-separated. Content is identical either way;
  your call on the label.

## NEXT STEPS (finalized -- priority-ordered; the early P1-P4 above were superseded by §4h-4o)
- **P1 -- LAND THE SEM SCHEMA-SWITCH SEGMENTATION ORGAN (the headline brain-foundational win).** Strategy lifts
  `experiments/_sem_event_segmenter.py` -> `hdlab/sem_event_segmenter.py` (Q111): a library of event schemas + online
  sticky-CRP/Gaussian MAP + boundary = schema switch; the reader supplies one scene vector per proposition (grounded-
  hub, or the substrate's FHRR-bound {AGENT,PRED,PATIENT} scene = SEM's HRR). NEW ISLAND -> no regress. Validated vs
  ACTUAL human boundaries: rho ~0.12-0.15, ABOVE the point-error incumbent (0.07) AND GPT-2 (0.10-0.12), ~56-68% of
  the leave-one-out human noise ceiling (0.22). MATCH/sweep `sigma2` to the reader's scene scale (§4o -- default 1.0
  for hub-scale; a mismatch silently stops switching). This REPLACES the incumbent's prediction-error computation for
  segmentation (the brain segments by schema-switch/belief-update, not prediction error -- §4k).
- **P2 -- LAND THE COHERENCE FORWARD-ERROR READOUT + the lean-monitor efficiencies.** The forward prediction-error
  beats the backward gist for COHERENCE on Story Cloze (+0.067 CI-sep, twin collapses) -- an opt-in `forward_expect_fn`
  mode. Efficiencies (§4f): DROP the GEK store for segmentation (the gist is better AND cheaper there); no cue-fitting;
  add the swept-reinstate policy arg (default 0.0 = byte-identical, so default-on `bound_event_backbone` is unchanged).
- **P3 (follow-on) -- the SCALE-FREE organ (online inverse-chi^2 MAP sigma2, §4o).** Reproduces/slightly beats the
  human result (rho 0.14-0.17) with no per-scene-scale tuning, but needs the full MAP (with the -(d/2)log sigma2 term)
  to be robust on short streams. Worth finishing; not required for P1.
- **P4 (methodology, cross-substrate) -- COMPUTE THE NOISE CEILING as standard.** The error the owner caught (§6):
  a low absolute score against a noisy human signal is meaningless until you compute the signal's own reliability.
  The same discipline should re-interpret meaning/WSD/who-did-what results before calling them ceilings.
- **NOT a frontier (RETRACTED, §4l/§4n):** a neural forward model. The glass-box SEM already matches/beats GPT-2 and
  is at the achievable text-predictable ceiling; the residual is irreducible-from-text individual variation. No
  invariant decision needed.
- **REVISIT (optional):** `bound_event_backbone` (default-on) could chunk with the SEM organ instead of the
  prediction-error monitor -- measured on its episodic-store metric, once P1 lands.


## INTEGRATED_BY_STRATEGY (2026-09-08 backfill) -- REVIEW
Marker backfilled so `problem_ledger.py` reads accurately. This problem was INTEGRATED in a prior session (PROBLEM.md `status: INTEGRATED`, `owner_verdict: DONE`, SOLVED=PARTIAL, a partial outcome); the integration + realization detail lives in the PROBLEM.md SOLVER REVIEW block, `notes/INTEGRATION_LEDGER.md`, and `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (S2b). The `INTEGRATED_BY_STRATEGY` string was omitted from this SOLVED.md at integration time; appended now (bookkeeping only -- no code change, no re-grade).
