# exp_dev hand-off -- research: sparse-KEY composition partners (2x level-2 operational)

**Filed:** 2026-06-06 by research sub-agent.

**Trigger:** Level-2 operational drill on composition partners for sparse-KEY alpha coding.
Cite: notes/research_drill_sparse_key_composition_partners_2x_2026-06-06.md

**Pause state:** check data/orchestrator_paused.flag before dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only.
exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice, anchor name, ETA,
smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Headline finding (for exp_dev context)

Sparse-KEY composes with multi-head (orthogonal axis: error-correction via MMV joint sparsity)
and hierarchical VQ (orthogonal axis: coarse-grain pre-filtering). Hadamard failures are
construction-specific: independent per-row masks are an untested route that may compose.
Compound ceiling: 60-100x synthetic; 20-35x real-encoder (d_eff=91.6 ceiling).

---

## Anchor candidates (rank-ordered; exp_dev chooses from these per priorities and queue state)

### 1. Multi-head sparse-KEY composition test [FIRST PRIORITY]

- Anchor pointer: research note Section 2a + Section 6 (HP1 / HF1 thresholds).
- Substrate-product reading: if M=2 heads gives >1.3x capacity vs M=1 at same alpha, the
  multi-head axis is confirmed as independent. This unlocks the M=4 stack and the path to
  30-50x compound. MMV theory (Davies-Eldar 2012) gives the most precisely testable prediction
  of any composition candidate (sqrt(M) gain formula). This is the cheapest test.
- Tier hint: likely remote CPU or local (no new write rule needed; partition N into M_heads heads).
- Why now: cheapest composition test; highest P_deflated (0.40); MMV lit is the strongest
  cross-domain backing.

### 2. Hadamard + independent per-row masks [SECOND PRIORITY]

- Anchor pointer: research note Section 1b construction (A).
- Substrate-product reading: the orchestrator currently holds "Hadamard fails to compose."
  This verdict is construction-specific (shared mask tested; independent mask not tested).
  Testing independent per-row masks would either (a) recover Hadamard's orthogonality benefit
  and enable Hadamard+sparse stacking, OR (b) confirm true incompatibility.
  Either outcome advances the cap_map decisively.
- Tier hint: likely local or remote CPU (same write rule as current; only mask generation changes).
- Why now: cheap; directly tests the strongest unresolved claim in the current cap_map.

### 3. Block-sparse nesting (outer/inner alpha) [THIRD PRIORITY]

- Anchor pointer: research note Section 2c + Section 6 (HP2 / HF2 thresholds).
- Substrate-product reading: block-RIP lit (Eldar-Mishali 2009) predicts 1.3-2x improvement
  over flat sparse-KEY at same total density. If confirmed, block-sparsity becomes the CHEAPEST
  always-on improvement to sparse-KEY. Implementation: add outer group mask before sparse-KEY write.
- Tier hint: remote CPU (similar wall time to current sparse-KEY runs).
- Why now: third-cheapest; block-RIP is a well-established theoretical prediction.

### 4. PCA whitening pre-processing [SUPPORTING; queue with any of the above]

- Anchor pointer: research note Section 10 (substrate-product implication 6).
- Substrate-product reading: d_eff = 91.6 is the binding ceiling on real-encoder compound gains.
  PCA whitening redistributes encoder output mass over more dims, lifting d_eff.
  Cheap pre-processing step. Should be paired with any composition experiment on real encoder.
- Tier hint: local (CPU; pre-processing only; minimal wall time).
- Why now: needed before any real-encoder composition test to avoid hitting d_eff ceiling prematurely.

### 5. Hierarchical VQ coarse+fine sparse-KEY [FOURTH PRIORITY; higher cost]

- Anchor pointer: research note Section 2b + Section 6 (HP3 / HF3 thresholds).
- Substrate-product reading: sqrt(B) gain (8x for B=64) is the highest-potential composition.
  Combined with sparse-KEY: theoretical 160x; realistic 30-50x real-encoder.
  This is the "composable architecture" product differentiator if confirmed.
  Higher implementation cost: requires new coarse-cluster step.
- Tier hint: remote GPU (requires larger N to see VQ gain clearly).
- Why now: after multi-head is confirmed; this is the high-gain follow-up.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_sparse_key_composition_partners_2x_2026-06-06.md
- Drill W (key-collision rescue): d:/AI/hd-instrument/notes/ [search for Drill W or key-collision]
- D-RIP unified framework: d:/AI/hd-instrument/notes/research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md
- Sparse outer-product writes: d:/AI/hd-instrument/notes/research_drill_sparse_outer_product_writes_cross_cutting_2x_2026-06-05.md
- Cap map: d:/AI/hd-instrument/data/cap_map.md [rows relevant: sparse-KEY capacity row, Hadamard row]

---

## Contract

exp_dev designs and ships experiments from the anchor candidates above.
It does NOT interpret verdicts, update cap_map, or make strategic decisions.
It DOES: select anchors, choose queue tier, pre-register HP/MID/HF bands, run smoke gate,
ship via queue_add.sh, and perform post-ship REMOTE VERIFY.

## Autonomy declaration

exp_dev has full autonomy on: which anchors to queue, in what order, at what N and seed count,
with what timeout formula, and to which queue tier. The rank ordering above is a SUGGESTION;
exp_dev overrides based on current queue state, available wall time, and pause flag.
