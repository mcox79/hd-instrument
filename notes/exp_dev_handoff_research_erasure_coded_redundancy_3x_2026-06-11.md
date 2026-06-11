# exp_dev hand-off -- research: erasure-coded substrate redundancy

**Filed-by**: Research sub-agent, 2026-06-11
**Trigger**: d:/AI/hd-instrument/notes/research_drill_erasure_coded_redundancy_3x_2026-06-11.md
**Per [[feedback-no-experiment-design-in-prompts]]**: this file names candidates and pointers only; exp_dev designs the anchor cells, pre-reg bands, and smoke gates.

---

## Pause state block

Pause flag: check data/orchestrator_paused.flag before dispatching. If present, do not queue. If absent, dispatch in priority order below.

---

## Anchor candidates (rank-ordered)

### 1. FHRR-XOR-PARITY-SMOKE (Tier: CPU, ~5 min)

Anchor pointer: Scheme 2 in research note.
Substrate-product reading: validates that the FHRR phase-domain XOR parity can recover a single lost shard with similarity >= 0.999. This is the foundation of all multi-shard erasure schemes. If this fails (similarity < 0.99), all higher schemes are blocked.
Tier hint: CPU-only. Pure torch arithmetic, N=1024, M=10. No cloud needed.
Why now: cheapest possible validation of the core algebraic claim (phase-domain XOR = RAID-5 analog). Unblocks the RS code anchor.
Pre-reg note: HARD-PASS >= 0.999 sim for all 10 drop-1 configs; HARD-FAIL < 0.99 for any config.

### 2. FHRR-RS-10OF13-SMOKE (Tier: CPU, ~15 min)

Anchor pointer: Scheme 4 in research note; encode_rs / decode_rs sketch.
Substrate-product reading: validates 10-of-13 Reed-Solomon analog in FHRR phase domain at N=256, 512, 1024. This is the direct substrate implementation of the ZIP file redundancy the user described.
Tier hint: CPU-only. 30 lines of new code. torch.linalg.inv on 10x10 matrix.
Why now: this is the headline result. A HARD-PASS here means the substrate natively supports production erasure coding with no new dependencies.
Pre-reg note: test drop-{0,1,2}, drop-{4,7,11}, drop-{10,11,12} at each N. HARD-PASS >= 0.99 sim for all configs at N >= 512; HARD-FAIL < 0.95 at any N >= 512.

### 3. FHRR-CHECKSUM-HEALTH (Tier: CPU, ~20 min)

Anchor pointer: Scheme 7 in research note.
Substrate-product reading: validates bind-as-checksum for damage detection. Requires adding checksum field to Codebook. This is the detection layer without which damage is silent (the CORE-PERIPHERY failure mode).
Tier hint: CPU-only. 20 lines added to hdlab/memory.py.
Why now: damage detection is prerequisite to self-healing. Without it, all Schemes 2/4/6/8 are reactive-only (you don't know damage occurred until retrieval fails).
Pre-reg note: HARD-PASS precision=1.0 AND recall=1.0 for noise sigma in [0.1, 0.5]. HARD-FAIL: FP or FN rate > 5%.

### 4. FHRR-SNAPSHOT-RESTORE (Tier: CPU, ~30 min)

Anchor pointer: Scheme 6 in research note. hdlab/snapshots.py already exists.
Substrate-product reading: validates full round-trip snapshot + corrupt + restore. The snapshots.py module exists but has not been tested as a recovery mechanism.
Tier hint: CPU-only. Extend snapshots.py; no new module needed.
Why now: highest P_deflated (0.70) of all schemes; zero novel math; existing code. If snapshot restore fails (latency > 1s for 10K atoms), the self-heal loop cannot be relied on.
Pre-reg note: HARD-PASS similarity >= 0.999 for all 1000 atoms after restore. HARD-FAIL: any atom < 0.99 after restore OR restore latency > 1s.

### 5. FHRR-PHASE-DRIFT-AUDIT (Tier: CPU, ~10 min)

Anchor pointer: Part 5 (phase noise budget) in research note.
Substrate-product reading: measure actual float32 phase drift per bind operation empirically to calibrate the Scheme 7 health-check interval. The predicted interval (10^5 ops) is theoretical; the actual may differ.
Tier hint: CPU-only. Tight loop of bind operations on one atom; measure phase drift vs operation count.
Why now: calibrates all other health-check schemes. Without this measurement, the health-check interval is ungrounded.
Pre-reg note: HARD-PASS: drift < 0.06 rad after 10^5 bind ops at N=1024 (similarity > 0.998). HARD-FAIL: drift > 0.5 rad after 10^4 ops (would require health-check every 10K ops, which is expensive).

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_erasure_coded_redundancy_3x_2026-06-11.md
- Existing atoms module: d:/AI/hd-instrument/hdlab/atoms.py (similarity, make_atom_fhrr)
- Existing binding module: d:/AI/hd-instrument/hdlab/binding.py (bind, unbind)
- Existing memory module: d:/AI/hd-instrument/hdlab/memory.py (Codebook, add, lookup)
- Existing snapshots module: d:/AI/hd-instrument/hdlab/snapshots.py
- KB-shard prior PASS result: notes/substrate_capability_map.md (row for KB-shard, 0.965)
- Compositional cliff v3.0: memory/exp_dev_wave5_v3_cliff_crossed_2026-06-10.md
- CORE-PERIPHERY failure motivating context: MEMORY.md (substrate_primitives_yes_integration_no entry)

---

## Contract

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs anchor cells, pre-reg bands, smoke parameters, and queue routing. This file is a hand-off, not a spec.

## Autonomy declaration

exp_dev chooses: which anchors to ship first, exact smoke parameters, GPU vs CPU routing, whether to batch anchors 2+3 into one cell, and whether to implement Scheme 4 as a standalone verification script or as an hdlab extension. The above ordering is a priority recommendation, not a constraint.
