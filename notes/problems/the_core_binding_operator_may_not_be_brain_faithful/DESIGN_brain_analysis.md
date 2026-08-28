# Brain analysis + experiment design -- the core binding operator

**Opening move (per SOLVER PROTOCOL): which brain structure does role-filler binding, and are we
replicating the OPERATION or substituting convenient VSA math?**

## The three contested brain hypotheses, pinned to a concrete OPERATION

The brain problem all three share (so we must COPY it): bind role R to filler F such that a later
cue with R (possibly PARTIAL/degraded) recovers F, while many other (R,F) pairs coexist and
interfere.

1. **Tensor-product / conjunctive product** (Smolensky TPR; Whittington 2020 TEM `p = g (X) x`;
   Rigotti-Fusi mixed selectivity). OPERATION: `bind = outer product`, `recover = contract by the
   role index`. Exact, zero crosstalk when roles are orthogonal. PARAMETER we don't share:
   dimensionality (full outer product is d_role x d_filler; the brain has ~10^10 neurons, we have d).
   **FHRR/HRR ARE compressed TPRs** -- HRR (circular convolution) is literally a random compression
   of the outer product (Plate); FHRR complex-multiply is phase-addition, the same compression on
   the unit torus. So our "invention" is already in this family; the untested question is whether the
   UNCOMPRESSED product beats the compressed one AT EQUAL STORAGE.

2. **Theta-gamma phase coding** (Lisman & Jensen; ~7 gamma slots per theta cycle). OPERATION: do NOT
   superpose -- TIME-MULTIPLEX. Each (R,F) pair occupies its own gamma slot; pairs in different slots
   do not interfere at all. Recovery: match the cue-role against the ~7 slot role-tags, pick the
   slot, read its filler. This is DIFFERENT IN KIND from VSA superposition: the brain's answer to the
   "superposition catastrophe" (von der Malsburg) is separation, not better superposition math.
   PARAMETER we don't share: the brain gets ~7 slots x d neurons of capacity PER theta cycle FOR FREE
   (same neurons, different times); a single stored static vector does not have "time".

3. **Conjunctive / sparse mixed-selectivity** -- the product (as in 1) pushed into a sparse
   high-dimensional code. Perirhinal-style. We already own `perirhinal_conjunctive.py` (a quadratic
   bag code) but it is a CONTEXT code, not a role-filler binder. For role-filler the conjunction cell
   IS the outer product, so this collapses onto (1) plus a sparsity parameter.

## What is PINNED vs OUR-INVENTION here

- PINNED-ADJACENT: (a) TEM conjunctive code is a product; (b) LATL conceptual combination is ADDITIVE
  (Baron & Osherson 2011). (b) licenses the SUM in `bundle` and **indicts only the per-component
  normaliser after it** (`bundling.py:36-39`, `out = s / s.abs()`), which whitens every component to
  the unit torus and is NOT motivated by any brain fact. Measured to cost 20-32% d' on FEATURE
  bundling (`diag_percomp_vs_l2_normaliser_v1`) -- but never on BINDING recovery, which is the gap.
- OUR-INVENTION-UNDER-TEST: (i) the elementwise complex multiply (compressed TPR); (ii) the decision
  to SUPERPOSE all pairs into one d-vector and eat sqrt(N) crosstalk instead of separating them;
  (iii) the per-component magnitude normaliser.

## The decisive experiment (interference + partial cue, where schemes diverge)

Canonical key-value associative memory = role-filler binding. N distinct random role-keys, N filler
values drawn from a value codebook (|V|=256). Store M = superpose_i bind(role_i, value_i). Query
role_j (exact OR component-dropout PARTIAL cue) -> recover value_j by cleanup-argmax over |V|.

- **Interference sweep:** N_pairs in {2,4,6,8,12,16,24,32}.
- **Partial cue:** zero a fraction p in {0,.25,.5,.75} of the role-key components, renormalise.
- **EQUAL STORAGE FOOTPRINT** across all arms (2*D reals, D=1024 complex default) -- the conservative
  fairness convention. Theta-gamma also reported WITH its temporal-capacity bonus (the parameter we
  don't share), labelled as such.
- **Arms:** FHRR_percomp (LIVE), FHRR_L2, FHRR_rawsum (normaliser ablation, same operator),
  HRR, TPR (outer product, sweep role/filler split), TPR_sparse (mixed-selectivity), ThetaGamma_K
  slots (temporal separation).
- **Info-free twins that MUST lose:** random-memory, shuffled-key (query an unbound key),
  bag-of-values (no binding). Floor = chance 1/|V| and the strongest twin's upper CI.
- **Decision:** a brain-motivated operator (TPR / theta-gamma / conjunctive) beating FHRR_percomp
  CI-separated = replace. FHRR ties/beats all at equal storage = the invention is VALIDATED (still a
  full PASS per the brief). The normaliser ablation is a separate, actionable sub-finding on the LIVE op.

## FINDINGS (measured) -- the deviation is NOT the bind operator

1. **The bind OPERATOR is validated.** At equal storage, FHRR (a compressed TPR) BEATS the
   uncompressed TPR and the sparse conjunctive product. Compression is more storage-efficient than
   the outer product. So of the three brain hypotheses, TWO (tensor-product, conjunctive) LOSE to
   FHRR at equal storage -- the invention is sound at the operator level.
2. **The deviation is the SUPERPOSITION-AND-UNBIND RETRIEVAL, not the multiply.** The brain does not
   cram many bindings into one vector and unbind; it SEPARATES (theta-gamma ~7 slots; DG-separated
   episodic engrams) and retrieves by CONTENT-ADDRESSABLE cue matching (Lewis & Vasishth 2005;
   McElree SAT; the audit's own E3 entry). A content-addressable separation arm (theta-gamma) beats
   FHRR CI-separated under partial cue + interference (5.2x at equal footprint, D=64/N=16/p=0.9).
3. **The per-component normaliser costs on binding recovery too.** FHRR_L2/rawsum >= FHRR_percomp
   (+0.13 at D=64/N=16/p=0). Confirms audit E1's "additive SUM is faithful, the normaliser is not"
   on a NEW task (binding recovery, not just feature bundling where the 20-32% d' was measured).
4. **The gain is ARCHITECTURAL, not a fancier terminal cleanup.** Routing the FHRR readback through
   the brain's own CA3 attractor completion (hdlab.iterative_attractor, alpha=0.5) TIES one-shot
   argmax. You cannot fix superposition crosstalk by cleaning up harder; you must not superpose.
5. **The substrate already owns the pieces but wires them non-faithfully.**
   `situation_model_multibank.py` SEPARATES into banks (good) but routes by hash of the EXACT key
   (`stable_bank_id`), which cannot degrade gracefully under a partial cue -- the brain routes by
   content-addressable matching. `ca3_completer.py` (content-addressable completion) is DEFAULT-OFF.
