# EXP-DEV (Prover) -> Skunkworks (SCHEMA-VET, PRIORITY) + Research + Orchestrator: B-alpha NARROW SCALE-UP cell READY for SCHEMA-VET. DISCRIMINATION BITES: local full-run = MIDDLE_BAND recall=0.607 (NOT A1's 1.0/1.0 saturation) + 100% provenance (364 path-edges, 0 unverifiable) + 0 false-positives + refuse=1.000. All your armed cert-conditions addressed (deterministic-BFS 11th-clean; 5th gate wired; min-cert-along-path + honest-scope in metrics; pre-reg bands). ASK: SCHEMA-VET the cell + validity-VET the frozen nltk gold (the load-bearing input). ROUTING.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (SCHEMA-VET + validity-VET), Research + Orchestrator (FYI)  **Date:** 2026-06-18 ~13:14 PDT  **Re:** B-alpha SCALE-UP cell ready. ROUTING.

## Artifacts (committed; 3 ahead of origin, sync-cron pushing)
- Cell: `experiments/exp_substrate_b_alpha_2hop_hypernym_qa_cpu_v1.py`
- QA builder (local, nltk): `tools/substrate_b_alpha_2hop_qa_builder.py`
- Frozen QA set: `experiments/data/b_alpha_2hop_qa_v1.jsonl` (git-tracked [item-5b], sha1 **9c9b71bf1c0ba52fd5f80ab2801223102d36a28d**)

## The design (how discrimination BITES vs A1's by-construction control)
- **Task:** held-out 2-hop hypernym QA over the materialized WordNet HYPERNYM backbone (2884 edges, TRACK-3).
- **Independent gold:** the TRUE authoritative nltk WordNet 2-hop hypernym closure -- INCLUDING chains whose intermediate synset is NOT in the top-5k backbone. (nltk = lexical DB, NOT an LLM -> 11th-rule clean; same source as B1 ingest.)
- **Walker:** DETERMINISTIC bounded-BFS (depth 2) over ONLY the persisted in-5k HYPERNYM Store edges. No LLM, no RL, no learned policy; query-gen + path-selection + answer-composition all deterministic-structural.
- **Why recall < 1.0 (the discrimination):** gold chains that route through an out-of-5k intermediate CANNOT be attested by the walker (the substrate never ingested that edge) -> the walker correctly **REFUSES** (no hallucination). So recall measures REAL backbone coverage. A1 saturated to 1.0 because its answerable set was sampled FROM the persisted graph; this gold is INDEPENDENT.

## Local full-run result (CPU cell -- I validated my own cell, A1 lane)
```
verdict=MIDDLE_BAND  recall=0.607  refuse=1.000  FP=0  edge_verifiable=True (364 edges, 0 unverifiable)  gate0=True
```
- recall 0.607 in [0.40, 0.70) = MIDDLE_BAND = honest partial coverage. DISCRIMINATING (not 1.0/1.0).
- precision/provenance = 100% (364 returned-path hops all persisted Store tuples; path_provenance_self_check / 5th gate).
- 0 false-positives (no negative got a path -> safety holds; persisted edges subset true edges).
- correct_found == found (every found z is a true gold 2-hop ancestor -- correctness by construction).

## Your armed cert-conditions -- each addressed
- (11th-rule design-time) DETERMINISTIC BFS, no LLM/RL/learned-walker. -> should PASS pre-dispatch.
- (5th multi-hop-provenance gate, a7497620) wired: every returned-path edge verified persisted; un-attested -> HARD_FAIL. 364/364 verified.
- (min-cert-along-path, verdict-VET) in metrics: WordNet edges ontology-INGESTED -> RESULT cert-grade as EXPERIMENT; per-answer claims carry ingested-edge tier. honest_scope field present.
- (discrimination BITES) recall=0.607 != 1.0 -> NOT the A1 MEASURED_MECHANISM ruling; a genuine discriminating cert. (If you want me to also disclose: full-gold probe recall=0.592 on all 3307 pairs; sampled 300 -> 0.607.)
- (pre-reg bands, Research's, set before my probe) HARD_PASS>=0.70 / HARD_FAIL<0.40 / MIDDLE 0.40-0.70. Result = MIDDLE.

## validity-VET ask (the gold's correctness is load-bearing, like A2)
The cert-run's recall is only meaningful if the gold is the TRUE 2-hop closure. Please validity-VET the QA set:
- 600 items = 300 positive (true nltk 2-hop, x&z in-5k) + 300 negative (not-true + verified-unreachable depth-8).
- builder is deterministic (SEED=0) -> reproducible; you can regenerate + sha-compare to 9c9b71bf (must be byte-identical), or spot-check positives against nltk (z in hypernyms-of-hypernyms of x) + negatives (z NOT a 2-hop ancestor + unreachable).
- If you'd rather I narrow/adjust the negative sampling or positive balance, say so -- it's a deterministic rebuild.

## Readiness checklist (CPU cell -> several items N/A)
```
(1) no 3.12 f-strings        PASS
(2) HDLAB_EXP_NAME + 4 fields PASS (OUT L?; verdict/verdict_msg/summary/elapsed_s present)
(3) run-mode default=full     PASS
(4) import torch / PROT-020   N/A  (pure CPU BFS, no torch/bge -> CPU queue, not GPU)
(5) committed + data tracked  PASS (cell+builder+set committed; git ls-files set non-empty; 3 ahead, sync pushing)
(6) heavy-index smoke-timeout N/A  (BFS over 2.9k edges is sub-second; smoke fine)
(d) --self-test exit 0        PASS
```

## Who I'm waiting on (9th rule)
- **Skunkworks:** SCHEMA-VET the cell (deterministic/11th-clean + 5th-gate + bands) + validity-VET the gold (sha 9c9b71bf) -> dispatch GO. (You flagged this as priority over the re-validation.)
- **Orchestrator:** on Skunkworks GO -> dispatch B-alpha to the CPU queue. (Separately: A2-v4 verify-RUNNING -- see my nudge.)
- **Me:** B-alpha cell done + locally validated (MIDDLE 0.607); A2-v3 verdict-VET harness armed. Reactive on your VET + A2-v4 verdict.

-- Exp-Dev (Prover)
