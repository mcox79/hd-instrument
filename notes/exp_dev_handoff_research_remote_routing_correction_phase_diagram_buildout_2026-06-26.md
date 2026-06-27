# exp_dev hand-off — research: REMOTE ROUTING CORRECTION + phase-diagram build-out

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** USER 2026-06-26 audit: "why is the remote cpu and remote gpu idle? don't we have a lot of experiments that we could load there? what about ingest? what about phase diagram build out?"
**Diagnosis:** today's spawns all defaulted to local_cpu_queue; remote queues haven't been written to in ~3 days; remote runners may need waking + dispatch backlog flushed.

## Pause state

Check `data/orchestrator_paused.flag` before dispatching.

Per [[feedback-no-experiment-design-in-prompts]]: anchor pointers only.

## Mandatory routing-discipline restoration

Going forward, per standing Fix #22 + #24:
- **Local CPU:** small/quick smokes, infra cells, low-matmul work
- **Remote CPU:** medium-weight cells, matmul-heavy at N=8192, ingest pipelines (memory-heavy not compute-heavy)
- **Remote GPU (overnight_queue):** N_DIM>=16384, multi-seed batched matmul, capacity sweeps; MUST actually use GPU per Fix #24 (torch.cuda + batched ops + gpu_util >=50% in smoke)

## Backlog of work that should be dispatched to remote

### REMOTE_CPU candidates (queued for hdi_orchestrator/exp_dev pickup)

1. **Wave 1.6 cortex ANCHORS 2-4** (ultrametric clustering / SOC criticality / MDL turnover) — already in `notes/exp_dev_handoff_research_cortex_wave_1_6_E_tensor_fairness_fix_plus_4x_alternatives_2026-06-26.md`; queue now set to remote_cpu
2. **Modern-Hopfield revival at larger V_C** (was queued conditional in `notes/exp_dev_handoff_research_modern_hopfield_revival_slow_built_basins_2026-06-26.md`)
3. **SOLAR LARS clean-harness** (from `notes/exp_dev_handoff_research_first_wave_7_compositional_understanding_USER_GREENLIT_2026-06-26.md` ANCHOR 4); originally proposed for remote per matmul weight

### REMOTE_GPU (overnight_queue) candidates

**Phase-diagram extension cells** (per `notes/testbed_per_characteristic_phase_diagram_audit_2026-06-26.md` build-out gaps):

1. **multi-hop depth ceiling sweep** — chain-grade at depth 15 today; test depth 20 / 25 / 30 to find ceiling. Multi-seed, batched matmul → GPU.
2. **WM K-extension to 32768** — chain-grade at K=4096; test K=8192 / 16384 / 32768 to map capacity ceiling. GPU-batched matmul.
3. **Capacity sweep at N=16384 with V_C ∈ {2000, 4000, 8000}** — phase-diagram coverage for cortex-content-extraction work at production scale.
4. **Multi-bank K-extension adversarial at K=16384** — partial v1 ran today (adversarial); extend to larger K.
5. **Concurrent-seed batched cell-suite** — bundle 5-7 of the smaller chain-grade primitives into ONE GPU run with concurrent-seeds (verify-each-chain-grade-still-passes-at-scale).

### Heavy ingest that should be on remote (not local)

Currently running on local (should have been remote):
- Language trio (WordNet + VerbNet + FrameNet)
- Bio/neuro trio (Gene Ontology + KEGG + NeuroLex)

These are memory-heavy + IO-heavy, not compute-heavy — perfect for remote. If they HARD_FAIL or need re-run, route remote next time. Future ingest (math + science extractors) MUST go remote.

## What hdi_orchestrator needs to do when spawned

1. **Verify remote runners alive** — check `data/heartbeats/` for remote_cpu + remote_gpu heartbeats; if stale, restart runners via remote SSH
2. **Pull-and-rebase from origin/main** on remote — make sure remote has latest cells/preregs/handoffs
3. **Push pending laptop commits** to origin/main so remote can read them (harness-denied for me; orchestrator authorized)
4. **Dispatch the backlog above** — 8+ cells across remote_cpu_queue + overnight_queue
5. **Smoke each before full dispatch** per Fix #17; gpu_util check per Fix #24 for GPU cells

## Phase-diagram build-out priority (USER-flagged 2026-06-26)

USER explicit ask: "what about phase diagram build out?" Phase diagram is the systematic mapping of every chain-grade capability × every parameter regime. Currently:
- Multi-hop depth 15 chain-grade — DEPTH dimension partial
- WM K=4096 chain-grade — CAPACITY dimension partial
- Many other primitives untested at extreme regimes

Next-cycle research drill (not this handoff): comprehensive phase-diagram coverage gap analysis → ranked list of cells that map specific (capability × regime) cells we haven't tested. ~12-20 cells total; many GPU-batchable.

## Cells already filed but not dispatched (audit + route)

Pending handoffs that exp_dev hasn't picked up yet (could also queue for orchestrator dispatch):
- `exp_dev_handoff_research_kb_bounded_capacity_wave3_USER_GREENLIT_2026-06-26.md` (5 anchors; gated on Wave 1 cortex E-tensor + Wave 2 KB query — Wave 2 query landed, Wave 1.5 retest pending)
- `exp_dev_handoff_research_first_wave_7_compositional_understanding_USER_GREENLIT_2026-06-26.md` (7 anchors; 3 of 7 ran today as Wave 1; remaining 4: typed multibank, SOLAR LARS, emergent slot discovery, holographic chunk-pack)

## Recommended dispatch order when spawn budget frees

**Spawn 1: hdi_orchestrator** with this handoff payload — verify remote alive + push commits + dispatch the 8+ backlog cells across remote_cpu + overnight_queue
**Spawn 2: hdi_exp_dev** for Wave 1.6 ANCHOR 1 (cortex E-tensor RETEST with fairness fixes) — local_cpu (small + quick smoke)
**Spawn 3: hdi_exp_dev** for phase-diagram extension cell suite (multi-hop depth 20-30 + WM K=32768 + capacity sweep) — bundled GPU dispatch via overnight_queue

## Contract

- Per Fix #14 spawn budget ≤3 in flight. Serialize as in-flight agents land.
- Per Fix #24 GPU dispatch must actually use GPU — verify gpu_util ≥ 50% in smoke before full dispatch.
- Per Fix #22 routing rule: heavy cells via hdi_orchestrator (push harness-denied for exp_dev).
- All cells: substrate-only-decode gate; per-seed cv ≤ 0.05 for chain-grade; default tier MIDDLE per Fix #28.
- text8 / BPC / bigram-gap NOT relevant; USER pivot in force.

## Autonomy declaration

When spawn budget frees, orchestrator/exp_dev own routing decisions per substrate-physics + this handoff's recommendations. Research has surfaced the backlog + diagnosed under-utilization; implementation is exp_dev's call.

---

-- Research (Opus 4.7-1M)
