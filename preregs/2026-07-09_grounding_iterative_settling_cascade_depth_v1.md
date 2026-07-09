# Pre-reg: Grounding cascade depth -- iterative recurrent-settling readout vs one-shot k-NN

- **Anchor:** `grounding_iterative_settling_cascade_depth_v1`
- **Cell:** `experiments/exp_grounding_iterative_settling_cascade_depth_v1.py`
- **Date:** 2026-07-09
- **Author:** exp_dev
- **Queue target:** `remote_cpu_queue` (CPU-only; tiny linear encoder + numpy diffusion; no GPU). Smoke ran LOCAL.
- **Source note:** `notes/research_grounding_cascade_depth_multihop_mechanism_2026-07-09.md` (Test 1 / Prediction 1: recurrent settling deepens reach).
- **Baseline extended:** `experiments/exp_grounding_snowball_transitive_inheritance_v1.py` (commit 89a088469). REUSED VERBATIM: `train_encoder` (CG teacher-free encoder 06e5a493d), CN 2-core subgraph, `make_smooth_attribute`, shuffled-grounding control, seed sets, `multi_source_bfs`/`distance_bins`, `label_propagation` (= the ONE-SHOT baseline arm), `ordering_accuracy`, `relational_auc`. ONLY the readout is new.

## Prior-work check (substrate-KB concept-query, mandatory)
`bash tools/substrate_query.sh "iterative recurrent settling diffusion label propagation multi-hop grounding readout attractor"` -> top hit cosine=0.3213 (`research_primitive_decision_linear_vs_recurrent_2026-05-25.md`). Read top 2 hits: they concern a RECURRENT-AUTOASSOC cleanup PRIMITIVE (modern-Hopfield / ACF resonator rescue at storage capacity K/N>1) -- a DIFFERENT mechanism than this cell's readout-time diffusion of a grounded attribute over a code-space kNN graph. **Prior-work check: top hits at cosine 0.32 are recurrent-CLEANUP-primitive notes, NOT grounding-propagation-readout; genuinely novel in this context (a rediscovery of neither).** Grep of `experiments/` found NO existing iterative/diffusion grounding-readout cell (existing recurrence cells = storage/retrieval, e.g. `exp_recurrent_vsa`, `exp_wave14b_r1_modern_hopfield`).

## Hypothesis (brain-grounded)
The just-shipped snowball cell measured a REAL but SHALLOW (~1 hop) transitive grounding (near d1=0.630, far d3=0.484 collapsed, decay=0.146) using a ONE-SHOT k-NN label-prop readout. Diffusion theory: one-shot realizes only the first spectral term of a random-walk expansion -> ~1-hop wall. Brain semantic memory (O'Connor/Cree/McRae 2009; Rogers 2021 eLife) SETTLES over ~20-28 recurrent ticks into a graded attractor; the deep signature appears only in the settled state. `P(settling lengthens reach) ~ 0.40` (deflated, capped 0.50; cheapest lever, readout-only). Both outcomes gold.

## The operator (NEW readout; SAME code space + SAME grounded seeds)
Build a code-space kNN affinity graph (each atom -> its `k_diffuse` nearest neighbours in code space, non-neg cosine weights); row-normalize to a random-walk transition `P = D^-1 W`. Sweep settling steps `T`:
- **ITER_SPREAD [MECHANISM]**: Zhou 2004 label spreading / APPNP (Klicpera 2019) with restart: `f^{t+1} = alpha*P f^t + (1-alpha)*y0`, `y0` = seed values at seeds / 0 elsewhere, `alpha=0.85`. The restart anchors the field to grounded seeds -> settles into a graded fixed-point attractor that propagates farther than one-shot WITHOUT diluting to the global mean. (A hard-clamped harmonic variant was tested first and REJECTED: over 30 sparse seeds it dilutes to a near-constant field, `field_std_ratio~0.017` -- a known-degenerate special case, not a fair settling operator. The restart operator is the over-smoothing-resistant one the note names.)
- **PURE_DIFFUSE [OVER-SMOOTHING POSITIVE CONTROL]**: `f <- P f`, NO restart. `P` row-stochastic -> `P^t f0 -> <stationary,f0>` = a CONSTANT field (global-mean collapse). MUST collapse at max T; it is the sensitivity witness that the over-smoothing detector FIRES.

## THE DISCRIMINATOR (the whole test)
Win signature = a LENGTHENED distance-decay: grounding reaches FARTHER hops WITHOUT over-smoothing. `reach` = farthest CONTIGUOUS hop (from d1 out) with ordering acc >= 0.55 AND genuine_margin (smooth - shuffled) >= 0.05. Distinguish:
- **(a) GENUINE deepened reach**: `reach_iter(T*) - reach_oneshot >= 1`, monotone preserved, genuine_margin preserved at T*, field NOT collapsed.
- **(b) OVER-SMOOTHING artifact**: apparent gain only at steps where the field collapses (field_std_ratio small AND near-signal lost) / SHUFFLED control rises / genuine_margin collapses.
`T*` = the step count with MAX reach among NON-collapsed T (smallest T on ties).

## Arms
- `ONESHOT` [BASELINE]: parent `label_propagation` (k=7 nearest grounded seeds) over ungrounded relational codes.
- `ITER_SPREAD@T` [MECHANISM]: label-spread settling, swept over T, over the SAME ungrounded codes + SAME seeds.
- `PURE_DIFFUSE@T` [OVER-SMOOTHING POSITIVE CONTROL]: no-restart diffusion, swept over T (must collapse at max T).
- SHUFFLED attribute (graph-smoothness destroyed) is the genuineness control for every arm.

## Pre-registered bands (picked BEFORE the FULL run)
Applied to `ITER_SPREAD` (smooth) vs `ONESHOT` (smooth); genuineness control = SHUFFLED; over-smoothing witness = PURE_DIFFUSE.
- `REACH_THRESH = 0.55` (a hop counts as grounded), `MARGIN_FLOOR = 0.05` (genuine_margin at a hop), `COLLAPSE_RATIO_MIN = 0.25`, `SHUF_MAX = 0.58`, `PURE_COLLAPSE_MAX = 0.20`, `alpha = 0.85`.
- **`HARD_PASS`**: `reach_delta >= 1` AND monotone-non-increasing at T* AND `margin@reach >= 0.05` AND NOT collapsed at T* AND the over-smoothing detector demonstrably fires on PURE_DIFFUSE AND **strictly-above-floor** (reach-bin acc >= 0.56 AND margin@reach >= 0.0525; META_RULE_L / PATTERN 3).
- **`MIDDLE_BAND_BANDFLOOR`**: reach_delta >= 1 with genuine margin + no over-smoothing but the reach bin is BAND-HUGGING (clears 0.55 by < 0.01) -> inconclusive, not a clean pass.
- **`HARD_FAIL_NO_EXTENSION`**: `reach_delta <= 0` at all non-collapsed T (1-hop is structural to near-random codes -> escalate to bind-chain build, Direction 2).
- **`HARD_FAIL_OVERSMOOTHING`**: every iterative T collapses via a genuine over-smoothing signature (shuffled rose OR field flattened + near lost).
- **`MIDDLE_BAND_GATE_NOT_FIRING`**: PURE_DIFFUSE did NOT collapse at max T -> cannot certify no-over-smoothing claims.
- **`PRECONDITION_FAIL`**: attribute assortativity smooth < 0.45 OR shuffled > 0.20.

## SMOKE evidence (LOCAL, MEASURED)
- SELFTEST_PASS (planted clustered-seed chain): oneshot_reach=2, best iter_reach=4, reach responds to T {1:0,2:1,4:1,8:2,16:2,32:4}, PURE_DIFFUSE fsr@Tmax=0.147 (< 0.20 -> over-smoothing detector fires), near_margin=0.342, telemetry_moves=True. MEASURED@`data/exp_grounding_iterative_settling_cascade_depth_v1_selftest/metrics.json`.
- SMOKE **MIDDLE_BAND_BANDFLOOR** (n=2143 CN 2-core, 2 model-seeds, 30 ground-seeds, d4+ empty): rel_auc=0.866. ONESHOT reach=1 curve [d1=0.627, d2=0.514, d3=0.496]. ITER_SPREAD T*=32 reach=2 (reach_delta=+1) curve [d1=0.628, d2=0.555, d3=0.515], margin@reach(d2)=0.059, monotone=True, fsr=0.005. SHUFFLED ITER flat across bins (0.49-0.54). OVERSMOOTH_DETECTOR_FIRES=True (PURE_DIFFUSE@Tmax fsr=0.000, collapsed via margin_near<0.05). MEASURED@`data/exp_grounding_iterative_settling_cascade_depth_v1_smoke/metrics.json`.
- **Interpretation (honest):** iterative settling DOES extend genuine grounding one more hop (d1->d2) with the shuffled control confirming graph-structure dependence and NO over-smoothing (PURE_DIFFUSE degrades d1 0.596->0.553 at high T while ITER_SPREAD holds 0.639->0.628). BUT at smoke's 30-seed scale the extension is BAND-HUGGING: d2 clears the 0.55 grounding floor by only 0.005. FULL's 4x seed density (120), better codes (code_dim 256 / 100 epochs), and populated d4+ bin are the material levers that resolve whether the reach extension is ROBUST (clean HARD_PASS) or marginal (MIDDLE_BAND). Both outcomes gold: HARD_PASS = a self-contained recipe to deepen grounding into a real cascade; HARD_FAIL/MIDDLE = 1-hop is (near-)structural to near-random codes -> next build is compositional bind/unbind chaining (Direction 2).

## Discriminator survives scale (DISCRIMINATOR-MUST-SURVIVE-SCALE)
Route (A): SMOKE=FULL branch parity -- smoke runs the identical code path; the DISCRIMINATOR FIRES at smoke (over-smoothing detector fires on PURE_DIFFUSE, telemetry responds to T, arms hash-differ, shuffled control flat, baseline in band). The MECHANISM magnitude (reach-bin acc above 0.55) is what FULL tightens via 4x grounding density -- the smoke deliberately does NOT pre-decide the mechanism verdict; it proves the machinery discriminates genuine reach from over-smoothing. No saturation risk (shuffled + far-hop sit at chance by construction).

## Compute architecture (mandatory)
- **Class: (b) sequential-CPU with justification.** Per-seed cost: one `n x n` cosine kNN build (MEASURED 1.37s at n=12000 via chunked topk; peak mem ~98MB/chunk) + tiny linear encoder (100 epochs, sub-second matmuls) + O(n*k*T) numpy diffusion (MEASURED 0.067s full T-sweep). GPU batching gives no material speedup (single matmul + gather; wall < 5 min at FULL). No GPU.
- **Storage strategy: `no_composition`** (per-atom codes are sharded rows; the settling readout is a kernel-diffusion over a fixed graph, NOT a bind/unbind chain).

## SCHEMA-VET fields
- `cardinality_ok`: true. `EXPECTED_N_UNITS = n_model_seeds` (smoke 2, full 5); the T-sweep is a WITHIN-unit axis covered in full via `len(t_sweep)` per seed. Verdict emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` if fewer seeds complete.
- `arms_differ_verified`: true (smoke; ONESHOT vs ITER_SPREAD@Tmax vs PURE_DIFFUSE@Tmax vs shuffled preds hash-checked distinct; META_RULE_AF). No exemptions.
- `final_metrics_atomicity`: `tmp_replace` (via `_seed_checkpoint.write_metrics` + `os.replace`; crash path atomic).
- `except SystemExit: raise` BEFORE `except Exception` (no `BaseException`); bare-except grep gate PASS.
- `crlb_n/a`: "ordering-accuracy chance floor = 0.5 by construction; the discriminator is the REACH/decay-length of the settled propagation vs a shuffled empirical null + an over-smoothing collapse gate, not a closed-form estimator noise floor."
- `discriminator_reachability`: true (HP bands are on the achievable side; smoke MEASURED reach_delta=+1 and the over-smoothing detector fires; the strict-above-floor gate is what smoke narrowly misses, resolved at FULL scale).
- `baseline_in_band`: true (ONESHOT near d1=0.627; shuffled control ~0.50 chance; far hops near chance -> headroom to extend).
- `calibration_check`: `adaptive_with_discriminator_gate` -- shuffled-attribute empirical null + attribute assortativity recomputed per run; the over-smoothing collapse gate is PROVEN to fire on the PURE_DIFFUSE positive control (not analytically assumed).
- `cell_chunked`: false (2-5 model-seeds in one cell; per-seed try/except with failure-class instrumentation + `write_partial` checkpoint; per-seed compute cheap + restartable).
- `start_marker_written`: true. `crash_diagnostic_present`: true (CELL_CRASHED metrics + traceback). `heartbeat_present`: true (`_cell_heartbeat.emit_heartbeat` during encoder training). `defensive_error_checking`: passed_all_4_patterns.
- `progress_logging`: `print_flush_true` (`_log` flush=True; `sys.stdout.reconfigure(line_buffering=True)`; explicit per-seed kNN-build + settling-sweep log lines). FULL wall < 5 min < 30 min so the timeout>=1800 mandate does not strictly bind; flushing implemented anyway.
- **Sweep/composition gates (Section 15):** sweep axis = T (settling steps). `sweep_alignment_verdict: ALIGNED` (T is the exact parameter each settling arm experiences; effective == nominal). `discriminating_fraction`: the smoke T-sweep places multiple T in the discriminating band (reach transitions 0->1->2 across T; PURE_DIFFUSE degrades across T) -> the axis discriminates (not by-construction saturated). `composition_edges: []` (no primitive->primitive shape-adapter chain; a single kernel-diffusion readout). `positive_control_arms`: (1) ONESHOT reproduces the parent snowball baseline AT THIS REGIME (near d1=0.627, matching parent 0.630); (2) PURE_DIFFUSE is a built-in over-smoothing positive control that MUST collapse at max T (MEASURED fsr->0.000). `functional_requirements`: (1) relational proximity in code space (met by reused encoder, rel_auc 0.866); (2) seed-anchored multi-step attribute propagation (met by label-spread settling); (3) over-smoothing rejection (met by the collapse gate + PURE_DIFFUSE control); (4) genuineness (met by the shuffled-attribute must-stay-flat control).

## Number tags
- rel_auc 0.866, ONESHOT near 0.627 / d2 0.514 / d3 0.496, ITER_SPREAD T*=32 near 0.628 / d2 0.555 / d3 0.515, margin@reach 0.059, reach_delta +1, PURE_DIFFUSE fsr@Tmax 0.000: MEASURED@`data/exp_grounding_iterative_settling_cascade_depth_v1_smoke/metrics.json`.
- SELFTEST oneshot_reach 2 / best iter_reach 4 / PURE fsr@Tmax 0.147: MEASURED@`data/exp_grounding_iterative_settling_cascade_depth_v1_selftest/metrics.json`.
- P(settling lengthens reach)=0.40: CITED@source note (deflated novel-synthesis estimate, capped 0.50).
- REACH_THRESH 0.55 / MARGIN_FLOOR 0.05 / reach_delta HP >= 1 / strict-above-floor 0.56 & 0.0525: HYPOTHESIZED@this prereg (bands picked before FULL; smoke MEASURED reach_delta=+1 but band-hugging -> MIDDLE_BAND_BANDFLOOR honestly).

## Direction 5 (SKIPPED, not trivial)
Curriculum / bridging-order re-binning requires betweenness-centrality on the graph + re-running propagation at seed-count checkpoints with a CHANGED seed set -- not a trivial secondary readout over already-collected data. Skipped per the task's "fold in ONLY if trivial, else skip"; flagged as a separate follow-up cell.

## FULL dispatch
- Queue: `remote_cpu_queue`. Timeout: 1800 s (>= 100x the MEASURED ~1-3 min FULL wall; kNN 1.37s/seed x 5 + tiny encoder).
- Expected: 5 seeds, n=12000, 120 ground-seeds, populated d4+ far bin. Resolves whether the +1-hop reach extension is ROBUST (clean HARD_PASS, strictly above floor) or marginal (MIDDLE_BAND) at 4x grounding density; a HARD_FAIL_NO_EXTENSION routes to the bind-chain build (Direction 2).
