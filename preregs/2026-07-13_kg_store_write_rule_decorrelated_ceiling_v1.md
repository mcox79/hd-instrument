# Pre-registration: DECORRELATED WRITE RULE raises the native representational CEILING (glass-box, zero-SGD)

- **Cell:** `experiments/exp_kg_store_write_rule_decorrelated_ceiling_v1.py`
- **Anchor name:** `kg_store_write_rule_decorrelated_ceiling_v1`
- **Metrics path:** `data/exp_kg_store_write_rule_decorrelated_ceiling_v1/metrics.json`
- **Filed:** 2026-07-13 (exp_dev). **Target queue:** `remote_cpu_queue` (one-shot closed-form solve, no SGD -> CPU-cheap).
- **Source of design:** `notes/research_native_representational_ceiling_levers_2026-07-13.md` (lever #1, cheap decisive test Anchor A).

## Prior-work check (mandatory)
`bash tools/substrate_query.sh "decorrelating write rule pseudoinverse storkey associative memory capacity ceiling"`
-> top hit cosine **0.316** (`Modern Hopfield / dense associative memory capacity`, a research lit-scan note, generic);
2nd 0.316 same note chunk; 3rd/4th `assortative mating` (0.289, spurious wordnet); 5th
`hebb_vs_pseudoinverse_write_rule_v1` metrics at **0.286** (below the 0.30 gate but directly relevant, and named by the
task). **Prior-work check: at cosine>0.30 only GENERIC associative-memory-capacity lit notes; NO prior arc cell tests a
decorrelated write rule inside the LIVE KGStore native-bind compose harness.** The prior pinv cells
(`hebb_vs_pseudoinverse_write_rule_v1` HARD_PASS 8x, `pseudoinverse_real_encoder_keys_v1`, `wave14_pseudoinverse_capacity_v1`)
are AUTOassociative capacity micro-tests (`W = P^T (PP^T)^-1 P`, project onto pattern span). This cell is the genuinely
novel application of the HETEROassociative decorrelated solve (`W = Cross @ inv(Gram+ridge)`, key -> E[o]) INSIDE the
CERT-584/585 KGStore native-bind inductive-compose harness, measuring the ORACLE-CEILING rise. Not a rediscovery: the
prior cells proved the lever exists on synthetic autoassoc; this measures whether it raises THIS store's task ceiling.

## Question
Does swapping the store's naive one-shot Hebbian write rule (`W += outer(E[o], key)/n_dim`, ~0.14N capacity) for a
DECORRELATING closed-form least-squares (pseudo-inverse / Widrow-Hoff) write rule RAISE the substrate's native
ORACLE ceiling + native inductive MRR toward the additive level -- WITHOUT any gradient descent (stays glass-box)?
- **HARD-PASS** => the write rule is the dominant ceiling lever; the substrate CAN carry the optimized magnitude with a
  purely-linear-algebra write; nativize side of optimize-then-nativize is de-risked.
- **HARD-FAIL** => ceiling barely moves; write rule is NOT the lever / a native magnitude wall; redirect to the code-side
  (DG sparse front-end) lever.
Either outcome is decisive.

## Mechanism / construction (the crux; only the WRITE RULE changes)
Re-run the EXACT `exp_native_bind_compose_inductive_entity_cskg_v1` 7-arm harness (split / planted arena / compose /
readout / localization / verdict REUSED VERBATIM via import) on a BIT-IDENTICAL seed-deterministic split, under two rules:
```
hebbian : the current KGStore Hebbian W (untouched path; positive-control reproducer of the landed 0.0231 oracle).
pinv    : W minimizes sum_i ||W k_i - E[o_i]||^2 + ridge||W||^2 over the SAME triple stream.
          Closed form:  W = Cross @ inv(Gram + ridge*I)
              Cross = sum_i outer(E[o_i], k_i)   [n_dim x n_dim]   (streaming, same shape as the Hebbian pass)
              Gram  = sum_i outer(k_i,   k_i)     [n_dim x n_dim]
          then ONE dense linalg.solve. k_i = E[s_i]*R[p_i]*sqrt(n_dim) (the store's OWN native bind).
          ZERO gradient descent, ZERO epochs, ZERO loss loop -> glass-box.
```
- **Write-rule choice (autonomy):** PSEUDO-INVERSE / ridge-least-squares (not Storkey). It is the single closed-form
  solve the prior on-substrate cell already validated at 8x on synthetic autoassoc; ridge doubles as the numerical
  stability guard the research note flagged. Storkey (local iterative, no inverse) is the reserved fallback if pinv is
  numerically unstable (it is not: n_train ~360k >> n_dim=1024 -> Gram full-rank, well-conditioned).
- **Ridge (autonomy / calibration_check=adaptive_with_discriminator_gate):** `ridge = 1e-2 * mean(diag(Gram))`,
  auto-scaling to the key-Gram magnitude (NOT tuned on real data). The ORACLE_RISE discriminator must still fire and is
  logged; ridge is reported per store build.
- **NO regression risk to CERT-584/585.** KGStore is NOT modified. The decorrelated W is recomputed on a LOCAL
  cell-owned store INSTANCE after the standard Hebbian ingest, overwriting only that instance's W. The default
  `KGStore.ingest_triples` Hebbian path is bit-identical / untouched; the `hebbian` arm exercises it and must reproduce
  the landed result (Gate D). pinv is a SELECTED path, never the default -- same defaulted-off discipline as hard_neg_frac.

## Arms
Each write rule runs the full base 7-arm harness (NATIVE_ANCHOR_COMPOSE / MEMORIZE_FIXEDCODE / RANDOM_CODES /
NATIVE_SCRAMBLE / IDENTITY_SHUFFLE / ORACLE_FOLDIN / BASELINE_POP), scored PAIRED on the SAME held-out QUERY edges. The
top-level verdict compares the two rules' aggregate MRR.

## Pre-registered bands (primary = ORACLE_FOLDIN mrr RISE = the ceiling question; picked BEFORE the run)
- `ORACLE_RISE = pinv_oracle_mrr / hebb_oracle_mrr`; `NATIVE_RISE = pinv_native_mrr / hebb_native_mrr`;
  `GAP_CLOSED = (pinv_oracle_mrr - hebb_oracle_mrr) / (0.137 - hebb_oracle_mrr)`.
  ADDITIVE_ORACLE_CEIL = 0.137 CITED@notes/research_native_representational_ceiling_levers_2026-07-13.md.
- **HARD-PASS** (`HARD_PASS_DECORRELATED_WRITE_RAISES_CEILING`): `(ORACLE_RISE >= 2.0 OR GAP_CLOSED >= 0.50)` AND native
  mrr rises (`(pinv_native - hebb_native) >= 0.003 OR NATIVE_RISE >= 1.3`) AND the pinv must-fail controls still fire
  (pinv `scramble_controlled` AND `idshuf_controlled` AND `oracle_fires`) AND pinv numerically stable (matrix_norm
  finite, no NaN) AND the hebbian arm reproduces the landed oracle (`|hebb_oracle - 0.023083| <= 0.006`, Gate D).
- **MIDDLE** (`MIDDLE_BAND_PARTIAL_CEILING_RISE`): `1.3 <= ORACLE_RISE < 2.0` and `GAP_CLOSED < 0.50`, OR ceiling rises
  but native mrr does not (ceiling vs realized are separate gaps).
- **HARD-FAIL** (`HARD_FAIL_WRITE_RULE_NOT_THE_LEVER`): `ORACLE_RISE < 1.3` (ceiling barely moves) OR numerical
  instability erases signal.
- **INCONCLUSIVE** if the hebbian arm does NOT reproduce the landed oracle within tolerance (harness/invocation drift).

MEASURED baseline anchors (Gate D):
- hebb ORACLE_FOLDIN mrr = 0.023083  MEASURED@data/exp_native_bind_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ORACLE_FOLDIN
- hebb NATIVE_ANCHOR mrr = 0.013967  MEASURED@ same path :NATIVE_ANCHOR_COMPOSE
- additive oracle ceiling = 0.137     CITED@notes/research_native_representational_ceiling_levers_2026-07-13.md

## Compute architecture
class (c) MIXED: split/support-query/POP = sequential-CPU graph ops. hebbian arm = untouched one-shot KGStore Hebbian
ingest (reproduces landed ~140s/3-seed). pinv arm adds a streaming float64 Gram/Cross accumulation (same [n_dim x n_dim]
shape as the Hebbian pass, ~72 chunks over ~360k train edges) + ONE [1024 x 1024] linalg.solve per store build -- NO
gradient descent, NO epochs. 2 store builds/seed/rule (train-W + oracle fold-in); 3 seeds; only pinv does the solve.
No GPU necessity (one-shot, dense small matmuls) -> `remote_cpu_queue` (device=cpu). FULL wall estimate ~20-25min.
storage_strategy: no_composition (native Hebbian/decorrelated W is a matrix store; no bundled-vs-sharded axis; E/R untouched).

## SCHEMA-VET fields
- `arms_differ_verified: true` (7 arms per rule + hebb-W hash != pinv-W hash asserted at self-test; META_RULE_AF)
- `final_metrics_atomicity: "tmp_replace"` (write_metrics + os.replace)
- `cardinality_ok: true`; `EXPECTED_N_UNITS = n_seeds * 2 rules = 6`; verdict counts units, HARD_FAIL_CARDINALITY_BREACH if short
- `crlb_n/a: "primary is a RISE RATIO of ORACLE mrr (ceiling-relative); bands are ratios of the per-rule MEASURED ceiling, not absolute thresholds"`
- `discriminator_reachability: true` (ratio bands scale to whatever ceiling the FULL measures)
- `baseline_in_band: true` (hebbian ORACLE must fire + reproduce landed; RANDOM/POP near 1/N floor)
- `calibration_check: "adaptive_with_discriminator_gate"` (ridge = 1e-2*mean(diag(Gram)); ORACLE_RISE discriminator still fires; logged)
- `discriminator_survives_scale: analytical + self-test` (pinv capacity gain vs Hebbian is a scale-INVARIANT ratio law; the
  self-test WRITE-RULE micro-discriminator fires pinv-beats-hebb heteroassociative recall by margin 0.252 at load 0.8N >> the 0.14N Hebbian cliff)
- `positive_control_arms:` hebbian arm reproduces landed oracle 0.023083 within +-0.006 at n_dim=1024 (Gate D); ORACLE fires under both rules
- `per_unit_failure_class: true` (no bare except; per (seed,rule) failure_class recorded)
- `start_marker_written / crash_diagnostic_present / heartbeat_present: true`; `cell_chunked: false` (2 rules x 3 seeds in one cell, all persisted per-unit via write_partial; single-shot CPU cell < 30min)
- `progress_logging: "print_flush_true"` (line-buffered stdout + per-seed/per-rule flush prints; timeout >= 1800)
- `functional_requirements:` (1) raise native oracle ceiling via a glass-box write -> pinv least-squares solve;
  (2) keep the relation-operator / entity-identity signal -> pinv must-fail controls (scramble/idshuf) still fire;
  (3) not regress CERT-584/585 -> KGStore untouched, hebbian arm reproduces landed.

## Four validity-preflight checks (declared in the self-test)
1. positive_control_passes: ORACLE fires under BOTH rules on the planted arena.
2. metric_moves: the write-rule micro-discriminator moves synthetic heteroassociative recall cosine across [hebb, pinv] above the Hebbian cliff.
3. negative_control_margin: under pinv, RANDOM + relation-scramble + identity-shuffle sit below NATIVE_ANCHOR by the MRR margin (>=3 controls).
4. full_gates_exercised: aggregate_and_verdict + the top-level ceiling-rise verdict fire every gate at self-test scale under both rules.

## Self-test result (MEASURED, local .venv, run_mode=self_test, n_dim=256)
- writerule discriminator: pinv_cos=0.9979 hebb_cos=0.746 margin=0.2519 (>= 0.20 gate; load 0.8N); low-load pinv intact.
- compose harness (planted arena): pinv ORACLE mrr 0.887 vs hebb 0.763 (pinv RAISES recoverable signal); pinv
  scramble_margin=0.254 idshuf_margin=0.265 (must-fails FIRE); W-hash differs across rules; pinv W finite.
- `SELFTEST_PASS`, validity_preflight_ok=True.

## Dispatch
`bash tools/orchestrator/queue_add.sh remote_cpu_queue kg_store_write_rule_decorrelated_ceiling_v1 experiments/exp_kg_store_write_rule_decorrelated_ceiling_v1.py preregs/2026-07-13_kg_store_write_rule_decorrelated_ceiling_v1.md 3600`
