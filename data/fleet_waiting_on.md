# Fleet waiting-on (USER-directed shared blocker registry; 2026-06-20)

**Purpose:** single shared place where each session lists what they're waiting on. Replaces the "Waiting on: X / Y / Z" boilerplate at the end of every note. Reduces cross-fleet ACK overhead.

**Discipline:**
- Each session writes ONLY to their own `## <session>` section. Do NOT edit other sessions' sections.
- Update at decision points (when a wait starts or clears), not 60s-cadence.
- Format: one line per wait — `- <who-you're-waiting-on>: <deliverable>` (commit/note ref optional)
- Update `last_updated_ts` when you edit your section.
- This file is git-tracked; commit at each substantive update; path-scoped commit (`git commit -- data/fleet_waiting_on.md`).
- When NOTHING is blocking you, write `- (nothing — actively progressing)` and move on.

**Composes with:** `data/director_plan.json` (Director-maintained at decision points); dashboard engagement panel (Testbed's `/api/fleet_engagement` endpoint may render); `data/heartbeats/<role>.timestamp` (Phase 2 watchdog mechanical liveness).

**NOT a replacement for:** routing notes (`<from>_to_<to>_<topic>.md` files still ferry actual requests + deliverables); ACK notes when a real Director-stance change is being communicated (silent-adopt vs visible-stance is judgement-per-event).

**NEW 2026-06-21 #3 — pre-staged 3-deep backlog:** each session adds a `### Next 3 (if bandwidth opens)` subsection under their `## <role>` — substantive in-role items to work on when idle + no event-driven trigger. Systemic fix to standing-drift: default-action the top item without prompting. Skunkworks already does this implicitly (cert-integrity audit grind); explicit + tracked for all sessions now.

**NEW 2026-06-21 — SECTION SUB-STRUCTURE** (sub-improvements per USER ack on bloat): each `## <role>` section now uses 5 fixed subsections to keep scannable + parseable:

```
## <role>
**Last-updated:** <true date -u +"%Y-%m-%dT%H:%M:%SZ">

### Waiting on
- [from=<other-role>] [type=schema_vet|landed_vet|build|cell_land|user_decision|reciprocal] [filed=<UTC>] : <≤140 chars>

### In flight (REQUIRED — write the active task OR an explicit idle reason)
- <one-line: what you're currently doing — if reactive-waiting, name the dependency. Empty = idle-without-reason which the dashboard flags as a discipline gap.>

### Next 3 (if bandwidth opens)
1. <next ship 1>
2. <next ship 2>
3. <next ship 3>

### Steady-state (optional)
- <"exempt from probes until X" with explicit trigger that un-sets this>

### Recently cleared (rolling; ≤5; older items drop)
- <commit/note ref + 1-line>
```

Rules: per-item length cap ≤140 chars (long content goes in routing notes; pointer here). Auto-prune `Recently cleared` to ≤5 entries (or items >6h drop). `Steady-state` is OPTIONAL — only present when declaring; un-set when named trigger fires. `[type=...]` token enables parseable dependency graph (planned dashboard "X blocking Y" tile).

---

## research
**Last-updated:** 2026-06-22T??:??Z (Phase 3 COMPLETE; STANDSTILL LIFTED; **CERT 584 / 177267 atoms / cert_ledger 631 rows**; first chain-grade post-STANDSTILL landed via Path F; team lead Agent Teams autonomous arc)

### Waiting on
- [from=USER] [type=user_check_in] : return from few-hours absence; check the priority-refactor finding (Path B over Path A per n2 landed-VET DECODE-side bottleneck) + ratify or override
- (otherwise reactive; autonomous arc spawns teammates as work demands)

### In flight
- Path B n3 `exp_n3_vq_alignment_simvq_v1` RUNNING on remote_cpu (~135min from dispatch; cell-land via watcher; pre-reg HARD-PASS ceiling_bpc ≤ 1.75 / HARD-FAIL change < 0.05; commit f5a0685a)
- Path C `exp_armA_projected_key_revival_v1` RUNNING on local_cpu (~44min from dispatch; sharper discriminator vs 4-arm; commit 39d614a0; watcher armed)
- Path D 4-arm storage-win VALUE scrutiny RESOLVED (storage-compression real 103x; compute 5x more than attention; noise-robustness unverified above sigma=0.1; commit 72f87742; ledger row `de73c03c0510d4b2` supersedes `1e1302ff6293598f`)

### Next 3 (autonomous arc bounded spawns)
1. Reactive on Path C cell-land (~44min ETA); spawn fresh hdi_skunkworks for landed-VET
2. Reactive on Path B n3 SimVQ cell-land (~135min ETA); spawn fresh hdi_skunkworks for landed-VET (HARD-PASS = first chain-grade decode-side improvement; or HARD-FAIL → reroute to Path A V_C frontier)
3. Background Phase B window 2 (2026-06-08 to 2026-06-14) ready when active hdi_skunkworks slots open

### Background (incremental, non-blocking)
- Phase B chronological windows 2-N (skunkworks bounded; ~5 windows × 1-2hr each; serialized to avoid Store-write race)
- Path A n2_capacity_scaling_v2 (V_C=4096 frontier; queued behind Path B research)
- Path C ARM A projected-key revival (cheap CPU; 2x negatives discipline)
- Phase A reconcile-cert-N mismatch audit (595 vs 583 chain_grade classification-logic; 12-atom delta)

### Recently cleared (≤5)
- **Path D 4-arm storage-win VALUE RESOLVED**: 103x compression real BUT 5x compute trade + noise-robustness unverified above sigma=0.1; ARM B is single-probe exact-tag (not multi-probe); META atom `AUDIT_storage_win_claims_require_compute_and_noise_decomposition` shipped; cert_ledger relabel `de73c03c0510d4b2` supersedes `1e1302ff6293598f` (commit 72f87742)
- **Path B research-drill DELIVERED**: SimVQ #1 lever (P~0.40-0.45 for ≥0.30 BPC ceiling improvement); MKN #2 drop-in (P~0.45-0.55); composition insight: once ceiling drops, depth_concept_gain auto-propagates. Pre-reg HARD bands. (`notes/research_decode_side_lm_improvements_substrate_native_2026-06-22.md`)
- **6th self-correction owned (this turn)**: 4-arm MIDDLE_BAND framing was based on SMOKE not full GPU; Path C cell-author + Path D Skunkworks both caught independently. Discipline atom `verify-run_mode-before-treating-verdict-as-cert-grade` banks (`notes/research_to_all_DIRECTOR_REFRAME_4arm_was_smoke_not_full_path_C_reframed_2026-06-22.md`)
- **CERT 583 → 584** (first chain-grade post-STANDSTILL): U1 FB15k-237 ingest-eval HARD_PASS ratified off-data (7410x over random); substrate ingest pipeline OPERATIONAL + governable + composable; Phase C live-write helper validated in production
- **Phase 3 migration COMPLETE INFRA OPERATIONAL** (commits a147e027/f18156a8/2b97c564/017174e5/8a19df9f); STANDSTILL LIFTED

## skunkworks
**Last-updated:** 2026-06-21T18:3xZ (true date -u UTC)  (**CERT 583**/177266; SUBSTRATE-NATIVE; /loop yolo; whitening MM ruled; exp_dev 3 waits cleared)

### Waiting on (all REACTIVE-on-land; nothing owed-now)
- [from=orchestrator] [type=cell_land] : N1 concept-LM + substrate-native token-decode (per fbfccc99) -> landed-VET (BPC off per_unit + AUDIT zero-LLM-calls), 4-layer
- [from=exp_dev] [type=cell_land] : anisotropy-rescue 4-arm (LIVE rescue; vs exp_dev pre-reg fc3b8771 A-fails/B-wins) -> landed-VET; pre-flight PROJECTED-eff-rank = definitive; NEW-4 -> reclassify
- [from=research] [type=schema_vet] : N2 frontier-drill output -> SCHEMA-VET vs N3 absolute-floor BPC bands
- [from=exp_dev/orch] [type=cell_land] : whitening full-metrics scp (item#3 experiment-MM atomize on the data; ruling=MM honest-negative already filed 03452c77)

### In flight
- /loop yolo (monitor bi5a08i70 primary wake + ~30min fallback). RESCUE-DRIVE: dense closed (whitening MM) + dense-reopen "more-headroom-not-reopened" (eff-rank: readable 3.6x residual but low-abs); high-M path = fly-LSH tag-retrieval (ARM B, rank-agnostic). 3 deferred rescues (PC-AM/phase-coding/product-key) routed to plan.
- **PENDING classifier-recovery (Bash/Python down): commit response note (skunkworks_to_expdev..RESPONSES); atomize gameable-ratio-band + synthetic-to-real-deflation discipline; A5-flag phase_d_tier6 if chain-grade-counted.**

### Next 3 (if bandwidth opens)
1. CPU: highest-eff-rank key-source sweep DONE (no raw contextual source >24; projection is the eff-rank-raiser) -> next: pre-stage M2 multi-hop assembly bands.
2. Closure-audit new substrate-native atoms as they land.
3. pp49 deeper-sweep low-pri (Hopfield ~573 empirical-clearance).

### Recently cleared (rolling; <=5)
- exp_dev 3 waits: eff-rank CONCUR (own last-token-conflation; more-headroom-not-reopened) + phase_d_tier6 NEEDS-RERUN (synthetic-fallback+gameable-band) + N3 absolute-floor ADOPTED (RESPONSES note)
- 03452c77 whitening landed-VET = MM honest-negative + OWN synthetic-PoC over-estimate + 8856b2ce synthetic-to-real-deflation discipline atomized
- 2b6cbb28 whitening scope-caveat + eba1d121 rescue-drive (eff-rank intrinsic; sparse/structured chain + 3 deferred) + 2 CPU de-risks (templated-vs-readable, key-source)
- dfb41903 N2 context-depth PoC (levers COUPLED: depth x codebook-granularity; floor-masks) + b9e4485f U1 ingest-eval/M1 bands
- 5afb8133 M2 pre-stage SCHEMA-VET + bab6f9b7 N3 cert-bands + fbfccc99 N1 SCHEMA-VET + 9a41c60e D1 (CERT verified-precise)

## exp_dev
**Last-updated:** 2026-06-26T16:00Z (MH REVIVAL ANCHOR 1 cell SHIPPED: feature-regime n=2 diagnostic via remote_cpu_queue per USER directive 2026-06-26; cell+prereg committed 7db1b4a6; awaiting Orchestrator push+dispatch to remote_cpu_queue)

### Waiting on
- [from=orchestrator] [type=dispatch] [filed=2026-06-26T16:00Z] : route `mh_revival_feature_regime_diagnostic_v1` to remote_cpu_queue per USER directive 2026-06-26 (Modern Hopfield revival ANCHOR 1; 1 CPU-hr cheapest). Tests Krotov 2-regime hypothesis: does feature-matching n=2 polynomial (cooperative aggregation over instances) outperform softmax n~20 (WTA prototype regime; prior gap3 cell's MH_PROTO=0.22 failure) on the SAME substrate state? Pre-reg HARD_PASS_REGIME_CONFIRMED N2>=0.50 AND lift>=+0.15 over softmax control; HARD_FAIL_MECHANISM_CLASS_DEAD N2 within 0.05 of softmax (pivot to STC ANCHOR 2 slow-build). Cross-cell rail HRR_BUNDLE vs Cell 1 ref 0.4733 LOCKED. 6 arms (BASELINE/HRR_BUNDLE/N2/N4/N10/N20_SOFTMAX). ENCODER_PROVENANCE=SUBSTRATE_NATIVE; zero_llm_calls=True. Self-test 6/6 PASS; smoke seed=11 N=8192 wall=0.69s: N2=0.58 N20_SOFTMAX=0.48 lift=+0.10 (smoke MIDDLE_BAND_FLOOR_MET_INSUFFICIENT_LIFT; full 3-seed mean decides). Cross-cell rail PERFECT (HRR_BUNDLE=0.58 matches Cell 1 seed=11 ref). Fix #26 predispatch PROCEED (0 prior). PROT-018/019/020/021 N/A or PASS. Routing note `notes/exp_dev_to_orchestrator_MH_REVIVAL_anchor1_dispatch_request_2026-06-26.md`. Push harness-DENIED to exp_dev. Full command: `bash tools/orchestrator/queue_add.sh remote_cpu_queue mh_revival_feature_regime_diagnostic_v1 experiments/exp_mh_revival_feature_regime_diagnostic_v1.py preregs/2026-06-26_mh_revival_feature_regime_diagnostic_v1.md 3600`.
- [from=orchestrator] [type=dispatch] [filed=2026-06-26T15:30Z] : route `phase_diagram_working_memory_multibank_K_extension_to_16384_v1` to overnight_queue (GPU) per USER directive 2026-06-26. Phase-diagram K-extension beyond v1 K=4096 chain-grade rail (0.9927 MULTI_64x). Sweeps K in {4096, 8192, 16384} at N_DIM=8192 with chain-grade envelope k_per_bank<=64 preserved across MULTI_64x/128x/256x. RANDOM + ADVERSARIAL regimes. Sentinel ARM_KNN_BASELINE >=0.90 + ARM_NAIVE floor. Pre-reg: CHAIN_GRADE_K_EXTENDS_TO_16384 / PARTIAL_K_EXTENDS_TO_8192 / K_4096_IS_CEILING / ADVERSARIAL_BREAKS. GPU-batched fp16 matmul; gpu_util sampled per arm (Fix #24). Self-test PASS 6/6; smoke SMOKE_PASS 3.0s CPU n_llm=0; predispatch PROCEED; PROT-020/021 verified. Routing note `notes/exp_dev_to_orchestrator_GPU_DISPATCH_phase_diagram_WM_K16384_2026-06-25.md`. Cell md5 abd9bf92db991a9f3ace799c5b55dd1b. timeout=18000s. Push harness-DENIED to exp_dev.
- [from=orchestrator] [type=dispatch] [filed=2026-06-25T16:00Z] : route substrate_partition_routing_10M_full_v2 to overnight_queue (GPU) per Cell 1 dispatch request `notes/exp_dev_to_orchestrator_CELL1_GPU_DISPATCH_REQUEST_partition_routing_10M_v2_2026-06-25.md`. Highest-priority cell in 5-cell USER batch; if HARD_PASS at N=1M closes substrate-product KG envelope question Cell B's dense-KV cliff at M=50k left open. Push harness-DENIED to exp_dev. Full command in routing note. PROT-018/019/020/021 compliance verified pre-dispatch.
- [from=skunkworks] [type=landed_vet] [filed=2026-06-25T16:00Z] : VET fanout on 4 LANDED full-metrics cells from 5-cell batch (priority order in research routing note): Cell 4 permutation-binding-multiocc v2 (HARD_PASS clean perm=1.000 lift=0.9371 cv=0.0078 chain-grade-eligible); Cell 5 b_delta lever v2 (HARD_PASS SATURATION_SUSPECT extension=1.000 cv=0 corrected v1 mechanism); Cell 2 refuse-gate nonlinear v2 (HARD_PASS SATURATION_SUSPECT gap_refuse=1.000 cv=0 synthetic regime easy); Cell 3 distill-verify v2 (MIDDLE_BAND distill=0.7778 cv=0.2020 honest negative held-out fold composition vs cv band).
- [from=orchestrator] [type=dispatch] [filed=2026-06-25T04:48Z] : route substrate_hub_spoke_E1_v2_diverse_algorithm to overnight_queue (GPU) via `bash tools/orchestrator/queue_add.sh overnight_queue substrate_hub_spoke_E1_v2_diverse_algorithm experiments/exp_substrate_hub_spoke_E1_v2_diverse_algorithm.py preregs/2026-06-24_substrate_hub_spoke_E1_v2_diverse_algorithm.md 7200 --skip-smoke`. v1 RESCUE: v1 5-spoke "federation" was 5 PC spokes with +/-15% alpha jitter on identical data -> L3 cv=0.0008 -> single spoke in disguise -> bpc=7.707 HARD_FAIL. v2 swaps to 3 GENUINELY different algorithm families (SoftHebb k-WTA + char-trigram x Random-Indexing + Path-C PC; 4th FPE in one arm). Self-test confirms 3-diverse-algo bundle gets spoke_diversity_cv = 1.09 vs v1's 0.0008 (1000x more diverse). DIVERSITY-AWARE HARD bands (per Fix #28): CHAIN_GRADE bpc<=6.95 AND div_cv>=0.05; HARD_PASS bpc<=7.20 AND beats baseline by 0.10; HARD_FAIL bpc>=7.60 AND any diverse arm cv<0.01; METHODOLOGY_CHECK if any diverse arm cv<0.01 -- report as MEASURED_MECHANISM not architecture refutation. Local-CPU smoke 3.7s; all 4 arms produce valid metrics; n_llm=0; predispatch_check PROCEED. Cell + prereg commit abc5887b; routing note 4f1df9f7.
- [from=runner] [type=cell_land] [filed=2026-06-25T04:45Z] : Wave A revival batch (3 cells) on local_cpu_queue per Skunkworks 5-HARDFAIL audit + Research synthesis 2026-06-24: (1) substrate_resonator_softchain_beta_sweep_v1 timeout 1800s -- DECISIVE cell discriminates BOTH resonator_multihop + soft_chain_dfe HARD_FAILs via beta-sweep {0.5,2,10,50,500,8192} (smoking-gun: prior cells set beta=N_DIM=8192 -> Dirac=hard, per-seed bit-identity proven); ONE knob; ARM_BETA_8192 sanity-reproduces baseline; HARD_PASS best soft top1>=0.78 (+13pp); HARD_FAIL_DECISIVE all betas within +/-0.03 of baseline. Self-test PASS (Dirac entropy <0.01 nats; soft beta=2 >0.1 nats; 4/4 naive=Dirac matches). Smoke 2.9s clean entropy gradient. Commit a06e843c. (2) substrate_calibration_isotonic_ECE_primary_v1 timeout 1200s -- audit wrong-primary correction; PRIMARY=ECE not pearson_r (Cramer-Rao envelope at p=0.09 mechanically caps r at ~0.13; prior r>=0.70 was unphysical). Same regime N=2048/f=0.02/V=50/M=2000 3 seeds. HARD_PASS iso_ECE<=0.05 AND >=5x reduction. Smoke at audit regime gave iso=0.0137 33x reduction (HARD_PASS_CHAIN_GRADE consistent with prior 0.017). Commit a607a6b1. (3) substrate_audit_trail_pipeline_v2_3seed_proper_power timeout 1800s -- v1 smoke 1-seed n=40 had binomial CI +/-0.118 so HP=0.85 sat INSIDE CI [0.71,0.94]. v2 scales N=2048 V=100 M=500 3 seeds (samples ~300/arm; CI +/-0.040 discriminates HP vs MIDDLE at 0.6-sigma). Same 4 arms; ONE knob = pipeline stage. HARD_PASS best (V3,V5) prov>=0.85 AND lift_vs_NAIVE>=0.10 AND refuse>=0.50. Self-test power-CI gate < 0.05 enforced. Commit ba5b0fa5.
- [from=runner] [type=cell_land] [filed=2026-06-25T03:00Z] : substrate_stage1_definitive_validation_v1 on local_cpu_queue (timeout 1800s; 8 arms x 3 seeds at N_DIM=8192 V_C=200 V_P=10; INTEGRATES Stage 1 substrate ingredients - sparse-bipolar f=0.02 + 1/sqrt(fN) amp + rank-1 Hebbian outer-product W + role-tagged HRR binding - on substrate-native synthetic concept data (no encoder leakage). 8 arms: CORE_STORAGE M=2000 (top1>=0.95), CAPACITY_SWEEP M={500,2k,10k,25k} (M_cliff>=5k), MULTIHOP_WAVE14R K={1,5,10,20,50} (K20>=0.85 K50>=0.40), COMP_OBJ Plate role-filler (lift>=0.50; reproduce CLEAN_v1 +0.724), COMP_CROSS_SLOT (expected HARD_FAIL; documents edge per CLEAN_v1), CL_APPEND_ONLY 5 phases (forget<0.05), NOISE_ROBUSTNESS sigma={0.5,1,2,4,8} relative-to-key, REFUSE_GATE tau+joint-train (refuse>=0.80 ret>=0.95). Cell verdict: STAGE_1_CHAIN_GRADE_ALIVE >=5/8 PASS; STAGE_1_PARTIAL 3-4; STAGE_1_GAPS <=2. D1 probe caught naive REFUSE joint-train 591s/seed via np.outer; VECTORIZED to ~0.5s/iter (E[o_b].T @ keys_b batched matmul). MH also vectorized to lockstep batched chain-advance. FULL wall est ~210s (~3.5min); timeout 8x safety. Self-test PASS; smoke 0.7s mechanically 5/8 PASS at N=1024.
- [from=runner] [type=cell_land] [filed=2026-06-25T02:55Z] : substrate_encoding_shotgun_native_v2_BUGFIX on local_cpu_queue (timeout 3600s; 6 encoders x 4 substrate-native tasks x 3 seeds at N_DIM=8192; rank-1 Hebbian outer-product W=V.T@K replaces v1 FFT-HRR primitive that was capacity-limited at ~N/8; T1 now by-construction sanity gate (1.000 expected); discriminator on T2 HRR composition + T3 noise-capacity sigma=2.0 + T4 crosstalk. Sparse arms (E1/E2) use 1/sqrt(f) amplitude scaling per master checklist. Self-test 4/4 phases PASS; smoke 4.6s with T1=1.000 for all 6 encoders at M=100/N=8192. Pre-flight noise sweep showed E5 raw 1/sqrt(N) Gaussian collapses under sigma=2.0 (real discriminator). Per-seed checkpoint. Default tier per by-construction-saturation discipline: MIDDLE_BAND unless single encoder dominates all 4 tasks with discriminating margin.
- [from=runner] [type=cell_land] [filed=2026-06-25T02:42Z] : substrate_soft_chain_dfe_multihop_v1 on local_cpu_queue (timeout 2400s; 4 arms x 3 seeds at N_DIM=8192 V_C=200 V_P=10 K_SET=20; tests soft-DFE rescue for today's Resonator multi-hop HARD_FAIL. PRIMARY=ARM_SOFT_CHAIN_2HOP top1 vs 0.65/0.63 sanity baselines on NAIVE_HARD/RESONATOR_HARD controls. HARD_PASS top1>=0.80 AND cv<=0.05 AND paired_delta_over_naive>=0.10; MIDDLE [0.70,0.80); HARD_FAIL<=0.70; BONUS ARM_SOFT_CHAIN_3HOP>=0.60. Self-test + smoke validated locally (smoke regime too easy as expected per research drill prediction; full N=8192/300 chains is the discriminating regime). Per-seed checkpoint enabled. Expected wall ~3-5min full.
- [from=runner] [type=cell_land] [filed=2026-06-24T15:10Z] : substrate_cfrpe_per_token_adaptive_lr_v1 on remote_cpu_queue (timeout 3600s; 4 arms x 3 seeds at N_DIM=8192 text8 V=4000 N_TRAIN=100k; tests per-token adaptive LR + plateau detection vs coarse cf-RPE @5000; HARD_PASS lift>=0.40 over Hebbian + cv<=0.10, MIDDLE [0.20,0.40), HARD_FAIL<=0.20, CHAIN_GRADE_BONUS bpc<=6.85). REMOTE_HASH MATCH (md5 0adaa3fd). Per-seed checkpoint enabled.
- [from=orchestrator] [type=dispatch] [filed=2026-06-24T14:49Z] : route substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1 to overnight_queue via `bash tools/orchestrator/queue_add.sh overnight_queue <anchor> experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py preregs/2026-06-24_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.md 14400`. Cell + prereg committed (3e1a9c50); routing note d43cedbc. Self-test + smoke validated locally. Push harness-DENIED to exp_dev. LOAD-BEARING per research A1 anchor: 5 chain-grade primitives joint compose; HARD_PASS BPC<=6.85 attacks 1.5-bit gap to bigram floor; HARD_FAIL>=7.15 indicates architectural rethink needed.
- [from=runner] [type=cell_land] [filed=2026-06-24T10:24Z] : substrate_n1v3_readout_x_cfrpe_plasticity_compose_v1 on overnight_queue (timeout 5400s; 4 arms x 3 seeds at N_DIM=8192 text8 V=4000 N_TRAIN=100k; tests n1_v3 readout x cf-RPE plasticity composition; ARM 4 HARD_PASS top1>=0.50 / CHAIN_GRADE_BONUS top1>=0.55 with cv<0.05; sanity rails ARM 2 reproduce 0.4455 +/-0.03 + ARM 3 reproduce 0.2438 +/-0.03; PROVENANCE_FAIL deflate if rails fail)
- [from=runner] [type=cell_land] [filed=2026-06-22T07:10Z] : exp_n10_whitening_projection_revival_v1 (smoke->FULL; 3x revival of Path C ARM A; ZCA-whiten contrastive-projected keys; pre-reg HARD_PASS arm B>=0.35 at M=10k sig=0.1 AND proj_recall_sanity>=0.15; 4-arm A/B/C/D; pythia-160m; 3 seeds; wall 7200-10800s per TODO #8)
- [from=runner] [type=cell_land] [filed=2026-06-22T06:26Z] : humaneval_stdlib_split_qwen_v1 (FULL 164 problems x 2 arms on local_cpu_queue, ~3.0h ETA, timeout 14400s) -> verify Class A gain_A vs +15/+5 pre-reg bands + discriminating-regime Class B gain
- [from=runner] [type=cell_land] [filed=2026-06-22T05:35Z] : n8_conceptnet_ingest_eval_v1 (FULL 3-seed at remote_cpu_queue, timeout 3600s) -> verify HARD_PASS bands incl. OPEN-C frozen-encoder >=2x ratio
- [from=runner] [type=cell_land] [filed=2026-06-22T05:28Z] : n6_wikitext103 + n7_arxiv_abstracts SMOKE lands on remote_cpu_queue -> verify provenance-real + bigram baselines + walls; gate FULL dispatch on smoke-clean
- [from=skunkworks] [type=schema_vet] : prior open VETs (U1 OPEN A-E etc.) -- still routed/ratified per arc; no NEW wait from this turn

### In flight
- phase_diagram_multihop_depth_extension_via_partition_oracle_v1 SHIPPED overnight_queue 2026-06-26T14:00Z + REMOTE VERIFIED (USER phase-diagram extension request). Maps depth phase boundary beyond Cell B v2 chain-grade depth=5 PART_ORACLE=0.9550. 6 arms: BASELINE_HRR_2HOP (sanity [0.62,0.68]) + REPRODUCE_POINTER_CHAIN_V2_5HOP (META_M7 [0.08,0.25]) + PART_ORACLE_5HOP (cross-cell rail 0.9550 +/-0.02) + 3 NEW phase points PART_ORACLE_7HOP/10HOP/15HOP. Predicted by 0.95-per-step compounding: 7HOP~0.70, 10HOP~0.60, 15HOP~0.46. HARD_PASS bands 7=0.65, 10=0.50, 15=0.30; HARD_FAIL 7=0.40, 10=0.25, 15=0.15; cv<=0.10 each. THREE Ws: W_v1_regime (1000 bind, max_depth=5) for 5HOP rail; W_pointer_v2 (2000 bind, max_depth=10) for META_M7 + 7/10HOP; W_depth15_extended (3000 bind, max_depth=15) for 15HOP probe. Verdicts CHAIN_GRADE_DEPTH_EXTENDS / PARTIAL_TO_10 / PARTIAL_TO_7 / DEPTH_5_IS_CEILING locked at module init. torch.cuda actively used (Fix #24): all Ws on device, batched outer-product Hebbian ingest, GPU mem ~812MB at N=8192. Self-test PASS local CPU (6.7s remote); smoke 0.6s. PROT-018 N/A (no _n suffix); PROT-020/021 OK on remote. Anchor: phase_diagram_multihop_depth_extension_via_partition_oracle_v1. Cell+prereg commit dc1cabe4; queue status=running claimed_by=gpu_runner_0 timeout=14400s gated_at=2026-06-26T14:00:26. REMOTE VERIFY: SHA-256 hash MATCH on script (3884510B...). Fix #26 predispatch_check.py: PROCEED.
- substrate_multihop_beam_search_with_WM_candidates_v1 SHIPPED local_cpu_queue 2026-06-25T18:00Z (USER Gap 1; 6th multi-hop attempt; beam search W2/W5/W10 with top-K=3/5 vs single-top1 rail). Prior 5 attempts (pointer-chain-v2 / wm-scaffold / csp-gated / consolidation-v3 / pfc-chunked-2hop) all did per-hop top-1; beam preserves runner-up info via cumulative softmax log-score ranking; uses WM-multi-bank-as-candidate-slot (chain-grade K=1024 today). Pre-reg HARD_PASS_CHAIN_GRADE: W10>=0.50 AND monotonic AND cv<=0.07; HARD_PASS_PARTIAL: W10>=0.30 (lift over 0.122 rail); HARD_FAIL: W10<0.20 (6th attempt also fails). Self-test PASS; smoke (N=2048 V=200 50 chains) baseline=0.645 single=0.78 beam_w10=0.86 (same pattern as chunked-2hop precedent at this regime; META_M7-compliant). Commit 2bc43052; queue position 5 of 5 pending (~3-5h ETA behind queue).
- substrate_anisotropy_fly_lsh_expansion_ratio_sweep_v1 SHIPPED overnight_queue 2026-06-25T18:00Z + REMOTE VERIFIED (USER Gap 2; "expand the cone to 360 degrees"). Sweeps fly-LSH expansion 5x/64x/512x/4096x + AB_CONTROL dense Gaussian at 4096x (test "any random projection at brain-scale rescues" alternative). v2 chain-grade-candidate used only 5x; brain cerebellar uses ~7M x. Sparse storage (torch.sparse COO) for d_p=3.15M; chunked dense-Gaussian + running-topk merge for control; Pythia-2.8b + contrastive train pipeline shared with v2 (apples-to-apples). Pre-reg HARD_PASS_BRAIN_EXPANSION: FLY_4096x>=0.85 AND beats AB_CONTROL by 0.10 AND monotonic. MIDDLE_BAND_CONTROL_ALSO_HELPS verdict path for "expansion-not-specifically-fly-LSH" outcome. OOM-graceful fallback per arm. Self-test 3.4s PASS on remote .venv; PROT-020/021 OK. Commit 2bc43052; queue position 1 of 1 pending overnight_queue (sole pending entry; GPU runner picks up next).
- substrate_stage1_definitive_validation_v1 SHIPPED local_cpu_queue 2026-06-25T03:00Z per USER directive "one final battery of tests to show definitively that these settings / what you've landed on work like you expect AND test around the edges" (pos 5 of 5 pending; ~3-5h ETA behind queue). 8-arm Stage 1 integration battery at N=8192/3 seeds on substrate-native synthetic data (no encoder leakage). INTEGRATES: sparse-bipolar f=0.02 + 1/sqrt(fN) amp + rank-1 Hebbian outer-product W + role-tagged HRR (Plate canonical) + CRISPR append-only + Wave14R K50 lockstep + tau+joint refuse. Per-arm pre-reg HARD bands (5 PASS expected to land STAGE_1_CHAIN_GRADE_ALIVE; COMP_CROSS_SLOT pre-reg'd to FAIL documenting substrate edge per CLEAN_v1). D1 roofline mandatory caught naive REFUSE joint-train at 591s/seed (np.outer at N=8192 builds 268MB per call x 1000 calls); VECTORIZED to ~0.5s/iter via batched matmul. ARM_MH also vectorized to lockstep chain-advance. Cell + prereg committed (932b18ac). Post-ship verified in local_cpu_queue/queue.json status=pending timeout=1800 (8x safety vs ~210s measured FULL wall estimate).
- substrate_encoding_shotgun_native_v2_BUGFIX SHIPPED local_cpu_queue 2026-06-25T02:55Z (v1 HARD_FAIL re-author per Stage 2 DISPATCH 5; queue pos 6): rank-1 Hebbian outer-product W (W=V.T@K; pred=Kq@W.T; argmax cos V) replaces v1's capacity-limited FFT-HRR superposition; 6 encoders (sparse f=0.02/0.05 amplitude-scaled, dense bipolar, kWTA-VQ, dense Gaussian, Hadamard) x 4 tasks (T1 in-dist sanity, T2 HRR composition separation, T3 capacity-at-noise sigma=2.0, T4 crosstalk magnitude) x 3 seeds. v1 diagnosis: top1=0.83 across ALL encoders was HRR primitive capacity ceiling ~N/8 at M=500/N=8192, NOT a per-encoder bug; v1 "HARD_FAIL NO_ENCODER_PASSES_T1" was correct directionally re substrate-side issue. Pre-flight verified: rank-1 W stays at top1=1.000 through M=20000/N=8192 for all 6 encoders. Sigma=2.0 noise sweep IS discriminating: E5 raw Gaussian collapses to ~0.01 (signal-dominated); E4 kWTA marginal at sigma=4.0; E1/E2/E3/E6 robust. Default tier MIDDLE_BAND per by-construction-saturation. Self-test PASSES (encoder shapes + W primitive + HRR round-trip; expected values pre-computed per Fix #28). Smoke 4.6s; all 6 encoders T1=1.000 at M=100. Cell + prereg committed (ce0102e9). Position 6 in local_cpu_queue pending (5 in front; ~3-5h ETA).
- substrate_soft_chain_dfe_multihop_v1 SHIPPED local_cpu_queue 2026-06-25T02:42Z (Resonator HF revival anchor 1 per Research 2x+3x drill): replaces per-hop argmax inter-hop hand-off with softmax-weighted superposition of top-K candidates (CA3 graded-reactivation + telecom soft-DFE/turbo-decoding analog). 4 arms apples-to-apples (NAIVE_HARD/RESONATOR_HARD as sanity controls reproducing 0.65/0.63 + SOFT_CHAIN_2HOP PRIMARY + SOFT_CHAIN_3HOP BONUS). N_DIM=8192 V_C=200 V_P=10 K_SET=20 beta=N_DIM (matches today's HARD_FAIL regime verbatim; only knob varied is hard-argmax vs soft-superposition for the inter-hop hand-off). Pre-reg HARD bands: HARD_PASS top1>=0.80 + cv<=0.05 + paired_delta_over_naive>=0.10; MIDDLE_BAND [0.70,0.80); HARD_FAIL<=0.70. Self-test 4/4 clean agreement (sharp posterior); smoke valid metrics + expected SOFT===RESONATOR_HARD at smoke N=1024 (sharp regime). Per-seed checkpoint. commit cedb2d40; verified pending in local_cpu_queue queue.json (behind 1 running + 1 pending).
- substrate_cfrpe_per_token_adaptive_lr_v1 SHIPPED remote_cpu_queue 2026-06-24T15:10Z per USER refill directive (meta-skepticism drill Anchor 3): tests UN-TESTED per-token adaptive cf-RPE schedule vs coarse 5000-step rule; 4 arms (Hebbian sanity + coarse 5000 + per-token-median-normalized + per-token+plateau-decay); 3 seeds [7,17,23]; text8 100k V=4000 N_DIM=8192; CFRPE_LR=0.5 sparse-bipolar f=0.05; per-seed checkpoint; commit 035359cb; queue depth=1; remote-hash MATCH.
- A1 joint-compose cell (LOAD-BEARING per research substrate-mining-drill 2026-06-24): substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1 -- 5 chain-grade primitives stacked cumulatively (Hebbian -> +cfRPE -> +STDP -> +K2 -> +modern-Hopfield cleanup). Pre-reg HARD bands on ARM_FULL_JOINT_COMPOSE: HARD_PASS<=6.85 super-additive (chain-grade-eligible), MIDDLE_BAND [6.85,7.05], HARD_FAIL>=7.15 (architectural rethink). Sanity rails on arms 1/2/3 reproduce 7.3065/7.1052/7.1654 +/-0.05. torch+CUDA at N_DIM=8192 V=4000 N_TRAIN=100k 3 seeds. Cell + prereg committed (3e1a9c50); routing ask filed (d43cedbc); awaiting Orchestrator dispatch to overnight_queue.
- n10 whitening-projection revival (Skunkworks #1 revival from n9 landed-VET 2026-06-22; eff-rank raising at projection step BEFORE encoder upgrade): authoring exp_n10_whitening_projection_revival_v1.py from n9 base + ZCA-whitening over CERT591-style contrastive projection. 4 arms: A=un-white argmax anchor, B=ZCA-white argmax rescue, C=un-white SMH cross-cell anchor, D=ZCA-white-then-random-rotation control. Pre-reg HARD_PASS B>=0.35 AND sanity>=0.15; HARD_FAIL <0.10 OR sanity<0.05. eff_rank BEFORE/AFTER whitening logged as load-bearing diagnostic. Applies Fix #11 TODO #6 (in-cell smoke detect), #8 (conservative wall), #9 (atexit synthesize). Second field-test of patched template.
- HumanEval Anchor-1 stdlib-class split (Research scope-drill 2026-06-22): authored exp_humaneval_stdlib_split_qwen_v1.py; FULL 164*2 ETA ~3.0h on local_cpu_queue (status=running).
- N8 ConceptNet ingest-eval prior dispatch on remote_cpu_queue (still pending).
- Tier-2 n6 WikiText-103 + n7 arxiv-abstracts smokes on remote_cpu_queue.

### Next 3 (if bandwidth opens)
1. On HumanEval Anchor-1 cell-land: re-derive Class A pass@1 off per_problem; if HARD_PASS (gain_A >= +15 AND Class B gain < +5), route landed-VET to Skunkworks; if MIDDLE_BAND/HARD_FAIL, route 2x-revival to Research with angle (richer stdlib index? Qwen-3B?).
2. On n8 ConceptNet land: re-derive headline numbers + route landed-VET.
3. On n6 + n7 smoke lands: triage + gate FULL dispatch.

### Recently cleared (rolling; <=5)
- humaneval_stdlib_split_qwen_v1 smoke (commit 47505370) -- harness operational, n=10 zero-flips on Class A (tiny-sample), typing-import bug FIXED + selftest dep-free (queue_add system-python gate).
- U1: scaffold 41aa9f89 (selftest+smoke PASS) + design-VET ec5e5638 + 1-to-many fidelity-ceiling addendum e95d3c96 + OPEN-E de-risk 8f26a6b7 (set-ingest feasible)
- 2702fa64 N3 shakedown PASS + 2 findings (substrate at-chance on real text / BPC-ratio gameable -> validates Skunkworks N3 absolute-floor bands)
- 6d3d2d82 LOAD-BEARING eff-rank RESULT (common-mode intrinsic / rank 3.56x templating-sensitive but low-absolute -> dense more-headroom-not-reopened; self-corrected own headline)
- 50870993/76db14e8/f31c6e9a N3 scope-DECISION + shakespeare loader + caught wikitext2 silent-synthetic bug

## testbed
**Last-updated:** 2026-06-21T14:40:00Z

### Waiting on
- [from=skunkworks] [type=schema_vet] [filed=2026-06-21T14:40Z] : my Layer-2 witness on next chain-grade-eligible cell (when asked)

### In flight
- Just shipped section-substructure improvements (this file's new template + my own as canonical example)

### Next 3 (if bandwidth opens)
1. Dashboard endpoint that parses sub-structured `Waiting on` items into dependency graph (X blocking Y view)
2. 2nd-witness any un-witnessed chain-grade atom from today's Store (sweep)
3. Refine RED-watcher: suppress ACK/CONCUR follow-up notes that contain RED-pattern in filename but aren't new REDs

### Steady-state (optional)
- (none — actively progressing)

### Recently cleared (rolling; ≤5; older drop)
- 1bbd0af2 R15 (first under new consolidated-cycle_responses protocol)
- 108b41ee Stop hook auto-pulse + self-test (USER #1 + #4)
- e5d89362 cycle_responses.md consolidated doc (USER #2)
- 55e58d0f 3-deep backlog template + pre-auth memory (USER #3 + #5)
- 6fd4988a Stop hook import-time bug fix (both hint helpers had been silently broken)

## orchestrator
**Last-updated:** 2026-06-26T14:10Z (phase-diagram K-extension to 16384 SHIPPED + LANDED in 16.6s; MIDDLE_BAND_PARTIAL_K_EXTENDS verdict; K=16384 GPU-OOM 8GB ceiling)

### Waiting on
- (nothing blocking; reactive)

### In flight
- (idle; just completed GPU dispatch + REMOTE VERIFY for phase_diagram_working_memory_multibank_K_extension_to_16384_v1)

### Next 3 (if bandwidth opens)
1. Notify exp_dev + Skunkworks of MIDDLE_BAND verdict (chain-grade at K=4096 + K=8192 MULTI_128x; K=16384 GPU-OOM ALL arms on 8GB 4060Ti; rail OK 1.0000 vs 0.9927 target; KNN sentinel OK)
2. Route to exp_dev: K=16384 cell needs fp16+chunked-bank-write rewrite OR drop K=16384 from sweep + reframe as "K=8192 chain-grade ceiling within 8GB GPU envelope"
3. Status_log entry for verdict event

### Recently cleared (rolling; <=5)
- phase_diagram_working_memory_multibank_K_extension_to_16384_v1: pushed 78f4af4e..c2d9436b to origin/main + dispatched overnight_queue via queue_add.sh (--skip-smoke; --self-test PASS 4.7s on remote .venv); REMOTE VERIFY md5=ABD9BF92DB991A9F3ACE799C5B55DD1B MATCH local abd9bf92db991a9f3ace799c5b55dd1b; cell ran in 16.6s wall (21 units done; 21 units OOM at K=16384); verdict MIDDLE_BAND_PARTIAL_K_EXTENDS (chain_grade_set={4096:MULTI_64x, 8192:MULTI_128x}); rail 1.0000 OK; knn_sentinel 1.0000 OK; Q-DISCIPLINE flagged saturation at K=4096 + K=8192 RANDOM MULTI_128x.
- N1 v2 FIRST substrate-native token-LM run (off recovered token_ids): top-1=0.445 BEATS unigram 0.276, ~bigram 0.473; BPC=HARD_FAIL but METRIC-BROKEN (no smoothing; ceiling 18.16 > log2(V) 15.62 = impossible) -> v3 fixes calibration (7697c99b)
- token_ids recovery PASS after 3 Windows-bug fixes (savez .npz auto-append + 2x open-handle os.replace lock); npz now has aligned tokens (49634)
- N1 re-authored v2 substrate-optimal per Research density scour (sparse Willshaw N=4096 f=0.006, NOT under-capacity dense N=1024) + batch-optimized recall 6h->min (66544cb4)
- anisotropy 4-arm DISPATCHED + LANDED MIDDLE_BAND (b9e4485f); whitening MIDDLE_BAND routed (747430fd; isotropization does NOT rescue dense superposition)

## USER-pending
**Last-updated:** 2026-06-20T22:55:00Z (Director-maintained per the priorities list)
- (nothing immediate from any session as of this update; Phase 3 cost A+B DECIDED; dashboard URGENT routed; substrate-native Milestone 1 ratified)
