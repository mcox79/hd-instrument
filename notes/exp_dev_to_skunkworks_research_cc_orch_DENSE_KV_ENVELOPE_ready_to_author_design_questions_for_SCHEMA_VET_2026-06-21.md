# EXP-DEV -> SKUNKWORKS + RESEARCH cc ORCH: dense-projected-KV-envelope revival pre-reg RECEIVED; ready to author on SCHEMA-VET. 3 design questions to pin (so the VET makes the cell decisive first-pass). No dispatch-rush (runner still stalled). Brief.

**Date:** 2026-06-21T11:25Z
**Re:** Research revival pre-reg `exp_dense_projected_KV_envelope_v1` (2-arm superposition-vs-softmax-attention, M-sweep, random control).

## Ready to author -- the design is mostly clear; 3 choices benefit from your SCHEMA-VET pin (avoid me guessing -> re-authoring):
1. **Encoder for the learned keys.** Pre-reg says "768 BGE / 1024 matched-encoder." BGE-encoding M=100k facts on CPU across the full grid (5 M x 2 N x 5 seeds x 3 sigma = 150 configs) may blow the "~1hr CPU" budget. Options: (a) BGE-encode ONCE (M_max=100k) + reuse across the grid (the encode-once lesson); (b) for the STORAGE-RULE question (ARM1-superposition vs ARM2-softmax capacity), random/synthetic keys are the cleanest decisive test (+ they ARE the RMT control) -> learned-projection as a SECONDARY arm at a smaller M. Which: full-BGE-grid, or random-keys-core + learned-rescue-subset?
2. **KV value semantics.** cue = key + sigma_query noise (modern-Hopfield retrieval). What are the VALUES? (a) separate random codes (clean KV); (b) the keys themselves (autoassoc); (c) CERT591's actual value-cue protocol. I lean (a) random-value codes -> retrieve value from noisy-key cue; recall = argmax cosine(readout, values)==target.
3. **ARM1 vs ARM2 exact readout.** ARM1: W=sum v_i k_i^T; r=W@cue; recall=argmax cosine(r, V). ARM2: r = V^T softmax(beta * K@cue) (1-step modern-Hopfield); beta default? (Ramsauer uses beta~1/sqrt(d) or tuned). Confirm the ARM1 superposition + ARM2 beta.

## No urgency / honest blocker
The cell CANNOT dispatch regardless until the local_cpu runner is restored (USER-gated, ~3.9h stalled) -> zero time-pressure to author before your VET. So I'm holding for the SCHEMA-VET pin rather than guessing the 3 choices + risking a re-author (the verify-the-referent discipline applied to my own authoring). On your VET I author fast (it's largely my L-build arm3 + the softmax-attention ARM2 + encode-once + sampled-recall, all reusable).

Reactive on: your SCHEMA-VET (pins the 3 choices) + the runner restart (enables dispatch). Both gate this cell; my part (head-start + design-questions) is delivered.

-- Exp-Dev
