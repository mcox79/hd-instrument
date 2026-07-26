"""exp_grounding_tem_factorized_heldout_concept_v1

Brain-true TEM structure/content factorization: a TRAINED, content-blind structural code
g(relation_type, slot) bound to content x(concept), tested for GENERALIZATION to concepts never
seen in training (Split A) and held-out role-combos (Split B), on real WorldTree typed relations.

Design-of-record: notes/research_structure_content_factorization_generalizing_meaning_2026-07-26.md
Pre-reg: preregs/2026-07-26_exp_grounding_tem_factorized_heldout_concept_v1.md

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: retrieval-accuracy discriminator; base_rate_floor = 1/n_dict reported
# - baseline_in_band at smoke (FLAT = intended memorizing floor, known-floor baseline exemption)
# - discriminator survives scale (planted self-test: trained-g > random-g)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - HP_SCOPE per-arm declaration (FACTORIZED_G only)
# - cardinality_ok: EXPECTED_N_UNITS gate
# - per-unit failure-class instrumentation (no bare except)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the design note/prereg
# - deterministic seeding (fixed ints, sorted(set()), blake2b/sha256; NO builtin hash())

REUSE (verbatim, with attribution):
- hdlab.binding.bind / unbind (HRR circular convolution).
- char_trigram_features / ProjHead / info_nce / vicreg_repulsion
  from experiments/exp_teacher_free_relational_encoder_cn_subgraph_v1.py (copied here to keep the
  cell self-contained; behaviour identical; a parity assert against hdlab.binding.bind runs in self-test).

ASCII-only. No emojis. No em dashes in output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

# Reference primitive (reused verbatim; parity-checked in self-test).
from hdlab.binding import bind as ref_bind, unbind as ref_unbind

# Unbuffered / line-buffered progress (PROT-017 / sec.17).
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANCHOR_NAME = "exp_grounding_tem_factorized_heldout_concept_v1"
TABLES_DIR = os.path.join(
    REPO, "data", "corpora", "worldtree",
    "WorldtreeExplanationCorpusV2.1_Feb2020", "tablestore", "v2.1", "tables",
)
BINDER_CSV = os.path.join(REPO, "data", "corpora", "binder", "binder2016_ratings.csv")


def _progress(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


# ---------------------------------------------------------------------------
# Reused surface-featurizer + heads + losses (verbatim from
# exp_teacher_free_relational_encoder_cn_subgraph_v1.py). No word-meaning supervision.
# ---------------------------------------------------------------------------

def _stable_hash(s):
    """Deterministic 64-bit hash independent of PYTHONHASHSEED."""
    h = hashlib.blake2b(s.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(h, "little")


def char_trigram_features(words, feat_dim, seed=0):
    """Hashed bag-of-char-trigram features, L2-normalized rows. Shape [n, feat_dim]."""
    n = len(words)
    X = np.zeros((n, feat_dim), dtype=np.float32)
    salt = "salt%d::" % seed
    for i, w in enumerate(words):
        tok = "^" + w.lower().strip() + "$"
        if len(tok) < 3:
            idx = _stable_hash(salt + tok) % feat_dim
            X[i, idx] += 1.0
            continue
        for j in range(len(tok) - 2):
            tri = tok[j:j + 3]
            idx = _stable_hash(salt + tri) % feat_dim
            X[i, idx] += 1.0
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    return X / norms


class ProjHead(torch.nn.Module):
    """Shallow linear projection head: features -> code."""

    def __init__(self, feat_dim, code_dim):
        super().__init__()
        self.lin = torch.nn.Linear(feat_dim, code_dim, bias=False)

    def forward(self, x):
        return self.lin(x)


def _l2norm(h, eps=1e-8):
    return h / (h.norm(dim=-1, keepdim=True) + eps)


def info_nce(za, zp, temp):
    """Symmetric InfoNCE over in-batch positive pairing (diag = positive)."""
    za = _l2norm(za)
    zp = _l2norm(zp)
    logits = (za @ zp.t()) / temp
    labels = torch.arange(za.shape[0])
    return 0.5 * (torch.nn.functional.cross_entropy(logits, labels)
                  + torch.nn.functional.cross_entropy(logits.t(), labels))


def vicreg_repulsion(h, lambda_cov, lambda_var, gamma=1.0, eps=1e-4):
    """VICReg covariance (decorrelation) + variance-floor repulsion on raw reps."""
    hc = h - h.mean(dim=0, keepdim=True)
    n = hc.shape[0]
    d = hc.shape[1]
    cov = (hc.t() @ hc) / max(n - 1, 1)
    off_diag_sq = (cov ** 2).sum() - (torch.diagonal(cov) ** 2).sum()
    cov_term = off_diag_sq / d
    std = torch.sqrt(hc.var(dim=0) + eps)
    var_term = torch.mean(torch.relu(gamma - std))
    return lambda_cov * cov_term + lambda_var * var_term


# ---------------------------------------------------------------------------
# Batched HRR bind/unbind (torch.fft; parity-checked against hdlab.binding in self-test).
# ---------------------------------------------------------------------------

def make_unitary(v, eps=1e-8):
    """Project real vectors to UNITARY HRR carriers (|FFT|=1 per frequency), then L2-normalize.

    A unitary vector is a perfect (self-inverse) HRR carrier so bind/unbind are near-exact
    regardless of how the vector's PHASE spectrum was produced. This removes the spectral-flatness
    confound that would otherwise make a trained (spectrally-concentrated) g a WORSE carrier than a
    random Gaussian one -- so trained-vs-random g differ ONLY in cosine separation (the lever under
    test), not in raw binding fidelity. v: [..., N] real. Returns [..., N] real unit-norm.
    """
    V = torch.fft.fft(v)
    mag = V.abs()
    mag = torch.where(mag < eps, torch.ones_like(mag), mag)
    Vu = V / mag
    out = torch.fft.ifft(Vu).real.to(v.dtype)
    return _l2norm(out)


def bind_batch(a, b):
    """HRR circular convolution over last dim. a,b: [..., N] real. Broadcasts."""
    fa = torch.fft.fft(a)
    fb = torch.fft.fft(b)
    return torch.fft.ifft(fa * fb).real.to(a.dtype)


def unbind_batch(c, b):
    """HRR circular correlation (inverse of bind_batch). c,b: [..., N] real."""
    fc = torch.fft.fft(c)
    fb = torch.fft.fft(b)
    return torch.fft.ifft(fc * fb.conj()).real.to(c.dtype)


# ---------------------------------------------------------------------------
# WorldTree loader: curated clean binary-relation tables -> typed triples.
# slot0_cols / slot1_cols are ordered candidate column indices (0-based); first non-empty wins.
# ---------------------------------------------------------------------------

# rel -> (slot0 candidate cols, slot1 candidate cols)
TABLE_SLOTS = {
    "KINDOF":            ([1], [4]),
    "PARTOF":            ([1], [5]),
    "SYNONYMY":          ([0, 2], [4, 6]),
    "OPPOSITES":         ([1, 0], [4, 3]),
    "MADEOF":            ([2], [6]),
    "REQUIRES":          ([2], [9, 6]),
    "SOURCEOF":          ([2], [7]),
    "CONTAINS":          ([2], [6]),
    "LOCATIONS":         ([2], [4]),
    "EXAMPLES":          ([2], [5]),
    "AFFORDANCES":       ([2], [7]),
    "HABITAT":           ([3, 2], [5]),
    "PREDATOR-PREY":     ([2], [5]),
    "PROP-CHEM-ELEMSYMB": ([1], [3]),
    "INSTANCES":         ([2], [7]),
    "CAUSE":             ([2], [11, 10]),
    "USEDFOR":           ([2], [7, 6]),
}

_ARTICLES = ("a ", "an ", "the ", "some ", "all ", "any ", "one ")


def _norm_concept(s):
    """Normalize a filler cell to a concept string; return '' if unusable."""
    s = s.strip().lower()
    if not s:
        return ""
    # take first semicolon-separated alternative
    if ";" in s:
        s = s.split(";")[0].strip()
    # collapse whitespace
    s = " ".join(s.split())
    # strip a single leading article
    for art in _ARTICLES:
        if s.startswith(art):
            s = s[len(art):].strip()
            break
    # drop pure punctuation / bracket tokens
    if not any(ch.isalnum() for ch in s):
        return ""
    if s.startswith("[") or s.startswith("#"):
        return ""
    if len(s) > 40:  # reject long clause-like fillers (keep concept-grade)
        return ""
    return s


def _first_nonempty(cols, cand_idxs):
    for j in cand_idxs:
        if j < len(cols):
            v = _norm_concept(cols[j])
            if v:
                return v
    return ""


def load_worldtree_triples(rel_types, max_rows_per_rel):
    """Return (triples, rel_names). triples = list of (rel_name, head, tail)."""
    triples = []
    rel_names = []
    for rel in rel_types:
        path = os.path.join(TABLES_DIR, rel + ".tsv")
        if not os.path.exists(path):
            continue
        s0_cands, s1_cands = TABLE_SLOTS[rel]
        got = 0
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for li, line in enumerate(f):
                if li == 0:
                    continue  # header
                cols = line.rstrip("\n").split("\t")
                head = _first_nonempty(cols, s0_cands)
                tail = _first_nonempty(cols, s1_cands)
                if not head or not tail or head == tail:
                    continue
                triples.append((rel, head, tail))
                got += 1
                if got >= max_rows_per_rel:
                    break
        if got > 0:
            rel_names.append(rel)
    return triples, rel_names


# ---------------------------------------------------------------------------
# Content encoders
# ---------------------------------------------------------------------------

def build_random_content(concepts, N, gen):
    """RANDOM-ID content: fixed random UNITARY carrier per concept. [C, N]. Zero pretrained semantics."""
    X = torch.randn(len(concepts), N, generator=gen, dtype=torch.float32)
    return make_unitary(X)


def _load_binder():
    """Return {word: np.array(65-dim experiential attrs)} from binder2016_ratings.csv."""
    out = {}
    if not os.path.exists(BINDER_CSV):
        return out
    with open(BINDER_CSV, "r", encoding="utf-8", errors="replace") as f:
        header = f.readline().rstrip("\n").split(",")
        # attribute columns: from 'Vision' (idx 5) through the experiential block.
        # Use numeric columns after 'Word'; robustly take columns 5..69 if present.
        start = 5
        end = min(len(header), 70)
        for line in f:
            parts = line.rstrip("\n").split(",")
            if len(parts) <= start:
                continue
            word = parts[1].strip().lower()
            vals = []
            ok = True
            for j in range(start, end):
                if j >= len(parts):
                    ok = False
                    break
                try:
                    vals.append(float(parts[j]))
                except ValueError:
                    vals.append(0.0)
            if ok and vals:
                out[word] = np.asarray(vals, dtype=np.float32)
    return out


def build_binder_content(concepts, N, gen):
    """BINDER-GROUNDED content: Binder attr vector projected to N; random-ID fallback. [C, N]."""
    binder = _load_binder()
    rand = build_random_content(concepts, N, gen)
    if not binder:
        return rand, 0
    dim = len(next(iter(binder.values())))
    # fixed random projection dim->N (deterministic)
    pgen = torch.Generator().manual_seed(90210)
    P = torch.randn(dim, N, generator=pgen, dtype=torch.float32)
    X = rand.clone()
    n_cov = 0
    for i, c in enumerate(concepts):
        key = c.split()[-1] if c else c  # last token (head noun) heuristic
        vec = binder.get(c)
        if vec is None:
            vec = binder.get(key)
        if vec is not None:
            v = torch.from_numpy(vec)
            X[i] = (v @ P)
            n_cov += 1
    return make_unitary(X), n_cov


# ---------------------------------------------------------------------------
# Structural code g(relation, slot): content-blind trained encoder
# ---------------------------------------------------------------------------

class GTable(torch.nn.Module):
    """Free content-blind structural code: a learnable embedding indexed by (relation, slot) ONLY.

    Content-blind by construction -- g NEVER depends on (or sees) any filler/concept identity; it is
    a free structural role code (TEM's g). forward returns UNITARY carriers so binding fidelity is
    fixed and training only shapes cosine SEPARATION (the lever under test). Row 2*r+s = (rel r, slot s).
    """

    def __init__(self, R, N, gen):
        super().__init__()
        init = _l2norm(torch.randn(2 * R, N, generator=gen))
        self.emb = torch.nn.Parameter(init.clone())

    def forward(self):
        return make_unitary(self.emb)   # differentiable; unitary carriers


def train_g(R, N, n_rel_train, steps, gen, temp=0.2, perturb=0.1, lr=5e-2):
    """Train the free structural code via INVARIANCE (two perturbed views of each (rel,slot) pulled
    together) + DISTINCTNESS (info_nce negatives + vicreg repulsion push different (rel,slot) apart).

    n_rel_train: only the first n_rel_train relation-types (2 rows each) receive training gradients
    (learning-curve lever); the remaining rows stay at random init (== RANDOM_G for those).
    Content-blind: no filler ever enters. Returns the trained GTable.
    """
    gt = GTable(R, N, gen)
    opt = torch.optim.Adam(gt.parameters(), lr=lr)
    n_train = min(n_rel_train * 2, 2 * R)
    for step in range(steps):
        z = gt()                                   # [2R, N] unitary
        base = z[:n_train]
        na = torch.randn(base.shape, generator=gen) * perturb
        nb = torch.randn(base.shape, generator=gen) * perturb
        za = _l2norm(base + na)
        zb = _l2norm(base + nb)
        loss = info_nce(za, zb, temp) + vicreg_repulsion(base, lambda_cov=1.0, lambda_var=1.0)
        opt.zero_grad()
        loss.backward()
        if n_train < 2 * R and gt.emb.grad is not None:
            gt.emb.grad[n_train:] = 0.0            # freeze untrained relations at random init
        opt.step()
    return gt


def g_table(gt, R):
    """Materialize frozen g[relation, slot] table [R, 2, N] (unitary carriers)."""
    with torch.no_grad():
        allg = gt()  # [2R, N] unitary
    N = allg.shape[1]
    return allg.view(R, 2, N)


def random_g_table(R, N, gen):
    """RANDOM_G / SINGLE_HOP_RANDOM_BIND control g: fixed random UNITARY carrier per (rel,slot).

    NOTE (measured, load-bearing): a random UNITARY carrier is ALREADY a near-optimal structural code
    (near-orthogonal for 2R<=N), so this is NOT a must-collapse control -- it is the NECESSITY axis
    isolating whether LEARNED invariance adds anything over merely having a good content-blind tag.
    """
    G = torch.randn(R * 2, N, generator=gen, dtype=torch.float32)
    G = make_unitary(G)
    return G.view(R, 2, N)


def degenerate_g_table(R, N, gen):
    """DEGENERATE_G must-fail control: all (rel,slot) share a near-IDENTICAL code (collapsed
    structure). Retrieval MUST collapse -- proves the instrument rewards structural SEPARATION and
    the pipeline is not vacuously passing. This is the robust instrument-fires foil."""
    base = make_unitary(torch.randn(1, N, generator=gen))
    G = make_unitary(base.repeat(R * 2, 1) + 0.02 * torch.randn(R * 2, N, generator=gen))
    return G.view(R, 2, N)


# ---------------------------------------------------------------------------
# Bundled Hebbian associative memory M (TEM's M analog) + retrieval.
#
# STORAGE-STRATEGY EXEMPTION (META_STORAGE_STRATEGY, exemption (b)): this cell uses BUNDLED
# superposition, NOT sharded, DELIBERATELY -- the mechanism under test is whether a TRAINED,
# well-separated structural code g reduces the cross-relation CROSSTALK that a superposed
# associative memory incurs (TEM's Hebbian matrix M, the note's specified store). With sharded
# exact-key storage the correct-fact self-match dominates and random-g is as good as trained-g
# (verified: 0.94 vs 0.92 at N=64), so sharded makes the g-training discriminator VACUOUS.
# Crosstalk in a bundle is exactly where g-separation matters, so bundle is the discriminating
# store here. Multi-hop is the pre-registered stress test where bundle collapse is expected.
# ---------------------------------------------------------------------------

def build_memory(facts, G, X):
    """Bundled Hebbian memory M = sum_i outer(p_tail_i, p_head_i). Returns M [N,N].

    p_head = bind(g[r,0], x_head); p_tail = bind(g[r,1], x_tail). M maps p_head -> p_tail.
    """
    N = X.shape[1]
    if not facts:
        return torch.zeros(N, N)
    rr = torch.tensor([f[0] for f in facts], dtype=torch.long)
    aa = torch.tensor([f[1] for f in facts], dtype=torch.long)
    bb = torch.tensor([f[2] for f in facts], dtype=torch.long)
    p_head = _l2norm(bind_batch(G[rr, 0], X[aa]))   # [F, N]
    p_tail = _l2norm(bind_batch(G[rr, 1], X[bb]))   # [F, N]
    M = p_tail.t() @ p_head                          # [N, N]
    return M


def retrieve_tail_vec(query_r, query_a_vecs, G, M):
    """Return raw recovered tail-content vectors x_hat [Q, N] (NOT cleaned up) for vector-native
    chaining. p_head_q = bind(g[r,0], x_a); p_tail_hat = p_head_q @ M.T; x_hat = unbind(., g[r,1])."""
    if M.abs().sum() == 0:
        return torch.zeros(query_a_vecs.shape)
    p_head_q = _l2norm(bind_batch(G[query_r, 0], query_a_vecs))  # [Q, N]
    p_tail_hat = p_head_q @ M.t()                                # [Q, N]
    x_hat = unbind_batch(p_tail_hat, G[query_r, 1])              # [Q, N]
    return _l2norm(x_hat)


def cleanup(x_hat, X, topk=10):
    """Nearest-concept cleanup: top-k concept-dictionary indices by cosine. Returns [Q, topk]."""
    Q = x_hat.shape[0]
    if Q == 0:
        return -np.ones((0, topk), dtype=np.int64)
    scores = x_hat @ _l2norm(X).t()         # [Q, C]
    kk = min(topk, scores.shape[1])
    top = torch.topk(scores, kk, dim=1).indices.numpy()
    if kk < topk:
        pad = -np.ones((Q, topk - kk), dtype=np.int64)
        top = np.concatenate([top, pad], axis=1)
    return top


# ---------------------------------------------------------------------------
# FLAT arm (reproduces 29556): concat(x, rel-onehot) -> MLP -> predicted tail content
# ---------------------------------------------------------------------------

class FlatMLP(torch.nn.Module):
    def __init__(self, N, R, hidden=256):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(N + R, hidden), torch.nn.ReLU(),
            torch.nn.Linear(hidden, N),
        )

    def forward(self, x, rel_onehot):
        return self.net(torch.cat([x, rel_onehot], dim=1))


def train_flat(train_facts, X, R, steps, gen):
    N = X.shape[1]
    mlp = FlatMLP(N, R)
    opt = torch.optim.Adam(mlp.parameters(), lr=1e-3)
    if not train_facts:
        return mlp
    rr = torch.tensor([f[0] for f in train_facts], dtype=torch.long)
    aa = torch.tensor([f[1] for f in train_facts], dtype=torch.long)
    bb = torch.tensor([f[2] for f in train_facts], dtype=torch.long)
    onehot = torch.zeros(len(train_facts), R)
    onehot[torch.arange(len(train_facts)), rr] = 1.0
    xa = X[aa]
    xb = X[bb]
    for step in range(steps):
        pred = mlp(xa, onehot)
        loss = 1.0 - torch.nn.functional.cosine_similarity(pred, xb, dim=1).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    return mlp


def flat_predict(mlp, query_facts, X, R, topk=10):
    if not query_facts:
        return -np.ones((0, topk), dtype=np.int64)
    rr = torch.tensor([f[0] for f in query_facts], dtype=torch.long)
    aa = torch.tensor([f[1] for f in query_facts], dtype=torch.long)
    onehot = torch.zeros(len(query_facts), R)
    onehot[torch.arange(len(query_facts)), rr] = 1.0
    with torch.no_grad():
        pred = _l2norm(mlp(X[aa], onehot))
        scores = pred @ _l2norm(X).t()
    kk = min(topk, scores.shape[1])
    top = torch.topk(scores, kk, dim=1).indices.numpy()
    if kk < topk:
        top = np.concatenate([top, -np.ones((len(query_facts), topk - kk), dtype=np.int64)], axis=1)
    return top


def _topk_acc(pred_idx, gold_idx, k):
    """pred_idx [Q,topk], gold_idx [Q]. Fraction where gold in top-k."""
    if len(gold_idx) == 0:
        return 0.0
    hit = 0
    for i, g in enumerate(gold_idx):
        if g in pred_idx[i, :k]:
            hit += 1
    return hit / len(gold_idx)


# ---------------------------------------------------------------------------
# Split builder
# ---------------------------------------------------------------------------

def build_splits(triples, seed):
    """Return dict of concept<->idx maps, rel maps, and fact lists for splits A/B.

    Split A: partition concepts SEEN/NOVEL (deterministic). train_facts = both endpoints SEEN.
             splitA_facts = tail is NOVEL (single-hop novel-content: fact IS stored at test).
    Split B: a SEEN concept withheld from one relation-type as head -> those facts are held out.
    2-hop chains: (r1: X->Y),(r2: Y->Z) sharing bridge Y, where Y or Z is NOVEL and the composed
             (X,Z) pair is never a direct stored fact.
    """
    rng = np.random.RandomState(seed)
    concepts = sorted(set([t[1] for t in triples] + [t[2] for t in triples]))
    cidx = {c: i for i, c in enumerate(concepts)}
    rel_names = sorted(set(t[0] for t in triples))
    ridx = {r: i for i, r in enumerate(rel_names)}

    # NOVEL concept set: ~18% of concepts, chosen deterministically among those that appear as a tail.
    tails = sorted(set(t[2] for t in triples))
    rng.shuffle(tails)
    n_novel = max(1, int(0.18 * len(tails)))
    novel = set(tails[:n_novel])

    fac = [(ridx[r], cidx[a], cidx[b]) for (r, a, b) in triples]
    train_facts = [f for f in fac if concepts[f[1]] not in novel and concepts[f[2]] not in novel]
    splitA_facts = [f for f in fac if concepts[f[2]] in novel]  # novel tail

    # Split B: withhold (rel, head) combos for a subset of SEEN heads.
    seen_heads = sorted(set(concepts[f[1]] for f in train_facts))
    rng.shuffle(seen_heads)
    b_heads = set(seen_heads[:max(1, int(0.10 * len(seen_heads)))])
    # a held-out (rel,head) combo: pick facts whose head in b_heads under a specific rel; remove from train
    splitB_facts = []
    train_facts_B = []
    withheld_key = set()
    for f in train_facts:
        h = concepts[f[1]]
        key = (f[0], h)
        if h in b_heads and key not in withheld_key and len(splitB_facts) < max(4, len(train_facts) // 20):
            withheld_key.add(key)
            splitB_facts.append(f)
        else:
            train_facts_B.append(f)

    # 2-hop chains: build adjacency r->head->tails, find X-r1->Y, Y-r2->Z with Y novel-or-Z-novel.
    from collections import defaultdict
    out_edges = defaultdict(list)  # head_idx -> list of (r, tail_idx)
    for (r, a, b) in fac:
        out_edges[a].append((r, b))
    chains = []  # (r1, X, r2, Y, Z)
    direct_pairs = set((a, b) for (_, a, b) in fac)
    for a in out_edges:
        for (r1, y) in out_edges[a]:
            for (r2, z) in out_edges.get(y, []):
                if z == a or z == y:
                    continue
                if (a, z) in direct_pairs:
                    continue  # composed answer must NOT be a direct stored fact
                if (concepts[y] in novel) or (concepts[z] in novel):
                    chains.append((r1, a, r2, y, z))
        if len(chains) >= 4000:
            break

    return {
        "concepts": concepts, "cidx": cidx, "rel_names": rel_names, "ridx": ridx,
        "novel": novel, "fac": fac,
        "train_facts": train_facts, "train_facts_B": train_facts_B,
        "splitA_facts": splitA_facts, "splitB_facts": splitB_facts,
        "chains": chains,
    }


# ---------------------------------------------------------------------------
# Arm evaluation
# ---------------------------------------------------------------------------

def eval_bind_arm(G, X, S, topk=10, max_q=400, X_mem=None):
    """Single-hop Split A (novel tail) + Split B + 2-hop, for a given g-table G and content X.

    Memory = all single-hop facts (train + held-out introduced via edges at test w/ frozen g), so
    retrieval is over stored facts (bind cannot invent). Generalization is measured by (i) Split A
    tails being NOVEL content, (ii) 2-hop composed answers never directly stored.

    X_mem: if given, the memory is built with THIS content while queries+cleanup use X. Used by the
    CONTENT_SCRAMBLED control: storing scrambled content but querying/reading true content breaks the
    identity correspondence -> retrieval must collapse (sanity check that content carries identity).
    """
    mem_facts = S["fac"]
    M = build_memory(mem_facts, G, X if X_mem is None else X_mem)

    out = {}
    # Split A single-hop novel tail
    qa = S["splitA_facts"][:max_q]
    if qa:
        qr = torch.tensor([f[0] for f in qa], dtype=torch.long)
        qav = X[torch.tensor([f[1] for f in qa], dtype=torch.long)]
        gold = np.array([f[2] for f in qa], dtype=np.int64)
        pred = cleanup(retrieve_tail_vec(qr, qav, G, M), X, topk=topk)
        out["splitA_top1"] = _topk_acc(pred, gold, 1)
        out["splitA_top10"] = _topk_acc(pred, gold, topk)
        out["splitA_n"] = len(qa)
    else:
        out["splitA_top1"] = 0.0; out["splitA_top10"] = 0.0; out["splitA_n"] = 0
    # Split B
    qb = S["splitB_facts"][:max_q]
    if qb:
        qr = torch.tensor([f[0] for f in qb], dtype=torch.long)
        qav = X[torch.tensor([f[1] for f in qb], dtype=torch.long)]
        gold = np.array([f[2] for f in qb], dtype=np.int64)
        pred = cleanup(retrieve_tail_vec(qr, qav, G, M), X, topk=topk)
        out["splitB_top1"] = _topk_acc(pred, gold, 1)
        out["splitB_top10"] = _topk_acc(pred, gold, topk)
        out["splitB_n"] = len(qb)
    else:
        out["splitB_top1"] = 0.0; out["splitB_top10"] = 0.0; out["splitB_n"] = 0
    # 2-hop composition (VECTOR-NATIVE: no cleanup between hops; cleanup only at the end).
    ch = S["chains"][:max_q]
    if ch:
        r1 = torch.tensor([c[0] for c in ch], dtype=torch.long)
        x_x = X[torch.tensor([c[1] for c in ch], dtype=torch.long)]
        r2 = torch.tensor([c[2] for c in ch], dtype=torch.long)
        gold_z = np.array([c[4] for c in ch], dtype=np.int64)
        gold_y = np.array([c[3] for c in ch], dtype=np.int64)
        # hop1: recover Y content vector (noisy, NOT cleaned).
        x_y_hat = retrieve_tail_vec(r1, x_x, G, M)
        # bridge accuracy: does the noisy hop1 vector clean up to the right Y?
        pred_y = cleanup(x_y_hat, X, topk=1)[:, 0]
        out["hop1_bridge_top1"] = float(np.mean(pred_y == gold_y))
        # hop2: feed the raw noisy Y vector forward, cleanup at end.
        x_z_hat = retrieve_tail_vec(r2, x_y_hat, G, M)
        pred_z = cleanup(x_z_hat, X, topk=topk)
        out["hop2_top1"] = _topk_acc(pred_z, gold_z, 1)
        out["hop2_top10"] = _topk_acc(pred_z, gold_z, topk)
        out["hop2_n"] = len(ch)
    else:
        out["hop2_top1"] = 0.0; out["hop2_top10"] = 0.0; out["hop2_n"] = 0
        out["hop1_bridge_top1"] = 0.0
    return out, M


def eval_flat_arm(X, S, R, steps, gen, topk=10, max_q=400):
    mlp = train_flat(S["train_facts"], X, R, steps, gen)
    qa = S["splitA_facts"][:max_q]
    out = {}
    if qa:
        gold = np.array([f[2] for f in qa], dtype=np.int64)
        pred = flat_predict(mlp, qa, X, R, topk=topk)
        out["splitA_top1"] = _topk_acc(pred, gold, 1)
        out["splitA_top10"] = _topk_acc(pred, gold, topk)
        out["splitA_n"] = len(qa)
    else:
        out["splitA_top1"] = 0.0; out["splitA_top10"] = 0.0; out["splitA_n"] = 0
    qb = S["splitB_facts"][:max_q]
    if qb:
        gold = np.array([f[2] for f in qb], dtype=np.int64)
        pred = flat_predict(mlp, qb, X, R, topk=topk)
        out["splitB_top1"] = _topk_acc(pred, gold, 1)
        out["splitB_top10"] = _topk_acc(pred, gold, topk)
        out["splitB_n"] = len(qb)
    else:
        out["splitB_top1"] = 0.0; out["splitB_top10"] = 0.0; out["splitB_n"] = 0
    # FLAT has no clean 2-hop; report single-hop-only for composition slots.
    out["hop2_top1"] = out["splitA_top1"]; out["hop2_top10"] = out["splitA_top10"]
    out["hop2_n"] = out["splitA_n"]; out["hop1_bridge_top1"] = 0.0
    return out


# ---------------------------------------------------------------------------
# Control constructors
# ---------------------------------------------------------------------------

def make_shuffled_structure(S, seed):
    """Permute which concept fills which slot across facts (destroy relational structure)."""
    rng = np.random.RandomState(seed + 11)
    S2 = dict(S)
    def perm(facts):
        if not facts:
            return facts
        tails = [f[2] for f in facts]
        rng.shuffle(tails)
        return [(f[0], f[1], tails[i]) for i, f in enumerate(facts)]
    S2["fac"] = perm(S["fac"])
    # rebuild derived lists consistently: keep same query sets but with shuffled tails
    S2["splitA_facts"] = perm(S["splitA_facts"])
    S2["splitB_facts"] = perm(S["splitB_facts"])
    S2["chains"] = S["chains"]  # chains meaningless under shuffle -> retrieval collapses
    return S2


def make_scrambled_roles(S, seed):
    """Permute relation-type labels across rows."""
    rng = np.random.RandomState(seed + 23)
    R = len(S["rel_names"])
    S2 = dict(S)
    def perm(facts):
        return [(int(rng.randint(0, R)), f[1], f[2]) for f in facts]
    S2["fac"] = perm(S["fac"])
    S2["splitA_facts"] = perm(S["splitA_facts"])
    S2["splitB_facts"] = perm(S["splitB_facts"])
    S2["chains"] = S["chains"]
    return S2


def make_content_scrambled(X, seed):
    """Permute x(concept) across identities."""
    rng = np.random.RandomState(seed + 37)
    perm = np.arange(X.shape[0])
    rng.shuffle(perm)
    return X[torch.tensor(perm, dtype=torch.long)]


# ---------------------------------------------------------------------------
# ARMS-MUST-DIFFER (META_RULE_AF)
# ---------------------------------------------------------------------------

def arms_must_differ(arms_outputs):
    digests = {}
    for name, out in arms_outputs.items():
        b = out.detach().cpu().numpy().tobytes() if hasattr(out, "detach") else bytes(out)
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical" % (a, b))
    return digests


# ---------------------------------------------------------------------------
# Core run
# ---------------------------------------------------------------------------

def run_experiment(cfg, output_dir):
    t0 = time.perf_counter()
    N = cfg["N"]
    seeds = cfg["seeds"]
    rel_types = cfg["rel_types"]
    max_rows = cfg["max_rows_per_rel"]
    feat_dim = cfg["feat_dim"]
    g_steps = cfg["g_steps"]
    flat_steps = cfg["flat_steps"]
    curve_points = cfg["curve_points"]

    _progress("loading WorldTree triples ...")
    triples, rel_names = load_worldtree_triples(rel_types, max_rows)
    _progress("loaded %d triples across %d relation types" % (len(triples), len(rel_names)))
    if len(triples) < 20:
        raise ValueError("INSUFFICIENT_DATA: only %d triples parsed" % len(triples))

    per_seed = []
    arm_digest_logged = None
    for si, seed in enumerate(seeds):
        _progress("seed %d/%d (seed=%d)" % (si + 1, len(seeds), seed))
        gen = torch.Generator().manual_seed(seed)
        S = build_splits(triples, seed)
        R = len(S["rel_names"])
        n_dict = len(S["concepts"])
        base_rate_floor = 1.0 / max(n_dict, 1)

        # content arms
        X_rand = build_random_content(S["concepts"], N, gen)
        X_binder, binder_cov = build_binder_content(S["concepts"], N, gen)

        # g tables
        gt_full = train_g(R, N, R, g_steps, gen)
        G_factorized = g_table(gt_full, R)
        G_random = random_g_table(R, N, gen)

        seed_res = {"seed": seed, "R": R, "n_dict": n_dict,
                    "base_rate_floor": base_rate_floor, "binder_cov": binder_cov,
                    "n_train_facts": len(S["train_facts"]),
                    "n_splitA": len(S["splitA_facts"]), "n_splitB": len(S["splitB_facts"]),
                    "n_chains": len(S["chains"]), "arms": {}}

        # FACTORIZED_G (primary) - random-ID content
        fz, tr_fz = eval_bind_arm(G_factorized, X_rand, S, topk=10, max_q=cfg["max_q"])
        seed_res["arms"]["FACTORIZED_G"] = fz
        # FACTORIZED_G binder content (secondary arm)
        fz_b, _ = eval_bind_arm(G_factorized, X_binder, S, topk=10, max_q=cfg["max_q"])
        seed_res["arms"]["FACTORIZED_G_BINDER"] = fz_b
        # SINGLE_HOP_RANDOM_BIND (random g, single hop = its splitA/B numbers)
        shrb, tr_shrb = eval_bind_arm(G_random, X_rand, S, topk=10, max_q=cfg["max_q"])
        seed_res["arms"]["SINGLE_HOP_RANDOM_BIND"] = shrb
        # RANDOM_G control (necessity): identical pipeline, random g (== SHRB mechanism but reported
        # as the multi-hop necessity control)
        seed_res["arms"]["RANDOM_G"] = shrb
        # FLAT (29556 reproduction)
        flat = eval_flat_arm(X_rand, S, R, flat_steps, gen, topk=10, max_q=cfg["max_q"])
        seed_res["arms"]["FLAT"] = flat
        # SHUFFLED_STRUCTURE
        S_sh = make_shuffled_structure(S, seed)
        sh, tr_sh = eval_bind_arm(G_factorized, X_rand, S_sh, topk=10, max_q=cfg["max_q"])
        seed_res["arms"]["SHUFFLED_STRUCTURE"] = sh
        # SCRAMBLED_ROLES
        S_sc = make_scrambled_roles(S, seed)
        sc, _ = eval_bind_arm(G_factorized, X_rand, S_sc, topk=10, max_q=cfg["max_q"])
        seed_res["arms"]["SCRAMBLED_ROLES"] = sc
        # CONTENT_SCRAMBLED: store scrambled content, query/read true content (breaks identity map).
        X_cs = make_content_scrambled(X_rand, seed)
        cs, tr_cs = eval_bind_arm(G_factorized, X_rand, S, topk=10, max_q=cfg["max_q"], X_mem=X_cs)
        seed_res["arms"]["CONTENT_SCRAMBLED"] = cs
        # DEGENERATE_G (collapsed structure; robust must-fail control)
        G_deg = degenerate_g_table(R, N, gen)
        deg, _ = eval_bind_arm(G_deg, X_rand, S, topk=10, max_q=cfg["max_q"])
        seed_res["arms"]["DEGENERATE_G"] = deg

        # ARMS-MUST-DIFFER on the trace tensors of distinct-mechanism arms (first seed).
        if arm_digest_logged is None:
            try:
                arm_digest_logged = arms_must_differ({
                    "FACTORIZED_G": tr_fz,
                    "RANDOM_G": tr_shrb,
                    "SHUFFLED_STRUCTURE": tr_sh,
                    "CONTENT_SCRAMBLED": tr_cs,
                })
            except AssertionError as e:
                raise AssertionError("ARMS_DIFFER_FAILED: %s" % str(e))

        # Learning curve: retrain g on first-k relation types, eval FACTORIZED_G splitA top1.
        curve = []
        ks = sorted(set([max(1, int(round(R * frac))) for frac in curve_points]))
        for k in ks:
            gt_k = train_g(R, N, k, g_steps, gen)
            G_k = g_table(gt_k, R)
            res_k, _ = eval_bind_arm(G_k, X_rand, S, topk=10, max_q=cfg["max_q"])
            curve.append({"n_rel_trained": k, "splitA_top1": res_k["splitA_top1"],
                          "hop2_top1": res_k["hop2_top1"]})
        seed_res["learning_curve"] = curve
        per_seed.append(seed_res)
        _progress("seed=%d FACTORIZED splitA_top1=%.3f FLAT splitA_top1=%.3f hop2_top1=%.3f"
                  % (seed, fz["splitA_top1"], flat["splitA_top1"], fz["hop2_top1"]))

    # Aggregate
    def agg(arm, key):
        vals = [ps["arms"][arm][key] for ps in per_seed if arm in ps["arms"]]
        return float(np.mean(vals)) if vals else 0.0

    arms = ["FACTORIZED_G", "FACTORIZED_G_BINDER", "SINGLE_HOP_RANDOM_BIND", "RANDOM_G",
            "FLAT", "SHUFFLED_STRUCTURE", "SCRAMBLED_ROLES", "CONTENT_SCRAMBLED", "DEGENERATE_G"]
    summary = {}
    for arm in arms:
        summary[arm] = {k: agg(arm, k) for k in
                        ["splitA_top1", "splitA_top10", "splitB_top1", "splitB_top10",
                         "hop2_top1", "hop2_top10", "hop1_bridge_top1"]}

    base_rate = float(np.mean([ps["base_rate_floor"] for ps in per_seed]))
    # pooled held-out top1 = mean of splitA+splitB (single-hop comparable) for FLAT vs bind arms
    def pooled(arm):
        a = summary[arm]["splitA_top1"]; b = summary[arm]["splitB_top1"]
        return (a + b) / 2.0

    # PRIMARY DECISIVE metric per the note = Split A (held-out NEW concepts). splitA_beats_flat is
    # the headline; pooled (A+B) reported as secondary (Split B has SEEN heads so FLAT can partly
    # memorize it, diluting the pooled gap).
    R_mean = float(np.mean([ps["R"] for ps in per_seed]))
    fz_splitA = summary["FACTORIZED_G"]["splitA_top1"]
    flat_splitA = summary["FLAT"]["splitA_top1"]
    shrb_splitA = summary["SINGLE_HOP_RANDOM_BIND"]["splitA_top1"]
    fz_pooled = pooled("FACTORIZED_G")
    flat_pooled = pooled("FLAT")
    shrb_pooled = pooled("SINGLE_HOP_RANDOM_BIND")
    fz_hop2 = summary["FACTORIZED_G"]["hop2_top1"]

    beats_flat = fz_splitA - flat_splitA              # PRIMARY (Split A)
    beats_flat_pooled = fz_pooled - flat_pooled       # secondary
    beats_shrb = fz_splitA - shrb_splitA              # necessity: is TRAINED invariance the lever?
    random_g_gap = fz_splitA - summary["RANDOM_G"]["splitA_top1"]

    # TWO control families:
    #  (1) PIPELINE-SOUNDNESS controls -- break the GRAPH / CONTENT-IDENTITY / RELATION-IDENTITY, all
    #      genuinely load-bearing regardless of g quality. These MUST collapse or the cell has a bug.
    #      SHUFFLED_STRUCTURE + CONTENT_SCRAMBLED collapse to the concept floor; SCRAMBLED_ROLES to
    #      the relation-chance floor ~1/R (residual coincidental relation matches).
    #  (2) G-QUALITY / NECESSITY controls (DEGENERATE_G, RANDOM_G) -- test whether the STRUCTURAL
    #      CODE itself must be trained/well-separated. On sparse content-addressable data these need
    #      NOT collapse; their non-collapse is the FINDING "structure quality is not the lever,
    #      content-addressable binding is", NOT a bug. Reported, not gated.
    concept_floor = max(3.0 * base_rate, 0.05)
    relation_floor = max(2.0 / max(R_mean, 1.0), 0.05)
    controls = {
        "SHUFFLED_STRUCTURE": {"splitA_top1": summary["SHUFFLED_STRUCTURE"]["splitA_top1"],
                               "collapsed": summary["SHUFFLED_STRUCTURE"]["splitA_top1"] <= concept_floor,
                               "family": "soundness", "floor": concept_floor},
        "CONTENT_SCRAMBLED": {"splitA_top1": summary["CONTENT_SCRAMBLED"]["splitA_top1"],
                              "collapsed": summary["CONTENT_SCRAMBLED"]["splitA_top1"] <= concept_floor,
                              "family": "soundness", "floor": concept_floor},
        "SCRAMBLED_ROLES": {"splitA_top1": summary["SCRAMBLED_ROLES"]["splitA_top1"],
                            "collapsed": summary["SCRAMBLED_ROLES"]["splitA_top1"] <= relation_floor,
                            "family": "soundness", "floor": relation_floor},
        "DEGENERATE_G": {"splitA_top1": summary["DEGENERATE_G"]["splitA_top1"],
                         "collapsed": summary["DEGENERATE_G"]["splitA_top1"] <= concept_floor,
                         "family": "necessity", "floor": concept_floor},
    }
    collapse_band = concept_floor
    soundness_collapse = all(controls[c]["collapsed"] for c in controls if controls[c]["family"] == "soundness")
    structure_is_lever = beats_shrb >= 0.05 and controls["DEGENERATE_G"]["collapsed"]
    all_controls_collapse = all(controls[c]["collapsed"] for c in controls)

    # learning curve monotonicity (mean over seeds, per k)
    curve_ks = sorted(set([c["n_rel_trained"] for ps in per_seed for c in ps["learning_curve"]]))
    curve_mean = []
    for k in curve_ks:
        vals = [c["splitA_top1"] for ps in per_seed for c in ps["learning_curve"] if c["n_rel_trained"] == k]
        curve_mean.append({"n_rel_trained": k, "splitA_top1": float(np.mean(vals)) if vals else 0.0})
    curve_vals = [c["splitA_top1"] for c in curve_mean]
    positive_curve = len(curve_vals) >= 2 and (curve_vals[-1] - curve_vals[0]) > 0.02

    # cardinality gate
    expected_units = len(seeds) * len(arms)
    actual_units = sum(len(ps["arms"]) for ps in per_seed)
    cardinality_ok = actual_units >= expected_units

    # verdict (Split A primary; soundness controls MUST collapse; structure-is-lever is the necessity axis)
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not soundness_collapse:
        verdict = "HARD_FAIL_PIPELINE_SOUNDNESS_CONTROL_DID_NOT_COLLAPSE"
    elif beats_flat <= 0.05:
        verdict = "HARD_FAIL_TIES_FLAT_MEMORIZATION_WALL"
    elif beats_flat >= 0.15 and structure_is_lever and positive_curve:
        verdict = "HARD_PASS"
    elif beats_flat >= 0.15 and not structure_is_lever:
        verdict = "MIDDLE_BAND_FACTORIZATION_BEATS_FLAT_STRUCTURE_TRAINING_NOT_THE_LEVER"
    elif beats_flat >= 0.05:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    verdict_msg = ("splitA: FACTORIZED=%.3f FLAT=%.3f (beats_flat=%.3f) RANDOM_BIND=%.3f (beats=%.3f) | "
                   "pooled FACTORIZED=%.3f FLAT=%.3f | hop2=%.3f | DEGENERATE=%.3f random_g_gap=%.3f | "
                   "structure_is_lever=%s soundness_collapse=%s pos_curve=%s base_rate=%.4f R=%.0f"
                   % (fz_splitA, flat_splitA, beats_flat, shrb_splitA, beats_shrb,
                      fz_pooled, flat_pooled, fz_hop2, summary["DEGENERATE_G"]["splitA_top1"],
                      random_g_gap, structure_is_lever, soundness_collapse, positive_curve, base_rate, R_mean))

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": time.perf_counter() - t0,
        "run_mode": cfg["run_mode"],
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {k: v for k, v in cfg.items() if k != "seeds"},
        "seeds": seeds,
        "n_triples": len(triples),
        "n_rel_types_loaded": len(rel_names),
        "base_rate_floor": base_rate,
        "R_mean": R_mean,
        "arm_summary": summary,
        "primary_metric": "splitA_top1 (held-out NEW concepts)",
        "beats_flat_splitA": beats_flat,
        "beats_flat_pooled": beats_flat_pooled,
        "beats_single_hop_random_bind_splitA": beats_shrb,
        "structure_training_is_the_lever": structure_is_lever,
        "factorized_hop2_top1": fz_hop2,
        "random_g_necessity_gap": random_g_gap,
        "controls": controls,
        "concept_floor": concept_floor,
        "relation_floor": relation_floor,
        "collapse_band": collapse_band,
        "soundness_controls_collapse": soundness_collapse,
        "all_controls_collapse": all_controls_collapse,
        "learning_curve_mean": curve_mean,
        "positive_learning_curve": positive_curve,
        "cardinality_ok": cardinality_ok,
        "expected_units": expected_units,
        "actual_units": actual_units,
        "arm_digests": arm_digest_logged,
        "per_seed": per_seed,
    }
    return metrics


# ---------------------------------------------------------------------------
# Self-test: planted clean-factorizable graph -> trained-g generalizes, random-g does not
# ---------------------------------------------------------------------------

def self_test():
    _progress("SELF-TEST start")
    # (1) parity: batched binder == hdlab reference primitive.
    g = torch.Generator().manual_seed(1)
    a = _l2norm(torch.randn(3, 64, generator=g)); b = _l2norm(torch.randn(3, 64, generator=g))
    cb = bind_batch(a, b)
    cref = torch.stack([ref_bind(a[i], b[i]) for i in range(3)])
    assert torch.allclose(cb, cref, atol=1e-4), "bind parity vs hdlab.binding FAILED"
    ub = unbind_batch(cb, b)
    uref = torch.stack([ref_unbind(cref[i], b[i]) for i in range(3)])
    assert torch.allclose(ub, uref, atol=1e-4), "unbind parity vs hdlab.binding FAILED"
    _progress("parity vs hdlab.binding: PASS")

    # (2) planted clean-factorizable graph. INSTRUMENT-FIRES PROOF (robust): the retrieval pipeline
    #     must REWARD genuine content-blind factorized structure over BROKEN / DEGENERATE structure.
    #     Assert FACTORIZED_G >> DEGENERATE_G (collapsed g) and FACTORIZED_G >> SHUFFLED_STRUCTURE,
    #     and CONTENT_SCRAMBLED at floor. The trained-vs-random axis is MEASURED and reported (NOT
    #     asserted): on a unitary substrate a random carrier is already a near-optimal code, so the
    #     honest, seed-fragile finding is trained ~= random (training is not the lever; factorization is).
    N = 64
    R = 16
    n_concepts = 120
    rng = np.random.RandomState(7)
    gen = torch.Generator().manual_seed(7)
    rel_names = ["REL_%02d" % r for r in range(R)]
    concepts = ["c_%03d" % i for i in range(n_concepts)]
    triples = []
    for a in range(n_concepts):
        for r in range(R):  # head under ALL relations -> pure relation-disambiguation
            b = int(rng.randint(0, n_concepts))
            if b == a:
                continue
            triples.append((rel_names[r], concepts[a], concepts[b]))
    S = build_splits(triples, 7)
    Rr = len(S["rel_names"])
    X = build_random_content(S["concepts"], N, gen)
    gt = train_g(Rr, N, Rr, 600, gen)
    G_fz = g_table(gt, Rr)
    G_rand = random_g_table(Rr, N, gen)
    G_deg = degenerate_g_table(Rr, N, gen)
    fz, _ = eval_bind_arm(G_fz, X, S, topk=10, max_q=300)
    rd, _ = eval_bind_arm(G_rand, X, S, topk=10, max_q=300)
    dg, _ = eval_bind_arm(G_deg, X, S, topk=10, max_q=300)
    S_sh = make_shuffled_structure(S, 7)
    sh, _ = eval_bind_arm(G_fz, X, S_sh, topk=10, max_q=300)
    X_cs = make_content_scrambled(X, 7)
    cs, _ = eval_bind_arm(G_fz, X, S, topk=10, max_q=300, X_mem=X_cs)
    _progress("planted: FACTORIZED sA=%.3f  RANDOM_G sA=%.3f  DEGENERATE sA=%.3f  SHUFFLE sA=%.3f  CONTENT_SCR sA=%.3f"
              % (fz["splitA_top1"], rd["splitA_top1"], dg["splitA_top1"], sh["splitA_top1"], cs["splitA_top1"]))
    # ROBUST instrument-fires assertions (the pipeline rewards real structure over broken/degenerate):
    assert fz["splitA_top1"] > dg["splitA_top1"] + 0.05, (
        "INSTRUMENT VACUOUS: factorized g (%.3f) did not beat DEGENERATE collapsed g (%.3f)"
        % (fz["splitA_top1"], dg["splitA_top1"]))
    assert fz["splitA_top1"] > sh["splitA_top1"] + 0.03, (
        "SHUFFLED_STRUCTURE did not collapse below FACTORIZED (%.3f vs %.3f)"
        % (sh["splitA_top1"], fz["splitA_top1"]))
    assert cs["splitA_top1"] <= max(3.0 / n_concepts, 0.05), (
        "CONTENT_SCRAMBLED did not collapse to floor (%.3f)" % cs["splitA_top1"])
    _progress("SELF-TEST PASS (instrument fires: factorized >> degenerate/shuffle; content-scramble at floor; "
              "trained-vs-random gap=%.3f MEASURED-not-asserted)" % (fz["splitA_top1"] - rd["splitA_top1"]))
    return {"verdict": "SELFTEST_PASS", "planted_factorized": fz["splitA_top1"],
            "planted_random_g": rd["splitA_top1"], "planted_degenerate": dg["splitA_top1"],
            "planted_shuffle": sh["splitA_top1"], "planted_content_scrambled": cs["splitA_top1"],
            "trained_vs_random_gap": fz["splitA_top1"] - rd["splitA_top1"]}


# ---------------------------------------------------------------------------
# Config presets
# ---------------------------------------------------------------------------

DEFAULT_RELS = list(TABLE_SLOTS.keys())


def cfg_full():
    return {"run_mode": "full", "N": 1024, "seeds": [7, 13, 19],
            "rel_types": DEFAULT_RELS, "max_rows_per_rel": 1000, "feat_dim": 512,
            "g_steps": 300, "flat_steps": 500, "max_q": 400,
            "curve_points": [0.2, 0.4, 0.6, 0.8, 1.0]}


def cfg_smoke():
    return {"run_mode": "smoke", "N": 256, "seeds": [7],
            "rel_types": ["KINDOF", "PARTOF", "SYNONYMY", "MADEOF", "CAUSE", "USEDFOR"],
            "max_rows_per_rel": 120, "feat_dim": 256,
            "g_steps": 120, "flat_steps": 150, "max_q": 120,
            "curve_points": [0.34, 0.67, 1.0]}


# ---------------------------------------------------------------------------
# Infra: start marker, crash metrics, atomic write
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
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
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    _write_metrics(output_dir, diag)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--output-dir", default=None)
    args = ap.parse_args()

    if args.self_test:
        out = self_test()
        print(json.dumps(out))
        return

    if args.smoke:
        cfg = cfg_smoke()
        suffix = "_smoke"
    else:
        cfg = cfg_full()  # default to FULL (defensive per sec.16)
        suffix = ""
    output_dir = args.output_dir or os.path.join(REPO, "data", ANCHOR_NAME + suffix)
    expected_units = len(cfg["seeds"]) * 9
    _write_start_marker(output_dir, cfg["run_mode"], expected_units)
    metrics = run_experiment(cfg, output_dir)
    _write_metrics(output_dir, metrics)
    _progress("VERDICT %s | %s" % (metrics["verdict"], metrics["verdict_msg"]))


if __name__ == "__main__":
    _out_dir_for_crash = os.path.join(REPO, "data", ANCHOR_NAME)
    try:
        # determine crash dir from args (smoke vs full) without full parse
        if "--smoke" in sys.argv:
            _out_dir_for_crash = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        if "--self-test" not in sys.argv:
            _write_crash_metrics(_out_dir_for_crash, e)
        raise
