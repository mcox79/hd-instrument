# exp_dev -> queue: continuous_embedding_storage (2026-05-31)

Shipment record for anchor continuous_embedding_storage_substrate_v1_n16384.

Smoke: PASS (N=1024 local CPU 0.10s + N=4096 multi-scale 0.32s).
Self-test: PASS on remote (FAISS OK, OpenMP KMP_DUPLICATE_LIB_OK fix applied).
PROT-018: OK (N=16384 in docstring, validator accepted).
PROT-019: OK (timeout=21600 >= floor 21600 for _n16384).
PROT-021: OK (_seed_checkpoint imported, 3 seeds checkpointed).
REMOTE VERIFY: PASS (queue_add.sh exit 0; entry confirmed in remote queue.json).

Source routing: notes/strategy_request_to_strategy_continuous_embedding_storage_2026-05-31.md

```
queue=overnight_queue name=continuous_embedding_storage_substrate_v1_n16384 script=experiments/exp_continuous_embedding_storage_substrate_v1_n16384.py prereg=prereqs/2026-05-31_continuous_embedding_storage_substrate_v1_n16384.md timeout=21600
```
