# Exp Dev Queue Routing: Heavy-Research-Night Batch 2

Filed: 2026-05-25
Queue: local_cpu_queue

```
queue=local_cpu_queue name=wave14_saddle_saadsolla_plateau_arithmetic_v1 script=experiments/exp_wave14_saddle_saadsolla_plateau_arithmetic_v1.py prereg=preregs/2026-05-25_saddle_saadsolla_plateau_arithmetic_v1.md timeout=120
queue=local_cpu_queue name=wave14_verdict_dispatch_context_v1 script=experiments/exp_wave14_verdict_dispatch_context_v1.py prereg=preregs/2026-05-25_verdict_dispatch_context_v1.md timeout=120
queue=local_cpu_queue name=wave14_pac_bayes_kl_extended_corpus_v1 script=experiments/exp_wave14_pac_bayes_kl_extended_corpus_v1.py prereg=preregs/2026-05-25_pac_bayes_kl_extended_corpus_v1.md timeout=120
queue=local_cpu_queue name=wave14_taxonomy_contrast_retention_sep_v1 script=experiments/exp_wave14_taxonomy_contrast_retention_sep_v1.py prereg=preregs/2026-05-25_taxonomy_contrast_retention_sep_v1.md timeout=120
```

## Batch summary

4 local_cpu Tier C re-analyses continuing heavy-research-night deep drilling.

1. **wave14_saddle_saadsolla_plateau_arithmetic_v1**: Drills into whether the 3 plateau heights (G1=0.899, G2=0.804, G3=0.633) satisfy the Saad-Solla EQUAL-ANGLE spacing prediction (theta_mid = (theta_top + theta_bottom)/2 via cos^2 map), not just equal-height. Equal-angle is the structural prediction of the mode-overlap ODE; equal-height is the first-order approximation. Smoke: NEITHER_EQUAL (angle_gap_ratio=0.70, height_gap_ratio=0.56 -- both outside thresholds, suggesting the plateau spacing is NOT well-explained by simple Saad-Solla equal-spacing arithmetic despite the discrete BIC evidence from v1).

2. **wave14_verdict_dispatch_context_v1**: Follow-up to multi-agent gap (pass 0.36 vs single 0.69, p=0.019, V=0.32). Tests which dispatch sub-patterns drive the gap: inline-vs-wrapper, concreteness keyword signal, temporal stability. Smoke: NO_REFINEMENT (no sub-pattern exceeds V=0.25; gap persists but is not explained by dispatch style -- consistent with selection-bias interpretation where complex hypotheses go multi-agent).

3. **wave14_pac_bayes_kl_extended_corpus_v1**: Applies v1 KL-retention power-law fit to the full 109-value Bet B corpus. Smoke: FLOOR_VIOLATED (power-law extrapolation gives floor > observed_retention for all 107 cells; the 3-anchor fit is too noisy for extrapolation -- confirms GPU v2 is needed for direct Fisher KL measurement, cannot shortcut via extrapolation).

4. **wave14_taxonomy_contrast_retention_sep_v1**: Contrasts K=2/3/4/6 taxonomies on silhouette, F-ratio, incremental efficiency, product clarity, and Saad-Solla compatibility. Smoke: TWO_TIER_SUFFICIENT (F-ratio at K=2 is 334 vs 256 at K=4 -- 2-tier is within 80% of 4-tier on F-ratio; though silhouette improves monotonically up to K=4, the F-ratio DROPS when splitting into more classes because groups become unbalanced).

## Notes

- Smoke outputs already represent the FULL run for these pure-JSON re-analyses (no scale sweep needed)
- All self-tests passed (4/4 scripts)
- No suspicious result gates triggered (all results show meaningful variance)
- Local CPU queue verified post-ship: all 4 entries PRESENT
