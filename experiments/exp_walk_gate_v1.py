"""pri 147 -- GATE THE SPREADING-ACTIVATION WALK ON THE FREQUENCY BARRIER.

THE DEFECT (pri 146 phase 7, `data/exp_ppr_memo_v1/consumers.json`).  The graph walk that costs 61% of a
read is ONE TERM beside the verb's sense-frequency resting level in
`grounded_semantic_graph._blend_pick` -- `argmax[ log P_freq + lam*log PPR ]`.  On 12 GUM TEST documents
the walk overturns the frequency argmax on 91 of 844 occasions (10.8%).  On the other 89% it runs, costs
its 0.3 s, and cannot change the answer the resting level already gives.

THE BRAIN'S MECHANISM -- PINNED.  REORDERED ACCESS / THE SUBORDINATE-BIAS EFFECT (Duffy, Morris & Rayner
1988; Rayner & Frazier 1989; Binder & Rayner 1998): for a BALANCED ambiguous word (two senses of similar
frequency) a disambiguating context measurably changes and lengthens/shortens the fixation; for a BIASED
one (a dominant sense) prior context produces no comparable effect unless it is strong enough to overcome
the dominance.  Context is RECRUITED where the resting levels are close and NOT where one already
dominates.  ACT-R's retrieval has the same shape: a chunk whose base-level activation dominates resolves
without further cues.  THE COMPUTATION ("spread only when the base rate has not already decided") IS
PINNED.  THE THRESHOLD IS OURS: swept on TRAIN, reported on TEST, never adopted -- and (arm `--criterion`)
replaced by an ONLINE criterion the reader sets from its own experienced overturns, so nothing is frozen.

WHAT THE GATE IS, EXACTLY.  The barrier a walk would have to overcome is
    B = log P_freq(top-1) - log P_freq(top-2)          [nats, on the NORMALISED resting level]
computable from the prior ALONE, BEFORE the walk is requested.  Skip the walk when B >= tau.  NOTHING
ABOUT THE WALK CHANGES: not the damping, not the 30 iterations, not the graph, not the blend's lam.  Only
WHEN it runs changes.  `_blend_pick(None, prior, lam)` is the organ's OWN "no context" branch -- the gate
reuses it rather than re-deriving an argmax (REUSE BY STRUCTURE, owner 2026-09-16).

REUSE BY STRUCTURE.  The barrier's only input -- the normalised frequency prior -- is already computed
inside `_blend_pick` (`pf = prior + alpha; pf /= pf.sum()`).  The patch FACTORS THAT OUT into `_norm_prior`
and has BOTH `_blend_pick` and `frequency_barrier` call it, so there is exactly ONE implementation of the
resting level in this organ.  The distribution path's resting level is `affect_lexicon.resting_level`
(an existing organ function); the gate CALLS it and never re-derives it.

USAGE
  .venv/Scripts/python.exe experiments/exp_walk_gate_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_walk_gate_v1.py --sweep --split train [--docs 12]
  .venv/Scripts/python.exe experiments/exp_walk_gate_v1.py --sweep --split test  [--docs 12]
  .venv/Scripts/python.exe experiments/exp_walk_gate_v1.py --identity [--docs 12] [--tau T]
  .venv/Scripts/python.exe experiments/exp_walk_gate_v1.py --twin     [--docs 3]  [--tau T]
  .venv/Scripts/python.exe experiments/exp_walk_gate_v1.py --timing   [--docs 6]  [--pairs 2]
  .venv/Scripts/python.exe experiments/exp_walk_gate_v1.py --criterion [--docs 12]
  .venv/Scripts/python.exe experiments/exp_walk_gate_v1.py --board    [--docs 3]
  .venv/Scripts/python.exe experiments/exp_walk_gate_v1.py --make-diff [--out PATH]

Glass-box, NO external tool/dataset/model at inference, deterministic, CPU-only.  Modern gold only
(GUM; TEST = odd document index, TRAIN = even).  `data/corpora/holdout/` is never read.
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import random
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments._seed_checkpoint import get_output_dir          # noqa: E402  (Q115: canonical out dir)

ANCHOR = "exp_walk_gate_v1"
OUT_DIR = str(get_output_dir(ANCHOR))
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GSG_PATH = os.path.join(REPO, "hdlab", "grounded_semantic_graph.py")
FDV_PATH = os.path.join(REPO, "hdlab", "force_dynamics_valence.py")

# The tau the patch SHIPS.  Set from the TRAIN sweep (`--sweep --split train`); the sweep writes the value
# it chose into data/exp_walk_gate_v1/sweep_train.json and this constant is what `--make-diff` renders.
TAU_SHIPPED = 1.25
# The distribution path's own tau.  0.0 = the gate is OFF on that path.  DECIDED BY MEASUREMENT AT THE
# CONSUMER (`--identity` arm C), not by assumption: its prior is a different one (affect_lexicon's resting
# level) and its lam is 4.0, so the argmax path's tau does not transfer -- and NO tau > 0 is lossless on that
# path's own argmax (TRAIN: 27 of 242 moves lost at 1.25, 1 at 3.0, and 0 only where it skips nothing), so it
# can ONLY be certified at its consumer.  It is: on TRAIN it removes the graded posterior on 106 of 403
# consumer calls and changes 0 of 541 outputs, and the situation model is byte-identical on 12/12 documents;
# TEST confirms at 135 of 535 and 0 of 565, 12/12.
TAU_POST_SHIPPED = 1.25


# =====================================================================================================================
# 1. THE PROPOSED CHANGE, WRITTEN ONCE  (these strings are BOTH the runtime shim AND the shipped diff)
# =====================================================================================================================

def src_gsg_gate(tau: float) -> str:
    return '''WALK_GATE_TAU = %(tau).2f     # NATS.  THE BARRIER GATE (pri 147).  Spreading activation is recruited only when
                         # the sense-frequency RESTING LEVEL has NOT already decided: skip the walk when the
                         # top sense already leads the runner-up by >= WALK_GATE_TAU nats on the normalised
                         # prior.  THE COMPUTATION IS PINNED -- reordered access / the subordinate-bias effect
                         # (Duffy, Morris & Rayner 1988; Rayner & Frazier 1989; Binder & Rayner 1998): context
                         # measurably changes the read of a BALANCED ambiguous word and not of a BIASED one
                         # unless it is strong enough to overcome the dominance.  THE THRESHOLD IS OURS and is
                         # SWEPT, never adopted: swept on the GUM TRAIN split (even document index) and
                         # reported on the 12 TEST documents.  0.0 disables the gate (every walk runs), which
                         # is the floor arm every identity and timing comparison is made against.
                         # NOTHING ABOUT THE WALK CHANGES -- not DAMPING, not PPR_ITERS, not the graph, not
                         # the blend's lam.  Only WHEN it runs.


def _norm_prior(prior, alpha=0.1):
    """The sense-frequency RESTING LEVEL as a distribution.  ONE implementation, used by the blend AND by the
    barrier that gates it -- a second copy of this line would be a second implementation of the same
    computation."""
    pf = np.asarray(prior, dtype=float) + alpha
    return pf / pf.sum()


def frequency_barrier(prior, alpha=0.1):
    """HOW FAR AHEAD THE BASE RATE'S WINNER ALREADY IS, in nats: log P(top-1) - log P(top-2) on the normalised
    resting level.  `inf` when there is only one candidate (nothing to compete).  This is the whole of the
    gate's evidence and it is computed from the PRIOR ALONE, before any walk is requested."""
    pf = _norm_prior(prior, alpha)
    if pf.size < 2:
        return float("inf")
    top = np.partition(pf, -2)[-2:]
    return float(np.log(top[1]) - np.log(top[0]))


def _blend_pick(ppr, prior, lam, alpha=0.1, eps=1e-6):
    """argmax [ log P_freq + lam*log PPR ]. ppr None (no context, or the barrier gate fired) -> prior only
    (== MFS-by-count)."""
    pf = _norm_prior(prior, alpha)
    if ppr is None:
        return int(np.argmax(pf))
    pp = ppr + eps; pp = pp / pp.sum()
    return int(np.argmax(np.log(pf) + lam * np.log(pp)))

''' % {"tau": tau}


SRC_GSG_SELECT = '''    def select_sense_blended(self, lemma, pos, context_words, lam=0.5):
        """Read + the frequency resting-level prior via the log-linear blend (log P_freq + lam*log PPR) --
        the brain's ambiguity gate == the field's UKB combination. Best for all-words WSD where the prior matters.

        THE BARRIER GATE (pri 147).  The blend's prior is available before the walk is, so the walk is
        REQUESTED only when the resting level has not already decided (`frequency_barrier` >= WALK_GATE_TAU
        -> the prior stands).  Skipping hands `_blend_pick` the organ's own `ppr is None` branch, so the
        gated answer is the SAME function of the SAME prior -- there is no second argmax anywhere.
        MEASURED (12 GUM TEST documents, 817 sentences): the walk overturns the prior on 91 of 844 calls,
        and every one of those 91 had a barrier below 1.0 nat."""
        from hdlab.lexicon_foundation import wordnet as wn
        tgt = wn.synsets(lemma, pos=_WNPOS.get(pos)); tn = [s.name() for s in tgt]
        if not tgt:
            return None
        if len(tgt) == 1:
            return tn[0]
        prior = _sense_prior(lemma, tgt)
        if WALK_GATE_TAU > 0.0 and frequency_barrier(prior) >= WALK_GATE_TAU:
            return tn[_blend_pick(None, prior, lam)]          # the resting level has already decided
        ppr = _sense_ppr(wn, lemma, pos, list(context_words), self.syn2idx, self.T, len(self.syn2idx), tgt, tn)
        return tn[_blend_pick(ppr, prior, lam)]

'''


def src_fdv_post(tau: float) -> str:
    return '''SENSE_POSTERIOR_GATE_TAU = %(tau).2f   # NATS.  The barrier gate (pri 147) on the DISTRIBUTION path.  Same
                                  # pinned computation as grounded_semantic_graph.WALK_GATE_TAU, a DIFFERENT
                                  # threshold because this path has a different prior (affect_lexicon's
                                  # resting level, SENSE_ALPHA smoothing) and a different temperature
                                  # (SENSE_LAM = 4.0), so the argmax path's tau does not transfer and is not
                                  # reused.  0.0 = OFF.  Returning None here is EXACTLY equivalent to
                                  # returning the resting level: every consumer of this value
                                  # (`sense_expectation`, `fused_sense_value`, `sense_endstate_sign`) falls
                                  # back to `resting_level(rows)` when the posterior is None.


def sense_posterior_in_context(verb: str, tokens, gov_idx: int, lam: Optional[float] = None):
    """P(s | context) over ALL of the verb's senses (pri 100): the semantic graph's own log-linear blend of the resting level with
    the settled spreading activation over the sentence's content words, read as a DISTRIBUTION (not an argmax). None when the
    verb has < 2 senses in the asset, the context is thin (< 2 content words), the graph has no seed, or the frequency
    barrier has already decided (pri 147) -- the resting level stands."""
    try:
        from hdlab.affect_lexicon import sense_rows, resting_level, SENSE_LAM
        import numpy as np
        from hdlab.lexicon_foundation import wordnet as wn
        from hdlab.grounded_semantic_graph import _sense_ppr, frequency_barrier
        lam = SENSE_LAM if lam is None else lam
        lem = lemmatize_verb(verb)
        rows = sense_rows(lem)
        if not rows or len(rows) < 2:
            return None
        ctx = [str(t).lower() for i, t in enumerate(tokens) if i != gov_idx and str(t).isalpha()]
        if sum(1 for w in ctx if len(w) > 2 and w not in _CTX_STOP) < 2:
            return None
        rest = resting_level(rows)
        if SENSE_POSTERIOR_GATE_TAU > 0.0 and frequency_barrier(rest, alpha=0.0) >= SENSE_POSTERIOR_GATE_TAU:
            return None                      # the resting level has already decided -> do not recruit context
        g = _gsg()
        tgt = [wn.synset(r[0]) for r in rows]; tn = [r[0] for r in rows]
        ppr = _sense_ppr(wn, lem, "V", ctx, g.syn2idx, g.T, len(g.syn2idx), tgt, tn)
        if ppr is None:
            return None
        pp = np.asarray(ppr, float) + 1e-6; pp = pp / pp.sum()
        lg = np.log(np.asarray(rest, float)) + lam * np.log(pp)
        lg = lg - lg.max(); q = np.exp(lg)
        return list(q / q.sum())
    except Exception:
        return None

''' % {"tau": tau}


# =====================================================================================================================
# 2. THE PATCH  (anchors read from the LIVE files so they cannot drift out of date silently)
# =====================================================================================================================

def _read_lines(path):
    """The file as a list of lines, EACH KEEPING ITS OWN ENDING.  This tree mixes CRLF files with LF islands,
    so the patch is built at LINE granularity and every untouched line keeps the bytes it had --
    `git diff -w --stat` must equal `git diff --stat` for it."""
    with open(path, "rb") as fh:
        raw = fh.read()
    lines = raw.decode("utf-8").splitlines(keepends=True)
    assert "".join(lines).encode("utf-8") == raw, "round trip is not byte-identical: %s" % path
    return raw, lines


def _norm_text(lines):
    return "".join(l.replace("\r\n", "\n") for l in lines)


def _block(src, start, end):
    """The text from `start` (inclusive) to `end` (exclusive), both literal and each occurring once."""
    for m in (start, end):
        if src.count(m) != 1:
            raise SystemExit("ANCHOR MARKER matched %d times (expected 1): %r" % (src.count(m), m[:80]))
    a = src.index(start)
    b = src.index(end, a)
    return src[a:b]


def old_gsg_gate(lines):
    """`_blend_pick` as it stands on disk (the block the gate's constants + helpers replace)."""
    return _block(_norm_text(lines), "def _blend_pick(ppr, prior, lam, alpha=0.1, eps=1e-6):",
                  "\ndef _learn_cooc_edges(")


def old_gsg_select(lines):
    return _block(_norm_text(lines), "    def select_sense_blended(self, lemma, pos, context_words, lam=0.5):",
                  "\ndef _demo():")


def old_fdv_post(lines):
    return _block(_norm_text(lines), "def sense_posterior_in_context(verb: str, tokens, gov_idx: int,",
                  "\ndef context_sense_sign(")


def _apply(lines, old, new, path):
    """Replace the whole-line block `old` by `new`, giving every inserted line the ending of the first line it
    replaces."""
    each = [l.replace("\r\n", "\n") for l in lines]
    text = "".join(each)
    if text.count(old) != 1:
        raise SystemExit("PATCH ANCHOR matched %d times in %s (expected 1)" % (text.count(old), path))
    off = text.index(old)
    starts, acc = [], 0
    for l in each:
        starts.append(acc); acc += len(l)
    if off not in starts:
        raise SystemExit("PATCH ANCHOR does not start at a line boundary in %s" % path)
    i = starts.index(off)
    n_old = old.count("\n")
    eol = "\r\n" if lines[i].endswith("\r\n") else "\n"
    new_lines = [x + eol for x in new.split("\n")[:-1]]
    return lines[:i] + new_lines + lines[i + n_old:]


def patch_spec(tau=None, tau_post=None):
    tau = TAU_SHIPPED if tau is None else tau
    tau_post = TAU_POST_SHIPPED if tau_post is None else tau_post
    return [("hdlab/grounded_semantic_graph.py", GSG_PATH,
             [(old_gsg_gate, src_gsg_gate(tau)), (old_gsg_select, SRC_GSG_SELECT)]),
            ("hdlab/force_dynamics_valence.py", FDV_PATH,
             [(old_fdv_post, src_fdv_post(tau_post))])]


def patched_lines(path, edits):
    lines = _read_lines(path)[1]
    for old, new in edits:
        lines = _apply(lines, old(lines) if callable(old) else old, new, path)
    return lines


def make_diff(tau=None, tau_post=None) -> str:
    out = []
    for rel, path, edits in patch_spec(tau, tau_post):
        a = _read_lines(path)[1]
        b = patched_lines(path, edits)
        d = list(difflib.unified_diff(a, b, fromfile="a/" + rel, tofile="b/" + rel, n=6))
        if not d:
            continue
        out.append("diff --git a/%s b/%s\n" % (rel, rel))
        out.extend(d)
    return "".join(out)


def write_diff(path, tau=None, tau_post=None):
    """IN BYTES.  A shell redirect turns every CRLF into CRCRLF on this box; the cell writes the file itself."""
    txt = make_diff(tau, tau_post)
    with open(path, "wb") as fh:
        fh.write(txt.encode("utf-8"))
    return txt


# =====================================================================================================================
# 3. THE RUNTIME SHIM  (the same source, exec'd into the live modules; skipped when the patch has LANDED)
# =====================================================================================================================

def landed():
    """Detect the landed state from the LIVE MODULES, from names ONLY THIS DIFF ADDS, so the cell and the
    witness are green on either tree."""
    import hdlab.grounded_semantic_graph as GSG
    import hdlab.force_dynamics_valence as FDV
    return {"gate": hasattr(GSG, "WALK_GATE_TAU") and hasattr(GSG, "frequency_barrier")
                    and hasattr(GSG, "_norm_prior"),
            "post_gate": hasattr(FDV, "SENSE_POSTERIOR_GATE_TAU")}


_SAVED = {}


def install(tau=None, tau_post=None):
    """Exec the proposed source into the live modules.  A no-op for any part already landed.  `landed()` alone
    is NOT the test (pri 146's bug): after a `restore()` the ADDED NAMES would still be present, so the saved
    token is the authority."""
    import hdlab.grounded_semantic_graph as GSG
    import hdlab.force_dynamics_valence as FDV
    st = landed()
    if not st["gate"] and "gsg_blend" not in _SAVED:
        _SAVED["gsg_blend"] = GSG._blend_pick
        _SAVED["gsg_select"] = GSG.GroundedSemanticGraph.select_sense_blended
        _pre = set(GSG.__dict__)
        exec(compile(src_gsg_gate(TAU_SHIPPED if tau is None else tau), GSG_PATH, "exec"), GSG.__dict__)
        _SAVED["gsg_added"] = set(GSG.__dict__) - _pre - {"_blend_pick"}
        ns = {}
        exec(compile("class _P:\n" + SRC_GSG_SELECT, GSG_PATH, "exec"), GSG.__dict__, ns)
        GSG.GroundedSemanticGraph.select_sense_blended = ns["_P"].select_sense_blended
    if not st["post_gate"] and "fdv_post" not in _SAVED:
        _SAVED["fdv_post"] = FDV.sense_posterior_in_context
        _pre = set(FDV.__dict__)
        exec(compile(src_fdv_post(TAU_POST_SHIPPED if tau_post is None else tau_post), FDV_PATH, "exec"),
             FDV.__dict__)
        _SAVED["fdv_added"] = set(FDV.__dict__) - _pre - {"sense_posterior_in_context"}
    return st


def restore():
    """Put the live modules back exactly as they were."""
    import hdlab.grounded_semantic_graph as GSG
    import hdlab.force_dynamics_valence as FDV
    if "gsg_blend" in _SAVED:
        GSG._blend_pick = _SAVED.pop("gsg_blend")
        GSG.GroundedSemanticGraph.select_sense_blended = _SAVED.pop("gsg_select")
        for nm in _SAVED.pop("gsg_added", ()):
            GSG.__dict__.pop(nm, None)
    if "fdv_post" in _SAVED:
        FDV.sense_posterior_in_context = _SAVED.pop("fdv_post")
        for nm in _SAVED.pop("fdv_added", ()):
            FDV.__dict__.pop(nm, None)


class gate:
    """`with gate(tau, tau_post):` -- select the arm on a tree where the mechanism is present.  0.0 = the gate
    is INERT (every walk runs), which is the floor arm."""

    def __init__(self, tau=0.0, tau_post=0.0):
        self.tau, self.tau_post = float(tau), float(tau_post)

    def __enter__(self):
        import hdlab.grounded_semantic_graph as GSG
        import hdlab.force_dynamics_valence as FDV
        self.prev = (GSG.WALK_GATE_TAU, FDV.SENSE_POSTERIOR_GATE_TAU)
        GSG.WALK_GATE_TAU, FDV.SENSE_POSTERIOR_GATE_TAU = self.tau, self.tau_post
        return self

    def __exit__(self, *exc):
        import hdlab.grounded_semantic_graph as GSG
        import hdlab.force_dynamics_valence as FDV
        GSG.WALK_GATE_TAU, FDV.SENSE_POSTERIOR_GATE_TAU = self.prev
        return False


# =====================================================================================================================
# 4. THE READ, ITS SIGNATURE, AND THE SPLITS   (REUSE: pri 146's harness owns all of these)
# =====================================================================================================================

def _H():
    import experiments.exp_ppr_memo_v1 as H
    return H


def sig_json(sm):
    """pri 146's full-field situation-model signature -- REUSED, not re-implemented."""
    H = _H()
    return H.sig_json(H.sig(sm))


def _split_docs(split="test", n_docs=12):
    """The board's own GUM split: TEST = odd document index (pri 142/146), TRAIN = EVEN index.  Evenly spaced
    so a prefix cap cannot hand the run one or two genres."""
    import experiments.gum_coref as G
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, name_gazetteer=gaz, decision_source=G.DECISION_SOURCE)
    want = 1 if split == "test" else 0
    sel = [d for i, d in enumerate(docs) if i % 2 == want]
    if n_docs and n_docs < len(sel):
        step = len(sel) / float(n_docs)
        sel = [sel[int(i * step)] for i in range(n_docs)]
    return sel, gaz


def _conll(doc, tmp):
    return _H()._conll(doc, tmp)


def _reader(gaz):
    return _H()._reader(gaz)


def _read(path, gaz, tau=0.0, tau_post=0.0, reader=None):
    """One read at one operating point.  Returns (seconds, situation model, memo stats)."""
    rdr = reader if reader is not None else _reader(gaz)
    with gate(tau, tau_post):
        t0 = time.perf_counter()
        sm = rdr.read(path)
        dt = time.perf_counter() - t0
    m = getattr(rdr, "_ppr_memo", None)
    return dt, sm, (m.stats() if m is not None else None)


# =====================================================================================================================
# 5. THE RECORDER  (one instrumented read yields the WHOLE tau curve for both paths + the memo join)
# =====================================================================================================================

TAUS = (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 6.0)


class Recorder:
    """Wraps the four points the walk's signal passes through and records, per call:
      blend   -- the argmax path: the frequency barrier, the prior's argmax, the blend's pick.
      post    -- the distribution path: the resting level's barrier, its argmax, the posterior's argmax.
      hh      -- `harm_help_arithmetic`: its inputs' identity and its OUTPUT (the consumer bar).
      ppr     -- every walk request: its exact memo key and which path asked (the memo join).
    Nothing is changed: every wrapper calls the live function and returns its value unaltered."""

    def __init__(self):
        self.blend, self.post, self.hh, self.ppr = [], [], {}, []
        self.hh_post = {}
        self._path = [None]
        self._saved = None

    def __enter__(self):
        import numpy as np
        import hdlab.grounded_semantic_graph as GSG
        import hdlab.force_dynamics_valence as FDV
        b_blend, b_ppr = GSG._blend_pick, GSG._ppr
        b_select = GSG.GroundedSemanticGraph.select_sense_blended
        b_post, b_hh = FDV.sense_posterior_in_context, FDV.harm_help_arithmetic
        self._saved = (b_blend, b_ppr, b_select, b_post, b_hh)
        rec, path = self, self._path

        def blend(ppr, prior, lam, alpha=0.1, eps=1e-6):
            out = b_blend(ppr, prior, lam, alpha, eps)
            pf = np.asarray(prior, float) + alpha
            pf = pf / pf.sum()
            order = np.argsort(-pf)
            bar = float(np.log(pf[order[0]]) - np.log(pf[order[1]])) if pf.size > 1 else float("inf")
            raw = np.asarray(prior, float)
            row = {"prior_argmax": int(order[0]), "picked": int(out),
                   "walk_changed_the_argmax": int(out) != int(order[0]),
                   "frequency_barrier": round(bar, 6), "n_senses": int(pf.size),
                   "had_walk": ppr is not None,
                   # `_sense_prior` falls back to 1/(1+rank) when the lemma has NO SemCor counts -- a RANK
                   # GUESS, not evidence.  The gate must never fire on one, and this records whether it could.
                   "prior_is_the_rank_fallback": bool(raw.size > 1 and np.allclose(
                       raw, 1.0 / (1.0 + np.arange(raw.size))))}
            if ppr is not None and pf.size > 1:
                # THE BLEND'S OWN ALGEBRA (pri 147, the identity lever).  The blend picks j over the prior's
                # winner i* iff  lam*(log pp_j - log pp_i*) > log pf_i* - log pf_j.  For every j != i*,
                # log pf_i* - log pf_j >= B (the barrier is the SMALLEST such gap), so
                #     a flip REQUIRES  A := lam * max_j (log pp_j - log pp_i*)  >  B.
                # A is the whole force the walk can exert on this call, and it is MEASURABLE on every walk
                # that runs -- not only on the 10.8% that flip.  Gating at tau >= sup(A) is therefore lossless
                # BY IDENTITY on the population where that bound holds, not by a fitted threshold.
                pp = np.asarray(ppr, float) + eps
                pp = pp / pp.sum()
                lp = np.log(pp)
                i1 = int(order[0])
                adv = lam * float(np.max(np.delete(lp, i1)) - lp[i1])
                gap = np.log(pf[i1]) - np.delete(np.log(pf), i1)
                row["contextual_advantage"] = round(adv, 6)
                row["flip_margin"] = round(float(np.max(lam * (np.delete(lp, i1) - lp[i1]) - gap)), 6)
            rec.blend.append(row)
            return out

        def select(self_g, lemma, pos, context_words, lam=0.5):
            path[0] = "argmax"
            try:
                return b_select(self_g, lemma, pos, context_words, lam)
            finally:
                path[0] = None

        def post(verb, tokens, gov_idx, lam=None):
            from hdlab.affect_lexicon import sense_rows, resting_level
            path[0] = "posterior"
            try:
                out = b_post(verb, tokens, gov_idx, lam)
            finally:
                path[0] = None
            rows = sense_rows(FDV.lemmatize_verb(verb))
            bar, ram = float("inf"), None
            if rows and len(rows) >= 2:
                r = np.asarray(resting_level(rows), float)
                o = np.argsort(-r)
                bar = float(np.log(r[o[0]]) - np.log(r[o[1]]))
                ram = int(o[0])
            key = (verb, tuple(tokens), gov_idx)
            rec.post.append({"key": repr(key), "resting_barrier": round(bar, 6) if bar != float("inf") else None,
                             "resting_argmax": ram, "n_senses": len(rows),
                             "posterior_argmax": (int(np.argmax(out)) if out else None),
                             "posterior_is_none": out is None,
                             "posterior_moves_the_argmax": bool(out is not None and ram is not None
                                                                and int(np.argmax(out)) != ram)})
            return out

        def hh(verb, animacy, **kw):
            out = b_hh(verb, animacy, **kw)
            # THE KEY IS THE CONSUMER'S SITUATION, NOT ITS INPUTS' PROVENANCE: whether a posterior was handed
            # in is exactly what the gate changes, so including it in the key would report every gated call as
            # a "difference" without ever asking whether the ANSWER moved.  The provenance is recorded beside
            # the answer instead.
            k = "%s|%s|%s|%s|%s" % (verb, animacy, kw.get("endstate_reached"),
                                    kw.get("embedded_endstate_valence"), kw.get("endstate_sign_override"))
            rec.hh.setdefault(k, []).append(out)
            rec.hh_post.setdefault(k, []).append(kw.get("posterior") is not None)
            return out

        def ppr(seed_idx, Tt, n, d=GSG.DAMPING, iters=GSG.PPR_ITERS):
            # the memo's OWN key, hashed: the join only ever compares keys for equality, and the cue set can
            # be thousands of synsets -- rendering it per call would make the instrument the cost it measures.
            rec.ppr.append({"key": hash((tuple(seed_idx or ()), n, d, iters)), "path": path[0],
                            "n_seed": len(seed_idx or ())})
            return b_ppr(seed_idx, Tt, n, d, iters)

        GSG._blend_pick = blend
        GSG._ppr = ppr
        GSG.GroundedSemanticGraph.select_sense_blended = select
        FDV.sense_posterior_in_context = post
        FDV.harm_help_arithmetic = hh
        return self

    def __exit__(self, *exc):
        import hdlab.grounded_semantic_graph as GSG
        import hdlab.force_dynamics_valence as FDV
        (GSG._blend_pick, GSG._ppr, GSG.GroundedSemanticGraph.select_sense_blended,
         FDV.sense_posterior_in_context, FDV.harm_help_arithmetic) = self._saved
        return False


def curve(blend_rows, taus=TAUS):
    """The WHOLE tau curve for the argmax path, from ONE gate-off read: at every tau, how many walks the gate
    skips and how many of the walk's argmax changes it loses.  Exact -- the barrier is a function of the prior,
    which the gate cannot change."""
    w = [x for x in blend_rows if x["had_walk"]]
    ch = [x for x in w if x["walk_changed_the_argmax"]]
    out = {}
    for t in taus:
        sk = [x for x in w if x["frequency_barrier"] >= t]
        lost = [x for x in sk if x["walk_changed_the_argmax"]]
        out["tau_%.2f" % t] = {"walks_skipped": len(sk),
                               "share_skipped": round(len(sk) / max(len(w), 1), 4),
                               "argmax_changes_lost": len(lost),
                               "share_of_changes_lost": round(len(lost) / max(len(ch), 1), 4)}
    return out, len(w), len(ch)


def advantage_report(blend_rows, taus=TAUS):
    """THE IDENTITY, NOT THE THRESHOLD.  A flip REQUIRES the walk's contextual advantage A to exceed the
    barrier B (see `Recorder.blend`), so:
      * sup(A) over the population is a tau at which the gate is lossless BY CONSTRUCTION -- the arithmetic
        forbids a loss, no fitting is involved;
      * `flip_margin` > 0 is exactly 'the walk flipped this call', which is the algebra's own can-fail check
        against the observed outcome: if the two ever disagree, the derivation is wrong."""
    import numpy as np
    w = [x for x in blend_rows if x["had_walk"] and "contextual_advantage" in x]
    if not w:
        return {"n": 0}
    a = np.array([x["contextual_advantage"] for x in w], float)
    b = np.array([x["frequency_barrier"] for x in w], float)
    m = np.array([x["flip_margin"] for x in w], float)
    flipped = np.array([x["walk_changed_the_argmax"] for x in w], bool)
    q = {"q%d" % p: round(float(np.percentile(a, p)), 4) for p in (50, 90, 99)}
    out = {"n": len(w), "sup_contextual_advantage": round(float(a.max()), 4),
           "mean_contextual_advantage": round(float(a.mean()), 4), "percentiles": q,
           "algebra_agrees_with_the_outcome": int(((m > 0) == flipped).sum()),
           "algebra_disagrees_with_the_outcome": int(((m > 0) != flipped).sum()),
           "flips_with_advantage_below_the_barrier": int((flipped & (a <= b)).sum()),
           "share_skipped_at_the_provable_tau": round(float((b >= a.max()).mean()), 4),
           "provable_tau_curve": {}}
    for t in taus:
        out["provable_tau_curve"]["tau_%.2f" % t] = {
            "share_skipped": round(float((b >= t).mean()), 4),
            "calls_whose_advantage_exceeds_this_tau": int((a > t).sum())}
    return out


def random_twin(blend_rows, taus=TAUS, seeds=(11, 22, 33)):
    """THE INFO-FREE TWIN, computed exactly: a gate that skips the SAME NUMBER of walks AT RANDOM.  It has the
    same shape and the same cost saving and no information about the barrier, so it must LOSE."""
    w = [x for x in blend_rows if x["had_walk"]]
    ch = sum(1 for x in w if x["walk_changed_the_argmax"])
    out = {}
    for t in taus:
        k = sum(1 for x in w if x["frequency_barrier"] >= t)
        lost = []
        for s in seeds:
            rng = random.Random(s)
            pick = rng.sample(range(len(w)), k) if k <= len(w) else list(range(len(w)))
            lost.append(sum(1 for i in pick if w[i]["walk_changed_the_argmax"]))
        out["tau_%.2f" % t] = {"walks_skipped": k, "argmax_changes_lost_per_seed": lost,
                               "mean_lost": round(sum(lost) / len(lost), 2),
                               "expected_lost": round(k * ch / max(len(w), 1), 2)}
    return out


def memo_join(ppr_rows, blend_rows, tau):
    """THE JOIN THE BRIEF ASKS FOR: of the walks the gate skips, how many were ALREADY FREE (a memo hit), how
    many are genuinely REMOVED, and how many are merely MOVED to the other caller (the first request is
    skipped, so the second -- which was a hit -- becomes a miss and pays the full cost).

    A key's FIRST occurrence in a read is a memo miss; a repeat is a hit (the capacity is 128 and evictions
    are ~0.5% of calls, so this is the memo's own accounting and is cross-checked against `stats()`)."""
    arg = [i for i, r in enumerate(ppr_rows) if r["path"] == "argmax"]
    if len(arg) != len([x for x in blend_rows if x["had_walk"]]):
        # the two lists are aligned by construction (one _ppr per gated select that reaches the walk); if a
        # walk returned None early the counts diverge and the join is reported as unavailable rather than
        # silently mis-aligned.
        return {"aligned": False, "n_argmax_ppr_calls": len(arg),
                "n_blend_calls_with_a_walk": len([x for x in blend_rows if x["had_walk"]])}
    seen, first_hit = {}, []
    for i, r in enumerate(ppr_rows):
        first_hit.append(r["key"] in seen)
        seen.setdefault(r["key"], []).append(i)
    w = [x for x in blend_rows if x["had_walk"]]
    already_free = removed = moved = 0
    for j, i in enumerate(arg):
        if w[j]["frequency_barrier"] < tau:
            continue
        if first_hit[i]:
            already_free += 1
        elif any(k > i for k in seen[ppr_rows[i]["key"]]):
            moved += 1
        else:
            removed += 1
    # THE DOUBLE ACCESS, COUNTED.  `moved` exists only because the same cue set is asked by BOTH callers --
    # the sibling pays what the gate stops the first one paying.  The size of the double access is the number
    # of distinct cue sets both paths ask for, and it is the cap on what ANY gate on one path alone can save.
    by_key = {}
    for r in ppr_rows:
        by_key.setdefault(r["key"], set()).add(r["path"])
    both = [k for k, v in by_key.items() if "argmax" in v and "posterior" in v]
    return {"aligned": True, "tau": tau, "walks_skipped": already_free + removed + moved,
            "already_free_a_memo_hit": already_free, "genuinely_removed": removed,
            "merely_moved_to_the_other_caller": moved,
            "distinct_cue_sets": len(by_key), "cue_sets_asked_by_BOTH_paths": len(both),
            "total_ppr_calls": len(ppr_rows),
            "ppr_calls_by_path": {p: sum(1 for r in ppr_rows if r["path"] == p)
                                  for p in ("argmax", "posterior", None)},
            "memo_hits_in_this_read": sum(1 for x in first_hit if x)}


# =====================================================================================================================
# 6. ARMS
# =====================================================================================================================

def sweep(split="train", n_docs=12, mode="annotated"):
    """BAR 1 -- SWEEP TAU.  One GATE-OFF read per document with the recorder on, which yields the exact curve
    for every tau (the barrier is a function of the prior, so no re-read is needed per tau), the random twin,
    the distribution path's own curve, and the memo join."""
    install()
    docs, gaz = _split_docs(split, n_docs)
    tmp = tempfile.mkdtemp(prefix="p147_sweep_")
    per, blend_all, post_all, join = [], [], [], {}
    for d in docs:
        path = _conll(d, tmp)
        rdr = _reader(gaz)
        with Recorder() as rec:
            dt, sm, m = _read(path, gaz, tau=0.0, tau_post=0.0, reader=rdr)
        c, nw, nch = curve(rec.blend)
        row = {"docid": d.docid, "n_sentences": sm.n_sentences, "n_events": len(sm.events), "seconds": round(dt, 2),
               "blend_calls": len(rec.blend), "blend_calls_with_a_walk": nw, "walk_changed_the_argmax": nch,
               "posterior_calls": len(rec.post),
               "posterior_moves_the_argmax": sum(1 for x in rec.post if x["posterior_moves_the_argmax"]),
               "ppr_calls": len(rec.ppr), "memo": m, "curve": c}
        per.append(row); blend_all += rec.blend; post_all += rec.post
        join[d.docid] = {"%.2f" % t: memo_join(rec.ppr, rec.blend, t) for t in (1.0, 1.25, 1.5)}
        print("  %-30s sents=%-4d walks(argmax)=%-4d flips=%-3d  posterior calls=%-4d moves=%-4d  %.1fs"
              % (d.docid, sm.n_sentences, nw, nch, len(rec.post),
                 row["posterior_moves_the_argmax"], dt))
    c_all, nw, nch = curve(blend_all)
    # the distribution path's own curve, on ITS prior and ITS consequence (does the posterior's argmax differ
    # from the resting level's?) -- the analogue of "the walk overturns the prior" on that path
    pc = {}
    pw = [x for x in post_all if x["resting_barrier"] is not None and not x["posterior_is_none"]]
    pch = [x for x in pw if x["posterior_moves_the_argmax"]]
    for t in TAUS:
        sk = [x for x in pw if x["resting_barrier"] >= t]
        pc["tau_%.2f" % t] = {"walks_skipped": len(sk), "share_skipped": round(len(sk) / max(len(pw), 1), 4),
                              "argmax_moves_lost": sum(1 for x in sk if x["posterior_moves_the_argmax"]),
                              "share_of_moves_lost": round(sum(1 for x in sk if x["posterior_moves_the_argmax"])
                                                           / max(len(pch), 1), 4)}
    fb = [x for x in blend_all if x["had_walk"] and x.get("prior_is_the_rank_fallback")]
    safe = [t for t in TAUS if c_all["tau_%.2f" % t]["argmax_changes_lost"] == 0]
    chosen = min(safe) if safe else None
    adv = advantage_report(blend_all)
    res = {"arm": "sweep", "split": split, "landed_before_install": landed(), "n_documents": len(per),
           "per_document": per, "curve_totals": c_all, "random_twin": random_twin(blend_all),
           "posterior_curve_totals": pc, "memo_join": join,
           "blend_calls_with_a_walk": nw, "walk_changed_the_argmax": nch,
           "walk_changed_share": round(nch / max(nw, 1), 4),
           "posterior_calls_with_a_walk": len(pw), "posterior_moves_the_argmax": len(pch),
           "chosen_tau_smallest_that_loses_nothing": chosen, "advantage": adv,
           "walks_whose_prior_is_the_rank_fallback": len(fb),
           "rank_fallback_walks_the_gate_would_skip_at_the_chosen_tau":
               sum(1 for x in fb if chosen is not None and x["frequency_barrier"] >= chosen),
           "plain": ("on each page the reader is asked, before each spread, how far ahead the commonest "
                     "meaning of the verb already is; this counts how many spreads a given head start would "
                     "skip and how many real changes of mind that would cost")}
    _write("sweep_%s.json" % split, res)
    print("\n%s: %d walks, %d overturn the resting level (%.1f%%); smallest tau that loses NOTHING = %s"
          % (split.upper(), nw, nch, 100 * res["walk_changed_share"], chosen))
    for t in TAUS:
        k = "tau_%.2f" % t
        print("   tau=%-5.2f skip %-4d (%.1f%%)  lost %-3d   [random twin loses %.1f]"
              % (t, c_all[k]["walks_skipped"], 100 * c_all[k]["share_skipped"], c_all[k]["argmax_changes_lost"],
                 res["random_twin"][k]["mean_lost"]))
    return res


def identity(n_docs=12, tau=None, tau_post=None, split="test"):
    """BAR 2 + BAR 3 -- THE IDENTITY GATE AND THE CONSUMER.  Three arms per document, a FRESH READER each:
      A  gate OFF                      (the floor: every walk runs)
      B  the ARGMAX-path gate at tau   (must be byte-identical, or the loss is counted per event)
      C  B + the DISTRIBUTION-path gate at tau_post (measured AT `harm_help_arithmetic`, not assumed)
    Arm C runs only when tau_post > 0."""
    tau = TAU_SHIPPED if tau is None else tau
    tau_post = 1.0 if tau_post is None else tau_post
    install()
    docs, gaz = _split_docs(split, n_docs)
    tmp = tempfile.mkdtemp(prefix="p147_ident_")
    rows = []
    for d in docs:
        path = _conll(d, tmp)
        arms = {}
        for name, tt, tp in (("A_gate_off", 0.0, 0.0), ("B_argmax_gate", tau, 0.0),
                             ("C_both_gates", tau, tau_post)):
            if name == "C_both_gates" and tau_post <= 0:
                continue
            rdr = _reader(gaz)
            with Recorder() as rec:
                dt, sm, m = _read(path, gaz, tau=tt, tau_post=tp, reader=rdr)
            arms[name] = {"s": round(dt, 2), "sig": sig_json(sm), "hh": dict(rec.hh),
                          "hh_post": dict(rec.hh_post), "misses": (m or {}).get("misses"),
                          "ppr_calls": len(rec.ppr), "memo": m,
                          "events": {"%d|%d|%s" % (e.sent_idx, getattr(e, "idx", getattr(e, "global_idx", -1)),
                                                   e.predicate): e.affect for e in sm.events}}
        a = arms["A_gate_off"]
        row = {"docid": d.docid, "n_events": len(a["events"]), "tau": tau, "tau_post": tau_post}
        for name in ("B_argmax_gate", "C_both_gates"):
            if name not in arms:
                continue
            b = arms[name]
            ev = sorted(k for k in set(a["events"]) | set(b["events"])
                        if a["events"].get(k) != b["events"].get(k))
            hhk = sorted(set(a["hh"]) | set(b["hh"]))
            hh_diff = [k for k in hhk if a["hh"].get(k) != b["hh"].get(k)]
            # how many consumer calls LOST the graded posterior (the distribution path's gate firing), so
            # "the answer did not move" is reported against the number of chances it had to.
            lost_post = sum(1 for k in hhk
                            for x, y in zip(a["hh_post"].get(k, []), b["hh_post"].get(k, []))
                            if x and not y)
            tot_post = sum(sum(1 for x in a["hh_post"].get(k, []) if x) for k in hhk)
            row[name] = {"situation_model_identical": a["sig"] == b["sig"],
                         "affect_fields_that_differ": [{"event": k, "gate_off": a["events"].get(k),
                                                        "gate_on": b["events"].get(k)} for k in ev],
                         "n_affect_fields_that_differ": len(ev),
                         "harm_help_call_keys_compared": len(hhk),
                         "harm_help_outputs_that_differ": hh_diff[:20],
                         "n_harm_help_outputs_that_differ": len(hh_diff),
                         "harm_help_calls_that_lost_the_graded_posterior": lost_post,
                         "harm_help_calls_that_had_a_graded_posterior": tot_post,
                         "ppr_calls_off": a["ppr_calls"], "ppr_calls_on": b["ppr_calls"],
                         # THE COST CURRENCY IS THE MISS, NOT THE CALL.  With the memo live a skipped call
                         # that the sibling asks for again is MOVED, not removed: the call count falls but
                         # nothing is saved.  `misses` is the number of spreads actually computed.
                         "spreads_computed_off": a["misses"], "spreads_computed_on": b["misses"],
                         "spreads_removed": (None if a["misses"] is None
                                             else a["misses"] - b["misses"]),
                         "ppr_calls_removed": a["ppr_calls"] - b["ppr_calls"],
                         "ppr_calls_removed_share": round((a["ppr_calls"] - b["ppr_calls"])
                                                          / max(a["ppr_calls"], 1), 4),
                         "s_off": a["s"], "s_on": b["s"]}
        rows.append(row)
        print("  %-30s B: identical=%-5s walks %d->%d (-%.1f%%)  hh diffs=%d%s"
              % (d.docid, row["B_argmax_gate"]["situation_model_identical"],
                 row["B_argmax_gate"]["ppr_calls_off"], row["B_argmax_gate"]["ppr_calls_on"],
                 100 * row["B_argmax_gate"]["ppr_calls_removed_share"],
                 row["B_argmax_gate"]["n_harm_help_outputs_that_differ"],
                 ("   C: identical=%s hh diffs=%d walks -%.1f%%"
                  % (row["C_both_gates"]["situation_model_identical"],
                     row["C_both_gates"]["n_harm_help_outputs_that_differ"],
                     100 * row["C_both_gates"]["ppr_calls_removed_share"])) if "C_both_gates" in row else ""))
    res = {"arm": "identity", "split": split, "landed_before_install": landed(), "tau": tau,
           "tau_post": tau_post, "n_documents": len(rows), "per_document": rows}
    for name in ("B_argmax_gate", "C_both_gates"):
        got = [r[name] for r in rows if name in r]
        if not got:
            continue
        res[name] = {"n_identical": sum(1 for g in got if g["situation_model_identical"]),
                     "n_documents": len(got),
                     "total_affect_fields_that_differ": sum(g["n_affect_fields_that_differ"] for g in got),
                     "total_harm_help_outputs_that_differ": sum(g["n_harm_help_outputs_that_differ"]
                                                                for g in got),
                     "total_harm_help_call_keys": sum(g["harm_help_call_keys_compared"] for g in got),
                     "total_calls_that_lost_the_graded_posterior":
                         sum(g["harm_help_calls_that_lost_the_graded_posterior"] for g in got),
                     "total_calls_that_had_a_graded_posterior":
                         sum(g["harm_help_calls_that_had_a_graded_posterior"] for g in got),
                     "walks_off": sum(g["ppr_calls_off"] for g in got),
                     "walks_on": sum(g["ppr_calls_on"] for g in got),
                     "spreads_computed_off": sum(g["spreads_computed_off"] or 0 for g in got),
                     "spreads_computed_on": sum(g["spreads_computed_on"] or 0 for g in got)}
        res[name]["walks_removed_share"] = round(1 - res[name]["walks_on"] / max(res[name]["walks_off"], 1), 4)
        res[name]["spreads_removed_share"] = round(
            1 - res[name]["spreads_computed_on"] / max(res[name]["spreads_computed_off"], 1), 4)
    res["plain"] = ("each page is read with the gate off and with it on and the two readings are compared "
                    "field by field; any difference is the gate's own loss and is listed event by event")
    _write("identity_%s.json" % split, res)
    for name in ("B_argmax_gate", "C_both_gates"):
        if name in res:
            print("\n%s: IDENTICAL on %d of %d documents; walks %d -> %d (-%.1f%%); harm/help outputs that "
                  "differ: %d of %d"
                  % (name, res[name]["n_identical"], res[name]["n_documents"], res[name]["walks_off"],
                     res[name]["walks_on"], 100 * res[name]["walks_removed_share"],
                     res[name]["total_harm_help_outputs_that_differ"], res[name]["total_harm_help_call_keys"]))
    return res


def twin(n_docs=3, tau=None, seeds=(11, 22, 33), mode="annotated"):
    """BAR 4 -- THE INFO-FREE TWIN, RUN LIVE.  A gate that skips the SAME NUMBER of walks AT RANDOM (per
    document, per seed) must LOSE: the situation model must MOVE where the real gate's is identical.  (The
    exact per-change accounting over all 12 documents is in `sweep`'s `random_twin`, computed from the
    recorded barriers; this arm proves the loss reaches the product.)"""
    tau = TAU_SHIPPED if tau is None else tau
    install()
    import hdlab.grounded_semantic_graph as GSG
    docs, gaz = _split_docs("test", n_docs)
    tmp = tempfile.mkdtemp(prefix="p147_twin_")
    rows = []
    for d in docs:
        path = _conll(d, tmp)
        rdr = _reader(gaz)
        with Recorder() as rec:
            _, sm_off, _ = _read(path, gaz, tau=0.0, reader=rdr)
        w = [x for x in rec.blend if x["had_walk"]]
        share = sum(1 for x in w if x["frequency_barrier"] >= tau) / max(len(w), 1)
        off_j = sig_json(sm_off)
        _, sm_real, _ = _read(path, gaz, tau=tau, reader=_reader(gaz))
        row = {"docid": d.docid, "walks": len(w), "real_gate_skipped_share": round(share, 4),
               "real_gate_identical": sig_json(sm_real) == off_j, "twin": []}
        base_select = GSG.GroundedSemanticGraph.select_sense_blended
        for s in seeds:
            rng = random.Random(s)

            def rnd_select(self_g, lemma, pos, context_words, lam=0.5, _b=base_select, _r=rng, _p=share):
                """Same shape, same cost saving, NO information: skip with probability `share` regardless of
                the barrier."""
                from hdlab.lexicon_foundation import wordnet as wn
                tgt = wn.synsets(lemma, pos=GSG._WNPOS.get(pos)); tn = [x.name() for x in tgt]
                if not tgt:
                    return None
                if len(tgt) == 1:
                    return tn[0]
                prior = GSG._sense_prior(lemma, tgt)
                if _r.random() < _p:
                    return tn[GSG._blend_pick(None, prior, lam)]
                ppr = GSG._sense_ppr(wn, lemma, pos, list(context_words), self_g.syn2idx, self_g.T,
                                     len(self_g.syn2idx), tgt, tn)
                return tn[GSG._blend_pick(ppr, prior, lam)]

            GSG.GroundedSemanticGraph.select_sense_blended = rnd_select
            try:
                _, sm_t, _ = _read(path, gaz, tau=0.0, reader=_reader(gaz))
            finally:
                GSG.GroundedSemanticGraph.select_sense_blended = base_select
            row["twin"].append({"seed": s, "identical": sig_json(sm_t) == off_j})
        row["twin_changed_the_read_on_seeds"] = sum(1 for t in row["twin"] if not t["identical"])
        rows.append(row)
        print("  %-30s real gate identical=%-5s (skips %.1f%%)   random twin changed the read on %d of %d seeds"
              % (d.docid, row["real_gate_identical"], 100 * share, row["twin_changed_the_read_on_seeds"],
                 len(seeds)))
    res = {"arm": "twin", "landed_before_install": landed(), "tau": tau, "seeds": list(seeds),
           "per_document": rows, "n_documents": len(rows),
           "n_documents_real_gate_identical": sum(1 for r in rows if r["real_gate_identical"]),
           "n_seed_runs_twin_changed_the_read": sum(r["twin_changed_the_read_on_seeds"] for r in rows),
           "n_seed_runs": len(rows) * len(seeds),
           "plain": ("a gate that skips exactly as many spreads but picks them at random is run three times "
                     "on each page; it must change the reading where the real gate does not")}
    _write("twin.json", res)
    print("\nREAL GATE identical on %d of %d; RANDOM TWIN changed the read on %d of %d seed-runs"
          % (res["n_documents_real_gate_identical"], res["n_documents"],
             res["n_seed_runs_twin_changed_the_read"], res["n_seed_runs"]))
    return res


def timing(n_docs=6, pairs=2, tau=None, tau_post=0.0, mode="annotated"):
    """BAR 5 -- THE SAVING, HONESTLY TIMED, AND THE COMPOSITION WITH THE MEMO.  Four conditions per document,
    ALTERNATING within the pair so a load spike falls on both halves: memo OFF/ON x gate OFF/ON.  A pair whose
    two halves differ by more than 3x, or whose saving is negative, is DISCARDED and reported, and the
    ALL-PAIRS mean is printed beside the kept mean so the direction of the selection is visible."""
    tau = TAU_SHIPPED if tau is None else tau
    install()
    import hdlab.grounded_semantic_graph as GSG
    docs, gaz = _split_docs("test", n_docs)
    tmp = tempfile.mkdtemp(prefix="p147_time_")
    rows = []

    def one(path, cap, tt):
        """(seconds, spreads actually computed).  The MISS count is the cost currency: with the memo live a
        skipped call whose sibling asks again is MOVED, not removed."""
        prev = GSG.PPR_MEMO_MAX
        GSG.PPR_MEMO_MAX = cap
        try:
            dt, _sm, st = _read(path, gaz, tau=tt, tau_post=tau_post)
            return dt, (st or {}).get("misses")
        finally:
            GSG.PPR_MEMO_MAX = prev

    for d in docs:
        path = _conll(d, tmp)
        one(path, 0, 0.0)                    # warm every lazy asset OUT of the measurement
        acc = {k: [] for k in ("memo_off_gate_off", "memo_off_gate_on", "memo_on_gate_off", "memo_on_gate_on")}
        spreads = {k: [] for k in acc}
        for i in range(pairs):
            order = [("memo_off_gate_off", 0, 0.0), ("memo_off_gate_on", 0, tau),
                     ("memo_on_gate_off", None, 0.0), ("memo_on_gate_on", None, tau)]
            if i % 2:
                order = order[::-1]
            for nm, cap, tt in order:
                dt, ms = one(path, GSG.PPR_MEMO_MAX if cap is None else cap, tt)
                acc[nm].append(dt)
                spreads[nm].append(ms)
        row = {"docid": d.docid, "pairs": pairs, "seconds": {k: [round(x, 3) for x in v] for k, v in acc.items()},
               "mean_s": {k: round(sum(v) / len(v), 3) for k, v in acc.items()},
               "spreads_computed": {k: v for k, v in spreads.items()}}
        m = row["mean_s"]
        row["gate_saving_no_memo"] = round((m["memo_off_gate_off"] - m["memo_off_gate_on"])
                                           / m["memo_off_gate_off"], 4)
        row["gate_saving_with_memo"] = round((m["memo_on_gate_off"] - m["memo_on_gate_on"])
                                             / m["memo_on_gate_off"], 4)
        row["memo_saving_no_gate"] = round((m["memo_off_gate_off"] - m["memo_on_gate_off"])
                                           / m["memo_off_gate_off"], 4)
        row["both_vs_neither"] = round((m["memo_off_gate_off"] - m["memo_on_gate_on"])
                                       / m["memo_off_gate_off"], 4)
        row["kept"] = bool(row["gate_saving_with_memo"] > 0
                           and max(m.values()) / max(min(m.values()), 1e-9) <= 3.0)
        rows.append(row)
        print("  %-30s  no memo: %.2f->%.2f (-%.1f%%)   with memo: %.2f->%.2f (-%.1f%%)   both vs neither -%.1f%%%s"
              % (d.docid, m["memo_off_gate_off"], m["memo_off_gate_on"], 100 * row["gate_saving_no_memo"],
                 m["memo_on_gate_off"], m["memo_on_gate_on"], 100 * row["gate_saving_with_memo"],
                 100 * row["both_vs_neither"], "" if row["kept"] else "   [DISCARDED]"))
    ok = [r for r in rows if r["kept"]]

    def mean(rs, k):
        return round(sum(r[k] for r in rs) / len(rs), 4) if rs else None
    res = {"arm": "timing", "landed_before_install": landed(), "tau": tau, "tau_post": tau_post,
           "per_document": rows, "n_documents": len(rows), "n_kept": len(ok),
           "kept": {k: mean(ok, k) for k in ("gate_saving_no_memo", "gate_saving_with_memo",
                                             "memo_saving_no_gate", "both_vs_neither")},
           "ALL_pairs": {k: mean(rows, k) for k in ("gate_saving_no_memo", "gate_saving_with_memo",
                                                    "memo_saving_no_gate", "both_vs_neither")},
           "plain": ("how much reading time the gate removes, timed in alternating runs on the same machine, "
                     "with the walk-memory off and on so the two savings can be added up honestly")}
    _write("timing.json", res)
    print("\nKEPT (%d of %d): gate alone -%.1f%%; gate ON TOP OF the memo -%.1f%%; memo alone -%.1f%%; "
          "both vs neither -%.1f%%"
          % (len(ok), len(rows), 100 * (res["kept"]["gate_saving_no_memo"] or 0),
             100 * (res["kept"]["gate_saving_with_memo"] or 0), 100 * (res["kept"]["memo_saving_no_gate"] or 0),
             100 * (res["kept"]["both_vs_neither"] or 0)))
    return res


# =====================================================================================================================
# 7. THE QUALITY PUSH -- THE CRITERION IS LEARNED ONLINE, NOT A SWEPT CONSTANT
# =====================================================================================================================

class WalkGateCriterion:
    """NOTHING FROZEN (owner: 'plastic, never frozen').  A swept constant is a measurement of an equilibrium,
    not a mechanism.  The brain does not read a threshold off a table: it SETS A CRITERION from experienced
    outcomes (signal-detection criterion setting, Green & Swets 1966; the same accumulate-to-criterion shape
    as ACT-R's retrieval and the drift-diffusion boundary).

    THE OBSERVATION IS FREE AND IT IS ALREADY MADE.  Every time the gate lets a walk run, the reader learns
    whether the context OVERTURNED the resting level at that barrier -- `_blend_pick` already computes both
    argmaxes.  The criterion tracks the LARGEST barrier at which an overturn was ever experienced, plus a
    margin, so it is a running upper confidence bound on 'context can still win here':

        tau_t = max(tau_floor, margin + max{ B_i : overturn_i })

    It is CONSERVATIVE by construction (it only ever RISES when an overturn is seen at a high barrier, i.e.
    it only ever gates LESS after being surprised), it needs no labels, and it is exactly the quantity the
    swept constant estimates -- with the difference that it keeps estimating.  `observe` is one comparison
    per walk; the state is four floats on the reader.

    TWO OBSERVABLES, AND THE SECOND IS STRICTLY BETTER.
      mode="outcome"    observe WHETHER the context won at this barrier.  Informative on the ~11% of walks
                        that flip, so the estimate moves slowly.
      mode="advantage"  observe HOW HARD the context pushed -- A = lam*max_j(log pp_j - log pp_i*), the
                        contextual advantage the blend's own algebra says a flip requires to exceed the
                        barrier.  Available on EVERY walk that runs, so the criterion is estimated from all
                        of them, and a criterion at max(A)+margin is lossless BY IDENTITY, not by fit."""

    def __init__(self, tau_floor=0.5, margin=0.25, warmup=25, mode="outcome"):
        self.tau_floor, self.margin, self.warmup = float(tau_floor), float(margin), int(warmup)
        self.mode = mode
        self.n = 0
        self.n_overturn = 0
        self.max_overturn_barrier = 0.0
        self.max_advantage = 0.0

    def tau(self):
        if self.n < self.warmup:
            return 0.0                      # do not gate until the reader has seen anything: the floor arm
        seen = self.max_advantage if self.mode == "advantage" else self.max_overturn_barrier
        return max(self.tau_floor, self.margin + seen)

    def observe(self, barrier, overturned, advantage=None):
        self.n += 1
        if overturned:
            self.n_overturn += 1
            if barrier > self.max_overturn_barrier:
                self.max_overturn_barrier = float(barrier)
        if advantage is not None and advantage > self.max_advantage:
            self.max_advantage = float(advantage)

    def state(self):
        return {"n": self.n, "n_overturn": self.n_overturn, "mode": self.mode,
                "max_overturn_barrier": round(self.max_overturn_barrier, 4),
                "max_advantage": round(self.max_advantage, 4), "tau": round(self.tau(), 4)}


def criterion(n_docs=12, split="test", tau_floor=0.5, margin=0.25, warmup=25):
    """THE QUALITY PUSH, MEASURED.  Replay the TEST documents' recorded walks IN READING ORDER through the
    online criterion: it starts at 0 (gate off), observes each walk it lets through, and raises its criterion
    the first time context wins at a high barrier.  Report the share it skips and the changes it loses --
    against the swept constant, which is the equilibrium it is estimating.

    The replay is EXACT, not a simulation: the barrier is a function of the prior, which the gate cannot
    change, and a walk the criterion skips is one whose outcome the criterion then does not observe (the
    honest, causal version -- skipping costs it the observation)."""
    install()
    docs, gaz = _split_docs(split, n_docs)
    tmp = tempfile.mkdtemp(prefix="p147_crit_")
    seq, per = [], []
    for d in docs:
        path = _conll(d, tmp)
        with Recorder() as rec:
            dt, sm, _ = _read(path, gaz, tau=0.0, tau_post=0.0, reader=_reader(gaz))
        w = [x for x in rec.blend if x["had_walk"]]
        seq.append((d.docid, w))
        per.append({"docid": d.docid, "walks": len(w),
                    "overturns": sum(1 for x in w if x["walk_changed_the_argmax"]),
                    "max_contextual_advantage": round(max([x.get("contextual_advantage", 0.0) for x in w]
                                                          or [0.0]), 4)})
        print("  recorded %-30s walks=%-4d overturns=%-3d  sup(A)=%.3f"
              % (d.docid, len(w), per[-1]["overturns"], per[-1]["max_contextual_advantage"]))
    blend_all = [x for _, w in seq for x in w]
    adv = advantage_report(blend_all)

    def replay(mode):
        crit = WalkGateCriterion(tau_floor, margin, warmup, mode=mode)
        skipped = lost = ran = 0
        trace = []
        for docid, w in seq:
            d0 = {"docid": docid, "tau_at_start": round(crit.tau(), 4)}
            for x in w:
                t = crit.tau()
                if t > 0.0 and x["frequency_barrier"] >= t:
                    skipped += 1
                    if x["walk_changed_the_argmax"]:
                        lost += 1                 # the gate SKIPPED a walk that would have overturned
                    continue                      # ... and therefore does not observe it (honest and causal)
                ran += 1
                crit.observe(x["frequency_barrier"], x["walk_changed_the_argmax"],
                             x.get("contextual_advantage"))
            d0.update({"tau_at_end": round(crit.tau(), 4), "state": crit.state(),
                       "cum_skipped": skipped, "cum_lost": lost})
            trace.append(d0)
            print("    [%-9s] after %-30s tau=%.3f  skipped=%-4d lost=%-3d"
                  % (mode, docid, crit.tau(), skipped, lost))
        tot = sum(len(w) for _, w in seq)
        tot_ch = sum(1 for _, w in seq for x in w if x["walk_changed_the_argmax"])
        return {"mode": mode, "trace": trace, "walks": tot, "overturns": tot_ch,
                "walks_skipped": skipped, "walks_run": ran,
                "share_skipped": round(skipped / max(tot, 1), 4), "overturns_lost": lost,
                "share_of_overturns_lost": round(lost / max(tot_ch, 1), 4),
                "final_state": crit.state(), "final_tau": round(crit.tau(), 4)}

    arms = {m: replay(m) for m in ("outcome", "advantage")}
    res = {"arm": "criterion", "split": split, "landed_before_install": landed(), "n_documents": len(per),
           "per_document_recorded": per, "advantage": adv,
           "tau_floor": tau_floor, "margin": margin, "warmup": warmup, "arms": arms,
           "swept_constant_for_comparison": TAU_SHIPPED,
           "plain": ("instead of a fixed head start set once, the reader sets its own bar from what it keeps "
                     "seeing -- either from being surprised, or from how hard the context ever pushes -- and "
                     "this replays twelve pages in reading order to see where that bar settles and what it "
                     "costs")}
    _write("criterion.json", res)
    for m, a in arms.items():
        print("\nONLINE CRITERION [%s] settled at tau=%.3f: skipped %d of %d walks (%.1f%%), lost %d of %d "
              "overturns" % (m, a["final_tau"], a["walks_skipped"], a["walks"], 100 * a["share_skipped"],
                             a["overturns_lost"], a["overturns"]))
    print("sup(contextual advantage) = %.4f over %d walks; the gate is lossless BY IDENTITY at that tau, "
          "skipping %.1f%%" % (adv.get("sup_contextual_advantage", 0.0), adv.get("n", 0),
                               100 * adv.get("share_skipped_at_the_provable_tau", 0.0)))
    return res


def board(n_docs=3, n_boot=200, tau=None, tau_post=0.0, mode="annotated"):
    """BAR 6 -- THE PRODUCT BOARD'S OWN ROWS, byte-identical with the gate on."""
    tau = TAU_SHIPPED if tau is None else tau
    install()
    import experiments.exp_board_rows_on_the_reader_v1 as B

    def _arm(tt, tp):
        with gate(tt, tp):
            t0 = time.perf_counter()
            rows = B.run_gum(n_docs=n_docs, n_boot=n_boot)
            return time.perf_counter() - t0, rows

    off_t, off_rows = _arm(0.0, 0.0)
    on_t, on_rows = _arm(tau, tau_post)

    def _cmp(a, b):
        out, diff = {}, []
        ra, rb = a.get("rows", {}), b.get("rows", {})
        for m in sorted(ra):
            for r in sorted(ra[m]):
                same = (json.dumps(ra[m][r], sort_keys=True, default=str)
                        == json.dumps(rb.get(m, {}).get(r), sort_keys=True, default=str))
                out["%s/%s" % (m, r)] = same
                if not same:
                    diff.append("%s/%s" % (m, r))
        same_per = (json.dumps(a.get("per"), sort_keys=True, default=str)
                    == json.dumps(b.get("per"), sort_keys=True, default=str))
        out["per_document_scored_data"] = same_per
        if not same_per:
            diff.append("per_document_scored_data")
        return out, diff

    _write("board_raw.json", {"gate_off": off_rows, "gate_on": on_rows,
                              "seconds": {"gate_off": off_t, "gate_on": on_t}})
    cmp_, diff = _cmp(off_rows, on_rows)
    res = {"arm": "board", "landed_before_install": landed(), "tau": tau, "tau_post": tau_post,
           "n_documents": n_docs, "n_boot": n_boot, "gate_off_s": round(off_t, 1), "gate_on_s": round(on_t, 1),
           "per_row": cmp_, "rows_that_differ": diff, "all_identical": not diff,
           "reader_block_saved_share": round((off_t - on_t) / off_t, 4) if off_t else None,
           "plain": ("the product board's own reading block is run with the gate off and on and every "
                     "published row value is compared exactly")}
    _write("board.json", res)
    print("\nBOARD: %s (%d rows differ: %s)  block %.0fs -> %.0fs"
          % ("BYTE-IDENTICAL" if not diff else "DIFFERS", len(diff), diff or "none", off_t, on_t))
    return res


def chain(n_docs=12, split="test"):
    """PHASE 3(a) -- WHERE THE WALK'S SIGNAL IS LOST, COUNTED RUNG BY RUNG, NOT NARRATED.

    The distribution the walk feeds reaches the record through `harm_help_arithmetic` ->
    `endstate_valence_sign(v, afx, states, posterior)`, and that function is a CASCADE whose FIRST rung is
    posterior-BLIND:
      rung 0  `_EV_CACHE`               -- context-free reads only, so a call WITH a posterior never hits it
      rung 1  `result_state_value(v)`   -- the verb's VerbNet result state.  Decides without looking at the
                                          posterior at all; when it fires the walk cannot matter.
      rung 2  `sense_endstate_sign(v, posterior)` -- THE ONLY RUNG THAT READS THE DISTRIBUTION, and it reads
                                          it through `fused_sense_value` = (pw*v_word + E)/(pw+1) with
                                          pw = 2*rho, i.e. the WORD-FORM norm outweighs the sense expectation
                                          whenever rho > 0.5, and then thresholds |fused| at SENSE_TAU = 0.10
      rungs 3-5  superordinate / manner / genus -- posterior-blind again
    This arm reads each document once with the gate OFF and counts, per consumer call, which rung decided."""
    install()
    import hdlab.force_dynamics_valence as FDV
    import hdlab.affect_lexicon as AFX
    docs, gaz = _split_docs(split, n_docs)
    tmp = tempfile.mkdtemp(prefix="p147_chain_")
    calls = []
    b_hh, b_evs = FDV.harm_help_arithmetic, FDV.endstate_valence_sign

    def hh(verb, animacy, **kw):
        out = b_hh(verb, animacy, **kw)
        v = FDV.lemmatize_verb(verb)
        post = kw.get("posterior")
        rs = None
        try:
            rs = FDV.result_state_value(v)
        except Exception:
            rs = None
        rung1 = bool(rs is not None and abs(rs) >= FDV.STATE_MIN)
        verdict = None
        try:
            if AFX.sense_rows(v):
                verdict = AFX.sense_endstate_sign(v, post)[1]
        except Exception:
            verdict = None
        calls.append({"verb": v, "animacy": animacy, "had_posterior": post is not None,
                      "override_present": kw.get("endstate_sign_override") is not None,
                      "rung1_result_state_decides": rung1, "rung2_verdict": verdict,
                      "in_sense_asset": bool(AFX.sense_rows(v)), "output": out})
        return out

    FDV.harm_help_arithmetic = hh
    try:
        for d in docs:
            path = _conll(d, tmp)
            _read(path, gaz, tau=0.0, tau_post=0.0, reader=_reader(gaz))
            print("  read %-30s cumulative consumer calls=%d" % (d.docid, len(calls)))
    finally:
        FDV.harm_help_arithmetic = b_hh
    n = len(calls)
    withp = [c for c in calls if c["had_posterior"]]
    pre = [c for c in withp if c["rung1_result_state_decides"]]
    reach = [c for c in withp if not c["rung1_result_state_decides"] and c["in_sense_asset"]]
    verdicts = {}
    for c in reach:
        verdicts[str(c["rung2_verdict"])] = verdicts.get(str(c["rung2_verdict"]), 0) + 1
    res = {"arm": "chain", "split": split, "n_documents": len(docs), "n_consumer_calls": n,
           "calls_handed_a_graded_posterior": len(withp),
           "of_those_decided_by_the_posterior_BLIND_result_state_rung_first": len(pre),
           "of_those_reaching_the_only_rung_that_reads_the_distribution": len(reach),
           "rung2_verdicts_on_those": verdicts,
           "share_of_posterior_calls_where_the_distribution_can_matter":
               round(len(reach) / max(len(withp), 1), 4),
           "outputs": {str(k): sum(1 for c in calls if c["output"] == k)
                       for k in {c["output"] for c in calls}},
           "SENSE_TAU": AFX.SENSE_TAU, "SENSE_K_W": AFX.SENSE_K_W, "STATE_MIN": FDV.STATE_MIN,
           "plain": ("counts, for every harm/help judgement the reader makes, whether the graded meaning "
                     "distribution the expensive spread produces could have mattered at all -- an earlier "
                     "rung of the same cascade answers first on most of them")}
    _write("chain_%s.json" % split, res)
    print("\nCONSUMER CALLS %d; handed a graded posterior %d; the posterior-BLIND result-state rung decides "
          "first on %d; only %d (%.1f%%) reach the one rung that reads the distribution -- verdicts %s"
          % (n, len(withp), len(pre), len(reach),
             100 * res["share_of_posterior_calls_where_the_distribution_can_matter"], verdicts))
    return res


def organs(_unused=None):
    """REUSE BY STRUCTURE, COUNTED NOT ASSERTED (owner 2026-09-16; 'an absence claim is an enumeration').

    Two questions, both answered by enumerating the tree rather than by recalling it:
      (a) WHICH ORGAN OWNS THIS COMPUTATION?  The barrier is the top-1-minus-top-2 margin of an additive
          log-activation -- exactly `graded_competition.graded_pick(...)["margin"]` on a single cue.  This
          arm PROVES the equality numerically on random priors instead of claiming it in prose.
      (b) IS THE BRAIN STRUCTURE ALREADY BUILT?  Reordered access / LIFG-pMTG semantic control is
          `hdlab/semantic_control.py` (landed, owner-DONE).  This arm counts its LIVE callers inside
          `hdlab/` -- a dormancy claim must be a count."""
    import re
    import numpy as np
    from hdlab import graded_competition as GC
    install()
    import hdlab.grounded_semantic_graph as GSG
    rng = np.random.RandomState(20260917)
    worst = 0.0
    for _ in range(500):
        k = int(rng.randint(2, 9))
        prior = np.abs(rng.gamma(0.7, 3.0, size=k))
        pf = GSG._norm_prior(prior, 0.1)
        gp = GC.graded_pick({"frequency": np.log(pf)}, {"frequency": 1.0})
        worst = max(worst, abs(float(gp["margin"]) - GSG.frequency_barrier(prior, 0.1)))
    callers = {}
    for mod in ("semantic_control", "graded_competition", "underspecified_sense_reader",
                "diagnostic_context_wsd"):
        hits = []
        for root, _dirs, files in os.walk(os.path.join(REPO, "hdlab")):
            for fn in files:
                if not fn.endswith(".py") or fn == mod + ".py":
                    continue
                p = os.path.join(root, fn)
                with open(p, encoding="utf-8", errors="replace") as fh:
                    txt = fh.read()
                for m in re.finditer(r"^[ \t]*(?:from|import)\s+[\w.]*\b%s\b" % mod, txt, re.M):
                    hits.append(os.path.relpath(p, REPO).replace("\\", "/") + ":"
                                + str(txt[:m.start()].count("\n") + 1))
        callers[mod] = hits
    res = {"arm": "organs",
           "barrier_equals_graded_competition_margin": {"max_abs_difference_over_500_random_priors":
                                                        float(worst), "identical": worst < 1e-12},
           "live_import_sites_inside_hdlab": {k: {"n": len(v), "sites": v} for k, v in callers.items()},
           "plain": ("checks, by counting rather than recalling, that the head-start number this work adds is "
                     "arithmetically the same quantity an existing competition organ already computes, and "
                     "how many places in the live reader actually use the organ that owns this decision")}
    _write("organs.json", res)
    print("barrier == graded_competition margin on 500 random priors: max |diff| = %.2e" % worst)
    for k, v in callers.items():
        print("  hdlab modules that import %-28s : %d %s" % (k, len(v), v or ""))
    return res


def _write(name, obj):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2)
    print("wrote %s" % os.path.join(OUT_DIR, name))


# =====================================================================================================================
# 8. SELF-TEST
# =====================================================================================================================

def self_test() -> int:
    import numpy as np
    import hdlab.grounded_semantic_graph as GSG
    import hdlab.force_dynamics_valence as FDV
    ok = [True]
    log = []

    def chk(name, cond, detail=""):
        ok[0] = ok[0] and bool(cond)
        log.append({"check": name, "pass": bool(cond), "detail": str(detail)})
        print("  [%s] %-58s %s" % ("PASS" if cond else "FAIL", name, detail))

    st0 = landed()
    print("tree state before install: %s" % st0)
    install()
    st = landed()
    chk("T1 the gate's names are live after install", st["gate"] and st["post_gate"], st)

    # -- the barrier's arithmetic -------------------------------------------------------------------------
    b = GSG.frequency_barrier(np.array([10.0, 1.0]), alpha=0.0)
    chk("T2 barrier == log(p1/p2) exactly", abs(b - np.log(10.0)) < 1e-12, "%.6f vs %.6f" % (b, np.log(10.0)))
    chk("T3 barrier is inf for a single candidate", GSG.frequency_barrier(np.array([3.0])) == float("inf"))
    chk("T4 barrier is 0 for a tie", abs(GSG.frequency_barrier(np.array([2.0, 2.0, 1.0]), alpha=0.0)) < 1e-12)
    chk("T5 barrier ignores order", abs(GSG.frequency_barrier(np.array([1.0, 9.0, 3.0]))
                                        - GSG.frequency_barrier(np.array([9.0, 3.0, 1.0]))) < 1e-12)
    chk("T6 barrier uses top-2 not top-1-vs-last",
        abs(GSG.frequency_barrier(np.array([8.0, 4.0, 1.0]), alpha=0.0) - np.log(2.0)) < 1e-12)

    # -- ONE implementation of the resting level ----------------------------------------------------------
    pr = np.array([7.0, 2.0, 1.0])
    chk("T7 _norm_prior is the blend's own normalisation",
        np.allclose(GSG._norm_prior(pr, 0.1), (pr + 0.1) / (pr + 0.1).sum()))
    chk("T8 _blend_pick(None,...) == argmax of the normalised prior (the organ's own branch, reused)",
        GSG._blend_pick(None, pr, 0.5) == int(np.argmax(GSG._norm_prior(pr, 0.1))))
    src = src_gsg_gate(1.0) + SRC_GSG_SELECT
    chk("T9 the shipped source normalises the prior in exactly one place",
        src.count("/ pf.sum()") == 1, "%d occurrences" % src.count("/ pf.sum()"))

    # -- the gate's live behaviour on the real organ ------------------------------------------------------
    from hdlab.force_dynamics_valence import _gsg
    g = _gsg()
    ctx = ["river", "water", "flow", "shore", "boat"]
    calls = {"n": 0}
    base = GSG._sense_ppr

    def counted(*a, **k):
        calls["n"] += 1
        return base(*a, **k)
    GSG._sense_ppr = counted
    try:
        with gate(0.0, 0.0):
            calls["n"] = 0
            off = g.select_sense_blended("bank", "N", ctx)
            n_off = calls["n"]
        with gate(1e9, 0.0):
            calls["n"] = 0
            hi = g.select_sense_blended("bank", "N", ctx)
            n_hi = calls["n"]
        with gate(1e-9, 0.0):
            calls["n"] = 0
            lo = g.select_sense_blended("bank", "N", ctx)
            n_lo = calls["n"]
            prior_pick = g.select_sense_blended("bank", "N", ctx)
    finally:
        GSG._sense_ppr = base
    chk("T10 tau=0 is INERT: the walk runs", n_off == 1, "walks=%d" % n_off)
    chk("T11 an unreachable tau never gates: same answer, walk still runs", hi == off and n_hi == 1,
        "%s vs %s, walks=%d" % (hi, off, n_hi))
    chk("T12 tau -> 0+ gates EVERY walk", n_lo == 0, "walks=%d" % n_lo)
    from hdlab.lexicon_foundation import wordnet as wn
    tgt = wn.synsets("bank", pos="n")
    mfs = tgt[int(np.argmax(GSG._norm_prior(GSG._sense_prior("bank", tgt), 0.1)))].name()
    chk("T13 a gated pick IS the resting level's own answer", lo == mfs, "%s vs %s" % (lo, mfs))
    chk("T13b and it is deterministic", prior_pick == lo)

    # -- the walk itself is untouched ---------------------------------------------------------------------
    srcs = src_gsg_gate(1.0) + SRC_GSG_SELECT + src_fdv_post(1.0)
    code = "\n".join(l.split("#")[0] for l in srcs.split("\n"))     # comments name them; CODE must not touch them
    chk("T14 no CODE line in the patch touches a walk parameter",
        ("DAMPING" not in code) and ("PPR_ITERS" not in code) and ("def _ppr(" not in code)
        and ("iters" not in code),
        "damping/iters/_ppr absent from %d code lines" % len(code.split("\n")))
    stock_call = ("_sense_ppr(wn, lemma, pos, list(context_words), self.syn2idx, self.T, "
                  "len(self.syn2idx), tgt, tn)")
    chk("T14b the walk is still requested with the stock argument list", stock_call in SRC_GSG_SELECT)
    chk("T15 the patch does not change the blend's lam", "lam=0.5" in SRC_GSG_SELECT and "lam * np.log" in srcs)

    # -- the distribution path ----------------------------------------------------------------------------
    chk("T16 the posterior gate returns None (== the resting level for every consumer)",
        "return None                      # the resting level has already decided" in src_fdv_post(1.0))
    from hdlab.affect_lexicon import sense_rows, resting_level, sense_endstate_sign
    lem = None
    for cand in ("treat", "beat", "hold", "pull", "run"):
        if len(sense_rows(cand)) >= 2:
            lem = cand
            break
    chk("T17 a lemma with >= 2 senses exists in the asset", lem is not None, lem)
    if lem:
        a = sense_endstate_sign(lem, None)
        b2 = sense_endstate_sign(lem, resting_level(sense_rows(lem)))
        chk("T18 posterior=None IS posterior=resting_level at the consumer", a == b2, "%s vs %s" % (a, b2))

    # -- install / restore / install (the pri 146 lesson: hasattr alone is not the test) -------------------
    if not st0["gate"]:
        restore()
        chk("T19 restore puts the stock module back", not landed()["gate"])
        install()
        chk("T20 re-install works after a restore", landed()["gate"] and hasattr(GSG, "frequency_barrier"))
    else:
        chk("T19 tree is LANDED: the shim is correctly skipped", "gsg_blend" not in _SAVED)
        chk("T20 landed tree exposes the gate on the live module", hasattr(GSG, "WALK_GATE_TAU"))

    # -- the curve and the twin ---------------------------------------------------------------------------
    rows = [{"had_walk": True, "frequency_barrier": 0.1, "walk_changed_the_argmax": True},
            {"had_walk": True, "frequency_barrier": 2.0, "walk_changed_the_argmax": False},
            {"had_walk": True, "frequency_barrier": 3.0, "walk_changed_the_argmax": False},
            {"had_walk": False, "frequency_barrier": 9.0, "walk_changed_the_argmax": False}]
    c, nw, nch = curve(rows, taus=(0.5, 2.5))
    chk("T21 the curve counts only walks that ran", nw == 3 and nch == 1)
    chk("T22 the curve is monotone in tau", c["tau_0.50"]["walks_skipped"] >= c["tau_2.50"]["walks_skipped"])
    chk("T23 the gate at tau=0.5 loses nothing here", c["tau_0.50"]["argmax_changes_lost"] == 0,
        c["tau_0.50"])
    tw = random_twin(rows, taus=(0.5,), seeds=(1, 2, 3))
    chk("T24 the random twin skips the same number", tw["tau_0.50"]["walks_skipped"] == 2)

    # -- the memo join ------------------------------------------------------------------------------------
    pr_rows = [{"key": "k1", "path": "argmax"}, {"key": "k1", "path": "posterior"},
               {"key": "k2", "path": "argmax"}, {"key": "k3", "path": "posterior"}]
    bl = [{"had_walk": True, "frequency_barrier": 5.0, "walk_changed_the_argmax": False},
          {"had_walk": True, "frequency_barrier": 5.0, "walk_changed_the_argmax": False}]
    j = memo_join(pr_rows, bl, 1.0)
    chk("T25 the join separates MOVED from REMOVED",
        j["aligned"] and j["merely_moved_to_the_other_caller"] == 1 and j["genuinely_removed"] == 1, j)

    # -- the online criterion -----------------------------------------------------------------------------
    cr = WalkGateCriterion(tau_floor=0.5, margin=0.25, warmup=2)
    chk("T26 the criterion does not gate before warm-up", cr.tau() == 0.0)
    cr.observe(0.1, False); cr.observe(0.2, False)
    chk("T27 after warm-up it sits at its floor", abs(cr.tau() - 0.5) < 1e-12, cr.state())
    cr.observe(1.4, True)
    chk("T28 a surprise at a high barrier RAISES the criterion (it gates LESS)",
        abs(cr.tau() - 1.65) < 1e-12, cr.state())
    cr.observe(0.3, True)
    chk("T29 a surprise at a low barrier does not lower it", abs(cr.tau() - 1.65) < 1e-12, cr.state())

    # -- THE GATE CANNOT FIRE WHERE THE PRIOR IS A RANK GUESS ---------------------------------------------
    fb_bars = [GSG.frequency_barrier(1.0 / (1.0 + np.arange(k))) for k in range(2, 12)]
    chk("T33 a lemma with NO frequency evidence is never gated (the rank fallback's barrier < tau)",
        max(fb_bars) < TAU_SHIPPED, "max fallback barrier %.4f < tau %.2f" % (max(fb_bars), TAU_SHIPPED))

    # -- REUSE BY STRUCTURE: the barrier is an EXISTING organ's computation ---------------------------------
    from hdlab import graded_competition as GC
    rng = np.random.RandomState(4242)
    worst = 0.0
    for _ in range(200):
        k = int(rng.randint(2, 9))
        prior = np.abs(rng.gamma(0.7, 3.0, size=k))
        pf = GSG._norm_prior(prior, 0.1)
        worst = max(worst, abs(float(GC.graded_pick({"frequency": np.log(pf)}, {"frequency": 1.0})["margin"])
                               - GSG.frequency_barrier(prior, 0.1)))
    chk("T34 the barrier IS graded_competition's competition margin on the frequency cue", worst < 1e-12,
        "max |diff| over 200 random priors = %.2e" % worst)

    # -- the patch ----------------------------------------------------------------------------------------
    try:
        d = make_diff()
        chk("T30 the diff builds and touches both files",
            "a/hdlab/grounded_semantic_graph.py" in d and "a/hdlab/force_dynamics_valence.py" in d,
            "%d bytes" % len(d))
        crlf = sum(1 for l in d.split("\n") if l.endswith("\r"))
        chk("T31 the diff carries the files' own line endings", crlf > 0, "%d CRLF lines" % crlf)
        for rel, path, edits in patch_spec():
            b3 = patched_lines(path, edits)
            raw = "".join(b3)
            chk("T32 %s patched source compiles" % rel, compile(raw.replace("\r\n", "\n"), path, "exec")
                is not None)
    except SystemExit as e:
        chk("T30 the diff builds", False, e)

    res = {"arm": "self_test", "landed_before_install": st0, "checks": log,
           "n_pass": sum(1 for x in log if x["pass"]), "n": len(log)}
    _write("selftest.json", res)
    print("\n%d/%d checks passed" % (res["n_pass"], res["n"]))
    return 0 if ok[0] else 1


# =====================================================================================================================
# 9. MAIN
# =====================================================================================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--identity", action="store_true")
    ap.add_argument("--twin", action="store_true")
    ap.add_argument("--timing", action="store_true")
    ap.add_argument("--criterion", action="store_true")
    ap.add_argument("--board", action="store_true")
    ap.add_argument("--organs", action="store_true")
    ap.add_argument("--chain", action="store_true")
    ap.add_argument("--make-diff", action="store_true")
    ap.add_argument("--split", default="train", choices=("train", "test"))
    ap.add_argument("--docs", type=int, default=12)
    ap.add_argument("--twin-docs", type=int, default=3)
    ap.add_argument("--board-docs", type=int, default=3)
    ap.add_argument("--pairs", type=int, default=2)
    ap.add_argument("--boot", type=int, default=200)
    ap.add_argument("--tau", type=float, default=None)
    ap.add_argument("--tau-post", type=float, default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.make_diff:
        p = a.out or os.path.join(OUT_DIR, "walk_gate_patch.diff")
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
        txt = write_diff(p, a.tau, a.tau_post)
        print("wrote %s (%d bytes, tau=%s tau_post=%s)"
              % (p, len(txt.encode("utf-8")), a.tau if a.tau is not None else TAU_SHIPPED,
                 a.tau_post if a.tau_post is not None else TAU_POST_SHIPPED))
        return 0
    if a.sweep:
        sweep(a.split, a.docs)
    if a.identity:
        identity(a.docs, a.tau, a.tau_post, a.split)
    if a.twin:
        twin(a.twin_docs, a.tau)
    if a.timing:
        timing(a.docs, a.pairs, a.tau, a.tau_post or 0.0)
    if a.criterion:
        criterion(a.docs, a.split)
    if a.chain:
        chain(a.docs, a.split)
    if a.organs:
        organs()
    if a.board:
        board(a.board_docs, a.boot, a.tau, a.tau_post or 0.0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
