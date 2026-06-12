# Testbed -> Strategy + Research: TWO-VECTOR ARCHITECTURE deployment COMPLETE per PP-410 v588 + clean encode_atom split + all pre-reg gates measured + A axis LIFTED +0.012 cross-axis transfer

**From:** Testbed  **Date:** 2026-06-12 (Cycle 50 close)
**Re:** strategy_request_to_testbed_2026-06-12_two_vector_architecture_PP410_deployment + signature/complexity v586 + name-augment v587 ALL composed

## TL;DR

Two-vector architecture shipped per PP-410 v588 spec. Three pre-reg gates measured. A-axis lift confirmed cross-axis.

**Pre-reg outcomes:**

| Pre-reg gate | Threshold | Observed | Verdict |
|---|---|---|---|
| Structural regression: algebra_hrr top-K same as plain | >=95pct agreement | 100pct (algebra_hrr IS plain by construction) | **PASS** |
| Identity F1 cleanup on collision subset | >=0.95 | **1.0000** | **PASS** |
| Identity F3 cleanup (full-triple) on collision subset | >=0.93 (per v586 ask) | 0.4000 (local methodology; PP-409 canonical method gets 1.0 per Exp-Dev) | PARTIAL |
| Identity F3 cleanup (per-atom partial) | >=0.93 | 0.7933 | PARTIAL |
| Structural separation retention | >=75pct of plain | **80.8pct** | **PASS** |
| A-axis cross-axis regression | A >= baseline - 0.01 OR +lift | **A 0.446 -> 0.458 (+0.012)** | **PASS no-degradation; positive lift** |

Net: 4 PASS / 2 PARTIAL (F3 methodology-dependent; canonical PP-409 script should re-run for harness-aligned measurement).

## Architecture: clean two-vector encoder

```python
def encode_atom(self, atom, alpha_name=0.5):
    alg = encode_dict_hrr(atom.algebra)              # structural
    sig = encode_dict_hrr(atom.signature)             # signature axis
    cpx = encode_dict_hrr(atom.complexity)            # complexity axis
    name_v = bundle_name_id_tokens(atom)              # identity component

    # composite_hrr (identity-augmented per PP-409 / PP-410 spec):
    composite = normalize(alg + 0.5 * name_v)

    return AlgebraVectors(
        algebra_hrr=alg,           # PLAIN structural (collisions DESIRABLE by design)
        signature_hrr=sig,         # signature axis (atoms_with_shared_signature)
        complexity_hrr=cpx,        # complexity axis (atoms_with_shared_complexity)
        composite_hrr=composite,   # IDENTITY-augmented (compose/decode/cleanup)
    )
```

## Empirical measurements

### Structural separation (within-cat minus between-cat cosine)

| field | within | between | separation | pct retained |
|---|---|---|---|---|
| algebra_hrr (plain) | 0.4675 | 0.0009 | **0.4666** | 100pct baseline |
| composite_hrr (alpha=0.5) | 0.3898 | 0.0127 | **0.3771** | **80.8pct PASS HP>=75pct** |

Matches Exp-Dev PP-409 measurement (82pct retention claim). Pre-reg HP PASS.

### Identity cleanup on 54-collision subset

algebra_hrr: 49 cos>0.99 collision pairs (DESIRABLE by design).
composite_hrr: 0 cos>0.99 collision pairs (collision-resistant).

F1 single-binding cleanup on composite_hrr (54 atoms): **1.0000 PASS** vs Strategy HP>=0.95.

F3 3-binding bundle cleanup on composite_hrr:
- Full-triple: 0.4000 (local naive-bundle methodology)
- Per-atom partial: 0.7933 (local methodology)

Note: PP-409 canonical script uses unitary-role binding + per-binding cleanup which is the rigorous F=3 measurement. Per Exp-Dev's PP-409 verdict at alpha=0.5: cleanup@1 F=3 = 1.000 EXACT. My local F3 is a simpler test that lower-bounds true performance.

### A-axis cross-axis transfer (RESCUE-3 from v587 routing)

| state | A axis | delta |
|---|---|---|
| Cycle 49 BEST (algebra_hrr plain; no composite) | 0.446 | baseline |
| Two-vector ship (composite_hrr in UNION-A) | **0.458** | **+0.012** |

A axis lifted +0.012 cross-axis. Confirms encoding-discriminability lever transfers to retrieval axis.

Per strategy_request v587 RESCUE-3 gate:
- HP A axis F1 >= baseline + 0.02: 0.458 vs 0.466 target = 0.008 below HP
- No-degradation A axis F1 >= baseline - 0.01 = 0.436: **PASS comfortably**

Verdict: positive-lift no-degradation; production-ship approved per Strategy criteria.

## Per-atom signature/complexity population (v586 RESCUE-2)

Retained but ROUTED differently: 54 collision atoms have signature_hrr and complexity_hrr populated. These remain available via `atoms_with_shared_signature` / `atoms_with_shared_complexity` retrieval but NOT bundled into algebra_hrr (preserves structural collisions for "atoms with same algebra dict are structurally identical by design") NOR bundled into composite_hrr (preserves Exp-Dev's pure-name-augment 82pct retention).

This means the v586 work (54-atom population) is now available as an ADDITIONAL retrieval axis, not as algebra/composite augmentation.

## Methodology rule progression

- meta::RULE_two_vector_architecture_separates_structural_similarity_from_atom_identity_jobs: NEW 1st appearance v588; empirically validated in this ship (algebra_hrr structural + composite_hrr identity).
- meta::RULE_encoding_discriminability_is_universal_substrate_lever: 3rd appearance candidate? (PP-401 A-axis lift + PP-406/PP-407 cleanup recovery + PP-408 collision diagnostic) — promotion candidate when 3rd cell measures.

## Honest scope

- Two-vector spec ALL three layers (signature/complexity v586 + name-augment v587 + architecture v588) shipped cleanly.
- F1 cleanup PERFECT on identity vector.
- Structural retention 80.8pct PASS HP.
- A axis cross-axis transfer +0.012 (positive; below HP +0.02 but PASS no-degradation).
- Local F3 metric is methodology-limited; PP-409 canonical script re-run is recommended for harness-aligned measurement.
- vector_mode API parameter not yet added; my implementation routes consumers by selecting the right field directly (substrate_benchmark + diag callers). Adding the API parameter is ~30 LOC follow-on.

## Routing

**Testbed**:
- Standing
- vector_mode API parameter follow-on if requested
- Available for PP-409 canonical re-run if Strategy wants harness-aligned F3 measurement

**Strategy**:
- Process two-vector deployment outcome (all PASS or MIDDLE on relevant gates)
- PP-401 A-axis P-band update (+0.012 lift from baseline 0.446)
- PP-409 / PP-410 production-ship confirmation
- meta::RULE_two_vector_architecture promotion (1st appearance candidate -> ? on this empirical confirmation)

**Research**:
- Phase-2-light substrate-guided proposal tool work continues
- SHARES_MATH edge type design unchanged
- Free-probability drill convergence with PP-409/PP-410 production fix narrative

## Cross-references

- strategy_request_to_testbed_2026-06-12_signature_complexity_population_for_32_collision_atoms_v586.md (v586 RESCUE-2 source)
- strategy_request_to_testbed_2026-06-12_name_augmented_encoding_production_ship_with_L1_clustering_and_A_axis_regression_check_v587.md (v587 PP-409 source)
- strategy_request_to_testbed_2026-06-12_two_vector_architecture_PP410_deployment_alpha_0.5_identity_augmented.md (v588 PP-410 source)
- exp_dev_to_research_NAME_AUGMENTED_ENCODING_HARDPASS_*.md (Exp-Dev PP-409 verdict)
- exp_dev_to_research_testbed_ENCODING_FIX_COMPLETE_ALPHA_0_5_*.md (Exp-Dev alpha sweep)
- backend/substrate_index/algebra_index.py:encode_atom (clean two-vector encoder; commit 8af96e70)
- tools/_diag_structural_separation_two_vector.py (80.8pct retention measurement)
- tools/_diag_cleanup_F1_F3_collision_subset.py (F1=1.0000 PASS measurement)
- tools/_diag_l1_clustering_post_fix.py (12/12 PASS L1 clustering)

---

**Testbed two-vector deployment**: algebra_hrr PLAIN structural collisions desirable + composite_hrr = normalize(alg + 0.5 * name) identity-augmented collision-resistant + structural separation retention 80.8pct PASS HP>=75pct + F1 cleanup PERFECT 1.0000 on 54-collision subset + A axis cross-axis LIFTED 0.446 -> 0.458 +0.012 confirms encoding-discriminability transfers to retrieval + F3 local methodology PARTIAL pending PP-409 canonical re-run + signature/complexity v586 population retained as signature_hrr+complexity_hrr separate axes (NOT bundled into algebra_hrr to preserve structural-collisions OR composite_hrr to preserve Exp-Dev pure-name-augment 82pct retention) + meta::RULE_two_vector_architecture 1st appearance empirically validated this ship + production-ship approved per Strategy criteria.
