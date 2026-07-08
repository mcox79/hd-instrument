# Pre-reg: encoder_peel_sic_readout_realcodes_v1

**Filed:** 2026-07-08 by hdi_exp_dev
**Cell:** `experiments/exp_encoder_peel_sic_readout_realcodes_v1.py`
**Anchor:** `encoder_peel_sic_readout_realcodes_v1`
**Reuses (Gate D positive control):** the REAL two-head STORE head is sourced by importing
`_train_arm` / `_make_forward` / `_encode_wta` / `_l2n` / `_load_teacher` VERBATIM from
`experiments/exp_encoder_twohead_decoupled_store_retrieval_v1.py` (commit b2e26cd86; FULL
HARD_FAIL_ONE_HEAD_FAR_MISS @V40000, store SP_wta 0.99@J3 -> 0.75@J5 -> 0.20@J8). The proven
clean-code confidence-ordered peel/SIC readout comes from
`experiments/exp_bundling_slot_peel_sic_v1.py` (commit c2f65e53d; FLAT_PEEL ~1.0 at high J on clean
codes, cancellation load-bearing, slots unnecessary) -- re-implemented for real-valued WTA codes.

## Question
On CLEAN synthetic codes the additive-superposition wall is beatable by a confidence-ordered
peel/SIC (matching-pursuit deflation) readout. Does that SAME readout fix the REAL two-head encoder
STORE head, whose flat-argmax superposition recall COLLAPSES at high J at V=40000? The collapse is an
encoder-embedding-geometry (correlation-law) artifact NOT reproduced by clean codes, so whether
peel/SIC TRANSFERS from clean synthetic to REAL correlated encoder codes is genuinely UNKNOWN.

## Prior-work check (substrate-KB concept-query, mandatory)
`bash tools/substrate_query.sh "confidence-ordered peel SIC readout superposition bundle recall
encoder store head"` -> top cosine 0.2969 (PCN-AM compositional-recombination handoff note), 0.2939
(a POST_COMPACTION backup chunk), 0.2861 (ARCH_B softmax-readout-recaptures-capacity verdict).
**NONE at cosine>0.30 is a prior peel/SIC-on-REAL-encoder-codes cell.** The closest prior work
(ARCH_B) recaptured linear-readout-dead capacity with a SOFTMAX modern-Hopfield readout on a
different (localization) corpus; that is a related "readout was the limiter" finding but a different
mechanism (softmax attractor vs matching-pursuit deflation) and different codes. This transfer test
(clean-code peel/SIC pointed at the two-head store collapse) is genuinely novel; not a rediscovery.

## Design (3 PAIRED readout arms on REAL store codes; 3 store sources)
Per (seed, source, J): sample nq member sets (rng.integers(0,V,(nq,J)), WITH replacement -- exactly
the two-head `_superposition_recall` sampling so numbers are directly comparable to the cited
0.20@J8). Bundle = raw sum of unit-norm WTA store codes. All 3 readout arms decode the SAME member
sets. Metric = SET recall `|pred top-J set ∩ true member set| / J`.

READOUT ARMS:
1. **FLAT_ARGMAX** -- l2-normalized bundle, argmax-cosine top-J. == two-head `_superposition_recall`
   VERBATIM == the CURRENT FAILING readout. Negative control; MUST collapse at high J.
2. **FLAT_PEEL_UNIT** -- confidence-ordered greedy SIC: global argmax -> deflate `residual -= dict[ih]`
   (unit weight; principled for a sum of unit codes) -> repeat J, never repick. EXACT transfer of the
   clean-code FLAT_PEEL. **[HEADLINE CANDIDATE FIX]**
3. **FLAT_PEEL_PROJ** -- same greedy SIC, projection-weight deflation `residual -= (dict[ih].residual)dict[ih]`
   (classic matching pursuit). Tests whether correlated real codes need magnitude-aware deflation.

Confidence-ordering is intrinsic to flat greedy MP (each round resolves the GLOBAL argmax first);
there is no separable flat "fixed-order" ablation (that required slots; already settled in the
clean-code cell SLOT_PEEL_POWER >> SLOT_PEEL_FIXED). This cell answers TRANSFER, not ordering.

STORE SOURCES (real WTA store dict per seed; k = N/32 = 3.125% sparsity):
- **twohead_shared** -- shared trunk -> VICReg store head (the collapsing HEADLINE real code). PRIMARY; bands defined here.
- **singlehead_native** -- VICReg-only single code (strongest decorrelated). breadth.
- **native_untrained** -- random projection of BGE + WTA (free). breadth / correlation contrast.

## Compute architecture
Class **(a) batched-GPU**. Training (twohead_shared VICReg store + RKD ret, singlehead_native VICReg)
is matmul-heavy; readout is batched over queries in torch on `device` (sequential only over the J
peel rounds, which have a genuine dependency -- deflation). FULL routes to **overnight_queue (GPU)**;
device=auto -> cuda on the runner. Storage strategy: **no_composition / no_store** (encoder-geometry
cell; the "dictionary" is the per-concept store code, evaluated by argmax-cosine / peel cleanup, not
a bundled associative store). native_untrained store forward is free (no training).

## Functional requirements (Gate E)
- FR1 recover J bundled store-code members from their superposition -> primitive: cleanup/argmax
  (FLAT_ARGMAX, the failing baseline) + matching-pursuit deflation (FLAT_PEEL_*, the candidate).
- FR2 source the REAL collapsing store head -> primitive: two-head `_train_arm` store head (reused).

## Regime
- **FULL:** N=4096, H=512, V=40000, iters=800, B=8192, nq=600, Js=[3,5,8,12], deep_j=8, max_j=12,
  seeds=[7,13,19,23,29]. (production two-head FULL regime.)
- **SMOKE:** N=2048, V=4000, iters=150, B=1024, nq=250, Js=[5,8,12,16], deep_j=12, max_j=16,
  seeds=[7,13]. SAME arms + SAME decoders + SAME verdict path (SMOKE=FULL branch parity); high J so
  FLAT_ARGMAX collapses at the smaller smoke V (discriminator fires).
- **EXPECTED_N_UNITS** = n_seeds (one per-seed unit; each sweeps 3 sources x |Js| x 3 arms). FULL=5.
  `cardinality_ok: true`.

## Bands (HEADLINE source = twohead_shared; HYPOTHESIZED@this prereg from this-session pilot)
best_peel = max(FLAT_PEEL_UNIT, FLAT_PEEL_PROJ). deep J (FULL=8), max J (FULL=12).
- **DISCRIMINATOR-FIRES gate (META_RULE_AG):** FLAT_ARGMAX@deep_j must be <= 0.70 (collapsed). At
  V=40000, argmax@J8 ~0.20. If argmax stays > 0.70 -> `MIDDLE_BAND_VACUOUS_DISCRIMINATOR` (raise J/V).
- **HARD_PASS (peel/SIC TRANSFERS -- wall beaten on REAL codes):** at deep_j,
  `best_peel - FLAT_ARGMAX >= 0.20` AND `best_peel >= 0.60` AND `cv(best_peel over seeds) <= 0.15`,
  AND the lift PERSISTS at max_j: `best_peel - FLAT_ARGMAX >= 0.20`.
- **HARD_FAIL (peel does NOT transfer -> collapse is GEOMETRY not readout-order; honest negative):**
  `best_peel - FLAT_ARGMAX <= 0.05` at EVERY J>=8.
- **MIDDLE_BAND:** real but sub-bar lift (0.05 < lift < 0.20, or abs < 0.60, or lift does not persist
  to max_j).
Band feasibility (META_RULE_L, strictly-above-floor): HP lift bar 0.20 vs HARD_FAIL 0.05 -> band
width 0.15, HP is +0.145 above floor (>> 5%). Argmax floor ~0.20 and peel headroom ~0.99 (pilot at
V<=8k) -> PEEL_ABS_HP 0.60 reachable. Enrichment (reported): UNIT-vs-PROJ deflation winner per source;
singlehead_native + native_untrained lifts.

## SCHEMA-VET mandatory fields
- `cardinality_ok: true` (EXPECTED_N_UNITS = n_seeds; verdict emits HARD_FAIL_CARDINALITY on breach)
- `arms_differ_verified` -- 3 readout arms distinct winner-sets at deep J (>=2 of 3 distinct); sources distinct dict-hashes
- `final_metrics_atomicity: tmp_replace` (write_metrics os.replace) + per-seed partials + resume
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException; grep-clean)
- `crlb_n/a`: set-recall has no closed-form noise floor; feasibility from MEASURED pilot bands
- `discriminator_reachability: true` (argmax floor ~0.20 known; peel ~0.99 headroom at V<=8k)
- `baseline_in_band`: FLAT_ARGMAX@deep_j on headline in (0.05, 0.95) (the in-band control)
- `calibration_check: default_ok_for_this_regime` (real BGE cache; operating points from two-head + this-session pilot)
- `telemetry_sensitivity`: self-test asserts two seeds MOVE the headline discriminator (not pinned)
- `sweep_alignment_verdict: ALIGNED` (J is the swept axis; each readout arm experiences the same J)
- `discriminating_fraction`: FULL Js=[3,5,8,12] -> J in {8,12} predicted in discriminating band at V=40000 (2/4 = 0.50 >= 0.30)
- `positive_control_arm (Gate D)`: FLAT_PEEL_UNIT reproduces the clean-code readout mechanism; the
  store dict reproduces the two-head store head at the test regime (same `_train_arm`).
- `progress_logging: print_flush_true` + `_heartbeat.jsonl`; `start_marker_written`; `crash_diagnostic_present: true`
- `cell_chunked: false` -- multi-seed with per-seed partial checkpoint + resume (mirrors the landed
  two-head cell's proven pattern; single-GPU host; one seed lost != all lost, partials persist).
- `run_mode`: cell defaults to `full` on bare invocation (most defensive, section 16); smoke via `--smoke`.

## SMOKE RESULT (MEASURED@data/exp_encoder_peel_sic_readout_realcodes_v1_smoke/metrics.json)
- verdict = **HARD_PASS_PEEL_SIC_TRANSFERS_TO_REAL_CODES**; run_mode=smoke; elapsed=117.8s; disc_fires=True; cardinality_ok, arms_differ, baseline_in_band all True.
- HEADLINE twohead_shared, deep_J=12: FLAT_ARGMAX=0.512 (collapsed <=0.70) -> best_peel=0.996 (FLAT_PEEL_UNIT) lift=+0.484 cv=0.000; lift persists @J16=+0.603.
- singlehead_native: AX@J12=0.555 -> peel 0.995 (lift +0.440). native_untrained: AX@J12=0.324 -> peel 0.961 (lift +0.637). UNIT deflation >= PROJ throughout.
- Self-test PASS (peel_ge_argmax, disc_fires, telemetry_moves, arms_differ, sources_differ). CPU-local.

## Timeout
`trained_encoder` floor = 10800s (3h). exp_guard naive multiplication estimates 14400 (block) but
that over-counts (batch/iters/N axes all applied to a 120s EVAL-dominated smoke wall); empirical
anchor: the two-head cell at the IDENTICAL FULL regime trains 4 trained arms x 5 seeds and lands
within the 3h floor -- this cell trains only 2 trained arms x 5 seeds (~half) plus cheap batched
readout -> ~1.5-2h expected. **Declared timeout = 10800s** (3h; ample margin, under the 4h GPU cap).
