# exp_dev handoff snapshot (Phase-3 Agent-Teams migration)

**Written:** 2026-06-22 (real `date -u` ~00:00Z) by the exp_dev session that ran this turn-sequence. Standstill in effect.

---

## 1. CURRENT IN-FLIGHT WORK
- **U1 ingest-eval (`u1_fb15k237_ingest_eval_v1`) is DONE and atomized.** Full run (3 seeds, N=8192, scale-curve to 50k) completed naturally during standstill; HARD_PASS across all 3 load-bearing bands. Metrics committed (d46ec0c6). Routed to Skunkworks for landed-VET (301ccde0) with honest caveats. **Nothing of mine is mid-step.**
- **Anisotropy-rescue 4-arm landed** earlier this session — Skunkworks's landed-VET is in progress (their notes flag fly-LSH rank-agnostic CONFIRMED but noise-brittle at low eff-rank + storage-win needs compressed-rerank). My PRE-REG fc3b8771 (A sparse-superposition FAILS / B tag-retrieval WINS) was validated.
- **NEW-4 per-cluster-stratified** is in an uncertain state — local dir has only a self-test gate-log, no metrics dir. Did NOT relaunch (standstill). Flag for the next exp_dev teammate to triage with Orchestrator.
- I did NOT start M1 or N3-cert-cell (both were next in my queue when STANDSTILL fired; halted cleanly).

## 2. WORKING ASSUMPTIONS (not in plan.json / fleet_waiting_on)
- The storage-chain arc has cleanly resolved into "dense-superposition (item#3) is CLOSED for high-M on intrinsic-anisotropic LM keys; tag-retrieval (item#4 attention OR fly-LSH) is the high-M path." This is convergent across whitening MM + my eff-rank + the rescue land + Skunkworks's flylsh analysis. I treat it as load-bearing for M1 design.
- **Multi-value Hebbian-accumulate ingest + set-readout** is the correct U1 ingest mechanism (resolves the 25.8% 1-to-many keys; ceiling rises from ~0.742 single-value to 0.99 at scale). OPEN-E vindicated at scale. M1 should use the SAME multi-value approach when it gets built.
- The wikitext2 HF loader is BROKEN NOW; any wikitext2-using cell silently falls back to synthetic. phase_d_tier6's prior MIDDLE_BAND is doubly-suspect (synthetic + gameable ratio band). Skunkworks adopted NEEDS-RERUN.
- N3 sequencing: **Shakespeare shakedown (CPU, harness validated) → text8 cert (GPU)** — Skunkworks's absolute-floor bands replace any ratio-to-baseline framing. text8 cert requires the N1↔N3 boundary confirm (does N3 eval N1's concept-LM or a standalone substrate char-LM?). My read of the existing `testbed/substrate_lm/` infra (phase_d_tier6 base, SubstrateCharLM 4-primitive) is that **standalone substrate char-LM (option b)** is the more likely answer — but I won't author the cert until Research confirms.
- N1 (concept-LM) landed MM/substrate-only-PASS — that's the first substrate-native LM, a real capability milestone. Orchestrator's lane; not mine to claim.

## 3. WHAT I WAS ABOUT TO DO NEXT (queue at STANDSTILL fire)
1. **M1 attention-store comparison cell** — same FB15k-237 50k ingest, but item#4 attention store (softmax over keys) instead of U1's Hebbian-superposition. Tests whether attention-retrieval matches/beats Hebbian on the ingest. Direct comparison: same data, different store primitive. Buildable; gated only on U1 ingest validating at scale (it did, 0.99 set-recall).
2. **N3 Shakespeare shakedown extension → text8 cert authoring** — once Research confirms the N1↔N3 boundary, extend the shakedown harness (works on real shakespeare, `shakespeare_char_corpus` loader done) to a text8 cert run with Skunkworks's N3 absolute-floor + by-construction guards + substrate-only-decode + VQ-floor.
3. **Re-point the eff-rank diagnostic at the real substrate-LM key pipeline** (N3/M1 readable text + contrastive at scale) — the decisive dense-vs-tag-retrieval measurement on what the substrate-LM actually uses.

## 4. TACTICAL CONTEXT (what fresh exp_dev wouldn't know from memory + notes alone)
- The **eff-rank discrepancy with Skunkworks** was reconciled honestly: Skunkworks initially had `readable~templated 1.15×` (concluded "intrinsic, refuted"); my 3-metric reconciliation (PR / Roy / stable-rank) on shakespeare showed readable IS 2-4.7× higher across all metrics. We DID NOT diverge — Skunkworks owned a "last-token-conflation" bug behind their 1.15× and concurred with my "more-headroom-not-reopened" framing. **Don't re-litigate this. The convergent practical conclusion: dense more-headroom-not-reopened, high-M non-viable, tag-retrieval is the path.**
- My **PR vs Roy vs stable-rank reconciliation tool** is in `experiments/exp_dev_diag_templated_vs_readable_key_eff_rank_v1.py`. Reusable on any key set. The lesson: don't report a single rank metric for a load-bearing claim — report all three.
- **The U1 cell stalled the first time I launched it** (laptop sleep + no checkpointing = my discipline violation per my own "long cells must checkpoint+resume" memory). Fixed: per-seed CONFIG_VERSION-gated resume + vectorized BLAS ingest (20×) + chunked. The fixed cell ran to completion in ~13 min total wall (777.7s reported).
- **The U1 inference-transfer baseline is scoped.** Skunkworks's band wanted "frozen-encoder single-hop" — but FB15k-237 entities are MIDs (`/m/027rn`), not readable. So a frozen sentence-encoder is meaningless. I used the **1-hop-lookup baseline** (MID-valid), which is ~0 by construction (heldout has no direct edge). So "substrate composes beyond graph-lookup" is shown (0.381 vs 0.007 = 54×); "beats a semantic encoder" is **UNTESTED** (OPEN-C deferred; needs FB15k-237 entity-name mapping). Fresh exp_dev: if you stage `entity2text.txt`, add the frozen-bge baseline to U1 v2.
- **N3 shakedown found two real things** the fresh teammate should respect: (a) substrate char-LM at smoke scale on REAL text is at chance (`BPC 5.834 ≈ uniform 5.833`) while baseline learns — phase_d_tier6's apparent learning was on synthetic data (broken wikitext2 loader); (b) the phase_d_tier6 BPC-ratio band (substrate ≤ 2.0× baseline) is gameable — chance substrate reads HARD-PASS when baseline is weak. Both validate why Skunkworks's N3 absolute-floor + real-baseline bands matter. **Don't use ratio-bands for N3; use absolute floors against real chance/bigram baselines.**

## 5. CRITICAL OPEN LOOPS
- **U1 landed-VET pending** (Skunkworks). Result is HARD_PASS, but the cert call is theirs, not mine.
- **N1↔N3 boundary confirm** (Research) — does N3 evaluate N1's concept-LM applied to char-BPC, or a standalone substrate char-LM? Affects N3 cert structure. I'm betting on standalone (option b) per the phase_d_tier6 infra, but won't author until confirmed.
- **NEW-4 fate** — uncertain status (no metrics dir locally). Was on the local runner ~hours ago. Did it complete? Stall? Get killed? Needs Orchestrator triage.
- **Frozen-encoder baseline for U1 (OPEN-C)** — deferred because FB15k-237 is MIDs. Stage entity-names → add the stronger baseline → re-run U1 → stronger cert.
- **tau ≈ 0 on the U1 refuse-gate** — the in-KB vs OOD top-1-score separation is small-magnitude but consistent. Worth Skunkworks's eye for robustness/noise-sensitivity in the VET.
- **The fleet-infra issues** I surfaced this session (Orchestrator silent ~2 hr; Skunkworks Bash/Python down for a while) appear resolved — Skunkworks recovered + filed multiple notes. Orchestrator filed a STANDSTILL ACK (3 min before USER directive landed). But if these recur post-migration, the agent-teams architecture may need its own liveness story.

## 6. POINTER TO MY LAST 3 NOTES
- `notes/exp_dev_to_skunkworks_U1_LANDED_hardpass_VET_request_2026-06-21.md` (the U1 HARD_PASS landed result + caveats + VET ask)
- `notes/exp_dev_to_all_STANDSTILL_ACK_inflight_inventory_2026-06-21.md` (STANDSTILL ACK + in-flight inventory)
- `notes/exp_dev_to_skunkworks_U1_fidelity_NOT_by_construction_1to_many_2026-06-21.md` (the critical 1-to-many fidelity-ceiling finding + OPEN-E multi-value recommendation)

Earlier in the same arc: `exp_dev_to_skunkworks_U1_ingest_cell_DESIGN_schema_vet_2026-06-21.md` (the U1 design SCHEMA-VET, OPEN A-E); `exp_dev_to_skunkworks_eff_rank_RESULT_templated_vs_readable_2026-06-21.md` (the load-bearing eff-rank finding); `exp_dev_to_skunkworks_anisotropy_rescue_PREREG_prediction_2026-06-21.md` (fc3b8771; pre-reg validated by the rescue land).

---

## 7. ACCUMULATED ROLE KNOWLEDGE (load-bearing addition)

### 7a. Workflow patterns I actually use

**Authoring a cell — the order matters:**
1. **Read the base cell first.** If a similar cell exists (look in `experiments/exp_*`), extend it; don't write fresh. Pattern-match on the closest precedent — it captures conventions (selftest format, RUN_MODE handling, CONFIG_VERSION, metrics.json shape) that aren't documented but are load-bearing.
2. **Write the selftest BEFORE the smoke runner.** The selftest is the unit-test of the mechanism; it catches "does the math even work" in seconds, before you waste minutes on an encode. My U1 selftest caught the 1-to-many key-collision issue immediately — that became the most important finding of the cell.
3. **Smoke after selftest.** Smoke = the full pipeline on a tiny config (pythia-160m, N=2048, M=hundreds). It catches integration bugs (import paths, metrics-shape mismatches, the wikitext2-fallback class). Smoke should run in ~30s-3min on CPU.
4. **Then dispatch full** (or run full locally if CPU-cheap). Full = the science. Always vectorize BLAS-able loops before dispatching (`outer(...)` in a Python loop → batched matmul saves 10-100×). The U1 vectorization went 50k iterations → 1 chunked matmul → 20× faster, makes the full run feasible locally instead of on the runner.

**When a cell lands (mine or someone else's):**
1. Check `run_mode` in `metrics.json` FIRST. If it's `smoke`, the verdict isn't the cert. I was bitten by this twice this session — the whitening cell's metrics.json on my local machine was stale `run_mode=smoke` from my pre-dispatch validation; the REAL `run_mode=full` result was synced separately by Orchestrator. **Never read `metrics.json` without checking `run_mode` against the expected.**
2. Check `n_seeds` matches the expected full config. Mismatched seed count = stale partial / wrong run.
3. Independent re-derive: load the per-seed dict + compute the verdict metrics yourself, don't trust `verdict_msg`. (Skunkworks's discipline; I've adopted it.)
4. If `cv` is reported and > the band (typically 0.05), it's seed-unstable even if the mean passes — call MIDDLE_BAND, not HARD_PASS.

**When deciding "is this worth atomizing":**
- Pure characterization (a measurement) → not a cert; atomize as a MEASURED_MECHANISM in the Store via Skunkworks.
- A claim with a threshold (PASS / FAIL bands) → cert candidate; needs Skunkworks's landed-VET.
- A negative result (HARD_FAIL or HONEST_NEGATIVE) → still atomize; Research routes a 2x-revival drill per USER standing.
- A bug I caught + fixed → atomize as a discipline (META cert-neutral), not as a result.

**When pinging another role:**
- Always check `data/fleet_waiting_on.md` FIRST. They may have already addressed it. I almost sent a redundant eff-rank discrepancy note today — checking the tracker caught that Skunkworks had already CONCURred + owned the bug.
- Always include `[from=<my_role>]` and `[type=<event-type>]` tokens in shared-tracker entries (the dashboard parser uses them).
- Filename ≤120 chars; single primary recipient + `cc_<other>` in body (not in filename).

### 7b. Mistake patterns I've caught (mine + others')

- **Cited number doesn't reproduce from the cell.** The dominant failure mode in the cert audit. Always re-run the cell or read its per_unit to verify a cited number; don't trust a summary string. (This is my main job per Skunkworks's audit-discipline catalog.)
- **Stale-checkpoint resume from a different config.** If `_ckpt_key` doesn't include all result-affecting params (`run_mode`, `proj_dim`, `TRAIN_M`, etc.), a re-dispatch with new params silently resumes the old partials. **CONFIG_VERSION must include every param that affects the result.** D1 cells, dense-KV cells, and my own U1 v1 all bit on this. Fix: per-seed checkpoint key derived from a hash of the full run-config; assert the loaded partial's stored config matches before continuing.
- **Synthetic-PoC over-estimate.** Skunkworks's whitening PoC showed 0.84 on synthetic; real keys came back 0.025. Synthetic anisotropy (single common-mode) ≠ real anisotropy (multi-directional + low eff-rank). **Mechanism validated on synthetic must deflate P(real-data success) by ~0.20-0.30.** Skunkworks atomized this as a META discipline (`8856b2ce`).
- **Templated-fact eval set as a proxy for "LM keys."** `make_facts` produces near-identical sentences → cm_frac=0.999 + tiny effective rank. This isn't intrinsic LM anisotropy; it's templating-amplified. Reporting "LM keys are low-rank" off `make_facts` over-claims. Always scope the conclusion to "this eval set" until measured on diverse readable text.
- **Silent data-fallback.** wikitext2's HF loader falls back to a synthetic bigram-Markov pseudo-corpus when HF is unreachable, and only prints to stdout — `metrics.json` never records "synthetic." Any cell using `allow_synthetic=True` can silently run on fake data. **For cert cells, ALWAYS pass `allow_synthetic=False` (fail-loud).** Same class as the phase05 truncated-npz issue earlier in the project.
- **By-construction-saturation in fidelity.** I assumed (and Skunkworks's band assumed) "exact in-KB recall is perfect-by-construction." False for a multigraph: a key-value store with 1-to-many keys has a fidelity ceiling well below 1.0 (25.8% of FB15k-237's (s,p) keys are 1-to-many; ceiling ~0.742 for single-value last-write-wins). Always quantify the by-construction ceiling before setting a "perfect" floor.
- **Ratio-to-weak-baseline band is gameable.** phase_d_tier6's `substrate ≤ 2.0× baseline` reads HARD-PASS when substrate is at chance AND baseline is weak. Replace with absolute floors against real chance/bigram baselines.
- **Hardcoding labels into summary strings.** My eff-rank diagnostic's summary said `"@M=10k"` even on a smoke run where M=200 — caused a brief misread of "stale smoke as full HARD_FAIL." Always compute labels dynamically from the actual config.
- **Over-claiming from one metric.** My PR-based eff-rank ratio (3.56×) was load-bearing; I should have reported PR + Roy-eff-rank + stable-rank from the start, not just PR. For any rank claim, report at least two metrics.
- **Building before SCHEMA-VET on a load-bearing mechanism.** I almost did this for U1's refuse-gate + inference-transfer. Pulled back, sent the design + OPEN A-E, de-risked OPEN-E with a quick PoC, THEN built. The "design SCHEMA-VET before guess-authoring 300 lines" discipline is worth slowing down for.

### 7c. Cross-role coordination patterns (unwritten)

- **Skunkworks's SCHEMA-VET responses arrive in ~minutes to ~hours depending on whether they're in /loop yolo or sleeping.** If you've sent a SCHEMA-VET and >30 min pass without response, check `fleet_waiting_on` for their state (in flight / steady-state / infra-down). Skunkworks goes infra-down occasionally (Bash/Python crash) — their notes are sometimes WRITTEN but UNCOMMITTED; their tracker section will say so.
- **Skunkworks is AUDIT-ONLY. They never author cells.** Don't ask them to write a cell, even a smoke. They VET; we author. They'll push back if you cross the line.
- **Research (Director) makes scope-decisions; I make cell-design-decisions.** Research decides which corpus / which lever / which scope; I decide the cell mechanism, the smoke gate, the dispatch path. Don't expect Research to specify the cell internals; don't expect Skunkworks to tell you which corpus to use.
- **Orchestrator owns push + scp + remote verify-it-starts.** Push is harness-DENIED to me; I route GPU/remote cells to Orchestrator with the dispatch ask. If Orchestrator goes silent, GPU results don't sync back even if the remote job completed. I learned to verify-the-referent on Orchestrator's activity before assuming a GPU run "just hasn't finished."
- **Testbed = integrator + infra refinements + 2nd-witness.** When Testbed files a "RED" or KEEPALIVE escalation, take it seriously — they monitor fleet health that I don't see. Their pings are not noise.
- **Route negatives to Research for a 2x revival drill** (USER standing). Every HARD_FAIL / HONEST_NEGATIVE / MIDDLE_BAND from a cell gets a routing note: "negative; here's a revival angle to drill." Research turns it into a research drill. This is per-negative, not one-time.
- **Reciprocal-if-count-move.** If a verdict moves the cert count (PROMOTE / DEMOTE), Skunkworks expects a reciprocal acknowledgement (you saw the move; you concur or push back). Silent count-changes erode trust in the cert-chain.
- **The "always check tracker before acting" rule is load-bearing.** USER caught Research missing waits twice. I caught myself almost re-litigating the eff-rank with Skunkworks today (tracker showed they'd already CONCURred). The cost of one Read on `fleet_waiting_on.md` is far less than the cost of a redundant note + a stale conversation thread.

### 7d. Substrate-specific intuition

- **A cell that produces `verdict=HARD_PASS` instantly should be suspicious.** Genuine HARD_PASS at full scale takes a meaningful run time (minutes-to-hours of compute). An instant HARD_PASS usually means: (a) resumed from a stale checkpoint, (b) ran in smoke mode by accident, or (c) the metric is by-construction-saturated. Always look at `elapsed_s` and `n_seeds` together.
- **A cell with `setrecall=1.0` at small scale is fine; at full scale it's suspicious.** Real-data, large-M retrieval shouldn't be perfect — crosstalk and the 1-to-many ceiling cap it. My U1 scale-curve hit 1.0 through M=25k and dropped to 0.99 at M=50k; that 0.99 is more believable than a 1.0 would have been.
- **The substrate is "healthy" when:** the dashboard `recent_verdicts` shows a mix of PASS / MM / honest-negative (not all one kind); cert count moves both up and down with disciplined reciprocal-acks; Skunkworks's open SCHEMA-VET backlog is <5; no session has been silent >1 hour during work hours.
- **Early-warning signs:** (a) two consecutive smoke results that "look too good" on a new mechanism = synthetic-overestimate brewing; (b) Orchestrator silent + a GPU dispatch un-acked = run probably stuck (verify remote + the scp); (c) `tasklist | grep python` jumps to 20+ procs = a runner left zombies, kill them before the next dispatch; (d) `.git/index.lock` exists more than briefly = a session is mid-commit, wait or it'll race.
- **The cert-chain "feels right" when:** every cited number in a verdict_msg can be re-derived from a partial within 1 minute; every "PASS" has a corresponding cv ≤ band; every negative routes to a revival drill within the same cycle.

### 7e. Tooling I reach for instinctively

**Bash one-liners:**
```bash
# fresh notes to me / to_all in last N min
now=$(date -u +%s); for f in $(ls -t notes/*.md | head -40); do age=$(( (now-$(stat -c %Y "$f"))/60 )); [ $age -gt 30 ] && break; b=$(basename "$f"); case "$b" in exp_dev_*) ;; *exp_dev*|*to_all*|*cc_all*) echo "${age}min: $b";; esac; done

# heartbeat touch (every turn)
touch data/last_processed_auto_f88f660e1d.timestamp data/heartbeats/exp_dev.timestamp

# check a cell's verdict + run_mode quickly
.venv/Scripts/python.exe -c "import json;m=json.load(open('data/exp_<NAME>/metrics.json'));print('run_mode:',m.get('run_mode'),'verdict:',m.get('verdict'),'n_seeds:',m.get('n_seeds'))"

# guard a commit against shared-index race
if [ -f .git/index.lock ]; then sleep 2; fi
git add -- <path>     # path-scoped, never -A or .

# python proc count (zombie / contention check)
tasklist | grep -ic python

# get real UTC, never guess
date -u +"%Y-%m-%dT%H:%M:%SZ"
```

**Python one-liners (inside `.venv/Scripts/python.exe`):**
```python
# load + summarize a metrics.json
import json; m=json.load(open('data/exp_X/metrics.json')); print(json.dumps({k:v for k,v in m.items() if k!='per_seed'}, indent=2))

# count 1-to-many keys in a KG (the gotcha for fidelity-by-construction)
from collections import defaultdict; sp=defaultdict(set)
for line in open('data/datasets/fb15k_237_train_50k.jsonl'):
    r=json.loads(line); sp[(r['subject'],r['predicate'])].add(r['object'])
multi=sum(1 for v in sp.values() if len(v)>1); print(f"1-to-many {multi/len(sp):.1%}")

# participation ratio + Roy eff-rank + stable-rank from eigenvalues (use ALL three for rank claims)
eigs = np.clip(np.linalg.eigvalsh(cov)[::-1], 0, None); s=eigs.sum()
pr = float(s*s/(eigs*eigs).sum()); stable = float(s/eigs[0])
p = eigs/s; p = p[p>0]; roy = float(np.exp(-(p*np.log(p)).sum()))
```

**Specific cells I reuse as base:**
- `exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1.py` for `make_facts` + `encode` + `_np_norm` + `fit_zca` + `apply_zca` + `train_contrastive` + `recall_at`. These are CERT591-faithful; copy them, don't reimplement.
- `exp_ccc1_extra_fb15k237_kg_multihop_v1.py` for `bipolar` + `cfrpe` + `load_kg` (the FB15k-237 ingest pattern).
- `exp_phase_d_tier6_full_pipeline_4_core_char_lm_v1.py` for the SubstrateCharLM + GradientCharLM driver pattern.
- `testbed/substrate_lm/` for the substrate-native LM infra (char_lm, baseline_gradient_lm, data, primitives).
- `experiments/_seed_checkpoint.py` for the resume-from-partials pattern (use it for any cell > 5 min wall).

**Dashboards / logs:** I tail `/tmp/<task_id>.output` (the harness writes background-task stdout there) when watching long-running cells; for runner-dispatched cells, the dashboard's `recent_verdicts` tile is the canonical view (others have built that).

### 7f. Open questions / unresolved tensions

- **OPEN-C frozen-encoder baseline for U1 is structurally limited by FB15k-237 being MIDs.** Either we stage `entity2text.txt` (one-time data prep) and add the bge baseline to U1, OR we accept the MID-valid 1-hop-lookup baseline as the cert bar (weaker). Skunkworks's VET on the landed U1 will likely surface this. My read: stage the names — it's a strictly-stronger baseline at modest data cost.
- **The phase_d_tier6 result (MIDDLE_BAND) is now formally NEEDS-RERUN.** When/how to re-run is open. The cleanest path: re-author with `allow_synthetic=False` + absolute-floor bands + real-baseline (the same fixes I baked into the N3 shakedown harness). This is a small cell-author task someone (likely me / next exp_dev) owes the cert chain.
- **The tension between "build now to make progress" and "SCHEMA-VET first to avoid rework"** comes up repeatedly. My heuristic: SCHEMA-VET for LOAD-BEARING mechanism choices; build directly for unambiguous infrastructure (data loaders, smoke harnesses, scaffolds). Don't SCHEMA-VET trivia; don't guess load-bearing.
- **The "in-flight cell completion under standstill" rule should be checked against Skunkworks's cert-chain hygiene.** My U1 completed + atomized after STANDSTILL fired — is that a cert-integrity risk (the rules-of-engagement changed mid-run)? I think no (the cell didn't change; only the post-cell action gating changed), but it's a precedent worth Skunkworks weighing in on.
- **The eff-rank diagnostic is a reusable substrate-characterization tool**, but it currently lives in `experiments/` (cell-shaped). Should it migrate to `tools/` (utility-shaped)? Same for the multi-value-ingest PoC. Tension between "experiments are cells" and "these are diagnostics, not certs."
- **The substrate's "high-M storage path" question is still open** post-rescue. Fly-LSH is rank-agnostic (good) but noise-brittle at low eff-rank (per Skunkworks); storage-win needs compressed-rerank (also Skunkworks). So fly-LSH isn't a clean win at high M either. What IS the substrate's high-M storage primitive? Open. M1 (attention-store on the U1 ingest) is the next probe; further options (product-key memory, phase-coding AM) are in Skunkworks's deferred-rescue list.
- **N1↔N3 boundary** — I lean standalone-substrate-char-LM (option b) but haven't pushed on it. Research owns the call.

### 7g. Files / paths I reference constantly

- `data/fleet_waiting_on.md` — every turn, check tracker before acting. My section starts at the `## exp_dev` heading; never touch other sections.
- `data/heartbeats/exp_dev.timestamp` + `data/last_processed_auto_f88f660e1d.timestamp` — touch every turn (the watchdog uses them).
- `notes/` — Glob `*exp_dev*`, `*to_all*`, `*cc_all*` filtered by mtime when checking what's new.
- `data/exp_<anchor>/metrics.json` + `partial_seed*.json` — every cell-land starts here.
- `experiments/exp_<anchor>.py` — read the SOURCE before VETing a verdict_msg.
- `experiments/_seed_checkpoint.py` — the resume primitives.
- `testbed/substrate_lm/{char_lm,baseline_gradient_lm,data,primitives}.py` — the substrate-native LM infra for N3 / char-LM work.
- `.venv/Scripts/python.exe` — ALWAYS this, never system python. The .venv has duckdb + torch + transformers + sentence-transformers. System python will produce false-greens (no torch → silent skip).
- `data/datasets/fb15k_237_train_50k.jsonl` — the U1 ingest data (50000 lines, MID-based triples).
- `data/shakespeare_cache/tinyshakespeare.txt` — my new addition (urllib-downloaded; the wikitext2 alternative for real-data shakedown).
- `tools/monitor_arm.py exp_dev` — the canonical monitor (Python port, popup-free; never re-arm the bash variant).
- `~/.claude/projects/d--AI/memory/MEMORY.md` — my index of disciplines + user-prefs + facts; CLAUDE.md only loads ~24KB so the index is curated.

---

## 8. U1 INGEST-EVAL — exp_dev's view of where it stands + remaining work

**Skunkworks's open loop:** "U1 HARD_PASS landed-VET" (their `[from=exp_dev] [type=cell_land]` wait). My view of where it actually stands:

**Status = result is in; cert call is theirs.**
- Cell: `experiments/exp_u1_fb15k237_ingest_eval_v1.py` (commit 373c8bb9; vectorized + per-seed checkpointed).
- Result: `data/exp_u1_fb15k237_ingest_eval_v1/metrics.json` (commit d46ec0c6) — 3 seeds (7/17/23), full 50k, N=8192, run_mode=full, elapsed 777.7s, verdict HARD_PASS.
- Routing note: `notes/exp_dev_to_skunkworks_U1_LANDED_hardpass_VET_request_2026-06-21.md` (commit 301ccde0) — has the per-band numbers + the honest caveats.
- The exp_dev side is COMPLETE. Nothing of mine is in-flight on U1.

**Numeric headlines (re-derive from per_seed, don't trust the summary string):**
- Fidelity (set-recall@k) @M=50k: all=0.990 ± 0.004, 1to1=0.988 ± 0.003 across seeds (3 of 3 > 0.95 floor).
- Refuse-gate: OOD-refuse 0.974 (0.963/0.993/0.967 per seed); in-KB-accept 0.958 (0.957/0.953/0.963). Both > 0.80 bar on every seed.
- Inference-transfer: substrate-2hop 0.381 (0.370/0.367/0.405); 1-hop-lookup baseline 0.007 (consistent across seeds; ~0 by construction).
- Scale-curve: {5k: 1.0, 10k: 1.0, 25k: 0.999, 50k: 0.99} — graceful, no cliff.

**What the cert-owner (Skunkworks) needs to do, not me:**
- Recompute each headline number off `partial_seed*_full.json` independently (the partials are gitignored but on disk locally; full re-run is ~13 min on CPU if needed).
- Audit the 3 by-construction guards (exact-closure NOT cert-graded — set-recall is the multigraph-faithful metric; `heldout_in_compose_graph==0` asserted in code + the `leak_skipped` counter is logged; refuse-gate non-circular: tau calibrated on first half of held queries, evaluated on second half).
- Decide the scope: cert with the MID-valid 1-hop-lookup baseline (current state), OR require the frozen-encoder baseline (deferred OPEN-C, needs entity-name staging).
- Eye the refuse-gate robustness — tau≈0 means the in-KB/OOD top-1 separation is small-magnitude; the calibration works but it's not a wide margin. Worth a sensitivity check (noise injection / cv on tau under perturbations).

**Remaining work I'd queue (post-VET, NOT under standstill):**
1. **U1 v2 with frozen-encoder baseline** — IF Skunkworks rules the 1-hop-lookup bar insufficient. One-time prep: stage `entity2text.txt` (FB15k-237 entity-name mapping, public dataset). Then add a bge-encoder single-hop similarity baseline to inference-transfer. Closes OPEN-C; gives a stronger cert.
2. **U1 refuse-gate robustness probe** — IF Skunkworks's audit flags the tau≈0 small-margin. Quick CPU PoC: add noise to keys at recall time, measure how OOD-refuse / in-KB-accept degrade. Reports whether the gate is brittle.
3. **U1 atomization into the Store** — once Skunkworks signs the VET, atomize the result as a cert-graded substrate-native-KB-ingest atom (Skunkworks A5-gated Store write; my role = produce + route, not write).
4. **Phase_d_tier6 re-run on real shakespeare** — separate from U1 but related: my N3 shakedown found phase_d_tier6's MIDDLE_BAND was on synthetic data (broken wikitext2 loader) + a gameable ratio band. The clean re-run is essentially trivial (extend the shakedown harness with the full 4-primitive substrate char-LM config; my shakespeare loader is `allow_synthetic=False` provenance-asserted). Quick cell when Skunkworks calls for it.

**The fresh exp_dev teammate should NOT re-author U1.** It's done. They should resume by reading `metrics.json` + the VET response + (if VET ratifies) atomizing.

---

## 9. NEXT N2 CHAIN-GRADE CELL — exp_dev's design plan absorbing Skunkworks's per-unit instrumentation spec

**Skunkworks's structural blocker (for any N2 chain-grade cell):** per_unit BPC + cv ≤ 0.05 + zero-LLM-call-counter LOGGED + VQ-floor decomposition. The next exp_dev teammate authoring an N2 cell MUST bake all four in from the start. Here's how:

### Cell anchor + scope (per Research's N2 frontier-drill + Skunkworks's N2-lever findings dfb41903)
- **Anchor name:** `n2_substrate_lm_lever_chain_grade_v1` (or similar; `[lever_x_lever]` if multiple coupled levers).
- **Levers (COUPLED per Skunkworks):** the chain-grade run sweeps **context-depth × codebook-granularity** jointly (not factored independently — Skunkworks's finding is that they couple via floor-masks). Optional secondary dimensions: capacity (V_C-sweep, per N1 storage-density scour), HD-binding-vs-count.
- **Corpus:** text8 (N3 primary per my N3 scope-decision) OR pythia-residual subset (N3 secondary; depends on Orchestrator's token-id-recovery cell). Real data, `allow_synthetic=False`. Real chance/bigram baseline computed on the same held-out split.
- **Run config:** SEEDS=[7,17,23,31,41] (5 seeds for cv tightness); per-seed CONFIG_VERSION-gated checkpoint per `experiments/_seed_checkpoint.py`; vectorized BLAS for any matmul-able loop.

### Per-unit metrics.json shape (load-bearing for Skunkworks's recompute-off-per_unit discipline)
```python
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": v, "verdict_msg": vmsg,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
    "config_version": CONFIG_VERSION,        # MUST include every param affecting BPC
    "per_seed": [                            # one entry per (seed, lever-config) cell
        {"seed": s, "lever_config": {...},
         "substrate_bpc": ..., "baseline_bpc": ..., "uniform_bpc": ..., "vq_floor_bpc": ...,
         "gain_above_vq_floor": substrate_bpc - vq_floor_bpc,  # the load-bearing claim
         "primitive_health": {...},
         "llm_forward_calls_at_inference": 0,  # MUST be 0; assert before write
         "wall_s": ..., "checkpoint_key": "..."},
        ...
    ],
    "aggregate": {                           # for the verdict_msg ONLY; never the cert
        "substrate_bpc_mean": ..., "substrate_bpc_cv": ...,
        "gain_above_vq_floor_mean": ..., "gain_above_vq_floor_cv": ...,
    },
    "by_construction_guards": {
        "vq_floor_methodology": "round-trip lossy bound: token -> concept_codebook -> token; BPC computed on the round-tripped tokens against the original",
        "real_data_asserted": True,  # allow_synthetic=False all the way down
        "zero_llm_call_at_inference": True,  # asserted from per_seed counters
    },
}
```

### The 4 load-bearing instrumentation requirements (Skunkworks's structural blocker)

**1. Per-unit BPC** (per-seed-per-lever-config):
- Every (seed, lever_config) point is a separate entry in `per_seed`; do NOT collapse before write. Skunkworks recomputes the aggregate off the per_unit, never trusts the summary.
- Store at minimum: `seed`, `lever_config` (dict), `substrate_bpc`, `baseline_bpc`, `uniform_bpc`, `vq_floor_bpc`, `wall_s`, `checkpoint_key`.

**2. cv ≤ 0.05** (across seeds, per lever_config):
- Compute `cv = std(substrate_bpc) / mean(substrate_bpc)` across seeds for each lever_config.
- HARD-FAIL the cell if any reported HARD_PASS config has cv > 0.05 (seed-unstable; don't cert flaky configs).
- MIDDLE_BAND if PASS conditions met but cv ∈ (0.05, 0.10]; HARD_FAIL if > 0.10.
- This is non-negotiable per Skunkworks's cv discipline (saved multiple cells from false-PASS this year).

**3. Zero-LLM-call-counter LOGGED** (the substrate-only audit gate):
- Add a counter `LLM_CALLS = [0]` (list-as-mutable-int) at module top.
- Wrap any conceivable LLM-forward call (transformers' `model.forward`, `model.__call__`, the embedding lookup, etc.) at the boundary the substrate uses. Simplest pattern: monkey-patch `transformers.PreTrainedModel.__call__` with a counter-incrementing wrapper at module import; assert the counter is 0 AFTER `score_bpc` returns.
- Log the per-seed counter into `per_seed[i]["llm_forward_calls_at_inference"]`. Assert = 0 before the metrics.json write; if non-zero, HARD_FAIL with the verdict_msg naming the call-site.
- This makes the substrate-only claim AUDITABLE (Skunkworks's inherited N1 gate). The fresh teammate should NOT skip this; it's a single import-time monkey-patch + an assert.

**4. VQ-floor decomposition** (subtract the by-construction VQ-granularity ceiling):
- The substrate-native LM goes `token → concept_codebook → next_concept → token` (or similar VQ round-trip). The round-trip itself loses information (the VQ codebook is lossy). That loss is the **VQ-floor BPC**: the BPC of a perfect-next-concept-predictor that nonetheless has to round-trip through the same codebook.
- Compute the VQ-floor by:
  1. Round-trip the held-out text: encode tokens → VQ-codebook lookup → decode back to tokens.
  2. Compute the BPC of this round-trip against the original tokens (this is the IRREDUCIBLE loss from the VQ codebook granularity).
  3. Report `vq_floor_bpc` per (seed, lever_config).
- The **load-bearing claim** is `gain_above_vq_floor = substrate_bpc - vq_floor_bpc`. Skunkworks's PASS bar should be on the gain, NOT the raw BPC (raw BPC can "beat baseline" just by inheriting the VQ floor's structural advantage; that's by-construction-saturation).
- If `substrate_bpc ≈ vq_floor_bpc`, the substrate LM isn't doing anything beyond the codebook — it's a saturated result. HARD_FAIL band.

### Cell-design dos and don'ts (from the wikitext2 / phase_d_tier6 / ratio-band lessons)

**DO:**
- `corpus = wikitext2_or_text8_or_shakespeare_char_corpus(allow_synthetic=False)` — fail-loud if real data isn't reachable.
- Use `experiments/_seed_checkpoint.py` for resume; CONFIG_VERSION includes corpus_chars + n_layers + N + lever_config + every BPC-affecting param.
- Vectorize: any `for triple/token: outer(...)` → chunked BLAS matmul. The phase_d_tier6 base used the Python-loop SubstrateCharLM; vectorizing the substrate primitives (where possible) gives 10-100×.
- Reuse `testbed/substrate_lm/{char_lm,baseline_gradient_lm,data,primitives}.py` for the substrate LM + baseline + corpus + char_vocab. Add your N2-lever-sweep wrapper around them.
- Compute real chance/bigram baseline on the SAME held-out (uniform_bpc + a bigram-count BPC); make Skunkworks's absolute-floor band the gate (substrate < bigram - margin), NOT a ratio-to-baseline.

**DON'T:**
- Don't reuse the phase_d_tier6 ratio band (`substrate ≤ 2.0 × baseline`). Gameable — chance substrate passes if baseline is weak.
- Don't pass `allow_synthetic=True` to any corpus loader in a cert run. Silent synthetic fallback = false-green (the wikitext2 / phase05 pattern).
- Don't compute aggregates before writing per_unit. Skunkworks needs the per_unit to recompute.
- Don't skip the LLM-call counter assert. The substrate-only claim is auditable or it's not a cert.
- Don't trust your verdict_msg string. Re-derive from per_seed before reading the verdict aloud.

### Smoke + selftest gates (before any full dispatch)
- Selftest: 1-second mechanism check (the 4-primitive substrate + a tiny synthetic, asserts primitives operational + BPC < uniform).
- Smoke: pythia-160m or shakespeare-snippet, M ≤ 1000 chars per split, 1 seed, 1-2 lever configs, ~30s-3min. MUST: produce valid per_unit; the LLM-call counter must read 0; the VQ-floor decomposition must run end-to-end; cv computation must produce a finite number (even on 1 seed it shouldn't crash). If smoke catches a "substrate at chance on real text at smoke" (the phase_d_tier6 lesson) → that's a smoke-scale artifact, NOT necessarily a fail; the full is the real test. Flag it but don't auto-FAIL.

### Verdict logic template
```python
def verdict(per_seed_by_config):
    pass_configs = []; mb_configs = []; fail_configs = []
    for cfg, units in per_seed_by_config.items():
        bpcs = [u["substrate_bpc"] for u in units]
        gains = [u["gain_above_vq_floor"] for u in units]
        cv = float(np.std(bpcs) / max(np.mean(bpcs), 1e-9))
        zero_llm = all(u["llm_forward_calls_at_inference"] == 0 for u in units)
        gain_mean = float(np.mean(gains))
        # absolute-floor band against real bigram baseline (PRE-REG'd per Skunkworks)
        beats_bigram = (np.mean(bpcs) + ABS_MARGIN) < np.mean([u["bigram_bpc"] for u in units])
        if not zero_llm:
            fail_configs.append((cfg, "LLM_CALL_VIOLATION"))
        elif cv > 0.10:
            fail_configs.append((cfg, f"cv={cv:.3f}>0.10"))
        elif beats_bigram and gain_mean > 0 and cv <= 0.05:
            pass_configs.append((cfg, gain_mean, cv))
        elif beats_bigram or gain_mean > 0:
            mb_configs.append((cfg, gain_mean, cv))
        else:
            fail_configs.append((cfg, f"no-gain bpc={np.mean(bpcs):.3f}"))
    # chain-grade requires >=1 PASS config with cv <= 0.05 + substrate-only verified
    if pass_configs: return ("HARD_PASS", ...)
    if mb_configs: return ("MIDDLE_BAND", ...)
    return ("HARD_FAIL", ...)
```

### Pre-flight before dispatch (verify-the-referent on the cell itself)
1. selftest PASS on local CPU.
2. smoke PASS + the 4 instrumentation hooks visible in smoke metrics (per_unit shape correct; cv computed; LLM-count = 0; VQ-floor present).
3. CONFIG_VERSION text manually-inspected for completeness (every BPC-affecting param appears).
4. Real-data provenance asserted (cache file exists or download URL reachable; no synthetic fallback path triggered in smoke).
5. Commit cell + smoke metrics BEFORE dispatch (pre-reg trail).
6. Route to Orchestrator with the dispatch ask (GPU-or-CPU + ETA + scp request).

### Hand-off pointer to base infra
- Base cell to fork: `experiments/exp_phase_d_tier6_full_pipeline_4_core_char_lm_v1.py` (has the SubstrateCharLM/GradientCharLM driver pattern, per-seed checkpoint, wikitext2 corpus loader).
- Replace: wikitext2_char_corpus → text8/shakespeare_char_corpus with `allow_synthetic=False`; add VQ-floor computation; add LLM-call counter import + assert; add per_unit shape; add real-bigram baseline; replace the ratio band with absolute-floor.
- Don't break `phase_d_tier6` (still imported elsewhere if any cells reference it); fork to a new file.

**This is the cell-design plan. The fresh exp_dev teammate authoring N2 should follow this template + read Skunkworks's per-unit-instrumentation note (the one they flagged as the structural blocker — locate it via `Glob 'notes/skunkworks_*per_unit*'` or `*N2*chain*`).**

---

**End of handoff. Migration-ready. The next exp_dev teammate will spawn fresh with CLAUDE.md + MEMORY.md + this snapshot. Sections 7-9 are the load-bearing additions; sections 1-6 are tactical-continuation.**
