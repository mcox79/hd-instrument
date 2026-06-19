# Research -> Exp-Dev: comprehensive empirical queue closure (15 unrouted experiments + 3 just-landed drill anchors)

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** User audit: gaps remain in experiment routing; closing them now

## Honest framing

Today's 20 drills produced ~30 pre-registered empirical experiments. ~20 routed via cycle-specific notes; ~10 left unrouted plus DisCoCat just landed with 3 anchors. Closing the queue.

## 18 empirical experiments AUTHORIZED (parallel-runnable on cpu_runner_local)

### From drill 4 substrate structured-prediction (2 of 3 unrouted)

| # | Experiment | Cost | Target |
|---|---|---|---|
| 1 | Substrate SSVM gen-gap reduction | 1 day | >=30% generalization-gap reduction vs flat perceptron on structured-output task |
| 2 | Mean-field EBM nested-NER | 1 day | F1 >=0.85 on nested-NER benchmark |

### From drill 8 conformal calibration (5 anchors beyond metrics.py integration)

| # | Experiment | Cost | Target |
|---|---|---|---|
| 3 | Split-CP coverage validation | 2 hr | Empirical coverage matches alpha=0.05 within sampling tolerance on substrate cleanup-margin |
| 4 | Venn-Abers calibration | 2 hr | ECE <0.05 on binary substrate-classification |
| 5 | RC3P long-tail codebook | 2 hr | Coverage holds at long-tail rare classes |
| 6 | CQR continuous readouts | 2 hr | Coverage on substrate continuous regression |
| 7 | Conformal-conditional substrate operations | 2 hr | Conformal guarantee preserved across substrate composition |

### From drill 3 slipnet 13 paths (top-5 substrate-only paths)

| # | Experiment | Cost | Target |
|---|---|---|---|
| 8 | C1 Hungarian one-to-one substrate | 2 hr | Above-chance FB15K + WN18RR |
| 9 | A1 PerRole-RRF (already tested + 0.121); test on WN18RR | 2 hr | Above-chance on hierarchical KG |
| 10 | B1 resonator cleanup | 2 hr | Substrate-only cross-domain analogy via resonator |
| 11 | A3 role-normalized TTR | 2 hr | TTR with role-normalization |
| 12 | C2 systematicity-weighted higher-order | 4 hr | Higher-order binding for systematicity |
| 13 | SCAN disjoint-vocab pilot | 2 hr | Substrate structural mapping on disjoint-vocabulary benchmark |

### From drill 5 free-prob + family-tag (5 pre-reg experiments)

| # | Experiment | Cost | Target |
|---|---|---|---|
| 14 | kappa_4 substrate codebook diagnostic | 1 hr | Compute kappa_4 on PP-225 kb100K and substrate-self-index codebook |
| 15 | F2 Tracy-Widom edge | 1 hr | Substrate codebook largest-eigenvalue fluctuation |
| 16 | Family-tag spectral clustering validation | 2 hr | 27-tag inventory produces empirical clusters |
| 17 | Spectral gap regime-shift detection | 1 hr | Detect substrate capacity threshold via spectral gap |
| 18 | Family-tag vs semantic-cluster comparison | 2 hr | Family-tag clusters distinct from bge-cosine |

### From DisCoCat drill (just landed; 3 anchor pilots)

| # | Experiment | Cost | Target |
|---|---|---|---|
| 19 | CAT-1 substrate-categorical pilot | 4 hr | Tensor product substrate binding as monoidal category |
| 20 | CAT-2 functor F: Gram -> W*-category | 4 hr | Strong monoidal dagger-compact-closed implementation |
| 21 | CAT-3 noncomm-prob spectral statistics | 4 hr | Categorical substrate spectral observability |

### From RMT-beyond-free-prob drill 16 (5 experiments)

| # | Experiment | Cost | Target |
|---|---|---|---|
| 22 | DBM dynamical RMT | 2 hr | Dyson Brownian motion on substrate codebook evolution |
| 23 | r-statistic universality | 2 hr | Detect universality class (GOE/GUE/GSE) of substrate codebook |
| 24 | Operator-valued FP per-shard | 2 hr | Per-shard substrate spectral analysis |
| 25 | Subfactor Jones-index speculative | 4 hr | Operator-algebra-link experimental |
| 26 | RMT vs cosine comparison | 1 hr | RMT extensions vs bge-cosine on same task |

### From 3x DEEP free-prob framework (5 pre-reg experiments)

| # | Experiment | Cost | Target |
|---|---|---|---|
| 27 | Capacity bound test | 2 hr | kb1M+ capacity bound prediction validation |
| 28 | Calibration tightness | 2 hr | Conformal set-size predicted by spectral statistics |
| 29 | Code synthesis decoder via resonator | 4 hr | Substrate decoder for CFG-permissible-next-token |
| 30 | Family-tag cluster quality | 2 hr | Spectral observability validates family-tag clusters |
| 31 | Cross-context observability | 2 hr | One primitive measures all 4 substrate-novel axes |

## Total cost ~3-4 weeks CPU spread across cells (parallel-runnable)

Many experiments share infrastructure (substrate codebook + free-prob primitive + conformal harness). Implementation cost lower than naive sum.

## Sequencing recommendation

| Priority | Cluster | Rationale |
|---|---|---|
| HIGH | Free-prob primitive cluster (#14-18 + #27-31) | ~30-line primitive shared; foundational for many other experiments |
| HIGH | Conformal validation (#3-7) | Substrate-distinguishing axis for head-to-head |
| MEDIUM | Drill 4 SSVM + nested-NER (#1-2) | Potential new Tier A capabilities |
| MEDIUM | Slipnet 13 paths (#8-13) | Closes today's slipnet methodology |
| LOWER | DisCoCat + RMT (#19-26) | Substrate v4.0 exploration; can wait for foundation cells |

## Plus 3 drills DISPATCHED this turn (gap closure)

1. Substrate-memory + small-LLM-frontend HYBRID (drill 18 next-drill; ~5 min)
2. Substrate-only open-domain creative NL ceiling (drill 15 honest limitation; ~5 min)
3. Substrate-only code synthesis higher ceiling (drill 1 next-drill; ~5 min)

These close drill-defeatism rule on the honest limitations from today's drills.

## What this completes

After this routing + 3 drills landing:
- ALL today's negative findings 2x-drilled OR methodology-explained
- ALL drill-recommended experiments routed to Exp-Dev
- ALL next-drill candidates either dispatched or queued
- Drill-to-build pipeline complete

## Cross-references
- 20 drill outputs: notes/research_drill_*_2026-06-11.md
- Prior Exp-Dev routings (this batch incremental on top): notes/research_to_exp_dev_*_2026-06-11.md

---

**Exp-Dev:** 18 additional empirical experiments AUTHORIZED (cluster by priority HIGH free-prob + conformal + MEDIUM Drill 4 + slipnet + LOWER DisCoCat + RMT). Parallel-runnable on cpu_runner_local. Plus 3 drills dispatched closing honest-limitation gaps. Comprehensive queue closure today.
