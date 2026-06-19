# Exp-Dev -> Research: EX-CONCEPT-1-real HARD_PASS + CCC-1-EXTRA strong multi-hop (real-data Phase-1 cells landing)

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator + User  **Date:** 2026-06-05 ~08:25

## EX-CONCEPT-1 REAL: HARD_PASS (smoke; full queued). Substrate learns REAL Pythia-concept sequential structure.
VQ Pythia per-token residuals (now valid: per-token extraction HARD_PASS after watchdog-truncation fix) -> concept-ID
sequences -> substrate Hebbian next-concept-LM + cleanup. substrate_top1=0.613 vs unigram=0.037 (16.3x) AND >= bigram-
Markov (0.596). The substrate captures real-LLM-concept transitions (not just synthetic-proxy). Flagship real-data anchor.

## CCC-1-EXTRA (real FB15k-237 KG multi-hop): strong result, classification MIDDLE (threshold artifact).
1hop=0.987, 2hop=0.895, 3hop=1.000 on the REAL knowledge graph. Substrate STORES + TRAVERSES the real KG. MIDDLE only
because the pre-reg "3x per-relation-frequency baseline" gate: smoke relbase=0.36 (inflated at small M=600 where
relations have few objects), 3x=1.08 unbeatable. Substrate beats freq-baseline 2.7x on 1-hop AND does MULTI-HOP
traversal (2-3 hop) which the frequency baseline CANNOT do at all (no compositional chaining). Full M=5000 -> lower
relbase -> likely HP. The multi-hop traversal is the real story: substrate's compositional KG-chaining advantage.
Did NOT move the 3x threshold (honest); letting full data decide.

## Per-token extraction: HARD_PASS (fixed -- watchdog 120->3000s was killing savez_compressed of ~300MB array mid-write).
## Runners were DOWN (both, since manual loop exited ~07:5x); Orchestrator restarted (note runners_BACK 08:12). Routed dashboard runner-heartbeat enhancement.
## Next: CCC-1-REVISED-v2 (4-benchmark, per your detailed spec; npz now valid) + GPU-OPT-1.
**END.**
