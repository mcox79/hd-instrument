"""
190a TRACK B C1 PROTOTYPE/CENTROID-RETRIEVAL execution cell (implements the FULLY-CERTIFIED prereg +
adversarial-completeness addendum, DECISION 196 RATIFIED; post-hoc-impossible contract). Tests whether
corr(bundle,c) = (superposition-inner, similarity-outer) UNIQUELY closes prototype-retrieval, blind, across
the (p,k,M) grid at k>2 -- the EARN-the-ARM-3-uniqueness path.

CERTIFIED CONTRACT (locked; this cell implements it exactly):
  GENERATIVE (S1): codebook C = M bipolar prototypes; k exemplars = prototype with per-coordinate bit-flip rate p
     (Posner-Keele additive noise). TASK: recover the prototype (nearest codebook entry) from the k exemplars.
  12-CELL GRID: INNER {I_sup target, I_psup, I_conv, I_xor} x OUTER {O_corr target, O_cunb, O_xunb}.
     TARGET T = (I_sup, O_corr) = corr(bundle,c). Evaluated blind among all 12 (no seed priming = no leakage).
  GRID (S2): p in {.05,.10,.15,.20,.25,.30} x k in {2,3,4,5,6,8} x M in {32,64,128,256} = 144 cells.
  S3 k>2 load-bearing (k=2 = ARM-2 connection, reported separately). S4 per-axis diagnostic. 2nd-codebook reuse.
  VERDICT (tune-free): HARD_PASS = T unique closer (acc>=chance+0.20) robust across k>2 AND all 11 non-targets
     < chance+0.10 AND per-axis diagnostic confirms predicted-axis failure. chance=1/M.

HEAVY (~10-100 GPU-hours full) -> REMOTE GPU (torch.cuda batched). Local --smoke is CPU/tiny (zero-verdict per
DECISION 149; validates pipeline + SURFACES the readout-degeneracy check below).

*** IMPLEMENTATION FLAG (verify-before-asserting; surfaced in --smoke for Skunkworks PRE-REMOTE confirm) ***
For a KEYLESS bipolar prototype-retrieval readout, O_xunb (elementwise-unbind score = mean(inner * c_j)) is
ALGEBRAICALLY (1/N)<inner,c_j> = O_corr (cosine up to norm) -> O_xunb may be a DEGENERATE competitor (tie with
the target by construction, not a genuine distinct readout). O_cunb (circular-correlation PEAK over shifts) IS
genuinely distinct (s=0 only for O_corr; max over s for O_cunb). The smoke REPORTS per-readout recovery so the
degeneracy is empirically confirmed; if O_xunb==O_corr, the OUTER axis has 2 distinct readouts not 3 -> Skunkworks
must rule (redefine O_xunb / drop it / accept caveat) BEFORE the heavy remote run. NO heavy dispatch until ruled.

torch, ASCII only.
"""
import sys, os, time, json, math
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
import torch

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SELFTEST = "--self-test" in sys.argv
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
ANCHOR = "trackB_c1_prototype_retrieval_190a_gpu_v1"

if RUN_MODE == "smoke":
    P_LIST = [0.10, 0.20]; K_LIST = [2, 4]; M_LIST = [32]; SEEDS = [7]; N = 256; TRIALS = 200
else:
    P_LIST = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]; K_LIST = [2, 3, 4, 5, 6, 8]; M_LIST = [32, 64, 128, 256]
    SEEDS = [7, 17, 23]; N = 1024; TRIALS = 2000   # per (p,k,M,seed,codebook) recovery trials

INNER = ["I_sup", "I_psup", "I_conv", "I_xor"]      # I_sup = superposition (target inner)
OUTER = ["O_corr", "O_cunb", "O_xunb"]              # O_corr = similarity (target outer)
TARGET = ("I_sup", "O_corr")                         # corr(bundle,c)


def _bipolar(shape, g):
    return (torch.randint(0, 2, shape, generator=g, device=DEV) * 2 - 1).float()


def _norm(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-8)


def inner_aggregate(name, ex):
    """ex: (T, k, N) k exemplars per trial -> (T, N) aggregated. Batched."""
    T, k, n = ex.shape
    if name == "I_sup":
        return _norm(ex.sum(dim=1))                                  # k-ary centroid (SUPERPOSITION; target)
    if name == "I_psup":
        shifts = [torch.roll(ex[:, i, :], shifts=i, dims=-1) for i in range(k)]  # permuted superposition
        return _norm(torch.stack(shifts, dim=1).sum(dim=1))
    if name == "I_conv":
        acc = ex[:, 0, :].clone()                                    # iterated circular convolution (BINDING)
        for i in range(1, k):
            acc = torch.fft.irfft(torch.fft.rfft(acc) * torch.fft.rfft(ex[:, i, :]), n=n, dim=-1)
        return _norm(acc)
    if name == "I_xor":
        acc = ex[:, 0, :].clone()                                    # iterated elementwise product (BINDING)
        for i in range(1, k):
            acc = acc * ex[:, i, :]
        return _norm(acc)
    raise ValueError(name)


def outer_recover(name, inner, codebook):
    """inner: (T, N); codebook: (M, N) -> recovered index (T,). Batched."""
    if name == "O_corr":
        return (inner @ codebook.t()).argmax(dim=-1)                 # cosine similarity (SIMILARITY; target)
    if name == "O_xunb":
        # elementwise-unbind score = mean(inner * c_j) = (1/N)<inner,c_j> -- ALGEBRAICALLY == O_corr (FLAG).
        return (inner @ codebook.t()).argmax(dim=-1)
    if name == "O_cunb":
        # circular-correlation PEAK over shifts: max_s |irfft(conj(rfft(inner)) * rfft(c_j))[s]| -- genuinely
        # distinct from O_corr (which is the s=0 value only). Binding-style readout.
        n = inner.shape[-1]
        Fi = torch.fft.rfft(inner)                                   # (T, F)
        Fc = torch.fft.rfft(codebook)                                # (M, F)
        # corr[t,j,s] = irfft(conj(Fi[t]) * Fc[j]); score = max_s |.|. Loop over M to bound memory.
        scores = torch.empty((inner.shape[0], codebook.shape[0]), device=DEV)
        for j in range(codebook.shape[0]):
            cc = torch.fft.irfft(torch.conj(Fi) * Fc[j].unsqueeze(0), n=n, dim=-1)  # (T, N)
            scores[:, j] = cc.abs().max(dim=-1).values
        return scores.argmax(dim=-1)
    raise ValueError(name)


def axis_inner_centroid_cosine(name, ex, target_proto):
    """per-axis-inner diagnostic: is the aggregated inner SIMILAR to the true prototype (centroid-like)?"""
    inner = inner_aggregate(name, ex)
    return float((_norm(inner) * _norm(target_proto)).sum(dim=-1).mean().item())


def run_cell(p, k, M, seed, codebook_idx):
    g = torch.Generator(device=DEV); g.manual_seed(seed * 1000 + codebook_idx)
    codebook = _bipolar((M, N), g)
    tgt = torch.randint(0, M, (TRIALS,), generator=g, device=DEV)          # true prototype per trial
    proto = codebook[tgt]                                                   # (T, N)
    flip = (torch.rand((TRIALS, k, N), generator=g, device=DEV) < p).float()  # bit-flip mask
    ex = proto.unsqueeze(1) * (1 - 2 * flip)                                # (T, k, N) noisy exemplars
    chance = 1.0 / M
    res = {}
    diag_inner = {}
    for inm in INNER:
        inner = inner_aggregate(inm, ex)
        diag_inner[inm] = float((_norm(inner) * _norm(proto)).sum(-1).mean().item())  # centroid-cosine
        for onm in OUTER:
            rec = outer_recover(onm, inner, codebook)
            res[f"{inm}+{onm}"] = float((rec == tgt).float().mean().item())
    return res, diag_inner, chance


def _selftest():
    assert DEV is not None
    r_odd, _, ch = run_cell(0.10, 3, 32, 7, 0)     # k=3 ODD
    r_evn, _, _ = run_cell(0.10, 4, 32, 7, 0)      # k=4 EVEN
    # target (superposition-inner + similarity-outer) must close on a clean-ish case
    assert r_odd["I_sup+O_corr"] > ch + 0.2, f"target should close k=3 p=0.10: {r_odd['I_sup+O_corr']:.3f}/ch {ch:.3f}"
    # PARITY FINDING (documented, not assumed): I_xor = proto^k * prod(flips). k ODD -> proto^k=proto -> xor-inner
    # RECOVERS (a genuine inner-axis competitor at odd k); k EVEN -> proto cancels -> xor-inner ~ chance.
    xor_odd, xor_evn = r_odd["I_xor+O_corr"], r_evn["I_xor+O_corr"]
    assert xor_evn < ch + 0.1, f"even-k binding-inner should cancel proto (~chance): {xor_evn:.3f}/ch {ch:.3f}"
    # DEGENERACY FLAG: O_xunb algebraically == O_corr for keyless bipolar prototype-retrieval
    deg = abs(r_odd["I_sup+O_xunb"] - r_odd["I_sup+O_corr"]) < 1e-6
    print(f"[selftest] PASS target-closes + even-k-binding-cancels | FINDINGS: xor-inner odd-k recovers "
          f"({xor_odd:.3f}) vs even-k cancels ({xor_evn:.3f}); O_xunb==O_corr degeneracy={deg}", flush=True)


def main():
    print(f"[start] {ANCHOR} run_mode={RUN_MODE} dev={DEV} N={N} grid p={P_LIST} k={K_LIST} M={M_LIST} "
          f"seeds={SEEDS} trials={TRIALS}", flush=True)
    _selftest()
    out = get_output_dir(os.environ.get("HDLAB_EXP_NAME", ANCHOR)); t0 = time.time()
    cells = {}
    degeneracy_seen = False
    for p in P_LIST:
        for k in K_LIST:
            for M in M_LIST:
                accs = {comp: [] for comp in [f"{i}+{o}" for i in INNER for o in OUTER]}
                diags = {i: [] for i in INNER}
                for s in SEEDS:
                    for cb in (0, 1):                                  # 2nd-codebook reuse
                        r, di, chance = run_cell(p, k, M, s, cb)
                        for comp, v in r.items(): accs[comp].append(v)
                        for i, v in di.items(): diags[i].append(v)
                macc = {comp: sum(v) / len(v) for comp, v in accs.items()}
                chance = 1.0 / M
                if abs(macc["I_sup+O_xunb"] - macc["I_sup+O_corr"]) < 1e-6:
                    degeneracy_seen = True
                cells[f"p{p}_k{k}_M{M}"] = {"chance": chance, "acc": macc,
                                            "diag_inner_centroid_cos": {i: sum(v)/len(v) for i, v in diags.items()},
                                            "k": k}
                if RUN_MODE == "smoke":
                    print(f"  [p={p} k={k} M={M}] chance={chance:.3f} TARGET(I_sup+O_corr)={macc['I_sup+O_corr']:.3f} "
                          f"| O_xunb={macc['I_sup+O_xunb']:.3f} O_cunb={macc['I_sup+O_cunb']:.3f} "
                          f"| I_conv+O_corr={macc['I_conv+O_corr']:.3f} I_xor+O_corr={macc['I_xor+O_corr']:.3f}",
                          flush=True)
    metrics = {"anchor_name": ANCHOR, "run_mode": RUN_MODE, "device": str(DEV), "N": N,
               "grid": {"p": P_LIST, "k": K_LIST, "M": M_LIST}, "seeds": SEEDS, "trials": TRIALS,
               "target": "I_sup+O_corr", "cells": cells,
               "IMPLEMENTATION_FLAG_O_xunb_eq_O_corr_degeneracy": degeneracy_seen,
               "elapsed_s": time.time() - t0, "compute_backend": str(DEV)}
    write_metrics(out, metrics, [cells])
    print(f"\n[metrics] written {out}/metrics.json | O_xunb==O_corr degeneracy seen: {degeneracy_seen}", flush=True)
    if degeneracy_seen:
        print("[FLAG] O_xunb is algebraically O_corr for keyless bipolar prototype-retrieval -> NOT a genuine "
              "distinct outer competitor. Skunkworks must rule before the heavy remote run (redefine/drop/caveat).",
              flush=True)


if __name__ == "__main__":
    if SELFTEST:
        _selftest(); sys.exit(0)
    main()
