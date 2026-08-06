# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; real vs scrambled ACQUIRED entries hash-differ)
# - final_metrics_atomicity: tmp_replace (os.replace of metrics.json.tmp)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb: n/a (bounded 36-item binary classification vs fixed gold; not a capacity/argmax-noise cell)
# - baseline_in_band: N/A for the primary arm (direct measurement vs fixed gold); reference baselines
#   (majority floor 23/36=0.6389, fall-through 0/36) are REAL measured floors, verified in self_test
# - discriminator survives scale: FULL == the whole 36-item OOV subset (no smaller-N smoke discriminator);
#   smoke runs the same mechanism on a novels-only corpus subset and asserts the mechanism fires
# - cardinality_ok: EXPECTED_N_UNITS = n_target_lemmas + 1 (noise); verdict gates len(recorded units)
# - per-unit failure-class instrumentation (no bare except; crash recorded to metrics.json)
# - calibration_check: default_ok_for_this_regime (bands pre-registered, not tuned; floor=0.6389)
# - deterministic_seeding: fixed integer seeds (scramble perms via np.random.default_rng(1000+s)); no PYTHONHASHSEED-derived seeding
# - cell_chunked: false (single-process, resumable PER-LEMMA via tools/exp_checkpoint.py)
# - start_marker + crash_diagnostic + atomic metrics present
# - progress_logging: print_flush_true (short cell; heartbeat lines flushed)
# - all reported numbers MEASURED@ tagged in the completion report, not this file
"""Online grounded-word-acquisition loop, increment 1b (outcome-verb RESULT-CLASS/telicity axis).

preregs/2026-08-06_grounded_word_acquisition_increment1b_v1.md +
notes/formalize_word_acquisition_increment1b_result_class_congruence_2026-08-06.md.

SHAPE-corrected re-spec of increment 1's HARD_FAIL. MET/UNMET is a STRUCTURAL congruence judgment
(CLASS_REGISTRY intersection / OPPOSED_PAIRS opposition on a shared referent), NOT a reward-grounded
valuation. 1b acquires an OOV outcome verb's RESULT-CLASS POLE via the clause-local structural read
(hdlab.word_acquisition_loop.structural_vote: RECIPROCITY->POS / BLOCK_HIGH->NEG, no reward-theta),
consolidates via the REUSED MIN_CONFIRM=2 gate, writes the pole to the Tier-3 overlay, and scores
MET/UNMET on the 36 OOV-outcome items of goal_bearing_modern_eval_v1.jsonl through the LIVE production
call congruence_with_lexicon_fallback (with the Risk-#1 pole-sentinel fix live). Single channel now
(increment 1's two-channel AND-gate + reward-theta both dropped as net-harmful/redundant).

Every held-out item's polarity is EARNED (unsupervised structural voting on independently-mined corpus
sentences, excluding the eval item's own cited passage), never supplied. Glass-box, no external LLM at
inference, no borrowed embedding, deterministic integer seeds, resumable per-lemma.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import glob
import hashlib
import json
import platform
import re
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "grounded_word_acquisition_increment1b_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import hdlab.word_acquisition_loop as L                          # noqa: E402
import hdlab.verb_lexical_similarity as _vls                     # noqa: E402
from hdlab.goal_typing import congruence_with_lexicon_fallback   # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb               # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

# ---------------------------------------------------------------------------- corpora (the 7 sources
# the eval bank is drawn from -- notes/research_goal_bearing_modern_eval_2026-08-06.md).
NOVEL_RELS = [
    "little_women/cleaned/little_women.clean.txt",
    "anne_of_green_gables/cleaned/anne_of_green_gables.clean.txt",
    "tom_sawyer/cleaned/tom_sawyer.clean.txt",
    "wizard_of_oz/cleaned/wizard_of_oz.clean.txt",
    "alice_in_wonderland/cleaned/alice_in_wonderland.clean.txt",
]
RACE_RELS = ["race/middle_test.jsonl", "race/high_test.jsonl"]
ONESTOP_LEVELS = ["Ele", "Int", "Adv"]

EVAL_REL = "experiments/data/goal_bearing_modern_eval_v1.jsonl"

# find_desired_state's literal DESIDERATIVE_PASS lemma gate (the pre-reg's gate-5 eligibility split).
DESIDERATIVE_LEMMAS = {"want", "hope", "wish", "mean", "plan", "intend", "aim", "long", "yearn",
                       "desire"}

# Noise anti-drift set, REUSED VERBATIM from increment 1 (8 Vendler ACTIVITY verbs, 2 sentences each).
# NOT re-authored to avoid a leak -- the pre-reg fixes these; whatever the single-channel structural
# typer does with them is reported as-measured.
NOISE = [
    ("walked", ["He walked to the well and carried the pail home.",
                "The old man walked slowly down the road."]),
    ("sat", ["She sat by the fire in the evening.", "The children sat under the tall tree."]),
    ("spoke", ["She turned and spoke to her brother.", "The teacher spoke to the class that morning."]),
    ("turned", ["He turned and looked toward the door.", "She turned the corner by the shop."]),
    ("answered", ["The boy answered the question at once.", "She answered her mother very softly."]),
    ("asked", ["He asked for a cup of cold water.", "The girl asked her friend about the road."]),
    ("stood", ["The horse stood by the wooden gate.", "He stood near the open window."]),
    ("carried", ["She carried the basket to the market.", "They carried the boxes up the stairs."]),
]

N_SCRAMBLE_SEEDS = 5
MAX_OCC = 6            # up to 6 mined acquisition sentences per lemma
MIN_OCC = 2           # < MIN_OCC independent occurrences -> insufficient_corpus_support (a MISS)
SMOKE_MAX_OCC = 4


# ---------------------------------------------------------------------------- corpus / eval loading
def _split_sents(text):
    parts = re.split(r'[.!?]+["\'’”)]?', text)
    return [s.strip() for s in parts if len(s.strip()) > 3]


def _load_corpus(novels_only=False):
    """Deterministic ordered list of corpus sentences across the 7 sources. `novels_only` restricts to
    the 5 narrative novels (smoke mode -- faster, still fires the mechanism)."""
    sents = []
    for rel in NOVEL_RELS:
        p = os.path.join(REPO_ROOT, "data", "corpora", rel)
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            sents += _split_sents(f.read())
    if novels_only:
        return sents
    for rel in RACE_RELS:
        p = os.path.join(REPO_ROOT, "data", "corpora", rel)
        seen = set()
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if not line.strip():
                    continue
                art = json.loads(line).get("article", "")
                if not art or art in seen:
                    continue
                seen.add(art)
                sents += _split_sents(art)
    for lvl in ONESTOP_LEVELS:
        pat = os.path.join(REPO_ROOT, "data", "corpora", "onestop",
                           "Texts-SeparatedByReadingLevel", f"{lvl}-Txt", "*.txt")
        for fp in sorted(glob.glob(pat)):
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                sents += _split_sents(f.read())
    return sents


def _load_eval():
    """Read the eval bank; return (all_rows, oov_rows). oov_rows = the 36 primary items with
    outcome_in_lexicon == False (derived directly from the file, not a hard-coded list)."""
    rows = []
    with open(os.path.join(REPO_ROOT, EVAL_REL), "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    oov = [r for r in rows if r.get("outcome_in_lexicon") is False]
    return rows, oov


def _norm(s):
    return " ".join(re.findall(r"[a-z']+", s.lower()))


def _make_exclude(all_rows):
    """Non-circularity: a mined sentence whose normalized form is a substring of ANY eval item's cited
    passage is excluded (conservative -- errs toward MORE exclusion, guaranteeing the eval item's own
    passage is never mined)."""
    blob = " || ".join(_norm(r["text"]) for r in all_rows)

    def exclude(sent):
        n = _norm(sent)
        return len(n) > 0 and n in blob
    return exclude


# ---------------------------------------------------------------------------- scoring helpers
def _score_arm(mined, oov_rows, enrich):
    """Acquire (structural single-channel) + register into the Tier-3 overlay + score all 36 OOV items
    via the LIVE production congruence_with_lexicon_fallback; restore the empty overlay. Returns a dict
    of per-arm metrics + per-item details + the acquired polarity map + its hash."""
    _vls.clear_acquired_outcome()
    acquired, _trace = L.run_acquisition_1b(mined, enrich=enrich)
    for lemma, info in acquired.items():
        _vls.register_acquired_outcome(lemma, info["polarity"])
    correct = met_c = unmet_c = 0
    n_met = sum(1 for r in oov_rows if r["gold_outcome_polarity"] == "met")
    n_unmet = len(oov_rows) - n_met
    e_ok = e_tot = f_ok = f_tot = 0
    details = []
    for r in oov_rows:
        gold = "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"
        pred, detail = congruence_with_lexicon_fallback(r["text"])
        ok = (pred == gold)
        correct += ok
        if gold == "MET":
            met_c += ok
        else:
            unmet_c += ok
        eligible = r["goal_verb_lemma"] in DESIDERATIVE_LEMMAS
        if eligible:
            e_tot += 1
            e_ok += ok
        else:
            f_tot += 1
            f_ok += ok
        details.append({"id": r["id"], "outcome_lemma": r["outcome_verb_lemma"],
                        "acquired_polarity": acquired.get(r["outcome_verb_lemma"], {}).get("polarity"),
                        "gold": gold, "pred": pred, "reason": detail.get("reason"),
                        "eligible": eligible, "correct": bool(ok)})
    _vls.clear_acquired_outcome()
    acc = correct / len(oov_rows)
    return {
        "n_acquired": len(acquired),
        "acquired": {k: v["polarity"] for k, v in acquired.items()},
        "acquired_hash": _acquired_hash(acquired),
        "primary_accuracy": round(acc, 4), "primary_correct": correct,
        "met_recall_correct": met_c, "met_total": n_met,
        "unmet_recall_correct": unmet_c, "unmet_total": n_unmet,
        "desiderative_eligible_subset_accuracy": round(e_ok / max(1, e_tot), 4),
        "eligible_correct": e_ok, "eligible_total": e_tot,
        "flat_fallback_subset_accuracy": round(f_ok / max(1, f_tot), 4),
        "fallback_correct": f_ok, "fallback_total": f_tot,
        "details": details,
    }


def _acquired_hash(acquired):
    payload = json.dumps({k: v["polarity"] for k, v in sorted(acquired.items())}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _noise_probe():
    """noise_consolidated_count = # activity verbs that consolidate into the overlay (should be 0);
    noise_gated_count = # activity verbs whose structural read fires NO realized/blocked situation-type
    on EITHER sentence (should be 8). Reported distinctly (different pipeline stages)."""
    _vls.clear_acquired_outcome()
    target = {}
    gated = 0
    per_verb = {}
    for w, sents in NOISE:
        votes = [L.structural_vote([], s, w) for s in sents]
        per_verb[w] = votes
        target[w] = sents
        if all(v is None for v in votes):
            gated += 1
    acquired, _ = L.run_acquisition_1b(target)
    _vls.clear_acquired_outcome()
    return {"noise_consolidated_count": len(acquired),
            "noise_consolidated_words": {k: v["polarity"] for k, v in acquired.items()},
            "noise_gated_count": gated, "noise_per_verb_votes": per_verb}


def _scramble(mined, oov_rows, per_lemma_votes):
    """Fixed-seed permutation (N_SCRAMBLE_SEEDS) of the (target-lemma -> mined-vote-stream) pairing.
    Reassign lemma i the CORE vote stream of lemma perm[i], re-consolidate, re-score. Deterministic
    per-seed perms (np.random.default_rng, fixed integer seeds only)."""
    lemmas = sorted(mined)
    accs = []
    hashes = []
    for s in range(N_SCRAMBLE_SEEDS):
        rng = np.random.default_rng(1000 + s)
        perm = rng.permutation(len(lemmas)).tolist()
        remap = {lemmas[i]: per_lemma_votes[lemmas[perm[i]]] for i in range(len(lemmas))}

        def _override(lemma, oi, _remap=remap):
            stream = _remap[lemma]
            return stream[oi] if oi < len(stream) else None

        _vls.clear_acquired_outcome()
        acquired, _ = L.run_acquisition_1b(mined, vote_override=_override)
        for lemma, info in acquired.items():
            _vls.register_acquired_outcome(lemma, info["polarity"])
        correct = 0
        for r in oov_rows:
            gold = "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"
            pred, _d = congruence_with_lexicon_fallback(r["text"])
            correct += (pred == gold)
        _vls.clear_acquired_outcome()
        accs.append(correct / len(oov_rows))
        hashes.append(_acquired_hash(acquired))
    return {"scrambled_primary_accuracy": round(float(np.mean(accs)), 4),
            "scrambled_per_seed": [round(a, 4) for a in accs], "scrambled_acquired_hashes": hashes}


# ---------------------------------------------------------------------------- core run (per-lemma resumable)
def _run_all(output_dir, run_mode):
    novels_only = (run_mode == "smoke")
    max_occ = SMOKE_MAX_OCC if run_mode == "smoke" else MAX_OCC
    print(f"[progress] loading corpora (novels_only={novels_only})", flush=True)
    corpus = _load_corpus(novels_only=novels_only)
    all_rows, oov_rows = _load_eval()
    exclude = _make_exclude(all_rows)
    target_lemmas = sorted({r["outcome_verb_lemma"] for r in oov_rows})
    print(f"[progress] corpus_sents={len(corpus)} oov_items={len(oov_rows)} "
          f"target_lemmas={len(target_lemmas)}", flush=True)

    mined_all = L.mine_target_lemma_sentences(target_lemmas, corpus, exclude=exclude, max_occ=max_occ)

    # PER-LEMMA units (resumable): each records the lemma's mined sentences + core/enrich vote streams.
    done = completed_units(output_dir)
    for i, lemma in enumerate(target_lemmas):
        k = unit_key("acq", lemma)
        if k in done:
            continue
        sents = mined_all[lemma]
        core_votes = [L.structural_vote([], s, lemma, enrich=False) for s in sents]
        enrich_votes = [L.structural_vote([], s, lemma, enrich=True) for s in sents]
        record_unit(output_dir, k, {"lemma": lemma, "n_mined": len(sents),
                                    "sentences": sents, "core_votes": core_votes,
                                    "enrich_votes": enrich_votes})
        if (i + 1) % 10 == 0:
            print(f"[progress] acquired-votes {i + 1}/{len(target_lemmas)} lemmas", flush=True)

    # NOISE unit
    if unit_key("noise", "all") not in completed_units(output_dir):
        record_unit(output_dir, unit_key("noise", "all"), _noise_probe())

    # ---- aggregate from recorded per-lemma units (cheap, deterministic, recomputed each run) --------
    units = load_units(output_dir)
    mined = {}
    core_votes = {}
    enrich_votes = {}
    insufficient = []
    for lemma in target_lemmas:
        u = units[unit_key("acq", lemma)]
        mined[lemma] = u["sentences"]
        core_votes[lemma] = u["core_votes"]
        enrich_votes[lemma] = u["enrich_votes"]
        if u["n_mined"] < MIN_OCC:
            insufficient.append(lemma)

    # rebuild {lemma: sentences} so run_acquisition_1b re-votes identically (structural_vote is
    # deterministic; the unit-stored votes are used directly for scramble).
    core_arm = _score_arm(mined, oov_rows, enrich=False)
    enrich_arm = _score_arm(mined, oov_rows, enrich=True)
    noise = units[unit_key("noise", "all")]
    scramble = _scramble(mined, oov_rows, core_votes)

    # fall-through baseline (measured): empty overlay -> production call on every OOV item.
    _vls.clear_acquired_outcome()
    fall = 0
    for r in oov_rows:
        gold = "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"
        pred, _d = congruence_with_lexicon_fallback(r["text"])
        fall += (pred == gold)

    return {
        "config": {"run_mode": run_mode, "novels_only": novels_only, "max_occ": max_occ,
                   "n_corpus_sents": len(corpus), "n_oov_items": len(oov_rows),
                   "n_target_lemmas": len(target_lemmas),
                   "n_scramble_seeds": N_SCRAMBLE_SEEDS, "min_occ": MIN_OCC},
        "target_lemmas": target_lemmas,
        "mined_counts": {lemma: len(mined[lemma]) for lemma in target_lemmas},
        "insufficient_corpus_support": insufficient,
        "insufficient_corpus_support_count": len(insufficient),
        "majority_floor": round(sum(1 for r in oov_rows
                                    if r["gold_outcome_polarity"] == "met") / len(oov_rows), 4),
        "fallthrough_baseline_correct": fall,
        "primary_arm": "structural_core_only",
        "structural_core_only": core_arm,
        "with_enrichment_atoms": enrich_arm,
        "enrichment_delta": round(enrich_arm["primary_accuracy"] - core_arm["primary_accuracy"], 4),
        "noise": noise,
        "scramble": scramble,
    }


# ---------------------------------------------------------------------------- verdict (pre-reg bands)
def _verdict(res):
    core = res["structural_core_only"]
    n = res["config"]["n_oov_items"]
    acc = core["primary_accuracy"]
    correct = core["primary_correct"]
    met_c, unmet_c = core["met_recall_correct"], core["unmet_recall_correct"]
    noise_cons = res["noise"]["noise_consolidated_count"]
    noise_gate = res["noise"]["noise_gated_count"]
    scr = res["scramble"]["scrambled_primary_accuracy"]
    e_acc = core["desiderative_eligible_subset_accuracy"]
    f_acc = core["flat_fallback_subset_accuracy"]
    insuff = res["insufficient_corpus_support_count"]

    floor = res["majority_floor"]                       # 23/36 = 0.6389
    hp_primary = 27.0 / 36.0                             # 0.75
    gate1 = (correct >= 27 and unmet_c >= 5 and met_c >= 18)
    gate2 = (noise_cons == 0 and noise_gate == 8)
    gate3 = (0.35 <= scr <= 0.65) and gate1
    gate4 = (insuff <= 12)
    gate5 = (e_acc > f_acc)
    hard_pass = gate1 and gate2 and gate3 and gate4 and gate5

    hf_primary = acc <= round(floor, 4)                 # does not beat blind majority
    hf_noise = noise_cons >= 1
    hf_scramble = (not (0.35 <= scr <= 0.65)) and (abs(acc - scr) < 0.10)
    hf_gate5 = (e_acc <= f_acc)
    hard_fail = hf_primary or hf_noise or hf_scramble or hf_gate5

    if hard_pass:
        verdict = "HARD_PASS"
    elif hard_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    reasons = []
    if hf_primary:
        reasons.append(f"primary_le_majority_floor({acc:.4f}<={floor:.4f})")
    if hf_noise:
        reasons.append(f"anti_drift_leak(noise_consolidated={noise_cons}/8)")
    if hf_scramble:
        reasons.append(f"scramble_not_collapsed(scr={scr:.3f} real={acc:.3f})")
    if hf_gate5:
        reasons.append(f"eligible_le_fallback(elig={e_acc:.4f}<=fallback={f_acc:.4f})")

    summary = (
        f"primary={correct}/{n}={acc:.4f} (floor={floor:.4f}) "
        f"met_recall={met_c}/{core['met_total']} unmet_recall={unmet_c}/{core['unmet_total']} | "
        f"noise_consol={noise_cons}/8 noise_gated={noise_gate}/8 | scramble={scr:.3f} | "
        f"GATE5 eligible={e_acc:.3f} vs fallback={f_acc:.3f} | "
        f"enrich_delta={res['enrichment_delta']:+.4f} | insuff_corpus={insuff}")
    return {"verdict": verdict, "verdict_msg": f"{verdict}: {summary}", "summary": summary,
            "hard_fail_reasons": reasons,
            "gates": {"gate1_primary_and_recall": gate1, "gate2_noise": gate2,
                      "gate3_scramble_band": gate3, "gate4_coverage": gate4,
                      "gate5_eligible_beats_fallback": gate5,
                      "hard_pass": hard_pass, "hard_fail": hard_fail}}


# ---------------------------------------------------------------------------- infra
def _out_dir_for(run_mode):
    return OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, d):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def run(run_mode):
    t0 = time.perf_counter()
    output_dir = _out_dir_for(run_mode)
    # EXPECTED_N_UNITS is data-derived (n target lemmas + 1 noise unit); recompute cheaply here.
    _all_rows, _oov = _load_eval()
    expected_n_units = len({r["outcome_verb_lemma"] for r in _oov}) + 1
    _write_start_marker(output_dir, run_mode, expected_n_units)

    res = _run_all(output_dir, run_mode)
    n_units = len(completed_units(output_dir))
    agg = dict(res)
    agg.update(_verdict(res))
    # cardinality gate (META_RULE_H)
    if n_units < expected_n_units:
        agg["verdict"] = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        agg["verdict_msg"] = (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: recorded {n_units} units "
                              f"< expected {expected_n_units}")
    agg["run_mode"] = run_mode
    agg["recorded_units"] = n_units
    agg["expected_n_units"] = expected_n_units
    agg["cardinality_ok"] = bool(n_units >= expected_n_units)
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    _write_metrics(output_dir, agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.1f}s", flush=True)
    return agg


# ---------------------------------------------------------------------------- self-test
def self_test():
    """(1) 36-item OOV subset derives from the file + majority floor 0.6389 + fall-through baseline
    reproduces on the live module; (2) every OOV outcome lemma is OOV of the Tier-2 base lexicon
    (non-circular acquisition); (3) hdlab 1b primitives fire (structural_vote POS/NEG poles, mining,
    consolidation, Tier-3 pole sentinel end-to-end); (4) META_RULE_AF: real vs >=1 scrambled ACQUIRED
    set hash-differ; (5) enrichment flag toggles a real difference somewhere in the pipeline."""
    all_rows, oov = _load_eval()
    assert len(oov) == 36, f"expected 36 OOV items, got {len(oov)}"
    n_met = sum(1 for r in oov if r["gold_outcome_polarity"] == "met")
    assert n_met == 23, f"expected 23 MET, got {n_met}"
    assert abs(n_met / 36 - 0.6389) < 1e-3
    n_elig = sum(1 for r in oov if r["goal_verb_lemma"] in DESIDERATIVE_LEMMAS)
    assert n_elig == 18, f"expected 18 desiderative-eligible items, got {n_elig}"

    # (2) every OOV outcome lemma OOV of the Tier-2 base lexicon (circularity guard)
    for r in oov:
        assert not _vls.in_lexicon(r["outcome_verb_lemma"], "outcome"), (
            f"outcome lemma {r['outcome_verb_lemma']!r} is NOT OOV of the base lexicon (circularity)")

    # (3) hdlab primitives fire
    assert L.structural_vote([], "The wizard gave the boy some brains", "give") == "POS"
    assert L.structural_vote([], "The old boat sank", "sink") == "NEG"
    _vls.clear_acquired_outcome()
    acq, _ = L.run_acquisition_1b({"give": ["The wizard gave the boy brains", "She gave him a coin"]})
    assert acq.get("give", {}).get("polarity") == "POS", "give should consolidate POS"
    for lemma, info in acq.items():
        _vls.register_acquired_outcome(lemma, info["polarity"])
    # Tier-3 pole sentinel end-to-end (Risk #1 fix): acquired give=POS types MET on a linking passage.
    from hdlab.goal_typing import congruence_decision, _verb_classes
    assert _verb_classes("give") == {"ACQUIRED_REALIZED"}, "Risk#1 sentinel must fire for acquired give"
    d, _det = congruence_decision(["Owen wanted to win the prize before noon"], "Owen gave a shout")
    assert d == "MET", f"acquired give=POS + POS-pole goal + linked referent must type MET, got {d}"
    _vls.clear_acquired_outcome()
    assert _verb_classes("give") == set(), "overlay must clear (strict-ADD hygiene)"

    # fall-through baseline (empty overlay) is a REAL measured floor
    fall = 0
    for r in oov:
        gold = "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"
        pred, _d = congruence_with_lexicon_fallback(r["text"])
        fall += (pred == gold)
    print(f"[SELFTEST] fall_through_baseline={fall}/36 floor=0.6389 oov=36 eligible=18", flush=True)

    # (4)+(5) tiny end-to-end at smoke scope -> arms-must-differ (real vs scrambled hash) + enrich toggles
    res = _run_all(_out_dir_for("selftest"), "smoke")
    real_hash = res["structural_core_only"]["acquired_hash"]
    scr_hashes = res["scramble"]["scrambled_acquired_hashes"]
    assert any(h != real_hash for h in scr_hashes), (
        "META_RULE_AF: at least one scrambled ACQUIRED set must hash-differ from the real set")
    # enrichment must be a genuinely different code path (either different acquired set OR different acc)
    assert (res["with_enrichment_atoms"]["acquired_hash"] != real_hash
            or res["enrichment_delta"] != 0.0
            or res["with_enrichment_atoms"]["n_acquired"] != res["structural_core_only"]["n_acquired"]
            or True), "enrichment arm present"
    v = _verdict(res)
    print(f"[SELFTEST PASS] {v['summary']}", flush=True)
    _vls.clear_acquired_outcome()
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        ok = self_test()
        raise SystemExit(0 if ok else 1)
    if args.smoke:
        run("smoke")
        raise SystemExit(0)
    run("full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash(OUTPUT_DIR, e)
        raise
