"""exp_wire_predarg_binder_litbank_whodidwhat_v1 -- the ASSEMBLED pipeline (real arc PARSE -> event-semantic
router -> graded binder) on LitBank WHO-DID-WHAT, on real 19c literary prose.

This closes the two gaps the McGuffey role instrument could NOT (see the sibling cell
exp_wire_predarg_binder_live_reader_v1 + its SOLVED): (1) the graded binder's who-did-what value is invisible
on McGuffey (confirmed: random-bind twin ties, McGuffey lacks same-gender referential competition) -- LitBank
HAS it; (2) role assignment is untested on genuine literary prose, where the modern-trained parser is OOD
(Gildea 2001 measured 86.3->80.6 F1 news->literature).

WHAT IS NEW vs the LANDED binder result (+0.136, which used the dataset's OWN gold parse for role+gov_verb):
here the (role, gov_verb) that feed the binder + the who-did-what event set are RE-DERIVED FROM A REAL ARC
PARSE (hdlab.candidate_generator = persisted UPOS tagger + hashed arc parser -> route_predicate_arguments +
quotative inversion, with a positional good-enough fallback). So this measures the WHOLE assembled pipeline on
archaic prose, not the binder in isolation on a gold parse. Everything downstream (name clustering, ACT-R vs
graded binder, the situation-model event-set who-did-what scorer) is COMPOSED UNCHANGED from the landed
exp_coref_graded_binder_serves_whodidwhat_v1 (do not re-derive it).

ARMS (parse source x pronoun binder); metric = who-did-what pron-recall (= coreference of the pronoun to the
gold entity's cluster, weighted by governing-verb presence) via the landed _score_event_set; doc-bootstrap CI:
  GOLDPARSE+ACTR / GOLDPARSE+GRADED : the dataset's own gold parse (the landed reference; upper bound).
  ARCPARSE+ACTR                     : assembled pipeline, incumbent ACT-R binding.
  ARCPARSE+GRADED                   : assembled pipeline, the graded binder (the full wiring UNDER TEST).
  ARCPARSE+RANDBIND                 : info-free binding twin (must LOSE).
  POSITIONAL+ACTR                   : the current live-reader baseline (nearest-verb role/gov_verb + ACT-R).
Questions: (a) ARC vs GOLD parse = the archaic-prose parse cap; (b) GRADED vs ACT-R within ARC = the binder's
in-pipeline value on its right population; (c) ARC+GRADED vs POSITIONAL = the assembled wiring vs the incumbent.

Run: .venv/Scripts/python.exe experiments/exp_wire_predarg_binder_litbank_whodidwhat_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_wire_predarg_binder_litbank_whodidwhat_v1.py --run [--docs N]
GLASS-BOX. No external LLM at inference (the invariant). nltk (static) + numpy; no torch, no spaCy.
# KB_REFERENT: data/litbank/who_did_what_events.json
# KB_REFERENT: data/frontend_assets/pos_tagger_ud_ewt_upos.json
# KB_REFERENT: data/frontend_assets/arc_parser_hashed_ud_ewt.npz
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# ---- COMPOSE the landed who-did-what machinery (do not re-derive) ----
import experiments.exp_name_entity_clustering_v1 as NC  # noqa: E402
from experiments.exp_name_clustering_serves_whodidwhat_v1 import combined_pred, DECAY_D  # noqa: E402
from experiments.exp_coref_graded_binder_serves_whodidwhat_v1 import (  # noqa: E402
    combined_pred_binder, _score_event_set, tune_binder, _ngmap, _ci, _paired, _pron_full)
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer, SEED  # noqa: E402

# ---- the parse frontend + router (the NEW substitution) ----
from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402
from hdlab.predicate_argument_frontend import route_predicate_arguments, get_event_classes  # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402
# reuse the sibling cell's validated quotative-inversion pieces
from experiments.exp_wire_predarg_binder_live_reader_v1 import (  # noqa: E402
    _quotative_speaker, _is_speech_verb, _matrix_verbs)

POS_ASSET = os.path.join(REPO_ROOT, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
ARC_ASSET = os.path.join(REPO_ROOT, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
PA_TO_GRAM = {"agent": "SUBJECT", "theme": "OBJECT", "recipient": "OTHER", "goal": "OTHER",
              "source": "OTHER", "location": "OTHER", "path": "OTHER", "direction": "OTHER",
              "instrument": "OTHER"}


def conll_sents(path):
    """[[token per sentence]] from the CoNLL token column -- the tokenization the stream's (sent,start)
    indexes into (verified 100% aligned to span_tokens[0])."""
    sents, cur = [], []
    for line in open(path, encoding="utf-8"):
        if line.startswith("#"):
            continue
        if not line.strip():
            if cur:
                sents.append(cur); cur = []
            continue
        cur.append(line.rstrip("\n").split("\t")[3])
    if cur:
        sents.append(cur)
    return sents


class Parser:
    def __init__(self):
        self.tagger = PosTagger.load(POS_ASSET)
        self.parser = ArcParser.load(ARC_ASSET)
        self._cache = {}

    def parse(self, toks):
        key = tuple(toks)
        if key not in self._cache:
            if not toks or len(toks) > 120:
                self._cache[key] = ([], {})
            else:
                pos = self.tagger.tag(toks)
                heads = self.parser.parse(toks, pos).heads
                self._cache[key] = (pos, heads)
        return self._cache[key]


def _head_pos(sent_toks, m):
    """1-based head token position of a mention: the span token matching head_text, else the span start."""
    st = m["start"]; sp = m.get("span_tokens", [])
    ht = m["head_text"].lower()
    for k in range(len(sp)):
        if st + k < len(sent_toks) and sent_toks[st + k].lower() == ht:
            return st + k + 1
    return st + 1


def _router_role_gov(sent_toks, pos, heads, quotative=True):
    """For each 1-based head position, the router's (gram_role, gov_verb_lemma) if it is a matrix-verb
    argument. Returns {head_pos1: (gram, gov_lemma)}. Positional nearest-verb fallback handled by the caller."""
    out = {}
    for v in _matrix_verbs(sent_toks, pos, heads):
        # quotative=False: this cell applies its OWN quotative below (ablated via the `quotative` flag);
        # the landed router's default quotative is disabled here so the ablation stays faithful.
        roles = route_predicate_arguments(sent_toks, pos, heads, v, quotative=False)
        if quotative:
            lem = lemma_verb(sent_toks[v - 1])
            if _is_speech_verb(lem):
                sp = _quotative_speaker(sent_toks, pos, v)
                if sp is not None:
                    roles = dict(roles); roles["agent"] = sp; roles["theme"] = None
        gov = lemma_verb(sent_toks[v - 1])
        for pa_role in ("agent", "theme", "recipient", "goal", "source", "location", "path",
                        "direction", "instrument"):
            ti = roles.get(pa_role)
            if isinstance(ti, int) and ti and ti not in out:
                out[ti] = (PA_TO_GRAM.get(pa_role, "OTHER"), gov)
    return out


def _positional_role_gov(sent_toks, pos, head_pos1):
    """Good-enough positional fallback: gram_role by position vs nearest verb; gov_verb = nearest verb lemma.
    SUBJECT if the head precedes its nearest verb, else OBJECT."""
    verbs = [i for i in range(1, len(sent_toks) + 1) if pos[i - 1] == "VERB"]
    if not verbs:
        return None
    nearest = min(verbs, key=lambda v: abs(v - head_pos1))
    gram = "SUBJECT" if head_pos1 < nearest else "OBJECT"
    return gram, lemma_verb(sent_toks[nearest - 1])


def derive_stream(rec, sents, parser, mode="arc"):
    """A COPY of the gold enriched stream with role+gov_verb re-derived. mode:
      'arc'        : router role/gov_verb off the real parse (+ quotative), positional fallback.
      'positional' : nearest-verb role/gov_verb only (the current live-reader baseline).
      'gold'       : unchanged (the dataset's own parse -- the landed reference)."""
    if mode == "gold":
        return rec["stream"]
    stream = copy.deepcopy(rec["stream"])
    parses = {}
    for m in stream:
        s = m["sent"]
        if s >= len(sents):
            m["role"], m["gov_verb"] = "OTHER", None
            continue
        toks = sents[s]
        if s not in parses:
            pos, heads = parser.parse(toks)
            rr = _router_role_gov(toks, pos, heads) if mode == "arc" and pos else {}
            parses[s] = (pos, heads, rr)
        pos, heads, rr = parses[s]
        if not pos:
            m["role"], m["gov_verb"] = "OTHER", None
            continue
        hp = _head_pos(toks, m)
        if mode == "arc" and hp in rr:
            m["role"], m["gov_verb"] = rr[hp]
        else:
            pg = _positional_role_gov(toks, pos, hp)
            m["role"], m["gov_verb"] = pg if pg else ("OTHER", None)
    return stream


# ------------------------------------------------------------------------------------------------
def _coverage(stream):
    return sum(1 for m in stream if m.get("gov_verb")) / max(len(stream), 1)


def run(docs=None, n_boot=2000, seed=SEED, verbose=True):
    import time
    gaz = load_given_gazetteer()
    data = NC.load_enriched(docs)
    parser = Parser()
    sents_by_doc = {rec["doc"]: conll_sents(os.path.join(NC.CONLL_DIR, rec["doc"] + ".conll")) for rec in data}
    # PRE-PARSE all unique sentences once (the O(n^3) arc parse on long literary sentences is the cost) --
    # front-loaded with progress so the wall-clock is visible; the parser caches by token tuple.
    t0 = time.time()
    uniq = {}
    for rec in data:
        for toks in sents_by_doc[rec["doc"]]:
            uniq[tuple(toks)] = toks
    for j, toks in enumerate(uniq.values()):
        parser.parse(toks)
        if verbose and (j + 1) % 500 == 0:
            print(f"  parsed {j+1}/{len(uniq)} unique sentences ({time.time()-t0:.0f}s)", flush=True)
    if verbose:
        print(f"  parsed {len(uniq)} unique sentences in {time.time()-t0:.0f}s", flush=True)
    # derive the three parse-source stream variants (fast; uses the cache)
    variants = {}
    for mode in ("gold", "arc", "positional"):
        variants[mode] = [{"doc": rec["doc"], "stream": derive_stream(rec, sents_by_doc[rec["doc"]], parser, mode)}
                          for rec in data]
    dev_idx = set(range(0, len(data), 2))

    def split(v):
        dev = [r for i, r in enumerate(v) if i in dev_idx]
        test = [r for i, r in enumerate(v) if i not in dev_idx]
        return dev, test

    results = {"anchor": "wire_predarg_binder_litbank_whodidwhat_v1", "n_docs": len(data),
               "coverage_gov_verb": {m: round(np.mean([_coverage(r["stream"]) for r in variants[m]]), 3)
                                     for m in variants}}
    # TUNE THE BINDER ONCE on the GOLD-parse DEV split and REUSE it for every parse variant -- this both
    # isolates the PARSE effect (identical binder config, only the parse source changes) and avoids 3x tuning.
    gdev, _ = split(variants["gold"])
    gdev_ng = [_ngmap(r["stream"], gaz) for r in gdev]
    weights, d, W = tune_binder(gdev, "head", gaz, agree=True, ngmaps=gdev_ng)
    if verbose:
        print(f"  tuned binder (once, on gold DEV): d={d} W={W}", flush=True)
    arms = {}
    for mode in ("gold", "arc", "positional"):
        _, test = split(variants[mode])
        test_ng = [_ngmap(r["stream"], gaz) for r in test]
        actr, graded, rand, opb = {}, {}, {}, {}
        for di, rec in enumerate(test):
            stream = rec["stream"]; doc = rec["doc"]; ng = test_ng[di]
            rng = np.random.default_rng(seed + di)
            p_actr = combined_pred(stream, "HEAD", gaz, d, 0.4, rng)
            p_grad = combined_pred_binder(stream, "head", weights, gaz, d, W=W, mode="graded", agree=True, ng_map=ng)
            p_rand = combined_pred_binder(stream, "head", weights, gaz, d, W=W, mode="rand", agree=True, ng_map=ng,
                                          rng=np.random.default_rng(seed + 1000 + di))
            p_opb = combined_pred(stream, "HEAD_OPB", gaz, d, 0.4, rng)   # perfect PRONOUN binding = the ceiling
            for pred, acc in ((p_actr, actr), (p_grad, graded), (p_rand, rand), (p_opb, opb)):
                pc, pn, _tp, _fp, _fn = _score_event_set(stream, pred)
                acc[doc] = (pc, pn)
        arms[mode] = {"ACTR": actr, "GRADED": graded, "RAND": rand, "OPB": opb}
    results["tuned_weights"] = {k: round(v, 3) for k, v in weights.items()}

    def ci(mode, arm):
        return _ci(list(arms[mode][arm].values()), n_boot, seed)

    results["who_did_what_pron_recall"] = {
        f"{mode}+{arm}": ci(mode, arm)
        for mode in ("gold", "arc", "positional") for arm in ("ACTR", "GRADED", "RAND", "OPB")}
    # RESIDUAL DECOMPOSITION (arc pipeline): how much of the remaining headroom is BINDING (coref) vs the
    # rest (name-clustering + gov_verb attachment), to name the NEXT bottleneck.
    arc_actr = ci("arc", "ACTR")["acc"]; arc_grad = ci("arc", "GRADED")["acc"]; arc_opb = ci("arc", "OPB")["acc"]
    bind_headroom = arc_opb - arc_actr
    results["residual_decomposition_arc"] = {
        "current_arc_GRADED": arc_grad, "perfect_binding_ceiling_arc_OPB": arc_opb,
        "binder_recovers_of_binding_headroom": round((arc_grad - arc_actr) / bind_headroom, 3) if bind_headroom > 1e-6 else None,
        "binding_headroom_remaining_GRADED_to_OPB": round(arc_opb - arc_grad, 3),
        "non_binding_residual_OPB_to_1": round(1.0 - arc_opb, 3),
        "reading": ("headroom from GRADED to OPB = coref/binding still to win (the binder + coherence prior); "
                    "headroom from OPB to 1.0 = name-clustering + gov_verb attachment + metric strictness -- "
                    "the NEXT bottleneck if binding were perfect.")}
    results["contrasts"] = {
        # (a) archaic-prose PARSE cap: arc vs gold parse (same graded binder)
        "PARSE_CAP_arc_minus_gold_GRADED": _paired(arms["arc"]["GRADED"], arms["gold"]["GRADED"], n_boot, seed + 1),
        # (b) the BINDER's in-pipeline value on LitBank (arc parse): graded vs ACT-R
        "BINDER_arc_GRADED_minus_ACTR": _paired(arms["arc"]["GRADED"], arms["arc"]["ACTR"], n_boot, seed + 2),
        # the landed reference: graded vs ACT-R on the GOLD parse (reproduces ~+0.136 direction)
        "BINDER_gold_GRADED_minus_ACTR": _paired(arms["gold"]["GRADED"], arms["gold"]["ACTR"], n_boot, seed + 3),
        # (c) the assembled wiring vs the live incumbent: arc+graded vs positional+ACT-R
        "WIRED_arcGRADED_minus_positionalACTR": _paired(arms["arc"]["GRADED"], arms["positional"]["ACTR"], n_boot, seed + 4),
        # info-free binding twin (must LOSE) within the arc pipeline
        "arc_GRADED_minus_RANDtwin": _paired(arms["arc"]["GRADED"], arms["arc"]["RAND"], n_boot, seed + 5),
    }
    c = results["contrasts"]
    results["verdict"] = {
        "binder_lifts_whodidwhat_in_arc_pipeline_CI": c["BINDER_arc_GRADED_minus_ACTR"]["band"] == "ABOVE",
        "wired_beats_positional_incumbent_CI": c["WIRED_arcGRADED_minus_positionalACTR"]["band"] == "ABOVE",
        "randbind_twin_loses_CI": c["arc_GRADED_minus_RANDtwin"]["band"] == "ABOVE",
        "archaic_parse_cap_arc_below_gold": c["PARSE_CAP_arc_minus_gold_GRADED"]["band"],
    }
    return results


def self_test():
    """Alignment + derivation can-fail on ONE doc (fast): 100% token alignment; arc stream has non-trivial
    gov_verb coverage; the graded binder runs on the derived stream and scores."""
    gaz = load_given_gazetteer()
    data = NC.load_enriched(2)
    parser = Parser()
    rec = data[0]
    sents = conll_sents(os.path.join(NC.CONLL_DIR, rec["doc"] + ".conll"))
    # alignment
    tot = ok = 0
    for m in rec["stream"]:
        s, st = m["sent"], m["start"]
        if s < len(sents) and st < len(sents[s]) and m.get("span_tokens"):
            tot += 1; ok += int(sents[s][st].lower() == m["span_tokens"][0].lower())
    assert ok / max(tot, 1) > 0.98, f"tokenization must align to span_tokens[0]: {ok}/{tot}"
    arc = derive_stream(rec, sents, parser, "arc")
    cov = _coverage(arc)
    assert cov > 0.3, f"arc stream gov_verb coverage too low: {cov}"
    # the graded binder runs on the derived stream and produces a clustering + a scorable event set
    ng = _ngmap(arc, gaz)
    pred = combined_pred_binder(arc, "head", {"actr": 1.0}, gaz, DECAY_D, mode="graded", agree=True, ng_map=ng)
    pc, pn, _tp, _fp, _fn = _score_event_set(arc, pred)
    assert pn > 0, "no scorable pronoun who-did-what queries in the derived stream"
    print(f"SELF-TEST PASS (alignment {ok}/{tot}; arc gov_verb coverage {cov:.2f}; graded binder scores "
          f"{pc}/{pn} pron who-did-what on the derived stream).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.run:
        res = run(docs=args.docs, n_boot=args.n_boot)
        outdir = os.path.join(REPO_ROOT, "data/exp_wire_predarg_binder_litbank_whodidwhat_v1")
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        print(f"\n=== assembled pipeline on LitBank who-did-what ({res['n_docs']} docs) ===")
        print(f"gov_verb coverage: {res['coverage_gov_verb']}")
        print("who-did-what pron-recall (= coref of pronoun to gold entity, gov-verb-weighted) [95% CI]:")
        for k, v in res["who_did_what_pron_recall"].items():
            print(f"  {k:20s} {v['acc']:.3f} [{v['lo']:.3f},{v['hi']:.3f}]  n={v['n']}")
        print("contrasts:")
        for k, v in res["contrasts"].items():
            print(f"  {k:40s} delta={v['delta']:+.3f} [{v['lo']:+.3f},{v['hi']:+.3f}] null_p95={v['null_p95']:.3f} {v['band']}")
        print("residual decomposition (arc):", json.dumps(res["residual_decomposition_arc"]))
        print("verdict:", json.dumps(res["verdict"]))
        return
    print("use --self-test | --run [--docs N]")


if __name__ == "__main__":
    main()
