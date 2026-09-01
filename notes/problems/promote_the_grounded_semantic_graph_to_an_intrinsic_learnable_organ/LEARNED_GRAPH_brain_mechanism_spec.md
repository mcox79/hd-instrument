# The LEARNED / growing semantic-graph organ -- EXACT brain mechanism + buildable spec (north-star follow-on)

Companion to the READ organ (competitive attractor settling). This is the WRITE/LEARN side: how the brain
GROWS, TUNES, and CARVES the semantic network the settling reads. From a deep literature drill (2026-09-01).
Tags: [PINNED] brain-fixed | [MODELLED] a specific model instantiating a pinned mechanism | [OUR-INVENTION] sweep.

## THE MECHANISM (what the brain actually does)
1. **Complementary Learning Systems [PINNED].** FAST hippocampal one-shot, pattern-SEPARATED store (keeps a new
   sense distinct, = fast mapping, Carey) + SLOW neocortical distributed graph (interleaved, extracts structure).
   A single fast-learned distributed net suffers CATASTROPHIC INTERFERENCE (McClelland/McNaughton/O'Reilly 1995) --
   the only stable fix is fast-separate-store + REPLAY/INTERLEAVE into the slow net.
2. **Schema-gated fast cortical learning [PINNED] (Tse 2007/2011; McClelland 2013) -- THE key knob.** If a new
   item is SCHEMA-CONSISTENT with existing knowledge, neocortex integrates it FAST + safely (~48h, hippocampus-
   independent); if INCONSISTENT it must stay slow/interleaved. Cortical learning RATE is prior-knowledge-dependent.
   (Rodd & Davis 2012, ON OUR TASK -- new meaning for an existing word: fragile immediately, needs OVERNIGHT
   consolidation to become a stable competitor; semantic RELATEDNESS facilitates = schema-consistency.)
3. **Senses = regions of a CONTINUOUS space, NOT a discrete list [PINNED] (Rodd).** Granularity is emergent basin
   GEOMETRY. Homonymy = distant non-overlapping basins -> compete -> disadvantage; polysemy = overlapping basins
   -> mutual support -> advantage. OWN-GRANULARITY = SPLIT when a form's usages become contextually SEPARABLE,
   MERGE when basins overlap/co-occur. Usage-based (Srinivasan 2019: children use one sense to bootstrap the next).
   Engineering analog = nonparametric sense induction (Neelakantan 2014 threshold; Li & Jurafsky 2015 CRP; AdaGram).
4. **Learning rules.** Edges = BCM/XCAL co-activation `Δw = η·a_i·a_j·(a_j - θ_M)`, θ_M = ⟨a_j²⟩ sliding threshold
   (LTP+LTD, self-normalizing, no runaway) [MODELLED, well-supported; O'Reilly Leabra = Hebbian + error-driven in
   one rule]. Resting level = `r_s = r_0 + β·log(1+f_s)` (frequency -> basin DEPTH -> dominance) [PINNED behavior,
   MODELLED form]. Cross-situational accumulation (Yu & Smith 2007) [PINNED] = the evidence gate before a sense
   crystallizes. SHARED divisive-normalization pool for read AND write (bounds weight/depth runaway for free).

## BUILDABLE SPEC (minimal faithful; composes with the settling READ organ)
SUBSTRATE ROLE MAP: co-occurrence store + learner recent-buffer = the FAST pattern-separated store; the WordNet++
settling graph = the SLOW cortical store; **the consolidation organ = replay/interleaving -- WIRE IT to READ the
fast store and WRITE back to the settling graph (this fixes the flagged "cleaned store written-but-never-read"
bug = the real completion, not bookkeeping)**; schema-gate = relatedness of a candidate sense/edge to its graph
neighborhood. Context vectors `c` = reuse the (unwired) `distributional_meaning_channel` or the reader extraction.
- **(a) SPLIT/create:** token context `c`, form `w`; `s* = argmax_s cos(c, μ_s)`. If `cos < τ_split` -> fast-map a
  TENTATIVE new sense `μ_new=c` (one-shot); else assign + update prototype + increment `f`. PROMOTE tentative ->
  real node only after k cross-situational confirmations AND a schema-consistency check (fast rate if consistent).
- **(b) TUNE:** edges via BCM/XCAL; resting levels via log-frequency; bounded by the shared normalization.
- **(c) CONSOLIDATE (offline):** MERGE senses if `cos(μ_a,μ_b) > τ_merge` AND contexts non-separable; PRUNE edges
  `w < θ_prune` + low recent co-activation; INTERLEAVED replay of existing items when writing new ones (anti-interference).
- **Params (5):** τ_split [OUR-INVENTION], τ_merge [OUR-INVENTION], η_fast/η_slow RATIO (kind PINNED: hippo >> cortex,
  schema raises cortical rate; magnitude sweep), θ_M (self-adjusting, NOT a swept constant), k confirmations [sweep].

## CAN-FAIL TEST (fair, one-variable, brain-metric)
- PRIMARY: learned graph must improve SETTLING-WSD on HELD-OUT MODERN text over the static WordNet++ graph,
  CI-separated over the static upper bound (+ CI half-width + null p95); recompute floor on the held-out population.
- INFO-FREE TWIN (must LOSE): add the SAME number of nodes/edges by SHUFFLED co-occurrence / random attachment.
- GATE ABLATION (must show interference): remove the schema-consistency gate + integrate everything fast ->
  WSD on OLD words should DEGRADE (catastrophic interference) -- proves the gate does the CLS work.
- EMERGENT SIGNATURES that must fall out UNBID (faithfulness proof, not hand-coded): frequency-DOMINANCE (high-f
  sense wins ties/settles faster); POLYSEMY-ADVANTAGE + HOMONYMY-DISADVANTAGE from post-learning basin geometry
  (Rodd); OVERNIGHT-FRAGILITY (un-consolidated fast-store senses lost under interference until a consolidation pass).

## KEY CITATIONS
McClelland/McNaughton/O'Reilly 1995 (CLS/interference); McClelland 2013 + Tse 2007/2011 (schema-gated fast cortical
learning); Kumaran/Hassabis/McClelland 2016 (CLS update + replay); Rodd 2004/2020 (continuous semantic space,
polysemy/homonymy geometry); Rodd & Davis 2012 (new-meaning-for-old-word: overnight consolidation, relatedness);
Srinivasan 2019/2021 (usage-based polysemy acquisition); Yu & Smith 2007 (cross-situational); O'Reilly Leabra/XCAL
(BCM + error-driven); Neelakantan 2014 / Li & Jurafsky 2015 / Bartunov 2016 (nonparametric sense induction).
