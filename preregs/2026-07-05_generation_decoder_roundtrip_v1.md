# Pre-registration: generation_decoder_roundtrip_v1 (FIRST generative DECODER -- the substrate's "mouth")

Date: 2026-07-05
Cell: experiments/exp_generation_decoder_roundtrip_v1.py
Queue: remote_cpu_queue (CPU-only: DEVICE=cpu, torch.set_num_threads(8); task-mandated CPU probe, no LLM/GPU)
Run mode: full (runner invokes WITHOUT --smoke; cell defaults run_mode=full per META_RULE_16)
Design pointer: notes/decoder_design_stage_A_factor_B_order_C_cleanup_generation_readout_2026-07-05.md
Authorized by: data/exp_factorization_envelope_v1/metrics.json verdict=GO (GEN_svo_1k mean=1.000)

## Purpose

Close the encode->reason->GENERATE loop with a substrate-native, faithful-BY-CONSTRUCTION readout:
read a bound proposition HV back into an ORDERED surface token sequence. This is the clean INVERSE
of the concept encoder. Constructive build work (NOT a vs-LLM comparison).

A proposition = superposition of D bound TERMS, each term = bind(position_role, filler), F=2 factors:
    p = sum_{d=0..D-1}  pos_book[d] * lex[toks[d]]   (bipolar BSC elementwise product)
Position IS the role (2 factors; the envelope F=3 cliff/F=4 wall forbids a 3rd factor). Order is
CARRIED in the vector via position binding at encode (Stage B), not invented at decode.

## Prior-work check (substrate-KB concept query, mandatory)
`bash tools/substrate_query.sh "generative decoder resonator factorization ... position role cleanup lexicon"`
Top relevant hit: resonator_factorization_v1 (cosine=0.3262, verdict MIDDLE_BAND) -- a prior tiny
resonator probe (N=2048, V=30). Rest of hits are gene-ontology noise (substrate knows no language).
This cell is NOT a rediscovery: it is the first ROUND-TRIP generation readout on REAL correlated
concept fillers at substrate scale N=8192, keyed on the memo-mandated hub-rescue mechanism.

## Architecture (3 stages, inverse of encode->reason->generate)
- Stage A FACTOR: recover the D role-filler tuples (iterative unbind + cleanup + explaining-away).
- Stage B ORDER: order carried by position binding; recovered per-slot -> ordered token sequence.
- Stage C CLEANUP: codebook argmax per factor; same-slot collisions prevented BY CONSTRUCTION by
  PROTECTED/INDEX position binding pos_book[k]=roll(base,k) (E3 permutation-indexed binding; the
  VET-confirmed MM_STANDARD hub-rescue mechanism, exp_deep_reasoning_hub_robustness_v1 commit 5eb05b4e5).

PRIMARY deliverable arm = ROLES-KNOWN decoder (positions known -- the decoder owns its own fixed role
vectors; unbind by each known position + iterative explaining-away). This IS the memo-mandated Stage-C
mechanism (roles-known resonator + protected/index binding). Faithful: every emitted token traces to
one unbind op on the bound structure. SECONDARY arm = full resonator (positions ALSO recovered) --
documented to COLLAPSE on correlated fillers (a genuine finding: positions-unknown factorization on
correlated codebooks is v2 / sparse-block-resonator territory; known-position decode is the right MVP).

## Real correlated fillers (clean-test discipline, USER-locked)
Deliverable arm uses REAL concept fillers: sample V real concept BGE vectors from
data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz["semantic"] -> FIXED random
Gaussian projection BGE_DIM(1024)->N(8192) -> sign() -> bipolar. Preserves the real cos-cone
(measured mean pairwise cos ~0.34). Synthetic iid bipolar = the envelope ceiling (positive control).
The gap between them is the point; the clean-iid 1.0 is the ceiling, this cell measures the REALIZED
round-trip on real correlated fillers.
REFERENT NOTE: the 1.3GB BGE npz is a local-only-flagged artifact. VERIFIED PRESENT on remote
marsh@home:C:/dev/hd-instrument/... on 2026-07-05 (ssh Test-Path -> BGE_PRESENT) before dispatch.

## Metrics (joint-gate; report all three co-equally, per contract)
1. per_term_recovery -- Stage A (envelope cross-check; roles-known -> per-slot filler correct).
2. exact_ordered_sequence -- Stages A+B+C end-to-end (the real generation goal).
3. per_token_cleanup -- Stage C filler cleanup (order-free filler match).

## Pre-registered verdict bands (memo)
- HARD_PASS: exact_ordered_sequence >= 0.70 AND per_term within 0.10 of envelope ceiling (>= 0.90;
  ENVELOPE_CEILING=1.0). Scope: real_rolesknown_hi arm only (HP_SCOPE below).
- HARD_FAIL: exact_ordered_sequence < 0.30 (decoder cannot round-trip even S/V/O).
- MIDDLE_BAND: 0.30-0.70 -> chunking wrapper needed for propositions beyond the GO region.
- Discriminator-fires gates (block HARD_PASS if unmet):
  (a) synth-iid roles-known ceiling per_term >= 0.90 (decoder wiring positive control), else DISCRIMINATOR_DID_NOT_FIRE.
  (b) noorder control (shared-position encode destroys order) collapses: real_exact - noorder_exact >= 0.20,
      else ORDER_DISCRIMINATOR_DID_NOT_FIRE.

## Arms (6; PAIRED trials -- SAME propositions across all arms per seed)
- synth_rolesknown      : roles-known, synth iid lexicon (ceiling / positive control)
- real_rolesknown_hi    : roles-known, real lexicon, iterated explaining-away  [PRIMARY DELIVERABLE]
- real_rolesknown_lo    : roles-known, real lexicon, single-shot (n_iters=0)   [compute-lever floor]
- noorder_ctrl          : roles-known, real lexicon, SHARED-position encode     [must collapse]
- synth_fullreso_hi     : full resonator (positions recovered), synth iid, R=16 [full-reso positive control]
- real_fullreso_hi      : full resonator (positions recovered), real, R=16       [secondary: correlation limit]

## Compute architecture
Class: (b) sequential-CPU WITH justification. (1) task-mandated CPU probe (no LLM, no GPU); (2) the
resonator ALREADY batches its RESTARTS as matmul (restarts x N @ V x N); per-trial/per-seed loops are
cheap; (3) full local wall for the FULL config (V=1024, D=3, 3 seeds, 30 trials) = 100.8s MEASURED
(well under any batching-mandate threshold). Storage strategy: no_storage / no_composition (read-only;
propositions built in-cell; no PartitionedStore writes).

## Config
N=8192, V=1024 (<= envelope V<=1024 DIRECT-decoder cliff), D=3 (S/V/O), F=2, RESTARTS=16, MAX_ITER=40,
n_iters=6, seeds=(7,13,19), trials=30. Smoke: V=256, 1 seed, 5 trials. Selftest: V=128, 1 seed, 3 trials.
ALL modes decode AT full N=8192 (never smoke at reduced N; envelope discipline "do NOT smoke at 2048").

## SCHEMA-VET mandatory fields
- cardinality_ok: EXPECTED_N_UNITS = n_seeds * 6 arms = 18 (full). (No sweep axis; fixed grid.)
- final_metrics_atomicity: tmp_replace (metrics.json.tmp -> os.replace).
- arms_differ_verified: True at smoke (real_rolesknown_hi / noorder_ctrl / real_fullreso_hi hash-distinct).
- crlb / capacity-feasibility: envelope ceiling GEN_svo_1k=1.000 (clean-iid) is the analytic UPPER bound;
  discriminator_reachability = True (HARD_PASS thresholds are on the achievable side; MEASURED local
  preview hit exact=1.000/per_term=1.000 3/3 seeds). crlb formula n/a: recovery is deterministic given
  the mechanism (argmax cleanup over a fixed codebook), no continuous-score noise floor.
- baseline_in_band: the load-bearing "baseline" is the noorder control, which MUST collapse (measured
  0.000) -- it is at floor BY DESIGN (order destroyed), which is the required discriminator behavior, not
  an AG saturation failure. The single-shot arm (real_rolesknown_lo) is the compute-lever reference.
- calibration_check: default_ok_for_this_regime (substrate primitives used directly: bipolar bind =
  elementwise product; sign() is a fixed label-free transform; fixed projection is data-independent).
- discriminator survives scale: MEASURED at full N=8192 V=1024 in a local preview (isolated
  HDLAB_EXP_NAME=..._localpreview): 3/3 seeds exact=1.000 per_term=1.000, noorder=0.000, full-reso
  real=0.000 vs synth=1.000. Not a reduced-N extrapolation.
- HP_SCOPE: {real_rolesknown_hi: [HARD_PASS_exact_ordered, HARD_PASS_perterm_within_0.10]}. Ceiling/
  control/secondary arms do NOT inherit the chain-grade gates.
- effective_vs_nominal: V is the true per-slot lexicon the argmax cleanup experiences (no partition
  routing); sweep_alignment_verdict: ALIGNED (single fixed config, no sweep).
- composition_edges: encode(bind) -> resonator(unbind+cleanup) -> order(sort/slot). SHAPE_MATCH
  (bipolar BSC throughout; resonator reused from envelope where it is proven at F=2).
- positive_control_arms: synth_rolesknown reproduces the clean ceiling (roles-known); synth_fullreso_hi
  reproduces envelope GEN_svo (full resonator on iid). Both MEASURED=1.000 in preview -> the real
  full-reso collapse (0.000) is a genuine correlation finding, not a wiring bug.
- functional_requirements: (i) recover which tokens (Stage A/C filler cleanup) -> resonator argmax
  cleanup; (ii) recover their order (Stage B) -> position binding; (iii) avoid slot collisions ->
  protected/index roll binding (hub-rescue). Each maps to an existing chain-grade primitive.
- progress_logging: print_flush_true + line_buffered_stdout + per-seed prints + _heartbeat.jsonl
  (timeout_s < 1800 so not strictly mandatory, but present).
- defensive_error_checking: start_marker_written True; crash_diagnostic_present True (except Exception ->
  CELL_CRASHED + traceback, SystemExit re-raised first); heartbeat_present True; cell_chunked False
  (single 3-seed cell, fast; not multi-seed-chunked -- 100.8s local wall, no zombie risk).
- HYPOTHESIZED vs MEASURED: all band numbers are memo-registered; the preview values
  (exact=1.000, per_term=1.000, noorder=0.000, full-reso real=0.000) are
  MEASURED@data/exp_generation_decoder_roundtrip_v1_localpreview/metrics.json.

## Timeout
Local FULL wall = 100.8s MEASURED. Remote CPU margin: timeout_s = 1200 (20 min = ~12x local; ample for
remote-CPU variance). PROT-018/019/021 n/a (no _n suffix; timeout < 14400).
