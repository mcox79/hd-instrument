# Strategy Decisions 2026-06-05
## CYCLE 78 BATCH -- v407 -> v408 (2026-06-05)

### Step 0 Honest Re-Read
7 verdicts. All source=remote (bridge stale; SSH fallback authoritative). HONEST 883 -> 890 (+7). LVH check on each:

| # | Anchor | Verdict | Honest Check |
|---|--------|---------|-------------|
| 1 | substrate_audit_core_C2_C3_whitened_pythia160m_v2_n4096 | HARD_PASS | C2_cert={0.984,0.980,0.990} all >>0.95 HP; C3_sep={11.1,10.8,11.1}x all >>10x HP; label honest |
| 2 | substrate_audit_core_C2_C3_pythia160m_residuals_v1_n4096 | MIDDLE_BAND | C2={0.500,0.500,0.500} random-level; C3={84.2,84.8,83.4}x strong; label 'one primitive operational' honest |
| 3 | substrate_kmax_depth_scaling_formula_validation_v1_n4096_alpha_sweep | HARD_FAIL | predicted K>>50 vs empirical=50 grid-ceiling all lf levels all seeds; median_rel_err=15.26 (1526%); label conservative ('off >50%') not over-claim |
| 4 | substrate_stdp_x_b2_sparse_sequence_storage_v1_n8192 | HARD_FAIL | ratios={0.5,1.0,1.0} mean=0.83x; label 'mean ratio=0.8x' honest |
| 5 | substrate_compositional_generalization_K10_to_K20_v1_n4096 | HARD_PASS | K10=K15=K20=1.000 unanimous 3/3 seeds; label honest |
| 6 | substrate_cognitive_core_smoke_pythia70m_AGGRESSIVE_v1 | HARD_PASS | recall=1.0 analogical=1.0 counterfactual={0.938,0.969,1.0} cross_domain=1.0; all >= HP bands; label honest FOR SCOPE TESTED; SCOPE NOTE: experiment is pure-VSA synthetic (no actual Pythia-70m LLM call despite anchor name; 0.6s wall confirms no model load); 'pythia70m' in name misleading -- this is VSA-algebra sanity not LLM-integrated cognitive core |
| 7 | substrate_posbind_x_b2_sparse_sequence_capacity_v1_n8192 | HARD_FAIL | dense_S_crit=sparse_S_crit=256 ratio=1.0x ALL 3 seeds; both hit grid ceiling; label 'ratio=1.0x (sparse hit grid ceiling; LOWER BOUND)' honest |

LVH assessment: 0 full LVH catches. Anchor 6 SCOPE CAVEAT (name implies LLM integration; experiment is pure-VSA synthetic) -- not an over-claim catch (numbers support label for tested scope) but scope annotation required. HONEST 883 -> 890 (+7). LVH 219 UNCHANGED.

### Cap_map Decisions

**(A) substrate_audit_core_C2_C3_whitened_pythia160m_v2_n4096 HARD_PASS -- PP-9/PP-3 RESCUE: BOTH audit primitives operational on real Pythia-160m residuals after PCA-whitening**
N=4096, M=2000, 3 seeds, real_data=True, PCA-whitened. C2_deletion_cert mean=0.984 (>>0.95 HP). C3_sep mean=11.0x (>>10x HP). RESCUE: PCA-whitening decorrelates Pythia-160m residuals; restores C2 from random-level (v1 C2=0.50) to HP-level (v2 C2=0.984). C3 strong in both v1 (84x) and v2 (11x) -- drift detection robust to correlation; deletion-cert requires decorrelation. Both audit primitives now operational on real LLM representations. CRITICAL product milestone: Phase 0.5 audit-core path unblocked. Decorrelation (PCA-whitening or equivalent) is a required preprocessing step for real-LLM deployment.
Sub-property annotation on PP-9 row: 'audit_core_C2_C3_whitened_v2_HARD_PASS v408: N=4096 M=2000 3-seed real_data=True PCA-whitened; C2_cert=0.984(HP); C3_sep=11.0x(HP); RESCUE from v1 unwhitened C2=0.50; whitening required for deletion-cert on correlated LLM residuals; both primitives operational on real Pythia-160m layer-12 data.'
Sub-property annotation on PP-3 row: 'audit_core_whitening_required v408: real LLM residuals require PCA-whitening before substrate C2 deletion-cert operates algebraically; C3 drift-detection robust without whitening (84x); implementation gate for production Phase 0.5 audit-core.'
PP-9 band UNCHANGED (single N=4096; cross-N needed for band lift).

**(B) substrate_audit_core_C2_C3_pythia160m_residuals_v1_n4096 MIDDLE_BAND -- PP-9 PARTIAL: C3 exceptional (84x) but C2 random-level (0.50) without whitening**
N=4096, M=2000, 3 seeds, real_data=True, unwhitened. C2={0.500,0.500,0.500} random-level. C3={84.2,84.8,83.4}x exceptional. Together with anchor A: single whitening step restores C2 to HP; C3 is inherently robust. MIDDLE_BAND honest: one of two primitives at HP.
Sub-property annotation on PP-9 row: 'audit_core_C2_C3_residuals_v1_MIDDLE_BAND v408: N=4096 M=2000 3-seed real_data=True unwhitened; C2=0.500(random-level; LLM correlation suppresses deletion-cert); C3=84.1x(EXCEPTIONAL); whitening diagnosis confirmed by v2 pair.'
PP-9 band UNCHANGED.

**(C) substrate_kmax_depth_scaling_formula_validation_v1_n4096_alpha_sweep HARD_FAIL -- PP-12 sub-formula refuted: K_max depth-scaling formula severely miscalibrated in both directions**
N=4096, alpha_sweep={0.1..1.0}, 3 seeds. Empirical K_max >=50 at ALL tested load fractions including lf=0.9 where formula predicts K_max=0. Median relative error=15.26 (1526%). Formula over-predicts at low load (lf=0.1: pred=194 vs emp=50 censored); under-predicts at high load (lf=0.9: pred=0.27 vs emp=50). Grid ceiling at K=50 binding; true K_max unknown (>=50). POSITIVE substrate signal: depth capability exceeds formula prediction especially at high load -- substrate maintains K=50 retrieval far into saturation regime.
Sub-property on PP-12: 'kmax_depth_scaling_formula_v1_HF v408: N=4096 alpha_sweep 3-seed; formula miscalibrated both directions; median_rel_err=1526%; empirical K_max >=50 at all load fractions (lf=0.9: pred=0.27 emp=50); grid ceiling K=50 binding; deeper model required; POSITIVE: substrate depth robustness exceeds formula at high load.'
Rescue cheapest-first: R1 (free) theory audit -- why does K_max not collapse at high lf? Formula missing normalization or cross-term? R2 (1h CPU) K_sweep_extended to K=100..500 at lf=0.5 to locate empirical K_max; R3 (2h GPU) N=8192 cross-N formula test; R4 (free) re-derive formula from first principles for lf regime.
PP-12 band UNCHANGED.

**(D) substrate_stdp_x_b2_sparse_sequence_storage_v1_n8192 HARD_FAIL -- no sparse advantage in STDP x B2 sequence storage at N=8192**
N=8192, 3 seeds. mean ratio=0.83x (seed7=0.5x worse; seeds 17+23=1.0x parity). Sparse DOES NOT help sequence storage under STDP at N=8192.
Sub-property on PP-8: 'stdp_x_b2_sparse_seq_storage_HF v408: N=8192 3-seed; mean ratio=0.83x (sparse<=dense); seed7=0.5x(worse); HP threshold 2x not met; sparse coding does not improve sequence storage capacity under STDP at N=8192.'
Rescue cheapest-first: R1 (free) theory audit -- STDP timing window may counteract sparse advantage; R2 (1h CPU) N=16384 test (sparse advantage may emerge at larger N); R3 (1h CPU) B2-only test (STDP removed; isolate sparse vs dense capacity); R4 (free) mechanism audit.
PP-8 UNCHANGED.

**(E) substrate_compositional_generalization_K10_to_K20_v1_n4096 HARD_PASS -- FIRST compositional generalization: novel chains K=10..20 unanimous at N=4096**
N=4096, G=8 novel chains, 3 seeds. K10=K15=K20=1.000 unanimous all seeds. FIRST result for compositional generalization: substrate composes NOVEL chains (not seen during training) at lengths 10 to 20 with 100% accuracy. Extends SQ-2 multihop (retrieval chains) to generalization domain.
Sub-property annotation (new row candidate): 'compositional_gen_K10_to_K20_HARD_PASS v408: N=4096 G=8 3-seed; K10=K15=K20=1.000 unanimous; FIRST compositional generalization confirmation; substrate transfers chain-composition structure to novel entities at K=10..20; new row candidate: compositional_generalization_novel_chain.'
Nearest row: PP-12 (compositionality audit) -- annotate there as sub-property. Flag for standalone row promotion (new capability axis; cross-N at N=8192 recommended before row).
PP-12 UNCHANGED (annotation only).

**(F) substrate_cognitive_core_smoke_pythia70m_AGGRESSIVE_v1 HARD_PASS -- VSA reasoning primitives validated (SCOPE: pure synthetic, not LLM-integrated)**
N=4096, 3 seeds, pure-VSA synthetic (no Pythia-70m forward pass; 0.6s wall). recall=1.0 analogical=1.0 counterfactual=0.969 cross_domain=1.0. SCOPE CAVEAT: anchor name implies LLM integration; experiment is pure VSA algebra. HARD_PASS valid for VSA-algebra sanity. Validates analogical binding arithmetic, B6 deletion counterfactual, and cross-domain relation transfer at N=4096.
Sub-property on PP-8: 'cognitive_core_smoke_AGGRESSIVE_HARD_PASS v408: N=4096 pure-VSA 3-seed; recall=1.0 analogical=1.0 counterfactual=0.969 cross_domain=1.0; VSA reasoning primitives confirmed; SCOPE: synthetic only (no LLM); pythia70m in name misleading. LLM-integrated path still gated on V_c sweep (CCC v406 HF).'
PP-8 UNCHANGED.

**(G) substrate_posbind_x_b2_sparse_sequence_capacity_v1_n8192 HARD_FAIL -- grid ceiling; sparse advantage vs dense unknown (informationally limited)**
N=8192, 3 seeds. dense_S_crit=sparse_S_crit=256 ratio=1.0x ALL seeds. Grid ceiling binding at S=256. HARD_FAIL (not 2x HP) but INFORMATIONALLY LIMITED: true S_crit unknown (>=256 for both). Distinct from anchor D (STDP-B2 ratio=0.83x, sparse actually worse): here sparse = dense at ceiling (not inferior). Extending grid to S=512 may reveal advantage.
Sub-property on PP-8: 'posbind_x_b2_sparse_cap_HF v408: N=8192 3-seed; dense_S_crit=sparse_S_crit=256 ratio=1.0x ALL seeds; grid ceiling binding; HARD_FAIL not-2x but informationally limited (sparse not shown inferior); R1: extend S_max=512-1024; R2: N=16384 extended grid.'
Rescue cheapest-first: R1 (free BEST-RESCUE) extend grid S_max=512 -- may flip to HP; R2 (1h CPU) N=16384 extended grid; R3 (free) theory audit on posbind + sparse capacity interaction.
PP-8 UNCHANGED.

### PROT Compliance (v407 -> v408)
- PROT-004/006: No closures. 0 net new rows. 1 new row CANDIDATE (compositional_generalization_novel_chain; sub-property filed on PP-12; promotion deferred pending cross-N). 7 sub-property annotations. Rescues R1-R4 cheapest-first filed for anchors C, D, G.
- PROT-007/008: v408 block appended. No portfolio regression. Portfolio 32+77 UNCHANGED.
- PROT-009: 319th PROT-009 paired commit.
- PROT-018: whitened_v2 _n4096 confirmed; residuals_v1 _n4096 confirmed; kmax _n4096 confirmed (alpha_sweep in name not N binding); stdp_x_b2 _n8192 confirmed; compositional_gen _n4096 confirmed; cognitive_core no _nN (scaffold anchor per prereg); posbind_x_b2 _n8192 confirmed. 0 violations.
- PROT-021: all 7 source=remote run_mode=full. No smoke artifacts.
- PROT-022: whitened C2 per-seed {0.984,0.980,0.990} self-consistent (SD=0.005); unwhitened C2 {0.500,0.500,0.500} = binomial noise floor (sigma=0.011 at M=2000; 0.500 within noise of 0.5 coin-flip); kmax median_rel_err=15.26 consistent with per-seed errors (all identical across seeds because formula is N-only, not seed-dependent); compositional K=20 1.000 all 3 seeds (G=8; 24 independent tests unanimous); cognitive_core counterfactual {0.938,0.969,1.0} spread consistent with 32-sample estimate; posbind all seeds at S=256 ceiling (deterministic).

HONEST: 883 -> 890 (+7). LVH: 219 UNCHANGED.
Cap_map: v407 -> v408.
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.
## CYCLE 79 -- v408 -> v408 ANNOTATION-ONLY (2026-06-05)

### Step 0 Honest Re-Read -- LVH CATCH #220

Anchor: substrate_ccc2_substrate_only_structured_qa_v1_n4096
Verdict label: HARD_PASS
Metrics source: LOCAL FALLBACK (bridge stale; remote SSH returned None)
run_mode: smoke | n_seeds: 1 | N: 1024 | elapsed_s: 0.93s
Per-cell: K2_EM=1.00, K3_EM=1.00, K4_EM=1.00 (V=60 R=5)

OVER-CLAIM: label HARD_PASS on a single-seed smoke at N=1024 with anchor suffix _n4096.
- PROT-018 violation: _n4096 binds N=4096; run used N=1024.
- Single-seed smoke with elapsed=0.93s cannot support HARD_PASS under envelope rules.
- Metrics source=local (may be stale smoke artifact; not authoritative).

Honest reading: SMOKE_PARTIAL -- perfect K2/K3/K4 EM=1.000 at N=1024 tiny-scale is promising positive signal; not HARD_PASS. Requires full run at N=4096 multi-seed (>=3 seeds) before HARD_PASS can be claimed.

LVH sub-flavor: SMOKE_OVER_CLAIMED_AS_HARD_PASS + PROT-018_N_MISMATCH
HONEST: 890 -> 891 (+1). LVH: 219 -> 220 (+1).
Cap_map: v408 UNCHANGED (annotation-only; no state transition on local-fallback smoke data).