"""Multi-scale smoke for depth-55 at N=4096."""
import sys
sys.path.insert(0, 'C:/dev/hd-instrument')
import torch
DEVICE = torch.device('cuda')

N_ACTIVE = 4096
N_CHAINS = 5
CHAIN_DEPTH = 55
SNAPSHOT_DEPTHS = [5, 10, 20, 30, 45, 55]

def cosine_sim_gpu(a, b):
    na = float(a.norm())
    nb = float(b.norm())
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(torch.dot(a, b)) / (na * nb)

gen = torch.Generator(device=DEVICE)
gen.manual_seed(7)

def bsc(m, n_d):
    return (torch.randint(0, 2, (m, n_d), generator=gen, device=DEVICE).float() * 2 - 1)

chains = [[bsc(1, N_ACTIVE).squeeze(0) for _ in range(CHAIN_DEPTH + 1)] for _ in range(N_CHAINS)]
H = torch.zeros((N_ACTIVE, N_ACTIVE), device=DEVICE, dtype=torch.float32)
for chain in chains:
    for h in range(CHAIN_DEPTH):
        H += torch.outer(chain[h + 1], chain[h]) / N_ACTIVE

results = []
for chain in chains:
    r = chain[0].clone()
    snaps = {}
    for step in range(1, CHAIN_DEPTH + 1):
        h_vec = H @ r
        r = torch.sign(h_vec)
        r[r == 0] = 1.0
        if step in SNAPSHOT_DEPTHS:
            snaps[step] = cosine_sim_gpu(r, chain[step])
    results.append(snaps)

mean = {d: sum(r[d] for r in results) / len(results) for d in SNAPSHOT_DEPTHS}
print("d55_multiscale_N4096: " + " ".join(f"d{d}:{mean[d]:.4f}" for d in SNAPSHOT_DEPTHS))
