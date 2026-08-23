---
owner_verdict: DONE
---

SUBMISSION — problem: cortical_read_has_no_scored_path — status: REFUTED (fair, powered)

WHAT WAS ASKED
Build a scored test for the "cortical read" (the route that answers from the brain-model's
settled-knowledge store) and find out if it's any good — nobody had ever scored it.

THE SOLUTION (delivered)
1. A clean, floored, CI'd scored path now exists (experiments/solverB_cortical_scored_path_v1.py).
   Task: hide a settled-knowledge word in a held-out sentence, ask the cortical read to recover it
   from the settled pool. 3 seeds, 300 items each, ~430-480 candidates.
2. While building it I found the only prior scoring (Aug-19) was run on 298-300 of 300 ALREADY-READ
   sentences — near-total train leakage. Fixed with a provably-unread split (0 overlap).
3. Verdict on the clean test: the cortical read reads its cue (beats scrambled/random) but LOSES to
   plain word-co-occurrence counting at every operating point, every seed.

THE FAIR / BRAIN-FOUNDATIONAL TEST (added on owner request)
A cloze-vs-counting task is biased toward counting, so it doesn't test what a cortical read is FOR:
generalizing to situations it never trained on. I built that test too
(experiments/solverB_cortical_generalization_v1.py): train on encyclopedia text, test on novel
fiction, isolate the cases where counting has no signal (n=177-188/seed, powered), and test the
organ's MOST brain-faithful setting — the sensorimotor "similar-things-are-close" space.
RESULT: it still fails. Where counting can't help, the cortical read does no better than a dumb
"prefer concrete words" rule — its only generalization signal IS concreteness, not meaning. So
"REFUTED" means: on a fair, powered, brain-faithful test, the cortical read carries no
situation-specific meaning. It does NOT mean the problem was ill-posed — the scored path works fine.

WHY IT FAILS, AND WHAT WOULD FIX IT
The bottleneck is the REPRESENTATION, not the ranking or retrieval dynamics. The settled-knowledge
codes encode "which words co-occur" + "how concrete a word is," but not "which words MEAN similar
things." No pattern-completion trick can retrieve structure the store doesn't hold. The brain's
cortex stores meaning as a distributed OVERLAPPING code (similar concepts -> similar patterns),
which is exactly what enables generalization — and ours doesn't have that shape. Fixing it is a
BUILD of the cortical code, which is the strategy session's lane, not a solver tweak.

RECOMMENDED NEXT PROBLEM (full brief saved at
notes/problems/cortical_read_has_no_scored_path/PROPOSED_FUTURE_PROBLEM_paradigmatic_cortical_code.md)
  slug: cortical_read_needs_a_paradigmatic_code
  Build a settled-knowledge code whose similarity tracks MEANING (second-order/paradigmatic — dog
  near cat because they occur in similar contexts, not because they co-occur). Brain-motivated
  (CLS replay extracting structure; LSA as a model of human semantic acquisition; ATL amodal hub) —
  but the specific construction is OURS-UNDER-TEST, label it so.
  BAR: the new code's cortical read clears the CONCRETENESS floor CI-separated on the
  unseen-co-occurrence regime (the confound that's killed this organ's story twice), 3 seeds,
  >=100 unseen items/seed, with info-free twins losing. The fair instrument already exists
  (solverB_cortical_generalization_v1.py), so this is a representation build against a ready eval.
  A brain-faithful code that STILL can't clear concreteness = REFUTED -> shelve B3' as a dead end
  (a first-class outcome).
  NOTE: reconcile with the already-filed cortical_read_never_tested_where_it_matters (that was the
  powered test, now answered) so the next solver builds the representation rather than re-running
  the test.

REVERIFY
cd d:/AI/hd-instrument && .venv/Scripts/python.exe experiments/solverB_cortical_generalization_v1.py --mode full --seeds 3
