# exp_dev hand-off -- research: cross-domain new mechanism 5x

Filed-by: research sub-agent
Date: 2026-06-10
Trigger: notes/research_drill_cross_domain_new_mechanism_5x_2026-06-10.md
Urgency: HIGH -- P9 retracted; entity-geometry confound confirmed; 3 substrate-native revival paths with P_deflated 0.40-0.45; cheapest test ~2 hr laptop CPU

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered by P_deflated)

### Anchor 1: SLIPNET-SUBSTRATE (P_deflated = 0.45; ~2 hr CPU, laptop)

Anchor pointer: Research note Section B1 + F2.10 + F3 Test 1
Substrate-product reading: Hofstadter-style spreading activation over FHRR role atoms. Domain-general role atoms (DOMINATES, COOPERATES, FEEDS-ON, MANAGES, etc.) stored as FHRR keys. Spreading activation = weighted superposition of neighbor bundles. Query: inject a source-domain relation triple; measure whether the structurally analogous target-domain triple rises above noise floor via role-key activation. This is substrate-native, requires no LLM, and inverts the entity-geometry confound by using role subspace as the primary signal.
Tier hint: Laptop CPU, pure FHRR operations, ~2 hours. Cheapest decisive test for the new mechanism class.
Why-now: This is the highest P_deflated path that (a) requires no LLM, (b) uses only existing substrate operations, (c) directly addresses the entity-geometry confound in D3.1/P9, and (d) has a 30-year empirical track record in cognitive analogy (Copycat). Three independent streams (biology, brain, physics) converge on role-structure as the correct primary signal. If HARD-PASS, the product has substrate-native cross-domain analogy.

Pre-reg bands:
  HARD-PASS: correct target-domain counterpart at rank <=3 in 15 of 20 trials across 2 domain pairs
  MIDDLE-BAND: rank 4-5 in 10-15 of 20 trials (spreading partially focused; iterate on slipnet topology)
  HARD-FAIL: rank >5 in more than 12 of 20 trials, or activation spreads uniformly (no focus)

### Anchor 2: OT-DOMAIN-ALIGN (P_deflated = 0.42; ~4 hr CPU, laptop)

Anchor pointer: Research note Section C3 + F2.3 + F3 Test 2
Substrate-product reading: Gromov-Wasserstein optimal transport between FHRR relational distance matrices. Source domain: D_s[i,j] = FHRR distance between role-bindings of entity i and entity j. Target domain: D_t[i,j] similarly. GW coupling = the analogy mapping. GW is off-the-shelf (POT library); the substrate contribution is the FHRR-distance relational matrix representation. Cross-domain alignment is obtained without entity-level similarity comparison.
Tier hint: Laptop CPU, FHRR distances + POT GW solver. ~4 hours. Second-cheapest decisive test.
Why-now: GW is a principled, well-studied method for cross-metric-space alignment. The substrate-FHRR-distance representation is novel but algebraically direct. If HARD-PASS (delta > 0.10 between analogous and random domain pairs), the product has a principled domain-alignment score that is interpretable (coupling matrix is the analogy mapping).

Pre-reg bands:
  HARD-PASS: GW_distance(analogous pairs) - GW_distance(random pairs) > 0.10 normalized, across 3 domain pairs
  MIDDLE-BAND: delta 0.02-0.10 (partial structural signal; refine relational distance metric)
  HARD-FAIL: delta < 0.02 (GW does not distinguish analogous from random; relational matrix does not capture structure)

### Anchor 3: SHEAF-SUBSTRATE (P_deflated = 0.40; ~3 hr CPU, laptop)

Anchor pointer: Research note Section C4 + F2.4 + F3 Test 3
Substrate-product reading: Sheaf consistency check on partial FHRR structural matches. Each local subgraph binding = a section. The consistency radius measures how close to globally consistent the local matches are. If consistency radius is low, local sections glue to a valid global analogy. Reuses existing bundle cleanup operations; no new substrate primitives needed.
Tier hint: Laptop CPU, ~3 hours. Third-cheapest decisive test.
Why-now: If HARD-PASS (consistency radius < 0.30 for analogous pairs), the product gains an auditable quality score for cross-domain analogy: "this analogy is globally consistent / locally inconsistent in 3 of 5 subgraphs." This is a differentiating product capability (no LLM can currently produce auditable analogy quality scores).

Pre-reg bands:
  HARD-PASS: consistency radius < 0.30 for analogous domain pairs; > 0.50 for random domain pairs (separation >=0.20)
  MIDDLE-BAND: consistency radius in [0.30, 0.50] for analogous pairs (partial gluing; refine local section definitions)
  HARD-FAIL: consistency radius > 0.50 for ALL pairs including analogous (no structural consistency signal)

### Anchor 4: ROLE-KEY-SHARED-CODEBOOK (P_deflated = 0.38; ~1 hr CPU, laptop)

Anchor pointer: Research note Section E4 + F3 Test 4
Substrate-product reading: Empirically validates that domain-general role atoms (10 pre-defined) enable cross-domain retrieval by construction. Bind 3 domains using the same role keys; query with source-domain filler; measure whether target-domain filler is retrieved via shared role key. This is a codebook design validation, not a new mechanism -- it validates that the FHRR binding algebra supports cross-domain reuse when role atoms are domain-general.
Tier hint: Laptop CPU, ~1 hour. Prerequisite for all other anchors (if this fails, shared role key architecture is invalid).
Why-now: Should be run FIRST as a prerequisite check before the more expensive anchors. Very cheap; high information value. If HARD-FAIL, all role-structure paths above are invalidated.

Pre-reg bands:
  HARD-PASS: top-1 retrieval accuracy >= 0.50 across 30 queries; top-3 >= 0.75
  MIDDLE-BAND: top-1 in [0.30, 0.50] (role keys partially shared; refine codebook organization)
  HARD-FAIL: top-1 <= 0.20 (no better than random; shared role key architecture does not work)

### Anchor 5: UNIVERSALITY-CLASS-EXPONENT (P_deflated = 0.30; ~4 hr CPU)

Anchor pointer: Research note Section D2-D3 + F3 Test 5
Substrate-product reading: Measure recall-vs-load capacity cliff exponents in two structurally analogous domains embedded in substrate codebooks. Test whether exponents match. If yes, domains are in the same structural universality class, and cross-domain analogy is possible by construction (same fixed point under coarse-graining).
Tier hint: Laptop CPU or remote_cpu_queue, ~4 hours. Lower priority than Anchors 1-4.
Why-now: Novel empirical prediction that is uniquely testable on the substrate. If HARD-PASS, provides a principled similarity metric that requires no entity comparison, only capacity measurement.

Pre-reg bands:
  HARD-PASS: exponent ratio in [0.90, 1.10] for analogous pairs; > 1.25 for random pairs
  MIDDLE-BAND: exponent ratio in [0.75, 1.25] (weak signal; increase N to sharpen cliff)
  HARD-FAIL: exponent ratio outside [0.75, 1.25] for analogous pairs (no universality-class signal)

---

## Suggested dispatch order

1. Anchor 4 (ROLE-KEY prerequisite check, ~1 hr): run first. If HARD-FAIL, re-route to Research for codebook architecture revision before proceeding.
2. Anchor 1 (SLIPNET-SUBSTRATE, ~2 hr): run second if Anchor 4 passes. Highest P_deflated.
3. Anchor 2 (OT-DOMAIN-ALIGN, ~4 hr): run third. Can run in parallel with Anchor 1 if runner available.
4. Anchor 3 (SHEAF-SUBSTRATE, ~3 hr): run fourth. Can batch with Anchor 2.
5. Anchor 5 (UNIVERSALITY-CLASS, ~4 hr): run last; requires Anchors 1-3 outcome context.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_cross_domain_new_mechanism_5x_2026-06-10.md
- Prior failed attempts (entity-geometry confound): d:/AI/hd-instrument/notes/research_drill_cross_domain_analogy_negative_2x_2026-06-10.md
- Prior revival handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_cross_domain_revival_3x_2026-06-10.md
- Field advisor output: top candidates are free-probability and semiconductor (orthogonal to this drill; no conflict)

---

## Contract

exp_dev MUST:
- Check data/orchestrator_paused.flag before dispatching any cell
- Run Anchor 4 first as a prerequisite check
- Pre-register all cells with explicit HARD-PASS / MIDDLE-BAND / HARD-FAIL bands before dispatch
- Report back to Research if Anchor 4 HARD-FAILs (codebook architecture needs revision)
- Do NOT treat the anchor descriptions above as implementation specs -- design the cell grids from the research note + cap_map context

---

## Autonomy declaration

exp_dev has full autonomy to:
- Order anchors within the suggested dispatch sequence
- Design cell grids (N, codebook size, domain pair selection) appropriate to laptop CPU capability
- Batch Anchors 2+3 if runner capacity allows
- Halt the sequence and escalate to Research if any anchor produces an ambiguous (MIDDLE-BAND) result that changes the interpretation of subsequent anchors
