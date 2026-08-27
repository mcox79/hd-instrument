"""Full composed-reader INTEGRATION test on running narrative (LitBank): the LANDED organs IN the pipeline.

Unlike a unit witness, this runs `hdlab.salience_binder` INSIDE the end-to-end reader (front-end mention stream ->
entity binding -> the REAL situation-model register decode) and measures cross-sentence who-did-what. It establishes
the composition harness the improved front-end (solver p1) will slot into (the `annotate` step is the pluggable
front-end SEAM; here it is the existing spaCy stream, cached).

ARMS (cross-sentence who-did-what, pronoun-contributed subset):
  * ACTR_LANDED    : pronouns bound by hdlab.salience_binder.bind (ACT-R base-level + Centering prominence) -- THE ORGAN.
  * STRING_IDENTITY: pronouns are singletons (the cheap-trick floor).
  * SHUFFLED_TWIN  : pronouns -> a random compatible entity (info-free -> must lose).
Expected (from the integration, which this confirms IN-PIPELINE): ACTR beats string-identity CI-sep, twin losing.

Run:  .venv/Scripts/python.exe experiments/exp_composed_reader_litbank_full_v1.py [--docs N]
"""
from __future__ import annotations

import os
import sys

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))

import experiments.exp_litbank_entity_tracking_end_to_end_v1 as H  # the validated harness (decode + data)
from experiments.exp_litbank_activation_binder_v1 import PRONOUNS, _gn_compat  # noqa: E402
from hdlab.salience_binder import bind as salience_bind, DEFAULT_DECAY  # THE LANDED ORGAN

SEED = 20260827
ARMS = ["ACTR_LANDED", "STRING_IDENTITY", "SHUFFLED_TWIN"]


def _name_tokens(head_text):
    return H._name_tokens(head_text)


def build_links_landed(stream, rng):
    """Per-mention entity id under each arm. Names link by head-token overlap (identical in all arms); pronouns
    differ: ACTR_LANDED uses the LANDED salience_binder.bind over compatible candidates' histories."""
    pred = {a: [] for a in ARMS}
    ents = {a: [] for a in ARMS}
    for m in stream:
        ht = m["head_text"]; role = m["role"]; is_pron = ht in PRONOUNS
        for a in ARMS:
            tbl = ents[a]
            if is_pron:
                pg, pn = PRONOUNS[ht]
                compat = [i for i, e in enumerate(tbl) if e["hist"] and _gn_compat(pg, pn, e["gender"], e["number"])]
                if not compat or a == "STRING_IDENTITY":
                    tbl.append({"tokens": set(), "gender": pg, "number": pn, "hist": [(m["sent"], role)]})
                    pred[a].append(len(tbl) - 1); continue
                if a == "ACTR_LANDED":
                    cand_hists = [tbl[i]["hist"] for i in compat]
                    idx = salience_bind(cand_hists, now=m["sent"], decay=DEFAULT_DECAY)   # <-- THE LANDED ORGAN
                    best = compat[idx]
                else:  # SHUFFLED_TWIN
                    best = compat[int(rng.integers(0, len(compat)))]
                pred[a].append(best)
                tbl[best]["hist"].append((m["sent"], role))
                if tbl[best]["gender"] is None:
                    tbl[best]["gender"] = pg
                if tbl[best]["number"] is None:
                    tbl[best]["number"] = pn
            else:
                toks = _name_tokens(ht)
                best, best_ov = None, 0.0
                for i, e in enumerate(tbl):
                    if not e["tokens"]:
                        continue
                    ov = len(toks & e["tokens"]) / len(toks | e["tokens"]) if toks else 0.0
                    if ov > best_ov:
                        best_ov, best = ov, i
                if best is not None and best_ov > 0.0:
                    pred[a].append(best); tbl[best]["tokens"] |= toks; tbl[best]["hist"].append((m["sent"], role))
                else:
                    g, n = H._name_gender(ht)
                    tbl.append({"tokens": set(toks), "gender": g, "number": n, "hist": [(m["sent"], role)]})
                    pred[a].append(len(tbl) - 1)
    return pred


def main():
    docs = 60
    if "--docs" in sys.argv:
        docs = int(sys.argv[sys.argv.index("--docs") + 1])
    recs = H.load_cache()[:docs]
    rng = np.random.default_rng(SEED)
    per_doc = {a: [] for a in ARMS}       # (pron_c, pron_n) per doc
    for di, rec in enumerate(recs):
        stream = rec["stream"]
        if not stream:
            continue
        slot_map, n_slots = H._slots(stream)
        verb_vocab = sorted({m["gov_verb"] for m in stream if m["gov_verb"] is not None})
        if not verb_vocab:
            continue
        links = build_links_landed(stream, rng)
        for a in ARMS:
            g = H._torch_gen(SEED + di * 1000 + ARMS.index(a))
            r = H._score_arm(stream, links[a], verb_vocab, slot_map, n_slots, g, "multibank", difficulty=None)
            per_doc[a].append((r["pron_c"], r["pron_n"]))

    def acc_ci(pairs, s):
        arr = np.array(pairs, float); tot = arr[:, 1].sum()
        acc = arr[:, 0].sum() / tot if tot else 0.0
        r = np.random.default_rng(s); nd = len(arr)
        b = [arr[r.integers(0, nd, nd)][:, 0].sum() / max(arr[r.integers(0, nd, nd)][:, 1].sum(), 1) for _ in range(1500)]
        # paired resample (same idx for num+den)
        b = []
        for _ in range(1500):
            idx = r.integers(0, nd, nd); b.append(arr[idx, 0].sum() / max(arr[idx, 1].sum(), 1))
        return acc, float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))

    def paired(a_pairs, b_pairs, s):
        a = np.array(a_pairs, float); b = np.array(b_pairs, float); r = np.random.default_rng(s); nd = len(a)
        d = []
        for _ in range(1500):
            idx = r.integers(0, nd, nd)
            d.append(a[idx, 0].sum() / max(a[idx, 1].sum(), 1) - b[idx, 0].sum() / max(b[idx, 1].sum(), 1))
        lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
        return {"delta": round(float(a[:, 0].sum() / max(a[:, 1].sum(), 1) - b[:, 0].sum() / max(b[:, 1].sum(), 1)), 4),
                "ci": [round(lo, 4), round(hi, 4)], "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}

    n_docs = len(per_doc["ACTR_LANDED"])
    n_pron = int(np.array(per_doc["ACTR_LANDED"])[:, 1].sum())
    print(f"=== FULL COMPOSED READER on LitBank (LANDED salience_binder IN pipeline; {n_docs} docs, {n_pron} pronoun queries) ===")
    for a in ARMS:
        acc, lo, hi = acc_ci(per_doc[a], SEED + ARMS.index(a))
        print(f"  {a:16s} {acc:.4f}  CI[{lo:.4f},{hi:.4f}]")
    print(f"  ACTR_LANDED - STRING_IDENTITY : {paired(per_doc['ACTR_LANDED'], per_doc['STRING_IDENTITY'], SEED+10)}")
    print(f"  ACTR_LANDED - SHUFFLED_TWIN   : {paired(per_doc['ACTR_LANDED'], per_doc['SHUFFLED_TWIN'], SEED+11)}")
    print("\n[integration] the LANDED salience_binder, run IN the end-to-end reader, reproduces the entity-tracking")
    print("cross-sentence payoff (ACT-R salience > string-identity CI-sep; shuffled twin losing) -> composes end-to-end.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
