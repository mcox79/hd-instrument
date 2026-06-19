# exp_dev hand-off -- research: substrate evaluation methodology 5x chain drill 1

Filed-by: research sub-agent
Trigger: d:/AI/hd-instrument/notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill1_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT + AUTONOMY.
exp_dev decides anchor names, sweep grids, threshold formulas, queue choice, and ETA.
Do NOT re-specify what is already specified here.

---

## Anchor Candidates (rank-ordered)

### Rank 1: FActScore + HalluLens Nonsense track baseline run (EVAL-1)
- Anchor pointer: Research note Section 3 (Framework S1: Substrate Auditability Score) + Section 4 (Cheap Decisive Test)
- Substrate-product reading: Run substrate on HalluLens 2025 Nonsense track (non-existent entity handling) and FActScore medical domain 100-question test set. Compare provenance coverage and soundness to GPT-4 and RAG baseline. If substrate FActScore atomic precision exceeds RAG baseline by >15pp, the SAS framework has empirical legs for commercial differentiation.
- Tier hint: CPU-local, ~2h analyst time + API spend; no GPU required; uses existing substrate retrieval pipeline
- Why now: Cheapest possible differentiation signal; no additional development needed; HalluLens Nonsense track directly measures the structural property substrate claims

### Rank 2: ZKP Soundness test -- never-stored adversarial query suite (EVAL-2)
- Anchor pointer: Research note Section 2.2 (ZKP Completeness/Soundness) + Framework S3 (SZA)
- Substrate-product reading: Present 500 never-stored facts as queries to substrate. Measure false assertion rate (soundness score S). This directly tests whether substrate's structural no-false-assertion property holds empirically. If S < 0.5% false assertion rate, substrate has a uniquely differentiating HIPAA/SEC claim.
- Tier hint: CPU-local, ~1h to generate query suite + run; no GPU required
- Why now: Directly tests the GOLD finding (ZKP soundness unmeasured axis); result immediately informs enterprise sales narrative; zero dependency on other experiments

### Rank 3: Membership inference leakage measurement (EVAL-3)
- Anchor pointer: Research note Section 2.2 (Zero-knowledge leakage metric ZKL) + Framework S3 (SZA)
- Substrate-product reading: Run black-box membership inference attack against substrate outputs. Measure what fraction of stored vector content can be reconstructed from output behavior alone. Hard-fail threshold: >10% reconstruction means HIPAA use case is disqualified. This is currently unmeasured and is the HIPAA-critical eval axis.
- Tier hint: CPU-local; standard membership inference attack implementations available; ~4h implementation + run
- Why now: HIPAA compliance officers are asking this question; no current ML benchmark measures it; substrate may uniquely pass where LLMs fail

### Rank 4: Temporal ordering accuracy test -- SORT protocol (EVAL-4)
- Anchor pointer: Research note Section 2.4 (EpBench/SORT) + Framework S4 (STP)
- Substrate-product reading: Store 50 facts with known timestamps; query substrate for temporal ordering of events; measure SORT accuracy. Hard-fail: <80% accuracy means temporal provenance claims are not supportable for legal discovery use case.
- Tier hint: CPU-local, ~2h; uses existing substrate timestamp architecture; directly testable without new infrastructure
- Why now: Legal discovery market; temporal ordering is the question that eliminates expert testimony disputes; substrate's timestamped provenance should trivially pass where LLMs fail

### Rank 5: Contradiction transparency measurement (EVAL-5)
- Anchor pointer: Research note Section 2.3 (AAR standard) + Framework S1 (SAS)
- Substrate-product reading: Store intentionally contradictory facts (fact X and negation of X) in substrate. Query substrate on the disputed fact. Measure whether substrate surfaces the contradiction vs suppressing it. AAR standard's contradiction transparency metric directly corresponds. Healthcare AI customers need to know whether the system lies vs flags uncertainty.
- Tier hint: CPU-local, ~1h; synthetic contradiction test set; directly measures AAR metric 3
- Why now: Contradiction transparency is an AAR-standard metric substrate can score on immediately; supports the commercial SAS framework positioning

---

## Context Pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill1_2026-06-07.md
- AAR standard paper: arXiv 2602.13855 (Claim-Level Auditability for Deep Research Agents)
- HalluLens 2025: arXiv 2504.17550
- EpBench SORT: openreview.net/forum?id=LLtUtzSOL5
- ZKProof benchmarking: docs.zkproof.org/pages/standards/accepted-workshop3/proposal-benchmarking.pdf
- Cap map: d:/AI/hd-instrument/data/cap_map.md (check current eval-related rows before dispatch)
- Status log: d:/AI/hd-instrument/data/orchestrator_status_log.jsonl

---

## Contract

exp_dev owns: anchor naming, test set construction, scoring threshold choice, queue selection,
runtime estimate, and all implementation decisions.
Research hands off: the evaluation framework design space, P_deflated estimates, HARD-PASS /
HARD-FAIL thresholds (as stated above), and the commercial use-case rationale.

---

## Autonomy Declaration

exp_dev is fully autonomous on all implementation decisions for EVAL-1 through EVAL-5.
Do not ask research or orchestrator for clarification on test set design, scoring formulas,
or queue routing. The hard-fail thresholds stated above are the pre-reg boundaries;
exp_dev may tighten but not loosen them without re-routing to orchestrator.
