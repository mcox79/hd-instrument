"""exp_board_common_noun_coref_v1 -- the COMMON-NOUN COREF board arm (realizes the entity-KB tier).

WHY: the board `coref` dim scores only PRONOUN coreference (he/she->antecedent). The entity-KB resolver
(owner-DONE seed_the_entity_world_model_resolver...) improves COMMON-NOUN clustering (the master=the squire=
the old man) -- a DIFFERENT brain system (Sanford-Garrod scenario binding) the board never scored, so its
+0.0882 aggregate common-noun CoNLL win was board-INVISIBLE. This arm scores it: the full-chain entity-KB
resolver's character-cluster CoNLL vs the surface-head floor + the shuffled-KB info-free twin.

REUSES the reverified `exp_entitykb_resolver_v2` (`_per_doc` = the full-chain per-doc CoNLL) +
`exp_commonnoun_referent_linker_v1` (surface_head floor + bootstrap_delta) verbatim, reshaped into the
board's per_dimension row schema (model_acc/strongest_floor/twin_acc/model_minus_strongest[obs,lo,hi]/ci_sep_*),
so it folds into `exp_situation_model_qa_v1.run()` like the patient/goal_hierarchy/wic arms.

Glass-box, NO external LLM (curated KB + WordNet). ASCII.
Run: .venv/Scripts/python.exe experiments/exp_board_common_noun_coref_v1.py [--n 40]
"""
from __future__ import annotations
import os, sys, argparse, json, time
from datetime import datetime, timezone

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_commonnoun_coref_diagnostic_v1 as DIAG
import experiments.exp_commonnoun_referent_linker_v1 as LK
import experiments.exp_entitykb_resolver_v2 as R
from experiments._seed_checkpoint import get_output_dir

ANCHOR = "board_common_noun_coref_v1"
WINDOW = 8
FULL = dict(salience="composite", kb=True, repair=True, sitmodel=True, sitmodel_margin=1.0,
            attrs=True, pron_coref=True, use_reader_coref=True)


def board_common_noun_coref_dimension(n_docs=40, nboot=800):
    """A per_dimension board row (schema-matched to board_goal_dimension) scoring the full-chain entity-KB
    resolver's character-cluster common-noun CoNLL vs the surface-head floor + the shuffled-KB twin. Returns
    (row, detail)."""
    docs, gaz = DIAG.load_docs(n_docs)
    model = R._per_doc(docs, gaz, window=WINDOW, **FULL)
    _, sh = LK.per_doc_stats(docs, gaz, "surface_head")
    r2g_s, r2gen_s = R.shuffle_kb(20260905)
    twin = R._per_doc(docs, gaz, window=WINDOW, **dict(FULL, kb_maps=(r2g_s, r2gen_s)))
    ms = LK.bootstrap_delta(model, sh, nboot)          # {delta, lo, hi, ci_sep} over the CoNLL avg
    mt = LK.bootstrap_delta(model, twin, nboot)
    _acc = lambda sts: round(float(LK._conll_from_stats(sts)["conll_avg"]), 4)   # B3/MUC/CEAFe avg
    m, f, tw = _acc(model), _acc(sh), _acc(twin)
    n_items = sum(int(s[2]) for s in model)            # tuple[2] = n (nonpron mentions) per doc
    row = {
        "n": n_items, "model_acc": m,
        "overlap_floor": f,
        "floor_accs": {"surface_head": f, "shuffled_kb_twin": tw},
        "strongest_floor_name": "surface_head",
        "strongest_floor": f,
        "twin_acc": tw,
        "model_minus_strongest": [ms["delta"], ms["lo"], ms["hi"]],
        "model_minus_twin": [mt["delta"], mt["lo"], mt["hi"]],
        "ci_sep_over_strongest": bool(ms.get("ci_sep")),
        "ci_sep_over_twin": bool(mt.get("ci_sep")),
        "population": "held-out LitBank character-cluster CoNLL (common-noun coref); full-chain entity-KB "
                      "resolver vs surface-head + shuffled-KB twin. The board coref dim scores PRONOUN coref; "
                      "this scores COMMON-NOUN clustering (a distinct brain system the board did not score).",
    }
    detail = {
        "n_docs": n_docs, "model_full_chain": m, "surface_head_floor": f, "shuffled_kb_twin": tw,
        "model_minus_floor": [ms["delta"], ms["lo"], ms["hi"]],
        "model_minus_twin": [mt["delta"], mt["lo"], mt["hi"]],
        "note": "common-noun coref board arm (realizes the entity-KB tier). Reuses exp_entitykb_resolver_v2._per_doc "
                "(full chain, use_reader_coref -- the Step-3 lever, cached two-pass) + the surface-head floor + the "
                "shuffled-KB info-free twin. This is the +0.0882 win the board's PRONOUN coref dim could not see.",
    }
    return row, detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    a = ap.parse_args()
    t0 = time.time()
    row, detail = board_common_noun_coref_dimension(n_docs=(12 if a.self_test else a.n))
    out_dir = get_output_dir(ANCHOR)
    os.makedirs(out_dir, exist_ok=True)
    out = {"anchor": ANCHOR, "row": row, "detail": detail,
           "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print("=" * 96)
    print("COMMON-NOUN COREF board arm  n=%d (%d docs)" % (row["n"], a.n))
    print("  model_acc (full-chain entity-KB) : %.4f" % (row["model_acc"] or 0))
    print("  strongest_floor (surface_head)   : %.4f" % (row["strongest_floor"] or 0))
    print("  twin (shuffled-KB, info-free)    : %.4f" % (row["twin_acc"] or 0))
    print("  model - floor : %s  ci_sep=%s" % (row["model_minus_strongest"], row["ci_sep_over_strongest"]))
    print("  model - twin  : %s  ci_sep=%s" % (row["model_minus_twin"], row["ci_sep_over_twin"]))
    print("=" * 96)
    print("[done] %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
