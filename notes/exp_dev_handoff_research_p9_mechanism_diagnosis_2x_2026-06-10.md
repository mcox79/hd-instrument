# exp_dev hand-off -- research: P9 mechanism diagnosis (2x)

**Filed-by.** research sub-agent, 2026-06-10.  
**Trigger.** Research note d:/AI/hd-instrument/notes/research_drill_p9_mechanism_diagnosis_2x_2026-06-10.md delivered mechanism diagnosis for P9 Option A (Hits@1=0.183 / Hits@10=0.514 on held-out ConceptNet relations). Five ranked control experiments ready for empirical test.

**Pause state.** Check d:/AI/hd-instrument/data/orchestrator_paused.flag before dispatch. If paused, hold until flag cleared.

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and provides context pointers only. Exp-dev designs the actual experiment code, pre-reg bands, and dispatch config autonomously.

---

## Anchor candidates (rank-ordered)

### 1. RANDOM-TIER-1 (mechanism discriminator -- highest priority)

**What it tests.** After training the multi-tier RotatE checkpoint, randomly shuffle universal-relation embedding vectors across relation types. Entity embeddings (Tier-3) remain unchanged. Re-evaluate Hits@10 on the held-out-relation query set.

**Substrate-product reading.** If shuffled Hits@10 drops by >= 11pp (below 0.40), Tier-1 is contributing non-trivially; multi-tier mechanism is plausible. If shuffled Hits@10 stays above 0.45, entity-geometry confound is dominant and Hits@10=0.514 is not evidence for multi-tier mechanism. This is the cheapest, most decisive single test in the battery.

**Pre-implementation check required.** Verify that the eval code passes the actual Tier-1 embedding vector at inference for held-out-relation queries (not zero-phase or default). If the eval code uses zero-phase for unseen relations, Tier-1 contributes nothing by construction -- the shuffle will be flat regardless, and entity-geometry confound is confirmed by that fact alone.

**Tier hint.** Inference-only on existing checkpoint. CPU, minutes. No retraining. No cloud required.

**Why now.** This is the first gate for any product claim about cross-relation generalization. Without it, Hits@10=0.514 is labeled "undifferentiated MIDDLE-BAND: mechanism vs confound unresolved" -- not "weak-positive."

**Pre-reg bands (for exp-dev to formalize):**
- HARD-PASS: shuffled Hits@10 <= 0.40 (Tier-1 contributes >= 11pp; multi-tier mechanism non-trivial)
- MID-BAND: shuffled Hits@10 0.40-0.45
- HARD-FAIL: shuffled Hits@10 >= 0.46 (Tier-1 contributes <= 5pp; entity-geometry confound dominant)

---

### 2. TIER-3-ONLY baseline (entity geometry contribution)

**What it tests.** Score (h, r, t) triples using entity embedding proximity only -- no relation phase applied. For RotatE in complex space, this means scoring by Re(h * conj(t)) across all tail candidates, ignoring the relation vector. Evaluate Hits@10 on the same held-out-relation query set.

**Substrate-product reading.** This isolates entity-geometry contribution. If Tier-3-only Hits@10 is close to 0.514, the relation embedding (Tier-1) is redundant. If substantially lower (< 0.38), the relation embedding is doing real work.

**Tier hint.** Inference-only, modify score function on existing checkpoint. CPU, minutes.

**Why now.** Should run immediately after RANDOM-TIER-1. Together they bound the Tier-1 contribution from both sides (shuffle test = upper bound on Tier-1 contribution; Tier-3-only = direct measurement of entity-geometry baseline).

**Pre-reg bands (for exp-dev to formalize):**
- HARD-PASS: Tier-3-only Hits@10 <= 0.38 (entity geometry alone insufficient)
- MID-BAND: 0.38-0.45
- HARD-FAIL: Tier-3-only Hits@10 >= 0.46 (entity geometry alone nearly matches full model; Tier-1 redundant)

---

### 3. FLAT-ROTATE-SAME-DATA (architectural null hypothesis)

**What it tests.** Train standard flat RotatE on the same dense-subgraph ConceptNet data (21.6K triples / 4.3K entities / 5 relations), with no multi-tier universal-relation construction. Evaluate on the same held-out-relation queries as P9 Option A. Measures the net lift of the multi-tier architecture vs a matched baseline.

**Substrate-product reading.** If flat RotatE achieves Hits@10 >= 0.48, the multi-tier architecture adds less than 3pp -- not distinguishable from noise at this scale. If flat RotatE achieves Hits@10 <= 0.45 and multi-tier achieves >= 0.50, the 5pp+ lift is architecturally meaningful. This is the minimum viable architectural validation.

**Tier hint.** Requires a full training run on the 21K-triple dense subgraph. Home GPU preferred (fast); local CPU feasible (slower, ~30-60 min for small scale). Short wall.

**Why now.** Without this comparison, the multi-tier architecture is evaluated only against itself -- no matched baseline exists. STRETCH4-2 data may provide this if the same subgraph was used; confirm before re-training.

**Pre-reg bands (for exp-dev to formalize):**
- HARD-PASS: flat RotatE Hits@10 <= 0.45 AND multi-tier Hits@10 >= 0.50 (5pp lift confirmed)
- MID-BAND: 2-5pp lift
- HARD-FAIL: flat RotatE Hits@10 >= 0.48 (multi-tier lift < 3pp; architecture not distinguished)

---

### 4. LEXICAL-COSINE-BASELINE (zero-training reference point)

**What it tests.** Score (h, r, t) held-out queries using GloVe or FastText cosine similarity between head entity string and candidate tail entity strings. No training, no KGE. Rank tails by lexical proximity to head. Report Hits@10.

**Substrate-product reading.** If the KGE model (Hits@10=0.514) exceeds lexical baseline by >= 10pp, the model has learned structural relational knowledge beyond raw concept-word similarity. If the gap is < 5pp, most of the KGE performance is explained by pre-existing lexical semantics and the training data provides minimal relational learning.

**Tier hint.** Load GloVe/FastText 300d (pre-trained, freely available). Score eval set. CPU, minutes. No GPU.

**Why now.** Cheapest external reference baseline. ConceptNet entities are concept words; lexical similarity is a non-trivial prior. This baseline should accompany all ConceptNet KGE evaluation reports.

**Pre-reg bands (for exp-dev to formalize):**
- HARD-PASS: KGE Hits@10 - lexical Hits@10 >= 0.10 (KGE adds 10pp above lexical)
- MID-BAND: 5-10pp gap
- HARD-FAIL: KGE Hits@10 - lexical Hits@10 < 0.05 (barely above lexical; structural learning minimal)

---

### 5. FREQUENCY-CONTROLLED HELD-OUT (clean cross-relation transfer test, requires structured ConceptNet)

**What it tests.** Select held-out relations that have similar head/tail entity degree distributions to training relations. This controls for degree bias by ensuring held-out queries do not systematically involve higher-degree entities than training queries. Evaluate Hits@10 on this frequency-controlled held-out set.

**Substrate-product reading.** If Hits@10 drops substantially vs the uncontrolled held-out eval (from 0.514 to < 0.35), degree bias was a primary confound. If Hits@10 stays above 0.45, the multi-tier result is robust to degree control.

**Tier hint.** Requires structured ConceptNet dump (not NL-parsed) to get clean relation splits and degree statistics. Testbed's ConceptNet 458K structured facts (from ingestion pipeline) is the right data source. Home GPU preferred.

**Why now.** Lower priority than anchors 1-4 because it requires data design work (structured ConceptNet + relation frequency analysis). Run after anchors 1-3 resolve the mechanism vs confound question at the design level.

**Pre-reg bands (for exp-dev to formalize):**
- HARD-PASS: frequency-controlled Hits@10 >= 0.45 (result is robust to degree control; multi-tier likely genuine)
- MID-BAND: 0.35-0.45 (partial degree confound; architecture partially robust)
- HARD-FAIL: frequency-controlled Hits@10 < 0.35 (degree bias was primary driver; result not robust)

---

## Context pointers

- Research note (full mechanism analysis and lit review): d:/AI/hd-instrument/notes/research_drill_p9_mechanism_diagnosis_2x_2026-06-10.md
- P9 Option A original result: d:/AI/hd-instrument/notes/exp_dev_to_research_P9_OPTION_A_RESULT_2026-06-10.md
- P9 data design blocker note: d:/AI/hd-instrument/notes/exp_dev_to_research_P9_DATA_DESIGN_BLOCKER_2026-06-10.md
- P9 ACK and WAVE-5 hand-off: d:/AI/hd-instrument/notes/exp_dev_to_research_P9_ACK_AND_HANDOFF_2026-06-10.md
- RotatE source paper: https://arxiv.org/abs/1902.10197
- Degree bias in KGC: https://arxiv.org/abs/2302.05044
- Status log: d:/AI/hd-instrument/data/orchestrator_status_log.jsonl

---

## Contract

Exp-dev designs anchors with pre-regs per envelope-fail-bands. No inline experiment design in this file. Dispatch via queue_add.sh (home GPU for training anchors; local CPU for inference-only controls). Post-ship REMOTE VERIFY per role contract.

## Autonomy declaration

Exp-dev has full autonomy to: run anchors 1-2 (inference-only) before retraining for anchor 3; batch anchors 1+2+4 in a single CPU session; skip anchor 5 until structured ConceptNet is available from Testbed; adjust pre-reg band numbers based on current cap_map state at dispatch time. Escalate to orchestrator if: anchor 1 (RANDOM-TIER-1) returns HARD-PASS (Tier-1 contributes >= 11pp) AND anchor 2 (TIER-3-ONLY) HARD-FAILS simultaneously -- this combination would require Research review of the mechanism story before proceeding to anchor 3. Also escalate if the eval code turns out to use zero-phase for unseen relations (confirms entity-geometry confound by construction; no further controls needed for P9 Option A).
