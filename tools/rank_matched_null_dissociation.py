"""RANK-MATCHED NULL for the dissociation instrument -- the control a low-rank arm must beat.

WHY THIS EXISTS (2026-08-18). The dissociation instrument
(`experiments/exp_dissociation_score_instrument_v1.py`) scores AUC(SET P vs SET S) where the
INCUMBENT BASELINE SITS FAR BELOW 0.5 (0.0603 on the 202-row sub-population, 0.0710 on 242).
On such an instrument, DESTROYING INFORMATION MOVES THE SCORE TOWARD 0.5. The whole interval
(0.06, 0.50) is therefore reachable by degradation alone, and an arm that reduces the rank of the
representation will read "closer to substitutability" while carrying strictly less of anything.

None of the four standing floors catches this. F_SCRAMBLE permutes the word-to-row assignment and
F_CONSTANT_PROTOTYPE collapses to a mean direction -- both destroy ALL of the representation and
land AT chance, so they bound the top of the range, not the middle. F_ORTHOGRAPHIC and F_FREQUENCY
are representation-independent. NOTHING in the battery asks "what would an arm of THIS RANK score
if its directions carried no information at all?".

MEASURED (this tool, on `exp_crossview_convergence_hub_v1`'s own 202-row surviving population):
a RANDOM k-dimensional projection of the incumbent store, which has never seen any second channel,
reads AUC 0.4119 (k=2), 0.3057 (k=8), 0.1776 (k=32), 0.0795 (k=128), 0.0536 (k=256, = centered
full rank). That cell's PRIMARY arm, at its own k*=8, read 0.3129. The rank-matched null accounts
for the arm in full.

USE: for any arm that reduces rank, report its AUC BESIDE this null AT THE ARM'S OWN RANK.
An arm that does not beat its own rank-matched null has demonstrated no extraction.

    python tools/rank_matched_null_dissociation.py

Read-only: loads the landed population + the store cache, writes nothing but stdout.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_cue_to_store_translation_v1 as CTS          # noqa: E402
import experiments.exp_dissociation_score_instrument_v1 as DISS    # noqa: E402
from tools import floor_battery as FB                              # noqa: E402
from tools.exp_checkpoint import unit_key, load_units              # noqa: E402

CELL_DIR = os.path.join(REPO, "data", "exp_crossview_convergence_hub_v1")
INST_DIR = os.path.join(REPO, "data", "exp_dissociation_score_instrument_v1")
DEF_CACHE = os.path.join(REPO, "scratch", "_simplewiki_defs.json")
SEED = 20260816
N_REP = 200
RANKS = (2, 4, 8, 16, 32, 64, 128, 256)
# MAIN_STORE_DEF's landed k* and canonical correlations, read off
# data/exp_crossview_convergence_hub_v1/metrics.json:report.CCA_DIAGNOSTICS.MAIN_STORE_DEF
K_STAR = 8
RHO = np.array([0.4701, 0.3089, 0.3072, 0.2824, 0.2756, 0.2646, 0.2564, 0.2474])
LAM_REL = 1.0                       # lam_rel_selected for that pairing

l2n = FB.l2n


def surviving_population():
    """The exact 202-row sub-population exp_crossview_convergence_hub_v1 scored, rebuilt off disk
    from the landed instrument checkpoint + that cell's own COVERAGE unit. Both reconstruction
    counts are ASSERTED, so a silent drift in either input voids this tool rather than shifting
    its numbers."""
    C = CTS.load_cache()
    anchors = C["anchors"]
    mat = np.asarray(C["mat"], dtype=np.float64)
    mat_ok = np.asarray(C["mat_ok"], dtype=bool)
    pos_idx = C["pos"]
    pop = load_units(INST_DIR)[unit_key("POPULATION", "v1.7", "full")]
    mP = [tuple(x) for x in pop["matchedP"]]
    mS = [tuple(x) for x in pop["matchedS"]]
    eval_words = sorted(set(w for a, b, _ in mP + mS for w in (a, b)))
    defs = json.load(open(DEF_CACHE, encoding="utf-8"))
    has_use = load_units(CELL_DIR)[unit_key("COVERAGE", "v1.1", "full")]["has_use"]
    keep = [i for i in range(len(mP))
            if all((w in defs and defs[w]) and has_use.get(w, False)
                   for w in (mP[i][0], mP[i][1], mS[i][0], mS[i][1]))]
    Pk = [mP[i] for i in keep]
    Sk = [mS[i] for i in keep]
    assert len(Pk) == 202, "population reconstruction MISMATCH (%d != 202) -- VOID" % len(Pk)
    anchor_ok = set(a for a, ok in zip(anchors, mat_ok) if ok)
    fit_words = sorted(set(sorted(set(defs) & anchor_ok)) - set(eval_words))
    assert len(fit_words) == 3064, "fit-word reconstruction MISMATCH (%d != 3064) -- VOID" \
        % len(fit_words)
    words = list(fit_words) + list(eval_words)
    X = l2n(mat[np.array([pos_idx[w] for w in words])]).astype(np.float64)
    return words, X, len(fit_words), Pk, Sk


def main() -> int:
    words, X, n_fit, Pk, Sk = surviving_population()
    print("[population] 242 -> %d rows; fit_words=%d" % (len(Pk), n_fit), flush=True)

    def auc_of_matrix(M):
        st = {w: M[i] for i, w in enumerate(words)}
        return DISS.auc_of(DISS.dense_scores_from_dict_store(st, Pk),
                           DISS.dense_scores_from_dict_store(st, Sk))

    raw = auc_of_matrix(l2n(X))
    print("[check] incumbent store, full rank 256: AUC=%.4f "
          "(MEASURED@data/exp_crossview_convergence_hub_v1/metrics.json:"
          "report.AUC_PER_ARM.A_INCUMBENT_STORE.auc = 0.0603)" % raw, flush=True)

    mx = X[:n_fit].mean(axis=0)
    Xc = X - mx
    print("[check] CENTERING ALONE, full rank 256: AUC=%.4f -- centering is not the effect"
          % auc_of_matrix(l2n(Xc)), flush=True)

    rng = np.random.default_rng(SEED + 99)
    d = X.shape[1]
    print("\n--- RANK-MATCHED NULL: random k-dim projection, NO second channel anywhere ---",
          flush=True)
    for k in RANKS:
        a = []
        for _ in range(N_REP):
            Qo, _ = np.linalg.qr(rng.standard_normal((d, k)))
            a.append(auc_of_matrix(l2n(Xc @ Qo)))
        a = np.asarray(a)
        print("[null] k=%3d  AUC mean=%.4f sd=%.4f  p05=%.4f p95=%.4f"
              % (k, a.mean(), a.std(ddof=1), np.percentile(a, 5), np.percentile(a, 95)), flush=True)

    # --- PIPELINE-MATCHED: identical whitening + rho weights, RANDOM directions ----------------
    Xcf = X[:n_fit] - mx
    Sxx = (Xcf.T @ Xcf) / max(1, n_fit - 1)
    Sxx = Sxx + LAM_REL * (np.trace(Sxx) / Sxx.shape[0]) * np.eye(Sxx.shape[0])
    w, Q = np.linalg.eigh(0.5 * (Sxx + Sxx.T))
    w = np.maximum(w, 1e-10 * float(w.max()))
    Wx = (Q * (w ** -0.5)) @ Q.T

    a_x, a_both = [], []
    for _ in range(N_REP):
        Qo, _ = np.linalg.qr(rng.standard_normal((d, K_STAR)))
        U = l2n((Xc @ (Wx @ Qo)) * RHO)
        a_x.append(auc_of_matrix(U))
        V = l2n(rng.standard_normal((X.shape[0], K_STAR)))     # information-free second addend
        a_both.append(auc_of_matrix(l2n(U + V)))
    print("\n--- PIPELINE-MATCHED NULL: same whitening, same rho, same k*=8, RANDOM directions ---",
          flush=True)
    for nm, arr, real in (("vs HUB_CCA_X       (landed 0.2458)", a_x, 0.2458),
                          ("vs HUB_CCA_BOTH    (landed 0.3129)", a_both, 0.3129)):
        a = np.asarray(arr)
        print("[null] %-36s mean=%.4f sd=%.4f p05=%.4f p95=%.4f | frac(null >= landed arm)=%.3f"
              % (nm, a.mean(), a.std(ddof=1), np.percentile(a, 5), np.percentile(a, 95),
                 float((a >= real).mean())), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
