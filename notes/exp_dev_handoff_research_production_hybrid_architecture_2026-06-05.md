# exp_dev hand-off -- research: production substrate-LLM hybrid architecture (2x depth)

Filed-by: research sub-agent (2026-06-05)
Trigger: notes/research_drill_production_substrate_llm_hybrid_architecture_at_scale_2x_2026-06-05.md

Pause state: CHECK data/orchestrator_paused.flag before dispatching any anchor below.

Per [[feedback-no-experiment-design-in-prompts]]: anchor candidates below specify WHAT to test and WHY. exp_dev decides HOW (sweep grids, thresholds, queue routing, timing). Do not encode anchor-internal design choices here.

---

## ANCHOR CANDIDATES (rank-ordered)

### ANCHOR 1 (Tier 1, CPU feasible, HIGHEST PRIORITY)
Pointer: Two-bridge hybrid smoke test (Config B scaled down: D=2, N=65536, M=10K)
Substrate-product reading: Validates that Bridge 2 KV injection at layers 8/10/12 of Gemma-2-2B adds >=5pp on 3-hop QA vs text-injection only. First empirical test of the KV bridge at the recommended LLM+layer configuration.
Tier hint: CPU feasible (substrate ops); small GPU recommended for Gemma-2-2B inference. ~30 min with GPU.
Why now: Phase 3 production architecture specifies this exact bridge config. Validating it at small scale before building full D=8 system is the correct rung-1 test. P_deflated=0.33 -- needs empirical check before Phase 3 build.
Pre-reg bands (to be finalized by exp_dev):
  HARD-PASS direction: Bridge 2 adds >=5pp accuracy.
  MIDDLE-BAND: Bridge 2 adds 2-5pp -- partial benefit, adjust injection heads or layers.
  HARD-FAIL: Bridge 2 adds <2pp -- text-injection sufficient; Bridge 2 not warranted.

### ANCHOR 2 (Tier 1, CPU feasible)
Pointer: Config B capacity sweep -- D=2 or D=4, N=65536, n=3 cubic write, M sweep from 10K to 10M
Substrate-product reading: Validates that n=3 cubic Hebbian write achieves M_max ~ N^2 scaling (100M+ capacity at N=65536). Key open question -- n=3 interaction never validated at this N. Also tests whether D-parallel aggregation achieves error compensation per arXiv:2604.25470.
Tier hint: CPU feasible for D=2, N=65536 at 1-bit storage. Sweep M over ~10 values. ~60 min CPU.
Why now: Without n=3 validation, Phase 3 substrate architecture is algebraic-only. This is the cheapest decisive test.
Pre-reg bands:
  HARD-PASS direction: <5% error at M=100M per substrate with n=3.
  HARD-FAIL: >20% error at M=10M -- n=3 insufficient; escalate to n=4 or increase N.

### ANCHOR 3 (Tier 2, GPU, depends on Anchor 2 PASS)
Pointer: Full Config B at D=8, N=65536, Wikipedia sample (1M facts) retrieval accuracy + latency
Substrate-product reading: First end-to-end test of the full Phase 3 substrate configuration. Validates 12 GB footprint, per-substrate routing via VQ codebook, and multi-hop depth at scale.
Tier hint: Single GPU (RTX 3080+). V_c=100K cleanup codebook (edge-optimized). ~2 hours.
Why now: If Anchor 2 PASSes, this is the direct Phase 3 substrate validation.

---

## CONTEXT POINTERS

Research note: d:/AI/hd-instrument/notes/research_drill_production_substrate_llm_hybrid_architecture_at_scale_2x_2026-06-05.md
Controller architecture drill: d:/AI/hd-instrument/notes/research_drill_substrate_controller_hybrid_architecture_2x_2026-06-05.md
System 1+2 hybrid drill: d:/AI/hd-instrument/notes/research_drill_substrate_system1_hybrid_architecture_2x_2026-06-04.md
Algebraic capacity lit: arXiv:2604.25470 (hierarchical Hopfield robust recovery) + arXiv:2603.26217 (n=3 capacity scaling)
LLM partner lit: arXiv:2408.00118 (Gemma-2-2B distillation training + architecture)

---

## CONTRACT

exp_dev reads the research note and context pointers above before designing any anchor.
exp_dev uses tools/orchestrator/queue_add.sh for dispatch.
exp_dev does NOT encode experiment design (sweep grids, thresholds, numerical bounds) in this file -- that is exp_dev's job.
exp_dev pre-registers HARD-PASS / HARD-FAIL bands per [[feedback-envelope-expansion-fail-bands]] before shipping each anchor.
exp_dev verifies per-experiment --timeout per [[feedback-per-experiment-timeout-required]].
exp_dev checks for name collisions per [[feedback-ship-name-collision]] before dispatch.

---

## AUTONOMY DECLARATION

exp_dev has full autonomy over: anchor naming, sweep design, threshold formulas, queue selection (overnight_queue vs remote_cpu_queue), timeout formula, seed count, and sequencing of anchors within this hand-off. Orchestrator reviews verdicts; exp_dev designs the tests.
