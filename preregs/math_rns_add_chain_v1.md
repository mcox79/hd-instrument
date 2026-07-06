# PRE-REG: exp_math_rns_add_chain_v1

**Cell:** `experiments/exp_math_rns_add_chain_v1.py`
**Anchor:** `math_rns_add_chain_v1`
**Author:** exp_dev  **Date:** 2026-07-05
**Source pre-reg (bands):** `notes/research_math_capability_translation_first_cell_2026-07-05.md`
**Prior-work check (substrate KB):** NONE at cosine>0.30 (top hit "Group homomorphism" math-KB *fact*
atom at 0.248; no prior phase-linear *arithmetic capability cell*). Cell is genuinely novel; it is the
first cell that turns the landed RNS/CRT *addressing* machinery into VALUE arithmetic via a phase-linear
re-encoding. Reuses the CRT number-theory + disjoint-sub-block decode topology from the landed HARD_PASS
`exp_generation_decoder_rns_crt_highvocab_v1` (FULL exact_ordered=1.000 @ V=65536).

## Claim
Phase-linear phasor residue encoding (m-th roots of unity, k_j integer freqs) makes ADDITION a group
homomorphism under the EXISTING FHRR bind operator (elementwise complex product): `enc(a) (*) enc(b) ==
enc((a+b) mod M)`. Decode via existing per-sub-block phasor argmax + CRT. Yields exact multi-step add
chains and an exact (discrete, non-fuzzy) equality-check primitive (the self-reasoning hook).

## Arms (all PAIRED on identical (a,b) integer pairs per regime/seed)
- `phase_linear_add` [MECHANISM] -- phasor FPE codebook; bind=complex product; decode=argmax+CRT.
- `random_codebook_add` [CONTROL] -- IDENTICAL pipeline, random-per-(r,j) phasors (not linear in r) -> no
  homomorphism. Isolates phase-LINEARITY (stronger than random-real: everything held constant except linearity).
- `scrambled_modulus` [CONTROL] -- arm-A phasor decode then DERANGE residues before CRT -> reconstruction collapse.
- `chain` [MECHANISM] -- arm A over L-step add chains (running bind product), depths L in {1,3,5,10}; per-step
  decode inspectable.
- `equality_check` [PRIMITIVE] -- decode(result) EXACTLY == claimed answer (discrete True/False, not cosine):
  accept-correct + reject-incorrect crispness.

## Regimes (dynamic-range sweep, >=3 moduli-products)
small (7,8,9) M=504 | mid (16,17,19) M=5168 | large (40,41,43) M=70520. N=8192, R=3, sb=2730. Seeds (7,13,19).

## Pre-registered bands
| Metric | HARD-PASS | HARD-FAIL |
|---|---|---|
| `phase_linear_add` exact-add (min over regimes) | >= 0.99, cv <= 0.10 | < 0.60 at any regime |
| `random_codebook_add` exact-add (max) | <= 0.15 | >= 0.40 (leak) |
| `scrambled_modulus` exact-add (max) | <= 0.05 | -- |
| `chain` depth-3 exact (min) | >= 0.75 | < 0.20 |
| `equality_check` accept-correct (min) | >= 0.99 | -- |
| `equality_check` reject-incorrect (min) | >= 0.99 | -- |
| near-miss frac (runner-up <= 0.5*rank1) | >= 0.90 (is-math-easier probe; reported, not hard-gated) | -- |

## SCHEMA-VET fields
- **Compute architecture:** `(b) sequential-CPU with justification`. numpy complex64; wall < 10s total
  (smoke MEASURED 1.9s). Carve-outs: cell IS the substrate-primitive being validated (bit-exact reference)
  AND total wall < 10s. No GPU speedup relevant (per-trial work ~3*40*2730 flops). No batching required.
- **Storage strategy:** `no_storage_algebraic_bind`. Composition is via BIND (elementwise product); the
  composite IS exactly the codeword of the sum (a single valid value), not a superposition of items to be
  separately retrieved. Neither sharded nor bundled in the retrieval sense -> sharded/bundled rule N/A.
- **cardinality_ok:** EXPECTED_N_UNITS = n_regimes * n_seeds * (3 single + n_depths + 1 eq). Gated; smoke
  MEASURED 63/63.
- **arms_differ_verified:** phase codebook hash != random codebook hash; arm-A recovered integers hash !=
  scrambled recovered integers hash. MEASURED True. (Truth-integer arrays never hash-compared -- an exact
  adder and a broken adder both know truth; we hash CODEBOOKS and RECOVERED-integer arrays, which differ.)
- **final_metrics_atomicity:** `tmp_replace` (metrics.json.tmp -> os.replace).
- **except ordering:** `except SystemExit: raise` before `except Exception` (no BaseException, no bare except).
- **crlb / discriminator_reachability:** True. Per-residue argmax over m_i<=43 candidates in sb=2730 sub-block;
  SNR ~ sqrt(sb) rank-1 vs ~1/sqrt(sb) runner-up; sb >> max modulus -> collision-free; no noise floor gates 0.99.
- **baseline_in_band (META_RULE_AG):** N/A -- exactness/correctness test, not a difficulty sweep. arm A
  expected ~1.0 by exact-homomorphism construction; arms B and C are declared CONTROLS intentionally ~0.0
  (exempt, same carve-out as single_synth/rns_scram in the landed rns_crt cell). Discriminator = CONTRAST
  A(~1.0) vs B(~0.0); does NOT saturate at scale (B -> 1/M as M grows).
- **discriminator survives scale:** option A -- smoke runs at FULL N=8192, FULL sb=2730, ALL 3 regimes; only
  trials/seeds/depths reduced. A-holds + B-collapse + C-collapse + chain-exact all FIRE in smoke.
- **run_mode verification:** metrics assert run_mode==mode; smoke landed run_mode=smoke, size 15099B.
- **defensive error-checking:** start_marker + heartbeat + crash-diagnostic + atomic metrics = passed_all_4.
- **progress_logging:** N/A (wall < 10s; single-shot per unit; not a timeout_s>=1800 cell).
- **positive_control (gate D):** CRT decode reproduced AT TEST REGIME via `crt_selftest` + `homomorphism_selftest`
  (decode(bind(enc(a),enc(b)))==(a+b) mod M) run for EVERY regime before arms; both MEASURED PASS all modes.
- **functional_requirements (gate E):**
  1. exact addition -> existing FHRR bind (complex product) + phase-linear encoding (this cell's new 100-line increment).
  2. multi-step derivation -> repeated bind (associative homomorphism); reuses running-product bookkeeping.
  3. modular wraparound / carry -> handled at encoding (integer freqs -> exact period-m) + CRT reconstruction (landed CG).
  4. exact equality-check -> discrete decode-and-compare (CRT integer ==), not cosine; the self-reasoning primitive.
- **effective_vs_nominal (gate A):** ALIGNED. Swept axis = M (moduli product); each primitive experiences the
  same M (no partition routing dilutes it).
- **discriminating_fraction (gate B):** the discriminator is a CONTRAST (A~1.0 vs B~0.0), not a sweep landing
  in [0.3,0.7]; N/A by cell-type (correctness/homomorphism test, declared).

## SMOKE RESULT (MEASURED@data/exp_math_rns_add_chain_v1/metrics.json)
HARD_PASS. All 3 regimes x 3 seeds: phase_linear_add=1.000 (cv=0.000), random_codebook_add=0.000,
scrambled_modulus=0.000, chain d1/d3/d5=1.000, equality accept=1.000 reject=1.000, near-miss frac=1.000.
Demos (M=504): 7+5=12, 12+30=42, 250+250=500, 100+404=0 (WRAP), 503+2=1 (WRAP) -- all exact.
Wall 1.9s.

## FULL staging
FULL = same 3 regimes, seeds (7,13,19), trials=300, depths (1,3,5,10). LOCAL-CPU-feasible (~10-15s) but per
USER-lock FULL must NOT go to local_cpu_queue (SMOKE-only on local); canonical run = remote landing. Route
FULL to `remote_cpu_queue` via Orchestrator (push to origin/main required; harness-denied to exp_dev).
Timeout: 600s (generous; expected ~15s).
