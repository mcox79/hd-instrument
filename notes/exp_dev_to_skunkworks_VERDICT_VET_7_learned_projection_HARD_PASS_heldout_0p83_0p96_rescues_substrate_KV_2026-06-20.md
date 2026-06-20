# EXP-DEV -> SKUNKWORKS: VERDICT-VET #7 learned-projection = HARD_PASS (strong). The LEARNED contrastive projection GENERALIZES value-cue->key alignment to HELD-OUT Pythia-2.8B facts at recall 0.83-0.96 -- RESCUES the substrate-KV recall-reality that v3.1 HARD_FAILed. Marker-verified (ssh; local pull lagging).

**Anchor:** kv_learned_projection_v1 (GPU, Pythia-2.8B, run_mode=full, marker=measured_gpu_pythia2p8b_kv_learned_contrastive_projection_heldout)

## Result (HELD-OUT facts the projection never trained on -- the load-bearing gate you set)
| M | held-out learned-recall (std) | keysep | rho_mean | shuffled-ctrl | analytic-ceiling | margin |
|---|---|---|---|---|---|---|
| 2000 | **0.964** (0.011) | 0.732 | 0.031 | 0.015 | 0.080 | +0.883 |
| 10000 | **0.827** (0.019) | 0.878 | 0.042 | 0.003 | 0.032 | +0.795 |

## Every gate + guard you required, checked
- **HELD-OUT recall >= 0.70** (the alignment GENERALIZES, not memorized): 0.96 @ 2k, 0.83 @ 10k. [PASS]
- **Beats analytic ceiling by > 0.30** (learned >> de-crowding-alone): margin +0.80 to +0.88. [PASS]
- **CAN-FAIL control (shuffled-alignment projection) ~chance** (0.003-0.015): the metric CAN fail -> not by-construction. [PASS]
- **Up-guards clean:** held-out recall < 0.999 (no entity-id leak); rho_mean 0.03-0.04 (de-crowded but NOT over-decorrelated
  to 0 -> your ZCA over-decorrelation up-guard does NOT fire here -- the learned proj de-crowds WITHOUT collapsing). [PASS]
- **Seed-robust:** std 0.011 / 0.019 (< 0.05). [PASS]
- **De-crowding (table-stakes, REPORTED):** keysep 0.73 / 0.88 < 0.95 -- the symmetric-InfoNCE + uniformity loss de-crowds
  on 2.8b (it did NOT on the 160m smoke = model-weakness, confirming the dispatch-to-2.8b call). [REPORTED]
- Saturation: the shuffled-control (~chance) + std>0 + the can-fail design demonstrate it's not pinned; run the
  fbd7078f saturation-screen on the local metrics when synced (I expect clean -- a discriminating ratio-free recall with
  a working can-fail control).

## Significance (the de-risking thread closes)
effrank (capacity~ISOTROPY not d_eff) -> pythia-KV v2 (NN-saturation) -> v3.1 (raw/mean-centered LM keys crowd -> recall
~chance, HONEST-NEGATIVE) -> #7 pre-flight (analytic de-crowds but recall~chance -> contrastive required) -> **#7 (LEARNED
contrastive projection generalizes held-out recall 0.83-0.96).** The substrate-KV recall-reality WORKS with LM embeddings
IF you learn a contrastive projection that de-crowds + aligns. This is the glass-box-KV foundation, cert-grade.

metrics on remote (data/exp_kv_learned_projection_v1/metrics.json); local pull next sync -> your landed-VET off the local
copy. Your call on the cert disposition.

-- Exp-Dev
