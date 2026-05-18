"""Wave 14.A: Shuffle Hopf algebra — tractable cousin of Connes-Kreimer.

Per buried-treasure audit (2026-05-18): Connes-Kreimer's tree coproduct
gives native decomposition with closed-form rules. Implementing the
full CK tree algebra is multi-week work. Starting with the SIMPLER
**shuffle Hopf algebra on words**, which has the same key property —
explicit decomposition via deconcatenation coproduct — but on words
not trees.

Shuffle Hopf algebra on alphabet A:
- Atoms: words over A of bounded length L
- Multiplication: shuffle product (sum over all interleavings)
  e.g., (ab) ⊔ (cd) = abcd + acbd + acdb + cabd + cadb + cdab
- Coproduct (deconcatenation): Delta(w_1...w_n) = Σ_{i=0..n} (w_1...w_i) ⊗ (w_{i+1}...w_n)
  Returns ALL prefix-suffix splits as explicit tensor terms.
- Antipode: S(w) = (-1)^n · reverse(w)

The deconcatenation coproduct IS the structural decomposition we want.
For HDC, this means: bind two atoms (concatenate words), bundle several,
then Delta recovers all prefix-suffix pairs that could have produced the bundle.

Test (Phase A toy):
1. Generate 32 random words of length L=4 over alphabet of 8 symbols.
2. Concatenate two: c = w_a · w_b (length 8 word).
3. Compute Delta(c) — should give (w_a, w_b) as the dominant split among
   all length-8 deconcatenation pairs.
4. Compare to baseline: random codebook NN cleanup of c against the
   length-4 codebook.

If Delta explicitly recovers (w_a, w_b) better than NN, the deconcatenation
coproduct delivers what H_4's Delta couldn't.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch


SEED = 17
L_WORD = 4              # word length
ALPHABET_SIZE = 8       # |A|
NUM_ATOMS = 32          # codebook size
NUM_TRIALS = 100


def _say(msg: str) -> None:
    print(msg, flush=True)


def generate_word(gen) -> torch.Tensor:
    """Random word of length L over alphabet of size ALPHABET_SIZE."""
    return torch.randint(0, ALPHABET_SIZE, (L_WORD,), generator=gen)


def concatenate(w1: torch.Tensor, w2: torch.Tensor) -> torch.Tensor:
    """Word concatenation w1 · w2 (length L_WORD * 2 for two L_WORD words)."""
    return torch.cat([w1, w2])


def deconcatenation_coproduct(w: torch.Tensor) -> list[tuple[torch.Tensor, torch.Tensor]]:
    """Delta(w) = Σ_i (prefix_i) ⊗ (suffix_i) for i = 0..len(w).

    Returns list of (prefix, suffix) pairs.
    """
    n = w.shape[0]
    pairs = []
    for i in range(n + 1):
        pairs.append((w[:i], w[i:]))
    return pairs


def word_to_vec(word: torch.Tensor) -> torch.Tensor:
    """Convert word (a tensor of indices) to a hash/embedding for similarity.

    For this toy: just flatten one-hot encoding. Bigger embeddings could
    be used but unnecessary for the unit test.
    """
    n = word.shape[0]
    out = torch.zeros(n, ALPHABET_SIZE)
    for i, idx in enumerate(word):
        out[i, idx] = 1.0
    return out.flatten()


def word_similarity(w1: torch.Tensor, w2: torch.Tensor) -> float:
    """Cosine similarity between two words via one-hot embedding."""
    if w1.shape != w2.shape:
        return 0.0
    v1 = word_to_vec(w1)
    v2 = word_to_vec(w2)
    return float(v1.dot(v2) / (v1.norm() * v2.norm() + 1e-9))


def codebook_top1(query_word: torch.Tensor, codebook: list[torch.Tensor]) -> int:
    """Find the codebook index whose embedding is most similar to query."""
    best_idx, best_sim = -1, -float("inf")
    for i, atom in enumerate(codebook):
        sim = word_similarity(query_word, atom)
        if sim > best_sim:
            best_sim = sim
            best_idx = i
    return best_idx


def main() -> None:
    _say(f"Wave 14.A: Shuffle Hopf algebra deconcatenation cleanup test")
    _say(f"  L_WORD={L_WORD}, ALPHABET_SIZE={ALPHABET_SIZE}, NUM_ATOMS={NUM_ATOMS}, NUM_TRIALS={NUM_TRIALS}")
    _say(f"  Hypothesis: deconcatenation Delta explicitly recovers (prefix, suffix) split")

    gen = torch.Generator().manual_seed(SEED)
    _say(f"\nGenerating codebook of {NUM_ATOMS} random words...")
    codebook = [generate_word(gen) for _ in range(NUM_ATOMS)]
    for i, w in enumerate(codebook[:5]):
        _say(f"  atom[{i}] = {w.tolist()}")

    _say(f"\nDeconcatenation recovery test:")
    delta_correct = 0
    naive_correct_either = 0
    naive_correct_both = 0

    for trial in range(NUM_TRIALS):
        tg = torch.Generator().manual_seed(SEED + 1000 + trial)
        a_idx = torch.randint(0, NUM_ATOMS, (1,), generator=tg).item()
        b_idx = torch.randint(0, NUM_ATOMS, (1,), generator=tg).item()
        if a_idx == b_idx:
            b_idx = (b_idx + 1) % NUM_ATOMS
        w_a = codebook[a_idx]
        w_b = codebook[b_idx]
        c = concatenate(w_a, w_b)  # length 2*L_WORD

        # Delta-based recovery: take the deconcatenation split at position L_WORD
        # (the "correct" split for concatenation a · b)
        pairs = deconcatenation_coproduct(c)
        # The pair at i=L_WORD is (a, b) exactly (by construction)
        prefix, suffix = pairs[L_WORD]
        # Project each onto the codebook
        a_hat_idx = codebook_top1(prefix, codebook)
        b_hat_idx = codebook_top1(suffix, codebook)
        if a_hat_idx == a_idx and b_hat_idx == b_idx:
            delta_correct += 1

        # Naive baseline: try to find a, b by similarity of c to length-4 codebook
        # (c is length 8, can't directly compare; would have to slide or compare partial views)
        # Simulate naive: compare prefix-half and suffix-half embeddings
        c_first_half = c[:L_WORD]
        c_second_half = c[L_WORD:]
        # If naive doesn't know L_WORD, it would search at multiple positions; we give it
        # the best case (correct split position).
        nn_a = codebook_top1(c_first_half, codebook)
        nn_b = codebook_top1(c_second_half, codebook)
        if nn_a == a_idx and nn_b == b_idx:
            naive_correct_both += 1
        if nn_a == a_idx or nn_b == b_idx:
            naive_correct_either += 1

    _say(f"\n========= RESULTS =========")
    _say(f"  Delta-based recovery (deconcat at known position):  {delta_correct}/{NUM_TRIALS} ({100*delta_correct/NUM_TRIALS:.0f}%)")
    _say(f"  Naive split + NN match (both):                  {naive_correct_both}/{NUM_TRIALS} ({100*naive_correct_both/NUM_TRIALS:.0f}%)")
    _say(f"  Naive (at least one):                           {naive_correct_either}/{NUM_TRIALS} ({100*naive_correct_either/NUM_TRIALS:.0f}%)")
    _say(f"")
    _say(f"  NOTE: this test is favorable to naive — it knows the split position.")
    _say(f"  The real Hopf advantage shows up when split position is UNKNOWN.")
    _say(f"  Phase B would test against c viewed as 'a generic bound vector' with unknown structure.")

    # Phase B: try ALL splits (this is where Hopf would shine on real-world unknown structures)
    _say(f"\nPhase B: recovery WITHOUT knowing the correct split position")
    delta_b_correct = 0
    for trial in range(NUM_TRIALS):
        tg = torch.Generator().manual_seed(SEED + 2000 + trial)
        a_idx = torch.randint(0, NUM_ATOMS, (1,), generator=tg).item()
        b_idx = torch.randint(0, NUM_ATOMS, (1,), generator=tg).item()
        if a_idx == b_idx:
            b_idx = (b_idx + 1) % NUM_ATOMS
        w_a = codebook[a_idx]
        w_b = codebook[b_idx]
        c = concatenate(w_a, w_b)

        # Delta enumerates ALL splits; for each, score against codebook
        pairs = deconcatenation_coproduct(c)
        best_score = -float("inf")
        best_a_idx, best_b_idx = -1, -1
        for i, (prefix, suffix) in enumerate(pairs):
            if prefix.shape[0] == 0 or suffix.shape[0] == 0:
                continue  # skip trivial splits
            # Find best codebook match for each side
            ai = codebook_top1(prefix, codebook)
            bi = codebook_top1(suffix, codebook)
            # Score: combined similarity
            sim_a = word_similarity(prefix, codebook[ai])
            sim_b = word_similarity(suffix, codebook[bi])
            score = sim_a + sim_b
            if score > best_score:
                best_score = score
                best_a_idx, best_b_idx = ai, bi
        if best_a_idx == a_idx and best_b_idx == b_idx:
            delta_b_correct += 1

    _say(f"  Delta-based recovery (all splits): {delta_b_correct}/{NUM_TRIALS} ({100*delta_b_correct/NUM_TRIALS:.0f}%)")

    out = {"seed": SEED, "L_word": L_WORD, "alphabet_size": ALPHABET_SIZE,
           "num_atoms": NUM_ATOMS, "num_trials": NUM_TRIALS,
           "delta_known_split": delta_correct,
           "delta_all_splits": delta_b_correct,
           "naive_both": naive_correct_both,
           "naive_either": naive_correct_either}
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_wave14a_shuffle_hopf"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
