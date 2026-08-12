"""exp_context_conditioned_sense_selection_v1 -- given a CONTEXT, can the substrate select the
RIGHT sense of a word that has several?

PRE-REG: preregs/2026-08-12_context_conditioned_sense_selection_v1.md (commit e3901e289).
Bands, controls and the leakage mechanisms were registered BEFORE any accuracy existed.

This is the capability a flat single-pair store cannot have AT ALL: a flat store has no
context input, so its best possible strategy is a fixed choice per word -> mean(1/k) = 0.4316
over the 288 multi-sense subjects of the v3 definitional fact set.

NOT the 50-pair MEANINGFUL/RELATED/NOISE rubric: that rubric scores isolated pairs and is
provably invariant to storage representation (see notes/wire_reader_to_meaning_organs_2026-08-12.md).
No number against that rubric is produced or reported here.

Owned organs reused (no promotion, no reinvention):
  hdlab/random_indexing.py       RandomIndexingEncoder  (open-vocab distributional)
  hdlab/grounded_similarity.py   Lancaster+Brysbaert 12-dim perceptual profiles
  hdlab/closed_class_lexicon.py  is_eligible_meaning     (content-word gate)
FHRRProcessStore is NOT promoted: a superposition store is one IMPLEMENTATION of the collapse
and cannot create signal the selection function does not have. Measure first.

ASCII only. Deterministic. Single CPU process.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys
import time
from typing import Dict, FrozenSet, List, Optional, Sequence, Tuple

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.random_indexing import RandomIndexingEncoder
from hdlab import grounded_similarity as GS
from hdlab.closed_class_lexicon import is_eligible_meaning

FACTS_PATH = os.path.join(REPO_ROOT, "data", "foundation",
                          "reading_grounding_v3_definitional", "definitional_facts.jsonl")
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_context_conditioned_sense_selection_v1")

# ---- pre-registered constants (declared in the prereg, not tuned on the outcome) ----------
RI_N = 8192
RI_SPARSITY = 10
RI_WINDOW = 5
RI_MIN_COUNT = 3
RI_SEED = 0
FLOOR_SUBJECT_WEIGHTED = 0.4316   # mean(1/k) over the 288 multi-sense subjects
N_SWAP_SEEDS = 5                  # C1 cross-item swap repetitions
N_FLOOR_SIM_SEEDS = 1000          # empirical check of the analytic floor

_TOKEN_RE = re.compile(r"[a-z]+")


def tokenize(text: str) -> List[str]:
    """Lowercase alphabetic tokens. THE single tokenizer -- used for the RI fit corpus, for
    context extraction, and for masking, so the three cannot silently diverge."""
    return _TOKEN_RE.findall(text.lower())


# ============================================================== eval-set construction
def load_multisense_eval() -> Tuple[Dict[str, List[dict]], List[dict], dict]:
    """Return (word -> its fact rows, trials, census). A trial is (word, true object, sentence)."""
    rows = [json.loads(line) for line in open(FACTS_PATH, encoding="utf-8")]
    by_subj: Dict[str, List[dict]] = collections.defaultdict(list)
    for r in rows:
        by_subj[r["subject"]].append(r)
    multi = {w: v for w, v in sorted(by_subj.items()) if len({r["object"] for r in v}) > 1}

    trials: List[dict] = []
    n_ambiguous = 0
    ambiguous_words = set()
    for w in sorted(multi):
        facts = multi[w]
        # a sentence attested for >1 DISTINCT sense of the same word has no unique label
        sent_owner: Dict[str, set] = collections.defaultdict(set)
        for f in facts:
            for s in f["source_sentences"]:
                sent_owner[s].add(f["object"])
        for f in facts:
            for s in f["source_sentences"]:
                if len(sent_owner[s]) > 1:
                    n_ambiguous += 1
                    ambiguous_words.add(w)
                    continue
                trials.append({"word": w, "true_object": f["object"], "sentence": s,
                               "fid": f["fid"], "k": len({x["object"] for x in facts}),
                               "n_src": len(f["source_sentences"])})

    ks = [len({r["object"] for r in v}) for v in multi.values()]
    census = {
        "n_facts_total": len(rows),
        "n_distinct_subjects": len(by_subj),
        "n_multisense_subjects": len(multi),
        "multisense_subject_frac": round(len(multi) / len(by_subj), 4),
        "n_facts_in_multisense": sum(len(v) for v in multi.values()),
        "mean_k": round(sum(ks) / len(ks), 4),
        "k_distribution": dict(sorted(collections.Counter(ks).items())),
        "analytic_floor_subject_weighted": round(sum(1.0 / k for k in ks) / len(ks), 4),
        "analytic_floor_micro_per_fact": round(len(multi) / sum(len(v) for v in multi.values()), 4),
        "n_trials": len(trials),
        "n_trials_excluded_label_ambiguous": n_ambiguous,
        "n_words_with_ambiguous_sentence": len(ambiguous_words),
        "src_sentence_count_distribution": dict(sorted(collections.Counter(
            len(f["source_sentences"]) for v in multi.values() for f in v).items())),
    }
    return multi, trials, census


# ============================================================== L2: answer masking
def build_mask_terms(word: str, facts: Sequence[dict]) -> FrozenSet[str]:
    """Every token that could lexically reveal the answer, for ALL k candidates symmetrically.

    Symmetric across candidates by construction: the mask set is built from the word's WHOLE
    candidate list, never from the true object alone, so the masking pattern carries no
    information about which candidate is correct."""
    terms = set(tokenize(word))
    for f in facts:
        terms.update(tokenize(f["object"]))
        terms.update(tokenize(f.get("definiens_surface") or ""))
        terms.update(tokenize(f.get("definiendum_surface") or ""))
    return frozenset(terms)


def masked_context_tokens(sentence: str, mask_terms: FrozenSet[str]) -> List[str]:
    """L2 + content-word gate. Returns the ONLY thing a selector is allowed to see from H."""
    return [t for t in tokenize(sentence)
            if t not in mask_terms and is_eligible_meaning(t) and len(t) > 2]


# ============================================================== selectors
class DistSelector:
    """S1 -- open-vocabulary distributional (random indexing), fit with eval sentences EXCLUDED."""

    name = "S1_DIST"

    def __init__(self, encoder: RandomIndexingEncoder) -> None:
        self.enc = encoder
        self._cache: Dict[str, Optional[np.ndarray]] = {}

    def vec(self, word: str) -> Optional[np.ndarray]:
        if word not in self._cache:
            if self.enc.has(word):
                v = self.enc.encode(word).astype(np.float64)
                n = float(np.linalg.norm(v))
                self._cache[word] = (v / n) if n > 0 else None
            else:
                self._cache[word] = None
        return self._cache[word]

    def covers(self, word: str) -> bool:
        return self.vec(word) is not None

    def scores(self, tokens: Sequence[str], candidates: Sequence[str]) -> Optional[List[float]]:
        cvs = [self.vec(c) for c in candidates]
        if sum(v is not None for v in cvs) < 2:
            return None
        tvs = [self.vec(t) for t in tokens]
        tvs = [v for v in tvs if v is not None]
        if not tvs:
            return [0.0] * len(candidates)
        T = np.stack(tvs)
        out: List[float] = []
        for v in cvs:
            out.append(float(np.mean(T @ v)) if v is not None else float("-inf"))
        return out


class PercSelector:
    """S2 -- raw uncapped Lancaster+Brysbaert 12-dim perceptual profiles.

    RANKING ONLY. GROUNDED_CAP=0.45 exists to stop this asset making a same-idea/link decision
    at SIMILARITY_LINK_THRESHOLD=0.50; no link decision is emitted anywhere in this cell, so
    ranking on the raw cosine does not touch what the cap protects."""

    name = "S2_PERC"

    def __init__(self) -> None:
        self.table = GS._table()
        self._cache: Dict[str, Optional[np.ndarray]] = {}

    def vec(self, word: str) -> Optional[np.ndarray]:
        if word not in self._cache:
            t = self.table.get(word.lower())
            if t is None:
                self._cache[word] = None
            else:
                v = np.asarray(t, dtype=np.float64).reshape(-1)
                n = float(np.linalg.norm(v))
                self._cache[word] = (v / n) if n > 0 else None
        return self._cache[word]

    def covers(self, word: str) -> bool:
        return self.vec(word) is not None

    def scores(self, tokens: Sequence[str], candidates: Sequence[str]) -> Optional[List[float]]:
        cvs = [self.vec(c) for c in candidates]
        if sum(v is not None for v in cvs) < 2:
            return None
        tvs = [self.vec(t) for t in tokens]
        tvs = [v for v in tvs if v is not None]
        if not tvs:
            return [0.0] * len(candidates)
        T = np.stack(tvs)
        return [float(np.mean(T @ v)) if v is not None else float("-inf") for v in cvs]


def argmax_deterministic(scores: Sequence[float], candidates: Sequence[str]) -> str:
    """Ties broken by sorted candidate order -- NEVER by a random draw. This is what makes the
    C2 lesion control able to fail: with no context, whatever bias this tie-break plus the
    candidate-side scores carry is exposed as an above-floor number."""
    best_i, best_s = 0, float("-inf")
    for i, s in enumerate(scores):
        if s > best_s + 1e-12:
            best_i, best_s = i, s
    return candidates[best_i]


def rank_of(scores: Sequence[float]) -> List[int]:
    order = sorted(range(len(scores)), key=lambda i: (-scores[i], i))
    r = [0] * len(scores)
    for pos, i in enumerate(order):
        r[i] = pos
    return r


# ============================================================== evaluation driver
def evaluate(trials: List[dict], multi: Dict[str, List[dict]], selectors: List[object],
             context_fn) -> Dict[str, dict]:
    """context_fn(trial) -> token list. One pass, all selectors, all trials."""
    per_sel: Dict[str, dict] = {s.name: {"correct": collections.Counter(),
                                         "total": collections.Counter(),
                                         "unscorable": 0, "wrong_rows": []} for s in selectors}
    per_sel["S3_COMBO"] = {"correct": collections.Counter(), "total": collections.Counter(),
                           "unscorable": 0, "wrong_rows": []}
    for tr in trials:
        w = tr["word"]
        candidates = sorted({f["object"] for f in multi[w]})
        tokens = context_fn(tr)
        rank_acc: Optional[List[float]] = None
        n_rank = 0
        for sel in selectors:
            sc = sel.scores(tokens, candidates)
            d = per_sel[sel.name]
            if sc is None:
                d["unscorable"] += 1
                continue
            pick = argmax_deterministic(sc, candidates)
            d["total"][w] += 1
            if pick == tr["true_object"]:
                d["correct"][w] += 1
            else:
                d["wrong_rows"].append((w, tr["true_object"], pick))
            r = rank_of(sc)
            rank_acc = [float(x) for x in r] if rank_acc is None else [a + b for a, b in zip(rank_acc, r)]
            n_rank += 1
        dc = per_sel["S3_COMBO"]
        if rank_acc is not None and n_rank == len(selectors):
            sc = [-x for x in rank_acc]
            pick = argmax_deterministic(sc, candidates)
            dc["total"][w] += 1
            if pick == tr["true_object"]:
                dc["correct"][w] += 1
        else:
            dc["unscorable"] += 1
    return per_sel


def summarize(d: dict) -> dict:
    words = sorted(d["total"])
    if not words:
        return {"subject_weighted_acc": None, "micro_acc": None, "n_words": 0, "n_trials": 0,
                "unscorable_trials": d["unscorable"]}
    per_word = [d["correct"][w] / d["total"][w] for w in words]
    n_tot = sum(d["total"][w] for w in words)
    n_cor = sum(d["correct"][w] for w in words)
    return {
        "subject_weighted_acc": round(sum(per_word) / len(per_word), 4),
        "micro_acc": round(n_cor / n_tot, 4),
        "micro_ci95": wilson(n_cor, n_tot),
        "n_words": len(words),
        "n_trials": n_tot,
        "unscorable_trials": d["unscorable"],
        "n_words_zero_correct": sum(1 for p in per_word if p == 0.0),
    }


def wilson(k: int, n: int, z: float = 1.96) -> List[float]:
    if n == 0:
        return [0.0, 0.0]
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / den
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


# ============================================================== main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="tiny corpus + 40 trials, gate only")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--timeout", type=int, default=3600)
    args = ap.parse_args()

    if args.self_test:
        run_self_tests()
        print("SELF-TEST OK")
        return

    t_start = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    multi, trials, census = load_multisense_eval()
    print("[census] %s" % json.dumps(census), flush=True)

    # ---- FLOOR: analytic vs empirical (a mismatch is a harness bug and blocks the run) ----
    ks = [len({r["object"] for r in v}) for v in multi.values()]
    analytic = sum(1.0 / k for k in ks) / len(ks)
    rng = np.random.default_rng(12345)
    sims = [float(np.mean([1.0 if rng.integers(k) == 0 else 0.0 for k in ks]))
            for _ in range(N_FLOOR_SIM_SEEDS if not args.smoke else 50)]
    emp = float(np.mean(sims))
    assert abs(analytic - FLOOR_SUBJECT_WEIGHTED) < 5e-4, "analytic floor drifted: %r" % analytic
    assert abs(emp - analytic) < 0.02, "empirical floor %r != analytic %r" % (emp, analytic)
    print("[floor] analytic=%.4f empirical=%.4f (n=%d)" % (analytic, emp, len(sims)), flush=True)

    # ---- L1: fit corpus with EVERY eval sentence removed --------------------------------
    from experiments.exp_definitional_grounding_v3 import load_corpus
    print("[corpus] loading...", flush=True)
    corpus = load_corpus(200 if args.smoke else None)
    eval_sentences = {tr["sentence"] for tr in trials}
    kept = [s for _seg, s in corpus if s not in eval_sentences]
    n_removed = len(corpus) - len(kept)
    assert not (set(kept) & eval_sentences), "L1 VIOLATION: an eval sentence survived in the fit corpus"
    print("[corpus] %d sentences, %d removed as eval, %d kept" % (len(corpus), n_removed, len(kept)),
          flush=True)

    fit_tokens: List[str] = []
    for s in kept:
        fit_tokens.extend(tokenize(s))
    print("[corpus] %d fit tokens" % len(fit_tokens), flush=True)

    enc = RandomIndexingEncoder(N=1024 if args.smoke else RI_N, sparsity=RI_SPARSITY,
                                window=RI_WINDOW, min_count=RI_MIN_COUNT, seed=RI_SEED)
    t0 = time.time()
    enc.fit_corpus(fit_tokens)
    print("[ri] vocab=%d fit_s=%.1f" % (enc.vocab_size(), time.time() - t0), flush=True)

    s1, s2 = DistSelector(enc), PercSelector()
    selectors = [s1, s2]

    if args.smoke:
        trials = trials[:40]

    # ---- L2 verification on every trial, asserted -----------------------------------------
    mask_cache = {w: build_mask_terms(w, multi[w]) for w in sorted(multi)}
    ctx_cache: Dict[Tuple[str, str], List[str]] = {}

    def ctx_primary(tr: dict) -> List[str]:
        key = (tr["word"], tr["sentence"])
        if key not in ctx_cache:
            toks = masked_context_tokens(tr["sentence"], mask_cache[tr["word"]])
            cand_tokens = set()
            for f in multi[tr["word"]]:
                cand_tokens.update(tokenize(f["object"]))
            assert not (set(toks) & cand_tokens), \
                "L2 VIOLATION: candidate token survived masking for %r" % tr["word"]
            ctx_cache[key] = toks
        return ctx_cache[key]

    n_empty_ctx = sum(1 for tr in trials if not ctx_primary(tr))
    ctx_lens = [len(ctx_primary(tr)) for tr in trials]
    print("[L2] masked ok; mean ctx tokens=%.2f empty=%d" %
          (sum(ctx_lens) / len(ctx_lens), n_empty_ctx), flush=True)

    # ---- PRIMARY ---------------------------------------------------------------------------
    print("[run] primary...", flush=True)
    primary = {k: summarize(v) for k, v in evaluate(trials, multi, selectors, ctx_primary).items()}
    for k, v in primary.items():
        print("  %s subj_w=%s micro=%s n=%s unscorable=%s" %
              (k, v["subject_weighted_acc"], v["micro_acc"], v["n_trials"], v["unscorable_trials"]),
              flush=True)

    # ---- C1 CROSS-ITEM CONTEXT SWAP (the scramble that can fail) --------------------------
    print("[run] C1 cross-item swap...", flush=True)
    all_sents = sorted({(tr["word"], tr["sentence"]) for tr in trials})
    c1_runs: List[Dict[str, dict]] = []
    for seed in range(N_SWAP_SEEDS if not args.smoke else 2):
        r = np.random.default_rng(1000 + seed)
        swap: Dict[Tuple[str, str], List[str]] = {}
        for tr in trials:
            for _try in range(20):
                w2, s2_ = all_sents[int(r.integers(len(all_sents)))]
                if w2 != tr["word"]:
                    break
            swap[(tr["word"], tr["sentence"])] = masked_context_tokens(s2_, mask_cache[tr["word"]])
        c1_runs.append({k: summarize(v) for k, v in evaluate(
            trials, multi, selectors, lambda tr: swap[(tr["word"], tr["sentence"])]).items()})
    c1 = {k: {"subject_weighted_acc": round(float(np.mean([run[k]["subject_weighted_acc"]
                                                           for run in c1_runs])), 4),
              "subject_weighted_sd": round(float(np.std([run[k]["subject_weighted_acc"]
                                                         for run in c1_runs])), 4),
              "micro_acc": round(float(np.mean([run[k]["micro_acc"] for run in c1_runs])), 4),
              "n_seeds": len(c1_runs)} for k in c1_runs[0]}
    for k, v in c1.items():
        print("  C1 %s subj_w=%s (sd %s)" % (k, v["subject_weighted_acc"], v["subject_weighted_sd"]),
              flush=True)

    # ---- C2 CONTEXT LESION (same code path, empty context; measures candidate-side bias) ---
    print("[run] C2 lesion...", flush=True)
    c2 = {k: summarize(v) for k, v in evaluate(trials, multi, selectors, lambda tr: []).items()}
    for k, v in c2.items():
        print("  C2 %s subj_w=%s" % (k, v["subject_weighted_acc"]), flush=True)

    # ---- C3 STRICT LEAVE-ONE-SENTENCE-OUT POSITIVE CONTROL --------------------------------
    print("[run] C3 strict LOO...", flush=True)
    c3 = run_c3(multi, s1, mask_cache)
    print("  C3 %s" % json.dumps(c3), flush=True)

    # ---- inseparable tail -------------------------------------------------------------------
    tail = analyse_tail(trials, multi, selectors, ctx_primary, s1, s2)

    # ---- verdict against the PRE-REGISTERED bands ------------------------------------------
    best_name = max(("S1_DIST", "S2_PERC", "S3_COMBO"),
                    key=lambda n: primary[n]["subject_weighted_acc"] or 0.0)
    acc = primary[best_name]["subject_weighted_acc"] or 0.0
    c1_best = c1[best_name]["subject_weighted_acc"]
    c2_best = c2[best_name]["subject_weighted_acc"] or 0.0
    c1_drop = round(acc - c1_best, 4)
    both_at_floor = ((primary["S1_DIST"]["subject_weighted_acc"] or 0) <= FLOOR_SUBJECT_WEIGHTED + 0.03
                     and (primary["S2_PERC"]["subject_weighted_acc"] or 0) <= FLOOR_SUBJECT_WEIGHTED + 0.03)
    if both_at_floor or c1_drop < 0.05 or c2_best >= acc - 0.03:
        verdict = "HARD_FAIL_context_conditioned_sense_selection_DOES_NOT_WORK"
    elif acc <= 0.55:
        verdict = "MIDDLE_BAND"
    elif acc >= 0.65 and c2_best <= FLOOR_SUBJECT_WEIGHTED + 0.03 and c1_drop >= 0.08 \
            and (c3.get("acc") or 0) >= 0.70:
        verdict = "HARD_PASS"
    elif c1_drop >= 0.08 and c2_best <= FLOOR_SUBJECT_WEIGHTED + 0.03:
        verdict = "PASS"
    else:
        verdict = "MIDDLE_BAND"

    metrics = {
        "cell": "exp_context_conditioned_sense_selection_v1",
        "prereg": "preregs/2026-08-12_context_conditioned_sense_selection_v1.md",
        "census": census,
        "floor": {"analytic_subject_weighted": round(analytic, 4),
                  "empirical_subject_weighted": round(emp, 4),
                  "analytic_micro_per_fact": census["analytic_floor_micro_per_fact"]},
        "ri_encoder": {"N": enc.N, "sparsity": enc.sparsity, "window": enc.window,
                       "min_count": enc.min_count, "seed": enc.seed,
                       "vocab_size": enc.vocab_size(), "n_tokens_seen": enc._n_tokens_seen},
        "leakage_control": {
            "L1_eval_sentences_removed_from_fit_corpus": n_removed,
            "L1_asserted_disjoint": True,
            "L2_answer_tokens_masked_asserted": True,
            "L2_mean_context_tokens": round(sum(ctx_lens) / len(ctx_lens), 2),
            "L2_empty_context_trials": n_empty_ctx,
            "L3_no_extractor_metadata_in_scorer": True,
            "S2_asset_is_sentence_independent": True,
        },
        "primary": primary,
        "C1_cross_item_context_swap": c1,
        "C2_context_lesion": c2,
        "C3_strict_leave_one_sentence_out": c3,
        "removed_control_cannot_fail": (
            "WORD-ORDER SCRAMBLE of the context: both selectors are bag-of-words aggregates, so "
            "permuting token order leaves every score bit-identical -- it cannot fail by "
            "construction and was removed. C1 cross-item swap replaces it."),
        "best_selector": best_name,
        "best_subject_weighted_acc": acc,
        "C1_drop": c1_drop,
        "inseparable_tail": tail,
        "final_verdict": verdict,
        "runtime_s": round(time.time() - t_start, 1),
        "smoke": bool(args.smoke),
    }
    out = os.path.join(OUTPUT_DIR, "metrics_smoke.json" if args.smoke else "metrics.json")
    tmp = out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out)
    print("VERDICT %s  best=%s acc=%.4f floor=%.4f C1=%.4f C2=%.4f" %
          (verdict, best_name, acc, FLOOR_SUBJECT_WEIGHTED, c1_best, c2_best), flush=True)
    print("wrote %s" % out, flush=True)


def run_c3(multi: Dict[str, List[dict]], s1: DistSelector,
           mask_cache: Dict[str, FrozenSet[str]]) -> dict:
    """C3 -- the ONE arm whose sense-side representation is genuinely CONTEXT-derived.

    For each fact with >=2 source sentences: hold out one sentence H; represent EVERY candidate
    sense of that word by the mean RI vector of the content tokens of its OTHER sentences
    (H excluded from all of them); pick the nearest. Leakage-proof by construction: H never
    contributes to any sense representation. Underpowered by design."""
    n_ok = n_tot = 0
    n_unscorable = 0
    per_word: Dict[str, List[int]] = collections.defaultdict(list)
    for w in sorted(multi):
        facts = multi[w]
        for f in facts:
            if len(f["source_sentences"]) < 2:
                continue
            for held in f["source_sentences"]:
                cand_vecs: Dict[str, Optional[np.ndarray]] = {}
                for g in facts:
                    sents = [s for s in g["source_sentences"] if s != held]
                    vecs = []
                    for s in sents:
                        for t in masked_context_tokens(s, mask_cache[w]):
                            v = s1.vec(t)
                            if v is not None:
                                vecs.append(v)
                    cand_vecs[g["object"]] = (np.mean(np.stack(vecs), axis=0) if vecs else None)
                usable = sorted([o for o, v in cand_vecs.items() if v is not None])
                if len(usable) < 2:
                    n_unscorable += 1
                    continue
                q = [s1.vec(t) for t in masked_context_tokens(held, mask_cache[w])]
                q = [v for v in q if v is not None]
                if not q:
                    n_unscorable += 1
                    continue
                qv = np.mean(np.stack(q), axis=0)
                sc = [float(qv @ cand_vecs[o] / (np.linalg.norm(qv) * np.linalg.norm(cand_vecs[o])
                                                 + 1e-12)) for o in usable]
                pick = argmax_deterministic(sc, usable)
                n_tot += 1
                hit = 1 if pick == f["object"] else 0
                n_ok += hit
                per_word[w].append(hit)
    subj_w = (sum(sum(v) / len(v) for v in per_word.values()) / len(per_word)) if per_word else None
    return {"acc": round(n_ok / n_tot, 4) if n_tot else None,
            "subject_weighted_acc": round(subj_w, 4) if subj_w is not None else None,
            "n_trials": n_tot, "n_words": len(per_word), "n_unscorable": n_unscorable,
            "ci95": wilson(n_ok, n_tot),
            "note": "sense side built ONLY from the sense's other sentences; held-out sentence "
                    "excluded from every candidate. Underpowered: facts with >=2 source sentences."}


def analyse_tail(trials, multi, selectors, ctx_fn, s1: DistSelector, s2: PercSelector) -> dict:
    """The honest tail: which words are NEVER selected correctly, and is there a pattern?"""
    per_word_hits: Dict[str, List[int]] = collections.defaultdict(list)
    for tr in trials:
        w = tr["word"]
        candidates = sorted({f["object"] for f in multi[w]})
        toks = ctx_fn(tr)
        best_hit = 0
        scored = False
        for sel in selectors:
            sc = sel.scores(toks, candidates)
            if sc is None:
                continue
            scored = True
            if argmax_deterministic(sc, candidates) == tr["true_object"]:
                best_hit = 1
        if scored:
            per_word_hits[w].append(best_hit)

    dead = sorted(w for w, hits in per_word_hits.items() if hits and sum(hits) == 0)
    # classify
    cats: Dict[str, List[str]] = collections.defaultdict(list)
    for w in dead:
        facts = multi[w]
        objs = sorted({f["object"] for f in facts})
        surfaces = [f.get("definiendum_surface") or "" for f in facts]
        proper = any(s[:1].isupper() for s in surfaces if s)
        # near-duplicate senses: any object pair with high perceptual profile cosine
        sims = []
        for i in range(len(objs)):
            for j in range(i + 1, len(objs)):
                a, b = s2.vec(objs[i]), s2.vec(objs[j])
                if a is not None and b is not None:
                    sims.append(float(a @ b))
        max_sim = max(sims) if sims else None
        if proper:
            cats["proper_noun_entity_collision"].append(w)
        elif max_sim is not None and max_sim >= 0.90:
            cats["near_duplicate_senses_extraction_split"].append(w)
        else:
            cats["distinct_senses_no_context_support"].append(w)

    n_words_scored = len(per_word_hits)
    return {
        "n_words_scored": n_words_scored,
        "n_words_never_correct": len(dead),
        "frac_words_never_correct": round(len(dead) / n_words_scored, 4) if n_words_scored else None,
        "pattern_counts": {k: len(v) for k, v in sorted(cats.items())},
        "examples": {k: [{"word": w, "senses": sorted({f["object"] for f in multi[w]})}
                         for w in v[:8]] for k, v in sorted(cats.items())},
    }


# ============================================================== formula self-tests
def run_self_tests() -> None:
    # (1) tokenizer + masking really removes every candidate token, symmetrically
    facts = [{"object": "company", "definiens_surface": "the biggest company",
              "definiendum_surface": "Apple", "source_sentences": ["x"]},
             {"object": "valuable", "definiens_surface": "the most valuable",
              "definiendum_surface": "Apple", "source_sentences": ["y"]}]
    mt = build_mask_terms("apple", facts)
    assert "company" in mt and "valuable" in mt and "apple" in mt, mt
    toks = masked_context_tokens("The brand value of Apple, the biggest company, rose", mt)
    assert "company" not in toks and "apple" not in toks, toks
    assert "brand" in toks, toks

    # (2) deterministic tie-break, never random -- what makes C2 able to fail
    assert argmax_deterministic([0.5, 0.5, 0.5], ["a", "b", "c"]) == "a"
    assert argmax_deterministic([0.1, 0.9], ["a", "b"]) == "b"

    # (3) floor formula matches the pre-registered number on the real k distribution
    kd = {2: 187, 3: 77, 4: 12, 5: 7, 6: 3, 7: 1, 10: 1}
    ks = [k for k, n in kd.items() for _ in range(n)]
    assert len(ks) == 288, len(ks)
    f = sum(1.0 / k for k in ks) / len(ks)
    assert abs(f - FLOOR_SUBJECT_WEIGHTED) < 5e-4, f
    assert abs(sum(ks) / len(ks) - 2.5104) < 5e-4

    # (4) wilson sanity
    lo, hi = wilson(50, 100)
    assert lo < 0.5 < hi and hi - lo < 0.25, (lo, hi)

    # (5) THE removed control really is invariant -- proves removing it was correct, not lazy
    class _Enc:
        def has(self, w): return True
        def encode(self, w): return np.array([hash(w) % 7, len(w), 1.0], dtype=np.float64)
    sel = DistSelector(_Enc())
    t = ["alpha", "beta", "gamma", "delta"]
    a = sel.scores(t, ["one", "two"])
    b = sel.scores(list(reversed(t)), ["one", "two"])
    assert a == b, "word-order scramble is NOT invariant -- the removal rationale is wrong"

    # (6) rank helper
    assert rank_of([0.1, 0.9, 0.5]) == [2, 0, 1]

    # (7) the eval set on disk still matches what the prereg fixed
    _multi, _trials, census = load_multisense_eval()
    assert census["n_multisense_subjects"] == 288, census
    assert census["mean_k"] == 2.5104, census
    assert census["analytic_floor_subject_weighted"] == 0.4316, census
    assert census["n_facts_total"] == 1751, census


if __name__ == "__main__":
    main()
