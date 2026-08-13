"""experiments/exp_grounding_text_vs_mechanism.py

IS THE BINDING CONSTRAINT ON GROUNDED_MEANING THE TEXT, OR THE MECHANISM?

Tonight's blind hand-score (notes/director_handscore_readout_v1_2026-08-13.md) was
3 MEANINGFUL / 19 RELATED / 78 NOISE over 100 rows, with OpenStax-Biology rows far ahead of
OneStopEnglish news rows (52.9% vs 16.0% meaningful-or-related, Fisher p=0.0024) -- but 8 of
those 9 bio hits were RELATED, not MEANINGFUL.

  (A) TEXT HYPOTHESIS      news mentions, textbooks explain -> remedy: read textbooks
  (B) MECHANISM HYPOTHESIS the read-out is a co-occurrence proxy; better text buys TOPICAL
                           ADJACENCY, never MEANING -> remedy: architectural

ONE VARIABLE: THE CORPUS.
  arm NEWS      OneStopEnglish only          (Ele + Int + Adv, 189 files each)
  arm TEXTBOOK  OpenStax only                (biology_2e, anatomy_physiology_2e, psychology_2e,
                                              microbiology, chemistry_2e; line-aware split)
Matched sentence count, same seed, same reading-order policy, same read-out configuration
(the CURRENT DEFAULT: readout=None, freeze_episode=False -- F1+F3 OFF and NOT varied).

THIS CELL CLAIMS NO QUALITY BAND. It writes the blind material for the Director's hand-score
and ONE machine-computed control that can support (B) on its own:

  THE CO-OCCURRENCE CONTROL. For every blind row, what would a plain sentence-window
  co-occurrence baseline (top-PMI / most-frequent co-occurring content word) have predicted for
  that subject, over THAT ARM'S OWN read corpus? Sealed in cooccurrence_control.json, never
  printed in the scoring sheet. If the substrate's output largely REPRODUCES the baseline,
  hypothesis (B) is supported regardless of the hand-score -- the result reproduced from the
  WRONG SOURCE.

Pre-reg: preregs/2026-08-13_grounding_text_vs_mechanism.md
  sec 3  PRIMARY bands (scored LATER by the Director, NOT here):
         TEXT_HYPOTHESIS_SUPPORTED  MEANINGFUL(TEXTBOOK) >= 0.20
         MIXED                      MEANINGFUL(TEXTBOOK) in [0.10, 0.20)
         MECHANISM_IS_BINDING       MEANINGFUL(TEXTBOOK) < 0.10 AND RELATED >= NEWS + 0.10
         NULL_NO_TEXT_EFFECT        MEANINGFUL < 0.10 and RELATED not above NEWS by 0.10
  sec 4  CO-OCCURRENCE CONTROL bands (reported, not gating)
  sec 5  STRUCTURAL gates S1..S6 (this cell's own, machine-checked)
  sec 6  DECLARED LIMITATION: the blind is LABEL-blind but GENRE-VISIBLE.

GROWTH IS PAUSED: writes are confined to data/exp_grounding_text_vs_mechanism/. No canonical
foundation path is written. Nothing is banked. The cell never calls git.

# CELL-TEMPLATE MANDATORY:
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException); no bare except
# - start_marker_written / crash_diagnostic_present / per-chunk progress flush / heartbeat
# - cardinality_ok: EXPECTED_N_UNITS = 22 (2 arm_done + 2 arms x 10 decile ledger units)
# - crlb n/a: the primary discriminator is a human-bucketed proportion; the binding limit is
#   BINOMIAL (SE 0.057 at n=50, p~0.2) and is stated in the pre-reg
# - arms-must-differ: S3, sha256 over each arm's sorted (subject, object) set
# - real_code_path: drives the REAL ReadingLoopState / process_sentence / checkpoint /
#   HDFactStore / make_pbv_fns objects; no synthetic-only branch
# - all numbers in comments are tagged MEASURED@ / CITED@

ASCII-only. Deterministic (fixed seeds; sorted(set(...)) throughout; no built-in hash()).
"""
from __future__ import annotations

import os

# MUST precede numpy import (PROT: split-nondeterminism / BLAS thread nondeterminism)
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import glob
import hashlib
import json
import math
import platform
import random
import re
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.closed_class_lexicon import is_closed_class
from hdlab.hd_fact_store import HDFactStore
from hdlab.reading_grounding_loop import (
    KNOWN_RELATION,
    MEANING_RELATION,
    PBV_COMMIT_STRENGTH,
    ReadingLoopState,
    checkpoint,
    make_pbv_fns,
    process_sentence,
    seed_known_words,
)
from hdlab.thematic_role_labeler import lemma_word
from tools import exp_checkpoint

from experiments.exp_reading_grounding_loop_cycle1_v1 import (
    N_DIM, SCHEMA_THRESH_FULL, load_base_vocab_seed, repo_path,
)
from experiments.exp_reading_grounding_loop_cycle2_v1 import (
    CHUNK_SIZE, grounded_lemmas_in_store,
)
from experiments.exp_definitional_grounding_v5 import _clean_sentences

ANCHOR_NAME = "grounding_text_vs_mechanism"
PREREG = "preregs/2026-08-13_grounding_text_vs_mechanism.md"

ARMS = ["NEWS", "TEXTBOOK"]
N_DECILE_UNITS = 10
EXPECTED_N_UNITS = len(ARMS) * (1 + N_DECILE_UNITS)     # S1 = 22

# ONE VARIABLE: both arms get the IDENTICAL store seed, the IDENTICAL base-vocabulary seed and
# the IDENTICAL (current-default) read-out. Only the sentences differ.
ARM_SEED = 4201
SAMPLE_SEED = 42
SAMPLE_N = 50
BLIND_SHUFFLE_SEED = 42
SUBSAMPLE_SEED = 42
BLOCK_SIZE = CHUNK_SIZE                  # 150; a sampled block never straddles a chunk boundary

TOK = re.compile(r"[A-Za-z][A-Za-z'-]*")

ONESTOP_LEVELS = ["Ele-Txt", "Int-Txt", "Adv-Txt"]
TEXTBOOKS = ["biology_2e", "anatomy_physiology_2e", "psychology_2e", "microbiology",
             "chemistry_2e"]

SMOKE_BLOCKS_PER_ARM = 8                 # smoke only; FULL uses the matched N

S5_YIELD_FLOOR = 50                      # each arm must bank >= 50 GROUNDED_MEANING facts
COOC_MIN_PAIR_COUNT = 3                  # PMI on singleton co-occurrences is noise
COOC_TOPK = 5

# --- pre-registered bands, RECORDED so the later hand-score is judged against the registration
QUALITY_BANDS_RECORDED = {
    "primary_statistic": "MEANINGFUL rate on the TEXTBOOK arm (Director blind hand-score, "
                         "n=50/arm)",
    "TEXT_HYPOTHESIS_SUPPORTED": "MEANINGFUL(TEXTBOOK) >= 0.20",
    "MIXED": "MEANINGFUL(TEXTBOOK) in [0.10, 0.20)",
    "MECHANISM_IS_BINDING": "MEANINGFUL(TEXTBOOK) < 0.10 AND RELATED(TEXTBOOK) >= "
                            "RELATED(NEWS) + 0.10 -- pre-declared, expected, acceptable",
    "NULL_NO_TEXT_EFFECT": "MEANINGFUL(TEXTBOOK) < 0.10 and RELATED not above NEWS by 0.10",
    "secondary_reported_not_gated": "RELATED rate per arm and the MEANINGFUL:RELATED ratio per "
                                    "arm; under (A) the ratio shifts toward MEANINGFUL, under "
                                    "(B) it stays adjacency-dominated",
    "power": "SE of a proportion at n=50, p~0.2 is 0.057; differences below ~0.10 are "
             "unresolvable",
    "reference_point": "MEASURED@notes/director_handscore_readout_v1_2026-08-13.md -- "
                       "3 MEANINGFUL / 19 RELATED / 78 NOISE over 100 mixed-corpus rows",
}
COOC_BANDS_RECORDED = {
    "COOC_REPRODUCES_supports_B": "either_top1 >= 0.50 OR top5_containment >= 0.70, AND >= 0.20 "
                                  "above the permutation floor",
    "COOC_PARTIAL": "either_top1 in [0.20, 0.50) or top5_containment in [0.40, 0.70), above the "
                    "floor",
    "COOC_DOES_NOT_EXPLAIN": "either_top1 < 0.20 and top5_containment < 0.40 -- the substrate "
                             "output is NOT reproducible from plain co-occurrence; weakens (B)",
    "note": "reported per arm; does NOT gate the primary. If the substrate largely REPRODUCES "
            "the baseline, (B) is supported regardless of the hand-score.",
}


# =========================================================================== io helpers
def _output_dir(run_mode: str) -> str:
    return repo_path(f"data/exp_{ANCHOR_NAME}" + ("_smoke" if run_mode == "smoke" else ""))


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def _write_start_marker(output_dir: str, run_mode: str, arm: Optional[str]) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "arm": arm,
              "expected_n_units": EXPECTED_N_UNITS, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    _atomic_json(os.path.join(output_dir, "_start_marker.json"), marker)


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    _atomic_json(os.path.join(output_dir, "metrics.json"), {
        "verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:400]),
        "summary": "CELL_CRASHED", "elapsed_s": 0.0, "anchor_name": ANCHOR_NAME,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat()})


def _heartbeat(output_dir: str, payload: dict) -> None:
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(payload, ts_iso=datetime.now(timezone.utc).isoformat())) + "\n")


def _digest_pairs(pairs) -> str:
    """sha256 over an arm's sorted (subject, object) set -- S3 arms-must-differ."""
    h = hashlib.sha256()
    for s, o in sorted(set(pairs)):
        h.update(("%s\x1f%s\x1e" % (s, o)).encode("utf-8"))
    return h.hexdigest()


# =========================================================================== corpora
def load_news_pool() -> List[str]:
    """OneStopEnglish, ALL three reading levels, ALL 189 files each, file-sorted (deterministic).

    MEASURED 2026-08-13: Ele 6176 + Int 6810 + Adv 7408 = 20394 sentences. The three levels are
    the SAME 189 articles rewritten at three reading levels, so the pool carries built-in
    paraphrase repetition; that is a property of OneStopEnglish, it is disclosed in the pre-reg
    sec 8, and it was equally true of the corpus tonight's hand-score was drawn from.
    """
    out: List[str] = []
    for level in ONESTOP_LEVELS:
        d = repo_path(f"data/corpora/onestop/Texts-SeparatedByReadingLevel/{level}")
        for fp in sorted(glob.glob(os.path.join(d, "*.txt"))):
            with open(fp, encoding="utf-8-sig", errors="ignore") as fh:
                text = fh.read()
            out.extend(_clean_sentences(text))
    return out


def load_textbook_pool() -> List[str]:
    """The five cleaned OpenStax books, book-order fixed, sentence split PER LINE.

    Per-line splitting is v5's F9 fix: the cleaned files hold one glossary entry / one paragraph
    per LINE, and joining lines before splitting produces run-on pseudo-sentences in which term
    boundaries are unrecoverable (that bug is what the v5 term-boundary repair addressed). A line
    boundary in a markdown-stripped file is a paragraph boundary, so splitting there cannot merge
    two halves of one real sentence.

    MEASURED 2026-08-13 with this loader: bio 30498 + a&p 27352 + psych 30378 + micro 27251 +
    chem 21550 = 137029 sentences. (STATUS.md quotes 117642 for these five books; that figure
    comes from the per-book density_report.json splitter, a DIFFERENT sentence splitter. Both
    numbers are on disk; this cell reports the one it actually read.)
    """
    out: List[str] = []
    for label in TEXTBOOKS:
        path = repo_path(f"data/corpora/textbook_{label}/cleaned/{label}.clean.txt")
        with open(path, encoding="utf-8") as f:
            for ln in f:
                s = ln.strip()
                if not s or s.startswith("#"):
                    continue
                s = re.sub(r"^[-*]\s+", "", s)
                s = re.sub(r"^\d+\.\s+", "", s)
                out.extend(_clean_sentences(s))
    return out


def block_subsample(pool: Sequence[str], target_n: int, seed: int) -> List[str]:
    """Contiguous 150-sentence blocks, uniformly selected without replacement, ORIGINAL ORDER
    restored, truncated to exactly `target_n`.

    The SAME function runs in both arms (pre-reg sec 2). For an arm whose pool already equals the
    target it selects every block and is a no-op. Block (not per-sentence) sampling preserves the
    local discourse contiguity the read-out depends on, and spreads the sample over the whole of
    every book instead of the front matter.
    """
    if target_n >= len(pool):
        return list(pool)
    n_blocks = math.ceil(len(pool) / BLOCK_SIZE)
    need = math.ceil(target_n / BLOCK_SIZE)
    picked = sorted(random.Random(seed).sample(range(n_blocks), need))
    out: List[str] = []
    for b in picked:
        out.extend(pool[b * BLOCK_SIZE:(b + 1) * BLOCK_SIZE])
    return out[:target_n]


def build_streams(run_mode: str) -> Dict[str, List[str]]:
    """Both arms' final sentence lists. Matched N = min(|NEWS|, |TEXTBOOK|)."""
    news = load_news_pool()
    book = load_textbook_pool()
    target = min(len(news), len(book))
    if run_mode == "smoke":
        target = SMOKE_BLOCKS_PER_ARM * BLOCK_SIZE
    return {"NEWS": block_subsample(news, target, SUBSAMPLE_SEED),
            "TEXTBOOK": block_subsample(book, target, SUBSAMPLE_SEED)}


# =========================================================================== one arm
def run_arm(arm: str, stream: List[str], output_dir: str) -> dict:
    already = exp_checkpoint.completed_units(output_dir)
    done_key = exp_checkpoint.unit_key("arm_done", arm)
    if done_key in already:
        return dict(exp_checkpoint.load_units(output_dir)[done_key], skipped=True)

    store = HDFactStore(n_dim=N_DIM, seed=ARM_SEED,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                              MEANING_RELATION: "FUNCTIONAL"},
                        use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, load_base_vocab_seed(), source="seed_base_vocabulary")
    known_seed_snapshot = set(state.known_seed)

    # THE READ-OUT IS THE CURRENT DEFAULT IN BOTH ARMS (F1+F3 OFF). Not a variable here.
    propose_fn, verify_fn = make_pbv_fns(state)
    pbv_fns = (propose_fn, verify_fn)

    n_chunks = math.ceil(len(stream) / CHUNK_SIZE) if stream else 0
    t0 = time.time()
    last_hb = t0
    deciles_written = set()

    for chunk_idx in range(n_chunks):
        chunk = stream[chunk_idx * CHUNK_SIZE:(chunk_idx + 1) * CHUNK_SIZE]
        for i, sent in enumerate(chunk):
            process_sentence(state, sent, f"{arm}_{chunk_idx}_{i}", pass_idx=chunk_idx,
                             pbv_fns=pbv_fns, revive_terminal=True)
        checkpoint(state, pass_idx=chunk_idx, source_tag=arm,
                   schema_thresh=SCHEMA_THRESH_FULL, pbv=True,
                   commit_strength=PBV_COMMIT_STRENGTH)

        # decile progress ledger (S1 cardinality); resume granularity is ARM-level by design
        dec = min(N_DECILE_UNITS - 1, (chunk_idx * N_DECILE_UNITS) // max(1, n_chunks))
        if dec not in deciles_written:
            deciles_written.add(dec)
            key = exp_checkpoint.unit_key(arm, "decile%d" % dec)
            if key not in already:
                exp_checkpoint.record_unit(output_dir, key, {
                    "arm": arm, "decile": dec, "first_chunk_idx": chunk_idx,
                    "n_grounded_at_open": len(grounded_lemmas_in_store(state.store))})
        if chunk_idx % 10 == 0 or chunk_idx == n_chunks - 1:
            print(f"[progress] {arm} chunk={chunk_idx + 1}/{n_chunks} "
                  f"grounded={len(grounded_lemmas_in_store(state.store))} "
                  f"refused={len(state.refusals)} elapsed={time.time() - t0:.1f}s", flush=True)
        if time.time() - last_hb >= 30.0:
            last_hb = time.time()
            _heartbeat(output_dir, {"arm": arm, "chunk": chunk_idx, "n_chunks": n_chunks,
                                    "elapsed_s": round(time.time() - t0, 1)})

    gm = [f for f in state.store.live_facts() if f.relation == MEANING_RELATION]
    grounded = grounded_lemmas_in_store(state.store)
    summary = {
        "arm": arm,
        "corpus": "OneStopEnglish (Ele+Int+Adv)" if arm == "NEWS" else
                  "OpenStax (" + ", ".join(TEXTBOOKS) + ")",
        "readout": None, "freeze_episode": False,
        "n_sentences": len(stream), "n_chunks": n_chunks,
        "n_grounded": len(grounded),
        "n_meaning_facts": len(gm),
        "n_tautology_facts": sum(1 for f in gm if f.subject == f.obj),
        "n_closed_class_object_facts": sum(1 for f in gm if is_closed_class(f.obj)),
        "no_leak_violations": sorted(set(l for l in grounded if l in known_seed_snapshot)),
        "n_refusals": len(state.refusals),
        "refusal_reasons": _count_reasons(state.refusals),
        "pairs_digest": _digest_pairs((f.subject, f.obj) for f in gm),
        "elapsed_s": round(time.time() - t0, 2),
    }
    _atomic_json(os.path.join(output_dir, f"arm_{arm}_provenance.json"),
                 [_prov_row(p) for p in state.provenance if p["relation"] == MEANING_RELATION])
    # the exact sentence list the arm read -- the co-occurrence control must be computed over
    # THIS, not over the full pool
    _atomic_json(os.path.join(output_dir, f"arm_{arm}_stream.json"),
                 {"arm": arm, "n_sentences": len(stream), "sentences": stream})
    exp_checkpoint.record_unit(output_dir, done_key, summary)
    return summary


def _prov_row(p: dict) -> dict:
    return {k: p.get(k) for k in ("fid", "subject", "relation", "object", "segment", "pass_idx",
                                  "best_cos", "n_exposures", "schema_score", "evidence",
                                  "hypothesis")}


def _count_reasons(refusals: List[dict]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for r in refusals:
        out[r["reason"]] = out.get(r["reason"], 0) + 1
    return dict(sorted(out.items()))


# =========================================================================== co-occurrence control
def _sentence_lemmas(sent: str) -> List[str]:
    return sorted(set(lemma_word(t) for t in TOK.findall(sent)))


def cooccurrence_baseline(subjects: Sequence[str], stream: Sequence[str]) -> Dict[str, dict]:
    """Plain sentence-window co-occurrence prediction for each subject (pre-reg sec 4).

    Window = ONE SENTENCE, the same "document" convention as
    hdlab/low_information_filter.build_profile. Candidates are open-class lemmas
    (hdlab.closed_class_lexicon.is_closed_class), excluding the subject itself.

      pmi_top1  = argmax log2( c(s,w) * N / (c(s) * c(w)) ) over w with c(s,w) >= 3
      freq_top1 = most frequent co-occurring open-class lemma
    Ties: higher c(s,w), then lexicographic (deterministic; no built-in hash()).

    Only the sampled subjects are tracked, so this is one pass and no full pair-count table.
    """
    want = sorted(set(subjects))
    want_set = set(want)
    df: Counter = Counter()
    pair: Dict[str, Counter] = {s: Counter() for s in want}
    n_docs = 0
    for sent in stream:
        lem = _sentence_lemmas(sent)
        if not lem:
            continue
        n_docs += 1
        df.update(lem)
        present = [w for w in lem if w in want_set]
        if not present:
            continue
        for s in present:
            pair[s].update(w for w in lem if w != s)

    out: Dict[str, dict] = {}
    for s in want:
        c_s = df.get(s, 0)
        cands = []
        for w, c_sw in pair[s].items():
            if is_closed_class(w) or w == s:
                continue
            c_w = df.get(w, 0)
            if c_s <= 0 or c_w <= 0 or c_sw <= 0:
                continue
            pmi = math.log((c_sw * n_docs) / float(c_s * c_w), 2)
            cands.append((w, c_sw, round(pmi, 6)))
        # STRICT = the pre-registered rule exactly: PMI only over candidates with c(s,w) >= 3;
        # if none qualify the baseline PREDICTS NOTHING (top1 = None). RELAXED = the same with a
        # fall-back to all candidates when none qualify.
        #
        # Both are reported. The distinction matters and is not cosmetic: the fall-back can only
        # ADD agreement, and agreement is the statistic that would support hypothesis (B). Scoring
        # the control on the relaxed variant alone would bias the headline toward the conclusion
        # this cell is meant to be able to refute. The PRE-REG variant is STRICT; the relaxed
        # numbers are carried alongside so the gap is visible rather than buried.
        strict_pool = [c for c in cands if c[1] >= COOC_MIN_PAIR_COUNT]
        pmi_strict = sorted(strict_pool, key=lambda c: (-c[2], -c[1], c[0]))
        pmi_relaxed = sorted(strict_pool or cands, key=lambda c: (-c[2], -c[1], c[0]))
        freq_sorted = sorted(cands, key=lambda c: (-c[1], c[0]))
        out[s] = {
            "subject_doc_count": c_s,
            "n_candidates": len(cands),
            "n_candidates_meeting_min_pair_count": len(strict_pool),
            # pre-registered (STRICT) baseline
            "pmi_top1": pmi_strict[0][0] if pmi_strict else None,
            "pmi_top5": [c[0] for c in pmi_strict[:COOC_TOPK]],
            "pmi_top5_detail": [{"word": c[0], "pair_count": c[1], "pmi": c[2]}
                                for c in pmi_strict[:COOC_TOPK]],
            # relaxed variant, reported for contrast only
            "pmi_top1_relaxed": pmi_relaxed[0][0] if pmi_relaxed else None,
            "pmi_top5_relaxed": [c[0] for c in pmi_relaxed[:COOC_TOPK]],
            "used_relaxed_fallback": (not strict_pool) and bool(cands),
            "freq_top1": freq_sorted[0][0] if freq_sorted else None,
            "freq_top5": [c[0] for c in freq_sorted[:COOC_TOPK]],
            "min_pair_count": COOC_MIN_PAIR_COUNT,
        }
    return out


def _agreement(rows: Sequence[Tuple[str, str]], base: Dict[str, dict]) -> dict:
    """rows = [(subject, substrate_object)]."""
    n = len(rows)
    if not n:
        return {"n": 0}
    pmi1 = sum(1 for s, o in rows if base.get(s, {}).get("pmi_top1") == o)
    frq1 = sum(1 for s, o in rows if base.get(s, {}).get("freq_top1") == o)
    eith = sum(1 for s, o in rows if o in (base.get(s, {}).get("pmi_top1"),
                                           base.get(s, {}).get("freq_top1")))
    top5 = sum(1 for s, o in rows
               if o in sorted(set(base.get(s, {}).get("pmi_top5", []))
                              | set(base.get(s, {}).get("freq_top5", []))))
    pmi1_rx = sum(1 for s, o in rows if base.get(s, {}).get("pmi_top1_relaxed") == o)
    eith_rx = sum(1 for s, o in rows if o in (base.get(s, {}).get("pmi_top1_relaxed"),
                                              base.get(s, {}).get("freq_top1")))
    top5_rx = sum(1 for s, o in rows
                  if o in sorted(set(base.get(s, {}).get("pmi_top5_relaxed", []))
                                 | set(base.get(s, {}).get("freq_top5", []))))
    return {"n": n,
            # PRE-REGISTERED (strict c(s,w) >= 3) -- these are the numbers the bands judge
            "pmi_top1_agreement": round(pmi1 / n, 4),
            "freq_top1_agreement": round(frq1 / n, 4),
            "either_top1_agreement": round(eith / n, 4),
            "top5_containment": round(top5 / n, 4),
            # relaxed-fallback variant, for contrast only
            "pmi_top1_agreement_relaxed": round(pmi1_rx / n, 4),
            "either_top1_agreement_relaxed": round(eith_rx / n, 4),
            "top5_containment_relaxed": round(top5_rx / n, 4),
            "n_subjects_using_relaxed_fallback": sum(
                1 for s, _o in rows if base.get(s, {}).get("used_relaxed_fallback"))}


def cooc_control_for_arm(arm: str, sample_rows: List[dict], stream: Sequence[str]) -> dict:
    subs = [r["subject"] for r in sample_rows]
    base = cooccurrence_baseline(subs, stream)
    rows = [(r["subject"], r["object"]) for r in sample_rows]
    observed = _agreement(rows, base)
    # permutation floor: same subjects, objects shuffled across subjects within the arm
    objs = [o for _s, o in rows]
    random.Random(SAMPLE_SEED).shuffle(objs)
    floor = _agreement(list(zip([s for s, _o in rows], objs)), base)
    return {"arm": arm, "baseline": base, "observed": observed, "permutation_floor": floor,
            "delta_either_top1": round(observed.get("either_top1_agreement", 0.0)
                                       - floor.get("either_top1_agreement", 0.0), 4),
            "delta_top5": round(observed.get("top5_containment", 0.0)
                                - floor.get("top5_containment", 0.0), 4)}


# =========================================================================== audit sample
def _sample_rows(prov: List[dict]) -> List[dict]:
    """50 rows, random.Random(42).sample over fid order -- the SAME sampling convention as
    data/exp_definitional_grounding_v5/b3_audit_sample_DEF_V5.json."""
    by_fid = sorted(prov, key=lambda r: (int(r["fid"]), str(r["subject"])))
    n = min(SAMPLE_N, len(by_fid))
    picked = random.Random(SAMPLE_SEED).sample(by_fid, n)
    rows = []
    for r in picked:
        sents = sorted(set(e.get("sentence") for e in (r.get("evidence") or [])
                           if e.get("sentence")))
        hyp = r.get("hypothesis") or {}
        rows.append({
            "subject": r["subject"], "object": r["object"],
            "source_sentences": sents[:5],
            "_sealed": {"fid": r["fid"], "segment": r.get("segment"),
                        "best_cos": r.get("best_cos"), "schema_score": r.get("schema_score"),
                        "n_attestations": r.get("n_exposures"),
                        "n_confirm": hyp.get("n_confirm"),
                        "n_disconfirm": hyp.get("n_disconfirm"),
                        "n_abandoned": hyp.get("n_abandoned")},
        })
    return rows


def render_scoring_sheet(blind_rows: List[dict]) -> str:
    """EXACT format of data/exp_grounding_quality_readout_v1/SCORING_SHEET.txt.

    NO-LEAK (pre-reg sec 5 S6): index / `subject -> object` / ONE context sentence truncated to
    160 chars. No best_cos, no schema_score, no attestation counter, no fid, no segment, no arm
    label, no corpus name. This function is handed ONLY the blind rows: it has no arm key in
    scope and cannot print one.
    """
    lines = [
        "GROUNDED_MEANING BLIND SCORING SHEET  (exp_grounding_text_vs_mechanism)",
        "%d rows, file order preserved. Rubric: MEANINGFUL / RELATED / NOISE." % len(blind_rows),
        "Line 1: [idx] subject -> assigned grounded meaning.  Line 2: one context sentence "
        "(<=160 chars).",
        "Write your verdict at the end of line 1 for each row.",
        "=" * 100,
        "",
    ]
    for i, r in enumerate(blind_rows, start=1):
        sents = r.get("source_sentences") or []
        ctx = sents[0] if sents else ""
        if len(ctx) > 160:
            ctx = ctx[:160] + "..."
        lines.append("[%03d] %s  ->  %s" % (i, r["subject"], r["object"]))
        lines.append('      "%s"' % ctx)
        lines.append("")
    return "\n".join(lines)


def write_blind_material(output_dir: str, arms: Dict[str, dict],
                         streams: Dict[str, List[str]]) -> dict:
    combined: List[Tuple[str, dict]] = []
    per_arm_counts = {}
    cooc = {}
    for arm in ARMS:
        with open(os.path.join(output_dir, f"arm_{arm}_provenance.json"), encoding="utf-8") as f:
            prov = json.load(f)
        rows = _sample_rows(prov)
        per_arm_counts[arm] = len(rows)
        cooc[arm] = cooc_control_for_arm(arm, rows, streams[arm])
        combined.extend((arm, r) for r in rows)

    rng = random.Random(BLIND_SHUFFLE_SEED)
    rng.shuffle(combined)

    blind_rows, key_rows, sealed_rows = [], [], []
    cooc_by_blind_id = {}
    for i, (arm, r) in enumerate(combined):
        blind_rows.append({"blind_id": i, "subject": r["subject"], "object": r["object"],
                           "source_sentences": r["source_sentences"]})
        key_rows.append({"blind_id": i, "arm": arm, "subject": r["subject"],
                         "object": r["object"], "fid": r["_sealed"]["fid"]})
        sealed_rows.append({"blind_id": i, "arm": arm, "subject": r["subject"],
                            "object": r["object"], **r["_sealed"]})
        b = cooc[arm]["baseline"].get(r["subject"], {})
        cooc_by_blind_id[str(i)] = {
            "blind_id": i, "subject": r["subject"], "substrate_object": r["object"],
            "cooc_pmi_top1": b.get("pmi_top1"), "cooc_freq_top1": b.get("freq_top1"),
            "cooc_pmi_top5": b.get("pmi_top5"), "cooc_freq_top5": b.get("freq_top5"),
            "cooc_pmi_top5_detail": b.get("pmi_top5_detail"),
            "cooc_pmi_top1_relaxed": b.get("pmi_top1_relaxed"),
            "cooc_pmi_top5_relaxed": b.get("pmi_top5_relaxed"),
            "used_relaxed_fallback": b.get("used_relaxed_fallback"),
            "subject_doc_count": b.get("subject_doc_count"),
            "n_candidates_meeting_min_pair_count": b.get("n_candidates_meeting_min_pair_count"),
            "matches_pmi_top1": b.get("pmi_top1") == r["object"],
            "matches_freq_top1": b.get("freq_top1") == r["object"],
        }

    _atomic_json(os.path.join(output_dir, "blind_sample.json"), {
        "n_rows": len(blind_rows), "shuffle_seed": BLIND_SHUFFLE_SEED,
        "sample_seed": SAMPLE_SEED,
        "arms_present": "TWO, LABELS STRIPPED -- the key is in arm_key.json, do not open it "
                        "until every row is scored",
        "rubric": "MEANINGFUL / RELATED / NOISE per "
                  "notes/foundation_grounding_sample_2026-08-12.md",
        "instruction": "Score each row's (subject -> object) read-out as MEANINGFUL / RELATED / "
                       "NOISE using source_sentences as context. Score all rows in ONE sitting. "
                       "Do NOT open arm_key.json, blind_provenance_sealed.json or "
                       "cooccurrence_control.json until every row is scored.",
        "scored": False,
        "blinding_caveat": "LABEL-blind but GENRE-VISIBLE: the corpus is the variable, so a "
                           "context sentence can reveal which arm a row came from. Pre-reg sec 6 "
                           "declares this limitation.",
        "bands": QUALITY_BANDS_RECORDED,
        "rows": blind_rows,
    })
    _atomic_json(os.path.join(output_dir, "arm_key.json"), {
        "warning": "DO NOT OPEN UNTIL blind_sample.json IS FULLY SCORED",
        "shuffle_seed": BLIND_SHUFFLE_SEED, "rows": key_rows})
    _atomic_json(os.path.join(output_dir, "blind_provenance_sealed.json"), {
        "warning": "SEALED. Carries fid / segment / best_cos / schema_score / attestation "
                   "counters, all of which correlate with the arm. DO NOT OPEN UNTIL SCORED.",
        "rows": sealed_rows})
    _atomic_json(os.path.join(output_dir, "cooccurrence_control.json"), {
        "warning": "SEALED CONTROL. Never printed in the scoring sheet. DO NOT OPEN UNTIL "
                   "blind_sample.json IS FULLY SCORED.",
        "method": "sentence-window co-occurrence over THAT ARM'S OWN read stream; candidates are "
                  "open-class lemmas excluding the subject; pmi_top1 = argmax "
                  "log2(c(s,w)*N/(c(s)*c(w))) with c(s,w) >= %d; freq_top1 = most frequent "
                  "co-occurring open-class lemma" % COOC_MIN_PAIR_COUNT,
        "bands": COOC_BANDS_RECORDED,
        "per_arm_summary": {a: {"observed": cooc[a]["observed"],
                                "permutation_floor": cooc[a]["permutation_floor"],
                                "delta_either_top1": cooc[a]["delta_either_top1"],
                                "delta_top5": cooc[a]["delta_top5"]} for a in ARMS},
        "rows_by_blind_id": cooc_by_blind_id})

    # THE RENDERER SEES ONLY THE BLIND ROWS. arm_key.json is not opened here.
    sheet = render_scoring_sheet(blind_rows)
    with open(os.path.join(output_dir, "SCORING_SHEET.txt"), "w", encoding="utf-8",
              newline="\n") as f:
        f.write(sheet)

    return {"n_blind_rows": len(blind_rows), "per_arm_sample_n": per_arm_counts,
            "cooc_per_arm": {a: {"observed": cooc[a]["observed"],
                                 "permutation_floor": cooc[a]["permutation_floor"],
                                 "delta_either_top1": cooc[a]["delta_either_top1"],
                                 "delta_top5": cooc[a]["delta_top5"]} for a in ARMS},
            "sheet_text": sheet, "blind_rows": blind_rows}


def _s6_no_leak_check(sheet: str, blind_rows: List[dict]) -> dict:
    """Pre-reg sec 5 S6. The banned items are the METADATA FIELD NAMES and the ARM / CORPUS
    NAMES, matched at WORD BOUNDARIES.

    A naked substring scan (the first cut of this function) is wrong and fails on ordinary
    English: 'fid' occurs inside 'confidence'/'confident', 'arm' inside 'warm'/'farm'/'harm'/
    'pharmaceutical', and 'segment' is a legitimate content word in a biology sentence. Those
    are context words the rubric NEEDS, not leaked metadata, and flagging them would HARD_FAIL a
    clean sheet. The pre-reg bans the segment TAG and the arm NAME, not those letter sequences.

    The real no-leak guarantee is STRUCTURAL and is asserted as such below: the sheet is
    reproduced byte-for-byte from nothing but (index, subject, object, first source sentence).
    If that re-render matches, no other field can be present, whatever any substring scan says.
    """
    identifier_banned = ["best_cos", "schema_score", "n_attestations", "n_exposures",
                         "pass_idx", "blind_id", "arm_key", "n_confirm", "n_disconfirm",
                         "n_abandoned"]
    name_banned = ["NEWS", "TEXTBOOK", "OneStop", "onestop", "OneStopEnglish",
                   "OpenStax", "openstax"]
    hits = sorted(set([b for b in identifier_banned if b in sheet]
                      + [b for b in name_banned
                         if re.search(r"\b%s\b" % re.escape(b), sheet)]))

    # STRUCTURAL no-leak: re-render from the four permitted fields only and require equality.
    minimal = [{"subject": r["subject"], "object": r["object"],
                "source_sentences": (r.get("source_sentences") or [])[:1]} for r in blind_rows]
    structural_ok = (render_scoring_sheet(minimal) == sheet)

    body = sheet.split("\n")
    n_ctx = sum(1 for ln in body if ln.startswith('      "'))
    n_hdr = sum(1 for ln in body if ln.startswith("["))
    n = len(blind_rows)
    return {"ok": (not hits) and structural_ok and n_ctx == n and n_hdr == n,
            "banned_tokens_found": hits,
            "structural_rerender_matches": structural_ok,
            "n_context_lines": n_ctx,
            "n_row_header_lines": n_hdr, "expected_rows": n,
            "renderer_saw_arm_key": False,
            "note": "render_scoring_sheet() is passed ONLY blind rows; arm_key.json is not "
                    "opened by the renderer. Exactly one context sentence per row is enforced "
                    "by the structural re-render, which is given only source_sentences[:1]."}


# =========================================================================== finalize
def finalize(run_mode: str, output_dir: str, streams: Dict[str, List[str]]) -> dict:
    units = exp_checkpoint.load_units(output_dir)
    arms = {a: units[exp_checkpoint.unit_key("arm_done", a)] for a in ARMS
            if exp_checkpoint.unit_key("arm_done", a) in units}
    missing_arms = [a for a in ARMS if a not in arms]

    expected = sorted(set([exp_checkpoint.unit_key("arm_done", a) for a in ARMS]
                          + [exp_checkpoint.unit_key(a, "decile%d" % d)
                             for a in ARMS for d in range(N_DECILE_UNITS)]))
    missing_units = sorted(set(expected) - set(units))
    s1 = not missing_units and len(expected) == EXPECTED_N_UNITS

    s2 = bool(arms) and all(
        arms[a]["n_tautology_facts"] == 0 and arms[a]["n_closed_class_object_facts"] == 0
        and not arms[a]["no_leak_violations"] for a in arms)

    digests = {a: arms[a]["pairs_digest"] for a in arms}
    s3 = len(arms) == len(ARMS) and len(sorted(set(digests.values()))) == len(ARMS)

    ns = {a: arms[a]["n_sentences"] for a in arms}
    s4 = len(sorted(set(ns.values()))) == 1 and len(arms) == len(ARMS)

    s5 = bool(arms) and all(arms[a]["n_meaning_facts"] >= S5_YIELD_FLOOR for a in arms)

    blind = None
    s6_detail = {"ok": False, "note": "not reached"}
    if len(arms) == len(ARMS) and s5:
        blind = write_blind_material(output_dir, arms, streams)
        s6_detail = _s6_no_leak_check(blind.pop("sheet_text"), blind.pop("blind_rows"))
    s6 = bool(s6_detail["ok"])

    gates = {"S1_cardinality": s1, "S2_integrity": s2, "S3_arms_differ": s3,
             "S4_matched_n": s4, "S5_yield_floor": s5, "S6_blind_hygiene": s6}
    hard_fail = sorted(k for k, v in gates.items() if not v)
    if hard_fail:
        verdict = "HARD_FAIL"
        verdict_msg = ("STRUCTURAL gate(s) failed: " + ", ".join(hard_fail) +
                       " -- the blind sample is NOT fit to hand-score. No quality claim.")
    else:
        verdict = "STRUCTURAL_PASS_PENDING_B3"
        verdict_msg = (
            "structural gates pass; %d blind rows written for the Director's hand-score. "
            "THIS CELL MAKES NO QUALITY CLAIM. Matched N=%d sentences per arm."
            % (blind["n_blind_rows"], list(ns.values())[0]))

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "prereg": PREREG, "wire_status": "EXPERIMENT_LOCAL_NOT_WIRED",
        "verdict": verdict, "verdict_msg": verdict_msg,
        "QUALITY_CLAIM": "NONE -- this cell emits no quality tier. The primary discriminator is "
                         "a BLIND DIRECTOR HAND-SCORE on blind_sample.json / SCORING_SHEET.txt. "
                         "MECHANISM_IS_BINDING is a pre-registered, expected, acceptable "
                         "outcome (prereg sec 3).",
        "quality_bands_recorded_not_evaluated": QUALITY_BANDS_RECORDED,
        "cooccurrence_control_bands_recorded": COOC_BANDS_RECORDED,
        "cooccurrence_control_per_arm": (blind or {}).get("cooc_per_arm"),
        "matched_n_per_arm": ns,
        "per_arm": {a: {k: v for k, v in arms[a].items() if k != "refusal_reasons"}
                    for a in arms},
        "per_arm_refusal_reasons": {a: arms[a]["refusal_reasons"] for a in arms},
        "structural_gates": {
            "S1_cardinality": {"ok": s1, "expected_n_units": EXPECTED_N_UNITS,
                               "missing_units": missing_units, "missing_arms": missing_arms},
            "S2_integrity": {"ok": s2, "per_arm": {
                a: {"n_tautology_facts": arms[a]["n_tautology_facts"],
                    "n_closed_class_object_facts": arms[a]["n_closed_class_object_facts"],
                    "no_leak_violations": arms[a]["no_leak_violations"]} for a in arms}},
            "S3_arms_differ": {"ok": s3, "digests": digests},
            "S4_matched_n": {"ok": s4, "n_sentences_per_arm": ns},
            "S5_yield_floor": {"ok": s5, "floor": S5_YIELD_FLOOR,
                               "per_arm": {a: arms[a]["n_meaning_facts"] for a in arms}},
            "S6_blind_hygiene": s6_detail,
        },
        "blind_material": blind,
        "files": {"blind": "blind_sample.json", "sheet": "SCORING_SHEET.txt",
                  "key_SEALED": "arm_key.json",
                  "provenance_SEALED": "blind_provenance_sealed.json",
                  "cooccurrence_control_SEALED": "cooccurrence_control.json"},
        "summary": verdict,
    }
    _atomic_json(os.path.join(output_dir, "metrics.json"), metrics)
    return metrics


# =========================================================================== main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--arm", choices=ARMS + ["all"], default="all")
    args = ap.parse_args(argv)

    output_dir = _output_dir(args.run_mode)
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, args.run_mode, None if args.arm == "all" else args.arm)
    t0 = time.time()
    try:
        streams = build_streams(args.run_mode)
        print("[corpus] matched N per arm = %d (NEWS %d, TEXTBOOK %d)"
              % (len(streams["NEWS"]), len(streams["NEWS"]), len(streams["TEXTBOOK"])), flush=True)
        for arm in ARMS:
            if args.arm in (arm, "all"):
                s = run_arm(arm, streams[arm], output_dir)
                print("[arm-done] %s facts=%d grounded=%d elapsed=%.1fs"
                      % (arm, s["n_meaning_facts"], s["n_grounded"], s.get("elapsed_s", 0.0)),
                      flush=True)
        m = finalize(args.run_mode, output_dir, streams)
        print("[verdict] %s :: %s" % (m["verdict"], m["verdict_msg"]), flush=True)
        print("[elapsed] %.1fs" % (time.time() - t0), flush=True)
        return 0 if m["verdict"] != "HARD_FAIL" else 1
    except SystemExit:
        raise
    except Exception as exc:                                    # noqa: BLE001 - crash diagnostic
        _write_crash_metrics(output_dir, exc)
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
