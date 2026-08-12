# Forward-predictive second-encoder build plan (2026-07-30)

Scope: BUILD-READY plan for hdi_exp_dev. Answers whether a forward-predictive/JEPA-style
encoder produces reps where role-filler BINDING is more directly readable, so the
whitening+address-supervision read-conditioning scaffold (that the frozen MLM v2 encoder
needed, per `exp_selective_overwrite_recall_nl_wm_readcond_v1.py`) can be reduced or
dropped. USER-authorized expensive GPU work (idle capacity). Calibration per
[[feedback-lit-scan-calibration-penalty]]: CITED@ vs REASONED@ tagged; P deflated
0.15-0.25; novel-synthesis capped at P<=0.50.

KB-check (this cycle): `substrate_query.sh "JEPA latent predictive coding binding
role filler frozen encoder read conditioning"` -> top hit cosine=0.3447 (generic
lexical "conditioning"/WordNet matches only; no substantive prior result on this exact
question). Genuinely novel test, not a rediscovery.

---

## 0. What already exists (do not re-derive, reuse verbatim)

Two design docs and ONE fully-built (never run) experiment cell already cover most of
part 1 of this ask:

- `notes/forward_predictive_objective_from_wm_state_design_2026-07-29.md` — the
  WM-COUPLED forward-predictive design (predicts next-CLAUSE latent from maintained
  SLOT state). NOT what this plan builds — that is a situation-model/WM-gate lever,
  sequenced after the audit-C WM re-smoke. Kept separate per that note's own section 4.
- `notes/encoder_representation_lever_ranking_2026-07-29.md` — ranks encoder-level
  latent-PC (JEPA, no WM) as lever #1, distinct from the WM-coupled design. THIS is the
  lever this plan builds and tests.
- `experiments/exp_encoder_latent_pc_arc_v1.py` — **already fully authored** per lever
  #1's spec: 4 matched-budget arms (ARM_LPC, ARM_LPC_TC, ARM_MLM, ARM_RANDOM), EMA-target
  + stop-grad + VICReg variance/covariance collapse guards, rep-quality battery
  (graded-geometry Spearman, held-out linear probe, relational AUC, collapse
  diagnostics), pre-registered HARD_PASS/HARD_FAIL/FAIL_BY_COLLAPSE bands, cuda-safety
  audit, self-test. **It has never been run at FULL scale** — the only prior FULL-scale
  attempt at this class of objective (the causal-LM variant,
  `experiments/exp_scale_meaning_learn_arc_heldout_v5_forwardpc.py`) hit CUDA OOM, and a
  separate latent-PC data-prep attempt died silently at "collect pass" (~5h, no
  checkpoint). Section 2 below diagnoses both and gives the fix.
- `experiments/exp_selective_overwrite_recall_nl_wm_readcond_v1.py` (+ its base
  `exp_selective_overwrite_recall_nl_wm_roleseparated_v1.py`) — the exact
  read-conditioning binding-test mechanism this plan reuses for the sharp comparison
  (section 3). Confirmed by direct read: encoder is loaded via
  `FrozenV2Encoder(V2_CKPT)` (`V2_CKPT = data/exp_scale_meaning_learn_arc_heldout_v2/
  ckpt_seed_7.pt`), which needs a dict with `state_dict`, `model_cfg` (vocab, max_len,
  d_model, n_layers, n_heads, ffn_mult, pad_id), and `tokenizer_json` — architecturally
  identical to what `exp_encoder_latent_pc_arc_v1.py` already builds internally
  (same `TinyTransformer` class, imported from v2). **Gap: `exp_encoder_latent_pc_arc_v1.py`
  currently does NOT save a checkpoint for any arm** (`_build_encoder` returns
  `(model, diag)` in-memory only, nothing is `torch.save`d). This is the one piece of
  new plumbing section 3 needs.

**Conclusion: no new encoder architecture or objective needs to be designed.** The work
is (a) fix the two failure modes that have blocked this cell from ever completing a FULL
run, (b) add checkpoint-saving so the trained encoder can be reused downstream, (c) build
one new small comparison cell that swaps the frozen encoder in the existing
read-conditioning mechanism and runs the none/whiten-only/whiten+supervision arms against
both encoders.

---

## 1. The exact forward-predictive objective + architecture (as already built)

From direct read of `experiments/exp_encoder_latent_pc_arc_v1.py`:

- **Objective**: masked-SPAN latent prediction (I-JEPA/V-JEPA-style, CITED@Assran2023,
  CITED@Bardes2024, CITED@LeCun2022). Per training step: sample a batch of `max_len`
  token windows; mask a contiguous span (`lpc_mask_frac=0.20` of length) per row with
  `[MASK]` tokens to form the CONTEXT input; run the frozen-by-stopgrad TARGET encoder
  over the UNMASKED ids to get target latents at the masked positions; run the ONLINE
  encoder over the masked-context ids to get context latents at the same positions; a
  small predictor MLP (`LatentPredictor`, `d_model -> 2*d_model (GELU) -> d_model`) maps
  context latent -> predicted target latent; loss = smooth-L1(predicted, stopgrad(target))
  + VICReg variance hinge + VICReg covariance decorrelation on both predicted and target
  latents (float32, safe under AMP).
- **Architecture**: identical `TinyTransformer` (bidirectional, non-causal attention —
  see section 4 rationale below on why this is a deliberate, justified choice, not an
  oversight) to the current MLM v2 encoder — same d_model/n_layers/n_heads/ffn_mult/
  vocab/max_len/BPE-from-ARC. This is a FRESH-init encoder trained from scratch with the
  LPC objective (NOT an MLM-init fine-tune) — matched architecture, different objective,
  the clean one-variable comparison the ranking note calls for.
- **Collapse avoidance**: EMA target encoder (momentum 0.996, BYOL/I-JEPA range,
  CITED@) + stop-gradient through the target (SimSiam-style asymmetry, CITED@Chen&He2021)
  + VICReg variance floor (gamma=1.0 hinge) + VICReg covariance off-diagonal
  decorrelation (CITED@Bardes2022). This is the STRONGER guard than the WM-coupled
  design's SimSiam-only recommendation, because `encoder_representation_lever_ranking`
  section 1 flagged SimSiam-alone as sensitivity-risky at our small-data/model-size
  ratio (SCAN 1 finding) — the encoder-level cell already built in the stronger EMA+VICReg
  combination rather than the cheaper stop-grad-only guard. Correct choice; keep as-is.
- **MLM-vs-causal**: bidirectional (MLM-style attention), NOT causal. See section 4.
- **Granularity**: token-level windows (`max_len` tokens per row, contiguous masked
  span within it) — sub-clause granularity, distinct from the WM-coupled design's
  clause-level prediction. This is intentional per the ranking note's stated
  distinction (pretraining-stage lever vs maintenance-stage lever).
- **Fresh vs fine-tune**: FRESH per-arm init (`ARM_LPC` and `ARM_MLM` are each trained
  from a different random init of the SAME architecture, matched steps/tokens/batch) —
  this is the correct discipline for isolating the OBJECTIVE as the one variable; an
  MLM-init-then-LPC-finetune variant is explicitly NOT part of this plan (would confound
  "objective changes the reps" with "residual MLM structure persists under fine-tune").

**No changes needed to this part of the design.** The predictor head, collapse guards,
masking scheme, and matched-budget arm structure are already correctly specified and
implemented per the ranking note's lever #1. What is missing is (a) making it actually
finish a FULL run (section 2), (b) persisting the trained weights (section 2.3), and
(c) the downstream binding comparison (section 3).

---

## 2. Root-cause fixes for the two prior failures (MANDATORY, must ship before FULL dispatch)

### 2a. The data-prep silent hang at "collect pass" — diagnosed

Direct read of `experiments/exp_scale_meaning_learn_arc_heldout_v2.py` (imported
verbatim by the LPC cell for `prepare_data`/`load_concept_universe`/`TinyTransformer`/
`mlm_train`):

- `prepare_data()` calls `count_pass()` THEN `collect_pass()` **sequentially**, each of
  which opens `ARC_CORPUS` (`data/corpora/arc/ARC-V1-Feb2018-2/ARC_Corpus.txt`,
  MEASURED@ 1.4GB, 14,621,856 lines) and iterates it **line-by-line in pure Python**
  (regex `_WORD_RE.findall`, a quality check, a blake2b line-hash, dict/set updates) up
  to `cfg["max_lines"]` (FULL_CFG = 10,000,000 — i.e. two full ~10M-line single-threaded
  Python passes over the corpus, back to back).
- **Root cause #1 (why it looked "silent"): zero progress logging inside either loop.**
  `_log(...)` is called exactly once before `count_pass` starts, once after it finishes,
  once before `collect_pass` starts, once after it finishes — nothing in between. A
  multi-hour pure-Python regex/hash loop over 10M lines with NO interim signal is
  indistinguishable, from the outside (heartbeat file, console tail), from a genuine
  hang. This matches "died silently ~5h at collect pass" exactly: MEASURED@ this cycle,
  the file is large enough (1.4GB / 10M lines, two full passes) that multi-hour
  wall-clock for a bare Python loop is entirely plausible on its own, with or without an
  actual crash — the operational failure was invisibility, not necessarily death.
- **Root cause #2 (real, compounding): the corpus is scanned TWICE.** `count_pass` and
  `collect_pass` both do their own independent line-by-line read of the same file. This
  is wasted wall-clock that can be halved.
- **Fix A (mandatory, ships with the cell):** add heartbeat/progress logging inside
  BOTH `count_pass` and `collect_pass` — every `N=500_000` lines, `_log` (and write to
  `_heartbeat.jsonl` via the existing heartbeat helper, already present in this file) the
  running `n_read`, elapsed seconds, lines/sec rate, and ETA to `cfg["max_lines"]`. This
  alone converts "silent — assume hung" into "visibly slow but alive," the correct
  diagnosis-preserving fix (do not conflate "looked dead" with "was dead").
- **Fix B (mandatory, ships with the cell): merge `count_pass` + `collect_pass` into ONE
  single-pass read.** Both need: dedup-hash, quality filter, word-set, and (for
  collect_pass) held-vs-train routing + postings + BPE sample; `count_pass`'s per-concept
  mention COUNTS can be accumulated in the same loop that `collect_pass` already builds
  postings in (postings length IS effectively the count, capped at `cap_mentions` — the
  cell already needs a separate exact count for `build_split`'s median-mention
  eligibility computation, so keep an uncapped `np.zeros(K)` counter incremented
  alongside the capped-postings accumulation, in the SAME loop). This is a real ~2x
  wall-clock reduction on the single most expensive fixed cost of the whole cell, not
  just a smoke-gate nicety.
- **Fix C (mandatory, the "fails loud" smoke gate):** a fast, TIME-BOUND data-prep smoke
  that exercises the REAL corpus (not a synthetic stand-in) at a bounded line count and
  extrapolates: run the merged single-pass loop with `max_lines` capped at 2,000,000
  (roughly a 5-minute-scale slice, MEASURE the actual wall-clock and lines/sec), then
  assert `measured_lines_per_sec * (FULL_CFG["max_lines"] or corpus_total_lines) <=
  DATA_PREP_TIME_CEILING_S` (recommend ceiling = 4 hours = 14400s, i.e. roughly 2x the
  post-merge-fix expected cost, generous but bounded) BEFORE FULL is queued. If the
  extrapolated ETA exceeds the ceiling, the smoke FAILS LOUD with the measured rate and
  projected ETA in the verdict message — this is the exact gate that would have caught
  either an unexpectedly-slow environment (network filesystem, cold cache, single vCPU
  quota on the remote box) or a correctness regression that turns an O(1) per-line op
  into something quadratic (e.g. `seen` set growth pathology), BEFORE 5 hours are spent
  finding out live. Wire this into the cell's own `--smoke` path as an additional printed
  gate (`data_prep_headroom: DATA_PREP_OK | DATA_PREP_TOO_SLOW`), not a separate script.
- **Fix D (defensive, cheap): checkpoint `prepare_data`'s output bundle to disk once
  computed** (pickle or torch.save the `bundle` dict — postings/counts/split/tok/spec/
  stream/adj are all plain numpy/python/tokenizers objects, no torch state) keyed by a
  hash of `(cfg subset that affects data, corpus mtime)`, and have `main()` check for
  and reuse that cache before calling `prepare_data()` again. This makes a crash AFTER
  successful data-prep (e.g. during arm training) not repeat the ~2-3h data-prep cost on
  resume — directly serves the CLAUDE.md checkpoint/resume mandate at the level ABOVE
  the per-arm loop (section 2c handles the per-arm level).

### 2b. The CUDA OOM on full-position logits — confirmed structurally absent, not just smaller

Direct comparison of the two files:
- `exp_scale_meaning_learn_arc_heldout_v5_forwardpc.py` (the FAILED prior attempt): its
  `causal_lm_train` computes `logits = model.lm_logits(ids)` which is `[B, L, vocab]`
  (`vocab=16000` at FULL) — a full per-position, per-vocab-entry tensor, then
  `F.cross_entropy` over `[B*L, vocab]` — this is the OOM class (activations +
  cross-entropy backward over a `[B, L, 16000]` tensor at `B=128, L=128` = 262M logit
  entries per batch, times AMP/backward buffers).
- `exp_encoder_latent_pc_arc_v1.py` (this plan's cell): the ONLY head is
  `LatentPredictor: d_model -> d_model` (a `[T, d]` tensor, `d_model<=512`, `T` = number
  of masked positions in the batch, at most `B*L*mask_frac ~= 128*128*0.20 ~= 3277` rows
  of width 512). **No `[B, L, vocab]` tensor is ever materialized anywhere in this file**
  — confirmed by reading every tensor-producing line in `lpc_train`. This is not "a
  smaller version of the same risk," it is a categorically different tensor shape
  (bounded by `d_model`, independent of `vocab`) — the OOM class the causal-LM attempt
  hit cannot recur here by construction.
- **Fix (verification-only, ships as a smoke assertion, not new code):** add one
  explicit runtime assertion in `--self-test`/`--smoke` (and ideally `--full`) mode: after
  each `lpc_train` step, assert `zp.shape[-1] == cfg["d_model"]` and that no tensor with
  last-dim `== spec["size"]` (vocab) exists among the loss-path tensors (a simple shape
  check on `zp`/`zt`/`zc` is sufficient given there is only one head). This is a cheap,
  permanent guard against a future edit accidentally reintroducing a vocab-sized head
  into this path — not a fix for a live bug, a tripwire against regression.

### 2c. Per-arm checkpoint/resume (CLAUDE.md mandate, currently violated)

`exp_encoder_latent_pc_arc_v1.py`'s `run_one_seed` trains all 4 arms
(`ARM_LPC`, `ARM_LPC_TC`, `ARM_MLM`, `ARM_RANDOM`) in a single in-process loop and only
calls `write_partial(out_dir, seed, res)` ONCE per seed, after all 4 arms finish. Each
trained arm at FULL scale costs ~2.8-3.2 GPU-hours (section 4 anchor); losing all
in-flight arms on a crash mid-seed is exactly the failure class CLAUDE.md's "Multi-unit
cell checkpoint/resume" section exists to prevent, and directly caused this cell to
never complete a FULL run to date (combined with 2a's invisibility, a crash mid-arm-3
could not even be diagnosed as "which arm died").

**Fix (mandatory):** treat `(seed, arm)` as the checkpoint unit key, per
`tools/exp_checkpoint.py`'s `unit_key`/`completed_units`/`record_unit`/`load_units`
contract:
1. Before training an arm, check `completed_units(out_dir)` for
   `"seed%d_arm%s" % (seed, arm)`; if present, `load_units` the prior arm result
   (including its saved checkpoint path, section 2.3 below) instead of retraining.
2. After each arm's `_build_encoder` + rep-quality battery completes, immediately
   `record_unit(out_dir, key, arm_result)` — so a crash during arm 4 does not lose arms
   1-3's ~9 GPU-hours of already-complete work.
3. `run_one_seed`'s final return value is assembled from `load_units`, matching the
   existing final-`write_metrics` atomic-replace pattern already used by this cell (no
   change needed to the outer aggregation, only to the inner per-arm loop).

### 2d. NEW: save a reusable checkpoint per trained arm (needed for section 3)

Add, at the end of each trained arm's build step in `_build_encoder` (mirroring
`exp_scale_meaning_learn_arc_heldout_v5_forwardpc.py`'s own `ckpt` dict construction,
lines ~328-345, and V2's own checkpoint format read by `FrozenV2Encoder`): for
`ARM_LPC` and `ARM_MLM` (the two arms section 3 needs; `ARM_LPC_TC`/`ARM_RANDOM`
optional, cheap to include for completeness) save
`torch.save(dict(state_dict=..., spec=spec, model_cfg=dict(vocab=..., max_len=...,
d_model=..., n_layers=..., n_heads=..., ffn_mult=..., pad_id=...), tokenizer_json=...,
seed=seed, run_mode=cfg["run_mode"], anchor=ANCHOR_NAME, arm=arm), os.path.join(out_dir,
"ckpt_seed_%d_%s.pt" % (seed, arm)))`. This is bit-for-bit the same dict shape
`FrozenV2Encoder` already knows how to load — zero new loader code needed downstream,
only a path change (section 3).

---

## 3. The sharp comparison experiment (the actual scientific payoff)

### 3.1 What to build (one new small cell, CPU-only, cheap)

New file: `experiments/exp_binding_readcond_encoder_compare_v1.py`. Thin wrapper/fork of
`exp_selective_overwrite_recall_nl_wm_readcond_v1.py` with exactly ONE change:
parameterize the frozen encoder checkpoint path instead of hardcoding `base.V2_CKPT`.
Concretely:
- Add a module-level `ENCODER_ARM` selector (`"MLM_V2"` = current behavior, reusing
  `base.V2_CKPT`; `"LPC"` = the new
  `data/exp_encoder_latent_pc_arc_v1/ckpt_seed_<seed>_ARM_LPC.pt` from section 2.4).
- `FrozenV2Encoder.__init__` already only depends on `state_dict`/`model_cfg`/
  `tokenizer_json` matching `TinyTransformer`'s constructor signature — the LPC arm's
  saved checkpoint (section 2.4) satisfies this identically. NO change needed to
  `FrozenV2Encoder` itself; only which path is passed to its constructor.
- Everything else (the role-separated WM mechanism, the NL Selective-Overwrite-Recall
  task, the conditioning arms none/zscore/pca_whiten, the aux-CE and warm-start levers,
  the RANDOM_INIT_WM control, the bands `RI_NEAR_CHANCE`/`MECH_MARGIN`/`WM_PROVEN_MIN`/
  `WM_PARTIAL_MIN`) is reused VERBATIM by importing
  `exp_selective_overwrite_recall_nl_wm_readcond_v1` and re-running its config matrix
  once per encoder choice — this is intentionally a thin harness, not a rewrite.

### 3.2 Pre-registered arms (the actual test matrix)

Cross the ENCODER axis with a REDUCED conditioning-arm set (the full readcond cell's
config matrix already covers none/zscore/pca_whiten/+aux/+warmstart for the MLM
encoder — reuse those numbers as the MLM_V2 reference row rather than re-running them):

| Encoder | conditioning=none | conditioning=whiten-only (pca_whiten) | conditioning=whiten+aux+warmstart (combined) |
|---|---|---|---|
| MLM_V2 (existing, reference) | STUCK_FLAT (chance, ~0.05) — MEASURED@ b3e5c0b7f | fails alone (untrained key separates only 4/6) — MEASURED@ readcond diagnostic | proven / partial — MEASURED@ readcond cell's own combined-arm result (read off its metrics.json at run time; do not re-derive here) |
| LPC (new) | run | run | run |

Each cell of the LPC row = one `(seed, conditioning-config)` run of the SAME
role-separated WM mechanism, seeds 7 and 13, identical bands (`RI_NEAR_CHANCE=0.10`,
`WM_PROVEN_MIN=0.50`, `WM_PARTIAL_MIN=0.15`) — no band changes, so the comparison is
apples-to-apples by construction.

### 3.3 HARD-WIN definition (pre-registered)

- **HARD-WIN (the sharp test this plan exists to run):** LPC-encoder + `conditioning=none`
  OR LPC-encoder + `conditioning=pca_whiten` (whiten-only, NO aux CE, NO warm-start)
  reaches `eval_acc >= WM_PROVEN_MIN (0.50)` on both seeds, with `RANDOM_INIT_WM` control
  staying `< RI_NEAR_CHANCE (0.10)` on the same conditioning (control-floor intact) —
  i.e. binding is learnable WITHOUT the supervision/warm-start scaffold the MLM encoder
  needed. This is a strictly HIGHER bar than merely "LPC + combined-scaffold also works"
  (that would only be a replication, section 3.4) — the win is specifically that LESS
  scaffolding suffices.
- **PARTIAL-WIN:** LPC + none/whiten-only clears `WM_PARTIAL_MIN (0.15)` and is
  significantly (`Z_THRESH=2.0`) above its `RANDOM_INIT_WM` control, but below
  `WM_PROVEN_MIN` — real-but-partial reduction in required scaffolding.
- **HARD-FAIL (encoder-objective hypothesis refuted for binding-readability):** LPC +
  none AND LPC + whiten-only BOTH stay within the MLM encoder's own no-scaffold/whiten-
  only band (i.e. `<= MLM's own none/whiten-only eval_acc + 0.05`, both near chance) —
  the forward-predictive objective did not make binding any more directly readable than
  MLM at the representation level; whatever gain LPC has (if any, per section
  encoder-level battery in `exp_encoder_latent_pc_arc_v1.py` itself) does not transfer to
  this readout task.
- **Replication arm (mandatory, separate question):** LPC + whiten+aux+warmstart
  (the full combined scaffold) — does read-conditioning still work AT ALL on a
  DIFFERENT encoder, i.e. is the read-conditioning fix itself encoder-general/robust, or
  was it somehow tuned to the specific MLM v2 checkpoint's geometry? This is reported
  regardless of the HARD-WIN/HARD-FAIL outcome above — a negative result here (combined
  scaffold ALSO fails on LPC) would be a distinct and important finding (the
  read-conditioning MECHANISM itself may be checkpoint-specific, not just under-scaffolded
  for MLM).

### 3.4 Cardinality / arms-must-differ

`(seed x conditioning-arm x encoder)` = 2 x 3 x 2 = 12 LEARNED_WM runs + matching
RANDOM_INIT_WM controls per conditioning (reuse the readcond cell's existing
`N_RANDOM_INIT=3` control-replication discipline) + 2 WARMSTART_FROZEN honesty-diagnostic
runs (combined arm only, both encoders). All CPU, cheap (readcond cell is already
CPU-only per its own header). `_arms_must_differ` hash-check (already a pattern in both
source cells) applies across the two encoders' held-out eval-logit matrices at minimum.

---

## 4. Cost / time estimate + checkpoint requirements

**GPU-hour anchor (MEASURED@, this cycle, from `data/exp_scale_meaning_learn_arc_heldout_v2/
metrics.json`):** V2's own FULL MLM training, same architecture
(d_model=512/n_layers=6/vocab=16000/mlm_steps=40000/train_token_budget~121M), measured
`elapsed_s` = 10206s and 10205s for seeds 7 and 13 respectively (~2.83 GPU-hours per
trained arm-seed on the reference remote box). This elapsed figure is per-seed
train+encode+eval, NOT including the shared one-time data-prep (measured separately,
section 2a — historically unmeasured because it never completed; post-fix-B (single-pass
merge) estimate is roughly half of whatever the two-pass version would have taken, with
Fix-C's own smoke measuring the real per-line rate before FULL commits to a number).

**FULL cost estimate for `exp_encoder_latent_pc_arc_v1.py --full`:**
- Data-prep (shared once, post Fix A/B/C/D): budget 2-4 GPU-idle-CPU-hours (bounded by
  Fix C's own 4h ceiling; if the smoke's extrapolation exceeds this, the cell should
  refuse to dispatch FULL and report the measured rate instead of guessing).
- Trained arms: reuse V2's own checkpoint for `ARM_MLM` (do not retrain — identical
  architecture/budget already exists at `data/exp_scale_meaning_learn_arc_heldout_v2/
  ckpt_seed_{7,13}.pt`; this is the SAME reuse pattern `exp_scale_meaning_learn_arc_
  heldout_v5_forwardpc.py` already uses via `_load_mlm_baseline_encoder` — copy that
  function's pattern into this cell to cut ~2/4 of the trained-arm cost). Only
  `ARM_LPC` and `ARM_LPC_TC` need fresh training: 2 arms x 2 seeds x ~2.83h (LPC's
  predictor+VICReg overhead is small relative to the shared TinyTransformer forward/
  backward cost; budget +15% -> ~3.25h/run) = **~13 GPU-hours** for the 4 trained runs.
  `ARM_RANDOM` is untrained (seconds).
- **Total estimated wall-clock for the encoder-training half: ~15-17 GPU-hours**
  (2-4h data-prep + ~13h training), assuming the remote box is not shared/contended.
  Per section 2c, this is now resumable at the (seed, arm) granularity, so a preemption
  loses at most one in-flight arm (~3h), not the whole run.
- **Downstream binding comparison (section 3): CPU-only, cheap.** The base
  role-separated WM cell and its readcond variant are both explicitly CPU/local
  (no CUDA in that `.venv`); budget on the order of the existing readcond cell's own
  FULL run time (not separately measured in this cycle, but the cell's own doc states
  `STEPS_WM=800, BATCH=256` per config — this is a small-model CPU training loop,
  expect low tens of minutes per `(seed, conditioning, encoder)` cell, i.e. **under 4
  CPU-hours total** for all 12+ runs in section 3.4, dominated by iteration/re-run
  convenience rather than raw compute).

**Checkpoint/resume requirements (mandatory, per CLAUDE.md):**
- `exp_encoder_latent_pc_arc_v1.py`: (seed, arm) unit checkpointing per section 2c,
  PLUS the data-prep bundle cache per section 2a Fix D. Both are new code, both are
  small (the `tools/exp_checkpoint.py` helper functions already exist and are already
  imported by this file — `write_partial`/`aggregate_partials` — the work is moving the
  unit boundary from "whole seed" to "(seed, arm)", not building new infra).
- `exp_binding_readcond_encoder_compare_v1.py`: CPU/cheap enough that per-cell-run
  checkpointing is optional (each individual `(seed, conditioning, encoder)` run is
  short); still use `tools/exp_checkpoint.py` at the `(encoder, seed, conditioning)`
  unit level for consistency with the mandate and because the total matrix (12+ runs)
  is >1 unit.

---

## 5. Honest brain-fidelity + risk read

**Is forward-prediction genuinely expected to reduce binding entanglement, or is that
hope?** Genuinely expected, with real (not overwhelming) literature support found THIS
cycle beyond what the two prior notes already cited:

- CITED@ "Predictive learning enables compositional representations" (bioRxiv preprint,
  2025, generic-term-verified this cycle): RNNs trained SOLELY to predict future sensory
  input develop MODULAR, DISENTANGLED representations that support systematic
  compositional generalization to novel combinations — this is close to a direct
  precedent for "a forward-predictive objective, by itself, yields more
  factorized/separable representations than a non-predictive one," which is exactly the
  mechanism this plan's HARD-WIN needs (binding-readable = the slot/filler factors are
  separable enough for an untrained or lightly-trained address key to find them, per the
  read-conditioning diagnostic's own finding that the current MLM encoder's slot signal
  exists but is swamped by a shared component in a low-variance subspace).
- CITED@ "On the Binding Problem in Artificial Neural Networks" (Greff, van Steenkiste,
  Schmidhuber survey, arXiv 2012.05208) — establishes that binding-readability is a
  representation-geometry property (variable-binding requires representations that
  preserve per-object/per-role modularity), independent of any specific architecture;
  supports treating "is binding more directly readable" as a well-posed, literature-
  grounded question rather than a substrate-specific hope.
- CITED@ (title-verified generic search this cycle; treat as REASONED@ for the
  transfer, per calibration discipline) "Compositional Generalization Requires Linear,
  Orthogonal Representations in Vision Embedding Models" — the linear/orthogonal framing
  matches this plan's own read-conditioning finding (whitening = decorrelation = pushing
  toward orthogonality) and suggests that IF the LPC objective's training-time VICReg
  covariance term (already decorrelating, section 1) transfers its effect to the
  DOWNSTREAM slot/filler subspace (not just the aggregate rep it was trained on), whitening
  becomes LESS NECESSARY post-hoc because the encoder did some of that work during
  training — this is the precise mechanism the HARD-WIN bets on.
- REASONED@ (this cycle's own synthesis, not independently verified, P capped per
  novel-synthesis rule): the connection from "VICReg decorrelates the TRAINING objective's
  target/predicted latents" to "the DOWNSTREAM role/filler slot subspace (which the LPC
  objective never explicitly sees — it masks spans, not slot/filler labels) is ALSO
  decorrelated" is a TRANSFER, not a proven equivalence. This is the single weakest link
  in the whole hypothesis chain and the primary reason P is capped below 0.50.

**Failure mode the experiment would show, and how:** forward-prediction ALSO entangles
(or entangles differently but not less) — the masked-span prediction objective operates
on WHATEVER factors are locally predictive of a token-window's content, which need not
align with the slot/filler semantic factors the NL Selective-Overwrite-Recall task probes.
If so: LPC + none/whiten-only lands in the SAME near-chance band the MLM encoder did
(HARD-FAIL band, section 3.3), and — the informative part — the replication arm
(LPC + full combined scaffold) still tells us whether the read-conditioning FIX itself
generalizes across encoders even when the raw-readability hypothesis is refuted. Either
way this is a real, decisive, cheap-to-run test: the CPU-only downstream half
(section 4) means a HARD-FAIL costs almost nothing beyond the already-necessary
encoder-training GPU spend, which itself also answers the SEPARATE, already-pre-registered
`exp_encoder_latent_pc_arc_v1.py` rep-quality-battery question (graded-geometry Spearman
etc.) regardless of the binding-readability outcome — no wasted GPU spend even on a
binding-side HARD-FAIL.

**P_deflated on the HARD-WIN: 0.30.** (Base REASONED@ transfer confidence ~0.40-0.45
per the compositional-representations precedent, deflated 0.15 per lit-scan-calibration
penalty for the uncharted-regime transfer from "RNN predicts sensory sequences" /
"vision embeddings" to "our from-scratch small BPE-token TinyTransformer / NL
slot-filler task," landing at 0.30 — below the 0.50 novel-synthesis cap, consistent with
this being a real-but-unproven mechanism bet, not a coin flip and not a confident
prediction.) PARTIAL-WIN is assessed as substantially more likely than HARD-WIN
(REASONED@, P~0.45 deflated) given the general pattern in this program that objective/
architecture levers tend to land in the "real but below the pre-registered HARD band"
MIDDLE_BAND (per `encoder_representation_lever_ranking`'s own "soft floor" finding,
section 2 of that note) rather than cleanly clearing a HARD bar on the first attempt.

---

## Go/no-go recommendation (for Director)

**GO**, with the two mandatory root-cause fixes (2a/2b/2c) shipped FIRST and gated by
their own smoke (Fix C's data-prep-headroom gate) before any FULL GPU dispatch — no new
architecture design is needed (the cell is already correctly speced per lever #1 of the
ranking note), the two prior failures are now diagnosed to concrete, cheap code fixes
(progress logging + single-pass merge + per-arm checkpointing), and the downstream sharp
comparison (section 3) is a thin, cheap, CPU-only harness reusing the exact proven
read-conditioning mechanism verbatim. **Single biggest risk:** the REASONED@ transfer
in section 5 — that VICReg-driven decorrelation of the LPC objective's OWN training
target transfers to make the DOWNSTREAM, never-explicitly-trained-for slot/filler
subspace also more separable. This is plausible and literature-adjacent (compositional-
representations-from-prediction precedent) but not proven, which is why P_deflated is
capped at 0.30 on the HARD-WIN specifically (not on whether the LPC encoder is "better"
in general — the rep-quality battery already built into `exp_encoder_latent_pc_arc_v1.py`
answers that separately, per its own pre-registered bands, independent of this binding
question).

---

## Citations (this cycle)

- CITED@ carried from `notes/forward_predictive_objective_from_wm_state_design_2026-07-29.md`
  and `notes/encoder_representation_lever_ranking_2026-07-29.md`: Rao & Ballard (1999),
  Friston (2005), LeCun (2022), Assran et al. (2023, I-JEPA/V-JEPA), Bardes et al.
  (2024, V-JEPA2), Chen & He (2021, SimSiam), Bardes et al. (2022, VICReg), BabyLM
  Challenge literature, Kaplan/Hoffmann scaling laws (REASONED@ transfer).
- NEW this cycle (generic-term WebSearch, query-privacy compliant — no substrate-novel
  terms used): "Predictive learning enables compositional representations" (bioRxiv
  preprint, 2025) — CITED@, direct precedent for predictive objectives yielding
  modular/disentangled/compositionally-generalizing representations.
- NEW this cycle: Greff, van Steenkiste & Schmidhuber, "On the Binding Problem in
  Artificial Neural Networks" (arXiv 2012.05208) — CITED@, establishes binding-
  readability as a representation-geometry property.
- NEW this cycle: "Compositional Generalization Requires Linear, Orthogonal
  Representations in Vision Embedding Models" — CITED@ for existence/title, REASONED@
  for the transfer of its linear/orthogonal framing to this plan's whitening mechanism.

Verified citation count this cycle: 3 new generic-term-verified anchors (compositional-
representations-from-prediction, binding-problem survey, linear/orthogonal-compositional-
generalization) + 8 carried/reconfirmed CITED@ anchors from the two prior 2026-07-29
design notes. Lit-scan calibration penalty applied throughout: HARD-WIN P deflated to
0.30 (base ~0.40-0.45 REASONED@ minus 0.15 uncharted-regime-transfer penalty); all
REASONED@ transfer claims flagged inline, not asserted as settled.
