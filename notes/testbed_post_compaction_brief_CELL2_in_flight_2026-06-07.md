# Testbed POST-COMPACTION BRIEF — CELL-2 IN FLIGHT — read FIRST on resume

**Compiled:** 2026-06-07 ~01:55 UTC
**Read this FIRST after any compaction event.**

---

## 🔴 ACTIVE CLOUD RUN: CELL-2 Wikipedia layer-15 extraction

| Item | Value |
|---|---|
| **Cluster name** | `cell2wiki-162723` |
| **SKU** | gpu_1x_gh200 ($2.29/h) |
| **Region** | us-east-3 (Lambda) |
| **Lambda instance ID** | `5a3e2d80967b491c94ac23df1562871d` |
| **IP** | 192.222.51.240 |
| **Acquired at** | v1 19:43 (killed); **v2 acquired 2026-06-06 20:27 UTC** |
| **Expected wall** | v2 with DataLoader(workers=8, prefetch=4): **~1.5-3h** (was 9h on v1 single-stream) |
| **Expected cost** | **$3-7** (well under Research's $31-50 envelope) |
| **v1 killed because** | single-stream IO bottleneck: 192/s on GH200; GPU at 2.6% utilization. Redesigned with parallel DataLoader. |
| **v1 partial preserved** | `data/cell2_results_v1_partial_41shards/` (different shard scheme; reference only) |
| **HARD cost cap** | ~$30 (12-hour autostop is launcher safety; if anything bigger, kill manually) |

### Process state on `marsh@home`/WSL

| PID | What |
|---|---|
| `29488` (Windows) | wsl wrapper for the v2 launcher Start-Process |
| `105392` (WSL) | `bash /mnt/d/AI/hd-instrument/skypilot/smart_launch_cell2.sh` (v2) |
| `[child]` (WSL) | `sky launch -c cell2wiki-162723 ...` subprocess |
| Lock file | `/tmp/smart_launch_cell2.pid` (holds `105392`) |

### Monitor (auto-armed)

- Task ID: `bavl5upnn` (v2; bxtvospv2 was v1, now stopped)
- Pattern matches: CAPACITY DETECTED, ACQUIRED, sky launch exit code, launch failed, setup N/7, run complete, VERDICT, traceback, error, OOM, shard NNNN0000, COMPLETE/PARTIAL/FAILED, module-not-found
- ANSI codes stripped via `sed`
- Will surface key events automatically

### What the launcher AUTONOMOUSLY does after run completes

The launcher's post-acquisition code (already running as part of PID 103533) will:
1. SCP rsync `~/sky_workdir/data/exp_substrate_wikipedia_layer15_cache_extraction_v1/` → `/mnt/d/AI/hd-instrument/data/cell2_results/` (~26 GB shard transfer; uses `--partial --progress`)
2. Issue explicit `sky down -y cell2wiki-162723`
3. Run `verify_no_lambda_instances.sh`
4. Release the lock file via TRAP cleanup

**No manual finalization needed** unless launcher crashes mid-flight.

---

## Files involved (post-compaction navigation)

| File | Purpose |
|---|---|
| `experiments/exp_substrate_wikipedia_layer15_cache_extraction_v1.py` | The cell script (17592 bytes; AutoModel + last-token + streaming + atomic shard write) |
| `skypilot/cell2_wiki_gh200.yaml` | GH200 YAML (cu128 aarch64 torch install for Grace Hopper) |
| `skypilot/smart_launch_cell2.sh` | Smart launcher with PID lock + TRAP + preflight + sky api stop + GH200-only polling |
| `skypilot/build_cell2_ship.sh` | Bundle builder; targets `/root/cell2-ship/` |
| `skypilot/preflight_cloud_dispatch.sh` | 6-check gate (script-ref consistency, bundle, orphan procs, Lambda direct probe, sky status, HF token) |
| `data/cell2_smart_launch.log` | Launcher log; tail to check progress |
| `data/cell2_smart_launch_stdout.log` | PowerShell-side stdout (redundant) |
| `data/cell2_results/` | Where ~640 shards (~26 GB) + metrics.json will land |

---

## What to do on resume (in order)

### Step 1: Check if CELL-2 still running

```bash
wsl -d Ubuntu -- bash -c "python3 /tmp/ci.py 2>&1 | head -3"
wsl -d Ubuntu -- bash -c "source /root/skyvenv/bin/activate && sky status 2>&1 | head -8"
ls -la /d/AI/hd-instrument/data/cell2_results/ 2>&1
tail -30 /d/AI/hd-instrument/data/cell2_smart_launch.log
```

### Step 2: Possible states

| State | What it means | Action |
|---|---|---|
| Lambda has 1 instance booting/active + sky cluster INIT/UP | Still running | Wait + tail log periodically |
| Lambda has 1 instance + sky cluster gone | Launcher just terminated cluster; rsync may be in flight | Wait for launcher to finish; check `cell2_smart_launch.log` for "CELL-2 ACQUIRED + RAN" and "SCPing CELL-2 metrics" lines |
| Lambda 0 instances + `data/cell2_results/metrics.json` exists | Run COMPLETED CLEANLY | Read metrics; file delivery note to Research |
| Lambda 0 instances + no metrics.json | FAILED somewhere | Diagnose via launcher log; check for sky launch exit code != 0 |
| Lambda has 1 instance + no launcher process alive | Orphan instance (zombie scenario from earlier today) | Manual `sky down -y cell2wiki-162723` + Lambda API direct terminate via tmp_nuke_all.py pattern |

### Step 3: If COMPLETE — what to do

The run produces `data/cell2_results/metrics.json` plus ~640 `shard_NNNNN.npz` files (~26 GB total). Each shard contains:
- `hidden_states` (fp16, ~10000 × 2048)
- `article_ids` (object array)
- `titles` (object array)
- `token_counts` (int32 array)

Verdict types in metrics.json:
- `COMPLETE`: extracted_this_run + skipped_existing_this_run ≥ 0.95 × TARGET_ARTICLES (6.5M)
- `PARTIAL`: less than 95% — resumable via re-dispatch
- `FAILED`: 0 shards on disk (catastrophic)

If COMPLETE: file a delivery note to Research describing total articles, n_shards, GB on disk, layer used, hidden_dim, time + cost. Standing item: this cache is the foundation for CELL-3 (distilled 22M student training data) and downstream substrate work.

---

## Other context to NOT lose

### Today's findings (locked into project state)

- **CELL-1 ARCHITECTURAL_CONFIRMED**: 70B late-layer crash is real (not NF4 quant)
- **70B-Instruct ARCHITECTURE_ROBUST + Instruct destroys mid-depth**: USE BASE NOT INSTRUCT for all Phase 4 cells
- **Layer convention**: 1B Base L=15; 8B Base L=29; 70B Base L=50 (mid for 70B; late for smaller)
- **FAISS env fix**: WSL Linux venv `/root/faiss-env` with `faiss-cpu==1.12.0 + numpy==2.2.6`; HP-12 V2 HNSW cell unblocked
- **SkyPilot API server cache**: must `sky api stop` after CSV catalog patches (lesson from us-southeast-1 dispatch)
- **`us-southeast-1` is now in SkyPilot catalog** (manual CSV patch at `/root/.sky/catalogs/v8/lambda/vms.csv`)

### Standing items (post-CELL-2)

| Item | Status |
|---|---|
| **CELL-5** cascade distillation FD smoke (Path X + Option 4) | Ready to fire when user says go (Together API key in `.together_token` already verified; key prefix `tgp_v1_ysc...`; 405B accessible) |
| CELL-3 distilled 22M student ($15) | Gated on CELL-2 |
| CELL-4 HP-12 V2 at 100K ($10-20) | Gated on CELL-2; FAISS env now ready |
| HP-12 V1 5-min screen recording | User manual task |
| Llama-3.2-1B runner re-download | DONE today (model.safetensors 2471.6 MB at runner HF cache) |

### Today's commits to recall (most recent)

```
2e746cc testbed: Llama-3.2-1B weights re-downloaded; G15/G16 unblocked
[next commit, after CELL-2 dispatch happens to land in this brief] (search by date)
5cef2ed testbed: FAISS env fix DONE (WSL Linux venv); HNSW cell unblocked
ac76340 testbed: dual-SKU smart launcher (CELL-1 hardening pattern)
2cfaf8c testbed: CELL-1 ARCHITECTURAL_CONFIRMED + delivery note
365342c (and similar) testbed: smart launcher region filter fixes
```

### Total cost today as of compaction

| Cell | Cost |
|---|---|
| CLOUD-1 v1 (sunk; mean-pool bug) | $0.50 |
| Failed bootstraps + zombies | $0.20 |
| CLOUD-1b binding test | $0.63 |
| CELL-1 fp16 70B disambiguation | $1.95 |
| 70B-Instruct follow-up | $0.69 |
| FAISS env fix (no cloud) | $0 |
| Llama-1B runner re-download | $0 |
| **CELL-2 (in flight)** | **est. $5-9** |
| **Total post-CELL-2 expected** | **~$9-13** |

---

## Critical safety rules (do not forget post-compaction)

1. **Verify only ONE smart_launch process running** — duplicate launchers can spawn orphan clusters
2. **Watch Lambda API directly** — sky status can be stale; trust direct probe
3. **Never `sky api stop` while CELL-2's sky launch is in flight** — would orphan the subprocess
4. **Cluster name `cell2wiki-162723` is unique** — if you see different cluster names (different HHMMSS), that's a NEW launch
5. **No dual-SKU** — launcher is GH200-only per user explicit request; don't fall through to H100 unless user re-authorizes
6. **rsync ~26 GB takes minutes** — be patient between sky launch exit code 0 and full metrics availability
7. **All 25 known bug defenses are in place** — see CELL-2 dispatch checklist in commit history

---

## END BRIEF

This brief is referenced by `MEMORY.md` entry `cell2-post-compaction-brief` for post-compaction discoverability.
