# Pre-registration: NATIVE_BIND_COMPOSE Stage-0 decisive test (live-store multiplicative bind, CSKG held-out-ENTITY)

- **Cell:** `experiments/exp_native_bind_compose_inductive_entity_cskg_v1.py`
- **Anchor name:** `native_bind_compose_inductive_entity_cskg_v1`
- **Metrics path:** `data/exp_native_bind_compose_inductive_entity_cskg_v1/metrics.json`
- **Filed:** 2026-07-13 (exp_dev). **Target queue:** `remote_cpu_queue` (one-shot Hebbian, no SGD -> cheap CPU).
- **Source of design:** `notes/research_anchor_compose_live_store_integration_path_2026-07-13.md` (Stage-0 "Cheap decisive test").

## Prior-work check (mandatory)
`bash tools/substrate_query.sh "native multiplicative bind Hadamard compose held-out entity inductive
generalization"` -> top hit cosine **0.418** (`Multiplicative vs additive composition`, a research-drill note on
biology/architecture; 2nd `multiplicative` wordnet gloss 0.412; 3rd `Multiplicative composition` note 0.409). These
are GENERIC composition-concept notes, NOT a prior arc cell running this native-bind held-out-entity compose test.
**Prior-work check: hits at cosine>0.30 are generic multiplicative/additive-composition concept notes; NO prior
cell tests native multiplicative-bind + one-shot Hebbian compose of an unseen entity.** Genuinely novel on this
substrate (a NEW native read-path probe), not a rediscovery. The additive counterpart
(`exp_anchor_compose_inductive_entity_cskg_v1`) is the CONFIRMED comparison arm this cell is measured against.

## Question
Does the live `KGStore`'s OWN native MULTIPLICATIVE (Hadamard) bind `key(s,p)=E[s]*R[p]*sqrt(n_dim)` + one-shot
Hebbian W, used with the SAME "compose an unseen entity's code as a bundle of its support-edge estimates" pattern,
deliver the held-out-ENTITY inductive win -- WITHOUT the additive SGD machinery of the confirmed ANCHOR_COMPOSE?
- **HARD-PASS** => native bind NATIVELY carries inductive generalization; live integration is CHEAP (Stage-0a).
- **HARD-FAIL** => native multiplicative bind does NOT support the compose pattern; the additive SGD construction is
  essential and a costlier adjunct bridge is needed (Stage-0b), and continued magnitude-optimization of the additive
  recipe is load-bearing.
Either outcome is decisive and publishable-internally; the test gates the whole live-integration path.

## Mechanism / construction (the crux: multiplicative-bind analog of the additive mean bundle)
For a held-out entity `t` whose test-time-visible SUPPORT edges reach seen anchors `h_i` via relation `r_i`:
```
recall_i     = W @ key(h_i, r_i)          # the store's OWN native Hebbian tail-recall (E-space estimate)
E_derived[t] = sign( sum_i recall_i )     # MAJORITY-SIGN bundle -> bipolar, SAME format/norm as E
```
- **Compose-op choice (autonomy):** MAJORITY-SIGN of the store's native Hebbian tail-recall vectors, NOT a
  real-valued mean. Sign-thresholding keeps the composed code in the store's native bipolar format so its norm is
  degree-INVARIANT and creates NO magnitude/popularity confound in the dot-product readout -- the standard VSA
  "bundle then threshold" op. This is the direct multiplicative analog of the additive degree-invariant mean
  `mean_i(X[h_i]+D[r_i])`.
- **Readout choice (autonomy):** the store's NATIVE bilinear readout `scores = E_patched @ (W @ key(h_q,r_q))`
  (`score_all` with a patched candidate codebook), NOT an external `cleanup_family` primitive. This is the exact
  readout CERT-584/585 ratified; `cleanup_family` was evaluated and rejected as it would swap the native readout
  mechanism (the thing under test) for a distractor.
- `W` is FROZEN on both-seen TRAIN edges; SUPPORT and QUERY edges of a held-out entity are DISJOINT -> genuine
  zero-shot, no leakage. Cold (degree-1) held-out entities keep their fixed row.
- **NO regression risk to CERT-584/585.** This is a NEW read path added IN-CELL (`native_compose_codes` +
  `native_query_recall` + `score_from_codes`); `KGStore.E/R/W`, `key`, `score_all`, `predict_*` are used read-only
  and are NOT modified. `n_dim=1024` = the store default + CERT-584/585 chain-grade regime.

## Arms (7; scored PAIRED on the SAME held-out QUERY edges + candidate set)
| arm | held-out entity code | recall (readout) | role |
|---|---|---|---|
| NATIVE_ANCHOR_COMPOSE | `sign(sum W@key(support))` bundle | train-W | MECHANISM |
| MEMORIZE_FIXEDCODE | fixed random bipolar row `E[t]` | train-W | native memorize control (direct comparison; same W) |
| RANDOM_CODES | random bipolar | random recall | null (the bar) |
| NATIVE_SCRAMBLE | compose with SUPPORT relations scrambled | train-W | must-fail (relation-signal control) |
| IDENTITY_SHUFFLE | compose assigned to the WRONG held-out entity | train-W | must-fail (entity-identity control) |
| ORACLE_FOLDIN | fixed row `E[t]`; held-out edges folded into W | fold-in-W | positive control / arena-answerable ceiling |
| BASELINE_POP | frequency incumbent | - | fit-independence sanity |

The two stores (train-W and fold-in-W) share BIT-IDENTICAL E/R (same generator seed + n_dim) so candidate codes are
comparable; only W differs. NATIVE/MEMORIZE/SCRAMBLE/IDSHUF SHARE one train-W recall (computed once).

## Ceiling-aware, degree-unbiased metric set (IDENTICAL to the additive arena for direct comparability)
Every arm scored under the full FILTERED rank spectrum, rank-vs-ALL-N candidates (KGE standard; other true tails of
`(h,r)` masked): **hits@{1,3,10,100} + MRR**, NO sampled-negative pool (avoids popularity/degree bias). **Primary
metric = FILTERED MRR.** Per-arm spectrum + a per-metric `oracle_fire_by_metric` table written to `gates`.

## Pre-registered bands (primary = FILTERED MRR; `H` = MEASURED oracle headroom `= ORACLE_mrr - RANDOM_mrr`; picked BEFORE the run)
Bands are **CEILING-RELATIVE** (fractions of the in-run-measured `H`) so ONE FULL computes the ceiling AND scores
NATIVE_ANCHOR against a fair fraction of it. Same fractions as the additive arena.
- **ORACLE-FIRES** (arena answerable): `ORACLE_mrr >= 3x RANDOM_mrr` (scale-free ratio) **AND**
  `ORACLE_mrr - RANDOM_mrr >= 0.003`.
- **HARD_PASS** (`HARD_PASS_NATIVE_BIND_INDUCTIVE`): `(NATIVE - RANDOM)_mrr >= max(0.50*H, 0.002)` **AND**
  `(NATIVE - MEMORIZE)_mrr >= 0.10*H` (beats the native memorize control) **AND** ORACLE fires **AND** scramble
  controlled (`(SCRAMBLE - RANDOM)_mrr <= 0.25*H`) **AND** identity-shuffle controlled
  (`(IDSHUF - RANDOM)_mrr <= 0.25*H`) **AND** not broken **AND** the NATIVE MRR margin holds on the low+mid degree
  stratum (fair, non-super-hub). **Interpretation: the substrate NATIVELY does inductive generalization.**
- **MIDDLE_BAND**: `(NATIVE-RANDOM)_mrr >= 0.20*H` but not HARD_PASS. Localize via anchor-support-degree stratification.
- **HARD_FAIL** (`HARD_FAIL_NATIVE_BIND_NO_TRANSFER`): `(NATIVE - RANDOM)_mrr < 0.20*H` with ORACLE firing.
  **Interpretation: native multiplicative bind cannot induce; the additive construction is essential (adjunct bridge).**
- Gated **INCONCLUSIVE** if ORACLE does not fire, `< 20` held-out queries, or RANDOM beats POP by
  `> max(0.005, 0.25*H)` mrr (broken).
- **HP_SCOPE:** the inductive HARD_PASS gates apply to **NATIVE_ANCHOR_COMPOSE only**. ORACLE = positive control
  (must fire); RANDOM/NATIVE_SCRAMBLE/IDENTITY_SHUFFLE = must-not-clear-bar controls; MEMORIZE = native memorize
  head-to-head; POP = fit-independence sanity.

## Weak-point localization (first-class per cell)
Reported in `per_seed[*].localization`: (1) **anchor-support degree** bins {cold(0),d1,d2_3,d4_7,d8+} -- does the
margin scale with support? cold = sparse-entity failure mode; (2) **global-degree tertile** (low/mid/high) +
`fair_low_mid` -- super-hub vs tail (P1 skew); (3) **relation tertile** (hardest vs rest, CITED@
`data/exp_cskg_graph_structure_diagnostic_v1/metrics.json:diagnostic.hardest_tertile`).

## Four validity-preflight checks (declared in the self-test via experiments._validity_preflight)
1. **positive_control_passes**: ORACLE_FOLDIN recovers planted held-out tails and clears RANDOM by the ceiling-aware ratio+abs fire gate on MRR.
2. **metric_moves**: held-out MRR MOVES across [RANDOM, MEMORIZE, NATIVE_ANCHOR, ORACLE].
3. **negative_control_margin**: RANDOM + NATIVE_SCRAMBLE + IDENTITY_SHUFFLE sit below NATIVE_ANCHOR by margin, deterministically (>=3 controls).
4. **full_gates_exercised**: `aggregate_and_verdict` runs on the planted per-seed, firing every fail-closed gate.

## Self-test (MEASURED, local .venv, single-thread CPU, 0.7s) -- PASS
Planted GROUP-STRUCTURED arena (`build_planted_native_arena`, n_groups=8, members_per_group=12, rels_per_group=3
disjoint per group, anchor_repeat=6, member_edges=4; n_ent=112, n_rel=24) where each group has a dedicated seen
anchor tail A_g reinforced from every (member, group-relation) pair so `W@key(member, group-rel)` is DOMINATED by
`E[A_g]`; a held-out member's support/query edges then all recall ~E[A_g] -> native compose CAN recover it, and
scrambling a support relation to a FOREIGN group's relation recalls ~0 (relation is NECESSARY -> must-fail controls
genuinely fail). MEASURED@`data/exp_native_bind_compose_inductive_entity_cskg_v1_selftest/metrics.json:mechanism_selftest`:
- held-out **MRR** (primary): **NATIVE=0.26618, MEMORIZE=0.03469, RANDOM=0.05078, SCRAMBLE=0.09467, IDSHUF=0.21703,
  ORACLE=0.76315, POP=0.03105**; native_margin(MRR)=**0.2154**, form_margin(NATIVE-MEMORIZE)=**0.2315**,
  scramble_margin(NATIVE-SCRAMBLE)=**0.1715**, idshuf_margin(NATIVE-IDSHUF)=**0.0491**, oracle ratio=**15.03x**;
  **7 distinct sigs**; `validity_preflight_ok=True`; verdict=**SELFTEST_PASS**.
- held-out hits@10 (legacy display): NATIVE=0.429, MEMORIZE=0.107, RANDOM=0.071, SCRAMBLE=0.286, IDSHUF=0.446,
  ORACLE=0.920, POP=0.071.
- All gates fire: oracle_recovers, oracle_fires, native_recovers, native_beats_random, scramble_fails, idshuf_fails,
  pop_at_floor, arms_differ = **all True**.
- Internal `aggregate_and_verdict` on the planted seed = **MIDDLE_BAND_PARTIAL_NATIVE_TRANSFER** (native recovers 30%
  of `H` on the planted arena -> below the 50% HARD_PASS fraction; band gate exercised, NOT short-circuited). Note:
  IDENTITY_SHUFFLE is a WEAKER control on this tiny arena (15 held-out across 8 groups -> within-group swaps preserve
  the anchor signal, idshuf_margin 0.049) but still fires above the 0.03 self-test floor; at FULL CSKG scale
  (thousands of held-out entities across a large relation space) cross-group shuffles collapse it far more strongly.
- **The construction RECOVERS a planted held-out entity's edges ZERO-training (native-bind, MRR 0.266 vs random
  0.051); both must-fail controls fire with margin; the fold-in ORACLE fires 15x (arena answerable by the native store).**

## SCHEMA-VET / cell-template fields
```json
{
  "cell": "experiments/exp_native_bind_compose_inductive_entity_cskg_v1.py",
  "anchor_name": "native_bind_compose_inductive_entity_cskg_v1",
  "arms_differ_verified": true,
  "arms_differ_note": "7 arms; self-test measured 7 distinct score signatures (>=5 gate)",
  "final_metrics_atomicity": "tmp_replace",
  "cardinality_ok": true,
  "EXPECTED_N_UNITS": "n_seeds (per-seed all-7-arms + >=5 distinct sigs asserted; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H on shortfall)",
  "crlb_floor_computed": 0.0004,
  "crlb_formula_reference": "chance hits@10 = k/N = 10/25752 ~ 0.0004; INFO-CEILING: filtered hits@10-vs-all-N caps low for the ORACLE at N~25.7k -> primary metric = FILTERED MRR + ceiling-RELATIVE bands (fractions of the MEASURED oracle MRR headroom H)",
  "discriminator_reachability": true,
  "discriminator_reachability_note": "bands are FRACTIONS of the MEASURED oracle MRR headroom H (in-run), not fixed absolutes -> reachable by construction whenever ORACLE fires; the fold-in ORACLE fires at 15.03x on the planted self-test (arena answerable by the native store)",
  "baseline_in_band": true,
  "baseline_in_band_note": "RANDOM/POP near the 1/N floor on held-out; ORACLE-fires gate = ORACLE_mrr >= 3x RANDOM_mrr AND headroom >= 0.003 (scale-free ratio + non-noise floor)",
  "discriminator_survives_scale": "analytical_plus_selftest",
  "discriminator_survives_scale_note": "a fixed-random-atom entity code is a random LABEL, not a structure-derived position, so the native MEMORIZE null persists at ANY N; the fold-in ORACLE proves the metric can move at scale; the self-test fires NATIVE-beats-RANDOM + scramble-fails + identity-shuffle-fails deterministically on a group-structured arena where the store's own recall is relationally consistent",
  "hard_pass_strictly_above_floor": true,
  "hp_scope": {"NATIVE_ANCHOR_COMPOSE": ["native_margin_vs_random", "form_margin_vs_memorize", "fair_lowmid_native_margin"], "ORACLE_FOLDIN": ["oracle_fires"], "RANDOM_CODES": ["must_not_clear_bar"], "NATIVE_SCRAMBLE": ["scramble_controlled"], "IDENTITY_SHUFFLE": ["idshuf_controlled"], "BASELINE_POP": ["fit_independence"]},
  "calibration_check": "adaptive_with_discriminator_gate",
  "calibration_check_note": "HELDOUT_ENTITY_FRAC=0.15 / SUPPORT_FRAC=0.5 / ORACLE_FIRE_RATIO=3.0 / ORACLE_FIRE_ABS=0.003 / HP_CEIL_FRAC=0.50 / FORM_CEIL_FRAC=0.10 / HF_CEIL_FRAC=0.20 / SCRAMBLE_CEIL_FRAC=0.25 pre-registered, NOT tuned on real data; identical to the additive arena; NATIVE bands are FRACTIONS OF THE MEASURED oracle headroom H (in-run)",
  "per_unit_failure_class": true,
  "cell_chunked": false,
  "cell_chunked_note": "in-process seed loop with write_partial per-seed persistence; one-shot Hebbian (no SGD, no epochs) -> each seed is minutes, a crash loses at most the in-progress seed",
  "start_marker_written": true,
  "crash_diagnostic_present": true,
  "heartbeat_present": true,
  "defensive_error_checking": "start_marker + crash_diagnostic + heartbeat + per-seed failure_class",
  "except_ordering": "SystemExit/KeyboardInterrupt re-raised before except Exception; no bare except / no BaseException (grep-clean)",
  "progress_logging": "print_flush_true",
  "sweep_alignment_verdict": "ALIGNED",
  "discriminating_fraction": "n/a (not a parameter sweep; single held-out-entity split per seed)",
  "composition_edges": "native bind key(s,p)=E[s]*R[p]*sqrt(n) -> Hebbian recall W@key -> majority-sign bundle -> native bilinear readout E_patched@(W@key); SHAPE_MATCH (all in the store's bipolar n_dim E-space; the bundle is dimension-preserving)",
  "positive_control_arms": "ORACLE_FOLDIN (held-out edges folded into W) reproduces the arena-answerable ceiling AT THE TEST REGIME; must fire under the ceiling-aware gate (ORACLE_mrr >= 3x RANDOM_mrr AND headroom >= 0.003) -> the ORACLE score IS the measured ceiling H against which NATIVE bands are set. Native store primitives (key/ingest/score_all) are the CERT-584/585 primitive, reproduced verbatim (read-only), NOT reimplemented",
  "functional_requirements": "represent an unseen entity via the store's OWN bind (E_derived majority-sign bundle of native Hebbian recalls) | rank its held-out edges (native bilinear readout) | prove signal is relational not degree/anchor (NATIVE_SCRAMBLE) | prove signal is entity-specific (IDENTITY_SHUFFLE) | prove arena answerable (ORACLE_FOLDIN) | fit-independence (BASELINE_POP)",
  "final_metrics_write": "write_metrics(...) -> os.replace atomic"
}
```

## Compute architecture
class (c) MIXED. Split + support/query partition + POP = sequential-CPU graph ops (no matmul). The native store is
ONE-SHOT Hebbian (NO SGD, NO epochs) -> the whole cell is CHEAP CPU: ingest = KGStore.ingest_triples chunked Hebbian
matmul; native compose = one batched (S,n_dim)@(n_dim,n_dim) recall + vectorized index_add bundle + sign; readouts =
query-chunked batched matmul (recall @ E_patched.T; (nq,N) map chunked). NATIVE/MEMORIZE/SCRAMBLE/IDSHUF share one
train-W recall. device=cpu (no gradient training -> GPU unnecessary; routed to remote_cpu_queue). Storage: the store's
native Hebbian W (CERT-584/585 primitive, untouched); the ONLY new bundle is the per-ENTITY majority-sign
superposition of the entity's own support-edge recall vectors -- read-only, additive to the store.

## Run profiles
- **self_test** (LOCAL .venv gate, PASSED 0.7s): n_dim=256, planted group arena, single-thread CPU, 1 seed.
- **full** (REMOTE CPU): n_dim=1024, CSKG core k_core=12 (N~25.7k), held-out-entity split frac=0.15 support_frac=0.5,
  n_heldout_eval=3000, seeds=[7,13,17]. One-shot Hebbian; estimated wall ~10-15min; timeout 3600s (generous margin,
  well within the 14400 cap).

## Numbers provenance
- self-test held-out MRR + margins + oracle_fire_by_metric: MEASURED@`data/exp_native_bind_compose_inductive_entity_cskg_v1_selftest/metrics.json:mechanism_selftest`.
- CSKG core N~25752, deg_mean 36.8, 12-core, P1 skew max/mean=164, hardest_tertile relations: MEASURED@`data/exp_cskg_graph_structure_diagnostic_v1/metrics.json`.
- Additive comparison (ANCHOR_COMPOSE, same split + arena + ceiling-relative bands): `experiments/exp_anchor_compose_inductive_entity_cskg_v1.py` + `preregs/2026-07-12_anchor_compose_inductive_entity_cskg_v1.md`.
- HARD-PASS "native bind already suffices" P~0.25 (deflated; no direct precedent in either lit-scan): CITED@`notes/research_anchor_compose_live_store_integration_path_2026-07-13.md`.
