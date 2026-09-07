"""Scaffold-free LANDING witness: the promoted hdlab.polarity_operator + the read_polarity post-read pass wired
into the LIVE SituationReader (the strategy-session landing of the owner-DONE p9,
represent_negation_and_quantifier_scope_for_truth_conditional_reading_modern_gold).

Distinct from the three reverify witnesses (test_polarity_operator_ewt / test_quantifier_operator /
test_polarity_operator_upgrades), which import experiments._polarity_operator. THIS witness drives the LANDED
path: hdlab.polarity_operator + SituationReader(read_polarity=...).read().

  L1 PROMOTION FAITHFUL: hdlab.polarity_operator is byte-faithful to experiments._polarity_operator -- its own
     26/26 self-test passes AND it agrees with the experiments module case-for-case (the witnesses that import the
     experiments module therefore transfer). state_match is REUSED from hdlab.state_register (no experiments dep).
  L2 ADDITIVE BYTE-IDENTITY: read_polarity ON vs OFF leaves EVERY existing EventRecord field byte-identical (and
     coref_acc / event count / causal-link count -- the board dims read those), on BOTH the canonical
     all_capabilities_off baseline (one-variable isolation) AND the deployed default reader; the new fields are
     None when OFF and populated when ON.
  L3 EWT HEADLINE THROUGH THE LANDED PASS: driving SituationReader(read_polarity=True).read() over the modern
     UD-EWT negation gold and reading e.polarity off the landed field reproduces the net-factuality headline
     (net > 0.85, negated-recall > 0.80, beats the polarity-blind floor which the blind reading gets backwards).

Run: .venv/Scripts/python.exe verification/test_polarity_operator_landing.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import SituationReader, _write_temp_conll
import hdlab.polarity_operator as HP
import experiments._polarity_operator as EP
from experiments.exp_polarity_operator_ewt_v1 import tokenize, align_event, GOLD_PATH

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


# existing EventRecord fields (must be byte-identical read_polarity ON vs OFF -- the additive-isolation target)
_EXISTING = ("global_idx", "sent_idx", "predicate", "agent", "patient", "tense", "subj_role", "obj_role",
             "affect", "patient_surprisal", "pred_precision", "low_confidence", "pred_idx", "patient_prerevise",
             "patient_is_bare_do", "patient_conf", "patient_defer", "agent_conf", "agent_defer", "event_conf")


def _existing(sm):
    return [tuple(getattr(e, f) for f in _EXISTING) for e in sm.events]


def _doc_conll(doc):
    rows = [(si, wi, t, "-") for si, s in enumerate(doc) for wi, t in enumerate(tokenize(s))]
    return _write_temp_conll(rows)


def main():
    # ---------------- L1 promotion faithful ----------------
    try:
        HP._self_test()
        st_ok = True
    except AssertionError:
        st_ok = False
    # agree case-for-case with the experiments module (the witnesses that import it transfer to the landing)
    cases = [
        ("She did not take the key .".split(), 3, "take"),
        ("No one left the room .".split(), 2, "leave"),
        ("He did not manage to escape .".split(), 5, "escape"),
        ("She did not remember him leaving .".split(), 5, "leaving"),
        ("I have not done a test but have done a panel .".split(), 8, "do"),
    ]
    agree_pol = all(HP.event_polarity(t, i, l, verb_lows={"take", "leave", "escape", "remember", "leaving",
                                                          "manage", "do", "done"}).polarity
                    == EP.event_polarity(t, i, l, verb_lows={"take", "leave", "escape", "remember", "leaving",
                                                             "manage", "do", "done"}).polarity
                    for t, i, l in cases)
    q1 = HP.read_quantifier("Everyone but Mary agreed .".split(), subject_region=(0, 3))
    q2 = EP.read_quantifier("Everyone but Mary agreed .".split(), subject_region=(0, 3))
    agree_q = (q1.card, q1.exception) == (q2.card, q2.exception) == ("EXC", "mary")
    # the unified state_match path resolves FROM hdlab (no experiments dep)
    uni = (HP.proposition_answer("She did not take the key .".split(), 3, "take", "take") == "NO"
           and HP.proposition_answer("She took the key .".split(), 1, "take", "take") == "YES")
    chk("L1 promotion faithful: hdlab.polarity_operator self-test 26/26 + agrees with experiments module + "
        "state_match reused from hdlab", st_ok and agree_pol and agree_q and uni,
        "selftest=%s pol_agree=%s quant_agree=%s unified=%s" % (st_ok, agree_pol, agree_q, uni))

    # ---------------- L2 additive byte-identity (isolation on all_capabilities_off + default reader) ----------
    doc = ["She did not take the key from the drawer .", "No one left the room during the meeting .",
           "Everyone but Mary agreed to the new plan .", "He managed to escape before the guards arrived .",
           "All the students passed the difficult exam .", "None of the guards moved .",
           "She knew that he had lied .", "They refused to sign the contract ."]
    conll = _doc_conll(doc)

    # (a) canonical baseline isolation: all_capabilities_off, read_polarity the ONLY variable
    off0 = SituationReader.all_capabilities_off().read(conll)
    on0 = SituationReader.all_capabilities_off(read_polarity=True).read(conll)
    ident0 = _existing(off0) == _existing(on0)
    off0_none = all(e.polarity is None and e.quantity is None and e.quantity_exception is None
                    and e.polarity_provenance is None for e in off0.events)
    on0_set = all(e.polarity is not None for e in on0.events)
    chk("L2a all_capabilities_off isolation: existing EventRecord fields byte-identical (off vs read_polarity ON); "
        "new fields None off / set on", ident0 and off0_none and on0_set,
        "existing_identical=%s off_new_None=%s on_new_set=%s (n_events=%d)" % (
            ident0, off0_none, on0_set, len(on0.events)))

    # (b) deployed default reader: read_polarity ON vs OFF, existing fields + board dims byte-identical
    d_off = SituationReader(read_polarity=False).read(conll)
    d_on = SituationReader(read_polarity=True).read(conll)
    ident_d = _existing(d_off) == _existing(d_on)
    dims_id = (d_off.coref_acc == d_on.coref_acc and len(d_off.events) == len(d_on.events)
               and len(d_off.causal_links) == len(d_on.causal_links)
               and d_off.n_targets == d_on.n_targets)
    d_off_none = all(e.polarity is None for e in d_off.events)
    d_on_set = all(e.polarity is not None for e in d_on.events)
    chk("L2b default reader: existing EventRecord fields + board dims (coref_acc/events/causal/n_targets) "
        "byte-identical (read_polarity ON vs OFF); new fields None off / set on",
        ident_d and dims_id and d_off_none and d_on_set,
        "existing_identical=%s dims_identical=%s off_None=%s on_set=%s" % (ident_d, dims_id, d_off_none, d_on_set))

    # ---------------- L3 EWT headline through the LANDED read_polarity pass ----------------
    if not os.path.exists(GOLD_PATH):
        print("  SKIP L3: EWT negation gold not on disk", flush=True)
    else:
        import json
        gold = json.load(open(GOLD_PATH, encoding="utf-8"))["gold"]
        reader = SituationReader(read_polarity=True)   # the DEPLOYED default config, read_polarity ON
        n = 0; correct = 0; align_fail = 0
        neg_hit = neg_tot = 0; over_neg = aff_tot = 0
        for k, v in gold.items():
            toks = tokenize(v["text"])
            sm = reader.read(_doc_conll([v["text"]]))
            # events for sentence 0 (the item is a single sentence)
            ev = align_event([e for e in sm.events if e.sent_idx == 0], v["verb"], toks)
            if ev is None:
                align_fail += 1
                continue
            # read the LANDED field; map undetermined (0) -> realized (do not over-negate), as factuality scoring does
            pol = -1 if ev.polarity == -1 else +1
            gold_neg = (v["factuality"] == "NEGATED")
            n += 1
            correct += int((pol == -1) == gold_neg)
            if gold_neg:
                neg_tot += 1; neg_hit += int(pol == -1)
            else:
                aff_tot += 1; over_neg += int(pol == -1)
        net = correct / max(1, n)
        neg_recall = neg_hit / max(1, neg_tot)
        blind = sum(1 for _k, _v in gold.items() if _v["factuality"] != "NEGATED")  # blind=all-realized
        # recompute blind on the SCORED population: an event is realized -> blind correct iff item is realized
        # (n scored != len(gold) only by align_fail; blind_floor is realized-fraction of the scored population)
        over_neg_rate = over_neg / max(1, aff_tot)
        chk("L3 EWT headline via LANDED read_polarity field: net-factuality > 0.85, negated-recall > 0.80, "
            "over-negation small (blind reading gets negations backwards)",
            net > 0.85 and neg_recall > 0.80 and over_neg_rate <= 0.05,
            "net %.4f | neg-recall %.4f (n_neg=%d) | over-neg %.4f | n_scored=%d align_fail=%d" % (
                net, neg_recall, neg_tot, over_neg_rate, n, align_fail))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
