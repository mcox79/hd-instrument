# exp_dev hand-off -- research: cross-domain round 5

**Filed:** 2026-06-07 by research sub-agent (Sonnet).

**Trigger:** Cross-domain mining round 5 delivered. 6 fields mined; 5 testable cell candidates identified with clear HP/HF bands. Cheap decisive test identified (30 min CPU). See notes/research_drill_cross_domain_round5_2026-06-07.md for full findings.

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered; exp_dev picks across queues)

### 1. Effective interaction order probe (CELL-MF-1 from mean-field field)
- Anchor pointer: notes/research_drill_cross_domain_round5_2026-06-07.md section FIELD 1 CELL-MF-1
- Substrate-product reading: RSB alpha_c=0.144N is the hard ceiling for two-spin Hebbian W. If substrate W is truly two-spin, d_eff=91.6 supports only ~13 patterns maximum -- the 122-cap result is impossible under two-spin unless alpha is computed vs N=1024 (not d_eff). This single cheap test determines whether production is at its fundamental limit or has 5-10x headroom.
- Tier hint: LOCAL or REMOTE CPU (30 min, algebraic sweep, no GPU needed)
- Why now: cheapest decisive test in this round; adjudicates between O(N) and O(N^2) capacity scaling

### 2. Encoder health / IB collapse check (CELL-IB-3)
- Anchor pointer: notes/research_drill_cross_domain_round5_2026-06-07.md section FIELD 3 CELL-IB-3
- Substrate-product reading: if BGE-large encoder has undergone neural collapse on the fabrication domain, within-class instance discrimination fails. This is a product-reliability blocker -- all per-batch and per-supplier localization fails silently. Pre-scaling health check.
- Tier hint: REMOTE CPU (encode 20 instances per class, measure cosine similarity distribution, ~30 min)
- Why now: should run BEFORE scaling to larger M or more customers; 30-min test that can save weeks of debugging

### 3. K-hop sequential vs CRT composition error scaling (CELL-CAT-1)
- Anchor pointer: notes/research_drill_cross_domain_round5_2026-06-07.md section FIELD 2 CELL-CAT-1
- Substrate-product reading: category-theory predicts sequential K-hop composition accumulates error faster than CRT product composition. If confirmed, CRT is the correct architecture for K > 5 chains and multi-head + staged-pipeline should be deprecated for long chains.
- Tier hint: REMOTE GPU (K sweep from 1 to 20, multiple seeds, multiple composition modes)
- Why now: directly informs production architecture decision; CRT 143x smoke awaiting full validation

### 4. CRT mode-locking check for near-rational moduli (CELL-RD-1)
- Anchor pointer: notes/research_drill_cross_domain_round5_2026-06-07.md section FIELD 4 CELL-RD-1
- Substrate-product reading: Turing-instability predicts that CRT moduli with near-rational ratio m1/m2 ~ p/q (small p+q) will mode-lock and collapse the multi-scale representation. Standard coprime moduli should be safe but this has not been empirically verified. A quick ablation comparing incommensurable vs near-commensurable moduli validates the 143x claim.
- Tier hint: REMOTE CPU (algebraic sweep over moduli ratios, ~1 hr)
- Why now: low cost; validates a known vulnerability in CRT architecture before production

### 5. Glass-phase spurious attractor profile (CELL-MF-2)
- Anchor pointer: notes/research_drill_cross_domain_round5_2026-06-07.md section FIELD 1 CELL-MF-2
- Substrate-product reading: RSB predicts spurious attractors at alpha > 0.05*d_eff with overlap q~0.5 to true patterns. If confirmed at production loading levels, it explains the cycle-137 multi-head collapse at 45% noise: retrievals land in glass-phase spurious basins. Knowing the glass-phase alpha boundary enables principled capacity planning per CRT subspace.
- Tier hint: REMOTE CPU (alpha sweep from 0.02 to 0.20, measure retrieval overlap distribution, ~2 hr)
- Why now: fills the glass-phase boundary which is the safe operating regime per multiple converging cross-field findings

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_cross_domain_round5_2026-06-07.md
- Prior spin-glass round (RSB prior): notes/research_drill_cross_domain_round4_*.md (most recent)
- Production recipe (locked): notes/orchestrator_post_compaction_brief.md
- Cycle 137 multi-head collapse at 45% flip (failure mode 1): data/exp_*/metrics.json for multi-head collapse anchor
- Field advisor: tools/orchestrator/research_field_advisor.py

---

## Contract

exp_dev owns ALL implementation decisions: anchor names, N/M/K sweeps, seed counts, threshold bands, queue routing, ETA. Research provides only the WHAT and WHY -- not the HOW.

## Autonomy declaration

exp_dev may sequence, merge, or defer these anchors per strategic priorities and queue depth. If queue is already full (depth >= 3), hold anchors 3-5 and ship only 1-2. If queue is empty and runner is idle, ship all 5 in a single batch with smoke gates on 1-2.
