# Testbed -> Research: CLOUD-1 in-flight + mean-pool retrieval bug diagnosed via Pythia-160M

**From:** Testbed
**To:** Research (evaluation + next steps)
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-06 ~13:30
**Re:** `research_to_testbed_cloud_experiments_list_when_authorized_2026-06-06` (CLOUD-1: 8B vs 70B substrate-extraction quality binding test)

---

## TL;DR

CLOUD-1 dispatched + acquired GH200 in us-east-3 ($2.29/h, ~96GB unified mem). 8B run completed with retrieval acc = 0.000 (alarming). User asked for diagnostic on smaller model -- I ran the SAME pipeline on Pythia-160M locally on the runner's 4060 Ti. Result: **mean-pool is the bug**. Last-token-pool pipeline gives top-5 = 0.130 on Pythia-160M; mean-pool gives 0.000. CLOUD-1's binding test ratio will be uninformative as designed. Need design decision before CLOUD-1b.

---

## CLOUD-1 progress timeline

| Time UTC | Event |
|---|---|
| 12:34 | First sky launch attempt: stuck on us-east-1 PCIe (Lambda H100 inventory zero) |
| 12:51 | Switched to GH200 (Lambda API showed availability); first attempt failed at setup 3/8 (`ModuleNotFoundError: No module named 'torch'` -- GH200 image does NOT have torch pre-installed) |
| 13:01 | Patched cloud_1_gh200.yaml: install torch via cu124 aarch64 wheel index (works for Linux aarch64+CUDA, unlike cu121 which is x86-only). Smart launcher relaunched |
| 13:07 | Cluster `cloud1quality-090134` provisioned on GH200 us-east-3 |
| 13:08 | Setup 1-7 PASS. 70B snapshot downloaded in 1m 18s (Lambda network excellent) |
| 13:09 | Setup 8 PROT-022 self-test PASS. Run begins |
| 13:10 | 8B fp16 load (34.6s, 16 GB peak) |
| 13:11 | **8B retrieval: top-1=0.000, top-5=0.000** -- alarming |
| 13:12 | 70B 4-bit load (291s, 39.57 GB peak; fits GH200's 96 GB comfortably) |
| 13:14+ | 70B extraction in progress (~5-8 min) |

Cost so far: ~$0.50 (~$0.25 failed bootstraps + ~$0.25 actual run). GH200 will tear down after final rsync.

---

## Diagnostic: Pythia-160M local (4060 Ti, ~3 min wall, $0)

I ran the SAME pipeline used in CLOUD-1 (load_squad_v2_dev + mean-pool layer-6 hidden_states + random-projection seed=1729 + cosine top-K) on **EleutherAI/pythia-160m** locally. Added diagnostics: per-query gold-passage rank stats + last-token pool baseline + raw-hidden-state cosine baseline + gold-index concentration.

### Result

```
[data] 1000 passages + 100 questions loaded
[diag] gold_indices: 41 unique passages out of 1000
[diag] gold_indices min=0 max=40 first10=[0, 0, 0, 0, 0, 1, 1, 1, 2, 2]
[load] EleutherAI/pythia-160m  done in 4.0s
[extract] passages done in 7.7s
[diag] passage mean-pool norm: median=15.25 min=10.72 max=30.51
[diag] query   mean-pool norm: median=39.71 min=23.35 max=67.96
```

| Variant | top-1 | top-5 | median rank | n_in_top_50 | n_in_top_100 |
|---|---|---|---|---|---|
| **MEAN-POOL + RP** (CLOUD-1's pipeline) | **0.000** | **0.000** | **237** | 28 | 30 |
| **LAST-TOKEN pool + RP** | 0.020 | **0.130** | **80** | 41 | 53 |
| MEAN-POOL + no RP (raw cosine) | 0.000 | 0.000 | 243 | 28 | 32 |

**Verdict from script:** "LAST-TOKEN pool dominates -- mean-pool is the bug in CLOUD-1."

### What this tells us

1. **Random projection is NOT the bug.** Removing RP gives same 0.000 on mean-pool. The information loss is upstream of RP.

2. **Mean-pool over causal-LM hidden states destroys retrieval signal.** Causal LMs concentrate semantic compression at the LAST token (it has attended to everything). Averaging across all tokens dilutes this. The query/passage embeddings end up structurally similar regardless of content.

3. **Mean-pool norm asymmetry is a fingerprint.** Passage mean-pool norms median=15.25; query mean-pool norms median=39.71. Queries are 2.6x larger magnitude. After F.normalize this collapses to unit vectors but the underlying DIRECTIONS were never aligned between long-passages and short-queries.

4. **Gold-index concentration is real but secondary.** Only 41 unique passages out of 1000 receive gold-pointing queries (first 100 answerable questions in SQuAD-v2 dev order cover ~41 contexts). But even with this concentration, last-token-pool gets 13% top-5 -- which means the concentration isn't the dominant problem; mean-pool is.

### Predicted CLOUD-1 outcome

If 70B finishes (in flight; will land in ~5 min):
- 70B mean-pool retrieval will ALSO be ~0.000 (same bug applies)
- Ratio = 0/0 -- undefined, uninformative
- CLOUD-1's binding-test question NOT answered by this run

The cloud spend was $0.50; the GH200+aarch64 cu124 pipeline is now proven (a valuable infra result), and the bug is now identified. But the SCIENTIFIC question CLOUD-1 asked is not answered.

---

## Audit done on CLOUD-1 script (pre-diagnostic)

Code review found no obvious math bugs:
- `load_squad_v2_dev`: gold_indices correctly map question -> passage index
- `mean_pool`: padding correctly masked (self-test passes on toy input)
- `random_projection_matrix`: deterministic JL projection (P/sqrt(out_dim) scaling)
- `top_k_retrieval_acc`: torch.topk gives largest by default, cosine math is right (self-test with identity corpus gives 1.0)

**The bug was in the DESIGN choice (mean-pool for causal LM), not the implementation.**

---

## Proposed CLOUD-1b design

Same cloud config (GH200 if available; aarch64 cu124 path proven); replace pipeline with:

1. **Last-token pool** (causal-LM-appropriate; last hidden state has attended to everything)
2. **Per-query gold-passage rank emitted** as a diagnostic (median, p25, p75, p95)
3. **MiniLM-L6-v2 baseline added** as upper-bound calibrator (sentence-transformer should give 60-80% top-5 -- proves task is doable)
4. **Spread gold_indices across the full corpus** by shuffling the 1000 passages (avoid the first-15-context concentration artifact)
5. **Llama-3.2-1B added as third model** (smaller anchor) -- already gated-license-accepted; weights need ~5 min download

Expected wall: ~25-30 min on GH200. Cost: ~$1.15.

OR (cheaper if you want fast confirmation): just rerun with last-token-pool + MiniLM baseline. ~20 min, ~$0.80.

---

## Three options for next steps (Research call)

### A. Kill CLOUD-1 now, save $0.15

70B is in flight; will likely yield 0.000 (same mean-pool bug). Could `sky cancel` immediately and save the rest of the H100-equivalent compute. Then file CLOUD-1b proposal.

### B. Let CLOUD-1 finish for confirmation

Lets us VERIFY 70B mean-pool = 0.000 (which would empirically confirm the diagnostic conclusion at scale). Costs ~$0.15 more. Strengthens the negative-result evidence.

### C. CLOUD-1b proposal evaluation

Whichever path on (A/B), Research evaluates the CLOUD-1b proposal above:
- Is last-token-pool + MiniLM baseline + per-query rank the right fix?
- Should we add Llama-3.2-1B as the third model? (matches Tier-4 family)
- Should we shuffle the 1000 passages to spread gold_indices?
- Is the binding-test threshold (8B / 70B >= 0.80 = HP) still the right shape?

---

## What the GH200 + aarch64 infra success means (independent of bug)

The CLOUD-1 dispatch + GH200 +aarch64+cu124 path is now PROVEN end-to-end:
- Lambda GH200 image doesn't have torch pre-installed -- BUT cu124 aarch64 wheels exist and install cleanly
- bitsandbytes 4-bit NF4 works on GH200 (39.57 GB peak for 70B 4-bit; comfortable in 96 GB)
- Setup-step time: ~3-4 min after Ray ready
- 70B safetensors download from HF on Lambda's network: 1m 18s (~10x faster than I estimated)
- Total per-run cost ~$0.50 for the 8B+70B+setup work

This unblocks GH200 as a CLOUD-1b option AND future Phase 4a work where >40 GB VRAM is needed.

---

## What I did NOT do

- Did NOT kill the cloud run (waiting on your call on Option A vs B)
- Did NOT push the local diagnostic script to git (it's `experiments/tmp_pythia_retrieval_diag.py` -- happy to clean up + commit if you want it preserved for the audit trail)
- Did NOT propose CLOUD-1b dispatch yet (waiting on your evaluation)
- Did NOT pivot to Llama-3.2-1B local run (Pythia diagnostic was sufficient to identify the bug)

---

**END.**

**Research:** Mean-pool is the cause of CLOUD-1's 0.000. Pythia diagnostic on the runner: last-token pool gives top-5=0.130, mean-pool gives 0.000, raw-cosine (no RP) gives 0.000. Random projection is innocent. Proposed CLOUD-1b: last-token-pool + MiniLM baseline + per-query rank + spread gold_indices. Awaiting your evaluation + decision on (A) kill running CLOUD-1 / (B) let it finish for negative-confirmation / (C) green-light CLOUD-1b.

**Exp-Dev:** infra learning: GH200 + aarch64 + cu124 torch wheels works end-to-end. Lambda's GH200 image lacks pre-installed torch (counterintuitive); fix is in cloud_1_gh200.yaml setup step 3. Useful for future Phase 4a work.

**User:** Bug isolated. Mean-pool over causal-LM hidden states gives 0 retrieval because last token is where the semantic summary lives. Pythia diagnostic confirmed in ~3 min on runner. CLOUD-1 cost ~$0.50 so far; will reach ~$0.65 if we let 70B finish. Awaiting your call on next step. CLOUD-1b is cleanly scoped and ready to go when authorized.
