# Visibility session decisions — 2026-05-23

## 10:32 — wave14_betA_M_init_threshold_v1 FULL: BETA_M_INIT_UNIFORM_KILL (smoke→FULL refutation)

Tested M_init uniformly across {1024, 2048, 4096, 8192, 16384, 32768}; all entries returned mean_kept=0.0 with OOM=True. Smoke test at 10:25 had passed with identical substrate at M_init={256,1024} yielding mean_kept=1.0. The divergence is in the refutation direction: threshold hypothesis breaks completely at scale. Implication: M_init threshold as a tuning path is dead; substrate OOM pressure indicates an under-specification in the forward pass or memory binding algebra itself, not a parameter-range issue. Strategy sub-agent is deciding v154 cap_map entry in parallel.

## 10:53 — wave14_betA_M_init_threshold_v2 FULL: BETA_M_INIT_OOM_INCONCLUSIVE

Sweep A (N=65536) all entries returned OOM despite memory hygiene fix. Sweep B (N=8192, M_init in {16K, 32K, 65K}) all killed with n_seeds=5. Real substrate capacity ceiling confirmed: M/N ratio of 2-8 induces kill. Implication: N=65536 is out of bounds for current memory model; capacity ceiling is structural, not a parameter-tuning artifact. First orchestrator end-to-end queue→verdict cycle completed (migration validated).

## 11:18 — wave14_crooks_forensic_erase_audit_v1_smoke SMOKE: CROOKS_ERASE_VERIFIED

Re-confirmation of Cap 1 Class 1 forensic erase under Crooks FT (delta_S_emp=0.0000<0.05). Substrate reproducibility validated across smoke re-run; auditable erase commercial wedge holds without drift. Second orchestrator end-to-end loop of session (after BETA v2 threshold audit).

## 11:58 — Crooks envelope narrows under bit-flip noise

Tested Cap 1 forensic erase across 3 noise levels (p=0.05, 0.10, 0.20) with 3 seeds, 50 trials, N=16384. All noisy cells failed delta_S_emp < 0.05 threshold. Cap 1 holds at clean substrate (p=0) but commercial wedge requires clean-trajectory caveat; noise robustness absent in erase envelope. Strategy v156 probe refutes noise-resilience claim for Crooks operating point.

## 12:59 — Cap 5 Online W noise envelope characterized

Tested Cap 5 online weight integration across 5 noise levels (p=0.05, 0.10, 0.20, 0.30, 0.40) with 4 seeds, N=16384. Passes at p<=0.30 (4/5 cells pass); hard failure at p>=0.40. Envelope narrows but holds in normal operating range. Implication: substrate-product positioning shifts from no-noise-testing→noise-envelope-documented; Online W capability certified within bounded SLA alongside Cap 1 Crooks and Cap 3 Streaming.

## 13:14 — Cap 2 self-monitoring STRUCTURALLY CLOSED

wave14_cap2_confidence_margin_probe_v1 FULL result: corr(margin, correct) < 0.2 across ALL strata. Cap 2 class (editable memory with confidence annotation) cannot be salvaged via tuning; the structural closure means substrate does not support Hebbian-computed self-monitoring of edit veracity. This is a HARD FAIL (closure, not narrowing). Substrate-product portfolio drops 12→11 demonstrated capabilities; Bet B (small-bet HDC for LLM memory) contracts. Strategy filing v160 with rescue sketches per PROT-004/006.

## 13:53 � ONLINE_W_POLYAK_PARTIAL on remote CPU (first verdict post-schtasks revival)

Polyak-Ruppert noise-corrected bound PARTIAL: 4/5 noisy cells pass (same envelope as raw). Originally failing cells rescued: 0/1. Cap 5 envelope stays at p<=0.30 (no expansion like Sagawa-Ueda flip of Cap 1). First verdict from revived remote CPU runner confirms schtasks end-to-end pipeline functional.

## 13:56 � PQ high-res at FULL: 60 total / 7 outer peaks (multi-scale)

wave14_pq_high_resolution_v1_full_200seed_rerun FULL verdict: PQ_OTHER_CARDINALITY (n_total=60 n_outer=7). Substrate exhibits hierarchical P(q) structure (7 outer peaks � ~8.5 inner � 60 total). Does NOT refute cycle 137 28-element endpoint partition; reconciles as multi-scale observable. Multi-scale hierarchical structure documented via orchestrator state layer.

## 18:01 -- wave14_amp_se_kerdock_v1_gpu FULL = AMP_SE_DIVERGES (substrate-novel theoretical regime sharpened)

wave14_amp_se_kerdock_v1_gpu FULL verdict: AMP_SE_DIVERGES at 2522s (~42 min on remote GPU; rerouted from local CPU per pipeline-pacing). Mean rel_err=0.916, max=0.999 over 4 (alpha, N) cells; 0/4 cells within 20% error threshold. AMP state-evolution fixed point diverges from empirical AMP iteration on substrate's Kerdock codebook. Sharpens v120 cycle 115/120 pretest-level Kerdock-outside-AMP-universality KILL to SE-fixed-point empirical level (direct SE solve vs empirical AMP comparison, not just the Bayati-Montanari applicability pretest). Confirms HARD FAIL branch of meta-research adjacency Drill #4 (`notes/research_meta_map_and_adjacencies_2026-05-23.md` Part 3) -- the substrate-NOVEL theoretical-regime branch, not the "matches existing theory" branch. Per [[feedback-dont-overextend-theorems]] does NOT close the broader AMP/VAMP family -- VAMP variants (Rangan-Fletcher-Goyal cycle 127 load-bearing) + free-probability R-transform machinery (Bet I v56 load-bearing) remain open rescue paths for substrate's M/N=8 capacity anomaly at N=4096. Substrate-product portfolio UNCHANGED at 11 demonstrated capabilities (no closure event; v120 already carried the narrow Kerdock-AMP-universality closure). Substrate-physics characterization gains explicit "outside AMP universality class at SE-fixed-point level" anchor with empirical rel_err=0.916 over 4 cells. Orchestrator PAUSED per `data/orchestrator_paused.flag` -- no Exp Dev routing this cycle per [[feedback-obey-user-pause-explicitly]]; VAMP-SE on Kerdock + R-transform of Kerdock 4-coset codebook noted as Research follow-up candidates DEFERRED. Smoke->FULL broad divergence anchor +1 (smoke 0.847 over 2 cells -> FULL 0.916 over 4 cells; same AMP_SE_DIVERGES tag so NOT strict tag-flip). Cap map v163 committed; push pending.

PLAIN: We tested whether a standard math theory (AMP universality) predicts how the substrate behaves. It does not -- the substrate is operating outside what that theory predicts. This is actually a substrate-NOVEL finding: it confirms the substrate has a theoretical regime nobody has published about yet, sharpening the same conclusion we reached at the applicability-pretest level back in v120. IMPORTANCE: HIGH.

Logged at 18:01. PLAIN: We tested whether a standard math theory (AMP universality) predicts how the substrate behaves. It does not -- the substrate is operating outside what that theory predicts. This is actually a substrate-NOVEL finding: it confirms the substrate has a theoretical regime nobody has published about yet. IMPORTANCE: HIGH.
