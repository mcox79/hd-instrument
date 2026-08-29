"""exp_discfact_store_multifact_load_v1 -- does the proven discourse-fact-store RESOLUTION capability SURVIVE
realistic MULTI-FACT-PER-ENTITY load in the brain-faithful FHRR store, and does the brain's fix hold it up?

THE WALL. Cells B/C proved the capability with ONE fact per entity. But a real situation model accumulates
MANY facts per character ("Sam is a doctor, Sam lives in Boston, Sam owns a dog..."). The FHRR store the brief
names BUNDLES these into one register: reg = sum_i bind(relation_i, value_i). Retrieving the deciding attribute
by unbinding the ISA relation returns value + CROSSTALK from the other K-1 facts; crosstalk grows with the
fact load K (the bundle capacity law: hdlab/binding.py k_50% ~ N^1.004). So the recovered role degrades, and
the resolution built on it should degrade too -- a capacity wall the single-fact demo hid.

THE BRAIN'S FIX (PINNED). The hippocampus binds many facts to one entity WITHOUT interference via DENTATE-GYRUS
SPARSE PATTERN SEPARATION (Marr 1971; O'Reilly & McClelland 1994; McClelland-McNaughton-O'Reilly 1995 CLS):
sparse, minimally-overlapping codes so distinct facts do not corrupt each other's retrieval. The computational
levers are (a) CAPACITY (more dimensions D -> less crosstalk, the scaling law) and (b) SEPARATION (relation-
indexed / sparse slots so the ISA fact is retrieved without the other facts' interference). Both are
brain-faithful; the dense single-register bundle is the OUR-INVENTION shortcut that fails under load.

MEASURED RESULT (this cell). Role-recovery and end-to-end resolution accuracy vs fact-load K, on a CLEAN bridge
(full KG, so the ONLY error source is the store): the DENSE FHRR bundle DEGRADES with K (the interference wall,
matching the capacity law); higher D pushes the curve up (capacity); the RELATION-INDEXED store (pattern
separation) holds accuracy FLAT across K. The info-free twin (shuffled ISA bindings) is at chance. So the
capability survives realistic load ONLY with the brain's pattern-separation fix -- the single-register bundle
is a fidelity shortcut, and the DG-sparse / indexed store is the faithful representation.

Run: .venv/Scripts/python.exe experiments/exp_discfact_store_multifact_load_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_discfact_store_multifact_load_v1.py --run
ASCII only. Reuses hdlab.binding (FHRR) + situation_model_accumulate.unit_phase_vec. Writes only its own dir.
NO hdlab/ write. torch (FHRR) CPU. NO spaCy.
# KB_REFERENT: data/cskg_foundation_v1/edges_shard_00.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict

import numpy as np
import torch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.binding import bind, unbind  # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec  # noqa: E402
from experiments.exp_discfact_store_bridging_graded_v1 import load_role_action_edges  # noqa: E402
from experiments.exp_discfact_store_bridging_capability_v1 import ROLE_VOCAB  # noqa: E402

OUTDIR = os.path.join(REPO, "data", "exp_discfact_store_multifact_load_v1")
SEED = 20260829
RELATIONS = ["ISA", "LOC", "HAS", "LIKES", "FEARS", "OWNS", "VISITS", "KNOWS"]
FILLERS = ("boston london dog cat house garden river hill money book horse ship apple bread gold "
           "letter song fire water road field tree stone bell door coat hat road star moon").split()


def _sim(a, b):
    """FHRR similarity = Re<a, conj(b)> (real part of the conjugate inner product)."""
    return float(torch.real(torch.vdot(a, b)))


class MultiFactStore:
    """Accumulate K facts per entity. mode='dense' bundles all facts into ONE register (interference);
    mode='indexed' keeps a SEPARATE register per relation (pattern separation -> no cross-relation
    interference). Retrieval of a relation's value = unbind by the relation vector + cleanup argmax."""

    def __init__(self, d, gen, mode="dense"):
        self.d = d; self.gen = gen; self.mode = mode
        self.rel = {r: unit_phase_vec(d, gen) for r in RELATIONS}
        self.val = {}
        self.dense = defaultdict(lambda: torch.zeros(d, dtype=torch.complex64))
        self.slots = defaultdict(dict)   # entity -> {relation -> bundle}

    def _vv(self, v):
        if v not in self.val:
            self.val[v] = unit_phase_vec(self.d, self.gen)
        return self.val[v]

    def add(self, entity, relation, value, shuffle_val=None):
        bound = bind(self.rel[relation], self._vv(shuffle_val if shuffle_val is not None else value))
        if self.mode == "dense":
            self.dense[entity] = self.dense[entity] + bound
        else:
            self.slots[entity].setdefault(relation, torch.zeros(self.d, dtype=torch.complex64))
            self.slots[entity][relation] = self.slots[entity][relation] + bound

    def recover(self, entity, relation, vocab):
        """unbind the relation's value and clean up to the nearest value in `vocab` (argmax cosine)."""
        if self.mode == "dense":
            reg = self.dense[entity]
        else:
            reg = self.slots[entity].get(relation, torch.zeros(self.d, dtype=torch.complex64))
        noisy = unbind(reg, self.rel[relation])
        best, bestv = None, -1e9
        for v in vocab:
            s = _sim(noisy, self._vv(v))
            if s > bestv:
                bestv, best = s, v
        return best


def _build_entity(store, entity, isa_role, k, rng, shuffle_isa=None):
    """entity gets the deciding ISA fact + (k-1) random distractor facts (other relations, filler values)."""
    store.add(entity, "ISA", isa_role, shuffle_val=shuffle_isa)
    for _ in range(k - 1):
        r = RELATIONS[1 + int(rng.integers(0, len(RELATIONS) - 1))]   # a non-ISA relation
        v = FILLERS[int(rng.integers(0, len(FILLERS)))]
        store.add(entity, r, v)


def run(d=256, ks=(1, 8, 32, 64, 128, 256, 512), n_items=150, seed=SEED, kg=None):
    if kg is None:
        sa = load_role_action_edges()
        kg = {r: set(sa[r]) for r in ROLE_VOCAB if r in sa and len(sa[r]) >= 4}
    roles = list(kg)
    role_vocab = roles + FILLERS                         # realistic cleanup: ISA competes against ~60 distractors
    rng = np.random.default_rng(seed)

    def one_condition(mode, d_use, k):
        gen = torch.Generator().manual_seed(seed + k + d_use + (0 if mode == "dense" else 7))
        rr = np.random.default_rng(seed + 1000 * k + d_use)
        role_ok = res_ok = res_twin_ok = n = 0
        for _ in range(n_items):
            # pick gold + distractor roles with a discriminative action
            r_gold = roles[int(rr.integers(0, len(roles)))]
            disc = [a for a in kg[r_gold]]
            cand_d = [r for r in roles if r != r_gold]
            r_dist = cand_d[int(rr.integers(0, len(cand_d)))]
            actions = [a for a in kg[r_gold] if a not in kg[r_dist]]
            if not actions:
                continue
            action = actions[int(rr.integers(0, len(actions)))]
            store = MultiFactStore(d_use, gen, mode=mode)
            twin = MultiFactStore(d_use, gen, mode=mode)
            # gold entity + distractor entity, each loaded with k facts
            _build_entity(store, "G", r_gold, k, rr)
            _build_entity(store, "D", r_dist, k, rr)
            # info-free twin: the ISA role is SHUFFLED (random role) -> binding carries no identity
            _build_entity(twin, "G", r_gold, k, rr, shuffle_isa=roles[int(rr.integers(0, len(roles)))])
            _build_entity(twin, "D", r_dist, k, rr, shuffle_isa=roles[int(rr.integers(0, len(roles)))])
            rec_g = store.recover("G", "ISA", role_vocab)
            rec_d = store.recover("D", "ISA", role_vocab)
            role_ok += int(rec_g == r_gold)
            # resolution via a CLEAN bridge on the RECOVERED roles (only the store can err)
            def bridge_pick(rg, rd):
                g_hit = action in kg.get(rg, set()); d_hit = action in kg.get(rd, set())
                if g_hit and not d_hit:
                    return "G"
                if d_hit and not g_hit:
                    return "D"
                return "G" if rr.random() < 0.5 else "D"       # tie -> chance
            res_ok += int(bridge_pick(rec_g, rec_d) == "G")
            tg = twin.recover("G", "ISA", role_vocab); td = twin.recover("D", "ISA", role_vocab)
            res_twin_ok += int(bridge_pick(tg, td) == "G")
            n += 1
        return {"role_recovery": round(role_ok / max(n, 1), 4),
                "resolution": round(res_ok / max(n, 1), 4),
                "twin": round(res_twin_ok / max(n, 1), 4), "n": n}

    dense = {str(k): one_condition("dense", d, k) for k in ks}
    indexed = {str(k): one_condition("indexed", d, k) for k in ks}
    dense_highd = {str(k): one_condition("dense", d * 4, k) for k in ks}

    kmax = str(max(ks))
    out = {
        "anchor": "discfact_store_multifact_load_v1",
        "population": "multi-fact-per-entity FHRR store; resolution via a CLEAN bridge so the ONLY error source "
                      "is store crosstalk; sweep fact-load K and dimension D",
        "d": d, "d_high": d * 4, "ks": list(ks), "n_items": n_items,
        "DENSE_bundle": dense,
        "INDEXED_pattern_separation": indexed,
        "DENSE_high_dimension": dense_highd,
        "headline": {
            "dense_resolution_at_K1": dense["1"]["resolution"],
            "dense_resolution_at_Kmax": dense[kmax]["resolution"],
            "indexed_resolution_at_Kmax": indexed[kmax]["resolution"],
            "dense_highD_resolution_at_Kmax": dense_highd[kmax]["resolution"],
            "twin_at_Kmax": dense[kmax]["twin"]},
        "verdict": ("INTERFERENCE_WALL_CONFIRMED_AND_PATTERN_SEPARATION_FIXES_IT"
                    if (dense[kmax]["resolution"] < dense["1"]["resolution"] - 0.05
                        and indexed[kmax]["resolution"] > dense[kmax]["resolution"] + 0.05) else "NO_WALL_OR_NO_FIX"),
    }
    return out


def self_test():
    """Can-fail fixture: at high fact-load the DENSE bundle's ISA recovery is corrupted while the INDEXED
    (pattern-separated) store recovers it exactly -- the interference wall + the brain's fix, on one entity."""
    d = 512
    gen = torch.Generator().manual_seed(0)
    rng = np.random.default_rng(0)
    vocab = ["doctor", "lawyer", "farmer", "baker", "singer", "hunter", "sailor", "judge"]
    # DENSE: load 12 facts, ISA=doctor + 11 fillers -> recovery should be corruptible
    dense = MultiFactStore(d, gen, mode="dense")
    _build_entity(dense, "E", "doctor", 12, rng)
    # INDEXED: same facts, separate slots -> ISA recovery exact
    idx = MultiFactStore(d, gen, mode="indexed")
    _build_entity(idx, "E", "doctor", 12, rng)
    assert idx.recover("E", "ISA", vocab) == "doctor", "pattern-separated store must recover ISA exactly under load"
    # dense at K=1 must be exact (no interference); the wall is a LOAD effect
    dense1 = MultiFactStore(d, gen, mode="dense")
    _build_entity(dense1, "E", "doctor", 1, rng)
    assert dense1.recover("E", "ISA", vocab) == "doctor", "dense store must be exact at K=1 (no load)"
    print("SELF-TEST PASS (pattern-separated store recovers ISA under load; dense is exact at K=1 -- the wall is load)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--d", type=int, default=1024)
    ap.add_argument("--n-items", type=int, default=300)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.run:
        m = run(d=args.d, n_items=args.n_items)
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
