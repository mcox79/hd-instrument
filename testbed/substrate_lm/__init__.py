"""substrate_lm -- 4-primitive substrate-native LM module.

Implements the Drill-4 white-space combination:
    (1) outer-product Hopfield write           (re-used from substrate_audit)
    (2) anti-Hebbian bipartite contrastive     (NEW)
    (3) hierarchical recurrent retrieval       (NEW)
    (4) stacked independent-W composition      (NEW)
"""
