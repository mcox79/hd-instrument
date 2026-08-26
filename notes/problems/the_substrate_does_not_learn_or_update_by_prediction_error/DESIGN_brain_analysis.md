# Brain analysis + experiment design -- prediction-error learning/update

**Opening move (SOLVER PROTOCOL): which brain structure does this, and are we replicating the
OPERATION or substituting something convenient?**

## The two framings the brief offers, and which is already CLOSED

1. **LEARNING** -- reps trained with a forward-PC term beat cloze-trained reps downstream.
2. **UPDATE / SEGMENTATION** -- a PE-driven "when to write / event boundary" signal (N400
   `||Delta situation_model||`) beats fixed/random segmentation at getting the right content into the
   situation model.

**Disk check (the disk outranks the brief):**
- The **item-write-gate** reading of framing 2 is KILLED TWICE and I will not touch it.
  `exp_predictive_coding_write_gate_dissociation_v1` (2026-08-18): PE-gated writing is `NOT_SEPARATED`
  from a **rate-matched RANDOM gate** at all four thresholds -- *the benefit is from writing LESS, not
  from writing the RIGHT things.* The mechanism was later named
  (`SURPRISE_IS_REAL_BUT_UNINFORMATIVE_ABOUT_VALUE...`): the surprise proxy (`1 - cos(item, accumulated
  anchor)`) measures **novelty of FORM, not novelty of CONTENT**; in a near-orthogonal representation
  form-novelty is ~constant, so gating on it IS gating at random.
- The **symbolic** event segmenter `exp_event_boundary_relevance_gate_v1` (HARD-PASS, f1 0.95) is a
  DISCRETE check (did protagonist / tense / causal-link change), n=17 hand-built -- **not** the graded
  N400 prediction-error signal. F5 (the N400 generator, `||Delta situation_model||`) is **MISSING
  outright** in the audit; E2 has the register but **no PE-driven segmentation**.
- The one **learning-angle** prior, `exp_substrate_owned_predictive_coding_encoder_v1` (HARD_FAIL vs
  word2vec), used a `sign()`-quantised forward pass (the exact p1 confound this brief forbids) and came
  back FLAT (every arm pinned at the unigram floor 7.738 = broken experiment, not a ceiling). Not
  cleanly closed, but heavy and low-headroom (+0.44 forward structure already latent in cloze reps).

**THE SHARED WALL across every prior PE failure is REPRESENTATIONAL:** the error was computed on a
`sign()`-quantised or near-orthogonal prediction, so **magnitude is uninformative** (big & small misses
look identical; form-novelty ~constant). Per the protocol, a shared wall across variations means NONE of
them was the brain's mechanism -- the faithful signal is GRADED, PRECISION-WEIGHTED, and measured
against the CURRENT MODEL STATE, and NO prior cell did that.

## The brain mechanism (PINNED reference, UNPINNED equation)

**N400 = the magnitude of the update forced on a RUNNING situation-model representation by the incoming
word** -- `||Delta situation_model||`, a prediction error against the CURRENT discourse state, not a
fixed template (Rabovsky, Hansen & McClelland 2018 Nat Hum Behav; Kutas & Federmeier 2011). **Event
segmentation posts a boundary where prediction error spikes RELATIVE to the model's own recent baseline**
(Zacks & Franklin SEM; Reynolds/Zacks/Braver 2007 -- the running-average relative threshold, which
`hdlab/predictive_coding.py:relative_threshold_gate` already implements). The reference point (current
model state) is PINNED; the norm, the precision estimator, and where the error drives learning vs
updating are OURS to sweep.

**Copy the COMPUTATION:** maintain a running state; forward-PREDICT the next input from it; the GRADED
residual is the update/learn signal; post a boundary when it spikes relative to the running baseline;
reset the state at the boundary. **Sweep the PARAMETERS:** dimensionality, within-event coherence,
precision estimator, threshold. Do NOT quantise the prediction; do NOT anchor on the whole stream.

## Why the killed proxy failed and this does not (the crux)

The killed proxy anchored on the item's OWN history across the WHOLE stream and never reset, in a
representation where every context is near-orthogonal -> the "surprise" was novelty-of-FORM, ~constant,
uncorrelated with value. The brain's N400 is different in three ways, ALL of which this design copies:
1. **RUNNING state that RESETS at boundaries** (the "current event", not the whole stream).
2. **A GRADED content prediction error** against that running state (not a sign-quantised bit-flip
   count, not a whole-vector cosine).
3. **PRECISION-WEIGHTING** -- weight the error by how reliable the running estimate is.

## The decisive experiment (event segmentation of a discourse with GROUND-TRUTH boundaries)

A discourse = a sequence of N propositions partitioned into K true events (variable length). Each
proposition i carries:
- a **role** r_i (small vocab; DISTINCT within an event, REPEATED across events),
- an **identity filler** f_i (near-orthogonal codebook |V|, used for binding + the readout),
- a **context feature** c_i = normalize(topic_{event(i)} + noise * eta_i) -- topics near-orthogonal
  ACROSS events, so c is coherent WITHIN an event and JUMPS at a boundary. `noise` (within-event
  coherence) is the key stimulus PARAMETER and is SWEPT, never adopted.

*(Two vector spaces on purpose, and it is brain-faithful: a word has a lexical IDENTITY that gets bound
into memory and a semantic CONTEXT that drives the N400 fit -- distinct streams.)*

**The situation model** binds `bind(f_i, event_slot)` into a per-segment bundle using the REAL substrate
ops (`hdlab.binding.bind/unbind`, `hdlab.bundling.bundle`, `cleanup_argmax`). The SEGMENTER decides which
propositions share an event slot.

**Downstream DV -- within-event cross-role recovery (penalises BOTH over- and under-segmentation):**
for every ordered within-true-event pair (a,b), unbind segment_of(a)'s bundle by role_b and cleanup-
argmax over |V|; correct iff == f_b. Over-segmentation splits a from b (b absent from a's segment ->
miss); under-segmentation merges a foreign event carrying role_b with a different filler (collision ->
miss); correct segmentation recovers it. Accuracy over all pairs = "did segmentation get the right thing
into the situation model." Boundary-detection F1 vs gold is reported as a secondary read.

### Arms
- **N400_content** (MAIN, brain mechanism): running `m` = normalized mean of c since last boundary;
  `e_i = 1 - cos(c_i, m)` (GRADED); post boundary when `e_i / running_avg(e) >= tau` (EST relative);
  reset `m` at boundary. Sweep tau.
- **N400_content_precision**: same, error weighted by prediction confidence `kappa = ||sum c|| / n`
  (precision of the running estimate) -- tests the precision term.
- **N400_modelupdate**: `e_i = ||register_after - register_before||` (the LITERAL naive `||Delta model||`)
  -- tests whether the raw state-update magnitude is the form-novelty trap in disguise.

### Floors (recomputed on THIS population; gate on the UPPER CI)
- **FIXED_k**: boundary every k props (k = median event length; swept).
- **RANDOM_ratematched**: boundaries at random positions, COUNT matched per-stream to N400_content --
  *the killer control from the write-gate null: beats it only if boundaries are in the RIGHT places.*
- **FORM_NOVELTY**: the KILLED proxy -- `e_i = 1 - cos(c_i, global anchor)`, anchor = mean of ALL c
  from stream start, NEVER reset. Must lose (or tie random).
- **NO_SEG** (one bundle) and **EVERY_PROP** (boundary every prop) -- the degenerate extremes.
- **ORACLE_true_boundaries** -- ceiling.

### Info-free twin (must LOSE)
- **PERMUTED_SURPRISE**: take N400_content's `e_i` sequence, SHUFFLE across positions, apply the same
  boundary rule -> boundaries decorrelated from content. Null p95 comes from this.

### Gate
On a held-out population with floors recomputed on it: **N400_content lower-CI > UPPER-CI of the
strongest floor** among {RANDOM_ratematched, FIXED_k, FORM_NOVELTY} AND > PERMUTED_SURPRISE upper-CI,
CI half-width + null p95 reported. Decisive either way:
- **WIN** -> graded forward-PE against the running model state is the missing N400/segmentation signal;
  propose wiring F5 (`||Delta model||` computed as CONTENT prediction error, GRADED, precision-weighted;
  boundary via the existing `relative_threshold_gate`) into E2's write decision.
- **LOSS** (ties random / form-novelty) -> the update magnitude is form-novelty in disguise in our
  representation; the fix is upstream (p1 graded content reps), a foundational negative and a full PASS.

### Parameters swept (never adopted)
D in {64,128,256} (low-dim = brain-faithful and dodges the ceiling); within-event coherence `noise`;
tau; precision on/off; >=3 seeds. Bootstrap CIs; save the scored population.
