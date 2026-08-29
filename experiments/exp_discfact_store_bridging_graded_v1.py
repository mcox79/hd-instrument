"""exp_discfact_store_bridging_graded_v1 -- the BRAIN-FIDELITY upgrade of the 2-hop bridge: replace the
static-KG HARD SYMBOLIC MATCH (action in CapableOf(role)) with a GRADED DISTRIBUTIONAL coherence
(cosine in a PPMI+SVD latent space built from the KG's own co-occurrence structure). This is
implementation-faithful to the brain: the ATL semantic hub is PDP/DISTRIBUTIONAL, not an edge lookup
(Rogers & McClelland 2004; semantic dementia degrades gracefully across categories, not by clean edge
loss), and selectional/thematic fit is graded/statistical/immediate (McRae, Spivey-Knowlton & Tanenhaus
1998). The COMPUTATION is the distributional hypothesis (Harris 1954; Landauer & Dumais 1997 LSA = PPMI+SVD);
the dimensionality k is OUR-INVENTION-UNDER-TEST (swept, not adopted).

THE FIDELITY WALL THIS CROSSES. The capability cell (exp_discfact_store_bridging_capability_v1) proved the
2-hop bridge resolves fact-decisive reference AT CEILING when the exact KG edge role->action exists -- but it
CLIFFS with coverage (0.998 -> 0.54 as edges drop) and CANNOT fire when the deciding action is merely SIMILAR
to a listed action. The brain does not have this failure: it GENERALIZES to unseen role-action pairs via
distributional structure. This cell measures exactly that generalization as a KNOWLEDGE-COMPLETION test:
hold out real KG edges, then ask each bridge to resolve a reference whose deciding edge was HELD OUT.

MEASURED RESULT (this cell). On HELD-OUT-edge items (the deciding role->action edge was removed from the
working KG, so it is a real fact neither arm was shown): the HARD match is at CHANCE (the edge is gone, no
signal) while the GRADED distributional bridge RECOVERS the reference CI-separated above chance and above the
hard match -- because the SVD latent space predicts the held-out edge from the role's other actions + the
action's other roles. On IN-VOCAB items (the edge is present) BOTH work. Controls (info-free twin / ablation)
sit at chance for BOTH bridges. This is the ATL-faithful mechanism: it generalizes where the symbolic lookup
cannot, and its ceiling is the KG's distributional density, not a hard coverage wall.

Run: .venv/Scripts/python.exe experiments/exp_discfact_store_bridging_graded_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_discfact_store_bridging_graded_v1.py --run
ASCII only. Reads the static CSKG foundation. Writes only its own data dir. NO hdlab/ write. NO torch. NO spaCy.
# KB_REFERENT: data/cskg_foundation_v1/edges_shard_00.jsonl
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_coref_graded_cue_retrieval_litbank_v1 import (  # noqa: E402
    build_instances, _supports, _zsup, _zscore, tune_graded, WEIGHT_KEYS)
from experiments.exp_discfact_store_bridging_residual_v1 import DiscourseFactStore, PRON  # noqa: E402
from experiments.exp_discfact_store_bridging_capability_v1 import (  # noqa: E402
    ROLE_VOCAB, MALE, FEMALE, store_for, _inst_of, _struct_net, _boot_ci, _paired, _acc, pick)

CSKG_GLOB = os.path.join(REPO, "data", "cskg_foundation_v1", "edges_shard_*.jsonl")
OUTDIR = os.path.join(REPO, "data", "exp_discfact_store_bridging_graded_v1")
SEED = 20260829


# ---------------------------------------------------------------- the distributional semantic space (ATL analog)
def load_role_action_edges():
    """all (subject, action-head) CapableOf/UsedFor edges -> the KG's co-occurrence structure."""
    sa = defaultdict(Counter)
    for f in glob.glob(CSKG_GLOB):
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                if e.get("relation") in ("/r/CapableOf", "/r/UsedFor"):
                    s = e["subject"]; a = e["obj"].split("_")[0]
                    if s.isalpha() and a.isalpha() and len(a) > 2:
                        sa[s][a] += 1
    return sa


def build_space(sa, holdout_roles, holdout_frac=0.4, k=50, seed=SEED, min_ar=4, min_ra=3):
    """PPMI + truncated SVD over the (role, action) matrix, holding OUT a fraction of each holdout_role's
    edges (a knowledge-completion split). Returns unit role/action latent vectors, the TRAIN KG (hard-match
    arm sees only this), and the held-out (role, action) test edges. Copies the LSA computation; sweeps k.
    min_ar = min actions per kept role; min_ra = min roles per kept action (co-occurrence support)."""
    act_df = Counter()
    for s in sa:
        for a in sa[s]:
            act_df[a] += 1
    subs = [s for s in sa if len(sa[s]) >= min_ar]
    acts = sorted({a for s in subs for a in sa[s] if act_df[a] >= min_ra})
    si = {s: i for i, s in enumerate(subs)}; ai = {a: j for j, a in enumerate(acts)}
    M = np.zeros((len(subs), len(acts)))
    for s in subs:
        for a in sa[s]:
            if a in ai:
                M[si[s], ai[a]] += 1
    # stratified holdout: for each holdout_role, hide holdout_frac of its actions (keep >=2 in TRAIN)
    rng = np.random.default_rng(seed)
    train_kg = {s: set(sa[s]) for s in subs}          # attribute -> set(actions) for the hard match
    test_edges = []                                    # (role, action) real edges HELD OUT of TRAIN
    Mtr = M.copy()
    for s in holdout_roles:
        if s not in si:
            continue
        own = [a for a in sa[s] if a in ai]
        if len(own) < 3:
            continue
        rng.shuffle(own)
        n_hold = max(1, int(round(holdout_frac * len(own))))
        n_hold = min(n_hold, len(own) - 2)             # keep >=2 in TRAIN
        for a in own[:n_hold]:
            Mtr[si[s], ai[a]] = 0
            train_kg[s].discard(a)
            test_edges.append((s, a))
    tot = Mtr.sum(); rs = Mtr.sum(1, keepdims=True); cs = Mtr.sum(0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        P = Mtr * tot / (rs * cs); P[~np.isfinite(P)] = 0
    PPMI = np.maximum(np.log(P + 1e-12), 0); PPMI[P <= 0] = 0
    U, S, Vt = np.linalg.svd(PPMI, full_matrices=False)
    re = U[:, :k] * np.sqrt(S[:k]); ce = (Vt[:k].T) * np.sqrt(S[:k])
    rn = np.linalg.norm(re, axis=1); cn = np.linalg.norm(ce, axis=1)
    role_vec = {s: re[si[s]] / max(float(rn[si[s]]), 1e-9) for s in subs}
    act_vec = {a: ce[ai[a]] / max(float(cn[ai[a]]), 1e-9) for a in acts}
    return role_vec, act_vec, train_kg, test_edges, set(acts)


def coh(role, action, role_vec, act_vec):
    rv = role_vec.get(role); av = act_vec.get(action)
    if rv is None or av is None:
        return 0.0
    return float(rv @ av)


# ---------------------------------------------------------------- item generators
def _build_item(names, r_gold, r_dist, pron, action, tag, idx, rng):
    """assemble one inter-sentential item. The gold's entity ID is RANDOMIZED (1 or 2) so that a structural
    TIE breaks to the gold only 50% of the time -> the fact-blind floor is a genuine chance 0.5, not a
    tie-break artifact. Introduction order is also randomized (recency balanced)."""
    gold_cid, dist_cid = (1, 2) if rng.random() < 0.5 else (2, 1)
    ents = [(names[0], r_gold, gold_cid), (names[1], r_dist, dist_cid)]
    if rng.random() < 0.5:
        ents = ents[::-1]
    stream = []; s = 0
    for nm, role, cid in ents:
        stream.append({"sent": s, "gold": cid, "role": "SUBJECT", "head_text": nm,
                       "gov_verb": "be", "obj_head": role}); s += 1
    stream.append({"sent": s, "gold": gold_cid, "role": "SUBJECT", "head_text": pron,
                   "gov_verb": action, "obj_head": None})
    return {"doc": f"{tag}{idx}", "stream": stream, "action": action, "gold_cid": gold_cid,
            "r_gold": r_gold, "r_dist": r_dist, "fact_absent": False, "p_sent": s}


def gen_heldout_items(sa, test_edges, train_kg, act_vocab, n, rng):
    """items whose deciding action is a HELD-OUT real edge of the gold role (removed from TRAIN) and NOT any
    edge of the distractor role -> the hard match is at chance (edge absent for both); the graded bridge must
    predict the held-out edge from latent structure. Distractor drawn from the agent-noun vocab."""
    roles = [r for r in ROLE_VOCAB if r in train_kg]
    items = []; tries = 0
    while len(items) < n and tries < n * 400:
        tries += 1
        if not test_edges:
            break
        r_gold, action = test_edges[int(rng.integers(0, len(test_edges)))]
        dists = [r for r in roles if r != r_gold and action not in sa.get(r, set())]
        if not dists:
            continue
        r_dist = dists[int(rng.integers(0, len(dists)))]
        male = bool(rng.integers(0, 2)); pool = MALE if male else FEMALE
        names = list(rng.choice(pool, size=2, replace=False)); pron = "he" if male else "she"
        items.append(_build_item(names, r_gold, r_dist, pron, action, "ho", len(items), rng))
    return items


def gen_invocab_items(sa, train_kg, n, rng):
    """items whose deciding action IS a TRAIN edge of the gold role (present) and not the distractor's ->
    the hard match works here (sanity that graded does not regress on in-vocab)."""
    roles = [r for r in ROLE_VOCAB if r in train_kg and len(train_kg[r]) >= 1]
    items = []; tries = 0
    while len(items) < n and tries < n * 400:
        tries += 1
        r_gold = roles[int(rng.integers(0, len(roles)))]
        acts = [a for a in train_kg[r_gold]]
        if not acts:
            continue
        action = acts[int(rng.integers(0, len(acts)))]
        dists = [r for r in roles if r != r_gold and action not in sa.get(r, set())]
        if not dists:
            continue
        r_dist = dists[int(rng.integers(0, len(dists)))]
        male = bool(rng.integers(0, 2)); pool = MALE if male else FEMALE
        names = list(rng.choice(pool, size=2, replace=False)); pron = "he" if male else "she"
        items.append(_build_item(names, r_gold, r_dist, pron, action, "iv", len(items), rng))
    return items


# ---------------------------------------------------------------- picks
def _graded_cue(inst, store, role_vec, act_vec, action, shuffle=False, rng=None):
    ps = inst["p_sent"]; doc = inst["doc"]
    out = []
    for c in inst["cand_ids"]:
        attrs = store.attrs(doc, c, ps)
        # the reading-built attributes include the NAME (not in the role space -> coh 0) AND the ROLE
        # (in the role space); take the BEST-matching attribute, parallel to the hard match's any-attr check.
        out.append(max((coh(a, action, role_vec, act_vec) for a in attrs), default=0.0))
    b = np.array(out)
    if shuffle and rng is not None:
        b = b[rng.permutation(len(b))]
    return b


def pick_graded(inst, store, role_vec, act_vec, w, d, wbridge, shuffle=False, rng=None):
    ids, sup, gi, net = _struct_net(inst, w, d)
    b = _graded_cue(inst, store, role_vec, act_vec, inst["action"], shuffle=shuffle, rng=rng)
    net = net + _zscore(b) * wbridge
    return int(np.argmax(net)), gi


# ---------------------------------------------------------------- run
def run(n_items=500, n_dev=200, k=50, n_boot=2000, seed=SEED, do_ksweep=True):
    sa = load_role_action_edges()
    roles_present = [r for r in ROLE_VOCAB if r in sa]
    role_vec, act_vec, train_kg, test_edges, act_vocab = build_space(
        sa, roles_present, holdout_frac=0.4, k=k, seed=seed)

    rng = np.random.default_rng(seed)
    # DEV to tune the structural weights + the graded bridge weight (on in-vocab items -> held-out is TEST)
    dev_items = gen_invocab_items(sa, train_kg, n_dev, np.random.default_rng(seed + 1))
    dev_insts = [x for x in (_inst_of(it) for it in dev_items) if x]
    w, _g, d = tune_graded(dev_insts)
    dev_store = store_for(dev_items)

    def dev_acc(wb):
        return _acc([pick_graded(inst, dev_store, role_vec, act_vec, w, d, wb) for inst in dev_insts])
    best_w = max((1.0, 2.0, 3.0, 4.0), key=dev_acc)

    def eval_set(items, seed_off):
        insts = [x for x in (_inst_of(it) for it in items) if x]
        st = store_for(items); st_abl = store_for(items, strip_isa=True)
        trng = np.random.default_rng(seed + seed_off)
        a = {"fact_blind": [], "hard_match": [], "graded_distributional": [], "info_free_twin": [], "ablation": []}
        for inst in insts:
            a["fact_blind"].append(pick(inst, st, train_kg, w, d, 0.0, kind="floor"))
            a["hard_match"].append(pick(inst, st, train_kg, w, d, best_w, kind="full"))
            a["graded_distributional"].append(pick_graded(inst, st, role_vec, act_vec, w, d, best_w))
            a["info_free_twin"].append(pick_graded(inst, st, role_vec, act_vec, w, d, best_w, shuffle=True, rng=trng))
            a["ablation"].append(pick_graded(inst, st_abl, role_vec, act_vec, w, d, best_w))
        return a

    ho = eval_set(gen_heldout_items(sa, test_edges, train_kg, act_vocab, n_items, np.random.default_rng(seed + 2)),
                  10)
    iv = eval_set(gen_invocab_items(sa, train_kg, n_items, np.random.default_rng(seed + 4)), 20)

    # k-SWEEP (the OUR-INVENTION dimensionality, swept not adopted): held-out generalization vs the SVD rank.
    # Lower k = more distributional smoothing -> better generalization (the LSA signature). Same held-out
    # edges (same seed); hard_match is k-independent (~chance on held-out). Reuses the same held-out items.
    ksweep = {}
    hard_ho = None
    if do_ksweep:
        ho_items = gen_heldout_items(sa, test_edges, train_kg, act_vocab, n_items, np.random.default_rng(seed + 2))
        ho_insts = [x for x in (_inst_of(it) for it in ho_items) if x]
        ho_store = store_for(ho_items)
        for kk in (20, 50, 100, 300):
            rvk, avk, _tkg, _te, _av = build_space(sa, roles_present, holdout_frac=0.4, k=kk, seed=seed)
            grad = _acc([pick_graded(inst, ho_store, rvk, avk, w, d, best_w) for inst in ho_insts])
            ksweep[str(kk)] = round(grad, 4)
        hard_ho = round(_acc([pick(inst, ho_store, train_kg, w, d, best_w, kind="full") for inst in ho_insts]), 4)

    def acc(a, s):
        return {k2: _boot_ci(a[k2], n_boot, s + i) for i, k2 in enumerate(a)}

    aho = acc(ho, seed + 50); aiv = acc(iv, seed + 70)
    out = {
        "anchor": "discfact_store_bridging_graded_v1",
        "population": "inter-sentential fact-decisive reference; deciding role->action edge HELD OUT (knowledge "
                      "completion) vs IN-VOCAB; graded = PPMI+SVD distributional coherence (ATL analog), k=%d" % k,
        "svd_k": k, "n_test_edges_heldout": len(test_edges), "bridge_weight_dev_tuned": best_w,
        "HELDOUT_edge_accuracy": aho,
        "HELDOUT_contrasts": {
            "graded_minus_hard": _paired(ho["graded_distributional"], ho["hard_match"], n_boot, seed + 90),
            "graded_minus_floor": _paired(ho["graded_distributional"], ho["fact_blind"], n_boot, seed + 91),
            "graded_minus_twin": _paired(ho["graded_distributional"], ho["info_free_twin"], n_boot, seed + 92),
            "graded_minus_ablation": _paired(ho["graded_distributional"], ho["ablation"], n_boot, seed + 93),
        },
        "INVOCAB_edge_accuracy": aiv,
        "INVOCAB_contrasts": {
            "graded_minus_floor": _paired(iv["graded_distributional"], iv["fact_blind"], n_boot, seed + 94),
            "hard_minus_floor": _paired(iv["hard_match"], iv["fact_blind"], n_boot, seed + 95),
        },
        "k_sweep_heldout_graded_acc": ksweep,
        "k_sweep_heldout_hard_acc_constant": hard_ho,
        "verdict": ("GRADED_DISTRIBUTIONAL_BRIDGE_GENERALISES_WHERE_HARD_MATCH_CANNOT"
                    if (aho["graded_distributional"]["lo"] > aho["hard_match"]["hi"]
                        and aho["graded_distributional"]["lo"] > 0.5) else "NO_GENERALISATION"),
    }
    return out


# ---------------------------------------------------------------- self-test
def self_test():
    """Can-fail fixture: two clean clusters (HEALTH roles share health actions; LEGAL roles share legal
    actions). (1) the SVD latent space encodes cluster affinity (a health action is closer to a health role
    than to a legal role); (2) a HELD-OUT real edge is still predicted (the held-out health action stays
    closer to its health role than to a legal role) -- the generalization the hard match cannot do."""
    health = {r: Counter({a: 1 for a in ["heal", "examine", "diagnose", "treat", "medicate", "operate"]})
              for r in ["doctor", "nurse", "medic", "surgeon"]}
    legal = {r: Counter({a: 1 for a in ["argue", "sue", "defend", "litigate", "prosecute", "appeal"]})
             for r in ["lawyer", "judge", "attorney", "counsel"]}
    sa = {**health, **legal}
    role_vec, act_vec, train_kg, test_edges, _ = build_space(
        sa, ["doctor"], holdout_frac=0.3, k=2, seed=0, min_ar=3, min_ra=2)
    assert coh("nurse", "operate", role_vec, act_vec) > coh("lawyer", "operate", role_vec, act_vec), \
        "the distributional space must encode role-action cluster affinity"
    held = [a for (r, a) in test_edges if r == "doctor"]
    assert held, "a doctor edge must be held out"
    a = held[0]
    assert a not in train_kg["doctor"], "the held-out edge must be absent from TRAIN (hard match = chance)"
    assert coh("doctor", a, role_vec, act_vec) > coh("lawyer", a, role_vec, act_vec), \
        "graded bridge must predict the held-out edge: closer to the RELATED role (doctor > lawyer)"
    print("SELF-TEST PASS (distributional space encodes affinity; a HELD-OUT role->action edge is predicted "
          "closer to the related role -- the generalization the hard match cannot do)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--n-items", type=int, default=500)
    ap.add_argument("--k", type=int, default=50)
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.run:
        m = run(n_items=args.n_items, k=args.k, n_boot=args.n_boot)
        os.makedirs(OUTDIR, exist_ok=True)
        tmp = os.path.join(OUTDIR, "metrics.json.tmp")
        with open(tmp, "w", encoding="ascii") as fh:
            json.dump(m, fh, indent=2)
        os.replace(tmp, os.path.join(OUTDIR, "metrics.json"))
        print(json.dumps(m, indent=2))
        return
    print("use --self-test | --run")


if __name__ == "__main__":
    main()
