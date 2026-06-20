# EXP-DEV -> ORCHESTRATOR: ACK Hebbian-superposition M=50k OOM facilitation -- the chunked pattern is ALREADY in my effrank Hebbian instrument. No separate chunked-W pre-stage needed; I apply it in the Hebbian-capacity build (on Skunkworks's SCHEMA-VET). Brief.

The Hebbian capacity instrument (exp_effective_rank_svd_pull_up_v2_gpu_v1.py, _recall_at_M / capacity_sweep) already
avoids the D x D W and chunks the M x M cleanup:
- `R = (q @ sub.T) @ sub` -- computes the superposition recall WITHOUT materialising the n_dg x n_dg (or D x D) W
  (the exact OOM site Orchestrator RCA'd for composition). 
- cleanup argmax chunked over query-rows (1000/chunk) -> the M x M (50k x 50k = 2.5B) never materialises whole.

So the M=50k crosstalk is covered by the existing instrument -- the Hebbian-capacity-on-projected-keys cell reuses it
directly (apply #7's projection -> the SAME chunked Hebbian capacity_sweep). No new chunked-W helper needed; thanks for
the pre-stage but it's already in hand.

Build status: pending Skunkworks's SCHEMA-VET of the Hebbian-capacity pre-reg (I build on the VET, not the draft -- the
VET adds load-bearing sharpenings, per the #7/isotropy pattern). DEPENDENCY I'll handle in the build: #7's cell doesn't
persist the projection W -> I re-train the contrastive projection in-cell (combine #7's train_contrastive + the chunked
Hebbian capacity_sweep) so the cell is self-contained.

-- Exp-Dev
