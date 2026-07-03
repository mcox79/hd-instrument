"""exp_substrate_stage1_apply_exp2b_ppr_walk_wikipedia_semantic_kb_smoke_2026_07_03.

Experiment 2B (semantic-KB detour) from the optimal-retrieval-architecture drill.

Question: on a REAL semantic KG built from HotpotQA distractor's Wikipedia-derived
context (10 titles per query, edges = title-A mentions title-B via case-insensitive
word-boundary substring match), does fixed-iteration PPR (alpha=0.15, 5 iters) seeded
from Exp-1-style char-trigram-matched title entities extracted from hop-1 top-K
bge-small sentences recover supporting-facts sentences at recall@5 meaningfully
higher than hop-1-dense-alone on the missed-by-hop-1 subset?

Decision-point experiment:
  HARD_PASS (recovery_rate >= 0.50)  -> graph-walk viable; chain Exp 3.
  HARD_FAIL (recovery_rate <  0.15)  -> graph-walk dead even w/ semantic signal;
                                        revive encoder-swap path.
  MIDDLE   (0.15 <= rate < 0.50)     -> partial signal; call USER.

Precedent replay: imports Exp 1's char-trigram entity extraction (`build_entity_codebook`,
`extract_matched_entities`) and Exp 2's PPR primitives (`build_undirected_adjacency`,
`ppr_iterate`, `rank_chunks_by_ppr`, `seed_from_entities`). NO new sparse-linear-algebra
abstraction.

Real semantic KG replaces Exp 2's synthetic random-UUID KG. HotpotQA (Yang et al 2018)
is the sibling dataset of 2WikiMultihopQA which HippoRAG (arXiv:2405.14831) reported
+11-20pp lift on.

ASCII-only. sequential-CPU (~30-40s per seed dominated by bge encoding).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (per-arm per-query hit-vector hash)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (not BaseException)
# - crlb_n_a: PPR recall@5 is a rate not a shift-noise measurement
# - baseline_in_band: hop-1 baseline expected 0.20 < BASELINE < 0.60 typical HippoRAG regime
# - discriminator survives scale: this IS the honest scale-test (real semantic KG)
# - HARD_PASS strict at >= 0.50; HARD_FAIL strict at < 0.15; band 0.15..0.50 = MIDDLE
# - HP_SCOPE: HARD_PASS applies to MAIN vs missed-by-hop1; POS/NEG independent
# - cardinality_ok: EXPECTED_N_UNITS = 4 arms x 3 seeds = 12
# - per-unit failure-class instrumentation (no bare except; specific Exception only)
# - calibration_check: default_ok_for_this_regime (Exp 1/Exp 2 defaults hold)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
# - progress_logging: print_flush_true (short cell but still flush all output)
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except (AttributeError, TypeError, ValueError):
    pass

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import argparse
import hashlib
import json
import platform
import random
import re
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

# Import Exp 1 primitives (char-trigram fuzzy entity extraction)
from experiments import exp_substrate_stage1_apply_exp1_bridge_entity_coverage_smoke_2026_07_03 as EXP1  # noqa: E402
# Import Exp 2 primitives (PPR power iteration + column-normalized adjacency)
from experiments import exp_substrate_stage1_apply_exp2_ppr_walk_bridge_recovery_smoke_2026_07_03 as EXP2  # noqa: E402


ANCHOR_NAME = "substrate_stage1_apply_exp2b_ppr_walk_wikipedia_semantic_kb_smoke_2026_07_03"

# ---------- CLI / run_mode ----------
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--full", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if "--self-test" in sys.argv:
    RUN_MODE = "self_test"
elif "--full" in sys.argv:
    RUN_MODE = "full"
elif "--smoke" in sys.argv:
    RUN_MODE = "smoke"
else:
    RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "smoke").lower()

# ---------- Config ----------
SEEDS = [11, 17, 23]  # match Exp 1 / Exp 2 seed convention
N_QUERIES_PER_SEED = 20  # per-seed sample of bridge queries; 60 total across 3 seeds
BGE_MODEL = "BAAI/bge-small-en-v1.5"  # fast CPU-eligible; matches RAG-composition SMOKE
Q_INSTR = "Represent this sentence for searching relevant passages: "
BGE_MAX_LEN = 128  # HotpotQA sentences are longer than the synthetic RAG facts
BGE_BATCH = 32
PPR_ALPHA = 0.15         # CITED@Haveliwala_2003 / matches Exp 2
PPR_ITERS = 5            # matches Exp 2
PPR_TOP_K = 5            # apples-to-apples with baseline hop-1 top-K
COSINE_THRESH = 0.5      # matches Exp 1 char-trigram fuzzy threshold
N_DIM_TRIGRAM = 1024     # matches Exp 1
MASS_CONSERVATION_TOL = 0.005
KG_SIGNAL_FLOOR = 1.0    # mean_edges_per_node discriminator-fires floor
KG_SIGNAL_QUERY_FRAC_MIN = 0.50  # at least 50% of queries must clear KG floor

HOTPOTQA_PATH = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"


# ---------- HotpotQA loader ----------
def load_bridge_queries(path: Path) -> List[Dict]:
    """Load HotpotQA JSONL, keep only type=='bridge' entries."""
    out = []
    if not path.exists():
        raise FileNotFoundError("HotpotQA dataset not found: %s" % path)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d.get("type") == "bridge":
                out.append(d)
    return out


def sample_queries(bridge_queries: List[Dict], seed: int, n: int) -> List[Dict]:
    """Deterministic sample of n bridge queries via random.Random(seed)."""
    if n > len(bridge_queries):
        n = len(bridge_queries)
    rng = random.Random(seed)
    return rng.sample(bridge_queries, n)


# ---------- KG construction ----------
def flatten_context(query: Dict) -> Tuple[List[str], List[str], List[str]]:
    """Return (titles, per_sentence_title, sentences) where sentences is the flat
    concatenation of context.sentences in title-order, per_sentence_title[k] is the
    title article of flat sentence k, titles is the distinct title list preserving
    input order.
    """
    titles = list(query["context"]["title"])  # 10 titles (may include dupes rarely)
    sentence_groups = list(query["context"]["sentences"])
    flat_sentences: List[str] = []
    per_sent_title: List[str] = []
    for t, sents in zip(titles, sentence_groups):
        for s in sents:
            flat_sentences.append(s.strip())
            per_sent_title.append(t)
    return titles, per_sent_title, flat_sentences


def target_flat_indices(query: Dict, titles: List[str],
                        sentence_groups: List[List[str]]) -> List[int]:
    """Resolve supporting_facts (title, sent_id) to flat sentence indices.

    HotpotQA supporting_facts.sent_id references sentence index WITHIN that title's
    paragraph. We flatten to global sentence idx.
    Skip supporting_facts whose title is not in context (rare distractor mismatch).
    """
    sf_titles = query["supporting_facts"]["title"]
    sf_sent_ids = query["supporting_facts"]["sent_id"]
    # Build title -> flat_offset (index of first sentence of that title in flat list)
    title_to_offset: Dict[str, int] = {}
    running = 0
    for t, sents in zip(titles, sentence_groups):
        # Only set first occurrence in case of dupe titles
        if t not in title_to_offset:
            title_to_offset[t] = running
        running += len(sents)
    out: List[int] = []
    for t, sid in zip(sf_titles, sf_sent_ids):
        if t in title_to_offset:
            # bounds check: sid must be < n_sents_of_title
            # find matching sents; supporting_facts sid is relative to that title's sentence list
            offset = title_to_offset[t]
            # Determine title sentence count from the paired position; take first occurrence
            n_sents_for_title = len(
                sentence_groups[titles.index(t)]) if t in titles else 0
            if 0 <= sid < n_sents_for_title:
                out.append(offset + sid)
    return sorted(set(out))


def _title_regex(title: str) -> "re.Pattern[str]":
    """Build a case-insensitive word-boundary regex for a title string.

    Escape regex metachars in the title. Word boundary at both ends. Empty or
    all-non-word titles produce a pattern that never matches (returns re.compile("$^")).
    """
    if not title.strip():
        return re.compile(r"$^")
    escaped = re.escape(title.strip())
    # Use \b if either end of title is word-char; otherwise pattern still works via re.escape
    return re.compile(r"(?<!\w)" + escaped + r"(?!\w)", re.IGNORECASE)


def build_query_kg(titles: List[str], sentence_groups: List[List[str]]) -> Tuple[
        List[str], np.ndarray, int, float]:
    """Build the per-query mini-KG adjacency.

    Nodes = distinct titles (dedup preserving order).
    Edges: for each ordered pair (A, B) with A != B, count sentences in A's paragraph
    that contain B as a case-insensitive word-boundary substring. Symmetrize into
    undirected count matrix. Column-normalize per Exp 2's PPR convention.

    Returns (distinct_titles, A_col_stochastic, n_edges_nonzero, mean_edges_per_node).
    """
    # Dedup preserving order
    seen = set()
    distinct: List[str] = []
    for t in titles:
        if t not in seen:
            seen.add(t)
            distinct.append(t)
    n = len(distinct)
    # For each title, pool its sentences (concatenated; dedupe if title dupes exist)
    title_to_sents: Dict[str, List[str]] = {t: [] for t in distinct}
    for t, sents in zip(titles, sentence_groups):
        if t in title_to_sents:
            title_to_sents[t].extend(sents)
    # Precompile regexes per title (as the "target of mention")
    regexes = {t: _title_regex(t) for t in distinct}
    C = np.zeros((n, n), dtype=np.float64)
    idx = {t: i for i, t in enumerate(distinct)}
    for t_src in distinct:
        src_text = " \n ".join(title_to_sents[t_src])
        for t_tgt in distinct:
            if t_src == t_tgt:
                continue
            # count occurrences
            matches = regexes[t_tgt].findall(src_text)
            if matches:
                C[idx[t_src], idx[t_tgt]] += len(matches)
    # Symmetrize (undirected mention graph)
    C_sym = C + C.T
    n_edges_nonzero = int((C_sym > 0).sum() // 2)  # undirected edge count
    edges_per_node = (C_sym > 0).sum(axis=0)  # degree count per node
    mean_deg = float(edges_per_node.mean()) if n > 0 else 0.0
    # Column-normalize (Exp 2 convention). Isolated columns stay zero.
    col_sums = C_sym.sum(axis=0)
    col_safe = np.where(col_sums > 0, col_sums, 1.0)
    A = C_sym / col_safe[np.newaxis, :]
    A[:, col_sums == 0] = 0.0
    return distinct, A, n_edges_nonzero, mean_deg


# ---------- BGE retrieval ----------
def bge_encode_all(texts: List[str]) -> np.ndarray:
    """Encode a list of texts via bge-small; returns (N, hidden_size) L2-normalized."""
    import torch
    from transformers import AutoModel, AutoTokenizer
    DEV = torch.device("cpu")
    tok = AutoTokenizer.from_pretrained(BGE_MODEL)
    mdl = AutoModel.from_pretrained(BGE_MODEL).to(DEV).eval()
    out = []
    for i in range(0, len(texts), BGE_BATCH):
        batch = texts[i:i + BGE_BATCH]
        t = tok(batch, return_tensors="pt", padding=True, truncation=True,
                max_length=BGE_MAX_LEN).to(DEV)
        with torch.no_grad():
            o = mdl(**t)
        v = o.last_hidden_state[:, 0, :].float().cpu().numpy()
        v = v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-8)
        out.append(v)
    del mdl
    return np.concatenate(out, 0).astype(np.float32)


def dense_top_k(query_vec: np.ndarray, sent_matrix: np.ndarray, k: int) -> List[int]:
    """Return top-k sentence indices by cosine (both L2-normalized already)."""
    sims = sent_matrix @ query_vec
    order = np.argsort(sims)[::-1][:k].tolist()
    return [int(i) for i in order]


# ---------- PPR-ranked sentence recovery ----------
def rank_sentences_by_ppr(per_sent_title: List[str], distinct_titles: List[str],
                          ppr_dist: np.ndarray,
                          hop1_scores: np.ndarray) -> List[int]:
    """Rank flat sentence indices by ppr[title_of(sent)].

    Ties broken by hop-1 dense score (stable secondary; helps disambiguate sentences
    from the same PPR-dominant title).
    """
    title_idx = {t: i for i, t in enumerate(distinct_titles)}
    n = len(per_sent_title)
    scores = np.zeros(n, dtype=np.float64)
    for k, t in enumerate(per_sent_title):
        if t in title_idx:
            scores[k] = ppr_dist[title_idx[t]]
        else:
            scores[k] = 0.0
    # Composite: ppr as primary (scale 1.0), hop-1 dense as tiebreak (small weight)
    composite = scores + 1e-6 * hop1_scores
    order = np.argsort(composite)[::-1].tolist()
    return [int(i) for i in order]


# ---------- per-seed run ----------
def run_seed(seed: int, bridge_queries: List[Dict]) -> Dict:
    print("[seed=%d] loading + sampling %d bridge queries..." % (
        seed, N_QUERIES_PER_SEED), flush=True)
    t0 = time.perf_counter()
    sample = sample_queries(bridge_queries, seed, N_QUERIES_PER_SEED)
    print("  sampled n=%d bridge queries" % len(sample), flush=True)

    # Collect all sentences across all sampled queries for a single bge encode pass
    all_texts: List[str] = []
    query_meta: List[Dict] = []
    for query in sample:
        titles, per_sent_title, sents = flatten_context(query)
        sentence_groups = list(query["context"]["sentences"])
        target = target_flat_indices(query, titles, sentence_groups)
        query_meta.append({
            "titles": titles,
            "sentence_groups": sentence_groups,
            "per_sent_title": per_sent_title,
            "sentences": sents,
            "target": target,
            "sf_titles": list(query["supporting_facts"]["title"]),
            "question": query["question"],
            "answer": query["answer"],
        })
        # Record sentence offsets so we can slice bge output back per query
    # Compute per-query offsets in the flat encode buffer
    offsets = []
    running = 0
    for qm in query_meta:
        offsets.append((running, running + len(qm["sentences"])))
        all_texts.extend(qm["sentences"])
        running += len(qm["sentences"])
    # Append queries at the end
    q_offset = running
    all_texts.extend([Q_INSTR + qm["question"] for qm in query_meta])

    print("  encoding %d texts with %s (bge)..." % (len(all_texts), BGE_MODEL),
          flush=True)
    t_enc = time.perf_counter()
    vecs = bge_encode_all(all_texts)
    print("  bge_encode elapsed=%.1fs" % (time.perf_counter() - t_enc), flush=True)

    # Split
    sent_vecs = vecs[:q_offset]
    q_vecs = vecs[q_offset:]

    # Build char-trigram encoder (Exp 1) — codebook depends on distinct titles per query
    # We rebuild per-query since KGs are per-query. That's cheap.

    # PPR walks
    rng = random.Random(seed + 9999)
    all_mass_sums: List[float] = []
    r_baseline: List[int] = []
    r_main: List[int] = []
    r_pos: List[int] = []
    r_neg: List[int] = []
    per_query_diag: List[Dict] = []
    kg_signal_ok_flags: List[bool] = []
    mean_degrees: List[float] = []

    for qi, qm in enumerate(query_meta):
        s0, s1 = offsets[qi]
        sent_matrix = sent_vecs[s0:s1]
        q_vec = q_vecs[qi]

        # Baseline hop-1 dense retrieval: top-K over ALL sentences in this query's context
        hop1_scores = sent_matrix @ q_vec  # (n_sents,)
        hop1_top_k = dense_top_k(q_vec, sent_matrix, PPR_TOP_K)
        target_set = set(qm["target"])
        # binary hit
        r_b = 1 if any(idx in target_set for idx in hop1_top_k) else 0
        r_baseline.append(r_b)

        # Build per-query KG from the raw HotpotQA context (titles + sentence_groups)
        distinct_titles, A_kg, n_edges, mean_deg = build_query_kg(
            qm["titles"], qm["sentence_groups"])
        mean_degrees.append(mean_deg)
        kg_signal_ok_flags.append(mean_deg >= KG_SIGNAL_FLOOR)

        # Char-trigram encoder on distinct titles (per-query codebook, Exp 1 style)
        enc, codebook = EXP1.build_entity_codebook(distinct_titles, N_DIM_TRIGRAM)

        # ARM_MAIN: entity extract from hop-1 chunks, seed PPR
        hop1_text = " ".join(qm["sentences"][j] for j in hop1_top_k)
        matched = EXP1.extract_matched_entities(
            hop1_text, enc, codebook, distinct_titles, COSINE_THRESH)
        if not matched:
            # Fallback: extract from query text itself
            matched = EXP1.extract_matched_entities(
                qm["question"], enc, codebook, distinct_titles, COSINE_THRESH)
        seed_main = EXP2.seed_from_entities(matched, distinct_titles)
        ppr_main, ms_main = EXP2.ppr_iterate(
            A_kg, seed_main, PPR_ALPHA, PPR_ITERS, MASS_CONSERVATION_TOL)
        all_mass_sums.extend(ms_main)
        ranked_main = rank_sentences_by_ppr(
            qm["per_sent_title"], distinct_titles, ppr_main, hop1_scores)
        r_m = 1 if any(idx in target_set for idx in ranked_main[:PPR_TOP_K]) else 0
        r_main.append(r_m)

        # ARM_POS_CTL: seed from FIRST supporting-facts title
        pos_seed_entity = qm["sf_titles"][0] if qm["sf_titles"] else None
        if pos_seed_entity in distinct_titles:
            seed_pos = EXP2.seed_from_entities([pos_seed_entity], distinct_titles)
        else:
            # Distractor mismatch — treat as uniform seed (defensive; will show up in POS_CTL rate)
            seed_pos = EXP2.seed_from_entities(distinct_titles, distinct_titles)
        ppr_pos, ms_pos = EXP2.ppr_iterate(
            A_kg, seed_pos, PPR_ALPHA, PPR_ITERS, MASS_CONSERVATION_TOL)
        all_mass_sums.extend(ms_pos)
        ranked_pos = rank_sentences_by_ppr(
            qm["per_sent_title"], distinct_titles, ppr_pos, hop1_scores)
        r_p = 1 if any(idx in target_set for idx in ranked_pos[:PPR_TOP_K]) else 0
        r_pos.append(r_p)

        # ARM_NEG_CTL: seed from random title NOT in supporting-facts titles
        sf_set = set(qm["sf_titles"])
        candidates = [t for t in distinct_titles if t not in sf_set]
        if candidates:
            neg_entity = rng.choice(candidates)
            seed_neg = EXP2.seed_from_entities([neg_entity], distinct_titles)
        else:
            # Extremely rare: all titles are supporting facts. Uniform fallback.
            neg_entity = "<UNIFORM_FALLBACK>"
            seed_neg = EXP2.seed_from_entities(distinct_titles, distinct_titles)
        ppr_neg, ms_neg = EXP2.ppr_iterate(
            A_kg, seed_neg, PPR_ALPHA, PPR_ITERS, MASS_CONSERVATION_TOL)
        all_mass_sums.extend(ms_neg)
        ranked_neg = rank_sentences_by_ppr(
            qm["per_sent_title"], distinct_titles, ppr_neg, hop1_scores)
        r_n = 1 if any(idx in target_set for idx in ranked_neg[:PPR_TOP_K]) else 0
        r_neg.append(r_n)

        per_query_diag.append({
            "qi": qi,
            "n_sents": len(qm["sentences"]),
            "n_titles_distinct": len(distinct_titles),
            "n_edges": n_edges,
            "mean_deg": round(mean_deg, 2),
            "target_flat_idx": qm["target"],
            "hop1_top_k": hop1_top_k,
            "matched_entities": matched,
            "pos_seed_entity": pos_seed_entity,
            "neg_seed_entity": neg_entity,
            "r_baseline": r_b,
            "r_main": r_m,
            "r_pos": r_p,
            "r_neg": r_n,
            "ranked_main_top5": ranked_main[:PPR_TOP_K],
            "sf_titles": qm["sf_titles"],
        })

    n = len(query_meta)
    if n == 0:
        return {"seed": seed, "n_queries": 0, "vacuous": True, "per_arm": {},
                "elapsed_s": time.perf_counter() - t0}

    def _rate(v):
        return sum(v) / len(v) if v else 0.0

    per_arm = {
        "ARM_HOP1_DENSE_ALONE_BASELINE": {
            "recall_at_k": _rate(r_baseline),
            "n_hits": sum(r_baseline), "n": n,
        },
        "ARM_MAIN_PPR_RECOVERED": {
            "recall_at_k": _rate(r_main),
            "n_hits": sum(r_main), "n": n,
        },
        "ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE": {
            "recall_at_k": _rate(r_pos),
            "n_hits": sum(r_pos), "n": n,
        },
        "ARM_NEG_CTL_PPR_FROM_RANDOM": {
            "recall_at_k": _rate(r_neg),
            "n_hits": sum(r_neg), "n": n,
        },
    }

    # MISSED-BY-HOP1 subset
    missed_idx = [i for i, r in enumerate(r_baseline) if r == 0]
    n_missed = len(missed_idx)
    if n_missed > 0:
        n_ppr_recovered = sum(r_main[i] for i in missed_idx)
        ppr_recovery_rate = n_ppr_recovered / n_missed
    else:
        ppr_recovery_rate = None

    # KG signal availability
    kg_signal_frac = (sum(kg_signal_ok_flags) / n) if n > 0 else 0.0
    kg_signal_ok = kg_signal_frac >= KG_SIGNAL_QUERY_FRAC_MIN

    # ARMS-DIFFER hashes on per-query hit vectors
    def _hash(vec):
        return hashlib.sha256("|".join(str(x) for x in vec).encode()).hexdigest()[:16]
    digests = {
        "ARM_HOP1_DENSE_ALONE_BASELINE": _hash(r_baseline),
        "ARM_MAIN_PPR_RECOVERED": _hash(r_main),
        "ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE": _hash(r_pos),
        "ARM_NEG_CTL_PPR_FROM_RANDOM": _hash(r_neg),
    }
    arm_vecs = {
        "ARM_HOP1_DENSE_ALONE_BASELINE": r_baseline,
        "ARM_MAIN_PPR_RECOVERED": r_main,
        "ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE": r_pos,
        "ARM_NEG_CTL_PPR_FROM_RANDOM": r_neg,
    }
    zero_arms = [name for name, v in arm_vecs.items() if sum(v) == 0]
    arms_differ_exempted = []
    for i in range(len(zero_arms)):
        for j in range(i + 1, len(zero_arms)):
            arms_differ_exempted.append(
                (zero_arms[i], zero_arms[j],
                 "both all-zero hit vectors (adverse regime)"))
    # Also allow BASELINE==MAIN collision when both mid-band identical (not a bug);
    # this is a legitimate case where PPR doesn't change hit-pattern.
    seen: Dict[str, str] = {}
    arms_differ_violations = []
    exempted_pairs = {frozenset([a, b]) for a, b, _ in arms_differ_exempted}
    for name, dig in digests.items():
        if dig in seen:
            other = seen[dig]
            if frozenset([name, other]) in exempted_pairs:
                continue
            arms_differ_violations.append((other, name, dig))
        else:
            seen[dig] = name

    # Mass conservation
    if all_mass_sums:
        max_dev = max(abs(m - 1.0) for m in all_mass_sums)
    else:
        max_dev = 0.0
    mass_ok = max_dev <= MASS_CONSERVATION_TOL

    return {
        "seed": seed,
        "n_queries": n,
        "n_missed_by_hop1": n_missed,
        "vacuous": False,
        "per_arm": per_arm,
        "ppr_recovery_rate": ppr_recovery_rate,
        "n_ppr_recovered_on_missed_subset": (
            sum(r_main[i] for i in missed_idx) if n_missed > 0 else 0),
        "arm_digests": digests,
        "arms_differ_violations": arms_differ_violations,
        "arms_differ_exempted": arms_differ_exempted,
        "per_query_diag": per_query_diag,
        "ppr_mass_max_deviation_from_1": max_dev,
        "ppr_mass_conservation_ok": mass_ok,
        "mean_edges_per_node_across_queries": round(
            float(np.mean(mean_degrees)) if mean_degrees else 0.0, 2),
        "kg_signal_query_frac_ok": kg_signal_frac,
        "kg_signal_ok": kg_signal_ok,
        "elapsed_s": time.perf_counter() - t0,
    }


# ---------- verdict ----------
def compute_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    # KG signal availability across all seeds
    active_seeds = [s for s in per_seed if not s.get("vacuous", False)]
    if not active_seeds:
        return ("HARD_FAIL",
                "HARD_FAIL_ALL_VACUOUS: no seeds returned non-vacuous results", {})

    kg_signal_all_ok = all(s.get("kg_signal_ok", False) for s in active_seeds)
    kg_signal_stats = [(s["seed"], s.get("kg_signal_query_frac_ok", 0.0),
                        s.get("mean_edges_per_node_across_queries", 0.0))
                       for s in active_seeds]
    if not kg_signal_all_ok:
        return ("HARD_FAIL",
                "HALT_KG_DATA_AVAILABILITY_FLOOR_BREACH: KG mean_edges_per_node < %.1f "
                "across >= 50%% of queries in at least one seed. Stats %s. "
                "Data problem (HotpotQA titles don't cross-reference enough for a "
                "graph-walk KG); NOT a mechanism failure. Escalate to Director to "
                "revisit KG construction (LLM-based OpenIE / bigger KG scope)." % (
                    KG_SIGNAL_FLOOR, kg_signal_stats), {})

    total_missed = sum(s.get("n_missed_by_hop1", 0) for s in active_seeds)
    if total_missed < 10:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_VACUOUS_SUBSET: total_missed_by_hop1=%d < 10 across seeds; "
                "baseline saturated on HotpotQA -- insufficient discriminator subset. "
                "META_RULE_K discriminator-fires floor breach." % total_missed, {})

    arm_names = ["ARM_HOP1_DENSE_ALONE_BASELINE", "ARM_MAIN_PPR_RECOVERED",
                 "ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE", "ARM_NEG_CTL_PPR_FROM_RANDOM"]
    per_arm_mean = {}
    for name in arm_names:
        th = 0
        tn = 0
        for s in active_seeds:
            th += s["per_arm"][name]["n_hits"]
            tn += s["per_arm"][name]["n"]
        per_arm_mean[name] = th / max(tn, 1)

    baseline = per_arm_mean["ARM_HOP1_DENSE_ALONE_BASELINE"]
    main = per_arm_mean["ARM_MAIN_PPR_RECOVERED"]
    pos = per_arm_mean["ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE"]
    neg = per_arm_mean["ARM_NEG_CTL_PPR_FROM_RANDOM"]

    total_recovered = 0
    total_missed_agg = 0
    for s in active_seeds:
        if s.get("n_missed_by_hop1", 0) == 0:
            continue
        total_recovered += s.get("n_ppr_recovered_on_missed_subset", 0)
        total_missed_agg += s["n_missed_by_hop1"]
    ppr_recovery_rate = total_recovered / max(total_missed_agg, 1)

    expected_units = 4 * len(active_seeds)
    actual_units = sum(len(s.get("per_arm", {})) for s in active_seeds)
    cardinality_ok = actual_units == expected_units
    arms_differ_ok = all(len(s.get("arms_differ_violations", [])) == 0
                        for s in active_seeds)
    mass_ok = all(s.get("ppr_mass_conservation_ok", True) for s in active_seeds)

    summary = ("baseline=%.3f | main=%.3f | pos_ctl=%.3f | neg_ctl=%.3f | "
               "ppr_recovery_rate=%.3f (%d/%d missed-by-hop1) | "
               "cardinality_ok=%s arms_differ_ok=%s mass_ok=%s kg_signal_ok=True" % (
                   baseline, main, pos, neg, ppr_recovery_rate,
                   total_recovered, total_missed_agg,
                   cardinality_ok, arms_differ_ok, mass_ok))

    if not cardinality_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected %d got %d. %s" % (
                    expected_units, actual_units, summary), per_arm_mean)
    if not arms_differ_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_META_RULE_AF: arms bit-identical. %s" % summary, per_arm_mean)
    if not mass_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_PPR_MASS_NONCONSERVATIVE: PPR primitive broken. %s" % summary,
                per_arm_mean)
    if pos < 0.95:
        return ("CONTROL_FAIL",
                "CONTROL_FAIL_POSITIVE: pos_ctl=%.3f < 0.95; PPR + chunk-scoring cannot "
                "recover supporting-facts sentence even when seeded from true bridge title. "
                "Regime extension (synthetic entities -> real Wikipedia titles) breaks the "
                "mechanism; do NOT trust MAIN. %s" % (pos, summary), per_arm_mean)
    if neg > 0.10:
        return ("CONTROL_FAIL",
                "CONTROL_FAIL_NEGATIVE: neg_ctl=%.3f > 0.10; random-title-seeded PPR is "
                "recovering supporting-facts too often -- HotpotQA context is by-construction "
                "dense enough that mass diffuses to all sentences; MAIN lift is confounded. "
                "%s" % (neg, summary), per_arm_mean)

    scale_note = ("SCALE-HONEST-TEST: HotpotQA context is a real Wikipedia-derived semantic "
                  "KG (10 titles per query, title-mention edges); RESULT IS REPRESENTATIVE "
                  "of the HippoRAG target regime unlike Exp 2's synthetic UUID KG.")

    if ppr_recovery_rate >= 0.50:
        return ("HARD_PASS",
                "HARD_PASS_PPR_BRIDGE_RECOVERY_SEMANTIC_KB: ppr_recovery_rate=%.3f >= 0.50 on "
                "missed-by-hop-1 subset (%d/%d recovered) on REAL Wikipedia-derived KG. "
                "Graph-walk is viable at semantic-KB scale; chain Exp 3 with confidence. "
                "%s %s" % (ppr_recovery_rate, total_recovered, total_missed_agg,
                          summary, scale_note), per_arm_mean)
    if ppr_recovery_rate < 0.15:
        return ("HARD_FAIL",
                "HARD_FAIL_PPR_BRIDGE_RECOVERY_SEMANTIC_KB: ppr_recovery_rate=%.3f < 0.15 on "
                "REAL Wikipedia-derived KG -- graph-walk approach is dead even with semantic "
                "signal (worse than Exp 2 synthetic floor 0.170). STRATEGIC DECISION: revive "
                "encoder-swap path as primary. %s %s" % (
                    ppr_recovery_rate, summary, scale_note), per_arm_mean)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_PPR_BRIDGE_RECOVERY_SEMANTIC_KB: ppr_recovery_rate=%.3f in "
            "[0.15, 0.50); partial signal on real Wikipedia-derived KG (BridgeRAG "
            "selective-effect pattern). CALL USER for direction: chain Exp 3 with modest "
            "expectations OR pivot to encoder-swap. %s %s" % (
                ppr_recovery_rate, summary, scale_note), per_arm_mean)


# ---------- selftest ----------
def selftest() -> None:
    """Formula selftest — verify HotpotQA loader + KG construction + verdict compute."""
    print("[selftest] running formula selftest...", flush=True)

    # 1. HotpotQA loader
    all_bridge = load_bridge_queries(HOTPOTQA_PATH)
    assert len(all_bridge) >= 100, "expected >= 100 bridge queries, got %d" % len(all_bridge)
    assert all(q.get("type") == "bridge" for q in all_bridge), "non-bridge slipped in"
    assert 500 <= len(all_bridge) <= 900, "unexpected bridge count %d (measured 807)" % len(all_bridge)

    # 2. Sample determinism
    s1 = sample_queries(all_bridge, 11, 5)
    s2 = sample_queries(all_bridge, 11, 5)
    assert [q["id"] for q in s1] == [q["id"] for q in s2], "sample not deterministic"
    s3 = sample_queries(all_bridge, 17, 5)
    assert [q["id"] for q in s1] != [q["id"] for q in s3], "seed doesn't vary sample"

    # 3. flatten_context
    q = s1[0]
    titles, per_sent_title, sents = flatten_context(q)
    assert len(sents) == sum(len(g) for g in q["context"]["sentences"]), \
        "flatten sentence count mismatch"
    assert len(per_sent_title) == len(sents), "per_sent_title/sents length mismatch"
    assert len(titles) == len(q["context"]["title"]), "titles length mismatch"

    # 4. target_flat_indices
    target = target_flat_indices(q, titles, list(q["context"]["sentences"]))
    # supporting_facts titles may or may not all be in context — target is at least 0-length
    assert isinstance(target, list) and all(0 <= i < len(sents) for i in target), \
        "target flat indices out of bounds: %s" % target

    # 5. build_query_kg — must return column-stochastic adjacency
    distinct_titles, A_kg, n_edges, mean_deg = build_query_kg(
        titles, list(q["context"]["sentences"]))
    assert A_kg.shape[0] == A_kg.shape[1] == len(distinct_titles), "A shape wrong"
    col_sums = A_kg.sum(axis=0)
    for cs in col_sums:
        assert cs == 0.0 or abs(cs - 1.0) < 1e-9, "col not stochastic: %.6f" % cs
    print("[selftest] sample KG stats: n_titles=%d n_edges=%d mean_deg=%.2f" % (
        len(distinct_titles), n_edges, mean_deg), flush=True)

    # 6. _title_regex sanity
    r = _title_regex("Ed Wood")
    assert r.search("Directed by Ed Wood in 1994") is not None, "regex missed exact match"
    assert r.search("Edwards was there") is None, "regex over-matched substring"
    assert r.search("ED WOOD") is not None, "regex not case-insensitive"

    # 7. _title_regex with regex metachar in title
    r2 = _title_regex("Star Wars: Episode I")
    assert r2.search("about Star Wars: Episode I here") is not None, "escaped meta"

    # 8. PPR primitives (delegated to Exp 2 module which has its own selftest)
    facts = [("A", "r", "B", "text"), ("B", "r", "C", "text")]
    A_tri = EXP2.build_undirected_adjacency(facts, ["A", "B", "C"])
    seed_v = EXP2.seed_from_entities(["A"], ["A", "B", "C"])
    x, ms = EXP2.ppr_iterate(A_tri, seed_v, 0.15, 5, 0.005)
    assert abs(x.sum() - 1.0) < 0.01, "PPR mass leaked"

    # 9. rank_sentences_by_ppr sanity
    per_sent_title = ["A", "A", "B", "C", "C"]
    distinct = ["A", "B", "C"]
    ppr_dist = np.array([0.6, 0.2, 0.2])
    hop1_scores = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    ranked = rank_sentences_by_ppr(per_sent_title, distinct, ppr_dist, hop1_scores)
    # A has highest ppr -> A sentences (indices 0,1) should be at top
    assert set(ranked[:2]) == {0, 1}, "PPR ranking wrong: %s" % ranked

    # 10. Verdict compute — HARD_PASS path
    fake = [{
        "seed": 0, "n_queries": 20, "n_missed_by_hop1": 15, "vacuous": False,
        "per_arm": {
            "ARM_HOP1_DENSE_ALONE_BASELINE": {"recall_at_k": 0.25, "n_hits": 5, "n": 20},
            "ARM_MAIN_PPR_RECOVERED": {"recall_at_k": 0.75, "n_hits": 15, "n": 20},
            "ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE": {"recall_at_k": 1.0, "n_hits": 20, "n": 20},
            "ARM_NEG_CTL_PPR_FROM_RANDOM": {"recall_at_k": 0.05, "n_hits": 1, "n": 20},
        },
        "arm_digests": {"ARM_HOP1_DENSE_ALONE_BASELINE": "a", "ARM_MAIN_PPR_RECOVERED": "b",
                        "ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE": "c", "ARM_NEG_CTL_PPR_FROM_RANDOM": "d"},
        "arms_differ_violations": [],
        "n_ppr_recovered_on_missed_subset": 10,  # 10/15 = 0.667
        "ppr_mass_conservation_ok": True,
        "kg_signal_ok": True, "kg_signal_query_frac_ok": 1.0,
        "mean_edges_per_node_across_queries": 3.0,
    }]
    v, msg, _ = compute_verdict(fake)
    assert v == "HARD_PASS", "verdict HARD_PASS fail: got %s\nmsg=%s" % (v, msg)

    # 11. HARD_FAIL (low recovery)
    fake2 = [{**fake[0], "n_ppr_recovered_on_missed_subset": 1}]  # 1/15 ~ 0.067
    v, msg, _ = compute_verdict(fake2)
    assert v == "HARD_FAIL" and "SEMANTIC_KB" in msg, "verdict low-recovery fail: %s" % v

    # 12. MIDDLE_BAND
    fake3 = [{**fake[0], "n_ppr_recovered_on_missed_subset": 5}]  # 5/15 = 0.333
    v, msg, _ = compute_verdict(fake3)
    assert v == "MIDDLE_BAND", "verdict mid fail: %s" % v

    # 13. CONTROL_FAIL_POSITIVE
    fake4 = [{**fake[0], "per_arm": {**fake[0]["per_arm"],
        "ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE": {"recall_at_k": 0.5, "n_hits": 10, "n": 20}}}]
    v, msg, _ = compute_verdict(fake4)
    assert v == "CONTROL_FAIL" and "POSITIVE" in msg, "pos ctl fail path wrong: %s" % v

    # 14. CONTROL_FAIL_NEGATIVE
    fake5 = [{**fake[0], "per_arm": {**fake[0]["per_arm"],
        "ARM_NEG_CTL_PPR_FROM_RANDOM": {"recall_at_k": 0.5, "n_hits": 10, "n": 20}}}]
    v, msg, _ = compute_verdict(fake5)
    assert v == "CONTROL_FAIL" and "NEGATIVE" in msg, "neg ctl fail path wrong: %s" % v

    # 15. HALT_KG_DATA_AVAILABILITY_FLOOR_BREACH
    fake6 = [{**fake[0], "kg_signal_ok": False, "kg_signal_query_frac_ok": 0.20,
              "mean_edges_per_node_across_queries": 0.5}]
    v, msg, _ = compute_verdict(fake6)
    assert v == "HARD_FAIL" and "KG_DATA_AVAILABILITY" in msg, "KG halt fail: %s" % v

    # 16. VACUOUS_SUBSET (baseline saturates)
    fake7 = [{**fake[0], "n_missed_by_hop1": 5}]  # < 10 total
    v, msg, _ = compute_verdict(fake7)
    assert v == "MIDDLE_BAND" and "VACUOUS_SUBSET" in msg, "vacuous path fail: %s" % v

    print("[selftest] PASS: exp2b_ppr_walk_wikipedia_semantic_kb primitives OK",
          flush=True)


# ---------- start marker + crash diag ----------
def _write_start_marker(out_dir: Path, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    final = out_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(out_dir: Path, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------- main ----------
def main() -> None:
    print("[config] anchor=%s mode=%s seeds=%s alpha=%.2f iters=%d top_k=%d "
          "n_per_seed=%d bge=%s" % (
              ANCHOR_NAME, RUN_MODE, SEEDS, PPR_ALPHA, PPR_ITERS, PPR_TOP_K,
              N_QUERIES_PER_SEED, BGE_MODEL), flush=True)

    selftest()
    if RUN_MODE == "self_test":
        print("[selftest] mode=self_test -- exit 0", flush=True)
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, expected_n_units=4 * len(SEEDS))

    print("[main] loading HotpotQA bridge queries...", flush=True)
    all_bridge = load_bridge_queries(HOTPOTQA_PATH)
    print("[main] loaded %d bridge queries" % len(all_bridge), flush=True)

    t_all = time.perf_counter()
    per_seed: List[Dict] = []
    for seed in SEEDS:
        result = run_seed(seed, all_bridge)
        per_seed.append(result)
        if result.get("vacuous", False):
            print("[seed=%d done] VACUOUS" % seed, flush=True)
        else:
            print("[seed=%d done] baseline=%.3f main=%.3f pos=%.3f neg=%.3f "
                  "recovery=%.3f (%d/%d) mean_deg=%.2f kg_ok=%s mass_ok=%s" % (
                      seed,
                      result["per_arm"]["ARM_HOP1_DENSE_ALONE_BASELINE"]["recall_at_k"],
                      result["per_arm"]["ARM_MAIN_PPR_RECOVERED"]["recall_at_k"],
                      result["per_arm"]["ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE"]["recall_at_k"],
                      result["per_arm"]["ARM_NEG_CTL_PPR_FROM_RANDOM"]["recall_at_k"],
                      result["ppr_recovery_rate"] if result["ppr_recovery_rate"] is not None else -1.0,
                      result.get("n_ppr_recovered_on_missed_subset", 0),
                      result.get("n_missed_by_hop1", 0),
                      result.get("mean_edges_per_node_across_queries", 0.0),
                      result.get("kg_signal_ok", False),
                      result.get("ppr_mass_conservation_ok", False)), flush=True)

    verdict, verdict_msg, per_arm_mean = compute_verdict(per_seed)
    elapsed = time.perf_counter() - t_all

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "n_queries_per_seed": N_QUERIES_PER_SEED,
        "bge_model": BGE_MODEL,
        "ppr_alpha": PPR_ALPHA,
        "ppr_iters": PPR_ITERS,
        "ppr_top_k": PPR_TOP_K,
        "cosine_thresh": COSINE_THRESH,
        "mass_conservation_tol": MASS_CONSERVATION_TOL,
        "kg_signal_floor": KG_SIGNAL_FLOOR,
        "kg_signal_query_frac_min": KG_SIGNAL_QUERY_FRAC_MIN,
        "per_seed": per_seed,
        "per_arm_mean_recall_at_k": per_arm_mean,
        "expected_n_units": 4 * len(SEEDS),
        "actual_n_units": sum(len(s.get("per_arm", {})) for s in per_seed
                              if not s.get("vacuous", False)),
        "cardinality_ok": (sum(len(s.get("per_arm", {})) for s in per_seed
                               if not s.get("vacuous", False))
                           == 4 * len([s for s in per_seed if not s.get("vacuous", False)])),
        "arms_differ_verified": all(
            len(s.get("arms_differ_violations", [])) == 0
            for s in per_seed if not s.get("vacuous", False)),
        "ppr_mass_conservation_verified": all(
            s.get("ppr_mass_conservation_ok", True)
            for s in per_seed if not s.get("vacuous", False)),
        "kg_signal_ok_all_seeds": all(
            s.get("kg_signal_ok", False) for s in per_seed
            if not s.get("vacuous", False)),
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "PPR recall@k is a rate, not a shift-noise measurement; "
                    "discriminator reachability via POS_CTL >= 0.95 / NEG_CTL <= 0.10 "
                    "span + KG mean_edges_per_node >= 1.0 availability floor.",
        "discriminator_reachability": True,
        "calibration_check": "default_ok_for_this_regime",
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)
    print("[VERDICT] %s" % verdict_msg, flush=True)
    print("[metrics] written to %s (elapsed=%.1fs)" % (final, elapsed), flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _out_dir = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out_dir, e)
        raise
