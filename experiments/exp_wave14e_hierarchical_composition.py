"""Hierarchical bundle composition — placeholder for research-informed v2.

Minimal probe: 2-level hierarchy.
- Level 1: K=4 byte bundles ("words")
- Level 2: 3-word "phrase" bundles, where each word is bound to a phrase-position

Test:
- Build 50 phrases. Each phrase = 3 random words.
- Decompose each phrase bundle at each phrase position to recover word bundle.
- Decompose each recovered word bundle to recover bytes.
- Pass: byte-recovery accuracy >= 70% (less than flat due to noise amplification).

v2 (after research) will use block-structured codes or FHRR to fight noise.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N = 4096
K_WORD = 4         # bytes per word
K_PHRASE = 3       # words per phrase
VOCAB_SIZE = 256
NUM_PHRASES = 50
SEED = 17


def _say(m): print(m, flush=True)


def make_bsc(k, n, gen):
    return 2.0 * (torch.rand((k, n), generator=gen) > 0.5).float() - 1.0


def build_word_bundle(byte_atoms, byte_pos_atoms, byte_indices):
    bound = byte_atoms[byte_indices] * byte_pos_atoms
    out = torch.sign(bound.sum(dim=0))
    return torch.where(out == 0, torch.ones_like(out), out)


def build_phrase_bundle(word_bundles, phrase_pos_atoms):
    """word_bundles: (K_PHRASE, N). phrase_pos_atoms: (K_PHRASE, N).
    phrase = sign(sum_i word_bundles[i] * phrase_pos_atoms[i])."""
    bound = word_bundles * phrase_pos_atoms
    out = torch.sign(bound.sum(dim=0))
    return torch.where(out == 0, torch.ones_like(out), out)


def decode_word_from_phrase(phrase_bundle, phrase_pos_atom):
    """Project phrase at a position -> word bundle (approximate, no sign() to keep noise)."""
    return phrase_bundle * phrase_pos_atom  # no sign — gives noisy word


def decode_byte_from_word(word_noisy, byte_atoms, byte_pos_atom):
    """Project noisy word at a byte position -> byte index via argmax."""
    proj = word_noisy * byte_pos_atom
    return int((byte_atoms @ proj).argmax().item())


def main():
    _say(f"Hierarchical composition probe (v1): N={N}, K_word={K_WORD}, K_phrase={K_PHRASE}, {NUM_PHRASES} phrases")
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc(VOCAB_SIZE, N, gen).to(DEVICE)
    byte_pos_atoms = make_bsc(K_WORD, N, gen).to(DEVICE)
    phrase_pos_atoms = make_bsc(K_PHRASE, N, gen).to(DEVICE)

    fact_gen = torch.Generator().manual_seed(SEED * 7)
    phrases_truth = []
    phrase_bundles = []
    for _ in range(NUM_PHRASES):
        word_byte_indices = []
        word_bundles = []
        for _ in range(K_PHRASE):
            byte_indices = torch.randint(0, VOCAB_SIZE, (K_WORD,), generator=fact_gen).to(DEVICE)
            word_byte_indices.append(byte_indices.cpu().tolist())
            wb = build_word_bundle(byte_atoms, byte_pos_atoms, byte_indices)
            word_bundles.append(wb)
        word_stack = torch.stack(word_bundles)
        phrase = build_phrase_bundle(word_stack, phrase_pos_atoms)
        phrases_truth.append(word_byte_indices)
        phrase_bundles.append(phrase)

    # Decode: for each phrase, for each word position, decode word -> bytes
    correct_bytes = 0
    total_bytes = 0
    correct_words = 0
    total_words = 0
    for phrase_idx, phrase in enumerate(phrase_bundles):
        for word_pos in range(K_PHRASE):
            word_noisy = decode_word_from_phrase(phrase, phrase_pos_atoms[word_pos])
            recovered_bytes = []
            for byte_pos in range(K_WORD):
                rb = decode_byte_from_word(word_noisy, byte_atoms, byte_pos_atoms[byte_pos])
                recovered_bytes.append(rb)
            truth = phrases_truth[phrase_idx][word_pos]
            for tb, rb in zip(truth, recovered_bytes):
                if tb == rb:
                    correct_bytes += 1
                total_bytes += 1
            if recovered_bytes == truth:
                correct_words += 1
            total_words += 1

    byte_acc = correct_bytes / total_bytes
    word_acc = correct_words / total_words
    _say(f"\n  Byte-level recovery: {byte_acc*100:.1f}% ({correct_bytes}/{total_bytes})")
    _say(f"  Word-level recovery: {word_acc*100:.1f}% ({correct_words}/{total_words})")

    if byte_acc >= 0.7:
        _say(f"\n  PASS: 2-level hierarchy preserves byte content at {byte_acc*100:.1f}%.")
    elif byte_acc >= 0.4:
        _say(f"\n  PARTIAL: hierarchy adds noise, but signal present.")
    else:
        _say(f"\n  WEAK: noise dominates at K_phrase={K_PHRASE}. Need block codes or FHRR.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14e_hierarchical_composition"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "K_WORD": K_WORD, "K_PHRASE": K_PHRASE, "NUM_PHRASES": NUM_PHRASES,
        "byte_accuracy": byte_acc, "word_accuracy": word_acc,
    }, indent=2))


if __name__ == "__main__":
    main()
