# exp_dev hand-off -- research: synthetic-to-real gap audit (Sprint 1 primitives)

**Filed:** 2026-06-10 by research sub-agent.

**Trigger:** Research drill on Cycle 221 Sprint 1 mechanism demonstrations (PP-313/315/316/317).
All 4 HARD_PASS on synthetic encodings. Exp-Dev honest caveat: "Sprint 2+ is where P_deflated
honestly drops with real data." Research drill characterizes expected gaps and designs Sprint 2
real-data tests for all four primitives.

**Research note path:** d:/AI/hd-instrument/notes/research_drill_synthetic_to_real_gap_audit_2x_2026-06-10.md

**Pause state:** Check data/orchestrator_paused.flag before dispatching. This hand-off is
eligible for dispatch when ACTIVE.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names anchors and pointers
only. exp_dev designs ALL of: N, seed count, threshold bands, queue choice (Tier A/B/C),
anchor name, ETA, smoke profile, FULL profile.

---

## Anchor candidates (rank-ordered; exp_dev picks from these)

### Anchor 1: KB-SHARD-REAL (PRIORITY -- most tractable, highest P_deflated)
- Anchor pointer: PP-313 (cap_map v555, cycle 221); research note Section 4.4 + Section 3.4
- Substrate-product reading: encode FB15K-237 entity embeddings (TransE or RotatE, publicly
  available via PyKEEN / DGL-KE, 150-dim) via PCA-whitening to substrate N; construct 40
  relation-type shards; test shard recall@1 on 200 held-out triples. The dominant failure mode
  (intra-shard KGE correlation) is quantifiable and has a known fix (increase N or add
  whitening). This is the most directly product-relevant test (factual KB retrieval).
- Tier: Remote CPU or local CPU (purely numpy/CPU; no GPU needed).
- Pre-registered gates per research note Section 9 F1:
  HARD-PASS: recall@1 >= 0.80 at 40-shard config with TransE embeddings.
  HARD-FAIL: recall@1 < 0.70.
  MIDDLE-BAND: 0.70-0.80 (navigate by increasing N).
- Why now: cheapest path from Sprint 1 to qualified product claim. Data downloadable in
  minutes. Total cost ~4-6 CPU hours. P_deflated=0.50 (highest in Sprint 2 battery).

### Anchor 2: BOREDOM-REAL (CHEAP -- URL revisit log variant)
- Anchor pointer: PP-315 (cap_map v555, cycle 221); research note Section 4.1 + Section 3.1
- Substrate-product reading: run the cleanup-margin novelty classifier on a URL revisit
  session log (URL hash as atom identity; revisit = repeat). No image encoder required.
  Ground truth: revisit flag from session log. Measures whether boredom/novelty signal
  holds when items are exact URL matches but the test is against a real browsing distribution
  (irregular inter-visit intervals, burst-and-gap temporal structure).
  Alternative variant: MIT LowFix reading fixation corpus with gaze data (requires image
  encoder; more expensive but more informative on temporal buffer calibration).
- Tier: local CPU (pure hash-based, no model weights needed for URL variant).
- Pre-registered gates per research note Section 9 F2:
  HARD-PASS: AUC >= 0.75 on URL revisit stream or fixation repeat stream.
  HARD-FAIL: AUC < 0.65.
  MIDDLE-BAND: 0.65-0.75 (buffer decay recalibration needed).
- Why now: cheapest test in the Sprint 2 battery (~4 CPU hours or less). High practical
  relevance (attention/active-learning agent use case).

### Anchor 3: IMAGE-SCHEMA-REAL (ConceptNet abstracts, DEPRIORITIZED)
- Anchor pointer: PP-316 (cap_map v555, cycle 221); research note Section 4.2 + Section 3.2
- Substrate-product reading: extract abstract noun nodes from ConceptNet 5.7 (data already
  in local pipeline -- 458K facts, see Testbed overnight chain note). Encode via production
  encoder (Llama-1B BASE last-token pool, PCA-whitened). Cluster to k-means with k=10-20
  schema categories. Evaluate purity with BOTH hard single-label and soft top-2 schema
  membership (per research note polysemy framing).
- Tier: Remote CPU (requires Llama-1B BASE encoding; 2000+ concepts; ~2 CPU hours after
  ConceptNet abstract filter).
- Pre-registered gates per research note Section 9 F3:
  HARD-PASS: cluster_purity >= 0.50 (hard) OR >= 0.65 (soft top-2).
  HARD-FAIL: cluster_purity < 0.35 on both labeling schemes.
  MIDDLE-BAND: 0.35-0.50.
  IMPORTANT: if HARD-FAIL triggers, report purity separately for mono-schema and multi-schema
  concepts (polysemy-limited floor is not a mechanism failure).
- Why DEPRIORITIZED: P_deflated=0.28 (lowest; polysemy is a qualitative challenge, not just
  noise). The demo story for image-schema grounding requires additional mechanism work if
  Sprint 2 hard-fails. Run AFTER KB-shard and boredom.

### Anchor 4: TOOL-EXTENDED-REAL (PyBullet simulation, DEPRIORITIZED)
- Anchor pointer: PP-317 (cap_map v555, cycle 221); research note Section 4.3 + Section 3.3
- Substrate-product reading: use PyBullet physics simulation (Kuka or Franka arm grasping
  objects of varying mass/compliance). Encode joint-torque + end-effector force streams as HD
  atoms via time-series feature extraction (mean + variance + peak torque) -> PCA-whitening.
  Run body-schema update after N_use trials. Measure membership_AUC of used-tool HD vector
  against body-part HD vectors.
- Tier: local CPU (PyBullet is CPU-only physics; ~1-2 CPU days).
- Pre-registered gates per research note Section 9 F4:
  HARD-PASS: membership_AUC >= 0.75, tool_delta >= 0.05.
  HARD-FAIL: AUC < 0.65 or tool_delta <= 0.00.
  MIDDLE-BAND: AUC 0.65-0.75.
- Why DEPRIORITIZED: requires physics simulation setup overhead; P_deflated=0.42. Run after
  KB-shard and boredom. Key question is transduction chain transparency.

---

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_synthetic_to_real_gap_audit_2x_2026-06-10.md
  -- full per-primitive gap analysis, failure modes, and pre-registered gates
- d:/AI/hd-instrument/notes/substrate_capability_map.md
  -- PP-313/315/316/317 entries (v555, cycle 221) + PP-314 gap analysis
- d:/AI/hd-instrument/notes/research_drill_synthetic_vs_real_prediction_gap_2x_2026-06-07.md
  -- prior methodology drill; Type 1/2/3 failure taxonomy; split P_deflated framework

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE
  smoke (use gates from research note Section 9 above).
- Self-test per [[feedback-formula-selftests]].
- Multi-seed FULL on smoke clearance.
- Queue routing per Tier A/B/C in agents/exp_dev.md Section 0.
- Ship via bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>.
- POST-SHIP REMOTE VERIFY per [[feedback-ship-name-collision]].
- status_log entry per anchor with plain_language + importance.

## Autonomy declaration

exp_dev decides ALL of: anchor name, N, seed count, threshold bands (HARD-PASS + HARD-FAIL),
queue choice (Tier A/B/C), ETA, smoke profile, FULL profile. The orchestrator passes anchor
POINTERS only. If exp_dev wants to run URL-revisit boredom before KB-shard (e.g., because
local queue is idle and CPU is available), that is exp_dev's call. Research note provides
the failure-mode framing and pre-registered gate logic; experiment design parameters are
exp_dev's exclusive domain.

---

## Filed by

Research sub-agent (Sonnet), 2026-06-10, following cycle 221 5-row Sprint 1 HARD_PASS batch.
Hand-off ready for exp_dev auto-discovery on next emergency-refill or scheduled cycle scan.
