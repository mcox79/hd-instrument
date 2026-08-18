"""EVENTS SUPPLY-GRAMMAR: does SUPPLYING better grammar (spaCy POS) cut the events bottleneck
that cell 29520 localized to UPSTREAM POS-tagging on 19th-c literary prose?

29520 (exp_read_events_fix_role_reader_litbank_v1) found the dominant events residual = 160
obviously-wrong NONVERB_PRED events: NLTK PerceptronTagger mis-tags proper-nouns / adjectives as
verbs on 19c prose (mirvan-as-verb, handsome-as-verb, red-as-verb). That is UPSTREAM POS, which
role-knowledge cannot fix (shared parse). This cell SUPPLIES better grammar: swap the POS SOURCE
from NLTK to spaCy (en_core_web_sm), holding the ENTIRE downstream who-did-what reader fixed.

NORTH-STAR FRAME (humans read via already-known grammar): spaCy POS = SUPPLIED PREPROCESSING (a
fixed input), NOT a black-box LLM in the reasoning loop. The reader's REASONING (dependency decode
+ role clf + subcat gate + selectional argmax) stays glass-box and UNCHANGED. ONE variable = POS.

DISCRIMINATOR (can-fail, pre-reg): does spaCy POS REDUCE the NONVERB_PRED noise vs NLTK, same
downstream extractor, same 25 LitBank books, same D.ORC.tokenize tokenization?
  HARD_PASS      rel reduction >= 0.25 -> supply-grammar VALIDATED (bottleneck WAS upstream POS).
  CLEAN_NEGATIVE rel reduction <= 0.0  -> not POS-tagging (deeper) / spaCy own-errors offset.
  MIDDLE_BAND    0 < rel < 0.25        -> partial.
CAN-FAIL: spaCy has its OWN tagging errors that can offset the gains. Reported (no free lunch).

Two measurement levels (both all-25-books, real data):
  L1 pure-POS (NO trained parser): nonverb tokens SELECTED AS PREDICATES by content_verb_indices_ext,
     NLTK vs spaCy. Confound-free (parser/clf not involved).
  L2 full extractor: full (pred, agent, patient) events both arms -> 29520's obviously-wrong metric
     (score_events). Absolute obviously-wrong RATE + agent typing. PRIMARY tier discriminator.
POSITIVE CONTROL (Gate D, FULL): NLTK arm = 29520's real-reader path -> reproduces n_nonverb_pred
~= 160, n_events ~= 2601 (CITED@29520). If not, wiring drifted -> flag, distrust delta.

Pre-reg: preregs/2026-07-24_read_events_supply_grammar_spacy_pos_litbank_v1.md
Contract: INLINE-LOCAL foreground-to-completion; LOCAL-ONLY (no bank/push/commit). ASCII-only.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified (NLTK vs spaCy event-list hashes differ)
# - final_metrics_atomicity = tmp_replace (metrics.json.tmp -> os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - crlb_n/a: proxy obviously-wrong COUNT comparison; no Cramer-Rao floor applies
# - baseline_in_band N/A (noise count not accuracy) -> discriminator-fires + positive-control
# - discriminator can-fail (rel<=0 CLEAN_NEGATIVE reachable); FULL run IS full-N (all 25 books)
# - HARD_PASS strictly above floor (rel>=0.25 vs CLEAN_NEG 0.0; gap)
# - real_code_path: self-test builds real reader (W/clf/gate/sel_fn) + calls both taggers + extractor
# - calibration_check: default_ok_for_this_regime (fixed WordNet + pretrained spaCy; band = effect)
# - all numbers MEASURED@ / CITED@ / HYPOTHESIZED@
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

# reuse the 29520 events-fix cell: build_reader, score_events, is_nonverb_pred, is_inanimate_agent,
# the D-chain (D.ORC / D.M / D.E), SR lightweight reader, parse_conll_sentences, LITBANK_DIR.
import experiments.exp_read_events_fix_role_reader_litbank_v1 as EF  # noqa: E402
D = EF.D
ORC = D.ORC
M = D.M
E = D.E

ANCHOR_NAME = "read_events_supply_grammar_spacy_pos_litbank_v1"
SEED = 20260724
LITBANK_DIR = EF.LITBANK_DIR

# ---- pre-registered bands (see prereg) ----
HP_NONVERB_REL_REDUCTION = 0.25     # HARD_PASS: spaCy cuts real-reader nonverb_pred count >=25% rel
CLEAN_NEG_NONVERB_REL = 0.0         # CLEAN_NEGATIVE: spaCy same or NOISIER (no POS benefit)
# positive-control (Gate D) against 29520 real-reader arm (CITED)
CITED_29520_NONVERB = 160          # CITED@data/exp_read_events_fix_role_reader_litbank_v1/metrics.json:gate2_litbank.real_reader.n_nonverb_pred
CITED_29520_NEVENTS = 2601         # CITED@...:gate2_litbank.real_reader.n_events
POS_CTRL_TOL = 0.15                # +/-15% reproduction tolerance


# ===========================================================================
# spaCy POS tagger over the SAME D.ORC.tokenize tokens (pre-tokenized -> one variable = POS only)
# Returns the identical (surface, low, pos) triple format as ORC.pos_tag_sentence, with pos = spaCy
# Penn-Treebank tag_ (VBD/NN/NNP/JJ/...) -- a drop-in for NLTK's tags. SUPPLIED grammar.
# ===========================================================================
def make_spacy_tagger():
    import spacy
    from spacy.tokens import Doc
    # minimal pipeline for tags only (tok2vec -> tagger -> attribute_ruler); no dep-parse / ner / lemma
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner", "lemmatizer"])
    vocab = nlp.vocab
    pipeline = list(nlp.pipeline)

    def tag(sentence):
        toks = ORC.tokenize(sentence)      # SAME tokenization as the NLTK path (one-variable guarantee)
        if not toks:
            return []
        doc = Doc(vocab, words=toks)
        for _name, pipe in pipeline:
            doc = pipe(doc)
        out = []
        for t in doc:
            surf = t.text
            low = surf.lower().strip(".,'\"!?;:")
            out.append((surf, low, t.tag_))
        return out

    return tag


def nltk_tagger(sentence):
    """NLTK arm = the existing 29520 POS source (PerceptronTagger)."""
    return ORC.pos_tag_sentence(sentence)


# ===========================================================================
# LEVEL-1 (pure POS, NO trained parser): nonverb tokens SELECTED AS PREDICATES.
# Confound-free -- content_verb_indices_ext is pure POS (VB* + do/have-lexical). This directly
# measures the localized bottleneck (does the POS source pick fewer non-verbs as predicates).
# ===========================================================================
def predicate_level_counts(raw, tagger_fn):
    n_pred = n_nonverb = 0
    flagged = []
    for clause_text in ORC.split_sentences(raw):
        tagged = tagger_fn(clause_text)
        if not tagged:
            continue
        for pi in E.content_verb_indices_ext(tagged, use_dohave=True):
            low = tagged[pi][1]
            n_pred += 1
            if EF.is_nonverb_pred(low):
                n_nonverb += 1
                flagged.append((low, tagged[pi][2]))   # (token, POS-tag the arm assigned)
    return n_pred, n_nonverb, flagged


# ===========================================================================
# LEVEL-2 (full extractor): parameterized by tagger_fn. Identical to 29520's
# extract_real_events_for_sentence except the POS source is injected (ONE variable).
# ===========================================================================
def extract_events(raw, tagger_fn, W, clf, gate_fn, sel_fn, use_dohave=True, use_ecm=False):
    carried_agent = None
    tups = []
    for clause_text in ORC.split_sentences(raw):
        tagged = tagger_fn(clause_text)
        if not tagged:
            continue
        heads = M.decode_clause(tagged, W)
        clause_tups, carried_agent, _ev = E.clause_predicate_pass_v4(
            tagged, heads, clf, gate_fn, carried_agent, sel_fn=sel_fn,
            use_dohave=use_dohave, use_ecm=use_ecm)
        tups.extend([(t[0], t[1], t[2]) for t in clause_tups])
    return tups


def _events_hash(events):
    b = json.dumps(events, sort_keys=False, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def _pred_tag(clause_text, low_token, tagger_fn):
    """Return the POS tag a tagger assigned to the first occurrence of low_token in a clause
    (glass-box helper: show mirvan/handsome/red POS in each arm)."""
    for clause in ORC.split_sentences(clause_text):
        for (surf, low, pos) in tagger_fn(clause):
            if low == low_token:
                return pos
    return "?"


# ===========================================================================
# main gate: spaCy vs NLTK over the LitBank books
# ===========================================================================
def run_gate(W, clf, gate_fn, sel_fn, spacy_tag, max_books=None, collect_glass=10):
    books = sorted(glob.glob(os.path.join(LITBANK_DIR, "*.conll")))
    books = [b for b in books if os.path.getsize(b) > 1000]
    if max_books is not None:
        books = books[:max_books]

    # Level-1 accumulators
    l1 = {"nltk": {"n_pred": 0, "n_nonverb": 0, "flagged": []},
          "spacy": {"n_pred": 0, "n_nonverb": 0, "flagged": []}}
    # Level-2 event lists
    ev_nltk, ev_spacy = [], []
    glass = []             # NLTK produced an obviously-wrong nonverb-pred; show spaCy side-by-side
    spacy_own_errors = []  # spaCy introduced a nonverb-pred event that NLTK did NOT (own POS error)

    for bi, path in enumerate(books):
        pid = os.path.splitext(os.path.basename(path))[0]
        sents = EF.parse_conll_sentences(path)
        for si, toks in enumerate(sents):
            raw = " ".join(toks)
            # ---- Level 1 (pure POS) ----
            for arm, tf in (("nltk", nltk_tagger), ("spacy", spacy_tag)):
                np_, nn_, fl_ = predicate_level_counts(raw, tf)
                l1[arm]["n_pred"] += np_
                l1[arm]["n_nonverb"] += nn_
                l1[arm]["flagged"].extend(fl_)
            # ---- Level 2 (full extractor) ----
            e_n = extract_events(raw, nltk_tagger, W, clf, gate_fn, sel_fn)
            e_s = extract_events(raw, spacy_tag, W, clf, gate_fn, sel_fn)
            ev_nltk.extend(e_n)
            ev_spacy.extend(e_s)

            # ---- glass-box: sentences where NLTK emitted a nonverb-pred event ----
            _, nflag = EF.score_events(e_n)
            n_nonverb_here = [(p, a, pt) for (p, a, pt, nv, ia) in nflag if nv]
            if n_nonverb_here and len(glass) < collect_glass:
                rows = []
                for (p, a, pt) in n_nonverb_here:
                    rows.append({
                        "nltk_event": [p, a, pt],
                        "nltk_pred_pos": _pred_tag(raw, p, nltk_tagger),
                        "spacy_pred_pos": _pred_tag(raw, p, spacy_tag),
                        "still_pred_in_spacy": any(sp == p for (sp, _sa, _spt) in e_s),
                    })
                glass.append({"book": pid, "sent_idx": si, "text": raw[:220],
                              "nltk_events": e_n, "spacy_events": e_s,
                              "nonverb_preds": rows})

            # ---- spaCy own-error: spaCy emitted a nonverb-pred event NLTK did not ----
            _, sflag = EF.score_events(e_s)
            s_nonverb_here = [(p, a, pt) for (p, a, pt, nv, ia) in sflag if nv]
            nltk_preds = set(p for (p, _a, _pt) in e_n)
            for (p, a, pt) in s_nonverb_here:
                if p not in nltk_preds and len(spacy_own_errors) < 40:
                    spacy_own_errors.append({
                        "book": pid, "sent_idx": si,
                        "spacy_event": [p, a, pt],
                        "spacy_pred_pos": _pred_tag(raw, p, spacy_tag),
                        "nltk_pred_pos": _pred_tag(raw, p, nltk_tagger),
                        "text": raw[:180]})

        if max_books is None:
            print(f"[gate] book {bi+1}/{len(books)} {pid} done "
                  f"(cum nltk_ev={len(ev_nltk)} spacy_ev={len(ev_spacy)})", flush=True)

    # ---- scores ----
    sc_n, _ = EF.score_events(ev_nltk)
    sc_s, _ = EF.score_events(ev_spacy)

    def _rel(a, b):   # reduction from a (nltk) to b (spacy)
        return ((a - b) / a) if a > 0 else 0.0

    l2_nonverb_rel = _rel(sc_n["n_nonverb_pred"], sc_s["n_nonverb_pred"])
    l2_wrongrate_rel = _rel(sc_n["obviously_wrong_rate"], sc_s["obviously_wrong_rate"])
    l2_inan_rel = _rel(sc_n["n_inanimate_agent"], sc_s["n_inanimate_agent"])
    l1_nonverb_rel = _rel(l1["nltk"]["n_nonverb"], l1["spacy"]["n_nonverb"])

    verdict_g = ("HARD_PASS" if l2_nonverb_rel >= HP_NONVERB_REL_REDUCTION
                 else "CLEAN_NEGATIVE" if l2_nonverb_rel <= CLEAN_NEG_NONVERB_REL
                 else "MIDDLE_BAND")

    # positive control: NLTK arm reproduces 29520 real-reader
    pc_nonverb_ok = abs(sc_n["n_nonverb_pred"] - CITED_29520_NONVERB) <= POS_CTRL_TOL * CITED_29520_NONVERB
    pc_nevents_ok = abs(sc_n["n_events"] - CITED_29520_NEVENTS) <= POS_CTRL_TOL * CITED_29520_NEVENTS

    return {
        "n_books": len(books),
        "level1_pure_pos": {
            "nltk_n_pred": l1["nltk"]["n_pred"], "nltk_n_nonverb": l1["nltk"]["n_nonverb"],
            "spacy_n_pred": l1["spacy"]["n_pred"], "spacy_n_nonverb": l1["spacy"]["n_nonverb"],
            "nonverb_rel_reduction": l1_nonverb_rel,
        },
        "level2_full_extractor": {
            "nltk": sc_n, "spacy": sc_s,
            "nonverb_rel_reduction": l2_nonverb_rel,
            "obviously_wrong_rate_rel_reduction": l2_wrongrate_rel,
            "inanimate_agent_rel_reduction": l2_inan_rel,
            "net_event_count_delta": sc_s["n_events"] - sc_n["n_events"],
        },
        "positive_control_vs_29520": {
            "cited_nonverb": CITED_29520_NONVERB, "measured_nltk_nonverb": sc_n["n_nonverb_pred"],
            "cited_n_events": CITED_29520_NEVENTS, "measured_nltk_n_events": sc_n["n_events"],
            "nonverb_reproduced": bool(pc_nonverb_ok), "n_events_reproduced": bool(pc_nevents_ok),
        },
        "discriminator_fires": bool(sc_n["n_nonverb_pred"] > 0),
        "arms_differ": bool(_events_hash(ev_nltk) != _events_hash(ev_spacy)),
        "verdict_gate": verdict_g,
        "spacy_own_error_modes": {
            "n_spacy_introduced_nonverb_preds": len(spacy_own_errors),
            "examples": spacy_own_errors[:12],
        },
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
    print("[self-test] building spaCy tagger + hard-case tagging ...", flush=True)
    spacy_tag = make_spacy_tagger()
    # tokenization parity (one-variable guarantee): spaCy arm uses the SAME tokens as NLTK arm
    s = "a handsome man dodged and the man plunged past him"
    toks_nltk = [t[0] for t in nltk_tagger(s)]
    toks_spacy = [t[0] for t in spacy_tag(s)]
    assert toks_nltk == toks_spacy, f"tokenization drift: {toks_nltk} != {toks_spacy}"
    # spaCy correctly tags the hard 19c cases (proper-noun / adjective NOT verb)
    def _tag(sent, word):
        for (surf, low, pos) in spacy_tag(sent):
            if low == word:
                return pos
        return "?"
    assert not _tag("Mirvan entered the room", "mirvan").startswith("VB"), "spaCy: mirvan tagged VB"
    assert _tag("a handsome man", "handsome") == "JJ", "spaCy: handsome not JJ"
    assert _tag("the red coat lay there", "red") == "JJ", "spaCy: red not JJ"
    assert _tag("the man plunged past him", "plunged").startswith("VB"), "spaCy: plunged not VB"
    # spaCy triple format matches ORC contract
    trip = spacy_tag("the man ran")
    assert all(len(t) == 3 for t in trip), "spaCy tagger not returning (surf,low,pos) triples"

    print("[self-test] building REAL banked reader (smoke budget) ...", flush=True)
    (W, clf, rt, sel_fn, gate, order, sent_text, reader_arm,
     mcg_slice, pinfo) = EF.build_reader("smoke")
    assert pinfo["uas_dev"] > 0.5, f"parser UAS suspiciously low: {pinfo}"

    # REAL code path: both taggers -> extractor produce events on a real clause
    raw0 = sent_text[order[0]]
    e_n = extract_events(raw0, nltk_tagger, W, clf, gate, sel_fn)
    e_s = extract_events(raw0, spacy_tag, W, clf, gate, sel_fn)
    print(f"[self-test] sample clause nltk_events={e_n} spacy_events={e_s}", flush=True)

    # gate on a tiny book slice: discriminator fires + arms differ
    g = run_gate(W, clf, gate, sel_fn, spacy_tag, max_books=3, collect_glass=3)
    assert g["discriminator_fires"], "GATE: NLTK arm has 0 nonverb-preds (nothing to cut)"
    assert g["arms_differ"], "META_RULE_AF: NLTK and spaCy event lists bit-identical"
    l1 = g["level1_pure_pos"]
    l2 = g["level2_full_extractor"]
    print(f"[self-test] (3 books) L1 nonverb nltk={l1['nltk_n_nonverb']} spacy={l1['spacy_n_nonverb']} "
          f"rel={l1['nonverb_rel_reduction']:.3f} | L2 nonverb nltk={l2['nltk']['n_nonverb_pred']} "
          f"spacy={l2['spacy']['n_nonverb_pred']} rel={l2['nonverb_rel_reduction']:.3f} "
          f"verdict={g['verdict_gate']}", flush=True)
    print("[self-test] PASS", flush=True)
    return 0


# ===========================================================================
# full verdict
# ===========================================================================
def build_verdict(run_mode):
    t0 = time.perf_counter()
    output_dir = _out_dir(run_mode)
    _write_start_marker(output_dir, run_mode, expected_n_units=25)
    print(f"[full] mode={run_mode} building spaCy tagger + banked reader ...", flush=True)
    spacy_tag = make_spacy_tagger()
    (W, clf, rt, sel_fn, gate, order, sent_text, reader_arm,
     mcg_slice, pinfo) = EF.build_reader(run_mode)
    print(f"[full] parser uas={pinfo['uas_dev']}", flush=True)

    max_books = 3 if run_mode == "smoke" else None
    g = run_gate(W, clf, gate, sel_fn, spacy_tag, max_books=max_books, collect_glass=10)
    l1 = g["level1_pure_pos"]
    l2 = g["level2_full_extractor"]
    pc = g["positive_control_vs_29520"]

    print(f"[full] n_books={g['n_books']}", flush=True)
    print(f"[full] L1 pure-POS  nonverb-preds nltk={l1['nltk_n_nonverb']} spacy={l1['spacy_n_nonverb']} "
          f"(rel_reduction={l1['nonverb_rel_reduction']:+.3f})", flush=True)
    print(f"[full] L2 full  nonverb_pred nltk={l2['nltk']['n_nonverb_pred']} "
          f"spacy={l2['spacy']['n_nonverb_pred']} (rel={l2['nonverb_rel_reduction']:+.3f}) | "
          f"obviously_wrong_rate nltk={l2['nltk']['obviously_wrong_rate']:.3f} "
          f"spacy={l2['spacy']['obviously_wrong_rate']:.3f} "
          f"(rel={l2['obviously_wrong_rate_rel_reduction']:+.3f})", flush=True)
    print(f"[full] positive-control(29520): nltk_nonverb={pc['measured_nltk_nonverb']} "
          f"(cited {pc['cited_nonverb']}, reproduced={pc['nonverb_reproduced']}) "
          f"nltk_n_events={pc['measured_nltk_n_events']} (cited {pc['cited_n_events']}, "
          f"reproduced={pc['n_events_reproduced']})", flush=True)

    # tier
    if not (pc["nonverb_reproduced"] and pc["n_events_reproduced"]):
        tier = "HARD_FAIL_POSITIVE_CONTROL"
        summary = (f"NLTK arm did NOT reproduce 29520 real-reader (nonverb "
                   f"{pc['measured_nltk_nonverb']} vs cited {pc['cited_nonverb']}; n_events "
                   f"{pc['measured_nltk_n_events']} vs {pc['cited_n_events']}); delta untrusted")
    else:
        vg = g["verdict_gate"]
        if vg == "HARD_PASS":
            tier = "HARD_PASS"
            summary = (f"SUPPLY-GRAMMAR VALIDATED: spaCy POS cuts nonverb_pred noise "
                       f"{l2['nltk']['n_nonverb_pred']}->{l2['spacy']['n_nonverb_pred']} "
                       f"(rel {l2['nonverb_rel_reduction']:+.3f} >= {HP_NONVERB_REL_REDUCTION}); "
                       f"events bottleneck WAS upstream POS")
        elif vg == "CLEAN_NEGATIVE":
            tier = "CLEAN_NEGATIVE"
            summary = (f"spaCy POS does NOT cut nonverb_pred noise "
                       f"{l2['nltk']['n_nonverb_pred']}->{l2['spacy']['n_nonverb_pred']} "
                       f"(rel {l2['nonverb_rel_reduction']:+.3f} <= 0); noise not POS-tagging or "
                       f"spaCy own-errors offset")
        else:
            tier = "MIDDLE_BAND"
            summary = (f"spaCy PARTIAL nonverb_pred reduction "
                       f"{l2['nltk']['n_nonverb_pred']}->{l2['spacy']['n_nonverb_pred']} "
                       f"(rel {l2['nonverb_rel_reduction']:+.3f}, below {HP_NONVERB_REL_REDUCTION})")

    elapsed = time.perf_counter() - t0
    verdict_msg = (f"{tier}: {summary}. L1 pure-POS nonverb {l1['nltk_n_nonverb']}->"
                   f"{l1['spacy_n_nonverb']} (rel {l1['nonverb_rel_reduction']:+.3f}); "
                   f"abs obviously-wrong-rate {l2['nltk']['obviously_wrong_rate']:.3f}->"
                   f"{l2['spacy']['obviously_wrong_rate']:.3f}; spaCy introduced "
                   f"{g['spacy_own_error_modes']['n_spacy_introduced_nonverb_preds']} own nonverb-preds; "
                   f"{g['n_books']} books.")

    metrics = {
        "verdict": tier,
        "verdict_msg": verdict_msg,
        "summary": summary,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "seed": SEED,
        "parser_uas_dev": pinfo["uas_dev"],
        "gate": g,
        "bands": {
            "HP_NONVERB_REL_REDUCTION": HP_NONVERB_REL_REDUCTION,
            "CLEAN_NEG_NONVERB_REL": CLEAN_NEG_NONVERB_REL,
            "positive_control_tol": POS_CTRL_TOL,
        },
        "arms_differ_verified": g["arms_differ"],
        "baseline_in_band": "n/a_noise_count_metric; discriminator_fires + positive_control used",
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "proxy obviously-wrong count comparison; no Cramer-Rao floor applies",
        "calibration_check": "default_ok_for_this_regime",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "progress_logging": "per-book flush prints in run_gate",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "notes": ("SUPPLY-GRAMMAR cell. ONE variable = POS source (NLTK PerceptronTagger vs spaCy "
                  "en_core_web_sm), same D.ORC.tokenize tokenization, same trained parser W + role "
                  "clf + admissibility gate + selectional sel_fn (built once, shared both arms), "
                  "same 25 LitBank books. spaCy POS = SUPPLIED preprocessing (fixed input), NOT a "
                  "black-box LLM in the glass-box reasoning. L1 = pure-POS predicate selection "
                  "(confound-free, no parser); L2 = full extractor (29520 obviously-wrong metric). "
                  "CAVEAT: parser W + clf were fit on NLTK-tagged McGuffey; feeding spaCy tags is a "
                  "mild train/test tag-distribution shift (both Penn Treebank) -> L1 is the "
                  "confound-free evidence, L2 corroborates including the shift. spaCy own-error modes "
                  "reported (no free lunch)."),
    }
    _write_metrics(output_dir, metrics)
    print(f"[full] wrote {os.path.join(output_dir, 'metrics.json')} elapsed={elapsed:.1f}s", flush=True)

    print("[full] === GLASS-BOX: clauses where NLTK emitted a nonverb-pred event (NLTK vs spaCy) ===",
          flush=True)
    for gb in g["glass_box"][:8]:
        print(f"  [{gb['book']} S{gb['sent_idx']}] {gb['text']}", flush=True)
        print(f"    NLTK  events: {gb['nltk_events']}", flush=True)
        print(f"    spaCy events: {gb['spacy_events']}", flush=True)
        for r in gb["nonverb_preds"]:
            print(f"      nonverb-pred '{r['nltk_event'][0]}': NLTK pos={r['nltk_pred_pos']} -> "
                  f"spaCy pos={r['spacy_pred_pos']} (still a pred in spaCy arm: "
                  f"{r['still_pred_in_spacy']})", flush=True)
    print("[full] === spaCy OWN-ERROR modes (nonverb-preds spaCy introduced that NLTK did not) ===",
          flush=True)
    for r in g["spacy_own_error_modes"]["examples"][:8]:
        print(f"  [{r['book']} S{r['sent_idx']}] pred '{r['spacy_event'][0]}' spaCy pos={r['spacy_pred_pos']} "
              f"(NLTK pos={r['nltk_pred_pos']}) :: {r['text']}", flush=True)
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
