"""Checker over EXISTING results: declared-vs-realised condition mismatches.

Companion to realised_condition.py (the convention going forward). This script audits what is
ALREADY on disk under data/, most of which predates the convention and therefore has no
realised_* fields at all -- that absence is itself the headline number this script reports.

For each data/<cell>/metrics.json, it:
  1. Parses the DIRECTORY NAME for scale/size/seed/model tokens (N12345, kb500k, 3seed, a known
     model substring) -- this is the "declared condition".
  2. Looks for a REALISED value to compare it against, in priority order:
       a. an explicit realised_<field> written per the new convention (best case -- proves the
          convention is in force here),
       b. a same-named config/summary field (config.N, top-level n_seeds, len(per_seed)) --
          this is what actually caught both confirmed incidents tonight, since neither predates
          the convention,
       c. for the kb-sweep shape specifically, a DERIVED realised proxy: n_train + n_test off
          the SAME arithmetic the incident's author used by hand (149 + 100 = 249, matching
          N_FACTS in config only by coincidence of upper-bounding a fixed pool).
  3. Classifies the cell as: no-condition-declared / declared-but-unrecoverable /
     declared-and-matches / declared-and-MISMATCHES (with a smoke-disclosure flag on the last).

Reports a PROPORTION, not a pile: N cells scanned, how many declare a condition, how many carry
ANY realised_ field, how many of the declaring cells are checkable at all, and of those, how
many mismatch and how many mismatches are disclosed via run_mode/config.mode == "smoke".

Usage:
    .venv/Scripts/python.exe tools/realised_condition_checker.py [--data-dir DIR] [--limit N]
    .venv/Scripts/python.exe tools/realised_condition_checker.py --self-test
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import json
import re
import sys

REPO = "D:/AI/hd-instrument"
DEFAULT_DATA_DIR = os.path.join(REPO, "data")

MODEL_TOKENS = [
    "pythia-160m", "pythia-1.4b", "pythia-1p4b", "pythia1p4b",
    "pythia-2.8b", "pythia-2p8b", "pythia2p8b", "pythia2.8b",
    "qwen2.5-1.5b", "qwen1p5b", "qwen1.5b", "qwen",
    "gpt2", "bert", "bge-small", "bgesmall",
]

CONFIG_SCALE_KEYS = ("N", "N_FACTS", "n_seeds", "M", "MODEL", "model", "K", "scale", "size")

_N_RE = re.compile(r"[_-][Nn](\d{3,})(?:[_-]|$)")
_SEED_RE = re.compile(r"(\d+)seed")
# NOTE: no \b around "kb" -- underscore is a word character (CLAUDE.md evidence-discipline
# note), so "_kb500k_" has no \w/\W transition before "kb" and \b would silently miss it.
_KB_RE = re.compile(r"kb(\d+)([km]?)(?![0-9a-z])", re.IGNORECASE)


def _get(d, *keys):
    """Walk nested dict access, return None on any miss."""
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def _realised_fields(metrics):
    out = {}
    if isinstance(metrics, dict):
        for k, v in metrics.items():
            if isinstance(k, str) and k.startswith("realised_"):
                out[k] = v
        summ = metrics.get("summary")
        if isinstance(summ, dict):
            for k, v in summ.items():
                if isinstance(k, str) and k.startswith("realised_"):
                    out["summary." + k] = v
    return out


def _is_smoke(metrics, name=None):
    """Is the smoke/full mode disclosed anywhere recoverable? Checked several spellings after
    an over-firing bug: the FIRST version of this function checked only run_mode and
    config.mode and produced 242 "UNDISCLOSED" mismatches, most of which were actually
    disclosed via summary.smoke=true or a top-level smoke=true boolean (neither config nor
    run_mode exists on those cells at all) -- e.g. data/exp_adaptive_cleanup_operator_v1_n4096_smoke
    has summary={"N": 1024, "smoke": true, ...} and no "config" key whatsoever. Re-measured
    after the fix: of a 60-mismatch sample, 55/60 carry an explicit smoke signal in one of
    these forms or the directory name itself; the fix moved them out of UNDISCLOSED."""
    if isinstance(metrics, dict):
        if str(metrics.get("run_mode", "")).lower() == "smoke":
            return True
        if metrics.get("smoke") is True:
            return True
        cfg = metrics.get("config")
        if isinstance(cfg, dict):
            if str(cfg.get("mode", "")).lower() == "smoke":
                return True
            if cfg.get("smoke") is True:
                return True
        summ = metrics.get("summary")
        if isinstance(summ, dict):
            if summ.get("smoke") is True:
                return True
            if str(summ.get("run_mode", "")).lower() == "smoke":
                return True
    if name and "smoke" in name.lower():
        return True
    return False


def name_tokens(name):
    """Extract declared-condition tokens from a directory name. Returns list of
    (kind, declared_value) tuples. kind in {"N", "seed", "kb_facts", "model"}."""
    toks = []
    m = _N_RE.search(name)
    if m:
        toks.append(("N", int(m.group(1))))
    m = _SEED_RE.search(name)
    if m:
        toks.append(("seed", int(m.group(1))))
    m = _KB_RE.search(name)
    if m:
        val = int(m.group(1))
        suf = m.group(2).lower()
        if suf == "k":
            val *= 1000
        elif suf == "m":
            val *= 1_000_000
        toks.append(("kb_facts", val))
    low = name.lower()
    for tok in MODEL_TOKENS:
        if tok in low:
            toks.append(("model", tok))
            break
    return toks


def config_declares(metrics):
    cfg = metrics.get("config") if isinstance(metrics, dict) else None
    if not isinstance(cfg, dict):
        return False
    return any(k in cfg for k in CONFIG_SCALE_KEYS)


def realised_value_for(kind, metrics):
    """Return (value, source_label) or (None, None) if unrecoverable."""
    rf = _realised_fields(metrics)
    if kind == "N":
        for k in ("realised_N", "realised_n"):
            if k in rf:
                return rf[k], "realised_field"
        v = _get(metrics, "config", "N")
        if v is not None:
            return v, "config.N"
        v = _get(metrics, "summary", "N")
        if v is not None:
            return v, "summary.N"
        v = metrics.get("N") if isinstance(metrics, dict) else None
        if v is not None:
            return v, "top.N"
        return None, None
    if kind == "seed":
        if "realised_n_seeds" in rf:
            return rf["realised_n_seeds"], "realised_field"
        v = metrics.get("n_seeds") if isinstance(metrics, dict) else None
        if v is not None:
            return v, "top.n_seeds"
        v = _get(metrics, "config", "n_seeds")
        if v is not None:
            return v, "config.n_seeds"
        ps = metrics.get("per_seed") if isinstance(metrics, dict) else None
        if isinstance(ps, list):
            return len(ps), "len(per_seed)"
        return None, None
    if kind == "kb_facts":
        if "realised_n_facts" in rf:
            return rf["realised_n_facts"], "realised_field"
        ntr = metrics.get("n_train") if isinstance(metrics, dict) else None
        nte = metrics.get("n_test") if isinstance(metrics, dict) else None
        if ntr is None:
            ntr = _get(metrics, "summary", "n_train")
        if nte is None:
            nte = _get(metrics, "summary", "n_test")
        if isinstance(ntr, (int, float)) and isinstance(nte, (int, float)):
            return int(ntr) + int(nte), "n_train+n_test (derived)"
        return None, None
    if kind == "model":
        if "realised_model" in rf:
            return str(rf["realised_model"]).lower(), "realised_field"
        for key in ("model", "MODEL", "model_name"):
            v = metrics.get(key) if isinstance(metrics, dict) else None
            if v is None:
                v = _get(metrics, "config", key)
            if v is not None:
                return str(v).lower(), "config/top." + key
        return None, None
    return None, None


def check_dir(name, metrics):
    """Return a dict summarising declared/realised/checkable/mismatch state for one cell."""
    toks = name_tokens(name)
    declared = bool(toks) or config_declares(metrics)
    has_realised_field = bool(_realised_fields(metrics))
    findings = []
    checkable = False
    any_mismatch = False
    for kind, decl_val in toks:
        rval, src = realised_value_for(kind, metrics)
        if rval is None:
            findings.append({"kind": kind, "declared": decl_val, "realised": None, "source": None,
                              "status": "unrecoverable"})
            continue
        checkable = True
        if kind == "model":
            match = decl_val in str(rval) or str(rval) in decl_val
        else:
            match = (rval == decl_val)
        status = "match" if match else "MISMATCH"
        if not match:
            any_mismatch = True
        findings.append({"kind": kind, "declared": decl_val, "realised": rval, "source": src,
                          "status": status})
    return {
        "name": name,
        "declared": declared,
        "has_realised_field": has_realised_field,
        "checkable": checkable,
        "mismatch": any_mismatch,
        "smoke_disclosed": _is_smoke(metrics, name) if any_mismatch else None,
        "findings": findings,
    }


def scan(data_dir=DEFAULT_DATA_DIR, limit=None):
    n_dirs = 0
    n_read = 0
    n_unreadable = 0
    n_declared = 0
    n_has_realised_field = 0
    n_checkable = 0
    n_mismatch = 0
    n_mismatch_disclosed = 0
    n_mismatch_undisclosed = 0
    mismatches = []

    with os.scandir(data_dir) as it:
        entries = [e for e in it if e.is_dir()]
    entries.sort(key=lambda e: e.name)
    if limit:
        entries = entries[:limit]

    for e in entries:
        n_dirs += 1
        mp = os.path.join(e.path, "metrics.json")
        if not os.path.isfile(mp):
            continue
        try:
            with open(mp, "r", encoding="utf-8") as fh:
                metrics = json.load(fh)
        except Exception:
            n_unreadable += 1
            continue
        n_read += 1
        r = check_dir(e.name, metrics)
        if r["declared"]:
            n_declared += 1
        if r["has_realised_field"]:
            n_has_realised_field += 1
        if r["checkable"]:
            n_checkable += 1
        if r["mismatch"]:
            n_mismatch += 1
            if r["smoke_disclosed"]:
                n_mismatch_disclosed += 1
            else:
                n_mismatch_undisclosed += 1
            mismatches.append(r)

    return {
        "data_dir": data_dir,
        "n_dirs": n_dirs,
        "n_metrics_read": n_read,
        "n_metrics_unreadable": n_unreadable,
        "n_declare_a_condition": n_declared,
        "n_carry_any_realised_field": n_has_realised_field,
        "n_checkable": n_checkable,
        "n_mismatch": n_mismatch,
        "n_mismatch_smoke_disclosed": n_mismatch_disclosed,
        "n_mismatch_UNDISCLOSED": n_mismatch_undisclosed,
        "mismatches": mismatches,
    }


def _selftest():
    # POSITIVE 1: confirmed n_seeds mismatch, real file on disk.
    p1 = os.path.join(REPO, "data", "exp_b2_self_improving_routing_3seed_cpu_v1", "metrics.json")
    with open(p1, encoding="utf-8") as fh:
        m1 = json.load(fh)
    r1 = check_dir("exp_b2_self_improving_routing_3seed_cpu_v1", m1)
    assert r1["declared"] is True, r1
    assert r1["checkable"] is True, r1
    assert r1["mismatch"] is True, r1
    seed_finding = [f for f in r1["findings"] if f["kind"] == "seed"][0]
    assert seed_finding["declared"] == 3 and seed_finding["realised"] == 1, seed_finding
    assert r1["smoke_disclosed"] is True, r1  # run_mode=smoke IS present -- disclosed, not hidden
    print("POSITIVE 1 (b2 3seed/n_seeds=1) PASS:", seed_finding)

    # POSITIVE 2: confirmed N mismatch, real file on disk (smoke variant, N65536 name vs config.N=4096).
    p2 = os.path.join(REPO, "data", "exp_wave14_betC_M_N_capacity_N65536_v1_smoke", "metrics.json")
    with open(p2, encoding="utf-8") as fh:
        m2 = json.load(fh)
    r2 = check_dir("exp_wave14_betC_M_N_capacity_N65536_v1_smoke", m2)
    assert r2["mismatch"] is True, r2
    n_finding = [f for f in r2["findings"] if f["kind"] == "N"][0]
    assert n_finding["declared"] == 65536 and n_finding["realised"] == 4096, n_finding
    assert r2["smoke_disclosed"] is True, r2
    print("POSITIVE 2 (betC N65536/config.N=4096) PASS:", n_finding)

    # POSITIVE 3 (synthetic, hermetic): the kb500k shape from the identical-across-models fragment.
    m3 = {"config": {"N_FACTS": 500000, "mode": "full"}, "n_train": 149, "n_test": 100,
          "run_mode": "full"}
    r3 = check_dir("exp_t5c_pp225_kb500k_v1", m3)
    kb_finding = [f for f in r3["findings"] if f["kind"] == "kb_facts"][0]
    assert kb_finding["declared"] == 500000 and kb_finding["realised"] == 249, kb_finding
    assert kb_finding["source"] == "n_train+n_test (derived)", kb_finding
    assert r3["mismatch"] is True and r3["smoke_disclosed"] is False, r3  # UNDISCLOSED -- this IS the incident
    print("POSITIVE 3 (kb500k synthetic, undisclosed) PASS:", kb_finding)

    # NEGATIVE 1: clean match, real file on disk (non-smoke N65536 cell).
    p4 = os.path.join(REPO, "data", "exp_wave14_betV_N65536_v1", "metrics.json")
    with open(p4, encoding="utf-8") as fh:
        m4 = json.load(fh)
    r4 = check_dir("exp_wave14_betV_N65536_v1", m4)
    assert r4["declared"] is True and r4["checkable"] is True and r4["mismatch"] is False, r4
    print("NEGATIVE 1 (betV N65536 clean match) PASS")

    # NEGATIVE 2: no condition asserted by name or config -- must not be flagged as declared.
    m5 = {"verdict": "PASS", "elapsed_s": 1.2, "summary": {"acc": 0.9}}
    r5 = check_dir("exp_baseline_sanity_v1", m5)
    assert r5["declared"] is False and r5["checkable"] is False and r5["mismatch"] is False, r5
    print("NEGATIVE 2 (no condition declared) PASS")

    # NEGATIVE 3: declares but genuinely unrecoverable -- must not be reported as a mismatch.
    m6 = {"verdict": "PASS"}
    r6 = check_dir("exp_something_3seed_v1", m6)
    assert r6["declared"] is True and r6["checkable"] is False and r6["mismatch"] is False, r6
    assert r6["findings"][0]["status"] == "unrecoverable", r6
    print("NEGATIVE 3 (declared, unrecoverable, not a false mismatch) PASS")

    # POSITIVE 4 / regression guard: the over-firing bug found while running this checker for
    # real. summary.smoke=true (no config, no run_mode) must be recognised as disclosure.
    p7 = os.path.join(REPO, "data", "exp_adaptive_cleanup_operator_v1_n4096_smoke", "metrics.json")
    with open(p7, encoding="utf-8") as fh:
        m7 = json.load(fh)
    assert "config" not in m7 and "run_mode" not in m7, "fixture assumption changed"
    assert _is_smoke(m7, "exp_adaptive_cleanup_operator_v1_n4096_smoke") is True, m7
    r7 = check_dir("exp_adaptive_cleanup_operator_v1_n4096_smoke", m7)
    assert r7["mismatch"] is True and r7["smoke_disclosed"] is True, r7
    print("POSITIVE 4 (summary.smoke=true regression guard) PASS")

    # NEGATIVE 4: a mismatch with NO smoke signal anywhere must still read as UNDISCLOSED --
    # the fix must not blanket-suppress every mismatch.
    m8 = {"config": {"N": 512}, "summary": {"N": 512}}
    r8 = check_dir("exp_fictitious_n4096_v1", m8)
    assert r8["mismatch"] is True and r8["smoke_disclosed"] is False, r8
    print("NEGATIVE 4 (genuine undisclosed mismatch still fires) PASS")

    print("\nrealised_condition_checker selftest: 8/8 PASS (4 positive incl. 2 real on-disk "
          "cells + 1 synthetic incident replay + 1 real regression fixture, 4 negative)")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Declared-vs-realised condition checker")
    ap.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--json-out", default=None, help="write full result JSON here")
    args = ap.parse_args()

    if args.self_test:
        _selftest()
        sys.exit(0)

    result = scan(args.data_dir, args.limit)
    print("=== realised-condition checker ===")
    print("data dir scanned:        %s" % result["data_dir"])
    print("top-level dirs:          %d" % result["n_dirs"])
    print("metrics.json read:       %d  (unreadable: %d)" % (result["n_metrics_read"], result["n_metrics_unreadable"]))
    print("declare a condition:     %d  (%.1f%% of read)" % (
        result["n_declare_a_condition"], 100.0 * result["n_declare_a_condition"] / max(1, result["n_metrics_read"])))
    print("carry ANY realised_ field: %d  (%.1f%% of read; %.1f%% of declaring)" % (
        result["n_carry_any_realised_field"],
        100.0 * result["n_carry_any_realised_field"] / max(1, result["n_metrics_read"]),
        100.0 * result["n_carry_any_realised_field"] / max(1, result["n_declare_a_condition"])))
    print("checkable (declared value recoverable): %d  (%.1f%% of declaring)" % (
        result["n_checkable"], 100.0 * result["n_checkable"] / max(1, result["n_declare_a_condition"])))
    print("MISMATCHES among checkable: %d  (%.1f%% of checkable)" % (
        result["n_mismatch"], 100.0 * result["n_mismatch"] / max(1, result["n_checkable"])))
    print("  smoke-disclosed:   %d" % result["n_mismatch_smoke_disclosed"])
    print("  UNDISCLOSED:       %d" % result["n_mismatch_UNDISCLOSED"])

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, default=str)
        print("\nfull result written to %s" % args.json_out)
