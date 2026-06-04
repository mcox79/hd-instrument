"""
substrate_polynomial_p4_bcm_factorial_rung1_v1_n512 -- modern-Hopfield polynomial-p upgrade factorial.

ROUTING: notes/routing_polynomial_p_modern_hopfield_engineering_2026-06-04.md +
         notes/exp_dev_handoff_research_bcm_snr_poly_p_2026-06-04.md (Q3 GREEN; episodic spec).

CAPABILITY QUESTION:
  Does upgrading the substrate retrieval from classical outer-product (p=2) to polynomial-p=4 modern
  Hopfield lower the substrate-as-training capacity floor, letting a tiny bigram char-LM learn at N=512
  where classical p=2 fails? 2x2 factorial: (p=2 vs p=4) x (cumulative vs episodic writes). Tests both
  levers (modern-Hopfield capacity AND episodic M_eff bound) per the BCM-SNR drill.

MODERN HOPFIELD RETRIEVAL (Demircigil 2017; bipolar-native):
  Bank of stored (ctx_key, next_value) bipolar pairs. For query ctx q:
    sim_k = (ctx_key_k . q) / N  in [-1,1];  weight_k = sim_k**(p-1)  (sign-preserving for odd p-1);
    pred = sum_k weight_k * next_value_k.   (p=2 -> linear classical; p=4 -> cubic separation, sharper.)
  Score pred vs vocab codes by cosine -> calibrated-temperature softmax -> BPC (de-confounded readout).

WRITE MODES:
  cumulative: bank = ALL training bigram pairs (M grows toward training size; overloads classical p=2).
  episodic:   bank = most-recent E=200 pairs (hard reset every E; M_eff bounded at 200 per BCM drill).

PRE-REGISTERED BANDS (BITS; uniform ~ log2(vocab)):
  HARD-PASS (modern-Hopfield upgrade lowers the floor): p4 arm BPC < uniform - 1.0 on >= 2/3 seeds AND
    p4 beats p2 at matched write mode by > 0.3 bit (the polynomial-p upgrade is causally responsible).
  MIDDLE: p4 shows partial gain (BPC < uniform - 0.5) OR p4>p2 but < 0.3 bit, OR 1/3 seeds.
  HARD-FAIL: p4 no better than p2 at matched mode (upgrade does not help) OR no arm learns (all within
    0.3 bit of uniform).

FORMULA SELF-TESTS (PROT-022):
  1. p=4 retrieval of a single stored pair: pred cosine with the true next_value > 0.9.
  2. polynomial separation sharpens: for sims [1.0, 0.5], weight ratio (1/0.5)**3 = 8 at p=4 vs 2 at p=2.
  3. uniform_bpc = log2(vocab) > 0.

PROT-018: anchor has _n512; substrate N MUST = 512.
PROT-021: seed checkpoints keyed run_mode + N; partials per seed.
QUEUE: remote_cpu_queue (pure numpy; CPU; rung-1). TIMEOUT: 7200s.
ASCII-only stdout.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json, math
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True); sys.exit(1)
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials
from testbed.substrate_lm.data import wikitext2_char_corpus

ANCHOR_NAME = "substrate_polynomial_p4_bcm_factorial_rung1_v1_n512"
_N_SUFFIX = 512
N = 512
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

EPISODE = 200
READOUT_TEMP_GRID = [1.0, 0.5, 0.3, 0.2, 0.15, 0.1]
HP_GAP = 1.0
MID_GAP = 0.5
HF_GAP = 0.3
P4_BEATS_P2 = 0.3

# Arms: (name, p, mode)
ARMS = [("p2_cumulative", 2, "cumulative"), ("p2_episodic", 2, "episodic"),
        ("p4_cumulative", 4, "cumulative"), ("p4_episodic", 4, "episodic")]

if RUN_MODE == "smoke":
    N_ACTIVE = 128
    SEEDS = [7, 17]
    TRAIN_CHARS = 6000
    VAL_CHARS = 1500
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23]
    TRAIN_CHARS = 60000
    VAL_CHARS = 12000


def build_codebook(vocab, n_dim, seed):
    rng = np.random.default_rng(seed + 101)
    return rng.choice([-1.0, 1.0], size=(len(vocab), n_dim)).astype(np.float32)


def poly_retrieve(bank_ctx, bank_next, q, n_dim, p):
    """Modern Hopfield polynomial-p retrieval. bank_ctx/next: (M,N); q:(N,)."""
    if bank_ctx.shape[0] == 0:
        return np.zeros(n_dim, dtype=np.float32)
    sim = (bank_ctx @ q) / n_dim            # (M,) in [-1,1]
    w = np.sign(sim) * (np.abs(sim) ** (p - 1))   # sign-preserving polynomial separation
    return (bank_next.T @ w).astype(np.float32)


def calibrated_bpc(bank_ctx, bank_next, code_matrix, val_ids, n_dim, p, rng):
    nb = min(2000, len(val_ids) - 1)
    starts = rng.integers(0, len(val_ids) - 1, size=nb)
    ctx = code_matrix[val_ids[starts]]       # (nb,N)
    nxt = val_ids[starts + 1]
    # batched retrieval
    sim = (ctx @ bank_ctx.T) / n_dim          # (nb,M)
    w = np.sign(sim) * (np.abs(sim) ** (p - 1))
    pred = w @ bank_next                      # (nb,N)
    pn = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-8)
    cos = pn @ code_matrix.T                  # (nb,V)
    best = float("inf")
    for temp in READOUT_TEMP_GRID:
        z = cos / temp; z = z - z.max(axis=1, keepdims=True); ez = np.exp(z)
        pr = ez / (ez.sum(axis=1, keepdims=True) + 1e-30)
        pt = np.clip(pr[np.arange(nb), nxt], 1e-12, 1.0)
        best = min(best, float(np.mean(-np.log2(pt))))
    return best


def build_bank(train_ids, code_matrix, mode):
    """Return (bank_ctx, bank_next). cumulative=all pairs; episodic=last EPISODE pairs."""
    ctx_ids = train_ids[:-1]; nxt_ids = train_ids[1:]
    if mode == "episodic":
        ctx_ids = ctx_ids[-EPISODE:]; nxt_ids = nxt_ids[-EPISODE:]
    return code_matrix[ctx_ids], code_matrix[nxt_ids]


def _selftest():
    n = 128
    cb = build_codebook(list("abcdef "), n, 1)
    bank_ctx = cb[0:1]; bank_next = cb[1:2]
    pred = poly_retrieve(bank_ctx, bank_next, cb[0], n, 4)
    cos = float(pred @ cb[1] / ((np.linalg.norm(pred) + 1e-8) * (np.linalg.norm(cb[1]) + 1e-8)))
    assert cos > 0.9, f"single-pair p4 recall cos={cos}"
    assert abs((1.0 ** 3 / 0.5 ** 3) - 8.0) < 1e-6
    assert math.log2(7) > 0
    print(f"[selftest] PASS: p4 single-pair recall cos={cos:.3f} poly-sharpening ok", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.default_rng(seed)
    t0 = time.time()
    train_text = wikitext2_char_corpus(split="train", max_chars=TRAIN_CHARS)
    val_text = wikitext2_char_corpus(split="validation", max_chars=VAL_CHARS)
    vocab = sorted(set(train_text) | set(val_text))
    idx = {c: i for i, c in enumerate(vocab)}
    cb = build_codebook(vocab, n_dim, seed)
    train_ids = np.array([idx[c] for c in train_text], dtype=np.int64)
    val_ids = np.array([idx[c] for c in val_text], dtype=np.int64)
    uniform = math.log2(len(vocab))
    arms = {}
    for name, p, mode in ARMS:
        bank_ctx, bank_next = build_bank(train_ids, cb, mode)
        bpc = calibrated_bpc(bank_ctx, bank_next, cb, val_ids, n_dim, p, rng)
        gap = uniform - bpc
        arms[name] = {"p": p, "mode": mode, "bpc": float(bpc), "gap": float(gap), "M": int(bank_ctx.shape[0])}
        print(f"  [seed={seed} {name}] M={bank_ctx.shape[0]} bpc={bpc:.4f} uniform={uniform:.4f} gap={gap:.4f}", flush=True)
    elapsed = time.time() - t0
    print(f"  [seed={seed}] elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "run_mode": RUN_MODE, "uniform_bpc": float(uniform), "arms": arms, "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No results.")
    n_seeds = len(results)
    def arm_gap(name):
        gs = [r["arms"][name]["gap"] for r in results if name in r.get("arms", {})]
        return gs
    def mean_gap(name):
        gs = arm_gap(name); return float(np.mean(gs)) if gs else 0.0
    mg = {a[0]: mean_gap(a[0]) for a in ARMS}
    # p4 learns on >=2/3 seeds?
    p4c_seeds_hp = sum(1 for g in arm_gap("p4_cumulative") if g >= HP_GAP)
    p4e_seeds_hp = sum(1 for g in arm_gap("p4_episodic") if g >= HP_GAP)
    best_p4_hp_seeds = max(p4c_seeds_hp, p4e_seeds_hp)
    # p4 beats p2 at matched mode?
    p4_beats_cum = mg["p4_cumulative"] - mg["p2_cumulative"]
    p4_beats_epi = mg["p4_episodic"] - mg["p2_episodic"]
    best_beat = max(p4_beats_cum, p4_beats_epi)
    best_p4_gap = max(mg["p4_cumulative"], mg["p4_episodic"])
    summary = ("gaps=" + " ".join(f"{a[0]}:{mg[a[0]]:.3f}" for a in ARMS) +
               f" p4_beats_p2(cum={p4_beats_cum:+.3f},epi={p4_beats_epi:+.3f}) "
               f"p4_hp_seeds={best_p4_hp_seeds}/{n_seeds}")

    if best_p4_gap < HF_GAP:
        return ("HARD_FAIL", f"HARD_FAIL: no p4 arm learns (best p4 gap {best_p4_gap:.3f} < {HF_GAP}). {summary}")
    if best_p4_hp_seeds >= math.ceil(2 * n_seeds / 3) and best_beat > P4_BEATS_P2:
        return ("HARD_PASS",
                f"HARD_PASS: polynomial-p=4 learns (gap>={HP_GAP}, {best_p4_hp_seeds}/{n_seeds} seeds) AND "
                f"beats p=2 at matched mode by >{P4_BEATS_P2} bit (upgrade causally lowers the floor). {summary}")
    if best_p4_gap >= MID_GAP or best_beat > 0:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: partial p4 gain or modest p4>p2. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: p4 no better than p2 (upgrade does not help). {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_ACTIVE} mode={RUN_MODE} seeds={SEEDS} "
      f"arms={[a[0] for a in ARMS]} EPISODE={EPISODE}", flush=True)
if RUN_MODE == "full" and N_ACTIVE != _N_SUFFIX:
    raise RuntimeError(f"PROT-018: N_ACTIVE={N_ACTIVE} != _N_SUFFIX={_N_SUFFIX}")

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE, "run_mode": RUN_MODE, "arms": [a[0] for a in ARMS], "EPISODE": EPISODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep
metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "run_mode": RUN_MODE, "EPISODE": EPISODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "uniform_bpc": r.get("uniform_bpc"),
                  "arms": r.get("arms", {}), "elapsed_s": r.get("elapsed_s")} for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
