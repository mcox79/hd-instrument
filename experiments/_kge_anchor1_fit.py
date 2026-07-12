"""Anchor-1 KGE fit recipe (Phase-2 lever 1-2): cross-entropy (self-adversarial) loss + N3 regularization +
reciprocal relations + MINIBATCH SGD. Drop-in replacement for exp_course_c_operator's full-batch margin-rank
fit_transe_coords -- same (X coords, D relation displacement) output geometry, same downstream FPE-kernel
readout, but fit with the more sample-efficient objective the KGE literature (Sun et al. 2019 RotatE
self-adversarial; Lacroix et al. 2018 N3 + reciprocal) shows buys +25-42% relative MRR holding architecture
fixed.

WHY this is the capacity lever. The original fit_transe_coords is FULL-BATCH margin-ranking: `epochs` gradient
steps TOTAL regardless of |edges|, and the margin loss only pushes gold margin-closer than KGE_NEG=10 random
negatives. At N=25752 entities / ~485k edges that is (a) severely under-trained (600 steps) and (b) weak
ranking pressure (gold need only beat 10 of 25751 competitors). This recipe fixes BOTH: minibatch SGD gives
|edges|/bs steps per epoch, and the self-adversarial CE loss with n_neg hard-weighted negatives drives gold
toward rank-1 out of N. Reciprocal augmentation doubles the training signal per entity (Lacroix). N3 is the
norm-cubed prior that the KGE literature ties to generalization on sparse graphs.

ASCII-only. Returns (X, D_forward) on the given device; D_forward = the first n_rel relation displacements
(reciprocal inverse-relation rows are used ONLY to enrich the fit, never exposed to the forward readout)."""

import os
import sys

import numpy as np
import torch
import torch.nn.functional as F

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._fit_checkpoint import edges_hash, restore_into  # noqa: E402

# ---- Anchor-1 defaults (pre-registered; the ladder cell sweeps epochs/k/dim, holds these fixed) ----
A1_LR = 0.05
A1_GAMMA = 9.0            # score margin gamma: s(h,r,t) = gamma - ||X_h + D_r - X_t|| (RotatE-style logit)
A1_N_NEG = 64            # negatives per positive (self-adversarial weighted)
A1_ADV_TEMP = 1.0       # self-adversarial temperature alpha (Sun et al. 2019 eq.)
A1_N3_LAMBDA = 5e-4     # N3 (Lacroix) regularization weight on |emb|^3
A1_BATCH = 8192         # minibatch size (step count = |aug_edges| / bs per epoch)


def fit_kge_anchor1(train_edges, N, n_rel, k, device, seed, epochs,
                    transductive_extra=None, reciprocal=True,
                    lr=A1_LR, gamma=A1_GAMMA, n_neg=A1_N_NEG, adv_temp=A1_ADV_TEMP,
                    n3_lambda=A1_N3_LAMBDA, batch_size=A1_BATCH, neg_chunk=None,
                    ckpt=None, stop_after_epochs=None):
    """Fit X (N,k), D (n_rel,k) with CE self-adversarial loss + N3 + reciprocal augmentation, minibatch SGD.

    train_edges: (E,3) int64 [h, r, t]. transductive_extra: optional (E2,3) held-out edges folded into the fit
    (the ORACLE arm passes hold here). reciprocal: augment with inverse relations for the fit only.
    Returns X.detach() (N,k), D_forward.detach() (n_rel,k)."""
    g = torch.Generator(device="cpu").manual_seed(seed * 7919 + 11)
    ed = train_edges
    if transductive_extra is not None and transductive_extra.shape[0] > 0:
        ed = np.concatenate([train_edges, transductive_extra], axis=0)
    n_rel_eff = n_rel
    if reciprocal:
        inv = ed[:, [2, 1, 0]].copy()
        inv[:, 1] = inv[:, 1] + n_rel                 # inverse-relation ids live in [n_rel, 2*n_rel)
        ed = np.concatenate([ed, inv], axis=0)
        n_rel_eff = 2 * n_rel

    X = (torch.randn(N, k, generator=g) * 0.1).to(device).requires_grad_(True)
    D = (torch.randn(n_rel_eff, k, generator=g) * 0.1).to(device).requires_grad_(True)
    opt = torch.optim.Adam([X, D], lr=lr)

    h_all = torch.from_numpy(ed[:, 0]).long().to(device)
    r_all = torch.from_numpy(ed[:, 1]).long().to(device)
    t_all = torch.from_numpy(ed[:, 2]).long().to(device)
    E = h_all.shape[0]
    bs = min(batch_size, E)
    gperm = torch.Generator(device="cpu").manual_seed(seed * 13 + 1)
    gneg = torch.Generator(device="cpu").manual_seed(seed * 17 + 3)

    # DURABILITY: resume from a matching checkpoint (same config-fingerprint) instead of restarting.
    start_epoch = 0
    if ckpt is not None and ckpt.enabled():
        ckpt.set_fingerprint(dict(
            fn="additive", N=int(N), n_rel=int(n_rel), k=int(k), epochs=int(epochs), n_neg=int(n_neg),
            lr=float(lr), gamma=float(gamma), adv_temp=float(adv_temp), n3_lambda=float(n3_lambda),
            batch_size=int(bs), reciprocal=bool(reciprocal), seed=int(seed),
            split_hash=edges_hash(ed), device=str(device)))
        _ck = ckpt.try_load(device)
        if _ck is not None:
            start_epoch = restore_into(_ck, {"X": X, "D": D}, opt, {"gperm": gperm, "gneg": gneg}, device)

    for ep in range(start_epoch, epochs):
        perm = torch.randperm(E, generator=gperm)
        _last_loss = float("nan")
        for s in range(0, E, bs):
            bidx = perm[s:s + bs].to(device)
            hb = h_all[bidx]; rb = r_all[bidx]; tb = t_all[bidx]
            b = hb.shape[0]
            _is_last_batch = (s + bs >= E)
            pred = X[hb] + D[rb]                                    # (b, k)
            pos_d = torch.norm(pred - X[tb], dim=1)                 # (b,)
            pos_score = gamma - pos_d                               # (b,) logit, higher = better
            neg_t = torch.randint(0, N, (b, n_neg), generator=gneg).to(device)  # SAME draw as pre-fix
            if neg_chunk is None or neg_chunk >= n_neg:
                # ORIGINAL single-shot path (bit-identical to pre-fix; default for all existing callers).
                neg_d = torch.norm(pred.unsqueeze(1) - X[neg_t], dim=2)  # (b, n_neg)
                neg_score = gamma - neg_d                           # (b, n_neg)
                with torch.no_grad():
                    w = torch.softmax(adv_temp * neg_score, dim=1)  # self-adversarial weights (stop-grad)
                pos_loss = -F.logsigmoid(pos_score)                 # (b,)
                neg_loss = -(w * F.logsigmoid(-neg_score)).sum(dim=1)   # (b,)
                loss = (pos_loss + neg_loss).mean()
                if n3_lambda > 0.0:
                    reg = (X[hb].abs().pow(3).sum() + X[tb].abs().pow(3).sum()
                           + D[rb].abs().pow(3).sum()) / float(b)
                    loss = loss + n3_lambda * reg
                opt.zero_grad()
                loss.backward()
                opt.step()
                if ckpt is not None and ckpt.enabled() and _is_last_batch:
                    _last_loss = float((-F.logsigmoid(pos_score)).mean().detach())
            else:
                # MEMORY-CHUNKED path: bound the (b,n_neg,k) neg-scoring transient to (b,neg_chunk,k) via
                # per-block backward (grad accumulation). Numerically equivalent (backprop is linear); w is
                # stop-grad so it is precomputed over ALL negatives chunked. Effective batch is UNCHANGED.
                with torch.no_grad():
                    neg_score_ng = torch.empty((b, n_neg), device=device, dtype=pred.dtype)
                    for c0 in range(0, n_neg, neg_chunk):
                        c1 = min(c0 + neg_chunk, n_neg)
                        nd = torch.norm(pred.unsqueeze(1) - X[neg_t[:, c0:c1]], dim=2)
                        neg_score_ng[:, c0:c1] = gamma - nd
                    w = torch.softmax(adv_temp * neg_score_ng, dim=1)  # (b,n_neg) stop-grad
                opt.zero_grad()
                base = (-F.logsigmoid(pos_score)).mean()
                if n3_lambda > 0.0:
                    reg = (X[hb].abs().pow(3).sum() + X[tb].abs().pow(3).sum()
                           + D[rb].abs().pow(3).sum()) / float(b)
                    base = base + n3_lambda * reg
                base.backward(retain_graph=True)                   # pred subgraph retained for the neg blocks
                n_blocks = (n_neg + neg_chunk - 1) // neg_chunk
                done = 0
                for c0 in range(0, n_neg, neg_chunk):
                    c1 = min(c0 + neg_chunk, n_neg)
                    nd = torch.norm(pred.unsqueeze(1) - X[neg_t[:, c0:c1]], dim=2)  # (b,block)
                    ns = gamma - nd
                    lc = -(w[:, c0:c1] * F.logsigmoid(-ns)).sum(dim=1).mean()
                    done += 1
                    lc.backward(retain_graph=(done < n_blocks))    # free pred subgraph on the last block
                opt.step()
                if ckpt is not None and ckpt.enabled() and _is_last_batch:
                    _last_loss = float((-F.logsigmoid(pos_score)).mean().detach())
        # DURABILITY: periodic + final checkpoint (atomic) at the epoch boundary. Copies only; the trajectory
        # is unchanged whether or not checkpointing is enabled. Saved gperm/gneg states are exactly where an
        # uninterrupted run would be at the start of epoch (ep+1) -> resume reproduces the same trajectory.
        if ckpt is not None and ckpt.enabled():
            _do_stop = (stop_after_epochs is not None) and ((ep + 1) >= stop_after_epochs)
            if ((ep + 1) % ckpt.every == 0) or ((ep + 1) == epochs) or _do_stop:
                ckpt.save(ep + 1, {"X": X, "D": D}, opt,
                          {"gperm": gperm.get_state(), "gneg": gneg.get_state()})
                ckpt.write_progress(ep + 1, epochs, _last_loss)
            if _do_stop:
                break
    return X.detach(), D.detach()[:n_rel].contiguous()
