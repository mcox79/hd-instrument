# Prereg: exp_hp12_v1_decisive_extraction_v1
## Anchor
exp_hp12_v1_decisive_extraction_v1
## Routing
HP-12 V1 decisive Test 1 + HF-3: substrate geometry on Pythia-160m (live) + real Llama-1B embeddings (npz). GPU $0.
## Bands
HARD-PASS both recall>0.80 (no geometry mismatch). MIDDLE one>0.70. HARD-FAIL recall<0.60 (HF-3).
Smoke: pythia 1.0 + llama 1.0 -> HARD_PASS. Test 3 speed deferred (Llama weights gated/not-local).
## Queue
overnight_queue timeout 14400s. PROT-022 PASS.
