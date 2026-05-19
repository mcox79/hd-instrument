"""Wave 14.B Interpretability Demo: show what's IN stored memories.

Uses already-built M2 artifacts (CP factors, NMF concepts, PPMI pairs) to
produce human-readable summaries of pool entries. No new training needed.

Algorithm:
1. Load Phase A state (pool entries, codebooks).
2. Extract concepts via PPMI (cheap, interpretable - byte n-gram pairs).
3. For each pool entry:
   - Decompose into (byte, position) bindings (we already have pool_labels for target).
   - Compute concept activation: which PPMI pairs are present.
   - Output: pool entry index, target byte, ctx bytes, top-K activated concepts.
4. Print a sample of pool entries with their concept-readouts.

This is the "what does my AI remember?" capability that no vector DB has.
Even though concepts don't improve retrieval (theorem-bound), they're
EXPLICIT human-readable structure.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import torch
import math


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
VOCAB_SIZE = 256
K = 4
N = 4096
NUM_CONCEPTS = 50
PPMI_K = 1.0
SAMPLE_POOL_ENTRIES = 10
TOP_CONCEPTS_PER_ENTRY = 5


def _say(msg):
    print(msg, flush=True)


def byte_readable(b):
    """Human-readable byte: ASCII char if printable, else hex."""
    if 32 <= b < 127:
        return repr(chr(b))
    elif b == 10:
        return "'\\n'"
    elif b == 9:
        return "'\\t'"
    elif b == 32:
        return "' '"
    else:
        return f"0x{b:02x}"


def decompose_pool_to_bytes(pool_vecs, byte_atoms, pos_atoms, n):
    P = pool_vecs.shape[0]
    out = torch.zeros((P, K), dtype=torch.long, device=DEVICE)
    for r in range(K):
        proj = pool_vecs * pos_atoms[r].unsqueeze(0)
        scores = proj @ byte_atoms.T / n
        out[:, r] = scores.argmax(dim=1)
    return out


def extract_ppmi_concepts(pool_byte_at_pos, K_pos, vocab, num_concepts, k_neg):
    P = pool_byte_at_pos.shape[0]
    pair_counts = Counter()
    marginal_counts = Counter()
    total = 0
    for entry_idx in range(P):
        bytes_at = pool_byte_at_pos[entry_idx].cpu().tolist()
        for i in range(K_pos):
            marginal_counts[(i, bytes_at[i])] += 1
            for j in range(i + 1, K_pos):
                pair_counts[(i, bytes_at[i], j, bytes_at[j])] += 1
                total += 1
    total_marginal = P
    ppmi_scores = []
    for (i, b_i, j, b_j), cnt in pair_counts.items():
        p_ab = cnt / total
        p_a = marginal_counts[(i, b_i)] / total_marginal
        p_b = marginal_counts[(j, b_j)] / total_marginal
        if p_a > 0 and p_b > 0 and p_ab > 0:
            pmi = math.log(p_ab / (p_a * p_b ** 0.75 + 1e-12)) - math.log(k_neg)
            ppmi_scores.append((i, b_i, j, b_j, max(0.0, pmi), cnt))
    ppmi_scores.sort(key=lambda x: -x[4])
    return ppmi_scores[:num_concepts]


def main():
    _say(f"Wave 14.B Interpretability Demo: show what's IN pool memories")
    _say(f"  Using PPMI-extracted concepts (top-{NUM_CONCEPTS})")

    state_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_cl_phase_a" / "state.pt"
    state = torch.load(state_path, weights_only=False)
    pool_vecs = state["pool_vecs_A"].to(DEVICE)
    pool_labels = state["pool_labels_A"].to(DEVICE)
    pool_used = int(state["pool_used_A"])
    byte_atoms = state["byte_atoms"].to(DEVICE)
    pos_atoms = state["pos_atoms"].to(DEVICE)
    _say(f"  Pool has {pool_used} entries")

    # Decompose all pool entries into per-position bytes
    _say(f"\nDecomposing all pool entries...")
    pool_byte_at_pos = decompose_pool_to_bytes(pool_vecs[:pool_used], byte_atoms, pos_atoms, N)
    _say(f"  Done. Pool entries are now (ctx[4 bytes], target_byte).")

    # Extract PPMI concepts
    _say(f"\nExtracting top-{NUM_CONCEPTS} PPMI concepts...")
    concepts = extract_ppmi_concepts(pool_byte_at_pos, K, VOCAB_SIZE, NUM_CONCEPTS, PPMI_K)
    _say(f"\nTop-15 concepts by PPMI score:")
    for c_idx, (i, b_i, j, b_j, ppmi, cnt) in enumerate(concepts[:15]):
        _say(f"  #{c_idx+1:2d}: pos {i}={byte_readable(b_i)} & pos {j}={byte_readable(b_j)}  "
             f"(PPMI={ppmi:.2f}, count={cnt})")

    # For each sampled pool entry, find its activated concepts
    _say(f"\n\nSample pool entries with their activated concepts:")
    _say(f"{'=' * 80}")
    gen = torch.Generator().manual_seed(SEED + 100)
    sample_indices = torch.randperm(pool_used, generator=gen)[:SAMPLE_POOL_ENTRIES].tolist()

    for sample_i, entry_idx in enumerate(sample_indices):
        ctx_bytes = pool_byte_at_pos[entry_idx].cpu().tolist()
        target = int(pool_labels[entry_idx].item())
        # Find activated concepts for this entry
        activated = []
        for c_idx, (i, b_i, j, b_j, ppmi, _cnt) in enumerate(concepts):
            if ctx_bytes[i] == b_i and ctx_bytes[j] == b_j:
                activated.append((c_idx, i, b_i, j, b_j, ppmi))
        activated.sort(key=lambda x: -x[5])

        _say(f"\nPool entry #{entry_idx} (sample {sample_i+1}/{SAMPLE_POOL_ENTRIES}):")
        ctx_readable = " | ".join(f"p{p}={byte_readable(b)}" for p, b in enumerate(ctx_bytes))
        _say(f"  context: {ctx_readable}  -> target: {byte_readable(target)}")
        if activated:
            _say(f"  activated concepts ({len(activated)} total, showing top {TOP_CONCEPTS_PER_ENTRY}):")
            for (c_idx, i, b_i, j, b_j, ppmi) in activated[:TOP_CONCEPTS_PER_ENTRY]:
                _say(f"    concept #{c_idx+1:2d}: 'p{i}={byte_readable(b_i)} & p{j}={byte_readable(b_j)}' "
                     f"(PPMI={ppmi:.2f})")
        else:
            _say(f"  no concepts activated (entry is unique / no recurring pairs)")

    # Statistics: how many entries activate how many concepts?
    _say(f"\n\nConcept-activation statistics across full pool:")
    activation_counts = []
    for entry_idx in range(pool_used):
        ctx_bytes = pool_byte_at_pos[entry_idx].cpu().tolist()
        n_active = sum(1 for (i, b_i, j, b_j, _, _) in concepts
                       if ctx_bytes[i] == b_i and ctx_bytes[j] == b_j)
        activation_counts.append(n_active)
    mean_act = sum(activation_counts) / len(activation_counts)
    max_act = max(activation_counts)
    pct_with_any = sum(1 for x in activation_counts if x > 0) / len(activation_counts) * 100
    _say(f"  Mean concepts activated per entry: {mean_act:.2f}")
    _say(f"  Max concepts activated by single entry: {max_act}")
    _say(f"  Percent of entries activating at least one concept: {pct_with_any:.1f}%")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_interpretability_demo"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "num_concepts_extracted": len(concepts),
        "top_15_concepts": [(i, b_i, j, b_j, ppmi, cnt) for (i, b_i, j, b_j, ppmi, cnt) in concepts[:15]],
        "mean_concepts_activated_per_entry": mean_act,
        "pct_entries_with_concepts": pct_with_any,
    }, indent=2))

    _say(f"\n========= INTERPRETABILITY VERDICT =========")
    if pct_with_any > 50:
        _say(f"  WORKS: {pct_with_any:.0f}% of memories contain interpretable structural patterns.")
        _say(f"  We can show users WHAT THEIR AI REMEMBERS via concept readouts.")
        _say(f"  Capability no vector DB has natively.")
    else:
        _say(f"  Partial: only {pct_with_any:.0f}% of memories have detectable structural patterns.")
        _say(f"  Might need more concepts or different extraction.")


if __name__ == "__main__":
    main()
