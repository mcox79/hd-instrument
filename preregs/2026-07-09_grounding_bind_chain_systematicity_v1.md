# Pre-reg: grounding_bind_chain_systematicity_v1

Cell: `experiments/exp_grounding_bind_chain_systematicity_v1.py`
Anchor: `grounding_bind_chain_systematicity_v1`
Date: 2026-07-09
Queue target: `remote_cpu_queue` (pure CPU numpy/torch; no GPU speedup available)
Bands picked BEFORE the FULL run.

## Thesis (three interpretable numbers, one build)

The recurrent-settling cascade cell HARD_FAIL_NO_EXTENSION'd at FULL (reach_delta=0): a better
similarity-only readout did not break the 1-hop grounded-attribute cap, now confirmed across two
independent readouts. Three same-week research literatures converge on the same missing primitive:
an explicit, invertible role-filler bind/unbind operator that can be CHAINED (Fodor-Pylyshyn 1988;
Smolensky 1990; Plate HRR; Gayler VSA; Kanerva). This cell uses a VSA-native FHRR
(unit-modulus circular-convolution) bind/unbind operator, reusing `hdlab.binding.bind/unbind`
(complex dtype path; bit-identical, asserted in selftest), to produce:

1. REACH-DEEPENING (block 2, synthetic typed graph): does bind/unbind CHAINING deepen grounded-attribute
   reach past the 1-hop cap (beat settling's reach_delta=0)?
2. SYSTEMATICITY (block 1, synthetic role-filler): do novel held-out (role,filler) recombinations
   generalize (BIND) above a genuine flat-similarity control (FLAT_NN)?
3. ORACLE SKYLINE (block 3, REAL CN encoder codes): is hop-2/3 grounded signal even linearly present in
   the encoder codes (READOUT limit) or absent (ENCODER limit)? Director-requested arbiter.

## Compute architecture

Class: **(b) sequential-CPU with justification**. Substrate primitives here (FHRR elementwise bind/unbind,
cleanup matmul) are small (N <= 2048, n <= 800, F <= 60); block-3 encoder training is the reused CG'd
CPU pipeline (cert 06e5a493d). No GPU speedup regime (per-block wall < 10s except encoder train ~1-3
min/seed). Storage strategy: `no_storage` (no PartitionedStore writes); the bound node-memory / scenes are
in-RAM VSA vectors, not persisted atoms. Not a bundled-vs-sharded composition-store cell.

## Pre-registered bands

### Block 1 -- systematicity (cleanup top1 accuracy; chance = 1/F)
- SYS_HARD_PASS: bind_heldout >= 0.80 AND (bind_heldout - flat_heldout) >= 0.40 AND
  |bind_seen - bind_heldout| <= 0.15 AND flat_heldout <= 0.40, with flat_seen >= 0.50 (control-valid).
- SYS_HARD_FAIL: bind_heldout < 0.60 OR margin < 0.20.
- SYS_INCONCLUSIVE: flat_seen < 0.50 (flat control merely broken, not a fair baseline).
- Genuine flat-similarity control (NOT disguised binding): FLAT_NN returns the queried-role filler of the
  most cosine-similar TRAINING scene stored as a role-blind filler-superposition bundle. Handles SEEN
  (memorised) combos; fails held-out minimal-pair recombinations. NOBIND (role-blind cleanup) = floor.

### Block 2 -- bind-chain reach (ordering acc; chance = 0.5)
- REACH_HARD_PASS: reach(best non-collapsed D>=2) - reach(D=1) >= 1 AND the newly-reached bin clears
  REACH_THRESH=0.55 by >= 0.01 with genuine_margin (smooth - shuffled) >= 0.05 AND not over-smoothed.
- REACH_HARD_FAIL_NO_EXTENSION: reach_delta <= 0 (chaining does not add a hop -> structural, matches
  settling; escalate to encoder-level binding).
- REACH_HARD_FAIL_ALL_COLLAPSE: every D>=2 over-smooths (shuffled rises > 0.58 OR field flattens + near lost).
- Over-smoothing gate (honesty guard): shuffled attribute must stay < 0.58 at every D; a diffuse/collapsed
  field is detected via field_std_ratio + near-signal-loss. baseline_in_band: reach(D=1) <= 2 (a genuine
  one-shot cap to extend; else INCONCLUSIVE_NO_ONESHOT_CAP). Operator fidelity reported (edge_recall/precision
  of bind/unbind adjacency recovery; the SNR-limiting resource, telemetry-sensitive to N/degree).

### Block 3 -- oracle skyline (ridge decode ordering acc; chance = 0.5) -- DIAGNOSTIC (no pass/fail gate)
- READOUT_LIMIT flag: oracle_reach >= 2 while flat_oneshot_reach <= 1.5 (signal IS in encoder codes; a
  better operator can extract farther hops).
- ENCODER_LIMIT flag: oracle_reach <= 1.5 (even privileged decode cannot reach hop-2; fix is encoder-level;
  binding must happen at ENCODE time).

## SCHEMA-VET fields

- cardinality_ok: true; EXPECTED_N_UNITS = n_model_seeds (3 FULL); D-sweep + bin coverage asserted within-seed.
- arms_differ_verified: true (hash-test BIND vs FLAT vs NOBIND held-out preds; reach D=min vs D=max fields).
- arms_differ_exempted: none.
- final_metrics_atomicity: "tmp_replace" (via `_seed_checkpoint.write_metrics` + os.replace).
- except SystemExit: raise BEFORE except Exception; no BaseException, no bare except (grep-clean).
- crlb_n/a: "ordering-acc chance=0.5, cleanup top1 chance=1/F; discriminators are reach/decay-length vs a D=1
  control + shuffled empirical null + over-smoothing gate, held-out-recombination margin vs a flat control,
  and ridge-decodability skyline -- none is a closed-form estimator noise floor."
- discriminator_reachability: true (bands are within-capacity: FHRR cleanup of R<=8 bound pairs at N>=2048 is
  well above SNR floor; reach extension bounded by operator edge-recall which is measured, not assumed).
- baseline_in_band: true (reach D=1 caps at 1; FLAT_NN control-valid on seen yet fails held-out; shuffled ~ chance).
- calibration_check: "adaptive_with_discriminator_gate" (shuffled empirical null + attribute assortativity
  recomputed per run; over-smoothing collapse gate; FLAT_NN control-validity gate).
- cell_chunked: false (multi-seed within one cell via `_seed_checkpoint`; per-seed failure-class instrumented;
  seeds are cheap; runner-death loses at most the in-progress seed which write_partial checkpoints).
- start_marker_written: true. crash_diagnostic_present: true. heartbeat_present: false (blocks are short;
  per-block + per-seed flush logs provide progress cadence). defensive_error_checking:
  "start_marker + crash_diagnostic + per-seed failure-class; heartbeat exempt (short blocks, per-seed flush logs)".
- progress_logging: "print_flush_true" (all `_log` use flush=True + sys.stdout.reconfigure line_buffering;
  per-seed + per-block lines). FULL timeout 1800s.
- HP_SCOPE: {BIND: [SYS_HARD_PASS], FLAT_NN: [must-fail-heldout, control-valid-seen], NOBIND: [floor],
  BIND_CHAIN_Dge2: [REACH_HARD_PASS vs BIND_CHAIN_D1], SHUFFLED: [over-smoothing genuineness control],
  ORACLE: [diagnostic arbiter only, no gate]}.
- effective_vs_nominal_parameter_audit: swept D (chain depth) is the effective depth each propagation step
  experiences (ALIGNED); swept distance-bin is the effective graph distance to nearest seed (ALIGNED).
  sweep_alignment_verdict: ALIGNED.
- bracket_includes_discriminating_band: reach curves span [0, 0.8] across bins/D (>= 30% in [0.30,0.70]);
  systematicity BIND(1.0)/FLAT(0.0) straddle; discriminating_fraction >= 0.30.
- composition_edges: bind -> bundle -> unbind -> cleanup (SHAPE_MATCH, VSA-native, exact inverse on unit phasors).
- positive_control_arms: FHRR bind/unbind asserted bit-identical to hdlab.binding (reuse-fidelity, selftest);
  D=1 bind-chain = one-shot control reproducing the 1-hop cap; flat_oneshot on CN reproduces settling reach~1.
- functional_requirements: (i) recover a bound filler for a novel role-filler combo -> unbind+cleanup (binding);
  (ii) traverse a 2nd relational edge -> chained unbind over recovered typed adjacency; (iii) decide
  encoder-vs-readout -> privileged ridge skyline.

## Numbers (MEASURED at SMOKE; FULL bands pre-registered above)

- SMOKE verdict: SYS=SYS_HARD_PASS | REACH=REACH_HARD_PASS | ORACLE=READOUT_LIMIT
  MEASURED@data/exp_grounding_bind_chain_systematicity_v1_smoke/metrics.json:verdict
- systematicity margin (bind_heldout - flat_heldout) = 1.000, gen_gap = 0.000, nobind = 0.175
  MEASURED@...smoke/metrics.json:gates.sys_margin
- reach_delta = 3.0 (reach D=1 -> 1 ; best D*=4 -> 4), edge_precision = 1.000
  MEASURED@...smoke/metrics.json:gates.reach_delta
- oracle_reach = 3.0 ; flat_oneshot_reach = 1.5 -> READOUT_LIMIT
  MEASURED@...smoke/metrics.json:gates.oracle_reach
- settling baseline to beat: ONESHOT reach=1, reach_delta=0
  CITED@notes/research_grounding_cascade_depth_multihop_mechanism_2026-07-09.md + settling cell landed-VET
- Test-2 (bind-chain reach) P=0.30, systematicity P=0.25-0.30
  HYPOTHESIZED@notes/research_*_2026-07-09.md (deflated, capped 0.50)

## Honest limitation (report to Director)

Block 2 builds node memory from the TRUE typed edges (encode-time binding -- the note's thesis that binding
must be ENCODED to license hop-chaining). It demonstrates the OPERATOR can chain when structure is encoded;
it does NOT claim a binding readout extracts hop-2 from the current similarity-trained ENCODER codes. Block 3
(oracle) speaks to the real substrate: the signal IS linearly decodable at hop-2/3 (READOUT_LIMIT), which
motivates a binding-structured encoder/readout as the next construction. Framed as compositional
grounded-attribute propagation + systematic role-filler generalization, NOT "language understanding".
