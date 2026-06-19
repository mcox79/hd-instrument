"""Autoregressive generation with sampling (not greedy argmax).

yy showed greedy decoding collapses to repetition. yz tests if sampled
decoding fixes it. Sampling from softmax(BETA*sims) at temperature T.

Pre-reg: preregs/2026-05-21_wave14yz_generation_with_sampling.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from collections import Counter
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_yy = importlib.util.spec_from_file_location("yy",
    REPO / "experiments" / "exp_wave14yy_autoregressive_generation.py")
yy = importlib.util.module_from_spec(_yy); _yy.loader.exec_module(yy)
_v3d = importlib.util.spec_from_file_location("v3d",
    REPO / "experiments" / "exp_wave14d_icl_via_pool_v3_scaling.py")
v3 = importlib.util.module_from_spec(_v3d); _v3d.loader.exec_module(v3)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def generate_sampled(W, pool_vecs, pool_labels, pool_used, byte_atoms, pos_atoms,
                       prefix_bytes, generate_length, n_dim, device, temperature, seed):
    """Generate via temperature-scaled sampling instead of argmax."""
    K = v3.K
    context = list(prefix_bytes)
    generated = []
    gen_rng = torch.Generator(device=device).manual_seed(seed)

    for step in range(generate_length):
        ctx_bytes = context[-K:]
        if len(ctx_bytes) < K:
            ctx_bytes = [v3.PAD_BYTE] * (K - len(ctx_bytes)) + ctx_bytes
        idx_tensor = torch.tensor([ctx_bytes], dtype=torch.long, device=device)
        ctx = v3.build_ctx(byte_atoms, pos_atoms, idx_tensor)
        q = ctx @ W.T
        q = v3.shifted_relu(q, v3.RELU_B)
        sims = (byte_atoms @ q.T) / n_dim
        P_W = torch.softmax(yy.BETA * sims / temperature, dim=0).squeeze(1)
        if pool_used > 0 and yy.ALPHA > 0:
            active = pool_vecs[:pool_used]
            labels = pool_labels[:pool_used]
            sims_p = (active @ ctx.T) / n_dim
            weights_p = torch.softmax(yy.BETA * sims_p / temperature, dim=0).squeeze(1)
            P_retr = torch.zeros(v3.VOCAB_SIZE, device=device)
            P_retr.scatter_add_(0, labels, weights_p)
            P = yy.ALPHA * P_retr + (1 - yy.ALPHA) * P_W
        else:
            P = P_W
        next_byte = int(torch.multinomial(P, 1, generator=gen_rng).item())
        generated.append(next_byte)
        context.append(next_byte)
    return generated


def compute_verdict(summary):
    per_temp = summary.get("per_temperature")
    if not per_temp:
        return ("GEN_SAMPLE_INCONCLUSIVE", "Missing.")
    # Find the temperature with best (entropy in band, repetition low)
    valid_temps = []
    for t, m in per_temp.items():
        e = m["char_entropy"]
        r = m["ngram_repetition"]
        if yy.PASS_ENTROPY_LOW <= e <= yy.PASS_ENTROPY_HIGH and r < yy.PASS_REPETITION:
            valid_temps.append(t)
    if valid_temps:
        best_t = valid_temps[0]
        m = per_temp[best_t]
        return (f"GEN_SAMPLE_RESCUES_AT_T_{best_t}",
                f"Sampling at temperature={best_t} produces non-degenerate text: "
                f"entropy={m['char_entropy']:.3f}, repetition={m['ngram_repetition']:.3f}. "
                f"Per-temp: " + ", ".join(f"T{t}=(e{m2['char_entropy']:.2f},r{m2['ngram_repetition']:.2f})"
                                              for t, m2 in sorted(per_temp.items())))
    # No temperature gives non-degenerate output
    return ("GEN_SAMPLE_NO_RESCUE",
            f"No temperature produced non-degenerate text. Per-temp: " +
            ", ".join(f"T{t}=(e{m['char_entropy']:.2f},r{m['ngram_repetition']:.2f})"
                       for t, m in sorted(per_temp.items())))


def self_test_verdict():
    cases = [
        ({"per_temperature": {0.5: {"char_entropy": 1.2, "ngram_repetition": 0.95},
                                1.0: {"char_entropy": 4.0, "ngram_repetition": 0.20},
                                2.0: {"char_entropy": 7.5, "ngram_repetition": 0.05}}},
         "GEN_SAMPLE_RESCUES_AT_T_1.0"),
        ({"per_temperature": {0.5: {"char_entropy": 1.0, "ngram_repetition": 0.95},
                                1.0: {"char_entropy": 1.5, "ngram_repetition": 0.85},
                                2.0: {"char_entropy": 7.8, "ngram_repetition": 0.05}}},
         "GEN_SAMPLE_NO_RESCUE"),
        ({}, "GEN_SAMPLE_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed (3/3 cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    n_dim = yy.N_SMOKE if smoke else yy.N_FULL
    gen_len = yy.GENERATE_LENGTH_SMOKE if smoke else yy.GENERATE_LENGTH_FULL
    max_epochs = yy.MAX_EPOCHS_SMOKE if smoke else yy.MAX_EPOCHS_FULL
    temperatures = [0.5, 1.0] if smoke else [0.5, 0.8, 1.0, 1.5, 2.0]
    seed = 17

    config = {"mode": "smoke" if smoke else "full", "N": n_dim,
              "generate_length": gen_len, "temperatures": temperatures,
              "max_epochs": max_epochs}
    print(f"[config] {config}", flush=True)

    corpus_a = v3.load_corpus_a()
    train_a = corpus_a[:int(0.8 * len(corpus_a))]
    if smoke:
        train_a = train_a[:4000]
    gen_rng = torch.Generator().manual_seed(seed)
    byte_atoms = v3.make_bsc_atoms(v3.VOCAB_SIZE, n_dim, gen_rng).to(device)
    pos_atoms = v3.make_bsc_atoms(v3.K, n_dim, gen_rng).to(device)
    W, pool_vecs, pool_labels, pool_used = v3.train_phase_a(
        byte_atoms, pos_atoms, train_a, n_dim, max_epochs, yy.BATCH_SIZE)

    prefix_bytes = list(corpus_a[:yy.PREFIX_LENGTH])
    per_temp = {}
    for T in temperatures:
        gen = generate_sampled(W, pool_vecs, pool_labels, pool_used,
                                  byte_atoms, pos_atoms, prefix_bytes, gen_len,
                                  n_dim, device, T, seed)
        e = yy.char_entropy(gen)
        r = yy.ngram_repetition_rate(gen, n=4)
        per_temp[T] = {"char_entropy": e, "ngram_repetition": r,
                         "sample_bytes": bytes(gen[:100]).decode("utf-8", errors="replace")}
        print(f"  T={T}  entropy={e:.3f}  repetition={r:.3f}", flush=True)

    summary = {"per_temperature": per_temp}
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
    out_dir = get_output_dir("wave14yz_generation_with_sampling_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14yz_generation_with_sampling")
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
