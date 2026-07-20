"""SCENE-COHERENCE VERIFIER (SCV): a CONTRASTIVE, glass-box, zero-pixel type-coherence check over
rival candidate parses of the same sentence, used BOTH as a parse-SELECTOR and as a SELF-SUPERVISED
TRAINING SIGNAL for the reader's structural cue-weights -- with NO gold PARSES.

WHAT THIS IS (honest ceiling -- read before interpreting any number):
  The "does the scene make sense" coherence judgment is computed by LOOKING UP hand-curated WordNet
  noun-supersenses + VerbNet selectional-restriction structure. That is a LOT of human WORLD-EXPERIENCE,
  GIVEN to the substrate, not learned by it. The correct claim ceiling is therefore:
    "the reader learns to PARSE from a HAND-CURATED type-coherence oracle (WordNet/VerbNet), using NO
     gold PARSE labels -- self-supervised w.r.t. parse-labels, but SUPERVISED by an external curated
     world-knowledge resource. The world-knowledge is LOOKED UP, not learned by the substrate."
  This run tests the MECHANISM (contrastive coherence as selector + training signal). The fully-honest
  "substrate LEARNS the type-knowledge from its OWN reading/experience" version is a HARDER, SEPARATE
  future test (and likely corpus-sparse, per the animacy lesson, atom 29357). Do NOT frame any result
  here as "the substrate evaluates scene realism from its own experience."

THE GENUINE NOVELTY (independent of where the knowledge came from): CONTRAST. Prior "meaning" signals
  failed to TRAIN because they were not contrastive -- the cosine was a single blended score (no
  candidate-vs-candidate comparison); the animacy filter was a per-candidate PRE-filter (removed a
  candidate before scoring -> zero training signal, fixed_ON=0, atom 29357). The SCV scores BOTH rival
  parses of one sentence and uses the GAP (exactly-one-coherent cases) as a margin/perceptron update.
  Contrast-structure, not discreteness, is the operative variable for TRAINABILITY.

FOUR FAIRNESS GUARDS (USER, load-bearing -- enforced + reported so no VET or director is fooled):
  (G-FAIR-1) NO CIRCULAR EVAL: the independent gold (data/gold_mcguffey_lccp_argstruct_v1.json) is
    human who-did-what annotation of pos/nopat argument structure, annotated by READING RAW TEXT,
    INDEPENDENT of WordNet/VerbNet typing (verified: _meta.independence). The residual triage (Pred-1)
    is computed vs GOLD (within-frame FP), NOT vs supersense. So the SCV is NOT predicting its own
    oracle. metrics.gold_type_oracle_independent=True with rationale.
  (G-FAIR-2) HONEST LABELING: framed as above everywhere; metrics.claim_ceiling states it.
  (G-FAIR-3) IS IT JUST DISTILLATION? explicit ablation: SCV_DIRECT (apply the WordNet/VerbNet type
    check DIRECTLY at eval, no learned weights) vs SCV_TRAINED (learned cue-weights only, no direct
    lookup at eval) vs FROZEN. If the direct lookup already resolves the residual, the "learned training
    signal" adds little -> reported plainly (distillation_attribution).
  (G-FAIR-4) ORACLE COVERAGE/NOISE on THIS corpus: report WordNet supersense coverage + OOV rate on the
    corpus's actual filler nouns, VerbNet SELRESTR usable-rate on the corpus's verbs, and the count of
    residual cases the oracle cannot type. Mechura granularity-mismatch is real and measured, not assumed
    away (empirically: VerbNet build-26.1 has EMPTY SELRESTRS; WordNet stream/river/hill -> noun.object
    NOT noun.location -> the literal build/huts-vs-build/stream location-vs-artifact split does NOT hold
    under WordNet supersense; reported honestly as a coverage finding, not hidden).

THE MECHANISM (glass-box, CPU, NO gold parses, NO external LLM at runtime):
  Rival candidates = the LCCP reader's raw over-extracted (v,a,p) tuples grouped per verb-instance
    (35% of verb-instances have >=2 rival candidate patients -- measured). NO new candidate-gen.
  Coherence bit (per candidate filler f proposed as the direct object of verb v):
    junk filler (funcword/prep/non-alpha) -> 0 ; pronoun -> 1 (valid object) ;
    noun with WordNet supersense ss: ss in NONOBJECT_SS (location/abstract/communication/act/event/...) ->
    0 (mismatch: not a plausible physical thing to be acted on) ; concrete ss -> 1 ; OOV noun -> 1
    (benefit of doubt, tracked as coverage gap). The verb-side subcat gate via VerbNet is INTENTIONALLY
    NOT baked into the bit (VerbNet class-OR-ing is too permissive -- marks come/go/sit/wonder as
    object-taking; reported as a coverage finding), so the SELECTOR DEFERS subcat to the LCCP and only
    overrides WITHIN-FRAME type choices -- it never force-commits an object onto an LCCP-suppressed verb.
  CONTRAST: per verb-instance with >=2 rivals, sum(bits). exactly-one-coherent (sum==1) = the informative
    gap; both/neither = abstain (no override, no training pair).

  Prediction 1 (SELECTOR): layered on LCCP arm C (the reproduced ~0.557 reader). On multi-candidate
    verb-instances where the LCCP KEPT a patient AND exactly-one-coherent, override to the coherent
    candidate. Break-budget (broken vs fixed) vs INDEPENDENT gold.
  Prediction 2 (TRAINER -- the central, novel claim): margin/perceptron update of the reader's structural
    cue-weights from exactly-one-coherent CONTRAST pairs mined from RAW text (no gold), evaluated on a
    HELD-OUT gold slice never in the mining corpus, vs a FROZEN-weight control (same LCCP structural
    teacher, WITHOUT the coherence pass -- ONE variable). Corpus-size ablation (full ~74k external words
    vs gold-slice-raw only) to separate sparsity from mechanism-null.
  Prediction 3 (SCOPE): is the exactly-one-coherent contrast bucket non-trivial? plus the specific
    artifact-vs-location sub-bucket size (expected small under WordNet -- honest).

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  REAL baseline = LCCP arm C precision vs INDEPENDENT gold (reproduced live, ~0.557 ballpark).
  ONE VARIABLE per prediction. CAN-FAIL BOTH WAYS (bands below). Held-out (third reader) NEVER in the
  mining corpus. Contrast fires at smoke (>0 exactly-one-coherent instances). Determinism enforced.

VERDICT BANDS (pre-registered BEFORE running; do NOT redefine mid-run):
  P1 (selector): HARD_PASS = residual >= 5 changed AND fixed >= broken AND net precision delta >= 0.
                 HARD_FAIL = broken > fixed OR exactly-one-coherent multi-cand bucket < 3.
  P2 (trainer):  HARD_PASS = mean(precision(SCV_TRAINED) - precision(FROZEN)) >= +0.02 over seeds AND
                             min over seeds > 0 (consistent sign).
                 HARD_FAIL = mean delta <= 0 (null/negative). Then ablation decides sparsity vs null.
                 MIDDLE = 0 < mean delta < 0.02 or inconsistent sign.
  P3 (scope):    HARD_PASS = exactly-one-coherent multi-cand bucket >= 10.
                 HARD_FAIL = bucket < 5.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- the reader (~105 ms/sent) is the
  cost; run ONCE on the mining corpus + gold slice, cache to JSON; the multi-seed perceptron is cheap.
  Foreground local-to-completion (NO queue; NO push; NO remote-persist). Storage: no_storage
  (extraction-precision measurement). progress_logging: print_flush_true. Determinism: OMP/MKL/OPENBLAS=1,
  fixed int seeds, hashlib digests, sorted(set); numpy default_rng seeded.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import re
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "scene_coherence_verifier_contrastive_scv_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402

from nltk.corpus import wordnet as wn  # noqa: E402
from nltk.corpus import verbnet as vn  # noqa: E402

# Mining corpus files (RAW, unlabeled). The third reader is the GOLD source -> EXCLUDED from mining so
# the held-out eval text is never seen by the self-supervised update.
MINING_FILES_FULL = [
    "data/corpora/graded_readers_grade1/cleaned/mcguffey_primer.clean.txt",
    "data/corpora/graded_readers_grade1/cleaned/mcguffey_first_reader.clean.txt",
    "data/corpora/graded_readers_graded/cleaned/mcguffey_second_reader.clean.txt",
    "data/corpora/graded_readers_graded/cleaned/mcguffey_fourth_reader.clean.txt",
]
MINING_FILES_SMOKE = [
    "data/corpora/graded_readers_grade1/cleaned/mcguffey_primer.clean.txt",
    "data/corpora/graded_readers_grade1/cleaned/mcguffey_first_reader.clean.txt",
]
EXCLUDED_FROM_MINING = "data/corpora/graded_readers_graded/cleaned/mcguffey_third_reader.clean.txt (GOLD source)"

# ----------------------------------------------------------------------------------------------
# Coherence type sets (WordNet lexicographer files = noun supersenses). Glass-box, documented.
# CONCRETE = plausible physical thing that can be a direct object. NONOBJECT = not a plausible
# direct-object type for a physical/creation/perception verb (location / abstract / communication /...).
# ----------------------------------------------------------------------------------------------
CONCRETE_SS = {"noun.artifact", "noun.object", "noun.substance", "noun.food", "noun.plant",
               "noun.animal", "noun.body", "noun.person", "noun.group", "noun.possession", "noun.shape"}
NONOBJECT_SS = {"noun.location", "noun.time", "noun.state", "noun.attribute", "noun.cognition",
                "noun.communication", "noun.feeling", "noun.act", "noun.event", "noun.relation",
                "noun.motive", "noun.phenomenon", "noun.process", "noun.quantity"}

_SS_CACHE = {}


def supersense(noun):
    """First-synset WordNet noun supersense (lexname), cached. None if OOV."""
    if noun in _SS_CACHE:
        return _SS_CACHE[noun]
    ss = None
    try:
        syns = wn.synsets(noun, pos="n")
        if syns:
            ss = syns[0].lexname()
    except Exception:
        ss = None
    _SS_CACHE[noun] = ss
    return ss


_VN_SELRESTR_CACHE = {}


def verbnet_object_selrestr_usable(lemma):
    """Does VerbNet supply a NON-EMPTY selectional restriction on an object role for this verb? (coverage
    probe for G-FAIR-4). Returns bool. Empirically ~0 for this corpus's verbs (build-26.1 SELRESTRS empty)."""
    if lemma in _VN_SELRESTR_CACHE:
        return _VN_SELRESTR_CACHE[lemma]
    usable = False
    try:
        for cid in vn.classids(lemma):
            vc = vn.vnclass(cid)
            for tr in vc.findall("THEMROLES/THEMROLE"):
                if tr.get("type") in ("Theme", "Patient", "Product", "Topic", "Stimulus"):
                    if tr.findall("SELRESTRS/SELRESTR"):
                        usable = True
                        break
            if usable:
                break
    except Exception:
        usable = False
    _VN_SELRESTR_CACHE[lemma] = usable
    return usable


def coherence_bit(v, p):
    """Discrete scene-coherence bit for filler p as the direct object of verb v. Returns (bit, reason).
    Type-driven (WordNet supersense) + junk/pronoun structural guards. Verb-side subcat NOT baked in
    (VerbNet class-OR too permissive; deferred to LCCP)."""
    pl = p.lower()
    if pl in L.FUNCWORD or pl in L.PREPS or len(pl) < 2 or not pl.replace("'", "").isalpha():
        return 0, "junk_filler"
    if pl in L.PRONOUN:
        return 1, "pronoun_object"
    ss = supersense(pl)
    if ss is None:
        return 1, "oov_noun_benefit_of_doubt"
    if ss in NONOBJECT_SS:
        return 0, "type_mismatch:" + ss
    return 1, "concrete:" + ss


# ----------------------------------------------------------------------------------------------
# Corpus loaders.
# ----------------------------------------------------------------------------------------------
def _read_text_file(rel):
    with open(os.path.join(REPO_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def run_reader_on_files(files, cache_path, max_sents=None):
    """Run the REAL hand-rule reader over raw text files -> {sid: {"sent":..., "svo":[[v,a,p],...]}}.
    Cached to JSON (deterministic) keyed by files+max_sents so multi-seed iteration is cheap."""
    key = hashlib.sha256(("|".join(files) + f"|{max_sents}").encode()).hexdigest()[:16]
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            obj = json.load(f)
        if obj.get("_key") == key:
            return obj["data"]
    from experiments import exp_read_nested_clause_relative_third_reader_v1 as NEST
    from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2
    clf = V2._fit_clf()
    passages, order = {}, []
    for fi, rel in enumerate(files):
        sents = L.split_sents(_read_text_file(rel))
        for j, s in enumerate(sents):
            sid = f"M{fi}_{j:05d}"
            passages[sid] = s
            order.append(sid)
            if max_sents is not None and len(order) >= max_sents:
                break
        if max_sents is not None and len(order) >= max_sents:
            break
    print(f"[{ANCHOR_NAME}] reading {len(order)} mining sentences from {len(files)} files ...", flush=True)
    t0 = time.time()
    # chunk to emit progress
    data = {}
    CH = 300
    for start in range(0, len(order), CH):
        chunk = {sid: passages[sid] for sid in order[start:start + CH]}
        store = NEST.read_corpus(clf, chunk, nest=True)["store"]
        for sid in chunk:
            tups = [[str(r[1]).lower(), str(r[2]).lower(), str(r[3]).lower()]
                    for r in store.get(sid, []) if r[0] == "svo" and r[1] != "kind"]
            data[sid] = {"sent": chunk[sid], "svo": tups}
        print(f"[{ANCHOR_NAME}]   mined {min(start + CH, len(order))}/{len(order)} sents "
              f"({time.time() - t0:.0f}s)", flush=True)
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    tmp = cache_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"_key": key, "data": data}, f)
    os.replace(tmp, cache_path)
    return data


# Extended feature vector = LCCP's 6 STRUCTURAL cues + a 7th TYPE cue (the coherence bit). The type cue
# is what gives the self-supervised coherence contrast a CHANNEL to teach the reader something the 6
# structural features cannot express (location-vs-artifact when both are post-verbal non-prep fillers).
# Without it, P2 would be rigged to fail (no way for type-knowledge to enter the weights). FROZEN and
# SCV both carry f_type; ONE variable = whether the coherence contrast pass runs (see train_weights).
FEAT_NAMES_EXT = L.FEAT_NAMES + ["f_type"]
FEAT_DIM = 7


def build_candidates(reader_data):
    """reader_data: {sid:{sent,svo}} -> list of cand dicts (sid,v,a,p,tup,feat[7]) grouped-ready.
    feat = [bias, f_adj, f_postv, f_prep, f_func, f_clause, f_type] (f_type = coherence bit)."""
    cands = []
    for sid, rec in reader_data.items():
        toks = L.tokenize(rec["sent"])
        for tup in rec["svo"]:
            v_surf, a, p = tup
            feat6, _ = L.candidate_features(toks, v_surf, p)
            v_lemma = L.lemma_verb(v_surf)
            f_type = float(coherence_bit(v_lemma, p)[0])
            feat = np.concatenate([feat6, [f_type]])
            cands.append({"sid": sid, "v": v_lemma, "a": a, "p": p,
                          "tup": (v_surf, a, p), "feat": feat})
    return cands


def group_by_instance(cands):
    g = defaultdict(list)
    for c in cands:
        g[(c["sid"], c["v"])].append(c)
    return g


# ----------------------------------------------------------------------------------------------
# Contrast + coherence pair mining.
# ----------------------------------------------------------------------------------------------
def contrast_stats(inst_groups):
    """Per multi-candidate verb-instance: distribution of sum(coherence bits). Returns stats + pairs."""
    n_multi = 0
    n_one = n_both = n_neither = 0
    coh_pairs = []  # (feat_pos, feat_neg)
    reasons = defaultdict(int)
    artifact_vs_location = 0
    for (sid, v), cs in inst_groups.items():
        if len(cs) < 2:
            continue
        n_multi += 1
        bits = []
        sss = []
        for c in cs:
            b, r = coherence_bit(v, c["p"])
            bits.append(b)
            reasons[r.split(":")[0]] += 1
            sss.append(supersense(c["p"].lower()))
        s = sum(bits)
        if "noun.artifact" in sss and "noun.location" in sss:
            artifact_vs_location += 1
        if s == 1:
            n_one += 1
            pos = cs[bits.index(1)]
            for k, c in enumerate(cs):
                if bits[k] == 0:
                    coh_pairs.append((pos["feat"].copy(), c["feat"].copy()))
        elif s == len(cs):
            n_both += 1
        elif s == 0:
            n_neither += 1
    return {"n_multi_candidate_instances": n_multi, "n_exactly_one_coherent": n_one,
            "n_all_coherent": n_both, "n_none_coherent": n_neither,
            "n_artifact_vs_location_pairs": artifact_vs_location,
            "n_coherence_pairs": len(coh_pairs), "bit_reason_counts": dict(reasons)}, coh_pairs


# ----------------------------------------------------------------------------------------------
# Weight training (LCCP structural teacher +/- coherence contrast pass). ONE variable = use_coherence.
# ----------------------------------------------------------------------------------------------
def train_weights(cands, sel_fn, coh_pairs, cfg, seed, use_coherence):
    rng = np.random.default_rng(seed)
    w = np.zeros(FEAT_DIM)
    train = []
    for c in cands:
        t = L.cand_target(c, sel_fn, cfg["sel_keep"], cfg["sel_drop"])
        if t is None:
            continue
        train.append((c["feat"].copy(), t))
    for _ in range(cfg["epochs"]):
        for k in rng.permutation(len(train)):
            x, t = train[k]
            pred = L.sigmoid(float(np.dot(w, x)))
            w = w + cfg["lr"] * (t - pred) * x
        if use_coherence and coh_pairs:
            for k in rng.permutation(len(coh_pairs)):
                fpos, fneg = coh_pairs[k]
                if float(np.dot(w, fpos)) - float(np.dot(w, fneg)) < cfg["coh_margin"]:
                    w = w + cfg["coh_lr"] * (fpos - fneg)
    return w, len(train)


def eval_kept(w, inst_groups, keep_thr, direct=False):
    """Apply weights (arm-B keep-best>=thr) OR direct coherence pick. Returns kept [(sid,tup)]."""
    kept = []
    for (sid, v), cs in inst_groups.items():
        if direct:
            bits = [coherence_bit(v, c["p"])[0] for c in cs]
            if len(cs) >= 2 and sum(bits) == 1:
                best = cs[bits.index(1)]
                kept.append((best["sid"], best["tup"]))
                continue
        best = max(cs, key=lambda c: L.score_cand(w, c["feat"]))
        if L.score_cand(w, best["feat"]) >= keep_thr:
            kept.append((best["sid"], best["tup"]))
    return kept


# ----------------------------------------------------------------------------------------------
# Config.
# ----------------------------------------------------------------------------------------------
def cfg_smoke():
    return dict(mode="smoke", gold_slice=["L04", "L05", "L07"], mining_files=MINING_FILES_SMOKE,
               mining_max_sents=500, sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=40, keep_thr=0.45,
               coh_lr=0.10, coh_margin=0.30, seeds=[7, 13, 19])


def cfg_full():
    return dict(mode="full", gold_slice=["L04", "L05", "L07", "L08", "L09", "L10", "L12"],
                mining_files=MINING_FILES_FULL, mining_max_sents=None, sel_keep=0.28, sel_drop=0.10,
                lr=0.20, epochs=60, keep_thr=0.45, coh_lr=0.10, coh_margin=0.30, seeds=[7, 13, 19])


# ----------------------------------------------------------------------------------------------
# Prediction 1: selector layered on LCCP arm C.
# ----------------------------------------------------------------------------------------------
def prediction1_selector(cfg):
    order, sent_text, reader_svo = L.load_slice_and_reader(cfg["gold_slice"])
    gold, _ = L.load_gold(cfg["gold_slice"])
    toks = set()
    for sid in order:
        for v, a, p in reader_svo[sid]:
            toks.update([p, L.lemma_verb(v)])
    for rec in gold.values():
        for g in rec["pos"]:
            toks.update([g["patient"], g["v"]])
    glove = L.load_glove_for(toks)
    lccp_cfg = dict(sel_keep=cfg["sel_keep"], sel_drop=cfg["sel_drop"], lr=cfg["lr"], epochs=cfg["epochs"],
                    keep_thr=cfg["keep_thr"], subcat_thr=0.42, heldout_frac=0.25, k_constructions=4,
                    kappa=1.5, seed=7)
    decisions, artifacts, subcat_dec, ho, sn, inst_groups, w = L.run_arms(
        order, reader_svo, sent_text, glove, lccp_cfg, 7)
    kept_C = decisions["C_lccp"]
    c_kept = {}
    for sid, tup in kept_C:
        c_kept[(sid, L.lemma_verb(tup[0]))] = tup

    kept_scv = []
    changes = []
    for (sid, v), cs in inst_groups.items():
        ckt = c_kept.get((sid, v))
        if ckt is None:
            continue  # LCCP suppressed -> SCV defers subcat, also suppresses
        if len(cs) >= 2:
            bits = [coherence_bit(v, c["p"])[0] for c in cs]
            if sum(bits) == 1:
                chosen = cs[bits.index(1)]["tup"]
                kept_scv.append((sid, chosen))
                if tuple(chosen) != tuple(ckt):
                    changes.append((sid, v, ckt, chosen))
                continue
        kept_scv.append((sid, ckt))

    base_m = L.score_arm(kept_C, gold)
    scv_m = L.score_arm(kept_scv, gold)
    fixed = broken = neutral = 0
    change_detail = []
    for (sid, v, ckt, chosen) in changes:
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        old_ok = L.match_pos(v, ckt[2], rec["pos"]) is not None
        new_ok = L.match_pos(v, chosen[2], rec["pos"]) is not None
        if new_ok and not old_ok:
            fixed += 1
        elif old_ok and not new_ok:
            broken += 1
        else:
            neutral += 1
        change_detail.append({"sid": sid, "v": v, "old": list(ckt), "new": list(chosen),
                              "old_correct": old_ok, "new_correct": new_ok})
    cstats, _ = contrast_stats(inst_groups)
    net_p = round(scv_m["precision"] - base_m["precision"], 4)
    n_changed = len(changes)
    if n_changed >= 5 and fixed >= broken and net_p >= 0.0:
        p1 = "HARD_PASS_P1_SELECTOR_HELPS"
    elif broken > fixed or cstats["n_exactly_one_coherent"] < 3:
        p1 = "HARD_FAIL_P1_SELECTOR_HURTS_OR_EMPTY"
    else:
        p1 = "MIDDLE_BAND_P1"
    return {"verdict_p1": p1, "baseline_lccp_C": base_m, "scv_selector": scv_m,
            "n_changed": n_changed, "fixed": fixed, "broken": broken, "neutral": neutral,
            "net_precision_delta": net_p, "contrast_stats": cstats,
            "change_detail": change_detail[:40],
            "baseline_precision_reproduced": base_m["precision"]}, inst_groups, glove


# ----------------------------------------------------------------------------------------------
# Prediction 2: self-supervised training signal (FROZEN vs SCV_TRAINED vs SCV_DIRECT) + ablation.
# ----------------------------------------------------------------------------------------------
def prediction2_trainer(cfg):
    # held-out EVAL = gold slice (third reader), NEVER in mining corpus.
    order, sent_text, reader_svo = L.load_slice_and_reader(cfg["gold_slice"])
    gold, _ = L.load_gold(cfg["gold_slice"])
    eval_data = {sid: {"sent": sent_text[sid], "svo": [list(t) for t in reader_svo[sid]]} for sid in order}
    eval_cands = build_candidates(eval_data)
    eval_groups = group_by_instance(eval_cands)

    out_dir = _out_dir(cfg["mode"])
    # FULL mining corpus (external, ~74k words excl third reader)
    mine_data = run_reader_on_files(cfg["mining_files"], os.path.join(out_dir, "_mining_cache.json"),
                                    max_sents=cfg["mining_max_sents"])
    mine_cands = build_candidates(mine_data)
    mine_groups = group_by_instance(mine_cands)
    cstats_full, coh_pairs_full = contrast_stats(mine_groups)

    # SMALL mining = gold-slice RAW sentences only (no gold labels used) -> sparsity control
    small_cands = eval_cands
    small_groups = eval_groups
    cstats_small, coh_pairs_small = contrast_stats(small_groups)

    # GloVe for the LCCP structural teacher over mining + eval patients
    toks = set()
    for c in mine_cands + eval_cands:
        toks.update([c["p"], c["v"]])
    glove = L.load_glove_for(toks)
    sel_full, _, _ = L.build_semantic_teacher(mine_cands, glove)
    sel_small, _, _ = L.build_semantic_teacher(small_cands, glove)

    def coverage_report(cands):
        nouns = [c["p"].lower() for c in cands
                 if c["p"].lower() not in L.FUNCWORD and c["p"].lower() not in L.PREPS
                 and c["p"].lower() not in L.PRONOUN and c["p"].lower().replace("'", "").isalpha()
                 and len(c["p"].lower()) >= 2]
        uniq = sorted(set(nouns))
        covered = [n for n in uniq if supersense(n) is not None]
        verbs = sorted(set(c["v"] for c in cands))
        vn_usable = [v for v in verbs if verbnet_object_selrestr_usable(v)]
        return {"n_unique_filler_nouns": len(uniq), "wordnet_supersense_coverage": round(len(covered) / max(1, len(uniq)), 4),
                "n_oov_nouns": len(uniq) - len(covered), "n_unique_verbs": len(verbs),
                "verbnet_object_selrestr_usable_rate": round(len(vn_usable) / max(1, len(verbs)), 4),
                "n_verbs_with_usable_selrestr": len(vn_usable)}

    cov = coverage_report(mine_cands + eval_cands)

    # G-FAIR-4 decisive noise probe: how often does the coherence bit WRONGLY reject a TRUE gold patient?
    # (gold used ONLY to characterize oracle noise here, NOT for training -- this is the mechanism of any
    # P2 negative: a noisy teacher that down-weights real objects will degrade the reader.)
    tp_bit1 = tp_bit0 = 0
    noise_reasons = defaultdict(int)
    for rec in gold.values():
        for g in rec["pos"]:
            b, r = coherence_bit(g["v"], g["patient"])
            if b == 1:
                tp_bit1 += 1
            else:
                tp_bit0 += 1
                noise_reasons[r] += 1
    cov["coherence_bit_false_incoherent_rate_on_true_gold_patients"] = round(tp_bit0 / max(1, tp_bit0 + tp_bit1), 4)
    cov["n_true_patients_wrongly_judged_incoherent"] = tp_bit0
    cov["n_true_patients_total"] = tp_bit0 + tp_bit1
    cov["false_incoherent_reason_counts"] = dict(noise_reasons)

    per_seed = []
    for seed in cfg["seeds"]:
        w_frozen, n_tr = train_weights(mine_cands, sel_full, coh_pairs_full, cfg, seed, use_coherence=False)
        w_scv, _ = train_weights(mine_cands, sel_full, coh_pairs_full, cfg, seed, use_coherence=True)
        w_scv_small, _ = train_weights(small_cands, sel_small, coh_pairs_small, cfg, seed, use_coherence=True)
        w_frozen_small, _ = train_weights(small_cands, sel_small, coh_pairs_small, cfg, seed, use_coherence=False)

        m_frozen = L.score_arm(eval_kept(w_frozen, eval_groups, cfg["keep_thr"]), gold)
        m_scv = L.score_arm(eval_kept(w_scv, eval_groups, cfg["keep_thr"]), gold)
        m_direct = L.score_arm(eval_kept(w_frozen, eval_groups, cfg["keep_thr"], direct=True), gold)
        m_scv_small = L.score_arm(eval_kept(w_scv_small, eval_groups, cfg["keep_thr"]), gold)
        m_frozen_small = L.score_arm(eval_kept(w_frozen_small, eval_groups, cfg["keep_thr"]), gold)
        per_seed.append({
            "seed": seed, "n_train_examples": n_tr,
            "frozen_precision": m_frozen["precision"], "scv_trained_precision": m_scv["precision"],
            "scv_direct_precision": m_direct["precision"],
            "frozen_recall": m_frozen["recall"], "scv_trained_recall": m_scv["recall"],
            "frozen_f1": m_frozen["f1"], "scv_trained_f1": m_scv["f1"],
            "delta_full": round(m_scv["precision"] - m_frozen["precision"], 4),
            "delta_small": round(m_scv_small["precision"] - m_frozen_small["precision"], 4),
            "w_frozen": [round(x, 4) for x in w_frozen.tolist()],
            "w_scv": [round(x, 4) for x in w_scv.tolist()],
        })

    deltas_full = [s["delta_full"] for s in per_seed]
    deltas_small = [s["delta_small"] for s in per_seed]
    mean_full = round(float(np.mean(deltas_full)), 4)
    mean_small = round(float(np.mean(deltas_small)), 4)
    min_full = round(float(np.min(deltas_full)), 4)
    frozen_mean = round(float(np.mean([s["frozen_precision"] for s in per_seed])), 4)
    scv_mean = round(float(np.mean([s["scv_trained_precision"] for s in per_seed])), 4)
    direct_mean = round(float(np.mean([s["scv_direct_precision"] for s in per_seed])), 4)

    if mean_full >= 0.02 and min_full > 0.0:
        p2 = "HARD_PASS_P2_TRAINING_SIGNAL_REAL"
    elif mean_full <= 0.0:
        p2 = "HARD_FAIL_P2_NULL_OR_NEGATIVE"
    else:
        p2 = "MIDDLE_BAND_P2"

    # distillation attribution (G-FAIR-3): how much of any move is direct-lookup vs learned weights
    distill = {"scv_direct_precision_mean": direct_mean, "frozen_precision_mean": frozen_mean,
               "scv_trained_precision_mean": scv_mean,
               "direct_minus_frozen": round(direct_mean - frozen_mean, 4),
               "trained_minus_frozen": round(scv_mean - frozen_mean, 4),
               "interpretation": ("if direct_minus_frozen already captures most of the residual, the DIRECT "
                                  "WordNet/VerbNet lookup resolves it and the LEARNED training signal adds "
                                  "little (pure distillation, scaffolded); if trained_minus_frozen > 0 while "
                                  "the direct bit is NOT applied at eval, the reader has INTERNALIZED the "
                                  "type-knowledge into portable structural cue-weights (still scaffolded by "
                                  "the curated oracle, NOT learned from the substrate's own experience).")}

    ablation = {"mean_delta_full_corpus": mean_full, "mean_delta_small_gold_slice_only": mean_small,
                "n_coherence_pairs_full": cstats_full["n_coherence_pairs"],
                "n_coherence_pairs_small": cstats_small["n_coherence_pairs"],
                "interpretation": ("if full<=0 AND small<=0 -> mechanism-null; if full>small (esp full>0, "
                                   "small<=0) -> sparsity was masking the signal (per animacy/per-verb-stats "
                                   "sparsity lesson).")}

    return {"verdict_p2": p2, "mean_delta_full": mean_full, "min_delta_full": min_full,
            "frozen_precision_mean": frozen_mean, "scv_trained_precision_mean": scv_mean,
            "per_seed": per_seed, "corpus_size_ablation": ablation,
            "distillation_attribution": distill, "oracle_coverage_noise": cov,
            "contrast_stats_full_mining": cstats_full, "contrast_stats_small": cstats_small,
            "n_mining_sentences": len(mine_data), "n_eval_sentences": len(eval_data)}


# ----------------------------------------------------------------------------------------------
# Prediction 3: scope.
# ----------------------------------------------------------------------------------------------
def prediction3_scope(inst_groups):
    cstats, _ = contrast_stats(inst_groups)
    bucket = cstats["n_exactly_one_coherent"]
    if bucket >= 10:
        p3 = "HARD_PASS_P3_SCOPE_REAL"
    elif bucket < 5:
        p3 = "HARD_FAIL_P3_NEAR_EMPTY"
    else:
        p3 = "MIDDLE_BAND_P3"
    return {"verdict_p3": p3, "exactly_one_coherent_bucket": bucket,
            "artifact_vs_location_specific_bucket": cstats["n_artifact_vs_location_pairs"],
            "contrast_stats_gold_slice": cstats}


# ----------------------------------------------------------------------------------------------
# Run.
# ----------------------------------------------------------------------------------------------
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
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = _out_dir(mode)

    p1, inst_groups, _glove = prediction1_selector(cfg)
    p3 = prediction3_scope(inst_groups)
    p2 = prediction2_trainer(cfg)

    baseline_in_band = bool(0.05 < p1["baseline_precision_reproduced"] < 0.95)
    contrast_fires = bool(p3["exactly_one_coherent_bucket"] > 0)

    elapsed = time.perf_counter() - t0
    msg = (f"P1={p1['verdict_p1']} P2={p2['verdict_p2']} P3={p3['verdict_p3']} "
           f"| baseline_LCCP_C_P={p1['baseline_precision_reproduced']:.3f} "
           f"scv_sel_P={p1['scv_selector']['precision']:.3f} (changed={p1['n_changed']} "
           f"fixed={p1['fixed']} broken={p1['broken']} netdP={p1['net_precision_delta']:+.3f}) "
           f"| P2 frozen_P={p2['frozen_precision_mean']:.3f} scv_trained_P={p2['scv_trained_precision_mean']:.3f} "
           f"meandelta={p2['mean_delta_full']:+.3f} (min={p2['min_delta_full']:+.3f}) "
           f"direct_P={p2['distillation_attribution']['scv_direct_precision_mean']:.3f} "
           f"| ablation full={p2['corpus_size_ablation']['mean_delta_full_corpus']:+.3f} "
           f"small={p2['corpus_size_ablation']['mean_delta_small_gold_slice_only']:+.3f} "
           f"| scope one-coh={p3['exactly_one_coherent_bucket']} artif-vs-loc={p3['artifact_vs_location_specific_bucket']} "
           f"| WNcov={p2['oracle_coverage_noise']['wordnet_supersense_coverage']:.3f} "
           f"VNselrestr={p2['oracle_coverage_noise']['verbnet_object_selrestr_usable_rate']:.3f} "
           f"bit_false_incoh={p2['oracle_coverage_noise']['coherence_bit_false_incoherent_rate_on_true_gold_patients']:.3f} "
           f"| base_in_band={baseline_in_band} contrast_fires={contrast_fires}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": f"{p1['verdict_p1']}|{p2['verdict_p2']}|{p3['verdict_p3']}",
        "verdict_msg": msg, "summary": msg, "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "config": cfg,
        "prediction1_selector": p1, "prediction2_trainer": p2, "prediction3_scope": p3,
        "baseline_in_band": baseline_in_band, "contrast_fires": contrast_fires,
        "final_metrics_atomicity": "tmp_replace",
        "gold_type_oracle_independent": True,
        "gold_independence_rationale": ("data/gold_mcguffey_lccp_argstruct_v1.json is human who-did-what "
            "annotation of pos/nopat argument structure, annotated by READING RAW TEXT (verified _meta."
            "independence), INDEPENDENT of WordNet/VerbNet typing. The Pred-1 residual triage is computed "
            "vs GOLD (within-frame FP), NOT vs supersense. So the SCV is NOT predicting its own oracle "
            "(G-FAIR-1 satisfied)."),
        "claim_ceiling": ("SELF-SUPERVISED w.r.t. PARSE-LABELS (no gold parses), but SUPERVISED by an "
            "EXTERNAL HAND-CURATED world-knowledge oracle (WordNet supersenses + VerbNet). The world-"
            "knowledge is LOOKED UP, not learned by the substrate. This run tests the CONTRAST MECHANISM, "
            "NOT learned-world-experience. The fully-honest 'substrate learns type-knowledge from its own "
            "reading' version is a HARDER, SEPARATE future test (likely corpus-sparse per atom 29357). "
            "Do NOT frame any result as 'the substrate evaluates scene realism from its own experience' "
            "(G-FAIR-2)."),
        "excluded_from_mining": EXCLUDED_FROM_MINING,
        "novelty_note": ("Genuine novelty = CONTRAST (score BOTH rivals, use the GAP), which does NOT "
            "depend on where the knowledge came from. Prior signals failed to TRAIN because non-contrastive "
            "(cosine=blended score; animacy=pre-filter, fixed_ON=0)."),
        "REQUIRED_FIELDS": ["verdict", "prediction1_selector", "prediction2_trainer", "prediction3_scope",
                            "gold_type_oracle_independent", "claim_ceiling",
                            "prediction2_trainer.distillation_attribution",
                            "prediction2_trainer.oracle_coverage_noise",
                            "prediction2_trainer.corpus_size_ablation"],
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"  [G-FAIR-3 distillation] direct-frozen={p2['distillation_attribution']['direct_minus_frozen']:+.3f} "
          f"trained-frozen={p2['distillation_attribution']['trained_minus_frozen']:+.3f}", flush=True)
    print(f"  [G-FAIR-4 oracle] WordNet noun coverage={p2['oracle_coverage_noise']['wordnet_supersense_coverage']:.3f} "
          f"(OOV={p2['oracle_coverage_noise']['n_oov_nouns']}) | VerbNet obj-selrestr usable="
          f"{p2['oracle_coverage_noise']['verbnet_object_selrestr_usable_rate']:.3f} "
          f"({p2['oracle_coverage_noise']['n_verbs_with_usable_selrestr']} verbs)", flush=True)
    print(f"  [P2 per-seed deltas] {[s['delta_full'] for s in p2['per_seed']]}", flush=True)
    return payload


def self_test():
    # coherence bit fires as designed
    assert coherence_bit("build", "hut")[0] == 1, "hut should be coherent object (artifact)"
    assert coherence_bit("come", "out")[0] == 0, "funcword filler incoherent"
    assert coherence_bit("throw", "it")[0] == 1, "pronoun object coherent"
    b_field, r_field = coherence_bit("cross", "field")
    assert b_field == 0 and "noun.location" in r_field, f"field should be type-mismatch location, got {r_field}"
    # HONEST self-test of the known granularity failure: stream is noun.object NOT noun.location under WordNet
    assert supersense("stream") == "noun.object", "granularity finding: WordNet buckets stream as object"
    assert supersense("hut") == "noun.artifact"
    # contrastive update moves a weight on a clean toy: one coherent (post-verbal concrete) vs one
    # incoherent (funcword) rival -> coh pass should raise score(pos)-score(neg).
    toks = L.tokenize("he built a hut out")
    f_pos = np.concatenate([L.candidate_features(toks, "built", "hut")[0], [float(coherence_bit("build", "hut")[0])]])
    f_neg = np.concatenate([L.candidate_features(toks, "built", "out")[0], [float(coherence_bit("build", "out")[0])]])
    assert f_pos[-1] == 1.0 and f_neg[-1] == 0.0, "f_type channel must separate hut(1) from out(0)"
    cfg = dict(sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=5, coh_lr=0.10, coh_margin=0.30)
    cands = [{"sid": "t", "v": "build", "p": "hut", "tup": ("built", "he", "hut"), "feat": f_pos},
             {"sid": "t", "v": "build", "p": "out", "tup": ("built", "he", "out"), "feat": f_neg}]
    sel_fn, _, _ = L.build_semantic_teacher(cands, {})
    w_no, _ = train_weights(cands, sel_fn, [(f_pos, f_neg)], cfg, 7, use_coherence=False)
    w_yes, _ = train_weights(cands, sel_fn, [(f_pos, f_neg)], cfg, 7, use_coherence=True)
    gap_no = float(np.dot(w_no, f_pos)) - float(np.dot(w_no, f_neg))
    gap_yes = float(np.dot(w_yes, f_pos)) - float(np.dot(w_yes, f_neg))
    assert gap_yes > gap_no, f"coherence pass must widen pos-neg gap: {gap_yes} !> {gap_no}"
    print(f"[{ANCHOR_NAME}] self-test PASS | coherence bits fire; contrastive update widens gap "
          f"{gap_no:.3f}->{gap_yes:.3f}; stream={supersense('stream')} hut={supersense('hut')} "
          f"field={supersense('field')}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
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
