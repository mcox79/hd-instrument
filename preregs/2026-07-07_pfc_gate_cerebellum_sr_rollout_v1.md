# Pre-reg: pfc_gate_cerebellum_sr_rollout_v1

Author: exp_dev (Sonnet 5, agent-spawn) 2026-07-07
Cell: `experiments/exp_pfc_gate_cerebellum_sr_rollout_v1.py`
Anchor: `pfc_gate_cerebellum_sr_rollout_v1` (smoke: `_smoke`)

## Prior-work check (USER-locked concept-query-before-authoring, 2026-07-01)
`bash tools/substrate_query.sh "cerebellar forward model anticipatory rollout successor
representation gate correction predictive"` -> top hit cosine=0.3643
(`notes/research_gap1_multihop_5x_drill_2026-06-26.md` N3 "CEREBELLAR FORWARD-MODEL
CORRECTION"), second hit cosine=0.3564/0.3525 (Wolpert MOSAIC,
`notes/research_drill_realtime_multimodal_biology_3x_2026-06-09.md`), third cosine=0.3262
(`notes/research_brain_drill_3_multihop_reasoning_5x_DEEPER_2026-06-22.md` Stream H).
Both top hits READ. **Verdict: related-but-distinct, NOT a rediscovery.**
- N3 (2026-06-26) proposed a *SUPERVISED* forward-model F trained on (state,action)->next-state,
  used as a disagreement-threshold COMPARATOR that triggers discrete re-cleanup/rollback.
  P_deflated=0.30, never built (confirmed: no `exp_*forward_model*`/`exp_*cerebell*` cell on
  disk implements it; only `exp_substrate_cerebellar_random_expansion_write_v1.py` exists,
  a granule-cell-expansion-coding mechanism, unrelated).
- Stream H (2026-06-22) explicitly DEFERRED cerebellum: "cerebellar refinement is the
  SUPERVISED error signal (climbing fiber) -- substrate doesn't have ground truth per hop...
  NOT immediately substrate-applicable."
- THIS cell's mechanism resolves that exact blocker: it reuses the ALREADY-TRAINED
  `train_sr_transport` M (TD-bootstrap on rollout transitions, unsupervised, verbatim from
  `exp_pfc_gate_cfrpe_trained_v2.py`/`exp_pfc_gate_cfrpe_deeper_regime_v1.py` -- itself
  descended from the 2026-06-26 drill's OWN accepted primitive "Successor-W closure
  M=sum gamma^k W^k"), NOT a new supervised comparator. The score-bias (anticipatory) /
  state-projection (reactive) formulation is also structurally different from N3's
  disagreement-threshold rollback. This is the FIRST actual build/test of any
  cerebellar-forward-model variant in this program; genuinely novel per the drill's own
  external lit-scan (no direct precedent for anticipatory-rollout on a gating policy's
  horizon-degradation specifically).

## Question
Per `notes/research_brain_component_consumer_ranking_cerebellum_control_depth_2026-07-07.md`
(the brain-component-driven-development drill's TOP PICK, "prove a consumer BEFORE building"):
does a cerebellar-style anticipatory forward-model (SR-rollout bias at decision time) recover
a material fraction of the PFC-BG gate's measured depth-4-to-depth-6 collapse, and does the
recovery depend specifically on the ANTICIPATORY (before-commit) property vs a generic
after-the-fact correction?

CONSUMER (MEASURED@data/exp_pfc_gate_cfrpe_trained_v2/metrics.json): HARD_PASS at fair
depth-4 (V1200_d4: gonogo_lift=0.600, closure=0.661) DEGRADING at depth
(V800_d4:0.603->V800_d5:0.301->; V1200_d4:0.600->V1200_d5:0.281->; V2400_d4:0.468->
V2400_d5:0.204->V2400_d6:0.068). A prior smoke (MEASURED@
data/exp_pfc_gate_cfrpe_deeper_regime_v1_smoke/metrics.json) tested WIDENING the SR horizon
(higher gamma) and found `horizon_attributable=-0.008` -- NOT the lever. This cell tests a
DIFFERENT lever (multi-hop-ahead SR-rollout informing the gate's argmax) at FIXED gamma=0.85
(the horizon axis is NOT re-tested here; it is held constant to avoid conflating the two
levers).

## Design (3-arm smoke per the drill's spec; reuses train_sr_transport verbatim, NO new
representational machinery -- the only new primitive is `rollout_forward`, a thin composition
of the EXISTING `cleanup_batched` applied K times through the EXISTING M)
Fixed gamma=0.85 (BASELINE_GAMMA, unchanged from v2). One SR matrix M trained per (V,n_ops)
group via `train_sr_transport` (untouched). `rollout_forward(state, M, E, k)`: forward-simulate
k virtual hops (`state @ M` then `cleanup_batched` back onto the codebook manifold, repeated k
times) -- a genuine multi-step lookahead ("hypothesized future state"), distinct from the
existing one-step `reach_value(cleaned, goal, M)` read. K_ROLLOUT=2 fixed a priori
(HYPOTHESIZED@"multi-hop-ahead" framing in the drill note; NOT tuned against the outcome, to
avoid p-hacking -- calibration_check=default_ok_for_this_regime).

## Arms (paired; share E, W_ops, M, and the SAME test chains per (regime,seed))
- `v1_no_goal`, `additive_baseline` (SR-independent; alpha tuned on train),
  `cfrpe_control_identity` (identity-reach anti-tautology foil), `oracle` (ceiling) --
  same 4 baselines as v2/deeper_regime, reused verbatim for headroom/closure scaffolding.
- `no_correction` -- the EXISTING mechanism (one-step SR reach via M, `mode="gonogo"`,
  identical formula to v2/deeper_regime's `gonogo_g0.85`). Measured FRESH in this same run
  (paired, not cited from the other disk artifact) per PAIRED-TRIALS-MANDATORY (USER-locked
  2026-07-04) -- doubles as a Gate-D positive-control reproduction of the known decay.
- `feedback_only_reactive` -- decision uses the ADDITIVE score ONLY (no SR signal at
  decision time, identical selection rule to additive_baseline); AFTER the hop commits, apply
  `rollout_forward` (K=2) to the landed state as a POST-HOC correction/denoiser feeding the
  next hop (and the final correctness check). Isolates "does ANY correction help" from
  anticipation specifically.
- `gonogo_sr_rollout_anticipatory` -- for EACH candidate op, compute the K-step
  `rollout_forward`-projected future state BEFORE choosing, score
  `w_manifold*manifold + alpha*goal_sim + w_reach*cos(rolled_candidate, goal)`, argmax over
  that anticipatory score. State fed to the next hop is the RAW (uncorrected) chosen
  candidate -- isolates the DECISION-TIME-BIAS property from post-hoc correction.

## Discriminators
PRIMARY (matched-group, best-controlled): op4_V300 group (smoke) / op4_V1200 group (FULL),
SAME V and n_ops, ONLY depth differs (d4 vs d6):
```
d4_lift[arm] = score[arm]@d4 - additive@d4
d6_lift[arm] = score[arm]@d6 - additive@d6
gap = d4_lift[no_correction] - d6_lift[no_correction]          (the measured collapse, IN THIS RUN)
recovered_frac[arm] = (d6_lift[arm] - d6_lift[no_correction]) / gap
anticipatory_minus_reactive_d6 = d6_lift[gonogo_sr_rollout_anticipatory] - d6_lift[feedback_only_reactive]
```
SECONDARY (reporting only, not gating): the FAIR in-band d6 regime (op2_V300_d6 / op2_*_d6 in
FULL), absolute `closure[arm] = (score[arm]-additive)/headroom` per arm, for context.
MECHANISM-FIRES (Discipline Pattern #2): `rollout_reach_rank_acc` -- along the TRUE trajectory,
does argmax_op(K-step-rollout reach) == true op? (chance=1/n_ops). Must exceed chance+0.05 at
d4 or the whole smoke is testing a non-informative signal.

## PASS / FAIL bands
**REFINEMENT FLAG (per contract: "refine only if mis-specified, and say so"):** the drill's
literal band text anchors to the FULL-scale V1200_d4/V2400_d6 ABSOLUTE numbers
(`d6 lift >= 0.075 + 0.40*(0.653-0.075) = 0.306`). This smoke runs at a DIFFERENT scale
(N=2048/V=300 vs N=8192/V=1200-2400) where absolute lift values do not transfer (deeper_regime's
own prereg documents this: "at N=2048 the reach signal is cleanup-noise limited... may be
MASKED at smoke scale"). Refined to a RELATIVE form using THIS run's OWN paired
same-V/same-n_ops d4-vs-d6 measurement (op4 group, better-controlled than the original
cross-V V1200-vs-V2400 comparison), preserving the drill's exact percentages/margins:
- **HARD_PASS:** gap > 0.02 (collapse reproduced) AND `recovered_frac[anticipatory] >= 0.40`
  AND `anticipatory_minus_reactive_d6 >= 0.10` AND `cv[anticipatory@d6] < 0.15` AND
  `oracle@d6 >= 0.90` AND mechanism-fires AND no arms-differ collision.
- **HARD_FAIL_NO_CEREBELLAR_CONSUMER:** `recovered_frac[anticipatory] <= 0.05` (no material
  lift) OR `anticipatory_minus_reactive_d6 <= 0.0` (doesn't beat reactive -- the
  feedforward-specific story is wrong, a generic denoiser would do the same job) OR
  `cv[anticipatory@d6] >= 0.25` (unstable, not a real effect).
- **MIDDLE_BAND_PARTIAL_RECOVERY:** real lift over no_correction (>0.05) but
  `recovered_frac < 0.40`, or between the HF/HP margins on anticipatory-vs-reactive.
- **MIDDLE_BAND_MECHANISM_DOES_NOT_FIRE:** rollout_reach_rank_acc <= chance+0.05 at d4 (the
  whole 3-arm comparison is untrustworthy; regime needs a nudge, not a verdict).
- **INCONCLUSIVE_GAP_TOO_SMALL_TO_MEASURE:** gap <= 0.02 at this scale (regime-miss, not
  structural; report mechanism signals regardless).

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = n_arms(7) * n_seeds * n_regimes (smoke: 7*3*3=63; FULL:
  7*5*6=210).
- arms_differ_verified: op-trace hash pairwise among {no_correction, gonogo_sr_rollout_
  anticipatory, feedback_only_reactive, additive_baseline}, exempt when the relevant tuned
  w_reach==0 (legitimate reduction).
- final_metrics_atomicity: tmp_replace (os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException). Grep-gate: PASS
  (verified before dispatch).
- baseline_in_band (META_RULE_AG): reused verbatim from deeper_regime's own smoke measurement
  (op2_V300_d6 additive=0.118 FAIR; op4_V300_d6 additive=0.007 unfair/floored) -- same grid,
  same expected in-band structure.
- calibration_check: default_ok_for_this_regime. K_ROLLOUT=2 fixed a priori (not tuned against
  outcome); w_reach tuned on TRAIN only (standard convention, matches v2/deeper_regime).
- crlb_n/a: accuracy-closure has no single closed-form noise floor; reachability by feasibility
  (v2 measured closure=0.66 at fair d4; the gap being tested is itself measured in-run).
- effective_vs_nominal (Gate A): K_ROLLOUT directly parametrizes `rollout_forward`; gamma fixed
  (not swept, avoiding conflation with the already-tested-and-rejected horizon lever).
  sweep_alignment_verdict: ALIGNED (no sweep axis this cell besides seed/regime).
- positive_control (Gate D): `no_correction` arm at op4_V300_d4/d6 reproduces
  deeper_regime's own `gonogo_g0.85` measurement at the SAME regime (tolerance 0.10) --
  in-run reproduction, not cross-scale citation.
- discriminating_fraction (Gate B): 3-regime grid spans floored (op4_d6, diagnosis) and
  in-band (op2_d6, FAIR) -- matches deeper_regime's own design, >= 30% of grid discriminating.
- functional_requirements: (1) per-hop op-selection toward a distant goal -> SR reach value
  (existing); (2) extend the reach signal beyond one-step -> K-step rollout (NEW, this cell); (3)
  isolate anticipation from generic correction -> before-commit vs after-commit ablation (NEW).
  All map to existing primitives (`cleanup_batched`, `train_sr_transport`) recomposed, no new
  representational machinery.
- defensive_error_checking: passed_all_4 (start_marker, crash_diagnostic, heartbeat, chunked
  via `resumable_seeds` per-seed partial + fatal-flag).
- progress_logging: print_flush_true (line-buffered + flush per line + per-seed heartbeat).
  FULL timeout_s >= 1800 -> heartbeat mandatory.

## Compute architecture
(a) batched-GPU-capable, CPU-first for smoke (per RESOURCE RULES: remote compute only for
FULLs; local only for quick smokes). SR-TD training (1 gamma), operator application, cleanup,
rollout are batched matmuls, device-agnostic (cuda-if-available, defaults cpu). Chains batched;
within-chain hops sequential (genuine dependency); rollout's K virtual hops are ALSO genuinely
sequential (each step depends on the previous cleanup). Storage: sharded (each op its own W;
M a learned value operator, not an item store). No bundled store.

## Discriminator-survives-scale (option C, same as deeper_regime precedent)
Smoke reuses deeper_regime's EXACT matched-N/V discriminator-preview grid (N=2048, V=300,
depths {4,6}). Caveat carried forward: at N=2048 the underlying reach signal is
cleanup-noise-limited (deeper_regime's own reach_rank ~0.40-0.45 at n_ops=4 vs 0.69 at
N=8192) -- if the anticipatory mechanism is genuinely noise-limited at THIS scale but would
resolve at N=8192, smoke could under-read the true effect. This is flagged honestly, not
smoothed over: a MIDDLE_BAND or borderline HARD_FAIL at smoke scale is not dispositive against
FULL if the mechanism-fires check and reach_rank trend look promising -- but per contract, do
NOT force a pass on a P~0.25 test; an honest borderline result routes to a scoped FULL
follow-up only if the smoke shows a genuinely trending recovered_frac, not a coin-flip.

## Smoke config
N=2048, seeds=[7,17,23], regimes={op4_V300_d4, op4_V300_d6, op2_V300_d6} (IDENTICAL to
deeper_regime's own smoke grid), SR_STEPS=300, SR_BATCH=64, n_train=48, n_test=48,
rollout_per_V=8, gamma=0.85 fixed, K_ROLLOUT=2 fixed. Expect wall time comparable to
deeper_regime's own smoke (136s on CPU with 2 gammas trained); this cell trains only 1 gamma
per group but adds rollout overhead on 2 new arms -- expect a similar order of magnitude,
verified empirically before any dispatch.

## FULL config (staged pending smoke clearing >= MIDDLE_BAND; do NOT self-dispatch below
MIDDLE_BAND)
N=8192, seeds=[7,17,23,31,41], regimes={op4_V1200_d4, op4_V1200_d6, op2_V800_d4, op2_V800_d6,
op2_V1200_d4, op2_V1200_d6} (IDENTICAL grid to deeper_regime's own staged FULL config),
SR_STEPS=8000, SR_BATCH=256, n_train=300, n_test=240, rollout_per_V=50, gamma=0.85 fixed (no
sweep -- cheaper than deeper_regime's 3-gamma FULL by construction), K_ROLLOUT=2 fixed.
EXPECTED_N_UNITS=7*5*6=210. Recommended queue: remote_cpu_queue (CPU-batched matmuls; no CUDA
kernel dependency introduced by rollout_forward beyond what v2/deeper_regime already use).
Recommended --timeout: computed from measured smoke wall time (see completion report),
formula ceil(1.5 * smoke_wall_s * (8192/2048)^1.5 * (5/3)), capped at 14400s or justified.
