#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_census_mcguffey_first_reader_whoaffected_escalation_recon_v1

RECONNAISSANCE / CENSUS (NOT a capability cell; NO gold who-affected labels). Characterizes the
McGuffey First Reader (just ingested) as a candidate FIRST real-story-reading target for the
who-is-affected + oracle-escalation loop, BEFORE building the loop. Measures the reader's BEHAVIOR
(its own confidence signals: arc-parser margin + the state-vs-parse CONTRADICTION flag) + the text's
STRUCTURE (discourse density) -- NOT accuracy (no gold parse for McGuffey).

CENSUS QUESTIONS (the load-bearing steer):
  1. STRUCTURE: lesson/sentence count; cross-sentence referential rate (fraction of sentences with a
     pronoun that the running WorkingOverlay binds to a PRIOR-sentence entity) = is there discourse?
  2. ESCALATION LOAD: run the reader; what fraction of who-affected decisions would go to the oracle
     under (a) low arc-parser margin (abstain) and (b) the contradiction flag = escalation rate.
  3. REGISTER-vs-DISCOURSE split of the uncertain cases: register/archaic difficulty (inversion /
     quotative-inversion / archaic markers -- the known labeler weakness) vs genuine DISCOURSE
     (cross-sentence pronoun reference). Load-bearing: if register DOMINATES -> confounded target.
  4. Does the contradiction flag FIRE on real story text? flag_rate McGuffey vs UD-EWT.

COMPARABILITY: the abstain margin threshold tau_abstain is the 16th-percentile of predicted-patient
base-pick arc-parser margins measured on a UD-EWT test subset (the memory's ~16% abstain operating
point), applied UNCHANGED to McGuffey so the escalation rate is calibrated + comparable. UD-EWT
contradiction flag_rate is computed on the same subset (gold available there) for the side-by-side.

REUSE (read-only import): the VALIDATED reader front-end + overlay wiring from
exp_read_discourse_docorder_stateofmind_whoaffected_ud_ewt_v1 (reader_pass, base_pick, salient_pick,
observe_sentence, build_scored, coherence_stats, load_ud_docs). No hdlab mutation.

HONEST CONTRACT (pre-registered VERDICT bands -- this is a MEASUREMENT cell; deliverable = numbers):
  TOO_SIMPLE: cross_sentence_referential_rate < 0.05 (little discourse -> context cannot help).
  CONFOUNDED_ARCHAIC: of uncertain instances, register/archaic share >= 0.60 (labeler-register
      difficulty dominates escalation -> modern story text would be cleaner).
  GOOD_TARGET: cross_sentence_referential_rate >= 0.08 AND register share < 0.50 AND escalation_rate
      in a workable band [0.05, 0.60] (real discourse, manageable + not archaic-dominated escalation).
  MIXED: otherwise (reported honestly with the numbers; USER + skunkworks-VET decide).

LOCAL-ONLY foreground; NO queue, NO push, NO remote-persist, NO git add. Determinism: OMP/MKL/
OPENBLAS=1, fixed seeds, default_rng, sorted(set). Storage: writes metrics.json (atomic tmp+replace).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import re
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "census_mcguffey_first_reader_whoaffected_escalation_recon_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# reuse the validated reader/overlay wiring (read-only import)
from experiments.exp_read_discourse_docorder_stateofmind_whoaffected_ud_ewt_v1 import (  # noqa: E402
    POS_PATH, ARC_PATH, LABELER_PATH, UD_TEST,
    reader_pass, base_pick, salient_pick, observe_sentence,
    load_ud_docs, build_scored, coherence_stats,
)
from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402
from hdlab.arc_labeler import ArcLabeler  # noqa: E402
from hdlab.state_of_mind import WorkingOverlay, PRONOUN_SCOPE  # noqa: E402
from hdlab.candidate_generator import candidates_from_parse  # noqa: E402

MCG_TXT = os.path.join(REPO_ROOT, "data", "exp_textbook_extract_mcguffey_v1",
                       "mcguffey_first_document_order.txt")

PATIENT_LABELS = {"obj", "nsubj:pass"}
# archaic / register markers (ASCII). McGuffey First is mostly modern-simple; this measures how
# archaic it actually is. quotative-inversion + verb-initial are the labeler's register weakness.
ARCHAIC_MARKERS = {
    "thee", "thou", "thy", "thine", "ye", "hast", "hath", "doth", "dost", "art",
    "unto", "o'er", "ere", "oft", "whilst", "aught", "naught", "methinks", "forsooth",
    "prithee", "cometh", "yonder", "nay", "lo", "shalt", "wilt", "twas", "tis",
    "mamma", "papa", "nurse", "bade", "hark", "yea",
}
QUOTATIVE_VERBS = {"said", "cried", "asked", "answered", "replied", "called", "sang",
                   "shouted", "whispered", "exclaimed"}

LESSON_RE = re.compile(r"^LESSON\s+[IVXLCDM]+\.?", re.IGNORECASE)
PAGE_MARKER_RE = re.compile(
    r"^(ECLECTIC|FIRST READER|MCGUFFEY|THE ALPHABET|SCRIPT|SUGGESTIONS|Preface|Copyright|"
    r"Produced by|Transcriber|EP\d+|N E W|R e v i s e d)", re.IGNORECASE)


def is_phonics_line(tokens):
    """A diacritic/phonics strip: >=3 tokens all length<=2 (single letters/digraphs)."""
    if len(tokens) < 3:
        return False
    return all(len(t.strip(".,'\"!?;:-()")) <= 2 for t in tokens)


def is_prose_line(raw):
    """Classify a raw line as a prose-contributing line (vs vocab strip / phonics / header / page)."""
    s = raw.strip()
    if not s:
        return False
    if LESSON_RE.match(s) or PAGE_MARKER_RE.match(s):
        return False
    if re.fullmatch(r"[\dIVXLCDM.\s]+", s):  # page numbers / roman numerals only
        return False
    if not re.search(r"[a-z]", s):  # no lowercase letter -> not running prose (all-caps header)
        return False
    toks = s.split()
    if is_phonics_line(toks):
        return False
    # real prose: ends with terminal punctuation OR is a multi-token wrap-continuation line.
    # vocab word-list lines are 1-3 bare tokens with no terminal punctuation.
    if s[-1] in ".?!":
        return True
    if len(toks) >= 4:
        return True
    return False


# sentence splitter: on terminal punctuation, keeping the terminator.
SENT_SPLIT_RE = re.compile(r"(?<=[.?!])\s+")


def parse_mcguffey(path):
    """Return list of lessons; each lesson = list of prose sentence strings (document order)."""
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    # find first LESSON to skip teacher front-matter
    start = 0
    for i, ln in enumerate(lines):
        if LESSON_RE.match(ln.strip()):
            start = i
            break
    lessons = []
    cur_prose = []  # accumulated prose lines for the current lesson

    def flush_lesson():
        if not cur_prose:
            return []
        buf = " ".join(cur_prose)
        buf = re.sub(r"\s+", " ", buf).strip()
        raw_sents = SENT_SPLIT_RE.split(buf)
        sents = []
        for rs in raw_sents:
            rs = rs.strip().strip('"').strip()
            # keep only genuine sentences: >=3 alpha tokens
            atoks = [t for t in rs.split() if re.search(r"[A-Za-z]", t)]
            if len(atoks) >= 3 and rs and rs[-1] in ".?!":
                sents.append(rs)
        return sents

    for i in range(start, len(lines)):
        ln = lines[i]
        if LESSON_RE.match(ln.strip()):
            s = flush_lesson()
            if s:
                lessons.append(s)
            cur_prose = []
            continue
        if is_prose_line(ln):
            cur_prose.append(ln.strip())
    s = flush_lesson()
    if s:
        lessons.append(s)
    return [L for L in lessons if L]


def ud_tokens_of(sentence):
    """Whitespace/punct tokenization matching how reader_pass expects a token list. We reuse the
    candidate_generator ud_tokenize by importing it lazily to keep tokenization consistent."""
    from hdlab.candidate_generator import ud_tokenize
    return ud_tokenize(sentence)


def reader_pass_text(text, tagger, parser, labeler):
    """reader_pass wants a sent dict with 'tokens'. Tokenize McGuffey text ourselves."""
    tokens = ud_tokens_of(text)
    return reader_pass({"tokens": tokens}, tagger, parser, labeler), tokens


def is_inverted(pos, tokens):
    """Register construction the labeler mislabels: verb-initial ('Here comes...','Come, Nat') or
    quotative inversion ('said James')."""
    # quotative inversion: a quotative verb immediately followed by a PROPN/PRON subject
    for k in range(len(tokens) - 1):
        if tokens[k].lower() in QUOTATIVE_VERBS and pos[k + 1] in ("PROPN", "PRON", "NOUN"):
            return True
    # verb-initial main clause (skip leading PUNCT / adverb 'Here'/'Now'/'There')
    j = 0
    while j < len(pos) and (pos[j] == "PUNCT" or tokens[j].lower() in ("here", "there", "now")):
        # 'Here comes X' is locative inversion -> register
        if tokens[j].lower() in ("here", "there") and j + 1 < len(pos) and pos[j + 1] == "VERB":
            return True
        j += 1
    if j < len(pos) and pos[j] == "VERB":
        return True
    return False


def run_census(mode):
    t0 = time.perf_counter()
    out_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    os.makedirs(out_dir, exist_ok=True)
    print(f"[{ANCHOR_NAME}:{mode}] START", flush=True)

    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    print(f"[{ANCHOR_NAME}:{mode}] front-end loaded", flush=True)

    lessons = parse_mcguffey(MCG_TXT)
    if mode == "smoke":
        lessons = lessons[:8]
    n_lessons = len(lessons)
    n_sent = sum(len(L) for L in lessons)
    print(f"[{ANCHOR_NAME}:{mode}] parsed McGuffey: {n_lessons} lessons, {n_sent} prose sentences", flush=True)

    # ---------- calibration on UD-EWT: tau_abstain (16th pct base-pick margin) + flag_rate ----------
    ud_docs = load_ud_docs(UD_TEST)
    ud_docs = [d for d in ud_docs if len(d) >= 2]
    ud_docs = ud_docs[:(20 if mode == "smoke" else 80)]
    ud_cache = {}
    for di, doc in enumerate(ud_docs):
        for si, sent in enumerate(doc):
            ud_cache[(di, si)] = reader_pass(sent, tagger, parser, labeler)
    ud_margins = []
    for (di, si), rp in ud_cache.items():
        for v, pool in rp["pools"].items():
            bp = base_pick(pool)
            if bp is not None:
                ud_margins.append(bp["margin"])
    tau_abstain = float(np.percentile(ud_margins, 16)) if ud_margins else 0.0
    ud_true = build_scored(ud_docs, ud_cache, "true")
    ud_coh = coherence_stats(ud_true)
    ud_flag_rate = ud_coh["flag_rate"]
    ud_lift = ud_coh["flag_error_lift_ratio"]
    print(f"[{ANCHOR_NAME}:{mode}] UD calib: tau_abstain(16pct)={tau_abstain:.4f} "
          f"n_ud_margins={len(ud_margins)} ud_flag_rate={ud_flag_rate} ud_lift={ud_lift}", flush=True)

    # ---------- McGuffey pass (per-lesson overlay, document order) ----------
    sent_lens = []
    n_cross_ref_sents = 0
    n_sents_with_pron = 0
    instances = []  # per verb with a non-empty predicted patient pool
    n_verbs_total = 0
    n_verbs_no_patient = 0

    for L in lessons:
        overlay = WorkingOverlay()
        for si, text in enumerate(L):
            rp, tokens = reader_pass_text(text, tagger, parser, labeler)
            pos = rp["pos"]
            sent_lens.append(len(tokens))

            # cross-sentence referential: any in-scope pronoun that binds to a PRIOR-sentence entity
            sent_has_pron = False
            sent_cross_ref = False
            for k in range(len(tokens)):
                low = tokens[k].lower().strip(".,'\"!?;:")
                if pos[k] == "PRON" and low in PRONOUN_SCOPE:
                    sent_has_pron = True
                    try:
                        ent = overlay.resolve_pronoun(low, strategy="maintained")
                    except ValueError:
                        ent = None
                    if ent is not None:
                        sent_cross_ref = True
            if sent_has_pron:
                n_sents_with_pron += 1
            if sent_cross_ref:
                n_cross_ref_sents += 1

            inverted = is_inverted(pos, tokens)
            archaic_marker = any(tokens[k].lower().strip(".,'\"!?;:") in ARCHAIC_MARKERS
                                 for k in range(len(tokens)))

            # who-affected decisions: per verb, base pick over predicted patient pool
            # count all VERBs (incl. those with no patient candidate = intransitive/copular)
            n_verbs_in_sent = sum(1 for p in pos if p == "VERB")
            n_verbs_total += n_verbs_in_sent
            pooled_verbs = set(rp["pools"].keys())
            n_verbs_no_patient += max(0, n_verbs_in_sent - len(pooled_verbs))

            for v, pool in rp["pools"].items():
                bp = base_pick(pool)
                if bp is None:
                    continue
                sp = salient_pick(pool, overlay)  # overlay holds PRIOR sentences only
                disagreement = bool(sp is not None and sp["aidx"] != bp["aidx"])
                # is the base or salient pick a pronoun / does the pool involve cross-sentence ref?
                base_is_pron = bp["pos"] == "PRON"
                pool_has_pron = any(c["pos"] == "PRON" for c in pool)
                # discourse-driven uncertainty: pick is a pronoun, OR disagreement where salient
                # resolves to a prior entity
                salient_resolves = False
                if disagreement and sp is not None and sp["pos"] == "PRON" and sp["surf"] in PRONOUN_SCOPE:
                    try:
                        salient_resolves = overlay.resolve_pronoun(sp["surf"], strategy="maintained") is not None
                    except ValueError:
                        salient_resolves = False
                discourse_driven = bool(base_is_pron or pool_has_pron or salient_resolves)
                register_driven = bool(inverted or archaic_marker)

                low_margin = bool(bp["margin"] < tau_abstain)
                escalate = bool(low_margin or disagreement)
                instances.append({
                    "margin": bp["margin"], "low_margin": low_margin, "disagreement": disagreement,
                    "escalate": escalate, "discourse_driven": discourse_driven,
                    "register_driven": register_driven, "base_is_pron": base_is_pron,
                    "n_cands": len(pool),
                })

            observe_sentence(overlay, tokens, pos)  # advance state AFTER scoring (leak-clean)

    # ---------- aggregate ----------
    n_inst = len(instances)
    n_escalate = sum(1 for i in instances if i["escalate"])
    n_low_margin = sum(1 for i in instances if i["low_margin"])
    n_disagree = sum(1 for i in instances if i["disagreement"])
    mcg_flag_rate = round(n_disagree / n_inst, 4) if n_inst else None
    escalation_rate = round(n_escalate / n_inst, 4) if n_inst else None
    low_margin_rate = round(n_low_margin / n_inst, 4) if n_inst else None

    # register-vs-discourse split OF THE UNCERTAIN (escalated) cases
    unc = [i for i in instances if i["escalate"]]
    n_unc = len(unc)
    n_reg = sum(1 for i in unc if i["register_driven"] and not i["discourse_driven"])
    n_disc = sum(1 for i in unc if i["discourse_driven"] and not i["register_driven"])
    n_both = sum(1 for i in unc if i["discourse_driven"] and i["register_driven"])
    n_other = n_unc - n_reg - n_disc - n_both
    # register share (register-attributable = register-only + half of both, conservatively assign both to both)
    register_share = round((n_reg + n_both) / n_unc, 4) if n_unc else None
    discourse_share = round((n_disc + n_both) / n_unc, 4) if n_unc else None
    register_only_share = round(n_reg / n_unc, 4) if n_unc else None

    cross_ref_rate = round(n_cross_ref_sents / n_sent, 4) if n_sent else None

    # ---------- verdict ----------
    if cross_ref_rate is not None and cross_ref_rate < 0.05:
        verdict = "TOO_SIMPLE"
    elif register_share is not None and register_share >= 0.60:
        verdict = "CONFOUNDED_ARCHAIC"
    elif (cross_ref_rate is not None and cross_ref_rate >= 0.08
          and register_share is not None and register_share < 0.50
          and escalation_rate is not None and 0.05 <= escalation_rate <= 0.60):
        verdict = "GOOD_TARGET"
    else:
        verdict = "MIXED"

    elapsed = round(time.perf_counter() - t0, 2)
    mean_len = round(float(np.mean(sent_lens)), 2) if sent_lens else None
    verdict_msg = (
        f"[{verdict}] n_lessons={n_lessons} n_sent={n_sent} mean_sent_len={mean_len} "
        f"n_whoaffected_decisions={n_inst} (verbs_total={n_verbs_total} verbs_no_patient={n_verbs_no_patient}) "
        f"| cross_sent_ref_rate={cross_ref_rate} (sents_with_pron={n_sents_with_pron}) "
        f"| escalation_rate={escalation_rate} (low_margin={low_margin_rate} contradiction_flag={mcg_flag_rate}) "
        f"| uncertain_split: register={register_share} discourse={discourse_share} register_only={register_only_share} "
        f"(n_unc={n_unc} reg_only={n_reg} disc_only={n_disc} both={n_both} other={n_other}) "
        f"| CONTRADICTION_FLAG mcg_rate={mcg_flag_rate} vs ud_rate={ud_flag_rate} (ud_lift={ud_lift}) "
        f"| tau_abstain={round(tau_abstain,4)}(UD16pct)"
    )

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict,
        "elapsed_s": elapsed, "run_mode": mode, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "note": "RECONNAISSANCE/CENSUS -- reader BEHAVIOR + text STRUCTURE, NO gold who-affected; "
                "escalation = reader's OWN confidence signals (arc-parser margin + contradiction flag), "
                "NOT verified correctness.",
        "structure": {
            "n_lessons": n_lessons, "n_prose_sentences": n_sent, "mean_sent_len_tokens": mean_len,
            "median_sent_len_tokens": float(np.median(sent_lens)) if sent_lens else None,
            "n_sents_with_pronoun": n_sents_with_pron,
            "n_cross_sentence_referential_sents": n_cross_ref_sents,
            "cross_sentence_referential_rate": cross_ref_rate,
        },
        "escalation": {
            "n_whoaffected_decisions": n_inst, "n_verbs_total": n_verbs_total,
            "n_verbs_no_patient_candidate": n_verbs_no_patient,
            "escalation_rate": escalation_rate, "low_margin_rate": low_margin_rate,
            "contradiction_flag_rate": mcg_flag_rate,
            "n_escalate": n_escalate, "n_low_margin": n_low_margin, "n_contradiction_flag": n_disagree,
            "tau_abstain_ud16pct": round(tau_abstain, 4),
        },
        "uncertain_split": {
            "n_uncertain": n_unc, "register_only": n_reg, "discourse_only": n_disc,
            "both": n_both, "other_parse": n_other,
            "register_share": register_share, "discourse_share": discourse_share,
            "register_only_share": register_only_share,
        },
        "contradiction_flag_comparability": {
            "mcguffey_flag_rate": mcg_flag_rate, "ud_ewt_flag_rate": ud_flag_rate,
            "ud_ewt_flag_error_lift_ratio": ud_lift,
            "note": "UD lift = P(isolated wrong|flag)/P(wrong|noflag) MEASURED with UD gold; McGuffey has "
                    "no gold so only flag_rate is comparable, not lift.",
        },
        "calibration": {"ud_subset_docs": len(ud_docs), "n_ud_base_margins": len(ud_margins),
                        "tau_abstain_percentile": 16},
    }
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print(f"[{ANCHOR_NAME}:{mode}] DONE {verdict} elapsed={elapsed}s", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] {verdict_msg}", flush=True)
    return metrics


def self_test():
    print("[self_test] start", flush=True)
    # prose/vocab line classifier
    assert is_prose_line("The fat hen is on the box.")
    assert is_prose_line("has it on his head, and he is a big man.")  # wrap continuation, >=4 tok
    assert not is_prose_line("LESSON XXI.")
    assert not is_prose_line("FIRST READER. ")
    assert not is_prose_line("a    o    n   d   g    r    th")  # phonics
    assert not is_prose_line("dog   ")     # vocab single token
    assert not is_prose_line("big rat")    # vocab 2 tokens no terminal
    assert not is_prose_line("27")         # page number
    # inversion detector
    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    rp, toks = reader_pass_text('"Not now James" said Kate.', tagger, parser, labeler)
    assert is_inverted(rp["pos"], toks), "quotative inversion 'said Kate' must flag register"
    rp2, toks2 = reader_pass_text("The dog ran to the box.", tagger, parser, labeler)
    # canonical SVO should NOT be flagged inverted
    assert not is_inverted(rp2["pos"], toks2), "canonical SVO must not flag as inverted"
    # parse a couple of real McGuffey lines end-to-end
    rp3, toks3 = reader_pass_text("Ned has fed the hen.", tagger, parser, labeler)
    assert len(rp3["pools"]) >= 0  # runs without error
    print("[self_test] line-classifier OK; inversion OK; reader_pass on McGuffey text OK", flush=True)
    print("[self_test] PASS", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_census("smoke"); return
    if args.full:
        run_census("full"); return
    self_test()


if __name__ == "__main__":
    out_dir_crash = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        os.makedirs(out_dir_crash, exist_ok=True)
        with open(os.path.join(out_dir_crash, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump({"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                       "traceback": traceback.format_exc()[:4000]}, f, indent=2)
        raise
