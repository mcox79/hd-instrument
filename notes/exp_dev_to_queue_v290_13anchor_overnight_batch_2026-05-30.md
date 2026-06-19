# exp_dev -> queue: v290 13-anchor overnight batch (2026-05-30)

User-authorized batch closing the v290 cap_map (commit 16d7b82) with the
Modern Hopfield activation + Path D no-ceiling + adversarial vulnerabilities
findings.

## Batch composition
- 7 GPU anchors (overnight_queue): G5 G6 G7 G8 G9 G10 G12
- 6 CPU anchors (remote_cpu_queue): C1 C2 C3 C5 C6 C7

## Duplication skip
- G11 (KF-1 non-saturated regime) was SKIPPED. Rationale: G4
  multi_signal_kf1_refinement_v1 already covers M=8192 and M=16384
  non-saturated cells per its pre-reg. Adding G11 would be redundant.

## Queue entries (Schema A: inline key=value)

```
queue=overnight_queue name=modern_hopfield_ceiling_probe_gpu_v1_n8192 script=experiments/exp_modern_hopfield_ceiling_probe_gpu_v1_n8192.py prereg=preregs/2026-05-30_modern_hopfield_ceiling_probe_gpu_v1_n8192.md timeout=21600
queue=overnight_queue name=modern_hopfield_replication_gpu_v1_n8192 script=experiments/exp_modern_hopfield_replication_gpu_v1_n8192.py prereg=preregs/2026-05-30_modern_hopfield_replication_gpu_v1_n8192.md timeout=21600
queue=overnight_queue name=path_d_24n_32n_envelope_v1_n4096 script=experiments/exp_path_d_24n_32n_envelope_v1_n4096.py prereg=preregs/2026-05-30_path_d_24n_32n_envelope_v1_n4096.md timeout=14400
queue=overnight_queue name=adversarial_codebook_collision_defense_probe_v1_n4096 script=experiments/exp_adversarial_codebook_collision_defense_probe_v1_n4096.py prereg=preregs/2026-05-30_adversarial_codebook_collision_defense_probe_v1_n4096.md timeout=14400
queue=overnight_queue name=alternative_edit_isolation_mechanisms_v1_n4096 script=experiments/exp_alternative_edit_isolation_mechanisms_v1_n4096.py prereg=preregs/2026-05-30_alternative_edit_isolation_mechanisms_v1_n4096.md timeout=14400
queue=overnight_queue name=multi_hop_adversarial_concurrent_edits_v1_n4096 script=experiments/exp_multi_hop_adversarial_concurrent_edits_v1_n4096.py prereg=preregs/2026-05-30_multi_hop_adversarial_concurrent_edits_v1_n4096.md timeout=14400
queue=overnight_queue name=memory_pattern_characterization_v1_n4096 script=experiments/exp_memory_pattern_characterization_v1_n4096.py prereg=preregs/2026-05-30_memory_pattern_characterization_v1_n4096.md timeout=14400
queue=remote_cpu_queue name=modern_hopfield_cpu_backup_extended_v1_n16384 script=experiments/exp_modern_hopfield_cpu_backup_extended_v1_n16384.py prereg=preregs/2026-05-30_modern_hopfield_cpu_backup_extended_v1_n16384.md timeout=86400
queue=remote_cpu_queue name=multi_hop_caching_baseline_v1_n4096 script=experiments/exp_multi_hop_caching_baseline_v1_n4096.py prereg=preregs/2026-05-30_multi_hop_caching_baseline_v1_n4096.md timeout=14400
queue=remote_cpu_queue name=substrate_state_compression_v1_n4096 script=experiments/exp_substrate_state_compression_v1_n4096.py prereg=preregs/2026-05-30_substrate_state_compression_v1_n4096.md timeout=14400
queue=remote_cpu_queue name=edit_audit_trail_refinement_v1_n4096 script=experiments/exp_edit_audit_trail_refinement_v1_n4096.py prereg=preregs/2026-05-30_edit_audit_trail_refinement_v1_n4096.md timeout=14400
queue=remote_cpu_queue name=substrate_operation_cost_modeling_v1_n4096 script=experiments/exp_substrate_operation_cost_modeling_v1_n4096.py prereg=preregs/2026-05-30_substrate_operation_cost_modeling_v1_n4096.md timeout=14400
queue=remote_cpu_queue name=path_d_cpu_latency_profiling_v1_n4096 script=experiments/exp_path_d_cpu_latency_profiling_v1_n4096.py prereg=preregs/2026-05-30_path_d_cpu_latency_profiling_v1_n4096.md timeout=14400
```

## Sequencing
Batch queues behind running V2 sustained_workload_24h_baseline (~21h
remaining) and G1-G4 GPU pending. Once those drain, the 7 GPU entries
above will run sequentially. The 6 CPU entries run in parallel on
remote_cpu_queue starting immediately (CPU queue empty pre-ship).

## Notes
- All 13 self-tests pass at module scope.
- All 13 smoke runs produce verdicts cleanly (no crashes).
- All 13 PROT-018 _n<N> bindings verified (grep matched production N).
- All 13 anchor names verified unique against current queues + outcomes.
- All scripts include stdout reconfigure block + ASCII verdict_msg.
- All scripts import multi-hop mechanisms from experiments/_multi_hop_mechanisms.py
  where applicable (G7, G8, G9, G10, G12, C2, C3, C5, C6, C7).
- All scripts use _seed_checkpoint per-cell-seed resume (PROT-021).
