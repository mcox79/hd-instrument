"""AFFECTEDNESS / CHANGE-OF-STATE PATIENT-SELECTION DESIGN-GATE (v1).

The forensic component-audit of CPCL-v2 (2026-07-19) proved the entity-recurrence continuation target is
UNCORRELATED with per-instance patient-correctness (corr ~ 0; min-err selects gold BELOW chance) -- the 6th
text-internal self-supervised signal to fail the SAME residual (cosine/distributional-similarity, animacy,
coref, scene-coherence, thematic-fit, entity-recurrence). The forensic's explicit REVIVAL prescription: before
wiring ANY future candidate signal into a loop, MEASURE corr(candidate_signal, gold_patient_correct) and
require it clear a floor (~0.2) FIRST -- a corr~0 target cannot be rescued by re-running; catch it at a
design-gate instead of burning a full loop run. This cell IS that design-gate for the VET's prescribed next
signal class: GROUNDED / weak-supervised AFFECTEDNESS (Dowty 1991 proto-patient entailments; Talmy 1988
force-dynamics), operationalized as a hand-curated ontology LOOKUP -- weak-supervised/curated, NOT
self-supervised-from-corpus-statistics (the class of signal distinct in KIND from the 6 failures).

CONTRACT: measure ONLY. Do NOT build a contrastive loop here. A loop is warranted only if a candidate signal
clears the pre-registered correlation floor (see preregs/2026-07-19_affectedness_change_of_state_patient_
selection_design_gate_v1.md).

CANDIDATE SIGNALS (measured, not tuned-for-pass):
  1. SIG_PROTO_PATIENT_ONTOLOGY: Dowty-motivated closed-class lexicon over the candidate patient's head token
     -> scalar affectedness (ARTIFACT/CONCRETE +1.0, ANIMATE +0.8, BODY_PART +0.6, ABSTRACT -0.3,
     LOCATION/PLACE -1.0; pronouns/funcwords -> None/neutral, needs coref, not conflated here).
  2. SIG_PLACE_GAZETTEER_EXCLUSION: narrower binary -1-if-place-else-0 subset, isolating JUST the
     locative-exclusion hypothesis the forensic audit directly measured as the confound.
  3. SIG_COS_VERB_GATED_ONTOLOGY: signal-1 gated to 0.0 unless the verb is in a hand-curated Change-of-
     State/Creation/Destruction/Contact-effect Levin-style verb class.

EXTENSION (2026-07-19, Director brain-drill 3x, notes/research_brain_patienthood_affectedness_grounding_
2026-07-20.md): the ~0.557 reader behaves like a Caramazza-Zurif agrammatic patient -- lacking syntactic/
trace representation, it falls back on linear-order/frequency heuristics and fails reversible cases. None of
the 6 failed signals tested structural argument-linking / affectedness-ENTAILMENT. Three more candidates,
gated the same way:
  4. SIG_VERBNET_COS_GATED_ONTOLOGY: signal-1 gated by REAL NLTK VerbNet classids (not a hand list) --
     verb_is_cos = True iff any of the verb's VerbNet classids has Levin group number 45 (Break / Other
     Change-of-State) or 26 (Create and Transform). This is literally "Levin/VerbNet causative-inchoative
     CLASS membership" (candidate A in the drill), using the SAME curated-lookup/weak-supervision framing as
     signal-3 but grounded in real VerbNet data instead of a hand-guessed verb list (both reported so the
     hand-list vs VerbNet framings can be compared).
  5. SIG_ALTERNATION_TEXT_INTERNAL: the genuinely TEXT-INTERNAL / self-supervised-from-raw-text candidate
     (candidate B) -- Levin's OWN causative-inchoative diagnostic procedure operationalized as a corpus scan:
     does the candidate patient token p appear, ANYWHERE in the (held-out-from-eval) mining corpus, as the
     SUBJECT of an INTRANSITIVE use of the SAME verb v (no direct object following) OR as the subject of a
     "aux-be + v-participle" PASSIVE use? No lexicon imported for this one (only the pre-existing FUNCWORD/
     PRONOUN closed-class lists already used throughout LCCP's structural cues). Scan coverage /
     non-vacuousness is checked explicitly before the corr is trusted (a verb+corpus too small to show ANY
     alternation evidence would produce a spurious null, not a real one).
  6. SIG_ALTERNATION_ANIMACY_GATED: candidate C -- signal-5 gated to 0.0 when p is in the ANIMATE_BEING
     lexicon (animate intransitive-subjects are more often unergative AGENTS -- "he ran" -- than unaccusative
     PATIENTS -- "the door opened"; animacy used ONLY as a co-feature here, per the drill's explicit framing,
     not retried standalone).
  Sanity controls: SIG_ORACLE_LABEL (must corr=1.000 exactly) + SIG_RANDOM_CONTROL (must |corr|<0.15).

EXPLICITLY NOT RETRIED (avoid rediscovery; logged not silently dropped): plain ANIMACY-alone standalone,
distributional THEMATIC-FIT (GloVe verb-centroid cosine), ENTITY-RECURRENCE, COREFERENCE, SCENE-COHERENCE,
raw cosine/distributional-similarity, object-typicality/selectional-coherence (closed per atoms af19aa9d
graded-fit HARD_FAIL + a5f2c3d0 SCV null-trainer even at gold-perfect oracle=0.000) -- ALL already tried +
FAILED at this same residual; none re-run here.

MEASUREMENT METHODOLOGY (mirrors the forensic CHECK-1 methodology exactly, for direct comparability):
  Eval set = SAME held-out third-reader gold slice CPCL-v2 used (225 reader candidates via
  CPCL.build_candidates, 44 gold-correct via L.match_pos; no new annotation).
  corr_all / corr_content_subset (Pearson, None-scored candidates excluded from content_subset + reported as
  a separate coverage %); selection_rate_vs_chance (argmax(signal) picks gold over multi-rival groups where
  gold is among the rivals; chance = mean(1/n_rivals) over those groups, matching the forensic's methodology
  exactly, e.g. their "chance_rate": 0.386 for n=19 groups).

PRE-REGISTERED BANDS (see prereg; NOT tuned):
  HARD_PASS_DESIGN_GATE: >=1 candidate corr_content_subset >= 0.20 AND selection_rate - chance >= +0.10.
  MIDDLE_BAND_DESIGN_GATE: best candidate in [0.10, 0.20) or the two measures disagree.
  HARD_FAIL_DESIGN_GATE: no candidate clears corr>=0.10 AND none beats chance by >=+0.05.
  SANITY GATE (blocks all): SIG_ORACLE_LABEL corr must be exactly 1.000; SIG_RANDOM_CONTROL |corr| < 0.15.

COMPUTE ARCHITECTURE: class (b) sequential-CPU, trivially fast (~1-3s; cached LCCP reader run + dict-lookup
  scoring over 225 candidates; NOT a batching candidate). storage=no_storage. final_metrics_atomicity=
  tmp_replace. crlb_n/a (categorical-lookup correlation-gate, no quantitative noise-floor formula applies).
  No sweep axis, no seeds (fully deterministic except SIG_RANDOM_CONTROL's own fixed seed). LOCAL,
  foreground-to-completion (COMPUTE-PROPORTIONALITY: cheapest decisive method for a correlation/gate
  question -- no training, no queue).
CELL-TEMPLATE MANDATORY: except SystemExit: raise BEFORE except Exception (no BaseException); no bare
  except / no silent-continue; final_metrics_atomicity=tmp_replace; all report numbers tagged in metrics.
ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "affectedness_change_of_state_patient_selection_design_gate_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_contrastive_entity_recurrence_reader_loop_cpcl_v2 as CPCL  # noqa: E402
from experiments import exp_scene_coherence_verifier_contrastive_scv_v1 as S  # noqa: E402 (mining files + VerbNet)

try:
    from nltk.corpus import verbnet as vn  # noqa: E402
    _VERBNET_AVAILABLE = True
except Exception:
    vn = None
    _VERBNET_AVAILABLE = False

GOLD_SLICE_FULL = ["L04", "L05", "L07", "L08", "L09", "L10", "L12"]
GOLD_SLICE_SMOKE = ["L04", "L05"]
COS_VERBNET_GROUPS = {"45", "26"}  # Levin 1993: ch.45 Break/Other Change-of-State, ch.26 Create+Transform
AUX_BE = {"was", "were", "is", "are", "been", "be", "being"}

# ==================================================================================================
# Pre-registered bands (declared BEFORE running; NOT tuned to pass).
# ==================================================================================================
HP_CORR = 0.20
HP_SEL_MARGIN = 0.10
MB_CORR = 0.10
MB_SEL_MARGIN = 0.05
SANITY_ORACLE_CORR_MIN = 0.999
SANITY_RANDOM_CORR_MAX = 0.15
RANDOM_CONTROL_SEED = 2026

# ==================================================================================================
# Dowty/Talmy-motivated proto-patient ontology lexicon (general English vocabulary; argued from category
# membership, NOT fit to maximize corr on this eval set -- see prereg's non-construction-guard note).
# ==================================================================================================
ARTIFACT_CONCRETE = {
    "book", "books", "copybook", "castle", "castles", "hut", "huts", "house", "houses", "blockhouse",
    "dam", "boat", "boats", "ship", "ships", "wheel", "wheels", "kite", "kites", "box", "boxes",
    "basket", "baskets", "coat", "coats", "cup", "cups", "bowl", "bowls", "tool", "tools", "letter",
    "letters", "picture", "pictures", "cake", "cakes", "bread", "wood", "block", "blocks", "mark",
    "marks", "seed", "seeds", "fur", "bark", "wall", "walls", "bridge", "bridges", "gate", "gates",
    "door", "doors", "table", "tables", "chair", "chairs", "hat", "hats", "shoe", "shoes", "ball",
    "balls", "top", "tops", "pen", "pencil", "pencils", "sled", "sword", "swords", "flag", "flags",
    "nest", "nests", "fire", "fires", "dress", "dresses", "wagon", "wagons", "cart", "carts", "fence",
    "fences", "money", "foundation", "foundations",
}
ANIMATE_BEING = {
    "dog", "dogs", "cat", "cats", "pussy", "boy", "boys", "girl", "girls", "child", "children", "man",
    "men", "woman", "women", "animal", "animals", "beaver", "beavers", "fish", "bird", "birds",
    "horse", "horses", "cow", "cows", "sheep", "lamb", "lambs", "mother", "father", "parent",
    "parents", "son", "sons", "daughter", "daughters", "brother", "sister", "friend", "friends",
    "teacher", "gardener", "fisherman", "baby", "babies",
}
BODY_PART = {
    "head", "heads", "hand", "hands", "face", "faces", "forehead", "foreheads", "eye", "eyes", "foot",
    "feet", "arm", "arms", "leg", "legs", "hair", "ear", "ears", "mouth", "nose", "finger", "fingers",
    "tail", "tails", "wing", "wings", "paw", "paws",
}
ABSTRACT_QUALITY_EVENT = {
    "grief", "joy", "beauty", "name", "names", "sentence", "sentences", "lesson", "lessons", "time",
    "times", "hour", "hours", "harm", "way", "ways", "ruin", "thought", "thoughts", "idea", "ideas",
    "love", "fear", "hope", "plan", "plans", "word", "words", "sound", "sounds", "mew", "story",
    "stories", "tale", "tales",
}
LOCATION_PLACE_SETTING = {
    "garden", "gardens", "home", "room", "rooms", "place", "places", "field", "fields", "yard",
    "yards", "town", "towns", "village", "villages", "road", "roads", "path", "paths", "school",
    "church", "market", "country", "ground", "forest", "river", "shore", "sky", "window", "windows",
    "city", "cities", "street", "streets", "farm", "farms", "hill", "hills", "valley", "valleys",
    "world",
}
ONTOLOGY_SCORE = {}
for _t in ARTIFACT_CONCRETE:
    ONTOLOGY_SCORE[_t] = 1.0
for _t in ANIMATE_BEING:
    ONTOLOGY_SCORE[_t] = 0.8
for _t in BODY_PART:
    ONTOLOGY_SCORE[_t] = 0.6
for _t in ABSTRACT_QUALITY_EVENT:
    ONTOLOGY_SCORE[_t] = -0.3
for _t in LOCATION_PLACE_SETTING:
    ONTOLOGY_SCORE[_t] = -1.0

# Levin-style Change-of-State / Creation / Destruction / Contact-effect verb class (lemma form, matches
# L.lemma_verb output). Hand-curated, general verb-class knowledge, not fit to this eval set.
COS_VERB_CLASS = {
    "build", "make", "form", "break", "open", "close", "tear", "burn", "melt", "cook", "paint", "rub",
    "knock", "dig", "cut", "kill", "hurt", "wash", "dye", "spin", "knit", "write", "draw", "catch",
    "throw", "chop", "bake", "peel", "brush", "hammer",
}


def sig_proto_patient_ontology(p, v):
    """Dowty-motivated affectedness score for candidate patient head token p. None = neutral/no-signal
    (pronoun or function word -- these need coreference, a separate already-failed signal class)."""
    if p in L.PRONOUN or p in L.FUNCWORD:
        return None
    return ONTOLOGY_SCORE.get(p)  # None if OOV (not in any bucket)


def sig_place_gazetteer_exclusion(p, v):
    """Narrower binary locative-exclusion signal (subset of signal-1's LOCATION bucket)."""
    if p in L.PRONOUN or p in L.FUNCWORD:
        return None
    if p in LOCATION_PLACE_SETTING:
        return -1.0
    if p in ONTOLOGY_SCORE:
        return 0.0
    return None  # OOV: no lexicon coverage either way


def sig_cos_verb_gated_ontology(p, v):
    """SIG_PROTO_PATIENT_ONTOLOGY gated to 0.0 unless the verb is a Change-of-State/Creation/Destruction/
    Contact-effect class member (per Levin). Verb is CONSTANT within a rival-group; this only changes the
    per-candidate value via the (constant) gate multiplied by the (per-candidate) ontology term."""
    base = sig_proto_patient_ontology(p, v)
    if base is None:
        return None
    return base if v in COS_VERB_CLASS else 0.0


_VERBNET_COS_CACHE = {}


def verbnet_is_cos_class(v_lemma):
    """True iff any of v_lemma's REAL NLTK VerbNet classids has Levin group 45 (Break/Other-COS) or 26
    (Create+Transform). Memoized. Returns False (not None) if VerbNet unavailable or lemma unknown --
    logged via VERBNET_AVAILABLE at the metrics level, not silently swallowed."""
    if v_lemma in _VERBNET_COS_CACHE:
        return _VERBNET_COS_CACHE[v_lemma]
    result = False
    if _VERBNET_AVAILABLE:
        try:
            cids = vn.classids(v_lemma)
        except LookupError:
            cids = []
        for cid in cids:
            parts = cid.split("-")
            if len(parts) < 2:
                continue
            grp = parts[1].split(".")[0]
            if grp in COS_VERBNET_GROUPS:
                result = True
                break
    _VERBNET_COS_CACHE[v_lemma] = result
    return result


def sig_verbnet_cos_gated_ontology(p, v):
    """SIG_PROTO_PATIENT_ONTOLOGY gated by REAL VerbNet causative-inchoative class membership (not a hand
    list). Candidate (A) per the 2026-07-19 brain-drill, VerbNet framing."""
    base = sig_proto_patient_ontology(p, v)
    if base is None:
        return None
    return base if verbnet_is_cos_class(v) else 0.0


def _find_subject_before(toks, vi):
    """Walk left from position vi (exclusive), skipping FUNCWORD, to find a lexical NP-head subject
    candidate. Returns None for pronouns (need coref, not conflated here) or if nothing lexical found."""
    j = vi - 1
    while j >= 0 and toks[j] in L.FUNCWORD:
        j -= 1
    if j < 0:
        return None
    cand = toks[j]
    if cand in L.PRONOUN:
        return None
    if not cand.isalpha() or len(cand) < 2:
        return None
    return cand


def scan_alternation_evidence(mining_files, v_scan):
    """Levin's causative-inchoative diagnostic as a raw TEXT-INTERNAL corpus scan (no lexicon; only the
    pre-existing FUNCWORD/PRONOUN closed classes). For each verb lemma in v_scan, record every lexical NP
    head token seen as the SUBJECT of (a) an INTRANSITIVE use (no direct object following) or (b) a
    "aux-be + participle" PASSIVE use, of that SAME verb, anywhere in mining_files. Returns
    (alt_map: {v_lemma: set(subject_tokens)}, n_intrans_hits, n_passive_hits)."""
    alt_map = defaultdict(set)
    n_intrans = 0
    n_passive = 0
    for rel in mining_files:
        with open(os.path.join(REPO_ROOT, rel), encoding="utf-8") as f:
            text = f.read()
        for sent in L.split_sents(text):
            toks = L.tokenize(sent)
            n = len(toks)
            for i, tok in enumerate(toks):
                vlem = L.lemma_verb(tok)
                if vlem not in v_scan:
                    continue
                prev1 = toks[i - 1] if i - 1 >= 0 else ""
                prev2 = toks[i - 2] if i - 2 >= 0 else ""
                is_passive = (prev1 in AUX_BE) or (prev2 in AUX_BE)
                if is_passive:
                    aux_idx = i - 1 if prev1 in AUX_BE else i - 2
                    subj = _find_subject_before(toks, aux_idx)
                    if subj:
                        alt_map[vlem].add(subj)
                        n_passive += 1
                    continue
                subj = _find_subject_before(toks, i)
                if subj is None:
                    continue
                nxt = toks[i + 1] if i + 1 < n else None
                obj_present = (nxt is not None and nxt.isalpha() and len(nxt) >= 2
                               and nxt not in L.FUNCWORD)
                if not obj_present:
                    alt_map[vlem].add(subj)
                    n_intrans += 1
    return alt_map, n_intrans, n_passive


def sig_alternation_text_internal(p, v, alt_map):
    """Candidate B: pure text-internal alternation evidence. None for pronoun/funcword p (needs coref)."""
    if p in L.PRONOUN or p in L.FUNCWORD:
        return None
    return 1.0 if p in alt_map.get(v, ()) else 0.0


def sig_alternation_animacy_gated(p, v, alt_map):
    """Candidate C: signal-5 gated to 0.0 when p is animate (co-feature only, not a standalone re-test of
    the already-failed plain-animacy signal)."""
    base = sig_alternation_text_internal(p, v, alt_map)
    if base is None:
        return None
    return 0.0 if p in ANIMATE_BEING else base


def sig_oracle_label(p, v, label):
    """Positive sanity control: the gold label itself. MUST corr = 1.000 exactly."""
    return float(label)


def sig_random_control(p, v, idx, rng):
    """Negative sanity control: fixed-seed random score, independent of p/v/label. MUST |corr| < 0.15."""
    return float(rng.standard_normal())


SIGNAL_NAMES = ["SIG_PROTO_PATIENT_ONTOLOGY", "SIG_PLACE_GAZETTEER_EXCLUSION", "SIG_COS_VERB_GATED_ONTOLOGY",
                "SIG_VERBNET_COS_GATED_ONTOLOGY", "SIG_ALTERNATION_TEXT_INTERNAL",
                "SIG_ALTERNATION_ANIMACY_GATED"]
CONTROL_NAMES = ["SIG_ORACLE_LABEL", "SIG_RANDOM_CONTROL"]
EXPECTED_N_SIGNALS = len(SIGNAL_NAMES) + len(CONTROL_NAMES)


# ==================================================================================================
# Correlation + selection-rate measurement (mirrors forensic CHECK-1 methodology exactly).
# ==================================================================================================
def pearson(xs, ys):
    """Pearson corr; returns (corr, degenerate) where degenerate=True if either series has zero variance."""
    x = np.asarray(xs, dtype=np.float64)
    y = np.asarray(ys, dtype=np.float64)
    if len(x) < 2 or float(np.std(x)) < 1e-12 or float(np.std(y)) < 1e-12:
        return 0.0, True
    c = float(np.corrcoef(x, y)[0, 1])
    if not np.isfinite(c):
        return 0.0, True
    return c, False


def measure_signal(name, score_fn, cands, labels, groups_multi_rival):
    """cands/labels aligned by index. score_fn(c) -> float or None. Returns the full metrics dict."""
    scored_all = []
    labels_all = []
    scored_content = []
    labels_content = []
    n_none = 0
    for c, lab in zip(cands, labels):
        s = score_fn(c)
        if s is None:
            n_none += 1
            continue
        scored_all.append(s)
        labels_all.append(lab)
        scored_content.append(s)
        labels_content.append(lab)
    coverage = round(1.0 - n_none / len(cands), 4) if cands else 0.0
    corr_content, degen_content = pearson(scored_content, labels_content) if scored_content else (0.0, True)

    # selection-rate vs chance over multi-rival groups with gold present among rivals
    n_hit = 0
    n_included = 0
    n_dropped_no_signal = 0
    chance_terms = []
    for key, group in groups_multi_rival.items():
        gold_present = any(labels[i] for i in group)
        if not gold_present:
            continue
        scores = [(i, score_fn(cands[i])) for i in group]
        if all(s is None for _, s in scores):
            n_dropped_no_signal += 1
            continue
        n_included += 1
        # argmax; None treated as -inf; ties broken by first-in-list-order (stable sort)
        best_i, best_s = None, None
        for i, s in scores:
            sv = s if s is not None else float("-inf")
            if best_s is None or sv > best_s:
                best_s, best_i = sv, i
        if labels[best_i] == 1:
            n_hit += 1
        chance_terms.append(1.0 / len(group))
    selection_rate = round(n_hit / n_included, 4) if n_included else 0.0
    chance_rate = round(float(np.mean(chance_terms)), 4) if chance_terms else 0.0
    low_coverage_caveat = coverage < 0.30

    return {
        "coverage": coverage, "n_none_scored": n_none, "n_scored": len(scored_all),
        "corr_all": round(float(pearson(scored_all, labels_all)[0]), 4) if scored_all else 0.0,
        "corr_content_subset": round(corr_content, 4), "corr_content_degenerate": degen_content,
        "n_multi_rival_groups_with_gold": n_included + n_dropped_no_signal,
        "n_groups_no_signal_dropped": n_dropped_no_signal,
        "selection_rate_vs_chance": selection_rate, "chance_rate": chance_rate,
        "selection_margin": round(selection_rate - chance_rate, 4),
        "low_coverage_caveat": low_coverage_caveat,
    }


# ==================================================================================================
# Main run.
# ==================================================================================================
def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def run_mode(mode):
    t0 = time.perf_counter()
    gold_slice = GOLD_SLICE_SMOKE if mode == "smoke" else GOLD_SLICE_FULL
    out_dir = _out_dir(mode)

    order, sent_text, reader_svo = L.load_slice_and_reader(gold_slice)
    gold, gold_meta = L.load_gold(gold_slice)
    eval_data = {sid: {"sent": sent_text[sid], "svo": [list(t) for t in reader_svo[sid]]} for sid in order}
    print(f"[{ANCHOR_NAME}:{mode}] eval sents={len(order)}", flush=True)

    cands = CPCL.build_candidates(eval_data, order)
    labels = []
    for c in cands:
        rec = gold.get(c["sid"], {"pos": []})
        m = L.match_pos(c["v"], c["p"], rec["pos"])
        labels.append(1 if m is not None else 0)
    n_pos = sum(labels)
    print(f"[{ANCHOR_NAME}:{mode}] n_cands={len(cands)} n_gold_correct={n_pos}", flush=True)

    inst_groups = defaultdict(list)
    for i, c in enumerate(cands):
        inst_groups[(c["sid"], c["v"])].append(i)
    groups_multi_rival = {k: v for k, v in inst_groups.items() if len(v) >= 2}

    rng = np.random.default_rng(RANDOM_CONTROL_SEED)
    random_scores = {i: float(rng.standard_normal()) for i in range(len(cands))}

    results = {}
    results["SIG_PROTO_PATIENT_ONTOLOGY"] = measure_signal(
        "SIG_PROTO_PATIENT_ONTOLOGY", lambda c: sig_proto_patient_ontology(c["p"], c["v"]),
        cands, labels, groups_multi_rival)
    results["SIG_PLACE_GAZETTEER_EXCLUSION"] = measure_signal(
        "SIG_PLACE_GAZETTEER_EXCLUSION", lambda c: sig_place_gazetteer_exclusion(c["p"], c["v"]),
        cands, labels, groups_multi_rival)
    results["SIG_COS_VERB_GATED_ONTOLOGY"] = measure_signal(
        "SIG_COS_VERB_GATED_ONTOLOGY", lambda c: sig_cos_verb_gated_ontology(c["p"], c["v"]),
        cands, labels, groups_multi_rival)
    results["SIG_VERBNET_COS_GATED_ONTOLOGY"] = measure_signal(
        "SIG_VERBNET_COS_GATED_ONTOLOGY", lambda c: sig_verbnet_cos_gated_ontology(c["p"], c["v"]),
        cands, labels, groups_multi_rival)

    # ---- Candidate B/C: text-internal alternation scan over the SAME held-out mining corpus (third
    # reader excluded, matching CPCL-v2's own mining/eval split). No lexicon; VET non-vacuousness first. ----
    mining_files = S.MINING_FILES_SMOKE if mode == "smoke" else S.MINING_FILES_FULL
    v_scan = set(c["v"] for c in cands)
    alt_map, n_intrans_hits, n_passive_hits = scan_alternation_evidence(mining_files, v_scan)
    alternation_nonvacuous = bool((n_intrans_hits + n_passive_hits) > 0 and len(alt_map) > 0)
    print(f"[{ANCHOR_NAME}:{mode}] alternation scan: n_verbs_scanned={len(v_scan)} "
          f"n_verbs_with_evidence={len(alt_map)} n_intrans_hits={n_intrans_hits} "
          f"n_passive_hits={n_passive_hits} nonvacuous={alternation_nonvacuous}", flush=True)

    results["SIG_ALTERNATION_TEXT_INTERNAL"] = measure_signal(
        "SIG_ALTERNATION_TEXT_INTERNAL", lambda c: sig_alternation_text_internal(c["p"], c["v"], alt_map),
        cands, labels, groups_multi_rival)
    results["SIG_ALTERNATION_TEXT_INTERNAL"]["alternation_scan_nonvacuous"] = alternation_nonvacuous
    results["SIG_ALTERNATION_ANIMACY_GATED"] = measure_signal(
        "SIG_ALTERNATION_ANIMACY_GATED", lambda c: sig_alternation_animacy_gated(c["p"], c["v"], alt_map),
        cands, labels, groups_multi_rival)
    results["SIG_ALTERNATION_ANIMACY_GATED"]["alternation_scan_nonvacuous"] = alternation_nonvacuous

    # SIG_ORACLE_LABEL / SIG_RANDOM_CONTROL need per-candidate INDEX (not just the c dict), so they are
    # measured via measure_indexed below rather than measure_signal (which scores off c alone).
    def measure_indexed(score_by_index):
        scored_content, labels_content = [], []
        for i, lab in enumerate(labels):
            s = score_by_index(i)
            if s is None:
                continue
            scored_content.append(s)
            labels_content.append(lab)
        corr, degen = pearson(scored_content, labels_content)
        n_hit = n_included = n_dropped = 0
        chance_terms = []
        for key, group in groups_multi_rival.items():
            gold_present = any(labels[i] for i in group)
            if not gold_present:
                continue
            scores = [(i, score_by_index(i)) for i in group]
            if all(s is None for _, s in scores):
                n_dropped += 1
                continue
            n_included += 1
            best_i, best_s = None, None
            for i, s in scores:
                sv = s if s is not None else float("-inf")
                if best_s is None or sv > best_s:
                    best_s, best_i = sv, i
            if labels[best_i] == 1:
                n_hit += 1
            chance_terms.append(1.0 / len(group))
        sel = round(n_hit / n_included, 4) if n_included else 0.0
        chance = round(float(np.mean(chance_terms)), 4) if chance_terms else 0.0
        return {
            "coverage": 1.0, "n_none_scored": 0, "n_scored": len(cands),
            "corr_all": round(corr, 4), "corr_content_subset": round(corr, 4),
            "corr_content_degenerate": degen,
            "n_multi_rival_groups_with_gold": n_included + n_dropped,
            "n_groups_no_signal_dropped": n_dropped,
            "selection_rate_vs_chance": sel, "chance_rate": chance,
            "selection_margin": round(sel - chance, 4), "low_coverage_caveat": False,
        }

    results["SIG_ORACLE_LABEL"] = measure_indexed(lambda i: float(labels[i]))
    results["SIG_RANDOM_CONTROL"] = measure_indexed(lambda i: random_scores[i])

    # ---- SANITY GATE ----
    oracle_corr = results["SIG_ORACLE_LABEL"]["corr_content_subset"]
    random_corr = abs(results["SIG_RANDOM_CONTROL"]["corr_content_subset"])
    sanity_ok = (oracle_corr >= SANITY_ORACLE_CORR_MIN) and (random_corr < SANITY_RANDOM_CORR_MAX)

    # ---- DESIGN-GATE VERDICT over the 6 real candidates ----
    per_signal_verdict = {}
    best_corr = -1.0
    best_name = None
    for name in SIGNAL_NAMES:
        r = results[name]
        corr = r["corr_content_subset"]
        margin = r["selection_margin"]
        if r.get("alternation_scan_nonvacuous") is False:
            per_signal_verdict[name] = "HARD_FAIL_VACUOUS_SCAN_UNINTERPRETABLE"
            continue
        clears_hp = (corr >= HP_CORR) and (margin >= HP_SEL_MARGIN)
        clears_mb = (corr >= MB_CORR) and (margin >= MB_SEL_MARGIN)
        per_signal_verdict[name] = "HARD_PASS" if clears_hp else ("MIDDLE" if clears_mb else "HARD_FAIL")
        if corr > best_corr:
            best_corr = corr
            best_name = name

    if not sanity_ok:
        gate_verdict = "HARD_FAIL_METHODOLOGY_BROKEN"
    elif any(v == "HARD_PASS" for v in per_signal_verdict.values()):
        gate_verdict = "HARD_PASS_DESIGN_GATE"
    elif any(v == "MIDDLE" for v in per_signal_verdict.values()):
        gate_verdict = "MIDDLE_BAND_DESIGN_GATE"
    else:
        gate_verdict = "HARD_FAIL_DESIGN_GATE"

    elapsed = time.perf_counter() - t0
    msg = (f"gate_verdict={gate_verdict} | sanity_ok={sanity_ok} "
           f"(oracle_corr={oracle_corr:.4f} random_corr={random_corr:.4f}) | "
           f"per_signal={ {k: (per_signal_verdict[k], results[k]['corr_content_subset'],
                                results[k]['selection_margin']) for k in SIGNAL_NAMES} } | "
           f"best={best_name}({best_corr:.4f}) | n_cands={len(cands)} n_gold_correct={n_pos} "
           f"n_multi_rival_groups={len(groups_multi_rival)}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": gate_verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "gold_slice": gold_slice, "n_cands": len(cands), "n_gold_correct": n_pos,
        "n_multi_rival_groups": len(groups_multi_rival),
        "sanity_gate": {"ok": sanity_ok, "oracle_corr": oracle_corr, "random_corr": random_corr,
                        "oracle_floor": SANITY_ORACLE_CORR_MIN, "random_ceiling": SANITY_RANDOM_CORR_MAX},
        "bands": {"HP_CORR": HP_CORR, "HP_SEL_MARGIN": HP_SEL_MARGIN, "MB_CORR": MB_CORR,
                  "MB_SEL_MARGIN": MB_SEL_MARGIN},
        "per_signal_verdict": per_signal_verdict,
        "signals": {k: results[k] for k in SIGNAL_NAMES},
        "controls": {k: results[k] for k in CONTROL_NAMES},
        "best_signal": best_name, "best_corr": best_corr,
        "verbnet_available": _VERBNET_AVAILABLE,
        "alternation_scan": {"n_verbs_scanned": len(v_scan), "n_verbs_with_evidence": len(alt_map),
                             "n_intrans_hits": n_intrans_hits, "n_passive_hits": n_passive_hits,
                             "nonvacuous": alternation_nonvacuous, "mining_files": mining_files},
        "explicitly_not_retried": [
            "plain ANIMACY standalone (already failed; ontology score's animate bucket is a component, not"
            " a standalone re-test)",
            "distributional THEMATIC-FIT / GloVe verb-centroid selectional cosine (already failed)",
            "ENTITY-RECURRENCE (already failed; this cell's direct parent forensic)",
            "COREFERENCE (already failed)",
            "SCENE-COHERENCE (already failed)",
            "raw cosine/distributional-similarity (already failed)",
            "object-typicality / selectional-coherence (closed: af19aa9d graded-fit HARD_FAIL;"
            " a5f2c3d0 SCV null-trainer even at gold-perfect oracle=0.000)",
        ],
        "cardinality_ok": len(results) == EXPECTED_N_SIGNALS, "expected_n_signals": EXPECTED_N_SIGNALS,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "categorical-lookup correlation-gate metric; no quantitative noise-floor formula applies",
        "gold_meta_independence": gold_meta,
        "claim_ceiling": ("DESIGN-GATE measurement only. Not a loop; not a claim these are the only possible"
                          " grounded/weak-sup signals. HARD_FAIL here narrows curated-lookup-ontology"
                          " specifically, distinct from the 6 already-failed self-supervised text signals."),
        "REQUIRED_FIELDS": ["verdict", "sanity_gate", "per_signal_verdict", "signals", "controls",
                            "best_signal", "cardinality_ok", "alternation_scan", "verbnet_available"],
    }
    write_metrics(out_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(out_dir, 'metrics.json')}", flush=True)
    return payload


# ==================================================================================================
# Self-test (real code path: constructs real LCCP/gold objects at the actual tiny smoke slice L04 only
# would still hit real files; use an embedded toy in-memory example to keep self-test instant + isolated,
# then ALSO call the real L.match_pos + real lexicons on that toy example -- real functions, tiny scale).
# ==================================================================================================
def self_test():
    # --- lexicon sanity: known category members score as expected ---
    assert sig_proto_patient_ontology("castle", "build") == 1.0, "castle must be ARTIFACT (+1.0)"
    assert sig_proto_patient_ontology("dog", "call") == 0.8, "dog must be ANIMATE (+0.8)"
    assert sig_proto_patient_ontology("head", "rub") == 0.6, "head must be BODY_PART (+0.6)"
    assert sig_proto_patient_ontology("grief", "feel") == -0.3, "grief must be ABSTRACT (-0.3)"
    assert sig_proto_patient_ontology("garden", "work") == -1.0, "garden must be LOCATION (-1.0)"
    assert sig_proto_patient_ontology("he", "see") is None, "pronoun must be neutral (None)"
    assert sig_proto_patient_ontology("zzz_unknown_tok", "see") is None, "OOV must be None"
    assert sig_place_gazetteer_exclusion("garden", "work") == -1.0, "garden must be excluded (-1.0)"
    assert sig_place_gazetteer_exclusion("castle", "build") == 0.0, "castle (non-place, in-lexicon) -> 0.0"
    assert sig_cos_verb_gated_ontology("castle", "build") == 1.0, "build is COS-class -> gate passes"
    assert sig_cos_verb_gated_ontology("castle", "see") == 0.0, "see is NOT COS-class -> gated to 0.0"

    # --- correlation formula sanity: perfect signal -> corr=1.0; constant signal -> degenerate ---
    c, degen = pearson([1.0, 0.0, 1.0, 0.0], [1, 0, 1, 0])
    assert abs(c - 1.0) < 1e-9 and not degen, f"perfect-match corr should be 1.0, got {c}"
    c2, degen2 = pearson([1.0, 1.0, 1.0], [1, 0, 1])
    assert degen2, "constant-signal series must be flagged degenerate"

    # --- REAL code path: measure_signal / measure_indexed exercised on a tiny embedded toy instance set,
    #     using the REAL L.match_pos (not a stub) against a fabricated gold pos-list. ---
    toy_gold_pos = [{"v": "build", "patient": "castle", "agent": "he", "refs": {"he"}}]
    cands = [
        {"sid": "T0", "v": "build", "p": "castle"},   # correct patient (label=1)
        {"sid": "T0", "v": "build", "p": "garden"},    # over-extracted locative (label=0)
        {"sid": "T0", "v": "build", "p": "hut"},       # another rival artifact, not gold (label=0)
    ]
    labels = [1 if L.match_pos(c["v"], c["p"], toy_gold_pos) is not None else 0 for c in cands]
    assert labels == [1, 0, 0], f"real match_pos toy labels wrong: {labels}"
    groups = defaultdict(list)
    for i, c in enumerate(cands):
        groups[(c["sid"], c["v"])].append(i)
    groups_multi = {k: v for k, v in groups.items() if len(v) >= 2}
    r = measure_signal("toy", lambda c: sig_proto_patient_ontology(c["p"], c["v"]), cands, labels, groups_multi)
    assert r["n_scored"] == 3 and r["n_none_scored"] == 0, f"toy coverage wrong: {r}"
    # castle(+1.0)=argmax among [castle,garden,hut]=[1.0,-1.0,1.0] -- TIE with hut; first-in-list wins ->
    # castle (index 0) selected first since it's earlier in the list and strictly > follows only on '>'.
    assert r["selection_rate_vs_chance"] == 1.0, f"toy selection should hit gold (castle ties-wins first): {r}"
    assert r["chance_rate"] == round(1.0 / 3.0, 4), f"toy chance should be 1/3: {r}"

    # oracle control sanity on the toy set
    def oracle_by_index(i):
        return float(labels[i])
    scored_content = [oracle_by_index(i) for i in range(len(cands))]
    oc, odeg = pearson(scored_content, labels)
    assert abs(oc - 1.0) < 1e-9, f"toy oracle control corr must be 1.0, got {oc}"

    # --- SIG_VERBNET_COS_GATED_ONTOLOGY: real NLTK VerbNet lookup (degrades gracefully if unavailable) ---
    if _VERBNET_AVAILABLE:
        assert verbnet_is_cos_class("build") is True, "build has VerbNet class build-26.1 (group 26) -> COS"
        assert verbnet_is_cos_class("open") is True, "open has VerbNet class other_cos-45.4 (group 45) -> COS"
        assert verbnet_is_cos_class("see") is False, "see's VerbNet classes (29,30) are not COS groups"
        assert sig_verbnet_cos_gated_ontology("castle", "build") == 1.0, "build+castle: VerbNet-gated ontology"
        assert sig_verbnet_cos_gated_ontology("castle", "see") == 0.0, "see is not VerbNet-COS -> gated to 0.0"
    else:
        print(f"[{ANCHOR_NAME}] WARN: NLTK VerbNet corpus unavailable in this environment -- "
              f"SIG_VERBNET_COS_GATED_ONTOLOGY will degrade to all-0.0 (gate never fires); "
              f"logged via verbnet_available=False in metrics, not silently swallowed.", flush=True)

    # --- Candidate B/C: text-internal alternation scan (real function, tiny embedded toy corpus) ---
    toy_dir = os.path.join(REPO_ROOT, "data", f"_{ANCHOR_NAME}_selftest_toy")
    os.makedirs(toy_dir, exist_ok=True)
    toy_file = os.path.join(toy_dir, "toy_mining.txt")
    with open(toy_file, "w", encoding="utf-8") as f:
        f.write("The ice melted. He melted the ice. The castle was built. "
                "He built the castle. He ran home. The boy opened the door.")
    toy_rel = os.path.relpath(toy_file, REPO_ROOT).replace("\\", "/")
    alt_map, n_intrans, n_passive = scan_alternation_evidence([toy_rel], {"melt", "build", "run"})
    assert "ice" in alt_map.get("melt", set()), f"intransitive 'the ice melted' must record ice: {alt_map}"
    assert "castle" in alt_map.get("build", set()), f"passive 'castle was built' must record castle: {alt_map}"
    assert "he" not in alt_map.get("run", set()), "pronoun subject (he ran) must NOT be recorded (needs coref)"
    assert n_intrans >= 1 and n_passive >= 1, f"toy scan must find both intrans + passive hits: {n_intrans},{n_passive}"
    assert sig_alternation_text_internal("ice", "melt", alt_map) == 1.0, "ice must score 1.0 (attested alternation)"
    assert sig_alternation_text_internal("hut", "melt", alt_map) == 0.0, "hut has no attested alternation -> 0.0"
    assert sig_alternation_animacy_gated("dog", "melt", {"melt": {"dog"}}) == 0.0, "animate gated to 0.0"
    assert sig_alternation_animacy_gated("hut", "melt", {"melt": {"hut"}}) == 1.0, "inanimate passes through"
    os.remove(toy_file)

    print(f"[{ANCHOR_NAME}] self-test PASS | lexicon buckets ok; pearson formula ok "
          f"(perfect=1.0, constant flagged degenerate); real L.match_pos toy labels={labels}; "
          f"toy selection_rate={r['selection_rate_vs_chance']} chance={r['chance_rate']}; "
          f"oracle control corr={oc:.3f}; verbnet_available={_VERBNET_AVAILABLE}; "
          f"toy alternation scan intrans={n_intrans} passive={n_passive}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only; accept-and-ignore for runner parity
    args, _ = ap.parse_known_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
                "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat()}
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
