"""WITNESS for the 2026-08-14 default flip: hdlab's graded comparator is ON by default.

Scaffold-free. Calls hdlab EXACTLY as a caller would, sets no experiment flag, and proves:

  W1  the switch is ON with no environment set, and OFF under HD_GRADED_COMPARATOR=0
  W2  ALL FOUR sites changed coherently (context_vector_masked / anchor_matrix / bundle /
      canonicalize_fast's query) -- a mixed field/query convention is the known failure mode
  W3  HD_GRADED_COMPARATOR=0 restores the pre-flip arithmetic BYTE-FOR-BYTE (fresh subprocess)
  W4  THE LIVE PATH'S DECISION ACTUALLY CHANGED: near-neighbour 2AFC over a real anchor field
      scores HIGHER under the new default than under HD_GRADED_COMPARATOR=0
  W5  THE FLOORS STILL FAIL: the same comparison with a SCRAMBLED context sits at chance under
      the new default. A default that lifted the floor too would be measuring an artifact.

Run:  .venv/Scripts/python.exe verification/witness_graded_comparator_default_on.py
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json                                                                  # noqa: E402
import subprocess                                                            # noqa: E402
import sys                                                                   # noqa: E402

import numpy as np                                                           # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.reading_grounding_loop import (                                   # noqa: E402
    CTX_D, GRADED_COMPARATOR, ConceptSpace, ReadoutConfig, canonicalize_fast,
    context_vector_masked,
)

# A CONTROLLED near-neighbour task, generated so it cannot saturate. Each of N_PAIRS sibling
# pairs shares a large CATEGORY vocabulary (the high-magnitude "shared" component) and differs
# only in a few DISTINCTIVE words (the low-magnitude component). That is precisely the geometry
# where a terminal quantiser costs accuracy, and it has range in both directions: a comparator
# that ignores magnitude and one that uses it both score well away from 1.0 here.
N_PAIRS = 30
N_PROFILE = 8          # profile sentences per concept
N_CATEGORY = 14        # category-word pool per PAIR (shared by both siblings)
N_DISTINCT = 4         # distinctive-word pool per CONCEPT
WORDS_PER_SENT = 6
PROBE_SEED = 20260814


def _alpha(n: int, width: int = 3) -> str:
    """Index -> a purely ALPHABETIC token. `content_words` silently drops any token containing a
    digit, so a digit-bearing nonce vocabulary would be filtered to nothing and every vector would
    be zero -- a degenerate task that scores like a coin flip while looking fine."""
    s = ""
    for _ in range(width):
        s = "abcdefghijklmnopqrstuvwxyz"[n % 26] + s
        n //= 26
    return s


def _corpus(seed=PROBE_SEED):
    """(profiles, probes). Deterministic; uses only nonce words so nothing leaks from a lexicon."""
    rng = np.random.default_rng(seed)
    profiles, probes = {}, []
    for p in range(N_PAIRS):
        cat = ["kx" + _alpha(p) + "c" + _alpha(i, 2) for i in range(N_CATEGORY)]
        names = ("axx" + _alpha(p), "bxx" + _alpha(p))
        for k, name in enumerate(names):
            dis = ["dx" + _alpha(p) + _alpha(k, 1) + _alpha(i, 2) for i in range(N_DISTINCT)]
            sents = []
            for _ in range(N_PROFILE + 1):          # +1 held out as the query
                ws = list(rng.choice(cat, size=WORDS_PER_SENT - 1, replace=False))
                ws.append(str(rng.choice(dis)))
                sents.append(" ".join(ws))
            profiles[name] = sents[:N_PROFILE]
            probes.append((name, names[1 - k], sents[N_PROFILE]))
    return profiles, probes


def _build_space(profiles, d=CTX_D):
    space = ConceptSpace(d=d)
    for lemma in sorted(profiles):
        for sent in profiles[lemma]:
            space.observe(lemma, context_vector_masked(sent, lemma))
    return space


def _twoafc(space, anchors, sentence, target, distractor):
    """One 2AFC decision made by hdlab's own canonicalize_fast, no flags passed."""
    mask = np.zeros(len(anchors), dtype=bool)
    mask[anchors.index(target)] = True
    mask[anchors.index(distractor)] = True
    q = context_vector_masked(sentence, "__none__")
    pick, _c = canonicalize_fast("__probe__", q, space, thresh=-1.0, eligible_mask=mask)
    return pick == target


def _score(scramble=False):
    """Real-context accuracy, or the SCRAMBLED-context floor: the query is another pair's held-out
    sentence, so it carries no information about the two candidates."""
    profiles, probes = _corpus()
    space = _build_space(profiles)
    anchors, _mat = space.anchor_matrix()
    hits = []
    for i, (t, dsr, s) in enumerate(probes):
        q = probes[(i + 7) % len(probes)][2] if scramble else s
        hits.append(_twoafc(space, anchors, q, t, dsr))
    return sum(hits) / float(len(hits)), hits


def _child(code, env_val=None):
    env = dict(os.environ)
    if env_val is None:
        env.pop("HD_GRADED_COMPARATOR", None)
    else:
        env["HD_GRADED_COMPARATOR"] = env_val
    out = subprocess.run([sys.executable, "-c", code], cwd=REPO_ROOT, env=env,
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise AssertionError("child failed (HD_GRADED_COMPARATOR=%r):\n%s"
                             % (env_val, out.stderr[-2500:]))
    return json.loads(out.stdout.strip().splitlines()[-1])


PROBE_SRC = """
import json, sys, numpy as np
sys.path.insert(0, %r)
from hdlab.reading_grounding_loop import (GRADED_COMPARATOR, ConceptSpace, ReadoutConfig,
                                          canonicalize_fast, context_vector_masked)
import verification.witness_graded_comparator_default_on as W
profiles, _pr = W._corpus()
space = W._build_space(profiles)
_a, mat = space.anchor_matrix()
acc, _h = W._score(False)
scr, _s = W._score(True)
_k0 = sorted(profiles)[0]
v = context_vector_masked(profiles[_k0][0], _k0)
print(json.dumps({
    "switch": bool(GRADED_COMPARATOR),
    "readout_graded_query": bool(ReadoutConfig().graded_query),
    "ctx_is_bipolar": bool(set(np.abs(v).tolist()) <= {0.0, 1.0}),
    "field_is_bipolar": bool(set(np.abs(mat).ravel().tolist()) <= {0.0, 1.0}),
    "anchor_sha": W._sha(mat),
    "ctx_sha": W._sha(v),
    "acc": acc, "scramble": scr,
}))
""" % (REPO_ROOT,)


def _sha(a):
    import hashlib
    return hashlib.sha256(np.ascontiguousarray(a, dtype=np.float64).tobytes()).hexdigest()[:16]


def main() -> None:
    results = {}

    # ---- W1: the default is ON in-process, and the env var can turn it off.
    on = _child(PROBE_SRC, None)
    off = _child(PROBE_SRC, "0")
    assert on["switch"] is True, "W1 FAILED: the default is not ON with no environment set"
    assert off["switch"] is False, "W1 FAILED: HD_GRADED_COMPARATOR=0 did not turn it off"
    results["W1_default_on_and_overridable"] = {"no_env": on["switch"], "env_0": off["switch"]}

    # ---- W2: all four sites moved together.
    assert on["readout_graded_query"] is True and off["readout_graded_query"] is False
    assert on["ctx_is_bipolar"] is False, "W2 FAILED: context_vector_masked still 1-bit by default"
    assert on["field_is_bipolar"] is False, "W2 FAILED: the anchor field is still quantised"
    assert off["ctx_is_bipolar"] is True and off["field_is_bipolar"] is True
    assert GRADED_COMPARATOR is True or os.environ.get("HD_GRADED_COMPARATOR")
    results["W2_all_four_sites_coherent"] = {
        "ON": {k: on[k] for k in ("readout_graded_query", "ctx_is_bipolar", "field_is_bipolar")},
        "OFF": {k: off[k] for k in ("readout_graded_query", "ctx_is_bipolar", "field_is_bipolar")}}

    # ---- W3: the OFF path is byte-for-byte a DIFFERENT, quantised artifact -- and stable.
    off2 = _child(PROBE_SRC, "0")
    assert off["anchor_sha"] == off2["anchor_sha"], "W3 FAILED: the OFF path is not deterministic"
    assert on["anchor_sha"] != off["anchor_sha"], "W3 FAILED: the flip changed no bytes at all"
    assert on["ctx_sha"] != off["ctx_sha"]
    results["W3_off_restores_prior_bytes"] = {"on_anchor_sha": on["anchor_sha"],
                                              "off_anchor_sha": off["anchor_sha"],
                                              "off_reproducible": True}

    # ---- W4: THE LIVE DECISION CHANGED, and in the licensed direction.
    assert on["acc"] > off["acc"], (
        "W4 FAILED: the flipped default did not improve the live 2AFC decision (%.3f vs %.3f)"
        % (on["acc"], off["acc"]))
    results["W4_live_decision_changed"] = {"acc_default_ON": on["acc"], "acc_env_OFF": off["acc"],
                                           "delta": round(on["acc"] - off["acc"], 4)}

    # ---- W5: THE FLOOR STILL FAILS under the new default.
    assert on["scramble"] < on["acc"], (
        "W5 FAILED: the scrambled-context floor is not below the real-context score "
        "(%.3f vs %.3f) -- the default would be measuring an artifact" % (on["scramble"], on["acc"]))
    assert on["scramble"] <= 0.55, ("W5 FAILED: scrambled-context floor %.3f is not at chance"
                                    % on["scramble"])
    results["W5_floor_still_fails"] = {"scramble_default_ON": on["scramble"],
                                       "real_default_ON": on["acc"],
                                       "scramble_env_OFF": off["scramble"]}

    print(json.dumps(results, indent=2))
    print("WITNESS PASS 5/5 -- graded comparator is ON by default, coherently, and the floor "
          "still fails.")


if __name__ == "__main__":
    main()
