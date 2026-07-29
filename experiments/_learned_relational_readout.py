"""Shared learned-relational-readout probe: fit + leak-proof eval (2026-07-28).

Extracted from `experiments/diag_readout_limit_probe_v1.py` (the diagnostic that
first measured the readout-limit finding, seed_7 only, single-shot) so the
mechanism has ONE implementation reusable by:
  - `experiments/exp_relational_readout_promote_v1.py` (this promotion cell:
    leak-proof, multi-seed, arbitrary-ckpt)
  - `experiments/eval_battery_relational_cloze_v7.py` (already independently
    re-implements a similar bilinear-fit inline per its own docstring/comments
    referencing diag_readout_limit_probe_v1 -- a WIRE-consolidation candidate
    flagged for Skunkworks/Director at land-time, not done in this pass to keep
    this cell's diff bounded).

Two probe families (both linear maps over frozen reps -- deliberately NOT a
full nonlinear readout; see module docstring of diag_readout_limit_probe_v1.py
for the representation-limit vs readout-limit framing this measures):
  PROBE_DIAG     : diagonal-reweighted cosine (per-dim reweighting).
  PROBE_BILINEAR : low-rank (d->r) linear projection then cosine.

All RNG is seeded via explicit integer seeds (torch.manual_seed / np.random.
default_rng) -- NEVER via built-in hash() or list(set()) ordering (PROT-023 /
META_RULE F.5). Anchor/pair ordering is done via sorted() on int ids.
"""
from __future__ import annotations

import numpy as np
import torch


def z1_rows(mat: np.ndarray) -> np.ndarray:
    """Row-wise z-normalization; degenerate (near-zero std) rows pass through mean-centered."""
    mu = mat.mean(axis=1, keepdims=True)
    sd = mat.std(axis=1, keepdims=True)
    return np.where(sd > 1e-12, (mat - mu) / (sd + 1e-8), mat - mu)


def build_train_pairs(split, adj, deg, have_text, seed, n_anchors=2000, max_pos=8):
    """Leak-proof TRAIN-TRAIN positive/negative pair builder (degree-matched negatives).

    Both endpoints of every pair are guaranteed inside split['train_eval_idx'];
    the self-test asserts below raise (not warn) on any leak. seed is a FIXED
    int (never hash()-derived) so pair sampling is reproducible across
    processes (PROT-023 / META_RULE F.5).
    """
    train_idx = split["train_eval_idx"]
    train_set = set(int(x) for x in train_idx.tolist())
    deg_bin = {}
    for t in train_idx.tolist():
        deg_bin.setdefault(int(deg[t]), []).append(t)
    max_deg = int(deg[train_idx].max()) if train_idx.shape[0] else 0
    rng = np.random.default_rng(seed + 501)
    anchors = [int(i) for i in train_idx.tolist() if have_text[i]]
    rng.shuffle(anchors)
    anchors = anchors[:n_anchors]
    pi, pj, lab = [], [], []
    for a in anchors:
        pos = sorted(j for j in adj[a] if j in train_set and have_text[j] and j != a)
        if not pos:
            continue
        pos = pos[:max_pos]
        exclude = set(adj[a]) | {a}
        negs, used = [], set()
        for p in pos:
            dp = int(deg[p])
            picked = -1
            for tol in range(0, max_deg + 1):
                cands = []
                for dd in ((dp,) if tol == 0 else (dp - tol, dp + tol)):
                    if dd in deg_bin:
                        cands.extend(deg_bin[dd])
                cands = [c for c in cands if c not in exclude and c not in used and have_text[c]]
                if cands:
                    picked = cands[int(rng.integers(0, len(cands)))]
                    break
            if picked < 0:
                continue
            negs.append(picked)
            used.add(picked)
        for p in pos:
            pi.append(a); pj.append(p); lab.append(1.0)
        for n in negs:
            pi.append(a); pj.append(n); lab.append(0.0)
    pi = np.asarray(pi, dtype=np.int64)
    pj = np.asarray(pj, dtype=np.int64)
    lab = np.asarray(lab, dtype=np.float32)
    held_set = set(int(x) for x in split["held_idx"].tolist())
    endpoints = set(pi.tolist()) | set(pj.tolist())
    assert endpoints.issubset(train_set), "LEAK: a fit-pair endpoint is outside train_eval_idx"
    assert endpoints.isdisjoint(held_set), "LEAK: a fit-pair endpoint is a held-out concept"
    return pi, pj, lab, dict(n_anchors_used=len(anchors), n_pairs=int(lab.shape[0]),
                             n_pos=int(lab.sum()), n_neg=int((1 - lab).sum()),
                             leak_check="PASS_disjoint_from_held")


def fit_diag_probe(text_reps, pi, pj, lab, steps=500, lr=0.03, weight_decay=1e-2, seed=0):
    """Diagonal-weighted cosine: score = sum_k w_k * x_k * y_k. TRAIN-TRAIN only."""
    torch.manual_seed(seed)
    d = text_reps.shape[1]
    X = torch.from_numpy(text_reps).float()
    w = torch.ones(d, requires_grad=True)
    opt = torch.optim.Adam([w], lr=lr, weight_decay=weight_decay)
    pi_t, pj_t, lab_t = torch.from_numpy(pi).long(), torch.from_numpy(pj).long(), torch.from_numpy(lab)
    xi, xj = X[pi_t], X[pj_t]
    last_loss = float("nan")
    for _ in range(steps):
        opt.zero_grad()
        score = (xi * xj * w).sum(dim=1)
        loss = torch.nn.functional.binary_cross_entropy_with_logits(score, lab_t)
        loss.backward()
        opt.step()
        last_loss = float(loss.detach())
    if not np.isfinite(last_loss):
        raise FloatingPointError("PROBE_DIAG training diverged (non-finite loss)")
    return w.detach().numpy(), last_loss


def fit_bilinear_probe(text_reps, pi, pj, lab, r=32, steps=500, lr=0.01, weight_decay=5e-2, seed=0):
    """Low-rank linear projection d->r then cosine. TRAIN-TRAIN only. r=32 default (not 128)
    + weight_decay because n_pairs is small relative to r*d params -- overparameterized bilinear
    would overfit fit pairs; this is the fair-test guard against that failure mode."""
    torch.manual_seed(seed)
    d = text_reps.shape[1]
    X = torch.from_numpy(text_reps).float()
    P = torch.nn.Linear(d, r, bias=False)
    torch.nn.init.orthogonal_(P.weight)
    opt = torch.optim.Adam(P.parameters(), lr=lr, weight_decay=weight_decay)
    pi_t, pj_t, lab_t = torch.from_numpy(pi).long(), torch.from_numpy(pj).long(), torch.from_numpy(lab)
    xi_raw, xj_raw = X[pi_t], X[pj_t]
    last_loss = float("nan")
    for _ in range(steps):
        opt.zero_grad()
        xi = P(xi_raw); xj = P(xj_raw)
        xi = xi / (xi.norm(dim=1, keepdim=True) + 1e-8)
        xj = xj / (xj.norm(dim=1, keepdim=True) + 1e-8)
        score = (xi * xj).sum(dim=1) * 4.0
        loss = torch.nn.functional.binary_cross_entropy_with_logits(score, lab_t)
        loss.backward()
        opt.step()
        last_loss = float(loss.detach())
    if not np.isfinite(last_loss):
        raise FloatingPointError("PROBE_BILINEAR training diverged (non-finite loss)")
    return P.weight.detach().numpy(), last_loss


def eval_relational_all_arms(text_reps, ground, split, adj, deg, have_text, w_diag, P_bilinear,
                             seed, auc_fn):
    """Held-out-NEW relational eval, all arms paired on the SAME candidate sets per query.

    auc_fn: injected AUC helper (exp_scale_meaning_learn_arc_heldout_v2._auc_from_scores) so this
    module has no import-time dependency on that experiment file.
    """
    held = split["held_idx"]
    train_pool = split["train_eval_idx"]
    train_set = set(int(x) for x in train_pool.tolist())
    deg_bin = {}
    for t in train_pool.tolist():
        deg_bin.setdefault(int(deg[t]), []).append(t)
    max_deg = int(deg[train_pool].max()) if train_pool.shape[0] else 0
    rng = np.random.default_rng(seed + 909)
    elig_q = [int(h) for h in held.tolist() if have_text[h]]

    if elig_q:
        eq = np.array(sorted(elig_q), dtype=np.int64)
        perm = rng.permutation(eq.shape[0])
        text_sh = text_reps.copy()
        text_sh[eq] = text_reps[eq][perm]
    else:
        text_sh = text_reps

    arm_names = ["BASELINE_COSINE", "PROBE_DIAG", "PROBE_BILINEAR", "FUSE_ZAVG_REF",
                 "SHUFFLE_CONTROL", "POPULARITY_CONTROL"]
    out = {a: [] for a in arm_names}
    per_query = []
    n_used = 0
    for h in elig_q:
        pos_neigh = sorted(j for j in adj[h] if j in train_set and have_text[j])
        if not pos_neigh:
            continue
        pos_neigh = pos_neigh[:8]
        exclude = set(adj[h]) | {h}
        negs, used, ok = [], set(), True
        for p in pos_neigh:
            dp = int(deg[p])
            picked = -1
            for tol in range(0, max_deg + 1):
                cands = []
                for dd in ((dp,) if tol == 0 else (dp - tol, dp + tol)):
                    if dd in deg_bin:
                        cands.extend(deg_bin[dd])
                cands = [c for c in cands if c not in exclude and c not in used and have_text[c]]
                if cands:
                    picked = cands[int(rng.integers(0, len(cands)))]
                    break
            if picked < 0:
                ok = False
                break
            negs.append(picked)
            used.add(picked)
        if not ok or not negs:
            continue
        n_used += 1
        cand = np.array(pos_neigh + negs, dtype=np.int64)
        posm = np.array([True] * len(pos_neigh) + [False] * len(negs))

        ct = text_reps[h] @ text_reps[cand].T
        cd = (text_reps[h][None, :] * text_reps[cand] * w_diag[None, :]).sum(axis=1)
        ph = P_bilinear @ text_reps[h]
        ph = ph / (np.linalg.norm(ph) + 1e-8)
        pc = text_reps[cand] @ P_bilinear.T
        pc = pc / (np.linalg.norm(pc, axis=1, keepdims=True) + 1e-8)
        cb = pc @ ph
        cg = ground[h] @ ground[cand].T
        czavg = 0.5 * (z1_rows(cg[None, :])[0] + z1_rows(ct[None, :])[0])
        cs = text_sh[h] @ text_reps[cand].T
        pop = np.log1p(deg[cand].astype(np.float64))

        per_q_ok = True
        per_q = {}
        for a, sc in (("BASELINE_COSINE", ct), ("PROBE_DIAG", cd), ("PROBE_BILINEAR", cb),
                      ("FUSE_ZAVG_REF", czavg), ("SHUFFLE_CONTROL", cs), ("POPULARITY_CONTROL", pop)):
            au = auc_fn(sc, posm)
            if au is not None:
                out[a].append(au)
                per_q[a] = au
            else:
                per_q_ok = False
        if per_q_ok:
            per_query.append(per_q)
    res = {a: (float(np.mean(v)) if v else None) for a, v in out.items()}
    res["_n_query"] = n_used
    return res, per_query


class AttnBilinearReadout(torch.nn.Module):
    """Brain-faithful structure-preserving readout (ledger row 4, 2026-07-29;
    notes/drill_brain_faithful_comprehension_readout.md). Learned head on a FROZEN encoder's
    per-token hidden states -- NOT a retrain of the encoder. Two components:

    (a) Query-conditioned ATTENTION POOL over per-token hidden states H [N,L,D] with pad mask
        M [N,L] (True=pad; matches diag_comprehension_readout_sweep_v1.readout_mean_pool's mask
        convention). Mirrors that module's AttnPool (nn.Linear(d,1) score + masked softmax +
        weighted sum) -- reimplemented inline here (not imported) to avoid dragging that
        diagnostic's heavy eval_battery_relational_cloze_v7/LOOP5 import chain into this shared,
        lightweight probe module; same mechanism, credited not duplicated-as-novel. This replaces
        order-blind mean-pool with a content/query-dependent weighting -- the gain-modulated-
        readout analog (Reynolds & Heeger attentional gain).
    (b) Explicit LOW-RANK QUADRATIC interaction term between the two attention-pooled segments
        (e.g. clause1 vs clause2): P: d->r (the SAME low-rank machinery as fit_bilinear_probe
        above, r=32 default) then an ELEMENTWISE PRODUCT P(u1)*P(u2) -- a genuinely multiplicative
        cross-feature between the two inputs, not two independent linear projections. This is the
        mixed-selectivity substitute (Rigotti/Fusi 2013): the nonlinear interaction lives in the
        FEATURE CONSTRUCTION, so the downstream classifier on [u1, u2, interaction] can stay
        linear and still express an XOR-class (order/relation) decision.

    Trained END-TO-END (attention weights + low-rank projection + final linear classifier) via a
    single class-weighted cross-entropy loss -- same TRAIN-only leak-proof discipline as
    fit_bilinear_probe/fit_diag_probe above (train_reps/labels only; eval is forward-only).
    """

    def __init__(self, d_model: int, r: int = 32, seed: int = 0):
        super().__init__()
        torch.manual_seed(seed)
        self.d_model = d_model
        self.r = r
        self.w_attn = torch.nn.Linear(d_model, 1)          # attention-pool score head
        self.P = torch.nn.Linear(d_model, r, bias=False)   # low-rank projection for interaction term
        torch.nn.init.orthogonal_(self.P.weight)
        self.classifier = torch.nn.Linear(2 * d_model + r, 2)

    def attn_pool(self, H: torch.Tensor, M: torch.Tensor) -> torch.Tensor:
        """H: [N,L,D] float; M: [N,L] bool, True=PAD (matches readout_mean_pool convention)."""
        scores = self.w_attn(H).squeeze(-1)
        scores = scores.masked_fill(M, float("-inf"))
        a = torch.softmax(scores, dim=1)
        pooled = (a.unsqueeze(-1) * H).sum(dim=1)
        return pooled

    def features(self, H1, M1, H2, M2):
        u1 = self.attn_pool(H1, M1)
        u2 = self.attn_pool(H2, M2)
        p1 = self.P(u1)
        p2 = self.P(u2)
        interaction = p1 * p2
        return torch.cat([u1, u2, interaction], dim=1)

    def forward(self, H1, M1, H2, M2):
        feat = self.features(H1, M1, H2, M2)
        return self.classifier(feat), feat


def fit_attn_bilinear_readout(d_model, H1_tr, M1_tr, H2_tr, M2_tr, y_train, r=32, epochs=15,
                               lr=0.01, wd=1e-3, seed=0, random_init=False):
    """TRAIN-only fit (both endpoints of every training pair are TRAIN items by construction of
    the caller's split). random_init=True: build the identical structure at its
    torch.manual_seed(seed) initialization and take ZERO optimizer steps -- the MANDATORY
    structure-vs-learning control (per the frontier-scoping doc's random-init discipline)."""
    mod = AttnBilinearReadout(d_model, r=r, seed=seed)
    if random_init:
        mod.eval()
        return mod
    mod.train()
    opt = torch.optim.Adam(mod.parameters(), lr=lr, weight_decay=wd)
    y = y_train if torch.is_tensor(y_train) else torch.as_tensor(y_train, dtype=torch.long)
    counts = torch.clamp(torch.bincount(y, minlength=2).float(), min=1.0)
    class_weight = counts.sum() / (2 * counts)
    last_loss = float("nan")
    for _ in range(epochs):
        opt.zero_grad()
        logits, _ = mod(H1_tr, M1_tr, H2_tr, M2_tr)
        loss = torch.nn.functional.cross_entropy(logits, y, weight=class_weight)
        loss.backward()
        opt.step()
        last_loss = float(loss.detach())
    if not np.isfinite(last_loss):
        raise FloatingPointError("AttnBilinearReadout training diverged (non-finite loss)")
    mod.eval()
    return mod


def score_attn_bilinear_arm(name, mod, H1_tr, M1_tr, H2_tr, M2_tr, y_train,
                            H1_ec, M1_ec, H2_ec, M2_ec, H1_es, M1_es, H2_es, M2_es, y_eval,
                            margin_thresh, coherent_floor, sanity_margin):
    """Same output-dict schema as diag_order_critical_comprehension_calib_v1.score_readout_arm so
    this arm plugs into the SAME verdict logic as every other readout arm in this arc (margin,
    comprehension_specific, train_sanity decoder-collapse gate). y_train/y_eval: numpy int arrays."""
    with torch.no_grad():
        pred_tr = mod(H1_tr, M1_tr, H2_tr, M2_tr)[0].argmax(dim=1).numpy()
        pred_ec = mod(H1_ec, M1_ec, H2_ec, M2_ec)[0].argmax(dim=1).numpy()
        pred_es = mod(H1_es, M1_es, H2_es, M2_es)[0].argmax(dim=1).numpy()

    def _bal_acc(pred, y):
        recalls = []
        for c in (0, 1):
            mask = (y == c)
            if mask.sum() > 0:
                recalls.append(float((pred[mask] == c).mean()))
        return float(np.mean(recalls)) if recalls else 0.0

    train_bal = _bal_acc(pred_tr, y_train)
    sanity = dict(train_balanced_acc=train_bal, chance=0.5,
                  train_beats_chance=bool(train_bal >= 0.5 + sanity_margin))
    coh_acc = float((pred_ec == y_eval).mean())
    coh_bal = _bal_acc(pred_ec, y_eval)
    scr_acc = float((pred_es == y_eval).mean())
    scr_bal = _bal_acc(pred_es, y_eval)
    margin = coh_acc - scr_acc
    comprehension_specific = bool(sanity["train_beats_chance"] and coh_acc >= coherent_floor
                                   and margin >= margin_thresh)
    return dict(name=name, train_sanity=sanity, coherent_acc=coh_acc, coherent_balanced_acc=coh_bal,
                scrambled_acc=scr_acc, scrambled_balanced_acc=scr_bal, margin=margin,
                n_eval=int(len(y_eval)), comprehension_specific=comprehension_specific)


def arms_must_differ_hashes(arms_outputs: dict) -> dict:
    """META_RULE_AF hash-test: assert arm score arrays are not bit-identical. Returns digests to log."""
    import hashlib
    digests = {}
    for name, out in arms_outputs.items():
        arr = np.asarray(out, dtype=np.float64)
        digests[name] = hashlib.sha256(arr.tobytes()).hexdigest()
    names = sorted(digests)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            assert digests[a] != digests[b], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical (hash=%s)"
                % (a, b, digests[a]))
    return digests
