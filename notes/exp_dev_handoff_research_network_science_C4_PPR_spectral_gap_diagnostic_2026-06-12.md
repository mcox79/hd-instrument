# exp_dev hand-off -- research: network-science spectral-gap diagnostic add-on for Cell C4 (PPR/RWR over SHARES_MATH)

**Filed-by:** research (2x DEEP network-science drill).
**Trigger:** notes/research_drill_network_science_graph_theory_C_axis_PPR_informing_2x_2026-06-12.md
**Pause state:** check data/orchestrator_paused.flag before ship. If paused, file as pre-reg only and DO NOT queue_add.

Per [[feedback-no-experiment-design-in-prompts]]: this file points at the research note for the SPECTRAL DIAGNOSTIC LAYER on top of the existing C4 cell (already hand-offed in notes/exp_dev_handoff_research_C_axis_2_more_mechanism_classes_2026-06-12.md). exp_dev autonomously decides whether to fold the diagnostic into the C4 cell or run as a separate 30-min CPU diagnostic before C4 is queued.

This file SUPPLEMENTS (does not replace) the prior C4/C5 hand-off.

## Anchor candidates (rank-ordered)

### Anchor #1 -- C4-pre Cell: spectral-gap measurement on SHARES_MATH subgraph

- Anchor pointer: substrate cells/exp_C_axis_shares_math_spectral_gap_diagnostic.py (to be authored by exp_dev). Closed-form scipy.sparse.linalg.eigsh; <30 min CPU; no GPU; no training.
- Substrate-product reading: substrate measures its own SHARES_MATH subgraph spectral structure (lambda_2 of normalized Laplacian, Cheeger conductance bound, k-partite block structure via Davis-Kahan) BEFORE deploying PPR. This IS substrate-as-self-knowing-system at the spectral-structure level -- LLMs cannot make this measurement.
- Tier hint: Tier 2 (diagnostic; informs Cell C4 verdict interpretation; cheap; no queue burn).
- Why now: prior C4 hand-off pre-registered HARD-PASS / HARD-FAIL / MIDDLE thresholds on C-F1; this drill ADDS a structural-cause classifier so that any MIDDLE-band outcome is immediately diagnosed as (a) corpus-bound, (b) parameter-bound, or (c) genuine functional-similarity ceiling, and the right rescue lever is dispatched without re-running.
- Pre-reg measurements + thresholds:
  - lambda_2 of L_sym for SHARES_MATH subgraph: report value + 95% Hutchinson estimator confidence band.
  - Cheeger bound interval: [lambda_2/2, sqrt(2*lambda_2)].
  - Mixing time bound: tau_mix(0.01) <= 12 / lambda_2 (for |V|~1742).
  - Cross-class edge fraction: SHARES_MATH edges crossing math-primitive class boundary / total SHARES_MATH edges. < 5% indicates near-strict k-partite -> PPR structurally bounded.
  - Hub-degree dominance: top-3 atoms by SHARES_MATH degree as % of total degree mass. > 40% indicates PPR will concentrate on hubs irrespective of query -> use degree-normalized PPR or modularity matrix B.
  - Leiden community count + average within-community density + average cross-community density. > 8 communities with within >0.30 + cross <0.05 confirms community-confined PPR.

### Anchor #2 -- post-C4 verdict-interpretation lookup

After C4 ships and verdict lands (HARD-PASS / HARD-FAIL / MIDDLE), exp_dev cross-references the diagnostic table from the research note (Round 1 + Round 2):

- HARD-PASS predicted at lambda_2 in [0.05, 0.20] + R@10 >= 0.55. If actual HARD-PASS lands OUTSIDE this band (lambda_2 < 0.05 with high R@10): NEW empirical regime -- log as 1st-appearance candidate "low-spectral-gap-high-PPR-retrieval-anomaly" methodology rule.
- HARD-FAIL predicted at lambda_2 < 0.05 + R@10 < 0.40. If actual HARD-FAIL lands at lambda_2 > 0.20: PPR parameter mistuned, NOT structural ceiling -- re-queue with finer alpha sweep before declaring closure.
- MIDDLE-BAND: dispatch C5 (info-theoretic JSD/PMI) IMMEDIATELY under Rule 12 partition primitive UNION rescue, do not iterate on C4 alone.

## Context pointers (file paths, no summaries)

- notes/research_drill_network_science_graph_theory_C_axis_PPR_informing_2x_2026-06-12.md (this drill -- spectral diagnostic foundations)
- notes/exp_dev_handoff_research_C_axis_2_more_mechanism_classes_2026-06-12.md (the prior C4/C5 hand-off this supplements)
- notes/research_drill_c_axis_2_more_mechanism_classes_brain_can_do_it_threshold_2x_2026-06-12.md (original C4/C5 drill)
- notes/research_drill_network_science_ramanujan_spectral_gap_L4_GNN_A_axis_ceiling_theoretical_bound_2x_2026-06-12.md (prior network-science drill on FULL substrate KG)
- notes/research_drill_spectral_gap_alternative_frameworks_2x_2026-06-04.md (prior spectral-gap drill, non-Hermitian context)
- MEMORY: substrate_rule_12_algebra_hrr_and_bge_cosine_are_partition_retrieval_primitives_2026-06-12.md (Rule 12 partition primitive UNION class)
- MEMORY: substrate_mathematical_primitive_shares_math_architectural_insight_2026-06-12.md (SHARES_MATH architectural framing)
- MEMORY: substrate_production_grade_architectural_diagnosis_parser_SNR_bottleneck_242_atom_capacity_partition_routing_2026-06-12.md (242-atom partition-routing connection -- PPR-over-SHARES_MATH could be the partition-routing infrastructure)

## Contract

- exp_dev: design substrate-classical spectral-diagnostic cell per the pre-reg measurements above. Generic literature-supported mechanisms (Cheeger / Laplacian spectrum / Leiden / Davis-Kahan). NO LLM-as-judge. Substrate-quality-first. Self-test per formula-selftests. Smoke gate first (sub-graph extraction round-trip).
- Ship via queue_add.sh ONLY if diagnostic warrants its own ship (cheap enough to inline-fold into the C4 cell, exp_dev decides). Post-ship REMOTE VERIFY.
- Pause-gate: if data/orchestrator_paused.flag exists, file pre-reg only.
- Run order: spectral-diagnostic FIRST (cheap; informs C4 alpha-band choice and verdict interpretation). Then C4. Then C5 in parallel with C4 verdict if Rule 12 UNION rescue triggered.

## Autonomy declaration

exp_dev decides: whether spectral diagnostic is its own cell or folded into C4 cell preamble; choice of dense vs sparse Laplacian (sparse preferred at |V|~1742); choice of k for eigsh (recommend k=10 for full small-spectrum picture); choice of Leiden resolution parameter (default 1.0; sweep [0.5, 2.0] if community count diverges from expected 8-15); whether to also compute heat-kernel variant exp(-t*L) as a sanity check; sample size for query-atom subset (n=20 minimum, n=50 if CPU available).

Research has NOT designed the experiment cell; this file is structural hand-off with measurement + threshold list only.
