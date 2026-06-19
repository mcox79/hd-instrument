"""Wikitext-2 character-level corpus loader.

Tries (in order):
  1. HuggingFace `datasets.load_dataset('wikitext', 'wikitext-2-raw-v1')`
  2. Local cached copy under data/wikitext2_cache/
  3. Synthetic fallback: deterministic 1MB pseudo-text from fixed seed
     (Markov-bigram style; preserves char-vocab statistics adequately for smoke).

ASCII-only output to stdout; suitable for offline runs where HF is unreachable.
"""
from __future__ import annotations

import os
import string
from pathlib import Path
from typing import Optional

_REPO = Path(__file__).resolve().parents[2]
_CACHE_DIR = _REPO / "data" / "wikitext2_cache"
_SYNTHETIC_VOCAB = (
    " " + string.ascii_lowercase + string.ascii_uppercase + string.digits
    + ".,;:'\"!?-\n"
)  # 78 chars total -- proxy for natural-language vocab


def _synthetic_corpus(max_chars: int, seed: int = 1729) -> str:
    """Generate a deterministic English-like pseudo-corpus.

    Uses a simple bigram Markov chain seeded with realistic-ish transitions so
    char-bigram statistics are non-uniform (the LM should be able to learn
    something). This is the LAST-RESORT fallback when HF + local cache miss.
    """
    import random

    rng = random.Random(seed)
    # Seed transitions from a tiny English-ish source.
    words = [
        "the", "and", "of", "to", "in", "a", "is", "that", "for", "on", "with",
        "as", "was", "are", "this", "by", "an", "be", "from", "or", "have",
        "it", "not", "but", "they", "which", "you", "their", "all", "can",
        "her", "what", "would", "make", "about", "more", "time", "no", "up",
        "out", "if", "when", "than", "into", "some", "could", "them", "see",
        "other", "then", "two", "people", "him", "year", "your", "good", "any",
        "much", "us", "way", "even", "new", "want", "because", "these",
        "give", "day", "most", "country", "world", "school", "work", "life",
        "system", "fact", "case", "model", "study", "research", "data",
        "information", "process", "result", "method", "function",
    ]
    out = []
    total = 0
    while total < max_chars:
        sentence_len = rng.randint(6, 14)
        sentence = " ".join(rng.choice(words) for _ in range(sentence_len))
        sentence = sentence.capitalize() + "."
        # Sometimes add a comma somewhere
        if rng.random() < 0.3 and " " in sentence:
            parts = sentence.split(" ")
            mid = len(parts) // 2
            parts[mid] += ","
            sentence = " ".join(parts)
        out.append(sentence)
        total += len(sentence) + 1
        if rng.random() < 0.1:
            out.append("\n")
            total += 1
        else:
            out.append(" ")
            total += 1
    full = "".join(out)
    return full[:max_chars]


def _try_load_hf(max_chars: Optional[int]) -> Optional[str]:
    """Attempt to load Wikitext-2 raw text via HuggingFace datasets. Returns
    None on failure (network unreachable, package missing, etc.).
    """
    try:
        from datasets import load_dataset
    except Exception:
        return None
    try:
        ds = load_dataset("wikitext", "wikitext-2-raw-v1")
    except Exception as e:
        print(f"[data] HF load failed ({type(e).__name__}: {e}); "
              f"will try local cache or synthetic.", flush=True)
        return None
    parts = []
    total = 0
    for row in ds["train"]:
        t = row.get("text", "")
        if not t:
            continue
        parts.append(t)
        total += len(t)
        if max_chars is not None and total >= max_chars:
            break
    full = "".join(parts)
    if max_chars is not None:
        full = full[:max_chars]
    return full


def _try_load_cache(split: str, max_chars: Optional[int]) -> Optional[str]:
    """Load from local cache file if present."""
    p = _CACHE_DIR / f"wikitext2_{split}.txt"
    if not p.exists():
        return None
    try:
        full = p.read_text(encoding="utf-8")
    except Exception:
        return None
    if max_chars is not None:
        full = full[:max_chars]
    return full


def _save_cache(split: str, text: str) -> None:
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        (_CACHE_DIR / f"wikitext2_{split}.txt").write_text(text, encoding="utf-8")
    except Exception:
        pass  # cache is opportunistic; never block on failure


def wikitext2_char_corpus(
    split: str = "train",
    max_chars: Optional[int] = None,
    allow_synthetic: bool = True,
) -> str:
    """Return a character corpus for the requested split.

    Resolution order:
      1. Local cache under data/wikitext2_cache/wikitext2_<split>.txt
      2. HuggingFace `datasets` library
      3. Synthetic fallback (deterministic, seed=1729) iff allow_synthetic.

    Args:
        split:        "train" | "validation" | "test"
        max_chars:    cap on returned length; None = full available text.
        allow_synthetic: if True, fall back to a synthetic corpus when neither
                         HF nor local cache is reachable. Set False to force a
                         real-data run (raises RuntimeError on no data).

    Returns:
        A string of length min(max_chars, len(available)).
    """
    # Try cache first (cheapest, offline-safe)
    text = _try_load_cache(split, max_chars)
    if text is not None and len(text) >= max(1024, (max_chars or 0) // 2):
        return text

    # Try HF
    text = _try_load_hf(max_chars)
    if text is not None and len(text) >= max(1024, (max_chars or 0) // 2):
        _save_cache(split, text)
        return text

    if not allow_synthetic:
        raise RuntimeError(
            f"Wikitext-2 split={split} not reachable via HF or local cache "
            f"({_CACHE_DIR}); set allow_synthetic=True or stage the cache."
        )

    target = max_chars if max_chars is not None else 1_000_000
    # Slightly different seed per split so val/test differ from train.
    seed = {"train": 1729, "validation": 1733, "test": 1741}.get(split, 1729)
    text = _synthetic_corpus(target, seed=seed)
    print(f"[data] using synthetic fallback corpus for split={split}: "
          f"{len(text)} chars (seed={seed})", flush=True)
    return text


def char_vocab_from_corpus(text: str) -> list:
    """Return sorted list of unique chars in `text` (canonical vocab order)."""
    return sorted(set(text))


def _selftest() -> None:
    text_smoke = wikitext2_char_corpus(split="train", max_chars=5000)
    assert len(text_smoke) >= 1000, f"smoke corpus too short: {len(text_smoke)}"
    vocab = char_vocab_from_corpus(text_smoke)
    assert len(vocab) >= 10, f"smoke vocab too small: {len(vocab)}"
    # Determinism: same call returns same content (mod cache)
    text_smoke_2 = wikitext2_char_corpus(split="train", max_chars=5000)
    assert text_smoke[:1000] == text_smoke_2[:1000], "non-deterministic loader"
    print(f"[data selftest] PASS train smoke: {len(text_smoke)} chars, "
          f"vocab={len(vocab)}", flush=True)


if __name__ == "__main__":
    _selftest()
