# exp_dev decisions 2026-06-23

- shipped substrate_dual_trace_scaling_v1 to overnight_queue; smoke PASS 28s wall; remote VERIFY PASS (queue_add.sh exit 0 + remote --self-test 2.4s); ETA 2-4h; pre-reg HARD_PASS=lift_grows+0.40bits at N16384/T1M vs N8192/T100k; MIDDLE_BAND=flat+/-0.10; HARD_FAIL=lift-halves; git commit 4fe6783a
