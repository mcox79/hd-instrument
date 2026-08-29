"""read_terminal_bundle_stores_normalize_per_component_not_pooled -- the sign()->graded FIX on the REAL overloading callers.

DRILL 3 measured (on a synthetic bipolar grid) that sign(sum) discards the graded vote margin a direction-sensitive
read needs under load, and that dropping sign() for the GRADED sum recovers it (+0.17 @overload). This cell lands that
finding on the REAL hdlab organs at their ACTUAL overloading sites, each on its OWN readout, with an info-free twin.

CALLER A -- `hdlab.situation_focus.FlatFocus` (the working-memory focus; Cowan bounded-capacity superposition).
  build() does `focus = _bipolar_quantize( sum_j bind(pos_j, event_j) )` -- the sign() over a superposition of N
  events. query(j, role) unbinds the position key then unbinds the role + cleanup (EventBundleCodec.query_role_vec).
  As N grows this OVERLOADS. FIX: skip the focus-level quantize (keep the graded integer superposition); the readout
  (bipolar unbind = multiply; cleanup = codebook matmul + argmax) works unchanged on a graded focus. (The per-event
  4-role bundle stays quantized -- low load, neutral, matches DRILL 3's m<=16 no-gap regime.)

CALLER B -- `hdlab.char_positional_encoder.CharPositionalEncoder.encode_sentence` (orthographic spoke; bag-of-word HDs).
  encode_sentence does `_sign_bundle( [encode_word(w) for w in words] )` -- the sign() over W word-HDs. Read by cosine
  (word/sentence matching). As W grows this OVERLOADS. FIX: drop the sentence-level sign (keep the graded word sum),
  read by the same cosine. (encode_word's char-level sign stays -- few chars, low load.)

METRIC per caller: recovery/retrieval accuracy on its own read, swept over LOAD, sign vs graded, with a paired
bootstrap CI over trials and an INFO-FREE TWIN (query the WRONG position / a non-member word) that must collapse.

Run:
  .venv/Scripts/python.exe experiments/exp_read_terminal_divnorm_sign_real_callers_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_read_terminal_divnorm_sign_real_callers_v1.py --run
"""
from __future__ import annotations

import argparse
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import torch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.event_bundle import EventBundleCodec, DEFAULT_ROLES  # noqa: E402
from hdlab.situation_focus import FlatFocus  # noqa: E402
from hdlab.role_slot_summarizer import _bipolar_bind  # noqa: E402
from hdlab.char_positional_encoder import CharPositionalEncoder  # noqa: E402

N_DIM = 2048
BASE_SEED = 20260829
N_BOOT = 2000


# ============================ CALLER A: situation_focus.FlatFocus ============================
class GradedFlatFocus(FlatFocus):
    """FlatFocus with the focus-level sign() (`_bipolar_quantize`) DROPPED -- the graded superposition. Everything
    else (position keys, per-event bundles, the query path) is byte-identical to the landed FlatFocus."""

    def build(self, event_vecs):
        acc = torch.zeros(self.codec.n_dim, dtype=torch.float32)
        for j, ev in enumerate(event_vecs):
            acc = acc + _bipolar_bind(self.pos_keys[j], ev)
        self.focus = acc                       # <-- NO _bipolar_quantize (graded), vs FlatFocus's sign
        self.n = len(event_vecs)
        return self.focus


def _focus_trial(n_events, seed, graded, twin=False):
    rng = np.random.default_rng(seed)
    vocab = [f"f{i}" for i in range(60)]
    codec = EventBundleCodec(N_DIM, roles=DEFAULT_ROLES, seed=seed % 100000)
    codec.prime_symbols(vocab)
    truth = []
    events = []
    for _ in range(n_events):
        rf = {r: vocab[int(rng.integers(0, len(vocab)))] for r in DEFAULT_ROLES}
        truth.append(rf)
        events.append(codec.encode_event(rf))
    focus = (GradedFlatFocus if graded else FlatFocus)(codec, max_items=n_events, seed=seed % 100000)
    focus.build(events)
    correct = total = 0
    for j in range(n_events):
        qj = (j + 1) % n_events if twin else j          # twin: query the WRONG position
        for role in DEFAULT_ROLES:
            got, _ = focus.query(qj, role)
            correct += int(got == truth[j][role])
            total += 1
    return correct / total


def caller_a(loads=(2, 4, 8, 12, 16, 24), n_trials=24):
    res = {"loads": list(loads), "sign": {}, "graded": {}, "twin": {}}
    for n in loads:
        s = [_focus_trial(n, BASE_SEED + 100 * t + n, graded=False) for t in range(n_trials)]
        g = [_focus_trial(n, BASE_SEED + 100 * t + n, graded=True) for t in range(n_trials)]
        tw = [_focus_trial(n, BASE_SEED + 100 * t + n, graded=True, twin=True) for t in range(n_trials)]
        res["sign"]["n=%d" % n] = s
        res["graded"]["n=%d" % n] = g
        res["twin"]["n=%d" % n] = tw
    return res


# ============================ CALLER B: char_positional_encoder.encode_sentence ============================
_WORDS = ("the quick brown fox jumps over a lazy dog river boat sailor captain crew water ship vessel dock harbor "
          "storm wind rope anchor deck cargo mast sail wave tide port stern bow hull keel").split()


def _sentence_trial(n_words, seed, graded, twin=False):
    """Encode a sentence of n_words distinct words; query word-membership by cosine (a member word must score higher
    than a non-member). sign vs graded at the SENTENCE-bundling level (word-level sign kept)."""
    rng = np.random.default_rng(seed)
    enc = CharPositionalEncoder(n_dim=N_DIM, seed_prefix="SPOKE1")
    idx = rng.permutation(len(_WORDS))
    members = [_WORDS[i] for i in idx[:n_words]]
    nonmembers = [_WORDS[i] for i in idx[n_words:n_words + n_words]]  # equal-size foil set
    word_hd = {w: enc.encode_word(w) for w in members + nonmembers}
    parts = np.stack([word_hd[w] for w in members], axis=0)
    if graded:
        sent = parts.sum(axis=0)                                     # graded word sum (drop sentence-level sign)
    else:
        s = parts.sum(axis=0); sent = np.sign(s).astype(np.float32); sent[sent == 0] = 1.0   # the landed sign()
    sn = sent / (np.linalg.norm(sent) + 1e-9)
    pool = nonmembers if twin else members                          # twin: "recover" the FOILS (must fail)
    correct = 0
    for w in pool:
        wn = word_hd[w] / (np.linalg.norm(word_hd[w]) + 1e-9)
        member_score = float(np.dot(sn, wn))
        # rank vs the best NON-member: a true member should beat every foil
        best_foil = max(float(np.dot(sn, word_hd[f] / (np.linalg.norm(word_hd[f]) + 1e-9))) for f in nonmembers)
        correct += int(member_score > best_foil)
    return correct / len(pool)


def caller_b(loads=(2, 4, 8, 12, 16, 24), n_trials=24):
    res = {"loads": list(loads), "sign": {}, "graded": {}, "twin": {}}
    for n in loads:
        if n * 2 > len(_WORDS):
            continue
        s = [_sentence_trial(n, BASE_SEED + 200 * t + n, graded=False) for t in range(n_trials)]
        g = [_sentence_trial(n, BASE_SEED + 200 * t + n, graded=True) for t in range(n_trials)]
        tw = [_sentence_trial(n, BASE_SEED + 200 * t + n, graded=True, twin=True) for t in range(n_trials)]
        res["sign"]["n=%d" % n] = s
        res["graded"]["n=%d" % n] = g
        res["twin"]["n=%d" % n] = tw
    return res


def _boot_delta(g, s, rng, n_boot=N_BOOT):
    g = np.asarray(g); s = np.asarray(s); n = len(g)
    idx = rng.integers(0, n, size=(n_boot, n))
    d = g[idx].mean(1) - s[idx].mean(1)
    return float(g.mean() - s.mean()), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def _report(name, res, rng):
    print("\n  %s -- recovery accuracy, sign(landed) vs graded(fix), over load:" % name)
    print("    load    sign    graded   delta(graded-sign)  [CI]            twin")
    for k in res["sign"]:
        s = res["sign"][k]; g = res["graded"][k]; tw = res["twin"][k]
        d, lo, hi = _boot_delta(g, s, rng)
        sep = "CI-sep" if (lo > 0 or hi < 0) else "  --  "
        print("    %-7s %.3f   %.3f    %+.3f [%+.3f,%+.3f] %s   %.3f" %
              (k, float(np.mean(s)), float(np.mean(g)), d, lo, hi, sep, float(np.mean(tw))))


def _self_test():
    # MEASURED on the real callers (AVERAGED over trials -- single seeds are high-variance): graded >= sign, the
    # gap GROWS with load, but the payoff is MODEST (+0.03-0.045 at high overload) -- MUCH smaller than the
    # synthetic random-atom grid (+0.17) because the real callers have CORRELATED (encode_sentence: char-based word
    # HDs) and NESTED (FlatFocus: position->role->filler double-unbind) structure that dampens the graded margin.
    ns = 12
    a_s = float(np.mean([_focus_trial(24, BASE_SEED + 100 * t + 24, graded=False) for t in range(ns)]))
    a_g = float(np.mean([_focus_trial(24, BASE_SEED + 100 * t + 24, graded=True) for t in range(ns)]))
    a_tw = float(np.mean([_focus_trial(24, BASE_SEED + 100 * t + 24, graded=True, twin=True) for t in range(ns)]))
    assert a_g >= a_s - 0.005, "FlatFocus overload (avg): graded (%.3f) should be >= sign (%.3f)" % (a_g, a_s)
    assert a_tw < a_g - 0.2, "FlatFocus twin (wrong position) must collapse: %.3f vs %.3f" % (a_tw, a_g)
    b_s = float(np.mean([_sentence_trial(12, BASE_SEED + 200 * t + 12, graded=False) for t in range(ns)]))
    b_g = float(np.mean([_sentence_trial(12, BASE_SEED + 200 * t + 12, graded=True) for t in range(ns)]))
    assert b_g >= b_s - 0.005, "encode_sentence overload (avg): graded (%.3f) should be >= sign (%.3f)" % (b_g, b_s)
    print("[self-test] PASS (avg over %d trials): graded >= sign on BOTH real callers but MODEST -- "
          "FlatFocus @n=24 graded %.3f vs sign %.3f; encode_sentence @n=12 graded %.3f vs sign %.3f; "
          "twin collapses %.3f" % (ns, a_g, a_s, b_g, b_s, a_tw))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        _self_test()
        raise SystemExit(0)
    _self_test()
    rng = np.random.default_rng(BASE_SEED)
    print("=== sign()->graded on the REAL overloading callers (each on its OWN readout) N_DIM=%d ===" % N_DIM)
    _report("CALLER A: situation_focus.FlatFocus (role recovery from N superposed events)", caller_a(), rng)
    _report("CALLER B: char_positional_encoder.encode_sentence (word membership by cosine)", caller_b(), rng)
