# Pre-reg: native encoder ON THE GRAPH TASK (reframe) -- 2026-07-08

Cell: `experiments/exp_encoder_native_graph_task_retrieval_reframe_v1.py`
Seed wrappers (CHUNKED, one seed per cell):
`experiments/exp_encoder_native_graph_task_retrieval_reframe_v1_seed_{7,13,17}.py`
Anchor: `encoder_native_graph_task_retrieval_reframe_v1`

## Question (Director hand-off 2026-07-08, REFRAME -- questions the yardstick)

The native teacher-free encoder tops out at ret_agree10-vs-BGE ~ 0.199 (< 0.30 bar)
BUT it learned GRAPH-RELATIONAL structure BY DESIGN (modularity_z = 336
MEASURED@data/exp_encoder_native_gradedcode_ret_agree_v1_smoke_seed7_smoke/metrics.json:modularity_z.NATIVE_DENSE).
ret_agree10 measures AGREEMENT-WITH-BGE (distributional semantics). For the deep-prize
task (retrieval/reasoning over the GRAPH-structured ConceptNet KB), graph-relational
similarity may be the RIGHT target -- so ret_agree10-vs-BGE may be the WRONG yardstick.
MEASURE the native encoder ON THE TASK (graph-neighbor retrieval against GRAPH ground
truth), not against BGE. Measurement only -- no re-ingest, no operational flip.

## Task metric (GRAPH ground truth, NOT BGE-agreement)

Held-out link prediction. ConceptNet edges split TRAIN (80%) / TEST (20%). The native
encoder trains ONLY on TRAIN edges (never sees TEST -- held-out methodology, USER-LOCKED
11th rule). Retrieval quality = filtered Hits@10 + MRR of HELD-OUT (TEST) graph
neighbors: for each query node, rank all aligned candidates by encoder cosine, mask self
+ known TRAIN neighbors, measure whether the held-out TRUE graph neighbors surface in
top-10. This is the task's OWN graph-relational target (the retrieval the glass-box
multi-hop loop depends on).

## Encoders (4; + native graded reported alongside)

- `NATIVE_DENSE`  : trained native teacher-free encoder (graph InfoNCE + VICReg,
                    char-trigram surface, NO teacher), code_dim=4096. PRIMARY (reframe subject).
- `NATIVE_GRADED` : graded_block_code(NATIVE_DENSE, kb=32, blk_l=128, m=5). Reported alongside.
- `BGE`           : name-aligned BGE-large cached embeddings (distributional). Eval
                    comparator, NOT ingested. Used AS AN ENCODER on the graph task.
- `CHAR`          : raw hashed char-trigram bag (lexical; CURRENT operational default). FLOOR.

## Divergence discriminator (graph-relational != BGE-distributional)

A query is in the DIVERGENCE set if its held-out graph target is DISTRIBUTIONALLY FAR
under BGE (best target BGE rank > K_DIV=50). On this set the two notions genuinely
disagree; load-bearing question: does NATIVE still retrieve the graph target where
BGE-distributional cannot?

## Bands (pre-registered BEFORE full run)

Constants (in cell): TRAIN_FRAC=0.80, K_HITS=10, K_DIV=50, DIV_MIN=0.10,
COMPETE_EPS=0.02, BEAT_EPS=0.02, DIV_EPS=0.02, MIN_QUERIES=40, MIN_ALIGN_FRAC=0.50.

- **HARD_PASS_REFRAME_CONFIRMED** (FULL): `NATIVE_hits10 >= BGE_hits10 - COMPETE_EPS`
  (competitive-or-better) AND `NATIVE - CHAR >= BEAT_EPS` AND `BGE - CHAR >= BEAT_EPS`
  (both beat lexical default) AND discriminator fires. Strong sub-flag if
  `NATIVE_div - BGE_div >= DIV_EPS` (native wins exactly where notions diverge).
  Meaning: ret_agree10-vs-BGE was the WRONG yardstick; native is task-good; KB flip
  viable on task merit with NO external model.
- **HARD_FAIL_REFRAME_REJECTED** (FULL): `NATIVE_hits10 < BGE_hits10 - COMPETE_EPS` AND
  `NATIVE_div <= BGE_div + DIV_EPS` (worse overall AND on divergence). Meaning genuinely
  weak; strengthen teacher-free semantics FIRST.
- **MIDDLE_BAND**: native beats char and/or wins divergence but not cleanly
  competitive-or-better than BGE overall. Real graph-relational signal, partial reframe.

## Discriminator-fires (assert at smoke; task requirement)

(a) `divergence_frac >= DIV_MIN` (non-vacuous); (b) `max(NATIVE,BGE)_hits10 - CHAR_hits10
>= BEAT_EPS` (char floor underperforms); (c) `BGE_hits10_div < BGE_hits10 - 0.05`
(divergence set genuinely BGE's blind spot -- non-degenerate). SMOKE_GATE_FAIL on any
missing (or too few queries / low BGE-alignment). Native-vs-BGE reframe verdict is
FULL-authoritative (needs full training scale + multi-seed); smoke fires the
discriminator + previews.

## SMOKE RESULT (MEASURED@data/exp_encoder_native_graph_task_retrieval_reframe_v1_smoke_seed7_smoke/metrics.json)

verdict=HARD_PASS (SMOKE_MACHINERY_OK; discriminator FIRES). n_queries=1204, align_frac=1.0,
modularity_z(NATIVE,train)=397.5, divergence_frac=0.354, divergence_distinguishes=True.
- OVERALL Hits@10: NATIVE=0.1553, BGE=0.3111, CHAR=0.0951, GRADED=0.1314.
- DIVERGENCE Hits@10: NATIVE=0.0729, BGE=0.0000, CHAR=0.0169.
- MRR: NATIVE=0.1264, BGE=0.2528, CHAR=0.1069.
PREVIEW reading (NOT authoritative; native undertrained at smoke 200ep/2143n vs FULL
800ep/12000n): native WINS the divergence set (0.073 vs BGE 0.0, char 0.017 -> native
captures real graph structure BGE misses) but TRAILS BGE on the overall task at smoke
scale (native 0.155 < BGE 0.311). Whether full training closes the overall gap =
HARD_PASS vs MIDDLE_BAND is what the FULL run decides. HARD_FAIL_REFRAME_REJECTED is
NOT indicated (native does not lose the divergence set).

## SCHEMA-VET

- cardinality_ok: EXPECTED_N_UNITS=4 encoders (counted from per_encoder).
- arms_differ_verified: sha256 over float32 aligned code matrices.
- final_metrics_atomicity: tmp_replace (write_metrics os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException / bare except -- grep-clean).
- crlb_n_a: no closed-form noise floor; discriminator = Hits@10 agreement with GRAPH ground
  truth; chance floor = K_HITS/(Na-1) ~ 0.0047 (THEORETICAL). discriminator_reachability=True
  (eps bands 0.02 >> chance).
- baseline_in_band: AG saturate-high (baseline>0.95) CANNOT occur for filtered Hits@10 over
  ~2143 candidates; live risk is char being TOO strong (graph task lexically solvable),
  caught + reported by discriminator-fires gate (b). AG-exemption declared.
- discriminator survives scale: char-underperform + divergence set are STRUCTURAL (BGE
  cached; divergence a fixed property of BGE geometry vs graph). Smoke fired both at scale.
  Native-vs-BGE overall needs full training -> FULL-authoritative.
- HP strictly above floor: COMPETE_EPS/BEAT_EPS margins (META_RULE_L).
- HP_SCOPE: {NATIVE_DENSE: [reframe_confirmed_gate]}. BGE/CHAR/NATIVE_GRADED comparator/floor/diag.
- calibration_check: default_ok_for_this_regime (graded m=5 pinned; K_HITS=10/K_DIV=50 standard).
- cell_chunked: True (one seed per cell; sibling _seed_7/13/17 wrappers).
- start_marker_written / crash_diagnostic_present / heartbeat_present: True.
- progress_logging: print_flush_true (line-buffered stdout + flush=True).
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ above.

### Section 15 gates
- sweep_alignment_verdict: N/A (no parameter sweep; single held-out split per seed).
- discriminating_fraction: SMOKE MEASURED -- divergence_frac=0.354 and encoder Hits@10 in
  [0.095, 0.311] (all in the discriminating band [0.05,0.70], none saturated). >= 0.30 satisfied.
- composition_edges: N/A (no primitive->primitive composition; single encoder-retrieval measurement).
- positive_control: native train-edge assortativity modularity_z=397.5 MEASURED at smoke ->
  reproduces the parent's high graph structure (parent DENSE modz=336) at the test regime;
  confirms native learned genuine graph structure (Gate D reproduction AT TEST REGIME).
- functional_requirements: (1) "find the right ConceptNet graph neighbors for a query" ->
  addressed by native graph-InfoNCE encoder (trained on graph edges) + measured by held-out
  filtered Hits@10; (2) "distinguish graph-relational from distributional similarity" ->
  divergence set + BGE comparator; (3) "beat the current lexical operational default" ->
  char-trigram floor arm.

## Compute architecture

(c) MIXED. Native training sequential-CPU (SGD sequential dependency; single linear ProjHead;
parent teacher-free encoder CPU-only established). Retrieval Hits@k/MRR = chunked torch matmul
(device-agnostic; remote_cpu_queue runner). GPU speedup marginal for one linear layer.
Storage strategy: no_storage / no_composition (encoder-retrieval measurement; SHARDED-default N/A).
FULL routes to remote_cpu_queue. Remote dep note: cell imports
`experiments/exp_teacher_free_relational_encoder_cn_subgraph_v1.py` (native encoder parent,
Pattern-6 auto-SCP via explicit wrapper import) AND `hdlab/gsbc_graded_encoder.py` (NOT in
queue_add sibling auto-SCP allowlist -- orchestrator must ensure it is present on remote before
dispatch). BGE cache `data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz`
(1.35 GB) must also be present on the remote for the BGE + divergence arms.

## FULL dispatch (remote_cpu_queue; orchestrator ships -- exp_dev does not push)

3 seeds (7/13/17), one wrapper each. Timeout 7200s/seed (smoke train 110s at 200ep/2143n;
FULL 800ep/12000n/feat8192 ~ 16x train + larger retrieval; 1.5x headroom).
```
bash tools/orchestrator/queue_add.sh remote_cpu_queue encoder_native_graph_task_retrieval_reframe_v1_seed7  experiments/exp_encoder_native_graph_task_retrieval_reframe_v1_seed_7.py  preregs/2026-07-08_exp_encoder_native_graph_task_retrieval_reframe_v1.md 7200
bash tools/orchestrator/queue_add.sh remote_cpu_queue encoder_native_graph_task_retrieval_reframe_v1_seed13 experiments/exp_encoder_native_graph_task_retrieval_reframe_v1_seed_13.py preregs/2026-07-08_exp_encoder_native_graph_task_retrieval_reframe_v1.md 7200
bash tools/orchestrator/queue_add.sh remote_cpu_queue encoder_native_graph_task_retrieval_reframe_v1_seed17 experiments/exp_encoder_native_graph_task_retrieval_reframe_v1_seed_17.py preregs/2026-07-08_exp_encoder_native_graph_task_retrieval_reframe_v1.md 7200
```
