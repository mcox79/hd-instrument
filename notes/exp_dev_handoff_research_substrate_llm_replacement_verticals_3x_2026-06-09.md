# exp_dev hand-off -- research: substrate LLM replacement verticals 3x drill

Filed-by: research sub-agent
Date: 2026-06-09
Trigger: notes/research_drill_substrate_llm_replacement_verticals_3x_2026-06-09.md

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by
exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as
implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: legal_full_pipeline_cuad_v1 (rank 1 -- cheapest, strongest ground truth)

Anchor pointer: Research note Section 7, Anchor 1 (LEGAL-FULL-PIPELINE)
Substrate-product reading: End-to-end substrate-primary pipeline on CUAD benchmark. Retrieval
(PP-225) + defeasible rule check (PP-252) + modal classification (PP-253) + Merkle audit (PP-184)
on 100 contract clauses from 10K precedent KB. Zero LLM calls for structured steps.
Tier hint: CPU laptop, ~2 hours. This is the first vertical benchmark -- gates the commercial demo
story. CHEAPEST decisive test for the entire substrate-primary architecture claim.
Why-now: Cycle 200 validated all 4 primitive components individually. This anchor validates them
as an integrated vertical pipeline. CUAD provides clean F1 ground truth. Legal is the nearest-term
commercial vertical per demo priorities.

Pre-reg bands:
  HARD-PASS: retrieval precision@3 >= 0.80 AND defeasible accuracy >= 0.80 AND p95 latency <= 50ms,
             zero LLM calls for structured classification steps
  MIDDLE-BAND: F1 = 0.65-0.80 (retrieval or rule accuracy partially degraded; encoder fine-tuning
               may be required)
  HARD-FAIL: F1 < 0.60 on clause classification OR pipeline requires LLM call for any structured
             classification step (would mean substrate-primary claim needs qualification)

### Anchor 2: healthcare_ddi_hipaa_pipeline_v1 (rank 2 -- strongest compliance claim)

Anchor pointer: Research note Section 7, Anchor 2 (HEALTHCARE-FULL-PIPELINE)
Substrate-product reading: DDI checking (PP-225 retrieval + PP-253 modal) + Bayesian risk
aggregation (PP-246) + HIPAA audit trace (PP-228) + multi-tenant PHI isolation. DrugBank or
FDA Orange Book as KB. Measures DDI sensitivity/specificity + confirms zero PHI exfiltration
+ HIPAA audit trace present per query.
Tier hint: CPU laptop, ~3 hours. Must validate multi-tenant isolation algebraically (no cross-
tenant leakage under adversarial queries).
Why-now: HIPAA compliance by architecture (algebraic isolation vs LLM policy-only) is substrate's
most defensible categorical claim in any vertical. Needs benchmark validation before any customer
conversation in healthcare.

Pre-reg bands:
  HARD-PASS: DDI sensitivity >= 0.90 on FDA Orange Book interactions AND HIPAA audit trace present
             per query AND cross-tenant leakage = 0 under 1000 adversarial queries
  MIDDLE-BAND: DDI sensitivity = 0.75-0.90 (some DDI classifications incorrect; KB completeness
               issue rather than mechanism failure)
  HARD-FAIL: DDI sensitivity < 0.75 OR any cross-tenant information leakage detected (1 or more
             cross-tenant retrievals from adversarial query set)

### Anchor 3: substrate_primary_latency_comparison_v1 (rank 3 -- table-stakes metric)

Anchor pointer: Research note Section 7, Anchor 4 (SUBSTRATE-PRIMARY-LATENCY-COMPARISON)
Substrate-product reading: Head-to-head latency: substrate-primary vs GPT-4o-mini API on identical
100-query legal clause analysis batch. Measures p50/p95/p99 latency per query and total wall time.
Tier hint: CPU laptop (substrate) + API calls (LLM), ~1 hour. Cheapest differentiator metric.
Why-now: Enterprise buyers will demand latency comparison before evaluating further. Run this early
to anchor the commercial conversation.

Pre-reg bands:
  HARD-PASS: substrate p95 latency < 100ms AND LLM p95 > 500ms (>5x improvement demonstrated)
  MIDDLE-BAND: substrate p95 = 100-250ms (still faster than LLM but less dramatic)
  HARD-FAIL: substrate p95 > 500ms (performance parity with LLM; no differentiation; infrastructure
             issue to diagnose)

### Anchor 4: substrate_primary_cost_comparison_v1 (rank 4 -- commercial model validation)

Anchor pointer: Research note Section 7, Anchor 5 (SUBSTRATE-PRIMARY-COST-COMPARISON)
Substrate-product reading: Compute cost per query comparison at 3 scales (100, 10K, 1M queries).
Measures: substrate compute time/cost vs LLM API pricing at each scale. Calculates break-even point.
Tier hint: ~30 minutes (timing + accounting calculation; no GPU needed).
Why-now: Cost model determines the commercial positioning. If break-even is above 10M queries, the
cost argument only applies to large enterprises. Need to know before building the commercial deck.

Pre-reg bands:
  HARD-PASS: substrate $/query < 0.01x LLM $/query at 10K+ scale AND break-even < 1M cumulative
             queries (cost advantage is accessible to mid-market, not just large enterprise)
  MIDDLE-BAND: break-even = 1M-10M queries (cost advantage real but only large enterprise)
  HARD-FAIL: substrate setup cost exceeds 6 months of LLM savings at 100K queries/month (cost
             advantage not commercially meaningful at realistic volumes)

### Anchor 5: finance_full_pipeline_sec_v1 (rank 5 -- third vertical)

Anchor pointer: Research note Section 7, Anchor 3 (FINANCE-FULL-PIPELINE)
Substrate-product reading: SEC 10-K risk analysis + SOX audit on EDGAR filings. PP-225 retrieval
+ PP-252 defeasible (SEC rule compliance) + PP-246 Bayesian (materiality scoring) + PP-184 Merkle
(SOX audit trace) + multi-tenant fund isolation.
Tier hint: CPU laptop, ~3 hours. Requires EDGAR filing sample KB (can be constructed from public
SEC EDGAR in ~1 hour).
Why-now: Finance vertical completes the first-priority commercial trifecta (legal + healthcare +
finance). Third anchor in sequence; run after Anchors 1-2 validate the pipeline architecture.

Pre-reg bands:
  HARD-PASS: recall >= 0.80 on EDGAR risk entity annotation AND SOX audit trace present AND
             cross-fund isolation passes adversarial query test
  MIDDLE-BAND: recall = 0.65-0.80 (free-form narrative sections require LLM extraction layer)
  HARD-FAIL: recall < 0.65 OR cross-fund leakage detected

---

## Context pointers (file paths, not summaries)

- Research note (this drill):
  d:/AI/hd-instrument/notes/research_drill_substrate_llm_replacement_verticals_3x_2026-06-09.md
- Prior compliance drill:
  d:/AI/hd-instrument/notes/research_drill_compliance_maximization_2x_2026-06-09.md
- Prior hard reasoning drill:
  d:/AI/hd-instrument/notes/research_drill_substrate_hard_reasoning_2x_2026-06-09.md
- Prior multihop drill:
  d:/AI/hd-instrument/notes/research_drill_multihop_maximization_2x_2026-06-09.md
- Prior HOL/ToM drill:
  d:/AI/hd-instrument/notes/research_drill_HOL_meta_reasoning_biology_3x_2026-06-09.md
- North Star memory:
  C:/Users/marsh/.claude/projects/d--AI/memory/north_star_functional_system_beats_LLMs.md
- Exp-Dev post-compaction brief:
  d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md
- Production architecture lock:
  C:/Users/marsh/.claude/projects/d--AI/memory/production_architecture_locked_2026-06-07.md

---

## Contract section

This handoff proposes 5 anchor candidates. Exp_dev selects from these based on current queue state,
runner availability, and pause flag. Exp_dev does NOT need to implement all 5.

SEQUENCING CONSTRAINT: Run Anchor 1 (legal) first. It validates the pipeline architecture that
Anchors 2 and 5 depend on. Anchors 3 and 4 (latency + cost comparison) can run in parallel with
Anchor 1 since they do not depend on its outcome.

GATE: Anchor 8 in the research note (HEAD-TO-HEAD-VERTICAL-VS-FRONTIER-LLM) requires Anchors 1-3
to complete first for substrate-side results. Do not dispatch Anchor 8 until those are in.

GATING NOTE for Anchor 6 (scientific/arXiv): the research note ranks scientific pipeline as Anchor
6 and notes it is gated on arXiv KB extraction completing. Check data/orchestrator_status_log.jsonl
for arXiv extraction status before dispatching scientific pipeline anchor.

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which of the 5 anchors to dispatch first (subject to sequencing constraint above)
- Choosing KB sample size (e.g., subset of CUAD, subset of DrugBank) for initial smoke runs
- Choosing encoder for initial runs (recommend sentence-transformers/all-MiniLM-L6-v2 as baseline;
  domain-specific encoder upgrade is a second-pass decision after baseline established)
- Choosing cell grid dimensions, seed counts, and parameter values for each anchor
- Routing to CPU laptop for all 5 anchors (no GPU required; none use torch.cuda per dispatch rules)

Exp_dev is NOT autonomous in:
- Making cap_map decisions from verdicts (orchestrator / verdict_handler owns this)
- Making customer-facing claim revisions (orchestrator owns after verdicts are in)
- Committing to a commercial vertical prioritization based on these results (strategy owns this)
- Reopening the PRODUCTION ARCHITECTURE LOCK (requires explicit user authorization)
