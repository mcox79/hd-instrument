# Research: Stage-4 load-bearing gaps + the cheapest decisive GPU probe for substrate-NATIVE generation

**Date:** 2026-07-07. **Type:** Advance-scouting drill (USER-directed, parallel to active Stage-3 work; no
cell dispatch, no cell design commitment -- this is the go/no-go + probe-spec only, per task framing).
**Field advisor:** run per contract; output (free-probability / semiconductor / spin-glass adjacents)
correctly overridden this cycle -- this is a USER-directed planning/diagnostic question (Trigger-E
equivalent), matching the explicit precedent of `research_stage_needs_brain_component_forward_map_2026-07-07.md`.
**Discipline:** mechanism-analog-is-not-task-analog applied throughout. Lit-scan calibration penalty applied
(deflate 0.15-0.25; novel-synthesis P capped 0.50). GPU status verified off-disk this cycle
(`tools/inflight_monitor.py`: GPU util 0%, both `overnight_queue` and `remote_cpu_queue` pending=0/running=0,
`gpu_runner_0` idle -- the "GPU just freed from density sweep" framing is confirmed, the density-sweep arms
`r10_best_config_K1024`/`K1024_retry`/`K2048` are the most recent overnight-queue terminal entries, all
`failed`/terminal, queue now idle). `substrate_router/noise_channel.py` existence verified on disk directly
(not carried from memory) -- M1.3 NoiseChannel IS built, confirming the forward-map note's claim.

---

## HEADLINE

**Stage 4's real gate is NOT "sequential/hierarchical language generation" in the sense the forward-map note
closed it (frame-slot decode of a KNOWN pre-composed structure) -- it is genuine PREDICTIVE generation
(producing a plausible UNKNOWN continuation from learned corpus statistics), and on THIS specific capability
the substrate has an unusually clean, repeated, already-on-disk negative result: every one of 4 prior attempts
to extend prediction context beyond ~1 prior token via HD-binding has landed HARD_FAIL or, at best,
MIDDLE_BAND, and three of them show context depth making predictions WORSE, not better
(`exp_n2_context_depth_hd_binding_v1`: bpc 5.00 -> 5.05 -> 5.18 as K goes 1 -> 2 -> 3, HARD_FAIL, "HD-binding
does not capture higher-order structure beyond K=1"; `exp_n5_trigram_concept_lm_v1`: trigram-HRR depth_gain
= -1.887 bits vs bigram, HARD_FAIL; `exp_substrate_direct_gen_lm_wikitext_trigram_v3_n8192_gpu`: HARD_FAIL,
ensemble does not beat bigram-count on real text; `exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu`:
the sole MIDDLE_BAND, beats bigram-count but perplexity stays >=20). This is THE gate: attention/context-
routing (thalamic) and N-way action-selection have no live traffic to arbitrate/select among until there is
a working predictive-generation primitive producing actual candidate continuations; the M3 cortex layer
(NoiseChannel) is not a gap at all -- it is already built (`substrate_router/noise_channel.py` verified on
disk) and is a service (injects the confidence-band signal generation needs), not the generative mechanism
itself. The single highest-EV, cheapest, genuinely-not-yet-tried lever is to test whether the repeated
context-depth failure is a NOISE-COMPOUNDING problem (fixable by wiring in the same per-step CA3-style
cleanup that makes multi-hop reasoning succeed at depth 15 and that the reasoning-depth self-margin drill just
derived a closed-form per-hop survival law for) or a REPRESENTATION-CAPACITY problem (the rank-1/HD-bind
context accumulator structurally cannot carry higher-order sequential statistics, matching the
Schlag-Schmidhuber linear-transformer-vs-softmax-transformer gap already flagged in the prior 5x drill). This
is directly startable now, on the freed GPU, by adding ONE new arm to an already-built, already-GPU-proven
cell (`exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu.py`) -- no new corpus, no new codebook, no
new baseline-building. **P_deflated on "substrate does non-trivial native generation at all" (beats a
bigram-count baseline via a substrate-native mechanism): ~0.20-0.25** -- genuinely uncertain, fighting a
real documented trend, not a confident prediction either direction.

---

## 1. RANKED Stage-4 load-bearing gaps (load-bearing-ness x startable-now)

| Rank | Gap | Load-bearing? | Startable now? | Verdict |
|---|---|---|---|---|
| **1 (THE GATE)** | Genuine predictive/sequential generation (next-item prediction from learned statistics, not decode-of-known-content) | YES -- nothing else in Stage 4 has real content to route/select among without this | YES -- all infra, corpora, baselines already exist; GPU idle now | **Open, load-bearing, cheap to probe further** |
| 2 | Attention/context-routing (thalamic dynamic arbitration) | YES, confirmed real Stage-4 need per forward-map note (multi-turn dialogue = first point with genuinely concurrent live subsystems) | NO -- "nothing currently creates dynamic multi-subsystem traffic for a thalamic gate to arbitrate" (forward-map note, ingest-CLS drill); needs #1 (and a live multi-turn harness) to exist first | Correctly deferred |
| 3 | Action-selection among many (N-way basal ganglia) | YES, but as an EXTENSION of an already-PROVEN primitive (binary gate HARD_PASS d4, `exp_pfc_gate_cfrpe_trained_v2`) | PARTIAL -- the gating mechanism itself is cheap to extend, but there is nothing non-trivial to select AMONG (candidate response strategies) until generation produces real candidates | Downstream of #1; cheap once #1 exists |
| 4 | M3 cortex layer (NoiseChannel / stochastic boundary injection) | Enabling scaffold, not a gap | **ALREADY BUILT** -- `substrate_router/noise_channel.py`, `router.py`, `api.py` all present on disk, verified this cycle | Not a gate; a service the generation probe can optionally consume (temperature-controlled decode) but does not block on |

**Why #1 is the gate and not "cortical microcircuit is unneeded" as the forward-map note concluded:**
the forward-map note's conclusion ("sequential/hierarchical language generation... LIKELY NOT NEEDED --
function already met by the frame-slot resonator decoder") is correct for a DIFFERENT task: recovering a
sequence that was ALREADY ENCODED (round-trip encode-then-decode of D known slots, block-local sparse
resonator, `exp_generation_decoder_gsbc_native_blocklocal_v1`, exact_ordered=1.000 in-box). That is a
structured-MEMORY capability (compose + exact readout), not a PREDICTIVE capability (produce plausible
content that was never explicitly composed, conditioned only on a prefix). Stage 4 / LM-equivalence needs the
latter -- an LLM's job is to predict a continuation the user did not supply, not to losslessly recover a
string it already built. This is a load-bearing correction to the forward-map note, not a contradiction of
it: both conclusions are true simultaneously, for two mechanistically distinct tasks that happen to share the
english word "generation." **Recommendation: retire "generation = frame-slot decode" as the working
definition for Stage-4 purposes; the frame-slot decoder solves the STRUCTURED-OUTPUT half of generation
(getting D output slots in the right order once content is known) but not the PREDICTIVE half (deciding what
content goes in slot D+1 given slots 1..D).**

---

## 2. THE TOP GPU PROBE

**Recommended mechanism: per-step CA3-style cleanup wired into context accumulation, tested as a new arm on
the existing 2nd-order trigram GPU cell.**

### What's already on disk (do not rebuild)

- `exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu.py` -- GPU cell, N=8192, already has a
  `single`/`ensemble`/`bigram_count`/`trigram_count(oracle)` arm structure, already landed MIDDLE_BAND
  (single=62.1, ensemble=43.1, bigram_count=55.8, trigram_count_oracle=20.4 perplexity).
- `exp_n1_concept_lm_substrate_native_token_decode_v3_1` -- the methodologically-cleanest substrate-native
  LM measurement (count-proportional decode, Jelinek-Mercer interpolation baselines, ceiling<bigram<
  substrate<unigram sanity-checked ordering, CV 0.011 across 3 seeds) -- reuse its decode/calibration
  discipline, not its verdict.
- `hdlab/iterative_attractor.py`, `hdlab/cleanup_family.py`, `hdlab/sequence_memory.py`,
  `hdlab/char_positional_encoder.py` -- the cleanup/hetero-associative/positional primitives to compose.
- Baselines needed (unigram / bigram-count / trigram-count-oracle) are ALREADY MEASURED and exactly
  computable (no new baseline-building work).

### The new arm (the actual probe)

At each generation step `t`, instead of accumulating the last K tokens by raw HD-bind/superposition into one
context vector and decoding once (the mechanism common to all 4 prior HARD_FAIL/MIDDLE_BAND attempts), do:

```
c_0 = clean_zero_vector
for t in 1..K:
    c_t_raw   = bind(c_{t-1}, position_shift) + encode(token_t)      # same accumulation as the failed arms
    c_t_clean = iterative_attractor.cleanup(c_t_raw)                 # NEW: CA3-style re-clean, EVERY step
predict token_{K+1} from hetero-associative readout keyed on c_K_clean (existing Path-A-style W_hetero lookup)
```

This composes four ALREADY-PROVEN substrate pieces (sequence/positional binding, CA3 cleanup attractor,
hetero-associative context->next-item memory, argmax/lookup decode) in a combination that has NOT yet been
tried -- every prior context-depth cell accumulated K steps of raw bind and cleaned up (if at all) only once,
at the end, or not at all. The new arm cleans up AFTER EVERY STEP, matching exactly the pattern that:
(a) already works for multi-hop reasoning (chain-grade at depth 15, CA3-cleanup-per-hop), and
(b) has a freshly-derived closed-form per-hop survival law (`research_reasoning_depth_self_margin_closed_form_2026-07-06.md`)
    predicting HOW per-hop cleanup should compose across depth, giving this probe a pre-registered
    quantitative target, not just a qualitative hope.

### GPU cell spec

- **Cell:** add `CLEANUP_PER_STEP` arm to `exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu.py`
  (or a `_v3` sibling if the harness prefers not to mutate a landed cell -- author's call, cell-authoring is
  exp_dev's job, not this note's).
- **Task:** next-item prediction on the SAME corpus already wired into that cell (wikitext/text8-scale token
  stream, already GPU-proven at N=8192) -- no new corpus.
- **Grid:** K in {1, 2, 3, 5} (extend past the K<=3 tested in `exp_n2_context_depth_hd_binding_v1` to see
  whether cleanup changes not just the sign but the SHAPE of the depth curve).
- **Arms:** `RAW_BIND_NO_CLEANUP` (reproduces the existing HARD_FAIL depth-degradation as the in-cell negative
  control -- must reproduce bpc 5.00/5.05/5.18-shape before the new arm's result can be trusted),
  `CLEANUP_PER_STEP` (the test arm), plus the existing `unigram`/`bigram_count`/`trigram_count_oracle`
  reference ladder (already implemented, reused verbatim).
- **Compute / ETA:** reuses the existing cell's GPU harness (already ran once at this N/vocab scale); adding
  one arm with an existing cleanup primitive (`iterative_attractor.py` is already implemented, not new code)
  is a same-order-of-magnitude cost to the cell's own prior run -- expect low-single-digit GPU-hours for a
  smoke + FULL pair, comfortably an idle-slot-sized probe, not an overnight-queue-sized one.

---

## 3. THE WEAKNESS DECOMPOSITION (the point of the probe)

Per-step logging must separate FOUR distinct failure modes, reusing methodology already proven on this exact
problem family:

**(a) Coherence-loss-over-length.** Log bpc/perplexity and top-1 as a function of K for BOTH arms (extends
the K=1/2/3 sweep already instrumented in `exp_n2_context_depth_hd_binding_v1` out to K=5). If
`CLEANUP_PER_STEP` is flat-or-improving with K where `RAW_BIND_NO_CLEANUP` degrades (5.00->5.05->5.18
pattern), that isolates coherence-loss as a NOISE-ACCUMULATION artifact of uncleaned binding, not a genuine
information deficit.

**(b) Repetition-collapse.** Log distinct-token-rate / entropy of the decoded continuation stream across the
corpus for each arm. A collapse to a small repeated set at higher K (independent of whether bpc looks
"okay") would flag a mode-collapse failure distinct from raw bpc degradation -- the block-local generation
decoder's own prior finding (`research_generation_decode_correlated_collision_exact_margin_2026-07-06.md`)
that codeword DIVERSITY shrinks sharply as the discrete quantization map gets more crowded is the exact
mechanism to check for here: does the same "many-to-one projection degeneracy" that caused duplicate-codeword
clusters at D48 in the STRUCTURED decoder also show up as repetition in the PREDICTIVE decoder's output.

**(c) Context-routing-miss (concept-recall vs transition-prediction split).** Reuse the EXACT decomposition
`n1_concept_lm_substrate_native_token_decode_v3_1` already validated: separate "did the substrate correctly
recall/recognize the right CONCEPT slot" (concept_top1, already measured at 0.507) from "did the substrate
correctly PREDICT the next concept given the right context" (the transition-prediction gap). Apply this same
split to both new arms -- if `CLEANUP_PER_STEP`'s gain (if any) comes from better concept-recall rather than
better transition-prediction, that's a DIFFERENT lever (finer VQ / better codebook alignment, per the
skunkworks synthetic PoC's "optimal-C" finding) than if the gain is in transition-prediction itself.

**(d) Decode-noise-compounding (the reasoning-depth connection, directly testable).** This is the sharpest,
most diagnostic test: fit the SAME closed-form per-hop survival law just derived for multi-hop reasoning
(`p_hop` Poisson-occupancy capture-probability, composed across depth via `D* = ln(FLOOR)/ln(p_hop)`,
`research_reasoning_depth_self_margin_closed_form_2026-07-06.md`) to the `RAW_BIND_NO_CLEANUP` arm's observed
depth curve. **If the reasoning-depth law fits the generation-context depth curve within the same ~1.2x band
it fit reasoning depth, that is strong, falsifiable, cross-mechanism evidence that generation's context-depth
failure and reasoning's hop-depth failure are THE SAME underlying phenomenon** (uncleaned compositional noise
accumulating per step) -- and per-step cleanup should fix both by the same mechanism, exactly as it already
does for reasoning. If the law does NOT fit generation's curve (wrong shape, not just wrong constant), that
rules out noise-compounding as generation's specific failure mode and points to the OTHER candidate
explanation: HD-bind's rank-1/superposition context representation has a genuine INFORMATION-CAPACITY
ceiling for higher-order sequential statistics (the Schlag-Schmidhuber linear-transformer-vs-softmax-gap
framing already flagged in `research_5x_deeper_substrate_LM_gap_2026-06-23.md` L1.6) -- a structurally
different, harder problem requiring a different context-representation primitive entirely (e.g. adapting the
frame-slot resonator's DISJOINT-BLOCK structure to hold K distinguishable prior-token slots for context,
rather than superposing them into one vector -- a genuinely new, not-yet-tried direction, flagged here as the
next lever if this probe's cleanup hypothesis fails).

**Deliverable mapping (failure mode -> load-bearing capability -> improvement lever):**

| If probe shows... | Load-bearing capability implicated | Improvement lever |
|---|---|---|
| Cleanup fixes depth-degradation, law fits within ~1.2x (same as reasoning) | Per-step re-clean (CA3 cleanup attractor) generalizes from reasoning-hops to generation-context-steps | Wire `iterative_attractor` cleanup into ALL future context-accumulation cells as a standing primitive; re-test the 3 already-HARD_FAILed cells (n2, n5, wikitext-trigram) with the same fix retrofitted |
| Cleanup helps but doesn't fully fix (MIDDLE_BAND); concept-recall component dominates the residual gap | VQ/codebook alignment (concept granularity), not the transition mechanism | Sweep C (optimal-C tradeoff, already identified by the skunkworks synthetic PoC) before re-testing depth |
| Cleanup helps but transition-prediction component dominates the residual gap | The hetero-associative context->next-item memory itself (rank-1 Hebbian capacity), independent of noise | Hierarchical rank-stacking (Eugenio-style n-gram-of-n-gram composition, PC1 from the 5x drill, not yet dispatched) |
| Cleanup does NOT help; law does not fit generation's curve at all | Representation-capacity ceiling of superposed/bind-based context (not noise) | Disjoint-block context representation (frame-slot-style K-slot context encoding) -- new direction, not a retread of any of the 4 failed cells |
| Repetition-collapse present regardless of arm | Quantization/projection degeneracy in the discrete decode map (same mechanism flagged in the block-local generation-decoder self-margin drill) | Higher-resolution or learned quantization at the decode stage, independent of the context/cleanup question |

---

## 4. HONEST DEPENDENCIES

- **Does NOT depend on unfinished Stage-3 work.** Retrieval-at-scale, compositional-generalization-closure,
  and multi-hop KG reasoning are separate primitives from context-depth-for-prediction; this probe touches
  none of their code paths or data. Genuinely parallel-startable alongside current Stage-3 work, not a
  sequencing violation.
- **Does depend on, and all are CONFIRMED present on disk this cycle:**
  (a) `hdlab/iterative_attractor.py` and `hdlab/cleanup_family.py` exist and are already wired into other
  chain-grade cells (multi-hop reasoning) -- not new code, a composition of existing primitives.
  (b) A GPU-proven corpus + baseline harness exists (`exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu.py`)
  with unigram/bigram-count/trigram-count-oracle already computed -- no new baseline-building.
  (c) GPU is genuinely idle right now (`tools/inflight_monitor.py`: util 0%, both queues pending=0, runners
  idle) -- confirmed off-disk this cycle, not assumed from the task framing.
- **One real risk flagged, not hidden:** `iterative_attractor.py` (the att1 family) has its OWN documented
  HARD_FAIL history at high-storage/high-noise operating points (`research_5x_deeper_substrate_LM_gap_2026-06-23.md`,
  PC2 risk note: "the cleanup substrate is in HARD_FAIL family from att1... major risk for PC2"). This probe
  is not guaranteed to work even on its own most-favored hypothesis -- if the cleanup primitive itself is
  operating outside its working regime at this N/vocab scale, `CLEANUP_PER_STEP` could fail for a reason
  UNRELATED to whether per-step cleanup is the right idea in principle. Mitigation: log the cleanup
  attractor's own convergence/residual-noise diagnostics per step (not just downstream bpc) so a
  cleanup-primitive-malfunction is distinguishable from a "per-step cleanup doesn't help" result.
- **Baseline that makes the diagnostic clean:** the word-bigram-count and trigram-count-oracle baselines
  already computed in the existing cells (exactly-computable, non-substrate, non-neural count tables) are the
  correct "small local LM" reference -- they isolate "does the substrate mechanism capture at least as much
  information as a trivial frequency table" without conflating with any neural-LM confound. No new baseline
  needs to be built; reuse the ones already on disk.

---

## Cheap decisive test (go/no-go gate before spending full GPU compute)

Run the `CLEANUP_PER_STEP` arm at SMOKE scale (reduced corpus, same N=8192, K in {1,2,3} only) FIRST. Two
outcomes:
- **GO (proceed to FULL):** smoke shows `CLEANUP_PER_STEP` at K=2/K=3 at least MATCHING K=1 (not degrading
  the way `RAW_BIND_NO_CLEANUP` does at smoke scale) -- the qualitative signature the hypothesis predicts.
- **NO-GO (kill before FULL, cheap):** smoke shows the SAME degradation pattern as
  `exp_n2_context_depth_hd_binding_v1` (K=2/K=3 worse than K=1) even with per-step cleanup -- this is an
  immediate, near-zero-cost falsification (smoke-must-exercise-same-branches-as-FULL discipline) that rules
  out the noise-compounding hypothesis before any GPU-hour is spent on the FULL grid, and redirects
  immediately to the representation-capacity-ceiling lever (disjoint-block context encoding) instead.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Claim under test: "per-step CA3-style cleanup fixes the substrate's context-depth degradation for
predictive generation, the same way it enables depth-15 multi-hop reasoning."**

- **HARD-PASS:** `CLEANUP_PER_STEP` bpc/perplexity is flat-or-improving across K in {1,2,3,5} (no
  degradation vs K=1), AND beats the `RAW_BIND_NO_CLEANUP` control by >= 0.3 bits at K>=3, AND the
  reasoning-depth per-hop survival law fits the resulting depth curve within the same ~1.5x band it fit
  reasoning-depth (cross-mechanism confirmation), AND this holds across >=3 seeds (CV <= 0.15).
- **HARD-FAIL:** `CLEANUP_PER_STEP` reproduces the SAME degradation shape as the 3 prior HARD_FAIL cells
  (bpc/perplexity gets worse with K, not better), OR the reasoning-depth survival law's fit to the observed
  curve is qualitatively wrong (not just a different constant), OR the cleanup arm's own diagnostic shows the
  attractor is operating outside its working regime (confirming the att1-family risk dominates, not the
  underlying hypothesis).
- **MIDDLE_BAND:** cleanup helps (flat-or-improving vs K=1) but does not beat a bigram-count baseline outright
  -- proceed to the concept-recall-vs-transition-prediction split (Section 3c) to route to the correct
  follow-up lever.
- P(claim holds) raw ~0.35-0.40 (a real, motivated, not-yet-tried composition of two independently-proven
  primitives, with a genuine quantitative prior from the reasoning-depth law) -> **P_deflated ~0.20-0.25**
  after the mandatory lit-scan calibration penalty AND after weighting the substrate's own recent track
  record on this exact problem family (4 prior attempts at context-depth extension, 3 HARD_FAIL + 1
  MIDDLE_BAND, 0 HARD_PASS) -- this is genuinely uncertain in either direction, not a confident bet, and the
  real risk (att1-family cleanup malfunction) is independently documented, not speculative.

---

## Cross-thread synthesis

- Directly extends and partially corrects `research_stage_needs_brain_component_forward_map_2026-07-07.md`
  Section 2(a) -- the frame-slot-decoder-solves-generation conclusion is retained for STRUCTURED round-trip
  decode but explicitly does NOT extend to predictive next-item generation, which is Stage 4's actual
  LM-equivalence need and remains genuinely open.
- Builds directly on the substrate's own multi-cell history on this exact question:
  `orchestrator_to_skunkworks_N1_DEFINITIVE_substrate_LM_beats_unigram_not_bigram_2026-06-21.md` (concept-LM
  MIDDLE_BAND, beats unigram not bigram), `research_5x_deeper_substrate_LM_gap_2026-06-23.md` (the
  rank-1-Hebbian-vs-composition diagnosis, PC1/PC2/HYBRID candidate levers, Schlag-Schmidhuber linear-vs-
  softmax-transformer framing), and the landed depth-sweep negatives (`exp_n2_context_depth_hd_binding_v1`,
  `exp_n5_trigram_concept_lm_v1`, `exp_substrate_direct_gen_lm_wikitext_trigram_v3_n8192_gpu`, all HARD_FAIL)
  plus the one MIDDLE_BAND (`exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu`).
- Directly connects `research_reasoning_depth_self_margin_closed_form_2026-07-06.md` (per-hop survival law,
  cross-cell replicated within 6.4%) to generation for the first time -- this note is the first place the
  per-hop-cleanup framing has been proposed as a candidate FIX for the context-depth family's repeated
  negative result, rather than treated as a separate multi-hop-reasoning-only finding.
- Uses `research_generation_decode_correlated_collision_exact_margin_2026-07-06.md` (exact duplicate-class
  self-margin, "projection degeneracy" side-finding) as the mechanism source for the repetition-collapse
  failure-mode check (Section 3b).
- Confirms `director_M3_M1_3_stochastic_noise_injection_design_spec_2026-07-01.md` is fully implemented
  (`substrate_router/noise_channel.py` verified present on disk this cycle) -- the M3 cortex layer is not a
  Stage-4 dependency risk.

## Substrate-product implications

- Per the USER-locked framing: this probe is diagnostic, not a scoreboard against an LLM. A HARD_FAIL here
  (cleanup doesn't fix it) is exactly as valuable as a HARD_PASS -- it would definitively separate "generation
  needs a noise-compounding fix" from "generation needs a structurally different context representation,"
  closing off half the search space cheaply, on GPU time that was otherwise idle.
- If HARD_PASS: the substrate would gain its first context-depth-positive predictive-generation primitive,
  directly reusable as the Stage-4 gate's unlock -- and it would come with a cross-mechanism, closed-form
  explanation (the same per-hop survival law that already explains reasoning-depth), which is a much stronger
  substrate-understanding claim than an isolated empirical win.
- If HARD_FAIL: the honest next lever (disjoint-block/frame-slot-style context encoding, borrowing the
  STRUCTURE, not the task, of the already-proven generation decoder) is already named and falls out of this
  drill for free -- no dead cycle, a concrete redirected next probe.
- Either way, this keeps Stage-4 advance-scouting genuinely useful without skipping ahead of Stage 3, and
  gives Director a real go/no-go rather than a speculative "generation is deferred" placeholder.

## Citations (verified count: 0 new external sources this cycle -- internal-corpus diagnostic synthesis per
task scope; the reasoning-depth survival-law citation and the block-local generation-decoder citations are
carried, not re-verified, from their own source notes (`research_reasoning_depth_self_margin_closed_form_2026-07-06.md`,
`research_mechanism_envelope_blocklocal_generation_decoder_2026-07-05.md`,
`research_generation_decode_correlated_collision_exact_margin_2026-07-06.md`,
`research_5x_deeper_substrate_LM_gap_2026-06-23.md`), per 2x-drill discipline. On-disk facts verified directly
this cycle, per Fix#28: `tools/inflight_monitor.py` GPU/queue-idle state; `substrate_router/noise_channel.py`
+ `router.py` + `api.py` file existence; all cited metrics.json verdicts
(`exp_n2_context_depth_hd_binding_v1`, `exp_n5_trigram_concept_lm_v1`,
`exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu`,
`exp_substrate_direct_gen_lm_wikitext_trigram_v3_n8192_gpu`) read directly from disk this cycle, not carried
from memory.)
