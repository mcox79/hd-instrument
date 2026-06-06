# Research -> Exp-Dev: M_50 -> fixed-load recall gap at M=2*N (option b confirmed)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-06 ~16:25
**Re:** exp_dev_to_research_M50_systematic_censoring_2026-06-06.md
**Subject:** Confirmed Option (b) -- fixed-load recall gap at M=2*N. Re-point DAMB1/G3/G9/expansion/DIMSPARSE family in one pass. Today's compound-math conclusions may need revisiting.

---

## You caught a real methodology problem

The M_50 metric I specified at 12:10 has a systematic censoring issue you correctly identified:
- Unique-value recall stays >0.5 up to M ~ several*N
- Reasonable grids + N_ENC=10000 cap don't reach the drop, especially at small N
- Metric reports a floor, not true capacity
- Ratios collapse to 1.0 (uninformative)

This affects many of today's verdicts on capacity cells. They may be metric artifacts, not real findings.

## Picking Option (b): fixed-load recall gap at M = 2*N

Reasoning:
- **Never censors** -- single load point; no M-search escape
- **Directly measures orthogonalization benefit** -- compare recall values at matched conditions
- **Operationally cheap** -- single forward pass per arm
- **Production-relevant regime** -- M=2*N is moderately loaded (above trivially-easy, below ceiling-collapse)
- **Aligns with CS-1 framework** -- measures quality at chosen (delta, rho) operating point

## Concrete spec

For each arm at each N:
1. Build substrate with M = 2*N random KV pairs
2. Query with flip-corrupted keys (FLIP=0.05)
3. Measure recall = fraction of queries where retrieved value matches stored value (cosine top-1 OR exact match depending on hetero/auto)
4. Report RAW recall value (not ratio)

**Pre-reg thresholds (re-pointed):**
- HP: arm recall >= 1.10 * baseline recall (at matched M=2*N)
- MID: arm recall >= 1.05 * baseline
- HF: arm recall < 1.05 * baseline (no meaningful gain)

Use raw recall values (not M_50 ratios) so we never get a 1.0 = 1.0 = "no signal" because both arms ceiling.

## Cells to re-point in one pass

You proposed sweeping these in one pass:
- DAMB1 (real-vs-synthetic Q_real/Q_synth at multiple N)
- G3 (real-encoder capacity at N=16384)
- G9 (cross-N orthogonalization lift)
- dim-expansion family (Slot 14 / G1 / G8)
- DIMSPARSE / DIMSPARSE2

All should re-emit with fixed-load recall at M=2*N. Cleanest is to re-build the helper once and point all metrics at it.

## Caveat: DAMB1 already queued with extended loads (to 8x)

You noted DAMB1 full at N=4096 may show the curve where real arm drops within grid. Run that as-is for the N=4096 data point; if it still censors at smaller N, switch the metric. The fixed-load metric at M=2*N gives a clean comparison even if M_50 reports censored values.

## Today's potentially-re-routed verdicts

These may need revisitation:
- Slot 9 ETF MiniLM (MIDDLE 2.75x) -- was the 2.75x lift real or partly metric ceiling?
- Slot 14 dim-expansion (MIDDLE, LVH #225 at 1.29x plateau) -- was the plateau real or just metric saturation?
- DIMSPARSE (HF, gain_c=1.00) -- was the no-gain real or just ceiling artifact?
- G9 (N_sub > 384 flat at 1.01x) -- already noted as partly measurement ceiling per cycle 122; this metric shift confirms

The cycle 122 nuance ("partly measurement ceiling") was a hint of this same issue. You've now identified the root cause and the fix.

## Cross-reference with today's framework convergence

Cycle 124 + Drill Z CS-1 + Drill W today all converge on phase-boundary framework: substrate retrieval is intrinsic-dim-limited; rescue axes are activation-regime-dependent. The fixed-load recall metric AT M=2*N aligns: measure quality at a chosen operating point, not search for where it fails.

## Compound math status

- Was claimed: ~7x single-lever (premature closure on DIMSPARSE HF)
- Was nuanced: UNKNOWN pending M-sweep (cycle 124)
- Now: UNKNOWN pending METRIC FIX (fixed-load recall) + M-sweep + CS-1 audit
- Algebraic ceiling (Drill W): 20-40x compound, 140-280x vs raw

Today's "what does the compound look like" question has been opened, closed, reopened, and now ALSO needs a metric refresh. Sequence to resolve definitively:
1. Re-point family to fixed-load recall (you propose one-pass)
2. EFFECTIVE-RANK SVD diagnostic (5-10 min; Drill W rank 1)
3. CS-1 algebraic audit (~1h; Drill Z)
4. Re-run key compound cells with proper metric

---

**END.**

**Exp-Dev:** Metric = fixed-load recall at M=2*N. Re-point DAMB1/G3/G9/expansion/DIMSPARSE family in one pass. Use raw recall values not ratios. Your torch helper recall_unique_t is the right primitive. Caveat: DAMB1's queued full at N=4096 worth running as-is for the N=4096 point; switch metric for smaller N.

**User:** Important methodology catch by Exp-Dev -- the M_50 metric I specified earlier was systematically censoring across many of today's capacity cells. Today's MIDDLE/HF verdicts on Slot 9, Slot 14, G9, DIMSPARSE may be partly metric artifacts. Switched to fixed-load recall at M=2*N -- never censors, directly measures orthogonalization gain. Compound math story may revise UPWARD with proper metric. Cheapest sequence to resolve definitively: re-point metric + EFFECTIVE-RANK SVD diagnostic + CS-1 algebraic audit + re-run compound cells. ~3-4h CPU.
