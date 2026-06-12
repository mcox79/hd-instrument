# Pre-registration: closed-feature TOPIC cross-domain transfer (AG-News -> 20NG)

**Date:** 2026-06-12 Cycle 50. Cell: exp_substrate_crossdomain_transfer_agnews_20ng_topic_cpu_v1.py. Lane: remote_cpu_queue (DESKTOP; laptop paused). NO LLM frame.
Routing: strategy_request closed-feature topic transfer v591 (2nd closed-feature anchor for the capability-class tail-shape rule).

## Design
Multiclass averaged perceptron (discriminative_perceptron) over hashed word+bigram features. Source: AG-News (news), restricted
to the 3 cleanly-shared classes {World, Sports, Sci/Tech} (Business dropped -- 20NG has no Business topic). Target: 20NG
(SetFit/20_newsgroups parquet via datasets lib; 20 groups mapped onto the 3 classes; news ARTICLES -> forum POSTS domain shift).
Warm-start transfer (init target weights from AG-News weights) vs scratch, at target fractions {1,2.5,5,10,100}pct, 3 seeds.
Macro-F1.

## Pre-reg (v591; transfer/scratch ratio)
- HARD-PASS: ratio@2.5pct >= 1.20 (low-data lift) AND ratio@100pct in [0.95,1.10] (CONVERGES -- confirms closed-feature class).
- MIDDLE: ratio@2.5pct >= 1.20 but ratio@100pct > 1.10 (non-converging tail -> closed-feature converging prediction NOT cleanly
  confirmed; rule may need refinement: vocab-size vs open/closed).
- HARD-FAIL: ratio@2.5pct < 1.20 (no low-data transfer). UNKNOWN if 20NG unavailable.

## Why
CONFIRMING-vs-FALSIFYING 2nd closed-feature anchor (topic, non-sentiment) for the capability-class tail-shape rule (1st anchor
PP-409 sentiment converged). Smoke: zero-shot AG-on-20NG macro-F1=0.344; ratio@2.5pct=1.82.
