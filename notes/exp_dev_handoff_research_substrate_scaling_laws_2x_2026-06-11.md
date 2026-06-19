# exp_dev hand-off -- research: substrate scaling laws (2x)

**Filed:** 2026-06-11 by research sub-agent (Sonnet 4.6).

**Trigger:** Research drill on substrate scaling laws and distributed architecture
(notes/research_drill_substrate_scaling_laws_2x_2026-06-11.md).
10 concrete experiment anchors designed; cheap-first sequenced.

**Pause state:** check data/orchestrator_paused.flag before dispatching any anchor.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only.
exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C),
anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered, cheapest decisive first)

### Anchor 1: EXP-SCALE-2 -- FHRR similarity std vs large N
- Anchor pointer: research note Section "EXP-SCALE-2"; theory baseline in verification/test_capacity.py
- Substrate-product reading: extends already-passing test_fhrr_atom_similarity_std_matches_theory to
  N=[8192, 16384, 32768, 65536]; confirms 1/sqrt(2N) noise floor holds at production scale; enables
  all T1 capacity predictions to be trusted at larger N.
- Tier hint: local_cpu_queue (< 5 min; almost free; just extend existing test loop)
- Why now: foundational validity check; must pass before any larger N experiment is trusted

### Anchor 2: EXP-SCALE-5 -- Storage formula validation
- Anchor pointer: research note Section "EXP-SCALE-5"; formula: K * N * 8 bytes for complex64
- Substrate-product reading: confirms product sizing projections (65 MB per shard at K=2000, N=4096;
  52 GB at N=65536 K=100K); catches any hidden memory overhead before GPU sweep
- Tier hint: local_cpu_queue (< 2 min; measure tensor memory vs formula)
- Why now: must confirm before storage projections go into product narrative

### Anchor 3: EXP-SCALE-3 -- Codebook size V impact on recall
- Anchor pointer: research note Section "EXP-SCALE-3"; Plate formula: K_max ~ N / (2 log(2V/epsilon))
- Substrate-product reading: fixes the V-dependent capacity bound; production codebooks have V=100K+
  entries; this test determines whether V is actually limiting recall at current K values, and how much
  headroom exists before needing N-scaling
- Tier hint: local_cpu_queue (< 10 min; fixed N=4096, V sweep)
- Why now: required to calibrate T1 formula for production deployment guidance

### Anchor 4: EXP-SCALE-6 -- Streaming write throughput and recall stability
- Anchor pointer: research note Section "EXP-SCALE-6"; measures recall@1 at write rates [10,100,500,1000/s]
- Substrate-product reading: validates that substrate can be used as a write-heavy real-time memory
  without consolidation gating the write path; directly relevant to the compliance-sidecar product
  narrative where writes happen on the hot path of an existing pipeline
- Tier hint: local_cpu_queue (< 20 min; single-threaded streaming test)
- Why now: HARD-FAIL here (recall degrades at 100/s) would require architecture change BEFORE any
  production deployment; find this now not at demo time

### Anchor 5: EXP-SCALE-1-PARTIAL -- N-sweep K-cliff, N=[4096, 8192, 16384]
- Anchor pointer: research note Section "EXP-SCALE-1"; most decisive capacity scaling experiment
- Substrate-product reading: determines whether K_c/N is N-invariant (confirming FHRR percolation-class
  cliff) or N-dependent (requiring different product capacity projections at larger N); HARD-PASS means
  the existing 0.56 cliff guidance holds at all deployment scales; HARD-FAIL means capacity degrades
  with N and shard size must be bounded
- Tier hint: remote_cpu_queue for N=[8192, 16384]; local_cpu_queue for N=4096 (baseline only)
- Why now: single most important open question about substrate scalability; partial run at 3 N values
  costs < 1 hr CPU and resolves the question directionally

### Anchor 6: EXP-SCALE-4 -- Sharding recall: hash vs semantic routing
- Anchor pointer: research note Section "EXP-SCALE-4"; 10-shard test with controlled routing strategy
- Substrate-product reading: hash-based sharding FAILING is expected and confirms semantic routing is
  required; semantic routing PASSING at recall >= 0.90 with fan-out <= 3 enables the distributed
  substrate architecture spec (Tier 1 Router + Tier 2 Shard Nodes); this is the gate for the product
  roadmap item "1M-item substrate cluster"
- Tier hint: remote_cpu_queue (30 min; 10x shard construction + 1000 cross-shard queries)
- Why now: architecture gate for distributed product milestone

### Anchor 7: EXP-SCALE-7 -- Consolidation overhead measurement
- Anchor pointer: research note Section "EXP-SCALE-7"; 10K-item write followed by full consolidation pass
- Substrate-product reading: if consolidation is currently a no-op or very fast, the streaming
  architecture is valid as-is; if consolidation is expensive, an offline-amortization pass must be
  engineered before production; the handoff from research is that biological evidence and streaming
  RAG literature both say "amortize offline" -- this test confirms whether current substrate matches
  that pattern or needs architectural work
- Tier hint: remote_cpu_queue (15 min; single run with timing instrumentation)
- Why now: operational architecture dependency for EXP-SCALE-8 interpretation

### Anchor 8: EXP-SCALE-8 -- Multi-shard linear capacity (S=[1,2,4,8,16])
- Anchor pointer: research note Section "EXP-SCALE-8"; validates K_total = K_per_shard * S
- Substrate-product reading: if linear capacity is confirmed, the product roadmap can cite "100M items
  with 1000 shards at N=4096" as a concrete scaling target; if sublinear, routing overhead is eating
  into capacity and a different shard count optimization is needed
- Tier hint: remote_cpu_queue (45 min; multi-shard build with semantic routing)
- Why now: required for product roadmap capacity claim validation

### Anchor 9: EXP-SCALE-9 -- GPU throughput vs N
- Anchor pointer: research note Section "EXP-SCALE-9"; N=[4096, 8192, 16384, 32768] throughput
- Substrate-product reading: confirms whether GPU compute cost scales linearly (acceptable) or worse
  with N; required for infrastructure cost projections in the product plan; linear scaling means N=16384
  costs 4x the GPU budget of N=4096, which is acceptable for the compliance-sidecar price point
- Tier hint: remote_gpu_queue (1 hr GPU; torch.cuda timing)
- Why now: compute cost projections needed for pricing model

### Anchor 10: EXP-SCALE-10 + EXP-SCALE-1-FULL -- Cliff sharpness and full N-sweep
- Anchor pointer: research note Sections "EXP-SCALE-10" and "EXP-SCALE-1" (full 5-point sweep)
- Substrate-product reading: completes the N-scaling picture; cliff sharpness measurement enables
  precise capacity safety margin recommendations for production operators; this is the "no surprises"
  gate before any production deployment
- Tier hint: remote_gpu_queue (2-4 hr GPU; multi-N fine-K sweep)
- Why now: final validation after Anchors 1-9 have returned clean results

---

## Context pointers (file paths, not summaries)

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_scaling_laws_2x_2026-06-11.md
- Theory code (capacity formulas): d:/AI/hd-instrument/verification/theory.py
- Existing capacity test: d:/AI/hd-instrument/verification/test_capacity.py
- hdlab module root: d:/AI/hd-instrument/hdlab/
- Prior N-scaling result (N=8192 vs N=4096): cap_map row "M1 bundle-SNR mechanism confirmed"
- Prior cliff validation: cap_map rows "K-cliff at K/N~0.56" and "Resonator decomposition with ACF rescue"
- Capability map: d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract

exp_dev reads this file on emergency-refill cycles (notes/exp_dev_handoff_*.md sorted by mtime).
Dispatch order follows the Cheap-first sequencing in the research note.
All HARD-PASS / HARD-FAIL thresholds are pre-registered in the research note.
exp_dev does NOT re-derive thresholds -- it uses the ones in the research note verbatim
(or adjusts per Tier A/B/C envelope policy in agents/exp_dev.md Section 0).

## Autonomy declaration

exp_dev has full autonomy to:
- Choose the specific anchor names and queue routing
- Set K, N, seed count, and timing parameters within the scope of each EXP-SCALE-* description
- Stage the runs (smoke gate first, full run only on smoke pass)
- Merge anchors that can share infrastructure (e.g., EXP-SCALE-2 + EXP-SCALE-5 can run in one script)
- Skip anchors if a prior verdict already resolves the question

exp_dev must NOT:
- Change the HARD-PASS / HARD-FAIL thresholds
- Redesign the experiment question (the "what is being measured" is fixed)
- Dispatch GPU anchors while remote_cpu_queue has capacity (cost discipline)
