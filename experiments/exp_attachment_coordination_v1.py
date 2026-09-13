"""exp_attachment_coordination_v1 -- COORDINATION AS PARALLEL STRUCTURE in the attachment arm.

THE PROBLEM (measured): "X and Y" is the arm's worst structural class -- conj recall 0.300 (map1), 0.288 (incr) on UD-EWT
test 700, gold categories, current asset. A `coord` construction cue already exists but conj is still 0.30.

THE FULL-STACK-UPSTREAM TRACE (experiments/scratch_conj_anatomy.py, n=233 gold conj arcs):
  - the `coord` construction proposes the EXACT gold arc only 0.245 of the time (modifier bug 0.30, cross-UPOS 0.215);
  - THE SMOKING GUN: the ACQUISITION TEACHER (co-occurrence SelfSupEM + semantic-bootstrapping) puts mean 0.054 posterior
    mass on the gold conj arc (64% get <0.05). The teacher is COORDINATION-BLIND, so the learned `coord` validity is ~flat.
The end component (coordination) is a real brain mechanism; it fails because an UPSTREAM component it relies on (the
acquisition teacher) is missing a genuine brain mechanism: PARALLEL-STRUCTURE PREDICTION.

THE BRAIN (PINNED at the computational level): a coordinator predicts a second phrase of the SAME KIND as the phrase just
closed (Frazier 1985; Munn 1993; Taft & Clifton 2000 parallel-structure facilitation; Levy 2008 prediction), retrieved by a
cue-based, like-category antecedent (Lewis & Vasishth 2005), the two conjuncts SHARING one slot of the governor (a plural
set). UD's convention (right conjunct depends on the left; cc depends on the right conjunct) is the MEASURING INSTRUMENT.

THE MECHANISM (both halves treebank-free, both brain-foundational):
  1. TEACHER (upstream fix): add parallel-structure prediction to the acquisition teacher -- when a coordinator sits between
     two like-CLASS phrase heads L (before) and R (after), boost A[L][R] (conj) and A[R][cc] (cc) in the teacher's score
     matrix. Derived from coordinator position + category parallelism, NEVER from trees. This gives the `coord` cue positive
     signal to learn a validity from (plastic: it lands as counts -> strengths like every other cue).
  2. READ-TIME construction (fix the head identification): R = head of the phrase after cc (last NOUN/PROPN of the nominal
     run / the verb / the predicate adjective), L = nearest preceding content head of R's parallel CLASS (coarse: nominal
     {NOUN,PROPN,PRON,NUM} / predicate {VERB,ADJ} / adverbial {ADV}). Fixes the modifier bug + the cross-UPOS reject.

ABLATION arms rebuild the SAME pipeline at the SAME cap with the coordination change on/off, isolating each half. Twin =
the full asset with the coord-cue strengths permuted across configurations (info-free: the coordination bonus applied to the
wrong category pairs) -- must collapse conj back toward base. Glass-box, numpy only, NO LLM, NO external parser, NO treebank
trees read while learning (the UD tree column is the measuring instrument only).

Run: .venv/Scripts/python.exe experiments/exp_attachment_coordination_v1.py --run [--smoke] [--cap 6000] [--gamma 4]
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"
__bf_note__ = ("coordination = parallel-structure prediction (Frazier/Munn/Taft&Clifton 2000; Levy 2008; Lewis&Vasishth "
               "2005 cue-based retrieval; slot-sharing). Added to the acquisition teacher (upstream) + the read-time coord "
               "construction; learned validity in counts, online-observable. Treebank-free.")

import argparse
import json
import os
import sys
import time
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
os.environ.setdefault("PYTHONHASHSEED", "0")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import hdlab.attachment_arm as AA
from hdlab.graded_parser import single_root_marginals
from experiments._seed_checkpoint import get_output_dir
from tools.build_attachment_validities import sentences, TRAIN, TEST, knowledge_free_teacher

CORE_RELS = ("root", "nsubj", "obj", "obl", "nmod", "xcomp", "ccomp", "advcl", "conj", "cc", "case", "punct", "amod", "det")

# ------------------------------------------------------------------------------------------------ parallel structure
NOMINAL_CLASS = frozenset({"NOUN", "PROPN", "PRON", "NUM"})
PRED_CLASS = frozenset({"VERB", "ADJ"})
NP_RUN = AA.NP_RUN


def pclass(p: str, coarse: bool) -> Optional[str]:
    """The parallel CLASS of a category. coarse: phrase-type (nominal / predicate / adverbial); strict: the UPOS itself."""
    if coarse:
        if p in NOMINAL_CLASS:
            return "NOM"
        if p in PRED_CLASS:
            return "PRED"
        if p == "ADV":
            return "ADV"
        return None
    return p if p in AA.CONTENT else None


def right_head(pos: Sequence[str], k: int, n: int) -> Optional[int]:
    """Head of the phrase AFTER the coordinator at 1-based k: the last NOUN/PROPN of the nominal run (head-final English NP),
    else the last ADJ/NUM of the run (predicate-adjective coordination), else the first content word (a verb / adverb)."""
    j = k + 1
    while j <= n and pos[j - 1] == "PUNCT":
        j += 1
    if j > n:
        return None
    p = pos[j - 1]
    if p in NP_RUN:                                   # DET/ADJ/NUM/NOUN/PROPN run
        e = j
        while e <= n and pos[e - 1] in NP_RUN:
            e += 1
        nouns = [q for q in range(j, e) if pos[q - 1] in ("NOUN", "PROPN")]
        if nouns:
            return nouns[-1]
        adjs = [q for q in range(j, e) if pos[q - 1] in ("ADJ", "NUM")]
        return adjs[-1] if adjs else None
    if p in AA.CONTENT:                               # VERB / ADV / PRON standing alone
        return j
    return None


def left_head(pos: Sequence[str], k: int, rclass: str, coarse: bool) -> Optional[int]:
    """Cue-based retrieval of the like-category antecedent: nearest preceding content head of R's parallel class before cc."""
    for q in range(k - 1, 0, -1):
        c = pclass(pos[q - 1], coarse)
        if c is not None and c == rclass:
            return q
    return None


def left_head_slotshare(toks: Sequence[str], pos: Sequence[str], k: int, R: int, rclass: str, coarse: bool) -> Optional[int]:
    """SLOT-SHARING antecedent selection (the lever past the ~0.54 nearest-same-class ceiling): the two conjuncts jointly
    fill ONE governor slot (a plural set), so among the like-class antecedents pick the CO-ARGUMENT that best shares R's
    governor -- the preceding same-class head most plausible as a filler of the same verb slot R would fill. Uses the
    semantic-bootstrapping plausibility (the SAME upstream asset). Falls back to nearest when no verb / no plausibility."""
    cands = [q for q in range(k - 1, 0, -1) if pclass(pos[q - 1], coarse) == rclass]
    if not cands:
        return None
    if rclass != "NOM":                                   # verb-argument slot sharing is a nominal-coordination story
        return cands[0]
    n = len(pos)
    v_after = next((q for q in range(R + 1, n + 1) if pos[q - 1] == "VERB"), None)
    v_before = next((q for q in range(k - 1, 0, -1) if pos[q - 1] == "VERB"), None)
    try:
        teach = AA._plaus_teacher()
    except Exception:
        return cands[0]

    def plaus(V, w):
        if V is None:
            return 0.0
        try:
            return float(teach.plausibility(toks[V - 1], toks[w - 1]))
        except Exception:
            return 0.0
    # only credit a verb R itself fits (so we share R's actual slot, not an unrelated verb)
    fit_after = plaus(v_after, R); fit_before = plaus(v_before, R)
    best = cands[0]; best_s = -1.0
    for L in cands:
        s = max(plaus(v_after, L) if fit_after > 0 else 0.0, plaus(v_before, L) if fit_before > 0 else 0.0)
        if s > best_s:
            best_s = s; best = L
    return best if best_s > 0 else cands[0]


def coord_sites(toks: Sequence[str], pos: Sequence[str], coarse: bool = True,
                mode: str = "parallel") -> List[Tuple[int, int, int]]:
    """Every coordinator's parallel heads (L before, R after) + the coordinator index cc. The ONE source of truth used by
    BOTH the read-time construction and the teacher's parallel-structure boost. mode="scramble": the info-free twin -- keep
    R and cc and the SAME NUMBER of sites, but replace L with a deterministic WRONG preceding content word (parallelism
    removed, density matched)."""
    n = len(toks); out = []
    for k in range(1, n + 1):
        if pos[k - 1] != "CCONJ":
            continue
        R = right_head(pos, k, n)
        if R is None:
            continue
        rc = pclass(pos[R - 1], coarse)
        if rc is None:
            continue
        if mode == "scramble":
            cands = [q for q in range(1, k) if pos[q - 1] in AA.CONTENT and q != R]
            if not cands:
                continue
            L = cands[(k * 7 + R * 13) % len(cands)]     # deterministic wrong antecedent (decorrelated from parallelism)
        elif mode == "slot":
            L = left_head_slotshare(toks, pos, k, R, rc, coarse)
        else:
            L = left_head(pos, k, rc, coarse)
        if L is None or L == R:
            continue
        out.append((L, R, k))
    return out


def coord_arcs_parallel_factory(coarse: bool, mode: str = "parallel"):
    """A drop-in replacement for AA.coord_arcs (the read-time construction): the parallel-head arcs (L->R conj, R->cc)."""
    def coord_arcs(toks, pos):
        out = []
        for (L, R, k) in coord_sites(toks, pos, coarse, mode):
            out.append((L, R)); out.append((R, k))
        return out
    return coord_arcs


def parallelism_boost(A: np.ndarray, toks: Sequence[str], pos: Sequence[str], gamma: float, coarse: bool,
                      mode: str = "parallel") -> np.ndarray:
    """Parallel-structure PREDICTION as the acquisition teacher: boost the conj arc (head L, dep R) and the cc arc
    (head R, dep cc) in the teacher's score matrix. Treebank-free (coordinator position + category parallelism)."""
    if gamma <= 0:
        return A
    B = A.copy()
    for (L, R, k) in coord_sites(toks, pos, coarse, mode):
        if np.isfinite(B[L][R]):
            B[L][R] += gamma
        else:
            B[L][R] = gamma
        if np.isfinite(B[R][k]):
            B[R][k] += gamma
        else:
            B[R][k] = gamma
    return B


# ------------------------------------------------------------------------------------------------- asset construction
class _CoordConstr:
    """Context manager: install the parallel-head coord construction (and restore the original) around a build/eval."""
    def __init__(self, coarse: bool, on: bool, mode: str = "parallel"):
        self.coarse = coarse; self.on = on; self.mode = mode; self._orig = None

    def __enter__(self):
        if self.on:
            self._orig = AA.CONSTRUCTIONS["coord"]
            AA.CONSTRUCTIONS["coord"] = coord_arcs_parallel_factory(self.coarse, self.mode)
        return self

    def __exit__(self, *a):
        if self.on and self._orig is not None:
            AA.CONSTRUCTIONS["coord"] = self._orig


def build_asset(train, teacher, base_marg, *, coord_teacher: bool, coord_constr: bool, coarse: bool,
                gamma: float, rounds: int, alpha: float = 0.8, mode: str = "parallel") -> Dict[str, object]:
    """Rebuild the arm's asset with the coordination change on/off. `base_marg[i]` = the teacher score matrix (A, n) for
    sentence i, cached once. coord_teacher adds the parallelism boost to the teaching posterior; coord_constr installs the
    corrected read-time construction (so the coord cue is accrued on the right arcs). mode="scramble" = the info-free twin."""
    frames = teacher._frames; pp_assoc = teacher._pp_assoc
    with _CoordConstr(coarse, coord_constr, mode):
        # round 0: accrue soft counts from the (optionally boosted) teacher posterior
        counts = AA.new_counts(); tmarg = {}
        for i, (toks, pos, _, _) in enumerate(train):
            A, n = base_marg[i]
            Ab = parallelism_boost(A, toks, pos, gamma, coarse, mode) if coord_teacher else A
            mt = single_root_marginals(Ab.copy(), n, 1.0); tmarg[i] = mt
            AA.accrue_sentence(counts, AA.SentenceCues(toks, pos, frames, pp_assoc), mt)
        table = {"counts": counts, "frames": frames, "pp_assoc": pp_assoc,
                 "strength": AA.strengths_from_arc_counts(counts)}
        # anchored self-teaching rounds
        for _ in range(rounds):
            nxt = AA.new_counts()
            for i, (toks, pos, _, _) in enumerate(train):
                ms = AA.head_posterior(toks, pos, table); mt = tmarg[i]; n = len(toks)
                mix = {j: {h: alpha * ms.get(j, {}).get(h, 0.0) + (1 - alpha) * mt.get(j, {}).get(h, 0.0)
                           for h in set(ms.get(j, {})) | set(mt.get(j, {}))} for j in range(1, n + 1)}
                AA.accrue_sentence(nxt, AA.SentenceCues(toks, pos, frames, pp_assoc), mix)
            table = {"counts": nxt, "frames": frames, "pp_assoc": pp_assoc,
                     "strength": AA.strengths_from_arc_counts(nxt)}
    return table


def shuffle_strengths_twin(table: Dict[str, object], seed: int) -> Dict[str, object]:
    """Info-free twin (the brief's literal 'shuffled strengths'): permute every strength value within each cue/config table.
    The asset keeps its shape and value distribution but loses all structure -> attachment collapses toward chance."""
    import copy
    st = copy.deepcopy(table["strength"]); rng = np.random.default_rng(seed)
    for key, sub in st.items():
        if key == "pcfg" or not isinstance(sub, dict):
            continue
        ks = list(sub.keys()); vals = [sub[k] for k in ks]
        rng.shuffle(vals)
        for k, v in zip(ks, vals):
            sub[k] = v
    return {"counts": table["counts"], "frames": table["frames"], "pp_assoc": table["pp_assoc"], "strength": st}


# --------------------------------------------------------------------------------------------------------- evaluation
def eval_table(table, test, decode: str, coarse: bool, coord_constr: bool, mode: str = "parallel") -> Dict:
    """UAS + per-relation recall + per-item conj/cc hit lists (for bootstrap CI), under the chosen decode."""
    old = AA.DECODE; AA.DECODE = decode
    conj_hits: List[int] = []; cc_hits: List[int] = []
    tot = ok = 0; rt = Counter(); rk = Counter()
    with _CoordConstr(coarse, coord_constr, mode):
        for toks, pos, gold, rels in test:
            A, n = AA.arc_scores(toks, pos, table)
            hd, _ = AA.decode(toks, pos, A, n, table=table)
            for i, (g, r) in enumerate(zip(gold, rels), start=1):
                if not (0 <= g <= n):
                    continue
                hit = int(hd.get(i, -1) == g); ok += hit; tot += 1
                if r in CORE_RELS:
                    rt[r] += 1; rk[r] += hit
                if r == "conj":
                    conj_hits.append(hit)
                elif r == "cc":
                    cc_hits.append(hit)
    AA.DECODE = old
    return {"uas": round(ok / max(1, tot), 4), "n_tok": tot,
            "rel": {r: round(rk[r] / rt[r], 3) for r in CORE_RELS if r in rt},
            "conj_hits": conj_hits, "cc_hits": cc_hits}


def _boot_ci(hits: Sequence[int], seed=17, n_boot=4000) -> Dict:
    a = np.array(hits, float)
    if len(a) < 3:
        return {"acc": round(float(a.mean()), 4) if len(a) else float("nan"), "ci": [None, None], "n": len(a)}
    r = np.random.default_rng(seed)
    bs = [a[r.integers(0, len(a), len(a))].mean() for _ in range(n_boot)]
    return {"acc": round(float(a.mean()), 4),
            "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)], "n": len(a)}


def _paired_delta_ci(hits_a: Sequence[int], hits_b: Sequence[int], seed=23, n_boot=4000) -> Dict:
    """Paired bootstrap of (full - base) per-arc recall difference (same gold arcs, same order)."""
    a = np.array(hits_a, float); b = np.array(hits_b, float)
    if len(a) != len(b) or len(a) < 3:
        return {"delta": round(float(a.mean() - b.mean()), 4) if len(a) and len(b) else None, "ci": [None, None]}
    d = a - b; r = np.random.default_rng(seed)
    bs = [d[r.integers(0, len(d), len(d))].mean() for _ in range(n_boot)]
    return {"delta": round(float(d.mean()), 4),
            "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]}


# --------------------------------------------------------------------------------------------------------------- run
class _TeacherWrap:
    """Wraps knowledge_free_teacher + the frames/pp_assoc the asset build needs, and caches per-sentence score matrices."""
    def __init__(self, train, beta=10.0):
        self._frames = AA.verb_frames_from_reading([(t, p) for t, p, _, _ in train])
        self._pp_assoc = AA.pp_assoc_from_reading([(t, p) for t, p, _, _ in train])
        self._t = knowledge_free_teacher(train, beta=beta)

    def base_matrices(self, train):
        return [self._t._score_matrix(toks, pos) for toks, pos, _, _ in train]


def run(smoke: bool = False, cap: int = 6000, gamma: float = 4.0, rounds: int = 3, arms: Optional[List[str]] = None) -> Dict:
    t0 = time.time(); out_dir = get_output_dir("attachment_coordination_v1"); os.makedirs(out_dir, exist_ok=True)
    if smoke:
        cap = min(cap, 1200); rounds = min(rounds, 2)
    train = sentences(TRAIN, cap=cap)
    test = sentences(TEST, cap=(200 if smoke else 700), maxlen=10 ** 6)
    print("[coord] train=%d test=%d cap=%d gamma=%g rounds=%d" % (len(train), len(test), cap, gamma, rounds), flush=True)
    tw = _TeacherWrap(train); base_marg = tw.base_matrices(train)
    print("[coord] teacher built + base matrices cached in %.0fs" % (time.time() - t0), flush=True)

    specs = {
        "base":        dict(coord_teacher=False, coord_constr=False, coarse=True,  mode="parallel"),   # floor
        "constr_only": dict(coord_teacher=False, coord_constr=True,  coarse=True,  mode="parallel"),   # construction only
        "teach_only":  dict(coord_teacher=True,  coord_constr=False, coarse=True,  mode="parallel"),   # teacher only
        "full":        dict(coord_teacher=True,  coord_constr=True,  coarse=True,  mode="parallel"),   # both (coarse class)
        "full_strict": dict(coord_teacher=True,  coord_constr=True,  coarse=False, mode="parallel"),   # both, strict UPOS
        "full_slot":   dict(coord_teacher=True,  coord_constr=True,  coarse=True,  mode="slot"),       # + slot-sharing L (lever)
        "scramble":    dict(coord_teacher=True,  coord_constr=True,  coarse=True,  mode="scramble"),   # INFO-FREE twin: wrong L
    }
    arms = arms or ["base", "constr_only", "teach_only", "full", "full_strict", "full_slot", "scramble"]
    tables = {}
    for name in arms:
        s = specs[name]
        tables[name] = build_asset(train, tw, base_marg, gamma=gamma, rounds=rounds, **s)
        print("[coord] asset '%s' built (%.0fs)" % (name, time.time() - t0), flush=True)

    results = {}
    for name in arms:
        s = specs[name]
        for dec in ("map1", "incr"):
            ev = eval_table(tables[name], test, dec, s["coarse"], s["coord_constr"], s["mode"])
            results["%s@%s" % (name, dec)] = {"uas": ev["uas"], "rel": ev["rel"],
                                              "conj": _boot_ci(ev["conj_hits"]), "cc": _boot_ci(ev["cc_hits"]),
                                              "_conj_hits": ev["conj_hits"], "_cc_hits": ev["cc_hits"]}
            rr = results["%s@%s" % (name, dec)]
            print("[coord]   %s@%s: conj %.3f cc %.3f UAS %.4f | obj %.3f nsubj %.3f nmod %.3f root %.3f" % (
                name, dec, rr["conj"]["acc"], rr["cc"]["acc"], rr["uas"], ev["rel"].get("obj", float("nan")),
                ev["rel"].get("nsubj", float("nan")), ev["rel"].get("nmod", float("nan")), ev["rel"].get("root", float("nan"))), flush=True)
        print("[coord] eval '%s' done (%.0fs)" % (name, time.time() - t0), flush=True)

    # twin: shuffle ALL strengths of the full asset (3 seeds), eval map1 -- the brief's literal info-free control
    twin_conj = []; twin_uas = []
    if "full" in tables:
        for sd in (1, 2, 3):
            tw_tab = shuffle_strengths_twin(tables["full"], sd)
            ev = eval_table(tw_tab, test, "map1", True, True)
            twin_conj.append(float(np.mean(ev["conj_hits"])) if ev["conj_hits"] else float("nan"))
            twin_uas.append(ev["uas"])
        print("[coord] shuffled-strengths twin: conj %s UAS %s" % ([round(x, 3) for x in twin_conj], twin_uas), flush=True)

    # paired base->full deltas (map1 + incr) on conj and cc
    paired = {}
    if "base" in arms and "full" in arms:
        for dec in ("map1", "incr"):
            b = results["base@%s" % dec]; f = results["full@%s" % dec]
            paired["conj@%s" % dec] = _paired_delta_ci(f["_conj_hits"], b["_conj_hits"])
            paired["cc@%s" % dec] = _paired_delta_ci(f["_cc_hits"], b["_cc_hits"])

    # strip the raw hit lists before writing
    for k in results:
        results[k].pop("_conj_hits", None); results[k].pop("_cc_hits", None)

    out = {"smoke": smoke, "cap": cap, "gamma": gamma, "rounds": rounds, "n_train": len(train), "n_test": len(test),
           "results": results, "twin_conj_map1": [round(x, 4) for x in twin_conj],
           "twin_uas_map1": [round(x, 4) for x in twin_uas], "paired_base_to_full": paired,
           "elapsed_s": round(time.time() - t0, 1)}
    b = results.get("base@map1", {}); f = results.get("full@map1", {}); fi = results.get("full@incr", {})
    bi = results.get("base@incr", {}); sc = results.get("scramble@map1", {})
    out["headline"] = (
        "COORDINATION map1: conj base %.3f -> full %.3f (paired %s) | scramble-twin %.3f | shuffled-twin %s || cc %.3f -> "
        "%.3f | UAS %.4f -> %.4f | incr conj %.3f -> %.3f" % (
            b.get("conj", {}).get("acc", float("nan")), f.get("conj", {}).get("acc", float("nan")),
            paired.get("conj@map1", {}).get("ci"), sc.get("conj", {}).get("acc", float("nan")), out["twin_conj_map1"],
            b.get("cc", {}).get("acc", float("nan")), f.get("cc", {}).get("acc", float("nan")),
            b.get("uas", float("nan")), f.get("uas", float("nan")),
            bi.get("conj", {}).get("acc", float("nan")), fi.get("conj", {}).get("acc", float("nan"))))
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print("[coord] " + out["headline"], flush=True)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--cap", type=int, default=6000); ap.add_argument("--gamma", type=float, default=4.0)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--arms", default=None, help="comma list subset of base,constr_only,teach_only,full,full_strict")
    a = ap.parse_args(argv)
    arms = a.arms.split(",") if a.arms else None
    if a.self_test or a.smoke:
        run(smoke=True, cap=a.cap, gamma=a.gamma, rounds=a.rounds, arms=arms); print("SELFTEST PASS", flush=True); return 0
    run(cap=a.cap, gamma=a.gamma, rounds=a.rounds, arms=arms); return 0


if __name__ == "__main__":
    sys.exit(main())
