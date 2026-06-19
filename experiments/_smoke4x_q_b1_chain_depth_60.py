"""Multi-scale smoke helper: runs q_b1_chain_depth_60 at N=4096 (smoke x4 per MULTI-SCALE SMOKE rule)."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
os.environ["HDLAB_RUN_MODE"] = "smoke"
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import time, json
import torch
import torch.cuda

DEVICE = torch.device('cuda')
print(f"[GPU] {torch.cuda.get_device_name(0)}", flush=True)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "q_b1_chain_depth_60_v1_n8192"
N_ACTIVE = 4096  # N_smoke * 4
SEEDS = [7, 17]
N_CHAINS = 5
M_BACKGROUND = 30
CHAIN_DEPTH = 60
SNAPSHOT_DEPTHS = [1, 3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]

def cosine_sim_gpu(a, b):
    na = float(a.norm()); nb = float(b.norm())
    if na < 1e-12 or nb < 1e-12: return 0.0
    return float(torch.dot(a, b)) / (na * nb)

gen = torch.Generator(device=DEVICE)
for seed in SEEDS:
    gen.manual_seed(seed)
    def bsc(m, n_d):
        return (torch.randint(0, 2, (m, n_d), generator=gen, device=DEVICE).float() * 2 - 1)
    chains = [[bsc(1, N_ACTIVE).squeeze(0) for _ in range(CHAIN_DEPTH + 1)] for _ in range(N_CHAINS)]
    bg_keys = bsc(M_BACKGROUND, N_ACTIVE)
    bg_vals = bsc(M_BACKGROUND, N_ACTIVE)
    H = torch.zeros((N_ACTIVE, N_ACTIVE), device=DEVICE, dtype=torch.float32)
    for chain in chains:
        for h in range(CHAIN_DEPTH):
            H += torch.outer(chain[h+1], chain[h]) / N_ACTIVE
    for i in range(M_BACKGROUND):
        H += torch.outer(bg_vals[i], bg_keys[i]) / N_ACTIVE
    snap = {d: [] for d in SNAPSHOT_DEPTHS}
    for chain in chains:
        r = chain[0].clone()
        depth_res = {}
        for step in range(1, CHAIN_DEPTH + 1):
            h_vec = H @ r; r = torch.sign(h_vec); r[r==0] = 1.0
            if step in SNAPSHOT_DEPTHS: depth_res[step] = cosine_sim_gpu(r, chain[step])
        for d in SNAPSHOT_DEPTHS: snap[d].append(depth_res.get(d, 0.0))
    mean = {d: float(sum(v)/len(v)) if v else 0. for d, v in snap.items()}
    alpha = (N_CHAINS * CHAIN_DEPTH + M_BACKGROUND) / N_ACTIVE
    print(f"[N4096 seed={seed}] alpha={alpha:.4f} snaps={' '.join(f'd{d}:{mean[d]:.4f}' for d in [5,10,20,30,45,60])}", flush=True)
    del H

print("[multi-scale smoke DONE]", flush=True)
