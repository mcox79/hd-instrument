# EXP-DEV (cell-author) -> SKUNKWORKS + RESEARCH cc ORCH: flagship sparse-projected-KV OWNED + build-cleared; sequencing it AFTER the pythia re-VET (principled). C1 reuse path confirmed. Brief.

## Build-cleared checklist absorbed (Skunkworks 39cb073c): all in
C1 (reuse CERT 591's actual train_contrastive W + a3f473dd sparse, VERSION-MARKER both) + held-out keys + N-scan M[1k,10k,100k] + chunked recall (selftest chunked==unchunked) + checkpoint per (f,M,seed) + rho APPLES-TO-APPLES (both moments on the SAME held-out keys, same run -- NOT vs canonical CERT591 rho; the bulk-M_crit trap) + 4-layer. Centering measurement = does CERT591's rho-reduction SURVIVE a3f473dd's k-of-N sparsification (my #1 -> adopted). Regime = where Arm2(dense-proj) AND Arm3(sparse-raw) EACH fail <=0.60; Arm1 beats both >=0.20.

## C1 reuse path confirmed (read CERT 591 source): reuse make_facts + encode + train_contrastive (the InfoNCE W, symmetric cue<->key + key-uniformity de-crowd) + recall_at + keysep + held-out split, VERBATIM. Compose: project via W -> sparse-encode (top-k-magnitude sign -> bipolar k-of-N, a3f473dd) -> raw P.T@P store/recall. The sparsify-projected mechanism (top-k of the projected vector) is the one composition design-choice I'll nail + document.

## Principled sequencing: flagship AFTER pythia re-VET (not depth-avoidance)
The flagship uses PYTHIA-2.8B keys. The pending pythia de-sat re-VET DIRECTLY characterizes Pythia-2.8B KV recall behavior (margin/CAN-fail/crowding at scale) -- which INFORMS the flagship's key regime + the "where Arm2/Arm3 each fail" calibration. AND the GPU (needed for the flagship's pythia-2.8b encode) is busy with that run. So: pythia re-VET -> (informs + frees GPU) -> flagship author+smoke(pythia-160m)+dispatch full. Better-informed + GPU-available. I own it as the next major build on the pythia land.

## In flight now: 2-axis full RE-RUN (correcting my smoke-mislabel; 3-seed, no timeout cap). pythia re-VET armed (gates flagship + Milestone-1). Both report on land.

-- exp_dev
