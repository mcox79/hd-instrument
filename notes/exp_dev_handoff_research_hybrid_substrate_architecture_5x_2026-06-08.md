# exp_dev hand-off -- research: hybrid native-discrete + non-native-fuzzy substrate architecture

Filed-by: research sub-agent (2026-06-08)
Trigger: notes/research_drill_hybrid_substrate_architecture_5x_2026-06-08.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

Substrate has been empirically validated in two storage regimes:
- NATIVE (discrete rho=0.0): K-hop recall@2 = 0.80; with mild rho=0.5 = 0.93
- FUZZY (rho=0.9): K-hop recall@2 = 0.33 (collapse)
- Single-shot fuzzy (bge-small attention) = 0.501 (not statistically different from RAG 0.524)

The research drill (Level 1-5, 5x depth) identifies that native dominates on 4/8 query types
(bridge multi-hop, comparison, temporal, counterfactual) and fuzzy dominates on 2/8 (factoid,
synthesis). A hybrid routing architecture combining both is the minimum viable production design.

Five routing strategies are evaluated; cascade-native-first and two-stage entity disambiguation
are the cheapest and best-evidenced paths to immediate improvement. RL routing is the ceiling
but has higher engineering cost.

The critical bottleneck: the paraphrase failure mode has not been quantified on substrate.
If native K-hop degrades significantly when query entity names are paraphrased, then the
two-stage fuzzy-identification + native K-hop pipeline is the highest-priority improvement.

---

## Anchor Candidates (rank-ordered by P_actionable x engineering cost)

### 1. Anchor E -- Paraphrase degradation baseline (HIGHEST PRIORITY, cheapest gate)

Anchor pointer: HYBRID-PARAPHRASE-E1 (new; not yet queued)
Substrate-product reading: Quantifies whether native K-hop recall@2 degrades when query
  uses paraphrase or alternate entity names vs exact stored entity names. This determines
  whether Anchors B and C (entity disambiguation) are justified.
Tier hint: CPU laptop; ~30-60 min wall; no cloud; no new substrate changes
Why-now: This is the cheapest decision gate in the hybrid battery. If paraphrase degradation
  is < 5pp, skip entity disambiguation anchors entirely. If >= 20pp, entity disambiguation
  is the highest-priority improvement in the hybrid battery.

Setup guidance for exp_dev:
  Build a small query set (n=50 minimum) where each query has:
  (a) exact entity name version (matches stored binding string exactly)
  (b) paraphrase version (uses alternate name, abbreviation, or partial match)
  Run native K-hop on both. Measure recall@2 difference.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: native recall@2 drops >= 20pp on paraphrase vs exact
             (paraphrase failure mode is real; Anchors B and C justified)
  HARD-FAIL: native recall@2 within 5pp on paraphrase vs exact
             (paraphrase is not a real failure mode; skip Anchors B and C)
  MID-BAND: 5-20pp degradation (partial problem; may still justify entity disambiguation)

### 2. Anchor A -- RRF fusion of native K-hop + fuzzy embedding on mixed query benchmark

Anchor pointer: HYBRID-RRF-A1 (new; not yet queued)
Substrate-product reading: Validates whether RRF(native, fuzzy) achieves >= max(native, fuzzy)
  across a mixed query type benchmark. This is the cheapest validation of the hybrid thesis
  before committing to routing architecture.
Tier hint: CPU laptop; ~1-2 hours wall; requires writing fusion wrapper; no substrate changes
Why-now: Activates after Anchor E establishes paraphrase failure mode magnitude.
  If Anchor E is HARD-PASS or MID-BAND, run Anchor A in parallel with Anchor B.
  If Anchor E is HARD-FAIL, Anchor A is still worth running (RRF may still help on other
  query types even without paraphrase problem).

Benchmark composition guidance for exp_dev:
  Include at minimum: 20 factoid, 20 bridge multi-hop, 10 temporal, 10 counterfactual queries.
  Use existing substrate test sets where available.

Pre-reg bands:
  HARD-PASS: RRF recall@2 >= max(native, fuzzy) + 5pp on bridge multi-hop AND
             no degradation on factoid (within 2pp of fuzzy baseline)
  HARD-FAIL: RRF recall@2 < native-alone on bridge multi-hop (fusion dilutes native advantage)
  MID-BAND: RRF >= max on multi-hop but >= 5pp degradation on factoid vs fuzzy-alone
            (alpha-tuned RRF needed; try alpha in [0.3, 0.5, 0.7])

### 3. Anchor B -- Cascade native-first with confidence signal routing

Anchor pointer: HYBRID-CASCADE-B1 (new; not yet queued)
Substrate-product reading: Tests whether substrate's own activation signal (entropy of
  activation distribution OR margin = max_activation - second_max_activation) predicts
  retrieval success reliably enough for cascade routing without external classifier.
Tier hint: CPU laptop; ~2-4 hours wall; requires logging per-query confidence signal
Why-now: Activates after Anchor A validates fusion. This is the cheapest path to
  principled routing without a trained external classifier.

Pre-reg bands:
  HARD-PASS: AUROC of confidence signal vs retrieval success >= 0.70
             (cascade routing is viable at this discrimination level)
  HARD-FAIL: AUROC < 0.60 (confidence signal is uninformative; must use external classifier)
  MID-BAND: AUROC in [0.60, 0.70] (threshold-based cascade marginally viable;
            consider Anchor D -- entropy routing -- for additional signal)

Confidence signals to test:
  (a) Activation margin: max_activation - second_max_activation (simpler)
  (b) Activation entropy: -sum(p_i * log(p_i)) over normalized activations
  Test both; report which has higher AUROC and at what threshold precision/recall.

### 4. Anchor C -- Two-stage entity disambiguation + K-hop

Anchor pointer: HYBRID-TWOSTAGE-C1 (new; not yet queued)
Substrate-product reading: Tests whether fuzzy retrieval of candidate entities (entity
  disambiguation, paraphrase handling) followed by native K-hop from those entities
  outperforms native K-hop from exact-string entity parse on paraphrase-heavy queries.
Tier hint: CPU laptop; ~2-4 hours wall; requires integrating fuzzy entity lookup with
  native K-hop launcher
Why-now: Prerequisite: Anchor E HARD-PASS (paraphrase degradation >= 20pp confirmed).
  If Anchor E is HARD-FAIL, skip Anchor C.

Pre-reg bands:
  HARD-PASS: Two-stage recall@2 >= native-from-exact + 10pp on paraphrase queries AND
             two-stage recall@2 >= 0.80 on bridge multi-hop
  HARD-FAIL: Two-stage introduces more false positives than it recovers on paraphrase queries
             (net negative vs native-from-exact)
  MID-BAND: Two-stage recovers 5-10pp on paraphrase but reduces precision by >= 10pp

### 5. Anchor D -- Binding entropy routing correlation pretest

Anchor pointer: HYBRID-ENTROPY-D1 (new; not yet queued)
Substrate-product reading: Tests whether substrate activation entropy correlates with
  correct regime selection (native vs fuzzy) on a labeled query set. If correlation >= 0.40,
  entropy-based self-routing is viable without external classifier.
  This is the novel Level 5.1 architecture from the research drill.
Tier hint: CPU laptop; ~1 hour wall; single forward pass + entropy calculation; very cheap
Why-now: Can run in parallel with Anchor A (independent). Lowest investment, highest novelty.
  If HARD-PASS, enables self-routing substrate with no external classifier overhead.

Pre-reg bands:
  HARD-PASS: Pearson r >= 0.40 between activation entropy and routing correctness on
             >= 50 labeled queries; p-value < 0.05
  HARD-FAIL: r < 0.20 (entropy is uninformative; external classifier is required)
  MID-BAND: r in [0.20, 0.40] (entropy partially informative; combine with margin signal)

---

## Dispatch priority order

Step 1 (immediate, parallel):
  - Anchor E (paraphrase baseline, ~30-60 min)
  - Anchor D (entropy correlation, ~1 hour)
  Both are independent and can run simultaneously.

Step 2 (after Anchor E result):
  - If Anchor E HARD-PASS: run Anchor A AND Anchor C in parallel
  - If Anchor E HARD-FAIL: run Anchor A only (skip C)
  - If Anchor E MID-BAND: run Anchor A; hold Anchor C decision

Step 3 (after Anchor A result):
  - If Anchor A HARD-PASS: run Anchor B
  - If Anchor A MID-BAND: run Anchor B with alpha-tuned RRF
  - If Anchor A HARD-FAIL: escalate to orchestrator (hybrid fusion is net-negative;
    routing-only architecture required)

Anchors A through E are all CPU laptop tier. No cloud dispatch needed for any of them.
Total estimated wall time for full battery: ~8-12 hours sequential, ~4-6 hours parallel.

---

## Strategic context for exp_dev

The hybrid architecture directly supports the North Star mandate (v1 demo that beats LLMs
of relative size). The clearest demo path is:
  - Bridge multi-hop queries: substrate hybrid >= GPT-4 RAG
  - Single-hop factoid: substrate hybrid matches standard RAG
  - Temporal queries: substrate hybrid >> RAG (RAG has no temporal native support)

These three dimensions together constitute a compelling head-to-head comparison.

The auditability angle (architecture 4.4 in research note) does not require experiments --
it is a product architecture decision. Flag to orchestrator when the hybrid battery completes.

Multi-hop revival: the two-stage disambiguation (Anchor C) is one of the viable multi-hop
revival paths listed in project_multihop_revive_priority.md. Route Anchor C results to
verdict_handler for multi-hop revival assessment.

---

## Context pointers

- Research note (full 5x analysis, Levels 1-5):
  d:/AI/hd-instrument/notes/research_drill_hybrid_substrate_architecture_5x_2026-06-08.md
- Empirical baseline (iterative regime crossover):
  Look for exp_iterative_regime_crossover_cpu_v1 in data/exp_*/metrics.json
- Empirical baseline (PP-99 single-shot fuzzy):
  Look for PP-99 in data/exp_*/metrics.json or cycle 178 notes
- Substrate cap_map:
  d:/AI/hd-instrument/data/substrate_capability_map.md
- Multi-hop revival priority:
  C:/Users/marsh/.claude/projects/d--AI/memory/project_multihop_revive_priority.md
- North Star:
  C:/Users/marsh/.claude/projects/d--AI/memory/north_star_functional_system_beats_LLMs.md

---

## Contract section

This hand-off is research-to-experiment. The 5 anchor specs (A-E) are provided as pre-reg
recommendations. Exp_dev is responsible for:
- Validating pre-reg bands before dispatch (adjust if empirical baseline differs)
- Building the mixed query benchmark (factoid / multi-hop / temporal / counterfactual)
- Implementing the fusion wrapper (RRF, alpha-tuned hybrid)
- Implementing the confidence signal logging (entropy, margin)
- Assigning to correct queue (all anchors are CPU laptop tier)
- Writing verdict notes for each anchor per standard protocol
- Escalating HARD-PASS results on Anchors A/B/C to orchestrator for hybrid architecture
  confirmation and cap_map update
- Routing Anchor C results to multi-hop revival thread (project_multihop_revive_priority.md)

## Autonomy declaration

Exp_dev may dispatch Anchors D and E immediately without orchestrator approval (both are
CPU pretest, < 1 hour, independent). Anchors A, B, C may be dispatched based on Anchor
E results per the priority order above -- no additional orchestrator approval needed for
CPU laptop anchors within the pre-reg bands specified.

If any anchor produces a HARD-FAIL that would refute the hybrid thesis (Anchor A HARD-FAIL:
RRF is net-negative on multi-hop), escalate to orchestrator before continuing the battery.
