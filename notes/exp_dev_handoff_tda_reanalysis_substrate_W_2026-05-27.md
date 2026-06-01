# Exp Dev hand-off — TDA re-analysis on existing substrate W artifacts

**Date.** 2026-05-27
**Owner.** Research → Exp Dev hand-off.
**Source drill.** `notes/research_persistent_homology_substrate_2026-05-27.md`.
**Strategic call.** OVERLAPPING (with one ORTHOGONAL sub-question: TDA-C SHIFT-vs-PARTITION via b_0-plateau width). P(adds 4th MoE diagnostic to cap_map) = 0.38.

---

## TASK

Ship a single experiment anchor that consumes existing W artifacts from v200-era MoE experiments + battery v1 fixtures and emits a 5-probe TDA re-analysis (TDA-A through TDA-E per drill section b).

**No new W generation. No GPU. CPU-only. Existing artifacts only.**

## WHY

Substrate has rejected all standard phase-class labels; SKAH-M battery v1 returned MIDDLE_BAND. TDA is overlapping with existing spectral / free-prob diagnostics via the persistent-spectral-graph bridge (Wang-Nguyen-Wei 2020), with one genuinely orthogonal sub-question: does TDA's b_0-plateau width agree with free-additive top-edge ratio + DMPK SVD-bimodality on the SHIFT-vs-PARTITION MoE classification? If yes (P=0.38), this becomes a 4th cross-family diagnostic in the cap_map and strengthens the substrate-product MoE SLA story.

## CONTRACT

Exp Dev decides:
- Anchor name (suggest prefix `tda_reanalysis_5probe_`)
- Which existing W artifacts to consume (Exp Dev's call — at minimum 2 SHIFT-labeled MoE runs + 2 PARTITION-labeled MoE runs + 1 ambiguous run + 1 battery v1 fixture for plateau analysis)
- Whether to use ripser, gudhi, giotto-ph, or a pure-PyTorch implementation (suggest ripser for b_0/b_1; pure-PyTorch Laplacian eigendecomp for b_0(τ) trajectory to avoid new dependency burden)
- Queue choice (suggest local CPU per [[feedback-laptop-cpu-quick-probes]] given <60s/cell budget per anchor; if pushed to remote CPU, also fine)
- ETA (suggest <2h end-to-end)

Pre-register the 5 probe HARD-PASS / HARD-FAIL thresholds (lifted from research note section b):

| Probe | HARD-PASS | HARD-FAIL | MIDDLE |
|---|---|---|---|
| TDA-A b_0(τ) trajectory | Monotone non-increasing AND plateau at b_0 ∈ {3,4} for finite τ-interval | Non-monotone (e.g., b_0 spikes) | Single-value or 2-value plateau only |
| TDA-B longest b_1 bar ratio (substrate / random control) | ratio ≥ 1.5 with p<0.05 (≥5 seeds) | ratio ≤ 1.1 | 1.1 < ratio < 1.5 |
| TDA-C b_0-plateau width SHIFT-vs-PARTITION agreement | Agreement with free-additive + DMPK on ≥4/5 cases; width monotonic in inter-expert coupling | Agreement on ≤2 cases OR non-monotonic width | Agreement on exactly 3 cases |
| TDA-D long-persistence-bar count vs plateau count | count ∈ {3,4} long bars with lifetime > 0.3·max_lifetime AND ≤1 short noise | Continuous distribution (no gap) | count ∈ {2, 5} |
| TDA-E predicted plateau heights | max \|pred-obs\| < 0.05 across 3 plateaus | \|pred-obs\| ≥ 0.10 on ≥2 plateaus | one plateau off by 0.05-0.10 |

**Joint verdict rules:**
- TDA-OVERLAPPING-USEFUL: TDA-C HARD-PASS (≥4/5 agreement). P=0.38. Ship as cap_map 4th MoE diagnostic.
- TDA-NOVEL-USEFUL: TDA-B AND TDA-D BOTH HARD-PASS. P=0.10. Open new cap_map row for topological substrate fingerprint.
- TDA-CONSISTENT-REDUNDANT: TDA-A monotone matching spectral gap; TDA-C parity with free-additive (not better). P=0.32. Log as confirmation; close orthogonality question.
- TDA-INCONCLUSIVE / IRRELEVANT: TDA-C HARD-FAIL or TDA-D continuous distribution. P=0.20. Close algebraic-topo direction structurally.

**Self-test cells (formula-selftests per [[feedback-strategy-spec-formula-selftests]]):**
- b_0(τ=0) of fully connected weighted graph = 1 (sanity)
- b_0(τ=max(W)+ε) of any graph = N (all-singleton sanity)
- Persistence barcode of N=10 K_10 complete graph at uniform weight 1.0: single b_0 bar [1.0, ∞), b_1 = b_2 = ... = 0 (textbook sanity)
- Persistence barcode of N=10 disjoint K_5 ⊔ K_5 at intra-cluster weight 0.9, inter-cluster weight 0.1: b_0(τ < 0.1) = 2, b_0(τ > 0.1) = 1; SHIFT/PARTITION discriminator sanity case

**Output JSON schema** (suggested):
```
{
  "verdict": "<PASS|FAIL|PARTIAL|MIDDLE_BAND>",
  "verdict_msg": "<one-line summary keyed by probe>",
  "tda_a": {"b0_tau_trajectory": [[tau, b0], ...], "plateau_found": bool, "plateau_b0": int, "plateau_width": float},
  "tda_b": {"substrate_longest_b1": float, "random_longest_b1_mean": float, "ratio": float, "p_value": float, "n_seeds": int},
  "tda_c": {"experiments": [{"name": str, "tda_call": "SHIFT|PARTITION|MIXED", "free_additive_call": ..., "dmpk_call": ..., "agreement": bool}], "n_agree": int, "n_total": int, "width_monotonic": bool},
  "tda_d": {"long_bar_count": int, "long_bar_lifetimes": [float, ...], "short_bar_count": int, "gap_observed": bool},
  "tda_e": {"predicted_heights": [float, float, float], "observed_heights": [float, float, float], "max_abs_diff": float},
  "joint_call": "<TDA_OVERLAPPING_USEFUL|TDA_NOVEL_USEFUL|TDA_CONSISTENT_REDUNDANT|TDA_INCONCLUSIVE>"
}
```

## AUTONOMY

Exp Dev has full autonomy on:
- Implementation language (Python + PyTorch + ripser preferred; pure-Python fallback OK)
- Artifact selection (pick the strongest available SHIFT/PARTITION examples; if v200-era MoE artifacts not extant, surface back to orchestrator with a no-ship request)
- Filtration metric (cosine recommended; L2 acceptable if cosine pathologically expensive)
- ASCII-only print() / verdict_msg per [[feedback-ascii-only-in-scripts]]

## NOT IN SCOPE

- New W generation
- GPU compute
- MoE re-run
- Higher Betti numbers (b_2, b_3, etc.) — b_0 and b_1 sufficient
- Cap_map edits (Exp Dev does not modify cap_map; verdict_handler does that based on the joint_call)

## DEPENDENCIES

- **Confirm W artifact availability**: before queuing, verify ≥2 SHIFT-labeled + ≥2 PARTITION-labeled MoE W artifacts exist on disk OR can be regenerated from saved seeds within a 5-min budget. Per [[feedback-ship-before-dependency-verified]] — DO NOT ship anchor without this confirmation.
- **Confirm ripser or equivalent installable**: pip install ripser is fast; if blocked by sandbox, fall back to pure-Python Vietoris-Rips for N=1024 (computable but slower — budget ~10 min instead of ~1 min per case).

## EXPECTED VERDICT DISTRIBUTION (calibrated)

- TDA_OVERLAPPING_USEFUL: P = 0.38 — most likely; ships 4th MoE diagnostic
- TDA_CONSISTENT_REDUNDANT: P = 0.32 — second-most likely; closes orthogonality question
- TDA_INCONCLUSIVE: P = 0.20 — closes algebraic-topo direction
- TDA_NOVEL_USEFUL: P = 0.10 — opens new cap_map row

## POST-VERDICT ACTIONS (for verdict_handler)

- TDA_OVERLAPPING_USEFUL → cap_map: add 4th MoE diagnostic row; commit "Cap map: TDA-C SHIFT/PARTITION diagnostic LOCKED at parity with free-additive (post-tda_reanalysis_5probe_)"
- TDA_NOVEL_USEFUL → cap_map: open "topological substrate fingerprint" row; flag for product whitepaper integration
- TDA_CONSISTENT_REDUNDANT → cap_map: no change; status_log entry "TDA confirmed as redundant readout; algebraic-topo closure stands for novel-diagnostic purposes"
- TDA_INCONCLUSIVE → cap_map: no change; lock in Tier-3 algebraic-topo closure rule with reinforced calibration penalty
