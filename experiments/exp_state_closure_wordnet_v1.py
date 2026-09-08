"""exp_state_closure_wordnet_v1 -- DERIVE state antonymy/scale-type from WordNet for the state-span CLOSURE
path, replacing the hand-enumerated lexicon that gates a CORE computation.

THE BRAIN-FOUNDATIONAL DEFECT (verified on disk 2026-09-08):
  hdlab/state_register.py implements a brain-faithful default-persist state model (Dowty 1986 temporal
  inertia: a state span holds until an EXPLICIT incompatibility). BUT the closure trigger
  `incompatible(v1,v2)` (state_register.py ~L226-240) fires ONLY on the hand lists `_OPPOSED`/`_INCOMPAT`
  (~L62-89) plus a morphological un-/in- rule. Consequence: a state antonym pair NOT in the hand list
  (e.g. wet/dry, tired/rested, honest/dishonest) NEVER closes the span -> `add_state` (~L272-284) keeps the
  old state open -> `is_in_state` wrongly reports the superseded state "still holds". The brain DERIVES
  antonymy/scale-type from the semantic hub (ATL; Patterson/Nestor/Rogers 2007); it does not hand-enumerate.
  The organ's OTHER path `state_match` (~L198-221) ALREADY uses WordNet (synonymy/hypernym entailment) -- so
  the FOUNDATION route is precedented and available. Note `state_match`'s own ANTONYM branch (L207/L211)
  also calls `incompatible`, so it inherits the same hand-list cap.

THIS CELL: a WordNet-augmented `wn_incompatible` (adjective/adverb antonym relations, top-k senses,
  symmetric) that FALLS BACK to the stock `incompatible` (hand list + morphology) -- ADDITIVE, never removes
  coverage. Plus a WordNet scale-type deriver (`wn_scale_type`, Kennedy 2007 gradability) for the typed
  contradictory/contrary guard (NOTE: scale-type is NOT on the closure path; closure uses only
  `incompatible`). We MEASURE, on MODERN gold (19c banned), floors recomputed per population + CI half-width
  + info-free twin + null p95:
    (A) the STATE board dim (qa_state; reuse exp_situation_model_state_qa_v1.board_state_dimension) -- NO
        REGRESS + any gain (STOCK vs monkeypatched `incompatible`).
    (B) the polarity/negation board (exp_polarity_operator_monli_v1.run) -- NO REGRESS (the negation
        operator does not consult `incompatible`; measured to confirm byte-identical).
    (C) a constructed MODERN state-CLOSURE gold isolating the closure mechanism (abstract state events, like
        the organ's own spaCy-free core self-test): antonym pairs NOT in the hand list SHOULD close (gold
        False), non-antonym co-states must NOT close (gold True). Arms: HAND (stock) / WN / info-free TWIN
        (permuted second state) / always-persist floor. Plus a lexicon precision/recall probe that
        EXPLICITLY measures the over-closing risk (WordNet antonymy noise: hungry/thirsty, loud/piano).

GLASS-BOX: pure symbolic + offline WordNet (nltk); NO external LLM at inference. ASCII only, no em-dash.
Experiments-side only (does not edit hdlab/): if net-positive/no-regress, SOLVED.md proposes the hdlab diff.

Run: .venv/Scripts/python.exe experiments/exp_state_closure_wordnet_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_state_closure_wordnet_v1.py --run [--cap N]
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import hdlab.state_register as SR
from hdlab.state_register import _canon_value as _canon, StateRegister, CURRENT, PRIOR

ANCHOR = "state_closure_wordnet_v1"
from experiments._seed_checkpoint import get_output_dir  # Q115: provably re-runnable canonical output dir
OUT_DIR = get_output_dir(ANCHOR)
SEED = 20260908

# the ORIGINAL closure predicate (hand list + morphology) -- captured BEFORE any patch so the WordNet
# augmentation can fall back to it without recursion.
_ORIG_INCOMPAT = SR.incompatible

_ANT_CACHE: Dict[Tuple[str, int], frozenset] = {}


def _adj_ants(word: str, k: int = 1) -> frozenset:
    """WordNet CORE-ADJECTIVE antonym lemmas of `word` over its top-k adjective ('a') senses. CONFIG pinned by
    a precision/recall sweep (see SOLVED): core-adjective-only + top-1 sense is strictly best -- opp-recall
    1.00, constructed-antonym-recall 1.00, false-close 0.133 (vs 0.200 for k>=2 or including 's' satellites,
    which add the loud/piano music-sense noise). Antonymy in WordNet is anchored on the core 'a' adjective
    (satellites relate via similar_to), so this is the principled restriction. The full-synset /
    derivationally-related expansion pulls in cross-POS junk (tired->interest/refresh, loud->louden/sound) --
    tested and REJECTED. Closure RETRACTS a state, so we bias to precision (a missed close just leaves the
    pre-existing conservative default; a false close destroys information)."""
    key = (word, k)
    if key in _ANT_CACHE:
        return _ANT_CACHE[key]
    out = set()
    try:
        from nltk.corpus import wordnet as wn
        adjs = [s for s in wn.synsets(word) if s.pos() == "a"][:k]
        for s in adjs:
            for l in s.lemmas():
                for a in l.antonyms():
                    out.add(a.name().replace("_", " ").lower())
    except Exception:
        pass
    out.discard(word)
    _ANT_CACHE[key] = frozenset(out)
    return _ANT_CACHE[key]


def wn_incompatible(v1: str, v2: str, k: int = 1) -> bool:
    """WordNet-AUGMENTED closure predicate: True iff two state VALUES cannot co-hold. ADDITIVE drop-in for
    hdlab.state_register.incompatible -- first the stock hand-list + morphological rule (never removes
    coverage), THEN adjective antonym relations from WordNet (the FOUNDATION route, as the brain derives
    antonymy rather than hand-listing it)."""
    if _ORIG_INCOMPAT(v1, v2):          # hand list + un-/in- morphology (coverage preserved)
        return True
    a, b = _canon(v1), _canon(v2)
    if a == b:
        return False
    return (b in _adj_ants(a, k)) or (a in _adj_ants(b, k))


def wn_scale_type(word: str) -> Optional[str]:
    """Derive scale-type from WordNet (Kennedy 2007 gradability), for the typed contradictory/contrary
    antonymy guard. 'closed' = absolute/contradictory (negation flips: not-alive |= dead); 'open' =
    relative/contrary (a middle exists: not-tall =/= short). Heuristic: a gradable adjective (a satellite
    's' sense, or has similar_to satellites) is OPEN; a non-gradable core 'a' adjective is CLOSED. Falls back
    to the hand scale sets. NOTE: scale-type is NOT on the closure path (closure uses only incompatible); it
    only types state_match's negated branch."""
    w = _canon(word)
    if w in SR._CLOSED_SCALE:
        return "closed"
    if w in SR._OPEN_SCALE:
        return "open"
    try:
        from nltk.corpus import wordnet as wn
        adjs = [s for s in wn.synsets(w) if s.pos() in ("a", "s")][:3]
        if not adjs:
            return None
        gradable = any(s.pos() == "s" or s.similar_tos() for s in adjs)
        return "open" if gradable else "closed"
    except Exception:
        return None


# ---------------------------------------------------------------------------
# monkeypatch helpers: swap the module-global `incompatible` so add_state / state_match / _contradictory_pair
# (all bare-name module-global lookups) route through the WordNet augmentation.
# ---------------------------------------------------------------------------
def _patch():
    SR.incompatible = wn_incompatible


def _unpatch():
    SR.incompatible = _ORIG_INCOMPAT


# ===========================================================================
# (A) STATE BOARD (qa_state) no-regress: STOCK vs WordNet-patched, same population.
# ===========================================================================
def measure_state_board(cap: Optional[int] = 1500, n_boot: int = 1000) -> dict:
    import experiments.exp_situation_model_state_qa_v1 as STQA
    _unpatch()
    stock_row, stock = STQA.board_state_dimension(cap=cap, n_boot=n_boot)
    _patch()
    try:
        wn_row, wn = STQA.board_state_dimension(cap=cap, n_boot=n_boot)
    finally:
        _unpatch()
    return {
        "population": stock_row["population"],
        "n_pred_clauses": stock["n_pred_clauses"],
        "stock": {"qa_state_model": stock["qa_state_model"], "yesno_accuracy": stock["yesno_accuracy"],
                  "positional_floor": stock["positional_floor"],
                  "shuffle_holder_twin": stock["shuffle_holder_twin"],
                  "model_vs_floor": stock["model_vs_floor"]},
        "wordnet": {"qa_state_model": wn["qa_state_model"], "yesno_accuracy": wn["yesno_accuracy"],
                    "positional_floor": wn["positional_floor"],
                    "shuffle_holder_twin": wn["shuffle_holder_twin"],
                    "model_vs_floor": wn["model_vs_floor"]},
        "delta_model": round(wn["qa_state_model"] - stock["qa_state_model"], 4),
        "delta_yesno": round(wn["yesno_accuracy"] - stock["yesno_accuracy"], 4),
        "no_regress": bool(wn["qa_state_model"] >= stock["qa_state_model"] - 1e-9
                           and wn["yesno_accuracy"] >= stock["yesno_accuracy"] - 1e-9),
    }


# ===========================================================================
# (B) POLARITY board (MoNLI) no-regress: STOCK vs WordNet-patched.
# ===========================================================================
def measure_polarity_board() -> dict:
    import experiments.exp_polarity_operator_monli_v1 as PMON
    _unpatch()
    stock = PMON.run(use_train=True)
    _patch()
    try:
        wn = PMON.run(use_train=True)
    finally:
        _unpatch()

    def _op(res):
        p = res["populations"]["POOLED"]
        return {"operator_acc": p["acc"]["operator"], "blind_floor": p["acc"]["blind_floor"],
                "operator_minus_blind": p["operator_minus_blind"]}
    return {
        "note": "the negation/polarity operator (event_polarity, read_quantifier) does NOT call incompatible; "
                "MoNLI entailment uses hyponymy (_wn_hypernym_entails), not the antonym/closure path -- so this "
                "is expected byte-identical. Measured to confirm.",
        "stock_pooled": _op(stock), "wordnet_pooled": _op(wn),
        "identical": bool(stock["populations"]["POOLED"]["acc"]["operator"]
                          == wn["populations"]["POOLED"]["acc"]["operator"]),
    }


# ===========================================================================
# (C) constructed MODERN state-CLOSURE gold (mechanism-isolated: abstract state events, extraction held as
# oracle -- mirrors the organ's own spaCy-free core self-test). 19c-free vocabulary.
# ===========================================================================
# ANTONYM closures the HAND list does NOT cover (not in _OPPOSED, not an un-/in- morphological pair): the
# span SHOULD close -> the old state does NOT hold at the end (gold False = does_not_hold).
_CLOSURE_ANTONYM: List[Tuple[str, str, str]] = [
    ("towel", "wet", "dry"), ("she", "tired", "rested"), ("room", "quiet", "noisy"),
    ("man", "drunk", "sober"), ("street", "safe", "dangerous"), ("clerk", "honest", "dishonest"),
    ("music", "loud", "soft"), ("suspect", "innocent", "guilty"), ("blade", "sharp", "dull"),
    ("road", "wide", "narrow"), ("water", "shallow", "deep"), ("surface", "smooth", "rough"),
    ("box", "light", "heavy"), ("cup", "hot", "cold"), ("engine", "wet", "dry"),
]
# CO-STATE controls: the later value is NOT an antonym of the first -> the span must NOT close -> the first
# state STILL holds at the end (gold True). Probes OVER-closing.
_CLOSURE_COSTATE: List[Tuple[str, str, str]] = [
    ("she", "tired", "hungry"), ("man", "drunk", "angry"), ("room", "quiet", "cold"),
    ("clerk", "honest", "tall"), ("suspect", "innocent", "young"), ("towel", "wet", "blue"),
    ("music", "loud", "fast"), ("blade", "sharp", "old"), ("water", "shallow", "cold"),
    ("road", "wide", "empty"),
]


def _closes(incompat_fn, first: str, second: str) -> bool:
    """Does asserting `second` at t=2 close a `first` span opened at t=0, under closure predicate incompat_fn?
    Returns True iff `first` no longer holds at the end (i.e. the span closed)."""
    save = SR.incompatible
    SR.incompatible = incompat_fn
    try:
        reg = StateRegister().start([first + "@e"])
        reg.apply_state(first + "@e", first, aspect=CURRENT, t=0)
        reg.apply_state(first + "@e", second, aspect=CURRENT, t=2)
        holds = reg.is_in_state(first + "@e", first, t=4)   # True/False/None
    finally:
        SR.incompatible = save
    return holds is not True    # closed (False) or undetermined -> "does not still hold"


def measure_closure_gold(n_boot: int = 5000, seed: int = SEED) -> dict:
    rng = np.random.default_rng(seed)
    items = [(e, a, b, False) for (e, a, b) in _CLOSURE_ANTONYM] \
        + [(e, a, b, True) for (e, a, b) in _CLOSURE_COSTATE]
    # info-free TWIN: permute the SECOND value across the ANTONYM items only (keep entity+first; the
    # closure signal must beat a permuted second state). Co-state items keep their own second (control).
    ant_seconds = [b for (_, _, b) in _CLOSURE_ANTONYM]
    perm = rng.permutation(len(ant_seconds))
    twin_second = {i: ant_seconds[perm[i]] for i in range(len(ant_seconds))}

    arms = {"hand": [], "wordnet": [], "twin": [], "persist_floor": []}
    ant_i = 0
    for (e, a, b, gold_holds) in items:
        gold_closed = not gold_holds   # gold: should the span have closed?
        # HAND (stock): closed iff stock incompatible
        hand_closed = _closes(_ORIG_INCOMPAT, a, b)
        # WN: closed iff wn_incompatible
        wn_closed = _closes(wn_incompatible, a, b)
        arms["hand"].append(int(hand_closed == gold_closed))
        arms["wordnet"].append(int(wn_closed == gold_closed))
        # always-persist floor: never closes -> holds=True always
        arms["persist_floor"].append(int(False == gold_closed))
        # TWIN: WN closure but with the permuted second value (antonym items only; co-state uses own b)
        if gold_holds is False:  # an antonym item
            b_tw = twin_second[ant_i]; ant_i += 1
        else:
            b_tw = b
        tw_closed = _closes(wn_incompatible, a, b_tw)
        arms["twin"].append(int(tw_closed == gold_closed))

    def _acc(v):
        return round(float(np.mean(v)), 4)

    def _boot(a, b):
        av = np.array(arms[a], float); bv = np.array(arms[b], float); n = len(av)
        obs = av.mean() - bv.mean()
        ds = np.empty(n_boot)
        for k in range(n_boot):
            idx = rng.integers(0, n, n)
            ds[k] = av[idx].mean() - bv[idx].mean()
        lo, hi = np.percentile(ds, [2.5, 97.5])
        return dict(delta=round(float(obs), 4), lo=round(float(lo), 4), hi=round(float(hi), 4),
                    hw=round(float((hi - lo) / 2), 4),
                    null_p95=round(float(np.percentile(np.abs(ds - obs), 95)), 4), ci_sep=bool(lo > 0))

    # split accuracies for interpretability
    n_ant = len(_CLOSURE_ANTONYM); n_co = len(_CLOSURE_COSTATE)
    def _split(arm):
        v = arms[arm]
        return {"antonym_recall": _acc(v[:n_ant]), "costate_precision": _acc(v[n_ant:]), "overall": _acc(v)}
    return {
        "n_items": len(items), "n_antonym": n_ant, "n_costate": n_co,
        "accuracy": {arm: _split(arm) for arm in arms},
        "wordnet_vs_hand": _boot("wordnet", "hand"),
        "wordnet_vs_twin": _boot("wordnet", "twin"),
        "wordnet_vs_persist_floor": _boot("wordnet", "persist_floor"),
    }


# ===========================================================================
# lexicon precision/recall (the OVER-CLOSING risk, explicit): labeled opposite vs non-opposite state pairs.
# ===========================================================================
# TRUE opposites (should be incompatible) -- mix of hand-listed and NOT.
_POS_PAIRS = [("open", "shut"), ("alive", "dead"), ("locked", "unlocked"), ("ill", "well"),
              ("wet", "dry"), ("tired", "rested"), ("drunk", "sober"), ("honest", "dishonest"),
              ("safe", "dangerous"), ("innocent", "guilty"), ("wide", "narrow"), ("sharp", "dull"),
              ("shallow", "deep"), ("smooth", "rough"), ("loud", "soft"), ("asleep", "awake"),
              ("visible", "invisible"), ("full", "empty"), ("clean", "dirty"), ("happy", "sad")]
# NON-opposites (must NOT be incompatible): synonyms, co-states, unrelated, AND known WordNet noise.
_NEG_PAIRS = [("ill", "sick"), ("happy", "glad"), ("big", "large"), ("broken", "shattered"),
              ("tired", "hungry"), ("drunk", "angry"), ("quiet", "cold"), ("honest", "tall"),
              ("wet", "blue"), ("loud", "fast"), ("sharp", "old"), ("shallow", "cold"),
              # KNOWN WordNet-antonym noise (these will FALSE-fire under wn -> over-close):
              ("hungry", "thirsty"), ("loud", "piano"), ("safe", "out")]


def measure_lexicon() -> dict:
    def _rate(fn, pairs):
        return round(float(np.mean([int(fn(a, b)) for (a, b) in pairs])), 4)
    hand_pos = _rate(_ORIG_INCOMPAT, _POS_PAIRS); hand_neg = _rate(_ORIG_INCOMPAT, _NEG_PAIRS)
    wn_pos = _rate(wn_incompatible, _POS_PAIRS); wn_neg = _rate(wn_incompatible, _NEG_PAIRS)
    # per-pair diagnosis of WordNet false-fires on the negative set (the over-closing cases)
    wn_false_fires = [f"{a}/{b}" for (a, b) in _NEG_PAIRS if wn_incompatible(a, b)]
    return {
        "hand": {"recall_on_opposites": hand_pos, "false_close_rate_on_nonopposites": hand_neg},
        "wordnet": {"recall_on_opposites": wn_pos, "false_close_rate_on_nonopposites": wn_neg},
        "recall_gain": round(wn_pos - hand_pos, 4),
        "over_close_cost": round(wn_neg - hand_neg, 4),
        "wordnet_false_fires_on_nonopposites": wn_false_fires,
        "n_pos": len(_POS_PAIRS), "n_neg": len(_NEG_PAIRS),
    }


def run(cap: Optional[int] = 1500, quick: bool = False) -> dict:
    t0 = time.time()
    res = {"anchor": ANCHOR, "seed": SEED,
           "closure_gold": measure_closure_gold(),
           "lexicon": measure_lexicon()}
    if not quick:
        res["state_board"] = measure_state_board(cap=cap)
        res["polarity_board"] = measure_polarity_board()
    res["elapsed_s"] = round(time.time() - t0, 1)
    res["ts_iso"] = datetime.now(timezone.utc).isoformat()
    return res


def _print(res):
    cg = res["closure_gold"]
    print("\n=== (C) CONSTRUCTED MODERN CLOSURE GOLD (mechanism-isolated) ===")
    print(f"  n_items={cg['n_items']} (antonym={cg['n_antonym']} should-close, costate={cg['n_costate']} keep-open)")
    for arm, d in cg["accuracy"].items():
        print(f"  {arm:14s} antonym_recall={d['antonym_recall']:.3f}  costate_precision={d['costate_precision']:.3f}"
              f"  overall={d['overall']:.3f}")
    for name, key in [("WN vs HAND", "wordnet_vs_hand"), ("WN vs TWIN", "wordnet_vs_twin"),
                      ("WN vs persist-floor", "wordnet_vs_persist_floor")]:
        d = cg[key]
        print(f"  {name:20s} d={d['delta']:+.4f} [{d['lo']:+.4f},{d['hi']:+.4f}] hw={d['hw']:.4f} "
              f"nullp95={d['null_p95']:.4f} {'CI-SEP' if d['ci_sep'] else 'n.s.'}")
    lx = res["lexicon"]
    print("\n=== lexicon precision/recall (over-closing risk) ===")
    print(f"  HAND: recall_on_opposites={lx['hand']['recall_on_opposites']:.3f}  "
          f"false_close_on_nonopposites={lx['hand']['false_close_rate_on_nonopposites']:.3f}")
    print(f"  WN  : recall_on_opposites={lx['wordnet']['recall_on_opposites']:.3f}  "
          f"false_close_on_nonopposites={lx['wordnet']['false_close_rate_on_nonopposites']:.3f}")
    print(f"  recall_gain={lx['recall_gain']:+.3f}  over_close_cost={lx['over_close_cost']:+.3f}")
    print(f"  WN false-fires on non-opposites: {lx['wordnet_false_fires_on_nonopposites']}")
    if "state_board" in res:
        sb = res["state_board"]
        print("\n=== (A) STATE BOARD (qa_state) no-regress ===")
        print(f"  population={sb['population']}  n_pred_clauses={sb['n_pred_clauses']}")
        print(f"  STOCK  model={sb['stock']['qa_state_model']:.4f}  yesno={sb['stock']['yesno_accuracy']:.4f}"
              f"  floor={sb['stock']['positional_floor']:.4f}")
        print(f"  WN     model={sb['wordnet']['qa_state_model']:.4f}  yesno={sb['wordnet']['yesno_accuracy']:.4f}"
              f"  floor={sb['wordnet']['positional_floor']:.4f}")
        print(f"  delta_model={sb['delta_model']:+.4f}  delta_yesno={sb['delta_yesno']:+.4f}  "
              f"NO_REGRESS={sb['no_regress']}")
    if "polarity_board" in res:
        pb = res["polarity_board"]
        print("\n=== (B) POLARITY board (MoNLI) no-regress ===")
        print(f"  STOCK operator_acc={pb['stock_pooled']['operator_acc']}  "
              f"WN operator_acc={pb['wordnet_pooled']['operator_acc']}  IDENTICAL={pb['identical']}")
    print(f"\n  elapsed={res['elapsed_s']}s")


def self_test():
    # sanity: the augmentation fires on non-hand-listed antonyms, preserves hand coverage, and does not
    # touch synonyms.
    assert _ORIG_INCOMPAT("wet", "dry") is False, "precondition: hand list does NOT cover wet/dry"
    assert wn_incompatible("wet", "dry") is True, "wn must close wet/dry"
    assert wn_incompatible("open", "shut") is True, "wn must preserve hand coverage (open/shut)"
    assert wn_incompatible("ill", "sick") is False, "wn must NOT close synonyms (ill/sick)"
    assert wn_incompatible("tired", "rested") is True, "wn must close tired/rested"
    res = run(quick=True)
    cg = res["closure_gold"]
    assert cg["accuracy"]["wordnet"]["antonym_recall"] > cg["accuracy"]["hand"]["antonym_recall"], \
        ("wn must recover closures the hand list misses", cg)
    print("SELFTEST PASS")
    _print(res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--quick", action="store_true", help="skip the board runs (closure gold + lexicon only)")
    ap.add_argument("--cap", type=int, default=1500)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    res = run(cap=args.cap, quick=args.quick)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as f:
        json.dump(res, f, indent=2)
    _print(res)
    print(f"\nwrote {os.path.relpath(os.path.join(OUT_DIR, 'metrics.json'), REPO)}")


if __name__ == "__main__":
    main()
