"""u1_fb15k237_ingest_eval_v1 -- U1: certify the substrate KB-INGEST of real FB15k-237 (50k triples).

Per Skunkworks U1 bands (b9e4485f): the cert is the INGEST, not the LM. Load-bearing =
(1) REFUSE-GATE (fact-fab-bound = the genuine KG value), (2) INFERENCE-TRANSFER vs frozen-encoder
single-hop (heldout_in_compose_graph==0), (3) RETRIEVAL-AT-SCALE M=50k. FIDELITY (exact recall) =
report-floor (perfect-by-construction), NOT a cert-bar.

THIS FILE = the UNAMBIGUOUS scaffold (load + cfrpe ingest + fidelity-floor + scale-curve), RUNNABLE
now. The two load-bearing mechanisms (refuse-gate + inference-transfer) are STUBBED pending
Skunkworks SCHEMA-VET of OPEN-A..D (note exp_dev_to_skunkworks_U1_ingest_cell_DESIGN_2026-06-21).
On VET -> fill the stubs + flip to a real cert. ASCII only; CPU.
"""
import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
ANCHOR_NAME = "u1_fb15k237_ingest_eval_v1"
KG_PATH = REPO / "data" / "datasets" / "fb15k_237_train_50k.jsonl"
LR = 0.5

# Skunkworks U1 bands (b9e4485f) as named constants (thresholds locked; mechanisms pending VET)
FIDELITY_FLOOR = 0.98          # report-floor: below this the ingest pipeline is BROKEN (NOT a cert-bar)
REFUSE_OOD_MIN = 0.80         # load-bearing #1: OOD (fabricated) refuse-rate >= this
ACCEPT_INKB_MIN = 0.80       # load-bearing #1: in-KB accept-rate >= this (don't over-refuse)
# inference-transfer (#2): substrate-2hop > frozen-encoder-single-hop on held-out; heldout_in_compose_graph==0

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 2048; SCALE_POINTS = [600]; N_EVAL = 150
else:
    SEEDS = [7, 17, 23]; N_DIM = 8192; SCALE_POINTS = [5000, 10000, 25000, 50000]; N_EVAL = 500

CONFIG_VERSION = "u1-ingest-scaffold: cfrpe-VSA-bind; fidelity-floor+scale-curve LIVE; refuse-gate+inference-transfer PENDING-SCHEMA-VET; N%d scale%s LR%.2f" % (
    N_DIM, str(SCALE_POINTS), LR)


def bipolar(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def cfrpe(W, key, val, n):
    """Contrastive-Hebbian outer-product store update (substrate associative core)."""
    W += (LR / n) * np.outer(val - W @ key, key)


def _selftest():
    g = np.random.default_rng(0); n = 256
    E = bipolar(4, n, g); R = bipolar(2, n, g)
    key = E[1] * R[0] * math.sqrt(n)
    W = np.zeros((n, n), dtype=np.float32); cfrpe(W, key, E[2], n)
    assert int(np.argmax(E @ (W @ key))) == 2, "cfrpe triple store+recall"
    # scale-curve sanity: 25 DISTINCT-(s,p)-key triples (distinct subject i) -> no key collision ->
    # cfrpe should recall well. (NOTE: real FB15k-237 has 1-to-many relations = key collisions ->
    # fidelity NOT perfect-by-construction on the multigraph; flagged to Skunkworks for the fidelity band.)
    ne = 30; Es = bipolar(ne, n, g); Rs = bipolar(3, n, g); sq = math.sqrt(n)
    rows = [(i, int(g.integers(0, 3)), int(g.integers(0, ne))) for i in range(25)]  # distinct subject = unique key
    Ws = np.zeros((n, n), dtype=np.float32)
    for (s, p, o) in rows:
        cfrpe(Ws, Es[s] * Rs[p] * sq, Es[o], n)
    hit = sum(int(np.argmax(Es @ (Ws @ (Es[s] * Rs[p] * sq))) == o) for (s, p, o) in rows)
    assert hit >= 20, "distinct-key fidelity sanity (>=20/25); got %d" % hit
    print("[selftest] PASS: cfrpe store + distinct-key fidelity (%d/25 in-KB recall)" % hit, flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def load_kg(seed, m_triples):
    if not KG_PATH.exists():
        raise FileNotFoundError("FB15k-237 not found at %s" % KG_PATH)
    rows = []
    with open(KG_PATH, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line); rows.append((r["subject"], r["predicate"], r["object"]))
    g = np.random.default_rng(seed); g.shuffle(rows); rows = rows[:m_triples]
    ents = sorted({s for s, _, _ in rows} | {o for _, _, o in rows})
    rels = sorted({p for _, p, _ in rows})
    eid = {e: i for i, e in enumerate(ents)}; rid = {p: i for i, p in enumerate(rels)}
    triples = [(eid[s], rid[p], eid[o]) for s, p, o in rows]
    return triples, len(ents), len(rels)


def ingest(triples, n_ent, n_rel, g):
    """Build the substrate KB: bipolar entity/relation codebooks + cfrpe-stored W."""
    E = bipolar(n_ent, N_DIM, g); R = bipolar(n_rel, N_DIM, g); sq = math.sqrt(N_DIM)
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    for (s, p, o) in triples:
        cfrpe(W, E[s] * R[p] * sq, E[o], N_DIM)
    return E, R, W, sq


def fidelity_recall(E, R, W, sq, triples, n_eval, g):
    """Exact in-KB recall (perfect-by-construction floor; REPORT not cert)."""
    idx = g.permutation(len(triples))[:min(n_eval, len(triples))]
    hit = 0
    for i in idx:
        s, p, o = triples[i]
        hit += int(np.argmax(E @ (W @ (E[s] * R[p] * sq))) == o)
    return hit / max(len(idx), 1)


# ============================================================================
# LOAD-BEARING mechanisms -- STUBBED pending Skunkworks SCHEMA-VET (OPEN-A..D).
# Do NOT cert until filled + VET'd. Returning None marks "not yet measured".
# ============================================================================
def refuse_gate(E, R, W, sq, triples, n_ent, n_rel, g):
    """LOAD-BEARING #1 (PENDING-VET OPEN-B): margin-threshold refuse on OOD vs in-KB.
    Proposed: margin = top1_cos - top2_cos; tau calibrated on held split; OOD = in-KB (s,p) with no edge.
    Returns dict(ood_refuse_rate, inkb_accept_rate) once VET'd."""
    return None  # OPEN-B: OOD construction + refuse mechanism pending VET


def inference_transfer(E, R, W, sq, triples, g):
    """LOAD-BEARING #2 (PENDING-VET OPEN-C): substrate-2hop vs frozen-encoder-single-hop on held-out
    (assert heldout_in_compose_graph==0). sentence-transformers 5.5.1 CONFIRMED available for the
    frozen-bge baseline. Returns dict(substrate_acc, frozen_encoder_acc, heldout_in_compose_graph)."""
    return None  # OPEN-C: frozen-encoder baseline + heldout-disjoint construction pending VET


def run_seed(seed):
    g = np.random.default_rng(seed)
    out = {"seed": seed, "scale_curve": {}, "config_version": CONFIG_VERSION}
    # RETRIEVAL-AT-SCALE (load-bearing #3) + FIDELITY floor: ingest at each scale point, measure recall
    for M in SCALE_POINTS:
        triples, n_ent, n_rel = load_kg(seed, M)
        t = time.time()
        E, R, W, sq = ingest(triples, n_ent, n_rel, g)
        fid = fidelity_recall(E, R, W, sq, triples, N_EVAL, np.random.default_rng(seed + 1))
        out["scale_curve"]["M%d" % M] = {"fidelity": round(fid, 4), "n_ent": n_ent, "n_rel": n_rel,
                                          "n_triples": len(triples), "ingest_s": round(time.time() - t, 1)}
        print("  [seed=%d M=%d] fidelity=%.4f (n_ent=%d n_rel=%d, %.1fs)" % (
            seed, M, fid, n_ent, n_rel, time.time() - t), flush=True)
    # largest-scale store for the load-bearing stubs (pending VET)
    triples, n_ent, n_rel = load_kg(seed, max(SCALE_POINTS))
    E, R, W, sq = ingest(triples, n_ent, n_rel, g)
    out["refuse_gate"] = refuse_gate(E, R, W, sq, triples, n_ent, n_rel, g)
    out["inference_transfer"] = inference_transfer(E, R, W, sq, triples, g)
    return out


def verdict(ps) -> Tuple[str, str]:
    big = "M%d" % max(SCALE_POINTS)
    fid_big = float(np.mean([p["scale_curve"][big]["fidelity"] for p in ps]))
    curve = {M: round(float(np.mean([p["scale_curve"]["M%d" % M]["fidelity"] for p in ps])), 4) for M in SCALE_POINTS}
    pending = ps[0]["refuse_gate"] is None or ps[0]["inference_transfer"] is None
    summary = "fidelity@%s=%.4f (floor %.2f) | scale-curve=%s" % (big, fid_big, FIDELITY_FLOOR, curve)
    if pending:
        return ("SCAFFOLD_PENDING_SCHEMA_VET",
                "SCAFFOLD: fidelity-floor + retrieval-at-scale curve LIVE; refuse-gate + inference-transfer "
                "PENDING Skunkworks SCHEMA-VET (OPEN-B/C). " + summary)
    # (post-VET cert logic added once the stubs are filled)
    return ("SCAFFOLD_PENDING_SCHEMA_VET", summary)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d scale=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, SCALE_POINTS, CONFIG_VERSION), flush=True)
    t0 = time.time()
    ps = [run_seed(s) for s in SEEDS]
    v, vmsg = verdict(ps)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
               "n_seeds": len(SEEDS), "config_version": CONFIG_VERSION, "per_seed": ps,
               "elapsed_s": round(time.time() - t0, 1)}
    out_dir = REPO / "data" / ("exp_%s" % ANCHOR_NAME); out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
