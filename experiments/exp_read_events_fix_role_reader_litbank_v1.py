"""EVENTS-FIX: wire the banked who-did-what role reader (29502) onto LitBank events.

Swaps the LIGHTWEIGHT event extractor in hdlab/situation_reader.py (POS predicate + nearest
gold-mention agent/patient) for the banked 29502 consolidated role reader (arc-eager parse ->
role clf -> subcat admissibility gate -> selectional-argmax patient = SUPPLIED VerbNet valency
/ subcat / spurious-suppression knowledge), applied per-clause on LitBank sentences.

This is a WIRING/INTEGRATION cell (knowledge-supply throughline), NOT a new capability. Every
reader component is IMPORTED and CALLED from its banked module (no reimplementation): the
per-clause helper reproduces run_consolidated_reader's arm BIT-FOR-BIT (faithfulness self-test).

MEASUREMENT (no LitBank role gold -> 3 honest ways):
  GATE 1  McGuffey gold cross-check (CAN-FAIL anchor): banked reader F1 >> naive/lightweight F1.
  GATE 2  LitBank noise-reduction (novel discriminator): obviously-wrong events (non-verb
          predicate + inanimate agent), lightweight vs real reader, over 25 books. rel-reduction.
  GLASS   3-4 LitBank side-by-sides (lightweight events vs real-reader events).

HONEST EXPECTATION: PARTIAL noise reduction. Real reader cuts role-assignment noise via the
supplied gate/valency; upstream NLTK POS mis-tags on 19th-c prose that survive the gate PERSIST
(shared parse). If it degrades badly on LitBank -> CLEAN NEGATIVE locating the bottleneck as
upstream POS, not role-knowledge. Reported either way.

Pre-reg: preregs/2026-07-24_read_events_fix_role_reader_litbank_v1.md
Contract: INLINE-LOCAL foreground-to-completion; LOCAL-ONLY (no bank/push/commit). ASCII-only.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified (LIGHTWEIGHT vs REAL_READER event-list hashes differ)
# - final_metrics_atomicity = tmp_replace (metrics.json.tmp -> os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: proxy obviously-wrong COUNT comparison; no Cramer-Rao floor applies
# - baseline_in_band: naive McGuffey F1 in (0.05, 0.95)
# - discriminator: GATE1 reader_f1 >> naive_f1 (real gold, can-fail); GATE2 rel-reduction (can-fail)
# - HARD_PASS strictly above floor; MIDDLE_BAND and CLEAN_NEGATIVE pre-registered
# - real_code_path: self-test builds real clf/sel_fn/parser/gate + calls banked reader fns
# - calibration_check: default_ok_for_this_regime (fixed WordNet lexical test; band = effect size)
# - all numbers MEASURED@ / HYPOTHESIZED@ / CITED@
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import glob
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from nltk.corpus import wordnet as wn  # noqa: E402

# banked 29502 consolidated role reader (import the whole demo -> reuse its wired components) --
import experiments.exp_consolidated_reader_chaingrade_demo_v1 as D  # noqa: E402
# deployed lightweight extractor (the component being replaced) --
import hdlab.situation_reader as SR  # noqa: E402
from hdlab.scene_segment import parse_conll_sentences  # noqa: E402

ANCHOR_NAME = "read_events_fix_role_reader_litbank_v1"
SEED = 20260724
LITBANK_DIR = os.path.join(_REPO, "data", "corpora", "litbank_coref_conll")

# ---- pre-registered bands (see prereg) ----
HP_G1_F1_MIN = 0.55
HP_G1_MARGIN_MIN = 0.12
HF_G1_MARGIN_MAX = 0.0
NAIVE_BAND = (0.05, 0.95)
HP_G2_REL_REDUCTION = 0.20          # HARD_PASS: real cuts obviously-wrong rate by >=20% rel
CLEAN_NEG_G2_REL = -0.20            # CLEAN_NEGATIVE: real >=20% rel NOISIER

# WordNet animacy roots (a noun sense under any of these => animate/person => valid agent)
_ANIM_ROOTS = frozenset({"person.n.01", "animal.n.01", "causal_agent.n.01"})
_AUX_CLOSED = frozenset({
    "is", "are", "was", "were", "be", "been", "being", "am",
    "has", "have", "had", "do", "does", "did",
    "will", "would", "can", "could", "shall", "should", "may", "might", "must"})


# ===========================================================================
# obviously-wrong event signals (applied IDENTICALLY to both arms)
# ===========================================================================
def is_nonverb_pred(pred: str) -> bool:
    """True if the predicate token is NOT a verb (no WordNet verb synset, surface or morphy),
    and not a closed-class aux. Catches proper-noun / adjective mis-tagged as a predicate."""
    if pred is None:
        return False
    w = pred.strip().lower()
    if not w or w in _AUX_CLOSED:
        return False
    if wn.synsets(w, "v"):
        return False
    base = wn.morphy(w, "v")
    if base and wn.synsets(base, "v"):
        return False
    return True


def is_inanimate_agent(agent: str) -> bool:
    """True if the agent is a common noun whose WordNet senses are ALL inanimate (no
    person/animal/causal-agent hypernym). OOV tokens (proper names) and pronouns/'?' are NOT
    flagged (benefit of the doubt for character names). Catches place/thing as agent."""
    if agent is None:
        return False
    w = agent.strip().lower()
    if not w or w == "?":
        return False
    if w in _PRONOUNS:
        return False
    syns = wn.synsets(w, "n")
    if not syns:
        return False  # OOV -> likely a proper name -> not flagged
    for s in syns[:4]:
        for path in s.hypernym_paths():
            for h in path:
                if h.name() in _ANIM_ROOTS:
                    return False
    return True


_PRONOUNS = frozenset({
    "he", "she", "it", "they", "we", "i", "you", "him", "her", "them", "us", "me",
    "his", "hers", "its", "their", "our", "my", "your", "who", "whom", "which", "that",
    "himself", "herself", "itself", "themselves", "myself", "yourself", "ourselves"})


def score_events(events):
    """events: list of (pred, agent, patient). Returns count dict + the per-event flags."""
    n = len(events)
    n_nonverb = n_inan = n_wrong = 0
    n_agent_unfilled = 0
    flagged = []
    for (pred, agent, patient) in events:
        nv = is_nonverb_pred(pred)
        ia = is_inanimate_agent(agent)
        if agent in (None, "?"):
            n_agent_unfilled += 1
        if nv:
            n_nonverb += 1
        if ia:
            n_inan += 1
        wrong = nv or ia
        if wrong:
            n_wrong += 1
            flagged.append((pred, agent, patient, nv, ia))
    rate = (n_wrong / n) if n else 0.0
    return {
        "n_events": n, "n_nonverb_pred": n_nonverb, "n_inanimate_agent": n_inan,
        "n_obviously_wrong": n_wrong, "n_agent_unfilled": n_agent_unfilled,
        "obviously_wrong_rate": rate,
    }, flagged


# ===========================================================================
# the wiring: banked 29502 reader applied per-clause on arbitrary sentence text
# (replicates E.build_parse_arm_v4's inner loop for ONE sentence; every call is a
# banked function -> faithfulness self-test proves bit-identity to the native arm)
# ===========================================================================
def extract_real_events_for_sentence(raw, W, clf, gate_fn, sel_fn,
                                      use_dohave=True, use_ecm=False):
    """raw: one sentence as a RAW STRING (McGuffey sent_text is already a string; LitBank token
    lists are joined by the caller). Returns [(pred, agent, patient), ...]."""
    carried_agent = None
    tups = []
    for clause_text in D.ORC.split_sentences(raw):
        tagged = D.ORC.pos_tag_sentence(clause_text)
        if not tagged:
            continue
        heads = D.M.decode_clause(tagged, W)
        clause_tups, carried_agent, _ev = D.E.clause_predicate_pass_v4(
            tagged, heads, clf, gate_fn, carried_agent, sel_fn=sel_fn,
            use_dohave=use_dohave, use_ecm=use_ecm)
        tups.extend([(t[0], t[1], t[2]) for t in clause_tups])
    return tups


def _events_hash(all_events):
    b = json.dumps(all_events, sort_keys=False, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


# ===========================================================================
# component build (banked 29502 reader components + the McGuffey-derived gate)
# ===========================================================================
def build_reader(run_mode):
    """Returns (W, clf, ratings_table, sel_fn, gate, mcg_order, mcg_text, mcg_slice).
    The gate = the reader's own learned admissibility gate built from its McGuffey training
    slice (SUPPLIED verb-structure knowledge) -- reused unchanged for LitBank extraction."""
    clf = D.V2._fit_clf()
    ratings_table = D.V3.load_knowledge_table()
    W, parser_info = D.M.train_dep_parser(run_mode)
    mcg_slice = D.SMOKE_SLICE if run_mode == "smoke" else D.FULL_SLICE
    # native reader on the McGuffey slice -> returns the learned gate + sel_fn we reuse
    order, sent_text, reader_arm, gate, sel_fn = D.run_consolidated_reader(
        mcg_slice, W, clf, ratings_table, use_dohave=True, use_ecm=False)
    return (W, clf, ratings_table, sel_fn, gate, order, sent_text, reader_arm,
            mcg_slice, parser_info)


# ===========================================================================
# GATE 1 -- McGuffey gold cross-check (real reader >> naive; can-fail anchor)
# ===========================================================================
def gate1_mcguffey(reader_arm, mcg_slice):
    gold, _meta = D.L.load_gold(mcg_slice)
    r_sc, r_rc, _ = D._score_arm_dict(reader_arm, gold)
    _o, _st, naive_arm = D.naive_positional_arm(mcg_slice)
    n_sc, _nrc, _ = D._score_arm_dict(naive_arm, gold)
    reader_f1 = float(r_sc["f1"])
    naive_f1 = float(n_sc["f1"])
    margin = reader_f1 - naive_f1
    return {
        "reader_f1": reader_f1, "reader_prec": float(r_sc["precision"]),
        "reader_rec": float(r_sc["recall"]),
        "naive_f1": naive_f1, "naive_prec": float(n_sc["precision"]),
        "margin": margin,
        "naive_in_band": bool(NAIVE_BAND[0] < naive_f1 < NAIVE_BAND[1]),
        "hard_pass": bool(reader_f1 >= HP_G1_F1_MIN and margin >= HP_G1_MARGIN_MIN),
        "hard_fail": bool(margin <= HF_G1_MARGIN_MAX),
    }


# ===========================================================================
# GATE 2 -- LitBank noise-reduction (lightweight vs real reader over all books)
# ===========================================================================
def gate2_litbank(W, clf, sel_fn, gate, max_books=None, collect_glassbox=8):
    books = sorted(glob.glob(os.path.join(LITBANK_DIR, "*.conll")))
    books = [b for b in books if os.path.getsize(b) > 1000]
    if max_books is not None:
        books = books[:max_books]

    light_events = []   # all (pred, agent, patient) from the lightweight extractor
    real_events = []
    glass = []          # per-sentence side-by-sides where lightweight has an obviously-wrong event
    reader = SR.SituationReader()

    for path in books:
        pid = os.path.splitext(os.path.basename(path))[0]
        # lightweight = the deployed situation_reader event extractor (gold-mention roles)
        sm = reader.read(path)
        light_by_sent = {}
        for ev in sm.events:
            light_by_sent.setdefault(ev.sent_idx, []).append(
                (ev.predicate, ev.agent, ev.patient))
            light_events.append((ev.predicate, ev.agent, ev.patient))
        # real reader = banked 29502 path, per-clause on the same sentence token streams
        sents = parse_conll_sentences(path)
        for si, toks in enumerate(sents):
            rtups = extract_real_events_for_sentence(" ".join(toks), W, clf, gate, sel_fn)
            real_events.extend(rtups)
            # collect glass-box: sentences where lightweight emitted an obviously-wrong event
            if len(glass) < collect_glassbox:
                ltups = light_by_sent.get(si, [])
                _, lflag = score_events(ltups)
                if lflag:
                    glass.append({
                        "book": pid, "sent_idx": si,
                        "text": " ".join(toks)[:220],
                        "lightweight": ltups,
                        "lightweight_flagged": [(p, a, pt, "nonverb" if nv else "",
                                                 "inanimate_agent" if ia else "")
                                                for (p, a, pt, nv, ia) in lflag],
                        "real_reader": rtups,
                        "real_flagged_n": score_events(rtups)[0]["n_obviously_wrong"],
                    })

    light_sc, _ = score_events(light_events)
    real_sc, _ = score_events(real_events)
    lr = light_sc["obviously_wrong_rate"]
    rr = real_sc["obviously_wrong_rate"]
    rel_reduction = ((lr - rr) / lr) if lr > 0 else 0.0
    verdict_g2 = ("HARD_PASS" if rel_reduction >= HP_G2_REL_REDUCTION
                  else "CLEAN_NEGATIVE" if rel_reduction <= CLEAN_NEG_G2_REL
                  else "MIDDLE_BAND")
    return {
        "n_books": len(books),
        "lightweight": light_sc,
        "real_reader": real_sc,
        "rel_reduction": rel_reduction,
        "discriminator_fires": bool(light_sc["n_obviously_wrong"] > 0),
        "verdict_gate2": verdict_g2,
        "arms_differ": bool(_events_hash(light_events) != _events_hash(real_events)),
        "glass_box": glass,
    }


# ===========================================================================
# atomic metrics + markers
# ===========================================================================
def _out_dir(run_mode):
    return os.path.join(_REPO, "data",
                        f"exp_{ANCHOR_NAME}" + ("_smoke" if run_mode == "smoke" else ""))


def _write_start_marker(output_dir, run_mode, expected_n_units):
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    os.makedirs(output_dir, exist_ok=True)
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}",
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ===========================================================================
# formula self-test (REAL code path)
# ===========================================================================
def self_test():
    print("[self-test] obviously-wrong signals ...", flush=True)
    assert is_nonverb_pred("handsome") and is_nonverb_pred("mirvan"), "nonverb-pred miss"
    assert not is_nonverb_pred("ran") and not is_nonverb_pred("go"), "verb wrongly flagged"
    assert not is_nonverb_pred("is") and not is_nonverb_pred("had"), "aux wrongly flagged"
    assert is_inanimate_agent("streets") and is_inanimate_agent("england"), "inanimate miss"
    assert not is_inanimate_agent("passengers") and not is_inanimate_agent("man"), "animate flagged"
    assert not is_inanimate_agent("he") and not is_inanimate_agent("?"), "pronoun/? flagged"
    assert not is_inanimate_agent("villars"), "OOV proper name flagged"

    print("[self-test] building REAL banked reader components (smoke budget) ...", flush=True)
    (W, clf, rt, sel_fn, gate, order, sent_text, reader_arm,
     mcg_slice, pinfo) = build_reader("smoke")
    assert pinfo["uas_dev"] > 0.5, f"parser UAS suspiciously low: {pinfo}"

    # FAITHFULNESS: per-clause helper reproduces the native reader arm BIT-FOR-BIT
    my_arm = {sid: extract_real_events_for_sentence(sent_text[sid], W, clf, gate, sel_fn)
              for sid in order}
    h_helper = D.M.arm_hash(my_arm)
    h_native = D.M.arm_hash(reader_arm)
    assert h_helper == h_native, \
        f"FAITHFULNESS FAIL: helper arm {h_helper} != native arm {h_native} (wiring drift)"
    print(f"[self-test] faithfulness: helper==native arm hash ({h_helper[:12]})", flush=True)

    # GATE 1 discriminator fires at smoke: reader >> naive
    g1 = gate1_mcguffey(reader_arm, mcg_slice)
    assert NAIVE_BAND[0] < g1["naive_f1"] < NAIVE_BAND[1], \
        f"naive F1 {g1['naive_f1']} outside can-fail band"
    assert g1["reader_f1"] > g1["naive_f1"], \
        f"discriminator did not fire: reader {g1['reader_f1']} <= naive {g1['naive_f1']}"
    print(f"[self-test] GATE1 (smoke): reader_f1={g1['reader_f1']:.4f} "
          f"naive_f1={g1['naive_f1']:.4f} margin={g1['margin']:.4f}", flush=True)

    # GATE 2 runs on a tiny book slice + discriminator (there is noise) + arms differ
    g2 = gate2_litbank(W, clf, sel_fn, gate, max_books=3, collect_glassbox=3)
    assert g2["discriminator_fires"], "GATE2: lightweight has 0 obviously-wrong (nothing to cut)"
    assert g2["arms_differ"], "META_RULE_AF: lightweight and real event lists bit-identical"
    print(f"[self-test] GATE2 (3 books): light_rate="
          f"{g2['lightweight']['obviously_wrong_rate']:.3f} "
          f"real_rate={g2['real_reader']['obviously_wrong_rate']:.3f} "
          f"rel_reduction={g2['rel_reduction']:.3f} verdict={g2['verdict_gate2']}", flush=True)
    print("[self-test] PASS", flush=True)
    return 0


# ===========================================================================
# full verdict
# ===========================================================================
def build_verdict(run_mode):
    t0 = time.perf_counter()
    output_dir = _out_dir(run_mode)
    _write_start_marker(output_dir, run_mode, expected_n_units=25)
    print(f"[full] mode={run_mode} building banked reader components ...", flush=True)
    (W, clf, rt, sel_fn, gate, order, sent_text, reader_arm,
     mcg_slice, pinfo) = build_reader(run_mode)
    print(f"[full] parser uas={pinfo['uas_dev']}", flush=True)

    # GATE 1
    g1 = gate1_mcguffey(reader_arm, mcg_slice)
    print(f"[full] GATE1 reader_f1={g1['reader_f1']:.4f} naive_f1={g1['naive_f1']:.4f} "
          f"margin={g1['margin']:.4f} HP={g1['hard_pass']}", flush=True)

    # GATE 2 (all 25 books at full)
    max_books = 3 if run_mode == "smoke" else None
    g2 = gate2_litbank(W, clf, sel_fn, gate, max_books=max_books, collect_glassbox=8)
    print(f"[full] GATE2 n_books={g2['n_books']} "
          f"light: n_ev={g2['lightweight']['n_events']} wrong={g2['lightweight']['n_obviously_wrong']} "
          f"rate={g2['lightweight']['obviously_wrong_rate']:.3f} | "
          f"real: n_ev={g2['real_reader']['n_events']} wrong={g2['real_reader']['n_obviously_wrong']} "
          f"rate={g2['real_reader']['obviously_wrong_rate']:.3f} | "
          f"rel_reduction={g2['rel_reduction']:.3f} -> {g2['verdict_gate2']}", flush=True)

    # overall tier
    if g1["hard_fail"]:
        tier = "HARD_FAIL_WIRING"
        summary = "GATE1 wiring broke the reader (margin<=0); GATE2 untrusted"
    elif not g1["hard_pass"]:
        tier = "MIDDLE_BAND"
        summary = f"GATE1 below HP floor (reader_f1={g1['reader_f1']:.3f} margin={g1['margin']:.3f})"
    else:
        tier = "MEASURED_MECHANISM"
        summary = (f"GATE1 HARD_PASS (reader {g1['reader_f1']:.3f} >> naive {g1['naive_f1']:.3f}); "
                   f"GATE2 {g2['verdict_gate2']} (rel_reduction={g2['rel_reduction']:.3f})")

    elapsed = time.perf_counter() - t0
    verdict_msg = (f"{tier}: {summary}. LitBank noise rate light "
                   f"{g2['lightweight']['obviously_wrong_rate']:.3f} -> real "
                   f"{g2['real_reader']['obviously_wrong_rate']:.3f} "
                   f"(rel {g2['rel_reduction']:+.3f}), {g2['n_books']} books.")

    metrics = {
        "verdict": tier,
        "verdict_msg": verdict_msg,
        "summary": summary,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "seed": SEED,
        "parser_uas_dev": pinfo["uas_dev"],
        "gate1_mcguffey": g1,
        "gate2_litbank": g2,
        "bands": {
            "HP_G1_F1_MIN": HP_G1_F1_MIN, "HP_G1_MARGIN_MIN": HP_G1_MARGIN_MIN,
            "HP_G2_REL_REDUCTION": HP_G2_REL_REDUCTION, "CLEAN_NEG_G2_REL": CLEAN_NEG_G2_REL,
        },
        "arms_differ_verified": g2["arms_differ"],
        "baseline_in_band": g1["naive_in_band"],
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "proxy obviously-wrong count comparison; no Cramer-Rao floor applies",
        "calibration_check": "default_ok_for_this_regime",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "notes": ("WIRING/INTEGRATION cell (knowledge-supply throughline). Real reader = banked "
                  "29502 (V4_DOHAVE_ONLY config, F1 reproduces CITED_DOHAVE_F1=0.592). Lightweight "
                  "= hdlab/situation_reader deployed extractor. Noise proxy (no LitBank role gold): "
                  "non-verb predicate (WordNet verb synset) + inanimate agent (WordNet animacy "
                  "hypernym). Place-specific NER unavailable in-env; animacy proxy substitutes. "
                  "Lightweight is gold-mention-AIDED, real reader is self-contained -> conservative."),
    }
    _write_metrics(output_dir, metrics)
    print(f"[full] wrote {os.path.join(output_dir, 'metrics.json')} elapsed={elapsed:.1f}s", flush=True)
    print("[full] === GLASS-BOX side-by-sides (lightweight vs real reader) ===", flush=True)
    for gb in g2["glass_box"][:6]:
        print(f"  [{gb['book']} S{gb['sent_idx']}] {gb['text']}", flush=True)
        print(f"    LIGHTWEIGHT: {gb['lightweight']}", flush=True)
        print(f"      flagged : {gb['lightweight_flagged']}", flush=True)
        print(f"    REAL      : {gb['real_reader']} (obviously_wrong={gb['real_flagged_n']})", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    return build_verdict("smoke" if args.smoke else "full")


if __name__ == "__main__":
    _od = _out_dir("smoke" if ("--smoke" in sys.argv) else "full")
    try:
        rc = main()
        sys.exit(rc)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
