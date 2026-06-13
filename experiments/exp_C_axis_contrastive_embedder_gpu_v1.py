"""
exp_C_axis_contrastive_embedder_gpu_v1.py -- C-axis functional-similarity via CONTRASTIVE supervised metric learning (3rd mechanism class) -- GPU.

ROUTING: Research hand-off (exp_dev_handoff_research_C_axis_functional_similarity_contrastive_2026-06-12). C-axis residual is
  FUNCTIONAL-similarity-bound: bge-cosine REFUTED (functional != topical) and structural 1-hop propagation REFUTED (precision
  crash). Third mechanism class = LEARN functional similarity from the substrate's OWN structured supervision graph
  (serves_capability pairs). bge-FROZEN + 2-layer projection head (1024->256->128) trained with Multiple-Negatives-Ranking +
  batch-hard triplet (margin 0.2) on (capability, serving-atom) positives. Substrate-product reading: substrate learns functional
  similarity from its structured trace; LLMs have no serves_capability supervision graph. C-axis becomes a LEARNABLE surface,
  not a corpus-bound ceiling. NO generative LLM (bge is an embedding model; the head is substrate-trained).

  HONEST DESIGN (exp_dev): HELD-OUT eval -- the 9 benchmark C-Q capabilities are EXCLUDED from training pairs, so the eval tests
  GENERALIZATION of the learned functional metric to UNSEEN capabilities (no train/eval leakage). Eval policies on the 9 C-Qs:
  what_serves (baseline 0.58), contrastive-top-k, contrastive-threshold, what_serves UNION contrastive (field-gold + learned
  recovery of serves_capability=NONE gold). Also reports recovery of the NONE-gold specifically.

PRE-REGISTERED (from research note, exp_dev-tightened): HARD-PASS best contrastive policy C-F1 >= what_serves + 0.05 (>= ~0.63)
  AND train loss converges. MIDDLE +0.02..0.05. HARD-FAIL < +0.02 OR loss not converging -> functional similarity not learnable
  from this supervision (C stays authoring-bound). UNKNOWN if bge/data unavailable.
ASCII-only. write_metrics. PROT-020 (import torch). GPU. Remote-only training. Route via overnight_queue.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, json
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "C_axis_contrastive_embedder_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
MARGIN = 0.2; TEMP = 0.05; STEPS = 40 if SMOKE else 800; BATCH = 32; LR = 1e-3; SEED = 1028


def _norm(x):
    return str(x).split("::")[-1].strip().lower()


def _f1(retrieved, gold):
    if not gold:
        return 1.0 if not retrieved else 0.0
    tp = len(retrieved & gold); fp = len(retrieved - gold); fn = len(gold - retrieved)
    p = tp / (tp + fp + 1e-9); r = tp / (tp + fn + 1e-9)
    return 2 * p * r / (p + r + 1e-9)


def _selftest():
    assert abs(_f1({"a"}, {"a", "b"}) - (2 * 1.0 * 0.5 / 1.5)) < 1e-6
    print("[selftest] PASS: C_axis_contrastive_embedder_gpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required (remote-only training).", flush=True); sys.exit(1)
DEV = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def run() -> Dict:
    from backend.substrate_index.partition import PartitionedStore
    bench_fp = REPO / "experiments" / "data" / "gap7_benchmark_v1.jsonl"
    if not bench_fp.exists():
        return {"error": "benchmark_missing"}
    raw = [json.loads(l) for l in open(bench_fp, encoding="utf-8") if l.strip()]
    cqs = []
    for r in raw:
        if r.get("type", "A").split("_")[0].upper() != "C":
            continue
        gold = list(r.get("ground_truth_atoms") or r.get("gold") or [])
        if not gold:
            continue
        cqs.append({"id": r.get("qid") or r.get("id"), "cap": (r.get("args") or {}).get("capability", ""),
                    "gold": set(_norm(g) for g in gold)})
    idx_dir = REPO / "data" / "substrate_index"
    if not idx_dir.exists():
        return {"error": "no_substrate_index"}
    pstore = PartitionedStore(idx_dir); atoms = pstore.all_atoms()
    try:
        from backend.substrate_index.encode import AtomEncoder
        from backend.substrate_index.retrieve import Retriever
        enc = AtomEncoder(); retr = Retriever(getattr(pstore, "store", pstore), enc); retr.rebuild_index()
    except Exception as e:
        return {"error": "bge_unavailable", "note": str(e)[:160]}
    id_order = retr._id_order; sem = retr._semantic_matrix.astype(np.float32)
    norm_ids = [_norm(i) for i in id_order]; nid_row = {nid: i for i, nid in enumerate(norm_ids)}
    allids = set(norm_ids)
    # capability bge vector: atom row if present, else encode capability text
    def cap_vec(capq):
        c = _norm(capq)
        if c in nid_row:
            return sem[nid_row[c]]
        import re as _re
        t = _re.sub(r"^(cap_|pp-\d+_?)", "", c).replace("_", " ")
        v = enc.bge.encode([t])[0].astype(np.float32); return v / (np.linalg.norm(v) + 1e-9)
    # restrict gold to in-index
    for q in cqs:
        q["gold"] = set(g for g in q["gold"] if g in allids)
    held_out_caps = set(_norm(q["cap"]) for q in cqs)  # NO training on benchmark C-Q capabilities (no leakage)
    # build positive pairs (capability, serving-atom), excluding held-out caps
    pairs = []
    for a in atoms:
        sc = getattr(a, "serves_capability", None) or ()
        if isinstance(sc, str): sc = [sc]
        for c in sc:
            cn = _norm(c)
            if cn in allids and cn not in held_out_caps:
                pairs.append((cn, _norm(a.id)))
    pairs = [(c, a) for c, a in pairs if a in nid_row]
    n_pairs = len(pairs)
    if n_pairs < 20:
        return {"error": "insufficient_training_pairs", "n_pairs": n_pairs}
    anchor_bge = np.stack([cap_vec(c) for c, _a in pairs]).astype(np.float32)
    pos_bge = np.stack([sem[nid_row[a]] for _c, a in pairs]).astype(np.float32)
    A = torch.from_numpy(anchor_bge).to(DEV); P = torch.from_numpy(pos_bge).to(DEV)
    # projection head
    torch.manual_seed(SEED)
    head = nn.Sequential(nn.Linear(1024, 256), nn.ReLU(), nn.Linear(256, 128)).to(DEV)
    opt = torch.optim.Adam(head.parameters(), lr=LR)
    g = torch.Generator(device=DEV).manual_seed(SEED)
    loss_hist = []
    for step in range(STEPS):
        bidx = torch.randperm(n_pairs, generator=g, device=DEV)[:min(BATCH, n_pairs)]
        a = F.normalize(head(A[bidx]), dim=1); p = F.normalize(head(P[bidx]), dim=1)
        sim = a @ p.T                                            # [B,B]
        labels = torch.arange(a.shape[0], device=DEV)
        loss_mnr = F.cross_entropy(sim / TEMP, labels)
        eye = torch.eye(a.shape[0], device=DEV).bool()
        hardest_neg = sim.masked_fill(eye, -1e9).max(dim=1).values
        loss_tri = F.relu(MARGIN - sim.diag() + hardest_neg).mean()
        loss = loss_mnr + loss_tri
        opt.zero_grad(); loss.backward(); opt.step()
        loss_hist.append(float(loss))
    conv = loss_hist[-1] < loss_hist[0] * 0.7   # rough convergence check
    print("  trained head: %d pairs, %d steps; loss %.4f -> %.4f (converged=%s)" % (n_pairs, STEPS, loss_hist[0], loss_hist[-1], conv), flush=True)
    # project all atoms once
    head.eval()
    with torch.no_grad():
        allproj = F.normalize(head(torch.from_numpy(sem).to(DEV)), dim=1)  # [N,128]
    Np = allproj.shape[0]
    from backend.substrate_index import self_knowledge as sk
    # eval policies on held-out C-Qs
    pol_f1 = {p: [] for p in ["what_serves", "contrastive_top5", "contrastive_top10", "thr_0.5", "thr_0.6", "ws_U_ctop5", "ws_U_ctop10"]}
    none_recovered = 0; none_total = 0
    for q in cqs:
        gold = q["gold"]
        try:
            ws = set(_norm(x.id) for x in sk.what_serves(pstore, q["cap"]))
        except Exception:
            ws = set()
        cv = cap_vec(q["cap"])
        with torch.no_grad():
            cvp = F.normalize(head(torch.from_numpy(cv[None, :]).to(DEV)), dim=1)
            sims = (allproj @ cvp.T).squeeze(1)                 # [N]
        order = torch.argsort(sims, descending=True).tolist()
        cn = _norm(q["cap"])
        def ctop(k):
            out = set();
            for i in order:
                if norm_ids[i] == cn: continue
                out.add(norm_ids[i])
                if len(out) >= k: break
            return out
        simnp = sims.detach().cpu().numpy()
        def cthr(t):
            return set(norm_ids[i] for i in range(Np) if simnp[i] >= t and norm_ids[i] != cn)
        rets = {"what_serves": ws, "contrastive_top5": ctop(5), "contrastive_top10": ctop(10),
                "thr_0.5": cthr(0.5), "thr_0.6": cthr(0.6), "ws_U_ctop5": ws | ctop(5), "ws_U_ctop10": ws | ctop(10)}
        for p in pol_f1: pol_f1[p].append(_f1(rets[p], gold))
        # NONE-gold recovery: gold atoms NOT retrieved by what_serves, recovered by contrastive-top10
        none_g = gold - ws
        none_total += len(none_g); none_recovered += len(none_g & ctop(10))
    macro = {p: round(float(np.mean(v)), 4) for p, v in pol_f1.items()}
    base = macro["what_serves"]
    best_p = max((p for p in macro if p != "what_serves"), key=lambda p: macro[p]); best = macro[best_p]
    print("  C-F1 by policy (held-out eval, n=%d):" % len(cqs), flush=True)
    for p in pol_f1:
        print("    %-20s %.4f%s" % (p, macro[p], "  <-- what_serves baseline" if p == "what_serves" else ""), flush=True)
    print("  best=%s %.4f vs what_serves %.4f (delta %+.4f); NONE-gold recovered %d/%d" % (best_p, best, base, best - base, none_recovered, none_total), flush=True)
    return {"n": len(cqs), "n_pairs": n_pairs, "macro_by_policy": macro, "ws_baseline": base, "best_policy": best_p,
            "best_f1": best, "delta": round(best - base, 4), "converged": bool(conv),
            "loss_first": round(loss_hist[0], 4), "loss_last": round(loss_hist[-1], 4),
            "none_recovered": none_recovered, "none_total": none_total}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("note", r.get("n_pairs", ""))))
    d = r["delta"]; conv = r["converged"]
    s = "best=%s C-F1=%.4f vs what_serves %.4f (delta %+.4f); loss %.3f->%.3f conv=%s; NONE-gold recovered %d/%d; n_pairs=%d; all=%s" % (
        r["best_policy"], r["best_f1"], r["ws_baseline"], d, r["loss_first"], r["loss_last"], conv, r["none_recovered"], r["none_total"], r["n_pairs"], r["macro_by_policy"])
    if d >= 0.05 and conv:
        return ("HARD_PASS", "HARD_PASS: the contrastive functional-similarity embedder LIFTS C-axis >= +0.05 over what_serves on HELD-OUT capabilities -- functional similarity IS learnable from the substrate's serves_capability supervision graph. C-axis is a learnable surface, not a corpus-bound ceiling (3rd mechanism class succeeds where bge-cosine + propagation failed). " + s)
    if d >= 0.02 and conv:
        return ("MIDDLE_BAND", "MIDDLE_BAND: contrastive embedder gives a small held-out C-F1 lift (+0.02..0.05) -- functional similarity partially learnable; hard-negative-mining ablation (anchor #2) + more supervision pairs may push it. " + s)
    return ("HARD_FAIL", "HARD_FAIL: contrastive embedder does not lift C-F1 >= +0.02 on held-out caps (or loss not converged) -- functional similarity not learnable from this sparse supervision (155 pairs, median 1/cap); C stays authoring-bound. " + s)


print("[config] anchor=%s mode=%s steps=%d" % (ANCHOR_NAME, RUN_MODE, STEPS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
