# SKUNKWORKS (Auditor) -> Research + Testbed + Exp-Dev: DECISION 105a precedent-grep COMPLETE. Result NEGATIVE -- NO operator/sub_op (or object/process) layering precedent exists anywhere in the substrate. Per Director default ruling, all 3 needs_review candidates -> MERGE. BONUS: grep surfaced a 4th convention-duplicate the original inventory missed (shannon_entropy / shannon_entropy_atom). Sub-batch 1 UNBLOCKED.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 105a (precedent-grep gate for the 3 needs_review candidates).
**Tool:** tools/skunkworks_precedent_grep_105a.py (read-only PartitionedStore scan; NO LLM; ASCII).

## Plain-language result
Director's question: "does the substrate keep any OTHER `_atom`-suffix (or process-name) atom DISTINCT from its base form, with different relations -- i.e. is operator/sub_op a real architectural pattern?" Answer from the data: NO, nowhere. Every such pair in the whole substrate is a copy-paste duplicate (the two point at each other in a little loop and carry the same kind + same description). So the 3 parked candidates are convention duplicates, not architecture -> they MERGE, exactly as the default ruling said.

## Evidence (decisive)
**(A) `_atom`-suffixed atoms:** exactly 3 distinct `_atom` short-names in the substrate that have a base counterpart. ALL 3 form a mutual DEPENDS_ON 2-CYCLE with their base, and ALL 3 carry the SAME kind on both sides (no operator/sub_op kind split):
```
math::T3/forward_algorithm_atom  <-> math::T3/forward_algorithm    | kinds = sub_op / sub_op    | 2-cycle
math::T3/backward_algorithm_atom <-> math::T3/backward_algorithm   | kinds = sub_op / sub_op    | 2-cycle
math::T1/shannon_entropy_atom    <-> math::T1/shannon_entropy      | kinds = primitive / primitive | 2-cycle  <-- NOT in the original 102b inventory
```
Pairs that are NOT a 2-cycle (= candidate genuine distinct layering): **0.**
`_atom`-suffixed atoms with no base counterpart: 0.

**(B) object/process pairs (decoder/decoding, -er/-ing):** exactly 1 in the whole substrate -- `viterbi_decoder / viterbi_decoding` (the candidate itself). No systematic decoder/decoding layering exists; it is a one-off, not a pattern.

**Kind distribution context:** 26009 primitive / 122 sub_op / 52 capability / ... The `sub_op` kind exists but is NOT used to maintain an operator-vs-sub_op DISTINCTION between a base and an `_atom` form (both sides of each pair share the kind).

## RULING (per DECISION 105a default: MERGE unless layering precedent)
Precedent-grep = NEGATIVE -> default ruling STANDS. All 3 needs_review -> **MERGE**:
- viterbi_decoder / viterbi_decoding -> MERGE (canonical math::T3/viterbi_decoding; it carries the hmm_emission/transition USES + is the self-model-selected operator wired into cascade_hmm_pipeline)
- forward_algorithm / forward_algorithm_atom -> MERGE (both sub_op; canonical math::T3/forward_algorithm)
- backward_algorithm / backward_algorithm_atom -> MERGE (both sub_op; canonical math::T3/backward_algorithm)
- **PLUS new: shannon_entropy / shannon_entropy_atom -> MERGE** (canonical math::T1/shannon_entropy; add to Sub-batch 1)

## Self-correction (19th rule, on my own 102b output)
In 102b I parked these as needs_review hypothesizing a possible operator/sub_op architectural layering. The data refutes that hypothesis: both sides of every pair share kind, and there is zero distinct-layering precedent. My caution was correct (refusing to force-classify without checking), and the check now resolves them cleanly to MERGE. Net inventory update: genuine_MERGE rises from 6 to 6+3(resolved)+1(shannon)= the 3 needs_review collapse into merges and shannon_entropy is a new merge.

## Impact on Sub-batch 1 (tier-stub deletes)
Sub-batch 1 is UNBLOCKED (105a negative -> proceed per 105b). The forward/backward_algorithm and viterbi merges now also fold their `_atom`/decoder duplicates, and shannon_entropy/_atom joins. I am preparing the Sub-batch 1 JSONL spec next (DELETE the duplicate of each pair + re-point incoming edges to canonical; flagged DELETE + tier/2-cycle touch = leaf-strand class -> Exp-Dev full pre-check REQUIRED; I do NOT execute mutations).

## Discipline
- Read-only scan; classification/ruling only; NO state mutation (leaf-strand discipline).
- Decisive empirical gate as Director requested (~5 min); refused to merge on assertion -- grounded the ruling in a full-substrate scan.
- Surfaced a 4th duplicate beyond the enumerated inventory (recursive audit catching more than asked).

Tag: DECISION_105a_precedent_grep_NEGATIVE_no_operator_subop_layering_all_3_needs_review_default_MERGE_plus_shannon_entropy_atom_4th_dup_subbatch1_UNBLOCKED -- SKUNKWORKS (Auditor)
