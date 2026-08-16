"""TIE CONVENTIONS BOTH WAYS for the arms this cell actually quotes.

The standing discipline is that a tie convention is never picked silently, because a floor can hold
large tie mass while the treatment holds none (the top-50 spelling comparison flipped from
+0.0105 NOT_SEPARATED to +0.0641 ABOVE on exactly that). The main cell reports hit_exp only, which
is the tie-AWARE expectation and the right primary, but the optimistic and conservative columns and
the tie mass have to be visible beside it. This probe recomputes all three, plus tie mass, for the
five store variants the report quotes, on all three instruments.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402

import tools.floor_battery as FB  # noqa: E402
import experiments.exp_synonym_clumping_consolidation_v1 as C  # noqa: E402

OUT = os.path.join(_REPO, "scratch", "synonym_clumping")
os.makedirs(OUT, exist_ok=True)


def main() -> int:
    D = C.load_all()
    INS = C.Instruments(D)
    base = D["mat"]
    Vth, _ok, _st = C.build_thematic_vectors(D["anchors"], D["pos"])

    variants = {}
    variants["REAL_STORE_rho0"] = C.l2n(base)
    for m in (5, 20):
        idx, w, dead = C.thematic_neighbourhood(Vth, m, 3.0, "second_order", C.MASTER_SEED + 71,
                                                D["fq"])
        variants["M4_THEMATIC_SECOND_ORDER_eta0.50_m%d" % m] = C.m4_replay_from_neighbourhood(
            base, idx, w, dead, 0.5, 1)
    idx, w, dead = C.thematic_neighbourhood(Vth, 5, 3.0, "shuffled", C.MASTER_SEED + 71, D["fq"])
    variants["C_THEM_SHUFFLED_PROFILES_m5_eta0.50"] = C.m4_replay_from_neighbourhood(
        base, idx, w, dead, 0.5, 1)
    variants["C_ISO_GLOBAL_CENTROID_beta0.50"] = C.c_iso_collapse(base, 0.5)
    variants["ORACLE_SYNONYM_CENTROID_rho0.30"] = C.oracle_synonym_shrink(base, D["syn"], 0.30)

    def three(S, elig, gold, mask, name):
        r = FB.hit_at_1_both_tie_conventions(S, elig, gold)
        rk = FB.rank_of_best_gold(S, elig, gold)
        return {"hit_exp_PRIMARY": round(float(np.mean(np.asarray(r["hit_exp"])[mask])), 4),
                "hit_optimistic": round(float(np.mean(np.asarray(r["hit_opt"])[mask])), 4),
                "hit_conservative": round(float(np.mean(np.asarray(r["hit_cons"])[mask])), 4),
                "mean_tie_mass_of_the_pool": round(
                    float(np.mean(np.asarray(r["tie_mass"])[mask])), 4),
                "top50_optimistic": round(float(np.mean(
                    np.asarray(rk["rank_opt"])[mask] <= 50)), 4),
                "top50_conservative": round(float(np.mean(
                    np.asarray(rk["rank_cons"])[mask] <= 50)), 4),
                "_arm": name}

    rep = {"why": __doc__.strip().splitlines()[0],
           "n_items_A2_population": int(INS.maskA2.sum()), "n_items_full": int(INS.n_i),
           "arms": {}}
    allT = np.ones(INS.n_i, dtype=bool)
    for nm, S in variants.items():
        Qsem = INS.semantic_cue(S)
        rep["arms"][nm] = {
            "A2_gated_semantic_channel": three(INS.score(S, Qsem), INS.gate, INS.goldA,
                                               INS.maskA2, "A2"),
            "A1_sentence_cue_full_pool": three(INS.score(S, D["Q_part"][INS.rows]), INS.eligA,
                                               INS.goldA, allT, "A1"),
            "B_exact_key_open_vocabulary": three(INS.score(S, D["Q_exact"][INS.rows]), INS.eligB,
                                                 INS.goldB, INS.maskA2 & INS.has_goldB, "B"),
        }
        print(nm, json.dumps(rep["arms"][nm]), flush=True)

    # THE FLOORS TOO -- a floor's tie mass is exactly what makes a convention flattering.
    rep["FLOORS_on_instrument_B"] = {
        "F1_TRIGRAM_ONLY": three((D["t_mat"] @ D["Tq"][INS.rows].T).astype(np.float32),
                                 INS.eligB, INS.goldB, INS.maskA2 & INS.has_goldB, "F1"),
        "F2_PREFIX_ONLY": three(D["Pq"][INS.rows].T.astype(np.float32), INS.eligB, INS.goldB,
                                INS.maskA2 & INS.has_goldB, "F2"),
        "F4_CONSTANT_PROTOTYPE": three(
            np.repeat(FB.constant_prototype_floor(base, INS.mat_ok)[:, None], INS.n_i,
                      axis=1).astype(np.float32), INS.eligB, INS.goldB,
            INS.maskA2 & INS.has_goldB, "F4"),
    }
    rep["FLOORS_on_instrument_A2"] = {
        "F_RANDOM_WITHIN_GATE": three(
            np.random.default_rng(C.MASTER_SEED + 9).random((INS.n_a, INS.n_i)).astype(np.float32),
            INS.gate, INS.goldA, INS.maskA2, "Frand"),
        "F_CONSTANT_PROTOTYPE": three(
            np.repeat(FB.constant_prototype_floor(base, INS.mat_ok)[:, None], INS.n_i,
                      axis=1).astype(np.float32), INS.gate, INS.goldA, INS.maskA2, "Fconst"),
    }
    p = os.path.join(OUT, "tie_conventions.json")
    with open(p + ".tmp", "w", encoding="ascii") as fh:
        json.dump(rep, fh, indent=1)
    os.replace(p + ".tmp", p)
    print("wrote", p, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
