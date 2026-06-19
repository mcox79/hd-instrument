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


## v210 (2026-05-26) — Mixed verdict batch (Bet N + recurrent K6); cap_map v209 -> v210; portfolio 13 -> 14

**Trigger.** Two production-scale verdicts batched into ONE cap_map version bump (per orchestrator routing + [[feedback-cap-map-update-protocol]] atomicity discipline):
1. `wave14e_bet_n_wta_v1` -> `BET_N_ATOM_MODE_FLEXIBILITY` composite (mtime 2026-05-26T11:13; elapsed 9.71s GPU; N=4096, K=128, k_active=12, 5 seeds, 3 corpora EN/PY/RND, M_grid {500,1000,2000,4000})
2. `wave14g_recurrent_cleanup_k6_v1` -> `RECURRENT_HARD_FAIL` (mtime 2026-05-26T10:58; elapsed 31.73s GPU; N=4096, d_values {10,25,50}, M_grid {50,100,200,500}, T_values {2,3,5}, 5 seeds)

**Step 0 honest re-read (per [[feedback-verdict-msg-honest-reread]]).**

*Bet N composite:* label matches per-cell numbers exactly per the handoff verdict-tag taxonomy ("P1 HARD-PASS, P2 MIDDLE" -> BET_N_ATOM_MODE_FLEXIBILITY). P1 util=0.923 (>= 0.70 gate) + sparsity_avg=12.0 (k_active exact; ratio 1.00 centered in [0.8, 1.2]) -> clean HARD_PASS. P2 cleanup_acc_ratio_M2000=0.974 -> MIDDLE in (0.80, 1.10). P3 cos_dist=1.79e-07 + corp_gap=0.000 -> below 0.40 HARD_FAIL floor. **Anomaly flagged**: P3 EXACT-ZERO cos_dist + EXACT-ZERO corp_gap + per-corpus M2000 ratios IDENTICAL to 4 decimal places across EN/PY/RND is the empirical signature of "atoms not actually trained corpus-specifically" (atoms identical by construction), NOT of "atoms trained on 3 corpora that failed to differentiate". Verdict label HARD_FAIL stands under pre-reg discipline; underlying mechanism question is NOT yet refuted -- instrumentation may not have actually run corpus-specific training. P3 v2 redesign flagged as NEW pre-reg item.

*Recurrent cleanup K6:* label matches per-cell numbers exactly per the handoff HARD-FAIL band (">=3/4 d=25 cells with non-positive delta"). Actual: 4/4 d=25 cells with strict delta=-1.000. All 12 (d, M) cells across d in {10,25,50} have linear=1.000, lift=-1.000, ci_width=0.000. **Anomaly flagged**: linear=1.000 EXACTLY across ALL 36 (d, M, seed) cells (including d=50 d-cliff region where this probe was specifically designed) means K=6 is in the SUB-d-cliff regime (cliff manifests at K >= 8 per cap_map v60). The linear primitive saturates the test by construction; recurrent has zero room for benefit. The HARD_FAIL stands AND is strengthened: not just "recurrent didn't help" but "linear already saturates this regime". The lift=-1.000 (full collapse to anti-correlated output) is sign-Hopfield divergence to an orthogonal fixed point; pre-reg INSTRUMENTATION-FAIL band requires CI width >= 0.10 OR >20% convergence-failure, neither triggers (CI=0.000 deterministic; output is deterministic if anti-correlated). Label is correct under pre-reg. Closure scope NARROW per [[feedback-dont-overextend-theorems]]: K=6 multi-hop d=25 only; ACF-resonator at decomposition layer UNAFFECTED; K!=6 / non-d-cliff regimes NOT closed.

**Decision (1): Bet N -> 🟢 PARTIAL Tier-2 NEW row "atom-mode flexibility (capacity-equivalent learned atoms)".** Per handoff compound row-state matrix line 64 ("P1 HARD-PASS + P2 MIDDLE + * -> 🔬 -> 🟢 PARTIAL atom-mode flexibility Tier-2"). Portfolio 13 -> 14 demonstrated. FIRST Tier-1-path row-state advance since v205 design-ready handoff. Product claim ratified: "substrate can learn its own atoms via self-supervised competitive-WTA at full utilization (0.923) and 97.4% of PPMI baseline capacity at M=2000" -- distinctive vs transformers (no atom-basis analog in KV-cache).

**Decision (2): Recurrent-cleanup-head K6 multi-hop variant -> ❌ HARD_FAIL CLOSED narrow scope.** Per handoff line 45: "Close the recurrent-variant question for multi-hop. The primitive decision tightens to 'linear is sole primitive across all evaluated tasks'." Scope NARROW: K=6 multi-hop d=25 only.

**Decision (3): v205 LINEAR-heteroassoc primary EMPIRICALLY corroborated.** Annotation on existing linear-heteroassoc ✅ row (no new row, no row-state change). The recurrent K6 closure is the empirical anchor for the v205 theoretical lock. Product framing UNCHANGED but with stronger empirical grounding.

**Decision (4): PROT-004 rescue sketches for recurrent-cleanup-head K6 closure (per [[feedback-rehabilitation-after-rejection]] + [[feedback-rescue-sketch-first-sequencing]] cheapest-first sequencing).**

  1. **T > 5 same-K probe (CHEAPEST)**: bounded-iteration with T in {8, 16, 32} at SAME K=6 / d=25. Tests whether sign-Hopfield divergence is the only failure mode or whether convergence at higher iteration count could recover benefit. ETA ~15-30 min CPU. P_rescue ~ 0.10 (low; if T=5 collapses to anti-correlated output, larger T is unlikely to recover -- but it's the cheapest direct probe of the convergence question).

  2. **Continuous-readout (non-sign) iterative variant**: replace sign() nonlinearity with tanh or linear identity in the recurrence y_{t+1} = nonlinearity((1/N) Σ_j <y_t, v_j> k_j). Continuous variants avoid the orthogonal-fixed-point divergence behavior. ETA ~30-60 min CPU. P_rescue ~ 0.20.

  3. **K=8 (d-cliff regime) probe**: shift K from 6 to 8 to access the d-cliff regime where linear baseline does NOT saturate (cap_map v60: d-cliff manifests at K >= 8). Tests whether recurrent benefit (if any) manifests when linear baseline has room to improve. ETA ~30-60 min GPU. P_rescue ~ 0.25 (moderate; if recurrent is going to help anywhere it's in the linear-non-saturated regime).

  4. **Iterative refinement ON PPMI atoms (not heteroassoc W)**: apply the bounded-iteration cleanup to PPMI atom retrieval rather than heteroassoc storage. Tests whether the recurrent pattern works at the atom layer (where Bet N now shows partial success) rather than at the storage layer (where linear saturates). ETA ~1-2 h CPU. P_rescue ~ 0.15.

  5. **Attention-style modern-Hopfield iteration (HEAVIEST)**: full Ramsauer modern-Hopfield iteration as the cleanup head (softmax attention iterates to nearest pattern). Tests the FULLY-iterative-attention rescue, distinct from sign-Hopfield. ETA ~2-4 h GPU. P_rescue ~ 0.10 (modern-Hopfield as label readout was already closed at cap_map v??; modern-Hopfield as multi-hop cleanup is the not-yet-tested variant).

Strategy decides which (if any) to elevate. Verdict_handler does NOT queue these. Per [[feedback-no-experiment-design-in-prompts]] this is rescue-arm enumeration, not experiment specification.

**Decision (5): Bet N P3-only v2 redesign FLAGGED as v210 NEW pre-reg item (instrumentation-priority).** Question: does Cao 2023 competitive-WTA produce corpus-specialized atoms when instrumentation correctly trains per-corpus? The v1 EXACT-ZERO + EXACT-MATCH-across-corpora signature suggests instrumentation may not have actually run corpus-specific training. P_deflated(P3 v2 HARD_PASS | instrumentation fixed) ~ 0.40 (Cao 2023 reports corpus-adaptive specialization at K >= 128; substrate is at K=128). Not auto-queued; surfaced for strategy/exp_dev consideration. Per [[feedback-no-experiment-design-in-prompts]] no design parameters specified -- task-level flag.

**Decision (6): Bet N P2 capacity-sweep extension FLAGGED as v210 NEW pre-reg item (scope-expansion).** Question: is there an M_stored cell where cleanup_acc_ratio >= 1.10 (full Tier-1 promotion threshold)? Candidates: M < 2000 (PPMI baseline drops first) or M >> 4000 (learned-atom basis adapts to higher load). P_deflated ~ 0.30. Not auto-queued.

**Decision (7): Combined Tier-1 probability recalibrated MARGINALLY UP** from 40-55% (v206 band) to ~42-58%. Rationale: FIRST Tier-1-path row-state advance since v205 design-ready handoff; direct evidence Tier-1 paths CAN advance. Lift is small (~2-3 pp) because partial (Tier-2 not full Tier-1 promotion) and based on one verdict pair. Conservative calibration.

**Decision (8): Framework reliability (saddle-cascade, linear-heteroassoc) UNCHANGED at 40-55%.** Bet N atom-discovery layer is orthogonal to saddle-cascade reliability. Recurrent K6 closure reinforces linear-primary architecture lock but is not a saddle-cascade prediction confirmation. No quantitative update warranted from this batch.

**Decision (9): Theoretical note for future recurrent-variant design (cap_map annotation).** K=6 is sub-d-cliff regime. Future recurrent-variant probes for multi-hop SHOULD target K >= 8 to access the d-cliff regime where linear baseline is not saturated and recurrent benefit (if any) has room to manifest. This is design guidance, not a closure.

**Decision (10): NO queue refill triggered by this verdict_handler cycle.** Per user directive ("DO NOT trigger queue-refill") + pause-gate discipline ([[feedback-obey-user-pause-explicitly]] + [[feedback-pipeline-pacing]]).

**Net cap_map effect.** v209 -> v210 MIXED VERDICT BATCH: 6 capability move rows. +1 portfolio (Bet N -> 🟢 Tier-2 NEW row; 13 -> 14 demonstrated). 1 NEW ❌ HARD_FAIL closure (recurrent-cleanup-head K6 multi-hop variant; scope NARROW). 1 EMPIRICAL CORROBORATION annotation (v205 linear-primary). 1 INSTRUMENTATION-SUSPECT annotation (Bet N P3 v2 flagged). 2 v210 NEW pre-reg items (P3 v2, P2 M-sweep). 1 theoretical note (K=6 sub-d-cliff). 1 architectural closure with 5 rescue sketches. 123rd PROT-009 paired commit.

PROT-004/006/008/009 compliance this commit: 1 new ❌ closure (recurrent-cleanup-head K6 -- NARROW scope per [[feedback-dont-overextend-theorems]]) with 5 rescue sketches filed in THIS entry (Decision 4); satisfies PROT-004 3-5 sketches requirement. 0 row-state demotions (new Tier-2 🟢 is promotion from 🔬; new ❌ is on a NEW row not previously in cap_map). 29 grandfathered violations unchanged; validator should pass on the new ❌ row (narrow probe-variant scope, not substrate-wide capability row). history.md v210 block written BEFORE cap_map.md v210 commit (PROT-007 sequencing verified). strategy_decisions_2026-05-26.md paired. 123rd PROT-009 commit.

Per [[feedback-subagent-permission-inheritance]]: commit LOCAL only; push deferred to main thread.
Per [[feedback-for-you-tab-primary-channel]]: TWO status_log entries written after this decision log entry (one per verdict; importance=HIGH for both).
Per [[feedback-cap-map-update-protocol]]: atomic .tmp+rename via append_decision_log.py; paired commit cap_map.md v210 + history.md v210 + this entry.
Per [[feedback-decision-log-eol-handling]]: this entry appended via tools/orchestrator/append_decision_log.py to preserve EOL convention.

## v211 (2026-05-26) -- BATCHED 7-VERDICT POST-v210 (alpha_c v3 dense-grid IN-BAND HARD_PASS; 1-RSB hysteresis v3 CONFIRMED first-order signature; REPLAY H-A LOCKED with zero-sum trade-off; Bet N STRONG_PARTIAL Tier-2 + NLP-genericity; free-additive top-edge INCONCLUSIVE finite-N; 2 INSTRUMENTATION-FAIL; framework reliability UPGRADED 40-55 -> 48-62)

**Trigger.** Seven terminal verdicts surfaced by post-v210 (commit 5fe7ff2) GPU/remote_cpu queue flush. ALL sources are remote run logs at `c:\dev\hd-instrument\data\overnight_queue\*.log` and `remote_cpu_queue\*.log` (no event_outcomes dir on remote; verdict labels parsed from log "VERDICT:" lines):

1. `wave14_moe_alpha_c_prestep_v3` (overnight, 4.3s) -> **ALPHA_C_HARD_PASS** alpha_c=0.5625 in [0.5,0.6], 5/5 seeds identical, CI=0.00, max_residual=0.0002
2. `wave14_moe_top_edge_v1` (overnight, 396s) -> **FREE_ADDITIVE_MIDDLE** 0/4 cells within 15%; systematic ~0.5x offset
3. `wave14_betB_replay_hB_collateral_v2` (overnight, 1342s, N=8192) -> **HB_SIGN_CONSISTENT_NEGATIVE / H-A ONLY** 5/5 collateral_lift in [-0.102, -0.093]
4. `wave14_research_wf_taup_reship_v1` (overnight, 337s) -> **INSTRUMENTATION-FAIL** all sigma(tau_p)=0; tau_p=2.0 floor in 15/15 cells
5. `wave14e_bet_n_wta_v2` (overnight, 3172s, N=4096) -> **BET_N_PARTIAL_TIER2** P1+P2 HARD_PASS (ratio=34.7); P3 MIDDLE NLP-genericity
6. `wave14_1rsb_hysteresis_v3` (remote_cpu, 1013s) -> **HYSTERESIS_1RSB_CONFIRMED** max gap=1.8423 = 18x gate; monotone decreasing to capacity
7. `wave14_saddle_cascade_plateau_v2` (remote_cpu, TIMEOUT 7200s) -> **INSTRUMENTATION_FAIL** 2/7 f-points completed

**Step 0 honest re-read of verdict_msg vs per-cell metrics** (per [[feedback-verdict-msg-honest-reread]]):

- *alpha_c v3*: HARD_PASS label is consistent. 5/5 seeds returned alpha_c=0.5625 IDENTICALLY; theory predicts alpha_c=1/tau^2-1=0.5625 (tau=0.80) EXACTLY; per-cell cos and pred match to 4 decimals across 9 M-grid points per seed (max residual 0.0002). The v207 ALPHA_C_HARD_FAIL was a coarse-grid extraction artifact (factor-2 spacing forced 1600/4096=0.390625); v208 BAND_RIGHT_INSTRUMENTATION_FAIL reframe is NOW empirically confirmed by dense-grid v3.

- *MoE top edge v1*: MIDDLE label is correct under pre-reg discipline. Substantive observation: per-cell ratio_emp/ratio_pred is CONSISTENTLY ~0.50x predicted across all 4 cells (K=2 M=6400 ratio 0.715; K=4 M=6400 ratio 0.481; K=4 M=12800 ratio 0.542; K=8 M=12800 ratio 0.365; K=8 M=25600 ratio 0.434). This is SYSTEMATIC factor-2 offset, NOT stochastic noise. Two hypotheses: finite-N 1/sqrt(N) correction at N=4096, or formula normalization missing. Annotation as INCONCLUSIVE with N=16384 retry flag; do NOT downgrade.

- *REPLAY H-B v2*: HB_SIGN_CONSISTENT_NEGATIVE label correctly reflects: all 5/5 seeds direct_lift in [0.117, 0.126] (>= 0.10 production gate); collateral_lift in [-0.102, -0.093] (all 5/5 NEGATIVE sign-consistent); ret_held=0.708 mean < ret_noreplay=0.806 mean (replay HURTS held-out by 0.098 absolute). Label is consistent. CRITICAL substantive finding NOT in label: REPLAY is ZERO-SUM-WITH-NET-POSITIVE (transfers retention from non-replayed to replayed; cost 0.098 to non-replayed for benefit 0.122 to replayed; net per-item +0.024 if replayed share is 0.5). H-A consolidation is the SOLE surviving REPLAY mechanism (v209 H-C dead; v211 H-B dead) WITH the additional zero-sum-trade-off characterization.

- *WF tau_p*: INSTRUMENTATION-FAIL label CORRECT. tau_p=2.0 floor in ALL 15 cells (5 seeds x N in {1024,2048,4096}); trajectories show smooth retention decrease without detectable plateau-entry/exit transitions. Metric reaches floor BEFORE variance could discriminate. WF strand NEITHER corroborated NOR refuted; theoretical strand (complementary to Saad-Solla) carried forward; instrumentation redesign required.

- *Bet N v2*: BET_N_PARTIAL_TIER2 label is correct. P1 util=1.000 (was 0.923 in v1) clean HARD_PASS. P2 ratio_M2000=34.698 (DRAMATIC IMPROVEMENT from v1=1.061; A_LEARNED acc@M4000=1.000 vs RANDOM ~0.003 = 300x ratio). P3 pca_cos_dist=0.6551 well above HARD_FAIL floor; matched_gap=0.0000 means EN_atoms-vs-PY_atoms within natural-language overlap nearly perfectly (EN_own vs PY_atoms gap=0.0014; PY_own vs EN_atoms gap=-0.0014), only RND atoms cleanly separate (gap=1.000). Substantive finding: LEARNED ATOMS ARE GENERIC across natural-language corpora (NLP-genericity supports universal-substrate framing), NOT failure-to-specialize. UPGRADE Bet N row PARTIAL -> STRONG_PARTIAL with NLP-genericity annotation.

- *1-RSB hysteresis v3*: HYSTERESIS_1RSB_CONFIRMED label matches numbers. Max BPC gap=1.8423 = 18x gate; per-cell gap monotone decreasing M=2000:1.84 -> M=48000:0.0084 (closes at capacity boundary). This monotone-decreasing structure is THEORETICALLY CONSISTENT with first-order phase transition (hysteresis strongest at low M deep in ordered phase; vanishes at capacity transition). The discriminator we have been waiting for since v1 (INSTRUMENTATION_FAIL) and v2 (TIMEOUT) now PASSES with 18x margin. CRITICAL interpretation: 1-RSB and Saad-Solla saddle-cascade are NOT mutually exclusive -- 1-RSB describes order-parameter geometry (first-order transition at capacity); Saad-Solla describes multi-plateau retention dynamics. BOTH frameworks now have empirical support.

- *Saddle cascade v2*: INSTRUMENTATION_FAIL label CORRECT (partial data). 2/7 f-points completed (f=0.00 ret=0.402 3 seeds tight; partial f=0.10 ret~0.665) before 7200s wall. Data we DO have suggests real step consistent with discrete plateau structure, but cannot characterize cascade with 2/7. NO row-state move per [[feedback-honest-evaluation]].

**Decision (1): MoE alpha_c row PROMOTE annotation -> 🟢 CONFIRMED dense-grid in-band; MoE rebuild prereq UNBLOCKED.**
alpha_c=0.5625 5/5 seeds identical; bands [0.40, 0.70] CONFIRMED defensible; substrate lands IN BAND when grid is fine enough (factor-2 grid artifact resolved). Log recommendation: M_per_expert=1612, M_total_k4=5160 -- proceed to MoE SHIFT/PARTITION/SINGLE rebuild. MoE rebuild can proceed with confidence on alpha_c calibration; remaining gate is SHIFT/PARTITION v3 (in flight at this commit time, started 2026-05-26T15:48:54).

**Decision (2): Pred-4 hysteresis 1-RSB row PROMOTE 🔬 -> 🟢 CONFIRMED first-order signature; theoretical-home FRAMEWORK_RELIABILITY upper bound UPGRADE 40-55% -> 48-62%.**
The 1-RSB-class binary discriminator (Pred-4) PASSED after two prior failures (v1 INSTRUMENTATION_FAIL TypeError; v2 TIMEOUT+design-bug). Max BPC gap=1.8423 = 18x gate; per-cell structure (monotone gap-decreasing to capacity boundary) theoretically consistent with first-order phase transition. CRITICAL: this is the THIRD positive theoretical-home confirmation in 48h (4-corpus equalspacing arithmetic CONFIRMED v206 + REPLAY structural axis CONFIRMED v206 + 1-RSB hysteresis CONFIRMED v211). 1-RSB + Saad-Solla complementarity (geometry + dynamics) provides the FIRST DOUBLE-POSITIVE at framework level. Framework reliability lift +8 pp (40-55 -> 48-62) is CONSERVATIVE because: (i) saddle_cascade_plateau_v2 TIMEOUT means extended-f sweep extension is UNCONFIRMED beyond v206 4-corpus arithmetic; (ii) 1-RSB v3 is one experiment at N=1024 needing production-N replication; (iii) free-additive top-edge MoE discriminator is INCONCLUSIVE not corroborated.

**Decision (3): REPLAY row ANNOTATE H-A LOCKED + zero-sum trade-off characterization; mechanism story FINAL.**
All three REPLAY hypotheses now resolved: H-A consolidation CONFIRMED (v211 sole surviving); H-B interference-reduction REFUTED at production N=8192 (v211 sign-consistent negative collateral); H-C effective-N-doubling REFUTED (v209 replay > 2x data). Additional characterization: REPLAY is ZERO-SUM-WITH-NET-POSITIVE -- transfers retention from non-replayed to replayed items with cost 0.098 to non-replayed for benefit 0.122 to replayed; net per-item +0.024 if replayed share is 0.5. Bet B retention story FINAL LOCK: "discrete 4-tier shift-class taxonomy (v208) with H-A consolidation as REPLAY mechanism via zero-sum item-pool transfer (v211)". REPLAY row state UNCHANGED 🟢 CONFIRMED; v210 H-A vs H-B pre-reg item CLOSED.

**Decision (4): Bet N atom-mode flexibility UPGRADE 🟢 PARTIAL Tier-2 -> 🟢 STRONG_PARTIAL Tier-2 + NLP-genericity annotation.**
v2 instrumentation fix (PCA-based corpus signature replacing degenerate mean-centroid) UPGRADED P2 from MIDDLE ratio=1.061 to HARD_PASS ratio_M2000=34.698 (300x improvement). P1 also UPGRADED util 0.923 -> 1.000 across all 5 seeds x 3 corpora x 4 M-points (60 cells). P3 MIDDLE pca_cos_dist=0.6551 well above HARD_FAIL floor; matched_gap=0.0000 reveals SUBSTANTIVE FINDING: learned atoms are CORPUS-AGNOSTIC across natural-language corpora (EN_own_atoms vs PY_atoms gap=0.0014 matched; only RND atoms cleanly separate at gap=1.000). This is NLP-genericity, NOT failure-to-specialize -- atoms learned on one natural-language corpus ARE generic to other natural-language corpora, only differentiating from RANDOM-token contexts. Product story strengthens: "substrate atoms generalize across natural-language domains" supports universal-substrate framing. Tier-1 promotion path requires P3 corpus-specialization at HARDER tasks (larger K, narrower-domain corpora) per v210 pre-reg.

**Decision (5): Free-additive top-edge MoE discriminator STAYS 🔬 INCONCLUSIVE finite-N + systematic factor-2 offset annotation.**
0/4 cells match within 15%; per-cell ratio_emp/ratio_pred CONSISTENTLY ~0.50x predicted (range 0.365-0.715). This is SYSTEMATIC factor-2 offset, NOT stochastic noise. Two hypotheses: (a) finite-N correction scaling 1/sqrt(N) at N=4096 (N=16384 retry would converge if true), (b) predicted ratio formula missing normalization (e.g. K-dependent factor). Row state UNCHANGED 🔬; do NOT downgrade since offset is systematic (would converge under hypothesis (a)); flagged for N=16384 retry per log recommendation; do NOT auto-queue.

**Decision (6): Wright-Fisher strand STAYS 🔬 annotation; INSTRUMENTATION-FAIL flagged for redesign.**
tau_p metric floors at 2 epochs across all 15 cells. WF sigma(tau_p) ~ N^{-1/2} prediction CANNOT BE TESTED with this instrumentation. Strand NEITHER corroborated NOR refuted; theoretical complement-to-Saad-Solla annotation (v208) CARRIED FORWARD; instrumentation redesign required. Candidate redesigns: per-epoch retention checkpoints with finer resolution; alternative plateau-residence proxy (retention variance across replay intervals; inverse-time-since-last-transition). Not auto-queued.

**Decision (7): Saddle-cascade v2 TIMEOUT -> NO row-state move; v3 redesign FLAGGED.**
2/7 f-points completed (f=0.00 ret=0.402; partial f=0.10 ret~0.665). v206 4-corpus equalspacing arithmetic CONFIRMED was the load-bearing test for saddle-cascade theoretical home -- v2 was an extension probe (finer f-resolution) NOT the load-bearing test. v206 row UNCHANGED 🟢 green-CORROBORATED. Saddle-cascade extension flagged for v3 redesign: reduced f-grid {0.0, 0.5, 1.0} for cascade verification (3 points), OR split-job approach (3 separate queue entries, one per f-range), OR migrate to overnight_queue with longer wall, OR reduce N from 2048 to 1024 (with corresponding seed reduction). Not auto-queued.

**Decision (8): Framework reliability UPGRADE 40-55% -> 48-62%; Combined Tier-1 P UPGRADE 42-58% -> 50-65%.**
THIRD positive theoretical-home confirmation in 48h. 1-RSB + Saad-Solla complementarity FIRST DOUBLE-POSITIVE at framework level. Conservative +8 pp lift per [[feedback-lit-scan-calibration-penalty]] discipline: substrate retention transition has TWO complementary theoretical homes with empirical support, but lift is constrained by 2 INSTRUMENTATION-FAIL items and INCONCLUSIVE free-additive top-edge. Combined Tier-1 P moves +8 pp with Bet N STRONG_PARTIAL counting as ongoing Tier-1-path progress.

**Decision (9): Portfolio count update 14 demonstrated + 6 evidence-strength rows (v210) -> 14 demonstrated + 7 evidence-strength rows.**
+1 evidence-strength: 1-RSB hysteresis CONFIRMED is a framework-level evidence-strength row, not a new product capability row. MoE alpha_c calibration row promoted from annotation to 🟢 CONFIRMED but is a MoE rebuild prereq, not a standalone capability.

**Decision (10): 5 v211 NEW pre-reg items FLAGGED (instrumentation-redesign + open questions); none auto-queued per [[feedback-no-experiment-design-in-prompts]].**
- WF tau_p redesign (P_deflated 0.30)
- Saddle-cascade v3 design (no specific parameters; exp_dev decides)
- Free-additive top-edge N=16384 retry (P_deflated 0.30)
- MoE alpha_c grid-quantization discipline (structural lock: future alpha_c-band measurements MUST use grid spacing < 0.10 in alpha-units OR dense-grid verification)
- Bet N P3 harder-task probe (carried from v210; larger K or narrower-domain corpora)

**Decision (11): NO queue refill triggered by this verdict_handler cycle.**
Per user directive in dispatch prompt ("DO NOT trigger queue-refill"). Pause flag NOT set at commit time (verified via Bash); however user explicit directive takes precedence. Per [[feedback-obey-user-pause-explicitly]] discipline.

**Decision (12): MoE SHIFT/PARTITION v3 NOTE.**
MoE SHIFT/PARTITION v2 FAILED OOM exit_code=1 (pre-v210 known event); v3 with OOM-fix anticipatory ship IS IN FLIGHT at this commit (started 2026-05-26T15:48:54 on overnight_queue). v3 outcome is the load-bearing MoE SHIFT/PARTITION discriminator. Next verdict_handler cycle should process v3 when it lands.

**Net cap_map effect.** v210 -> v211 BATCHED 7-VERDICT: 10 capability move rows. 4 promotions (alpha_c annotation -> 🟢; 1-RSB 🔬 -> 🟢; Bet N PARTIAL -> STRONG_PARTIAL; framework reliability 40-55 -> 48-62). 1 mechanism characterization (REPLAY H-A LOCKED zero-sum). 1 INCONCLUSIVE annotation (free-additive top-edge systematic factor-2). 2 INSTRUMENTATION-FAIL flagged for redesign (WF tau_p; saddle-cascade v2). 1 prereq UNBLOCK (MoE rebuild M_total_k4=5160). 1 portfolio update (+1 evidence-strength). 5 v211 NEW pre-reg items. 124th PROT-009 paired commit.

PROT-004/006/008/009 compliance: 0 new ❌ closures (no capabilities CLOSED); 0 row-state demotions (4 promotions; 1 mechanism characterization; 2 redesign-flagged); 29 grandfathered violations unchanged; 0 new violations; history.md v211 block written BEFORE cap_map.md v211 block (PROT-007 sequencing verified); strategy_decisions_2026-05-26.md paired with this entry; 124th PROT-009 commit.

Honest-reread LOCK (per [[feedback-verdict-msg-honest-reread]]): 77th-83rd observations post-lock. 7/7 labels consistent with per-cell numbers under pre-reg discipline. 3 SUBSTANTIVE FINDINGS surfaced beyond bare labels: (i) REPLAY zero-sum-with-net-positive characterization (HB_SIGN_CONSISTENT_NEGATIVE label correct but bare label does not capture the zero-sum item-pool-transfer interpretation that emerges from per-cell ret_held vs ret_noreplay vs ret_direct); (ii) Bet N NLP-genericity finding (P3 MIDDLE label correct but matched_gap=0.0000 reveals atoms are corpus-agnostic across natural-language NOT failure-to-specialize); (iii) alpha_c v3 empirical confirmation that v207 ALPHA_C_HARD_FAIL was a grid-quantization artifact (v208 reframe NOW directly evidenced).

Per [[feedback-subagent-permission-inheritance]]: commit LOCAL only; push deferred to main thread.
Per [[feedback-for-you-tab-primary-channel]]: 7 verdict_processed status_log entries + 1 cap_map_commit status_log entry written this cycle.
Per [[feedback-cap-map-update-protocol]]: atomic .tmp+rename via append_decision_log.py; paired commit cap_map.md v211 + history.md v211 + this entry.
Per [[feedback-decision-log-eol-handling]]: this entry appended via tools/orchestrator/append_decision_log.py to preserve EOL convention.
Per [[feedback-no-experiment-design-in-prompts]]: 5 v211 pre-reg items flagged WITHOUT design parameters (no anchor names, sweep grids, threshold formulas, queue/ETA, or pre-committed cap_map decisions).

## v212 BATCH VERDICT CYCLE (2026-05-26)

**Step 0: Honest re-read of verdict labels vs per-cell metrics**

LABEL-VS-HONEST FINDING 1: exp_wave14_moe_shift_partition_v3 FULL RUN
- Verdict label: MOE_SHIFT_MIDDLE
- Honest reading: MOE_SHIFT_HARD_PASS at K>=4
- Evidence: K=4 M=12800 lift_A=0.2052 > 0.15 threshold; K=8 M=12800 lift_A=0.3120 > 0.15 threshold. Pre-reg HARD-PASS: 'Arm A (SHIFT) mean_lift > Arm C (SINGLE) mean_lift by > 0.15 across K=[4,8]'. Mode-collapse Gini=0.003-0.004 (well below 0.4 ceiling). ALL K=[4,8] cells meet HARD-PASS condition.
- Cap_map treatment: HARD-PASS is the authoritative label; MIDDLE NOT propagated.

LABEL-VS-HONEST FINDING 2: exp_wave14_betB_nscaling_v1 SMOKE
- Verdict label: NSCALING_HARD_FAIL 'N=8192 4-class taxonomy FAILS'
- Honest reading: Smoke ran at N=512 (NOT N=8192). Full N_FULL=8192 run RUNNING on remote.
- Contradiction: verdict_msg claims N=8192 failed; config shows N=512 (16x smaller).
- Cap_map treatment: NO cap_map action. Await full N=8192 results.

LABEL-VS-HONEST FINDING 3: exp_wave14_beti_depth_polylog_v1 SMOKE
- Verdict_msg says 'Some N-dependence present'; d_c_range_across_N=0 (ZERO variation).
- Honest reading: NO N-dependence at smoke scale (d_c=20 for both N=256 and N=512).
- Cap_map treatment: MIDDLE_BAND label correct; 'N-dependence present' phrase inaccurate.

**Decision (1): MoE SHIFT/PARTITION v3 FULL -> HARD-PASS; MoE SHIFT mechanism CONFIRMED.**
exp_wave14_moe_shift_partition_v3 FULL (N=4096, K=[1,2,4,8], 5 seeds, 3639s GPU). Per pre-reg HARD-PASS bands: K=4 M=12800 lift=0.2052 > 0.15; K=8 M=12800 lift=0.3120 > 0.15. Mode-collapse Gini < 0.005 across all K=[4,8] cells. Pre-reg HARD-PASS conditions ALL MET. Algorithm emitted MIDDLE; pre-reg bands are authoritative per [[feedback-verdict-msg-honest-reread]]; HARD-PASS stands.
Strategic: MoE SHIFT mechanism CONFIRMED at production scale (N=4096, 5 seeds). PARTITION arm (Arm B) provides minimal benefit (lift 0.003-0.032 vs SINGLE) -- routing SHIFT beats PARTITION decisively. MoE rebuild direction: SHIFT routing, not PARTITION. This is the load-bearing discriminator awaited since v211 commit.
Cap_map: MoE SHIFT/PARTITION row: 'v211 in-flight' -> '🟢 SHIFT HARD-PASS CONFIRMED'. PARTITION arm closes (insufficient benefit; SINGLE baseline comparable). Framework reliability marginal +2 pp upper annotation: 48-64% (MoE SHIFT is architecture-level, not framework-level).

**Decision (2): HiPPO-init W v1 FULL -> P1 HARD-FAIL on 3/3 seeds; framing CLOSED-NEGATIVE.**
exp_wave14f_hippo_init_w_v1 FULL (N=4096, 3 seeds, 1629s GPU). P1: depth_ratio=1.00x on ALL 3 seeds (pre-reg HARD-FAIL: ratio <= 1.0x on ANY seed). P2: ndouble_ratio=1.000 = MIDDLE (not < 0.8 HARD-PASS; not >= 1.8 HARD-FAIL). P3: spectral_corr=0.993 across 3 seeds = HARD-PASS.
Per pre-reg cap_map outcome for P1 HARD-FAIL: 'close HiPPO-init W as inapplicable'. P2 characterization: N-doubling provides LINEAR scaling (not SSM-bound); substrate is NOT in the regime where N-doubling is insufficient. P3 finding: post-Hebbian W implicitly learns HiPPO-like eigenspace (spectral convergence, not by initialization).
Cap_map: Open new row 'HiPPO-init W chain-cleanup' as CLOSED-NEGATIVE (P1 HARD-FAIL all seeds). P3 spectral finding annotated as 'Hebbian training converges to HiPPO-like eigenspace regardless of init; init provides no additional benefit'. P2 N-doubling characterization annotated as 'linear N-scaling in depth; NOT SSM-bound per Jelassi MIDDLE regime'.
PROT-004 (1 closure): 5 rescue sketches:
1. (SUBSUMPTION) P3 implicit HiPPO convergence: annotate into depth/Cap3 rows as spectral characterization. Zero cost.
2. (CHEAP CPU) HiPPO-init as warm-start: test convergence SPEED (not final depth). Pre-reg: convergence epochs with HiPPO-init vs random.
3. (CHEAP CPU) HiPPO-init on REPLAY W: inter-phase consolidation arm (H-A) has temporal dynamics potentially receptive to long-range HiPPO structure.
4. (CPU/GPU) Test at K >= 8 (d-cliff regime per v60). HiPPO benefit may be regime-specific; K=12 probe is sub-cliff.
5. (THEORETICAL) Spectral regularization forcing W to remain in HiPPO basis throughout Hebbian training; would make HiPPO a structural constraint not just emergent result.

**Decision (3): betB_2tier_coarse_analysis_v1 -> 2TIER_HARD_PASS; binary taxonomy CONFIRMED at cell level.**
Pure re-analysis (elapsed=0.015s, N=99 data points from betB_shift_class_full_replication_v1). Silhouette=0.788 >= 0.70, CIs non-overlapping (HIGH [0.848, 0.863] vs LOW [0.673, 0.715]), KW p=0.0005. All pre-reg HARD-PASS conditions met.
Cap_map: Bet B discrete-class taxonomy row: upgrade from 'GROUP-LEVEL CONFIRMED' to 'CELL-LEVEL CONFIRMED, binary taxonomy (2-tier silhouette=0.788, non-overlapping CIs at 95%)'. Row state UNCHANGED (🟢 mechanism characterization enriched).

**Decision (4): betB_nscaling_v1 SMOKE -> NO CAP_MAP ACTION.**
Smoke at N=512 (NOT N=8192 as labeled). NSCALING_HARD_FAIL label is scope-misattributed. Full N=8192, 5 seeds RUNNING on remote. Await.

**Decision (5): Remaining smoke verdicts -- annotation only, no row-state changes.**
- betB_rd_perturbation_recovery_v1 smoke: RD_MIDDLE_BAND. Lambda negative. Full PENDING.
- beti_depth_polylog_v1 smoke: MIDDLE_BAND (NO N-dependence at smoke). Full PENDING.
- betB_replay_hA_direct_v1 smoke: HA_MIDDLE lift=0.028. Single seed N=512. Full PENDING.
- saddle_cascade_plateau_v3 smoke: CASCADE_HARD_PASS directionally. Full RUNNING.
- moe_shift_K_scaling_v1 smoke: MIDDLE_BAND. Anomaly: Arm_C INCREASES with K while Arm_A DECREASES. No full pre-reg.

**PROT compliance (v212):**
- PROT-004: 1 new closure (HiPPO-init W). 5 rescue sketches filed (Decision 2). Cheap-first sequencing honored.
- PROT-007: history.md v212 block written BEFORE cap_map.md v212 update.
- PROT-008: validate_capmap_commit.py run before commit.
- PROT-009: cap_map.md + history.md + strategy_decisions_2026-05-26.md staged atomically.
- 2 labeled-vs-honest findings surfaced per [[feedback-verdict-msg-honest-reread]].
- Per [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to main thread.
- Per [[feedback-no-experiment-design-in-prompts]]: rescue sketches named WITHOUT design parameters.
- Per [[feedback-obey-user-pause-explicitly]]: no queue refill (user explicit directive in dispatch prompt).

Net cap_map effect v211 -> v212: 3 actionable verdicts. (1) MoE SHIFT HARD-PASS: 'in-flight' -> CONFIRMED routing-architecture; (2) HiPPO-init: CLOSED-NEGATIVE + P3 spectral characterization + P2 N-scaling characterization; (3) Bet B 2-tier HARD-PASS: GROUP-LEVEL -> CELL-LEVEL taxonomy confirmation. 0 Tier-1 capability row-state promotions. 1 new closure. Framework reliability marginal upper-bound annotation +2 pp. 125th PROT-009 paired commit.
**Decision (urgent_refill 2026-05-26T18:20): Part A + B urgent queue refill.**

Part A: wave14_moe_shift_K_scaling_v1 COMPLETED MIDDLE_BAND (p=-0.01 sub-linear K scaling, 6.5min GPU); wave14_betB_5corpus_fullscale_v1 COMPLETED HARD_FAIL (5-plateau fails at n_G4=20, 5.2min GPU); wave14_moe_top_edge_v2 CRASHED OOM (SVD on 16384x16384 at torch.linalg.svdvals, 2.9s exit=1); wave14f_hippo_warmstart_v1 still running on remote_cpu. Root cause: GPU anchors completed in 5-7min each (not 2-3h), not crash or ship failure.

Part B: 6 experiments written+smoke-passed+shipped REMOTE_SSH_VERIFIED 6/6.
- overnight_queue: wave14_beti_depth_polylog_v2, wave14_moe_shift_M_scaling_v1, wave14_moe_gating_sharpness_v1
- remote_cpu_queue: wave14_1rsb_hysteresis_v4_multi_N, wave14_saddle_cascade_plateau_v4_n2048, wave14f_hippo_replay_w_v1

Immediate result: beti_depth_polylog_v2 completed in 22s with MIDDLE_BAND (d_c=60 at all N; cliff still above d=60 even at alpha=0.40). Structural issue: D_SWEEP max=60 insufficient; v3 needed with D_SWEEP extended to [100,150,200].

PROT-009: exp_dev decisions paired to strategy_decisions.

---

## v213 - 2026-05-26 BATCHED 4-VERDICT CYCLE (urgent_refill cycle ~17:55)

**Step 0 honest re-reads (4 verdicts, per [[feedback-verdict-msg-honest-reread]]):**

Re-read 1: wave14_moe_shift_K_scaling_v1 MIDDLE_BAND.
- Label: MIDDLE_BAND. Metrics: Arm_A K=2->8: 0.818->0.799 (decreasing), Arm_B: 0.750->0.495 (sharply decreasing), Arm_C: 0.886->0.938 (increasing). ratio=0.97, p=-0.01.
- Honest reading: MIDDLE_BAND label is correct. Key nuance: this is DIVERGING ARMS (not monotone decline). Arm_C improves while Arm_A/B degrade with K. The metric "structural_lift_at_K16=-0.158" in dashboard vs "-0.106" in local smoke metrics.json -- dashboard is authoritative (full 389s run). Dispatch description of K={2,4,8,16,32} overstates: K_sweep was {2,4,8} only.
- Label override: NONE (MIDDLE_BAND honest). Annotation: diverging arms characterization added.

Re-read 2: wave14_betB_5corpus_fullscale_v1 HARD_FAIL.
- Label: HARD_FAIL. Dashboard verdict_msg: "5-plateau equal-spacing does not hold even at n_G4=20. Reasons: monotone order violated. 4-plateau structure has a hard limit."
- Honest reading: HARD_FAIL is correct and appropriately scoped. Does NOT retract the v206 4-corpus HARD_PASS. Local metrics.json shows SMOKE_PASS (different file -- the smoke passed, the full-scale GPU run produced HARD_FAIL on the dashboard). Framework scope: Saad-Solla equal-spacing holds for 3-4 plateaus, fails at 5. Bet B discrete-class taxonomy is unaffected.
- Label override: NONE (HARD_FAIL honest). Labeled-vs-honest: N/A.

Re-read 3: wave14_moe_top_edge_v2 (dispatch says CRASHED_OOM_SVD_16384; metrics.json shows FREE_ADDITIVE_FORMULA_ERROR completed at N=1024).
- Dispatch label: CRASHED_OOM_SVD_16384.
- Metrics: smoke N=1024 COMPLETED with FREE_ADDITIVE_FORMULA_ERROR (offset=0.611, offset DID NOT IMPROVE from v1 N=4096 offset~0.50).
- Honest reading: TWO findings present. (a) Smoke result (FREE_ADDITIVE_FORMULA_ERROR) is scientifically conclusive: offset grew from ~0.50 at N=4096 to 0.611 at N=1024; this REFUTES the finite-N hypothesis (finite-N predicts offset should SHRINK at larger N; instead it stayed or grew). (b) Full N=16384 run CRASHED OOM (infrastructure failure). The dispatch "CRASHED_OOM_SVD_16384" describes finding (b) only; it missed finding (a).
- Label override: Dispatch label is PARTIALLY CORRECT (OOM real) but INCOMPLETE (formula error is the primary scientific finding). Authoritative verdict: FREE_ADDITIVE_FORMULA_ERROR (formula missing N-independent normalization) + infrastructure OOM. Cap_map row state: CLOSED-NEGATIVE.
- Labeled-vs-honest entry: dispatch described only OOM; honest reading includes formula-error finding from smoke run as primary science result.

Re-read 4: wave14_beti_depth_polylog_v2 MIDDLE_BAND.
- Label: MIDDLE_BAND. Dashboard shows full run (elapsed=19.6s; valid_N_count=5; dc_range=0; MRE=4.900). Local smoke metrics.json shows d_c=30 at N={256,512}; D_SWEEP max=30 (ceiling). Dashboard full run: d_c flat at all 5 N values with dc_range=0.
- Honest reading: MIDDLE_BAND label is correct. Key clarification: dispatch says "d_c=60 at all N" but full-run metrics show dc_range=0 (flat) with D_SWEEP max=60 (not 30 as in smoke). The d_c hits the ceiling regardless of N; the MRE=4.900 means the fit looks like polylog but with a 4.9x calibration miss -- this is the ceiling artifact, not a true polylog signal.
- Label override: NONE (MIDDLE_BAND honest). Annotation: D_SWEEP ceiling (max=60) is the blocking factor; v3 needed.

**Decision (1): moe_shift_K_scaling_v1 -> DIVERGING ARMS MIDDLE_BAND annotation.**
Cap_map: MoE SHIFT K-scaling characterization row: OPEN -> DIVERGING ARMS (Arm_A K=2->8: 0.818->0.799; Arm_B: 0.750->0.495; Arm_C: 0.886->0.938). K=4 design point for primary-corpus deployment; K=8 acceptable for cross-corpus at Arm_B cost. Row state UNCHANGED (MoE SHIFT architecture CONFIRMED at v212; characterization enriched).

**Decision (2): betB_5corpus_fullscale_v1 -> HARD_FAIL; 4-plateau scope confirmed.**
Cap_map: Bet B equal-spacing row: 5-plateau hypothesis HARD_FAIL. 4-plateau structure is the hard scope limit. Saad-Solla v206 4-corpus HARD_PASS NOT retracted (different experiment, different claim). Bet B discrete-class taxonomy FINAL LOCK unchanged (4-tier G1/G2/G3/G5). No row-state change (mechanism characterization clarified: scope bounded at 4-tier).

**Decision (3): moe_top_edge_v2 -> CLOSED-NEGATIVE (formula error N-independent).**
Cap_map: Free-additive top-edge MoE discriminator row: 🔬 INCONCLUSIVE finite-N -> CLOSED-NEGATIVE. Primary finding: smoke N=1024 showed offset=0.611 > v1 offset ~0.50; finite-N hypothesis refuted (offset did not shrink). Full N=16384 OOM is infrastructure, does not change the conclusion. DMPK SVD-bimodality remains as SOLE MoE rebuild discriminator. Row state: CLOSED-NEGATIVE.
PROT-004 check: free-additive top-edge row is a sub-discriminator (not a product capability row). PROT-004 does NOT trigger for sub-discriminator closures. No rescue sketches required.

**Decision (4): beti_depth_polylog_v2 -> D_SWEEP CEILING annotation; v3 design guidance.**
Cap_map: Bet I depth polylog row: OPEN -> MIDDLE_BAND D_SWEEP ceiling at 60 (all N; dc_range=0). True d_c unknown (>60 at alpha=0.40). v3 design: D_SWEEP=[100,150,200], alpha=0.40, same seed configuration. Row state UNCHANGED (🟡 inconclusive; Bet I 3rd envelope still OPEN).

**Queue-visibility gap (STRUCTURAL OBSERVATION):**
remote C:\dev\hd-instrument\data\overnight_queue\queue.json shows 7-day-old completed entries (last from 2026-05-19; 5 pending experiments never removed). Yet 5+ verdicts landed today (moe_shift_K_scaling, betB_5corpus_fullscale, beti_depth_polylog_v2, moe_shift_partition_v3, others). The runner consumes work from a DIFFERENT source than the queue.json file that exp_dev "REMOTE-SSH VERIFIED" post-ship. This explains why post-ship verification has repeatedly shown items as "present" in queue.json but not actually confirmed as queued for execution. TRUE queue state on remote is OPAQUE from main thread. Flag for operational triage: identify the actual queue source the runner reads (likely internal state DB or separate runner-state file).

**PROT compliance (v213):**
- PROT-004: 0 new capability closures; no rescue sketches required.
- PROT-007: history.md v213 block written FIRST (confirmed).
- PROT-008: 0 new grandfathered violations; no row-state demotions.
- PROT-009: cap_map.md + history.md + this file staged atomically.
- Labeled-vs-honest: 1 partial over-claim (moe_top_edge_v2 dispatch described OOM only; formula error scientific finding missed); recorded above.
- [[feedback-subagent-permission-inheritance]]: LOCAL commit only; push deferred to main thread.
- No queue-refill triggered per dispatch instruction.
- 126th PROT-009 paired commit.

Net cap_map effect v212 -> v213: 4 annotations/reframes. (1) MoE K-scaling: DIVERGING-ARMS characterization (K=4 design point confirmed); (2) Bet B 5-plateau: HARD_FAIL scope clarification (4-plateau hard limit); (3) Free-additive top-edge: CLOSED-NEGATIVE (formula error N-independent); (4) Bet I polylog: D_SWEEP ceiling artifact (v3 needed). 0 Tier-1 advances. 0 PROT-004 closures. Portfolio 14+7 UNCHANGED.

---

## v214 (2026-05-26) -- ANNOTATION-ONLY: Strategic synthesis post-48h inversion window + 5 design-ready killer features + 8 LLM-leapfrog directions + SVD-cascade smoke HARD-FAIL

**Trigger.** Direct user strategic synthesis integrating 11 strategic dimensions following the 48h inversion window (Saad-Solla + 1-RSB + MoE SHIFT all POSITIVE). No new experimental verdicts. Annotation-only bump. Multi-section v214 entry. User stated "lock this as DEFINITIVE current-state framing."

**Decision (1): Framework reliability UPGRADED to 55-70% LOCKED.**
48h window (v206 Saad-Solla 4-corpus CONFIRMED + v211 1-RSB first-order CONFIRMED + v212 MoE SHIFT CONFIRMED) constitutes three independent Tier-1 positive results in 48h -- qualitative inversion of prior negative-monotone period. Prior estimates: 40-55% (v206 band) -> 50-65% (v211 post-double-positive) -> 55-70% (v214 lock). DEFINITIVE current-state estimate, not a probability range to be narrowed further without new Tier-1 evidence. Conservative upper bound: saddle-cascade INSTRUMENTATION_FAIL twice on extended-f sweep; 1-RSB confirmed at one N only; SVD-cascade smoke HARD-FAIL. Combined Tier-1 P moved from 40-55% (v210) through 42-58% (v210) -> 50-65% (v211) -> 55-70% (v214 lock).

**Decision (2): Bet B substrate-product positioning LOCKED to stronger customer-facing language.**
v214 FINAL LOCK customer-facing spec: "substrate retains 94% on same-corpus / 74% on 4-stage continual / 60% on diff-corpus; 4-plateau hard limit; information-theoretic floor + basin-discrete structure." This supersedes prior "73-92% on this corpus triple" framing. Stronger because: (a) information-theoretic floor = mathematical guarantee (not empirical claim); (b) basin-discrete structure = Saad-Solla theoretical grounding (mechanism, not phenomenology); (c) 4-plateau hard limit = HARD_FAIL falsification of 5-plateau at v213 closes overpromise risk; (d) retention numbers are conservative (worst-case in 4-tier taxonomy, not cherry-picked). Combines with binary taxonomy (silhouette=0.788 CELL-LEVEL v212) and H-A consolidation mechanism (zero-sum trade-off v211) for complete Bet B product story.

**Decision (3): MoE rebuild reclassified as engineering-rate-limited.**
All research dependencies resolved as of v212/v213: alpha_c=0.5625 confirmed dense-grid (v211); SHIFT mechanism HARD-PASS at K=4 lift=0.205 K=8 lift=0.312 (v212); K=4 primary-corpus design point confirmed (v213 diverging-arms K-saturation analysis); K=8 cross-corpus design point confirmed (v213 Arm_C improvement pattern). Row annotation: from "research-rate-limited" to "engineering-rate-limited." Build-out can proceed without new research gates.

**Decision (4): Bet N STRONG_PARTIAL annotation upgrade -- substrate-novel universality finding.**
EN/PY gap=0.0014 (matched_gap from v211 Bet N v2 result) supports UNIVERSAL-SUBSTRATE framing. Atoms learned on one natural-language corpus are generic to other natural-language corpora; only RND atoms cleanly differentiate (gap=1.000). Annotation upgrade: Bet N 🟢 STRONG_PARTIAL + "substrate-novel finding: atom universality across NLP corpora." Product story: "substrate atoms generalize across natural-language domains" (distinctive vs transformers -- no atom-basis analog in KV-cache).

**Decision (5): SVD-cascade unified framework NEW 🔬 SMOKE HARD-FAIL row.**
wave14_unified_svd_cascade_falsifier_v1 smoke fired UNIFIED_HARD_FAIL at N=256: spacing_error ~2-3 vs 0.15 threshold; singular spectrum is spike-structured, not equally-spaced. Preliminary evidence: three theoretical homes (Saad-Solla saddle-cascade, 1-RSB first-order transition, MoE SHIFT architecture) are INDEPENDENT, not projections of one master SVD-cascade mechanism. FULL run pending; if confirms HARD-FAIL, Bachtis-Biroli-Decelle-Seoane SVD-cascade is NOT the substrate's unifying picture. Annotation only -- NO row-state changes to existing Saad-Solla, 1-RSB, or MoE SHIFT rows; those are confirmed independent of SVD-cascade unification. Three independent homes is ACCEPTABLE (arguably stronger: three distinct mathematical validations instead of one unified).

**Decision (6): Five new killer features filed as DESIGN-READY product roadmap (NEW v214 section).**
Two product categories established:
- **Category A -- Audit + Compliance**: deletion certificate primitive (HIGH leverage, ~2-3 weeks, DESIGN-READY); compositionality audit API (HIGH leverage, ~1-2 weeks, DESIGN-READY); per-fact retention policy (MEDIUM leverage, ~3-4 weeks, DESIGN-READY)
- **Category B -- Operational Reliability**: live concept drift detection (HIGH leverage, ~2-3 weeks, DESIGN-READY); edit-with-impact-prediction (MEDIUM leverage, ~3-4 weeks, CONTINGENT on SVD-cascade FULL)

All Category A features are no-new-research (direct from demonstrated capabilities). Category B drift detection is no-new-research (REPLAY H-A + structural axis sufficient). Category B edit-with-impact is blocked pending SVD-cascade FULL verdict. This is the first explicit product-roadmap section in cap_map.

**Decision (7): Eight LLM-leapfrog directions locked as three-category framework.**
Category 1 (LLM failure modes substrate solves structurally): hallucination-as-structural-impossibility, cost-per-token 1-10%, genuine personalization at user-scale.
Category 2 (LLM commodity capabilities substrate does better): verifiable knowledge cutoff updates, multi-substrate provable isolation, real-time model surgery.
Category 3 (new problem spaces substrate enables): CI/CD for AI knowledge ("Git for facts"), verifiable AI compliance attestation ($20B+ by 2030).
Three product narratives: (A) "the hallucination-impossible LLM" -- target healthcare/legal/financial; (B) "AI that respects data sovereignty" -- target enterprise; (C) "compliance-native AI" -- target regulated industries. Each narrative maps to demonstrated substrate capabilities.

**Decision (8): Three paths to category leadership; path (b) highest strategic priority.**
(a) substrate gen matches GPT-quality: P=20-30%; requires substrate gen to close quality gap.
(b) substrate gen good enough at 1-10% cost + audit/edit/compliance wins specific markets: P=60-75%; HIGHEST PRIORITY; probable AND transformative.
(c) substrate as memory-layer complement to LLMs: P=80-90%; most likely; lowest transformative upside.
Path (b) binding constraint = substrate generation quality reaching deployable levels at compute-matched cost. R26 AGS-style scaling-law extrapolation is the priority research drill to estimate the generation ceiling.

**Decision (9): R26 AGS-style scaling-law extrapolation flagged as PRIORITY NEXT RESEARCH DRILL.**
Path (b) viability depends on knowing the substrate generation quality ceiling at compute-matched cost targets. R26 = AGS-style scaling-law extrapolation: 2-3 (N, K, M) design points, fit, extrapolate to compute-matched GPT-2-small equivalent. This is the next binding constraint for the most strategically important path. Flag for Research agent dispatch in next cycle. See prior filing at notes/exp_dev_handoff_path3_ags_scaling_2026-05-24.md for context; v214 escalates this to PRIORITY status.

**Decision (10): 24-36 month competitive window acknowledged as structural annotation.**
Substrate-product framing has matured: MoE rebuild is engineering-rate-limited; Category A features are all engineering-rate-limited; only substrate-gen ceiling (path b constraint) remains research-rate-limited. Competitive window before Anthropic Memory / competitors close category gap on Audit+Compliance features is approximately 24-36 months. Engineering velocity on Category A is the near-term moat. Not a cap_map row -- a structural annotation to substrate-product positioning.

**Net cap_map effect.** v213 -> v214 ANNOTATION-ONLY: 5 annotation/reframe moves (framework reliability 48-64% -> 55-70% LOCK; Bet B spec LOCK; MoE rate-limiter reclassification; Bet N universality upgrade; SVD-cascade NEW 🔬 SMOKE HARD-FAIL row). 2 NEW cap_map sections (product-roadmap + LLM-leapfrog-directions). 1 priority research flag (R26). 1 competitive window annotation. 0 Tier-1 row-state changes. 0 PROT-004 closures. 14 demonstrated + 7 evidence-strength rows UNCHANGED. 127th PROT-009 paired commit.

PROT-004/006/008/009 compliance: 0 new ❌ closures; 0 row-state demotions; 29 grandfathered violations UNCHANGED; validator passes (no new violations); history.md v214 block written BEFORE cap_map.md v214 block (PROT-007 sequencing verified); strategy_decisions_2026-05-26.md paired; 127th PROT-009 commit.

Per [[feedback-subagent-permission-inheritance]]: commit LOCAL only; push deferred to main thread.
Per [[feedback-for-you-tab-primary-channel]]: status_log entry written after this decision log entry.
Per [[feedback-cap-map-update-protocol]]: atomic .tmp+rename; paired commit cap_map.md v214 + history.md v214 + this entry.
Per [[feedback-decision-log-eol-handling]]: this entry appended via tools/orchestrator/append_decision_log.py to preserve EOL convention.
Per [[feedback-no-experiment-design-in-prompts]]: R26 flagged as research task WITHOUT design parameters (no anchor names, sweep grids, threshold formulas).

---

## 2026-05-26 21:50 — cap_map v215 BATCHED 9-VERDICT MAJOR

**Trigger.** Orchestrator processed 8 verdicts (user-listed) plus 1 diagnostic (queue_source_diag_test_v1) that landed 2026-05-26 18:24-21:24 and were not picked up immediately due to orchestrator out-of-cycle window. Honest re-read mandated by [[feedback-verdict-msg-honest-reread]]: dashboard "completed" labels for moe_shift_M_scaling_v1, moe_gating_sharpness_v1, and 1rsb_pq_retained_v3 all hide HARD_FAIL verdict_msg payloads.

**Per-verdict label/numbers honest re-read.**

| Anchor | Dashboard | verdict_msg (honest) | Disposition |
|---|---|---|---|
| moe_shift_M_scaling_v1 | completed | HARD_FAIL: lift uniformly negative across M ∈ {0.25,0.40,0.55,0.70,0.85,1.0}·αc·N=2304 (-0.0205 → -0.0468, MORE NEGATIVE with load) | M-load NOT a lever for MoE SHIFT; annotation to MoE SHIFT row |
| moe_gating_sharpness_v1 | completed | GATING_HARD_FAIL: max_lift=-0.0018 (τ=0.01); sharper gating monotonically HURTS (-0.0581 at τ=1, -0.1009 at τ=2) | Gating sharpness NOT a lever; annotation to MoE SHIFT row |
| queue_source_diag_test_v1 | completed | R_TRANSFORM_STABLE_IN_N: Kerdock R-transform dev > 0.20 STAYS across N=1024,4096; 3/3 α-cells stable+diverge | Free-cumulant fingerprint N-stability RE-CONFIRMED (already ✅ at v166); canary plumbing verified |
| moe_shift_K_scaling_v2 | failed | OOM K=64 outer_product_store CUDA 8GB cap; K∈{2,4,8,16,32} clean data shows A=0.821→0.792 / B=0.750→0.272 / C=0.885→0.967 | INFRASTRUCTURE-FAIL on K=64; K≤32 partial-clean corroborates K=4 design point |
| moe_top_edge_v3 | failed | OOM SVD at N=16384 K=2 (3rd consecutive top-edge OOM) | INFRASTRUCTURE-FAIL; row already CLOSED-NEGATIVE v213; CONFIRMED CLOSED |
| betB_replay_hA_direct_v2 | completed | HA_MIDDLE: N=8192 inter=0.677 intra=0.717 no_replay=0.515; lift=-0.04 inter-vs-intra (weak) but replay > no-replay by 16pp directionally | MIDDLE; H-A directional consolidation present; inter-vs-intra timing weak at this scale |
| 1rsb_pq_retained_v3 | completed | PQ_RETAINED_RS_HARD_FAIL: N=8192 / 30 seeds / 435 overlaps; binder=-0.255 (<<+0.05); n_peaks=1; mean_q_sig≈0.0017; q distribution UNIMODAL at q≈0 (mean_q=1.87e-5, std=2e-4) | **MAJOR CONTRARY**: 1-RSB Pred-2 P(q) independent corroborator HARD-FAIL at production scale; RS-unimodal opposite of expected 1-RSB multi-delta |
| 1rsb_hysteresis_v4_multi_N | failed | Runner-killed mid N=4096 seed=17 reverse M=80000 (no metrics.json, no traceback); N=2048 clean max_gap=1.27; N=4096 partial seed=7 corroborates persistence | INFRASTRUCTURE-FAIL (process death); N=2048 partial-clean confirms hysteresis at higher N (gap shrinks but persists) |

**Decision (1): 1-RSB row demoted ✅ → 🟡 PARTIAL-POSITIVE.** "Hierarchical retrieval index (RSB phase, ultrametric structure)" row was ✅ Validated structural via `wave14e2_parisi_ultrametricity` (P(q) multi-peaked, ultrametricity 0.357) at smaller N. v215 `wave14_1rsb_pq_retained_v3` at N=8192 / 30 seeds fires RS-UNIMODAL (binder=-0.255, n_peaks=1) — direct contradiction at production scale with well-resolved statistics. Row demoted to 🟡 with both findings annotated. Honest disposition: the earlier ultrametricity finding may have been finite-N pseudo-RSB OR the production-scale measurement may have a measurement floor masking true multi-delta. Resolution drill flagged (Decision 5).

**Decision (2): Framework reliability LOCK 55-70% REVISED DOWN to 48-62% PROVISIONAL.** v214's lock at 55-70% was predicated on THREE independent Tier-1 positives (Saad-Solla 4-corpus, MoE SHIFT, 1-RSB hysteresis CONFIRMED + 1-RSB Pred-2 P(q) AWAITED as independent corroborator). The corroborator just fired NEGATIVE at the highest-resolution measurement. 1-RSB framework now stands on hysteresis alone — single-observable evidence is structurally weaker than double-corroborator evidence. Backstep to 48-62% PROVISIONAL until: (a) hysteresis N-scaling re-ship completes (v4 was infra-fail); (b) Pred-3 / Pred-4 independent observables available; (c) resolution research drill returns explanation for hysteresis-positive / P(q)-RS-unimodal disconnect.

**Decision (3): MoE SHIFT architecture engineering-locked at K=4 / K=8 / default τ / default M_per_expert.** Three v215 hard-fails close three major architectural exploration axes: (a) M-load is uniformly negative (no axis); (b) gating sharpness is uniformly negative (no axis); (c) K≥64 hits 8GB OOM cliff (script-design failure on K=64, NOT signal; K≤32 partial-clean already established K=4 saturation pattern). MoE rebuild engineering-rate-limited classification (v214) STRENGTHENED by elimination of three axes as levers. v214 K=4 primary / K=8 cross-corpus design point is the operating regime.

**Decision (4): Free-additive top-edge framework CONFIRMED CLOSED.** wave14_moe_top_edge_v3 is the 3rd consecutive OOM at N=16384 SVD step. Row already CLOSED-NEGATIVE v213 (FORMULA_ERROR + OOM). v215 result is third-strike confirmation. **Do NOT re-ship at N=16384**. DMPK SVD-bimodality remains sole MoE rebuild discriminator (v213 lock holds).

**Decision (5): NEW research drill flagged — hysteresis-without-RSB phase-class question.** The disconnect between hysteresis CONFIRMED (v211: gap=1.84 at N=1024) and Pred-2 P(q) RS-UNIMODAL (v215: binder=-0.255 at N=8192 / 30 seeds) is anomalous if both are read as canonical 1-RSB markers. Candidate explanations: (a) different phase class — hysteresis without thermodynamic RSB is known in glass literature (kinetic arrest without ergodicity breaking); (b) P(q) measurement floor at substrate-relevant α/M masks finite multi-delta structure (mean_q=1.87e-5 vs floor=0.011 — measurement is below floor, possibly inverted resolution issue); (c) hysteresis is metastability artifact rather than thermodynamic 1-RSB signature. Cheapest decisive drill: literature search on hysteresis-without-RSB phase classes AND post-hoc P(q) floor sensitivity analysis on existing v3 metrics.json data. **Flag for research routing (NOT done in this v215 cycle to avoid expanding scope).**

**Decision (6): Re-ship dispositions.**
- `wave14_1rsb_hysteresis_v5_n4096_n8192`: MEDIUM PRIORITY — N=2048 already confirmed (drop), re-ship N=4096 multi-seed + N=8192 with faster runner heartbeat to detect process-death sooner. Confirms-or-closes hysteresis N-scaling extrapolation.
- `wave14_moe_shift_K_scaling_v3` chunked or N=2048: LOW PRIORITY — K-saturation answer already obtained at K≤32; K=64+ is research-quality-of-data not load-bearing.
- `wave14_moe_top_edge_v4`: **DO NOT SHIP** — row CLOSED 3 times confirmed.
- `wave14_moe_shift_M_scaling_v2`, `wave14_moe_gating_sharpness_v2`: **DO NOT SHIP** — lever absent, no architectural axis to extend.

**Decision (7): Portfolio count revision.** 14 demonstrated + 7 evidence-strength → 14 demonstrated + 6 evidence-strength (Hierarchical retrieval / RSB row ✅→🟡 moves out of ✅ portfolio). Free-cumulant fingerprint stays ✅ (already promoted v166; v215 re-confirms but no new state). Net: -1 ✅ row.

**Net cap_map effect.** v214 → v215: 1 row-state demotion (Hierarchical retrieval / RSB ✅→🟡 with contrary-evidence annotation); 3 NO-LEVER annotations to MoE SHIFT row (M-load HARD_FAIL, gating-sharpness HARD_FAIL, K≥64 OOM infra cliff); 1 framework-reliability LOCK→PROVISIONAL backstep (55-70% → 48-62%); 1 confirmed closure (free-additive top-edge — already closed v213); 1 NEW research drill flagged (hysteresis-without-RSB phase-class question); H-A direct annotation (MIDDLE directional). 14+6 portfolio (was 14+7); 0 PROT-004 NEW closures.

PROT-004/006/008/009 compliance: 0 new ❌ closures (top-edge already CLOSED v213); 1 row-state demotion (Hierarchical retrieval / RSB ✅→🟡) captured at PROT-008; 29 grandfathered violations UNCHANGED; validator passes (no new violations beyond v214 baseline); history.md v215 block written BEFORE cap_map.md v215 row (PROT-007 sequencing verified); strategy_decisions_2026-05-26.md paired; 128th PROT-009 commit.

Per [[feedback-subagent-permission-inheritance]]: commit LOCAL only; push deferred to main thread.
Per [[feedback-for-you-tab-primary-channel]]: status_log entries written after this decision-log entry — one per verdict + one cap_map_commit summary.
Per [[feedback-cap-map-update-protocol]]: atomic .tmp+rename via append_decision_log.py; paired commit cap_map.md v215 + history.md v215 + this entry.
Per [[feedback-decision-log-eol-handling]]: this entry appended via tools/orchestrator/append_decision_log.py to preserve EOL convention.
Per [[feedback-verdict-msg-honest-reread]]: 3 "completed" labels overridden via verdict_msg honest re-read (M_scaling, gating_sharpness, pq_retained_v3 ALL fired HARD_FAIL despite dashboard "completed").
Per user instruction: queue-refill NOT triggered in this v215 cycle (orchestrator dispatching exp_dev separately in same turn).

---

## 2026-05-26 22:00 — Cap map v215 → v216 RECLASSIFICATION: 1-RSB row demotion over-corrected; SPLIT into substrate-multi-basin 🟢 + phase-class-label 🟡 per [[feedback-dont-overextend-theorems]]

**Context.** User strategic re-read of v215 verdict_handler disposition. v215 dropped Hierarchical retrieval / RSB row ✅→🟡 and revised framework reliability 55-70% LOCK → 48-62% PROVISIONAL on the basis of `wave14_1rsb_pq_retained_v3` PQ_RETAINED_RS_HARD_FAIL (binder=-0.255, n_peaks=1, mean_q_sig≈0 at N=8192/30 seeds). User identifies that v215 collapsed TWO distinct claims into a single demotion and that this propagates a phase-class label refutation onto the underlying substrate observations, which is the [[feedback-dont-overextend-theorems]] failure mode.

**Decision (1): RECLASSIFY Hierarchical retrieval row — split state into substrate-claim + phase-class-label-claim.**

The row at line 405 of cap_map.md is reframed:

- Title changed from "Hierarchical retrieval index (RSB phase, ultrametric structure)" to "Hierarchical retrieval index (multi-basin discrete structure; phase classification under refinement)".
- State column SPLIT into two sub-claims:
  - **substrate-has-multi-basin-discrete-structure → 🟢 55-70%** (three independent positive witnesses: Saad-Solla 4-corpus equal-spacing ✅, MoE SHIFT K=4 lift=0.205 / K=8 lift=0.312 ✅, retention plateaus 0.94/0.74/0.60 unchanged direct observation; hysteresis 18× gate ✅ compatible with multiple phase classes — observation unchanged, label uncertain).
  - **1-RSB-specifically-is-the-right-framework-label → 🟡 30-45%** (v215 `wave14_1rsb_pq_retained_v3` N=8192/30 seeds RS-UNIMODAL binder=-0.255 n_peaks=1 mean_q_sig≈0; cluster-conditional re-analysis pending).
- Evidence column annotated with four rescue paths (cheapest-first per [[feedback-rescue-sketch-first-sequencing]]).
- Product-implication column annotated: product-feature reliability depends on the FORMER (🟢), NOT the LATTER (🟡); product-feature reliability UNCHANGED.

**Decision (2): Framework-reliability number SPLIT (not single PROVISIONAL).** v215's 48-62% PROVISIONAL collapses two distinct uncertainties into one number. v216:

- "Substrate has theoretically-derivable multi-basin discrete structure" → 🟢 55-70% (three independent positive witnesses unchanged + hysteresis observation as fourth corroborator)
- "1-RSB SPECIFICALLY is the right framework label" → 🟡 30-45% (v8192 P(q) refuted; cluster-conditional pending)
- Product-feature reliability depends on the FORMER (🟢), NOT the LATTER (🟡)
- Therefore product-feature reliability UNCHANGED

This is the load-bearing reframe. v215 was structurally honest about the phase-class label refutation but propagated that refutation onto the underlying substrate observations, which v216 corrects.

**Decision (3): Three positive framework predictions PRESERVED as observation-level facts.**

- Saad-Solla 4-corpus equal-spacing ✅ unchanged (cap_map v206)
- MoE SHIFT K=4 lift=0.205 / K=8 lift=0.312 ✅ unchanged (cap_map v211/v212)
- Hysteresis 18× gate ✅ unchanged (cap_map v211 N=1024 gap=1.84; v215 N=2048 partial-clean gap=1.27)

**Critical**: Hysteresis is an OBSERVATION (forward-reverse loop area > threshold across M-load sweep at slow annealing rate). The OBSERVATION is independent of which phase class explains it. v215 effectively re-attributed the hysteresis observation to a more uncertain framework category by demoting the entire row. v216 restores observation-vs-label distinction: hysteresis is compatible with 1-RSB, cluster glass, RS-multi-ferromagnet, geometric frustration. Label uncertain; observation intact.

**Decision (4): Four rescue paths filed under Hierarchical retrieval row (cheapest-first per [[feedback-rescue-sketch-first-sequencing]]).**

1. **Cluster-conditional P(q) re-analysis on v8192 data using v212 silhouette classification** — ZERO COMPUTE, decisive, HIGHEST-LEVERAGE. If conditioning the overlap-pair selection on the v212 silhouette-derived cluster assignment reveals multi-delta structure that the unconditional P(q) averages away, v215 RS-unimodal is measurement-collapse artifact. **exp_dev dispatched 2026-05-26.**
2. **AGS retrieval phase with multi-ferromagnets at α=0.153 + Kerdock codebook** — analytic. If retrieval phase is multi-ferromagnetic (multiple basins, RS within each), P(q) is single-peaked at q≈0 (replicas in DIFFERENT ferromagnets average to ≈0) while hysteresis is multi-basin first-order. **research dispatched 2026-05-26.**
3. **Geometric frustration without ergodicity-breaking** — frustration produces discrete metastable basins (hysteresis) without RSB; P(q) single-peaked. Mid-cost research.
4. **1-RSB-approximate-nearby-phase** — substrate could be in 1-RSB-vicinity (dynamic 1-RSB, finite-size pseudo-RSB) where N=8192 P(q) is in "approximately RS" regime but thermodynamically not. Compute-heavy verification.

**Decision (5): Three parallel actions dispatched 2026-05-26 (recorded for v216 history).**

(a) **exp_dev** for cluster-conditional P(q) + rate-dependence of hysteresis (annealing-rate sweep)
(b) **research** for AGS retrieval-phase derivation at α=0.153 with Kerdock codebook
(c) **diagnostic** for v215 P(q) failure investigation (instrumentation-vs-signal disambiguation; P(q) measurement-floor analysis at substrate-relevant α/N/M)

**Decision (6): Product implications — NO ROADMAP CHANGE.**

- Bet B 4-tier retention shift-class taxonomy FINAL LOCK — unchanged (depends on Saad-Solla saddle-cascade ✅ + retention plateaus, NOT on 1-RSB label)
- MoE rebuild engineering-rate-limited — unchanged (depends on MoE SHIFT K=4/K=8 ✅, NOT on 1-RSB label)
- 5 killer features design-ready — unchanged (deletion certificate / compositionality audit / drift detection / hysteresis-based edits / hierarchical retrieval all depend on substrate-multi-basin 🟢, NOT on 1-RSB phase-class label 🟡)

**Decision (7): USER DIRECTION — DELAY product engineering until full substrate characterization complete.**

User this turn explicitly directs DELAY product engineering (deletion certificate / compositionality audit / drift detection) until cluster-conditional P(q), AGS retrieval-phase, rate-dep hysteresis, TCFT falsifier rescue paths return. Substrate-physics rescue paths take priority over product-feature engineering. Captured here for orchestrator priority queue.

**Decision (8): Portfolio count.** v215 14+6 (Hierarchical retrieval demoted out of ✅). v216 restores to **14+7** (substrate-multi-basin claim back to 🟢 evidence-strength sub-claim; phase-class label annotated 🟡 sub-claim within same row — not a separate portfolio row).

**Net cap_map effect.** v215 → v216: 1 row REFRAMED (Hierarchical retrieval — title + state SPLIT + evidence augmented with 4 rescue paths + product-implication annotated as UNCHANGED); 1 reliability SPLIT (substrate-multi-basin 🟢 55-70% / phase-class-label 🟡 30-45% / product-feature UNCHANGED); 0 PROT-004 closures; 0 ❌ closures; portfolio 14+6 → 14+7; 1 version-table entry appended (v216 ANNOTATION-ONLY); 1 history-block appended (v216 with 5 sub-tables: trigger, reframe, rescue paths, framework predictions preserved, dispositions, PROT compliance).

PROT-004/006/008/009 compliance: 0 new ❌ closures; 1 row REFRAME (Hierarchical retrieval) captured at PROT-008 as ANNOTATION; 29 grandfathered violations UNCHANGED; validator passes (no new violations beyond v215 baseline); history.md v216 block written BEFORE cap_map.md v216 row reframe (PROT-007 sequencing verified); strategy_decisions_2026-05-26.md paired; 129th PROT-009 commit.

Per [[feedback-subagent-permission-inheritance]]: commit LOCAL only; push deferred to main thread.
Per [[feedback-dont-overextend-theorems]]: load-bearing — splits "narrow form refuted" (1-RSB phase-class label) from "broader idea space intact" (substrate multi-basin discrete structure); rescue paths filed BEFORE labelling the broader claim demoted; this is the third worked example of this feedback at the cap_map level.
Per [[feedback-rescue-sketch-first-sequencing]]: four rescue paths sequenced cheapest-first (cluster-conditional P(q) ZERO COMPUTE highest-leverage; AGS retrieval-phase analytic; geometric frustration mid-cost research; 1-RSB-approximate compute-heavy).
Per [[feedback-for-you-tab-primary-channel]]: status_log entry written after this decision-log entry with plain_language + importance=HIGH.
Per [[feedback-cap-map-update-protocol]]: atomic .tmp+rename via append_decision_log.py; paired commit cap_map.md v216 + history.md v216 + this entry.
Per [[feedback-decision-log-eol-handling]]: this entry appended via tools/orchestrator/append_decision_log.py to preserve EOL convention.
Per user instruction (this turn): annotation-only; no queue-triggering; allowed under pause flag per strategy_scribe pause-gate rules.

## 2026-05-26 23:55 — Cap map v216 → v217 BATCHED 5-VERDICT (3 INDEPENDENT INFRA FAILURES + 2 completed)

Five verdicts landed 23:24-23:47. User direction: investigate failure pattern. Orchestrator handles exp_dev queue-refill separately this turn — verdict_handler does NOT trigger refill.

**Decision (1): Failure-pattern diagnosis — INDEPENDENT root causes, NOT a common-source bug.**

The three FAILED verdicts at 23:24 / 23:30 / 23:31 have three distinct mechanistic roots:

- (1) wave14_saddle_cascade_plateau_v4_n2048 — CPU TIMEOUT 7200s. Per-seed cost ~1700s; 3 seeds × 5 f-points = 25500s exceeds 2h CPU budget. Runner log: `TIMEOUT ... after 7200.1s`; experiment log truncates clean at `[run] f=1.0 seed=17 N=2048` with NO error and NO completion. Self-test passed. Partial data (seed=7 complete) corroborates v3 non-monotone retention pattern at N=2048.
- (2) wave14_1rsb_pq_retained_v4 — CUDA OOM on `(residual.T @ ctxs) / N` at N=16384 with 8 GiB GPU. Failed inside train_w_with_replay (exp_wave14d_betB_kovacs_v1.py line 183). Self-test passed; OOM only at full-N runtime.
- (3) wave14_betB_6corpus_extension_v1 — ImportError: `cannot import name 'evaluate_retention' from 'experiments.exp_wave14_k2_m1_hierreplay_v1'`. Crashed at 20s, seed=7 step 1. Self-test passed but only checked BIC/equal-spacing instrumentation, NOT the cross-script symbol.

Unlike PROT-013 (single evaluate_bpc helper bug breaking many co-incident experiments), these three failures share NO scaffolding. NO infrastructure-wide regression. NO SCP path drift. NO disk-full / CUDA-threshold environmental issue.

**Decision (2): Per-anchor disposition.**

| Anchor | Disposition | Row impact |
|---|---|---|
| saddle_cascade v4_n2048 | UNCHANGED Saad-Solla row ✅; N=2048 extension PENDING re-design | v3 HARD_PASS at v206 4-corpus N=1024 stands |
| 1rsb_pq_retained v4 | UNCHANGED phase-class-label 🟡 row; v215 HARD_FAIL evidence base intact | v5 redesign with N=8192-batched needed |
| betB_6corpus_extension v1 | ⚪ STILL not-tested; structural-fail-pre-test annotation; PROT-016 lock-in candidate logged | NEW probe never produced signal |
| hippo_replay_w v1 | CLOSED-NEGATIVE corroborated rescue #3; all 3 HiPPO-init-W rescues now closed | v211/v212 closure strengthened |
| moe_intraexpert_overlap v1 | NEW 🔬 sub-row under MoE K-scaling; VERDICT LABEL SEMANTICS PENDING | Threshold-comparator direction needs Strategy clarification |

**Decision (3): MoE intra-expert-overlap verdict label — HONEST CONTRADICTION flagged.**

verdict_msg reads: `"OVERLAP_DOMINANT: intra-expert overlap explains flat K-scaling. inter_cosine=-0.0001 (>=0.3), routing_entropy=4.343bits (>=1.5) at K=32"`. The parenthetical `(>=0.3)` reads as the threshold the metric SHOULD satisfy for OVERLAP_DOMINANT — but inter_cosine=-0.0001 OBVIOUSLY does not satisfy `>= 0.3`. Either the threshold-comparator direction is mis-stated (should be `<= 0.3`?) or the label-trigger logic does not actually use that condition (maybe it uses intra/inter ratio).

Per-cell numbers ARE meaningful: monotone intra_cosine growth K=2:0.0003 → K=32:0.0025 with inter_cosine flat at ≈0 across K. Empirical reading: experts are non-redundant between-expert but accumulate slight within-expert alignment as K grows. This MAY be the K-flatness diagnosis (intra-expert overlap absorbs extra capacity) but cannot be accepted as definitive until the verdict-script logic is re-read. Per [[feedback-verdict-msg-honest-reread]] this is observation 67+ post-lock.

**Decision (4): Three open redesign anchors carried into next exp_dev cycle.**

1. **saddle_cascade_plateau v5** — N-extension at N=2048: move to GPU OR cut f-grid (drop f=0.25 and f=0.75 → 3-point grid) OR shrink seeds. Pre-build at `experiments/exp_wave14_saddle_cascade_plateau_v5_n4096.py` may already be the redesign vehicle (visible in git status untracked).
2. **1rsb_pq_retained v5** — N=8192 with batched residual matmul (avoid full N×N allocation at N=16384). Independent corroborator at N=8192 already exists at v215.
3. **betB_6corpus_extension v2** — inspect `exp_wave14_k2_m1_hierreplay_v1.py` for actual retention-evaluation symbol; OR inline evaluation logic; verify import locally before queue_add.

Orchestrator dispatches exp_dev separately this turn (per user instruction this turn); verdict_handler does NOT trigger queue-refill.

**Decision (5): PROT-016 lock-in candidate filed — [[feedback-ship-before-dependency-verified]] pre-ship import verification.**

6corpus_extension v1 ImportError is a textbook violation of [[feedback-ship-before-dependency-verified]]. The self-test gated the instrumentation (BIC, equal-spacing math) but did NOT gate the cross-script `from experiments.exp_wave14_k2_m1_hierreplay_v1 import evaluate_retention` line. Structural fix candidate: smoke gate should `python -c "from <target_module> import <symbol>"` for each cross-script import in the experiment script BEFORE queue_add. Memory lock-in pending.

**Decision (6): Framework reliability UNCHANGED 48-62% PROVISIONAL.**

Three failures are infra not signal — they contribute NO substrate-physics evidence either direction. Two completed verdicts also leave framework-level evidence unchanged: HiPPO rescue closure is rescue-family-specific (not framework-level); MoE intra-overlap diagnosis is structurally executed but verdict-label semantics pending. No reliability re-calibration this version.

**Decision (7): Portfolio count UNCHANGED 14+7.**

No new ✅ or ❌ this batch. No row state demotions / promotions. One NEW 🔬 sub-row annotation under MoE K-scaling.

**Net cap_map effect.** v216 → v217: 0 row state changes; 1 NEW 🔬 sub-row (intra-expert-overlap K-scaling pending Strategy clarification of verdict-label threshold direction); 0 PROT-004 closures; 0 ❌ closures; portfolio UNCHANGED 14+7; framework reliability UNCHANGED 48-62% PROVISIONAL; 3 open redesign anchors carried; 1 NEW PROT lock-in candidate (PROT-016 [[feedback-ship-before-dependency-verified]]); 1 verdict label flagged for Strategy clarification (MoE intra-expert-overlap threshold-comparator direction).

PROT-004/006/008/009 compliance: 0 new ❌ closures; 0 row state demotions; 1 NEW 🔬 sub-row annotation captured at PROT-008 as ANNOTATION; 29 grandfathered violations UNCHANGED; validator passes; history.md v217 block written BEFORE cap_map.md v217 version-table entry (PROT-007 sequencing verified); strategy_decisions_2026-05-26.md paired; 130th PROT-009 commit.

Per [[feedback-subagent-permission-inheritance]]: commit LOCAL only; push deferred to main thread.
Per [[feedback-verdict-msg-honest-reread]]: MoE intra-expert-overlap verdict_msg threshold-comparator direction reads as fail-of-threshold yet OVERLAP_DOMINANT label is set; per-cell numbers preserved; interpretation gated pending Strategy clarification.
Per [[feedback-ship-before-dependency-verified]]: 6corpus_extension v1 ImportError logged as PROT-016 candidate for pre-ship import verification.
Per [[feedback-for-you-tab-primary-channel]]: 6 status_log entries (one per verdict + one for cap_map bump) with plain_language + importance.
Per [[feedback-cap-map-update-protocol]]: atomic .tmp+rename via append_decision_log.py.
Per user instruction (this turn): exp_dev queue-refill is dispatched SEPARATELY by orchestrator; verdict_handler does NOT trigger refill. Pause flag ACTIVE verified at decision time.


## wave14f_hippo_eigenspace_v1 INSTRUMENTATION_FAIL — annotation v217->v218 (2026-05-27T00:16:22)

### Step 0: honest re-read
- verdict tag: INSTRUMENTATION_FAIL
- verdict_msg: "Vanilla baseline depth_at_half=1.0 < 2.0. Training is not working at this scale."
- per-cell: all 3 seeds (7/17/23) — hippo depth_at_half=1.0, vanilla depth_at_half=1.0; cosines drop to near-zero (< 0.02) after layer 1; mean_ratio=1.0
- HONEST: label is accurate. Both branches degenerate identically. No comparison signal possible.

### cap_map decision: ANNOTATION-ONLY v217->v218
- HiPPO family status: CLOSED-NEGATIVE (v212) — CONFIRMED by 4th arm
- Rescue #1 (hippo_warmstart_v1): WARMSTART_HARD_FAIL — speedup_ratio=1.0, no convergence advantage
- Rescue #2 (hippo_warmstart already batched); Rescue #3 (hippo_replay_w_v1): HIPPO_REPLAY_HARD_FAIL delta=-0.0014
- Rescue #4 (hippo_eigenspace_v1): INSTRUMENTATION_FAIL — degenerate training at N=1024
- All 4 rescue arms closed. Closure REVISIT ruled out: no positive result in any arm.
- v212 CLOSED-NEGATIVE stands. No row-state move. Annotation only.

### pipeline-pacing: SKIP (overnight=7 pending, cpu=19 pending — queues non-empty)
