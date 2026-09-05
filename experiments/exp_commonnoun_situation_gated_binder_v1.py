"""exp_commonnoun_situation_gated_binder_v1 -- CAN WE BUILD IT? Extend the landed situation-model organ
(hdlab.event_centrality_coref: HD event-bundle memory that breaks same-gender PRONOUN ties by which entity
is most CENTRAL in the recent event structure) from pronouns to DEFINITE COMMON-NOUN descriptions -- the
capability the drill named as the precise missing piece (82% of common-noun links have 2-3 competing active
persons; the correct one is the scene-foregrounded entity, not the most recent).

MECHANISM: the incremental discourse-referent former (this problem's build) + a genuine Cowan-4 HD event
memory. Per sentence, extract one event (AGENT = first person referent in subject position; PATIENT = next)
keyed by the REFERENT so the memory tracks which discourse entity drives recent events. At a definite
common-noun description with >=2 gender/number-compatible active referents, break the tie by HD
event-centrality (unbind+cleanup over the Cowan-4 focus; the scene protagonist wins) instead of by ACT-R
recency alone. This is the SITUATION-MODEL cue the drill says the 82% multi-person links require.

ARMS (character-cluster coref chain-F1, CoNLL, doc bootstrap): surface_head (floor) / LINKER (ACT-R
accessibility, no situation model) / SITUATION (ACT-R + event-centrality tie-break) / TWIN.
If SITUATION beats surface_head CI-separated -> the located negative is crossable by building this; if it
washes (like the REFUTED focus-stack + next-mention-prior on this same task) -> the residual genuinely needs
the role-relational/world knowledge the event structure cannot supply (the Phase-1 boundary).

Reuses hdlab.event_centrality_coref (EventMemory, hd_centrality) VERBATIM. Glass-box HD, NO external LLM.
hdlab READ-only. ASCII. own dir. Run: .venv/Scripts/python.exe experiments/exp_commonnoun_situation_gated_binder_v1.py --self-test
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse, json, time
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.coref import EntityAliaser
from hdlab.event_centrality_coref import EventMemory, hd_centrality
import experiments.exp_commonnoun_coref_diagnostic_v1 as DIAG
import experiments.exp_commonnoun_referent_linker_v1 as LK
import experiments.exp_commonnoun_linktype_decomposition_v1 as DEC

# possessive-pronoun possessor -> gender of the POSSESSOR (for relational-role binding).
POSS_GENDER = {"her": "fem", "hers": "fem", "his": "masc"}
RELATIONAL_ROLE = DEC.KINSHIP_ROLE

OUT_DIR = os.path.join(_REPO, "data/exp_commonnoun_situation_gated_binder_v1")
SEED = 20260904
head_lemma = DIAG.head_lemma
is_name = DIAG.is_name


def situation_predict(mentions, gaz, *, window=8, n_dim=4096, mem_seed=7, headmatch_gate=False,
                      relational=False):
    """Incremental referent former + HD event-memory situation gate on definite common-noun descriptions.
    headmatch_gate=True = the DEPLOYABLE recipe: restrict candidates to head-lemma matches (net-safe recall,
    like surface_head) + modifier-split + the situation-gate tie-break among >=2 head-match candidates.
    relational=True = the RELATIONAL SITUATION MODEL (prototype of the Phase-1 lever): a role-relational
    description with a possessive-pronoun possessor ("her father", "his wife") is bound by the brain's rule
    SAME-RELATION+SAME-RELATUM: resolve the possessor to a discourse referent and key the role-referent by
    (role_lemma, possessor_ref) -- so 'her father' ... 'her father' (same 'her') co-refer, overriding the
    head-match link. Extracts + uses relations from the narrative, no lexicon of who-is-whose."""
    aliaser = EntityAliaser()
    refs = []                       # LK.Ref
    name_key_to_ref = {}
    head_group = {}
    labels = {}
    rel_map = {}                    # (role_lemma, possessor_ref_key) -> Ref  (the relational graph)
    ln = 0

    def resolve_possessor(pg, si):
        """most-recent active person referent gender-compatible with the possessive pronoun's gender."""
        cands = [r for r in refs if r.person and (not window or (si - r.last_sent) <= window)
                 and LK._gender_ok(pg, r.gender)]
        return max(cands, key=lambda r: r.last_midx).key if cands else None
    mem = EventMemory(n_dim=n_dim, capacity=4, fanout=2, seed=mem_seed)
    cur_sent = None
    sent_buf = []                   # (ref_key, role_rank, is_person) for the current sentence

    def emit_event():
        if not sent_buf:
            return
        agent = next((k for (k, r, p) in sent_buf if p and r == 0), None)
        if agent is None:
            return
        patient = next((k for (k, r, p) in sent_buf if p and k != agent), None)
        mem.push_event(agent, patient, cur_sent)

    for m in sorted([x for x in mentions if not x["is_pronoun"]], key=lambda x: x["midx"]):
        si = m["sent_idx"]; role = m.get("sent_role_rank", 99)
        if cur_sent is None:
            cur_sent = si
        if si != cur_sent:
            emit_event(); sent_buf = []; cur_sent = si
        span = m.get("span_toks", [m["head"]])
        g = m.get("gender") or m.get("name_gender"); num = LK._num_of(m); mods = LK.modifiers(m)
        if is_name(m, gaz):
            canon = aliaser.assign(span, g)
            if canon is not None and canon in name_key_to_ref:
                r = name_key_to_ref[canon]; r.update(head_lemma(m["head"]), g, mods, si, m["midx"], role)
            else:
                r = LK.Ref("R%d" % ln, head_lemma(m["head"]), g, num, mods, si, m["midx"], True, True, role); ln += 1
                refs.append(r)
                if canon is not None:
                    name_key_to_ref[canon] = r
            labels[m["midx"]] = r.key; sent_buf.append((r.key, role, True)); continue
        hl = head_lemma(m["head"])
        person = LK.person_synset(hl) is not None
        if not person:
            if hl not in head_group:
                head_group[hl] = "H%d" % ln; ln += 1
            labels[m["midx"]] = head_group[hl]; sent_buf.append((head_group[hl], role, False)); continue
        defn = LK.definiteness(m)
        # RELATIONAL SITUATION MODEL: a possessed role-relational description binds by (role, possessor).
        rel_key = None
        if relational and hl in RELATIONAL_ROLE:
            span0 = (span[0].lower() if span else "")
            pg = POSS_GENDER.get(span0)
            if pg is not None:
                poss_key = resolve_possessor(pg, si)
                if poss_key is not None:
                    rel_key = (hl, poss_key)
                    if rel_key in rel_map:
                        r = rel_map[rel_key]
                        r.update(hl, g, mods, si, m["midx"], role)
                        labels[m["midx"]] = r.key; sent_buf.append((r.key, role, True)); continue
        cand_refs = []
        if not defn == "indef":
            for r in refs:
                if not r.person or (window and (si - r.last_sent) > window):
                    continue
                if not LK._gender_ok(g, r.gender) or not LK._number_ok(num, r.number):
                    continue
                if headmatch_gate and hl not in r.hls:
                    continue                  # DEPLOYABLE: link only on head-lemma match (net-safe recall)
                if headmatch_gate and hl in r.hls and mods and r.mods and mods.isdisjoint(r.mods):
                    continue                  # modifier-split: 'the old man' != 'the young man'
                cand_refs.append(r)
        chosen = None
        if len(cand_refs) == 1:
            chosen = cand_refs[0]
        elif len(cand_refs) >= 2:
            # SITUATION-MODEL GATE: which candidate referent is most central in recent events?
            pool = {r.key for r in cand_refs}
            scores, _detail = hd_centrality(mem, pool, "event_role")
            mx = max(scores.values()) if scores else 0.0
            if mx > 0.0:
                # among top-centrality, prefer head-lemma match then ACT-R activation (tie-break)
                top = [r for r in cand_refs if scores.get(r.key, 0.0) == mx]
                chosen = max(top, key=lambda r: (hl in r.hls, LK._actr(r, si)))
            else:
                # degenerate (no recent event mentions any candidate) -> ACT-R + head-match bonus
                chosen = max(cand_refs, key=lambda r: LK._actr(r, si) + (1.5 if hl in r.hls else 0.0))
            # modifier guard on a head-identical merge
            if hl in chosen.hls and mods and chosen.mods and mods.isdisjoint(chosen.mods):
                chosen = None
        if chosen is not None:
            chosen.update(hl, g, mods, si, m["midx"], role); labels[m["midx"]] = chosen.key
            sent_buf.append((chosen.key, role, True)); assigned = chosen
        else:
            r = LK.Ref("R%d" % ln, hl, g, num, mods, si, m["midx"], False, person, role); ln += 1
            refs.append(r); labels[m["midx"]] = r.key; sent_buf.append((r.key, role, True)); assigned = r
        if rel_key is not None:
            rel_map[rel_key] = assigned          # register the role+possessor -> referent relation
    emit_event()
    return labels


def _name_only_stats(docs, gaz):
    """name_only baseline on the NAME-mention subpopulation (for the no-regress-on-named check)."""
    st = []
    for di, (doc, ms) in enumerate(docs):
        lab = DIAG.cluster_labels(ms, gaz, "name_only")
        noms = [m for m in ms if not m["is_pronoun"] and DIAG.is_name(m, gaz)]
        st.append(LK._doc_stats([lab[m["midx"]] for m in noms], ["g%d" % m["cluster"] for m in noms]))
    return st


def per_doc_situation(docs, gaz, window=8, headmatch_gate=False, subpop="char", relational=False):
    st = []
    for di, (doc, ms) in enumerate(docs):
        lab = situation_predict(ms, gaz, window=window, headmatch_gate=headmatch_gate, relational=relational)
        if subpop == "char":
            chars = LK._char_clusters(ms)
            noms = [m for m in ms if not m["is_pronoun"] and m["cluster"] in chars]
        elif subpop == "name":
            noms = [m for m in ms if not m["is_pronoun"] and DIAG.is_name(m, gaz)]
        else:
            noms = [m for m in ms if not m["is_pronoun"]]
        st.append(LK._doc_stats([lab[m["midx"]] for m in noms], ["g%d" % m["cluster"] for m in noms]))
    return st


def kinship_recovery(docs, gaz, labels_fn):
    """On the kinship_role gold links, frac where the mention shares a predicted label with a prior
    same-gold-cluster mention (= correctly linked into its chain) = recall on the relational slice."""
    opp = hit = 0
    for doc, ms in docs:
        lab = labels_fn(ms)
        noms = sorted([m for m in ms if not m["is_pronoun"]], key=lambda m: m["midx"])
        prior = {}
        for m in noms:
            hl = DIAG.head_lemma(m["head"]); person = LK.person_synset(hl) is not None or DIAG.is_name(m, gaz)
            pri = prior.get(m["cluster"], [])
            if (not DIAG.is_name(m, gaz)) and person and pri:
                ante = pri[-1]; ahl = DIAG.head_lemma(ante["head"])
                is_kinship = (hl in DEC.KINSHIP_ROLE or ahl in DEC.KINSHIP_ROLE) and ahl != hl \
                    and not DIAG.is_name(ante, gaz) and not DEC.wn_bridge(hl, ahl)
                if is_kinship:
                    opp += 1
                    if any(lab[pm["midx"]] == lab[m["midx"]] for pm in pri):
                        hit += 1
            prior.setdefault(m["cluster"], []).append(m)
    return {"opportunities": opp, "recovered": hit, "recall": round(hit / max(1, opp), 4)}


def run(n=None, n_boot=1000, window=8, best_window=16):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    docs, gaz = DIAG.load_docs(n)
    _, sh = LK.per_doc_stats(docs, gaz, "surface_head")
    _, tw = LK.per_doc_stats(docs, gaz, "TWIN", twin_seed=SEED, window=window)
    sit = per_doc_situation(docs, gaz, window=window)
    best = per_doc_situation(docs, gaz, window=best_window, headmatch_gate=True)   # the DEPLOYABLE recipe
    rel = per_doc_situation(docs, gaz, window=best_window, headmatch_gate=True, relational=True)  # + relational
    best_nm = per_doc_situation(docs, gaz, window=best_window, headmatch_gate=True, subpop="name")
    rel_nm = per_doc_situation(docs, gaz, window=best_window, headmatch_gate=True, subpop="name", relational=True)
    nm_no = _name_only_stats(docs, gaz)
    pooled = {"surface_head": LK._conll_from_stats(sh), "SITUATION": LK._conll_from_stats(sit),
              "BEST_deploy": LK._conll_from_stats(best), "BEST+RELATIONAL": LK._conll_from_stats(rel),
              "TWIN": LK._conll_from_stats(tw)}
    st = {"surface_head": sh, "SITUATION": sit, "BEST_deploy": best, "BEST+RELATIONAL": rel, "TWIN": tw}
    pairs = [("BEST_deploy", "surface_head"), ("BEST+RELATIONAL", "BEST_deploy"),
             ("BEST+RELATIONAL", "surface_head"), ("BEST+RELATIONAL", "TWIN")]
    deltas = {"%s-%s" % (a, b): LK.bootstrap_delta(st[a], st[b], n_boot) for a, b in pairs}
    deltas["BEST_named_noregress"] = LK.bootstrap_delta(best_nm, nm_no, n_boot)
    deltas["RELATIONAL_named_noregress"] = LK.bootstrap_delta(rel_nm, nm_no, n_boot)
    kin = {"BEST_deploy": kinship_recovery(docs, gaz,
                lambda ms: situation_predict(ms, gaz, window=best_window, headmatch_gate=True)),
           "BEST+RELATIONAL": kinship_recovery(docs, gaz,
                lambda ms: situation_predict(ms, gaz, window=best_window, headmatch_gate=True, relational=True))}
    res = {"n_docs": len(docs), "window": window, "best_window": best_window,
           "pooled_char_cluster": pooled, "deltas": deltas, "kinship_slice_recovery": kin,
           "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor": "commonnoun_situation_gated_binder_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def _print(res):
    print("=" * 86)
    print("SITUATION-MODEL-GATED common-noun binder (%d docs, window=%d, best_window=%d) -- character clusters"
          % (res["n_docs"], res["window"], res["best_window"]))
    print("  %-14s %8s %8s %8s %8s" % ("arm", "MUC", "B3", "CEAFe", "CoNLL"))
    for a, sc in res["pooled_char_cluster"].items():
        print("  %-14s %8.4f %8.4f %8.4f %8.4f" % (a, sc["muc_f1"], sc["b3_f1"], sc["ceafe_f1"], sc["conll_avg"]))
    print("  " + "-" * 80)
    for kk, d in res["deltas"].items():
        print("  %-28s CoNLL %+.4f CI[%+.4f,%+.4f] ci_sep=%s"
              % (kk, d["delta"], d["lo"], d["hi"], d["ci_sep"]))
    if "kinship_slice_recovery" in res:
        print("  " + "-" * 80)
        for arm, k in res["kinship_slice_recovery"].items():
            print("  kinship-slice link recall  %-16s %d/%d = %.4f"
                  % (arm, k["recovered"], k["opportunities"], k["recall"]))
    print("=" * 86)


def self_test():
    docs, gaz = DIAG.load_docs(n=6)
    lab = situation_predict(docs[0][1], gaz)
    n_np = sum(1 for m in docs[0][1] if not m["is_pronoun"])
    assert len(lab) == n_np, (len(lab), n_np)
    res = run(n=6, n_boot=200)
    assert "SITUATION" in res["pooled_char_cluster"]
    print("[self-test] PASS")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--window", type=int, default=8)
    ap.add_argument("--nboot", type=int, default=1000)
    a = ap.parse_args()
    if a.self_test:
        self_test(); return
    _print(run(n=a.n, n_boot=a.nboot, window=a.window))


if __name__ == "__main__":
    main()
