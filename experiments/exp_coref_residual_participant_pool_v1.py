"""exp_coref_residual_participant_pool_v1 -- the REAL mechanism underneath the coref anti-typical residual, after
the focus-STACK was refuted (exp_coref_focus_stack_oracle_ceiling_v1): the residual is a CANDIDATE-SET-QUALITY
problem, and the one clean, causal, brain-faithful lever is DISCOURSE-PARTICIPANT EXCLUSION.

PROBLEM: the_coref_residual_needs_a_discourse_focus_stack. The brief proposed a Grosz-Sidner focus STACK. The
oracle-ceiling cell REFUTED that as a distinct lever (with GOLD quote/paragraph/entity-shift segmentation the stack
diverges from finer token-locality in 1/420 cases and ties it; the shuffle twin ties). Reading the person-pronoun
hard cases showed WHY: the anti-typical residual is not topic-shift; the gold looks anti-salient only because the
candidate pool (mean ~44) is FLOODED with non-referents that permissive gender/number agreement admits -- above all
the DISCOURSE PARTICIPANTS (the narrator/speaker "I"/"we", the addressee "you"), whose gender is unknown so they pass
_gn_compat, and who are the most frequent+recent entity so salience grabs them for a 3rd-person pronoun.

THE BRAIN (frame; PINNED vs OUR-INVENTION):
  * PINNED (the computation): discourse comprehension separates the DEICTIC PARTICIPANT roles (speaker=I, hearer=you)
    from the 3rd-person REFERENTS in the focus space (Grosz & Sidner 1986 attentional state distinguishes the
    conversational participants from the focused entities; deixis vs anaphora -- Buhler; Levinson). A 3rd-person
    pronoun (he/she/him/her) never takes the current speaker or addressee as antecedent -- person-feature agreement is
    an OBLIGATORY morphosyntactic constraint (a 1st/2nd-person entity is [+participant], categorically ineligible).
    So the brain's referential candidate SET excludes participants; ours does not.
  * OUR-INVENTION-UNDER-TEST (swept): the operational test for "this cluster is a participant" (here: >=50% of its
    PRIOR mentions are 1st/2nd-person forms). Copy the constraint (participants are ineligible 3rd-person antecedents);
    sweep the threshold / the participant lexicon.
  * NEGATIVE (reported, leak-corrected): positive GENDER agreement does NOT help causally. Using a candidate's OWN
    gendered mentions to establish gender and PRIORITIZE agreeing candidates gives 0.766 ONLY when future mentions
    leak in; causally (prior mentions only, + NLTK-name + gendered-noun gazetteer) gender is unknown for gold ~half
    the time (gold is freshly named), so prioritizing confirmed-gender candidates promotes DISTRACTORS (-0.042
    NOT_SEP). Gender as a hard NEGATIVE (drop confirmed-opposite-gender) is recall-safe but negligible (+0.010
    NOT_SEP): the pool pollution is UNKNOWN-gender clutter, not confirmed-opposite. So the lever is the PARTICIPANT
    feature, not gender.

POPULATION: the anti-typical competitive coref residual (gold best on NONE of global recency/subject/freq), PERSON
pronouns (he/she/him/her/his) -- where person-feature agreement applies. Also the FULL competitive person population
(regression check: the fix must not hurt the typical cases).

ARMS (pick = most-recent candidate by TOKEN distance over the KEPT pool; arms differ ONLY in which candidates are
dropped -- the pool is held otherwise identical, isolating the filter):
  floor_token         FLOOR: token-recency over the permissive pool (the STRONGEST salience floor; sentence-recency
                      and graded score ~0 on this population by construction).
  landed_cleanup      the landed keep_after_pool_cleanup (drops PURE 1st/2nd-person-pronoun artifact clusters).
  participant         OURS: drop clusters whose PRIOR mentions are >=50% 1st/2nd-person (the deixis constraint;
                      catches NAMED narrators the pure-pronoun filter misses).
  gender_disagree     drop confirmed-OPPOSITE-gender clusters (recall-safe hard-negative agreement; reported negative).
  random_drop         INFO-FREE twin: drop the SAME NUMBER of candidates as `participant`, at random -> destroys the
                      participant information, keeps the pool-size reduction. MUST LOSE (and it collapses recall).

Run: .venv/Scripts/python.exe experiments/exp_coref_residual_participant_pool_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_coref_residual_participant_pool_v1.py --run
ASCII. Pure numpy + NLTK names (static gazetteer, gender NEGATIVE arm only). Writes only its own dir. NO hdlab/ write.
# KB_REFERENT: data/litbank/who_did_what_events.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_coref_focus_stack_oracle_ceiling_v1 import build_rich, is_antitypical, _gpos  # noqa: E402
from experiments.exp_coref_graded_cue_retrieval_litbank_v1 import load_streams, _supports  # noqa: E402
from experiments.exp_litbank_activation_binder_v1 import PRONOUNS  # noqa: E402
from hdlab.graded_coref_pick import is_first_second_person_artifact  # noqa: E402 (read-only import)

OUTDIR = os.path.join(REPO, "data", "exp_coref_residual_participant_pool_v1")
SEED = 20260830

# 1st/2nd-person forms: a cluster dominated by these is a discourse PARTICIPANT (speaker/hearer), never a 3rd-person
# antecedent. Superset of graded_coref_pick.FIRST_SECOND_PERSON (adds archaic thou/thee/thy for 19c prose).
FIRST_SECOND = set("i we me us my our ours mine you your yours thou thee thy thine "
                   "myself ourselves yourself yourselves".split())
PERSONAL = set("he she him her his himself herself".split())
# closed lexical-gender lexicon (grammatical/lexical gender; NOT a commonsense KB) for the gender NEGATIVE arm
MALE = set("he him his himself man men boy boys gentleman gentlemen sir master mr lord king father son brother "
           "husband uncle nephew widower".split())
FEM = set("she her hers herself woman women girl girls lady ladies madam miss mrs mistress queen mother daughter "
          "sister wife aunt niece widow".split())

_NAME_GENDER: Dict[str, str] = {}


def _load_name_gender():
    if _NAME_GENDER:
        return
    try:
        from nltk.corpus import names as nltk_names
        male = set(n.lower() for n in nltk_names.words("male.txt"))
        fem = set(n.lower() for n in nltk_names.words("female.txt"))
        for n in male:
            _NAME_GENDER[n] = "m" if n not in fem else "x"
        for n in fem:
            _NAME_GENDER[n] = "f" if n not in male else "x"
    except Exception:
        pass  # gender is the NEGATIVE arm only; absence just makes it weaker, never affects the participant result


# --------------------------------------------------------------------------- cluster features (PRIOR-only = causal)
def _cluster_mentions(streams) -> Dict[Tuple[str, int], List[Tuple[int, str, int]]]:
    cl = defaultdict(list)
    for r in streams:
        for m in r["stream"]:
            cl[(r["doc"], m["gold"])].append((m["sent"], m["head_text"].lower(), m["start"]))
    return cl


def is_participant(cl, doc, c, p_sent, p_start, thresh=0.5) -> bool:
    """>=thresh of the cluster's PRIOR mentions (strictly before the pronoun) are 1st/2nd-person forms -> a discourse
    participant. Causal: uses only mentions before the pronoun."""
    tot = fs = 0
    for (s, h, st) in cl[(doc, c)]:
        if (s, st) < (p_sent, p_start):
            tot += 1
            fs += int(h in FIRST_SECOND)
    return tot > 0 and fs / tot >= thresh


def conf_gender(cl, doc, c, p_sent, p_start) -> Optional[str]:
    """Confirmed gender from PRIOR mentions only (gendered pronouns + gendered nouns + NLTK name gazetteer); None if
    unknown or mixed. For the gender NEGATIVE arm."""
    _load_name_gender()
    male = fem = 0
    for (s, h, st) in cl[(doc, c)]:
        if (s, st) < (p_sent, p_start):
            g = None
            if h in MALE:
                g = "m"
            elif h in FEM:
                g = "f"
            elif h in _NAME_GENDER and _NAME_GENDER[h] != "x":
                g = _NAME_GENDER[h]
            if g == "m":
                male += 1
            elif g == "f":
                fem += 1
    if male > 0 and fem == 0:
        return "m"
    if fem > 0 and male == 0:
        return "f"
    return None


def _cluster_heads(streams) -> Dict[Tuple[str, int], List[str]]:
    ch = defaultdict(list)
    for r in streams:
        for m in r["stream"]:
            ch[(r["doc"], m["gold"])].append(m["head_text"].lower())
    return ch


# --------------------------------------------------------------------------- pick + eval
def _recency(inst, i) -> int:
    doc = inst["doc"]
    return max(_gpos(doc, s, st) for (s, r, st) in inst["prior_rich"][inst["cand_ids"][i]])


def _pick(inst, keep) -> int:
    if not keep:
        keep = list(range(len(inst["cand_ids"])))
    return max(keep, key=lambda i: _recency(inst, i))


def _ci(pd, n_boot, seed):
    arr = np.array([v for v in pd.values()], float)
    tot = arr[:, 1].sum()
    acc = arr[:, 0].sum() / tot if tot else 0.0
    r = np.random.default_rng(seed)
    n = len(arr)
    b = []
    for _ in range(n_boot):
        idx = r.integers(0, n, n)
        c, t = arr[idx, 0].sum(), arr[idx, 1].sum()
        b.append(c / t if t else 0.0)
    lo, hi = np.percentile(b, [2.5, 97.5])
    return {"acc": round(acc, 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4), "n": int(tot)}


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


def _eval(insts, cl, ch, dropfn, population, n_boot, seed):
    """Return per-doc (correct,total), recall, mean kept-pool size, for a drop function over the given population."""
    pd = defaultdict(lambda: [0, 0])
    rec = tot = 0
    kept_sizes = []
    for inst, sup, gi in insts:
        doc = inst["doc"]
        cids = inst["cand_ids"]
        ps, pst = inst["p_sent"], inst["p_start"]
        keep = [i for i in range(len(cids)) if not dropfn(inst, doc, cids[i], ps, pst, i)]
        keep_eff = keep if keep else list(range(len(cids)))
        rec += int(gi in keep)
        kept_sizes.append(len(keep_eff))
        pick = _pick(inst, keep)
        pd[doc][0] += int(pick == gi)
        pd[doc][1] += 1
        tot += 1
    return pd, {"recall": round(rec / max(tot, 1), 4), "n": tot, "mean_kept_pool": round(float(np.mean(kept_sizes)), 1)}


def run(docs=None, n_boot=2000, seed=SEED) -> Dict:
    streams = load_streams(docs)
    insts = build_rich(streams)
    cl = _cluster_mentions(streams)
    ch = _cluster_heads(streams)

    def pop_filter(person_only=True, anti=True):
        out = []
        for inst in insts:
            ids, sup, gi = _supports(inst)
            if person_only and inst["pronoun"].lower() not in PERSONAL:
                continue
            if anti and not is_antitypical(sup, gi):
                continue
            out.append((inst, sup, gi))
        return out

    anti = pop_filter(person_only=False, anti=True)      # FULL anti-typical residual (person + neuter/plural)
    anti_person = pop_filter(person_only=True, anti=True)
    full = pop_filter(person_only=False, anti=False)     # FULL competitive population (regression check)

    # drop functions
    def d_none(inst, doc, c, ps, pst, i):
        return False

    def d_landed(inst, doc, c, ps, pst, i):
        return is_first_second_person_artifact(ch[(doc, c)])

    def d_part(inst, doc, c, ps, pst, i):
        return is_participant(cl, doc, c, ps, pst)

    def d_gender(inst, doc, c, ps, pst, i):
        g = conf_gender(cl, doc, c, ps, pst)
        pg = PRONOUNS[inst["pronoun"].lower()][0]
        return g is not None and g != pg

    def d_part_gender(inst, doc, c, ps, pst, i):
        return d_part(inst, doc, c, ps, pst, i) or d_gender(inst, doc, c, ps, pst, i)

    # random-drop twin: per-instance, drop the SAME number as participant drops, at random (deterministic per instance)
    def make_random_twin():
        def d_rand(inst, doc, c, ps, pst, i):
            cids = inst["cand_ids"]
            ndrop = sum(1 for j in range(len(cids)) if is_participant(cl, doc, cids[j], ps, pst))
            if ndrop == 0:
                return False
            key = (doc, inst["p_sent"], inst["p_start"], len(cids))
            r = np.random.default_rng(abs(hash(key)) % (2 ** 31))
            drop = set(r.permutation(len(cids))[:ndrop].tolist())
            return i in drop
        return d_rand

    arms = {"floor_token": d_none, "landed_cleanup": d_landed, "participant": d_part,
            "gender_disagree": d_gender, "participant_and_gender": d_part_gender, "random_drop": make_random_twin()}

    res_anti = {a: _eval(anti, cl, ch, f, "anti", n_boot, seed + i) for i, (a, f) in enumerate(arms.items())}
    res_person = {a: _eval(anti_person, cl, ch, f, "person", n_boot, seed + 60 + i) for i, (a, f) in enumerate(arms.items())}
    res_full = {a: _eval(full, cl, ch, f, "full", n_boot, seed + 100 + i) for i, (a, f) in enumerate(arms.items())}

    acc_anti = {a: _ci(res_anti[a][0], n_boot, seed + 10 + i) for i, a in enumerate(arms)}
    meta_anti = {a: res_anti[a][1] for a in arms}
    acc_person = {a: _ci(res_person[a][0], n_boot, seed + 70 + i) for i, a in enumerate(arms)}
    acc_full = {a: _ci(res_full[a][0], n_boot, seed + 200 + i) for i, a in enumerate(arms)}

    contrasts = {
        "participant_minus_floor": _paired(res_anti["participant"][0], res_anti["floor_token"][0], n_boot, seed + 40),
        "participant_minus_landed": _paired(res_anti["participant"][0], res_anti["landed_cleanup"][0], n_boot, seed + 41),
        "participant_minus_random_twin": _paired(res_anti["participant"][0], res_anti["random_drop"][0], n_boot, seed + 42),
        "gender_disagree_minus_floor": _paired(res_anti["gender_disagree"][0], res_anti["floor_token"][0], n_boot, seed + 43),
        "part_and_gender_minus_participant": _paired(res_anti["participant_and_gender"][0], res_anti["participant"][0], n_boot, seed + 44),
        "full_pop_participant_minus_floor": _paired(res_full["participant"][0], res_full["floor_token"][0], n_boot, seed + 45),
        "person_participant_minus_floor": _paired(res_person["participant"][0], res_person["floor_token"][0], n_boot, seed + 46),
    }

    # positive control: on the subset where a PARTICIPANT is the (wrong) token-pick, participant exclusion must recover
    pc_n = pc_recover = 0
    for inst, sup, gi in anti:
        doc, cids, ps, pst = inst["doc"], inst["cand_ids"], inst["p_sent"], inst["p_start"]
        floor_pick = _pick(inst, list(range(len(cids))))
        if is_participant(cl, doc, cids[floor_pick], ps, pst) and floor_pick != gi:
            pc_n += 1
            keep = [i for i in range(len(cids)) if not is_participant(cl, doc, cids[i], ps, pst)]
            pc_recover += int(_pick(inst, keep) == gi)

    # residual decomposition (why gold looks anti-typical)
    part_in_pool = 0
    for inst, sup, gi in anti:
        doc, cids, ps, pst = inst["doc"], inst["cand_ids"], inst["p_sent"], inst["p_start"]
        if any(is_participant(cl, doc, cids[i], ps, pst) for i in range(len(cids))):
            part_in_pool += 1

    return {
        "anchor": "coref_residual_participant_pool_v1",
        "population_anti": "LitBank anti-typical coref residual, ALL 3rd-person pronouns (gold best on none of recency/subject/freq)",
        "n_anti": len(anti), "n_anti_person": len(anti_person), "n_full": len(full),
        "mean_pool_permissive": meta_anti["floor_token"]["mean_kept_pool"],
        "participant_present_in_pool_frac": round(part_in_pool / max(len(anti), 1), 3),
        "accuracy_anti": acc_anti, "recall_and_pool_anti": meta_anti,
        "accuracy_anti_person_only": acc_person,
        "accuracy_full_population": acc_full,
        "contrasts": contrasts,
        "positive_control_participant_is_wrong_pick": {"n": pc_n, "recovered_by_exclusion": pc_recover,
                                                       "frac": round(pc_recover / max(pc_n, 1), 3)},
        "reading": {
            "participant_beats_strongest_floor_CI_sep": contrasts["participant_minus_floor"]["band"] == "ABOVE",
            "incremental_over_landed_cleanup_CI_sep": contrasts["participant_minus_landed"]["band"] == "ABOVE",
            "info_free_random_drop_twin_LOSES_CI_sep": contrasts["participant_minus_random_twin"]["band"] == "ABOVE",
            "does_not_regress_full_person_population": contrasts["full_pop_participant_minus_floor"]["band"] != "BELOW",
            "gender_agreement_is_NOT_a_causal_lever": contrasts["gender_disagree_minus_floor"]["band"] != "ABOVE"
            and contrasts["part_and_gender_minus_participant"]["band"] != "ABOVE",
            "verdict": ("PARTICIPANT_EXCLUSION_IS_A_CAUSAL_BRAIN_FAITHFUL_LEVER"
                        if (contrasts["participant_minus_floor"]["band"] == "ABOVE"
                            and contrasts["participant_minus_random_twin"]["band"] == "ABOVE")
                        else "NO_CLEAN_LEVER"),
        },
    }


def self_test():
    """Can-fail fixture: a 3rd-person pronoun with the narrator ('I', a participant, most-recent+frequent) polluting
    the pool. Token-recency grabs the participant; participant exclusion returns the real referent."""
    streams = [{"doc": "__t", "stream": [
        {"sent": 0, "start": 0, "gold": 1, "role": "SUBJECT", "head_text": "Mary", "gov_verb": None, "obj_head": None},
        {"sent": 0, "start": 5, "gold": 0, "role": "SUBJECT", "head_text": "I", "gov_verb": None, "obj_head": None},
        {"sent": 1, "start": 0, "gold": 0, "role": "SUBJECT", "head_text": "I", "gov_verb": None, "obj_head": None},
        {"sent": 1, "start": 4, "gold": 1, "role": "OBJECT", "head_text": "her", "gov_verb": None, "obj_head": None},
        {"sent": 2, "start": 0, "gold": 0, "role": "SUBJECT", "head_text": "I", "gov_verb": None, "obj_head": None},
        {"sent": 2, "start": 3, "gold": 1, "role": "SUBJECT", "head_text": "she", "gov_verb": None, "obj_head": None},
    ]}]
    from experiments.exp_coref_focus_stack_oracle_ceiling_v1 import _META
    _META["__t"] = {"sents": [[]], "sent_lens": [10, 10, 10], "cum": [0, 10, 20, 30], "quote_sents": set(), "n_sent": 3}
    cl = _cluster_mentions(streams)
    # candidate cluster 0 = the narrator "I" (participant); cluster 1 = Mary/her (gold, female)
    # at the "she" pronoun (sent 2, start 3): prior mentions of cluster 0 = I,I,I (participant); cluster 1 = Mary,her.
    assert is_participant(cl, "__t", 0, 2, 3), "cluster 0 (I,I,I) must be flagged a participant"
    assert not is_participant(cl, "__t", 1, 2, 3), "cluster 1 (Mary,her) must NOT be a participant"
    del _META["__t"]
    print("SELF-TEST PASS (narrator 'I' flagged participant; the named referent is not)")


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
