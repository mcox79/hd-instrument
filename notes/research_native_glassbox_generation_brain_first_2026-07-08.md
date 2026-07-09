# Brain-first drill: the native generative mechanism, and a buildable glass-box path

**Date:** 2026-07-08. **Type:** heavy brain-grounding drill (USER-directed, self-authored, no sub-agents).
Biology leads throughout; ML/LLM framings (autoregressive decoding, beam search, denoising diffusion) are
treated as weak secondary references and explicitly flagged where the brain diverges from them.
**Field advisor:** run per contract (thermodynamics/spin-glass/free-probability top-ranked as usual); overridden
this cycle — this is a USER-directed mechanism-inventory question (Trigger-E equivalent), matching precedent of
prior forward-map / gap-scoping drills.

**What was verified off-disk before writing anything** (per Fix#28, do not re-derive what's already landed):
- `data/exp_substrate_gen_lm_contextgate_depth_v5_n8192_gpu/metrics.json` — CONTEXT_GATE (recency-only) arm,
  MEASURED_MECHANISM, dGATE=+0.0028 vs dRAW=+0.6486 (99.56% flatten), 3/3 seeds, permutation-scramble control
  fires at 11x. RECENCY gate on a 1st-order corpus (optimal selection = attend-most-recent).
- `data/exp_substrate_gen_lm_contentgate_flagdep_v6_n8192_gpu/metrics.json` — HARD_PASS. Content-addressed
  (query-key) admission gate beats the 1/(K-1) content-blind cap (CONTENT=1.000 vs cap 0.200) on a corpus where
  the informative slot's POSITION is uniform-random (recency provably fails, RECENCY=0.272≈cap).
- `data/exp_substrate_gen_lm_contentgate_noisycue_v7_n8192_gpu/metrics.json` — HARD_PASS. Same content-gate,
  now under a realistic noise-corrupted (inferred, not handed) relevance cue, q=0.08/cue_snr=7.24: still clears
  cap+0.30, monotone degradation with cue quality.
- `data/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu/metrics.json` — HARD_PASS[COMBINED]_
  ARBITRATION. A single graded-normalization gate arbitrates recency-prior vs content-cue: beats BOTH single
  gates on a mixed corpus, wins the sub-regime where each single gate individually fails (conflict → content
  wins; cue-absent → falls back to recency), and a scramble-of-content-ordering control separates by 0.658.
- All four cells' corpora are **synthetic, explicitly-tagged** (a `flag_id` cue token/slot with controllable
  `cue_q` corruption, random codebooks) — NOT natural higher-order language statistics. This is the honest gap
  this note sharpens below.
- `research_noise_compounding_bound_deep_mechanism_2026-07-07.md` — regenerative-repeater vs decision-feedback-
  equalizer law: chains that hard-reset against a FIXED EXTERNAL reference at every hop (reasoning-depth) don't
  compound error; chains that "correct" using the SAME noisy estimator that produced the error (waypoint
  verify-gate, cerebellar SR-rollout) do. `retry_rate_combo=0.0` proved the waypoint verify-gate was self-
  referential, not independent.
- `research_brain_predictive_generation_predict_residual_build_spec_2026-07-07.md` — PREDICT_RESIDUAL_TD
  (deep online TD-bootstrap residual correction) was proposed as the "deep antidote"; per the task framing it
  landed WORST, capped at the substrate's ~0.507 concept-recall ceiling.
- `research_neural_reasoning_loop_mechanism_inventory_2026-07-08.md` — same-day 5-lit-scan inventory for the
  glass-box reasoning loop: PFC bias-signal → hippocampal CA3 completion (indirect, via entorhinal/nucleus
  reuniens); bimodal working memory (active attractor + activity-silent trace); cortico-BG-thalamic Go/NoGo
  gating (PBWM, value-trained, separable input/output loci); **hippocampal SWR replay as OFFLINE multi-hop
  composition, run BEFORE the loop commits, prioritized by gain × need** (Pfeiffer & Foster 2013; Mattar & Daw
  2018); PFC subgoaling is continuously-parameterized/compositional, not a discrete option library (Yang et al.
  2019; Bernardi et al. 2020) — directly relevant below, since this is the SAME replay mechanism this drill
  independently re-derives for generation.
- `research_deep_chain_reasoning_bounded_compounding_error_brain_first_2026-07-08.md` — same-day sibling drill,
  independently converges on "replay-generate-then-select (bidirectional forward/reverse full-candidate
  scoring)" as the fix for a different compounding-error target (waypoint chains). Independent cross-
  validation of the mechanism this note proposes for generation.

---

## HEADLINE

**The brain does not generate by recurrently accumulating raw state and decoding once at the end — the failure
mode this substrate has hit four times. It generates by (1) composing a bounded, whole-sequence "plan" OFFLINE,
before commitment, by hippocampal sharp-wave-ripple replay that recombines already-learned local fragments
(never free improvisation from nothing — the field's own evidence against "preplay" of never-experienced
structure, Silva/Feng/Foster 2015 vs Dragoi/Tonegawa, settles this), prioritized by a gain×need value schedule
(Mattar & Daw 2018); then (2) reading that bounded plan out ONE ITEM AT A TIME via competitive-queuing
extraction — a parallel activation-gradient ("primacy code") read off by repeated winner-take-all-and-inhibit,
which this substrate already has built as the peel/SIC decoder; and (3) arbitrating, at the fragment-selection
and read-out-order level, between a recency prior and a content-match cue via a value-trained cortico-BG-
thalamic gate — which this substrate has ALREADY PROVEN in isolation (v5 recency-only MEASURED_MECHANISM, v6/v7
content-only HARD_PASS, v8 combined-arbitration HARD_PASS) at the synthetic-tagged-cue level. None of these
three steps ever "corrects a noisy accumulator using more of the same noisy signal" — which is exactly, and
specifically, why the substrate's own deep antidote (PREDICT_RESIDUAL_TD, an online TD-bootstrap residual
correction against its OWN uncertain prediction) failed: it is architecturally the self-referential-correction
failure class the regenerative-repeater law already named and proved kills chains (same class as the waypoint
verify-gate and cerebellar SR-rollout failures), not a new or mysterious result.

**The crux is narrower and harder than the task's original framing.** "Content-dependent gating on a
higher-order corpus" is NOT untested — v6/v7/v8 already prove content-addressed admission beats recency when
position is uninformative, including under realistic cue noise, and arbitrates correctly against recency in a
mixed regime. What remains genuinely untested is the harder generalization: v6/v7/v8's "content" is an
EXPLICIT, single tagged cue token matched against an explicit query (a needle-in-haystack retrieval) — real
language relevance has no such tag; it must be inferred from the LEARNED CO-OCCURRENCE GEOMETRY of the
associative store itself (the same store, `W_hetero`, already flagged as the rank-1-Hebbian capacity
bottleneck in `research_5x_deeper_substrate_LM_gap_2026-06-23.md`). **The crux is: does content-addressed
admission generalize from "match an explicit tag" to "match on implicit, learned, graded relevance" — and does
it survive being driven by a fragment-store that is itself capacity-limited (the barrier-#1 encoder problem)?**

**Highest-probability-superior NEW mechanism flagged:** stop treating generation as "predict-next-token given
an accumulating context" altogether (the frame that has failed four times, independent of which patch is
applied to the accumulator). Reframe it as "compose a bounded plan vector offline (replay), then repeatedly
extract from that ONE FIXED, BOUNDED object" (competitive queuing via peel/SIC) — this removes the accumulator
data structure that is the actual site of noise-compounding, by construction, rather than patching it with
gating/cleanup/residual (which is what all four prior attempts, and three of the four antidotes, did).
</br>

---

## 1. The brain's native generative loop, by mechanism (deep biology, ranked)

### Mechanism 1 (RANK 1 — the reframe): Competitive-Queuing whole-sequence readout

**Brain mechanism + source signature.** Grossberg (1978); Houghton (1990); Bullock & Rhodes (2003); Kornysheva
et al., "Neural Competitive Queuing of Ordinal Structure Underlies Skilled Sequential Action," *Neuron* 2019
(PMC6436939). A **parallel planning layer** holds ALL items of a to-be-produced sequence simultaneously active
at once, coded by a graded **primacy activation gradient** (item to be produced soonest = highest activation).
A **competitive choice layer**, downstream, runs winner-take-all: the currently-highest-activation planning
unit fires its choice-layer counterpart, which both executes AND inhibits (a) all other choice units and (b)
its own planning-layer source. The next-highest item now wins. Sequence order is recovered entirely from a
STATIC (bounded, non-accumulating) activation pattern by repeated extract-and-inhibit — never by updating a
running state across the sequence.

**How it avoids noise-compounding.** Every extraction reads directly off the SAME fixed, bounded parallel
code — there is no accumulator that grows or decays with sequence position. This is mathematically the SAME
class of fix as the regenerative-repeater law already proven for reasoning-depth (hard reset against a FIXED
EXTERNAL reference at every hop keeps per-hop error i.i.d.) — except here the "fixed external reference" is a
single composed object read multiple times, rather than an external codebook. Per-item error does not compound
with read-out position because read-out position never touches the representation of items not yet extracted.

**Composition with already-operational pieces.** This is **already built and proven** on the STRUCTURED half of
generation: the frame-slot / block-local sparse resonator decoder (`exp_generation_decoder_gsbc_native_
blocklocal_v1`, exact_ordered=1.000) IS a competitive-queuing-style extraction (peel / successive-interference-
cancellation: decode highest-confidence slot, subtract/inhibit, repeat) over a KNOWN, pre-composed plan. The
`research_stage4_generation_load_bearing_gap_and_gpu_probe_2026-07-07.md` note already correctly separated
"structured round-trip decode" (solved) from "predictive generation" (open) — this drill's contribution is
identifying that the SAME read-out mechanism is brain-correct for BOTH; what's missing for the predictive case
is not a new read-out primitive, it's mechanism 2 below to CONSTRUCT the plan vector when content is not yet
known.

**Sequencing vs. the native reader (barrier #1).** Read-out itself does NOT need the reader — it operates on
whatever plan vector already exists (already proven at exact_ordered=1.0 for known content). It DOES inherit
whatever fidelity the plan-vector-construction step (mechanism 2) achieves, so it is buildable and testable
NOW, but its ceiling is set by mechanism 2 / the encoder.

### Mechanism 2 (RANK 2 — the real lever): Hippocampal generative replay (recombination, not raw continuation)

**Brain mechanism + source signature.** Sharp-wave ripples (150-250Hz, CA1, driven by CA3 recurrent discharge)
reactivate place-cell sequences at ~10-20x compressed speed, forward or reverse. Pfeiffer & Foster, *Nature*
2013: at a choice point, decoded replay depicts full paths to a remembered goal **including start-goal
combinations the animal never directly traversed together** — the hippocampus composes a route from
independently-learned LOCAL segments before committing to move, and the composed sequence predicts the path
actually taken next. Mattar & Daw, *Nat. Neurosci.* 2018: replay content = a one-step Bellman backup applied to
a stored transition, with **priority = gain × need** (how much would updating this transition change behavior,
times how likely is this state to be needed soon) — reproduces known replay-content biases (reward
over-representation, reverse replay after reward, forward pre-run, shortcut replay). Schacter & Addis,
*Constructive Episodic Simulation*, 2007, and Hassabis & Maguire, *Scene Construction*, 2007: imagining a
novel future event works by **flexible recombination of elements of past (REAL, experienced) episodes** into
a new configuration, with the hippocampus providing the relational/spatial scaffold that makes the recombined
scene coherent — hippocampal amnesics cannot construct coherent novel scenes at all, not just recall old ones.
**Critically, "preplay" (composing sequences with NO experiential basis at all, Dragoi & Tonegawa) is
CONTESTED and the larger-population replication (Silva, Feng & Foster 2015) found chance-level pre-experience
trajectory events, abolished by NMDA blockade during actual experience** — genuine sequence-coding is
experience-dependent. The brain does not improvise from nothing; it recombines REAL, previously-stored local
fragments into novel global sequences.

**How it avoids noise-compounding.** This is content-addressed RECOMBINATION over a fixed associative store
(the same weights used for ordinary single-step completion), not step-wise accumulation of a running estimate.
Each candidate global sequence is composed, scored, and can be DISCARDED wholesale if it scores poorly — errors
don't propagate INTO the next step of the same trajectory because multiple whole trajectories are proposed and
compared, not extended one uncertain step at a time. This directly explains, for the first time in this
substrate's own history, WHY `PREDICT_RESIDUAL_TD` failed: it corrected a SINGLE forward-rolling online
estimate against its own TD-bootstrapped (i.e., self-referential, same source as the estimate it's correcting)
prediction — precisely the decision-feedback-equalizer failure class the noise-compounding law already proved
kills chains, not a new or substrate-specific mystery. The brain's actual antidote to "my forward guess might be
wrong" is never "run a deeper correction on the SAME rolling guess" — it is "propose several INDEPENDENT
candidate compositions (offline, before commitment) and pick by evaluation."

**Composition with already-operational pieces.** Directly reuses (a) the existing hetero-associative
`W_hetero` context→next-item store AS the fragment library (no new representation primitive — replay draws
candidate segments from the SAME weights used for ordinary single-step lookup); (b) the certified `combinedgate`
recency+content arbitration (v8, HARD_PASS) as the CANDIDATE-SCORING signal (does this candidate's next fragment
match content-relevance or only recency?); (c) `iterative_attractor` / `cleanup_family` as the completion
operator that turns a noisy retrieved fragment into a clean candidate item before it's scored; (d) the glass-box
reasoning loop's own retrieve→evaluate→(re-query or commit) shell (`research_neural_reasoning_loop_mechanism_
inventory_2026-07-08.md`) is LITERALLY this same architecture already scoped for reasoning — generation is not
a separate system to build, it is the SAME loop run in "propose several, score, commit one" mode instead of
"retrieve once, verify, done" mode. CLS-style consolidation is the natural sequencing partner: candidates that
get replayed/scored-well repeatedly should be cached as directly-retrievable chunks (schemas), shrinking the
online-composition burden over time — this is the same schema-consolidation lever already banked in
`research_reasoning_over_large_store_without_collapse_brain_first_2026-07-08.md`.

**Sequencing vs. the native reader.** PARTIALLY needs it. The fragment library (`W_hetero`) itself doesn't need
concept-recall fidelity beyond what it already has to propose candidates — genuinely testable now, on the
EXISTING 2nd-order trigram GPU cell + corpus, with zero new representation-building. But candidate SCORING
(does this candidate's content genuinely match the relevant part of the context, mechanism 3) inherits whatever
concept-recall ceiling the encoder currently has (~0.507) — so the CEILING on how well this mechanism can score
is barrier-#1-gated, even though the mechanism itself is buildable and testable today.

### Mechanism 3 (RANK 3 — already substantially de-risked, the sharpened crux): content-addressed PFC-BG output gating, generalized from explicit-tag to implicit-statistical relevance

**Brain mechanism + source signature.** O'Reilly & Frank 2006, PBWM: cortico-BG-thalamic Go/NoGo loops,
value-trained by dopaminergic RPE, gate WHAT enters and WHAT drives output from working memory, per independent
PFC "stripe." Chatham & Badre 2015: input-gating and output-gating are separable, partially-separate-locus
gates. The gating decision is a LEARNED expected-value comparison (trained by RPE), not raw novelty/salience.

**How it avoids noise-compounding.** It does not correct noise at all — it PREVENTS irrelevant content from
being admitted into the composition/accumulation process in the first place (selection, not denoising),
matching this substrate's own already-atomized finding (`CONTEXT_GATE selective-admission gating flattens...
the lever is SELECTION not renormalization`, MEASURED_MECHANISM, v5) and its complementary "correlation-hurts-
capacity" law (decouple store from retrieval; admission gating discards noise slots BEFORE they dilute the
superposition — admission acts EARLIER than denoise/residual, exactly why it beat CLEANUP and PREDICT_RESIDUAL
in the same v8 run).

**Composition + honest scope.** ALREADY PROVEN in isolation at three levels this cell family: v5 (recency-only,
MM, recency-optimal 1st-order regime), v6 (content-only via explicit query-key match, HARD_PASS, beats recency
when position is uninformative), v7 (content-only under realistic noise-corrupted cue, HARD_PASS, survives
q=0.08/snr=7.24), v8 (combined recency+content arbitration, HARD_PASS, correctly arbitrates per sub-regime).
**The honest remaining gap:** all four use an EXPLICIT tagged cue (`flag_id`) — a designed needle that the gate
is trained to match against an explicit query. Real higher-order language dependency has no such explicit tag:
"which prior token matters" must be inferred from LEARNED, GRADED, IMPLICIT co-occurrence structure (e.g., a
real trigram/skip-gram dependency where the informative token is identifiable only by what it predicts, not by
a marker). This is a strictly harder generalization — going from "find the token that matches this key" to
"find the token whose statistical relationship to the target is strongest, with no key at all" — and it is the
sharpest remaining open question in this entire inventory.

**Sequencing vs. the native reader.** Testing the generalization itself does NOT strictly need the reader (it
can be tested on progressively-less-explicit synthetic corpora before touching real text — see cheap decisive
test below). But its CEILING on real language is barrier-#1-gated: content-relevance inferred from co-occurrence
is only as good as the substrate's ability to recognize which concept a context slot actually holds.

### Mechanism 4 (RANK 4 — confirms an existing piece is already brain-correct, not a new build): discrete competitive lexical selection

**Brain mechanism + source signature.** Dell's interactive-activation model and Levelt/Roelofs/Meyer's WEAVER++
(spreading activation concept→lemma→phonology, COMPETITIVE selection resolves to one discrete lexical node per
output position). Speech-error evidence (mixed semantic+phonological errors) shows activation is graded and
continuous UP UNTIL the selection step, which is then discrete and competitive — each output word is a hard,
resetting choice among a FIXED external lexical inventory, not a continuously-evolving vector state carried
across words.

**How it avoids noise-compounding.** Each emitted symbol is a hard reset against the SAME fixed external
codebook (the lexicon) — structurally identical to the regenerative-repeater property already proven for
reasoning-depth (hard argmax decode against a fixed external key-slot codebook, zero residual carries forward
on success). This is not a new mechanism to build; it is confirmation that the substrate's EXISTING decode step
(hard argmax against a fixed codebook) is already the brain-correct final stage — the entire open problem is
upstream, in how the pre-decode context/plan representation is constructed (mechanisms 1-3), never in the
decode step itself.

**Sequencing.** No dependency either way — already built, already brain-aligned, nothing to change here.

### Mechanism 5 (RANK 5 — diagnosis, not a build lever): bounded-residual predictive coding explains WHY the deep antidote failed

**Brain mechanism + source signature.** Rao & Ballard 1999; Huang & Rao 2011 review: hierarchical generative
cortex, top-down PREDICTIONS, bottom-up RESIDUAL ERRORS ONLY — the residual is bounded because it is computed
against a jointly-trained, already-good generative model, and only the part the model didn't already explain
propagates. Friston's active-inference extension: the whole loop minimizes a bounded variational free-energy
functional, not an unbounded accumulating error.

**Why this substrate's residual antidote failed anyway.** The theoretical account requires the top-down
prediction to come from an INDEPENDENT, already-fitted generative model — but `PREDICT_RESIDUAL_TD` computed
its residual against `W_hetero`'s OWN online TD-bootstrapped prediction, i.e., against the SAME uncertain
estimator it was trying to correct. This is self-referential correction, the exact decision-feedback-equalizer
failure class already proven (this same week) to kill the waypoint verify-gate and the cerebellar SR-rollout.
Real predictive coding's bounded-residual property depends on the predictor being independently good, not on
running a correction against itself — this substrate's implementation never had that independence, so the
theoretical bound never applied. **This is a diagnosis, not a new build item**, but it retroactively resolves
what was previously reported as a bare empirical negative ("deep predict-residual failed, capped at concept-
recall ceiling") into a mechanistically-understood one, and it independently reinforces why mechanism 2
(propose SEVERAL independent candidates, not one self-corrected rolling estimate) is the right fix rather than
"try a better residual rule."

---

## 2. Cheap decisive test (single sharpest, buildable now, on the existing harness)

**Target: mechanism 2 (generative replay-then-select) vs. the two existing single-pass antidotes
(CLEANUP_PER_STEP, CONTEXT_GATE) AND a compute-matched redundancy-only control**, on the SAME already-GPU-proven
2nd-order trigram cell / corpus (`exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu.py` family) — no new
corpus, no new codebook.

**Design sketch (exp_dev authors the exact implementation; this is a mechanism sketch, not a spec):**
1. At each generation step, instead of extending ONE rolling context estimate, propose R independent candidate
   next-fragments by sampling from `W_hetero` with a gain×need-style priority (candidates weighted toward
   transitions that would most change the current best guess AND are most likely to be needed given the
   current context — the Mattar-Daw structure), not uniformly at random.
2. Score each candidate using the certified `combinedgate` content-relevance-vs-recency arbitration signal
   (already HARD_PASS, v8) plus an `iterative_attractor` cleanup-confidence check.
3. Commit the top-scored candidate; do NOT accumulate the rejected candidates into any running state (this is
   the load-bearing structural difference from every prior attempt — nothing carries forward except the single
   committed choice).
4. **The control that makes this a real test, not a redundancy illusion:** a RANDOM-restart-matched-compute arm
   that proposes the same R candidates with the SAME sampling noise but NO gain×need prioritization and NO
   combinedgate scoring (uniform random pick among the R). This isolates whether any win comes from genuine
   content-relevance-scored recombination (brain-favored) versus mere ensemble-averaging/redundancy (already
   shown NOT to work for the resonator's K4 case per the noise-compounding law's own pending test, and directly
   analogous to that same open test — both should be run together, same harness).

**HARD-PASS:** replay-then-select beats CLEANUP_PER_STEP/CONTEXT_GATE by ≥0.3 bits at K≥3, AND beats the
RANDOM-restart-no-scoring control by ≥0.2 bits (proving the win is the content-relevance-scored recombination,
not bare redundancy), AND the advantage GROWS (not shrinks) with K, AND holds across ≥3 seeds with CV≤0.15.

**HARD-FAIL:** performance is statistically indistinguishable from the RANDOM-restart control (redundancy alone
explains any gain — not a brain-specific mechanism), OR candidates collapse onto the same 1-2 outputs regardless
of prioritization (proves `W_hetero` itself is too degenerate/low-capacity to support genuine multi-candidate
composition — a barrier-#1/encoder-capacity finding, not a replay-mechanism finding), OR it fails to beat
CLEANUP_PER_STEP/CONTEXT_GATE outright.

**MIDDLE:** beats RANDOM-restart but not by the full margin, or helps only at low K — informative partial
result, route to mechanism-3's generalization test (below) as the next lever rather than force-fitting a verdict.

**Companion test for mechanism 3 (the sharper crux, cheaper, do first or in parallel):** re-run the v6/v7
content-gate harness with the explicit `flag_id` tag REMOVED and replaced by a GRADED, implicit statistical
dependency (e.g., a real skip-bigram/trigram co-occurrence signal computed from the SAME corpus, no explicit
marker) as the thing the gate must learn to key on. **HARD-PASS:** content-gate still beats the recency-cap
and the content-blind cap on this implicit-cue corpus (proves the mechanism generalizes past explicit-tag
retrieval to true statistical relevance). **HARD-FAIL:** content-gate collapses to chance or to the recency
baseline once the explicit tag is removed (proves v6/v7/v8's win was retrieval-specific, not a general
relevance-learning capability) — this would be the single most important negative in this whole inventory,
because it would mean the "first positive on Stage-4 attention-routing" needs a fundamentally different
learning signal, not just a harder corpus.

---

## 3. Sequencing table (what needs the native reader first vs. buildable now)

| Mechanism | Buildable now? | Ceiling gated by barrier #1 (encoder)? |
|---|---|---|
| 1. Competitive-queuing whole-sequence readout (peel/SIC) | YES — already proven for known content (exact_ordered=1.0) | Only via mechanism 2's plan-vector quality |
| 2. Hippocampal generative replay (propose-score-commit) | YES — reuses `W_hetero`, `combinedgate`, `iterative_attractor`; zero new representation primitive; the cheap decisive test above runs on the EXISTING cell | Candidate-SCORING ceiling only, not candidate-proposal |
| 3. Content-gate generalization (explicit-tag → implicit statistical relevance) | YES for the companion test (synthetic implicit-cue corpus); real-corpus ceiling depends on encoder | YES on real language — content-match quality bounded by concept-recall (~0.507) |
| 4. Discrete lexical competitive decode | Already built/proven, no dependency | No — this stage is already brain-correct |
| 5. Bounded-residual predictive coding (diagnosis) | N/A — explains a landed negative, not a build item | N/A |

**Bottom line on sequencing:** mechanisms 1, 2, and the mechanism-3 companion test are ALL startable now, on
existing GPU harnesses, with zero new corpus or codebook work — none of them are blocked on the native reader
landing. Only the CEILING on real-language performance (not the ability to run and learn from the tests) is
gated by barrier #1. This matches, and extends, the `research_stage4_generation_load_bearing_gap_and_gpu_probe_
2026-07-07.md` framing: generation is entangled with representation fidelity, but is not blocked from useful,
decisive experimentation today.

---

## 4. Honest priors (calibration penalty applied per [[feedback-lit-scan-calibration-penalty]])

- **Mechanism 1 (CQ readout generalizes to predictive use once a plan vector exists):** raw ~0.55 (well-
  precedented; the substrate's own frame-slot decoder already proves the read-out half at exact_ordered=1.0)
  → **P_deflated ~0.35** (uncertainty is almost entirely in mechanism 2's plan-vector quality, not in this
  step itself).
- **Mechanism 2 (generative-replay-then-select clears the cheap decisive test's HARD-PASS bar):** raw ~0.35-0.40
  (well-motivated, converges independently with the SAME-DAY resonator-redundancy test and the sibling deep-
  chain-reasoning drill's own "generate-then-select" recommendation — genuine, not manufactured, convergence)
  → **P_deflated ~0.20-0.25**, capped at 0.50 under the mandatory novel-synthesis rule regardless of raw
  confidence.
- **Mechanism 3 (content-gate generalizes from explicit-tag to implicit statistical relevance, the sharpest
  crux):** raw ~0.30-0.35 (genuinely the least-precedented step in this inventory — no existing cell has tested
  it, and the substrate's own concept-recall ceiling is an independent, documented risk to any implicit-relevance
  signal) → **P_deflated ~0.15-0.20**.
- **Mechanism 5 diagnosis (self-referential correction, not bounded-residual predictive coding, explains the
  PREDICT_RESIDUAL_TD failure):** raw ~0.65-0.70 (directly matches an already-proven, disk-verified mechanism
  class from the SAME-WEEK noise-compounding drill — `retry_rate_combo=0.0` is a hard, quantitative precedent
  for the self-referential-correction failure signature) → **P_deflated ~0.45-0.50** (highest confidence item in
  this note, still capped at 0.50 per rule).

---

## 5. Cross-thread synthesis

- Directly extends and re-scopes `research_stage4_generation_load_bearing_gap_and_gpu_probe_2026-07-07.md`
  (structured-decode vs. predictive-generation split retained; this note supplies the brain-grounded mechanism
  for the predictive half specifically).
- Directly explains, for the first time, WHY `research_brain_predictive_generation_predict_residual_build_spec_
  2026-07-07.md`'s deep antidote failed — not a standalone puzzle, an instance of the self-referential-
  correction failure class from `research_noise_compounding_bound_deep_mechanism_2026-07-07.md`.
- Directly reuses the CONTEXT_GATE / CONTENT_GATE / COMBINED_GATE cell family (v5-v8, all landed this cycle) as
  ALREADY-PROVEN building blocks, correcting the task's framing that content-dependent gating was untested —
  it is proven at the explicit-tag level; the sharper, still-open question is generalization to implicit
  statistical relevance, which this note names precisely and gives a cheap test for.
- Converges independently, same day, with `research_deep_chain_reasoning_bounded_compounding_error_brain_first_
  2026-07-08.md`'s "replay-generate-then-select" recommendation for a DIFFERENT compounding-error target
  (waypoint chains) — two independent drills, two independent substrate failures, one brain mechanism (SWR
  replay) as the common fix. This is a structural, not coincidental, convergence: both targets share the same
  underlying pathology (self-referential online correction of a single rolling estimate).
- Composes directly with `research_neural_reasoning_loop_mechanism_inventory_2026-07-08.md`'s minimal loop —
  generation is not a separate architecture to design; it is the SAME retrieve/replay/gate/commit loop already
  scoped for reasoning, run in "propose several, score, commit one" mode.
- Reconciles with `reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08` —
  admission gating (mechanism 3) discards noise/correlated slots BEFORE they dilute the superposition, acting
  earlier in the pipeline than denoise/residual (mechanisms already shown to only partially work).

## 6. Substrate-product implications

- No overclaim: this note does not promote any cap_map row. It proposes one buildable, cheap, decisive
  experiment (mechanism 2) that reuses existing certified pieces with zero new representation-building, plus
  one sharpened companion test (mechanism 3's implicit-relevance generalization) that directly targets the
  crux the task named.
- If mechanism 2 clears HARD-PASS: the substrate gains a brain-grounded, glass-box-inspectable (each candidate
  and its score are individually auditable — literally what "glass-box" requires) generative primitive that
  composes FOUR already-proven pieces (W_hetero, combinedgate, iterative_attractor, peel/SIC readout) with no
  new architecture, and it would be the first mechanism in this substrate's history to beat the noise-
  compounding failure by STRUCTURAL REMOVAL of the accumulator rather than by patching it.
- If mechanism 2 HARD-FAILs against the random-restart control: this is exactly as valuable — it would prove
  the substrate's `W_hetero` fragment store lacks the diversity/capacity to support genuine multi-candidate
  composition, sharpening the barrier-#1 encoder problem into a specific, falsifiable, previously-untested
  claim about associative-store capacity rather than a vague "representation fidelity" concern.
- If mechanism 3's companion test HARD-FAILs (content-gate collapses without the explicit tag): this is the
  most consequential possible negative in this note — it would mean the "first positive on Stage-4 attention-
  routing" (v5-v8) does not generalize past explicit-tag retrieval, redirecting the entire content-gating
  program toward a different learning signal before any further investment.

## Citations (verified count)

**Fresh external sources, verified via WebSearch this cycle (generic neuro/cognitive-science terms only, per
query-privacy discipline), 9 searches, distinct primary sources identified:**
1. Rao & Ballard, "Predictive coding in the visual cortex," *Nat. Neurosci.* 1999 (via Huang & Rao 2011 review,
   homes.cs.washington.edu/~rao/predcoding2011.pdf).
2. Friston, free-energy-principle / active-inference synthesis (multiple 2019-2024 reviews cross-checked).
3. Schacter & Addis, "Constructive episodic simulation of the future," *Phil. Trans. R. Soc. B* 2007.
4. Hassabis & Maguire, "Deconstructing episodic memory with construction," *Trends Cogn. Sci.* 2007 (scene
   construction hypothesis).
5. Dell, interactive-activation model of lexical access in speech production (Dell, Nozari & Oppenheim review,
   oppenheim-lab.bangor.ac.uk).
6. Levelt, Roelofs & Meyer, WEAVER++ model of word production (LRM model, competitive lexical selection).
7. O'Reilly & Frank, "Making Working Memory Work," *Neural Computation* 2006 (PBWM, ccnlab.org/papers/
   OReillyFrank06.pdf).
8. Chatham & Badre 2015, separable input/output gating loci (carried from same-day reasoning-loop drill,
   re-confirmed present in this cycle's search results).
9. Grossberg 1978; Houghton 1990; Bullock & Rhodes 2003; Kornysheva et al., "Neural Competitive Queuing of
   Ordinal Structure Underlies Skilled Sequential Action," *Neuron* 2019 (PMC6436939) — competitive-queuing
   serial-order model.

**Carried, re-verified against fresh on-disk reads this cycle (not re-fetched externally, per drill
discipline):** Pfeiffer & Foster 2013; Mattar & Daw 2018; Silva, Feng & Foster 2015; Dragoi & Tonegawa (all
from `research_neural_reasoning_loop_mechanism_inventory_2026-07-08.md`, itself sourced from 5 independent
Sonnet lit-scans, 62 total citations); Ross & Bagnell 2010/2011; Duttweiler-Mazo-Messerschmitt 1974 (from
`research_noise_compounding_bound_deep_mechanism_2026-07-07.md`).

**Internal artifacts freshly re-read off-disk this cycle (load-bearing, not carried from memory):**
`data/exp_substrate_gen_lm_contextgate_depth_v5_n8192_gpu/metrics.json`; `data/exp_substrate_gen_lm_
contentgate_flagdep_v6_n8192_gpu/metrics.json`; `data/exp_substrate_gen_lm_contentgate_noisycue_v7_n8192_gpu/
metrics.json`; `data/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu/metrics.json` (verdict_msg
and per_seed structure read directly, including gate_log internals confirming synthetic explicit-tag corpus
structure via `flag_id`/`build_slot_codes`/`content_gate_codes` in `experiments/exp_substrate_gen_lm_
contentgate_noisycue_v7_n8192_gpu.py`); `tools/_skunkworks_atomize_2026_07_08_contextgate_depth_v5_
CONTEXT_GATE_MEASURED_MECHANISM.py` (full landed-VET record, off-disk recompute numbers).

**Total: 9 fresh external primary-source lines (verified via WebSearch this cycle) + ~8 carried/re-verified
external sources (from same-day sibling drills, not re-fetched, per 2x-drill discipline) + 5 fresh on-disk
artifact re-reads = 22 verified sources/checks.**
