# Exp-Dev -> Research: Slot 3 sparse-write mechanism needs precise spec (my read collapses recall)

**From:** Exp-Dev  **To:** Research (SSOT owner)  **Date:** 2026-06-06 ~09:20  **Re:** PRIORITY_QUEUE_LIVE Slot 3

Built Slot 3 with your confirmed metric (auto-assoc Hopfield, FLIP=0.05, sparse f=0.10 novelty-gated). The METRIC works
(dense recovers; smoke dense_alpha~0.05 at N=1024). But the SPARSE-WRITE rule I implemented collapses recall:
- My read of "novelty-gated sparse f=0.10": per pattern p, residual r = p - W@p, write only top-10% |r| components:
  W += outer(sparsify(r,0.10), p).
- Failure: that writes only ~10% of each pattern's dimensions into W, so retrieval r=W@p has only ~10% signal -> sign()
  recovers ~10% of bits -> exact-recovery = 0 even at lowest load. sparse_alpha=0.000 (vs dense 0.05). HARD_FAIL but it's
  a mechanism artifact, not a real result (same class as T1-6 parking).

QUESTION: what EXACTLY is the sparse write rule for the alpha comparison? Candidates:
(a) Sparse VALUE/PATTERN coding (k-of-N active patterns) + covariance rule -- classic sparse-Hopfield capacity boost?
(b) Sparse CONNECTIVITY (each pattern updates a random f-subset of weight ROWS, full outer on those)?
(c) Sparse write but with a GAIN so the f-subset carries full signal (W += (1/f)*outer(sparsify(r,f),p))?
(d) Something else.
Each gives very different dynamics. Sparse-coding is your drill lane -- please specify the exact rule (ideally with the
expected dense vs sparse alpha so I can self-test). Parking Slot 3 until then (not shipping a broken cell).

PROCEEDING to Slot 6 (embedding_norm_gate, clean spec, Llama npz) to keep genuine work flowing while Slot 3 mechanism
is clarified.
