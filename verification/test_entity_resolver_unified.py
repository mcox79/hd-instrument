"""Witness for `consolidate_the_six_coreference_organs_into_one_cue_based_entity_resolver`.

PROVES (Q111: proposal + proof, strategy lands) that the ONE cue-based `entity_resolver`
(experiments/exp_entity_resolver_unified_v1.EntityResolver -- a single ACT-R content-addressable retrieval
CORE + mention-type-routed cue-arms) reproduces the LIVE-wired coreference resolvers BYTE-IDENTICALLY on real
GUM mentions -- so substituting the unified organ into the reader is byte-identical / no-regress on every board
dim BY CONSTRUCTION (the invariant the bar demands):

  W1  cluster(exact)         == hdlab.online_entity_cluster.online_cluster           (sm.entities producer, default-on)
  W2  cluster(isa/partwhole/hold/centering) == online_cluster(same kwargs)           (the arms + write-policies fold in)
  W3  bridge_links           == hdlab.crosstype_bridge.crosstype_bridge_links         (definite->name bridge, default-on)
  W4  stage1 dispatcher      == hdlab.world_state_entity_binding.EntityBinder         (world-state Stage-1, default-on)

Each is checked byte-for-byte across many GUM docs / a deterministic call sequence -- a control that EXCLUDES a
lucky-sample pass. Glass-box, NO external LLM.
Run: .venv/Scripts/python.exe verification/test_entity_resolver_unified.py
"""
from __future__ import annotations
import os
import random
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.gum_coref as G
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
from experiments.exp_route_unified_to_consumers_gum_v1 import _gum_to_live
from experiments.exp_crosstype_live_wire_gum_v1 import live_reparse

from hdlab.online_entity_cluster import online_cluster
from hdlab.crosstype_bridge import crosstype_bridge_links
from hdlab.world_state_entity_binding import EntityBinder
from hdlab.salience_binder import bind as salience_bind, DEFAULT_DECAY, ROLE_PROMINENCE

from experiments.exp_entity_resolver_unified_v1 import EntityResolver

RESULTS = []


def check(name, cond):
    RESULTS.append((name, bool(cond)))
    print(("  [PASS] " if cond else "  [FAIL] ") + name)
    return bool(cond)


def main():
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, limit=80, name_gazetteer=gaz)
    R = EntityResolver()

    # -- W1/W2: ONLINE CLUSTERING byte-identity (all default + arm/policy variants) ------------------------
    n_docs = 0
    n_ment = 0
    w1 = w_isa = w_pw = w_hold = w_center = True
    first_div = None
    for d in docs:
        ms = _gum_to_live(d)
        n_docs += 1
        n_ment += sum(1 for m in ms if not m["is_pronoun"])
        for route, ok_name in (("exact", "w1"), ("isa", "isa"), ("partwhole", "pw")):
            a = R.cluster(ms, gaz, type_route=route)
            b = online_cluster(ms, gaz, type_route=route)
            if a != b:
                if first_div is None:
                    first_div = (route, {k: a.get(k) for k in list(a)[:5]}, {k: b.get(k) for k in list(b)[:5]})
                if route == "exact":
                    w1 = False
                elif route == "isa":
                    w_isa = False
                else:
                    w_pw = False
        if R.cluster(ms, gaz, hold=0.0, margin=1.0) != online_cluster(ms, gaz, hold=0.0, margin=1.0):
            w_hold = False
        if R.cluster(ms, gaz, centering=True) != online_cluster(ms, gaz, centering=True):
            w_center = False
    check("W1 cluster(exact) == online_entity_cluster.online_cluster byte-for-byte (%d docs, %d non-pron mentions)"
          % (n_docs, n_ment), w1)
    check("W2a cluster(isa) == online_cluster(isa) byte-for-byte", w_isa)
    check("W2b cluster(partwhole) == online_cluster(partwhole) byte-for-byte", w_pw)
    check("W2c cluster(hold=0.0,margin=1.0) == online_cluster(hold policy) byte-for-byte", w_hold)
    check("W2d cluster(centering=True) == online_cluster(Centering-Cb bonus) byte-for-byte", w_center)
    if first_div is not None:
        print("      first divergence:", first_div)

    # -- W3: CROSSTYPE definite->name BRIDGE byte-identity (live conf_thr + a sweep + ALL FIVE modes) ---------
    w3 = {ct: True for ct in (-3.0, 0.0, -1.0)}
    w3_modes = {mo: True for mo in ("cue_retrieval", "cue_gated", "cue_competed", "cue_novelty", "cue_conf")}
    n_bin = 0
    for d in docs[:60]:
        ld = live_reparse(d)
        for ct in (-3.0, 0.0, -1.0):                                   # the LIVE mode (cue_conf) across conf_thr
            a = R.bridge_links(ld, gaz, conf_thr=ct)
            b = crosstype_bridge_links(ld, gaz, conf_thr=ct)
            if ct == -3.0:
                n_bin += len(b)
            if a != b:
                w3[ct] = False
        for mo in w3_modes:                                            # ALL FIVE cue modes at the live conf_thr
            a = R.bridge_links(ld, gaz, conf_thr=-3.0, mode=mo)
            b = crosstype_bridge_links(ld, gaz, conf_thr=-3.0, mode=mo)
            if a != b:
                w3_modes[mo] = False
    check("W3 bridge_links == crosstype_bridge_links byte-for-byte @ live conf_thr=-3.0 (60 docs, %d binds)" % n_bin,
          w3[-3.0])
    check("W3b bridge_links byte-identical across a conf_thr sweep {0.0, -1.0} (the swept operating point folds in)",
          w3[0.0] and w3[-1.0])
    check("W3c bridge_links byte-identical across ALL FIVE cue modes {retrieval,gated,competed,novelty,conf} "
          "(the WHOLE crosstype organ folds, incl. the board's cue_competed experiencer instrument): %s"
          % {k: v for k, v in w3_modes.items()}, all(w3_modes.values()))

    # -- W4: WORLD-STATE Stage-1 DISPATCH byte-identity (deterministic sequence, incl. stats) --------------
    heads = ["I", "me", "my", "he", "she", "him", "her", "it", "them", "they", "we", "you",
             "cup", "dog", "John", "table", "Mary", "book", None]
    verbs = [None, "take", "gave", "hold", "see", "require"]
    clusters = [None, 1, 2, 5, None, 7]
    rng = random.Random(20260910)
    seq = [(rng.choice(heads), rng.choice(clusters), rng.choice(verbs)) for _ in range(400)]
    orig = EntityBinder(); mine = R.new_stage1_binder()
    w4 = True
    for (h, cl, vb) in seq:
        # alternate participant / theme by a deterministic bit, exercising both routes + the Centering theme state
        if (hash((h, cl, vb)) & 1):
            o = orig.bind_participant(h, coref_cluster=cl, verb=vb)
            m = mine.bind_participant(h, coref_cluster=cl, verb=vb)
        else:
            o = orig.bind_theme(h, verb=vb)
            m = mine.bind_theme(h, verb=vb)
        if o != m:
            w4 = False
            print("      Stage-1 divergence at (%r,%r,%r): orig=%r mine=%r" % (h, cl, vb, o, m))
            break
    check("W4 Stage-1 dispatch == EntityBinder byte-for-byte over 400 mixed participant/theme binds", w4)
    check("W4b Stage-1 final stats Counter identical (route accounting byte-identical)", dict(orig.stats) == dict(mine.stats))

    # -- W5 NON-VACUITY CONTROL: the byte-identity test is DISCRIMINATING (a wrong arm config DIVERGES). If the
    #    equality test could not fail, the passes above would be meaningless. A different type-route / a shuffled
    #    cue produces a DIFFERENT clustering on real docs -> the match in W1/W2 is a real constraint, not trivial.
    diverged = False
    for d in docs:
        ms = _gum_to_live(d)
        if online_cluster(ms, gaz, type_route="exact") != online_cluster(ms, gaz, type_route="partwhole"):
            diverged = True
            break
    check("W5 CONTROL: byte-identity is discriminating (exact vs part-whole route DIVERGE on real docs -> the "
          "W1/W2 matches are a real constraint, not a vacuous pass)", diverged)

    # -- W6: the PRONOUN arm (GENERALIZE) -- pronoun_pick == salience_binder.bind byte-for-byte. Proves the ONE
    #    core serves the pronoun mention-type too (phi applied by the caller; argmax over ACT-R base-level), so the
    #    resolver spans all four Ariel mention types. Random candidate-history sets + a degenerate/empty case.
    rp = random.Random(4242)
    roles = ["SUBJECT", "POSSESSIVE", "OBJECT", "OTHER"]
    w6 = True
    n_pick = 0
    for _ in range(3000):
        k = rp.randint(0, 5)
        cands = [[(float(rp.randint(0, t)), rp.choice(roles)) for _ in range(rp.randint(0, 3))]
                 for t in range(k)]
        now = float(k + rp.randint(0, 4))
        if R.pronoun_pick(cands, now) != salience_bind(cands, now, DEFAULT_DECAY, ROLE_PROMINENCE):
            w6 = False
            break
        n_pick += 1
    check("W6 GENERALIZE: pronoun_pick == salience_binder.bind byte-for-byte over %d random candidate sets "
          "(the ONE core serves the pronoun arm; phi+salience -> argmax)" % n_pick,
          w6 and R.pronoun_pick([], 0.0) == salience_bind([], 0.0))

    npass = sum(1 for _, ok in RESULTS if ok)
    print("\n[witness] %d/%d PASS" % (npass, len(RESULTS)))
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
