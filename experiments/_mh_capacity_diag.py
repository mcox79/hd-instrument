"""Diagnostic only: find modern-vs-classical regime at N=65536 with heavier noise + M sweep."""
import torch, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

N = 65536
dev = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
print("device:", dev, "N:", N, flush=True)

for noise_stdev in [0.5, 1.0, 1.5, 2.0]:
    print(f"--- noise_stdev={noise_stdev} ---", flush=True)
    gen = torch.Generator(device=dev).manual_seed(7)
    for M in [10000, 30000, 100000]:
        try:
            K_raw = torch.empty(M, N, device=dev)
            K_raw.bernoulli_(0.5, generator=gen).mul_(2).sub_(1)
            K = K_raw / K_raw.norm(dim=1, keepdim=True)
            NQ = 50
            perm = torch.randperm(M, generator=gen, device=dev)[:NQ]
            Q_raw = K_raw[perm].clone()
            noise = torch.empty_like(Q_raw); noise.normal_(0, noise_stdev, generator=gen)
            Q_n = (Q_raw + noise); Q_n = Q_n / Q_n.norm(dim=1, keepdim=True)
            sims = Q_n @ K.T
            line = f"M={M:7d} alpha={M/N:.3f}"
            for b in [1.0, 4.0, 8.0]:
                w = torch.softmax(b * sims, dim=1)
                ret = w @ K
                sims2 = ret @ K.T
                modern = float((torch.argmax(sims2, dim=1) == perm).float().mean().item())
                line += f" m_b{b:.0f}={modern:.3f}"
            y = sims @ K / N
            sims3 = y @ K.T
            classical = float((torch.argmax(sims3, dim=1) == perm).float().mean().item())
            line += f" cls={classical:.3f}"
            # plain (no retrieval; just argmax sims)
            plain = float((torch.argmax(sims, dim=1) == perm).float().mean().item())
            line += f" plain={plain:.3f}"
            print(line, flush=True)
            del K, K_raw, Q_raw, Q_n, sims, sims3, perm
            if dev.type == "cuda":
                torch.cuda.empty_cache()
        except torch.cuda.OutOfMemoryError as e:
            print(f"M={M} OOM: {e}", flush=True)
            if dev.type == "cuda":
                torch.cuda.empty_cache()
