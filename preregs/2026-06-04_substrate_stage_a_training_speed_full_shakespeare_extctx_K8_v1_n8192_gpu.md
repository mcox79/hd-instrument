# Prereg: substrate_stage_a_training_speed_full_shakespeare_extctx_K8_v1_n8192_gpu
## Anchor
substrate_stage_a_training_speed_full_shakespeare_extctx_K8_v1_n8192_gpu
## Routing
Stage A Cell 3 (unblock note). PURE one-pass substrate (substrate-attention features + closed-form ridge, ZERO
backprop) vs Adam transformer; Shakespeare extctx-K8; training-speed claim. torch GPU, $0. overnight_queue.
## Pre-registered bands
HARD-PASS substrate_BPC<=1.20x adam AND speedup>=3x. MIDDLE BPC<=1.5x OR speedup>=1.5x. HARD-FAIL BPC>1.5x AND speedup<1.5x.
## Smoke gate
Smoke (D=256): substrate_BPC=5.62 vs adam 4.48 (ratio=1.26x), speedup=2.7x -> MIDDLE (near HP; full D=512/800-steps should widen speedup). Ridge selftest fixed (linear target).
## Queue
overnight_queue timeout 21600s (_n8192). PROT-022 self-tests PASS. Corpus on runner.
