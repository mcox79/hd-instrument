"""Profile the POS tagger inner loop -- FIRST-HAND confirmation of the _viterbi/pos_features hotspot.

Problem: optimize_the_pos_tagger_viterbi_inner_loop_the_co_dominant_read_cost.
This cell ONLY MEASURES (writes to its own data dir). It does NOT change hdlab/.

It (1) loads the live frontend PosTagger asset, (2) inspects the weight schema (confirms every
emission key is `<base>~<tag>` and every transition key is `tt:<prev>~<cur>` -- the factorization
the optimization relies on), (3) tags a fixed set of real LitBank sentences and cProfiles the tag
loop to confirm _viterbi / pos_features dominate, and (4) times the warm (unprofiled) tag cost as
the baseline the optimization must beat -- with byte-identity of the tag sequence as the invariant.

NO LLM. numpy + pure-python. ASCII-only. Deterministic (fixed doc + fixed sentence slice).
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import cProfile
import pstats
import io
import time
import json

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.pos_tagger import PosTagger, pos_features, pos_transition
from hdlab.scene_segment import parse_conll_sentences

_POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_DOC = os.path.join(_REPO, "data/litbank/coref_conll/1023_bleak_house_brat.conll")
_OUT = os.path.join(_REPO, "data/exp_pos_tagger_profile_v1")


def load_sentences(n_sents, minlen=1, maxlen=100):
    """Return [tokens] for the first n_sents in-range sentences of the doc (raw, untagged)."""
    toks_list = parse_conll_sentences(_DOC)
    out = []
    for toks in toks_list:
        if not (minlen <= len(toks) <= maxlen):
            continue
        out.append(list(toks))
        if len(out) >= n_sents:
            break
    return out


def inspect_schema(tagger):
    """Confirm the weight-key factorization the fast path depends on."""
    W = tagger._perc.weights
    tags = tagger.tags
    tagset = set(tags)
    n_tt = n_emis = n_bad = 0
    bad_samples = []
    emis_prefixes = {}
    for k in W:
        if k.startswith("tt:"):
            n_tt += 1
            continue
        # emission key must be <base>~<tag> with tag in tagset (split on LAST '~')
        if "~" not in k:
            n_bad += 1
            if len(bad_samples) < 5:
                bad_samples.append(k)
            continue
        base, tag = k.rsplit("~", 1)
        if tag not in tagset:
            n_bad += 1
            if len(bad_samples) < 5:
                bad_samples.append(k)
            continue
        n_emis += 1
        pre = base.split(":", 1)[0] if ":" in base else base[:3]
        emis_prefixes[pre] = emis_prefixes.get(pre, 0) + 1
    return {"n_weights": len(W), "n_tags": len(tags), "tags": list(tags),
            "n_transition": n_tt, "n_emission": n_emis, "n_unparseable": n_bad,
            "bad_samples": bad_samples,
            "emission_prefix_hist": dict(sorted(emis_prefixes.items(), key=lambda x: -x[1]))}


def _tag_all(tagger, sents):
    return [tagger.tag(t) for t in sents]


def main(n_sents=250, warm_reps=3):
    os.makedirs(_OUT, exist_ok=True)
    tagger = PosTagger.load(_POS_ASSET)

    schema = inspect_schema(tagger)
    print("SCHEMA: %d weights = %d transition + %d emission + %d UNPARSEABLE  (%d tags)"
          % (schema["n_weights"], schema["n_transition"], schema["n_emission"],
             schema["n_unparseable"], schema["n_tags"]), flush=True)
    print("        tags:", " ".join(schema["tags"]), flush=True)
    print("        emission-base prefixes:", schema["emission_prefix_hist"], flush=True)
    if schema["n_unparseable"]:
        print("        !! UNPARSEABLE SAMPLES:", schema["bad_samples"], flush=True)

    sents = load_sentences(n_sents)
    n_tok = sum(len(t) for t in sents)
    print("sentences=%d tokens=%d (mean len=%.1f)"
          % (len(sents), n_tok, n_tok / max(1, len(sents))), flush=True)

    _tag_all(tagger, sents[:5])   # warm
    times = []
    for _ in range(warm_reps):
        t0 = time.perf_counter()
        _tag_all(tagger, sents)
        times.append(time.perf_counter() - t0)
    times.sort()
    warm = times[len(times) // 2]
    print("WARM tag (median of %d): %.3fs  (%.0f tok/s, %.1f sents/s)"
          % (warm_reps, warm, n_tok / warm, len(sents) / warm), flush=True)

    pr = cProfile.Profile()
    pr.enable()
    _tag_all(tagger, sents)
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("tottime")
    ps.print_stats(15)
    prof_txt = s.getvalue()
    print("\n=== cProfile (tottime, top 15) ===\n" + prof_txt, flush=True)

    hot = {}
    for line in prof_txt.splitlines():
        for key in ("_viterbi", "pos_features", "pos_transition", "weights", "get", "<listcomp>", "array"):
            if key in line:
                hot.setdefault(key.strip(), line.strip())

    with open(os.path.join(_OUT, "profile.json"), "w", encoding="ascii") as f:
        json.dump({"schema": schema, "n_sents": len(sents), "n_tok": n_tok,
                   "warm_s": warm, "warm_reps": warm_reps, "tok_per_s": n_tok / warm,
                   "hot_lines": hot}, f, indent=2)
    print("wrote", os.path.join(_OUT, "profile.json"), flush=True)
    return warm


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=250)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        tg = PosTagger.load(_POS_ASSET)
        sc = inspect_schema(tg)
        ss = load_sentences(8)
        tags = _tag_all(tg, ss)
        assert all(len(tt) == len(s) for tt, s in zip(tags, ss)), "bad tag lengths"
        assert sc["n_unparseable"] == 0, ("unparseable weight keys", sc["bad_samples"])
        print("SELF-TEST PASS: %d sents tagged; schema clean (%d emis + %d trans, 0 bad)"
              % (len(ss), sc["n_emission"], sc["n_transition"]))
    else:
        main(a.n, a.reps)
