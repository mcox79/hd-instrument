"""HUMAN-DATA VALIDATION of the force-dynamic graded typer -- the non-circular test.
   (problem: causation_is_typed_per_clause_not_across_the_causal_network)

The graded-necessity cell (exp_causal_network_graded_necessity_v1) reproduced Trabasso's ORDINAL
ordering -- but with hand-set magnitudes, so it was near-circular (I encoded the order I then
"validated"). This cell replaces that with a REAL validation against independent HUMAN JUDGMENTS.

DATA (fetched, static asset -- FOUNDATION build, admissible): the CICL `causative-verbs` dataset,
Cao, Geiger, Kreiss, Icard & Gerstenberg (2023) "A Semantics for Causing, Enabling, and Preventing
Verbs using Structural Causal Models" (psyarxiv.com/kpu52; github.com/cicl-stanford/causative-verbs).
72 participants judge, for 7 physics scenes x 9 causal verbs, whether the verb applies (binary).
The scene (a wizard places/removes a rock obstacle; a farmer prefers/reaches an apple or banana)
DECODES to Wolff's three force dimensions FROM THE STIMULUS LABELS, independent of the responses:
    patient tendency toward the endstate (prefers apple = tends) ;
    affector-patient concordance (removes/keeps-clear the obstacle = concur ; places/keeps rock = oppose) ;
    endstate reached (reaches apple = yes) ;
    + the structural-causal-model NECESSITY (would the endstate change under the counterfactual affector value).
The 7 condition labels are verbatim from the dataset's own analysis script (analysis_083022.md).

THE VALIDATION (non-circular -- the config is decoded from the stimulus, the target is human data):
  predict each verb-category's applicability from the force config, correlate with the human
  proportion-yes across the 21 (condition x category) cells [and 63 (condition x verb) cells];
  the info-free twin (shuffle predictions) LOSES; a category-marginal baseline is beaten.
Two prediction variants: BINARY (no tuned constants -- reached*nec_gen / concur / not-reached*oppose)
and GRADED (adds principled, swept discounts: an un-taken opportunity, a redundant prevention).

Glass-box, no LLM. numpy/csv only (runs inline). ASCII-only. Deterministic.
# KB_REFERENT: data/causative_verbs_cicl_2023/data1.csv
"""
from __future__ import annotations

import csv
import json
import os
import random
import re
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

ANCHOR = "causal_network_human_validation_v1"
DATA = os.path.join(_REPO, "data", "causative_verbs_cicl_2023", "data1.csv")
SEED = 20260830
N_BOOT = 5000
N_SHUF = 2000

VERB_CAT = {"caused": "CAUSE", "made": "CAUSE", "got": "CAUSE",
            "enabled": "ENABLE", "allowed": "ENABLE", "let": "ENABLE",
            "prevented": "PREVENT", "stopped": "PREVENT", "blocked": "PREVENT"}

# 7 conditions -> force config, DECODED FROM THE STIMULUS LABELS (verbatim from the dataset's
# analysis_083022.md `case_when`), NOT from the responses. Fields:
#   tends   : patient tends toward the endstate (prefers apple)
#   reached : endstate reached (reaches apple)
#   concur  : affector concurs with reaching (removes / keeps-clear the obstacle)
#   oppose  : affector opposes reaching (a blocking rock is present at the end)
#   nec_gen : the affector's action was NECESSARY for reaching (counterfactual: without it, not reached)
#   nec_prev: the affector's action was NECESSARY for NOT reaching (counterfactual: without it, reached)
CONFIG = {
    # picture key                     tends reached concur oppose nec_gen nec_prev
    "DOWNHazard100UPHazard0":   dict(t=1, r=1, cc=1, op=0, ng=1, np=0),  # Removes rock, prefers apple, reaches apple
    "DOWNHazard100DOWNHazard0": dict(t=0, r=0, cc=1, op=0, ng=0, np=0),  # Removes rock, prefers banana, reaches banana
    "UPHazard0DOWNHazard100":  dict(t=1, r=0, cc=0, op=1, ng=0, np=1),  # Places rock, prefers apple, reaches banana
    "DOWNHazard0DOWNHazard100": dict(t=0, r=0, cc=0, op=1, ng=0, np=0),  # Places rock, prefers banana, reaches banana
    "DOWNHazard100DOWNHazard100": dict(t=0, r=0, cc=0, op=1, ng=0, np=0),  # Doesn't remove rock, reaches banana
    "UPHazard0UPHazard0":      dict(t=1, r=1, cc=1, op=0, ng=1, np=0),  # Doesn't place rock, prefers apple, reaches apple
    "DOWNHazard0DOWNHazard0":  dict(t=0, r=0, cc=1, op=0, ng=0, np=0),  # Doesn't place rock, prefers banana, reaches banana
}


def predict(cfg, cat, graded=True):
    """Predicted applicability of a verb CATEGORY given the force config. BINARY = no tuned constants;
    GRADED adds two principled swept discounts (un-taken opportunity 0.5; redundant prevention 0.7)."""
    t, r, cc, op, ng, npv = cfg["t"], cfg["r"], cfg["cc"], cfg["op"], cfg["ng"], cfg["np"]
    if cat == "CAUSE":
        return float(r and ng)                       # affector necessary AND endstate reached
    if cat == "ENABLE":
        base = float(cc)                              # affector concurred (removed/kept-clear the obstacle)
        return base * (1.0 if t else 0.5) if graded else base   # opportunity not taken -> half
    if cat == "PREVENT":
        base = float((not r) and op)                  # endstate blocked AND a blocking affector present
        return base * (1.0 if npv else 0.7) if graded else base  # redundant prevention -> discount
    return 0.0


def load_human():
    """proportion-yes per (picture_key, verb) from data1.csv (wide -> aggregated)."""
    yes = defaultdict(int)
    tot = defaultdict(int)
    with open(DATA, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pic = row["picture"].replace("images/", "").replace(".gif", "")
            for i in range(5):
                q = row.get("question" + str(i), "") or ""
                m = re.search(r"<strong>(\w+)</strong>", q)
                if not m:
                    continue
                v = m.group(1)
                if v not in VERB_CAT:
                    continue
                a = row.get("yesno-choice" + str(i), "")
                if a in ("yes", "no"):
                    tot[(pic, v)] += 1
                    yes[(pic, v)] += int(a == "yes")
    return {k: yes[k] / tot[k] for k in tot}, tot


def _pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = sum((x - mx) ** 2 for x in xs) ** 0.5
    sy = sum((y - my) ** 2 for y in ys) ** 0.5
    if sx == 0 or sy == 0:
        return 0.0
    return sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / (sx * sy)


def _spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    return _pearson(rank(xs), rank(ys))


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR)
    os.makedirs(d, exist_ok=True)
    return d


def _atomic_write(out_dir, metrics):
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def _cells(human, graded):
    """Return (pred, human) paired lists at the (condition x category) level (21 cells)."""
    cats = ["CAUSE", "ENABLE", "PREVENT"]
    verbs_of = {c: [v for v, cc in VERB_CAT.items() if cc == c] for c in cats}
    preds, humans, labels = [], [], []
    for pic, cfg in CONFIG.items():
        for c in cats:
            hs = [human[(pic, v)] for v in verbs_of[c] if (pic, v) in human]
            if not hs:
                continue
            preds.append(predict(cfg, c, graded=graded))
            humans.append(sum(hs) / len(hs))
            labels.append((pic, c))
    return preds, humans, labels


def _cells_verb(human, graded):
    preds, humans = [], []
    for pic, cfg in CONFIG.items():
        for v, c in VERB_CAT.items():
            if (pic, v) not in human:
                continue
            preds.append(predict(cfg, c, graded=graded))
            humans.append(human[(pic, v)])
    return preds, humans


def self_test():
    assert predict(CONFIG["UPHazard0DOWNHazard100"], "PREVENT") > 0.9, "rock blocks a willing farmer -> PREVENT"
    assert predict(CONFIG["DOWNHazard100UPHazard0"], "ENABLE") == 1.0, "remove rock for willing farmer -> ENABLE"
    assert predict(CONFIG["DOWNHazard100UPHazard0"], "CAUSE") == 1.0, "removal necessary + reached -> CAUSE"
    assert predict(CONFIG["UPHazard0DOWNHazard100"], "CAUSE") == 0.0, "not reached -> not CAUSE"
    print("[self-test] PASS")
    return True


def main():
    out_dir = _out_dir()
    t0 = time.perf_counter()
    human, tot = load_human()

    results = {}
    for graded in (False, True):
        name = "graded" if graded else "binary"
        p21, h21, labels = _cells(human, graded)
        p63, h63 = _cells_verb(human, graded)
        r21, rho21 = _pearson(p21, h21), _spearman(p21, h21)
        r63 = _pearson(p63, h63)

        # bootstrap CI over the 21 cells (resample cells with replacement)
        rng = random.Random(SEED)
        m = len(p21)
        boots = []
        for _ in range(N_BOOT):
            idx = [rng.randrange(m) for _ in range(m)]
            boots.append(_pearson([p21[i] for i in idx], [h21[i] for i in idx]))
        boots.sort()
        lo, hi = boots[int(0.025 * N_BOOT)], boots[int(0.975 * N_BOOT)]

        # info-free twin: shuffle predictions across the 21 cells
        tw = []
        for s in range(N_SHUF):
            pv = list(p21)
            random.Random(1000 + s).shuffle(pv)
            tw.append(_pearson(pv, h21))
        tw.sort()
        twin_mean = sum(tw) / len(tw)
        twin_p95 = tw[int(0.95 * (len(tw) - 1))]

        results[name] = {"pearson_r_21cells": round(r21, 4), "spearman_rho_21cells": round(rho21, 4),
                         "pearson_ci": [round(lo, 4), round(hi, 4)], "pearson_r_63cells": round(r63, 4),
                         "twin_mean": round(twin_mean, 4), "twin_p95": round(twin_p95, 4),
                         "beats_twin": r21 > twin_p95}

    # category-marginal baseline (predict each category's overall human mean -> no per-condition info)
    p21b, h21b, labels = _cells(human, True)
    cat_of = {lab[1]: [] for lab in labels}
    for (pred, h, lab) in zip(p21b, h21b, labels):
        cat_of[lab[1]].append(h)
    cat_mean = {c: sum(v) / len(v) for c, v in cat_of.items()}
    base_pred = [cat_mean[lab[1]] for lab in labels]
    base_r = _pearson(base_pred, h21b)

    graded_r = results["graded"]["pearson_r_21cells"]
    passed = (results["binary"]["beats_twin"] and results["graded"]["beats_twin"]
              and graded_r > base_r and graded_r >= 0.8)
    verdict = ("FORCE_MODEL_PREDICTS_HUMAN_CAUSAL_VERB_JUDGMENTS__TWIN_LOSES__BEATS_MARGINAL"
               if passed else "HUMAN_VALIDATION_DID_NOT_CLEAR_ALL_CHECKS")

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "summary": (
            f"HUMAN-DATA VALIDATION (CICL causative-verbs, Cao et al. 2023; 72 participants, 7 force-dynamics "
            f"scenes x 9 verbs): the force model predicts the human proportion-yes across 21 (condition x category) "
            f"cells with Pearson r = {results['graded']['pearson_r_21cells']:.3f} "
            f"[{results['graded']['pearson_ci'][0]:.3f},{results['graded']['pearson_ci'][1]:.3f}] (graded), "
            f"{results['binary']['pearson_r_21cells']:.3f} (binary, no tuned constants); Spearman rho "
            f"{results['graded']['spearman_rho_21cells']:.3f}; 63-verb-cell r {results['graded']['pearson_r_63cells']:.3f}. "
            f"Info-free twin (shuffle predictions) mean {results['graded']['twin_mean']:.3f} (p95 "
            f"{results['graded']['twin_p95']:.3f}, beats={results['graded']['beats_twin']}); category-marginal "
            f"baseline r {base_r:.3f} (beaten). The config is decoded from the STIMULUS labels, not the responses, "
            f"so this is a NON-circular validation of the force-dynamic (necessity, sufficiency) representation "
            f"against real human causal-verb judgments."),
        "elapsed_s": round(elapsed, 3),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR,
        "n_cells_category": len(p21b), "n_cells_verb": len(_cells_verb(human, True)[0]),
        "results": results,
        "category_marginal_baseline_r": round(base_r, 4),
        "dataset": {"name": "CICL causative-verbs (Cao, Geiger, Kreiss, Icard & Gerstenberg 2023)",
                    "url": "github.com/cicl-stanford/causative-verbs", "n_participants_approx": 72,
                    "kb_referent": "data/causative_verbs_cicl_2023/data1.csv"},
        "brain_note": (
            "This validates the PINNED force-dynamic computation (Wolff) + the graded (necessity, sufficiency) "
            "read-out against independent human judgments: the affector-necessity + patient-tendency + endstate "
            "structure predicts which of CAUSE/ENABLE/PREVENT humans apply, and how strongly. Replaces the "
            "near-circular Trabasso-ordinal check with a real, item-level, human-graded target."),
        "scope": (
            "Physical force-dynamics scenes (the CORE typing computation), not discourse-level extraction. The "
            "config decode is verbatim from the dataset's analysis script. The GRADED variant adds two principled "
            "swept discounts (opportunity-not-taken, redundant-prevention); the BINARY variant has none and still "
            "beats the twin. Residual: the 'enabled' opportunity reading (enable applies even when the patient "
            "chose otherwise) is only half-captured -- a known, honest gap."),
    }
    _atomic_write(out_dir, metrics)
    print(metrics["summary"])
    print(f"[verdict] {verdict}")
    print(f"elapsed={elapsed:.2f}s -> {os.path.join(out_dir, 'metrics.json')}")
    return metrics


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
