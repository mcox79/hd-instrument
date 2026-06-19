# Exp-Dev -> Research: closed-feature TOPIC transfer (AG-News->20NG) HARD_PASS -- CONVERGES at 100pct; 2nd closed-feature anchor CONFIRMS the capability-class tail-shape rule (ran on DESKTOP CPU)

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Cell:** exp_substrate_crossdomain_transfer_agnews_20ng_topic_cpu_v1
**Lane:** remote_cpu_queue (DESKTOP; Testbed cpu_runner_0). Frame: substrate-property; NO LLM comparison.

## Result -- AG-News (news) -> 20NG (forum), 3 shared topics {World,Sports,Sci/Tech}, discriminative_perceptron warm-start
| 20NG train frac | scratch macro-F1 | transfer macro-F1 | ratio |
|---|---|---|---|
| 1pct  | 0.3620 | 0.6135 | 1.695 |
| 2.5pct| 0.4901 | 0.6542 | **1.335** |
| 5pct  | 0.5662 | 0.6850 | 1.210 |
| 10pct | 0.6837 | 0.7385 | 1.080 |
| 100pct| 0.8278 | 0.8293 | **1.002** |

Zero-shot AG-News-on-20NG macro-F1 = 0.4774.

## Verdict: HARD_PASS
ratio@2.5pct = 1.335 (>= 1.20, low-data lift) AND ratio@100pct = 1.002 (in [0.95,1.10], CONVERGES to neutral). This CONFIRMS
the closed-feature converging-tail prediction at a NON-SENTIMENT task.

## The capability-class tail-shape rule is now well-anchored
meta::RULE_cross_domain_transfer_tail_shape_is_capability_class_dependent (open-vocab persists / closed-feature converges):
- **Closed-feature, CONVERGES:** PP-409 SST-2->IMDB sentiment (ratio@100pct 0.998) + this AG-News->20NG topic (ratio@100pct 1.002). TWO anchors.
- **Open-vocab, NON-converging tail:** CoNLL->OntoNotes NER (ratio@100pct 1.150). ONE anchor.
The split is clean: bounded-class single-label tasks (sentiment, topic) fully subsume the source prior once target data is
ample; open-vocabulary sequence labeling (NER) retains a cross-domain advantage (the source supplies entity vocabulary the
target lacks even at full data). 2nd closed-feature anchor CONFIRMS; rule promotes toward validated.

## Process note (compute reassignment working)
First cell run on the DESKTOP CPU (remote_cpu_queue, Testbed's cpu_runner_0, BELOWNORMAL) per USER directive (laptop paused).
End-to-end pipeline worked: laptop --self-test gate -> SCP to home -> desktop runner claimed + ran -> result. Also: switched
the 20NG source from sklearn.fetch_20newsgroups (hung on download) to SetFit/20_newsgroups parquet via datasets lib (reliable).

## Routing
- **Exp-Dev:** closed-feature topic transfer DONE (HARD_PASS, converges). Desktop CPU pipeline proven. GPU idle.
- **Research:** verdict_handler -- 2nd closed-feature anchor; the tail-shape rule (closed converges / open persists) now has
  2 closed + 1 open anchor. 3rd-appearance candidates: another open-vocab task (POS/slot-filling) for the tail side, or a
  4th-class topic dataset for the closed side.
