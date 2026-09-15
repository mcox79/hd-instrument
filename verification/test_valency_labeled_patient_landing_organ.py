"""LANDING WITNESS (pure hdlab): the LABELED who-did-what PATIENT readout is landed INTO the hdlab substrate
(hdlab.predicate_argument_frontend.structural_patient_pick, Q111 diffs 1+2) and, THROUGH THE LANDED hdlab path
only, reproduces the +0.086 patient improvement over the PRE-UPGRADE deployed pick on clean UD-EWT gold, with
the AGENT byte-identical and the shipped (NAMED `structural_patient` flag) router path net-safe.

Problem: improve_the_parser_verb_argument_attachment_for_who_did_what (owner-DONE). The deployed structure-first
patient read the object off the parse by POSITION with a lossy voice detector (robust_passive). The landed fix
reads the verb's LABELED obj / nsubj:pass relation (arc_labeler over the parse heads) + valency-gated binding +
PRECISE voice remapping (precise_passive) + net-safe hybrid fallback. This gate asserts, scaffold-free, through
the LANDED hdlab path only (NO experiment helper for the pick logic):
  (a) on CLEAN UD-EWT gold (patient := obj|nsubj:pass off the GOLD relations), the LANDED
      structural_patient_pick (labeled readout) beats the FROZEN pre-upgrade deployed pick (position +
      robust_passive + coordination-share + hybrid fallback) by >= +0.06 on the LIVE arc_parser heads;
  (b) the SHIPPED router path (route_predicate_arguments, structural_patient flag) reproduces the SAME gain
      -- landed theme (flag ON) == the direct labeled pick -- and beats the flag-OFF heuristic theme;
  (c) AGENT byte-identical: route_predicate_arguments agent is identical structural_patient OFF vs ON on
      every gold item (the P2 AGENT / by-phrase path is untouched -- only the THEME moves).

Run: .venv/Scripts/python.exe verification/test_valency_labeled_patient_landing_organ.py
Glass-box, NO LLM. Writes nothing. ASCII. ~1-2 min on CPU.
"""
from __future__ import annotations
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.pos_tagger import PosTagger
from hdlab.arc_parser import ArcParser
from hdlab.predicate_argument_frontend import (structural_patient_pick, route_predicate_arguments,
                                               _verb_nom_deps, _shared_object, _cands)
from hdlab.graded_role_assigner import robust_passive, hybrid_role_patient
import experiments.exp_whodidwhat_ud_structural_v1 as UD

POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
ARC_ASSET = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
UD_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")


def _deployed_pick(toks, pos, heads, v):
    """FROZEN pre-upgrade deployed structural_patient_pick (byte-identical to the pre-landing body:
    structural_roles patient with robust_passive voice + position + _shared_object, then the hybrid fallback).
    Reconstructed inline from hdlab primitives so this witness compares the LANDED pick against the historical
    deployed floor without importing any experiment helper."""
    n = len(toks)
    is_passive = robust_passive(toks, pos, v)
    nom = _verb_nom_deps(pos, heads, v, n)
    pre = [c for c in nom if c < v]
    post = [c for c in nom if c > v]
    if is_passive:
        patient = pre[-1] if pre else (post[0] if post else None)
    else:
        patient = post[0] if post else None
    if patient is None:
        patient = _shared_object(toks, pos, heads, v, n)
    if patient is not None:
        return patient
    return hybrid_role_patient(toks, pos, v, cands=_cands(pos))


def main():
    tagger = PosTagger.load(POS_ASSET)
    arc = ArcParser.load(ARC_ASSET)
    sents = UD.load_ud(UD_TEST)

    n = 0
    hit_deployed = 0
    hit_landed = 0
    hit_router_on = 0
    hit_router_off = 0
    agent_identical = 0
    for toks_l, v, pat, passive in UD.gold_items(sents):
        pos = tagger.tag(list(toks_l))
        try:
            heads = arc.parse(list(toks_l), pos).heads
        except Exception:
            heads = {}
        # (a) direct LANDED hdlab pick vs the FROZEN deployed pick, same heads
        landed = structural_patient_pick(toks_l, pos, heads, v)
        deployed = _deployed_pick(toks_l, pos, heads, v)
        # (b) the SHIPPED router path, structural_patient OFF vs ON
        r_off = route_predicate_arguments(toks_l, pos, heads, v, quotative=False, structural_patient=False)
        r_on = route_predicate_arguments(toks_l, pos, heads, v, quotative=False, structural_patient=True)
        n += 1
        hit_deployed += int(deployed == pat)
        hit_landed += int(landed == pat)
        hit_router_off += int(r_off["theme"] == pat)
        hit_router_on += int(r_on["theme"] == pat)
        # (c) AGENT byte-identity OFF vs ON
        agent_identical += int(r_off["agent"] == r_on["agent"])

    acc = lambda h: (h / n) if n else 0.0
    deployed_acc = acc(hit_deployed)
    landed_acc = acc(hit_landed)
    router_on_acc = acc(hit_router_on)
    router_off_acc = acc(hit_router_off)
    margin = landed_acc - deployed_acc

    checks = []
    checks.append(("(a) LANDED structural_patient_pick beats the frozen DEPLOYED pick by >= +0.06 on clean UD gold",
                   margin >= 0.06,
                   "landed %.4f vs deployed %.4f  (+%.4f), n=%d" % (landed_acc, deployed_acc, margin, n)))
    checks.append(("(b) the SHIPPED router path (structural_patient=True) == the direct labeled pick (the flag routes it)",
                   abs(router_on_acc - landed_acc) < 1e-9,
                   "router-ON %.4f vs direct %.4f" % (router_on_acc, landed_acc)))
    checks.append(("(b') router structural_patient=True beats structural_patient=False (net-positive shipped path)",
                   (router_on_acc - router_off_acc) >= 0.06,
                   "ON %.4f vs OFF %.4f (+%.4f)" % (router_on_acc, router_off_acc, router_on_acc - router_off_acc)))
    checks.append(("(c) AGENT byte-identical structural_patient OFF vs ON on every gold item (P2 AGENT untouched)",
                   agent_identical == n,
                   "%d/%d items agent-identical" % (agent_identical, n)))

    npass = 0
    print("=" * 82)
    for name, ok, detail in checks:
        print("  [%s] %s -- %s" % ("PASS" if ok else "FAIL", name, detail))
        npass += int(ok)
    print("%d/%d checks passed" % (npass, len(checks)))
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
