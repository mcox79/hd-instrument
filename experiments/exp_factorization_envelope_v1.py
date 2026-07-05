# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ: N/A (single-mechanism envelope map; redundancy R=1 vs R=RESTARTS reported side by side)
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb/capacity-feasibility: analytic random baseline (1/V^F per term) + theoretical cliff noted
# - baseline_in_band: the grid is designed to SPAN success->cliff at full-N (discriminator = the cliff)
# - discriminator survives scale: envelope measured AT full-N=8192 (substrate compositional default)
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
#
# FACTORIZATION-ENVELOPE PROBE v1 (generation go/no-go gate)
# =========================================================
# Purpose: measure how far a resonator network can factorize substrate bound
# proposition-vectors back into their role-filler components -- the inverse of
# the encoder, i.e. the core of a substrate-native GENERATION decoder.
#
# A proposition is a SUPERPOSITION of D bound terms; each term is a PRODUCT of
# F factors, each factor drawn from a per-factor codebook of size V (vocab).
#     p = sum_{d=1..D}  prod_{f=1..F}  codebook_f[ idx[d][f] ]      (bipolar BSC)
# The resonator recovers the F-tuple of each term via iterative unbind+cleanup.
# We map the ENVELOPE over three axes the generation decoder cares about:
#     F = factors per term       (role x filler x tense x ... nesting depth)
#     V = per-factor vocab       (lexicon size)
#     D = composition depth      (number of superposed role-filler slots)
# at substrate scale N. High-energy compute (many random restarts + iterate to
# convergence + explaining-away peel-off) is the redundancy lever: we report the
# envelope for single-shot (R=1) vs high-energy (R=RESTARTS) so the single-shot
# cliff is NOT mistaken for a wall.
#
# Contamination control (USER-locked clean-test discipline): codebooks are CLEAN
# iid bipolar vectors (the resonator's intrinsic capacity == honest UPPER BOUND).
# Real concept-encoder fillers are correlated (similar concepts -> similar HVs),
# which REDUCES the envelope; the clean envelope is the ceiling the real decoder
# cannot exceed. If even the clean ceiling is too small, generation is dead
# regardless of encoder quality -- that is the honest go/no-go.
#
# Algebra = the substrate's committed compositional algebra (bipolar BSC:
# bind = elementwise product, superposition = sum) per wave14e/wave14b. The
# resonator factors the REAL-VALUED superposition (faithful resonator target;
# Frady/Kent/Sommer 2020), enabling exact explaining-away subtraction for D>1.
#
# Sources (CITED@):
#  - Resonator Networks 1&2, Frady/Kent/Olshausen/Sommer, Neural Computation 2020 (arxiv 1906.11684)
#  - ACF redundancy lever proven for F=2 in experiments/exp_wave14b_acf_resonator.py (~50x cap lift)
#  - Prior tiny probe: data/exp_resonator_factorization_v1/metrics.json (MIDDLE_BAND; N=2048 V=30 K2=1.0 K3=0.733)

from __future__ import annotations

import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # flush progress on newline (17. PRINT-PROGRESS)

torch.set_num_threads(8)
DEVICE = torch.device("cpu")

ANCHOR_NAME = "factorization_envelope_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)

# ---- high-energy compute budget --------------------------------------------
RESTARTS = 16          # parallel random restarts (batched matmul; redundancy lever)
MAX_ITER = 60          # resonator iterations per restart (early-stop on fixed point)
SEEDS = (7, 13, 19)    # 3 seeds for CI
TRIALS = 10            # trials per (config, seed)
SUCCESS_THRESH = 0.90  # term-recovery rate for "recoverable" (strictly-above-floor band)


def _say(msg: str) -> None:
    print(msg, flush=True)


def _write_start_marker() -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": "envelope",
        "host": platform.node(),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "_start_marker.json.tmp")
    final = os.path.join(OUT_DIR, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(exc: Exception) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME,
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def make_codebooks(F: int, V: int, N: int, gen: torch.Generator) -> list[torch.Tensor]:
    """F codebooks, each V bipolar (+/-1) vectors of dim N (clean iid)."""
    books = []
    for _ in range(F):
        raw = torch.rand((V, N), generator=gen)
        books.append((2.0 * (raw > 0.5).float() - 1.0).to(DEVICE))
    return books


def resonate(residual: torch.Tensor, books: list[torch.Tensor], N: int,
             restarts: int, max_iter: int, gen: torch.Generator):
    """Factor ONE product-term out of `residual` (real-valued superposition).

    Batched resonator: F factors, `restarts` parallel random inits run as
    matmuls. Returns (best_tuple, best_recon, best_dot, iters_used).
    """
    F = len(books)
    V = books[0].shape[0]
    # est[f]: (restarts, N) bipolar current estimate of factor f
    est = []
    for _ in range(F):
        raw = torch.rand((restarts, N), generator=gen)
        est.append((2.0 * (raw > 0.5).float() - 1.0).to(DEVICE))
    prev_sign = None
    iters_used = max_iter
    for it in range(max_iter):
        for i in range(F):
            # unbind factor i: residual * product of the OTHER factor estimates
            other = torch.ones((restarts, N), device=DEVICE)
            for j in range(F):
                if j != i:
                    other = other * est[j]
            unbound = residual.unsqueeze(0) * other           # (restarts, N)
            scores = unbound @ books[i].t() / N                # (restarts, V)
            recon = scores @ books[i]                          # (restarts, N)
            est[i] = torch.sign(recon)
            est[i] = torch.where(est[i] == 0, torch.ones_like(est[i]), est[i])
        cur_sign = torch.cat(est, dim=1)
        if prev_sign is not None and torch.equal(cur_sign, prev_sign):
            iters_used = it + 1
            break
        prev_sign = cur_sign
    # decode each restart -> per-factor argmax index; reconstruct; score vs residual
    idx = []       # (F, restarts)
    for i in range(F):
        sims = est[i] @ books[i].t() / N                       # (restarts, V)
        idx.append(sims.argmax(dim=1))                         # (restarts,)
    idx = torch.stack(idx, dim=0)                              # (F, restarts)
    recon = torch.ones((restarts, N), device=DEVICE)
    for i in range(F):
        recon = recon * books[i][idx[i]]                       # (restarts, N)
    dots = (recon * residual.unsqueeze(0)).sum(dim=1)          # (restarts,)
    best = int(dots.argmax().item())
    best_tuple = tuple(int(idx[i, best].item()) for i in range(F))
    best_recon = recon[best]
    return best_tuple, best_recon, float(dots[best].item()), iters_used


def factor_proposition(true_tuples, books, N, D, restarts, max_iter, gen):
    """Explaining-away: build superposition of D terms, peel off D terms."""
    F = len(books)
    # build real-valued superposition
    s = torch.zeros(N, device=DEVICE)
    for tup in true_tuples:
        term = torch.ones(N, device=DEVICE)
        for i in range(F):
            term = term * books[i][tup[i]]
        s = s + term
    residual = s.clone()
    recovered = []
    for _ in range(D):
        tup, recon, _dot, _iters = resonate(residual, books, N, restarts, max_iter, gen)
        recovered.append(tup)
        residual = residual - recon        # exact peel-off (real-valued residual)
    # order-free multiplicity-aware match
    truth = list(true_tuples)
    hits = 0
    rec_pool = list(recovered)
    for t in truth:
        if t in rec_pool:
            rec_pool.remove(t)
            hits += 1
    return hits / D


def run_config(F: int, V: int, D: int, N: int, restarts: int, seeds, trials, max_iter):
    """Return mean term-recovery over seeds x trials for one envelope point."""
    per_seed = []
    for sd in seeds:
        gen_cb = torch.Generator().manual_seed(1000 + sd + F * 31 + V * 7 + D * 13 + N)
        books = make_codebooks(F, V, N, gen_cb)
        gen_tr = torch.Generator().manual_seed(5000 + sd + F * 17 + V * 3 + D * 11 + N)
        s_ok = 0.0
        for _ in range(trials):
            # sample D DISTINCT random tuples
            tuples = set()
            guard = 0
            while len(tuples) < D and guard < 1000:
                tup = tuple(int(torch.randint(0, V, (1,), generator=gen_tr).item()) for _ in range(F))
                tuples.add(tup)
                guard += 1
            tuples = list(tuples)
            gen_res = torch.Generator().manual_seed(9000 + sd + guard)
            s_ok += factor_proposition(tuples, books, N, D, restarts, max_iter, gen_res)
        per_seed.append(s_ok / trials)
    t = torch.tensor(per_seed)
    return {"F": F, "V": V, "D": D, "N": N, "restarts": restarts,
            "mean": float(t.mean().item()), "std": float(t.std(unbiased=False).item()),
            "per_seed": per_seed}


def build_grid(smoke: bool):
    """Envelope grid. smoke = tiny correctness gate; full = 3-axis map at scale."""
    if smoke:
        # correctness gate: easy config MUST recover ~1.0; hard config MUST cliff.
        return [
            ("easy_D1", dict(F=2, V=16, D=1, N=8192, restarts=RESTARTS)),   # must ~1.0
            ("easy_D2", dict(F=2, V=16, D=2, N=8192, restarts=RESTARTS)),   # peel-off must work
            ("hard_V", dict(F=2, V=4096, D=4, N=1024, restarts=1)),         # must cliff (low)
        ]
    N0 = 8192  # substrate compositional default (gap3: "do NOT smoke at 2048")
    grid = []
    # Sweep A -- factors F (hold V=256, D=2), single-shot vs high-energy
    for F in (2, 3, 4):
        grid.append((f"A_F{F}_hi", dict(F=F, V=256, D=2, N=N0, restarts=RESTARTS)))
        grid.append((f"A_F{F}_lo", dict(F=F, V=256, D=2, N=N0, restarts=1)))
    # Sweep B -- vocab V (hold F=2, D=2)
    for V in (64, 256, 1024, 4096):
        grid.append((f"B_V{V}_hi", dict(F=2, V=V, D=2, N=N0, restarts=RESTARTS)))
        grid.append((f"B_V{V}_lo", dict(F=2, V=V, D=2, N=N0, restarts=1)))
    # Sweep C -- composition depth D (hold F=2, V=256)
    for D in (1, 2, 3, 4, 6):
        grid.append((f"C_D{D}_hi", dict(F=2, V=256, D=D, N=N0, restarts=RESTARTS)))
        grid.append((f"C_D{D}_lo", dict(F=2, V=256, D=D, N=N0, restarts=1)))
    # Generation-relevant points: subject/verb/object = 3 slots at real vocab
    grid.append(("GEN_svo_1k", dict(F=2, V=1024, D=3, N=N0, restarts=RESTARTS)))
    grid.append(("GEN_svo_4k", dict(F=2, V=4096, D=3, N=N0, restarts=RESTARTS)))
    # N-scaling of reference point (F=2, V=256, D=2)
    for N in (1024, 4096):
        grid.append((f"N_{N}_ref", dict(F=2, V=256, D=2, N=N, restarts=RESTARTS)))
    return grid


def verdict_from_results(results: dict):
    """GO / MIDDLE / NO-GO for the generation direction."""
    def m(name):
        return results[name]["mean"] if name in results else None
    # GO if a generation-useful point clears threshold at full-N with high energy
    gen_ok = (m("GEN_svo_1k") is not None and m("GEN_svo_1k") >= SUCCESS_THRESH)
    # NO-GO if even a small config fails badly
    tiny = m("B_V64_hi")
    nogo = (tiny is not None and tiny < 0.50)
    if nogo:
        v = "NO_GO"
        msg = "cliff too early: F=2 V=64 D=2 recovery < 0.50 even high-energy"
    elif gen_ok:
        v = "GO"
        msg = "generation-viable: S/V/O (F=2 V=1024 D=3) recovery >= 0.90 at N=8192 high-energy"
    else:
        v = "MIDDLE_BAND"
        msg = "partial envelope: usable for small propositions; chunking needed beyond"
    return v, msg


def _run_selftest() -> int:
    """Fast correctness gate for the queue_add step-3 --self-test (180s cap).

    Runs the same 3-config smoke correctness grid (build_grid(smoke=True)) with
    the same seed/trial budget as the --smoke gate and asserts the identical
    easy/cliff bands. Returns 0 on pass, 1 on fail.

    Writes NO metrics.json and NO start-marker: this must NOT clobber the
    canonical envelope output at data/exp_<ANCHOR_NAME>/metrics.json. The gate
    isolates output via HDLAB_EXP_NAME=<name>_selftest, but this cell hardcodes
    OUT_DIR and does not honor that env var, so the only safe behavior is to
    touch nothing on disk here and signal correctness purely via exit code.
    """
    t0 = time.perf_counter()
    grid = build_grid(smoke=True)
    results = {}
    for name, cfg in grid:
        results[name] = run_config(seeds=(SEEDS[0],), trials=5, max_iter=MAX_ITER, **cfg)
    easy1 = results["easy_D1"]["mean"]
    easy2 = results["easy_D2"]["mean"]
    hard = results["hard_V"]["mean"]
    ok = (easy1 >= 0.99) and (easy2 >= 0.90) and (hard < 0.60)
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: "
         f"easy_D1={easy1:.3f} (>=0.99) easy_D2={easy2:.3f} (>=0.90) "
         f"hard_cliff={hard:.3f} (<0.60)  [{time.perf_counter()-t0:.1f}s]")
    return 0 if ok else 1


def main() -> None:
    # --self-test: fast correctness gate for the queue_add step-3 gate (180s cap).
    # Mirrors the --smoke correctness asserts but writes NO metrics/start-marker,
    # so it cannot clobber the canonical envelope metrics.json (OUT_DIR is
    # hardcoded and HDLAB_EXP_NAME isolation is not honored by this cell, so we
    # simply touch nothing on disk here). sys.exit -> SystemExit is re-raised
    # ahead of the except-Exception crash handler. Exits 0 pass / 1 fail.
    if "--self-test" in sys.argv:
        sys.exit(_run_selftest())
    smoke = "--smoke" in sys.argv
    run_mode = "smoke" if smoke else "envelope"
    _write_start_marker()
    t0 = time.perf_counter()
    _say(f"[{ANCHOR_NAME}] run_mode={run_mode} restarts={RESTARTS} iters={MAX_ITER} "
         f"seeds={SEEDS} trials={TRIALS}")

    grid = build_grid(smoke)
    results = {}
    for i, (name, cfg) in enumerate(grid):
        tc = time.perf_counter()
        seeds = (SEEDS[0],) if smoke else SEEDS
        trials = 5 if smoke else TRIALS
        r = run_config(seeds=seeds, trials=trials, max_iter=MAX_ITER, **cfg)
        results[name] = r
        _say(f"  [{i+1}/{len(grid)}] {name:12s} F={cfg['F']} V={cfg['V']:5d} D={cfg['D']} "
             f"N={cfg['N']:5d} R={cfg['restarts']:3d}  recovery={r['mean']:.3f} "
             f"(+/-{r['std']:.3f})  [{time.perf_counter()-tc:.1f}s]")

    # analytic random baseline (per-term): 1 / V^F  (THEORETICAL@combinatorial)
    elapsed = time.perf_counter() - t0

    if smoke:
        easy1 = results["easy_D1"]["mean"]
        easy2 = results["easy_D2"]["mean"]
        hard = results["hard_V"]["mean"]
        ok = (easy1 >= 0.99) and (easy2 >= 0.90) and (hard < 0.60)
        verdict = "SMOKE_PASS" if ok else "SMOKE_FAIL"
        msg = (f"resonator correctness: easy_D1={easy1:.3f} (must>=0.99) "
               f"easy_D2={easy2:.3f} (peel-off, must>=0.90) hard_cliff={hard:.3f} (must<0.60)")
    else:
        verdict, msg = verdict_from_results(results)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "run_mode": run_mode,
        "elapsed_s": elapsed,
        "n_seeds": len(SEEDS) if not smoke else 1,
        "config": {"RESTARTS": RESTARTS, "MAX_ITER": MAX_ITER, "SEEDS": list(SEEDS),
                   "TRIALS": TRIALS, "SUCCESS_THRESH": SUCCESS_THRESH,
                   "algebra": "bipolar_BSC_elementwise_product",
                   "codebook": "clean_iid_bipolar_upper_bound"},
        "results": results,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)  # atomic (META_RULE_AH)
    _say(f"\n[{ANCHOR_NAME}] {verdict}: {msg}")
    _say(f"[{ANCHOR_NAME}] metrics -> {final}  elapsed={elapsed:.1f}s")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(e)
        raise
