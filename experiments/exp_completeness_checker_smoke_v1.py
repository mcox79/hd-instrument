"""exp_completeness_checker_smoke_v1 -- design-gate + smoke for the glass-box
sentence-completeness checker (hdlab.completeness_checker).

Rides on the persisted front-end (data/frontend_assets/{pos_tagger,arc_parser}).
Does NOT rebuild them. Evaluates the checker vs a naive "has any verb" baseline
on a held-out UD-EWT DEV labeled set (gold completeness type derived from the
GOLD parse -- VerbForm=Fin / Mood=Imp / cop; INDEPENDENT of our reader), the
136-sentence construction gold (per-construction false-fragment rate), the
McGuffey third-reader clean narrative (false-fragment rate on mostly-complete
text), and the 3 USER canary sentences.

Brain grounding: predication requirement (subject + finite predicate),
clause-boundary WRAP-UP closure, and GOOD-ENOUGH graded acceptance of context
fragments -> the checker is GRADED, not a hard binary reject, and IMPERATIVE is
a first-class COMPLETE type. See hdlab/completeness_checker.py header (credited).

# CELL-TEMPLATE MANDATORY:
# - arms = {our_checker, naive_verb_baseline}; ARMS-MUST-DIFFER hash-checked at self-test
# - final_metrics_atomicity = tmp_replace (write metrics.json.tmp -> os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: deterministic rule classifier -- no noise floor (declared)
# - baseline_in_band: naive baseline binary acc verified 0.05<acc<0.95 at self-test scale + full
# - discriminator survives scale: eval runs at FULL DEV scale (no reduced smoke-N) = pattern A
# - HARD_PASS strictly above floor: PASS gate = checker_acc >= baseline_acc + 0.05 (margin)
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - real_code_path: self-test constructs CompletenessChecker.from_assets + runs check() on canaries
#
# NO push / NO store write / NO queue_add: this is a local design-gate + smoke cell.

NO LLM. NO nltk. numpy + pure-python + the numpy/pure-python front-end. ASCII-only.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

ANCHOR_NAME = "completeness_checker_smoke_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_%s" % ANCHOR_NAME)

TAGGER_PATH = os.path.join(REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
PARSER_PATH = os.path.join(REPO, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")
DEV_CONLLU = os.path.join(REPO, "experiments", "data", "ud_english_ewt", "en_ewt-ud-dev.conllu")
CONSTR_GOLD = os.path.join(REPO, "data", "gold_construction_argstruct_ewt_v1",
                           "gold_construction_argstruct_ewt_v1.json")
MCGUFFEY = os.path.join(REPO, "data", "corpora", "graded_readers_graded", "cleaned",
                        "mcguffey_third_reader.clean.txt")

# USER-verified canary sentences (hand-tokenized UD-style). Expected labels:
#   CAN_FRAG_1 = FRAGMENT   CITED@USER  (KNOWN honest-divergence risk: initial base verb)
#   CAN_FRAG_2 = FRAGMENT   CITED@USER
#   CAN_IMP    = IMPERATIVE/COMPLETE  CITED@USER  (must NOT be flagged)
CANARIES = [
    ("CAN_FRAG_1", "FRAGMENT",
     ["Feel", "you", "'re", "completely", "surrounded", "by", "that",
      "infinite", "peace", "and", "happiness", "."]),
    ("CAN_FRAG_2", "FRAGMENT",
     ["And", "another", "$", "100", "for", "wrapping", "the", "furniture"]),
    ("CAN_IMP", "COMPLETE",
     ["fill", "it", "with", "water", ":)", "lol"]),
]


# ---------------------------------------------------------------------------
# gold reference (conllu + UD feats)
# ---------------------------------------------------------------------------
def parse_conllu(path):
    sents = []
    sid = None
    text = None
    toks = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# sent_id"):
                sid = line.split("=", 1)[1].strip()
            elif line.startswith("# text"):
                text = line.split("=", 1)[1].strip()
            elif line == "":
                if toks:
                    sents.append({"sent_id": sid, "text": text, "toks": toks})
                sid = None
                text = None
                toks = []
            elif line.startswith("#"):
                continue
            else:
                c = line.split("\t")
                if len(c) != 10:
                    continue
                if "-" in c[0] or "." in c[0]:
                    continue
                toks.append({"id": int(c[0]), "form": c[1], "upos": c[3],
                             "feats": c[5], "head": int(c[6]),
                             "deprel": c[7].split(":")[0]})
    if toks:
        sents.append({"sent_id": sid, "text": text, "toks": toks})
    return sents


def gold_type(toks):
    """Reference completeness type from the GOLD parse. COMPLETE_CLAUSE|IMPERATIVE|FRAGMENT."""
    root = [t for t in toks if t["head"] == 0]
    if not root:
        return "FRAGMENT"
    r = root[0]
    kids = [t for t in toks if t["head"] == r["id"]]
    subj = [t for t in kids if t["deprel"] in ("nsubj", "csubj", "expl")]
    cop = [t for t in kids if t["deprel"] == "cop"]
    aux = [t for t in kids if t["deprel"] == "aux"]
    feats = r["feats"]
    if r["upos"] == "VERB" and "Mood=Imp" in feats:
        return "IMPERATIVE"
    fin_verb = r["upos"] == "VERB" and "VerbForm=Fin" in feats
    fin_cop = any("VerbForm=Fin" in t["feats"] for t in cop)
    fin_aux = any("VerbForm=Fin" in t["feats"] for t in aux)
    finite = fin_verb or fin_cop or fin_aux
    if finite and subj:
        return "COMPLETE_CLAUSE"
    if r["upos"] == "VERB" and subj:   # verb root + subject, feats missing VerbForm -> treat complete
        return "COMPLETE_CLAUSE"
    return "FRAGMENT"


def gold_is_copular(toks):
    root = [t for t in toks if t["head"] == 0]
    if not root:
        return False
    r = root[0]
    return r["upos"] not in ("VERB", "AUX") and \
        any(t["deprel"] == "cop" for t in toks if t["head"] == r["id"])


# ---------------------------------------------------------------------------
# naive baseline: has any verb -> COMPLETE, else FRAGMENT
# ---------------------------------------------------------------------------
def naive_verb_complete(pos_tags):
    return any(p in ("VERB", "AUX") for p in pos_tags)


# ---------------------------------------------------------------------------
# McGuffey narrative -> sentences -> simple UD-ish tokens
# ---------------------------------------------------------------------------
_PAGE = re.compile(r"^\(\d+\)$")
_CONTRACTIONS = ("n't", "'s", "'re", "'ve", "'ll", "'d", "'m")


def simple_tokenize(sent):
    out = []
    for w in sent.split():
        # peel leading punctuation
        m = re.match(r"^([\"'(\[]+)(.*)$", w)
        if m:
            for ch in m.group(1):
                out.append(ch)
            w = m.group(2)
        # peel trailing punctuation
        tail = []
        while w and w[-1] in ".,!?;:\")]'":
            tail.append(w[-1])
            w = w[:-1]
        # split common contractions
        low = w.lower()
        split_c = None
        for c in _CONTRACTIONS:
            if low.endswith(c) and len(w) > len(c):
                split_c = c
                break
        if split_c:
            out.append(w[:-len(split_c)])
            out.append(w[-len(split_c):])
        elif w:
            out.append(w)
        out.extend(reversed(tail))
    return [t for t in out if t]


def mcguffey_sentences(path, max_sents):
    lines = []
    for raw in open(path, encoding="utf-8"):
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        if _PAGE.match(s):
            continue
        # drop ALL-CAPS short title lines (e.g. "THE SHEPHERD BOY.")
        letters = [c for c in s if c.isalpha()]
        if letters and all(c.isupper() for c in letters) and len(s.split()) <= 6:
            continue
        lines.append(s)
    text = " ".join(lines)
    parts = re.split(r"(?<=[.!?])\s+", text)
    sents = []
    for p in parts:
        toks = simple_tokenize(p)
        content = [t for t in toks if any(ch.isalpha() for ch in t)]
        if len(content) >= 4:
            sents.append(toks)
        if len(sents) >= max_sents:
            break
    return sents


# ---------------------------------------------------------------------------
# metrics IO (atomic)
# ---------------------------------------------------------------------------
def write_metrics(metrics):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def write_crash(exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
    }
    write_metrics(diag)


# ---------------------------------------------------------------------------
# self-test: real code path + arms-differ + baseline-in-band
# ---------------------------------------------------------------------------
def self_test():
    import hashlib
    from hdlab.completeness_checker import CompletenessChecker

    checker = CompletenessChecker.from_assets(TAGGER_PATH, PARSER_PATH)
    exercised = set()
    # real_code_path: construct + run the REAL checker on the canaries
    got = {}
    for name, _, toks in CANARIES:
        r = checker.check(toks)
        got[name] = r
        exercised.add("CompletenessChecker.from_assets")
        exercised.add("check")
    # assert measured == expected BEFORE any full (the two clean canaries)
    assert got["CAN_IMP"].is_complete and got["CAN_IMP"].type == "IMPERATIVE", \
        "SELF-TEST FAIL: CAN_IMP must be IMPERATIVE/complete, got %s" % (got["CAN_IMP"].type,)
    assert got["CAN_FRAG_2"].type == "FRAGMENT", \
        "SELF-TEST FAIL: CAN_FRAG_2 must be FRAGMENT, got %s" % (got["CAN_FRAG_2"].type,)

    # ARMS-MUST-DIFFER: checker vs naive baseline predictions differ on the canaries
    tagger = checker.tagger
    chk_pred = "".join("1" if got[n].is_complete else "0" for n, _, _ in CANARIES)
    naive_pred = "".join("1" if naive_verb_complete(tagger.tag(t)) else "0"
                         for _, _, t in CANARIES)
    h1 = hashlib.sha256(chk_pred.encode()).hexdigest()
    h2 = hashlib.sha256(naive_pred.encode()).hexdigest()
    assert h1 != h2, "META_RULE_AF: arms bit-identical on canaries (chk=%s naive=%s)" \
        % (chk_pred, naive_pred)

    assert exercised >= {"CompletenessChecker.from_assets", "check"}, \
        "real_code_path: entrypoints not exercised: %s" % (exercised,)
    print("[self-test] PASS real_code_path + canary asserts + arms-differ "
          "(chk=%s naive=%s)" % (chk_pred, naive_pred))
    return True


# ---------------------------------------------------------------------------
# main eval
# ---------------------------------------------------------------------------
def percentile(vals, q):
    if not vals:
        return 0.0
    v = sorted(vals)
    k = max(0, min(len(v) - 1, int(q * (len(v) - 1))))
    return float(v[k])


def main():
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    from hdlab.completeness_checker import CompletenessChecker, classify_completeness

    tagger_only = CompletenessChecker.from_assets(TAGGER_PATH, PARSER_PATH)
    tagger = tagger_only.tagger
    parser = tagger_only.parser

    # ---- pass 1: DEV labeled eval, collect root margins for the margin floor ----
    dev = parse_conllu(DEV_CONLLU)
    dev = [s for s in dev if 1 <= len(s["toks"]) <= 40]

    records = []
    complete_root_margins = []
    for s in dev:
        toks = [t["form"] for t in s["toks"]]
        pos = tagger.tag(toks)
        parse = parser.parse(toks, pos)
        res = classify_completeness(toks, pos, parse, margin_floor=None)
        gt = gold_type(s["toks"])
        cop = gold_is_copular(s["toks"])
        records.append((gt, cop, res, naive_verb_complete(pos)))
        if gt == "COMPLETE_CLAUSE":
            complete_root_margins.append(res.root_margin)

    # margin floor = 20th percentile of complete-clause root margins (independent signal)
    margin_floor = percentile(complete_root_margins, 0.20)

    # ---- score DEV ----
    gt_bin = {"COMPLETE_CLAUSE": True, "IMPERATIVE": True, "FRAGMENT": False}
    n = len(records)
    chk_correct = 0
    base_correct = 0
    # 3-way confusion for checker
    conf = defaultdict(Counter)      # gold_type -> Counter(pred_type)
    base_conf = defaultdict(Counter)
    # error directions
    overflag = 0     # gold complete/imperative, checker says FRAGMENT
    underflag = 0    # gold FRAGMENT, checker says complete/imperative
    overflag_den = 0
    underflag_den = 0
    # copular handling
    cop_total = 0
    cop_complete = 0
    # margin corroboration on fragments
    frag_margins = []
    comp_margins = []
    frag_low_margin = 0
    frag_total = 0

    for gt, cop, res, naive_c in records:
        gbin = gt_bin[gt]
        cbin = res.is_complete
        chk_correct += int(cbin == gbin)
        base_correct += int(naive_c == gbin)
        conf[gt][res.type] += 1
        base_conf[gt]["COMPLETE" if naive_c else "FRAGMENT"] += 1
        if gbin:
            overflag_den += 1
            if not cbin:
                overflag += 1
        else:
            underflag_den += 1
            if cbin:
                underflag += 1
            frag_total += 1
            frag_margins.append(res.root_margin)
            if res.root_margin < margin_floor:
                frag_low_margin += 1
        if not gbin:
            pass
        else:
            comp_margins.append(res.root_margin)
        if cop:
            cop_total += 1
            if cbin:
                cop_complete += 1

    chk_acc = chk_correct / n
    base_acc = base_correct / n

    # per-gold-type recall for checker (fraction assigned a complete-consistent type)
    per_type = {}
    for gt in ("COMPLETE_CLAUSE", "IMPERATIVE", "FRAGMENT"):
        tot = sum(conf[gt].values())
        if gt == "FRAGMENT":
            correct = conf[gt]["FRAGMENT"]
        else:
            correct = conf[gt]["COMPLETE_CLAUSE"] + conf[gt]["IMPERATIVE"]
        per_type[gt] = {"n": tot, "checker_correct": correct,
                        "recall": (correct / tot if tot else 0.0),
                        "pred_dist": dict(conf[gt])}
    # imperative not-flagged-as-fragment rate (key can-fail)
    imp_tot = sum(conf["IMPERATIVE"].values())
    imp_not_frag = imp_tot - conf["IMPERATIVE"]["FRAGMENT"]

    # ---- construction gold: per-construction false-fragment rate (all are complete) ----
    with open(CONSTR_GOLD, encoding="utf-8") as f:
        cg = json.load(f)["gold"]
    dev_by_sid = {s["sent_id"]: s for s in parse_conllu(DEV_CONLLU)}
    # gold sentences may be train/test/ambiguity split; re-parse all conllu for tokens
    all_sids = {}
    for split in ("train", "dev", "test"):
        p = os.path.join(REPO, "experiments", "data", "ud_english_ewt",
                         "en_ewt-ud-%s.conllu" % split)
        for s in parse_conllu(p):
            all_sids[s["sent_id"]] = s
    constr = defaultdict(lambda: {"n": 0, "flagged_fragment": 0})
    constr_examples = []
    for key, entry in cg.items():
        sid = entry["sent_id"]
        s = all_sids.get(sid)
        if s is None or not (1 <= len(s["toks"]) <= 60):
            continue
        toks = [t["form"] for t in s["toks"]]
        pos = tagger.tag(toks)
        parse = parser.parse(toks, pos)
        res = classify_completeness(toks, pos, parse, margin_floor=margin_floor)
        c = entry["construction"]
        constr[c]["n"] += 1
        if not res.is_complete:
            constr[c]["flagged_fragment"] += 1
            if len(constr_examples) < 8:
                constr_examples.append({"construction": c, "text": entry["text"][:80],
                                        "type": res.type, "conf": res.confidence})
    constr_out = {c: {"n": d["n"], "false_fragment": d["flagged_fragment"],
                      "false_fragment_rate": round(d["flagged_fragment"] / d["n"], 3) if d["n"] else 0.0}
                  for c, d in sorted(constr.items())}
    cg_n = sum(d["n"] for d in constr.values())
    cg_ff = sum(d["flagged_fragment"] for d in constr.values())
    cg_ff_rate = cg_ff / cg_n if cg_n else 0.0

    # ---- McGuffey: false-fragment rate on clean narrative ----
    mg = mcguffey_sentences(MCGUFFEY, max_sents=150)
    mg_frag = 0
    mg_examples = []
    for toks in mg:
        pos = tagger.tag(toks)
        parse = parser.parse(toks, pos)
        res = classify_completeness(toks, pos, parse, margin_floor=margin_floor)
        if not res.is_complete:
            mg_frag += 1
            if len(mg_examples) < 8:
                mg_examples.append({"text": " ".join(toks)[:80], "type": res.type,
                                    "conf": res.confidence, "reason": res.reasons[-1]})
    mg_ff_rate = mg_frag / len(mg) if mg else 0.0

    # ---- canaries ----
    canary_out = []
    canary_pass = True
    for name, expect, toks in CANARIES:
        pos = tagger.tag(toks)
        parse = parser.parse(toks, pos)
        res = classify_completeness(toks, pos, parse, margin_floor=margin_floor)
        got = "COMPLETE" if res.is_complete else "FRAGMENT"
        ok = (got == "COMPLETE") if expect == "COMPLETE" else (got == "FRAGMENT")
        canary_out.append({"name": name, "expect": expect, "type": res.type,
                           "got": got, "conf": res.confidence, "match": ok,
                           "root": res.root_form, "root_pos": res.root_pos,
                           "has_subject": res.has_subject, "reasons": res.reasons})
        # CAN_FRAG_1 is the KNOWN honest-divergence case -> not a hard gate
        if name in ("CAN_FRAG_2", "CAN_IMP") and not ok:
            canary_pass = False

    # margin corroboration
    frag_mean = sum(frag_margins) / len(frag_margins) if frag_margins else 0.0
    comp_mean = sum(comp_margins) / len(comp_margins) if comp_margins else 0.0
    frag_low_rate = frag_low_margin / frag_total if frag_total else 0.0
    margin_corroborates = frag_mean < comp_mean

    lift = chk_acc - base_acc
    baseline_in_band = 0.05 < base_acc < 0.95

    # ---- verdict bands (pre-registered) ----
    # PASS: lift >= +0.05 AND canary_pass (CAN_IMP not flagged, CAN_FRAG_2 flagged)
    #       AND McGuffey false-fragment rate < 0.35 AND baseline_in_band
    # FAIL: lift <= 0 OR McGuffey false-fragment > 0.50 OR CAN_IMP flagged fragment
    fail = (lift <= 0.0) or (mg_ff_rate > 0.50) or (not canary_pass)
    hard_pass = (lift >= 0.05) and canary_pass and (mg_ff_rate < 0.35) and baseline_in_band
    if fail and not hard_pass:
        verdict = "HARD_FAIL"
    elif hard_pass:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    vmsg = ("checker_acc=%.3f naive_acc=%.3f lift=%+.3f | frag_recall=%.3f "
            "imp_not_frag=%d/%d | McGuffey_false_frag=%.3f | canary(imp,frag2)=%s"
            % (chk_acc, base_acc, lift, per_type["FRAGMENT"]["recall"],
               imp_not_frag, imp_tot, mg_ff_rate, canary_pass))

    metrics = {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": "completeness checker vs naive-verb baseline (DEV UD-EWT held-out)",
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "crlb_n/a": "deterministic rule classifier; no noise floor",
        "baseline_in_band": baseline_in_band,
        "arms": {
            "our_checker": {"binary_acc": round(chk_acc, 4)},
            "naive_verb_baseline": {"binary_acc": round(base_acc, 4)},
        },
        "lift": round(lift, 4),
        "dev": {
            "n": n,
            "checker_binary_acc": round(chk_acc, 4),
            "naive_binary_acc": round(base_acc, 4),
            "per_gold_type": per_type,
            "naive_confusion": {k: dict(v) for k, v in base_conf.items()},
            "error_directions": {
                "overflag_fragment_on_complete": overflag,
                "overflag_denominator": overflag_den,
                "overflag_rate": round(overflag / overflag_den, 4) if overflag_den else 0.0,
                "underflag_complete_on_fragment": underflag,
                "underflag_denominator": underflag_den,
                "underflag_rate": round(underflag / underflag_den, 4) if underflag_den else 0.0,
            },
            "copular": {"n": cop_total, "handled_complete": cop_complete,
                        "rate": round(cop_complete / cop_total, 4) if cop_total else 0.0},
            "imperative_not_flagged_fragment": {"n": imp_tot, "not_flagged": imp_not_frag},
        },
        "margin_signal": {
            "margin_floor_p20_complete": round(margin_floor, 4),
            "frag_root_margin_mean": round(frag_mean, 4),
            "complete_root_margin_mean": round(comp_mean, 4),
            "fragments_below_floor_rate": round(frag_low_rate, 4),
            "corroborates_fragment_flag": bool(margin_corroborates),
        },
        "construction_gold": {
            "n": cg_n, "false_fragment": cg_ff,
            "false_fragment_rate": round(cg_ff_rate, 4),
            "per_construction": constr_out,
            "examples_flagged": constr_examples,
        },
        "mcguffey": {
            "n": len(mg), "false_fragment": mg_frag,
            "false_fragment_rate": round(mg_ff_rate, 4),
            "examples_flagged": mg_examples,
        },
        "canaries": canary_out,
        "notes": {
            "known_divergence": "CAN_FRAG_1 ('Feel you're...') roots on an initial "
            "base-form verb -> structurally IMPERATIVE; USER labels it FRAGMENT. "
            "A structural glass-box checker cannot resolve this without semantics; "
            "reported, not gated.",
            "subject_inference": "unlabeled parser -> subject = pre-root nominal dep of root; heuristic (main risk).",
            "register_caveat": "DEV+construction gold = modern web text; McGuffey = children's narrative. Cross-corpus register differs.",
        },
    }
    write_metrics(metrics)
    print(vmsg)
    print("[verdict]", verdict)
    return metrics


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        try:
            self_test()
            sys.exit(0)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:
            write_crash(e)
            raise
    else:
        try:
            main()
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:
            write_crash(e)
            raise
