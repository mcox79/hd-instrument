"""learned_meaning_frontend_differentiation_v1 -- FIRST component of the LEARNED meaning front-end.

WALL (atom 29555, VET-confirmed across ~10 ARC experiments): the substrate cannot tell the CORRECT
fine content from a lexically-similar-but-WRONG alternative over thin frozen GloVe/WordNet meaning
(hydro/nuclear/coal conflate as "energy"; entailing vs merely-similar facts). Oracle-given-facts = 0.69
=> the reasoning/combiner already works; the MEANING representation is the wall. 29546 (relational
STRUCTURE) closed the structure axis; 29547 HAND-BOUND properties and failed answer-agnostic selection.
This cell opens the DIFFERENT lever the note names: a LEARNED front-end that LEARNS the differentiation
from data (error-driven property completion) rather than WIRING it.

DESIGN (implements notes/research_learned_meaning_frontend_differentiation_2026-07-25.md pre-reg):
Rumelhart/Rogers-McClelland item+relation -> property-completion hub (small glass-box MLP), trained by
error-driven backprop over a curated real-concept environment. The FROZEN GloVe/WordNet meaning vector
(SemanticHDEncoder.fused, the ACTUAL conflated baseline used across 29544/45/46) is the hub INPUT; the
hub LEARNS to map concept(+relation) into a meaning vector that DISCRIMINATES the fine contrast the
frozen rep conflates. ONE VARIABLE = LEARNED front-end vs FROZEN GloVe (the eval question + the property
targets are IDENTICAL for both arms; only the concept->meaning transform differs).

DIFFERENTIATION METRIC (the note's METRIC; concept recovery among a minimal-pair contrast set):
For a minimal-pair contrast set S (e.g. {solar,wind,hydroelectric,geothermal,coal,nuclear}) and a
relation r, probe = the TRUE property meaning-vector of the query concept c* under r. Both arms score
each candidate concept c in S and pick argmax; correct iff c*.
  LEARNED score(c) = cos( hub(fused(c), onehot(r)) , probe )
  FROZEN  score(c) = cos( fused(c) , probe )                     [today's conflated frozen GloVe]
Because the design choice makes the property TARGET a real GloVe/WordNet meaning vector (property phrase
embedded by the SAME SemanticHDEncoder), the frozen arm is literally the "frozen-GloVe-cosine baseline"
the note names, and the ONLY difference between arms is the learned hub transform.

  COARSE tier (high shared-variance): category recovery (renewable vs nonrenewable; precious vs base; ...)
  FINE   tier (low shared-variance): exact-concept recovery within the contrast set (hydro vs nuclear...)

PRIMARY = the LEARNING CURVE: fine-tier discrimination accuracy vs #exposures (training epochs), for the
LEARNED arm, against the FROZEN baseline (flat, no learning) and the SHUFFLED-label must-fail control.
The flexible/IMPROVING property the USER requires = the curve rises with exposure.

CONTROLS / GATES (pre-registered a priori in the note; bands below):
- MUST-FAIL: SHUFFLED-label arm (property targets permuted across concepts within-relation; marginals
  preserved, item->property mapping destroyed). Its curve MUST stay materially below the real arm; if it
  rises to match, the "learning" is memorization/leak and the cell is INVALIDATED.
- COMPOSITIONAL-GENERALIZATION probe (diagnostic, NOT gating per note): held-out (concept,relation) pairs
  never trained (same-item/new-relation). Report separately; a flat here is expected+in-scope.
- NEAR-DEGENERATE-SEED pre-check (difficulty-on): pairwise cosine among the frozen fused vectors of each
  contrast set; confirm frozen conflates (so learning has something real to fix) and flag garbage-in if
  degenerate (>~0.9) OR task-too-easy if frozen fine accuracy already high.
- COARSE-BEFORE-FINE ordering (note pred #1): per-domain, coarse crosses 80%-of-asymptote at fewer
  exposures than fine, for >=3 domains.

VERDICT (author-designed a priori from the note):
  HARD_PASS  = fine lift (learned max-exposure - frozen) >= REL_LIFT_HP AND real-vs-shuffled separation
               >= SHUFFLE_SEP AND shuffled stays flat AND coarse-before-fine holds for >=3 domains.
  MIDDLE     = fine lift in [REL_LIFT_HF, REL_LIFT_HP) with control holding (learning real but modest).
  HARD_FAIL  = fine lift < REL_LIFT_HF -> learned front-end does not out-differentiate frozen -> pivot to
               grounded/richer-INPUT front-end (Barsalou/Lambon-Ralph); report STRAIGHT + sub-diagnosis
               (near-degenerate seed vs mechanism).
  INVALID    = shuffled control rises >= real (leak/memorization) OR neither curve rises (pipeline).
NO tuning to force a win (H, LR, epochs, schedule all a priori).

Contract: INLINE-LOCAL foreground-to-completion (GloVe/WordNet git-ignored/large -> NOT remote-portable;
inherits 29544/45/46 contract); NO push/remote-persist; ASCII-only; deterministic (fixed int seeds,
numpy default_rng, sorted iteration; no builtin-hash-seeded RNG); repo .venv; agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker at entry ; crash-diagnostic metrics ; heartbeat
# - real_code_path: self_test builds REAL SemanticHDEncoder + REAL meaning_vec + REAL hub train/eval +
#   REAL near-degenerate pre-check at tiny scale; PLANTED separable env asserts the hub LEARNS to
#   discriminate (learned curve rises to ~1) where FROZEN stays ~chance and SHUFFLED stays flat
# - arms_differ: learned vs frozen vs shuffled discrimination scores differ (hash + value asserts)
# - no-leak: compositional probe pairs held out of training; shuffled control guards in-vocab memorization
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no builtin-hash
# - baseline_in_band: FROZEN fine accuracy checked in (near-chance, not-saturated) band at smoke
# - discriminator_fires: LEARNED fine curve must rise above FROZEN in smoke (else respec, not dispatch)
# - storage = no_composition (self-contained differentiation cell; fixed-VSA selection stage UNCHANGED)
# - GLASS-BOX: hub is a small inspectable MLP; per-concept bottleneck separation logged
# - all reported numbers MEASURED@ this cell's metrics.json
"""
from __future__ import annotations

import os
import sys
import json
import time
import argparse
import platform
import traceback
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (  # noqa: E402
    SemanticHDEncoder, _load_glove, _load_wordnet)

ANCHOR_NAME = "learned_meaning_frontend_differentiation_v1"
SEED = 20260725
PRETRAIN_DIM = 300

# ---------------------------------------------------------------------------
# Concept environment: minimal-pair contrast SETS (real GloVe-vocab concepts) with a COARSE category
# (high shared-variance) + FINE per-concept distinctive properties (low shared-variance). Property values
# are ordinary words -> embedded by the SAME frozen SemanticHDEncoder -> the property TARGET vector. These
# are TRAINING SUPERVISION (the environment statistics, Rogers-McClelland style), NOT hand-wired answers:
# the hub LEARNS the map and is judged on a shuffled-label must-fail + held-out probe.
# ---------------------------------------------------------------------------
DOMAINS = {
    # each concept: 1 COARSE relation (category, category-shared) + 3 FINE relations. Two fine relations
    # are per-concept DISTINCTIVE (source/device/property/feature/... -> real fine discrimination); one is
    # CATEGORY-CORRELATED (byproduct/source/moons/body -> a learnable shared-structure signal so held-out
    # same-item/new-relation generalization is a FAIR, in-scope test rather than impossible-by-design).
    "energy": {
        "solar":         {"category": "renewable",    "source": "sunlight", "device": "panel",   "byproduct": "clean"},
        "wind":          {"category": "renewable",    "source": "air",      "device": "turbine", "byproduct": "clean"},
        "hydroelectric": {"category": "renewable",    "source": "water",    "device": "dam",     "byproduct": "clean"},
        "geothermal":    {"category": "renewable",    "source": "heat",     "device": "well",    "byproduct": "clean"},
        "coal":          {"category": "nonrenewable", "source": "carbon",   "device": "furnace", "byproduct": "smoke"},
        "nuclear":       {"category": "nonrenewable", "source": "uranium",  "device": "reactor", "byproduct": "radiation"},
    },
    "metal": {
        "gold":     {"category": "precious", "property": "shiny",      "use": "jewelry", "source": "nugget"},
        "silver":   {"category": "precious", "property": "reflective", "use": "coin",    "source": "nugget"},
        "iron":     {"category": "base",     "property": "magnetic",   "use": "steel",   "source": "ore"},
        "copper":   {"category": "base",     "property": "reddish",    "use": "wire",    "source": "ore"},
        "aluminum": {"category": "base",     "property": "light",      "use": "foil",    "source": "ore"},
        "lead":     {"category": "base",     "property": "heavy",      "use": "battery", "source": "ore"},
    },
    "planet": {
        "mercury": {"category": "rocky", "property": "hot",    "feature": "cratered", "moons": "none"},
        "venus":   {"category": "rocky", "property": "cloudy", "feature": "volcanic", "moons": "none"},
        "mars":    {"category": "rocky", "property": "red",    "feature": "dusty",    "moons": "two"},
        "jupiter": {"category": "gas",   "property": "huge",   "feature": "stormy",   "moons": "many"},
        "saturn":  {"category": "gas",   "property": "ringed", "feature": "golden",   "moons": "many"},
        "neptune": {"category": "gas",   "property": "blue",   "feature": "windy",    "moons": "many"},
    },
    "animal": {
        "shark":   {"category": "fish", "property": "predator", "habitat": "ocean",  "body": "fins"},
        "salmon":  {"category": "fish", "property": "pink",     "habitat": "river",  "body": "fins"},
        "tuna":    {"category": "fish", "property": "fast",     "habitat": "ocean",  "body": "fins"},
        "eagle":   {"category": "bird", "property": "soaring",  "habitat": "cliff",  "body": "wings"},
        "sparrow": {"category": "bird", "property": "tiny",     "habitat": "garden", "body": "wings"},
        "penguin": {"category": "bird", "property": "black",    "habitat": "ice",    "body": "wings"},
    },
}

# global relation vocabulary (onehot order fixed -> deterministic)
RELATIONS = ("category", "source", "device", "byproduct", "property", "use", "feature", "moons",
             "habitat", "body")
COARSE_REL = "category"
FINE_RELS = tuple(r for r in RELATIONS if r != COARSE_REL)
REL_IDX = {r: i for i, r in enumerate(RELATIONS)}
NREL = len(RELATIONS)

# ---------------------------------------------------------------------------
# hub hyperparameters (a priori; NOT tuned for PASS)
# ---------------------------------------------------------------------------
H_BOTTLENECK = 32        # hidden bottleneck width (small; forces structure over rote memorization)
LR = 0.1                 # full-batch GD learning rate (stable a priori; verified converge on planted env)
GRAD_CLIP = 1.0          # per-matrix gradient-norm clip (optimizer-stability safety net; inactive at LR=0.1)
WEIGHT_DECAY = 1e-4      # tiny L2 (regularizes toward structured/low-rank maps; helps shuffled fail)
EXPOSURE_SCHED_FULL = (0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512)
EXPOSURE_SCHED_SMOKE = (0, 4, 32, 128)
HELDOUT_FRAC = 0.18      # fraction of (concept,relation) pairs held out for the compositional probe

# ---------------------------------------------------------------------------
# pre-registered bands (author-designed a priori; from the note's predictions)
# ---------------------------------------------------------------------------
REL_LIFT_HP = 0.25       # note pred #4: learned fine (max exposure) - frozen fine >= this -> HARD_PASS lift
REL_LIFT_HF = 0.10       # note pred #4: fine lift < this -> HARD_FAIL (no material out-differentiation)
SHUFFLE_SEP = 0.15       # real fine (max exposure) - shuffled fine (max exposure) >= this
SHUFFLE_FLAT = 0.12      # shuffled fine must stay within this of its exposure-0 value (control stays flat)
FROZEN_SAT = 0.85        # AG-guard: frozen fine >= this -> task too easy (no headroom) -> report + harden
DEGEN_COS = 0.90         # near-degenerate: mean pairwise fused cosine >= this in a set -> garbage-in risk
COARSE_FIRST_MIN_DOMAINS = 3  # note pred #1: coarse-before-fine ordering must hold for >= this many domains
ASYMPTOTE_FRAC = 0.80    # crossing threshold = 80% of the curve's own asymptote (note pred #1)

_T0 = [0.0]


# ---------------------------------------------------------------------------
# markers / crash diagnostics / heartbeat
# ---------------------------------------------------------------------------
def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir, stage, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


# ---------------------------------------------------------------------------
# frozen meaning vector (SemanticHDEncoder fused meaning; the ACTUAL conflated baseline)
# ---------------------------------------------------------------------------
def _l2(v, eps=1e-12):
    n = np.linalg.norm(v)
    return v / (n + eps) if n > 0 else v


def _tok(phrase):
    """Deterministic ASCII tokenizer: lowercase alpha runs of length >= 2."""
    out, cur = [], []
    for ch in phrase.lower():
        if ("a" <= ch <= "z"):
            cur.append(ch)
        else:
            if len(cur) >= 2:
                out.append("".join(cur))
            cur = []
    if len(cur) >= 2:
        out.append("".join(cur))
    return out


def meaning_vec(enc, phrase):
    """Frozen fused meaning vector (300d, L2) for a word/phrase; None if no GloVe/WordNet signal.
    Sum of per-token fused vectors -> L2. Stays in the interpretable 300d GloVe/WordNet meaning space
    (no JL projection): the frozen concept meaning and the property target live in the SAME space, so the
    frozen-cosine baseline and the learned arm answer an identically-shaped question (ONE variable)."""
    acc = np.zeros(PRETRAIN_DIM, dtype=np.float32)
    got = False
    for w in _tok(phrase):
        fv = enc.fused(w)
        if fv is not None:
            acc = acc + fv
            got = True
    return _l2(acc) if got else None


# ---------------------------------------------------------------------------
# environment assembly: (concept,relation)->target ; coverage-checked; OOV dropped+logged
# ---------------------------------------------------------------------------
def build_environment(enc, domains):
    """Return env: list of domain dicts, each with concept list, per-(concept,relation) target vectors,
    category labels, and frozen concept vectors. Drops (and records) any OOV concept/property."""
    env = []
    dropped = []
    for dname in sorted(domains.keys()):
        concepts = domains[dname]
        cnames = sorted(concepts.keys())
        cvec = {}          # concept -> frozen fused vector
        cat = {}           # concept -> category label
        targ = {}          # (concept, relation) -> target meaning vector
        kept = []
        for c in cnames:
            fv = meaning_vec(enc, c)
            if fv is None:
                dropped.append(f"{dname}:{c}(concept OOV)")
                continue
            props = concepts[c]
            ctgt = {}
            for rel, val in sorted(props.items()):
                if rel not in REL_IDX:
                    continue
                pv = meaning_vec(enc, val)
                if pv is None:
                    dropped.append(f"{dname}:{c}:{rel}={val}(prop OOV)")
                    continue
                ctgt[rel] = pv
            if COARSE_REL not in ctgt:
                dropped.append(f"{dname}:{c}(no coarse target)")
                continue
            cvec[c] = fv
            cat[c] = concepts[c]["category"]
            for rel, pv in ctgt.items():
                targ[(c, rel)] = pv
            kept.append(c)
        if len(kept) >= 3:
            env.append({"domain": dname, "concepts": kept, "cvec": cvec, "cat": cat, "targ": targ})
    return env, dropped


def near_degenerate_precheck(env):
    """Mean pairwise cosine among frozen concept vectors per domain (difficulty-on evidence)."""
    out = {}
    for d in env:
        cs = d["concepts"]
        V = np.stack([d["cvec"][c] for c in cs], axis=0)
        cosm = V @ V.T
        iu = np.triu_indices(len(cs), k=1)
        out[d["domain"]] = round(float(np.mean(cosm[iu])), 4) if iu[0].size else None
    return out


# ---------------------------------------------------------------------------
# training pairs (item+relation -> property target); held-out compositional split
# ---------------------------------------------------------------------------
def make_pairs(env, heldout_frac, seed):
    """Flatten env to (domain_idx, concept, relation, target) pairs; split TRAIN vs HELDOUT.
    HELDOUT = same-item/new-relation compositional probe: hold out a fraction of (concept,relation) pairs
    such that the concept still appears with OTHER relations in TRAIN and the relation still appears with
    OTHER concepts in TRAIN (deterministic; numpy default_rng; sorted)."""
    all_pairs = []
    for di, d in enumerate(env):
        for c in d["concepts"]:
            for rel in sorted({r for (cc, r) in d["targ"].keys() if cc == c}):
                if rel == COARSE_REL:
                    continue  # coarse always trained (shared category signal); probe holds out FINE rels
                all_pairs.append((di, c, rel))
    rng = np.random.default_rng(seed + 4242)
    order = rng.permutation(len(all_pairs))
    n_hold = int(round(heldout_frac * len(all_pairs)))
    held, train_set = set(), set()
    # tentatively hold out the first n_hold in permuted order, but only if it preserves coverage
    train_pairs = list(all_pairs)
    held_list = []
    # counts per (domain,concept) and (domain,relation) in the full fine set
    from collections import Counter
    cnt_cr = Counter((di, c) for (di, c, rel) in all_pairs)
    cnt_rr = Counter((di, rel) for (di, c, rel) in all_pairs)
    used_c = Counter()
    used_r = Counter()
    for oi in order.tolist():
        if len(held_list) >= n_hold:
            break
        di, c, rel = all_pairs[oi]
        # keep >=1 training pair for this concept and this relation within the domain
        if (cnt_cr[(di, c)] - used_c[(di, c)] - 1) >= 1 and (cnt_rr[(di, rel)] - used_r[(di, rel)] - 1) >= 1:
            held_list.append((di, c, rel))
            used_c[(di, c)] += 1
            used_r[(di, rel)] += 1
    held = set(held_list)
    train_fine = [p for p in all_pairs if p not in held]
    # coarse pairs (always in train)
    coarse_pairs = []
    for di, d in enumerate(env):
        for c in d["concepts"]:
            if (c, COARSE_REL) in d["targ"]:
                coarse_pairs.append((di, c, COARSE_REL))
    train_all = coarse_pairs + train_fine
    return train_all, sorted(held), coarse_pairs, train_fine


def _pair_matrix(env, pairs):
    """Build X_in [n,300+NREL] and Y [n,300] for a list of (domain_idx, concept, relation) pairs."""
    X = np.zeros((len(pairs), PRETRAIN_DIM + NREL), dtype=np.float32)
    Y = np.zeros((len(pairs), PRETRAIN_DIM), dtype=np.float32)
    for i, (di, c, rel) in enumerate(pairs):
        d = env[di]
        X[i, :PRETRAIN_DIM] = d["cvec"][c]
        X[i, PRETRAIN_DIM + REL_IDX[rel]] = 1.0
        Y[i] = d["targ"][(c, rel)]
    return X, Y


def shuffle_targets(env, seed):
    """MUST-FAIL control: permute property targets ACROSS concepts WITHIN (domain,relation) -- preserves
    the marginal target distribution per relation, destroys the item->property mapping. Deterministic."""
    rng = np.random.default_rng(seed + 9090)
    new_env = []
    for d in env:
        ntarg = dict(d["targ"])
        # per relation, permute the concept->target assignment
        rels = sorted({r for (_, r) in d["targ"].keys()})
        for rel in rels:
            cs = [c for c in d["concepts"] if (c, rel) in d["targ"]]
            if len(cs) < 2:
                continue
            perm = rng.permutation(len(cs))
            src = {cs[k]: d["targ"][(cs[perm[k]], rel)] for k in range(len(cs))}
            for c in cs:
                ntarg[(c, rel)] = src[c]
        nd = dict(d)
        nd["targ"] = ntarg
        new_env.append(nd)
    return new_env


# ---------------------------------------------------------------------------
# the LEARNED hub: 2-layer tanh MLP (item+relation -> property meaning vector), full-batch GD
# ---------------------------------------------------------------------------
class Hub:
    def __init__(self, in_dim, h, out_dim, seed):
        rng = np.random.default_rng(seed)
        self.W1 = (rng.standard_normal((in_dim, h)).astype(np.float32) / np.sqrt(in_dim))
        self.b1 = np.zeros(h, dtype=np.float32)
        self.W2 = (rng.standard_normal((h, out_dim)).astype(np.float32) / np.sqrt(h))
        self.b2 = np.zeros(out_dim, dtype=np.float32)

    def forward(self, X, cache=False):
        Z1 = X @ self.W1 + self.b1
        A1 = np.tanh(Z1)
        Yh = A1 @ self.W2 + self.b2
        if cache:
            return Yh, A1
        return Yh

    def bottleneck(self, X):
        return np.tanh(X @ self.W1 + self.b1)

    def train_epochs(self, X, Y, n_epochs, lr, wd, clip=GRAD_CLIP):
        n = max(1, X.shape[0])
        for _ in range(n_epochs):
            Yh, A1 = self.forward(X, cache=True)
            dYh = (2.0 / n) * (Yh - Y)
            dW2 = A1.T @ dYh + wd * self.W2
            db2 = dYh.sum(axis=0)
            dA1 = dYh @ self.W2.T
            dZ1 = dA1 * (1.0 - A1 * A1)
            dW1 = X.T @ dZ1 + wd * self.W1
            db1 = dZ1.sum(axis=0)
            if clip:
                for g in (dW1, db1, dW2, db2):
                    nrm = np.linalg.norm(g)
                    if nrm > clip:
                        g *= clip / nrm
            self.W1 -= lr * dW1
            self.b1 -= lr * db1
            self.W2 -= lr * dW2
            self.b2 -= lr * db2


# ---------------------------------------------------------------------------
# discrimination eval (concept recovery among the minimal-pair contrast set)
# ---------------------------------------------------------------------------
def _rel_onehot(rel):
    v = np.zeros(NREL, dtype=np.float32)
    v[REL_IDX[rel]] = 1.0
    return v


def learned_predict(hub, cvec, rel):
    """hub-completed property vector for a concept under a relation (L2)."""
    x = np.concatenate([cvec, _rel_onehot(rel)]).astype(np.float32)[None, :]
    return _l2(hub.forward(x)[0])


def fine_discrimination(env, pairs, hub=None):
    """Concept recovery among the domain contrast set S using each FINE (concept,relation) pair as probe.
    hub=None -> FROZEN arm (score = cos(fused(c), probe)); else LEARNED arm.
    Returns overall accuracy + per-domain accuracy."""
    per_dom_hit = {d["domain"]: [] for d in env}
    tot = 0
    hit = 0
    for (di, cstar, rel) in pairs:
        if rel == COARSE_REL:
            continue
        d = env[di]
        probe = d["targ"][(cstar, rel)]
        cs = d["concepts"]
        scores = np.zeros(len(cs), dtype=np.float64)
        for k, c in enumerate(cs):
            if hub is None:
                rep = d["cvec"][c]
            else:
                rep = learned_predict(hub, d["cvec"][c], rel)
            scores[k] = float(rep @ probe)
        pred = cs[int(np.argmax(scores))]
        ok = 1 if pred == cstar else 0
        per_dom_hit[d["domain"]].append(ok)
        hit += ok
        tot += 1
    acc = round(hit / tot, 4) if tot else None
    per_dom = {k: (round(float(np.mean(v)), 4) if v else None) for k, v in per_dom_hit.items()}
    return acc, per_dom, tot


def coarse_discrimination(env, hub=None):
    """Category recovery: probe = the concept's coarse (category) target; pick argmax concept over the
    contrast set; correct iff picked concept shares the query's CATEGORY (coarse tier is category-level)."""
    per_dom_hit = {d["domain"]: [] for d in env}
    hit = tot = 0
    for d in env:
        cs = d["concepts"]
        for cstar in cs:
            if (cstar, COARSE_REL) not in d["targ"]:
                continue
            probe = d["targ"][(cstar, COARSE_REL)]
            scores = np.zeros(len(cs), dtype=np.float64)
            for k, c in enumerate(cs):
                rep = d["cvec"][c] if hub is None else learned_predict(hub, d["cvec"][c], COARSE_REL)
                scores[k] = float(rep @ probe)
            pred = cs[int(np.argmax(scores))]
            ok = 1 if d["cat"][pred] == d["cat"][cstar] else 0
            per_dom_hit[d["domain"]].append(ok)
            hit += ok
            tot += 1
    acc = round(hit / tot, 4) if tot else None
    per_dom = {k: (round(float(np.mean(v)), 4) if v else None) for k, v in per_dom_hit.items()}
    return acc, per_dom, tot


def _crossing_exposure(exposures, accs, frac):
    """First exposure at which acc >= frac * asymptote (asymptote = max over the curve). None if never."""
    asy = max(a for a in accs if a is not None) if any(a is not None for a in accs) else 0.0
    if asy <= 0:
        return None
    thr = frac * asy
    for e, a in zip(exposures, accs):
        if a is not None and a >= thr:
            return e
    return None


def _sigmoid_vs_linear_aic(exposures, accs):
    """Coarse AIC comparison of a 3-param logistic vs a linear fit for a curve (note pred #2, diagnostic).
    Deterministic grid search for the logistic; closed-form linear. Returns dict with aic_delta (sigmoid
    favored if negative)."""
    x = np.array([float(e) for e, a in zip(exposures, accs) if a is not None], dtype=np.float64)
    y = np.array([float(a) for a in accs if a is not None], dtype=np.float64)
    if x.size < 4:
        return {"aic_linear": None, "aic_sigmoid": None, "aic_delta": None}
    xl = np.log1p(x)  # exposures span orders of magnitude -> fit in log-exposure
    # linear
    A = np.vstack([xl, np.ones_like(xl)]).T
    coef, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    rss_lin = float(np.sum((A @ coef - y) ** 2))
    # logistic: y ~ lo + (hi-lo)/(1+exp(-k*(xl-x0)))
    lo, hi = float(y.min()), float(y.max())
    best = None
    for x0 in np.linspace(xl.min(), xl.max(), 21):
        for k in np.linspace(0.3, 6.0, 20):
            pred = lo + (hi - lo) / (1.0 + np.exp(-k * (xl - x0)))
            rss = float(np.sum((pred - y) ** 2))
            if best is None or rss < best[0]:
                best = (rss, float(x0), float(k))
    rss_sig = best[0]
    n = x.size
    eps = 1e-9
    aic_lin = n * np.log(rss_lin / n + eps) + 2 * 2
    aic_sig = n * np.log(rss_sig / n + eps) + 2 * 4
    return {"aic_linear": round(float(aic_lin), 3), "aic_sigmoid": round(float(aic_sig), 3),
            "aic_delta": round(float(aic_sig - aic_lin), 3), "logistic_x0_k": [best[1], best[2]]}


# ---------------------------------------------------------------------------
# curve driver: train from scratch, checkpoint discrimination at exposure milestones
# ---------------------------------------------------------------------------
def exposure_curve(train_env, eval_env, train_pairs, eval_sets, schedule, seed, label, output_dir):
    """Train a hub from scratch on train_env/train_pairs; at each exposure milestone measure
    discrimination on eval_env. CRITICAL: train_env supplies the TRAINING targets (for the shuffled
    control these are permuted) while eval_env supplies the TRUE targets used for discrimination, so a
    hub that learned a WRONG (shuffled) mapping is scored against the TRUE task and must fail.
      eval_sets: dict name -> list of fine (domain_idx,concept,relation) eval pairs.
    Returns {exposures, sets:{name:{fine[],per_dom_fine[]}}, coarse[], per_dom_coarse[], hub}."""
    X, Y = _pair_matrix(train_env, train_pairs)
    hub = Hub(PRETRAIN_DIM + NREL, H_BOTTLENECK, PRETRAIN_DIM, seed=seed + 11)
    sets = {name: {"fine": [], "per_dom_fine": []} for name in eval_sets}
    coarse, pdc = [], []
    prev = 0
    for e in schedule:
        step = e - prev
        if step > 0:
            hub.train_epochs(X, Y, step, LR, WEIGHT_DECAY)
            prev = e
        for name, pairs in eval_sets.items():
            fa, fpd, _ = fine_discrimination(eval_env, pairs, hub=hub)
            sets[name]["fine"].append(fa)
            sets[name]["per_dom_fine"].append(fpd)
        ca, cpd, _ = coarse_discrimination(eval_env, hub=hub)
        coarse.append(ca)
        pdc.append(cpd)
        _heartbeat(output_dir, f"curve_{label}", {"exposure": e,
                   "fine": {n: sets[n]["fine"][-1] for n in eval_sets}, "coarse": ca})
    return {"exposures": list(schedule), "sets": sets, "coarse": coarse,
            "per_dom_coarse": pdc, "hub": hub}


# ---------------------------------------------------------------------------
# self-test: planted separable env (mechanism fires) + real code path (encoder + pre-check)
# ---------------------------------------------------------------------------
def _planted_mechanism(nd=64):
    """Planted separable environment: distinct random concept vectors + distinct random per-(concept,rel)
    targets. A hub MUST learn to complete them so fine discrimination rises to ~1, while the FROZEN arm
    (concept vector cosine) stays near chance and a SHUFFLED-target hub stays flat -> proves the learned
    mechanism + the discrimination metric fire, independent of GloVe."""
    rng = np.random.default_rng(31)
    n_c, n_r = 5, 3
    cvec = {f"c{i}": _l2(rng.standard_normal(nd).astype(np.float32)) for i in range(n_c)}
    cats = {f"c{i}": ("A" if i < 2 else "B") for i in range(n_c)}
    rels = ["category", "source", "property"]
    cat_vec = {"A": _l2(rng.standard_normal(nd).astype(np.float32)),
               "B": _l2(rng.standard_normal(nd).astype(np.float32))}
    targ = {}
    for i in range(n_c):
        # category target shared within a category (coarse, high shared-variance); fine targets distinct
        targ[(f"c{i}", "category")] = cat_vec[cats[f"c{i}"]]
        for r in ["source", "property"]:
            targ[(f"c{i}", r)] = _l2(rng.standard_normal(nd).astype(np.float32))
    env = [{"domain": "planted", "concepts": [f"c{i}" for i in range(n_c)], "cvec": cvec,
            "cat": cats, "targ": targ}]
    global PRETRAIN_DIM
    old = PRETRAIN_DIM
    PRETRAIN_DIM = nd
    try:
        fine_pairs = [(0, c, r) for (c, r) in targ.keys() if r != "category"]
        Xtr, Ytr = _pair_matrix(env, [(0, c, r) for (c, r) in targ.keys()])
        hub = Hub(nd + NREL, 24, nd, seed=7)
        # frozen fine accuracy (no hub)
        fa0, _, _ = fine_discrimination(env, fine_pairs, hub=None)
        hub.train_epochs(Xtr, Ytr, 800, LR, 0.0)
        fa1, _, _ = fine_discrimination(env, fine_pairs, hub=hub)
        # shuffled control: TRAIN on permuted targets, EVALUATE against the TRUE env targets. A hub that
        # learned the WRONG mapping is scored on the true task and must fail (-> ~chance).
        senv = shuffle_targets(env, seed=1)
        Xs, Ys = _pair_matrix(senv, [(0, c, r) for (c, r) in senv[0]["targ"].keys()])
        shub = Hub(nd + NREL, 24, nd, seed=7)
        shub.train_epochs(Xs, Ys, 800, LR, 0.0)
        fas, _, _ = fine_discrimination(env, fine_pairs, hub=shub)   # EVAL on TRUE env targets
    finally:
        PRETRAIN_DIM = old
    assert fa1 >= 0.9, f"planted: learned hub did not learn to discriminate (fine={fa1})"
    assert fa1 - fa0 >= 0.3, f"planted: learned did not lift over frozen (learned={fa1} frozen={fa0})"
    assert fa1 - fas >= 0.3, f"planted: shuffled(train)->true(eval) control not separated (learned={fa1} shuffled={fas})"
    return {"frozen_fine": fa0, "learned_fine": fa1, "shuffled_true_eval_fine": fas}


def self_test():
    print("[self-test] planted separable env: learned hub must discriminate (fine->~1), frozen ~chance, "
          "shuffled flat ...", flush=True)
    planted = _planted_mechanism()
    print(f"[self-test]   planted: {planted}", flush=True)

    print("[self-test] REAL code path: SemanticHDEncoder + meaning_vec + build_environment + "
          "near-degenerate pre-check + one real hub epoch ...", flush=True)
    kv = _load_glove()
    _load_wordnet()
    enc = SemanticHDEncoder(n_dim=512, seed=SEED, use_wordnet=True, kv=kv)
    # tiny real environment (energy domain only)
    tiny = {"energy": DOMAINS["energy"]}
    env, dropped = build_environment(enc, tiny)
    assert env and len(env[0]["concepts"]) >= 3, f"real: environment too small (dropped={dropped})"
    mv = meaning_vec(enc, "hydroelectric")
    assert mv is not None and mv.shape == (PRETRAIN_DIM,), "real: meaning_vec shape"
    degen = near_degenerate_precheck(env)
    assert "energy" in degen, "real: pre-check ran"
    train_all, held, coarse_pairs, train_fine = make_pairs(env, HELDOUT_FRAC, SEED)
    assert len(train_fine) >= 3, "real: too few fine train pairs"
    X, Y = _pair_matrix(env, train_all)
    hub = Hub(PRETRAIN_DIM + NREL, H_BOTTLENECK, PRETRAIN_DIM, seed=SEED + 11)
    fa_frozen, _, _ = fine_discrimination(env, train_fine, hub=None)
    hub.train_epochs(X, Y, 2, LR, WEIGHT_DECAY)
    fa_learn2, _, _ = fine_discrimination(env, train_fine, hub=hub)
    # determinism: identical re-train reproduces
    hub2 = Hub(PRETRAIN_DIM + NREL, H_BOTTLENECK, PRETRAIN_DIM, seed=SEED + 11)
    hub2.train_epochs(X, Y, 2, LR, WEIGHT_DECAY)
    assert np.allclose(hub.W1, hub2.W1) and np.allclose(hub.W2, hub2.W2), "real: training non-deterministic"
    # arms differ: learned prediction != frozen concept vector
    lp = learned_predict(hub, env[0]["cvec"][env[0]["concepts"][0]], "source")
    assert not np.allclose(lp, env[0]["cvec"][env[0]["concepts"][0]]), "real: learned arm == frozen arm"
    print(f"[self-test]   real energy: frozen_fine={fa_frozen} degen={degen} dropped={dropped}", flush=True)
    print("[self-test] PASS (planted mechanism fires; real encoder+hub path; determinism; arms differ)",
          flush=True)
    return True


# ---------------------------------------------------------------------------
# full / smoke run
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        return {"n_dim": 512, "schedule": EXPOSURE_SCHED_SMOKE,
                "domains": {k: DOMAINS[k] for k in ("energy", "metal")}}
    return {"n_dim": 512, "schedule": EXPOSURE_SCHED_FULL, "domains": DOMAINS}


def _verdict(learn_iv, frozen_iv, shuf_iv, learn_ho, frozen_ho, shuf_ho,
             coarse_first_domains, n_domains, invalid_reason):
    """Compose the pre-registered composite verdict.
      IN-VOCAB (iv): trained (concept,relation) pairs -> demonstrates the flexible/IMPROVING learning
        curve + that the hub learned the TRUE mapping (shuffled-trained/true-eval control near chance).
      HELD-OUT (ho): compositional same-item/new-relation pairs -> the genuine GENERALIZATION edge; gates
        HARD_PASS vs MIDDLE (memorization-leaning if held-out does not generalize).
    NOTE (honesty): in-vocab fine discrimination is memorization-INCLUSIVE (a learnable front-end can fit
    distinct inputs); it is informative as "a LEARNABLE front-end acquires the TRUE fine distinction the
    FROZEN encoder lacks, improving with exposure" but is NOT sufficient alone for HARD_PASS -- held-out
    generalization must ALSO clear REL_LIFT_HF."""
    iv_lift = round(learn_iv[-1] - frozen_iv, 4)
    iv_sep = round(learn_iv[-1] - shuf_iv[-1], 4)          # learned(true) - shuffled(wrong)-eval-true
    ho_lift = round((learn_ho[-1] - frozen_ho), 4) if (learn_ho and frozen_ho is not None) else None
    ho_sep = round((learn_ho[-1] - shuf_ho[-1]), 4) if (learn_ho and shuf_ho) else None
    controls_hold = iv_sep >= SHUFFLE_SEP
    real_rises = (learn_iv[-1] - learn_iv[0]) > 0.02
    coarse_ok = coarse_first_domains >= min(COARSE_FIRST_MIN_DOMAINS, n_domains)
    ho_generalizes = (ho_lift is not None and ho_lift >= REL_LIFT_HF)
    extra = {"iv_lift": iv_lift, "iv_sep": iv_sep, "ho_lift": ho_lift, "ho_sep": ho_sep,
             "controls_hold": bool(controls_hold), "coarse_before_fine_ok": bool(coarse_ok)}

    if invalid_reason:
        return "INVALID", invalid_reason, extra
    if not real_rises and learn_iv[-1] <= frozen_iv + 0.02:
        return "INVALID", "learned in-vocab curve does not rise above frozen (pipeline/degenerate-seed) -- debug before conclusion", extra
    if not controls_hold and shuf_iv[-1] >= learn_iv[-1] - 0.02:
        return "INVALID", f"shuffled-trained/true-eval control matched the learned arm in-vocab (iv_sep={iv_sep}) -- leak/artifact", extra
    if iv_lift >= REL_LIFT_HP and controls_hold and coarse_ok and ho_generalizes:
        return "HARD_PASS", (f"in-vocab fine lift={iv_lift}>={REL_LIFT_HP} over frozen; true-vs-shuffled sep={iv_sep}; "
                             f"coarse-before-fine {coarse_first_domains}/{n_domains}; AND held-out GENERALIZES "
                             f"(ho_lift={ho_lift}>={REL_LIFT_HF} over frozen-heldout)"), extra
    if iv_lift >= REL_LIFT_HF and controls_hold:
        return "MIDDLE", (f"in-vocab learning real+improving (fine lift={iv_lift}, sep={iv_sep}; coarse-first "
                          f"{coarse_first_domains}/{n_domains}) BUT held-out does not generalize "
                          f"(ho_lift={ho_lift} < {REL_LIFT_HF}) -> memorization-leaning; genuine compositional "
                          f"differentiation belongs to the SEPARATE native-bind component"), extra
    return "HARD_FAIL", (f"in-vocab fine lift={iv_lift} < {REL_LIFT_HF}: even a learnable front-end does not "
                         f"out-differentiate frozen -> near-degenerate seed OR mechanism fail -> pivot to "
                         f"grounded/richer-INPUT front-end (Barsalou/Lambon-Ralph)"), extra


def run(mode, output_dir):
    cfg = _config(mode)
    _heartbeat(output_dir, "load_glove")
    kv = _load_glove()
    _load_wordnet()
    enc = SemanticHDEncoder(n_dim=cfg["n_dim"], seed=SEED, use_wordnet=True, kv=kv)

    _heartbeat(output_dir, "build_environment")
    env, dropped = build_environment(enc, cfg["domains"])
    n_domains = len(env)
    degen = near_degenerate_precheck(env)
    print(f"[env] domains={[d['domain'] for d in env]} sizes={[len(d['concepts']) for d in env]} "
          f"dropped={dropped}", flush=True)
    print(f"[precheck] near-degenerate mean-pairwise-fused-cosine per domain: {degen}", flush=True)

    train_all, held, coarse_pairs, train_fine = make_pairs(env, HELDOUT_FRAC, SEED)
    print(f"[pairs] train_all={len(train_all)} (coarse={len(coarse_pairs)} fine={len(train_fine)}) "
          f"heldout_compositional={len(held)}", flush=True)

    if not held:
        # cannot run the compositional gate without a held-out split
        m = {"verdict": "INVALID", "verdict_msg": "no held-out compositional pairs could be formed "
             "(environment too small) -- cannot gate generalization", "summary": "INVALID: no heldout",
             "run_mode": mode, "elapsed_s": round(time.perf_counter() - _T0[0], 2),
             "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
             "dropped_oov": dropped}
        _write_metrics_atomic(output_dir, m)
        print("[verdict] INVALID: no heldout", flush=True)
        return m

    # ---- FROZEN baseline (no learning; same eval question, no hub) ----
    _heartbeat(output_dir, "frozen_baseline")
    frozen_fine, frozen_fine_pd, _ = fine_discrimination(env, train_fine, hub=None)
    frozen_coarse, _, _ = coarse_discrimination(env, hub=None)
    frozen_fine_held, _, _ = fine_discrimination(env, held, hub=None)
    chance_fine = round(float(np.mean([1.0 / len(d["concepts"]) for d in env])), 4)
    print(f"[frozen] fine_invocab={frozen_fine} (chance~{chance_fine}) coarse={frozen_coarse} "
          f"fine_heldout={frozen_fine_held}", flush=True)

    eval_sets = {"invocab": train_fine, "heldout": held}

    # ---- LEARNED arm exposure curve (train real targets; eval real) ----
    _heartbeat(output_dir, "learned_curve")
    learned = exposure_curve(env, env, train_all, eval_sets, cfg["schedule"], SEED, "learned", output_dir)
    L_iv = learned["sets"]["invocab"]["fine"]
    L_ho = learned["sets"]["heldout"]["fine"]

    # ---- SHUFFLED must-fail control: TRAIN on permuted targets, EVAL on TRUE env ----
    _heartbeat(output_dir, "shuffled_curve")
    senv = shuffle_targets(env, SEED)
    shuf = exposure_curve(senv, env, train_all, eval_sets, cfg["schedule"], SEED, "shuffled", output_dir)
    S_iv = shuf["sets"]["invocab"]["fine"]
    S_ho = shuf["sets"]["heldout"]["fine"]

    # ---- coarse-before-fine ordering (note pred #1) on IN-VOCAB learning dynamics ----
    exposures = list(cfg["schedule"])
    coarse_first = 0
    ordering = {}
    pdf_iv = learned["sets"]["invocab"]["per_dom_fine"]
    pdc = learned["per_dom_coarse"]
    for d in env:
        c_curve = [pdc[t].get(d["domain"]) for t in range(len(exposures))]
        f_curve = [pdf_iv[t].get(d["domain"]) for t in range(len(exposures))]
        xc = _crossing_exposure(exposures, c_curve, ASYMPTOTE_FRAC)
        xf = _crossing_exposure(exposures, f_curve, ASYMPTOTE_FRAC)
        is_first = (xc is not None and xf is not None and xc < xf)
        if is_first:
            coarse_first += 1
        ordering[d["domain"]] = {"coarse_cross": xc, "fine_cross": xf, "coarse_before_fine": bool(is_first)}

    # ---- sigmoidal-shape diagnostic (note pred #2) on the in-vocab fine curve ----
    shape = _sigmoid_vs_linear_aic(exposures, L_iv)

    # ---- glass-box: bottleneck separation (frozen vs learned) ----
    glass = {}
    for d in env[:2]:
        cs = d["concepts"]
        Vf = np.stack([d["cvec"][c] for c in cs], axis=0)
        iu = np.triu_indices(len(cs), k=1)
        frozen_dist = round(float(1.0 - np.mean((Vf @ Vf.T)[iu])), 4)
        Bl = np.stack([_l2(learned["hub"].bottleneck(
            np.concatenate([d["cvec"][c], _rel_onehot("source")]).astype(np.float32)[None, :])[0])
            for c in cs], axis=0)
        learned_dist = round(float(1.0 - np.mean((Bl @ Bl.T)[iu])), 4)
        glass[d["domain"]] = {"frozen_mean_pairwise_dist": frozen_dist,
                              "learned_bottleneck_mean_pairwise_dist": learned_dist, "concepts": cs}

    # ---- INVALID guards ----
    invalid_reason = None
    if frozen_fine is not None and frozen_fine >= FROZEN_SAT:
        invalid_reason = (f"frozen in-vocab fine acc={frozen_fine} >= {FROZEN_SAT}: task too easy "
                          f"(frozen GloVe already discriminates) -- harden the contrast sets")
    max_degen = max([v for v in degen.values() if v is not None], default=0.0)

    arms_differ = not (abs(L_iv[-1] - frozen_fine) < 1e-9 and abs(L_iv[-1] - S_iv[-1]) < 1e-9)

    verdict, vmsg, gx = _verdict(L_iv, frozen_fine, S_iv, L_ho, frozen_fine_held, S_ho,
                                 coarse_first, n_domains, invalid_reason)

    metrics = {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: {vmsg}",
        "run_mode": mode,
        "elapsed_s": round(time.perf_counter() - _T0[0], 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "seed": SEED,
        "one_variable": "LEARNED item+relation->property hub vs FROZEN GloVe (eval question + property targets identical)",
        "primary_metric": "in-vocab fine-tier discrimination learning curve (flexible/improving); HARD_PASS also requires held-out generalization",
        "n_domains": n_domains,
        "domains": [d["domain"] for d in env],
        "dropped_oov": dropped,
        "chance_fine": chance_fine,
        "exposures": exposures,
        # PRIMARY learning curves
        "learned_fine_invocab_curve": L_iv,
        "learned_fine_heldout_curve": L_ho,
        "learned_coarse_curve": learned["coarse"],
        "frozen_fine_invocab": frozen_fine,
        "frozen_fine_heldout": frozen_fine_held,
        "frozen_coarse": frozen_coarse,
        "frozen_fine_per_domain": frozen_fine_pd,
        # must-fail control (shuffled-trained, TRUE-eval)
        "shuffled_fine_invocab_curve": S_iv,
        "shuffled_fine_heldout_curve": S_ho,
        # pre-reg gate quantities
        "in_vocab_fine_lift_over_frozen": gx["iv_lift"],
        "in_vocab_true_vs_shuffled_sep": gx["iv_sep"],
        "heldout_fine_lift_over_frozen": gx["ho_lift"],
        "heldout_true_vs_shuffled_sep": gx["ho_sep"],
        "controls_hold": gx["controls_hold"],
        "heldout_n": len(held),
        "coarse_before_fine_domains": coarse_first,
        "coarse_before_fine_ordering": ordering,
        # difficulty-on / diagnostics
        "near_degenerate_cosine_per_domain": degen,
        "max_near_degenerate_cosine": round(float(max_degen), 4),
        "sigmoid_vs_linear_aic": shape,
        "glassbox_bottleneck_separation": glass,
        # bands
        "bands": {"REL_LIFT_HP": REL_LIFT_HP, "REL_LIFT_HF": REL_LIFT_HF, "SHUFFLE_SEP": SHUFFLE_SEP,
                  "SHUFFLE_FLAT": SHUFFLE_FLAT, "FROZEN_SAT": FROZEN_SAT, "DEGEN_COS": DEGEN_COS,
                  "COARSE_FIRST_MIN_DOMAINS": COARSE_FIRST_MIN_DOMAINS},
        "hub_config": {"H_BOTTLENECK": H_BOTTLENECK, "LR": LR, "WEIGHT_DECAY": WEIGHT_DECAY,
                       "GRAD_CLIP": GRAD_CLIP, "in_dim": PRETRAIN_DIM + NREL, "out_dim": PRETRAIN_DIM},
        "arms_differ_verified": bool(arms_differ),
        "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": "fixed_int_seeds_numpy_default_rng_sorted_no_builtin_hash",
        "storage": "no_composition_selfcontained_differentiation",
        "contract": "INLINE-LOCAL foreground-to-completion; no push/remote-persist; VET-PENDING",
    }
    _write_metrics_atomic(output_dir, metrics)
    print(f"[verdict] {verdict}: {vmsg}", flush=True)
    print(f"[curves] frozen_iv={frozen_fine} learned_iv={L_iv} shuffled_iv={S_iv}", flush=True)
    print(f"[curves] frozen_ho={frozen_fine_held} learned_ho={L_ho} shuffled_ho={S_ho}", flush=True)
    print(f"[curves] learned_coarse={learned['coarse']}", flush=True)
    print(f"[ordering] coarse_before_fine {coarse_first}/{n_domains} {ordering}", flush=True)
    print(f"[gates] {gx}", flush=True)
    return metrics


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    _T0[0] = time.perf_counter()
    output_dir = _out_dir()

    if args.self_test:
        _write_start_marker(output_dir, "self_test")
        ok = self_test()
        sys.exit(0 if ok else 1)

    mode = "smoke" if args.smoke else "full"
    _write_start_marker(output_dir, mode)
    run(mode, output_dir)
    sys.exit(0)


if __name__ == "__main__":
    _out_dir_top = _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_out_dir_top, e)
        raise
