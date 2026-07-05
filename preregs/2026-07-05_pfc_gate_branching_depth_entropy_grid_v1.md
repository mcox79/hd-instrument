# Pre-reg: pfc_gate_branching_depth_entropy_grid_v1

Author: exp_dev (Opus 4.8 1M, agent-spawn) 2026-07-05
Cell: `experiments/exp_pfc_gate_branching_depth_entropy_grid_v1.py`
Anchor: `pfc_gate_branching_depth_entropy_grid_v1`  (smoke: `_smoke`)

## Question
Control's flat cf-RPE Go/NoGo gate is PROVEN at depth-4 (v2 FULL V1200_d4 closure=0.661) but
COLLAPSES to gonogo=0.075 (closure=0.073) at depth-6. The deeper-regime cell's OWN smoke
showed the collapse is a BRANCHING-factor problem, NOT a memory-horizon problem: SR-horizon
gamma is bit-identical d6 (op4 gonogo g0.85 == g0.95 = 0.104) while lowering branching n_ops
4->2 triples closure. Does a HIERARCHICAL-OPTIONS gate -- decomposing the deep/high-branching
decision into low-horizon sub-goals -- RECOVER the flat depth-6 collapse, and does the benefit
track decision-entropy (log2(n_ops)*depth) across an n_ops x depth grid?

MEASURED@data/exp_pfc_gate_cfrpe_deeper_regime_v1_smoke/metrics.json (N=2048):
- op4_V300_d6 gonogo g0.85 = 0.10417 == g0.95 = 0.10417 (gamma inert; horizon_is_the_lever=False)
- op2_V300_d6 gonogo = 0.389 (branching 4->2 -> ~3.7x closure)
MEASURED@data/exp_pfc_gate_cfrpe_trained_v2/metrics.json: flat gate d4 closure=0.661; d6 collapse.

## Mechanism (TESTED, not assumed): hierarchical-options gate
Decompose a depth-d op-chain into ceil(d/SEG_LEN) segments (SEG_LEN=2). At each segment boundary
re-anchor the goal to the NEXT sub-goal (waypoint) instead of the far final goal; within a segment
run the SAME flat Go/NoGo gate toward a target <= SEG_LEN hops away, where the trained SR reach is
accurate. This bounds the per-decision REACH HORIZON to SEG_LEN WITHOUT touching gamma (smoke
showed extending M's horizon fails -- M cannot represent 6-hop-distant successor features; but
re-anchoring to a NEAR waypoint keeps every reach evaluation in M's accurate short range).
Brain-grounded: CITED@Sutton-Precup-Singh 1999 (options/SMDP temporal abstraction);
Botvinick-Niv-Barto 2009 (HRL); Frank-Badre corticostriatal HRL; Redgrave-Prescott-Gurney 1999 +
Hick 1952 + Usher-McClelland 2001 (branching/decision-entropy). Prior-work check: substrate-KB
concept query top hits cosine 0.327 ("Option C hierarchical decomposition stack" = pattern
encoding, unrelated) and 0.313 (hierarchical-PLANNING revival = symbolic BlocksWorld, different
substrate primitives). This is the FIRST hierarchical-options gate on the cf-RPE Go/NoGo control
harness -- genuinely novel in this lineage (not a rediscovery).

SUB-GOAL SOURCE (declared oracle-assist, honestly scoped): the waypoint STATES at segment
boundaries are the true intermediate states of the chain (an assumed-optimal top-level option
policy). The arm is NOT handed the OPS -- it must still SELECT ops via the gate. The scientific
claim is therefore SCOPED: "GIVEN a correct sub-goal decomposition, does per-segment low-horizon
gating recover the flat collapse?" Autonomous waypoint DISCOVERY is an explicit FOLLOW-ON, not
claimed here. Two rails keep it honest: (1) hier_shuffled negative control (identical structure,
WRONG other-chain waypoints); HP requires hier_options >> hier_shuffled so the CORRECT decomposition
is load-bearing (not "extra reach score"); (2) reach_tcos_corr < 0.85 (reach is dynamics, not
target-cosine).

## Arms (paired; share E, W_ops, M, and the SAME test chains per (regime,seed))
v1_no_goal | additive_baseline (fair-regime labeler) | flat_control_identity (identity-reach foil) |
oracle (ceiling) | flat_gonogo (FLAT SR gate toward final goal -- COLLAPSES) | hier_options (the
fix) | hier_shuffled (wrong-waypoint neg control).

## Grid + discriminators
GRID: n_ops {2,3,4} (branching) x depth {4,6,8} (depth) at FIXED gamma=0.85 (smoke proved inert).
entropy = log2(n_ops)*depth. Per regime (FLAT-referenced so it survives additive-floor at op4_d6):
  headroom_flat = oracle - flat_gonogo; hier_closure = (hier - flat)/headroom_flat;
  hier_lift = hier - flat; shuf_gap = hier - shuffled.
FOCUS = highest-entropy regime with oracle>=0.90 AND headroom_flat>=0.10 (the high-branching deep
regime where flat collapses; op4_d6 in smoke, highest-entropy oracle-ok cell in full).

## PASS / FAIL bands (envelope-fail-bands; META_RULE_L strict floor)
- HARD_PASS: at the FOCUS regime, hier_closure >= 0.25 AND hier_lift > 0.05 AND shuf_gap > 0.10
  (hier > shuffled) AND reach_tcos_corr < 0.85 AND sign_p(hier vs flat) < 0.05 AND
  reach_rank > 1/n_ops + 0.05 AND oracle >= 0.90 AND cv(hier) < 0.10 (FULL only) AND no
  af_collision. => hierarchical decomposition extends control past the flat depth-6 collapse.
- HARD_FAIL_HIERARCHY_NOT_THE_LEVER: at focus, hier_lift <= 0.05 (hierarchy does not beat flat)
  OR shuf_gap <= 0.05 (correct decomposition adds nothing beyond arbitrary waypoint bias).
- MIDDLE_BAND_*: hierarchy helps (hier_lift>0.05) but hier_closure in [0.05,0.25), or clears 25%
  but shuf_gap/cv/sign/anti-tautology fails.
- INCONCLUSIVE_NO_DISCRIMINATING_REGIME: no regime with oracle>=0.90 AND headroom_flat>=0.10.
Reported regardless: full entropy surface (FLAT/HIER/lift/closure per n_ops,depth,entropy);
spearman(hier_lift, entropy); spearman(flat, -entropy) vs spearman(flat, -depth) (does entropy
predict flat collapse better than depth alone -- SECONDARY, not an HP gate); op2_d8-vs-op4_d4
iso-entropy cross-over (full grid); hier_extends_depth flag.

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = n_arms(7) * n_seeds(5) * n_regimes(9) = 315 (FULL).
- arms_differ_verified (AF): hier_options vs flat_gonogo AND vs hier_shuffled op-trace hash per
  seed; exempt when best_w_reach_hier==0. MEASURED@smoke: af_collision=False all 4 regimes.
- final_metrics_atomicity: tmp_replace (os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException). Grep-gate: PASS (CLEAN).
- baseline_in_band (META_RULE_AG): reported per-regime for the ADDITIVE reference; the HIER
  discriminator is FLAT-referenced (headroom_flat), measurable even where additive floors. The
  fair-for-hier gate = oracle>=0.90 AND headroom_flat>=0.10 (declared substitute for
  additive-in-band, because op4_d6 additive floors by design -- the exact v2 META_RULE regime).
- calibration_check: adaptive_with_discriminator_gate (adaptive cf-RPE LR + reach_rank gate +
  hier_shuffled load-bearing gate).
- crlb_n/a: accuracy-closure has no single closed-form noise floor; reachability by feasibility
  (v2 flat closure=0.66 at fair d4; op2_d6 gonogo=0.39 shows the gate works when per-decision
  complexity is low; hierarchy manufactures that low-complexity regime at high depth).
- effective_vs_nominal (Gate A): n_ops directly sets reach_rank chance + per-hop branching; depth
  directly sets chain length + n segments; SEG_LEN directly sets per-decision reach horizon.
  sweep_alignment_verdict: ALIGNED.
- positive_control (Gate D): flat_gonogo reproduces the deeper-cell/v2 flat collapse AT TEST
  REGIME (op4_d6 flat MEASURED@smoke=0.090, matches deeper-smoke 0.104 / v2 FULL 0.075 direction).
  tolerance: qualitative (flat must collapse at op4_d6). MEASURED: flat=0.090 at op4_d6 (collapsed).
- discriminating_fraction (Gate B): 4/4 smoke regimes discriminating (oracle_ok + headroom_ok +
  hp_ok all True); full grid spans entropy 4..16. >= 0.30.
- signal_shape_compatibility (Gate C): all arms consume E/W_ops/M identically; hier adds a
  waypoint-state input (E[traj_idx]); SHAPE_MATCH (states are E-manifold vectors like goals).
- functional_requirements: (1) per-hop op-selection toward a goal -> SR reach value (existing CG);
  (2) recover far-goal reach starvation at depth -> re-anchor to near sub-goal (hierarchical
  decomposition; the new op); (3) prove decomposition (not info) is load-bearing -> hier_shuffled;
  (4) fair measurability at floored-additive regime -> flat-referenced closure + headroom gate.
- defensive_error_checking: passed_all_4 (start_marker, crash_diagnostic, heartbeat, chunked via
  resumable_seeds per-seed partial + fatal-flag).
- progress_logging: print_flush_true (line-buffered + flush per line + per (seed,V,n_ops) print;
  per-seed heartbeat). FULL timeout_s >= 1800.

## Compute architecture
(a) batched-GPU. SR-TD training (gamma=0.85 fixed), operator application, cleanup, reach = batched
matmuls on cuda-if-available. Chains batched; within-chain hops sequential (genuine dependency). SR
trained once per (V,n_ops) group (3 groups/seed) and shared across depths. Storage: sharded (each
op its own W; M a learned value operator). No bundled store. FULL strongly prefers overnight_queue
(GPU).

## Discriminator-survives-scale (option C)
Smoke holds N/V == FULL per (V,n_ops)=6.83 AND includes the focus op4_d6 at IDENTICAL depth ->
per-hop cleanup difficulty + depth-dependence match FULL. The discriminator FIRED decisively at
smoke. Scale expectation: at N=8192 reach is SHARPER (deeper cell: reach_rank 0.40->0.69,
N2048->8192) so hier's near-waypoint reach IMPROVES, while flat's far-goal reach does NOT recover
(v2 flat d6=0.075 at N=8192 is even lower than smoke 0.104) -> the hier-vs-flat gap should be
EQUAL or LARGER at scale. Discriminator survives scale robustly.

## SMOKE RESULT (MEASURED@data/exp_pfc_gate_branching_depth_entropy_grid_v1_smoke/metrics.json)
N=2048, 3 seeds [7,17,23], grid {n_ops 2,4} x {depth 4,6}, 121s wall, cardinality 84/84.
verdict=HARD_PASS. FOCUS=op4_V300_d6 (entropy=12): FLAT=0.090 HIER=0.868 SHUF=0.014 ORACLE=0.951;
hier_closure=0.903 (>=0.25) hier_lift=0.778 shuf_gap=0.854 reach_tcos_corr=-0.049 sign_p=1.1e-32
reach_rank=0.403 (>0.30) cv=0.041 af=False hier_extends_depth=True.
Grid (F=flat/H=hier/dH=lift): op2_d4(e4:F0.535/H0.944/dH0.410) op2_d6(e6:F0.194/H0.882/dH0.688)
op4_d4(e8:F0.222/H0.812/dH0.590) op4_d6(e12:F0.090/H0.868/dH0.778). All 4 regimes hp_ok=True.
spearman(hier_lift,entropy)=+0.80 (hierarchy helps MORE at higher entropy, as predicted).
HONEST READS:
- FLAT collapses monotonically with entropy (0.535->0.090); HIER stays ~0.81-0.94 across the grid
  -- hierarchy essentially FLATTENS the entropy dependence (removes the collapse).
- hier is NEAR oracle (0.868 vs 0.951 at op4_d6): the correct-waypoint assist is STRONG. The
  hier_shuffled control (SHUF=0.014, floor) is the guard -- wrong waypoints fully fail, so the
  recovery is decomposition-SPECIFIC, not free score. Claim is scoped to "given decomposition"
  (autonomous waypoint discovery is the follow-on).
- entropy_beats_depth=False at smoke: spr(flat,ent)=-0.80 vs spr(flat,depth)=-0.89. The 2x2 smoke
  grid is UNDERPOWERED to separate log2(n_ops)*depth from depth-alone (only 2 depths, 2 n_ops).
  The entropy-vs-depth MODEL question is INCONCLUSIVE at smoke; the HIERARCHY question is
  decisively HARD_PASS. The full 3x3 grid (9 entropy points 4..16, incl. iso-entropy op2_d8 vs
  op4_d4) has the spread to test the entropy model properly.

## FULL config (staged; do NOT self-dispatch -- needs push, route via orchestrator to GPU)
N=8192, seeds [7,17,23,31,41], gamma=0.85, seg_len=2, grid {n_ops 2,3,4} x {depth 4,6,8}
(V: op2=800, op3=1000, op4=1200), SR_STEPS=8000, SR_BATCH=256, n_train=300, n_test=240,
rollout_per_V=50. EXPECTED_N_UNITS=315 (7 arms x 5 seeds x 9 regimes).
Recommended queue: overnight_queue (GPU). Recommended --timeout: 14400s (4h; expected ~90-150min
on GPU; 3 SR trains/seed x 8000 steps N=8192 + 9-regime x 7-arm grid incl depth-8; per-seed
checkpoint/resume protects partials on timeout-kill). Note: op4_d8 oracle may dip near 0.90
(0.99^8~0.92) -- if it falls below, that regime is excluded from FOCUS (falls back to op4_d6) but
still reported; focus-selection is robust.
