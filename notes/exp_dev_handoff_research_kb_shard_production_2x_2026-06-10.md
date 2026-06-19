# exp_dev hand-off -- research: kb_shard_production_2x

**Filed:** 2026-06-10 by research sub-agent (Sonnet 4.6).

**Trigger:** PP-324 KB-SHARD-REAL HARD_PASS at 0.965 on 1539 real FB15K entities / 20 shards (cycle 222, v556). Research drill confirms the 0.965 is structurally explainable and identifies 5 empirical tests needed to convert to production-scale commercial claim.

**Pause state:** check `data/orchestrator_paused.flag` before queue dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Research note

Full findings at: `d:/AI/hd-instrument/notes/research_drill_kb_shard_production_2x_2026-06-10.md`

Key findings:
- 0.965 holds because: single-domain entity distribution + optimal subject-shard strategy + N >> M_per_shard at 20 shards
- The 3.5% miss rate is most likely hub-entity concentration (high-degree entities with cross-shard correlation bleed)
- 8 push paths identified; D8 (hard-negative shard assignment) is the cheapest/highest-yield fix
- 5 empirical benchmark tests pre-registered with HARD-PASS / HARD-FAIL thresholds
- Open adversarial vulnerability: auc_adv=0.206 (PP, cycle 186) is a known gap requiring shard-consistency-enforcement engineering

---

## Anchor candidates (rank-ordered; exp_dev picks from this list)

### Anchor 1 -- MISS-ENTITY-ANALYSIS (cheapest; 10-minute CPU)

- **Anchor pointer:** PP-324 cap_map v556 (kb_shard_real_cpu_v1, n_ent=1539, n_shard=20, shard_recall=0.965). The 53 miss entities are identifiable from the existing result.
- **Substrate-product reading:** If misses concentrate on hub entities (high-degree nodes in FB15K-237 graph), the shard-construction policy needs degree-weighted assignment. This fixes the 3.5% miss rate without any substrate changes -- pure engineering fix. Research note Section D8 + "Rank 1 cheap test."
- **Tier hint:** Local CPU. Zero cloud cost. Analysis-only.
- **Why now:** The cheapest diagnostic that directly informs the shard-construction engineering fix. If hub concentration is confirmed, D8 anchor follows immediately.

---

### Anchor 2 -- SHARD-SCALE-SWEEP (scale from 20 to 100 shards on full FB15K-237)

- **Anchor pointer:** PP-146 cap_map v513 (fb15k237_kg_khop_benchmark_cpu_v1, n_ent=12838); PP-324 (n_ent=1539, n_shard=20). Research note TEST-1 (WIKIDATA5M-TRANSDUCTIVE-SHARD) + Section D1.
- **Substrate-product reading:** PP-324's 0.965 used 20 shards / 1539 entities. Full FB15K-237 has 14505 entities. Scaling to 100 shards (145 entities/shard) and 500 shards (29 entities/shard) measures the shard-count vs recall tradeoff curve. If recall at 100 shards >= 0.90, the production commercial claim ("96.5% shard recall at production scale") upgrades to "production-range grounded." If recall drops below 0.80 at 100 shards, this is a HARD-FAIL requiring shard-construction redesign before commercial claims.
- **Pre-reg thresholds (research note):** HARD-PASS >= 0.90 at 100 shards; HARD-FAIL < 0.80 at 100 shards.
- **Tier hint:** Remote CPU (full FB15K-237 load, 100+ shard sweep; benchmark requires multi-shard-count sweep). Cross-ref PP-147 (subject-sharding strategy HARD_PASS).
- **Why now:** This is the single experiment that upgrades PP-324 from "real-entity grounded (1539)" to "production-range grounded (14505, 100 shards)." It is the bottleneck for the commercial viability claim.

---

### Anchor 3 -- OGBL-BIOKG-PHASOR-LINK (OGBL leaderboard entry path)

- **Anchor pointer:** PP-275 cap_map v550 (lap3_rotate_analogy_cpu_v1 HARD_PASS Hits@1=0.899, n_ent=1241, n_rel=55; VSA-RotatE equivalence). Research note TEST-3 (OGBL-BIOKG-SUBSTRATE-LINK-SCORE) + Section D4.
- **Substrate-product reading:** PP-275 established that FHRR phasor binding IS mathematically equivalent to RotatE. OGBL-biokg (93,773 entities, 51M triples) is the smaller OGBL link-prediction benchmark. Running substrate phasor embeddings + RotatE relation vectors on OGBL-biokg would produce the first substrate result on a major public ML benchmark leaderboard. NodePiece baseline (6.9M params) achieves MRR ~0.83. Pre-reg HARD-PASS: MRR >= 0.80.
- **Pre-reg thresholds:** HARD-PASS MRR >= 0.80; HARD-FAIL MRR < 0.60.
- **Tier hint:** GPU (OGBL-biokg is 51M triples; embedding training may require GPU; alternatively remote CPU with learned-embedding approach). Research note Section D4 "Rank 3 cheap test."
- **Why now:** This is the leaderboard path. PP-275 provides the theoretical bridge. A competitive OGBL result would be the first substrate claim on a standard public ML benchmark -- required for the "functional system beats LLMs" north star (d:/AI/hd-instrument/notes/north_star_functional_system_beats_LLMs.md).

---

### Anchor 4 -- ADVERSARIAL-SHARD-STRESS (quantify the auc_adv gap)

- **Anchor pointer:** KF-1 cap_map result (auc_adv=0.206, adversarially shuffled KB facts); PP-324 (shard_recall=0.965 on clean data). Research note TEST-4 (ADVERSARIAL-SHARD-ROUTING-STRESS) + Section D3.
- **Substrate-product reading:** The auc_adv=0.206 result (cycle 186) shows the substrate is brittle to adversarially shuffled KB facts. For shard routing specifically, adversarial query vectors (perturbed toward adjacent shard centroids) could reduce shard-routing recall below 0.80. Documenting this failure mode is mandatory before commercial deployment claims. Pre-reg HARD-PASS: shard recall >= 0.90 under 20% adversarial queries; HARD-FAIL: shard recall < 0.75.
- **Pre-reg thresholds:** HARD-PASS >= 0.90; HARD-FAIL < 0.75 under 20% adversarial query injection.
- **Tier hint:** Local CPU. Adversarial construction is a perturbation of existing FB15K query vectors -- no new data needed. Cross-ref KF-1 row.
- **Why now:** The auc_adv=0.206 result is already on record. Before any commercial KB storage claim, the adversarial failure mode must be quantified on the shard-routing task specifically.

---

### Anchor 5 -- HOTPOTQA-DISTRACTOR-MINIKB (multi-hop QA benchmark)

- **Anchor pointer:** PP-149 (cwq_kgqa_benchmark_cpu_v1 recall=0.926 on ComplexWebQA); PP-148 (webqsp_kgqa_benchmark_cpu_v1 recall=0.976). Research note TEST-2 (HOTPOTQA-DISTRACTOR-KB) + Section D2. External reference: arxiv 2512.09369 (Encoder-Free KG Reasoning via Hyperdimensional Path Retrieval) -- directly adjacent prior work to read before design.
- **Substrate-product reading:** PP-148/PP-149 established strong recall on WebQSP and ComplexWebQA given a pre-loaded KG. HotpotQA distractor setting provides 10 candidate paragraphs per question -- build a mini-KB from those 10 paragraphs, use substrate K-hop to find the bridge entity and derive the answer. This isolates reasoning quality from open retrieval. Pre-reg HARD-PASS: Answer EM >= 0.50 (competitive with 2019 baselines); HARD-FAIL: Answer EM < 0.30.
- **Pre-reg thresholds:** HARD-PASS Answer EM >= 0.50; HARD-FAIL Answer EM < 0.30.
- **Tier hint:** Remote CPU (paragraph parsing + KB construction + K-hop traversal; no GPU needed for substrate reasoning layer). Cross-ref PP-119, PP-146, PP-237, PP-258.
- **Why now:** HotpotQA is the canonical multi-hop QA benchmark. PP-148/149 results on WebQSP/CWQ suggest the substrate reasoning layer is ready. This is the head-to-head test vs RAG-based multi-hop systems.

---

## Context pointers

- Research note: `d:/AI/hd-instrument/notes/research_drill_kb_shard_production_2x_2026-06-10.md`
- PP-324 cap_map entry: `d:/AI/hd-instrument/notes/substrate_capability_map.md` (search "PP-324")
- PP-237/238 (FB15K traversal/ranking): same file, search "PP-237"
- PP-149 (ComplexWebQA): same file, search "PP-149"
- PP-275 (VSA-RotatE equivalence): same file, search "PP-275"
- KF-1 adversarial result: same file, search "auc_adv=0.206"
- North star: `d:/AI/hd-instrument/notes/north_star_functional_system_beats_LLMs.md`

---

## Contract

Research filing this hand-off confirms:
1. All 5 anchors have been cross-checked against cap_map state (PP-324/PP-237/PP-238/PP-146/PP-147/PP-148/PP-149/PP-275/KF-1 all read before filing).
2. Pre-reg HARD-PASS / HARD-FAIL thresholds are pre-registered in the research note, not invented post-hoc.
3. Per [[feedback-no-experiment-design-in-prompts]]: no N / M / seed count / queue assignment specified here. exp_dev decides all design parameters.
4. Adversarial vulnerability (auc_adv=0.206) is disclosed; commercial claim without Anchor 4 test is not warranted.

## Autonomy declaration

exp_dev picks which of the 5 anchors to run, in what order, on which queues. Anchor 1 (miss-entity analysis) is flagged as cheapest and should be run first regardless of queue state -- it is analysis-only with zero cost. Anchors 2-5 are ranked by commercial-claim urgency but exp_dev decides the sequence per its own queue-depth and cost policy.
