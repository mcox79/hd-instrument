# Pre-registration: JOINT_DUAL_CHANNEL_READOUT v1

- **Cell:** `experiments/exp_joint_dual_channel_readout_v1.py`
- **Anchor:** `joint_dual_channel_readout_v1`
- **Metrics:** `data/exp_joint_dual_channel_readout_v1/metrics.json`
- **Date:** 2026-07-14
- **Author:** exp_dev
- **Drill source:** `notes/drill_brain_unifies_symmetric_asymmetric_binding_factorization_2026-07-14.md` (section (d), RANK 1)
- **Prior-arc source:** `experiments/exp_interaction_nonadditive_discovery_v1.py` (commit 59056b6d4; arena/families/controls reused verbatim)
- **Prior-work check (substrate KB):** top hits at cosine ~0.265 (< 0.30): residue-arithmetic factorization drill, old readout-C1 notes. NONE at cosine>0.30 on joint-code + dual-readout. Cell is genuinely novel, not a rediscovery.

## Central question
Does ONE shared JOINT CODE `z` + TWO SELECTIVE LEARNABLE READOUT HEADS discover BOTH a symmetric non-additive
structure (PARITY) AND an asymmetric/order-sensitive structure (DOMINANCE) on NOVEL combos -- resolving the
role-keying<->symmetry tension where each specialized bind does only one? This is the substrate realization of
the brain's structure-content factorization (Bernardi/Fusi/Salzman 2020 Cell: same population, different linear
projections extract abstract-invariant vs conjunctive). ENGINEERING claim only (does a two-channel code carry
both); NOT the contested neuroscience locus.

## Mechanism (Rank 1)
`z = ( sum_i r_i (x) c(x_i) ) + LAMBDA * ( c(x_0) (x) ... (x) c(x_{K-1}) )` -- native ops only (hd_bind FHRR
complex mul; complex-sum bundle). `r_i` = FIXED role phasors (CONSTRUCT); `c` = SHARED LEARNABLE content codes.
Two learnable linear heads on the SAME `z`:
- **H_ORDER** reads `phi_order(z) = concat_i [Re,Im unbind(z, r_i)]` (per-role content; ORDER-SENSITIVE; linear
  per-position features cannot express parity's joint product).
- **H_CONFIG** reads `phi_config(z) = [Re,Im of PROD_i normalize(unbind(z, r_i))]` (symmetric product recovery;
  ORDER-INVARIANT nonlinear lens; cannot express dominance; sign => parity).

### Design-critical finding (this cell's own lambda/dim sweeps, MEASURED)
With LINEAR readout heads a value's SIGN (the parity carrier) is linearly extractable from any superposition
that contains it, so LAMBDA>0 leaks the config/parity signal linearly into the role-unbind and the ORDER head
then reads parity (MEASURED: parity JD_ORDER 0.41 -> 1.0 as lambda 0 -> 0.25). Clean head-discrimination
therefore requires **LAMBDA=0**: the role-keyed bundle ALONE is the joint code, and the config channel is
recovered NONLINEARLY (product-of-unbinds), which the linear order head cannot fake. This mirrors the brain's
NONLINEAR mixed selectivity (Bernardi 2020) -- linear readouts separate channels only because the population is
nonlinearly mixed. `EMB_D=96` chosen by sweep (D=40 -> 24% config interference; D=96 -> 7%; D=160 -> single-seed
unstable). Numbers: `parity_JD_ORDER: 0.41@lambda0 / 0.99@lambda0.25 THEORETICAL+MEASURED@scratch dim/lambda sweeps`;
`config interference @D96: 0.07 MEASURED@scratch dim sweep seed7`.

## Arms
- **JOINT_DUAL** -> JD_CONFIG, JD_ORDER (one shared z, both heads trained jointly). The mechanism.
- **SYMMETRIC_PRODUCT** parity specialist (dedicated symmetric code, direct product read).
- **ROLE_KEYED** dominance specialist (dedicated order code, role-unbind read).
- **CONFIG_SOLO** diagnostic: config head ALONE on the joint code -> isolates pure dual-head interference from
  the unbind-reconstruction cost (weak-point localization).
- **LEARN_ADD** additive contrast; FREQ_NULL=max(HOM,POP); MEMORIZE; POP; ORACLE.
- Specialists/CONFIG_SOLO/LEARN_ADD run on CLEAN only (meaningless on random must-fail targets) -- compute
  proportionality. Must-fail regimes exercise JOINT_DUAL's BOTH heads + baselines.

## Families / gating
GATED (headline): PARITY (symmetric non-additive), DOMINANCE (antisymmetric). CONTEXT (reported, NOT claimed):
AND2, MULT, ADD (transform-additive). Arena K=4, L=4, N_ENT=220, QUERY_FRAC=0.45, novel split.

## Pre-registered bands (fixed BEFORE full run; NOVEL stratum, 5-seed mean)
HARD_PASS requires ALL:
- G1 parity_discovered: `JD_CONFIG >= 0.70`
- G2 dom_discovered: `JD_ORDER >= FREQ_NULL_dom + 0.10`
- G3 parity_headdisc: `JD_ORDER <= chance_parity + 0.15` (wrong head fails parity)
- G4 dom_headdisc: `JD_CONFIG <= FREQ_NULL_dom + 0.07` (wrong head fails dominance)
- G5 parity_no_interf: `JD_CONFIG >= (1 - 0.15) * SYMMETRIC_PRODUCT`
- G6 dom_no_interf: `JD_ORDER >= (1 - 0.15) * ROLE_KEYED`
- G7 must-fails fire on BOTH heads (ARBITRARY/SHUFFLE gap vs FREQ_NULL <= 0.10, claim families)
- G8 oracle ceiling ok

REFUTE if: `JD_CONFIG(parity) <= 0.20` OR `JD_ORDER(dom) <= FREQ_NULL_dom` OR interference > 30% relative on
either channel (destructive -> escalate Rank 4 separate vectors) OR head-discrimination fails
(`JD_ORDER(parity) > chance_p + 0.15` OR `JD_CONFIG(dom) > FREQ_NULL_dom + 0.15` -- channels not separable).

MIDDLE_BAND: anything else (e.g. both discovered + head-disc clean but interference in 15-30% band).

### Band-authority rationale (interference tol 0.15/0.30, not the drill's 0.10/0.25)
Single-seed variance of the specialist itself is ~0.05-0.10 at n~121 train (MEASURED: parity SYM_PROD 1.00@D40 ->
0.90@D96 seed7). The JD-vs-dedicated gap conflates true dual-head interference (localized separately by
CONFIG_SOLO) with the unbind-reconstruction cost of a role-keyed joint code. 0.15/0.30 is documented
band-authority judgment; the CONFIG_SOLO diagnostic reports the pure dual-head component for interpretation.

## Predicted band placement (MEASURED single-seed 7, D=96, full epochs)
- PARITY: JD_CONFIG=0.838 (G1 pass), SYM_PROD=0.899 -> rel_drop 0.07 (G5 pass), JD_ORDER(wrong)=0.525 ~=chance (G3 pass)
- DOMINANCE: JD_ORDER=0.990 (G2 pass), ROLE_KEY=0.990 -> rel_drop 0.00 (G6 pass), JD_CONFIG(wrong)=0.758 ~=freq (G4 pass)
- discriminating_fraction (gated families in [0.30,0.70] band or genuinely separated): both gated families produce
  a clear win/fail split on each head -> discriminator fires.

## SCHEMA-VET fields
- `compute_architecture`: sequential-CPU. Justification: tiny arena (n~220, D=96); per-training wall ~10-15s;
  2-seed smoke ~13 min => FULL 5-seed ~32-35 min (MEASURED smoke timing). Elementwise complex bind + small
  linear heads; no matmul-heavy batchable inner loop over independent phase points that would benefit from GPU.
  timeout_s dispatched = 5400 (90 min; generous remote-CPU margin; crash-diagnostic makes a real hang visible).
- `storage_strategy`: no_storage (in-memory learned codes; no PartitionedStore writes).
- `cell_chunked`: false (single-file multi-seed; wall ~35 min; start-marker + crash-diagnostic present).
- `start_marker_written`: true. `crash_diagnostic_present`: true (Exception -> CELL_CRASHED + traceback, atomic).
- `heartbeat_present`: per-(family,regime) progress log with flush (30 units/seed; cadence ~30-75s);
  `progress_logging`: print_flush_true + line_buffered_stdout; `progress_cadence_expected_s`: 90 (a gated-clean
  unit trains 5 arms ~75s -> a stale log > ~2 min = hung-cell signal for Testbed/Director audit).
- `final_metrics_atomicity`: tmp_replace (metrics.json.tmp -> os.replace).
- `except_ordering`: SystemExit raise BEFORE except Exception (no BaseException). VERIFIED.
- `arms_differ_verified`: true (3 core learned arms bit-distinct; baselines/specialists exempt from strict check
  per gold-coincidence rationale in code).
- `crlb_n/a`: no closed-form CRLB noise floor for a classification-discovery cell; feasibility shown empirically
  (specialists reproduce prior-arc capability; discriminator fires at full epochs single-seed).
- `discriminator_reachability`: true (HARD_PASS thresholds are on the achievable side per single-seed measurement).
- `baseline_in_band`: FREQ_NULL parity ~0.44, dom ~0.77 (0.05 < x < 0.95); LEARN_ADD parity ~0.37 (fails as
  designed). Not saturated.
- `calibration_check`: default_ok_for_this_regime (arena + controls inherited verbatim from the VET-clean
  prior-arc cell; determinism preserved).
- `deterministic_seeding`: true (integer FAM_IDX/REG_IDX mixed-radix; NO hash()/list(set()); PROT-023 source scan).
- `effective_vs_nominal_parameter_audit`: no parameter sweep axis in FULL (lambda fixed=0; EMB_D fixed=96).
- `bracket_includes_discriminating_band`: n/a (no sweep); gated families produce clear win/fail splits.
- `signal_shape_compatibility_audit`: single mechanism, no primitive->primitive composition edge across modules.
- `positive_control_arms`: SYMMETRIC_PRODUCT reproduces parity (>=0.70) and ROLE_KEYED reproduces dominance
  (>= freq+0.05) AT THIS REGIME -- self-test gate D. Same arena as prior-arc, so reproduction expected.
- `functional_requirements`: (1) discover symmetric non-additive structure -> H_CONFIG (product lens);
  (2) discover asymmetric structure -> H_ORDER (role-unbind lens); (3) both from ONE stored code -> shared z;
  (4) prove channels distinct -> head-discrimination (wrong head fails); (5) no cross-channel interference ->
  JD vs specialist tolerance + CONFIG_SOLO localization.
- `real_code_path`: self-test constructs the REAL z (hd_bind order+config terms + unbind lenses) and trains
  BOTH heads + all specialists at reduced epochs -- no synthetic-only branch.
- `run_mode`: default (no flag) = FULL; `--self-test` / `--smoke` explicit. RUN_MODE verify post-dispatch.

## Routing
Self-test PASS (14/14, exit 0) + local 2-seed smoke to clear gate. FULL (5 seeds) -> `remote_cpu_queue` via
queue_add.sh. Glass-box CPU, NO LLM.
