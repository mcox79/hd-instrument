# Pre-registration: multicorpus_reasoning_headroom_survey_v1

SURVEY of degree-stratified reasoning-HEADROOM over frequency across a LADDER of real KG/commonsense
corpora + 2 synthetic anchors, to pick the durable-escape reasoning corpus ON MERIT. Reuses the CSKG-
acceptance / FB15k-237-VET headroom apparatus apples-to-apples (identical code path). No file conflict with
the acceptance cell (new script + new anchor).

- **Cell**: `experiments/exp_multicorpus_reasoning_headroom_survey_v1.py`
- **Anchor**: `multicorpus_reasoning_headroom_survey_v1`
- **Filed**: 2026-07-10 by hdi_exp_dev.

## Prior-work check (concept-query before authoring)
`bash tools/substrate_query.sh "multi corpus reasoning headroom survey degree stratified fairness reach
ceiling frequency baseline"` top hits: generic `Reasoning`/`reasoning` atoms (cosine 0.288) + a 2026-06-18
`headroom_discrimination` routing note (0.275) -- ALL below the 0.30 prior-arc threshold; no prior
multi-corpus reasoning-headroom SURVEY cell. **Verdict: GENUINELY NOVEL** -- first cross-corpus fair-
headroom ranking; the CSKG-acceptance cell (which this extends) only compared CSKG vs FB15k-237 + 2 synth.
Not a rediscovery; a ladder extension of validated apparatus.

## Question
Which REAL corpus is the best FAIR reasoning testbed -- i.e. has MATERIAL degree-stratified reach-ceiling
headroom over the frequency baseline ACROSS strata INCLUDING higher degree (frequency does NOT saturate the
info-ceiling the way FB15k-237's hubs do)? Rank a ladder of real corpora by fair-derivable-reasoning
headroom, benchmarked against the synthetic upper (compositional) and lower (freq-guessable) references. The
winner = our durable-escape reasoning-corpus candidate. MEASURE, do not assume.

## Apparatus (reused apples-to-apples)
Imports `headroom_table`, `build_syn_compositional`, `build_syn_freq_guessable`, `build_cskg_core_triples`,
`_table_digest`, `_mean_strata`, `_ensure_cskg` from `exp_cskg_dense_core_headroom_acceptance_v1`, which
imports `Graph`/`build_ids`/`mine_rules`/`reachable`/`pop_rank`/`_load_fb15k237`/`_load_triples` from
`exp_gt_induction_fb15k237_dense_v1` -- the SAME code path that produced the VET's FB15k-237 numbers and the
acceptance cell's synthetic anchors. Per held-out test edge (h, r, gold), stratified by GLOBAL degree
tertile of the gold TAIL: reach-ceiling / POP_RELFREQ (freq baseline) / HEADROOM (reachable AND freq-misses-
top-10). Identical MIN_SUPPORT=10 / MIN_CONF=0.10 thresholds (comparability, not tuned-for-pass).

## Ladder (each run through the IDENTICAL headroom apparatus, gold-tail degree-tertile stratified)
- **SYN_COMPOSITIONAL** -- upper reference; planted composition, UNIFORM tails; analytic headroom-HIGH at
  any scale. POSITIVE control. THEORETICAL@construction.
- **SYN_FREQ_GUESSABLE** -- lower reference; gold IS the freq-#1 tail; analytic headroom~0 at any scale.
  MUST-FAIL control (FB15k-237 hub failure mode, isolated + scale-invariant). THEORETICAL@construction.
- **FB15K237** -- villmow mirror (cached `data/fb15k237_testbed/`). Reference reproducer + real-corpus
  hub-collapse witness. CITED@notes VET aa7f151f: LOW 0.320 MID 0.299 HIGH 0.027 ALL 0.011.
- **WN18RR** -- villmow/Dettmers mirror (self-acquire). Sparse/hierarchical; expected LOW real-corpus
  must-fail witness (reported, not analytic gate).
- **CODEX_S / CODEX_M / CODEX_L** -- CoDEx Wikidata subsets (tsafavi/codex raw; self-acquire). Degree
  ladder within Wikidata (~36k / ~185k / ~551k triples).
- **CSKG_XCUT_CORE** -- CSKG cross-cutting commonsense k=12 dense core (Zenodo 4331372; self-acquire, size-
  gated). The acceptance candidate.
- **CONCEPTNET_SLICE** -- ConceptNet English slice (`data/datasets/conceptnet5_en_100k.jsonl`); BEST-EFFORT
  (recorded UNAVAILABLE if the local slice is absent on the remote host).

## Fair-headroom score + ranking
`fair_score = min(LOW, MID, HIGH) stratum headroom` (a durable reasoning testbed must not collapse at any
stratum, incl the hub end). Corpora ranked descending by (fair_score, HIGH headroom, ALL headroom). The two
synthetics are fixed upper/lower references (not ranked among the reals).

## Pre-registered bands (SURVEY / measurement; discriminator-gated)
Real-corpus headroom values are the UNMEASURED survey question (HYPOTHESIZED bands only). The VALIDITY
gate = the synthetic control pair (analytic, scale-invariant).

- **control_fires** (analytic hard gate): SYN_FREQ_GUESSABLE headroom_all <= 0.02 AND SYN_COMPOSITIONAL
  headroom_all >= 0.15. THEORETICAL@construction; verified at self-test (0.790/0.000) + smoke (0.860/0.000).
- **verdict = SURVEY_COMPLETE** iff control_fires AND >= 2 real corpora rank (ladder produced a ranking).
- **verdict = INCONCLUSIVE_CONTROL_BROKEN** iff NOT control_fires (apparatus auto-passing -> the whole
  survey is inconclusive, no ranking trusted).
- **verdict = INCONCLUSIVE_INSUFFICIENT_CORPORA** iff control_fires but < 2 real corpora reachable (staging
  failure, not a substrate result). [This is the CORRECT smoke verdict -- smoke ladder = 1 real rung.]
- **WN18RR real-corpus must-fail witness** (reported gate, not analytic): wn18rr_all_headroom <= 0.10.
  Expected to fire (sparse/hierarchical). If it does NOT fire, that is a genuine MEASURED finding surfaced
  in verdict_msg, not a crash -- the analytic discriminator rests on the SYNTHETIC anchors only.
- **Winner interpretation**: the top-ranked real corpus by fair_score is the durable-escape candidate; its
  fair_score / HIGH headroom are reported against the SYN upper ref (~0.79-0.86) and lower ref (0.0).

## Discriminator-survives-scale (option B: analytical justification)
The VALIDITY discriminator = the SYN control pair, SCALE-INVARIANT BY CONSTRUCTION: SYN_FREQ_GUESSABLE
headroom=0 exactly (gold IS the freq-#1 tail, reach=1.0 -> saturated hub failure mode) and SYN_COMPOSITIONAL
headroom>=0.79 (uniform tails, planted rule) at ANY N. Both fire at --self-test (0.790/0.000) AND smoke
(0.860/0.000, reach 1.0 -> saturated-not-vacuous). The real-corpus headroom values are MEASUREMENTS (the
survey question), not discriminator gates; previewing them would require the full ladder assembly = the
forbidden over-scoping (heavy data local) -> deferred to remote FULL. FB15k-237's hub-collapse (VET 0.027) +
WN18RR's expected sparse collapse are the real-corpus witnesses of the must-fail behavior at FULL. Satisfies
saturation-vacuous-smoke (the must-fail control fails at ANY scale, reach=1.0 confirms freq-saturation not
unreachability).

## Compute architecture
- Class **(b) sequential-CPU with justification**: pure symbolic relational hash-joins + dict lookups
  (mine_rules L2 path composition, reachable-set traversal, filtered ranking, iterative k-core degree-peel).
  NO substrate vectors, NO bind/unbind, NO matmul -- combinatorial graph traversal, not linear algebra.
- Storage strategy: **no_storage / no_composition**.

## SCHEMA-VET fields
- cardinality_ok: true. EXPECTED_N_UNITS = 3 seeds x N_real_reachable corpora + 2 synthetic anchors (no
  parameter sweep axis). Per-corpus per-seed table always has strata {low,mid,high,all}; a corpus whose data
  is unreachable is recorded status=UNAVAILABLE / ERROR:<class> and excluded from ranking (surfaced in
  gates.statuses + verdict_msg, NOT silently dropped). n_real_ranked logged.
- discriminator-fires (META_RULE_K): self-test D1 (SYN_COMPOSITIONAL headroom>=0.15 @ reach>=0.8) + D2
  (SYN_FREQ_GUESSABLE headroom<=0.02 @ reach>=0.8) + D3 (SYN tables differ) + D4 (ranking orders by
  min-strata then HIGH then ALL) -- ALL FIRE. MEASURED@selftest stdout (0.790/0.000, order A,C,B). Control
  fires at smoke too (0.860/0.000).
- baseline_in_band (META_RULE_AG): the frequency baseline (POP_RELFREQ) is a REFERENCE, not a saturating
  arm; SYN_FREQ_GUESSABLE headroom=0.000 is an INTENDED must-fail control; SYN_COMPOSITIONAL headroom=0.86
  is in-band (< 0.95). baseline_in_band: true.
- strictly-above-floor (META_RULE_L): control_fires uses a strict analytic pair (0.02 lower / 0.15 upper)
  with a wide 0.13 gap; not a floor-hug.
- HP_SCOPE: {SYN_FREQ_GUESSABLE: [control_fires-lower], SYN_COMPOSITIONAL: [control_fires-upper], WN18RR:
  [wn18rr_mustfail_witness-reported], <real candidates>: [ranked_by_fair_score]}. Each corpus gated only by
  its role's assertion; frequency baseline inherits NO pass gate.
- calibration_check (META_RULE_M): "default_ok_for_this_regime" -- MIN_SUPPORT=10 / MIN_CONF=0.10 are the
  SAME thresholds the FB15k-237 VET + CSKG acceptance cell used (comparability, not tuned-for-pass).
- crlb_n/a: "no quantitative substrate noise floor -- symbolic reach/frequency ranking, not a
  capacity/argmax-noise-limited readout."
- arms_differ_verified: true. ARMS-MUST-DIFFER over the available corpus tables at main() uses a FULL
  fingerprint (`_full_digest`: reach+pop+headroom+n per stratum) so genuinely-different arms sharing an
  all-zero headroom vector (a sparse capped smoke rung vs SYN_FREQ) are NOT false-flagged. table_digests
  (headroom-only, for logging) also written. Verified: smoke FB (reach0/pop0.367) != SYN_FREQ (reach1/pop~1).
- final_metrics_atomicity: "tmp_replace" (write_metrics + crash-diagnostic both write .tmp then os.replace).
- except-ordering: `except SystemExit: raise` then KeyboardInterrupt then `except Exception` (NOT
  BaseException). Grep-clean (verified: no bare `except:` / `except BaseException`). Per-corpus try/except
  records failure_class + continues the SURVEY (a partial ladder is a valid survey result; NOT a silent
  phantom-continue -- each failure is printed + recorded in gates.statuses).

## §13 defensive fields
- cell_chunked: false. JUSTIFICATION: this is a MEASUREMENT survey (not a capability claim); each corpus is
  best-effort and independently recorded; a runner death loses only the in-flight corpus's tables. Full
  crash-diagnostic + start-marker + heartbeat present (heartbeat after anchors, per corpus-seed, per corpus
  done). [FLAG for Skunkworks: multi-corpus-multi-seed-in-one-cell measurement.]
- start_marker_written: true. crash_diagnostic_present: true (Exception -> CELL_CRASHED + traceback,
  tmp+replace). heartbeat_present: true. defensive_error_checking: "passed_all_4_patterns".

## §15 test-design gates
- sweep_alignment_verdict: N/A (no parameter sweep; corpora + strata are not a swept axis). ALIGNED-by-vacuity.
- discriminating_fraction: N/A (no sweep). The discriminator is the SYN control PAIR, guaranteed to fire.
- composition_edges: load/self-acquire(corpus) -> (xcut+k-core for CSKG) -> split -> build_ids/Graph ->
  mine_rules -> reachable/pop_rank -> per-stratum accumulate -> mean-over-seeds -> rank. All SHAPE_MATCH
  (every loader emits the SAME (h,r,t) string-tuple list build_ids/Graph consume; verified by smoke
  completing FB end-to-end + self-test completing both synthetics).
- positive_control_arms (Gate D): FB15K237 arm IS the reproducer AT THE TEST REGIME (VET's exact
  Graph/mine_rules/reachable/pop_rank on the VET's exact corpus; cited VET {low 0.320 ... high 0.027}).
  Regime-extension audit: the other real corpora are NEW inputs (SHAPE_DRIFT from FB15k-237's named-entity
  relations to Wikidata/WordNet/commonsense relations) -- DECLARED risk; the apparatus (code path) is
  identical, only the input graph changes -- which is precisely what the survey measures.
- functional_requirements:
  1. assemble each ladder corpus              -> per-corpus loader (self-acquire / cached / k-core)
  2. define held-out edge prediction          -> canonical split (FB/WN/CoDEx) or random 90/5/5 (CSKG/CN)
  3. compute per-stratum reach-ceiling         -> mine_rules + reachable (imported VET apparatus)
  4. compute per-stratum frequency baseline    -> pop_rank over rel_tail_freq (imported VET apparatus)
  5. compute per-stratum HEADROOM              -> reachable AND pop-misses-top-10, by gold-tail deg tertile
  6. rank corpora by fair-derivable headroom   -> min-strata fair_score (self-test D4)
  7. prove the test discriminates              -> SYN_COMPOSITIONAL (fires) vs SYN_FREQ_GUESSABLE (must-fail)

## §16 run_mode
RUN_MODE defaults to "full" (runner invokes `python -u script.py`, no argv; `--smoke` local only, `--self-
test` local only). Post-dispatch: orchestrator verifies landed metrics run_mode=="full", size >= 5KB (FULL
writes per-corpus per-seed tables + syn anchors + ranking -> well above 5KB; smoke already 5.5KB).

## §17 progress_logging
FULL timeout >= 1800s (self-acquire + mine 6-8 corpora x 3 seeds incl CoDEx-L 551k + full CSKG 112MB stream +
k=12 core). MANDATORY field: progress_logging = "print_flush_true" -- `print(..., flush=True)` on config,
per-anchor, per-corpus-load, per-corpus-seed headroom line + `_heartbeat.jsonl` after anchors, per corpus-
seed, per corpus-done. Progress advances at least per corpus-seed (well under 60s cadence on smaller rungs;
CoDEx-L / CSKG minings are the coarse-grained units).

## SMOKE result (LOCAL; harness validation, offline, no downloads)
2 synthetic anchors + one capped-FB rung (15k train), 1 seed, 0.5s:
- control_fires=True: SYN_COMPOSITIONAL headroom_all=0.860 (reach 1.0), SYN_FREQ_GUESSABLE headroom_all=0.000
  (reach 1.0 -> saturated-not-vacuous). MEASURED@data/exp_multicorpus_reasoning_headroom_survey_v1_smoke/
  metrics.json:gates -> the DISCRIMINATOR FIRES at smoke.
- FB15K237 rung loaded (nodes=12982 edges=53001 train=15000) + stratified + ranked (capped -> headroom 0;
  HARNESS-ONLY, not an FB measurement). MEASURED@ same :real_per_seed.FB15K237.
- ARMS-MUST-DIFFER passed (full fingerprint distinguishes FB reach0/pop0.367 from SYN_FREQ reach1/pop~1).
- Ranking function unit test D4 passed (order A,C,B by min-strata). run_mode=smoke. verdict=INCONCLUSIVE_
  INSUFFICIENT_CORPORA (CORRECT for a 1-real-rung smoke ladder).

## Dispatch
- Smoke: LOCAL (this author), harness validated, control fires, ARMS-MUST-DIFFER + ranking + run_mode
  verified. PASS.
- FULL: canonical run -> **remote_cpu_queue** via orchestrator (local_cpu_queue is SMOKE-ONLY per USER lock;
  FULL self-acquires WN18RR/CoDEx-S/M/L + streams the 112MB CSKG + mines the k=12 core x 3 + FB x 3 ->
  heavy + LONG, route remote). Timeout 14400s (4h; generous for 6-8 corpora x 3 seeds incl CoDEx-L + full
  CSKG assembly on remote-CPU variance).
- queue_add command returned to orchestrator (exp_dev cannot push/SCP; orchestrator ships + verifies +
  pushes cell+prereg to origin/main first).
