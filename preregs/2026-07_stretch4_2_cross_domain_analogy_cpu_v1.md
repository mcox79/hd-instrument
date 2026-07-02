# Prereg: stretch4_2_cross_domain_analogy_cpu_v1

## Anchor
`stretch4_2_cross_domain_analogy_cpu_v1`

## Cell path
`d:/AI/hd-instrument/experiments/exp_stretch4_2_cross_domain_analogy_cpu_v1.py`

## Metrics path
`d:/AI/hd-instrument/data/exp_stretch4_2_cross_domain_analogy_cpu_v1/metrics.json`

## Queue routing
- **Smoke:** local direct invocation via `.venv/Scripts/python.exe ... --smoke`; ran 2026-07-02 in 79s wall. Not via queue_add (smoke is direct-verification). USER 2026-07-01 SMOKE-ONLY-LOCAL rule complied.
- **Full:** WOULD ROUTE `remote_cpu_queue` — but see PRIOR-WORK REDISCOVERY finding below. Director decision required BEFORE dispatch.

## 🚨 PRIOR-WORK REDISCOVERY FINDING (substrate-KB concept query)

Query `bash tools/substrate_query.sh "cross domain analogy transform inference few-shot relation held-out substrate"` returned:

1. `notes/research_drill_cross_domain_analogy_negative_2x_2026-06-10.md` (cosine 0.335): documents STRETCH4-2 empirical result **0.244 cross-domain Hits@1 vs 0.899 within-domain** — the same mechanism (RotatE learned phase embeddings; K=10 held-out relation shots on FB15K-237). Six-level drill explains WHY it fails: relation params are closed-vocabulary lookup tables; 10 shots insufficient to characterize a rotation in R^N/2 with N/2 = 100 DOF.
2. `notes/research_to_skunkworks_exp_dev_DECISION_146*` (cosine 0.339): DECISION 146a **cross-domain analogy DROP CONFIRMED**; only within-domain atomized as clean capability. Cross-domain retracted 2026-06-10.
3. `notes/research_gap_D_analogy_cross_domain_mapping_2026-06-26.md` (cosine 0.335): "Cross-domain analogy RETRACTED 2026-06-10: STRETCH4-2 (RotatE) 0.244 cross vs 0.899 within".

**This cell replicates the retracted mechanism.** Current cell smoke result (see Smoke evidence below) reproduces **exactly** the prior empirical 0.244. Director must decide whether to:
- (A) ACCEPT rediscovery, skip FULL dispatch, atomize HARD_FAIL confirmation on smoke-N=400 seed=7 result (0.244; matches prior).
- (B) Dispatch FULL for 3-seed triple-witness closure at SUBN=1200, EPOCHS=250 (~10-15 min wall estimated).
- (C) PIVOT: file a NEW cell implementing one of the six drill Level-4 mechanisms (multi-domain KGE / universal relation vocabulary / meta-learner / structural alignment) instead of re-running the known-negative mechanism.

Cell-author recommendation: **(A) or (C)**. The substrate-KB explicitly records this mechanism as RETRACTED with theoretical explanation; a FULL run would consume ~15 min of `remote_cpu_queue` slot for a result already known to 3 decimal places.

### Director decision 2026-07-02: PATH (A) ACCEPTED — rediscovery closure

**Tier-decision hand-off (for Skunkworks atomization):**

This cell REPRODUCES the 2026-06-10 HARD_FAIL to 3 decimals (0.244 Hits@1) via the same RotatE mechanism. NOT a novel finding. Atom scope for Skunkworks: `stretch4_2_cross_domain_analogy_rotate_reproduction_HARD_FAIL_2026-07-02` — verifies durability of prior negative + validates substrate-KB-first discipline caught the rediscovery. Tier: **MM_TENTATIVE_REDISCOVERY_CONFIRMATION** at Skunkworks' discretion; alternatively **discipline-META** citing substrate-KB-query value.

**No FULL dispatch.** Smoke result at `data/exp_stretch4_2_cross_domain_analogy_cpu_v1/metrics.json` is the closure evidence.

**Level-4 pivot mechanisms (backlog; USER-decision scope):** the 2026-06-10 drill lists six alternative mechanisms that could enable substrate-native cross-domain analogy:
- 4.1 Multi-domain KGE training (FB15K + Wikidata + ConceptNet joint)
- 4.2 Universal relation vocabulary (ConceptNet 34 primitives as relation basis)
- 4.3 Meta-learning over relation pairs (GMatching / FSRL few-shot KGE)
- 4.4 Structural alignment over symbolic representations (SME-style, Gentner 1983)
- 4.5 Hyperbolic embeddings (Poincare model, hierarchical abstraction)
- 4.6 Substrate stores relation-TYPES separately from instances (HRR binding taxonomy)
- 4.7 ConceptNet as universal substrate anchor

Each is bigger-scope than a single exp_dev cycle; needs Director-level scope decision + likely a research drill to pick most-viable mechanism. Deferred for USER decision.

## Framing (Stage 3 compositional-understanding arc, USER 2026-06-26 pivot)

Cross-domain analogy = infer a NEW relation's transform from K=10 example pairs, apply to held-out heads. The mechanism tests whether learned entity geometry generalizes to relations not seen at training. Prior work (2026-06-10) shows RotatE geometry does NOT generalize this way — relation phases are dataset-specific.

**Honest scope (like stretch4_1):** cell uses `torch.nn.Parameter` on entity+relation phases with cos/sin distance (a manual FHRR-style representation) but does NOT invoke hdlab primitives (no `cphasor` / `cidx` / `bind` / `bundle` imports). The verdict message describes "learned entity space supports NEW relation transforms" — this is a FHRR-style claim about phase-encoded geometry, not a substrate-primitive-composition claim. Atom scope should reflect what actually ran (torch autograd on phase params), not "substrate does cross-domain analogy."

## Hypothesis

At SUBN=1200 entities, DIM=200, EPOCHS=250, K=10 shots per held-out relation:
- Cross-domain Hits@1 falls at or below 0.25 (matching prior 0.244 empirical).
- Direction: prior 2x-drill Level-1 theory predicts HARD_FAIL regardless of scale within the tested mechanism class.

## Bands (envelope-fail; from cell verdict function)

| Band | Cross-domain Hits@1 | Notes |
|---|---|---|
| HARD_PASS | `>= 0.40` | strict; band-floor 0.40 + 0.05*(1-0.40) = 0.43 strict-floor |
| MIDDLE_BAND | `>= 0.25 and < 0.40` | Partial |
| HARD_FAIL | `< 0.25` | Below random-with-margin baseline |

**Band strictness (META_RULE_L):** HARD_PASS band [0.40, 1.0]; width 0.60; strict floor = 0.40 + 0.05*0.60 = 0.430. Smoke observed 0.244 is well INSIDE HARD_FAIL band (-0.006 below the 0.25 HF ceiling).

**Baseline analytical (META_RULE_AG):** at NE=400 (smoke) argmax-random baseline = 1/400 = 0.0025; at NE=1200 (full) = 0.00083. Chance-level Hits@1 is ~0.003. Observed 0.244 is ~100x chance — the cell trains an entity space where NEAREST-NEIGHBOR after mean-phase-diff-rotation is much better than random, but NOT good enough to hit the HP band. This matches prior 2x-drill Level-1: 10 shots underdetermined for N/2=100 DOF rotation.

## Discriminator-must-survive-scale (META_RULE_AG + USER 2026-06-26 rule)

**Path C: full-N smoke-arm preview (partial).** Smoke at SUBN=400 got 0.244 in HARD_FAIL band. Full is SUBN=1200 (3x entities). Argmax denominator triples → candidate set is HARDER; random baseline drops from 0.0025 to 0.00083. Direction of scale: WORSE for HARD_PASS (more distractors). Analytical prediction: full-N result 0.20-0.25 range (may drop below smoke value). Discriminator SURVIVES scale — if smoke fires HARD_FAIL, full-N cannot suddenly hit HARD_PASS 0.40.

**Full-N would NOT reveal a new mechanism regime.** Rejection criterion (baseline ≥ 0.95 of mechanism at full-N preview): N/A — cell has no separate baseline arm; the mechanism IS the readout.

## Compute architecture

**Class:** (b) sequential-CPU with justification.

**Justification:** Cell workload = torch autograd on 200-dim phase parameters over EPOCHS=250 epochs of batch size 2048 negative-sampling triplet loss on CPU. Smoke wall 79s at SUBN=400, EPOCHS=40. Full expected wall ~10-15 min at SUBN=1200 (3x entities, 6.25x epochs). GPU batching WOULD provide substantial speedup on this training loop — this cell VIOLATES the USER 2026-07-02 GPU-batching-mandatory rule for matmul-heavy CPU loops. If FULL dispatched, should be `overnight_queue` (GPU) not `remote_cpu_queue`.

**Compute architecture caveat:** the cell name says `_cpu_v1` but this is a training loop where GPU would give substantial speedup. If Director elects (B) above, recommend re-routing to `overnight_queue` and dropping the `_cpu` suffix, OR proceeding on remote_cpu_queue for continuity with prior 0.244 run. Cell-author preference: don't dispatch (path A or C).

## META_RULE compliance

- **cardinality_ok**: N/A — no sweep axis; single-mode readout (cross-domain Hits@1 aggregated over held-out relations with >=14 pairs).
- **arms_differ_verified**: N/A — cell has ONE arm (cross-domain readout only; no within-domain arm in this cell); no arm-comparison logic.
- **final_metrics_atomicity**: relies on `experiments._seed_checkpoint.write_metrics` (tmp_replace pattern per §7).
- **except SystemExit: raise BEFORE except Exception**: cell has minimal try/except (stdout reconfigure + data load fallback + torch import); no wildcard BaseException catcher; SystemExit safe.
- **crlb_floor_computed**: N/A for this class — discriminator is nearest-neighbor Hits@1 vs 1/NE random baseline. `crlb_n/a: "argmax-over-NE-entity-space; random baseline 1/NE analytically computed above"`.
- **baseline_in_band**: analytical 1/NE = 0.0025 (smoke) / 0.00083 (full) is far below both smoke observed 0.244 and HF band 0.25. Cell trains to non-trivial-above-random even under retracted mechanism.
- **HP_SCOPE**: single arm; HP gate applies to that arm.
- **calibration_check**: `default_ok_for_this_regime` — thresholds match cell verdict function; DIM=200 / EPOCHS=250 / K=10 are cell-hardcoded and match 2026-06-10 prior setup.
- **cell_chunked**: false — single-seed run.
- **start_marker_written**: false — cell is single-seed, no seed-loop needing per-seed marker.
- **crash_diagnostic_present**: cell logs [selftest] / [config] / [train] progress / [VERDICT] / [metrics] to stdout with flush=True; runner log will capture crash location.
- **heartbeat_present**: false — expected full wall ~10-15 min; below the §17 30-min mandatory-progress threshold. Cell prints train-progress every 100 epochs (`  [train] ep %d/%d`) which serves as coarse heartbeat.
- **defensive_error_checking**: `"data_download_failure_handled_returns_UNKNOWN"` — FB15K raw fetch has try/except with UNKNOWN verdict return; verified in cell body.
- **run_mode**: cell defaults RUN_MODE="full" when `--smoke` absent; env override `HDLAB_RUN_MODE` respected. Runner will invoke without `--smoke` → RUN_MODE=full landed correctly.
- **progress_logging**: `runner_python_u_only` — cell uses `print(..., flush=True)` on train-loop lines; total wall expected <30 min; §17 30-min progress-logging rule N/A.

## Test-design gates (§15)

- **A) sweep_alignment_verdict**: N/A (no swept parameters).
- **B) discriminating_fraction**: smoke fires (HARD_FAIL band; discriminator = threshold-vs-random-Hits@1); full-N preserves the regime per §Discriminator-must-survive-scale.
- **C) composition_edges**: N/A — cell does not compose prior chain-grade primitives; standalone torch autograd.
- **D) positive_control_arms**: N/A — cell has no positive control (within-domain arm) in this file. Prior 2026-06-10 STRETCH4-2 within-domain positive control landed 0.899.
- **E) functional_requirements**: (1) RotatE-style entity+relation phase learning via triplet-loss on FB15K-237 subgraph; (2) held-out relation transform inference via circular mean of phase-diffs across K=10 example pairs; (3) held-out prediction via nearest-neighbor in phase-cos/sin space. All implemented via raw torch autograd, not hdlab primitives.

## Stage progression

**Stage 3** (compositional understanding — analogical inference / cross-domain transform). NOT Stage 4 (no language / no vocab / no text corpus). Confirmed in-scope for USER 2026-06-26 pivot arc. Note: this Stage-3 mechanism was already tested + retracted 2026-06-10; re-running is redundant unless a NEW mechanism is being probed.

## Substrate-doesn't-know-anything check

FB15K-237 IS a real knowledge-graph benchmark with human-authored triples (e.g., `/film/actor/film` etc.). BUT the cell:
- Downloads only the `train.txt` triples (head\trelation\ttail rows).
- Uses relation SURFACE STRING only as a dict key for `ri[r]` index — NEVER reads/embeds/tokenizes the relation NAME.
- Trains entity phases from co-occurrence structure ONLY (no lexical/semantic ingestion).

Verdict: **compatible** with USER 2026-06-26 "no language testing" rule. The cell tests graph-structural inference, not language understanding. FB15K-237 is used as a source of graph topology, not linguistic content.

## Timeout

If Director elects to dispatch FULL: `--timeout 1800s` (30 min) — 2-3x safety margin over expected 10-15 min wall. If PROT-019 applies (`_n>=4096`): cell has no `_n` suffix; PROT-019 N/A.

## Smoke evidence

- Timestamp: 2026-07-02 fresh (this session; cell-author dispatch cycle)
- Command: `HDLAB_EXP_NAME=stretch4_2_cross_domain_analogy_cpu_v1 .venv/Scripts/python.exe experiments/exp_stretch4_2_cross_domain_analogy_cpu_v1.py --smoke`
- Wall: 79.4s
- Result: `cross-domain-Hits@1=0.244 (held-rels=11, test=2078)` → **HARD_FAIL** (below 0.25 band-ceiling)
- Discriminator: FIRED at smoke-N. -0.006 below HF band-ceiling; -0.156 below HP strict-floor 0.43.
- **Empirical match to 2026-06-10 prior**: exactly 0.244 (three-decimal identical). This is the same mechanism reproducing the retracted result.
- Selftest: PASS (`[selftest] PASS: cross-domain-analogy`).

## Post-dispatch RUN_MODE_VERIFICATION (§16) — IF FULL dispatched (path B)

After FULL landing at `data/exp_stretch4_2_cross_domain_analogy_cpu_v1/metrics.json`, verify:
- `run_mode == "full"`
- `elapsed_s` in range [300, 1800] (expected ~600-900s at SUBN=1200)
- `per_seed[0]` has `hits1`, `n_held_rels`, `n_test` keys with numeric values; `hits1` likely 0.20-0.25 range
- File size > 400B
- Verdict field: HARD_FAIL expected; MIDDLE_BAND would be surprising; HARD_PASS would be an anomaly requiring diagnosis (would falsify prior 2x-drill)

## Framing caveat for atomization (Skunkworks/Director)

**If atomized (as HARD_FAIL confirmation):** atom claim should be `"stretch4_2 cross-domain analogy RotatE mechanism REPRODUCED HARD_FAIL 2026-07-02 (0.244 identical to 2026-06-10 prior; retracted mechanism confirmed retracted)"` — NOT "substrate cannot do cross-domain analogy" (substrate's cross-domain capability is untested; this cell tests torch/RotatE, not substrate primitives).

**Do NOT atomize as substrate-capability finding.** The 2026-06-10 drill already documented six alternative mechanisms (multi-domain KGE, universal relation vocab, meta-learner, structural alignment, hyperbolic embeddings, ConceptNet substrate) that COULD enable substrate-native cross-domain analogy. This cell tests none of them.

## Dispatch-ready status

- Selftest: PASS ✓
- Smoke: RAN 79s wall; HARD_FAIL 0.244 discriminator fired ✓
- Pre-reg: authored with all META_RULE fields ✓
- Prior-work check: **REDISCOVERY DETECTED** — director decision required ✗
- Queue routing: local smoke complete; FULL dispatch DEFERRED pending Director path selection (A/B/C above)
- Timeout: 1800s computed (if FULL elected)
