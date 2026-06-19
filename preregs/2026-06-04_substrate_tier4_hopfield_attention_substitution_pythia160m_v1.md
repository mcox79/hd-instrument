# Prereg: substrate_tier4_hopfield_attention_substitution_pythia160m_v1
## Anchor
substrate_tier4_hopfield_attention_substitution_pythia160m_v1
## Routing
Tier-4 Cell 2 (unblock note). Swap 1 attention layer of Pythia-160M with substrate-Hebbian (linear/Hopfield)
attention; fine-tune Shakespeare; training-stability. torch+transformers GPU, $0. overnight_queue.
## Pre-registered bands
HARD-PASS entropy_ratio>0.50 AND grad_ratio<8 AND ppl_ratio<=1.5. MIDDLE entropy 0.25-0.50 OR grad 8-15. HARD-FAIL collapse/explosion/ppl>2x.
## Smoke gate
Smoke: ppl_ratio=1.06, entropy_ratio=3.08, grad_ratio=0.7 -> HARD_PASS (substrate-attention training-stable in Pythia-160M). fp32+grad-clip (fixed fp16 NaN); eager attn (output_attentions); TOKENIZERS_PARALLELISM=false.
## Queue
overnight_queue timeout 14400s. PROT-022 self-tests PASS. Corpus on runner.
