# exp_dev hand-off -- research: substrate scientific reasoning engine (3x)

Filed-by: research sub-agent
Date: 2026-06-09
Trigger: notes/research_drill_substrate_scientific_reasoning_3x_2026-06-09.md
Urgency: HIGH -- scientific reasoning engine claim enables regulated-industry v2.0 positioning; 8 anchors
ranked; cheapest decisive test is 4hr CPU, no cloud required.

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev
from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: abduction_smoke_10k_v1

Anchor pointer: Research note Section 5 (Cheap Decisive Test) + Section 4 Rank 1 (ABDUCTION-PIPELINE 7.1)
Substrate-product reading: K-hop depth-5 candidate enumeration + PP-246 Bayesian ranking over a 10k-fact
biomedical KB. Validates end-to-end abduction (inference to best explanation) with Merkle audit certificate
per hypothesis. This is the GATEWAY anchor -- gates all downstream scientific reasoning engine claims. If
recall@1 >= 0.60, the reasoning engine claim is smoke-validated. If recall@1 < 0.30, the bottleneck is KB
quality, not reasoning primitive quality.
Tier hint: CPU laptop, ~4 hours total (2hr KB construction from curated biomedical triples + 2hr inference).
No GPU. No cloud. Gate: run FIRST.
Why now: Cheapest and most decisive. Validates or redirects all 7 downstream anchors.

Pre-reg bands:
  HARD-PASS: recall@1 >= 0.60 AND audit certificate completeness = 1.0 for all 20 abduction tasks.
  MIDDLE-BAND: recall@1 = 0.30-0.60 (partial; investigate K-hop depth or KB density).
  HARD-FAIL: recall@1 < 0.30 OR any audit certificate gap (KB quality bottleneck; redirect to KB construction
  methodology before reasoning engine claim).

### Anchor 2: belief_revision_agm_v1

Anchor pointer: Research note Section 1.5 + Section 4 Rank 3 (BELIEF-REVISION-PIPELINE 7.4)
Substrate-product reading: Validates that PP-246 Bayesian update + sleep-defrag satisfies AGM belief revision
postulates (success, inclusion, vacuity, consistency, extensionality) over 50 revision operations on a 1k-fact
KB. This is the formal precondition for the "auditable scientific reasoning engine" positioning claim -- without
AGM compliance, the belief revision claim is informal.
Tier hint: CPU laptop, ~2-3 hours. Algebraic verification, no GPU.
Why now: Second-cheapest decisive test; establishes formal correctness of the belief revision primitive.

Pre-reg bands:
  HARD-PASS: all 5 AGM postulates satisfied for >= 45/50 operations.
  MIDDLE-BAND: 4/5 postulates satisfied for >= 45/50 (identify which postulate fails; direct rescue).
  HARD-FAIL: any postulate violated in >= 20% of operations (sleep-defrag does NOT implement AGM; explicit
  AGM-compliant operator needed).

### Anchor 3: hypothesis_gen_biomed_v1

Anchor pointer: Research note Section 2.1 + Section 4 Rank 2 (HYPOTHESIS-GEN-BIOMED 7.2)
Substrate-product reading: Drug repurposing via RESOLVE analogical transfer + PP-246 ranking over a 1k
biomedical fact KB (drug-mechanism-effect triples). Validate recall@5 vs DrugBank gold standard. Combined
with Anchor 1 result: if abduction works + RESOLVE identifies correct drug analogies, the biomedical
reasoning engine claim is validated at CPU-demo scale.
Tier hint: CPU laptop, ~3-4 hours. Requires RESOLVE empirical validation (not yet run). Gate: run after
Anchor 1 (abduction smoke) PASSES.
Why now: Biomedical is highest-value regulated vertical for v1 demo. GDPR exact erasure + Merkle audit are
already validated; this anchors the REASONING capability in the same vertical.

Pre-reg bands:
  HARD-PASS: recall@5 >= 0.40 AND deletion certificate verified for 5 patient-data facts.
  MIDDLE-BAND: recall@5 = 0.15-0.40 (partial; RESOLVE partially functional; tune relation schema alignment).
  HARD-FAIL: recall@5 < 0.15 OR deletion certificate failure.

### Anchor 4: experimental_design_eig_v1

Anchor pointer: Research note Section 1.6 + Section 4 Rank 4 (EXPERIMENTAL-DESIGN 7.5)
Substrate-product reading: Expected information gain maximization: given current substrate KB, rank 20
candidate experiments by expected PP-246 posterior shift. Validate Spearman correlation vs oracle (experiments
that actually changed beliefs most). Closes the autonomous science loop: hypothesis -> experiment -> evidence
-> belief update.
Tier hint: CPU laptop, ~2-3 hours. 100-fact chemistry KB. Gate: run after Anchor 2 (AGM validation) shows
belief revision is functioning.
Why now: EIG-based experiment ranking is the most differentiating capability vs manual or LLM-based science --
fully automated, auditable experiment prioritization.

Pre-reg bands:
  HARD-PASS: Spearman >= 0.60 (EIG ranking significantly correlated with oracle).
  MIDDLE-BAND: Spearman = 0.20-0.60 (partial; investigate PP-246 resolution vs continuous parameter spaces).
  HARD-FAIL: Spearman < 0.20 (EIG worse than random; discrete-fact approximation insufficient for continuous
  parameter experiment design).

### Anchor 5: head_to_head_vs_lm_science_v1

Anchor pointer: Research note Section 4 Rank 6 (HEAD-TO-HEAD-VS-COSCIENTIST 7.8)
Substrate-product reading: Direct comparison on 20 knowledge-base-grounded scientific inference tasks:
substrate pipeline (K-hop + PP-246 + Merkle) vs GPT-4o-mini (no KB). Measures (a) audit certificate
completeness (substrate guaranteed 1.0), (b) hypothesis correctness (neutral -- LLM may win), (c) GDPR
erasure provability (substrate wins by construction). Validates the North Star "functional system beats LLMs
in measurable ways" specifically for the scientific reasoning vertical.
Tier hint: CPU + API calls (~$0.10 at GPT-4o-mini pricing). ~4-6 hours. Gate: run after Anchor 1 + Anchor 3
establish substrate's baseline correctness.
Why now: North Star objective requires head-to-head empirical evidence. This is the most direct validation.

Pre-reg bands:
  HARD-PASS: audit completeness = 1.0 (guaranteed by construction) AND hypothesis correctness >= 0.5 * LLM
  baseline (reasoning quality not too far below LLM).
  MIDDLE-BAND: hypothesis correctness = 0.2-0.5 * LLM (substrate less correct but audit-certified; valid
  for regulated industry where audit > correctness in the short term).
  HARD-FAIL: hypothesis correctness < 0.2 * LLM (reasoning quality too poor for any practical use case;
  redirect to KB quality investigation).

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_scientific_reasoning_3x_2026-06-09.md
- Substrate cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md (PP-246, PP-247, PP-172, PP-248,
  PP-184, PP-104 rows)
- Exp_dev brief: d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md (PATH B KBLaM
  synthesis: scientific reasoning engine + in-weights memory converge on same architecture)
- Fact extraction pipeline: testbed brief (Wikipedia 100K DONE, ConceptNet 8M DONE, arXiv 2M RUNNING) --
  use these as KB sources for Anchor 1 and 3, not raw PubMed (extraction infrastructure already running)
- RESOLVE routing: substrate_capability_map.md (RESOLVE pattern, analogical reasoning row)

---

## Contract

exp_dev is responsible for:
- Deciding whether to queue any of these anchors (pause gate check first).
- Authoring all cell grids, hyperparameters, and script details from the research note pointers.
- Pre-registering HARD-PASS/HARD-FAIL bands before dispatch (use research note Section 6 as starting point;
  adjust based on any additional smoke data).
- Reporting verdict back to orchestrator for cap_map update.

Research is responsible for:
- Providing the scientific framing and P estimates above.
- Answering follow-up questions if a HARD-FAIL redirects to a new research question.

---

## Autonomy declaration

exp_dev has full autonomy to sequence, prioritize, and queue these anchors within the pause gate constraint.
The rank ordering above is a recommendation based on cost-and-gate logic; exp_dev may reorder based on lane
availability (CPU vs GPU). Anchor 1 (abduction smoke) is the only hard gate: anchors 3, 4, 5 should not be
dispatched before Anchor 1 result is known.
