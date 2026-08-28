# Remote desktop compute — solver self-service brief (updated 2026-08-28)

**You have access to the remote desktop `marsh@home`: a CPU runner + a GPU (RTX 4060 Ti), for heavy/long runs.**
You queue your OWN runs by dropping a request file — a standing watcher (`hd_remote_run_watcher`, every 5 min)
turns it into a real run. **No preregs, no ssh, no pinging strategy.** You are deliberately walled off from the
remote box; the tooling does the prereg + remote ops for you. Standing rule: heavy/long runs go remote;
lightweight probes/self-tests stay inline.

## The 5-minute version
1. Make your cell **remote-safe** (rules below — these are what actually bite).
2. Drop `notes/problems/<your-slug>/REMOTE_RUN_REQUEST_<cell>.md` (you may write your own problem folder).
3. Wait ≤5 min. The watcher validates, writes the prereg, ships your code + data, and queues it (CPU or GPU).
4. Read your verdict at `results_path` after the ~20-min sync (or `python tools/orchestrator/scp_recover_landing.py --verify-after <cell_name>`).
5. To re-run after a fix, **EDIT the request file** (even one character) — it auto-re-fires with `--rerun`.

## Make your cell remote-safe — ALL required (each line here is a real failure we hit)
1. **NO spaCy on any RUN-TIME path.** The remote has no spaCy (documented install failure). It is not enough to
   avoid a module-level `import spacy` — a spaCy import inside ANY function reached during the full run crashes it,
   and **your `--self-test` may not exercise that path (this is the #1 trap).** Load a PRE-PARSED cache; never parse.
   If an **hdlab module you depend on** imports spaCy at run time, that is a strategy-side fix — flag it. (The
   fulfiller now emits a `RUN-TIME spaCy RISK` warning pre-dispatch when your dependency closure imports spaCy — heed it.)
2. **Default to FULL on a bare invocation.** The runner invokes your cell with `--timeout` but **NOT** `--mode full`.
   So write `smoke = bool(args.smoke) or args.mode == "smoke"` (bare == full). A smoke-default cell silently runs a
   tiny sample and usually dies on an unshipped smoke cache. (The fulfiller warns if it sees `mode != "full"`.)
3. **Declare EVERY data dependency** as `# KB_REFERENT: <repo/relative/path>` — including files read by **sibling
   experiments or hdlab modules** you import, not just your own. If anything on your run path `open()`s a file,
   declare it. Undeclared dep → `FileNotFoundError` on the remote. (hdlab `.py` CODE is auto-shipped — the whole
   import closure incl. sibling→hdlab chains — you do NOT manage that.)
4. **Expose `--self-test`** (and/or `--smoke`), GREEN locally — required. **But self-test GREEN ≠ the full run
   works** (see #1/#3). If you can, run the full path once locally.
5. **Persist results robustly.** Write `metrics.json` **incrementally / per-arm** (`partial: true`, `arms_done`)
   so a late failure or timeout KEEPS completed arms. (A run this session computed its entire verdict, then crashed
   writing the file → result lost. Don't let a write bug erase a completed run.)

## The request file (front-matter)
```
---
cell: experiments/exp_yourcell_v1.py
mode: full                         # or  args: "--mode full --k 50"
queue: remote_cpu_queue            # CPU (numpy/scipy/sklearn, NO torch)
#  OR: queue: overnight_queue      # GPU runner (RTX 4060 Ti) — REQUIRED if your cell imports torch
timeout_s: 7200
results_path: data/exp_yourcell_v1/metrics.json
self_test: green
question: one-line question
gate: X beats the strongest FLOOR CI-separated AND beats the info-free TWIN (recompute floors per population)
kb_referents:
  - data/.../your_cache.jsonl
  - data/.../your_gold.txt
---
(free-form notes: arms, floor, twin, population)
```
Omit `queue:` and it auto-routes by torch usage (torch → GPU, else CPU). A torch-less cell aimed at the GPU queue
is rejected (it would idle the GPU).

## What's automatic vs. yours
- **Automatic:** the prereg; hdlab CODE shipping (the full import closure, incl. sibling→hdlab chains, ship-if-missing);
  declared-`KB_REFERENT` DATA shipping; CPU/GPU routing; dispatch; the remote `--self-test` gate; re-run on edit.
- **Yours:** the 5 remote-safety rules above; a GREEN `--self-test`; declaring every data dep; a robust metrics write.

## Results & re-runs
Results land at your `results_path` via the ~20-min sync. Watch `data/remote_run_request_watcher_log.jsonl` for
dispatch outcomes and `data/remote_cpu_queue/<cell>.log` (on remote) for run errors. **Edit the request file to
re-fire** (resets a failed remote entry via `--rerun`). Strategy does NOT integrate on your result — it stays WIP
until `owner_verdict: DONE`.

## Big-data caveat
Not everything is on the remote. **GB-scale corpora/caches may need a one-time strategy sync** (they are not in git).
Declare them as `KB_REFERENT`; if a run fails on missing data, say so and strategy syncs it. Small declared files are
shipped automatically.
