"""Phase A2 -- how MATERIAL is the archaic subject confound? Measure the INCIDENCE of the constructions
that break spaCy (Phase A: subject-verb INVERSION + archaic MORPHOLOGY) in the actual LitBank reading
corpus, and spaCy's real error rate on them. Together with the Phase A finding (natural archaic prose is
NOT harder than modern for spaCy), this sizes the confound at the CORPUS level.

The gold here is DEFINITIONAL, so no annotation is needed: a nominative pronoun (he/she/they/I/we)
immediately following a reporting verb (said/replied/cried/...) IS that verb's grammatical subject
("said he" = he is subject). If spaCy does not tag it nsubj, that is a real subject error, in situ.

Also reports: the pronoun-subject FRACTION overall (pronoun subjects are easy -> explains why natural
archaic prose scores high), and archaic-morphology token incidence (thou/hath/-est ...).

spaCy LOCAL only. Deterministic. ASCII-only. Diagnostic (reports rates; no HARD_PASS gate).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time
from datetime import datetime, timezone

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

ANCHOR = "role_confound_incidence_litbank_v1"
REPORT_VERBS = {"say", "said", "reply", "replied", "cry", "cried", "ask", "asked", "answer", "answered",
                "exclaim", "exclaimed", "mutter", "muttered", "murmur", "murmured", "whisper", "whispered",
                "observe", "observed", "remark", "remarked", "rejoin", "rejoined", "continue", "continued",
                "add", "added", "return", "returned", "resume", "resumed", "quoth", "declare", "declared",
                "think", "thought", "call", "called", "shout", "shouted", "groan", "groaned"}
NOM_PRON = {"he", "she", "they", "i", "we"}          # unambiguous nominative (excludes ambiguous you/it)
ARCHAIC_MORPH = {"thou", "thee", "thy", "thine", "hath", "dost", "doth", "art", "wilt", "shalt", "hast",
                 "canst", "wouldst", "couldst", "shouldst", "knowest", "sayest", "quoth", "ye", "'tis", "ere",
                 "whilst", "betwixt", "unto", "nay", "yea"}
SUBJ_DEPS = {"nsubj", "nsubjpass"}


def _load_spacy():
    import spacy
    return spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR); os.makedirs(d, exist_ok=True); return d


def _atomic_write(m):
    d = _out_dir(); tmp = os.path.join(d, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    os.replace(tmp, os.path.join(d, "metrics.json"))


def main(max_files=40, max_sents_per_file=1200):
    from hdlab.scene_segment import parse_conll_sentences
    nlp = _load_spacy()
    files = sorted(glob.glob(os.path.join(_REPO, "data", "corpora", "litbank_coref_conll", "*.conll")))[:max_files]

    t0 = time.perf_counter()
    n_sents = n_clauses = 0
    n_subj_total = n_subj_pron = 0
    inv_pron_n = inv_pron_err = 0                # reporting-verb + nominative pronoun inversion
    inv_npro_n = inv_npro_err = 0                # reporting-verb + full-NP inversion (approx)
    morph_tokens = 0
    morph_sents = 0
    err_examples, morph_examples = [], []

    for fp in files:
        try:
            sents = parse_conll_sentences(fp)
        except Exception:
            continue
        for toks in sents[:max_sents_per_file]:
            if len(toks) < 3:
                continue
            text = " ".join(toks)
            low = [t.lower() for t in toks]
            n_sents += 1
            has_morph = any(w in ARCHAIC_MORPH for w in low)
            if has_morph:
                morph_sents += 1
                mt = [w for w in low if w in ARCHAIC_MORPH]
                morph_tokens += len(mt)
                if len(morph_examples) < 15:
                    morph_examples.append({"text": text[:120], "morph": mt})
            doc = nlp(text)
            for t in doc:
                if t.pos_ in ("VERB", "AUX"):
                    n_clauses += 1
                # subject inventory
                if t.dep_ in SUBJ_DEPS:
                    n_subj_total += 1
                    if t.pos_ == "PRON":
                        n_subj_pron += 1
                # inversion: reporting verb followed by nominative pronoun / NP
                if (t.lemma_.lower() in REPORT_VERBS or t.text.lower() in REPORT_VERBS) and t.i + 1 < len(doc):
                    nxt = doc[t.i + 1]
                    if nxt.text.lower() in NOM_PRON:
                        inv_pron_n += 1
                        ok = (nxt.dep_ in SUBJ_DEPS and nxt.head.i == t.i)
                        if not ok:
                            inv_pron_err += 1
                            if len(err_examples) < 20:
                                err_examples.append({"text": text[:120], "verb": t.text, "pron": nxt.text,
                                                     "spacy_dep": nxt.dep_, "spacy_head": nxt.head.text})
                    elif nxt.pos_ in ("DET", "PROPN", "NOUN") and nxt.text.lower() not in ("that", "the"):
                        # a following bare NP head is a plausible inverted subject (approx)
                        head_np = nxt
                        for k in range(t.i + 1, min(t.i + 4, len(doc))):
                            if doc[k].pos_ in ("NOUN", "PROPN"):
                                head_np = doc[k]; break
                        if head_np.pos_ in ("NOUN", "PROPN"):
                            inv_npro_n += 1
                            ok = (head_np.dep_ in SUBJ_DEPS and head_np.head.i == t.i)
                            if not ok:
                                inv_npro_err += 1

    elapsed = time.perf_counter() - t0
    rate = lambda a, b: round(a / b, 4) if b else 0.0
    metrics = {
        "verdict": "MEASURED", "anchor_name": ANCHOR,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "elapsed_s": round(elapsed, 1),
        "n_files": len(files), "n_sents": n_sents, "n_finite_verbs": n_clauses,
        "n_subjects_total": n_subj_total, "n_subjects_pronoun": n_subj_pron,
        "pronoun_subject_fraction": rate(n_subj_pron, n_subj_total),
        "inversion_pronoun": {"n": inv_pron_n, "n_per_1000_verbs": rate(inv_pron_n, n_clauses) * 1000,
                              "spacy_error_rate": rate(inv_pron_err, inv_pron_n), "n_errors": inv_pron_err,
                              "errors_per_1000_verbs": rate(inv_pron_err, n_clauses) * 1000},
        "inversion_full_np_approx": {"n": inv_npro_n, "spacy_error_rate": rate(inv_npro_err, inv_npro_n),
                                     "n_errors": inv_npro_err, "note": "approx detector; upper-noisy"},
        "archaic_morphology": {"n_sents_with_morph": morph_sents, "frac_sents": rate(morph_sents, n_sents),
                               "n_morph_tokens": morph_tokens, "examples": morph_examples[:10]},
        "inversion_error_examples": err_examples,
        "interpretation": ("pronoun_subject_fraction high => most subjects are easy pronouns (why natural "
                           "archaic scores high). inversion_pronoun.spacy_error_rate = spaCy's real in-situ "
                           "subject error on dialogue-tag inversion; errors_per_1000_verbs = the corpus-level "
                           "subject-error contribution of THIS construction."),
    }
    _atomic_write(metrics)
    ip = metrics["inversion_pronoun"]
    print(f"[LitBank {n_sents} sents, {n_clauses} finite verbs] pronoun_subj_frac={metrics['pronoun_subject_fraction']}")
    print(f"[dialogue-tag inversion 'said he'] n={ip['n']} ({ip['n_per_1000_verbs']:.1f}/1000 verbs) "
          f"spaCy_error_rate={ip['spacy_error_rate']} -> {ip['errors_per_1000_verbs']:.1f} subj-errors/1000 verbs")
    print(f"[full-NP inversion approx] n={metrics['inversion_full_np_approx']['n']} "
          f"err={metrics['inversion_full_np_approx']['spacy_error_rate']}")
    print(f"[archaic morphology] {metrics['archaic_morphology']['frac_sents']*100:.2f}% of sents "
          f"({morph_tokens} tokens)")
    print(f"-> {os.path.join(_out_dir(), 'metrics.json')} ({elapsed:.0f}s)")
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        nlp = _load_spacy()
        doc = nlp("Said he to the crowd.")
        he = [t for t in doc if t.text == "he"][0]
        print(f"[self-test] 'Said he' -> he.dep_={he.dep_} head={he.head.text}")
        sys.exit(0)
    smoke = args.smoke or args.mode == "smoke"
    try:
        main(max_files=(3 if smoke else 40), max_sents_per_file=(200 if smoke else 1200))
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        _atomic_write({"verdict": "CELL_CRASHED", "error": f"{type(e).__name__}: {e}",
                       "traceback": traceback.format_exc()[:4000]})
        raise
