"""Queue two decisive followup experiments + clear K=1024 zombie."""
import json
from pathlib import Path

REPO = Path(r"C:\dev\hd-instrument")

# 1) Fork ACF K-dependent: K=2944 only, 100 trials (settles ACF dip)
acf_base = (REPO / "experiments" / "exp_wave14b_acf_K_dependent.py").read_text()
acf_2944 = acf_base.replace(
    "K_SWEEP = [2048, 2304, 2560, 3072, 4096, 6144]",
    "K_SWEEP = [2944]"
).replace(
    "NUM_TRIALS = 30",
    "NUM_TRIALS = 100"
).replace(
    "exp_wave14b_acf_K_dependent",
    "exp_wave14b_acf_K2944_100trials"
)
(REPO / "experiments" / "exp_wave14b_acf_K2944_100trials.py").write_text(acf_2944)
print("wrote exp_wave14b_acf_K2944_100trials.py")

# 2) Fork r3_unigram_diagnostic to add sparse-gated unigram mode
# Settles: is +0.032 R3 effect just sparsity-matched class prior?
src = (REPO / "experiments" / "exp_wave14b_r3_unigram_diagnostic.py").read_text()
# Add sparse_unigram mode: same query_active gating as R3, but bias is unigram log-prior
src2 = src.replace(
    'elif mode == "unigram":\n            combined_logits = BETA * sims + GAMMA * unigram_logp.unsqueeze(1)',
    '''elif mode == "unigram":
            combined_logits = BETA * sims + GAMMA * unigram_logp.unsqueeze(1)
        elif mode == "sparse_unigram":
            qa = query_active(idx_b, ppmi)
            fire_count = qa.sum(dim=1, keepdim=True)
            sparse_bias = fire_count.T * unigram_logp.unsqueeze(1)
            combined_logits = BETA * sims + GAMMA * sparse_bias'''
).replace(
    '    post_unigram = eval_with_bias(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A,\n                                   used_A, "unigram", ppmi, vote_logp, unigram_logp)',
    '''    post_unigram = eval_with_bias(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                                   used_A, "unigram", ppmi, vote_logp, unigram_logp)
    post_sparse_unigram = eval_with_bias(W_AB, byte_atoms, pos_atoms, test_a, pool_A, labels_A,
                                          used_A, "sparse_unigram", ppmi, vote_logp, unigram_logp)'''
).replace(
    '    return {\n        "post_off": post_off,\n        "post_r3": post_r3,\n        "post_unigram": post_unigram,',
    '''    return {
        "post_off": post_off,
        "post_r3": post_r3,
        "post_unigram": post_unigram,
        "post_sparse_unigram": post_sparse_unigram,
        "sparse_unigram_gain": post_off - post_sparse_unigram,
        "r3_minus_sparse_unigram": (post_off - post_r3) - (post_off - post_sparse_unigram),'''
).replace(
    "exp_wave14b_r3_unigram_diagnostic",
    "exp_wave14b_r3_sparse_unigram_diagnostic"
)
(REPO / "experiments" / "exp_wave14b_r3_sparse_unigram_diagnostic.py").write_text(src2)
print("wrote exp_wave14b_r3_sparse_unigram_diagnostic.py")

# 3) Clear K=1024 zombie + queue followups + N8192_K256 already in queue
gpu_q_path = REPO / "data" / "overnight_queue" / "queue.json"
gpu_q = json.loads(gpu_q_path.read_text())
for e in gpu_q["experiments"]:
    if e["name"] == "r10_best_config_K1024" and e["status"] == "running":
        e["status"] = "failed"
        e["error"] = "orphaned during cycle 1 runner crash; needs requeue"
gpu_new = [
    {"name": "r10_best_config_K1024_retry", "script": "experiments/exp_wave14b_r10_best_config_K1024.py",
     "status": "pending",
     "purpose": "Retry K=1024 after zombie clear. Extends R10 best-config headline; predicted toward +0.7 if K=8 to K=512 trend continues.",
     "timeout_s": 14400},
    {"name": "r3_sparse_unigram_diagnostic", "script": "experiments/exp_wave14b_r3_sparse_unigram_diagnostic.py",
     "status": "pending",
     "purpose": "Settles R3 mechanism: sparse-gated unigram (same query_active as R3 but uses unigram log-prior). If matches R3 +0.032, R3 reframed as sparsity-gated class-prior. If R3 still residual >0.01, substrate-unique signal.",
     "timeout_s": 1800},
]
gpu_q["experiments"].extend(gpu_new)
gpu_q_path.write_text(json.dumps(gpu_q, indent=2))

cpu_q_path = REPO / "data" / "remote_cpu_queue" / "queue.json"
cpu_q = json.loads(cpu_q_path.read_text())
cpu_new = [
    {"name": "acf_K2944_100trials", "script": "experiments/exp_wave14b_acf_K2944_100trials.py",
     "status": "pending",
     "purpose": "Settles ACF K=2944 dip: 100 trials (vs 30) at K=2944 only. If recovery returns to ~75%, dip was noise. If <=60%, real resonance.",
     "timeout_s": 5400},
]
cpu_q["experiments"].extend(cpu_new)
cpu_q_path.write_text(json.dumps(cpu_q, indent=2))

print("\nGPU pending after refill:")
for e in gpu_q["experiments"]:
    if e["status"] == "pending":
        print(f"  - {e['name']}")
print("\nCPU pending after refill:")
for e in cpu_q["experiments"]:
    if e["status"] == "pending":
        print(f"  - {e['name']}")
