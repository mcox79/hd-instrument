# CELL-TEMPLATE (measurement/build-probe; NOT a queue-dispatch cell). v2 HIGH-PRECISION FILTER on
# top of exp_stated_entity_fate_reading_extractor_v1 (curated P=R=1.0 but real-prose hand-checked
# P=0.394; failure = role/argument-structure + verb-sense, NOT arc-parse). Reframe (coordinator):
# for GROW-BY-READING, PRECISION is paramount and RECALL is nearly free (read millions of sentences,
# accumulate correct facts from the CLEAN ones; a poisoned store fails, a slow-but-clean store wins).
# Trade recall HARD for precision, target filtered P >= 0.85.
#
# Six glass-box filters, each from v1's own error taxonomy (_handcheck_adjudicated.json), NO LLM:
#  1. PATIENT must be a true DIRECT OBJECT (transitive active, no governing ADP) or the SUBJECT of a
#     clean passive -- REJECT any PP-object / by-agent / locative / goal / possessor (an ADP
#     of/in/into/towards/by/at/from... governs the patient NP). Kills wrong_patient (17).
#  2. Intransitive fate-verbs (rise/fall/flow/travel/...) NEVER emit a following object; + a
#     clause-boundary/distance guard so 'coal burn ..., the mixture' can't grab a later nominal.
#     Kills intransitive_subject_is_theme (13).
#  3. Causative/light-verb 'make' guard: reject 'make up/of/out' particles + 'make X <ADJ>' causatives
#     (make it hotter/easier/blind/more concentrated). Kills causative_light_verb (12).
#  4. Proper-noun/title reject: verb or patient tagged PROPN, or a Titlecase mid-sentence patient.
#     Kills proper_noun_title (6) (Burns-the-person, song/book titles).
#  5. Concreteness/verb-sense gate: emit ONLY when the entity head is a physical OBJECT per
#     hdlab.animacy_lexicon.lookup_animacy (category=='object') -- rejects abstract (decision/
#     progress/notice/avenue), animate (cat/Solomon), and work/album/document senses. Kills
#     verb_sense (3) + adjectival/noun-misparse (4).
#  6. Confidence gate: require a clean SVO-active (nominal subject before the verb + adjacent object)
#     OR clean BE+participle(+optional by-PP) passive; the POS-mistag positional-recovery path is
#     allowed ONLY through all of 1-5. + WIDENED negation window (adverb between 'not' and verb).
#
# WIRE-DON'T-ISLAND: reuses the v1 extractor's frontend (candidate_generator = pos_tagger+arc_parser,
# UAS 0.776) + thematic_role_labeler + hd_fact_store + SimpleWiki + ProPara. NO rebuild.
# See preregs/2026-08-11_stated_entity_fate_reading_extractor_v2_highprecision.md for full pre-reg.
"""exp_stated_entity_fate_reading_extractor_v2_highprecision -- precision-hardened grow-by-reading.

Validation: re-score curated gold (design/held-out P should stay ~1.0; negation must stay clean) +
run raw(v1) AND strict(v2) extraction on the SAME corpus sample to get the survival rate / recall
cost + absolute surviving count, then HAND-CHECK a fresh random sample of the SURVIVORS (target
P>=0.85). Corpus-scale estimate (facts-per-science-sentence x total qualifying SimpleWiki science
sentences x hand-precision) + ProPara dev-entity coverage of the surviving fact set. Store survivors
in hd_fact_store (trust=TRUST_LOW). Modes: --self-test / (no flag)=validation.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import random
import re
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

ANCHOR_NAME = "stated_entity_fate_reading_extractor_v2_highprecision"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
SIMPLEWIKI_PATH = os.path.join(REPO_ROOT, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")

from hdlab.thematic_role_labeler import lemma_verb, frame_slot_role, is_passive_clause  # noqa: E402
from hdlab.animacy_lexicon import lookup_animacy  # noqa: E402
from hdlab.hd_fact_store import HDFactStore  # noqa: E402
# reuse v1 wholesale (wire-don't-island): frontend, lexicon, helpers, curated gold, corpus helpers
from experiments.exp_stated_entity_fate_reading_extractor_v1 import (  # noqa: E402
    _load_or_build_frontend, FATE_VERB_LEXICON, FATE_LABEL, _singularize, _expand_np,
    extract_facts as extract_facts_raw, _propara_train_sentences, NOMINAL, _BE_AUX, _NEG,
    _STOP_ENT, _neg_in_window, _WORD, _SCI_TOPIC,
    CURATED_DESIGN, CURATED_HELDOUT, CURATED_NEGATION,
)
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import _load_split  # noqa: E402
from experiments.exp_propara_schema_learned_grounded_binder_v1 import (  # noqa: E402
    _participant_head_tokens, _seen_surface_tokens, _is_unseen_surface,
)

# ------------------------------------------------------------------ filter constants
_ADP_PREPS = {"of", "in", "into", "on", "onto", "to", "toward", "towards", "by", "at", "from",
              "through", "over", "across", "with", "for", "out", "off", "about", "against",
              "between", "among", "around", "near", "above", "below", "beneath", "within", "along"}
# motion/appearance verbs that in ordinary prose are INTRANSITIVE (the mover IS the subject); they
# must NEVER emit a following nominal as patient (lemma_verb-reduced forms too).
_INTRANSITIVE_ONLY = set()
for _v in ["rise", "ris", "fall", "flow", "travel", "circulate", "circulat", "drift", "migrate",
           "migrat", "ascend", "descend", "emerge", "emerg", "arise", "aris", "erupt"]:
    _INTRANSITIVE_ONLY.add(_v)
_LIGHT_MAKE = {"make", "mak"}
_CLAUSE_BREAK_TOK = {",", ";", ":", "and", "or", "but", "because", "which", "that", "while", "when", "so"}
_COMPARATIVE = {"more", "less", "better", "worse", "easier", "harder", "hotter", "colder", "bigger",
                "smaller", "faster", "slower", "blind", "hard", "soft", "concentrated"}


def _np_start(pos: List[str], i: int) -> int:
    j = i
    while j - 1 >= 1 and pos[j - 2] in {"NOUN", "PROPN", "ADJ", "NUM"}:
        j -= 1
    return j


def _patient_is_pp_object(tokens: List[str], pos: List[str], patient_i: int) -> bool:
    """True if the patient NP is governed by a preposition (PP-object / by-agent / locative / goal /
    possessor) rather than being a bare direct object. Filter rule 1. Coordination-aware: an ADP
    governing a COORDINATED NP ('of nitrogen and sulphur', 'by air and water') still rejects the
    later conjunct (walk back over 'and/or' + the conjunct NP, then re-check for the governing ADP)."""
    b = _np_start(pos, patient_i) - 1
    while True:
        if b >= 1 and pos[b - 1] == "DET":
            b -= 1
        if b >= 1 and (pos[b - 1] == "ADP" or tokens[b - 1].lower() in _ADP_PREPS):
            return True
        if b >= 1 and (pos[b - 1] == "CCONJ" or tokens[b - 1].lower() in {"and", "or"}):
            b -= 1
            while b >= 1 and pos[b - 1] in {"NOUN", "PROPN", "ADJ", "NUM"}:
                b -= 1
            continue
        return False


def _clause_break_between(tokens: List[str], pos: List[str], a: int, b: int) -> bool:
    for j in range(a + 1, b):
        if pos[j - 1] in {"CCONJ", "SCONJ"} or tokens[j - 1].lower() in _CLAUSE_BREAK_TOK:
            return True
    return False


def _causative_make(tokens: List[str], pos: List[str], v: int, patient_i: int, lemma: str) -> bool:
    if lemma not in _LIGHT_MAKE:
        return False
    n = len(tokens)
    if v < n and tokens[v].lower() in {"up", "of", "out", "off"}:  # tokens[v] = 1-based v+1
        return True
    for j in range(patient_i + 1, min(n, patient_i + 2) + 1):  # ADJ/comparative right after the object
        if pos[j - 1] == "ADJ" or tokens[j - 1].lower() in _COMPARATIVE:
            return True
    return False


def _proper_or_title(tokens: List[str], pos: List[str], v: int, patient_i: int) -> bool:
    if pos[v - 1] == "PROPN" or pos[patient_i - 1] == "PROPN":
        return True
    tok = tokens[patient_i - 1]
    if patient_i > 1 and tok[:1].isupper() and not tok.isupper():  # Titlecase mid-sentence proper noun
        return True
    return False


def _is_concrete_object(head: str) -> bool:
    r = lookup_animacy(head, "NOUN")
    return bool(r and r.get("category") == "object")


def extract_facts_strict(gen, text: str) -> List[Dict]:
    """High-precision STATED (entity,fate) extraction: v1 candidate selection + the six filters."""
    cr = gen.generate(text, extended=True)
    tokens, pos, heads = cr.tokens, cr.pos, cr.heads
    n = len(tokens)
    if n == 0:
        return []
    passive_sent = is_passive_clause(tokens, pos)
    out: List[Dict] = []
    seen = set()
    for v in range(1, n + 1):
        lemma = lemma_verb(tokens[v - 1])
        fate = FATE_VERB_LEXICON.get(lemma)
        if fate is None:
            continue
        if frame_slot_role(lemma, "obj") != "PATIENT":
            continue
        local_passive = any(tokens[j - 1].lower() in _BE_AUX for j in range(max(1, v - 3), v))
        voice_passive = local_passive or (passive_sent and pos[v - 1] == "VERB")
        # INFINITIVAL/PURPOSE guard (from taxonomy: passive 'to make/form X' picks the matrix
        # subject/device/reactant as a false patient). If the fate-verb is an infinitival complement
        # ('to make electricity', 'for carrying items'), it is NOT passive: its patient is the
        # POST-verbal object, never the pre-verbal matrix subject. Force active-object mode.
        prev = tokens[v - 2].lower() if v >= 2 else ""
        prev2 = tokens[v - 3].lower() if v >= 3 else ""
        if prev in {"to", "for"} or (v >= 3 and pos[v - 2] == "ADV" and prev2 in {"to", "for"}):
            voice_passive = False
        path = "parse" if pos[v - 1] == "VERB" else "positional"

        # ---- candidate patient selection
        patient_i = None
        noms_before = [i for i in range(1, v) if pos[i - 1] in NOMINAL]
        noms_after = [i for i in range(v + 1, n + 1) if pos[i - 1] in NOMINAL]
        if voice_passive:
            # clean passive: patient = surface subject (nearest preceding nominal)
            patient_i = noms_before[-1] if noms_before else None
        else:
            # transitive active: patient = nearest following nominal (direct object)
            if lemma in _INTRANSITIVE_ONLY:
                continue  # rule 2: intransitive motion never takes a following-object patient
            patient_i = noms_after[0] if noms_after else None
            # rule 2/6: object must be CLOSE + no clause break between verb and object
            if patient_i is not None:
                if (patient_i - v) > 4 or _clause_break_between(tokens, pos, v, patient_i):
                    continue
        if patient_i is None:
            continue

        # ---- rule 6 confidence gate: require a clean shape
        if not voice_passive and not noms_before:
            continue  # active with no subject before the verb (title/fragment)

        # ---- rule 1: PP-object / by-agent / locative / goal / possessor reject
        if _patient_is_pp_object(tokens, pos, patient_i):
            continue
        # ---- rule 3: causative/light-verb make guard
        if _causative_make(tokens, pos, v, patient_i, lemma):
            continue
        # ---- rule 4: proper-noun / title reject
        if _proper_or_title(tokens, pos, v, patient_i):
            continue
        # ---- rule 6: widened negation guard (adverb between 'not' and verb)
        if _neg_in_window(tokens, v - 4, max(patient_i, v)):
            continue

        phrase, head_tok = _expand_np(tokens, pos, patient_i, "back")
        if head_tok in _STOP_ENT or len(head_tok) < 2 or not head_tok.isalpha():
            continue
        # ---- rule 5: concreteness / verb-sense gate (physical OBJECT only)
        if not _is_concrete_object(head_tok):
            continue

        key = (head_tok, fate, lemma)
        if key in seen:
            continue
        seen.add(key)
        out.append({"entity": phrase, "entity_head": head_tok, "fate": fate,
                    "fate_label": FATE_LABEL[fate], "via_verb": lemma,
                    "voice": "passive" if voice_passive else "active", "path": path,
                    "sentence": text.strip()})
    return out


# ------------------------------------------------------------------ curated scoring (reuse contract)
def _score_curated(gen, cases) -> Dict:
    tp = fp = fn = 0
    rows = []
    for sent, gold in cases:
        gold_set = {(_singularize(e), f) for e, f in gold}
        preds = extract_facts_strict(gen, sent)
        pred_set = {(p["entity_head"], p["fate"]) for p in preds}
        tp += len(gold_set & pred_set)
        fp += len(pred_set - gold_set)
        fn += len(gold_set - pred_set)
        rows.append({"sentence": sent, "gold": sorted(gold_set), "pred": sorted(pred_set)})
    prec = tp / (tp + fp) if (tp + fp) else (1.0 if fn == 0 else 0.0)
    rec = tp / (tp + fn) if (tp + fn) else 1.0
    return {"n_cases": len(cases), "tp": tp, "fp": fp, "fn": fn,
            "precision": round(prec, 4), "recall": round(rec, 4), "rows": rows}


def _score_negation(gen, cases) -> Dict:
    n_fp = 0
    rows = []
    for sent, _g in cases:
        preds = extract_facts_strict(gen, sent)
        n_fp += len(preds)
        rows.append({"sentence": sent, "emitted": [(p["entity_head"], p["fate_label"]) for p in preds]})
    return {"n_cases": len(cases), "n_false_positive_emissions": n_fp, "negation_clean": n_fp == 0, "rows": rows}


# ------------------------------------------------------------------ corpus sampler (returns n_seen)
def _sample_simplewiki_counted(n_target: int, seed: int) -> Tuple[List[str], int]:
    rng = random.Random(seed)
    reservoir: List[str] = []
    n_seen = 0
    with open(SIMPLEWIKI_PATH, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not (12 <= len(s) <= 240):
                continue
            if not _SCI_TOPIC.search(s):
                continue
            toks = set(_WORD.findall(s.lower()))
            if not any(lemma_verb(t) in FATE_VERB_LEXICON for t in toks):
                continue
            n_seen += 1
            if len(reservoir) < n_target:
                reservoir.append(s)
            else:
                j = rng.randint(0, n_seen - 1)
                if j < n_target:
                    reservoir[j] = s
    return reservoir, n_seen


def run_validation(n_simplewiki: int = 4000, sample_dump: int = 100, seed: int = 20260811) -> Dict:
    t0 = time.time()
    gen = _load_or_build_frontend()

    design = _score_curated(gen, CURATED_DESIGN)
    heldout = _score_curated(gen, CURATED_HELDOUT)
    negation = _score_negation(gen, CURATED_NEGATION)
    print(f"[curated] STRICT design P={design['precision']}/R={design['recall']} "
          f"heldout P={heldout['precision']}/R={heldout['recall']} "
          f"negation_clean={negation['negation_clean']}", flush=True)

    sw, n_seen_total = _sample_simplewiki_counted(n_simplewiki, seed)
    pp = _propara_train_sentences()
    print(f"[corpus] simplewiki sampled={len(sw)} (of {n_seen_total} qualifying) propara={len(pp)}", flush=True)

    store = HDFactStore(n_dim=8192, seed=0)
    survivors: List[Dict] = []
    n_raw = 0
    path_counts = Counter()
    fate_counts = Counter()
    n_raw_sw = 0
    n_strict_sw = 0
    for src_name, sents in (("simplewiki", sw), ("propara_train", pp)):
        for s in sents:
            raw = extract_facts_raw(gen, s)
            strict = extract_facts_strict(gen, s)
            n_raw += len(raw)
            if src_name == "simplewiki":
                n_raw_sw += len(raw)
                n_strict_sw += len(strict)
            for fact in strict:
                fact["source_corpus"] = src_name
                survivors.append(fact)
                path_counts[fact["path"]] += 1
                fate_counts[fact["fate_label"]] += 1
                store.store(subject=fact["entity"], relation=f"fate_via_{fact['via_verb']}",
                            obj=fact["fate_label"], source="reading", trust="TRUST_LOW")
    n_strict = len(survivors)
    survival_rate = round(n_strict / n_raw, 4) if n_raw else 0.0
    print(f"[corpus] raw(v1)={n_raw} strict(v2)={n_strict} survival_rate={survival_rate} "
          f"paths={dict(path_counts)} fates={dict(fate_counts)}", flush=True)

    # distinct entity heads among survivors
    distinct_entities = sorted({f["entity_head"] for f in survivors})

    # ProPara dev-entity coverage of the surviving fact set (does reading cover the missing entities?)
    dev = _load_split("dev")
    train = _load_split("train")
    seen_tokens = _seen_surface_tokens(train)
    dev_participants = sorted({(str(para["para_id"]), part) for para in dev for part in para["participants"]})
    surv_heads = {f["entity_head"] for f in survivors}
    surv_heads_sing = surv_heads | {_singularize(h) for h in surv_heads}

    def _covered(part: str) -> bool:
        return any(_singularize(t) in surv_heads_sing or t in surv_heads_sing
                   for t in _participant_head_tokens(part))

    dev_unseen = [(pid, part) for (pid, part) in dev_participants if _is_unseen_surface(part, seen_tokens)]
    n_dev_cov = sum(1 for (_pid, part) in dev_participants if _covered(part))
    n_unseen_cov = sum(1 for (_pid, part) in dev_unseen if _covered(part))
    print(f"[coverage] ProPara dev participants covered by reading: {n_dev_cov}/{len(dev_participants)}; "
          f"unseen covered: {n_unseen_cov}/{len(dev_unseen)}", flush=True)

    # corpus-scale estimate (SimpleWiki science subset only, from the sampled rate)
    facts_per_sci_sentence = (n_strict_sw / len(sw)) if sw else 0.0
    est_full_survivors = int(facts_per_sci_sentence * n_seen_total)

    # dump a fresh random sample of SURVIVORS for hand adjudication (offset chosen AFTER the
    # infinitival+coordination hardening so this is an independent sample, not the tuned-against set)
    rng = random.Random(seed + 23)
    idxs = list(range(len(survivors)))
    rng.shuffle(idxs)
    sample = [survivors[i] for i in idxs[:sample_dump]]
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    dump_path = os.path.join(OUTPUT_DIR, "_survivors_for_handcheck.json")
    with open(dump_path, "w", encoding="utf-8") as f:
        json.dump({"n_survivors": len(survivors), "sample": sample}, f, indent=2)
    print(f"[corpus] dumped {len(sample)} survivors for hand-check -> {dump_path}", flush=True)

    # PRELIMINARY verdict on reproducible curated + survival; hand-checked P folded in by operator
    if not negation["negation_clean"]:
        verdict = "HARD_FAIL_NEGATION_HALLUCINATION"
    elif heldout["precision"] >= 0.85:
        verdict = "STRICT_READY_PENDING_HANDCHECK"
    else:
        verdict = "STRICT_CURATED_REGRESSED"
    verdict_msg = (f"{verdict}: curated STRICT design P={design['precision']}/R={design['recall']}, "
                   f"held-out P={heldout['precision']}/R={heldout['recall']}, negation_clean="
                   f"{negation['negation_clean']}; corpus raw={n_raw} -> strict={n_strict} "
                   f"(survival={survival_rate}); distinct_entities={len(distinct_entities)}; "
                   f"ProPara dev coverage={n_dev_cov}/{len(dev_participants)} "
                   f"(unseen {n_unseen_cov}/{len(dev_unseen)}); est_full_simplewiki_survivors~{est_full_survivors}; "
                   f"hand-check sample dumped ({len(sample)}) -- final precision folded in by operator")

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2), "run_mode": "validation", "anchor_name": ANCHOR_NAME,
        "curated_design": design, "curated_heldout": heldout, "curated_negation": negation,
        "corpus": {"n_simplewiki_sampled": len(sw), "n_simplewiki_qualifying_total": n_seen_total,
                   "n_propara_train_sents": len(pp), "n_raw_v1": n_raw, "n_strict_v2": n_strict,
                   "survival_rate": survival_rate, "n_raw_simplewiki": n_raw_sw,
                   "n_strict_simplewiki": n_strict_sw, "path_counts": dict(path_counts),
                   "fate_counts": dict(fate_counts), "n_distinct_entities": len(distinct_entities),
                   "facts_per_science_sentence": round(facts_per_sci_sentence, 4),
                   "est_full_simplewiki_survivors": est_full_survivors},
        "propara_coverage": {"n_dev_participants": len(dev_participants), "n_dev_covered": n_dev_cov,
                             "n_dev_unseen": len(dev_unseen), "n_dev_unseen_covered": n_unseen_cov,
                             "dev_coverage_frac": round(n_dev_cov / max(len(dev_participants), 1), 4),
                             "dev_unseen_coverage_frac": round(n_unseen_cov / max(len(dev_unseen), 1), 4)},
        "distinct_entities_sample": distinct_entities[:80],
        "handcheck_dump_path": dump_path,
        "bands": {"HARD_PASS_FILTERED_PRECISION": 0.85},
    }


# ------------------------------------------------------------------ metrics I/O
def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ------------------------------------------------------------------ self-test
def self_test() -> Dict:
    print("[self-test] starting", flush=True)
    out = {"checks": {}}
    gen = _load_or_build_frontend()

    # (1) filters still emit the clean canonical facts
    keep = set()
    for s in ["Fire consumes the wood.", "The fuel is consumed.", "Combustion produces carbon dioxide.",
              "Plants release oxygen.", "The river carries sediment."]:
        for p in extract_facts_strict(gen, s):
            keep.add((p["entity_head"], p["fate"]))
    for need in [("wood", "DESTROY"), ("fuel", "DESTROY"), ("dioxide", "CREATE"),
                 ("oxygen", "CREATE"), ("sediment", "MOVE")]:
        assert need in keep, f"strict filter dropped a clean fact {need}: {sorted(keep)}"
    out["checks"]["clean_kept"] = sorted(keep)
    print("[self-test] clean canonical facts survive the strict filter", flush=True)

    # (2) each filter rejects its taxonomy target
    rej = [
        ("rise into the sky", "rise into the sky"),                      # PP goal + intransitive
        ("hydrogen burns in oxygen", "burns in <loc>"),                  # PP locative
        ("valleys formed by lahars", "by-agent"),                        # by-agent
        ("It makes the object hotter", "causative make X ADJ"),          # causative
        ("The Temple of Solomon was burned", "possessor + PROPN"),       # possessor/propn
        ("It could make the cat blind", "animate + causative"),          # animate/causative
        ("They make big progress here", "abstract object"),             # abstract concreteness
    ]
    rejrows = {}
    for s, why in rej:
        preds = extract_facts_strict(gen, s)
        rejrows[why] = [(p["entity_head"], p["fate_label"]) for p in preds]
        assert preds == [], f"strict filter FAILED to reject [{why}] on {s!r}: {preds}"
    out["checks"]["rejected"] = rejrows
    print("[self-test] all taxonomy targets rejected (PP/by-agent/causative/propn/animate/abstract)", flush=True)

    # (3) negation still clean (incl adverb-separated)
    for s in ["The wood is not consumed.", "No oxygen is produced.",
              "They do not readily form bonds."]:
        assert extract_facts_strict(gen, s) == [], f"negation leak on {s!r}: {extract_facts_strict(gen, s)}"
    out["checks"]["negation"] = "clean"
    print("[self-test] negation guard clean (incl 'do not readily form')", flush=True)

    out["verdict"] = "SELFTEST_PASS"
    out["verdict_msg"] = "SELFTEST_PASS: clean facts survive; PP/by-agent/causative/propn/animate/abstract rejected; negation clean"
    out["summary"] = "SELFTEST_PASS"
    out["elapsed_s"] = 0.0
    out["run_mode"] = "self_test"
    out["anchor_name"] = ANCHOR_NAME
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--n-simplewiki", type=int, default=4000)
    p.add_argument("--sample-dump", type=int, default=100)
    args = p.parse_args()
    run_mode = "self_test" if args.self_test else "validation"
    out_dir = OUTPUT_DIR + ("_selftest" if args.self_test else "")
    _write_start_marker(out_dir, run_mode)
    try:
        if args.self_test:
            t0 = time.time()
            metrics = self_test()
            metrics["elapsed_s"] = round(time.time() - t0, 2)
        else:
            metrics = run_validation(n_simplewiki=args.n_simplewiki, sample_dump=args.sample_dump)
        _write_metrics(out_dir, metrics)
        print(f"[main] wrote metrics verdict={metrics['verdict']}", flush=True)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
