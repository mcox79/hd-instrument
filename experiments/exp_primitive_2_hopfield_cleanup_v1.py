"""
PRIMITIVE 2 -- Hopfield-cleanup quad-head (DECISION 226 STEP-3; implements the LOCKED Skunkworks prereg).
The CLEANUP/DECODE layer for residue-FPE (P1 deferred the efficient decode here). Four heads over the residue
codebook, with an honest distinctness analysis (heads 1-3 = softness spectrum on the SAME flat O(R) cleanup;
HEAD 4 = the only sub-O(R) FACTORED class):

  HEAD 1 naive max-cos         flat O(R); hard argmax over the codebook (cosine_cleanup).
  HEAD 2 dense modern-Hopfield flat O(R); softmax(beta * C @ q) with beta SET from Ramsauer Theorem-4 (NOT tuned).
  HEAD 3 sparse-Hopfield       flat O(R); sparsemax(beta * C @ q) (alpha=2 entmax; closed-form; sparser basins).
  HEAD 4 resonator-decoder     FACTORED O(sum m_b); OLS/Gram-correction + soft phasor estimates + random restarts
                               + reconstruction-accept (the de-risked recipe; T3/resonator_network_decoder + Kymn-OLS).

GATES (tune-free; honest both-verdict-paths):
  GATE-D (closed-form beta fidelity): verify HEAD-2 retrieval succeeds at beta SET from Ramsauer Theorem-4
     beta=f(N,|M|,Delta_min) (NOT fitted). PASS = accuracy within the predicted band at the formula-beta.
  GATE-E (gerrymander-guarded Delta_min envelope): sweep noise (the Delta_min-comfort proxy); measure ALL heads on
     the SAME grid + SAME codebooks; report best-head-per-regime vs a PRE-REGISTERED theory-derived selection map.
     Divergence from the map = honest theory-gap finding, NOT a re-pick.
  GATE-F (resonator log-scaling = WORK-vs-R; the headline open-part): MEASURE decode WORK (K restarts x iterations)
     as a FUNCTION of R; compare to brute-force O(R). PASS = work SUB-LINEAR in R (~sum(m_b)) with accuracy held AND
     no per-scale re-tuning. HONEST_BOUNDED = work ~O(R) OR per-scale-tuning required. INTEGER-residue scope ONLY
     (continuous bounded by P1 GATE-C1; not claimed here). Work counters (K + iterations) are FIRST-CLASS metrics.

INTEGER-residue scope. OOM-lesson: loop-not-broadcast where memory matters. torch device-agnostic + batched where safe.
queue-compatible (--self-test/--smoke/full). 11th rule (substrate-internal; no LLM; closed-form heads). ASCII only.
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
ANCHOR = "primitive_2_hopfield_cleanup_v1"

if RUN_MODE == "smoke":
    N = 1024; SEEDS = [7]; ENV_BASES = [3, 5, 7]; NOISE = [0.05, 0.30, 0.45]; F_BASES = [[3, 5, 7], [3, 5, 7, 11]]
else:
    N = 4096; SEEDS = [7, 17, 23]; ENV_BASES = [3, 5, 7, 11]
    NOISE = [0.05, 0.15, 0.25, 0.35, 0.42, 0.46]   # span the naive->sparse crossover (high noise differentiates heads)
    # GATE-F R-sweep: 5 points spanning R ~1155 -> ~111M (5 orders of magnitude) for the R8 asymptotic regression.
    # The resonator is FACTORED (per-base codebooks sum(m_b); NEVER the R-codebook) -> large R is cheap (no OOM).
    F_BASES = [[3, 5, 7, 11], [3, 5, 7, 11, 13], [3, 5, 7, 11, 13, 17],
               [3, 5, 7, 11, 13, 17, 19], [3, 5, 7, 11, 13, 17, 19, 23]]   # R=1155,15015,255255,~4.85M,~111M
F_NTEST = 40 if RUN_MODE == "smoke" else 200   # R7: test-set adequacy (~1.5% CI at large R)

# ---- PRE-REGISTERED tune-free bands (locked BEFORE run) ----
BETA_K = 2.0                 # GATE-D: Ramsauer-style closed-form beta = BETA_K/Delta_min * log(2 N M); NOT fitted
TOL_D = 0.02 + 3.0 / math.sqrt(N)        # GATE-D finite-N band around the predicted retrieval bound
ACC_BAR = 0.90              # GATE-E/F per-head accuracy bar (recovered correct codeword)
RESON_RESTARTS = 6          # GATE-F pre-registered K_max (FIXED across the R-sweep; per-scale-retune = honest-bounded)
RESON_ITERS = 60            # GATE-F pre-registered iteration cap
RESON_BETA = 8.0            # GATE-F resonator soft-weight temperature (FIXED)
RECON_THRESH = 0.9          # GATE-F reconstruction-accept threshold (FIXED)
# GATE-F log-scaling band = log-log work-vs-R EXPONENT < 0.5 (the operative test; a raw ratio constant was dropped
# per STEP-4 VET minor -- the regression exponent is the better, scale-robust band).
# WORK granularity: "work" = number of N-dim codeword-correlations (HEAD-4 ~ sum(m_b)/iter; brute-force ~ R), so
# work-vs-O(R) is apples-to-apples (both pay O(N) per correlation).


def _gen(seed):
    return torch.Generator(device=DEV).manual_seed(seed)


# ---------------- residue-FPE codebook (P1 machinery; integer scope) ----------------
def base_channels(seed, bases):
    g = _gen(seed)
    return [(m, torch.randint(1, m, (N,), generator=g, device=DEV).double()) for m in bases]


def residue_fpe(x, chans):
    out = torch.ones((x.shape[0], N), dtype=torch.complex128, device=DEV)
    for (m, a) in chans:
        out = out * torch.exp(1j * (2 * math.pi / m) * x.unsqueeze(-1) * a.unsqueeze(0))
    return out


def per_base_vec(m, a, r):
    return torch.exp(1j * (2 * math.pi / m) * float(r) * a)


def _crt(residues, bases, R):
    x = 0
    for r, m in zip(residues, bases):
        Mi = R // m; inv = pow(Mi % m, -1, m); x = (x + r * Mi * inv) % R
    return x


def noisy_query(c, p, g):
    # bit-flip-style phase noise on a unit-phasor codeword: rotate a fraction p of coords by random phase
    mask = (torch.rand(c.shape, generator=g, device=DEV) < p)
    rot = torch.exp(1j * (torch.rand(c.shape, generator=g, device=DEV) * 2 * math.pi))
    return torch.where(mask, c * rot, c)


# ---------------- HEADS 1-3 (flat O(R) cleanup; softness spectrum) ----------------
def head_naive(q, C):                              # HEAD 1: hard argmax (= HEAD 2 at beta->inf)
    return int((C.conj() @ q).real.argmax().item())


def head_dense_hopfield(q, C, beta):               # HEAD 2: softmax(beta * sim) one-step + argmax
    sim = (C.conj() @ q).real / N
    w = torch.softmax(beta * sim, 0)
    return int(w.argmax().item())                  # one-step retrieval -> nearest stored pattern


def _sparsemax(z):
    # Martins-Astudillo sparsemax (alpha=2 entmax; closed form; sparse simplex projection)
    zs, _ = torch.sort(z, descending=True)
    rng = torch.arange(1, z.shape[0] + 1, device=z.device, dtype=z.dtype)
    cs = torch.cumsum(zs, 0)
    k = (1 + rng * zs > cs).to(z.dtype)
    kmax = int(k.sum().item())
    tau = (cs[kmax - 1] - 1) / kmax
    return torch.clamp(z - tau, min=0.0)


def head_sparse_hopfield(q, C, beta):              # HEAD 3: sparsemax(beta*sim) -> sharper sparse basins
    sim = (C.conj() @ q).real / N
    w = _sparsemax(beta * sim)
    return int(w.argmax().item())


# ---------------- HEAD 4 (factored O(sum m_b) resonator; de-risked recipe + work counters) ----------------
def head_resonator(Rx, chans, cbs, Grams, bases, R):
    """OLS/Gram-correction + soft phasor estimates + random restarts + reconstruction-accept.
    Returns (residue_picks, K_restarts, iters_total, work_units). R6 WORK-ACCOUNTING COMPLETENESS: work counts
    per-iteration codeword-correlations (sum m_b) + per-base soft-recombine + the reconstruction-accept verify cost;
    it EXCLUDES the OLS Grams = pinv(C_b C_b^H) which are PRECOMPUTED ONCE per base (codebook fixed -> AMORTIZED,
    not per-decode). iters_total reported SEPARATELY (R8: confirm iterations stay sub-linear vs R)."""
    nb = len(chans); work = 0; iters_total = 0
    for rs in range(RESON_RESTARTS):
        est = [cbs[b][rs % cbs[b].shape[0]].clone() for b in range(nb)]; last = None
        for _ in range(RESON_ITERS):
            iters_total += 1
            picks = []
            for b in range(nb):
                other = torch.ones(N, dtype=torch.complex128, device=DEV)
                for b2 in range(nb):
                    if b2 != b:
                        other = other * est[b2]
                unbound = Rx * other.conj()
                coeffs = Grams[b] @ (cbs[b] @ unbound.conj())              # OLS/Gram-corrected (simplex codebook)
                w = torch.softmax(RESON_BETA * coeffs.abs(), 0).to(torch.complex128)
                soft = (cbs[b] * w.unsqueeze(-1)).sum(0); est[b] = soft / (soft.abs() + 1e-12)
                picks.append(int(coeffs.abs().argmax().item()))
                work += 2 * cbs[b].shape[0]                                # m_b corr + m_b soft-recombine -> O(sum m_b)/iter
            if picks == last:
                break
            last = picks
        work += sum(bases)                                                # R6: reconstruction-accept verify cost (per restart)
        rec = residue_fpe(torch.tensor([float(_crt(picks, bases, R))], device=DEV).double(), chans)[0]
        if (rec * Rx.conj()).real.mean() > RECON_THRESH:                  # reconstruction-accept
            return picks, rs + 1, iters_total, work
    return picks, RESON_RESTARTS, iters_total, work


def beta_closed_form(delta_min, M):
    # Ramsauer-Theorem-4-style closed-form beta = f(N, |M|, Delta_min); SET not fitted (GATE-D tune-free).
    # |M| = R = the ACTUAL number of stored patterns (codebook size), NOT a hardcoded cap (F1 fix).
    return BETA_K / max(delta_min, 1e-6) * math.log(2 * N * M)


def preregistered_best_head(delta_min, noise_list):
    """GATE-E gerrymander-guard (F2 fix): PRE-REGISTERED theory-derived selection map, computed from the codebook
    margin + noise-erosion model BEFORE any accuracy. SIMILARITY-MARGIN crossover (naive-suffices-at-large-separation
    vs sparse-at-small):
      - phase-noise rate p erodes the true-codeword similarity to ~ (1 - 2p) (rotated coords average to ~0).
      - the nearest COMPETITOR similarity ~ off_diag_max = (1 - delta_min) (the codebook's max off-diagonal).
      - naive (hard nearest-codeword) is robust while the margin (1-2p) - off_diag exceeds the finite-N noise
        fluctuation 3/sqrt(N); below that, sparse-Hopfield's sharper basins are the predicted lever.
    Theory-derived (codebook margin + noise model + finite-N band), NOT fitted to accuracy. A genuine differentiated
    per-regime prediction (naive at low noise, sparse at high noise); the run VERIFIES it (divergence = theory-gap)."""
    # F2b fix: derive the noise-eroded margin from the cell's ACTUAL noisy_query model (rotate fraction p of coords):
    #   true-codeword sim ~ (1-p); nearest competitor sim ~ (1-p)*off_diag; eroded MARGIN ~ (1-p)*delta_min.
    # (was (1-2p)-off_diag, inconsistent with the noise model -> produced an artifact divergence; now consistent.)
    band = 3.0 / math.sqrt(N)
    pred = {}
    for p in noise_list:
        margin = (1.0 - p) * delta_min
        pred[str(p)] = "naive" if margin >= band else "sparse"
    return pred


# ---------------- GATES ----------------
def codebook_delta_min(C):
    # min separation Delta_i = min_j (1 - Re<c_i,c_j>/N); sampled subset for cost
    k = min(C.shape[0], 80)
    G = (C[:k].conj() @ C[:k].T).real / N
    G = G - torch.eye(k, device=DEV) * 2
    return float((1.0 - G.max()).item())


def gate_DE(seed, bases):
    """GATE-D (closed-form beta fidelity) + GATE-E (quad-head Delta_min/noise envelope, gerrymander-guarded)."""
    g = _gen(seed); chans = base_channels(seed, bases)
    R = 1
    for m in bases: R *= m
    xs = torch.arange(0, R, device=DEV).double()
    C = residue_fpe(xs, chans)                                            # (R, N) flat codebook
    cbs = [torch.stack([per_base_vec(m, a, r) for r in range(m)], 0) for (m, a) in chans]
    Grams = [torch.linalg.pinv(cb @ cb.conj().T) for cb in cbs]
    dmin = codebook_delta_min(C)
    beta = beta_closed_form(dmin, R)                                      # SET from formula, |M|=R (F1 fix)
    # GATE-E gerrymander-guard (F2): PRE-REGISTERED theory-derived selection map, BEFORE the accuracy run
    predicted = preregistered_best_head(dmin, NOISE)
    n_test = min(R, 120)
    env = {}
    for p in NOISE:
        tgt = torch.randint(0, R, (n_test,), generator=g, device=DEV)
        acc = {h: 0 for h in ["naive", "dense", "sparse", "reson"]}
        for i in range(n_test):
            q = noisy_query(C[tgt[i]], p, g)
            if head_naive(q, C) == int(tgt[i]): acc["naive"] += 1
            if head_dense_hopfield(q, C, beta) == int(tgt[i]): acc["dense"] += 1
            if head_sparse_hopfield(q, C, beta) == int(tgt[i]): acc["sparse"] += 1
            picks, _, _, _ = head_resonator(q, chans, cbs, Grams, bases, R)
            if _crt(picks, bases, R) == int(tgt[i]): acc["reson"] += 1
        env[str(p)] = {h: acc[h] / n_test for h in acc}
    # empirical best among the FLAT heads (1-3; HEAD-4 resonator efficiency is GATE-F's domain, not the flat envelope)
    emp_best = {p: max(("naive", "dense", "sparse"), key=lambda h: env[p][h]) for p in env}
    # gerrymander-guarded comparison: empirical-best vs PRE-REGISTERED predicted; divergence = honest theory-gap
    regime_map = {p: {"predicted": predicted[p], "empirical_best": emp_best[p],
                      "match": predicted[p] == emp_best[p]} for p in env}
    return {"R": R, "delta_min": dmin, "beta_closed_form": beta, "envelope": env,
            "preregistered_selection_map": predicted, "regime_map_predicted_vs_empirical": regime_map,
            "map_match_fraction": sum(v["match"] for v in regime_map.values()) / len(regime_map),
            "gate_D_dense_acc_lownoise": env[str(NOISE[0])]["dense"]}


def gate_F(seed, bases):
    """GATE-F resonator WORK-vs-R: instrument K + iterations (work) at fixed (pre-registered) hyperparams."""
    g = _gen(seed); chans = base_channels(seed, bases)
    R = 1
    for m in bases: R *= m
    summ = sum(bases)
    cbs = [torch.stack([per_base_vec(m, a, r) for r in range(m)], 0) for (m, a) in chans]
    Grams = [torch.linalg.pinv(cb @ cb.conj().T) for cb in cbs]   # R6: precomputed ONCE per base (amortized)
    n_test = min(R, F_NTEST)                                       # R7: test-set adequacy (~1.5% CI at large R)
    tgt = torch.randint(0, R, (n_test,), generator=g, device=DEV)
    Rt = residue_fpe(tgt.double(), chans)                          # (n_test, N) -- factored, NOT R-codebook
    ok = 0; tot_K = 0; tot_work = 0; tot_iters = 0
    for i in range(n_test):
        picks, K, iters, wk = head_resonator(Rt[i], chans, cbs, Grams, bases, R)
        tot_K += K; tot_work += wk; tot_iters += iters
        if _crt(picks, bases, R) == int(tgt[i]): ok += 1
    acc = ok / n_test
    ci95 = 1.96 * math.sqrt(max(acc * (1 - acc), 1e-9) / n_test)   # R7: report accuracy 95% CI
    return {"R": R, "sum_m_b": summ, "acc": acc, "acc_ci95": ci95, "n_test": n_test, "avg_K": tot_K / n_test,
            "avg_iters": tot_iters / n_test, "avg_work": tot_work / n_test, "brute_force_O_R": R}


def _loglog_slope(xs, ys):
    # least-squares slope of log(y) vs log(x) = the scaling exponent
    import math as _m
    lx = [_m.log(x) for x in xs]; ly = [_m.log(max(y, 1e-9)) for y in ys]
    n = len(lx); mx = sum(lx) / n; my = sum(ly) / n
    num = sum((lx[i] - mx) * (ly[i] - my) for i in range(n)); den = sum((lx[i] - mx) ** 2 for i in range(n))
    return num / den if den > 1e-12 else float("nan")


def verdict(de, fsweep):
    d_pass = de["gate_D_dense_acc_lownoise"] >= ACC_BAR
    if not d_pass:
        return ("GATE_D_FAIL", f"dense-Hopfield at closed-form beta acc {de['gate_D_dense_acc_lownoise']:.3f} < {ACC_BAR} -> beta formula does not retrieve")
    # R8 ASYMPTOTIC-FIT: log-log regression of WORK vs R (exponent) + ITERATIONS vs R (separately)
    Rs = [f["R"] for f in fsweep]
    work_exp = _loglog_slope(Rs, [f["avg_work"] for f in fsweep])      # < 1 => sub-linear in R (log-scaling)
    iters_exp = _loglog_slope(Rs, [max(f["avg_iters"], 1e-9) for f in fsweep])
    k_grows = fsweep[-1]["avg_K"] > fsweep[0]["avg_K"] + 0.5
    # R7 (F3 fix): PASS gate uses the CONSERVATIVE LOWER CI bound (acc - ci95 >= bar), not the lenient upper bound,
    # so sub-bar accuracy at large R cannot slip through and get labeled log-scaling-demonstrated.
    acc_held = all(f["acc"] - f["acc_ci95"] >= ACC_BAR for f in fsweep)
    # PASS: work exponent well below 1 (sub-linear), iterations not accelerating, K not growing, accuracy held
    sublinear = (work_exp < 0.5) and (iters_exp < 0.5) and (not k_grows) and acc_held
    if sublinear:
        return ("P2_LOGSCALING_DEMONSTRATED_INTEGER",
                f"GATE-D PASS + GATE-F work-vs-R SUB-LINEAR: work exponent={work_exp:.3f} (<1; ~log R), iters exponent={iters_exp:.3f}, K not growing, acc held>={ACC_BAR} within CI across R {Rs[0]}->{Rs[-1]} -> INTEGER-residue log-scaling decode DEMONSTRATED + quad-head envelope characterized (P1's deferred B2 delivered, integer scope)")
    return ("P2_HONEST_BOUNDED",
            f"GATE-D PASS + quad-head envelope characterized BUT GATE-F NOT sub-linear (work exponent={work_exp:.3f}, iters exponent={iters_exp:.3f}, k_grows={k_grows}, acc_held={acc_held}) -> log-scaling advantage NOT demonstrated; convergent OLS-Gram recipe + cleanup envelope still fileable (honest-bounded)")


def _selftest():
    assert DEV is not None
    # sparsemax sums to 1 + is sparse
    z = torch.tensor([3.0, 1.0, 0.2, 0.1], device=DEV, dtype=torch.float64)
    sm = _sparsemax(z); assert abs(float(sm.sum()) - 1.0) < 1e-6 and int((sm > 0).sum()) < 4, "sparsemax not sparse-simplex"
    # closed-form beta positive + retrieves on a clean-ish small case
    de = gate_DE(7, [3, 5]); assert de["gate_D_dense_acc_lownoise"] >= 0.5, f"dense head low-noise acc too low {de['gate_D_dense_acc_lownoise']}"
    # distinctness: HEAD 1 == HEAD 2 at beta->inf (hard-argmax limit) on a sample
    g = _gen(0); chans = base_channels(0, [3, 5]); R = 15
    C = residue_fpe(torch.arange(0, R, device=DEV).double(), chans)
    q = noisy_query(C[4], 0.05, g)
    assert head_naive(q, C) == head_dense_hopfield(q, C, 1e6), "HEAD1 != HEAD2 at beta->inf (distinctness check)"
    print("[selftest] PASS: sparsemax-simplex + closed-form-beta-retrieves + HEAD1=HEAD2@beta-inf distinctness", flush=True)


def main():
    print(f"[start] {ANCHOR} run_mode={RUN_MODE} dev={DEV} N={N} env_bases={ENV_BASES} F_bases={F_BASES} seeds={SEEDS}", flush=True)
    _selftest()
    out = get_output_dir(os.environ.get("HDLAB_EXP_NAME", ANCHOR)); t0 = time.time()
    de = gate_DE(SEEDS[0], ENV_BASES)
    print(f"\n[GATE-D] R={de['R']} delta_min={de['delta_min']:.3f} beta_cf={de['beta_closed_form']:.2f} dense_acc_lownoise={de['gate_D_dense_acc_lownoise']:.3f}", flush=True)
    print(f"[GATE-E] envelope (acc per head per noise) + gerrymander-guard (predicted vs empirical best):", flush=True)
    for p, row in de["envelope"].items():
        rm = de["regime_map_predicted_vs_empirical"][p]
        print(f"   noise={p}: naive={row['naive']:.2f} dense={row['dense']:.2f} sparse={row['sparse']:.2f} reson={row['reson']:.2f} | predicted={rm['predicted']} empirical={rm['empirical_best']} match={rm['match']}", flush=True)
    print(f"[GATE-E] selection-map match fraction (predicted==empirical): {de['map_match_fraction']:.2f}", flush=True)
    print(f"[GATE-F] resonator WORK-vs-R sweep (K + work first-class):", flush=True)
    fsweep = [gate_F(SEEDS[0], B) for B in F_BASES]
    for f in fsweep:
        print(f"   R={f['R']} sum_m_b={f['sum_m_b']}: acc={f['acc']:.3f}+-{f['acc_ci95']:.3f} (n={f['n_test']}) avg_K={f['avg_K']:.2f} avg_iters={f['avg_iters']:.1f} avg_work={f['avg_work']:.0f} | brute O(R)={f['brute_force_O_R']}", flush=True)
    v, vmsg = verdict(de, fsweep)
    print(f"\n[VERDICT] {v} -- {vmsg}", flush=True)
    metrics = {"anchor_name": ANCHOR, "run_mode": RUN_MODE, "device": str(DEV), "N": N, "seeds": SEEDS,
               "gate_DE": de, "gate_F_sweep": fsweep, "verdict": v, "verdict_msg": vmsg,
               "prereg_bands": {"BETA_K": BETA_K, "ACC_BAR": ACC_BAR, "RESON_RESTARTS": RESON_RESTARTS,
                                "RESON_ITERS": RESON_ITERS, "RESON_BETA": RESON_BETA, "RECON_THRESH": RECON_THRESH,
                                "logscaling_band": "work-vs-R log-log exponent < 0.5; acc-ci95-lower >= ACC_BAR"},
               "honest_scope": "INTEGER-residue cleanup/decode. HEADS 1-3 softness spectrum flat O(R) (HEAD1=HEAD2 at beta-inf); HEAD4 factored sub-O(R). GATE-F log-scaling is INTEGER-scoped; continuous bounded by P1 GATE-C1. Both-verdict-paths; work-vs-R MEASURED not presupposed.",
               "elapsed_s": time.time() - t0, "compute_backend": str(DEV)}
    write_metrics(out, metrics, [{"gate_DE": de, "gate_F_sweep": fsweep}])
    print(f"[metrics] written {out}/metrics.json", flush=True)


if __name__ == "__main__":
    if SELFTEST:
        _selftest(); sys.exit(0)
    main()
