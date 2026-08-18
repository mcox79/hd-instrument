"""The realised-condition convention.

Incident this fixes (2026-08-15, .claude/scan-out/identical-across-models.json,
GROUP_2980c296a8d1baba): four cells named exp_t5c_pp225_kb10k/50k/100k/500k_v1 each set a
different N_FACTS config constant (10000..500000), then sliced a hardcoded 249-word literal
pool: `subs = list(dict.fromkeys(DISC_POOL))[:N_FACTS]`. Above 249 the slice is a no-op, so
all four ran identically at 149 train / 100 test, and the declared condition (the directory
name, the config constant) never reached the measured path. Nothing in metrics.json said so --
the file recorded the SCORE but not the CONDITION. The fix the incident's author proposed,
verbatim: "record the REALISED condition beside the score. `realised_n_facts=len(facts)`
written next to a directory named kb500k would have exposed [this] on day one."

THE CONVENTION.

Any experiment cell whose name, config, or verdict asserts a scale, size, model, or count MUST
record what it ACTUALLY realised at run time, beside the score -- not the config value, the
value measured from the object that was actually used. Concretely, into metrics.json (or
per_seed, if per-seed values can differ):

    realised_n_facts = len(facts)              # not N_FACTS
    realised_N       = int(K.shape[0])          # not the config N
    realised_model    = str(getattr(mdl, "name_or_path", MODEL))   # not the MODEL constant
    realised_n_seeds  = len(per_seed)           # not the config seed count

The rule of thumb: if you can name the config constant that a directory name or a verdict_msg
claims, you can name the ONE LINE that measures it back off the object that was actually built
or iterated, and that line costs one call. Compare that to the other incident in the same
fragment (GROUP_f9db26aa72937aec): five models gave bit-identical results because the only
per-run quantity written was a saturated integer ratio (recall = 2000/2000 in every arm) plus
two config constants -- the model identity itself was never written at all. A `realised_model`
field would not have prevented the saturation, but it would have made the collision
self-explaining instead of alarming.

This module is intentionally thin -- a naming convention plus one merge helper, not a schema
enforcer (cells vary too much for one shape to fit). Use `attach_realised` at the point in the
cell where metrics.json is assembled.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

REALISED_PREFIX = "realised_"


def attach_realised(metrics: dict, **realised) -> dict:
    """Merge realised_-prefixed condition fields into a metrics dict, in place, and return it.

    Every kwarg name is prefixed with `realised_` if not already prefixed, so callers can write
    `attach_realised(metrics, n_facts=len(facts))` and get `metrics["realised_n_facts"]`.
    Raises ValueError on an empty call -- an empty attach is very likely a forgotten argument,
    not a deliberate no-op (there is no legitimate reason to call this with nothing to record).
    """
    if not realised:
        raise ValueError(
            "attach_realised() called with no fields -- if the cell has no varying condition "
            "to record, do not call this helper at all; an empty call is almost certainly a "
            "forgotten argument."
        )
    for k, v in realised.items():
        key = k if k.startswith(REALISED_PREFIX) else REALISED_PREFIX + k
        metrics[key] = v
    return metrics


def realised_keys(metrics: dict) -> list:
    """Return the realised_-prefixed keys present at the top level of a metrics dict."""
    if not isinstance(metrics, dict):
        return []
    return sorted(k for k in metrics if isinstance(k, str) and k.startswith(REALISED_PREFIX))


def declares_a_condition(name: str) -> bool:
    """Heuristic: does an experiment/directory NAME assert a scale, size, model, or count?

    Used by realised_condition_checker.py to decide whether a cell is in-scope for this
    convention at all. Matches the shapes actually seen in this repo: N65536, kb10k/kb500k,
    3seed, M2000, and bare large integers with a k/m suffix. Deliberately permissive (a false
    positive here just means "checked and found nothing to compare", not a wrong verdict).
    """
    import re
    patterns = [
        r"[_-][Nn]\d{3,}",          # N65536, n4096
        r"\bkb\d+[km]?\b",          # kb10k, kb500k, kb1500
        r"\d+seed",                  # 3seed
        r"[_-][Mm]\d{3,}",          # M2000
        r"\d+[km]_v\d",              # 500k_v1
    ]
    return any(re.search(p, name) for p in patterns)


def _selftest():
    m = {}
    attach_realised(m, n_facts=249, model="EleutherAI/pythia-160m")
    assert m == {"realised_n_facts": 249, "realised_model": "EleutherAI/pythia-160m"}, m
    m2 = {}
    attach_realised(m2, realised_n=65536)  # already-prefixed kwarg name is not double-prefixed
    assert m2 == {"realised_n": 65536}, m2
    assert realised_keys(m) == ["realised_model", "realised_n_facts"]
    assert realised_keys({"n_facts": 249}) == []  # NEGATIVE: unprefixed key is not picked up
    assert realised_keys("not a dict") == []       # NEGATIVE: non-dict input degrades safely

    threw = False
    try:
        attach_realised({})
    except ValueError:
        threw = True
    assert threw, "attach_realised({}) must raise on an empty call"  # NEGATIVE

    assert declares_a_condition("exp_t5c_pp225_kb500k_v1") is True     # POSITIVE
    assert declares_a_condition("exp_b2_self_improving_routing_3seed_cpu_v1") is True  # POSITIVE
    assert declares_a_condition("exp_wave14_betV_N65536_v1") is True   # POSITIVE
    assert declares_a_condition("exp_baseline_sanity_check_v1") is False  # NEGATIVE
    assert declares_a_condition("exp_scorer_swap_e2_v1") is False      # NEGATIVE (e2 is not a scale token)

    print("realised_condition selftest: 9/9 PASS (incl. 4 explicit negatives)")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        _selftest()
    else:
        ap.print_help()
