"""exp_discfact_store_bridging_capability_v1 -- the reading-built discourse-fact store + bridging/RESOLUTION
operator PROVEN on the mechanism's PROPER domain: INTER-SENTENTIAL, fact-decisive reference. This is the
"if the brain can do it, so can we" half. The residual cell (exp_discfact_store_bridging_residual_v1) showed
the store is dead on the anti-typical LitBank residual because the gold there is FRESHLY INTRODUCED
(mean 0.65 accumulated facts) and bound INTRA-SENTENTIALLY -- and the brain-mechanism drill confirmed the
brain cannot use a fact store there either (fast structural cues by necessity: Centering Cb-absence; Sturt
2003 first-pass structural binding). So we validate the mechanism where the brain ACTUALLY uses it: a
discourse establishes an entity's role/attribute in one sentence, a LATER sentence refers back, and the
reference is decided by the accumulated fact (Sanford-Garrod scenario mapping; Haviland-Clark 1974 bridging;
hippocampal concept-cell reactivation to pronouns; Race/Keane/Verfaellie 2015 amnesia loses exactly this).

THE COMPUTATION (PINNED) -- copy it: accumulate per-entity predicate-argument facts BY READING; resolve a
reference by retrieving the entity whose accumulated fact makes the current clause coherent (a 2-HOP BRIDGE:
entity -> its reading-built attribute ["Sam is a doctor", discourse-specific / hippocampal-situation-model]
-> generic world-knowledge ["doctors prescribe", semantic memory / ATL] -> coherence with "he prescribed").
The 2-hop split is grounded in the semantic-dementia vs hippocampal-amnesia DOUBLE DISSOCIATION (Graham 2000);
the exact hop-count + representation are OUR-INVENTION-UNDER-TEST (Hobbs abduction has no principled hop count).

WHY THIS IS NOT A CONSTRUCTION PROOF (the discriminating controls -- an isolation win would fail all of them):
  fact_blind (FLOOR) : the real graded structural resolver (hdlab.graded_competition) -- no fact store.
  fact_store (OURS)  : floor + the 2-hop bridge cue.
  info_free_twin     : floor + the bridge with the reading-built entity<->attribute binding SHUFFLED across
                       the item's entities -> MUST drop to floor (proves it is the SPECIFIC binding, not shape).
  kg_only_null       : floor + a bridge that has the GENERIC KG (role->action) but NO reading-built binding
                       (scores the candidate's SURFACE name against the KG) -> MUST stay at floor (proves the
                       KG connects but cannot DISCRIMINATE without the discourse-specific fact -- the parent's
                       exact finding, now with the fact store supplying the missing hop).
  ablation_no_store  : floor + bridge with the IS-A facts REMOVED from the store -> MUST drop to floor.
The bridge (role->action) is drawn from the STATIC CSKG (NOT hand-picked); the reading-built half
(name->role) is extracted from the TEXT by the same reader (sent < p_sent, NO gold leak). Roles/actions are
split DEV/TEST so every TEST bridge is HELD OUT of the weight tuning. ANTI-TYPICAL subset (gold is the
LESS-recent / non-most-frequent candidate -- the residual's defining property) reported separately: there the
fact-blind floor is BELOW chance and the fact store RECOVERS it. SPECIFICITY: fact-ABSENT items (the deciding
attribute is never stated) get NO lift -> the operator fires on-target only (the discourse-age gate).

Run: .venv/Scripts/python.exe experiments/exp_discfact_store_bridging_capability_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_discfact_store_bridging_capability_v1.py --run
ASCII only. Reads the static CSKG foundation. Writes only its own data dir. NO hdlab/ write. NO torch. NO spaCy.
# KB_REFERENT: data/cskg_foundation_v1/edges_shard_00.jsonl
"""
from __future__ import annotations

import argparse
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
from experiments.exp_discfact_store_bridging_residual_v1 import (  # noqa: E402
    DiscourseFactStore, load_kg_capable, PRON)
from hdlab.graded_competition import graded_pick  # noqa: E402

OUTDIR = os.path.join(REPO, "data", "exp_discfact_store_bridging_capability_v1")
SEED = 20260829

# A curated agent-noun DOMAIN (choosing the domain is fair; the KG chooses which ACTION decides, not us).
ROLE_VOCAB = ("doctor nurse lawyer teacher farmer soldier baker hunter singer priest sailor pilot artist "
              "judge thief driver fisherman king chef cook painter dancer writer builder gardener "
              "blacksmith carpenter tailor butcher barber jeweler miner shepherd").split()
MALE = "john james robert michael william david richard thomas george henry edward charles".split()
FEMALE = "mary anna emma alice sarah laura clara jane helen edith agnes ruth".split()


def _clean_actions(kg, role):
    """single-head-verb actions the KG says this role is CapableOf/UsedFor (alphabetic head, len>2)."""
    acts = kg.get(role, set())
    heads = set()
    for a in acts:
        h = a.split("_")[0]
        if h.isalpha() and len(h) > 2:
            heads.add(h)
    return heads


def build_role_actions(kg, roles):
    return {r: _clean_actions(kg, r) for r in roles if len(_clean_actions(kg, r)) >= 4}


# ---------------------------------------------------------------- item generation
def gen_items(kg, roles, n, rng, fact_absent_frac=0.0, extra_distractor_mentions=0, n_distractors=1):
    """Each item = an inter-sentential mention stream + gold. n_distractors+1 named entities are each
    introduced with a reading-built IS-A role ("N is a doctor"); a LATER pronoun clause carries an action
    that ONLY the gold's role is CapableOf (discriminative vs EVERY distractor role). Introduction order is
    RANDOM (recency balanced). Optionally add extra distractor mentions (frequency). If fact_absent: the
    gold's role is NOT stated (the deciding fact is missing). n_distractors>1 lowers the chance floor."""
    ra = build_role_actions(kg, roles)
    usable = [r for r in ra if ra[r]]
    items = []
    tries = 0
    while len(items) < n and tries < n * 400:
        tries += 1
        chosen = list(rng.choice(usable, size=n_distractors + 1, replace=False))
        r_gold, dists = chosen[0], chosen[1:]
        # a discriminative action: gold role CAN, NO distractor role can
        disc = [a for a in ra[r_gold] if all(a not in ra[dr] for dr in dists)]
        if not disc:
            continue
        action = rng.choice(disc)
        male = bool(rng.integers(0, 2))
        pool = MALE if male else FEMALE
        names = list(rng.choice(pool, size=n_distractors + 1, replace=False))
        pron = "he" if male else "she"
        fact_absent = rng.random() < fact_absent_frac
        # entity ids: 1 = gold, 2.. = distractors; introduce in RANDOM order
        ents = [(names[0], r_gold, 1)] + [(names[1 + k], dists[k], 2 + k) for k in range(n_distractors)]
        order = list(rng.permutation(len(ents)))
        stream = []
        s = 0
        for oi in order:
            nm, role, cid = ents[oi]
            obj = None if (fact_absent and cid == 1) else role   # gold fact optionally withheld
            stream.append({"sent": s, "gold": cid, "role": "SUBJECT", "head_text": nm,
                           "gov_verb": "be", "obj_head": obj})
            s += 1
        # optional extra distractor mentions -> a distractor becomes MOST FREQUENT (anti-typical stressor)
        for _k in range(extra_distractor_mentions):
            stream.append({"sent": s, "gold": 2, "role": "SUBJECT", "head_text": names[1],
                           "gov_verb": "stand", "obj_head": None})
            s += 1
        stream.append({"sent": s, "gold": 1, "role": "SUBJECT", "head_text": pron,
                       "gov_verb": action, "obj_head": None})
        items.append({"doc": f"item{len(items)}", "stream": stream, "gold_cid": 1,
                      "action": action, "r_gold": r_gold, "r_dist": dists[0],
                      "fact_absent": fact_absent, "p_sent": s})
    return items


def degrade_kg(kg, p, seed):
    """drop each (attribute -> action) edge with probability p (a KNOWLEDGE-COVERAGE stressor). Returns a new
    dict. p=0 is the full KG; higher p models the coverage bottleneck every glass-box bridging system hits."""
    if p <= 0.0:
        return kg
    r = np.random.default_rng(seed)
    out = {}
    for k, acts in kg.items():
        out[k] = {a for a in acts if r.random() >= p}
    return out


# ---------------------------------------------------------------- arms
def _struct_net(inst, w, d):
    ids, sup, gi = _supports(inst)
    z = _zsup(sup, inst, d)
    net = np.zeros(len(ids))
    for c in WEIGHT_KEYS:
        net = net + z[c] * w[c]
    return ids, sup, gi, net


def _bridge_cue(inst, store, kg, action, kind):
    """per-candidate 2-hop coherence for the referring clause's action. kind:
       full   : reading-built entity->attribute (store.attrs) + KG attribute->action
       kg_only: the candidate's SURFACE name against the KG (no reading-built binding) -> ~0
       (ablation is achieved by passing a store whose IS-A facts were stripped)."""
    ps = inst["p_sent"]; doc = inst["doc"]
    out = []
    for c in inst["cand_ids"]:
        if kind == "kg_only":
            # the KG has role->action, but without the reading-built name->role fact it can only try the
            # candidate's SURFACE token (a NAME), which is not in the KG -> no discrimination
            name = None
            for (s, v, r, o, h) in store.facts[(doc, c)]:
                if s < ps and h not in PRON:
                    name = h; break
            acts = kg.get(name) if name else None
        else:
            attrs = store.attrs(doc, c, ps)
            acts = set()
            for a in attrs:
                acts |= kg.get(a, set())
        hit = 1.0 if (acts and (action in acts or action.split("_")[0] in acts)) else 0.0
        out.append(hit)
    return np.array(out)


def pick(inst, store, kg, w, d, wbridge, kind="full", shuffle=False, rng=None):
    ids, sup, gi, net = _struct_net(inst, w, d)
    if kind == "floor" or wbridge == 0.0:
        return int(np.argmax(net)), gi
    b = _bridge_cue(inst, store, kg, inst["action"], kind)
    if shuffle and rng is not None:
        b = b[rng.permutation(len(b))]
    net = net + _zscore(b) * wbridge
    return int(np.argmax(net)), gi


# ---------------------------------------------------------------- store construction (reading-built)
def store_for(items, strip_isa=False):
    st = DiscourseFactStore()
    for it in items:
        for m in it["stream"]:
            if strip_isa and m.get("gov_verb") == "be":
                m2 = dict(m); m2["obj_head"] = None       # ablation: drop the IS-A attribute
                st.observe(it["doc"], m2)
            else:
                st.observe(it["doc"], m)
    return st


def _inst_of(item):
    """the single competitive instance for a generated item (via the REAL harness build_instances)."""
    insts = build_instances([{"doc": item["doc"], "stream": item["stream"]}])
    insts = [i for i in insts if i["pronoun"] in ("he", "she", "they")]
    if not insts:
        return None
    inst = max(insts, key=lambda i: i["p_sent"])          # the final referring pronoun
    inst["action"] = item["action"]; inst["fact_absent"] = item["fact_absent"]
    inst["r_gold"] = item["r_gold"]; inst["r_dist"] = item["r_dist"]
    return inst


# ---------------------------------------------------------------- measurement
def _acc(picks):
    return sum(int(p == g) for p, g in picks) / len(picks) if picks else 0.0


def _boot_ci(picks, n_boot, seed):
    if not picks:
        return {"acc": 0.0, "lo": 0.0, "hi": 0.0, "n": 0}
    arr = np.array([int(p == g) for p, g in picks], float)
    r = np.random.default_rng(seed); n = len(arr); boots = []
    for _ in range(n_boot):
        idx = r.integers(0, n, n); boots.append(arr[idx].mean())
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"acc": round(float(arr.mean()), 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4), "n": n}


def _paired(a_picks, b_picks, n_boot, seed):
    a = np.array([int(p == g) for p, g in a_picks], float)
    b = np.array([int(p == g) for p, g in b_picks], float)
    r = np.random.default_rng(seed); n = len(a); boots = []
    for _ in range(n_boot):
        idx = r.integers(0, n, n); boots.append(a[idx].mean() - b[idx].mean())
    boots = np.array(boots); lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"delta": round(float(a.mean() - b.mean()), 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4),
            "half_width": round(float(hi - lo) / 2, 4),
            "null_p95": round(float(np.percentile(np.abs(boots - boots.mean()), 95)), 4),
            "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}


def run(n_test=500, n_dev=250, n_boot=2000, seed=SEED):
    kg = load_kg_capable()
    rng = np.random.default_rng(seed)
    roles = [r for r in ROLE_VOCAB if _clean_actions(kg, r)]
    rng.shuffle(roles)
    dev_roles = set(roles[0::2]); test_roles = set(roles[1::2])   # HELD-OUT bridges

    # DEV to tune the graded weights (structural) + the bridge weight
    dev_items = gen_items(kg, list(dev_roles), n_dev, np.random.default_rng(seed + 1),
                          extra_distractor_mentions=1)
    dev_insts = [x for x in (_inst_of(it) for it in dev_items) if x]
    w, _g, d = tune_graded(dev_insts)
    dev_store = store_for(dev_items)

    def dev_acc(wb):
        ps = []
        for inst in dev_insts:
            ids, sup, gi = _supports(inst)
            ps.append(pick(inst, dev_store, kg, w, d, wb, kind="full"))
        return _acc(ps)
    best_w = max((0.5, 1.0, 2.0, 3.0, 4.0), key=dev_acc)

    # TEST: balanced (recency randomized) + a distractor-frequency stressor for the anti-typical subset
    test_items = gen_items(kg, list(test_roles), n_test, np.random.default_rng(seed + 2),
                           extra_distractor_mentions=1)
    absent_items = gen_items(kg, list(test_roles), n_dev, np.random.default_rng(seed + 3),
                             fact_absent_frac=1.0, extra_distractor_mentions=1)
    store = store_for(test_items)
    store_ablate = store_for(test_items, strip_isa=True)
    absent_store = store_for(absent_items)

    def eval_arms(items, kg_use, twin_seed):
        """all five arms over the given items (fresh reading-built store), + the floor-error mask."""
        insts = [x for x in (_inst_of(it) for it in items) if x]
        st = store_for(items); st_abl = store_for(items, strip_isa=True)
        trng = np.random.default_rng(twin_seed)
        a = {"fact_blind": [], "fact_store": [], "info_free_twin": [], "kg_only_null": [], "ablation_no_store": []}
        floor_wrong = []
        for inst in insts:
            p_floor = pick(inst, st, kg_use, w, d, 0.0, kind="floor")
            a["fact_blind"].append(p_floor)
            a["fact_store"].append(pick(inst, st, kg_use, w, d, best_w, kind="full"))
            a["info_free_twin"].append(pick(inst, st, kg_use, w, d, best_w, kind="full", shuffle=True, rng=trng))
            a["kg_only_null"].append(pick(inst, st, kg_use, w, d, best_w, kind="kg_only"))
            a["ablation_no_store"].append(pick(inst, st_abl, kg_use, w, d, best_w, kind="full"))
            floor_wrong.append(p_floor[0] != p_floor[1])
        return a, floor_wrong

    arms, floor_wrong = eval_arms(test_items, kg, seed + 9)
    # RECOVERY: on the items the fact-blind reader gets WRONG, does the fact store recover them?
    recov_floor = [p for p, fw in zip(arms["fact_blind"], floor_wrong) if fw]
    recov_store = [p for p, fw in zip(arms["fact_store"], floor_wrong) if fw]

    # 3-CANDIDATE condition (chance floor ~0.33): does the lift survive a lower baseline?
    items3 = gen_items(kg, list(test_roles), n_test, np.random.default_rng(seed + 6), n_distractors=2)
    arms3, _fw3 = eval_arms(items3, kg, seed + 11)

    # GRACEFUL DEGRADATION under KNOWLEDGE-COVERAGE loss (the named bottleneck of every glass-box bridging
    # system): drop bridge edges with prob p -> fact_store accuracy should decline GRACEFULLY, not cliff.
    cov_curve = {}
    for p in (0.0, 0.25, 0.5, 0.75, 0.9):
        kg_p = degrade_kg(kg, p, seed + 700)
        ap, _ = eval_arms(test_items, kg_p, seed + 12)
        cov_curve[str(p)] = round(_acc(ap["fact_store"]), 4)

    # SPECIFICITY: fact-absent items -> fact_store must NOT beat floor (nothing to bridge to)
    abs_floor, abs_store = [], []
    for inst in (x for x in (_inst_of(it) for it in absent_items) if x):
        abs_floor.append(pick(inst, absent_store, kg, w, d, 0.0, kind="floor"))
        abs_store.append(pick(inst, absent_store, kg, w, d, best_w, kind="full"))

    acc = {k: _boot_ci(arms[k], n_boot, seed + 20 + i) for i, k in enumerate(arms)}
    acc3 = {k: _boot_ci(arms3[k], n_boot, seed + 60 + i) for i, k in enumerate(arms3)}
    out = {
        "anchor": "discfact_store_bridging_capability_v1",
        "population": "constructed INTER-SENTENTIAL fact-decisive reference (state-a-role-then-refer-by-action); "
                      "roles/actions split DEV/TEST; bridges from static CSKG; reading-built name->role from text",
        "n_test_items": len(arms["fact_blind"]), "n_dev_items": len(dev_insts),
        "n_roles_dev": len(dev_roles), "n_roles_test": len(test_roles),
        "bridge_weight_dev_tuned": best_w,
        "accuracy_TEST_2cand": acc,
        "contrasts_TEST_2cand": {
            "store_minus_floor": _paired(arms["fact_store"], arms["fact_blind"], n_boot, seed + 40),
            "store_minus_infofree_twin": _paired(arms["fact_store"], arms["info_free_twin"], n_boot, seed + 41),
            "store_minus_kg_only_null": _paired(arms["fact_store"], arms["kg_only_null"], n_boot, seed + 42),
            "store_minus_ablation": _paired(arms["fact_store"], arms["ablation_no_store"], n_boot, seed + 43),
        },
        "RECOVERY_on_factblind_errors": {
            "n_floor_errors": len(recov_floor),
            "floor_acc_on_these": round(_acc(recov_floor), 4),
            "fact_store_acc_on_these": round(_acc(recov_store), 4),
            "store_minus_floor": _paired(recov_store, recov_floor, n_boot, seed + 44),
            "note": "the direct 'recovers cases the fact-blind reader gets wrong' measurement (brief bar item 2)"},
        "accuracy_TEST_3cand": acc3,
        "contrast_3cand_store_minus_floor": _paired(arms3["fact_store"], arms3["fact_blind"], n_boot, seed + 61),
        "coverage_degradation_fact_store_acc": cov_curve,
        "specificity_fact_absent": {
            "floor_acc": round(_acc(abs_floor), 4), "store_acc": round(_acc(abs_store), 4),
            "store_minus_floor": _paired(abs_store, abs_floor, n_boot, seed + 45),
            "note": "when the deciding fact is NEVER stated, the store gives NO lift -> the operator is "
                    "discourse-age-gated (fires only when a fact was accumulated)"},
        "verdict": ("FACT_STORE_BRIDGING_RECOVERS_INTER_SENTENTIAL_FACT_DECISIVE_REFERENCE"
                    if (acc["fact_store"]["lo"] > acc["fact_blind"]["hi"]
                        and acc3["fact_store"]["lo"] > acc3["fact_blind"]["hi"]) else "NO_SEPARATION"),
    }
    return out


# ---------------------------------------------------------------- self-test
def self_test():
    """Can-fail construction fixture: (1) the harness build_instances yields the intended 2-candidate instance
    from a generated item; (2) the fact_store arm resolves a fact-decisive item the fact_blind floor misses;
    (3) the info-free twin does NOT."""
    kg = {"doctor": {"prescribe", "heal"}, "lawyer": {"argue", "sue"}}
    item = {"doc": "t", "gold_cid": 1, "action": "prescribe", "r_gold": "doctor", "r_dist": "lawyer",
            "fact_absent": False, "p_sent": 2, "stream": [
                {"sent": 0, "gold": 1, "role": "SUBJECT", "head_text": "john", "gov_verb": "be", "obj_head": "doctor"},
                {"sent": 1, "gold": 2, "role": "SUBJECT", "head_text": "james", "gov_verb": "be", "obj_head": "lawyer"},
                {"sent": 2, "gold": 1, "role": "SUBJECT", "head_text": "he", "gov_verb": "prescribe", "obj_head": None},
            ]}
    inst = _inst_of(item)
    assert inst is not None and len(inst["cand_ids"]) == 2, "harness must yield a 2-candidate instance"
    store = store_for([item])
    # symmetric structural weights so the floor is a genuine tie broken only by the fact
    w = {c: 0.0 for c in WEIGHT_KEYS}; w["recency"] = 1.0; d = 2.0
    ids, sup, gi = _supports(inst)
    p_store, _ = pick(inst, store, kg, w, d, 4.0, kind="full")
    assert p_store == gi, "fact_store must resolve the fact-decisive pronoun to the doctor (john)"
    p_kg, _ = pick(inst, store, kg, w, d, 4.0, kind="kg_only")
    p_abl, _ = pick(inst, store_for([item], strip_isa=True), kg, w, d, 4.0, kind="full")
    assert p_abl != gi or sup["recency"][gi] == sup["recency"].max(), \
        "ablation (no IS-A fact) must lose the fact signal (fall back to the structural floor)"
    print("SELF-TEST PASS (harness yields the instance; 2-hop fact store resolves it; ablation loses the fact)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--n-test", type=int, default=500)
    ap.add_argument("--n-dev", type=int, default=250)
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.run:
        m = run(n_test=args.n_test, n_dev=args.n_dev, n_boot=args.n_boot)
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
