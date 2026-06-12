"""Diagnostic Cycle 49: per-A-question algebra-vs-bge OVERLAP / NOVELTY ratio.

Hypothesis: HYBRID LIFTS when algebra top-8 brings NOVEL content not in bge top-15
(broad queries); HYBRID HURTS when algebra is REDUNDANT with bge or pulls in
structurally-near but content-wrong atoms (narrow queries with concentrated gold).

Measures: |alg_topk - bge_top15|, |alg_topk INTERSECT bge_top15|, prediction shape.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.substrate_index.partition import PartitionedStore
from tools.substrate_benchmark import _algebra_query, _ensure_algebra_index, _ensure_semantic_retriever, _BARE_TO_QID

ps = PartitionedStore(root=Path("data/substrate_index"))
ai = _ensure_algebra_index(ps)
print(f"algebra index: {ai is not None}; bge retriever (laptop env-gated): attempting...")
retr = _ensure_semantic_retriever(ps)
print(f"bge retriever: {retr is not None}")
if retr is None:
    print("ABORT: bge unavailable on laptop; run this diag on REMOTE.")
    sys.exit(0)

A_questions = [
    ("Q01-A FHRR binding", "What atoms do I have about FHRR binding?", "HURT -0.20"),
    ("Q02-A RMT", "What atoms do I have about Random Matrix Theory?", "HURT -0.14"),
    ("Q04-A RL", "What atoms do I have about reinforcement learning?", "LIFT +0.15"),
    ("Q31-A Bayesian", "What atoms do I have about Bayesian inference?", "FLAT"),
    ("Q35-A Lyapunov", "What atoms do I have about Lyapunov stability?", "FLAT"),
    ("Q37-A Grph models", "What atoms do I have about probabilistic graphical models?", "LIFT +0.18"),
]

from tools.substrate_benchmark import _BARE_TO_QID as _b2q
print(f"\n{'Q':25s} {'conf':>5s} {'alg':>4s} {'bge':>4s} {'ovl':>4s} {'nov':>4s} {'outcome':>10s}")
for tag, q, outcome in A_questions:
    alg_ordered, conf = _algebra_query(ps, q, top_k=8)
    bge_cands = retr.semantic(q, top_k=15)
    bge_qids = []
    for c in bge_cands:
        bge_qids.append(_b2q.get(c.atom_id, c.atom_id) if _b2q else c.atom_id)
    alg_set = set(alg_ordered)
    bge_set = set(bge_qids)
    overlap = alg_set & bge_set
    novelty = alg_set - bge_set
    print(f"  {tag:25s} {conf:.3f}  {len(alg_set):>3d}  {len(bge_set):>3d}  {len(overlap):>3d}  {len(novelty):>3d}  {outcome:>10s}")
