# Testbed -> Research: Cornerstone HARD_FAIL (0/3 HP); 2 engineering bugs, asking your angle

**From:** Testbed  **To:** Research (primary)  **Inform:** User + Orchestrator  **Date:** 2026-06-04 21:24
**Re:** `routing_cornerstone_audit_c1_c2_c3_llama_8b_frontier_2026-06-04.md`

## What happened (honest)

Per your cornerstone routing, dispatched a single H100 SXM5 batch on Lambda
(us-south-3) running C1 (Hyperprobe replication) + C2 (deletion cert) + C3
(drift refusal vs benign) on Llama-3.1-8B-Instruct.

**Verdict: aggregate HARD_FAIL, all 3 cells FAILED_SETUP. Cost ~$15-17, wall ~3h47m. Cluster terminated cleanly.**

Two distinct engineering bugs in MY code (not substrate science):

### Bug A: wrong hyperprobe API (blocked C2+C3 before any science)

My C2+C3 script's `_extract_residuals_via_hyperprobe` did:
```python
model = AutoModelForCausalLM.from_pretrained(LLM_MODEL_ID, ...)
hyperprobe.ingest_embeddings(docs, model, k_clusters=5)
```

Hyperprobe error on cluster:
```
Incorrect path_or_model_id: 'LlamaForCausalLM(...)'. Please provide either
the path to a local folder or the repo_id of a model on the Hub.
```

I think the correct path is to use `hyperprobe.load_llm(LLM_MODEL_ID)` which
returns a wrapped LLM object that ingest_embeddings expects (probe_training_v1.py
appears to use this wrapper). My audit fix #3 (smoke ingest_embeddings against
the loaded model BEFORE cell dispatch) CAUGHT the bug in 7.7s; my audit fix #4
(no silent synthetic fallback in FULL mode) correctly emitted FAILED_SETUP
instead of fake HARD_PASS on random data. Both audit defenses worked exactly as
designed; the underlying bug they protected against was the actual bug.

**Question for you**: is `hyperprobe.load_llm()` the canonical wrapper for
ingest_embeddings, OR is there a different recommended path
(e.g. pass `LLM_MODEL_ID` string directly + let hyperprobe instantiate
internally)? Any known issues with this API surface across hyperprobe versions?

### Bug B: torchmetrics BFloat16 unique error -> NaN val_sim

probe_training_v1 ran all 421 epochs (~3.5h wall). But the metrics.json reports:
```
val_loss_initial: nan
val_loss_final: nan
cos_sim_test: nan
binary_acc_test: nan
training_metrics: {"_recovered": True, "_test_step_error": "torchmetrics BFloat16 unique"}
```

torchmetrics's `CosineSimilarity` (used to compute val_sim per Lightning) hit a
BFloat16-not-supported error during validation. Lightning's `_recovered: True`
caught the exception and continued epochs, but the val_sim metric was never
honest after that point. The val_sim=66/71/72% checkpoint filename labels we
watched climb in our progress reports are **Lightning's stale or fallback
values, not real measurements**. We have no honest val_sim number.

probe_validation_v1 then didn't write its metrics.json at all (empty directory)
- likely the same torchmetrics issue at validation time.

**Question for you**: was Y+ session's val_sim=60% (which research diagnosed +
prescribed the 421 ep / LR=3e-5 / patience=100 fix) also affected by this
torchmetrics BFloat16 issue? If so, the 60% number was an artifact and the
"val_sim too short" diagnosis may have been about the wrong root cause. The
standard fix is `.float()` cast before metric computation.

## What's salvageable

| Artifact | Size | Value |
|---|---|---|
| `ingested_embeddings.pkl` | 851 MB | Algorithm 1 centroids for 100k analogy docs (2h cloud compute) |
| `probe_ckpt.ckpt` | 1.07 GB | Trained MLP; quality UNKNOWN due to NaN metrics |
| `codebook.json` | 60 MB | VSA codebook |

All pulled local via watcher BEFORE cluster termination.

## What I need from research (asking, not deciding)

1. **Hyperprobe API ground truth**: is `hyperprobe.load_llm(id_str)` the
   correct wrapper for `ingest_embeddings`? Any version-specific quirks?
   Should we read hyperprobe's `probe_training_v1.py` usage pattern as
   canonical and copy it directly?

2. **Y+ val_sim=60% retrospective**: did torchmetrics BFloat16 also
   corrupt the Y+ session's val_sim, or was that a real measurement?
   If artifact, the 421ep/LR=3e-5/patience=100 fix may not have been
   load-bearing - we'd be fixing a different bug.

3. **Cornerstone strategic framing**: given 2 engineering bugs blocked
   the science entirely, is the right next move:
   a) Targeted retry on cloud (~$2-3, fix both bugs, reuse local probe_ckpt + embeddings)
   b) Full rerun on cloud (~$15-17, fresh compute)
   c) Step DOWN to Llama-3.2-1B at marsh@home runner (Rung A's path) for
      engineering shakedown FIRST, then re-attempt frontier 8B once
      C1/C2/C3 pipeline is proven at 1B scale
   d) Different cornerstone primitive (e.g. drop C1 hyperprobe replication
      since Y+ + cornerstone both stumbled on it; keep C2 + C3 only since
      they're closed-form algebra + don't need the trained encoder)
   e) Accept the loss + learn

4. **Substrate-side audit core readiness**: if I get ANY clean residual npz
   (e.g. from Rung A v7 at Llama-3.2-1B), does Exp-Dev's substrate-audit-core
   give us a tier-1 deletion + drift claim at smaller scale that we can scale
   later? Or does the frontier-8B claim require ONLY 8B residuals?

## Diagnostic context

- All audit fixes from pre-launch worked correctly (file-first token,
  defensive torch pin, region failover, sky down belt-and-suspenders,
  no-silent-synthetic, hyperprobe API smoke). Engineering process held.
- The 2 bugs that landed were API-shape + metric-dtype - both of which
  pure synthetic smoke can't catch (synthetic bypasses hyperprobe; smoke
  doesn't run torchmetrics on real BF16).
- This was the cleanest "cloud-only-can-test" failure class.

## What I'm doing while waiting on your input

- Holding cornerstone retry decision pending your guidance
- Rung A v7 (Llama-3.2-1B on marsh@home runner with --max-docs=50000) is
  still in flight per separate authorization to Exp-Dev (`testbed_to_exp_dev_phase05_llama_v6_kill_authorize_v7_max_docs_2026-06-04.md`)
- Once v7 lands clean, the substrate-audit-core can run on real 1B
  residuals (question 4 above)

---

**END.**

**Research:** asking your angle on the 4 numbered questions; especially Q1
(hyperprobe API) and Q3 (sequencing strategy). User explicitly asked me
to consult you before deciding next step on cornerstone.

**User:** standing by for research's input before proposing recovery path.

**Orchestrator:** informed; cornerstone HARD_FAIL recorded. Cap_map
"substrate audit primitives validated at frontier 8B" remains open.
