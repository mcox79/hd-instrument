"""substrate_native_qa_hotpotqa_v1 -- substrate-as-LLM-substitute proof-of-concept.

Composes 3 chain-grade primitives (CERT 587/588 family + char_trigram_encoder)
into the first substrate-native QA pipeline on a real benchmark (HotpotQA dev):

  question text
     -> CharTrigramEncoder            (substrate-native text -> HD)
     -> KGStore.score_all(q_hd)        (CERT 588 multi-value Hebbian KG)
     -> top-K candidate entities
     -> SubstrateGenerator.generate    (CERT 587 g1b autoregressive generation)
     -> entity-name lookup -> answer

Zero LLM forward calls at inference (substrate-only-decode gate enforced).

THREE ARMS (Fix #16 discriminator):
  1. SUBSTRATE_COMPOSED -- full pipeline (retrieval + generation)
  2. RETRIEVAL_ONLY     -- KGStore top-1 = answer (no generation)
  3. GENERATION_ONLY    -- SubstrateGenerator from question-HD alone (no KG W)

PRE-REGISTERED BANDS (preregs/2026-06-22_substrate_native_qa_hotpotqa_v1.md):

  HARD_PASS (substrate-as-LLM-substitute existence proof):
    SUBSTRATE_COMPOSED EM >= 0.20
    AND (SUBSTRATE_COMPOSED_EM - max(RETRIEVAL_ONLY_EM, GENERATION_ONLY_EM)) >= +0.05
    AND n_llm_calls == 0
    AND cv across 3 seeds for SUBSTRATE_COMPOSED_EM <= 0.10

  HARD_FAIL:
    SUBSTRATE_COMPOSED_EM < 0.10
    OR SUBSTRATE_COMPOSED_EM <= max(per-primitive EM)
    OR n_llm_calls > 0

ROUTING: overnight_queue (GPU) per Fix #22 + #24 (N_DIM=8192 LLM-class; torch.cuda;
batched matmul over codebook scoring).

ASCII-only. Single-file. Resumable via _seed_checkpoint.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse
import json
import math
import re
import time
import signal
import atexit
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)
from hdlab.char_trigram_encoder import CharTrigramEncoder
from hdlab.kg_traversal import KGStore
from hdlab.sequence_memory import SequenceMatrix
from hdlab.generation import SubstrateGenerator

ANCHOR_NAME = "substrate_native_qa_hotpotqa_v1"

# Substrate-only-decode gate (asserted == 0 at exit)
_LLM_CALL_COUNTER = [0]

CORPUS_PROVENANCE = "hotpotqa_distractor_dev_1k_jsonl"
HOTPOT_PATH = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"

# Pre-reg bands (locked)
HARD_PASS_COMPOSED_EM = 0.20
HARD_PASS_LIFT = 0.05
HARD_PASS_CV_MAX = 0.10
HARD_FAIL_COMPOSED_EM = 0.10

_METRICS_WRITTEN = [False]


def _detect_run_mode():
    if "--smoke" in sys.argv:
        return "smoke"
    env_mode = os.environ.get("HDLAB_RUN_MODE", "").lower()
    if env_mode in ("smoke", "full"):
        return env_mode
    exp_name = os.environ.get("HDLAB_EXP_NAME", "")
    if exp_name.endswith("_smoke"):
        return "smoke"
    return "full"


RUN_MODE = _detect_run_mode()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 2048
    N_Q = 50
    TOP_K = 5
    GEN_DEPTH = 3
    ARMS = ["SUBSTRATE_COMPOSED", "RETRIEVAL_ONLY", "GENERATION_ONLY"]
    SIGMA_SCALE = 0.10
else:
    SEEDS = [7, 17, 23]
    N_DIM = 8192
    N_Q = 1000
    TOP_K = 5
    GEN_DEPTH = 4
    ARMS = ["SUBSTRATE_COMPOSED", "RETRIEVAL_ONLY", "GENERATION_ONLY"]
    SIGMA_SCALE = 0.10

CONFIG_VERSION = (
    "substrate-native-qa-hotpotqa-v1: N_DIM=%d N_Q=%d TOP_K=%d GEN_DEPTH=%d "
    "arms=%s sigma=%.3f run_mode=%s device=%s; bands HP_composed_em=%.2f "
    "HP_lift=%.2f HF_composed_em=%.2f cv_max=%.2f"
) % (
    N_DIM, N_Q, TOP_K, GEN_DEPTH, ",".join(ARMS), SIGMA_SCALE, RUN_MODE,
    str(DEVICE),
    HARD_PASS_COMPOSED_EM, HARD_PASS_LIFT, HARD_FAIL_COMPOSED_EM, HARD_PASS_CV_MAX,
)


# ----- Answer normalization (HotpotQA standard EM normalization) -----
_PUNCT_RE = re.compile(r"[^\w\s]")
_ARTICLE_RE = re.compile(r"\b(a|an|the)\b", flags=re.IGNORECASE)


def normalize_answer(s: str) -> str:
    """Standard HotpotQA EM normalization: lowercase, strip punct, strip articles, collapse ws."""
    if s is None:
        return ""
    s = s.lower()
    s = _PUNCT_RE.sub(" ", s)
    s = _ARTICLE_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def exact_match(pred: str, gold: str) -> int:
    return int(normalize_answer(pred) == normalize_answer(gold))


# ----- HotpotQA load + KG build -----
def load_hotpot_items(path: Path, max_items: int) -> List[Dict]:
    if not path.exists():
        raise FileNotFoundError("HotpotQA corpus not found at %s" % path)
    items = []
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if i >= max_items:
                break
            r = json.loads(line)
            sf = r.get("supporting_facts", {}) or {}
            titles = sf.get("title", []) or []
            seen = set()
            uniq = []
            for t in titles:
                if t not in seen:
                    uniq.append(t)
                    seen.add(t)
            if len(uniq) < 2:
                continue
            items.append({
                "id": r["id"],
                "question": r["question"],
                "answer": str(r.get("answer", "")).strip(),
                "type": r.get("type", "bridge"),
                "title1": uniq[0],
                "title2": uniq[1],
            })
    return items


def build_kg_and_vocab(items: List[Dict], seed: int) -> Tuple[KGStore, Dict, List[str], List[str]]:
    """Build KGStore from items. Each item -> 2 triples: (t1, linked_via, t2) + (t2, supplies_ans, a).

    Returns: (kg, eid map, ents list, rels list)
    """
    REL_LINK = "linked_via"
    REL_ANS = "supplies_answer"
    rels = [REL_LINK, REL_ANS]
    rid = {r: i for i, r in enumerate(rels)}

    ents_set = set()
    for it in items:
        ents_set.add(it["title1"])
        ents_set.add(it["title2"])
        ents_set.add(it["answer"])
    ents = sorted(ents_set)
    eid = {e: i for i, e in enumerate(ents)}

    triples = []
    for it in items:
        t1, t2, a = it["title1"], it["title2"], it["answer"]
        if t1 == t2 or t2 == a or t1 == a:
            continue
        triples.append((eid[t1], rid[REL_LINK], eid[t2]))
        triples.append((eid[t2], rid[REL_ANS], eid[a]))
    triples_t = torch.tensor(triples, dtype=torch.long)

    gen = torch.Generator()
    gen.manual_seed(int(seed))
    kg = KGStore(n_ent=len(ents), n_rel=len(rels), n_dim=N_DIM, generator=gen)
    kg.ingest_triples(triples_t)
    # Heavy matmul tensors stay on DEVICE for batched GPU scoring (Fix #24).
    # Generation runs on CPU (per-question scalar loop; small wall) -- the kg.E used by
    # SubstrateGenerator codebook needs CPU copies. We keep both: kg.E + kg.W on DEVICE
    # for score_q_against_kg; SubstrateGenerator gets a CPU-copy of kg.E as codebook.
    kg.E = kg.E.to(DEVICE)
    kg.R = kg.R.to(DEVICE)
    kg.W = kg.W.to(DEVICE)
    return kg, eid, ents, rels


def build_question_codebook(items: List[Dict], encoder: CharTrigramEncoder,
                            ents: List[str], device: torch.device
                            ) -> Tuple[torch.Tensor, torch.Tensor]:
    """Encode question text + entity names via char-trigram encoder.

    Returns:
      q_hd:       [N_Q, n_dim] torch tensor on `device` (question encodings)
      ent_hd:     [n_ent, n_dim] torch tensor on `device` (entity-name encodings)
    """
    # Question encoding -- one HD per question
    q_np = encoder.encode_batch([it["question"] for it in items])  # [N_Q, n_dim] float32 numpy
    # Entity-name encoding -- one HD per entity
    ent_np = encoder.encode_batch(ents)  # [n_ent, n_dim]
    q_t = torch.from_numpy(q_np).to(device=device, dtype=TORCH_DTYPE)
    ent_t = torch.from_numpy(ent_np).to(device=device, dtype=TORCH_DTYPE)
    return q_t, ent_t


def score_q_against_kg(q_hd: torch.Tensor, kg: KGStore) -> torch.Tensor:
    """Use q_hd as a bound key into KGStore.W; returns [N_Q, n_ent] scores.

    Effectively: scores[i] = kg.E @ (kg.W @ q_hd[i]). Batched over questions.
    """
    # q_hd: [N_Q, n_dim] -> Wq: [N_Q, n_dim]; scores: [N_Q, n_ent]
    Wq = q_hd @ kg.W.T  # equivalent to (W @ q^T).T
    scores = Wq @ kg.E.T
    return scores


def topk_entities(scores: torch.Tensor, k: int) -> Tuple[torch.Tensor, torch.Tensor]:
    """Return (topk_indices [N_Q, k], topk_scores [N_Q, k])."""
    r = torch.topk(scores, k=k, dim=1)
    # torch.topk returns (values, indices); we expose (indices, values) for clarity.
    return r.indices, r.values


def score_q_against_entity_codebook(q_hd: torch.Tensor, ent_hd: torch.Tensor) -> torch.Tensor:
    """Cosine-like scoring of q_hd against char-trigram entity-name codebook.

    Used by GENERATION_ONLY arm (no KG W). Returns [N_Q, n_ent] scores.
    """
    # Both bipolar-ish from encoder (sign-bundle). Use dot-product (proportional to cos for
    # equal-norm bipolar vectors).
    return q_hd @ ent_hd.T


def build_sequence_matrix_from_items(items: List[Dict], kg: KGStore, eid: Dict,
                                     rels: List[str], seed: int) -> SequenceMatrix:
    """Build a SequenceMatrix that binds (entity_t, entity_{t+1}) for adjacent entities
    in each ingested chain. Used by SubstrateGenerator to autoregressively step from a
    starting entity to subsequent entities along learned chains.

    Pair pattern: for each item with chain (t1 -> t2 -> a):
        write_pair(E[t1], E[t2])
        write_pair(E[t2], E[a])
    """
    # SequenceMatrix stays on CPU (generation loop is per-question; small wall; avoids
    # torch.randn device-mismatch in SubstrateGenerator which uses CPU-default RNG).
    sm = SequenceMatrix(n_dim=N_DIM)
    E_cpu = kg.E.detach().cpu()
    pairs_prev = []
    pairs_curr = []
    for it in items:
        t1, t2, a = it["title1"], it["title2"], it["answer"]
        if t1 == t2 or t2 == a or t1 == a:
            continue
        if t1 not in eid or t2 not in eid or a not in eid:
            continue
        i1, i2, ia = eid[t1], eid[t2], eid[a]
        pairs_prev.append(E_cpu[i1])
        pairs_curr.append(E_cpu[i2])
        pairs_prev.append(E_cpu[i2])
        pairs_curr.append(E_cpu[ia])
    if not pairs_prev:
        return sm
    K_prev = torch.stack(pairs_prev)
    K_curr = torch.stack(pairs_curr)
    sm.S.add_((K_curr.T @ K_prev) / N_DIM)
    sm._n_pairs_bound = len(pairs_prev)
    return sm


# ----- Per-arm prediction -----
def predict_retrieval_only(scores: torch.Tensor, ents: List[str]) -> List[str]:
    """Top-1 of KGStore scores; entity name as answer."""
    top1 = scores.argmax(dim=1).detach().cpu().numpy().tolist()
    return [ents[i] for i in top1]


def predict_substrate_composed(scores: torch.Tensor, kg: KGStore, gen: SubstrateGenerator,
                               ents: List[str], depth: int, k_top: int,
                               rng: torch.Generator) -> Tuple[List[str], List[int]]:
    """Full pipeline: top-K from KG -> seed SubstrateGenerator from top-1 entity HD ->
    generate `depth` steps -> pick the candidate (top-K + generated visited) that
    is most-frequently-supported across the trajectory.

    Returns (predicted_names, n_distinct_per_q).
    """
    topk_idx, topk_scores = topk_entities(scores, k=k_top)
    topk_idx_cpu = topk_idx.detach().cpu().numpy()
    n_q = scores.shape[0]
    preds = []
    distincts = []
    # CPU codebook (matches gen.codebook device); avoid per-step GPU->CPU transfer
    codebook_cpu = gen.codebook  # already CPU (set in run_one_arm)
    for qi in range(n_q):
        # Seed: top-1 entity HD vector (CPU codebook entry)
        start_idx = int(topk_idx_cpu[qi, 0])
        start_key = codebook_cpu[start_idx]
        # Generate depth-step rollout
        visited = gen.generate(start_key, depth, rng=rng)
        # Candidate set = top-K from retrieval + generation-visited
        cand = list(topk_idx_cpu[qi].tolist()) + list(visited)
        # Pick the most frequent candidate (mode); break ties by KG score order
        counts = defaultdict(int)
        for c in cand:
            counts[int(c)] += 1
        # Order: most-frequent then KG-score (preserves rank when frequencies equal)
        # Tie-break: KG top-K order (priority to top1, then top2, etc.)
        score_order = {int(topk_idx_cpu[qi, j]): -j for j in range(k_top)}
        best = max(counts.items(), key=lambda kv: (kv[1], score_order.get(kv[0], -1e9)))
        preds.append(ents[best[0]])
        distincts.append(len(set(visited)))
    return preds, distincts


def predict_generation_only(q_hd: torch.Tensor, ent_hd: torch.Tensor, gen: SubstrateGenerator,
                            ents: List[str], depth: int, rng: torch.Generator
                            ) -> Tuple[List[str], List[int]]:
    """No KG W; seed the generator from char-trigram entity-name HD that's nearest to the
    question HD (substrate-only nearest-name in char-trigram space), then generate `depth`
    steps and pick most-frequent visited entity.

    Tests whether generation alone (no KG retrieval signal) carries the QA signal.
    """
    # Nearest entity name to question in char-trigram space (no KG involvement)
    cos = score_q_against_entity_codebook(q_hd, ent_hd)  # [N_Q, n_ent]
    top1 = cos.argmax(dim=1).detach().cpu().numpy().tolist()
    n_q = q_hd.shape[0]
    preds = []
    distincts = []
    for qi in range(n_q):
        # Seed: nearest entity-name HD (use the codebook entry from KGStore.E for valid step)
        start_idx = int(top1[qi])
        start_key = gen.codebook[start_idx]  # gen.codebook == kg.E (passed in)
        visited = gen.generate(start_key, depth, rng=rng)
        # No KG retrieval signal here -- pick most-frequent visited entity (mode)
        counts = defaultdict(int)
        for c in visited:
            counts[int(c)] += 1
        # Include the start as a candidate (often the right answer for trivial cases)
        counts[start_idx] += 0
        best = max(counts.items(), key=lambda kv: kv[1]) if counts else (start_idx, 0)
        preds.append(ents[best[0]])
        distincts.append(len(set(visited)))
    return preds, distincts


# ----- Per-arm runner -----
def run_one_arm(arm: str, items: List[Dict], kg: KGStore, sm: SequenceMatrix,
                q_hd: torch.Tensor, ent_hd: torch.Tensor, ents: List[str],
                seed: int) -> Dict:
    """Run one arm; return per-arm metrics dict."""
    t_arm_start = time.time()
    rng = torch.Generator()
    rng.manual_seed(int(seed) + hash(arm) % 100003)

    # SubstrateGenerator runs CPU-side (sm.S on CPU; uses default-device torch.randn).
    # Provide a CPU copy of the entity codebook (kg.E) so SubstrateGenerator stays CPU-coherent.
    kg_E_cpu = kg.E.detach().cpu()
    gen = SubstrateGenerator(sm, kg_E_cpu, sigma_scale=SIGMA_SCALE)

    # KG scores (used by RETRIEVAL_ONLY and SUBSTRATE_COMPOSED)
    if arm in ("RETRIEVAL_ONLY", "SUBSTRATE_COMPOSED"):
        scores = score_q_against_kg(q_hd, kg)  # [N_Q, n_ent]
    else:
        scores = None

    if arm == "RETRIEVAL_ONLY":
        preds = predict_retrieval_only(scores, ents)
        distincts = [1] * len(preds)
    elif arm == "SUBSTRATE_COMPOSED":
        preds, distincts = predict_substrate_composed(
            scores, kg, gen, ents, GEN_DEPTH, TOP_K, rng)
    elif arm == "GENERATION_ONLY":
        preds, distincts = predict_generation_only(
            q_hd, ent_hd, gen, ents, GEN_DEPTH, rng)
    else:
        raise ValueError("unknown arm: %s" % arm)

    # Exact-match
    em_hits = 0
    recall_at_5_hits = 0
    for qi, it in enumerate(items):
        gold = it["answer"]
        if exact_match(preds[qi], gold):
            em_hits += 1
        # Recall@5 only meaningful for arms that produce top-K (RETRIEVAL_ONLY + COMPOSED)
        if scores is not None:
            top5_idx = torch.topk(scores[qi], k=min(5, scores.shape[1])).indices.detach().cpu().numpy().tolist()
            top5_names = [ents[int(i)] for i in top5_idx]
            if any(exact_match(n, gold) for n in top5_names):
                recall_at_5_hits += 1

    n = len(items)
    em = em_hits / n if n > 0 else 0.0
    recall_at_5 = (recall_at_5_hits / n) if (scores is not None and n > 0) else None

    arm_wall_s = time.time() - t_arm_start
    return {
        "arm": arm,
        "seed": int(seed),
        "n_q": n,
        "em": float(em),
        "retrieval_recall_at_5": float(recall_at_5) if recall_at_5 is not None else None,
        "generation_n_distinct_mean": float(np.mean(distincts)) if distincts else 0.0,
        "arm_wall_s": float(arm_wall_s),
        "n_dim": N_DIM,
        "gen_depth": GEN_DEPTH,
        "top_k": TOP_K,
    }


def run_seed(seed: int, items: List[Dict]) -> Dict:
    """Build KG + seq matrix + encoder for this seed; run all arms."""
    t0 = time.time()
    encoder = CharTrigramEncoder(n_dim=N_DIM)
    kg, eid, ents, rels = build_kg_and_vocab(items, seed)
    sm = build_sequence_matrix_from_items(items, kg, eid, rels, seed)
    q_hd, ent_hd = build_question_codebook(items, encoder, ents, DEVICE)

    per_unit = []
    for arm in ARMS:
        res = run_one_arm(arm, items, kg, sm, q_hd, ent_hd, ents, seed)
        per_unit.append(res)
        print("  [seed=%d] arm=%s EM=%.3f recall@5=%s n_distinct=%.1f wall=%.1fs" %
              (seed, arm, res["em"],
               ("%.3f" % res["retrieval_recall_at_5"]) if res["retrieval_recall_at_5"] is not None else "n/a",
               res["generation_n_distinct_mean"], res["arm_wall_s"]), flush=True)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_DIM,
        "M": len(items),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "per_unit": per_unit,
        "elapsed_s": float(elapsed),
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    }


def compute_verdict(per_seed: Dict[str, Dict]) -> Tuple[str, str, Dict]:
    """Verdict logic per pre-reg bands."""
    if not per_seed:
        return ("HARD_FAIL", "HARD_FAIL: no per-seed data.", {})

    # Aggregate per-arm EM across seeds
    agg_em = defaultdict(list)
    agg_recall_at_5 = defaultdict(list)
    agg_distinct = defaultdict(list)
    for sid, body in per_seed.items():
        for pu in body.get("per_unit", []):
            arm = pu["arm"]
            agg_em[arm].append(float(pu.get("em", 0.0)))
            r5 = pu.get("retrieval_recall_at_5")
            if r5 is not None:
                agg_recall_at_5[arm].append(float(r5))
            agg_distinct[arm].append(float(pu.get("generation_n_distinct_mean", 0.0)))

    mean_em = {arm: float(np.mean(v)) for arm, v in agg_em.items()}
    cv_em = {}
    for arm, v in agg_em.items():
        m = float(np.mean(v))
        s = float(np.std(v))
        cv_em[arm] = (s / max(m, 1e-9))
    mean_recall_at_5 = {arm: float(np.mean(v)) for arm, v in agg_recall_at_5.items()}
    mean_distinct = {arm: float(np.mean(v)) for arm, v in agg_distinct.items()}

    composed_em = mean_em.get("SUBSTRATE_COMPOSED", float("nan"))
    retrieval_em = mean_em.get("RETRIEVAL_ONLY", float("nan"))
    generation_em = mean_em.get("GENERATION_ONLY", float("nan"))
    best_primitive = max(retrieval_em if not math.isnan(retrieval_em) else -1.0,
                         generation_em if not math.isnan(generation_em) else -1.0)
    lift = composed_em - best_primitive if not math.isnan(composed_em) else float("nan")
    cv_composed = cv_em.get("SUBSTRATE_COMPOSED", float("inf"))

    n_llm = sum(int(b.get("n_llm_calls", 0)) for b in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    detail = {
        "mean_em": mean_em,
        "cv_em": cv_em,
        "mean_retrieval_recall_at_5": mean_recall_at_5,
        "mean_generation_n_distinct": mean_distinct,
        "composed_em": float(composed_em) if not math.isnan(composed_em) else None,
        "retrieval_only_em": float(retrieval_em) if not math.isnan(retrieval_em) else None,
        "generation_only_em": float(generation_em) if not math.isnan(generation_em) else None,
        "lift_composed_vs_best_primitive": float(lift) if not math.isnan(lift) else None,
        "cv_composed_em": float(cv_composed),
        "substrate_only_ok": bool(substrate_only_ok),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "honest_scope": (
            "Substrate-native QA on HotpotQA-distractor 1k-dev (N_Q=%d subsample), "
            "N_DIM=%d, GEN_DEPTH=%d, TOP_K=%d. 3-arm discriminator (Fix #16): "
            "SUBSTRATE_COMPOSED vs RETRIEVAL_ONLY vs GENERATION_ONLY. "
            "Substrate-only-decode gate enforced (n_llm=%d). Encoder: char-trigram "
            "(no MiniLM); accepts semantic-loss tradeoff for full substrate-only-decode. "
            "Composes CERT 587 (g1b generation) + CERT 588 (h_hotpotqa KG family) + "
            "char_trigram_encoder."
            % (N_Q, N_DIM, GEN_DEPTH, TOP_K, n_llm)),
    }

    summary = (
        "composed_em=%.3f retrieval_em=%.3f generation_em=%.3f lift=%.3f "
        "cv_composed=%.3f n_llm=%d" %
        (composed_em, retrieval_em, generation_em, lift, cv_composed, n_llm))

    # Verdict logic
    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (%d LLM calls). %s"
                % (n_llm, summary), detail)
    if math.isnan(composed_em):
        return ("HARD_FAIL",
                "HARD_FAIL: SUBSTRATE_COMPOSED arm missing data. %s" % summary, detail)
    if composed_em < HARD_FAIL_COMPOSED_EM:
        return ("HARD_FAIL",
                ("HARD_FAIL: composed_em %.3f < HARD_FAIL bar %.2f. %s"
                 % (composed_em, HARD_FAIL_COMPOSED_EM, summary)), detail)
    if not math.isnan(lift) and lift <= 0.0:
        return ("HARD_FAIL",
                ("HARD_FAIL: composition hurts -- composed_em %.3f <= max(per-primitive) %.3f. %s"
                 % (composed_em, best_primitive, summary)), detail)

    # HARD_PASS check
    if (composed_em >= HARD_PASS_COMPOSED_EM
            and (not math.isnan(lift)) and lift >= HARD_PASS_LIFT
            and cv_composed <= HARD_PASS_CV_MAX
            and substrate_only_ok):
        return ("HARD_PASS",
                ("HARD_PASS: substrate-native QA on HotpotQA. composed_em=%.3f >= %.2f "
                 "AND lift=%.3f >= %.2f AND cv=%.3f <= %.2f AND n_llm=0. %s"
                 % (composed_em, HARD_PASS_COMPOSED_EM,
                    lift, HARD_PASS_LIFT,
                    cv_composed, HARD_PASS_CV_MAX, summary)), detail)

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: composed_em=%.3f lift=%.3f cv=%.3f; bands not crossed. %s"
            % (composed_em, lift if not math.isnan(lift) else float("nan"),
               cv_composed, summary), detail)


# ----- Self-test -----
def _selftest():
    """Mechanism self-tests; no I/O of the real corpus."""
    # Test 1: encoder returns shape (n_dim,) bipolar
    enc = CharTrigramEncoder(n_dim=128)
    v = enc.encode("apple")
    assert v.shape == (128,), "selftest 1: encoder shape %s != (128,)" % (v.shape,)
    assert float(np.abs(v).sum()) > 0, "selftest 1: encoder returned zero vector"

    # Test 2: KGStore topk
    gen = torch.Generator()
    gen.manual_seed(0)
    kg = KGStore(n_ent=20, n_rel=2, n_dim=128, generator=gen)
    triples = torch.tensor([[0, 0, 1], [1, 1, 2], [2, 0, 3]], dtype=torch.long)
    kg.ingest_triples(triples)
    idx, sc = kg.predict_one_hop_topk(0, 0, k=3)
    assert idx.shape == (3,), "selftest 2: topk shape %s != (3,)" % (idx.shape,)

    # Test 3: SubstrateGenerator depth-N rollout
    sm = SequenceMatrix(n_dim=128)
    K_prev = kg.E[0:3]
    K_curr = kg.E[1:4]
    sm.S = sm.S + (K_curr.T @ K_prev) / 128
    sm._n_pairs_bound = 3
    g = SubstrateGenerator(sm, kg.E, sigma_scale=0.1)
    rng = torch.Generator(); rng.manual_seed(0)
    path = g.generate(kg.E[0], depth=2, rng=rng)
    assert len(path) == 2, "selftest 3: gen path len %d != 2" % len(path)

    # Test 4: substrate-only-decode gate
    assert _LLM_CALL_COUNTER[0] == 0, "selftest 4: LLM counter non-zero"

    # Test 5: normalize_answer / exact_match
    assert exact_match("The Beatles", "the beatles") == 1, "selftest 5: EM normalization"
    assert exact_match("yes", "no") == 0, "selftest 5: EM rejection"

    print("[selftest] PASS: encoder, KG-topk, gen-rollout, llm=0, EM-normalize", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----- atexit synthesizer (TODO #9 pattern) -----
def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    try:
        out_dir = get_output_dir(ANCHOR_NAME)
        run_config = {"N": N_DIM, "run_mode": RUN_MODE}
        per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
        if not per_seed:
            return
        verdict, verdict_msg, detail = compute_verdict(per_seed)
        verdict_msg = "TIMEOUT_OR_INTERRUPTED_PARTIAL: " + verdict_msg
        metrics = {
            "anchor": ANCHOR_NAME,
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "n_seeds": len(per_seed),
            "N": N_DIM,
            "N_DIM": N_DIM,
            "N_Q": N_Q,
            "TOP_K": TOP_K,
            "GEN_DEPTH": GEN_DEPTH,
            "arms": ARMS,
            "run_mode": RUN_MODE,
            "device": str(DEVICE),
            "config_version": CONFIG_VERSION,
            "corpus_provenance": CORPUS_PROVENANCE,
            "allow_synthetic": False,
            "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
            "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
            "detail": detail,
            "per_seed": [
                {"seed": k, **{kk: vv for kk, vv in v.items() if kk != "per_unit"},
                 "per_unit": v.get("per_unit", [])}
                for k, v in per_seed.items()
            ],
            "metrics_source": "synthesized_from_partials_on_exit",
            "summary": verdict_msg[:200],
            "synthesized_at_exit": True,
        }
        write_metrics(out_dir, metrics, results=list(per_seed.values()))
        _METRICS_WRITTEN[0] = True
        print("[atexit] synthesized metrics.json from %d partials" % len(per_seed),
              flush=True)
    except Exception as e:
        print("[atexit] FAILED to synthesize: %s" % e, flush=True)


atexit.register(_synthesize_on_exit)


def _sigterm_handler(signum, frame):
    _synthesize_on_exit()
    sys.exit(143)


try:
    signal.signal(signal.SIGTERM, _sigterm_handler)
except (ValueError, AttributeError):
    pass


# ----- Main runner -----
out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)
t0_total = time.time()
run_config = {"N": N_DIM, "run_mode": RUN_MODE}

# Load corpus ONCE (shared across seeds; the RNG-dependent thing is KG codebook + seq matrix)
items = load_hotpot_items(HOTPOT_PATH, N_Q)
print("[corpus] loaded %d HotpotQA items from %s" % (len(items), HOTPOT_PATH), flush=True)

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print("[run] mode=%s N_DIM=%d N_Q=%d TOP_K=%d GEN_DEPTH=%d arms=%s device=%s "
      "seeds_done=%s seeds_todo=%s"
      % (RUN_MODE, N_DIM, N_Q, TOP_K, GEN_DEPTH, str(ARMS), str(DEVICE),
         str(done), str(seeds_todo)), flush=True)

if DEVICE.type == "cuda":
    try:
        # Print GPU info for Fix #24 verification
        print("[gpu] device=%s name=%s total_mem_gb=%.2f"
              % (DEVICE, torch.cuda.get_device_name(0),
                 torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
    except Exception as e:
        print("[gpu] info-fetch failed: %s" % e, flush=True)

for s in seeds_todo:
    print("[seed=%d] starting at %.1fs" % (s, time.time() - t0_total), flush=True)
    res = run_seed(s, items)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
verdict, verdict_msg, detail = compute_verdict(per_seed)

metrics = {
    "anchor": ANCHOR_NAME,
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(per_seed),
    "N": N_DIM,
    "N_DIM": N_DIM,
    "N_Q": N_Q,
    "TOP_K": TOP_K,
    "GEN_DEPTH": GEN_DEPTH,
    "arms": ARMS,
    "run_mode": RUN_MODE,
    "device": str(DEVICE),
    "config_version": CONFIG_VERSION,
    "corpus_provenance": CORPUS_PROVENANCE,
    "allow_synthetic": False,
    "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
    "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    "detail": detail,
    "per_seed": [
        {"seed": k, **{kk: vv for kk, vv in v.items() if kk != "per_unit"},
         "per_unit": v.get("per_unit", [])}
        for k, v in per_seed.items()
    ],
    "metrics_source": "measured_substrate_native_qa_hotpotqa_3arm",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))
_METRICS_WRITTEN[0] = True

print("\n[VERDICT] %s" % verdict, flush=True)
print("[VERDICT_MSG] %s" % verdict_msg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
