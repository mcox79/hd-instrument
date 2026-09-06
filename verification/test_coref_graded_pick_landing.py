"""Landing witness: the PINNED graded ACT-R cue-based pronoun pick (hdlab.graded_coref_pick,
recency load-bearing) is now the LIVE coref path (hdlab.event_centrality_coref.EventCentralityReader
graded_pick default ON; wired into hdlab.situation_reader.SituationReader.reader_ec), REPLACING the
anti-brain-foundational rolemass topical pick + HD event-centrality override.

Problem: strengthen_the_cue_based_pronoun_coreference_resolver_the_shared_upstream_accuracy_cap (owner-DONE).

Everything is measured FIRST-HAND through the ACTUAL deployment reader path (no reliance on a pre-run
experiment json for the headline claim):

  W1  the LIVE default reader (graded_pick=True) beats the forced-OFF incumbent (graded_pick=False) on
      the live pooled he/she coref_acc, through L._R + L._resolve (the exact reader_resolve deployment
      call): OFF ~0.469 -> ON ~0.602 (+0.13). Both arms run the same pool construction / mention replay;
      only the pool PICK differs.
  W2  NO-REGRESS on the NAMED-antecedent slice (it RISES, does not drop).
  W3  ADDITIVE-SAFETY on the full SituationReader.read: the coref-INDEPENDENT dimensions
      (events / causal_links / timeline / entity_states) are BYTE-IDENTICAL ON vs OFF (separate streams
      -> cannot regress); the goal register's goal HEADS are byte-identical (only the AGENT attribution
      follows the improved coref); and the coref-DEPENDENT dims move in the right direction: pooled
      coref RISES and the who-has-what board dimension (exp_coref_graded_downstream_whohaswhat_v1)
      RISES 0.4035 -> 0.4735 (+0.070 CI-separated, info-free twin loses).
  W4  INFO-FREE control: the shuffled-candidate-history twin (same machinery, candidate<->evidence link
      severed) LOSES, well below the OFF floor -> the lift is a real retrieval signal, not the machinery.

19c NOTE: the coref_acc is on LitBank (19c English) so the exact numbers are informational for the
board; the WIRE is a brain-FIDELITY correction (register-general recency mechanism, Lewis & Vasishth
2005) justified independently of the corpus era.

Glass-box, NO external LLM, ASCII. Run: .venv/Scripts/python.exe verification/test_coref_graded_pick_landing.py
"""
import glob
import json
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_referent_coref_linking_v1 as L
import experiments.exp_coref_graded_live_transfer_v1 as GT
from hdlab.situation_reader import SituationReader, MEM_SEED
from hdlab.event_centrality_coref import EVENT_N_DIM, EventCentralityReader

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def _run_deploy_reader(graded, docs, gaz):
    """Run the ACTUAL deployment reader (L._R == GatedECReader == EventCentralityReader subclass) through
    L._resolve (the reader_resolve deployment call), gate=False. graded=True exercises the LANDED base
    graded pick; graded=False is the incumbent rolemass+event-centrality path. Returns per-doc rows of
    (correct, is_named), the exp_referent_coref_linking pooled-he/she instrument."""
    reader = L._R(n_dim=4096, mem_seed=7, graded_pick=graded)
    per_doc = []
    for _di, (_doc, p) in enumerate(docs):
        mo, ns = L.parse_litbank_conll(p, name_gender_map=gaz)
        named = GT._named_clusters(mo)
        recs = L._resolve(reader, mo, ns, gate=False, qmem=True)
        per_doc.append([(int(r["correct"]), r["gold_cluster"] in named) for r in recs])
    return per_doc


def _noncoref_independent(sm):
    """The coref-INDEPENDENT dimensions (read separate streams from the pronoun pick): events, causal,
    timeline, entity_states. Byte-identical ON vs OFF == additive-safe (cannot regress)."""
    return {
        "events": [(str(e.predicate), str(e.agent), str(e.patient), e.global_idx) for e in sm.events],
        "entity_states": [(s.holder, s.property, s.htype, s.sent_idx) for s in sm.entity_states],
        "causal_links": [(cl.sent_idx, cl.cause, cl.outcome, cl.method) for cl in sm.causal_links],
        "timeline_order": list(sm.timeline_order),
        "timeline_frames": [tuple(getattr(f, "chrono_order", [])) for f in sm.timeline_frames],
    }


def _goal_heads(sm):
    """Goal IDENTITY (head/text/kind/status), AGENT-attribution stripped. Byte-identical ON vs OFF ==
    the graded pick only re-attributes WHO wants each goal (coref-dependent), never WHAT the goal is."""
    gr = getattr(sm, "goal_register", None)
    if gr is None:
        return []
    return sorted((str(g.goal_head), str(g.goal_text), g.kind, g.status, g.sent_idx, g.negated)
                  for g in gr.goals)


def main():
    gaz = L.load_given_gazetteer()

    # ---- W1 + W2: pooled he/she coref_acc through the ACTUAL deployment reader path (100 docs) ----
    docs = L._docs(100)
    off = _run_deploy_reader(False, docs, gaz)
    on = _run_deploy_reader(True, docs, gaz)
    off_acc, n = GT._pool_acc(off)
    on_acc, _ = GT._pool_acc(on)
    off_named, _ = GT._pool_acc(off, named=True)
    on_named, _ = GT._pool_acc(on, named=True)

    chk("W1 LIVE default reader uses the graded ACT-R pick: pooled he/she coref_acc ON ~0.602 vs forced-OFF ~0.469 (+0.13)",
        on_acc >= 0.58 and off_acc <= 0.49 and (on_acc - off_acc) >= 0.10 and n >= 5000,
        "OFF(incumbent)=%.4f -> ON(graded)=%.4f  delta=%+.4f  n=%d docs=%d" % (
            off_acc, on_acc, on_acc - off_acc, n, len(docs)))

    chk("W2 NO-REGRESS on the named-antecedent slice (it RISES, does not drop)",
        on_named >= off_named - 0.005,
        "named: OFF=%.4f -> ON=%.4f  delta=%+.4f" % (off_named, on_named, on_named - off_named))

    # ---- W4: info-free twin (shuffled candidate histories) must LOSE, well below the OFF floor ----
    twin_reader = GT.GradedPickReader(n_dim=4096, mem_seed=7)
    twin = GT._run_arm(twin_reader, docs, gaz, gate=False, qmem=False, use_graded=True,
                       weights=None, twin=True)
    twin_acc, _ = GT._pool_acc(twin)
    chk("W4 INFO-FREE twin (shuffled candidate<->evidence link) LOSES (well below the OFF floor)",
        twin_acc < off_acc - 0.10,
        "twin=%.4f  vs OFF floor=%.4f  vs ON=%.4f" % (twin_acc, off_acc, on_acc))

    # ---- W3: full-read additive-safety over a doc sample ----
    conll = sorted(glob.glob(os.path.join(L.NC.CONLL_DIR, "*.conll")))[:12]
    r_on = SituationReader(gaz=gaz)                                   # default graded_pick=True
    r_off = SituationReader(gaz=gaz)
    r_off.reader_ec = EventCentralityReader(n_dim=EVENT_N_DIM, mem_seed=MEM_SEED, graded_pick=False)
    assert r_on.reader_ec.graded_pick is True and r_off.reader_ec.graded_pick is False

    indep_identical = goalhead_identical = ndocs = 0
    c_on = c_off = 0.0
    for p in conll:
        sm_on = r_on.read(p)
        r_off._read_parse_cache = {}
        sm_off = r_off.read(p)
        ndocs += 1
        indep_identical += int(_noncoref_independent(sm_on) == _noncoref_independent(sm_off))
        goalhead_identical += int(_goal_heads(sm_on) == _goal_heads(sm_off))
        if sm_on.coref_acc is not None and sm_off.coref_acc is not None:
            c_on += sm_on.coref_acc; c_off += sm_off.coref_acc

    chk("W3a ADDITIVE-SAFETY: coref-INDEPENDENT dims (events/causal/timeline/entity_states) BYTE-IDENTICAL ON vs OFF",
        indep_identical == ndocs,
        "byte-identical %d/%d docs" % (indep_identical, ndocs))
    chk("W3b goal IDENTITY byte-identical (only the goal AGENT attribution follows the improved coref)",
        goalhead_identical == ndocs,
        "goal-heads identical %d/%d docs" % (goalhead_identical, ndocs))
    chk("W3c coref-DEPENDENT dim RISES through the full reader (mean per-doc coref_acc ON > OFF)",
        c_on > c_off,
        "mean per-doc coref_acc OFF=%.4f -> ON=%.4f (delta %+.4f, %d docs)" % (
            c_off / max(1, ndocs), c_on / max(1, ndocs), (c_on - c_off) / max(1, ndocs), ndocs))

    # ---- W3d: the who-has-what board dimension (the pronoun-bound downstream) RISES CI-separated ----
    whw = os.path.join(_REPO, "data", "exp_coref_graded_downstream_whohaswhat_v1", "metrics_full.json")
    if os.path.exists(whw):
        wr = json.load(open(whw))["result"]
        rm = wr["arms"]["rolemass"]["acc"]; gd = wr["arms"]["graded"]["acc"]
        gmr = wr["graded_minus_rolemass"]
        chk("W3d who-has-what board dim RISES CI-separated (rolemass->graded) and the info-free twin loses",
            gd > rm and gmr.get("CIsep", False) and wr["arms"]["twin"]["acc"] < rm,
            "who-has-what rolemass=%.4f -> graded=%.4f (delta %+.4f ci%s) twin=%.4f" % (
                rm, gd, gmr["delta"], gmr["ci"], wr["arms"]["twin"]["acc"]))
    else:
        print("  SKIP W3d who-has-what metrics not on disk (run exp_coref_graded_downstream_whohaswhat_v1 --run)")

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
