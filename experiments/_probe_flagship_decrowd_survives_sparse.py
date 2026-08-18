"""FLAGSHIP de-risk probe (lull shippable): does CERT 591's projection DECROWDING survive a3f473dd's SPARSIFICATION?
The make-or-break for sparse-projected-KV. If projected-THEN-sparse keys stay MORE decrowded (lower keysep) than raw-sparse
keys on the SAME held-out set -> composition genuine -> green-light the full flagship. If sparse washes it out -> MM-negative.
Reuses CERT 591 funcs VERBATIM (C1: make_facts/encode/train_contrastive/keysep/_np_norm) + a3f473dd-style top-k sparsify.
Apples-to-apples (Skunkworks guard): both keyseps on the SAME held-out keys, same run. pythia-160m (CPU). ASCII.
"""
import sys, os
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
ENCODER = "EleutherAI/pythia-160m"; M = 800; PROJ_DIM = 128; HELDOUT_FRAC = 0.25; TRAIN_STEPS = 200
_ADJ = "red blue swift quiet ancient modern silver golden hidden northern rapid silent hollow bright frozen molten crimson azure verdant amber".split()
_NOUN = "falcon river engine archive bridge reactor delta harbor summit forge canyon beacon orchard meadow glacier tower lagoon prairie quarry vault".split()
_VALW = "helium cobalt basalt cedar quartz copper marble willow granite saffron indigo cypress bronze jasper walnut".split()
_PROPS = ["founded in", "powered by", "located near", "awarded for", "merged with"]


def make_facts(M):                                          # VERBATIM CERT 591
    keys, vq = [], []
    for i in range(M):
        ent = "the %s %s" % (_ADJ[i % len(_ADJ)], _NOUN[(i // len(_ADJ)) % len(_NOUN)])
        prop = _PROPS[i % len(_PROPS)]; value = "%s %d" % (_VALW[i % len(_VALW)], 1000 + i)
        keys.append("%s was %s %s." % (ent, prop, value)); vq.append("Which one was %s %s?" % (prop, value))
    return keys, vq


def _np_norm(X):                                            # VERBATIM CERT 591
    return (X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def recall_at(Qn, Kn, chunk=256):                           # VERBATIM CERT 591 (cue->key nearest@1)
    cor = 0
    for i in range(0, len(Qn), chunk):
        cor += int((np.argmax(Qn[i:i + chunk] @ Kn.T, axis=1) == np.arange(i, min(i + chunk, len(Qn)))).sum())
    return cor / len(Qn)


def keysep(Kn, sample=512, g=None):                         # VERBATIM CERT 591 (median of max off-diag key-sim; LOWER = more decrowded)
    n = len(Kn); idx = (g.permutation(n)[:min(sample, n)] if g is not None else np.arange(min(sample, n)))
    S = Kn[idx]; G = S @ Kn.T
    for r, j in enumerate(idx): G[r, j] = -2.0
    return float(np.median(G.max(1)))


def sparsify(X, f):                                         # a3f473dd-style: top-k magnitude -> sign-binarize -> bipolar k-of-d
    k = max(1, int(f * X.shape[1])); out = np.zeros_like(X, np.float32)
    idx = np.argpartition(np.abs(X), -k, axis=1)[:, -k:]
    np.put_along_axis(out, idx, np.sign(np.take_along_axis(X, idx, axis=1)).astype(np.float32), axis=1)
    return out


import torch, torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer
DEV = torch.device("cpu")


def encode(texts):                                         # VERBATIM CERT 591 (mean-pooled)
    tok = AutoTokenizer.from_pretrained(ENCODER)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    mdl = AutoModel.from_pretrained(ENCODER, torch_dtype=torch.float32).to(DEV).eval(); out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=48).to(DEV)
        with torch.no_grad(): h = mdl(**t).last_hidden_state
        m = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * m).sum(1) / m.sum(1).clamp(min=1)).float().cpu().numpy())
    del mdl; return np.concatenate(out, 0).astype(np.float32)


def train_contrastive(K_tr, Q_tr, d, steps, seed):         # VERBATIM CERT 591 (InfoNCE align + key-uniformity de-crowd)
    torch.manual_seed(seed); K = torch.tensor(K_tr); Q = torch.tensor(Q_tr); n, D = K.shape
    W = (torch.randn(D, d) * (1.0 / D ** 0.5)).requires_grad_(True); opt = torch.optim.Adam([W], lr=1e-2); bs = min(256, n)
    for step in range(steps):
        idx = torch.randperm(n)[:bs]; tgt = torch.arange(len(idx))
        kp = F.normalize(K[idx] @ W, dim=1); qp = F.normalize(Q[idx] @ W, dim=1)
        lq = (qp @ kp.T) / 0.07; lk = (kp @ qp.T) / 0.07
        loss = 0.5 * (F.cross_entropy(lq, tgt) + F.cross_entropy(lk, tgt)) + 0.5 * ((kp @ kp.T) - torch.eye(len(idx)) * 2.0).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return W.detach().cpu().numpy().astype(np.float32)


def recall_arm(Kn, Qn):                                     # cue->key nearest@1 (the chain-grade metric)
    return recall_at(_np_norm(Qn), _np_norm(Kn))


if __name__ == "__main__":
    g = np.random.default_rng(0); keys, cues = make_facts(M); print("[probe] encoding %d facts on %s (CPU)..." % (M, ENCODER), flush=True)
    K = encode(keys); Q = encode(cues)
    nh = int(M * HELDOUT_FRAC); Ktr, Qtr = K[:-nh], Q[:-nh]; Kho, Qho = K[-nh:], Q[-nh:]         # held-out (projection never trained on)
    print("[probe] training CERT591 projection (D=%d -> d=%d, %d steps)..." % (K.shape[1], PROJ_DIM, TRAIN_STEPS), flush=True)
    W = train_contrastive(Ktr, Qtr, PROJ_DIM, TRAIN_STEPS, 0)
    Kraw, Qraw = Kho, Qho; Kproj, Qproj = Kho @ W, Qho @ W
    ks_raw = keysep(_np_norm(Kraw)); ks_proj = keysep(_np_norm(Kproj))
    print("\n[DECROWD-SURVIVES-SPARSE]  keysep LOWER=decrowded | RECALL (cue->key @1) HIGHER=better -- the CHAIN-GRADE metric")
    print("  DENSE:  keysep raw=%.4f proj=%.4f (decrowd %.4f) | RECALL Arm2(dense-proj)=%.3f  raw-dense=%.3f" % (
        ks_raw, ks_proj, ks_raw - ks_proj, recall_arm(Kproj, Qproj), recall_arm(Kraw, Qraw)))
    print("  3-ARM RECALL per f: Arm1(proj-sparse) vs Arm3(raw-sparse) -- chain-grade needs Arm1 >= Arm3 + 0.20")
    for f in [0.05, 0.10, 0.20]:
        Kproj_sp, Qproj_sp = sparsify(Kproj, f), sparsify(Qproj, f)
        Kraw_sp, Qraw_sp = sparsify(Kraw, f), sparsify(Qraw, f)
        r1 = recall_arm(Kproj_sp, Qproj_sp); r3 = recall_arm(Kraw_sp, Qraw_sp)
        ks1 = keysep(_np_norm(Kproj_sp)); ks3 = keysep(_np_norm(Kraw_sp))
        print("  f=%.2f: RECALL Arm1(proj-sparse)=%.3f  Arm3(raw-sparse)=%.3f  (margin %+.3f)  | keysep proj-sp=%.3f raw-sp=%.3f  | Arm1>=Arm3+0.20=%s" % (
            f, r1, r3, r1 - r3, ks1, ks3, r1 >= r3 + 0.20))
    print("\n[VERDICT] Arm1(proj-sparse) >= Arm3(raw-sparse)+0.20 on RECALL -> flagship salvageable; else -> top-k-sparsify destroys it -> MM-negative or needs different sparse-encode")
