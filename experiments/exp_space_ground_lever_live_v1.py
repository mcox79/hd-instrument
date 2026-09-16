"""exp_space_ground_lever_live_v1 -- measure the NAMED-GROUND lever WHERE IT ACTUALLY RUNS, and the entity-file
hand-off that decides whether its output survives.

problem: the_live_space_readers_named_ground_lever_has_been_unmeasured_since_the_organ_was_promoted... (pri 137)

THE DEFECT THIS CELL MEASURES AROUND. `verification/test_space_ground_binding.py` W4 switches the lever off by
stubbing `experiments._space_reader.ground_bind_events` -- a function in the COPY the live reader stopped running at
the 2026-09-09 promotion (`hdlab/situation_reader.py::_read_space` imports `hdlab.space_reader`). Both W4 arms
therefore run the lever ON, so ON == OFF by construction. This cell stubs the module the reader REALLY calls.

WHAT IT MEASURES (every arm is a FULL live read -- SituationReader(...).read(cp).locations, never a private driver):
  A. THE LEVER, ON THE HISTORICAL WEAK READER (the config W4 uses: all_capabilities_off(track_space=True)),
     queried by the gold protagonist id "0" -- the exact W4 measurement, with the stub on the LIVE module.
  B. THE LEVER, ON THE PRODUCT READER (SituationReader() default flags -- what the board actually runs), queried
     by the file the reader itself put the protagonist in (gold cluster ids are read ONLY to align the question to
     the reader's own file, AFTER every decision -- never inside one).
  C. THE ENTITY-FILE HAND-OFF. The spatial dimension indexes place BY ENTITY FILE (hippocampal binding of an
     agent to a place; Zwaan & Radvansky event-indexing). `_read_space` receives the reader's own mention stream
     (pri 125) in which every PRONOUN carries a different file id from its own antecedent -- the reader resolves
     those pronouns at `_read_entities` (which runs BEFORE `_read_space`) and then discards the resolution at this
     hand-off. ONE-FILE arm = apply the reader's OWN resolutions to the stream (Heim 1982 file change: a pronoun
     updates the antecedent's card, it does not open a new one).
  FLOOR: the stateless last-mention place floor, recomputed on THIS population.
  TWINS: (1) shuffled-GROUND (the landed twin, `ground_bind_events(shuffle_rng=...)`) -- keeps the firing, destroys
  the ground content; (2) RANDOM-MERGE -- collapses the same number of files as the one-file arm but picks the
  target file at random, so "fewer files" alone cannot explain a gain.

Glass-box, deterministic, ASCII, CPU-only, NO spaCy / NO LLM at inference. Writes ONLY its own data dir.
Run:  .venv/Scripts/python.exe experiments/exp_space_ground_lever_live_v1.py            # FULL (bare == full)
      .venv/Scripts/python.exe experiments/exp_space_ground_lever_live_v1.py --smoke    # 3 passages, weak reader
      .venv/Scripts/python.exe experiments/exp_space_ground_lever_live_v1.py --self-test
"""
from __future__ import annotations

import json
import os
import sys
import time

os.environ.setdefault("PYTHONHASHSEED", "0")
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np                                                          # noqa: E402

from hdlab import space_reader as LIVE                                      # noqa: E402
from hdlab.situation_reader import SituationReader                          # noqa: E402
from hdlab.coref import parse_litbank_conll                                 # noqa: E402
from experiments.exp_space_where_is_end_to_end_v1 import (                  # noqa: E402
    gold_at, correct, floor_lastment, _place_positions, _mention_gidx)
import experiments.exp_space_where_is_modern_v1 as MOD                      # noqa: E402
from hdlab.scene_segment import parse_conll_sentences                       # noqa: E402

ANCHOR = "space_ground_lever_live_v1"
SEED = 20260916
ONE_FILE_ENV = "HDLAB_SPACE_ONE_FILE"      # the patch's switch; "0" forces the pre-repair hand-off


def get_output_dir(default_name: str = ANCHOR) -> str:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = os.path.join(_REPO, "data", "exp_%s" % name)
    os.makedirs(d, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# the ONE-FILE hand-off (measured here; proposed as hdlab.situation_reader.unify_entity_files)
# ---------------------------------------------------------------------------
def _unify_local(mentions, resolutions, rng=None, all_files=None):
    """Return (mentions_with_one_file_per_referent, n_links). The union target is the ANTECEDENT's file, so the
    root of every merged set is the card the reader itself named (`CorefResolution.resolved_entity` stays a valid
    register key). rng is not None -> the RANDOM-MERGE TWIN: the same number of unions, target chosen at random
    from `all_files`, i.e. the structure with the information removed."""
    par = {}

    def find(x):
        par.setdefault(x, x)
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    def uni(pron_file, ante_file):
        a, b = find(pron_file), find(ante_file)
        if a != b:
            par[a] = b          # the pronoun's file is filed UNDER the antecedent's

    by_pos = {(m["sent_idx"], m["wtok_start"]): m for m in mentions}
    by_head = {}
    for m in mentions:
        if m.get("is_pronoun"):
            by_head.setdefault((m["sent_idx"], str(m["head"]).lower()), []).append(m)
    n_links = 0
    for r in (resolutions or []):
        rc = getattr(r, "resolved_entity", None)
        if rc is None:
            rc = getattr(r, "resolved_cluster", None)
        if rc is None:
            continue
        pm = by_pos.get((r.sent_idx, int(getattr(r, "target_wpos", -1) or -1)))
        # pri 125 fills target_wpos only on the discovered-pronoun path; fall back to the pronoun's own head
        # in its own sentence (the coref-column path), never across sentences.
        cands = ([pm] if (pm is not None and pm.get("is_pronoun"))
                 else by_head.get((r.sent_idx, str(r.pronoun or "").lower()), []))
        for m in cands:
            tgt = rc if rng is None else int(rng.choice(all_files))
            uni(m["cluster"], tgt)
            n_links += 1
    return [dict(m, cluster=find(m["cluster"])) for m in mentions], n_links


def unify_impl():
    """The LANDED implementation when the patch is on the tree, else this cell's own copy. Reported as
    `unify_provenance` so a number can never be read as measuring code that is not shipped."""
    from hdlab import situation_reader as SR
    fn = getattr(SR, "unify_entity_files", None)
    if callable(fn):
        return fn, "landed:hdlab.situation_reader.unify_entity_files"
    return _unify_local, "cell-local (patch not on the tree)"


def install_as_landed():
    """Emulate `notes/problems/<pri137 slug>/space_ground_lever_patch.diff` IN-PROCESS -- the sys.modules alias for
    the promoted-away copy, the module-level join, and the env-gated call inside `_read_space` -- so this cell and
    the REPINNED witness can be shown GREEN ON THE TREE AS LANDED without a solver writing hdlab/ (Q111). Every
    installed object is the patch's own source; nothing here is a measurement short-cut, and `landed_state()`
    reports the result so no arm can be read as measuring code that is not shipped."""
    import experiments
    from hdlab import situation_reader as SR
    sys.modules["experiments._space_reader"] = LIVE          # the shim: one organ, one module object
    setattr(experiments, "_space_reader", LIVE)
    SR.unify_entity_files = _unify_local                     # the patch's pure join
    SR.SPACE_ONE_FILE_ENV = ONE_FILE_ENV
    _orig_rs = SR.SituationReader._read_space
    _orig_re = SR.SituationReader._read_entities

    def _re(slf, mentions, targets, n_sents, coarg=None):
        out = _orig_re(slf, mentions, targets, n_sents, coarg=coarg)
        slf._as_landed_res = out[0]                          # == what the patched call site passes (sm.coref_resolutions)
        return out

    def _read_space(slf, conll_path, mentions=None, resolutions=None):
        if resolutions is None:
            resolutions = getattr(slf, "_as_landed_res", None)
        if mentions is not None and os.environ.get(ONE_FILE_ENV, "1") != "0":
            mentions, slf._space_one_file_links = SR.unify_entity_files(mentions, resolutions)
        slf._space_stream = slf._pri137_stream = mentions
        return _orig_rs(slf, conll_path, mentions=mentions)

    SR.SituationReader._read_space = _read_space
    SR.SituationReader._read_entities = _re
    return landed_state()


# ---------------------------------------------------------------------------
# the measurement harness: every arm is a full live read
# ---------------------------------------------------------------------------
class Harness:
    """Installs the arm switches around SituationReader.read and scores where_is on the modern gold."""

    def __init__(self, passages, as_landed=None):
        self.passages = passages
        # as_landed: the ONE-FILE join is performed by the reader itself (landed or emulated), so the harness must
        # only flip the switch, never apply the join a second time.
        self.as_landed = (landed_state()["unify_landed"] if as_landed is None else bool(as_landed))
        self.cdir = os.path.join(get_output_dir(), "conll")
        os.makedirs(self.cdir, exist_ok=True)
        self.unify, self.unify_provenance = unify_impl()
        self._orig_gb = LIVE.ground_bind_events
        self._orig_rs = SituationReader._read_space
        self._orig_re = SituationReader._read_entities
        self.counts = {"gb_calls": 0, "gb_clauses": 0, "gb_events": 0}
        hz = self

        def _re(slf, mentions, targets, n_sents, coarg=None):
            out = hz._orig_re(slf, mentions, targets, n_sents, coarg=coarg)
            slf._pri137_res = out[0]
            return out
        SituationReader._read_entities = _re

    # -- the two levers -----------------------------------------------------
    def _ground(self, mode):
        """mode: 'on' | 'off' | 'twin' | 'asis' (leave whatever the caller installed -- used by the self-test to
        prove that a stub on the OTHER module name reaches, or does not reach, the organ)."""
        hz = self
        if mode == "asis":
            return
        if mode == "on":
            def gb(*a, **k):
                hz.counts["gb_calls"] += 1
                hz.counts["gb_clauses"] += len(a[0]) if a else 0
                ev = hz._orig_gb(*a, **k)
                hz.counts["gb_events"] += len(ev)
                return ev
            LIVE.ground_bind_events = gb
        elif mode == "off":
            LIVE.ground_bind_events = (lambda *a, **k: [])
        elif mode == "twin":
            def gb_twin(*a, **k):
                k = dict(k)
                k["shuffle_rng"] = np.random.default_rng(SEED + 7)
                return hz._orig_gb(*a, **k)
            LIVE.ground_bind_events = gb_twin
        else:
            raise ValueError(mode)

    def _onefile(self, mode):
        """mode: 'off' | 'on' | 'twin'. Installs a _read_space wrapper that rewrites the stream and records it."""
        hz = self

        def _rs(slf, conll_path, mentions=None, **kw):
            res = getattr(slf, "_pri137_res", None) or getattr(slf, "_as_landed_res", None)
            passed = mentions
            if mentions is not None and mode == "twin":
                files = sorted({m["cluster"] for m in mentions if not m.get("is_pronoun")}) or \
                        sorted({m["cluster"] for m in mentions})
                passed, n = hz.unify(mentions, res, rng=np.random.default_rng(SEED + 11), all_files=files)
                hz.last_links = n
            elif mentions is not None and mode == "on" and not hz.as_landed:
                passed, n = hz.unify(mentions, res)     # the patch is not on the tree: apply it here
                hz.last_links = n
            # ALIGNMENT STREAM: what the reader's space dimension actually receives. When the join is the READER's
            # (landed or emulated) the harness recomputes it for alignment only -- it never passes it in twice.
            slf._pri137_stream = (hz.unify(mentions, res)[0] if (mode == "on" and hz.as_landed and
                                                                 mentions is not None) else passed)
            return hz._orig_rs(slf, conll_path, mentions=passed)
        SituationReader._read_space = _rs
        # the landed patch reads its own switch: ON only for the 'on' arm, so 'off' is the pre-repair hand-off and
        # 'twin' is the random-merge control rather than random-merge-on-top-of-the-repair.
        os.environ[ONE_FILE_ENV] = "1" if mode == "on" else "0"

    def restore(self):
        LIVE.ground_bind_events = self._orig_gb
        SituationReader._read_space = self._orig_rs
        os.environ.pop(ONE_FILE_ENV, None)

    # -- one arm ------------------------------------------------------------
    def run_arm(self, config, ground, onefile, query):
        """config: 'weak'|'product'; query: 'gold' (ask by gold id "0") | 'aligned' (ask by the reader's own file).
        Returns (items, info). items = [{tl_key, t, pred, gold_node}] paired across arms by (passage, t)."""
        self.counts = {"gb_calls": 0, "gb_clauses": 0, "gb_events": 0}
        self.last_links = 0
        self._ground(ground)
        self._onefile(onefile)
        items, files_per_protagonist, links = [], [], []
        try:
            for p in self.passages:
                cp = MOD.write_conll(p, self.cdir)
                rows = sorted(MOD.build_gold(p), key=lambda r: r["t"])
                gold_m, _ = parse_litbank_conll(cp)
                rd = (SituationReader.all_capabilities_off(track_space=True) if config == "weak"
                      else SituationReader())
                reg = rd.read(cp).locations
                stream = {(m["sent_idx"], m["wtok_start"]): m["cluster"]
                          for m in (getattr(rd, "_pri137_stream", None)
                                    or getattr(rd, "_space_stream", None) or [])}
                links.append(getattr(self, "last_links", 0))
                # ALIGNMENT (gold read AFTER every decision): which file did the reader put the protagonist's
                # mentions in? The count of distinct answers IS the fragmentation number.
                cand = {}
                for m in gold_m:
                    if m["cluster"] == 0:
                        c = stream.get((m["sent_idx"], m["wtok_start"]))
                        if c is not None:
                            cand[c] = cand.get(c, 0) + 1
                files_per_protagonist.append(len(cand))
                rep = (max(cand.items(), key=lambda kv: (kv[1], -abs(kv[0])))[0] if cand else 0)
                key = "0" if query == "gold" else str(rep)
                sents = parse_conll_sentences(cp, lower=False)
                places = _place_positions(sents)
                f, l = rows[0]["t"], rows[-1]["t"] + 20
                for t in sorted({m["sent_idx"] for m in gold_m
                                 if m["cluster"] == 0 and f <= m["sent_idx"] <= l}):
                    g = gold_at(rows, t)
                    if g is None:
                        continue
                    items.append({"tl_key": p[0], "t": t, "pred": reg.where_is(key, t), "gold_node": g[0],
                                  "floor": floor_lastment(places, _mention_gidx(sents, gold_m, 0, t), t)})
        finally:
            self.restore()
        info = {"config": config, "ground": ground, "onefile": onefile, "query": query,
                "acc": _acc(items, "pred"), "n": len(items),
                "files_per_protagonist": files_per_protagonist,
                "one_file_links": links, "ground_bind": dict(self.counts)}
        return items, info


def _acc(items, field):
    xs = [correct(it[field], it["gold_node"]) for it in items]
    return float(np.mean(xs)) if xs else 0.0


def boot(items_a, items_b, field_a="pred", field_b="pred", n_boot=2000, seed=SEED, unit="item"):
    """Paired bootstrap of (acc_a - acc_b) over ITEMS or over TIMELINES (passages). Arms are paired by
    (tl_key, t); a missing pair is a defect, not a drop."""
    ka = [(it["tl_key"], it["t"]) for it in items_a]
    kb = [(it["tl_key"], it["t"]) for it in items_b]
    assert ka == kb, "arms are not item-paired"
    a = np.array([correct(it[field_a], it["gold_node"]) for it in items_a], dtype=float)
    b = np.array([correct(it[field_b], it["gold_node"]) for it in items_b], dtype=float)
    rng = np.random.default_rng(seed)
    delta = float(a.mean() - b.mean())
    if unit == "item":
        idx = np.arange(len(a))
        draws = [float(a[s].mean() - b[s].mean())
                 for s in (rng.choice(idx, size=len(idx), replace=True) for _ in range(n_boot))]
    else:
        keys = sorted({k[0] for k in ka})
        pos = {k: [i for i, kk in enumerate(ka) if kk[0] == k] for k in keys}
        kk = np.array(keys)
        draws = []
        for _ in range(n_boot):
            s = rng.choice(kk, size=len(kk), replace=True)
            ii = [i for k in s for i in pos[k]]
            draws.append(float(a[ii].mean() - b[ii].mean()))
    lo, hi = float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))
    return {"unit": unit, "a_mean": float(a.mean()), "b_mean": float(b.mean()), "delta": delta,
            "lo": lo, "hi": hi, "CI_sep": bool(lo > 0), "n": int(len(a))}


# ---------------------------------------------------------------------------
def run(smoke=False, n_boot=2000):
    t0 = time.time()
    passages = MOD.PASSAGES[:3] if smoke else MOD.PASSAGES
    hz = Harness(passages)
    out = {"anchor_name": ANCHOR, "run_mode": "smoke" if smoke else "full", "seed": SEED,
           "n_passages": len(passages), "unify_provenance": hz.unify_provenance,
           "landed_state": landed_state(), "arms": {}, "gates": {}}

    def arm(name, *a, **k):
        items, info = hz.run_arm(*a, **k)
        out["arms"][name] = info
        print("  %-28s acc %.4f  n=%d  files/protagonist=%s  gb(calls=%d clauses=%d events=%d)"
              % (name, info["acc"], info["n"], info["files_per_protagonist"], info["ground_bind"]["gb_calls"],
                 info["ground_bind"]["gb_clauses"], info["ground_bind"]["gb_events"]))
        return items

    # -- A. THE WITNESS POPULATION (weak reader, gold id) -- the W4 measurement, on the LIVE module -----
    print("[A] weak reader (the W4 config), stub on the LIVE module, gold id '0':")
    a_on = arm("weak/ground=on", "weak", "on", "off", "gold")
    a_off = arm("weak/ground=off", "weak", "off", "off", "gold")
    a_twin = arm("weak/ground=twin", "weak", "twin", "off", "gold")
    a_one = arm("weak/ground=on+onefile", "weak", "on", "on", "aligned")
    for tag, x, y, fa, fb in (("lever_vs_off_item", a_on, a_off, "pred", "pred"),
                              ("lever_vs_off_tl", a_on, a_off, "pred", "pred"),
                              ("lever_vs_floor_item", a_on, a_on, "pred", "floor"),
                              ("lever_vs_twin_item", a_on, a_twin, "pred", "pred"),
                              ("onefile_vs_asis_item", a_one, a_on, "pred", "pred")):
        out["gates"][tag] = boot(x, y, fa, fb, n_boot=n_boot, unit=("tl" if tag.endswith("_tl") else "item"))

    if not smoke:
        # -- B. THE PRODUCT READER (default flags) -- what the board actually runs -------------------
        print("[B] PRODUCT reader (default flags), query = the reader's OWN file for the protagonist:")
        p_on = arm("product/ground=on", "product", "on", "off", "aligned")
        p_off = arm("product/ground=off", "product", "off", "off", "aligned")
        p_on1 = arm("product/ground=on+onefile", "product", "on", "on", "aligned")
        p_off1 = arm("product/ground=off+onefile", "product", "off", "on", "aligned")
        p_tw1 = arm("product/ground=twin+onefile", "product", "twin", "on", "aligned")
        p_rnd = arm("product/ground=on+mergetwin", "product", "on", "twin", "aligned")
        out["gates"]["product_lever_at_onefile_item"] = boot(p_on1, p_off1, n_boot=n_boot)
        out["gates"]["product_lever_at_onefile_tl"] = boot(p_on1, p_off1, n_boot=n_boot, unit="tl")
        out["gates"]["product_lever_asis_item"] = boot(p_on, p_off, n_boot=n_boot)
        out["gates"]["product_onefile_item"] = boot(p_on1, p_on, n_boot=n_boot)
        out["gates"]["product_onefile_tl"] = boot(p_on1, p_on, n_boot=n_boot, unit="tl")
        out["gates"]["product_onefile_vs_mergetwin_item"] = boot(p_on1, p_rnd, n_boot=n_boot)
        out["gates"]["product_ground_vs_groundtwin_item"] = boot(p_on1, p_tw1, n_boot=n_boot)
        out["gates"]["product_best_vs_floor_item"] = boot(p_on1, p_on1, "pred", "floor", n_boot=n_boot)

    out["elapsed_s"] = round(time.time() - t0, 1)
    d = get_output_dir()
    with open(os.path.join(d, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    return out


def landed_state():
    """Detect, from the LIVE modules, which parts of the pri-137 patch are on this tree."""
    import experiments._space_reader as OLD
    from hdlab import situation_reader as SR
    return {"one_organ": bool(OLD is LIVE),
            "old_module_file": getattr(OLD, "__file__", None),
            "live_module_file": getattr(LIVE, "__file__", None),
            "unify_landed": callable(getattr(SR, "unify_entity_files", None))}


def _print(o):
    print("\n[LEVER, LIVE MODULE] %s  n_passages=%d  unify=%s" % (o["run_mode"], o["n_passages"],
                                                                 o["unify_provenance"]))
    print("  landed_state:", o["landed_state"])
    for k, v in o["arms"].items():
        print("   %-28s %.4f (n=%d)" % (k, v["acc"], v["n"]))
    for k, g in o["gates"].items():
        print("   %-34s %.4f vs %.4f  delta %+.4f CI[%+.4f,%+.4f] sep=%s (%s, n=%d)"
              % (k, g["a_mean"], g["b_mean"], g["delta"], g["lo"], g["hi"], g["CI_sep"], g["unit"], g["n"]))


def self_test():
    """Scaffold-free invariants. Every check is a CLAIM (a direction / an invariant), never a pinned number, and
    the state-dependent check asserts the DEFECT'S ABSENCE once the patch is landed."""
    st = landed_state()
    print("[self-test] landed_state:", st)
    import experiments._space_reader as OLD
    hz = Harness(MOD.PASSAGES[:2])
    on, _i = hz.run_arm("weak", "on", "off", "gold")
    off, _j = hz.run_arm("weak", "off", "off", "gold")
    a_on, a_off = _acc(on, "pred"), _acc(off, "pred")
    assert a_on > a_off, ("the named-ground lever must MOVE where-is on the LIVE module", a_on, a_off)
    print("[self-test] 1 OK: stubbing the LIVE module moves where-is (%.4f -> %.4f)" % (a_off, a_on))

    # the two-copy defect: stubbing the DEAD copy must be a no-op BEFORE the patch and must bite AFTER it.
    orig = OLD.ground_bind_events
    try:
        OLD.ground_bind_events = (lambda *a, **k: [])
        stub_old, _k = hz.run_arm("weak", "asis", "off", "gold")
        a_stub_old = _acc(stub_old, "pred")
    finally:
        OLD.ground_bind_events = orig
    if st["one_organ"]:
        assert a_stub_old < a_on, ("ONE ORGAN: stubbing experiments._space_reader must now switch the live lever "
                                   "off", a_stub_old, a_on)
        print("[self-test] 2 OK (LANDED): the copy IS the organ -- stubbing it switches the live lever off "
              "(%.4f < %.4f); the W4 defect is ABSENT" % (a_stub_old, a_on))
    else:
        assert abs(a_stub_old - a_on) < 1e-12, ("PRE-PATCH: stubbing the dead copy must be a NO-OP (this is the "
                                                "defect W4 hides)", a_stub_old, a_on)
        print("[self-test] 2 OK (PRE-PATCH): stubbing the dead copy is a NO-OP (%.4f == %.4f) -- the W4 defect is "
              "PRESENT on this tree" % (a_stub_old, a_on))

    # the hand-off: the one-file repair must not INCREASE the number of files the protagonist is spread over.
    _m, i_asis = hz.run_arm("weak", "on", "off", "aligned")
    _n, i_one = hz.run_arm("weak", "on", "on", "aligned")
    assert all(x <= y for x, y in zip(i_one["files_per_protagonist"], i_asis["files_per_protagonist"])), \
        (i_one["files_per_protagonist"], i_asis["files_per_protagonist"])
    print("[self-test] 3 OK: the one-file hand-off never fragments (%s -> %s)"
          % (i_asis["files_per_protagonist"], i_one["files_per_protagonist"]))
    print("[self-test] unify provenance:", hz.unify_provenance)
    print("SELF-TEST GREEN")
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--as-landed", action="store_true", dest="as_landed",
                    help="emulate space_ground_lever_patch.diff in-process, then run as if it were landed")
    a = ap.parse_args()
    if a.as_landed:
        print("[as-landed] installed:", install_as_landed())
    if a.self_test:
        sys.exit(self_test())
    _print(run(smoke=a.smoke or a.mode == "smoke", n_boot=a.n_boot))
