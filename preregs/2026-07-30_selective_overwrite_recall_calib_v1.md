# Pre-reg: Selective-Overwrite-Recall reservoir-failing CONSTRUCTION + CALIBRATION (v1)

Anchor: `selective_overwrite_recall_calib_v1`
Date: 2026-07-30
Author: exp_dev (cell author)
Design source: `notes/wm_value_regime_and_contextual_stream_design_2026-07-30.md` (Q2b)
Run: LOCAL / CPU / push-free. Measurement-first (D3): calibrate the construction BEFORE building any WM mechanism.

## Purpose
Our current MES task is RESERVOIR-decodable (random-init whole-sentence = 0.80 = structure-alone),
so it cannot test LEARNED comprehension. This cell BUILDS + CALIBRATES a task where a random-init
reservoir FAILS (near chance) but content-gated maintenance succeeds -- the only kind that can PROVE
the WM. This dispatch does NOT build the WM; it validates the construction is can-fail FIRST.

## The construction (Selective-Overwrite-Recall)
A per-example stream of `(slot_id, filler)` ASSIGNMENT events. S target slots each WRITTEN multiple
times (overwrites); interleaved with D >> S distractor slot-touches (each also a (slot,filler)).
Ordering/spacing RANDOMIZED per example. Query = one target slot_id at the end; the answer = its
MOST-RECENTLY-OVERWRITTEN filler (not first, not globally-last). Tail constraint: >= TAIL_MIN
distractor events occur AFTER every target slot's last write, so the globally-last token is a
distractor and recency alone cannot answer. Encoding is symbolic: each token id -> a FIXED random
embedding (the "random-init frozen encoder"); surface text/idiom deferred to the mechanism build
(reservoir-failing is a STRUCTURAL property, independent of surface strings).

Reservoir-defeating properties (all present): (i) randomized order/spacing -> no fixed position
predicts the binding token; (ii) each queried slot overwritten >=2x; (iii) answer = MOST-RECENT
write -> requires overwrite-with-suppression (a passive reservoir superimposes/averages all writes,
and a LINEAR/shallow readout cannot form the query x state multiplicative gate needed to select the
last write of the QUERIED slot); (iv) high distractor count + tail distractors bury the target write.

## Params (author-owned; iterated at smoke to reach VALID)
- V_FILL (filler vocab) = 20 -> CHANCE = 1/20 = 0.05 (reported explicitly)
- S (target slots) = 6 ; N_DISTRACT_SLOTS = 24 (slot vocab = 30)
- writes per target slot in [2,4]; D distractor touches ~ 30 ; TAIL_MIN distractor-after-last-write = 8
- stream length ~ 45-50 events
- d_emb (random embedding) = 64 ; d_res (reservoir) = 128 ; spectral radius rho = 0.9
- FULL: train 3000 / eval 1500 streams ; seeds = {7, 13}
- SELF-TEST: tiny (train 200 / eval 200, d_res 32, seed 7)

## Arms
CAN-FAIL controls (MUST land near chance):
- `reservoir_esn_linear` -- random-init frozen ESN encoder + LINEAR probe (query one-hot appended)
- `reservoir_esn_mlp`    -- SAME random ESN + shallow MLP probe (fair non-tautological shot; if this
  passes, the info is linearly-recoverable from the reservoir -> HAS_SHORTCUT)
- `shortcut_globally_last`     -- oracle: filler of last stream event
- `shortcut_fixed_position`    -- oracle: filler at a fixed event index (MAX over several indices)
- `shortcut_first_occurrence`  -- oracle: first filler written to queried slot
- `shortcut_most_frequent`     -- oracle: mode filler of the stream

HEADROOM controls (task learnable; MUST clear well above chance):
- `oracle_keep_last`               -- rule-follower keep-last-write-per-slot = ground truth (ceiling ~1.0)
- `gated_reservoir_at_lastwrite`   -- SAME reservoir state sampled at the queried slot's last-write
  timestep (fixed-rule gating) + LINEAR probe -> localizes the difficulty to GATING, not features.
  NOTE: gating here is a FIXED ORACLE RULE, not a learned mechanism -- this is a calibration
  reference, NOT the WM build.

## Envelope / bands (PASS + FAIL, pre-registered)
- CHANCE = 0.05 (explicit).
- NEAR_CHANCE: accuracy < CHANCE + 0.05 (= < 0.10). Eval N=1500 -> SE ~ 0.006 at chance; 0.05 margin ~ 8 SE.
- HEADROOM_MIN: accuracy >= 0.50 (= 10x chance) for the gap to certify real work.
- VERDICT = `RESERVOIR_FAILING_VALID` iff (both seeds): ALL can-fail arms < 0.10 AND
  `gated_reservoir_at_lastwrite` >= 0.50 AND `oracle_keep_last` >= 0.95.
- VERDICT = `HAS_SHORTCUT` iff any can-fail arm >= 0.10 (esp. reservoir_esn_mlp or any shortcut).
  -> fix construction (increase D / TAIL_MIN / writes, decrease d_res) and re-calibrate.
- VERDICT = `NOT_LEARNABLE` iff headroom arms fail to clear (< 0.50) -> construction too hard / mis-specified.

## Leak-proofing (self-test asserts BEFORE any probe)
- label balance: answer-filler distribution ~ uniform (max class share < 2x uniform).
- naive-shortcut immunity: globally_last / fixed_position(all k) / first_occurrence / most_frequent
  oracle accuracy all < CHANCE + 0.05 on a generated sample.
- split disjointness: train vs eval stream (slot-seq, filler-seq, query) tuples disjoint (hash-set).
- tail constraint: every queried slot has >= TAIL_MIN distractor events after its last write.

## Compute architecture
Sequential-CPU, justified: light calibration (numpy ESN vectorized over streams + sklearn probes);
wall << 10 min foreground; no substrate primitives, no GPU-batchable matmul-heavy sweep. No_storage,
no_composition. Deterministic seeding: FIXED int seeds + numpy default_rng(seed); no `hash()`,
no `list(set())`. final_metrics_atomicity = tmp_replace. crlb_n/a: accuracy task, chance floor stated
(1/V_FILL), no Cramer-Rao noise floor. Progress: print(flush=True) (runtime < 30min; not required).
This cell is measurement-first and builds NO learned mechanism (per task: HOLD the WM).
