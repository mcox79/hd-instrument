"""FLAGSHIP sparse-projected-KV PROBE (whiten-before-topk) -- cell 1 of 2 per Research amendment-v4 prestage.

PURPOSE: does CERT 591's learned-projection DECROWDING survive a3f473dd's SPARSIFICATION? The de-risk probe showed naive
top-k magnitude COLLAPSES projected keys (all keys pick the same few high-variance dims -> support-overlap high -> recall dies).
Amendment v4 fix-hypothesis: WHITEN (decorrelate) the projected keys BEFORE top-k so magnitude is spread across dims ->
top-k diversifies supports -> recall survives. This probe DECIDES which sparse-encode to L-build (cell 2), data-driven.

3 variants on the SAME held-out keys, SAME run (apples-to-apples):
  A naive_topk            (the de-risk failure mode -- baseline)
  B whiten_before_topk    (amendment-v4 LEAD; ZCA-whiten projected keys THEN top-k)
  C random_fixed_positions(fallback; fixed random k-of-N mask, diversity-by-construction, may lose recall)
+ baselines raw_sparse (no projection) and dense_projected (CERT 591 raw, ~0.83-0.96 recall).

PRE-DISPATCH CATCH (Exp-Dev, model-free diagnostic before GPU): naive amendment-v4 ZCA (absolute eps=1e-3) RECALL-COLLAPSES in
the flagship regime N=8192 >> n_held-out-keys~1250 -- cov is rank-deficient (~N-n exactly-zero eigendirections), abs-eps amplifies
them 31x, top-k then selects amplified noise -> matched key/cue supports diverge -> recall 0.07 while dense recall 1.0 (STRUCTURAL,
not the smoke under-training confound; verified 3 synthetics). FIX = SHRINKAGE ZCA (relative floor eps=tau*max_eig, tau=1e-2):
whitens the signal subspace, bounds the null space -> recall 1.0 AND supports still diversify. Baked into fit_zca + selftest guard (6).

Skunkworks VET-delta guards baked in:
  D1 whiten-before-topk encode (NOT naive; SHRINKAGE-ZCA per the pre-dispatch catch above). D2 support-overlap (Jaccard) collapse-guard = LOAD-BEARING SELFTEST (deterministic,
     no model: assert whiten diversifies supports vs naive on a constructed-collapse synthetic). D3 RECALL measured on every
     arm (recall-required; keysep alone misled the de-risk). rho apples-to-apples: projected-then-sparse rho vs raw-sparse rho
     computed on IDENTICAL held-out keys in THIS run (never vs a canonical CERT591 rho -- the bulk-M_crit/own-flattering trap).
C1 composition-integrity: CERT 591 funcs (make_facts/encode/train_contrastive/keysep/recall_at/_np_norm) reused VERBATIM +
a3f473dd-style top-k sparsify. VERSION-MARKER stamped. ASCII; no em-dashes.

Gate (amendment v4): at least one of {B,C} holds keysep<=raw_sparse AND recall>=raw_sparse at f=0.05 -> PASS that variant ->
L-build (cell 2). B-pass with recall preserved = chain-grade path; C-only = MM_negative_recall_axis; neither = MM_negative_full.
"""
import sys
from pathlib import Path
import argparse
import os
import time
import numpy as np

REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1"
CONFIG_VERSION = "CERT591-proj-verbatim + a3f473dd-topk-sparse + amendmentv5: 4-variant(A-naive/B-SHRINKAGE-ZCA-relfloor-tau1e-2/C-random-fixed/D-abs-ZCA-neg-control) x f{0.02-anchor,0.05-anchor,0.10,0.20} x 3seed; gate@f0.02|f0.05; rho-apples-to-apples-same-heldout"
_P = argparse.ArgumentParser(); _P.add_argument("--self-test", action="store_true", dest="self_test"); _ARGS, _ = _P.parse_known_args()
RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "full" if not _ARGS.self_test else "smoke")
FRACS = [0.02, 0.05, 0.10, 0.20]      # amendment v5-followup: f=0.02 ANCHOR (healthy regime per Skunkworks capacity-nuance) + 0.05 boundary + 0.10/0.20 honest-scope (reported, NOT gated; a3f473dd lower-bound precedent)
ANCHOR_FRACS = [0.02, 0.05]           # HARD_PASS gated at f=0.02 OR f=0.05 (structured-sparse healthy only at sparse f; moderate f pays ~3-4x projection-structure cost vs random-k-of-N)
HELDOUT_FRAC = 0.25                   # CERT 591 split
if RUN_MODE == "full":
    ENCODER = "EleutherAI/pythia-2.8b"; SEEDS = [7, 17, 23]; N = 8192; M = 5000; TRAIN_STEPS = 600
else:
    ENCODER = "EleutherAI/pythia-160m"; SEEDS = [0]; N = 2048; M = 500; TRAIN_STEPS = 200

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


def recall_at(Qn, Kn, chunk=256):                          # VERBATIM CERT 591 (cue->key nearest@1)
    cor = 0
    for i in range(0, len(Qn), chunk):
        cor += int((np.argmax(Qn[i:i + chunk] @ Kn.T, axis=1) == np.arange(i, min(i + chunk, len(Qn)))).sum())
    return cor / len(Qn)


def keysep(Kn, sample=512, g=None):                        # VERBATIM CERT 591 (median of max off-diag key-sim; LOWER=decrowded)
    n = len(Kn); idx = (g.permutation(n)[:min(sample, n)] if g is not None else np.arange(min(sample, n)))
    S = Kn[idx]; G = S @ Kn.T
    for r, j in enumerate(idx): G[r, j] = -2.0
    return float(np.median(G.max(1)))


def crosstalk_rho(Kn, sample=512, g=None):                 # rho = MEAN abs off-diag cosine sim (the apples-to-apples crosstalk metric; LOWER=decrowded)
    n = len(Kn); idx = (g.permutation(n)[:min(sample, n)] if g is not None else np.arange(min(sample, n)))
    S = Kn[idx]; G = np.abs(S @ Kn.T)
    for r, j in enumerate(idx): G[r, j] = 0.0
    return float(G.sum() / (len(idx) * (n - 1)))


def top_k_magnitude(X, f):                                  # a3f473dd-style: top-k magnitude -> sign-binarize (bipolar k-of-N)
    k = max(1, int(f * X.shape[1])); out = np.zeros_like(X, np.float32)
    idx = np.argpartition(np.abs(X), -k, axis=1)[:, -k:]
    np.put_along_axis(out, idx, np.sign(np.take_along_axis(X, idx, axis=1)).astype(np.float32), axis=1)
    return out


def fit_zca(X, tau=1e-2):                                   # SHRINKAGE ZCA: floor eigenvalues at tau*max(eig). In N>>n_keys, cov has ~N-n exactly-zero
    mu = X.mean(0, keepdims=True); Xc = X - mu              # eigendirections; an ABSOLUTE eps (1e-3) amplifies them 31x -> top-k picks amplified-noise -> recall
    cov = (Xc.T @ Xc) / max(1, len(X) - 1)                  # COLLAPSES (verified: full-ZCA recall 0.07 vs dense 1.0). Spectrum-RELATIVE floor whitens the
    w, V = np.linalg.eigh(cov.astype(np.float64)); floor = tau * float(w.max())   # signal subspace, bounds the null space -> recall 1.0 + supports still diversify.
    Wz = (V @ np.diag(1.0 / np.sqrt(np.maximum(w, floor))) @ V.T).astype(np.float32)
    return mu.astype(np.float32), Wz


def fit_zca_abs(X, eps=1e-3):                              # NEG-CONTROL (variant D): the BROKEN absolute-eps ZCA -- amplifies the N>>n_keys null space 31x.
    mu = X.mean(0, keepdims=True); Xc = X - mu             # Runs alongside shrinkage B so the fix-effect (B holds recall, D collapses) is VISIBLE in landed-VET metrics.
    cov = (Xc.T @ Xc) / max(1, len(X) - 1); w, V = np.linalg.eigh(cov.astype(np.float64))
    return mu.astype(np.float32), (V @ np.diag(1.0 / np.sqrt(np.maximum(w, eps))) @ V.T).astype(np.float32)


def apply_zca(X, mu, Wz):
    return ((X - mu) @ Wz).astype(np.float32)


def mask_fixed_random(X, f, g):                            # variant C: fixed random k-of-N positions (same for ALL rows) -> sign-binarize; diversity by construction
    k = max(1, int(f * X.shape[1])); idx = g.choice(X.shape[1], k, replace=False)
    out = np.zeros_like(X, np.float32); out[:, idx] = np.sign(X[:, idx]).astype(np.float32)
    return out


def support_overlap(Ksp, sample=128, g=None):              # D2 collapse-guard: mean pairwise Jaccard of active-position SUPPORTS (HIGH=collapsed, LOW=diversified)
    n = len(Ksp); idx = (g.permutation(n)[:min(sample, n)] if g is not None else np.arange(min(sample, n)))
    sups = [set(np.nonzero(Ksp[i])[0].tolist()) for i in idx]
    tot, cnt = 0.0, 0
    for a in range(len(sups)):
        for b in range(a + 1, len(sups)):
            u = len(sups[a] | sups[b])
            tot += (len(sups[a] & sups[b]) / u) if u else 0.0; cnt += 1
    return float(tot / max(1, cnt))


# ---- encoder + projection (VERBATIM CERT 591) ----
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")   # fragmentation guard (flagship OOM-footprint fix)
import torch, torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# OOM FIX: float32 pythia-2.8b (~11GB) exceeds the ~6.8GB runner cap -> OOM at model-load (verified 2x). Load in bf16 (~5.6GB,
# fits w/ headroom; range-safe unlike fp16 which overflows on GPT-NeoX). Pool upcasts to float32 (precise). float32 on CPU smoke.
ENC_DTYPE = torch.bfloat16 if torch.cuda.is_available() else torch.float32


def encode(texts):                                         # VERBATIM CERT 591 (mean-pooled last hidden state)
    tok = AutoTokenizer.from_pretrained(ENCODER)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    mdl = AutoModel.from_pretrained(ENCODER, torch_dtype=ENC_DTYPE).to(DEV).eval(); out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=48).to(DEV)
        with torch.no_grad(): h = mdl(**t).last_hidden_state
        m = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * m).sum(1) / m.sum(1).clamp(min=1)).float().cpu().numpy())
    del mdl
    if DEV.type == "cuda": torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


def train_contrastive(K_tr, Q_tr, d, steps, seed):        # VERBATIM CERT 591 (InfoNCE align + key-uniformity de-crowd)
    torch.manual_seed(seed); K = torch.tensor(K_tr).to(DEV); Q = torch.tensor(Q_tr).to(DEV); n, D = K.shape
    W = (torch.randn(D, d, device=DEV) * (1.0 / D ** 0.5)).requires_grad_(True); opt = torch.optim.Adam([W], lr=1e-2); bs = min(256, n)
    for step in range(steps):
        idx = torch.randperm(n, device=DEV)[:bs]; tgt = torch.arange(len(idx), device=DEV)
        kp = F.normalize(K[idx] @ W, dim=1); qp = F.normalize(Q[idx] @ W, dim=1)
        lq = (qp @ kp.T) / 0.07; lk = (kp @ qp.T) / 0.07
        loss = 0.5 * (F.cross_entropy(lq, tgt) + F.cross_entropy(lk, tgt)) + 0.5 * ((kp @ kp.T) - torch.eye(len(idx), device=DEV) * 2.0).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return W.detach().cpu().numpy().astype(np.float32)


def _measure(K_sp, Q_sp, g):                               # the 3 measurements on a sparsified arm (D3 recall REQUIRED + keysep + rho)
    Kn = _np_norm(K_sp); Qn = _np_norm(Q_sp)
    return {"recall": recall_at(Qn, Kn), "keysep": keysep(Kn, g=g), "rho": crosstalk_rho(Kn, g=g),
            "support_overlap": support_overlap(K_sp, g=g)}


def run_unit(seed):
    g = np.random.default_rng(seed)
    keys, cues = make_facts(M)
    print("  [seed=%d] encoding %d facts on %s (%s)..." % (seed, M, ENCODER, DEV.type), flush=True)
    K = encode(keys); Q = encode(cues)
    nh = int(M * HELDOUT_FRAC); Ktr, Qtr = K[:-nh], Q[:-nh]; Kho, Qho = K[-nh:], Q[-nh:]   # projection never sees held-out
    print("  [seed=%d] training CERT591 projection D=%d -> N=%d (%d steps)..." % (seed, K.shape[1], N, TRAIN_STEPS), flush=True)
    W = train_contrastive(Ktr, Qtr, N, TRAIN_STEPS, seed)
    PK = Kho @ W; PQ = Qho @ W                              # projected held-out keys/cues (the shared substrate for all variants)
    mu, Wz = fit_zca(PK)                                    # B SHRINKAGE ZCA (v5 fix): fit on projected KEYS, applied to keys AND cues (apples-to-apples)
    WK = apply_zca(PK, mu, Wz); WQ = apply_zca(PQ, mu, Wz)
    mua, Wza = fit_zca_abs(PK)                              # D abs-eps ZCA NEG-CONTROL (broken; visibility of the fix)
    AK = apply_zca(PK, mua, Wza); AQ = apply_zca(PQ, mua, Wza)

    by_variant = {"A_naive_topk": {}, "B_whiten_before_topk": {}, "C_random_fixed_positions": {}, "D_abs_zca_neg_control": {}}
    for f in FRACS:
        fk = "f%.2f" % f
        by_variant["A_naive_topk"][fk] = _measure(top_k_magnitude(PK, f), top_k_magnitude(PQ, f), g)
        by_variant["B_whiten_before_topk"][fk] = _measure(top_k_magnitude(WK, f), top_k_magnitude(WQ, f), g)
        by_variant["D_abs_zca_neg_control"][fk] = _measure(top_k_magnitude(AK, f), top_k_magnitude(AQ, f), g)
        cidx = g.choice(N, max(1, int(f * N)), replace=False)
        Cmask = lambda X: (lambda o: (o.__setitem__((slice(None), cidx), np.sign(X[:, cidx]).astype(np.float32)), o)[1])(np.zeros_like(X, np.float32))
        by_variant["C_random_fixed_positions"][fk] = _measure(Cmask(PK), Cmask(PQ), g)

    # baselines on the SAME held-out keys (apples-to-apples): raw-sparse (no proj) + dense-projected (CERT591 raw)
    raw_sparse = {"f%.2f" % f: _measure(top_k_magnitude(Kho, f), top_k_magnitude(Qho, f), g) for f in FRACS}
    dn_K = _np_norm(PK); dn_Q = _np_norm(PQ)
    dense_projected = {"recall": recall_at(dn_Q, dn_K), "keysep": keysep(dn_K, g=g), "rho": crosstalk_rho(dn_K, g=g)}
    af = "f0.02"
    print("  [seed=%d] dense-proj recall=%.3f (CERT591 ref 0.83-0.96) | @f0.02 B(shrink)recall=%.3f overlap=%.3f / D(abs-control)recall=%.3f / A(naive)recall=%.3f" % (
        seed, dense_projected["recall"], by_variant["B_whiten_before_topk"][af]["recall"], by_variant["B_whiten_before_topk"][af]["support_overlap"],
        by_variant["D_abs_zca_neg_control"][af]["recall"], by_variant["A_naive_topk"][af]["recall"]), flush=True)
    return {"seed": seed, "by_variant": by_variant, "raw_sparse_baseline": raw_sparse, "dense_projected_baseline": dense_projected}


def _med(units, path):                                      # median over seeds of a nested value
    vals = []
    for u in units:
        x = u
        for p in path: x = x[p]
        vals.append(x)
    return float(np.median(vals))


VARIANTS = ["A_naive_topk", "B_whiten_before_topk", "C_random_fixed_positions", "D_abs_zca_neg_control"]


def _res_at(units, fk):                                     # median-over-seeds of every variant + raw at one f
    raw = {m: _med(units, ["raw_sparse_baseline", fk, m]) for m in ["keysep", "recall", "rho"]}
    rv = {v: {m: _med(units, ["by_variant", v, fk, m]) for m in ["keysep", "recall", "rho", "support_overlap"]} for v in VARIANTS}
    return raw, rv


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    dense_recall = _med(units, ["dense_projected_baseline", "recall"])
    # all f's reported; HARD_PASS gated only at the ANCHOR f's (0.02 OR 0.05) per amendment v5-followup
    all_f = {}
    for f in FRACS:
        fk = "f%.2f" % f; raw, rv = _res_at(units, fk)
        all_f[fk] = {"raw_sparse": raw, "variants": rv,
                     "B_diversifies_vs_A": rv["B_whiten_before_topk"]["support_overlap"] < rv["A_naive_topk"]["support_overlap"],
                     "B_rho_survives_vs_raw": rv["B_whiten_before_topk"]["rho"] < raw["rho"],
                     "B_beats_D_recall": rv["B_whiten_before_topk"]["recall"] - rv["D_abs_zca_neg_control"]["recall"]}  # fix-effect visibility
    # gate: B holds keysep<=raw AND recall>=raw at an anchor f; record which anchors pass
    b_anchor_pass = [("f%.2f" % f) for f in ANCHOR_FRACS
                     if all_f["f%.2f" % f]["variants"]["B_whiten_before_topk"]["keysep"] <= all_f["f%.2f" % f]["raw_sparse"]["keysep"]
                     and all_f["f%.2f" % f]["variants"]["B_whiten_before_topk"]["recall"] >= all_f["f%.2f" % f]["raw_sparse"]["recall"]]
    c_anchor_pass = [("f%.2f" % f) for f in ANCHOR_FRACS
                     if all_f["f%.2f" % f]["variants"]["C_random_fixed_positions"]["keysep"] <= all_f["f%.2f" % f]["raw_sparse"]["keysep"]
                     and all_f["f%.2f" % f]["variants"]["C_random_fixed_positions"]["recall"] >= all_f["f%.2f" % f]["raw_sparse"]["recall"]]
    detail = {"anchor_fracs": ["f%.2f" % f for f in ANCHOR_FRACS], "dense_recall": round(dense_recall, 4), "by_f": all_f,
              "B_anchor_pass": b_anchor_pass, "C_anchor_pass": c_anchor_pass, "CONFIG_VERSION": CONFIG_VERSION,
              "cites": ["CERT591_kv_learned_projection_v1", "a3f473dd_sparse_super_capacity", "amendment_v5_shrinkage_zca_relfloor"]}
    # per-anchor one-line summary (B shrinkage vs D abs-control = the fix-effect)
    def _s(fk):
        a = all_f[fk]; b = a["variants"]["B_whiten_before_topk"]; d = a["variants"]["D_abs_zca_neg_control"]
        return "%s[raw_rec=%.2f Bshrink_rec=%.2f(ks=%.2f div=%s) Dabs_rec=%.2f fix=%+.2f]" % (
            fk, a["raw_sparse"]["recall"], b["recall"], b["keysep"], a["B_diversifies_vs_A"], d["recall"], a["B_beats_D_recall"])
    summ = "dense_rec=%.2f | %s | B_anchor_pass=%s C_anchor_pass=%s" % (dense_recall, " ".join(_s("f%.2f" % f) for f in FRACS), b_anchor_pass, c_anchor_pass)
    if b_anchor_pass:
        best = b_anchor_pass[0]; b = all_f[best]["variants"]["B_whiten_before_topk"]
        strong = b["recall"] >= 0.80 * dense_recall and all_f[best]["B_diversifies_vs_A"]
        return ("HARD_PASS", "HARD_PASS: variant B (shrinkage-ZCA whiten-before-topk) holds keysep<=raw AND recall>=raw at anchor %s%s -> L-build variant=B at %s. %s" % (
            best, " (recall>=0.80*dense + diversifies)" if strong else " (passes; recall<0.80*dense or weak-diversify -> document margin)", best, summ), detail)
    if c_anchor_pass:
        return ("MIDDLE_BAND", "MM_negative_recall_axis: only C (random-fixed) passes an anchor f (%s); B's recall path lost. L-build C with recall-loss documented. %s" % (c_anchor_pass, summ), detail)
    return ("MIDDLE_BAND", "MM_negative_full: neither B nor C holds keysep<=raw AND recall>=raw at f=0.02 or f=0.05 -- projection+sparse do not compose for KV recall; reframe storage chain to non-sparse composition. %s" % summ, detail)


def _selftest():
    g = np.random.default_rng(3)
    # (1) top_k_magnitude: exactly k nonzeros per row, bipolar
    X = g.standard_normal((10, 100)).astype(np.float32); S = top_k_magnitude(X, 0.1)
    assert np.all((S != 0).sum(1) == 10), "top-k k-of-N count"
    assert set(np.unique(S).tolist()) <= {-1.0, 0.0, 1.0}, "top-k bipolar"
    # (2) ZCA math: on full-rank well-conditioned Y, tiny relative floor -> cov(whitened) ~ I
    Y = g.standard_normal((400, 32)).astype(np.float32) @ g.standard_normal((32, 32)).astype(np.float32)
    mu, Wz = fit_zca(Y, tau=1e-8); Yw = apply_zca(Y, mu, Wz); C = np.cov(Yw.T)
    assert np.abs(C - np.eye(32)).max() < 0.15, "ZCA->I on full-rank, got %.3f" % np.abs(C - np.eye(32)).max()
    # (3) mask_fixed_random: SAME positions all rows, k nonzeros
    Mk = mask_fixed_random(X, 0.1, np.random.default_rng(1))
    sup = [set(np.nonzero(Mk[i])[0].tolist()) for i in range(len(Mk))]
    assert all(s == sup[0] for s in sup) and len(sup[0]) == 10, "fixed-random same positions k-of-N"
    # (4) D2 LOAD-BEARING: on a constructed-collapse synthetic (3 huge-variance dims), naive top-k COLLAPSES (high overlap);
    #     whiten-before-topk DIVERSIFIES (lower overlap). The deterministic guard that the encode actually fixes the collapse.
    Z = g.standard_normal((60, 64)).astype(np.float32); Z[:, :3] *= 50.0      # 3 dominant dims -> naive picks them for every row
    oA = support_overlap(top_k_magnitude(Z, 0.1), g=np.random.default_rng(0))
    muz, Wzz = fit_zca(Z); oB = support_overlap(top_k_magnitude(apply_zca(Z, muz, Wzz), 0.1), g=np.random.default_rng(0))
    assert oB < oA, "D2 collapse-guard: whiten must diversify supports (oB=%.3f < oA=%.3f)" % (oB, oA)
    # (5) recall_at chunked==full
    Qn = _np_norm(g.standard_normal((50, 16)).astype(np.float32)); Kn = Qn.copy()
    assert abs(recall_at(Qn, Kn, chunk=8) - recall_at(Qn, Kn, chunk=50)) < 1e-9 and recall_at(Qn, Kn) == 1.0, "recall chunk-invariant + identity=1.0"
    # (6) RANK-DEFICIENCY GUARD (load-bearing pre-dispatch catch): in N>>n_keys, an absolute-eps full-ZCA recall-COLLAPSES
    #     (amplifies ~N-n null eigendirections 31x -> top-k picks noise); SHRINKAGE ZCA (relative floor, the cell default) PRESERVES recall.
    Nr, nr, rr = 512, 80, 20; Br = g.standard_normal((rr, Nr)).astype(np.float32); Sr = g.standard_normal((nr, rr)).astype(np.float32)
    Pk = (Sr @ Br).astype(np.float32); Pq = (Pk + 0.05 * g.standard_normal((nr, Nr)).astype(np.float32)).astype(np.float32)
    def _abs_zca(Z2, eps):                                                    # the BROKEN absolute-eps full-ZCA (for the negative control)
        m = Z2.mean(0, keepdims=True); Zc = Z2 - m; cv = (Zc.T @ Zc) / (len(Z2) - 1)
        wv, Vv = np.linalg.eigh(cv.astype(np.float64)); return m.astype(np.float32), (Vv @ np.diag(1.0 / np.sqrt(np.maximum(wv, eps))) @ Vv.T).astype(np.float32)
    maf, Waf = _abs_zca(Pk, 1e-3); rec_full = recall_at(_np_norm(top_k_magnitude(apply_zca(Pq, maf, Waf), 0.05)), _np_norm(top_k_magnitude(apply_zca(Pk, maf, Waf), 0.05)))
    muS, WzS = fit_zca(Pk); rec_shrink = recall_at(_np_norm(top_k_magnitude(apply_zca(Pq, muS, WzS), 0.05)), _np_norm(top_k_magnitude(apply_zca(Pk, muS, WzS), 0.05)))
    assert rec_shrink > 0.8 and rec_full < 0.5, "rank-deficiency guard: shrinkage rescues recall (shrink=%.2f>0.8 vs broken-full-ZCA=%.2f<0.5)" % (rec_shrink, rec_full)
    print("[selftest] PASS: top-k + ZCA->I + fixed-random + D2 collapse-guard(oB=%.3f<oA=%.3f) + recall chunk-inv + rank-deficiency-guard(shrink=%.2f vs full-ZCA=%.2f)" % (oB, oA, rec_shrink, rec_full), flush=True)


if __name__ == "__main__":     # GUARD: import-safe (L-build cell + diagnostics reuse these funcs via import; never trigger a run on import)
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s ENCODER=%s N=%d M=%d steps=%d FRACS=%s seeds=%s DEV=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, ENCODER, N, M, TRAIN_STEPS, FRACS, SEEDS, DEV.type, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE, "encoder": ENCODER, "schema": "v5-4variant-f0.02-anchor"}; t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_config).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "model": ENCODER,
               "N": N, "M": M, "FRACS": FRACS, "n_seeds": len(SEEDS), "detail": detail,
               "metrics_source": "measured_flagship_probe_whiten_before_topk_3variant", "per_unit": units, "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
