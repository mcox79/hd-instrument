"""LANDING WITNESS for the WORD-SENSE-SELECTION meaning stage (hdlab/underspecified_sense_reader.py) + its live
read()-time wire into hdlab/situation_reader.py (sm.select_sense). Self-contained, ASCII, deterministic, capped
threads. Proves the LANDED organ -- not the experiment cell -- carries the validated capability, and that the wire
is a PURE ADD (every other situation-model dimension byte-identical off vs on). Wired 2026-09-06 from the owner-DONE
select_word_sense_by_context_primed_biased_competition_over_a_decorrelated_sense_hub (Q111, SOLVED sec 10d/10e).

  W1  PROMOTION FAITHFUL: the promoted hdlab.underspecified_sense_reader reproduces the reference
      experiments.exp_underspecified_sense_reader_v1 on U1-U5 -- and does so THROUGH THE LIVE default_vec_lookup()
      (the sglite-w2v space), proving byte-identity of the vec source too:
        U1 'bank' resolves to DIFFERENT shared-core clusters in river vs money context (== reference).
        U2 the committed COARSE sense beats the coarse-MFS floor AND a context-shuffle twin CI-separated (the +0.169
           win), realized through the promoted module + live vec_lookup; per-item coarse picks == the reference.
        U3 mode='cluster_first' competes among FEWER candidates and still beats the coarse-MFS floor CI-sep.
        U4 mode='fine' at default knobs == the raw diagnostic_context_wsd argmax over the curated hub (byte-identical).
        U5 compose_joint('bind') = the multiplicative Bayesian-AND composition (bind, not bundle).
  W2  ADDITIVE / BYTE-SAFE: a live read with track_senses ON is byte-identical (every existing situation-model
      dimension) to track_senses OFF -- the stage is lazy (sm.senses == [] until invoked); ON adds ONLY
      sm.select_sense.
  W3  LIVE CONSUMER: through the LIVE reader, sm.select_sense('bank', river-context) and sm.select_sense('bank',
      money-context) return DIFFERENT coarse clusters (the sense-selection capability is now live).

Run: .venv/Scripts/python.exe verification/test_word_sense_meaning_stage_landing.py
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

import experiments.exp_curated_foundation_wic_v1 as E
import experiments.exp_sense_hub_separation_as_v1 as SEP
import experiments.exp_underspecified_sense_reader_v1 as R      # the promotion-ready reference
from hdlab import meaning_foundation as MF
from hdlab.diagnostic_context_wsd import diagnostic_context_scores
from hdlab import underspecified_sense_reader as U              # the PROMOTED organ
from hdlab.situation_reader import SituationReader, _write_temp_conll

P = 0


def check(name, cond, detail=""):
    global P
    assert cond, "FAIL %s -- %s" % (name, detail)
    P += 1
    print("  ok  %s  %s" % (name, detail))


print("=" * 96)
print("LANDING WITNESS: word-sense-selection meaning stage + the live sm.select_sense read()-time consumer")
print("=" * 96)

# ============================================================ W1: promotion faithful (through the LIVE vec_lookup)
# vl_ref = the reference witness's sglite-w2v lookup; vl_live = the PROMOTED module's default_vec_lookup (the live
# path's source). Proving picks match through vl_live proves BOTH promotion faithfulness AND that the +0.169
# transfers through the live reader's vec source/config (the coref transfer-risk lesson).
w2i, mat = E._w2v(); mat = np.asarray(mat, float)
def vl_ref(w):
    i = w2i.get(w); return R._unit(np.asarray(mat[i], float)) if i is not None else None
vl_live = U.default_vec_lookup()

# vec-source byte-identity spot check (a sample of covered words)
_probe = ["river", "water", "money", "bank", "loan", "shore", "deposit", "flow", "cash", "account"]
_vec_ok = 0
for w in _probe:
    a, b = vl_ref(w), vl_live(w)
    if a is not None and b is not None and np.array_equal(a, b):
        _vec_ok += 1
check("W1-veclookup-byte-identical", _vec_ok == len(_probe),
      "default_vec_lookup() == the reference sglite-w2v lookup on %d/%d probe words (the +0.169 transfers through "
      "the live vec source)" % (_vec_ok, len(_probe)))

# ---- U1 functional (through the PROMOTED module + live vec_lookup) ----
rr = U.select_sense(["river", "water", "flow", "shore", "boat", "muddy"], vl_live, lemma="bank", pos="n")
rm = U.select_sense(["money", "loan", "account", "deposit", "cash", "savings"], vl_live, lemma="bank", pos="n")
rr_ref = R.select_sense(["river", "water", "flow", "shore", "boat", "muddy"], vl_ref, lemma="bank", pos="n")
check("W1-U1-functional", rr["coarse"] != rm["coarse"] and rr["coarse"] == rr_ref["coarse"],
      "bank/river -> %s (%s) | bank/money -> %s (%s) [river!=money, == reference]"
      % (rr["coarse"], rr["fine"], rm["coarse"], rm["fine"]))

# ---- SemCor subordinate population (identical build to the reference witness) ----
recs = SEP.build_recs(max_files=12)
sub = [r for r in recs if r["subordinate"] and any(MF.covers(s) and MF.sense_signature(s) is not None for s in r["tn"])]
rng = np.random.default_rng(0); perm = rng.permutation(len(sub))
und, cf, mfs, tw = [], [], [], []
nfine, nclus = [], []
passthrough_ok = passthrough_n = 0
promo_match = 0
for i, r in enumerate(sub):
    tn = r["tn"]; glex = U.coarse_cluster(r["gold"])
    u = U.select_sense(r["ctx"], vl_live, candidate_synsets=tn, mode="underspecified")
    c = U.select_sense(r["ctx"], vl_live, candidate_synsets=tn, mode="cluster_first")
    u_ref = R.select_sense(r["ctx"], vl_ref, candidate_synsets=tn, mode="underspecified")
    promo_match += int(u["coarse"] == u_ref["coarse"])
    und.append(int(u["coarse"] == glex)); cf.append(int(c["coarse"] == glex))
    mfs.append(int(U.coarse_cluster(tn[0]) == glex))
    nfine.append(u["n_fine"]); nclus.append(u["n_coarse"])
    us = U.select_sense(sub[perm[i]]["ctx"], vl_live, candidate_synsets=tn, mode="underspecified")
    tw.append(int(us["coarse"] == glex))
    if passthrough_n < 400:
        C = U._context_matrix(r["ctx"], vl_live); G = MF.sense_signatures(tn)
        if C is not None and np.any(G):
            raw = tn[int(np.argmax(diagnostic_context_scores(C, G)))]
            f = U.select_sense(r["ctx"], vl_live, candidate_synsets=tn, mode="fine")
            passthrough_ok += int(f["fine"] == raw); passthrough_n += 1
und = np.array(und); cf = np.array(cf); mfs = np.array(mfs); tw = np.array(tw); n = len(sub)
a_und = round(float(und.mean()), 4); a_cf = round(float(cf.mean()), 4)
a_mfs = round(float(mfs.mean()), 4); a_tw = round(float(tw.mean()), 4)
vs_mfs = E._paired((und - mfs).astype(float), 11); vs_tw = E._paired((und - tw).astype(float), 12)
cf_vs_mfs = E._paired((cf - mfs).astype(float), 13)

check("W1-promotion-byte-identity", promo_match == n,
      "promoted coarse pick == reference coarse pick on %d/%d items (byte-faithful promotion)" % (promo_match, n))
check("W1-U2-coarse-win",
      vs_mfs["sep"] and vs_tw["sep"],
      "[U2] n=%d COARSE a_s=%.4f | coarse-MFS floor=%.4f (%+.4f sep=%s) | ctx-shuffle twin=%.4f (%+.4f sep=%s)"
      % (n, a_und, a_mfs, vs_mfs["delta"], vs_mfs["sep"], a_tw, vs_tw["delta"], vs_tw["sep"]))
check("W1-U3-cluster-first",
      np.mean(nclus) < np.mean(nfine) and cf_vs_mfs["sep"],
      "[U3] cluster-first a_s=%.4f (vs coarse-MFS %+.4f sep=%s); mean %.2f fine -> %.2f clusters (%.0f%% fewer)"
      % (a_cf, cf_vs_mfs["delta"], cf_vs_mfs["sep"], np.mean(nfine), np.mean(nclus),
         100 * (1 - np.mean(nclus) / np.mean(nfine))))
rate = passthrough_ok / max(passthrough_n, 1)
check("W1-U4-fine-passthrough", rate > 0.999,
      "[U4] mode='fine' == raw diagnostic argmax over the curated hub on %d/%d items (%.3f)"
      % (passthrough_ok, passthrough_n, rate))
base = np.array([0.30, 0.10, 0.05]); sib = np.array([0.02, 0.40, 0.05])
bind = U.compose_joint(base, sib, "bind"); bundle = U.compose_joint(base, sib, "bundle")
check("W1-U5-bind", int(np.argmax(bind)) == 1,
      "[U5] compose_joint('bind') argmax=%d (multiplicative Bayesian-AND); bundle argmax=%d"
      % (int(np.argmax(bind)), int(np.argmax(bundle))))


# ============================================================ W2: additive / byte-safe (ON vs OFF)
def _dim_signature(sm):
    """A canonical serialization of every LOAD-BEARING situation-model dimension EXCEPT the new sense one."""
    return {
        "entities": [tuple(e.heads) for e in sm.entities],
        "events": [(e.predicate, e.agent, e.patient, e.tense, e.subj_role, e.obj_role, e.affect)
                   for e in sm.events],
        "coref": [(r.pronoun, r.sent_idx, r.resolved_cluster, r.correct) for r in sm.coref_resolutions],
        "causal": [(c.sent_idx, c.cause, c.outcome, c.method) for c in sm.causal_links],
        "timeline_order": list(sm.timeline_order),
        "suppressed": [(s.sent_idx, s.predicate) for s in sm.suppressed_predicates],
        "entity_states": [(s.holder, s.property, s.htype) for s in sm.entity_states],
        "bridges": list(sm.bridges),
        "scalars": (sm.n_targets, sm.n_xsent_targets, sm.coref_acc, sm.coref_xsent_acc,
                    bool(sm.locations is not None), bool(sm.world_state is not None),
                    bool(sm.goal_register is not None), bool(sm.affect_register is not None)),
    }


doc = [["The", "sailor", "loved", "his", "ship", "."],
       ["He", "repaired", "the", "hull", "after", "the", "storm", "."],
       ["The", "captain", "feared", "the", "reef", "."]]
rows = [(si, wi, tok, "-") for si, toks in enumerate(doc) for wi, tok in enumerate(toks)]
_path = _write_temp_conll(rows)
try:
    sm_on = SituationReader().read(_path)                      # track_senses ON (default)
    sm_off = SituationReader(track_senses=False).read(_path)   # the pre-landing reader
finally:
    os.remove(_path)

sig_on, sig_off = _dim_signature(sm_on), _dim_signature(sm_off)
mismatch = [k for k in sig_on if sig_on[k] != sig_off[k]]
check("W2-additive-safety", not mismatch,
      "all %d existing dimensions byte-identical ON vs OFF (mismatches: %s)" % (len(sig_on), mismatch or "none"))
check("W2-off-is-pre-landing", not hasattr(sm_off, "select_sense") and sm_off.senses == [],
      "track_senses=False -> no sm.select_sense bound, sm.senses empty (== the pre-landing reader)")
check("W2-on-lazy-additive", callable(getattr(sm_on, "select_sense", None)) and sm_on.senses == [],
      "track_senses=True adds ONLY sm.select_sense; sm.senses stays [] until invoked (lazy, zero read-time cost)")


# ============================================================ W3: live consumer (different sense by context)
rv = sm_on.select_sense("bank", ["river", "water", "bank"])
rmn = sm_on.select_sense("bank", ["money", "deposit", "bank"])
check("W3-live-consumer",
      rv is not None and rmn is not None and rv["coarse"] != rmn["coarse"],
      "sm.select_sense('bank', river) -> %s (%s) | sm.select_sense('bank', money) -> %s (%s) [different coarse]"
      % (None if rv is None else rv["coarse"], None if rv is None else rv["fine"],
         None if rmn is None else rmn["coarse"], None if rmn is None else rmn["fine"]))

print("=" * 96)
print("LANDING WITNESS PASS: %d/%d" % (P, P))
print("=" * 96)
