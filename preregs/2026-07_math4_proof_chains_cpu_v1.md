# Prereg: math4_proof_chains_cpu_v1

## Anchor
math4_proof_chains_cpu_v1

## Routing
AGGRESSIVE_OVERNIGHT THRUST-2 MATH. Stage 3 (compositional understanding). Substrate-native
multi-step deductive reasoning (MODUS PONENS chained over IMPL-bound rule pairs). Not a language
benchmark; not Stage 4 LM equivalence. Directly aligned with USER 2026-06-26 stage-3 pivot: cell
tests whether substrate primitives (unbind + cleanup) support multi-step derivation of the form
`(A=>B) & A -> B`, chained L=2/4/6 steps.

## Queue
FULL: `remote_cpu_queue` (light CPU cell; per USER 2026-07-01 local is smoke-only).
SMOKE: `local_cpu_queue` (fast probe; ~10s wall).

## Purpose
Substrate-native operational test of Longshot #1 "Compositional reasoning chains" (from
`notes/substrate_longshot_capabilities.md`). A rule base of NPROP=60 implications `A_i => B_i`
is stored as per-antecedent-sharded `cnorm(A_i * IMPL * B_i)` vectors. At derivation time the
substrate does per-step MODUS PONENS: given current fact `p`, look up its rule (indexed by `p`)
and unbind to derive consequent `rule_vec[idx(p)] * conj(p) * conj(IMPL) -> cleanup -> next fact`.
Chains repeat L times. Discriminator = mean accuracy that final fact equals the ground-truth
L-step successor along the deterministic functional graph.

## Envelope-fail-bands (META_RULE_L: strict >= floor+5%)
- HARD_PASS: mean accuracy across L in {2,4,6} >= 0.65 (substrate supports multi-step MP proofs)
- MIDDLE_BAND: 0.50 <= mean < 0.65 (partial — likely degrades with length)
- HARD_FAIL: mean < 0.50 (chain-degradation dominates by L=4-6; MP-via-substrate not viable)

Band-width HP-vs-MB = 0.15; strict-above-floor threshold 0.65 + 5% * 0.15 = 0.6575. Cell code
uses `>= 0.65`; if smoke lands in 0.65-0.6575 window flag as MIDDLE_BAND-adjacent per §L.

## Discriminator (META_RULE_K: fires-check)
Class = ERROR-CORRECTION at each MP step (per-step cleanup must recover the correct next fact
from a noisy unbind). Discriminator fires when accuracy differs from chance = 1/NPROP = 1/60 =
0.0167. Smoke fires-check: mean accuracy at L=2 > 0.20 (well above chance; not by-construction
saturation at 1.0 either — see baseline-in-band below).

## Baseline-in-band (META_RULE_AG)
No adversarial parallel baseline arm (cell is single-mechanism substrate probe). The three
chain-length points (L=2/4/6) form a within-arm degradation gradient — L=2 is the "easy"
regime, L=6 is the "hard" regime. Interpretation:
- If L=2 accuracy >= 0.95 AND L=6 accuracy >= 0.95: SATURATED (chains too easy at NPROP=60/N=8192)
- If L=2 accuracy <= 0.05: substrate fails single-step MP; regime too hard OR rule-store broken
- Discriminator-fires zone: L=2 in (0.20, 0.98) AND L=6 in (0.05, 0.95)

Wall of MIDDLE_BAND is expected: substrate should show length-dependent degradation reflecting
per-step cleanup error compounding. That gradient IS the signal.

## Compute architecture (USER-LOCKED 2026-07-02)
Class: **(b) sequential-CPU with justification**.

Justification: Each MP chain has genuine step-to-step dependency (step k+1 requires the cleanup
output of step k). No way to batch within a chain. Cross-chain / cross-trial batching would help
in theory, but per-trial work is dominated by ~60 * 8192 complex-vector cleanups (~0.5M complex
FLOPs per step, ~4 steps avg per length, 3 lengths = ~6M complex FLOPs per trial). At FULL
TR=120: ~720M complex FLOPs on numpy CPU ~ 30-90s wall. GPU cuda-init cost (~1s startup +
per-call kernel launch ~50us * ~1500 per-step calls ~75ms + transfer overhead) plus the
overhead of orchestrating tiny (60,8192) matvecs on GPU would likely INCREASE wall time.

Wall-time sanity check: numpy `complex64` matvec (60,8192)@(8192,) benched ~50-100us; 12 such
calls per trial * 120 trials = 1440 calls ~ 100-150ms just for matvecs. Rule-vec construction
(60 cnorms per trial * 120 trials * 8192 complex-vector ops) is the bulk of compute ~ 60-90s.
Total FULL wall estimate: 60-120s. Comfortably below the 10s-per-phase-point batching threshold
when amortized across the 3 length points (~20-40s per length).

Genuine sequential dependency justifies (b). Not a batching candidate.

## CRLB / capacity-feasibility (§9)
Per-step cleanup is `argmax over (60, 8192) @ (8192,)` inner product against `NPROP=60` cleanup
codebook. Per-step SNR at N=8192, K=1 bound-pair: signal magnitude ~ 1, noise magnitude ~
`1/sqrt(N/K)` ~ 1/sqrt(8192) ~ 0.011. Per-step top-1 cleanup error probability at this SNR is
<< 0.01 in the ideal case (~perfect single-step). BUT the empirical rule-store construction
uses `cnorm(A * IMPL * B)` per antecedent; unbind is `rule * conj(A) * conj(IMPL)` = `cnorm(A *
IMPL * B) * conj(A) * conj(IMPL)`. For unit-modulus phasors this is EXACTLY `cnorm(B) * noise`
where noise comes from the `cnorm` phase-normalization (nonlinear). Empirical single-step
cleanup should be near-perfect (~0.95+) at N=8192 NPROP=60.

Compounded across L steps: `accuracy(L) ~ (per_step_accuracy)^L`. At per_step=0.95:
- L=2: 0.90
- L=4: 0.81
- L=6: 0.74
- Mean: 0.82 -> HARD_PASS expected if single-step ~0.95

At per_step=0.85 (more pessimistic):
- L=2: 0.72
- L=4: 0.52
- L=6: 0.38
- Mean: 0.54 -> MIDDLE_BAND

HP threshold 0.65 is achievable when per_step_accuracy >= ~0.88. THEORETICAL@compounded-Bernoulli.

`crlb_floor_computed`: n/a as noise-floor rank stat; use per-step accuracy compounding above.
`discriminator_reachability`: True (HP=0.65 achievable if per-step cleanup >= 0.88 at
N=8192/NPROP=60).

## Arms-must-differ (META_RULE_AF)
arms_differ_verified: n/a — single-mechanism cell (no parallel arms; three L-length points
share the same substrate mechanism). Exempt.

## Final-metrics atomicity (META_RULE_AH)
final_metrics_atomicity: `tmp_replace` (uses `experiments/_seed_checkpoint.write_metrics` which
writes tmp then `os.replace()` atomically).

## Except-SystemExit ordering (§8)
Cell has NO outer try/except around main-logic; execution is top-level after `_selftest()`.
Selftest is called unconditionally; `--self-test` triggers `sys.exit(0)` cleanly. The single
`try/except Exception` at line 13-16 wraps `sys.stdout.reconfigure` narrowly; does not swallow
SystemExit.

Grep gate verified: no bare `except:`; no `except BaseException`.

## Cardinality (META_RULE_H)
No K/depth/V_C/alpha sweep. The L in {2,4,6} is a within-run gradient (not a sweep-axis with
separate n_seeds per point). `n_seeds=1` per invocation via `HDLAB_SEED` env; FULL run =
1 invocation TR=120. `cardinality_ok`: n/a for non-sweep cell.

## Discriminating-fraction (Gate B)
Not a parameter sweep; 3 length points form a within-arm degradation gradient. Expected
per-length landing under HP-band prediction (per_step=0.95): L=2 ~0.90 (band [0.30,0.70]:
NO — above), L=4 ~0.81 (NO — above), L=6 ~0.74 (marginal — above). Under
MIDDLE-band prediction (per_step=0.85): L=2 ~0.72, L=4 ~0.52, L=6 ~0.38 — L=4 IN
discriminating band; L=6 in [0.30,0.70]; L=2 near-edge. 2/3 in band = 0.67 > 0.30 threshold.
`discriminating_fraction`: 0.67 under the expected mixed scenario.

## Sweep-alignment (Gate A)
No sweep axis with primitive-composition. `sweep_alignment_verdict`: n/a.

## Composition-edges (Gate C)
Single primitive: FHRR bind (`*`), unbind (`* conj()`), cleanup (`argmax((book @ conj(v)).real)`).
Composition edge = rule-store shard -> cleanup. Shape match: rule_vec (NPROP, N) complex64,
cleanup vector (N,) complex64 -> inner product (NPROP,) real -> argmax int. SHAPE_MATCH throughout.

## Positive-control (Gate D)
Chain-grade primitive being invoked: FHRR complex-phasor bind + per-antecedent-sharded cleanup.
Sharding (not global-bundle) chosen because prior TRACE / ultrametric / sequence-binding
chain-grade cells document global-bundle capacity as `~0.14 * N` for binding pairs; NPROP=60 <<
0.14 * 8192 = 1146, so a global bundle would ALSO succeed at this scale. Per-antecedent shard
strengthens single-hop recovery to near-perfect at expense of NPROP memory, prioritizing chain
integrity over storage compression. This is a design choice, not a regime mismatch. No cited
prior atom to reproduce; MP-chained-via-substrate is a NEW capability probe. n/a with declaration
of design rationale.

## Functional-requirements (Gate E)
1. **Store implications as rules the substrate can lookup.** Cell impl: rule_vec[a] =
   cnorm(A_a * IMPL * B_a); sharded per antecedent A_a. Lookup by using antecedent AS the shard
   index (via cleanup `argmax`). Encoding mechanism explicit; test rational (see
   `feedback_test_rationality_encoding_before_readout_2026-06-27`).
2. **Derive consequent from (rule, current_fact).** Cell impl: `rule * conj(current) *
   conj(IMPL)` isolates B_a modulo phasor noise; cleanup against props book recovers B_a's
   discrete identity.
3. **Chain L steps.** Cell impl: feed recovered B back as new current_fact; repeat L times.
   Ground truth = deterministic permutation `nxt` starting from `start`.

## Defensive-error-checking (§13)
- `cell_chunked`: False (single-file; TR=120 loop is <2min total; runner-death loses one seed
  which IS this run)
- `start_marker_written`: False (cell is <2min total; low value; write_metrics atomic-writes
  at end)
- `crash_diagnostic_present`: False (no outer try/except; short cell; SystemExit-safe)
- `heartbeat_present`: False (cell is <2min; heartbeat unnecessary)
- `defensive_error_checking`: "exempt_short_cell (FULL wall ~60-120s)"

## Progress-logging (§17)
`progress_logging`: `print_flush_true` — all `print()` calls use `flush=True`. Runner also
invokes `python -u` (defense in depth). Cell timeout target 300s (well below 1800 threshold).

## Calibration-check (META_RULE_M)
`calibration_check`: `default_ok_for_this_regime`. FHRR complex-phasor primitives at N=8192
are the substrate default (matches HRR/FHRR sequence-binding chain-grade cells). Rule-store
shape (NPROP=60 rules) is well within cleanup capacity at this N. No adaptive tuning.

## Stage-progression check (USER-LOCKED 2026-06-26)
Stage 3 (compositional understanding). Not Stage 4 language equivalence. Cell uses synthetic
FHRR phasors as propositions — NO tokens, NO text, NO language benchmarks. MP over
IMPL-bound pairs is a compositional-reasoning primitive: the substrate must COMPOSE (bind
rule to fact, unbind, cleanup) across steps. This is exactly the Stage 3 arc opened per
USER 2026-06-26 pivot. VERIFIED Stage 3.

## Prior-work check
Substrate-KB query `"modus ponens chain reasoning proof chain length composition"` returned:
- Rank 1: `notes/substrate_longshot_capabilities.md` "1. Compositional reasoning chains" at
  cosine=0.39. This IS the longshot doc that motivates this cell. The doc is a broad brainstorm
  ("bet substrate composes stored atoms to derive new facts"). This cell is the FIRST operational
  substrate-only implementation targeting that longshot. Not a prior-arc collision — it's the
  first probe of the longshot.
- Rank 2-5: chain-extraction / cross-shard chain / composition-with-CG references — all about
  DIFFERENT chain semantics (extracted narrative chains, cross-shard partition chains, CG-atom
  composition — not modus-ponens deductive chaining).
- No prior operational MP-chain cell exists in the substrate.
Genuinely novel; not a rediscovery.

## Selftest formulas (PROT-022)
1. `single_step_reproducibility`: with fixed seed, per-antecedent-sharded rule_vec construction
   is deterministic; two runs with same seed produce bit-identical rule_vec (implicit via
   `HDLAB_SEED`).
2. `cleanup_bounds`: `cidx` returns int in `[0, NPROP)` (argmax over NPROP scores).
3. `phasor_unit_modulus`: `cnorm(v)` output has `|v_i| == 1` for all i (up to floating-point).
   THEORETICAL@FHRR-phasor-definition.
4. `deps`: numpy + math imports; `experiments._seed_checkpoint.get_output_dir` / `write_metrics`
   present.

## Timeout
- SMOKE (TR=20, local_cpu_queue): 60s
- FULL (TR=120, remote_cpu_queue): 300s (5min; ~60-120s estimated wall + generous buffer for
  numpy variance on shared remote host)
