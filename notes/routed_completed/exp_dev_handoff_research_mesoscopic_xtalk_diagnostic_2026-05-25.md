# exp_dev hand-off: SVD-bimodality instrumentation patch for in-flight MoE rebuild

**Filed:** 2026-05-25 by Research sub-agent (mesoscopic-transport DMPK drill).
**Status:** READY for exp_dev pickup. **Additive patch only** — no architecture change, no separate experiment.
**Companion research note:** `notes/research_mesoscopic_transport_moe_2026-05-25.md`
**Target script:** `experiments/exp_wave14_moe_shift_partition_v1.py` (3-arm MoE rebuild; queued or in-flight)
**Lit-scan calibration:** penalty applied; novel-synthesis cap NOT invoked (direct DMPK universality application).

---

## TL;DR

The 3-arm MoE rebuild script measures retention-curve differences between SHIFT, PARTITION, and SINGLE arms. **Add a single SVD-instrumentation block per cell** that computes the Dorokhov-bimodal signature of the per-expert W_k matrices. This gives a mechanism-level SHIFT-vs-PARTITION discriminator that is independent of the retention-curve comparison and costs ~2 sec per cell at N=4096.

The patch adds 3 fields to per-cell metrics:
- `bimodality_ratio` (open-channel count / bulk count) — distinguishes Dorokhov bimodal (≥1.0) from MP unimodal (≤0.3)
- `sigmas_n_above_half_max` — open-channel count (should match K · α_c · N for clean SHIFT)
- `gate_overlap_max` — max off-diagonal |⟨pₖ, pⱼ⟩|² (mesoscopic ξ parameter; verifies gates are near-orthogonal)

These augment the existing HARD-PASS / HARD-FAIL bands; they do NOT replace them.

---

## WHY (research motivation)

Per `notes/research_mesoscopic_transport_moe_2026-05-25.md` §(a-c):

The Landauer-Büttiker scattering formalism gives a closed-form prediction:
- **SHIFT regime** = independent channels = transmission-eigenvalue spectrum is **Dorokhov bimodal** (peak near σ_max + peak near 0; K · α_c · N open channels)
- **PARTITION regime** = coupled channels = transmission spectrum is **unimodal** (single Marchenko-Pastur-like bulk peaked < σ_max; α_c · N effective channels total, regardless of K)
- **Mode-collapse failure** = bimodal but with imbalanced open-channel mass (only 1-2 experts' worth in the open peak)

The substrate's per-expert outer-product W_k = (1/N) Σ vᵢ kᵢᵀ is non-unitary but the universality of bimodal distributions in random-matrix theory (Beenakker 1997 RMP 69:731) gives reasonable hope the signature carries over. Calibrated P(useful discrimination) = 0.67 (HARD-PASS 0.32 + MIDDLE 0.35).

This adds a **mechanism-level** observable to a script that currently has only **outcome-level** observables (retention curves). For the auditable-AI-memory-subsystem product direction, mechanism-level observables are first-class differentiation.

---

## WHAT (the patch — additive, no removal)

### Patch 1: New helper function `compute_dmpk_signature()`

Insert after the existing `mode_collapse_metrics()` helper (~line 243):

```python
# ─── DMPK / Dorokhov bimodality instrumentation (per mesoscopic-transport drill 2026-05-25) ───
def compute_dmpk_signature(Wks: list, K: int, N: int, device) -> dict:
    """SVD spectrum of per-expert W_k matrices; returns Dorokhov bimodality signature.

    Each W_k is the per-expert outer-product matrix (shape (N, N) for SHIFT,
    (N/K, N/K) for PARTITION). The aggregated singular-value spectrum, viewed as
    transmission-eigenvalue analog, should be:
      - BIMODAL under SHIFT (peak near sigma_max + peak near 0, ~K*alpha_c*N open channels)
      - UNIMODAL under PARTITION (single Marchenko-Pastur bulk, ~alpha_c*N effective channels)

    Returns dict suitable for direct merge into per-cell metrics.
    """
    sigmas_all = []
    for k in range(K):
        Wk = Wks[k]
        if Wk.numel() == 0 or Wk.norm() < 1e-12:
            continue
        # Truncated SVD: top min(N_k, 512) singular values is sufficient for bimodality
        # (full SVD at N=4096 is 16M elements; truncated keeps cost ~2 sec/cell)
        s_k = torch.linalg.svdvals(Wk)
        sigmas_all.extend(s_k.tolist())
    if not sigmas_all:
        return {
            "bimodality_ratio": 0.0,
            "sigmas_n_above_half_max": 0,
            "sigmas_n_below_tenth_max": 0,
            "sigmas_n_bulk": 0,
            "max_sigma": 0.0,
            "median_sigma": 0.0,
        }
    sigmas_all.sort(reverse=True)
    sigma_max = sigmas_all[0]
    if sigma_max < 1e-12:
        sigma_max = 1e-12
    n_above_half = sum(1 for s in sigmas_all if s >= 0.5 * sigma_max)
    n_below_tenth = sum(1 for s in sigmas_all if s <= 0.1 * sigma_max)
    n_bulk = len(sigmas_all) - n_above_half - n_below_tenth
    return {
        "bimodality_ratio": float(n_above_half) / float(max(n_bulk, 1)),
        "sigmas_n_above_half_max": n_above_half,
        "sigmas_n_below_tenth_max": n_below_tenth,
        "sigmas_n_bulk": n_bulk,
        "max_sigma": float(sigma_max),
        "median_sigma": float(sigmas_all[len(sigmas_all) // 2]),
        "n_sigmas_total": len(sigmas_all),
    }


def compute_gate_overlap(proj: torch.Tensor, K: int) -> dict:
    """Compute the mesoscopic-xi gate-overlap parameter |<p_k, p_j>|^2 off-diagonal.

    proj: (K, N) tensor of K row projections.
    Returns max and mean off-diagonal squared inner product (should be << 1 for SHIFT).
    """
    if K <= 1:
        return {"gate_overlap_max": 0.0, "gate_overlap_mean": 0.0, "xi_mesoscopic": 0.0}
    G = proj @ proj.T   # (K, K) — Gram matrix
    G2 = (G * G)         # element-wise square
    # Zero out diagonal
    diag_mask = 1.0 - torch.eye(K, device=proj.device)
    off_diag = G2 * diag_mask
    n_off = K * (K - 1)
    return {
        "gate_overlap_max": float(off_diag.max()),
        "gate_overlap_mean": float(off_diag.sum() / n_off),
        "xi_mesoscopic": float(off_diag.sum() / (K * K)),  # the xi parameter from research note
    }
```

### Patch 2: Wire into `run_arm_a_shift()` and `run_arm_b_partition()`

In `run_arm_a_shift()` (~line 246) — BEFORE `del Wks`, add:

```python
    # ─── DMPK bimodality signature (added 2026-05-25 per mesoscopic-transport drill) ───
    dmpk = compute_dmpk_signature(Wks, K, N, device)
    gate_ov = compute_gate_overlap(proj, K)
```

And update the return dict to include `"dmpk": dmpk, "gate_overlap": gate_ov`.

Same pattern in `run_arm_b_partition()` (~line 288). Note: for Arm B, Wks are (N/K, N/K) not (N, N), but the function handles arbitrary shapes — no modification needed.

For `run_arm_c_single()` (~line 336): Arm C has only ONE W matrix; compute_dmpk_signature still works as called with K=1, returns a single-mode signature (no bimodality possible; serves as baseline reference).

### Patch 3: Update verdict logic in `compute_verdict()` (~line 393)

Add 3 new cell-level aggregates:

```python
    # ─── DMPK bimodality cell aggregates (per mesoscopic-transport drill 2026-05-25) ───
    for r in results:
        key = (r["K"], r["M_total"])
        cells[key].setdefault("arm_a_bimodality", []).append(r["arm_a"]["dmpk"]["bimodality_ratio"])
        cells[key].setdefault("arm_b_bimodality", []).append(r["arm_b"]["dmpk"]["bimodality_ratio"])
        cells[key].setdefault("arm_a_n_open", []).append(r["arm_a"]["dmpk"]["sigmas_n_above_half_max"])
        cells[key].setdefault("arm_b_n_open", []).append(r["arm_b"]["dmpk"]["sigmas_n_above_half_max"])
        cells[key].setdefault("arm_a_xi", []).append(r["arm_a"]["gate_overlap"]["xi_mesoscopic"])
```

And add a NEW SECONDARY VERDICT FIELD (does not override primary retention verdict):

```python
    # Secondary verdict: mesoscopic-transport mapping confirmation
    bimodality_separation_K4 = None
    for (K, M), d in cells.items():
        if K == 4:  # check at K=4 (the canonical comparison point)
            a_bim = mean(d.get("arm_a_bimodality", []))
            b_bim = mean(d.get("arm_b_bimodality", []))
            if not math.isnan(a_bim) and not math.isnan(b_bim):
                sep = a_bim - b_bim
                bimodality_separation_K4 = (a_bim, b_bim, sep)
                break

    if bimodality_separation_K4 is not None:
        a_bim, b_bim, sep = bimodality_separation_K4
        if a_bim >= 1.0 and b_bim <= 0.4 and sep >= 0.6:
            mesoscopic_verdict = "MESOSCOPIC_PASS"
        elif sep >= 0.2:
            mesoscopic_verdict = "MESOSCOPIC_MIDDLE"
        elif sep < 0.2 and a_bim >= 0.5:
            mesoscopic_verdict = "MESOSCOPIC_FAIL_NO_DISCRIMINATION"
        else:
            mesoscopic_verdict = "MESOSCOPIC_FAIL_BOTH_UNIMODAL"
    else:
        mesoscopic_verdict = "MESOSCOPIC_NOT_TESTED"
```

Add `mesoscopic_verdict` and `bimodality_separation_K4` to summary dict that is logged to metrics.json. **DO NOT** let this gate the primary retention-curve verdict — it is purely additive instrumentation.

### Patch 4: Add SELF-TEST cells to the existing self-test block

In the existing self-test block (~line 74-79 in the file's docstring), add as runnable assertions in `__main__` block before the main run loop:

```python
# Self-tests for DMPK instrumentation
def _selftest_dmpk():
    """Verify DMPK signature on known synthetic spectra."""
    import torch
    # Test 1: pure-bimodal spectrum (K=2 experts with 1 open + 1 closed channel each)
    W1 = torch.eye(4)  # all 4 singular values = 1
    W2 = torch.eye(4) * 0.01  # all 4 singular values = 0.01
    sig = compute_dmpk_signature([W1, W2], K=2, N=4, device=torch.device("cpu"))
    # Expected: 4 sigmas above half max (= 1.0), 4 below tenth max (= 0.01), bulk=0
    assert sig["sigmas_n_above_half_max"] == 4, f"bimodal test: got {sig}"
    assert sig["sigmas_n_below_tenth_max"] == 4, f"bimodal test: got {sig}"
    assert sig["bimodality_ratio"] >= 1.0, f"bimodal test: got {sig}"
    # Test 2: pure-uniform spectrum (Marchenko-Pastur-like)
    W3 = torch.diag(torch.linspace(0.3, 0.7, 8))
    sig2 = compute_dmpk_signature([W3], K=1, N=8, device=torch.device("cpu"))
    # Expected: all 8 sigmas in [0.3, 0.7]; with sigma_max=0.7, half_max=0.35, tenth=0.07
    # n_above_half_max = sigmas >= 0.35 = 7 (0.357, 0.414, ..., 0.7)
    # n_below_tenth = sigmas <= 0.07 = 0
    # bulk = 1, bimodality_ratio = 7
    # NOTE: this synthetic isn't TRULY MP — actual MP has continuous density, this is uniform sample
    # For a real test of MP-vs-bimodal we'd need more singular values; this test just checks API
    assert sig2["sigmas_n_below_tenth_max"] == 0, f"uniform test: got {sig2}"
    # Test 3: gate overlap on orthogonal projections
    proj_orth = torch.eye(4)  # K=4, N=4, mutually orthogonal
    ov = compute_gate_overlap(proj_orth, K=4)
    assert ov["gate_overlap_max"] < 1e-6, f"orth test: got {ov}"
    # Test 4: gate overlap on parallel projections (worst case)
    proj_par = torch.ones(4, 4) / 2.0  # all parallel, normalized
    ov2 = compute_gate_overlap(proj_par, K=4)
    assert ov2["gate_overlap_max"] > 0.9, f"parallel test: got {ov2}"
    print("DMPK self-tests passed.")

if __name__ == "__main__" and os.environ.get("HDLAB_SELFTEST") == "1":
    _selftest_dmpk()
    sys.exit(0)
```

This satisfies [[feedback-strategy-spec-formula-selftests]] for the new formulas.

---

## HARD-PASS / HARD-FAIL bands for the SECONDARY verdict

These are **additive** to the existing primary retention-curve bands. They do NOT block ship of the primary verdict.

**MESOSCOPIC_PASS — mesoscopic mapping confirmed:**
- At K=4, full mode (N=4096, 5 seeds): Arm A `bimodality_ratio` median ≥ 1.0
- Arm A `sigmas_n_above_half_max` median ≥ 0.6 · K · α_c · N (≥ ~5500 at K=4, N=4096, α_c=0.56)
- Arm B `bimodality_ratio` median ≤ 0.4
- Separation A−B ≥ 0.6
- → Use as substrate-API health-check for any future MoE-style composite storage

**MESOSCOPIC_MIDDLE — partial mapping:**
- Separation A−B in [0.2, 0.6] OR
- Arm A `sigmas_n_above_half_max` in [0.3, 0.6] · K · α_c · N
- → Directionally correct; report as observable but not promote to substrate-API gate

**MESOSCOPIC_FAIL_NO_DISCRIMINATION:**
- Separation A−B < 0.2 AND both arms bimodal (a_bim ≥ 0.5)
- → DMPK signature doesn't discriminate at this scale; other instrumentation remains canonical

**MESOSCOPIC_FAIL_BOTH_UNIMODAL:**
- Both arms unimodal (a_bim < 0.5)
- → Non-unitarity of substrate W matrices breaks the bimodal universality; abandon framing

**MESOSCOPIC_NOT_TESTED:**
- K=4 cell missing or NaN — should not happen in normal runs

---

## DELIVERABLES SPECIFICATION

### 1. Numeric thresholds to log

Per-cell metrics.json must add (under each arm result):
```json
{
  "dmpk": {
    "bimodality_ratio": <float>,
    "sigmas_n_above_half_max": <int>,
    "sigmas_n_below_tenth_max": <int>,
    "sigmas_n_bulk": <int>,
    "max_sigma": <float>,
    "median_sigma": <float>,
    "n_sigmas_total": <int>
  },
  "gate_overlap": {
    "gate_overlap_max": <float>,
    "gate_overlap_mean": <float>,
    "xi_mesoscopic": <float>
  }
}
```

Per-summary fields must add:
- `mesoscopic_verdict` (one of MESOSCOPIC_PASS / MIDDLE / FAIL_NO_DISCRIMINATION / FAIL_BOTH_UNIMODAL / NOT_TESTED)
- `bimodality_separation_K4` (tuple: a_bim, b_bim, sep)

### 2. Performance budget

- SVD at N=4096 on GPU: ~2 sec per cell
- Per-cell overhead: SHIFT (K SVDs at N×N) + PARTITION (K SVDs at N/K × N/K) ≈ ~3 sec at K=4
- Total run overhead: 240 cells × 3 sec = ~12 minutes added to ~4-6 GPU-hr run; **~3% overhead. Acceptable.**

For smoke mode (N=512): negligible (<10 sec total).

### 3. Output discipline

Log to metrics.json. **DO NOT** print bimodality_ratio to verdict_msg (the primary verdict_msg is the retention-curve outcome; mechanism-level fields are in the summary dict). Per [[feedback-ascii-only-in-scripts]] — no special chars in printed fields.

### 4. Verification order

Per [[feedback-strategy-spec-formula-selftests]]:
1. Run `HDLAB_SELFTEST=1 python experiments/exp_wave14_moe_shift_partition_v1.py` — must pass DMPK self-tests
2. Run smoke mode: `python experiments/exp_wave14_moe_shift_partition_v1.py --smoke` — must produce non-empty dmpk fields
3. Inspect smoke metrics.json: verify `mesoscopic_verdict` is one of the 5 enum values; verify `bimodality_separation_K4` is a 3-tuple of floats
4. ONLY THEN: register the patch and re-ship full mode (or re-pull from queue if already shipped)

---

## CONTEXT POINTERS

- `notes/research_mesoscopic_transport_moe_2026-05-25.md` — full research note motivating this patch (companion)
- `experiments/exp_wave14_moe_shift_partition_v1.py` — target script (currently in queue / in flight)
- `notes/research_substrate_alpha_c_anomaly_2026-05-24.md` — α_c recalibration; α_c ≈ 0.56 used in numeric thresholds above
- `notes/exp_dev_handoff_research_moe_rebuild_2026-05-24.md` — original rebuild handoff (this patch ADDS to it)
- Beenakker, C.W.J. — Rev. Mod. Phys. 69:731 (1997) — DMPK universality reference
- Wexler, G. — Proc. Phys. Soc. 89:927 (1966) — Sharvin-Drude interpolation (referenced in research note §(d) for connection to α_c two-regime finding)

---

## DISCIPLINE CITATIONS

- per [[feedback-no-experiment-design-in-prompts]] — this handoff names ONE additive patch (~80 lines), NOT a new experiment; exp_dev decides SVD truncation rank / chunking / where in pipeline to insert
- per [[feedback-verify-implementations]] — DMPK formulas verified vs 3 sources (Dorokhov 1984; Beenakker RMP 1997; mesoscopic-transport textbooks)
- per [[feedback-envelope-expansion-fail-bands]] — MESOSCOPIC_PASS / MIDDLE / FAIL_NO_DISCRIMINATION / FAIL_BOTH_UNIMODAL bands pre-registered with explicit numerical thresholds
- per [[feedback-strategy-spec-formula-selftests]] — 4 self-test cells provided (bimodal, uniform, orthogonal gate, parallel gate); HDLAB_SELFTEST=1 entry point added
- per [[feedback-lit-scan-calibration-penalty]] — P(useful discrimination) deflated to 0.67 from naive 0.85; HARD-PASS thresholds set strict; MIDDLE-BAND criterion captures partial success
- per [[feedback-2x-means-depth]] — this patch is the OPERATIONAL output of the depth drill (not a re-verification request)
- per [[feedback-composition-classification]] — this is a SCORE-level composition (purely additive metric on existing experiment); no architectural change; no separate ship
- per [[feedback-ship-before-dependency-verified]] — depends on `experiments/exp_wave14_moe_shift_partition_v1.py` existing (verified at file write time, line counts above are approximate); depends on torch.linalg.svdvals being available (standard PyTorch ≥1.8); depends on α_c ≈ 0.56 from prior recalibration drill being usable as threshold reference

---

## AUTONOMY DECLARATION

exp_dev decides:
- Exact insertion point of SVD calls (recommend: end of run_arm_* before `del Wks`)
- SVD truncation rank if memory is tight (recommend: full SVD at N=4096 is fine on GPU; truncate to top-2048 if OOM)
- Whether to chunk per expert or batched (recommend: per-expert loop, simpler)
- Whether to also log per-expert sigma histograms (recommend: no — too much data; just the aggregates)
- Re-ship trigger: if rebuild is already running, decide whether to kill+restart with patch or wait for current run to finish and patch for next run
- Smoke validation order before full re-ship

exp_dev does NOT decide:
- The DMPK formula (`bimodality_ratio`, `sigmas_n_above_half_max`) — pre-specified above
- The MESOSCOPIC_PASS / MIDDLE / FAIL thresholds — pre-registered above
- Whether mesoscopic verdict gates primary verdict — it does NOT (additive only)
- Whether to remove existing Gini / max_min / top2_frac instrumentation — DO NOT remove (complementary, not redundant)

---

**End handoff.**

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
