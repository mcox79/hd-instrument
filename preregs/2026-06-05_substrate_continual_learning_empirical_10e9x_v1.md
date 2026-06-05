# Prereg: substrate_continual_learning_empirical_10e9x_v1
## Anchor
substrate_continual_learning_empirical_10e9x_v1
## Routing
CONT-LRN-1: continual-learning speed + no-forgetting (substrate batched Hebbian vs Pythia-160M fine-tune). torch+transformers GPU, $0.
## Bands
HARD-PASS speedup>=100x AND sub_retention>=0.95 AND llm-forgets. MIDDLE speedup>=1x + no-forget + llm-forgets. HARD-FAIL advantage absent.
Smoke: 27x faster, sub retention 1.00 (no forget), llm 0.53->0.49 (forgets) -> MIDDLE (1000x is large-LLM-scale; Pythia-160M conservative).
## Queue
overnight_queue timeout 7200s. PROT-022 PASS.
