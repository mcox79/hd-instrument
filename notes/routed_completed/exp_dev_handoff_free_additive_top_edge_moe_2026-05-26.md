# exp_dev hand-off — free-additive-convolution top-edge instrumentation for MoE rebuild

**Filed:** 2026-05-26 by Research sub-agent.
**Source drill:** `notes/research_free_probability_substrate_2026-05-26.md` (Q3 → P3.1 load-bearing).
**Routing:** companion to in-flight MoE rebuild + DMPK xtalk instrumentation (`exp_dev_handoff_research_mesoscopic_xtalk_diagnostic_2026-05-25.md`).
**Pause-gated:** YES. Honor `data/orchestrator_paused.flag` per [[feedback-obey-user-pause-explicitly]].

---

## TASK

Add a single-cell-per-arm instrumentation hook to the MoE rebuild (next iteration, ideally folded into the same rebuild that already adds the DMPK SVD signature). The hook computes the **top singular value ratio** between SHIFT-aggregate and PARTITION-per-expert and compares to the free-additive-convolution closed-form prediction.

## WHY

Free-additive-convolution governs the bulk-edge of the aggregate W spectrum when K experts each store a partial W_k. The closed-form ratio prediction (load-bearing P3.1 from the drill):

- SHIFT mode: λ_top^aggregate ≈ K·(1+√c)², with c = M_total / (K·N)
- PARTITION mode: λ_top^per-expert ≈ √(N/K)·(1+√(Kc)) — so K·λ_top^per-expert ≈ K·√(N/K)·(1+√(Kc))

Ratio λ_top^SHIFT / (K · λ_top^per-PARTITION-mean) is a **scalar** observable distinct from the DMPK bimodal-histogram observable. The two together pin down the SHIFT/PARTITION regime at both the bulk-edge level AND the channel-by-channel level — substantially raising the falsification power per cell at zero additional compute.

## CONTRACT

### Input

Existing per-cell `(W_k_shift_list, W_k_partition_list, K, N, M_total)` tensors already computed by the rebuild + DMPK instrumentation.

### Helper to add (Python; ~25 lines):

```python
def compute_free_additive_top_edge_ratio(Wks_shift, Wks_partition, K, N, M_total):
    """Free-additive-convolution prediction: top-edge ratio SHIFT vs PARTITION.

    Returns dict with empirical + predicted + match flag.
    """
    import torch
    W_shift_total = sum(Wks_shift)
    sigma_top_shift = torch.linalg.svdvals(W_shift_total)[0].item()
    sigma_tops_part = [torch.linalg.svdvals(W)[0].item() for W in Wks_partition]
    sigma_top_partition_mean = sum(sigma_tops_part) / max(K, 1)
    c = M_total / max(K * N, 1)
    sigma_top_shift_predicted = float(K) * (1.0 + c**0.5)**2
    sigma_top_partition_predicted = (1.0 + (K * c)**0.5)**2
    ratio_empirical = sigma_top_shift / max(K * sigma_top_partition_mean, 1e-9)
    ratio_predicted = sigma_top_shift_predicted / max(K * sigma_top_partition_predicted, 1e-9)
    return {
        "sigma_top_shift": sigma_top_shift,
        "sigma_top_partition_mean": sigma_top_partition_mean,
        "sigma_top_shift_predicted": sigma_top_shift_predicted,
        "sigma_top_partition_predicted": sigma_top_partition_predicted,
        "ratio_empirical": ratio_empirical,
        "ratio_predicted_free_additive_conv": ratio_predicted,
        "match_within_15pct": abs(ratio_empirical - ratio_predicted) / max(ratio_predicted, 1e-9) < 0.15,
    }
```

### Output

Persist results into the existing per-cell metrics dict (alongside DMPK `sigmas_*` keys). Aggregate over seeds per (K, M_total) cell using mean + IQR for the ratio columns.

### Pre-registered bands (P3.1 + P3.2 + P3.3 per drill section c)

- **HARD-PASS (free-additive-convolution confirmed):** mean `match_within_15pct == True` across ≥ 80% of seeds at K ∈ {2, 4}; AND mean `ratio_empirical` within ±15% of `ratio_predicted_free_additive_conv` at the operating M_total.
- **HARD-FAIL (free-additive-convolution does NOT govern aggregate spectrum):** mean `ratio_empirical` off by > 30% from prediction at K ∈ {2, 4}.
- **MIDDLE BAND:** ratio off 15-30% — finite-N corrections likely; mark INCONCLUSIVE and request N=16384 re-confirmation; do NOT escalate as failure.
- **K=8 EXEMPTION:** at K=8, N=4096, N/K=512 is borderline for asymptotic freeness; treat MIDDLE-BAND there as expected, not as failure.

### Verdict envelope

Standard verdict envelope (PASS / FAIL / PARTIAL / UNKNOWN per cell with the bands above).

## AUTONOMY

- Choose smoke vs full mode based on queue state and pause flag.
- Choose K-sweep granularity within {2, 4, 8} default; may add K=1 control if useful.
- If the rebuild has already shipped, file as a re-analysis pass on existing tensors (no GPU re-run) by adding the helper to the post-hoc analysis script and re-reading the per-cell W_k snapshots if persisted.
- If per-cell W_k tensors were not persisted in the original rebuild, ship as a re-run with persistence enabled; ETA ~ same as original rebuild + ε.

## NOT IN SCOPE

- Do NOT modify the DMPK SVD code; this is purely additive.
- Do NOT change architecture, K-sweep design, or pre-registered DMPK bands.
- Do NOT attempt to derive the closed form here; the formula is settled by the drill note.

## CROSS-REFS

- [Free-probability second drill](research_free_probability_substrate_2026-05-26.md) — full pre-reg + caveats
- [Mesoscopic-transport DMPK companion](exp_dev_handoff_research_mesoscopic_xtalk_diagnostic_2026-05-25.md) — instrumentation cell this folds into
- [α_c anomaly diagnostic](research_substrate_alpha_c_anomaly_2026-05-24.md) — substrate-IS-linear-heteroassoc grounding

---

**End hand-off.**

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
