# exp_dev decisions 2026-06-23

- shipped substrate_dual_trace_scaling_v1 to overnight_queue; smoke PASS 28s wall; remote VERIFY PASS (queue_add.sh exit 0 + remote --self-test 2.4s); ETA 2-4h; pre-reg HARD_PASS=lift_grows+0.40bits at N16384/T1M vs N8192/T100k; MIDDLE_BAND=flat+/-0.10; HARD_FAIL=lift-halves; git commit 4fe6783a
2026-06-23: shipped substrate_per_context_decode_temperature_LM_v1 to local_cpu_queue; smoke PASS 0.4s; predispatch PROCEED; PROT-018 N/A (no _nN suffix); HARD_PASS bar +0.10 BPC lift over global T (7.3065); Yu-Dayan 2005 P=0.45; timeout_s=3600; commit 7d0a9e96