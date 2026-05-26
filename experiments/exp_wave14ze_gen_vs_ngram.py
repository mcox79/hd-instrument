"""Substrate generation vs n-gram baseline.

yz showed sampled substrate generation works. ze compares to a baseline:
trigram-Markov sampler trained on the same Corpus A. Real product question:
is substrate generation BETTER than a simple n-gram?

Pre-reg: preregs/2026-05-21_wave14ze_gen_vs_ngram.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from collections import Counter, defaultdict
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_yy = importlib.util.spec_from_file_location("yy", REPO / "experiments" / "exp_wave14yy_autoregressive_generation.py")
yy = importlib.util.module_from_spec(_yy); _yy.loader.exec_module(yy)
_yz = importlib.util.spec_from_file_location("yz", REPO / "experiments" / "exp_wave14yz_generation_with_sampling.py")
yz = importlib.util.module_from_spec(_yz); _yz.loader.exec_module(yz)
_v3 = importlib.util.spec_from_file_location("v3", REPO / "experiments" / "exp_wave14d_icl_via_pool_v3_scaling.py")
v3 = importlib.util.module_from_spec(_v3); _v3.loader.exec_module(v3)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def build_ngram_model(bytes_data, n=3):
    """Build n-gram model: dict of (n-1)-tuple prefix -> Counter of next bytes."""
    model = defaultdict(Counter)
    for i in range(len(bytes_data) - n + 1):
        prefix = tuple(bytes_data[i:i + n - 1])
        next_byte = bytes_data[i + n - 1]
        model[prefix][next_byte] += 1
    return model


def sample_ngram(model, n, prefix_bytes, generate_length, rng):
    """Generate from n-gram model with sampling."""
    context = list(prefix_bytes)
    generated = []
    for step in range(generate_length):
        prefix = tuple(context[-(n - 1):])
        counts = model.get(prefix, Counter())
        if not counts:
            # Unknown prefix; sample uniformly
            next_byte = rng.randint(0, 255)
        else:
            total = sum(counts.values())
            # Multinomial sample
            r = rng.random() * total
            cum = 0
            next_byte = list(counts.keys())[-1]
            for b, c in counts.items():
                cum += c
                if cum >= r:
                    next_byte = b
                    break
        generated.append(int(next_byte))
        context.append(int(next_byte))
    return generated


def compute_verdict(summary):
    sub = summary.get("substrate")
    ngram = summary.get("ngram")
    if sub is None or ngram is None:
        return ("GEN_VS_NGRAM_INCONCLUSIVE", "Missing.")

    sub_e = sub["char_entropy"]
    sub_r = sub["ngram_repetition"]
    ng_e = ngram["char_entropy"]
    ng_r = ngram["ngram_repetition"]

    sub_score = sub_e - 2 * sub_r  # higher is better
    ng_score = ng_e - 2 * ng_r

    if sub_score > ng_score + 0.3:
        return ("GEN_SUBSTRATE_BEATS_NGRAM",
                f"Substrate generation outperforms trigram-Markov baseline: "
                f"substrate=(e={sub_e:.3f},r={sub_r:.3f}); ngram=(e={ng_e:.3f},r={ng_r:.3f}). "
                f"Composite score {sub_score:.3f} vs {ng_score:.3f}.")
    if ng_score > sub_score + 0.3:
        return ("GEN_NGRAM_BEATS_SUBSTRATE",
                f"Trigram-Markov baseline produces better generation than substrate: "
                f"ngram=(e={ng_e:.3f},r={ng_r:.3f}); substrate=(e={sub_e:.3f},r={sub_r:.3f}).")
    return ("GEN_SIMILAR",
            f"Substrate and n-gram generation similar: "
            f"substrate=(e={sub_e:.3f},r={sub_r:.3f}); "
            f"ngram=(e={ng_e:.3f},r={ng_r:.3f}).")


def self_test_verdict():
    cases = [
        ({"substrate": {"char_entropy": 5.5, "ngram_repetition": 0.0},
          "ngram": {"char_entropy": 4.0, "ngram_repetition": 0.3}},
         "GEN_SUBSTRATE_BEATS_NGRAM"),
        ({"substrate": {"char_entropy": 3.0, "ngram_repetition": 0.4},
          "ngram": {"char_entropy": 5.0, "ngram_repetition": 0.0}},
         "GEN_NGRAM_BEATS_SUBSTRATE"),
        ({"substrate": {"char_entropy": 5.0, "ngram_repetition": 0.05},
          "ngram": {"char_entropy": 5.1, "ngram_repetition": 0.05}},
         "GEN_SIMILAR"),
        ({}, "GEN_VS_NGRAM_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed (4/4 cases)", flush=True)


def run_experiment(smoke):
    import random
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    n_dim = yy.N_SMOKE if smoke else yy.N_FULL
    gen_len = yy.GENERATE_LENGTH_SMOKE if smoke else yy.GENERATE_LENGTH_FULL
    max_epochs = yy.MAX_EPOCHS_SMOKE if smoke else yy.MAX_EPOCHS_FULL
    T = 1.0
    seed = 17

    config = {"mode": "smoke" if smoke else "full", "N": n_dim,
              "generate_length": gen_len, "temperature": T,
              "ngram_n": 3, "max_epochs": max_epochs}
    print(f"[config] {config}", flush=True)

    corpus_a = v3.load_corpus_a()
    train_a = corpus_a[:int(0.8 * len(corpus_a))]
    if smoke:
        train_a = train_a[:4000]

    # Train substrate
    gen_rng = torch.Generator().manual_seed(seed)
    byte_atoms = v3.make_bsc_atoms(v3.VOCAB_SIZE, n_dim, gen_rng).to(device)
    pos_atoms = v3.make_bsc_atoms(v3.K, n_dim, gen_rng).to(device)
    W, pool_A, labels_A, used_A = v3.train_phase_a(
        byte_atoms, pos_atoms, train_a, n_dim, max_epochs, yy.BATCH_SIZE)

    prefix_bytes = list(corpus_a[:yy.PREFIX_LENGTH])

    # Substrate sampled generation
    sub_gen = yz.generate_sampled(W, pool_A, labels_A, used_A, byte_atoms, pos_atoms,
                                       prefix_bytes, gen_len, n_dim, device, T, seed)
    sub_e = yy.char_entropy(sub_gen)
    sub_r = yy.ngram_repetition_rate(sub_gen, n=4)

    # Trigram baseline
    ngram_model = build_ngram_model(list(train_a), n=3)
    py_rng = random.Random(seed)
    ng_gen = sample_ngram(ngram_model, 3, prefix_bytes, gen_len, py_rng)
    ng_e = yy.char_entropy(ng_gen)
    ng_r = yy.ngram_repetition_rate(ng_gen, n=4)

    summary = {
        "substrate": {"char_entropy": sub_e, "ngram_repetition": sub_r,
                       "sample": bytes(sub_gen[:200]).decode("utf-8", errors="replace")},
        "ngram": {"char_entropy": ng_e, "ngram_repetition": ng_r,
                   "sample": bytes(ng_gen[:200]).decode("utf-8", errors="replace")},
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nsubstrate: entropy={sub_e:.3f} repetition={sub_r:.3f}", flush=True)
    print(f"ngram:     entropy={ng_e:.3f} repetition={ng_r:.3f}", flush=True)
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
    out_dir = get_output_dir("wave14ze_gen_vs_ngram_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14ze_gen_vs_ngram")
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
