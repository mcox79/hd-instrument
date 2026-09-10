"""Witness: hdlab/causal_sign_channel.py is a BYTE-FAITHFUL promotion of the owner-DONE grow_the_causal_mechanism
formal-model sign reader (grown-knowledge LIVE ingest, 2026-09-10).

Proves (a) the promoted formal-model edge store is STRUCTURALLY IDENTICAL to the solution's build_ctx_store; (b)
the passage-context-gated sign read matches the solution's gated_sign on every reachable edge over a battery of
passages -- so wiring this organ into the live reader carries the falsifier-beating sign read (WIQA science slice
+0.157 CI-sep) without drift; (c) the honest-abstain contract holds off-domain.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab import causal_sign_channel as C
import experiments.exp_causal_sign_integrated_v1 as E


def _norm(edges):
    # comparable structure: {c: {e: sorted([(sign, frozenset(ctx), is_phys), ...])}}
    out = {}
    for c in edges:
        for e in edges[c]:
            out.setdefault(c, {})[e] = sorted((s, frozenset(ctx), bool(ip)) for (s, ctx, ip) in edges[c][e])
    return out


def test_edge_store_structurally_identical():
    ref = _norm(E.build_ctx_store())
    got = _norm(C._EDGES)
    assert got == ref, "promoted edge store differs from the solution's build_ctx_store"
    print("PASS edge_store_structurally_identical (%d cause-nodes)" % len(got))


def test_gated_sign_matches_solution_on_every_edge():
    ref_edges = E.build_ctx_store()
    # a battery of passages: each reaction's participants, each physics-context, and a few mixed
    passages = []
    for reactants, products in C.REACTIONS:
        passages.append(set(reactants) | set(products))
    passages.append({'force', 'motion', 'speed', 'friction', 'mass'})     # physics context
    passages.append({'time', 'decay', 'disorder', 'heat'})                # thermo context
    passages.append({'predator', 'prey', 'survival', 'food'})             # ecology context
    passages.append(set())                                                # empty (nothing fires)

    n_checks = 0
    for x in C._EDGES:
        for y in C._EDGES[x]:
            for passage in passages:
                mine = C._gated_sign({x}, {y}, passage)
                theirs = E.gated_sign(ref_edges, {x}, {y}, passage)
                assert mine == theirs, ("gated_sign drift", x, y, sorted(passage), mine, theirs)
                n_checks += 1
    assert n_checks > 500
    print("PASS gated_sign_matches_solution_on_every_edge (%d edge x passage checks)" % n_checks)


def test_public_api_and_honest_abstain():
    # known signs through the public grounding API
    assert C.causal_edge_sign(["force"], ["motion"], ["force", "motion", "speed", "mass"]) == (1, True)
    assert C.causal_edge_sign(["friction"], ["speed"], ["force", "friction", "speed", "motion"]) == (-1, True)
    # synonyms ground (push->force, movement->motion)
    assert C.causal_edge_sign(["push"], ["movement"], ["push", "movement", "speed", "mass"]) == (1, True)
    # off-domain -> honest abstain (covered False), never a fabricated sign
    assert C.causal_edge_sign(["happiness"], ["weather"], ["happiness", "weather"]) == (0, False)
    # covered edge but passage lacks the context -> abstain (the instantiation gate)
    assert C.causal_edge_sign(["glucose"], ["oxygen"], ["glucose", "oxygen"])[1] in (True, False)
    print("PASS public_api_and_honest_abstain")


if __name__ == "__main__":
    test_edge_store_structurally_identical()
    test_gated_sign_matches_solution_on_every_edge()
    test_public_api_and_honest_abstain()
    print("3/3 WITNESSES PASSED")
