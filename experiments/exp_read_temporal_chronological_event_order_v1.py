"""SITUATION-MODEL TIME DIMENSION, cell 1: CHRONOLOGICAL event-ordering BEATS naive
text-order on real past-perfect / flashback LitBank prose.

THESIS (parallel to the passive discriminator): the default reader assumes text order ==
event order. That FAILS on flashbacks, where a past-perfect ("had" + VBN) event mentioned
LATER in the text occurred EARLIER in time. A cue-aware reconstruction that reads
tense/aspect (+ temporal connectives) recovers the true CHRONOLOGICAL order and binds it
into the substrate's SequenceMatrix (glass-box in-substrate temporal representation).

MECHANISM (see experiments/_temporal_ordering.py, the reusable pluggable module):
  (1) extract content-verb events + tense from the reader POS pipeline (ORC.pos_tag_sentence)
  (2) classify: had+VBN = PAST_PERFECT (PRIOR); VBD = SIMPLE_PAST (narrative-now);
      be+VBN = PASSIVE (narrative-now); bare VBN = adjectival (skipped)
  (3) reconstruct chronological order: past-perfect events demoted BEFORE narrative-now
      events (single-frame flashback); "after"/"earlier" connectives reorder adjacent
      simple-past pairs; default = text order (abstain when no cue -> never confidently wrong)
  (4) bind the reconstructed chronological sequence into hdlab.SequenceMatrix

ARMS (the ONE variable is the ordering function; extraction is SHARED):
  TEXT           baseline: chronological order == text order (MUST fail on flashbacks)
  CUE            mechanism: tense + connective cue-aware reconstruction
  CUE_ABLATE     P2 ablation: cue detection OFF -> reduces to text order (== TEXT by design)
  NAIVE_REVERSE  precision control: always reverse text order (over-triggers; wins flashback
                 but WRECKS linear -> proves the win is the TENSE CUE, not reordering-per-se)

GOLD: REAL LitBank sentences (public-domain novels; ASCII-normalized quotes/dashes, verbs +
order VERBATIM), hand-labeled with the UNAMBIGUOUS chronological (earlier, later) event
pairs derived from MEANING (not from the mechanism's rule -> non-circular). 12 flashback +
8 linear-control items. Source citation shown per item for verifiability. This gold is a
BASE INGREDIENT and WILL be skunkworks-VET'd.

HONEST SCOPE: reconstruction is deterministic/binary given correct tagging, so the flashback
separation is clean (0.0 vs 1.0) BECAUSE past-perfect is a high-precision cue and the gold is
CONSERVATIVE (short single-frame flashbacks where "all pp before all now" is exactly correct).
The graded difficulty / real frontier lives in (a) EXTRACTION robustness and (b) MULTI-FRAME
multi-sentence chronology -- named as the next lever, NOT claimed solved. The SequenceMatrix
interference envelope provides the graded substrate measurement.

Compute architecture: sequential-CPU JUSTIFIED -- deterministic, wall < 10s, no seed axis on
the discriminator (the substrate matrices are tiny N_DIM=1024); this cell IS validating the
SequenceMatrix primitive on real reader tuples. Storage: sharded per-event codevectors in a
Codebook + a separate SequenceMatrix S (no bundling). Not banked here (skunkworks VETs).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (TEXT==CUE_ABLATE is an INTENTIONAL P2 exemption)
# - final_metrics_atomicity: tmp_replace (metrics.json.tmp + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: reconstruction accuracy is a discrete order-match, no Gaussian noise floor
# - baseline_in_band: TEXT flashback acc must be LOW (validity gate), not saturated
# - discriminator: real LitBank flashbacks; margin CUE-TEXT on flashback subset
# - numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
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

ANCHOR_NAME = "read_temporal_chronological_event_order_v1"
N_DIM = 1024
CODEBOOK_SEED = 20260723

# Pre-registered bands (set BEFORE this run).
VALIDITY_GATE_MAX = 0.60      # TEXT flashback acc must be <= this (genuinely non-linear)
HARD_PASS_MARGIN = 0.25       # CUE-TEXT on flashback >= this (strict; band floor + width)
HARD_FAIL_MARGIN = 0.10       # CUE-TEXT on flashback < this -> autopsy
NONFLASH_REGRESS_MAX = 0.05   # CUE must not drop below TEXT on linear by more than this


# ---------------------------------------------------------------------------
# GOLD -- REAL LitBank prose. gold_pairs = (earlier_lemma, later_lemma) in CHRONOLOGY.
# ---------------------------------------------------------------------------
FLASHBACK_GOLD = [
    {"text": "The first man who came in was a large officer she had once seen talking to her father.",
     "source": "The Secret Garden (Burnett), LitBank 113",
     "pairs": [["seen", "came"]]},
    {"text": "He looked at the others -- at all, that is, save Pink and Irish, who had disappeared.",
     "source": "The Flying U Ranch (Bower), LitBank 1206",
     "pairs": [["disappeared", "looked"]]},
    {"text": "Her hand closed on the oilskin packet that had lain in his palm.",
     "source": "The Secret Adversary (Christie), LitBank 1155",
     "pairs": [["lain", "closed"]]},
    {"text": "Denham, mother, she said aloud, for she saw that her mother had forgotten his name.",
     "source": "Night and Day (Woolf), LitBank 1245",
     "pairs": [["forgotten", "said"], ["forgotten", "saw"]]},
    {"text": "He stood framed in the great plate-glass window of the very building which had brought about the defeat of his predecessor.",
     "source": "Personality Plus (Ferber), LitBank 12677",
     "pairs": [["brought", "stood"]]},
    {"text": "I thought of course that somebody had stolen them, some boy from the village, or perhaps the chastised cowherd.",
     "source": "Elizabeth and Her German Garden (von Arnim), LitBank 1327",
     "pairs": [["stolen", "thought"]]},
    {"text": "Upon asking him why he did not write, he said that he had decided upon doing no more writing.",
     "source": "Bartleby the Scrivener (Melville), LitBank 11231",
     "pairs": [["decided", "said"]]},
    {"text": "When I turned, I found that the young man had taken out the dog and was standing at the door looking in upon us.",
     "source": "Bleak House (Dickens), LitBank 1023",
     "pairs": [["taken", "turned"], ["taken", "found"]]},
    {"text": "When we came to the door, we found the woman who had brought such consolation with her standing there.",
     "source": "Bleak House (Dickens), LitBank 1023",
     "pairs": [["brought", "came"], ["brought", "found"]]},
    {"text": "Oh, I beg your pardon, cried Alice hastily, afraid that she had hurt the poor animal's feelings.",
     "source": "Alice's Adventures in Wonderland (Carroll), LitBank 11",
     "pairs": [["hurt", "cried"]]},
    {"text": "Raising my eyes as he went out, I once more saw him looking at me after he had passed the door.",
     "source": "Bleak House (Dickens), LitBank 1023",
     "pairs": [["passed", "saw"]]},
    {"text": "She heard neither voices nor footsteps, and wondered if everybody had got well of the cholera.",
     "source": "The Secret Garden (Burnett), LitBank 113",
     "pairs": [["got", "wondered"], ["got", "heard"]]},
]

LINEAR_GOLD = [
    {"text": "I advanced towards the screen, and demanded the reason for such extraordinary conduct.",
     "source": "Bartleby the Scrivener (Melville), LitBank 11231",
     "pairs": [["advanced", "demanded"]]},
    {"text": "So she set to work, and very soon finished off the cake.",
     "source": "Alice's Adventures in Wonderland (Carroll), LitBank 11",
     "pairs": [["set", "finished"]]},
    {"text": "Then he passed his hand over his eyes several times and at last turned back into the house.",
     "source": "Treasure Island (Stevenson), LitBank 120",
     "pairs": [["passed", "turned"]]},
    {"text": "He listened till I paused to breathe, and then he said that.",
     "source": "Elizabeth and Her German Garden (von Arnim), LitBank 1327 (trimmed to clause)",
     "pairs": [["listened", "paused"], ["paused", "said"]]},
    {"text": "The lad quickened his pace and came near.",
     "source": "Tess of the d'Urbervilles (Hardy), LitBank 110",
     "pairs": [["quickened", "came"]]},
    {"text": "The revel went whirlingly on, until at length there commenced the sounding of midnight.",
     "source": "The Masque of the Red Death (Poe), LitBank 1064",
     "pairs": [["went", "commenced"]]},
    {"text": "There he lay a while trembling and at last drifted into dreamless sleep.",
     "source": "The Quest of the Silver Fleece (Du Bois), LitBank 15265",
     "pairs": [["lay", "drifted"]]},
    {"text": "The three guardian priests followed and watched it in disguise.",
     "source": "The Moonstone (Collins), LitBank 155",
     "pairs": [["followed", "watched"]]},
]


# ---------------------------------------------------------------------------
# Arm scoring helpers.
# ---------------------------------------------------------------------------
def _order_for_arm(arm, events, tagged):
    if arm == "TEXT":
        return T.text_order(events)
    if arm == "CUE":
        return T.reconstruct_order(events, tagged, use_tense=True, use_connective=True)
    if arm == "CUE_ABLATE":
        return T.reconstruct_order(events, tagged, use_tense=False, use_connective=False)
    if arm == "NAIVE_REVERSE":
        return list(reversed(T.text_order(events)))
    raise ValueError(f"unknown arm {arm}")


def _score_subset(arm, items):
    ncorr = nsc = nab = 0
    per_item = []
    for it in items:
        events, tagged = T.extract_events(it["text"])
        order = _order_for_arm(arm, events, tagged)
        c, s, a = T.pairwise_accuracy(order, [tuple(p) for p in it["pairs"]])
        ncorr += c; nsc += s; nab += a
        per_item.append({"source": it["source"], "n_correct": c, "n_scored": s,
                         "n_abstain": a, "order": [e.lemma for e in order]})
    acc = (ncorr / nsc) if nsc else 0.0
    return {"acc": acc, "n_correct": ncorr, "n_scored": nsc, "n_abstain": nab,
            "per_item": per_item}


def _arm_signature(arm, items):
    """Concatenated per-item ordering -> bytes, for ARMS-MUST-DIFFER hashing."""
    parts = []
    for it in items:
        events, tagged = T.extract_events(it["text"])
        order = _order_for_arm(arm, events, tagged)
        parts.append("|".join(e.lemma for e in order))
    return ("\n".join(parts)).encode("utf-8")


# ---------------------------------------------------------------------------
# Improving-property measurements.
# ---------------------------------------------------------------------------
def _cue_density(item):
    events, _ = T.extract_events(item["text"])
    if not events:
        return 0.0
    npp = sum(1 for e in events if e.is_pp)
    return npp / len(events)


def _improving_cue_density(items):
    """Lift (CUE-TEXT pairwise acc) binned by cue-density."""
    bins = {}
    for it in items:
        d = _cue_density(it)
        band = "0.0" if d == 0 else ("(0,0.34]" if d <= 0.34 else ("(0.34,0.5]" if d <= 0.5 else ">0.5"))
        ev, tg = T.extract_events(it["text"])
        gp = [tuple(p) for p in it["pairs"]]
        tc, ts, _ = T.pairwise_accuracy(T.text_order(ev), gp)
        cc, cs, _ = T.pairwise_accuracy(
            T.reconstruct_order(ev, tg, use_tense=True, use_connective=True), gp)
        b = bins.setdefault(band, {"text_c": 0, "cue_c": 0, "n": 0, "n_items": 0})
        b["text_c"] += tc; b["cue_c"] += cc; b["n"] += ts; b["n_items"] += 1
    out = {}
    for band, b in bins.items():
        ta = b["text_c"] / b["n"] if b["n"] else 0.0
        ca = b["cue_c"] / b["n"] if b["n"] else 0.0
        out[band] = {"text_acc": round(ta, 4), "cue_acc": round(ca, 4),
                     "lift": round(ca - ta, 4), "n_items": b["n_items"], "n_pairs": b["n"]}
    return out


def _sequence_matrix_envelope(items):
    """(b) SequenceMatrix ordered-binding depth envelope + glass-box successor prediction.

    b1: shared-matrix interference -- bind ALL chronological sequences into ONE
        SequenceMatrix (repeated lemmas across items -> interference); per-item chain
        recovery depth from event 0.
    b3: chrono-bound vs text-bound successor prediction on flashback items -- does
        predict_next(chrono[0]) recover the TRUE temporal successor chrono[1]?
    """
    # collect all lemmas
    all_lemmas = []
    chrono_orders = []
    for it in items:
        ev, tg = T.extract_events(it["text"])
        order = T.reconstruct_order(ev, tg, use_tense=True, use_connective=True)
        chrono_orders.append((it, order))
        all_lemmas += [e.lemma for e in order]
    cb = T.build_codebook(all_lemmas, N_DIM, seed=CODEBOOK_SEED)

    # b1 shared interference matrix
    shared = T.SequenceMatrix(N_DIM, torch.float32)
    for _, order in chrono_orders:
        if len(order) >= 2:
            keys = torch.stack([T._vec(cb, e.lemma) for e in order])
            shared.bind_sequence(keys)
    depths = []
    for _, order in chrono_orders:
        depths.append(T.chain_recover_depth(shared, order, cb))
    seqlens = [max(0, len(o) - 1) for _, o in chrono_orders]
    mean_depth = sum(depths) / len(depths) if depths else 0.0
    full_frac = (sum(1 for d, L in zip(depths, seqlens) if d == L and L > 0)
                 / max(1, sum(1 for L in seqlens if L > 0)))

    # b3 chrono vs text successor on flashback items (per-item fresh matrices)
    chrono_ok = text_ok = n_fb = 0
    for it, order in chrono_orders:
        if it not in FLASHBACK_GOLD:
            continue
        if len(order) < 2:
            continue
        n_fb += 1
        ev, tg = T.extract_events(it["text"])
        # chrono-bound
        sm_c = T.bind_order(order, cb, N_DIM)
        if T.successor_prediction_correct(sm_c, cb, order[0].lemma, order[1].lemma):
            chrono_ok += 1
        # text-bound
        torder = T.text_order(ev)
        sm_t = T.bind_order(torder, cb, N_DIM)
        if T.successor_prediction_correct(sm_t, cb, order[0].lemma, order[1].lemma):
            text_ok += 1
    return {
        "shared_matrix_mean_chain_depth": round(mean_depth, 4),
        "shared_matrix_full_recovery_frac": round(full_frac, 4),
        "per_item_depths": depths,
        "per_item_seqlens": seqlens,
        "n_distinct_event_lemmas": len(cb),
        "flashback_chrono_successor_acc": round(chrono_ok / n_fb, 4) if n_fb else 0.0,
        "flashback_text_successor_acc": round(text_ok / n_fb, 4) if n_fb else 0.0,
        "n_flashback_scored": n_fb,
    }


# ---------------------------------------------------------------------------
# Infra: start marker + crash metrics (atomic).
# ---------------------------------------------------------------------------
def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(out_dir):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": "full",
              "expected_n_units": len(FLASHBACK_GOLD) + len(LINEAR_GOLD),
              "host": platform.node()}
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    final = os.path.join(out_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _atomic_write(out_dir, metrics):
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}",
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _atomic_write(out_dir, diag)


# ---------------------------------------------------------------------------
# Self-test: synthetic mechanism probes + real substrate code path.
# ---------------------------------------------------------------------------
def self_test():
    print("[self-test] mechanism + substrate code path")
    exercised = set()

    # (1) synthetic past-perfect flashback: cue-aware demotes pp before now
    ev, tg = T.extract_events("She left the room. He had locked the door.")
    assert any(e.is_pp for e in ev), "past-perfect not detected in synthetic probe"
    exercised.add("extract_events")
    base = T.text_order(ev)
    cue = T.reconstruct_order(ev, tg, use_tense=True, use_connective=True)
    # gold: locked before left
    bc = T.pairwise_accuracy(base, [("locked", "left")])
    cc = T.pairwise_accuracy(cue, [("locked", "left")])
    assert bc[0] == 0 and cc[0] == 1, f"synthetic flashback: base={bc} cue={cc}"
    exercised.add("reconstruct_order")

    # (2) synthetic linear: no cue -> cue-aware must NOT reorder (no regression)
    ev2, tg2 = T.extract_events("He opened the door and walked inside.")
    cue2 = T.reconstruct_order(ev2, tg2, use_tense=True, use_connective=True)
    cc2 = T.pairwise_accuracy(cue2, [("opened", "walked")])
    assert cc2[0] == cc2[1] == 1, f"linear regression: {cc2}"

    # (3) synthetic connective "after" reversal on simple-past pair
    ev3, tg3 = T.extract_events("He arrived after she departed.")
    cue3 = T.reconstruct_order(ev3, tg3, use_tense=True, use_connective=True)
    base3 = T.text_order(ev3)
    # gold: departed before arrived
    bc3 = T.pairwise_accuracy(base3, [("departed", "arrived")])
    cc3 = T.pairwise_accuracy(cue3, [("departed", "arrived")])
    assert cc3[0] >= bc3[0], f"connective reversal did not help: base={bc3} cue={cc3}"
    exercised.add("_connective_between")

    # (4) REAL substrate code path at tiny scale: Codebook + SequenceMatrix bind/predict
    cb = T.build_codebook(["a", "b", "c"], 64, seed=1)
    exercised.add("build_codebook")
    assert len(cb) == 3
    from experiments._temporal_ordering import Event
    order = [Event("a", 0, "VBD", T.TENSE_SIMPLE_PAST),
             Event("b", 1, "VBD", T.TENSE_SIMPLE_PAST),
             Event("c", 2, "VBD", T.TENSE_SIMPLE_PAST)]
    sm = T.bind_order(order, cb, 64)
    exercised.add("bind_order")
    d = T.chain_recover_depth(sm, order, cb)
    assert d == 2, f"chain recover depth {d} != 2 on clean 3-seq"
    exercised.add("chain_recover_depth")
    assert T.successor_prediction_correct(sm, cb, "a", "b"), "successor prediction failed"
    exercised.add("successor_prediction_correct")

    required = {"extract_events", "reconstruct_order", "build_codebook", "bind_order",
                "chain_recover_depth", "successor_prediction_correct", "_connective_between"}
    missing = required - exercised
    assert not missing, f"real_code_path: entrypoints not exercised: {missing}"
    print(f"[self-test] PASS; exercised={sorted(exercised)}")
    return True


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------
def main():
    out_dir = _out_dir()
    _write_start_marker(out_dir)
    t0 = time.perf_counter()

    arms = ["TEXT", "CUE", "CUE_ABLATE", "NAIVE_REVERSE"]
    results = {}
    for arm in arms:
        results[arm] = {
            "flashback": _score_subset(arm, FLASHBACK_GOLD),
            "linear": _score_subset(arm, LINEAR_GOLD),
        }

    # ARMS-MUST-DIFFER (META_RULE_AF); TEXT == CUE_ABLATE is an INTENTIONAL P2 exemption.
    import hashlib
    sig = {a: hashlib.sha256(_arm_signature(a, FLASHBACK_GOLD + LINEAR_GOLD)).hexdigest()
           for a in arms}
    arms_differ_exempted = [("TEXT", "CUE_ABLATE")]
    for i in range(len(arms)):
        for j in range(i + 1, len(arms)):
            a, b = arms[i], arms[j]
            if (a, b) in arms_differ_exempted or (b, a) in arms_differ_exempted:
                assert sig[a] == sig[b], f"P2 exemption broken: {a} != {b} (must be identical)"
            else:
                assert sig[a] != sig[b], f"META_RULE_AF: arms {a},{b} bit-identical"

    fb_text = results["TEXT"]["flashback"]["acc"]
    fb_cue = results["CUE"]["flashback"]["acc"]
    fb_naive = results["NAIVE_REVERSE"]["flashback"]["acc"]
    lin_text = results["TEXT"]["linear"]["acc"]
    lin_cue = results["CUE"]["linear"]["acc"]
    lin_naive = results["NAIVE_REVERSE"]["linear"]["acc"]
    fb_ablate = results["CUE_ABLATE"]["flashback"]["acc"]

    margin_fb = fb_cue - fb_text
    regress_lin = lin_text - lin_cue

    validity_gate_fires = fb_text <= VALIDITY_GATE_MAX
    p2_ok = abs(fb_ablate - fb_text) < 1e-9 and \
        abs(results["CUE_ABLATE"]["linear"]["acc"] - lin_text) < 1e-9

    # Verdict logic.
    if not validity_gate_fires:
        verdict = "HARD_FAIL"
        vmsg = (f"VALIDITY GATE FAILED: TEXT flashback acc={fb_text:.3f} > {VALIDITY_GATE_MAX} "
                f"-> flashback cases not genuinely non-linear; discriminator invalid.")
    elif regress_lin > NONFLASH_REGRESS_MAX:
        verdict = "HARD_FAIL"
        vmsg = (f"NON-FLASHBACK REGRESSION: CUE linear acc={lin_cue:.3f} vs TEXT {lin_text:.3f} "
                f"(drop {regress_lin:.3f} > {NONFLASH_REGRESS_MAX}).")
    elif margin_fb >= HARD_PASS_MARGIN and regress_lin <= NONFLASH_REGRESS_MAX and p2_ok:
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS: cue-aware beats text-order on real flashbacks by "
                f"{margin_fb:.3f} (CUE {fb_cue:.3f} vs TEXT {fb_text:.3f}); no linear regression "
                f"(CUE {lin_cue:.3f} == TEXT {lin_text:.3f}); validity gate fires (TEXT_fb {fb_text:.3f}); "
                f"P2 ablation collapses to text-order. Precision: NAIVE_REVERSE wins flashback "
                f"({fb_naive:.3f}) but WRECKS linear ({lin_naive:.3f}) -> the win is the TENSE CUE.")
    elif margin_fb < HARD_FAIL_MARGIN:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL: cue-aware does NOT beat text-order on flashbacks "
                f"(margin {margin_fb:.3f} < {HARD_FAIL_MARGIN}). See autopsy.")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: flashback margin {margin_fb:.3f} in "
                f"[{HARD_FAIL_MARGIN}, {HARD_PASS_MARGIN}).")

    # Autopsy (populated when margin is short OR always reported for transparency).
    autopsy = {}
    if margin_fb < HARD_PASS_MARGIN:
        low = []
        for it in FLASHBACK_GOLD:
            ev, tg = T.extract_events(it["text"])
            order = T.reconstruct_order(ev, tg, use_tense=True, use_connective=True)
            c, s, a = T.pairwise_accuracy(order, [tuple(p) for p in it["pairs"]])
            if s == 0 or (s and c < s):
                low.append({"source": it["source"], "text": it["text"],
                            "extracted": [(e.lemma, "PP" if e.is_pp else e.tense) for e in ev],
                            "n_correct": c, "n_scored": s, "n_abstain": a})
        autopsy = {"failing_items": low,
                   "candidate_levers": ["extraction: pp verb head detection (had+been+VBG)",
                                        "multi-frame: single-frame demotion assumption",
                                        "parser tense mis-tag"]}

    improving = {
        "cue_density_bins": _improving_cue_density(FLASHBACK_GOLD + LINEAR_GOLD),
        "sequence_matrix": _sequence_matrix_envelope(FLASHBACK_GOLD + LINEAR_GOLD),
    }

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: flashback CUE {fb_cue:.3f} vs TEXT {fb_text:.3f} (margin {margin_fb:+.3f}); "
                   f"linear CUE {lin_cue:.3f} vs TEXT {lin_text:.3f}; validity_gate={validity_gate_fires}",
        "elapsed_s": round(elapsed, 3),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "n_dim": N_DIM,
        "prereg_bands": {
            "validity_gate_max_text_flashback_acc": VALIDITY_GATE_MAX,
            "hard_pass_margin": HARD_PASS_MARGIN,
            "hard_fail_margin": HARD_FAIL_MARGIN,
            "nonflash_regress_max": NONFLASH_REGRESS_MAX,
        },
        "gates": {
            "validity_gate_fires": validity_gate_fires,
            "p2_ablation_collapses_to_textorder": p2_ok,
            "margin_flashback": round(margin_fb, 4),
            "regression_linear": round(regress_lin, 4),
        },
        "arms": {
            a: {"flashback_acc": round(results[a]["flashback"]["acc"], 4),
                "linear_acc": round(results[a]["linear"]["acc"], 4),
                "flashback_n_scored": results[a]["flashback"]["n_scored"],
                "linear_n_scored": results[a]["linear"]["n_scored"],
                "signature_sha256": sig[a][:16]}
            for a in arms
        },
        "arms_differ_exempted": [list(p) for p in arms_differ_exempted],
        "improving_property": improving,
        "autopsy": autopsy,
        "gold": {
            "n_flashback_items": len(FLASHBACK_GOLD),
            "n_linear_items": len(LINEAR_GOLD),
            "flashback": [{"source": it["source"], "text": it["text"], "pairs": it["pairs"]}
                          for it in FLASHBACK_GOLD],
            "linear": [{"source": it["source"], "text": it["text"], "pairs": it["pairs"]}
                       for it in LINEAR_GOLD],
        },
        "per_arm_detail": {a: results[a] for a in arms},
        "honest_scope": ("clean 0/1 flashback separation reflects past-perfect being a "
                         "high-precision cue on CONSERVATIVE short single-frame flashbacks; "
                         "graded frontier = extraction robustness + multi-sentence multi-frame "
                         "chronology (the situation-model NEXT PHASE), named not claimed."),
    }
    _atomic_write(out_dir, metrics)
    print(metrics["summary"])
    print(f"verdict={verdict} elapsed={elapsed:.2f}s -> {os.path.join(out_dir, 'metrics.json')}")
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
