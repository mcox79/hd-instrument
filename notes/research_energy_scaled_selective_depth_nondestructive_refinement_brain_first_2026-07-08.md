# Research Drill (5x-revival, brain-first): Non-Destructive Energy-Scaled Selective-Depth Refinement (2026-07-08)

**Author:** Research (Sonnet)
**Trigger:** USER-directed 5x-revival brain-grounding drill on a CONFIRMED GENUINE negative (skunkworks-
confirmed, not a design-failure): the PHASE-TRAVERSAL CONDENSER cell
(`experiments/exp_encoder_phase_traversal_spread_condense_v1.py`) HARD_FAILED with
`structural_gain = -0.348` (condensed read WORSE than raw static read) because the store code
`s = WTA_topk(x @ W_up)` is a hard sign+top-k quantization that discards magnitude/sub-threshold
information a later condense-time fine read needs, and that information is not recoverable downstream.
Skunkworks confirmed this specifically via the cell's own `phase_traversal_dense` arm (condense off the
NON-sparsified dense code) reaching `SC = 0.993` (near-oracle) -- i.e. the trained condenser itself works
perfectly; the entire loss is the discontinuity of the sign+top-k quantization applied BEFORE condensation.
A rescue cell is already in flight (`exp_encoder_phase_traversal_graded_sparse_rescue_v1.py`, magnitude-
graded top-k sweep, gamma in [0,1]) testing whether SOFTENING the hard threshold rescues both properties
from one code.
**Method:** brain-first deep dive. 4 parallel Sonnet lit-scan sub-agents (separate framework angles: visual
coarse-to-fine, hippocampal progressive retrieval, information-theoretic successive-refinement math,
effort/precision neuromodulation), generic scientific terms only, no substrate-internal names or numbers
sent off-platform, per [[feedback-query-privacy-decomposition]]. Synthesis grounded against direct on-disk
reads of both phase-traversal cell docstrings (v1 negative + rescue-in-flight) and the prior gating note.
**Calibration:** per [[feedback-lit-scan-calibration-penalty]], all P estimates below are deflated 0.15-0.25
from raw confidence; novel-synthesis claims are capped at P<=0.50. Per [[feedback-brain-grounding-drills-
lead-with-deep-biology-ml-not-the-guide]], biology leads; ML (BranchyNet/cascade retrieval, EZW/SPIHT) is
cited only as a weak secondary confirmation, never as the design target.

---

## HEADLINE

**The brain does not have this problem because it never does what the substrate cell did: it never
builds its "coarse" representation BY DESTROYING the fine one. Every non-destructive coarse-to-fine
mechanism found across four independent literatures (vision, hippocampus, information theory, effort
control) resolves to exactly ONE of two structural moves -- (1) KEEP THE FULL TRACE AND ONLY TAP A CHEAP
PROJECTION OF IT (parallel channels, sparse index-to-untouched-trace, graded/distributed population
codes), or (2) MAKE THE COARSE CODE A PROVABLE MARKOV-DEGRADED FUNCTION OF THE FINE CODE (progressive/
successive-refinement coding, where refining APPENDS residual detail rather than re-deriving from a
lossy summary). Hard sign+top-k quantization does neither: it is a genuinely non-invertible, information-
theoretically floored map (proven for 1-bit/top-k quantization specifically) with no retained residual and
no parallel intact channel -- so no downstream operator, however well-trained, can recover what it threw
away. This is exactly what the substrate's own `phase_traversal_dense` arm already proved empirically
(SC=0.993 when NOT sparsified first) before this drill ever ran. The single highest-probability-superior,
near-zero-new-mechanism fix is the direct biological analog of hippocampal indexing theory: never ask the
destroyed sparse code to yield fine information it doesn't have -- retain (or cheaply recompute) the intact
source for the coarse-filtered shortlist only, and run the ALREADY-WORKING condenser on THAT, not on the
sparse code.**

P_deflated(hard sign+top-k quantization is information-theoretically non-invertible in a way the brain's
coarse-to-fine mechanisms structurally avoid -- i.e. the wall is general, not an artifact of this specific
condenser) = **0.75** (three independent literatures -- rate-distortion successive-refinement theory,
1-bit/top-k compressed-sensing floors, and biological parallel-channel/graded-population evidence --
converge on the identical structural diagnosis; deflated from ~0.90 because the substrate's own single
measured counter-example, `phase_traversal_dense` at 0.993, is doing most of the empirical lifting and the
general claim beyond that one cell is still an inference).
P_deflated(retained-trace re-query on the coarse-filtered shortlist recovers phase_traversal_dense-level SC
at a fraction of phase_traversal_dense's O(V) cost, i.e. mechanism A below is a real, near-zero-new-code
fix) = **0.50** (capped novel-synthesis; the condensability half is already MEASURED at 0.993, but the
shortlist-gating half is untested, same caveat as the prior gating note).
P_deflated(a bounded residual-sketch code, mechanism C below, closes most of the gap to dense_condense at
materially less storage than retaining the full dense code) = **0.40** (capped; theoretically clean via the
Equitz-Cover successive-refinement condition, but no on-disk measurement exists for this substrate's
condenser under partial-residual reconstruction).

---

## Part 1 -- The brain mechanism, four independent angles

### 1a. Visual cortex: coarse-to-fine is PARALLEL CHANNELS priming an intact fine trace, not sequential destruction

Bar et al. (2006, PNAS; 2007, J. Neurosci.) show a fast, low-spatial-frequency ("gist") signal is shunted
via the magnocellular pathway to orbitofrontal cortex ~50ms before the slower high-spatial-frequency
parvocellular-driven fine analysis completes, and is fed BACK to bias/prime the still-arriving fine
analysis -- it does not overwrite or consume it. Hochstein & Ahissar's Reverse Hierarchy Theory (Neuron,
2002; TICS, 2004) requires, as a load-bearing premise, that lower-level fine-grained representations
REMAIN INTACT and available for later top-down access; the theory would be falsified if a later descent
found the detail already gone. Predictive-coding precision-weighting (Rao & Ballard lineage) is the one
mechanism in this literature that is architecturally AMBIGUOUS on this point -- precision is a gain/
attentional multiplier on prediction-error units, and no source found directly states whether low-precision
(not-yet-predicted fine) information is erased vs. merely down-weighted; treat this thread as unresolved,
not as evidence either way. **Verdict: the best-evidenced visual mechanisms are non-destructive by
construction (parallel intact channel + priming), not by luck.**

### 1b. Hippocampus: two DIFFERENT non-destructive strategies, not one

Two structurally distinct non-destructive mechanisms coexist in the hippocampal literature, and it matters
which one the substrate's fix resembles:
- **Graded settling** (CA3 attractor dynamics, Rolls 2013; cue-morph physiology, Leutgeb line): retrieval is
  gradient descent through an energy landscape where intermediate states are genuine graded waypoints
  (distance-to-attractor is itself information, extractable by continuing the dynamics) -- moderate
  confidence; some morph studies show more discrete jumps far from the basin, so this may hold near the
  boundary and degrade to steplike behavior far from it (a live, unresolved empirical debate, not settled).
  Theta phase precession (O'Keefe & Recce 1993; Skaggs et al. 1996) is a related but architecturally
  DIFFERENT non-destructive trick: coarse (current-position) and fine (trajectory) information are carried
  by DIFFERENT ensembles at different phases of the SAME theta cycle -- multiplexing across phase, not
  iterative refinement of one shared state. Well-established, highly replicated.
- **Architectural separation** (hippocampal indexing theory, Teyler & Rudy 1986/2007): the hippocampus
  stores ONLY a sparse orthogonalized INDEX/pointer; the full, fine-detail trace is preserved SEPARATELY in
  neocortex, untouched. This is the strongest, most direct biological analog to "coarse pointer and fine
  content are physically different objects, not the same object at different quantization levels" -- well-
  established as a computational-level framework with substantial supporting lesion/replay evidence, though
  it remains a computational abstraction rather than a fully mechanistic circuit proof.
Signal-detection strength models (Wixted's UVSD; Yonelinas familiarity/recollection) show recognition
memory itself is graded/continuous rather than quantized, but describe a single-shot readout, not a
within-trial iterative-refinement account -- a separate, weaker point that does not itself resolve the
non-destructiveness question.

### 1c. The precise mathematical condition for non-destructive refinement, and why hard top-k+sign breaks it

Equitz & Cover (1991, IEEE Trans. IT, "Successive Refinement of Information") prove that a coarse code can
ALWAYS be losslessly extended to a finer one at the jointly-optimal rate **if and only if** the coarse
reconstruction is a Markov-degraded FUNCTION of the fine reconstruction (`X - Xhat_fine - Xhat_coarse` forms
a Markov chain) -- i.e. the coarse code must be literally DERIVABLE FROM the fine one (a projection/subset),
not an independently-thresholded second estimate. This holds for Gaussian sources under squared error and
discrete sources under Hamming distortion, but is known to FAIL for some source/distortion pairs -- it is a
structural condition to verify, not a free guarantee. Embedded wavelet coding (EZW/SPIHT) satisfies this
condition by literal construction: coefficients are transmitted in magnitude order, so any coarse-rate
codeword is a strict PREFIX of the full one, and refining only ever APPENDS bits. **Hard top-k + sign
quantization violates this condition on both counts**: it discards sub-threshold coordinates entirely (no
residual retained anywhere) and collapses surviving coordinates to sign only (proven ~pi/2 SNR floor for
1-bit quantization at low SNR; 1-bit compressed sensing can recover only support/sign, never amplitude, from
sign(y) alone -- an information floor, not an algorithmic shortfall). Real neural population codes,
empirically, tend to be graded/distributed and redundant rather than quantized -- "winner-share-all"
readouts materially beat winner-take-all for information capacity, and WTA-only readouts cannot account for
measured perceptual precision. **This is the sharpest, most quantitative confirmation of the wall**: the
substrate's `s = sign(z) restricted to top-k` is precisely the mathematically-floored case Equitz-Cover and
1-bit-CS theory both name, and precisely the case biological population codes appear to avoid by staying
graded/distributed.

### 1d. Effort/depth allocation is LOCAL AND REFLEXIVE; global neuromodulatory systems only retune the criterion

LC-norepinephrine adaptive gain (Aston-Jones & Cohen 2005) and ACh precision-weighting (Yu & Dayan 2005;
Feldman & Friston 2013) operate as SLOW, aggregate-state dials (tonic/phasic arousal mode, "expected
uncertainty" tracked over trial history) -- gain/criterion setters, not per-item content-selection
computations. The dorsal ACC / Expected Value of Control framework (Shenhav, Botvinick & Cohen 2013)
explicitly integrates payoff, control cost, and effort into an aggregate allocation signal over task/trial
epochs, not within a single retrieval act. By contrast, familiarity directly and locally gates recollection
onset with no separate arbiter (Yonelinas dual-process ERP evidence), and metacognitive fluency/feeling-of-
knowing signals (Koriat) directly and automatically gate continue-vs-stop search decisions at the retrieval
site itself, with only their CRITERION set by slower aggregate history. Calibrated confidence on this exact
two-timescale split: ~0.55 (architecturally coherent and consistent with every source found, but assembled
from separately-studied literatures rather than a single unified test).

---

## Part 2 -- The mechanistic contrast, stated precisely

The brain's coarse read is never the SAME representation as the fine read, subsequently damaged by
quantization. It is always one of:
- a cheap PARALLEL projection of an intact underlying signal (magno/parvo; index/cortical-trace), or
- a genuinely graded/continuous readout of a shared substrate that has not been collapsed (CA3 attractor
  distance; population-vector pooling), or
- a temporally-multiplexed READOUT of different information from the same trace at different moments
  (theta phase), or
- a formally Markov-degraded PROJECTION of a fine code that is provably losslessly refinable (EZW-style
  embedded coding, the Equitz-Cover condition).

Hard sign+top-k is none of these. It THROWS AWAY the sub-threshold coordinates and the sign-collapsed
magnitude information, with no retained residual, no parallel channel, and no Markov relationship to the
original -- it is drawn from exactly the class of quantizers that information theory proves cannot be
undone by a downstream decoder, however well-trained. The substrate's own `phase_traversal_dense` result
(0.993 when the condenser is run on the UN-quantized code) is the direct empirical confirmation: the
condenser was never the bottleneck; the quantization step was.

---

## Part 3 -- Ranked shortlist of buildable substrate mechanisms

### Mechanism A (top pick): Retained-trace re-query -- "index, don't invert"

**(a) Brain mechanism + source signature.** Hippocampal indexing theory (Teyler & DiScenna 1986; Teyler &
Rudy 2007, Hippocampus 17(3), PMID 17696170): the hippocampus stores only a sparse orthogonalized INDEX; it
never attempts to reconstruct fine content FROM the index. Fine content lives in a separately-preserved,
untouched cortical trace, queried directly when needed.

**(b) How it preserves the residual for a later deeper read.** Trivially -- there is no residual to
preserve because the fine representation was never destroyed. Mapped onto the substrate: keep `s =
WTA_topk(z)` as the cheap coarse code used for superposition (SP) AND coarse ranking (the existing
`spread_static` cosine, exactly as in the prior gating note); but for the FINE read, never condense `s` --
condense the RETAINED (or cheaply recomputed) dense `z` for the coarse-filtered shortlist only. This is not
a new mechanism to build: it is already MEASURED on disk. The v1 cell's own `phase_traversal_dense` arm is
literally this operation (condense off dense `z`, no WTA first) and it reached SC=0.993. The only new piece
is restricting that already-working operation to a coarse-ranked top-k shortlist instead of all V, for
compute savings -- an evaluation-order change, not a new trained component.

**(c) Composition.** Identical shape to the prior gating note's Part 4/5: the coarse `spread_static` cosine
(cheap, computed over the full V-item store) is the LOCAL, reflexive, per-item confidence signal (per Part
1d -- familiarity-style, no separate arbiter); it both (i) feeds the shortlist-selection step here and (ii)
is architecturally the same primitive the combinedgate cell already computes for its WHICH-slot decision
(`content_rel_j`), so the two composition points (WHICH slot, HOW FINE to read it) can plausibly share one
margin signal. The self-manager aggregate-threshold dial retunes ONLY the shortlist size k (the aggregate
compute budget for "how many candidates get the expensive retained-trace re-query this cycle") -- matching
Part 1d's finding that neuromodulatory/effort systems retune criteria over aggregate state, never make the
per-item call themselves.

**(d) Honest prior + kill test.** The condensability half is not a prediction -- it is a fact already on
disk (0.993). The shortlist-gating half is deflated to P=0.50 (capped, novel synthesis) because it is
untested. **Kill test:** using the v1 cell's already-collected artifacts, rank all V items by
`spread_static` coarse cosine, and measure the SHORTLIST HIT RATE -- the fraction of queries where the true
nearest concept under the DENSE condensed ranking is actually inside the coarse top-k -- at k = 0.05V,
0.10V, 0.25V. HARD-FAIL if hit rate stays below 0.70 even at k=0.25V (the coarse and dense-condensed
geometries are too decoupled for staged retrieval to help, independent of the quantization-wall finding).
**Honest caveat:** this mechanism trades compute for MEMORY -- retaining dense `z` per item costs O(V*N)
instead of the sparse code's O(V*k); this is fine at the substrate's current V but should be flagged as a
scaling cost, not assumed free at much larger V (motivating mechanism C below).

### Mechanism B (already in flight, partial support): Graded/soft top-k

**(a) Brain mechanism + source.** Distributed/graded neural population coding -- "winner-share-all" pooled
readouts materially outperform winner-take-all for information capacity (population-coding literature); CA3
graded attractor settling (Rolls 2013; Leutgeb-line cue-morph physiology) shows partial/intermediate states
carry real, usable graded information near the basin boundary.

**(b) How it preserves residual.** Partially. Magnitude-gradedness (`code_i = sign(z_i)*|z_i|^gamma` on the
top-k support) softens the sign-collapse discontinuity as gamma -> 1, approaching the Equitz-Cover Markov
condition on the RETAINED support -- but sub-threshold coordinates outside the top-k support are still
hard-zeroed regardless of gamma, so this only ever partially satisfies non-destructiveness. This matches
exactly what the substrate's own rescue cell (`exp_encoder_phase_traversal_graded_sparse_rescue_v1.py`)
frames as an open EMPIRICAL TENSION (decorrelation-for-SP vs. condensability-for-SC), not a guaranteed fix
-- the brain literature corroborates that this is a genuine, not obviously resolved, tradeoff (CA3 morph
studies themselves show graded-vs-discrete behavior split by distance from the attractor).

**(c) Composition.** Same shape as A; self-manager would retune the aggregate gamma operating point (how
graded the store code is, substrate-wide) rather than deciding gradedness per item.

**(d) Honest prior + kill test.** P_deflated=0.35-0.40 that some gamma in (0,1) clears BOTH pre-registered
bars (SP_HI=0.83, SC_HI=0.90, structural_gain>=0.15) -- this is the cell's own live pre-registered question,
not a new proposal from this drill; its own HARD-FAIL criterion (no gamma beats its own static readout) is
already the correct kill test and should not be duplicated here.

### Mechanism C (flagged HIGH-PROBABILITY-SUPERIOR, NEW): Bounded residual-sketch code

**(a) Brain mechanism + source.** The formal generalization of 1a/1c's parallel-channel and Markov-
degraded-projection evidence into an explicit engineering construction: Laplacian-pyramid-style predictive
residual coding (predict coarse, retain only the residual needed to reconstruct fine) and embedded wavelet
coding (EZW/SPIHT: coarse = retained coefficient subset, refine = append residual detail coefficients) --
both satisfy the Equitz-Cover Markov condition BY CONSTRUCTION, and both are the direct formal generalization
of what hippocampal indexing theory does at the systems level (mechanism A) down to the level of a single
vector's bit budget.

**(b) How it preserves residual.** By explicit construction, not by luck: store the cheap sparse coarse
code `s` (for SP, as today) PLUS a SMALL fixed-budget residual sketch `r` (e.g. the next-largest-k
coordinates by magnitude, or a random-projection sketch of `z - reconstruct(s)`) such that `s + r`
reconstructs `z` closely enough for the trained condenser (already proven to work perfectly on true dense
`z`, per `phase_traversal_dense`) to recover near-oracle SC. This is DISTINCT from mechanism A: it is the
memory-bounded variant -- instead of retaining the FULL dense `z` (O(N) per item), it retains only enough
residual to close most of the gap (a tunable O(k) to O(2-3k) budget), directly answering mechanism A's
honest storage-cost caveat. This is the one candidate in this shortlist that is genuinely NEW (no existing
arm on disk measures it) and theoretically the cleanest (it is the only mechanism that satisfies the
Equitz-Cover condition exactly, rather than approximately or by a different route).

**(c) Composition.** Identical local-reflexive-gate + self-manager-retunes-aggregate-budget shape as A/B;
here the self-manager's aggregate dial is the RESIDUAL SKETCH SIZE (how much extra budget per stored item
to spend on future fine-readability), a genuinely new knob distinct from shortlist-size-k in A.

**(d) Honest prior + kill test.** P_deflated=0.40 (capped; theoretically well-grounded, but zero on-disk
measurement for this substrate's specific condenser and residual construction). **Sharpest kill test:**
sweep residual-sketch size `r_k` as a fraction of the full dense width N (e.g. r_k in {0, k, 2k, 4k, N}, with
r_k=0 recovering the confirmed hard-negative and r_k=N recovering the confirmed 0.993 dense ceiling);
HARD-FAIL if the SC-vs-r_k curve is NOT smoothly graded -- i.e. if even r_k=N/2 fails to close within 0.05
of the dense_condense ceiling, that would show the condenser's recoverability is closer to all-or-nothing
than smoothly graded in retained information, which would undermine the entire "partial residual buys
partial fidelity" premise this mechanism depends on (and would also cast some doubt on mechanism B's
gradedness premise, since both rely on the same graded-recoverability assumption from different angles).

### Mechanism D (not new -- brain-grounding confirmation of an existing alternative): Parallel two-head channels

**(a) Brain mechanism + source.** Bar et al.'s magnocellular/parvocellular PARALLEL pathway evidence: coarse
and fine are never one signal quantized into another -- they are separate projections of the same input,
computed in parallel, both intact.

**(b)/(c)/(d).** This is structurally the substrate's ALREADY-BUILT two-head decoupled-store-retrieval cell
(referenced in the v1 docstring as the prior solution this cell was trying to improve on with a single
code). No new work is proposed here; the point of flagging it in a brain-first drill is that the brain's
OWN best-evidenced parallel-channel solution is architecturally the two-head cell, not a single traversed
code -- so if A/B/C do not close the gap, the honest, brain-grounded fallback is not a failure state, it is
the biologically-modal answer. Per [[feedback-dont-frame-baselines-as-ceilings]], this is not framed as a
ceiling -- A and C both remain live bets that a single traversed code CAN work, brain evidence just says
"don't be surprised or discouraged if it doesn't, because the brain itself usually doesn't do it that way
either."

---

## Cheap decisive test (aggregate, across mechanisms)

All three live/new mechanisms (A, B, C) can be evaluated on data that already exists or is already in
flight, with NO new cell required for the first pass on A:

1. **Mechanism A (immediate, zero new cells):** re-analyze the v1 cell's already-collected artifacts.
   Rank all V items by `spread_static` coarse cosine; take top-k (k=0.05V, 0.10V, 0.25V); within that
   shortlist, look up the ALREADY-COMPUTED `phase_traversal_dense` condensed ranking (no re-run needed --
   this arm already exists in the v1 output) and check whether the true nearest concept is captured.
2. **Mechanism B (already in flight):** let the graded-sparse-rescue cell land; read its gamma sweep
   directly against ITS OWN pre-registered bars.
3. **Mechanism C (needs one new, cheap cell):** a residual-sketch sweep cell, reusing the v1 cell's harness
   verbatim (same metrics, same store/dictionary), varying only `r_k` as described above. Class (a)
   CPU-batched smoke feasible; this is a controlled add-on to an existing harness, not a new architecture.

---

## Falsifiable predictions

**HARD-PASS** (mechanism A, the top pick, is a real near-zero-new-code fix worth shipping into the
phase-traversal read path):
- Shortlist hit rate (true dense-condensed nearest-neighbor inside the `spread_static` coarse top-k) is
  >= 0.85 at k <= 0.10*V, AND
- Retained-trace re-query SC@alpha_OP on that shortlist is within 0.03 of the full `phase_traversal_dense`
  SC@alpha_OP (0.993 ceiling) -- i.e. gating to a shortlist costs negligible accuracy relative to the
  already-confirmed dense ceiling.

**HARD-FAIL** (mechanism A does not transfer cheaply; the coarse and dense-condensed geometries are too
decoupled for staged retrieval to help here):
- Shortlist hit rate stays below 0.65 even at k=0.25*V -- meaning the coarse WTA-sign ranking (used for
  SP/superposition) is nearly uncorrelated with the fine dense-condensed ranking (used for SC), so a
  coarse-first filter cannot safely gate the expensive-but-working fine read at any useful shortlist size.
  This would be a genuinely new, interesting negative distinct from the original quantization-wall finding
  -- it would say the TWO GEOMETRIES (sparse-for-SP vs. dense-for-SC) are close to orthogonal, not just that
  quantization loses magnitude information within one geometry.

**MIDDLE:** shortlist hit rate lands in [0.65, 0.85) at k=0.10*V -- gating helps directionally but needs a
larger k, a better coarse ranking signal (e.g. the existing `topk_mag`/graded-code cosine instead of raw
`wta_sign`), or a hybrid of mechanisms A and B (graded coarse ranking + retained-trace fine read).

---

## Cross-thread synthesis

- **`research_energy_scaled_selective_depth_retrieval_coarse_to_fine_2026-07-08.md`** (same-day prior
  drill): that note proposed shortlist-GATING the condenser (run it on fewer items) but implicitly assumed
  the condenser would still run on the SPARSE store code `s`, since at the time it was written the v1 smoke
  had not yet landed and the quantization-specific wall was not yet known. This drill sharpens that
  proposal into mechanism A above: gate AND redirect the fine read to the retained dense code, not the
  sparse one -- the earlier note's cost-savings argument (`V*C_coarse + k*C_fine` dominating
  `V*C_fine`) still holds, but the target of `C_fine` changes from "condense(s)" to "condense(z)," which is
  the difference between recovering the negative's -0.348 and recovering the dense arm's +0.993.
- **`exp_encoder_phase_traversal_spread_condense_v1.py` / `exp_encoder_phase_traversal_graded_sparse_
  rescue_v1.py`** (direct on-disk reads, this cycle): the confirmed negative and its in-flight rescue are
  the ground truth this entire drill is grounded against; mechanism B above is explicitly that rescue cell,
  not a new proposal.
- **`research_content_gate_brain_grounding_2026-07-08.md`** (combinedgate's grounding note, referenced via
  the prior coarse-to-fine note): the same competitive-normalization/margin-as-confidence-signal argument
  used there for the WHICH-slot decision is reused here (Part 3, mechanism A(c)) for the shortlist-selection
  decision -- both drills converge on "a signal already computed for a different decision is a free,
  local, reflexive confidence signal for a second decision," which this drill additionally grounds in Part
  1d's neuromodulation literature (local reflex decides; aggregate systems only retune the threshold).
- **`substrate_capability_map.md` "correlation hurts associative store capacity, decouple from retrieval"
  reference** (`reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08`):
  this is the certified law the entire phase-traversal line of cells is trying to beat with ONE code instead
  of two. This drill's honest reading of the brain evidence (mechanism D) is that the brain's own
  best-evidenced solution to the identical tension is itself a decoupled two-channel architecture -- so the
  decouple law and the brain evidence are NOT in tension; a working single-code mechanism (A or C) would be
  a genuine, non-trivial WIN beyond what biology typically does, not a expected default.

---

## Substrate-product implications

- **No new mechanism needs to be invented for the highest-value fix.** Mechanism A is already measured on
  disk (`phase_traversal_dense` SC=0.993); the only missing piece is directing the fine read at the RETAINED
  DENSE code for a coarse-filtered shortlist, not at the sparse store code. This is a near-zero-cost,
  near-immediate re-analysis of already-collected v1 artifacts (see Cheap decisive test #1), and should be
  the FIRST thing checked before waiting on the graded-sparse-rescue cell's gamma sweep to land.
  Recommend: run this re-analysis in parallel with (not instead of) letting the rescue cell finish.
- **The graded-sparse-rescue cell (mechanism B) remains valuable and should proceed as pre-registered** --
  brain evidence (CA3 graded settling, population gradedness) lends it real but PARTIAL support; its own
  HARD-FAIL criterion already correctly frames a clean negative as "the wall is fundamental for single-code
  approaches, two-head is confirmed necessary," which is an honest, publishable-internally closing result
  either way.
- **Mechanism C (bounded residual-sketch code) is the one genuinely new, highest-probability-superior
  candidate this drill surfaces.** It is cheap to test (reuses the v1 harness, one new sweep axis) and is
  the only candidate that satisfies the formal non-destructiveness condition (Equitz-Cover) by construction
  rather than approximately. If mechanism A's memory cost (retaining full dense `z` per item) becomes a
  real constraint at larger V, C is the direct, principled answer -- recommend filing it as the immediate
  next cell after mechanism A's re-analysis and mechanism B's rescue land, not before.
- **No separate real-time controller is needed for the per-item coarse-to-fine decision.** This drill's
  brain evidence (Part 1d) independently re-confirms the prior coarse-to-fine note's recommendation: keep
  the drill-down decision local and reflexive (a per-item margin/confidence signal, already computed as a
  byproduct of the coarse read); reserve any self-manager / aggregate-threshold dial for RETUNING that
  local criterion under aggregate load (shortlist size k, residual-sketch size r_k, or graded-code gamma) --
  never for making the per-item call itself. This composition point is now independently supported by TWO
  separate research cycles converging on the same architecture from different questions (WHICH-slot
  vs. HOW-FINE), which raises confidence in it as a general substrate design principle, not a one-off.

---

## Citations (verified count)

External (verified via WebSearch/WebFetch across 4 parallel sub-agents, generic terms only; no
substrate-internal names or numbers sent off-platform):
1. Bar, M. et al. "Top-down facilitation of visual recognition," PNAS 2006.
   https://www.pnas.org/doi/10.1073/pnas.0507062103
2. Bar, M. et al. "Magnocellular Projections as the Trigger of Top-Down Facilitation in Recognition,"
   J. Neurosci. 27(48):13232, 2007. https://www.jneurosci.org/content/27/48/13232
3. Hochstein, S. & Ahissar, M. "View from the Top: Hierarchies and Reverse Hierarchies in the Visual
   System," Neuron 36(5):791-804, 2002. PMID 12467584.
4. Ahissar, M. & Hochstein, S. "The reverse hierarchy theory of visual perceptual learning," TICS, 2004.
   PMID 15450510.
5. "Neural bases of spatial frequency processing during scene perception," PMC4019851, 2014.
6. Rolls, E.T. "Mechanisms for pattern completion and pattern separation in the hippocampus," Frontiers
   Syst. Neurosci., PMC3812781, 2013.
7. "Tracking the flow of hippocampal computation," Neuron 2015 (Leutgeb-line summary), PMC4792674 /
   PMID 26514299.
8. O'Keefe, J. & Recce, M.L. "Phase relationship between hippocampal place units and the EEG theta
   rhythm," Hippocampus, 1993; Skaggs, W.E. et al., Hippocampus, 1996, PMID 8797016.
9. Teyler, T.J. & DiScenna, P. "The hippocampal memory indexing theory," Behav. Neurosci., 1986, PMID
   3008780; Teyler, T.J. & Rudy, J.W. "The hippocampal indexing theory and episodic memory: updating the
   index," Hippocampus 17(3), 2007, PMID 17696170.
10. Wixted, J.T. "Dual-process theory and signal-detection theory of recognition memory," Psych. Review,
    2007; Parks, C.M. & Yonelinas, A.P., 2007 (graded recollection).
11. Equitz, W.H.R. & Cover, T.M. "Successive Refinement of Information," IEEE Trans. Info. Theory, 1991.
    (Rate-distortion abstract-source and Rimoldi multi-stage extensions also surveyed.)
12. Embedded zerotree wavelet (EZW) / SPIHT progressive coding, standard references.
    https://en.wikipedia.org/wiki/Embedded_zerotrees_of_wavelet_transforms
13. 1-bit quantization SNR floor and 1-bit compressed-sensing recovery limits (support/sign-only recovery),
    surveyed via arXiv (1-bit CS reformulation, receiver-quantization framework papers).
14. Population coding: redundant/graded population codes; "winner-share-all" vs winner-take-all
    information-capacity comparison; WTA-readout precision limits (arXiv + MIT Neural Computation +
    PMC12088601).
15. Aston-Jones, G. & Cohen, J.D. "An integrative theory of locus coeruleus-norepinephrine function,"
    Annu. Rev. Neurosci. 28:403-450, 2005.
16. Yu, A.J. & Dayan, P. (2005, expected/unexpected uncertainty, ACh); Feldman, H. & Friston, K.J.,
    J. Neurosci. 33:8227, 2013 (ACh precision-weighting).
17. Shenhav, A., Botvinick, M.M. & Cohen, J.D. "The expected value of control," Neuron 79:217-240, 2013.
18. Yonelinas dual-process ERP meta-analytic evidence (familiarity/recollection onset); Koriat,
    metacognitive feeling-of-knowing / retrieval-fluency literature.
19. BranchyNet / CascadeBERT / early-exit cascade retrieval (general ML confirmation only, lowest-
    confidence citation tier, not brain-primary -- consistent with [[feedback-brain-grounding-drills-lead-
    with-deep-biology-ml-not-the-guide]]).

Internal (direct on-disk reads, this cycle):
- `d:/AI/hd-instrument/experiments/exp_encoder_phase_traversal_spread_condense_v1.py` (full docstring,
  arm definitions, pre-reg bands -- the confirmed negative's ground truth)
- `d:/AI/hd-instrument/experiments/exp_encoder_phase_traversal_graded_sparse_rescue_v1.py` (full docstring
  -- the in-flight rescue's exact mechanism, pre-reg, and HARD-FAIL criterion)
- `d:/AI/hd-instrument/notes/research_energy_scaled_selective_depth_retrieval_coarse_to_fine_2026-07-08.md`
  (full read, same-day prior drill, extended and sharpened by this one)
- `d:/AI/hd-instrument/tools/orchestrator/research_field_advisor.py` (run at cycle start per role contract;
  no directly-adjacent field-advisor candidate maps onto this specific brain-mechanism question -- noted,
  not force-fit)

**19 external source threads (4 parallel Sonnet sub-agents, generic-terms-only), 4 internal artifacts,
directly read/verified this cycle.**

---

## Intuitive summary (plain language)

Our new memory-reading mechanism (phase-traversal) tried to save space by storing things in a heavily
compressed form (only keep the biggest few numbers, and only their plus/minus sign) and then, later, using
a trained "un-squisher" to pull the fine detail back out. It didn't work -- and this drill explains exactly
why, by looking at how real brains handle the same problem. Brains never do what we did: they never build a
cheap "gist" version BY THROWING AWAY the detailed version. Instead they either (1) keep a full detailed
copy sitting around untouched and just glance at a cheap summary of it first (vision's fast-then-detailed
pathways; the hippocampus's "index card pointing at the full file" trick), or (2) build the cheap version as
a strict SUBSET of the detailed one, so getting more detail later just means adding a bit more information
back, never re-deriving it from scratch (this is literally how progressive image compression works). Our
compressed code did neither -- it threw information away with no residue left anywhere, which is a specific,
mathematically well-understood kind of information loss that no amount of clever downstream processing can
undo. The good news: we already proved, by accident, that the "un-squisher" itself works great -- it got
99.3% accuracy when we ran it on the UN-compressed version. So the fix is not to build a smarter un-squisher;
it's to stop asking it to work from the compressed version at all. Keep (or cheaply regenerate) the original
detailed version for the small shortlist of items worth a closer look, and only compress for the items that
are just being used for cheap bulk storage.

**Why it matters:** this turns a dead-end negative into a near-free fix (re-use data we already collected,
no new training) plus one genuinely new, well-grounded idea (a "keep just enough leftover detail to
reconstruct on demand" code, borrowed from how progressive image/video compression and predictive
retinal coding both work) that could get most of the benefit at a fraction of the storage cost.
**Near-term decision:** re-analyze the phase-traversal cell's already-collected data first (cheapest, zero
new code) to check whether a coarse ranking reliably contains the right answer in its shortlist when the
FINE read comes from the retained original, not the compressed code; let the in-flight graded-code rescue
finish in parallel; file the bounded-residual-sketch cell as the next new build after both land.

ASCII-only. No emojis. No em dashes.
