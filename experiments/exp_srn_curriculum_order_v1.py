"""exp_srn_curriculum_order_v1 -- does a CURRICULUM (starting small: simple->complex presentation
order) make the self-supervised order-sensitive predictive reader induce category structure MORE
efficiently, at the SAME token budget, than RANDOM-order training?

DECISIVE QUESTION (contested: Elman 1990 POSITIVE "starting small" vs Rohde-Plaut 1999 NEGATIVE)
  Hold the order-sensitive next-word prediction learner, corpus, architecture, and TOTAL token/exposure
  budget FIXED. Vary ONLY the PRESENTATION ORDER of the training pair-stream:
    CURRICULUM  : easy(simple)->hard(complex). Simple = short sentences of high-frequency words.
    RANDOM      : the parent cell's default (shuffle each epoch). REAL baseline, same budget + arch.
    ANTI        : hard->easy (complex-first). Directional control.
  Metric = category-induction AMI vs POS gold (identical to parent exp_srn_predict_category_v1).
  Does curriculum improve AMI at fixed budget?

FIXED-BUDGET / ONE-VARIABLE (difficulty-on, design-gate compliant)
  Every arm sees EVERY training pair the SAME number of times (one presentation per epoch, epochs fixed).
  Curriculum CANNOT see more data -- only the ORDER within each epoch differs (easy-first / shuffle /
  hard-first). Complexity is per-source-sentence: z(length) + z(mean word-frequency-rank). Learner arm,
  corpus, gold, k, d, epochs, lr, batch are IDENTICAL across CURRICULUM / RANDOM / ANTI. The lone
  manipulated variable is the epoch-wise presentation order of the same pairs.

CAN-FAIL BOTH WAYS (first-class either direction; we do NOT torture toward "helps")
  HARD_PASS  : curriculum > random by pre-registered margin on >= 2/3 seeds  (Elman: right inductive bias
               helps small-scale learning -- an efficiency lever).
  HARD_FAIL  : curriculum <= random on >= 2/3 seeds (Rohde-Plaut confirmed on the substrate; the flat-
               scaling is not fixable by curriculum ordering either -- a clean negative).

REAL BASELINE: RANDOM-order learner = the parent's VET-confirmed default (AMI ~ 0.15 at full config).
  STATIC_PPMI + RANDOM_CODE are carried as reference / metric-fires + baseline-in-band gates only; the
  DECISIVE contrast is CURRICULUM vs RANDOM vs ANTI (all the SAME order-sensitive learner).

GLASS-BOX: numpy / torch(cpu) / sklearn / nltk. NO spaCy-default / Stanza / transformers / runtime LLM.
  ASCII-only. No emojis. Seeded torch.Generator + numpy default_rng + fixed int seeds. Reuses the parent
  cell's VET-confirmed arm_static_ppmi / eval / vocab / gold code verbatim.

BRAIN-CHECK (report): the brain's developmental curriculum benefit is confounded with the LEARNER'S OWN
  CAPACITY growing during development (Elman's later "importance of starting small" = a network with
  LIMITED early memory that GROWS). This test holds capacity FIXED and varies ONLY input order, so a NULL
  here does NOT refute developmental curriculum in general -- it isolates the input-order component.
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

ANCHOR_NAME = "srn_curriculum_order_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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


# --------------------------------------------------------------------------- corpus + gold (verbatim parent)
def load_brown_slice(n_sents):
    from nltk.corpus import brown
    tagged = brown.tagged_sents(tagset="universal")
    out = []
    for i, sent in enumerate(tagged):
        if i >= n_sents:
            break
        out.append([(w.lower(), t) for (w, t) in sent])
    return out


def build_vocab_and_gold(sentences, vocab_size, min_count):
    freq = Counter()
    tagcnt = defaultdict(Counter)
    for sent in sentences:
        for (w, t) in sent:
            if w.isalpha():
                freq[w] += 1
                tagcnt[w][t] += 1
    cand = sorted([w for w, c in freq.items() if c >= min_count], key=lambda w: (-freq[w], w))
    vocab = cand[:vocab_size]
    word2id = {w: i for i, w in enumerate(vocab)}   # id == frequency rank (0 = most frequent)
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
    seqs = []
    for sent in sentences:
        ids = [word2id[w] for (w, _t) in sent if w in word2id]
        if len(ids) >= 2:
            seqs.append(ids)
    return seqs


# --------------------------------------------------------------------------- complexity + pairs (curriculum lever)
def seq_complexity(seqs):
    """Per-sequence complexity = z(length) + z(mean token freq-rank). token id == freq rank (0 = most freq),
    so higher mean id = rarer words. Simple = short + high-frequency. Returns float array [len(seqs)]."""
    lens = np.array([len(s) for s in seqs], dtype=np.float64)
    mean_rank = np.array([float(np.mean(s)) if len(s) else 0.0 for s in seqs], dtype=np.float64)

    def z(x):
        sd = x.std()
        return (x - x.mean()) / (sd if sd > 1e-9 else 1.0)
    return z(lens) + z(mean_rank)


def build_pairs_with_complexity(seqs, k, seq_comp):
    """Causal next-word pairs (context most-recent-first, pad -1). Each pair tagged with the complexity of
    its SOURCE sentence. Returns (ctx_ids [P,k], ctx_mask [P,k], targets [P], pair_comp [P])."""
    ctx_rows, mask_rows, tgts, comp = [], [], [], []
    for si, ids in enumerate(seqs):
        sc = float(seq_comp[si])
        for t in range(1, len(ids)):
            lo = max(0, t - k)
            ctx = ids[lo:t][::-1]
            pad = k - len(ctx)
            ctx_rows.append(ctx + [-1] * pad)
            mask_rows.append([1.0] * len(ctx) + [0.0] * pad)
            tgts.append(ids[t])
            comp.append(sc)
    return (np.asarray(ctx_rows, dtype=np.int64), np.asarray(mask_rows, dtype=np.float32),
            np.asarray(tgts, dtype=np.int64), np.asarray(comp, dtype=np.float64))


# --------------------------------------------------------------------------- ARM: order-sensitive learner (parent, + presentation order)
def arm_learner_ordered(seqs, V, d, k, epochs, batch, lr, seed, order, seq_comp, jitter=0.15, device="cpu"):
    """Order-SENSITIVE prediction learner (parent LEARNER_POS, verbatim mechanics) trained under a chosen
    epoch-wise PRESENTATION ORDER. order in {"random","curriculum","anti"}. Every arm sees every pair once
    per epoch (fixed budget); only the WITHIN-EPOCH order differs.

      random     : full shuffle each epoch (parent default = REAL baseline).
      curriculum : sort ascending by pair complexity (+ small seeded jitter so batches vary across epochs
                   yet the global easy->hard trend holds).
      anti       : sort descending (complex-first).

    Returns (E [V,d], W [V,d], mean_ce_last_epoch)."""
    g = torch.Generator(device=device).manual_seed(seed)
    scale = 1.0 / math.sqrt(d)
    E = torch.nn.Parameter((torch.randn(V, d, generator=g, device=device) * scale))
    W = torch.nn.Parameter((torch.randn(V, d, generator=g, device=device) * scale))
    gr = torch.Generator(device=device).manual_seed(20260718)   # FIXED structural role vectors (not run-seed)
    roles = (torch.randint(0, 2, (k, d), generator=gr, device=device).float() * 2.0 - 1.0)
    opt = torch.optim.Adam([E, W], lr=lr)

    ctx_ids, ctx_mask, tgts, pair_comp = build_pairs_with_complexity(seqs, k, seq_comp)
    P = ctx_ids.shape[0]
    ctx_ids_t = torch.from_numpy(ctx_ids).to(device)
    ctx_mask_t = torch.from_numpy(ctx_mask).to(device)
    tgts_t = torch.from_numpy(tgts).to(device)
    ctx_safe = ctx_ids_t.clamp(min=0)
    rng = np.random.default_rng(seed)
    cstd = pair_comp.std()
    cstd = cstd if cstd > 1e-9 else 1.0
    last_ce = float("nan")
    for _ep in range(epochs):
        if order == "random":
            perm = rng.permutation(P)
        elif order in ("curriculum", "anti"):
            key = pair_comp + rng.standard_normal(P) * jitter * cstd   # local jitter, global trend preserved
            perm = np.argsort(key, kind="stable")
            if order == "anti":
                perm = perm[::-1].copy()
        else:
            raise ValueError("order must be random|curriculum|anti, got %r" % order)
        perm_t = torch.from_numpy(np.ascontiguousarray(perm)).to(device)
        ep_loss, ep_n = 0.0, 0
        for s in range(0, P, batch):
            idx = perm_t[s:s + batch]
            cids = ctx_safe[idx]
            m = ctx_mask_t[idx].unsqueeze(-1)
            ce_emb = E[cids] * m
            ce_emb = ce_emb * roles.unsqueeze(0)               # position bind (order-sensitive VSA)
            denom = m.sum(dim=1).clamp(min=1.0)
            ctx_vec = ce_emb.sum(dim=1) / denom
            logits = ctx_vec @ W.t()
            loss = torch.nn.functional.cross_entropy(logits, tgts_t[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
            ep_loss += float(loss.item()) * idx.numel()
            ep_n += int(idx.numel())
        last_ce = ep_loss / max(1, ep_n)
    return (E.detach().cpu().numpy().astype(np.float32),
            W.detach().cpu().numpy().astype(np.float32), last_ce)


# --------------------------------------------------------------------------- ARM: static PPMI + random (reference; verbatim parent)
def arm_static_ppmi(seqs, V, d, k, seed):
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
    row = C.sum(axis=1, keepdims=True)
    col = C.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((C * total) / (row * col))
    pmi[~np.isfinite(pmi)] = 0.0
    ppmi = np.maximum(pmi, 0.0)
    from sklearn.decomposition import TruncatedSVD
    dd = min(d, max(2, min(ppmi.shape) - 1))
    svd = TruncatedSVD(n_components=dd, random_state=seed)
    U = svd.fit_transform(ppmi)
    if dd < d:
        U = np.concatenate([U, np.zeros((V, d - dd), dtype=U.dtype)], axis=1)
    return U.astype(np.float32)


def arm_random(V, d, seed):
    g = torch.Generator().manual_seed(seed)
    return (torch.randn(V, d, generator=g).numpy()).astype(np.float32)


# --------------------------------------------------------------------------- eval (verbatim parent)
def eval_category_structure(vectors, gold, n_cats, kmeans_seed):
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
    N = len(g_sub)
    pur = 0
    for c in np.unique(preds):
        members = g_sub[preds == c]
        if len(members):
            pur += Counter(members.tolist()).most_common(1)[0][1]
    purity = float(pur) / max(1, N)
    return ami, nmi, ari, purity, preds, g_sub, idx


def example_clusters(preds, gold_sub, idx_sub, id2word, cats_used, n_show=4, n_words=8):
    out = []
    for c in sorted(np.unique(preds))[:n_show]:
        mask = preds == c
        member_words = [id2word[idx_sub[j]] for j in np.where(mask)[0][:n_words]]
        cats = [cats_used[g] for g in gold_sub[mask]]
        dom = Counter(cats).most_common(1)[0] if cats else ("?", 0)
        out.append({"cluster": int(c), "dominant_gold": dom[0],
                    "dominant_frac": round(dom[1] / max(1, mask.sum()), 3),
                    "example_words": member_words})
    return out


# --------------------------------------------------------------------------- arms-must-differ (verbatim parent)
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
                    batch=512, lr=0.01, jitter=0.15, seeds=[7], kmeans_seeds=[0], min_members=5)
    if mode == "full":
        # SAME budget/config as parent exp_srn_predict_category_v1 (provenance-rail: RANDOM arm must
        # reproduce parent LEARNER_POS AMI ~ 0.15).
        return dict(n_sents=8000, vocab_size=900, min_count=5, d=128, k=5, epochs=16,
                    batch=512, lr=0.01, jitter=0.15, seeds=[7, 13, 19], kmeans_seeds=[0, 1, 2], min_members=8)
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
    seq_comp = seq_complexity(seqs)

    present = np.array([g for g in gold if g >= 0])
    cat_counts = Counter(present.tolist())
    keep_cats = sorted([c for c, n in cat_counts.items() if n >= cfg["min_members"]])
    remap = {c: i for i, c in enumerate(keep_cats)}
    gold2 = np.array([remap.get(g, -1) if g >= 0 else -1 for g in gold], dtype=np.int64)
    n_cats = len(keep_cats)
    cats_used2 = [cats_used[c] for c in keep_cats]
    n_gold_words = int((gold2 >= 0).sum())

    static_vec = arm_static_ppmi(seqs, V, cfg["d"], cfg["k"], seed=0)
    random_vec = arm_random(V, cfg["d"], seed=0)

    per_seed = []
    example_clusters_curric = None
    for si, seed in enumerate(cfg["seeds"]):
        curE, curW, cur_ce = arm_learner_ordered(seqs, V, cfg["d"], cfg["k"], cfg["epochs"], cfg["batch"],
                                                  cfg["lr"], seed, "curriculum", seq_comp, cfg["jitter"])
        rndE, rndW, rnd_ce = arm_learner_ordered(seqs, V, cfg["d"], cfg["k"], cfg["epochs"], cfg["batch"],
                                                  cfg["lr"], seed, "random", seq_comp, cfg["jitter"])
        antE, antW, ant_ce = arm_learner_ordered(seqs, V, cfg["d"], cfg["k"], cfg["epochs"], cfg["batch"],
                                                  cfg["lr"], seed, "anti", seq_comp, cfg["jitter"])
        if si == 0:
            digests = arms_must_differ({"CURRICULUM": curE, "RANDOM": rndE, "ANTI": antE,
                                        "STATIC_PPMI": static_vec, "RANDOM_CODE": random_vec})
        kseed = cfg["kmeans_seeds"][si % len(cfg["kmeans_seeds"])]
        ami_c, nmi_c, ari_c, pur_c, preds_c, gsub, idxsub = eval_category_structure(curE, gold2, n_cats, kseed)
        ami_rd, nmi_rd, ari_rd, pur_rd, _, _, _ = eval_category_structure(rndE, gold2, n_cats, kseed)
        ami_a, nmi_a, ari_a, pur_a, _, _, _ = eval_category_structure(antE, gold2, n_cats, kseed)
        ami_s, nmi_s, ari_s, pur_s, _, _, _ = eval_category_structure(static_vec, gold2, n_cats, kseed)
        ami_r, nmi_r, ari_r, pur_r, _, _, _ = eval_category_structure(random_vec, gold2, n_cats, kseed)
        if si == 0:
            example_clusters_curric = example_clusters(preds_c, gsub, idxsub, id2word, cats_used2)
        per_seed.append({"seed": seed, "kmeans_seed": kseed,
                         "cur_ce": round(cur_ce, 4), "rnd_ce": round(rnd_ce, 4), "ant_ce": round(ant_ce, 4),
                         "ami_curriculum": round(ami_c, 4), "ami_random": round(ami_rd, 4),
                         "ami_anti": round(ami_a, 4), "ami_static": round(ami_s, 4),
                         "ami_randomcode": round(ami_r, 4),
                         "purity_curriculum": round(pur_c, 4), "purity_random": round(pur_rd, 4),
                         "delta_curric": round(ami_c - ami_rd, 4),     # PRIMARY: curriculum vs random-order
                         "delta_anti": round(ami_a - ami_rd, 4)})      # directional control: anti vs random-order

    # ---- verdict logic (PRIMARY = delta_curric = AMI(curriculum) - AMI(random-order), same learner) ----
    def mean(key):
        return float(np.mean([p[key] for p in per_seed]))
    ami_cur_mean = mean("ami_curriculum")
    ami_rnd_mean = mean("ami_random")
    ami_ant_mean = mean("ami_anti")
    ami_static_mean = mean("ami_static")
    ami_rc_mean = mean("ami_randomcode")

    HP_MARGIN = 0.02  # AMI is chance-corrected; strictly-above-floor efficiency-lever margin
    hp_seeds = sum(1 for p in per_seed if p["delta_curric"] >= HP_MARGIN)
    hf_seeds = sum(1 for p in per_seed if p["delta_curric"] <= 0.0)
    n_seed = len(per_seed)
    maj = (n_seed // 2) + 1  # >= 2/3

    metric_fires = abs(ami_rc_mean) < 0.03                   # random codes ~ 0 AMI
    baseline_in_band = 0.03 < ami_rnd_mean < 0.95            # RANDOM-order learner (real baseline) is structured

    if not metric_fires or not baseline_in_band:
        verdict = "INVALID_REGIME"
        msg = ("regime invalid: ami_randomcode_mean=%.3f (must|.|<0.03, fires=%s), ami_random_order_mean=%.3f "
               "(must in (0.03,0.95), in_band=%s)" % (ami_rc_mean, metric_fires, ami_rnd_mean, baseline_in_band))
    elif hp_seeds >= maj:
        verdict = "HARD_PASS"
        msg = ("CURRICULUM (starting small) improves category-induction at fixed budget: "
               "delta_curric>=+%.2f on %d/%d seeds; ami_curriculum=%.3f > ami_random=%.3f (anti=%.3f, "
               "static=%.3f, randcode=%.3f) -- Elman: input-order is an efficiency lever"
               % (HP_MARGIN, hp_seeds, n_seed, ami_cur_mean, ami_rnd_mean, ami_ant_mean, ami_static_mean, ami_rc_mean))
    elif hf_seeds >= maj:
        verdict = "HARD_FAIL"
        msg = ("CURRICULUM does NOT beat RANDOM-order at fixed budget (FIRST-CLASS negative, Rohde-Plaut): "
               "delta_curric<=0 on %d/%d seeds; ami_curriculum=%.3f <= ami_random=%.3f (anti=%.3f) -- "
               "flat-scaling not fixable by input-order curriculum either"
               % (hf_seeds, n_seed, ami_cur_mean, ami_rnd_mean, ami_ant_mean))
    else:
        verdict = "MIDDLE_BAND"
        msg = ("marginal/split: delta_curric in (0,+%.2f) or seed-split; ami_curriculum=%.3f vs ami_random=%.3f "
               "(anti=%.3f); hp_seeds=%d hf_seeds=%d" % (HP_MARGIN, ami_cur_mean, ami_rnd_mean, ami_ant_mean,
                                                         hp_seeds, hf_seeds))

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": "%s: %s" % (verdict, msg[:120]),
        "elapsed_s": round(elapsed, 2), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "mode": mode,
        "config": cfg,
        "corpus": {"n_sentences": len(sentences), "n_sequences": len(seqs),
                   "n_tokens": int(sum(len(s) for s in seqs)), "vocab_size": V,
                   "n_gold_words": n_gold_words, "n_categories": n_cats, "categories": cats_used2,
                   "complexity_metric": "z(sentence_length)+z(mean_word_freq_rank)"},
        "arms": ["CURRICULUM", "RANDOM", "ANTI", "STATIC_PPMI", "RANDOM_CODE"],
        "per_seed": per_seed,
        "aggregate": {"ami_curriculum_mean": round(ami_cur_mean, 4), "ami_random_mean": round(ami_rnd_mean, 4),
                      "ami_anti_mean": round(ami_ant_mean, 4), "ami_static_mean": round(ami_static_mean, 4),
                      "ami_randomcode_mean": round(ami_rc_mean, 4),
                      "delta_curric_mean": round(ami_cur_mean - ami_rnd_mean, 4),
                      "delta_anti_mean": round(ami_ant_mean - ami_rnd_mean, 4),
                      "hp_seeds": hp_seeds, "hf_seeds": hf_seeds, "hp_margin": HP_MARGIN},
        "gates": {"metric_fires": metric_fires, "baseline_in_band": baseline_in_band,
                  "arms_differ_verified": True},
        "example_clusters_curriculum": example_clusters_curric,
    }
    _write_metrics(output_dir, metrics)
    print("[%s] verdict=%s" % (ANCHOR_NAME, verdict))
    print(msg)
    print("per_seed:", json.dumps(per_seed, indent=2))
    print("metrics ->", os.path.join(output_dir, "metrics.json"))
    return metrics


# --------------------------------------------------------------------------- self-test (real code path)
def self_test():
    """Exercise the REAL arm functions on a tiny synthetic corpus with a genuine complexity spread; assert
    shapes, arms differ (order actually changes the trajectory), ordering is non-vacuous, metric fires."""
    print("[self-test] building tiny synthetic corpus with a complexity gradient...")
    dets = ["the", "a", "this", "that"]
    nouns = ["dog", "cat", "man", "car", "tree", "house"]
    verbs = ["runs", "sees", "eats", "moves", "finds", "holds"]
    rares = ["zephyr", "quokka", "basalt", "gantry"]     # low-freq -> high complexity contribution
    tagmap = {}
    for w in dets:
        tagmap[w] = "DET"
    for w in nouns:
        tagmap[w] = "NOUN"
    for w in verbs:
        tagmap[w] = "VERB"
    for w in rares:
        tagmap[w] = "NOUN"
    rng = np.random.default_rng(0)
    sentences = []
    for _ in range(400):
        d = rng.choice(dets); n = rng.choice(nouns); v = rng.choice(verbs)
        sent = [(d, tagmap[d]), (n, tagmap[n]), (v, tagmap[v])]
        if rng.random() < 0.3:  # ~30% longer/rarer sentences -> real complexity spread
            sent.append((rng.choice(rares), "NOUN"))
            sent.append((rng.choice(verbs), tagmap[rng.choice(verbs)]))
        sentences.append(sent)
    word2id, id2word, gold, cats_used, purity = build_vocab_and_gold(sentences, vocab_size=50, min_count=1)
    V = len(id2word)
    seqs = tokenize_ids(sentences, word2id)
    seq_comp = seq_complexity(seqs)
    assert seq_comp.std() > 1e-6, "complexity must have spread (curriculum lever is vacuous otherwise)"

    cur, curW, cce = arm_learner_ordered(seqs, V, 32, 2, 6, 128, 0.02, 7, "curriculum", seq_comp)
    rnd, rndW, rce = arm_learner_ordered(seqs, V, 32, 2, 6, 128, 0.02, 7, "random", seq_comp)
    ant, antW, ace = arm_learner_ordered(seqs, V, 32, 2, 6, 128, 0.02, 7, "anti", seq_comp)
    S = arm_static_ppmi(seqs, V, 32, 2, 0)
    R = arm_random(V, 32, 0)
    assert cur.shape == (V, 32) and rnd.shape == (V, 32) and ant.shape == (V, 32), "arm shape mismatch"
    # ONE-VARIABLE + DISCRIMINATOR-FIRES: same seed, same data, same budget; ONLY order differs -> the three
    # learner arms MUST diverge (order is non-vacuous). Bit-identical here = the lever did nothing.
    digests = arms_must_differ({"CURRICULUM": cur, "RANDOM": rnd, "ANTI": ant, "STATIC_PPMI": S, "RANDOM_CODE": R})
    assert len(set(digests.values())) == 5, "all 5 arms must be distinct"

    present = sorted(set(int(g) for g in gold if g >= 0))
    remap = {c: i for i, c in enumerate(present)}
    gold2 = np.array([remap[int(g)] if g >= 0 else -1 for g in gold], dtype=np.int64)
    n_cats = len(present)
    ami_c, nmi_c, _, _, _, _, _ = eval_category_structure(cur, gold2, n_cats, 0)
    ami_rd, nmi_rd, _, _, _, _, _ = eval_category_structure(rnd, gold2, n_cats, 0)
    ami_r, nmi_r, _, _, _, _, _ = eval_category_structure(R, gold2, n_cats, 0)
    print("[self-test] ami curriculum=%.3f random=%.3f randcode=%.3f | ce cur=%.3f rnd=%.3f ant=%.3f"
          % (ami_c, ami_rd, ami_r, cce, rce, ace))
    assert nmi_r < 0.5, "random-code NMI %.3f unexpectedly high (metric broken?)" % nmi_r
    assert nmi_c > nmi_r and nmi_rd > nmi_r, "structured learner arms must beat random-code on rigid grammar"
    # F.5 determinism: same order+seed re-run is bit-identical
    cur2, _, _ = arm_learner_ordered(seqs, V, 32, 2, 6, 128, 0.02, 7, "curriculum", seq_comp)
    assert np.array_equal(cur, cur2), "curriculum arm nondeterministic across runs (F.5 violation)"
    print("[self-test] PASS: real code path; 5 arms distinct; order is non-vacuous; metric fires; deterministic.")
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
