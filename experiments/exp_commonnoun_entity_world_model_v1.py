"""exp_commonnoun_entity_world_model_v1 -- the PROPER brain-foundational implementation (per the research
drill): resolve definite reference by QUERYING an accumulated ENTITY WORLD-MODEL restricted to the
FOREGROUNDED set, not by weighting surface cues.

Research (PINNED: Kintsch CI; Zwaan-Radvansky event-indexing; Sanford-Garrod bonding->resolution; Morrow-
Bower/Glenberg foregrounding; Heim FCS / Kamp DRT file cards): the reader keeps one RECORD per entity
(types/head-lemmas, social ROLE, RELATIONS accumulated across the text, recent-EVENT participation,
presence, salience) and resolves "the man"/"her father"/"the master" by forming a descriptive constraint
from the NP and MATCHING it against the records, restricted to the foregrounded/co-present set, with ACT-R
activation only as a tiebreak. Our surface-cue resolver never builds or queries such a model -- so this cell
builds it and measures the AMBIGUOUS-LINK resolution accuracy (the metric the research says goes 0.26->0.5-
0.65), on GOLD referents (isolates the resolution SIGNAL from our clustering errors).

ARMS on ambiguous person common-noun links (>=2 compatible active person entities; GOLD referents):
  recency_floor        most-recent compatible entity (the surface baseline, ~0.24).
  event_agent          most-recent-event-AGENT among compatible (the situation-model cue alone).
  WORLD_MODEL          the accumulated entity-model query: descriptive-type match + social ROLE match +
                       possessor-RELATION match + recent-event participation + recency + ACT-R, restricted
                       to the foregrounded set (bonding) then scored (resolution).
  UNION_ORACLE         upper bound: correct if ANY single cue UNIQUELY picks the gold antecedent (measures
                       whether the disambiguating facts are even IN the narrative).

Glass-box, NO LLM (WordNet = static offline type asset; a small static scenario/role library). hdlab READ.
ASCII. own dir. Run: .venv/Scripts/python.exe experiments/exp_commonnoun_entity_world_model_v1.py --self-test
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse, glob, json, time
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.coref import parse_litbank_conll, load_name_gender
from hdlab.graded_coref_pick import ROLE_W, DEFAULT_ACTR_D
import experiments.exp_commonnoun_coref_diagnostic_v1 as DIAG
import experiments.exp_commonnoun_referent_linker_v1 as LK
import experiments.exp_commonnoun_linktype_decomposition_v1 as DEC

CONLL_DIR = os.path.join(_REPO, "data/litbank/coref_conll")
OUT_DIR = os.path.join(_REPO, "data/exp_commonnoun_entity_world_model_v1")
head_lemma = DIAG.head_lemma
is_name = DIAG.is_name
POSS_GENDER = {"her": "fem", "hers": "fem", "his": "masc"}
ROLE_SET = DEC.KINSHIP_ROLE


class Entity:
    """A discourse-entity FILE CARD (Heim/Kamp), accumulated across the text."""
    __slots__ = ("cluster", "gender", "number", "heads", "roles", "relations", "event_agent_sents",
                 "hist", "last_sent")

    def __init__(self, cluster):
        self.cluster = cluster; self.gender = None; self.number = None
        self.heads = set(); self.roles = set(); self.relations = set()   # relations = {(role, possessor_cluster)}
        self.event_agent_sents = []; self.hist = []; self.last_sent = -1

    def observe(self, hl, g, num, si, role_rank, is_role):
        self.heads.add(hl)
        if self.gender is None and g in ("masc", "fem"):
            self.gender = g
        if self.number is None and num in ("sing", "plur"):
            self.number = num
        if is_role:
            self.roles.add(hl)
        self.hist.append((si, role_rank)); self.last_sent = si


def _actr(ent, si):
    s = 0.0
    for (sent, role) in ent.hist:
        rw = ROLE_W["SUBJECT"] if role == 0 else ROLE_W["OTHER"]
        s += rw * (float(max(1, si - sent + 1)) ** (-DEFAULT_ACTR_D))
    return np.log(s) if s > 0 else -1e9


def resolve_ambiguous(docs_paths, gaz, window=8):
    cats = ["ALL", "head_identical", "name_antecedent", "wordnet_bridge", "kinship_role", "residual"]
    B = {c: defaultdict(int) for c in cats}
    for path in docs_paths:
        ms, _ = parse_litbank_conll(path, name_gender_map=gaz)
        by_cluster = defaultdict(list)
        for m in ms:
            by_cluster[m["cluster"]].append(m)
        ents = {}
        prior = defaultdict(list)
        sent_buf = []; cur_sent = None                     # for positional event agent
        noms_and_pron = sorted(ms, key=lambda m: m["midx"])

        def flush_event():
            if cur_sent is None:
                return
            agent = next((c for (c, rr, pers) in sent_buf if pers and rr == 0), None)
            if agent is not None and agent in ents:
                ents[agent].event_agent_sents.append(cur_sent)

        for m in noms_and_pron:
            si = m["sent_idx"]
            if cur_sent is None:
                cur_sent = si
            if si != cur_sent:
                flush_event(); sent_buf = []; cur_sent = si
            if m["is_pronoun"]:
                continue
            hl = head_lemma(m["head"]); g = m.get("gender") or m.get("name_gender"); num = LK._num_of(m)
            role_rank = m.get("sent_role_rank", 99)
            person = LK.person_synset(hl) is not None or is_name(m, gaz)
            is_role = hl in ROLE_SET
            span = [w.lower() for w in m.get("span_toks", [m["head"]])]
            pri = prior.get(m["cluster"], [])
            # ---- an ambiguous definite-description link to resolve ----
            if (not is_name(m, gaz)) and person and pri:
                ante = pri[-1]; ante_c = ante["cluster"]; ahl = head_lemma(ante["head"])
                cat = ("head_identical" if ahl == hl else "name_antecedent" if is_name(ante, gaz)
                       else "wordnet_bridge" if DEC.wn_bridge(hl, ahl)
                       else "kinship_role" if (hl in ROLE_SET or ahl in ROLE_SET) else "residual")
                # BONDING: compatible + foregrounded (in window) + PERSON-like entities
                comp = [c for c, e in ents.items()
                        if (window == 0 or (si - e.last_sent) <= window)
                        and LK._gender_ok(g, e.gender) and LK._number_ok(num, e.number)
                        and (e.gender or e.roles or any(LK.person_synset(h) is not None for h in e.heads))]
                if len(comp) >= 2:
                    # possessor for relational query
                    poss_cluster = None
                    if span and span[0] in POSS_GENDER:
                        pg = POSS_GENDER[span[0]]
                        pcs = [c for c in ents if LK._gender_ok(pg, ents[c].gender) and (si - ents[c].last_sent) <= window]
                        poss_cluster = max(pcs, key=lambda c: ents[c].last_sent) if pcs else None
                    scores = {}
                    for c in comp:
                        e = ents[c]; s = 0.0
                        # DESCRIPTIVE type match (head lemma seen for this entity, or WordNet-type compatible)
                        if hl in e.heads:
                            s += 3.0
                        elif any(DEC.wn_bridge(hl, h) for h in e.heads):
                            s += 1.0
                        # social ROLE match
                        if is_role and hl in e.roles:
                            s += 2.5
                        # possessor RELATION match: entity established as (role, possessor)
                        if is_role and poss_cluster is not None and (hl, poss_cluster) in e.relations:
                            s += 4.0
                        # recent-EVENT participation (foregrounding): was agent of a recent event
                        if e.event_agent_sents and (si - e.event_agent_sents[-1]) <= window:
                            s += 1.0
                        # foregrounding recency + ACT-R salience (tiebreak)
                        s += 0.5 * (1.0 / (1.0 + (si - e.last_sent))) + 0.4 * _actr(e, si)
                        scores[c] = s
                    wm_pick = max(comp, key=lambda c: scores[c])
                    rec_pick = max(comp, key=lambda c: ents[c].last_sent)
                    ev = [c for c in comp if ents[c].event_agent_sents]
                    ev_pick = max(ev, key=lambda c: ents[c].event_agent_sents[-1]) if ev else rec_pick
                    # union oracle: does ANY single cue uniquely pick ante?
                    union = (rec_pick == ante_c or ev_pick == ante_c
                             or (hl in ents[ante_c].heads and sum(1 for c in comp if hl in ents[c].heads) == 1)
                             or (poss_cluster is not None and (hl, poss_cluster) in ents[ante_c].relations))
                    for cc in ("ALL", cat):
                        b = B[cc]; b["n"] += 1
                        b["recency"] += int(rec_pick == ante_c)
                        b["event_agent"] += int(ev_pick == ante_c)
                        b["world_model"] += int(wm_pick == ante_c)
                        b["union_oracle"] += int(union)
            # ---- update the world-model with this mention ----
            e = ents.get(m["cluster"])
            if e is None:
                e = Entity(m["cluster"]); ents[m["cluster"]] = e
            e.observe(hl, g, num, si, role_rank, is_role)
            # RELATION extraction: a possessed role description asserts (role, possessor) for THIS entity
            if is_role and span and span[0] in POSS_GENDER:
                pg = POSS_GENDER[span[0]]
                pcs = [c for c in ents if c != m["cluster"] and LK._gender_ok(pg, ents[c].gender)
                       and (si - ents[c].last_sent) <= window]
                if pcs:
                    e.relations.add((hl, max(pcs, key=lambda c: ents[c].last_sent)))
            prior[m["cluster"]].append(m)
            sent_buf.append((m["cluster"], role_rank, person))
        flush_event()
    out = {}
    for c in cats:
        b = B[c]; n = b["n"]
        if n == 0:
            continue
        out[c] = {"n": n, "recency": round(b["recency"] / n, 4),
                  "event_agent": round(b["event_agent"] / n, 4),
                  "WORLD_MODEL": round(b["world_model"] / n, 4),
                  "union_oracle": round(b["union_oracle"] / n, 4)}
    return out


from hdlab.coref import EntityAliaser


def world_model_predict(mentions, gaz, window=8, link_thr=0.5, margin_thr=0.0):
    """DEPLOYABLE entity-world-model FORMER: build entity records from its OWN clustering and resolve each
    definite common-noun person description by the world-model query (descriptive/role/relation/event +
    foregrounding + ACT-R), restricted to compatible foregrounded records; link to the best-matching record
    iff it clears a descriptive-compatibility threshold, else open a NEW entity. Returns {midx -> label}.

    margin_thr>0 = the IDEAL CONFIDENCE GATE (graded_coref_pick abstain; Nieuwland Nref 'hold both'): link
    ONLY when the top-1 record beats the top-2 by >= margin_thr; otherwise DEFER (open a tentative referent)
    so an uncertain guess does NOT pollute a record -- the fix for the bootstrapping wall that caps the
    un-gated former (which committed every resolution and lost MUC to wrong-merges)."""
    aliaser = EntityAliaser()
    ents = []                        # Entity records (my clusters)
    name_key_to_ent = {}
    head_group = {}
    labels = {}
    ln = 0
    sent_buf = []; cur_sent = None

    def new_ent():
        nonlocal ln
        e = Entity("R%d" % ln); ln += 1; ents.append(e); return e

    def flush_event():
        if cur_sent is None:
            return
        agent = next((k for (k, rr, pers) in sent_buf if pers and rr == 0), None)
        if agent is not None:
            for e in ents:
                if e.cluster == agent:
                    e.event_agent_sents.append(cur_sent); break

    for m in sorted(mentions, key=lambda x: x["midx"]):
        si = m["sent_idx"]
        if cur_sent is None:
            cur_sent = si
        if si != cur_sent:
            flush_event(); sent_buf = []; cur_sent = si
        if m["is_pronoun"]:
            continue
        hl = head_lemma(m["head"]); g = m.get("gender") or m.get("name_gender"); num = LK._num_of(m)
        rr = m.get("sent_role_rank", 99); span = [w.lower() for w in m.get("span_toks", [m["head"]])]
        is_role = hl in ROLE_SET; person = LK.person_synset(hl) is not None or is_name(m, gaz)
        if is_name(m, gaz):
            canon = aliaser.assign(m.get("span_toks", [m["head"]]), g)
            if canon is not None and canon in name_key_to_ent:
                e = name_key_to_ent[canon]
            else:
                e = new_ent()
                if canon is not None:
                    name_key_to_ent[canon] = e
            e.observe(hl, g, num, si, rr, is_role); labels[m["midx"]] = e.cluster
            sent_buf.append((e.cluster, rr, True)); continue
        if not person:
            if hl not in head_group:
                head_group[hl] = "H%d" % ln; ln += 1
            labels[m["midx"]] = head_group[hl]; sent_buf.append((head_group[hl], rr, False)); continue
        defn = LK.definiteness(m)
        chosen = None
        if defn != "indef":
            comp = [e for e in ents if (window == 0 or (si - e.last_sent) <= window)
                    and LK._gender_ok(g, e.gender) and LK._number_ok(num, e.number)
                    and (e.gender or e.roles or any(LK.person_synset(h) is not None for h in e.heads))]
            poss_cluster = None
            if span and span[0] in POSS_GENDER:
                pg = POSS_GENDER[span[0]]
                pcs = [e for e in ents if LK._gender_ok(pg, e.gender) and (si - e.last_sent) <= window]
                poss_cluster = max(pcs, key=lambda e: e.last_sent).cluster if pcs else None
            best = None; best_s = -1e18; second_s = -1e18; best_desc = 0.0
            for e in comp:
                desc = 3.0 if hl in e.heads else (1.0 if any(DEC.wn_bridge(hl, h) for h in e.heads) else 0.0)
                s = desc
                if is_role and hl in e.roles:
                    s += 2.5
                if is_role and poss_cluster is not None and (hl, poss_cluster) in e.relations:
                    s += 4.0; desc = max(desc, 2.0)
                if e.event_agent_sents and (si - e.event_agent_sents[-1]) <= window:
                    s += 1.0
                s += 0.5 * (1.0 / (1.0 + (si - e.last_sent))) + 0.4 * _actr(e, si)
                if s > best_s:
                    second_s = best_s; best_s = s; best = e; best_desc = desc
                elif s > second_s:
                    second_s = s
            margin = best_s - second_s if second_s > -1e17 else 1e9
            if best is not None and best_desc >= link_thr and margin >= margin_thr:
                chosen = best                        # CONFIDENCE GATE: commit only high-margin; else defer
        if chosen is not None:
            chosen.observe(hl, g, num, si, rr, is_role); labels[m["midx"]] = chosen.cluster
        else:
            e = new_ent(); e.observe(hl, g, num, si, rr, is_role); labels[m["midx"]] = e.cluster
        if is_role and span and span[0] in POSS_GENDER and poss_cluster is not None:
            (chosen or ents[-1]).relations.add((hl, poss_cluster))
        sent_buf.append((labels[m["midx"]], rr, True))
    flush_event()
    return labels


def world_model_2pass(mentions, gaz, window=8, link_thr=0.5):
    """CONSOLIDATION (2-pass): pass 1 clusters; then build FULL entity records over the whole document from
    the pass-1 clustering; pass 2 RE-RESOLVES each common-noun person description against the consolidated
    records (descriptive/role/relation now complete), restricted to the foregrounded set. The brain's
    'accumulate the situation model, then resolve' -- tests whether consolidation crosses the bootstrapping
    wall that caps the single-pass former."""
    lab1 = world_model_predict(mentions, gaz, window=window, link_thr=link_thr)
    noms = sorted([m for m in mentions if not m["is_pronoun"]], key=lambda m: m["midx"])
    # consolidated records per pass-1 label
    recs = {}; sents_of = defaultdict(list); ev_of = defaultdict(list)
    sent_buf = []; cur = None
    for m in sorted(mentions, key=lambda x: x["midx"]):
        si = m["sent_idx"]
        if cur is None:
            cur = si
        if si != cur:
            ag = next((l for (l, rr, p) in sent_buf if p and rr == 0), None)
            if ag is not None:
                ev_of[ag].append(cur)
            sent_buf = []; cur = si
        if m["is_pronoun"]:
            continue
        l = lab1[m["midx"]]; hl = head_lemma(m["head"]); is_role = hl in ROLE_SET
        e = recs.get(l)
        if e is None:
            e = Entity(l); recs[l] = e
        e.observe(hl, m.get("gender") or m.get("name_gender"), LK._num_of(m), si, m.get("sent_role_rank", 99), is_role)
        sents_of[l].append(si)
        span = [w.lower() for w in m.get("span_toks", [m["head"]])]
        if is_role and span and span[0] in POSS_GENDER:
            pg = POSS_GENDER[span[0]]
            pcs = [ll for ll in recs if ll != l and LK._gender_ok(pg, recs[ll].gender) and recs[ll].last_sent <= si]
            if pcs:
                e.relations.add((hl, max(pcs, key=lambda ll: recs[ll].last_sent)))
        sent_buf.append((l, m.get("sent_role_rank", 99), True))
    ag = next((l for (l, rr, p) in sent_buf if p and rr == 0), None)
    if ag is not None:
        ev_of[ag].append(cur)
    for l in sents_of:
        sents_of[l].sort()
    # pass 2: re-resolve
    labels = dict(lab1)
    for m in noms:
        if is_name(m, gaz):
            continue
        hl = head_lemma(m["head"]); g = m.get("gender") or m.get("name_gender"); num = LK._num_of(m)
        if LK.person_synset(hl) is None or LK.definiteness(m) == "indef":
            continue
        si = m["sent_idx"]; span = [w.lower() for w in m.get("span_toks", [m["head"]])]; is_role = hl in ROLE_SET
        poss_cluster = None
        if span and span[0] in POSS_GENDER:
            pg = POSS_GENDER[span[0]]
            pcs = [ll for ll in recs if LK._gender_ok(pg, recs[ll].gender)
                   and any(abs(s - si) <= window for s in sents_of[ll])]
            poss_cluster = max(pcs, key=lambda ll: recs[ll].last_sent) if pcs else None
        best = None; best_s = -1e18; best_desc = 0.0
        for l, e in recs.items():
            near = [s for s in sents_of[l] if s != si]
            if not near or min(abs(s - si) for s in near) > window:
                continue
            if not (LK._gender_ok(g, e.gender) and LK._number_ok(num, e.number)):
                continue
            if not (e.gender or e.roles or any(LK.person_synset(h) is not None for h in e.heads)):
                continue
            desc = 3.0 if hl in e.heads else (1.0 if any(DEC.wn_bridge(hl, h) for h in e.heads) else 0.0)
            s = desc
            if is_role and hl in e.roles:
                s += 2.5
            if is_role and poss_cluster is not None and (hl, poss_cluster) in e.relations:
                s += 4.0; desc = max(desc, 2.0)
            if ev_of[l] and min(abs(x - si) for x in ev_of[l]) <= window:
                s += 1.0
            dt = min(abs(s2 - si) for s2 in near)
            s += 0.5 * (1.0 / (1.0 + dt))
            if s > best_s:
                best_s = s; best = l; best_desc = desc
        if best is not None and best_desc >= link_thr:
            labels[m["midx"]] = best
    return labels


def per_doc_wm(docs, gaz, window=8, subpop="char", two_pass=False, margin_thr=0.0):
    st = []
    for di, (doc, ms) in enumerate(docs):
        lab = (world_model_2pass(ms, gaz, window=window) if two_pass
               else world_model_predict(ms, gaz, window=window, margin_thr=margin_thr))
        if subpop == "char":
            chars = LK._char_clusters(ms); noms = [m for m in ms if not m["is_pronoun"] and m["cluster"] in chars]
        elif subpop == "name":
            noms = [m for m in ms if not m["is_pronoun"] and is_name(m, gaz)]
        else:
            noms = [m for m in ms if not m["is_pronoun"]]
        st.append(LK._doc_stats([lab[m["midx"]] for m in noms], ["g%d" % m["cluster"] for m in noms]))
    return st


def run_cluster(n=None, n_boot=1000, window=8):
    """Does the world-model resolution gain translate to a COREF-CLUSTERING (CoNLL) win with OWN records?"""
    docs, gaz = DIAG.load_docs(n)
    _, sh = LK.per_doc_stats(docs, gaz, "surface_head")
    _, tw = LK.per_doc_stats(docs, gaz, "TWIN", twin_seed=20260904, window=window)
    wm = per_doc_wm(docs, gaz, window=window)
    wm2 = per_doc_wm(docs, gaz, window=window, two_pass=True)
    wm2_nm = per_doc_wm(docs, gaz, window=window, subpop="name", two_pass=True)
    nm_no = []
    for doc, ms in docs:
        lab = DIAG.cluster_labels(ms, gaz, "name_only")
        noms = [m for m in ms if not m["is_pronoun"] and is_name(m, gaz)]
        nm_no.append(LK._doc_stats([lab[m["midx"]] for m in noms], ["g%d" % m["cluster"] for m in noms]))
    pooled = {"surface_head": LK._conll_from_stats(sh), "WM_1pass": LK._conll_from_stats(wm),
              "WM_2pass_consol": LK._conll_from_stats(wm2), "TWIN": LK._conll_from_stats(tw)}
    d1 = LK.bootstrap_delta(wm, sh, n_boot); d2 = LK.bootstrap_delta(wm2, sh, n_boot)
    d21 = LK.bootstrap_delta(wm2, wm, n_boot); d_tw = LK.bootstrap_delta(wm2, tw, n_boot)
    d_nm = LK.bootstrap_delta(wm2_nm, nm_no, n_boot)
    print("=" * 82)
    print("ENTITY-WORLD-MODEL FORMER -- character-cluster CoNLL (%d docs, window=%d)" % (len(docs), window))
    for a, s in pooled.items():
        print("  %-16s MUC %.4f B3 %.4f CEAFe %.4f CoNLL %.4f"
              % (a, s["muc_f1"], s["b3_f1"], s["ceafe_f1"], s["conll_avg"]))
    print("  WM_1pass-surface_head    %+.4f CI[%+.4f,%+.4f] ci_sep=%s" % (d1["delta"], d1["lo"], d1["hi"], d1["ci_sep"]))
    print("  WM_2pass-surface_head    %+.4f CI[%+.4f,%+.4f] ci_sep=%s" % (d2["delta"], d2["lo"], d2["hi"], d2["ci_sep"]))
    print("  WM_2pass-WM_1pass        %+.4f CI[%+.4f,%+.4f] ci_sep=%s" % (d21["delta"], d21["lo"], d21["hi"], d21["ci_sep"]))
    print("  WM_2pass-TWIN            %+.4f CI[%+.4f,%+.4f] ci_sep=%s" % (d_tw["delta"], d_tw["lo"], d_tw["hi"], d_tw["ci_sep"]))
    print("  named no-regress         %+.4f CI[%+.4f,%+.4f] ci_sep=%s" % (d_nm["delta"], d_nm["lo"], d_nm["hi"], d_nm["ci_sep"]))
    print("=" * 82)
    return {"pooled": pooled, "wm1_surface": d1, "wm2_surface": d2, "wm2_wm1": d21, "named_noregress": d_nm}


def run_ideal(n=None, n_boot=1000, window=8, margins=(0.0, 0.5, 1.0, 1.5, 2.0, 3.0)):
    """THE IDEAL solution: entity world-model + CONFIDENCE-GATED accumulation. Sweep the abstain margin;
    does deferring uncertain bindings (so records stay pure) turn the un-gated wash into a CI-sep win?"""
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    docs, gaz = DIAG.load_docs(n)
    _, sh = LK.per_doc_stats(docs, gaz, "surface_head")
    _, tw = LK.per_doc_stats(docs, gaz, "TWIN", twin_seed=20260904, window=window)
    nm_no = []
    for doc, ms in docs:
        lab = DIAG.cluster_labels(ms, gaz, "name_only")
        noms = [m for m in ms if not m["is_pronoun"] and is_name(m, gaz)]
        nm_no.append(LK._doc_stats([lab[m["midx"]] for m in noms], ["g%d" % m["cluster"] for m in noms]))
    sh_pooled = LK._conll_from_stats(sh)
    print("=" * 90)
    print("IDEAL: CONFIDENCE-GATED entity-world-model former -- char-cluster CoNLL (%d docs, window=%d)"
          % (len(docs), window))
    print("  surface_head floor CoNLL=%.4f  TWIN CoNLL=%.4f" % (sh_pooled["conll_avg"], LK._conll_from_stats(tw)["conll_avg"]))
    print("  %-8s %8s %8s %8s %8s | %-26s %-18s" % ("margin", "MUC", "B3", "CEAFe", "CoNLL", "vs surface_head", "named no-regress"))
    out = {}
    for mth in margins:
        wm = per_doc_wm(docs, gaz, window=window, margin_thr=mth)
        wm_nm = per_doc_wm(docs, gaz, window=window, subpop="name", margin_thr=mth)
        p = LK._conll_from_stats(wm)
        d = LK.bootstrap_delta(wm, sh, n_boot); dn = LK.bootstrap_delta(wm_nm, nm_no, n_boot)
        out[mth] = {"pooled": p, "vs_surface": d, "named_noregress": dn}
        print("  %-8.1f %8.4f %8.4f %8.4f %8.4f | %+.4f CI[%+.4f,%+.4f] sep=%-5s %+.4f sep=%s"
              % (mth, p["muc_f1"], p["b3_f1"], p["ceafe_f1"], p["conll_avg"],
                 d["delta"], d["lo"], d["hi"], d["ci_sep"], dn["delta"], dn["ci_sep"]))
    print("=" * 90)
    with open(os.path.join(OUT_DIR, "ideal_margin_sweep.json"), "w", encoding="ascii") as fh:
        json.dump({"surface_head": sh_pooled, "sweep": {str(k): v for k, v in out.items()}}, fh, indent=2)
    return out


def run_generalize(n=None, window=8, margin_thr=1.0):
    """DOES IT GENERALIZE? No weight was FIT to the data (reasoned brain-faithful priors). Confirm the two
    load-bearing results -- (a) resolution 0.255->0.540 with correct records, (b) deployable ~wash -- hold
    on DISJOINT held-out halves of the corpus (even vs odd docs). Stable across halves = not doc-overfit."""
    paths = sorted(glob.glob(os.path.join(CONLL_DIR, "*.conll")))
    if n:
        paths = paths[:n]
    gaz = load_name_gender()
    halves = {"A(even docs)": paths[0::2], "B(odd docs)": paths[1::2]}
    print("=" * 92)
    print("GENERALIZATION -- held-out split (zero fitted params; reasoned priors). window=%d margin=%.1f" % (window, margin_thr))
    for name, ph in halves.items():
        amb = resolve_ambiguous(ph, gaz, window)["ALL"]
        docs = [(os.path.basename(p), parse_litbank_conll(p, name_gender_map=gaz)[0]) for p in ph]
        _, sh = LK.per_doc_stats(docs, gaz, "surface_head")
        wm = per_doc_wm(docs, gaz, window=window, margin_thr=margin_thr)
        d = LK.bootstrap_delta(wm, sh, 600)
        print("  %-14s n_docs=%d | RESOLUTION: recency %.3f -> WORLD_MODEL %.3f (n=%d) | DEPLOY CoNLL: sh %.4f -> wm %.4f (%+.4f CI[%+.4f,%+.4f] sep=%s)"
              % (name, len(ph), amb["recency"], amb["WORLD_MODEL"], amb["n"],
                 LK._conll_from_stats(sh)["conll_avg"], LK._conll_from_stats(wm)["conll_avg"],
                 d["delta"], d["lo"], d["hi"], d["ci_sep"]))
    print("=" * 92)


def run(n=None, window=8):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    paths = sorted(glob.glob(os.path.join(CONLL_DIR, "*.conll")))
    if n:
        paths = paths[:n]
    gaz = load_name_gender()
    res = {"n_docs": len(paths), "window": window,
           "ambiguous_link_resolution": resolve_ambiguous(paths, gaz, window),
           "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor": "commonnoun_entity_world_model_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def _print(res):
    print("=" * 92)
    print("ENTITY WORLD-MODEL resolver on AMBIGUOUS person common-noun links (%d docs, window=%d, GOLD refs)"
          % (res["n_docs"], res["window"]))
    print("  resolution accuracy = pick the gold antecedent among >=2 compatible active person entities")
    a = res["ambiguous_link_resolution"]
    print("  %-16s %6s %9s %12s %12s %13s" % ("category", "n", "recency", "event_agent", "WORLD_MODEL", "union_oracle"))
    for c in ("ALL", "head_identical", "name_antecedent", "wordnet_bridge", "kinship_role", "residual"):
        s = a.get(c)
        if s:
            print("  %-16s %6d %9.3f %12.3f %12.3f %13.3f"
                  % (c, s["n"], s["recency"], s["event_agent"], s["WORLD_MODEL"], s["union_oracle"]))
    print("=" * 92)


def self_test():
    res = run(n=8)
    assert res["ambiguous_link_resolution"].get("ALL", {}).get("n", 0) > 0
    print("[self-test] PASS (%d ambiguous links over 8 docs)" % res["ambiguous_link_resolution"]["ALL"]["n"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--cluster", action="store_true", help="measure the DEPLOYABLE clustering CoNLL win")
    ap.add_argument("--ideal", action="store_true", help="the CONFIDENCE-GATED ideal: sweep the abstain margin")
    ap.add_argument("--generalize", action="store_true", help="held-out split: does it generalize?")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--window", type=int, default=8)
    a = ap.parse_args()
    if a.self_test:
        self_test(); return
    if a.generalize:
        run_generalize(n=a.n, window=a.window); return
    if a.ideal:
        run_ideal(n=a.n, window=a.window); return
    if a.cluster:
        run_cluster(n=a.n, window=a.window); return
    _print(run(n=a.n, window=a.window))


if __name__ == "__main__":
    main()
