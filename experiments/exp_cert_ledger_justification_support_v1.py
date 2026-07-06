# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate: per-claim supported flags under (real band) vs (adversarial band-flip)
#     vs (deranged band) are hash-distinct bool vectors over the SAME assembled cert claims -> they DIFFER.
# - final_metrics_atomicity: tmp_replace (metrics.json.tmp then os.replace). Per-seed checkpoint partials
#     (_partial_seed_<s>.json) written atomically; resume skips completed seeds.
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: this is a COVERAGE/RE-DERIVATION/DETECTION test, not a Gaussian-noise-floor sweep. The comparator
#     leg is exact by CRT decode (MEASURED_MECHANISM@data/exp_math_rns_subtract_compare_v1/metrics.json). The
#     discriminators are CONTRASTS: support-recall (verdict re-derivable from assembled evidence) vs the
#     ADVERSARIAL band-flip collapse (feed a wrong band -> the support-check must break). discriminator_reachability=True.
# - baseline_in_band (META_RULE_AG): the AG discriminator here is the ADVERSARIAL/deranged-band control collapse
#     (support minus scrambled-band support), NOT a difficulty gradient. support_recall SATURATES near 1.0 by
#     design -- that saturation IS the meaningful positive (certifications ARE backed by their evidence); it is
#     meaningful ONLY BECAUSE the band-scramble control collapses it to ~0. AG's 0.05 floor is EXEMPT for
#     support_recall (a high support-recall is the finding, not a saturation artifact); the scrambled-band support
#     (the "baseline") collapses to ~0 = well in band.
# - discriminator survives scale: the support re-derivation is a deterministic JSON-walk over the WHOLE cert_ledger
#     + the cited cells' own metrics.json, at FULL comparator N_DIM=8192. It is corpus-size-invariant; smoke reduces
#     only the number of comparator seeds. support-recall + adversarial collapse + op-agreement FIRE identically in
#     smoke (DISCRIMINATOR-MUST-SURVIVE-SCALE option A). The discriminator-fires gate (n_cert_claims + n_assemblable)
#     guards a too-sparse corpus.
# - HARD_PASS strictly above floor: support_recall HP 0.95 (HF 0.70); MEASURED@recon 1.0 clears by 0.05 (>> 5% of
#     the 0.25 band width). adversarial support HP <= 0.10; MEASURED 0.0. op-agreement HP 0.99; MEASURED 1.0.
# - HP_SCOPE per-arm: support_recall / op-agreement HP gates apply to the support MECHANISM only; adversarial_band
#     and deranged_band are FLOOR/CONTROL arms (must collapse, not clear HP).
# - cardinality_ok: EXPECTED_N_UNITS = len(seeds). support/assembly is seed-invariant (JSON-walk); seeds salt the
#     comparator phasor codebook + the deranged-band control (variance probe). verdict counts per_unit.
# - per-unit failure-class instrumentation (META_RULE_J): ledger + per-file parse failures caught by SPECIFIC class
#     (json.JSONDecodeError / OSError / ValueError), counted in metrics, non-gating; no bare except.
# - calibration_check: default_ok_for_this_regime -- the cited-value resolution tolerance is PRECISION-AWARE
#     (reused verbatim from source-direct; derived from the cited decimals, no tuned-for-pass free parameter). The
#     adversarial band-flip control collapse (support 1.0 -> 0.0) verifies the support-check actually reads the
#     band. Exact CRT decode for the comparator leg.
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# JUSTIFICATION-RETRIEVAL SELF-AUDIT RUNG: is each CERT CLAIM'S verdict SUPPORTED by its own assembled evidence?  v1
# ==============================================================================================================
# WHY (measured off-disk 2026-07-06, notes/research_justification_retrieval_rung_scoping_unblocked_by_source_direct
# _2026-07-06.md): source-direct entailment (exp_cert_ledger_source_direct_entailment_v1, MM, coverage 0.813) proved
# each cited NUMBER resolves against its citing metrics.json. This rung goes one level UP: for a given CERT CLAIM C
# (a cert_ledger entry's tier/verdict, referent_pointer -> a citing cell's metrics.json), ASSEMBLE C's justification
# and CHECK the recorded verdict is actually SUPPORTED by its OWN evidence -- re-derive the pass/fail from the
# backing and FLAG any claim whose verdict is NOT entailed by its assembled evidence (an unsupported certification).
#
# WHAT (this cell): join cert_ledger.jsonl claims to their referent metrics.json; for each claim ASSEMBLE the
# MACHINE-CLEAN gating evidence and re-derive support:
#   PATH A (structured_gate_claims): the cell's OWN declared gates {measured, threshold, op, gate_verdict}. Recompute
#          op(measured, threshold) via the VET'd decode_then_compare comparator and check it reproduces gate_verdict.
#   PATH B (verdict_msg cited NUM op NUM): REUSE source-direct's harvest + precision-aware resolution VERBATIM --
#          resolve the cited measured value (lhs) to a persisted leaf in the SAME citing metrics.json, quant-faithful
#          in-range, and re-check that the cited-as-true inequality actually HOLDS on the resolved source value.
# A cert claim is ASSEMBLABLE iff it yields >= 1 clean check. It is SUPPORTED iff ALL its clean checks hold.
#   support_recall = supported / assemblable = fraction of cert claims whose verdict is re-derivable from (consistent
#                    with) its own assembled evidence. MEASURED@recon 2026-07-06: 1.0 over 38 assemblable claims.
#   assembly_coverage = assemblable / cert-claims-with-existing-metrics. MEASURED 0.040 -- the HONEST residual: the
#                    vast majority of cert verdicts are PROSE (no machine-parseable band), bucketed not hidden.
#   GENUINE unsupported = assemblable PASS-family claim whose own clean evidence does NOT hold (expected ~0; MEASURED
#                    0). Zero genuine unsupported IS the meaningful positive: where evidence is machine-assemblable,
#                    the substrate's certifications ARE backed by it.
#
# FIRING CONTROLS (the load-bearing discriminators -- monitor-not-control has no accuracy dial, so the meaning comes
# from the controls collapsing):
#   adversarial_band : PRIMARY -- replace each check's band with a threshold the recorded expectation provably
#                      VIOLATES (band on the wrong side of the measured value). support MUST collapse to ~0. MEASURED
#                      0.0 (32/32 flip). Proves the support-check actually READS the band. [FLOOR]
#   deranged_band    : SECONDARY -- replace each check's (op, threshold) with a MISMATCHED real band from another
#                      claim (per-seed derangement). support collapses partially. MEASURED collapse 0.71. [FLOOR]
#   op_agreement     : GUARD -- decode_then_compare op-eval == Python oracle on the assembled checks (exact CRT
#                      decode; source-independent by construction -> a GUARD, not the discriminator). MEASURED 1.0.
#   scram_residue    : CONTROL -- derange residues before CRT -> garbage decode -> op-agreement collapses (confirms
#                      the CRT decode is load-bearing in the comparator leg). MEASURED ~0.47. [FLOOR]
#
# HONEST RESIDUAL (measured, reported, NOT gated): assembly buckets (prose_only_no_machine_band / cited_unresolved /
#   metrics_missing / no_verdict_msg) + a prereg-band coverage probe demonstrating WHY prereg bands are residual not
#   clean (multi-clause boolean + 3-seed-aggregation rules + name-match ambiguity make naive prereg re-derivation
#   LOSSY -> it produces FALSE unsupported flags, so prereg bands are deliberately EXCLUDED from the clean support
#   check and reported as the un-machine-parseable residual). ledger-vs-metrics verdict-family consistency reported.
#
# HONEST FRAMING (USER-LOCKED): NARROW glass-box MONITOR step. The audit READS the ledger + cell metrics + verdicts
# and RE-DERIVES entailment; it NEVER edits the ledger, never re-labels a cert_status, never edits code, never
# triggers a re-encode. Not fluent-language, not self-improvement. If support_recall did NOT clear its band, or the
# adversarial control did NOT collapse, that is a REAL bounded finding reported honestly (no smoke) -- NOT forced.
#
# ASCII-only. CPU default (numpy complex64 phasor comparator; no GPU, no LLM, no re-encode). Reads the live
# self-record referents (data/substrate_index/meta/cert_ledger.jsonl + the cited data/**/metrics.json). Run:
#   python experiments/exp_cert_ledger_justification_support_v1.py [--self-test | --smoke]   (bare -> full)

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

ANCHOR_NAME = "cert_ledger_justification_support_v1"
REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# REUSE source-direct's VET'd machinery VERBATIM (DRY): harvest regex + precision-aware resolution + the
# decode_then_compare comparator (quantize / substrate_compare / eval_op all close over SD's module globals,
# which SD._setup_regime() populates -- we call it once at run start).
import experiments.exp_cert_ledger_source_direct_entailment_v1 as SD  # noqa: E402

DATA_DIR = REPO / "data"
LEDGER_PATH = DATA_DIR / "substrate_index" / "meta" / "cert_ledger.jsonl"
PREREG_DIR = REPO / "preregs"

# ---- Pre-registered bands (calibrated from MEASURED@recon 2026-07-06; re-measured in-cell) ----
HP_SUPPORT = 0.95            # HARD_PASS: support_recall (supported / assemblable). MEASURED 1.0
HF_SUPPORT = 0.70            # HARD_FAIL: below -> the support-check itself is broken (evidence mostly fails on source)
MAX_ADVERSARIAL = 0.10       # FIRING CONTROL: adversarial band-flip support must collapse. MEASURED 0.0
MIN_DERANGE_COLLAPSE = 0.40  # SECONDARY: real-band derangement collapse (support - deranged). MEASURED 0.71
HP_OP_AGREE = 0.99           # GUARD HARD_PASS: comparator exactness on assembled checks. MEASURED 1.0
HF_OP_AGREE = 0.90           # HARD_FAIL: below -> comparator broke on real quantized data
MAX_SCRAM_RESIDUE = 0.72     # CONTROL: scrambled-residue comparator op-agreement near chance (CRT load-bearing)

MIN_CERT_CLAIMS_SMOKE = 300  # discriminator-fires: cert claims with a metrics referent (MEASURED 988)
MIN_CERT_CLAIMS_FULL = 300
MIN_ASSEMBLABLE_SMOKE = 25   # discriminator-fires: assemblable cert claims (MEASURED 38; headroom for remote drift)
MIN_ASSEMBLABLE_FULL = 25

ADV_DELTA_Q = 5              # quantized units to move an adversarial threshold to the violated side (0.005 > RES)

SEEDS_SMOKE = (7, 13, 19)            # multi-seed variance probe (comparator codebook + deranged-band control)
SEEDS_FULL = (7, 13, 19, 23, 29)     # >= 5 seeds (contract)

# prereg-residual band-clause parser (REPORTED-ONLY; demonstrates prereg bands are lossy -> residual)
_PREREG_CLAUSE = re.compile(r"`?([A-Za-z][A-Za-z0-9_]{2,})`?\s*(>=|<=|==|>|<)\s*(-?\d+\.?\d*)")


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
# Verdict-family normalization + path helpers
# ============================================================


def verdict_family(v) -> str:
    """Coarse verdict family for cross-referent consistency (ledger vs metrics.json own verdict)."""
    if not v:
        return "NONE"
    vu = str(v).upper()
    if "HARD_FAIL" in vu or "PROVEN_BOUND" in vu or "HONEST_NEGATIVE" in vu or "_MISS" in vu:
        return "FAIL"
    if "MIDDLE" in vu or "PARTIAL" in vu:
        return "MIDDLE"
    if "PASS" in vu or "MECHANISM" in vu or "MEASURED" in vu or "CHAIN_GRADE" in vu:
        return "PASS"
    return "OTHER"


def _norm_path(p) -> str:
    return str(p).replace("\\", "/").lstrip("./") if p else ""


def _exp_key_of(path: str) -> str:
    for x in _norm_path(path).split("/"):
        if x.startswith("exp_"):
            return x
    return ""


# ============================================================
# Load cert claims (the referents being audited) + citing metrics.json leaves
# ============================================================


def load_cert_claims(ledger_path: Path):
    """Parse cert_ledger.jsonl -> claims with a metrics_path referent. Per-line parse failures counted by class
    (META_RULE_J), never silently gating. Returns (claims, stats)."""
    claims = []
    n_lines = 0
    fail_json = 0
    n_no_referent = 0
    for line in open(ledger_path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        n_lines += 1
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            fail_json += 1
            continue
        rp = d.get("referent_pointer")
        mp = None
        if isinstance(rp, dict):
            mp = rp.get("metrics_path")
        elif isinstance(rp, str):
            mp = rp
        if not mp:
            n_no_referent += 1
            continue
        mpn = _norm_path(mp)
        if not mpn.endswith("metrics.json"):
            n_no_referent += 1
            continue
        claims.append({
            "atom_id": d.get("atom_id"),
            "verdict": d.get("verdict"),
            "cert_class": d.get("cert_class"),
            "cert_status": d.get("cert_status"),
            "mp": mpn,
        })
    stats = {"n_ledger_lines": n_lines, "n_claims_with_metrics_referent": len(claims),
             "n_no_referent": n_no_referent, "ledger_parse_failures": {"json_decode": fail_json}}
    return claims, stats


def load_metrics_file(mp: str, cache: dict):
    """Load a citing metrics.json ONCE; cache leaves + verdict + structured_gate_claims. Returns dict|None."""
    if mp in cache:
        return cache[mp]
    fp = REPO / mp
    r = None
    if fp.exists():
        try:
            d = json.load(open(fp, encoding="utf-8"))
            leaves = []
            SD.collect_numeric_leaves(d, "", leaves)
            r = {
                "vm": d.get("verdict_msg") if isinstance(d.get("verdict_msg"), str) else None,
                "verdict": d.get("verdict"),
                "leaves": leaves,
                "sgc": d.get("structured_gate_claims") if isinstance(d.get("structured_gate_claims"), list) else None,
                "err": None,
            }
        except json.JSONDecodeError:
            r = {"err": "json_decode"}
        except (OSError, ValueError) as e:
            r = {"err": type(e).__name__}
    else:
        r = {"err": "missing"}
    cache[mp] = r
    return r


# ============================================================
# Assemble the machine-clean gating evidence (the two clean paths) per cert claim
# ============================================================


def assemble_checks(fc: dict):
    """Return a list of clean checks for one cert claim's citing metrics.json.
    Each check: dict(src, op, qa, qb, expect) where qa/qb are quantized ints and `expect` is the recorded truth.
    support(check) := (comparator op-eval of `qa op qb`) == expect."""
    checks = []
    if not fc or fc.get("err"):
        return checks
    leaves = fc["leaves"]
    # PATH A: structured_gate_claims -- the cell's OWN declared {measured, threshold, op, gate_verdict}.
    if fc.get("sgc"):
        for g in fc["sgc"]:
            if not isinstance(g, dict):
                continue
            try:
                meas = float(g["measured"]); thr = float(g["threshold"]); op = str(g["op"]); gv = bool(g["gate_verdict"])
            except (KeyError, TypeError, ValueError):
                continue
            if op not in (">=", ">", "<=", "<", "=="):
                continue
            qa, qb = SD.quantize(meas), SD.quantize(thr)
            if qa is None or qb is None:
                continue
            checks.append({"src": "sgc", "op": op, "qa": qa, "qb": qb, "expect": gv})
    # PATH B: verdict_msg cited NUM op NUM, resolved to a name-matched persisted leaf (source-direct verbatim).
    vm = fc.get("vm")
    if isinstance(vm, str) and vm:
        for m in SD._INEQ.finditer(vm):
            name, lhs_s, op, rhs_s = m.group(1), m.group(2), m.group(3), m.group(4)
            try:
                lhs = float(lhs_s); rhs = float(rhs_s)
            except ValueError:
                continue
            if lhs.is_integer() and rhs.is_integer() and abs(lhs) > 1000 and abs(rhs) > 1000:
                continue
            if SD._is_trivial(lhs):
                continue
            r = SD.resolve_value(lhs, lhs_s, leaves, name or "")
            if not r["resolved"]:
                continue
            v = r["value"]
            qa, qb = SD.quantize(v), SD.quantize(rhs)
            if qa is None or qb is None:
                continue
            # quant-faithful: resolved value and threshold distinguishable at the comparator resolution
            if not ((abs(v - rhs) >= SD.RES) or (v == rhs)):
                continue
            # cited-as-true: a cited inequality in a verdict_msg is presented as satisfied -> expect True.
            checks.append({"src": "cited", "op": op, "qa": qa, "qb": qb, "expect": True})
    return checks


def _check_holds(ch, cbs, op=None, qb=None, scramble=None) -> bool:
    """comparator op-eval of (qa OP qb) == recorded expect. op/qb overrides drive the scramble controls."""
    _op = op if op is not None else ch["op"]
    _qb = qb if qb is not None else ch["qb"]
    cmp3 = SD.substrate_compare(ch["qa"], _qb, cbs, scramble=scramble)
    return SD.eval_op(cmp3, _op) == ch["expect"]


def _adversarial_qb(ch):
    """A threshold the recorded expectation provably VIOLATES: force comparator op-eval(qa OP qb_adv) = NOT expect.
    qb_adv is moved ADV_DELTA_Q quantized units to the violating side. Returns int or None (out of range)."""
    qa, op, expect = ch["qa"], ch["op"], ch["expect"]
    d = ADV_DELTA_Q
    # Want holds_adv := eval_op(compare(qa, qb_adv), op) == expect to be FALSE, i.e. op-eval must equal (not expect).
    if op in (">=", ">"):
        # >= / >: True side is qa >= qb. To make op-eval == expect FALSE:
        qb = (qa + d) if expect else (qa - d)  # expect True -> want qa<qb (op False); expect False -> want qa>qb
        if op == ">":
            qb = qa if expect else (qa - d)     # qa>qa is False; qa>(qa-d) is True
    elif op in ("<=", "<"):
        qb = (qa - d) if expect else (qa + d)
        if op == "<":
            qb = qa if expect else (qa + d)
    else:  # ==
        qb = (qa + d) if expect else qa         # expect True -> unequal (False); expect False -> equal (True)
    if qb < 0 or qb >= SD._M:
        return None
    return int(qb)


# ============================================================
# Per-seed run (support/assembly seed-invariant; comparator codebook + deranged-band control salt the seed)
# ============================================================


def run_seed(seed, claims, file_cache, cbs):
    """Re-derive support for every cert claim; measure support_recall + adversarial/deranged collapse + op-agreement
    + genuine-unsupported candidates + assembly residual buckets. Deterministic given the corpus + seed."""
    rng = np.random.default_rng(20260706 + seed)
    derange = SD._cyclic_derangement(SD.R_MODULI)

    # first pass: assemble checks per claim + build the global band bank for the derangement control
    per_claim = []
    band_bank = []          # (op, qb) pool of REAL bands, for the deranged-band control
    src_counts = {"sgc": 0, "cited": 0}
    n_exist = 0
    buckets = {"metrics_missing": 0, "parse_error": 0, "no_verdict_msg": 0,
               "prose_only_no_machine_band": 0, "cited_unresolved_or_prose": 0, "assemblable": 0}
    ledger_metrics_consistent = 0
    ledger_metrics_comparable = 0
    for c in claims:
        fc = load_metrics_file(c["mp"], file_cache)
        if not fc or fc.get("err"):
            if fc and fc.get("err") == "missing":
                buckets["metrics_missing"] += 1
            else:
                buckets["parse_error"] += 1
            continue
        n_exist += 1
        # ledger-vs-metrics verdict-family consistency (REPORTED)
        mf = verdict_family(fc.get("verdict"))
        lf = verdict_family(c["verdict"])
        if mf != "NONE" and lf != "NONE":
            ledger_metrics_comparable += 1
            if mf == lf:
                ledger_metrics_consistent += 1
        checks = assemble_checks(fc)
        if not checks:
            if fc.get("vm") is None:
                buckets["no_verdict_msg"] += 1
            else:
                buckets["prose_only_no_machine_band"] += 1
            continue
        buckets["assemblable"] += 1
        for ch in checks:
            src_counts[ch["src"]] += 1
            band_bank.append((ch["op"], ch["qb"]))
        per_claim.append((c, checks))

    n_assemblable = len(per_claim)
    B = len(band_bank)

    # second pass: support (real band) + adversarial band-flip + deranged band + op-agreement + scram-residue
    n_supported = 0
    n_supported_adv = 0
    n_supported_der = 0
    op_agree = op_n = 0
    scr_res_agree = scr_res_n = 0
    genuine = []            # PASS-family claims whose own clean evidence does NOT hold (expected 0)
    flags_real, flags_adv, flags_der = [], [], []
    for (c, checks) in per_claim:
        real_all = True
        adv_all = True
        der_all = True
        adv_countable = True
        failing = []
        for ch in checks:
            holds = _check_holds(ch, cbs)
            real_all = real_all and holds
            if not holds:
                failing.append({"src": ch["src"], "op": ch["op"]})
            # op-agreement guard: comparator op-eval == python oracle on the SAME (qa, qb)
            cmp_ora = 1 if ch["qa"] > ch["qb"] else (0 if ch["qa"] == ch["qb"] else -1)
            op_n += 1
            op_agree += 1 if SD.eval_op(SD.substrate_compare(ch["qa"], ch["qb"], cbs), ch["op"]) == SD.eval_op(cmp_ora, ch["op"]) else 0
            # scram-residue comparator control
            scr_res_n += 1
            scr_res_agree += 1 if SD.eval_op(SD.substrate_compare(ch["qa"], ch["qb"], cbs, scramble=derange), ch["op"]) == SD.eval_op(cmp_ora, ch["op"]) else 0
            # adversarial band-flip (must break)
            qadv = _adversarial_qb(ch)
            if qadv is None:
                adv_countable = False
            else:
                adv_all = adv_all and _check_holds(ch, cbs, qb=qadv)
            # deranged band (mismatched real band from another check)
            if B > 1:
                oop, oqb = band_bank[int(rng.integers(0, B))]
                for _ in range(6):
                    if oqb != ch["qb"] or oop != ch["op"]:
                        break
                    oop, oqb = band_bank[int(rng.integers(0, B))]
                der_all = der_all and _check_holds(ch, cbs, op=oop, qb=oqb)
        flags_real.append(1 if real_all else 0)
        flags_adv.append(1 if (adv_countable and adv_all) else 0)
        flags_der.append(1 if der_all else 0)
        if real_all:
            n_supported += 1
        else:
            if verdict_family(c["verdict"]) == "PASS" and len(genuine) < 40:
                genuine.append({"atom_id": c["atom_id"], "verdict": c["verdict"], "mp": c["mp"],
                                "failing_checks": failing[:4]})
        if adv_countable and adv_all:
            n_supported_adv += 1
        if der_all:
            n_supported_der += 1

    support_recall = n_supported / n_assemblable if n_assemblable else float("nan")
    adv_support = n_supported_adv / n_assemblable if n_assemblable else float("nan")
    der_support = n_supported_der / n_assemblable if n_assemblable else float("nan")
    op_agreement = op_agree / op_n if op_n else float("nan")
    scr_res_rate = scr_res_agree / scr_res_n if scr_res_n else float("nan")
    assembly_coverage = n_assemblable / n_exist if n_exist else float("nan")
    lm_consistency = ledger_metrics_consistent / ledger_metrics_comparable if ledger_metrics_comparable else float("nan")

    res = {
        "seed": seed,
        "n_cert_claims": len(claims),
        "n_metrics_exist": n_exist,
        "n_assemblable": n_assemblable,
        "n_checks": op_n,
        "check_sources": src_counts,
        "support_recall": round(support_recall, 4) if support_recall == support_recall else None,
        "assembly_coverage": round(assembly_coverage, 4) if assembly_coverage == assembly_coverage else None,
        "adversarial_band_support": round(adv_support, 4) if adv_support == adv_support else None,
        "deranged_band_support": round(der_support, 4) if der_support == der_support else None,
        "deranged_band_collapse": round(support_recall - der_support, 4) if (support_recall == support_recall and der_support == der_support) else None,
        "op_agreement_guard": round(op_agreement, 4) if op_agreement == op_agreement else None,
        "scram_residue_agreement": round(scr_res_rate, 4) if scr_res_rate == scr_res_rate else None,
        "ledger_metrics_verdict_consistency": round(lm_consistency, 4) if lm_consistency == lm_consistency else None,
        "assembly_buckets": buckets,
        "n_genuine_unsupported_pass_family": len([g for g in genuine]),
    }
    hashes = {
        "real": hashlib.sha256(np.asarray(flags_real, dtype=np.int8).tobytes()).hexdigest(),
        "adv": hashlib.sha256(np.asarray(flags_adv, dtype=np.int8).tobytes()).hexdigest(),
        "der": hashlib.sha256(np.asarray(flags_der, dtype=np.int8).tobytes()).hexdigest(),
    }
    return res, hashes, {"genuine_unsupported": genuine}


# ============================================================
# Prereg-band residual probe (REPORTED-ONLY; demonstrates prereg bands are lossy -> residual, NOT clean)
# ============================================================


def prereg_residual_probe(claims, file_cache):
    """Over the NON-assemblable cert claims, measure how many even have a mappable prereg and how many carry a
    parseable single-clause `name op threshold` band -- and how many NAIVE prereg re-derivations CONFLICT with the
    recorded verdict. A high conflict count demonstrates prereg-band re-derivation is LOSSY (multi-clause boolean +
    3-seed-aggregation rules + name-match ambiguity), so prereg bands are deliberately EXCLUDED from the clean
    support-check and reported as the un-machine-parseable residual. Best-effort; never gates."""
    preg_files = list(PREREG_DIR.glob("*.md"))
    stems = [(pf, pf.stem.lower()) for pf in preg_files]

    def find_prereg(ek):
        if not ek:
            return None
        a = ek[4:] if ek.startswith("exp_") else ek
        a = re.sub(r"_seed_\d+.*$", "", a)
        a = re.sub(r"_(smoke|FULL|full)$", "", a).lower()
        best, blen = None, 0
        for pf, stem in stems:
            if len(a) >= 4 and a in stem and len(a) > blen:
                best, blen = pf, len(a)
        return best

    n_mapped = n_parseable = n_naive_conflict = n_examined = 0
    for c in claims:
        fc = file_cache.get(c["mp"])
        if not fc or fc.get("err"):
            continue
        # only examine claims NOT already clean-assemblable
        if assemble_checks(fc):
            continue
        n_examined += 1
        pf = find_prereg(_exp_key_of(c["mp"]))
        if not pf:
            continue
        n_mapped += 1
        try:
            text = pf.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        clauses = []
        for line in text.splitlines():
            up = line.strip().upper()
            role = "PASS" if up.startswith(("- HARD_PASS", "HARD_PASS")) else ("FAIL" if up.startswith(("- HARD_FAIL", "HARD_FAIL")) else None)
            if role is None:
                continue
            for m in _PREREG_CLAUSE.finditer(line):
                nm, op, thr = m.group(1), m.group(2), m.group(3)
                if nm.upper() in ("HARD_PASS", "HARD_FAIL", "AND", "OR", "PLUS"):
                    continue
                try:
                    clauses.append((nm, op, float(thr), role))
                except ValueError:
                    continue
        if not clauses:
            continue
        n_parseable += 1
        # naive re-derivation: for a PASS-family recorded verdict, does at least one PASS band-clause FAIL on a
        # name-matched leaf? (that would NAIVELY read as unsupported -- but is a KNOWN false positive)
        leaves = fc["leaves"]
        lf = verdict_family(c["verdict"])
        conflict = False
        for (nm, op, thr, role) in clauses:
            cand = [(k, v) for (k, v) in leaves if nm.lower() in k.lower() and not SD._is_trivial(v)]
            if not cand:
                continue
            v = cand[0][1]
            qa, qb = SD.quantize(v), SD.quantize(thr)
            if qa is None or qb is None:
                continue
            if not ((abs(v - thr) >= SD.RES) or (v == thr)):
                continue
            holds = SD.eval_op(SD.substrate_compare(qa, qb, [SD.phasor_codebook(m, SD.SB, 6000 + i) for i, m in enumerate(SD._MODULI)]), op)
            if role == "PASS" and lf == "PASS" and not holds:
                conflict = True
        if conflict:
            n_naive_conflict += 1
    return {
        "n_non_assemblable_examined": n_examined,
        "n_with_mappable_prereg": n_mapped,
        "n_prereg_with_parseable_clause": n_parseable,
        "n_naive_prereg_conflict_FALSE_POSITIVES": n_naive_conflict,
        "note": ("REPORTED-ONLY. n_naive_prereg_conflict is the count of cert claims where a NAIVE single-clause "
                 "prereg re-derivation would FALSELY read as unsupported (a PASS-family verdict whose per-file "
                 "leaf fails a top-level PASS band-clause). These are FALSE POSITIVES caused by multi-clause "
                 "boolean bands + 3-seed-aggregation rules + name-match ambiguity -- proof that prereg-band "
                 "re-derivation is LOSSY, hence EXCLUDED from the clean support-check and reported as the "
                 "un-machine-parseable residual (the coverage gap the scoping note asked to measure)."),
    }


# ============================================================
# Formula self-tests (MANDATORY)
# ============================================================


def support_selftest(cbs) -> tuple:
    """Synthetic checks prove the support re-derivation is SPECIFIC (not a wildcard pass):
    (a) a resolved cited check whose inequality HOLDS -> supported;
    (b) a resolved cited check whose inequality does NOT hold -> unsupported (a genuine candidate);
    (c) adversarial band-flip of (a) -> supported flips to FALSE (the firing control fires);
    (d) an SGC gate whose op(measured,threshold) reproduces gate_verdict -> supported; a gate with a WRONG
        gate_verdict -> unsupported (the check reads the declared gate)."""
    # (a) 0.85 >= 0.60 True, expect True -> holds
    ch_a = {"src": "cited", "op": ">=", "qa": SD.quantize(0.85), "qb": SD.quantize(0.60), "expect": True}
    a_ok = _check_holds(ch_a, cbs) is True
    # (b) 0.15 >= 0.60 False, expect True -> does not hold
    ch_b = {"src": "cited", "op": ">=", "qa": SD.quantize(0.15), "qb": SD.quantize(0.60), "expect": True}
    b_ok = _check_holds(ch_b, cbs) is False
    # (c) adversarial flip of (a)
    qadv = _adversarial_qb(ch_a)
    c_ok = (qadv is not None) and (_check_holds(ch_a, cbs, qb=qadv) is False)
    # (d) SGC gate reproduce vs wrong-verdict
    ch_d_ok = {"src": "sgc", "op": ">=", "qa": SD.quantize(0.90), "qb": SD.quantize(0.60), "expect": True}
    ch_d_bad = {"src": "sgc", "op": ">=", "qa": SD.quantize(0.90), "qb": SD.quantize(0.60), "expect": False}
    d_ok = (_check_holds(ch_d_ok, cbs) is True) and (_check_holds(ch_d_bad, cbs) is False)
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


def classify(per_seed, seeds, mode, n_cert_claims, n_assemblable, min_cert_claims, min_assemblable):
    support = _meanv([per_seed[s]["support_recall"] for s in seeds])
    cov = _meanv([per_seed[s]["assembly_coverage"] for s in seeds])
    adv_max = _maxv([per_seed[s]["adversarial_band_support"] for s in seeds])
    der_collapse_min = _minv([per_seed[s]["deranged_band_collapse"] for s in seeds])
    op_min = _minv([per_seed[s]["op_agreement_guard"] for s in seeds])
    scr_res_max = _maxv([per_seed[s]["scram_residue_agreement"] for s in seeds])
    genuine = _maxv([per_seed[s]["n_genuine_unsupported_pass_family"] for s in seeds])

    diag = (f"n_cert_claims={n_cert_claims} n_assemblable={n_assemblable} support_recall={support:.4f} "
            f"assembly_coverage={cov:.4f} adversarial_band_support_max={adv_max if adv_max == adv_max else float('nan'):.4f} "
            f"deranged_collapse_min={der_collapse_min if der_collapse_min == der_collapse_min else float('nan'):.4f} "
            f"op_agreement_min={op_min if op_min == op_min else float('nan'):.4f} "
            f"scram_residue_max={scr_res_max if scr_res_max == scr_res_max else float('nan'):.4f} "
            f"genuine_unsupported={int(genuine) if genuine == genuine else '?'}")

    # --- discriminator-fires / control gates ---
    if n_cert_claims < min_cert_claims:
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"insufficient cert claims with a metrics referent: {n_cert_claims} < {min_cert_claims}. {diag}", False)
    if n_assemblable < min_assemblable:
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"insufficient assemblable cert claims: {n_assemblable} < {min_assemblable} (too few machine-parseable "
                f"gating referents in this corpus). {diag}", False)
    if op_min == op_min and op_min < HF_OP_AGREE:
        return ("HARD_FAIL",
                f"COMPARATOR BROKE on real quantized data: op_agreement min={op_min:.4f} < {HF_OP_AGREE}. {diag}", False)
    if scr_res_max == scr_res_max and scr_res_max > MAX_SCRAM_RESIDUE:
        return ("CONTROL_DID_NOT_COLLAPSE",
                f"scrambled-RESIDUE comparator op-agreement did NOT collapse (max={scr_res_max:.4f} > "
                f"{MAX_SCRAM_RESIDUE}): CRT decode not load-bearing. {diag}", False)
    if not (adv_max == adv_max and adv_max <= MAX_ADVERSARIAL):
        return ("CONTROL_DID_NOT_COLLAPSE",
                f"ADVERSARIAL band-flip did NOT collapse support (max={adv_max if adv_max == adv_max else float('nan'):.4f} "
                f"> {MAX_ADVERSARIAL}): the support-check is NOT reading the band -> re-derivation is vacuous. {diag}", False)

    # --- HARD_FAIL band ---
    if support < HF_SUPPORT:
        return ("HARD_FAIL",
                f"SUPPORT-CHECK BROKEN: support_recall={support:.4f} < {HF_SUPPORT} (assembled cited-as-true evidence "
                f"mostly does NOT hold on the resolved source values -> resolution/comparator fault, not a ledger "
                f"finding). {diag}", True)

    # --- smoke: discriminator fired + controls collapsed + support meaningful ---
    if mode == "smoke":
        return ("HARD_PASS",
                f"SMOKE_SUPPORT_FIRES: re-derived support_recall={support:.4f} of {n_assemblable} assemblable cert "
                f"claims from their OWN assembled evidence at FULL comparator N_DIM={SD.N_DIM}; ADVERSARIAL band-flip "
                f"collapses support to max={adv_max if adv_max == adv_max else float('nan'):.4f} (the firing control); "
                f"deranged-band collapse_min={der_collapse_min if der_collapse_min == der_collapse_min else float('nan'):.4f}; "
                f"comparator op-agreement min={op_min if op_min == op_min else float('nan'):.4f} (==oracle); "
                f"genuine unsupported certifications={int(genuine) if genuine == genuine else '?'}. Assembly residual "
                f"(prose-only bands) measured + bucketed. {diag}", True)

    # --- FULL bands ---
    hard_pass = (support >= HP_SUPPORT and n_assemblable >= min_assemblable
                 and (adv_max == adv_max and adv_max <= MAX_ADVERSARIAL)
                 and (op_min != op_min or op_min >= HP_OP_AGREE)
                 and (der_collapse_min != der_collapse_min or der_collapse_min >= MIN_DERANGE_COLLAPSE))
    if hard_pass:
        gtxt = (f"ZERO genuine unsupported certifications" if (genuine == genuine and genuine == 0)
                else f"{int(genuine) if genuine == genuine else '?'} GENUINE unsupported certification candidate(s) surfaced for VET")
        return ("HARD_PASS",
                f"JUSTIFICATION-RETRIEVAL RUNG MEANINGFUL: over {n_cert_claims} cert claims (metrics-referenced) the "
                f"audit ASSEMBLES each claim's machine-clean gating evidence (declared structured gates + cited "
                f"inequalities resolved DIRECTLY against the citing cell's OWN metrics.json) and RE-DERIVES the "
                f"verdict -- support_recall={support:.4f} of {n_assemblable} assemblable claims are re-derivable from "
                f"(consistent with) their own evidence. {gtxt}: where a cert claim's evidence is machine-assemblable, "
                f"its certification IS backed by that evidence. FIRING CONTROL: feeding an ADVERSARIAL band (a "
                f"threshold the recorded expectation provably violates) collapses support to "
                f"max={adv_max if adv_max == adv_max else float('nan'):.4f} <= {MAX_ADVERSARIAL} -> the support-check "
                f"genuinely READS the band, not vacuously passing; a real-band DERANGEMENT collapses it by "
                f">= {der_collapse_min if der_collapse_min == der_collapse_min else float('nan'):.4f}. COMPARATOR GUARD: "
                f"decode_then_compare op-agreement min={op_min if op_min == op_min else float('nan'):.4f} (==Python "
                f"oracle, exact CRT decode); scram-residue control collapses "
                f"(max={scr_res_max if scr_res_max == scr_res_max else float('nan'):.4f}). HONEST RESIDUAL: "
                f"assembly_coverage={cov:.4f} -- the MAJORITY of cert verdicts are PROSE (no machine-parseable band; "
                f"multi-clause boolean / 3-seed-aggregation / prose-only prereg criteria), measured + bucketed, not "
                f"hidden. NARROW glass-box MONITOR; re-derives verdicts from persisted evidence, NEVER edits the "
                f"ledger/cells/code. {diag}", True)
    return ("MIDDLE_BAND",
            f"support re-derivation is above the HARD_FAIL floor but below HARD_PASS on >= 1 gate "
            f"(support_recall={support:.4f} vs {HP_SUPPORT}; adversarial_max={adv_max if adv_max == adv_max else float('nan'):.4f} "
            f"vs {MAX_ADVERSARIAL}; op_agreement_min={op_min if op_min == op_min else float('nan'):.4f} vs {HP_OP_AGREE}; "
            f"deranged_collapse_min={der_collapse_min if der_collapse_min == der_collapse_min else float('nan'):.4f} vs "
            f"{MIN_DERANGE_COLLAPSE}). This may itself be a real finding (genuine unsupported certifications lower "
            f"support_recall) -- see audit_candidates. Honest partial. {diag}", True)


# ============================================================
# Config + driver
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"seeds": (7,), "min_cert_claims": 20, "min_assemblable": 5}
    if mode == "smoke":
        return {"seeds": SEEDS_SMOKE, "min_cert_claims": MIN_CERT_CLAIMS_SMOKE, "min_assemblable": MIN_ASSEMBLABLE_SMOKE}
    return {"seeds": SEEDS_FULL, "min_cert_claims": MIN_CERT_CLAIMS_FULL, "min_assemblable": MIN_ASSEMBLABLE_FULL}


def _partial_path(output_dir: Path, seed: int) -> Path:
    return output_dir / f"_partial_seed_{seed}.json"


def _append_units(per_unit, seed, res):
    per_unit.append({"seed": seed, "arm": "support_recall", "value": res["support_recall"]})
    per_unit.append({"seed": seed, "arm": "adversarial_band_support", "value": res["adversarial_band_support"]})
    per_unit.append({"seed": seed, "arm": "op_agreement_guard", "value": res["op_agreement_guard"]})
    per_unit.append({"seed": seed, "arm": "deranged_band_support", "value": res["deranged_band_support"]})


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    SD._setup_regime()      # populate SD's CRT globals used by quantize / substrate_compare
    cfg = get_config(mode)
    seeds = cfg["seeds"]
    exp_units = len(seeds)
    _write_start_marker(output_dir, mode, exp_units)
    _say(f"[{ANCHOR_NAME}] mode={mode} regime={SD.REGIME} moduli={SD._MODULI} M={SD._M} N={SD.N_DIM} "
         f"SB={SD.SB} SCALE={SD.SCALE} OFFSET={SD.OFFSET} seeds={seeds} expected_units={exp_units}")

    # formula self-tests (ALL modes)
    if not SD.comparator_selftest(seed=seeds[0]):
        raise AssertionError("COMPARATOR_SELFTEST_FAIL (op-eval != oracle, or round-trip inexact, or "
                             "scrambled-residue did not collapse)")
    cbs0 = [SD.phasor_codebook(m, SD.SB, 6000 + seeds[0] * 10 + i) for i, m in enumerate(SD._MODULI)]
    a_ok, b_ok, c_ok, d_ok = support_selftest(cbs0)
    if not (a_ok and b_ok and c_ok and d_ok):
        raise AssertionError(f"SUPPORT_SELFTEST_FAIL: holds={a_ok} not_holds={b_ok} adversarial_flip={c_ok} sgc={d_ok}")
    _say(f"[{ANCHOR_NAME}] formula self-tests PASSED (comparator op-eval + round-trip + scram-collapse; "
         f"support holds/not-holds/adversarial-flip/sgc)")

    # load cert claims (the referents) ONCE
    claims, cstats = load_cert_claims(LEDGER_PATH)
    n_cert_claims = len(claims)
    _say(f"[{ANCHOR_NAME}] cert_ledger: {cstats['n_ledger_lines']} lines, "
         f"{n_cert_claims} claims with a metrics referent, {cstats['n_no_referent']} no-referent, "
         f"parse_fail={cstats['ledger_parse_failures']}")
    if n_cert_claims == 0:
        raise AssertionError("EMPTY_REFERENT: 0 cert claims with a metrics referent")

    file_cache = {}
    per_seed = {}
    hashes_all = {}
    audit_union = {}
    per_unit = []
    n_assemblable = None
    for si, seed in enumerate(seeds):
        pp = _partial_path(output_dir, seed)
        if pp.exists():
            try:
                saved = json.load(open(pp, encoding="utf-8"))
                if saved.get("seed") == seed and saved.get("n_cert_claims") == n_cert_claims:
                    per_seed[seed] = saved["res"]
                    hashes_all[seed] = saved["hashes"]
                    for a in saved.get("audit", {}).get("genuine_unsupported", []):
                        audit_union[(a["atom_id"], a["mp"])] = a
                    n_assemblable = saved["res"]["n_assemblable"]
                    _append_units(per_unit, seed, saved["res"])
                    _say(f"  [seed {seed}] RESUMED from checkpoint")
                    continue
            except (json.JSONDecodeError, KeyError, OSError):
                pass
        cbs = [SD.phasor_codebook(m, SD.SB, 6000 + seed * 10 + i) for i, m in enumerate(SD._MODULI)]
        res, hashes, audit = run_seed(seed, claims, file_cache, cbs)
        per_seed[seed] = res
        hashes_all[seed] = hashes
        n_assemblable = res["n_assemblable"]
        for a in audit["genuine_unsupported"]:
            audit_union[(a["atom_id"], a["mp"])] = a
        _write_json_atomic(pp, {"seed": seed, "n_cert_claims": n_cert_claims, "res": res,
                                "hashes": hashes, "audit": audit})
        _append_units(per_unit, seed, res)
        _heartbeat(output_dir, si + 1, len(seeds), t0,
                   extra={"seed": seed, "support_recall": res["support_recall"],
                          "adversarial": res["adversarial_band_support"], "n_assemblable": res["n_assemblable"]})
        _say(f"  [seed {seed}] support_recall={res['support_recall']} "
             f"assembly_coverage={res['assembly_coverage']} adversarial={res['adversarial_band_support']} "
             f"deranged={res['deranged_band_support']} op_agree={res['op_agreement_guard']} "
             f"scram_residue={res['scram_residue_agreement']} genuine={res['n_genuine_unsupported_pass_family']}")

    # arms_differ (META_RULE_AF): real-band vs adversarial-band vs deranged-band supported-flag vectors differ
    reasons = []
    for seed in seeds:
        h = hashes_all[seed]
        if h["real"] == h["adv"]:
            reasons.append(f"seed{seed}:real==adversarial supported-flags")
        if h["real"] == h["der"]:
            reasons.append(f"seed{seed}:real==deranged supported-flags")
    arms_differ_ok = not reasons
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: " + "; ".join(reasons))

    # prereg residual probe (REPORTED-ONLY; best-effort, never gates)
    try:
        prereg_probe = prereg_residual_probe(claims, file_cache)
    except Exception as e:  # non-gating REPORTED sub-measurement
        prereg_probe = {"error": f"{type(e).__name__}: {str(e)[:200]}"}

    verdict, vmsg, controls_ok = classify(per_seed, seeds, mode, n_cert_claims, n_assemblable,
                                          cfg["min_cert_claims"], cfg["min_assemblable"])
    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: justification-retrieval support-check re-derives cert verdicts from own evidence ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(seeds),
        "n_units": len(per_unit),
        "expected_n_units": exp_units,
        "cardinality_ok": len(per_unit) >= exp_units,
        "n_cert_claims": n_cert_claims,
        "n_assemblable": n_assemblable,
        "config": {
            "regime": SD.REGIME, "moduli": list(SD._MODULI), "M": SD._M, "N": SD.N_DIM, "SB": SD.SB,
            "SCALE": SD.SCALE, "OFFSET": SD.OFFSET, "RES": SD.RES, "seeds": list(seeds),
            "ledger_path": str(LEDGER_PATH.relative_to(REPO)).replace("\\", "/"),
            "assembly_paths": "structured_gate_claims (declared gates) + verdict_msg cited NUM op NUM resolved source-direct",
            "comparison_leg": "decode_then_compare_two_CRT_decodes_from_exp_math_rns_subtract_compare_v1 (reused)",
            "resolution_leg": "source_direct precision_aware_leaf_lookup (reused from exp_cert_ledger_source_direct_entailment_v1)",
            "firing_control": "adversarial_band_flip (primary) + real_band_derangement (secondary)",
            "storage_strategy": "no_storage_algebraic (comparator CRT; ledger + source lookups are direct file reads)",
        },
        "cert_ledger_stats": cstats,
        "arms": {str(s): per_seed[s] for s in seeds},
        "per_unit": per_unit,
        "arms_differ_verified": arms_differ_ok,
        "controls": {"controls_collapsed": controls_ok},
        "prereg_residual_probe": prereg_probe,
        "audit_candidates": {
            "genuine_unsupported": list(audit_union.values())[:40],
            "n_genuine_unsupported_total": len(audit_union),
            "note": ("genuine_unsupported = a PASS-family cert claim whose OWN machine-clean assembled evidence "
                     "(declared gate or cited-as-true inequality resolved against its own metrics.json) does NOT "
                     "hold when re-evaluated via the VET'd comparator -- an UNSUPPORTED certification candidate for "
                     "VET. Expected ~zero (source-direct found records self-consistent); zero IS the meaningful "
                     "positive that certifications are backed by their evidence."),
        },
        "bands": {"HP_support_recall": HP_SUPPORT, "HF_support_recall": HF_SUPPORT,
                  "max_adversarial_band_support": MAX_ADVERSARIAL, "min_deranged_collapse": MIN_DERANGE_COLLAPSE,
                  "HP_op_agree": HP_OP_AGREE, "HF_op_agree": HF_OP_AGREE, "max_scram_residue": MAX_SCRAM_RESIDUE,
                  "min_cert_claims": MIN_CERT_CLAIMS_FULL, "min_assemblable": MIN_ASSEMBLABLE_FULL},
        "composition": {
            "predecessor_source_direct": "exp_cert_ledger_source_direct_entailment_v1 (leaf resolution + comparator reused verbatim)",
            "predecessor_numeric": "exp_cert_ledger_numeric_entailment_v1 (Tier-2 numeric entailment)",
            "comparator_cell": "exp_math_rns_subtract_compare_v1 (MEASURED_MECHANISM; decode_then_compare)",
            "rung": ("justification-retrieval: joins the cert_ledger to each claim's referent metrics.json, ASSEMBLES "
                     "the claim's machine-clean gating evidence, and RE-DERIVES whether the recorded verdict is "
                     "SUPPORTED. One level above source-direct (which resolves individual cited numbers); this "
                     "aggregates per CERT CLAIM and checks the VERDICT is entailed by its own evidence."),
        },
        "scope_guardrail": ("NARROW glass-box MONITOR: the audit READS the ledger + cell metrics + verdicts and "
                            "RE-DERIVES entailment. It NEVER edits the ledger, never re-labels a cert_status, never "
                            "edits code, never triggers a re-encode. Not fluent-language, not self-improvement."),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }
    _write_metrics_atomic(output_dir, metrics)
    written = json.load(open(output_dir / "metrics.json"))
    assert written["run_mode"] == mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {mode}"

    _say(f"\n[{ANCHOR_NAME}] {verdict}: {vmsg}")
    _say(f"[{ANCHOR_NAME}] metrics -> {output_dir / 'metrics.json'}  elapsed={elapsed:.1f}s")
    for seed in seeds:
        pp = _partial_path(output_dir, seed)
        if pp.exists():
            try:
                pp.unlink()
            except OSError:
                pass
    return 0


def _run_selftest() -> int:
    t0 = time.perf_counter()
    SD._setup_regime()
    ok_cmp = SD.comparator_selftest(seed=7)
    cbs = [SD.phasor_codebook(m, SD.SB, 6070 + i) for i, m in enumerate(SD._MODULI)]
    a_ok, b_ok, c_ok, d_ok = support_selftest(cbs)
    ok_sup = a_ok and b_ok and c_ok and d_ok
    # tiny real end-to-end over a claims sample
    claims, _cs = load_cert_claims(LEDGER_PATH)
    sample = claims[:400]
    e2e_ok = True
    sr = na = None
    if sample:
        res, _hh, _aa = run_seed(7, sample, {}, cbs)
        sr = res["support_recall"]
        na = res["n_assemblable"]
        e2e_ok = (res["n_cert_claims"] == len(sample)) and (na is not None)
    ok = ok_cmp and ok_sup and e2e_ok
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: comparator={ok_cmp} support={ok_sup} "
         f"(holds={a_ok} not_holds={b_ok} adv_flip={c_ok} sgc={d_ok}) e2e={e2e_ok} "
         f"(n_sample={len(sample)} n_assemblable={na} support_recall={sr}) [{time.perf_counter()-t0:.1f}s]")
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
