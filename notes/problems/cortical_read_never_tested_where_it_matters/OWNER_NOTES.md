---
owner_verdict: DONE
---

PROBLEM: cortical_read_never_tested_where_it_matters
STATUS: PARTIAL  (the capability is real and reachable with admissible supplied knowledge; the organ
as-built and every space we self-build are refuted as generalisers; wiring + spoke-combination is
the flagship reader_meaning_channel's lane)
BAR (verbatim): "A TASK SCORE ON ITEMS WHERE COUNTING CANNOT HELP, WITH AT LEAST 200 SUCH ITEMS,
AND A CI-SEPARATED MARGIN OVER THE STRONGEST FLOOR YOU ACTUALLY RUN ON THAT POPULATION."

WHAT THE QUESTION WAS
Does the "settled-knowledge" cortical read recognise a concept in a context it has NEVER seen it in
before -- the thing that store is FOR, and the regime where word-counting is useless? A prior solver
found "no" but only had 43 usable questions and only ever tested a first-order cue. So we did not
know: useless component, or tested in the one regime it could not win?

WHAT I BUILT AND RAN
A powered test (experiments/solverB_cortical_paradigmatic_generalization_v1.py): train on encyclopedia
(simplewiki), test on held-out NARRATIVE FICTION so that items where the target never co-occurred with
the cue words are abundant (co-occurrence counting is at floor there by construction). 3 seeds,
269/279/271 such UNSEEN items per seed (all >=200), candidate pool ~300, overlap with training = 0.
I ranked the settled-knowledge pool with, in increasing brain-fidelity:
  - the organ's own space, first-order cue AND a genuine second-order (paradigmatic) cue;
  - the sensorimotor MEANING ASSET (confirmed identical to the project's grounded_vector);
  - a glass-box distributional map (PPMI+SVD) built from our OWN reading (8k and 20k sentences);
  - a SUPPLIED distributional map (GloVe, a static inspectable lookup table, NOT an LLM) as a
    "could this even be won?" ceiling.
Full floor battery on the unseen population (frequency, concreteness, counting, plus two
information-free twins), both tie conventions, scaffold-free witness.

THE RESULT (hit@10, avg over 3 seeds; chance ~0.034; strongest floor = concreteness 0.115)
  GLOVE (supplied distributional) .... 0.189  -> CLEARS the floor CI-separated 3/3 (median rank 37/300)
  concreteness floor ................. 0.115  (the bar to beat)
  sensorimotor meaning asset ......... 0.083  -> BELOW the floor (concreteness-level)
  our self-built map (LSA, 20k) ...... 0.052  -> BELOW the floor (data-starved)
  info-free twins .................... ~0.037
  second-order cue ................... 0.020  -> at chance / at the twins
  first-order cue (organ) ............ 0.029  -> at chance
So: the bar IS clearable in the counting-free regime -- but ONLY by a supplied distributional map.
Nothing built from our own reading clears it.

WHERE OUR IMPLEMENTATION FAILS (three points; the brain does all three)
1. Our retrieval space is a co-occurrence/spelling code, not a meaning code -- it collapses to
   counting on novel contexts. Fixing the cue to be paradigmatic does NOT help (and this is already
   landed: exp_readout_second_order_v1, "paradigmatic readout does not clear the floor" -- reproduced).
2. Our one supplied meaning asset is the WRONG KIND for this task. The sensorimotor/Lancaster norms
   are great at word-word SIMILARITY (SimLex rho 0.317, the flagship's channel) but not at
   cloze RETRIEVAL ("which word fills this gap") -- below the floor here. Perceptual similarity is
   not contextual retrieval. New, task-specific finding that refines the flagship, not duplicates it.
3. The distributional structure that DOES solve retrieval needs experience at a scale our reading
   cannot reach: our entire readable corpus is ~326k sentences (~6.5M tokens), ~1,000x short of the
   supplied map. "Just read more" does not close it.

THE RESCUE -- IMPORT NOW, BUILD OVER TIME (two complementary tiers; the project's own three-tier CLS
architecture, and it dissolves the data-volume wall)
Split the same run by whether we had read about the target:
  arm                    SEEN (we read about it)   UNSEEN (novel context)
  counting                     0.157                    0.000
  our self-built map           0.338                    0.052
  imported map (GloVe)         0.336                    0.189
ON THE MATERIAL WE HAVE READ, OUR OWN MAP ALREADY EQUALS THE IMPORT (0.338 vs 0.336) and beats
counting 2:1. The import only wins on the UNREAD. So:
  - import a large-scale distributional map as the FOUNDATION -> a working read TODAY, covers the
    novel/generic (clears the floor now);
  - keep the LEARNED tier -> it already owns the familiar and matches the import there, and GROWS as
    the substrate reads;
  - "build over time" = ADAPT + EXTEND a good foundation, NOT rebuild from scratch -- which needs
    orders of magnitude less data (the 1,000x wall was only for building-from-scratch).
This is Complementary Learning Systems and hub-and-spoke (Lambon Ralph): a distributional spoke for
retrieval + the sensorimotor spoke for similarity, blended in the hub.

THE ONE HARD PART, STATED HONESTLY
The COMBINATION RULE. Naive fixed-weight blending has a LANDED record of HURTING here
(exp_substrate_concept_encoder_v2..._2spoke HARD_FAIL "composition hurts"; the flagship's own
prior+channel blend destroyed the signal). It must be reliability-weighted (trust the learned tier
only where it has evidence for that term) and likely segregated (flagship result: separate slots beat
superposition). That rule is the OPEN problem reader_meaning_channel already owns -- this plan adds no
new hard problem, it routes into the one already funded.

CONTROLS (all ran)
- info-free twins (scrambled cue, random permutation): every organ/self-built arm sits AT or BELOW
  them -> the space carries no cue-specific signal.
- concreteness floor: the sensorimotor asset sits below it -> its signal is concreteness, not meaning.
- supplied-distributional ceiling clears 3/3 -> the population is winnable, the negative is real (not
  a broken instrument), AND it is the proof-of-concept of the rescue.
- NOT benchmark-selection: items are natural fiction sentences with a random settled-knowledge target;
  the unseen filter and candidate pool come from the substrate's co-occurrence, not from any embedding.
- clean unseen partition (overlap 0, counting=0.000 by construction); metric-fails-safe witness
  (planted -> rank 1 every time, random -> chance, degenerate arm -> flagged and last); both tie
  conventions via rank_with_ties.

PRIOR WORK CHECKED (the owner flagged there is a lot -- there is; I did not re-derive or duplicate)
reader_meaning_channel (flagship, priority 1: sensorimotor = similarity channel, combination is the
bottleneck, read() makes zero calls to the asset); exp_readout_second_order_v1 (paradigmatic readout
landed-refuted); exp_arc_fact_retrieval_semantic_kb_climb_v1 KB_BELOW_FLOOR + the WordNet-oracle
caution (relational/knowledge-graph rescue explored, unpromising -- not built); ran before_you_start
and experiment_index across conceptnet/cskg/foundation/embedding/cortical/distributional/wordnet/
paradigmatic/relational before proposing anything.

THE HONEST WRINKLE
The clean win is ACROSS a domain shift. In-domain novel-context (the sparse route) is underpowered by
construction (114-129 unseen) and the floor is much stronger there; even the supplied map does not
clear it at k=10. Recognising a concept in a novel SAME-topic context is harder, and there the
frequency/concreteness prior is a strong baseline for everyone.

A CORRECTION I OWE
An interim SMOKE (94 items, a 136-word pool) made my self-built map look like it generalised (0.255)
and I said so briefly. It did NOT survive the full run (270 items, ~300-word pool): it fell to 0.052,
below the floor. The small pool flattered it. Recorded, not buried.

WHAT I DID NOT ESTABLISH
- A working WIRED cortical read (wiring + the combination rule are the flagship's lane).
- That a self-built glass-box space could ever suffice alone (bounded below at 20k, above at 6B; on
  our ~326k corpus almost certainly not).
- That in-domain novel-context retrieval is achievable at all (even the supplied map struggles).

WITHDRAW FIRST IF WRONG
The status PARTIAL rests on counting a supplied distributional map as an admissible cortical retrieval
space. If the owner rules the read must LEARN its space from the substrate's own reading, this becomes
a clean powered REFUTED. The powered negative on the organ and all self-built spaces is the robust part.

PROPOSED hdlab CHANGE (for the strategy session to land -- I do not write hdlab)
In hdlab/cortical_recall.py::build_cortical_index add space="foundation": represent each consolidated
term by its supplied distributional vector, leave the consolidation GATE unchanged (CLS sparsity
preserved). Wire it as a distributional spoke alongside the sensorimotor one, combined by the
reliability-weighted hub rule the flagship builds. Do NOT try to fix retrieval with a cue-rule change
or a self-built space -- both refuted here.

THE OWNER DECISION THIS SURFACES
May the cortical read IMPORT a large-scale distributional map (static, inspectable, offline, non-LLM
-- admissible under existing rulings; works today), or must it LEARN its map from the substrate's own
reading (needs ~1,000x more text than all our corpora combined)? The two-tier plan above says: do
both -- import to work now, learn to grow.

REVERIFY
.venv/Scripts/python.exe verification/solverB_verify_paradigmatic_generalization.py
(scaffold-free: proves a distributional space retrieves a target from cue words it NEVER co-occurred
with, the metric fails safe, the supplied-map ceiling is coherent. Landed numbers are in
data/solverB_cortical_paradigmatic_generalization_v1/metrics.json, byte-stable.)

FILES
- experiments/solverB_cortical_paradigmatic_generalization_v1.py
- verification/solverB_verify_paradigmatic_generalization.py
- data/solverB_cortical_paradigmatic_generalization_v1/{metrics.json, units.jsonl, _glove_subset.npz}
- notes/problems/cortical_read_never_tested_where_it_matters/SOLVED.md

VALIDATION: python tools/problem_ledger.py --check  ->  malformed/incomplete: 0
