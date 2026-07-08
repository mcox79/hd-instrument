# Degree-agnostic sparse-tail relational encoding (brain-first) -- 2026-07-08

**Origin:** revival drill on a CONFIRMED GENUINE NEGATIVE -- SimGRACE (the degree-agnostic fallback for the teacher-free relational encoder) is DEAD: at scale Z~149 ~= lexical floor ~149, below floor 4/5 seeds; the smoke lift did not survive. So we have NO working way to relationally encode the SPARSE / RARE / degree-1 tail of ingested knowledge (a concept with one or zero relational neighbors). Teacher-free works only on the DENSE CN 2-core (median deg 3).

**Process note (director):** the dispatched research agent spawned its own background lit-scan sub-children and then STALLED without reassembling -- a sub-agent-spawning-sub-agents coordination failure. The child lit-scan (a340a1d9) DID land and is captured below; the parent's ranked synthesis did not. LESSON: research-drill prompts must say "do the scan YOURSELF, do NOT spawn sub-agents." Content preserved here by the director.

## Brain-first finding (lit-scan a340a1d9, citations verified in-scan)

The brain's answer to "place a rare / single-exposure / relationally-isolated item so it is still discriminative" is **dentate-gyrus expansion-recoding + sparsification feeding CA3 autoassociation** -- and its separability is **degree-agnostic BY CONSTRUCTION**:

- **DG expand-then-sparsify** (Marr 1971; Treves & Rolls 1991; Bakker et al. 2008 Science; Berron et al. 2016): projects input into a much larger, very sparse (~2-5% active) space. Pattern SEPARATION comes from the expansion + sparsity + near-orthogonality, NOT from contrasting against a dense neighborhood.
- **CA3 as Marr autoassociator** (Nakazawa et al. 2003 Neuron; Liu et al. 2012 Nature): one-shot / single-trial encoding of a novel item via detonator synapses -- a rare item gets a stable, separable engram from ONE exposure, with no relational neighbors required.
- **Capacity/discrimination math** (Tsodyks & Feigel'man 1988; ~1/(a|ln a|), optimal a ~ sparse): governed by sparsity `a`, orthogonality, and network size `N` -- **all independent of the input's relational degree.** This is the crux: SimGRACE tried to manufacture discriminability from graph augmentation (needs neighbors); DG manufactures it from geometry (needs none).
- Recency/interference inhibition (Myers & Scharfman 2009/2011) protects the new sparse code from being overwritten.

**Confidence: MEDIUM-HIGH.** Direct because the capacity mathematics provably does not reference neighbor-count; short of HIGH only because no study isolates "number of relational neighbors" as an independent variable -- support is capacity theory + one-trial novel-item engram studies, not a neighbor-count ablation.

## Buildable conclusion (director synthesis)

**REPLACE SimGRACE with a DG-expansion front-end for the degree-agnostic / sparse-tail regime.** Rank-1, and cheap because the primitive already exists:

1. **DGProjection expand+sparsify front-end (P high; primitive EXISTS, unwired).** The `DGProjection` primitive is already in the codebase (built for the resonator DG-frontend, never wired). Wire it as the teacher-free encoder's sparse-tail front-end: expand -> k-WTA sparsify -> the SAME certified repulsion/InfoNCE term on the sparse code. Discriminability now comes from pattern-separation geometry, so a degree-1 concept gets a separable code without a dense neighborhood. **This is the load-bearing bet.**
2. **Intrinsic/featural view when relational neighbors are absent (P med).** For degree-0/1 items, substitute lexical/contextual/co-occurrence structure as the "positive" signal, expanded through DG -- schema-assisted placement (Tse/Morris systems-consolidation analog).
3. **Novelty-gated privileged encoding (P med-low, later).** DA/NE-style salience tag that raises the effective learning-rate / sparsity budget for surprising rare items (composes with the self-manager dials).

**KILL-TEST (the single sharpest discriminator):** on a held-out set of DEGREE-1 concepts, does DG-expand+sparsify+repulsion produce a code that beats the lexical floor by a real margin (lift, not absolute Z) AND separates degree-1 items as well as degree-3 items -- i.e. is the code quality FLAT across relational degree? If the degree-1 codes collapse to the floor exactly like SimGRACE did, the mechanism has NOT solved the degree-agnostic problem and this is a second genuine negative. Discriminator must FIRE: include a no-expansion control that MUST fail at degree-1.

**GATING:** build after the peel/SIC headline resolves (shares encoder-store infra; don't collide). Then dispatch as an exp_dev cell: DG-expand degree-agnostic teacher-free front-end, 3-arm (SimGRACE-dead-baseline / DG-expand / no-expand-control), sweep by relational degree, primary metric = lift-over-floor FLAT across degree.
