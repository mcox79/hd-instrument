"""Landing witness for hdlab/diagnostic_context_wsd.py -- the biased-competition diagnostic-context sense readout
promoted from the owner-DONE build_sg_lite. Asset-independent + can-fail: constructed vectors reproduce the
mechanism (the diagnostic word is identified; biased competition sharpens the pick over the flat topic average)
and the SHUFFLED-DIAGNOSTICITY twin LOSES (the mechanism's own W8b control -- correct diagnostic words carry the
signal). No embeddings/gold/LLM. Run: .venv/Scripts/python.exe verification/test_diagnostic_context_wsd_organ.py
"""
import os
import sys

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.diagnostic_context_wsd import (
    diagnosticity, diagnostic_query, diagnostic_context_scores, flat_context_scores,
    sense_gloss_vec, pick_sense)

_n = 0


def _ok(cond, msg):
    global _n
    assert cond, "FAIL: " + msg
    _n += 1
    print("  PASS " + msg, flush=True)


def _unit(v):
    v = np.asarray(v, dtype=np.float64)
    return v / (np.linalg.norm(v) + 1e-12)


def _item(rng, S=2, D=8, n_generic=6, diag_strength=0.9):
    """Construct one WSD item: S orthogonal sense glosses; the gold sense gets ONE diagnostic context word
    close to its gloss; plus n_generic topic words equidistant from all senses (in unused dims) that DOMINATE
    a flat average. Returns (context_vecs (W,D) unit, gloss_vecs (S,D) unit, gold_idx)."""
    gold = int(rng.integers(S))
    G = np.zeros((S, D));
    for s in range(S):
        G[s, s] = 1.0                                   # orthogonal sense glosses e_0..e_{S-1}
    # diagnostic word: mostly the gold sense's direction, a touch of a competitor
    other = (gold + 1) % S
    wd = np.zeros(D); wd[gold] = diag_strength; wd[other] = 1.0 - diag_strength
    ctx = [_unit(wd)]
    # generic topic words: live in the unused dims (>= S) -> equidistant (0 cosine) to every sense gloss
    for k in range(n_generic):
        g = np.zeros(D); g[S + (k % (D - S))] = 1.0; g[S + ((k + 1) % (D - S))] = 0.6
        ctx.append(_unit(g))
    C = np.stack(ctx)
    return C, G, gold


def main():
    rng = np.random.default_rng(0)

    # 1. MECHANISM: the diagnostic word is identified (highest weight); generic topic words get ~0.
    C, G, gold = _item(rng)
    d = diagnosticity(C, G)
    _ok(int(np.argmax(d)) == 0 and d[0] > 1e-6, "diagnosticity identifies the diagnostic context word (idx 0)")
    _ok(np.all(d[1:] <= 1e-9), "topic-generic context words get ~0 diagnosticity")

    # 2. BIASED COMPETITION beats the flat topic average on a single hard item (flat blurs -> wrong/tied; diag -> gold)
    ds = diagnostic_context_scores(C, G)
    fs = flat_context_scores(C, G)
    _ok(int(np.argmax(ds)) == gold, "diagnostic-context readout picks the gold sense")
    diag_margin = ds[gold] - np.max(np.delete(ds, gold))
    flat_margin = fs[gold] - np.max(np.delete(fs, gold))
    _ok(diag_margin > flat_margin, "biased competition SHARPENS the gold margin over the flat topic average")

    # 3. W8b CONTROL (batch): real diagnostic accuracy > shuffled-diagnosticity twin (correct words carry signal)
    N = 200
    real_ok = shuf_ok = 0
    for i in range(N):
        C, G, gold = _item(np.random.default_rng(100 + i))
        if int(np.argmax(diagnostic_context_scores(C, G))) == gold:
            real_ok += 1
        tw = np.random.default_rng(900 + i)
        if int(np.argmax(diagnostic_context_scores(C, G, shuffle_rng=tw))) == gold:
            shuf_ok += 1
    _ok(real_ok / N > shuf_ok / N, "shuffled-diagnosticity twin LOSES (real %.3f > shuffled %.3f)"
        % (real_ok / N, shuf_ok / N))
    _ok(real_ok / N >= 0.95, "real diagnostic readout solves the constructed items (acc %.3f)" % (real_ok / N))

    # 4. graceful fallback: no diagnostic context word -> falls back to the flat mean (no crash, unit query)
    C0 = np.stack([_unit(np.eye(8)[4]), _unit(np.eye(8)[5])])   # both generic (unused dims), 0 diagnosticity
    G0 = np.stack([_unit(np.eye(8)[0]), _unit(np.eye(8)[1])])
    q = diagnostic_query(C0, G0)
    _ok(abs(np.linalg.norm(q) - 1.0) < 1e-6, "non-diagnostic context -> unit flat-mean fallback (no crash)")

    # 5. CONVENIENCE ENTRY POINT (the solver-facing API): pick_sense over words + a vec_lookup picks the gold
    #    sense; sense_gloss_vec builds a unit signature; OOV context -> None fallback.
    D = 8
    vecs = {"diagword": np.zeros(D), "gen_a": np.zeros(D), "gen_b": np.zeros(D),
            "gloss0": np.zeros(D), "gloss1": np.zeros(D)}
    vecs["gloss0"][0] = 1.0; vecs["gloss1"][1] = 1.0                 # two orthogonal sense glosses
    vecs["diagword"][0] = 0.9; vecs["diagword"][1] = 0.1            # a diagnostic word for sense 0
    vecs["gen_a"][4] = 1.0; vecs["gen_b"][5] = 1.0                  # topic-generic words (unused dims)
    lookup = lambda w: vecs.get(w)
    idx = pick_sense(["diagword", "gen_a", "gen_b"], [["gloss0"], ["gloss1"]], lookup)
    _ok(idx == 0, "pick_sense (words + vec_lookup) picks the gold sense")
    sv = sense_gloss_vec(["gloss0", "gen_a"], lookup)
    _ok(sv is not None and abs(np.linalg.norm(sv) - 1.0) < 1e-6, "sense_gloss_vec builds a unit signature")
    _ok(pick_sense(["oov1", "oov2"], [["gloss0"], ["gloss1"]], lookup) is None,
        "pick_sense returns None on out-of-vocab context (caller keeps its fallback)")

    print("%d/%d checks passed" % (_n, _n), flush=True)
    print("SELF-TEST PASSED", flush=True)


if __name__ == "__main__":
    main()
