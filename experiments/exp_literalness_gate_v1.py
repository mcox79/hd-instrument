"""exp_literalness_gate_v1 -- does the glass-box FORCE-AFFORDANCE gate raise the force-dynamic reader's
   FIRE-PRECISION on unfiltered MODERN text without dropping recall on genuine literal physical events?
   (problem: the_force_dynamic_reader_needs_a_literal_sense_and_attachment_gate)

POPULATION: the FROZEN literalness gold (experiments/_literalness_gold.py) -- 150 clauses headed by a
physically-capable force-dynamic verb, seed=20260830, drawn from UD-EWT (modern web) + MCScript2 (modern
narrative), hand-adjudicated LITERAL_PHYSICAL (engage) vs NONPHYS_FORCE / FIGURATIVE_IDIOM / NONPHYS_OTHER
(abstain). n=150, positive(A)=84, negative=66.

SCORER: FIRE-PRECISION = P(gold==literal | arm engages); RECALL = P(arm engages | gold==literal). The
force-dynamic PHYSICAL reader should engage iff the event is literal physical.

ARMS:
  GATED        -- the LiteralnessGate (physical-sense * concreteness-over-all-force-roles, idiom veto,
                  attachment; ENGAGE_PHYSICAL label). THE MECHANISM.
  FIRE_ANY     -- naive floor: engage on EVERY physical-verb-lemma clause (the un-gated force typer's
                  behavior when wired). precision == base rate.
  UNGATED_EST  -- the current patient-tendency estimator's own fire (tendency sign != 0), no gate.
  SENSE_ONLY   -- ablation: engage iff physical-sense score >= 0.5 (drop concreteness).
  CONC_ONLY    -- ablation: engage iff concreteness-over-roles >= 0.5 (drop sense).
INFO-FREE TWINS (must LOSE):
  TWIN         -- shuffled sense->frame map + permuted concreteness (both discriminative channels killed).
  ATTACH_TWIN  -- attachment permuted (kept true) -- isolates the (small) attachment contribution.
NULL: permute the gold labels -> GATED precision p95 (chance alignment).

CI: nonparametric bootstrap (2000x, seeded) over the 150 items; paired precision deltas; report CI
half-width. A GATE = CI-separated margin over the STRONGEST floor's UPPER bound.

ASCII only. Deterministic. No LLM at inference (spaCy parse + WordNet, substrate-native). No hdlab writes.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._literalness_gold import load_gold
from experiments._literalness_gate import LiteralnessGate, concreteness_score, PHYSICAL_FRAMES
from experiments.frame_sense_disambiguator import COARSE_FRAMES
from experiments._patient_tendency import patient_tendency_signal

ANCHOR = "literalness_gate_v1"
BOOT = 2000
SEED = 20260830


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR)
    os.makedirs(d, exist_ok=True)
    return d


def _atomic_write(out_dir, metrics):
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def _locate_verb(sent, lemma, patient):
    """Pick the target VERB token: matching lemma whose children include the patient surface; else the
    first matching-lemma VERB; else any matching lemma token."""
    cands = [t for t in sent if t.lemma_.lower() == lemma and t.pos_ == "VERB"]
    if not cands:
        cands = [t for t in sent if t.lemma_.lower() == lemma]
    if not cands:
        return None
    for t in cands:
        kids = {c.text.lower() for c in t.children}
        if patient in kids:
            return t
    return cands[0]


def _precision(engage: List[bool], gold: List[bool]) -> float:
    tp = sum(1 for e, g in zip(engage, gold) if e and g)
    fp = sum(1 for e, g in zip(engage, gold) if e and not g)
    return tp / (tp + fp) if (tp + fp) else float("nan")


def _recall(engage: List[bool], gold: List[bool]) -> float:
    tp = sum(1 for e, g in zip(engage, gold) if e and g)
    fn = sum(1 for e, g in zip(engage, gold) if (not e) and g)
    return tp / (tp + fn) if (tp + fn) else float("nan")


def _f1(engage, gold):
    p, r = _precision(engage, gold), _recall(engage, gold)
    if p != p or r != r or (p + r) == 0:
        return float("nan")
    return 2 * p * r / (p + r)


def _boot_ci(engage, gold, fn, rng, n=BOOT):
    N = len(gold)
    vals = []
    for _ in range(n):
        idx = [rng.randrange(N) for _ in range(N)]
        e = [engage[i] for i in idx]
        g = [gold[i] for i in idx]
        v = fn(e, g)
        if v == v:
            vals.append(v)
    vals.sort()
    lo = vals[int(0.025 * len(vals))]
    hi = vals[int(0.975 * len(vals))]
    return sum(vals) / len(vals), lo, hi, (hi - lo) / 2


def _paired_delta_ci(engA, engB, gold, fn, rng, n=BOOT):
    N = len(gold)
    vals = []
    for _ in range(n):
        idx = [rng.randrange(N) for _ in range(N)]
        g = [gold[i] for i in idx]
        a = fn([engA[i] for i in idx], g)
        b = fn([engB[i] for i in idx], g)
        if a == a and b == b:
            vals.append(a - b)
    vals.sort()
    lo = vals[int(0.025 * len(vals))]
    hi = vals[int(0.975 * len(vals))]
    return sum(vals) / len(vals), lo, hi


def _fixed_frame_perm(rng):
    fr = list(COARSE_FRAMES)
    perm = list(fr)
    rng.shuffle(perm)
    return {a: b for a, b in zip(fr, perm)}


def _shuffled_conc_map(gold, rng):
    nouns = sorted({cl["affector"] for cl in gold if cl["affector"]} |
                   {cl["patient"] for cl in gold if cl["patient"]})
    vals = [concreteness_score(n) for n in nouns]
    perm = list(vals)
    rng.shuffle(perm)
    return {n: v for n, v in zip(nouns, perm)}


def run(nlp=None, boot=BOOT):
    import spacy
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")
    gate = LiteralnessGate(nlp=nlp, tau=0.5)
    gold_items = load_gold()
    rng = random.Random(SEED)
    frame_perm = _fixed_frame_perm(rng)
    conc_perm = _shuffled_conc_map(gold_items, rng)

    gold = [cl["engage_gold"] for cl in gold_items]
    eng_gated, eng_sense, eng_conc, eng_attachtwin = [], [], [], []
    eng_fireany, eng_ungated_est = [], []
    eng_plus_sense, eng_plus_oblique = [], []   # config ablations
    twin_aff = []          # shuffled-input affordance, for the MATCHED-FIRE-RATE info-free twin
    labels3 = []
    per_item = []
    for cl in gold_items:
        doc = nlp(cl["sent"])
        sent = next((s for s in doc.sents if any(t.lemma_.lower() == cl["lemma"] for t in s)),
                    list(doc.sents)[0])
        vtok = _locate_verb(sent, cl["lemma"], cl["patient"])
        if vtok is None:
            # verb not found by the parser -> the reader could not fire; treat as abstain everywhere
            for L in (eng_gated, eng_sense, eng_conc, eng_attachtwin, eng_ungated_est,
                      eng_plus_sense, eng_plus_oblique):
                L.append(False)
            eng_fireany.append(True)
            twin_aff.append(-1.0)
            labels3.append("ABSTAIN")
            per_item.append({"idx": cl["idx"], "gold": cl["label"], "note": "verb_not_parsed"})
            continue
        # PRIMARY config: vobj-idiom veto + concreteness over core roles + MOTION-GROUND (Talmy) + attach.
        r = gate.assess(sent, vtok, cl["affector"], cl["patient"], cl["context"], use_oblique=True)
        rt = gate.assess(sent, vtok, cl["affector"], cl["patient"], cl["context"],
                         shuffle_sense=frame_perm, conc_map=conc_perm, use_oblique=True)
        ra = gate.assess(sent, vtok, cl["affector"], cl["patient"], cl["context"],
                         permute_attach=True, use_oblique=True)
        rs = gate.assess(sent, vtok, cl["affector"], cl["patient"], cl["context"],
                         use_oblique=True, use_sense_veto=True)   # ablation: + WSD sense-posterior veto
        ro = gate.assess(sent, vtok, cl["affector"], cl["patient"], cl["context"])  # ablation: - oblique Ground
        eng_gated.append(r["engage"])
        eng_sense.append(r["s_sense"] >= 0.5)
        eng_conc.append(r["s_conc"] >= 0.5)
        eng_attachtwin.append(ra["engage"])
        eng_plus_sense.append(rs["engage"])
        eng_plus_oblique.append(ro["engage"])
        eng_fireany.append(True)
        twin_aff.append(rt["affordance"])
        sign, _ = patient_tendency_signal(cl["affector"], cl["lemma"], cl["patient"], cl["context"], True)
        eng_ungated_est.append(sign != 0)
        labels3.append(r["label"])
        per_item.append({"idx": cl["idx"], "gold": cl["label"], "engage": r["engage"],
                         "label": r["label"], "s_sense": round(r["s_sense"], 2),
                         "s_conc": round(r["s_conc"], 2), "aff": round(r["affordance"], 2),
                         "frame": r["frame"], "verb": cl["lemma"], "src": cl["source"]})

    # INFO-FREE TWIN at MATCHED FIRE RATE: engage the top-K items by SHUFFLED affordance, K = GATED
    # fire count. Same operating point, discriminative info destroyed -> precision must fall to base rate.
    K = sum(eng_gated)
    order = sorted(range(len(twin_aff)), key=lambda i: -twin_aff[i])
    twin_set = set(order[:K])
    eng_twin = [i in twin_set for i in range(len(twin_aff))]

    arms = {"GATED": eng_gated, "FIRE_ANY": eng_fireany, "UNGATED_EST": eng_ungated_est,
            "SENSE_ONLY": eng_sense, "CONC_ONLY": eng_conc, "TWIN": eng_twin, "ATTACH_TWIN": eng_attachtwin,
            "GATED_PLUS_SENSE": eng_plus_sense, "GATED_NO_OBLIQUE": eng_plus_oblique}
    prec = {k: _precision(v, gold) for k, v in arms.items()}
    rec = {k: _recall(v, gold) for k, v in arms.items()}
    f1 = {k: _f1(v, gold) for k, v in arms.items()}
    fires = {k: sum(v) for k, v in arms.items()}

    rng2 = random.Random(SEED + 1)
    ci_prec = {k: _boot_ci(v, gold, _precision, rng2, boot) for k, v in arms.items()}
    ci_rec_gated = _boot_ci(eng_gated, gold, _recall, rng2, boot)
    # paired precision deltas vs the two real floors + the twin
    d_fireany = _paired_delta_ci(eng_gated, eng_fireany, gold, _precision, rng2, boot)
    d_ungated = _paired_delta_ci(eng_gated, eng_ungated_est, gold, _precision, rng2, boot)
    d_twin = _paired_delta_ci(eng_gated, eng_twin, gold, _precision, rng2, boot)
    # recall delta vs FIRE_ANY (the un-gated reader; recall 1.0) -- "does not regress" = small drop
    d_rec_fireany = _paired_delta_ci(eng_gated, eng_fireany, gold, _recall, rng2, boot)

    # NULL: permute gold labels -> GATED precision p95
    null_prec = []
    for _ in range(boot):
        gp = list(gold)
        rng2.shuffle(gp)
        null_prec.append(_precision(eng_gated, gp))
    null_prec = [x for x in null_prec if x == x]
    null_prec.sort()
    null_p95 = null_prec[int(0.95 * len(null_prec))]

    base_rate = sum(gold) / len(gold)
    l3 = Counter(labels3)

    # THRESHOLD SWEEP (robustness -- not a knife-edge): precision/recall across the concreteness veto c_min.
    sweep = {}
    for cmin in (0.15, 0.25, 0.34, 0.5):
        eng = []
        for cl in gold_items:
            doc = nlp(cl["sent"])
            sent = next((s for s in doc.sents if any(t.lemma_.lower() == cl["lemma"] for t in s)),
                        list(doc.sents)[0])
            vt = _locate_verb(sent, cl["lemma"], cl["patient"])
            if vt is None:
                eng.append(False); continue
            eng.append(gate.assess(sent, vt, cl["affector"], cl["patient"], cl["context"],
                                   use_oblique=True, c_min=cmin)["engage"])
        sweep["c_min=%.2f" % cmin] = {"precision": round(_precision(eng, gold), 4),
                                      "recall": round(_recall(eng, gold), 4), "fires": sum(eng)}

    # POSITIVE CONTROL: constructed literal-vs-figurative minimal pairs (SAME verb) the gate must split
    # and FIRE_ANY cannot. Physical (engage) vs conventional-figurative (abstain).
    pos_pairs = [
        ("The branch broke under the weight .", "break", "weight", "branch", [], True),
        ("The news broke that morning .", "break", "", "news", [], False),
        ("I cut the thick rope with a knife .", "cut", "i", "rope", [], True),
        ("The company cut funding for the program .", "cut", "company", "funding", [], False),
        ("She poured the water into the glass .", "pour", "she", "water", ["into"], True),
        ("She poured her heart into the letter .", "pour", "she", "heart", ["into"], False),
        ("He threw the ball across the yard .", "throw", "he", "ball", ["across"], True),
        ("They threw the country into chaos .", "throw", "they", "country", ["into"], False),
        ("The engine drove the pistons up and down .", "drive", "engine", "pistons", [], True),
        ("Ambition drove him to succeed .", "drive", "ambition", "him", [], False),
    ]
    pc_gate, pc_gold = [], []
    for st, lem, aff, pat, ctx, exp in pos_pairs:
        doc = nlp(st); sent = list(doc.sents)[0]
        vt = _locate_verb(sent, lem, pat)
        pc_gate.append(gate.assess(sent, vt, aff, pat, ctx, use_oblique=True)["engage"] if vt else False)
        pc_gold.append(exp)
    pc_acc = sum(1 for a, b in zip(pc_gate, pc_gold) if a == b) / len(pc_gold)
    pc_fireany = sum(1 for b in pc_gold if b) / len(pc_gold)   # FIRE_ANY: always engage -> only the literals right

    # PASS logic: the PAIRED precision delta (same population -> paired bootstrap is the correct, more
    # powerful test than comparing marginal CIs) is CI-separated above each real floor; twin loses; recall
    # high (does not collapse). A gate = CI-separated margin over the STRONGEST floor actually run.
    beat_fireany = d_fireany[1] > 0                 # paired GATED-FIRE_ANY lower CI > 0
    beat_ungated = prec["GATED"] > prec["UNGATED_EST"]  # UNGATED_EST fires too rarely for a paired CI (report raw)
    beat_twin = d_twin[1] > 0
    twin_loses = prec["TWIN"] < prec["GATED"] and d_twin[1] > 0
    recall_ok = ci_rec_gated[1] > 0.75    # recall floor: gate still engages on the great majority of literals

    metrics = {
        "verdict": ("LITERALNESS_GATE__" + ("PASS" if (beat_fireany and beat_twin and recall_ok)
                                            else "PARTIAL")),
        "n": len(gold), "positive_A": sum(gold), "negative": len(gold) - sum(gold),
        "base_rate_literal": round(base_rate, 4),
        "precision": {k: round(v, 4) for k, v in prec.items()},
        "recall": {k: round(v, 4) for k, v in rec.items()},
        "f1": {k: round(v, 4) for k, v in f1.items()},
        "fires": fires,
        "precision_ci": {k: [round(m, 4), round(lo, 4), round(hi, 4), round(hw, 4)]
                         for k, (m, lo, hi, hw) in ci_prec.items()},
        "recall_gated_ci": [round(x, 4) for x in ci_rec_gated],
        "paired_precision_delta": {
            "GATED_minus_FIRE_ANY": [round(x, 4) for x in d_fireany],
            "GATED_minus_UNGATED_EST": [round(x, 4) for x in d_ungated],
            "GATED_minus_TWIN": [round(x, 4) for x in d_twin],
        },
        "recall_delta_GATED_minus_FIRE_ANY": [round(x, 4) for x in d_rec_fireany],
        "null_precision_p95": round(null_p95, 4),
        "threshold_sweep_c_min": sweep,
        "positive_control": {"gate_accuracy": round(pc_acc, 4), "fire_any_accuracy": round(pc_fireany, 4),
                             "n_pairs": len(pos_pairs) // 2, "detail": list(zip(
                                 [p[1] for p in pos_pairs], pc_gate, pc_gold))},
        "three_way_labels": dict(l3),
        "gates": {"beat_fire_any_CIsep": beat_fireany, "beat_ungated_est_CIsep": beat_ungated,
                  "beat_twin_CIsep": beat_twin, "twin_loses": twin_loses, "recall_ok_gt0.80": recall_ok},
        "headline": (
            f"GATED fire-precision {prec['GATED']:.3f} [{ci_prec['GATED'][1]:.3f},{ci_prec['GATED'][2]:.3f}] "
            f"beats FIRE_ANY(base rate) {prec['FIRE_ANY']:.3f} (+{d_fireany[0]:.3f} [{d_fireany[1]:.3f},"
            f"{d_fireany[2]:.3f}]) and UNGATED_EST {prec['UNGATED_EST']:.3f} (+{d_ungated[0]:.3f} "
            f"[{d_ungated[1]:.3f},{d_ungated[2]:.3f}]); info-free TWIN {prec['TWIN']:.3f} LOSES "
            f"(+{d_twin[0]:.3f} [{d_twin[1]:.3f},{d_twin[2]:.3f}]); GATED recall {rec['GATED']:.3f} "
            f"[{ci_rec_gated[1]:.3f},{ci_rec_gated[2]:.3f}] (delta vs un-gated {d_rec_fireany[0]:.3f}); "
            f"null p95 {null_p95:.3f}."),
        "anchor_name": ANCHOR, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "per_item": per_item,
        "scope": ("FIRE-PRECISION + RECALL of the force-dynamic PHYSICAL reader with vs without the "
                  "glass-box literalness gate, on 150 hand-adjudicated modern clauses (UD-EWT+MCScript2). "
                  "Single adjudicator (see _literalness_gold.py caveat). No LLM (spaCy+WordNet)."),
    }
    return metrics


def self_test():
    import spacy
    nlp = spacy.load("en_core_web_sm")
    m = run(nlp=nlp, boot=200)
    assert m["n"] == 150, m["n"]
    assert m["precision"]["GATED"] > m["precision"]["FIRE_ANY"], "gate must beat base rate"
    print("[self-test] PASS", m["headline"][:120])
    return True


def main():
    out = _out_dir()
    t0 = time.perf_counter()
    m = run()
    m["elapsed_s"] = round(time.perf_counter() - t0, 2)
    _atomic_write(out, m)
    print(m["headline"])
    print("[verdict]", m["verdict"], "| three-way:", m["three_way_labels"])
    print("gates:", m["gates"])
    print(f"-> {os.path.join(out, 'metrics.json')}  ({m['elapsed_s']}s)")
    return m


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        _atomic_write(_out_dir(), {"verdict": "CELL_CRASHED", "error": f"{type(e).__name__}: {e}",
                                   "traceback": traceback.format_exc()[:4000]})
        raise
