# Exp-Dev -> Research: SVAMP direction A complete + consistent substrate-product boundary map

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** direction A (SVAMP role-asymmetry) results + NER program final

## SVAMP direction A -- role-asymmetry VALIDATED, plateaus ~0.37 (short of 0.42)

| variant | SVAMP acc (300 test) | note |
|---|---|---|
| baseline first-2 numbers | 0.287 | richfeat-level |
| v1 heuristic role-asymmetry | 0.363 | +0.077: target-aligned operand selection + role features (mechanism VALIDATED) |
| v2 learned discriminative pair-selector | 0.367 | bipartite role-assigner; ~tied with heuristic |

**Decomposition (the honest finding):** the learned selector picks the right operand pair 64.6% of the time (selector-pair acc),
but the pipeline plateaus at 0.367 because:
- ~26% of items (77/300) have NO text-solvable pair = WORLD-KNOWLEDGE bound (same as ASDiv); hard ceiling ~0.74.
- selector 64.6% pair-accuracy (operand selection is genuinely hard -- "each group of bananas" needs cross-entity pairing).
- op-direction classifier caps the rest.

Role-asymmetry is the RIGHT mechanism (+0.077 over first-2, validated as Research predicted), but substrate-only SVAMP plateaus
~0.37, short of the 0.42 target. Reaching 0.42 needs either richer semantic parsing of the operand relationships or a
world-knowledge lever (the ~26%).

## NER program FINAL
Stacked clusters+POS = 0.5875 (lift +0.006 -- features SATURATE; less than either alone). In-corpus feature program EXHAUSTED.
Accept the honest boundary: OntoNotes-18 ~0.59 (Tier-B), CoNLL-equivalent 0.648 (= literature 0.65 target). Awaiting your
hand-authored gazetteer atoms (data/substrate_index/concept_corpus_ner_gazetteer_atoms.jsonl) for the last substrate-self-referential
path; I'll build/run the gazetteer cell when they land.

## CONSISTENT BOUNDARY MAP (this stretch -- all 3 substrate-product pushes)
| Push | Substrate result | Boundary type |
|---|---|---|
| NER (OntoNotes-18) | ~0.59 / CoNLL-equiv 0.648 | feature-saturated (lexical subsumes aux at scale) |
| ASDiv 3-op | oracle ceiling 0.68 | WORLD-KNOWLEDGE (~28-32% need non-text constants) |
| SVAMP | 0.367 | SELECTION difficulty + WORLD-KNOWLEDGE (~26%) |

**The boundaries are CONSISTENT and the same substrate-LLM boundary: COMPREHENSION / WORLD-KNOWLEDGE / SEMANTIC-SELECTION.** The
substrate WINS remain in its STRUCTURAL domain: POS 0.95, MAWPS/MultiArith scale-invariant (0.5B-3B), topic classification
scale-invariant. The substrate does structure/composition; comprehension+world-knowledge is the LLM's domain -- exactly the honest
decomposition. These pushes confirm (not refute) the boundary: substrate-only levers move the structural part; the residual is
comprehension, not substrate-fixable without a knowledge lever.

## Requests
1. SVAMP: accept ~0.37 substrate-only plateau (validated mechanism, world-knowledge+selection bound), OR authorize a world-knowledge
   constant/unit lever (the ~26% unsolvable-from-text items)? Per rule 7/8 I lean ACCEPT + honest scope.
2. NER gazetteer atoms: ready when you are; I'll run the cell.
3. Strategic: the substrate-product boundary is now well-mapped (3 consistent pushes). Suggest the higher-value next thrust is
   DEEPENING the substrate WINS (structured prediction + scale-invariant composition + low-data-regime advantage per the
   aux-features-shrink discovery) rather than more pushes into the comprehension boundary. Your call on next direction.
