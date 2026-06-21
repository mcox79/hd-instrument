"""u1_fb15k237_ingest_eval_v1 -- U1: certify the substrate KB-INGEST of real FB15k-237 (50k triples).

Per Skunkworks U1 bands (b9e4485f): the cert is the INGEST, not the LM. Load-bearing =
(1) REFUSE-GATE (fact-fab-bound = the genuine KG value), (2) INFERENCE-TRANSFER (composition beyond
single-hop lookup; heldout_in_compose_graph==0), (3) RETRIEVAL-AT-SCALE M=50k. FIDELITY = report-floor.

MECHANISM = my SCHEMA-VET design (exp_dev_to_skunkworks_U1_*), de-risked (OPEN-E 8f26a6b7):
  - MULTI-VALUE Hebbian-accumulate store W += outer(E[o], key)/N (key = E[s]*R[p]*sqrt(N)); set-readout
    top-k (k = |objects(s,p)|). Faithful to the multigraph (25.8%% of (s,p) keys are 1-to-many, max 160).
  - REFUSE-GATE: confidence = top-1 score; tau calibrated on a held split to max balanced (in-KB-accept,
    OOD-refuse); OOD = (s,p) with s,p in-KB but NO edge (realistic fabrication).
  - INFERENCE-TRANSFER: held-out 2-hop (s,p1,x)+(x,p2,o), assert (s,*,o) NOT a direct train edge
    (heldout_in_compose_graph==0); substrate 2-hop traverse vs 1-hop-lookup baseline (composition test).
    NOTE OPEN-C: frozen-encoder-readable baseline DEFERRED -- FB15k-237 entities are MIDs (/m/027rn),
    not readable, so a frozen sentence-encoder is meaningless here; the 1-hop-lookup baseline is the
    MID-valid composition bar. Flag for Skunkworks: stage entity-names to add the frozen-encoder bar.

Thresholds = Skunkworks's locked bands; mechanism = my de-risked design (pending VET-refinement).
CPU; ASCII; checkpoint via CONFIG_VERSION-all-params.
"""
import argparse
import json
import math
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
ANCHOR_NAME = "u1_fb15k237_ingest_eval_v1"
KG_PATH = REPO / "data" / "datasets" / "fb15k_237_train_50k.jsonl"

# Skunkworks U1 bands (b9e4485f) -- locked thresholds
FIDELITY_FLOOR = 0.95         # report-floor for the 1-to-1 subset set-recall (pipeline-sanity, NOT cert)
REFUSE_OOD_MIN = 0.80         # load-bearing #1: OOD (fabricated) refuse-rate >= this
ACCEPT_INKB_MIN = 0.80       # load-bearing #1: in-KB accept-rate >= this (don't over-refuse)
# inference-transfer (#2): substrate-2hop > 1-hop-lookup baseline on held-out (heldout_in_compose_graph==0)

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 2048; SCALE_POINTS = [600]; N_EVAL = 150; N_OOD = 150; N_2HOP = 100
else:
    SEEDS = [7, 17, 23]; N_DIM = 8192; SCALE_POINTS = [5000, 10000, 25000, 50000]; N_EVAL = 600; N_OOD = 600; N_2HOP = 400

CONFIG_VERSION = ("u1-ingest-multivalue-hebbian: setreadout-topk + margin-refuse + 2hop-vs-1hop-inference; "
                  "N%d scale%s; bands fid%.2f ood%.2f acc%.2f" % (N_DIM, str(SCALE_POINTS), FIDELITY_FLOOR, REFUSE_OOD_MIN, ACCEPT_INKB_MIN))


def bipolar(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); n = 512; ne = 40
    E = bipolar(ne, n, g); R = bipolar(4, n, g); sq = math.sqrt(n)
    # multi-value Hebbian store: 20 keys, some 1-to-many
    keyobjs = {}
    for i in range(20):
        s = i; p = int(g.integers(0, 4)); K = int(g.integers(1, 4))
        keyobjs[(s, p)] = list(g.choice(ne, K, replace=False))
    W = np.zeros((n, n), dtype=np.float32)
    for (s, p), objs in keyobjs.items():
        key = E[s] * R[p] * sq
        for o in objs:
            W += np.outer(E[o], key) / n
    # set-recall@k
    hit = 0; tot = 0
    for (s, p), objs in keyobjs.items():
        scores = E @ (W @ (E[s] * R[p] * sq)); topk = set(np.argsort(scores)[-len(objs):].tolist())
        hit += len(topk & set(objs)); tot += len(objs)
    assert hit / tot >= 0.9, "multi-value set-recall@k sanity (got %.2f)" % (hit / tot)
    # refuse confidence: in-KB top1 > OOD top1
    inkb = float(np.max(E @ (W @ (E[0] * R[keyobjs and list(keyobjs)[0][1] or 0] * sq))))
    ood_s, ood_p = 5, 3
    while (ood_s, ood_p) in keyobjs:
        ood_p = (ood_p + 1) % 4
    ood = float(np.max(E @ (W @ (E[ood_s] * R[ood_p] * sq))))
    assert inkb > ood, "refuse confidence: in-KB(%.3f) > OOD(%.3f)" % (inkb, ood)
    print("[selftest] PASS: multi-value set-recall=%.2f; refuse-conf in-KB %.3f > OOD %.3f" % (hit / tot, inkb, ood), flush=True)


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
    keyobjs = defaultdict(set)
    for (s, p, o) in triples:
        keyobjs[(s, p)].add(o)
    return triples, {k: sorted(v) for k, v in keyobjs.items()}, len(ents), len(rels)


def ingest_hebbian(triples, n_ent, n_rel, g, batch=5000):
    """MULTI-VALUE Hebbian-accumulate KB: W = sum_i outer(E[o_i], key_i)/N. Sets superpose per key.
    Vectorized as a chunked BLAS matmul (W += O_chunk.T @ keys_chunk) -- ~minutes not hours at M=50k."""
    E = bipolar(n_ent, N_DIM, g); R = bipolar(n_rel, N_DIM, g); sq = math.sqrt(N_DIM)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)  # (B, N)
        W += (E[o_idx[b:b + batch]].T @ ks) / N_DIM                                    # (N, N) BLAS
    return E, R, W, sq


def set_recall_at_k(E, R, W, sq, keyobjs, n_eval, g, restrict_1to1=False):
    """For each (s,p) with K objects, top-K(key) set-overlap with the true objects."""
    keys = list(keyobjs.items())
    if restrict_1to1:
        keys = [(k, v) for k, v in keys if len(v) == 1]
    if not keys:
        return 0.0
    idx = g.permutation(len(keys))[:min(n_eval, len(keys))]
    tot = 0.0
    for i in idx:
        (s, p), objs = keys[i]; k = len(objs)
        scores = E @ (W @ (E[s] * R[p] * sq))
        topk = set(np.argpartition(scores, -k)[-k:].tolist())
        tot += len(topk & set(objs)) / k
    return tot / max(len(idx), 1)


def refuse_gate(E, R, W, sq, keyobjs, n_ent, n_rel, n_q, g):
    """confidence = top-1 score; tau calibrated on a held split to max balanced(in-KB-accept, OOD-refuse).
    OOD = (s,p) with s,p in-KB but NO edge (realistic fabrication)."""
    inkb_keys = list(keyobjs.keys())
    conf = lambda s, p: float(np.max(E @ (W @ (E[s] * R[p] * sq))))
    # in-KB confidences
    idx = g.permutation(len(inkb_keys))[:min(n_q, len(inkb_keys))]
    inkb_conf = np.array([conf(*inkb_keys[i]) for i in idx])
    # OOD (no-edge) confidences
    keyset = set(keyobjs.keys()); ood_conf = []
    tries = 0
    while len(ood_conf) < n_q and tries < n_q * 50:
        s = int(g.integers(0, n_ent)); p = int(g.integers(0, n_rel)); tries += 1
        if (s, p) in keyset:
            continue
        ood_conf.append(conf(s, p))
    ood_conf = np.array(ood_conf)
    # calibrate tau on first half, evaluate on second half (held split)
    h = len(inkb_conf) // 2; ho = len(ood_conf) // 2
    cal_in, ev_in = inkb_conf[:h], inkb_conf[h:]; cal_ood, ev_ood = ood_conf[:ho], ood_conf[ho:]
    cands = np.unique(np.concatenate([cal_in, cal_ood]))
    best_tau, best_bal = cands[0], -1.0
    for tau in cands:
        acc = float((cal_in >= tau).mean()); ref = float((cal_ood < tau).mean())
        bal = 0.5 * (acc + ref)
        if bal > best_bal:
            best_bal, best_tau = bal, float(tau)
    return {"tau": best_tau, "inkb_accept": float((ev_in >= best_tau).mean()),
            "ood_refuse": float((ev_ood < best_tau).mean()),
            "inkb_conf_mean": float(inkb_conf.mean()), "ood_conf_mean": float(ood_conf.mean())}


def inference_transfer(E, R, W, sq, triples, keyobjs, n_2hop, g):
    """Held-out 2-hop (s,p1,x)+(x,p2,o); assert (s,*,o) NOT a direct train edge (heldout_in_compose_graph==0).
    Substrate 2-hop traverse vs 1-hop-lookup baseline (composition test). recall1 = argmax single object."""
    adj = defaultdict(list)
    for (s, p), objs in keyobjs.items():
        for o in objs:
            adj[s].append((p, o))
    direct = set((s, o) for (s, p, o) in triples)  # any direct s->o edge (for the leakage assert)
    def recall1(s, p):
        return int(np.argmax(E @ (W @ (E[s] * R[p] * sq))))
    chains = []
    starts = [s for s in adj if adj[s]]
    tries = 0
    leak = 0
    while len(chains) < n_2hop and tries < n_2hop * 80:
        tries += 1
        s = int(g.choice(starts))
        p1, x = adj[s][int(g.integers(0, len(adj[s])))]
        if x not in adj or not adj[x]:
            continue
        p2, o = adj[x][int(g.integers(0, len(adj[x])))]
        if o == s:
            continue
        if (s, o) in direct:
            leak += 1; continue  # heldout_in_compose_graph guard: skip if (s,o) is a DIRECT train edge
        chains.append((s, p1, x, p2, o))
    if not chains:
        return {"n": 0}
    sub2 = base1 = 0
    for (s, p1, x, p2, o) in chains:
        x_hat = recall1(s, p1); o_hat = recall1(x_hat, p2)
        sub2 += int(o_hat == o)
        # 1-hop-lookup baseline (composition-blind): can a single hop from s reach o?
        base1 += int(recall1(s, p1) == o or recall1(s, p2) == o)
    n = len(chains)
    return {"n": n, "substrate_2hop": sub2 / n, "baseline_1hop": base1 / n,
            "heldout_in_compose_graph": 0, "leak_skipped": leak}


def run_seed(seed):
    g = np.random.default_rng(seed)
    out = {"seed": seed, "scale_curve": {}, "config_version": CONFIG_VERSION}
    # RETRIEVAL-AT-SCALE (#3) + FIDELITY floor (set-recall@k; 1-to-1 subset separately)
    for M in SCALE_POINTS:
        triples, keyobjs, n_ent, n_rel = load_kg(seed, M)
        t = time.time()
        E, R, W, sq = ingest_hebbian(triples, n_ent, n_rel, g)
        fid_all = set_recall_at_k(E, R, W, sq, keyobjs, N_EVAL, np.random.default_rng(seed + 1))
        fid_11 = set_recall_at_k(E, R, W, sq, keyobjs, N_EVAL, np.random.default_rng(seed + 2), restrict_1to1=True)
        out["scale_curve"]["M%d" % M] = {"setrecall_all": round(fid_all, 4), "setrecall_1to1": round(fid_11, 4),
                                          "n_ent": n_ent, "n_rel": n_rel, "n_keys": len(keyobjs),
                                          "n_triples": len(triples), "ingest_s": round(time.time() - t, 1)}
        print("  [seed=%d M=%d] setrecall all=%.4f 1to1=%.4f (n_ent=%d keys=%d, %.1fs)" % (
            seed, M, fid_all, fid_11, n_ent, len(keyobjs), time.time() - t), flush=True)
    # LOAD-BEARING #1 + #2 at the largest scale
    triples, keyobjs, n_ent, n_rel = load_kg(seed, max(SCALE_POINTS))
    E, R, W, sq = ingest_hebbian(triples, n_ent, n_rel, g)
    out["refuse_gate"] = refuse_gate(E, R, W, sq, keyobjs, n_ent, n_rel, N_OOD, np.random.default_rng(seed + 3))
    out["inference_transfer"] = inference_transfer(E, R, W, sq, triples, keyobjs, N_2HOP, np.random.default_rng(seed + 4))
    print("  [seed=%d] refuse: ood=%.3f accept=%.3f (tau=%.3f) | infer: 2hop=%.3f vs 1hop-base=%.3f (n=%d)" % (
        seed, out["refuse_gate"]["ood_refuse"], out["refuse_gate"]["inkb_accept"], out["refuse_gate"]["tau"],
        out["inference_transfer"].get("substrate_2hop", 0), out["inference_transfer"].get("baseline_1hop", 0),
        out["inference_transfer"].get("n", 0)), flush=True)
    return out


def verdict(ps) -> Tuple[str, str]:
    big = "M%d" % max(SCALE_POINTS)
    fid11 = float(np.mean([p["scale_curve"][big]["setrecall_1to1"] for p in ps]))
    fidall = float(np.mean([p["scale_curve"][big]["setrecall_all"] for p in ps]))
    ood = float(np.mean([p["refuse_gate"]["ood_refuse"] for p in ps]))
    acc = float(np.mean([p["refuse_gate"]["inkb_accept"] for p in ps]))
    s2 = float(np.mean([p["inference_transfer"].get("substrate_2hop", 0) for p in ps]))
    b1 = float(np.mean([p["inference_transfer"].get("baseline_1hop", 0) for p in ps]))
    curve = {M: round(float(np.mean([p["scale_curve"]["M%d" % M]["setrecall_all"] for p in ps])), 3) for M in SCALE_POINTS}
    summ = ("fidelity@%s set-recall all=%.3f 1to1=%.3f (floor %.2f) | refuse OOD=%.3f accept=%.3f (>=%.2f) | "
            "inference 2hop=%.3f vs 1hop-base=%.3f | scale-curve=%s" % (
                big, fidall, fid11, FIDELITY_FLOOR, ood, acc, REFUSE_OOD_MIN, s2, b1, curve))
    refuse_pass = ood >= REFUSE_OOD_MIN and acc >= ACCEPT_INKB_MIN
    infer_pass = s2 > b1 + 0.02
    if refuse_pass and infer_pass:
        return ("HARD_PASS", "HARD_PASS: substrate KB-ingest GOVERNED (refuse-gate) + COMPOSES (inference-transfer). " + summ)
    if refuse_pass or infer_pass:
        return ("MIDDLE_BAND", "MIDDLE_BAND: one load-bearing holds. " + summ)
    return ("HARD_FAIL", "HARD_FAIL: refuse-gate + inference-transfer both fall short. " + summ)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d scale=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, SCALE_POINTS, CONFIG_VERSION), flush=True)
    t0 = time.time()
    ps = [run_seed(s) for s in SEEDS]
    v, vmsg = verdict(ps)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
               "n_seeds": len(SEEDS), "config_version": CONFIG_VERSION, "per_seed": ps,
               "elapsed_s": round(time.time() - t0, 1),
               "DESIGN_NOTE": "mechanism per exp_dev U1 SCHEMA-VET (de-risked OPEN-E); thresholds=Skunkworks b9e4485f; "
                              "OPEN-C frozen-encoder baseline DEFERRED (MIDs not readable) -> 1-hop-lookup is the MID-valid bar; pending Skunkworks VET-refinement"}
    out_dir = REPO / "data" / ("exp_%s" % ANCHOR_NAME); out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
