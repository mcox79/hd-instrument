"""
PRIMITIVE 1 -- residue-FPE cell (DECISION 210 STEP 3; implements the RATIFIED Skunkworks prereg EXACTLY;
cert-chain design->prereg->cell). TIER-3 foundation primitive: continuous-magnitude encoding via Fractional
Power Encoding (FPE) with residue (coprime-base) layering, decoded by CRT + resonator factorization.

CELL PIPELINE (locked):
  ENCODE: per-base channel V_b(x)[n] = exp(i * 2pi * a_{b,n} * x / m_b), a_{b,n} ~ U{1..m_b-1} integer harmonics
     (-> channel periodic in x with period m_b; encodes x mod m_b). residue_fpe(x) = elementwise PRODUCT over the r
     coprime bases (binds the per-base channels). Range = prod(m_b); resources ~ sum over bases (log-scaling). For
     GATE-A the single-channel continuous FPE uses theta ~ U(-pi,pi) (kernel = sinc). Unit-magnitude complex (FHRR).
  DECODE: residue-tuple -> x via per-base resonator cleanup (correlate against each base's m_b codebook) + CRT.
  Substrate-internal (complex-exponent elementwise + r channels + CRT); NO learned codebook (11th rule).

GATES (tune-free; honest-negative per gate):
  GATE-A (G1) closed-form kernel: measured sim(V^x,V^y) vs E_theta[cos(d theta)] = sinc(d); PASS max_d|.|<=TOL.
  GATE-B (G3) CRT uniqueness (theorem; self-test) + decode_acc within range (1.0 / >=0.99 bar).
  GATE-C (G5; OPEN; remote-heavy): C1 product-kernel base-independence VERIFY-NOT-ASSUME (combined vs product of
     per-base kernels; the O_xunb lesson -- MEASURE, do not assume); C2 resolution/capacity envelope as a FUNCTION.
  Honest scope: integer-residue + single-channel continuous-FPE GROUNDED; COMBINED continuous-residue product-kernel
     is the OPEN question; Primitive-1 load-bearing claim is BOUNDED by the GATE-C envelope (NOT assumed unbounded).

queue-compatible (--self-test/--smoke/full); torch device-agnostic (cuda if available) + BATCHED. ASCII only.
"""
import sys, os, time, math
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
import torch

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SELFTEST = "--self-test" in sys.argv
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
ANCHOR = "primitive_1_residue_FPE_v1"

if RUN_MODE == "smoke":
    N = 1024; SEEDS = [7]; BASES = [3, 5, 7]; GRID_PTS = 200; ENV_RES = [0.05, 0.2, 0.5]
else:
    N = 4096; SEEDS = [7, 17, 23]; BASES = [3, 5, 7, 11]; GRID_PTS = 1000; ENV_RES = [0.02, 0.05, 0.1, 0.2, 0.5, 1.0]

TOL_A = 0.02 + 3.0 * math.sqrt(1.0 / N)   # GATE-A finite-N fluctuation band (tune-free; prereg)
TOL_C1 = 0.02 + 3.0 * math.sqrt(1.0 / N)  # GATE-C1 product-kernel band (same finite-N discipline)
DECODE_BAR = 0.99                          # GATE-B decode-accuracy bar (resonator convergence allowance)


def _gen(seed):
    return torch.Generator(device=DEV).manual_seed(seed)


def sinc(d):
    # normalized sinc = sin(pi d)/(pi d); =1 at d=0
    d = torch.as_tensor(d, dtype=torch.float64, device=DEV)
    out = torch.where(d.abs() < 1e-12, torch.ones_like(d), torch.sin(math.pi * d) / (math.pi * d + 1e-30))
    return out


# ---- single-channel continuous FPE (GATE-A) ----
def fpe_single(x, theta):
    # x: (..,) ; theta: (N,) ; returns complex (.., N) = exp(i x theta)
    ph = x.unsqueeze(-1) * theta.unsqueeze(0)
    return torch.exp(1j * ph)


def gate_A(seed):
    g = _gen(seed)
    theta = (torch.rand(N, generator=g, device=DEV, dtype=torch.float64) * 2 - 1) * math.pi  # U(-pi,pi)
    ds = torch.linspace(-3.0, 3.0, GRID_PTS, dtype=torch.float64, device=DEV)
    x0 = torch.zeros_like(ds)
    Vx = fpe_single(x0, theta); Vy = fpe_single(ds, theta)
    measured = (Vx * Vy.conj()).real.mean(dim=-1)   # (1/N) Re<V^x, conj(V^y)>, x=0 so d = -ds (cos even)
    closed = sinc(ds)
    err = (measured - closed).abs().max().item()
    return {"max_kernel_err": err, "tol": TOL_A, "pass": err <= TOL_A}


# ---- residue channels (GATE-B / GATE-C) ----
def base_channels(seed, bases):
    """Per-base integer harmonics a_{b,n} ~ U{1..m_b-1}; channel V_b(x)=exp(i 2pi a_b x / m_b) periodic mod m_b."""
    g = _gen(seed)
    chans = []
    for m in bases:
        a = torch.randint(1, m, (N,), generator=g, device=DEV).to(torch.float64)  # harmonics in {1..m-1}
        chans.append((m, a))
    return chans


def residue_fpe(x, chans):
    # x: (B,) ; returns complex (B, N) = prod_b exp(i 2pi a_b x / m_b)
    out = torch.ones((x.shape[0], N), dtype=torch.complex128, device=DEV)
    for (m, a) in chans:
        ph = (2 * math.pi / m) * x.unsqueeze(-1) * a.unsqueeze(0)
        out = out * torch.exp(1j * ph)
    return out


def per_base_vec(m, a, r):
    # codebook vector for residue value r at base m: exp(i 2pi a r / m)
    ph = (2 * math.pi / m) * float(r) * a
    return torch.exp(1j * ph)


def _codebooks(chans):
    return [torch.stack([per_base_vec(m, a, r) for r in range(m)], dim=0) for (m, a) in chans]  # each (m, N)


def resonator_decode(Rx, chans, cbs, iters=50):
    """RESONATOR factorization (prereg 'CRT + resonator'): iteratively unbind the OTHER bases' current estimates
    from the combined vector, then cleanup the residual against the per-base codebook. Removes cross-base
    interference that naive per-base correlation cannot. Rx: (N,) complex. Returns list of residue ints."""
    nb = len(chans)
    est = [cbs[b][0].clone() for b in range(nb)]   # init estimate = residue-0 codeword per base
    last = None
    for _ in range(iters):
        picks = []
        for b in range(nb):
            other = torch.ones(N, dtype=torch.complex128, device=DEV)
            for b2 in range(nb):
                if b2 != b:
                    other = other * est[b2]
            unbound = Rx * other.conj()                                  # remove other bases -> ~ base-b channel
            sims = (unbound.unsqueeze(0) * cbs[b].conj()).real.mean(dim=-1)  # (m_b,)
            r = int(sims.argmax().item())
            est[b] = cbs[b][r]
            picks.append(r)
        if picks == last:                                               # converged (fixed point)
            break
        last = picks
    return picks


def gate_B(seed):
    """CRT uniqueness (theorem) + decode_acc via RESONATOR factorization + CRT recombine (prereg-faithful)."""
    g = _gen(seed)
    chans = base_channels(seed, BASES)
    cbs = _codebooks(chans)
    R = 1
    for m in BASES: R *= m
    coprime = all(math.gcd(BASES[i], BASES[j]) == 1 for i in range(len(BASES)) for j in range(i + 1, len(BASES)))
    n_test = min(R, 300)
    xs = torch.randint(0, R, (n_test,), generator=g, device=DEV).to(torch.float64)
    Rx = residue_fpe(xs, chans)
    correct = 0
    for i in range(n_test):
        rec_res = resonator_decode(Rx[i], chans, cbs)                   # RESONATOR iteration (not naive corr)
        x_hat = _crt(rec_res, BASES, R)
        if x_hat == int(xs[i].item()):
            correct += 1
    acc = correct / n_test
    return {"coprime": coprime, "range": R, "decode_acc": acc, "n_test": n_test,
            "pass": coprime and acc >= DECODE_BAR}


def _crt(residues, bases, R):
    # standard CRT recombine
    x = 0
    for r, m in zip(residues, bases):
        Mi = R // m
        inv = pow(Mi % m, -1, m)
        x = (x + r * Mi * inv) % R
    return x


def gate_C(seed):
    """C1 product-kernel base-independence (VERIFY-NOT-ASSUME) + C2 resolution/capacity envelope."""
    chans = base_channels(seed, BASES)
    R = 1
    for m in BASES: R *= m
    # --- C1: combined kernel vs product of per-base kernels, over continuous d ---
    ds = torch.linspace(0.0, float(min(R, 40)), GRID_PTS, dtype=torch.float64, device=DEV)
    x0 = torch.zeros_like(ds)
    Rx = residue_fpe(x0, chans); Ry = residue_fpe(ds, chans)
    combined = (Rx * Ry.conj()).real.mean(dim=-1)                  # combined kernel(d)
    # product of per-base kernels: per base, kernel_b(d) = (1/N) Re<V_b(0), conj(V_b(d))> = mean cos(2pi a_b d/m)
    product = torch.ones_like(combined)
    for (m, a) in chans:
        kb = torch.cos((2 * math.pi / m) * ds.unsqueeze(-1) * a.unsqueeze(0)).mean(dim=-1)
        product = product * kb
    c1_err = (combined - product).abs().max().item()
    c1_holds = c1_err <= TOL_C1
    # --- C2: resolution envelope -- min-distinguishable Delta_x: for each res spacing, can we separate x vs x+res? ---
    envelope = {}
    for res in ENV_RES:
        xs = torch.arange(0, min(R, 50), 1, dtype=torch.float64, device=DEV)
        Va = residue_fpe(xs, chans); Vb = residue_fpe(xs + res, chans)
        self_sim = (Va * Va.conj()).real.mean(dim=-1)              # ~1
        near_sim = (Va * Vb.conj()).real.mean(dim=-1)              # similarity to res-shifted neighbor
        # distinguishable if near-neighbor sim is well below self sim (margin)
        margin = float((self_sim - near_sim).mean().item())
        envelope[str(res)] = {"mean_self": float(self_sim.mean().item()),
                              "mean_near": float(near_sim.mean().item()), "margin": margin}
    return {"c1_kernel_err": c1_err, "c1_tol": TOL_C1, "c1_product_kernel_holds": c1_holds,
            "c2_resolution_envelope": envelope}


def _selftest():
    assert DEV is not None
    # CRT recombine correctness
    assert _crt([2, 3, 2], [3, 5, 7], 105) == _crt_ref([2, 3, 2], [3, 5, 7]), "CRT recombine mismatch"
    # sinc closed form
    assert abs(float(sinc(torch.tensor(0.0)).item()) - 1.0) < 1e-9
    assert abs(float(sinc(torch.tensor(1.0)).item())) < 1e-6   # sinc(1)=0
    # GATE-A kernel matches sinc within band (small smoke)
    a = gate_A(7); assert a["max_kernel_err"] < 0.2, f"GATE-A kernel way off: {a['max_kernel_err']}"
    # residue-FPE unit magnitude
    chans = base_channels(7, [3, 5])
    R = residue_fpe(torch.tensor([1.0, 2.0], device=DEV, dtype=torch.float64), chans)
    assert torch.allclose(R.abs(), torch.ones_like(R.abs()), atol=1e-5), "residue-FPE not unit-magnitude"
    print("[selftest] PASS: CRT + sinc + GATE-A-kernel + residue-FPE-unit-magnitude", flush=True)


def _crt_ref(residues, bases):
    # brute-force reference CRT for self-test
    R = 1
    for m in bases: R *= m
    for x in range(R):
        if all(x % m == r for r, m in zip(residues, bases)):
            return x
    return -1


def verdict(A, B, C):
    if not A["pass"]:
        return ("HARD_FAIL_GATE_A", f"kernel err {A['max_kernel_err']:.4f} > TOL {A['tol']:.4f} -> base-phase model wrong; STOP")
    if not B["pass"]:
        return ("HONEST_NEGATIVE_GATE_B", f"decode_acc {B['decode_acc']:.3f} < {DECODE_BAR} -> residue decode range-bounded (honest scope)")
    if C["c1_product_kernel_holds"]:
        return ("PRIMITIVE_1_LOAD_BEARING", f"GATE-A pass + GATE-B decode {B['decode_acc']:.3f} + GATE-C1 product-kernel HOLDS (err {C['c1_kernel_err']:.4f}<=TOL) + envelope reported -> continuous-residue load-bearing WITHIN envelope")
    return ("HONEST_BOUNDED_C1_BREAKS", f"GATE-A+B pass but GATE-C1 product-kernel BREAKS (err {C['c1_kernel_err']:.4f}>TOL) -> base independence fails for continuous x; file integer-residue + single-channel-continuous BOUNDED (honest scope)")


def main():
    print(f"[start] {ANCHOR} run_mode={RUN_MODE} dev={DEV} N={N} bases={BASES} seeds={SEEDS}", flush=True)
    _selftest()
    out = get_output_dir(os.environ.get("HDLAB_EXP_NAME", ANCHOR)); t0 = time.time()
    A = [gate_A(s) for s in SEEDS]; B = [gate_B(s) for s in SEEDS]; C = [gate_C(s) for s in SEEDS]
    A_m = {"max_kernel_err": max(a["max_kernel_err"] for a in A), "tol": TOL_A, "pass": all(a["pass"] for a in A)}
    B_m = {"decode_acc": sum(b["decode_acc"] for b in B) / len(B), "range": B[0]["range"],
           "coprime": all(b["coprime"] for b in B), "pass": all(b["pass"] for b in B)}
    C_m = {"c1_kernel_err": max(c["c1_kernel_err"] for c in C), "c1_tol": TOL_C1,
           "c1_product_kernel_holds": all(c["c1_product_kernel_holds"] for c in C),
           "c2_resolution_envelope": C[0]["c2_resolution_envelope"]}
    v, vmsg = verdict(A_m, B_m, C_m)
    print(f"\n[GATE-A] kernel_err={A_m['max_kernel_err']:.4f} TOL={TOL_A:.4f} -> {'PASS' if A_m['pass'] else 'FAIL'}", flush=True)
    print(f"[GATE-B] decode_acc={B_m['decode_acc']:.3f} range={B_m['range']} coprime={B_m['coprime']} -> {'PASS' if B_m['pass'] else 'FAIL'}", flush=True)
    print(f"[GATE-C1] product_kernel_err={C_m['c1_kernel_err']:.4f} TOL={TOL_C1:.4f} holds={C_m['c1_product_kernel_holds']}", flush=True)
    print(f"[GATE-C2] resolution envelope: {C_m['c2_resolution_envelope']}", flush=True)
    print(f"\n[VERDICT] {v} -- {vmsg}", flush=True)
    metrics = {"anchor_name": ANCHOR, "run_mode": RUN_MODE, "device": str(DEV), "N": N, "bases": BASES,
               "seeds": SEEDS, "gate_A": A_m, "gate_B": B_m, "gate_C": C_m, "verdict": v, "verdict_msg": vmsg,
               "honest_scope": "continuous-magnitude WITHIN GATE-C envelope; integer-residue + single-channel-FPE grounded; combined-continuous-residue product-kernel is the verified-not-assumed open question",
               "elapsed_s": time.time() - t0, "compute_backend": str(DEV)}
    write_metrics(out, metrics, [{"gate_A": A_m, "gate_B": B_m, "gate_C": C_m}])
    print(f"[metrics] written {out}/metrics.json", flush=True)


if __name__ == "__main__":
    if SELFTEST:
        _selftest(); sys.exit(0)
    main()
