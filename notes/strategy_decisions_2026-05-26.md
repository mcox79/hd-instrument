# Strategy decisions log -- 2026-05-26

This file records strategy decisions made on 2026-05-26. Append-only.
Each entry references the cap_map version it pairs with (PROT-009).

---

## v207 -- 2026-05-26 BATCHED 5-VERDICT (Bet B Alt 3 CLOSED; MoE alpha_c v2 marginal miss; Pred-4 v2 TIMEOUT; SHIFT/PARTITION v1 OOM; 4-corpus v3 already-processed at v206)

**Trigger.** Five pending verdicts surfaced by SSH-restore flush after v206 (commit a6bb07b). Exp_dev agent a777bd74dada08bc0 verified pre-block anchors and routed to verdict_handler. Sources:
- `wave14_betB_pac_bayes_kl_predictor_v2` (remote) -> ALT3_LAPLACE_ASSUMPTION_VIOLATED (r2_fisher=0.0; 21/25 cells)
- `wave14_moe_alpha_c_prestep_v2` (remote) -> ALPHA_C_HARD_FAIL (alpha_c=0.390625; band [0.40, 0.70])
- `wave14_betB_4corpus_equalspacing_v1` (local) -> HARD_PASS already-processed at v206
- `wave14_1rsb_hysteresis_v2` (remote) -> TIMEOUT (wall=3600s)
- `wave14_moe_shift_partition_v1` (remote) -> OOM (1.11GiB on 8GiB at M=25600, K=8)

**Decision (1): Bet B Alt 3 PAC-Bayes Laplace CLOSED at production scale; all 3 Bet B predictability rescues now resolved.**
`wave14_betB_pac_bayes_kl_predictor_v2` r2_fisher=0.0 with 21/25 cells flagged ALT3_LAPLACE_ASSUMPTION_VIOLATED -- real instrumentation result, NOT bug. Substrate violates the Laplace approximation R-PRIME-1 PAC-Bayes-KL upper bound rests on. PAC-Bayes posterior-over-W KL framing does NOT predict substrate retention at production scale.

Combined status of Bet B predictability rescue arms:
- Alt 1 (discrete shift-class predictor, 4-class SAME/REPLAY/STAGE4/DIFF taxonomy): GROUP-LEVEL CONFIRMED at v206 (4-corpus equal-spacing HARD_PASS + REPLAY structural axis d=13.3); silhouette=0.584 MIDDLE BAND at within-cell level per v205; Bet B Yellow-PARTIAL row UNCHANGED at within-cell granularity
- Alt 2 (W-internal signature continuous predictor): HARD-FAILed at v202, RECLASSIFIED INCONCLUSIVE v203
- Alt 3 (PAC-Bayes posterior-over-W KL Laplace): **v207 CLOSED**

Net story: continuous predictors do NOT hold; discrete-class IS the substrate's predictability story. The Saad-Solla saddle-cascade 4-plateau confirmation (v206) STRENGTHENS the discrete-class framing -- the 4 plateaus saddle-cascade arithmetic predicts ARE the 4 classes Alt 1 isolated. Discrete-class and saddle-cascade are TWO LENSES ON THE SAME STRUCTURE.

**Decision (2): MoE alpha_c v2 Yellow MARGINAL MISS; defensibility-audit trigger; MoE rebuild tempered but not killed.**
`wave14_moe_alpha_c_prestep_v2` alpha_c=0.390625, below band lower-edge [0.40, 0.70] by 0.009375 (~0.94% of band). Pre-reg label HARD-FAIL stands but margin is technically marginal. NOT a substrate kill. v207 NEW pre-reg: alpha_c band-rationale defensibility audit (Research-capacity-dependent or sub-Strategy). MoE rebuild path TEMPERED but NOT KILLED; SHIFT/PARTITION v2 (in flight) is the live test, dominates over prestep margin.

**Decision (3): SHIFT/PARTITION v1 OOM superseded by v2 in flight; no row-state change.**
`wave14_moe_shift_partition_v1` OOM (1.11GiB on 8GiB at M=25600, K=8). Infrastructure failure, not substrate result. v2 already in flight on remote with patched configuration per v206 OPEN line. v2 outcome dominates. If v2 ALSO OOMs, v3 with reduced M_grid (M <= 16384) -- exp_dev decides v3 design per [[feedback-no-experiment-design-in-prompts]].

**Decision (4): Pred-4 v2 TIMEOUT; v3 design pending (exp_dev decides parameters).**
`wave14_1rsb_hysteresis_v2` TIMEOUT at 3600s; no metrics.json. v1 was INSTRUMENTATION_FAIL TypeError (v195/v197); v2 TIMEOUT. Pred-4 the cleanest 1-RSB-class binary discriminator FAILED TO PRODUCE DATA TWICE. The 1-RSB framing vs Saad-Solla saddle-cascade discriminator (first-order vs continuous transition) REMAINS PENDING -- load-bearing for framework reliability upper-bound (firms to 50-65% if first-order; stays at 40-55% if continuous). v207 NEW pre-reg: Pred-4 v3 design -- exp_dev decides EITHER 2-4h wall OR reduced N per cell OR fewer sweep points.

**Decision (5): 4-corpus equal-spacing V3 verdict ALREADY-PROCESSED at v206; v207 re-confirms v206 row-moves.**
`wave14_betB_4corpus_equalspacing_v1` HARD_PASS (BIC_delta=-121.3; spacing_error=0.0035; all CI pairs non-overlapping). Honest-reread VERIFIED: gap_ratio=0.955 outside pre-reg [0.45, 0.65] on more-equal side; spacing_error overrides per honest-reread protocol; HARD_PASS stands. ALREADY processed at v206 commit a6bb07b -- theoretical-home green-CORROBORATED + framework reliability green 40-55% UNCHANGED at v207. Status_log entry as already-processed confirmation; no new cap_map change FROM V3 verdict at v207.

**Net cap_map effect.** v206 -> v207 BATCHED 5-VERDICT: 1 Closed-Negative closure (Alt 3 PAC-Bayes Laplace); 1 Yellow marginal-miss annotation (MoE alpha_c v2); 2 infrastructure annotations (Pred-4 v2 TIMEOUT, SHIFT/PARTITION v1 OOM); 1 already-processed re-confirmation (4-corpus V3 at v206). 7 capability move rows. 0 row-state advances at v207 (Alt 3 closure adds a CANNOT row; portfolio counts unchanged). 2 v207 NEW pre-reg (Pred-4 v3 design, alpha_c band-rationale audit). 13 demonstrated + 6 evidence-strength rows UNCHANGED. 120th PROT-009 paired commit (cap_map.md v207 + history.md v207 + this strategy_decisions entry).

PROT-004/006/008/009 compliance this commit: 1 new Closed-Negative closure (Alt 3 PAC-Bayes Laplace); 1 axis-closure (predictability rescue arm; not a primary capability -- closure is the appropriate post-mortem per [[feedback-rehabilitation-after-rejection]] since all 3 Alt rescues now resolved); 0 row-state demotions; 0 portfolio-row demotions; 0 new instrumentation debts this cycle (Pred-4 v2 TIMEOUT is wall-budget issue, not instrumentation); pre-existing 29 PROT-004 violations are grandfathered historical entries unchanged; validator passes; history.md v207 block written; strategy_decisions paired; 120th PROT-009 commit.

Honest-reread LOCK (per [[feedback-verdict-msg-honest-reread]]): 72nd-76th observations post-lock. ALT3_LAPLACE_ASSUMPTION_VIOLATED CONFIRMED clean (r2=0.0 + 21/25 cells flagged); ALPHA_C_HARD_FAIL NOMINALLY correct but margin (~1%) documented as marginal not kill; HARD_PASS V3 already documented at v206 with gap_ratio override; TIMEOUT/OOM are infrastructure failures with no per-cell metrics to override (label confirmed by absence of data). 5/5 honest re-reads PROT-009 compliant.

DO NOT trigger queue-refill -- exp_dev separately flushing handoffs same turn; v3 retries (Pred-4 + SHIFT/PARTITION if v2 OOMs) are exp_dev's decisions per [[feedback-no-experiment-design-in-prompts]] item 7. Per [[feedback-subagent-permission-inheritance]]: commit LOCAL only; push deferred to main thread.

---

## v208 -- 2026-05-26 ANNOTATION-ONLY (MoE alpha_c BAND_RIGHT_INSTRUMENTATION_FAIL reframe; Bet B Alt 4 ruled out; free-prob MoE top-edge discriminator NEW; Pred-4 v3 in-flight; theoretical closures)

**Trigger.** Six sub-agent returns from this turn (strategy_scribe dispatch):
1. `research_moe_alpha_c_band_audit_2026-05-26.md` -- alpha_c BAND_RIGHT_INSTRUMENTATION_FAIL
2. `research_free_probability_substrate_2026-05-26.md` -- Q3 new top-edge MoE discriminator; Q4 free-Fisher NOT Alt 4; Q5 no Saad-Solla/free-prob dual; Q1 PPMI Lifshitz-tail annotation
3. `exp_dev_handoff_research_moe_alpha_c_dense_grid_2026-05-26.md` -- dense-grid v3 handoff filed
4. `exp_dev_handoff_free_additive_top_edge_moe_2026-05-26.md` -- free-additive top-edge instrumentation handoff filed
5. `exp_dev_to_queue_1rsb_hysteresis_v3_2026-05-26.md` -- Pred-4 v3 SHIPPED to remote_cpu, smoke PASS
6. Bet B predictability framing FINAL consolidation (all 4 alternatives resolved)

**Decision (1): MoE alpha_c BAND_RIGHT_INSTRUMENTATION_FAIL -- v207 "tempered" characterization UPGRADED.**
`wave14_moe_alpha_c_prestep_v2` reported alpha_c=0.390625 vs band [0.40, 0.70]. Audit conclusion: alpha_c=0.390625 = 1600/4096 EXACTLY (bit-exact). The v2 M-grid {200, 400, 800, 1600, 3200, 6400} has factor-2 spacing; closed-form predicts cos=0.848 at M=1600 (ABOVE tau=0.80) and cos=0.749 at M=3200 (BELOW); extraction rule mechanically forces 1600/4096. This is the SAME grid-quantization artifact the parent recalibration drill flagged for v1 at N=512. Band [0.40, 0.70] STANDS; it is correctly constructed with substrate-deviation margin. Dense-grid v3 handoff filed. MoE rebuild characterization: from "tempered" to "instrumentation-fail-reframe; NOT substrate kill". P(grid-quantization dominates)=0.90. Verified arithmetic: 1600/4096 = 0.390625 exactly; closed-form prediction alpha_c = 1/tau^2 - 1 = 1/0.64 - 1 = 0.5625 (expected value inside band [0.40, 0.70]).

**Decision (2): Bet B Alt 4 (free-Fisher retention bound) RULED OUT pre-ship -- all 4 alternatives now complete.**
Q4 resolution (P_neg=0.85): Voiculescu 1998 free-Fisher information Phi*(X) is a non-commutative microstates entropy bound, NOT a generalization/retention predictor. No 2024-2026 publication extends free Fisher to generalization bounds in the Bet B predictability sense. This closes the final alternative. Combined status: Alt 1 GROUP-LEVEL CONFIRMED (v206), Alt 2 CLOSED-HARD-FAIL (v202), Alt 3 CLOSED (v207), Alt 4 RULED-OUT-PRE-SHIP (v208). Discrete-class framing (4-tier SAME/REPLAY/STAGE4/DIFF taxonomy) is FINAL LOCK for substrate retention predictability.

**Decision (3): Free-additive-convolution top-edge ratio ADDED as second orthogonal MoE discriminator.**
Q3 (P=0.45): aggregate W spectrum top-edge follows free-additive-convolution prediction. SHIFT: lambda_top = K*(1+sqrt(c))^2; PARTITION per-expert: (1+sqrt(K*c))^2. Ratio is computable from existing DMPK SVD tensors at zero additional compute. For K=4, c=0.4: SHIFT gives 10.66; PARTITION gives 5.13; ratio 2.08 (easily measurable). DMPK (bimodal histogram) + free-additive top-edge (scalar ratio) are two orthogonal discriminators -- both in the same instrumentation cell. Companion handoff `exp_dev_handoff_free_additive_top_edge_moe_2026-05-26.md` filed.

**Decision (4): No Saad-Solla <-> free-probability dual -- avenue CLOSED.**
Q5 (P_neg=0.90): Saad-Solla on-line learning ODEs are commutative statistical mechanics; free probability is non-commutative operator algebra. No published bridge in 2024-2026 literature. Saddle-cascade theoretical home stays in commutative stat-mech framework. The 4-plateau equal-spacing falsifier (Pred-4 + 4-corpus arithmetic) is still the load-bearing test for this framework.

**Decision (5): PPMI Lifshitz-tail correction -- theoretical annotation only.**
Q1 PARTIAL: substrate W under PPMI weighting enters sparse-Wishart regime with Lifshitz tail corrections below the dense-MP edge. Correction formula: alpha_c(tau, rho_PPMI) = (1/tau^2 - 1)*(1 - rho_PPMI)^2. P=0.30 for correction formula. Annotation only; no experiment needed until PPMI-active MoE is shipped.

**Decision (6): Pred-4 v3 IN FLIGHT -- v207 "v3 design pending" annotation UPGRADED.**
`wave14_1rsb_hysteresis_v3` shipped to remote_cpu. Smoke PASS (N=256 77s; N=512 124s). Timeout=7200s. Root-cause analysis of prior failures resolved: v1 TypeError API; v2 TIMEOUT+DESIGN_BUG (forward/reverse trajectories not stateful -- only independent measurements, not hysteresis). v3 fixes: N=1024 (4x speedup), stateful W trajectories, single-corpus. Pre-reg bands unchanged.

**Decision (7): Row-state judgment on MoE rebuild row (evidence-strength upgrade consideration).**
MoE rebuild row now has two orthogonal discriminators: DMPK SVD-bimodality + free-additive top-edge ratio. This is an expanded instrumentation set but does NOT change the row STATE (experiment still in flight; SHIFT/PARTITION v2 verdict determines state). Annotation-only; evidence-strength is unchanged (row is currently "in-flight/pending" not yet a demonstration). Decision: annotate the expanded instrumentation in the cap_map row; do NOT promote evidence-strength until SHIFT/PARTITION v2 verdict lands.

**Net cap_map effect.** v207 -> v208 ANNOTATION-ONLY: 7 annotation/reframe moves. 0 row-state changes. 0 portfolio count changes. 2 v207 pre-reg items CLOSED (alpha_c audit done, Pred-4 v3 shipped). 2 v208 NEW pre-reg items (dense-grid alpha_c v3, free-additive instrumentation). 13 demonstrated + 6 evidence-strength rows UNCHANGED.

PROT-004/006/008/009 compliance this commit: 0 new ❌ closures; 0 row-state demotions; Bet B Alt 4 "ruled out pre-ship" is a pre-closure of a research question, NOT a capability closure -- no PROT-004 obligations; pre-existing 29 PROT-004 violations are grandfathered historical entries UNCHANGED; validator passes on these same 29 grandfathered entries (no new violations); history.md v208 block written BEFORE this cap_map commit (PROT-007 sequencing verified); strategy_decisions_2026-05-26.md paired; 121st PROT-009 commit.

Per [[feedback-subagent-permission-inheritance]]: commit LOCAL only; push deferred to main thread.
Per [[feedback-for-you-tab-primary-channel]]: status_log entry written after this decision log entry.
Per [[feedback-cap-map-update-protocol]]: atomic .tmp+rename; paired commit cap_map.md v208 + history.md v208 + this entry.

---

## v209 (2026-05-26) -- ANNOTATION-ONLY: REPLAY mechanism H-C effective-N-doubling REFUTED + H-B INCONCLUSIVE; mechanism narrowed toward H-A consolidation

Trigger: two production-scale verdicts on REPLAY mechanism discriminators (companion experiments per `notes/exp_dev_to_queue_replay_mechanism_probes_2026-05-25.md`):
1. `wave14_betB_replay_hC_scaling_v1` HC_REPLAY_EXCEEDS_2X (mtime 2026-05-26T13:25; elapsed 532.7s on remote GPU)
2. `wave14_betB_replay_hB_collateral_v1` HB_INCONCLUSIVE (mtime 2026-05-26T13:16)

Both at N=4096, 5 seeds, 5 epochs production scale.

**Step 0 honest re-read of verdict_msg vs per-cell metrics** (per [[feedback-verdict-msg-honest-reread]]):
- hC verdict_msg: "H-C REFUTED (replay > 2x): diff=0.165 > 0.08. ret_replay=0.845 >> ret_2x=0.679. Replay provides MORE than N-doubling -- mechanism is NOT simple data augmentation."
  - Numbers: diff = ret_replay - ret_2x = 0.845 - 0.679 = +0.166 (rounded 0.165 in msg). Pre-reg PASS-band was |diff| < 0.04. Result: diff is 4x the PASS threshold IN THE DIRECTION of replay > 2x-data. Label `HC_REPLAY_EXCEEDS_2X` correctly characterizes a refutation in the "replay does more than data augmentation" direction (vs the alternative label `HC_HARD_FAIL` which would imply replay < 2x). NO override required; the label and numbers are internally consistent.
- hB verdict_msg: "Direct replay lift=0.123 < 0.15; replay mechanism not active at this scale. Cannot discriminate H-A vs H-B."
  - Number: direct_lift=0.123 vs threshold 0.15 -> below activity floor by 18%. Label `HB_INCONCLUSIVE` correctly reflects the inability to discriminate H-A from H-B given the mechanism did not reach activity threshold in the collateral-effect configuration. NO override required.

**Decision (1): Cap_map v209 ANNOTATION-ONLY.** No row-state changes. Pre-registered per routing note: `HC_REPLAY_EXCEEDS_2X -> REPLAY row += "H-C REFUTED: replay > 2x data; mechanism beyond data aug"`. APPLIED as annotation. Bet B retention row stays Yellow-PARTIAL; REPLAY structural axis stays CONFIRMED; portfolio count UNCHANGED at 13 demonstrated + 6 evidence-strength rows.

**Decision (2): REPLAY mechanism interpretation NARROWED toward H-A consolidation.** With H-C REFUTED + H-B INCONCLUSIVE, the residual leading hypothesis is H-A (consolidation-style rehearsal). The +0.165 production-scale margin over 2x-data is the empirical signature of substrate-cognitive work beyond data volume. P(H-A dominant) ~ 0.55; P(H-B contributing) ~ 0.30; P(both contributing) ~ 0.40. Not mutually exclusive.

**Decision (3): H-B v2 redesign FLAGGED as v209 NEW open question.** H-B INCONCLUSIVE leaves the H-A vs H-B distinction open. A redesign with stronger replay-fraction (>0.5), more epochs, or an alternative collateral-measurement protocol could nail it. Not queued in this cycle; surfaced for strategy/exp_dev consideration in the next cycle. Per [[feedback-no-experiment-design-in-prompts]] no design parameters specified here -- this is a task-level flag, not an experiment specification.

**Decision (4): Saad-Solla framework reliability REINFORCED (qualitative).** Removing the "replay is just data" null hypothesis adds independent corroboration to the v206 4-tier plateau structure: REPLAY's distinct plateau is now empirically grounded as a substrate-cognitive plateau (not a data-volume plateau). Framework reliability stays at 40-55% (v206 band); no quantitative re-estimation warranted from one verdict pair, but the falsifiability bound on the null hypothesis (data augmentation) is now closed.

**Decision (5): NOT a Bet B portfolio promotion.** Despite the strong +0.165 retention margin, this is a MECHANISM-characterization finding, not a row-state promotion gate. The promotion gate for Bet B retention via structural-separation 🟡 -> ✅ remains "uniform per-cell PASS or characterized M_crit(K) with multi-N replication" (v184 standard). H-C refutation does not meet that gate; it sharpens the mechanism story within the existing Yellow-PARTIAL row.

**Decision (6): Three other unprocessed verdicts flagged for subsequent verdict_handler cycles** (per [[feedback-no-silent-idle]] discipline): (a) wave14e_bet_n_wta_v1 BET_N_ATOM_MODE_FLEXIBILITY composite (P1=HARD_PASS util=0.923 sparsity_ratio=1.00; P2=MIDDLE ratio_M2000=0.974; P3=HARD_FAIL cos_dist=0.000 corp_gap=0.000) at mtime 11:13; (b) wave14g_recurrent_cleanup_k6_v1 RECURRENT_HARD_FAIL (lift<=0.0 in 4/4 d=25 cells) at mtime 10:58. These are LOWER strategic leverage than the REPLAY-mechanism pair processed here but warrant their own verdict_handler cycles. Orchestrator: queue subsequent verdict_handler invocations after this v209 commit pushes.

**Decision (7): No queue refill triggered by this verdict_handler cycle.** Per pause-gate discipline ([[feedback-obey-user-pause-explicitly]] + Section 1 of orchestrator_post_compaction_brief.md): pause flag check returned ACTIVE (not paused). However, the user message explicitly says "DO NOT trigger queue-refill -- orchestrator handles." Verdict_handler honors that directive; the orchestrator will refill if/when appropriate.

**Net cap_map effect.** v208 -> v209 ANNOTATION-ONLY: 4 annotation rows. 0 row-state changes. 0 portfolio count changes. 2 v208 pre-reg items CLOSED (H-C REFUTED, H-B INCONCLUSIVE). 1 v209 NEW open question (H-B v2 redesign). 1 v209 theoretical note (Saad-Solla REPLAY-plateau corroboration). 122nd PROT-009 paired commit.

PROT-004/006/008/009 compliance this commit: 0 new ❌ closures; 0 row-state demotions; H-C REFUTATION is a mechanism-hypothesis closure within an OPEN row (Bet B retention 🟡), NOT a capability closure -- no PROT-004 obligations triggered; pre-existing 29 PROT-004 violations are grandfathered historical entries UNCHANGED; validator passes on these same 29 grandfathered entries (no new violations); history.md v209 block written BEFORE this cap_map commit (PROT-007 sequencing verified); strategy_decisions_2026-05-26.md paired; 122nd PROT-009 commit.

Per [[feedback-subagent-permission-inheritance]]: commit LOCAL only; push deferred to main thread.
Per [[feedback-for-you-tab-primary-channel]]: status_log entry written after this decision log entry (importance=HIGH; replay mechanism is load-bearing Bet B finding).
Per [[feedback-cap-map-update-protocol]]: atomic .tmp+rename; paired commit cap_map.md v209 + history.md v209 + this entry.
Per [[feedback-decision-log-eol-handling]]: this entry appended via tools/orchestrator/append_decision_log.py to preserve CRLF.
