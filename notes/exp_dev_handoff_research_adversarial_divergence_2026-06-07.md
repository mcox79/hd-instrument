# exp_dev hand-off -- research: adversarial substrate divergence

**Filed-by:** research sub-agent
**Date:** 2026-06-07
**Trigger:** Adversarial probe on 6 production-ready capabilities; research note at notes/research_drill_adversarial_substrate_divergence_2026-06-07.md
**Pause state:** Respect data/orchestrator_paused.flag before dispatching.

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and context pointers only. exp_dev designs all sweep grids, thresholds, queue routing, and pre-reg bands autonomously.

---

## Anchor candidates (rank-ordered)

### 1. KF-1 paraphrase robustness battery [TIER-1 URGENT]
**Anchor pointer:** KF-1 hallucination detector (AUC=0.977 claimed).
**Substrate-product reading:** Word-bigram detector is known to collapse under paraphrase attacks per NLP adversarial robustness literature. Back-translation paraphrase is script-kiddie accessible. If AUC falls below 0.85 on back-translated test set, the production hallucination guard is not deployable without a hybrid upgrade.
**Tier hint:** Tier-1 (CRITICAL severity, script-kiddie accessible attack vector, cheap test: 1 GPU-hour).
**Why-now:** This is the cheapest and highest-impact adversarial validation available. KF-1 is the hallucination guard for ALL 6 production capabilities indirectly (reasoning chain verification relies on it). Paraphrase attack requires no novel infrastructure -- existing KF-1 checkpoint + open-source MT models.

### 2. fp16 vs fp32 parity test across 6 capabilities [TIER-2 HIGH]
**Anchor pointer:** Production recipe uses PCA whitening (3.05x mean-pool improvement), fp32 computed at training time.
**Substrate-product reading:** If production inference runs fp16 (common optimization), PCA whitening projection drifts. The 6 production-ready metric claims may not hold at fp16 precision. This is a quick parity check with high stakes.
**Tier hint:** Tier-2 (HIGH severity, quick verification test).
**Why-now:** LVH #241 (div-by-zero metric inflation) demonstrates measurement pipeline bugs exist. fp16 parity is the cheapest next measurement-hygiene check.

### 3. Cap overflow stress test [TIER-2 HIGH]
**Anchor pointer:** d_eff=91.6 ceiling at cap=122; continual-KV 100% retention at 120 sessions.
**Substrate-product reading:** Inject 130-150 semantically diverse items into a cap=122 substrate. Measure retention accuracy, retrieval quality, and K-hop reasoning accuracy above the documented ceiling. The "robust at production scale" claim is untested above cap=122.
**Tier hint:** Tier-2 (CRITICAL severity for production deployment, medium CPU cost).
**Why-now:** At-capacity forcing is a script-kiddie attack (AV-8). Understanding the degradation curve above cap=122 is required before hard write-guard thresholds can be set.

### 4. K=20 K-hop accuracy on 200-cell independent test [TIER-2 HIGH]
**Anchor pointer:** K-hop battery 100% on 30 cells.
**Substrate-product reading:** 30 cells gives 95% CI lower bound of ~88% per Wilson interval. 200-cell independent test with production-diverse (non-Dolly/SQuAD) inputs is required to tighten the interval and test distribution shift from lab to production.
**Tier hint:** Tier-2 (HIGH severity, moderate CPU cost for 200-cell sweep).
**Why-now:** "100% on 30 cells" is the most statistically thin of the 6 production claims. Independent verification required before production claim is defensible.

### 5. Merkle chain concurrent load latency test [TIER-3 MEDIUM]
**Anchor pointer:** Merkle-chain crypto-certified reasoning at 0.051ms (single-thread).
**Substrate-product reading:** 0.051ms is a single-thread median. Under 100 concurrent verifications, latency may degrade 10-50x due to hash function cache pressure. Production SLA requires characterization of 95th percentile latency under load.
**Tier hint:** Tier-3 (MEDIUM severity, low CPU cost).
**Why-now:** Concurrent load test requires minimal new infrastructure. Needed before audit chain can be presented as a production SLA component.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_adversarial_substrate_divergence_2026-06-07.md
- Adversary capability matrix and hardening checklist: see research note sections "ADVERSARY CAPABILITY MATRIX" and "PRODUCTION HARDENING CHECKLIST"
- Falsifiable predictions table with HARD-PASS / HARD-FAIL thresholds: see research note section "FALSIFIABLE PREDICTIONS"
- LVH #241 (div-by-zero metric inflation): referenced in research note AV-7 section
- Cap_map: d:/AI/hd-instrument/data/cap_map.md (rows: KF-1 hallucination, K-hop reasoning, continual-KV, Merkle audit)
- Prior KF-1 results: search notes/ for research notes mentioning KF-1 or hallucination AUC

---

## Contract

exp_dev owns: experiment design, sweep grids, anchor naming, queue routing, pre-reg bands, self-test verification.
research owns: literature synthesis, attack vector analysis, P_deflated estimates, hardening recommendations.
orchestrator owns: strategic prioritization, cap_map updates, verdict processing.

## Autonomy declaration

exp_dev is fully autonomous on all design decisions within the anchors above. The anchor candidates are rank-ordered by urgency but exp_dev may reorder based on queue state, runner availability, and dependency constraints. Do not design experiments inline in this file -- that is exp_dev's lane.
