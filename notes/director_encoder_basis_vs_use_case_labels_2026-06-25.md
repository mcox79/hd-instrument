# Strategic principle — encoder BASIS unsupervised; LABELS allowed at use-case layer

USER directive 2026-06-25: "we can ALWAYS have labels on cells for particular use cases, but I agree the basis shouldn't use a label it should do what biology does"

## The principle (load-bearing)

**Two-layer encoder architecture:**

1. **BASIS LAYER (substrate's foundational representation)**
   - UNSUPERVISED only
   - Biology-native mechanisms: Olshausen-Field sparse coding / DeepWalk-on-graph-edges / SOM / k-WTA / SoftHebb / Foldiak anti-Hebbian
   - Structure EMERGES from input statistics, graph connectivity, temporal coherence, competition, sparseness
   - NO imposed taxonomy / NO category labels / NO supervision

2. **USE-CASE LAYER (labeled readouts on top of unsupervised basis)**
   - Labels FINE here — classification heads, category queries, refuse-gate thresholds, audit-trail tags
   - Brain analog: IT / ATL / hippocampal place-cell-labeling
   - These don't CONSTRUCT the representation; they ATTACH to it for specific tasks

## Brain existence proof

- V1 simple cells emerge from natural-image statistics via unsupervised plasticity (Olshausen-Field 1996). NO labels.
- IT face/object cells emerge from temporal coherence + sparse coding on V1/V4 inputs. NO labels.
- ATL hub-spoke concept cells: hub emerges from cross-modal binding; spokes self-organize. Labels can be ATTACHED to atoms (e.g., a particular concept atom "fires for" a labeled category) but the atom's existence and structure is UNSUPERVISED.
- Hippocampal place cells: emerge from spatial experience. CAN be cued by labeled landmarks but the place-cell itself is not "labeled" — it's a substrate phenomenon.

## What this changes for substrate

### What to REMOVE from substrate encoder
- Label-driven axis-projection (Cell 7 v1 mechanism) — DROP. Lost to random-bipolar; commits to wrong taxonomy.
- Concept-KG categories used as encoder bases — DROP. Categories may be wrong; substrate inherits the taxonomy's mistakes.

### What to KEEP in substrate encoder
- Sparse-bipolar f=0.02 (already chain-grade; matches brain k-WTA ~5%)
- 1-bit bipolar with 1/√f amplitude (chain-grade primitive)
- Plate role-tagged HRR binding (algebraic primitive; not a label)
- Append-only growth (CRISPR-style CL)

### What to ADD to substrate encoder (per biology)
- Olshausen-Field sparse coding on co-occurrence (text or KG)
- DeepWalk-on-substrate-KG (uses graph EDGES, not LABELS; community structure emerges)
- SOM / k-WTA topographic competition
- SoftHebb hierarchy (forward-only Bayesian generative)
- Foldiak anti-Hebbian lateral inhibition for decorrelation

### Labels are still welcome at USE-CASE layer
- Refuse-gate: label "unknown_concept" → tau threshold; uses substrate's unsupervised similarity to decide
- Audit-trail: label "provenance_tag_X" → bind into atom; uses substrate's unsupervised storage to retrieve later
- Classifier readout: train a small W_classifier on labeled examples (the LABELS are at the W_classifier, not in the base atom encoding)
- Query-by-category: at retrieval time, label "find me all animals" → match against learned category atoms (themselves unsupervised but with attached labels)

## Implications for in-flight work

**Cell H spec update (extended-depth multihop consolidation):**
- Storage primitive (W_k matrices) is base-layer — UNSUPERVISED
- Consolidation policy (which paths to consolidate) is use-case-layer — can use labeled frequency thresholds
- Atom representations themselves: random-bipolar OR Olshausen-Field-learned (NOT label-driven)

**Wave F redispatch (4 bug fixes):**
- Cell 5 (role_tagged_compgen_KG): role-tags ARE labels but they're at the BINDING level (role-binding is Plate algebraic primitive). This is acceptable per the principle: role-tags don't construct the basis; they attach to bound atoms at the use-case layer. KEEP as-is.
- Cell 1 hub-spoke v3 MRC: spokes are biology-native algorithms (SoftHebb, char-trigram-RI, Path-C PC) — UNSUPERVISED basis construction. KEEP.
- Cell 2 heterog routing v3: cf-RPE / STDP / Hebbian are plasticity rules, not labels. KEEP.
- Cell 6 lock-in: frequency-domain separation, not label-driven. KEEP.

**Drop or deprioritize:**
- Wave E Cell D label-driven encoder (already MIDDLE_BAND; per principle, this was the wrong direction). DEPRIORITIZE retest at V=4000.

**Promote:**
- Biology-native unsupervised encoder cell (Cell H proposed by Cell 7 deepened drill): 5-arm shotgun on Olshausen-Field / DeepWalk / SOM / Foldiak / random-baseline. **This is the right Stage 1.5 encoder cell, replacing label-driven exploration.**

## Memory commit

Update bias master checklist with new principle:

### O (NEW 2026-06-25) — Basis vs use-case layer discipline
- **O1**: Substrate encoder BASIS must be unsupervised (biology-native mechanisms; structure emerges from input statistics, graph connectivity, temporal coherence, competition, sparseness)
- **O2**: Labels are welcome at USE-CASE layer (classifier readouts, query-by-category, refuse-gate, audit-trail) — they ATTACH to atoms; do not CONSTRUCT them
- **O3**: When a cell uses labels, declare which layer: BASIS (forbidden; reject) vs USE-CASE (allowed; document the readout architecture)
- **Brain alignment**: V1 unsupervised → IT labeled readout. ATL hub unsupervised → labeled queries on top.

## Strategic implication

The label-driven anisotropic encoder path is closed. The biology-native unsupervised path is open. Cell H (proposed by Cell 7 deepening drill) is the right next encoder cell. Cell 4 consolidation (Cell 4 already chain-grade-pending) is the right Stage 1.5 commit on the orthogonal Barrier 1 axis. These compose:

- Cell 4 (Barrier 1 closer): memory primitive for multi-hop ← orthogonal to encoder choice
- Cell H proposal (Barrier 4 closer): biology-native unsupervised anisotropic encoder ← drops labels at basis layer

Together: substrate with biology-native basis + memory consolidation = the Stage 1.5 architecture worth building.
