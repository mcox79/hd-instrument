"""Scaffold-free witness for hdlab/perirhinal_conjunctive.py.

Independent of the module's own self-tests: this file re-derives what it checks rather than
calling `_run_all_selftests()`.

Four gates, each of which CAN FAIL:
  G1 DEFAULT-OFF          -- importing the organ leaves the live reader BIT-IDENTICAL, and the
                             module switch is False.
  G2 REACHES-THE-READER   -- passed explicitly, the organ actually reaches the reader through the
                             pre-existing `process_sentence(encoder=...)` port and CHANGES the
                             stored profile (a wiring that changes nothing is not wired).
  G3 SAME-VECTOR-SPACE    -- the bag the organ conjoins is bit-identical to the live
                             `context_vector_masked`, so this is a metric SWAP and not a second,
                             incomparable space.
  G4 DISCRIMINATOR        -- the conjunctive metric is strictly sharper than the flat bag at
                             partial overlap and identical at full overlap. If this fails, the
                             organ is not doing the thing it claims.

Run:  .venv/Scripts/python.exe verification/verify_perirhinal_conjunctive_default_off.py
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

import hdlab.reading_grounding_loop as RGL
from hdlab.hd_fact_store import HDFactStore

SENT = "The zibbo flickered by the lantern in the storm above the quiet harbour."
SEEDS = ["lantern", "storm", "harbour", "fire"]


def _read(encoder):
    store = HDFactStore(n_dim=512, seed=11,
                        relation_cardinality={RGL.KNOWN_RELATION: "FUNCTIONAL",
                                              RGL.MEANING_RELATION: "FUNCTIONAL"},
                        use_index=True)
    st = RGL.ReadingLoopState(store=store)
    RGL.seed_known_words(st, SEEDS, source="witness")
    RGL.process_sentence(st, SENT, "e0", pass_idx=0, encoder=encoder)
    return st


def main() -> int:
    # baseline captured BEFORE the organ module is imported at all
    pre = _read(None)
    pre_prof = {a: pre.space.bundle(a).copy() for a in pre.space.anchors()}

    import hdlab.perirhinal_conjunctive as PC

    # ---- G1 default-off
    post = _read(None)
    g1_switch = (PC.PERIRHINAL_CONJUNCTIVE is False)
    g1_same = (sorted(pre_prof) == post.space.anchors()) and all(
        np.array_equal(pre_prof[a], post.space.bundle(a)) for a in pre_prof)
    assert g1_switch, "G1 FAIL: PERIRHINAL_CONJUNCTIVE defaulted ON"
    assert g1_same, "G1 FAIL: importing the organ perturbed the live default reader path"

    # ---- G2 reaches the reader and changes something
    on = _read(PC.PerirhinalEncoder(d=RGL.CTX_D, mode="pair"))
    assert on.space.anchors() == post.space.anchors(), "G2 FAIL: organ changed the anchor population"
    n_changed = sum(0 if np.array_equal(on.space.bundle(a), post.space.bundle(a)) else 1
                    for a in on.space.anchors())
    assert n_changed == len(on.space.anchors()) and n_changed > 0, \
        "G2 FAIL: the organ did not change every profile it should have (%d of %d)" % (
            n_changed, len(on.space.anchors()))
    for a in on.space.anchors():
        S = RGL.context_vector_masked(SENT, a, graded=True)
        m = len(PC.masked_content_tokens(SENT, a))
        assert np.array_equal(on.space.bundle(a), (S * S - float(m)) / 2.0), \
            "G2 FAIL: stored profile for %r is not the conjunctive code" % (a,)

    # ---- G3 same vector space
    g3 = 0
    for a in list(post.space.anchors()) + ["zibbo", "flicker"]:
        toks = PC.masked_content_tokens(SENT, a)
        assert np.array_equal(PC.bag_vector(toks, RGL.CTX_D),
                              RGL.context_vector_masked(SENT, a, graded=True)), \
            "G3 FAIL: the organ's bag is not the live bag for %r" % (a,)
        g3 += 1

    # ---- G4 discriminator: sharper at partial overlap, identical at full
    rng = np.random.default_rng(4242)
    d, m = 4096, 10
    table = []
    for j in (2, 5, 8, 10):
        bc, pc = [], []
        for _ in range(15):
            shared = [rng.choice([-1.0, 1.0], size=d) for _ in range(j)]
            A = np.sum(shared + [rng.choice([-1.0, 1.0], size=d) for _ in range(m - j)], axis=0)
            B = np.sum(shared + [rng.choice([-1.0, 1.0], size=d) for _ in range(m - j)], axis=0)
            PA, PB = PC.pair_conjunction(A, m), PC.pair_conjunction(B, m)
            f = lambda x, y: float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-12))
            bc.append(f(A, B))
            pc.append(f(PA, PB))
        mb, mp = float(np.mean(bc)), float(np.mean(pc))
        table.append({"shared": j, "of": m, "bag_cos": round(mb, 4), "conj_cos": round(mp, 4)})
        if j < m:
            assert mp < mb - 1e-3, "G4 FAIL: conjunctive metric is not sharper at j=%d (%.4f vs %.4f)" % (j, mp, mb)
        else:
            assert abs(mp - 1.0) < 1e-6 and abs(mb - 1.0) < 1e-6, \
                "G4 FAIL: full overlap did not give cosine 1.0"

    rep = {
        "witness": "verify_perirhinal_conjunctive_default_off",
        "G1_default_off_and_live_path_bit_identical": bool(g1_switch and g1_same),
        "G2_reaches_reader_via_existing_port_and_changes_profile": {"n_profiles_changed": n_changed},
        "G3_same_vector_space_as_live_bag": {"n_checked": g3},
        "G4_conjunctive_metric_is_sharper_at_partial_overlap": table,
        "result": "PASS 4/4",
    }
    print(json.dumps(rep, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
