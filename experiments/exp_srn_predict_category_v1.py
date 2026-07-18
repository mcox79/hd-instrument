"""exp_srn_predict_category_v1 -- glass-box VSA analog of Elman (1990) SRN category induction.

DECISIVE QUESTION
  Does self-supervised NEXT-WORD PREDICTION-LEARNING induce LEXICAL-CATEGORY structure in the
  learned word representations, significantly BETTER than a STATIC co-occurrence/count representation
  of the SAME text? This isolates what prediction-LEARNING (error-driven, iterative) adds over static
  distributional counting -- the thing that keeps tying frequency in the reading arc.

ARMS (ONE variable differs: prediction-LEARNING on/off, over identical text + identical causal window k)
  LEARNER     : learned word embeddings E (V,d), trained by Adam-SGD to minimize next-word prediction
                cross-entropy. Context = bundle (mean) of previous-k word embeddings (VSA superposition);
                prediction = score-all against output codes (VSA cleanup); update = prediction-error
                (surprisal) gradient = entrenchment. This is the substrate's own SGD-coordinate-fit
                machinery (cf. hdlab/additive_map.LearnedSGDCoordinateSource) applied to word sequences.
  STATIC_PPMI : REAL baseline. Directional (causal, same window k) co-occurrence COUNTS -> PPMI ->
                truncated SVD to d dims. The Levy-Goldberg (2014) count analog of word2vec; best-in-class
                static distributional representation, NOT a strawman. No prediction, no error, no updates.
  RANDOM_CODE : must-fail floor / metric-fires control. Fixed random Gaussian codes (V,d). NMI ~ 0.

  Learned per-word representation clustered = E (LEARNER) / SVD rows (STATIC) / random rows (RANDOM).

DISCRIMINATOR
  Delta_NMI = NMI(LEARNER clusters vs POS gold) - NMI(STATIC_PPMI clusters vs POS gold), per seed.
  CAN-FAIL: word2vec ~ PPMI-SVD (Levy-Goldberg 2014), so LEARNER beating STATIC is a genuine empirical
  question, NOT by-construction. A HARD_FAIL (prediction-learning adds nothing beyond counting) is
  FIRST-CLASS and drills the next question (what does the brain's predictor have that ours lacks?).
  We do NOT torture toward pass.

CORPUS + GOLD (difficulty-on)
  NLTK Brown, universal POS tagset. Gold = per-word MAJORITY POS category. Real prose, real category
  gold, unsupervised clustering (gold labels NEVER touch representation learning -> held-out-fair).

GLASS-BOX: numpy / torch(cpu) / sklearn(clustering+metrics) / nltk. NO spaCy-default / Stanza /
  torch-transformers / runtime LLM. ASCII-only. No emojis. Seeded torch.Generator + fixed int seeds.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (ARMS-MUST-DIFFER hash-test)
  - final_metrics_atomicity = tmp_replace (os.replace)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - baseline_in_band at smoke (0.05 < NMI_static < 0.95); metric-fires (NMI_random < 0.05)
  - discriminator fires at full-scale eval (real Brown slice, not toy)
  - HARD_PASS strictly above floor (Delta_NMI >= +0.03, not >= 0)
  - no hash()-derived seeds / no list(set()) ordering (F.5) -> fixed int seeds + sorted(set())
"""

import argparse
import hashlib
import json
import math
import os
import platform
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

ANCHOR_NAME = "srn_predict_category_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Gold POS categories we cluster over (universal tagset; exclude '.' and 'X').
GOLD_CATS = ("NOUN", "VERB", "ADJ", "ADV", "DET", "ADP", "PRON", "CONJ", "PRT", "NUM")


# --------------------------------------------------------------------------- IO / diagnostics
def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)  # atomic per META_RULE_AH


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


# --------------------------------------------------------------------------- corpus + gold
def load_brown_slice(n_sents):
    """Return (sentences, tag_counts) where sentences = list of list of (lower_token, universal_tag)."""
    from nltk.corpus import brown
    tagged = brown.tagged_sents(tagset="universal")
    out = []
    for i, sent in enumerate(tagged):
        if i >= n_sents:
            break
        out.append([(w.lower(), t) for (w, t) in sent])
    return out


def build_vocab_and_gold(sentences, vocab_size, min_count):
    """Top-V alphabetic tokens by freq. Gold = majority universal POS tag per word.

    Returns (word2id, id2word, gold_cat_id [V] int (-1 if no valid gold), cats_used list,
             tag_purity [V] float)."""
    freq = Counter()
    tagcnt = defaultdict(Counter)
    for sent in sentences:
        for (w, t) in sent:
            if w.isalpha():  # drop punctuation, numerals, symbols
                freq[w] += 1
                tagcnt[w][t] += 1
    # deterministic ordering: by (-count, word) -- no list(set()), no hash()
    cand = sorted([w for w, c in freq.items() if c >= min_count], key=lambda w: (-freq[w], w))
    vocab = cand[:vocab_size]
    word2id = {w: i for i, w in enumerate(vocab)}
    id2word = list(vocab)
    V = len(vocab)
    gold = np.full(V, -1, dtype=np.int64)
    purity = np.zeros(V, dtype=np.float64)
    cat2idx = {c: i for i, c in enumerate(GOLD_CATS)}
    for w, i in word2id.items():
        tc = tagcnt[w]
        top_tag, top_n = tc.most_common(1)[0]
        purity[i] = top_n / sum(tc.values())
        if top_tag in cat2idx:
            gold[i] = cat2idx[top_tag]
    return word2id, id2word, gold, list(GOLD_CATS), purity


def tokenize_ids(sentences, word2id):
    """Per-sentence lists of in-vocab token ids (OOV dropped). Keeps sentence boundaries (context no-cross)."""
    seqs = []
    for sent in sentences:
        ids = [word2id[w] for (w, _t) in sent if w in word2id]
        if len(ids) >= 2:
            seqs.append(ids)
    return seqs


# --------------------------------------------------------------------------- ARM: learner (prediction-error SGD)
def build_pairs(seqs, k):
    """Causal next-word pairs. Context stored MOST-RECENT-FIRST (col 0 = token at t-1) so a fixed
    per-column position role has consistent semantics; pad (-1) fills the far/older columns.

    Returns (ctx_ids [P,k] int64 padded with -1, ctx_mask [P,k] float32, targets [P] int64)."""
    ctx_rows, mask_rows, tgts = [], [], []
    for ids in seqs:
        for t in range(1, len(ids)):
            lo = max(0, t - k)
            ctx = ids[lo:t][::-1]                    # most-recent-first
            pad = k - len(ctx)
            row = ctx + [-1] * pad
            m = [1.0] * len(ctx) + [0.0] * pad
            ctx_rows.append(row)
            mask_rows.append(m)
            tgts.append(ids[t])
    return (np.asarray(ctx_rows, dtype=np.int64),
            np.asarray(mask_rows, dtype=np.float32),
            np.asarray(tgts, dtype=np.int64))


def arm_learner(seqs, V, d, k, epochs, batch, lr, seed, order_sensitive=False, device="cpu"):
    """Learned word embeddings E (V,d) trained by Adam-SGD next-word CE. Returns (E [V,d], W [V,d], mean_ce).

    Context = bundle of previous-k input codes. order_sensitive=True BINDS each position with a FIXED +/-1
    role vector (VSA sequence-encoding) BEFORE bundling, so position order is recoverable -- the thing a
    symmetric co-occurrence count structurally cannot capture (the Elman/SRN order-sensitivity)."""
    g = torch.Generator(device=device).manual_seed(seed)
    scale = 1.0 / math.sqrt(d)
    E = torch.nn.Parameter((torch.randn(V, d, generator=g, device=device) * scale))          # input codes
    W = torch.nn.Parameter((torch.randn(V, d, generator=g, device=device) * scale))          # output codes
    roles = None
    if order_sensitive:
        gr = torch.Generator(device=device).manual_seed(20260718)   # FIXED structural roles (not run-seed)
        roles = (torch.randint(0, 2, (k, d), generator=gr, device=device).float() * 2.0 - 1.0)  # +/-1 sign bind
    opt = torch.optim.Adam([E, W], lr=lr)
    ctx_ids, ctx_mask, tgts = build_pairs(seqs, k)
    P = ctx_ids.shape[0]
    ctx_ids_t = torch.from_numpy(ctx_ids).to(device)
    ctx_mask_t = torch.from_numpy(ctx_mask).to(device)
    tgts_t = torch.from_numpy(tgts).to(device)
    ctx_safe = ctx_ids_t.clamp(min=0)                # pad index -1 -> row 0, zeroed by mask
    rng = np.random.default_rng(seed)
    last_ce = float("nan")
    for _ep in range(epochs):
        perm = torch.from_numpy(rng.permutation(P)).to(device)
        ep_loss, ep_n = 0.0, 0
        for s in range(0, P, batch):
            idx = perm[s:s + batch]
            cids = ctx_safe[idx]                                  # (B,k)
            m = ctx_mask_t[idx].unsqueeze(-1)                     # (B,k,1)
            ce_emb = E[cids] * m                                  # (B,k,d) zero padded
            if roles is not None:
                ce_emb = ce_emb * roles.unsqueeze(0)             # (B,k,d) position bind (VSA)
            denom = m.sum(dim=1).clamp(min=1.0)                   # (B,1)
            ctx_vec = ce_emb.sum(dim=1) / denom                  # (B,d) bundle=mean superposition
            logits = ctx_vec @ W.t()                             # (B,V) cleanup / score-all
            loss = torch.nn.functional.cross_entropy(logits, tgts_t[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
            ep_loss += float(loss.item()) * idx.numel()
            ep_n += int(idx.numel())
        last_ce = ep_loss / max(1, ep_n)
    return (E.detach().cpu().numpy().astype(np.float32),
            W.detach().cpu().numpy().astype(np.float32), last_ce)


# --------------------------------------------------------------------------- ARM: static PPMI + SVD (counted)
def arm_static_ppmi(seqs, V, d, k, seed):
    """Directional (causal, window k) co-occurrence COUNTS -> PPMI -> truncated SVD to d. Returns numpy [V,d]."""
    C = np.zeros((V, V), dtype=np.float64)
    for ids in seqs:
        for t in range(1, len(ids)):
            lo = max(0, t - k)
            tgt = ids[t]
            for c in ids[lo:t]:
                C[tgt, c] += 1.0
    total = C.sum()
    if total <= 0:
        return np.zeros((V, d), dtype=np.float32)
    row = C.sum(axis=1, keepdims=True)   # P(target)
    col = C.sum(axis=0, keepdims=True)   # P(context)
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((C * total) / (row * col))
    pmi[~np.isfinite(pmi)] = 0.0
    ppmi = np.maximum(pmi, 0.0)
    from sklearn.decomposition import TruncatedSVD
    dd = min(d, max(2, min(ppmi.shape) - 1))
    svd = TruncatedSVD(n_components=dd, random_state=seed)
    U = svd.fit_transform(ppmi)          # (V, dd) already scaled by singular values
    if dd < d:  # pad with zeros so all arms share d columns (cosmetic; clustering uses only nonzero)
        U = np.concatenate([U, np.zeros((V, d - dd), dtype=U.dtype)], axis=1)
    return U.astype(np.float32)


def arm_random(V, d, seed):
    g = torch.Generator().manual_seed(seed)
    return (torch.randn(V, d, generator=g).numpy()).astype(np.float32)


# --------------------------------------------------------------------------- eval: cluster purity / NMI vs gold
def eval_category_structure(vectors, gold, n_cats, kmeans_seed):
    """L2-normalize gold-word rows, KMeans(K=n_cats), return (ami, nmi, ari, purity, preds, gold_sub, idx_sub).

    PRIMARY metric = AMI (adjusted_mutual_info_score): chance-CORRECTED (random ~ 0), unlike raw NMI which
    carries finite-sample upward bias that mis-fires the metric-fires gate at small sample sizes."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import (normalized_mutual_info_score, adjusted_rand_score,
                                 adjusted_mutual_info_score)
    idx = np.where(gold >= 0)[0]
    X = vectors[idx]
    norm = np.linalg.norm(X, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    Xn = X / norm
    g_sub = gold[idx]
    km = KMeans(n_clusters=n_cats, n_init=10, random_state=kmeans_seed)
    preds = km.fit_predict(Xn)
    ami = float(adjusted_mutual_info_score(g_sub, preds))
    nmi = float(normalized_mutual_info_score(g_sub, preds))
    ari = float(adjusted_rand_score(g_sub, preds))
    # purity = sum over clusters of max class count / N
    N = len(g_sub)
    pur = 0
    for c in np.unique(preds):
        members = g_sub[preds == c]
        if len(members):
            pur += Counter(members.tolist()).most_common(1)[0][1]
    purity = float(pur) / max(1, N)
    return ami, nmi, ari, purity, preds, g_sub, idx


def example_clusters(preds, gold_sub, idx_sub, id2word, cats_used, n_show=4, n_words=8):
    """Human-eyeball: for a few clusters, dominant gold category + example member words."""
    out = []
    for c in sorted(np.unique(preds))[:n_show]:
        mask = preds == c
        member_words = [id2word[idx_sub[j]] for j in np.where(mask)[0][:n_words]]
        cats = [cats_used[g] for g in gold_sub[mask]]
        dom = Counter(cats).most_common(1)[0] if cats else ("?", 0)
        out.append({"cluster": int(c), "dominant_gold": dom[0], "dominant_frac": round(dom[1] / max(1, mask.sum()), 3),
                    "example_words": member_words})
    return out


# --------------------------------------------------------------------------- secondary: next-word top-1 (context disambiguates?)
def secondary_nextword_topk(seqs, V, k, seed, d=128, held_frac=0.15):
    """SECONDARY (not load-bearing): order-sensitive learner top-1 next-word accuracy vs bigram-MLE, held-out.

    Learner trained on train split, scored on test split (no train-peek). Uses the TRAINED OUTPUT codes W
    (score = ctx @ W.T), not the input codes -- the earlier E-as-output proxy was a probe bug. bpc-class
    metrics are expected weak (documented confound); this only checks context-disambiguation directionally."""
    rng = np.random.default_rng(seed)
    n = len(seqs)
    perm = rng.permutation(n)
    n_test = max(1, int(n * held_frac))
    test_idx = set(int(x) for x in perm[:n_test])
    train = [seqs[i] for i in range(n) if i not in test_idx]
    test = [seqs[i] for i in range(n) if i in test_idx]
    big = defaultdict(Counter)
    uni = Counter()
    for ids in train:
        for a, b in zip(ids[:-1], ids[1:]):
            big[a][b] += 1
        for x in ids:
            uni[x] += 1
    global_top = uni.most_common(1)[0][0] if uni else 0
    Etr, Wtr, _ = arm_learner(train, V, d, k, epochs=8, batch=512, lr=0.01, seed=seed, order_sensitive=True)
    roles = (np.asarray(torch.randint(0, 2, (k, d),
             generator=torch.Generator().manual_seed(20260718)).float() * 2.0 - 1.0))
    bg_hit = lr_hit = tot = 0
    for ids in test:
        for t in range(1, len(ids)):
            tgt = ids[t]
            prev = ids[t - 1]
            bg_pred = big[prev].most_common(1)[0][0] if big.get(prev) else global_top
            bg_hit += int(bg_pred == tgt)
            lo = max(0, t - k)
            ctx_tokens = ids[lo:t][::-1]                          # most-recent-first
            emb = Etr[ctx_tokens] * roles[:len(ctx_tokens)]      # position bind
            ctx = emb.mean(axis=0)
            scores = ctx @ Wtr.T                                 # score against TRAINED output codes
            lr_pred = int(np.argmax(scores))
            lr_hit += int(lr_pred == tgt)
            tot += 1
    tot = max(1, tot)
    return {"bigram_top1": round(bg_hit / tot, 4), "learner_top1": round(lr_hit / tot, 4),
            "n_test_tokens": tot, "note": "learner uses trained W output codes (probe-bug fixed)"}


# --------------------------------------------------------------------------- arms-must-differ
def arms_must_differ(arm_outputs):
    digests = {}
    for name, out in arm_outputs.items():
        digests[name] = hashlib.sha256(np.ascontiguousarray(out).tobytes()).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], "META_RULE_AF: arms %s and %s bit-identical" % (a, b)
    return digests


# --------------------------------------------------------------------------- config
def cfg_for(mode):
    if mode == "smoke":
        return dict(n_sents=500, vocab_size=180, min_count=3, d=64, k=4, epochs=4,
                    batch=512, lr=0.01, seeds=[7], kmeans_seeds=[0], min_members=5)
    if mode == "full":
        return dict(n_sents=8000, vocab_size=900, min_count=5, d=128, k=5, epochs=16,
                    batch=512, lr=0.01, seeds=[7, 13, 19], kmeans_seeds=[0, 1, 2], min_members=8)
    raise ValueError("mode must be smoke|full")


# --------------------------------------------------------------------------- run
def run(mode):
    t0 = time.perf_counter()
    cfg = cfg_for(mode)
    output_dir = os.path.join(REPO, "data", "exp_%s%s" % (ANCHOR_NAME, "_smoke" if mode == "smoke" else ""))
    _write_start_marker(output_dir, mode, expected_n_units=len(cfg["seeds"]))

    sentences = load_brown_slice(cfg["n_sents"])
    word2id, id2word, gold, cats_used, purity = build_vocab_and_gold(
        sentences, cfg["vocab_size"], cfg["min_count"])
    V = len(id2word)
    seqs = tokenize_ids(sentences, word2id)

    # keep only gold categories with >= min_members present, remap so K = actual categories
    present = np.array([g for g in gold if g >= 0])
    cat_counts = Counter(present.tolist())
    keep_cats = sorted([c for c, n in cat_counts.items() if n >= cfg["min_members"]])
    remap = {c: i for i, c in enumerate(keep_cats)}
    gold2 = np.array([remap.get(g, -1) if g >= 0 else -1 for g in gold], dtype=np.int64)
    n_cats = len(keep_cats)
    cats_used2 = [cats_used[c] for c in keep_cats]
    n_gold_words = int((gold2 >= 0).sum())

    # STATIC arm (deterministic; compute once, reuse across run seeds)
    static_vec = arm_static_ppmi(seqs, V, cfg["d"], cfg["k"], seed=0)
    random_vec = arm_random(V, cfg["d"], seed=0)

    per_seed = []
    example_clusters_learner = None
    for si, seed in enumerate(cfg["seeds"]):
        # LEARNER_POS = order-sensitive prediction learner (primary mechanism arm; fair Elman-faithful form)
        posE, posW, pos_ce = arm_learner(seqs, V, cfg["d"], cfg["k"], cfg["epochs"], cfg["batch"],
                                         cfg["lr"], seed, order_sensitive=True)
        # LEARNER = bag (order-blind) ablation; isolates whether order-sensitivity is what matters
        bagE, bagW, bag_ce = arm_learner(seqs, V, cfg["d"], cfg["k"], cfg["epochs"], cfg["batch"],
                                         cfg["lr"], seed, order_sensitive=False)
        if si == 0:
            digests = arms_must_differ({"LEARNER_POS": posE, "LEARNER_BAG": bagE,
                                        "STATIC_PPMI": static_vec, "RANDOM_CODE": random_vec})
        kseed = cfg["kmeans_seeds"][si % len(cfg["kmeans_seeds"])]
        ami_p, nmi_p, ari_p, pur_p, preds_p, gsub, idxsub = eval_category_structure(posE, gold2, n_cats, kseed)
        ami_b, nmi_b, ari_b, pur_b, _, _, _ = eval_category_structure(bagE, gold2, n_cats, kseed)
        ami_s, nmi_s, ari_s, pur_s, _, _, _ = eval_category_structure(static_vec, gold2, n_cats, kseed)
        ami_r, nmi_r, ari_r, pur_r, _, _, _ = eval_category_structure(random_vec, gold2, n_cats, kseed)
        if si == 0:
            example_clusters_learner = example_clusters(preds_p, gsub, idxsub, id2word, cats_used2)
        per_seed.append({"seed": seed, "kmeans_seed": kseed,
                         "pos_ce": round(pos_ce, 4), "bag_ce": round(bag_ce, 4),
                         "ami_learner_pos": round(ami_p, 4), "ami_learner_bag": round(ami_b, 4),
                         "ami_static": round(ami_s, 4), "ami_random": round(ami_r, 4),
                         "nmi_learner_pos": round(nmi_p, 4), "nmi_static": round(nmi_s, 4),
                         "purity_learner_pos": round(pur_p, 4), "purity_static": round(pur_s, 4),
                         "delta_ami": round(ami_p - ami_s, 4),          # PRIMARY: order-sensitive learner vs static
                         "delta_ami_bag": round(ami_b - ami_s, 4)})     # ablation: bag learner vs static

    secondary = None
    if mode == "full":
        try:
            secondary = secondary_nextword_topk(seqs, V, cfg["k"], seed=cfg["seeds"][0])
        except Exception as e:  # secondary is non-load-bearing; record but never fatal
            secondary = {"error": "%s: %s" % (type(e).__name__, str(e)[:200])}

    # ---- verdict logic (PRIMARY = AMI, chance-corrected; mechanism arm = LEARNER_POS order-sensitive) ----
    ami_static_mean = float(np.mean([p["ami_static"] for p in per_seed]))
    ami_random_mean = float(np.mean([p["ami_random"] for p in per_seed]))
    ami_learner_mean = float(np.mean([p["ami_learner_pos"] for p in per_seed]))
    ami_bag_mean = float(np.mean([p["ami_learner_bag"] for p in per_seed]))
    nmi_static_mean = float(np.mean([p["nmi_static"] for p in per_seed]))
    nmi_learner_mean = float(np.mean([p["nmi_learner_pos"] for p in per_seed]))
    HP_MARGIN = 0.02  # AMI is chance-corrected (smaller scale than raw NMI); strictly-above-floor margin
    hp_seeds = sum(1 for p in per_seed if p["delta_ami"] >= HP_MARGIN)
    hf_seeds = sum(1 for p in per_seed if p["delta_ami"] <= 0.0)
    n_seed = len(per_seed)
    maj = (n_seed // 2) + 1  # >= 2/3

    metric_fires = abs(ami_random_mean) < 0.03           # AMI ~ 0 for random assignment
    baseline_in_band = 0.03 < ami_static_mean < 0.95     # static distributional counting is measurably structured

    if not metric_fires or not baseline_in_band:
        verdict = "INVALID_REGIME"
        msg = ("regime invalid: ami_random_mean=%.3f (must|.|<0.03, fires=%s), ami_static_mean=%.3f "
               "(must in (0.03,0.95), in_band=%s)" % (ami_random_mean, metric_fires, ami_static_mean,
                                                      baseline_in_band))
    elif hp_seeds >= maj:
        verdict = "HARD_PASS"
        msg = ("prediction-LEARNING induces category structure BEYOND static co-occurrence: "
               "delta_ami>=+%.2f on %d/%d seeds; ami_learner=%.3f > ami_static=%.3f (random=%.3f)"
               % (HP_MARGIN, hp_seeds, n_seed, ami_learner_mean, ami_static_mean, ami_random_mean))
    elif hf_seeds >= maj:
        verdict = "HARD_FAIL"
        msg = ("prediction-LEARNING does NOT beat static co-occurrence (FIRST-CLASS negative): "
               "delta_ami<=0 on %d/%d seeds; ami_learner=%.3f <= ami_static=%.3f (random=%.3f)"
               % (hf_seeds, n_seed, ami_learner_mean, ami_static_mean, ami_random_mean))
    else:
        verdict = "MIDDLE_BAND"
        msg = ("marginal: delta_ami in (0,+%.2f) or split across seeds; ami_learner=%.3f vs ami_static=%.3f "
               "(random=%.3f); hp_seeds=%d hf_seeds=%d" % (HP_MARGIN, ami_learner_mean, ami_static_mean,
                                                          ami_random_mean, hp_seeds, hf_seeds))

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": "%s: %s" % (verdict, msg[:120]),
        "elapsed_s": round(elapsed, 2), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "mode": mode,
        "config": cfg,
        "corpus": {"n_sentences": len(sentences), "n_sequences": len(seqs),
                   "n_tokens": int(sum(len(s) for s in seqs)), "vocab_size": V,
                   "n_gold_words": n_gold_words, "n_categories": n_cats,
                   "categories": cats_used2, "category_member_counts": {cats_used2[remap[c]]: int(cat_counts[c])
                                                                        for c in keep_cats}},
        "arms": ["LEARNER", "STATIC_PPMI", "RANDOM_CODE"],
        "per_seed": per_seed,
        "aggregate": {"ami_learner_pos_mean": round(ami_learner_mean, 4),
                      "ami_learner_bag_mean": round(ami_bag_mean, 4),
                      "ami_static_mean": round(ami_static_mean, 4),
                      "ami_random_mean": round(ami_random_mean, 4),
                      "delta_ami_pos_mean": round(ami_learner_mean - ami_static_mean, 4),
                      "delta_ami_bag_mean": round(ami_bag_mean - ami_static_mean, 4),
                      "nmi_learner_pos_mean": round(nmi_learner_mean, 4),
                      "nmi_static_mean": round(nmi_static_mean, 4),
                      "hp_seeds": hp_seeds, "hf_seeds": hf_seeds, "hp_margin": HP_MARGIN},
        "gates": {"metric_fires": metric_fires, "baseline_in_band": baseline_in_band,
                  "arms_differ_verified": True},
        "example_clusters_learner": example_clusters_learner,
        "secondary_nextword": secondary,
    }
    _write_metrics(output_dir, metrics)
    print("[%s] verdict=%s" % (ANCHOR_NAME, verdict))
    print(msg)
    print("per_seed:", json.dumps(per_seed, indent=2))
    print("metrics ->", os.path.join(output_dir, "metrics.json"))
    return metrics


# --------------------------------------------------------------------------- self-test (real code path)
def self_test():
    """Exercise the REAL arm functions on a tiny synthetic corpus; assert shapes, arms differ, NMI sane."""
    print("[self-test] building tiny synthetic corpus...")
    # synthetic 3-category grammar: DET NOUN VERB pattern so structure is present but not trivial
    dets = ["the", "a", "this", "that"]
    nouns = ["dog", "cat", "man", "car", "tree", "house"]
    verbs = ["runs", "sees", "eats", "moves", "finds", "holds"]
    tagmap = {}
    for w in dets:
        tagmap[w] = "DET"
    for w in nouns:
        tagmap[w] = "NOUN"
    for w in verbs:
        tagmap[w] = "VERB"
    rng = np.random.default_rng(0)
    sentences = []
    for _ in range(400):
        d = rng.choice(dets); n = rng.choice(nouns); v = rng.choice(verbs)
        sentences.append([(d, tagmap[d]), (n, tagmap[n]), (v, tagmap[v])])
    word2id, id2word, gold, cats_used, purity = build_vocab_and_gold(sentences, vocab_size=50, min_count=1)
    V = len(id2word)
    seqs = tokenize_ids(sentences, word2id)
    assert V == len(dets) + len(nouns) + len(verbs), "vocab size %d unexpected" % V
    assert (gold >= 0).sum() == V, "all synthetic words should have gold"

    E, W, ce = arm_learner(seqs, V, d=32, k=2, epochs=6, batch=128, lr=0.02, seed=7, order_sensitive=True)
    Eb, Wb, ceb = arm_learner(seqs, V, d=32, k=2, epochs=6, batch=128, lr=0.02, seed=7, order_sensitive=False)
    S = arm_static_ppmi(seqs, V, d=32, k=2, seed=0)
    R = arm_random(V, 32, seed=0)
    assert E.shape == (V, 32) and S.shape == (V, 32) and R.shape == (V, 32), "arm shape mismatch"
    assert W.shape == (V, 32), "output codes shape mismatch"
    digests = arms_must_differ({"LEARNER_POS": E, "LEARNER_BAG": Eb, "STATIC_PPMI": S, "RANDOM_CODE": R})
    assert len(set(digests.values())) == 4, "arms must be distinct"

    # remap gold present
    present = sorted(set(int(g) for g in gold if g >= 0))
    remap = {c: i for i, c in enumerate(present)}
    gold2 = np.array([remap[int(g)] if g >= 0 else -1 for g in gold], dtype=np.int64)
    n_cats = len(present)
    ami_l, nmi_l, _, pur_l, _, _, _ = eval_category_structure(E, gold2, n_cats, 0)
    ami_s, nmi_s, _, pur_s, _, _, _ = eval_category_structure(S, gold2, n_cats, 0)
    ami_r, nmi_r, _, pur_r, _, _, _ = eval_category_structure(R, gold2, n_cats, 0)
    print("[self-test] ami learner=%.3f static=%.3f random=%.3f | nmi l=%.3f s=%.3f r=%.3f (ce=%.3f)"
          % (ami_l, ami_s, ami_r, nmi_l, nmi_s, nmi_r, ce))
    # on a rigid DET-NOUN-VERB grammar BOTH learner and static should beat random; random should be low
    assert nmi_r < 0.5, "random NMI %.3f unexpectedly high (metric broken?)" % nmi_r
    assert nmi_l > nmi_r and nmi_s > nmi_r, "structured arms must beat random on rigid grammar"
    # F.5 determinism: re-run static is bit-identical (no hash()-seed)
    S2 = arm_static_ppmi(seqs, V, d=32, k=2, seed=0)
    assert np.array_equal(S, S2), "static arm nondeterministic across runs"
    print("[self-test] PASS: real arm code path exercised; arms differ; metric fires; deterministic.")
    return True


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run(args.mode)


if __name__ == "__main__":
    output_dir_guess = os.path.join(REPO, "data", "exp_%s" % ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(output_dir_guess, e)
        raise
