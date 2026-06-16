# SKUNKWORKS (Auditor) -> Research + Exp-Dev: R1 research-drill (DECISION 202c) -- Modern Hopfield-cleanup deep lit-scan, literature-base memo for Primitive 2. HEADLINE: Primitive 2's G1/G2/G3 anchors CONFIRMED real + citable (Ramsauer 2020 closed-form beta + separation + exp-small retrieval error; exponential capacity; attention=update-rule). The closed-form bound is EXPLICITLY separation(Delta_min)-DEPENDENT -> CONFIRMS + SHARPENS my installment-2 G5 envelope (cleanup guarantee DEGRADES as Delta_min -> 0, i.e. for continuous-FPE near-neighbors). New lever: SPARSE/STRUCTURED Hopfield variants (exact retrieval w/o sacrificing exp capacity) = candidate for the small-Delta_min near-neighbor regime. INTEGRITY FLAG: excluded a suspicious cross-query result ("SuperLocalMemory V3") as unverified -- not propagating an unvetted citation into the literature base.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** R1_modern_hopfield_cleanup_lit_scan_memo_closed_form_beta_confirmed_delta_min_envelope_sparse_variant

## CORE ANCHOR -- Ramsauer 2020 "Hopfield Networks is All You Need" (Primitive 2 G1/G2/G3 CONFIRMED)
- Modern Hopfield with CONTINUOUS states + log-sum-exp energy; update rule = transformer attention (softmax-weighted
  retrieval over stored patterns). EXPONENTIAL storage capacity O(e^(alpha*d)); retrieval error EXP-SMALL in separation.
- CLOSED-FORM (G1 anchor CONFIRMED, citable for G2 CHTV-1, provable for G3 L6-PROOF):
  - separation Delta_i = min_{j!=i}( x_i^T x_i - x_i^T x_j ) [min dot-product gap to other patterns].
  - well-separated if Delta_i >= 2/(beta*N) + (1/beta) log(2(N-1) N beta M^2).
  - one-step retrieval contraction ||Jbar||_2 <= 2 beta k M^2 (k-1) exp(-beta(Delta_i - 2 max{...})) -> retrieval
    error EXPONENTIALLY small in beta*Delta_i.
  -> the beta / separation / retrieval-error relationship is CLOSED-FORM (no learned params; 11th-rule clean). This is
     the citable anchor for Primitive 2's closed-form-beta gate. The "Theorem-4 closed-form beta" I cited in
     installment 2 is grounded.

## KEY ENVELOPE INSIGHT (Primitive 2 G5 -- CONFIRMED + SHARPENED, honest)
The bound is EXPLICITLY separation(Delta_min)-DEPENDENT. CONSEQUENCE for continuous-FPE (the TIER-3 use case):
```
  continuous-FPE codewords V^x, V^y with x~y are NEAR-NEIGHBORS -> Delta_min -> 0 as resolution increases ->
  the well-separation condition Delta_i >= 2/(beta*N) + ... FAILS (RHS can't be met for tiny Delta), and the
  retrieval-error contraction degrades (exp(-beta*Delta) -> 1). So modern-Hopfield-cleanup MITIGATES near-neighbor
  confusion ONLY within a Delta_min-BOUNDED ENVELOPE -- it does NOT eliminate the continuous-resolution limit.
  -> CONFIRMS my installment-2 G5(a) honest uncertainty (resolution/capacity envelope, Delta_min -> 0 degradation)
     -- now LITERATURE-GROUNDED, not just asserted. Primitive 2's honest capability surface = robust cleanup WITHIN
     a characterized (resolution, |M|, beta) envelope; the envelope is the Delta_min separation budget.
```

## NEW LEVER -- SPARSE/STRUCTURED Hopfield (candidate for the small-Delta_min regime)
- Sparse modern Hopfield (Hu et al. NeurIPS 2023) + Sparse/Structured Hopfield (Santos et al. 2024): EXACT retrieval
  WITHOUT sacrificing exponential capacity; sparse/structured differentiable attractor maps (single memory / weighted
  / combinatorial). A SPARSE cleanup may be MORE robust than dense-softmax in the near-neighbor (small-Delta_min)
  regime (sparsity sharpens basins). -> CANDIDATE to investigate at the Primitive-2 cell-gate: compare DENSE-softmax
  vs SPARSE cleanup on continuous-FPE near-neighbors; the sparse variant could widen the usable resolution envelope.
- Continuous-time MHN (2025, arXiv 2502.10122): compressed/graded memory over smooth sequences -- relevant to
  continuous attributes (Primitive 1's domain). Hopfield-Fenchel-Young (2024, arXiv 2411.08590): unified retrieval
  framework. Capacity-with-synaptic-noise (2025, arXiv 2503.00241) + "The Capacity of Modern Hopfield Networks"
  (OpenReview): capacity analyses to bound the envelope.

## INTEGRITY FLAG (verify-before-asserting on the lit-scan itself)
A result titled "SuperLocalMemory V3: ... Zero-LLM Enterprise Agent Memory" appeared in ALL THREE unrelated queries
-- a cross-query recurrence + commercial/SEO-style title that is NOT a standard modern-Hopfield reference. I am
EXCLUDING it (+ similarly-unverifiable hits) from the literature base: I do NOT propagate an unvetted citation into
the substrate's research-finding layer. Only the established, verifiable Hopfield literature (Ramsauer 2020 + the
peer-reviewed sparse/continuous/capacity follow-ups) is cited. (Same don't-assert-the-unverified discipline as the
79th propagated-summary-figure instance -- applied to external sources.)

## IMPLICATION for Primitive 2 (future foundation build; paper-design level)
- G1/G2/G3 CONFIRMED (closed-form beta/separation/error real + citable + provable). 
- G5 envelope LITERATURE-GROUNDED + SHARPENED: the cleanup guarantee is Delta_min-bounded; the Primitive-2 cell-gate
  must CHARACTERIZE the (resolution, |M|, beta) envelope (the Delta_min budget), NOT assume unbounded cleanup.
- NEW design option: dense-softmax vs SPARSE cleanup comparison at the cell-gate (sparse may widen the near-neighbor
  envelope). Fold into the Primitive-2 verification when/if USER GOs the foundation build.
- Connects to the ARM-1 dual-head control (naive-max-cos vs Hopfield) -> now extend to (naive / dense-Hopfield /
  sparse-Hopfield) as the cleanup-head options, selected by the empirical Delta_min envelope.

## Status
R1 DELIVERED (Primitive 2 literature base; closed-form beta CONFIRMED + Delta_min envelope grounded + sparse-variant
lever + unverified-source excluded). R2 (continuous-FPE capacity/resolution; Primitive 1 G5 + Drill 5) NEXT, light
cadence. Standing: 190c results VET + 190f atom type-VET + 190e hookup VET. These drills inform the FUTURE TIER-3
foundation build (USER-gated); no build commitment implied.

Sources (verifiable; cited): [Hopfield Networks is All You Need (Ramsauer 2020)](https://ml-jku.github.io/hopfield-layers/) | [On Sparse Modern Hopfield Model (Hu et al. NeurIPS 2023)](https://proceedings.neurips.cc/paper_files/paper/2023/file/57bc0a850255e2041341bf74c7e2b9fa-Paper-Conference.pdf) | [Sparse and Structured Hopfield Networks (2024)](https://arxiv.org/pdf/2402.13725) | [Modern Hopfield Networks with Continuous-Time Memories (2025)](https://arxiv.org/abs/2502.10122) | [Hopfield-Fenchel-Young Networks (2024)](https://arxiv.org/pdf/2411.08590) | [The Capacity of Modern Hopfield Networks](https://openreview.net/pdf?id=OBQwZaO4pt) | [Accuracy and capacity of MHNs with synaptic noise (2025)](https://arxiv.org/pdf/2503.00241)

Tag: R1_modern_hopfield_cleanup_lit_scan_ramsauer_2020_closed_form_beta_separation_delta_min_retrieval_error_exp_small_exponential_capacity_attention_update_rule_G1_G2_G3_CONFIRMED_G5_envelope_delta_min_dependent_LITERATURE_GROUNDED_continuous_FPE_near_neighbor_degradation_sparse_structured_hopfield_exact_retrieval_candidate_small_delta_min_regime_dense_vs_sparse_cleanup_head_option_continuous_time_MHN_capacity_analyses_INTEGRITY_excluded_SuperLocalMemory_V3_unverified_cross_query_SEO_title_not_propagate_unvetted_citation_79th_discipline_external_sources -- SKUNKWORKS (Auditor)
