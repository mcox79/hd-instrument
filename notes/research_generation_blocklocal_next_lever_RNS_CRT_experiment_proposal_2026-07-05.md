# exp_dev hand-off — research: mechanism + envelope-push for block-local generation decoder

**Filed by:** research (Sonnet, 4-way parallel lit-scan synthesis), 2026-07-05.

**Trigger:** `notes/research_mechanism_envelope_blocklocal_generation_decoder_2026-07-05.md` — mechanism +
envelope-push drill on `generation_decoder_gsbc_native_blocklocal_v1` (commit ec7aa9064).

**Pause state:** check `data/orchestrator_paused.flag` at pickup time; this hand-off does not itself
authorize dispatch under a pause.

**DISK-VERIFY FLAG (carry forward):** `data/exp_generation_decoder_gsbc_native_blocklocal_v1*` does not
exist on disk as of filing. The FULL 3-seed run is still pending on `remote_cpu_queue` per the prereg. Before
acting on either anchor below, re-read the landed `metrics.json` directly for the actual V8192/D26 cliff
number (prereg's own MEASURED@probe says 0.700, NOT the 0.86 figure that was floated informally) — do not
carry either number forward from memory.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names ANCHORS + POINTERS only. exp_dev
designs ALL of: exact grid points beyond the minimum named, trial counts, seed counts, threshold bands, queue
choice, timeout, smoke profile.

---

## Anchor candidates (rank-ordered)

### 1. [TOP, near-zero cost] Boundary grid-point extension to resolve the n0 location dispute

- **Anchor pointer:** extend `FULL_GRID` in `experiments/exp_generation_decoder_gsbc_native_blocklocal_v1.py`
  with `(8192, 8, "boundary")`, `(8192, 12, "boundary")`, `(8192, 16, "boundary")`, `(8192, 20, "boundary")`
  (block sizes n=1024, 683, 512, 410 respectively). No new mechanism; reuses the already-SCP'd
  `data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz`.
- **Substrate-product reading:** two independent literature frameworks (sparse-Hebbian associative-memory
  capacity law vs. channel-dispersion self-averaging) agree the V8192/D26 cliff should be a *sharp* transition
  but disagree by ~2x on where the 50% crossover (n0) sits — n0~915 (sparse-Hebbian fit, alpha_c~0.7) vs
  n0~400-500 (channel-dispersion estimate). Four new grid points bracket both estimates and settle it cheaply.
- **Tier hint:** local or CPU queue — measured 5-point grid ran in 8.9s; this is an analyzer-style extension
  of an existing cheap CPU cell, not a new build.
- **Why now:** resolves an open quantitative disagreement with a few lines of config change to code that
  already exists and already ran; the result also cross-validates (or falsifies) the specific capacity-law
  numbers in the research note's falsifiable-predictions section, which is otherwise going to sit unresolved
  until someone happens to look at a wider V8192 sweep.

### 2. [Highest-EV mechanism-class lever] Residue-Number-System / CRT modular sub-block prototype

- **Anchor pointer:** `notes/research_mechanism_envelope_blocklocal_generation_decoder_2026-07-05.md`
  Cross-thread synthesis #4, RANK 1 — Kymn, Kleyko, Frady, Sommer et al., "Computing with Residue Numbers in
  High-Dimensional Representation" (*Neural Computation*, 2024/2025), an existing published HDC realization
  of decomposing one large-vocabulary slot into several small pairwise-coprime-modulus sub-codes + CRT-style
  reconstruction. Grid-cell brain-grounding: Fiete, Burak & Brookings 2008 (*Neuron*); Sreenivasan & Fiete 2011
  (*Nat. Neurosci.*).
- **Substrate-product reading:** the V8192/D26 cliff is fundamentally a "single small block can't discriminate
  a large vocabulary via one argmax" problem. RNS/CRT sidesteps this by not requiring one block to discriminate
  all V items directly — it discriminates residues modulo several small numbers, each cheap, then reconstructs
  V combinatorially. This directly targets the observed ceiling without growing total width N, unlike simply
  adding more N or fewer D.
- **Tier hint:** likely local/CPU for a first small-scale prototype (mirrors the existing block-local cell's
  compute profile: numpy, no GPU, sub-minute wall for a bounded grid).
- **Why now:** ready-to-adapt published mechanism (not de-novo research), strongest brain-grounding of the 4
  candidates assessed, and directly resolves the exact axis (V-per-block ceiling) that cliffed in the just-
  landed cell — the natural next build once anchor #1's grid extension confirms where the current scheme's
  wall actually sits.

### Stretch candidate (lower priority, real risk noted)

3. **Hierarchical/nested chunking for D (sequence length) extension** — Miller/Cowan working-memory chunking
   gives real cognitive-science precedent, but no literature quantifies crosstalk compounding per unbind
   level; needs its own smoke test (does recovery degrade materially at 2+ levels of nesting) before trusting
   any capacity-multiplication formula. Lower EV than #2 until that risk is characterized.

---

## Context pointers (pointers, not summaries)

- `notes/research_mechanism_envelope_blocklocal_generation_decoder_2026-07-05.md` — full synthesis, capacity
  law derivation, all 4 lit-scan sub-agent findings, citations.
- `preregs/2026-07-05_exp_generation_decoder_gsbc_native_blocklocal_v1.md` — current cell's prereg, bands,
  MEASURED@probe numbers (ground truth pending FULL landing).
- `experiments/exp_generation_decoder_gsbc_native_blocklocal_v1.py` — the cell to extend (anchor #1) or use
  as the architectural template (anchor #2).
- `notes/decoder_design_stage_A_factor_B_order_C_cleanup_generation_readout_2026-07-05.md` — design memo,
  Stage A/B/C architecture, branch logic.
- `data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz` — existing native GSBC filler pool (untracked;
  already SCP'd to remote for the current cell; reuse, do not regenerate).

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE smoke, per the
  falsifiable-predictions section of the research note (anchor #1) or freshly derived (anchor #2).
- Smoke gate before FULL dispatch; self-test per [[feedback-formula-selftests]].
- Multi-seed FULL on smoke clearance; paired-trial discipline for any arm comparison.
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code.
- status_log entry with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: exact additional grid points beyond the 4 named minimums, trial/seed counts,
threshold bands, queue routing (Tier A/B/C), timeout, smoke vs FULL profile, and whether to build anchor #2
as a standalone cell or as a variant of the existing block-local cell. If exp_dev judges a different RNS/CRT
parameterization (module count, modulus sizes) is better-justified from first principles than anything named
here, that is exp_dev's call — this hand-off names the mechanism and its literature grounding, not the
implementation.
