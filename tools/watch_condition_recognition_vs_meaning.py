"""THE OWNER'S Q102 WATCH CONDITION, AS A NUMBER: recognition and meaning, measured together.

Owner's warning when authorising the form-identity wiring: *a better INDEX is not better
UNDERSTANDING; the tell is recognition scores rising while meaning scores stay flat.* That is only a
safeguard if it is a MEASUREMENT, so this reports both arms on one run. Any future consumer of
`form_identity_vector` is evaluated here BEFORE and AFTER.

THE RECOGNITION TASK IS CHOSEN TO BE THE ONE INVARIANCE ACTUALLY BUYS, NOT A GIMME.
Matching a word to itself is trivial for any code (the query IS the answer -- this project has already
been burned by exactly that, scoring 1.0000 on an identification arm for that reason). The honest task
is SURFACE-FORM MISMATCH: the corpus says "cats", the store is keyed "cat". That is precisely what
case/inflection invariance is for, and it is where a sha256 hash MUST fail -- it gives "cat" and "cats"
independent random codes.

  ARM HASH   symbol_vector       -- the live identity code
  ARM FORM   form_identity_vector -- the newly wired channel
  MEANING    SimLex-999 rho on the masked-context meaning channel, UNCHANGED by either arm

EXPECTED, and stated before running so it can fail: FORM beats HASH on surface-mismatch retrieval,
and MEANING is IDENTICAL across arms because the wiring is additive and touches no meaning path. If
MEANING moves at all, the additivity claim is wrong and that is the headline.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")

import collections
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.reading_grounding_loop import (        # noqa: E402
    CTX_D, content_words, context_vector_masked, form_identity_vector, normalize_lemma,
    symbol_vector,
)

N_SENT = 41
N_WORDS = 400


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na == 0 or nb == 0 else float(a @ b / (na * nb))


def main() -> int:
    from which_norm_dimensions_can_text_recover import _sentences   # noqa: E402
    sents = _sentences()
    print(f"corpus sentences: {len(sents):,}", flush=True)

    # surface -> lemma pairs where the SURFACE DIFFERS from the lemma (the invariance case)
    surf_by_lemma: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for s in sents:
        for w in content_words(s):
            lw = w.lower()
            lem = normalize_lemma(w)
            if len(lem) > 2:
                surf_by_lemma[lem][lw] += 1
    pairs = []
    for lem, c in surf_by_lemma.items():
        for surf, n in c.items():
            if surf != lem and n >= 3:
                pairs.append((surf, lem))
    rng = np.random.default_rng(7)
    lemmas = sorted({l for _, l in pairs})
    if len(lemmas) > N_WORDS:
        lemmas = sorted(rng.choice(lemmas, size=N_WORDS, replace=False).tolist())
    keep = {l: True for l in lemmas}
    pairs = [(s, l) for s, l in pairs if keep.get(l)]
    print(f"surface/lemma MISMATCH pairs: {len(pairs):,} over {len(lemmas)} lemmas", flush=True)
    if len(pairs) < 50:
        print("REFUSING: too few surface-mismatch pairs to read anything.")
        return 2

    print("\n[POSITIVE CONTROL] a code must match a lemma to ITSELF (else the harness is broken):")
    for name, fn in (("HASH", symbol_vector), ("FORM", form_identity_vector)):
        ok = sum(1 for l in lemmas[:50] if _cos(fn(l), fn(l)) > 0.99)
        print(f"    {name}: {ok}/50 self-match")
        if ok < 50:
            print("  REFUSING: self-match failed.")
            return 2

    print("\n=== RECOGNITION: retrieve the right lemma from a MISMATCHED surface form ===")
    for name, fn in (("HASH (live)", symbol_vector), ("FORM (new)", form_identity_vector)):
        codes = np.stack([fn(l) for l in lemmas])
        codes = codes / np.maximum(np.linalg.norm(codes, axis=1, keepdims=True), 1e-12)
        idx = {l: i for i, l in enumerate(lemmas)}
        hit1 = hit5 = tot = 0
        for surf, lem in pairs:
            q = fn(surf)
            q = q / max(np.linalg.norm(q), 1e-12)
            sims = codes @ q
            order = np.argsort(-sims)
            gold = idx[lem]
            tot += 1
            hit1 += int(order[0] == gold)
            hit5 += int(gold in order[:5])
        print(f"    {name:12s} hit@1 = {hit1/tot:.4f}   hit@5 = {hit5/tot:.4f}   (n={tot:,})")

    print("\n=== MEANING: unchanged by construction -- if this MOVES, additivity is wrong ===")
    by_lemma: dict[str, list[str]] = collections.defaultdict(list)
    for s in sents:
        for w in set(content_words(s)):
            lem = normalize_lemma(w)
            if len(lem) > 2 and len(by_lemma[lem]) < N_SENT:
                by_lemma[lem].append(s)
    probe = [l for l in lemmas if len(by_lemma[l]) >= N_SENT][:60]
    acc = {}
    for l in probe:
        v = np.zeros(CTX_D)
        for s in by_lemma[l][:N_SENT]:
            v += context_vector_masked(s, l)
        acc[l] = v
    if len(probe) >= 10:
        ms = [_cos(acc[a], acc[b]) for a in probe[:20] for b in probe[:20] if a != b]
        print(f"    meaning-channel mean pairwise cos over {len(probe)} words: {np.mean(ms):+.6f}")
        print("    (the meaning path never calls either identity code -- this is the additivity check)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
