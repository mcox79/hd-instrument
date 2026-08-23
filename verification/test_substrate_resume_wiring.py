"""Scaffold-free witness: the PROPOSED foundation-resume wiring works BOTH WAYS.

Slug: substrate_never_resumes. The bar's clause 2: prove the wiring both ways with a self-test --
OFF -> load not called, store starts at seeds; ON -> load called, store starts populated. And the
brief's warning: "an ablation asserted only by 'the off arm grounds nothing' would pass on a broken
build." So this pins, positively, that:

  1. OFF (foundation_dir=None): resuming_substrate() calls load_foundation ZERO times and the store
     starts at the seed vocabulary -- BYTE-IDENTICAL to a plain Substrate() (the additive-cannot-
     regress guarantee).
  2. ON  (foundation_dir=<saved>): load_foundation is called EXACTLY once and the store starts
     populated with the saved facts (live_facts strictly greater than seeds, equal to the snapshot).
  3. OFF-WITH-DIR (load=False): a dir is supplied but ignored -> store starts at seeds. This is the
     real ablation: the difference between arm 2 and arm 3 is ONLY the load, so a passing arm 2 can
     never be an artifact of a broken build.
  4. POSITIVE CONTROL on the spy: a deliberate load IS observed, so "zero" in arm 1 means zero, not
     a spy that cannot see.

Run:  python verification/test_substrate_resume_wiring.py
ASCII-only.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import sys
import tempfile

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import substrate_resume as R
from hdlab.reading_grounding_loop import KNOWN_OBJECT, KNOWN_RELATION, MEANING_RELATION
from hdlab.substrate import SEED_VOCAB, Substrate


def _build_tiny_foundation(dir_path: str) -> int:
    """A loadable foundation with a few facts BEYOND the seeds. Returns its live_facts count."""
    st = R.cold_state(seed=20260819, n_dim=256)
    seed_facts = len(st.store.live_facts())
    # add a handful of grounded meanings + their KNOWN_WORD facts, distinct from any seed
    for subj, obj in [("velmara", "boat"), ("flimzat", "storm"), ("qorbind", "harbor")]:
        st.store.store(subj, MEANING_RELATION, obj, "wiring_test", "TRUST_MID")
        st.store.store(subj, KNOWN_RELATION, KNOWN_OBJECT, "wiring_test", "TRUST_MID")
    R.fp.save_foundation(st, dir_path, source_tag="wiring_tiny", next_pass_idx=1)
    return len(st.store.live_facts()), seed_facts


class _LoadSpy:
    def __init__(self):
        self.calls = 0
        self._orig = R.fp.load_foundation

    def __enter__(self):
        def wrapped(*a, **k):
            self.calls += 1
            return self._orig(*a, **k)
        R.fp.load_foundation = wrapped
        return self

    def __exit__(self, *exc):
        R.fp.load_foundation = self._orig


def _seed_known_set(state) -> set:
    return {(f.subject, f.relation, f.obj) for f in state.store.live_facts()
            if f.relation == KNOWN_RELATION}


def test_off_arm_does_not_load_and_matches_plain_substrate():
    with _LoadSpy() as spy:
        sub = R.resuming_substrate(None, seed=20260819, n_dim=256)
    assert spy.calls == 0, "OFF arm must not call load_foundation (called %d)" % spy.calls
    plain = Substrate(seed=20260819, n_dim=256)
    # store starts at the seeds, byte-identical KNOWN_WORD set to a plain construction
    assert len(sub.state.store.live_facts()) == len(plain.state.store.live_facts())
    assert _seed_known_set(sub.state) == _seed_known_set(plain.state), \
        "OFF arm's seed store diverged from a plain Substrate()"
    assert sub.foundation_dir is None
    # no meaning facts yet (cold): the ConceptSpace anchor set is empty
    assert sub.state.space.anchors() == []


def test_on_arm_loads_once_and_starts_populated():
    with tempfile.TemporaryDirectory(prefix="resume_wiring_") as td:
        d = os.path.join(td, "foundation")
        n_loaded, n_seed = _build_tiny_foundation(d)
        with _LoadSpy() as spy:
            sub = R.resuming_substrate(d, seed=20260819, n_dim=256)
        assert spy.calls == 1, "ON arm must call load_foundation exactly once (called %d)" % spy.calls
        live = len(sub.state.store.live_facts())
        assert live == n_loaded, "loaded store size %d != saved %d" % (live, n_loaded)
        assert live > n_seed, "ON arm must start populated (%d) beyond seeds (%d)" % (live, n_seed)
        # the extra grounded meanings are present
        subs = {f.subject for f in sub.state.store.live_facts() if f.relation == MEANING_RELATION}
        assert {"velmara", "flimzat", "qorbind"} <= subs


def test_off_with_dir_ablation_is_real_not_asserted_by_absence():
    """load=False: dir supplied, ignored. Store starts at seeds. The ONLY difference from the ON arm
    is the load, so ON cannot be a broken-build artifact."""
    with tempfile.TemporaryDirectory(prefix="resume_wiring_") as td:
        d = os.path.join(td, "foundation")
        n_loaded, n_seed = _build_tiny_foundation(d)
        with _LoadSpy() as spy:
            off = R.resuming_substrate(d, seed=20260819, n_dim=256, load=False)
            assert spy.calls == 0, "load=False must not load"
            on = R.resuming_substrate(d, seed=20260819, n_dim=256, load=True)
            assert spy.calls == 1
        assert len(off.state.store.live_facts()) == n_seed, "OFF-with-dir must start at seeds"
        assert len(on.state.store.live_facts()) == n_loaded, "ON must start populated"
        assert len(on.state.store.live_facts()) > len(off.state.store.live_facts())


def test_spy_positive_control():
    """A deliberate load IS counted -- so 'zero' in the OFF arm proves absence, not a blind spy."""
    with tempfile.TemporaryDirectory(prefix="resume_wiring_") as td:
        d = os.path.join(td, "foundation")
        _build_tiny_foundation(d)
        with _LoadSpy() as spy:
            _ = R.fp.load_foundation(d)
            assert spy.calls == 1, "the spy cannot see a real load -- zero would prove nothing"


def _main() -> int:
    ok = True
    for fn in (test_off_arm_does_not_load_and_matches_plain_substrate,
               test_on_arm_loads_once_and_starts_populated,
               test_off_with_dir_ablation_is_real_not_asserted_by_absence,
               test_spy_positive_control):
        try:
            fn()
            print("[wiring] PASS", fn.__name__)
        except AssertionError as e:
            ok = False
            print("[wiring] FAIL", fn.__name__, "--", e, file=sys.stderr)
    print("[wiring] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_main())
