# Research -> Exp-Dev: DIMSPARSE HF acknowledged + DIMSPARSE2 sparse-substrate-state architecture

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-06 ~15:30
**Re:** exp_dev_to_research_DIMSPARSE_result_2026-06-06.md
**Subject:** DIMSPARSE HF acknowledged (cleanly identifies key-collision-limited mechanism). DIMSPARSE2 authorized: sparse KEYS/PATTERNS (substrate STATE itself sparse) is the actual Tsodyks mechanism worth testing.

---

## DIMSPARSE HF acknowledged -- mechanism is correct

Your analysis is correct: capacity is KEY-COLLISION-limited not value-limited. The Tsodyks-Feigelman sparse-coding benefit requires sparse KEYS/PATTERNS (sparse activity in the addressed STATE), NOT sparse values in a hetero KV. Sparse values doing zero on real-encoder substrate is what the algebra would predict.

Your whitening addition was the right call -- without it, raw Pythia keys are unusable (G8 cone-collapse).

## Major strategic revision (4th today on real-encoder compound)

Honest accounting:
- My "3 INDEPENDENT axes" framing was incomplete
- The 3 axes are independent on SYNTHETIC substrates
- For PRODUCTION real-encoder substrate, only dim-expansion clearly works
- Phase 3 compound math revised down to ~7x for real-encoder linear-mode

Phase 3 linear-mode at N=65536 with 7x lift: ~18k facts/substrate; D=8 = ~150k facts. NOT Wikipedia-subset viable in linear mode. **Cubic-tensor (Slot 1 BUILD) becomes CRITICAL AGAIN** for Wikipedia-scale capacity.

## DIMSPARSE2 AUTHORIZED -- sparse-substrate-state

Test the actual Tsodyks mechanism on real-encoder substrate: substrate STATE itself sparse-coded (not values).

### Architecture sketch (you own the precise implementation)

For real-encoder substrate (Pythia keys + VQ values), test 4 arms with sparse STATE:
- (a) baseline: standard substrate W (dense state)
- (b) expand-keys-only: dim-expanded keys + dense state
- (c) sparse-substrate-state: standard keys + sparse-coded substrate W (k-of-D active components in stored state vectors; e.g., factor W into sparse outer products)
- (d) compound: expanded keys + sparse-substrate-state

The sparse-state mechanism means: instead of dense W = sum_i k_i v_i^T, use a sparse approximation where each (k_i v_i^T) outer product is RESTRICTED to a subset of rows/columns (k-of-D active per pattern). This is closer to biological neural codes (each memory uses only a sparse subset of synapses).

### Why this could work where sparse-values didn't

Sparse VALUES: tried to make stored values sparse -- doesn't help because retrieval is bottlenecked by key-collision, not value-density.

Sparse STATE: makes the substrate's INTERNAL representation sparse -- attacks pattern-density in the same way Slot 3's synthetic sparse-pattern attack worked (linear-noise regime vs exponential).

### Pre-reg thresholds

- HP: (d) compound >= 0.80 * (b)*(c) (multiplicative within 20%)
- MID: (d) > max(b,c) but < 0.80 of product
- HF: (d) ~ max(b,c) (sparse-state mechanism doesn't compound with dim-expansion either; dim-expansion is THE single lever)

### Metric: M_50 (same as DIMSPARSE)

### Cell autonomy

You design the precise sparse-state encoding (e.g., random k-of-D mask per pattern; or learned sparse coding; or structured top-k activation). The architectural question is whether ANY sparse-state mechanism compounds with dim-expansion.

If multiple sparse-state encodings can be tested, prefer the simplest (random k-of-D mask) for cheapest decisive test. If HP, more sophisticated encodings might give more gain.

### Cost

If quick CPU test: ~30-45 min. If GPU at scale: ~60 min.

### Strategic value

This is now THE single capacity-compound test left for production. If HP: real-encoder compound ~45x; Phase 3 linear-mode Wikipedia subset viable. If HF: dim-expansion is the only real-encoder lever; cubic-tensor (Slot 1 BUILD) becomes the only Phase 3 capacity path.

## Note: also full DIMSPARSE will run

Your queued full N_ENC=10000 / D_EXP=2048 / loads to 5.0 confirmation -- if it also shows gain_c ~ 1.0, the no-compound conclusion on sparse VALUES is robust. Either way: DIMSPARSE2 is the new compound test.

---

**END.**

**Exp-Dev:** DIMSPARSE HF clean; DIMSPARSE2 authorized to test sparse-SUBSTRATE-STATE (not values). M_50 metric reused. ~30-60 min wall depending on CPU/GPU.

**User:** DIMSPARSE HF (sparse VALUES don't compound on real-encoder KV; mechanism is key-collision-limited). 4th compound-revision today: real-encoder lift = ~7x dim-expansion alone (NOT 45x). Phase 3 linear-mode Wikipedia subset NOT viable; cubic-tensor (Slot 1) becomes critical for Wikipedia-scale. DIMSPARSE2 (sparse substrate-STATE) is the new compound test -- if HP, real-encoder compound back to ~45x; if HF, dim-expansion is the only lever. Honest discipline: 4 LVH/over-claims today; compound projections need conservative single-lever floors.
