# Pre-registration: caching_lfu_lru_arc_tier0_unified_n8192_v1

DATE: 2026-06-02
QUEUE: remote_cpu_queue
ANCHOR: caching_lfu_lru_arc_tier0_unified_n8192_v1

## Scientific question
Does the substrate eigenvalue score (xi^T W xi / N) natively reflect LFU, LRU, and ARC
caching policies at production scale N=8192?

## Hard-pass (pre-registered)
HP-LFU: Spearman rho(substrate_score, access_freq) >= 0.60
HP-LRU: Spearman rho(substrate_score, access_recency) >= 0.60
HP-ARC: Spearman rho(substrate_score, arc_hybrid_score) >= 0.60

## Hard-fail (pre-registered)
HF: any rho < 0 (anti-correlated)

## Middle band
2/3 policies pass

## Smoke result
MIDDLE_BAND: 2/3 policies pass (LFU and ARC pass; LRU fails).
rho_lfu=0.974(pass), rho_lru=0.491(fail, genuinely < 0.60), rho_arc=0.850(pass).
LRU failure is a scientific finding: eigenvalue score tracks frequency/importance not pure
recency. Not a scale issue. Walk-back gate: LRU result is stable and informative.

## Production config
N=8192, M_PATTERNS=200, MAX_WRITES=800, SEEDS=[7,17,23,31,41]

## Timeout estimate
~615s (1.5 * 82s_per_seed * 5_seeds / 2_smoke_seeds; no N change)
Budget: 1800s to be conservative.

## PROT-018
_N_SUFFIX = 8192; N = 8192; assert enforced at module scope.
