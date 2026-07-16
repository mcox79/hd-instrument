# DECISIVE FAIR CLAIM-VALIDITY TEST (CoDEx-S triple classification; Safavi & Koutra EMNLP 2020).
#
# Question: do brain-faithful STRUCTURAL signals (plausibility/surprise, schema-fit,
# recurrence) beat a FREQUENCY-MATCHED baseline on NOVEL claim-validity, where frequency
# is structurally UNINFORMATIVE and structural signals should carry the signal IF the
# brain's novel-claim advantage is real?
#
# WHY CoDEx (native to the additive_map/RA machinery; a real pre-program benchmark):
#   CoDEx triple-classification = "is this claim (h,r,t) TRUE?" with HUMAN-VERIFIED hard
#   negatives that are TYPE-CONSTRAINED and KGE-plausible -> frequency-comparable to the
#   positives BY CONSTRUCTION. This is a claim-validity task native to KG triples (no NL
#   entity-linking/relation-extraction pipeline needed, which would inject a confound).
#   HONESTY NOTE: CoDEx negatives are KGE-PLAUSIBLE by construction (adversarial to any
#   embedding-style plausibility readout), so the additive_map surprise signal is at a
#   genuine disadvantage here. This is the fair, hard version -- P(structural wins) ~= 0.30.
#
# PRECONDITION (fairness certificate, verified FIRST -- like an info-gain certificate):
#   the degree/frequency baseline MUST be at/near CHANCE on the evaluated split by
#   construction. If frequency still discriminates, the split isn't frequency-blind and
#   the gate result cannot be trusted -- FIX THE SPLIT FIRST. We escalate fairness controls
#   (full -> relation-balanced -> relation+degree-bin-matched) and take the FIRST control
#   where the certificate fires. The controls remove KNOWN frequency confounds (relation
#   prior, entity-popularity) -- they are NOT tuned against structural performance.
#
# Signals (reuse hdlab.additive_map + hdlab.reachability_audit, per WDVC stage2 cell):
#   plausibility = mean reciprocal-rank of the held-out entity, BOTH directions
#                  (tail | h,r via forward D; head | r,t via reciprocal-inverse D) under
#                  additive_map trained on the train graph. (= 1 - surprise; higher => TRUE)
#   schema_fit   = Resource-Allocation structural index between h and t on train adjacency.
#   recurrence   = pattern-corroboration: # distinct OTHER heads asserting (r,t) in train.
#   [degree/importance is the FREQUENCY confound -> it goes in the baseline, not the gate.]
#
# Metric: AUROC primary (balanced split -> chance = 0.5) + AUPRC. Same test rows all arms.
#   Learned arms (freq baseline / learned-logistic / combo) FIT on the CoDEx VALID split
#   (same fairness control), EVAL on the TEST split. Parameter-free arms eval directly.
#
# ASCII-only. Local CPU. Deterministic (fixed seeds; no hash()-derived RNG). No queue/GPU/atoms.
#
# CELL-TEMPLATE notes: single-shot local run-to-completion (NOT a queue dispatch), so the
# runner start_marker/heartbeat gates do not apply; atomic tmp+os.replace metrics write,
# no bare except, arms-differ check, deterministic selection (sorted()) are all present.

import json
import math
import os
import sys
import time
from collections import Counter, defaultdict

import numpy as np
import torch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from hdlab.additive_map import additive_direct_scores
from hdlab import reachability_audit as ra
from experiments._kge_anchor1_fit import fit_kge_anchor1

RAW = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "codex_claimvalidity", "raw"))
OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "exp_codex_claimvalidity"))
RESULTS_PATH = os.path.join(OUT_DIR, "metrics.json")

SEED = int(os.environ.get("CV_SEED", "12345"))
NN_CALIPER = float(os.environ.get("CV_CALIPER", "0.20"))
K_DIM = 64
EPOCHS = 20
TAU = 3.0            # recurrence precision scale (calibrated on THIS corpus, not imported)
DEVICE = torch.device("cpu")

# certificate band: frequency baseline is "at/near chance" iff AUROC in [0.45, 0.55]
FREQ_CHANCE_HI = 0.55
FREQ_CHANCE_LO = 0.45


# --------------------------- metrics (verbatim from WDVC stage2) ------------
def average_precision(y, s):
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
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(len(s), dtype=np.float64)
    ranks[order] = np.arange(1, len(s) + 1)
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


def logistic_fit(Xtr, ytr, steps=800, lr=0.3, l2=1e-3):
    mu = Xtr.mean(axis=0)
    sd = Xtr.std(axis=0) + 1e-9
    Z = (Xtr - mu) / sd
    n, d = Z.shape
    w = np.zeros(d)
    b = 0.0
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


def pct_rank(a):
    """percentile-rank in (0,1], scale-free monotone (AUROC-invariant for single arms)."""
    order = np.argsort(a, kind="mergesort")
    r = np.empty(len(a), dtype=np.float64)
    r[order] = np.arange(1, len(a) + 1)
    return r / len(a)


# --------------------------- data ------------------------------------------
def read_triples(fname):
    return [tuple(l.split("\t")) for l in open(os.path.join(RAW, fname), encoding="utf-8").read().split("\n") if l]


def main():
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)

    train = read_triples("train.txt")
    val_p = read_triples("valid.txt");  val_n = read_triples("valid_negatives.txt")
    tst_p = read_triples("test.txt");   tst_n = read_triples("test_negatives.txt")

    # index spaces over union (transductive; all test entities are in train)
    ents, rels = set(), set()
    for h, r, t in train + val_p + val_n + tst_p + tst_n:
        ents.add(h); ents.add(t); rels.add(r)
    eidx = {e: i for i, e in enumerate(sorted(ents))}
    ridx = {p: i for i, p in enumerate(sorted(rels))}
    n_ent, n_rel = len(eidx), len(ridx)

    train_int = np.array([[eidx[h], ridx[r], eidx[t]] for h, r, t in train], dtype=np.int64)

    # leakage guard: no test/valid POSITIVE may appear in the training graph
    train_set = set(train)
    leak = sum(1 for tp in (val_p + tst_p) if tp in train_set)
    assert leak == 0, "LEAK: %d eval positives found in train graph" % leak

    # ---- structural scaffolding from TRAIN only ----
    adj = ra.build_undirected_adj(train_int, n_ent)
    deg = ra.degree_vector(adj)
    nbr = [set(row) for row in adj]

    rel_freq = Counter(r for h, r, t in train)                 # relation prior (frequency)
    rt_heads = defaultdict(set)                                 # (rel,tail) -> heads asserting it
    for h, r, t in train:
        rt_heads[(r, t)].add(h)

    def schema_fit_ra(h_i, t_i):
        if h_i >= n_ent or t_i >= n_ent:
            return 0.0
        common = nbr[h_i] & nbr[t_i]
        val = 0.0
        for z in common:
            dz = deg[z]
            if dz > 0:
                val += 1.0 / dz
        return val

    def recurrence(h, r, t):
        return float(len(rt_heads.get((r, t), set()) - {h}))

    # ---- fit additive_map (reciprocal -> both fwd + inverse displacement blocks) ----
    print("[fit] additive_map k=%d epochs=%d on %d triples (n_ent=%d n_rel=%d) ..."
          % (K_DIM, EPOCHS, len(train_int), n_ent, n_rel), flush=True)
    X, Df, Di = fit_kge_anchor1(train_int, n_ent, n_rel, K_DIM, DEVICE, SEED, EPOCHS, return_inverse=True)
    X = X.to(torch.float32); Df = Df.to(torch.float32); Di = Di.to(torch.float32)
    print("[fit] done in %.1fs" % (time.time() - t0), flush=True)

    def plausibility_batch(rows):
        """mean reciprocal-rank of held-out entity, tail-dir (fwd) + head-dir (inverse). higher=>TRUE."""
        n = len(rows)
        hri = np.array([[eidx[h], ridx[r], eidx[t]] for h, r, t in rows], dtype=np.int64)
        rr_t = np.zeros(n); rr_h = np.zeros(n)
        CH = 400
        # tail direction: score all tails given (h,r) via forward D
        for s in range(0, n, CH):
            e = min(s + CH, n)
            sc = additive_direct_scores(X, Df, hri[s:e], DEVICE).numpy()
            for j in range(e - s):
                ti = hri[s + j, 2]
                rank = int((sc[j] > sc[j, ti]).sum()) + 1
                rr_t[s + j] = 1.0 / rank
            del sc
        # head direction: score all heads given (r,t) via inverse D -> query edges [t, r, h]
        inv = hri[:, [2, 1, 0]].copy()
        for s in range(0, n, CH):
            e = min(s + CH, n)
            sc = additive_direct_scores(X, Di, inv[s:e], DEVICE).numpy()
            for j in range(e - s):
                hi = inv[s + j, 2]
                rank = int((sc[j] > sc[j, hi]).sum()) + 1
                rr_h[s + j] = 1.0 / rank
            del sc
        return 0.5 * (rr_t + rr_h)

    # ---- feature builder for a labeled row set ----
    def featurize(rows, labels):
        n = len(rows)
        plaus = plausibility_batch(rows)
        sf = np.zeros(n); rec = np.zeros(n)
        hdeg = np.zeros(n); tdeg = np.zeros(n); rfreq = np.zeros(n)
        for i, (h, r, t) in enumerate(rows):
            hi, ti = eidx[h], eidx[t]
            raw_sf = schema_fit_ra(hi, ti)
            sf[i] = raw_sf / (raw_sf + 1.0)
            rc = recurrence(h, r, t)
            rec[i] = rc / (rc + TAU)                       # corroboration in [0,1); higher=>TRUE
            hdeg[i] = math.log1p(deg[hi])
            tdeg[i] = math.log1p(deg[ti])
            rfreq[i] = math.log1p(rel_freq.get(r, 0))
        return {
            "y": np.array(labels, dtype=np.float64),
            "plausibility": plaus, "schema_fit": sf, "recurrence": rec,
            "head_deg": hdeg, "tail_deg": tdeg, "rel_freq": rfreq,
            "rows": rows,
        }

    # ---- fairness-control split constructors (deterministic) ----
    # global log-degree quartile thresholds from TRAIN (fixed reference for degree bins)
    ld = np.log1p(deg[deg > 0])
    qthr = np.quantile(ld, [0.25, 0.5, 0.75]) if len(ld) else np.array([0., 0., 0.])
    def dbin(e_i):
        v = math.log1p(deg[e_i])
        return int(np.searchsorted(qthr, v))

    def build_full(pos, neg):
        rows = list(pos) + list(neg)
        labels = [1] * len(pos) + [0] * len(neg)
        return rows, labels

    def build_relation_balanced(pos, neg):
        by_r_p = defaultdict(list); by_r_n = defaultdict(list)
        for tr in pos: by_r_p[tr[1]].append(tr)
        for tr in neg: by_r_n[tr[1]].append(tr)
        rows, labels = [], []
        for r in sorted(set(by_r_p) | set(by_r_n)):
            k = min(len(by_r_p[r]), len(by_r_n[r]))
            for tr in sorted(by_r_p[r])[:k]: rows.append(tr); labels.append(1)
            for tr in sorted(by_r_n[r])[:k]: rows.append(tr); labels.append(0)
        return rows, labels

    def build_relation_degree_matched(pos, neg):
        cell_p = defaultdict(list); cell_n = defaultdict(list)
        for tr in pos:
            key = (tr[1], dbin(eidx[tr[0]]), dbin(eidx[tr[2]]))
            cell_p[key].append(tr)
        for tr in neg:
            key = (tr[1], dbin(eidx[tr[0]]), dbin(eidx[tr[2]]))
            cell_n[key].append(tr)
        rows, labels = [], []
        for key in sorted(set(cell_p) | set(cell_n)):
            k = min(len(cell_p[key]), len(cell_n[key]))
            for tr in sorted(cell_p[key])[:k]: rows.append(tr); labels.append(1)
            for tr in sorted(cell_n[key])[:k]: rows.append(tr); labels.append(0)
        return rows, labels

    def build_relation_nn_degree_matched(pos, neg, caliper=NN_CALIPER):
        """1:1 nearest-neighbor caliper matching on (log head_deg, log tail_deg) within each
        relation -> matched pos/neg have near-identical popularity -> drives the frequency
        baseline to chance. Standard matched-control design; deterministic (sorted, greedy)."""
        by_r_p = defaultdict(list); by_r_n = defaultdict(list)
        for tr in pos: by_r_p[tr[1]].append(tr)
        for tr in neg: by_r_n[tr[1]].append(tr)
        def feat(tr): return (math.log1p(deg[eidx[tr[0]]]), math.log1p(deg[eidx[tr[2]]]))
        rows, labels = [], []
        for r in sorted(set(by_r_p) | set(by_r_n)):
            P = sorted(by_r_p[r]); Nn = sorted(by_r_n[r])
            if not P or not Nn:
                continue
            Pf = [feat(tr) for tr in P]; Nf = [feat(tr) for tr in Nn]
            used = [False] * len(Nn)
            for pi, tr in enumerate(P):
                best, bestd = -1, caliper
                for ni in range(len(Nn)):
                    if used[ni]:
                        continue
                    d = math.hypot(Pf[pi][0] - Nf[ni][0], Pf[pi][1] - Nf[ni][1])
                    if d <= bestd:
                        bestd, best = d, ni
                if best >= 0:
                    used[best] = True
                    rows.append(tr); labels.append(1)
                    rows.append(Nn[best]); labels.append(0)
        return rows, labels

    CONTROLS = [
        ("full", build_full),
        ("relation_balanced", build_relation_balanced),
        ("relation_degree_matched", build_relation_degree_matched),
        ("relation_nn_degree_matched", build_relation_nn_degree_matched),
    ]

    FREQ_FEATS = ["head_deg", "tail_deg", "rel_freq"]
    STRUCT_FEATS = ["plausibility", "schema_fit", "recurrence"]

    def freq_baseline_auroc(feat_tr, feat_te):
        """strongest freq baseline: logistic over degree/rel-freq, fit on valid-split, eval test-split.
        also report the best SINGLE degree feature AUROC (no fitting -> cannot underfit)."""
        Xtr = np.column_stack([feat_tr[f] for f in FREQ_FEATS])
        Xte = np.column_stack([feat_te[f] for f in FREQ_FEATS])
        w, b, mu, sd = logistic_fit(Xtr, feat_tr["y"])
        pred = logistic_score(Xte, w, b, mu, sd)
        logit_auc = auroc(feat_te["y"], pred)
        singles = {}
        for f in FREQ_FEATS:
            a = auroc(feat_te["y"], feat_te[f])
            singles[f] = max(a, 1 - a)   # |AUROC-0.5| best-orientation (freq's best shot)
        best_single_freq = max(singles.values())
        # certificate uses the STRONGER of logistic and best single freq feature
        cert_auc = max(logit_auc, best_single_freq)
        return {"freq_logistic_auroc": logit_auc, "freq_single_best_auroc": best_single_freq,
                "freq_singles": singles, "certificate_auroc": cert_auc}

    # ---- featurize valid + test ONCE, then apply controls (cheap re-selection) ----
    print("[featurize] valid + test ...", flush=True)
    vrows, vlab = build_full(val_p, val_n)
    trows, tlab = build_full(tst_p, tst_n)
    F_val_full = featurize(vrows, vlab)
    F_test_full = featurize(trows, tlab)

    def subselect(Ffull, pos, neg, builder):
        rows, labels = builder(pos, neg)
        # deterministic: map each builder-selected triple to its occurrence index in Ffull
        # (a triple can occur as both a positive and a hard negative -> match by occurrence order)
        used = defaultdict(int)
        buckets = defaultdict(list)
        for i, tr in enumerate(Ffull["rows"]):
            buckets[tr].append(i)
        out_idx = []
        for tr in rows:
            k = used[tr]
            out_idx.append(buckets[tr][k])
            used[tr] += 1
        out_idx = np.array(out_idx, dtype=np.int64)
        sub = {k: (v[out_idx] if isinstance(v, np.ndarray) else [v[i] for i in out_idx])
               for k, v in Ffull.items() if k != "rows"}
        sub["rows"] = [Ffull["rows"][i] for i in out_idx]
        sub["y"] = Ffull["y"][out_idx]
        return sub

    # ---- escalate controls until the frequency certificate fires ----
    certs = {}
    chosen = None
    for cname, builder in CONTROLS:
        F_te = subselect(F_test_full, tst_p, tst_n, builder)
        F_tr = subselect(F_val_full, val_p, val_n, builder)
        fb = freq_baseline_auroc(F_tr, F_te)
        n_te = len(F_te["y"]); prev = float(F_te["y"].mean())
        cert_fires = (FREQ_CHANCE_LO <= fb["certificate_auroc"] <= FREQ_CHANCE_HI)
        certs[cname] = {"n_test": n_te, "test_prevalence": prev,
                        "certificate_fires": cert_fires, **fb}
        print("[certificate] control=%s n_test=%d prev=%.3f freq_cert_auroc=%.3f fires=%s"
              % (cname, n_te, prev, fb["certificate_auroc"], cert_fires), flush=True)
        if cert_fires and chosen is None:
            chosen = (cname, F_tr, F_te, fb)

    results = {"certificates_by_control": certs}

    if chosen is None:
        summary = {
            "dataset": "CoDEx-S triple classification (Safavi & Koutra 2020)",
            "verdict": "SPLIT_NOT_FREQUENCY_BLIND",
            "verdict_msg": ("No fairness control drove the frequency baseline to chance "
                            "(all certificate AUROC outside [%.2f,%.2f]); the structural race "
                            "is NOT trustworthy on this dataset -- report the split failure, not a gate win."
                            % (FREQ_CHANCE_LO, FREQ_CHANCE_HI)),
            "results": results,
            "elapsed_s": time.time() - t0,
        }
        write_metrics(summary)
        print(json.dumps(summary, indent=2), flush=True)
        return

    cname, F_tr, F_te, fb = chosen
    yte = F_te["y"]; ytr = F_tr["y"]
    prevalence = float(yte.mean())

    def ev(score):
        return {"auroc": auroc(yte, score), "auprc": average_precision(yte, score)}

    arms = {}
    arms["chance_naive"] = {"auroc": 0.5, "auprc": prevalence}
    arms["frequency_baseline_degree_freq"] = {"auroc": fb["freq_logistic_auroc"],
                                              "auprc": average_precision(yte, logistic_score(
        np.column_stack([F_te[f] for f in FREQ_FEATS]),
        *logistic_fit(np.column_stack([F_tr[f] for f in FREQ_FEATS]), ytr)))}

    # single structural arms (parameter-free; eval directly on test)
    struct_single = {f: ev(F_te[f]) for f in STRUCT_FEATS}
    arms["structural_singles"] = struct_single
    best_struct_name = max(struct_single.items(), key=lambda kv: kv[1]["auroc"])[0]
    arms["best_single_structural"] = {"name": best_struct_name, **struct_single[best_struct_name]}

    # parameter-free brain-faithful conjunction gate: product of percentile-ranks
    gate = pct_rank(F_te["plausibility"]) * pct_rank(F_te["schema_fit"]) * pct_rank(F_te["recurrence"])
    arms["brain_faithful_gate_parameterfree"] = ev(gate)

    # learned-logistic over the 3 structural signals (fit valid, eval test)
    Gtr = np.column_stack([F_tr[f] for f in STRUCT_FEATS])
    Gte = np.column_stack([F_te[f] for f in STRUCT_FEATS])
    wg = logistic_fit(Gtr, ytr)
    arms["learned_logistic_structural"] = ev(logistic_score(Gte, *wg))

    # combo: structural + frequency (does structure ADD lift over frequency?)
    Atr = np.column_stack([F_tr[f] for f in STRUCT_FEATS + FREQ_FEATS])
    Ate = np.column_stack([F_te[f] for f in STRUCT_FEATS + FREQ_FEATS])
    wa = logistic_fit(Atr, ytr)
    arms["combo_structural_plus_frequency"] = ev(logistic_score(Ate, *wa))

    # ARMS-MUST-DIFFER (META_RULE_AF) sanity: structural single arms must not be bit-identical
    import hashlib
    digs = {f: hashlib.sha256(F_te[f].tobytes()).hexdigest() for f in STRUCT_FEATS}
    assert len(set(digs.values())) == len(digs), "META_RULE_AF: structural signals bit-identical"

    # ---- verdict ----
    struct_best_auroc = max(arms["best_single_structural"]["auroc"],
                            arms["learned_logistic_structural"]["auroc"],
                            arms["brain_faithful_gate_parameterfree"]["auroc"])
    freq_auroc = fb["freq_logistic_auroc"]
    cert_auroc = fb["certificate_auroc"]
    margin_vs_freq = struct_best_auroc - freq_auroc
    margin_vs_chance = struct_best_auroc - 0.5
    combo_lift = arms["combo_structural_plus_frequency"]["auroc"] - freq_auroc

    cert_fires = (FREQ_CHANCE_LO <= cert_auroc <= FREQ_CHANCE_HI)
    # HARD-PASS: structure DECISIVELY beats freq-matched baseline + chance on novel claim-validity
    hard_pass = cert_fires and (struct_best_auroc >= 0.60) and (margin_vs_freq >= 0.05) and (margin_vs_chance >= 0.07)
    # HARD-FAIL: structure at/near chance even here (genuine, brain-consistent bound)
    hard_fail = cert_fires and (struct_best_auroc <= 0.55)
    if not cert_fires:
        verdict = "SPLIT_NOT_FREQUENCY_BLIND"
    elif hard_pass:
        verdict = "HARD_PASS"
    elif hard_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE"

    summary = {
        "dataset": "CoDEx-S triple classification (Safavi & Koutra, EMNLP 2020) -- human-verified hard negatives",
        "chosen_control": cname,
        "n_test": len(yte), "test_prevalence": prevalence,
        "config": {"k_dim": K_DIM, "epochs": EPOCHS, "tau": TAU, "seed": SEED,
                   "freq_chance_band": [FREQ_CHANCE_LO, FREQ_CHANCE_HI]},
        "fairness_certificate": {
            "control_used": cname,
            "frequency_baseline_certificate_auroc": cert_auroc,
            "freq_logistic_auroc": fb["freq_logistic_auroc"],
            "freq_single_best_auroc": fb["freq_single_best_auroc"],
            "certificate_fires_near_chance": cert_fires,
            "band": [FREQ_CHANCE_LO, FREQ_CHANCE_HI],
        },
        "arms": arms,
        "decisive": {
            "structural_best_auroc": struct_best_auroc,
            "frequency_baseline_auroc": freq_auroc,
            "margin_structural_vs_frequency": margin_vs_freq,
            "margin_structural_vs_chance": margin_vs_chance,
            "combo_lift_vs_frequency": combo_lift,
        },
        "prereg_bands": {
            "HARD_PASS": "certificate fires AND struct_best AUROC>=0.60 AND (struct-freq)>=0.05 AND (struct-0.5)>=0.07",
            "HARD_FAIL": "certificate fires AND struct_best AUROC<=0.55 (structure at/near chance even here)",
            "MIDDLE": "certificate fires AND structure beats chance but not decisively over freq",
            "SPLIT_NOT_FREQUENCY_BLIND": "no control drove freq baseline into [0.45,0.55] -> gate result untrustworthy",
        },
        "verdict": verdict,
        "honesty_notes": [
            "CoDEx hard negatives are KGE-PLAUSIBLE by construction -> additive_map plausibility/surprise is at a genuine disadvantage; schema_fit + recurrence are different signal families.",
            "P(structural wins) pre-registered ~0.30; a clean HARD_FAIL with the freq-at-chance certificate firing is a DECISIVE, valuable result (real knowledge-vetting is frequency-explained OR our structural signals do not carry claim-validity signal).",
            "all test entities are seen in train (transductive) -> no cold-start disadvantage; novelty = held-out (h,r,t) + frequency-blind split, not unseen entities.",
            "learned arms fit on CoDEx VALID split (same fairness control), evaluated on TEST split -> no test-label leakage.",
        ],
        "elapsed_s": time.time() - t0,
    }
    write_metrics(summary)
    print(json.dumps(summary, indent=2), flush=True)


def write_metrics(summary):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = RESULTS_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    os.replace(tmp, RESULTS_PATH)


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
