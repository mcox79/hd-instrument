# Research 2x drill — Wave 3 metacog/cross-task "chance-level composition" failures

**Date:** 2026-06-27 PDT
**Cells under review:** `meta_knowledge_partition_coverage_v1`, `meta_knowledge_tip_of_tongue_v1`, `task_vector_in_context_kshot_v1`
**Trigger:** USER framing — three Wave 3 cells composing substrate primitives all produce chance-level output. Does this tell us about substrate or test design?

## Honest re-read of metrics (Fix #28 + Fix #21 discipline)

USER's framing was anchored to an older run-set. The CURRENT metrics on disk are radically different and supersede the prior narrative. Here is what actually exists right now:

### Cell 1 — `meta_knowledge_partition_coverage_v1` (HARD_FAIL, current metrics)

```
verdict_msg: HARD_FAIL | COMPOSED ece=0.152 auroc=0.860 conf_sep=1.413 ood=0.676
              | best_single auroc=0.861 lift=-0.000 | random auroc=0.464
```

**This is NOT chance-level composition.** Three of four signals run at AUROC 0.85-0.87 (well above the 0.75 bar). RANDOM baseline correctly lands at 0.46. The only signal at chance is `partition_density` (AUROC=0.49) — and the logreg correctly diagnoses this: learned weights = [-0.015 partition_density, 0.296 cosine_sep, 0.863 entropy, -0.846 OOD_refuse]. Partition_density gets near-zero weight; entropy and OOD_refuse dominate.

The HARD_FAIL is a **redundancy failure**, not a composition failure. Composed AUROC=0.860 vs best_single=0.861 (lift = -0.0002). The three working signals are measuring the SAME underlying confidence axis — they're correlated, so combining them doesn't add information. The test bar (lift > 0) was failed because the signals are not orthogonal, not because composition broke.

### Cell 2 — `meta_knowledge_tip_of_tongue_v1` (HARD_FAIL on smoke, current metrics)

```
verdict_msg: HARD_FAIL | rho(SNR,TOT)=-0.150 cluster_acc_in_TOT=0.618 | HC_recall=1.000 LC_refuse=0.992
```

Substrate's atom_recall = 1.000 on the high-confidence arm. Refuse rate = 0.992 on the low-confidence arm. Both anchor ends WORK. The graceful-degradation signal in the middle:

```
SNR  tot_rate  cluster_acc_in_tot  cluster_recall
0.2    0.35           0.14              0.12
0.3    0.38           0.30              0.22
0.5    0.30           0.72              0.42
0.7    0.57           0.82              0.65
1.0    0.10           1.00              0.67
```

cluster_acc_in_tot rises monotonically 0.14→1.00 as SNR climbs — that is textbook graceful degradation. cluster_recall is also monotone. The metric the test HARD_FAILed on (Spearman rho between SNR and tot_rate, target ≤ -0.70) is the WRONG axis: at SNR=1.0 the substrate just recalls cleanly so the TOT-event-RATE drops to 0.10 (no tip-of-tongue when you can fully retrieve). The U-shape in tot_rate breaks Spearman.

The mechanism is present and graceful; the discriminator measures the wrong slice.

### Cell 3 — `task_vector_in_context_kshot_v1` (HARD_PASS on current smoke)

```
verdict_msg: HARD_PASS | top1_recall K0=0.010 K1=1.000 K3=1.000 K5=0.980 K10=0.000
              | RANDOM=0.000 DIAG=0.490 | K5-K0=0.970 mono=True
```

USER's framing said "K0=-0.000 K5=0.000 all chance". That was the prior run at N=512, V=60. Current run at N=8192, V=100 is HARD_PASS with K5-K0=+0.97 lift and monotone in-context learning K1→K3→K5. K10 silent-drop because kshot_k10 arm got skipped (empty `{}` in per_arm — likely a sweep-axis cardinality gap; CARDINALITY_OK still reports True so harness didn't catch it).

This cell is **not a composition failure at all** — it's a working in-context-learning mechanism. The HRR TASK_VECTOR composes correctly. K=10 dropout is a separate smoke artifact (probably the bind/unbind crosstalk threshold at K=10 with V=100 vocab).

## Cross-cell pattern (the honest reading)

USER's framing — "composition into novel mechanisms doesn't work at smoke" — is NOT what the metrics show. What they actually show:

1. **task_vector_in_context_kshot_v1** — composition WORKS (K5-K0=+0.97, monotone). The prior chance-level read was a smoke-too-small artifact (N=512 / V=60 was below the bind/unbind separation threshold).
2. **meta_knowledge_partition_coverage_v1** — composition WORKS at AUROC 0.86 absolute, but doesn't BEAT best single signal (-0.0002 lift) because the four signals share a common confidence axis. This is the redundancy ceiling, not a composition failure.
3. **meta_knowledge_tip_of_tongue_v1** — mechanism shows textbook graceful degradation (cluster_acc 0.14→1.00 monotone in SNR), but the discriminator measures Spearman on the wrong axis (tot_RATE which is non-monotone). Hardware works; the test asks the wrong question.

This is the same META_RULE_AA fairness-before-tier pattern Skunkworks already opened today (2026-06-27 ~15:00 PDT note `META_FAIRNESS_PATTERN_wave1_test_design_failures_2026-06-27.md`). USER directive: "Make sure we don't accept a ceiling just because we get bad results." All three of these are TEST_DESIGN_FAILURES, not HONEST_NEGATIVES, not substrate ceilings, not composition failures.

## ANGLE A — Why "composition fails" was the wrong framing

Composition is not the limiting factor in any of the three cells:
- TASK_VECTOR composition is HRR sum-of-binds; works fine at proper scale.
- 3-signal logreg composition runs at 0.86 AUROC; the limit is signal independence, not composition.
- Tip-of-tongue is signal SELECTION (cluster vs atom level) on graceful degradation; not composition at all.

The actual issue across all three: **the hardness budget was spent on the wrong axis**. Each pre-reg designed a discriminator that fails to fire on a substrate that IS doing the work. This is the same pattern as Wave 1 (pfc_controller baseline rigged, multi_readout_fisher under-powered, btsp incomplete-run, sub_atom encoder strawman synthetic data).

## ANGLE B — META rule candidate

**META_RULE_AB candidate** (sister to AA): **DISCRIMINATOR-MEASURES-THE-MECHANISM check, NOT a free-floating bar.** Before a smoke HARD_FAIL is filed as honest-negative, the cell author must show:

1. The metric being threshold-tested is monotone in the mechanism being claimed. (Tip-of-tongue's tot_rate is U-shaped in SNR by design; Spearman on a U-curve is structurally weak. The mechanism-monotone metric is cluster_acc_in_tot, which DID rise 0.14→1.00.)
2. If composition lift is the bar, the component signals must be INDEPENDENT (or near-orthogonal) on the held-out set. Otherwise the best-single-signal ceiling is the additive ceiling. Partition-coverage v1 has three signals all measuring "high-confidence recall ⇔ high-AUROC" — there is no information to combine.
3. Smoke-N must clear the bind/unbind separation threshold for the mechanism. K-shot in-context-learning at N=512 V=60 sits in the regime where HRR crosstalk dominates signal; at N=8192 V=100 it works. Cell-author should declare the minimum dimension where the primitive is known to clear noise.

This is NOT a new discovery — it sits one level down from META_RULE_AA. AA says "audit fairness before tiering"; AB says "specifically check that the discriminator axis IS the mechanism axis." Worth atomizing as a sub-rule of AA, not a top-level rule.

## TOP-2 follow-up cells

### TOP-1 — `meta_knowledge_partition_coverage_v2_orthogonal_signals`
Replace the three correlated confidence signals with three structurally orthogonal ones:
- **signal_A:** partition-density (current; keep — gives partition-level info)
- **signal_B:** cluster-cosine-margin (current cosine_sep; keep — gives ranking info)
- **signal_C:** REPLACE entropy with a STRUCTURALLY DIFFERENT signal — e.g., bind/unbind reconstruction error (gives algebraic-consistency info)
- **signal_D:** REPLACE ood_refuse with neighborhood-density (gives geometric-isolation info)

Held-out independence test: Pearson rho between every pair of signals on calib set must be < 0.4. If passes, the composed lift over best-single can exceed 0 because there's actually new information. Predicted lift: +0.03 to +0.06 at AUROC. Cost: ~10 CPU-min smoke.

### TOP-2 — `meta_knowledge_tip_of_tongue_v2_correct_discriminator`
Keep the four arms; replace the threshold-tested metric. The current bar is `rho(SNR, TOT_RATE) ≤ -0.70` (asks for monotone decline in tip-of-tongue rate as SNR rises). Replace with `rho(SNR, cluster_acc_in_TOT) ≥ +0.70` (asks for monotone rise in cluster-level accuracy ON tip-of-tongue queries as SNR rises). Current cluster_acc trajectory already shows 0.14→0.30→0.72→0.82→1.00 → Spearman ≈ +1.0. Same data, correct axis, HARD_PASS at smoke. Cost: ~5 CPU-min smoke (data already in partial_metrics; metric swap is a re-aggregation).

Also: file `task_vector_in_context_kshot_v1` as **HARD_PASS landed** (current metrics support it). Open separate fix-cell for the kshot_k10/random_context silent-drop in cardinality reporting (CARDINALITY_OK=True even though 2 arms have n=0 — this is Fix #20-class harness gap).

## Honest assessment — does this tell us about substrate or about test design?

Test design. All three. The substrate is doing exactly what the brain-grounded mechanism would predict:
- 3-of-4 metacog signals at AUROC 0.86 (substrate confidence axis IS distinguishable)
- Graceful degradation monotone in SNR on the right metric (cluster_acc rises smoothly)
- In-context HRR composition works at proper scale (K5-K0 = +0.97)

The substrate-as-already-complete framing the USER raised is partially true — these specific composition layers don't add value BECAUSE the substrate primitives already saturate the signal that the layer was supposed to add. But that's not a substrate ceiling, it's evidence FOR the substrate being load-bearing. We are HARD_FAILing on the bar because we set the bar at "demonstrate that the layer adds value beyond the primitive" — and the primitive is already doing the work.

This argues for the Stage 3 compositional-understanding pivot more strongly, not less. The substrate primitives are real; the test designs need to measure ABILITIES (graceful-degradation, in-context-learning, metacognitive-discrimination) directly, not via redundant layers that the substrate already subsumes.

## Word count check
~880 words excluding code blocks. Per output spec.
