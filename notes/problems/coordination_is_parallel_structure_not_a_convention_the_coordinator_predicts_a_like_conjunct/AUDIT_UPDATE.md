# AUDIT UPDATE — for BRAIN_MATH_REFERENCE.md (attachment rows) + BRAIN_FOUNDATIONAL_AUDIT.md

**Proposed new row (Open-rows → resolved) in `notes/BRAIN_MATH_REFERENCE.md`:**

| computation | math | status | our numbers + control | organ |
|---|---|---|---|---|
| Coordination as PARALLEL STRUCTURE (Frazier 1985; Munn 1993; Taft & Clifton 2000 parallel-structure facilitation; Levy 2008 prediction; Lewis & Vasishth 2005 cue-based retrieval; slot-sharing = conjuncts fill one governor slot) | a coordinator predicts a like-CLASS phrase; the 2nd conjunct HEAD R attaches to the 1st conjunct head L of the same parallel class (L→R conj, R→cc); learned `coord` validity in counts; teacher supplies the parallel-structure prediction (boost L→R, R→cc) treebank-free | PINNED (parallel-structure facilitation; prediction; cue-based retrieval) / MODEL (the coarse parallel classes + gamma are ours, swept) | UD-EWT test 700, gold cats: conj base <FILL> → full <FILL> (paired <FILL> CI-sep), incr <FILL> → <FILL>, UAS not down; scramble twin (wrong heads) BELOW base; shuffled-strengths twin at chance. THE WALL WAS UPSTREAM: the acquisition teacher put 0.054 posterior mass on gold conj arcs (coordination-blind) | `hdlab/attachment_arm.py` `coord_arcs`/`coord_sites`/`parallelism_boost` |

**Correction to the existing attachment row's residual list:** the row lists "second-order occupancy (ccomp/advcl/conj)" as the remaining gap. conj is NOT a second-order-occupancy problem — it is a MISSING ACQUISITION SIGNAL (parallel-structure prediction) in the teacher. Update the residual note accordingly once landed.

**bf_status:** the arm stays BF_SPIRIT; this change is BF at the computational level (parallel-structure prediction is PINNED by psycholinguistics), treebank-free, plastic (counts→strengths, `observe_arc_outcome` accrues the coord cue online).
