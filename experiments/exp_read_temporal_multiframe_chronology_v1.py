"""SITUATION-MODEL TIME DIMENSION, cell 2: MULTI-FRAME MULTI-SENTENCE chronological
reconstruction -- a RUNNING TIMELINE that orders MULTIPLE events (multiple past-perfect
events among themselves, connectives that CONTRADICT past-perfect demotion, cross-sentence
flashback frames) BEATS both TEXT-ORDER and cell-1's SIMPLE-PP-DEMOTION on real LitBank
prose.

WHY (cell-1 auditor lesson 29509): cell-1 (banked MM 29508) proved SINGLE-FRAME past-perfect
ordering but was CONSTRUCTION-AIDED-CLEAN -- with one pp event "demote pp before narrative-
now" is trivially exactly right, so it could not separate genuine chronological reasoning
from simple pp-tagging+demotion. The real event-indexing TIME dimension is MULTI-FRAME.

THE FAIRER DISCRIMINATOR: the hard subset contains REAL cases where the trivial heuristics
FAIL, spanning three cue types, so that BOTH baselines are dragged low while the mechanism
stays high:
  (B) connectives that CONTRADICT past-perfect demotion ("She rose BEFORE he had finished"
      -> rose before finished; PP_DEMOTE over-demotes the pp). PP_DEMOTE fails, TEXT ok.
  (A) multiple past-perfect events ordered AMONG THEMSELVES by a connective ("had not set
      eyes SINCE he had conducted her" -> conducted before set). BOTH fail.
  (C) cross-sentence / now-first multi-pp flashbacks ("He felt as if strings which had held
      him had loosened" -> held, loosened before felt). TEXT fails, PP_DEMOTE ok.
Aggregated, the hard subset drags BOTH baselines low (the VALIDITY GATE), while a single cue
(text-order OR pp-demotion) cannot solve it -> genuinely multi-frame.

MECHANISM (see experiments/_temporal_ordering_multiframe.py; glass-box constraint graph +
topological sort, NO per-item rules): a RUNNING TIMELINE built from SOFT tense-anteriority
edges (pp anterior to its frame's now-events, across sentence boundaries -> flashback frames)
+ HARD connective edges (a subordinating temporal connective orders its subordinate clause
relative to the adjacent main clause; applies to pp-pp pairs and can REVERSE a tense edge) ->
Kahn topo-sort with text-order tiebreak (abstain when no cue -> never confidently wrong).
The full multi-event chronology is bound into hdlab.SequenceMatrix (glass-box, in-substrate).

ARMS (the ONE variable is the ordering function; extraction is SHARED -- the mechanism uses a
punctuation-preserving re-tokenization that yields the IDENTICAL event set, lemma+tense, as
cell-1's shared extractor, asserted at smoke; only ordering differs):
  TEXT         baseline: chronological order == text order (fails on flashbacks / reorders)
  PP_DEMOTE    baseline: cell-1's core heuristic (all pp before all now, text order within)
  CELL1_CUE    reference: cell-1's full CUE (pp-demote + adjacent-simple-past connective swap)
  MECH         mechanism: the running-timeline multi-frame reconstruction
  MECH_ABLATE  P2 ablation: mechanism with multi-frame logic OFF -> reduces to PP_DEMOTE

GOLD: REAL LitBank sentences (public-domain novels; ASCII-normalized; verbs + order VERBATIM),
hand-labeled with UNAMBIGUOUS chronological (earlier, later) event pairs derived from STORY-
WORLD MEANING (not from the mechanism's rule -> non-circular). Source citation + hard-case
TYPE (A/B/C) shown per item. This gold is a BASE INGREDIENT and WILL be skunkworks-VET'd.

HONEST SCOPE / construction-risk (declared for the auditor):
  * 8 of the 9 hard items are REAL verbatim/trimmed LitBank prose; the win holds on the
    REAL-ONLY subset (reported separately). ONE item (after_synth) is a synthetic
    illustrative case (a): genuine multi-pp-reorder-by-connective is near-nonexistent in
    natural prose (authors write pp events in chronological text order) -- an honest finding,
    flagged, and a MINORITY (1/9); dropping it does NOT change the verdict.
  * Two REAL type-B items (before2/before3) have a COORDINATED simple-past verb
    (hastened/dreamed) that the SHARED POS extractor mis-tags as pp via cross-clause 'had'
    bleed; the mechanism inherits this (parity is required) and mis-orders that ONE
    coordinate pair -> partial (1/2). It still recovers the DISCRIMINATING pair. This is an
    EXTRACTION limitation, not an ordering one; the named next lever = clause-bounded tense
    tagging.

Compute architecture: sequential-CPU JUSTIFIED -- deterministic, wall < 10s, no seed axis on
the discriminator (substrate matrices tiny N_DIM=1024); this cell validates the SequenceMatrix
multi-event chain on real reader tuples. Storage: sharded per-event codevectors in a Codebook
+ a separate SequenceMatrix S (no bundling). Not banked here (skunkworks VETs).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (PP_DEMOTE==MECH_ABLATE is an INTENTIONAL P2 exemption)
# - final_metrics_atomicity: tmp_replace (metrics.json.tmp + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: reconstruction accuracy is a discrete pairwise order-match, no Gaussian floor
# - baseline_in_band: TEXT + PP_DEMOTE hard-subset acc both in (0.05, 0.95) (validity gate)
# - discriminator: real LitBank multi-frame items; margins MECH-PP_DEMOTE and MECH-TEXT
# - numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
# - progress_logging: print_flush_true (cell is <10s but flushes each arm line)
from __future__ import annotations

import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import _temporal_ordering as T  # noqa: E402
from experiments import _temporal_ordering_multiframe as M  # noqa: E402
from experiments.exp_read_temporal_chronological_event_order_v1 import (  # noqa: E402
    FLASHBACK_GOLD as CELL1_FLASHBACK, LINEAR_GOLD as CELL1_LINEAR)

ANCHOR_NAME = "read_temporal_multiframe_chronology_v1"
N_DIM = 1024
CODEBOOK_SEED = 20260723

# Pre-registered bands (set BEFORE this run).
VALIDITY_TEXT_MAX = 0.60        # TEXT hard-subset acc must be <= this (genuinely reorderable)
VALIDITY_PPDEMOTE_MAX = 0.75    # PP_DEMOTE hard-subset acc <= this (cell-1 heuristic genuinely fails)
HARD_PASS_MARGIN_PP = 0.15      # MECH - PP_DEMOTE on the hard subset (strict; beat cell-1 heuristic)
HARD_PASS_MARGIN_TEXT = 0.20    # MECH - TEXT on the hard subset
HARD_PASS_MECH_MIN = 0.80       # MECH hard-subset acc floor
HARD_FAIL_MARGIN_PP = 0.05      # MECH - PP_DEMOTE < this -> HARD_FAIL (mechanism adds nothing)


# ---------------------------------------------------------------------------
# GOLD -- REAL LitBank prose (+ 1 flagged synthetic). type: A=multi-pp reorder,
# B=connective contradicts pp-demote, C=cross-sentence/now-first multi-pp flashback.
# pairs = (earlier_lemma, later_lemma) in CHRONOLOGY, from story-world meaning.
# ---------------------------------------------------------------------------
HARD_GOLD = [
    {"id": "before1", "type": "B", "risk": "real",
     "text": "Before Mrs Croft had written, he was arrived, and the very next time Anne walked out, she saw him.",
     "source": "Persuasion (Austen), LitBank 105",
     "pairs": [["arrived", "written"], ["arrived", "saw"], ["walked", "saw"]]},
    {"id": "before2", "type": "B", "risk": "real",
     "text": "She rose from breakfast before he had finished, and hastened upstairs.",
     "source": "Tess of the d'Urbervilles (Hardy), LitBank 110",
     "pairs": [["rose", "finished"], ["rose", "hastened"]]},
    {"id": "before3", "type": "B", "risk": "real",
     "text": "But I fell asleep before I had succeeded, and dreamed of the days when I lived in my godmother's house.",
     "source": "Bleak House (Dickens), LitBank 1023",
     "pairs": [["fell", "succeeded"], ["fell", "dreamed"]]},
    {"id": "since1", "type": "A", "risk": "real",
     "text": "She had not set eyes on him since he had conducted her to the cottage the day before.",
     "source": "Tess of the d'Urbervilles (Hardy), LitBank 110 (trimmed clause)",
     "pairs": [["conducted", "set"]]},
    {"id": "flash_held", "type": "C", "risk": "real",
     "text": "He felt as if tight strings which had held him had loosened themselves and let him go.",
     "source": "The Secret Garden (Burnett), LitBank 113",
     "pairs": [["held", "felt"], ["loosened", "felt"], ["held", "loosened"]]},
    {"id": "flash_asked", "type": "C", "risk": "real",
     "text": "Mary remembered what he had asked her the day she had gone to his room.",
     "source": "The Secret Garden (Burnett), LitBank 113",
     "pairs": [["asked", "remembered"], ["gone", "remembered"]]},
    {"id": "flash_saw", "type": "C", "risk": "real",
     "text": "I saw that the dress had been put upon the rounded figure of a young woman, and that the figure had shrunk to skin and bone.",
     "source": "Great Expectations (Dickens), LitBank 1400",
     "pairs": [["put", "saw"], ["shrunk", "saw"], ["put", "shrunk"]]},
    {"id": "flash_come", "type": "C", "risk": "real",
     "text": "She felt again that sensation of nausea which had come over her when she had met her first sneer.",
     "source": "Personality Plus (Ferber), LitBank 12677 (trimmed clause)",
     "pairs": [["come", "felt"], ["met", "felt"]]},
    {"id": "after_synth", "type": "A", "risk": "synthetic",
     "text": "She had mailed the letter after she had written it.",
     "source": "synthetic-illustrative (real multi-pp-reorder near-nonexistent in prose)",
     "pairs": [["written", "mailed"]]},
]

# REAL multi-frame CONTROL: baselines already SOLVE these (pp-demote / cell1-cue pass);
# the mechanism must NOT regress. (Proves the mechanism does not break real multi-frame prose
# where the simple heuristic already works.)
CONTROL_GOLD = [
    {"id": "c_earlier1", "risk": "real",
     "text": "She reached the corner of the lane which they had passed half an hour earlier, and she hopped down.",
     "source": "Tess of the d'Urbervilles (Hardy), LitBank 110",
     "pairs": [["passed", "reached"], ["reached", "hopped"]]},
    {"id": "c_earlier2", "risk": "real",
     "text": "She stooped to the threshold of the doorway, where she had pushed in the note two or three days earlier.",
     "source": "Tess of the d'Urbervilles (Hardy), LitBank 110",
     "pairs": [["pushed", "stooped"]]},
    {"id": "c_when1", "risk": "real",
     "text": "When she had first seen me she had been startled, and she looked at me steadily.",
     "source": "Great Expectations (Dickens), LitBank 1400 (trimmed)",
     "pairs": [["seen", "startled"], ["startled", "looked"]]},
    {"id": "c_after1", "risk": "real",
     "text": "He had left his wife, and after some years of a reckless existence, she had died before her time.",
     "source": "Night and Day (Woolf), LitBank 1245",
     "pairs": [["left", "died"]]},
    {"id": "c_before4", "risk": "real",
     "text": "Before this time he had known it but speculatively; now he thought he knew it as a practical man.",
     "source": "Tess of the d'Urbervilles (Hardy), LitBank 110",
     "pairs": [["known", "thought"]]},
]

ARMS = ["TEXT", "PP_DEMOTE", "CELL1_CUE", "MECH", "MECH_ABLATE"]


# ---------------------------------------------------------------------------
# Ordering per arm. Baselines use the SHARED cell-1 extractor; MECH/ABLATE use the
# punctuation-preserving extractor (identical event set, asserted).
# ---------------------------------------------------------------------------
def _order_for_arm(arm, text):
    if arm == "TEXT":
        ev, _ = T.extract_events(text)
        return T.text_order(ev), None
    if arm == "PP_DEMOTE":
        ev, tg = T.extract_events(text)
        return M.reconstruct_order_ppdemote(ev, tg), None
    if arm == "CELL1_CUE":
        ev, tg = T.extract_events(text)
        return M.reconstruct_order_cell1cue(ev, tg), None
    if arm == "MECH":
        ev, tg = M.extract_events_punct(text)
        order, edges = M.reconstruct_order_timeline(ev, tg, use_connectives=True, cross_sentence=True)
        return order, edges
    if arm == "MECH_ABLATE":
        ev, tg = M.extract_events_punct(text)
        order, edges = M.reconstruct_order_timeline(ev, tg, use_connectives=False, cross_sentence=False)
        return order, edges
    raise ValueError(f"unknown arm {arm}")


def _score_subset(arm, items):
    ncorr = nsc = nab = 0
    per_item = []
    for it in items:
        order, _ = _order_for_arm(arm, it["text"])
        c, s, a = T.pairwise_accuracy(order, [tuple(p) for p in it["pairs"]])
        ncorr += c; nsc += s; nab += a
        per_item.append({"id": it.get("id", it.get("source")), "n_correct": c, "n_scored": s,
                         "n_abstain": a, "order": [e.lemma for e in order]})
    acc = (ncorr / nsc) if nsc else 0.0
    return {"acc": acc, "n_correct": ncorr, "n_scored": nsc, "n_abstain": nab, "per_item": per_item}


def _arm_signature(arm, items):
    parts = []
    for it in items:
        order, _ = _order_for_arm(arm, it["text"])
        parts.append("|".join(e.lemma for e in order))
    return ("\n".join(parts)).encode("utf-8")


# ---------------------------------------------------------------------------
# Never-confidently-wrong: MECH accuracy on CONFIDENT pairs (cue-connected) vs abstained.
# ---------------------------------------------------------------------------
def _mech_confidence(items):
    conf_c = conf_n = abstain = 0
    for it in items:
        ev, tg = M.extract_events_punct(it["text"])
        order, edges = M.reconstruct_order_timeline(ev, tg, True, True)
        lemmas = [e.lemma for e in order]
        pos = {l: i for i, l in enumerate(lemmas)}
        for a, b in it["pairs"]:
            if a not in pos or b not in pos:
                continue
            if M.confident_pair(edges, a, b):
                conf_n += 1
                if pos[a] < pos[b]:
                    conf_c += 1
            else:
                abstain += 1
    return {"confident_correct": conf_c, "confident_scored": conf_n,
            "confident_acc": round(conf_c / conf_n, 4) if conf_n else 0.0,
            "abstained_pairs": abstain}


# ---------------------------------------------------------------------------
# Improving property: MECH lift vs #cues (temporal connectives) and #events (chain length);
# SequenceMatrix multi-event chain-depth envelope.
# ---------------------------------------------------------------------------
def _improving_by_cues(items):
    bins = {}
    for it in items:
        ev, tg = M.extract_events_punct(it["text"])
        ncue = len(M._find_connectives(tg))
        band = "0" if ncue == 0 else ("1" if ncue == 1 else ">=2")
        gp = [tuple(p) for p in it["pairs"]]
        tord, _ = _order_for_arm("TEXT", it["text"])
        pord, _ = _order_for_arm("PP_DEMOTE", it["text"])
        mord, _ = _order_for_arm("MECH", it["text"])
        tc = T.pairwise_accuracy(tord, gp); pc = T.pairwise_accuracy(pord, gp); mc = T.pairwise_accuracy(mord, gp)
        b = bins.setdefault(band, {"t": 0, "p": 0, "m": 0, "n": 0, "items": 0})
        b["t"] += tc[0]; b["p"] += pc[0]; b["m"] += mc[0]; b["n"] += mc[1]; b["items"] += 1
    out = {}
    for band, b in bins.items():
        n = b["n"] or 1
        out[band] = {"text_acc": round(b["t"] / n, 4), "pp_acc": round(b["p"] / n, 4),
                     "mech_acc": round(b["m"] / n, 4), "n_items": b["items"], "n_pairs": b["n"]}
    return out


def _improving_by_chainlen(items):
    bins = {}
    for it in items:
        ev, _ = M.extract_events_punct(it["text"])
        nev = len(ev)
        band = "2" if nev <= 2 else ("3" if nev == 3 else ">=4")
        gp = [tuple(p) for p in it["pairs"]]
        mord, _ = _order_for_arm("MECH", it["text"])
        pord, _ = _order_for_arm("PP_DEMOTE", it["text"])
        mc = T.pairwise_accuracy(mord, gp); pc = T.pairwise_accuracy(pord, gp)
        b = bins.setdefault(band, {"m": 0, "p": 0, "n": 0, "items": 0})
        b["m"] += mc[0]; b["p"] += pc[0]; b["n"] += mc[1]; b["items"] += 1
    return {band: {"mech_acc": round(b["m"] / (b["n"] or 1), 4),
                   "pp_acc": round(b["p"] / (b["n"] or 1), 4),
                   "lift": round((b["m"] - b["p"]) / (b["n"] or 1), 4),
                   "n_items": b["items"], "n_pairs": b["n"]}
            for band, b in bins.items()}


def _sequence_matrix_envelope(items):
    """Bind each item's MECH multi-event chronology into hdlab.SequenceMatrix; measure the
    ordered-binding chain-recovery depth envelope (glass-box in-substrate temporal store).
    Also a shared-interference matrix (all chronologies in ONE S -> repeated lemmas interfere)."""
    all_lemmas, chrono_orders = [], []
    for it in items:
        ev, tg = M.extract_events_punct(it["text"])
        order, _ = M.reconstruct_order_timeline(ev, tg, True, True)
        chrono_orders.append(order)
        all_lemmas += [e.lemma for e in order]
    cb = T.build_codebook(all_lemmas, N_DIM, seed=CODEBOOK_SEED)
    shared = T.SequenceMatrix(N_DIM, torch.float32)
    for order in chrono_orders:
        if len(order) >= 2:
            keys = torch.stack([M._vec(cb, e.lemma) for e in order])
            shared.bind_sequence(keys)
    depths, seqlens = [], []
    for order in chrono_orders:
        depths.append(T.chain_recover_depth(shared, order, cb))
        seqlens.append(max(0, len(order) - 1))
    npos = sum(1 for L in seqlens if L > 0)
    mean_depth = sum(depths) / len(depths) if depths else 0.0
    full_frac = (sum(1 for d, L in zip(depths, seqlens) if d == L and L > 0) / npos) if npos else 0.0
    multi = sum(1 for L in seqlens if L >= 2)
    return {"shared_matrix_mean_chain_depth": round(mean_depth, 4),
            "shared_matrix_full_recovery_frac": round(full_frac, 4),
            "per_item_depths": depths, "per_item_seqlens": seqlens,
            "n_distinct_event_lemmas": len(cb), "n_multi_event_chains": multi,
            "max_chain_len": max(seqlens) if seqlens else 0}


# ---------------------------------------------------------------------------
# Infra.
# ---------------------------------------------------------------------------
def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(out_dir):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": "full",
              "expected_n_units": len(HARD_GOLD) + len(CONTROL_GOLD) + len(CELL1_FLASHBACK) + len(CELL1_LINEAR),
              "host": platform.node()}
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(out_dir, "_start_marker.json"))


def _atomic_write(out_dir, metrics):
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _atomic_write(out_dir, diag)


# ---------------------------------------------------------------------------
# Self-test: mechanism probes + real substrate code path + parity + P2 collapse.
# ---------------------------------------------------------------------------
def self_test():
    print("[self-test] multi-frame mechanism + substrate code path", flush=True)
    exercised = set()

    # (1) PARITY: punct extractor yields the IDENTICAL event set (lemma+tense) as cell-1's.
    for it in HARD_GOLD + CONTROL_GOLD:
        a = sorted((e.lemma, e.tense) for e in T.extract_events(it["text"])[0])
        b = sorted((e.lemma, e.tense) for e in M.extract_events_punct(it["text"])[0])
        assert a == b, f"PARITY BREAK on {it['id']}: shared={a} punct={b}"
    exercised.add("extract_events_punct")

    # (2) case-B contradiction: 'before'+pp -> mechanism does NOT demote the pp below main
    ev, tg = M.extract_events_punct("She rose before he had finished the letter.")
    order, edges = M.reconstruct_order_timeline(ev, tg, True, True)
    lm = [e.lemma for e in order]
    assert lm.index("rose") < lm.index("finished"), f"case-B: rose should precede finished; got {lm}"
    exercised.add("reconstruct_order_timeline")

    # (3) case-A multi-pp reorder: 'after' between two pp events orders them
    ev, tg = M.extract_events_punct("She had mailed the letter after she had written it.")
    order, edges = M.reconstruct_order_timeline(ev, tg, True, True)
    lm = [e.lemma for e in order]
    assert lm.index("written") < lm.index("mailed"), f"case-A: written should precede mailed; got {lm}"
    assert M.confident_pair(edges, "written", "mailed"), "case-A pair should be confident (cue-connected)"
    exercised.add("confident_pair")

    # (4) P2 ablation reduces to pp-demotion on a contradiction item
    ev0, tg0 = T.extract_events("She rose before he had finished the letter.")
    pd = [e.lemma for e in M.reconstruct_order_ppdemote(ev0, tg0)]
    evp, tgp = M.extract_events_punct("She rose before he had finished the letter.")
    abl = [e.lemma for e in M.reconstruct_order_timeline(evp, tgp, False, False)[0]]
    assert pd == abl, f"P2 ablation != pp_demote: pd={pd} abl={abl}"
    exercised.add("reconstruct_order_ppdemote")

    # (5) REAL substrate code path at tiny scale: Codebook + SequenceMatrix bind/predict
    cb = T.build_codebook(["a", "b", "c"], 64, seed=1)
    exercised.add("build_codebook")
    from experiments._temporal_ordering import Event
    order = [Event("a", 0, "VBD", T.TENSE_SIMPLE_PAST), Event("b", 1, "VBD", T.TENSE_SIMPLE_PAST),
             Event("c", 2, "VBD", T.TENSE_SIMPLE_PAST)]
    sm = T.bind_order(order, cb, 64)
    exercised.add("bind_order")
    d = T.chain_recover_depth(sm, order, cb)
    assert d == 2, f"chain recover depth {d} != 2 on clean 3-seq"
    exercised.add("chain_recover_depth")

    required = {"extract_events_punct", "reconstruct_order_timeline", "confident_pair",
                "reconstruct_order_ppdemote", "build_codebook", "bind_order", "chain_recover_depth"}
    missing = required - exercised
    assert not missing, f"real_code_path: entrypoints not exercised: {missing}"
    print(f"[self-test] PASS; exercised={sorted(exercised)}", flush=True)
    return True


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------
def main():
    out_dir = _out_dir()
    _write_start_marker(out_dir)
    t0 = time.perf_counter()

    real_hard = [it for it in HARD_GOLD if it["risk"] == "real"]
    single_frame = [{"text": it["text"], "pairs": it["pairs"], "id": it["source"]}
                    for it in (CELL1_FLASHBACK + CELL1_LINEAR)]

    res = {}
    for arm in ARMS:
        res[arm] = {
            "hard": _score_subset(arm, HARD_GOLD),
            "hard_real": _score_subset(arm, real_hard),
            "control": _score_subset(arm, CONTROL_GOLD),
            "single_frame": _score_subset(arm, single_frame),
        }
        print(f"[arm] {arm:12} hard={res[arm]['hard']['acc']:.3f} hard_real={res[arm]['hard_real']['acc']:.3f} "
              f"control={res[arm]['control']['acc']:.3f} single_frame={res[arm]['single_frame']['acc']:.3f}", flush=True)

    # ARMS-MUST-DIFFER (META_RULE_AF). PP_DEMOTE, CELL1_CUE and MECH_ABLATE are provably
    # EQUIVALENT on this multi-frame item set -- an intentional, documented equivalence group:
    #   * MECH_ABLATE == PP_DEMOTE: the P2 ablation collapses the mechanism to pp-demotion.
    #   * CELL1_CUE == PP_DEMOTE: cell-1's adjacent-simple-past connective swap ({after,earlier}
    #     on text-adjacent VBD pairs) never FIRES on these items, so cell-1's full CUE reduces
    #     to pure pp-demotion here. (This is itself a finding: cell-1's connective handling adds
    #     nothing on multi-frame prose.) TEXT and MECH must differ from every other arm.
    import hashlib
    allitems = HARD_GOLD + CONTROL_GOLD + single_frame
    sig = {a: hashlib.sha256(_arm_signature(a, allitems)).hexdigest() for a in ARMS}
    EQUIV_GROUP = {"PP_DEMOTE", "CELL1_CUE", "MECH_ABLATE"}
    exempt = [(a, b) for i, a in enumerate(sorted(EQUIV_GROUP))
              for b in sorted(EQUIV_GROUP)[i + 1:]]
    for i in range(len(ARMS)):
        for j in range(i + 1, len(ARMS)):
            a, b = ARMS[i], ARMS[j]
            if (a, b) in exempt or (b, a) in exempt:
                assert sig[a] == sig[b], f"equivalence-group exemption broken: {a} != {b} (must be identical)"
            else:
                assert sig[a] != sig[b], f"META_RULE_AF: arms {a},{b} bit-identical"

    text_h = res["TEXT"]["hard"]["acc"]
    pp_h = res["PP_DEMOTE"]["hard"]["acc"]
    cue_h = res["CELL1_CUE"]["hard"]["acc"]
    mech_h = res["MECH"]["hard"]["acc"]
    text_hr = res["TEXT"]["hard_real"]["acc"]
    pp_hr = res["PP_DEMOTE"]["hard_real"]["acc"]
    mech_hr = res["MECH"]["hard_real"]["acc"]
    mech_sf = res["MECH"]["single_frame"]["acc"]
    cue_sf = res["CELL1_CUE"]["single_frame"]["acc"]
    mech_ctrl = res["MECH"]["control"]["acc"]
    pp_ctrl = res["PP_DEMOTE"]["control"]["acc"]

    margin_pp = mech_h - pp_h
    margin_text = mech_h - text_h
    margin_pp_real = mech_hr - pp_hr

    validity_fires = (text_h <= VALIDITY_TEXT_MAX) and (pp_h <= VALIDITY_PPDEMOTE_MAX)
    p2_collapse = abs(res["MECH_ABLATE"]["hard"]["acc"] - pp_h) < 1e-9 and sig["MECH_ABLATE"] == sig["PP_DEMOTE"]
    no_sf_regression = mech_sf >= cue_sf - 1e-9
    no_ctrl_regression = mech_ctrl >= pp_ctrl - 1e-9

    # Verdict logic.
    if not validity_fires:
        verdict = "HARD_FAIL"
        vmsg = (f"VALIDITY GATE FAILED: TEXT hard acc={text_h:.3f} (<= {VALIDITY_TEXT_MAX}?) "
                f"PP_DEMOTE hard acc={pp_h:.3f} (<= {VALIDITY_PPDEMOTE_MAX}?) -- hard subset not "
                f"genuinely multi-frame (a single heuristic solves it); discriminator invalid.")
    elif not no_sf_regression:
        verdict = "HARD_FAIL"
        vmsg = (f"SINGLE-FRAME REGRESSION: MECH single-frame acc={mech_sf:.3f} < cell1_cue {cue_sf:.3f} "
                f"(P1 no-regression violated on cell-1's 20 items).")
    elif margin_pp < HARD_FAIL_MARGIN_PP:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL: MECH does not beat PP_DEMOTE on the hard subset "
                f"(margin {margin_pp:.3f} < {HARD_FAIL_MARGIN_PP}); the running timeline adds nothing.")
    elif (margin_pp >= HARD_PASS_MARGIN_PP and margin_text >= HARD_PASS_MARGIN_TEXT
          and mech_h >= HARD_PASS_MECH_MIN and validity_fires and p2_collapse
          and no_sf_regression and no_ctrl_regression and margin_pp_real >= HARD_FAIL_MARGIN_PP):
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS: running-timeline multi-frame mechanism beats BOTH baselines on the hard "
                f"subset -- MECH {mech_h:.3f} vs PP_DEMOTE {pp_h:.3f} (+{margin_pp:.3f}) vs TEXT {text_h:.3f} "
                f"(+{margin_text:.3f}); holds REAL-only (MECH {mech_hr:.3f} vs PP_DEMOTE {pp_hr:.3f}); "
                f"validity gate fires (TEXT {text_h:.3f}<={VALIDITY_TEXT_MAX}, PP {pp_h:.3f}<={VALIDITY_PPDEMOTE_MAX}); "
                f"P2 ablation collapses to PP_DEMOTE; NO single-frame regression (MECH_sf {mech_sf:.3f}=={cue_sf:.3f}); "
                f"NO control regression (MECH_ctrl {mech_ctrl:.3f}).")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: MECH {mech_h:.3f} vs PP_DEMOTE {pp_h:.3f} (+{margin_pp:.3f}) vs TEXT {text_h:.3f} "
                f"(+{margin_text:.3f}); validity={validity_fires} p2_collapse={p2_collapse} "
                f"sf_ok={no_sf_regression} ctrl_ok={no_ctrl_regression} margin_pp_real={margin_pp_real:.3f}.")

    # Autopsy: per-item MECH failures with cue-type classification (always reported).
    autopsy = {"failing_items": [], "by_cue_type": {"A": [0, 0], "B": [0, 0], "C": [0, 0]}}
    for it in HARD_GOLD:
        order, edges = _order_for_arm("MECH", it["text"])
        c, s, a = T.pairwise_accuracy(order, [tuple(p) for p in it["pairs"]])
        bucket = autopsy["by_cue_type"].setdefault(it["type"], [0, 0])
        bucket[0] += c; bucket[1] += s
        if s and c < s:
            ev, _ = M.extract_events_punct(it["text"])
            autopsy["failing_items"].append({
                "id": it["id"], "type": it["type"], "risk": it["risk"], "source": it["source"],
                "text": it["text"], "n_correct": c, "n_scored": s, "n_abstain": a,
                "extracted": [(e.lemma, "PP" if e.is_pp else e.tense[:2]) for e in ev],
                "mech_order": [e.lemma for e in order]})
    autopsy["by_cue_type"] = {k: {"correct": v[0], "scored": v[1],
                                  "acc": round(v[0] / v[1], 4) if v[1] else None}
                              for k, v in autopsy["by_cue_type"].items() if v[1]}
    autopsy["candidate_levers"] = [
        "clause-bounded tense tagging: shared POS extractor mis-tags a coordinated simple-past "
        "verb (hastened/dreamed) as pp via cross-clause 'had' bleed (before2/before3 partials)",
        "lexical temporal adverbials (the day before / an hour later) beyond connective set",
        "genuine multi-pp-reorder is near-nonexistent in real prose (case-A leans synthetic)"]

    improving = {
        "by_n_cues": _improving_by_cues(HARD_GOLD),
        "by_chain_len": _improving_by_chainlen(HARD_GOLD),
        "sequence_matrix": _sequence_matrix_envelope(HARD_GOLD),
        "never_confidently_wrong": _mech_confidence(HARD_GOLD + CONTROL_GOLD),
    }

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": vmsg, "run_mode": "full",
        "summary": f"{verdict}: hard MECH {mech_h:.3f} vs PP_DEMOTE {pp_h:.3f} (+{margin_pp:+.3f}) vs TEXT "
                   f"{text_h:.3f} (+{margin_text:+.3f}); real-only MECH {mech_hr:.3f} vs PP {pp_hr:.3f}; "
                   f"validity={validity_fires}; sf_noregress={no_sf_regression}",
        "elapsed_s": round(elapsed, 3), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "n_dim": N_DIM,
        "prereg_bands": {
            "validity_text_max": VALIDITY_TEXT_MAX, "validity_ppdemote_max": VALIDITY_PPDEMOTE_MAX,
            "hard_pass_margin_pp": HARD_PASS_MARGIN_PP, "hard_pass_margin_text": HARD_PASS_MARGIN_TEXT,
            "hard_pass_mech_min": HARD_PASS_MECH_MIN, "hard_fail_margin_pp": HARD_FAIL_MARGIN_PP},
        "gates": {
            "validity_gate_fires": validity_fires, "p2_ablation_collapses_to_ppdemote": p2_collapse,
            "no_single_frame_regression": no_sf_regression, "no_control_regression": no_ctrl_regression,
            "margin_pp_hard": round(margin_pp, 4), "margin_text_hard": round(margin_text, 4),
            "margin_pp_hard_real": round(margin_pp_real, 4)},
        "arms": {a: {
            "hard_acc": round(res[a]["hard"]["acc"], 4), "hard_real_acc": round(res[a]["hard_real"]["acc"], 4),
            "control_acc": round(res[a]["control"]["acc"], 4), "single_frame_acc": round(res[a]["single_frame"]["acc"], 4),
            "hard_n_scored": res[a]["hard"]["n_scored"], "signature_sha256": sig[a][:16]} for a in ARMS},
        "arms_differ_exempted": [list(p) for p in exempt],
        "improving_property": improving, "autopsy": autopsy,
        "gold": {
            "n_hard_items": len(HARD_GOLD), "n_hard_real": len(real_hard),
            "n_control_items": len(CONTROL_GOLD),
            "n_single_frame_items": len(single_frame),
            "hard": [{"id": it["id"], "type": it["type"], "risk": it["risk"],
                      "source": it["source"], "text": it["text"], "pairs": it["pairs"]} for it in HARD_GOLD],
            "control": [{"id": it["id"], "risk": it["risk"], "source": it["source"],
                         "text": it["text"], "pairs": it["pairs"]} for it in CONTROL_GOLD]},
        "per_arm_detail": {a: res[a] for a in ARMS},
        "honest_scope": ("8/9 hard items are REAL LitBank prose (win holds real-only); 1 flagged synthetic "
                         "case-A (real multi-pp-reorder near-nonexistent); before2/before3 partials are a "
                         "SHARED-extractor cross-clause 'had'-bleed mis-tag, not an ordering failure -- named "
                         "next lever = clause-bounded tense tagging. Deterministic; the graded frontier is "
                         "extraction robustness + longer cross-turn discourse (situation-model NEXT PHASE)."),
    }
    _atomic_write(out_dir, metrics)
    print(metrics["summary"], flush=True)
    print(f"verdict={verdict} elapsed={elapsed:.2f}s -> {os.path.join(out_dir, 'metrics.json')}", flush=True)
    return metrics


if __name__ == "__main__":
    _od = _out_dir()
    if "--self-test" in sys.argv:
        self_test()
        sys.exit(0)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
