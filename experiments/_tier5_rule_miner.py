"""
_tier5_rule_miner.py -- substrate Tier-5 self-discovery primitive: mine methodology rules from solution_history -- packaged for re-use.

ROUTING: Research Cycle 46 close (research_to_exp_dev_TIER5_MECHANISM_VALIDATED_FIRST_APPEARANCE) -- "file the substrate_extracted_rules
  miner as a substrate Tier-5 primitive; re-run post-Phase-6 + post 5+ new solution_history entries + quarterly." This is the clean,
  cell/benchmark-decoupled miner: given a loaded PartitionedStore, it mines atom.solution_history (capability->mechanism->metric
  replacement chains) for candidate methodology rules (recurring replacement + universal lever), with MECHANISM-CONTAINMENT novelty
  (a candidate is novel only if its mechanism pair isn't already named in any rule -- per the 6th rule candidate; keyword-overlap is
  too shallow). Pure function; no LLM-judge. Testbed co-locates to backend/substrate_index/ when ready (route_primitives pattern).
"""
from __future__ import annotations
from collections import defaultdict

_STOP = {"the", "to", "a", "of", "is", "rule", "via", "for", "and", "with", "when", "not", "substrate"}


def _toks(s):
    return set(w for w in "".join(c if c.isalnum() else " " for c in (s or "").lower()).split() if w not in _STOP and len(w) > 2)


def mech_name(qid):
    """short mechanism name from an atom qid: drop corpus:: + tier prefix -> the leaf."""
    s = qid.split("::", 1)[1] if "::" in qid else qid
    return s.split("/")[-1].lower()


def _metric_val(m):
    if isinstance(m, dict):
        return m.get("value")
    return m if isinstance(m, (int, float)) else None


def _rule_texts(atoms):
    """existing methodology-rule descriptions + the documented universal-lever finding (novelty baseline)."""
    out = []
    for a in atoms:
        corp = str(getattr(a.corpus, "value", a.corpus)).lower()
        if corp in ("meta", "methodology") and "rule" in (a.id or "").lower():
            out.append(((a.id or "") + " " + (getattr(a, "description", "") or "")).lower())
    out.append("discriminative perceptron weighting universal lever current best across capabilities")
    return out


def mine_methodology_rules(pstore, min_caps=2, min_lift=0.05):
    """Mine solution_history for candidate methodology rules. Returns dict with candidate lists + the top NOVEL recurring rule (or None).

    A candidate is NOVEL only if its mechanism(s) are not already co-named in any existing rule text (mechanism-containment).
    """
    atoms = pstore.all_atoms()
    rule_text = _rule_texts(atoms)

    def mech_known(*mechs):
        for txt in rule_text:
            if all(m in txt for m in mechs):
                return True
        return False

    transitions = defaultdict(lambda: {"caps": set(), "deltas": []})
    lever = defaultdict(lambda: {"caps": set(), "metrics": []})
    n_sh = 0
    for a in atoms:
        sh = getattr(a, "solution_history", None)
        if not sh:
            continue
        n_sh += 1
        chain = sorted(sh, key=lambda e: (e.get("adopted_date") or ""))
        for i, e in enumerate(chain):
            mid = e.get("solution_atom_id"); mv = _metric_val(e.get("empirical_metric"))
            if not mid:
                continue
            m = mech_name(mid)
            if mv is not None and (e.get("status") == "current" or e.get("replaced_date") is None):
                lever[m]["caps"].add(a.id); lever[m]["metrics"].append(mv)
            if i > 0:
                p = chain[i - 1]; pmid = p.get("solution_atom_id"); pmv = _metric_val(p.get("empirical_metric"))
                if pmid and mv is not None and pmv is not None:
                    transitions[(mech_name(pmid), m)]["caps"].add(a.id)
                    transitions[(mech_name(pmid), m)]["deltas"].append(mv - pmv)

    candidates = []
    for (old, new), d in transitions.items():
        deltas = d["deltas"]; avg = sum(deltas) / len(deltas) if deltas else 0.0
        candidates.append({"type": "replacement", "name": "RULE_%s_to_%s" % (old, new), "n_caps": len(d["caps"]),
                           "avg_lift": round(avg, 4), "consistent": all(x >= 0 for x in deltas) if deltas else False,
                           "novel": not mech_known(old, new), "support": sorted(d["caps"])})
    for m, d in lever.items():
        if len(d["caps"]) >= 3:
            acc = [x for x in d["metrics"] if x is not None and x <= 1.0] or d["metrics"]
            candidates.append({"type": "universal_lever", "name": "RULE_%s_universal_lever" % m, "n_caps": len(d["caps"]),
                               "avg_metric": round(sum(acc) / max(1, len(acc)), 4), "avg_lift": 0.0, "consistent": True,
                               "novel": not mech_known(m), "support": sorted(d["caps"])})

    novel = [c for c in candidates if c["novel"] and c["n_caps"] >= min_caps and
             ((c["type"] == "replacement" and c["avg_lift"] > min_lift and c["consistent"]) or
              (c["type"] == "universal_lever" and c["n_caps"] >= 3))]
    novel.sort(key=lambda c: (c["n_caps"], c["avg_lift"]), reverse=True)
    re_derived = [c for c in candidates if (not c["novel"]) and c["n_caps"] >= min_caps]
    return {"n_sh_atoms": n_sh, "candidates": candidates, "novel_recurring": novel, "re_derived": re_derived,
            "top_novel": novel[0] if novel else None}


def _selftest():
    assert mech_name("math::T3/discriminative_perceptron") == "discriminative_perceptron"
    assert _metric_val({"name": "a", "value": 0.5}) == 0.5
    print("[selftest] PASS: tier5-rule-miner")


if __name__ == "__main__":
    _selftest()
