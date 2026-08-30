"""exp_coref_phi_agreement_prefilter_v1 -- the LANDING-READY validation: the phi-agreement pre-filter (participant +
animacy exclusion) improves the ACTUAL landed resolver `hdlab.graded_coref_pick.graded_antecedent_pick`, not just a
token-recency proxy. This is the turnkey proof for the strategy session's Q111 landing (I cannot write hdlab/).

The pre-filter (exactly what would be added to hdlab/graded_coref_pick.py) is applied to the candidate pool BEFORE
graded_antecedent_pick; the pick index is mapped back to the original pool. Recall-safe (drops only CONFIRMED-
incompatible candidates), causal (prior mentions only), glass-box, KB-free, NO external LLM.

ARMS (over the SAME instances; the only difference is the pre-filter):
  graded_asis         the landed graded_antecedent_pick on the full permissive pool (the deployed resolver = FLOOR).
  graded_prefiltered  the landed graded_antecedent_pick on the phi-agreement-filtered pool (the proposed change).
  prefilter_random    INFO-FREE twin: drop the SAME NUMBER of candidates at random -> must LOSE (recall collapses).
POPULATIONS: FULL competitive (all 3rd-person pronouns; the deployed workload -> the no-regression check) and the
anti-typical residual (where the gain concentrates).

Run: .venv/Scripts/python.exe experiments/exp_coref_phi_agreement_prefilter_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_coref_phi_agreement_prefilter_v1.py --run
ASCII. Pure numpy + NLTK names. Reads the cache. Writes only its own dir. NO hdlab/ write (read-only import of the
landed resolver + tuned weights).
# KB_REFERENT: data/litbank/who_did_what_events.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from typing import Dict, List, Tuple

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_coref_focus_stack_oracle_ceiling_v1 import build_rich, is_antitypical  # noqa: E402
from experiments.exp_coref_residual_participant_pool_v1 import _cluster_mentions, FIRST_SECOND  # noqa: E402
from experiments.exp_coref_residual_phi_agreement_v1 import _build_animacy  # noqa: E402
from experiments.exp_coref_participant_generalization_v1 import _doc_features  # noqa: E402
from experiments.exp_coref_graded_cue_retrieval_litbank_v1 import load_streams, _supports  # noqa: E402
from experiments.exp_litbank_activation_binder_v1 import PRONOUNS  # noqa: E402
from hdlab.graded_coref_pick import graded_antecedent_pick, TUNED_WEIGHTS, DEFAULT_GAIN, DEFAULT_ACTR_D  # noqa: E402

OUTDIR = os.path.join(REPO, "data", "exp_coref_phi_agreement_prefilter_v1")
SEED = 20260830
PERSON = set("he she him her his himself herself".split())
ITS = set("it its itself".split())
THIRD_PERSON = set("he she him her his himself herself it its they them their itself themselves".split())


def is_pure_participant(cl, doc, c, p_sent, p_start, thresh=0.5) -> bool:
    """The REFINED, deployment-faithful participant rule: a cluster is a DISCOURSE PARTICIPANT (the narrator/speaker,
    ineligible as a 3rd-person antecedent) iff its PRIOR mentions are >=thresh 1st/2nd-person AND it has NO PRIOR
    3rd-person mention. The 'no 3rd-person mention' clause is the research-drill fix (a quoted 'I' belongs to a
    CHARACTER, who IS narrated in 3rd person -> keep; the true narrator is never narrated in 3rd person -> exclude).
    Restores recall on the full population (0.979 -> 0.996) and turns the 3rd-person-narration split from a small
    regression into a small gain. Causal (prior mentions only)."""
    fs = third = tot = 0
    for (s, h, st) in cl[(doc, c)]:
        if (s, st) < (p_sent, p_start):
            tot += 1
            fs += int(h in FIRST_SECOND)
            third += int(h in THIRD_PERSON)
    return tot > 0 and fs / tot >= thresh and third == 0


# --------------------------------------------------------------------------- the pre-filter (drop-in for hdlab)
def phi_incompatible(pronoun_low: str, is_part: bool, animacy: str) -> bool:
    """The proposed hard-phi-agreement drop rule. A candidate is INELIGIBLE for a 3rd-person pronoun iff it violates an
    immediately-established phi-feature: PERSON (a discourse participant, 1st/2nd-person -> never a 3rd-person antecedent)
    or ANIMACY (he/she/him/her require an ANIMATE entity; it/its require an INANIMATE one). Confirmed-incompatible ONLY
    (unknown passes) -> recall-safe. Gender is deliberately NOT enforced (causal non-lever)."""
    if is_part:
        return True
    if pronoun_low in PERSON and animacy == "inanimate":
        return True
    if pronoun_low in ITS and animacy == "animate":
        return True
    return False


def _paired(a, b, n_boot, seed):
    docs = sorted(set(a) & set(b))
    A = np.array([a[d] for d in docs], float)
    B = np.array([b[d] for d in docs], float)
    delta = A[:, 0].sum() / max(A[:, 1].sum(), 1) - B[:, 0].sum() / max(B[:, 1].sum(), 1)
    r = np.random.default_rng(seed)
    n = len(docs)
    bo = []
    for _ in range(n_boot):
        idx = r.integers(0, n, n)
        bo.append(A[idx, 0].sum() / max(A[idx, 1].sum(), 1) - B[idx, 0].sum() / max(B[idx, 1].sum(), 1))
    bo = np.array(bo)
    lo, hi = np.percentile(bo, [2.5, 97.5])
    return {"delta": round(float(delta), 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4),
            "half_width": round(float(hi - lo) / 2, 4), "null_p95": round(float(np.percentile(np.abs(bo - bo.mean()), 95)), 4),
            "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}


def _graded_pick_on(priors_subset, p_sent, pron_role):
    """graded_antecedent_pick returns an index INTO the passed list; caller maps back."""
    r = graded_antecedent_pick(priors_subset, p_sent, pron_role, TUNED_WEIGHTS, DEFAULT_GAIN, DEFAULT_ACTR_D)
    return r["pick"]


def run(docs=None, n_boot=2000, seed=SEED) -> Dict:
    streams = load_streams(docs)
    insts = build_rich(streams)
    cl = _cluster_mentions(streams)
    _gold_anim, lex_anim = _build_animacy(streams)
    feats = _doc_features(streams)
    is1st = {d: feats[d]["narr_1st_density"] >= 0.15 for d in feats}

    def _pick_on_keep(priors, keep_idx, ps, prole):
        sub = [priors[i] for i in keep_idx]
        return keep_idx[_graded_pick_on(sub, ps, prole)]

    def eval_pop(anti_only: bool, doc_ok=lambda d: True):
        asis = defaultdict(lambda: [0, 0])
        p_only = defaultdict(lambda: [0, 0])       # TIER 1: participant exclusion only (recall-safe)
        pref = defaultdict(lambda: [0, 0])         # TIER 2: participant + animacy
        rand = defaultdict(lambda: [0, 0])
        rec_p = rec_full = tot = 0
        for inst in insts:
            ids, sup, gi = _supports(inst)
            if anti_only and not is_antitypical(sup, gi):
                continue
            doc = inst["doc"]
            if not doc_ok(doc):
                continue
            cids = inst["cand_ids"]
            plow = inst["pronoun"].lower()
            ps, pst, prole = inst["p_sent"], inst["p_start"], inst.get("pron_role", "OTHER")
            priors = [[(s, r) for (s, r, _st) in inst["prior_rich"][c]] for c in cids]
            part = [is_pure_participant(cl, doc, c, ps, pst) for c in cids]            # REFINED rule
            drop_p = list(part)                                                        # tier 1
            drop_full = [phi_incompatible(plow, part[i], lex_anim(doc, cids[i])) for i in range(len(cids))]  # tier 2
            keep_p = [i for i in range(len(cids)) if not drop_p[i]] or list(range(len(cids)))
            keep_full = [i for i in range(len(cids)) if not drop_full[i]] or list(range(len(cids)))
            p_asis = _graded_pick_on(priors, ps, prole)
            rec_p += int(gi in keep_p); rec_full += int(gi in keep_full); tot += 1
            ndrop = sum(drop_full)
            if ndrop > 0:
                rr = np.random.default_rng(abs(hash((doc, ps, pst, len(cids)))) % (2 ** 31))
                rdrop = set(rr.permutation(len(cids))[:ndrop].tolist())
                rkeep = [i for i in range(len(cids)) if i not in rdrop] or list(range(len(cids)))
            else:
                rkeep = list(range(len(cids)))
            asis[doc][0] += int(p_asis == gi); asis[doc][1] += 1
            p_only[doc][0] += int(_pick_on_keep(priors, keep_p, ps, prole) == gi); p_only[doc][1] += 1
            pref[doc][0] += int(_pick_on_keep(priors, keep_full, ps, prole) == gi); pref[doc][1] += 1
            rand[doc][0] += int(_pick_on_keep(priors, rkeep, ps, prole) == gi); rand[doc][1] += 1
        acc = lambda pd: sum(v[0] for v in pd.values()) / max(sum(v[1] for v in pd.values()), 1)
        return {"asis_acc": round(acc(asis), 4), "participant_only_acc": round(acc(p_only), 4),
                "prefiltered_acc": round(acc(pref), 4), "random_twin_acc": round(acc(rand), 4),
                "recall_participant_only": round(rec_p / max(tot, 1), 4), "recall": round(rec_full / max(tot, 1), 4), "n": tot,
                "participant_only_minus_asis": _paired(dict(p_only), dict(asis), n_boot, seed + 3),
                "prefiltered_minus_asis": _paired(dict(pref), dict(asis), n_boot, seed + 1),
                "prefiltered_minus_random_twin": _paired(dict(pref), dict(rand), n_boot, seed + 2)}

    full = eval_pop(anti_only=False)
    anti = eval_pop(anti_only=True)
    gen_1st = eval_pop(anti_only=False, doc_ok=lambda d: is1st.get(d, False))
    gen_3rd = eval_pop(anti_only=False, doc_ok=lambda d: not is1st.get(d, False))
    return {
        "anchor": "coref_phi_agreement_prefilter_v1",
        "note": "phi-agreement pre-filter (participant + animacy) applied BEFORE the landed graded_antecedent_pick",
        "full_competitive_population": full,
        "anti_typical_residual": anti,
        "generalization_1st_person_docs": gen_1st,
        "generalization_3rd_person_docs": gen_3rd,
        "reading": {
            "TIER1_recall_safe": "pure-participant exclusion: recall ~0.996 full, generalizes ABOVE on full/residual/1st/3rd",
            "TIER2_higher_gain": "+lexical animacy: bigger gain but recall ~0.989 (imperfect lexical animacy; reader NER improves it)",
            "tier1_improves_full_population_CI_sep": full["participant_only_minus_asis"]["band"] == "ABOVE",
            "tier1_improves_residual_CI_sep": anti["participant_only_minus_asis"]["band"] == "ABOVE",
            "tier1_generalizes_1st_person_ABOVE": gen_1st["participant_only_minus_asis"]["band"] == "ABOVE",
            "tier1_no_regression_3rd_person (not BELOW)": gen_3rd["participant_only_minus_asis"]["band"] != "BELOW",
            "tier1_recall_safe_full (>=0.99)": full["recall_participant_only"] >= 0.99,
            "tier2_animacy_adds_gain_full": full["prefiltered_acc"] > full["participant_only_acc"],
            "verdict": ("PREFILTER_IMPROVES_LANDED_RESOLVER_AND_GENERALIZES_LAND_IT"
                        if (full["participant_only_minus_asis"]["band"] == "ABOVE"
                            and gen_1st["participant_only_minus_asis"]["band"] == "ABOVE"
                            and gen_3rd["participant_only_minus_asis"]["band"] != "BELOW"
                            and full["recall_participant_only"] >= 0.99)
                        else "IMPROVES_BUT_CHECK_GENERALIZATION"),
        },
    }


def self_test():
    """The pre-filter drops a participant + an inanimate distractor for a person pronoun, keeps the animate gold."""
    assert phi_incompatible("she", True, None) is True, "a participant must be dropped for 'she'"
    assert phi_incompatible("she", False, "inanimate") is True, "an inanimate must be dropped for 'she'"
    assert phi_incompatible("she", False, "animate") is False, "an animate non-participant must be KEPT for 'she'"
    assert phi_incompatible("it", False, "animate") is True, "an animate person must be dropped for 'it'"
    assert phi_incompatible("it", False, "inanimate") is False, "an inanimate must be KEPT for 'it'"
    assert phi_incompatible("she", False, None) is False, "unknown animacy must PASS (recall-safe)"
    print("SELF-TEST PASS (phi-agreement drop rule: recall-safe, confirmed-incompatible only)")


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
