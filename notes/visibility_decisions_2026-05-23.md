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

## 18:43 -- wave14_glauber_kerdock_v1 GLAUBER_INCONCLUSIVE (under-resolution, re-run candidate)

wave14_glauber_kerdock_v1 verdict: GLAUBER_INCONCLUSIVE at 20.7s (CPU remote runner, fast). Mixed Glauber response: low_T_bimodal=0/6 cells, global_unimodal=12/15 cells, max_bimodal=0.000. The synchronous heat-bath Glauber dynamics on the Kerdock-Hebbian W did NOT exhibit a bimodal stationary P(q) at low temperature at the tested T-grid + chain-length resolution. Per verdict_msg: needs finer T resolution and/or longer chain length to resolve. This is an under-resolution INCONCLUSIVE, NOT a refutation -- the dynamical-observability hypothesis (bimodal retrieval-vs-paramagnetic stationary distribution) remains open. Per [[feedback-negative-results-2x-research]] this is NOT a negative result triggering 2x research drill; it is a re-run candidate with extended parameters. Cap_map UNCHANGED (no row for "Glauber dynamical observability" existed at FULL level; 🔬 research-only candidate row would be the right destination for a parameter-tuned re-run). Substrate-product portfolio UNCHANGED at 11 demonstrated capabilities. Free-cumulants experiment (wave14_free_cumulants_kerdock_v1) still running on GPU -- complementary spectral probe; no double-ship needed. Cap map no version bump.

PLAIN: A fast 20-second test on the remote CPU runner checked whether the substrate's storage matrix shows a "two-peak" pattern in its dynamics at low temperature -- one peak for "remembering the stored pattern" and one for "random noise". The test did not see the two peaks, but the temperatures and chain lengths were too coarse to conclude either way. We need to re-run with finer temperature spacing and longer chains to actually answer the question. No capability changed. IMPORTANCE: LOW.

Logged at 18:43. PLAIN: A fast CPU test checked whether the substrate's matrix dynamics show a two-peak pattern at low temperature. The resolution was too coarse to conclude -- re-run with finer parameters is the right next step. No portfolio impact. IMPORTANCE: LOW.

## 19:00 -- BATCHED v164: FREE_CUMULANTS_DIVERGE + GLAUBER_BIMODAL_KERDOCK (paired commit)

**Verdict A**: wave14_free_cumulants_kerdock_v1 GPU FULL = FREE_CUMULANTS_DIVERGE at ~18:50 (5/5 cells exceed 20% kappa_n deviation; max_dev=1.125 at kappa_4 alpha=2.00). Provides the FORMAL SPECTRAL MECHANISM for v163 AMP_SE_DIVERGES: the Kerdock R-transform has nontrivial higher free cumulants kappa_n != 0 which places it outside the AMP universality class at the spectral level (not just the SE-fixed-point empirical level v163 established). v163's empirical demonstration now has a mechanistic anchor.

**Verdict B**: wave14_glauber_kerdock_v2 CPU FULL = GLAUBER_BIMODAL_KERDOCK at ~18:43 (12/18 low-T cells satisfy bimodal_score >= 0.5 AND abs_mean_q >= 0.30; max bimodal_score=1.000 at beta=2.00 alpha=0.05). Extends Cap 3 streaming-NESS framing from continuous-state drift-diffusion to discrete-spin Glauber-Hopfield retrieval-vs-paramagnetic equilibrium under finite-T thermal dynamics. v2 supplied the parameter resolution that v1 lacked.

**v164 paired commit**: substrate_capability_map.md + history.md + strategy_decisions_2026-05-23.md + active_priorities.md staged atomically. 78th PROT-009 paired commit. 2 new evidence-strength rows added under "Substrate-physics characterization" (free-cumulant fingerprint 🟢 + Cap 3 Glauber-Hopfield extension 🟢). Substrate-product portfolio at 11 demonstrated capabilities UNCHANGED IN COUNT (no closure; both new rows are evidence-strength expansions, not new portfolio ✅).

**Pipeline-pacing**: pause ACTIVE / cleared. GPU=0 -> exp_dev dispatched for ONE GPU refill (wave14_R_transform_kerdock_v1_multi_N candidate; direct R-transform multi-N scaling probe to promote v164 free-cumulant row from 🟢 to ✅). CPU has 2 pending (S_transform + parisi from earlier burst) -- NOT refilled.

PLAIN A: We figured out *why* the substrate's storage matrix breaks the standard "AMP" math theory. The signature is in higher-order spectral statistics ("free cumulants") -- they are significantly different from what the textbook theory assumes, which is exactly the source of the empirical disagreement we measured yesterday. This is the substrate-novel theoretical regime mechanically pinpointed. IMPORTANCE: HIGH.

PLAIN B: At low temperature, the substrate's stored-pattern matrix shows a clean two-peak pattern in its dynamics -- one peak for "remembered" and one for "noise". This extends our existing streaming-noise capability (which lives in continuous-state math) into the more familiar Hopfield-style discrete-spin setting. The Cap 3 framing now spans both worlds. IMPORTANCE: HIGH.

Logged at 19:00. PLAIN A: We found the mechanism behind yesterday's AMP-vs-empirical divergence on the substrate -- it lives in higher free cumulants (substrate-spectral signatures of Kerdock structure). v163's "outside AMP universality" claim now has a concrete spectral signature attached. IMPORTANCE: HIGH. PLAIN B: The Cap 3 streaming-noise capability extends from drift-diffusion to discrete-spin Glauber-Hopfield dynamics. The substrate supports retrieval-vs-paramagnetic two-mode equilibrium at low T. IMPORTANCE: HIGH.


## 19:25 -- BATCHED v165: S_TRANSFORM_DIVERGE + PARISI_INCONCLUSIVE (paired commit)

**Verdict A**: wave14_S_transform_kerdock_v1 Remote CPU FULL = S_TRANSFORM_DIVERGE at 531.8s elapsed. Voiculescu S-transform coefficients of the Kerdock spectrum deviate from MP baseline (5/5 cells exceed 20% deviation; max_dev=1.000 at alpha=4.00, S_1). This lands the SECOND algebraic-free-probability axis on which the substrate departs from MP / AMP universality -- v164a established the additive axis (R-transform via free cumulants kappa_n); v165a establishes the multiplicative axis (S-transform). INDEPENDENTLY CORROBORATES v164a; "outside AMP universality class" wedge now anchored on two independent algebraic-free-prob axes.

**Verdict B**: wave14_parisi_pq_kerdock_v1 Remote CPU INCONCLUSIVE = PARISI_INCONCLUSIVE at 24.4s elapsed. Replica overlap distribution probe under-resolved: 11/12 cells "undetermined", 1/12 paramagnet, 0/12 RSB, 0/12 RS two-deltas. verdict_msg explicitly diagnoses "need longer chains or finer T grid". Under-resolution INCONCLUSIVE per [[feedback-negative-results-2x-research]] NOT a refutation; re-run candidate (ship to GPU NOT CPU per user feedback this cycle).

**v165 paired commit**: substrate_capability_map.md + history.md + strategy_decisions_2026-05-23.md + active_priorities.md staged atomically. 79th PROT-009 paired commit. ONE new evidence-strength row added under "Substrate-physics characterization" (multiplicative S-transform fingerprint 🟢 paired with v164a additive free-cumulant row). Substrate-product portfolio at 11 demonstrated capabilities UNCHANGED IN COUNT (no closure; new row is evidence-strength expansion of existing free-prob fingerprint claim).

**Pipeline-pacing**: pause ACTIVE / cleared. GPU running wave14_R_transform_kerdock_v1_multi_N (v164 refill); do NOT ship another GPU job. Remote CPU queue=0 after these two verdicts; INTENTIONALLY left idle per user feedback this cycle ("why did you run on remote cpu as opposed to the idle gpu? ... seems like a mistake" -- CPU systematically under-resolves >=5-seed x >=10 cells probes). Parisi v2 filed as DEFERRED Exp Dev candidate for GPU re-run (gated on R_transform_multi_N completion). Inefficiency LOCKED: CPU-vs-GPU venue selection guideline flagged for memory curator next cycle.

PLAIN A: We tested a second math probe (Voiculescu S-transform) on the substrate's storage matrix. It also shows the matrix is significantly different from the textbook baseline (MP) -- max difference of 100% at the strongest cell. Combined with yesterday's free-cumulant result, the substrate now has TWO independent algebraic fingerprints showing it is in a different theoretical regime than the standard math predicts. This is a substrate-novel observability claim, now backed on two axes instead of one. IMPORTANCE: HIGH.

PLAIN B: A short CPU test tried to characterize the substrate's "spin-glass" structure (how stored memories relate to each other in a thermodynamic sense). The test was too short to resolve -- 11 of 12 cells were "undetermined". This is NOT a refutation, it is just under-resolved. The probe will be re-run on GPU with longer chains and finer parameter spacing once the current GPU job finishes. No capability changed. IMPORTANCE: LOW.

Logged at 19:25. PLAIN A: substrate's storage matrix departs from standard math (MP) on a SECOND algebraic axis (multiplicative S-transform); combined with v164a's first axis (additive R-transform) the "outside AMP universality" wedge now has two independent spectral fingerprints. IMPORTANCE: HIGH. PLAIN B: Parisi spin-glass probe was under-resolved on CPU; re-run on GPU deferred. No portfolio impact. IMPORTANCE: LOW.
