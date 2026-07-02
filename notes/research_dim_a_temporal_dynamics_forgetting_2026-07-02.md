# Dim A: Temporal Dynamics / Forgetting Timescales — Research Drill 2026-07-02

**Filed:** 2026-07-02 (SONNET LIBERAL DRILL per USER 2026-07-01 full-night directive)
**Prior-arc check:** substrate_query "temporal dynamics forgetting timescales decay retention" — top hit cosine=0.31 (note chunk); no decisive cell on this exact question from post-Stage-2 perspective.
**P_def prior:** 0.32 (per hidden-dim drill doc)

---

## What the Prior Arc Actually Tells Us (Off-Disk Verified)

The substrate has substantial prior-arc temporal data. Key landed results:

### 1. Write-order has NO effect on retention (static-Hebbian confirmed)

The Hebbian write rule `W += outer(v_k, v_q)` is commutative and additive. Write order is irrelevant by construction: writing item A then B produces the same W as writing B then A. No LIFO / FIFO bias is mechanically possible in raw Hebbian accumulation. This is not an open empirical question — it is structurally closed by the superposition rule. The exp_a8_continual_writes cell (HARD_PASS) tested sequential writes at alpha=[0.05...0.3] and found flat recall across all alphas in the feasible regime, consistent with no positional advantage.

**Implication for Dim A question (recency bias):** Static-Hebbian substrate has zero write-order memory. All items written within the feasible capacity range are recalled with equal probability. There is no primacy, recency, or serial-position curve in raw substrate — these are absent by construction.

### 2. Forgetting requires ACTIVE mechanisms (not spontaneous)

exp_recency_forgetting_curve_cpu_v1 (HARD_PASS):
- Artificial age-decay applied to item weights produces monotone forgetting curve
- Half-life at "t=15" decay steps; curve: t0=1.0, t5=1.0, t10=0.72, t15=0.05, t20=0.0
- Decay is COMPETITIVE: cleanup identifies the strongest attractor; decayed items lose competition
- **Key finding:** forgetting requires explicit weight reduction — substrate does not forget spontaneously

exp_d2_2_frequency_decay_cpu_v1 (HARD_PASS):
- Frequency-selective decay: at 3x capacity, retrievability tracks access frequency (AUC=0.886)
- High-freq items retained=0.929; low-freq items retained=0.051
- This is an ENGINEERED mechanism, not a substrate native property

exp_d2_7_intentional_forgetting_cpu_v1 (HARD_PASS):
- Intentional forgetting (GDPR-erasure): retained=1.000, forgotten=0.004
- Clean targeted erasure — no collateral damage

exp_substrate_time_decay_eviction_phase_diagram_v1_seed_13 (HARD_PASS):
- Phase diagram of time-decay x load: 3 regimes (healthy / too-aggressive / too-permissive)
- Healthy regime: ws>=0.95, clutter<=0.20 — 6/28 grid points
- Phase map fills in "controllable forgetting" parameter space

### 3. Cleanup layer provides no implicit temporal gradient

v2c cell (HARD_PASS) shows cleanup_recall=1.0 at alpha=[0.3, 1.0, 3.0, 10.0, 30.0] and only degrades at alpha=100 (cleanup_recall=0.9925 clean / 0.05 noisy). Cleanup operates on SIGNAL AMPLITUDE (cosine similarity), not write recency. An item written at t=0 and an item written at t=1000 produce identical cleanup dynamics if written at the same alpha. The "cleanup dominance" result means cleanup is a strong retrieval mechanism — it does not introduce any temporal ordering.

### 4. What static-Hebbian IS (vs what it's NOT)

**Static-Hebbian IS:**
- Capacity-limited associative memory with hard cliff at alpha_crit ~ O(N) (Hopfield bound)
- Interference mechanism: at high load, SNR degrades for ALL items equally
- Within-feasible-region: equal access probability for all stored items regardless of write order
- Eviction only via explicit decay or competing writes that push older items below noise floor

**Static-Hebbian IS NOT:**
- Ebbinghaus-curve compliant (no spontaneous time-based decay)
- Rehearsal-sensitive (re-writing item i 10x vs 1x: addressed below)
- Spaced-repetition responsive without explicit weight-track

### 5. Rehearsal / repetition effect

Re-writing item i N times in Hebbian: W += N * outer(v_k, v_q). This linearly scales the item's contribution to W. At alpha near the cliff, higher-weight items WIN the cleanup competition. So yes, rehearsal helps — but it is frequency-selective weight amplification, not time-decay recovery. The d2_2 frequency cell directly confirms this (AUC=0.886 frequency-tracking).

### 6. Catastrophic interference at scale

exp_a8: forgetting cliff at alpha=0.3 (N=default). Below cliff: zero catastrophic forgetting when writing sequentially. Above cliff: rapid recall collapse regardless of write order. This is consistent with the Hopfield capacity picture — no temporal structure.

---

## Updated Assessment

**P_deflated update: 0.32 → 0.08 (sharp downward)**

Dim A is not a hidden risk — it is a known structural property: substrate is STATIC-HEBBIAN with no native temporal dynamics. The failure mode is not "we forgot this could be an issue" but rather "the substrate by design has no time axis in storage." This is not overlooked — it is the foundational property that the entire forgetting-mechanisms arc (Wave 14, D2, recency cells) was designed to address.

**Dim A is CLOSED as a research gap. It has become a DESIGN CONSTRAINT.**

---

## Headline Findings

1. **Substrate retention is static-Hebbian: no spontaneous decay, no recency bias, no write-order effect.** By construction, all items in feasible capacity range have equal recall probability regardless of when they were written.

2. **Forgetting requires external mechanism injection** — three confirmed primitives: age-decay (half-life curve), frequency-selective decay (AUC=0.886), intentional erasure (GDPR-grade, retained=1.0).

3. **Cleanup dominance does not introduce temporal structure.** Cleanup operates on signal amplitude; recency and age are invisible to it.

4. **Rehearsal = frequency amplification.** Writing item i N times scales its W contribution proportionally; at the noise cliff, high-frequency items outlast low-frequency ones. This is the d2_2 frequency-decay mechanism, now CG.

5. **The Ebbinghaus-compatible forgetting curve is achievable but must be externally engineered** via age-decay injection, not substrate-native behavior.

---

## M3 Architecture Implication (Load-Bearing)

**Cortex must own all temporal structure.** This is a strong constraint:

- Conversational context has clear temporal structure: recent turns matter more than old ones
- Substrate provides NO native recency weighting — a message from 100 turns ago has identical recall weight to the previous turn, if both are within capacity
- M3 cortex layer must implement temporal decay externally: either (a) age-decay injection into W per write, (b) sliding-window eviction (LRU Kendall partial signal at tau=0.88 for M=40), or (c) hierarchical STM/LTM (M1.5 TWO-TIER pattern: K=100 STM / K=4096 LTM with TWOTIER already CG via Atom 18)

**The M1.5 TWO-TIER CG directly addresses Dim A** for conversational M3: STM holds recent context at high fidelity; LTM holds compressed older context. This is the correct architectural response to a static-Hebbian substrate.

**Cortex stochastic noise injection (2026-06-30 directive)** interacts here: substrate determinism means no native forgetting randomness. Cortex noise must provide selective access variation — items in LTM retrieved stochastically vs STM items retrieved deterministically. This is the correct coupling pattern.

---

## Cheapest Decisive Experiment (if USER wants confirmatory cell)

**Cell design: exp_dim_a_write_order_recency_probe_v1**
- N=4096, alpha=0.25 (feasible regime), M=N*alpha items
- Write items 1-M sequentially; record write timestamp
- Probe recall for early (i < M/4), middle (M/4 <= i < 3M/4), late (i >= 3M/4) items
- Discriminator: top-1 recall per positional bucket; null hypothesis = equal recall
- Expected: recall flat across buckets (no recency/primacy effect)
- Additional arm: write item_1 10x then items 2-M 1x; measure item_1 recall vs control
- Runtime: ~15 min local CPU at N=4096
- This is a confirmatory check, NOT a discovery cell (P=0.08 of finding anything new)

**Recommendation: defer this cell.** The prior arc (a8, d2_2, recency curve, time-decay phase diagram) already answers the question definitively. Only run if USER wants a single clean cell that consolidates the temporal picture for M3 architecture documentation.

---

## Falsifiable Predictions (for confirmatory cell)

1. Recall@(early bucket) = Recall@(late bucket) +/- 0.02 (no recency/primacy)
2. Item written 10x has recall advantage >= 0.15 over singly-written item at alpha=0.25 near cliff
3. Cleanup recall for early-written items = cleanup recall for late-written items at any alpha <= 30

---

## Cross-references

- exp_a8_continual_writes: HARD_PASS, no catastrophic forgetting, serial writes tested
- exp_recency_forgetting_curve_cpu_v1: HARD_PASS, engineered decay half-life curve
- exp_d2_2_frequency_decay_cpu_v1: HARD_PASS, frequency-selective retention AUC=0.886
- exp_d2_7_intentional_forgetting_cpu_v1: HARD_PASS, clean erasure
- exp_substrate_time_decay_eviction_phase_diagram_v1_seed_13: HARD_PASS, 3-regime phase map
- exp_lru_decay_kendall_v1: MIDDLE_BAND, partial LRU signal (tau=0.88 at M=40; mean tau=0.60)
- exp_substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c_seed_7: HARD_PASS, cleanup dominates at alpha<=30
- Atom 18 M1.5 TWO-TIER TWOTIER: K=100 STM + K=4096 LTM — the M3 architectural answer to Dim A
- `notes/research_hidden_phase_diagram_dimensions_2026-07-01.md` — parent drill
