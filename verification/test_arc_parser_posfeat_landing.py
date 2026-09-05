"""Landing witness: the LANDED hdlab arc parser, now scoring through the vectorized POS-feature path
(sentence_scores_auto, length-gated at n>=GATE_THRESH), is BYTE-IDENTICAL to the stock reference.

Problem: numpy_vectorize_the_arc_parser_pos_only_joint_features_p8_named_lever (Q111 landing).

After the promotion, ArcParser.parse() / .eval_uas() score via sentence_scores_auto (vectorized
scatter/gather for long sentences, the scalar fast path below), and ArcParser._parse_reference() is
the UNCHANGED stock path (arc matrix via _arc_ids + _decode). This witness parses thousands of real
LitBank sentences from documents NOT used to tune the optimization and asserts, for EVERY sentence:
  - the vectorized flat feature-id stream per arc equals hdlab.sentence_flat exactly (values AND
    order), on EVERY sentence (exercises the vec construction regardless of the length gate)
  - parse() (routed through sentence_scores_auto) decoded heads + arcs are identical to
    _parse_reference()
  - every per-token confidence margin is bit-identical (==, not approx)
plus a control that the vectorized (n>=GATE_THRESH) branch was actually exercised, and a re-confirm
that parse() is materially faster than the stock reference (>= 2x on a warm slice).

Self-contained: imports ONLY hdlab (no experiments/ cell). Deterministic. NO LLM. numpy + pure-python.

Run: .venv/Scripts/python.exe verification/test_arc_parser_posfeat_landing.py
"""
import os
import sys
import time

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import hdlab.arc_parser as A
from hdlab.arc_parser import ArcParser, FeatCache, sentence_flat, sentence_flat_vec, pos_tables, GATE_THRESH
from hdlab.pos_tagger import PosTagger
from hdlab.scene_segment import parse_conll_sentences

_POS = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_ARC = os.path.join(_REPO, "data/frontend_assets/arc_parser_hashed_ud_ewt.npz")
_CONLL = os.path.join(_REPO, "data/litbank/coref_conll")

# held-out from the tuning doc (1023_bleak_house)
_HELD_OUT = [
    "105_persuasion_brat.conll",
    "110_tess_of_the_durbervilles_a_pure_woman_brat.conll",
    "113_the_secret_garden_brat.conll",
    "120_treasure_island_brat.conll",
    "11_alices_adventures_in_wonderland_brat.conll",
]

PASS = 0
FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += ok
    FAIL += (not ok)
    return ok


def load_tagged(docs, per_doc, minlen=1, maxlen=100):
    tagger = PosTagger.load(_POS)
    out = []
    for d in docs:
        path = os.path.join(_CONLL, d)
        if not os.path.exists(path):
            continue
        cnt = 0
        for toks in parse_conll_sentences(path):
            if not (minlen <= len(toks) <= maxlen):
                continue
            out.append((list(toks), list(tagger.tag(toks))))
            cnt += 1
            if cnt >= per_doc:
                break
    return out


def main():
    parser = ArcParser.load(_ARC)          # parse() = landed vectorized (auto) path; _parse_reference() = stock
    T = pos_tables()                       # build the closed-tagset PosTables once (also lazily built inside parse)

    sents = load_tagged(_HELD_OUT, per_doc=250)
    n_arc = sum(len(t) * (len(t) + 1) - len(t) for t, _ in sents)
    n_long = sum(1 for t, _ in sents if len(t) >= GATE_THRESH)
    print("held-out: %d sentences (%d with n>=%d -> vectorized branch), %d arcs, from %d docs"
          % (len(sents), n_long, GATE_THRESH, n_arc, len(_HELD_OUT)), flush=True)

    # 1) vectorized flat feature-id stream identity vs the scalar sentence_flat (values + order), every arc,
    #    on EVERY sentence (independent of the length gate -- proves the vec construction is byte-identical).
    Cref = FeatCache()
    Cvec = FeatCache()
    flat_ok = True
    flat_checked = 0
    for toks, pos in sents:
        sent = [(k + 1, toks[k], pos[k], 0, "_") for k in range(len(toks))]
        fr, sr, orr, _ = sentence_flat(sent, Cref)
        fv, sv, ov, _ = sentence_flat_vec(sent, Cvec, T)
        if list(fv) != list(fr) or list(sv) != list(sr) or ov != orr:
            flat_ok = False
            break
        flat_checked += len(orr)
    chk("landed sentence_flat_vec feature-id stream byte-identical to sentence_flat (values+order), every arc",
        flat_ok, "%d arcs checked" % flat_checked)

    # 2/3) end-to-end head + margin identity: parse() (auto, vectorized) vs _parse_reference() (stock), every sentence
    head_mism = marg_mism = 0
    arc_checked = 0
    for toks, pos in sents:
        r = parser._parse_reference(toks, pos)
        f = parser.parse(toks, pos)
        if r.heads != f.heads:
            head_mism += 1
        if r.arcs != f.arcs:
            head_mism += 1
        for kk in r.margins:
            if r.margins[kk] != f.margins.get(kk):
                marg_mism += 1
                break
        arc_checked += len(r.arcs)
    chk("parse() (via sentence_scores_auto) heads + arcs identical to _parse_reference() on every held-out sentence",
        head_mism == 0, "%d/%d mismatched, %d arcs" % (head_mism, len(sents), arc_checked))
    chk("parse() per-token confidence margins bit-identical to _parse_reference() (==, not approx)",
        marg_mism == 0, "%d/%d mismatched" % (marg_mism, len(sents)))

    # 4) control: the vectorized (n>=GATE_THRESH) branch MUST actually be exercised, else identity is vacuous
    chk("vectorized branch actually exercised by the gated parse() (at least one n>=GATE_THRESH sentence)",
        n_long > 0, "%d/%d sentences hit the vectorized path" % (n_long, len(sents)))

    # 5) parse() materially faster than the stock reference (fair: same process, interleaved, median)
    slc = sents[:120]

    def t(fn, reps=5):
        fn(*slc[0])
        xs = []
        for _ in range(reps):
            t0 = time.perf_counter()
            for a, b in slc:
                fn(a, b)
            xs.append(time.perf_counter() - t0)
        xs.sort()
        return xs[len(xs) // 2]

    ts = t(parser._parse_reference)
    tf = t(parser.parse)
    chk("parse() >= 2x faster than _parse_reference() on a warm held-out slice",
        ts / tf >= 2.0, "stock %.3fs vs landed %.3fs = %.2fx" % (ts, tf, ts / tf))

    ok = FAIL == 0
    print("\n%s -- %d/%d checks passed; %d arcs verified bit-identical across %d held-out sentences (%d via the vectorized path)"
          % ("PASS" if ok else "FAIL", PASS, PASS + FAIL, arc_checked, len(sents), n_long), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
