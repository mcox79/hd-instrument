# Pre-registration: CSKG graph-structure diagnostic v1

**Date:** 2026-07-12
**Cell:** `experiments/exp_cskg_graph_structure_diagnostic_v1.py`
**Anchor:** `cskg_graph_structure_diagnostic_v1`
**Design source:** `notes/research_kg_degree_community_diagnostic_2026-07-12.md` (section C "Concrete
REMOTE-runnable diagnostic design" + the four falsifiable predictions). Bands lifted VERBATIM from the
note; NOT re-derived.
**Route:** `remote_cpu_queue` (CPU-only, numpy+stdlib, no torch, no GPU). Resumable/one-shot census.

## Question

Two-part, per the drill note:
- (A) How big is frequency's structural moat on the actual test graph, and does it grow with scale?
- (B) Does the CSKG cross-cutting 12-core structurally SUPPORT a factorized (reusable per-relation-operator)
  map-builder, or is it too hub-dominated / schema-blurred for one shared operator per relation to help?

Pure GRAPH computation. ZERO training, ZERO substrate vectors, ZERO GPU, ZERO new data acquisition (reuses
`data/grounding_testbed/cskg.tsv.gz`, already on disk, 112,312,195 bytes, Zenodo 4331372).

## Graphs (three, per note section C)

- `G_full`  = simple undirected graph over ALL 58 relations (~2.16M nodes / ~5.17M simple edges) -- context.
- `G_xcut`  = simple undirected over the CROSS-CUTTING commonsense spine (~501k / ~1.18M) -- context.
- `G_core`  = the k=12 core of `G_xcut` (~23-26k nodes) -- **LOAD-BEARING** (matches course_c `k_core=12`
  test graph: `data/exp_course_c_rotate_cskg_l2_seed_17_gpu1024_v1/metrics.json:config.k_core=12`).

## The eight measures (note section C, items 1-8)

1. Degree power-law fit (Clauset-Shalizi-Newman discrete MLE: alpha, x_min, KS-distance, vs exponential
   alternative). 2. Gini of degree. 3. Max/mean-degree ratio (WITHIN each induced subgraph). 4. Sampled
   average local clustering coefficient. 5. PER-RELATION cardinality profile (TransH tphr/hptr =>
   1-1/1-N/N-1/N-N; symmetry fraction) on the FULL 58-relation set (SYNONYM/IS_A live here; the spine strips
   them). 6. Community detection + modularity (pure-python Louvain local-moving, NO networkx dep) on `G_core`
   + schema cross-tab (community vs relation-class + source-provenance). 7. Core-periphery: k-core curve of
   `G_xcut`; ultra-dense k>=20 kernel; structural cross-ref vs the high-degree tertile. 8. Fair-stratum size
   vs degree-cutoff sweep on `G_core`.

## Pre-registered bands (VERBATIM from the note's four falsifiable predictions)

**P1 (12-core is moderately, not extremely, hub-dominated).** Computed on `G_core`.
- HARD-PASS: max/mean-degree ratio in **[10, 50]** AND Gini in **[0.35, 0.60]**.
- HARD-FAIL: max/mean ratio **> 100** OR Gini **> 0.70**.
- (note P_deflated = 0.40)

**P2 (per-relation cardinality reproduces the functional-form gap from pure structure).** Full 58-relation set.
- HARD-PASS: the `SYNONYM`-class (symmetric) and `IS_A`-class (1-to-N) relations rank in the WORST
  (bottom-tertile) of the composite single-operator-difficulty score.
- HARD-FAIL: `SYNONYM`/`IS_A` land in the BEST tertile (no structural signal; the gap is fit-specific).
- (note P_deflated = 0.45; the sharpest, most-triangulable prediction)
- Operationalization: difficulty = log1p(max(tphr,hptr)-1) + 1.5 * symmetry_fraction (higher = harder for
  a single global relation operator, per the TransH/RotatE cardinality-heterogeneity critique).

**P3 (map-builder prerequisite: community structure exists AND is schema-flavoured). HEADLINE.** `G_core`.
- HARD-PASS (supports factorized map-builder, partially): modularity **Q > 0.30** AND communities show
  non-uniform relation-class/source composition (schema_alignment **> 0.15** above the uniform-null max
  relation-class fraction).
- HARD-FAIL (too hub-dominated / schema-poor): **Q < 0.15** OR near-uniform relation-class mixing
  (schema_alignment **<= 0.05**).
- (note P_deflated = 0.30; deflated hard -- CSKG's own stated schema-blurring design principle is genuine
  evidence toward the HARD-FAIL side)

**P4 (frequency's win localizes to a small ultra-dense kernel -- STRUCTURAL precondition only).** `G_core`.
- STRUCTURAL-PASS: the k>=20 ultra-dense kernel is a small node set (kernel node fraction **< 0.20** of
  `G_core`) carrying a DISPROPORTIONATE degree-mass share (mass-share / node-share **> 2.0**).
- STRUCTURAL-FAIL: no sharp kernel (mass concentration **<= 1.3**; mass share ~ node share).
- (note P_deflated = 0.35) **PERFORMANCE-margin concentration** (POP-vs-ROTATE inside the kernel) is
  `HYPOTHESIZED@this_prereg` -- it needs the course_c model scores and is OUT OF SCOPE for a pure-graph cell.
  This cell answers the STRUCTURAL precondition ONLY.

**Headline** = the map-builder decision, driven by P3:
`SUPPORTS_FACTORIZED_MAP_BUILDER` (P3 HARD_PASS) / `TOO_HUB_DOMINATED_OR_SCHEMA_POOR` (P3 HARD_FAIL) /
`PARTIAL_MAP_BUILDER_SUPPORT` (P3 MIDDLE_BAND). P1/P2/P4 reported as sub-verdicts in gates + verdict_msg.

## Validity preflight (four checks; all fire in the deterministic self-test, PASS locally on .venv)

1. **Apparatus correctness:** planted 5-clique-plus-leaves has coreness {4,4,4,4,4,1,1} (Batagelj-Zaversnik);
   power-law MLE returns a sane alpha on a synthetic heavy tail; fair-stratum curve is monotone and
   mass-shrinking on a skewed sequence.
2. **Discriminator fires BOTH sides:** a uniform ring is low-skew (Gini<0.15, ratio<2); a hub star fires the
   P1 HARD-FAIL ratio branch (ratio 197>100); a constructed heavy tail fires the P1 HARD-FAIL Gini branch
   (Gini>0.70). Cardinality classifier correctly labels planted 1-1 / 1-N / N-1 / N-N and detects a planted
   symmetric relation (sym>0.9) while NOT flagging 1-1 (sym<0.1).
3. **POSITIVE control (a factorization-friendly graph PASSES):** a synthetic schema-CLEAN modular graph (6
   dense communities, each dominated by one relation-class) yields Louvain **Q=0.826, schema_alignment=0.667**
   -> P3 HARD_PASS -> headline `SUPPORTS_FACTORIZED_MAP_BUILDER`.
4. **NEGATIVE control (a hub-dominated schema-blurred graph FAILS):** a synthetic giant-hub star with
   uniformly-random relation-classes yields **Q=0.029** + extreme skew -> P3 HARD_FAIL AND P1 HARD_FAIL ->
   headline `TOO_HUB_DOMINATED_OR_SCHEMA_POOR`.

Plus a **full-assembly end-to-end** self-test (check 9): the streaming path (GraphBuild.add/finalize, edge-code
dedup, k-core extraction, core_edge_relclasses, Louvain, compute_verdict) runs on a synthetic injected triple
stream and produces a well-formed verdict (n_core=400) -- de-risks the CSKG streaming path that otherwise
first executes only on the remote runner (SCRIPT_PRECONDITION_VIOLATION guard).

## SCHEMA-VET fields

- `compute_architecture`: class (b) sequential-CPU with justification (pure combinatorial graph computation;
  no matmul/torch; GPU batching does not apply). Storage strategy: `no_storage / no_composition`.
- `cardinality_ok`: true. EXPECTED_N_UNITS = len(FAIR_PCTL_GRID) = 7 fair-stratum sweep points; short count
  -> `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H`. Per-relation profile reports `n_relations` measured.
- `arms_differ_verified`: true (>=3 distinct graph fingerprints: FULL / XCUT / CORE sha256 sigs;
  `HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF` if <3).
- `final_metrics_atomicity`: `tmp_replace` (write_metrics + crash-writer both tmp + os.replace).
- `crlb_n/a`: no quantitative estimator-noise floor -- this is a graph-structure census + partition audit,
  not an estimator. Discriminators are pre-registered threshold bands on measured graph statistics; the
  self-test proves each band FIRES by construction on planted positive/negative controls.
- `discriminator_survives_scale`: option B (analytical). All measures are graph-size-invariant ratios /
  partition-quality scores (Gini, max/mean, modularity Q, cardinality ratios), NOT accuracies that saturate
  with N. `G_core` IS the full-scale test graph, so there is no smaller-than-scale smoke gap.
- `baseline_in_band`: the null is the schema-BLURRED hub control (fails P1+P3 by construction); the
  schema-CLEAN control passes by construction; both proven in self-test. Real-graph outcome is an OPEN
  MEASUREMENT reported as the verdict.
- `calibration_check`: `default_ok_for_this_regime` -- CSN-MLE, Gini, Batagelj-Zaversnik, local-moving
  Louvain are parameter-free / literature-standard; the only free knobs are the pre-registered band cutoffs.
- `defensive_error_checking`: `passed_all_4_patterns` -- start_marker + crash_diagnostic (Exception ->
  CELL_CRASHED tmp+os.replace) + heartbeat (`_heartbeat.jsonl` per stage) + `except SystemExit: raise`
  BEFORE `except Exception` (no BaseException; grep gate CLEAN).
- `cell_chunked`: false (single graph census; no per-seed axis).
- `progress_logging`: `print_flush_true` (all logs flush=True via line_buffering; per-stage heartbeat during
  parse / graph builds / Louvain). timeout_s >= 1800 so this field is mandatory -- satisfied.
- `run_mode`: defaults to `full` (runner invokes with no argv). `--smoke` reduces CSKG_MAX_LINES to 300000;
  `--self-test` runs planted controls only and writes SELFTEST_PASS.

## Composition/sweep gates (SCHEMA-VET section 15)

- `sweep_alignment_verdict`: ALIGNED. The only sweep axis is the fair-stratum degree-percentile grid; each
  point measures the real `G_core` degree distribution directly (no effective-vs-nominal parameter drift).
- `discriminating_fraction`: n/a for a structural census (no accuracy sweep). The pre-registered bands are
  the discriminators; each is shown to fire on planted controls.
- `composition_edges`: none (no primitive->primitive composition; single graph census).
- `positive_control_arms`: the synthetic schema-CLEAN graph reproduces the "factorization SHOULD work"
  regime (Q>0.30, align>0.15) at self-test; the hub-blurred graph reproduces the fail regime.
- `functional_requirements`: (a) quantify degree skew of the actual test graph -> items 1-3;
  (b) quantify per-relation cardinality heterogeneity -> item 5; (c) detect + score community/schema
  structure -> item 6; (d) localize the hub kernel -> item 7; (e) measure the fair-zone mass share -> item 8.

## Timeout

`timeout_s = 5400` (90 min). Analytical estimate (no local FULL timing per the no-local-smokes lock):
stream ~6M rows (~1-3 min) + GraphBuild + dedup (~2-4 min) + k-core Batagelj-Zaversnik on the ~2.16M-node /
1.18M-edge xcut graph (pure-Python O(N+E) loop, ~2-4 min) + degree/power-law (~1 min) + Louvain on ~23k
nodes / ~500k edges (~1-2 min) + core_edge_relclasses (~1 min) => ~10-20 min expected. 5400s is a generous
cap so a slow pure-Python k-core pass cannot get killed on a one-shot cheap census.

## metrics.json required fields

`verdict` (headline), `verdict_msg`, `summary`, `elapsed_s`, `run_mode`, `anchor_name`, `ts_iso`,
`arms_differ_verified`, `graph_sigs`, `gates` (p1/p2/p3/p4 verdicts + all band values + measured values),
`diagnostic` (full/xcut/core degree reports, kcore_curve, per-relation `relations` list, `community`,
`p4_kernel`, `fair_stratum`, `graph_sigs`), `config`.

## Prior-work check

Substrate-KB concept-query ("knowledge graph degree distribution community modularity relation cardinality
factorized map builder"): NONE at cosine > 0.30 for this specific CSKG structural diagnostic. Top hit
(cosine 0.34) is entity-resolution/KG-construction methodology; next (0.33/0.31) is theoretical
spectral-community/GNN-ceiling network-science work -- a DIFFERENT question. This cell is genuinely novel: a
pre-registered pure-structural census of the actual CSKG 12-core test graph with the note's verbatim bands.
