# Pre-reg: exp_analogy_candidate_inference_heldout_edge_v2

**Design-of-record:** notes/research_learned_inference_generalization_analogy_metalearning_2026-07-26.md
(Step 1a + HARD-FAIL forks b/c). **Author:** hdi_exp_dev. **Date:** 2026-07-26. **Stage:** 3.
**Anchor:** exp_analogy_candidate_inference_heldout_edge_v2
**Forks:** exp_analogy_candidate_inference_heldout_edge_v1 (commit 70a2ea10e, clean HARD_FAIL).

## Question (brain-vs-us delta iteration)
v1 ran structure-mapping analogy the NON-brain way (flat cosine over an edge-bag of ALL bundled
relations) and lost to a FREQUENCY_PRIOR
(MEASURED@data/exp_analogy_candidate_inference_heldout_edge_v1/metrics.json: analogy_top1=0.02590 <
frequency_prior_top1=0.07238). The brain-fidelity audit named two divergences; v2 closes BOTH and
keeps every v1 guardrail:
  (1) CAPACITY (Halford ~4 vars; LISA ~2-3 propositions): align on only the ~2-4 most informative
      relations of the query concept, not the full bundle.
  (2) STRUCTURED ALIGNMENT (Gentner/SME): score a base by one-to-one structural CORRESPONDENCE +
      systematicity, not flat bag-cosine.
THE ONE CHANGE is the analogy mechanism. Everything else reused verbatim from v1.

## Compute architecture
- Class: (b) sequential-CPU with justification. Sparse relational-profile alignment via inverted-index
  accumulation over base_pool candidates + small FLAT MLP + one bundled HRR memory build (floor arm).
  No GPU-batchable per-phase loop dominates; measured full wall = 112.5s (3 seeds).
  Storage: **no_composition** for all analogy arms (similarity+projection over profiles, no bind/unbind);
  **bundled** for STORE_RECALL_FLOOR ONLY (exemption (b): intentionally reproduces the bundled-memory
  pipeline on the exclusion-enforced split to show it collapses).
- Execution: LOCAL foreground-to-completion (remote/push NOT authorized by caller). smoke -> full.
- progress_logging: line_buffered_stdout (sys.stdout.reconfigure). timeout_s < 1800 (full ~112s).

## The mechanism (v2, brain-faithful; content-agnostic random-ID; leak-proof)
- CAPACITY: rank the query concept's (relation,slot) roles by summed-IDF; keep top `cap_rels` (=4,
  Halford). Roles exclude the predicted relation R (leak-proof).
- STRUCTURED: for each base E, SME structural correspondence over the capacity-limited role set =
  IDF-weighted count of EXACT shared partners per shared role (set intersection = one-to-one at partner
  level), + weak role-signature match, times systematicity multiplier n_matched_roles**gamma (gamma=1).
- Candidate inference: top-K aligned bases with a stored R-edge project their R-tail; rank by score.
- E's R-edge is used ONLY for projection, never for scoring. No borrowed embedding.

## Arms (2x2 ablation is the attribution engine)
- STORE_RECALL_FLOOR (reuse v1) -- MUST collapse to base-rate (leak detector; the load-bearing gate).
- FLAT-MLP (reuse v1) -- ho_lift ~ 0 baseline.
- ABLATE_NEITHER_V1  = flat cosine, all relations  (reproduces v1 ANALOGY; positive-control-at-regime).
- ABLATE_CAPACITY_ONLY  = flat cosine, top-m relations (isolates capacity divergence).
- ABLATE_STRUCTURE_ONLY = structured, all relations (isolates structured-alignment divergence).
- ANALOGY_v2 (BOTH)  = structured + top-m relations (PRIMARY). HP_SCOPE: {ANALOGY_v2: [all HP gates]}.
- FREQUENCY_PRIOR (reuse v1) -- THE bar to beat (v1 lost to it).
- Must-fail controls (reuse v1): SCRAMBLED_ANALOGY_SOURCE, SHUFFLED_PROFILE, RANDOM_ALIGNMENT.
- capacity_effect / structure_effect = 2x2 main effects -> report which divergence drove any gain.

## Metric
Per-relation AND pooled top-1/top-10 for all arms. Base-rate floor = 1/n_dict (~0.00029).
Secondary diagnostics: out-degree-vs-accuracy correlation (Gentner boundary; should be POSITIVE if the
mechanism is real), cap_bound_frac (how often the cap actually pruned), zero_role_frac (queries with no
non-R structure to align on).

## Pre-registered bands (envelope-fail-bands)
- **HARD_PASS:** ANALOGY_v2 beats FREQUENCY_PRIOR by >=0.05 AND beats FLAT by >=0.05 AND clears floor
  decisively (>=10x base-rate or +0.15) AND STORE_RECALL_FLOOR + all 3 must-fail controls collapse AND
  positive out-degree correlation.
- **HARD_FAIL:** ANALOGY_v2 still ties/loses FREQUENCY_PRIOR (d<0.05) OR ties floor+flat; OR any control
  fails to collapse; OR STORE_RECALL_FLOOR elevated (exclusion leaked -> respec). On HARD_FAIL report
  which of capacity vs structured-alignment moved the needle (2x2), so the next iteration targets the
  real divergence.
- **MIDDLE_BAND:** beats floor+flat by 5-15pp with controls holding, or beats freq but out-degree flat.

## Guardrails / schema-vet
- Leak-proof exclusion from ALL storage (build_analogy_split reused verbatim from v1).
- deterministic_seeding: true (fixed ints + np.random.RandomState(seed+offset) + sorted(set()); no hash()).
- final_metrics_atomicity: tmp_replace. except SystemExit: raise before except Exception (no BaseException).
- ARMS-MUST-DIFFER (META_RULE_AF): hard-gate ONLY when ANALOGY_v2 is bit-identical to a NON-ablation
  arm (control/baseline = real mechanism bug). Ablation-sibling coincidence (e.g. ANALOGY_v2 ==
  STRUCTURE_ONLY when the cap is a no-op on a relation-sparse corpus slice) is EXPECTED data, logged +
  surfaced via cap_bound_frac, NOT gated.
- crlb_n/a: prediction-accuracy discriminator; base_rate + FREQUENCY_PRIOR reported as floors.
- baseline_in_band: EXEMPT (FLOOR/FLAT/FREQ_PRIOR are intended-floor baselines).

## Smoke plan
KINDOF held-out at full-N (N=1024) so the discriminator survives scale. Confirm STORE_RECALL_FLOOR
collapses before any full investment (the single highest-value check; the thing v1 got right and this
design must keep right).

## RESULT (MEASURED@data/exp_analogy_candidate_inference_heldout_edge_v2/metrics.json)
**VERDICT = HARD_FAIL_ANALOGY_TIES_FLOOR_AND_FLAT** (full, 3 seeds, elapsed 112.5s).
- ANALOGY_v2 top1=0.01527 top10=0.08035; FREQUENCY_PRIOR=0.07238 (analogy LOSES, d=-0.0571);
  FLAT=0.03586; STORE_RECALL_FLOOR=0.01328 (collapsed=True, gate holds); controls collapsed
  (SCRAM=0.00465 SHUF=0.00996 RAND=0.00797).
- Ablation: NEITHER_V1=0.02324, CAPACITY_ONLY=0.02191, STRUCTURE_ONLY=0.01527, BOTH=0.01527.
  capacity_effect=-0.0007 (~0), structure_effect=-0.0073 (structure slightly HURT), driver=NEITHER_MOVED.
- Sparsity: cap_bound_frac=0.100 (cap=4 pruned only 10% of queries), zero_role_frac=0.172 (17% of
  queries have NO non-R structure to align on). outdeg_corr=-0.001 (Gentner boundary condition ABSENT).
- Per-relation: FREQUENCY_PRIOR beats ANALOGY_v2 on EVERY relation; ANALOGY_v2=0.0000 on CAUSE/MADEOF/
  PARTOF (diffuse tails -> a correct structural match still projects the wrong specific tail); KINDOF
  is the only relation where analogy scores >0 (0.061 vs FREQ 0.125).
- **Conclusion:** neither brain divergence moved the needle; structure slightly hurt. The real wall is
  UPSTREAM of the reasoner -- WorldTree concepts are relation-IMPOVERISHED per concept (median 1-2
  non-target relations), which structurally STARVES both divergences (capacity-integration AND
  systematicity both presuppose concepts embedded in rich multi-relation systems). This isolates the
  design-note's HARD-FAIL bottleneck (a) [corpus relation-sparsity], ruling out (b) alignment-metric
  and (c) capacity-mismatch via the 2x2 ablation. NOT banked (skunkworks VETs).
