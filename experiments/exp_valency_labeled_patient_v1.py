"""exp_valency_labeled_patient_v1 -- brain-faithful who-did-what PATIENT readout off the parse:
the verb's LABELED object relation + correct VOICE remapping + VALENCY-gated binding.

THE GAP (parent SOLVED `consume_the_graded_pos_posterior_...`): the structure-first patient reads the
verb's object off the parse by POSITION (nearest post-verbal nominal dependent) with a lossy voice
detector; live 0.735 vs a gold-parse ceiling 0.913 on clean UD-EWT. This session's decomposition of that
gap (scratch probes, reproduced here) localizes it to THREE brain-faithful readout stages, NOT raw UAS
(swapping arc_parser->arceager, 0.79->0.842 UAS, does not move who-did-what -- head-independent):
  VOICE   +0.057  robust_passive (acc 0.905, 9.2% false-passive on actives) -> precise_passive (acc 0.982)
  LABEL   +0.024  position pick -> the verb's obj / nsubj:pass -LABELED dependent (grammatical function)
  HEAD    +0.062  our heads -> gold heads (the residual; genuine attachment, register-general negative)

THE BRAIN'S MECHANISM (PINNED): core roles are read off GRAMMATICAL RELATIONS (subj/obj) bound into the
verb's VALENCY slots by unification (Hagoort MUC: verb frames in temporal cortex, unification in LIFG;
Levin/Rappaport-Hovav linking rules), with a VOICE remapping (passive: subject->patient, by-phrase->agent
-- the Stage-4 algorithmic override). This is a LABELED, verb-centric attachment + voice linking rule,
NOT position. This cell reads the patient that way and measures the ladder on BOTH parsers, with a
cluster-bootstrap CI, info-free TWINS (shuffled voice / shuffled labels / shuffled heads), and the gold
ceiling. Register-general by construction: voice morphology + grammatical-function labels + verb valency
are stable across registers (measured 19c in exp_valency_labeled_patient_19c_v1).

Glass-box, NO external LLM, NO trained-modern-only-parser dependence for the WIN (the win is voice+label
readout, head-independent). hdlab READ-only. ASCII. own dir.
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import argparse, json, time
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.pos_tagger import PosTagger
from hdlab.graded_role_assigner import robust_passive
from hdlab.relcl_resolver import precise_passive
from hdlab.arc_labeler import ArcLabeler, norm_label
from hdlab.arc_parser import ArcParser
from hdlab.thematic_role_labeler import lemma_verb, is_strictly_intransitive
from hdlab.verb_subcat import suppress_patient
from hdlab.predicate_argument_frontend import structural_patient_pick
from hdlab.graded_role_assigner import hybrid_role_patient
from hdlab.relcl_resolver import _cands
import experiments.exp_whodidwhat_ud_structural_v1 as UD

POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
LAB_ASSET = os.path.join(_REPO, "data/frontend_assets/arc_labeler_hashed_ud_ewt.json")
ARC_ASSET = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
UD_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
UD_TRAIN = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-train.conllu")
from experiments._seed_checkpoint import get_output_dir  # Q115 (owner 2026-08-23): route the output dir
OUT_DIR = str(get_output_dir("valency_labeled_patient_v1"))
NOMINAL = {"NOUN", "PROPN", "PRON"}


def _deployed_structural_patient_pick(tokens, pos, heads, v, cands=None, np_head_reduce=False):
    """FROZEN pre-upgrade deployed structural_patient_pick (position + robust_passive + coordination-share +
    hybrid fallback) -- the R0_landed floor. PINNED here (2026-09-04) because the labeled readout was landed
    INTO hdlab.predicate_argument_frontend.structural_patient_pick (Q111 diff 2), so importing that name now
    returns the IMPROVED pick; R0_landed must keep measuring the historical DEPLOYED floor (0.745) it always
    did. Byte-identical to the pre-landing body: structural_roles(...)['patient'] (robust_passive voice, verb
    nominal-deps by position, _shared_object coordination borrow) then the hybrid_role_patient fallback."""
    from hdlab.predicate_argument_frontend import _verb_nom_deps, _shared_object
    n = len(tokens)
    is_passive = robust_passive(tokens, pos, v)
    nom = _verb_nom_deps(pos, heads, v, n)
    pre = [c for c in nom if c < v]; post = [c for c in nom if c > v]
    if is_passive:
        patient = pre[-1] if pre else (post[0] if post else None)
    else:
        patient = post[0] if post else None
    if patient is None:
        patient = _shared_object(tokens, pos, heads, v, n)
    if patient is not None:
        return patient
    if cands is None:
        cands = _cands(pos)
    return hybrid_role_patient(tokens, pos, v, cands=cands, np_head_reduce=np_head_reduce)


def _transitive(lemma):
    """valency: does the verb expect a direct object? (glass-box subcat signal)."""
    return not is_strictly_intransitive(lemma) and not suppress_patient(lemma, 0.35)


def position_pick(toks, pos, v, heads, is_passive):
    """the CURRENT readout: nearest post-verbal (active) / pre-verbal (passive) NOMINAL dependent."""
    n = len(toks)
    deps = [c for c in range(1, n + 1) if heads.get(c) == v and pos[c - 1] in NOMINAL]
    pre = [c for c in deps if c < v]; post = [c for c in deps if c > v]
    if is_passive:
        return pre[-1] if pre else (post[0] if post else None)
    return post[0] if post else (pre[-1] if pre else None)


def labeled_pick(toks, pos, v, heads, labels, is_passive, valency=False):
    """BRAIN-FAITHFUL: fill the verb's obj (active) / nsubj:pass (passive) LABELED slot; if the parse
    labeled no such dependent, valency-gated bind the nearest non-PP nominal on the expected side when the
    verb's frame expects an argument (unification into the open slot). Falls back to position otherwise."""
    n = len(toks)
    deps = [c for c in range(1, n + 1) if heads.get(c) == v and pos[c - 1] in NOMINAL]
    want = "nsubj:pass" if is_passive else "obj"
    lab = [c for c in deps if labels.get(c) == want]
    if lab:
        side = [c for c in lab if (c < v if is_passive else c > v)]
        if side:
            return side[-1] if is_passive else side[0]
        return lab[-1] if is_passive else lab[0]
    if valency:
        lemma = lemma_verb(toks[v - 1])
        if is_passive:
            for c in range(v - 1, 0, -1):
                if pos[c - 1] in NOMINAL and not (c - 2 >= 0 and pos[c - 2] == "ADP"):
                    return c
        elif _transitive(lemma):
            for c in range(v + 1, n + 1):
                if pos[c - 1] in NOMINAL and not (c - 2 >= 0 and pos[c - 2] == "ADP"):
                    return c
        else:
            return None                      # intransitive frame -> no object bound
    return position_pick(toks, pos, v, heads, is_passive)


def _boot_ci(per_sent_hits, nboot=2000, seed=17):
    """cluster bootstrap over sentences. per_sent_hits: list of lists of 0/1. Returns (mean, half_width)."""
    flat = [h for s in per_sent_hits for h in s]
    if not flat:
        return None, None
    mean = float(np.mean(flat))
    rng = np.random.default_rng(seed)
    idx = np.arange(len(per_sent_hits))
    means = []
    sizes = np.array([len(s) for s in per_sent_hits])
    sums = np.array([sum(s) for s in per_sent_hits])
    tot = sizes.sum()
    for _ in range(nboot):
        pick = rng.integers(0, len(per_sent_hits), len(per_sent_hits))
        m = sums[pick].sum() / max(1, sizes[pick].sum())
        means.append(m)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return round(mean, 4), round(float(hi - lo) / 2, 4)


def _paired_ci(per_sent_a, per_sent_b, nboot=2000, seed=23):
    """cluster-bootstrap CI of the paired difference mean(a)-mean(b) over shared sentences."""
    sizes = np.array([len(s) for s in per_sent_a])
    suma = np.array([sum(s) for s in per_sent_a]); sumb = np.array([sum(s) for s in per_sent_b])
    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(nboot):
        pick = rng.integers(0, len(per_sent_a), len(per_sent_a))
        n = max(1, sizes[pick].sum())
        diffs.append(suma[pick].sum() / n - sumb[pick].sum() / n)
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    obs = (suma.sum() - sumb.sum()) / max(1, sizes.sum())
    return round(float(obs), 4), round(float(lo), 4), round(float(hi), 4)


def eval_split(sents, tagger, labeler, arc, arceager_W, seed=0):
    """Per-sentence hit lists for every route + parser. Returns {route: [[hits per sent], ...]}."""
    from hdlab.arceager_parser import parse_with_conf
    routes = ["R0_landed", "R0_live_pos_rp", "R1_voice", "R2_label", "R3_valency", "R_final",
              "twin_shufvoice", "twin_shuflabel", "twin_shufheads",
              "ceiling_gold"]
    parsers = ["arc", "arceager"]
    H = {p: {r: [] for r in routes} for p in parsers}
    rng = np.random.default_rng(seed)
    for s in sents:
        toks = [t["form"] for t in s]; pos_g = [t["upos"] for t in s]
        gh = {t["id"]: t["head"] for t in s}
        glab = {t["id"]: norm_label(t["deprel"]) for t in s}
        pos = tagger.tag(list(toks))
        heads_by = {}
        from hdlab import frontend as _FE   # ONE shared frontend (2026-09-12): the organ switches reach this arm
        if _FE.HEADS_SOURCE == "attachment_arm":
            try:
                _tp = tagger.tag_with_posterior(list(toks))[1] if hasattr(tagger, "tag_with_posterior") else None
                _h = _FE.parser().parse(toks, pos, _tp).heads
            except Exception:
                _h = {}
            heads_by["arc"] = dict(_h); heads_by["arceager"] = dict(_h)   # the BF heads rung for BOTH routes
        else:
            try:
                heads_by["arc"] = arc.parse(toks, pos).heads
            except Exception:
                heads_by["arc"] = {}
            try:
                heads_by["arceager"] = parse_with_conf(toks, pos, arceager_W)[0]
            except Exception:
                heads_by["arceager"] = {}
        # gold items in THIS sentence
        gold = []
        for t in s:
            if t["upos"] != "VERB":
                continue
            v = t["id"]; deps = [d for d in s if d["head"] == v]
            passive = any(d["deprel"].startswith("nsubj:pass") or d["deprel"].startswith("aux:pass") for d in deps)
            pat = None
            for d in deps:
                if not passive and d["dep"] == "obj":
                    pat = d["id"]; break
                if passive and d["deprel"].startswith("nsubj:pass"):
                    pat = d["id"]; break
            if pat is not None:
                gold.append((v, pat, passive))
        if not gold:
            continue
        for p in parsers:
            oh = heads_by[p]
            olab = labeler.label(toks, pos, oh)
            # info-free twins: shuffle labels (permute values) / shuffle heads (random verb head)
            lab_vals = list(olab.values()); rng.shuffle(lab_vals)
            shuflab = {k: lab_vals[i] for i, k in enumerate(olab.keys())}
            verbs = [i for i in range(1, len(toks) + 1) if pos[i - 1] == "VERB"] or [0]
            shufheads = {c: (int(rng.choice(verbs)) if pos[c - 1] in NOMINAL else oh.get(c, 0))
                         for c in range(1, len(toks) + 1)}
            row = {r: [] for r in routes}
            for (v, pat, passive) in gold:
                rp = robust_passive(toks, pos, v); pp = precise_passive(toks, pos, v)
                shufv = bool(rng.integers(0, 2))
                # exact deployed baseline + the improved drop-in (both with the net-safe hybrid fallback)
                row["R0_landed"].append(int(_deployed_structural_patient_pick(toks, pos, oh, v) == pat))
                fin = labeled_pick(toks, pos, v, oh, olab, pp, valency=True)
                if fin is None:
                    fin = hybrid_role_patient(toks, pos, v, cands=_cands(pos))
                row["R_final"].append(int(fin == pat))
                row["R0_live_pos_rp"].append(int(position_pick(toks, pos, v, oh, rp) == pat))
                row["R1_voice"].append(int(position_pick(toks, pos, v, oh, pp) == pat))
                row["R2_label"].append(int(labeled_pick(toks, pos, v, oh, olab, pp, valency=False) == pat))
                row["R3_valency"].append(int(labeled_pick(toks, pos, v, oh, olab, pp, valency=True) == pat))
                row["twin_shufvoice"].append(int(position_pick(toks, pos, v, oh, shufv) == pat))
                row["twin_shuflabel"].append(int(labeled_pick(toks, pos, v, oh, shuflab, pp, valency=False) == pat))
                row["twin_shufheads"].append(int(labeled_pick(toks, pos, v, shufheads, olab, pp, valency=True) == pat))
                row["ceiling_gold"].append(int(labeled_pick(toks, pos_g, v, gh, glab, passive, valency=True) == pat))
            for r in routes:
                H[p][r].append(row[r])
    return H, routes, parsers


def summarize(H, routes, parsers):
    out = {}
    for p in parsers:
        acc = {}
        for r in routes:
            m, hw = _boot_ci(H[p][r])
            acc[r] = {"acc": m, "ci_hw": hw, "n": sum(len(x) for x in H[p][r])}
        # paired deltas vs R0 and vs twins
        d = {}
        d["Rfinal_vs_landed"] = _paired_ci(H[p]["R_final"], H[p]["R0_landed"])
        d["R3_vs_R0"] = _paired_ci(H[p]["R3_valency"], H[p]["R0_live_pos_rp"])
        d["R1_vs_R0"] = _paired_ci(H[p]["R1_voice"], H[p]["R0_live_pos_rp"])
        d["R3_vs_twin_shufheads"] = _paired_ci(H[p]["R3_valency"], H[p]["twin_shufheads"])
        d["R1_vs_twin_shufvoice"] = _paired_ci(H[p]["R1_voice"], H[p]["twin_shufvoice"])
        d["R2_vs_twin_shuflabel"] = _paired_ci(H[p]["R2_label"], H[p]["twin_shuflabel"])
        out[p] = {"acc": acc, "paired": d}
    return out


def run(smoke=False):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tagger = PosTagger.load(POS_ASSET)
    labeler = ArcLabeler.load(LAB_ASSET)
    arc = ArcParser.load(ARC_ASSET)
    from hdlab.arceager_parser import load_model, MODEL_PATH
    aeW = load_model(MODEL_PATH)
    res = {}
    for split, path, cap in (("TEST", UD_TEST, 120 if smoke else None),
                             ("TRAIN", UD_TRAIN, 120 if smoke else 1500)):
        sents = UD.load_ud(path)
        if cap:
            sents = sents[:cap]
        H, routes, parsers = eval_split(sents, tagger, labeler, arc, aeW)
        res[split] = summarize(H, routes, parsers)
    res["elapsed_s"] = round(time.time() - t0, 1)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump({"anchor": "valency_labeled_patient_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    res = run(smoke=(a.self_test or a.smoke))
    for split in ("TEST", "TRAIN"):
        print("\n=== %s ===" % split, flush=True)
        for p in ("arc", "arceager"):
            acc = res[split][p]["acc"]; pr = res[split][p]["paired"]
            tag = "LIVE" if p == "arc" else "opt-off"
            print(" [%s %s] R0_landed=%.4f -> R_final=%.4f | R1_voice=%.4f R2_label=%.4f R3_valency=%.4f | ceiling=%.4f (n=%d)" % (
                p, tag, acc["R0_landed"]["acc"], acc["R_final"]["acc"], acc["R1_voice"]["acc"], acc["R2_label"]["acc"],
                acc["R3_valency"]["acc"], acc["ceiling_gold"]["acc"], acc["R0_landed"]["n"]), flush=True)
            print("      Rfinal_vs_landed=%s  R1_vs_shufvoice=%s  R3_vs_shufheads=%s  R2_vs_shuflabel=%s" % (
                pr["Rfinal_vs_landed"], pr["R1_vs_twin_shufvoice"], pr["R3_vs_twin_shufheads"], pr["R2_vs_twin_shuflabel"]), flush=True)
    if a.self_test or a.smoke:
        assert res["TEST"]["arc"]["acc"]["R0_live_pos_rp"]["n"] > 30
        print("\n[self-test] PASS", flush=True)


if __name__ == "__main__":
    main()
