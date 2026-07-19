"""CHAIN-GRADE PROMOTION gate for the structure-content factorization mechanism (component-1).

QUESTION (the make-or-break the synthetic proof, atom 29332, could NOT test):
Does the brain-faithful STRUCTURE-CONTENT FACTORIZATION -- a LEARNED content-blind structural
role code g bound to content x via native FHRR conjunctive binding -- still give held-out
role-combination generalization on REAL GROUNDED CONTENT (CORRELATED concept vectors from real
GloVe distributional semantics: dog~cat~animal), where a flat memorization baseline fails? OR
does real-content CORRELATION break the factorization (crosstalk between correlated fillers)?

WHY THIS IS THE PROMOTION GATE (VET a58c02e0 exact words): the synthetic proof used RANDOM
content codes (near-orthogonal -> factorize PERFECTLY). Real grounded concept vectors are
CORRELATED. The promotion gate = "same learned-g + native-bind compositional generalization on
REAL text (non-synthetic content) where flat memorization fails." THIS CELL is that gate, run on
REAL GloVe-grounded concept vectors with a curated relation set (roles) and a provably-unseen
held-out (role, filler) split.

------------------------------------------------------------------------------------------------
REAL GROUNDED CONTENT (the load-bearing real element)
------------------------------------------------------------------------------------------------
CONTENT (fillers) = REAL GloVe-wiki-gigaword-300 word vectors for 64 grounded concrete nouns
(dog, cat, car, apple, river ...). These carry REAL distributional correlation (measured GloVe
off-diagonal cosine mean ~0.175; dog-cat 0.68, dog-car 0.29, bee-table 0.03). They are encoded
into native FHRR unit phasors via a fixed random phase projection x_j = exp(i * (R_j . v_unit)),
R ~ N(0, beta^2). THEOREM: content FHRR cosine(u,v) = exp(-beta^2 (1-cos_glove(u,v))), so beta is
a content-CORRELATION knob that PRESERVES real GloVe structure (struct-corr-to-glove ~0.93-0.99
across the meaningful range) while setting the overall correlation level.

ROLES = a curated set of structural slots (abstract role scaffold; random FHRR g_true), NOT
semantic categories -- so a role's content prototype is a blend of semantically-DIVERSE fillers
and the flat baseline cannot back off via content similarity (keeps the must-fail control honest).

HONEST SCOPING: content is REAL grounded (GloVe distributional). The relation set is CURATED
(controlled roles + controlled held-out-combination split). A HARD_PASS here is a genuine
CHAIN-GRADE CANDIDATE (compositional generalization on REAL correlated grounded content where
flat fails, brain-faithful native bind, not previously done) -- but full real-text-from-actual-
reading with REAL extracted relations (ConceptNet/SVO tuples; data/datasets/conceptnet5_en_100k
.jsonl is staged) is the FURTHER step. CLAIM-VET-pending; not self-declared chain-grade.

------------------------------------------------------------------------------------------------
CONTENT CONDITIONS (the correlation axis; content = the ONLY thing that varies vs the mechanism)
------------------------------------------------------------------------------------------------
synthetic_orthogonal : random FHRR content (reproduces the v1 synthetic proof AT THIS REGIME =
                       Gate D positive control; the "no real correlation" reference).
glove_real           : GloVe->FHRR at beta=1.5 (content correlation ~= GloVe native, mean ~0.17)
                       -- THE make-or-break: real correlated grounded content.
glove_whitened       : GloVe with top-3 principal components removed (Mu-Viswanath isotropy =
                       brain-faithful decorrelation/whitening), same beta -- the FIX arm: does
                       decorrelating real content RESTORE factorization?
+ a beta correlation SWEEP (supporting context) tracing FACTORED vs FLAT as content correlation
  rises from ~0.02 (near-orthogonal) to ~0.59 (very correlated) -- LOCATES where correlation
  breaks it, honestly.

------------------------------------------------------------------------------------------------
ARMS within each content condition (ONE VARIABLE: structure-bind vs flat; same task/split/codes)
------------------------------------------------------------------------------------------------
World: g_true[r] random FHRR per role; x[f] the content code (REAL grounded, per condition). A
sentence assigns distinct fillers to a subset of m roles. Observable S = sum_i bind(g_true[r_i],
x[f_i]) (FHRR superposition of conjunctive bindings).

ARM_FLAT (must-fail control / memorization): per-role content prototype proto[r] = unit(mean over
training of x[filler-in-role-r]). Readout for query role r: among fillers PRESENT, argmax
sim(x[f], proto[r]). Pure content-typicality. Held-out true filler NEVER seen in role r -> not
typical -> FAILS. Canonical flat/holistic baseline (COGS-class structural failure).

ARM_FACTORED (structure-content factorization, LEARNED g): learn content-blind g_hat[r] by
TEM-style Hebbian averaging g_hat[r] = unit(mean over role-r occurrences of unbind(S, x[filler])).
Averaging over diverse co-fillers cancels crosstalk -> g_hat -> g_true. g_hat NEVER sees held-out
combos. Readout: est = unbind(S, g_hat[r]); among fillers PRESENT, argmax sim(est, x[f]). WITH
CORRELATED CONTENT the crosstalk from co-bundled CORRELATED fillers has a non-zero mean (diverse-
co-filler cancellation is imperfect) -> g_hat biased AND the est can be pulled toward a wrong-but-
content-similar present filler. Whether FACTORED still separates is the empirical make-or-break.

------------------------------------------------------------------------------------------------
BRAIN-CHECK (pre-registered; outcome NOT pre-assumed)
------------------------------------------------------------------------------------------------
The brain factorizes structure from CORRELATED real content (grid/TEM structural codes + SPARSE
DECORRELATED cortical codes; Mu-Viswanath show real embeddings are anisotropic and decorrelate
well). So real content SHOULD be factorizable with the right (decorrelated) content code. If RAW
grounded content breaks it, the brain-faithful FIX is decorrelation/whitening/sparsening -- NOT
abandoning factorization; the glove_whitened arm tests exactly that. Where might the substrate hit
a REAL bound? FHRR superposition crosstalk grows when co-bound content is CORRELATED (the mean of
the cross terms no longer vanishes), a genuine substrate-native limit that whitening addresses.

------------------------------------------------------------------------------------------------
BANDS (pre-registered; present-candidate readout, m=3 -> chance = 1/3 = 0.333)
------------------------------------------------------------------------------------------------
POSITIVE CONTROL (Gate D; MUST hold or cell is suspect): synthetic_orthogonal FACTORED held-out
  >= 0.80 AND (FACTORED-FLAT) held-out gap >= 0.30 (reproduces v1 mechanism AT THIS REGIME).
MUST-FAIL CONTROL (per glove condition; MUST fire): FLAT held-out <= 0.45 (at/below chance 0.333 =
  genuinely fails) AND (FACTORED - FLAT) held-out gap >= 0.30. NOTE: with CORRELATED content the
  flat baseline moves from "systematically wrong (<< chance; the orthogonal signature)" UP to
  "~chance" (correlated f* partially matches the role prototype) -- both are failures; the
  discriminator is the FACTORED-FLAT GAP, not a generalization drop (reported as info). If FLAT
  held-out > 0.60 -> VOID for that condition (flat generalizes via content similarity; split does
  not isolate compositional generalization there).
HARD_PASS (CG candidate): positive control holds AND glove_real FACTORED held-out >= 0.80 AND
  (FACTORED-FLAT) glove_real held-out gap >= 0.30 AND glove_real must-fail fired AND glove_real
  FACTORED held-out within 0.10 of synthetic FACTORED held-out (correlation did NOT break it).
HARD_FAIL_CORRELATION_BREAKS_FIXED_BY_WHITENING (crucial, buildable): positive control holds AND
  glove_real breaks (gap <= 0.05 OR FACTORED_real <= chance+0.05 OR FACTORED_real drops >= 0.30
  below synthetic) AND glove_whitened RESTORES (whitened FACTORED held-out - real FACTORED
  held-out >= 0.15 AND whitened FACTORED held-out >= 0.80). Localizes the barrier to real-content
  correlation; the brain-faithful decorrelation fix works.
HARD_FAIL_CORRELATION_BREAKS_UNFIXED: positive control holds AND glove_real breaks AND whitening
  does NOT restore -> deeper barrier (report; do not hide).
HARD_FAIL_POSITIVE_CONTROL: synthetic positive control does NOT reproduce v1 -> cell/regime
  suspect; downstream conditions untrusted.
MIDDLE_BAND: anything between.

------------------------------------------------------------------------------------------------
COMPUTE ARCHITECTURE (mandatory declaration)
------------------------------------------------------------------------------------------------
Class: (b) sequential-CPU with justification -- wall seconds-to-low-minutes; the cell IS
validating the substrate primitive (FHRR bind/unbind) as a reference computation on real content;
elementwise complex ops on a few thousand N=4096 vectors. Foreground local-to-completion.
Storage strategy: BUNDLED is the object under test (single sentence = one bundle of m bound
pairs, brain-faithful m=3); no sharded store -- this cell tests bind-factorization readout
crosstalk on correlated content directly.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

# CELL-TEMPLATE MANDATORY (subset applicable to a LOCAL foreground mechanism-proof; NOT queue-dispatched):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test on prediction arrays)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - baseline_in_band at smoke (META_RULE_AG; FLAT in-dist in (0.05,0.95); FLAT held-out is the must-fail control)
# - discriminator fires at smoke (must-fail control: FLAT held-out << FLAT in-dist; positive control reproduces v1)
# - Gate D positive control: synthetic_orthogonal condition reproduces the v1 mechanism AT THIS REGIME
# - deterministic seeding: fixed int seeds + random.Random + torch.Generator + sorted(); no salted-builtin hash, no set-order dedupe
# - scaffold-free witness in self-test EXERCISES the REAL hdlab.binding.bind/unbind + REAL GloVe vectors
# - all numbers in comments tagged HYPOTHESIZED@ (this file) / THEORETICAL@ (formula) / CITED@ (GloVe/brain lit); MEASURED@ printed at run

import argparse
import gzip
import hashlib
import json
import math
import random
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "role_filler_factorization_realcontent_cg_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Real substrate primitives (scaffold-free witness in self-test binds against these directly).
from hdlab.atoms import make_atoms  # noqa: E402
from hdlab.binding import bind as hdlab_bind  # noqa: E402
from hdlab.binding import unbind as hdlab_unbind  # noqa: E402
GLOVE_PATH = os.path.join(REPO_ROOT, "data", "gensim_cache",
                          "glove-wiki-gigaword-300", "glove-wiki-gigaword-300.gz")

# 64 grounded concrete nouns, all verified present in GloVe (calibration probe 2026-07-18).
# CITED@GloVe-wiki-gigaword-300 (Pennington et al. 2014; Wikipedia+Gigaword distributional).
VOCAB = [
    "dog", "cat", "horse", "cow", "pig", "sheep", "lion", "tiger", "bear", "wolf",
    "rabbit", "mouse", "bird", "eagle", "owl", "duck", "chicken", "fish", "shark", "whale",
    "frog", "snake", "bee", "ant", "car", "truck", "bus", "train", "boat", "ship",
    "plane", "bicycle", "wheel", "engine", "road", "bridge", "apple", "banana", "orange", "grape",
    "bread", "cheese", "meat", "rice", "sugar", "salt", "water", "milk", "house", "door",
    "window", "roof", "wall", "floor", "chair", "table", "bed", "lamp", "book", "pen",
    "tree", "flower", "grass", "leaf",
]

# Content-condition constants (calibration probe MEASURED 2026-07-18):
# THEORETICAL@ content_cos(u,v) = exp(-beta^2 (1 - cos_glove(u,v)))
BETA_REAL = 1.5      # MEASURED content_cos mean ~0.17 (~= GloVe native 0.175); struct-corr ~0.94
WHITEN_KPC = 3       # Mu-Viswanath top-PC removal -> GloVe cos mean 0.175 -> ~-0.015 (isotropic)


# ----------------------------------------------------------------------------------------------
# Native FHRR ops (elementwise complex; identical to hdlab.binding for complex dtype). Vectorized;
# self-test asserts bit-parity with hdlab_bind/hdlab_unbind on a witness.
# ----------------------------------------------------------------------------------------------
def fhrr_bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """FHRR bind = elementwise complex mul. Broadcasts (..., N)."""
    return a * b


def fhrr_unbind(c: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """FHRR unbind = elementwise mul by conjugate. Broadcasts (..., N)."""
    return c * b.conj()


def unit_phase(v: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    """Project each complex component back to unit magnitude (FHRR cleanup / phasor normalize)."""
    mag = v.abs()
    return v / torch.clamp(mag, min=eps)


def sim_to_codebook(q: torch.Tensor, cb: torch.Tensor) -> torch.Tensor:
    """Normalized real inner product of q (N,) against codebook cb (K,N). Returns (K,). FHRR sim."""
    n = q.shape[-1]
    return (cb * q.conj()).sum(dim=-1).real / n


def content_corr_stats(x: torch.Tensor) -> dict:
    """Off-diagonal FHRR cosine distribution among content codes x (V,N) -- the measured
    real content-correlation level of a condition."""
    v = x.shape[0]
    n = x.shape[-1]
    g = (x @ x.conj().t()).real / n  # (V,V)
    iu = torch.triu_indices(v, v, offset=1)
    off = g[iu[0], iu[1]]
    return {
        "content_cos_mean": float(off.mean()),
        "content_cos_median": float(off.median()),
        "content_cos_p90": float(torch.quantile(off, 0.90)),
        "content_cos_max": float(off.max()),
    }


# ----------------------------------------------------------------------------------------------
# REAL GloVe content loading + FHRR phase-encoding + whitening (Mu-Viswanath isotropy).
# ----------------------------------------------------------------------------------------------
def load_glove_vectors(vocab):
    """Stream the plain-text gzip GloVe file; extract only `vocab` rows. Returns (V,300) float32
    tensor aligned to `vocab` order. Raises if the file is missing or any word absent."""
    if not os.path.exists(GLOVE_PATH):
        raise FileNotFoundError(f"GloVe file not found: {GLOVE_PATH}")
    want = set(vocab)
    found = {}
    with gzip.open(GLOVE_PATH, "rt", encoding="utf-8") as f:
        f.readline()  # header "400000 300"
        for line in f:
            sp = line.rstrip().split(" ")
            w = sp[0]
            if w in want:
                found[w] = [float(t) for t in sp[1:]]
                if len(found) == len(want):
                    break
    missing = [w for w in vocab if w not in found]
    if missing:
        raise ValueError(f"GloVe missing {len(missing)} vocab words: {missing[:10]}")
    M = torch.tensor([found[w] for w in vocab], dtype=torch.float32)  # (V,300) in vocab order
    return M


def whiten_topk_pc(M: torch.Tensor, kpc: int) -> torch.Tensor:
    """Mu-Viswanath (2018) isotropy: center + remove top-kpc principal components. Returns (V,300)
    row-unit-normalized. Decorrelates real embeddings (brain-faithful whitening / sparse decorrel)."""
    Mc = M - M.mean(dim=0, keepdim=True)
    U, S, Vh = torch.linalg.svd(Mc, full_matrices=False)
    S2 = S.clone()
    S2[:kpc] = 0.0
    Mw = (U * S2) @ Vh
    return Mw / torch.clamp(Mw.norm(dim=1, keepdim=True), min=1e-8)


def glove_to_fhrr(M_unit: torch.Tensor, n_dim: int, beta: float, gen: torch.Generator) -> torch.Tensor:
    """Encode real unit vectors (V,300) into FHRR unit phasors (V,N) via random phase projection
    x_j = exp(i * beta * (R_j . v_unit)), R ~ N(0,1). content_cos(u,v)=exp(-beta^2(1-cos(u,v)))."""
    d = M_unit.shape[1]
    R = torch.randn((n_dim, d), generator=gen, dtype=torch.float32) * beta  # (N,300)
    phase = M_unit @ R.t()  # (V,N) real
    x = torch.complex(torch.cos(phase), torch.sin(phase)).to(torch.complex64)
    return x


def build_content(condition: str, vocab, n_dim: int, gen: torch.Generator, M_glove: torch.Tensor):
    """Return content codes x (V,N) complex64 unit phasors for a condition."""
    if condition == "synthetic_orthogonal":
        return make_atoms(len(vocab), n_dim, torch.complex64, gen)
    if condition.startswith("glove"):
        # parse optional beta/whiten from condition; primary names map to defaults
        if condition == "glove_real":
            beta, kpc = BETA_REAL, 0
        elif condition == "glove_whitened":
            beta, kpc = BETA_REAL, WHITEN_KPC
        else:
            raise ValueError(f"unknown glove condition {condition}")
        M_unit = (M_glove / torch.clamp(M_glove.norm(dim=1, keepdim=True), min=1e-8)
                  if kpc == 0 else whiten_topk_pc(M_glove, kpc))
        return glove_to_fhrr(M_unit, n_dim, beta, gen)
    raise ValueError(f"unknown condition {condition}")


# ----------------------------------------------------------------------------------------------
# Data: role-filler world + provably-unseen held-out combination split (arbitrary roles).
# ----------------------------------------------------------------------------------------------
def build_split(n_roles: int, n_fillers: int, held_per_role: int, rng: random.Random):
    """Held-out (role,filler) pairs. Each held-out filler stays TRAINABLE in >=1 other role;
    each role has trainable AND held-out fillers."""
    roles = list(range(n_roles))
    fillers = list(range(n_fillers))
    held_by_role = {r: [] for r in roles}
    for r in roles:
        start = (r * held_per_role) % n_fillers
        chosen = [fillers[(start + k) % n_fillers] for k in range(held_per_role)]
        held_by_role[r] = sorted(set(chosen))
    held_out = set()
    for r in roles:
        for f in held_by_role[r]:
            held_out.add((r, f))
    trainable_by_role = {r: sorted(set(fillers) - set(held_by_role[r])) for r in roles}
    for r in roles:
        assert len(trainable_by_role[r]) >= 2, f"role {r} lacks trainable fillers"
        assert len(held_by_role[r]) >= 1, f"role {r} lacks held-out fillers"
    for (r, f) in held_out:
        assert any(f in trainable_by_role[rr] for rr in roles), f"held-out filler {f} ungrounded"
    return held_out, trainable_by_role, held_by_role


def sample_train_sentence(m, trainable_by_role, held_out, rng):
    roles = list(trainable_by_role.keys())
    for _ in range(200):
        chosen_roles = sorted(rng.sample(roles, m))
        assign, used, ok = {}, set(), True
        for r in chosen_roles:
            cands = [f for f in trainable_by_role[r] if f not in used and (r, f) not in held_out]
            if not cands:
                ok = False
                break
            f = rng.choice(cands)
            assign[r] = f
            used.add(f)
        if ok and len(assign) == m:
            return assign
    raise RuntimeError("could not sample a valid training sentence")


def sample_heldout_sentence(m, trainable_by_role, held_by_role, held_out, rng):
    roles = list(trainable_by_role.keys())
    for _ in range(400):
        r_star = rng.choice([r for r in roles if held_by_role[r]])
        f_star = rng.choice(held_by_role[r_star])
        other_roles = sorted(rng.sample([r for r in roles if r != r_star], m - 1))
        assign, used, ok = {r_star: f_star}, {f_star}, True
        for r in other_roles:
            cands = [f for f in trainable_by_role[r] if f not in used and (r, f) not in held_out]
            if not cands:
                ok = False
                break
            f = rng.choice(cands)
            assign[r] = f
            used.add(f)
        if ok and len(assign) == m:
            return assign, r_star
    raise RuntimeError("could not sample a valid held-out sentence")


def sample_indist_sentence(m, trainable_by_role, held_out, rng):
    assign = sample_train_sentence(m, trainable_by_role, held_out, rng)
    query_role = rng.choice(sorted(assign.keys()))
    return assign, query_role


def make_test_set(kind, n, m, trainable_by_role, held_by_role, held_out, rng):
    out = []
    for _ in range(n):
        if kind == "heldout":
            assign, qr = sample_heldout_sentence(m, trainable_by_role, held_by_role, held_out, rng)
        else:
            assign, qr = sample_indist_sentence(m, trainable_by_role, held_out, rng)
        out.append((assign, qr, assign[qr]))
    return out


def encode_sentence(assign, g_true, x):
    """Observable S = sum_i bind(g_true[r_i], x[f_i]) (FHRR superposition of bound pairs)."""
    parts = [fhrr_bind(g_true[r], x[f]) for r, f in sorted(assign.items())]
    return torch.stack(parts, dim=0).sum(dim=0)


# ----------------------------------------------------------------------------------------------
# Learning + readout.
# ----------------------------------------------------------------------------------------------
def learn(train_sentences, n_roles, g_true, x, n_dim):
    """Returns (g_hat (P,N) FACTORED learned keys, proto (P,N) FLAT content prototypes)."""
    g_acc = torch.zeros((n_roles, n_dim), dtype=torch.complex64)
    p_acc = torch.zeros((n_roles, n_dim), dtype=torch.complex64)
    cnt = torch.zeros(n_roles)
    for assign in train_sentences:
        S = encode_sentence(assign, g_true, x)
        for r, f in assign.items():
            g_acc[r] += fhrr_unbind(S, x[f])   # ~ g_true[r] + crosstalk from co-bundled pairs
            p_acc[r] += x[f]                    # content prototype (no binding)
            cnt[r] += 1
    cnt = torch.clamp(cnt, min=1.0)
    g_hat = unit_phase(g_acc / cnt.unsqueeze(1))
    proto = unit_phase(p_acc / cnt.unsqueeze(1))
    return g_hat, proto


def readout_factored(S, query_role, candidates, g_hat, x):
    est = fhrr_unbind(S, g_hat[query_role])
    cb = torch.stack([x[f] for f in candidates], dim=0)
    scores = sim_to_codebook(est, cb)
    return candidates[int(torch.argmax(scores))]


def readout_flat(query_role, candidates, proto, x):
    cb = torch.stack([x[f] for f in candidates], dim=0)
    scores = sim_to_codebook(proto[query_role], cb)
    return candidates[int(torch.argmax(scores))]


def evaluate(test_set, g_true, g_hat, proto, x, n_fillers):
    """PRESENT (fair; both arms read present fillers) + VOCAB (hard; whole vocab) candidate sets."""
    vocab = list(range(n_fillers))
    correct = {"factored_present": 0, "flat_present": 0, "factored_vocab": 0, "flat_vocab": 0}
    pf_present, pl_present = [], []
    for assign, qr, true_f in test_set:
        S = encode_sentence(assign, g_true, x)
        present = sorted(assign.values())
        fp = readout_factored(S, qr, present, g_hat, x)
        lp = readout_flat(qr, present, proto, x)
        fv = readout_factored(S, qr, vocab, g_hat, x)
        lv = readout_flat(qr, vocab, proto, x)
        pf_present.append(fp)
        pl_present.append(lp)
        correct["factored_present"] += int(fp == true_f)
        correct["flat_present"] += int(lp == true_f)
        correct["factored_vocab"] += int(fv == true_f)
        correct["flat_vocab"] += int(lv == true_f)
    n = len(test_set)
    acc = {k: c / n for k, c in correct.items()}
    return acc, pf_present, pl_present


# ----------------------------------------------------------------------------------------------
# Core run over content conditions.
# ----------------------------------------------------------------------------------------------
def run_config(n_dim, n_roles, n_fillers, m, held_per_role, diversity_levels, n_test, seeds,
               conditions):
    chance = 1.0 / m
    vocab = VOCAB[:n_fillers]
    M_glove = load_glove_vectors(vocab)  # (V,300) real, once (deterministic)
    per_seed = []
    for seed in seeds:
        rng = random.Random(seed)
        gen = torch.Generator().manual_seed(seed)
        g_true = make_atoms(n_roles, n_dim, torch.complex64, gen)  # role scaffold (SAME across conds)

        held_out, trainable_by_role, held_by_role = build_split(n_roles, n_fillers, held_per_role, rng)
        rng_test = random.Random(seed + 100000)
        test_held = make_test_set("heldout", n_test, m, trainable_by_role, held_by_role, held_out, rng_test)
        test_ind = make_test_set("indist", n_test, m, trainable_by_role, held_by_role, held_out, rng_test)

        # Train sentences per D fixed per seed and IDENTICAL across conditions (content = only var).
        train_by_D = {}
        for D in diversity_levels:
            rng_tr = random.Random(seed * 1000 + D)
            train_by_D[D] = [sample_train_sentence(m, trainable_by_role, held_out, rng_tr) for _ in range(D)]

        cond_results = {}
        for cond in conditions:
            gen_c = torch.Generator().manual_seed(seed * 31 + hash_str(cond))
            x = build_content(cond, vocab, n_dim, gen_c, M_glove)
            ccorr = content_corr_stats(x)
            curve = []
            preds_hi = None
            for D in diversity_levels:
                g_hat, proto = learn(train_by_D[D], n_roles, g_true, x, n_dim)
                acc_h, pf, pl = evaluate(test_held, g_true, g_hat, proto, x, n_fillers)
                acc_i, _, _ = evaluate(test_ind, g_true, g_hat, proto, x, n_fillers)
                gcos = float(sim_to_codebook_diag(g_hat, g_true).mean())
                curve.append({
                    "D": D,
                    "factored_heldout": acc_h["factored_present"], "flat_heldout": acc_h["flat_present"],
                    "factored_indist": acc_i["factored_present"], "flat_indist": acc_i["flat_present"],
                    "factored_heldout_vocab": acc_h["factored_vocab"], "flat_heldout_vocab": acc_h["flat_vocab"],
                    "g_hat_to_g_true_cos": gcos,
                })
                preds_hi = (pf, pl)
            cond_results[cond] = {"curve": curve, "content_corr": ccorr, "preds_hi": preds_hi}
        per_seed.append({"seed": seed, "conditions": cond_results})
    return chance, per_seed


def sim_to_codebook_diag(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Row-wise FHRR similarity between two (K,N) codebooks. Returns (K,)."""
    n = a.shape[-1]
    return (a * b.conj()).sum(dim=-1).real / n


def hash_str(s: str) -> int:
    """Deterministic (NOT salted-builtin) small int from a string, for per-condition generator
    offsets. Uses hashlib (deterministic across processes; F.5-compliant)."""
    return int.from_bytes(hashlib.sha256(s.encode("utf-8")).digest()[:4], "big") % 1000003


def _stress_factored_vocab(n_dim, n_roles, n_fillers, m, held_per_role, D, n_test, seed, beta,
                           whiten_kpc, M_glove):
    """One (m, beta, seed) stress cell: FACTORED VOCAB held-out accuracy (hard readout among all
    fillers) + measured content correlation + g_hat->g_true cosine."""
    rng = random.Random(seed)
    gen = torch.Generator().manual_seed(seed)
    g_true = make_atoms(n_roles, n_dim, torch.complex64, gen)
    held_out, tb, hb = build_split(n_roles, n_fillers, held_per_role, rng)
    tr = [sample_train_sentence(m, tb, held_out, random.Random(seed * 1000 + D + int(beta * 100)))
          for _ in range(D)]
    th = make_test_set("heldout", n_test, m, tb, hb, held_out, random.Random(seed + 200000))
    gen_c = torch.Generator().manual_seed(seed * 31 + int(beta * 1000) + whiten_kpc)
    M_unit = (M_glove / torch.clamp(M_glove.norm(dim=1, keepdim=True), min=1e-8)
              if whiten_kpc == 0 else whiten_topk_pc(M_glove, whiten_kpc))
    x = glove_to_fhrr(M_unit, n_dim, beta, gen_c)
    g_hat, proto = learn(tr, n_roles, g_true, x, n_dim)
    acc, _, _ = evaluate(th, g_true, g_hat, proto, x, n_fillers)
    return (content_corr_stats(x)["content_cos_mean"], acc["factored_vocab"],
            acc["factored_present"], float(sim_to_codebook_diag(g_hat, g_true).mean()))


def stress_map(n_dim, n_roles, n_fillers, held_per_role, ms, betas, D, n_test, seeds, whiten_kpc):
    """(binding-load m x content-correlation beta) stress map on the HARD vocab readout. Real GloVe
    geometry throughout; beta sets overall correlation. Exposes the FHRR/SHRUTI superposition ceiling
    (crosstalk grows with m AND with content correlation). Plus a whitening probe at the most-broken
    cell (highest m, highest correlation) to test whether top-PC decorrelation RESTORES it."""
    import statistics as st
    vocab = VOCAB[:n_fillers]
    M_glove = load_glove_vectors(vocab)
    rows = []
    for m in ms:
        for beta in betas:
            cc, fv, fp, gc = [], [], [], []
            for seed in seeds:
                c, v, p, g = _stress_factored_vocab(n_dim, n_roles, n_fillers, m, held_per_role, D,
                                                    n_test, seed, beta, 0, M_glove)
                cc.append(c); fv.append(v); fp.append(p); gc.append(g)
            rows.append({"m": m, "beta": beta, "content_cos_mean": st.mean(cc),
                         "factored_vocab_heldout": st.mean(fv),
                         "factored_present_heldout": st.mean(fp), "g_hat_cos": st.mean(gc)})
    # Whitening probe at the most-broken cell (max m, min beta = highest correlation).
    m_max, beta_min = max(ms), min(betas)
    raw_fv, whit_fv, raw_cc, whit_cc = [], [], [], []
    for seed in seeds:
        c0, v0, _, _ = _stress_factored_vocab(n_dim, n_roles, n_fillers, m_max, held_per_role, D,
                                              n_test, seed, beta_min, 0, M_glove)
        c1, v1, _, _ = _stress_factored_vocab(n_dim, n_roles, n_fillers, m_max, held_per_role, D,
                                              n_test, seed, beta_min, whiten_kpc, M_glove)
        raw_fv.append(v0); whit_fv.append(v1); raw_cc.append(c0); whit_cc.append(c1)
    whiten_probe = {
        "m": m_max, "beta": beta_min, "whiten_kpc": whiten_kpc,
        "raw_content_cos": st.mean(raw_cc), "whitened_content_cos": st.mean(whit_cc),
        "raw_factored_vocab": st.mean(raw_fv), "whitened_factored_vocab": st.mean(whit_fv),
        "whitening_restores": bool(st.mean(whit_fv) - st.mean(raw_fv) >= 0.15),
        "note": ("top-PC whitening reduces GloVe anisotropy but at low beta the content-correlation "
                 "FLOOR is set by the encoding bandwidth (content_cos>=exp(-beta^2) even for orthogonal "
                 "GloVe), so decorrelating GloVe cannot fix the extreme-correlation break there; the "
                 "effective fix is a higher-bandwidth/sparser content code (more orthogonal FHRR)."),
    }
    return {"rows": rows, "whiten_probe": whiten_probe}


# ----------------------------------------------------------------------------------------------
# Aggregate + verdict.
# ----------------------------------------------------------------------------------------------
def cond_curve_mean(per_seed, cond, diversity_levels):
    import statistics as st
    keys = ["factored_heldout", "flat_heldout", "factored_indist", "flat_indist",
            "factored_heldout_vocab", "flat_heldout_vocab", "g_hat_to_g_true_cos"]
    curve = []
    for i, D in enumerate(diversity_levels):
        row = {"D": D}
        for k in keys:
            row[k] = st.mean([s["conditions"][cond]["curve"][i][k] for s in per_seed])
        curve.append(row)
    return curve


def cond_content_corr(per_seed, cond):
    import statistics as st
    return {k: st.mean([s["conditions"][cond]["content_corr"][k] for s in per_seed])
            for k in per_seed[0]["conditions"][cond]["content_corr"]}


def aggregate(chance, per_seed, diversity_levels, conditions):
    summ = {}
    for cond in conditions:
        cm = cond_curve_mean(per_seed, cond, diversity_levels)
        hi = cm[-1]
        summ[cond] = {
            "curve_mean": cm,
            "content_corr": cond_content_corr(per_seed, cond),
            "factored_heldout_hi": hi["factored_heldout"],
            "flat_heldout_hi": hi["flat_heldout"],
            "gap_heldout_hi": hi["factored_heldout"] - hi["flat_heldout"],
            "factored_indist_hi": hi["factored_indist"],
            "flat_indist_hi": hi["flat_indist"],
            "factored_gen_drop": hi["factored_indist"] - hi["factored_heldout"],
            "flat_gen_drop": hi["flat_indist"] - hi["flat_heldout"],
            "g_hat_cos_hi": hi["g_hat_to_g_true_cos"],
        }

    def mustfail(c):
        # FLAT genuinely FAILS on held-out real combinations = at/below chance AND FACTORED beats it
        # by a wide margin. NOTE (real-content finding): with CORRELATED content the flat baseline
        # moves from "systematically wrong (<< chance, the synthetic/orthogonal signature: content f*
        # is the single lowest-similarity present candidate)" UP TO "~chance" (correlated f* partially
        # matches the role prototype, removing the systematic anti-signal) -- both are failures. The
        # discriminator is the FACTORED-FLAT gap, not a generalization DROP (which the orthogonal case
        # shows but the correlated case need not).
        return (summ[c]["flat_heldout_hi"] <= 0.45) and (summ[c]["gap_heldout_hi"] >= 0.30)

    def void(c):
        return summ[c]["flat_heldout_hi"] > 0.60

    syn = summ.get("synthetic_orthogonal")
    real = summ.get("glove_real")
    whit = summ.get("glove_whitened")

    positive_control = bool(syn and syn["factored_heldout_hi"] >= 0.80 and syn["gap_heldout_hi"] >= 0.30)
    real_mustfail = bool(real and mustfail("glove_real"))
    real_void = bool(real and void("glove_real"))
    real_generalizes = bool(
        real and real["factored_heldout_hi"] >= 0.80 and real["gap_heldout_hi"] >= 0.30
        and real_mustfail
        and (syn is not None and (syn["factored_heldout_hi"] - real["factored_heldout_hi"]) <= 0.10)
    )
    real_breaks = bool(
        real and (real["gap_heldout_hi"] <= 0.05 or real["factored_heldout_hi"] <= chance + 0.05
                  or (syn is not None and (syn["factored_heldout_hi"] - real["factored_heldout_hi"]) >= 0.30))
    )
    whitening_restores = bool(
        whit and real and (whit["factored_heldout_hi"] - real["factored_heldout_hi"]) >= 0.15
        and whit["factored_heldout_hi"] >= 0.80
    )

    if not positive_control:
        verdict = "HARD_FAIL_POSITIVE_CONTROL"
    elif real_void:
        verdict = "VOID_FLAT_GENERALIZES_ON_REAL"
    elif real_generalizes:
        verdict = "HARD_PASS_CG_CANDIDATE"
    elif real_breaks and whitening_restores:
        verdict = "HARD_FAIL_CORRELATION_BREAKS_FIXED_BY_WHITENING"
    elif real_breaks:
        verdict = "HARD_FAIL_CORRELATION_BREAKS_UNFIXED"
    else:
        verdict = "MIDDLE_BAND"

    return {
        "verdict": verdict,
        "chance": chance,
        "per_condition": summ,
        "positive_control_reproduces_v1": positive_control,
        "real_must_fail_control_fired": real_mustfail,
        "real_generalizes": real_generalizes,
        "real_breaks": real_breaks,
        "whitening_restores": whitening_restores,
        "can_fail_both_ways": True,
    }


# ----------------------------------------------------------------------------------------------
# Arms-must-differ (META_RULE_AF): FACTORED vs FLAT predictions (glove_real) must NOT be identical.
# ----------------------------------------------------------------------------------------------
def arms_differ(per_seed, cond="glove_real"):
    """FACTORED vs FLAT predictions on the same held-out set (the two mechanism arms) must differ."""
    pf, pl = per_seed[0]["conditions"][cond]["preds_hi"]
    hpf = hashlib.sha256(bytes(pf)).hexdigest()
    hpl = hashlib.sha256(bytes(pl)).hexdigest()
    assert hpf != hpl, (f"META_RULE_AF: FACTORED and FLAT held-out preds bit-identical on {cond} "
                        f"({hpf}); arm-implementation bug")
    assert len(set(pf)) > 1, f"META_RULE_AF: {cond} FACTORED preds degenerate (all identical filler)"
    return {f"{cond}_factored_pred_hash": hpf, f"{cond}_flat_pred_hash": hpl}


# ----------------------------------------------------------------------------------------------
# Scaffold-free witness (self-test): REAL hdlab.binding.bind/unbind + REAL GloVe vectors; one
# hand-built held-out combination -> FACTORED unbinds the correct filler, FLAT does not.
# ----------------------------------------------------------------------------------------------
def scaffold_free_witness():
    n = 1024
    vocab = ["dog", "cat", "car", "apple"]  # real grounded, CORRELATED (dog~cat)
    M = load_glove_vectors(vocab)
    M_unit = M / torch.clamp(M.norm(dim=1, keepdim=True), min=1e-8)
    gen = torch.Generator().manual_seed(11)
    x = glove_to_fhrr(M_unit, n, BETA_REAL, gen)  # REAL correlated content, FHRR
    g = make_atoms(3, n, torch.complex64, gen)
    AGENT, PATIENT, GOAL = 0, 1, 2
    DOG, CAT, CAR, APPLE = 0, 1, 2, 3

    # Parity: bulk fhrr ops must equal REAL hdlab.binding on a witness (exercise real code path).
    b_bulk = fhrr_bind(g[AGENT], x[DOG])
    b_real = hdlab_bind(g[AGENT], x[DOG])
    assert torch.allclose(b_bulk, b_real), "fhrr_bind != hdlab.binding.bind"
    u_bulk = fhrr_unbind(b_bulk, x[DOG])
    u_real = hdlab_unbind(b_real, x[DOG])
    assert torch.allclose(u_bulk, u_real), "fhrr_unbind != hdlab.binding.unbind"

    # Confirm content is genuinely correlated (dog-cat > dog-car), the real-content premise.
    dc = float(sim_to_codebook(x[DOG], x[CAT].unsqueeze(0))[0])
    dcar = float(sim_to_codebook(x[DOG], x[CAR].unsqueeze(0))[0])
    assert dc > dcar, f"witness: real content not correlated as expected (dog-cat {dc:.3f} !> dog-car {dcar:.3f})"

    # Training: CAR seen only as PATIENT (never AGENT). AGENT trained with DOG, CAT.
    train = [
        {AGENT: DOG, PATIENT: CAT},
        {AGENT: CAT, PATIENT: CAR},   # CAR as PATIENT (grounds x[CAR], never AGENT)
        {AGENT: DOG, GOAL: APPLE},
        {AGENT: CAT, GOAL: APPLE},
    ]
    g_hat = torch.zeros((3, n), dtype=torch.complex64)
    proto = torch.zeros((3, n), dtype=torch.complex64)
    cnt = torch.zeros(3)
    for assign in train:
        S = torch.stack([hdlab_bind(g[r], x[f]) for r, f in sorted(assign.items())], 0).sum(0)
        for r, f in assign.items():
            g_hat[r] += hdlab_unbind(S, x[f])
            proto[r] += x[f]
            cnt[r] += 1
    g_hat = unit_phase(g_hat / torch.clamp(cnt, min=1.0).unsqueeze(1))
    proto = unit_phase(proto / torch.clamp(cnt, min=1.0).unsqueeze(1))

    # Held-out sentence: {AGENT: CAR, PATIENT: DOG}. Query AGENT. Present = {CAR, DOG}.
    S = torch.stack([hdlab_bind(g[AGENT], x[CAR]), hdlab_bind(g[PATIENT], x[DOG])], 0).sum(0)
    present = [DOG, CAR]
    cb = torch.stack([x[f] for f in present], 0)
    est = hdlab_unbind(S, g_hat[AGENT])
    fac_pred = present[int(torch.argmax(sim_to_codebook(est, cb)))]
    flat_pred = present[int(torch.argmax(sim_to_codebook(proto[AGENT], cb)))]
    assert fac_pred == CAR, f"witness: FACTORED failed to recover held-out AGENT=CAR (got {fac_pred})"
    assert flat_pred != CAR, f"witness: FLAT unexpectedly recovered held-out combo (got {flat_pred})"
    return {"factored_pred": "car", "flat_pred": "dog", "dog_cat_cos": round(dc, 3),
            "dog_car_cos": round(dcar, 3), "witness": "PASS"}


# ----------------------------------------------------------------------------------------------
# Config presets.
# ----------------------------------------------------------------------------------------------
PRIMARY_CONDITIONS = ["synthetic_orthogonal", "glove_real", "glove_whitened"]


def cfg_smoke():
    return dict(n_dim=2048, n_roles=4, n_fillers=24, m=3, held_per_role=2,
                diversity_levels=[8, 64], n_test=120, seeds=[7, 13],
                conditions=PRIMARY_CONDITIONS)


def cfg_full():
    return dict(n_dim=4096, n_roles=6, n_fillers=64, m=3, held_per_role=4,
                diversity_levels=[4, 16, 64, 256], n_test=300, seeds=[7, 13, 19],
                conditions=PRIMARY_CONDITIONS)


def cfg_stress_smoke():
    return dict(n_dim=1024, n_roles=12, n_fillers=40, held_per_role=4, ms=[3, 10],
                betas=[2.4, 0.8], D=16, n_test=120, seeds=[7], whiten_kpc=WHITEN_KPC)


def cfg_stress_full():
    # N=1024 stress dimensionality (exposes the crosstalk ceiling within reach; brain-faithful m=3-4
    # is far inside capacity). betas: 2.4~orthogonal, 1.5~GloVe-native, 0.8~extreme correlation.
    return dict(n_dim=1024, n_roles=12, n_fillers=40, held_per_role=4, ms=[3, 6, 10],
                betas=[2.4, 1.5, 0.8], D=16, n_test=300, seeds=[7, 13, 19], whiten_kpc=WHITEN_KPC)


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    stress_cfg = cfg_stress_smoke() if mode == "smoke" else cfg_stress_full()
    output_dir = os.path.join(REPO_ROOT, "data",
                              f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))

    witness = scaffold_free_witness()
    chance, per_seed = run_config(**cfg)
    agg = aggregate(chance, per_seed, cfg["diversity_levels"], cfg["conditions"])
    hashes = arms_differ(per_seed, "glove_real")
    stress = stress_map(**stress_cfg)

    elapsed = time.perf_counter() - t0
    v = agg["verdict"]
    syn = agg["per_condition"]["synthetic_orthogonal"]
    real = agg["per_condition"]["glove_real"]
    whit = agg["per_condition"]["glove_whitened"]
    msg = (f"{v} | SYN(control) F_held={syn['factored_heldout_hi']:.3f} gap={syn['gap_heldout_hi']:.3f} "
           f"| REAL F_held={real['factored_heldout_hi']:.3f} FLAT_held={real['flat_heldout_hi']:.3f} "
           f"gap={real['gap_heldout_hi']:.3f} corr={real['content_corr']['content_cos_mean']:.3f} "
           f"| WHIT F_held={whit['factored_heldout_hi']:.3f} corr={whit['content_corr']['content_cos_mean']:.3f} "
           f"| posctrl={agg['positive_control_reproduces_v1']} mustfail={agg['real_must_fail_control_fired']} "
           f"realgen={agg['real_generalizes']} realbreak={agg['real_breaks']} whiten_fix={agg['whitening_restores']} "
           f"chance={chance:.3f}")

    payload = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": mode,
        "verdict": v,
        "verdict_msg": msg,
        "summary": msg,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {k: (v2 if not isinstance(v2, list) else v2) for k, v2 in cfg.items()},
        "chance": chance,
        "aggregate": agg,
        "stress_map": stress,
        "arms_differ_hashes": hashes,
        "arms_differ_verified": True,
        "scaffold_free_witness": witness,
        "final_metrics_atomicity": "tmp_replace",
        "content_source": "REAL GloVe-wiki-gigaword-300 (Pennington et al. 2014); FHRR phase-encoded",
        "notes": ("CHAIN-GRADE PROMOTION gate: structure-content factorization on REAL correlated "
                  "grounded content (GloVe). HARD_PASS_CG_CANDIDATE = compositional generalization on "
                  "real correlated content where flat fails (brain-faithful native bind); still uses a "
                  "CURATED relation set (controlled roles) -- full real-text-from-reading with REAL "
                  "extracted relations (ConceptNet/SVO) is the further step. CLAIM-VET-pending."),
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    for cond in cfg["conditions"]:
        cc = agg["per_condition"][cond]
        print(f"  [{cond}] content_cos_mean={cc['content_corr']['content_cos_mean']:.3f} "
              f"F_held={cc['factored_heldout_hi']:.3f} FLAT_held={cc['flat_heldout_hi']:.3f} "
              f"gap={cc['gap_heldout_hi']:.3f} F_ind={cc['factored_indist_hi']:.3f} "
              f"FLAT_ind={cc['flat_indist_hi']:.3f} F_gendrop={cc['factored_gen_drop']:.3f} "
              f"FLAT_gendrop={cc['flat_gen_drop']:.3f} gcos={cc['g_hat_cos_hi']:.3f}", flush=True)
        for c in cc["curve_mean"]:
            print(f"      D={c['D']:>4} F_held={c['factored_heldout']:.3f} FLAT_held={c['flat_heldout']:.3f} "
                  f"F_ind={c['factored_indist']:.3f} vocab_F_held={c['factored_heldout_vocab']:.3f} "
                  f"gcos={c['g_hat_to_g_true_cos']:.3f}", flush=True)
    print("  [stress_map] (m x correlation on HARD vocab readout; real GloVe geometry; "
          "beta down = correlation up)", flush=True)
    for r in stress["rows"]:
        print(f"      m={r['m']:>2} beta={r['beta']:.2f} content_cos={r['content_cos_mean']:.3f} "
              f"F_vocab_held={r['factored_vocab_heldout']:.3f} F_pres_held={r['factored_present_heldout']:.3f} "
              f"gcos={r['g_hat_cos']:.3f}", flush=True)
    wp = stress["whiten_probe"]
    print(f"  [whiten_probe] m={wp['m']} beta={wp['beta']} raw_corr={wp['raw_content_cos']:.3f} "
          f"whit_corr={wp['whitened_content_cos']:.3f} raw_Fvocab={wp['raw_factored_vocab']:.3f} "
          f"whit_Fvocab={wp['whitened_factored_vocab']:.3f} restores={wp['whitening_restores']}", flush=True)
    print(f"  [witness] {witness}", flush=True)
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        w = scaffold_free_witness()
        print(f"[{ANCHOR_NAME}] self-test scaffold-free witness: {w}", flush=True)
        chance, per_seed = run_config(n_dim=512, n_roles=4, n_fillers=16, m=3, held_per_role=2,
                                      diversity_levels=[16, 64], n_test=40, seeds=[7],
                                      conditions=PRIMARY_CONDITIONS)
        agg = aggregate(chance, per_seed, [16, 64], PRIMARY_CONDITIONS)
        arms_differ(per_seed, "glove_real")
        real = agg["per_condition"]["glove_real"]
        syn = agg["per_condition"]["synthetic_orthogonal"]
        print(f"[{ANCHOR_NAME}] self-test end-to-end: verdict={agg['verdict']} "
              f"SYN_F_held={syn['factored_heldout_hi']:.3f} REAL_F_held={real['factored_heldout_hi']:.3f} "
              f"REAL_corr={real['content_corr']['content_cos_mean']:.3f} "
              f"REAL_gap={real['gap_heldout_hi']:.3f}", flush=True)
        return
    if args.smoke:
        run_mode("smoke")
        return
    if args.full:
        run_mode("full")
        return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
            "summary": f"CELL_CRASHED: {type(e).__name__}",
            "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
        }
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
