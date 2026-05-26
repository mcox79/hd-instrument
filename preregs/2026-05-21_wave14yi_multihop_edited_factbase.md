# Pre-registration: wave14yi_multihop_edited_factbase

Date: 2026-05-21
Status: Pre-registered, gated
Experiment: [exp_wave14yi_multihop_edited_factbase.py](../experiments/exp_wave14yi_multihop_edited_factbase.py)
Priority source: composes [wave14yc_continual_editing_kerdock](../experiments/exp_wave14yc_continual_editing_kerdock.py)
(continual editing validated) + multi-hop reasoning — does multi-hop
follow edited facts?
Author: experiment_dev session, pipeline tick 19

## Why

Continual editing works (Kerdock at 30+ edits, 100% accuracy). Multi-hop
reasoning works at depth ≤ 50 with per-hop retention ~0.96.

The interesting **composed** product question: when an edit changes a
fact (say "A → R → B" becomes "A → R → C"), do multi-hop chains that
**pass through that fact** follow the NEW value? Specifically:

- Build chain A → R1 → B → R2 → D (depth-2 chain)
- Edit the first fact: A → R1 → B becomes A → R1 → B_new
- Query the same depth-2 chain: should now return B_new → R2 → D' (where D'
  is what B_new → R2 maps to, which is undefined unless we also store it)

For meaningful test: edit the OBJECT of an intermediate hop, then ensure
the chain follows the new value. This tests "edits compose with reasoning."

## Hypothesis

At N=4096, NUM_FACTS=100, HOP_DEPTH=10, 5 seeds: after editing 10 facts
in the chain (each chain has 10 transitions), multi-hop chains return
the *updated* final entity, not the pre-edit one.

## Multi-probe success criteria

- pre_edit_accuracy: chain accuracy before any edits ≥ 0.85 (sanity)
- post_edit_accuracy_following_edits: chains follow the EDITED facts ≥ 0.80
- post_edit_accuracy_consistent: chains that DON'T touch edited facts
  still return original ≥ 0.85

## Verdict labels

- `MULTIHOP_EDIT_COMPOSES` — both post-edit criteria pass
- `MULTIHOP_EDIT_BREAKS_CHAIN` — edits damage chains that touch them
- `MULTIHOP_EDIT_LEAKS_SIDE_EFFECTS` — edits damage chains that DON'T touch them
- `MULTIHOP_EDIT_INCONCLUSIVE`

## Operational definition

For each trial:
1. Build M with NUM_FACTS chain + distractor transitions (random BSC
   entities, relations)
2. Run multi-hop query through chain. Measure pre_edit accuracy.
3. Edit some chain facts: replace (subj, rel, obj) with (subj, rel, obj_new).
   For each edit: apply anti-Hebbian erase on (subj * rel) key + insert
   new value v_new = obj_new (BSC algebra triple = subj * rel * obj_new).
4. Re-run the SAME chain query. Now the chain should follow obj_new at
   the edited step.
5. Compute:
   - post_edit_accuracy: fraction of edited chains where the chain
     reaches the new endpoint
   - kept_chain_accuracy: fraction of chains that don't touch edited
     facts still reach original endpoint

This is a substantive end-to-end product test.

## Notes on test design

This is harder than yc because multi-hop chains involve TRIPLE bindings
(subj * rel * obj). Edit operation needs to remove the OLD triple and
insert NEW. Pipeline:

  old_triple = sign(subj * rel * obj)
  new_triple = sign(subj * rel * obj_new)
  M_new = sign(M - old_triple + new_triple)

(Per-bit sign flip on M based on the old vs new contribution.)

This is the substrate's triple-edit primitive — a real product capability.

## Expected runtime

- Smoke (N=512, NUM_FACTS=20, depth=3, 1 seed): ~5 s
- Full (N=4096, NUM_FACTS=100, depth=10, 5 seeds, multiple trials):
  estimated 1-3 min on GPU
