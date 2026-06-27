"""substrate_md_chunk_config_sweep_E3_v1 -- substrate-vs-MD config-sweep diagnostic.

Tests: chunk-config sweep over (chunk_size, overlap_fraction) on synthetic MD-shaped corpus.
For each config, compute substrate-KB recall@5 vs MD-grep baseline recall@5 vs random.
Picks Pareto-optimal config; informs Wave 4 v2 full ingest BEFORE 1M-atom commit.

ARMS (3 per config, 15 configs in full):
  ARM_SUBSTRATE_KB_QUERY      cosine-search over substrate KB
  ARM_MD_FILE_GREP_BASELINE   token-match-count ranking over raw MD chunks
  ARM_DIAG_RANDOM             random ranking (chance baseline)

PRE-REG BANDS (LOCKED at module init, PROSPECTIVE):
  HARD_PASS:  best_config substrate recall@5 >= 0.70 AND substrate >= MD AND
              ARM_DIAG_RANDOM <= 0.20
  MIDDLE_BAND: substrate in [0.50, 0.70] OR within 0.05 of MD at best config
  HARD_FAIL:  NO config achieves substrate >= 0.40 OR ALL configs underperform MD by >= 0.20
              OR ARM_DIAG_RANDOM >= 0.30 (chance too high)

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 15 configs * 3 arms * 3 seeds * 50 queries = 6750
  EXPECTED_N_UNITS_SMOKE = 4  configs * 3 arms * 2 seeds * 10 queries = 240

ASCII-only; self-contained.
Author: exp_dev 2026-06-27 (Opus 4.7 1M, Wave 3B TOP-2)
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import os
import re
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "substrate_md_chunk_config_sweep_E3_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED at module init
HP_SUBSTRATE_RECALL_MIN = 0.70
HP_DIAG_MAX = 0.20
MB_SUBSTRATE_LO = 0.50
MB_PARITY_MARGIN = 0.05
HF_SUBSTRATE_FLOOR = 0.40
HF_MD_GAP = 0.20
HF_DIAG_TOO_HIGH = 0.30

# Config sweep
CHUNK_SIZES = [64, 128, 256, 512, 1024]
OVERLAP_FRACS = [0.0, 0.25, 0.50]

if SELF_TEST_MODE:
    N_DIM = 512
    N_DOCS = 12
    DOC_TOKENS = 200
    N_QUERIES = 8
    SEEDS = [7]
    CFG_GRID = [(64, 0.0), (256, 0.25)]
elif RUN_MODE == "smoke":
    N_DIM = 1024
    N_DOCS = 40
    DOC_TOKENS = 600
    N_QUERIES = 10
    SEEDS = [7, 17]
    CFG_GRID = [(64, 0.0), (1024, 0.0), (256, 0.25), (1024, 0.50)]
else:
    N_DIM = 2048
    N_DOCS = 152  # matches existing substrate-KB v1 file count
    DOC_TOKENS = 1200
    N_QUERIES = 50
    SEEDS = [7, 17, 23]
    CFG_GRID = [(cs, of) for cs in CHUNK_SIZES for of in OVERLAP_FRACS]

EXPECTED_ARMS = ["substrate_kb_query", "md_file_grep_baseline", "diag_random"]
EXPECTED_N_UNITS = len(CFG_GRID) * len(EXPECTED_ARMS) * len(SEEDS) * N_QUERIES

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,docs=%d,doc_tokens=%d,queries=%d,seeds=%s,n_configs=%d,mode=%s,"
    "HP_subst>=%.2f,HP_diag<=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, N_DOCS, DOC_TOKENS, N_QUERIES, SEEDS, len(CFG_GRID),
    RUN_MODE, HP_SUBSTRATE_RECALL_MIN, HP_DIAG_MAX, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        m = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_md_chunk_config_sweep_E3",
        }
        if extra:
            m.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(m, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        s = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_md_chunk_config_sweep_E3_import_crash",
        }
        (out_dir / "metrics.json").write_text(json.dumps(s, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# ----------------------- char-trigram encoder -----------------------

def char_trigrams(s: str) -> List[str]:
    s = s.lower()
    if len(s) < 3:
        return [s]
    return [s[i:i + 3] for i in range(len(s) - 2)]


def hash_trigram_to_dim(tg: str, n_dim: int) -> Tuple[int, int]:
    """Hash trigram to (dim, sign)."""
    h = hashlib.md5(tg.encode("utf-8")).digest()
    dim = int.from_bytes(h[:4], "little") % n_dim
    sign = 1 if (h[4] & 1) else -1
    return dim, sign


def encode_chunk(text: str, n_dim: int) -> np.ndarray:
    v = np.zeros(n_dim, dtype=np.float32)
    for tg in char_trigrams(text):
        d, s = hash_trigram_to_dim(tg, n_dim)
        v[d] += s
    nrm = np.linalg.norm(v)
    if nrm > 1e-8:
        v = v / nrm
    return v


# ----------------------- synthetic corpus -----------------------

VOCAB = [
    "substrate", "encoder", "cortex", "hippocampus", "binding", "cleanup",
    "ultrametric", "refuse", "gate", "partition", "coverage", "metric",
    "discriminator", "preplay", "rollout", "schema", "kshot", "task",
    "vector", "permutation", "chunk", "config", "sweep", "recall",
    "precision", "baseline", "control", "diagnostic", "cardinality",
    "smoke", "verdict", "cell", "experiment", "dispatch", "queue",
    "fairness", "regime", "saturated", "hard", "pass", "fail", "middle",
    "band", "the", "of", "and", "to", "in", "for", "with", "on", "by",
    "is", "are", "this", "that", "from", "as", "at", "be", "we", "it",
]


def make_synthetic_corpus(n_docs: int, tokens_per_doc: int,
                           g: np.random.Generator) -> List[str]:
    """Make N_DOCS pseudo-documents, each ~tokens_per_doc words from VOCAB."""
    docs: List[str] = []
    for i in range(n_docs):
        # Each doc gets a "topic" = a small subset of vocab over-represented
        topic_idx = g.choice(len(VOCAB), size=5, replace=False)
        topic = [VOCAB[t] for t in topic_idx]
        tokens = []
        for _ in range(tokens_per_doc):
            if g.random() < 0.30:
                tokens.append(topic[int(g.integers(0, len(topic)))])
            else:
                tokens.append(VOCAB[int(g.integers(0, len(VOCAB)))])
        docs.append(" ".join(tokens))
    return docs


def make_query_set(docs: List[str], n_queries: int,
                    g: np.random.Generator) -> List[Tuple[str, int]]:
    """For each query, pick a target doc and form a 3-5-word excerpt as query.
    Returns (query, target_doc_idx)."""
    queries: List[Tuple[str, int]] = []
    for _ in range(n_queries):
        target = int(g.integers(0, len(docs)))
        tokens = docs[target].split()
        n_excerpt = int(g.integers(3, 6))
        if len(tokens) <= n_excerpt:
            qstr = " ".join(tokens)
        else:
            start = int(g.integers(0, len(tokens) - n_excerpt))
            qstr = " ".join(tokens[start:start + n_excerpt])
        queries.append((qstr, target))
    return queries


# ----------------------- chunking -----------------------

def chunk_doc_by_tokens(doc: str, chunk_size: int, overlap_frac: float) -> List[str]:
    tokens = doc.split()
    chunks: List[str] = []
    step = max(1, int(chunk_size * (1.0 - overlap_frac)))
    for start in range(0, len(tokens), step):
        end = start + chunk_size
        if start >= len(tokens):
            break
        chunks.append(" ".join(tokens[start:end]))
        if end >= len(tokens):
            break
    return chunks if chunks else [doc]


# ----------------------- retrieval arms -----------------------

def recall_at_k(ranked_doc_ids: List[int], target: int, k: int = 5) -> float:
    return 1.0 if target in ranked_doc_ids[:k] else 0.0


def arm_substrate_kb(chunks: List[str], chunk_doc_ids: List[int],
                      query: str, n_dim: int) -> List[int]:
    """Encode chunks + query via char-trigram; rank by cosine; return doc ids dedup."""
    qv = encode_chunk(query, n_dim)
    sims: List[Tuple[int, float]] = []
    for i, c in enumerate(chunks):
        cv = encode_chunk(c, n_dim)
        sim = float(np.dot(qv, cv))
        sims.append((i, sim))
    sims.sort(key=lambda x: -x[1])
    seen = set()
    ranked_docs: List[int] = []
    for i, _ in sims:
        d = chunk_doc_ids[i]
        if d not in seen:
            seen.add(d)
            ranked_docs.append(d)
    return ranked_docs


def arm_md_grep(chunks: List[str], chunk_doc_ids: List[int],
                 query: str) -> List[int]:
    """For each chunk, count substring matches of query tokens; aggregate to doc; rank."""
    q_tokens = query.lower().split()
    doc_scores: Dict[int, int] = {}
    for i, c in enumerate(chunks):
        c_low = c.lower()
        score = 0
        for t in q_tokens:
            score += c_low.count(t)
        d = chunk_doc_ids[i]
        if d not in doc_scores or doc_scores[d] < score:
            doc_scores[d] = max(doc_scores.get(d, 0), score)
    ranked = sorted(doc_scores.items(), key=lambda x: -x[1])
    return [d for d, _ in ranked]


def arm_random(n_docs: int, g: np.random.Generator) -> List[int]:
    return list(g.permutation(n_docs))


# ----------------------- per-seed runner -----------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    docs = make_synthetic_corpus(N_DOCS, DOC_TOKENS, g)
    # Queries fixed across configs for fairness
    qg = np.random.default_rng(seed + 1009)
    queries = make_query_set(docs, N_QUERIES, qg)

    per_config: Dict[str, Dict[str, Dict[str, float]]] = {}
    for (cs, of) in CFG_GRID:
        # Build chunks for this config
        chunks: List[str] = []
        chunk_doc_ids: List[int] = []
        for di, d in enumerate(docs):
            cks = chunk_doc_by_tokens(d, cs, of)
            for ck in cks:
                chunks.append(ck)
                chunk_doc_ids.append(di)

        # Per-arm recall@5
        substrate_recalls: List[float] = []
        md_recalls: List[float] = []
        random_recalls: List[float] = []
        for (qstr, target) in queries:
            r_sub = arm_substrate_kb(chunks, chunk_doc_ids, qstr, N_DIM)
            substrate_recalls.append(recall_at_k(r_sub, target, k=5))
            r_md = arm_md_grep(chunks, chunk_doc_ids, qstr)
            md_recalls.append(recall_at_k(r_md, target, k=5))
            r_rd = arm_random(N_DOCS, g)
            random_recalls.append(recall_at_k(r_rd, target, k=5))

        cfg_key = "cs%d_of%.2f" % (cs, of)
        per_config[cfg_key] = {
            "substrate_kb_query": {
                "recall_at_5": float(np.mean(substrate_recalls)),
                "n": len(substrate_recalls),
                "n_chunks": len(chunks),
            },
            "md_file_grep_baseline": {
                "recall_at_5": float(np.mean(md_recalls)),
                "n": len(md_recalls),
            },
            "diag_random": {
                "recall_at_5": float(np.mean(random_recalls)),
                "n": len(random_recalls),
            },
            "chunk_size": cs,
            "overlap_frac": of,
        }

    # Synthesize per_arm view collapsed across configs (max substrate at any config)
    best_cfg = None
    best_recall = -1.0
    for cfg_key, body in per_config.items():
        r = body["substrate_kb_query"]["recall_at_5"]
        if r > best_recall:
            best_recall = r
            best_cfg = cfg_key

    per_arm: Dict[str, Dict[str, float]] = {
        "substrate_kb_query_best_cfg": {
            "best_cfg": best_cfg,
            "best_recall_at_5": best_recall,
        },
    }

    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_config": per_config,
        "per_arm": per_arm,
    }


# ----------------------- aggregate + verdict -----------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials", "per_arm": {}}

    # Aggregate per-config x per-arm across seeds
    cfg_arm_means: Dict[str, Dict[str, List[float]]] = {}
    for s_key, body in per_seed.items():
        pc = body.get("per_config", {})
        for cfg_key, body2 in pc.items():
            if cfg_key not in cfg_arm_means:
                cfg_arm_means[cfg_key] = {arm: [] for arm in EXPECTED_ARMS}
            for arm in EXPECTED_ARMS:
                if arm in body2:
                    cfg_arm_means[cfg_key][arm].append(body2[arm]["recall_at_5"])

    cfg_arm_summary: Dict[str, Dict[str, float]] = {}
    best_cfg = None
    best_substrate = -1.0
    best_md = 0.0
    best_diag = 0.0
    worst_md_gap = -1e9
    any_above_floor = False
    diag_max = 0.0
    for cfg_key, arm_dict in cfg_arm_means.items():
        sub_mean = float(np.mean(arm_dict["substrate_kb_query"])) if arm_dict["substrate_kb_query"] else 0.0
        md_mean = float(np.mean(arm_dict["md_file_grep_baseline"])) if arm_dict["md_file_grep_baseline"] else 0.0
        dg_mean = float(np.mean(arm_dict["diag_random"])) if arm_dict["diag_random"] else 0.0
        cfg_arm_summary[cfg_key] = {
            "substrate_recall_5_mean": sub_mean,
            "md_recall_5_mean": md_mean,
            "diag_recall_5_mean": dg_mean,
        }
        if sub_mean >= HF_SUBSTRATE_FLOOR:
            any_above_floor = True
        if sub_mean > best_substrate:
            best_substrate = sub_mean
            best_md = md_mean
            best_diag = dg_mean
            best_cfg = cfg_key
        gap = md_mean - sub_mean
        if gap > worst_md_gap:
            worst_md_gap = gap
        if dg_mean > diag_max:
            diag_max = dg_mean

    # min_md_gap: min(MD - substrate) across configs; if any config has substrate >= MD, this is <= 0
    min_md_gap = min(cfg_arm_summary[c]["md_recall_5_mean"] - cfg_arm_summary[c]["substrate_recall_5_mean"]
                     for c in cfg_arm_summary) if cfg_arm_summary else 0.0

    verdict = "MIDDLE_BAND"
    if (best_substrate >= HP_SUBSTRATE_RECALL_MIN and
            best_substrate >= best_md and
            diag_max <= HP_DIAG_MAX):
        verdict = "HARD_PASS"
    elif ((not any_above_floor) or min_md_gap >= HF_MD_GAP or diag_max >= HF_DIAG_TOO_HIGH):
        verdict = "HARD_FAIL"
    elif (best_substrate >= MB_SUBSTRATE_LO or abs(best_substrate - best_md) <= MB_PARITY_MARGIN):
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s | best_cfg=%s subst=%.3f md=%.3f diag=%.3f | min_md_gap=%.3f diag_max=%.3f"
    ) % (verdict, best_cfg, best_substrate, best_md, best_diag, min_md_gap, diag_max)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": cfg_arm_summary,  # config x arm view
        "per_config_summary": cfg_arm_summary,
        "best_cfg": best_cfg,
        "best_substrate_recall": float(best_substrate),
        "best_md_recall_at_best_cfg": float(best_md),
        "min_md_gap": float(min_md_gap),
        "diag_max": float(diag_max),
        "n_seeds_complete": len(per_seed),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(per_seed) * len(CFG_GRID) * len(EXPECTED_ARMS) * N_QUERIES,
        "cardinality_ok": (len(per_seed) >= 2),
    }


# ----------------------- main -----------------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "n_configs": len(CFG_GRID)})

    print("[%s] mode=%s N=%d docs=%d tokens=%d queries=%d configs=%d seeds=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, N_DOCS, DOC_TOKENS, N_QUERIES,
        len(CFG_GRID), SEEDS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_config" in r
            assert len(r["per_config"]) == len(CFG_GRID)
            for cfg_key, body in r["per_config"].items():
                for arm in EXPECTED_ARMS:
                    assert arm in body, "missing arm %s in %s" % (arm, cfg_key)
            best_cfg = r["per_arm"]["substrate_kb_query_best_cfg"]["best_cfg"]
            best_recall = r["per_arm"]["substrate_kb_query_best_cfg"]["best_recall_at_5"]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: best_cfg=%s best_recall=%.3f" % (best_cfg, best_recall),
                                   extra={"_phase": "selftest_done",
                                          "selftest_configs": list(r["per_config"].keys()),
                                          "best_cfg": best_cfg, "best_recall": best_recall})
            print("[selftest] OK; best_cfg=%s best_recall=%.3f" % (best_cfg, best_recall), flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_md_chunk_config_sweep_E3"
    (out_dir / "metrics.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
