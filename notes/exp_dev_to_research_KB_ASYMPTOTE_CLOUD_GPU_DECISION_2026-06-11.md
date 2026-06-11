# Exp-Dev -> Research: production-scaling asymptote (500K/1M) -- cloud-GPU decision needed

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** PP-225 fact-recall production asymptote; user routing decision

## Status: asymptote DECISIVE through 100K; 500K blocked on local hardware
PP-225 substrate-as-LLM-memory genuine fact-recall, FLAT across scales (no degradation):
| 10K | 25K | 50K | 100K |
|---|---|---|---|
| 0.9945 | 0.996 | 0.994 | **0.997** |

**kb500k FAILED on local hardware**: the desktop GPU is only 8 GiB (shared with ~7 procs, ~3 GiB used). Even after memory
fixes (bge encoder fp16, embeddings streamed to CPU, batch 64->16, expandable_segments), 500K facts + bge-large doesn't fit
the ~5 GiB headroom. This is a HARDWARE constraint, not a substrate limit.

## Decision needed (user routed to you)
User: "route that to research -- if it's important enough we can route it to the cloud GPU."

**Question for Research:** Is nailing the 500K / 1M production asymptote important enough to warrant a cloud GPU (e.g.,
H100/A100, ~$2-10 for the run)?

### Case FOR cloud-GPU 500K/1M
- Closes the production-scale claim definitively at 500K-1M (vs "flat through 100K, extrapolated").
- Strengthens the multi-hop-revive substrate-at-scale / fact-memory commercial claim with a hard 1M number.

### Case AGAINST (accept 100K)
- The curve is already FLAT 0.994-0.997 across 10K->100K (1 order of magnitude); high confidence it stays ~0.995 at 500K-1M.
- Marginal info from 500K/1M is modest (confirms flatness, no new regime expected).
- Cloud-GPU cost + setup + the per-case-justification rule for long cloud runs.

## My read (Exp-Dev)
The asymptote is decisive enough at 100K for the current claim. 500K/1M is a "nice-to-have hard number" rather than a
decision-changer. Recommend cloud-GPU ONLY if the 1M number is needed for a specific customer/commercial claim; otherwise
accept 100K. Your call -- if you say go, I'll build a memory-clean streaming cloud cell (chunked encode, no full-embedding
materialization) and dispatch to a cloud H100 with the usual safety stack.

## Cross-ref
- kb production results: data/exp_t5c_pp225_kb{10k,25k,50k,100k}_genuine_v1/metrics.json
- 8GB-GPU OOM: the local desktop GPU cannot host >100K fact-scaling for this cell.
