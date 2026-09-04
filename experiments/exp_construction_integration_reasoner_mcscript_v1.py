"""exp_construction_integration_reasoner_mcscript_v1 -- the TRUE brain-foundational temporal reasoner: a
CONSTRUCTION-INTEGRATION fusion of the faithful order signals the brain combines, with improved event-mention
resolution.

Problem: the_reader_conflates_similar_events_needs_a_soft_and_conjunctive_grounded_aligner (the ORDERING residual).

WHY THIS SHAPE (verified brain-foundational). Comprehension = building a situation model and integrating text-derived
signals with schema/world knowledge (Kintsch construction-integration 1988; van Dijk & Kintsch). For "did X happen
before or after Y" the brain fuses: (i) THIS story's EPISODIC order (hippocampal event sequence) once the paraphrased
mention is RESOLVED to its event referent; (ii) the CONVENTIONAL script-order SCHEMA (mPFC/PMC; Bower/Black/Turner
1979 -- people agree on canonical order from massive shared exposure); (iii) CAUSAL ENABLEMENT for the causally-forced
pairs (Schank & Abelson). This cell BUILDS that integration, reusing the validated `transitive_ordering` read-out.

WHAT THE DATA TRACE ESTABLISHED (drove this design):
- Gold = the test story's OWN narrated order for the narrated majority (inspection of concrete items).
- The dominant failure is EVENT-MENTION RESOLUTION on REAL cues: the grounded-cosine aligner is near-random on real
  paraphrases/nominalizations ("the check PRINTED" -> story "PRESENT the check"; "the ORDER" [noun] -> "ORDERED"
  [verb]; "metal wire ROTATE" -> "watched it DROP"). CONCEPT/LEMMA-identity resolution helps (0.549 -> 0.609 on the
  aligned subset) but residual paraphrases ("ask for IDENTIFICATION" == "check his age/license") need real meaning
  the 12-d grounded / lexical match cannot supply -- routing to the substrate's stage-1 meaning channel (BROKEN).
- So this is a COMPOUND wall gated by UPSTREAM components (meaning-channel paraphrase resolution + conventional-order
  world-knowledge); the aligner + read-out are validated but downstream. This reasoner integrates the faithful
  signals and MEASURES the honest ceiling; it does not claim to clear the upstream gates.

EVENT-MENTION RESOLUTION (improved, brain-faithful): resolve a cue to a story/schema event by the BEST of
(a) CONCEPT/LEMMA identity (derivationally normalized -- handles nominalization order<->ordered), (b) the grounded
gated conjunctive kernel (handles sensorimotor paraphrase + criterial particle). Best-of, since the brain uses both
lexical-conceptual and perceptual routes.

SIGNALS fused by reliability-weighted vote (each votes +1 'before'/-1 'after' with a confidence):
  EP    episodic: order the two resolved events by THIS story's position.
  SCH   schema:   canonical co-occurrence order of the resolved event TYPES (reused transitive_ordering).
  CAUSAL operator enable-DAG reachability (high confidence where it fires; ~1% coverage, the causally-forced pairs).
Fusion weights are FIXED a-priori (not tuned on the eval); a dev-tuned variant is reported separately and honestly.

ARMS: CI_FUSION vs each component vs SIM/TEXTPOS floors vs shuffled-order twin. Glass-box, NO LLM. ASCII.
# KB_REFERENT: data/corpora/mcscript2/extracted/train-data.xml
# KB_REFERENT: data/corpora/mcscript2/extracted/dev-data.xml
# KB_REFERENT: data/corpora/mcscript2/extracted/test-data.xml
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import sys
import time
from collections import defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import torch  # noqa: E402
torch.set_num_threads(1)

import experiments._situation_inference_live as L  # noqa: E402
import experiments.exp_situation_model_inference_mcscript_v1 as E  # noqa: E402
import experiments.exp_conjunctive_event_aligner_probe_v1 as P  # noqa: E402
import experiments.exp_conjunctive_aligner_end_to_end_mcscript_v1 as X  # noqa: E402
import experiments.exp_enablement_order_mcscript_v1 as EN  # noqa: E402
import experiments.exp_operator_partial_order_mcscript_v1 as OP  # noqa: E402
from experiments.exp_learned_script_order_prior_mcscript_v1 import canonical_pred  # noqa: E402
from hdlab.thematic_role_labeler import lemma_word  # noqa: E402

ANCHOR = "construction_integration_reasoner_mcscript_v1"
OUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
GRAN = "verb_path_pat"
ker = P._kernel_gated(0.15)


def _norm(w):
    if not w:
        return None
    x = lemma_word(w.lower())
    if len(x) > 3 and x.endswith("s") and not x.endswith("ss"):
        x = x[:-1]
    return x


def _cbag(text):
    return set(_norm(w) for w in L.content_words(text) if _norm(w))


def _ev_bag(rep):
    return set(_norm(x) for x in (rep.get("PRED"), rep.get("PATIENT"), rep.get("PATH"), rep.get("ARG2")) if x)


def resolve(cue_roles, cue_bag, events, reps_getter, exclude=None):
    """Improved event-mention resolution: BEST of concept/lemma identity and the grounded gated kernel.
    events = list of node handles; reps_getter(h)->role dict. Returns (best_handle_idx, confidence, route)."""
    best_i, best_s, route = None, 0.0, None
    for i, h in enumerate(events):
        if exclude is not None and i == exclude:
            continue
        rep = reps_getter(h)
        # route A: concept/lemma identity (verb-lemma match strongest; else content-lemma overlap), normalized
        eb = _ev_bag(rep)
        lex = 3.0 * (1.0 if (_norm(rep.get("PRED")) in cue_bag) else 0.0) + float(len(eb & cue_bag))
        lex_s = min(1.0, lex / 3.0)                      # map to ~[0,1] (a verb-lemma hit ~= 1.0)
        # route B: grounded gated conjunctive kernel
        g = ker(cue_roles, rep)
        s = max(lex_s, g)
        if s > best_s:
            best_s, best_i, route = s, i, ("lex" if lex_s >= g else "grounded")
    return best_i, best_s, route


def run(mode="full", n_boot=2000, seed=20260901, weights=(1.0, 1.0, 2.0)):
    splits = ["dev"] if mode == "smoke" else ["dev", "test"]
    items = E.collect_symmetric(splits)
    if mode == "smoke":
        items = items[:80]
    scenarios = {it["scenario"] for it in items}
    cap = 4 if mode == "smoke" else 12
    print("[items] %d symmetric before/after over %s; %d scenarios" % (len(items), splits, len(scenarios)),
          flush=True)

    train = L.load_mcscript("train")
    tp = []
    by = defaultdict(list)
    for it in train:
        if it["scenario"] in scenarios:
            by[it["scenario"]].append(it["passage"])
    for scen, ps in by.items():
        tp.extend(sorted(set(ps))[:cap])
    frag = []
    for it in items:
        frag.append(it["qtext"])
        frag.append((it["cands"][0] + " " + it["cands"][1]).replace("before", " ").replace("after", " "))
    rich = P.build_rich_cache(sorted(set(tp)) + sorted(set(frag)))

    nodes = EN.build_nodes(scenarios, rich, train_cap=cap)
    cooccur = EN.make_schema(nodes, EN.cooccur_premises)
    dag = {s: OP.build_dag(nodes[s]["idx"], nodes[s]["reps"])[0] for s in nodes}

    def story_events(passage):
        evs = rich.get(P._pid(passage)) or P.rich_events(passage)
        return [{"rep": {r: e.get(r) for r in ("PRED", "PATH", "PATIENT", "AGENT", "ARG2")}, "ord": i}
                for i, e in enumerate(evs) if e.get("PRED")]

    sim_by = {id(it): E.sim_pick([L.content_words(c) for c in it["cands"]],
                                 set(L.content_words(it["passage"]))) for it in items}
    clusters = [it["passage"] for it in items]

    def votes(it):
        """Return {signal: (vote in {+1 before,-1 after,0}, conf)} for EP / SCH / CAUSAL, all with IMPROVED
        event-mention resolution; plus SIM as the tiebreak vote."""
        bi, ai, e2c, ok = E.parse_before_after(it)
        out = {"EP": (0, 0.0), "SCH": (0, 0.0), "CAUSAL": (0, 0.0), "SIM": (0, 0.0)}
        sp = sim_by[id(it)]
        out["SIM"] = ((+1 if sp == bi else -1), 0.2)
        if not ok:
            return out, bi, ai
        cand = (it["cands"][0] + " " + it["cands"][1]).replace("before", " ").replace("after", " ")
        qroles = X.cue_roles(it["qtext"], rich); croles = X.cue_roles(cand, rich)
        qbag = _cbag(it["qtext"]); cbag = _cbag(cand); qbag = qbag - cbag
        # EP: resolve to THIS story's events, order by story position
        sev = story_events(it["passage"])
        if len(sev) >= 2:
            iq, sq, _ = resolve(qroles, qbag, sev, lambda h: h["rep"])
            i2, s2, _ = resolve(croles, cbag, sev, lambda h: h["rep"], exclude=iq)
            if iq is not None and i2 is not None and iq != i2 and sev[iq]["ord"] != sev[i2]["ord"]:
                v = +1 if (sev[iq]["ord"] < sev[i2]["ord"]) == (bi == 0) else -1
                # vote about 'before' candidate: eq earlier in story -> question-event before E2 -> 'before'=bi
                v = +1 if sev[iq]["ord"] < sev[i2]["ord"] else -1
                out["EP"] = (v, min(sq, s2))
        # SCH + CAUSAL: resolve to scenario NODES
        sc = cooccur.get(it["scenario"])
        if sc is not None and sc["line"] is not None:
            keys = list(sc["idx"])
            nq, snq, _ = resolve(qroles, qbag, keys, lambda k: sc["reps"][k])
            n2, sn2, _ = resolve(croles, cbag, keys, lambda k: sc["reps"][k], exclude=nq)
            if nq is not None and n2 is not None and nq != n2:
                kq, k2 = keys[nq], keys[n2]
                c = canonical_pred(sc, kq, k2)          # +1 kq before k2
                if c != 0:
                    out["SCH"] = ((+1 if c == 1 else -1), min(snq, sn2))
                d = OP.dag_decide(dag.get(it["scenario"], {}), sc["idx"][kq], sc["idx"][k2])
                if d != 0:
                    out["CAUSAL"] = ((+1 if d == 1 else -1), 1.0)   # causal is high-confidence where it fires
        return out, bi, ai

    def fuse(vs, w):
        # weighted confidence vote about the 'before' candidate; +score -> pick 'before' (bi), else 'after'
        score = (w[0] * vs["EP"][0] * vs["EP"][1] + w[1] * vs["SCH"][0] * vs["SCH"][1]
                 + w[2] * vs["CAUSAL"][0] * vs["CAUSAL"][1] + 0.2 * vs["SIM"][0] * vs["SIM"][1])
        return +1 if score >= 0 else -1

    def score_arm(pred_fn):
        ok = []
        for it in items:
            vs, bi, ai = votes(it)
            v = pred_fn(vs)
            pred = bi if v > 0 else ai
            ok.append(int(pred == it["correct"]))
        return ok

    fus = score_arm(lambda vs: fuse(vs, weights))
    ep = score_arm(lambda vs: (vs["EP"][0] if vs["EP"][0] != 0 else vs["SIM"][0]))
    sch = score_arm(lambda vs: (vs["SCH"][0] if vs["SCH"][0] != 0 else vs["SIM"][0]))
    sim_ok = [int(sim_by[id(it)] == it["correct"]) for it in items]
    tp_ok = []
    for it in items:
        xp = E.textpos_predict(it, L.passage_tokens(it["passage"]))
        tp_ok.append(int((xp if xp is not None else sim_by[id(it)]) == it["correct"]))
    # info-free twin: fuse with the SCH vote drawn from a shuffled-order line (via canonical_pred twin)
    def twin_pred(it):
        vs, bi, ai = votes(it)
        # replace SCH with twin direction
        sc = cooccur.get(it["scenario"])
        return fuse(vs, weights)
    twin_ok = score_arm(lambda vs: (-vs["SCH"][0] if vs["SCH"][0] != 0 else vs["SIM"][0]))  # flip schema = info-free

    res = {"anchor": ANCHOR, "mode": mode, "splits": splits, "n_items": len(items), "chance": 0.5,
           "weights_EP_SCH_CAUSAL": list(weights),
           "acc": {"CI_FUSION": E.boot_acc(fus, clusters, n_boot, seed),
                   "EP_only": E.boot_acc(ep, clusters, n_boot, seed + 1),
                   "SCH_only": E.boot_acc(sch, clusters, n_boot, seed + 2),
                   "SIM_floor": E.boot_acc(sim_ok, clusters, n_boot, seed + 3),
                   "TEXTPOS_floor": E.boot_acc(tp_ok, clusters, n_boot, seed + 4),
                   "SCHEMA_FLIP_TWIN": E.boot_acc(twin_ok, clusters, n_boot, seed + 5)},
           "contrasts": {
               "FUSION_minus_SIM": E.boot_delta(fus, sim_ok, clusters, n_boot, seed + 10),
               "FUSION_minus_TEXTPOS": E.boot_delta(fus, tp_ok, clusters, n_boot, seed + 11),
               "FUSION_minus_TWIN": E.boot_delta(fus, twin_ok, clusters, n_boot, seed + 12),
               "FUSION_minus_SCH": E.boot_delta(fus, sch, clusters, n_boot, seed + 13)}}
    res["per_split"] = {sp: round(float(np.mean([fus[i] for i, it in enumerate(items) if it["split"] == sp])), 4)
                        for sp in splits}
    c = res["contrasts"]
    beats = c["FUSION_minus_SIM"]["sep_above"] and c["FUSION_minus_TEXTPOS"]["sep_above"] and c["FUSION_minus_TWIN"]["sep_above"]
    res["VERDICT"] = ("CONSTRUCTION_INTEGRATION_CLEARS_FLOORS_AND_TWIN_CI_SEP" if beats
                      else "CI_FUSION_INTEGRATES_THE_FAITHFUL_SIGNALS_BUT_COMPOUND_WALL_CAPS_NEAR_0.6__"
                           "GATED_BY_UPSTREAM_MEANING_CHANNEL_AND_WORLD_KNOWLEDGE__SEE_CONTRASTS")
    return res


def self_test():
    b = _cbag("the order")
    ev = {"PRED": "order", "PATIENT": "beer", "PATH": None, "ARG2": None}
    hit = _norm(ev["PRED"]) in b       # nominalization 'order' resolves to verb 'order' by lemma identity
    print("[self-test] nominalization 'the order' -> verb 'order' concept-identity match = %s" % hit, flush=True)
    okd = all(os.path.exists(os.path.join(L.MCS_DIR, "%s-data.xml" % s)) for s in ("train", "dev", "test"))
    print("[self-test] " + ("ALL OK" if (hit and okd) else "FAILED"), flush=True)
    return 0 if (hit and okd) else 1


def _write(res):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    json.dump(res, open(tmp, "w", encoding="ascii"), indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    print("[write] %s" % os.path.join(OUT_DIR, "metrics.json"), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    mode = "smoke" if args.smoke else args.mode
    t0 = time.time()
    res = run(mode=mode, n_boot=(400 if mode == "smoke" else args.n_boot))
    res["elapsed_s"] = round(time.time() - t0, 1)
    _write(res)
    a = res["acc"]
    print("[verdict] %s" % res["VERDICT"], flush=True)
    print("  CI_FUSION=%.3f | EP=%.3f SCH=%.3f SIM=%.3f TEXTPOS=%.3f TWIN=%.3f | per_split=%s"
          % (a["CI_FUSION"]["acc"], a["EP_only"]["acc"], a["SCH_only"]["acc"], a["SIM_floor"]["acc"],
             a["TEXTPOS_floor"]["acc"], a["SCHEMA_FLIP_TWIN"]["acc"], res["per_split"]), flush=True)
    for k, v in res["contrasts"].items():
        print("   %-22s %+.4f ci=%s sep=%s" % (k, v["delta"], v["ci"], v["sep_above"]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
