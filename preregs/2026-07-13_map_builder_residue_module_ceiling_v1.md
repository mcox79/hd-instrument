# Pre-registration: map_builder_residue_module_ceiling_v1

Date: 2026-07-13. Author: exp_dev. Anchor: `map_builder_residue_module_ceiling_v1`.
Cell: `experiments/exp_map_builder_residue_module_ceiling_v1.py`.
Queue: remote_cpu_queue (device=cpu; zero SGD; one-shot Hebbian). Seeds [7,13,17].

## Question

Is RNS/CRT multi-module residue coding (grid-cell VSA construction; Frady/Kleyko arXiv:2311.04872; Sreenivasan &
Fiete 2011) a DEPLOYABLE lever that raises the recoverable-signal ORACLE CEILING of the inductive relational
map-builder at SUB-QUADRATIC cost, AND does it survive a MATCHED CLEAN decode? Tests the codes<->decode COUPLING
because a VET-banked prior predicts residue codes on a noisy associative readout are set up to fail.

Prior-work check (substrate-KB concept-query, cosine>0.30): top hit
`RULE_capacity_cell_gate_must_be_capacity_relative_not_fixed_M` (0.3135, a methodology rule, NOT a prior RNS cell);
`resonator_capacity_rescue_v1` (0.2754, MIDDLE_BAND, decode-side not residue-code). No prior RNS/CRT residue-module
ceiling cell at cosine>0.30 -> this cell is GENUINELY NOVEL for the substrate, not a rediscovery.

VET-banked design constraint honored: `reference_crt_residue_helps_clean_encoding_hurts_noisy_readout_2026-07-06`
(CRT/residue HELPS clean-exact encoding, HURTS noisy associative readout). Our relational readout IS
noisy-associative, so the cell tests RNS codes x {noisy per-module argmax decode, clean joint decode} to localize
capacity-present-but-unreadable vs capacity-absent.

## Reference bars (MEASURED, on-disk)

- Monolithic native ORACLE by dim (O(n_dim^2) W cost): {1024:0.023083, 2048:0.118037, 4096:0.413520, 8192:0.780600}
  MEASURED@data/exp_kg_store_dim_scaling_ceiling_v1/metrics.json:gates.oracle_mrr_by_dim. 8192 = the undeployable
  relief target (W cost 67.1M).
- Additive (SGD TransE k=24) ORACLE = 0.137293 ; realized additive compose = 0.128210
  MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.{ORACLE_ADDITIVE,ANCHOR_COMPOSE}.

## Design

RNS: K=5 pairwise-coprime moduli m=[7,11,13,17,19] (product 323323 >> N~25.7k). Only entities (the large decode
target) residue-coded; relations keep a full per-module codebook. Per module k: a REAL KGStore(n_ent=m_k, n_rel,
n_dim=d_k=2048) supplies random-bipolar codebooks + one-shot Hebbian W_k over residue-mapped (h%m_k, r, t%m_k)
train (+fold-in) edges. RNS W-cost = K*d_k^2 = 20.97M (3.2x CHEAPER than the 8192 relief). Matched-cost monolithic
control at d_match=round(sqrt(K)*d_k)=4579 (W-cost 20.97M) = the same-cost bar the residue code must beat.

## 2x2 (residue-code x decode; all ORACLE = fold-in; filtered MRR rank-vs-all-N)

- MONO_PC_ORACLE (d=1024): positive control, reproduce 0.023.
- MONO_MATCHED_ORACLE (d=4579, same W-cost as RNS): same-cost bar + oracle-fire gate.
- RNS_NOISY_ORACLE: residue codes, HARD per-module argmax decode + agreement (fragile; VET predicts loss).
- RNS_CLEAN_ORACLE: residue codes, SOFT joint decode score(t)=sum_k <recall_k, C_k[t%m_k]> over all N (HEADLINE).
- RANDOM: null floor. SECONDARY: RNS_CLEAN_COMPOSE (realized, support->signature, clean decode) + RNS_SCRAMBLE_COMPOSE
  must-fail vs additive compose 0.128. POP: fit-independence / BROKEN guard floor.

## Pre-registered bands (fractions of ADD_ORACLE=0.137293 + cost-relative + coupling; picked BEFORE the run)

- ORACLE-FIRES: MONO_MATCHED >= 3x RANDOM AND (MONO_MATCHED - RANDOM) >= 0.003.
- POS-CONTROL: |MONO_PC - 0.023| <= 0.010 AND RANDOM <= 0.004 AND finite W AND not BROKEN(POP>RANDOM).
- **CAPACITY_DEPLOYABLE_SUBQUADRATIC**: pos-controls + oracle-fires AND (RNS_CLEAN - RANDOM) >= max(0.50*0.137, 0.010)
  AND RNS_CLEAN >= MONO_MATCHED + 0.020 (beats same-cost monolithic) AND RNS_COST < RELIEF_8192_COST. Reports coupling
  DECODE_LIMITED if (RNS_CLEAN - RNS_NOISY) >= 0.50*(RNS_CLEAN - RANDOM).
- **NOT_DEPLOYABLE_CODES_ABSENT**: (RNS_CLEAN - RANDOM) < 0.010 (no recoverable residue signal under EITHER decode).
- **NOT_DEPLOYABLE_NO_SUBQUAD_ADVANTAGE**: recoverable but RNS_CLEAN <= MONO_MATCHED (same-cost monolithic >= it).
- MIDDLE_BAND_MARGINAL_RESIDUE_EDGE: recoverable and RNS_CLEAN in (MONO_MATCHED, MONO_MATCHED+0.020].
- INCONCLUSIVE if oracle doesn't fire / pos-controls fail / too few held-out / BROKEN.

HYPOTHESIZED expectation (NOT gating): the VET prior + arbitrary-entity-ID (no numeric structure to residue-exploit)
both point toward NOT_DEPLOYABLE or DECODE_LIMITED-but-below-mono; a genuine sub-quad win would be a strong surprise.
Either outcome is informative (see research note). Bands are honest; let the FULL decide.

## Schema-vet / cell-template compliance

- cell_chunked: false (3 seeds in one cell; cheap one-shot Hebbian, per-seed try/except with failure_class + cardinality gate).
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace). start_marker_written / crash_diagnostic_present / heartbeat_present: true.
- except SystemExit: raise BEFORE except Exception (no BaseException / no bare except; grep-clean).
- arms_differ_verified: 8 arms, >=5 distinct sigs enforced per seed (self-test observed 8).
- cardinality_ok: EXPECTED_N_UNITS = n_seeds; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if short.
- crlb/info-ceiling: bands are fractions of the measured additive-oracle ceiling + an in-run same-cost monolithic bar -> reachability OK by construction.
- baseline_in_band: MONO_MATCHED must fire (>=3x RANDOM); MONO_PC reproduces 0.023; RANDOM at floor.
- calibration_check: default_ok_for_this_regime (moduli/dims/fracs/tols pre-registered, not tuned on real data; CSKG core + split config copied verbatim from native + additive arenas).
- §15 gate F (ENFORCE): real_code_path_exercised=[KGStore, build_residue_module, ingest_triples, module_residue_sims];
  substrate_signature_checked=[KGStore] (base/portable kwargs n_ent,n_rel,n_dim,generator only -- NOT optional init_entities);
  guard_baseline_validated=[BROKEN_POP_BEATS_RANDOM] (compared vs RANDOM floor). All 7 validity-preflight checks declared; self-test PASSED under VALIDITY_PREFLIGHT_MODE=enforce.
- progress_logging: print_flush_true (line-buffered stdout + per-seed/per-module flush + heartbeat).

## Compute

class (b) sequential-CPU justified: one-shot Hebbian, no SGD, no GPU. Reference dim_scaling built stores up to
n_dim=8192 across 3 seeds on device=cpu in 1768s; this cell builds nothing above d=4579 -> strictly cheaper.
remote_cpu_queue, timeout 5400s.

## Smoke verdict (self-test, VALIDITY_PREFLIGHT_MODE=enforce)

SELFTEST_PASS (0.2s). Planted residue-recoverable arena (moduli [11,13,17], n_ent=80, d=1024):
RNS_CLEAN=0.691 >> RNS_NOISY=0.300 >> RANDOM=0.084 (discriminator + clean-vs-noisy coupling both fire);
MONO_PC=MONO_MATCHED=1.0 (oracle fires); relation-scramble=0.238 + scrambled-support-compose collapse below clean;
8 distinct sigs; real KGStore per-module residue path exercised (ingest_triples); all 7 validity-preflight checks pass.
