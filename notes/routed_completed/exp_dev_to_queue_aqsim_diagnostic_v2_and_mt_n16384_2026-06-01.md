# exp_dev_to_queue: AQSIM diagnostic v2 + multi-tenant N=16384 (2026-06-01)

Filed by exp_dev:sonnet 2026-06-01.

## Anchor 1: aqsim_3way_diagnostic_verbose_v2_n4096

```
queue=remote_cpu_queue name=aqsim_3way_diagnostic_verbose_v2_n4096 script=experiments/exp_aqsim_3way_diagnostic_verbose_v2_n4096.py prereg=preregs/2026-06-01_aqsim_3way_diagnostic_verbose_v2_n4096.md timeout=14400
```

Status: SHIPPED + REMOTE VERIFIED (queue_add.sh exit 0, entry present in remote queue.json).
Smoke: DIAGNOSTIC_HARD_PASS in 21.8s.
Fix: v1 wrote metrics to data/<NAME>/ (missing exp_ prefix); v2 uses data/exp_<NAME>/.
Root causes confirmed: (1) checkpoint contamination + (2) Kerdock odd-log2 N=8192.
PROT-018/019/021 all PASS.

## Anchor 2: multi_tenant_arch1_full_v1_n16384

```
queue=remote_cpu_queue name=multi_tenant_arch1_full_v1_n16384 script=experiments/exp_multi_tenant_arch1_full_v1_n16384.py prereg=preregs/2026-06-01_multi_tenant_arch1_full_v1_n16384.md timeout=21600
```

Status: SHIPPED + REMOTE VERIFIED (queue_add.sh exit 0, entry present in remote queue.json).
Smoke: MT_ARCH1_HARD_PASS at N=1024 and N=4096 (multi-scale smoke), zero contamination.
Strategic row: PP-13 (Multi-tenant isolation 0.75-0.90 VALIDATED).
Staged escalation: N=4096 HARD_PASS confirmed -> this N=16384 intermediate -> N=32768 authorized on PASS.
PROT-018/019/021 all PASS.


---

**Acted-on 2026-06-01:** AQSIM v2 root cause exp_ prefix bug IDENTIFIED + multi-tenant N=16384 staging IN-FLIGHT; cap_map v318 annotations applied.
