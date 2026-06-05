# Prereg: substrate_tier6_phase_D_4layer_charLM_shakespeare_CPU_v1_n2048
## Anchor
substrate_tier6_phase_D_4layer_charLM_shakespeare_CPU_v1_n2048
## Routing
Tier-6 Phase D (Cell 1, unblocked CPU+Shakespeare). Substrate-hybrid 4-layer char-LM (substrate-Hebbian-attention
no-backprop layers + gradient head) vs full-gradient baseline. THE first substrate-intrinsic-LLM-training test. torch CPU, $0.
## Pre-registered bands
HARD-PASS hybrid_BPC<=1.20x baseline AND wall<=0.5x baseline (>=2x speedup) AND audit operational. MIDDLE BPC[1.20,2.0]x OR speedup[1.0,2.0]x. HARD-FAIL BPC>2x OR slower.
## Smoke gate
Smoke (D=128,T=32): BPC ratio=1.08x, speedup=1.98x, audit=True -> MIDDLE (speedup just under 2x; full D=256/T=64 should widen). Vectorized causal-linear-attention; normalized (NaN fixed).
## Queue
remote_cpu_queue timeout 14400s. PROT-022 self-tests PASS. Corpus scp'd to runner.
