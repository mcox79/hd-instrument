# Pre-registration: working_memory_hrr_slots_smoke_v1

**Date:** 2026-06-23
**Anchor:** working_memory_hrr_slots_smoke_v1
**Queue:** local_cpu_queue
**N:** 4096, **Seeds:** [7, 17, 23], **ARMS:** 3 (FLAT_SUPERPOSITION, HRR_SLOTS, HRR_SLOTS_PLUS_CLEANUP)

## Scientific question
Can the substrate hold a working memory of K items, each bound to a slot tag,
in a single HD vector and retrieve them by slot? The mechanism is HRR-superposition:
workspace = sum_i bind(item_i, slot_tag_i); retrieve_i = unbind(workspace, slot_tag_i)
then optional cleanup against the codebook. Brain analog: PFC sustained firing +
theta-gamma binding (each working-memory slot held at a distinct gamma phase within
a theta cycle; Miller's magic number ~7 items). This implements substrate-native
scratch space for multi-hop reasoning.

## Pre-registered bands

**HARD-PASS (substrate working memory works; chain-grade-eligible primitive for multi-hop reasoning):**
- ARM_HRR_SLOTS_PLUS_CLEANUP mean per-slot recall across seeds >= 0.90 at K=7 (Miller's magic number)
- AND mean per-slot recall across seeds >= 0.70 at K=10
- AND mean per-slot recall across seeds >= 0.50 at K=16
- (averaged across all noise sigmas in [0.0, 0.5, 1.0])

**MIDDLE:** Works at small K (K=2 or K=4 recall >= 0.90) but degrades faster than
Miller's range (fails one or more of the K=7 / K=10 / K=16 thresholds); characterize
the capacity envelope.

**HARD-FAIL (substrate cannot hold even 4 items; working-memory primitive null):**
- ARM_HRR_SLOTS mean per-slot recall at K=4 <= 0.50 (averaged across noise sigmas)

## Calibration rationale
- HRR-superposition capacity for K bound items in N-dim bipolar space is well-studied:
  crosstalk variance ~ (K-1)/N, so SNR drops as 1/sqrt(K-1) after unbind. At N=4096
  and K=7, raw unbind SNR is roughly sqrt(4096/6) ~ 26 -- well above codebook
  cleanup threshold for a 50-item codebook. At K=16, SNR drops to ~16, still above
  cleanup for tiny codebooks but tightening; the HARD_PASS bands deliberately ladder
  these capacity points.
- K=7 = Miller's magic number (human working-memory capacity); a substrate that
  hits human-equivalent performance is a chain-grade primitive.
- K=10 = the upper end of expert chess-positions / chunk-reorganized human working
  memory; 0.70 is the substrate-product threshold here.
- K=16 = ~2x Miller; 0.50 (better than chance for any K, since random is 1/50=0.02)
  characterizes the graceful-degradation envelope.
- Noise sigmas [0.0, 0.5, 1.0] sit below the Shannon-floor we already characterized
  at sigma>=1.5 in prior arc; testing working memory in the regime where it should
  actually function.
- ARM_FLAT_SUPERPOSITION (no slot binding; just bundle items) is the control that
  cannot distinguish positions; should score near chance / 1/K at retrieval. Validates
  that the slot-binding mechanism is load-bearing.
- ARM_HRR_SLOTS_PLUS_CLEANUP is the full mechanism (slot-binding + per-slot
  codebook cleanup; the architectural complement per c3 + g1b precedent).
- The HARD-FAIL band at K=4 is well below Miller; if HRR_SLOTS cannot even hold 4
  items the whole substrate working-memory bet is structurally null.

## N-suffix section
Anchor has no `_n<N>` suffix; PROT-018 / PROT-019 / PROT-021 do not apply
(smoke cell; N=4096 fixed; K, sigma swept as inner-loop). Smoke runs full N=4096
on synthetic random bipolar atoms (no pretrained encoder needed); wall is bounded
by K-sweep x sigma-sweep x seeds.

## Timeout estimate
Smoke ~ 60s at N=4096 single seed (3 arms x 5 K-values x 3 sigmas x 50 items =
2250 retrievals; bipolar matmul against 50-item codebook is cheap; per-K
workspace assembly is sum of K outer-product binds at N=4096).
FULL: 3 seeds x same inner loop = ~3 minutes.
formula: ceil(1.5 * 60 * 1.0 * (3/1)) = 270s -> rounded up to 600s for safety.
timeout_s = 600

## Mechanism design (informative)
- Random bipolar atoms (numpy.default_rng.choice in {-1, +1}^N) for items + slot
  tags; deterministic per seed. 50 test items per K (drawn from a shared 50-item
  codebook); K slot tags (distinct seeds for slot vs item).
- bind = element-wise product on bipolar vectors (HRR-analog; involutive).
- workspace assembly: for K items + K slot tags, sum the K bind products. Optional
  sign-quantize after sum to keep bipolar (we leave both forms in mechanism;
  superposition itself does not require bipolar quantization of the sum, but cleanup
  uses raw-cosine to codebook so the un-quantized workspace is the canonical form).
- noise: add gaussian noise to workspace at chosen sigma; bipolar-quantize after.
- retrieve_i = bind(noisy_workspace, slot_tag_i)  (involutive; unbind = bind for bipolar).
- cleanup (PLUS_CLEANUP arm only): argmax of cosine(retrieve_i, codebook) ->
  recovered_item; correct iff recovered_item index == ground-truth item index.
- Per-slot recall = correct/K averaged over slots; per-K recall = mean over
  noise sigmas; HP bands compare against per-K recall targets.

## Sanity self-test (in --self-test path)
- T_K1: at K=1, all arms recall=1.0 at sigma=0 (trivial; bind then unbind
  recovers the single item exactly; cleanup is no-op for argmax over 50-item
  codebook with one exact hit).
- T_K_OVERLOAD: at K=N_DIM (extreme), all arms recall near chance (1/50 = 0.02).
- T_FLAT_FAIL: ARM_FLAT_SUPERPOSITION at any K>=2 cannot distinguish positions
  -> per-slot recall <= 1/K (random over the K items in the workspace, since
  the slot-tag information is absent).
- T_BIND_INVOLUTIVE: bind(bind(a, b), b) == a for bipolar a, b (validates the
  unbind == bind primitive).

## Cites
- experiments/exp_contextual_encoding_hrr_binding_smoke_v1.py (HRR bind pattern;
  bipolar quantization helpers)
- hdlab/sequence_memory.py (sequence-binding precedent: separate matrix for
  ordered-pair store; here we use HRR superposition for a single working-memory
  vector at any moment)
- USER 2026-06-23: "we definitely need this -- didn't we already agree on that
  and isn't there a clear solution that uses substrate just like the brain does?"
  Yes; this implements PFC-theta-gamma working-memory analog at Miller-capacity scale.
- Gap-3 composition enabler (substrate-native scratch space for multi-hop reasoning).
