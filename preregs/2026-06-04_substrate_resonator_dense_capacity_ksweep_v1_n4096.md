# Prereg: substrate_resonator_dense_capacity_ksweep_v1_n4096
## Anchor
substrate_resonator_dense_capacity_ksweep_v1_n4096
## Routing
exp_dev_handoff_research_resonator_capacity_substrate_scale (anchor 1: dense resonator K-sweep). GPU, $0.
## Scientific question
Resonator (Frady-Kent-Sommer-Kanerva) factorizes c=f1(x)..(x)fK into K factors via iterative unbind+cleanup.
At N=4096, V=100, what is K_max (max factors at >=99% accuracy)? Sets the Mode-4 NC1 capacity envelope.
K {5..11}, B=200 trials, T=50 iters, 3 seeds.
## Pre-registered bands
HARD-PASS K_max>=8. MIDDLE K_max 5-7. HARD-FAIL K_max<5.
## Formula self-tests (PROT-022)
bipolar bind self-inverse / K=2 resonator recovers / argmax cleanup / bipolar codebook. [PASS]
## Smoke gate
Smoke PASSED on remote GPU (N=512,V=50): K=2 acc=1.0, degrades with K (K_max=2 at tiny N=512, expected;
resonator capacity scales with N). Full N=4096 is the K_max test.
## PROT-018/019/021
_n4096 -> N=4096. timeout floor 14400s. 3 seeds.
## Queue
overnight_queue (GPU; batched resonator cleanup matmuls).
