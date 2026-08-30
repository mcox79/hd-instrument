"""SECOND-ADJUDICATOR robustness: inter-adjudicator agreement + re-score the gate on an INDEPENDENT
   adjudicator's labels and on the CONSENSUS. (problem: the_force_dynamic_reader_needs_a_literal_sense_and_attachment_gate)

The primary gold and the RACE held-out were labeled by ONE adjudicator (this solver). Here a SECOND,
INDEPENDENT adjudicator (a blind agent that saw ONLY the sentences + the A/B/C/O criterion -- never the gate,
never my labels) re-labels the same items. We report:
  * Cohen's KAPPA on the BINARY engage-decision (A vs not-A), adjudicator-1 (me) vs adjudicator-2 (agent).
  * The gate's FIRE-PRECISION / RECALL recomputed on (a) adjudicator-2's labels and (b) the CONSENSUS subset
    (items where both agree) -- if the headline SURVIVES an independent labeling and the consensus, it is not
    an artifact of one annotator.

Agent labels are read from JSON files: {"1": "A", "2": "C", ...}. Paths default to the scratchpad drop.
ASCII only. No LLM at inference. No hdlab writes.
"""
from __future__ import annotations

import json
import os
import random
import sys
from typing import Dict, List

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._literalness_gold import load_gold as load_primary
from experiments._dump_for_second_adjudicator import load_race_large
from experiments._literalness_gate import LiteralnessGate
import experiments.exp_literalness_gate_v1 as V
import experiments.exp_literalness_gate_heldout_race_v1 as H


def cohen_kappa(a: List[bool], b: List[bool]) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pa1 = sum(a) / n
    pb1 = sum(b) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    return (po - pe) / (1 - pe) if (1 - pe) > 1e-9 else 1.0


def _boot_prec_ci(eng, gold, seed, n=2000):
    rng = random.Random(seed)
    return V._boot_ci(eng, gold, V._precision, rng, n)


def _paired(engA, engB, gold, seed, n=2000):
    rng = random.Random(seed)
    return V._paired_delta_ci(engA, engB, gold, V._precision, rng, n)


def _score_set(name, items, my_engage, agent_labels: Dict[int, str], nlp, gate):
    """Return agreement + re-scored precision on adj-2 labels and consensus."""
    a2_engage = [agent_labels.get(c["idx"]) == "A" for c in items]
    a1_engage = my_engage
    kappa = cohen_kappa(a1_engage, a2_engage)
    agree = sum(1 for x, y in zip(a1_engage, a2_engage) if x == y) / len(items)

    # gate engage per item (recompute once)
    gate_engage, fireany = [], []
    for c in items:
        doc = nlp(c["sent"])
        sent = next((s for s in doc.sents if any(t.lemma_.lower() == c["lemma"] for t in s)),
                    list(doc.sents)[0])
        vt = V._locate_verb(sent, c["lemma"], c["patient"])
        gate_engage.append(gate.assess(sent, vt, c["affector"], c["patient"], c["context"],
                                       use_oblique=True)["engage"] if vt else False)
        fireany.append(True)

    def scores(gold):
        p = V._precision(gate_engage, gold); r = V._recall(gate_engage, gold)
        base = V._precision(fireany, gold)
        d = _paired(gate_engage, fireany, gold, 7)
        return {"gate_precision": round(p, 4), "gate_recall": round(r, 4), "base_rate": round(base, 4),
                "paired_delta_vs_base": [round(x, 4) for x in d]}

    gold_a1 = [e for e in a1_engage]
    gold_a2 = [e for e in a2_engage]
    cons_idx = [i for i in range(len(items)) if a1_engage[i] == a2_engage[i]]
    cons_gate = [gate_engage[i] for i in cons_idx]
    cons_fire = [True] * len(cons_idx)
    cons_gold = [a1_engage[i] for i in cons_idx]
    dp_cons = _paired(cons_gate, cons_fire, cons_gold, 9)
    cons = {"n": len(cons_idx),
            "gate_precision": round(V._precision(cons_gate, cons_gold), 4),
            "gate_recall": round(V._recall(cons_gate, cons_gold), 4),
            "base_rate": round(V._precision(cons_fire, cons_gold), 4),
            "paired_delta_vs_base": [round(x, 4) for x in dp_cons]}

    return {"set": name, "n": len(items), "kappa_binary_engage": round(kappa, 4),
            "raw_agreement": round(agree, 4),
            "adj1_positive": sum(a1_engage), "adj2_positive": sum(a2_engage),
            "scored_on_adj1_me": scores(gold_a1), "scored_on_adj2_agent": scores(gold_a2),
            "scored_on_consensus": cons}


def run(primary_labels_path: str, race_labels_path: str, nlp=None):
    import spacy
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")
    gate = LiteralnessGate(nlp=nlp)

    def _load(path):
        with open(path, encoding="ascii") as f:
            raw = json.load(f)
        return {int(k): str(v).strip().upper()[:1] for k, v in raw.items()}

    prim = load_primary()
    prim_my = [c["engage_gold"] for c in prim]
    race = H.load_gold()
    race_my = [c["engage_gold"] for c in race]

    out = {"primary": _score_set("primary_150", prim, prim_my, _load(primary_labels_path), nlp, gate),
           "race_heldout": _score_set("race_130", race, race_my, _load(race_labels_path), nlp, gate)}
    out["summary"] = (
        f"KAPPA (me vs independent agent): primary {out['primary']['kappa_binary_engage']}, "
        f"race {out['race_heldout']['kappa_binary_engage']}. Gate precision on the AGENT's labels: "
        f"primary {out['primary']['scored_on_adj2_agent']['gate_precision']} vs base "
        f"{out['primary']['scored_on_adj2_agent']['base_rate']} "
        f"(delta {out['primary']['scored_on_adj2_agent']['paired_delta_vs_base']}); on CONSENSUS: primary "
        f"{out['primary']['scored_on_consensus']['gate_precision']} vs base "
        f"{out['primary']['scored_on_consensus']['base_rate']}.")
    return out


if __name__ == "__main__":
    scratch = sys.argv[1] if len(sys.argv) > 1 else "."
    pp = os.path.join(scratch, "adj2_primary_labels.json")
    rp = os.path.join(scratch, "adj2_race_labels.json")
    m = run(pp, rp)
    outdir = os.path.join(_REPO, "data", "exp_literalness_gate_adjudicator_agreement_v1")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "metrics.json"), "w", encoding="ascii") as f:
        json.dump(m, f, indent=2)
    print(m["summary"])
    print(json.dumps({k: {"kappa": m[k]["kappa_binary_engage"],
                          "adj2_precision": m[k]["scored_on_adj2_agent"]["gate_precision"],
                          "adj2_base": m[k]["scored_on_adj2_agent"]["base_rate"],
                          "consensus_precision": m[k]["scored_on_consensus"]["gate_precision"],
                          "consensus_base": m[k]["scored_on_consensus"]["base_rate"]}
                      for k in ("primary", "race_heldout")}, indent=2))
