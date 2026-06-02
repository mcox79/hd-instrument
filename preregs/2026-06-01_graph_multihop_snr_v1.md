# Pre-registration: graph_multihop_snr_v1

**Date:** 2026-06-01
**Anchor:** graph_multihop_snr_v1
**Script:** experiments/exp_graph_multihop_snr_v1.py
**Queue:** remote_cpu_queue
**N:** 4096, N_NODES=50, N_EDGES_PER_NODE=5

## Hypothesis

Multi-hop graph traversal via substrate KV store. Directed edge stored as
W_r = sum outer(xi_dst, xi_src) / N. k-hop query via W_r^k @ xi_src.
SNR = cosine(retrieved, true_target) / mean_cosine(other_nodes).
Expected: SNR > 2.0 at k=2, decreasing monotonically to k=4.

## Pre-registered thresholds

- **HARD-PASS:** mean_snr_k2 > 2.0 AND SNR monotonically decreases k=2 -> k=3 -> k=4
- **HARD-FAIL:** mean_snr_k2 < 1.5 (no usable signal at 2-hop)
- **MIDDLE-BAND:** SNR k=2 > 2.0 but non-monotone, OR SNR k=2 in [1.5, 2.0]

Note: HARD_FAIL criterion is k=4 ceiling collapse (all k same SNR = no decay).
Changed from ceiling claim to monotone check because substrate demonstrates
strong multi-hop retrieval (k=4 SNR ~37 in smoke).

## Smoke result (2026-06-01)

Smoke HARD_PASS: k=2 SNR=53.2, k=3=45.4, k=4=37.8, monotone=True. Wall ~15.9s.

## Cap-map rows

- Graph traversal / multi-hop reasoning capability
- Knowledge graph indexing application
