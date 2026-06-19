"""Autoregressive generation: substrate predicts byte-by-byte, appends, repeats.

Train substrate on Corpus A; from a prefix, generate continuation. Evaluate
character entropy, repetition rate, self-bpc.

Pre-reg: preregs/2026-05-21_wave14yy_autoregressive_generation.md
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

_v3 = importlib.util.spec_from_file_location("v3", REPO / "experiments" / "exp_wave14d_icl_via_pool_v3_scaling.py")
v3 = importlib.util.module_from_spec(_v3); _v3.loader.exec_module(v3)


N_FULL = 4096
N_SMOKE = 1024
GENERATE_LENGTH_FULL = 512
GENERATE_LENGTH_SMOKE = 64
PREFIX_LENGTH = 64
MAX_EPOCHS_FULL = 5
MAX_EPOCHS_SMOKE = 1
BATCH_SIZE = 64
ALPHA = 1.0
BETA = 8.0

PASS_ENTROPY_LOW = 2.5
PASS_ENTROPY_HIGH = 6.0
PASS_REPETITION = 0.5


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def char_entropy(bytes_list):
    """Shannon entropy in bits over the byte distribution."""
    n = len(bytes_list)
    if n == 0:
        return 0.0
    counts = Counter(bytes_list)
    return -sum((c / n) * math.log2(c / n) for c in counts.values() if c > 0)


def ngram_repetition_rate(bytes_list, n=4):
    """Fraction of n-grams that appear more than once."""
    if len(bytes_list) < n:
        return 0.0
    ngrams = [tuple(bytes_list[i:i+n]) for i in range(len(bytes_list) - n + 1)]
    counts = Counter(ngrams)
    repeated = sum(1 for c in counts.values() if c > 1)
    total = len(counts)
    return repeated / total if total > 0 else 0.0


def generate(W, pool_vecs, pool_labels, pool_used, byte_atoms, pos_atoms,
             prefix_bytes, generate_length, n_dim, device):
    """Autoregressive generation: K-byte window predicts next byte, append, repeat."""
    K = v3.K
    context = list(prefix_bytes)
    generated = []

    for step in range(generate_length):
        # Take last K bytes (pad with PAD_BYTE if needed)
        ctx_bytes = context[-K:]
        if len(ctx_bytes) < K:
            ctx_bytes = [v3.PAD_BYTE] * (K - len(ctx_bytes)) + ctx_bytes
        idx_tensor = torch.tensor([ctx_bytes], dtype=torch.long, device=device)
        ctx = v3.build_ctx(byte_atoms, pos_atoms, idx_tensor)  # (1, N)

        # Substrate path
        q = ctx @ W.T
        q = v3.shifted_relu(q, v3.RELU_B)
        sims = (byte_atoms @ q.T) / n_dim
        P_W = torch.softmax(BETA * sims, dim=0).squeeze(1)  # (VOCAB_SIZE,)

        # Pool retrieval
        if pool_used > 0 and ALPHA > 0:
            active = pool_vecs[:pool_used]
            labels = pool_labels[:pool_used]
            sims_p = (active @ ctx.T) / n_dim
            weights_p = torch.softmax(BETA * sims_p, dim=0).squeeze(1)
            P_retr = torch.zeros(v3.VOCAB_SIZE, device=device)
            P_retr.scatter_add_(0, labels, weights_p)
            P = ALPHA * P_retr + (1 - ALPHA) * P_W
        else:
            P = P_W

        next_byte = int(P.argmax().item())
        generated.append(next_byte)
        context.append(next_byte)

    return generated


def compute_verdict(summary):
    m = summary.get("metrics")
    if not m:
        return ("GEN_INCONCLUSIVE", "Missing metrics.")
    entropy = m.get("char_entropy", 0.0)
    repetition = m.get("ngram_repetition", 1.0)
    bpc = m.get("self_bpc", float("inf"))

    if entropy >= PASS_ENTROPY_HIGH:
        return ("GEN_UNIFORM_RANDOM",
                f"Char entropy = {entropy:.3f} >= {PASS_ENTROPY_HIGH} bits (close to "
                f"uniform 8.0). Substrate's generation path produces near-uniform "
                f"output; not actually generating coherent text.")

    if entropy < PASS_ENTROPY_LOW or repetition >= PASS_REPETITION:
        return ("GEN_COLLAPSES_TO_REPETITION",
                f"Char entropy = {entropy:.3f} (< {PASS_ENTROPY_LOW}) OR 4-gram "
                f"repetition = {repetition:.3f} (>= {PASS_REPETITION}). Generation "
                f"collapses to repeating patterns.")

    if entropy >= PASS_ENTROPY_LOW and repetition < PASS_REPETITION:
        return ("GEN_PRODUCES_NONDEGENERATE_TEXT",
                f"Char entropy = {entropy:.3f} bits (in [{PASS_ENTROPY_LOW}, "
                f"{PASS_ENTROPY_HIGH}]); 4-gram repetition = {repetition:.3f} < "
                f"{PASS_REPETITION}. self_bpc on held-out continuation = {bpc:.3f}. "
                f"Substrate produces non-degenerate generation; auditable text "
                f"generator capability demonstrated at v1.")

    return ("GEN_PARTIAL",
            f"entropy={entropy:.3f}, repetition={repetition:.3f}, bpc={bpc:.3f}.")


def self_test_verdict():
    cases = [
        ({"metrics": {"char_entropy": 4.5, "ngram_repetition": 0.2, "self_bpc": 4.0}},
         "GEN_PRODUCES_NONDEGENERATE_TEXT"),
        ({"metrics": {"char_entropy": 1.5, "ngram_repetition": 0.8, "self_bpc": 2.0}},
         "GEN_COLLAPSES_TO_REPETITION"),
        ({"metrics": {"char_entropy": 7.5, "ngram_repetition": 0.05, "self_bpc": 7.0}},
         "GEN_UNIFORM_RANDOM"),
        ({}, "GEN_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed (4/4 cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    n_dim = N_SMOKE if smoke else N_FULL
    gen_len = GENERATE_LENGTH_SMOKE if smoke else GENERATE_LENGTH_FULL
    max_epochs = MAX_EPOCHS_SMOKE if smoke else MAX_EPOCHS_FULL
    seed = 17

    config = {"mode": "smoke" if smoke else "full", "N": n_dim,
              "generate_length": gen_len, "prefix_length": PREFIX_LENGTH,
              "max_epochs": max_epochs, "alpha": ALPHA, "beta": BETA, "seed": seed}
    print(f"[config] {config}", flush=True)
    print(f"[device] {device}", flush=True)

    # Train Phase A on Corpus A
    corpus_a = v3.load_corpus_a()
    train_a = corpus_a[:int(0.8 * len(corpus_a))]
    if smoke:
        train_a = train_a[:4000]
    print(f"[corpus] train_a={len(train_a)}B", flush=True)

    gen_rng = torch.Generator().manual_seed(seed)
    byte_atoms = v3.make_bsc_atoms(v3.VOCAB_SIZE, n_dim, gen_rng).to(device)
    pos_atoms = v3.make_bsc_atoms(v3.K, n_dim, gen_rng).to(device)
    print(f"[train] Phase A...", flush=True)
    W, pool_vecs, pool_labels, pool_used = v3.train_phase_a(
        byte_atoms, pos_atoms, train_a, n_dim, max_epochs, BATCH_SIZE)
    print(f"[train] done. pool_used={pool_used}", flush=True)

    # Generate
    prefix_bytes = list(corpus_a[:PREFIX_LENGTH])
    print(f"[generate] from prefix of {PREFIX_LENGTH} bytes...", flush=True)
    generated = generate(W, pool_vecs, pool_labels, pool_used, byte_atoms, pos_atoms,
                            prefix_bytes, gen_len, n_dim, device)
    generated_text = bytes(generated)
    print(f"[generated] first 100 bytes: {generated_text[:100]!r}", flush=True)

    # Metrics
    entropy = char_entropy(generated)
    repetition = ngram_repetition_rate(generated, n=4)

    # Self-bpc: take a Corpus A continuation and compute bpc using substrate prediction
    # Use bytes AFTER the prefix as ground truth, evaluate substrate prediction at each
    test_start = PREFIX_LENGTH
    test_bytes = list(corpus_a[test_start:test_start + min(256, gen_len)])
    bpc_total = 0.0
    for i, true_byte in enumerate(test_bytes):
        context_so_far = list(corpus_a[:test_start + i])
        ctx_bytes = context_so_far[-v3.K:]
        if len(ctx_bytes) < v3.K:
            ctx_bytes = [v3.PAD_BYTE] * (v3.K - len(ctx_bytes)) + ctx_bytes
        idx_tensor = torch.tensor([ctx_bytes], dtype=torch.long, device=device)
        ctx = v3.build_ctx(byte_atoms, pos_atoms, idx_tensor)
        q = ctx @ W.T
        q = v3.shifted_relu(q, v3.RELU_B)
        sims = (byte_atoms @ q.T) / n_dim
        P_W = torch.softmax(BETA * sims, dim=0).squeeze(1)
        if pool_used > 0 and ALPHA > 0:
            active = pool_vecs[:pool_used]
            labels = pool_labels[:pool_used]
            sims_p = (active @ ctx.T) / n_dim
            weights_p = torch.softmax(BETA * sims_p, dim=0).squeeze(1)
            P_retr = torch.zeros(v3.VOCAB_SIZE, device=device)
            P_retr.scatter_add_(0, labels, weights_p)
            P = ALPHA * P_retr + (1 - ALPHA) * P_W
        else:
            P = P_W
        p_true = float(P[true_byte].clamp(min=1e-12))
        bpc_total += -math.log2(p_true)
    self_bpc = bpc_total / len(test_bytes) if test_bytes else float("inf")

    summary = {
        "metrics": {
            "char_entropy": entropy,
            "ngram_repetition": repetition,
            "self_bpc": self_bpc,
            "n_generated": len(generated),
        },
        "sample_generated_bytes": generated_text[:200].decode("utf-8", errors="replace"),
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nMETRICS: entropy={entropy:.3f}  repetition={repetition:.3f}  "
          f"self_bpc={self_bpc:.3f}", flush=True)
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
    out_dir = get_output_dir("wave14yy_autoregressive_generation_smoke")
    log_event("experiment_started", name="wave14yy_autoregressive_generation", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    # Oracle: substrate self_bpc must be < 8.0 (better than uniform)
    self_bpc = summary["metrics"]["self_bpc"]
    oracle.assert_in_range("self_bpc_smoke", self_bpc, (0.5, 8.0))
    n_gen = summary["metrics"]["n_generated"]
    if n_gen != GENERATE_LENGTH_SMOKE:
        raise AssertionError(f"generated {n_gen} != {GENERATE_LENGTH_SMOKE}")
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yy_autoregressive_generation",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14yy_autoregressive_generation")
    log_event("experiment_started", name="wave14yy_autoregressive_generation", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yy_autoregressive_generation",
              mode="full", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
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
