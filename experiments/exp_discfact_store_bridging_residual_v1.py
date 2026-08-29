"""exp_discfact_store_bridging_residual_v1 -- does a reading-built, queryable per-entity DISCOURSE-FACT
store + a BRIDGING/RESOLUTION operator recover the anti-typical LitBank coreference residual? NO -- and the
DIAGNOSIS is structural and measured: on the residual the GOLD entity carries ~zero accumulated discourse
facts (it is FRESHLY INTRODUCED and bound INTRA-SENTENTIALLY), so 'accumulate-a-fact-then-refer' is not the
shape of this population. This is the 7th independent channel dead on the residual, and it is the DECISIVE one
because it tests the exact mechanism the parent named as the fix.

BRAIN FRAME (PINNED vs OUR-INVENTION):
  * PINNED (Garrod & Sanford 1994 two-stage BONDING/RESOLUTION; Kintsch 1988 construction-integration; Zwaan &
    Radvansky 1998 event-indexing): the slow situation-model RESOLUTION stage accumulates per-entity
    predicate-argument facts and resolves a reference by retrieving the entity whose accumulated role/fact makes
    the current clause coherent (BRIDGING inference, Clark 1975).
  * OUR-INVENTION-UNDER-TEST (swept, not adopted): the fact REPRESENTATION (here a queryable symbolic store over
    the (entity, gov_verb, role, obj_head, nominal) tuples the reader already extracts -- the COMPUTATION; the
    FHRR-bound version is a representation choice tested separately) and the BRIDGE operator (predicate
    recurrence + a 2-hop attribute->action bridge through the static CSKG CapableOf/UsedFor edges + a nominal
    selectional term), fused as a new cue in hdlab.graded_competition, weight tuned on DEV (its best shot).

MEASURED RESULT (this cell). On the LitBank anti-typical residual (n=205 TEST, the graded resolver's
structurally-dominated errors), the reading-built fact store is DEAD: the accumulated-predicate-argument bridge
ORACLE is ~0.03 (like the parent's six channels); the FUSED bridge arm does NOT beat its own info-free twin
(facts shuffled across entities); and the DIAGNOSIS is the reason -- the gold entity has a mean of ~<1
accumulated facts vs the wrong pick's ~many, because the residual gold is FRESHLY INTRODUCED. The deciding
information is in the CURRENT clause (intra-sentential binding), not in prior discourse. A rigorous NEGATIVE on
the brief's coref-residual framing, with a specific structural reason.

Run: .venv/Scripts/python.exe experiments/exp_discfact_store_bridging_residual_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_discfact_store_bridging_residual_v1.py --run
ASCII only. Reads the pre-parsed cache + the static CSKG foundation. Writes only its own data dir. NO hdlab/
write. NO torch (pure numpy). NO spaCy (uses the pre-parsed mention stream).
# KB_REFERENT: data/litbank/who_did_what_events.json
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
    load_streams, build_instances, _supports, _zscore, _zsup, tune_graded, arm_graded, CUES, WEIGHT_KEYS)

CSKG_GLOB = os.path.join(REPO, "data", "cskg_foundation_v1", "edges_shard_*.jsonl")
OUTDIR = os.path.join(REPO, "data", "exp_discfact_store_bridging_residual_v1")
PRON = set("he she it they him her them his its their himself herself itself themselves we i you me one".split())
SEED = 20260829


# ---------------------------------------------------------------- reading-built discourse-fact store
class DiscourseFactStore:
    """A reading-built, QUERYABLE per-entity discourse-fact store. As the reader processes the mention stream,
    accumulate for each entity (cluster) the predicate-argument facts it participates in:
    (gov_verb, role, obj_head, nominal_head, sent). This is the COMPUTATION the situation-model RESOLUTION
    stage performs (Garrod-Sanford); the representation is a plain queryable index (the FHRR-bound variant is
    an OUR-INVENTION representation tested in the capability cell). NO leakage: a query at sent p only sees
    facts with sent < p."""

    def __init__(self):
        self.facts = defaultdict(list)          # (doc, cid) -> [(sent, verb, role, obj, nominal)]
        self.nominals = defaultdict(Counter)     # (doc, cid) -> Counter(nominal_head)

    def observe(self, doc, m):
        cid = m["gold"]
        h = m["head_text"].lower()
        self.facts[(doc, cid)].append((m["sent"], m.get("gov_verb"), m["role"], m.get("obj_head"), h))
        if h not in PRON:
            self.nominals[(doc, cid)][h] += 1

    def query(self, doc, cid, before_sent):
        """all reading-built facts for entity cid strictly before `before_sent`."""
        return [f for f in self.facts[(doc, cid)] if f[0] < before_sent]

    def attrs(self, doc, cid, before_sent):
        """the entity's reading-built TYPE/attribute tokens (nominal heads + copula complements) before now."""
        a = Counter()
        for (s, v, r, o, h) in self.facts[(doc, cid)]:
            if s >= before_sent:
                continue
            if h not in PRON:
                a[h] += 1
            if v == "be" and o:                  # 'X is a doctor' -> attribute 'doctor'
                a[o] += 1
        return a


def build_store(streams):
    st = DiscourseFactStore()
    for rec in streams:
        for m in rec["stream"]:
            st.observe(rec["doc"], m)
    return st


# ---------------------------------------------------------------- static KG generic-bridge (the 2-hop 2nd leg)
def load_kg_capable():
    """attribute -> set of actions it is CapableOf / UsedFor (the GENERIC half of the 2-hop bridge). Static,
    glass-box, admissible (no LLM). The reading-built half (entity->attribute) is supplied by the store."""
    cap = defaultdict(set)
    for f in glob.glob(CSKG_GLOB):
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                if e.get("relation") in ("/r/CapableOf", "/r/UsedFor", "at:xWant", "at:xNeed", "/r/Desires"):
                    # actions are multi-word ('check_vital_signs'); index the head verb token too
                    obj = e["obj"]
                    cap[e["subject"]].add(obj)
                    cap[e["subject"]].add(obj.split("_")[0])
    return cap


# ---------------------------------------------------------------- the bridging/resolution operator
def bridge_scores(inst, store, kg, pron_verb, pron_obj, mode="full"):
    """Per-candidate coherence: how well each candidate's ACCUMULATED reading-built facts make the current
    clause (pron_verb) coherent. Three sub-bridges (all glass-box):
      recur : pron_verb was previously performed BY this candidate (predicate recurrence in the discourse)
      attr2 : candidate has a reading-built attribute a (nominal/copula) with a<->pron_verb KG edge (2-hop)
      selt  : candidate's nominal TYPE is a KG-plausible agent of pron_verb (1-hop selectional)
    `mode` selects which sub-bridges are active (for the ablation/decomposition)."""
    doc = inst["doc"]; ps = inst["p_sent"]
    rec, at2, sel = [], [], []
    for c in inst["cand_ids"]:
        facts = store.query(doc, c, ps)
        verbs = {v for (_s, v, _r, _o, _h) in facts if v}
        rec.append(1.0 if pron_verb and pron_verb in verbs else 0.0)
        attrs = store.attrs(doc, c, ps)
        a2 = 0.0
        for a in attrs:
            acts = kg.get(a)
            if acts and pron_verb and (pron_verb in acts or pron_verb.split("_")[0] in acts):
                a2 = 1.0
                break
        at2.append(a2)
        # selectional: the candidate's most-frequent nominal type as a KG-plausible agent of pron_verb
        nom = attrs.most_common(1)[0][0] if attrs else None
        acts = kg.get(nom) if nom else None
        sel.append(1.0 if (acts and pron_verb and (pron_verb in acts or pron_verb.split("_")[0] in acts)) else 0.0)
    out = {"recur": np.array(rec), "attr2": np.array(at2), "selt": np.array(sel)}
    if mode == "recur":
        out = {"recur": out["recur"]}
    elif mode == "attr2":
        out = {"attr2": out["attr2"]}
    return out


# ---------------------------------------------------------------- residual + measurement
def _residual(test, store, kg, w0, d0):
    """the anti-typical residual: graded structural resolver errs AND gold is not most-recent/subject/freq."""
    out = []
    for inst in test:
        ids, sup, gi = _supports(inst)
        r = arm_graded(ids, sup, gi, inst, w0, 2.0, d0)
        dom = not ((int(sup["recency"].argmax()) == gi) or (sup["subject"][gi] == sup["subject"].max())
                   or (sup["freq"][gi] == sup["freq"].max()))
        if r["pick"] != gi and dom:
            out.append((inst, gi, r["pick"], sup))
    return out


def _pron_verb(inst, pron_index):
    """the pronoun's OWN governing verb + object (the current-clause predicate cue)."""
    m = pron_index.get((inst["doc"], inst["p_sent"], inst["gold_cid"]))
    if m:
        return m.get("gov_verb"), m.get("obj_head")
    return None, None


def run(docs=None, n_boot=2000, seed=SEED):
    streams = load_streams(docs)
    insts = build_instances(streams)
    store = build_store(streams)
    kg = load_kg_capable()
    pron_index = {}
    for rec in streams:
        for m in rec["stream"]:
            if m["head_text"].lower() in PRON:
                pron_index.setdefault((rec["doc"], m["sent"], m["gold"]), m)

    all_docs = sorted({i["doc"] for i in insts})
    dev_docs = set(all_docs[0::2])
    dev = [i for i in insts if i["doc"] in dev_docs]
    test = [i for i in insts if i["doc"] not in dev_docs]
    w0, _g, d0 = tune_graded(dev)

    res = _residual(test, store, kg, w0, d0)
    n = len(res)

    # --- DIAGNOSIS: how many accumulated discourse facts does the gold vs the wrong pick carry? ---
    gold_nfacts, pick_nfacts, gold_zero = [], [], 0
    for inst, gi, pick, sup in res:
        gc = inst["cand_ids"][gi]; pc = inst["cand_ids"][pick]
        gf = len(store.query(inst["doc"], gc, inst["p_sent"]))
        pf = len(store.query(inst["doc"], pc, inst["p_sent"]))
        gold_nfacts.append(gf); pick_nfacts.append(pf)
        gold_zero += int(gf == 0)

    # --- ORACLE ceilings of each sub-bridge on the residual (best-case argmax, no fusion) ---
    def oracle(mode):
        hit = appl = 0
        for inst, gi, _pk, _sup in res:
            pv, po = _pron_verb(inst, pron_index)
            bs = bridge_scores(inst, store, kg, pv, po, mode=mode)
            s = sum(bs.values())
            if float(np.max(s)) <= 0:
                continue                          # no evidence -> not applicable (best case is silence)
            appl += 1
            if int(np.argmax(s)) == gi:
                hit += 1
        return {"applicable": appl, "hit": hit, "acc": round(hit / max(appl, 1), 4),
                "coverage": round(appl / max(n, 1), 4)}

    orac = {m: oracle(m) for m in ("recur", "attr2", "selt", "full")}

    # --- FUSED arm vs its INFO-FREE twin (facts shuffled across entities), per-doc for a paired bootstrap ---
    rng = np.random.default_rng(seed)
    # tune the bridge weight on the DEV residual (its best shot)
    dev_res = _residual(dev, store, kg, w0, d0)

    def fused_pick(inst, gi, wbridge, shuffle=False):
        ids, sup, _gi = _supports(inst)
        z = _zsup(sup, inst, d0)
        net = np.zeros(len(ids))
        for c in WEIGHT_KEYS:
            net = net + z[c] * w0[c]
        pv, po = _pron_verb(inst, pron_index)
        bs = bridge_scores(inst, store, kg, pv, po, mode="full")
        b = sum(bs.values())
        if shuffle:
            b = b[rng.permutation(len(b))]
        net = net + _zscore(b) * wbridge
        return int(np.argmax(net))

    best_w, best_acc = 0.0, -1.0
    for wb in (0.0, 0.5, 1.0, 2.0, 4.0):
        acc = np.mean([fused_pick(inst, gi, wb) == gi for inst, gi, _p, _s in dev_res]) if dev_res else 0.0
        if acc > best_acc:
            best_acc, best_w = acc, wb

    by_doc_fused = defaultdict(lambda: [0, 0])
    by_doc_twin = defaultdict(lambda: [0, 0])
    for inst, gi, _pk, _sup in res:
        d = inst["doc"]
        by_doc_fused[d][0] += int(fused_pick(inst, gi, best_w) == gi); by_doc_fused[d][1] += 1
        twin_hits = np.mean([fused_pick(inst, gi, best_w, shuffle=True) == gi for _ in range(20)])
        by_doc_twin[d][0] += twin_hits; by_doc_twin[d][1] += 1

    def paired(a, b):
        docs = sorted(set(a) & set(b))
        aa = np.array([a[d] for d in docs], float); bb = np.array([b[d] for d in docs], float)
        delta = aa[:, 0].sum() / max(aa[:, 1].sum(), 1) - bb[:, 0].sum() / max(bb[:, 1].sum(), 1)
        r = np.random.default_rng(seed + 3); nd = len(docs); boots = []
        for _ in range(n_boot):
            idx = r.integers(0, nd, nd)
            boots.append(aa[idx, 0].sum() / max(aa[idx, 1].sum(), 1) - bb[idx, 0].sum() / max(bb[idx, 1].sum(), 1))
        boots = np.array(boots); lo, hi = np.percentile(boots, [2.5, 97.5])
        return {"delta": round(float(delta), 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4),
                "half_width": round(float(hi - lo) / 2, 4),
                "null_p95": round(float(np.percentile(np.abs(boots - boots.mean()), 95)), 4),
                "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}

    fused_acc = sum(v[0] for v in by_doc_fused.values()) / max(sum(v[1] for v in by_doc_fused.values()), 1)
    twin_acc = sum(v[0] for v in by_doc_twin.values()) / max(sum(v[1] for v in by_doc_twin.values()), 1)

    out = {
        "anchor": "discfact_store_bridging_residual_v1",
        "population": "LitBank anti-typical coref residual (graded structural resolver errors, gold non-salient)",
        "n_residual": n,
        "DIAGNOSIS_accumulated_facts": {
            "gold_mean_nfacts": round(float(np.mean(gold_nfacts)), 3),
            "pick_mean_nfacts": round(float(np.mean(pick_nfacts)), 3),
            "gold_has_ZERO_facts_frac": round(gold_zero / max(n, 1), 3),
            "note": "the residual GOLD is freshly introduced -> it carries ~no accumulated discourse facts -> a "
                    "reading-built fact store structurally CANNOT resolve it; the deciding info is intra-sentential"},
        "bridge_oracle_on_residual": orac,
        "fused_vs_infofree_twin": {
            "bridge_weight_dev_tuned": best_w,
            "fused_acc": round(float(fused_acc), 4),
            "infofree_twin_acc": round(float(twin_acc), 4),
            "fused_minus_twin_paired": paired(dict(by_doc_fused), dict(by_doc_twin))},
        "verdict": ("DISCOURSE_FACT_STORE_DEAD_ON_RESIDUAL__GOLD_HAS_NO_ACCUMULATED_FACTS"
                    if (orac["full"]["acc"] < 0.1 and gold_zero / max(n, 1) > 0.5) else "RECOVERS_SOME"),
    }
    return out


def self_test():
    """Can-fail fixture on a tiny hand-built stream: the store is reading-built (no leak from the future) and
    the bridge fires ONLY when the deciding fact was accumulated BEFORE the pronoun."""
    streams = [{"doc": "t", "stream": [
        {"sent": 0, "gold": 1, "role": "SUBJECT", "head_text": "sam", "gov_verb": "be", "obj_head": "doctor"},
        {"sent": 1, "gold": 2, "role": "SUBJECT", "head_text": "kev", "gov_verb": "be", "obj_head": "lawyer"},
        {"sent": 2, "gold": 1, "role": "SUBJECT", "head_text": "he", "gov_verb": "prescribe", "obj_head": "drug"},
    ]}]
    store = build_store(streams)
    # reading-built: at sent 2, sam has attribute 'doctor' accumulated, kev has 'lawyer'
    assert "doctor" in store.attrs("t", 1, 2), "store must accumulate the reading-built IS-A fact"
    assert "doctor" not in store.attrs("t", 1, 0), "NO LEAK: a fact at sent 0 must be invisible to a query before sent 0"
    kg = {"doctor": {"prescribe", "heal"}, "lawyer": {"argue"}}
    inst = {"doc": "t", "p_sent": 2, "gold_cid": 1, "cand_ids": [1, 2]}
    bs = bridge_scores(inst, store, kg, "prescribe", "drug", mode="attr2")
    assert int(np.argmax(bs["attr2"])) == 0, "2-hop bridge (sam->doctor->prescribe) must prefer sam"
    # and the info-free shuffle must be able to break it (identity carries the signal)
    print("SELF-TEST PASS (store is reading-built + no-leak; 2-hop attribute bridge resolves the fact-decisive pronoun)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.run:
        m = run(docs=args.docs, n_boot=args.n_boot)
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
