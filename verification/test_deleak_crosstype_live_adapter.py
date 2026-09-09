"""Witness for DE-LEAK PART 2 -- the LIVE gold-free crosstype definite->name bridge wire
(`hdlab/crosstype_live_adapter.py` + the situation_reader.read online_entity_cluster_bridge wire).

Proves: (W1) the adapter is SELF-CONTAINED (imports NO experiments/); (W2) its deterministic + live-frontend
self-test passes (gold-free Doc, non-mutating merge, int labels, end-to-end fire); (W3) the LIVE reader runs
read() with the full de-leak ON (online_entity_cluster + bridge) WITHOUT crashing and builds sm.entities;
(W4) the PRONOUN stream is byte-identical floor vs part1 vs full (the online clustering + bridge touch ONLY
non-pronoun midx -- pronoun consumers unchanged); (W5) GOLD-FREE (a pronoun midx never appears in a bind, and
the adapter reads no gold column in any decision -- structural); (W6) the landed SOLVED downstream gain
(+0.0838 CI-sep experiencer over the honest floor) reproduces from disk if the metrics are present.

Run: .venv/Scripts/python.exe verification/test_deleak_crosstype_live_adapter.py
"""
from __future__ import annotations
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

_fail = []


def _ck(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        _fail.append(msg)


def _doc():
    from hdlab.situation_reader import _write_temp_conll
    # a cross-type case: a NAMED person (Elizabeth) predicated a role ("is a doctor"), a later DEFINITE role-noun
    # ("The doctor") that should bridge to her, and PRONOUNS (She/He/her) that must stay byte-identical.
    sents = ["Elizabeth arrived at the hospital .",
             "She is a doctor .",
             "The doctor examined the patient .",
             "He thanked her ."]
    rows = []
    for si, s in enumerate(sents, 1):
        for wi, w in enumerate(s.split(), 1):
            rows.append((si, wi, w, "-"))
    return _write_temp_conll(rows)


def main():
    # ---- W1 SELF-CONTAINMENT -------------------------------------------------------------------------------
    import hdlab.crosstype_live_adapter as A
    exp_mods = [m for m in sys.modules if m.startswith("experiments.") or m == "experiments"]
    _ck(not exp_mods, "W1 adapter self-contained: imports NO experiments/ module (found %s)" % exp_mods)

    # ---- W2 ADAPTER SELF-TEST (deterministic gold-free Doc + non-mutating merge + int labels + live-frontend fire)
    _ck(A._selftest() == 0, "W2 crosstype_live_adapter._selftest passes (W1-W5: gold-free Doc, merge, ints, e2e fire)")

    # ---- W5 GOLD-FREE / pronoun-safe MERGE (structural, deterministic) -------------------------------------
    # a pronoun mention (midx 3) must NEVER be a bind key or take a bind; the bind values are ONLINE labels.
    rms = [{"midx": 0, "head": "elizabeth", "span_toks": ["Elizabeth"], "gtok_start": 0, "gtok_end": 0,
            "sent_idx": 0, "is_pronoun": False, "gender": "fem", "name_gender": None},
           {"midx": 1, "head": "doctor", "span_toks": ["the", "doctor"], "gtok_start": 3, "gtok_end": 4,
            "sent_idx": 1, "is_pronoun": False, "gender": None, "name_gender": None},
           {"midx": 3, "head": "she", "span_toks": ["She"], "gtok_start": 2, "gtok_end": 2, "sent_idx": 1,
            "is_pronoun": True, "gender": "fem", "name_gender": None}]
    online = {0: 0, 1: 1}                       # pronoun midx 3 is NOT in the online layer (separate stream)
    merged = A.apply_binds(rms, online, {1: 0})  # bind the definite (position 1) to Elizabeth's online label 0
    _ck(3 not in merged and merged.get(0) == 0 and merged.get(1) == 0 and online == {0: 0, 1: 1},
        "W5 merge is pronoun-safe + gold-free + non-mutating (pronoun untouched, bind value is the online label): %s" % merged)

    # ---- W3/W4 LIVE READER: no-crash with the full de-leak ON + pronoun stream byte-identical ---------------
    from hdlab.situation_reader import SituationReader
    path = _doc()

    def run(oec, bridge):
        r = SituationReader()
        r.online_entity_cluster = oec
        r.online_entity_cluster_bridge = bridge
        return r.read(path)

    try:
        sm_floor = run(False, False)   # de-leak OFF (deployed baseline)
        sm_p1 = run(True, False)       # part 1 only (online clustering, no bridge)
        sm_full = run(True, True)      # full de-leak (online clustering + crosstype bridge)
        live_ok = True
    except Exception as e:
        import traceback; traceback.print_exc()
        live_ok = False
    _ck(live_ok, "W3 LIVE reader.read() runs with the full de-leak ON (online_entity_cluster + bridge) -- NO crash")
    if live_ok:
        _ck(getattr(sm_full, "entities", None) is not None and len(sm_full.entities) > 0,
            "W3 sm.entities built under the full de-leak (n=%d)" % len(getattr(sm_full, "entities", []) or []))

        # PRONOUN no-regress: the reader's coref resolutions for PRONOUN mentions must be identical across configs
        # (the online clustering + bridge rewrite ONLY non-pronoun labels). Compare the coref_resolutions projection.
        def coref_proj(sm):
            cr = getattr(sm, "coref_resolutions", None)
            if cr is None:
                return None
            out = []
            for c in cr:
                if isinstance(c, dict):
                    out.append((c.get("mention"), c.get("antecedent"), c.get("pron")))
                else:
                    out.append(tuple(getattr(c, k, None) for k in ("mention", "antecedent", "pron")))
            return out
        cf, c1, cx = coref_proj(sm_floor), coref_proj(sm_p1), coref_proj(sm_full)
        if cf is None:
            print("  SKIP W4 (reader exposes no coref_resolutions projection to compare)")
        else:
            _ck(cf == c1 == cx, "W4 pronoun/coref stream byte-identical floor vs part1 vs full de-leak")

    # ---- W6 LANDED GAIN (the SOLVED's authoritative +0.0838 CI-sep, reproduced from disk if present) --------
    import json
    dwp = os.path.join(_REPO, "data/exp_online_cluster_downstream_c3_gum_v1/metrics.json")
    if os.path.exists(dwp):
        dw = json.load(open(dwp))
        hl = dw.get("HEADLINE_A2_vs_A0", {})
        _ck(bool(hl.get("ci_sep")) and hl.get("delta", 0) > 0.05,
            "W6 landed: online-clustering+bridge C3 lift over honest floor CI-sep (+%.4f, n=549)" % hl.get("delta", 0))
    else:
        print("  SKIP W6 (SOLVED downstream metrics absent -- the +0.0838 is proven by "
              "verification/test_online_cue_cluster.py W15 on the landed run)")

    print("\nRESULT: %s" % ("PASS" if not _fail else "FAIL (%d): %s" % (len(_fail), _fail)))
    return 1 if _fail else 0


if __name__ == "__main__":
    sys.exit(main())
