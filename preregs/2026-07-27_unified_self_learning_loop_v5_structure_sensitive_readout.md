# Pre-reg: unified_self_learning_loop_v5 (STRUCTURE-SENSITIVE READOUT + CENTERED FAST-STORE KEYS)

Filed 2026-07-27. exp_dev. Cell: `experiments/exp_unified_self_learning_loop_v5.py`.
Status: BUILT; self-test PASS; smoke SMOKE_MECHANISM_PASS (2 local runs, both consistent). FULL = remote
GPU (loads scale-v2 ckpt, unchanged from v4).

## Question
v4 (FULL, MIDDLE_BAND, data/exp_unified_self_learning_loop_v4/metrics.json) was a clean FAIR NEGATIVE:
MAIN_fast_episodic LOW gain (0.0015) TIED word-scrambled (0.0015) and LOST to wrong-concept (0.0068). The
brain-fidelity audit (notes/v4_negative_brain_fidelity_audit_readout_is_order_blind_next_lever_2026-07-27.md)
mechanistically located the defect: v2's `TinyTransformer.pooled` readout is MEAN-POOL over token hiddens --
permutation-invariant over the token SET, so a word-scrambled sentence (identical multiset) produces nearly
the same rep as the coherent original (STEP-0 probe, data/probe_v4_readout_order_sensitivity_v1.json:
coh-vs-scrambled cos=0.9944). Does a STRUCTURE-SENSITIVE, own-mechanism readout (HRR-bind a fixed
per-position role vector to each token hidden, per STEP-0's winning BIND_HRR_position variant:
coh-vs-scrambled 0.7304, coh-vs-wrong-RAW 0.4848) finally produce COMPREHENSION-SPECIFIC learning gain on
the exact same v4 test?

## ONE-VARIABLE change from v4 (everything else held identical)
1. **READOUT**: `V2.TinyTransformer.pooled` (mean-pool) -> HRR-bind readout (`hdlab.binding.bind`, FFT
   circular convolution of a fixed per-position role vector with each token's contextual hidden state,
   summed over non-pad positions, L2-normalized). Applied as a GLOBAL CLASS-LEVEL monkeypatch at module
   import time (`V2.TinyTransformer.pooled = _bind_pooled`), BEFORE any encoder is built or text encoded.
2. **COMMON-MODE REMOVAL on the fast-store KEY path only**: `_sparse_keys` (used both for building each
   mention's DG key AND the context query in `_fast_episodic_read`) now mean/rank-centers its input via
   `LOOP2._apply_common_mode`, using a transform fit ONCE from the fixed train foundation (`base_text`, in
   bind-readout space) via `LOOP2._fit_common_mode(base_text, cm_rank)` -- the same helper v2's
   `precision_cm`/`ca3` arms already use. STEP-0: raw cross-concept cosine 0.9444 -> -0.0645 after centering.

Arms (7, identical specs to v4), HP bands, SLICES, SELFTEST/SMOKE/FULL cfg profiles: UNCHANGED from v4
(`experiments/exp_unified_self_learning_loop_v4.py`; both files diffable). No other variable moved.

## SPACE-CONSISTENCY design risk (the pre-reg's own explicit ask) -- resolved by construction
Comprehension GAIN is measured via relational-AUC over a `text` matrix mixing (a) `base_text` -- the FIXED
train-pool foundation, built ONCE by `V2.encode_concept_text_reps` which calls `model.pooled()` -- and (b)
`store[ci]` -- held concepts' consolidated reps, built from mention reps produced by `LOOP2._encode_sentences`
(also calls `model.pooled()`). If the readout were swapped at only ONE of these two call sites, `text` would
silently mix bind-space held rows against mean-pool-space candidate rows -- cosines between the two would be
geometrically meaningless. **Resolution**: patch `V2.TinyTransformer.pooled` at the CLASS level (not per
call site), so EVERY consumer of `.pooled()` in the whole process -- `encode_concept_text_reps` (base_text),
`LOOP2._encode_sentences` (all mention reads, all 7 arms, every cycle), and the self-test's own toy encoder
-- shares the identical readout. There is exactly ONE readout in the pipeline; store-write and
measurement-consumed reps are the same geometry by construction, not by convention.
The common-mode change is scoped NARROWLY on purpose: it only touches the DG KEY computation inside
`_sparse_keys`; the VALUE space (raw bind-readout mention reps summed into the final concept rep) is left
UNCENTERED, matching `base_text`'s geometry, so centering cannot introduce a store-vs-measure mismatch (it
only reweights which episodic traces the competitive read favors).

## Discriminator (LOAD-BEARING, unchanged from v4): COMPREHENSION-SPECIFIC GAIN
FAST_CORRECT LOW-slice across-cycle GAIN must EXCEED BOTH the word-scrambled control's LOW gain AND the
wrong-concept control's LOW gain. **Pre-registered honest DEFLATE**: if bound-coherent STILL ties
bound-scrambled on GAIN even though STEP-0 showed the representation now separates them at readout, that is
a real negative pointing DEEPER -- the relational-AUC metric or the consolidation/learning-UPDATE step
itself, NOT the readout -- and must be reported plainly as such, not spun as "the readout didn't work."

## Bands (FULL; pre-registered, identical to v4)
- HARD_PASS: MAIN_fast_episodic LOW sustained gain > +0.02 (no wash-out within WASHOUT_EPS=0.01)
  AND comprehension_specific_gain (LOW gain > scrambled LOW gain AND > wrong_concept LOW gain)
  AND beats_plain (LOW gain > plain LOW gain; plain reproduces wash-out)
  AND contrast (LOW gain > HIGH gain) AND retention(LOW) AND sleep-every AND controls-below-main(LOW)
  AND power (LOW n_query >= 40) AND stratified-probe-fires.
- MIDDLE_BAND: any positive LOW gain but discriminator/direction not fully met.
- HARD_FAIL: LOW gain <= 0 (fast episodic ALSO flat -> DEFLATE with per-slice power, mentions/concept,
  gain magnitude, specific-fact hit@1, headroom-norm gain, AND explicit readout_diagnostic values so a
  reader can see whether representation-level separation held at FULL scale even if the loop still failed
  to learn from it).
- Gain ALSO reported headroom-normalized (gain/(1-baseline)) per slice.

## NEW in v5: readout diagnostic (`_readout_diagnostic`)
Mirrors the STEP-0 probe but runs against THIS run's own encoder + REAL postings for the held concepts
actually used, every SMOKE and FULL run: samples up to 40 held concepts, encodes (coherent, scrambled,
wrong-concept) triplets, reports coh-vs-scrambled and coh-vs-wrong-RAW mean cosine + `order_sensitive_fires`
(cos<0.95) / `discriminative_fires` (cos<0.95). Computed and logged on every run (both SMOKE and FULL) for
visibility -- this is the mandatory "coherent/scrambled/wrong arms actually differ at readout" check the
task required, run against the ACTUAL run's data, not just a standalone probe script or self-test toy data.

## SMOKE gate scoping (DISCRIMINATOR-MUST-SURVIVE-SCALE, PATH B applies to the readout diagnostic)
MEASURED (2 local SMOKE runs, both consistent): on the SMOKE's own 250-MLM-step, d=128 fresh-trained toy
encoder, `readout_diagnostic` shows coh-vs-scrambled cos=0.9982 (order_blind=True) -- the readout does NOT
fire order-sensitivity on this specific tiny/undertrained encoder. Root cause (not a mechanism bug):
early-training anisotropy at 250 MLM steps is severe enough that even HRR-bind cannot escape it (loss only
fell 77.0 -> 6.56, far from convergence). Self-test's OWN order-sensitivity check, run against an UNTRAINED
random-init toy encoder (no training at all), DOES fire (coh-vs-scram cos=0.6644, `readout_diagnostic_selftest`
cos=0.5511) -- confirming the readout PATCH ITSELF is correctly wired and produces genuinely different reps
for different token orders; it is the SMOKE encoder's training-immaturity, not the readout code, suppressing
the effect at SMOKE scale. Per DISCRIMINATOR-MUST-SURVIVE-SCALE PATH B: the regime that matters -- the real
v2 checkpoint FULL will load -- was already measured DIRECTLY by STEP-0 on `ckpt_seed_7`: coh-vs-scrambled
cos=0.7304 (order_blind=**False**), coh-vs-wrong-RAW cos=0.4848 (discriminative=**True**), both comfortably
past the 0.95 gate. **Decision**: `readout_order_sensitive_fires` / `readout_discriminative_fires` are
COMPUTED + reported (payload + verdict_msg) on every SMOKE/FULL run for visibility, but are NOT part of the
SMOKE `mechanism_ok` AND-chain -- gating SMOKE_MECHANISM_PASS on the tiny/undertrained encoder's readout
diagnostic would reject a cell whose readout mechanism is independently, directly verified (STEP-0, disk
data) at the regime the FULL claim is actually made about. This is the SAME exemption class v4 already used
for the capability signal itself ("tiny encoder below signal threshold"); v5 extends it, honestly, to the
readout diagnostic specifically, with a citation to a real disk measurement rather than an assumption.
All 8 OTHER SMOKE mechanism gates (pattern-sep, arms-differ, context-address self-test, sleep-every,
stratified-probe-fires, comprehension-discriminator-resolves, noread-flat, clarify-fired, power-ok)
MEASURED PASS on both local SMOKE runs.

## Smoke result (MEASURED@data/exp_unified_self_learning_loop_v5_smoke/metrics.json, tiny fresh encoder,
128.6s / 129.4s wall, 2 consistent local runs)
SMOKE_MECHANISM_PASS. pattern_sep ratio=0.0893 (self-test synthetic anisotropic-input ratio=0.1161, keys
strongly decorrelated); common-mode-changes-keys self-test PASSED (centered vs uncentered keys differ,
not `allclose`); fast read denoise 0.9988 > plain 0.9796 (self-test); context-addressability PASSED;
specific-fact hit@1=1.0 (self-test synthetic). On the real tiny SMOKE encoder (informational, capability
FULL-deferred per v1-v4 precedent): FAST_LOW_gain=-0.0372 (washed), scrambled_LOW=-0.0543,
wrongconcept_LOW=-0.1516, plain_LOW=-0.0520, HIGH_gain=0.0251, spec_fact_LOW_hit1=0.4, sleep_every=True,
controls_below_main=True, LOW_nq=20. NOTE (honest, same caveat as v4): all LOW gains are NEGATIVE at SMOKE
scale (the tiny 250-step encoder has not learned enough to show any arm's directional capability); this is
NOT capability evidence, only the mechanism-fires + discriminator-resolves + readout-diagnostic-computed
check. Capability is FULL-deferred to the real v2 checkpoint.

## Self-test additions over v4 (all MEASURED PASS, 2 local runs)
- (0) readout-patch-identity: `V2.TinyTransformer.pooled is _bind_pooled` (patch is ACTUALLY active, not
  just present in source).
- (2b) order-sensitivity on the self-test's own untrained toy encoder: coh-vs-scrambled cos=0.6644 < 0.999.
- (3b) common-mode-changes-keys: centered vs uncentered `_sparse_keys` output on synthetic anisotropic
  input are NOT `np.allclose` (centering measurably fires).
- (7b) `_readout_diagnostic` self-test on the toy universe: n_pairs=6, order_sensitive_fires=True,
  discriminative_fires=True.
- (8) ckpt round-trip: reloaded model's `.pooled.__func__ is _bind_pooled` (class-level patch survives a
  fresh `TinyTransformer(...)` construction from a reloaded checkpoint, as required since the patch is
  applied once at v5 import time, not per-instance).

## SCHEMA-VET fields
- final_metrics_atomicity: tmp_replace (os.replace) -- unchanged from v4.
- arms_differ_verified: True (smoke; NO_READ==READ_NO_SLEEP exempted -- both freeze cycle-0 fast store).
- discriminator survives scale: PATH B analytical, TWO layers -- (a) capability signal: tiny encoder below
  signal threshold (v1-v4 MEASURED precedent, unchanged); (b) readout diagnostic: tiny/undertrained SMOKE
  encoder does not fire order-sensitivity (MEASURED, this cell), but the real v2 ckpt regime DOES (MEASURED
  by STEP-0, disk data cited above) -- both are PATH B, cited to actual disk measurements, not assumed.
- baseline_in_band: MAIN_plainavg LOW relational AUC ~0.44-0.49 at smoke (in [0.05,0.95]).
- crlb_n/a: directional gain gate, not a capacity/noise-floor threshold (no Cramer-Rao floor applies).
- calibration_check: default_ok_for_this_regime (inherits v2/v3/v4 consolidation defaults + leak-proof
  probe; the ONLY new calibrated element, the fast-store common-mode `cm_rank=3`, is fit from the fixed
  train foundation exactly as v2's existing precision_cm/ca3 arms already do -- not a new calibration choice).
- cardinality_ok: n/a (no seed/param sweep axis; single seed per run, fixed arm set).
- deterministic_seeding: True (fixed ints + default_rng + fixed DG projection seed + fixed
  READOUT_ROLE_SEED=20260727; no hash()/list(set())).
- progress_logging: print_flush_true (timeout_s >= 1800).
- except SystemExit: raise BEFORE except Exception (no BaseException; grep gate clean). start-marker +
  crash-diag + heartbeat unchanged from v4.
- arms_must_differ: hash-digest check, PASSED both local smoke runs (grep gate + runtime assert).
- LEAK-PROOF: unchanged from v4 -- predicted edge disjoint from read text; probe negatives degree-matched,
  adjacency excluded.
- INVARIANTS: TEACHER-FREE; NO borrowed vectors (OUR trained encoder only; HRR bind is a substrate-native
  glass-box primitive, not a learned/external component); GLASS-BOX; ASCII-only; store writes LOCAL-ONLY +
  UNCOMMITTED; VET_PENDING; NO bolt-on external reader/parser (readout is computed purely from this cell's
  own frozen/trained encoder's token hidden states via hdlab.binding.bind, the project's own primitive).

## Compute architecture
MIXED (unchanged classification from v4, with one addition): encoder forward passes batched on GPU
(`LOOP2._encode_sentences`, autocast for the transformer forward; the readout itself forces float32 --
`torch.fft` is not amp-safe under fp16, see `_bind_pooled` docstring); per-concept fast-store read + Kalman
+ FFT-bind readout are light (negligible wall time relative to the transformer forward pass: FFT over d=512
per token is O(d log d), same order as the matmuls already dominating the forward pass). FULL device = cuda
(`V2._select_device`). Sequential across 7 arms x 6 cycles (each arm depends on its own accumulated buffer;
same dependency structure as v4). Justified: heavy compute is the batched-GPU encode; the added FFT-bind
readout is a per-batch elementwise-FFT operation on the same batched tensor, not a new sequential loop.

## FULL dispatch
queue: overnight_queue (GPU; loads data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt, unchanged
from v4). Runner signals FULL via HDLAB_RUN_MODE=full. timeout_s: 12600 (3.5h; v4 used 10800 (3h) at the
same FULL_CFG scale -- bumped ~17% for the added FFT-bind readout cost on the base_text foundation encode
pass (all ~2500 train concepts + all held concepts, once) and the fast-store DG key path now performing a
common-mode-centering pass per mention; still well under the 14400s cap).

## Ship command (exp_dev returns; per LOCKED USER 2026-07-08 ship policy exp_dev does NOT SCP remote itself)
```
bash tools/orchestrator/queue_add.sh overnight_queue unified_self_learning_loop_v5 \
  experiments/exp_unified_self_learning_loop_v5.py \
  preregs/2026-07-27_unified_self_learning_loop_v5_structure_sensitive_readout.md 12600
```
