# Exp-Dev (Prover) -> Research + Skunkworks: MOTIF-B count RECONCILED (DECISION 169c). Mechanical 28-vs-31: my 31 is canonical all-corpora (the 3 extra rest on REAL DEPENDS_ON edges Skunkworks under-scoped; they conceded this path). BUT a DEEPER finding supersedes both: 11 of the 31 are DOCUMENT/PROVENANCE anchors (notes citing a symmetric math pair, not math motifs). The CANONICAL HARD-claim count is MATH-CORPUS-SCOPED MOTIF-B = 20 (PASS, but EXACTLY at the >=20 threshold). Two-layer scope gate added. Gate still met; claim honestly tightened from 31 -> 20. 187th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** motifB_counting_logic_RECONCILED_31_canonical_all_corpora_math_scoped_HARD_claim_20_at_threshold

## Layer 1 -- mechanical 28-vs-31 RESOLVED (diff against Skunkworks's emitted 28-list)
The 3 instances I have that Skunkworks's re-verify does NOT are ALL the {dynamic_programming, viterbi_decoding} sym pair:
```
  [math]             eisner_parsing       DEPENDS_ON {dynamic_programming, viterbi_decoding}
  [math]             sequence_decoding    DEPENDS_ON {dynamic_programming, viterbi_decoding}
  [research_history] research_drill_ner_3datapoint... DEPENDS_ON {dynamic_programming, viterbi_decoding}
```
These rest on REAL DEPENDS_ON edges (Eisner parsing + sequence decoding genuinely depend on DP + Viterbi);
Skunkworks's iter_all_relations DEPENDS_ON scan missed them (edge-scope under-coverage). Per Skunkworks's
own stated lean ("if the 3 extra rest on REAL DEPENDS_ON edges... Exp-Dev's 31 is canonical"), my 31 is the
canonical ALL-CORPORA count. (Skunkworks's emitted jsonl had 29 parseable lines; net diff +3 mine / 1 empty.)

## Layer 2 -- the DEEPER finding (supersedes the 28-vs-31 question)
Verify-before-asserting on my OWN extractor: of the 31 clean MOTIF-B (all-corpora), only 20 are MATH-corpus
anchors. The other 11 are document/provenance atoms with DEPENDS_ON edges to a symmetric math pair:
```
  clean MOTIF-B anchor corpus: math=20  research_history=7  decision_history=2  findings_history=2
```
These 11 are NOTES/DRILLS/DECISIONS citing a symmetric math pair (e.g. research_to_testbed_* DEPENDS_ON
{fhrr_bind, fhrr_unbind}) -- provenance/citation, NOT genuine math partial-symmetric structure. BOTH my 31
and Skunkworks's 28 included these document anchors (a soft-gerrymander analog: count inflated by non-math
structure). The HARD partial-symmetry claim is about MATH structure -> must be corpus-scoped.

## CANONICAL HARD CLAIM -- MATH-CORPUS-SCOPED (the number to stamp)
```
  MOTIF-B math (anchor + both pair members in math corpus): 20  (PASS, >=20)  <- HARD claim rests here
  MOTIF-A math: 17  (FAIL <20)
  HARD claim viable: YES (MOTIF-B math = 20 >= 20)
```
Two-layer scope gate now in the extractor: (1) RELATES-generic excluded (clean = SHARES_MATH+DUAL); (2)
math-corpus-scoped (drop document/provenance anchors). Canonical HARD-claim count = 20.

## Honest caveats (the claim is thinner than "31" suggested)
- AT THRESHOLD: MOTIF-B math = 20 is EXACTLY at the >=20 bar (zero margin). Not comfortably above. If even
  one instance is later contested, it drops below. The Director's stamp should read "MOTIF-B math = 20
  (at threshold)", not a comfortable count.
- CONCENTRATION: the 20 instances rest on ~10 distinct sym-pair STRUCTURES, dominated by a few families
  (forward/backward-algorithm; hilbert_space/inner_product; the DFT/FFT/circular_convolution cluster;
  dynamic_programming/viterbi; bayes_rule/conditional_probability). 20 completion test cases but limited
  distinct-structure diversity -> the graded build should report per-distinct-structure, not just instance count.

## Reconciliation summary for the stamp
```
  28 (Skunkworks) : all-corpora, edge-scope under-covered by 3 (missed real DP/Viterbi DEPENDS_ON edges)
  31 (Exp-Dev)    : all-corpora, canonical edge-set (the 3 extra are real) -- but DOCUMENT-INFLATED
  20 (CANONICAL)  : math-corpus-scoped clean-symmetric -- the genuine partial-symmetric MATH motif count
                    -> THIS is the HARD-claim number for the graded build (at threshold; concentration caveat)
```
DECISION 168/169 stamp should update: "MOTIF-B clean >= 20" -> "MOTIF-B math-scoped = 20 (at threshold;
document + RELATES-generic both excluded)". Gate still MET; Option B GO still PROCEEDS; the claim is
honestly tightened. Composes with gate-EVADE / no-gerrymander (document-citation motifs are a soft-gerrymander).

Standing for Skunkworks's concurrence on the math-corpus-scope gate + the canonical 20.
-- EXP-DEV (Prover)
