# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate: source_direct resolved-flags vs scrambled-source resolved-flags
#     hash-distinct; source_direct vs random-value resolved-flags hash-distinct. (all three are per-claim
#     bool vectors over the SAME harvested claims; they DO differ.)
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace). Per-seed checkpoint partials
#     (_partial_seed_<s>.json) written atomically; resume skips completed seeds.
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: this is a COVERAGE/CORRECTNESS/DETECTION test, not a Gaussian-noise-floor sweep. The comparator
#     leg is exact by CRT decode (MEASURED_MECHANISM@data/exp_math_rns_subtract_compare_v1/metrics.json). The
#     discriminators are CONTRASTS: source-direct resolution (coverage) vs scrambled-source collapse (LIFT);
#     comparator op-agreement ~1.0 (exactness guard). discriminator_reachability=True.
# - baseline_in_band (META_RULE_AG): the AG discriminator here is the SCRAMBLED-SOURCE control collapse
#     (correct minus scrambled resolution), NOT a difficulty gradient. The ledger-retrieval baseline it beats is
#     INTENTIONALLY LOW (0.0328): that low coverage IS the problem this cell fixes, so AG's 0.05 floor is EXEMPT
#     for the retrieval baseline (a low baseline is the finding, not a saturation artifact). coverage_nontrivial
#     is the in-band mechanism metric; the scrambled control must collapse for the discriminator to fire.
# - discriminator survives scale: smoke runs the source-direct-vs-scrambled LIFT + comparator exactness at FULL
#     comparator N_DIM=8192 over the WHOLE-corpus harvest (resolution is a deterministic JSON-walk, so coverage is
#     corpus-wide and scale-invariant; smoke reduces only the number of comparator seeds). The LIFT + collapse +
#     op-agreement FIRE identically in smoke (DISCRIMINATOR-MUST-SURVIVE-SCALE option A).
# - HARD_PASS strictly above floor: coverage_nontrivial HP 0.60 (HF 0.20); MEASURED@recon 0.8135 clears by >0.20.
#     lift HP 0.40 (HF 0.10); MEASURED 0.767. op-agreement HP 0.99 (HF 0.90); MEASURED 1.0. Strict HP band.
# - HP_SCOPE per-arm: coverage/lift/op-agreement HP gates apply to the source_direct MECHANISM only;
#     scrambled_source and random_value are FLOOR/CONTROL arms (must collapse, not clear HP).
# - cardinality_ok: EXPECTED_N_UNITS = len(seeds). coverage is seed-invariant (JSON-walk); seeds salt the
#     comparator phasor codebook + the random-value/scramble derangement (variance probe). verdict counts per_unit.
# - per-unit failure-class instrumentation (META_RULE_J): harvest per-file parse failures caught by SPECIFIC class
#     (json.JSONDecodeError / OSError / ValueError), counted in metrics, non-gating (one bad metrics.json must not
#     kill a 5800-file scan); no bare except.
# - calibration_check: default_ok_for_this_regime -- the resolution ACCEPT tolerance is PRECISION-AWARE (derived
#     from the number of decimals in the cited string; no tuned-for-pass free parameter). The scrambled-source
#     control collapse (MEASURED 0.813 -> 0.047 nontrivial) verifies the tolerance is not so loose that unrelated
#     files match; logged. Exact CRT decode for the comparator leg (SCALE/OFFSET cover the metric range).
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# TIER-2 SOURCE-DIRECT ENTAILMENT: RETRIEVAL-FREE SELF-AUDIT AGAINST EACH CELL'S OWN METRICS  v1
# =============================================================================================
# WHY (measured off-disk 2026-07-06, notes/research_ledger_coverage_negative_revival_2026-07-06.md): the landed
# Tier-2 numeric-entailment self-check (exp_cert_ledger_numeric_entailment_v1) closes the loop but its RETRIEVAL
# leg is near-vacuous -- CITED@data/exp_cert_ledger_numeric_entailment_v1/metrics.json:arms.7.retrieval_hit_rate
# = 0.0328. The bottleneck is NOT retrieval quality: the cert-ledger schema has NO slot for the cited numbers, so
# most cited claims have no backing record to retrieve at all (the content-addressable successor
# exp_cert_ledger_retrieval_coverage_v1 measured the ceiling at ~0.15-0.17, structurally bounded). The revival
# drill's #1 route: SKIP ledger retrieval entirely and audit each cited claim DIRECTLY against ITS OWN citing
# cell's metrics.json -- every metrics.json is its own referent (glob gives full, exact, non-fuzzy access; nothing
# needs to be "found" in a lossy index).
#
# WHAT (this cell): REUSE the numeric-entailment cell's claim-harvest + decode_then_compare op-agreement machinery
# VERBATIM; REPLACE ONLY the retrieval leg. For each cited `NUM op NUM` claim harvested from a file's verdict_msg,
# instead of retrieving a backing ledger record, open the SAME citing metrics.json, walk its numeric leaves, and
# RESOLVE the cited measured value (lhs) to a persisted metric field (precision-aware tolerance from the cited
# decimals). Then re-check the entailment on the RESOLVED persisted value via the VET'd decode_then_compare
# comparator (exp_math_rns_subtract_compare_v1). Measure BOTH:
#   COVERAGE = fraction of cited claims whose lhs resolves to a persisted source metric (the headline; a large
#              multiple of the 0.0328 ledger-retrieval baseline). MEASURED@recon 2026-07-06: 0.855 all / 0.8135
#              nontrivial (exclude lhs in {0,1}/integers that collide trivially).
#   OP_AGREEMENT = decode_then_compare == Python oracle over source-resolved in-range claims (exactness guard,
#              ~1.0) PLUS entailment_holds_rate = fraction of cited entailments that actually HOLD vs the persisted
#              source value (MEASURED 0.9759; the non-holding remainder is surfaced as SOURCE-BACKED audit
#              candidates -- higher-confidence than the free-text-only flags the predecessor could produce).
#   UN-AUDITABLE RESIDUAL (measured, not hidden) = 1 - coverage, bucketed: no_leaf_match (number lives only in
#              prose / is a relative-or-derived threshold / a genuine miscitation), trivial_excluded, resolved-but-
#              out-of-comparator-range, parse_fail.
# Plus a SECONDARY high-confidence arm: for the (currently 3-file / 1-cell) adopters of structured_gate_claims,
# recompute op(measured,threshold)==gate_verdict directly (route #1 as literally demonstrated; MEASURED 15/15
# agreement per file).
#
# ARMS (per comparator seed; coverage is seed-invariant, comparator/controls salt the seed):
#   source_direct     : MECHANISM -- lhs resolves to a persisted numeric leaf in the SAME citing metrics.json.
#                       coverage_nontrivial ~0.81. [MECHANISM]
#   scrambled_source  : CONTROL -- resolve lhs against a WRONG file's metrics.json (per-seed derangement). Must
#                       COLLAPSE (nontrivial ~0.047). This is the load-bearing firing control. [FLOOR]
#   random_value      : CONTROL -- resolve a RANDOM value (same precision) against the correct file. Collision
#                       floor for a non-cited number. [FLOOR]
#   op_agreement_guard: GUARD -- decode_then_compare op-eval == Python oracle on the resolved in-range values
#                       (exact CRT decode; source-independent by construction -> a GUARD, not the discriminator).
#   scram_residue     : CONTROL -- derange residues before CRT on the comparator -> garbage decode -> op-agreement
#                       collapses (confirms the CRT decode is load-bearing in the comparator leg). [FLOOR]
#   entailment_holds  : REPORTED -- fraction of resolved in-range cited entailments that evaluate TRUE vs source.
#   structured_gate   : REPORTED (secondary) -- recompute op(measured,threshold)==gate_verdict for the
#                       structured_gate_claims adopters (retrieval-free, machine-clean; 15/15 per adopter file).
#
# HONEST FRAMING (USER-LOCKED): NARROW glass-box MONITOR step. The audit READS cell metrics + verdicts and CHECKS
# entailment; it NEVER edits the ledger, never re-labels a cert_status, never edits code, never triggers a
# re-encode. Not fluent-language, not self-improvement. The source-direct DISCRIMINATOR is the RESOLUTION/coverage
# rate (which the scramble control collapses); the comparator op-agreement is an EXACTNESS GUARD that (correctly)
# does NOT depend on source. If source-direct resolution did NOT beat the retrieval baseline, or the scramble did
# NOT collapse, that is a REAL bounded finding reported honestly (no smoke) -- NOT forced to a pass.
#
# ASCII-only. CPU default (numpy complex64 phasor comparator; no GPU, no LLM, no re-encode). Reads the live
# self-record referent (whole data/ metrics.json tree). Run:
#   python experiments/exp_cert_ledger_source_direct_entailment_v1.py [--self-test | --smoke]   (bare -> full)

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)  # 17. PRINT-PROGRESS flush on newline

ANCHOR_NAME = "cert_ledger_source_direct_entailment_v1"
REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Comparison leg -- imported VERBATIM from the VET'd comparator primitive (genuine composition, DRY).
from experiments.exp_math_rns_subtract_compare_v1 import (  # noqa: E402
    REGIMES, SB, N_DIM, R_MODULI, _crt_setup, phasor_codebook, encode, decode_int,
    true_3way, _cyclic_derangement,
)

DATA_DIR = REPO / "data"

# ---- Fixed comparator regime: LARGE (M=70520) gives the widest exact dynamic range for quantized real metrics ----
REGIME = "large"                       # moduli (40,41,43); M=70520; decode_then_compare FULL-range exact
SCALE = 1000                           # quantize float v -> round(v*SCALE); 0.001 resolution
OFFSET = 20000                         # q(v) = round(v*SCALE)+OFFSET in [0,M); covers v in [-20.0, +50.5)
RES = 2.0 / SCALE                      # 0.002 -- ties below this are quantization-unresolvable

# ---- Source-direct resolution tolerance (PRECISION-AWARE; no tuned-for-pass free parameter) ----
REL_TOL = 1e-4                         # relative floor on the resolution tolerance
ABS_FLOOR = 1e-9                       # absolute floor (avoid zero tolerance)

# ---- Pre-registered bands (calibrated from MEASURED@recon 2026-07-06; re-measured in-cell) ----
BASELINE_LEDGER_RETRIEVAL = 0.0328     # CITED@data/exp_cert_ledger_numeric_entailment_v1/metrics.json:arms.7.retrieval_hit_rate
HP_COVERAGE_NT = 0.60                  # HARD_PASS: nontrivial source-direct resolution (MEASURED 0.8135)
HF_COVERAGE_NT = 0.20                  # HARD_FAIL: below -> source-direct not meaningfully above retrieval
COVERAGE_MULTIPLE_HP = 5.0             # HARD_PASS: coverage_nt >= 5x the ledger-retrieval baseline (>= 0.164)
HP_LIFT = 0.40                         # HARD_PASS: correct - scrambled nontrivial resolution (MEASURED 0.767)
HF_LIFT = 0.10                         # HARD_FAIL: scramble does not collapse -> resolution is coincidental
MAX_SCRAMBLED_NT = 0.15                # control: scrambled nontrivial resolution must collapse (MEASURED 0.047)
HP_OP_AGREE = 0.99                     # HARD_PASS: comparator exactness on resolved in-range (MEASURED 1.0)
HF_OP_AGREE = 0.90                     # HARD_FAIL: below -> comparator broke on real quantized data
MAX_SCRAM_RESIDUE = 0.72               # control: scrambled-residue comparator op-agreement near chance
MIN_CLAIMS_SMOKE = 100                 # discriminator-fires: need at least this many harvested claims (MEASURED 952)
MIN_CLAIMS_FULL = 300
MIN_RESOLVED_NT = 30                   # discriminator-fires: need enough resolved nontrivial claims

SEEDS_SMOKE = (7, 13, 19)              # multi-seed variance probe (comparator codebook + controls)
SEEDS_FULL = (7, 13, 19, 23, 29)       # >= 5 seeds (contract)

# NUM op NUM harvester regex -- LOGIC-IDENTICAL to exp_cert_ledger_numeric_entailment_v1 (same high-precision
# guards: left word-boundary, sci-notation as a unit, relative-threshold-coefficient drop; each removes a real
# harvester false-positive class verified on disk 2026-07-05).
_NUM = r"-?\d+\.?\d*(?:[eE][+-]?\d+)?"
_INEQ = re.compile(
    r"(?:([A-Za-z0-9_@]+)\s*=\s*)?(?<![\w@.])(" + _NUM + r")\s*(>=|<=|==|>|<)\s*(" + _NUM + r")(?![\d.eE])(?!\s*[*/xX])")


# ============================================================
# Defensive error-checking helpers (13/16)
# ============================================================


def _out_dir() -> Path:
    name = os.environ.get("HDLAB_EXP_NAME")
    return REPO / (f"data/exp_{name}" if name else f"data/exp_{ANCHOR_NAME}")


def _say(msg: str) -> None:
    print(msg, flush=True)


def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, output_dir / "_start_marker.json")


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int, t0: float, extra=None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": round(time.perf_counter() - t0, 2),
    }
    if extra:
        row["extra"] = extra
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_json_atomic(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)  # atomic (META_RULE_AH)


def _write_metrics_atomic(output_dir: Path, metrics: dict) -> None:
    _write_json_atomic(output_dir / "metrics.json", metrics)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME,
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
    }
    _write_metrics_atomic(output_dir, diag)


# ============================================================
# Quantization + numeric-op helpers (logic-identical to the comparator leg)
# ============================================================


# Module-level CRT constants for the fixed regime (populated in _setup_regime()).
_MODULI = REGIMES[REGIME]
_M = 1
_MI = _YI = None


def _setup_regime():
    global _M, _MI, _YI
    _M, _MI, _YI = _crt_setup(_MODULI)


def quantize(v: float):
    """float -> integer in [0,M) via q = round(v*SCALE)+OFFSET. None if out of the exact dynamic range."""
    q = int(round(v * SCALE)) + OFFSET
    return q if 0 <= q < _M else None


def eval_op(cmp3: int, op: str) -> bool:
    """cmp3 in {+1,0,-1} -> boolean truth of `lhs op rhs`."""
    if op == ">=":
        return cmp3 >= 0
    if op == ">":
        return cmp3 > 0
    if op == "<=":
        return cmp3 <= 0
    if op == "<":
        return cmp3 < 0
    if op == "==":
        return cmp3 == 0
    raise ValueError(f"unknown op {op!r}")


def substrate_compare(qa: int, qb: int, cbs, scramble=None) -> int:
    """Comparison leg: two exact CRT decodes (decode_then_compare, the VET'd mechanism-of-record) -> 3-way.
    scramble (a derangement) permutes residues before CRT on BOTH operands -> the scrambled-residue control."""
    da = decode_int(encode(qa, cbs, _MODULI, SB), cbs, _MODULI, SB, _M, _MI, _YI, scramble=scramble)
    db = decode_int(encode(qb, cbs, _MODULI, SB), cbs, _MODULI, SB, _M, _MI, _YI, scramble=scramble)
    return true_3way(da, db)


# ============================================================
# Identity-key normalization + source-metric resolution (the REPLACED leg)
# ============================================================


def _norm_exp_key(p: str) -> str:
    """Metrics path -> exp-dir key (basename of the exp_* dir), separator-agnostic."""
    s = str(p).replace("\\", "/")
    parts = [x for x in s.split("/") if x]
    for x in parts:
        if x.startswith("exp_"):
            return x
    return parts[-2] if len(parts) >= 2 else s


def collect_numeric_leaves(obj, key: str, out: list) -> None:
    """Collect (last_key, float_value) for every numeric leaf (bools excluded). List items inherit parent key."""
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        out.append((key, float(obj)))
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            collect_numeric_leaves(v, str(k), out)
    elif isinstance(obj, list):
        for v in obj:
            collect_numeric_leaves(v, key, out)


def _decimals(s: str) -> int:
    """Number of fractional decimals in a cited numeric string (sci-notation / int -> treated high-precision)."""
    s = s.strip()
    if "e" in s or "E" in s:
        return 6
    if "." in s:
        return len(s.split(".", 1)[1])
    return 0


def resolve_value(lhs: float, lhs_str: str, leaves, name: str):
    """SOURCE-DIRECT resolution: find a persisted numeric leaf ~= lhs in the citing file's own metrics.json.
    Precision-aware absolute tolerance from the cited decimals (no tuned free parameter). Prefer a leaf whose key
    contains the cited metric NAME. Returns dict(resolved, value, path, name_matched)."""
    dec = _decimals(lhs_str)
    prec_tol = 0.5 * (10.0 ** (-dec)) if dec <= 6 else 1e-6
    abstol = max(prec_tol, abs(lhs) * REL_TOL, ABS_FLOOR)
    name_l = name.lower() if name else ""
    best = None
    best_d = None
    best_name = False
    for (k, v) in leaves:
        d = abs(v - lhs)
        if d <= abstol:
            nm = bool(name_l) and len(name_l) >= 2 and (name_l in k.lower())
            take = (best is None) or (nm and not best_name) or (nm == best_name and d < best_d)
            if take:
                best = (k, v)
                best_d = d
                best_name = nm
    if best is None:
        return {"resolved": False, "value": None, "path": None, "name_matched": False}
    return {"resolved": True, "value": best[1], "path": best[0], "name_matched": best_name}


def _is_trivial(lhs: float) -> bool:
    """Trivial cited values (0, 1, integers) collide across unrelated files; excluded from the STRICT coverage."""
    return lhs in (0.0, 1.0) or float(lhs).is_integer()


# ============================================================
# Harvest: cited claims + the citing file's OWN numeric leaves (the referent)
# ============================================================


def harvest(data_dir: Path):
    """Scan every data/**/metrics.json; extract cited `NUM op NUM` claims from verdict_msg AND capture the SAME
    file's numeric leaves (the source referent). Returns (claims, file_leaves, order, stats). Deterministic.
    Per-file parse failures counted by class (META_RULE_J), never silently gating."""
    claims = []
    file_leaves = {}
    order = []
    seen = set()
    n_files = n_with = 0
    fail_json = fail_os = fail_val = 0
    struct_recompute = []          # secondary structured_gate_claims arm
    for mp in sorted(data_dir.glob("**/metrics.json"), key=lambda p: str(p)):
        s = str(mp)
        if ANCHOR_NAME in s or "cert_ledger_numeric_entailment" in s or "cert_ledger_retrieval_coverage" in s:
            continue  # never ingest this cell's own / sibling audit cells' output
        n_files += 1
        try:
            with open(mp, encoding="utf-8") as f:
                d = json.load(f)
        except json.JSONDecodeError:
            fail_json += 1
            continue
        except OSError:
            fail_os += 1
            continue
        except ValueError:
            fail_val += 1
            continue
        ek = _norm_exp_key(s)
        # secondary: structured_gate_claims recompute (machine-clean; retrieval-free)
        gc = d.get("structured_gate_claims")
        if isinstance(gc, list) and gc:
            n_ok = 0
            n_tot = 0
            for g in gc:
                if not isinstance(g, dict):
                    continue
                try:
                    meas = float(g["measured"])
                    thr = float(g["threshold"])
                    op = g["op"]
                    gv = bool(g["gate_verdict"])
                except (KeyError, TypeError, ValueError):
                    continue
                cmp3 = 1 if meas > thr else (0 if meas == thr else -1)
                n_tot += 1
                n_ok += 1 if eval_op(cmp3, op) == gv else 0
            if n_tot:
                struct_recompute.append({"exp_key": ek, "n_claims": n_tot, "n_agree": n_ok})
        vm = d.get("verdict_msg")
        if not isinstance(vm, str) or not vm:
            continue
        verdict = d.get("verdict")
        leaves = []
        collect_numeric_leaves(d, "", leaves)
        got = False
        for m in _INEQ.finditer(vm):
            name, lhs_s, op, rhs_s = m.group(1), m.group(2), m.group(3), m.group(4)
            try:
                lhs = float(lhs_s)
                rhs = float(rhs_s)
            except ValueError:
                continue
            # drop obvious non-metric integer pairs (IDs / dims): both integer AND both large
            if lhs.is_integer() and rhs.is_integer() and abs(lhs) > 1000 and abs(rhs) > 1000:
                continue
            key = (ek, name or "", round(lhs, 6), op, round(rhs, 6))
            if key in seen:
                continue
            seen.add(key)
            got = True
            claims.append({"exp_key": ek, "verdict": verdict, "name": name or "",
                           "lhs": lhs, "lhs_str": lhs_s, "op": op, "rhs": rhs,
                           "path": s.replace("\\", "/")})
        if got:
            n_with += 1
            if ek not in file_leaves:
                file_leaves[ek] = leaves
                order.append(ek)
    claims.sort(key=lambda t: (t["exp_key"], t["name"], t["lhs"], t["op"], t["rhs"]))
    stats = {"n_files_scanned": n_files, "n_files_with_cited_inequality": n_with,
             "n_raw_claims": len(claims),
             "harvest_parse_failures": {"json_decode": fail_json, "os_error": fail_os, "value_error": fail_val},
             "n_structured_gate_files": len(struct_recompute)}
    return claims, file_leaves, order, stats, struct_recompute


# ============================================================
# Per-seed run (coverage is seed-invariant; comparator + controls salt the seed)
# ============================================================


def run_seed(seed: int, claims, file_leaves, order, cbs):
    """One comparator seed over ALL harvested claims. Source-direct resolution (correct / scrambled / random-value)
    + comparator op-agreement + entailment-holds + residual buckets + source-backed audit candidates."""
    n = len(claims)
    idx = {ek: i for i, ek in enumerate(order)}
    n_files = len(order)
    # per-seed scramble = a cyclic shift of the file->leaves assignment (a derangement: no file maps to itself).
    shift = 1 + (seed * 2654435761) % (n_files - 1) if n_files > 1 else 0
    rng = np.random.default_rng(123457 + seed)
    derange = _cyclic_derangement(R_MODULI)

    n_nt = 0
    res_all = res_nt = 0
    scr_all = scr_nt = 0
    rnd_all = rnd_nt = 0
    name_match = 0
    in_range = exact_agree = exact_n = holds = 0
    n_faithful = holds_faithful = 0    # quant-faithful subset (excludes sub-resolution ties < RES)
    scr_res_agree = scr_res_n = 0
    confirmed_nt = 0                # nontrivial resolved-in-range (source_confirmed; collapses under scramble)
    scr_confirmed_nt = 0
    # residual buckets
    b_no_leaf = b_trivial = b_oor_resolved = 0
    # audit byproducts
    not_holding = []               # resolved in-range but v op rhs FALSE (source-backed candidate)
    unbacked_nt = []               # nontrivial cited number NOT found in the citing file's own metrics
    flags_src, flags_scr, flags_rnd = [], [], []

    for c in claims:
        lhs = c["lhs"]
        trivial = _is_trivial(lhs)
        if not trivial:
            n_nt += 1
        leaves = file_leaves.get(c["exp_key"], [])
        r = resolve_value(lhs, c["lhs_str"], leaves, c["name"])
        # scrambled source: resolve against a WRONG file
        wek = order[(idx[c["exp_key"]] + shift) % n_files] if n_files > 1 else c["exp_key"]
        rs = resolve_value(lhs, c["lhs_str"], file_leaves.get(wek, []), c["name"])
        # random-value control: a random value of the SAME precision, resolved in the correct file
        dec = _decimals(c["lhs_str"])
        rv = round(float(rng.random()), min(max(dec, 1), 6))
        rr = resolve_value(rv, f"{rv:.{min(max(dec,1),6)}f}", leaves, "")

        flags_src.append(1 if r["resolved"] else 0)
        flags_scr.append(1 if rs["resolved"] else 0)
        flags_rnd.append(1 if rr["resolved"] else 0)

        res_all += 1 if r["resolved"] else 0
        scr_all += 1 if rs["resolved"] else 0
        rnd_all += 1 if rr["resolved"] else 0
        if not trivial:
            res_nt += 1 if r["resolved"] else 0
            scr_nt += 1 if rs["resolved"] else 0
            rnd_nt += 1 if rr["resolved"] else 0
        if r["resolved"] and r["name_matched"]:
            name_match += 1

        if not r["resolved"]:
            if trivial:
                b_trivial += 1
            else:
                b_no_leaf += 1
                if len(unbacked_nt) < 40:
                    unbacked_nt.append({"exp_key": c["exp_key"], "name": c["name"],
                                        "cited": f"{c['lhs']} {c['op']} {c['rhs']}",
                                        "recorded_verdict": c["verdict"], "path": c["path"]})
            continue

        # resolved: comparator op-agreement + entailment-holds on the RESOLVED persisted value
        v = r["value"]
        qa, qb = quantize(v), quantize(c["rhs"])
        if qa is None or qb is None:
            b_oor_resolved += 1
            continue
        in_range += 1
        cmp_sub = substrate_compare(qa, qb, cbs)
        sub_holds = eval_op(cmp_sub, c["op"])
        cmp_ora = 1 if qa > qb else (0 if qa == qb else -1)
        ora_holds = eval_op(cmp_ora, c["op"])
        exact_n += 1
        exact_agree += 1 if sub_holds == ora_holds else 0
        holds += 1 if sub_holds else 0
        if not trivial:
            confirmed_nt += 1
        # quant-faithful = resolved value and threshold are distinguishable at the comparator resolution
        # (excludes sub-resolution ties like "0.0 < 1e-10" where 1e-10 < RES quantizes equal to 0.0).
        faithful = (abs(v - c["rhs"]) >= RES) or (v == c["rhs"])
        if faithful:
            n_faithful += 1
            holds_faithful += 1 if sub_holds else 0
        # scrambled-residue comparator control (garbage decode)
        cmp_scr = substrate_compare(qa, qb, cbs, scramble=derange)
        scr_res_n += 1
        scr_res_agree += 1 if eval_op(cmp_scr, c["op"]) == ora_holds else 0
        # source-backed audit candidate: cited entailment does NOT hold vs the persisted value.
        # Only flag QUANT-FAITHFUL cases (sub-resolution ties are comparator artifacts, not miscitations).
        if faithful and sub_holds is False:
            if len(not_holding) < 40:
                not_holding.append({"exp_key": c["exp_key"], "name": c["name"],
                                    "cited": f"{c['lhs']} {c['op']} {c['rhs']}",
                                    "resolved_source_value": round(v, 6), "resolved_path": r["path"],
                                    "recorded_verdict": c["verdict"], "path": c["path"]})

        # scrambled-source confirmed (nontrivial): resolved in the WRONG file AND in-range
        if not trivial and rs["resolved"]:
            qas, qbs = quantize(rs["value"]), quantize(c["rhs"])
            if qas is not None and qbs is not None:
                scr_confirmed_nt += 1

    cov_all = res_all / n if n else float("nan")
    cov_nt = res_nt / n_nt if n_nt else float("nan")
    scr_cov_all = scr_all / n if n else float("nan")
    scr_cov_nt = scr_nt / n_nt if n_nt else float("nan")
    rnd_cov_nt = rnd_nt / n_nt if n_nt else float("nan")
    lift_nt = cov_nt - scr_cov_nt
    op_agree = exact_agree / exact_n if exact_n else float("nan")
    holds_rate = holds / exact_n if exact_n else float("nan")
    holds_rate_faithful = holds_faithful / n_faithful if n_faithful else float("nan")
    scr_res_rate = scr_res_agree / scr_res_n if scr_res_n else float("nan")
    src_confirmed_nt = confirmed_nt / n_nt if n_nt else float("nan")
    scr_confirmed_rate_nt = scr_confirmed_nt / n_nt if n_nt else float("nan")
    name_match_rate = name_match / res_all if res_all else float("nan")

    res = {
        "seed": seed, "n_claims": n, "n_nontrivial": n_nt,
        "coverage_source_direct_all": round(cov_all, 4),
        "coverage_source_direct_nontrivial": round(cov_nt, 4),
        "scrambled_source_coverage_all": round(scr_cov_all, 4),
        "scrambled_source_coverage_nontrivial": round(scr_cov_nt, 4),
        "random_value_coverage_nontrivial": round(rnd_cov_nt, 4),
        "coverage_lift_nontrivial": round(lift_nt, 4),
        "coverage_multiple_vs_ledger_retrieval": round(cov_nt / BASELINE_LEDGER_RETRIEVAL, 2) if cov_nt == cov_nt else None,
        "n_resolved_in_comparator_range": in_range,
        "op_agreement_guard": round(op_agree, 4) if op_agree == op_agree else None,
        "entailment_holds_rate": round(holds_rate, 4) if holds_rate == holds_rate else None,
        "entailment_holds_rate_quant_faithful": round(holds_rate_faithful, 4) if holds_rate_faithful == holds_rate_faithful else None,
        "n_quant_faithful": n_faithful,
        "scram_residue_agreement": round(scr_res_rate, 4) if scr_res_rate == scr_res_rate else None,
        "source_confirmed_rate_nontrivial": round(src_confirmed_nt, 4) if src_confirmed_nt == src_confirmed_nt else None,
        "scrambled_source_confirmed_rate_nontrivial": round(scr_confirmed_rate_nt, 4) if scr_confirmed_rate_nt == scr_confirmed_rate_nt else None,
        "name_match_rate_among_resolved": round(name_match_rate, 4) if name_match_rate == name_match_rate else None,
        "residual_buckets": {"no_leaf_match": b_no_leaf, "trivial_excluded": b_trivial,
                             "resolved_out_of_comparator_range": b_oor_resolved},
        "n_not_holding_candidates": len(not_holding),
        "n_unbacked_nontrivial_candidates": len(unbacked_nt),
    }
    hashes = {
        "src": hashlib.sha256(np.asarray(flags_src, dtype=np.int8).tobytes()).hexdigest(),
        "scr": hashlib.sha256(np.asarray(flags_scr, dtype=np.int8).tobytes()).hexdigest(),
        "rnd": hashlib.sha256(np.asarray(flags_rnd, dtype=np.int8).tobytes()).hexdigest(),
    }
    audit = {"not_holding": not_holding, "unbacked_nontrivial": unbacked_nt}
    return res, hashes, audit


# ============================================================
# Formula self-tests (MANDATORY)
# ============================================================


def comparator_selftest(seed: int = 7) -> bool:
    """(a) substrate decode_then_compare op-eval == Python op-eval on random quantized pairs for all 5 ops;
    (b) round-trip encode/decode exact in [0,M); (c) scrambled-residue op-agreement collapses (<0.72)."""
    cbs = [phasor_codebook(m, SB, 6000 + seed * 10 + i) for i, m in enumerate(_MODULI)]
    derange = _cyclic_derangement(R_MODULI)
    rng = np.random.default_rng(999 + seed)
    ops = [">=", ">", "<=", "<", "=="]
    for _ in range(32):
        q = int(rng.integers(0, _M))
        if decode_int(encode(q, cbs, _MODULI, SB), cbs, _MODULI, SB, _M, _MI, _YI) != q:
            return False
    for _ in range(60):
        qa = int(rng.integers(0, _M)); qb = int(rng.integers(0, _M))
        cmp_sub = substrate_compare(qa, qb, cbs)
        cmp_py = 1 if qa > qb else (0 if qa == qb else -1)
        for op in ops:
            if eval_op(cmp_sub, op) != eval_op(cmp_py, op):
                return False
    agree = tot = 0
    for _ in range(80):
        qa = int(rng.integers(0, _M)); qb = int(rng.integers(0, _M))
        if qa == qb:
            continue
        tot += 1
        cmp_scr = substrate_compare(qa, qb, cbs, scramble=derange)
        if eval_op(cmp_scr, ">=") == eval_op((1 if qa > qb else -1), ">="):
            agree += 1
    return (agree / tot if tot else 1.0) <= MAX_SCRAM_RESIDUE


def resolution_selftest() -> tuple:
    """(a) a claim whose lhs EQUALS a persisted leaf RESOLVES; (b) a claim whose lhs is ABSENT does NOT resolve
    (proves resolution is specific, not a wildcard); (c) precision-aware tolerance: a 3-decimal cited value
    resolves a leaf 0.0004 away but a 6-decimal cited value 0.0004 away does NOT; (d) name-preference: given two
    leaves both within tol, the one whose key contains the cited NAME wins."""
    leaves = [("spearman", 0.886), ("recall", 1.0), ("balacc_scrambled", 0.5),
              ("compose_lift", -0.0059), ("other_metric", 0.8864)]
    # (a) present resolves
    r_present = resolve_value(0.886, "0.886", leaves, "spearman")
    a_ok = r_present["resolved"] and abs(r_present["value"] - 0.886) < 1e-6
    # (b) absent does not resolve (0.777 not near any leaf at 3-dec tol 0.0005)
    r_absent = resolve_value(0.777, "0.777", leaves, "nope")
    b_ok = not r_absent["resolved"]
    # (c) precision-aware tolerance
    r_loose = resolve_value(0.8864, "0.886", leaves, "")     # 3-dec tol=0.0005 -> 0.886 leaf within 0.0004: resolves
    r_tight = resolve_value(0.885600, "0.885600", leaves, "")  # 6-dec tol=5e-7 -> nearest 0.8864 is 0.0008 away: no
    c_ok = r_loose["resolved"] and (not r_tight["resolved"])
    # (d) name-preference: cited name 'other_metric' should land on the 0.8864 leaf, not the 0.886 leaf
    two = [("spearman", 0.8864), ("other_metric", 0.8864)]
    r_name = resolve_value(0.8864, "0.8864", two, "other_metric")
    d_ok = r_name["resolved"] and r_name["name_matched"] and r_name["path"] == "other_metric"
    return a_ok, b_ok, c_ok, d_ok


# ============================================================
# Classify
# ============================================================


def _minv(vals):
    v = [x for x in vals if x is not None and x == x]
    return min(v) if v else float("nan")


def _maxv(vals):
    v = [x for x in vals if x is not None and x == x]
    return max(v) if v else float("nan")


def _meanv(vals):
    v = [x for x in vals if x is not None and x == x]
    return (sum(v) / len(v)) if v else float("nan")


def classify(per_seed, seeds, mode, n_claims, n_nontrivial, min_claims):
    cov_nt = _meanv([per_seed[s]["coverage_source_direct_nontrivial"] for s in seeds])
    cov_all = _meanv([per_seed[s]["coverage_source_direct_all"] for s in seeds])
    scr_nt_max = _maxv([per_seed[s]["scrambled_source_coverage_nontrivial"] for s in seeds])
    lift_min = _minv([per_seed[s]["coverage_lift_nontrivial"] for s in seeds])
    op_min = _minv([per_seed[s]["op_agreement_guard"] for s in seeds])
    scr_res_max = _maxv([per_seed[s]["scram_residue_agreement"] for s in seeds])
    holds = _meanv([per_seed[s]["entailment_holds_rate"] for s in seeds])
    mult = _meanv([per_seed[s]["coverage_multiple_vs_ledger_retrieval"] for s in seeds])
    n_resolved_nt = int(round(cov_nt * n_nontrivial)) if cov_nt == cov_nt else 0

    diag = (f"n_claims={n_claims} n_nontrivial={n_nontrivial} coverage_all={cov_all:.4f} "
            f"coverage_nontrivial={cov_nt:.4f} (={mult:.1f}x ledger-retrieval baseline {BASELINE_LEDGER_RETRIEVAL}) "
            f"scrambled_nontrivial_max={scr_nt_max:.4f} lift_min={lift_min:.4f} op_agreement_min="
            f"{op_min if op_min == op_min else float('nan'):.4f} entailment_holds_rate={holds:.4f} "
            f"scram_residue_max={scr_res_max if scr_res_max == scr_res_max else float('nan'):.4f}")

    # --- discriminator-fires / control gates (ALL modes) ---
    if n_claims < min_claims:
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"insufficient harvested claims: n={n_claims} < {min_claims}. {diag}", False)
    if n_resolved_nt < MIN_RESOLVED_NT:
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"insufficient resolved nontrivial claims: {n_resolved_nt} < {MIN_RESOLVED_NT}. {diag}", False)
    if op_min == op_min and op_min < HF_OP_AGREE:
        return ("HARD_FAIL",
                f"COMPARATOR BROKE on real quantized data: op_agreement min={op_min:.4f} < {HF_OP_AGREE}. {diag}",
                False)
    if scr_res_max == scr_res_max and scr_res_max > MAX_SCRAM_RESIDUE:
        return ("CONTROL_DID_NOT_COLLAPSE",
                f"scrambled-RESIDUE comparator op-agreement did NOT collapse (max={scr_res_max:.4f} > "
                f"{MAX_SCRAM_RESIDUE}): CRT decode not load-bearing. {diag}", False)
    if not (scr_nt_max <= MAX_SCRAMBLED_NT):
        return ("CONTROL_DID_NOT_COLLAPSE",
                f"SCRAMBLED-SOURCE control did NOT collapse: scrambled_nontrivial_max={scr_nt_max:.4f} > "
                f"{MAX_SCRAMBLED_NT} -> resolution is coincidental (unrelated files match the cited numbers), "
                f"source-direct not load-bearing. {diag}", False)

    # --- HARD_FAIL band ---
    if cov_nt < HF_COVERAGE_NT:
        return ("HARD_FAIL",
                f"SOURCE-DIRECT DOES NOT LIFT COVERAGE: coverage_nontrivial={cov_nt:.4f} < {HF_COVERAGE_NT} "
                f"(not meaningfully above the ledger-retrieval baseline {BASELINE_LEDGER_RETRIEVAL}). {diag}", True)
    if lift_min <= HF_LIFT:
        return ("HARD_FAIL",
                f"SOURCE-DIRECT ADDS NO SIGNAL: lift_min={lift_min:.4f} <= {HF_LIFT} (correct-source resolution no "
                f"better than scrambled-source). {diag}", True)

    # --- smoke: discriminator fired + controls collapsed + coverage beats baseline ---
    if mode == "smoke":
        return ("HARD_PASS",
                f"SMOKE_SOURCE_DIRECT_FIRES: retrieval-free source-direct audit resolves coverage_nontrivial="
                f"{cov_nt:.4f} of cited claims against their OWN metrics.json ({mult:.1f}x the {BASELINE_LEDGER_RETRIEVAL} "
                f"ledger-retrieval baseline) at FULL comparator N_DIM={N_DIM}; scrambled-source control collapses "
                f"(max={scr_nt_max:.4f}); lift_min={lift_min:.4f}; comparator op-agreement min="
                f"{op_min if op_min == op_min else float('nan'):.4f} (==oracle); entailment_holds_rate={holds:.4f} "
                f"vs the persisted source values. Un-auditable residual measured + bucketed. {diag}", True)

    # --- FULL bands ---
    hard_pass = (cov_nt >= HP_COVERAGE_NT and cov_nt >= COVERAGE_MULTIPLE_HP * BASELINE_LEDGER_RETRIEVAL
                 and lift_min >= HP_LIFT and scr_nt_max <= MAX_SCRAMBLED_NT
                 and (op_min != op_min or op_min >= HP_OP_AGREE))
    if hard_pass:
        return ("HARD_PASS",
                f"SOURCE-DIRECT MAKES THE TIER-2 SELF-AUDIT MEANINGFUL: over {n_claims} real cited claims "
                f"({n_nontrivial} nontrivial) harvested from the substrate's own on-disk verdict_msgs, the "
                f"retrieval-free audit re-checks each cited number DIRECTLY against its citing cell's OWN "
                f"metrics.json -- coverage_nontrivial={cov_nt:.4f} ({mult:.1f}x the {BASELINE_LEDGER_RETRIEVAL} "
                f"ledger-retrieval ceiling; coverage_all={cov_all:.4f}). The cited entailments are then re-evaluated "
                f"on the PERSISTED source value via the VET'd decode_then_compare comparator: op-agreement "
                f"min={op_min if op_min == op_min else float('nan'):.4f} (==Python oracle, exact CRT decode); "
                f"entailment_holds_rate={holds:.4f} of cited inequalities actually HOLD vs source (the non-holding "
                f"remainder is surfaced as SOURCE-BACKED audit candidates). FIRING CONTROL: scrambled-source "
                f"resolution collapses (nontrivial max={scr_nt_max:.4f}; lift_min={lift_min:.4f}) -> resolution is "
                f"genuinely source-specific, not coincidental. Scrambled-RESIDUE comparator control collapses "
                f"(max={scr_res_max if scr_res_max == scr_res_max else float('nan'):.4f}) -> CRT decode load-bearing. "
                f"HONEST RESIDUAL: ~{(1-cov_nt)*100:.0f}% of nontrivial cited numbers do NOT resolve to a persisted "
                f"source metric (number lives only in prose / is a relative-or-derived threshold / a genuine "
                f"miscitation) -- measured + bucketed, not hidden. HONEST SCOPE: the source-direct DISCRIMINATOR is "
                f"the resolution/coverage rate (scramble collapses it); the comparator op-agreement is an EXACTNESS "
                f"GUARD that is source-independent by construction. NARROW glass-box monitor; reads cells + verdicts, "
                f"NEVER edits the ledger/cells/code. {diag}", True)
    return ("MIDDLE_BAND",
            f"source-direct coverage is above the HARD_FAIL floor but below HARD_PASS on at least one gate "
            f"(coverage_nontrivial={cov_nt:.4f} vs {HP_COVERAGE_NT}; lift_min={lift_min:.4f} vs {HP_LIFT}; "
            f"op_agreement_min={op_min if op_min == op_min else float('nan'):.4f} vs {HP_OP_AGREE}). "
            f"Honest partial. {diag}", True)


# ============================================================
# Config + driver
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"seeds": (7,), "min_claims": 20}
    if mode == "smoke":
        return {"seeds": SEEDS_SMOKE, "min_claims": MIN_CLAIMS_SMOKE}
    return {"seeds": SEEDS_FULL, "min_claims": MIN_CLAIMS_FULL}


def _partial_path(output_dir: Path, seed: int) -> Path:
    return output_dir / f"_partial_seed_{seed}.json"


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    _setup_regime()
    cfg = get_config(mode)
    seeds = cfg["seeds"]
    exp_units = len(seeds)
    _write_start_marker(output_dir, mode, exp_units)
    _say(f"[{ANCHOR_NAME}] mode={mode} regime={REGIME} moduli={_MODULI} M={_M} N={N_DIM} SB={SB} "
         f"SCALE={SCALE} OFFSET={OFFSET} seeds={seeds} expected_units={exp_units}")

    # formula self-tests (ALL modes)
    if not comparator_selftest(seed=seeds[0]):
        raise AssertionError("COMPARATOR_SELFTEST_FAIL (op-eval != oracle, or round-trip inexact, or "
                             "scrambled-residue did not collapse)")
    a_ok, b_ok, c_ok, d_ok = resolution_selftest()
    if not (a_ok and b_ok and c_ok and d_ok):
        raise AssertionError(f"RESOLUTION_SELFTEST_FAIL: present_resolves={a_ok} absent_rejected={b_ok} "
                             f"precision_aware={c_ok} name_preference={d_ok}")
    _say(f"[{ANCHOR_NAME}] formula self-tests PASSED (comparator op-eval + round-trip + scram-collapse; "
         f"resolution present/absent/precision/name-preference)")

    # harvest claims + citing-file leaves (ONCE; deterministic, corpus-wide)
    claims, file_leaves, order, hstats, struct_recompute = harvest(DATA_DIR)
    n_claims = len(claims)
    n_nontrivial = sum(1 for c in claims if not _is_trivial(c["lhs"]))
    _say(f"[{ANCHOR_NAME}] harvest: scanned {hstats['n_files_scanned']} metrics.json, "
         f"{hstats['n_files_with_cited_inequality']} cite an inequality, {n_claims} unique claims "
         f"({n_nontrivial} nontrivial), {hstats['n_structured_gate_files']} structured_gate_claims files, "
         f"parse_fail={hstats['harvest_parse_failures']}")
    if n_claims == 0:
        raise AssertionError("EMPTY_REFERENT: 0 harvested claims")

    # per-seed run (with checkpoint/resume)
    per_seed = {}
    hashes_all = {}
    audit_union_nh = {}
    audit_union_ub = {}
    per_unit = []
    for si, seed in enumerate(seeds):
        pp = _partial_path(output_dir, seed)
        if pp.exists():
            try:
                saved = json.load(open(pp, encoding="utf-8"))
                if saved.get("seed") == seed and saved.get("n_claims") == n_claims:
                    per_seed[seed] = saved["res"]
                    hashes_all[seed] = saved["hashes"]
                    for a in saved.get("audit", {}).get("not_holding", []):
                        audit_union_nh[(a["exp_key"], a["name"], a["cited"])] = a
                    for a in saved.get("audit", {}).get("unbacked_nontrivial", []):
                        audit_union_ub[(a["exp_key"], a["name"], a["cited"])] = a
                    _say(f"  [seed {seed}] RESUMED from checkpoint")
                    _append_units(per_unit, seed, saved["res"])
                    continue
            except (json.JSONDecodeError, KeyError, OSError):
                pass  # corrupt/stale partial -> recompute
        cbs = [phasor_codebook(m, SB, 6000 + seed * 10 + i) for i, m in enumerate(_MODULI)]
        res, hashes, audit = run_seed(seed, claims, file_leaves, order, cbs)
        per_seed[seed] = res
        hashes_all[seed] = hashes
        for a in audit["not_holding"]:
            audit_union_nh[(a["exp_key"], a["name"], a["cited"])] = a
        for a in audit["unbacked_nontrivial"]:
            audit_union_ub[(a["exp_key"], a["name"], a["cited"])] = a
        _write_json_atomic(pp, {"seed": seed, "n_claims": n_claims, "res": res, "hashes": hashes, "audit": audit})
        _append_units(per_unit, seed, res)
        _heartbeat(output_dir, si + 1, len(seeds), t0,
                   extra={"seed": seed, "coverage_nt": res["coverage_source_direct_nontrivial"],
                          "scrambled_nt": res["scrambled_source_coverage_nontrivial"]})
        _say(f"  [seed {seed}] coverage_nt={res['coverage_source_direct_nontrivial']:.4f} "
             f"scrambled_nt={res['scrambled_source_coverage_nontrivial']:.4f} "
             f"lift={res['coverage_lift_nontrivial']:+.4f} op_agree={res['op_agreement_guard']} "
             f"holds={res['entailment_holds_rate']} scram_residue={res['scram_residue_agreement']} "
             f"residual={res['residual_buckets']}")

    # arms_differ (META_RULE_AF): source-resolved flags differ from scrambled-source + random-value flags
    reasons = []
    for seed in seeds:
        h = hashes_all[seed]
        if h["src"] == h["scr"]:
            reasons.append(f"seed{seed}:source==scrambled resolved-flags")
        if h["src"] == h["rnd"]:
            reasons.append(f"seed{seed}:source==random-value resolved-flags")
    arms_differ_ok = not reasons
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: " + "; ".join(reasons))

    verdict, vmsg, controls_ok = classify(per_seed, seeds, mode, n_claims, n_nontrivial, cfg["min_claims"])
    elapsed = time.perf_counter() - t0

    struct_total = sum(g["n_claims"] for g in struct_recompute)
    struct_agree = sum(g["n_agree"] for g in struct_recompute)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: Tier-2 source-direct entailment self-audit over own metrics ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(seeds),
        "n_units": len(per_unit),
        "expected_n_units": exp_units,
        "cardinality_ok": len(per_unit) >= exp_units,
        "n_claims": n_claims,
        "n_nontrivial": n_nontrivial,
        "config": {
            "regime": REGIME, "moduli": list(_MODULI), "M": _M, "N": N_DIM, "SB": SB,
            "SCALE": SCALE, "OFFSET": OFFSET, "RES": RES, "REL_TOL": REL_TOL, "seeds": list(seeds),
            "retrieval_leg": "REPLACED -> source_direct_metric_lookup_in_citing_cell_own_metrics_json",
            "comparison_leg": "decode_then_compare_two_CRT_decodes_from_exp_math_rns_subtract_compare_v1",
            "claim_source": "verdict_msg_cited_NUM_op_NUM_inequalities_across_data_metrics_json",
            "resolution": "precision_aware_tolerance_from_cited_decimals_prefer_name_matched_leaf",
            "storage_strategy": "no_storage_algebraic_bind (comparator CRT; source lookup is direct file read)",
        },
        "harvest_stats": hstats,
        "arms": {str(s): per_seed[s] for s in seeds},
        "per_unit": per_unit,
        "arms_differ_verified": arms_differ_ok,
        "controls": {"controls_collapsed": controls_ok},
        "structured_gate_claims_audit": {
            "n_adopter_files": len(struct_recompute),
            "n_claims_total": struct_total,
            "n_agree_total": struct_agree,
            "recompute_agreement": round(struct_agree / struct_total, 4) if struct_total else None,
            "per_file": struct_recompute,
            "note": ("SECONDARY high-confidence retrieval-free arm: recompute op(measured,threshold)==gate_verdict "
                     "directly from structured_gate_claims. Machine-clean, no free-text parse. Adoption is currently "
                     "1 distinct cell (3 run-variant files) -- this is the SOUND-but-tiny path; the free-text "
                     "source-direct resolution above is the SCALE path (corpus-wide coverage)."),
        },
        "audit_candidates": {
            "not_holding_source_backed": list(audit_union_nh.values())[:40],
            "n_not_holding_total": len(audit_union_nh),
            "unbacked_nontrivial": list(audit_union_ub.values())[:40],
            "n_unbacked_nontrivial_total": len(audit_union_ub),
            "note": ("not_holding = QUANT-FAITHFUL cited inequality that does NOT hold when re-evaluated on the "
                     "RESOLVED persisted source value (SOURCE-BACKED candidate: higher confidence than the "
                     "predecessor's free-text-only flags; sub-resolution ties below RES like '0.0 < 1e-10' are "
                     "EXCLUDED as comparator artifacts -- but the list still includes FAIL-verdict citations where "
                     "the failing inequality is EXPECTED to not-hold; VET should classify). unbacked_nontrivial = "
                     "nontrivial cited number that does NOT "
                     "appear as any persisted numeric leaf in its OWN citing metrics.json (prose-only / relative "
                     "threshold / potential miscitation)."),
        },
        "bands": {"HP_coverage_nt": HP_COVERAGE_NT, "HF_coverage_nt": HF_COVERAGE_NT,
                  "coverage_multiple_hp": COVERAGE_MULTIPLE_HP, "baseline_ledger_retrieval": BASELINE_LEDGER_RETRIEVAL,
                  "HP_lift": HP_LIFT, "HF_lift": HF_LIFT, "max_scrambled_nt": MAX_SCRAMBLED_NT,
                  "HP_op_agree": HP_OP_AGREE, "HF_op_agree": HF_OP_AGREE, "max_scram_residue": MAX_SCRAM_RESIDUE,
                  "min_claims_smoke": MIN_CLAIMS_SMOKE, "min_claims_full": MIN_CLAIMS_FULL,
                  "min_resolved_nt": MIN_RESOLVED_NT},
        "composition": {
            "predecessor": "exp_cert_ledger_numeric_entailment_v1 (Tier-2; retrieval_hit_rate=0.0328 REPLACED here)",
            "sibling_negative": "exp_cert_ledger_retrieval_coverage_v1 (content-addressable ceiling ~0.15-0.17)",
            "comparator_cell": "exp_math_rns_subtract_compare_v1 (MEASURED_MECHANISM; decode_then_compare leg reused)",
            "finding": ("SKIP retrieval entirely -> audit each cited claim directly against its citing cell's own "
                        "metrics.json. Every metrics.json is its own referent (exact, non-fuzzy). This lifts audit "
                        "coverage from the ~0.033 ledger-retrieval ceiling to the majority of cited claims."),
        },
        "scope_guardrail": ("NARROW glass-box MONITOR: the audit READS cell metrics + verdicts and CHECKS entailment. "
                            "It NEVER edits the ledger, never re-labels a cert_status, never edits code, never "
                            "triggers a re-encode. Not fluent-language, not self-improvement."),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }
    _write_metrics_atomic(output_dir, metrics)
    written = json.load(open(output_dir / "metrics.json"))
    assert written["run_mode"] == mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {mode}"

    _say(f"\n[{ANCHOR_NAME}] {verdict}: {vmsg}")
    _say(f"[{ANCHOR_NAME}] metrics -> {output_dir / 'metrics.json'}  elapsed={elapsed:.1f}s")
    # clean up per-seed partials on success
    for seed in seeds:
        pp = _partial_path(output_dir, seed)
        if pp.exists():
            try:
                pp.unlink()
            except OSError:
                pass
    return 0


def _append_units(per_unit, seed, res):
    per_unit.append({"seed": seed, "arm": "source_direct_coverage_nontrivial",
                     "value": res["coverage_source_direct_nontrivial"]})
    per_unit.append({"seed": seed, "arm": "scrambled_source_coverage_nontrivial",
                     "value": res["scrambled_source_coverage_nontrivial"]})
    per_unit.append({"seed": seed, "arm": "op_agreement_guard", "value": res["op_agreement_guard"]})
    per_unit.append({"seed": seed, "arm": "entailment_holds_rate", "value": res["entailment_holds_rate"]})


def _run_selftest() -> int:
    t0 = time.perf_counter()
    _setup_regime()
    ok_cmp = comparator_selftest(seed=7)
    a_ok, b_ok, c_ok, d_ok = resolution_selftest()
    ok_res = a_ok and b_ok and c_ok and d_ok
    # tiny real end-to-end over a harvest sample
    claims, file_leaves, order, _h, _sg = harvest(DATA_DIR)
    sample = claims[:80]
    e2e_ok = True
    cov = None
    if sample:
        sub_order = []
        seen = set()
        for c in sample:
            if c["exp_key"] not in seen:
                seen.add(c["exp_key"])
                sub_order.append(c["exp_key"])
        cbs = [phasor_codebook(m, SB, 6000 + 7 * 10 + i) for i, m in enumerate(_MODULI)]
        res, _hh, _aa = run_seed(7, sample, file_leaves, sub_order, cbs)
        cov = res["coverage_source_direct_all"]
        e2e_ok = (res["n_claims"] == len(sample)) and (res["coverage_source_direct_all"] > 0.0)
    ok = ok_cmp and ok_res and e2e_ok
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: comparator={ok_cmp} resolution={ok_res} "
         f"(present={a_ok} absent={b_ok} precision={c_ok} name={d_ok}) e2e={e2e_ok} "
         f"(n_sample={len(sample)} coverage_all={cov}) [{time.perf_counter()-t0:.1f}s]")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    args, _ = ap.parse_known_args()
    if args.self_test:
        return _run_selftest()
    if args.smoke or os.environ.get("HDLAB_RUN_MODE", "").lower() == "smoke" \
            or os.environ.get("HDLAB_EXP_NAME", "").endswith("_smoke"):
        return _run("smoke")
    return _run("full")


if __name__ == "__main__":
    _od = None
    try:
        _od = _out_dir()
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        if _od is not None:
            _write_crash_metrics(_od, e)
        raise
