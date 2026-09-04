"""exp_prediction_error_graded_boundary_salience_v1 -- Direction B (fidelity frontier).

The real N400 is GRADED: a strong event shift produces a large N400, a subtle shift a small one
(Kutas & Federmeier). The main cell's boundaries were all clean near-orthogonal jumps, where ANY
content-referenced predictor wins and predictor sophistication does not matter. This cell makes
boundary STRENGTH graded and asks two brain-fidelity questions the main cell could not:

  Q1 (GRADED SIGNAL): does the prediction-error magnitude at a true boundary TRACK the boundary's
     semantic strength? (Spearman(e_at_boundary, gap).) A faithful N400 must be graded, not a flag.
  Q2 (WEAK BOUNDARIES): at WEAK boundaries -- where the strong-jump advantage disappears -- does a
     genuine forward predictor beat the running MEAN? MEAN (persistence prior), LAST (1st-order),
     LEARNED (online Rao-Ballard delta-rule transition map). This is the regime that WOULD separate
     them if the running mean were a mere convenience.

STIMULUS: K events; consecutive event topics separated by a per-boundary GAP g in [0.12, 1.0]:
  topic_ev = normalize(sqrt(1-g)*topic_{ev-1} + sqrt(g)*orthogonal)   (g=1 orthogonal, g->0 subtle).
Within-event context = normalize(topic + noise*randn). Same downstream DV + real hdlab register.
Detection = a posted boundary within +-TOL of the gold position. Floors: RANDOM_ratematched, PERMUTED.

Deterministic; writes only its own dir. ASCII-only.
Run:  .venv/Scripts/python.exe experiments/exp_prediction_error_graded_boundary_salience_v1.py
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import experiments.exp_prediction_error_event_segmentation_v1 as X
import experiments.exp_prediction_error_forward_predictor_drill_v1 as DR

DATA_DIR = REPO / "data" / "exp_prediction_error_graded_boundary_salience_v1"
EPS = 1e-9
GAP_LO, GAP_HI = 0.12, 1.0
TOL = 1  # a boundary counts as detected if posted within +-TOL positions of the gold boundary


def gen_stream_graded(seed: int, D: int, noise: float, g: torch.Generator) -> dict:
    role_vecs = torch.stack([X.unit_phase_vec(D, g) for _ in range(X.N_ROLES)])
    filler_cb = torch.stack([X.unit_phase_vec(D, g) for _ in range(X.V_SIZE)])
    # graded topic walk: each event topic is `gap` of the way toward a fresh orthogonal direction
    topics = []
    gaps = []
    t = X.real_unit(X.CTX_DIM, g)
    topics.append(t)
    for _ in range(X.K_EVENTS - 1):
        gap = float(torch.empty(1).uniform_(GAP_LO, GAP_HI, generator=g).item())
        r = X.real_unit(X.CTX_DIM, g)
        r = r - (r @ t) * t                      # orthogonalise vs current topic
        r = r / (r.norm() + EPS)
        t = math.sqrt(1 - gap) * t + math.sqrt(gap) * r
        t = t / (t.norm() + EPS)
        topics.append(t)
        gaps.append(gap)
    topics = torch.stack(topics)

    roles, fillers, ctx, event_of = [], [], [], []
    gold_boundaries = {}   # position -> gap strength
    pos = 0
    for ev in range(X.K_EVENTS):
        elen = int(torch.randint(X.EVT_LEN_MIN, X.EVT_LEN_MAX + 1, (1,), generator=g).item())
        role_perm = torch.randperm(X.N_ROLES, generator=g)[:elen].tolist()
        for j, r in enumerate(role_perm):
            if pos > 0 and j == 0:
                gold_boundaries[pos] = gaps[ev - 1]
            roles.append(int(r))
            fillers.append(int(torch.randint(0, X.V_SIZE, (1,), generator=g).item()))
            c = topics[ev] + noise * torch.randn(X.CTX_DIM, generator=g) / math.sqrt(X.CTX_DIM)
            ctx.append(c / (c.norm() + EPS))
            event_of.append(ev)
            pos += 1
    return {"N": pos, "roles": roles, "fillers": fillers, "ctx": torch.stack(ctx),
            "event_of": event_of, "gold_boundaries": set(gold_boundaries.keys()),
            "gold_strengths": gold_boundaries, "role_vecs": role_vecs, "filler_cb": filler_cb, "D": D}


def _detected(pred_b: set, gold_pos: int) -> bool:
    return any(abs(p - gold_pos) <= TOL for p in pred_b)


def main() -> int:
    t0 = time.time()
    X._guard()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    D, noise = 128, 1.0
    seeds, n = X.TEST_SEEDS, 60
    tau = 1.5  # fixed rate-sane threshold (main cell's headline value); reported, not tuned here

    # accumulators
    e_by_gap = {p: [] for p in DR.PRED_ARMS}      # (gap, e_at_boundary) pairs
    det_by_bin = {p: {"weak": [0, 0], "med": [0, 0], "strong": [0, 0]} for p in DR.PRED_ARMS}
    dv = {a: [] for a in ["MEAN", "LAST", "LEARNED", "RANDOM_ratematched", "PERMUTED_SURPRISE", "ORACLE", "NO_SEG"]}

    def gbin(g):
        return "weak" if g < 0.4 else ("med" if g < 0.75 else "strong")

    for seed in seeds:
        for si in range(n):
            g = X.gen(seed * 1_000_003 + si * 9176 + 777)
            st = gen_stream_graded(seed, D, noise, g)
            N = st["N"]
            gold = st["gold_boundaries"]
            strengths = st["gold_strengths"]
            segs = {}
            es = {}
            for p in DR.PRED_ARMS:
                seg, b, e_series = DR.seg_predictor(st["ctx"], tau, p)
                segs[p] = (seg, b)
                es[p] = e_series
                for gp, gval in strengths.items():
                    e_by_gap[p].append((gval, e_series[gp]))
                    b_bin = gbin(gval)
                    det_by_bin[p][b_bin][0] += int(_detected(b, gp))
                    det_by_bin[p][b_bin][1] += 1
            # DV
            named = {
                "MEAN": segs["mean"][0], "LAST": segs["last"][0], "LEARNED": segs["learned"][0],
                "ORACLE": X._seg_from_boundaries(N, gold),
                "NO_SEG": [0] * N,
                "RANDOM_ratematched": X.seg_random_ratematched(N, len(segs["mean"][1]), X.gen(seed * 7 + si * 13 + 3))[0],
                "PERMUTED_SURPRISE": X.seg_permuted_surprise(es["mean"], tau, X.gen(seed * 17 + si * 3 + 9))[0],
            }
            for a, seg in named.items():
                ok, tot = X.score_dv(seg, st)
                dv[a].append((ok, tot))

    # Q1: graded signal -- Spearman(e, gap) per arm
    def spearman(pairs):
        if len(pairs) < 3:
            return float("nan")
        a = np.array([p[0] for p in pairs]); b = np.array([p[1] for p in pairs])
        ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
        return float(np.corrcoef(ra, rb)[0, 1])

    q1 = {p: {"spearman_e_vs_gap": spearman(e_by_gap[p]), "n": len(e_by_gap[p])} for p in DR.PRED_ARMS}
    # Q2: detection recall by strength bin
    q2 = {p: {b: (det_by_bin[p][b][0] / det_by_bin[p][b][1] if det_by_bin[p][b][1] else float("nan"))
              for b in ("weak", "med", "strong")} for p in DR.PRED_ARMS}
    dv_ci = {a: X.bootstrap_stream_ci(dv[a], seed=hash(a) & 0xFFFF) for a in dv}

    print("Q1 GRADED SIGNAL -- Spearman(prediction-error, boundary gap):")
    for p in DR.PRED_ARMS:
        print(f"    {p:8s} rho={q1[p]['spearman_e_vs_gap']:.3f} (n={q1[p]['n']})")
    print("Q2 DETECTION RECALL by boundary strength (weak<0.4 / med / strong>=0.75):")
    for p in DR.PRED_ARMS:
        print(f"    {p:8s} weak={q2[p]['weak']:.3f} med={q2[p]['med']:.3f} strong={q2[p]['strong']:.3f}")
    print("DV (downstream recovery):")
    for a in ["ORACLE", "MEAN", "LAST", "LEARNED", "RANDOM_ratematched", "PERMUTED_SURPRISE", "NO_SEG"]:
        c = dv_ci[a]
        print(f"    {a:20s} {c['acc']:.3f} [{c['lo']:.3f},{c['hi']:.3f}]")

    payload = {"cell": "exp_prediction_error_graded_boundary_salience_v1",
               "elapsed_s": round(time.time() - t0, 2), "D": D, "noise": noise, "tau": tau,
               "TOL": TOL, "GAP_RANGE": [GAP_LO, GAP_HI], "n_streams": len(seeds) * n,
               "Q1_spearman_e_vs_gap": q1, "Q2_detection_recall_by_strength": q2, "DV": dv_ci}
    tmp = DATA_DIR / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
    os.replace(tmp, DATA_DIR / "metrics.json")
    print(f"wrote {DATA_DIR / 'metrics.json'}  elapsed={payload['elapsed_s']}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
