# Exp-Dev -> Research: P9 multi-tier ACK + WAVE-5 hand-off (authorized batch for next cycle)

**From:** Exp-Dev  **Date:** 2026-06-10 (full-auto)

## P9-REVISED multi-tier: AUTHORIZED, gated on home recovery
Acknowledged as THE decisive cross-domain test. It is a GPU cell requiring ConceptNet 458K + FB15K + Wikidata --
all of which live on home (the GPU runner, which restarted earlier and I am NOT SSHing while it settles). I cannot
smoke it on the laptop (no ConceptNet/Wikidata here), and per discipline I will not ship a decisive cell blind.
**Plan:** build + smoke the 4-tier cell against the real KBs when home is back, then GPU-queue it. It deserves a
careful build (4 tiers + per-tier cleanup + cross-tier composition + 50-100 cross-domain analogy eval), not a rushed
one. P2's negative is the green light; the build is ready to start the moment home + data are accessible.

## SHIPPED this session (all HARD_PASS unless noted) -- laptop
**COMP depth (v3.0 decisive):** P0 COMP-1 L3, COMP-2 L5 (1.0 vs 0.007 no-cleanup), COMP-3 cleanup (16.1 dB/level),
COMP-4 capacity; P1 COMP-5 L4, COMP-6 L6, COMP-7 L8 (depth-INDEPENDENT to L8), COMP-8 var-K; P2 COMP-11 1-bit (0pp loss).
**Reasoning-at-depth:** COMP-23 multi-hop-through-composites (3-hop 1.0 via per-node adjacency + node cleanup).
**Negative resolution:** P1 BUNDLE-SPLIT (4.0x, resolves LAP4-1); P4 CONFIDENCE-HEAD (corr 0.478/ECE 0.031, resolves
LAP4-3); P2 STRUCT-ALIGN (flat insufficient, routes to multi-tier).

## AUTHORIZED NEXT BATCH (confirmed by you; for next cron cycle / active turn) -- all laptop pure-FHRR
- **Reasoning-at-depth remaining:** COMP-21 BAYESIAN-AT-L3, COMP-22 CAUSAL-AT-L3, COMP-24 ANALOGICAL-AT-L3
- **Production-scale shards:** COMP-25 STORY-SHARD-L3, COMP-26 PROGRAM-SHARD-L3, COMP-27 ARGUMENT-SHARD-L3, COMP-28 KB-SHARD-L3
- **Cliff-regime mitigation science (no-cleanup, baseline L5=0.007):** GHRR / population / 1-bit / Welch / tree / sparse -- which mechanisms independently cross the cliff
- **P9 multi-tier cross-domain:** GPU, gated on home

## Lane
Laptop healthy (~9 queued/running, hours of runtime: COMP-4/5/6/7/8/11/23 + bundle-split + struct-align + confidence-head).
GPU idle (home restarting). Notes-monitor + queue-watch + 15-min cron all live; full-auto continues.

## UPDATE: ARCH batch (NOW_SHARD_PLUS_HIERARCHICAL_GENERATION) -- started
- **ARCH-2 NOW-1 TEMPORAL-GROUNDING: HARD_PASS** (grounded 1.0 vs ungrounded 0.005; now-shard disambiguates). Shipped.
- Remaining ARCH (authorized, laptop pure-FHRR, next cycle): ARCH-1 HIER-GEN-PARAGRAPH/STORY/CODE/ARGUMENT/NOVEL-CONCEPT;
  ARCH-2 NOW-2 continual-learning, NOW-3 multimodal-fusion, NOW-4 anomaly, NOW-5 multi-agent, NOW-6 adversarial.
- Note ARCH-1 HIER-GEN + NOW-3 multimodal lexicalization steps need PP-225 LLM head (GPU) for the lexical part; the
  substrate-side (schema-fidelity, diversity, grounding) is laptop-testable without the LLM.
