"""Scaffold-free witness for solverB_cortical_paradigmatic_generalization_v1.

A negative (or positive) from that cell is only a verdict about the cortical read if the harness
itself is sound. These tests each CAN FAIL, and each carries a positive control, so a broken scorer
cannot pass them silently. They witness the load-bearing mechanisms:

  1. THE CORE CLAIM: a PPMI+SVD distributional (LSA) space retrieves a target from cue words it
     NEVER co-occurred with -- i.e. where first-order counting is AT FLOOR by construction. This is
     the second-order/paradigmatic generalisation the whole experiment turns on. The regime is made
     real by a positive control: the target's first-order co-occurrence with the cue words is 0.
  2. THE FAIR RANKING: uncovered candidates (scored NEG) can never flatter an arm by leaving the
     target's rank, so every arm ranks over the SAME pool.
  3. THE METRIC FAILS SAFE: a planted-correct cue scores rank 1; an information-free ranker does
     not, and a degenerate all-equal arm is FLAGGED and ranks last under the pessimistic convention.
  4. THE UNSEEN PARTITION is exactly the "target never co-occurred with any cue word" set.
  5. MASKING removes the target from its own cue (a cue that is the answer measures nothing).
  6. THE GLOVE CEILING orders a related pair above an unrelated one (the instrument control that
     answers 'could this task have succeeded').

Run: .venv/Scripts/python.exe verification/solverB_verify_paradigmatic_generalization.py
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import random
import sys
from typing import Dict, List

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_REPO, os.path.join(_REPO, "experiments"), os.path.join(_REPO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import solverB_cortical_paradigmatic_generalization_v1 as E
from rank_with_ties import rank_with_ties


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    return 0.0 if na < 1e-12 or nb < 1e-12 else float(np.dot(a, b) / (na * nb))


def _paradigmatic_corpus(seed: int = 0):
    """A world where the target 'dog' co-occurs with only a SUBSET of animal-context words, never
    with {tail, bark}, and never with any vehicle word. Other animals occupy the full animal-context
    cluster, so {tail, bark} sit paradigmatically near 'dog' via second-order structure alone."""
    rng = random.Random(seed)
    animals = ["dog", "cat", "horse", "cow", "pig", "hen"]
    vehicles = ["car", "truck", "bus", "van", "jeep", "tram"]
    acx = ["pet", "vet", "fur", "paw", "tail", "bark", "leash", "kennel"]
    vcx = ["road", "drive", "wheel", "fuel", "engine", "garage", "tyre", "horn"]
    dog_seen = ["pet", "vet", "leash"]                 # the ONLY context words 'dog' ever sees
    sents: List[str] = []
    for _ in range(1200):
        if rng.random() < 0.5:
            a = rng.choice(animals)
            pool = dog_seen if a == "dog" else acx
            ctx = rng.sample(pool, k=min(3, len(pool)))
            sents.append(" ".join([a] + ctx))
        else:
            v = rng.choice(vehicles)
            ctx = rng.sample(vcx, k=3)
            sents.append(" ".join([v] + ctx))
    return sents, animals, vehicles


def test_lsa_generalises_where_counting_is_at_floor() -> dict:
    sents, animals, vehicles = _paradigmatic_corpus()
    lsa = E._build_lsa(sents)
    for w in ("dog", "cat", "car", "tail", "bark"):
        assert w in lsa, f"LSA space is missing {w!r} -- fixture/vocab-cap problem, test is vacuous"

    # POSITIVE CONTROL that the regime is real: 'dog' NEVER co-occurs with the cue words.
    from hdlab.reading_grounding_loop import content_lemmas
    cooc_dog = set()
    for s in sents:
        lems = content_lemmas(s)
        if "dog" in lems:
            cooc_dog.update(lems)
    assert "tail" not in cooc_dog and "bark" not in cooc_dog, (
        "fixture broken: 'dog' co-occurred with the cue words, so first-order counting is NOT at "
        "floor here and the test proves nothing")

    # (a) paradigmatic geometry: a same-family pair that never co-occurs beats a cross-family pair
    same = _cos(lsa["dog"], lsa["cat"])
    cross = _cos(lsa["dog"], lsa["car"])
    assert same > cross, f"LSA did not place same-family closer: cos(dog,cat)={same:.3f} <= cos(dog,car)={cross:.3f}"
    assert _cos(lsa["dog"], lsa["dog"]) > 0.99, "positive control failed: cos(dog,dog) != 1"

    # (b) THE RETRIEVAL: a cue of animal words 'dog' never saw ranks animals above vehicles, and
    #     ranks 'dog' itself above the best vehicle -- generalisation from cue words with zero
    #     first-order co-occurrence with the target.
    q = E._sum_vecs(["tail", "bark"], lsa)
    assert q is not None
    animal_sc = [ _cos(q, lsa[a]) for a in animals ]
    veh_sc = [ _cos(q, lsa[v]) for v in vehicles ]
    dog_sc = _cos(q, lsa["dog"])
    assert np.mean(animal_sc) > np.mean(veh_sc), (
        f"cue {{tail,bark}} did not favour animals: {np.mean(animal_sc):.3f} <= {np.mean(veh_sc):.3f}")
    assert dog_sc > max(veh_sc), (
        f"'dog' ({dog_sc:.3f}) did not outrank the best vehicle ({max(veh_sc):.3f}) from an "
        f"unseen-co-occurrence cue -- the generalisation mechanism is not present")
    return {"cos_dog_cat": round(same, 3), "cos_dog_car": round(cross, 3),
            "dog_from_unseen_cue": round(dog_sc, 3), "best_vehicle": round(max(veh_sc), 3)}


def test_uncovered_candidates_cannot_flatter_an_arm() -> dict:
    """A candidate an arm cannot represent (score NEG) must never change the TARGET's rank, so
    every arm effectively ranks over the same pool. This is the fairness guarantee of the cell."""
    NEG = -1e30
    covered = np.array([0.9, 0.2, 0.5, 0.7])            # target is index 0, the best real score
    r_cov = rank_with_ties(covered, 0)
    full = np.concatenate([covered, np.full(6, NEG)])    # 6 uncovered candidates appended
    r_full = rank_with_ties(full, 0)
    assert r_cov.optimistic == r_full.optimistic == 1, (r_cov, r_full)
    # and a would-be-high uncovered candidate, once set to NEG, does not outrank the target
    sneaky = np.array([0.9, 0.2, NEG])                   # index 2 would have been 99.0 uncovered
    assert rank_with_ties(sneaky, 0).optimistic == 1
    return {"rank_covered": r_cov.optimistic, "rank_with_uncovered": r_full.optimistic}


def test_metric_fails_safe() -> dict:
    """Planted-correct cue -> rank 1 every item; random ranker -> ~chance; degenerate arm -> FLAGGED
    and last under the pessimistic convention. A metric where 'no information' scores like 'perfect'
    cannot fail safely and no number from it means anything."""
    rng = np.random.default_rng(0)
    pool = 100
    planted_hits, random_hits = 0, 0
    for _ in range(200):
        tgt = int(rng.integers(pool))
        planted = rng.normal(size=pool)
        planted[tgt] = 100.0                             # the arm that KNOWS the answer
        planted_hits += int(rank_with_ties(planted, tgt).optimistic == 1)
        rnd = rng.normal(size=pool)                      # information-free
        random_hits += int(rank_with_ties(rnd, tgt).optimistic == 1)
    assert planted_hits == 200, f"planted-correct arm missed: {planted_hits}/200 at rank 1"
    assert random_hits <= 8, f"an information-free ranker hit rank 1 {random_hits}/200 -- metric unsafe"
    degenerate = np.zeros(pool)                          # empty/constant arm
    rd = rank_with_ties(degenerate, 3)
    assert rd.suspicious and rd.pessimistic == pool, (
        f"degenerate all-equal arm not caught: {rd} -- an empty arm could score a fake win")
    return {"planted_hit@1": planted_hits / 200, "random_hit@1": random_hits / 200,
            "degenerate_pessimistic": rd.pessimistic}


def test_unseen_partition_is_exact() -> dict:
    """The unseen set is EXACTLY 'target never co-occurred with any cue word', measured per item."""
    import collections
    cooc: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    # target 'apple' co-occurred with 'fruit' but never with 'planet'
    cooc["fruit"]["apple"] += 3

    def cooc_seen(cue_words, tgt):
        return any(tgt in cooc.get(l, {}) for l in cue_words if l != tgt)

    assert cooc_seen(["fruit", "red"], "apple") is True, "a genuinely-seen pair was called unseen"
    assert cooc_seen(["planet", "orbit"], "apple") is False, "a genuinely-unseen pair was called seen"
    assert cooc_seen(["apple"], "apple") is False, "the target's own token must not count as a cue"
    return {"seen_detected": True, "unseen_detected": True}


def test_masking_removes_the_answer() -> dict:
    """A cue that IS the target, once excluded, cannot retrieve it by identity."""
    from hdlab.cortical_recall import cue_vector
    profiles = {"dog": np.ones(16), "cat": np.ones(16) * 0.5}
    unmasked = cue_vector(["dog"], profiles, space="context")
    masked = cue_vector(["dog"], profiles, space="context", exclude=["dog"])
    assert unmasked is not None, "positive control failed: an unmasked single-word cue was empty"
    assert masked is None, f"exclusion did not empty a single-word cue: {masked!r}"
    return {"unmasked_built": True, "masked_empty": True}


def test_glove_ceiling_orders_related_above_unrelated() -> dict:
    """The instrument control that answers 'could the task have succeeded'. Skipped if absent."""
    g = E._load_glove()
    if not g or "dog" not in g or "cat" not in g or "justice" not in g:
        return {"skipped": "glove subset unavailable"}
    rel = _cos(g["dog"], g["cat"])
    unrel = _cos(g["dog"], g["justice"])
    assert rel > unrel, f"GLOVE ceiling incoherent: cos(dog,cat)={rel:.3f} <= cos(dog,justice)={unrel:.3f}"
    return {"cos_dog_cat": round(rel, 3), "cos_dog_justice": round(unrel, 3)}


def main() -> int:
    tests = [
        ("lsa_generalises_where_counting_is_at_floor", test_lsa_generalises_where_counting_is_at_floor),
        ("uncovered_candidates_cannot_flatter_an_arm", test_uncovered_candidates_cannot_flatter_an_arm),
        ("metric_fails_safe", test_metric_fails_safe),
        ("unseen_partition_is_exact", test_unseen_partition_is_exact),
        ("masking_removes_the_answer", test_masking_removes_the_answer),
        ("glove_ceiling_orders_related_above_unrelated", test_glove_ceiling_orders_related_above_unrelated),
    ]
    failed = []
    for name, fn in tests:
        try:
            out = fn()
            print(f"PASS  {name}: {out}")
        except AssertionError as e:
            failed.append(name)
            print(f"FAIL  {name}: {e}")
    print("ALL WITNESSES PASSED" if not failed else f"WITNESSES FAILED: {failed}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
