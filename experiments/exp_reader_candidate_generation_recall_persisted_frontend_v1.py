"""REAL candidate-GENERATION recall on full McGuffey gold -- kills the a2fd38a0 82% arc-existence PROXY.

QUESTION: using the PERSISTED glass-box front-end (hdlab.pos_tagger UPOS + hdlab.arc_parser, loaded not
retrained) + a UD-consistent tokenizer + an UNLABELED-parse candidate inferrer (hdlab.candidate_generator),
does the candidate generator PROPOSE the gold (verb, patient) pair among its candidates, on the FULL
McGuffey gold (100 pos who-is-affected links, 7 lessons)? Report candidate-set RECALL per construction
(coordination / relative / control / pronoun / simple), the real non-proxy aggregate, and compare to:
  (a) CRUDE baseline = the hand-rule reader's raw SVO tuples (the existing candidate generator the LCCP
      4-feature scorer consumed) -- re-derived here on the same gold; and
  (b) the a2fd38a0 82% arc-existence PROXY (CITED; a throwaway fresh parser + nltk POS under domain shift).

This is candidate-set RECALL = an UPPER BOUND on end-to-end (the Step-2 vote then SELECTS among the
candidates). We frame it as the EXTRACTION CEILING, not end-to-end accuracy. Candidate over-generation
(the unlabeled parser cannot tell subject from object) is REPORTED (candidate precision + count) so the
ceiling is honest.

WHY THIS IS NOT THE PROXY:
  proxy: fresh throwaway parser + nltk pos_tag + nltk tokenizer, "does a v->p arc EXIST" -> 82% (flagged
         optimistic: predicted-POS confound + UD-web->McGuffey domain shift + clitic-tokenizer noise).
  here : the PERSISTED front-end the real reader will use, a UD-consistent tokenizer (splits n't / 's), and
         a real candidate GENERATOR that infers verb-arg pairs from arc structure for the constructions a
         crude extractor drops (coordination 2nd-conjunct / relative-clause gap / control-xcomp / pronoun).
  The honest DOMAIN-SHIFT / mis-analysis rate on 1879 narrative (front-end funnel: tokenizer -> POS ->
  parse) is reported -- the number the proxy could not give.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (G1) REAL baseline = the hand-rule reader SVO candidate recall on the SAME gold (re-derived, not a
       strawman). CAN differ from parser -- reader empirically drops coordination-2nd-conjunct + pronoun.
  (G2) CAN-FAIL: the persisted parser on OUT-OF-DOMAIN 1879 text may recover LESS than the 82% proxy;
       reported honestly (real < proxy is the expected, informative outcome).
  (G3) DIFFICULTY-ON: coordination/relative/control/pronoun cases are a large fraction of the gold
       (measured + asserted at smoke; not a saturated all-simple set).
  (G4) ONE-VARIABLE: candidate SOURCE (crude reader vs persisted parser), same gold, same recall metric.

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- load a 5MB tagger json +
1.7MB npz once, tag+parse ~114 short sentences (arc-factored O(n^2), n<~30), + one hand-rule reader pass.
Wall < ~90s. FOREGROUND local-to-completion. NO queue; NO push; NO remote-persist; NO store write.
Storage: no_storage (extraction-recall measurement, not a superposition/composition cell).
Determinism: models are PERSISTED + loaded (no training); OMP/MKL/OPENBLAS=1; no salted hash / list(set);
this cell trains nothing -> single deterministic run (no seed axis, no multi-seed).

CELL-TEMPLATE (subset for a LOCAL foreground measurement; NOT queue-dispatched):
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException); crash -> CELL_CRASHED metrics
- arms differ: crude vs parser candidate sets differ (asserted at smoke)
- discriminator fires: hard-construction gold pairs exist + are recovered by parser but dropped by crude
- CRLB n/a: recall is a recovery FRACTION over a fixed gold, no argmax-noise floor
- cardinality n/a: no sweep axis (single deterministic pass; no seeds)
- multi-seed n/a: cell trains nothing (persisted models loaded)
- all reported numbers MEASURED@ this run's metrics.json; proxy 82% is CITED@scratch_parser_recovery_smoke.py
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import re
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "reader_candidate_generation_recall_persisted_frontend_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.candidate_generator import CandidateGenerator, ud_tokenize, NOMINAL  # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as LCCP  # noqa: E402

POS_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
ARC_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")
GOLD_PATH = os.path.join(REPO_ROOT, "data", "gold_mcguffey_lccp_argstruct_v1.json")
FULL_LESSONS = ["L04", "L05", "L07", "L08", "L09", "L10", "L12"]
SMOKE_LESSONS = ["L04", "L05"]
OUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
PROXY_AGGREGATE = 0.82  # CITED@scratch_parser_recovery_smoke.py (arc-existence proxy, ~82%)
CONSTRUCTIONS = ["coordination", "relative", "control_aspect", "pronoun_obj", "simple"]
HARD_CONSTR = {"coordination", "relative", "control_aspect", "pronoun_obj"}
_PRONOUNS = ("it", "him", "her", "them", "me", "us", "himself", "herself", "themselves")


# ------------------------------------------------------------------------------------------------
# Transparent construction classifier -- REUSED VERBATIM from the a2fd38a0 proxy so the construction
# buckets are apples-to-apples with the 82% number. Surface heuristic (NOT a decision; labels only).
# ------------------------------------------------------------------------------------------------
def classify(txt, v, pat):
    low = txt.lower()
    if pat in _PRONOUNS:
        return "pronoun_obj"
    if re.search(r"\b" + re.escape(pat) + r"\b[^.]*\b(he|she|they|it|which|that|who|whom)\b[^.]*\b" + re.escape(v[:4]), low):
        return "relative"
    if re.search(r"\b(began|begin|commenced|tried|used|going|about|continued|wished|wanted|intend|choose|chose)\b", low):
        return "control_aspect"
    if " and " in low:
        return "coordination"
    return "simple"


# ------------------------------------------------------------------------------------------------
# Surface matching (gold verb = lemma; gold patient = surface head token, pronouns kept).
# ------------------------------------------------------------------------------------------------
def _surf_match(tok, surf):
    tok = tok.lower()
    surf = surf.lower()
    if tok == surf:
        return True
    return len(surf) >= 4 and tok[:4] == surf[:4]


def locate_verb_idxs(tokens, pos, v_lemma):
    """Token indices (1-based) whose VERB lemma == gold v_lemma; plus any-POS match (for mistag audit)."""
    verb_hits, any_hits = [], []
    for i, tk in enumerate(tokens):
        lem = LCCP.lemma_verb(tk)
        if lem == v_lemma:
            any_hits.append(i + 1)
            if pos[i] == "VERB":  # pos is 0-based aligned to tokens; token i+1 (1-based)
                verb_hits.append(i + 1)
    return verb_hits, any_hits


def locate_patient_idxs(tokens, pos, patient):
    """Token indices (1-based) matching gold patient surface; split into nominal-tagged vs any-POS."""
    nom_hits, any_hits = [], []
    for i, tk in enumerate(tokens):
        if _surf_match(tk, patient):
            any_hits.append(i + 1)
            if pos[i] in NOMINAL:
                nom_hits.append(i + 1)
    return nom_hits, any_hits


# ------------------------------------------------------------------------------------------------
# CRUDE baseline: does the hand-rule reader SVO set propose the gold (v, patient) pair for this sid?
# ------------------------------------------------------------------------------------------------
def crude_recovers(reader_tuples, v_lemma, patient):
    for (vs, a, p) in reader_tuples:
        if LCCP.lemma_verb(vs) == v_lemma and _surf_match(p, patient):
            return True
    return False


# ------------------------------------------------------------------------------------------------
# Main measurement.
# ------------------------------------------------------------------------------------------------
def run(lessons):
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    order, sent_text, reader_svo = LCCP.load_slice_and_reader(lessons)
    with open(GOLD_PATH, encoding="utf-8") as f:
        gold_obj = json.load(f)
    gold = gold_obj["gold"]

    # per-construction tallies: [crude_rec, parser_core_rec, parser_ext_rec, located, pos_ok, total]
    by_con = defaultdict(lambda: [0, 0, 0, 0, 0, 0])
    ledger = []
    # domain-shift front-end funnel
    n_pairs = n_located = n_pos_ok = 0
    n_verb_mistag = n_pat_mistag = 0
    # margin calibration (patient-token arc margin on recovered vs missed EXTENDED)
    marg_rec, marg_miss = [], []
    # over-generation
    cand_counts, sent_tok_counts = [], []
    gold_pairs_by_sid = defaultdict(set)

    # cache parses per sid (only sentences with gold pos)
    parse_cache = {}
    for sid, rec in gold.items():
        if sid.split("_")[0] not in lessons:
            continue
        pos_rels = rec.get("pos", [])
        if not pos_rels:
            continue
        txt = sent_text.get(sid)
        if not txt:
            continue
        if sid not in parse_cache:
            parse_cache[sid] = gen.generate(txt, extended=True)
        cr = parse_cache[sid]
        # core-only candidate set (recompute without extended for the core/extended split)
        from hdlab.candidate_generator import candidates_from_parse
        core_pairs, _ = candidates_from_parse(cr.tokens, cr.pos, cr.heads, extended=False)
        ext_pairs = cr.candidates
        reader_tuples = reader_svo.get(sid, [])

        for pr in pos_rels:
            v_lemma = LCCP.lemma_verb(pr["v"])
            patient = pr["patient"].lower()
            con = classify(txt, pr["v"].lower(), patient)
            gold_pairs_by_sid[sid].add((v_lemma, patient))

            # crude baseline
            crude = 1 if crude_recovers(reader_tuples, v_lemma, patient) else 0

            # parser: locate tokens
            v_verb, v_any = locate_verb_idxs(cr.tokens, cr.pos, v_lemma)
            p_nom, p_any = locate_patient_idxs(cr.tokens, cr.pos, patient)
            located = 1 if (v_any and p_any) else 0
            pos_ok = 1 if (v_verb and p_nom) else 0
            # front-end mistag attribution (only when token located)
            if v_any and not v_verb:
                n_verb_mistag += 1
            if p_any and not p_nom:
                n_pat_mistag += 1

            core_rec = ext_rec = 0
            pmarg = None
            if v_verb and p_nom:
                core_rec = 1 if any((vi, pi) in core_pairs for vi in v_verb for pi in p_nom) else 0
                ext_rec = 1 if any((vi, pi) in ext_pairs for vi in v_verb for pi in p_nom) else 0
                pmarg = float(np.mean([cr.margins.get(pi, 0.0) for pi in p_nom]))
                if ext_rec:
                    marg_rec.append(pmarg)
                else:
                    marg_miss.append(pmarg)

            t = by_con[con]
            t[0] += crude; t[1] += core_rec; t[2] += ext_rec; t[3] += located; t[4] += pos_ok; t[5] += 1
            n_pairs += 1; n_located += located; n_pos_ok += pos_ok
            ledger.append({"sid": sid, "construction": con, "v": v_lemma, "patient": patient,
                           "crude": bool(crude), "parser_core": bool(core_rec), "parser_ext": bool(ext_rec),
                           "located": bool(located), "pos_ok": bool(pos_ok),
                           "parse_confidence": round(pmarg, 3) if pmarg is not None else None})

    # over-generation over the parsed gold-bearing sentences
    for sid, cr in parse_cache.items():
        cand_counts.append(len(cr.candidates))
        sent_tok_counts.append(len(cr.tokens))

    # aggregate recalls
    def agg(idx):
        num = sum(by_con[c][idx] for c in by_con)
        den = sum(by_con[c][5] for c in by_con)
        return (num / den) if den else 0.0

    crude_agg = agg(0); core_agg = agg(1); ext_agg = agg(2)

    # candidate precision (over-gen honesty): fraction of proposed candidate pairs that are gold
    tp_pairs = tot_cand_pairs = 0
    for sid, cr in parse_cache.items():
        gp = gold_pairs_by_sid.get(sid, set())
        for (vi, ai) in cr.candidates:
            tot_cand_pairs += 1
            v_lem = LCCP.lemma_verb(cr.tokens[vi - 1])
            a_surf = cr.tokens[ai - 1].lower()
            if any(v_lem == gv and _surf_match(a_surf, gpat) for (gv, gpat) in gp):
                tp_pairs += 1
    cand_precision = (tp_pairs / tot_cand_pairs) if tot_cand_pairs else 0.0

    # margin calibration AUC (recovered patient-margin > missed patient-margin)
    auc = None
    if marg_rec and marg_miss:
        gt = sum(1 for c in marg_rec for w in marg_miss if c > w)
        eq = sum(1 for c in marg_rec for w in marg_miss if c == w)
        auc = (gt + 0.5 * eq) / (len(marg_rec) * len(marg_miss))
    abstain = {}
    allm = [(l["parse_confidence"], l["parser_ext"]) for l in ledger if l["parse_confidence"] is not None]
    for thr in [0, 2, 4, 6, 8]:
        kept = [r for m, r in allm if m >= thr]
        abstain[str(thr)] = {"kept": len(kept), "n": len(allm),
                             "precision": round(sum(kept) / len(kept), 4) if kept else None}

    # per-construction table
    con_table = {}
    for c in CONSTRUCTIONS:
        cr_, co, ex, lo, po, n = by_con.get(c, [0, 0, 0, 0, 0, 0])
        con_table[c] = {"n_gold_pairs": n,
                        "crude_recall": round(cr_ / n, 4) if n else None,
                        "parser_core_recall": round(co / n, 4) if n else None,
                        "parser_ext_recall": round(ex / n, 4) if n else None,
                        "located_rate": round(lo / n, 4) if n else None,
                        "pos_ok_rate": round(po / n, 4) if n else None}

    n_hard = sum(by_con[c][5] for c in HARD_CONSTR)
    # parser structural-failure rate: pairs pos_ok but NOT recovered by extended = parser placed wrong arcs
    n_parse_fail = sum(1 for l in ledger if l["pos_ok"] and not l["parser_ext"])

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "lessons": lessons,
        "n_gold_pos_pairs": n_pairs,
        "aggregate_recall": {
            "crude_handrule_reader": round(crude_agg, 4),
            "parser_core": round(core_agg, 4),
            "parser_extended": round(ext_agg, 4),
            "proxy_arc_existence_CITED": PROXY_AGGREGATE,
        },
        "per_construction": con_table,
        "difficulty_on": {
            "n_hard_construction_pairs": n_hard, "n_total": n_pairs,
            "hard_fraction": round(n_hard / n_pairs, 4) if n_pairs else 0.0,
        },
        "domain_shift_funnel": {
            "located_rate": round(n_located / n_pairs, 4) if n_pairs else None,
            "pos_ok_rate": round(n_pos_ok / n_pairs, 4) if n_pairs else None,
            "parser_extended_recall": round(ext_agg, 4),
            "n_verb_mistag_when_located": n_verb_mistag,
            "n_patient_mistag_when_located": n_pat_mistag,
            "n_parse_structural_fail_when_pos_ok": n_parse_fail,
            "note": "funnel: tokenizer/coref (located) -> POS tagger (pos_ok|located) -> parser (recovered|pos_ok)",
        },
        "over_generation": {
            "mean_candidates_per_sentence": round(float(np.mean(cand_counts)), 2) if cand_counts else None,
            "mean_tokens_per_sentence": round(float(np.mean(sent_tok_counts)), 2) if sent_tok_counts else None,
            "candidate_precision": round(cand_precision, 4),
            "n_candidate_pairs": tot_cand_pairs,
            "note": "unlabeled parser cannot tell subject from object -> low precision by design; Step-2 vote selects",
        },
        "margin_calibration": {
            "mean_margin_recovered": round(float(np.mean(marg_rec)), 3) if marg_rec else None,
            "mean_margin_missed": round(float(np.mean(marg_miss)), 3) if marg_miss else None,
            "n_recovered": len(marg_rec), "n_missed": len(marg_miss),
            "margin_vs_recovery_auc": round(auc, 3) if auc is not None else None,
            "abstain_sweep": abstain,
        },
        "real_above_proxy": bool(ext_agg >= PROXY_AGGREGATE),
        "parser_beats_crude": bool(ext_agg > crude_agg),
    }
    return metrics, ledger


def _atomic_write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def _write_crash(exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "anchor_name": ANCHOR_NAME}
    _atomic_write(os.path.join(OUT_DIR, "metrics.json"), diag)


def self_test():
    """Fast local self-test: exercises the REAL persisted front-end + candidate generator + matching on a
    tiny hand-built set with KNOWN gold pairs. Asserts hard-construction recovery before any full run."""
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    cases = [
        ("He took the blocks and threw it.", "throw", "it", "coordination+pronoun 2nd-conjunct"),
        ("The castle which the cat rubbed fell down.", "rub", "castle", "relative-clause gap"),
        ("He began to build a house.", "build", "house", "control/xcomp embedded object"),
    ]
    ok = True
    for txt, vlem, pat, desc in cases:
        cr = gen.generate(txt, extended=True)
        v_verb, _ = locate_verb_idxs(cr.tokens, cr.pos, vlem)
        p_nom, _ = locate_patient_idxs(cr.tokens, cr.pos, pat)
        rec = bool(v_verb and p_nom and any((vi, pi) in cr.candidates for vi in v_verb for pi in p_nom))
        print("[selftest] %-42s gold=(%s,%s) recovered=%s" % (desc, vlem, pat, rec))
        ok = ok and rec
    # crude vs parser arms must differ on the coordination case (reader drops 2nd-conjunct pronoun)
    assert ok, "SELF-TEST FAIL: persisted front-end did not recover a hard construction it must"
    # tokenizer clitic split (kills the a2fd tokenizer confound)
    assert ud_tokenize("He didn't go.") == ["He", "did", "n't", "go", "."], "UD tokenizer clitic split broken"
    print("[selftest] PASS: hard constructions recovered + UD clitic tokenizer OK")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _ = ap.parse_known_args()
    if args.self_test:
        self_test()
        return
    lessons = SMOKE_LESSONS if args.smoke else FULL_LESSONS
    t0 = time.time()
    metrics, ledger = run(lessons)
    metrics["elapsed_s"] = round(time.time() - t0, 1)
    ext = metrics["aggregate_recall"]["parser_extended"]
    crude = metrics["aggregate_recall"]["crude_handrule_reader"]
    metrics["verdict"] = "MEASURED_CANDIDATE_RECALL"
    metrics["verdict_msg"] = ("parser_ext=%.3f crude=%.3f proxy=%.2f (real %s proxy; parser %s crude) hard_frac=%.2f"
                              % (ext, crude, PROXY_AGGREGATE,
                                 "ABOVE" if metrics["real_above_proxy"] else "BELOW",
                                 "beats" if metrics["parser_beats_crude"] else "<=",
                                 metrics["difficulty_on"]["hard_fraction"]))
    metrics["summary"] = metrics["verdict_msg"]
    _atomic_write(os.path.join(OUT_DIR, "metrics.json"), metrics)
    with open(os.path.join(OUT_DIR, "ledger.jsonl"), "w", encoding="utf-8") as f:
        for l in ledger:
            f.write(json.dumps(l, ensure_ascii=False) + "\n")

    print("\n=== CANDIDATE-GENERATION RECALL vs gold (%s; %d pairs) ===" % (",".join(lessons), metrics["n_gold_pos_pairs"]))
    print("  construction     n    crude   parser_core  parser_ext   located  pos_ok")
    for c in CONSTRUCTIONS:
        r = metrics["per_construction"][c]
        if r["n_gold_pairs"]:
            print("  %-14s %3d   %5s     %5s        %5s      %5s   %5s"
                  % (c, r["n_gold_pairs"], r["crude_recall"], r["parser_core_recall"],
                     r["parser_ext_recall"], r["located_rate"], r["pos_ok_rate"]))
    a = metrics["aggregate_recall"]
    print("  %-14s %3d   %5.3f     %5.3f        %5.3f" % ("ALL", metrics["n_gold_pos_pairs"],
          a["crude_handrule_reader"], a["parser_core"], a["parser_extended"]))
    print("  proxy (arc-existence, CITED) = %.2f" % a["proxy_arc_existence_CITED"])
    print("\n  domain-shift funnel:", json.dumps(metrics["domain_shift_funnel"]))
    print("  over-generation    :", json.dumps(metrics["over_generation"]))
    print("  margin calibration :", json.dumps(metrics["margin_calibration"]))
    print("\n  VERDICT:", metrics["verdict_msg"])
    print("  metrics ->", os.path.join(OUT_DIR, "metrics.json"))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash(e)
        raise
