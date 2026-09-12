"""SITUATION-MODEL BUILD (pri-1, strategy 2026-09-12): the FORWARD HALF -- entity TOKENS that accrue EVERY reference, and a
FOREGROUND window -- applied to the landed grammar resolver (affected_entity_resolver) on THIRD-person undergoer pronouns.

BRAIN (PINNED): an object/event file accrues every reference to its token (Kahneman-Treisman-Gibbs 1992 reviewing +
impletion; Hommel 2004): resolving a pronoun is itself a reference that raises the token's base-level activation
(ACT-R: every retrieval is a presentation). The situation model's foreground holds the entities situationally attached to
the current event (Glenberg-Meyer-Lindem 1987 availability; Zwaan-Radvansky event indexing); entities outside the current
event window are accessible only when nothing in focus qualifies.

WHAT CHANGES vs the landed resolver (byte-identical otherwise): (1) each pronoun mention in the document is resolved
INCREMENTALLY by the same resolver and its (time, role) is written to the picked entity's history -> later ACT-R
activations see the full reference history (the landed resolver sees only non-pronoun mentions); (2) candidates whose
last reference lies within W sentences of the pronoun are tried first (fallback: all). Operating point (clock, decay, W)
SWEPT, never adopted. Entities = the landed resolver's head-individuated buckets (the coref token question is its own
problem; this cell measures what the forward half buys on the incumbent's own tokens).

CONTROLS: ACCRUAL-SCRAMBLE twin (each pronoun is written to a RANDOM gn-compatible entity -> the accrual carries no
referent information); WINDOW-SCRAMBLE (the in-window set is a random same-size subset); ablations (accrual only,
window only); gold roles AND the predicted parse; paired 2000-draw bootstrap vs the incumbent on the same items.
NO gold in any decision (gold eid used only to score). Glass-box, no LLM. ASCII.
"""
from __future__ import annotations

import os
import random
import sys
from collections import defaultdict

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_affected_entity_salience_prior_gum_v1 as B1
import experiments.exp_affected_entity_binding_parallelism_gum_v1 as B4
import hdlab.affected_entity_resolver as AER
from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY
from hdlab.state_of_mind import PRONOUN_SCOPE

SEED = 20260912
THIRD_EXTRA = {"himself", "herself", "itself", "themselves"}
ROLE_OF_RANK = {0: "SUBJECT", 1: "OBJECT"}
WINDOW = 2          # sentences (swept: 1/2/3; 2 reported)


def is_third(text: str) -> bool:
    f = text.lower()
    return f in PRONOUN_SCOPE or f in THIRD_EXTRA


def _gn_ok(ug, un, g, n):
    if ug and g and ug != g:
        return False
    if un and n and un != n:
        return False
    return True


def load(predicted_parse=False, limit=None):
    import experiments.exp_hybrid_unified_incumbent_coref_gum_v1 as HYB
    docs = B1._load_test(limit)
    if predicted_parse:
        for doc in docs:
            B4._overlay_predicted(doc)
    out = []
    for doc in docs:
        mlive = HYB.gum_to_live(doc)
        for i, m in enumerate(mlive):
            m.setdefault("order", i)
        out.append((doc, mlive))
    return out


REFLEXIVE = {"himself", "herself", "itself", "themselves"}


def run_arm(data, *, accrue=True, window=WINDOW, clock="order", decay=DEFAULT_DECAY,
            scramble_accrual=False, scramble_window=False, rng=None, principle_a=False):
    """One configuration over all THIRD-person undergoer targets. Returns list of (hit, form).
    The LOAD-BEARING math is the organ: hdlab.affected_entity_resolver.EntityTokens (tokens, accrual, foreground,
    Principle A) -- this cell only feeds it the GUM mention stream and scores against gold. `clock` selects which
    time axis is fed as `order` (mention order / token position / sentence index); controls are applied by the cell
    around the organ call (scramble_accrual re-targets the accrual; scramble_window swaps the foreground set)."""
    rng = rng or random.Random(SEED)
    results = []
    for doc, mlive in data:
        head_to_mi = {doc.mentions[i].head_g: i for i in range(len(doc.mentions))}
        mi2headg = {i: doc.mentions[i].head_g for i in range(len(doc.mentions))}
        gidx2dep = {t.gidx: t.deprel for t in doc.toks}
        gidx2tok = {t.gidx: t for t in doc.toks}
        und = {}
        for t in doc.toks:
            if t.deprel in B1.UND_DEPRELS and t.gidx in head_to_mi and doc.mentions[head_to_mi[t.gidx]].mtype == "pronoun":
                und[head_to_mi[t.gidx]] = t
        T = AER.EntityTokens(window=None if scramble_window else window, decay=decay, accrue=accrue)
        for mi, m in enumerate(mlive):
            M = doc.mentions[mi]
            hg = mi2headg.get(mi); tk = gidx2tok.get(hg)
            t_tok = float(hg if hg is not None else m["order"]); t_sent = float(tk.sent if tk is not None else 0)
            tclock = {"order": float(m["order"]), "tokpos": t_tok, "sent": t_sent}[clock]
            role = ROLE_OF_RANK.get(m.get("sent_role_rank", 99), "OTHER")
            is_pron = m["is_pronoun"] or (M.mtype == "pronoun" and is_third(M.text))
            if not is_pron:
                T.observe(m["head"], tclock, role, t_sent, m.get("gender") or m.get("name_gender"), m.get("number"),
                          gidx2dep.get(hg, ""), payload=m)
                continue
            ug, un = m.get("gender"), m.get("number")
            coarg = None
            if mi in und:
                cg = AER.coarg_head_gidx(doc.toks, und[mi])
                if cg is not None and cg in head_to_mi and not mlive[head_to_mi[cg]]["is_pronoun"]:
                    coarg = mlive[head_to_mi[cg]]["head"]
            dep = gidx2dep.get(hg, "")
            a_role = AER.role_class(dep) if dep else "OBJ"
            reflexive = principle_a and M.text.lower() in REFLEXIVE
            if scramble_window and window is not None:
                # CONTROL: a random same-size "foreground" -- implemented by temporarily restricting the organ's tokens
                compat = T.candidates(ug, un); ents = list(compat)
                legal = AER.legal_candidates(ents, coarg) if ents else []
                k = sum(1 for h in legal if t_sent - T.last_ref_sent.get(h, -1e9) <= window)
                keep = set(rng.sample(legal, k)) if (0 < k < len(legal)) else set(legal)
                saved = T.mentions
                T.mentions = {h: ms for h, ms in saved.items() if h in keep} if keep else saved
                pick, n_c = T.resolve_pronoun(tclock, t_sent, gender=ug, number=un, a_role=a_role, role=role,
                                              coarg_key=coarg, reflexive=reflexive)
                T.mentions = saved
            else:
                pick, n_c = T.resolve_pronoun(tclock, t_sent, gender=ug, number=un, a_role=a_role, role=role,
                                              coarg_key=coarg, reflexive=reflexive)
            if mi in und and is_third(M.text):
                cm = [x for x in mlive if x["midx"] < mi and not x["is_pronoun"] and B1._gn_ok(m, x)]
                if len(cm) >= 2 and len(set(x["head"] for x in cm)) >= 2:
                    lm = T.last_mention(pick, ug, un) if pick is not None else None
                    # score: the token's last gn-compatible non-pronoun mention's gold cluster (gold used ONLY here)
                    hit = int(lm is not None and lm[6] is not None and lm[6]["cluster"] == M.eid)
                    results.append((hit, M.text.lower()))
            if pick is not None and scramble_accrual:
                # CONTROL: re-target the accrual to a RANDOM compatible token (the organ wrote it to `pick`; move it)
                ents = list(T.candidates(ug, un))
                if ents:
                    tgt = rng.choice(ents)
                    if tgt != pick:
                        rec = T.pron_hist[pick].pop()
                        T.pron_hist.setdefault(tgt, []).append(rec)
                        T.last_ref_sent[tgt] = t_sent
    return results


def run(predicted_parse=False, n_boot=2000, limit=None):
    data = load(predicted_parse, limit)
    base = run_arm(data, accrue=False, window=None)
    bvec = np.array([h for h, _ in base]); n = len(bvec)
    rng2 = np.random.default_rng(SEED)

    def paired(res):
        v = np.array([h for h, _ in res]); assert len(v) == n
        d = v.astype(float) - bvec
        boots = np.array([d[rng2.integers(0, n, n)].mean() for _ in range(n_boot)])
        return {"acc": round(float(v.mean()), 4), "delta": round(float(d.mean()), 4),
                "ci95": [round(float(np.percentile(boots, 2.5)), 4), round(float(np.percentile(boots, 97.5)), 4)],
                "ci_sep": bool(np.percentile(boots, 2.5) > 0 or np.percentile(boots, 97.5) < 0)}

    out = {"n_third_undergoers": n, "predicted_parse": predicted_parse, "incumbent_acc": round(float(bvec.mean()), 4)}
    out["accrual_only"] = paired(run_arm(data, accrue=True, window=None))
    out["window_only"] = paired(run_arm(data, accrue=False, window=WINDOW))
    out["accrual_plus_window"] = paired(run_arm(data, accrue=True, window=WINDOW))
    out["principle_a_only"] = paired(run_arm(data, accrue=False, window=None, principle_a=True))
    out["accrual_plus_window_plus_principle_a"] = paired(run_arm(data, accrue=True, window=WINDOW, principle_a=True))
    out["refl_n"] = sum(1 for _, f in run_arm(data, accrue=False, window=None) if f in REFLEXIVE)
    out["CONTROL_accrual_scrambled_plus_window"] = paired(run_arm(data, accrue=True, window=WINDOW, scramble_accrual=True, rng=random.Random(SEED)))
    out["CONTROL_window_scrambled_plus_accrual"] = paired(run_arm(data, accrue=True, window=WINDOW, scramble_window=True, rng=random.Random(SEED)))
    out["sweep_window"] = {w: paired(run_arm(data, accrue=True, window=w))["acc"] for w in (1, 2, 3, 5)}
    out["sweep_decay"] = {d: paired(run_arm(data, accrue=True, window=WINDOW, decay=d))["acc"] for d in (1.0, 1.5, 2.0, 3.0)}
    out["sweep_clock"] = {c: paired(run_arm(data, accrue=True, window=WINDOW, clock=c))["acc"] for c in ("order", "tokpos", "sent")}
    by_form = defaultdict(lambda: [0, 0])
    for (h, f), (hb, _) in zip(run_arm(data, accrue=True, window=WINDOW), base):
        by_form[f][0] += h; by_form[f][1] += 1
    out["by_form_accrual_plus_window"] = {f: [round(c / m, 3), m] for f, (c, m) in sorted(by_form.items(), key=lambda x: -x[1][1])[:8]}
    return out


def self_test():
    r = run()
    a = r["accrual_plus_window"]; c1 = r["CONTROL_accrual_scrambled_plus_window"]; c2 = r["CONTROL_window_scrambled_plus_accrual"]
    assert r["n_third_undergoers"] > 500
    assert a["ci_sep"] and a["delta"] > 0, f"forward half not CI-sep: {a}"
    assert c1["acc"] < a["acc"] and c2["acc"] < a["acc"], f"controls did not lose: {c1} {c2} vs {a}"
    print(f"[SELFTEST PASS] forward half (token accrual + foreground window) on THIRD-person undergoers n={r['n_third_undergoers']}: "
          f"incumbent {r['incumbent_acc']} -> {a['acc']} (+{a['delta']}, CI{a['ci95']}); accrual-only {r['accrual_only']['acc']}, "
          f"window-only {r['window_only']['acc']}; CONTROLS accrual-scrambled {c1['acc']}, window-scrambled {c2['acc']} (both lose).")
    return True


if __name__ == "__main__":
    if "--self-test" in sys.argv or "--smoke" in sys.argv:
        self_test()
    else:
        import pprint
        pprint.pprint(run(predicted_parse="--predicted" in sys.argv), width=120, sort_dicts=False)
