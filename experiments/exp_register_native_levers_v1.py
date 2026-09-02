"""exp_register_native_levers_v1 -- the THREE faithful, data-unblocked levers the disambiguation located, each
built as the BRAIN's mechanism (no gold parses/POS, no LLM), measured with controls + modern retention.

CONTEXT (from exp_19c_reach_failure_diagnosis + exp_19c_copula_disambiguation): the 19c who-did-what/PP-chain
reachability gap is NOT dominated by the brief's named levers. Decomposition of the reach residual:
  * COPULA/predicative clauses = 23% of the population, reachability 0.19 (UD predicate-as-head vs the gold's
    copula-as-head convention) -- a CONSTRUCTION/representation gap, needs NO data.
  * GENUINE archaic open-class verb mistag = 2.2% (equal->ADJ, saw->NOUN) -- the real "robust tagging" slice.
  * PP-attachment error = 8% of failures -- the brief's primary lever; the raw-exposure selectional signal is
    REAL (AUC 0.64) but small-scope.
So the '19c verb-ID -0.10' that motivated the brief is ~84% copula-as-AUX (CORRECT UPOS), not tagger error.

THREE LEVERS, each brain-faithful:
  A. COPULA-aware predication (traverse the cop relation): copular predication is a real construction (subject BE
     predicate). Controls: open-verb slice must be a NO-OP; an info-free 'traverse-ALL-verbs' twin must not help;
     a de-contaminated predicate-complement subset for the clean-comprehension number.
  B. FREQUENT-FRAMES register tagging (Mintz 2003: children categorize novel words from closed-class frames
     'he ___ the'), learned from RAW 19c exposure -- override the modern tagger on open-class words in strongly
     category-diagnostic frames. Generalizes to any register from raw text; no gold POS.
  C. DECISION-respecting selectional integration (Hindle-Rooth + MacDonald constraint-satisfaction): re-attach a
     PP object verb-ward ONLY among the REAL competing candidates AND only when the parser was UNCERTAIN
     (low margin) -- the faithful fix for v1's post-hoc surgery that shattered the confident-correct majority.

MEASURE: PP-chain reachability (= PP-attach precision) + CHAIN who-did-what, LB_19c (register) + QA_modern
(retention), bootstrap CI + null_p95. CPU numpy only. ASCII. own dir. --smoke fast.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time, random
from collections import Counter, defaultdict
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_parser_gap_decomp_v1 as GD
import experiments.exp_arceager_parser_operator_v1 as AEO
import experiments.exp_register_native_pp_attachment_v1 as REG
from experiments.exp_19c_copula_disambiguation_v1 import COP_AUX, cop_aware_reach
from hdlab.predicate_argument_frontend import _attaches_to_verb

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_register_native_levers_v1")
MAX_HOPS = 8
SUBJ_PRON = {"he", "she", "it", "they", "we", "i", "you", "who", "which", "that", "there"}


# ---------- lever B: frequent-frames register tagging (Mintz) ----------
def build_frames(tagged, min_count=25, conf=0.75):
    """closed-class neighbour frame (prev_tag,next_tag) -> category distribution of the middle OPEN-class word,
    from raw exposure. Also a subject-pronoun frame (prev_word in SUBJ_PRON) -> category. Kept only where a frame
    predicts a single category with prob>=conf and support>=min_count. Morphological suffix backoff too."""
    FR = defaultdict(Counter); PR = defaultdict(Counter); SUF = defaultdict(Counter)
    for toks, tags in tagged:
        low = [t.lower() for t in toks]
        for i in range(1, len(toks) - 1):
            if tags[i] not in ("NOUN", "VERB", "ADJ", "ADV", "PROPN", "AUX"):
                continue
            FR[(tags[i - 1], tags[i + 1])][tags[i]] += 1
            if low[i - 1] in SUBJ_PRON:
                PR[low[i - 1]][tags[i]] += 1
            w = low[i]
            if len(w) >= 4:
                SUF[w[-3:]][tags[i]] += 1

    def collapse(D):
        out = {}
        for k, c in D.items():
            tot = sum(c.values()); cat, n = c.most_common(1)[0]
            if tot >= min_count and n / tot >= conf:
                out[k] = cat
        return out
    return {"FR": collapse(FR), "PR": collapse(PR), "SUF": collapse(SUF)}


def retag_frames(toks, pos, FM):
    """override the modern tag toward the frame-predicted category for open-class-confusable words (never touch
    closed class). Focus: recover VERB the modern tagger dropped to NOUN/ADJ/AUX on archaic forms."""
    pos = list(pos); L = len(toks); low = [t.lower() for t in toks]
    for i in range(L):
        if pos[i] not in ("NOUN", "ADJ", "AUX", "PROPN"):
            continue
        pred = None
        if 0 < i < L - 1:
            pred = FM["FR"].get((pos[i - 1], pos[i + 1]))
        if pred is None and i > 0 and low[i - 1] in SUBJ_PRON:
            pred = FM["PR"].get(low[i - 1])
        if pred is None and len(low[i]) >= 4:
            pred = FM["SUF"].get(low[i][-3:])
        # only apply a VERB-recovery override (the measured failure mode); keep it conservative
        if pred == "VERB" and pos[i] in ("NOUN", "ADJ"):
            pos[i] = "VERB"
    return pos


# ---------- lever C: decision-respecting, uncertainty-gated selectional re-attach ----------
def sel_adapt(toks, pos, heads, marg, A, tau=1.0, mgate=30.0):
    """re-attach a PP object verb-ward among REAL candidates only when (a) the register association prefers the
    verb (LA>tau) AND (b) the parser was UNCERTAIN about the object's attachment (raw MARGIN<mgate -- softmax conf
    is saturated ~0.99, the margin is the discriminative uncertainty signal). Faithful fix for v1's post-hoc
    surgery that shattered the confident-correct majority."""
    heads = dict(heads); L = len(toks); low = [t.lower().strip(".,;:!?\"'()[]") for t in toks]
    for p in range(1, L + 1):
        if pos[p - 1] != "ADP" or low[p - 1] not in REG.PREPS:
            continue
        obj = heads.get(p)
        if obj is None or obj in (0, p) or not (1 <= obj <= L):
            continue
        if marg.get(obj, 1e9) >= mgate:                      # uncertainty gate: skip confident (high-margin) attachments
            continue
        h_obj = heads.get(obj)
        if h_obj is not None and 1 <= h_obj <= L and pos[h_obj - 1] == "VERB":
            continue                                         # already verb-attached
        v = n = None
        for j in range(p - 2, max(-1, p - 2 - REG.WINDOW * 2), -1):
            if pos[j] == "VERB" and v is None:
                v = j + 1
            if pos[j] in ("NOUN", "PROPN") and n is None and (j + 1) != obj:
                n = j + 1
            if v and n:
                break
        if v is None:
            continue
        la = REG.assoc_LA(A, V1._lem(toks[v - 1]), low[n - 1] if n else None, low[p - 1])
        if la > tau:
            heads[obj] = v
    return heads


# ---------- eval ----------
def _reach_base(c1, v1, heads, pos, toks):
    return _attaches_to_verb(c1, v1, heads, pos, max_hops=MAX_HOPS)


def cand_gov_prep(toks, pos, heads, c1):
    """the preposition that governs candidate c1 (an ADP case-marking c1 or an ancestor), else the ADP just
    before it -- the prep whose selectional fit with the verb we score."""
    chain = []; cur = c1
    for _ in range(4):
        if cur is None or cur == 0:
            break
        chain.append(cur); cur = heads.get(cur)
    for p in range(1, len(toks) + 1):
        if pos[p - 1] == "ADP" and heads.get(p) in chain and toks[p - 1].lower() in REG.PREPS:
            return toks[p - 1].lower()
    if c1 - 2 >= 0 and pos[c1 - 2] == "ADP" and toks[c1 - 2].lower() in REG.PREPS:
        return toks[c1 - 2].lower()
    return None


def chain_pick_assoc(r, toks, pos, heads, reachfn, A, verb_lem):
    """SELECTION via the raw-exposure verb-prep association: among the REACHABLE candidates, pick the one whose
    governing preposition the verb most SELECTS (max LA), tie-broken by farther position. This applies the
    AUC-0.64 selectional signal to the SELECTION problem (which reachable noun is the argument), not attachment."""
    vi0 = r["verb_idx"]
    attached = [c0 for c0 in r["cand_idx"] if reachfn(c0 + 1, vi0 + 1, heads, pos, toks)]
    post = [c for c in attached if c > vi0]; pool = post or attached
    if not pool:
        return r.get("pos_pick")
    best = None; bestkey = (-1e9, -1)
    for c0 in pool:
        prep = cand_gov_prep(toks, pos, heads, c0 + 1)
        sc = REG.assoc_LA(A, verb_lem, None, prep) if prep else -2.0
        if (sc, c0) > bestkey:
            bestkey = (sc, c0); best = c0
    return toks[best] if best is not None and 0 <= best < len(toks) else r.get("pos_pick")


def chain_pick_r(r, toks, pos, heads, reachfn):
    vi0 = r["verb_idx"]; vi1 = vi0 + 1
    attached = [c0 for c0 in r["cand_idx"] if reachfn(c0 + 1, vi1, heads, pos, toks)]
    post = [c for c in attached if c > vi0]; pool = post or attached
    if not pool:
        return r.get("pos_pick")
    idx = max(pool); return toks[idx] if 0 <= idx < len(toks) else r.get("pos_pick")


def reach_all(gold1, v1, heads, pos, toks):
    """info-free TWIN of copula-aware: traverse one extra edge for EVERY verb (not just copulas)."""
    if _attaches_to_verb(gold1, v1, heads, pos, max_hops=MAX_HOPS):
        return True
    h = heads.get(v1)
    if h and h not in (0, v1) and (gold1 == h or _attaches_to_verb(gold1, h, heads, pos, max_hops=MAX_HOPS)):
        return True
    return False


def evaluate(path, tg, W, A, FM, register_is_19c):
    rows = [r for r in V1.load_pop(path) if REG.cand_ok(r)]
    M = defaultdict(list)
    for r in rows:
        toks = r["sent"].split(); vi0 = r["verb_idx"]; gi0 = r.get("gold_idx")
        if not toks or gi0 is None or not (0 <= vi0 < len(toks)) or not (0 <= gi0 < len(toks)):
            continue
        pos = tg.tag(toks); vi1, gi1 = vi0 + 1, gi0 + 1
        heads, conf, marg = AEO.parse_with_conf(toks, pos, W)
        # lever B: frequent-frames retag -> re-parse
        pos_ft = retag_frames(toks, pos, FM)
        if pos_ft != pos:
            heads_ft, conf_ft, marg_ft = AEO.parse_with_conf(toks, pos_ft, W)
        else:
            heads_ft, conf_ft, marg_ft = heads, conf, marg
        # lever C: selectional re-attach (on base parse), margin-gated
        heads_sel = sel_adapt(toks, pos, heads, marg, A)
        is_cop = toks[vi0].lower() in COP_AUX
        pred = heads.get(vi1)
        cop_clean = int(is_cop and pred not in (None, 0, vi1) and (gi1 == pred or heads.get(gi1) == pred))
        # reach metrics
        M["base_reach"].append(int(_attaches_to_verb(gi1, vi1, heads, pos, max_hops=MAX_HOPS)))
        M["cop_reach"].append(int(cop_aware_reach(gi1, vi1, heads, pos, toks)))
        M["twin_reach"].append(int(reach_all(gi1, vi1, heads, pos, toks)))          # info-free copula twin
        M["ftag_reach"].append(int(_attaches_to_verb(gi1, vi1, heads_ft, pos_ft, max_hops=MAX_HOPS)))
        M["sel_reach"].append(int(_attaches_to_verb(gi1, vi1, heads_sel, pos, max_hops=MAX_HOPS)))
        M["all_reach"].append(int(cop_aware_reach(gi1, vi1, sel_adapt(toks, pos_ft, heads_ft, marg_ft, A), pos_ft, toks)))
        # who-did-what metrics (chain_pick with different reachability)
        M["base_wdw"].append(int(chain_pick_r(r, toks, pos, heads, _reach_base) == r["gold_head"]))
        M["cop_wdw"].append(int(chain_pick_r(r, toks, pos, heads, cop_aware_reach) == r["gold_head"]))
        M["twin_wdw"].append(int(chain_pick_r(r, toks, pos, heads, reach_all) == r["gold_head"]))   # DECISIVE control
        M["sel_wdw"].append(int(chain_pick_r(r, toks, pos, heads_sel, _reach_base) == r["gold_head"]))
        M["ftag_wdw"].append(int(chain_pick_r(r, toks, pos_ft, heads_ft, cop_aware_reach) == r["gold_head"]))
        M["all_wdw"].append(int(chain_pick_r(r, toks, pos_ft, sel_adapt(toks, pos_ft, heads_ft, marg_ft, A), cop_aware_reach) == r["gold_head"]))
        # SELECTION via association (among cop-aware-reachable): the AUC-0.64 signal on the SELECTION problem
        vlem = V1._lem(toks[vi0])
        Ash = REG.shuffle_assoc(A)
        M["assocsel_wdw"].append(int(chain_pick_assoc(r, toks, pos, heads, cop_aware_reach, A, vlem) == r["gold_head"]))
        M["assocsel_twin_wdw"].append(int(chain_pick_assoc(r, toks, pos, heads, cop_aware_reach, Ash, vlem) == r["gold_head"]))
        M["is_cop"].append(int(is_cop)); M["cop_clean"].append(cop_clean)
        # UPOS non-regression: how many tokens did frequent-frames CHANGE, and on confident modern tags
        M["ft_changed"].append(sum(1 for a, b in zip(pos, pos_ft) if a != b))
        M["ntok"].append(len(toks))
    return M


def bootd(a, b, nboot, seed=13):
    a = np.array(a, float); b = np.array(b, float); d = a - b; n = len(d); rng = np.random.default_rng(seed)
    bs = np.array([d[rng.integers(0, n, n)].mean() for _ in range(nboot)]); lo, hi = np.percentile(bs, [2.5, 97.5])
    nu = np.array([(d * rng.choice([-1, 1], n)).mean() for _ in range(nboot)])
    return {"a": round(float(a.mean()), 4), "b": round(float(b.mean()), 4), "delta": round(float(d.mean()), 4),
            "ci_lo": round(float(lo), 4), "ci_hi": round(float(hi), 4), "half": round(float((hi - lo) / 2), 4),
            "null_p95": round(float(np.percentile(np.abs(nu), 95)), 4)}


def report(name, M, nboot):
    print("\n=== %s (n=%d) ===" % (name, len(M["base_reach"])), flush=True)
    out = {"n": len(M["base_reach"])}
    arms = [("cop_reach", "base_reach", "COPULA reach"), ("twin_reach", "base_reach", "TWIN(traverse-all) reach"),
            ("ftag_reach", "base_reach", "FTAG reach"), ("sel_reach", "base_reach", "SEL reach"),
            ("all_reach", "base_reach", "ALL reach"),
            ("cop_wdw", "base_wdw", "COPULA who-did-what"), ("twin_wdw", "base_wdw", "TWIN who-did-what [CONTROL]"),
            ("sel_wdw", "base_wdw", "SEL who-did-what"), ("ftag_wdw", "base_wdw", "FTAG+cop who-did-what"),
            ("all_wdw", "base_wdw", "ALL who-did-what")]
    for a, b, lbl in arms:
        d = bootd(M[a], M[b], nboot); sep = "CI-SEP" if d["ci_lo"] > 0 else ("NEG" if d["ci_hi"] < 0 else "ns")
        print("  %-28s %.4f->%.4f  d=%+.4f CI[%+.4f,%+.4f] null_p95=%.4f  %s"
              % (lbl, d["b"], d["a"], d["delta"], d["ci_lo"], d["ci_hi"], d["null_p95"], sep), flush=True)
        out[lbl] = d
    # is the COPULA who-did-what gain > the permissive TWIN? (copula-specificity, not just more candidates)
    dc = bootd(M["cop_wdw"], M["twin_wdw"], nboot)
    out["cop_vs_twin_wdw"] = dc
    print("  COPULA vs TWIN who-did-what:  d=%+.4f CI[%+.4f,%+.4f]  %s"
          % (dc["delta"], dc["ci_lo"], dc["ci_hi"], "COPULA>TWIN CI-sep" if dc["ci_lo"] > 0 else "not separated"), flush=True)
    # SELECTION via association: does ranking reachable candidates by verb-prep association beat farthest-pick,
    # and does the SHUFFLED-association twin lose? (the constructive test: the AUC-0.64 signal on SELECTION)
    das = bootd(M["assocsel_wdw"], M["cop_wdw"], nboot)          # assoc-select vs cop-aware farthest-pick
    dat = bootd(M["assocsel_wdw"], M["assocsel_twin_wdw"], nboot)  # assoc-select vs shuffled-assoc twin
    out["assocsel_vs_farpick"] = das; out["assocsel_vs_shuftwin"] = dat
    print("  ASSOC-SELECT vs farthest-pick: %.4f->%.4f d=%+.4f CI[%+.4f,%+.4f] %s"
          % (das["b"], das["a"], das["delta"], das["ci_lo"], das["ci_hi"], "CI-SEP" if das["ci_lo"] > 0 else ("NEG" if das["ci_hi"] < 0 else "ns")), flush=True)
    print("  ASSOC-SELECT vs SHUFFLED-assoc twin: d=%+.4f CI[%+.4f,%+.4f] %s"
          % (dat["delta"], dat["ci_lo"], dat["ci_hi"], "CI-SEP(signal real)" if dat["ci_lo"] > 0 else "not separated"), flush=True)
    # de-contaminated copula subset (gold IS the predicate complement, not a deep oblique)
    mask = np.array(M["cop_clean"], bool)
    if mask.sum() > 20:
        cb = np.array(M["base_wdw"])[mask]; cc = np.array(M["cop_wdw"])[mask]
        dcl = bootd(cc.tolist(), cb.tolist(), nboot)
        out["copula_clean"] = {"n": int(mask.sum()), **dcl}
        print("  [CLEAN copula subset n=%d] who-did-what %.4f->%.4f d=%+.4f CI[%+.4f,%+.4f] %s"
              % (mask.sum(), dcl["b"], dcl["a"], dcl["delta"], dcl["ci_lo"], dcl["ci_hi"], "CI-SEP" if dcl["ci_lo"] > 0 else "ns"), flush=True)
    out["ft_changed_per100tok"] = round(100 * sum(M["ft_changed"]) / max(1, sum(M["ntok"])), 3)
    out["copula_share"] = round(sum(M["is_cop"]) / max(1, len(M["is_cop"])), 4)
    print("  [FTAG changed %.2f tags / 100 tokens ; copula share %.3f]" % (out["ft_changed_per100tok"], out["copula_share"]), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true"); ap.add_argument("--nboot", type=int, default=2000)
    ap.add_argument("--exposure", type=int, default=120000)
    args = ap.parse_args()
    if args.smoke:
        args.exposure = 6000; args.nboot = 400
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json"))
    W = AEO.load_model(AEO.MODEL_PATH)
    tag19 = REG.load_or_tag(os.path.join(REG.OUT_DIR, "tagged_19c_%d.jsonl" % args.exposure), REG.LB_RAW, args.exposure, tg)
    # dedup eval sentences
    ev = set(" ".join(r["sent"].split()) for pth in (V1.LB, V1.QA) for r in V1.load_pop(pth))
    tag19d = [(t, p) for (t, p) in tag19 if " ".join(t) not in ev]
    A19 = REG.build_assoc(tag19d)
    FM = build_frames(tag19d)
    print("[built] assoc(VA=%d) frames(FR=%d PR=%d SUF=%d) from %d exposure sents"
          % (A19["n_va"], len(FM["FR"]), len(FM["PR"]), len(FM["SUF"]), len(tag19d)), flush=True)

    res = {"exposure": len(tag19d), "frames": {k: len(FM[k]) for k in FM}}
    Mlb = evaluate(V1.LB, tg, W, A19, FM, True)
    res["LB_19c"] = report("LB_19c (register)", Mlb, args.nboot)
    Mqa = evaluate(V1.QA, tg, W, A19, FM, False)
    res["QA_modern"] = report("QA_modern (retention)", Mqa, args.nboot)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "register_native_levers_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
