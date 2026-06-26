# Pre-reg: gap1_partition_routing_cortex_R_schema_closed_form_v1_META_M7

**Authored:** 2026-06-26 (exp_dev under autonomous YOLO; Research Gap 1 cortex-as-router drill)
**Anchor:** `gap1_partition_routing_cortex_R_schema_closed_form_v1_META_M7`
**Cell:** `experiments/exp_gap1_partition_routing_cortex_R_schema_closed_form_v1_META_M7.py`
**Routing:** `remote_cpu_queue` (per USER directive 2026-06-26 -- USER traveling; all dispatches remote)
**Source:** `notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md` (Research; P_deflated=0.55)

---

## Rationale

Cell B v2 PART_ORACLE_5HOP=0.9550 cleared chain-grade but used `target_part = target_o // part_sz` (ORACLE -- carries BIAS-P scope flag). Parent cell `gap1_partition_routing_bidirectional_collide_and_fly_lsh_v1_META_M7` tested USER's steelman (bidirectional collide) + fly-LSH router + naive centroid; ALL three routers landed at the **0.66 ceiling** (BIDIR_COLLIDE=0.6583, FLY_LSH=0.6017, NAIVE_CENTROID=0.6617). Cell C v2 probe data confirmed `mean_midpoint_cosine=0.0000` on the forward state at hop 2 -- the state is noise-collapsed.

Research drilled the brain mechanism (mPFC schema-bias via theta-gamma phase coupling) and concluded the 0.66 ceiling is **NOT** a substrate-physics ceiling -- it is a **SINGLE-PATHWAY ceiling**. All current substrate routers read from the SAME noise-degraded signal (state_fwd or state_bwd from the unbind chain). The brain solves this by routing via a **SEPARATE PATHWAY** that bypasses the noise: mPFC reads the QUERY (clean input) and provides destination-bias via theta-gamma PAC.

The substrate analog: closed-form R_schema in R^{N_PARTS x N_DIM x N_HOPS}, fitted from QUERY embeddings (NOT noise-collapsed state_fwd) to one-hot target partition per hop. This sidesteps the 0.66 ceiling structurally because it reads a clean signal through a separate pathway.

Substrate-precedent: `kv_learned_projection` chain-grade 0.827 (2026-06-20) -- same capability class (closed-form learned projection).

## Cell design (6 arms; one closed-form fit; numpy-bound)

| Arm | Mechanism | Band |
|---|---|---|
| ARM_BASELINE_HRR_2HOP | beta-sweep beta_sweep_naive_hard | [0.62, 0.68] (sanity rail) |
| ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP | W_pointer_v2 (n=200, depth=10 -> 2000 bindings); verbatim chain naive | **[0.08, 0.25] (META_M7 rail; MANDATORY)** |
| ARM_SINGLE_TOP1_5HOP | W_v1_regime (n=200, depth=5 -> 1000 bindings); monolithic | informational rail (no band) |
| ARM_PART_ORACLE_5HOP | Cell B v2 oracle reproduce | **CROSS-CELL RAIL: [0.935, 0.975] (0.9550 +/- 0.02)** |
| ARM_PART_BIDIR_COLLIDE_5HOP | parent-cell bidir-collide reproduce | **CROSS-CELL RAIL: [0.628, 0.688] (0.6583 +/- 0.03)** |
| ARM_PART_R_SCHEMA_CLOSED_FORM_5HOP | closed-form ridge pseudoinverse query->partition; brain mPFC analog | **MAIN TEST; see prospective bands below** |

**Two-W discipline (parent cell):** `W_pointer_v2` for META_M7 (2000 bindings); `W_v1_regime` for ORACLE / BIDIR / R_SCHEMA (1000 bindings; matches Cell B v2). `disallow_s=set()` (no vocab-overlapping disallow per Cell X v2 fix).

**Train/test split for R_schema:** 80/20 deterministic per-seed split; train fit ridge-regularized least squares (`lambda=0.01 * trace(XtX)/N_DIM` for stability); test top1 is the verdict-relevant metric.

## PROSPECTIVE BANDS (LOCKED prospectively at module-init assert)

- **HARD_PASS_CHAIN_GRADE_BIDIR_ROUTER_REMOVED:**
  - R_SCHEMA test top1 >= 0.80
  - AND META_M7 PASS (REPRODUCE_PV2 in [0.08, 0.25])
  - AND R_schema cv <= 0.07
  - AND R_schema lift over BIDIR_COLLIDE >= 0.10
- **HARD_PASS_PARTIAL:** R_SCHEMA in [0.70, 0.80)
- **MIDDLE_BAND:** R_SCHEMA in [0.50, 0.70)
- **HARD_FAIL:** R_SCHEMA <= 0.50

## Cross-cell sanity rails

1. **META_M7 rail (MANDATORY):** REPRODUCE_POINTER_CHAIN_V2 in [0.08, 0.25].
2. **PART_ORACLE rail:** 0.9550 +/- 0.02 (reproduces Cell B v2).
3. **PART_BIDIR_COLLIDE rail:** 0.6583 +/- 0.03 (reproduces parent bidir-collide cell).
4. **Overfit flag:** train_top1 - test_top1 > 0.10 -> R_SCHEMA_OVERFIT in rails.
5. **Cone-preservation guard:** mean cosine of R_schema-projected query vs raw query >= 0.90; below -> CONE_ROTATION_RISK in rails.

## Disciplines

- ASCII only; substrate-only at inference; zero LLM forward calls; encoder_provenance = SUBSTRATE_NATIVE
- N=8192, V_C=200, V_P=10, K_set=20, n_chains=200, M_train per hop ~ 160, M_test per hop ~ 40
- Seeds = [11, 13, 19] (matches Research-routed Gap 1 follow-on series; differs from parent cell [7, 17, 23] to avoid same-seed-bias)
- Per-arm metrics returned (Fix #28; per-arm verdict-relevant metrics directly readable)
- META_M7 capacity-sensitive dims identical smoke/full (smoke keeps depth=10 to preserve crosstalk regime)
- Per-seed checkpoint (PROT-021; cell imports `_seed_checkpoint`)
- Pause flag re-check before queue dispatch
- BIAS-Q guard: 1.000 routing accuracy in PART_ORACLE arm by-construction (locked in code)
- Fix #26 predispatch_check.py run before dispatch
- Fix #17 strict runtime measurement (smoke wall-clock recorded; full timeout scaled from smoke)

## Verdict-msg requirements

- Explicitly state whether R_SCHEMA closed-form router REMOVES the BIAS-P scope flag from Gap 1
- Report R_schema lift over BIDIR_COLLIDE numerically (verdict-relevant)
- Report overfit_gap (train_top1 - test_top1) and cone_cos_mean
- Report cross-cell drift for both ORACLE and BIDIR rails (apples-to-apples verification)

## Compute budget

- Smoke (N=2048, 1 seed): expected ~30-60s wall (R_schema fit ~1-3s; arms scale with N)
- Full (N=8192, 3 seeds): expected ~4500-5500s wall (per Research budget). R_schema fit per hop on 160 training queries x 8192 dims = O(N^2) = 6.7e7 FLOPS x 5 hops = ~30s per seed; remainder dominated by W ingest, BIDIR_COLLIDE backward batched walks (the heaviest arm), and ORACLE cleanup
- **Per-formula self-test timeout:** smoke wall-clock measured under gate; full timeout = ceil(1.5 * smoke_wall * (8192/2048)^1.5 * (3/1)) ~ 1.5 * 60 * 8 * 3 ~ 2160s; scale to 7200s for safety margin given chain back-walk batched ops scale near N^2 for backward state computation

## Notes

- Research recommended P_deflated=0.55 (the cheapest decisive test of the brain-architecture insight). HF on this arm pivots to Cand 2 (Modern-Hopfield prototype router) or Cand 3 (CLS-replay R_schema).
- Composition with Cand 6 (two-stage R_schema + bidir-collide) gated on this cell's HP OR PARTIAL; that follow-on can be authored after this lands.
- This cell does NOT include ARM_PART_R_SCHEMA_TRAINED (gradient-trained upper bound; deferred to subsequent cell if HP unclear).
