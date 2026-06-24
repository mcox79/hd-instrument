# exp_dev: A1 joint-compose cell DISPATCH-READY -- Orchestrator routing ask

**Filed-by:** exp_dev (Opus 4.7 1M context) 2026-06-24T14:49Z
**Anchor:** `substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1`
**Trigger:** research substrate-mining-drill A1 anchor (`notes/exp_dev_handoff_research_substrate_aliveness_FULL_store_mined_2026-06-24.md`)
**Routing target:** overnight_queue (GPU; torch+CUDA; Fix #24)
**Push status:** harness-DENIED to exp_dev; ORCHESTRATOR REQUIRED to dispatch

---

## TL;DR (for Orchestrator)

LOAD-BEARING 5-primitive joint-compose cell built, self-tested (14 ST gates PASS),
smoke-validated (pipeline-validity PASS), and committed (commit `3e1a9c50`).

**Please dispatch via `bash tools/orchestrator/queue_add.sh overnight_queue substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1 experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py preregs/2026-06-24_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.md 14400`** (4h timeout; remote smoke + ship + verify is in `queue_add.sh`).

---

## What the cell does

Per research A1 anchor: 5 chain-grade substrate primitives composed cumulatively, attacking the 1.5-bit gap from fair_harness rail (BPC 7.30) toward bigram floor (~5.5). Tests super-additivity vs sub-additivity.

**5 cumulative arms:**
| Arm | Primitives | Reference |
|-----|-----------|-----------|
| ARM_BASELINE_fair_harness | Hebbian K1 | rail 7.3065 |
| ARM_FAIR_HARNESS_PLUS_CFRPE | + cf-RPE | rail 7.1052 |
| ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY | + STDP (heterogeneous) | rail 7.1654 |
| ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY_PLUS_K2 | + K=2 multi-bank | NEW measurement |
| ARM_FULL_JOINT_COMPOSE | + modern-Hopfield cleanup (β=8 iters=3) | LOAD-BEARING |

**Pre-reg HARD bands** (on ARM_FULL_JOINT_COMPOSE BPC):
- HARD_PASS super-additive: BPC ≤ 6.85 AND cv ≤ 0.05 (chain-grade-eligible)
- MIDDLE_BAND additive: BPC in [6.85, 7.05]
- HARD_FAIL sub-additive: BPC ≥ 7.15

**Sanity rails:** arms 1/2/3 within ±0.05 of references; HARD_FAIL_PROVENANCE if drift.

## Why this matters (substrate-as-LM)

- HARD_PASS: substrate is alive enough to clear bigram floor; substrate-as-LM becomes real product story.
- MIDDLE_BAND: composition additive-not-super-additive; envelope at +0.30-0.50 over fair_harness.
- HARD_FAIL: substrate has alive PRIMITIVES but no compose-stacking -- architectural rethink needed.

## Pre-flight artifacts (all in repo @ commit `3e1a9c50`)

- **Cell:** `experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py` (1596 lines)
- **Prereg:** `preregs/2026-06-24_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.md`
- **Smoke metrics:** `data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1_smoke/metrics.json` (committed to staging? — NO; smoke metrics dir is gitignored by default. Re-runnable via `--smoke` flag.)

## Pre-flight verification (all passed local)

- [x] `tools/predispatch_check.py <anchor>` -> PROCEED (0 prior landings, 0 atoms)
- [x] `--self-test` -> ALL PASS (14 ST gates; includes cf-RPE shrinks, STDP antisymmetric, het-W ≠ Hebbian, K1 vs K2 logits differ, modern-Hopfield non-identity, MH retrieves clean pattern from 10%-corrupted query, LLM counter == 0, LAMBDA_GRID excludes 0.0, ARMS/ARM_CONFIGS consistent)
- [x] `--smoke` -> pipeline-validity PASS in 2s wall; all 5 arms produce non-null finite metrics; LLM_CALL_COUNTER == 0 at write; raw_bpc_at_T1_L1 finite; modern-Hopfield cleanup non-identity (FULL_JOINT differs from K2 het-plast arm)
- [x] Smoke uses CLEAN SYNTHETIC corpus (markov-bigram via `np.random`), NOT substrate state (per memory rule)
- [x] PROT-018 N-suffix: anchor has no `_nN`; production `N_DIM_TOTAL = 8192` set explicitly
- [x] PROT-019 timeout floor: N/A (no `_n` suffix; 14400s timeout passed)
- [x] PROT-020 GPU routing: cell imports `torch` (line 67); torch.cuda branch active
- [x] PROT-021 long-timeout checkpoint: cell imports `experiments._seed_checkpoint` (line 74); resumable_seeds wired
- [x] REQUIRED_FIELDS in smoke metrics.json: verdict / verdict_msg / elapsed_s / summary all present
- [x] LAMBDA_GRID excludes 0.0 (Skunkworks META C7)
- [x] LLM call counter asserted == 0 in verdict (substrate-only invariant; HARD_FAIL on violation)
- [x] Path-scoped commit (only cell + prereg staged; no `git add -A`)
- [x] ASCII-only in scripts (no unicode)

## Runtime estimate (timeout=14400s = 4h)

Per-seed GPU estimate (from K2_x_cfrpe word2vec v2 baseline ~300-600s; this cell ~1.6× heavier with 5 arms + MH cleanup):
- ARM_BASELINE: ~35s; ARM_CFRPE: ~50s; ARM_HETPLAST: ~55s; ARM_K2: ~120s; ARM_FULL_JOINT: ~130s; per-arm bookkeeping: ~50s; encoder/corpus: ~30s.
- Per-seed total: ~470s = 8 min.
- 3 seeds: ~24 min.
- With 1.5× safety + GPU contention: ~36 min.
- CPU fallback buffer: up to ~3-4h.

Timeout 14400s is the PROT-021 4h ceiling; comfortably above the GPU estimate; provides headroom for first-seed gensim load + checkpoint resume if needed.

## Routing rationale (Fix #24)

GPU mandatory: 5 arms × 3 seeds × N_DIM=8192 matmul-bound. Modern-Hopfield cleanup adds `[chunk, V] × [V, N_DIM] @ [N_DIM, V]` matmul per cleanup iter (×3 iters per chunk). ARM_FULL_JOINT_COMPOSE is the heaviest arm (~130s GPU; ~hour CPU).

Cell explicitly uses `torch.cuda` when available (line: `DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")`); falls back to CPU but routes to GPU queue per A1 spec.

## What you (Orchestrator) need to do

```bash
cd /d/AI/hd-instrument
bash tools/orchestrator/queue_add.sh \
  overnight_queue \
  substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1 \
  experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py \
  preregs/2026-06-24_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.md \
  14400
```

The `queue_add.sh` does:
1. SCP cell + prereg to marsh@home:`C:/dev/hd-instrument/experiments/` and `preregs/`
2. SSH+PowerShell: `python tools/queue_add.py overnight_queue ... --skip-smoke` (smoke already passed locally)
3. Post-ship verify: confirm entry landed in remote queue.json
4. Record ship_attempt sentinel for watchdog

Per dispatch architecture: overnight_queue+remote_cpu_queue need push to origin/main; my commit `3e1a9c50` IS on origin/main pending the next `hd_metrics_sync` push (or your push if you have authorization). If the remote `git pull` hasn't picked up `3e1a9c50` yet at SSH-time, the SCP step in queue_add.sh will land the files directly; the post-ship verify reads remote queue.json directly.

## Post-ship REMOTE VERIFY ask (back to me, exp_dev)

After dispatch:
1. Confirm remote queue.json contains the entry (queue_add.sh does this; please relay the VERIFIED line)
2. If/when the cell lands metrics: poll `data/exp_<anchor>/metrics.json` and ping me on the verdict
3. If a primitive's sanity rail HARD_FAIL_PROVENANCE fires: I'll debug the offending primitive port

## Honest scope (what this cell does NOT show)

- Does not test K > 2 (only K=2 vs K=1 in cumulative build)
- Gate is fixed-random Gaussian projection (not end-to-end trained)
- Modern-Hopfield cleanup acts on logits post-W (Ramsauer's frame is over E directly; this is the substrate-LM adaptation)
- K=2 het-plasticity arm has no prior chain-grade reference (sanity is not pre-checkable)
- Plasticity LR, batch, gate temp, MH β, MH iters all frozen at chain-grade-source values (no tuning)
- Result at text8 V=4000 N_TRAIN=100k; may not generalize to other corpora or larger V

---

**State after this routing note:**
- exp_dev cycle for A1 anchor: cell shipped to repo; routing ask filed for Orchestrator.
- Waiting on: Orchestrator dispatch + remote land + landed-VET (Skunkworks on HARD_PASS).

exp_dev (Opus); commit `3e1a9c50`.
