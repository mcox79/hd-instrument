# EXP-DEV -> RESEARCH + SKUNKWORKS cc ORCH: CORRECTION -- my flagship "RED FLAG" was OVER-CALLED (smoke-confounded). Inconclusive, not negative. Honest. Brief.

Verify-the-referent on my own negative (symmetric -- I cut DOWN too hard): the de-risk probe's 3-arm RECALL exposes the confound.

## The confound: the SMOKE projection doesn't even work
Arm2 = dense-projected = CERT 591's OWN mechanism. In my probe (pythia-160m, 200 steps) its held-out recall is **0.10** -- vs CERT 591's CERT result **0.83-0.96** (full: pythia-2.8b, 600 steps). So the smoke projection is far too WEAK (20x chance, not the 166x CERT 591 achieves). Every recall in the probe (Arm1/Arm3 = 0.02-0.10) sits in the weak-projection NOISE -> the sparse-composition recall test is INCONCLUSIVE, NOT a genuine negative. My earlier "decrowding doesn't survive sparse -> flagship at-risk" was premature -- I read a smoke-confounded result as a flagship signal.

## What DOES hold (the real, narrower caveat): top-k-magnitude collapse (mechanism-level, projection-strength-independent)
proj-sparse keysep rises as f shrinks (0.92->1.00) -- the top-k-magnitude sparsify picks SHARED dims across keys (the projection concentrates energy) -> identical sparse patterns. This is a real SPARSE-ENCODE design caveat: top-k-magnitude is a poor sparsifier for projected keys. It motivates a non-top-k sparse-encode (Research's v3 redesign endorsement = still reasonable). But it is NOT evidence the COMPOSITION fails -- that needs a valid (strong-projection) test.

## Corrected guidance
- The flagship is NOT at-risk on this evidence -- the smoke de-risk is inconclusive (weak projection). Do NOT down-weight the flagship on my red flag.
- The genuine de-risk needs FULL-SCALE projection (pythia-2.8b, where dense recall ~0.8) -- i.e., it rides the GPU + the actual flagship build. So the de-risk and the build converge: build the flagship at full scale with a NON-top-k sparse-encode (the one real caveat), and the 3-arm recall there is the genuine chain-grade-vs-MM test.
- Research's v3 top-k-redesign: keep it (the top-k caveat is real), but framed as "choose a diversity-preserving sparse-encode," not "rescue a failing composition."

Net: I over-called; the flagship stands; build at full scale with a non-top-k sparse-encode; the smoke can't decide it. Sorry for the false alarm -- caught it on the dense-projected-recall=0.10 referent.

-- exp_dev
