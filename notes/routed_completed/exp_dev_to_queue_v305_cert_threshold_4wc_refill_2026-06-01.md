# exp_dev queue routing: v305 cert threshold + PP-11 5-seed (2026-06-01)

Queues empty post-v305 verdict. Pause flag ABSENT. Shipped 2 anchors.

## Anchors

```
queue=remote_cpu_queue name=continuous_embedding_cert_threshold_v1_n16384 script=experiments/exp_continuous_embedding_cert_threshold_v1_n16384.py prereg=preregs/2026-06-01_continuous_embedding_cert_threshold_v1_n16384.md timeout=14400
queue=remote_cpu_queue name=reasoning_storage_4way_cleanup_v2_n16384 script=experiments/exp_reasoning_storage_4way_cleanup_v2_n16384.py prereg=preregs/2026-06-01_reasoning_storage_4way_cleanup_v2_n16384.md timeout=14400
```

## Smoke results
- cert_threshold_v1: N=512 corpus=128 seed=17 HARD_PASS in 0.05s. Score separation=0.990; mult=0.2 already cert=1.0 fp=0.0.
- 4way_cleanup_v2: N=512 n_chains=20 seed=17 4WC_HARD_PASS C_ratio=1.000 verify=1.000 in 0.21s.

## Strategic rationale
- cert_threshold_v1: Arm4 rescue R2 from v305 MIDDLE_BAND. Closes deletion-cert moat gap via threshold calibration. If HARD_PASS: audit-grade-vector-store row lifts 0.45-0.65 -> 0.55-0.70.
- 4way_cleanup_v2: PP-11 V1 R2 from v304. Extends 3-seed borderline to 5-seed. If HARD_PASS: PP-11 row lifts 0.50-0.65 -> 0.55-0.70.


---

Acted-on 2026-06-01: cert_threshold + 4wc anchors all shipped + verdicts processed across v306-v316 batches


Acted-on 2026-06-01: cert_threshold + 4wc anchors all shipped + verdicts processed across v306-v316 batches
