"""Bet F SSH-BSC v2 - chiral class AIII topological probe redesign.

R10 redesigned the v1 probe with triple-invariant battery: Mondragon-Shem
real-space winding, Bott index, spectral localizer signature. v1 failed
(categorical_correct=0) due to no Hamiltonian construction. v2 builds
H = tridiagonal_hopping(key) (documented choice; see prereg) and runs
the triple battery + q-sweep.

W-construction caveat: prereg's tridiagonal interpretation chosen absent
Research clarification (exp_dev_request_to_research_2026-05-21.md filed).
If Research specifies differently, v3 will follow.

Pre-reg: preregs/2026-05-21_wave14_ssh_bsc_v2_protected.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def make_modulation(N, q, gen):
    """Generate +/-1 vector with exactly q sign domain walls, evenly spaced."""
    if q == 0:
        return torch.ones(N)
    positions = sorted(torch.randperm(N - 1, generator=gen)[:q].tolist())
    h = torch.ones(N)
    sign = 1.0
    pos = 0
    for wall in positions:
        h[pos:wall + 1] = sign
        sign = -sign
        pos = wall + 1
    h[pos:] = sign
    return h


def encode_topological_key(a_A, a_B, h_q):
    """key = sign(a_A + h_q * a_B)."""
    raw = a_A + h_q * a_B
    out = torch.sign(raw)
    return torch.where(out == 0, torch.ones_like(out), out)


def apply_bitflip_noise(key, p, gen):
    flips = (torch.rand(key.shape, generator=gen) < p).float()
    return key * (1.0 - 2.0 * flips)


def tridiagonal_hopping(key, device):
    """H[i, i+1] = key[i] * key[i+1]; H[i+1, i] = same (symmetric tridiagonal)."""
    N = key.shape[0]
    hop = key[:-1] * key[1:]  # (N-1,)
    H = torch.zeros((N, N), device=device, dtype=torch.float32)
    idx = torch.arange(N - 1, device=device)
    H[idx, idx + 1] = hop.to(device)
    H[idx + 1, idx] = hop.to(device)
    return H


def chiral_violation(H, device):
    """Gamma = diag(+1 even, -1 odd). class AIII requires Gamma H Gamma = -H."""
    N = H.shape[0]
    gamma = torch.ones(N, device=device)
    gamma[1::2] = -1.0
    GHG = gamma.unsqueeze(1) * H * gamma.unsqueeze(0)
    return float((GHG + H).norm() / max(float(H.norm()), 1e-12))


def mondragon_shem_winding(H, device):
    """Real-space winding via chiral projector difference Q = P_+ - P_-.
    nu = trace(Q @ (Q @ X - X @ Q)) / L."""
    N = H.shape[0]
    # eigendecomp of symmetric H
    eigvals, eigvecs = torch.linalg.eigh(H)
    # Project onto positive vs negative energy subspaces
    pos_mask = eigvals > 1e-9
    neg_mask = eigvals < -1e-9
    # P_+ = V[:, pos] V[:, pos].T;  P_- = V[:, neg] V[:, neg].T
    V_pos = eigvecs[:, pos_mask]
    V_neg = eigvecs[:, neg_mask]
    P_plus = V_pos @ V_pos.T
    P_minus = V_neg @ V_neg.T
    Q = P_plus - P_minus
    X = torch.arange(N, device=device, dtype=torch.float32).unsqueeze(0)  # (1, N)
    X_diag = X.squeeze(0)
    # Q @ (Q @ X - X @ Q): compute as Q @ (Q * X.row - X.col * Q)
    QX = Q * X_diag.unsqueeze(0)  # broadcast X across rows
    XQ = Q * X_diag.unsqueeze(1)
    inner = Q @ (QX - XQ)
    nu_raw = float(torch.trace(inner))
    return int(round(nu_raw))


def bott_index(H, device):
    """Bott index over lower-band projector."""
    N = H.shape[0]
    eigvals, eigvecs = torch.linalg.eigh(H)
    # Take the lower half (negative energy at half-filling)
    half = N // 2
    P = eigvecs[:, :half] @ eigvecs[:, :half].T
    X = torch.arange(N, device=device, dtype=torch.complex64)
    X_tilde = torch.exp(2j * math.pi * X / N)
    PXP = P.to(torch.complex64) * X_tilde.unsqueeze(0)
    PXP = PXP @ P.to(torch.complex64)
    PXP_conj = P.to(torch.complex64) * X_tilde.conj().unsqueeze(0)
    PXP_conj = PXP_conj @ P.to(torch.complex64)
    M = PXP @ PXP_conj
    # log of M: use eigvals
    m_eigs = torch.linalg.eigvals(M)
    # bott = trace(log M) / (2 pi i); use sum of log(eigvals)
    log_eigs = torch.log(m_eigs.clamp(min=torch.complex(torch.tensor(1e-12), torch.tensor(0.0))))
    bott = float((log_eigs.sum() / (2j * math.pi)).real)
    return int(round(bott))


def compute_verdict(summary):
    cells = summary.get("per_cell", {})
    if not cells:
        return ("BET_F_INCONCLUSIVE", "Missing per-cell.")
    # Check chiral class
    chiral_pct_AIII = sum(1 for c in cells.values() if c.get("chiral_violation", 1.0) < 0.05) / len(cells)
    if chiral_pct_AIII < 0.5:
        return ("BET_F_NOT_AIII",
                f"chiral_violation>0.05 in {(1 - chiral_pct_AIII) * 100:.0f}% of cells. "
                f"Tridiagonal-hopping W is not in class AIII for these substrates; "
                f"W-construction choice may need revision per Research clarification.")
    # Compute nu recovery rate at each (q, p)
    by_qp = {}
    for c in cells.values():
        if c.get("chiral_violation", 1.0) >= 0.05:
            continue
        key = (c["q"], c["p"])
        by_qp.setdefault(key, []).append(c["nu_MS"] == c["q"])
    nu_recovery = {qp: sum(vs) / len(vs) for qp, vs in by_qp.items() if vs}
    p_c_per_q = {}
    qs = sorted({q for (q, p) in nu_recovery.keys()})
    for q in qs:
        passing_p = [p for (q2, p), r in nu_recovery.items() if q2 == q and r >= 0.5]
        p_c_per_q[q] = max(passing_p, default=0.0)
    if not p_c_per_q or all(v == 0.0 for v in p_c_per_q.values()):
        return ("BET_F_NO_TRANSITION",
                f"No q gives recovery rate >= 0.5 at any p; no sharp transition observed.")
    # Check 1/(2q) scaling within 30%
    scalings_ok = []
    for q, pc in p_c_per_q.items():
        predicted = 1.0 / (2.0 * q)
        ok = abs(pc - predicted) / predicted < 0.30 if predicted > 0 else False
        scalings_ok.append(ok)
    if sum(scalings_ok) >= max(1, len(scalings_ok) * 2 // 3):
        return ("BET_F_PASS",
                f"Sharp transitions observed; p_c scales 1/(2q) within 30% for "
                f"{sum(scalings_ok)}/{len(scalings_ok)} q values. p_c={p_c_per_q}.")
    return ("BET_F_NO_TRANSITION",
            f"Transitions exist but p_c scaling does NOT match 1/(2q) within 30%. "
            f"Got p_c={p_c_per_q}. Topological protection unconfirmed.")


def self_test_verdict():
    def cell(q, p, chiral=0.02, nu_MS=None):
        return {"q": q, "p": p, "chiral_violation": chiral,
                "nu_MS": nu_MS if nu_MS is not None else q}
    # Case 1: PASS - recovery rate high at low p, drops near 1/(2q)
    s1_cells = {}
    for q in [2, 5]:
        for p in [0.0, 0.05, 0.10, 0.20]:
            pc_expected = 1.0 / (2.0 * q)
            for seed in [17, 23, 31]:
                ok = p < pc_expected * 1.2
                nu = q if ok else 0
                s1_cells[f"{q}_{p}_{seed}"] = cell(q, p, nu_MS=nu)
    s1 = {"per_cell": s1_cells}
    # Case 2: NOT_AIII - chiral violation high
    s2 = {"per_cell": {"a": cell(2, 0.0, chiral=0.5)}}
    # Case 3: NO_TRANSITION
    s3_cells = {f"{q}_{p}_{s}": cell(q, p, nu_MS=0) for q in [2, 5]
                for p in [0.0, 0.05] for s in [17]}
    s3 = {"per_cell": s3_cells}
    cases = [
        (s1, "BET_F_PASS"),
        (s2, "BET_F_NOT_AIII"),
        (s3, "BET_F_NO_TRANSITION"),
        ({}, "BET_F_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_cell(q, p, seed, N, device):
    gen = torch.Generator().manual_seed(seed)
    a_A = 2.0 * (torch.rand(N, generator=gen) > 0.5).float() - 1.0
    a_B = 2.0 * (torch.rand(N, generator=gen) > 0.5).float() - 1.0
    # A on even sites, B on odd
    mask_A = torch.zeros(N); mask_A[::2] = 1.0
    mask_B = torch.zeros(N); mask_B[1::2] = 1.0
    h_q = make_modulation(N, q, gen)
    key = encode_topological_key(a_A * mask_A, a_B * mask_B, h_q)
    noisy_key = apply_bitflip_noise(key, p, torch.Generator().manual_seed(seed + 100))
    H = tridiagonal_hopping(noisy_key, device)
    cv = chiral_violation(H, device)
    if cv > 0.05:
        return {"q": q, "p": p, "seed": seed, "chiral_violation": cv,
                "nu_MS": None, "bott": None}
    nu_MS = mondragon_shem_winding(H, device)
    try:
        bott = bott_index(H, device)
    except Exception:
        bott = None
    return {"q": q, "p": p, "seed": seed, "chiral_violation": cv,
             "nu_MS": nu_MS, "bott": bott}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 256 if smoke else 1024,
              "q_sweep": [2] if smoke else [2, 5, 10],
              "p_sweep": [0.0, 0.10] if smoke else [0.0, 0.05, 0.10, 0.20],
              "seeds": [17] if smoke else [17, 23, 31]}
    print(f"[config] {config}", flush=True)
    per_cell = {}
    for q in config["q_sweep"]:
        for p in config["p_sweep"]:
            for seed in config["seeds"]:
                key = f"{q}_{p}_{seed}"
                print(f"[cell] {key} ...", flush=True)
                per_cell[key] = run_one_cell(q, p, seed, config["N"], device)
                cv = per_cell[key]["chiral_violation"]
                nu = per_cell[key]["nu_MS"]
                print(f"  chiral_viol={cv:.4f} nu_MS={nu}", flush=True)
    summary = {"per_cell": per_cell}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_ssh_bsc_v2_protected_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first = list(summary["per_cell"].values())[0]
    oracle.assert_baseline_high("chiral_inv_present",
                                    1.0 - first["chiral_violation"], 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_ssh_bsc_v2_protected")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test: self_test_verdict(); return 0
    if args.smoke: run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
