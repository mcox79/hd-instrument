"""exp_noncanonical_agent_bymorph_v1 -- the DEFINITIVE decomposition of the non-canonical who-did-what AGENT
residual, on the role-balanced comprehension gold read through the reader's OWN weak front-end (QA-SRL, modern,
NO age confound; data/exp_noncanonical_role_diagnostic_v1/aligned_gold.jsonl). AGENT detection: candidates =
clause nominals, correct iff the competition argmax token is in the gold AGENT span. Live baseline =
hdlab.graded_role_assigner.agent_supports (the landed AGENT_VALIDITIES competition, incl. structure cue).

TWO findings this cell establishes with controls, both brain-foundational (MacWhinney & Bates Competition Model:
role = graded cue competition weighted by CONDITIONAL validity):

  (A) LOCATED NEGATIVE -- a WHITENED grounded selectional-fit cue (agent-vs-patient prototype, verb-keyed +
      global backoff, self-gated by is_passive_clause) does NOT beat structure+animacy on non-canonical AGENT:
      it TIES its own info-free twins (scrambled-meaning, verb-shuffled). WHY (diagnosed): on ANIMATE-agent
      clauses the competition's ANIMACY cue already saturates (0.70); on INANIMATE-agent clauses the agent is an
      inanimate CAUSER ("formed by a natural process", "scratched by topaz") that matches no agent-prototype --
      the reliable signal there is the by-phrase MORPHOLOGY, not a semantic prototype. This confirms + extends
      grounded_role_assignment_via_verb_keyed_thematic_fit (noun-side signal near a modest ceiling; structure+
      animacy is the baseline to beat).

  (B) THE REAL FIX -- a by-phrase CASE-MORPHOLOGY cue (`byhead`: a candidate governed by the passive-agent
      preposition "by" through its NP, self-gated to passives) BEATS the live baseline CI-separated on BOTH
      animate AND inanimate agents. The landed `byagent` cue misses multi-word by-phrases (it checks only the
      token ADJACENT to the head), so "by a natural process" is instead PENALIZED by `core_arg` (PP-governed ->
      not-subject). `byhead` is the pinned high-validity Competition-Model CASE cue (Bates & MacWhinney: case
      marking is a top cue; "by" is the English morphological marker of the demoted passive agent). Info-free
      twin (by-membership shuffled across candidates) LOSES; canonical is self-gated OFF (no regress).

  (C) GROUNDED RESIDUAL -- with by-morphology handled, does grounded fit add on the by-LESS non-canonical
      residual (fronting/clefts/agentless, where "by" does not mark the agent)? Measured here.

NO hdlab write, NO gold roles in the grounded foundation, NO LLM. REUSES the live competition organs +
meaning_foundation whitening. ASCII. Writes only to data/exp_noncanonical_agent_bymorph_v1[/_smoke].
Run: .venv/Scripts/python.exe experiments/exp_noncanonical_agent_bymorph_v1.py [--smoke] [--self-test]
"""
from __future__ import annotations
import argparse, json, os, sys
from datetime import datetime, timezone

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

from hdlab.graded_role_assigner import agent_supports, is_passive_clause, AGENT_VALIDITIES
from hdlab.graded_competition import net_activation
from hdlab.animacy_lexicon import lookup_animacy
from hdlab.thematic_role_labeler import _is_participle, is_passive_predicate
import experiments.exp_grounded_selfit_role_cue_v1 as G   # reuse: load_rows, nominal_cands, harvest_protos, selfit_raw, whitening, _subj_before

NOMINAL = {"NOUN", "PROPN", "PRON"}
SEED = 20260905
N_BOOT = 2000
BY_SWEEP = [4.0, 6.0, 8.0, 10.0, 12.0]
SELFIT_W = 3.0
# NP-internal tokens we scan through leftward to find a governing "by" (the by-PP head can sit several tokens in)
_NP_SKIP = {"DET", "ADJ", "NUM", "PUNCT", "NOUN", "PROPN", "CCONJ"}
_NP_SKIP_LOW = {"'s", "the", "a", "an", "of"}


def span_set(g):
    if not g:
        return set()
    return set(range(g[0], g[1])) if (len(g) == 2 and g[1] > g[0]) else set(g)


def by_governs(low, pos, p, maxscan=8):
    """Is the nominal at 0-based p the object of the passive-agent preposition 'by'? Scan left through
    NP-internal modifiers + coordination; a 'by' before any clause-blocking token -> by-PP member (agent)."""
    j = p - 1
    for _ in range(maxscan):
        if j < 0:
            return False
        if low[j] == "by":
            return True
        u = pos[j] if j < len(pos) else None
        if u in _NP_SKIP or low[j] in _NP_SKIP_LOW:
            j -= 1
            continue
        return False
    return False


def _cands(toks, pos, v):
    return [i for i in range(len(pos)) if pos[i] in NOMINAL and i != v]


def passive_agent_gate(toks, pos, v, cands):
    """The by-agent CONSTRUCTION detector: a participle verb (V-en) with a by-PP among candidates -- the exact
    morphological signature of the demoted passive agent. Higher recall + precision than is_passive_clause on
    real by-passives (fires 62/90 real agent-post passives vs 58; 14/845 canonical false-fires vs 106). This is
    the UPSTREAM voice cue that gates byhead (Bates & MacWhinney: voice morphology + case are top cues)."""
    if not (0 <= v < len(toks)):
        return False
    low = [t.lower() for t in toks]
    if not any(by_governs(low, pos, i) for i in cands):
        return False
    # pri 111 (2026-09-14): the same construction-plus-voice repair the LANDED organ got
    # (hdlab.graded_role_assigner.participle_bypp_gate). The suffix test alone cannot see an irregular
    # participle that carries no -ed/-en, so `They are led BY head coach Monreal` never gated byhead here
    # and this copy fell back to word order and picked `They`. Fire on a by-governed NP plus EITHER the
    # organ's voice read (an auxiliary opened the passive expectation) OR participial morphology (the
    # REDUCED passive, which has no auxiliary at all -- there the by-phrase is the only confirmation there
    # is). A strict SUPERSET of the old gate. Restores per-row byte-faithfulness with the landed organ on
    # the QA-SRL clean agent-post (n=90) and full non-canonical (n=201) slices.
    if is_passive_predicate(toks, pos, v + 1):
        return True
    return _is_participle(toks[v], pos[v] if v < len(pos) else None)


def pick(toks, pos, v, cands, subj_before, *, byhead_w=0.0, selfit=None, selfit_w=0.0,
         byhead_twin_seed=None, byhead_gate=None):
    """The live AGENT competition, optionally + byhead (case morphology) and/or + selfit (grounded). byhead is
    self-gated by `byhead_gate` (default: the participle+by-PP passive-agent construction detector); selfit is
    self-gated by is_passive_clause. selfit = (meaning, protos). Returns the 0-based winner token index."""
    if not cands:
        return None
    gate = byhead_gate if byhead_gate is not None else passive_agent_gate
    c = [(i, toks[i].lower(), None, i) for i in cands]
    S = agent_supports(toks, pos, v, c, gaz=None, cluster_freq=None, subj_before=subj_before)
    w = dict(AGENT_VALIDITIES)
    low = [t.lower() for t in toks]
    if byhead_w > 0.0 and gate(toks, pos, v, cands):
        bh = [1.0 if by_governs(low, pos, i) else 0.0 for i in cands]
        if byhead_twin_seed is not None:                       # info-free twin: shuffle by-membership
            rng = np.random.default_rng(byhead_twin_seed + v + len(cands))
            bh = list(np.asarray(bh)[rng.permutation(len(bh))])
        S["byhead"] = bh
        w["byhead"] = byhead_w
    if selfit is not None and selfit_w > 0.0 and is_passive_clause(toks, pos):
        meaning, protos = selfit
        raw = np.array([G.selfit_raw(toks[i].lower(), toks[v].lower(), meaning, protos) for i in cands])
        sd = raw.std()
        S["selfit"] = list((raw - raw.mean()) / sd if sd > 1e-9 else np.zeros_like(raw))
        w["selfit"] = selfit_w
    A = net_activation(S, w)
    return c[int(np.argmax(A))][0]


def positional(r, toks, pos, v, cands):
    pre = [i for i in cands if i < v]
    return pre[-1] if pre else (cands[0] if cands else None)


def _score(rows, pickfn):
    out = []
    for r in rows:
        toks, pos, v = r["toks"], r["pos"], r["verb_idx"]
        gold = span_set(r["agent"])
        if not gold or not (0 <= v < len(toks)):
            continue
        cands = _cands(toks, pos, v)
        pk = pickfn(r, toks, pos, v, cands)
        out.append(int(pk is not None and pk in gold))
    return np.array(out, float)


def _boot(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); n = len(a)
    if n == 0:
        return {"delta": 0.0, "lo": 0.0, "hi": 0.0, "hw": 0.0, "sep": False, "n": 0}
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, (N_BOOT, n))
    d = a[idx].mean(1) - b[idx].mean(1)
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    return {"delta": round(float(a.mean() - b.mean()), 4), "lo": round(lo, 4), "hi": round(hi, 4),
            "hw": round((hi - lo) / 2, 4), "sep": bool(lo > 0), "n": int(n)}


def _agent_head(r):
    g = sorted(span_set(r["agent"]))
    for i in reversed(g):
        if i < len(r["pos"]) and r["pos"][i] in NOMINAL:
            return i
    return g[-1] if g else None


def _agent_animate(r):
    h = _agent_head(r)
    if h is None:
        return None
    a = lookup_animacy(r["toks"][h].lower(), r["pos"][h])
    if a and a.get("animacy") == "animate":
        return True
    if a and a.get("animacy") == "inanimate":
        return False
    w = r["toks"][h].lower()
    if w in ("he", "she", "they", "him", "her", "them", "we", "us"):
        return True
    if r["pos"][h] == "PROPN":
        return True
    return None


def _has_by(r):
    low = [t.lower() for t in r["toks"]]
    v = r["verb_idx"]
    return any(by_governs(low, r["pos"], i) for i in _cands(r["toks"], r["pos"], v))


def run(smoke=False):
    rows = [r for r in G.load_rows() if r.get("agent")]
    if smoke:
        rows = rows[:600]
    key = [tuple(r["toks"]) for r in rows]
    uniq = sorted(set(key))
    rng = np.random.default_rng(SEED)
    perm = rng.permutation(len(uniq))
    tr_sents = {uniq[i] for i in perm[: int(0.7 * len(uniq))]}
    train = [r for r, k in zip(rows, key) if k in tr_sents]
    test = [r for r, k in zip(rows, key) if k not in tr_sents]

    allwords = [t for r in rows for t in r["toks"]]
    gm = G.GroundedMeaning()
    wm = G.WhitenedMeaning(gm, allwords, npc=3)
    gm_scr = G.GroundedMeaning(scramble_seed=31); gm_scr.install_scramble(allwords)
    wm_scr = G.WhitenedMeaning(gm_scr, allwords, npc=3)
    protos_w = G.harvest_protos(train, wm)
    protos_scr = G.harvest_protos(train, wm_scr)
    protos_vshuf = G.harvest_protos(train, wm, verb_shuffle_seed=7)

    subj_cache = {}
    def subj(toks, pos):
        k = tuple(toks)
        if k not in subj_cache:
            subj_cache[k] = G._subj_before(toks, pos)
        return subj_cache[k]

    base = lambda r, t, p, v, c: pick(t, p, v, c, subj(t, p))
    def byhead(w):
        return lambda r, t, p, v, c: pick(t, p, v, c, subj(t, p), byhead_w=w)
    byhead_twin = lambda w: (lambda r, t, p, v, c: pick(t, p, v, c, subj(t, p), byhead_w=w, byhead_twin_seed=13))
    selfit = lambda mp, w=SELFIT_W: (lambda r, t, p, v, c: pick(t, p, v, c, subj(t, p), selfit=mp, selfit_w=w))
    both = lambda w: (lambda r, t, p, v, c: pick(t, p, v, c, subj(t, p), byhead_w=w, selfit=(wm, protos_w), selfit_w=SELFIT_W))

    nc = lambda rs: [r for r in rs if r.get("voice") == "passive"]
    cn = lambda rs: [r for r in rs if r.get("voice") == "active"]

    # --- sweep byhead weight on TRAIN non-canonical ---
    tr_nc = nc(train)
    b_tr = _score(tr_nc, base)
    sweep = {w: round(float(_score(tr_nc, byhead(w)).mean() - b_tr.mean()), 4) for w in BY_SWEEP}
    best_bw = max(BY_SWEEP, key=lambda w: sweep[w])

    te_nc = nc(test); te_cn = cn(test)
    res = {"n_train": len(train), "n_test": len(test), "best_byhead_w": best_bw, "byhead_sweep_train": sweep,
           "selfit_w": SELFIT_W, "smoke": smoke}

    def acc(v):
        return round(float(v.mean()), 4) if len(v) else 0.0

    # ===== (B) THE FIX: byhead on non-canonical, by domain =====
    animate = [r for r in te_nc if _agent_animate(r) is True]
    inanim = [r for r in te_nc if _agent_animate(r) is False]
    bres = {}
    for name, rs in (("non_canonical_ALL", te_nc), ("animate_agent", animate), ("inanimate_agent", inanim)):
        b = _score(rs, base); h = _score(rs, byhead(best_bw)); tw = _score(rs, byhead_twin(best_bw))
        p = _score(rs, positional)
        bres[name] = {"n": len(rs), "positional": acc(p), "baseline": acc(b), "byhead": acc(h),
                      "byhead_twin": acc(tw),
                      "byhead_vs_baseline": _boot(h, b), "byhead_vs_twin": _boot(h, tw)}
    res["byhead_fix"] = bres

    # canonical no-regress (self-gated OFF -> paired boot must not CI-regress; report detector false-fire)
    b_cn = _score(te_cn, base); h_cn = _score(te_cn, byhead(best_bw))
    ff = float(np.mean([is_passive_clause(r["toks"], r["pos"]) for r in te_cn])) if te_cn else 0.0
    res["canonical_noregress"] = {"n": len(te_cn), "baseline": acc(b_cn), "byhead": acc(h_cn),
                                  "byte_identical": bool(np.array_equal(b_cn, h_cn)),
                                  "detector_falsefire_rate": round(ff, 4),
                                  "byhead_vs_baseline": _boot(h_cn, b_cn)}

    # ===== (A) LOCATED NEGATIVE: grounded selfit ties its twins on non-canonical =====
    b = _score(te_nc, base)
    sf = _score(te_nc, selfit((wm, protos_w)))
    sf_scr = _score(te_nc, selfit((wm_scr, protos_scr)))
    sf_vs = _score(te_nc, selfit((wm, protos_vshuf)))
    res["grounded_selfit_negative"] = {
        "n": len(te_nc), "baseline": acc(b), "selfit": acc(sf), "twin_scrambled_meaning": acc(sf_scr),
        "twin_verb_shuffled": acc(sf_vs),
        "selfit_vs_baseline": _boot(sf, b), "selfit_vs_twin_scrambled": _boot(sf, sf_scr),
        "selfit_vs_twin_vshuffled": _boot(sf, sf_vs)}

    # ===== (C) GROUNDED RESIDUAL: by-LESS non-canonical, does selfit add on top of byhead? =====
    byless = [r for r in te_nc if not _has_by(r)]
    bypres = [r for r in te_nc if _has_by(r)]
    # recoverability: is the gold agent among candidates on by-less rows?
    def recoverable(r):
        v = r["verb_idx"]; g = span_set(r["agent"]); c = set(_cands(r["toks"], r["pos"], v))
        return bool(g & c)
    rec_byless = sum(recoverable(r) for r in byless)
    hh = _score(byless, byhead(best_bw))
    hs = _score(byless, both(best_bw))
    res["grounded_residual_byless"] = {
        "n_byless": len(byless), "n_bypresent": len(bypres), "recoverable_byless": int(rec_byless),
        "byhead": acc(hh), "byhead_plus_selfit": acc(hs), "selfit_adds_vs_byhead": _boot(hs, hh)}

    # ===== CLEAN non-canonical slice: gold agent entirely POST-verbal (positional NECESSARILY wrong) =====
    def agent_post(r):
        v = r["verb_idx"]; g = span_set(r["agent"])
        return bool(g) and all(i > v for i in g)
    te_ap = [r for r in test if agent_post(r)]
    ap_base = _score(te_ap, base)
    ap_bh = _score(te_ap, byhead(best_bw))
    ap_tw = _score(te_ap, byhead_twin(best_bw))
    ap_sf = _score(te_ap, selfit((wm, protos_w)))
    ap_pos = _score(te_ap, positional)
    res["clean_agent_post"] = {"n": len(te_ap), "positional": acc(ap_pos), "baseline": acc(ap_base),
                               "byhead": acc(ap_bh), "byhead_twin": acc(ap_tw), "selfit": acc(ap_sf),
                               "byhead_vs_baseline": _boot(ap_bh, ap_base), "byhead_vs_twin": _boot(ap_bh, ap_tw),
                               "selfit_vs_baseline": _boot(ap_sf, ap_base)}

    # ===== UPSTREAM: the construction gate (participle+by-PP) vs is_passive_clause, on the clean slice =====
    isp_gate = lambda toks, pos, v, cands: is_passive_clause(toks, pos)
    def byhead_g(w, gate):
        return lambda r, t, p, v, c: pick(t, p, v, c, subj(t, p), byhead_w=w, byhead_gate=gate)
    gate_cmp = {}
    for gname, gfn in (("participle_byPP", passive_agent_gate), ("is_passive_clause", isp_gate)):
        fire_ap = sum(gfn(r["toks"], r["pos"], r["verb_idx"], _cands(r["toks"], r["pos"], r["verb_idx"])) for r in te_ap)
        fire_cn = sum(gfn(r["toks"], r["pos"], r["verb_idx"], _cands(r["toks"], r["pos"], r["verb_idx"])) for r in te_cn)
        ap = _score(te_ap, byhead_g(best_bw, gfn)); cn = _score(te_cn, byhead_g(best_bw, gfn))
        gate_cmp[gname] = {"fire_agent_post": int(fire_ap), "fire_canonical_falsefire": int(fire_cn),
                           "agent_post_acc": acc(ap), "agent_post_vs_baseline": _boot(ap, ap_base),
                           "canonical_acc": acc(cn), "canonical_minus_baseline": round(float(cn.mean() - b_cn.mean()), 4)}
    res["upstream_gate_comparison"] = gate_cmp

    # ===== ALL non-canonical: best combined vs baseline =====
    b = _score(te_nc, base); combo = _score(te_nc, both(best_bw))
    res["combined_vs_baseline_nc"] = _boot(combo, b)
    res["combined_acc"] = acc(combo)

    res["verdict"] = {
        "byhead_beats_baseline_nc_CIsep": res["byhead_fix"]["non_canonical_ALL"]["byhead_vs_baseline"]["sep"],
        "byhead_beats_twin_CIsep": res["byhead_fix"]["non_canonical_ALL"]["byhead_vs_twin"]["sep"],
        "byhead_beats_baseline_cleanslice_CIsep": res["clean_agent_post"]["byhead_vs_baseline"]["sep"],
        "byhead_beats_twin_cleanslice_CIsep": res["clean_agent_post"]["byhead_vs_twin"]["sep"],
        "byhead_helps_inanimate_CIsep": res["byhead_fix"]["inanimate_agent"]["byhead_vs_baseline"]["sep"],
        "byhead_no_canonical_regress": not (res["canonical_noregress"]["byhead_vs_baseline"]["hi"] < -0.005),
        "construction_gate_beats_is_passive": (gate_cmp["participle_byPP"]["fire_canonical_falsefire"]
                                               < gate_cmp["is_passive_clause"]["fire_canonical_falsefire"]),
        "grounded_selfit_ties_twin (LOCATED NEG)": not res["grounded_selfit_negative"]["selfit_vs_twin_scrambled"]["sep"],
        "grounded_adds_on_byless_residual": res["grounded_residual_byless"]["selfit_adds_vs_byhead"]["sep"],
    }
    res["PASS_byhead_solves_real_problem"] = bool(res["verdict"]["byhead_beats_baseline_cleanslice_CIsep"]
                                                  and res["verdict"]["byhead_beats_twin_cleanslice_CIsep"]
                                                  and res["verdict"]["byhead_no_canonical_regress"])
    res["PASS_grounded_located_negative"] = bool(res["verdict"]["grounded_selfit_ties_twin (LOCATED NEG)"])
    return res


def self_test():
    m = run(smoke=True)
    assert m["byhead_fix"]["non_canonical_ALL"]["n"] > 20, m["byhead_fix"]["non_canonical_ALL"]["n"]
    print("SELF-TEST PASS", json.dumps(m["verdict"]))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", dest="selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return self_test()
    m = run(smoke=a.smoke)
    from experiments._seed_checkpoint import get_output_dir   # Q115: re-runnable output path (HDLAB_EXP_NAME-driven; --smoke isolated by the helper)
    outd = str(get_output_dir("noncanonical_agent_bymorph_v1"))
    os.makedirs(outd, exist_ok=True)
    m["ts_iso"] = datetime.now(timezone.utc).isoformat()
    with open(os.path.join(outd, "metrics.json"), "w", encoding="ascii") as f:
        json.dump(m, f, indent=2, default=str)
    print("=" * 98)
    print("NON-CANONICAL AGENT: by-morphology fix vs grounded located-negative  (best byhead_w=%s)" % m["best_byhead_w"])
    print("=" * 98)
    print("(B) THE FIX -- byhead (case morphology) beats the live baseline on non-canonical AGENT:")
    for k, d in m["byhead_fix"].items():
        print("  %-20s n=%-4d positional %.4f  baseline %.4f  +byhead %.4f  vs_base %s  vs_twin %s"
              % (k, d["n"], d["positional"], d["baseline"], d["byhead"], d["byhead_vs_baseline"], d["byhead_vs_twin"]))
    cr = m["canonical_noregress"]
    print("  canonical no-regress n=%d baseline %.4f byhead %.4f detector_falsefire %.3f vs_base %s"
          % (cr["n"], cr["baseline"], cr["byhead"], cr["detector_falsefire_rate"], cr["byhead_vs_baseline"]))
    print("\n(A) LOCATED NEGATIVE -- grounded selfit ties its info-free twins on non-canonical:")
    g = m["grounded_selfit_negative"]
    print("  baseline %.4f  selfit %.4f  twin_scrambled %.4f  twin_vshuf %.4f"
          % (g["baseline"], g["selfit"], g["twin_scrambled_meaning"], g["twin_verb_shuffled"]))
    print("  selfit_vs_baseline %s | vs_twin_scrambled %s" % (g["selfit_vs_baseline"], g["selfit_vs_twin_scrambled"]))
    r = m["grounded_residual_byless"]
    print("\n(C) GROUNDED RESIDUAL (by-less non-canonical n=%d, recoverable=%d): byhead %.4f +selfit %.4f  adds %s"
          % (r["n_byless"], r["recoverable_byless"], r["byhead"], r["byhead_plus_selfit"], r["selfit_adds_vs_byhead"]))
    ap = m["clean_agent_post"]
    print("\nCLEAN non-canonical slice (gold agent POST-verbal, positional necessarily wrong) n=%d:" % ap["n"])
    print("  positional %.4f | baseline %.4f | +byhead %.4f | +selfit %.4f"
          % (ap["positional"], ap["baseline"], ap["byhead"], ap["selfit"]))
    print("  byhead vs baseline %s | vs twin %s | selfit vs baseline %s"
          % (ap["byhead_vs_baseline"], ap["byhead_vs_twin"], ap["selfit_vs_baseline"]))
    print("\nUPSTREAM gate (byhead coverage/precision), clean slice + canonical:")
    for gn, gd in m["upstream_gate_comparison"].items():
        print("  %-18s fire_ap=%d fire_cn(falsefire)=%d | agent-post %.4f %s | canonical d=%+.4f"
              % (gn, gd["fire_agent_post"], gd["fire_canonical_falsefire"], gd["agent_post_acc"],
                 gd["agent_post_vs_baseline"], gd["canonical_minus_baseline"]))
    print("\ncombined (byhead+selfit) vs baseline on non-canonical: %s (acc %.4f)"
          % (m["combined_vs_baseline_nc"], m["combined_acc"]))
    print("\nVERDICT:", json.dumps(m["verdict"], indent=2))
    print("PASS byhead solves real problem:", m["PASS_byhead_solves_real_problem"],
          "| grounded located-negative:", m["PASS_grounded_located_negative"])
    print("wrote", os.path.join(outd, "metrics.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
