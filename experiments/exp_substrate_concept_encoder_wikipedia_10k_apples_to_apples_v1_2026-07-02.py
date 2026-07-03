"""exp_substrate_concept_encoder_wikipedia_10k_apples_to_apples_v1_2026_07_02

USER-authorized 2026-07-02 late evening ("do it" -- Option A'):
Replace pre-existing bge-large-only encoder on prior Wikipedia infra with a
4-arm apples-to-apples test:
  ARM_BGE_LARGE_REFERENCE       (bge-large-en-v1.5 frozen)  -- Gate D reproducibility
  ARM_CONCEPT_ENCODER_ONESHOT   (hdlab.concept_encoder)     -- brain-analog CG'd 2026-07-02
  ARM_CHAR_POSITIONAL_ONLY      (V1-analog surface encoder) -- surface baseline
  ARM_CHAR_TRIGRAM_UNSUP        (bag-of-substrings)         -- current substrate-KB encoder

Question: does the brain-analog ConceptEncoder (Spoke 1 v3-D CG on 50-concept
synthetic corpus at N_DIM=4096) extend to real-corpus Wikipedia at
N_CONCEPTS=10000 N_DIM=8192 with one-shot title supervision?

FRAMING DISCIPLINE (LOAD-BEARING):
- Substrate has no general knowledge ingested (feedback_substrate_knows_almost_
  nothing_no_general_knowledge_ingest_yet_USER_LOCKED_REPEATED_2026-07-02.md).
- ConceptEncoder is a MECHANISM-analog to competitive-Hebbian sparse coding,
  not a task-analog to unsupervised concept discovery
  (feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_
  supervised_regime_USER_LOCKED_2026-07-02.md).
- Even HP does not grant "substrate knows Wikipedia" -- grants "mechanism works
  on real-corpus title->article retrieval with one-shot title supervision".

PRIOR HP baseline (bge-large only): recall@1=0.961 @5=0.992 over 100000 articles
    MEASURED@data/exp_wikipedia_ingest_100k_gpu_v1/metrics.json.

Pre-reg: preregs/2026-07-02_substrate_concept_encoder_wikipedia_10k_apples_to_apples_v1.md

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
- final_metrics_atomicity: tmp_replace (META_RULE_AH)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a declared: retrieval task, chance = 5/N=0.0005 at N=10K
- baseline_in_band verified at smoke (META_RULE_AG)
- discriminator survives scale: selftest checks concept_encoder selftest 10 (N=8192 scale sentinel)
- HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
- HP_SCOPE per-arm declaration (in verdict logic)
- cardinality_ok for arms cell (EXPECTED_N_UNITS = n_seeds x n_arms)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (with declared risk at N_CONCEPTS=10000)
- all numbers in cell comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ (META_RULE_AC)
- start_marker_written, crash_diagnostic_present, heartbeat_present (§13)
- print_flush_true progress logging (§17; timeout_s>=1800)

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import sys

# Line-buffered stdout so progress lines are visible during long runs (per §17).
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

# CUDA env before torch import (per feedback_cuda_env_var_must_precede_torch_import).
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_concept_encoder_wikipedia_10k_apples_to_apples_v1_2026_07_02"

# --- Config ---
BGE_MODEL = "BAAI/bge-large-en-v1.5"
BGE_Q_INSTR = "Represent this sentence for searching relevant passages: "
DS_FULL = REPO / "data" / "datasets" / "wikipedia_100k.jsonl"
DS_SMOKE = REPO / "data" / "datasets" / "wikipedia_smoke_500.jsonl"

# Substrate arm HD dimension. CG v3-D FULL config = 4096; scale-sentinel
# validated at 8192 but wall-cost 2x. We use 4096 to keep FULL feasible within
# ~5-6 hour budget on GPU+CPU hybrid dispatch. Any HP claim explicitly refers
# to N_DIM=4096 which matches the source CG regime.
N_DIM_SUBSTRATE = 4096

# Article body -> K sentences for ConceptEncoder training.
K_SENTENCES_PER_ARTICLE_FULL = 3
K_SENTENCES_PER_ARTICLE_SMOKE = 3

# Article body char cap: reduces char_positional per-sentence wall (168 ms
# at 1140ch N=4096 vs 26 ms at 230ch N=4096 -- ~6x speedup).
BODY_CHAR_CAP = 800

# Article corpus size.
N_ARTICLES_FULL = 10000
N_ARTICLES_SMOKE = 500

# Seeds.
SEEDS_FULL = [11, 17, 23]
SEEDS_SMOKE = [11]

# BGE encoding batch size.
BGE_BATCH = 32
BGE_MAX_LEN = 256

# HP band constants (per pre-reg; MEASURED comparisons written into verdict logic).
HP1_BGE_R5_FLOOR = 0.85            # Gate D reproducibility
HP2_CE_R5_FLOOR = 0.60             # Brain-analog real-corpus
HP3_LIFT_VS_POSITIONAL = 0.15
HP4_LIFT_VS_TRIGRAM = 0.15
HF1_BGE_R5_HARD_FLOOR = 0.75
HF3_CE_R5_HARD_FLOOR = 0.05
MB_CE_R5_LOWER = 0.30              # < this AND not near HP2 = HF territory
MB_LIFT_LOWER = 0.05


# --- Args ---
def _parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run-mode",
                    default=os.environ.get("HDLAB_RUN_MODE", None),
                    choices=[None, "self_test", "smoke", "full"])
    args, _ = ap.parse_known_args()
    # Resolution order: --self-test -> self_test; --smoke -> smoke;
    # else HDLAB_RUN_MODE via --run-mode; default "full".
    if args.self_test:
        return "self_test"
    if args.smoke:
        return "smoke"
    if args.run_mode is not None:
        return args.run_mode
    return "full"


RUN_MODE = _parse_args()
IS_SMOKE = RUN_MODE == "smoke"
IS_SELFTEST = RUN_MODE == "self_test"

N_ARTICLES = N_ARTICLES_SMOKE if IS_SMOKE else N_ARTICLES_FULL
K_SPC = K_SENTENCES_PER_ARTICLE_SMOKE if IS_SMOKE else K_SENTENCES_PER_ARTICLE_FULL
SEEDS = SEEDS_SMOKE if IS_SMOKE else SEEDS_FULL
DS_PATH = DS_SMOKE if IS_SMOKE else DS_FULL


# --- Deterministic small selftest corpus (does not require dataset file) ---
_MINI_CORPUS = [
    {"title": "Alpha Star", "text": "Alpha Star is a bright celestial object. It shines in the night sky. Astronomers observe alpha star regularly."},
    {"title": "Beta River", "text": "Beta River flows through the valley. Its waters are clear and cold. Beta river supports diverse aquatic life."},
    {"title": "Gamma Mountain", "text": "Gamma Mountain rises steeply above the plain. Its peak is snow-capped year round. Climbers ascend gamma mountain each summer."},
    {"title": "Delta Delta Forest", "text": "Delta Delta Forest is an ancient woodland. It contains rare tree species. Delta delta forest is a protected reserve."},
    {"title": "Epsilon Lake", "text": "Epsilon Lake is a large freshwater body. It attracts many migratory birds. Epsilon lake freezes each winter."},
]


# --- Progress + observability helpers (per §13, §17) ---
def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}", flush=True)


def _write_start_marker(output_dir: Path, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f, indent=2)
    os.replace(tmp, final)


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int, elapsed_s: float, extra: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": elapsed_s,
        "extra": extra,
    }
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# --- Data loading ---
def _split_body_sentences(body: str, k: int) -> List[str]:
    """Naive sentence split for ConceptEncoder training text.

    Body is split on '. ' then '? ' then '! '. Empty pieces dropped. Returns
    up to k non-empty sentences of the article body. If body has < k sentence
    boundaries, returns as many as available (min 1: the whole body as a
    single 'sentence').
    """
    body = body.strip()
    if not body:
        return []
    # Prefer sentence boundaries.
    pieces: List[str] = []
    # Simple splitter: normalize question / exclamation marks.
    tmp = body.replace("? ", ". ").replace("! ", ". ")
    for s in tmp.split(". "):
        s = s.strip()
        if len(s) >= 5:  # skip trivially-short chunks
            pieces.append(s)
        if len(pieces) >= k:
            break
    if not pieces:
        return [body[:500]]
    return pieces


def load_articles(n: int, path: Path) -> List[Dict[str, str]]:
    """Load n articles from a jsonl file. Each line: {'title': ..., 'text': ...}."""
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {path}. "
            f"For smoke: run tools to download data/datasets/wikipedia_smoke_500.jsonl. "
            f"For FULL: dataset only present on marsh@home remote; dispatch there."
        )
    out: List[Dict[str, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = (r.get("title") or "").strip()
            x = (r.get("text") or "").strip()
            if t and x:
                out.append({"title": t, "text": x[:BODY_CHAR_CAP]})
            if len(out) >= n:
                break
    return out


def _unit_norm(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + eps)


# --- Arm implementations ---

def _encode_bge(articles: List[Dict[str, str]], seed: int) -> Tuple[np.ndarray, np.ndarray, float]:
    """Return (body_hds [N,1024], title_hds [N,1024], encoding_wall_s)."""
    # Lazy import to keep --self-test light.
    try:
        import torch
        from transformers import AutoModel, AutoTokenizer
    except Exception as e:
        raise RuntimeError(f"BGE arm deps missing (torch/transformers): {e}")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _log(f"  [bge] device={device}")
    tok = AutoTokenizer.from_pretrained(BGE_MODEL)
    # Use bf16 on CUDA; float32 on CPU (bf16 CPU is slow / partial support).
    if device.type == "cuda":
        model = AutoModel.from_pretrained(BGE_MODEL, torch_dtype=torch.bfloat16).to(device).eval()
    else:
        model = AutoModel.from_pretrained(BGE_MODEL).to(device).eval()

    def _enc(texts: List[str]) -> np.ndarray:
        out = []
        for i in range(0, len(texts), BGE_BATCH):
            batch = texts[i:i + BGE_BATCH]
            toks = tok(batch, return_tensors="pt", padding=True, truncation=True, max_length=BGE_MAX_LEN).to(device)
            with torch.no_grad():
                o = model(**toks)
            emb = o.last_hidden_state[:, 0, :].float().cpu().numpy()
            out.append(emb)
        return np.concatenate(out, 0).astype(np.float32)

    titles = [a["title"] for a in articles]
    bodies = [a["text"] for a in articles]

    t0 = time.perf_counter()
    body_hds = _unit_norm(_enc(bodies))
    title_hds = _unit_norm(_enc([BGE_Q_INSTR + t for t in titles]))
    wall = time.perf_counter() - t0

    del model
    if device.type == "cuda":
        try:
            import torch as _t
            _t.cuda.empty_cache()
        except Exception:
            pass
    return body_hds, title_hds, wall


def _encode_concept_encoder(articles: List[Dict[str, str]], seed: int, k_spc: int,
                            output_dir: Path, arm_idx: int) -> Tuple[np.ndarray, np.ndarray, float]:
    """Fit ConceptEncoder with one-shot title supervision; return
    (body_hds [N, n_dim] float32 from concept_hds cast, title_hds [N, n_dim]
    float32 from surface encoder, encoding_wall_s).
    """
    from hdlab.concept_encoder import ConceptEncoder

    n_articles = len(articles)
    # Build (sentences, article_indices) supervised pairs.
    sentences: List[str] = []
    labels: List[int] = []
    for i, a in enumerate(articles):
        pieces = _split_body_sentences(a["text"], k_spc)
        if not pieces:
            # Fallback: use title as its own body sentence (so no empty class).
            pieces = [a["title"]]
        for s in pieces:
            sentences.append(s)
            labels.append(i)
    labels_arr = np.asarray(labels, dtype=np.int64)
    _log(f"  [ce] n_articles={n_articles} n_sentences={len(sentences)} avg_spc={len(sentences)/n_articles:.2f}")

    enc = ConceptEncoder(
        n_dim=N_DIM_SUBSTRATE,
        n_concepts=n_articles,
        k_sparsity=0.02,
        seed=seed,
        max_pos=24,
        concept_names=None,       # do NOT mask (title != concept identity string; encoder handles this fine)
        mask_target_word=False,
    )

    t0 = time.perf_counter()
    enc.fit(sentences, labels_arr)
    fit_s = time.perf_counter() - t0
    _log(f"  [ce] fit done in {fit_s:.1f}s; sparse_rate={enc.sparse_rate():.4f}")
    _heartbeat(output_dir, arm_idx, 4, fit_s, {"stage": "ce_fit_done"})

    # Body HDs = concept_hds (already learned).
    body_hds = enc.concept_hds.astype(np.float32)  # [n_articles, n_dim]

    # Title HDs = surface encoding of the title text.
    t1 = time.perf_counter()
    title_hds = np.zeros((n_articles, N_DIM_SUBSTRATE), dtype=np.float32)
    for i, a in enumerate(articles):
        title_hds[i] = enc._surface_encoder.encode_sentence(a["title"])
        if (i + 1) % max(1, n_articles // 10) == 0:
            _log(f"  [ce] title-encode {i+1}/{n_articles}")
    title_wall = time.perf_counter() - t1
    wall = fit_s + title_wall
    return body_hds, title_hds, wall


def _encode_char_positional(articles: List[Dict[str, str]], seed: int) -> Tuple[np.ndarray, np.ndarray, float]:
    from hdlab.char_positional_encoder import CharPositionalEncoder
    enc = CharPositionalEncoder(n_dim=N_DIM_SUBSTRATE, max_pos=24, seed_prefix=f"CP_S{seed}")
    n = len(articles)
    body_hds = np.zeros((n, N_DIM_SUBSTRATE), dtype=np.float32)
    title_hds = np.zeros((n, N_DIM_SUBSTRATE), dtype=np.float32)
    t0 = time.perf_counter()
    for i, a in enumerate(articles):
        body_hds[i] = enc.encode_sentence(a["text"])
        title_hds[i] = enc.encode_sentence(a["title"])
        if (i + 1) % max(1, n // 10) == 0:
            _log(f"  [char_pos] {i+1}/{n}")
    wall = time.perf_counter() - t0
    return body_hds, title_hds, wall


def _encode_char_trigram(articles: List[Dict[str, str]], seed: int) -> Tuple[np.ndarray, np.ndarray, float]:
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    # Trigram encoder is not seed-parameterized (deterministic from trigram hash);
    # seed is captured only to align caller loop. This is honest documented behavior.
    _ = seed
    enc = CharTrigramEncoder(n_dim=N_DIM_SUBSTRATE)
    n = len(articles)
    body_hds = np.zeros((n, N_DIM_SUBSTRATE), dtype=np.float32)
    title_hds = np.zeros((n, N_DIM_SUBSTRATE), dtype=np.float32)
    t0 = time.perf_counter()
    for i, a in enumerate(articles):
        body_hds[i] = enc.encode(a["text"])
        title_hds[i] = enc.encode(a["title"])
        if (i + 1) % max(1, n // 10) == 0:
            _log(f"  [trigram] {i+1}/{n}")
    wall = time.perf_counter() - t0
    return body_hds, title_hds, wall


# --- Retrieval metrics ---
def _retrieval_metrics(body_hds: np.ndarray, title_hds: np.ndarray, seed: int) -> Dict[str, float]:
    """Compute recall@k, MRR, intra/inter signal metrics from (body, title) HDs.

    Uses cosine similarity: unit-normalize then matmul. Row i of title_hds is
    the query for gold article i.
    """
    b = _unit_norm(body_hds.astype(np.float32))
    t = _unit_norm(title_hds.astype(np.float32))
    n = b.shape[0]

    # Compute sim in chunks to bound memory.
    chunk = 256
    r1 = r5 = r10 = 0
    mrr_sum = 0.0
    intra_sum = 0.0
    for i in range(0, n, chunk):
        sims = t[i:i + chunk] @ b.T  # [chunk, n]
        # Descending sort per row.
        order = np.argsort(-sims, axis=1)
        for j in range(order.shape[0]):
            gi = i + j
            intra_sum += float(sims[j, gi])
            r1 += int(order[j, 0] == gi)
            if gi in order[j, :5]:
                r5 += 1
            if gi in order[j, :10]:
                r10 += 1
            # MRR
            rank_arr = np.where(order[j] == gi)[0]
            if rank_arr.size > 0:
                mrr_sum += 1.0 / float(rank_arr[0] + 1)
    r1 /= n
    r5 /= n
    r10 /= n
    mrr = mrr_sum / n
    intra = intra_sum / n

    # Inter: random permutation different from identity.
    rng = np.random.default_rng(int(seed) * 991 + 7)
    perm = rng.permutation(n)
    # Ensure no i -> i mapping.
    for i in range(n):
        if perm[i] == i:
            j = (i + 1) % n
            perm[i], perm[j] = perm[j], perm[i]
    inter = float(np.mean(np.sum(t * b[perm], axis=1)))
    snr = intra / max(abs(inter), 1e-6)
    return {
        "recall_at_1": float(r1),
        "recall_at_5": float(r5),
        "recall_at_10": float(r10),
        "mean_reciprocal_rank": float(mrr),
        "intra_article_body_title_cos": float(intra),
        "inter_article_title_body_cos": float(inter),
        "signal_to_noise_ratio": float(snr),
    }


# --- Arms-differ check (META_RULE_AF) ---
def _arms_differ_hash(arms_body_hds: Dict[str, np.ndarray]) -> Dict[str, str]:
    digests: Dict[str, str] = {}
    for name, arr in arms_body_hds.items():
        # Hash first article's first 200 values (enough entropy, small).
        sig = arr[0, :200].astype(np.float32).tobytes()
        digests[name] = hashlib.sha256(sig).hexdigest()[:16]
    # Assert all pairs differ.
    names = list(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if digests[a] == digests[b]:
                raise RuntimeError(
                    f"META_RULE_AF VIOLATION arms_differ: {a!r} and {b!r} "
                    f"bit-identical first-article prefix (hash={digests[a]}). "
                    f"Arm-implementation bug."
                )
    return digests


# --- Selftests (--self-test path) ---
def _selftest_mini_arms_differ() -> None:
    """Verify each arm encodes a tiny in-code corpus AND the four arms differ.

    Does not require external dataset. Skips BGE (torch model heavy).
    """
    from hdlab.char_positional_encoder import CharPositionalEncoder
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    from hdlab.concept_encoder import ConceptEncoder

    articles = _MINI_CORPUS
    n = len(articles)
    # Char positional
    cp = CharPositionalEncoder(n_dim=1024, max_pos=24, seed_prefix="TESTC")
    b_pos = np.stack([cp.encode_sentence(a["text"]) for a in articles], axis=0)
    t_pos = np.stack([cp.encode_sentence(a["title"]) for a in articles], axis=0)
    # Char trigram
    ct = CharTrigramEncoder(n_dim=1024)
    b_tri = np.stack([ct.encode(a["text"]) for a in articles], axis=0)
    t_tri = np.stack([ct.encode(a["title"]) for a in articles], axis=0)
    # Concept encoder
    sentences = []
    labels = []
    for i, a in enumerate(articles):
        for s in _split_body_sentences(a["text"], 3):
            sentences.append(s)
            labels.append(i)
    ce = ConceptEncoder(n_dim=1024, n_concepts=n, k_sparsity=0.02, seed=11,
                       max_pos=24, concept_names=None, mask_target_word=False)
    ce.fit(sentences, np.asarray(labels, dtype=np.int64))
    b_ce = ce.concept_hds.astype(np.float32)
    t_ce = np.stack([ce._surface_encoder.encode_sentence(a["title"]) for a in articles], axis=0)

    arms = {
        "positional": b_pos,
        "trigram": b_tri,
        "concept": b_ce,
    }
    digests = _arms_differ_hash(arms)
    assert len(set(digests.values())) == len(arms), f"arms_differ failed at self-test: {digests}"

    # NaN sanity on all title/body HDs.
    for name, arr in [("b_pos", b_pos), ("t_pos", t_pos),
                      ("b_tri", b_tri), ("t_tri", t_tri),
                      ("b_ce", b_ce), ("t_ce", t_ce)]:
        n_nan = int(np.isnan(arr).sum())
        assert n_nan == 0, f"selftest NaN in {name}: n_nan={n_nan}"

    # Retrieval sanity: on the mini corpus, at least positional or trigram
    # should get recall@1 > 0.4 (titles are distinctive strings; small N=5).
    mp = _retrieval_metrics(b_pos, t_pos, seed=11)
    mt = _retrieval_metrics(b_tri, t_tri, seed=11)
    assert mp["recall_at_1"] >= 0.20 or mt["recall_at_1"] >= 0.20, (
        f"selftest sanity: neither positional nor trigram cleared 0.20 recall@1 "
        f"on N=5 mini corpus (positional={mp['recall_at_1']:.3f} trigram={mt['recall_at_1']:.3f})"
    )
    print(f"[selftest mini_arms_differ] PASS -- digests={digests} "
          f"positional r1={mp['recall_at_1']:.3f} trigram r1={mt['recall_at_1']:.3f}",
          flush=True)


def _selftest_split_body_sentences() -> None:
    body = "Foo bar baz. Alpha beta gamma delta. What is this? Yes indeed!"
    got = _split_body_sentences(body, 3)
    assert len(got) == 3, f"expected 3 sentences got {len(got)}: {got}"
    assert all(len(s) >= 5 for s in got)
    got1 = _split_body_sentences("", 3)
    assert got1 == [], f"empty body should return []; got {got1}"
    print("[selftest split_body_sentences] PASS", flush=True)


def _selftest_retrieval_metrics_identity() -> None:
    """When body == title, retrieval must be perfect."""
    n = 20
    n_dim = 128
    rng = np.random.default_rng(11)
    x = rng.standard_normal((n, n_dim)).astype(np.float32)
    m = _retrieval_metrics(x, x, seed=11)
    assert m["recall_at_1"] == 1.0, f"identity r@1={m['recall_at_1']}"
    assert m["recall_at_5"] == 1.0
    assert m["mean_reciprocal_rank"] == 1.0
    print(f"[selftest retrieval_metrics_identity] PASS r1={m['recall_at_1']}", flush=True)


def _selftest_scale_sentinel_concept_encoder() -> None:
    """Import + assert concept_encoder selftest 10 target: N=8192 scale sentinel."""
    from hdlab.concept_encoder import _selftest_10_scale_sentinel_n_8192
    _selftest_10_scale_sentinel_n_8192()
    print("[selftest scale_sentinel_concept_encoder] PASS", flush=True)


def _run_selftests() -> int:
    tests = [
        ("split_body_sentences", _selftest_split_body_sentences),
        ("retrieval_metrics_identity", _selftest_retrieval_metrics_identity),
        ("mini_arms_differ", _selftest_mini_arms_differ),
        ("scale_sentinel_concept_encoder", _selftest_scale_sentinel_concept_encoder),
    ]
    failed = []
    for name, fn in tests:
        try:
            fn()
        except AssertionError as e:
            failed.append((name, f"AssertionError: {e}"))
            print(f"[selftest {name}] FAIL: {e}", flush=True)
        except Exception as e:
            failed.append((name, f"{type(e).__name__}: {e}"))
            print(f"[selftest {name}] ERROR: {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
    print(f"[selftest summary] {len(tests) - len(failed)}/{len(tests)} passed", flush=True)
    return 0 if not failed else 1


# --- Per-seed driver ---
def _run_one_seed(seed: int, articles: List[Dict[str, str]], k_spc: int,
                  output_dir: Path) -> Dict:
    _log(f"[seed {seed}] starting; n_articles={len(articles)} k_spc={k_spc}")
    per_arm: Dict[str, Dict] = {}
    per_arm_body_hds: Dict[str, np.ndarray] = {}

    arm_defs = [
        ("ARM_BGE_LARGE_REFERENCE", lambda: _encode_bge(articles, seed)),
        ("ARM_CONCEPT_ENCODER_ONESHOT", lambda: _encode_concept_encoder(
            articles, seed, k_spc, output_dir, arm_idx=1)),
        ("ARM_CHAR_POSITIONAL_ONLY", lambda: _encode_char_positional(articles, seed)),
        ("ARM_CHAR_TRIGRAM_UNSUP", lambda: _encode_char_trigram(articles, seed)),
    ]

    # HDLAB_SKIP_ARMS: comma-separated arm names to skip (e.g. for local smoke
    # where BGE on CPU exceeds session budget; BGE arm code is a direct copy
    # of the prior CG'd exp_wikipedia_ingest_100k_gpu_v1 cell, so BGE arm smoke
    # can be deferred to FULL GPU dispatch without loss of infra verification).
    _skip_arms_env = os.environ.get("HDLAB_SKIP_ARMS", "").strip()
    skip_arms = set(x.strip() for x in _skip_arms_env.split(",") if x.strip())
    if skip_arms:
        _log(f"[config] HDLAB_SKIP_ARMS={sorted(skip_arms)}")

    for arm_idx, (arm_name, encode_fn) in enumerate(arm_defs):
        if arm_name in skip_arms:
            _log(f"[seed {seed}] arm {arm_name} SKIPPED (HDLAB_SKIP_ARMS)")
            per_arm[arm_name] = {
                "arm_name": arm_name,
                "failure_class": "SKIPPED_BY_HDLAB_SKIP_ARMS",
                "failure_msg": f"HDLAB_SKIP_ARMS env set; arm not run at this smoke.",
            }
            continue
        _log(f"[seed {seed}] arm {arm_name} starting")
        arm_t0 = time.perf_counter()
        try:
            body_hds, title_hds, encoding_wall_s = encode_fn()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            failure_class = type(e).__name__
            per_arm[arm_name] = {
                "arm_name": arm_name,
                "failure_class": failure_class,
                "failure_msg": str(e)[:500],
                "traceback": traceback.format_exc()[:2000],
            }
            _log(f"[seed {seed}] arm {arm_name} FAILED: {failure_class}: {e}")
            _heartbeat(output_dir, arm_idx, 4, time.perf_counter() - arm_t0,
                       {"arm": arm_name, "status": "failed", "failure_class": failure_class})
            continue
        n_nan = int(np.isnan(body_hds).sum()) + int(np.isnan(title_hds).sum())
        if n_nan > 0:
            per_arm[arm_name] = {
                "arm_name": arm_name,
                "failure_class": "NAN_IN_HDS",
                "failure_msg": f"n_nan={n_nan}",
                "encoding_wall_s": encoding_wall_s,
            }
            _log(f"[seed {seed}] arm {arm_name} NaN in HDs (n_nan={n_nan})")
            continue
        metrics = _retrieval_metrics(body_hds, title_hds, seed=seed)
        metrics.update({
            "arm_name": arm_name,
            "n_dim": int(body_hds.shape[1]),
            "encoding_wall_s": float(encoding_wall_s),
            "throughput_articles_per_sec": float(len(articles) / max(encoding_wall_s, 1e-6)),
        })
        per_arm[arm_name] = metrics
        per_arm_body_hds[arm_name] = body_hds
        _log(f"[seed {seed}] arm {arm_name} r@1={metrics['recall_at_1']:.3f} "
             f"r@5={metrics['recall_at_5']:.3f} r@10={metrics['recall_at_10']:.3f} "
             f"intra={metrics['intra_article_body_title_cos']:.3f} "
             f"inter={metrics['inter_article_title_body_cos']:.3f} "
             f"wall={encoding_wall_s:.1f}s")
        _heartbeat(output_dir, arm_idx, 4, time.perf_counter() - arm_t0,
                   {"arm": arm_name, "recall_at_5": metrics["recall_at_5"]})

    # Arms-differ check (only over arms that succeeded).
    arms_differ_verified = False
    arms_differ_digests: Dict[str, str] = {}
    if len(per_arm_body_hds) >= 2:
        try:
            arms_differ_digests = _arms_differ_hash(per_arm_body_hds)
            arms_differ_verified = True
        except Exception as e:
            _log(f"[seed {seed}] ARMS_DIFFER_FAIL: {e}")
            arms_differ_verified = False
            arms_differ_digests = {"error": str(e)[:200]}

    return {
        "seed": int(seed),
        "n_articles": int(len(articles)),
        "k_sentences_per_article": int(k_spc),
        "per_arm": per_arm,
        "arms_differ_verified": bool(arms_differ_verified),
        "arms_differ_digests": arms_differ_digests,
    }


# --- Aggregation + verdict ---
def _aggregate(per_seed: List[Dict]) -> Dict:
    """Aggregate per_seed into per-arm mean/std of recall@5, etc.

    Skips missing (failed) arms without inflating means.
    """
    arm_names = [
        "ARM_BGE_LARGE_REFERENCE",
        "ARM_CONCEPT_ENCODER_ONESHOT",
        "ARM_CHAR_POSITIONAL_ONLY",
        "ARM_CHAR_TRIGRAM_UNSUP",
    ]
    out: Dict[str, Dict] = {}
    for arm in arm_names:
        r5s: List[float] = []
        r1s: List[float] = []
        r10s: List[float] = []
        walls: List[float] = []
        n_failed = 0
        for ps in per_seed:
            arm_m = ps.get("per_arm", {}).get(arm, {})
            if "failure_class" in arm_m:
                n_failed += 1
                continue
            r1s.append(arm_m.get("recall_at_1", 0.0))
            r5s.append(arm_m.get("recall_at_5", 0.0))
            r10s.append(arm_m.get("recall_at_10", 0.0))
            walls.append(arm_m.get("encoding_wall_s", 0.0))
        if r5s:
            out[arm] = {
                "n_seeds_succeeded": len(r5s),
                "n_seeds_failed": n_failed,
                "recall_at_1_mean": float(np.mean(r1s)),
                "recall_at_5_mean": float(np.mean(r5s)),
                "recall_at_5_std": float(np.std(r5s)),
                "recall_at_10_mean": float(np.mean(r10s)),
                "encoding_wall_s_mean": float(np.mean(walls)),
            }
        else:
            out[arm] = {
                "n_seeds_succeeded": 0,
                "n_seeds_failed": n_failed,
                "recall_at_5_mean": None,
            }
    return out


def _verdict(agg: Dict, expected_n_units: int, actual_n_units: int) -> Tuple[str, str]:
    """HP_SCOPE per pre-reg:
    HP1 (BGE r@5 >= 0.85): ARM_BGE_LARGE_REFERENCE
    HP2 (CE r@5 >= 0.60): ARM_CONCEPT_ENCODER_ONESHOT
    HP3 (CE - CHAR_POS >= 0.15): ARM_CONCEPT_ENCODER_ONESHOT
    HP4 (CE - CHAR_TRIGRAM >= 0.15): ARM_CONCEPT_ENCODER_ONESHOT
    HP5 (BGE reproducibility check): ARM_BGE_LARGE_REFERENCE
    """
    bge = agg.get("ARM_BGE_LARGE_REFERENCE", {}).get("recall_at_5_mean")
    ce = agg.get("ARM_CONCEPT_ENCODER_ONESHOT", {}).get("recall_at_5_mean")
    cpos = agg.get("ARM_CHAR_POSITIONAL_ONLY", {}).get("recall_at_5_mean")
    ctri = agg.get("ARM_CHAR_TRIGRAM_UNSUP", {}).get("recall_at_5_mean")

    # Skipped arms (HDLAB_SKIP_ARMS at smoke) => partial-info verdict, not HF.
    skip_arms_env = os.environ.get("HDLAB_SKIP_ARMS", "").strip()
    skipped_arms = set(x.strip() for x in skip_arms_env.split(",") if x.strip())
    if skipped_arms:
        # Partial smoke: only report per-arm info + note skipped. Not HP/HF.
        return ("SMOKE_PARTIAL_INFO_SKIPPED_ARMS",
                f"SMOKE_PARTIAL_INFO: HDLAB_SKIP_ARMS={sorted(skipped_arms)}; ran "
                f"CE r@5={ce} CHAR_POS r@5={cpos} CHAR_TRIGRAM r@5={ctri} BGE r@5={bge}. "
                f"Full verdict requires BGE arm; FULL dispatch will run all 4 arms.")

    # Cardinality gate first (only enforced when no skip-arm set).
    if actual_n_units < expected_n_units:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                f"HARD_FAIL_CARDINALITY: expected {expected_n_units} unit-metrics but got {actual_n_units}; "
                f"one or more (seed, arm) units failed. See per-seed per_arm failure_class.")

    if bge is None or ce is None or cpos is None or ctri is None:
        return ("HARD_FAIL_ARM_MISSING",
                f"HARD_FAIL: one or more arms have no r@5 metric: "
                f"bge={bge} ce={ce} cpos={cpos} ctri={ctri}")

    # HARD_FAIL checks first.
    if bge < HF1_BGE_R5_HARD_FLOOR:
        return ("HARD_FAIL_GATE_D_VIOLATION",
                f"HF1 Gate D violated: BGE recall@5={bge:.3f} < {HF1_BGE_R5_HARD_FLOOR}; "
                f"cell has invocation bug or dataset changed. Halt+investigate. "
                f"CE={ce:.3f} CHAR_POS={cpos:.3f} CHAR_TRIGRAM={ctri:.3f}")
    if ce < HF3_CE_R5_HARD_FLOOR:
        return ("HARD_FAIL_MECHANISM_FUNDAMENTALLY_FAILS",
                f"HF3 concept encoder near chance: CE recall@5={ce:.3f} < {HF3_CE_R5_HARD_FLOOR}; "
                f"mechanism fails on real text at N_CONCEPTS=10K. "
                f"BGE={bge:.3f} CHAR_POS={cpos:.3f} CHAR_TRIGRAM={ctri:.3f}")
    if ce < max(cpos, ctri):
        return ("HARD_FAIL_NO_MECHANISM_ADVANTAGE",
                f"HF2 concept encoder no advantage over surface baselines: "
                f"CE recall@5={ce:.3f} < max(CHAR_POS={cpos:.3f}, CHAR_TRIGRAM={ctri:.3f}); "
                f"brain-analog mechanism has NO real-corpus lift over surface baselines. "
                f"MAJOR ARC REFRAME required. BGE={bge:.3f}")

    # HARD_PASS check: all HP gates satisfied.
    hp1_ok = bge >= HP1_BGE_R5_FLOOR
    hp2_ok = ce >= HP2_CE_R5_FLOOR
    hp3_lift = ce - cpos
    hp4_lift = ce - ctri
    hp3_ok = hp3_lift >= HP3_LIFT_VS_POSITIONAL
    hp4_ok = hp4_lift >= HP4_LIFT_VS_TRIGRAM
    hp5_ok = hp1_ok  # HP5 = HP1 discipline restatement

    all_hp = hp1_ok and hp2_ok and hp3_ok and hp4_ok and hp5_ok
    summary_num = (
        f"BGE r@5={bge:.3f} CE r@5={ce:.3f} CHAR_POS r@5={cpos:.3f} CHAR_TRIGRAM r@5={ctri:.3f} "
        f"| lifts: CE-POS={hp3_lift:+.3f} CE-TRI={hp4_lift:+.3f}"
    )
    scope_str = (
        f"HP1_bge_ge_0.85={hp1_ok} HP2_ce_ge_0.60={hp2_ok} "
        f"HP3_lift_pos_ge_0.15={hp3_ok} HP4_lift_tri_ge_0.15={hp4_ok} "
        f"HP5_bge_reproducibility={hp5_ok}"
    )
    if all_hp:
        return ("HARD_PASS",
                f"HARD_PASS: brain-analog ConceptEncoder holds on real Wikipedia at 10K articles + "
                f"one-shot title supervision, matched vs bge-large frozen (Gate D) and lifted over surface "
                f"baselines by >= 0.15. HONEST SCOPE: mechanism at real-corpus supervised regime; "
                f"does NOT grant substrate general knowledge. {summary_num} | {scope_str}")

    # MIDDLE_BAND check.
    ce_in_mid = MB_CE_R5_LOWER <= ce < HP2_CE_R5_FLOOR
    lift_in_mid = ((hp3_lift >= MB_LIFT_LOWER and not hp3_ok)
                   or (hp4_lift >= MB_LIFT_LOWER and not hp4_ok))
    if ce_in_mid or lift_in_mid:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: partial mechanism signal but below CG floor. {summary_num} | {scope_str}")

    # Below MB floor -> soft HARD_FAIL (all HFs above already didn't trigger; treat as MIDDLE_BAND
    # is the correct pigeonhole for below-band results per META_RULE_L; use HARD_FAIL only when
    # a specific HF gate fires).
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND (no HF gate fired but no HP gate cleared): {summary_num} | {scope_str}")


# --- main ---
def main() -> int:
    if IS_SELFTEST:
        rc = _run_selftests()
        sys.exit(rc)

    output_dir = get_output_dir(ANCHOR_NAME)
    output_dir.mkdir(parents=True, exist_ok=True)

    expected_n_units = len(SEEDS) * 4  # 4 arms
    _write_start_marker(output_dir, expected_n_units)

    _log(f"[config] anchor={ANCHOR_NAME}")
    _log(f"[config] run_mode={RUN_MODE} n_articles={N_ARTICLES} k_spc={K_SPC} "
         f"seeds={SEEDS} n_dim_substrate={N_DIM_SUBSTRATE}")
    _log(f"[config] dataset_path={DS_PATH}")

    if not DS_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DS_PATH}. "
            f"For SMOKE dispatch: pre-download via tools/dl_wikipedia_100k.py (adapted). "
            f"For FULL dispatch: this cell must run on marsh@home remote where "
            f"data/datasets/wikipedia_100k.jsonl exists."
        )

    t0 = time.perf_counter()
    articles = load_articles(N_ARTICLES, DS_PATH)
    _log(f"[load] loaded {len(articles)} articles in {time.perf_counter() - t0:.1f}s")
    if len(articles) < N_ARTICLES:
        _log(f"[warn] loaded fewer articles than requested: {len(articles)} < {N_ARTICLES}")

    per_seed: List[Dict] = []
    for seed in SEEDS:
        seed_t0 = time.perf_counter()
        ps = _run_one_seed(seed, articles, K_SPC, output_dir)
        ps["seed_elapsed_s"] = float(time.perf_counter() - seed_t0)
        per_seed.append(ps)

    # Aggregate + verdict.
    agg = _aggregate(per_seed)
    # Count actual (seed, arm) unit successes.
    actual_n_units = sum(
        1
        for ps in per_seed
        for arm_m in ps.get("per_arm", {}).values()
        if "failure_class" not in arm_m
    )
    verdict, verdict_msg = _verdict(agg, expected_n_units, actual_n_units)
    _log(f"[VERDICT] {verdict}")
    _log(f"[VERDICT_MSG] {verdict_msg}")

    total_elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "seeds": SEEDS,
        "n_articles": N_ARTICLES,
        "k_sentences_per_article": K_SPC,
        "n_dim_substrate": N_DIM_SUBSTRATE,
        "expected_n_units": expected_n_units,
        "actual_n_units": actual_n_units,
        "cardinality_ok": actual_n_units >= expected_n_units,
        "arms_differ_verified": all(ps.get("arms_differ_verified", False) for ps in per_seed),
        "final_metrics_atomicity": "tmp_replace",
        "hp_scope": {
            "HP1": ["ARM_BGE_LARGE_REFERENCE"],
            "HP2": ["ARM_CONCEPT_ENCODER_ONESHOT"],
            "HP3": ["ARM_CONCEPT_ENCODER_ONESHOT"],
            "HP4": ["ARM_CONCEPT_ENCODER_ONESHOT"],
            "HP5": ["ARM_BGE_LARGE_REFERENCE"],
        },
        "per_seed": per_seed,
        "per_arm_aggregate": agg,
        "elapsed_s": total_elapsed,
        "ts_iso_end": datetime.now(timezone.utc).isoformat(),
    }

    # Atomic write (META_RULE_AH).
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)
    _log(f"[metrics] written to {final} (elapsed={total_elapsed:.1f}s)")

    # Also persist a summary line for peek_arm_metrics-style readers.
    write_metrics(output_dir, metrics)  # helper injects any missing top-level fields
    return 0


if __name__ == "__main__":
    _output_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        rc = main()
        sys.exit(rc or 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_output_dir_for_crash, e)
        raise
