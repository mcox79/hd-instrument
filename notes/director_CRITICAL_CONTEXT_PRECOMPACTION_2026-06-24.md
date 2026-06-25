# CRITICAL CONTEXT — pre-compaction survival 2026-06-24 (v2 POST-5CELL-RESCUE)

Read this FIRST after compaction to recover session state.

## SUBSTRATE-PRODUCT STORY

Substrate is MEMORY + COMPOSITION + RETRIEVAL + AUDIT device. NOT a statistical LM competitor. Brain is the existence proof. Stages: 1 base → 2 optimize → 3 higher functions → 4 LM equivalence. Don't skip.

## MORNING 2026-06-25 STATUS UPDATE (post-Skunkworks tier ruling 07:40)

### Wave E HARD_PASSes BOTH RULED MEASURED_MECHANISM by Skunkworks

**Cell 3 (SEMANTIC v3 cv-tightening) MM**: A3 already at metric ceiling in v2; cv-tightening can't upgrade what's at cv=0.000. A4 actually DEGRADED v2→v3 (0.708→0.533, -25% rel); max_cv WORSENED 0.083→0.125. By-construction saturation; cert delta=0.

**Cell 4 (multihop consolidation) MM, NOT chain-grade breakthrough**: K_THRESH=1 wrote answer-tuple directly into W as 1-hop atom; retrieval was recall not chain. Smoking gun: hop2_oracle_min=0.880 < 0.95 but CONS_IMMEDIATE=1.000 — gap proves stored answers, not composition. Plus HYBRID (0.900) < CONS_IMMEDIATE (1.000) violates prereg discriminator. Plus NAIVE=0.847 vs beta-sweep 0.65 is chain-construction mismatch (make_two_hop_chains fixed-pair vs make_chains uniform) — NOT apples-to-apples; Cell 4 didn't test the regime Barrier 1 was diagnosed in.

### Director over-claim caught (Fix #28 recurring)

Director called Cell 4 the Barrier 1 breakthrough; Skunkworks correctly under-claimed. Anisotropic drill's "Lane A: Cell 4 P=0.55" estimate invalidated. Cell 4 does NOT close Barrier 1.

### New META atoms (M4 + M5 from this audit)

- META_M4: K_THRESH=1 consolidation = by-construction-saturated
- META_M5: cross-cell baseline comparisons require chain-construction match (make_chains signature), not just V/N/K_SET

### Right Barrier 1 cells (revised path)

- **Pointer-chain hybrid** (`substrate_multihop_pointer_chain_hybrid_v1`; Director spec at `notes/director_barrier1_pointer_chain_multihop_cell_spec_2026-06-25.md`): non-compositional escape hatch; Store has exp_pointer_chain depth=100 (verify-referent pending Skunkworks)
- **Proper consolidation cell** (revise Cell H spec): K_THRESH > 1 (only consolidate after seeing chain K times) + held-out chains whose (R1, R2) frequencies are not visible at consolidation time + apples-to-apples baseline matching beta-sweep chain-construction

### Strategic Stage 1.5 reread

Lane A (Barrier 1 via consolidation) is NOT closed; needs proper test cell (K_THRESH>1, held-out chains, matched baseline). Pointer-chain hybrid spec is alternate path.

Lane B (Barrier 4 via unsupervised anisotropic encoder per USER's basis-vs-use-case principle) is the right encoder direction. Cell H' (post-drill update): 5-arm shotgun random/Olshausen-Field/DeepWalk-on-graph/Foldiak/Kohonen-SOM at V=4000 text8 scale. Any-arm HARD_PASS P=0.45.

### Anisotropy may HURT retrieval (new finding from Cell 7 deepened drill)

Per Mu-Viswanath 2018 + Ethayarajh 2019 cone-collapse literature: word embeddings cluster in narrow cones in HD space (anisotropy). Good for downstream classification, BAD for retrieval — similar items become indistinguishable in dominant directions. Substrate's primary task IS retrieval. **This means label-driven encoder cone-collapse may be a red flag at ANY V, not just Cell 7's V=12.** Reinforces USER's basis-vs-use-case principle: keep base unsupervised; let labels ride on top for tasks that need them. Materials-science analog: field-cooled crystallization commits to imposed structure; spontaneous symmetry-breaking matches input statistics. Brain chose spontaneous; substrate should too.

## MORNING 2026-06-25 STATUS — substrate INTACT, three instrument bugs identified

### Wins overnight
- **SEMANTIC battery v2 FULL: HARD_PASS 6/6 arms at production N=8192** (A3 generalization top1=1.000 PRIMARY). cv=0.083 above 0.05 chain-grade-DEFINITIVE threshold; needs cv-tightening (v3 dispatched).
- **Calibration ECE-PRIMARY: HARD_PASS_CHAIN_GRADE** — ECE 0.017 = 26.9x reduction over raw 0.4576. Audit was right: pearson_r at 9% accuracy was Cramer-Rao-capped at ~0.13.
- **Stage 1 definitive algebra battery: STAGE_1_CHAIN_GRADE_ALIVE 5/8 PASS** — CORE / CAP 25000+ / CL forget=0.0000 / NOISE sigma_cliff=8.0 all PASS.
- **hdlab beta-convention bug fix shipped** — verification test green.
- **Encoder-leakage MIDDLE_BAND**: real leakage=0.13 BPC (NOT v1's 0.44); B/C/D all at bigram floor.

### Negative — multi-hop ceiling CONFIRMED upstream of decoder
- **Soft-chain beta-sweep HARD_FAIL** — at ALL betas {0.5, 2, 10, 50, 500, 8192} top1 ≤ baseline 0.65. Sanity rail OK (beta=8192 reproduces baseline). META prediction validated: multi-hop limit is encoder/W-capacity, NOT decoder weakness.
- **Audit-trail v2 at proper power HARD_FAIL_DECISIVE** — V3 prov=0.16 vs NAIVE=0.22 (V3 WORSE). Mechanism doesn't transfer to random-bipolar HRR.

### Three production-scale "failures" — ALL instrument bugs, NOT mechanism refutations (5x drill verified)
- **Cell 7 (cross-layer FULL)**: Skunkworks tier ruling = **MEASURED_MECHANISM** (NOT chain-grade as Director proposed). Top1 indep=0.232 vs unigram=0.217 = +7.05% rel; chain-grade bar is +61.6% rel (n1_v3 precedent). Cell failed its own pre-reg BPC ≤ 6.95 (observed 7.168). Cert row hash ef35a473b197e4ee. **Mechanism finding preserved**: independent-W beats shared-W +0.376 BPC cv=0.005 — real architectural result. Skunkworks revival proposal: top1-targeted re-eval on existing indep_2L W matrices (no new training); if top1 > +30% rel re-tier.
- **Cell 8 (hub-spoke v2 MIDDLE_BAND)**: REAL bug (broken SoftHebb spoke NaN + cf-RPE gates collapsed to broken spoke + sign-sum bundle loses 0.5·log(K) MI vs MRC). Diversity_cv=0.911 (1000x v1) is real. **Revival: v3 with per-spoke health check + MRC bundle + LR-trained gates (P=0.55).**
- **Cell 9 (heterog routing HARD_FAIL_PROVENANCE)**: rail-config mismatch. Rail 7.3065 measured at N=8192/N_TRAIN=100k/3seed/f=0.05; v2 ran at N=4096/N_TRAIN=50k/2seed. Half-N predicts +0.15-0.30 BPC drift; observed +0.35 fits. Tolerance 0.05 INSIDE cross-config noise floor 0.20-0.45. Underneath: ARM_FREQ_ROUTED_K2 still beats baseline by +0.22 BPC. **Revival: v3 full-config rerun (P=0.65).**

**Net:** substrate mechanisms ALL INTACT across cells 7-9. Wave B/C cell-author template added new verdict classifiers without calibrating for production-regime math. Memory updated with bias category M (M1+M2+M3) + N (N1+N2).

### Wave D in flight (remote-only per USER embargo on local smokes)
- Cell 8 v3 MRC + health-check + LR gates → GPU (via orchestrator handoff)
- Cell 9 v3 full-config rerun → GPU (via orchestrator handoff)
- SEMANTIC v3 cv-tightening (5 seeds, V_cats=12) → remote CPU

## ENCODER-LEAKAGE FAIR-REGIME RETEST LANDED — MIDDLE_BAND (22:42 UTC)

Decisive cell for substrate-as-LM picture. 4 arms, 3 seeds, V=20000, properly-converged clean w2v.

**Per-arm bigram-conditional BPC:**
- A Google News w2v 100B: 9.99 (external pretrained leakage)
- B text8 w2v 17M proper: 10.12
- C random projection: 10.12
- D char trigram: 10.12
- Bigram floor: 10.12

**delta_B_minus_A = 0.13 bigram (was 0.44 in v1)** — encoder-leakage REAL but HALF v1. Remaining 0.31 was v1 measurement artifact (V=4000 unigram pinning + 1.82s undertrained arm B).

**B/C/D all at bigram floor:** Stage-1 substrate (sparse-bipolar HRR + rank-1 Hebbian + clean encoder) = bigram-equivalent on text8 LM, NOT bigram-beating. To beat bigram requires Stage 2-3 architectural levers (separated-W, diverse-algorithm federation, heterogeneous plasticity) which Wave B+C cells are testing.

**Substrate-product story UNCHANGED.** This is an LM-ceiling clarification, not a substrate refutation.

## TODAY'S DEFINITIVE FINDING (the 5-cell rescue, landed earlier)

**Five HARD_FAILs from gap-map dispatch are ZERO clean negatives.** Both research drill + Skunkworks audit confirm USER intuition. Three orthogonal failure modes:

### Mode 1: REFERENT-MISLABEL (cells 1,2,3,4,5 — ALL)
The gap-map drill 2026-06-24 claimed "Store has chain-grade solutions" for 7 gaps. Skunkworks verified per-cell `verdict` field in metrics.json:
- wave14r_multihop_resonator_N65536_v1: verdict = **RESONATOR_INSUFFICIENT** (not chain-grade)
- lap4_3_meta_calibration: verdict = **HARD_FAIL** (not chain-grade)
- exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2: verdict = **MIDDLE_BAND** (not chain-grade)
- exp_wave14_cap12_audit_trail v3+v5: both **COMPA_AUDIT_MIDDLE_BAND** (not chain-grade)
- 5 of 5 cited Store referents are NON-chain-grade. Today's HARD_FAILs REPRODUCE the referent status; don't refute mechanisms.

### Mode 2: WIRING BUG (cells 1+2: resonator + soft-chain)
Modern-Hopfield inverse-temperature `beta = N_DIM = 8192` → softmax(8192·cos) = Dirac delta at argmax = identical to hard winner-take-all.
**Smoking gun: per-seed top1 BIT-IDENTICAL between RESONATOR_HARD and SOFT_CHAIN arms (0.61/0.61, 0.645/0.645, 0.64/0.64).** Soft-DFE mechanism that 5 disparate fields unanimously recommend was NEVER ACTUALLY EXERCISED. hdlab.multi_hop convention bug propagated silently.

### Mode 3: BY-CONSTRUCTION-NEAR-FLOOR + WRONG-METRIC + UNDERPOWERED
- **Cell 3 (isotonic)**: pearson_r=0.131 ≤ Cramer-Rao bound at 9% accuracy (~0.13-0.15 max). **ECE=0.017 = 27x reduction → chain-grade-eligible.** Wrong primary metric chosen.
- **Cell 4 (hub-spoke E1)**: 15 spokes from same PC algorithm + ±15% alpha jitter → L3 recon error cv=0.0008 → ensemble rank ≈ 1 → "federation" = single spoke disguised. cf-RPE gates collapsed to uniform [0.333, 0.333, 0.333]. HP band 7.20 BPC unreachable from unigram floor 7.738 at V=4000.
- **Cell 5 (audit-trail)**: 1-seed n=40, CI ±0.042 — HP=0.85 SITS INSIDE CI on V3=0.825. V5-V3 -0.133 within single-seed noise. INDETERMINATE not REFUTED.

## ARTIFACTS

- `notes/research_5cell_HARD_FAIL_revival_3x_pure_math_2026-06-24.md` (per-cell 3x drills incl. pure math)
- `notes/research_5cell_cross_HARDFAIL_synthesis_2026-06-24.md` (cross-cell + decisive test)
- `notes/skunkworks_cert_audit_5_HARDFAILS_2026-06-24.md` (cert disposition per cell)

## STAGE 1 STATUS

8 chain-grade native capabilities INTACT: storage / capacity / pattern completion / WM cap=30 / sequence binding / compositional gen obj-axis +0.724 / CL CRISPR forget=0.006 / trained analogical recovery. Plus SEMANTIC battery A3 generalization-to-new-instance top1=1.000 (smoke 1-seed; needs full 3-seed).

## ENCODER FOUNDATIONS (per Stage 1)

- Substrate-OWNED (NO word2vec leakage; encoder-leakage retest in flight)
- Sparse f=0.02 / 1-bit bipolar / 1/sqrt(f) amplitude
- LEARNED + UPDATEABLE
- Role-tagged HRR Plate-canonical (NOT pair-storage; 1/k bug recurring)
- APPEND-ONLY growth (CRISPR)
- Storage primitive: rank-1 Hebbian outer-product W (NOT FFT-HRR superposition)

## 12-HOUR OVERNIGHT PLAN (in flight)

### Wave A (Wave A IN FLIGHT — exp_dev background agent authoring 3 cells)
1. `substrate_resonator_softchain_beta_sweep_v1` — 6-arm beta in {0.5,2,10,50,500,8192} → discriminates cells 1+2 simultaneously. Sanity: beta=8192 must reproduce baseline (confirms wiring bug). Local CPU 30min.
2. `substrate_calibration_isotonic_ECE_primary_v1` — ECE as primary metric (chain-grade-eligible per audit). Local CPU 20min.
3. `substrate_audit_trail_pipeline_v2_3seed_proper_power` — 3 seeds, n=200, N=2048, V=100, M=500 → CI ±0.035 discriminates HP from V3. Local CPU 30min.

### Wave B (1-3h, main thread)
4. hdlab/multi_hop.py beta-convention bug fix (Edit + test)
5. `substrate_hub_spoke_E1_v2_diverse_algorithm` — S1=SoftHebb + S2=char-trigram-RI + S3=PC (THREE DIFFERENT ALGORITHMS not alpha-jitter). GPU full overnight.

### Wave C (3-6h)
6. Encoder-leakage fair-regime retest LANDS (5-7h ETA from pre-compaction). Process per Fix #28.
7. cross_layer_compose_LM_v2_RESCUE FULL (smoke HARD_PASSed; confirm at production N text8). GPU 2-3h.
8. compose_heterogeneous_routing_v2_RESCUE FULL (smoke HARD_PASSed; confirm). GPU 2-3h.
9. SEMANTIC concept-learner battery v2 FULL — 3 seeds N=8192 V_concepts=20+ V_attrs=30+.

### Wave D (6-10h)
10. Stage 1 integration GPU cell (ac3fcd7e routed to overnight_queue).
11. Stage 1 algebra battery (a6c8f632 position 5 local CPU).

### Wave E (10-12h)
12. Director synthesis note: 5-cell rescue + corrected Stage 1 picture
13. Bias master checklist update: NEW category **N1 referent-verdict-verification** + **N2 primary-metric-Cramer-Rao-feasibility**
14. Critical context update (THIS NOTE) refreshed
15. Skunkworks META rule atomization (verify-referent-verdict-field before gap-map inclusion)

## STANDING DISCIPLINES (USER-LOCKED)

- **NEVER-GO-IDLE**: 15min ScheduleWakeup `<<autonomous-loop-dynamic>>` ARMED (fires every cycle)
- **Fix #28**: per-arm metrics before any cross-arm claim; default UNDER-CLAIM
- **NEW DISCIPLINE (today)**: **VERIFY-REFERENT-VERDICT-FIELD** — before citing Store cell as "proven", read its metrics.json `verdict` field, NOT verdict_msg framing
- **NEW DISCIPLINE (today)**: **METRIC-CRAMER-RAO-FEASIBILITY** — pre-reg HARD bands must be physically achievable at the data's base rate (pearson_r at low-accuracy is bounded)
- D1 roofline probe + D2 atexit + per-seed checkpoint mandatory
- 3 corpus-encoding WORLDS never mix (text8/word2vec, Pythia, synthetic)
- Lane 1 substrate-native default
- Intuitive briefings; no jargon-only
- Compare to substrate-variants, NOT transformers/word-bigram

## KEY NOTES TO READ AT WAKE-UP

- `notes/director_CRITICAL_CONTEXT_PRECOMPACTION_2026-06-24.md` (THIS NOTE)
- `notes/research_5cell_cross_HARDFAIL_synthesis_2026-06-24.md`
- `notes/skunkworks_cert_audit_5_HARDFAILS_2026-06-24.md`
- `notes/director_stage1_closure_synthesis_2026-06-24.md`
- `notes/research_gap_map_transfer_meta_revival_drill_2026-06-24.md`
- `notes/director_stage2_preauthored_dispatch_specs_2026-06-24.md` (OUTDATED — Wave A revival cells supersede)

## CELLS IN FLIGHT

- **Local CPU**: algebra battery position 5 (1800s); Wave A 3 revival cells being authored by exp_dev background agent (will queue shortly)
- **GPU overnight_queue**: Stage 1 integration NDIM phase diagram cell routed
- **Remote CPU**: encoder-leakage fair-regime retest (5-7h ETA from pre-compaction; should land in next 2-4h)
- **Main thread (Director)**: hdlab beta-bug fix (Wave B), synthesis writeups, memory updates, wake-up loop

## AT NEXT WAKE-UP

1. Pull queue state across all 3 lanes
2. Check landings via mtime scan `find data -name metrics.json -mmin -30`
3. Process landings per Fix #28 per-arm + under-claim default
4. Check exp_dev background agent: did the 3 Wave A cells dispatch?
5. Verify ScheduleWakeup re-armed
6. Brief intuitively per USER directive
7. Continue 12h plan from current wave

## SUBSTRATE-PRODUCT MOAT (Stage 1 intact + corrected today)

- Lossless retrieval (HRR exact)
- Exact compositionality (chain-grade on obj-axis +0.724; SEMANTIC battery A3 top1=1.000)
- Auditable causal chains (pending Wave A audit-trail v2 confirmation)
- No catastrophic forgetting CL via CRISPR append-only (forget=0.006)
- Online learning without fine-tuning (cf-RPE)
- Working memory cap=30 > Miller 7±2
- Energy-efficient at scale (sparse linear vs transformer quadratic)

## FORBIDDEN FRAMINGS

- "Cell X HARD_FAILed → mechanism Y refuted" — first verify referent verdict, regime match, by-construction-saturation, primary-metric-feasibility
- "Substrate beats unigram" without bigram baseline
- Comparison to word-bigram framed as "beats LM" (cross-paradigm)
- Pair-storage compositional tests (1/k ceiling)
- Same-W stacking compose (structurally broken; universal biology violation)
- Comparing across corpus worlds (text8 vs Pythia vs synthetic)
- Citing gap-map without verify-referent-verdict-field check
