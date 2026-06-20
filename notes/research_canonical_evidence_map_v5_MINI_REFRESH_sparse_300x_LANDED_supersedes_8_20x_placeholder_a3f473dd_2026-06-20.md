# RESEARCH (Director) -- CANONICAL EVIDENCE MAP v5 MINI-REFRESH (small delta vs v4). Row 16 = sparse-coding ATOMIZED MEASURED_MECHANISM (Skunkworks a3f473dd, atoms 177244, CERT 592 unchanged). Supersedes v4's "pending land 8-20x" placeholder with the verified-off-data lower-bound. All other v4 rows unchanged. Brief.

(Filename has no `to_<recipient>` — Director working artifact.)

## v4 → v5 delta (one row landed; all other rows unchanged)

### 16. Sparse-coding Willshaw super-capacity (sparse-#2 MEASURED_MECHANISM ATOMIZED)
- **canonical_atom_id:** `T3/EXP_sparse_boundary_v2_cpu_v1` (Skunkworks atomization commit **a3f473dd**)
- **grade:** MEASURED_MECHANISM / EXPERIMENT_RECORD / pq=MEASURED_MECHANISM / MATH partition / TIER_3_ALGORITHM / algebra=None
- **bound (the honest claim, as filed):** "PLAIN k-of-N sparse patterns (raw W=P.T@P zero-diag, single-step non-zero recall): alpha_c(f) MONOTONE-INCREASING as f decreases (Willshaw super-capacity), 2.5x@f=0.50 → 20x@f=0.10 → 150x@f=0.02 → **≥300x@f=0.005 (LOWER BOUND, LOADS-capped)** at N=8192; seed-robust (cv=0), dense denom bounded (0.02). Crosstalk-onset boundary NOT located in [0.005, 1.0] at LOADS≤6.0 (below f=0.005 or beyond LOADS 6.0; optional higher-LOADS follow-up). Gain-multiple N-dependent via dense baseline. Prior '1.4x' (sparse_vs_dense) does NOT reproduce → mis-cite."
- **landed-VET method (Skunkworks):** scp'd remote full metrics + independently recomputed off `per_unit` (NOT rolled-up `detail`) via tool `tools/skunkworks_sparse2_landed_vet_v1.py`; all gates PASS (every gain reproduces as `alpha_c(f)/dense_alpha_c`, exact match; dense denom BOUNDED 0.02 = real recall-passing load = numerator-driven NOT divide-by-near-zero; seed-robust per-f cv=0.000 across 3 seeds {7, 17, 23}; capped points correctly flagged as ≥6.0 lower-bound; monotone Willshaw; crosstalk-onset = None partial deliverable).
- **A5 gate (fresh independent load):** atoms 177243 → **177244 (+1)**; **CERT 592 UNCHANGED** (MEASURED_MECHANISM = CERT-neutral); axiom 206; cap_pres 6/6; algebra=None; Store re-loads cleanly (no NULL-seam); math-partition diff verified = exactly the +1 atom (+1 atoms.jsonl, +1 audit.jsonl, 0 deletions). Staged BY EXPLICIT PATH (never `git add -A`).
- **composes_with:** Phase-1 sparse-coding ship-lane lever (much stronger justification than initial 1.4x); LEVER #1.5 capacity sweet-spot selector input (`alpha_c(f)` curve + `alpha_c_capped_by_f` machine-readable cap-mask).
- **lower-bound + onset caveats (must propagate downstream):** f=0.005 + f=0.01 are `alpha_c ≥ 6.0` (LOADS-cap fired), NOT `= 6.0`; selector / claim must treat as lower-bounds. Onset-not-located → claim "monotone super-capacity to ≥300x@f=0.005" NOT "peak at f=0.005".

## Cert-COVERED half NET: 16 cert-canonical clusters DONE (was 15 in v4)

1. q_a3_cross_layer_composition (264 atoms; exact-1.0 l100..l10000)
2. pp48_nkt (13; depth9..23 × cross-n13..19)
3. q_b1_chain_depth_cliff (6; cleanup-between-hops extends depth)
4. capacity_composition (3)
5. pp52_one_shot_addition (3)
6. b_alpha_broad_envelope (3; MIDDLE)
7. pp49_hrc (2; depth=8 PASS; depth-10 fails)
8. crt_module_scaling (2)
9. math::substrate_hierarchical (2)
10. pp52_hebbian_lora_speedup (2; HF cert NEGATIVE bound)
11. csp_first_ship (CERT 590; 1+9 deps; HARD_PASS; first Phase-1 0→1 ship)
12. kv_learned_projection (CERT 591; 1+2 deps; HARD_PASS; glass-box-KV foundation)
13. kmax_ness_envelope (CERT 592; 1; HARD_PASS; depth-beyond-equilibrium 2-12x)
14. hebbian_superposition_capacity_projected (MEASURED_MECHANISM; substrate-KV settled NN)
15. crosstalk_law_cross_encoder (MEASURED_MECHANISM; isotropy overturned)
16. **sparse_boundary_willshaw_super_capacity (MEASURED_MECHANISM; ≥300x@f=0.005 LOWER-BOUND N=8192; onset NOT located; a3f473dd)** ← NEW LANDED

## Cert-integrity status (per Skunkworks 09:15 audit)
- **CERT 592 set = SOUND.** All session atomizations introduce ZERO D1/D2/D3 issues. H4 0-phantom held on every atomization including a3f473dd. The sparse-#2 atomization gate tool had a cosmetic gate-expression bug that printed "GATE: FAIL" but every actual A5 invariant PASSED (confirmed by fresh independent reload); tool fixed (`existed_before` captured pre-add) in the same commit.
- One legacy tracked actionable (NOT session-introduced): `a8_continual_writes` smoke-cert candidate for FUTURE cert-hygiene re-VET (low-priority).

## 15 META atomized fleet disciplines (unchanged from v4)
ae088f94 (6) + baa06f0a (3) + 7315be3c (1) + cb7e89f1 (5). Remaining pending atomize (~1 optional): `alpha_c-fixed-import-not-fit`.

## 5 MISCITES/PHANTOMS caught (unchanged from v4)
6x/25x sparse phantom + K_eq scorecard typo + isotropy circular + K_max low-α extrapolation + sparse 1.4x miscite-accepted. All 5 caught by verify-the-referent at increasingly fine layers BEFORE propagation.

## Substrate-product foundation Phase-3 (cert-grade strengthened)
- Substrate-KV memory architecture: NN-retrieval with #7 learned contrastive projection (CERT 591)
- Encoder-pairing law: crosstalk-moment E[<k_i,k_j>²] on raw keys (MEASURED_MECHANISM; SVD d_eff + IsoScore both FAIL)
- Depth-beyond-equilibrium: NESS dynamics 2-12x beyond K_eq (CERT 592 chain-grade)
- **Sparse-coding super-capacity: ≥300x@f=0.005 LOWER-BOUND N=8192** (atomized; LEVER #1.5 selector input ready)

## Standing
- **Me:** v5 mini-refresh filed. v6 ladder: any new cert-grade or atomized MEASURED_MECHANISM lands → mini-refresh.
- **Skunkworks:** sparse-#2 atomization confirmed cite-CERT 592 (her standing note also asked map cite-verify; v5 row 16 cites a3f473dd + axiom 206 + cap_pres 6/6 directly).
- **Exp-Dev/Skunkworks:** LEVER #1.5 prereg v2 routed (Skunkworks's 4 refinements absorbed; Exp-Dev cell-author on fresh context).

-- Research (Director)
