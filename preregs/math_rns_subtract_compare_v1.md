# PRE-REG: exp_math_rns_subtract_compare_v1

**Cell:** `experiments/exp_math_rns_subtract_compare_v1.py`
**Anchor:** `math_rns_subtract_compare_v1`
**Author:** exp_dev  **Date:** 2026-07-05
**Source pre-regs (bands + mechanism):**
- `notes/research_math_arithmetic_basis_next_primitives_2026-07-05.md` (Q2/Q3/Q4: subtract-is-free,
  half-range sign detection, build order + bands)
- `notes/research_entailment_self_check_first_cell_2026-07-05.md` + handoff
  `notes/exp_dev_handoff_research_entailment_self_check_first_cell_2026-07-05.md` (folded in via coordinator
  SendMessage: native-signtest prior-negative recheck, decode-then-compare honesty baseline, a>=threshold target)

**Prior-work check (substrate KB):** top hits at cosine 0.3213/0.3203 are chunks of the 06-23 RNS-arithmetic
LITERATURE drill (`notes/research_drill_residue_arithmetic_vsa_compound_predicates_2026-06-23.md` Stream D:
MRC / core-function / diagonal-function comparison surveys) -- a lit-scan note, NOT a landed capability cell.
Genuinely novel as a CELL (no prior landed subtract/compare capability cell). Rediscovery relative to classical
RNS literature, which both math drills already scoured; half-range sign-detection is the 07-05 drill's
recommended cheapest-correct v1 (simpler than the surveyed MRC/core-function). Reuses the phase-linear codebook
+ CRT decode from `exp_math_rns_add_chain_v1` (FULL HARD_PASS exact-add=1.000) VERBATIM.

## Claim
1. SUBTRACTION is a free corollary of the exact additive group homomorphism: `enc(a) (*) conj(enc(b)) ==
   enc((a-b) mod M)` (conjugation is the additive inverse). Decode via the proven per-sub-block phasor argmax
   + CRT. Exact incl modular wraparound; multi-step subtract chains hold.
2. NUMERIC-THRESHOLD three-way COMPARISON (a<b / a==b / a>b, i.e. does a>=threshold) is achievable. HONESTY
   GATE: the mechanism-of-record is `decode_then_compare` (decode both operands via exact CRT, compare in
   scalar space) -- exact, full-range. The residue-native `half-range sign detection` (one decode of the
   difference, threshold vs M/2) MATCHES the baseline within |a-b|<M/2 but adds NO accuracy and is strictly
   worse out-of-range. Decode-SKIPPING comparators FAIL (residues/single channels carry no order).

## Arms (all PAIRED on identical integer pairs per regime/seed)
SUBTRACT:
- `sub_phase` [MECHANISM] -- conjugate-bind subtract; decode=argmax+CRT. Exact (a-b) mod M incl wraparound.
- `sub_random` [CONTROL] -- IDENTICAL pipeline, random-per-(r,j) phasors (not linear in r) -> no homomorphism.
  Isolates phase-LINEARITY (stronger than random-real: everything held constant except linearity).
- `sub_scram` [CONTROL] -- arm phasor decode then DERANGE residues before CRT -> reconstruction collapse.
- `add_inverse_id` [PRIMITIVE] -- decode(subtract(enc(a),enc(a)))==0 for all a (conjugation cancels exactly).
- `sub_chain` [MECHANISM] -- subtract over an L-step running-difference chain, L in {1,3,5,10}.
COMPARE (three-way; in-range a,b in [0,M//2)):
- `decode_then_compare` [STRONG BASELINE / mechanism-of-record] -- decode a,b separately, compare integers.
  Exact, FULL-range, no M/2 caveat. THE honest bar every residue-native comparator is judged against.
- `compare_halfrange` [MECHANISM UNDER TEST] -- decode the single difference d, threshold vs M//2. Reports
  3-way accuracy + ORDERING sub-accuracy + LIFT over baseline (expected ~0.000).
- `native_vector_signtest` [CONTROL / PRIOR-NEGATIVE recheck] -- single-channel sign read (decode ONLY residue
  0, half-range on m0; NO full CRT reconstruction). Discrete-rep analog of the closed FULL HARD_FAIL
  `exp_comparator_resonator_primitive_smoke_v1` sign-test (comp_acc=0.8556 < raw=0.8944). Informs whether the
  historical negative was FPE-specific or mechanism-general. Expected ~chance ORDERING.
- `compare_order_blind` [CONTROL] -- order from raw residue tuple lexicographically. EQ exact; ORDERING ~chance.
- `compare_random` [CONTROL] -- half-range rule on random-codebook (garbage) decode. ~chance.
- `eq_detect` [PRIMITIVE] -- a==b correctly labeled EQ by the decode mechanism.
REPORTED (not pass-gated on their own):
- `compare_out_of_range` -- |a-b| >= M//2: half-range mis-sign rate (documented limitation) AND
  decode_then_compare accuracy (~1.0; the baseline is unaffected -> strictly safer). Per the handoff's
  named HARD-FAIL trigger, the range violation is REPORTED, not silently mis-signed.
- `compare_near_boundary` -- |a-b| just below M//2: half-range accuracy (fragility probe). Expected 1.0.
- `threshold_entailment` -- does value >= threshold hold, over realistic (metric,threshold) pairs (self-VET target).

## Regimes (dynamic-range sweep, >=3 moduli-products; reused verbatim from the add cell)
small (7,8,9) M=504 half=252 | mid (16,17,19) M=5168 half=2584 | large (40,41,43) M=70520 half=35260.
N=8192, R=3, sb=2730. Seeds (7,13,19). Half-range precondition M > 2*max_operand_range satisfied: compare
operands drawn from [0, M//2) so |a-b| < M/2 strictly (never d==M/2).

## Pre-registered bands
| Metric | HARD-PASS | HARD-FAIL |
|---|---|---|
| `sub_phase` exact-subtract (min over regimes) | >= 0.99, cv <= 0.10 | < 0.60 at any regime |
| `sub_random` exact-subtract (max) | <= 0.15 | >= 0.40 (leak) |
| `sub_scram` exact-subtract (max) | <= 0.05 | -- |
| `add_inverse_id` (min) | >= 0.99 | -- |
| `decode_then_compare` 3-way (min) [mechanism-of-record] | >= 0.99, ordering >= 0.99 | < 0.70 (deep breakage) |
| `compare_halfrange` 3-way in-range (min) | >= 0.99, ordering >= 0.99 | -- (informational vs baseline) |
| half-range lift over baseline (\|lift\|) | ~0.00 (report; the honesty finding: adds no accuracy) | -- |
| decode-SKIPPING ORDERING (native_signtest / order_blind, max) | <= 0.72 (collapse to chance 0.5) | > 0.72 -> residues leak order / decode not load-bearing |
| `eq_detect` (min) | >= 0.99 | -- |
| `threshold_entailment` a>=threshold (min) | >= 0.99 | -- |
| `sub_chain` depth-3 exact (min) | >= 0.75 | < 0.20 |
| `compare_out_of_range` half-range mis-sign | REPORTED (not silent); baseline_acc ~1.0 | range-violation silently mis-signs >50% WITHOUT report |
| `compare_near_boundary` half-range acc (min) | >= 0.99 (no fragility within range) | -- |
| near-miss frac (runner-up <= 0.5*rank1) | >= 0.90 (is-math-easier probe; reported) | -- |

## SCHEMA-VET fields
- **Compute architecture:** `(b) sequential-CPU with justification`. numpy complex64; wall MEASURED 2.9s smoke.
  Carve-outs: cell IS the substrate-primitive being validated (bit-exact reference) AND total wall < 15s.
  No GPU speedup relevant (per-trial work ~3*60*2730 flops). No batching required.
- **Storage strategy:** `no_storage_algebraic_bind`. Composition via BIND / conjugate-BIND; composite IS
  exactly the codeword of the sum/difference (single valid value), not a superposition. sharded/bundled N/A.
- **cardinality_ok:** EXPECTED_N_UNITS = n_regimes*n_seeds*(4 subtract + n_depths chain + 6 compare + 3 reported).
  Gated; smoke MEASURED 144/144.
- **arms_differ_verified:** phase codebook hash != random codebook hash; arm subtract-recovered integers hash
  != scrambled recovered integers hash; half-range predictions hash != native_signtest AND != order_blind
  predictions. MEASURED True. EXEMPT pair `arms_differ_exempted=[[decode_then_compare, compare_halfrange]]`:
  both exact -> IDENTICAL correct labels by construction (that identity IS the honesty finding, not a bug).
- **final_metrics_atomicity:** `tmp_replace` (metrics.json.tmp -> os.replace).
- **except ordering:** `except SystemExit: raise` before `except Exception` (no BaseException, no bare except).
- **crlb / discriminator_reachability:** True. Per-residue argmax over m_i<=43 candidates in sb=2730 sub-block;
  SNR ~ sqrt(sb) rank-1 vs ~1/sqrt(sb) runner-up; sb >> max modulus -> collision-free; no noise floor gates 0.99.
- **baseline_in_band (META_RULE_AG):** N/A -- exactness/correctness test, not a difficulty sweep. sub_phase and
  decode_then_compare expected ~1.0 by exact CRT construction; subtract controls (random/scram) intentionally
  ~0.0; decode-SKIPPING compare controls intentionally ~chance ORDERING (exempt as declared controls). The
  discriminators are CONTRASTS (decode-based ~1.0 vs decode-skipping ~0.5; phase ~1.0 vs random ~0.0) and do
  NOT saturate at scale (random-subtract -> 1/M; decode-skipping ordering stays ~0.5 as M grows).
- **discriminator survives scale:** option A -- smoke runs at FULL N=8192, FULL sb=2730, ALL 3 regimes; only
  trials/seeds/depths reduced. sub-exact + random-collapse + scram-collapse + baseline-exact + halfrange-exact
  + native_signtest-collapse + order_blind-collapse + chain-exact all FIRE in smoke.
- **run_mode verification:** metrics assert run_mode==mode; smoke landed run_mode=smoke, size 33034B, 2.87s.
- **defensive error-checking:** start_marker + heartbeat + crash-diagnostic + atomic metrics = passed_all_4.
- **progress_logging:** N/A (wall < 15s; not a timeout_s>=1800 cell).
- **positive_control (gate D):** CRT decode reproduced AT TEST REGIME via `crt_selftest` + a per-regime
  `subtract_homomorphism_selftest` (decode(subtract(enc(a),enc(b)))==(a-b) mod M, add-inverse==0) +
  `compare_selftest` (half-range AND decode_then_compare == true 3-way; a decode-skip control diverges) run for
  EVERY regime before arms; all MEASURED PASS all modes.
- **functional_requirements (gate E):**
  1. exact subtraction -> conjugate-phasor bind (this cell's ~15-line increment over the add cell).
  2. multi-step derivation -> repeated conjugate-bind (associative group op); reuses running-product bookkeeping.
  3. modular wraparound -> handled at encoding (integer freqs -> exact period-m) + CRT (landed CG).
  4. numeric-threshold ordering (a>=threshold) -> decode_then_compare (mechanism-of-record) with half-range as
     validated range-limited efficiency variant; the self-VET primitive.
- **effective_vs_nominal (gate A):** ALIGNED. Swept axis = M (moduli product); each primitive experiences the
  same M (no partition routing dilutes it).
- **discriminating_fraction (gate B):** the discriminators are CONTRASTS (decode-based vs decode-skipping; phase
  vs random), not a sweep landing in [0.3,0.7]; N/A by cell-type (correctness/honesty test, declared).
- **signal_shape_compatibility (gate C):** subtract output vector -> decode input vector = SHAPE_MATCH (identical
  full-N complex64 as the add cell's bind output). No adapter needed.

## Honesty framing (coordinator SendMessage, folded in)
This cell does NOT over-claim half-range as a novel capability. In THIS substrate the CRT decode is exact, so
`decode_then_compare` already solves numeric-threshold comparison exactly over the full range. Half-range sign
detection is validated as a CORRECT, range-limited efficiency variant that MATCHES (does not exceed) the
baseline within |a-b|<M/2 and is strictly worse out-of-range (silent mis-sign). The prior FULL HARD_FAIL
comparator negative (native vector-space sign-test adds no lift over naive decode) is REPRODUCED here via the
`native_vector_signtest` control on the discrete rep -> the negative is mechanism-general (the decode is what
does the work), not FPE-specific. DESIGN FINDING (reported, not forced): no new residue-native comparison
mechanism is needed for correctness; the value is the honest confirmation that the substrate CAN do exact
subtraction + numeric-threshold comparison, attributable to the exact decode. Tier (likely by-construction /
MEASURED_MECHANISM, like the add cell -- exactness is by construction) is the VET's call.

## SMOKE RESULT (MEASURED@data/exp_math_rns_subtract_compare_v1/metrics.json)
HARD_PASS. All 3 regimes x 3 seeds at FULL N=8192, wall 2.87s:
- sub_phase=1.000 (cv=0.000), sub_random=0.000, sub_scram max=0.0056, add_inverse_id=1.000.
- sub_chain d1/d3/d5=1.000.
- decode_then_compare 3-way=1.000 (ordering 1.000); compare_halfrange 3-way=1.000 (ordering 1.000), lift=+0.000.
- native_vector_signtest ordering ~0.43-0.52; compare_order_blind ordering ~0.47-0.55 (max 0.650 over all seeds,
  <= 0.72 gate); order_gap=0.350.
- eq_detect=1.000; threshold_entailment=1.000; near_boundary=1.000.
- compare_out_of_range: half-range mis-sign ~0.99-1.00 (REPORTED limitation), baseline_acc=1.000 (safe).
- Demos (M=504): 12-5=7, 5-12=497(WRAP), 7-7=0, 250-100=150, 2-503=3(WRAP); 12vsGT/5vs12 LT/7vs7 EQ; threshold
  (large, /10000): 8860>=8000 True, 7200>=8000 False, 8000>=8000 True, 9500>=9000 True, 7990>=8000 False -- all exact.

## FULL staging
FULL = same 3 regimes, seeds (7,13,19), trials=300, depths (1,3,5,10). LOCAL-CPU-feasible (~10-15s) but per
USER-lock FULL must NOT go to local_cpu_queue (SMOKE-only on local); canonical run = remote landing. Route
FULL to `remote_cpu_queue` via Orchestrator (push to origin/main required; harness-denied to exp_dev).
Timeout: 600s (generous; expected ~15s).

## DEFERRED (NOT this cell; per handoff anchor #3)
Tier-2: wire the validated comparator onto real (measured_metric, HARD-PASS threshold, recorded verdict)
triples pulled from `preregs/*.md` + `data/*/metrics.json`, retrieved via `exp_cert_ledger_self_query_v1`'s
KG-retrieval -- the full "substrate checks its own certification claims" loop. Build AFTER this cell's FULL verdict.
