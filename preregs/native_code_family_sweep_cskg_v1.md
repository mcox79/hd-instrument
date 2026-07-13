# Pre-registration: native_code_family_sweep_cskg_v1

Cell: `experiments/exp_native_code_family_sweep_cskg_v1.py`
Queue: `remote_cpu_queue` (device=cpu; one-shot Hebbian, NO SGD -> CPU-appropriate; GPU unnecessary)
Author: exp_dev (hdi_exp_dev). Date: 2026-07-13.

## Question
Does any GLASS-BOX (closed-form, NO SGD) entity/relation CODE FAMILY carry more relational geometry through the
substrate's OWN native multiplicative-Hebbian store than the default random-bipolar atoms -- the DEPLOYABLE half of
the native-codes lever, at FIXED n_dim=1024 (dimension is a settled, separate ladder)? Swap ONLY the fixed E/R code
family; the store's bind/Hebbian/readout code path is bit-identical (CERT-584/585 untouched, atoms injected
read-only). Per family measure the native ORACLE ceiling AND native MECHANISM (compose-and-read) MRR + native/oracle
fraction on the SAME held-out-ENTITY arena/split/controls as `exp_native_bind_compose_inductive_entity_cskg_v1`.

## Prior work / novelty
Substrate-KB concept-query run 2026-07-13 (`bash tools/substrate_query.sh "native glass-box code family sweep..."`):
top hits at cosine 0.34 are substrate CONTENT atoms ("relational", framenet "Relation"), NOT prior arc experiment
cells. Prior-work check: NONE at cosine>0.30 (no arc-cell rediscovery). This cell is the code-family axis of the
levers program; the dimension axis (Anchor B) and write-rule axis (Anchor A) are separately scoped.

## Code families (all glass-box, closed-form, NO SGD; injected into KGStore.E/R only)
- `RANDOM_BIPOLAR` : store default {-1,+1}. THE REFERENCE (reproduces the baseline arm in-cell).
- `BLOCK_SPARSE_BSDC` : sparse ternary {-1,0,+1}, random support at density 0.10 (Willshaw/Rachkovskij BSDC; lever 4).
- `GAUSSIAN_DENSE` : dense continuous N(0,1). Binarization control (justified closed-form control; isolates whether
  {-1,+1} quantization costs geometry).
- `CONTENT_TRIGRAM` : char-trigram CONTENT codes from the entity/relation LABEL (KGStore content option; lever 7).
  Correlated codes -> tests the "content codes may HURT via crosstalk" prediction
  (CITED@reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08.md).

FHRR (complex unit-phase) DELIBERATELY EXCLUDED: requires a divergent complex64 bind/Hebbian/readout path that would
break the bit-identical real-arena contract and is NOT a drop-in deployable swap of the real CERT-584/585 store
(would need its own re-validation). Drill ranks it lowest (P_deflated=0.10, capacity-equivalent). Flagged as a
separately-scoped complex-path follow-up if the real families are inconclusive. (Cell-author scoping call.)

## Arms (per family; UNIFORM L2-normalized cosine readout for fair cross-family comparison; recall = native raw bind)
NATIVE_ANCHOR_COMPOSE (mechanism), MEMORIZE_FIXEDCODE, ORACLE_FOLDIN (per-family ceiling), NATIVE_SCRAMBLE (must-fail),
IDENTITY_SHUFFLE (must-fail). Shared family-agnostic (once/seed): RANDOM_CODES (null), BASELINE_POP (fit-independence).

## Pre-registered bands (primary = FILTERED MRR rank-vs-ALL-N; means over seeds; ref = RANDOM_BIPOLAR family)
- ARENA-ANSWERABLE (positive control): RANDOM_BIPOLAR ORACLE fires -- ORACLE_bipolar >= 3.0x RANDOM AND headroom
  >= 0.003. (THEORETICAL/MEASURED reachable: baseline landed ORACLE=0.0231 vs RANDOM=0.00045, ratio 51x
  MEASURED@data/exp_native_bind_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.)
- CODES_HELP: EXISTS a non-bipolar family f with ORACLE_f fires AND scramble+identity must-fails controlled
  (SCRAMBLE_f-RANDOM <= 0.25*H_f and IDSHUF_f-RANDOM <= 0.25*H_f, H_f=ORACLE_f-RANDOM) AND
  ORACLE_f >= 1.25*ORACLE_bipolar AND NATIVE_f >= 1.25*NATIVE_bipolar AND NATIVE_f > RANDOM AND the lift holds on the
  fair low+mid degree stratum => fixed glass-box codes ARE a deployable lever.
- MIDDLE (ceiling-only): some f raises ORACLE by 1.25x but NATIVE does not follow.
- CODES_DONT (structured hurts): some f (predicted: CONTENT) has ORACLE_f <= 0.75*ORACLE_bipolar (crosstalk).
- CODES_DONT (wash): all non-bipolar families in [0.75, 1.25)x reference on BOTH oracle and native.
- Gated INCONCLUSIVE if ref ORACLE does not fire, too few held-out queries (< 20), or RANDOM beats POP (broken).

Expectation (deflated, per drill CITED@notes/research_native_representational_ceiling_levers_2026-07-13.md): most
likely CODES_DONT (wash or content-HURTS); code family ranked a weak/neutral/negative lever (P 0.10-0.25). A CODES_HELP
would be a genuine, cheap surprise. Either outcome is decisive: HELP -> deployable glass-box lever; DONT -> the
learned/additive construction is the only path (feeds the integration endgame).

## SCHEMA-VET fields
- sweep axis: CODE FAMILY (4) x seeds (3). EXPECTED_N_UNITS = n_seeds = 3; each seed asserts all 4 families + shared
  arms + >=10 distinct sigs (`cardinality_ok`, META_RULE_H).
- `arms_differ_verified`: true (self-test 22 distinct sigs; FULL gate requires >=10/seed).
- `final_metrics_atomicity`: tmp_replace (write_metrics + os.replace).
- `except SystemExit: raise` before `except Exception` (no BaseException / no bare except; grep-gate CLEAN).
- `crlb_n/a`: primary is FILTERED MRR with RATIO-to-reference bands -> discriminator_reachability OK by construction
  (bands scale to whatever oracle each family MEASURES; not an absolute threshold).
- `baseline_in_band`: RANDOM_BIPOLAR ORACLE fires (positive control); RANDOM/POP near the 1/N floor.
- discriminator survives scale: (B) analytical (a fixed random-atom code is a random LABEL not a structure-derived
  position -> memorize null persists at any N; a content/correlated code's crosstalk grows with load, not shrinks) +
  baseline-MEASURED reference oracle fires at FULL n_dim=1024.
- `HP_SCOPE`: CODES_HELP gates apply to NON-BIPOLAR families' NATIVE+ORACLE only. RANDOM_BIPOLAR ORACLE = positive
  control; RANDOM/SCRAMBLE/IDSHUF = must-not-clear-bar controls; MEMORIZE = native head-to-head + CONTENT zero-shot
  probe; POP = fit-independence sanity.
- `calibration_check`: adaptive_with_discriminator_gate -- all fracs/ratios pre-registered, NOT tuned on real data;
  CODES_HELP bands are RATIOS to the in-run MEASURED reference family.
- Gate D (reproduce prior chain-grade at test regime): the RANDOM_BIPOLAR ORACLE arm should reproduce the baseline's
  ORACLE ~0.0231 at FULL (same fixed bipolar codes + fold-in recall; L2-norm is uniform scaling -> argsort identical).
  Divergence > 0.10 relative => flag invocation/regime mismatch. (REMOTE VERIFY checkpoint.)
- `cell_chunked`: false (single-process multi-seed loop with per-seed write_partial + failure-class capture; runner
  death loses at most the in-progress seed; per-seed try/except records failure_class).
- `start_marker_written`: true. `crash_diagnostic_present`: true (CELL_CRASHED metrics + traceback).
- `heartbeat_present`: true (_heartbeat.jsonl per selftest + per seed).
- `progress_logging`: print_flush_true (line_buffered stdout + per-seed/per-family flush prints). (timeout_s < 1800
  expected, but flush is present regardless.)

## Compute architecture
class (b) sequential-CPU with justification: one-shot Hebbian (NO SGD/epochs); per family 2 chunked-matmul ingests +
a few (nq,n_dim)@(n_dim,N) chunked scorings. Storage: SHARDED per-atom E/R + native Hebbian W (untouched CERT-584/585
primitive); the only new object is the per-entity L2-normed superposition of the entity's own support-edge recall
vectors (read-only). GPU unnecessary (small one-shot matmuls). remote_cpu_queue, device=cpu.

## Config
FULL: n_dim=1024, k_core=12 (N~25.7k, n_train~360k), heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=3000,
seeds=[7,13,17]. Timeout 3600s (baseline 1-family FULL = 143s MEASURED; ~4x families + content-code build ~= est
700-900s; 3600s = ~4x headroom; < 14400 cap).

## Self-test (MANDATED pre-flight; planted homophilic arena; PASSED locally 2026-07-13 on .venv)
RANDOM_BIPOLAR ORACLE=0.7631 fires; CONTENT_TRIGRAM beats RANDOM_BIPOLAR on MEMORIZE by struct_margin=0.091 (>=0.02);
content scramble/identity must-fails fire (0.142 / 0.761); POP at floor; 22 distinct sigs; 4 validity-preflight OK.
Content matnorm=155326 vs ~1400 others = the crosstalk signature predicted for correlated content codes (lever 7).

## REMOTE VERIFY checklist (orchestrator, post-ship)
run_mode=full; verify RANDOM_BIPOLAR ORACLE ~0.023 (Gate D reproduce); ref_oracle_fires=true; per_family table +
help/ceiling/hurt classification; metrics.json size > 5KB; status_log entry.
