# Prereg: substrate_continual_learning_30day_realistic_stream_v1
## Anchor
substrate_continual_learning_30day_realistic_stream_v1
## Routing
HP-3: 30-day continual learning (no-forgetting + cross-day chaining) vs Pythia-160M. Regulated-AI demo. GPU $0.
## Bands
HARD-PASS retention>=0.99 AND new>=0.95 AND cross_day>=0.80 AND substrate faster (100x is large-LLM-scale; Pythia-ceiling). MIDDLE retention>=0.90. HARD-FAIL forgets/no-chain.
Smoke: retention 0.998 new 1.0 cross_day 1.0 speedup 27x; Pythia forgets 0.52->0.50 -> HARD_PASS (qualitative); 100x revisit Llama-1B.
## Queue
overnight_queue timeout 14400s. PROT-022 PASS.
