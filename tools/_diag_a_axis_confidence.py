"""Diagnostic: per-A-question algebra confidence + branch decision."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.substrate_index.partition import PartitionedStore
from tools.substrate_benchmark import _algebra_query, _ensure_algebra_index

ps = PartitionedStore(root=Path("data/substrate_index"))
ai = _ensure_algebra_index(ps)
print(f"algebra index loaded: {ai is not None}")

A_questions = [
    "What atoms do I have about FHRR binding?",
    "What atoms do I have about Random Matrix Theory?",
    "What atoms do I have about Hopfield network family?",
    "What atoms do I have about reinforcement learning?",
    "What atoms do I have about quantum entanglement specifically?",
    "What atoms do I have about Bayesian inference?",
    "What atoms do I have about substrate-classical NL stack?",
    "What atoms do I have about backpropagation?",
    "What atoms do I have about sparse representations?",
    "What atoms do I have about Lyapunov stability?",
    "What atoms do I have about FFT and circular convolution?",
    "What atoms do I have about probabilistic graphical models?",
]

n_fired = 0
print("\nA axis confidence audit:")
print(f"{'branch':10s} {'conf':>6s}  question")
for q in A_questions:
    ordered, conf = _algebra_query(ps, q, top_k=8)
    branch = "ALG_RRF" if conf > 0.20 else "bge-only"
    if conf > 0.20:
        n_fired += 1
    print(f"  {branch:10s} {conf:.3f}  {q[:60]}")
print(f"\nAlgebra branch fired: {n_fired}/{len(A_questions)}")
