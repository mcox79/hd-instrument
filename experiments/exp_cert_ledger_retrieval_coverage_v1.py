# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate: content_addressable retrieved-record ids vs scrambled_index retrieved-record
#     ids hash-distinct; content vs random hash-distinct. (exact_match is a set-membership bool arm, hashed too.)
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: this is a RETRIEVAL-COVERAGE test (a noisy associative cleanup readout), not a Gaussian-noise-floor
#     sweep. The discriminators are CONTRASTS: content_addressable coverage vs exact_match baseline (LIFT);
#     scrambled-index control collapses toward chance; random-pick control ~1/n_records. discriminator_reachability=True.
# - baseline_in_band (META_RULE_AG): the AG discriminator here is the scrambled-index CONTROL collapse (mechanism
#     minus scrambled gap), NOT a difficulty gradient. The exact_match baseline is INTENTIONALLY LOW (~0.03-0.10):
#     that low coverage IS the problem this cell measures, so AG's 0.05-floor is EXEMPT for exact_match (a low
#     baseline is the finding, not a saturation artifact). content_recall_within_recoverable is the in-band
#     mechanism metric; the scrambled control must collapse for the discriminator to fire.
# - discriminator survives scale: smoke runs the content-vs-exact LIFT + scrambled-collapse at N_DIM in the FULL
#     family (2048/4096); the LIFT + collapse must FIRE in smoke (DISCRIMINATOR-MUST-SURVIVE-SCALE option A/C).
# - HARD_PASS strictly above floor: content_recall_within_recoverable HP 0.80 (HF 0.50); content_precision HP 0.90
#     (HF 0.75); lift HP +0.03 (HF <=0). Bands are RELATIVE (recall-within-recoverable / precision / lift), robust
#     to remote-vs-local corpus-size differences. The measured CEILING (recoverable fraction) is REPORTED, not gated.
# - HP_SCOPE per-arm: content_recall/precision/lift gates apply to the content_addressable MECHANISM only;
#     scrambled_index and random_baseline are FLOOR/CONTROL arms (must collapse, not clear HP).
# - cardinality_ok: EXPECTED_N_UNITS = len(seeds) * len(n_dims); verdict counts per_unit and gates on it.
# - per-unit failure-class instrumentation (META_RULE_J): harvest per-file parse failures caught by SPECIFIC class
#     (json.JSONDecodeError / OSError / ValueError), counted, non-gating; no bare except.
# - calibration_check: default_ok_for_this_regime -- the content ACCEPT gate uses a FIXED cosine tau (no label
#     leakage). Justification measured in the formula self-test: bag-of-char-trigram cosine between a cell key and
#     its suffix-variant (exp_foo_v1 vs exp_foo_v1_smoke) is >> cosine to an unrelated cell key; tau sits cleanly
#     between the two populations. The separation is logged; the scrambled-control-collapse verifies it still fires.
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# KB_REFERENT: data/substrate_index/meta/cert_ledger.jsonl
#
# TIER-2 RETRIEVAL-COVERAGE: CONTENT-ADDRESSABLE BACKING-RECORD RETRIEVAL FOR THE SELF-AUDIT  v1
# =============================================================================================
# WHY (measured off-disk 2026-07-06): the landed Tier-2 numeric-entailment self-check
# (exp_cert_ledger_numeric_entailment_v1) has a near-vacuous retrieval leg:
#   MEASURED@data/exp_cert_ledger_numeric_entailment_v1/metrics.json:arms.7.retrieval_hit_rate = 0.0328
# The leg was `exact string membership of the citing cell exp-key in the cert-ledger`. Two structural facts
# (both MEASURED off-disk this session) explain the low coverage and BOUND what any retrieval mechanism can do:
#   (1) THE LEDGER HOLDS NO NUMBERS. cert_ledger.jsonl rows carry {atom_id, verdict, cert_status,
#       referent_pointer} -- NOT the cited measured value or threshold. gate_claims (structured value/threshold/op)
#       present in 0/5817 corpus metrics.json (MEASURED@survey 2026-07-06). So a cited `NUM op NUM` claim has NO
#       numeric content in the ledger to match against; the only shared content between a claim and a record is the
#       CELL IDENTITY. Content-addressable retrieval must therefore join on cell-identity, not on the number.
#   (2) MOST CITATIONS HAVE NO BACKING RECORD. Of the distinct cited-inequality source cells, the exp-key overlap
#       with the ledger is: exact ~0.10, normalized(strip _smoke/_seed) ~0.15, fuzzy-substring ceiling ~0.17
#       (MEASURED@off-disk oracle-join 2026-07-06). ~83% of numeric citations come from NON-ATOMIZED
#       (smoke / wave14-exploration) cells with no certified record. The honest coverage CEILING is ~0.15-0.17,
#       NOT 1.0 -- raising N_DIM cannot change this; content-addressability cannot change this. This is the
#       dominant bound: finding (c) genuine claim-to-record mismatch.
#
# WHAT (this cell): REPLACE the brittle exact-string leg with a CONTENT-ADDRESSABLE retrieval that connects each
# cited claim to its backing ledger record via the SUBSTRATE's OWN HD text encoder + nearest-neighbour cleanup
# (hdlab.char_trigram_encoder = the char_trigram_v1 encoder; hdlab.cleanup_family k-NN readout). Then MEASURE the
# three candidate causes the Director flagged, off the REAL ledger:
#   (a) CAPACITY: sweep N_DIM {4096, 8192, 16384}; does content recall/precision rise with dimension? The record-
#       identity strings are highly near-duplicate (exp_wave14_betA_... vs exp_wave14_betZ_...), so cleanup is a
#       HIGH-INTERFERENCE associative readout -- exactly the regime where capacity matters and where, per the banked
#       CROSS-CELL LAW (reference_crt_residue_helps_clean_encoding_hurts_noisy_readout_2026-07-06), a noisy
#       associative readout can HARD_FAIL by returning the wrong near-duplicate sibling.
#   (b) THE LEG: content_addressable coverage vs exact_match baseline. Content-addressable recovers the format-
#       variant records (a `..._v1_smoke` claim whose backing record is `..._v1`) that a raw string-match drops.
#       LIFT = content - exact quantifies how much of the recoverable band the exact leg was leaving on the table.
#   (c) THE CEILING: the recoverable fraction (oracle normalized-join) is REPORTED as the measured ceiling. Even a
#       clean mechanism PASS means "coverage lifts from ~0.10 to ~0.15, ceiling ~0.17" -- the audit stays bounded
#       because most citations are structurally un-backed. HONEST: the real fix for (c) is emitting STRUCTURED
#       gate_claims + atomizing more cells, NOT a cleverer retrieval mechanism.
#
# ARMS (per seed x N_DIM unit; all over the SAME harvested real claims + real ledger records):
#   exact_match            : BASELINE -- raw citing-cell exp-key is a member of the ledger key set. ~0.03-0.10.
#   content_addressable    : MECHANISM -- HD char-trigram encode of the citing-cell identity; cosine top-1 cleanup
#                            over the HD-encoded ledger record-identity codebook; ACCEPT iff cos>=tau; a HIT iff
#                            ACCEPT and the retrieved record's canonical key == the claim's canonical key.
#   scrambled_index        : CONTROL -- permute the record-identity<->slot correspondence; retrieval must collapse.
#   random_baseline        : CONTROL -- random record pick; ~ recoverable_frac / n_records (near 0).
#   op_agreement_guard     : GUARD (retained comparator leg) -- on the in-dynamic-range content-retrieved claims,
#                            the VET'd decode_then_compare (exp_math_rns_subtract_compare_v1) op-eval must still
#                            equal the Python oracle (~1.0), so coverage is not bought by dropping hard claims.
#   ceiling                : REPORTED -- recoverable fraction (oracle normalized-join); the measured coverage ceiling.
#
# HONEST FRAMING (USER-LOCKED): NARROW glass-box MONITOR step. The substrate RETRIEVES + CHECKS its own certified
# records; it NEVER edits the ledger, never re-labels a cert_status, never edits code, never triggers a re-encode.
# Not fluent-language, not self-improvement. If content-addressable retrieval cannot beat exact-match (or returns
# wrong sibling records), that is a REAL bounded finding reported honestly (no smoke) -- NOT forced to a pass.
#
# ASCII-only. CPU default (numpy bipolar HD; no GPU, no LLM, no re-encode). Reads the live self-record referent
# (cert_ledger.jsonl + the data/ metrics.json tree). Run:
#   python experiments/exp_cert_ledger_retrieval_coverage_v1.py [--self-test | --smoke]   (bare -> full)

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

ANCHOR_NAME = "cert_ledger_retrieval_coverage_v1"
REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Substrate-native primitives (genuine reuse; the canonical char_trigram_v1 encoder + cleanup family).
from hdlab.char_trigram_encoder import (  # noqa: E402
    CharTrigramEncoder, _bipolar_hv, _seed_for_trigram,
)
from hdlab.cleanup_family import k_NN_lookup  # noqa: E402

# Comparison leg (op_agreement guard) -- imported VERBATIM from the just-VET'd comparator primitive (DRY).
from experiments.exp_math_rns_subtract_compare_v1 import (  # noqa: E402
    REGIMES, SB, N_DIM as COMPARATOR_N_DIM, R_MODULI, _crt_setup,
    phasor_codebook, encode as rns_encode, decode_int, true_3way,
)

DATA_DIR = REPO / "data"
LEDGER_PATH = REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"

# ---- comparator regime (mirror Tier-2: LARGE gives widest exact dynamic range for quantized real metrics) ----
CMP_REGIME = "large"                     # moduli (40,41,43); M=70520
CMP_SCALE = 1000                         # quantize float v -> round(v*SCALE)
CMP_OFFSET = 20000                       # q(v) = round(v*SCALE)+OFFSET in [0,M); covers v in [-20.0, +50.5)
CMP_RES = 2.0 / CMP_SCALE                # ties below this are quantization-unresolvable (audit-excluded)
_CMP_MODULI = REGIMES[CMP_REGIME]
_CMP_M = 1
_CMP_MI = _CMP_YI = None


def _setup_comparator():
    global _CMP_M, _CMP_MI, _CMP_YI
    _CMP_M, _CMP_MI, _CMP_YI = _crt_setup(_CMP_MODULI)


# ---- Pre-registered bands (RELATIVE; robust to corpus-size drift local-vs-remote) ----
HP_CONTENT_RECALL = 0.80    # HARD_PASS: content recovers >=80% of records that EXIST (recoverable band)
HF_CONTENT_RECALL = 0.50    # HARD_FAIL: below -> cannot even find half the existing records
HP_CONTENT_PRECISION = 0.90 # HARD_PASS: of accepted matches, >=90% land on the correct experiment's record
HF_CONTENT_PRECISION = 0.75 # HARD_FAIL: below -> noisy readout returns wrong sibling records (CROSS-CELL LAW)
HP_LIFT = 0.03              # HARD_PASS: content per-claim coverage beats exact by >= +0.03 absolute
HF_LIFT = 0.0               # HARD_FAIL: content no better than exact (content-addressability adds nothing)
MAX_SCRAMBLED_HIT = 0.03    # control: scrambled-index hit rate must collapse to/below this
HF_SCRAMBLED_HIT = 0.10     # scrambled above this -> control did not collapse -> not load-bearing -> HARD_FAIL
HP_OP_GUARD = 0.99          # guard: op-agreement on content-retrieved in-range claims (exact CRT decode)
TAU_ACCEPT = 0.45           # FIXED content ACCEPT cosine floor (justified + measured in formula self-test)
ACCEPT_MARGIN = 0.12        # FIXED ambiguity refuse-gate: accept only if top1_cos - top2_cos >= this. Targets the
                            # CROSS-CELL-LAW failure: an UNBACKED claim near two ledger siblings has a small top1-top2
                            # margin (ambiguous -> REFUSE); a true suffix-variant has its own near-exact record far
                            # above the runner-up (confident -> ACCEPT). Measured/justified in the formula self-test.
MIN_CLAIMS = 120            # discriminator-fires: need at least this many harvested cited claims
MIN_RECOVERABLE = 20        # discriminator-fires: need at least this many recoverable claims to measure recall
OP_GUARD_SAMPLE = 60        # cap op-agreement guard to this many accepted claims per unit (guard, not headline)

# ---- Regime config ----
SMOKE_SEEDS = (1, 2)
SMOKE_NDIMS = (2048, 4096)
FULL_SEEDS = (7, 13, 19, 23, 29)         # >= 5 seeds (each salts the trigram codebook)
FULL_NDIMS = (4096, 8192, 16384)         # capacity sweep (a): near-duplicate identity cleanup is capacity-sensitive

# NUM op NUM harvester regex (LOGIC-IDENTICAL to exp_cert_ledger_numeric_entailment_v1; the same high-precision
# guards -- left word-boundary, sci-notation as a unit, relative-threshold-coefficient drop -- each removes a
# real harvester false-positive class verified on disk 2026-07-05).
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


def _write_metrics_atomic(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, output_dir / "metrics.json")  # atomic (META_RULE_AH)


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
# Identity-key normalization (join keys)
# ============================================================


def _norm_exp_key(p: str) -> str:
    """Metrics path -> exp-dir key (basename of the exp_* dir), separator-agnostic. (Logic-identical to Tier-2.)"""
    s = str(p).replace("\\", "/")
    parts = [x for x in s.split("/") if x]
    for x in parts:
        if x.startswith("exp_"):
            return x
    return parts[-2] if len(parts) >= 2 else s


_SUFFIX_RE = [
    (re.compile(r"_smoke$"), ""),
    (re.compile(r"_selftest$"), ""),
    (re.compile(r"_seed_?\d+"), ""),
    (re.compile(r"_(FULL|full|preview|local|cpu|gpu|GPU|CPU)$"), ""),
]


def canon_key(k: str) -> str:
    """Canonical experiment identity: strip run-variant suffixes (smoke/seed/full/preview/device).
    Two cells with the same canon are the SAME experiment; the oracle join + correctness use canon equality."""
    out = k
    changed = True
    while changed:  # strip repeatedly (e.g. _v1_seed_7_smoke)
        changed = False
        for rx, rep in _SUFFIX_RE:
            new = rx.sub(rep, out)
            if new != out:
                out = new
                changed = True
    return out


# ============================================================
# Seeded substrate text encoder (per-seed salted trigram codebook; reuses canonical bundling)
# ============================================================


class SeededTrigramEncoder(CharTrigramEncoder):
    """CharTrigramEncoder with a per-seed salt on the per-trigram HD codebook.

    The canonical encoder is deterministic (trigram content -> fixed HD), so retrieval would be seed-invariant.
    Salting the per-trigram seed makes each seed a DISTINCT random HD codebook (the documented 'seed permutes only
    the random codebook' convention), so cleanup interference on near-duplicate identity strings becomes a random
    variable we can measure variance over. Reuses _trigrams / encode / bundling unchanged."""

    def __init__(self, n_dim: int, salt: int) -> None:
        super().__init__(n_dim=n_dim)
        self._salt = int(salt) & 0xFFFFFFFF

    def _hv_for_trigram(self, trigram: str) -> np.ndarray:
        cached = self._cache.get(trigram)
        if cached is not None:
            return cached
        seed = (_seed_for_trigram(trigram) ^ self._salt) & 0xFFFFFFFF
        hv = _bipolar_hv(seed, self.n_dim)
        self._cache[trigram] = hv
        self._n_unique_trigrams = len(self._cache)
        return hv


# ============================================================
# Comparator (op_agreement guard) -- copied helpers (logic-identical to Tier-2 comparator leg)
# ============================================================


def quantize(v: float):
    q = int(round(v * CMP_SCALE)) + CMP_OFFSET
    return q if 0 <= q < _CMP_M else None


def eval_op(cmp3: int, op: str) -> bool:
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


def substrate_compare(qa: int, qb: int, cbs) -> int:
    """Two exact CRT decodes -> 3-way (the VET'd decode_then_compare mechanism-of-record)."""
    da = decode_int(rns_encode(qa, cbs, _CMP_MODULI, SB), cbs, _CMP_MODULI, SB, _CMP_M, _CMP_MI, _CMP_YI)
    db = decode_int(rns_encode(qb, cbs, _CMP_MODULI, SB), cbs, _CMP_MODULI, SB, _CMP_M, _CMP_MI, _CMP_YI)
    return true_3way(da, db)


# ============================================================
# Harvest cited claims + load ledger records (the referents)
# ============================================================


def harvest_claims(data_dir: Path, max_files: int | None = None):
    """Scan data/**/metrics.json; extract cited `NUM op NUM` claims from verdict_msg. One claim per unique
    (exp_key, name, lhs, op, rhs). Returns (claims, stats). Per-file parse failures counted by class (META_RULE_J).
    max_files caps the scan (self-test wiring only; smoke/full pass None = whole tree)."""
    claims = []
    seen = set()
    n_files = n_with = 0
    fail_json = fail_os = fail_val = 0
    all_paths = sorted(data_dir.glob("**/metrics.json"), key=lambda p: str(p))
    if max_files is not None:
        all_paths = all_paths[:max_files]
    for mp in all_paths:
        s = str(mp)
        if ANCHOR_NAME in s or "cert_ledger_numeric_entailment" in s:
            continue  # never ingest this cell's own / the sibling audit cell's output
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
        vm = d.get("verdict_msg")
        if not isinstance(vm, str) or not vm:
            continue
        exp_key = _norm_exp_key(s)
        got = False
        for m in _INEQ.finditer(vm):
            name, lhs_s, op, rhs_s = m.group(1), m.group(2), m.group(3), m.group(4)
            try:
                lhs = float(lhs_s)
                rhs = float(rhs_s)
            except ValueError:
                continue
            if lhs.is_integer() and rhs.is_integer() and abs(lhs) > 1000 and abs(rhs) > 1000:
                continue  # drop obvious non-metric ID/dim pairs
            key = (exp_key, name or "", round(lhs, 6), op, round(rhs, 6))
            if key in seen:
                continue
            seen.add(key)
            got = True
            claims.append({"exp_key": exp_key, "canon": canon_key(exp_key), "name": name or "",
                           "lhs": lhs, "op": op, "rhs": rhs})
        if got:
            n_with += 1
    claims.sort(key=lambda t: (t["exp_key"], t["name"], t["lhs"], t["op"], t["rhs"]))
    stats = {"n_files_scanned": n_files, "n_files_with_cited_inequality": n_with,
             "harvest_parse_failures": {"json_decode": fail_json, "os_error": fail_os, "value_error": fail_val}}
    return claims, stats


def load_ledger_records(path: Path):
    """cert_ledger.jsonl -> deduped list of certified records with a retrievable identity string.

    Each record: {raw_key, canon, verdict, atom_id}. raw_key = _norm_exp_key(referent metrics_path) (or atom_id
    fallback). Deduped by raw_key (first verdict kept). This is the set the content-addressable index is built over."""
    records = []
    by_key = {}
    n_rows = 0
    if not path.exists():
        return records, 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            n_rows += 1
            ref = row.get("referent_pointer")
            mp = None
            if isinstance(ref, dict):
                mp = ref.get("metrics_path")
            elif isinstance(ref, str):
                mp = ref
            if not mp:
                mp = row.get("atom_id")
            v = row.get("verdict")
            if not mp or not v:
                continue
            raw = _norm_exp_key(mp)
            if raw in by_key:
                continue
            rec = {"raw_key": raw, "canon": canon_key(raw), "verdict": v, "atom_id": row.get("atom_id")}
            by_key[raw] = rec
            records.append(rec)
    return records, n_rows


# ============================================================
# Retrieval unit: one (seed, N_DIM)
# ============================================================


def _encode_matrix(enc: SeededTrigramEncoder, strings) -> np.ndarray:
    """Encode a list of strings into a [N, n_dim] bipolar matrix (batched; single python loop over strings only)."""
    out = np.zeros((len(strings), enc.n_dim), dtype=np.float32)
    for i, s in enumerate(strings):
        out[i] = enc.encode(s)
    return out


def run_unit(seed: int, n_dim: int, claims, records, rec_raw_set, rec_canon_set,
             canon_to_recidx, cmp_cbs, cap=None):
    """One (seed, N_DIM) retrieval unit. Returns a metrics dict + per-arm retrieved-id hashes (arms_differ)."""
    cl = claims[:cap] if cap else claims
    n = len(cl)
    rec_raw = [r["raw_key"] for r in records]
    rec_canon = [r["canon"] for r in records]

    enc = SeededTrigramEncoder(n_dim=n_dim, salt=(seed * 2654435761) & 0xFFFFFFFF)
    rec_cb = _encode_matrix(enc, rec_raw)                 # [nr, n_dim]
    claim_cb = _encode_matrix(enc, [c["exp_key"] for c in cl])  # [nq, n_dim]

    # cosine (bipolar; L2-normalize both then matmul)
    rec_unit = rec_cb / (np.linalg.norm(rec_cb, axis=1, keepdims=True) + 1e-8)
    claim_unit = claim_cb / (np.linalg.norm(claim_cb, axis=1, keepdims=True) + 1e-8)
    sims = claim_unit @ rec_unit.T                        # [nq, nr]

    # content_addressable retrieval: top-1 + top-2 (for the ambiguity refuse-gate)
    top_idx = sims.argmax(axis=1)
    top_cos = sims[np.arange(sims.shape[0]), top_idx]
    if sims.shape[1] >= 2:
        part = np.partition(sims, sims.shape[1] - 2, axis=1)
        top2_cos = part[:, -2]                            # 2nd-largest cosine per claim
    else:
        top2_cos = np.full(sims.shape[0], -1.0, dtype=np.float32)

    # scrambled-index control: permute record slots; row i now encodes a random record -> retrieval mislabels.
    rng = np.random.default_rng(987654 + seed * 131 + n_dim)
    perm = rng.permutation(len(records))
    sims_scr = claim_unit @ rec_unit[perm].T              # row i holds encoding of record perm[i]
    scr_idx_pos = sims_scr.argmax(axis=1)                 # argmax position i; treat position as record i (mislabelled)
    scr_cos = sims_scr[np.arange(sims_scr.shape[0]), scr_idx_pos]
    if sims_scr.shape[1] >= 2:
        scr_part = np.partition(sims_scr, sims_scr.shape[1] - 2, axis=1)
        scr_top2 = scr_part[:, -2]
    else:
        scr_top2 = np.full(sims_scr.shape[0], -1.0, dtype=np.float32)

    # oracle: recoverable iff claim canon is present among record canons
    n_recoverable = 0
    exact_hits = 0
    # MECHANISM (margin refuse-gate) counters:
    content_hits = content_accepts = content_correct_accepts = 0
    # DIAGNOSTIC (naive flat-tau, no margin) counters:
    flat_hits = flat_accepts = flat_correct_accepts = 0
    scr_hits = rnd_hits = 0
    cos_recov, cos_unrecov, margin_recov, margin_unrecov = [], [], [], []
    op_agree_hits = op_agree_n = 0
    retrieved_content_ids = []
    retrieved_scr_ids = []
    exact_flags = []

    for i, c in enumerate(cl):
        recoverable = c["canon"] in rec_canon_set
        margin = float(top_cos[i]) - float(top2_cos[i])
        if recoverable:
            n_recoverable += 1
            cos_recov.append(float(top_cos[i]))
            margin_recov.append(margin)
        else:
            cos_unrecov.append(float(top_cos[i]))
            margin_unrecov.append(margin)

        # exact_match baseline: raw citing key is a member of the ledger raw-key set
        exact = c["exp_key"] in rec_raw_set
        exact_hits += 1 if exact else 0
        exact_flags.append(1 if exact else 0)

        ridx = int(top_idx[i])
        retrieved_content_ids.append(ridx)
        ret_canon = rec_canon[ridx]
        correct_record = (ret_canon == c["canon"])

        # MECHANISM: accept iff cosine floor AND unambiguous (top1 clears top2 by margin)
        accept = (float(top_cos[i]) >= TAU_ACCEPT) and (margin >= ACCEPT_MARGIN)
        if accept:
            content_accepts += 1
            if correct_record:
                content_correct_accepts += 1
                content_hits += 1

        # DIAGNOSTIC: naive flat-tau accept (no margin) -- exposes the CROSS-CELL-LAW precision failure
        flat_accept = float(top_cos[i]) >= TAU_ACCEPT
        if flat_accept:
            flat_accepts += 1
            if correct_record:
                flat_correct_accepts += 1
                flat_hits += 1

        # scrambled control (same margin gate)
        spos = int(scr_idx_pos[i])
        retrieved_scr_ids.append(spos)
        scr_margin = float(scr_cos[i]) - float(scr_top2[i])
        scr_accept = (float(scr_cos[i]) >= TAU_ACCEPT) and (scr_margin >= ACCEPT_MARGIN)
        if scr_accept and (rec_canon[spos] == c["canon"]):
            scr_hits += 1

        # random control
        rpick = int(rng.integers(0, len(records)))
        rnd_hits += 1 if rec_canon[rpick] == c["canon"] else 0

        # op_agreement guard on content-ACCEPTED, in-dynamic-range claims (capped sample)
        if accept and op_agree_n < OP_GUARD_SAMPLE:
            qa, qb = quantize(c["lhs"]), quantize(c["rhs"])
            if qa is not None and qb is not None:
                op_agree_n += 1
                cmp_sub = substrate_compare(qa, qb, cmp_cbs)
                sub_holds = eval_op(cmp_sub, c["op"])
                ora_holds = eval_op((1 if qa > qb else (0 if qa == qb else -1)), c["op"])
                op_agree_hits += 1 if sub_holds == ora_holds else 0

    exact_rate = exact_hits / n if n else float("nan")
    content_rate = content_hits / n if n else float("nan")
    flat_rate = flat_hits / n if n else float("nan")
    ceiling = n_recoverable / n if n else float("nan")
    lift = content_rate - exact_rate
    content_recall = (content_hits / n_recoverable) if n_recoverable else float("nan")
    content_precision = (content_correct_accepts / content_accepts) if content_accepts else float("nan")
    flat_precision = (flat_correct_accepts / flat_accepts) if flat_accepts else float("nan")
    scr_rate = scr_hits / n if n else float("nan")
    rnd_rate = rnd_hits / n if n else float("nan")
    op_guard = (op_agree_hits / op_agree_n) if op_agree_n else float("nan")

    def _h(ids):
        return hashlib.sha256(np.asarray(ids, dtype=np.int64).tobytes()).hexdigest()

    res = {
        "seed": seed, "n_dim": n_dim, "n_claims": n, "n_records": len(records),
        "n_recoverable": n_recoverable,
        "exact_match_hit_rate": round(exact_rate, 4),
        "content_addressable_hit_rate": round(content_rate, 4),
        "ceiling_recoverable_frac": round(ceiling, 4),
        "coverage_lift": round(lift, 4),
        "content_recall_within_recoverable": round(content_recall, 4) if content_recall == content_recall else None,
        "content_precision": round(content_precision, 4) if content_precision == content_precision else None,
        "content_accepts": content_accepts,
        "flat_tau_hit_rate": round(flat_rate, 4),
        "flat_tau_precision": round(flat_precision, 4) if flat_precision == flat_precision else None,
        "flat_tau_accepts": flat_accepts,
        "scrambled_index_hit_rate": round(scr_rate, 4),
        "random_baseline_hit_rate": round(rnd_rate, 4),
        "op_agreement_guard": round(op_guard, 4) if op_guard == op_guard else None,
        "op_guard_n": op_agree_n,
        "mean_cos_recoverable": round(float(np.mean(cos_recov)), 4) if cos_recov else None,
        "mean_cos_unrecoverable": round(float(np.mean(cos_unrecov)), 4) if cos_unrecov else None,
        "mean_margin_recoverable": round(float(np.mean(margin_recov)), 4) if margin_recov else None,
        "mean_margin_unrecoverable": round(float(np.mean(margin_unrecov)), 4) if margin_unrecov else None,
    }
    hashes = {"content": _h(retrieved_content_ids), "scrambled": _h(retrieved_scr_ids), "exact": _h(exact_flags)}
    return res, hashes


# ============================================================
# Formula self-tests (MANDATORY)
# ============================================================


def cosine_separation_selftest() -> tuple:
    """(a) bag-of-trigram cosine: a key vs its _smoke suffix-variant >> vs an unrelated key -> TAU_ACCEPT sits
    cleanly between the two populations (justifies the FIXED accept floor, no label leakage).
    (b) content-addressable RECOVERS a synthetic suffix-variant that exact-string MISSES (recall).
    (c) the AMBIGUITY REFUSE-GATE: an UNBACKED claim near TWO ledger siblings is REFUSED by the margin gate
        (small top1-top2 margin) even though the naive flat-tau would ACCEPT it (the CROSS-CELL-LAW fix)."""
    enc = SeededTrigramEncoder(n_dim=4096, salt=12345)
    base = ["exp_alpha_metric_v1", "exp_beta_capacity_v2", "exp_gamma_routing_v3",
            "exp_delta_consolidation_v1", "exp_epsilon_cleanup_v4"]
    variants = [b + "_smoke" for b in base]
    others = ["exp_zeta_unrelated_v1", "exp_eta_something_else_v2"]
    cb_base = _encode_matrix(enc, base)
    cb_base_u = cb_base / (np.linalg.norm(cb_base, axis=1, keepdims=True) + 1e-8)
    same_cos, cross_cos = [], []
    for i, v in enumerate(variants):
        q = enc.encode(v)
        q = q / (np.linalg.norm(q) + 1e-8)
        sims = cb_base_u @ q
        same_cos.append(float(sims[i]))
        cross_cos.append(float(max(sims[j] for j in range(len(base)) if j != i)))
    for o in others:
        q = enc.encode(o)
        q = q / (np.linalg.norm(q) + 1e-8)
        sims = cb_base_u @ q
        cross_cos.append(float(sims.max()))
    min_same = min(same_cos)
    max_cross = max(cross_cos)
    sep_ok = (min_same > TAU_ACCEPT) and (max_cross < min_same)  # tau separates variant-of-self from others

    # (b)+(c): base records + two NEAR-DUPLICATE sibling records; claims = suffix-variants of backed cells
    # (recoverable) PLUS one UNBACKED claim near the two siblings (must be REFUSED by the margin gate).
    sib_a, sib_b = "exp_wave_lane_betA_v1", "exp_wave_lane_betB_v1"
    records = [{"raw_key": b, "canon": canon_key(b), "verdict": "HARD_PASS", "atom_id": b} for b in base]
    records += [{"raw_key": sib_a, "canon": canon_key(sib_a), "verdict": "HARD_FAIL", "atom_id": sib_a},
                {"raw_key": sib_b, "canon": canon_key(sib_b), "verdict": "HARD_FAIL", "atom_id": sib_b}]
    claims = [{"exp_key": variants[i], "canon": canon_key(variants[i]), "name": "", "lhs": 1.0, "op": ">=",
               "rhs": 0.0} for i in range(len(base))]
    unbacked = {"exp_key": "exp_wave_lane_betC_v1_smoke", "canon": canon_key("exp_wave_lane_betC_v1_smoke"),
                "name": "", "lhs": 1.0, "op": ">=", "rhs": 0.0}  # canon NOT in records -> correct action = REFUSE
    claims.append(unbacked)
    rec_raw_set = {r["raw_key"] for r in records}
    rec_canon_set = {r["canon"] for r in records}
    cmp_cbs = [phasor_codebook(m, SB, 6000 + 7 * 10 + i) for i, m in enumerate(_CMP_MODULI)]
    res, hashes = run_unit(7, 4096, claims, records, rec_raw_set, rec_canon_set, {}, cmp_cbs)
    exact_miss = res["exact_match_hit_rate"] == 0.0          # raw _smoke keys are NOT ledger members
    content_recovers = (res["content_recall_within_recoverable"] or 0.0) >= 0.99  # HD cleanup lands on the base
    # margin refuse-gate: mechanism precision is perfect (unbacked sibling REFUSED); flat-tau would false-accept it.
    margin_refuses = (res["content_precision"] is not None and res["content_precision"] >= 0.999)
    flat_false_accepts = (res["flat_tau_precision"] is not None and res["flat_tau_precision"] < res["content_precision"])
    arms_differ = hashes["content"] != hashes["scrambled"]
    refuse_ok = margin_refuses and flat_false_accepts
    return sep_ok, min_same, max_cross, exact_miss, content_recovers, arms_differ, refuse_ok, res


def op_eval_selftest(seed: int = 7) -> bool:
    """substrate decode_then_compare op-eval == Python oracle on random quantized pairs for all 5 ops."""
    cbs = [phasor_codebook(m, SB, 6000 + seed * 10 + i) for i, m in enumerate(_CMP_MODULI)]
    rng = np.random.default_rng(999 + seed)
    for _ in range(48):
        qa = int(rng.integers(0, _CMP_M)); qb = int(rng.integers(0, _CMP_M))
        cmp_sub = substrate_compare(qa, qb, cbs)
        cmp_py = (1 if qa > qb else (0 if qa == qb else -1))
        for op in [">=", ">", "<=", "<", "=="]:
            if eval_op(cmp_sub, op) != eval_op(cmp_py, op):
                return False
    return True


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


def classify(per_unit, mode, n_claims, n_recoverable, expected_units):
    if len(per_unit) < expected_units:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                f"units {len(per_unit)} < expected {expected_units}", False)
    if n_claims < MIN_CLAIMS:
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"insufficient harvested claims: n={n_claims} < {MIN_CLAIMS}", False)
    if n_recoverable < MIN_RECOVERABLE:
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"insufficient recoverable claims (backing records exist for only {n_recoverable} < "
                f"{MIN_RECOVERABLE}); coverage ceiling too low to measure content recall meaningfully", False)

    exact = _meanv([u["exact_match_hit_rate"] for u in per_unit])
    content = _meanv([u["content_addressable_hit_rate"] for u in per_unit])
    ceiling = _meanv([u["ceiling_recoverable_frac"] for u in per_unit])
    lift_min = _minv([u["coverage_lift"] for u in per_unit])
    recall_min = _minv([u["content_recall_within_recoverable"] for u in per_unit])
    prec_min = _minv([u["content_precision"] for u in per_unit])
    flat_prec_min = _minv([u["flat_tau_precision"] for u in per_unit])
    scr_max = _maxv([u["scrambled_index_hit_rate"] for u in per_unit])
    op_min = _minv([u["op_agreement_guard"] for u in per_unit])

    # capacity diagnosis (a): recall at min vs max N_DIM
    by_ndim = {}
    for u in per_unit:
        by_ndim.setdefault(u["n_dim"], []).append(u)
    ndims = sorted(by_ndim)
    recall_lo = _meanv([u["content_recall_within_recoverable"] for u in by_ndim[ndims[0]]])
    recall_hi = _meanv([u["content_recall_within_recoverable"] for u in by_ndim[ndims[-1]]])
    prec_lo = _meanv([u["content_precision"] for u in by_ndim[ndims[0]]])
    prec_hi = _meanv([u["content_precision"] for u in by_ndim[ndims[-1]]])
    cap_recall_gain = (recall_hi - recall_lo) if (recall_hi == recall_hi and recall_lo == recall_lo) else float("nan")
    cap_prec_gain = (prec_hi - prec_lo) if (prec_hi == prec_hi and prec_lo == prec_lo) else float("nan")
    capacity_sensitive = (cap_recall_gain > 0.05) or (cap_prec_gain > 0.05)

    diag = (f"n_claims={n_claims} n_recoverable={n_recoverable} exact={exact:.4f} content={content:.4f} "
            f"ceiling={ceiling:.4f} lift_min={lift_min:.4f} recall_min={recall_min:.4f} "
            f"precision_margin_gated_min={prec_min:.4f} precision_flat_tau_min="
            f"{flat_prec_min if flat_prec_min==flat_prec_min else float('nan'):.4f} "
            f"scrambled_max={scr_max:.4f} op_guard_min={op_min if op_min==op_min else float('nan'):.4f} "
            f"cap[recall {recall_lo:.3f}->{recall_hi:.3f} (+{cap_recall_gain:.3f}), "
            f"precision {prec_lo:.3f}->{prec_hi:.3f} (+{cap_prec_gain:.3f}); capacity_sensitive={capacity_sensitive}]")

    # control-collapse gate (all modes)
    if not (scr_max <= HF_SCRAMBLED_HIT):
        return ("HARD_FAIL",
                f"SCRAMBLED-INDEX CONTROL DID NOT COLLAPSE: scrambled_max={scr_max:.4f} > {HF_SCRAMBLED_HIT} "
                f"-> content-addressable retrieval is not load-bearing (near-duplicate strings match anything). "
                f"{diag}", False)

    # HARD_FAIL band (noisy-readout failure per CROSS-CELL LAW, or leg adds nothing)
    if lift_min <= HF_LIFT:
        return ("HARD_FAIL",
                f"CONTENT-ADDRESSABLE ADDS NO COVERAGE: lift_min={lift_min:.4f} <= {HF_LIFT} (content no better "
                f"than exact-string membership). The retrieval gap is NOT the exact-vs-content leg. {diag}", True)
    if prec_min == prec_min and prec_min < HF_CONTENT_PRECISION:
        return ("HARD_FAIL",
                f"NOISY-READOUT RETURNS WRONG RECORDS: content_precision_min={prec_min:.4f} < "
                f"{HF_CONTENT_PRECISION} -- content-addressable cleanup lands on the WRONG near-duplicate sibling "
                f"record (CROSS-CELL LAW: associative readout HARD_FAILs on near-duplicate keys). {diag}", True)
    if recall_min == recall_min and recall_min < HF_CONTENT_RECALL:
        return ("HARD_FAIL",
                f"CANNOT FIND EXISTING RECORDS: content_recall_within_recoverable_min={recall_min:.4f} < "
                f"{HF_CONTENT_RECALL}. {diag}", True)

    # smoke: discriminator fired + controls collapsed + content beats exact -> loop demonstrates locally
    if mode == "smoke":
        return ("HARD_PASS",
                f"SMOKE_CONTENT_ADDRESSABLE_FIRES: content-addressable coverage beats exact-string (lift_min="
                f"{lift_min:.4f} > 0) at FULL-family N_DIM; scrambled control collapses (max={scr_max:.4f}); "
                f"content precision_min={prec_min:.4f} recall_min={recall_min:.4f}; op-agreement guard "
                f"min={op_min if op_min==op_min else float('nan'):.4f}. MEASURED CEILING={ceiling:.4f} "
                f"(recoverable fraction) -- coverage stays bounded because most citations are non-atomized. {diag}",
                True)

    # FULL bands
    hard_pass = (recall_min >= HP_CONTENT_RECALL and prec_min >= HP_CONTENT_PRECISION
                 and lift_min >= HP_LIFT and scr_max <= MAX_SCRAMBLED_HIT
                 and (op_min != op_min or op_min >= HP_OP_GUARD))
    if hard_pass:
        return ("HARD_PASS",
                f"CONTENT-ADDRESSABLE RETRIEVAL LIFTS TIER-2 COVERAGE: over {n_claims} real cited claims, the "
                f"substrate's own HD char-trigram cleanup + ambiguity refuse-gate connects a claim to its backing "
                f"CERTIFIED record by content, recovering recall_min={recall_min:.4f} of the records that EXIST "
                f"(margin-gated precision_min={prec_min:.4f}; the naive flat-tau precision "
                f"{flat_prec_min if flat_prec_min==flat_prec_min else float('nan'):.4f} shows the CROSS-CELL-LAW "
                f"near-duplicate failure the refuse-gate corrects) and beating exact-string membership by "
                f"lift_min={lift_min:.4f} (exact={exact:.4f} -> content={content:.4f}). Scrambled-index control "
                f"collapses (max={scr_max:.4f}); op-agreement guard min={op_min if op_min==op_min else float('nan'):.4f} "
                f"(comparator still exact on retrieved claims -> coverage not bought by dropping hard claims). "
                f"HONEST BOUND (the headline): the MEASURED CEILING is {ceiling:.4f} -- ~{(1-ceiling)*100:.0f}% of "
                f"cited numbers come from NON-ATOMIZED (smoke/exploration) cells with no certified record, so the "
                f"audit's coverage is structurally bounded regardless of the retrieval mechanism. Capacity: "
                f"content is {'CAPACITY-SENSITIVE' if capacity_sensitive else 'NOT capacity-limited'} over "
                f"N_DIM {ndims[0]}->{ndims[-1]}. DIAGNOSIS: (b) exact-vs-content leg gives a real +{lift_min:.3f} "
                f"lift; (c) genuine claim-to-record mismatch is the dominant bound (ceiling {ceiling:.3f}); "
                f"(a) capacity_sensitive={capacity_sensitive}. NARROW glass-box monitor; no ledger/code edits. {diag}",
                True)
    return ("MIDDLE_BAND",
            f"content-addressable retrieval is above the HARD_FAIL floor but below HARD_PASS on at least one gate "
            f"(recall_min={recall_min:.4f} vs {HP_CONTENT_RECALL}; precision_min={prec_min:.4f} vs "
            f"{HP_CONTENT_PRECISION}; lift_min={lift_min:.4f} vs {HP_LIFT}). MEASURED CEILING={ceiling:.4f}; "
            f"capacity_sensitive={capacity_sensitive}. Honest partial: some lift, bounded by ceiling. {diag}", True)


# ============================================================
# Config + driver
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"seeds": (7,), "ndims": (2048,), "cap": 200}
    if mode == "smoke":
        return {"seeds": SMOKE_SEEDS, "ndims": SMOKE_NDIMS, "cap": None}
    return {"seeds": FULL_SEEDS, "ndims": FULL_NDIMS, "cap": None}


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    _setup_comparator()
    cfg = get_config(mode)
    expected_units = len(cfg["seeds"]) * len(cfg["ndims"])
    _write_start_marker(output_dir, mode, expected_units)
    _say(f"[{ANCHOR_NAME}] mode={mode} seeds={cfg['seeds']} ndims={cfg['ndims']} "
         f"tau_accept={TAU_ACCEPT} expected_units={expected_units}")

    # formula self-tests (ALL modes)
    if not op_eval_selftest(seed=cfg["seeds"][0]):
        raise AssertionError("OP_EVAL_SELFTEST_FAIL (substrate op-eval != oracle)")
    sep_ok, min_same, max_cross, exact_miss, content_recovers, arms_diff, refuse_ok, _res = \
        cosine_separation_selftest()
    if not sep_ok:
        raise AssertionError(f"COSINE_SEPARATION_SELFTEST_FAIL: min_same={min_same:.3f} max_cross={max_cross:.3f} "
                             f"tau={TAU_ACCEPT} (accept gate does not cleanly separate suffix-variant from others)")
    if not (exact_miss and content_recovers and arms_diff and refuse_ok):
        raise AssertionError(f"CONTENT_RECOVERY_SELFTEST_FAIL: exact_miss={exact_miss} "
                             f"content_recovers={content_recovers} arms_differ={arms_diff} "
                             f"margin_refuse_gate_ok={refuse_ok}")
    _say(f"[{ANCHOR_NAME}] formula self-tests PASSED (op-eval; cosine sep min_same={min_same:.3f} "
         f"max_cross={max_cross:.3f} tau={TAU_ACCEPT}; content recovers suffix-variant exact misses; "
         f"margin refuse-gate rejects ambiguous unbacked sibling; arms differ)")

    # harvest + ledger (ONCE)
    records, n_ledger_rows = load_ledger_records(LEDGER_PATH)
    claims, hstats = harvest_claims(DATA_DIR)
    if cfg["cap"]:
        claims = claims[:cfg["cap"]]
    rec_raw_set = {r["raw_key"] for r in records}
    rec_canon_set = {r["canon"] for r in records}
    canon_to_recidx = {}
    for i, r in enumerate(records):
        canon_to_recidx.setdefault(r["canon"], i)
    n_recoverable_global = sum(1 for c in claims if c["canon"] in rec_canon_set)
    _say(f"[{ANCHOR_NAME}] ledger: {n_ledger_rows} rows -> {len(records)} deduped records; "
         f"harvest: {hstats['n_files_scanned']} metrics.json, {hstats['n_files_with_cited_inequality']} cite an "
         f"inequality, {len(claims)} claims, {n_recoverable_global} recoverable (canon in ledger), "
         f"parse_fail={hstats['harvest_parse_failures']}")

    if not records or not claims:
        raise AssertionError(f"EMPTY_REFERENT: records={len(records)} claims={len(claims)}")

    # per-unit sweep (seed x N_DIM)
    per_unit = []
    hashes_all = {}
    ui = 0
    for seed in cfg["seeds"]:
        cmp_cbs = [phasor_codebook(m, SB, 6000 + seed * 10 + i) for i, m in enumerate(_CMP_MODULI)]
        for nd in cfg["ndims"]:
            res, hashes = run_unit(seed, nd, claims, records, rec_raw_set, rec_canon_set,
                                   canon_to_recidx, cmp_cbs)
            per_unit.append(res)
            hashes_all[(seed, nd)] = hashes
            ui += 1
            _heartbeat(output_dir, ui, expected_units, t0,
                       extra={"seed": seed, "n_dim": nd, "content": res["content_addressable_hit_rate"],
                              "exact": res["exact_match_hit_rate"], "scr": res["scrambled_index_hit_rate"]})
            _say(f"  [seed {seed} N_DIM {nd}] exact={res['exact_match_hit_rate']:.4f} "
                 f"content={res['content_addressable_hit_rate']:.4f} ceiling={res['ceiling_recoverable_frac']:.4f} "
                 f"lift={res['coverage_lift']:+.4f} recall={res['content_recall_within_recoverable']} "
                 f"precision={res['content_precision']} scrambled={res['scrambled_index_hit_rate']:.4f} "
                 f"random={res['random_baseline_hit_rate']:.4f} op_guard={res['op_agreement_guard']}")

    # arms_differ (META_RULE_AF): content vs scrambled + content vs exact-flag hashes distinct in >=1 unit
    reasons = []
    any_content_vs_scr = False
    for (seed, nd), h in hashes_all.items():
        if h["content"] != h["scrambled"]:
            any_content_vs_scr = True
        if h["content"] == h["exact"]:
            # not necessarily a bug (exact flags are bools) -- only flag if identical across the board; informational
            pass
    if not any_content_vs_scr:
        reasons.append("content==scrambled retrieved-ids in EVERY unit")
    arms_differ_ok = not reasons
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: " + "; ".join(reasons))

    n_claims = len(claims)
    verdict, vmsg, ok = classify(per_unit, mode, n_claims, n_recoverable_global, expected_units)
    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: Tier-2 content-addressable retrieval-coverage over own cert-record ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(cfg["seeds"]),
        "n_ndims": len(cfg["ndims"]),
        "n_units": len(per_unit),
        "expected_n_units": expected_units,
        "cardinality_ok": len(per_unit) >= expected_units,
        "n_claims": n_claims,
        "n_records": len(records),
        "n_recoverable": n_recoverable_global,
        "n_ledger_rows": n_ledger_rows,
        "config": {
            "seeds": list(cfg["seeds"]), "ndims": list(cfg["ndims"]), "tau_accept": TAU_ACCEPT,
            "retrieval_leg": "content_addressable_char_trigram_HD_cleanup_over_ledger_record_identities",
            "baseline_leg": "exact_string_membership_of_citing_exp_key_in_ledger_key_set",
            "comparison_guard_leg": "decode_then_compare_two_CRT_decodes_from_exp_math_rns_subtract_compare_v1",
            "join_key": "cell_identity_exp_key (the ledger holds NO cited numeric values -- see docstring finding 1)",
            "correctness_criterion": "retrieved record canon == claim canon (same experiment family)",
            "encoder": "hdlab.char_trigram_encoder (char_trigram_v1) with per-seed salted codebook",
            "cleanup": "cosine top-1 (hdlab.cleanup_family k_NN_lookup family) + fixed accept gate tau",
            "storage_strategy": "sharded (each ledger record its own HD identity vector; no bundling)",
        },
        "harvest_stats": hstats,
        "per_unit": per_unit,
        "arms_differ_verified": arms_differ_ok,
        "arms": {f"seed{u['seed']}_ndim{u['n_dim']}": u for u in per_unit},
        "bands": {"HP_content_recall": HP_CONTENT_RECALL, "HF_content_recall": HF_CONTENT_RECALL,
                  "HP_content_precision": HP_CONTENT_PRECISION, "HF_content_precision": HF_CONTENT_PRECISION,
                  "HP_lift": HP_LIFT, "HF_lift": HF_LIFT, "max_scrambled_hit": MAX_SCRAMBLED_HIT,
                  "HF_scrambled_hit": HF_SCRAMBLED_HIT, "HP_op_guard": HP_OP_GUARD, "tau_accept": TAU_ACCEPT,
                  "min_claims": MIN_CLAIMS, "min_recoverable": MIN_RECOVERABLE},
        "diagnosis": {
            "finding_a_capacity": "see verdict_msg cap[...] block: content recall/precision vs N_DIM sweep",
            "finding_b_leg": "content-addressable lift over exact-string membership (recovers suffix-variant records)",
            "finding_c_ceiling": "recoverable fraction = the measured coverage ceiling; ~83% of citations are "
                                 "non-atomized (dominant bound); the real fix is structured gate_claims + atomization",
            "ledger_holds_no_numbers": True,
            "corpus_gate_claims_structured": 0,
        },
        "scope_guardrail": ("NARROW glass-box MONITOR: the substrate retrieves + checks its OWN certified records "
                            "by content. It NEVER edits the ledger, never re-labels a cert_status, never edits code, "
                            "never triggers a re-encode. Not fluent-language, not self-improvement."),
        "composition": {
            "encoder_module": "hdlab.char_trigram_encoder.CharTrigramEncoder (char_trigram_v1)",
            "cleanup_module": "hdlab.cleanup_family (k_NN_lookup / cosine top-1)",
            "comparator_cell": "exp_math_rns_subtract_compare_v1 (MEASURED_MECHANISM; op-agreement guard)",
            "predecessor": "exp_cert_ledger_numeric_entailment_v1 (Tier-2; retrieval_hit_rate=0.0328 replaced here)",
        },
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }
    _write_metrics_atomic(output_dir, metrics)
    written = json.load(open(output_dir / "metrics.json"))
    assert written["run_mode"] == mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {mode}"

    _say(f"\n[{ANCHOR_NAME}] {verdict}: {vmsg}")
    _say(f"[{ANCHOR_NAME}] metrics -> {output_dir / 'metrics.json'}  elapsed={elapsed:.1f}s")
    return 0


def _run_selftest() -> int:
    t0 = time.perf_counter()
    _setup_comparator()
    ok_op = op_eval_selftest(seed=7)
    sep_ok, min_same, max_cross, exact_miss, content_recovers, arms_diff, refuse_ok, res = \
        cosine_separation_selftest()
    # tiny real end-to-end (small cap, single unit) to prove harvest+ledger+retrieval wires up on disk
    records, _nr = load_ledger_records(LEDGER_PATH)
    claims, _h = harvest_claims(DATA_DIR, max_files=1500)  # bounded wiring scan (robust under load)
    sample = claims[:150]
    e2e_ok = True
    n_recov = 0
    if records and sample:
        rec_raw_set = {r["raw_key"] for r in records}
        rec_canon_set = {r["canon"] for r in records}
        cmp_cbs = [phasor_codebook(m, SB, 6000 + 7 * 10 + i) for i, m in enumerate(_CMP_MODULI)]
        r2, _hh = run_unit(7, 2048, sample, records, rec_raw_set, rec_canon_set, {}, cmp_cbs)
        n_recov = r2["n_recoverable"]
        e2e_ok = (r2["n_claims"] == len(sample)) and (r2["content_addressable_hit_rate"] >= r2["exact_match_hit_rate"])
    ok = ok_op and sep_ok and exact_miss and content_recovers and arms_diff and refuse_ok and e2e_ok
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: op_eval={ok_op} cosine_sep={sep_ok} "
         f"(min_same={min_same:.3f} max_cross={max_cross:.3f} tau={TAU_ACCEPT}) exact_miss={exact_miss} "
         f"content_recovers={content_recovers} margin_refuse_ok={refuse_ok} arms_differ={arms_diff} e2e={e2e_ok} "
         f"(n_records={len(records)} n_sample={len(sample)} n_recoverable={n_recov}) "
         f"[{time.perf_counter()-t0:.1f}s]")
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
