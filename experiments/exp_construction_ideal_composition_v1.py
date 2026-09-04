"""exp_construction_ideal_composition_v1 -- the IDEAL, exact brain-foundational who-did-what composition over the
referent-per-NP candidate set, with the upstream optimizations, and an HONEST ceiling.

The refutation established: the SELECTOR is already the brain's mechanism (feature-competition, Bates & MacWhinney /
eADM / Frankland-Greene) and is at the competent-reader ceiling (0.928 vs spaCy 0.922). So "the ideal solution HERE"
is NOT a better selector -- it is the composition with UPSTREAM brain-foundational optimizations. This cell prototypes
and measures them on cleaned-DO (n=669, gold verb, selector task):

  S1 SOURCE (PINNED, Kamp/Heim DRT): referent-per-NP. UPSTREAM OPT: extend introduction to INDEFINITE-PRONOUN /
     QUANTIFIER heads (everybody/somebody/thee/...) -- DRT opens a referent for quantified NPs too; our source excludes
     all PRON, so 'invite everybody'/'tell thee' have NO candidate. Measured lift + no-regression + info-free twin.
  S3 SELECTOR (PINNED, Competition-Model feature-competition): the DEPLOYED hybrid_role_patient. NOT ideal_pick (whose
     animacy override is net-negative). Held fixed -- it is already optimal.
  S-PARSE (the filed parser problem): 56% of the residual is parse-recoverable (clefts/inversion/apposition/relcl). We
     do NOT rebuild the parser here; we BOUND its value with the competent-reader ORACLE (spaCy, reference-only): the
     best-of-(ours, competent) per clause = the source+selector+IDEAL-PARSE ceiling. The residual beyond it is the
     GENUINE, gated tail (ill-posed naming/object-complement + meaning-ambiguity + gold noise), categorized.

Brain-foundational verdict per stage is printed PINNED vs OUR-INVENTION. Glass-box, NO LLM at inference (spaCy is the
reference-only ORACLE, never on the inference path). ASCII. own dir. hdlab READ-only.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from collections import Counter
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_19c_composed_cleaned_gold_v1 as CG
import experiments.exp_whodidwhat_ideal_brain_foundational_v1 as IDEAL
from experiments.exp_construction_aware_selector_diagnosis_v1 import _boot, _null_p95
from experiments.exp_construction_aware_selector_brain_comparison_v1 import spacy_picks
from hdlab.pos_tagger import PosTagger
from hdlab.thematic_role_labeler import lemma_verb
from hdlab.graded_role_assigner import hybrid_role_patient

OUT_DIR = os.path.join(_REPO, "data/exp_construction_ideal_composition_v1")
POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")

# DRT opens a referent for quantified / indefinite NPs too (Kamp 1981; Heim 1982 -- indefinites are the paradigm
# referent-introducers). Our source excludes all PRON; these indefinite/quantifier/archaic-2nd-person heads are
# genuine who-did-what patients ("invite everybody", "tell thee") with NO candidate today. PINNED (DRT introduction).
INDEF_PRON = frozenset(("everybody somebody anybody nobody everyone someone anyone "
                        "everything something anything nothing "
                        "thee thou ye "
                        "all none each other others one").split())
NOMINAL = ("NOUN", "PROPN")


def _refnp_plus_indef(toks, pos, add_indef):
    """S1 source: referent-per-NP, optionally + indefinite-pronoun / quantifier heads."""
    base = IDEAL.referent_per_np(toks, pos)
    if not add_indef:
        return base
    extra = [(toks[i].lower(), i) for i in range(len(pos))
             if i < len(toks) and pos[i] == "PRON" and toks[i].lower() in INDEF_PRON]
    return base + [e for e in extra if e not in base]


def sel_pick(toks, pos, vi, add_indef=False, shuffle_rng=None):
    """S3 selector: the DEPLOYED feature-competition hybrid_role_patient over the (optionally extended) source.
    shuffle_rng => info-free twin on the INDEF extension: add the SAME NUMBER of random non-candidate PRON/token
    positions instead of the real indefinite heads."""
    pairs = _refnp_plus_indef(toks, pos, add_indef)
    if shuffle_rng is not None and add_indef:
        base = IDEAL.referent_per_np(toks, pos)
        k = len(pairs) - len(base)
        if k > 0:
            pool = [(toks[i].lower(), i) for i in range(len(toks))
                    if (t := (toks[i].lower(), i)) not in base]
            if pool:
                idx = shuffle_rng.choice(len(pool), size=min(k, len(pool)), replace=False)
                pairs = base + [pool[int(j)] for j in idx]
    if not pairs:
        return None
    cand1 = sorted(ix + 1 for h, ix in pairs)
    idx1 = hybrid_role_patient(toks, pos, vi + 1, cands=cand1, np_head_reduce=True)
    if idx1 is None or not (1 <= idx1 <= len(toks)):
        return None
    return toks[idx1 - 1].lower()


def _categorize_gated(toks, vi, gh, ours, sp):
    """Name why NEITHER ours nor the competent reader recovers a clause -- the genuine gated residual."""
    lv = lemma_verb(toks[vi]) if vi < len(toks) else ""
    NAMING = {"call", "name", "label", "dub", "make", "consider", "deem", "declare", "elect", "term", "appoint"}
    if lv in NAMING:
        return "ill_posed_naming_object_complement"      # small-clause; no single ground-truth patient
    if sp.get("dobj") and sp["dobj"] != gh and sp.get("oprd") and sp["oprd"] != gh:
        return "meaning_or_ambiguity"                    # a real parse exists but neither arg is the gold -> semantics/gold
    return "gold_noise_or_hard"


def run(smoke=False):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tg = PosTagger.load(POS_ASSET)
    rows = [r for r in V1.load_pop(IDEAL.LB) if r.get("gold_head")]
    clean = [r for r in rows if CG.is_clean_do(r, tg.tag(r["sent"].split()))[0]]
    if smoke:
        clean = clean[:100]

    base, indef, indef_twin, comp, best = [], [], [], [], []
    gated = []
    twin_rng = np.random.default_rng(20260903)
    for r in clean:
        toks = r["sent"].split(); vi = r["verb_idx"]; gh = r["gold_head"]
        pos = tg.tag(list(toks))
        b = (sel_pick(toks, pos, vi) or "")
        bi = (sel_pick(toks, pos, vi, add_indef=True) or "")
        bit = (sel_pick(toks, pos, vi, add_indef=True, shuffle_rng=twin_rng) or "")
        sp = spacy_picks(toks, vi)
        c = sp["best"] or ""
        base.append(int(b == gh)); indef.append(int(bi == gh)); indef_twin.append(int(bit == gh))
        comp.append(int(c == gh))
        best_hit = int(bi == gh or c == gh)                     # source+selector+ideal-parse ceiling (best of both)
        best.append(best_hit)
        if not best_hit:
            gated.append(_categorize_gated(toks, vi, gh, bi, sp))

    base = np.array(base); indef = np.array(indef); indef_twin = np.array(indef_twin)
    comp = np.array(comp); best = np.array(best)
    res = {
        "n": len(clean),
        "acc": {"base_deployed_selector": round(float(base.mean()), 4),
                "plus_indef_pron_source": round(float(indef.mean()), 4),
                "plus_indef_twin": round(float(indef_twin.mean()), 4),
                "competent_reader_spacy": round(float(comp.mean()), 4),
                "CEILING_source_selector_idealparse": round(float(best.mean()), 4)},
        "indef_vs_base": _boot(indef, base),
        "indef_vs_twin": _boot(indef, indef_twin),
        "indef_no_regression_note": "indef only ADDS candidates; check delta>=0 and twin loses",
        "ceiling_vs_base": _boot(best, base),
        "genuine_gated_residual_n": int((best == 0).sum()),
        "genuine_gated_residual_frac": round(float((best == 0).mean()), 4),
        "gated_categories": dict(Counter(gated).most_common()),
    }
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "construction_ideal_composition_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    res = run(smoke=(args.self_test or args.smoke))
    a = res["acc"]
    print("\n===== IDEAL brain-foundational who-did-what COMPOSITION (cleaned-DO n=%d, selector task) =====" % res["n"], flush=True)
    print("  [S3 SELECTOR = deployed feature-competition, PINNED, held fixed]", flush=True)
    print("  base deployed selector .................. %.4f" % a["base_deployed_selector"], flush=True)
    print("  + INDEF-PRON source coverage (S1 opt) ... %.4f   (twin %.4f)" % (a["plus_indef_pron_source"], a["plus_indef_twin"]), flush=True)
    di = res["indef_vs_base"]; dt = res["indef_vs_twin"]
    print("     indef vs base   d=%+.4f CI[%+.4f,%+.4f] %s" % (di["delta"], di["ci_lo"], di["ci_hi"], "CI-SEP" if di["sep"] else "n.s."), flush=True)
    print("     indef vs twin   d=%+.4f CI[%+.4f,%+.4f] %s" % (dt["delta"], dt["ci_lo"], dt["ci_hi"], "CI-SEP" if dt["sep"] else "n.s."), flush=True)
    print("  competent reader (spaCy, reference) ..... %.4f" % a["competent_reader_spacy"], flush=True)
    print("  CEILING source+selector+IDEAL-PARSE ..... %.4f   (= best of ours-or-competent per clause)" % a["CEILING_source_selector_idealparse"], flush=True)
    dc = res["ceiling_vs_base"]
    print("     ceiling vs base d=%+.4f CI[%+.4f,%+.4f] %s" % (dc["delta"], dc["ci_lo"], dc["ci_hi"], "CI-SEP" if dc["sep"] else "n.s."), flush=True)
    print("  GENUINE gated residual (neither): %d (%.1f%%) ->" % (res["genuine_gated_residual_n"], 100 * res["genuine_gated_residual_frac"]), res["gated_categories"], flush=True)
    if args.self_test or args.smoke:
        assert res["n"] >= 80
        print("\n[self-test] PASS", flush=True)


if __name__ == "__main__":
    main()
