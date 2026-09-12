"""PROBE v19 (heads -> roles HAND-OFF): the role competition reads the parser's HEAD POSTERIOR instead of its hard head.
The labeler's configuration cue (head class x order) is built from ONE head today; the spec says every consumer should read
P(head). Here: posterior(role | token) = SUM_h P(h | token) * posterior(role | config built with head h, other cues from h),
using the live arc-factored parser's exact Matrix-Tree marginals (hdlab.graded_parser.GradedParse over the live ArcParser asset).
Measured on UD-EWT test nominals with the deployment tagger (predicted POS): hard-head competition labels vs head-marginalised
labels vs the supervised labeler; per coarse class. Heads with P < min_p are dropped (renormalised).
Run: .venv/Scripts/python.exe experiments/probe_role_headmarg_handoff_v19.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
import json
import sys
import time
from collections import Counter

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.probe_parse_rung_loss_affected_entity_v11 as V11
from hdlab import graded_role_assigner as GRA
from hdlab.graded_competition import net_activation, softmax
from hdlab.graded_parser import GradedParse
from tools.build_coarse_role_validities import sentences, coarse_of

TEST = os.path.join(_REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")


def role_posterior_headmarg(toks, pos, heads, marg, i, tab, min_p=0.05):
    """P(role | token i) marginalised over the head posterior marg[i] = {h: p}; heads of the OTHER tokens stay the MAP heads."""
    out = np.zeros(len(GRA.ROLE_CLASSES)); tot = 0.0
    for h, p in sorted(marg.get(i, {}).items(), key=lambda kv: -kv[1]):
        if p < min_p:
            continue
        hh = dict(heads); hh[i] = h
        S = GRA.coarse_role_supports(toks, pos, hh, i, tab)
        out += p * softmax(net_activation(S, {k: 1.0 for k in S}), gain=1.0); tot += p
    if tot <= 0:
        return GRA.coarse_role_posterior(toks, pos, heads, i, tab)
    return out / tot


def main():
    tg, pp, lb = V11._fe()
    gp = GradedParse(pp)
    tab = GRA.load_coarse_validities()
    tot = Counter(); hard = Counter(); marg_hit = Counter(); sup = Counter(); t0 = time.time(); nsent = 0
    for toks, gpos, gheads, deps in sentences(TEST):
        pos = list(tg.tag(toks)); po = gp.parse(toks, pos); heads = dict(po.map_heads); marg = po.marginals; nsent += 1
        supl = lb.label(toks, pos, heads, competition_roles=False)
        for i in range(1, len(toks) + 1):
            if gpos[i - 1] not in GRA.NOMINAL:
                continue
            g = coarse_of(deps.get(i)); tot[g] += 1
            ph = GRA.coarse_role_posterior(toks, pos, heads, i, tab)
            pm = role_posterior_headmarg(toks, pos, heads, marg, i, tab)
            hard[g] += int(GRA.ROLE_CLASSES[int(ph.argmax())] == g)
            marg_hit[g] += int(GRA.ROLE_CLASSES[int(pm.argmax())] == g)
            sup[g] += int(coarse_of(supl.get(i)) == g)
    n = sum(tot.values())
    out = {"n": n, "sentences": nsent, "hard_head_CM": round(sum(hard.values()) / n, 4), "head_marginalised_CM": round(sum(marg_hit.values()) / n, 4),
           "supervised_labeler": round(sum(sup.values()) / n, 4),
           "per_class": {g: {"n": tot[g], "hard": round(hard[g] / max(1, tot[g]), 3), "marg": round(marg_hit[g] / max(1, tot[g]), 3), "sup": round(sup[g] / max(1, tot[g]), 3)} for g in GRA.ROLE_CLASSES if tot[g]},
           "elapsed_s": round(time.time() - t0, 1)}
    print(json.dumps(out, indent=1))
    from experiments._seed_checkpoint import get_output_dir
    od = str(get_output_dir("probe_role_headmarg_handoff_v19")); os.makedirs(od, exist_ok=True)
    json.dump(out, open(os.path.join(od, "metrics.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
