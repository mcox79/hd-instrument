"""substrate_native_qa_hotpotqa_v2_composition_drill -- composition fix for v1 HARD_FAIL.

v1 HARD_FAIL'd (composed_em=0.010) but GENERATION_ONLY arm got EM=0.122 (cv=0.004 across
3 seeds; n=1000 dev) = substrate-as-LLM-substitute existence proof OBSCURED by
mode-aggregation composition sabotage + char_trigram-on-sentences vs MiniLM-L6-on-entity-
names encoder regime mismatch (CERT 588 KGStore innocent).

This v2 drill (per Research 2x-revival drill 2026-06-22) tests the COMPOSITION FIX via
SCORE FUSION (instead of mode aggregation), plus 5-arm CHARACTERIZATION of the 12.2%
GENERATION_ONLY signal.

ARM SET (11 + 1 harness anchor):

  HARNESS ANCHOR (CAN-FAIL discriminator):
    GENERATION_ONLY_REPRO  -- exact v1 spec; must reproduce 0.122 +/- 0.005 EM

  B SCORE-FUSION SWEEP (6 alpha points):
    COMPOSED_alpha_0.0   -- posterior = 0*norm(KG) + 1.0*norm(gen_visit) = gen-only baseline
    COMPOSED_alpha_0.2   -- 0.2*norm(KG) + 0.8*norm(gen_visit)
    COMPOSED_alpha_0.4   -- 0.4 + 0.6
    COMPOSED_alpha_0.6   -- 0.6 + 0.4
    COMPOSED_alpha_0.8   -- 0.8 + 0.2
    COMPOSED_alpha_1.0   -- 1.0 + 0.0 = retrieval-only baseline

  C CHARACTERIZATION (5 CAN-FAIL gates):
    FREQ_BIAS              -- predict only top-100-frequent gold answers (should NOT hit 12.2%)
    SUBSTRING_OVERLAP      -- predict only if answer-string appears in question (~9%)
    QUESTION_TYPE_SPLIT    -- separate EM for comparison-type vs bridge-type questions
    START_ENTITY_LEAK      -- measure rate(prediction == nearest-entity-seed)
    RANDOM_SEED_CONTROL    -- replace nearest-entity seed with RANDOM entity; EM should drop

PRE-REG (preregs/2026-06-22_substrate_native_qa_hotpotqa_v2_composition_drill.md):

  HARD_PASS (composition fix works AND harness anchor reproduces):
    best_alpha_COMPOSED_em >= 0.20
    AND (best_alpha_COMPOSED_em - GENERATION_ONLY_REPRO_em) >= +0.05
    AND |GENERATION_ONLY_REPRO_em - 0.122| <= 0.005   (harness check)
    AND n_llm_calls == 0
    AND cv across 3 seeds for best-alpha COMPOSED <= 0.10

  HARD_FAIL:
    best_alpha_COMPOSED_em <= GENERATION_ONLY_REPRO_em   (composition still no lift)
    OR |GENERATION_ONLY_REPRO_em - 0.122| > 0.005       (harness FAIL = corrupted v1 invariant)
    OR n_llm_calls > 0

  MIDDLE_BAND: in between (e.g. composed_em > gen-only but < 0.20)

ROUTING: remote_cpu_queue per drill spec (post-processing layer on v1's KG+SeqMatrix;
~2hr CPU wall on N_DIM=8192 / N_Q=1000 / 3 seeds; numpy-bound matmul; NOT GPU-bound).
Note: re-builds KG+SeqMatrix per seed (cheap) rather than ingesting v1 per-question
scores (v1 did not persist per-question scores to disk; full re-run is cleaner).

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
from collections import defaultdict, Counter
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

ANCHOR_NAME = "substrate_native_qa_hotpotqa_v2_composition_drill"

# Substrate-only-decode gate (asserted == 0 at exit)
_LLM_CALL_COUNTER = [0]

CORPUS_PROVENANCE = "hotpotqa_distractor_dev_1k_jsonl"
HOTPOT_PATH = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"

# Pre-reg bands (locked at FULL; smoke uses looser tolerance for harness anchor since
# v1 invariant 0.122 is the FULL-config measurement at N_DIM=8192 / N_Q=1000 / 3 seeds.
# Smoke at N_DIM=2048 / N_Q=50 / 1 seed has higher inherent variance and CANNOT reproduce
# the FULL-config invariant -- smoke harness-tol is just a sanity bound, not the
# load-bearing reproduction check.)
HARD_PASS_COMPOSED_EM = 0.20
HARD_PASS_LIFT = 0.05
HARD_PASS_CV_MAX = 0.10
V1_GENERATION_ONLY_EM = 0.122   # v1 FULL-config metrics anchor

ALPHA_GRID = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
C_ARMS = [
    "FREQ_BIAS",
    "SUBSTRING_OVERLAP",
    "QUESTION_TYPE_SPLIT",
    "START_ENTITY_LEAK",
    "RANDOM_SEED_CONTROL",
]
HARNESS_ARM = "GENERATION_ONLY_REPRO"

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
    SIGMA_SCALE = 0.10
    HARD_PASS_HARNESS_TOL = 0.10  # loose at smoke (variance ~ sqrt(1/50)*0.122 ~ 0.05)
else:
    SEEDS = [7, 17, 23]
    N_DIM = 8192
    N_Q = 1000
    TOP_K = 5
    GEN_DEPTH = 4
    SIGMA_SCALE = 0.10
    HARD_PASS_HARNESS_TOL = 0.005  # tight at FULL (matches v1 cv=0.004)

CONFIG_VERSION = (
    "substrate-native-qa-hotpotqa-v2-composition-drill: N_DIM=%d N_Q=%d TOP_K=%d "
    "GEN_DEPTH=%d sigma=%.3f run_mode=%s device=%s alpha_grid=%s c_arms=%d; "
    "bands HP_composed_em=%.2f HP_lift=%.2f HP_harness_tol=%.3f cv_max=%.2f"
) % (
    N_DIM, N_Q, TOP_K, GEN_DEPTH, SIGMA_SCALE, RUN_MODE, str(DEVICE),
    str(ALPHA_GRID), len(C_ARMS),
    HARD_PASS_COMPOSED_EM, HARD_PASS_LIFT, HARD_PASS_HARNESS_TOL, HARD_PASS_CV_MAX,
)


# ----- Answer normalization (HotpotQA standard EM normalization) -----
_PUNCT_RE = re.compile(r"[^\w\s]")
_ARTICLE_RE = re.compile(r"\b(a|an|the)\b", flags=re.IGNORECASE)


def normalize_answer(s: str) -> str:
    """Standard HotpotQA EM normalization."""
    if s is None:
        return ""
    s = s.lower()
    s = _PUNCT_RE.sub(" ", s)
    s = _ARTICLE_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def exact_match(pred: str, gold: str) -> int:
    return int(normalize_answer(pred) == normalize_answer(gold))


# ----- HotpotQA load + KG build (identical to v1 for harness invariant) -----
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
    """Build KGStore from items (identical to v1)."""
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
    kg.E = kg.E.to(DEVICE)
    kg.R = kg.R.to(DEVICE)
    kg.W = kg.W.to(DEVICE)
    return kg, eid, ents, rels


def build_question_codebook(items: List[Dict], encoder: CharTrigramEncoder,
                            ents: List[str], device: torch.device
                            ) -> Tuple[torch.Tensor, torch.Tensor]:
    q_np = encoder.encode_batch([it["question"] for it in items])
    ent_np = encoder.encode_batch(ents)
    q_t = torch.from_numpy(q_np).to(device=device, dtype=TORCH_DTYPE)
    ent_t = torch.from_numpy(ent_np).to(device=device, dtype=TORCH_DTYPE)
    return q_t, ent_t


def score_q_against_kg(q_hd: torch.Tensor, kg: KGStore) -> torch.Tensor:
    Wq = q_hd @ kg.W.T
    scores = Wq @ kg.E.T
    return scores


def score_q_against_entity_codebook(q_hd: torch.Tensor, ent_hd: torch.Tensor) -> torch.Tensor:
    return q_hd @ ent_hd.T


def build_sequence_matrix_from_items(items: List[Dict], kg: KGStore, eid: Dict,
                                     rels: List[str], seed: int) -> SequenceMatrix:
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


# ----- v1-EXACT generation_only reproduction (HARNESS anchor) -----
def predict_generation_only_v1exact(q_hd: torch.Tensor, ent_hd: torch.Tensor,
                                    gen: SubstrateGenerator, ents: List[str],
                                    depth: int, rng: torch.Generator
                                    ) -> Tuple[List[str], List[int]]:
    """EXACT v1 logic: nearest entity-name seed -> generate depth steps -> mode of visited."""
    cos = score_q_against_entity_codebook(q_hd, ent_hd)
    top1 = cos.argmax(dim=1).detach().cpu().numpy().tolist()
    n_q = q_hd.shape[0]
    preds = []
    distincts = []
    for qi in range(n_q):
        start_idx = int(top1[qi])
        start_key = gen.codebook[start_idx]
        visited = gen.generate(start_key, depth, rng=rng)
        counts = defaultdict(int)
        for c in visited:
            counts[int(c)] += 1
        counts[start_idx] += 0
        best = max(counts.items(), key=lambda kv: kv[1]) if counts else (start_idx, 0)
        preds.append(ents[best[0]])
        distincts.append(len(set(visited)))
    return preds, distincts


# ----- Per-question raw signal collectors (load-bearing for B score-fusion) -----
def collect_per_question_signals(q_hd: torch.Tensor, ent_hd: torch.Tensor, kg: KGStore,
                                 gen: SubstrateGenerator, ents: List[str], depth: int,
                                 rng: torch.Generator
                                 ) -> Dict:
    """Collect per-question signals usable by ALL B alpha-fusion arms + C characterization.

    Returns dict with:
      kg_scores:           [N_Q, n_ent] KGStore W-scoring (raw)
      cos_scores:          [N_Q, n_ent] char-trigram q vs entity-name cosine (raw)
      nearest_ent_idx:     [N_Q] argmax cos (the "start entity" used by gen)
      gen_visit_counts:    [N_Q, n_ent] dense visit-count from depth-K generator rollouts
      random_visit_counts: [N_Q, n_ent] same but with RANDOM start (control)
    """
    n_q = q_hd.shape[0]
    n_ent = len(ents)

    kg_scores = score_q_against_kg(q_hd, kg)  # [N_Q, n_ent] on DEVICE
    cos_scores = score_q_against_entity_codebook(q_hd, ent_hd)  # [N_Q, n_ent]
    nearest = cos_scores.argmax(dim=1).detach().cpu().numpy().tolist()

    gen_visits = np.zeros((n_q, n_ent), dtype=np.float32)
    random_visits = np.zeros((n_q, n_ent), dtype=np.float32)

    # Use a stable secondary RNG for the RANDOM_SEED_CONTROL arm so we can reproduce.
    rand_rng = torch.Generator()
    rand_rng.manual_seed(int(rng.initial_seed()) ^ 0xDEADBEEF)

    for qi in range(n_q):
        # nearest-entity seed visited counts
        start_idx = int(nearest[qi])
        visited = gen.generate(gen.codebook[start_idx], depth, rng=rng)
        for c in visited:
            gen_visits[qi, int(c)] += 1.0
        # Include start_idx with 0 weight so it can be a candidate (matches v1)
        # (no add; counter starts at 0)

        # RANDOM_SEED_CONTROL: replace nearest with a random valid entity index
        rand_idx = int(torch.randint(0, n_ent, (1,), generator=rand_rng).item())
        rvisited = gen.generate(gen.codebook[rand_idx], depth, rng=rand_rng)
        for c in rvisited:
            random_visits[qi, int(c)] += 1.0

    return {
        "kg_scores_np": kg_scores.detach().cpu().numpy(),
        "cos_scores_np": cos_scores.detach().cpu().numpy(),
        "nearest_ent_idx": nearest,
        "gen_visit_counts_np": gen_visits,
        "random_visit_counts_np": random_visits,
    }


def _normalize_per_row(M: np.ndarray) -> np.ndarray:
    """Per-row min-max normalization to [0, 1]. Zero-row -> zero."""
    rmin = M.min(axis=1, keepdims=True)
    rmax = M.max(axis=1, keepdims=True)
    rng = rmax - rmin
    rng[rng < 1e-12] = 1.0
    return (M - rmin) / rng


def predict_score_fusion(kg_scores: np.ndarray, gen_visits: np.ndarray,
                         alpha: float, ents: List[str]) -> List[str]:
    """B-axis score-fusion: posterior = alpha * norm(KG) + (1-alpha) * norm(gen_visit)."""
    kg_norm = _normalize_per_row(kg_scores)
    gen_norm = _normalize_per_row(gen_visits)
    posterior = alpha * kg_norm + (1.0 - alpha) * gen_norm
    pred_idx = posterior.argmax(axis=1).tolist()
    return [ents[int(i)] for i in pred_idx]


def compute_em_per_arm(preds: List[str], items: List[Dict]) -> float:
    em = 0
    for qi, it in enumerate(items):
        em += exact_match(preds[qi], it["answer"])
    n = len(items)
    return em / n if n > 0 else 0.0


def compute_freq_bias_arm(per_q_signals: Dict, items: List[Dict], ents: List[str]
                          ) -> Dict:
    """C1 FREQ_BIAS: predict only from top-100 most-frequent gold answers; should NOT hit 12.2%.

    Logic: restrict argmax to a candidate set = top-100 most-frequent gold answer strings
    seen in the corpus. If 12.2% EM survives this restriction strongly, generation is
    riding answer-frequency-bias not retrieval.
    """
    answer_counts = Counter(it["answer"] for it in items)
    top100_answers = set(a for a, _ in answer_counts.most_common(100))
    top100_ent_indices = set(i for i, e in enumerate(ents) if e in top100_answers)

    gen_visits = per_q_signals["gen_visit_counts_np"]
    n_q, n_ent = gen_visits.shape
    mask = np.full((n_ent,), -1e18, dtype=np.float32)
    for idx in top100_ent_indices:
        mask[idx] = 0.0
    masked = gen_visits + mask[None, :]
    pred_idx = masked.argmax(axis=1).tolist()
    preds = [ents[int(i)] for i in pred_idx]
    em = compute_em_per_arm(preds, items)
    return {
        "arm": "FREQ_BIAS",
        "em": float(em),
        "n_candidates": int(len(top100_ent_indices)),
        "n_q": int(n_q),
        "note": "predict restricted to top-100 most-frequent answer entities",
    }


def compute_substring_overlap_arm(per_q_signals: Dict, items: List[Dict],
                                  ents: List[str]) -> Dict:
    """C2 SUBSTRING_OVERLAP: report (a) generation-only EM, (b) substring-overlap rate
    of predictions vs question text, (c) EM conditioned on substring-overlap.

    Discriminator: if pred-substring-in-question rate is very high (>50% per drill),
    the 12.2% is a question-text-rebroadcast artifact not substrate-internal retrieval.
    """
    gen_visits = per_q_signals["gen_visit_counts_np"]
    # Standard generation-only prediction (mode of visited)
    nearest = per_q_signals["nearest_ent_idx"]
    n_q, _ = gen_visits.shape
    pred_idx_list = []
    for qi in range(n_q):
        gv = gen_visits[qi]
        # Add start_idx with 0 weight (matches v1)
        start_idx = int(nearest[qi])
        if gv.sum() == 0:
            pred_idx_list.append(start_idx)
        else:
            pred_idx_list.append(int(gv.argmax()))
    preds = [ents[i] for i in pred_idx_list]

    em = compute_em_per_arm(preds, items)

    substring_hits = 0
    em_when_substring = 0
    em_when_not_substring = 0
    n_substring = 0
    n_not_substring = 0
    for qi, it in enumerate(items):
        pred_norm = normalize_answer(preds[qi])
        q_norm = normalize_answer(it["question"])
        is_sub = (len(pred_norm) >= 2 and pred_norm in q_norm)
        if is_sub:
            substring_hits += 1
            n_substring += 1
            em_when_substring += exact_match(preds[qi], it["answer"])
        else:
            n_not_substring += 1
            em_when_not_substring += exact_match(preds[qi], it["answer"])

    return {
        "arm": "SUBSTRING_OVERLAP",
        "em_generation_only": float(em),
        "substring_overlap_rate": float(substring_hits) / max(n_q, 1),
        "em_when_substring": float(em_when_substring) / max(n_substring, 1) if n_substring > 0 else None,
        "em_when_not_substring": float(em_when_not_substring) / max(n_not_substring, 1) if n_not_substring > 0 else None,
        "n_substring": int(n_substring),
        "n_not_substring": int(n_not_substring),
        "n_q": int(n_q),
    }


def compute_question_type_arm(per_q_signals: Dict, items: List[Dict],
                              ents: List[str]) -> Dict:
    """C3 QUESTION_TYPE_SPLIT: per-type EM (bridge vs comparison vs other).

    Per drill: drill found comparison=26%, bridge=8%. We re-measure here.
    """
    gen_visits = per_q_signals["gen_visit_counts_np"]
    nearest = per_q_signals["nearest_ent_idx"]
    n_q, _ = gen_visits.shape
    pred_idx_list = []
    for qi in range(n_q):
        gv = gen_visits[qi]
        start_idx = int(nearest[qi])
        if gv.sum() == 0:
            pred_idx_list.append(start_idx)
        else:
            pred_idx_list.append(int(gv.argmax()))
    preds = [ents[i] for i in pred_idx_list]

    by_type = defaultdict(lambda: {"em": 0, "n": 0})
    for qi, it in enumerate(items):
        t = it.get("type", "unknown") or "unknown"
        by_type[t]["em"] += exact_match(preds[qi], it["answer"])
        by_type[t]["n"] += 1

    result = {
        "arm": "QUESTION_TYPE_SPLIT",
        "n_q": int(n_q),
        "per_type": {},
    }
    for t, d in by_type.items():
        result["per_type"][t] = {
            "em": float(d["em"]) / max(d["n"], 1),
            "n": int(d["n"]),
        }
    return result


def compute_start_entity_leak_arm(per_q_signals: Dict, items: List[Dict],
                                  ents: List[str]) -> Dict:
    """C4 START_ENTITY_LEAK: rate(prediction == nearest-entity-seed).

    If gen output is mostly just the seed re-emitted, that's NOT generation -- that's
    char_trigram retrieval cosplaying as generation. Drill found this ~1/1000 in v1.

    Also reports: EM | start_entity is in supporting_facts (the "the start was useful"
    case) vs EM | start_entity NOT in supporting_facts (the "gen had to expand" case).
    The latter > 5% is one HARD_PASS criterion per drill.
    """
    gen_visits = per_q_signals["gen_visit_counts_np"]
    nearest = per_q_signals["nearest_ent_idx"]
    n_q, _ = gen_visits.shape

    pred_idx_list = []
    for qi in range(n_q):
        gv = gen_visits[qi]
        start_idx = int(nearest[qi])
        if gv.sum() == 0:
            pred_idx_list.append(start_idx)
        else:
            pred_idx_list.append(int(gv.argmax()))

    leak_hits = 0
    em_seed_in_sf = 0
    em_seed_not_in_sf = 0
    n_seed_in_sf = 0
    n_seed_not_in_sf = 0
    for qi, it in enumerate(items):
        if pred_idx_list[qi] == int(nearest[qi]):
            leak_hits += 1
        sf_set = {it["title1"], it["title2"]}
        seed_name = ents[int(nearest[qi])]
        em_i = exact_match(ents[pred_idx_list[qi]], it["answer"])
        if seed_name in sf_set:
            n_seed_in_sf += 1
            em_seed_in_sf += em_i
        else:
            n_seed_not_in_sf += 1
            em_seed_not_in_sf += em_i

    return {
        "arm": "START_ENTITY_LEAK",
        "leak_rate": float(leak_hits) / max(n_q, 1),
        "n_q": int(n_q),
        "em_seed_in_supporting_facts": float(em_seed_in_sf) / max(n_seed_in_sf, 1) if n_seed_in_sf > 0 else None,
        "em_seed_NOT_in_supporting_facts": float(em_seed_not_in_sf) / max(n_seed_not_in_sf, 1) if n_seed_not_in_sf > 0 else None,
        "n_seed_in_sf": int(n_seed_in_sf),
        "n_seed_not_in_sf": int(n_seed_not_in_sf),
    }


def compute_random_seed_control_arm(per_q_signals: Dict, items: List[Dict],
                                    ents: List[str]) -> Dict:
    """C5 RANDOM_SEED_CONTROL: same generation logic but RANDOM start entity.

    Discriminator: if EM stays ~12% with random seed, generation is doing uniform-prior
    emission (not seed-conditioned retrieval). Drill predicted 0% with random start;
    actual ~5% would be middle-band.
    """
    rand_visits = per_q_signals["random_visit_counts_np"]
    n_q, _ = rand_visits.shape

    pred_idx_list = []
    for qi in range(n_q):
        rv = rand_visits[qi]
        if rv.sum() == 0:
            # fallback: should not happen since random seed always produces depth>0 visits
            pred_idx_list.append(0)
        else:
            pred_idx_list.append(int(rv.argmax()))
    preds = [ents[i] for i in pred_idx_list]

    em = compute_em_per_arm(preds, items)
    return {
        "arm": "RANDOM_SEED_CONTROL",
        "em": float(em),
        "n_q": int(n_q),
        "note": "generation seeded from RANDOM entity (not nearest)",
    }


# ----- Per-seed runner -----
def run_seed(seed: int, items: List[Dict]) -> Dict:
    t0 = time.time()
    encoder = CharTrigramEncoder(n_dim=N_DIM)
    kg, eid, ents, rels = build_kg_and_vocab(items, seed)
    sm = build_sequence_matrix_from_items(items, kg, eid, rels, seed)
    q_hd, ent_hd = build_question_codebook(items, encoder, ents, DEVICE)

    kg_E_cpu = kg.E.detach().cpu()
    # arm-1: GENERATION_ONLY_REPRO (harness anchor; v1-exact RNG seeding for invariant)
    t_h0 = time.time()
    rng_h = torch.Generator()
    rng_h.manual_seed(int(seed) + hash("GENERATION_ONLY") % 100003)
    gen_h = SubstrateGenerator(sm, kg_E_cpu, sigma_scale=SIGMA_SCALE)
    preds_h, _ = predict_generation_only_v1exact(q_hd, ent_hd, gen_h, ents, GEN_DEPTH, rng_h)
    em_harness = compute_em_per_arm(preds_h, items)
    t_h = time.time() - t_h0
    print("  [seed=%d] HARNESS GENERATION_ONLY_REPRO EM=%.4f wall=%.1fs (v1 anchor=0.1223 cv=0.004)"
          % (seed, em_harness, t_h), flush=True)

    # arm-2: collect per-q signals (one shared pass for all B + C arms)
    t_c0 = time.time()
    rng_c = torch.Generator()
    rng_c.manual_seed(int(seed) + hash("SIGNAL_COLLECT") % 100003)
    gen_c = SubstrateGenerator(sm, kg_E_cpu, sigma_scale=SIGMA_SCALE)
    per_q = collect_per_question_signals(q_hd, ent_hd, kg, gen_c, ents, GEN_DEPTH, rng_c)
    t_c = time.time() - t_c0
    print("  [seed=%d] signal-collect wall=%.1fs (KG-scores + cos-scores + 2x gen rollouts)"
          % (seed, t_c), flush=True)

    # B arms (alpha sweep)
    b_results = []
    for alpha in ALPHA_GRID:
        preds = predict_score_fusion(per_q["kg_scores_np"], per_q["gen_visit_counts_np"],
                                     alpha, ents)
        em = compute_em_per_arm(preds, items)
        b_results.append({"arm": "COMPOSED_alpha_%.1f" % alpha, "alpha": float(alpha),
                          "em": float(em)})
        print("  [seed=%d]   COMPOSED_alpha_%.1f EM=%.4f" % (seed, alpha, em), flush=True)

    # C arms
    c_results = [
        compute_freq_bias_arm(per_q, items, ents),
        compute_substring_overlap_arm(per_q, items, ents),
        compute_question_type_arm(per_q, items, ents),
        compute_start_entity_leak_arm(per_q, items, ents),
        compute_random_seed_control_arm(per_q, items, ents),
    ]
    for c in c_results:
        if "em" in c:
            print("  [seed=%d]   C-%s em=%.4f" % (seed, c["arm"], c["em"]), flush=True)
        elif "em_generation_only" in c:
            print("  [seed=%d]   C-%s em=%.4f sub_rate=%.3f"
                  % (seed, c["arm"], c["em_generation_only"], c["substring_overlap_rate"]), flush=True)
        elif "leak_rate" in c:
            print("  [seed=%d]   C-%s leak_rate=%.4f" % (seed, c["arm"], c["leak_rate"]), flush=True)
        elif "per_type" in c:
            type_str = " ".join("%s=%.3f(n=%d)" % (k, v["em"], v["n"]) for k, v in c["per_type"].items())
            print("  [seed=%d]   C-%s %s" % (seed, c["arm"], type_str), flush=True)

    elapsed = time.time() - t0
    return {
        "seed": int(seed),
        "N": N_DIM,
        "M": len(items),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "harness_em": float(em_harness),
        "b_arms": b_results,
        "c_arms": c_results,
        "elapsed_s": float(elapsed),
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    }


def compute_verdict(per_seed: Dict[str, Dict]) -> Tuple[str, str, Dict]:
    if not per_seed:
        return ("HARD_FAIL", "HARD_FAIL: no per-seed data.", {})

    # Aggregate
    harness_ems = []
    b_by_alpha = defaultdict(list)
    c_aggs = defaultdict(list)
    for sid, body in per_seed.items():
        harness_ems.append(float(body.get("harness_em", 0.0)))
        for b in body.get("b_arms", []):
            b_by_alpha[b["alpha"]].append(float(b["em"]))
        for c in body.get("c_arms", []):
            c_aggs[c["arm"]].append(c)

    mean_harness = float(np.mean(harness_ems)) if harness_ems else float("nan")
    cv_harness = (float(np.std(harness_ems)) / max(mean_harness, 1e-9)) if harness_ems else float("inf")
    harness_delta = abs(mean_harness - V1_GENERATION_ONLY_EM)

    mean_b_by_alpha = {a: float(np.mean(v)) for a, v in b_by_alpha.items()}
    cv_b_by_alpha = {}
    for a, v in b_by_alpha.items():
        m = float(np.mean(v))
        s = float(np.std(v))
        cv_b_by_alpha[a] = s / max(m, 1e-9)

    best_alpha, best_em = max(mean_b_by_alpha.items(), key=lambda kv: kv[1])
    composed_lift = best_em - mean_harness
    cv_best = cv_b_by_alpha.get(best_alpha, float("inf"))

    # Aggregate C arms (mean of per-seed values, where present)
    c_aggregate = {}
    for arm_name, arm_list in c_aggs.items():
        agg = {}
        # numeric fields: mean across seeds
        numeric_keys = set()
        for arm_dict in arm_list:
            for k, v in arm_dict.items():
                if isinstance(v, (int, float)) and k != "n_q":
                    numeric_keys.add(k)
        for k in numeric_keys:
            vals = [float(d[k]) for d in arm_list if k in d and d[k] is not None]
            if vals:
                agg[k + "_mean"] = float(np.mean(vals))
        # special: per_type for QUESTION_TYPE_SPLIT
        if any("per_type" in d for d in arm_list):
            per_type_agg = defaultdict(list)
            for d in arm_list:
                for t, pt in d.get("per_type", {}).items():
                    per_type_agg[t].append(pt["em"])
            agg["per_type_em_mean"] = {t: float(np.mean(v)) for t, v in per_type_agg.items()}
            agg["per_type_n_mean"] = {
                t: float(np.mean([d["per_type"][t]["n"] for d in arm_list if t in d.get("per_type", {})]))
                for t in per_type_agg.keys()
            }
        c_aggregate[arm_name] = agg

    n_llm = sum(int(b.get("n_llm_calls", 0)) for b in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    detail = {
        "mean_harness_em": mean_harness,
        "v1_anchor_em": V1_GENERATION_ONLY_EM,
        "harness_delta_abs": harness_delta,
        "harness_tol": HARD_PASS_HARNESS_TOL,
        "harness_within_tol": bool(harness_delta <= HARD_PASS_HARNESS_TOL),
        "cv_harness": cv_harness,
        "mean_b_by_alpha": mean_b_by_alpha,
        "cv_b_by_alpha": cv_b_by_alpha,
        "best_alpha": float(best_alpha),
        "best_alpha_em": float(best_em),
        "composed_lift_vs_harness": float(composed_lift),
        "cv_best_alpha": float(cv_best),
        "c_aggregate": c_aggregate,
        "substrate_only_ok": bool(substrate_only_ok),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "honest_scope": (
            "Composition fix drill on HotpotQA-distractor 1k-dev (N_Q=%d), N_DIM=%d, "
            "GEN_DEPTH=%d, TOP_K=%d. 11 arms (1 harness + 6 B alpha-sweep + 5 C "
            "characterization). Substrate-only-decode gate enforced (n_llm=%d). "
            "Score-fusion replaces v1's mode-aggregation composition (per Research "
            "2x-revival drill 2026-06-22). Builds on CERT 587 (g1b) + CERT 588 "
            "(h_hotpotqa KG) + char_trigram_encoder."
            % (N_Q, N_DIM, GEN_DEPTH, TOP_K, n_llm)),
    }

    summary = (
        "harness_em=%.4f (v1=0.1223 delta=%.4f tol=%.3f) "
        "best_alpha=%.1f best_alpha_em=%.4f lift=%.4f cv_best=%.4f n_llm=%d" %
        (mean_harness, harness_delta, HARD_PASS_HARNESS_TOL,
         best_alpha, best_em, composed_lift, cv_best, n_llm))

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (%d LLM calls). %s"
                % (n_llm, summary), detail)

    # HARNESS check (CAN-FAIL gate)
    if harness_delta > HARD_PASS_HARNESS_TOL:
        return ("HARD_FAIL",
                "HARD_FAIL: harness anchor REPRODUCTION violated. |%.4f - %.4f| = %.4f > tol %.3f. "
                "v1 invariant broken => composition-fix verdict UNINTERPRETABLE. %s"
                % (mean_harness, V1_GENERATION_ONLY_EM, harness_delta, HARD_PASS_HARNESS_TOL, summary),
                detail)

    # COMPOSITION-NO-LIFT check (HARD_FAIL)
    if best_em <= mean_harness:
        return ("HARD_FAIL",
                "HARD_FAIL: composition still no lift. best_alpha=%.1f em=%.4f <= harness=%.4f. %s"
                % (best_alpha, best_em, mean_harness, summary), detail)

    # HARD_PASS check
    if (best_em >= HARD_PASS_COMPOSED_EM
            and composed_lift >= HARD_PASS_LIFT
            and cv_best <= HARD_PASS_CV_MAX
            and substrate_only_ok):
        return ("HARD_PASS",
                ("HARD_PASS: composition-fix lift confirmed. best_alpha=%.1f em=%.4f >= %.2f "
                 "AND lift=%.4f >= %.2f AND cv=%.4f <= %.2f AND harness reproduced (delta=%.4f). %s"
                 % (best_alpha, best_em, HARD_PASS_COMPOSED_EM,
                    composed_lift, HARD_PASS_LIFT,
                    cv_best, HARD_PASS_CV_MAX,
                    harness_delta, summary)), detail)

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: composition lifts but bands not crossed. %s"
            % summary, detail)


# ----- Self-test -----
def _selftest():
    enc = CharTrigramEncoder(n_dim=128)
    v = enc.encode("apple")
    assert v.shape == (128,), "selftest 1: encoder shape %s != (128,)" % (v.shape,)
    assert float(np.abs(v).sum()) > 0, "selftest 1: zero vector"

    gen_rng = torch.Generator(); gen_rng.manual_seed(0)
    kg = KGStore(n_ent=20, n_rel=2, n_dim=128, generator=gen_rng)
    triples = torch.tensor([[0, 0, 1], [1, 1, 2], [2, 0, 3]], dtype=torch.long)
    kg.ingest_triples(triples)

    sm = SequenceMatrix(n_dim=128)
    K_prev = kg.E[0:3]; K_curr = kg.E[1:4]
    sm.S = sm.S + (K_curr.T @ K_prev) / 128
    sm._n_pairs_bound = 3
    g = SubstrateGenerator(sm, kg.E, sigma_scale=0.1)
    rng = torch.Generator(); rng.manual_seed(0)
    path = g.generate(kg.E[0], depth=2, rng=rng)
    assert len(path) == 2, "selftest 2: gen path len %d != 2" % len(path)

    # selftest 3: score-fusion shape + range
    kg_s = np.array([[1.0, 0.5, 0.1], [0.2, 0.9, 0.3]], dtype=np.float32)
    gen_v = np.array([[0.0, 2.0, 1.0], [1.0, 0.0, 0.0]], dtype=np.float32)
    normed = _normalize_per_row(kg_s)
    assert normed.shape == (2, 3), "selftest 3: norm shape"
    assert normed.min() >= 0.0 and normed.max() <= 1.0, "selftest 3: norm range"

    # selftest 4: score-fusion endpoint check (alpha=0 = gen-only)
    preds_alpha0 = predict_score_fusion(kg_s, gen_v, 0.0, ["A", "B", "C"])
    # gen_v row 0 argmax = 1 (=2.0), row 1 argmax = 0 (=1.0)
    assert preds_alpha0 == ["B", "A"], "selftest 4: alpha=0 != gen-only argmax (got %s)" % preds_alpha0

    # selftest 5: score-fusion endpoint check (alpha=1 = retrieval-only)
    preds_alpha1 = predict_score_fusion(kg_s, gen_v, 1.0, ["A", "B", "C"])
    # kg_s row 0 argmax = 0 (=1.0), row 1 argmax = 1 (=0.9)
    assert preds_alpha1 == ["A", "B"], "selftest 5: alpha=1 != kg-only argmax (got %s)" % preds_alpha1

    # selftest 6: substrate-only-decode gate
    assert _LLM_CALL_COUNTER[0] == 0, "selftest 6: LLM counter non-zero"

    # selftest 7: EM normalization
    assert exact_match("The Beatles", "the beatles") == 1, "selftest 7: EM normalization"
    assert exact_match("yes", "no") == 0, "selftest 7: EM rejection"

    print("[selftest] PASS: encoder, gen-rollout, norm-shape, alpha=0/1 endpoints, llm=0, EM-norm",
          flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----- atexit synthesizer -----
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
            "alpha_grid": ALPHA_GRID,
            "c_arms": C_ARMS,
            "harness_arm": HARNESS_ARM,
            "run_mode": RUN_MODE,
            "device": str(DEVICE),
            "config_version": CONFIG_VERSION,
            "corpus_provenance": CORPUS_PROVENANCE,
            "allow_synthetic": False,
            "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
            "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
            "detail": detail,
            "per_seed": [
                {"seed": k, **{kk: vv for kk, vv in v.items()}}
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

items = load_hotpot_items(HOTPOT_PATH, N_Q)
print("[corpus] loaded %d HotpotQA items from %s" % (len(items), HOTPOT_PATH), flush=True)

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print("[run] mode=%s N_DIM=%d N_Q=%d TOP_K=%d GEN_DEPTH=%d alpha_grid=%s device=%s "
      "seeds_done=%s seeds_todo=%s"
      % (RUN_MODE, N_DIM, N_Q, TOP_K, GEN_DEPTH, str(ALPHA_GRID), str(DEVICE),
         str(done), str(seeds_todo)), flush=True)

if DEVICE.type == "cuda":
    try:
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
    "alpha_grid": ALPHA_GRID,
    "c_arms": C_ARMS,
    "harness_arm": HARNESS_ARM,
    "run_mode": RUN_MODE,
    "device": str(DEVICE),
    "config_version": CONFIG_VERSION,
    "corpus_provenance": CORPUS_PROVENANCE,
    "allow_synthetic": False,
    "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
    "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    "detail": detail,
    "per_seed": [
        {"seed": k, **{kk: vv for kk, vv in v.items()}}
        for k, v in per_seed.items()
    ],
    "metrics_source": "measured_substrate_native_qa_hotpotqa_v2_composition_drill",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))
_METRICS_WRITTEN[0] = True

print("\n[VERDICT] %s" % verdict, flush=True)
print("[VERDICT_MSG] %s" % verdict_msg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
