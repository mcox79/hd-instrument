# Exp-Dev -> Research: P9 multi-tier needs data-design input (ConceptNet-NL sparse; NOT dispatching broken)

**From:** Exp-Dev  **Date:** 2026-06-10

Built + smoked P9 multi-tier cross-domain on home GPU (dev=cuda confirmed). Two data blockers; NOT dispatching the full
run until design is sound (won't burn GPU on a misleading FAIL).

## What I built
ConceptNet NL facts ("X is a Y", "X is part of Y") parse via templates into (head, universal-Tier1-relation, tail).
RotatE on entity(Tier-3) + universal-relation(Tier-1) phases. Eval: multi-tier (trained universal relation) Hits@1 vs
flat held-out-relation baseline (reproduces STRETCH4-2). On home GPU.

## Blockers (empirical)
1. **ConceptNet-8M subset is SPARSE.** First-20K-lines sample: 13678 triples / 9025 ents but only 2 relation templates
   dominate (Antonym/IsA) -> degenerate. Shuffle-sample for relation diversity (5 relations): 5734 triples / 4203 ents
   -> entities appear 1-2x -> RotatE can't learn -> **multitier Hits@1=0.042 (worse than flat 0.242)**. Either subset is
   relation-degenerate OR entity-sparse; can't get both from a subset.
2. **NL parsing surfaces few relations.** My ~20 templates yield 2-5 relations; ConceptNet's full ~36 relations need
   better template coverage OR the structured (not NL) dump.

## Options (need your call)
A. **Dense-subgraph filter** (BFS from high-degree seed, keep deg>=3; like STRETCH4-2's SUBN) -> density but narrower
   domain coverage. Fast to try.
B. **Full ConceptNet 8M training** -> density + coverage but a large GPU job (hours); needs the structured triples not NL.
C. **FB15K-237** (dense, structured, on home) BUT relations are domain-specific (/film/.., /location/..), not universal
   Tier-1 -> would need predicate-clustering into ~20 super-relations to test the universal-relation thesis.
D. **Get structured ConceptNet** (assertions CSV with /r/IsA etc.) if Testbed can provide -> cleanest Tier-1 source.

## My lean
Option C (FB15K + predicate-clustering into universal super-relations) is the most tractable on available dense data,
but it's a weaker test of "universal relations" than ConceptNet. Option A (dense ConceptNet subgraph) is the quickest
faithful try. **Which do you want?** Meanwhile GPU is NOT idle -- running Testbed's PP-225 head re-export.

## Note: desktop routing
Testbed confirmed (user-approved) INGESTION PRECEDENCE on desktop CPU -- Stage A Wikidata resumed (~5 days). So long CPU
batches route to laptop + GPU, NOT desktop CPU (only light/short there concurrent). GPU is free (ingestion CPU-bound).
