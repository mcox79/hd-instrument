"""
exp_substrate_gpu_parity_v1 -- substrate FHRR algebra GPU parity (torch.complex64 on CUDA) -- GPU.

ROUTING: Wave-1 support / deployment validation. The Sprint-4 engineered-wrapper gates are validated on CPU numpy
  (complex64). Production substrate-as-LLM-memory will run on GPU, so this confirms the SAME algebra reproduces in
  torch.complex64 on CUDA: (A) basic bind/unbind recall, (B) write-lock locked-core protection, (C) per-role domain
  isolation vs shared, (D) 3x-redundant averaging under noise. Each gate ported faithfully to torch and run on DEV=cuda;
  PASS = GPU reproduces the CPU-validated band. Fast (tiny complex vectors; seconds). N=8192. Uses torch.cuda (PROT-020).
PRE-REGISTERED: HARD-PASS all 4 reproduce CPU bands (basic>=0.95, write-lock>=0.95, per-role>=0.90 AND >shared, 3x>=0.95).
  MIDDLE 3/4. HARD-FAIL <3 (GPU algebra diverges from CPU -> deployment blocker).
ASCII-only. write_metrics + per-seed checkpoint. PROT-018/020/021 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _seed_checkpoint import get_output_dir, write_metrics, write_partial_key, load_partial_key
ANCHOR_NAME = "substrate_gpu_parity_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192   # always full dim (complex64 vectors are tiny ~64KB; gate params tuned for 8192); smoke only reduces seeds
def _selftest():
    # softmax/argmax-free; just confirm complex algebra identity holds in pure python numpy proxy
    import numpy as _np
    a = _np.exp(1j * 0.3); b = _np.exp(1j * 0.7)
    assert abs((a * b) * _np.conj(b) - a) < 1e-6, "bind/unbind identity"
    print("[selftest] PASS: substrate-gpu-parity (bind/unbind identity)", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)
def _g(seed):
    return torch.Generator(device=DEV).manual_seed(int(seed))
def cphasor(m, d, g):
    ang = (torch.rand((m, d), generator=g, device=DEV) * 2 - 1) * math.pi
    return torch.polar(torch.ones_like(ang), ang).to(torch.complex64)
def cnorm(v):
    return torch.polar(torch.ones_like(v.real), v.angle()).to(torch.complex64)
def cidx(v, book):
    return int(torch.argmax((book @ torch.conj(v)).real))
def basic_recall(seed):
    g = _g(seed); K = 80; V = 400
    keys = cphasor(K, N, g); vals = cphasor(V, N, g); truth = torch.randint(0, V, (K,), generator=g, device=DEV)
    mem = cnorm(sum((keys[i] * vals[truth[i]] for i in range(K)), torch.zeros(N, dtype=torch.complex64, device=DEV)))
    return sum(cidx(mem * torch.conj(keys[i]), vals) == int(truth[i]) for i in range(K)) / K
def write_lock(seed):
    g = _g(seed); NS = 8; PER = 6; V = 400; CORE = 4
    keys = cphasor(NS * PER, N, g); vals = cphasor(V, N, g); truth = torch.randint(0, V, (NS * PER,), generator=g, device=DEV)
    shards = [torch.zeros(N, dtype=torch.complex64, device=DEV) for _ in range(NS)]; locked = [False] * NS; cf = []
    for s in range(NS):
        for j in range(PER):
            idx = s * PER + j; shards[s] = shards[s] + keys[idx] * vals[truth[idx]]
            if s < CORE: cf.append((s, idx))
        if s < CORE: locked[s] = True
    for _w in range(1500):
        s = int(torch.randint(0, NS, (1,), generator=g, device=DEV))
        if not locked[s]: shards[s] = shards[s] + cphasor(1, N, g)[0] * vals[int(torch.randint(0, V, (1,), generator=g, device=DEV))]
    return sum(cidx(cnorm(shards[s]) * torch.conj(keys[idx]), vals) == int(truth[idx]) for (s, idx) in cf) / len(cf)
def per_role(seed):
    g = _g(seed); ND = 3; PD = 280; V = 600
    keys = cphasor(ND * PD, N, g); vals = cphasor(V, N, g); truth = torch.randint(0, V, (ND * PD,), generator=g, device=DEV)
    pr = [cnorm(sum((keys[d * PD + j] * vals[truth[d * PD + j]] for j in range(PD)), torch.zeros(N, dtype=torch.complex64, device=DEV))) for d in range(ND)]
    shared = cnorm(sum((keys[i] * vals[truth[i]] for i in range(ND * PD)), torch.zeros(N, dtype=torch.complex64, device=DEV)))
    ph = 0; sh = 0; n = 0
    for d in range(ND):
        for j in range(0, PD, 8):
            idx = d * PD + j; ph += int(cidx(pr[d] * torch.conj(keys[idx]), vals) == int(truth[idx])); sh += int(cidx(shared * torch.conj(keys[idx]), vals) == int(truth[idx])); n += 1
    return ph / n, sh / n
def redundant3x(seed):
    g = _g(seed); K = 80; V = 400; NOISE = 2.2
    keys = cphasor(K, N, g); vals = cphasor(V, N, g); truth = torch.randint(0, V, (K,), generator=g, device=DEV)
    base = cnorm(sum((keys[i] * vals[truth[i]] for i in range(K)), torch.zeros(N, dtype=torch.complex64, device=DEV)))
    def noisy():
        nz = (torch.randn(N, generator=g, device=DEV) + 1j * torch.randn(N, generator=g, device=DEV)).to(torch.complex64)
        return cnorm(base + NOISE * nz)
    copies = [noisy() for _ in range(3)]
    merged = cnorm(sum(copies, torch.zeros(N, dtype=torch.complex64, device=DEV)))
    return sum(cidx(merged * torch.conj(keys[i]), vals) == int(truth[i]) for i in range(K)) / K
def run(out_dir) -> Dict:
    seeds = [1] if SMOKE else [1, 2, 3]
    suf = "_smoke" if SMOKE else "_full"
    A = []; B = []; C = []; Csh = []; D = []
    for s in seeds:
        rec = load_partial_key(out_dir, str(s) + suf)
        if rec is None:
            a = basic_recall(s); b = write_lock(s); c, csh = per_role(s); d = redundant3x(s)
            rec = {"basic": a, "write_lock": b, "per_role": c, "shared": csh, "redundant3x": d}
            write_partial_key(out_dir, str(s) + suf, rec)
            print("  seed %d: basic=%.3f write-lock=%.3f per-role=%.3f (shared=%.3f) 3x=%.3f" % (s, a, b, c, csh, d), flush=True)
        else:
            print("  seed %d (resumed): basic=%.3f write-lock=%.3f per-role=%.3f 3x=%.3f" % (s, rec["basic"], rec["write_lock"], rec["per_role"], rec["redundant3x"]), flush=True)
        A.append(rec["basic"]); B.append(rec["write_lock"]); C.append(rec["per_role"]); Csh.append(rec["shared"]); D.append(rec["redundant3x"])
    mean = lambda x: round(float(sum(x) / len(x)), 3)
    return {"basic": mean(A), "write_lock": mean(B), "per_role": mean(C), "shared": mean(Csh), "redundant3x": mean(D), "n_seeds": len(seeds), "device": str(DEV)}
def verdict(r) -> Tuple[str, str]:
    a = r["basic"]; b = r["write_lock"]; c = r["per_role"]; sh = r["shared"]; d = r["redundant3x"]
    s = "basic=%.3f write-lock=%.3f per-role=%.3f shared=%.3f 3x=%.3f dev=%s" % (a, b, c, sh, d, r["device"])
    ok = (a >= 0.95) + (b >= 0.95) + (c >= 0.90 and c > sh + 0.15) + (d >= 0.95)
    if ok == 4:
        return ("HARD_PASS", "HARD_PASS: substrate FHRR algebra reproduces on GPU (torch.complex64/CUDA) -- basic recall, write-lock core protection, per-role isolation, 3x-redundant denoise all match CPU numpy bands. Substrate is GPU-deployable; no algebra divergence. " + s)
    if ok == 3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 3/4 gates reproduce on GPU. " + s)
    return ("HARD_FAIL", "HARD_FAIL: <3 gates reproduce on GPU -- torch.complex64 algebra diverges from CPU (deployment blocker). " + s)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run(out_dir)
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": r.get("n_seeds", 3), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
