# PRE-REG: exp_math_rns_multiply_star_v1

**Cell:** `experiments/exp_math_rns_multiply_star_v1.py`
**Anchor:** `math_rns_multiply_star_v1`
**Author:** exp_dev  **Date:** 2026-07-06
**Source pre-reg (bands):** `notes/research_math_arithmetic_basis_next_primitives_2026-07-05.md` (Q1 + prediction 3)
**Prior-work check (substrate KB):** substrate_query "modular multiplication star operator prime moduli RNS
phasor exponentiation CRT decode" -> top hits ALL wordnet dictionary *fact* atoms (phase_modulation 0.369,
modulation 0.351, exponentiation 0.336, multiplication 0.325); NO prior arithmetic-*capability cell* at
cosine>0.30. Cell is genuinely novel -- the THIRD arithmetic-capability cell, completing {+, -, x, compare}
after the landed HARD_PASS add (`exp_math_rns_add_chain_v1`, exact-add=1.000) and subtract+compare
(`exp_math_rns_subtract_compare_v1`, FULL HARD_PASS). Reuses their phase-linear phasor encoding + CRT decode
topology VERBATIM; the ONLY new operator is elementwise integer-power (the star operator's exponentiate step).

## Claim
The STAR operator (CITED@Kymn et al. 2024, Neural Computation, arXiv:2311.04872 -- the substrate's primary VSA
reference) makes MODULAR MULTIPLICATION exact on the SAME phase-linear encoding the add cell certified. Because
the integer lives in the phasor EXPONENT (codebook_m[r] = w^r, w_j = exp(i*2*pi*k_j/m)), addition is the free
elementwise product; multiplication is the mirror-image cost: decode ONE operand back to a concrete residue,
then EXPONENTIATE the other operand's phasor sub-blocks by it -- `codebook_m[a]**b == w^(a*b) ==
codebook_m[(a*b) mod m]`. Per-sub-block argmax + CRT decode recovers `(a*b) mod M`. Yields exact multiply,
exact multiply-chains, and an exact (discrete) product-equality-check primitive.

## Arms (all PAIRED on identical (a,b) integer pairs per regime/seed)
- `star_multiply` [MECHANISM] -- decode b's residues, exponentiate enc(a) sub-blocks by them, argmax+CRT. ~1.0.
- `bind_not_power` [CONTROL] -- use the free-add bind (enc(a).enc(b) = enc((a+b) mod M)) and CLAIM it is the
  product. Isolates that EXPONENTIATION (not bind) is the multiply operator -- the load-bearing half of
  decode-then-exponentiate. ~0.0.
- `random_exponent` [CONTROL] -- exponentiate enc(a) by RANDOM wrong residues instead of the decoded b.
  Isolates the DECODE half (b must be decoded correctly). ~0.0.
- `random_codebook` [CONTROL] -- IDENTICAL star pipeline on random (non-phase-linear) phasors. Isolates
  phase-LINEARITY. ~0.0.
- `scrambled_modulus` [CONTROL] -- mechanism decode then DERANGE residues before CRT. Isolates CRT. ~0.0.
- `mult_chain` [MECHANISM] -- star over an L-step running-PRODUCT chain (running ** decoded next), depths
  {1,3,5,10}; per-step decode inspectable.
- `equality_check` [PRIMITIVE] -- decode(a*b) EXACTLY == claimed product (discrete True/False, not cosine):
  accept-correct + reject-incorrect crispness.

## Regimes (dynamic-range sweep)
PRIME (primary): prime_small (5,7,11) M=385 | prime_mid (13,17,19) M=4199 | prime_large (37,41,43) M=65231.
COMPOSITE (prime-necessity probe): composite (8,9,25) M=1800 (all composite, pairwise coprime).
N=8192, R=3, sb=2730. Seeds (7,13,19).

## PRIME-NECESSITY FINDING (honest, MEASURED -- inverts the drill's prediction 3)
The drill HYPOTHESIZED@ that the star operator "requires PRIMES" and pre-registered a composite-modulus control
that "collapses to <=0.15", framing non-collapse as "prime-cyclicity is not actually load-bearing at substrate
scale." A pre-dispatch numerical probe + smoke both MEASURED that decode-then-exponentiate multiply is EXACT
(1.000) for composite moduli (8,9,25) exactly as for primes. **Prime-cyclicity is NOT load-bearing for
decode-then-exponentiate** -- it is a property of the drill's REJECTED discrete-log/index-calculus route (which
needs a cyclic multiplicative group), not of this operator. THEORETICAL: `w^(a*b) = codebook[(a*b) mod m]` holds
for ANY m with integer k_j; primes only matter when residues are represented by discrete logs. The composite
regime is therefore reported as a PRIME-NECESSITY PROBE (an honest negative-control that did NOT fire), NOT a
pass-gated must-collapse arm. Primary HARD_PASS is on the 3 all-prime regimes (drill convention).

## Pre-registered bands
| Metric | HARD-PASS | HARD-FAIL |
|---|---|---|
| `star_multiply` exact-multiply, PRIME regimes (min) | >= 0.99, cv <= 0.10 | < 0.60 at any regime |
| each collapsing control (bind/rand_exp/rand_cb/scram), PRIME regimes (max) | <= 0.15 | >= 0.40 (leak) |
| `mult_chain` depth-3 exact (min) | >= 0.75 | < 0.20 |
| `equality_check` accept-correct (min) | >= 0.99 | -- |
| `equality_check` reject-incorrect (min) | >= 0.99 | -- |
| composite regime `star_multiply` (min) -- prime-necessity probe | >= 0.90 => PRIME_NOT_REQUIRED (finding, reported not gated) | -- |
| near-miss frac (runner-up <= 0.5*rank1) | >= 0.90 (is-math-easier probe; reported, not gated) | -- |

## SCHEMA-VET fields
- **Compute architecture:** `(b) sequential-CPU with justification`. numpy complex64; smoke MEASURED 3.3s;
  full est ~30-40s. Carve-outs: cell IS the substrate-primitive being validated (bit-exact reference) AND
  total wall << the 10s-per-phase-point batching threshold per-unit. No GPU speedup relevant (per-trial work
  ~3 sub-blocks x elementwise power over sb=2730). No batching required.
- **Storage strategy:** `no_storage_algebraic_star`. Composition is via the star operator (elementwise
  integer-power); the result IS exactly the codeword of the product (a single valid value), not a
  superposition of items to be separately retrieved -> sharded/bundled rule N/A.
- **cardinality_ok:** EXPECTED_N_UNITS = n_regimes * n_seeds * (5 single + n_depths + 1 eq). Gated; smoke
  MEASURED 108/108 (4 regimes x 3 seeds x (5 + 3 + 1)).
- **arms_differ_verified:** phase codebook hash != random codebook hash; star_multiply recovered integers hash
  != scrambled recovered integers hash; star_multiply integers hash != bind_not_power (additive) integers
  hash. MEASURED True. (Truth-integer arrays never hash-compared -- an exact multiplier and a broken one both
  know truth; we hash CODEBOOKS and RECOVERED-integer arrays, which differ: star recovers a*b, bind recovers
  a+b, scram recovers permuted-CRT.)
- **final_metrics_atomicity:** `tmp_replace` (metrics.json.tmp -> os.replace).
- **except ordering:** `except SystemExit: raise` before `except Exception` (no BaseException, no bare except).
  Grep gate MEASURED clean.
- **crlb / discriminator_reachability:** True. Per-residue argmax over m_i<=43 candidates in sb=2730
  sub-block; SNR ~ sqrt(sb) rank-1 vs ~1/sqrt(sb) runner-up; sb >> max modulus -> collision-free. Exponent
  <= m_i-1 <= 42; z^n stays exactly unit-modulus -> no precision floor gates the 0.99 exact-multiply target.
- **baseline_in_band (META_RULE_AG):** N/A -- exactness/correctness test, not a difficulty sweep. Mechanism
  expected ~1.0 by exact residue-multiply construction; the 4 controls are declared CONTROLS intentionally
  ~0.0 (exempt, same carve-out as the landed add cell). Discriminator = CONTRAST mechanism(~1.0) vs
  controls(~0.0); does NOT saturate at scale (controls -> 1/M as M grows).
- **discriminator survives scale:** option A -- smoke runs at FULL N=8192, FULL sb=2730, ALL 4 regimes; only
  trials/seeds/depths reduced. mechanism-exact + 4-controls-collapse + chain-exact + equality-crisp +
  composite-exact-probe all FIRE in smoke (MEASURED).
- **run_mode verification:** metrics assert run_mode==mode; smoke landed run_mode=smoke HARD_PASS.
- **defensive error-checking:** start_marker + heartbeat + crash-diagnostic + atomic metrics = passed_all_4.
- **progress_logging:** `line_buffered_stdout` (sys.stdout.reconfigure line_buffering + per-unit flush). N/A
  as mandatory (wall << 1800s) but present.
- **positive_control (gate D):** CRT decode + multiply-homomorphism reproduced AT TEST REGIME via
  `crt_selftest` + `multiply_homomorphism_selftest` (decode(star_multiply(enc(a),enc(b)))==(a*b) mod M, plus
  multiplicative-zero and multiplicative-identity checks) run for EVERY regime before arms; both MEASURED PASS
  all modes.
- **functional_requirements (gate E):**
  1. exact modular multiplication -> star operator (decode one operand + elementwise integer-power) on the
     landed phase-linear encoding (this cell's new ~120-line increment).
  2. multi-step product derivation -> repeated star (running ** decoded next term); reuses running-vector bookkeeping.
  3. modular wraparound -> handled at encoding (integer freqs -> exact period-m) + CRT reconstruction (landed CG).
  4. exact product-equality-check -> discrete decode-and-compare (CRT integer ==), not cosine; the self-reasoning primitive.
- **effective_vs_nominal (gate A):** ALIGNED. Swept axis = M (moduli product); each primitive experiences the
  same M (no partition routing dilutes it).
- **discriminating_fraction (gate B):** the discriminator is a CONTRAST (mechanism~1.0 vs controls~0.0), not a
  sweep landing in [0.3,0.7]; N/A by cell-type (correctness/homomorphism test, declared).

## SMOKE RESULT (MEASURED@data/exp_math_rns_multiply_star_v1/metrics.json)
HARD_PASS (wall 3.3s). All 4 regimes x 3 seeds: star_multiply=1.000 (cv=0.000); all 4 controls collapse
(bind=0.000, random_exponent<=0.050, random_codebook=0.000, scrambled_modulus<=0.050; ctrl_max=0.025 over prime
regimes); multiply chains d1/d3/d5=1.000; equality accept=1.000 reject=1.000; near-miss frac=1.000.
Composite regime (8,9,25) star_multiply=1.000 -> **PRIME_NOT_REQUIRED**. Demos (M=385): 3*4=12, 7*11=77,
20*20=15 (WRAP 400 mod 385), 50*50=190 (WRAP), 100*100=375 (WRAP) -- all exact.

## FULL staging
FULL = same 4 regimes, seeds (7,13,19), trials=300, depths (1,3,5,10). CPU-scale (numpy, est ~30-40s), zero
referent (self-contained synthetic codebooks) -> clean gate. Per USER-lock FULL must NOT go to
local_cpu_queue (SMOKE-only on local); canonical run = remote landing. Route FULL to `remote_cpu_queue` via
Orchestrator (push to origin/main required; harness-denied to exp_dev). Timeout: 900s (generous; expected ~40s).
