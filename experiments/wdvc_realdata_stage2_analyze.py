# Stage 2 ANALYZE: race the brain-faithful 4-signal gate vs a degree/frequency
# content-wall baseline on REAL held-out Wikidata revert labels.
#
# Signals (per notes/research_full4signal_realdata_capability_test_2026-07-16.md):
#   surprise    = 1 - reciprocal_rank(t | h, r) under additive_map (TransE readout),
#                 with ALL evaluation triples removed from the training graph (leakage control).
#   schema_fit  = Resource-Allocation structural plausibility of (h,t), direct edge removed.
#   recurrence  = pattern-corroboration: # OTHER entities asserting the same (rel,tail).
#                 (reference-count is revert-asymmetric so not used as primary; this proxy is symmetric.)
#   importance  = normalized(head statement_count + sitelinks) -- revert-invariant.
#
# Content-wall baseline (the bar to beat): temp-account, editor edit-freq, entity edit-freq,
#   |byte-delta|, head graph-degree, target graph-degree -- a genuine degree/frequency model.
#
# Metric: Average Precision (AUPRC) + AUROC on a TEMPORAL held-out split (train=early 60%,
#   test=late 40%). All arms scored on the SAME test rows (prevalence-fair).
# ASCII-only. No queue/GPU/atoms. Deterministic (fixed seeds, no hash()-derived RNG).

import json
import math
import os
import sys
import time

import numpy as np
import torch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hdlab.additive_map import additive_direct_scores
from hdlab import reachability_audit as ra

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "exp_wdvc_realdata_capability"))
RAW_PATH = os.path.join(OUT_DIR, "sample_raw.jsonl")
SAMPLE_PATH = os.path.join(OUT_DIR, "stage2_sample.jsonl")
CLAIMS_PATH = os.path.join(OUT_DIR, "entity_claims.jsonl")
RESULTS_PATH = os.path.join(OUT_DIR, "stage2_results.json")

SEED = 12345
K_DIM = 64
EPOCHS = 20
TAU = 3.0            # recurrence precision scale (calibrated on this corpus, not imported)
TRAIN_FRAC = 0.60
DEVICE = torch.device("cpu")


# --------------------------- metrics ---------------------------------------
def average_precision(y, s):
    """AUPRC via the standard step-wise average precision (y in {0,1}, s = score, higher=positive)."""
    order = np.argsort(-s, kind="mergesort")
    y = y[order]
    tp = np.cumsum(y)
    fp = np.cumsum(1 - y)
    precision = tp / np.maximum(tp + fp, 1)
    recall = tp / max(int(y.sum()), 1)
    ap = 0.0
    prev_r = 0.0
    for i in range(len(y)):
        if y[i] == 1:
            ap += precision[i] * (recall[i] - prev_r)
            prev_r = recall[i]
    return float(ap)


def auroc(y, s):
    """Rank-based AUROC (Mann-Whitney)."""
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(len(s), dtype=np.float64)
    ranks[order] = np.arange(1, len(s) + 1)
    # average ranks for ties
    s_sorted = s[order]
    i = 0
    while i < len(s_sorted):
        j = i
        while j + 1 < len(s_sorted) and s_sorted[j + 1] == s_sorted[i]:
            j += 1
        if j > i:
            avg = (ranks[order[i]] + ranks[order[j]]) / 2.0
            for kk in range(i, j + 1):
                ranks[order[kk]] = avg
        i = j + 1
    n_pos = int(y.sum())
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5
    sum_pos = ranks[y == 1].sum()
    return float((sum_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def logistic_fit(Xtr, ytr, steps=800, lr=0.3, l2=1e-3, seed=SEED):
    """Tiny deterministic GD logistic regression on standardized features. Returns (w, b, mu, sd)."""
    rng = np.random.RandomState(seed)
    mu = Xtr.mean(axis=0)
    sd = Xtr.std(axis=0) + 1e-9
    Z = (Xtr - mu) / sd
    n, d = Z.shape
    w = np.zeros(d)
    b = 0.0
    # class weighting to handle imbalance
    pos_w = (len(ytr) / max(2 * ytr.sum(), 1))
    neg_w = (len(ytr) / max(2 * (len(ytr) - ytr.sum()), 1))
    sw = np.where(ytr == 1, pos_w, neg_w)
    for _ in range(steps):
        p = 1.0 / (1.0 + np.exp(-(Z @ w + b)))
        g = (p - ytr) * sw
        gw = Z.T @ g / n + l2 * w
        gb = g.mean()
        w -= lr * gw
        b -= lr * gb
    return w, b, mu, sd


def logistic_score(X, w, b, mu, sd):
    Z = (X - mu) / sd
    return 1.0 / (1.0 + np.exp(-(Z @ w + b)))


# --------------------------- data ------------------------------------------
def load():
    claims = [json.loads(l) for l in open(CLAIMS_PATH, encoding="utf-8")]
    sample = [json.loads(l) for l in open(SAMPLE_PATH, encoding="utf-8")]
    raw = [json.loads(l) for l in open(RAW_PATH, encoding="utf-8")]
    return claims, sample, raw


def main():
    t0 = time.time()
    claims, sample, raw = load()

    # Frequency features from the FULL window stream (content-wall).
    from collections import Counter
    editor_freq = Counter(r["user"] for r in raw if not r["bot"])
    entity_freq = Counter(r["title"] for r in raw if not r["bot"])

    # Build graph triples from current claims (head from rec id).
    imp = {}          # entity -> statement_count + sitelinks
    triples_lbl = []  # (head, prop, target)
    for rec in claims:
        if rec.get("missing"):
            continue
        imp[rec["id"]] = rec["n_statements"] + rec["n_sitelinks"]
        for pid, tgt in rec["triples"]:
            triples_lbl.append((rec["id"], pid, tgt))

    # Evaluation triples to REMOVE from the training graph (both pos and neg) -> symmetric held-out.
    eval_triples = {(r["head"], r["prop"], r["target"]) for r in sample}
    train_triples = [t for t in triples_lbl if t not in eval_triples]

    # Index spaces: include every entity/relation that appears in graph OR sample.
    ents = set()
    rels = set()
    for h, p, t in triples_lbl:
        ents.add(h); ents.add(t); rels.add(p)
    for r in sample:
        ents.add(r["head"]); ents.add(r["target"]); rels.add(r["prop"])
    eidx = {e: i for i, e in enumerate(sorted(ents))}
    ridx = {p: i for i, p in enumerate(sorted(rels))}
    n_ent = len(eidx); n_rel = len(rels)
    print("[graph] n_ent=%d n_rel=%d train_triples=%d (removed %d eval triples)"
          % (n_ent, n_rel, len(train_triples), len(triples_lbl) - len(train_triples)), flush=True)

    train_int = np.array([[eidx[h], ridx[p], eidx[t]] for h, p, t in train_triples], dtype=np.int64)

    # ---- pattern-corroboration recurrence: count of DISTINCT heads per (rel,tail) in FULL graph ----
    rt_heads = {}
    for h, p, t in triples_lbl:
        rt_heads.setdefault((p, t), set()).add(h)
    def recurrence_of(h, p, t):
        s = rt_heads.get((p, t), set())
        return float(len(s - {h}))   # other entities asserting same (rel,tail)

    # ---- structural adjacency (undirected) for schema-fit ----
    adj = ra.build_undirected_adj(train_int, n_ent)
    deg = ra.degree_vector(adj)
    # neighbor sets for RA index
    nbr = [set(row) for row in adj]   # adj rows are arrays of neighbor ids

    def schema_fit_ra(h_i, t_i):
        """Resource-Allocation index between h and t (direct edge already excluded: eval triples removed)."""
        if h_i >= n_ent or t_i >= n_ent:
            return 0.0
        common = nbr[h_i] & nbr[t_i]
        if not common:
            return 0.0
        val = 0.0
        for z in common:
            dz = deg[z]
            if dz > 0:
                val += 1.0 / dz
        return val

    # ---- fit additive_map (modest KGE) ----
    print("[fit] additive_map k=%d epochs=%d on %d triples ..." % (K_DIM, EPOCHS, len(train_int)), flush=True)
    from experiments._kge_anchor1_fit import fit_kge_anchor1
    X, D = fit_kge_anchor1(train_int, n_ent, n_rel, K_DIM, DEVICE, SEED, EPOCHS)
    X = X.to(torch.float32); D = D.to(torch.float32)
    print("[fit] done in %.1fs" % (time.time() - t0), flush=True)

    # ---- surprise via held-out reciprocal rank, chunked over queries ----
    hold = np.array([[eidx[r["head"]], ridx[r["prop"]], eidx[r["target"]]] for r in sample], dtype=np.int64)
    surprise = np.zeros(len(sample))
    cold = np.zeros(len(sample), dtype=bool)
    CH = 400
    for s in range(0, len(sample), CH):
        e = min(s + CH, len(sample))
        sc = additive_direct_scores(X, D, hold[s:e], DEVICE)  # (b, n_ent)
        sc = sc.numpy()
        for j in range(e - s):
            t_i = hold[s + j, 2]
            tsc = sc[j, t_i]
            rank = int((sc[j] > tsc).sum()) + 1   # rank of true target (1=best)
            rr = 1.0 / rank
            surprise[s + j] = 1.0 - rr
        del sc
    # mark cold: head has zero training degree (no learned structure)
    for i, r in enumerate(sample):
        if deg[eidx[r["head"]]] == 0:
            cold[i] = True

    # ---- assemble per-row signals + content-wall features ----
    n = len(sample)
    y = np.array([1 if r["reverted"] else 0 for r in sample], dtype=np.float64)
    ts = np.array([r["timestamp"] for r in sample])
    sig_surprise = surprise
    sig_schema_viol = np.zeros(n)     # 1 - normalized schema_fit  (high => damage)
    sig_recur = np.zeros(n)
    sig_import = np.zeros(n)
    # content-wall
    cw_temp = np.zeros(n); cw_efreq = np.zeros(n); cw_entfreq = np.zeros(n)
    cw_bytes = np.zeros(n); cw_hdeg = np.zeros(n); cw_tdeg = np.zeros(n)
    for i, r in enumerate(sample):
        h_i = eidx[r["head"]]; t_i = eidx[r["target"]]
        raw_sf = schema_fit_ra(h_i, t_i)
        sf = raw_sf / (raw_sf + 1.0)               # [0,1)
        sig_schema_viol[i] = 1.0 - sf
        rec = recurrence_of(r["head"], r["prop"], r["target"])
        local_precision = rec / (rec + TAU)        # [0,1)
        sig_recur[i] = 1.0 - local_precision       # low corroboration => damage
        sig_import[i] = math.log1p(imp.get(r["head"], 0))
        cw_temp[i] = 1.0 if (r.get("user") or "").startswith("~") else 0.0
        cw_efreq[i] = math.log1p(editor_freq.get(r["user"], 0))
        cw_entfreq[i] = math.log1p(entity_freq.get(r["head"], 0))
        old, new = r.get("oldlen") or 0, r.get("newlen") or 0
        cw_bytes[i] = math.log1p(abs(new - old))
        cw_hdeg[i] = math.log1p(deg[h_i])
        cw_tdeg[i] = math.log1p(deg[t_i])
    # normalize importance to [0,1] for gate arithmetic
    sig_import_n = (sig_import - sig_import.min()) / (sig_import.max() - sig_import.min() + 1e-9)

    # ---- brain-faithful gate score (parameter-free, per scoping slow-track) ----
    # damage = surprising AND schema-violating AND low-corroboration; importance as mild tiebreak weight.
    gate = sig_surprise * sig_schema_viol * sig_recur * (1.0 + 0.25 * sig_import_n)

    # ---- temporal split ----
    order = np.argsort(ts, kind="mergesort")
    cut = int(TRAIN_FRAC * n)
    tr_idx = order[:cut]; te_idx = order[cut:]
    ytr, yte = y[tr_idx], y[te_idx]
    prevalence = float(yte.mean())

    def eval_on_test(score):
        return {"auprc": average_precision(yte, score[te_idx]), "auroc": auroc(yte, score[te_idx])}

    results = {}

    # naive (prevalence): AP == prevalence, AUROC == 0.5
    results["naive_prevalence"] = {"auprc": prevalence, "auroc": 0.5}

    # content-wall / degree-frequency logistic
    CW = np.column_stack([cw_temp, cw_efreq, cw_entfreq, cw_bytes, cw_hdeg, cw_tdeg])
    w, b, mu, sd = logistic_fit(CW[tr_idx], ytr)
    cw_pred = logistic_score(CW, w, b, mu, sd)
    results["content_wall_degree_freq"] = eval_on_test(cw_pred)

    # single-signal arms (evaluated directly; each higher=>damage)
    single = {"surprise": sig_surprise, "schema_violation": sig_schema_viol,
              "recurrence_deficit": sig_recur, "importance": sig_import_n}
    single_res = {name: eval_on_test(sc) for name, sc in single.items()}
    results["single_signals"] = single_res
    best_single = max(single_res.items(), key=lambda kv: kv[1]["auprc"])
    results["best_single_signal"] = {"name": best_single[0], **best_single[1]}

    # brain-faithful gate (parameter-free)
    results["brain_faithful_gate"] = eval_on_test(gate)

    # learned-logistic over the 4 gate signals
    G4 = np.column_stack([sig_surprise, sig_schema_viol, sig_recur, sig_import_n])
    wg, bg, mug, sdg = logistic_fit(G4[tr_idx], ytr)
    g4_pred = logistic_score(G4, wg, bg, mug, sdg)
    results["learned_logistic_4signal"] = eval_on_test(g4_pred)

    # gate + content-wall combined (does structure add over degree/freq?)
    ALL = np.column_stack([CW, G4])
    wa, ba, mua, sda = logistic_fit(ALL[tr_idx], ytr)
    all_pred = logistic_score(ALL, wa, ba, mua, sda)
    results["content_wall_plus_4signal"] = eval_on_test(all_pred)

    # ---- ablations of the brain-faithful gate (leave-one-signal-out) ----
    ablate = {}
    base_ap = results["brain_faithful_gate"]["auprc"]
    comps = {"surprise": sig_surprise, "schema_violation": sig_schema_viol,
             "recurrence_deficit": sig_recur, "importance_weight": (1.0 + 0.25 * sig_import_n)}
    for drop in ["surprise", "schema_violation", "recurrence_deficit", "importance_weight"]:
        g = np.ones(n)
        for name, arr in comps.items():
            if name == drop:
                continue
            g = g * arr
        ap = eval_on_test(g)["auprc"]
        ablate[drop] = {"auprc_without": ap, "delta_vs_full": base_ap - ap}
    results["ablations"] = ablate

    # ---- verdict ----
    gate_ap = results["brain_faithful_gate"]["auprc"]
    cw_ap = results["content_wall_degree_freq"]["auprc"]
    bs_ap = results["best_single_signal"]["auprc"]
    combo_ap = results["content_wall_plus_4signal"]["auprc"]
    rel_margin_vs_cw = (gate_ap - cw_ap) / max(cw_ap, 1e-9)
    combo_lift_vs_cw = (combo_ap - cw_ap) / max(cw_ap, 1e-9)
    min_ablation = min(v["delta_vs_full"] for v in ablate.values())

    hard_pass = (gate_ap > cw_ap) and (rel_margin_vs_cw >= 0.20) and (gate_ap >= bs_ap) and (min_ablation > 0)
    hard_fail = (gate_ap <= cw_ap)
    if hard_pass:
        verdict = "HARD_PASS"
    elif hard_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE"

    summary = {
        "stage": 2,
        "n_sample": n, "n_test": len(te_idx), "test_prevalence": prevalence,
        "n_positives_total": int(y.sum()), "cold_head_fraction": float(cold.mean()),
        "config": {"k_dim": K_DIM, "epochs": EPOCHS, "tau": TAU, "train_frac": TRAIN_FRAC, "seed": SEED},
        "split": "temporal (early %d%% train / late test)" % int(TRAIN_FRAC * 100),
        "metric": "AUPRC primary (AUROC secondary), same test rows all arms",
        "results": results,
        "decisive": {
            "gate_auprc": gate_ap, "content_wall_auprc": cw_ap, "best_single_auprc": bs_ap,
            "combo_auprc": combo_ap,
            "gate_rel_margin_vs_content_wall": rel_margin_vs_cw,
            "combo_rel_lift_vs_content_wall": combo_lift_vs_cw,
            "min_ablation_delta": min_ablation,
        },
        "prereg_bands": {
            "HARD_PASS": "gate AUPRC > content-wall AND rel_margin>=0.20 AND gate>=best_single AND all ablations positive",
            "HARD_FAIL": "gate AUPRC <= content-wall (no better than degree/freq)",
            "MIDDLE": "gate beats content-wall but <20% relative OR mixed",
        },
        "verdict": verdict,
        "caveats": [
            "label = mw-reverted tag (reverted-as-damage proxy; broader than pure-vandalism rollback)",
            "test restricted to item-valued edits (20% of edits) -- the subpopulation additive_map can score",
            "reference-count recurrence is revert-asymmetric; recurrence uses symmetric pattern-corroboration proxy",
            "FAIR-S / permutation-null DWPC SOTA debiased baselines NOT reproduced; content-wall logistic is the local degree/freq bar",
            "graph = current-state claims with eval triples removed (leave-out); not a true pre-edit historical snapshot",
        ],
        "elapsed_s": time.time() - t0,
    }
    with open(RESULTS_PATH + ".tmp", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    os.replace(RESULTS_PATH + ".tmp", RESULTS_PATH)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise
