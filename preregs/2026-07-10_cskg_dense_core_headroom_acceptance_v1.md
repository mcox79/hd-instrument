# Pre-registration: cskg_dense_core_headroom_acceptance_v1

FAIRNESS / HEADROOM ACCEPTANCE TEST for the CSKG dense commonsense core, BEFORE committing to build a
reasoning engine on it. Runs in parallel with the FB15k-237 symbolic-ranking proof (afd0d1cd) -- different
corpus, no file conflict.

- **Cell**: `experiments/exp_cskg_dense_core_headroom_acceptance_v1.py`
- **Anchor**: `cskg_dense_core_headroom_acceptance_v1`
- **Corpus**: CSKG v1.0 merged graph, `data/grounding_testbed/cskg.tsv.gz` (MEASURED@disk 112,312,195 B,
  Zenodo 4331372; `PROVENANCE_cskg.md` co-located; self-acquire via curl if absent, size-gated). Restricted
  to the CROSS-CUTTING commonsense subgraph (the 20.9% spine; strips 79.1% lexical/taxonomic dilution) and
  further to its **k=12 dense core** (CITED@notes/cskg_commonsense_core_kcore_density_gate_2026-07-10.md:
  23,632 nodes @ avg-deg 38.4). Random 90/5/5 edge split per seed. FB15k-237 standard split reused for the
  side-by-side comparison / real-corpus must-fail witness.
- **Filed**: 2026-07-10 by hdi_exp_dev.

## Prior-work check (concept-query before authoring)
`bash tools/substrate_query.sh "CSKG commonsense dense core reasoning headroom frequency baseline degree
stratified reach ceiling"` top hits: generic language atoms `commonsense` (cosine 0.286), `dense` (0.284),
`CN_commonsense` (0.271), `reasoning` (0.259) -- ALL below the 0.30 prior-arc threshold; no prior
experiment cell on CSKG-headroom-acceptance. **Verdict: GENUINELY NOVEL** -- first fairness/headroom
acceptance test of the CSKG dense core; the FB15k-237 headroom apparatus (VET aa7f151f) is reused
apples-to-apples but was never applied to CSKG. Not a rediscovery.

## Question
The fairness VET (aa7f151f) proved FB15k-237's aggregate "beat frequency" bar is UNFAIR: its high-degree
hub tails are FREQUENCY-GUESSABLE by construction, so no path-reasoner can beat frequency where the answer
just IS the popular tail (VET degree-tertile HEADROOM: LOW 0.320, MID 0.299, HIGH 0.027, ALL 0.011 --
collapses at high degree). Before building a reasoning engine on CSKG, DOES the CSKG dense commonsense core
show MATERIAL reasoning-headroom over frequency ACROSS degree strata INCLUDING at higher degree (i.e.
frequency does NOT saturate/exceed the reach-ceiling the way FB15k-237's hubs do) -- making it a FAIR
reasoning testbed where inference can beat frequency? MEASURE, do not assume CSKG is better.

## Apparatus (reused apples-to-apples with the VET)
Imports `Graph`, `build_ids`, `mine_rules`, `reachable`, `pop_rank`, `_load_fb15k237` from
`experiments/exp_gt_induction_fb15k237_dense_v1.py` -- the SAME code path that produced the VET's
FB15k-237 numbers. Per held-out test edge (h, r, gold), stratified by GLOBAL degree tertile of the gold
TAIL (tertile bounds on the mined train graph, exactly as the VET's `headroom_recompute.py`):
- **reach-ceiling** = frac gold REACHABLE by ANY mined L1/L2 body pattern (pre-verifier), not filtered-known
- **POP_RELFREQ** = frac gold ranked top-10 by per-relation tail frequency (the frequency baseline)
- **HEADROOM** = frac gold REACHABLE by composition BUT POP misses top-10 (= additional hits@10 a perfect
  reasoner could WIN over frequency, per stratum) -- the exact VET metric.

## Arms / corpora (each run through the IDENTICAL headroom apparatus)
1. **CSKG_XCUT_CORE** -- CSKG cross-cutting subgraph @ k=12 dense core, 90/5/5 split. THE CANDIDATE.
2. **FB15K237** -- full FB15k-237 standard split (the VET's corpus). POSITIVE-CONTROL reproducer +
   real-corpus MUST-FAIL witness (HIGH stratum must reproduce its hub-collapse). FULL-only.
3. **SYN_COMPOSITIONAL** -- synthetic planted-composition corpus, UNIFORM (non-popular) tails: gold
   reachable-by-composition but NOT frequency-guessable. Analytically headroom-HIGH at ANY scale. POSITIVE
   control (apparatus DETECTS reasoning headroom).
4. **SYN_FREQ_GUESSABLE** -- synthetic corpus where gold IS the single dominant popular tail of its relation
   (reachable, but frequency ranks it #1). Analytically headroom~0 at ANY scale. MUST-FAIL control (the
   FB15k-237 hub failure mode, isolated + scale-invariant).

## Pre-registered bands (ACCEPTANCE test; fairness-gated)
All CSKG values = mean over 3 split seeds [7,17,23]. Bands are HYPOTHESIZED@this prereg (the CSKG headroom
is the unmeasured FULL question); the synthetic-control bands are THEORETICAL@construction (scale-invariant).

**ACCEPT** (ALL three):
- material_cross_strata: CSKG headroom HIGH >= 0.10 AND min(LOW,MID,HIGH) >= 0.05 (freq does NOT saturate
  at high degree -- HIGH >= 0.10 is materially above FB15k-237's 0.027 hub-collapse; the whole point)
- control_fires: SYN_FREQ_GUESSABLE headroom_all <= 0.02 AND SYN_COMPOSITIONAL headroom_all >= 0.15
- fb_reproduces_collapse: FB15k-237 HIGH stratum headroom <= 0.10 (real-corpus must-fail witness reproduces)

**REJECT** (ANY):
- reject_hub_saturates: CSKG headroom HIGH < 0.05 (freq saturates hubs like FB15k-237 -> UNFAIR at high
  degree -- CSKG is NOT a fair reasoning testbed after all)
- reject_no_reach: min(CSKG LOW,MID,HIGH) < 0.02 (no reasoning reach in some stratum)
- reject_control_broken: NOT control_fires (apparatus is broken / auto-passing -> result INCONCLUSIVE, not
  acceptance)

**MIDDLE_BAND**: otherwise (e.g. CSKG HIGH in [0.05, 0.10) -- partial headroom, weaker than FB15k-237's
low/mid strata but not the full hub-collapse; investigate before committing).

## SMOKE result (LOCAL; assembly + apparatus + control-fires validation)
Small CSKG slice (150k lines streamed, k-core=2, 1200-node cap), 1 seed, 1.3s:
- Assembly: core_nodes=1200 core_edges=2809 rels=18 train=2529 test=140
  MEASURED@data/exp_cskg_dense_core_headroom_acceptance_v1_smoke/metrics.json:cskg_provenance
- CSKG slice headroom LOW=0.077 MID=0.200 HIGH=0.156 ALL=0.129 (ceiling ALL=0.214, pop ALL=0.171)
  MEASURED@ same :cskg_per_seed[0].strata  [NOTE: tiny k=2 slice, NOT the acceptance measurement -- the
  real test is the FULL k=12 core with FB15k-237 side-by-side]
- control_fires: SYN_COMPOSITIONAL headroom_all=0.860, SYN_FREQ_GUESSABLE headroom_all=0.000 (both reach
  ceiling=1.0 -> saturated-not-vacuous) MEASURED@ same :syn_* -> control FIRES
- ARMS-MUST-DIFFER passed (no bit-identical tables); run_mode=smoke, verdict ACCEPT (on the slice).

## Discriminator-survives-scale (option B: analytical justification)
The test's VALIDITY discriminator = the SYN control pair (does the apparatus distinguish good-vs-bad
reasoning corpora), which is SCALE-INVARIANT BY CONSTRUCTION: SYN_FREQ_GUESSABLE headroom=0 exactly (gold IS
the freq-#1 tail, reach=1.0 -> saturated hub failure mode) and SYN_COMPOSITIONAL headroom>=0.79 (uniform
tails, planted rule) at ANY N -- both verified in --self-test AND at smoke. The CSKG headroom itself is a
MEASUREMENT (the FULL acceptance question), not a discriminator gate; previewing it would require assembling
the full 12-core, which is the explicitly-forbidden over-scoping trap -- so it is deferred to the remote FULL
run. FB15k-237's hub-collapse (VET 0.027) is the real-corpus witness of the same must-fail behavior at FULL.
This satisfies saturation-vacuous-smoke (the must-fail control fails at ANY scale, and reach=1.0 confirms it
fails because freq saturates, not because gold is unreachable).

## Compute architecture
- Class **(b) sequential-CPU with justification**: pure symbolic relational hash-joins + dict lookups
  (mine_rules L2 path composition, reachable-set traversal, filtered ranking) + an iterative degree-peel
  k-core (linear in edges). NO substrate vectors, NO bind/unbind, NO matmul -- nothing GPU-batchable.
  Same justification as the imported FB15k-237 STEP-1 cell.
- Storage strategy: **no_storage / no_composition** (symbolic graph index; no substrate vector store).

## SCHEMA-VET fields
- cardinality_ok: true. EXPECTED_N_UNITS = 3 seeds x {CSKG, FB15k-237} corpora + 2 synthetic controls (no
  parameter sweep axis). cskg_per_seed / fb15k237_per_seed lengths = len(SEEDS); strata dict per table
  always has {low,mid,high,all}.
- discriminator-fires (META_RULE_K): self-test D1 (SYN_COMPOSITIONAL headroom>=0.15 @ reach>=0.8) + D2
  (SYN_FREQ_GUESSABLE headroom<=0.02 @ reach>=0.8) + D3 (SYN tables differ) -- ALL FIRE
  MEASURED@selftest stdout (SYN_COMP=0.790, SYN_FREQ=0.000). Control fires at smoke too (0.860 / 0.000).
- baseline_in_band (META_RULE_AG): the frequency baseline (POP_RELFREQ) is a REFERENCE, not a saturating
  arm; SYN_FREQ_GUESSABLE headroom=0.000 is an INTENDED must-fail control (not a saturation breach);
  SYN_COMPOSITIONAL headroom=0.790 is in-band (not >=0.95). baseline_in_band: true (no arm auto-saturates
  the acceptance discriminator).
- strictly-above-floor (META_RULE_L): ACCEPT HIGH gate = 0.10, which is 2x the 0.05 REJECT floor + margin;
  material_cross_strata requires strict >= on a value well above the reject band, not a bare floor-hug.
- HP_SCOPE: {CSKG_XCUT_CORE: [material_cross_strata], SYN_FREQ_GUESSABLE: [control_fires-lower],
  SYN_COMPOSITIONAL: [control_fires-upper], FB15K237: [fb_reproduces_collapse]}. Each corpus is gated only
  by the assertion appropriate to its role; the frequency baseline inherits NO pass gate.
- calibration_check (META_RULE_M): "default_ok_for_this_regime" -- MIN_SUPPORT=10 / MIN_CONF=0.10 are the
  SAME thresholds the FB15k-237 VET used (apples-to-apples); reusing them is required for comparability, not
  tuned-for-pass. The synthetic controls verify the apparatus discriminates at these values.
- crlb_n/a: "no quantitative substrate noise floor -- symbolic reach/frequency ranking, not a
  capacity/argmax-noise-limited readout."
- arms_differ_verified: true. ARMS-MUST-DIFFER hash-test over the 4 corpus headroom tables at main() (SYN,
  CSKG, FB) -- asserts no two are bit-identical; SYN_COMP (0.79) vs SYN_FREQ (0.00) vs CSKG-slice (0.13)
  already differ at smoke. table_digests logged to metrics.
- final_metrics_atomicity: "tmp_replace" (write_metrics + crash-diagnostic both write .tmp then os.replace).
- except-ordering: `except SystemExit: raise` then KeyboardInterrupt then `except Exception` (NOT
  BaseException). Grep-clean (verified: no bare `except:` / `except BaseException`).

## §13 defensive fields
- cell_chunked: false. JUSTIFICATION: the dominant cost (streaming CSKG once + k-core + L2 mining) is
  re-run per split-seed but each seed is a full independent measurement; there is no per-seed shared-state to
  lose, and a runner death loses only the incomplete seed's metrics (already-completed per-seed tables are
  in memory only until final write -- acceptable for a measurement cell, not a capability-claim cell). Full
  crash-diagnostic + start-marker + heartbeat present. [FLAG for Skunkworks: multi-seed-in-one-cell.]
- start_marker_written: true (`_start_marker.json` at main() entry).
- crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics.json + traceback, tmp+replace).
- heartbeat_present: true (`_heartbeat.jsonl` after controls, per CSKG seed, per FB seed).
- defensive_error_checking: "passed_all_4_patterns".

## §15 test-design gates
- sweep_alignment_verdict: N/A (no parameter sweep; corpora + strata are not a swept axis). ALIGNED-by-vacuity.
- discriminating_fraction: N/A (no sweep). The discriminator is the SYN control PAIR, guaranteed to fire.
- composition_edges: stream(CSKG) -> xcut-filter -> k-core-peel -> split -> Graph -> mine_rules ->
  reachable/pop_rank -> per-stratum accumulate. All SHAPE_MATCH (Python triple-lists / dict adjacency;
  the CSKG triple loader emits the SAME (h,r,t) string-tuple shape build_ids/Graph consume -- verified by
  the smoke run completing the apparatus end-to-end).
- positive_control_arms (Gate D): FB15K237 arm IS the positive-control reproducer AT THE TEST REGIME --
  reuses the VET's exact Graph/mine_rules/reachable/pop_rank on the VET's exact corpus; cited prior VET
  table {low 0.320, mid 0.299, high 0.027, all 0.011}; fb_reproduces_collapse gate (HIGH <= 0.10) checks the
  hub-collapse reproduces. Regime-extension audit: CSKG is a NEW corpus (SHAPE_DRIFT from FB15k-237's
  named-entity relations to CSKG commonsense relations) -- this is DECLARED risk and is precisely what the
  acceptance test measures; the apparatus (code path) is identical, only the input graph changes.
- functional_requirements:
  1. assemble the candidate reasoning core   -> stream CSKG -> xcut relation filter -> k=12 core peel
  2. define held-out edge prediction         -> random 90/5/5 edge split per seed
  3. compute per-stratum reach-ceiling        -> mine_rules + reachable (imported VET apparatus)
  4. compute per-stratum frequency baseline   -> pop_rank over rel_tail_freq (imported VET apparatus)
  5. compute per-stratum HEADROOM             -> reachable AND pop-misses-top-10, by gold-tail deg tertile
  6. prove the test discriminates             -> SYN_COMPOSITIONAL (fires) vs SYN_FREQ_GUESSABLE (must-fail)

## §16 run_mode
RUN_MODE defaults to "full" (runner invokes `python -u script.py`, no argv; `--smoke` only local, `--self-
test` only local). Post-dispatch: orchestrator verifies landed metrics run_mode=="full", size >= 5KB (FULL
writes per-seed CSKG + FB tables + syn tables -> well above 5KB).

## §17 progress_logging
FULL timeout >= 1800s (full CSKG stream + k-core + L2 mining per seed x 3 + FB15k-237 x 3). MANDATORY field:
progress_logging = "print_flush_true" -- `print(..., flush=True)` on config, per-control, per-seed CSKG +
per-seed FB lines + a `_heartbeat.jsonl` write after controls and per seed. Progress advances every seed.

## Dispatch
- Smoke: LOCAL (this author), verdict ACCEPT on the slice, control fires, ARMS-MUST-DIFFER + run_mode
  verified. Assembly + apparatus validated.
- FULL: canonical run -> **remote_cpu_queue** via orchestrator (local_cpu_queue is SMOKE-ONLY per USER lock;
  FULL streams the whole 112MB graph + mines the ~23.6k-node core x 3 seeds + FB15k-237 x 3 -> heavy, route
  remote). Timeout 5400s (90min; generous for the full stream + k-core + 6 minings on remote-CPU variance).
- queue_add command returned to orchestrator below (exp_dev cannot push/SCP; orchestrator ships + verifies).
