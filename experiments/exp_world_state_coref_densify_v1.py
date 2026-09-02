"""exp_world_state_coref_densify_v1 -- CORE measurement for
`the_world_state_register_is_coref_blind_wire_it_through_coreference_and_measure_who_has_what`.

QUESTION: does keying the world-state register's HOLDER through the reader's OWN coreference (instead of the raw
head string) RECOVER who-has-what on real third-person prose, CI-separated over the coref-BLIND register, with a
shuffled-coref twin losing? And precisely how much of the gap is left (and to WHICH residual)?

BRAIN FRAME (PINNED): the situation model binds an event participant to a persistent DISCOURSE ENTITY, not to
the surface mention; possession/object-availability attaches to the ENTITY node (Glenberg/Meyer/Lindem 1987;
Zwaan & Radvansky 1998). Surface-string keying FRAGMENTS the entity (John...he...him -> 3 keys). Reuse the
reader's Centering-based he/she resolver (hdlab.event_centrality_coref, the reader's OWN coref) -- do NOT build a
new resolver. What the reader's coref does NOT cover (first-person DEIXIS I/me; object anaphora it) is the
located residual, measured here and built across in the sibling deixis cell.

ISOLATION (one variable = HOLDER keying): the object key is held CONSTANT across arms (nominal theme surface head)
and everything is scored in GOLD-CLUSTER space, so the ONLY thing that varies between BLIND and READER is whether
a pronoun holder is resolved to its entity. Blind and reader are IDENTICAL on nominal holders; the gain is exactly
the reader's coref recall on he/she pronoun holders. FIRST/SECOND-person and object-pronoun holders are left
unresolved by BOTH (the residual -> the deixis/object-anaphora build).

ARMS (same fixed event stream from the substrate's OWN parser; differ only in the holder ENTITY KEY):
  blind    : holder key = raw head string (the wired register today).
  reader   : he/she pronoun holder -> reader's resolved gold cluster (hdlab coref); nominal -> head; I/you/it -> raw.
  gold     : holder -> its GOLD coref cluster (oracle ceiling; defines ground truth).
  twin     : reader arm with the per-target resolved-cluster assignments SHUFFLED (coref-shaped, wrong identity).

CONTROLS: gold oracle == 1.0 by construction (sanity); shuffled-coref twin must LOSE CI-sep (correct identity, not
any coref-shaped signal, does the work); change-point positive control (the holder the register reports CHANGES at
the transferring event). Population saved. Glass-box: substrate's OWN parser + OWN coref; NO spaCy/LLM.
# KB_REFERENT: data/corpora/litbank_coref_conll
# KB_REFERENT: data/frontend_assets/pos_tagger_ud_ewt_upos.json
# KB_REFERENT: data/frontend_assets/arc_parser_hashed_ud_ewt.npz
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import glob
import json
import sys
import time
from collections import Counter, defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_world_state_realtext_mcscript_v1 as RT
from experiments.exp_world_state_coref_diagnose_v1 import (
    classify_pron, _mention_pos_map, _sentences_from_conll, THIRD_PERSON)

ANCHOR = "world_state_coref_densify_v1"
from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_" + ANCHOR)
LITBANK_DIR = os.path.join(REPO, "data", "corpora", "litbank_coref_conll")


def extract_ops_idx(cr, lex, lemma_word):
    """RT.extract_ops but returns within-sentence 0-based token index (wtok) for agent/theme/recipient/source
    so each role filler can be aligned to a gold mention. Role picking mirrors RT.extract_ops EXACTLY."""
    toks = cr.tokens; pos = cr.pos; heads = cr.heads
    n = len(toks); low = [w.lower() for w in toks]
    out = []
    for vi in range(1, n + 1):
        if pos[vi - 1] != "VERB":
            continue
        lem = lemma_word(low[vi - 1])
        entry = lex.get(lem)
        if entry is None:
            continue
        deps = [a for a in range(1, n + 1) if heads.get(a) == vi]
        subj = [a for a in deps if pos[a - 1] in RT.NOMINAL and a < vi]
        obj = [a for a in deps if pos[a - 1] in RT.NOMINAL and a > vi]
        agent_a = subj[-1] if subj else None
        theme_a = obj[0] if obj else None
        recip_a = src_a = None
        for i in range(1, n + 1):
            if pos[i - 1] == "ADP" and heads.get(i) and pos[heads[i] - 1] in RT.NOMINAL:
                hw = low[i - 1]; nomi = heads[i]
                if hw in ("to", "unto", "toward"):
                    recip_a = nomi
                elif hw in ("from", "off"):
                    src_a = nomi
        op = entry["op"]
        # DOUBLE-OBJECT ditransitive (brain-faithful: the ditransitive construction is recipient-BEFORE-theme,
        # Goldberg 1995): "gave HER the book" -> obj = [her, book]; with no to-PP recipient the FIRST post-verbal
        # nominal is the recipient (indirect object) and the SECOND is the theme. Fixes both the mis-extracted
        # theme (was 'her') and recovers the pronoun-recipient HOLDER the to-PP rule missed.
        if op == "GIVE" and recip_a is None and len(obj) >= 2:
            recip_a = obj[0]
            theme_a = obj[1]
        arg2_a = recip_a if op == "GIVE" else (src_a if op == "GET" else None)

        def pack(a):
            return None if a is None else {"wtok": a - 1, "head": low[a - 1]}
        out.append({"verb": lem, "op": op,
                    "AGENT": pack(agent_a), "PATIENT": pack(theme_a), "ARG2": pack(arg2_a)})
    return out


def build_head2cluster(mentions):
    """nominal (non-pronoun) surface head -> majority gold cluster. The anti-circular scoring side-map
    (coref.py protocol): the resolver never sees gold; scoring maps a surface entity to its gold cluster."""
    c = defaultdict(Counter)
    for m in mentions:
        if not m["is_pronoun"]:
            c[m["head"]][m["cluster"]] += 1
    return {h: cc.most_common(1)[0][0] for h, cc in c.items()}


def run_doc(path, gen, lex, lemma_word, reader_ec, reader_cls, mem_seed, sup_kw, event_n_dim, rng):
    """Return a list of per-query records for this document: (gold_cluster, blind_ok, reader_ok, gold_ok,
    twin_ok, holder_class, changed) -- one per (transferred nominal object, post-event t)."""
    from hdlab.coref import parse_litbank_conll, build_pronoun_targets, load_name_gender
    gaz = load_name_gender()
    mentions, n_sents = parse_litbank_conll(path, name_gender_map=gaz)
    if not mentions:
        return []
    toks_by_sent = _sentences_from_conll(path)
    if len(toks_by_sent) != n_sents:
        return []
    posmap = _mention_pos_map(mentions)
    head2cl = build_head2cluster(mentions)
    targets = build_pronoun_targets(mentions)

    # reader's OWN coref (faithful reuse of the live config) -> target_midx -> resolved gold cluster.
    sid_fixed = [i // 5 for i in range(n_sents)]
    recs = reader_ec.resolve_stream(mentions, targets, scene_ids=sid_fixed, topical_mode="rolemass",
                                    query_memory=True, centrality_mode="event_role", **sup_kw)
    midx2res = {}
    for r in recs:
        midx2res[r["target_midx"]] = r.get("resolved_cluster")
    # twin: a single-instance random draw from the same-gender candidate pool (kept as a representative
    # single shuffle); the powered info-free control is the K-permutation NULL in run(), which draws each
    # he/she holder a random SAME-GENDER cluster (coref-shaped, wrong identity) and reports its p95.
    def gender_of(m):
        return m.get("gender") or m.get("name_gender")
    pool_by_g = {"masc": set(), "fem": set()}
    for m in mentions:
        g = gender_of(m)
        if g in ("masc", "fem"):
            pool_by_g[g].add(m["cluster"])
    pool_by_g = {g: sorted(s) for g, s in pool_by_g.items()}
    MASC = {"he", "him", "his"}

    def gold_cluster_of(tok, si):
        m = posmap.get((si, tok["wtok"]))
        return (m["cluster"] if m else None), m

    def key_blind(tok, si):
        return "S::" + tok["head"]                      # raw surface string (pronoun or nominal alike)

    def key_from_cluster(cl):
        return None if cl is None else "C%d" % cl

    def key_reader(tok, si):
        cl, m = gold_cluster_of(tok, si)
        if m is None:
            return "S::" + tok["head"]
        if m["is_pronoun"]:
            if m["head"] in THIRD_PERSON and m["midx"] in midx2res:   # reader resolves he/she only
                return key_from_cluster(midx2res[m["midx"]]) or ("S::" + tok["head"])
            return "S::" + tok["head"]                                 # I/you/it: reader out of scope -> raw
        # nominal -> its gold cluster via the anti-circular head->cluster side-map (same as blind's nominal path)
        return key_from_cluster(head2cl.get(m["head"])) or ("S::" + tok["head"])

    def key_twin(tok, si):
        # single-instance twin: he/she -> a random same-gender cluster (wrong identity, coref-shaped).
        cl, m = gold_cluster_of(tok, si)
        if m is None:
            return "S::" + tok["head"]
        if m["is_pronoun"]:
            if m["head"] in THIRD_PERSON:
                g = "masc" if m["head"] in MASC else "fem"
                pool = pool_by_g.get(g) or []
                return ("C%d" % pool[rng.integers(0, len(pool))]) if pool else ("S::" + tok["head"])
            return "S::" + tok["head"]
        return key_from_cluster(head2cl.get(m["head"])) or ("S::" + tok["head"])

    def key_gold(tok, si):
        cl, m = gold_cluster_of(tok, si)
        if m is None:
            return "S::" + tok["head"]
        return key_from_cluster(cl) or ("S::" + tok["head"])

    # score a holder KEY -> gold cluster (or None if unresolved surface string that is not a nominal head).
    def key_to_gold(key):
        if key is None:
            return None
        if key.startswith("C"):
            return int(key[1:])
        s = key[3:]                      # "S::head"
        return head2cl.get(s)            # nominal head -> cluster; pronoun string -> None (unresolved)

    from hdlab.world_state_register import WorldState
    arms = {"blind": key_blind, "reader": key_reader, "gold": key_gold, "twin": key_twin}
    # build the fixed event stream (reading order) with per-arm reps; theme key = nominal surface head (const).
    events = []   # (si, inst)
    for si, toks in enumerate(toks_by_sent):
        if not toks:
            continue
        try:
            cr = gen.generate(" ".join(toks))
        except Exception:
            continue
        if len(cr.tokens) != len(toks):
            continue
        for inst in extract_ops_idx(cr, lex, lemma_word):
            events.append((si, inst))

    ws = {a: WorldState() for a in arms}
    # object key = theme surface head (held constant); only NOMINAL themes enter the primary metric.
    obj_is_nominal = {}
    holder_gold = {}     # per event index -> gold cluster of the holder-after token (or None)
    holder_class = {}
    holder_pool = {}     # per event index -> same-gender candidate clusters (for the he/she NULL)
    for t, (si, inst) in enumerate(events):
        theme = inst["PATIENT"]
        objkey = ("S::" + theme["head"]) if theme else None
        # holder-after token: recipient(ARG2) for GIVE, agent for GET, agent(->None) for LOSE
        htok = inst["ARG2"] if (inst["op"] == "GIVE" and inst["ARG2"]) else inst["AGENT"]
        if theme is not None:
            m_theme = posmap.get((si, theme["wtok"]))
            obj_is_nominal[t] = (m_theme is None) or (not m_theme["is_pronoun"])   # nominal/unannotated obj = stable
        else:
            obj_is_nominal[t] = False
        holder_pool[t] = None
        if htok is not None:
            gcl, hm = gold_cluster_of(htok, si)
            holder_gold[t] = gcl
            if hm is None:
                holder_class[t] = "no_gold_mention"
            elif not hm["is_pronoun"]:
                holder_class[t] = "nominal_name"
            else:
                holder_class[t] = classify_pron(hm["head"]) or "other_pron"
                if hm["head"] in THIRD_PERSON:
                    g = "masc" if hm["head"] in MASC else "fem"
                    holder_pool[t] = pool_by_g.get(g) or []
        else:
            holder_gold[t] = None; holder_class[t] = "no_holder"
        for a, kf in arms.items():
            rep = {"PRED": inst["verb"], "OP": inst["op"],
                   "PATIENT": objkey,
                   "AGENT": (kf(inst["AGENT"], si) if inst["AGENT"] else None),
                   "ARG2": (kf(inst["ARG2"], si) if inst["ARG2"] else None)}
            ws[a].apply_event(rep, t, read_preconditions=False)

    # queries: for each event that is a state-CHANGING transfer on a NOMINAL object with a GOLD-mention holder,
    # ask "who holds this object right after (t)"  -- scored vs the gold arm's holder.
    out = []
    for t, (si, inst) in enumerate(events):
        if not obj_is_nominal.get(t):
            continue
        if holder_gold.get(t) is None:           # need a gold identity for the holder-after
            continue
        theme = inst["PATIENT"]
        objkey = "S::" + theme["head"]
        gold_h = key_to_gold(ws["gold"].holder_of(objkey, t))
        if gold_h is None:
            continue
        def ok(a):
            return int(key_to_gold(ws[a].holder_of(objkey, t)) == gold_h)
        # change-point: did the reported holder change vs just before this event?
        prev = key_to_gold(ws["gold"].holder_of(objkey, t - 1)) if t > 0 else None
        out.append({"gold_cluster": gold_h, "blind": ok("blind"), "reader": ok("reader"),
                    "gold": ok("gold"), "twin": ok("twin"),
                    "holder_class": holder_class.get(t, "?"), "changed": int(prev != gold_h),
                    "pool": holder_pool.get(t)})
    return out


def boot(vals, n_boot, seed):
    vals = np.asarray(vals, float)
    if len(vals) == 0:
        return {"acc": None, "ci": [None, None], "n": 0, "half": None}
    rng = np.random.default_rng(seed)
    bs = [vals[rng.integers(0, len(vals), len(vals))].mean() for _ in range(n_boot)]
    lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
    return {"acc": round(float(vals.mean()), 4), "ci": [round(lo, 4), round(hi, 4)],
            "n": len(vals), "half": round((hi - lo) / 2, 4)}


def run(mode="full", n_docs=100, n_boot=2000, seed=20260901):
    from hdlab.candidate_generator import CandidateGenerator
    from hdlab.thematic_role_labeler import lemma_word
    from hdlab.event_centrality_coref import EVENT_N_DIM, EventCentralityReader
    from hdlab.coref import CorefReader
    from experiments.possession_operators import build_lexicon
    pos_ckpt = os.path.join(REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
    arc_ckpt = os.path.join(REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
    gen = CandidateGenerator.load(pos_ckpt, arc_ckpt)
    lex = build_lexicon(use_cache=True)
    SUP_KW = dict(suppress_generic=True, use_nonref=True, use_struct=True, chain_pronouns=True, use_gazetteer=True)
    MEM_SEED = 7
    reader_ec = EventCentralityReader(n_dim=EVENT_N_DIM, mem_seed=MEM_SEED)
    files = sorted(glob.glob(os.path.join(LITBANK_DIR, "*.conll")))
    if mode == "smoke":
        n_docs = 4
    files = files[:n_docs]
    rng = np.random.default_rng(seed)
    rows = []
    per_doc = []
    for path in files:
        try:
            r = run_doc(path, gen, lex, lemma_word, reader_ec, CorefReader, MEM_SEED, SUP_KW, EVENT_N_DIM, rng)
        except Exception as e:
            per_doc.append({"doc": os.path.basename(path), "ERROR": str(e)[:120]})
            continue
        rows.extend(r)
        per_doc.append({"doc": os.path.basename(path), "n_queries": len(r)})
    n = len(rows)
    res = {"anchor": ANCHOR, "mode": mode, "n_docs": len(files), "n_queries": n}
    if n:
        res["blind"] = boot([x["blind"] for x in rows], n_boot, seed + 1)
        res["reader"] = boot([x["reader"] for x in rows], n_boot, seed + 2)
        res["gold_oracle"] = boot([x["gold"] for x in rows], n_boot, seed + 3)
        res["twin_shuffled_coref"] = boot([x["twin"] for x in rows], n_boot, seed + 4)
        # paired reader-minus-blind margin + its bootstrap CI (the gate).
        d = np.asarray([x["reader"] - x["blind"] for x in rows], float)
        rng2 = np.random.default_rng(seed + 99)
        bs = [d[rng2.integers(0, len(d), len(d))].mean() for _ in range(n_boot)]
        res["reader_minus_blind"] = {"delta": round(float(d.mean()), 4),
                                     "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)],
                                     "half": round((float(np.percentile(bs, 97.5)) - float(np.percentile(bs, 2.5))) / 2, 4)}
        dt = np.asarray([x["reader"] - x["twin"] for x in rows], float)
        bst = [dt[rng2.integers(0, len(dt), len(dt))].mean() for _ in range(n_boot)]
        res["reader_minus_twin"] = {"delta": round(float(dt.mean()), 4),
                                    "ci": [round(float(np.percentile(bst, 2.5)), 4), round(float(np.percentile(bst, 97.5)), 4)]}
        res["holder_class_dist"] = dict(Counter(x["holder_class"] for x in rows))
        res["changed_frac"] = round(float(np.mean([x["changed"] for x in rows])), 3)
        # DECISIVE subset: transfers whose HOLDER is a he/she pronoun (the reader's coref scope) -- the population
        # where coref-blindness bites. Blind ~0 by construction (a pronoun string maps to no cluster); reader =
        # coref recall; twin = chance; gold = 1. This is the clean mechanism claim (the aggregate dilutes it with
        # nominal holders, where no coref is needed).
        pron = [x for x in rows if x["holder_class"] == "third_person_reader_scope"]
        if pron:
            dpr = np.asarray([x["reader"] - x["blind"] for x in pron], float)
            rng3 = np.random.default_rng(seed + 7)
            bpr = [dpr[rng3.integers(0, len(dpr), len(dpr))].mean() for _ in range(n_boot)]
            # K-permutation NULL: each he/she holder drawn a random SAME-GENDER cluster (coref-shaped, wrong
            # identity). The powered info-free control -> null mean + p95; reader must beat p95.
            rng4 = np.random.default_rng(seed + 21)
            K = 2000
            null_accs = []
            pools = [(x["pool"] if x["pool"] else []) for x in pron]
            golds = [x["gold_cluster"] for x in pron]
            for _ in range(K):
                hits = 0
                for pool, g in zip(pools, golds):
                    if pool:
                        hits += int(pool[rng4.integers(0, len(pool))] == g)
                null_accs.append(hits / len(pron))
            null_accs = np.asarray(null_accs, float)
            res["pronoun_holder_subset"] = {
                "n": len(pron),
                "blind": boot([x["blind"] for x in pron], n_boot, seed + 11),
                "reader": boot([x["reader"] for x in pron], n_boot, seed + 12),
                "twin_single_draw": boot([x["twin"] for x in pron], n_boot, seed + 13),
                "gold": boot([x["gold"] for x in pron], n_boot, seed + 14),
                "shuffled_coref_null": {"mean": round(float(null_accs.mean()), 4),
                                        "p95": round(float(np.percentile(null_accs, 95)), 4),
                                        "reader_beats_null_p95": bool(np.mean([x["reader"] for x in pron]) > np.percentile(null_accs, 95))},
                "reader_minus_blind": {"delta": round(float(dpr.mean()), 4),
                                       "ci": [round(float(np.percentile(bpr, 2.5)), 4), round(float(np.percentile(bpr, 97.5)), 4)]},
            }
        # decompose accuracy by holder class (where the gain lives).
        byc = {}
        for cls in set(x["holder_class"] for x in rows):
            sub = [x for x in rows if x["holder_class"] == cls]
            byc[cls] = {"n": len(sub), "blind": round(np.mean([x["blind"] for x in sub]), 3),
                        "reader": round(np.mean([x["reader"] for x in sub]), 3)}
        res["by_holder_class"] = byc
    res["per_doc"] = per_doc[:20]
    return res


def _write(res):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    json.dump(res, open(tmp, "w", encoding="ascii"), indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[write] %s" % os.path.join(OUT_DIR, "metrics.json"), flush=True)


def self_test():
    """The register keying logic on a tiny synthetic transfer with a pronoun holder: blind fragments, reader
    (given a correct resolution) recovers. Pure-logic, no parser."""
    from hdlab.world_state_register import WorldState
    # John(cluster5) gets book; 'he'(->5) gives it to Mary(cluster6). Object key held const ('book').
    wsb, wsr, wsg = WorldState(), WorldState(), WorldState()
    # blind keys holders on raw strings; reader/gold on clusters.
    wsb.apply_event({"PRED": "get", "OP": "GET", "PATIENT": "S::book", "AGENT": "S::john"}, 0, read_preconditions=False)
    wsb.apply_event({"PRED": "give", "OP": "GIVE", "PATIENT": "S::book", "AGENT": "S::he", "ARG2": "S::mary"}, 1, read_preconditions=False)
    wsr.apply_event({"PRED": "get", "OP": "GET", "PATIENT": "S::book", "AGENT": "C5"}, 0, read_preconditions=False)
    wsr.apply_event({"PRED": "give", "OP": "GIVE", "PATIENT": "S::book", "AGENT": "C5", "ARG2": "C6"}, 1, read_preconditions=False)
    ok1 = wsb.holder_of("S::book", 0) == "S::john" and wsb.holder_of("S::book", 1) == "S::mary"
    ok2 = wsr.holder_of("S::book", 0) == "C5" and wsr.holder_of("S::book", 1) == "C6"
    print("[self-test] blind tracks raw strings: %s ; reader tracks clusters: %s" % (ok1, ok2), flush=True)
    assert classify_pron("he") == "third_person_reader_scope"
    print("[self-test] OK", flush=True)
    return 0 if (ok1 and ok2) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n-docs", type=int, default=100)
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    mode = "smoke" if args.smoke else args.mode
    t0 = time.time()
    res = run(mode=mode, n_docs=args.n_docs, n_boot=(400 if mode == "smoke" else args.n_boot))
    res["elapsed_s"] = round(time.time() - t0, 1)
    _write(res)
    if res["n_queries"]:
        print("  n_queries=%d over %d docs" % (res["n_queries"], res["n_docs"]), flush=True)
        print("  BLIND  %.3f %s" % (res["blind"]["acc"], res["blind"]["ci"]), flush=True)
        print("  READER %.3f %s   (reader-blind delta %.3f %s ; reader-twin %.3f %s)"
              % (res["reader"]["acc"], res["reader"]["ci"], res["reader_minus_blind"]["delta"],
                 res["reader_minus_blind"]["ci"], res["reader_minus_twin"]["delta"], res["reader_minus_twin"]["ci"]), flush=True)
        print("  TWIN   %.3f %s   GOLD %.3f %s" % (res["twin_shuffled_coref"]["acc"], res["twin_shuffled_coref"]["ci"],
              res["gold_oracle"]["acc"], res["gold_oracle"]["ci"]), flush=True)
        print("  holder classes: %s" % res["holder_class_dist"], flush=True)
        print("  by holder class: %s" % res["by_holder_class"], flush=True)
        ph = res.get("pronoun_holder_subset")
        if ph:
            print("  >> PRONOUN-HOLDER SUBSET (he/she; where blindness bites) n=%d:" % ph["n"], flush=True)
            print("     BLIND %.3f %s  READER %.3f %s  GOLD %.3f %s"
                  % (ph["blind"]["acc"], ph["blind"]["ci"], ph["reader"]["acc"], ph["reader"]["ci"],
                     ph["gold"]["acc"], ph["gold"]["ci"]), flush=True)
            print("     reader-blind delta %.3f %s" % (ph["reader_minus_blind"]["delta"], ph["reader_minus_blind"]["ci"]), flush=True)
            print("     shuffled-coref NULL mean=%.3f p95=%.3f  reader_beats_p95=%s"
                  % (ph["shuffled_coref_null"]["mean"], ph["shuffled_coref_null"]["p95"],
                     ph["shuffled_coref_null"]["reader_beats_null_p95"]), flush=True)
    else:
        print("  NO QUERIES (per_doc: %s)" % res["per_doc"][:6], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
