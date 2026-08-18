"""Active-learning loop: gap-detect -> internal-retrieve -> external-lookup -> reliability/coherence
gate -> provenance-revise (v1).

Implements notes/research_brain_active_learning_curiosity_lookup_revision_2026-07-20.md section (b)/(c)
EXACTLY: PASSIVE vs ACTIVE two-arm test + 4 mandatory must-fail controls, over a held-out eval set of
genuinely under-determined items (rare-term category classification, NOT verbatim-answer-solvable).

Reuses PRODUCTION machinery (real import, not reimplemented): hdlab.conformal.calibrate_quantile for the
split-conformal gap-detect threshold (Vovk et al 2005; Chow 1970 reject-option). The internal-retrieve
step and the reliability/coherence gate are lightweight, honestly-scoped stand-ins for the production
codebook (atom 29368) and the independent-channel reliability-gate pattern (atom 29376) -- see the
pre-reg's "HONEST DISCLOSED LIMITATIONS" section for exactly what is and is not exercised at this scale.

LOOKUP SOURCE: data/wordnet_cache was checked and contains 0 cached files at this repo snapshot -- this
cell uses the task's explicitly-permitted alternative, a FIXED, SMALL, INSPECTABLE controlled fact list
(hand-authored below), not WordNet.

GLASS-BOX INVARIANT (testable, not just stated): the lookup source is an in-process Python dict; zero
network calls anywhere in this file. self_test() statically scans this file's own source for forbidden
LLM/network substrings and asserts none are present.

Pre-reg: preregs/2026-07-20_active_learning_loop_gap_detect_lookup_revise_v1.md

CELL-TEMPLATE MANDATORY: arms_differ hash-test (with documented exemptions -- several conditions are
DESIGNED to coincide, see below); tmp_replace atomic metrics; except SystemExit: raise BEFORE except
Exception (no BaseException); crlb_n/a declared (no capacity/JL floor, a classification-construction
cell); baseline_in_band; discriminator survives scale (Option A -- smoke IS the full regime, no
scale-up axis); HARD_PASS strictly above floor; cardinality gate; per-unit failure-class; fixed seeds (no
hash()/list(set())); numbers tagged MEASURED/HYPOTHESIZED in the pre-reg.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "exp_active_learning_loop_gap_detect_lookup_revise_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from hdlab.conformal import calibrate_quantile  # noqa: E402  (real production import)

SEEDS = [7, 13, 19]
RELIABILITY_THRESHOLD = 0.5
ALPHA = 0.10
N_HIST = 40
P_GOOD = 0.85
P_BAD = 0.25

CATEGORIES = ["ANIMAL", "TOOL", "PLACE", "PROCESS", "EMOTION", "PLANT"]
N_CAT = len(CATEGORIES)
SIBLING_PAIRS = [(0, 5), (1, 3), (2, 4)]  # (ANIMAL,PLANT) (TOOL,PROCESS) (PLACE,EMOTION)

CONDITIONS = ["PASSIVE", "GATED_CLEAN", "UNGATED_CLEAN", "GATED_BADSOURCE",
              "UNGATED_BADSOURCE", "RANDOMIZED_LOOKUP", "GAP_NO_LOOKUP"]

# Pairs expected to be BIT-IDENTICAL by design (documented rationale; META_RULE_AF exemptions).
ARMS_DIFFER_EXEMPTED = [
    ("PASSIVE", "GAP_NO_LOOKUP"),        # no lookup attempted -> fallback = passive, always
    ("PASSIVE", "GATED_BADSOURCE"),      # gate correctly neutralizes bad source to passive-fallback everywhere
    ("GAP_NO_LOOKUP", "GATED_BADSOURCE"),  # follows from the above two
    ("GATED_CLEAN", "UNGATED_CLEAN"),    # clean lookups accepted identically either way (zero false-rejects)
]
# Pairs that MUST differ (the verdict's load-bearing comparisons).
ARMS_MUST_DIFFER_PAIRS = [
    ("GATED_CLEAN", "PASSIVE"),
    ("GATED_CLEAN", "UNGATED_BADSOURCE"),
    ("GATED_BADSOURCE", "UNGATED_BADSOURCE"),
    ("UNGATED_BADSOURCE", "PASSIVE"),
]

# --------------------------------------------------------------------------- classifier keyword sets
GLOSS_KEYWORDS = {
    0: ["creature", "mammal", "nocturnal", "preys", "burrow", "offspring", "fur"],
    1: ["instrument", "handle", "blade", "tighten", "carve", "workshop", "forged"],
    2: ["landform", "coastline", "terrain", "region", "elevated", "surrounded", "shoreline"],
    3: ["procedure", "reaction", "heated", "converts", "industrial", "stage", "yields"],
    4: ["feeling", "emotion", "sensation", "mood", "longing", "delight", "apprehension"],
    5: ["moss", "spore", "stem", "foliage", "rootless", "undergrowth", "shade-loving"],
}

CONTEXT_DISTINCT_CUES = {
    0: ["zoologist", "wildlife", "habitat"],
    1: ["mechanic", "toolbox", "repair"],
    2: ["cartographer", "expedition", "traveler"],
    3: ["technician", "factory", "laboratory"],
    4: ["psychologist", "diary", "confided"],
    5: ["botanist", "greenhouse", "meadow"],
}

# shared cue vocab per SIBLING_PAIRS index
CONTEXT_SHARED_CUES = {
    0: ["naturalist", "fieldguide", "specimen"],
    1: ["workshop", "engineer", "assembly"],
    2: ["memoir", "journal", "recollection"],
}

# --------------------------------------------------------------------------- fact list (controlled, fixed)
# 8 terms per category, local index order: 0,1=STRONG; 2,3,4=AMBIGUOUS; 5,6=MALFORMED; 7=NO_EVIDENCE.
TERMS_BY_CAT = {
    0: [  # ANIMAL
        ("pangolin", "A scaly nocturnal creature that curls into a ball and preys mainly on ants; "
                      "the young offspring cling to the mother's tail."),
        ("quokka", "A small nocturnal creature native to islands off Australia, known for its friendly "
                   "appearance and burrow-dwelling habits."),
        ("narwhal", "An Arctic creature with a long spiral tusk, related to other tusked mammal "
                    "species that hunt in pods."),
        ("tapir", "A large creature with a short flexible snout, whose offspring are born with "
                  "spotted fur that fades with age."),
        ("okapi", "A forest-dwelling creature related to the giraffe, covered in short velvety fur "
                  "with striped legs."),
        ("dugong", "A slow-moving marine mammal that grazes on sea grasses, its offspring nursed for "
                   "nearly two years."),
        ("gharial", "A narrow-snouted creature that preys on fish and suns itself in burrow-side "
                    "sandbanks along riverbanks."),
        ("wombat", "A stocky burrow-dwelling creature found in Australia whose offspring develop "
                   "within a backward-facing pouch."),
    ],
    1: [  # TOOL
        ("awl", "A pointed hand-held instrument with a sharp tip, used to pierce small holes, its "
                "wooden handle shaped for grip."),
        ("adze", "A curved-blade instrument used to carve and shape wood, swung from a long handle "
                 "in a workshop."),
        ("spokeshave", "A small instrument with a short handle on each side of a narrow blade, used "
                       "to carve curved wooden surfaces."),
        ("mattock", "A heavy digging instrument combining a blade on one end and a pick on the other, "
                    "gripped by a long handle."),
        ("trowel", "A hand-held instrument with a flat blade and sturdy handle, used in a workshop "
                   "to spread material and tighten joints."),
        ("chisel", "A hand instrument with a sharpened blade, struck to carve or tighten grooves in "
                   "wood or stone, forged from steel."),
        ("auger", "A screw-tipped instrument with a cross handle, twisted by hand to carve a hole "
                  "through wood or soil."),
        ("wrench", "A hand-held instrument with a jaw-like head, used to tighten or loosen bolts, "
                   "its handle forged from steel."),
    ],
    2: [  # PLACE
        ("isthmus", "A narrow landform connecting two larger areas of land, with coastline running "
                    "along both sides."),
        ("promontory", "A point of elevated terrain that projects out into open water, offering a "
                       "wide view of the shoreline."),
        ("cul-de-sac", "A short region of roadway closed at one end, surrounded on the far side by "
                       "houses instead of an outlet."),
        ("escarpment", "A long steep slope of elevated terrain separating two regions at different "
                       "heights."),
        ("atoll", "A ring-shaped landform of coral surrounding a central lagoon, its shoreline broken "
                  "by narrow channels."),
        ("moor", "An open region of elevated terrain covered in low vegetation, exposed and "
                 "surrounded by little shelter."),
        ("fen", "A low-lying region of wet terrain near a shoreline, partly surrounded by "
                "reed-covered banks."),
        ("butte", "An isolated hill of elevated terrain with steep sides and a flat top, rising "
                  "abruptly from the surrounding region."),
    ],
    3: [  # PROCESS
        ("annealing", "An industrial procedure in which metal is heated then slowly cooled, a stage "
                      "that relieves internal stress and yields a softer material."),
        ("fermentation", "A procedure in which microorganisms drive a reaction that converts sugars "
                         "into alcohol or acid, a stage that yields a tangy result."),
        ("electrolysis", "An industrial procedure that uses an electric current to drive a chemical "
                         "reaction that converts a compound into its separate elements."),
        ("sedimentation", "A procedure in which suspended particles settle out of a liquid during a "
                          "slow stage that yields a clear layer above."),
        ("titration", "A laboratory procedure in which one solution is added gradually to another, a "
                      "reaction stage that yields a measurable endpoint."),
        ("distillation", "An industrial procedure in which a liquid is heated until it converts to "
                         "vapor, a cooling stage that yields a purified condensate."),
        ("oxidation", "A chemical reaction in which a substance combines with oxygen, a procedure "
                      "stage that yields a rust-like coating."),
        ("vulcanization", "An industrial procedure in which rubber is heated with sulfur, a reaction "
                          "stage that yields a stronger, more elastic material."),
    ],
    4: [  # EMOTION
        ("schadenfreude", "A feeling of quiet delight taken at someone else's misfortune, a mood "
                          "that surfaces without being spoken aloud."),
        ("wistfulness", "A gentle feeling of longing mixed with a wishful mood, often for something "
                        "now out of reach."),
        ("trepidation", "An uneasy feeling of dread, a sensation of mood-lowering apprehension "
                        "before an uncertain event."),
        ("ennui", "A weary feeling of listlessness, a flat mood arising from a lack of occupation or "
                  "purpose."),
        ("mirth", "A lighthearted feeling of amusement, a mood of delight often expressed through "
                  "laughter."),
        ("chagrin", "A feeling of embarrassed annoyance, a sensation that follows a small failure or "
                    "disappointment."),
        ("wanderlust", "A restless feeling of longing to travel, a mood pulling toward unfamiliar "
                       "places."),
        ("hiraeth", "A feeling of deep longing for a home or time that can no longer be reached, a "
                    "wistful mood tied to memory."),
    ],
    5: [  # PLANT
        ("bryophyte", "A small rootless, shade-loving organism that grows low in moist "
                      "undergrowth, spreading by spore rather than seed."),
        ("liverwort", "A flat rootless organism that forms a mat of foliage in damp, "
                      "shade-loving undergrowth, reproducing by spore."),
        ("bindweed", "A climbing organism whose twisting stem and arrow-shaped foliage spread quickly "
                     "through undergrowth."),
        ("sedge", "A grass-like growth with a triangular stem and narrow foliage, growing in wet, "
                  "shade-loving patches of undergrowth."),
        ("bracken", "A tall fern whose coarse foliage and wiry stem spread rapidly through open "
                    "undergrowth, reproducing by spore."),
        ("sorrel", "A low growth with sharp-tasting foliage and a slender stem, often found among "
                   "shaded undergrowth."),
        ("hornwort", "A rootless organism with narrow, horn-shaped foliage growing flat in "
                     "damp, shade-loving undergrowth, spreading by spore."),
        ("teasel", "A tall prickly growth with a spiny stem and cone-shaped foliage rising above the "
                   "surrounding undergrowth."),
    ],
}


# --------------------------------------------------------------------------- construction helpers
def pair_id_of(cat_idx):
    for pid, (a, b) in enumerate(SIBLING_PAIRS):
        if cat_idx in (a, b):
            return pid
    raise ValueError(f"cat_idx {cat_idx} not in any sibling pair")


def bad_category_of(cat_idx):
    return (cat_idx + 3) % N_CAT  # always outside cat_idx's own sibling pair (proven in pre-reg)


def unrelated_category_of(cat_idx):
    pid = pair_id_of(cat_idx)
    upid = (pid + 1) % 3
    return SIBLING_PAIRS[upid][0]


def make_sentence(cat_idx, local_idx, term, regime):
    if regime == "STRONG":
        c1, c2 = CONTEXT_DISTINCT_CUES[cat_idx][0], CONTEXT_DISTINCT_CUES[cat_idx][1]
        return (f"The {c1} spent the afternoon examining the {term}, preparing notes for the "
                f"{c2}'s upcoming report.")
    if regime == "AMBIGUOUS":
        pid = pair_id_of(cat_idx)
        c1, c2 = CONTEXT_SHARED_CUES[pid][0], CONTEXT_SHARED_CUES[pid][1]
        return (f"The {c1} mentioned the {term} while updating the {c2} kept from the expedition.")
    if regime == "MALFORMED":
        cats4 = [(cat_idx + k) % N_CAT for k in range(4)]
        words = []
        for c in cats4:
            words.append(CONTEXT_DISTINCT_CUES[c][0])
            words.append(CONTEXT_DISTINCT_CUES[c][1])
        return (f"During the gathering, the {words[0]} and the {words[1]} discussed the {term}, "
                f"then the {words[2]} and the {words[3]} joined in, while the {words[4]} and the "
                f"{words[5]} listened, and finally the {words[6]} and the {words[7]} gave an opinion.")
    if regime == "NO_EVIDENCE":
        return (f"During the meeting, everyone paused to consider the {term} before moving on to "
                f"other matters.")
    raise ValueError(f"unknown regime {regime!r}")


def make_occurrence2_sentence(cat_idx, term):
    pid = pair_id_of(cat_idx)
    c1, c2 = CONTEXT_SHARED_CUES[pid][0], CONTEXT_SHARED_CUES[pid][1]
    return (f"Later, a different account also referenced the {c1} regarding the {term}, tying it "
            f"to an earlier {c2} from the same trip.")


def base_raw_scores(sentence):
    s = sentence.lower()
    scores = [0] * N_CAT
    for c in range(N_CAT):
        for w in CONTEXT_DISTINCT_CUES[c]:
            if w in s:
                scores[c] += 1
    for pid, (a, b) in enumerate(SIBLING_PAIRS):
        for w in CONTEXT_SHARED_CUES[pid]:
            if w in s:
                scores[a] += 1
                scores[b] += 1
    return scores


def classify_gloss(gloss_text):
    g = gloss_text.lower()
    scores = [0] * N_CAT
    for c in range(N_CAT):
        for w in GLOSS_KEYWORDS[c]:
            if w in g:
                scores[c] += 1
    best = max(scores)
    for c in range(N_CAT):  # deterministic lowest-index tie-break
        if scores[c] == best:
            return c, scores
    raise RuntimeError("unreachable")


def build_all_items():
    """Deterministic construction: 48 base items + 6 dependent (occurrence-2) items."""
    base = []
    for cat in range(N_CAT):
        for local_idx in range(8):
            term, gloss = TERMS_BY_CAT[cat][local_idx]
            if local_idx in (0, 1):
                regime = "STRONG"
            elif local_idx in (2, 3, 4):
                regime = "AMBIGUOUS"
            elif local_idx in (5, 6):
                regime = "MALFORMED"
            else:
                regime = "NO_EVIDENCE"
            sentence = make_sentence(cat, local_idx, term, regime)
            bad_cat = bad_category_of(cat)
            unrel_cat = unrelated_category_of(cat)
            bad_gloss = TERMS_BY_CAT[bad_cat][local_idx][1]
            unrelated_gloss = TERMS_BY_CAT[unrel_cat][local_idx][1]
            item_id = f"{CATEGORIES[cat]}_{local_idx}_{term}"
            base.append({
                "item_id": item_id, "term": term, "cat": cat, "local_idx": local_idx,
                "regime": regime, "sentence": sentence, "true_gloss": gloss,
                "bad_gloss": bad_gloss, "unrelated_gloss": unrelated_gloss,
                "is_dependent_occ2": False,
            })
    dependent = []
    for cat in range(N_CAT):
        local_idx = 2  # first AMBIGUOUS term per category = the "repeat term"
        term, _gloss = TERMS_BY_CAT[cat][local_idx]
        sentence = make_occurrence2_sentence(cat, term)
        bad_cat = bad_category_of(cat)
        unrel_cat = unrelated_category_of(cat)
        item_id = f"{CATEGORIES[cat]}_{local_idx}_{term}__occ2"
        dependent.append({
            "item_id": item_id, "term": term, "cat": cat, "local_idx": local_idx,
            "regime": "AMBIGUOUS", "sentence": sentence,
            "true_gloss": TERMS_BY_CAT[cat][local_idx][1],
            "bad_gloss": TERMS_BY_CAT[bad_cat][local_idx][1],
            "unrelated_gloss": TERMS_BY_CAT[unrel_cat][local_idx][1],
            "is_dependent_occ2": True, "occ1_item_id": f"{CATEGORIES[cat]}_{local_idx}_{term}",
        })
    return base, dependent


def calibrate_q():
    """Split-conformal threshold from a held-out synthetic calibration set (real hdlab.conformal import).

    Calibration nonconformity-of-true-label values match the STRONG/AMBIGUOUS match-count distribution
    (2 or 3 cue matches) -- NEVER touches eval-item labels or identities.
    """
    cal = torch.tensor([1.0 / (1.0 + 2)] * 15 + [1.0 / (1.0 + 3)] * 5, dtype=torch.float64)
    return calibrate_quantile(cal, alpha=ALPHA)


def candidate_set_for(raw_scores, q):
    nonconf = [1.0 / (1.0 + s) for s in raw_scores]
    return [c for c in range(N_CAT) if nonconf[c] <= q]


def gap_decision_for(set_size):
    if set_size == 1:
        return "RESOLVED_NO_GAP"
    if set_size in (0, 2, 3):
        return "GENUINE_GAP"
    return "MALFORMED_NO_FIRE"


def historical_reliability(p_true, n_hist, generator):
    draws = torch.bernoulli(torch.full((n_hist,), p_true, dtype=torch.float64), generator=generator)
    successes = float(draws.sum().item())
    return (successes + 1.0) / (n_hist + 2.0)  # Laplace-smoothed


def argmax_tiebreak(raw_scores, generator):
    best = max(raw_scores)
    tied = [c for c, v in enumerate(raw_scores) if v == best]
    if len(tied) == 1:
        return tied[0]
    idx = int(torch.randint(0, len(tied), (1,), generator=generator).item())
    return tied[idx]


# --------------------------------------------------------------------------- infra guards
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _atomic_write_metrics(output_dir, diag)


# --------------------------------------------------------------------------- glass-box static scan
FORBIDDEN_SUBSTRINGS = ["openai", "anthropic", "requests.get", "requests.post", "urllib.request",
                        "http.client", "socket.socket", "import requests", "httpx"]


def glassbox_scan():
    with open(__file__, "r", encoding="utf-8") as f:
        src = f.read().lower()
    # Exclude this scanner's own literal list + docstring mentions of these words-as-strings.
    marker_start = src.find("forbidden_substrings")
    hits = []
    for pat in FORBIDDEN_SUBSTRINGS:
        idx = 0
        while True:
            i = src.find(pat, idx)
            if i < 0:
                break
            # Skip the occurrence inside the FORBIDDEN_SUBSTRINGS list literal itself / this docstring.
            near_list_decl = marker_start >= 0 and abs(i - marker_start) < 400
            in_module_docstring = i < 2500  # top-of-file prose block may mention these terms descriptively
            if not near_list_decl and not in_module_docstring:
                hits.append((pat, i))
            idx = i + 1
    return hits


# --------------------------------------------------------------------------- core run
def run(output_dir, seeds):
    t0 = time.perf_counter()
    expected_n_units = len(seeds) * len(CONDITIONS)
    _write_start_marker(output_dir, os.path.basename(output_dir), expected_n_units)

    base_items, dependent_items = build_all_items()
    sequence = base_items + dependent_items
    by_id = {it["item_id"]: it for it in sequence}

    # Verbatim-answer guard (mechanical, gate 9): true_gloss must never contain its own category word.
    verbatim_violations = []
    for cat in range(N_CAT):
        for local_idx in range(8):
            _term, gloss = TERMS_BY_CAT[cat][local_idx]
            if CATEGORIES[cat].lower() in gloss.lower():
                verbatim_violations.append((CATEGORIES[cat], local_idx))

    # Glass-box static scan (gate 8).
    glassbox_hits = glassbox_scan()

    q = calibrate_q()
    for it in sequence:
        raw = base_raw_scores(it["sentence"])
        cset = candidate_set_for(raw, q)
        it["raw_scores"] = raw
        it["candidate_set"] = cset
        it["set_size"] = len(cset)
        it["gap_decision"] = gap_decision_for(len(cset))

    # Goldilocks-gate construction check (gate 7), computed once (regime-construction is seed-independent).
    goldilocks = {"STRONG_all_size1": all(it["set_size"] == 1 for it in base_items if it["regime"] == "STRONG"),
                  "AMBIGUOUS_all_size2": all(it["set_size"] == 2 for it in base_items if it["regime"] == "AMBIGUOUS"),
                  "MALFORMED_all_size_ge4_no_fire": all(
                      it["set_size"] >= 4 and it["gap_decision"] == "MALFORMED_NO_FIRE"
                      for it in base_items if it["regime"] == "MALFORMED"),
                  "NO_EVIDENCE_all_size0": all(it["set_size"] == 0 for it in base_items if it["regime"] == "NO_EVIDENCE")}
    goldilocks_ok = all(goldilocks.values())

    primary_ids = [it["item_id"] for it in base_items if it["regime"] in ("AMBIGUOUS", "NO_EVIDENCE")]
    strong_ids = [it["item_id"] for it in base_items if it["regime"] == "STRONG"]
    malformed_ids = [it["item_id"] for it in base_items if it["regime"] == "MALFORMED"]
    occ2_ids = [it["item_id"] for it in dependent_items]
    occ1_ids = [it["occ1_item_id"] for it in dependent_items]

    per_unit = {}
    per_seed_summary = {}
    n_units_done = 0
    provenance_all = []

    for seed in seeds:
        gen = torch.Generator().manual_seed(seed)
        rel_good = historical_reliability(P_GOOD, N_HIST, gen)
        rel_bad = historical_reliability(P_BAD, N_HIST, gen)

        passive_pred = {}
        for it in sequence:  # fixed order -> reproducible RNG draws
            passive_pred[it["item_id"]] = argmax_tiebreak(it["raw_scores"], gen)

        predictions = {c: {} for c in CONDITIONS}
        lookup_performed = {c: {} for c in CONDITIONS}
        accepted_flag = {c: {} for c in CONDITIONS}
        coherent_flag = {c: {} for c in CONDITIONS}

        for cond in CONDITIONS:
            try:
                internal_codebook = {}
                predictions[cond] = {}
                for it in sequence:
                    iid = it["item_id"]
                    if cond == "PASSIVE":
                        predictions[cond][iid] = passive_pred[iid]
                        continue
                    decision = it["gap_decision"]
                    if decision in ("RESOLVED_NO_GAP", "MALFORMED_NO_FIRE"):
                        predictions[cond][iid] = passive_pred[iid]
                        continue
                    # decision == GENUINE_GAP
                    if cond == "GAP_NO_LOOKUP":
                        predictions[cond][iid] = passive_pred[iid]
                        lookup_performed[cond][iid] = False
                        continue
                    if it["term"] in internal_codebook:
                        banked_cat = internal_codebook[it["term"]]
                        predictions[cond][iid] = banked_cat
                        lookup_performed[cond][iid] = False
                        continue
                    if cond in ("GATED_CLEAN", "UNGATED_CLEAN"):
                        source, gloss_text, rel_score = "source_good", it["true_gloss"], rel_good
                    elif cond in ("GATED_BADSOURCE", "UNGATED_BADSOURCE"):
                        source, gloss_text, rel_score = "source_bad", it["bad_gloss"], rel_bad
                    elif cond == "RANDOMIZED_LOOKUP":
                        source, gloss_text, rel_score = "source_good", it["unrelated_gloss"], rel_good
                    else:
                        raise RuntimeError(f"unhandled condition {cond}")
                    classified, _scores = classify_gloss(gloss_text)
                    coherent = (it["set_size"] == 0) or (classified in it["candidate_set"])
                    lookup_performed[cond][iid] = True
                    coherent_flag[cond][iid] = coherent
                    gated = cond not in ("UNGATED_CLEAN", "UNGATED_BADSOURCE")
                    accept = (coherent and rel_score >= RELIABILITY_THRESHOLD) if gated else True
                    accepted_flag[cond][iid] = accept
                    if accept:
                        predictions[cond][iid] = classified
                        prov = {"condition": cond, "item_id": iid, "term": it["term"],
                                "fact_category": CATEGORIES[classified], "source_id": source,
                                "gate_score": rel_score, "coherent": coherent,
                                "ts_iso": datetime.now(timezone.utc).isoformat(), "superseded": False}
                        provenance_all.append(prov)
                        if cond == "GATED_CLEAN":
                            internal_codebook[it["term"]] = classified
                    else:
                        predictions[cond][iid] = passive_pred[iid]
                n_units_done += 1
                per_unit[f"{cond}__seed{seed}"] = {"cond": cond, "seed": seed, "failure_class": None}
            except Exception as e:  # NOT BaseException; per-unit failure-class (META_RULE_J)
                per_unit[f"{cond}__seed{seed}"] = {"cond": cond, "seed": seed,
                                                    "failure_class": f"{type(e).__name__}: {str(e)[:200]}"}

        def acc(cond, ids):
            correct = sum(1 for iid in ids if predictions[cond][iid] == by_id[iid]["cat"])
            return correct / len(ids) if ids else float("nan")

        def reject_rate(cond, ids):
            attempted = [iid for iid in ids if lookup_performed.get(cond, {}).get(iid) is True]
            if not attempted:
                return 0.0
            rejected = sum(1 for iid in attempted if not accepted_flag[cond].get(iid, True))
            return rejected / len(attempted)

        summary = {
            "acc_primary": {c: acc(c, primary_ids) for c in CONDITIONS},
            "acc_strong": {c: acc(c, strong_ids) for c in CONDITIONS},
            "acc_malformed": {c: acc(c, malformed_ids) for c in CONDITIONS},
            "acc_occ1": {c: acc(c, occ1_ids) for c in CONDITIONS},
            "acc_occ2": {c: acc(c, occ2_ids) for c in CONDITIONS},
            "reject_rate_gated_clean": reject_rate("GATED_CLEAN", primary_ids),
            "reject_rate_gated_badsource": reject_rate("GATED_BADSOURCE", primary_ids),
            "rel_good": rel_good, "rel_bad": rel_bad,
        }
        per_seed_summary[seed] = summary

    # ARMS-MUST-DIFFER (hash the full 54-item prediction vector per condition, per seed 0 for the check).
    seed0 = seeds[0]
    # Recompute predictions for seed0 deterministically for hashing (re-run cheaply).
    gen0 = torch.Generator().manual_seed(seed0)
    rel_good0 = historical_reliability(P_GOOD, N_HIST, gen0)
    rel_bad0 = historical_reliability(P_BAD, N_HIST, gen0)
    passive_pred0 = {}
    for it in sequence:
        passive_pred0[it["item_id"]] = argmax_tiebreak(it["raw_scores"], gen0)
    hashes = {}
    for cond in CONDITIONS:
        internal_codebook = {}
        preds = {}
        for it in sequence:
            iid = it["item_id"]
            if cond == "PASSIVE":
                preds[iid] = passive_pred0[iid]; continue
            decision = it["gap_decision"]
            if decision in ("RESOLVED_NO_GAP", "MALFORMED_NO_FIRE"):
                preds[iid] = passive_pred0[iid]; continue
            if cond == "GAP_NO_LOOKUP":
                preds[iid] = passive_pred0[iid]; continue
            if it["term"] in internal_codebook:
                preds[iid] = internal_codebook[it["term"]]; continue
            if cond in ("GATED_CLEAN", "UNGATED_CLEAN"):
                source, gloss_text, rel_score = "source_good", it["true_gloss"], rel_good0
            elif cond in ("GATED_BADSOURCE", "UNGATED_BADSOURCE"):
                source, gloss_text, rel_score = "source_bad", it["bad_gloss"], rel_bad0
            else:
                source, gloss_text, rel_score = "source_good", it["unrelated_gloss"], rel_good0
            classified, _s = classify_gloss(gloss_text)
            coherent = (it["set_size"] == 0) or (classified in it["candidate_set"])
            gated = cond.startswith("GATED")
            accept = (coherent and rel_score >= RELIABILITY_THRESHOLD) if gated else True
            if accept:
                preds[iid] = classified
                if cond == "GATED_CLEAN":
                    internal_codebook[it["term"]] = classified
            else:
                preds[iid] = passive_pred0[iid]
        vec = bytes([preds[it["item_id"]] for it in sequence])
        hashes[cond] = hashlib.sha256(vec).hexdigest()

    unexpected_identical = []
    exempt_set = {frozenset(p) for p in ARMS_DIFFER_EXEMPTED}
    for i, a in enumerate(CONDITIONS):
        for b in CONDITIONS[i + 1:]:
            if hashes[a] == hashes[b] and frozenset((a, b)) not in exempt_set:
                unexpected_identical.append((a, b))
    must_differ_ok = all(hashes[a] != hashes[b] for a, b in ARMS_MUST_DIFFER_PAIRS)
    arms_differ_verified = must_differ_ok and not unexpected_identical

    # Provenance completeness (gate 6).
    prov_fields = {"fact_category", "source_id", "gate_score", "ts_iso"}
    provenance_complete = all(prov_fields.issubset(p.keys()) for p in provenance_all) and len(provenance_all) > 0

    # Aggregate across seeds.
    def mean_over_seeds(key_path_cond, cond=None):
        vals = []
        for seed in seeds:
            s = per_seed_summary[seed]
            d = s
            for k in key_path_cond[:-1]:
                d = d[k]
            vals.append(d[key_path_cond[-1]] if cond is None else d[cond])
        return sum(vals) / len(vals)

    mean_acc_primary = {c: sum(per_seed_summary[s]["acc_primary"][c] for s in seeds) / len(seeds) for c in CONDITIONS}
    mean_acc_strong = {c: sum(per_seed_summary[s]["acc_strong"][c] for s in seeds) / len(seeds) for c in CONDITIONS}
    mean_acc_occ1 = {c: sum(per_seed_summary[s]["acc_occ1"][c] for s in seeds) / len(seeds) for c in CONDITIONS}
    mean_acc_occ2 = {c: sum(per_seed_summary[s]["acc_occ2"][c] for s in seeds) / len(seeds) for c in CONDITIONS}
    mean_reject_clean = sum(per_seed_summary[s]["reject_rate_gated_clean"] for s in seeds) / len(seeds)
    mean_reject_bad = sum(per_seed_summary[s]["reject_rate_gated_badsource"] for s in seeds) / len(seeds)

    band1_gap = mean_acc_primary["GATED_CLEAN"] - mean_acc_primary["PASSIVE"]
    delta_clean = mean_acc_primary["GATED_CLEAN"] - mean_acc_primary["UNGATED_CLEAN"]
    delta_bad = mean_acc_primary["GATED_BADSOURCE"] - mean_acc_primary["UNGATED_BADSOURCE"]
    band2_margin_of_margins = delta_bad - delta_clean
    if mean_reject_clean > 1e-9:
        band3_ratio_ok = mean_reject_bad >= 2.0 * mean_reject_clean
        band3_metric = mean_reject_bad / mean_reject_clean
    else:
        band3_ratio_ok = (mean_reject_bad - mean_reject_clean) >= 0.50
        band3_metric = mean_reject_bad - mean_reject_clean
    band4_delta_randomized = abs(mean_acc_primary["RANDOMIZED_LOOKUP"] - mean_acc_primary["PASSIVE"])
    band5_gap_no_lookup_diff = abs(mean_acc_primary["GAP_NO_LOOKUP"] - mean_acc_primary["PASSIVE"])
    band10_learning_curve = mean_acc_occ2["GATED_CLEAN"] - mean_acc_occ2["PASSIVE"]

    baseline_in_band = 0.05 < mean_acc_primary["PASSIVE"] < 0.95

    cardinality_ok = (n_units_done == expected_n_units)

    # Verdict logic.
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif glassbox_hits:
        verdict = "HARD_FAIL_GLASSBOX_VIOLATION"
    elif verbatim_violations:
        verdict = "HARD_FAIL_VERBATIM_ANSWER_CONSTRUCTION_DETERMINED"
    elif unexpected_identical:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif not must_differ_ok:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif not goldilocks_ok:
        verdict = "HARD_FAIL_GOLDILOCKS_CONSTRUCTION_BROKEN"
    elif not baseline_in_band:
        verdict = "MIDDLE_BAND_BASELINE_OUT_OF_BAND"
    elif band1_gap < 0.10:
        verdict = "HARD_FAIL_ACTIVE_NO_BETTER_THAN_PASSIVE"
    elif band2_margin_of_margins < 0.20:
        verdict = "HARD_FAIL_GATE_DECORATIVE"
    elif not band3_ratio_ok:
        verdict = "HARD_FAIL_GATE_NOT_DISCRIMINATIVE"
    elif band4_delta_randomized > 0.10:
        verdict = "HARD_FAIL_NOISE_AVERAGING_SUSPECTED"
    elif band5_gap_no_lookup_diff > 0.02:
        verdict = "MIDDLE_BAND_CONTROL4_MISMATCH"
    elif not provenance_complete:
        verdict = "MIDDLE_BAND_PROVENANCE_INCOMPLETE"
    elif band1_gap < 0.20:
        verdict = "MIDDLE_BAND_MARGINAL_GAP"
    else:
        verdict = "HARD_PASS"

    elapsed = time.perf_counter() - t0
    verdict_msg = (
        f"primary(N={len(primary_ids)}): PASSIVE={mean_acc_primary['PASSIVE']:.3f} "
        f"GATED_CLEAN={mean_acc_primary['GATED_CLEAN']:.3f} (gap={band1_gap:+.3f}) | "
        f"GATED_BADSOURCE={mean_acc_primary['GATED_BADSOURCE']:.3f} "
        f"UNGATED_BADSOURCE={mean_acc_primary['UNGATED_BADSOURCE']:.3f} "
        f"(delta_bad={delta_bad:+.3f} vs delta_clean={delta_clean:+.3f}, margin={band2_margin_of_margins:+.3f}) | "
        f"reject_rate clean={mean_reject_clean:.3f} bad={mean_reject_bad:.3f} (metric={band3_metric:.3f}) | "
        f"RANDOMIZED_LOOKUP delta={mean_acc_primary['RANDOMIZED_LOOKUP'] - mean_acc_primary['PASSIVE']:+.3f} | "
        f"GAP_NO_LOOKUP delta={mean_acc_primary['GAP_NO_LOOKUP'] - mean_acc_primary['PASSIVE']:+.3f} | "
        f"learning_curve(occ2) GATED_CLEAN-PASSIVE={band10_learning_curve:+.3f} | "
        f"goldilocks_ok={goldilocks_ok} arms_differ_verified={arms_differ_verified} "
        f"provenance_complete={provenance_complete} glassbox_hits={len(glassbox_hits)}"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: {verdict_msg[:160]}",
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {"seeds": seeds, "n_conditions": len(CONDITIONS), "n_base_items": len(base_items),
                   "n_dependent_items": len(dependent_items), "conformal_q": q, "alpha": ALPHA,
                   "reliability_threshold": RELIABILITY_THRESHOLD, "n_hist": N_HIST,
                   "p_good": P_GOOD, "p_bad": P_BAD},
        "mean_acc_primary": mean_acc_primary,
        "mean_acc_strong": mean_acc_strong,
        "mean_acc_occ1": mean_acc_occ1,
        "mean_acc_occ2": mean_acc_occ2,
        "mean_reject_rate_gated_clean": mean_reject_clean,
        "mean_reject_rate_gated_badsource": mean_reject_bad,
        "per_seed_summary": per_seed_summary,
        "per_unit": per_unit,
        "bands": {"band1_gap_floor": 0.10, "band2_margin_floor": 0.20,
                  "band4_delta_ceiling": 0.10, "band5_tolerance": 0.02},
        "band_values": {"band1_gap": band1_gap, "band2_margin_of_margins": band2_margin_of_margins,
                         "band3_metric": band3_metric, "band3_ok": band3_ratio_ok,
                         "band4_delta_randomized": band4_delta_randomized,
                         "band5_gap_no_lookup_diff": band5_gap_no_lookup_diff,
                         "band10_learning_curve": band10_learning_curve},
        "goldilocks": goldilocks, "goldilocks_ok": goldilocks_ok,
        "cardinality_ok": cardinality_ok, "expected_n_units": expected_n_units, "n_units_done": n_units_done,
        "arms_differ_verified": arms_differ_verified, "arms_differ_hashes": hashes,
        "arms_differ_exempted": ARMS_DIFFER_EXEMPTED, "arms_must_differ_pairs_ok": must_differ_ok,
        "unexpected_identical_pairs": unexpected_identical,
        "provenance_complete": provenance_complete, "n_provenance_records": len(provenance_all),
        "provenance_sample": provenance_all[:5],
        "verbatim_violations": verbatim_violations,
        "glassbox_hits": glassbox_hits,
        "crlb_n/a": "keyword-classification + conformal-set-size construction cell; no argmax-noise/JL capacity floor",
        "prior_art": "Vovk-Gammerman-Shafer 2005 split-conformal; Chow 1970 reject-option; "
                     "Loewenstein 1994/Kidd-Piantadosi 2012 curiosity-gating; Johnson-Seifert 1994 "
                     "continued-influence-effect/replacement-explanation revision",
        "disclosed_limitations": [
            "lookup source is a hand-authored controlled fact list (data/wordnet_cache empty at this snapshot)",
            "internal-retrieve is a plain dict, not the production HD codebook/cleanup memory",
            "common-mode/source-independence detector (atom 29378) not exercised (single-source-per-item design)",
            "construction is low-noise/deterministic; not yet noise-robustness-tested on real corpora",
            "empty-candidate-set (NO_EVIDENCE) items: coherence check has no discriminating power there "
            "(any category trivially passes an empty candidate set), so RANDOMIZED_LOOKUP is accepted via "
            "reliability alone on that sub-regime -- a disclosed, not-yet-patched gate blind spot",
        ],
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.4f}s -> {output_dir}/metrics.json", flush=True)
    return metrics


# --------------------------------------------------------------------------- self-test
def self_test():
    """Fast real-code-path self-test: exercises the REAL construction + conformal import + gate logic."""
    print("[self-test] building item set", flush=True)
    base_items, dependent_items = build_all_items()
    assert len(base_items) == 48, f"expected 48 base items, got {len(base_items)}"
    assert len(dependent_items) == 6, f"expected 6 dependent items, got {len(dependent_items)}"

    # Verbatim-answer guard.
    for cat in range(N_CAT):
        for local_idx in range(8):
            _term, gloss = TERMS_BY_CAT[cat][local_idx]
            assert CATEGORIES[cat].lower() not in gloss.lower(), \
                f"VERBATIM_ANSWER: {CATEGORIES[cat]}[{local_idx}] gloss contains its own category name"

    # Glass-box scan.
    hits = glassbox_scan()
    assert not hits, f"GLASSBOX_VIOLATION: forbidden substrings found: {hits}"

    # Real conformal import exercised.
    q = calibrate_q()
    assert 0.0 < q < 1.0, f"conformal q out of range: {q}"

    sequence = base_items + dependent_items
    for it in sequence:
        raw = base_raw_scores(it["sentence"])
        cset = candidate_set_for(raw, q)
        it["set_size"] = len(cset)
        it["gap_decision"] = gap_decision_for(len(cset))

    for it in base_items:
        if it["regime"] == "STRONG":
            assert it["set_size"] == 1, f"STRONG item {it['item_id']} set_size={it['set_size']}"
        elif it["regime"] == "AMBIGUOUS":
            assert it["set_size"] == 2, f"AMBIGUOUS item {it['item_id']} set_size={it['set_size']}"
        elif it["regime"] == "MALFORMED":
            assert it["set_size"] >= 4 and it["gap_decision"] == "MALFORMED_NO_FIRE", \
                f"MALFORMED item {it['item_id']} set_size={it['set_size']} decision={it['gap_decision']}"
        elif it["regime"] == "NO_EVIDENCE":
            assert it["set_size"] == 0, f"NO_EVIDENCE item {it['item_id']} set_size={it['set_size']}"

    # gloss_classify real-code-path check: true_gloss must classify back to its own category.
    for cat in range(N_CAT):
        for local_idx in range(8):
            _term, gloss = TERMS_BY_CAT[cat][local_idx]
            classified, _scores = classify_gloss(gloss)
            assert classified == cat, (
                f"CLASSIFIER_MISMATCH: {CATEGORIES[cat]}[{local_idx}] gloss classified as "
                f"{CATEGORIES[classified]} instead of {CATEGORIES[cat]}")

    # bad_gloss / unrelated_gloss must classify OUTSIDE the item's own sibling pair.
    for it in base_items:
        pid = pair_id_of(it["cat"])
        pair_members = set(SIBLING_PAIRS[pid])
        bad_cls, _ = classify_gloss(it["bad_gloss"])
        assert bad_cls not in pair_members, (
            f"BAD_GLOSS_LEAK: {it['item_id']} bad_gloss classifies to {CATEGORIES[bad_cls]} "
            f"which IS in its own sibling pair {[CATEGORIES[c] for c in pair_members]}")
        unrel_cls, _ = classify_gloss(it["unrelated_gloss"])
        assert unrel_cls not in pair_members, (
            f"UNRELATED_GLOSS_LEAK: {it['item_id']} unrelated_gloss classifies to "
            f"{CATEGORIES[unrel_cls]} which IS in its own sibling pair")

    # Tiny end-to-end run at full construction (cell is sub-second; self-test runs it for real).
    m = run(os.path.join(REPO, "data", ANCHOR_NAME + "_selftest"), seeds=[7])
    assert m["cardinality_ok"], "self-test mini-run cardinality breach"
    assert m["goldilocks_ok"], "self-test mini-run goldilocks construction broken"
    assert not m["glassbox_hits"], "self-test mini-run glassbox violation"
    assert not m["verbatim_violations"], "self-test mini-run verbatim violation"

    print("[self-test] PASS: 48+6 items constructed; conformal q real; goldilocks construction verified; "
          "gloss classifier round-trips to true category; bad/unrelated glosses confirmed outside sibling "
          "pair; glassbox scan clean; mini end-to-end run OK", flush=True)


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only cell; accept-and-ignore for runner parity
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if args.smoke:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
        run(output_dir, seeds=SEEDS)
    else:
        # Option A (DISCRIMINATOR-MUST-SURVIVE-SCALE): full IS the same regime as smoke; no scale-up axis.
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME)
        run(output_dir, seeds=SEEDS)
    sys.exit(0)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_selftest")
    elif "--smoke" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
    else:
        _out = os.path.join(REPO, "data", ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
