"""Scaffold-free witness for the LANDING of the bound-event-token backbone (p4) into the live reader.

Proves the default-off `bind_event_tokens` flag on hdlab.situation_reader.SituationReader is an ADDITIVE,
byte-identical-when-off wire whose flag-ON output is BYTE-EQUAL to the validated cell
(experiments/exp_tiered_bound_event_token_coref_v1.py). Recomputes everything FROM SOURCE on a REAL LitBank
passage (no landed metrics.json read). Every check can fail.

  [1] DEFAULT-OFF BYTE-IDENTICAL: with the flag off, sm.event_tokens and sm.episodic_store are None, and the
      event set + the other dimensions are unchanged vs the flag on (turning it on only ADDS the two fields).
  [2] FLAG-ON POPULATED: with the flag on, sm.event_tokens is a non-empty list of FHRR bound tokens and
      sm.episodic_store is a BoundEpisodicStore of the same length.
  [3] BIND BYTE-EXACT: each sm.event_tokens[i] is torch-EQUAL to the validated cell's E.event_token() for the
      same normalized event (the promoted codec reproduces the cell bit-for-bit).
  [4] READOUT == THE VALIDATED joint_decide: sm.episodic_store.corefer reproduces E.joint_decide on every
      probe E.make_probes generates for the passage, AND a real event coref-accepts while a RECOMBINATION
      hard-negative (both marginals present, the joint absent) coref-REJECTS -- the non-gameable discriminator.
  [5] TIERED STORE ASSEMBLED: the store carries the N400 CHUNK segmentation (Cowan-small) + a DG/CA3 episodic
      tier (_stored_dg_codes shaped (n_events, dg_dim)) -- it COMPOSES the organs, not just the BIND tier.

Brain frame (PINNED): ONE bound event token per event indexed on all dimensions (Zwaan & Radvansky 1998;
Franklin 2020 SEM); same-event recognition = CA3 pattern completion (Marr 1971); the recombination control is
the conjunctive-memory dissociation (Konkel & Cohen 2009). Glass-box, NO LLM.

Run: .venv/Scripts/python.exe verification/test_bound_event_backbone_landing_organ.py
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402
import torch  # noqa: E402

import experiments.exp_tiered_bound_event_token_coref_v1 as E  # noqa: E402
import experiments.exp_situation_model_qa_v1 as QA  # noqa: E402
from hdlab.situation_reader import SituationReader  # noqa: E402
from hdlab import bound_event_backbone as BEB  # noqa: E402


CAPABLE = dict(tense_agnostic_events=True, preserve_tense=True, timeline_register=True,
               track_space=True, verb_subcat_gate=True, role_route="wired",
               spacy_pred_gate=False, causation_typed=False)


def _event_sig(sm):
    """A byte-stable signature of the event set (the fields the backbone reads)."""
    return [(str(e.predicate), str(e.agent), str(e.patient), str(e.tense)) for e in sm.events]


def _expected_tokens(sm):
    """Reconstruct the cell's kept-event tokens from sm.events: normalize + keep >=2 filled roles + bind,
    all via the VALIDATED cell E -- the independent reference the wire must reproduce bit-for-bit."""
    toks = []
    attrs_list = []
    for e in sm.events:
        a = E.Passage._norm({"AGENT": e.agent, "PATIENT": e.patient, "PRED": e.predicate, "TENSE": e.tense})
        if sum(1 for r in E.ROLES if a.get(r)) >= 2:
            attrs_list.append(a)
            toks.append(E.event_token(a))
    return attrs_list, toks


def main():
    gaz = QA.load_given_gazetteer()
    # pick the first LitBank doc that yields a bindable passage (>=5 events with >=2 roles)
    reader_off = SituationReader(gaz=gaz, bind_event_tokens=False, **CAPABLE)
    reader_on = SituationReader(gaz=gaz, bind_event_tokens=True, **CAPABLE)
    doc_used = None
    sm_off = sm_on = None
    for doc in QA.load_docs(12):
        path = os.path.join(QA.CONLL_DIR, doc + ".conll")
        if not os.path.exists(path):
            continue
        cand = reader_on.read(path)
        _, toks = _expected_tokens(cand)
        if len(toks) >= 5:
            doc_used = doc
            sm_on = cand
            sm_off = reader_off.read(path)
            break
    assert sm_on is not None, "no LitBank doc yielded a bindable passage (>=5 events with >=2 roles)"

    checks = []

    # [1] DEFAULT-OFF BYTE-IDENTICAL.
    off_ok = (sm_off.event_tokens is None and sm_off.episodic_store is None
              and _event_sig(sm_off) == _event_sig(sm_on)
              and len(sm_off.entities) == len(sm_on.entities)
              and list(sm_off.timeline_order) == list(sm_on.timeline_order)
              and len(sm_off.causal_links) == len(sm_on.causal_links))
    checks.append((off_ok,
                   "[1] DEFAULT-OFF byte-identical: flag-off event_tokens/episodic_store None; event set (%d) "
                   "+ entities/timeline/causal unchanged vs flag-on -> turning it on only ADDS the two fields"
                   % len(sm_off.events)))

    # [2] FLAG-ON POPULATED.
    n_tok = len(sm_on.event_tokens) if sm_on.event_tokens is not None else -1
    store = sm_on.episodic_store
    pop_ok = (isinstance(sm_on.event_tokens, list) and n_tok >= 5
              and isinstance(store, BEB.BoundEpisodicStore) and len(store) == n_tok)
    checks.append((pop_ok,
                   "[2] FLAG-ON populated: %d bound event tokens + a BoundEpisodicStore(len=%d) on doc '%s'"
                   % (n_tok, len(store) if store is not None else -1, doc_used)))

    # [3] BIND BYTE-EXACT vs the validated cell.
    exp_attrs, exp_toks = _expected_tokens(sm_on)
    bind_ok = (len(exp_toks) == n_tok
               and all(torch.equal(a, b) for a, b in zip(sm_on.event_tokens, exp_toks)))
    checks.append((bind_ok,
                   "[3] BIND byte-exact: all %d wired tokens torch-EQUAL the validated cell E.event_token() "
                   "(promoted codec reproduces the cell bit-for-bit)" % n_tok))

    # [4] READOUT == the validated joint_decide (+ a real accept and a recombination reject).
    p = E.Passage("witness::" + doc_used,
                  [{"AGENT": e.agent, "PATIENT": e.patient, "PRED": e.predicate, "TENSE": e.tense}
                   for e in sm_on.events])
    tokens_cell = p.tokens()
    gen = np.random.default_rng(20260901)
    probes = E.make_probes(p, gen)
    same = 0
    total = 0
    n_pos_accept = 0
    n_hardneg_reject = 0
    for pr in probes:
        (r1, r2) = pr["pair"]
        qa = {r1: pr[r1], r2: pr[r2]}
        wire = store.corefer(qa)
        cell = bool(E.joint_decide(pr, tokens_cell))
        total += 1
        same += int(wire == cell)
        if pr["kind"] == "pos" and wire:
            n_pos_accept += 1
        if pr["kind"] == "hard_neg" and (not wire):
            n_hardneg_reject += 1
    readout_ok = (total > 0 and same == total and n_pos_accept >= 1 and n_hardneg_reject >= 1)
    checks.append((readout_ok,
                   "[4] READOUT == joint_decide: %d/%d probes agree with the validated cell; >=1 real event "
                   "accepts (%d) and >=1 RECOMBINATION hard-neg rejects (%d) -- the non-gameable discriminator"
                   % (same, total, n_pos_accept, n_hardneg_reject)))

    # [5] TIERED STORE ASSEMBLED (N400 chunk + DG/CA3 episodic tier).
    seg = list(store.segment_sizes)
    dg = store._stored_dg_codes
    tier_ok = (len(seg) >= 1 and sum(seg) == n_tok and max(seg) <= n_tok
               and dg is not None and dg.shape == (n_tok, BEB._DG_DIM))
    checks.append((tier_ok,
                   "[5] TIERED store assembled: N400 CHUNK segments=%s (sum=%d==n_events) + DG/CA3 episodic "
                   "tier _stored_dg_codes shape=%s -- composes the organs, not just BIND"
                   % (seg if len(seg) <= 8 else ("%d segs, max %d" % (len(seg), max(seg))),
                      sum(seg), None if dg is None else tuple(dg.shape))))

    print("=== witness: bound-event-token backbone LANDING (doc '%s', %d events) ===" % (doc_used, n_tok))
    ok_all = True
    for ok, msg in checks:
        print("  %s  %s" % ("PASS" if ok else "FAIL", msg))
        ok_all = ok_all and bool(ok)
    print("\nRESULT: %s (%d/%d)" % ("ALL CHECKS PASS" if ok_all else "FAIL",
                                    sum(1 for ok, _ in checks if ok), len(checks)))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
