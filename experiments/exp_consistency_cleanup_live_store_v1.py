"""LIVE-STORE validation of the consistency-cleanup mechanism -- the concrete landing form.

The main cell (exp_knowledge_store_consistency_cleanup_v1) proved the mechanism on a PLAINTEXT is-a
graph. This runs the SAME relational schema-congruence energy through a REAL hdlab.HDFactStore
instance: facts are ingested via store.store() (so they pass through the live INGEST-VET), and the
consistency pass operates on store.live_facts() -- the live organ's actual post-ingest data
structures, generalised to the store's (subject, relation, object) schema (per-relation).

This closes the gap between the experiment and the landing: the code in `consistency_energies()`
below is what would move into hd_fact_store (a default-OFF pass), and it is validated to
  (a) run on the live store's FactRecords,
  (b) survive INGEST-VET (injected errors that COMBINE into the store are still detected),
  (c) reproduce the experiment's paired discrimination over the info-free twin.

GLASS-BOX: the pass reads (subject, relation, object) which the store recovers from its HD bundles by
unbind+cleanup (FactRecord shadow fields are proven bit-identical to that recovery). ASCII-only.
Deterministic. numpy-free; no spaCy/torch beyond what hd_fact_store already imports.
"""
from __future__ import annotations

import argparse
import os
import random
import statistics as st
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.hd_fact_store import HDFactStore
import experiments.exp_knowledge_store_consistency_cleanup_v1 as C


# =========================================================================================
# THE LANDING-FORM PASS: relational schema-congruence energy over a LIVE HDFactStore.
# Operates per-relation on (subject, relation, object) recovered from the store. This is the
# exact code shape that would become HDFactStore.consistency_energies() (default-OFF).
# =========================================================================================
def consistency_energies(store: HDFactStore, relation: str, k_min: int = 2
                         ) -> Dict[int, Tuple[str, float]]:
    """Return {fid: (status, energy)} for every live fact under `relation`.
    status in {"SCORED", "INSUFFICIENT_SUPPORT"}; energy in [0,1], HIGH = contradicts the majority.

    Mechanism (member-Jaccard family compatibility over the activated associative network,
    EXCLUDING the fact under test) -- identical to the validated experiment, generalised to the
    store's schema. Glass-box: uses (subject, object) recovered by the store (shadow fields are the
    bit-identical recovery)."""
    live = [f for f in store.live_facts() if f.relation == relation]
    subj2obj: Dict[str, set] = defaultdict(set)
    obj2subj: Dict[str, set] = defaultdict(set)
    for f in live:
        subj2obj[f.subject].add(f.obj)
        obj2subj[f.obj].add(f.subject)

    _compat_cache: Dict[Tuple[str, str], float] = {}

    def compat(o1: str, o2: str) -> float:
        if o1 == o2:
            return 1.0
        key = (o1, o2) if o1 <= o2 else (o2, o1)
        c = _compat_cache.get(key)
        if c is not None:
            return c
        a, b = obj2subj.get(o1, set()), obj2subj.get(o2, set())
        inter = len(a & b)
        c = inter / (len(a) + len(b) - inter) if inter else 0.0
        _compat_cache[key] = c
        return c

    def energy(s: str, o: str) -> Tuple[str, float]:
        other = set(subj2obj.get(s, set())) - {o}
        net: Dict[str, float] = defaultdict(float)
        for oo in other:
            net[oo] += 3.0                                  # s's own independent objects (strong)
        for oo in other:                                    # siblings reached via those objects
            for t in obj2subj.get(oo, ()):
                if t == s:
                    continue
                for to in subj2obj.get(t, ()):
                    if to != o:
                        net[to] += 1.0
        tot = sum(net.values())
        if tot < k_min:
            return "INSUFFICIENT_SUPPORT", float("nan")
        num = sum(w * compat(o, o2) for o2, w in net.items())
        return "SCORED", 1.0 - num / tot

    out: Dict[int, Tuple[str, float]] = {}
    for f in live:
        out[f.fid] = energy(f.subject, f.obj)
    return out


# =========================================================================================
# VALIDATION: build the live store, inject via the store API, score, measure paired vs twin.
# =========================================================================================
def build_live_store(facts: List[C.Fact], n_dim: int = 2048, seed: int = 1) -> HDFactStore:
    # MULTIVALUED so a same-(s,r) conflict COMBINEs (both kept) rather than DROP -- the realistic
    # case where INGEST-VET keeps an error and the consistency pass must then pick the outlier.
    store = HDFactStore(n_dim=n_dim, seed=seed,
                        relation_cardinality={"GROUNDED_MEANING": "MULTIVALUED"}, use_index=True)
    for f in facts:
        store.store(f.subject, "GROUNDED_MEANING", f.obj, "reading:def", "TRUST_MID")
    return store


def run(seed: int = 0, rate: float = 0.15, smoke: bool = False) -> Dict:
    facts = C.load_facts(C.DEFAULT_STORE)
    # rename fields onto the store schema (subject/obj)
    facts = [type("F", (), {"subject": f.s, "obj": f.g})() for f in facts]
    if smoke:
        facts = facts[:400]
    rng = random.Random(seed)

    # eligible = subjects with >=2 distinct objects (independent evidence); inject a FAR wrong object
    subj2obj: Dict[str, set] = defaultdict(set)
    obj2subj: Dict[str, set] = defaultdict(set)
    for f in facts:
        subj2obj[f.subject].add(f.obj)
        obj2subj[f.obj].add(f.subject)
    all_objs = [o for o, m in obj2subj.items() if len(m) >= 3]

    def far_compat_zero(o: str, cand: str) -> bool:
        a, b = obj2subj.get(o, set()), obj2subj.get(cand, set())
        return not (a & b)

    store = build_live_store(facts, seed=seed + 1)
    eligible = [f for f in facts if len(subj2obj[f.subject]) >= 2]
    rng.shuffle(eligible)
    n_inject = max(1, int(round(len(eligible) * rate)))
    injected: List[Tuple[str, str]] = []                 # (subject, wrong_object)
    for f in eligible[:n_inject]:
        cands = [o for o in all_objs if o != f.obj and o not in subj2obj[f.subject]
                 and far_compat_zero(f.obj, o)]
        if not cands:
            continue
        wrong = rng.choice(cands)
        store.store(f.subject, "GROUNDED_MEANING", wrong, "reading:BAD", "TRUST_MID")  # via INGEST-VET
        injected.append((f.subject, wrong))

    # score the post-ingest live store
    en = consistency_energies(store, "GROUNDED_MEANING", k_min=2)
    # map (subject,object) -> fid for the injected pairs and for the originals
    live = [f for f in store.live_facts() if f.relation == "GROUNDED_MEANING"]
    so2fid: Dict[Tuple[str, str], int] = {(f.subject, f.obj): f.fid for f in live}
    orig: Dict[str, List[str]] = defaultdict(list)
    for f in facts:
        orig[f.subject].append(f.obj)

    # coverage + survival: how many injected facts survived ingest and are scorable
    inj_scored = 0
    pair_wins: List[float] = []
    for (s, wrong) in injected:
        fid_w = so2fid.get((s, wrong))
        if fid_w is None or en.get(fid_w, ("", 0))[0] != "SCORED":
            continue
        inj_scored += 1
        ew = en[fid_w][1]
        for oc in orig.get(s, []):
            fid_c = so2fid.get((s, oc))
            if fid_c is not None and en.get(fid_c, ("", 0))[0] == "SCORED":
                pair_wins.append(1.0 if ew > en[fid_c][1] else 0.0)
    paired = sum(pair_wins) / len(pair_wins) if pair_wins else float("nan")
    # bootstrap CI + info-free twin (random sign = 0.5)
    lo, hi = _boot_ci(pair_wins, random.Random(seed + 5))
    scored = sum(1 for v in en.values() if v[0] == "SCORED")

    return {
        "n_live_facts": len(live), "n_injected": len(injected),
        "n_injected_scored": inj_scored,
        "coverage": round(scored / len(live), 4) if live else 0.0,
        "paired_corrupted_gt_original": round(paired, 4),
        "paired_ci_lo": round(lo, 4), "paired_ci_hi": round(hi, 4),
        "paired_n": len(pair_wins), "twin_paired": 0.5,
        "beats_twin_ci": lo > 0.5,
        "seed": seed, "rate": rate,
    }


def _boot_ci(vals: List[float], rng: random.Random, n: int = 2000) -> Tuple[float, float]:
    if not vals:
        return float("nan"), float("nan")
    L = len(vals)
    means = sorted(sum(vals[rng.randrange(L)] for _ in range(L)) / L for _ in range(n))
    return means[int(0.025 * (n - 1))], means[int(0.975 * (n - 1))]


def _self_test() -> None:
    """A wrong object stored into the LIVE store (via INGEST-VET) scores higher energy than the
    subject's real object -- proving the pass runs end-to-end on the organ's data structures."""
    facts = []
    for i in range(8):
        facts.append(type("F", (), {"subject": f"bio{i}", "obj": "process"})())
        facts.append(type("F", (), {"subject": f"bio{i}", "obj": "molecule"})())
    for i in range(8):
        facts.append(type("F", (), {"subject": f"geo{i}", "obj": "country"})())
        facts.append(type("F", (), {"subject": f"geo{i}", "obj": "region"})())
    store = build_live_store(facts, seed=2)
    store.store("bio0", "GROUNDED_MEANING", "country", "reading:BAD", "TRUST_MID")  # wrong
    en = consistency_energies(store, "GROUNDED_MEANING", k_min=2)
    live = {(f.subject, f.obj): f.fid for f in store.live_facts()}
    e_bad = en[live[("bio0", "country")]]
    e_ok = en[live[("bio0", "molecule")]]
    assert e_bad[0] == "SCORED" and e_ok[0] == "SCORED", (e_bad, e_ok)
    assert e_bad[1] > e_ok[1], (e_bad, e_ok)
    print(f"[self-test] PASS: live-store wrong obj energy {e_bad[1]:.2f} > real obj {e_ok[1]:.2f}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    if args.self_test:
        _self_test()
        return
    import json
    res = run(seed=args.seed, smoke=args.smoke)
    out_dir = os.path.join(_REPO, "data", "exp_consistency_cleanup_live_store_v1")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
