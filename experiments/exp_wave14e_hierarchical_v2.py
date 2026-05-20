"""Hierarchical composition v2 — with cleanup BETWEEN levels (Plate 1995 chunking).

Per wave14e_hierarchical_composition_research: cleanup is essential. v1 didn't cleanup,
so noise multiplied across levels. v2 cleans up each level via Hopfield-nearest-atom
projection (the substrate's word "dictionary" snaps the noisy projection to the
closest canonical word).

Test: 3-level hierarchy (bytes → words → phrases). Without cleanup the recovery
should drop sharply with depth. With cleanup it should hold.

Pass: 3-level recovery >=80% with cleanup; demonstrates depth-3+ viable.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N = 4096
K_BYTE = 4         # bytes per word
K_PHRASE = 3       # words per phrase
VOCAB_SIZE = 256
WORD_DICT_SIZE = 200  # canonical word inventory (act as Hopfield codebook)
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
    bound = word_bundles * phrase_pos_atoms
    out = torch.sign(bound.sum(dim=0))
    return torch.where(out == 0, torch.ones_like(out), out)


def hopfield_cleanup(noisy_bundle, dictionary):
    """Snap noisy bundle to the nearest dictionary atom (Hopfield-style)."""
    sims = dictionary @ noisy_bundle / N
    best_idx = int(sims.argmax().item())
    return dictionary[best_idx], best_idx


def decode_phrase_to_words(phrase, phrase_pos_atoms, word_dict, use_cleanup):
    """Decompose phrase at each position. Optionally cleanup to nearest dictionary word."""
    recovered_words = []
    cleanup_indices = []
    for r in range(phrase.shape[0] if phrase.dim() > 1 else K_PHRASE):
        # Project phrase at phrase_pos[r]
        word_noisy = phrase * phrase_pos_atoms[r]
        if use_cleanup:
            cleaned, idx = hopfield_cleanup(word_noisy, word_dict)
            recovered_words.append(cleaned)
            cleanup_indices.append(idx)
        else:
            recovered_words.append(torch.sign(word_noisy))  # at least sign-quantize
            cleanup_indices.append(-1)
    return recovered_words, cleanup_indices


def decode_word_to_bytes(word, byte_atoms, byte_pos_atoms):
    """Decode each byte position from a word bundle."""
    bytes_out = []
    for r in range(K_BYTE):
        proj = word * byte_pos_atoms[r]
        bytes_out.append(int((byte_atoms @ proj).argmax().item()))
    return bytes_out


def main():
    _say(f"Hierarchical v2: 3-level hierarchy with Hopfield cleanup between levels")
    _say(f"  K_byte={K_BYTE}, K_phrase={K_PHRASE}, WORD_DICT_SIZE={WORD_DICT_SIZE}")
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc(VOCAB_SIZE, N, gen).to(DEVICE)
    byte_pos_atoms = make_bsc(K_BYTE, N, gen).to(DEVICE)
    phrase_pos_atoms = make_bsc(K_PHRASE, N, gen).to(DEVICE)

    # Build a word dictionary: 200 canonical words
    fact_gen = torch.Generator().manual_seed(SEED * 7)
    word_byte_indices = torch.randint(0, VOCAB_SIZE, (WORD_DICT_SIZE, K_BYTE), generator=fact_gen).to(DEVICE)
    word_dict = torch.stack([build_word_bundle(byte_atoms, byte_pos_atoms, word_byte_indices[i])
                              for i in range(WORD_DICT_SIZE)])

    # Build NUM_PHRASES phrases, each from K_PHRASE random words drawn from dictionary
    phrase_word_ids = []
    phrase_bundles = []
    for _ in range(NUM_PHRASES):
        wids = torch.randperm(WORD_DICT_SIZE, generator=fact_gen)[:K_PHRASE].tolist()
        phrase_word_ids.append(wids)
        word_bundles = torch.stack([word_dict[w] for w in wids])
        phrase = build_phrase_bundle(word_bundles, phrase_pos_atoms)
        phrase_bundles.append(phrase)

    # Decode WITHOUT cleanup
    correct_words_no_cleanup = 0
    correct_bytes_no_cleanup = 0
    for phrase_idx, phrase in enumerate(phrase_bundles):
        recovered_words, _ = decode_phrase_to_words(phrase, phrase_pos_atoms, word_dict, use_cleanup=False)
        for slot, word_recovered in enumerate(recovered_words):
            recovered_bytes = decode_word_to_bytes(word_recovered, byte_atoms, byte_pos_atoms)
            truth = word_byte_indices[phrase_word_ids[phrase_idx][slot]].tolist()
            if recovered_bytes == truth:
                correct_words_no_cleanup += 1
            correct_bytes_no_cleanup += sum(1 for r, t in zip(recovered_bytes, truth) if r == t)

    # Decode WITH cleanup
    correct_words_cleanup = 0
    correct_bytes_cleanup = 0
    cleanup_word_ids_correct = 0
    for phrase_idx, phrase in enumerate(phrase_bundles):
        recovered_words, cleanup_ids = decode_phrase_to_words(phrase, phrase_pos_atoms, word_dict, use_cleanup=True)
        for slot, (word_recovered, recovered_id) in enumerate(zip(recovered_words, cleanup_ids)):
            recovered_bytes = decode_word_to_bytes(word_recovered, byte_atoms, byte_pos_atoms)
            truth_id = phrase_word_ids[phrase_idx][slot]
            truth = word_byte_indices[truth_id].tolist()
            if recovered_id == truth_id:
                cleanup_word_ids_correct += 1
            if recovered_bytes == truth:
                correct_words_cleanup += 1
            correct_bytes_cleanup += sum(1 for r, t in zip(recovered_bytes, truth) if r == t)

    total_words = NUM_PHRASES * K_PHRASE
    total_bytes = total_words * K_BYTE

    word_acc_no = correct_words_no_cleanup / total_words
    byte_acc_no = correct_bytes_no_cleanup / total_bytes
    word_acc_yes = correct_words_cleanup / total_words
    byte_acc_yes = correct_bytes_cleanup / total_bytes
    cleanup_id_acc = cleanup_word_ids_correct / total_words

    _say(f"\n  Without cleanup:  word_recovery = {word_acc_no*100:.1f}%, byte_recovery = {byte_acc_no*100:.1f}%")
    _say(f"  With cleanup:     word_recovery = {word_acc_yes*100:.1f}%, byte_recovery = {byte_acc_yes*100:.1f}%")
    _say(f"  Cleanup ID match: {cleanup_id_acc*100:.1f}% (Hopfield-snapped to right word in dictionary)")

    delta = byte_acc_yes - byte_acc_no
    _say(f"\n  Cleanup delta: {delta*100:+.1f}pp byte recovery")
    if byte_acc_yes >= 0.8 and cleanup_id_acc >= 0.8:
        _say(f"\n  PASS: cleanup-between-levels enables 3-level hierarchy at {byte_acc_yes*100:.1f}%.")
    elif byte_acc_yes >= 0.5:
        _say(f"\n  PARTIAL: cleanup helps but signal still degraded at this depth.")
    else:
        _say(f"\n  WEAK: even with cleanup, depth-3 hierarchy fails. Try block codes.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14e_hierarchical_v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "K_BYTE": K_BYTE, "K_PHRASE": K_PHRASE, "WORD_DICT_SIZE": WORD_DICT_SIZE,
        "NUM_PHRASES": NUM_PHRASES,
        "word_acc_no_cleanup": word_acc_no, "byte_acc_no_cleanup": byte_acc_no,
        "word_acc_cleanup": word_acc_yes, "byte_acc_cleanup": byte_acc_yes,
        "cleanup_id_accuracy": cleanup_id_acc,
    }, indent=2))


if __name__ == "__main__":
    main()
