"""n8_conceptnet_ingest_eval_v1 -- N8: certify substrate KB-INGEST of ConceptNet English 100k.

Mirrors U1 (FB15k-237) HARD_PASS pattern: multi-value Hebbian-accumulate + set-readout-top-k +
held-split refuse-gate + 2-hop inference-transfer. ConceptNet entities are READABLE English
(e.g. cat / mammal / locate / kitchen), so we ADD what U1 deferred (OPEN-C):
a frozen-encoder (sentence-transformers MiniLM-L6) semantic baseline for inference-transfer.

Load-bearing dimensions per U1 SCHEMA-VET pattern + the OPEN-C unlock:
  (1) RETRIEVAL-AT-SCALE M = {5k, 10k, 25k, 50k} -> 100k scale-curve;
  (2) REFUSE-GATE: fact-fab-bound (held-split tau; OOD = (s,p) with s,p in-KB but no edge);
  (3) INFERENCE-TRANSFER: 2-hop composition (s,p1,x)+(x,p2,o) NOT direct train edge;
      baselines = 1-hop-lookup (MID-valid analog) AND frozen-encoder semantic (OPEN-C UNLOCK).

Pre-reg bands (skunkworks-style; mirrors U1 absolute-floor framing):
  HARD_PASS: set-recall_all@M_max >= 0.95 AND refuse OOD_refuse >= 0.80 AND in-KB-accept >= 0.80
             AND substrate_2hop > 1-hop-baseline + 0.02 AND substrate_2hop >= 2x frozen-enc baseline.
  MIDDLE_BAND: partial -- one of refuse-gate / inference-transfer holds; the other falls short.
  HARD_FAIL: set-recall_all@M_max < 0.85 OR refuse-gate fails (either side < 0.80) OR
             substrate_2hop <= 1-hop-baseline + 0.02 (no genuine composition gain).

Honest scope upfront:
  - ConceptNet has 8 relation types (vs FB15k-237's ~237) -> rare-relation heldout class is N/A;
    OOD class = in-KB (s,p) with no edge (same as U1; remains realistic fabrication).
  - 1-to-many keys = 24.8% (max K = 1239); pattern faithfulness via set-readout-top-k.
  - Frozen-encoder cost: MiniLM-L6 (~22M params) at INGEST time, only once over n_ent (<= 80k); CPU-cheap.
  - License: ConceptNet 5.7 = CC-BY-SA 4.0 + ODC-BY 4.0 (cached locally as conceptnet5_en_100k.jsonl).

CPU; ASCII; per-seed CONFIG_VERSION-gated checkpoint via _seed_checkpoint helper pattern.
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
ANCHOR_NAME = "n8_conceptnet_ingest_eval_v1"
KG_PATH = REPO / "data" / "datasets" / "conceptnet5_en_100k.jsonl"

# Pre-reg bands (locked; mirrors U1 absolute-floor framing)
SETRECALL_FLOOR = 0.95        # load-bearing #1 component (set-recall@k at M_max)
REFUSE_OOD_MIN = 0.80         # load-bearing #2: OOD refuse-rate >= this
ACCEPT_INKB_MIN = 0.80        # load-bearing #2: in-KB accept-rate >= this (don't over-refuse)
INFER_MARGIN_OVER_1HOP = 0.02 # load-bearing #3a: substrate-2hop > 1-hop + 0.02
INFER_RATIO_OVER_ENC = 2.0    # load-bearing #3b: substrate-2hop >= 2x frozen-encoder semantic (OPEN-C)
SETRECALL_FAIL = 0.85         # HARD_FAIL floor

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [1]; N_DIM = 2048; SCALE_POINTS = [5000]; N_EVAL = 150; N_OOD = 150; N_2HOP = 100
    ENC_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
else:
    SEEDS = [7, 17, 23]; N_DIM = 8192; SCALE_POINTS = [5000, 10000, 25000, 50000, 100000]
    N_EVAL = 600; N_OOD = 600; N_2HOP = 400
    ENC_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CONFIG_VERSION = ("n8-conceptnet-ingest-multivalue-hebbian: setreadout-topk + margin-refuse + "
                  "2hop-vs-1hop-and-frozen-encoder; N%d scale%s; bands sr%.2f ood%.2f acc%.2f inf+%.2f enc%.1fx" %
                  (N_DIM, str(SCALE_POINTS), SETRECALL_FLOOR, REFUSE_OOD_MIN, ACCEPT_INKB_MIN,
                   INFER_MARGIN_OVER_1HOP, INFER_RATIO_OVER_ENC))


def bipolar(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _selftest():
    """Mechanism unit-test (no I/O, no encoder, no KG load): multi-value Hebbian + set-readout."""
    g = np.random.default_rng(0); n = 512; ne = 40
    E = bipolar(ne, n, g); R = bipolar(4, n, g); sq = math.sqrt(n)
    keyobjs = {}
    for i in range(20):
        s = i; p = int(g.integers(0, 4)); K = int(g.integers(1, 4))
        keyobjs[(s, p)] = list(g.choice(ne, K, replace=False))
    W = np.zeros((n, n), dtype=np.float32)
    for (s, p), objs in keyobjs.items():
        key = E[s] * R[p] * sq
        for o in objs:
            W += np.outer(E[o], key) / n
    hit = 0; tot = 0
    for (s, p), objs in keyobjs.items():
        scores = E @ (W @ (E[s] * R[p] * sq)); topk = set(np.argsort(scores)[-len(objs):].tolist())
        hit += len(topk & set(objs)); tot += len(objs)
    assert hit / tot >= 0.9, "multi-value set-recall@k sanity (got %.2f)" % (hit / tot)
    inkb = float(np.max(E @ (W @ (E[0] * R[list(keyobjs)[0][1]] * sq))))
    ood_s, ood_p = 5, 3
    while (ood_s, ood_p) in keyobjs:
        ood_p = (ood_p + 1) % 4
    ood = float(np.max(E @ (W @ (E[ood_s] * R[ood_p] * sq))))
    assert inkb > ood, "refuse confidence: in-KB(%.3f) > OOD(%.3f)" % (inkb, ood)
    print("[selftest] PASS: multi-value set-recall=%.2f; refuse-conf in-KB %.3f > OOD %.3f" %
          (hit / tot, inkb, ood), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def load_kg(seed, m_triples):
    if not KG_PATH.exists():
        raise FileNotFoundError("ConceptNet en 100k not found at %s (run the cache step first)" % KG_PATH)
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
    return triples, {k: sorted(v) for k, v in keyobjs.items()}, ents, rels, eid, rid


def ingest_hebbian(triples, n_ent, n_rel, g, batch=5000):
    """Multi-value Hebbian: W += outer(E[o_i], key_i)/N over all triples; chunked BLAS matmul."""
    E = bipolar(n_ent, N_DIM, g); R = bipolar(n_rel, N_DIM, g); sq = math.sqrt(N_DIM)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / N_DIM
    return E, R, W, sq


def _scores_batch(E, R, W, sq, sp_pairs):
    if not sp_pairs:
        return np.zeros((0, E.shape[0]), dtype=np.float32)
    s = np.array([x[0] for x in sp_pairs]); p = np.array([x[1] for x in sp_pairs])
    keys = (E[s] * R[p] * sq).astype(np.float32)
    return (E @ (W @ keys.T)).T


def set_recall_at_k(E, R, W, sq, keyobjs, n_eval, g, restrict_1to1=False):
    keys = list(keyobjs.items())
    if restrict_1to1:
        keys = [(k, v) for k, v in keys if len(v) == 1]
    if not keys:
        return 0.0
    idx = g.permutation(len(keys))[:min(n_eval, len(keys))]
    sp = [keys[i][0] for i in idx]; objs = [keys[i][1] for i in idx]
    S = _scores_batch(E, R, W, sq, sp)
    tot = 0.0
    for j, ob in enumerate(objs):
        k = len(ob)
        topk = set(np.argpartition(S[j], -k)[-k:].tolist())
        tot += len(topk & set(ob)) / k
    return tot / max(len(idx), 1)


def refuse_gate(E, R, W, sq, keyobjs, n_ent, n_rel, n_q, g):
    inkb_keys = list(keyobjs.keys())
    idx = g.permutation(len(inkb_keys))[:min(n_q, len(inkb_keys))]
    inkb_conf = _scores_batch(E, R, W, sq, [inkb_keys[i] for i in idx]).max(axis=1)
    keyset = set(keyobjs.keys()); ood_sp = []; tries = 0
    while len(ood_sp) < n_q and tries < n_q * 50:
        s = int(g.integers(0, n_ent)); p = int(g.integers(0, n_rel)); tries += 1
        if (s, p) in keyset: continue
        ood_sp.append((s, p))
    ood_conf = _scores_batch(E, R, W, sq, ood_sp).max(axis=1) if ood_sp else np.zeros(0, np.float32)
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


def encode_entities(ents, model_name):
    """Frozen sentence-encoder semantic embeddings of entity names (one-shot ingest cost).

    Substrate-native gate: this baseline is INPUT-stage only (entity-name -> vector); the score
    operation (cosine sim) is a numpy matmul, NOT a model forward call. The encoder model is
    discarded after this call; no further inference touches it.
    """
    from sentence_transformers import SentenceTransformer
    # Replace underscores with spaces so MiniLM tokenizer reads natural English (ConceptNet uses
    # underscores in multi-word entities e.g. "fire_engine" -> "fire engine").
    texts = [e.replace("_", " ") for e in ents]
    m = SentenceTransformer(model_name, device="cpu")
    embs = m.encode(texts, batch_size=128, show_progress_bar=False, normalize_embeddings=True)
    return np.asarray(embs, dtype=np.float32)


def inference_transfer(E, R, W, sq, triples, keyobjs, n_2hop, g, ent_embs):
    """Held-out 2-hop with three baselines: substrate-2hop, 1-hop-lookup, frozen-encoder semantic.

    Frozen-encoder semantic baseline (OPEN-C UNLOCK): for a held-out chain (s, p1, x, p2, o), the
    semantic baseline predicts o_hat = argmax_e cos(ent_embs[s], ent_embs[e]) (entity-name nearest
    neighbor). This is a NON-COMPOSITIONAL baseline -- it asks 'is the answer just semantically
    similar to s?' If the substrate's 2-hop traversal is genuine composition (not just NN), it
    must beat this by INFER_RATIO_OVER_ENC.
    """
    adj = defaultdict(list)
    for (s, p), objs in keyobjs.items():
        for o in objs:
            adj[s].append((p, o))
    direct = set((s, o) for (s, p, o) in triples)
    chains = []; starts = [s for s in adj if adj[s]]; tries = 0; leak = 0
    while len(chains) < n_2hop and tries < n_2hop * 80:
        tries += 1
        s = int(g.choice(starts))
        p1, x = adj[s][int(g.integers(0, len(adj[s])))]
        if x not in adj or not adj[x]: continue
        p2, o = adj[x][int(g.integers(0, len(adj[x])))]
        if o == s: continue
        if (s, o) in direct:
            leak += 1; continue
        chains.append((s, p1, x, p2, o))
    if not chains:
        return {"n": 0}
    s_a = [(c[0], c[1]) for c in chains]; o_a = np.array([c[4] for c in chains])
    s_b = [(c[0], c[3]) for c in chains]
    S1 = _scores_batch(E, R, W, sq, s_a)
    x_hat = S1.argmax(axis=1)
    S2 = _scores_batch(E, R, W, sq, [(int(x_hat[j]), chains[j][3]) for j in range(len(chains))])
    o_hat = S2.argmax(axis=1)
    Sb = _scores_batch(E, R, W, sq, s_b)
    sub2 = float((o_hat == o_a).mean())
    base1 = float(((S1.argmax(axis=1) == o_a) | (Sb.argmax(axis=1) == o_a)).mean())
    # Frozen-encoder semantic baseline: nearest neighbor by entity-name embedding
    s_vecs = ent_embs[np.array([c[0] for c in chains])]    # (B, D_enc)
    sim = s_vecs @ ent_embs.T                              # (B, n_ent)
    # Exclude self (s != o requirement preserved)
    for j, c in enumerate(chains):
        sim[j, c[0]] = -np.inf
    enc_hat = sim.argmax(axis=1)
    enc_acc = float((enc_hat == o_a).mean())
    n = len(chains)
    return {"n": n, "substrate_2hop": sub2, "baseline_1hop": base1,
            "baseline_frozen_encoder": enc_acc,
            "heldout_in_compose_graph": 0, "leak_skipped": leak}


def run_seed(seed, ent_embs_cache):
    g = np.random.default_rng(seed)
    out = {"seed": seed, "scale_curve": {}, "config_version": CONFIG_VERSION,
           "run_mode": RUN_MODE, "N": N_DIM}
    for M in SCALE_POINTS:
        triples, keyobjs, ents, rels, eid, rid = load_kg(seed, M)
        n_ent = len(ents); n_rel = len(rels)
        t = time.time()
        E, R, W, sq = ingest_hebbian(triples, n_ent, n_rel, g)
        fid_all = set_recall_at_k(E, R, W, sq, keyobjs, N_EVAL, np.random.default_rng(seed + 1))
        fid_11 = set_recall_at_k(E, R, W, sq, keyobjs, N_EVAL, np.random.default_rng(seed + 2), restrict_1to1=True)
        out["scale_curve"]["M%d" % M] = {
            "setrecall_all": round(fid_all, 4), "setrecall_1to1": round(fid_11, 4),
            "n_ent": n_ent, "n_rel": n_rel, "n_keys": len(keyobjs),
            "n_triples": len(triples), "ingest_s": round(time.time() - t, 1)}
        print("  [seed=%d M=%d] setrecall all=%.4f 1to1=%.4f (n_ent=%d keys=%d, %.1fs)" % (
            seed, M, fid_all, fid_11, n_ent, len(keyobjs), time.time() - t), flush=True)
    # Load-bearing #2 + #3 at largest scale
    triples, keyobjs, ents, rels, eid, rid = load_kg(seed, max(SCALE_POINTS))
    n_ent = len(ents); n_rel = len(rels)
    E, R, W, sq = ingest_hebbian(triples, n_ent, n_rel, g)
    out["refuse_gate"] = refuse_gate(E, R, W, sq, keyobjs, n_ent, n_rel, N_OOD,
                                      np.random.default_rng(seed + 3))
    # Frozen-encoder embeddings cached per-call-(or-process) since ents list size depends on M;
    # we re-encode at M_max since that is the eval scale for inference-transfer. Cache keyed by
    # (M_max, n_ent) is harmless since ents-order is deterministic from sorted-set + seed-shuffle
    # (different seeds rotate which subset of entities makes it into the M_max sample).
    ck = (max(SCALE_POINTS), n_ent, tuple(ents[:8]))
    if ent_embs_cache.get("key") == ck:
        ent_embs = ent_embs_cache["embs"]
    else:
        t = time.time()
        ent_embs = encode_entities(ents, ENC_MODEL)
        print("  [seed=%d] encoded %d entities with %s in %.1fs" %
              (seed, n_ent, ENC_MODEL, time.time() - t), flush=True)
        ent_embs_cache["key"] = ck; ent_embs_cache["embs"] = ent_embs
    out["inference_transfer"] = inference_transfer(E, R, W, sq, triples, keyobjs, N_2HOP,
                                                    np.random.default_rng(seed + 4), ent_embs)
    print("  [seed=%d] refuse: ood=%.3f accept=%.3f (tau=%.4g) | infer: 2hop=%.3f vs 1hop=%.3f "
          "vs frozen-enc=%.3f (n=%d)" % (
        seed, out["refuse_gate"]["ood_refuse"], out["refuse_gate"]["inkb_accept"],
        out["refuse_gate"]["tau"],
        out["inference_transfer"].get("substrate_2hop", 0),
        out["inference_transfer"].get("baseline_1hop", 0),
        out["inference_transfer"].get("baseline_frozen_encoder", 0),
        out["inference_transfer"].get("n", 0)), flush=True)
    return out


def verdict(ps) -> Tuple[str, str]:
    big = "M%d" % max(SCALE_POINTS)
    sr_all = float(np.mean([p["scale_curve"][big]["setrecall_all"] for p in ps]))
    sr_11 = float(np.mean([p["scale_curve"][big]["setrecall_1to1"] for p in ps]))
    ood = float(np.mean([p["refuse_gate"]["ood_refuse"] for p in ps]))
    acc = float(np.mean([p["refuse_gate"]["inkb_accept"] for p in ps]))
    s2 = float(np.mean([p["inference_transfer"].get("substrate_2hop", 0) for p in ps]))
    b1 = float(np.mean([p["inference_transfer"].get("baseline_1hop", 0) for p in ps]))
    enc = float(np.mean([p["inference_transfer"].get("baseline_frozen_encoder", 0) for p in ps]))
    curve = {M: round(float(np.mean([p["scale_curve"]["M%d" % M]["setrecall_all"] for p in ps])), 3)
             for M in SCALE_POINTS}
    enc_ratio = (s2 / enc) if enc > 1e-6 else float("inf")
    summ = ("setrecall@%s all=%.3f 1to1=%.3f (floor %.2f) | refuse OOD=%.3f accept=%.3f (>=%.2f) | "
            "infer 2hop=%.3f vs 1hop=%.3f vs frozen-enc=%.3f (ratio=%.2fx, need >=%.1fx) | "
            "scale-curve=%s" % (big, sr_all, sr_11, SETRECALL_FLOOR, ood, acc, REFUSE_OOD_MIN,
                                 s2, b1, enc, enc_ratio, INFER_RATIO_OVER_ENC, curve))
    sr_pass = sr_all >= SETRECALL_FLOOR
    sr_fail = sr_all < SETRECALL_FAIL
    refuse_pass = ood >= REFUSE_OOD_MIN and acc >= ACCEPT_INKB_MIN
    infer_pass_1hop = s2 > b1 + INFER_MARGIN_OVER_1HOP
    infer_pass_enc = s2 >= INFER_RATIO_OVER_ENC * enc
    infer_pass = infer_pass_1hop and infer_pass_enc
    if sr_fail:
        return ("HARD_FAIL", "HARD_FAIL: set-recall below floor. " + summ)
    if sr_pass and refuse_pass and infer_pass:
        return ("HARD_PASS",
                "HARD_PASS: substrate KB-ingest GOVERNED (refuse-gate) + COMPOSES (2-hop vs 1-hop AND "
                "frozen-encoder; OPEN-C unlocked). " + summ)
    if refuse_pass or infer_pass_1hop or infer_pass_enc:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial -- not all load-bearing dims hold. " + summ)
    return ("HARD_FAIL", "HARD_FAIL: refuse-gate + inference-transfer both fall short. " + summ)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d scale=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, SCALE_POINTS, CONFIG_VERSION), flush=True)
    t0 = time.time()
    out_dir = REPO / "data" / ("exp_%s" % os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME))
    out_dir.mkdir(parents=True, exist_ok=True)
    ent_embs_cache = {}
    ps = []
    for s in SEEDS:
        pf = out_dir / ("partial_seed%d_%s.json" % (s, RUN_MODE))
        if pf.exists():
            try:
                rec = json.loads(pf.read_text(encoding="utf-8"))
                if rec.get("config_version") == CONFIG_VERSION:
                    print("  [seed=%d] RESUME from checkpoint (config match)" % s, flush=True)
                    ps.append(rec); continue
            except Exception:
                pass
        rec = run_seed(s, ent_embs_cache)
        pf.write_text(json.dumps(rec, indent=2), encoding="utf-8")
        ps.append(rec)
    v, vmsg = verdict(ps)
    print("\n[VERDICT] " + vmsg, flush=True)
    big = "M%d" % max(SCALE_POINTS)
    summary = vmsg
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": summary,
               "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "config_version": CONFIG_VERSION,
               "per_seed": ps, "elapsed_s": round(time.time() - t0, 1),
               "DESIGN_NOTE": "N8 ConceptNet ingest-eval; reuses U1 chain-grade pattern; "
                              "OPEN-C UNLOCKED via frozen-encoder MiniLM-L6 semantic baseline at "
                              "ingest-time only (substrate-native gate: encoder is INPUT-stage; "
                              "scoring is matmul, no forward calls); honest scope: 8 relation types "
                              "in en-100k vs FB15k-237's ~237; OOD class = (s,p) in-KB no-edge."}
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
