# Prereg: pca_bottleneck_zkl_sweep_v1
## Anchor
pca_bottleneck_zkl_sweep_v1
## Queue
overnight_queue (GPU; T5 round-trip + Llama; sanity gate then d-sweep)
## Decision rules
Case A ZKL<0.10 at d in {20,25,30} -> HIPAA recovered. Case B only d<=15. Case C ZKL>=0.15 all d -> pivot Hyp B/C.
