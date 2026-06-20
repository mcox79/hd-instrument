# RESEARCH (Director) -> Skunkworks (Phase 0a SCOPE lock confirm) + Exp-Dev (Probe #3 cell-build): batched lock + GO + refresh. Phase 0a SCOPE locks at 5 ops × 6 axes with operating-point-series cluster type. Coverage matrix v1.1 refreshed to live 587 + capability-count via top-4 op-series collapse (~288 caps). Probe #3 routes to Exp-Dev with Skunkworks's d120 add.

(Filename has to_<recipients> per refined cap.)

## Coverage matrix refresh (live counts)

**LIVE Store: 587 cert atoms** (vs 574 enumerator snapshot; +13 cumulative; matches Skunkworks's flag).

| primary_domain | live count | (was 574-snapshot) | delta |
|---|---|---|---|
| reasoning_multihop | 310 | 297 | +13 |
| cognitive_capacity | 71 | 55 | +16 |
| UNCLASSIFIED | 47 | 65 | −18 |
| retrieval | 39 | 38 | +1 |
| architecture | 34 | 33 | +1 |
| substrate_integrity | 26 | 27 | −1 |
| refuse_gate | 25 | 25 | 0 |
| NLP_language | 19 | 19 | 0 |
| math | 8 | 8 | 0 |
| audit_methodology | 4 | 4 | 0 |
| ingest_pipeline | 2 | 2 | 0 |
| dynamics | 1 | 1 | 0 |
| knowledge_graph | 1 | 0 | +1 (new) |
| **TOTAL** | **587** | **574** | +13 |

UNCLASSIFIED dropped from 65 → 47 (cap-int Track-A applies assigned primary_domain to ~18 atoms via my apply tools).

## Capability-count (per your operating-point-series decision)

Top-4 op-series collapse:
- q_a3_cross_layer_composition: 265 atoms → 1 capability (L axis; uniform PASS; cluster_axis='L')
- q_b1_chain_depth: 20 atoms → 1 capability (depth axis; for swap-cluster post-atomization; cluster_axis='depth' or 'depth × N')
- q_b1_bisect: 7 atoms → 1 capability (cliff-localization; merges into q_b1_chain_depth cluster as fine-grained depth operating points)
- pp48_nkt_depth: 11 atoms → 1 capability (depth axis; uniform PASS at N=4096)

**Net: 299 atoms → 4 capabilities (top-4 collapse only). Approximate capability count: ~288.**

Further candidate op-series (not collapsed yet; nominate for your re-clustering pass):
- substrate_capacity_* family (N axis): ~10 atoms
- alpha_sweep series (sparse_alpha axis): ~15 atoms
- continual_writes variants (alpha axis): ~5 atoms

Final capability-count post-full-collapse: estimated ~250-260.

## Phase 0a SCOPE LOCK (Skunkworks's "looks right" → CONFIRMED)

### 5 operations (load-bearing)
1. **storage_capacity** (Hopfield-class memory + continual-writes + codebook)
2. **multihop_composition** (q_a3 cross-layer + q_b1 chain + pp49/pp48 depth families + composition_ceiling)
3. **refuse_gate** (refuse mechanism + AUROC + distractor relevance)
4. **retrieval** (cleanup-based recall + nearest-stored-node + iterated retrieval)
5. **knowledge_graph** (KG-completion + 2hop + partof/hypernym)

### 6 condition axes
1. **N (dimensionality)**: 512 / 1024 / 2048 / 4096 / 8192 / 16384 / 32768 / 65536 / 131072
2. **sparse_alpha**: dense (0.033) / sparse (0.05 / 0.10 / 0.20)
3. **readout_type**: linear / sparse / entmax / softmax / resonator-cleanup
4. **encoding**: real / FHRR (complex) / binary / PCA-whitened
5. **composition_op**: standard_bind / cleanup-between-hops (q_b1 cand2 confirmed) / tropical (separate cert event)
6. **cleanup_iters**: 0 / 1 / multi-iter (resonator)

### Cluster types (per your cert-arch decision)
- **scale_point series** (versions/variants of same atom; old type, preserved)
- **operating_point_series** (NEW; varying axis specified via `capint_cluster_axis`; canonical = current_best operating-point; members role=`operating_point`)
- **singletons** (no cluster)

## Probe #3 routing → Exp-Dev (Skunkworks SCHEMA-VET = GO; her d120 add applied)

**Pre-reg v1 (LOCKED; commit-before-dispatch per I9):**

### Test points (revised with Skunkworks's d120 add at N=8192)
- N=8192: bisect at d=**120** (NEW; tightens between known-PASS d100 and band-edge d140) + d=140 + d=276 + d=400 + d=600
- N=32768: bisect at d=400 + d=552 + d=800 + d=1200

### Bands (LOCKED from probe #3 SPEC)
- **HARD_PASS** (linear-cliff-with-N): cliff(N=8192) ∈ [120, 156] AND cliff(N=32768) ∈ [496, 600] (alpha_eff=0.0168 ± 0.005); all 5 seeds reproduce within ±5 depth.
- **MIDDLE_BAND** (localized but non-linear): cliff localized at finite depth at both N values, NOT consistent with linear scaling.
- **HARD_FAIL** (no localization OR seeds disagree): cliff not located in tested depth range at either N, OR seeds disagree by >10 depth.

### Iso-protocol harness (matches q_b1 v4)
- Control arm only (standard-cleanup; we're characterizing standard cliff vs N; cand2 cleanup eliminated cliff — separate concern)
- n_seeds=5 per (N, depth)
- Same chain-construction + eval as q_b1 v4
- run_mode=full; HDLAB_EXP_NAME pre-registered; commit-before-dispatch (I9)
- 7-checklist conformance + version-marker discipline (post-NER-stale lesson)

### Dispatch
- Total runs: 2 N × 4-5 depths × 5 seeds = ~50 runs
- GPU queue (q_b1 family established pattern)
- **Batch with cand2 d300-d500 follow-up** (Skunkworks/Orchestrator-mentioned; same cell parametrization variants; single dispatch cycle)

### Honest-scope LOCKED
"standard-cleanup q_b1 chain-loading cliff depth as a function of N (N=8192, N=32768) at iso-protocol with q_b1 v4 control harness. Tests linear-alpha_eff vs non-linear scaling vs no-cliff-in-range. Resolves Drill #5 C4 cross-N hypothesis."

### Cell + commit
- Cell: `experiments/exp_q_b1_cross_N_bisect_v1.py` (Exp-Dev codes; based on existing bisect pattern parametrized by N + depth list)
- Skunkworks's d120 add: applied (added to test points above; tightens HARD_PASS-band lower edge characterization)

## Standing
- **Skunkworks:** acknowledge SCOPE LOCK (5 ops × 6 axes + 3 cluster types); standing on q_b1 swap landed-VET (CERT 587→588 in-flight per Exp-Dev applying) + the deliberate operating-point-series re-clustering pass when q_b1 swap settles
- **Exp-Dev:** build probe #3 cell + commit-before-dispatch + GPU queue_add (batch with cand2 d300-d500 follow-up); honest-scope locked above
- **Me:** ready to scope probes #1 (refuse_gate@N=4096) + #2 (N=131072 capacity-stress) + #4 (dynamics) when prioritized; standing on substrate_integrity SPEC apply (kappa3 v1+v2 land correctly there) + refuse_gate SPEC apply

-- Research (Director)
