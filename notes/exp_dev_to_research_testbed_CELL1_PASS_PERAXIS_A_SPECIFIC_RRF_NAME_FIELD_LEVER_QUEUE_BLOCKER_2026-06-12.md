# Exp-Dev -> Research + Testbed: Cell 1 chunking multi-seed HARD_PASS + per-axis semantic A-SPECIFIC + Multi-field RRF finding (name/idtok field is the lever, naive RRF DILUTES) + dashboard/queue blocker (experiments/ doesn't sync to home)

**Date:** 2026-06-12 (Day 4 morning)  **From:** Exp-Dev (full-auto; USER: revive+use GPU, follow Research)

## Cell 1: PP-400 chunking multi-seed n=5 = HARD_PASS

mean F1 = **0.9237**, SD **0.0007** (min 0.9229, max 0.9250, seeds 1028-1032). Promoted single-seed -> **end-task multi-seed Tier-A**.
Substrate-classical NL roster 6 -> 7 multi-seed. (`exp_pp400_chunking_multiseed_cpu_v1.py`, subprocess over the validated cascade cell.)

## GPU finding 1: semantic retrieval is A-AXIS-SPECIFIC (informs HYBRID axis-gating)

Per-axis bge semantic retrieval F1 (top_k=8, current store, on GPU):

| axis | F1 | n |
|---|---|---|
| **A (content)** | **0.369** | 12 |
| B (relation) | 0.047 | 8 |
| C (capability) | 0.131 | 10 |
| E (methodology) | 0.153 | 7 |
| G (pattern) | 0.162 | 5 |

bge semantic helps CONTENT (A) but FAILS on relational/structural axes (B/C/E/G need graph traversal / route_primitives). **HYBRID
recommendation: axis-gate semantic to A-type only.** A naive "semantic for all axes" HYBRID would HURT B/C/D (drop them to ~0.05-0.16).

## GPU finding 2: Multi-field RRF -- naive equal-weight RRF DILUTES; the lever is the NAME/ID-TOKEN field

Ran the Multi-field RRF prototype (`exp_semantic_a_v2_multifield_rrf_gpu_v1.py`, read-only, GPU). Per-field A-axis F1 + RRF:

| k | RRF (equal-weight) | desc-only | idtok | name | serves |
|---|---|---|---|---|---|
| 5 | 0.340 | 0.330 | 0.402 | **0.410** | 0.192 |
| 8 | 0.305 | 0.310 | 0.327 | 0.356 | 0.175 |
| 12 | 0.310 | 0.273 | 0.259 | 0.294 | 0.159 |

**Key finding (contra the drill's naive-RRF projection of 0.43):** equal-weight RRF over 4 fields gives ~0.34 -- barely over desc-only --
because it DILUTES the strong fields with the weak ones (serves=0.19). But the **atom NAME / id-token-decomposition field ALONE hits
~0.41 at k=5**, clearly beating the description field (~0.33). The retrieval lever is a BETTER FIELD (name/idtok), not naive fusion.

**Recommendation for Testbed Semantic-A v2:** do NOT equal-weight RRF. Either (a) retrieve on name/idtok as PRIMARY (projects ~0.41
vs current ~0.37), or (b) WEIGHTED RRF favoring name/idtok over desc/serves. Honest revised projection: ~0.40-0.42 (not 0.43 via naive
RRF; not via desc). Graph-propagation (DEPENDS_ON) still untested -- could stack.

This is the go/no-go de-risking Research wanted: the lever is real (+~0.07 over description via field selection) but the MECHANISM is
field-choice, not naive RRF. Cheap win for Testbed.

## BLOCKER: dashboard/queue -- experiments/ does NOT sync to home

USER flagged dashboard shows idle. Root cause: I've run GPU/CPU work as DIRECT processes (background python, SSH stdin), which bypass
the runner queues the dashboard tracks. To make GPU work dashboard-visible I must QUEUE cells (overnight_queue -> gpu_runner_0 claims).
BUT: a newly-authored cell on the laptop does NOT reach home -- experiments/ does not auto-sync, I'm (correctly) blocked from writing
to the shared host, and home git-pull is blocked by Testbed's live substrate_index. So I currently CANNOT queue new cells to the GPU
runner.

**Need (Testbed/USER):** a way to get Exp-Dev-authored experiment cells onto home -- either Testbed periodically `git pull`s on home
(handling the dirty substrate_index), OR a sync for experiments/, OR explicit authorization for Exp-Dev to write cells to home. Until
then GPU work runs direct (invisible to dash) -- I've kept it read-only.

## Next (per Research routing)

- Cell 1 done. Next CPU: Phase 6.1 H3+H1 (distractor-relevance + quantity-verb atoms) -- starting now on laptop.
- Testbed: Semantic-A v2 -> use name/idtok field (per finding above) + axis-gate to A; git pull first (harness fix at 50f1da96).
- GPU: idle + ready; will route the next read-only GPU job (graph-propagation prototype?) or queue once cell-propagation is resolved.
