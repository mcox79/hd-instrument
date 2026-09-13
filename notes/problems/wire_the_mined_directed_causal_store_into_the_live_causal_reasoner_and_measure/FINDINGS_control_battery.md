# Control-battery decomposition of the "surprising +0.22" (working notes, WIP)

Owner flagged the concept-bound +0.223 as surprising ("clearly we don't understand it"). It contradicted the
grow_the_causal_mechanism SOLVED, where FOUR honest WIQA rung-2 attempts all TIED/LOST association (0.563-0.599).
The control battery (`experiments/exp_causal_store_wire_transfer_v1.py`) decomposed it. The skepticism was correct.

## The instrument
WIQA necessity, sign-free axis (EFFECT vs NO_EFFECT). Base graph = the reader's OWN extraction
(`hdlab.causal_network.build_causal_edges` = the exact `sm.causal_links` mechanism), nodes = event verb lemmas.
Necessity = pure rung-2 reachability(Xnode, Ynode) over the graph; abstain->no_effect when a phrase is unmapped
(NO direct-store-edge fallback, so no rung-1.5 store-as-scorer shortcut can leak in).

## What the numbers say (smoke n=300, thr=0.0; full n=5005 consistent)
| arm | acc | vs what | paired |
|---|---|---|---|
| LIVE lemma-node base (no store) | 0.430 | — | — |
| LIVE lemma-node + store | 0.430 | vs base | **+0.0000** |
| LIVE lemma-node + global twin | 0.430 | — | — |
| concept-bound + real store | 0.743 | — | — |
| concept-bound + GLOBAL-shuffle twin | 0.520 | vs cbound | +0.223 (CONFOUNDED) |
| concept-bound + DENSITY-MATCHED topotwin | 0.613 | vs cbound | **+0.130** |
| **map_only** (effect iff both X,Y map to a step; NO edges) | **0.763** | vs cbound | **-0.020** |

Diagnostics: real graph 26.8 edges/item vs global-twin 1.8 edges/item (15x sparser); lemma-pair store coverage
0.97-1.38% vs concept-pair 12.3-12.6%; pred_effect cbound 0.38 vs gold_effect 0.57; frac_same_step 0.09;
extraction avg_nodes 2.1, avg_edges 0.0, frac_any_link 0.00.

## The two stacked confounds (why +0.22 was not real transfer)
1. **DENSITY artifact of the wrong twin.** `shuffle_store` permutes the effect vocabulary GLOBALLY, so shuffled
   edges rarely land inside an item's small concept set -> the twin per-item graph is 15x sparser (1.8 vs 26.8
   edges). Beating THAT twin is largely "I have more edges." Against the density-MATCHED twin (the causal_reasoner's
   own `CausalGraph.shuffled()`: same node set + same edge count, random acyclic rewire) the gap falls +0.223 -> +0.130.
2. **The residual is a topicality/mapping baseline = association.** `map_only` (predict EFFECT iff both X and Y map
   to a process step, consulting NO edges) scores 0.763 > cbound 0.743. So the store's directed reachability adds
   NOTHING over "are both concepts in the process" -- which is undirected association. This reproduces the grow SOLVED
   VERBATIM: "process-simulation reachability is co-extensive with association -- related concepts ARE causally
   connected in a process." CHT (Bareinboim 2022): the EFFECT-vs-NO_EFFECT (connectedness) axis is rung-1-saturable;
   the store's only causal-specific content (DIRECTION) is never exercised by it.

## The live-lemma-node located negative (independent of the twin question)
On the reader's ACTUAL representation, the store transfers +0.0000: the extractor yields 2.1 nodes / 0.0 causal
edges on process prose (6 connectives + a 36-word hard-coded force-dynamics bridge fire on none of it), and
single-verb-lemma nodes get 0.97-1.38% store coverage. Wiring the store into the live `_graph()` adds cross-edges
to only ~3% of items and changes no necessity answer.

## Consequence for the brief's OWN headline (disk-outranks-brief, being verified at full scale)
The brief's +0.139 "storeonly" prize used the SAME global-shuffle twin. The reference arm here re-examines it
against the density-matched topotwin + map_only. If storeonly ties/loses those, the +0.139 was itself a
density/topicality artifact, not a directed-causal win -> a correction to the store's headline.

## Where this points (solve the REAL problem, not just refute)
The store's genuine causal-specific value is DIRECTION (grow SOLVED: load-bearing ONLY on direction-DISCRIMINATION
2AFC -- COPA +0.053, e-CARE, BCOPA-CE -- where association is neutralized by construction). WIQA necessity is not
direction-sensitive. So the right live test is whether the store's DIRECTION transfers to the reader's
extracted-from-prose concepts on a direction-sensitive causal read (cause-vs-effect 2AFC / actual-cause selection),
NOT the connectedness axis. That pivot is the next build. (Research check dispatched to confirm the interpretation +
name the direction-exercising instrument shape.)
