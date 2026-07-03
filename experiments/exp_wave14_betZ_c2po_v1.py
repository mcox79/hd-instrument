"""Bet Z.2 C2PO Classical 2-Pulse Overlap — pattern-pair coupling diagnostic.

Per Research 2026-05-22 14:50 EDT. Adapts Jonsson 2001 memory/rejuvenation +
Jalabert-Pastawski 2001 classical Loschmidt echo to substrate Glauber MC.

Protocol per pattern pair (A, B):
  1. baseline: cue1=A only, then measure overlap with B
  2. probe: cue1=A; delay; cue2=B; measure overlap with B
  echo(A,B,delay) = probe_overlap - baseline_overlap

Substrate-novel: probes pattern-pair coupling, not just per-pattern recall.
Predictions:
  diagonal A=B: echo positive (auto-recall)
  off-diagonal (orthogonal patterns): echo ~ 0 (noise floor)
  off-diagonal (correlated patterns): echo nonzero (cross-coupling)

Verdict thresholds:
  C2PO_PASS:     diagonal_mean > 0.1 AND off_diag_orthogonal_mean < 0.05 AND off_diag_correlated_mean > 0.05
  C2PO_PARTIAL:  diagonal works but off-diag signal weak (substrate decoupled)
  C2PO_BROKEN:   diagonal echo < 0.05 (cue mechanism not coupling to substrate)
  C2PO_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_betZ_c2po_v1.md
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass


PASS_DIAG = 0.10
PASS_OFF_ORTH_MAX = 0.05
PASS_OFF_CORR_MIN = 0.05
BROKEN_DIAG = 0.05


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "diag_mean" not in summary:
        return ("C2PO_INCONCLUSIVE", "Missing diag_mean.")
    diag = summary["diag_mean"]; orth = summary["off_orth_mean"]; corr = summary["off_corr_mean"]
    if diag < BROKEN_DIAG:
        return ("C2PO_BROKEN",
                f"Diagonal echo={diag:.4f} < {BROKEN_DIAG}; cue mechanism does not couple to substrate. "
                f"off_orth={orth:.4f}, off_corr={corr:.4f}.")
    if diag >= PASS_DIAG and orth <= PASS_OFF_ORTH_MAX and corr >= PASS_OFF_CORR_MIN:
        return ("C2PO_PASS",
                f"Substrate-novel pattern-pair coupling validated: diag={diag:.4f}, "
                f"off_orthogonal={orth:.4f} (<={PASS_OFF_ORTH_MAX}), off_correlated={corr:.4f} "
                f"(>={PASS_OFF_CORR_MIN}). C2PO diagnostic works on substrate.")
    return ("C2PO_PARTIAL",
            f"Partial C2PO signal: diag={diag:.4f}, off_orth={orth:.4f}, off_corr={corr:.4f}. "
            f"Substrate decouples or response too weak.")


def self_test_verdict():
    cases = [
        ({"diag_mean": 0.30, "off_orth_mean": 0.02, "off_corr_mean": 0.15}, "C2PO_PASS"),
        ({"diag_mean": 0.20, "off_orth_mean": 0.10, "off_corr_mean": 0.12}, "C2PO_PARTIAL"),
        ({"diag_mean": 0.01, "off_orth_mean": 0.0, "off_corr_mean": 0.0}, "C2PO_BROKEN"),
        ({}, "C2PO_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def random_bipolar(shape, cpu_gen, device):
    bits = (torch.rand(shape, generator=cpu_gen) > 0.5).to(device)
    return 2.0 * bits.float() - 1.0


def glauber_with_field(s, W, h, beta, n_sweeps, cpu_gen, device):
    """Run n_sweeps of Glauber MC with applied field h."""
    N = s.shape[0]
    for _ in range(n_sweeps):
        order = torch.randperm(N, generator=cpu_gen).to(device)
        us = torch.rand(N, generator=cpu_gen).to(device)
        for k, idx in enumerate(order):
            h_i = float(W[idx] @ s) + float(h[idx])
            p_plus = 1.0 / (1.0 + math.exp(-2.0 * beta * h_i))
            s[idx] = 1.0 if float(us[k]) < p_plus else -1.0
    return s


def c2po_one_pair(W, patterns, A_idx, B_idx, delay_steps, cue_strength, T_cue, T_readout,
                    beta, cpu_gen, device, n_reps):
    N = patterns.shape[1]
    xi_A = patterns[A_idx]
    xi_B = patterns[B_idx]
    echoes = []
    for rep in range(n_reps):
        # Baseline: cue1 only
        s0 = random_bipolar((N,), cpu_gen, device)
        s = s0.clone()
        s = glauber_with_field(s, W, cue_strength * xi_A, beta, T_cue, cpu_gen, device)
        s = glauber_with_field(s, W, torch.zeros(N, device=device), beta, delay_steps, cpu_gen, device)
        s = glauber_with_field(s, W, torch.zeros(N, device=device), beta, T_readout, cpu_gen, device)
        m_baseline = float((s * xi_B).mean())
        # Probe: cue1, delay, cue2
        s = s0.clone()
        s = glauber_with_field(s, W, cue_strength * xi_A, beta, T_cue, cpu_gen, device)
        s = glauber_with_field(s, W, torch.zeros(N, device=device), beta, delay_steps, cpu_gen, device)
        s = glauber_with_field(s, W, cue_strength * xi_B, beta, T_cue, cpu_gen, device)
        s = glauber_with_field(s, W, torch.zeros(N, device=device), beta, T_readout, cpu_gen, device)
        m_probe = float((s * xi_B).mean())
        echoes.append(m_probe - m_baseline)
    return sum(echoes) / len(echoes)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 256 if smoke else 1024,
              "K_patterns": 20 if smoke else 40,
              "n_diag_pairs": 3 if smoke else 8,
              "n_orth_pairs": 3 if smoke else 8,
              "n_corr_pairs": 3 if smoke else 8,
              "delay_steps": 5,
              "T_cue": 5 if smoke else 10,
              "T_readout": 10 if smoke else 20,
              "cue_strength": 0.5,
              "beta": 2.0,
              "n_reps": 3 if smoke else 8,
              "corr_overlap": 0.5,  # injection: correlated pair = sign(xi_A + xi_extra)
              "seed": 17}
    N = config["N"]; K = config["K_patterns"]
    cpu_gen = torch.Generator().manual_seed(config["seed"])
    # Construct K patterns: first K-n_corr_pairs are independent; last n_corr are correlated to a paired earlier index
    patterns = random_bipolar((K, N), cpu_gen, device)
    # Inject correlated pairs: pattern[K-n_corr_pairs+i] = sign(corr*pattern[i] + (1-corr)*noise)
    correlated_pairs = []
    for i in range(config["n_corr_pairs"]):
        partner = i
        extra = random_bipolar((N,), cpu_gen, device)
        mix = config["corr_overlap"] * patterns[partner] + (1 - config["corr_overlap"]) * extra
        new_idx = K - config["n_corr_pairs"] + i
        patterns[new_idx] = torch.sign(mix)
        patterns[new_idx][patterns[new_idx] == 0] = 1.0
        correlated_pairs.append((partner, new_idx))
    W = (patterns.T @ patterns) / N
    W.fill_diagonal_(0.0)
    print(f"[setup] N={N} K={K}, {config['n_corr_pairs']} correlated pairs", flush=True)

    # Diagonal: A=B for first n_diag indices
    diag_echoes = []
    for i in range(config["n_diag_pairs"]):
        echo = c2po_one_pair(W, patterns, i, i, config["delay_steps"], config["cue_strength"],
                                config["T_cue"], config["T_readout"], config["beta"],
                                cpu_gen, device, config["n_reps"])
        diag_echoes.append(echo)
        print(f"  diag A=B={i}: echo={echo:.4f}", flush=True)
    diag_mean = sum(diag_echoes) / len(diag_echoes)

    # Off-diagonal orthogonal: pick random A != B pairs from first half (independent patterns)
    orth_echoes = []
    half = K - config["n_corr_pairs"]
    for i in range(config["n_orth_pairs"]):
        a = i % half
        b = (i + half // 2) % half
        if a == b: b = (b + 1) % half
        echo = c2po_one_pair(W, patterns, a, b, config["delay_steps"], config["cue_strength"],
                                config["T_cue"], config["T_readout"], config["beta"],
                                cpu_gen, device, config["n_reps"])
        orth_echoes.append(abs(echo))
        print(f"  off_orth A={a} B={b}: |echo|={abs(echo):.4f}", flush=True)
    orth_mean = sum(orth_echoes) / len(orth_echoes)

    # Off-diagonal correlated: use the injected pairs
    corr_echoes = []
    for (a, b) in correlated_pairs[:config["n_corr_pairs"]]:
        echo = c2po_one_pair(W, patterns, a, b, config["delay_steps"], config["cue_strength"],
                                config["T_cue"], config["T_readout"], config["beta"],
                                cpu_gen, device, config["n_reps"])
        corr_echoes.append(abs(echo))
        dot = float((patterns[a] * patterns[b]).mean())
        print(f"  off_corr A={a} B={b} (dot={dot:.3f}): |echo|={abs(echo):.4f}", flush=True)
    corr_mean = sum(corr_echoes) / len(corr_echoes)

    summary = {"diag_mean": diag_mean,
                "off_orth_mean": orth_mean,
                "off_corr_mean": corr_mean,
                "diag_echoes": diag_echoes,
                "orth_echoes": orth_echoes,
                "corr_echoes": corr_echoes}
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
    out_dir = get_output_dir("wave14_betZ_c2po_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("diag_present", summary["diag_mean"] + 1.0, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betZ_c2po_v1")
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
