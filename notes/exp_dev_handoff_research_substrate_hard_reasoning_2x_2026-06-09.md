# exp_dev hand-off -- research: substrate hard reasoning extensions (2x drill)

**Filed:** 2026-06-09 by research sub-agent.

**Trigger:** Research drill on substrate hard reasoning extensions (modal, defeasible,
theory-of-mind, paradox, higher-order, analogical, common-sense). 10 levels analyzed.
Multiple categories confirmed tractable with existing Datalog^neg + algebra; several
produce immediately testable anchors.

**Research note path:** d:/AI/hd-instrument/notes/research_drill_substrate_hard_reasoning_2x_2026-06-09.md

**Pause state:** check data/orchestrator_paused.flag before queue dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS
only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice, anchor
name, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered)

### 1. DEFEASIBLE-1 -- default reasoning + exception suppression on ConceptNet
- Anchor pointer: research note Level 2.1-2.2; cheap decisive test Part A.
- Substrate-product reading: Datalog^neg NAF already handles this structurally. The anchor
  is a benchmark proof-of-capability. Load 20 ConceptNet facts + exception pairs; write 3
  layered defeasible rules; verify exception suppression is correct. Zero new engineering.
  Product claim: "substrate handles default reasoning and exceptions natively."
- Tier: LOCAL (ConceptNet already loaded; pure Datalog evaluation; no GPU).
- Why now: P_deflated=0.80 (highest in this batch). Costs near-zero. Immediate differentiator
  from retrieval-only and LLM baselines that do not guarantee exception suppression.

### 2. MODAL-K-1 -- K-modal logic primitives over 5-world Kripke frame
- Anchor pointer: research note Level 1.1-1.2; cheap decisive test Part B.
- Substrate-product reading: encode accessibility relation as facts + 3 box/diamond rules.
  No new algebra. Tests whether substrate can answer "necessarily true in all accessible
  worlds." Product: verifiable modal claims vs LLM probabilistic estimates.
- Tier: LOCAL (small synthetic frame; pure Datalog).
- Why now: P_deflated=0.55-0.65. CONV-11 is ROUTED but unstarted; this smoke either
  validates the CONV-11 engineering path or surfaces blockers before larger investment.

### 3. ANALOGICAL-1 -- structural alignment query on two relational KB partitions
- Anchor pointer: research note Level 6.1-6.4; cheap decisive test Part C.
- Substrate-product reading: encode two small relational domains (5 facts each); write
  homomorphism query (find mapping sigma). Tests whether HD bundle similarity + Datalog
  join correctly implements structural alignment vs surface-feature match.
- Tier: LOCAL or REMOTE-CPU (depends on exp_dev's call on KB partition query cost).
- Why now: P_deflated=0.65. PathHD multi-hop already works; analogical reasoning is the
  next structural generalization. Case-based reasoning product path.

### 4. TOM-1 -- depth-1 and depth-2 theory of mind queries (multi-tenant)
- Anchor pointer: research note Level 3.1-3.3; multi-tenant architecture already present.
- Substrate-product reading: create 3 agent tenants; populate per-agent belief facts;
  write cross-tenant believes() query; test depth-1 (A knows P) and depth-2 (A knows B
  believes P). The multi-tenant isolation layer is already built for GDPR; ToM is a query
  layer on top.
- Tier: LOCAL (small synthetic test; no model training).
- Why now: P_deflated=0.60. Architecture is free -- ToM is a reinterpretation of existing
  multi-tenant, not new code. High product value (legal reasoning, negotiation support).

### 5. PARACONS-1 -- 4-valued paraconsistent Datalog smoke
- Anchor pointer: research note Level 4.4; P-Datalog literature (Aranda et al.) provides
  the engineering recipe (LFI1 + 4-TP alternating fixpoint).
- Substrate-product reading: extend truth carrier from {T,F} to {T,F,U,B}; rewrite the
  consequence operator as 4-monotonic; test: (a) contradictory fact pair returns B without
  propagating, (b) unrelated queries still evaluate correctly.
- Tier: REMOTE-CPU (truth-carrier refactor; needs validation across KB).
- Why now: P_deflated=0.55. Real-world KBs have contradictions; paraconsistent handling
  is a production durability argument. Engineering cost is moderate (1-2 weeks) but the
  ROI is high for enterprise KB products.

### 6. CS-LLM-1 -- head-to-head common-sense comparison (ConceptNet-reachable subset)
- Anchor pointer: research note Level 7.5; KG-LLM-Bench (arXiv 2504.07087) provides
  the benchmark methodology.
- Substrate-product reading: extract CommonsenseQA questions where the correct answer
  is reachable via 2-hop ConceptNet chain. Run substrate Datalog chain vs gpt-4o / Claude
  on the same subset. Expected: substrate wins on in-KB structured questions; honest gap
  documented on out-of-KB questions.
- Tier: REMOTE-CPU (LLM API calls + ConceptNet queries; no GPU training).
- Why now: P_deflated=0.50 (matching substrate on ConceptNet questions). This is the
  North Star alignment anchor: demonstrates "functional system beats LLM on measurable
  subset" as the user-locked goal requires.

### 7. PARADOX-1 -- stratification paradox-rejection verification
- Anchor pointer: research note Level 4.1-4.2; PP-159 stratification proof.
- Substrate-product reading: load Liar-paradox rule (L :- not L); verify: rejected at
  stratification check. Load Russell-pattern; verify: returns undefined under well-founded
  evaluation. Documents existing behavior as a capability claim.
- Tier: LOCAL (analyzer-only; zero new code).
- Why now: P_deflated=0.75 (near-certain pass given stratification already implemented).
  Cost is essentially zero. Converts existing structural property into a documented
  product capability.

### 8. EPISTEMIC-1 -- knows/believes operator on 3-agent synthetic KB
- Anchor pointer: research note Level 1.4 + Level 3.1.
- Substrate-product reading: 3-agent epistemic accessibility frames; knows(Agent, Prop)
  query via forall-accessible-worlds pattern (not-exists counterexample via NAF).
  Tests whether stratified NAF correctly implements universal quantification over
  agent-scoped world sets.
- Tier: LOCAL (small synthetic; pure Datalog).
- Why now: P_deflated=0.60. Prerequisite before deploying TOM in production (EPISTEMIC-1
  is the simpler modal building block under TOM-1).

---

## Context pointers (file paths only)

- Research note (full analysis, 10 levels): d:/AI/hd-instrument/notes/research_drill_substrate_hard_reasoning_2x_2026-06-09.md
- ConceptNet facts loaded state: d:/AI/hd-instrument/notes (see testbed overnight chain
  memory entry -- 458K ConceptNet facts loaded as of 2026-06-09).
- Cap map (current): notes/substrate_capability_map.md (check latest CONV-11/CONV-12/CONV-13 rows).
- PP-159 stratification proof: search notes/ for pp159 or stratification_proof.
- PathHD / PP-226 multi-hop results: notes/ research_POST_COMPACTION_BRIEF_2026-06-07_evening.md.
- Pause state: data/orchestrator_paused.flag (check before dispatch).

---

## Contract

- Pre-reg per envelope-fail-bands: HARD-PASS + HARD-FAIL bands before smoke.
- Self-test per formula-selftests.
- Multi-seed FULL on smoke clearance.
- Queue routing per Tier A/B/C in agents/exp_dev.md Section 0.
- Ship via bash tools/orchestrator/queue_add.sh.
- POST-SHIP REMOTE VERIFY per feedback-ship-name-collision.
- status_log entry per anchor with plain_language + importance.

## Autonomy declaration

exp_dev decides ALL of: anchor name, N, M, K, seed count, threshold bands
(HARD-PASS + HARD-FAIL), queue choice (Tier A/B/C), ETA, smoke profile, FULL profile,
and whether to group anchors into a single run or sequence them. Research passes POINTERS
only. If exp_dev wants to substitute a different anchor from this list or reorder based on
current queue state, that is exp_dev's call.

---

## Filed by

Research sub-agent (Sonnet 4.6), 2026-06-09. Research-to-experiment feed is structural
via this file (auto-discovered by exp_dev on emergency-refill cycles via notes/exp_dev_handoff_*.md
sorted by mtime).
