"""LANDING witness -- the +0.0823 CI-sep coref stack wired into the LIVE EventCentralityReader.

problem: compose_the_unified_referent_with_the_incumbent_graded_pick_pool_for_a_live_coref_gain (owner-DONE p12).

Proves FIRST-HAND, through the ACTUAL deployed hdlab.event_centrality_coref.EventCentralityReader (native
head_to_cluster scorer) on the full GUM TEST he/she population (n~1240), that landing the three brain-
foundational coref-stack wires (WIRE 1 phi person-feature pool pre-filter; WIRE 1b agreement-narrow on `him`;
WIRE 1c soften generic-suppress) delivers the cumulative gain:

  W1  FULL STACK (all three wire flags ON) reproduces ~0.5855 vs the flag-OFF incumbent ~0.5032 -- the
      +0.0823 modern-GUM he/she gain, doc-paired bootstrap CI-SEPARATED.
  W2  NAMED-antecedent coref NO-REGRESS (it RISES / holds -- the wires are recall-safe).
  W3  BYTE-IDENTITY reference: with all three wire flags OFF the reader is byte-identical to the pre-landing
      incumbent (per-target picks identical to the default reader, whose wire flags default OFF at the class
      level, and acc == 0.5032). The live consumer SituationReader turns them ON by default; its
      all_capabilities_off() historical reader forces them OFF; all three are in CAPABILITY_FLAGS.
  W4  NO-GOLD: swapping the eval harness's gold-gender feed for the glass-box hdlab.gender_organ.GenderOrganizer
      MATCHES/BEATS the gold-gender full stack (~0.5887) -- the whole +0.08 stack runs with NO gold at inference.

Glass-box, NO external LLM, ASCII. Run: .venv/Scripts/python.exe verification/test_coref_stack_landing.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import random
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.gum_coref as G
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
from experiments.exp_hybrid_unified_incumbent_coref_gum_v1 import gum_to_live, _named_clusters
from hdlab.coref import build_pronoun_targets, name_content_tokens
from hdlab.event_centrality_coref import EventCentralityReader
from hdlab.gender_organ import GenderOrganizer
from hdlab.situation_reader import SituationReader

_KW = dict(topical_mode="rolemass", query_memory=True, centrality_mode="event_role")
FULL = dict(phi_person_filter=True, narrow_him=True, soften_generic_suppress=True)


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def _score(reader, docs, regender=None):
    """Per-doc rows of (correct, is_named, resolved_cluster) through the LIVE reader on GUM he/she.
    regender: optional GenderOrganizer -> re-source every nominal's gender GLASS-BOX (no gold)."""
    per = []
    for d in docs:
        ms = gum_to_live(d)
        if regender is not None:
            ms = _apply_organ_gender(ms, regender)
        tg = build_pronoun_targets(ms)
        sid = [0] * (max((m["sent_idx"] for m in ms), default=0) + 1)
        recs = reader.resolve_stream(ms, tg, scene_ids=sid, **_KW)
        named = _named_clusters(ms)
        per.append([(bool(r["correct"]), r["gold_cluster"] in named, r["resolved_cluster"]) for r in recs])
    return per


def _apply_organ_gender(ms, organ):
    """Replace the harness gold-gender feed with the glass-box organ (the SOLE gender source)."""
    out = []
    for m in ms:
        m = dict(m)
        if not m["is_pronoun"]:
            is_named = bool(name_content_tokens(m.get("span_toks", [m["head"]])))
            og = organ.infer(m.get("span_toks", [m["head"]]), is_named)
            m["gender"] = None if is_named else og
            m["name_gender"] = og if is_named else None
        out.append(m)
    return out


def _acc(per, named_only=False):
    h = t = 0
    for rows in per:
        for c, isn, _rc in rows:
            if named_only and not isn:
                continue
            t += 1; h += int(c)
    return (h / t if t else float("nan")), t


def _doc_paired_boot(A, B, seed=13, n_boot=2000, named_only=False):
    """Doc-level paired bootstrap of (B - A): resample docs with replacement, ratio-of-sums per resample."""
    rng = random.Random(seed)
    pa, pb = [], []
    for ra, rb in zip(A, B):
        ha = ta = hb = tb = 0
        for c, isn, _ in ra:
            if named_only and not isn:
                continue
            ta += 1; ha += int(c)
        for c, isn, _ in rb:
            if named_only and not isn:
                continue
            tb += 1; hb += int(c)
        pa.append((ha, ta)); pb.append((hb, tb))
    idx = list(range(len(pa))); ds = []
    for _ in range(n_boot):
        s = [rng.choice(idx) for _ in idx]
        ha = sum(pa[i][0] for i in s); ta = sum(pa[i][1] for i in s)
        hb = sum(pb[i][0] for i in s); tb = sum(pb[i][1] for i in s)
        if ta and tb:
            ds.append(hb / tb - ha / ta)
    ds.sort()
    return ds[int(0.025 * len(ds))], ds[int(0.975 * len(ds))]


def main():
    oks = []
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, name_gazetteer=gaz)
    test = [d for i, d in enumerate(docs) if i % 2 == 1]

    incumbent = EventCentralityReader(graded_pick=True)                       # wire flags default OFF
    full = EventCentralityReader(graded_pick=True, **FULL)                    # all three wires ON
    off_explicit = EventCentralityReader(graded_pick=True, phi_person_filter=False,
                                         narrow_him=False, soften_generic_suppress=False)

    p_inc = _score(incumbent, test)
    p_full = _score(full, test)
    p_off = _score(off_explicit, test)

    a_inc, n = _acc(p_inc)
    a_full, _ = _acc(p_full)
    lo, hi = _doc_paired_boot(p_inc, p_full)

    # ---- W1: the full stack reproduces ~0.5855 and beats the flag-off incumbent CI-separated ----
    oks.append(check(
        "W1 FULL STACK beats the flag-off incumbent CI-separated (~0.5855 vs ~0.5032, +0.082 on modern GUM he/she)",
        (lo > 0) and (a_full - a_inc) > 0.05 and abs(a_inc - 0.5032) < 0.003 and a_full > 0.57,
        "incumbent=%.4f -> full=%.4f delta=%+.4f CI[%.4f,%.4f] (n=%d)" % (a_inc, a_full, a_full - a_inc, lo, hi, n)))

    # ---- W2: named-antecedent NO-REGRESS (rises/holds) ----
    an_inc, nn = _acc(p_inc, named_only=True)
    an_full, _ = _acc(p_full, named_only=True)
    lon, hin = _doc_paired_boot(p_inc, p_full, named_only=True)
    oks.append(check(
        "W2 NAMED-antecedent coref NO-REGRESS (rises/holds)",
        (an_full - an_inc) > -0.01 and lon > -0.02,
        "named (n=%d): incumbent=%.4f -> full=%.4f delta=%+.4f CI[%.4f,%.4f]" % (nn, an_inc, an_full, an_full - an_inc, lon, hin)))

    # ---- W3: BYTE-IDENTITY -- wires OFF == the default reader per-target; acc == 0.5032; flag wiring ----
    per_target_identical = all(
        ro[2] == rf[2] for rowsa, rowsb in zip(p_inc, p_off) for ro, rf in zip(rowsa, rowsb))
    a_off, _ = _acc(p_off)
    sr_default = SituationReader(gaz={})
    sr_histoff = SituationReader.all_capabilities_off(gaz={})
    flags_in_caps = all(f in SituationReader.CAPABILITY_FLAGS
                        for f in ("phi_person_filter", "narrow_him", "soften_generic_suppress"))
    consumer_default_on = (sr_default.reader_ec.phi_person_filter and sr_default.reader_ec.narrow_him
                           and sr_default.reader_ec.soften_generic_suppress)
    consumer_histoff = not (sr_histoff.reader_ec.phi_person_filter or sr_histoff.reader_ec.narrow_him
                            or sr_histoff.reader_ec.soften_generic_suppress)
    default_class_off = not (incumbent.phi_person_filter or incumbent.narrow_him
                             or incumbent.soften_generic_suppress)
    oks.append(check(
        "W3 BYTE-IDENTITY: wires-OFF == default reader per-target (acc==incumbent); default-ON at the consumer; "
        "OFF in all_capabilities_off; all three in CAPABILITY_FLAGS",
        per_target_identical and abs(a_off - a_inc) < 1e-12 and default_class_off
        and flags_in_caps and consumer_default_on and consumer_histoff,
        "wires_off_acc=%.4f (incumbent=%.4f) per_target_identical=%s class_default_off=%s in_caps=%s "
        "consumer_on=%s hist_off=%s"
        % (a_off, a_inc, per_target_identical, default_class_off, flags_in_caps, consumer_default_on,
           consumer_histoff)))

    # ---- W4: NO-GOLD -- glass-box gender organ matches/beats the gold-gender full stack (~0.5887) ----
    organ = GenderOrganizer(gaz)
    p_full_organ = _score(full, test, regender=organ)
    a_organ, _ = _acc(p_full_organ)
    loO, hiO = _doc_paired_boot(p_full, p_full_organ)   # organ - gold-gender full stack
    oks.append(check(
        "W4 NO-GOLD: the glass-box gender organ MATCHES/BEATS the gold-gender full stack (~0.5887, no gold at inference)",
        a_organ >= a_full - 0.01 and hiO >= 0,
        "gold-gender full=%.4f -> organ(no-gold) full=%.4f delta=%+.4f CI[%.4f,%.4f]"
        % (a_full, a_organ, a_organ - a_full, loO, hiO)))

    n_ok = sum(oks)
    print("=" * 80)
    print("%s (%d/%d)" % ("ALL CHECKS PASS" if n_ok == len(oks) else "SOME CHECKS FAILED", n_ok, len(oks)))
    print("=" * 80)
    return 0 if n_ok == len(oks) else 1


if __name__ == "__main__":
    sys.exit(main())
