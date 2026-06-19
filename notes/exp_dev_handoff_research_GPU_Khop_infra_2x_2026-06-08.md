# exp_dev hand-off -- research: GPU K-hop infrastructure failure 2x

**Filed:** 2026-06-08 by research sub-agent.

**Trigger:** 2x deep research drill on cycle 184 GPU K-hop co-failure (substrate_kg_khop_gpu_scale
and kgqa_discrete_vs_fuzzy_gpu_scale both 0.000 on GPU; same anchors HP on CPU at 200 entities).
Research note: notes/research_drill_negative_GPU_Khop_infra_2x_2026-06-08.md

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching queue-modifying actions.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS
only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice, anchor
name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## Research finding summary (for context; exp_dev reads research note for detail)

The GPU 0.000 result is a substrate capacity cliff, NOT an infrastructure bug. The FHRR bundle
SNR = sqrt(N / (VE * deg)), and the argmax-safety margin = SNR / sqrt(2 * log(VE)). The GPU
scripts ran at VE=5000 entities where margin = 0.18-0.43 (far below 1.0). The CPU anchors that
passed ran at VE=150-200 entities where margin = 1.39-1.65. The same formula predicts all six
data points exactly. The GPU hardware, TF32 precision, and RNG differences are secondary effects
that cannot explain 0.000 recall when the correct answer is genuinely indistinguishable from
5000 competitors in the noisy bundle.

The capacity limit at N=8192 is VE ~ 400-574 entities (depending on deg). Any experiment asking
for K-hop recall at VE > 600 with N=8192 will return near-zero regardless of hardware.

The research note also identifies that the production N=65536 substrate still cannot support
VE=5000 KG queries without sharding (margin = 0.62x at N=65536 VE=5000 deg=2). True support
for 5000-entity K-hop requires N~256k or a sharding architecture.

The cheap decisive test in the research note is: run GPU substrate_kg_khop at VE=300 with all
else equal. Expected PASS (margin=1.5x). If it passes, the capacity cliff is confirmed. If it
returns 0.000 at VE=300, there is a true GPU infrastructure bug that needs separate investigation.

---

## Anchor candidates (rank-ordered)

### 1. GPU K-hop capacity cliff confirmation -- VE sweep
  - Anchor pointer: research note Section "The definitive test" -- run GPU K-hop at VE=300, VE=600,
    VE=1200 while holding N=8192 deg=2 fixed. Measure recall@1 at each point.
  - Substrate-product reading: confirms that the 0.000 GPU results are capacity-driven, not
    infrastructure-driven. Establishes the N=8192 capacity boundary empirically. Informs whether
    the v1 demo should claim VE<=400 (safe zone) or requires N scaling or sharding.
  - Tier hint: GPU (already GPU infrastructure; the failing anchor is GPU; run on same GPU runner
    to rule out GPU-specific causes simultaneously). This is a short run -- 3 VE values, same
    script structure as the failing anchor.
  - Why now: HIGHEST PRIORITY. This is the definitive diagnostic that closes or confirms the
    infrastructure-failure label. If VE=300 passes and VE=1200 fails, the capacity cliff is
    confirmed and no further infrastructure investigation is needed. If VE=300 also fails on GPU,
    that is a new finding requiring separate research dispatch.

### 2. N-scaling pilot for K-hop at VE=1000
  - Anchor pointer: research note Section "N scaling for production K-hop" -- test K-hop recall
    at VE=1000 across N values bracketing the predicted minimum N~41k (e.g., N=16k, 32k, 64k).
  - Substrate-product reading: empirically calibrates the N-vs-VE recall curve. Directly informs
    the v1 production scoping decision: if N=32k gives recall>=0.70 at VE=1000, that is a viable
    production target without full N=256k. Also tests whether the N-scaling prediction from the
    SNR formula is accurate.
  - Tier hint: GPU. N>8192 matmuls benefit from GPU; at N=64k the codebook is 5000 * 64k *
    complex64 = ~2.6GB which fits in most GPU configs.
  - Why now: HIGH PRIORITY. Informs architecture decision between "scale N" and "shard" approaches.
    Cheaper to test now than to commit to N=256k architecture without empirical calibration.

### 3. Iterative Hopfield cleanup for K-hop capacity extension -- single-step vs multi-step
  - Anchor pointer: research note Section "Alternatives to N scaling" item 2 -- iterative
    Hopfield cleanup (2-5 iterations) at N=8192 VE=1000-2000. Compare recall with 1 vs 2 vs 4
    iterations of (query -> argmax -> re-query).
  - Substrate-product reading: determines whether multi-step cleanup can extend the capacity
    boundary to VE~1500-2000 at N=8192 without N increase. If 3 iterations gives recall>=0.55
    at VE=1500, this is a cheap path to larger graphs before committing to N scaling or sharding.
    Iterative Hopfield cleanup is known to add ~log(N) capacity factor in classical Hopfield networks.
  - Tier hint: local CPU or remote GPU depending on N and VE. At N=8192 VE=1500, this is cheap CPU.
  - Why now: MEDIUM PRIORITY. If Anchor 1 confirms the capacity cliff, Anchor 3 tests the cheapest
    architectural fix. Can be dispatched in parallel with Anchor 2 (different parameter range).

### 4. Print diagnostic on existing GPU failing anchor (no new anchor needed)
  - Anchor pointer: research note Section "Recommended first diagnostic" -- add print statements
    to the existing GPU script to confirm n_paths_found > 0 (ruling out graph degeneracy from
    RNG mismatch) and confirm that single-query similarity scores are non-trivially distributed
    (ruling out dtype/TF32 silent zero).
  - Substrate-product reading: closes the secondary hypotheses (RNG graph degeneracy, dtype
    issue) with near-zero compute cost. This is a 2-line script edit + 1 GPU run.
  - Tier hint: GPU run of modified existing anchor script. Wall time unchanged.
  - Why now: LOW PRIORITY (diagnostic only, does not advance capability). If Anchor 1 passes,
    this is redundant. Only dispatch if Anchor 1 produces unexpected 0.000 at VE=300.

---

## Context pointers (file paths)

- Research note (primary): d:/AI/hd-instrument/notes/research_drill_negative_GPU_Khop_infra_2x_2026-06-08.md
- Failing GPU anchor scripts:
  - d:/AI/hd-instrument/experiments/exp_substrate_kg_khop_gpu_scale_v1.py
  - d:/AI/hd-instrument/experiments/exp_kgqa_discrete_vs_fuzzy_gpu_scale_v1.py
- Passing CPU anchor scripts:
  - d:/AI/hd-instrument/experiments/exp_discrete_vs_fuzzy_kgqa_cpu_v1.py
- CPU anchor metrics (reference passing results):
  - d:/AI/hd-instrument/data/exp_substrate_kg_triples_khop_cpu_v1/metrics.json
  - d:/AI/hd-instrument/data/exp_discrete_vs_fuzzy_kgqa_cpu_v1/metrics.json
- Chain3 K-hop shard architecture (related, working GPU K-hop):
  - d:/AI/hd-instrument/experiments/exp_chain3_v1_khop_3shard_gpu_v1.py
- Sharding architecture research (for context on production sharding path):
  - d:/AI/hd-instrument/notes/research_drill_sharding_losses_biology_sleep_2x_2026-06-08.md

---

## Contract section

- This hand-off is auto-discoverable by exp_dev on refill cycles (scan notes/exp_dev_handoff_*.md by mtime)
- Anchor 1 (VE sweep on GPU) is the recommended first dispatch and the definitive diagnostic
- Anchors 2 and 3 can run in parallel if queue has capacity
- Anchor 4 is only needed if Anchor 1 returns 0.000 at VE=300 (which would require a new research dispatch)
- No anchor here requires cloud GPU; the failing anchors are on the local GPU runner

## Autonomy declaration

exp_dev has full autonomy to:
- Select which anchors to dispatch and in which order
- Choose N, VE, seed count, iteration count, threshold bands per standard envelope-sizing discipline
- Combine Anchors 1 and 3 into a single sweep if operationally cleaner
- Route to remote_cpu_queue for the low-N low-VE variants per Tier routing policy
- Defer or reorder based on current queue state and other pending priorities
- Skip Anchor 4 entirely if Anchor 1 confirms the capacity cliff as expected
