"""PARALOG_CRISPR_SL_DETECTION_AUC (v1): the CHEAP DECISIVE reframe test -- is the near-zero-singles UNREADABLE null a
GENUINE dataset null, a HARNESS-TASK MISMATCH (a sparse synthetic-lethal DETECTION signal our continuous-MAE / variance-
readability lens was blind to), or STRUCTURALLY UNTESTABLE on this pocket (genes do not recur -> constituent codes cannot
generalize to novel pairs)?

BACKGROUND (VET skunkworks ac879338 on the parent regression cell exp_paralog_crispr_nearzero_singles_curated_ivf_v1, commit
651030f7e): on the SAME curated Dede near-zero-singles pocket the CONTINUOUS-MAE lens read HF_DATASET_SNR_NULL --
readable_rel=0.00424 (MEASURED@data/exp_paralog_crispr_nearzero_singles_curated_ivf_v1/metrics.json:readability.readable_rel),
IVF ratio 1.001 (pocket NOT variance-enriched), SYM HURTS -0.386 on the continuous target. The on-disk evidence LEANS null, so
this test is genuinely ADJUDICATING, not confirmation-seeking. Designed to REFUTE cleanly if the signal is absent.

THE REFRAME (this cell): drop continuous-MAE regression; ask a binary DETECTION/RANKING question on the pocket. Label a pocket
pair SL/positive if it is synthetic-lethal (large-negative interaction), neutral/negative otherwise. TASK = binary DETECTION
FROM CONSTITUENTS ONLY (the two gene identities/codes), held out on NOVEL pairs (each pair reserved before fitting; no label
leakage -- the label never enters the features). METRIC = detection ROC-AUC + AUPRC (class imbalance) + precision@k. The
question: does ANY constituent readout RANK true-SL pairs ABOVE neutral pairs on HELD-OUT novel pocket pairs, materially above
chance AND above the honest degree/popularity floor?

STRUCTURAL PRE-CHECK (LEADING expected outcome; the load-bearing honesty gate). The parent's landed pocket is a NEAR-MATCHING:
n_curated=360 pairs across n_tok_curated=704 genes -> avg gene pocket-degree = 2*360/704 = 1.02 (MEASURED@ the parent metrics).
A constituent-identity readout can only generalize to a NOVEL pair if BOTH its genes RECUR in training pairs; at degree ~1 they
do not, so ANY constituent method sits at chance for a TRIVIAL STRUCTURAL reason -- NOT because the interaction is genuinely
absent (genuine-null) and NOT because the lens was blind (harness-mismatch). The cell therefore MEASURES the exact learnable
sub-pocket (pairs whose both genes have pocket-degree >= MIN_DEG) and:
  - learnable sub-pocket < MIN_LEARNABLE (or scorable-novel positives < MIN_POS_NOVEL) -> STRUCTURAL_UNDERPOWER_GENES_DONT_RECUR
    => the reframe is UNTESTABLE on Dede; escalate to a COMBINATORIAL screen where each gene is crossed against many partners
    (Horlbeck GSE / Norman-Weissman Perturb-seq / a harmonized all-by-all compendium) so gene-level SL-propensity is learnable.
  - learnable sub-pocket adequate -> run the DETECTION-AUC test and adjudicate harness-mismatch vs genuine-null.

LABEL SOURCE (higher-SNR, INDEPENDENT of our CPM pipeline). PRIMARY = Dede Additional File 3 (MOESM3, per-pair zdLFC =
z-normalized dLFC = observed-minus-expected-from-SMF-sum, replicate-pooled, 3 cell lines) joined to pocket pairs by canonical
gene-symbol key: SL positive if mean zdLFC <= -Z_SL (Z_SL=3.0 == Dede's published SL call; one-sided -- synthetic LETHALITY is
the depleted tail, not the buffering tail). Using the PUBLISHED zdLFC (not our from-scratch DMF) is the point: it is a cleaner,
independent label, so a detection win cannot be dismissed as "you thresholded your own noise." FALLBACK (MOESM3 absent or pocket
join coverage < MIN_JOIN_FRAC) = DMF robust-z within the pocket (SL if z <= -Z_SL): in the near-zero-singles pocket both SMFs
~0, so DMF ~= the pairwise interaction and DMF-z <= -3 is the operational in-pocket SL equivalent. The label source used is
reported; the arms regress the BINARY label (features = gene codes), so there is no circularity with either label.

ARMS (detection score per novel pair; higher => more-SL): SYM (shared per-gene code + elementwise PRODUCT = substrate symmetric
bind; the pairwise-capable arm) ; LEARN_ADD (shared code + SUM = per-gene additive main-effects) ; ADD_RIDGE (closed-form ridge
on per-token count design = STRONG additive) ; LEARN_ROLE (role-keyed product; asymmetric algebra contrast) ; DEGREE (marginal
popularity deg[a]+deg[b] -- the honest floor a detection metric MUST beat; carries NO label information) ; CHANCE (random).
best_constituent = max(SYM, ADD, ADD_RIDGE, ROLE). In a near-zero-singles pocket the additive arms have NO pairwise term (both
SMFs ~0 -> additive predicts ~constant), so a SYM-over-additive gap localizes an irreducibly-pairwise SL signal.

CONTROLS (must fire before the real verdict is interpretable):
  POS = a planted RECURRENT pocket whose SL label IS a symmetric pairwise function of gene codes -> best_constituent AUC ~1.0
    (proves the detection readout CAN detect when a learnable signal exists AND genes recur).
  SCRAMBLE = real pocket labels permuted -> all arms AUC ~0.5 (detection must collapse to chance under a broken label).
  DEGREE-MATCHED negatives = evaluate on positives + degree-matched-subsampled negatives so marginal-popularity guessing carries
    NO AUC advantage (the module-2 leak lesson: the identity-free DEGREE arm must sit at chance on the matched eval). The
    HEADLINE AUC is computed on the DEGREE-MATCHED eval.

PRE-REGISTERED BANDS (fixed BEFORE running; see preregs/2026-07-15_paralog_crispr_sl_detection_auc.md):
  HARD_PASS_HARNESS_MISMATCH (SL IS detectable from constituents; the reframe is ALIVE): learnable sub-pocket adequate AND
    scorable-novel positives >= MIN_POS_NOVEL AND controls fire (pos>=POS_CTRL_AUC, scramble in [SCRAMBLE_AUC_LO,HI], degree-
    matched DEGREE-arm AUC <= DEGREE_MATCHED_CEIL) AND best_constituent DEGREE-MATCHED novel AUC >= AUC_HP=0.65 AND
    (best_constituent AUC - degree-matched DEGREE AUC) >= MARGIN_OVER_DEGREE=0.10.
  HARD_FAIL_GENUINE_NULL (readable structure absent even in detection framing): learnable adequate AND power adequate AND
    controls fire AND best_constituent AUC <= AUC_NULL_CEIL=0.55 AND not above the degree floor by the margin -> the pocket is a
    GENUINE null; detectable-interaction ABSENT in this framing -> escalate to higher-N pooled screens or drop.
  STRUCTURAL_UNDERPOWER_GENES_DONT_RECUR: learnable sub-pocket < MIN_LEARNABLE or scorable-novel positives < MIN_POS_NOVEL ->
    the constituent-detection reframe is UNTESTABLE on this near-matching pocket (NOT a genuine-null, NOT a harness-mismatch) ->
    escalate to a combinatorial screen where genes recur.
  HARD_FAIL_UNDERPOWERED_POCKET_N: near-zero-singles pocket < MIN_POCKET pairs -> insufficient (directional-only).
  INCONCLUSIVE_CONTROL_GATE_INVALID: pos/scramble/degree-match controls do not fire -> machinery invalid, do not interpret real.
  MIDDLE_BAND: best_constituent AUC in (0.55, 0.65) or above chance but not above the degree floor by the margin.

Compute architecture: (b) sequential-CPU with justification -- pocket is O(1e2) native gene-pairs x tiny (<=Nx32) Adam fits
  (ms each) + numpy solves + rank-sum AUCs; GPU yields no speedup on sub-ms matmuls; dominant cost = the (~1.5MB) MOESM4 + (~13KB)
  MOESM3 download (cached after first run). torch thread-capped. Storage: no_storage / no_composition (single-hop readout).
  Determinism: FIXED int seeds + numpy default_rng(seed*prime) + deterministic stratified split; no built-in salted-hash
  seeding, no set-to-list dedupe ordering (PROT-023 clean). ASCII-only; no bare except; except SystemExit before except
  Exception; atomic tmp+os.replace. Default invocation
  (no flag) = FULL run to completion. progress_logging: print_flush_true (ACQUIRE + per-seed detect lines, all flush=True).
"""

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF; float-hash on planted-pocket per-arm detection scores).
# - final_metrics_atomicity: tmp_replace (single-shot; os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: detection AUC has no closed-form CRLB for the bilinear-readout arm; the pre-registered AUC>=0.65 + margin-over-
#     degree + degree-matched-neutralization + scramble/pos controls substitute for a capacity-feasibility cap.
# - baseline_in_band: DEGREE/CHANCE floors measured ~0.5 on the degree-matched eval (planted degree-matched self-test asserts).
# - discriminator survives scale: self-test fires (a) POS control best_constituent AUC ~1.0 on a planted RECURRENT pocket at
#     plant scale, (b) SCRAMBLE collapses to ~0.5, (c) degree-matched neutralizes a planted degree<->SL confound (raw DEGREE
#     AUC > 0.6 -> matched DEGREE AUC ~0.5). Real-data discriminator is the DEGREE-MATCHED best_constituent AUC vs 0.65+margin.
# - HARD_PASS strictly above floor: AUC_HP=0.65 (>> 0.5) AND margin_over_degree>=0.10 (not a chance touch).
# - HP_SCOPE: HARD_PASS gates apply to best_constituent (SYM/ADD/ADD_RIDGE/ROLE) vs the degree-matched DEGREE floor only;
#     CHANCE/MEMORIZE are sanity contrasts (must sit ~0.5).
# - cardinality_ok: n_seeds detection folds; verdict counts len(per_seed) and NaN-guards; underpower gates fire on low counts.
# - per-unit failure-class instrumentation: acquire/parse/SMF/pocket/learnable failures -> explicit ACQUIRE_FAILED /
#     ESCALATE_NEED_RAW_CONSTITUENTS / HARD_FAIL_UNDERPOWERED_POCKET_N / STRUCTURAL_UNDERPOWER verdicts (no silent continue).
# - calibration_check: adaptive_with_discriminator_gate (units-adaptive near-zero-singles band [reused] + the STRUCTURAL learnable
#     gate + the degree-matched neutralization are the discriminator-still-fires verifications; MIN_LEARNABLE / MIN_POS_NOVEL are
#     the insufficient-power guards; the self-test fires POS/SCRAMBLE/degree-match on planted pockets and rejects a broken label).
# - all numbers in comments tagged MEASURED@ (parent metrics on disk) / CITED@ (Dede paper / VET) / to-be-MEASURED@ (real run).
# - real_code_path: self-test builds a SYNTHETIC Dede MOESM4-format raw-count TSV (reusing the parent's _make_synth_dede_moesm4)
#     + a synthetic MOESM3-format zdLFC TSV, runs them through the REAL _parse_dede_syms (adds token->symbol) + parse_zdlfc_moesm3
#     + near_zero_singles_mask + the REAL detect_run (SYM/ADD/ADD_RIDGE via the parent's _train_reg/arm_add_ridge) + roc_auc /
#     average_precision / degree_matched_negatives; hd_bind exercised on complex64 phasors (bind homomorphism).
# - deterministic_seeding: FIXED int seeds; numpy default_rng(seed*prime); sorted-set token ids; no salted-hash-seeded RNG,
#     no set-to-list dedupe ordering (PROT-023 static source scan clean).

import argparse
import hashlib
import json
import math
import os
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

torch.set_num_threads(int(os.environ.get("HDI_TORCH_THREADS", "2")))

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# REUSE the parent paralog cell's validated primitives (parser leaf helpers, curation, gene-code arms, controls fixture).
# The task mandates reusing the parser + near-zero-singles curation + gene-code construction. We import the leaf helpers and
# constants and RE-DERIVE only the two orchestration functions that must thread token->symbol (the parent parser returns
# tokenized X/y but not the id->symbol map needed to join the MOESM3 zdLFC label by gene symbol; editing the parent is out of
# scope under the concurrent module-2 lock). The copied parse is FAITHFUL to parent commit 651030f7e so the pocket is IDENTICAL.
from experiments.exp_paralog_crispr_nearzero_singles_curated_ivf_v1 import (  # noqa: E402
    acquire, near_zero_singles_mask, detect_smf_band, build_arena_from_mask,
    _train_reg, arm_add_ridge, _robust_center_scale,
    _read_rows, _detect_counts_columns, _split_gene_pair, _gene_sym, _finite_float, _norm,
    CACHE_DIR, PSEUDO, TOP_ORF, MAX_PAIRS, MIN_PAIRS, MIN_CTRL_REF, CTRL_TOKENS, CTRL_PREFIXES,
    SYM, ADD, ADDR, ROLE, EMB_D, hd_bind,
    _make_synth_dede_moesm4, SELFTEST_N_GENES, SELFTEST_N_NEUTRAL,
)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (ValueError, OSError):
        pass

ANCHOR_NAME = "paralog_crispr_sl_detection_auc_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)

# ---- detection arms ----
DEGREE = "DEGREE"; CHANCE = "CHANCE"; MEMO = "MEMORIZE"
CONSTITUENT_ARMS = [SYM, ADD, ADDR, ROLE]
DET_ARMS = [SYM, ADD, ADDR, ROLE, DEGREE, CHANCE, MEMO]

# ---- pre-registered bands (fixed BEFORE running) ----
Z_SL = 3.0                   # SL positive if zdLFC (or DMF-z fallback) <= -Z_SL. Dede's published SL call = zdLFC < -3.
SL_QUANTILE = 0.15           # secondary directional SL definition (worst 15% of pocket zdLFC) reported for the power check only
MIN_JOIN_FRAC = 0.5          # >= this fraction of pocket pairs must join to MOESM3 zdLFC else DMF-z fallback
MIN_POCKET = 50              # HARD_FAIL_UNDERPOWERED if fewer near-zero-singles pocket pairs (parent MIN_CURATED spirit)
MIN_DEG = 2                  # a gene must appear in >= this many pocket pairs to be LEARNABLE (recur across pairs)
MIN_LEARNABLE = 40           # STRUCTURAL_UNDERPOWER if the learnable sub-pocket (both genes deg>=MIN_DEG) is smaller
MIN_POS_NOVEL = 8.0          # mean scorable-novel positives per seed for adequate detection power
AUC_HP = 0.65                # HARD_PASS: best_constituent degree-matched novel ROC-AUC >= this (materially above chance)
MARGIN_OVER_DEGREE = 0.10    # AND best_constituent AUC - degree-matched DEGREE AUC >= this
AUC_NULL_CEIL = 0.55         # HARD_FAIL_GENUINE_NULL: best_constituent AUC <= this (not materially above chance)
DEGREE_MATCHED_CEIL = 0.58   # degree-matched DEGREE-arm AUC must sit <= this (matching neutralized popularity)
POS_CTRL_AUC = 0.90          # planted recurrent pocket best_constituent AUC floor (detection readout CAN detect)
SCRAMBLE_AUC_LO = 0.40       # scrambled-label best_constituent AUC band (must collapse to chance)
SCRAMBLE_AUC_HI = 0.60
K_TOPK = 10                  # precision@k
QFRAC = 0.40                 # query fraction (stratified by label)

SEEDS_FULL = (7, 13, 17, 23, 29, 31, 37, 41)
SEEDS_SMOKE = (7, 13, 17)


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    try:
        return ("%.4f" % x) if (x == x) else "nan"
    except (TypeError, ValueError):
        return "nan"


def _sig_f(arr):
    return hashlib.sha256(np.round(np.asarray(arr, dtype=np.float64), 6).tobytes()).hexdigest()[:16]


def _nanmean(vals):
    v = [x for x in vals if x == x]
    return float(np.mean(v)) if v else float("nan")


def _write_start_marker(expected_n_units, run_mode):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units)
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(OUT_DIR, "_start_marker.json"))


# ===========================================================================
# PARSE: faithful copy of parent parse_dede_encas12a + _finalize_pairs (commit 651030f7e), threading token->symbol (`toks`).
# ===========================================================================

def _finalize_pairs_syms(pair_dmf, smf_gene, n_rows, n_kept, diag):
    """Parent _finalize_pairs + returns `toks` (id->symbol). y = DMF; smf_tok[t] = mean SMF of token t (NaN if none)."""
    gene_freq = defaultdict(int)
    for (a, b) in pair_dmf:
        gene_freq[a] += 1; gene_freq[b] += 1
    top = set(sorted(gene_freq.keys(), key=lambda o: (-gene_freq[o], o))[:TOP_ORF])
    pairs = sorted([k for k in pair_dmf.keys() if k[0] in top and k[1] in top])
    if len(pairs) > MAX_PAIRS:
        stride = int(math.ceil(len(pairs) / float(MAX_PAIRS)))
        pairs = pairs[::stride][:MAX_PAIRS]
    if len(pairs) < MIN_PAIRS:
        return {"path": "B", "reason": "insufficient_native_pairs_after_subnetwork", "n_pairs": len(pairs), **diag}
    toks = sorted(set([o for k in pairs for o in k]))
    tokid = {o: i for i, o in enumerate(toks)}
    Xl = []
    for k in pairs:
        i0 = tokid[k[0]]; i1 = tokid[k[1]]
        Xl.append([min(i0, i1), max(i0, i1)])
    X = np.array(Xl, dtype=np.int64)
    y = np.array([pair_dmf[k] for k in pairs], dtype=np.float64)
    smf_tok = np.full(len(toks), np.nan, dtype=np.float64)
    n_smf_tok = 0
    for o, i in tokid.items():
        if o in smf_gene:
            smf_tok[i] = smf_gene[o]; n_smf_tok += 1
    return {"path": "A", "X": X, "y": y, "n_tok": len(toks), "n_pairs": len(pairs), "n_rows": n_rows, "n_kept": n_kept,
            "smf_tok": smf_tok, "n_smf_tok": int(n_smf_tok), "toks": toks, "diag": diag}


def _parse_dede_syms(counts_path):
    """Faithful copy of parent parse_dede_encas12a (CPM -> log2FC -> control detection -> SMF/DMF -> subnetwork), returning
    token->symbol via _finalize_pairs_syms. PATH 'A' (X,y=DMF,smf_tok,toks,...) or PATH 'B' (escalate diagnostic)."""
    rows = _read_rows(counts_path)
    if len(rows) < 3:
        return {"path": "B", "reason": "counts_file_empty_or_unreadable", "n_rows": len(rows)}
    header = rows[0]
    gi, bi, eidx = _detect_counts_columns(header)
    if gi is None:
        return {"path": "B", "reason": "no_gene_or_baseline_column", "header": [str(x) for x in header[:20]]}

    colsum = defaultdict(float)
    parsed = []
    for r in rows[1:]:
        if len(r) <= max(gi, bi, (max(eidx) if eidx else 0)):
            continue
        base = _finite_float(r[bi])
        if base is None:
            continue
        evals = []
        for c in eidx:
            v = _finite_float(r[c]) if c < len(r) else None
            evals.append(v)
        if not any(v is not None for v in evals):
            continue
        symA, symB = _split_gene_pair(r[gi])
        if symA is None or symB is None:
            continue
        colsum[bi] += base
        for c, v in zip(eidx, evals):
            if v is not None:
                colsum[c] += v
        parsed.append((symA, symB, base, evals))
    if len(parsed) < MIN_PAIRS:
        return {"path": "B", "reason": "too_few_parseable_count_rows", "n_rows": len(rows), "n_parsed": len(parsed),
                "header": [str(x) for x in header[:20]]}

    base_tot = colsum[bi] if colsum[bi] > 0 else 1.0
    end_tot = {c: (colsum[c] if colsum[c] > 0 else 1.0) for c in eidx}

    constructs = []
    for (symA, symB, base, evals) in parsed:
        cpm_base = 1e6 * base / base_tot
        lfcs = []
        for c, v in zip(eidx, evals):
            if v is None:
                continue
            cpm_end = 1e6 * v / end_tot[c]
            lfcs.append(math.log2((cpm_end + PSEUDO) / (cpm_base + PSEUDO)))
        if lfcs:
            constructs.append((symA, symB, float(np.mean(lfcs))))
    if len(constructs) < MIN_PAIRS:
        return {"path": "B", "reason": "too_few_constructs_with_lfc", "n_constructs": len(constructs)}

    partners = defaultdict(set)
    all_syms = set()
    for (a, b, _l) in constructs:
        all_syms.add(a); all_syms.add(b)
        partners[a].add(b); partners[b].add(a)
    n_syms = max(1, len(all_syms))

    def _is_ctrl_token(s):
        if s in CTRL_TOKENS:
            return True
        for p in CTRL_PREFIXES:
            if s.startswith(p):
                return True
        return False

    deg = {s: len(partners[s]) for s in all_syms}
    sorted_deg = sorted(deg.values())
    p75 = sorted_deg[int(0.75 * (len(sorted_deg) - 1))] if sorted_deg else 0
    deg_cut = max(8, int(math.ceil(4.0 * max(p75, 1))))
    ctrl_token = set(s for s in all_syms if _is_ctrl_token(s))
    ctrl_deg = set(s for s in all_syms if deg[s] >= deg_cut)
    degree_disabled = False
    if len(ctrl_deg) > 0.40 * n_syms:
        degree_disabled = True
        ctrl_deg = set()
    ctrl = ctrl_token | ctrl_deg
    ctrl_by_token = len(ctrl_token)
    ctrl_by_degree = len(ctrl_deg - ctrl_token)
    top_degree_tokens = [(s, deg[s]) for s in sorted(all_syms, key=lambda z: (-deg[z], z))[:12]]

    cc_lfcs = [lfc for (a, b, lfc) in constructs if (a in ctrl) and (b in ctrl) and math.isfinite(lfc)]
    if len(cc_lfcs) >= MIN_CTRL_REF:
        neutral_ref = float(np.median(cc_lfcs)); neutral_ref_src = "control_control_median"
    else:
        neutral_ref = 0.0; neutral_ref_src = "none_no_control_anchor"
    if not math.isfinite(neutral_ref):
        neutral_ref = 0.0; neutral_ref_src = "none_nonfinite_guard"

    smf_acc = defaultdict(lambda: [0.0, 0])
    dmf_acc = defaultdict(lambda: [0.0, 0])
    n_single = 0
    n_double = 0
    for (a, b, lfc) in constructs:
        lfc = lfc - neutral_ref
        a_c = a in ctrl
        b_c = b in ctrl
        if a_c and b_c:
            continue
        if a_c ^ b_c:
            real = b if a_c else a
            rec = smf_acc[real]; rec[0] += lfc; rec[1] += 1
            n_single += 1
        else:
            if a == b:
                continue
            key = (a, b) if a < b else (b, a)
            rec = dmf_acc[key]; rec[0] += lfc; rec[1] += 1
            n_double += 1

    diag = dict(n_constructs=len(constructs), n_syms=n_syms, n_ctrl=len(ctrl), ctrl_by_token=ctrl_by_token,
                ctrl_by_degree=ctrl_by_degree, deg_cut=deg_cut, degree_disabled=degree_disabled,
                top_degree_tokens=top_degree_tokens, n_single_constructs=n_single, n_double_constructs=n_double,
                ctrl_examples=sorted(ctrl)[:20], n_ctrl_ctrl=len(cc_lfcs), neutral_ref=round(neutral_ref, 5),
                neutral_ref_src=neutral_ref_src, endpoint_cols=[str(header[c]) for c in eidx][:12],
                baseline_col=str(header[bi]), gene_col=str(header[gi]))

    if n_single == 0 or len(smf_acc) == 0:
        return {"path": "B", "reason": "no_single_ko_controls_found", **diag}

    pair_dmf = {k: (s / c) for k, (s, c) in dmf_acc.items() if c >= 1}
    if len(pair_dmf) < MIN_PAIRS:
        return {"path": "B", "reason": "too_few_double_mutant_pairs", "n_pairs": len(pair_dmf), **diag}
    smf_gene = {g: (s / c) for g, (s, c) in smf_acc.items() if c >= 1}
    return _finalize_pairs_syms(pair_dmf, smf_gene, len(rows), n_double, diag)


# ===========================================================================
# MOESM3 zdLFC parser (per-pair z-normalized GI score, replicate-pooled over cell-line columns) -> symbol-keyed dict.
# ===========================================================================

def parse_zdlfc_moesm3(path):
    """Parse the Dede MOESM3 per-pair zdLFC file -> {canonical (symA,symB): mean zdLFC over numeric cell-line columns}.
    Robust to unknown exact header: the PAIR column is the column whose data cells most often split into a gene pair; numeric
    columns are the remaining mostly-finite-float columns. Two-single-symbol-column fallback if no single pair column exists."""
    rows = _read_rows(path)
    if len(rows) < 3:
        return {}, {"reason": "empty_or_unreadable", "n_rows": len(rows)}
    header = rows[0]
    ncol = len(header)
    sample = rows[1:min(len(rows), 120)]
    ns = max(1, len(sample))

    pair_col = None
    best = 0
    for c in range(ncol):
        hits = 0
        for r in sample:
            if c < len(r):
                a, b = _split_gene_pair(r[c])
                if a and b and a != b:
                    hits += 1
        if hits > best:
            best = hits; pair_col = c

    def _numeric_cols(exclude):
        cols = []
        for c in range(ncol):
            if c in exclude:
                continue
            fin = sum(1 for r in sample if c < len(r) and _finite_float(r[c]) is not None)
            if fin >= 0.6 * ns:
                cols.append(c)
        return cols

    out = {}
    diag = {}
    if pair_col is not None and best >= max(3, int(0.3 * ns)):
        num_cols = _numeric_cols({pair_col})
        diag = dict(mode="single_pair_col", pair_col=int(pair_col), pair_hits=int(best), num_cols=num_cols[:12],
                    header=[str(h) for h in header[:16]])
        if not num_cols:
            return {}, {**diag, "reason": "no_numeric_zdlfc_cols"}
        for r in rows[1:]:
            if pair_col >= len(r):
                continue
            a, b = _split_gene_pair(r[pair_col])
            if not a or not b or a == b:
                continue
            vals = [_finite_float(r[c]) for c in num_cols if c < len(r)]
            vals = [v for v in vals if v is not None]
            if not vals:
                continue
            key = (a, b) if a < b else (b, a)
            out.setdefault(key, []).append(float(np.mean(vals)))
    else:
        # fallback: two adjacent columns whose cells are single gene symbols (no pair separator)
        def _single_sym_frac(c):
            hits = 0
            for r in sample:
                if c < len(r):
                    s = _gene_sym(r[c])
                    a2, b2 = _split_gene_pair(r[c])
                    if s and not (a2 and b2):
                        hits += 1
            return hits / ns
        cand = [c for c in range(ncol) if _single_sym_frac(c) >= 0.6]
        if len(cand) < 2:
            return {}, {"reason": "no_pair_column_detected", "header": [str(h) for h in header[:16]]}
        ca, cb = cand[0], cand[1]
        num_cols = _numeric_cols({ca, cb})
        diag = dict(mode="two_symbol_cols", cols=(int(ca), int(cb)), num_cols=num_cols[:12],
                    header=[str(h) for h in header[:16]])
        if not num_cols:
            return {}, {**diag, "reason": "no_numeric_zdlfc_cols"}
        for r in rows[1:]:
            if ca >= len(r) or cb >= len(r):
                continue
            a = _gene_sym(r[ca]); b = _gene_sym(r[cb])
            if not a or not b or a == b:
                continue
            vals = [_finite_float(r[c]) for c in num_cols if c < len(r)]
            vals = [v for v in vals if v is not None]
            if not vals:
                continue
            key = (a, b) if a < b else (b, a)
            out.setdefault(key, []).append(float(np.mean(vals)))
    zmap = {k: float(np.mean(v)) for k, v in out.items()}
    diag["n_pairs_parsed"] = len(zmap)
    return zmap, diag


# ===========================================================================
# DETECTION METRICS (hand-rolled; no sklearn dependency on the remote runner)
# ===========================================================================

def _average_ranks(sorted_vals):
    """Average ranks (1..n) with ties averaged; sorted_vals ascending."""
    n = len(sorted_vals)
    ranks = np.empty(n, dtype=np.float64)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sorted_vals[j + 1] == sorted_vals[i]:
            j += 1
        avg = 0.5 * (i + 1 + j + 1)  # ranks are 1-based i+1..j+1
        ranks[i:j + 1] = avg
        i = j + 1
    return ranks


def roc_auc(scores, labels):
    """ROC-AUC via the Mann-Whitney rank-sum (higher score => more positive). NaN if a class is empty."""
    s = np.asarray(scores, dtype=np.float64)
    y = np.asarray(labels).astype(int)
    fin = np.isfinite(s)
    s = s[fin]; y = y[fin]
    npos = int((y == 1).sum()); nneg = int((y == 0).sum())
    if npos == 0 or nneg == 0:
        return float("nan")
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(len(s), dtype=np.float64)
    ranks[order] = _average_ranks(s[order])
    sum_pos = float(ranks[y == 1].sum())
    return (sum_pos - npos * (npos + 1) / 2.0) / (npos * nneg)


def average_precision(scores, labels):
    """AUPRC (average precision): sum over thresholds of (recall_k - recall_{k-1}) * precision_k."""
    s = np.asarray(scores, dtype=np.float64)
    y = np.asarray(labels).astype(int)
    fin = np.isfinite(s)
    s = s[fin]; y = y[fin]
    npos = int((y == 1).sum())
    if npos == 0:
        return float("nan")
    order = np.argsort(-s, kind="mergesort")
    ys = y[order]
    tp = np.cumsum(ys)
    fp = np.cumsum(1 - ys)
    precision = tp / np.maximum(tp + fp, 1)
    recall = tp / float(npos)
    ap = 0.0
    prev_r = 0.0
    for k in range(len(ys)):
        ap += (recall[k] - prev_r) * precision[k]
        prev_r = recall[k]
    return float(ap)


def precision_at_k(scores, labels, k):
    s = np.asarray(scores, dtype=np.float64)
    y = np.asarray(labels).astype(int)
    fin = np.isfinite(s)
    s = s[fin]; y = y[fin]
    if len(s) == 0:
        return float("nan")
    kk = int(min(k, len(s)))
    top = np.argsort(-s, kind="mergesort")[:kk]
    return float(y[top].mean())


def degree_matched_negatives(pos_local, neg_local, deg_local, seed, nbins=5):
    """Subsample negatives so their degree distribution matches the positives'. Returns matched negative indices (into the
    local eval array). Quantile-binned on the positive degrees; per-bin neg count == per-bin pos count (as feasible)."""
    rng = np.random.default_rng(seed * 100193 + 3)
    if len(pos_local) == 0 or len(neg_local) == 0:
        return np.array([], dtype=np.int64)
    pd = deg_local[pos_local].astype(np.float64)
    nd = deg_local[neg_local].astype(np.float64)
    edges = np.quantile(pd, np.linspace(0.0, 1.0, nbins + 1))
    edges[0] -= 1e-9; edges[-1] += 1e-9
    chosen = []
    for bi in range(nbins):
        lo, hi = edges[bi], edges[bi + 1]
        npos_bin = int(((pd >= lo) & (pd < hi)).sum())
        if npos_bin == 0:
            continue
        pool = neg_local[(nd >= lo) & (nd < hi)]
        if len(pool) == 0:
            continue
        take = int(min(npos_bin, len(pool)))
        chosen.append(rng.choice(pool, size=take, replace=False))
    if not chosen:
        return np.array([], dtype=np.int64)
    return np.concatenate(chosen)


# ===========================================================================
# DETECTION RUN (constituent arms regress the BINARY SL label; eval scorable-novel; raw + degree-matched)
# ===========================================================================

def _stratified_split(labels, seed, qfrac=QFRAC):
    """Stratified train/query split (query pairs are all NOVEL since pocket pairs are unique). Keeps positives in both."""
    rng = np.random.default_rng(seed * 100081 + 13)
    pos = np.where(labels == 1)[0]; neg = np.where(labels == 0)[0]
    rng.shuffle(pos); rng.shuffle(neg)
    nqp = int(round(qfrac * len(pos))); nqn = int(round(qfrac * len(neg)))
    nqp = min(max(nqp, 1), max(len(pos) - 1, 0)) if len(pos) >= 2 else 0
    nqn = min(max(nqn, 1), max(len(neg) - 1, 0)) if len(neg) >= 2 else 0
    q = np.concatenate([pos[:nqp], neg[:nqn]])
    tr = np.concatenate([pos[nqp:], neg[nqn:]])
    return np.sort(q), np.sort(tr)


def _detect_one_seed(Xc, labels, deg, n_tok, seed):
    """One detection fold. Returns per-arm raw + degree-matched AUC/AP/p@k on scorable-novel pairs, or None if degenerate."""
    q, tr = _stratified_split(labels, seed)
    if len(tr) < 4 or int(labels[tr].sum()) < 2 or int((labels[tr] == 0).sum()) < 2:
        return None
    train_toks = set(int(t) for t in Xc[tr].reshape(-1).tolist())
    scor = np.array([(int(Xc[i, 0]) in train_toks) and (int(Xc[i, 1]) in train_toks) for i in q], dtype=bool)
    q_s = q[scor]
    if len(q_s) < 6:
        return None
    lab_q = labels[q_s].astype(int)
    if int(lab_q.sum()) < 2 or int((lab_q == 0).sum()) < 2:
        return None
    Xq = Xc[q_s]; Xtr = Xc[tr]; ytr = labels[tr].astype(np.float64)
    rng = np.random.default_rng(seed * 777 + 11)
    preds = {
        SYM: _train_reg(Xtr, ytr, Xq, "sym", seed, n_tok),
        ADD: _train_reg(Xtr, ytr, Xq, "add", seed, n_tok),
        ROLE: _train_reg(Xtr, ytr, Xq, "role", seed, n_tok),
        ADDR: arm_add_ridge(Xtr, ytr, Xq, n_tok),
        DEGREE: (deg[Xq[:, 0]] + deg[Xq[:, 1]]).astype(np.float64),
        CHANCE: rng.random(len(q_s)),
        MEMO: np.full(len(q_s), float(ytr.mean()), dtype=np.float64),  # novel pairs unseen -> constant base rate -> ~chance
    }
    degq = (deg[Xq[:, 0]] + deg[Xq[:, 1]]).astype(np.float64)
    pos_local = np.where(lab_q == 1)[0]; neg_local = np.where(lab_q == 0)[0]
    neg_m = degree_matched_negatives(pos_local, neg_local, degq, seed)
    sel = np.concatenate([pos_local, neg_m]) if len(neg_m) > 0 else np.array([], dtype=np.int64)
    matched_valid = bool(len(sel) > 0 and int(lab_q[sel].sum()) >= 2 and int((lab_q[sel] == 0).sum()) >= 2)

    auc_raw = {a: roc_auc(preds[a], lab_q) for a in DET_ARMS}
    ap_raw = {a: average_precision(preds[a], lab_q) for a in DET_ARMS}
    pak_raw = {a: precision_at_k(preds[a], lab_q, K_TOPK) for a in DET_ARMS}
    if matched_valid:
        auc_m = {a: roc_auc(preds[a][sel], lab_q[sel]) for a in DET_ARMS}
    else:
        auc_m = {a: float("nan") for a in DET_ARMS}
    sigs = {a: _sig_f(preds[a]) for a in (SYM, ADD, ADDR, ROLE, DEGREE)}
    return dict(auc_raw=auc_raw, ap_raw=ap_raw, pak_raw=pak_raw, auc_matched=auc_m,
                n_scor=int(len(q_s)), n_pos=int(lab_q.sum()), n_neg=int((lab_q == 0).sum()),
                n_matched=int(len(sel)), base_rate=float(lab_q.mean()), matched_valid=matched_valid, sigs=sigs)


def detect_run(Xc, labels, seeds, tag):
    """Aggregate detection over seeds. Returns per-arm mean AUC (raw + degree-matched), power, base-rate, and the best
    constituent arm on the degree-matched eval (the HEADLINE)."""
    n_tok = int(Xc.max()) + 1 if Xc.shape[0] > 0 else 0
    deg = np.bincount(Xc.reshape(-1), minlength=n_tok).astype(np.float64) if n_tok > 0 else np.zeros(0)
    per = []
    for si, sd in enumerate(seeds):
        r = _detect_one_seed(Xc, labels, deg, n_tok, sd)
        per.append(r)
        if r is not None:
            _log("  [%s] detect seed %d/%d n_scor=%d n_pos=%d best_raw_AUC(SYM=%s ADD=%s ADDR=%s DEGm=%s)"
                 % (tag, si + 1, len(seeds), r["n_scor"], r["n_pos"], _fmt(r["auc_raw"][SYM]),
                    _fmt(r["auc_raw"][ADD]), _fmt(r["auc_raw"][ADDR]), _fmt(r["auc_matched"][DEGREE])))
        else:
            _log("  [%s] detect seed %d/%d DEGENERATE (too few scorable-novel or single-class train)" % (tag, si + 1, len(seeds)))
    valid = [r for r in per if r is not None]
    n_valid = len(valid)
    if n_valid == 0:
        return dict(tag=tag, n_valid=0, auc_raw={a: None for a in DET_ARMS}, auc_matched={a: None for a in DET_ARMS},
                    mean_n_scor=0.0, mean_n_pos=0.0, mean_base_rate=None, best_constituent_arm=None,
                    best_constituent_auc_matched=None, degree_auc_matched=None, per_seed_valid=0)
    auc_raw = {a: _nanmean([r["auc_raw"][a] for r in valid]) for a in DET_ARMS}
    auc_m = {a: _nanmean([r["auc_matched"][a] for r in valid]) for a in DET_ARMS}
    ap_raw = {a: _nanmean([r["ap_raw"][a] for r in valid]) for a in DET_ARMS}
    pak_raw = {a: _nanmean([r["pak_raw"][a] for r in valid]) for a in DET_ARMS}
    cons = [(a, auc_m[a]) for a in CONSTITUENT_ARMS if auc_m[a] == auc_m[a]]
    if cons:
        best_arm, best_auc = max(cons, key=lambda z: z[1])
    else:
        best_arm, best_auc = None, float("nan")
    mean_cons = _nanmean([auc_m[a] for a in CONSTITUENT_ARMS])
    return dict(
        tag=tag, n_valid=n_valid, per_seed_valid=n_valid,
        auc_raw={a: round(auc_raw[a], 5) if auc_raw[a] == auc_raw[a] else None for a in DET_ARMS},
        auc_matched={a: round(auc_m[a], 5) if auc_m[a] == auc_m[a] else None for a in DET_ARMS},
        ap_raw={a: round(ap_raw[a], 5) if ap_raw[a] == ap_raw[a] else None for a in DET_ARMS},
        pak_raw={a: round(pak_raw[a], 5) if pak_raw[a] == pak_raw[a] else None for a in DET_ARMS},
        mean_n_scor=round(float(np.mean([r["n_scor"] for r in valid])), 2),
        mean_n_pos=round(float(np.mean([r["n_pos"] for r in valid])), 2),
        mean_base_rate=round(float(np.mean([r["base_rate"] for r in valid])), 4),
        best_constituent_arm=best_arm,
        best_constituent_auc_matched=round(best_auc, 5) if best_auc == best_auc else None,
        best_constituent_auc_raw=round(_nanmean([auc_raw[a] for a in CONSTITUENT_ARMS]), 5),
        mean_constituent_auc_matched=round(mean_cons, 5) if mean_cons == mean_cons else None,
        sym_auc_matched=round(auc_m[SYM], 5) if auc_m[SYM] == auc_m[SYM] else None,
        degree_auc_matched=round(auc_m[DEGREE], 5) if auc_m[DEGREE] == auc_m[DEGREE] else None,
        degree_auc_raw=round(auc_raw[DEGREE], 5) if auc_raw[DEGREE] == auc_raw[DEGREE] else None,
        chance_auc_matched=round(auc_m[CHANCE], 5) if auc_m[CHANCE] == auc_m[CHANCE] else None,
    )


# ===========================================================================
# planted pockets (controls + self-test)
# ===========================================================================

def _plant_recurrent_pocket(seed=7, n_genes=40, n_draw=1200, sl_frac=0.25, rank=2):
    """Planted RECURRENT pocket (genes recur -> constituent codes learnable). SL label = threshold of a LOW-RANK SYMMETRIC
    pairwise function u_a . u_b (rank << EMB_D so the SYM bilinear readout CAN reconstruct it -> SYM-detectable; additive
    main-effects ~0 so ADD/ADD_RIDGE stay near chance). Uniform endpoint sampling -> near-uniform degree (no popularity signal).
    Returns (Xc, labels, n_tok)."""
    rng = np.random.default_rng(seed)
    a = rng.integers(0, n_genes, size=n_draw); b = rng.integers(0, n_genes, size=n_draw)
    keep = a != b
    a, b = a[keep], b[keep]
    uniq = sorted(set((min(int(x), int(y)), max(int(x), int(y))) for x, y in zip(a, b)))
    X = np.array(uniq, dtype=np.int64)
    U = rng.normal(0.0, 1.0, size=(n_genes, rank))
    val = np.array([float(U[int(X[i, 0])] @ U[int(X[i, 1])]) for i in range(X.shape[0])], dtype=np.float64)
    thr = float(np.quantile(val, 1.0 - sl_frac))
    labels = (val >= thr).astype(np.float64)
    toks = sorted(set(int(t) for t in X.reshape(-1).tolist()))
    remap = {t: i for i, t in enumerate(toks)}
    Xr = np.array([[remap[int(r[0])], remap[int(r[1])]] for r in X], dtype=np.int64)
    Xr = np.stack([Xr.min(axis=1), Xr.max(axis=1)], axis=1)
    return Xr, labels, len(toks)


def _plant_degree_confounded_pocket(seed=19, n_genes=40, n_draw=3000, sl_frac=0.25, noise_scale=1.0):
    """Planted pocket with HETEROGENEOUS degree (Zipf-ish endpoint sampling) and a DEGREE-BIASED SL label (SL more likely for
    high-degree pairs, with noise so high-degree NEUTRALS remain available for matching). Raw DEGREE-arm AUC >> 0.5; degree-
    matched DEGREE-arm AUC ~0.5 (matching neutralizes marginal popularity). Validates the degree-matched-negatives control."""
    rng = np.random.default_rng(seed)
    w = (np.arange(n_genes) + 1.0) ** 1.5
    p = w / w.sum()
    a = rng.choice(n_genes, size=n_draw, p=p); b = rng.choice(n_genes, size=n_draw, p=p)
    keep = a != b
    a, b = a[keep], b[keep]
    uniq = sorted(set((min(int(x), int(y)), max(int(x), int(y))) for x, y in zip(a, b)))
    X = np.array(uniq, dtype=np.int64)
    gdeg = np.bincount(X.reshape(-1), minlength=n_genes).astype(np.float64)
    degsum = gdeg[X[:, 0]] + gdeg[X[:, 1]]
    val = degsum + noise_scale * (float(np.std(degsum)) + 1e-9) * rng.normal(0.0, 1.0, size=X.shape[0])
    thr = float(np.quantile(val, 1.0 - sl_frac))
    labels = (val >= thr).astype(np.float64)
    toks = sorted(set(int(t) for t in X.reshape(-1).tolist()))
    remap = {t: i for i, t in enumerate(toks)}
    Xr = np.array([[remap[int(r[0])], remap[int(r[1])]] for r in X], dtype=np.int64)
    Xr = np.stack([Xr.min(axis=1), Xr.max(axis=1)], axis=1)
    return Xr, labels, len(toks)


# ===========================================================================
# label construction on the real pocket
# ===========================================================================

def build_pocket_labels(X, y, smf_tok, toks, zmap):
    """Return (detect_mask, labels_full, label_info). PRIMARY = MOESM3 zdLFC joined by symbol (SL if zdLFC<=-Z_SL); FALLBACK =
    DMF robust-z within pocket (SL if z<=-Z_SL). detect_mask = pocket pairs carrying a finite label."""
    n = X.shape[0]
    lo, hi, units = detect_smf_band(smf_tok)
    pocket = near_zero_singles_mask(X, smf_tok, lo, hi)
    n_pocket = int(pocket.sum())

    # symbol keys per pair
    canon = []
    for i in range(n):
        a = toks[int(X[i, 0])]; b = toks[int(X[i, 1])]
        canon.append((a, b) if a < b else (b, a))
    zdlfc_pair = np.array([zmap.get(k, np.nan) for k in canon], dtype=np.float64) if zmap else np.full(n, np.nan)
    pocket_idx = np.where(pocket)[0]
    if pocket_idx.size > 0 and zmap:
        pocket_join = float(np.isfinite(zdlfc_pair[pocket_idx]).mean())
    else:
        pocket_join = 0.0

    use_zdlfc = bool(zmap and pocket_join >= MIN_JOIN_FRAC)
    if use_zdlfc:
        valid = np.isfinite(zdlfc_pair)
        labels_full = np.where(zdlfc_pair <= -Z_SL, 1.0, 0.0)
        detect_mask = pocket & valid
        source = "zdlfc_moesm3"
        z_for_quant = zdlfc_pair
    else:
        yp = y[pocket_idx] if pocket_idx.size > 0 else y
        med, scale = _robust_center_scale(yp if yp.size > 0 else y)
        z = (y - med) / (scale if scale > 1e-9 else 1.0)
        labels_full = np.where(z <= -Z_SL, 1.0, 0.0)
        detect_mask = pocket.copy()
        source = "dmf_robust_z_fallback"
        z_for_quant = z

    # secondary directional SL definition (worst SL_QUANTILE of the pocket) for a power cross-check only
    n_pos_primary = int(labels_full[detect_mask].sum()) if detect_mask.sum() > 0 else 0
    dm_idx = np.where(detect_mask)[0]
    if dm_idx.size > 0:
        zq = z_for_quant[dm_idx]
        zq = zq[np.isfinite(zq)]
        n_pos_quantile = int(round(SL_QUANTILE * dm_idx.size))
    else:
        n_pos_quantile = 0

    info = dict(label_source=source, smf_units=units, smf_band=[round(lo, 4), round(hi, 4)],
                n_pocket=n_pocket, pocket_join_frac=round(pocket_join, 4) if zmap else None,
                zdlfc_pairs_available=len(zmap) if zmap else 0, Z_SL=Z_SL,
                n_detect=int(detect_mask.sum()), n_pos_primary=n_pos_primary,
                base_rate_primary=round(n_pos_primary / float(max(detect_mask.sum(), 1)), 4),
                n_pos_quantile_secondary=n_pos_quantile)
    return detect_mask, labels_full, info


def learnable_structure(Xc):
    """Learnable sub-pocket = pairs whose BOTH tokens have detection-arena degree >= MIN_DEG (recur across pairs)."""
    n_tok = int(Xc.max()) + 1 if Xc.shape[0] > 0 else 0
    if n_tok == 0:
        return 0, 0.0, np.zeros(0, dtype=bool)
    deg = np.bincount(Xc.reshape(-1), minlength=n_tok)
    recur = np.array([(deg[int(Xc[i, 0])] >= MIN_DEG) and (deg[int(Xc[i, 1])] >= MIN_DEG)
                      for i in range(Xc.shape[0])], dtype=bool)
    avg_deg = float(2.0 * Xc.shape[0] / n_tok) if n_tok > 0 else 0.0
    return int(recur.sum()), avg_deg, recur


# ===========================================================================
# full measurement
# ===========================================================================

def run_measurement(seeds, run_mode):
    _write_start_marker(expected_n_units=len(seeds), run_mode=run_mode)
    t0 = time.perf_counter()
    counts_path, zdlfc_path, prov = acquire()
    base = dict(run_mode=run_mode, anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
                elapsed_s=round(time.perf_counter() - t0, 2), provenance=prov, seeds=list(seeds),
                bands=dict(Z_SL=Z_SL, MIN_POCKET=MIN_POCKET, MIN_DEG=MIN_DEG, MIN_LEARNABLE=MIN_LEARNABLE,
                           MIN_POS_NOVEL=MIN_POS_NOVEL, AUC_HP=AUC_HP, MARGIN_OVER_DEGREE=MARGIN_OVER_DEGREE,
                           AUC_NULL_CEIL=AUC_NULL_CEIL, DEGREE_MATCHED_CEIL=DEGREE_MATCHED_CEIL, POS_CTRL_AUC=POS_CTRL_AUC,
                           SCRAMBLE_AUC_LO=SCRAMBLE_AUC_LO, SCRAMBLE_AUC_HI=SCRAMBLE_AUC_HI, MIN_JOIN_FRAC=MIN_JOIN_FRAC,
                           K_TOPK=K_TOPK, QFRAC=QFRAC))

    # ---- CONTROLS (planted; machinery must be valid before real interpretation) ----
    Xpos, lpos, _ = _plant_recurrent_pocket(seed=7)
    pos_res = detect_run(Xpos, lpos, (7, 13, 17), "POS_CTRL")
    pos_auc = pos_res.get("best_constituent_auc_matched")
    pos_ok = bool(pos_auc is not None and pos_auc >= POS_CTRL_AUC)

    lscr = lpos.copy()
    np.random.default_rng(101).shuffle(lscr)
    scr_res = detect_run(Xpos, lscr, (7, 13, 17), "SCRAMBLE_CTRL")
    scr_auc = scr_res.get("mean_constituent_auc_matched")  # MEAN (not max) is stable under the null; max-of-4 inflates
    scr_ok = bool(scr_auc is not None and SCRAMBLE_AUC_LO <= scr_auc <= SCRAMBLE_AUC_HI)

    # degree-confounded planted pocket: raw DEGREE arm beats chance, matched DEGREE arm neutralized ~0.5
    Xdc, ldc, _ = _plant_degree_confounded_pocket(seed=19)
    dc_res = detect_run(Xdc, ldc, (7, 13, 17), "DEGREE_MATCH_CTRL")
    dc_raw = dc_res.get("degree_auc_raw"); dc_matched = dc_res.get("degree_auc_matched")
    degmatch_ok = bool(dc_raw is not None and dc_matched is not None and dc_raw >= 0.56
                       and dc_matched <= DEGREE_MATCHED_CEIL and (dc_raw - dc_matched) >= 0.05)
    controls_ok = bool(pos_ok and scr_ok and degmatch_ok)
    base["controls"] = dict(pos_best_auc_matched=pos_auc, pos_ok=pos_ok,
                            scramble_mean_constituent_auc_matched=scr_auc, scramble_ok=scr_ok,
                            degconfound_degree_auc_raw=dc_raw, degconfound_degree_auc_matched=dc_matched,
                            degmatch_ok=degmatch_ok, controls_ok=controls_ok,
                            pos_detail=pos_res, scramble_detail=scr_res, degmatch_detail=dc_res)

    if counts_path is None:
        msg = ("ACQUIRE_FAILED || could not download the Dede 2020 MOESM4 raw-count file (see provenance.acquire_errors). "
               "controls_ok=%s" % controls_ok)
        base.update(verdict="ACQUIRE_FAILED", verdict_msg=msg, summary=msg[:200])
        base["elapsed_s"] = round(time.perf_counter() - t0, 2)
        return base

    try:
        data = _parse_dede_syms(counts_path)
    except (OSError, ValueError, UnicodeDecodeError) as e:
        msg = "ACQUIRE_FAILED || Dede MOESM4 present but unreadable: %s: %s. controls_ok=%s" % (type(e).__name__, str(e)[:160], controls_ok)
        base.update(verdict="ACQUIRE_FAILED", verdict_msg=msg, summary=msg[:200], parse_error=str(e)[:300])
        base["elapsed_s"] = round(time.perf_counter() - t0, 2)
        return base

    if data["path"] == "B":
        reason = data.get("reason", "")
        verdict = ("ESCALATE_NEED_RAW_CONSTITUENTS" if reason in ("no_gene_or_baseline_column", "no_single_ko_controls_found")
                   else "ESCALATE_NO_NATIVEPAIR_STRUCTURE")
        msg = ("%s || parser could not build the raw SMF/DMF pocket (reason=%s). controls_ok=%s" % (verdict, reason, controls_ok))
        base.update(verdict=verdict, verdict_msg=msg, summary=msg[:200], escalate=True, path="B",
                    parse_diag={k: v for k, v in data.items() if k not in ("path", "X", "y", "smf_tok", "toks")})
        base["elapsed_s"] = round(time.perf_counter() - t0, 2)
        return base

    X, y, n_tok, toks = data["X"], data["y"], data["n_tok"], data["toks"]
    smf_tok = data.get("smf_tok")
    if smf_tok is None or int(data.get("n_smf_tok", 0)) == 0:
        msg = "ESCALATE_NEED_RAW_CONSTITUENTS || parsed pairs carry no per-gene SMF (near-zero-singles curation impossible). controls_ok=%s" % controls_ok
        base.update(verdict="ESCALATE_NEED_RAW_CONSTITUENTS", verdict_msg=msg, summary=msg[:200], escalate=True, path="A")
        base["elapsed_s"] = round(time.perf_counter() - t0, 2)
        return base

    zmap, zdiag = parse_zdlfc_moesm3(zdlfc_path) if zdlfc_path else ({}, {"reason": "no_zdlfc_file"})
    detect_mask, labels_full, linfo = build_pocket_labels(X, y, smf_tok, toks, zmap)
    n_pocket = linfo["n_pocket"]
    base["label_info"] = linfo
    base["zdlfc_parse_diag"] = zdiag

    _log("PATH A: n_pairs=%d n_tok=%d | pocket=%d | label_source=%s join=%s | n_detect=%d n_pos=%d"
         % (X.shape[0], n_tok, n_pocket, linfo["label_source"], str(linfo["pocket_join_frac"]),
            linfo["n_detect"], linfo["n_pos_primary"]))

    if n_pocket < MIN_POCKET:
        msg = ("HARD_FAIL_UNDERPOWERED_POCKET_N || only %d near-zero-singles pocket pairs < MIN_POCKET=%d. controls_ok=%s"
               % (n_pocket, MIN_POCKET, controls_ok))
        base.update(verdict="HARD_FAIL_UNDERPOWERED_POCKET_N", verdict_msg=msg, summary=msg[:200], escalate=True, path="A",
                    n_pairs=int(X.shape[0]), n_tok=int(n_tok), n_pocket=n_pocket)
        base["elapsed_s"] = round(time.perf_counter() - t0, 2)
        return base

    # build detection arena from the labelled pocket
    Xc, _yc, n_tok_c = build_arena_from_mask(X, y, detect_mask)
    labels_c = labels_full[detect_mask].astype(np.float64)
    n_detect = int(Xc.shape[0])
    n_pos = int(labels_c.sum())
    n_learnable, avg_deg, _recur = learnable_structure(Xc)
    struct = dict(n_detect=n_detect, n_tok_detect=int(n_tok_c), n_pos=n_pos, base_rate=round(n_pos / float(max(n_detect, 1)), 4),
                  avg_gene_degree=round(avg_deg, 4), n_learnable_subpocket=n_learnable, MIN_DEG=MIN_DEG, MIN_LEARNABLE=MIN_LEARNABLE)
    base["structure"] = struct
    _log("STRUCTURE: n_detect=%d n_tok=%d n_pos=%d avg_gene_degree=%.3f learnable_subpocket=%d (MIN_LEARNABLE=%d)"
         % (n_detect, n_tok_c, n_pos, avg_deg, n_learnable, MIN_LEARNABLE))

    # STRUCTURAL gate: without gene recurrence, no constituent method can generalize to novel pairs (not a genuine null).
    if n_learnable < MIN_LEARNABLE or n_pos < 4:
        msg = ("STRUCTURAL_UNDERPOWER_GENES_DONT_RECUR || learnable sub-pocket=%d (< MIN_LEARNABLE=%d) / n_pos=%d ; avg gene "
               "pocket-degree=%.3f -- a near-matching: constituent-identity readouts cannot generalize to NOVEL pairs (genes do "
               "not recur). NOT a genuine-null, NOT a harness-mismatch: the reframe is UNTESTABLE on this pocket. HAND-OFF: "
               "escalate to a COMBINATORIAL screen where each gene is crossed against many partners (Horlbeck GSE / Perturb-seq "
               "all-by-all / harmonized compendium) so gene-level SL-propensity is learnable. controls_ok=%s"
               % (n_learnable, MIN_LEARNABLE, n_pos, avg_deg, controls_ok))
        base.update(verdict="STRUCTURAL_UNDERPOWER_GENES_DONT_RECUR", verdict_msg=msg, summary=msg[:200], escalate=True,
                    path="A", n_pairs=int(X.shape[0]), n_tok=int(n_tok))
        base["elapsed_s"] = round(time.perf_counter() - t0, 2)
        return base

    # ---- DETECTION on the real pocket ----
    real = detect_run(Xc, labels_c, seeds, "REAL")
    base["detection"] = real
    best_arm = real.get("best_constituent_arm")
    best_auc = real.get("best_constituent_auc_matched")
    deg_auc_m = real.get("degree_auc_matched")
    mean_pos = real.get("mean_n_pos", 0.0)
    n_valid = real.get("n_valid", 0)

    power_ok = bool(mean_pos is not None and mean_pos >= MIN_POS_NOVEL and n_valid >= max(2, len(seeds) // 2))
    margin = (best_auc - deg_auc_m) if (best_auc is not None and deg_auc_m is not None) else float("nan")
    beats_chance = bool(best_auc is not None and best_auc >= AUC_HP)
    beats_degree = bool(margin == margin and margin >= MARGIN_OVER_DEGREE)
    is_null = bool(best_auc is not None and best_auc <= AUC_NULL_CEIL and not (margin == margin and margin >= MARGIN_OVER_DEGREE))

    if not controls_ok:
        verdict = "INCONCLUSIVE_CONTROL_GATE_INVALID"
    elif not power_ok:
        verdict = "STRUCTURAL_UNDERPOWER_GENES_DONT_RECUR"
    elif beats_chance and beats_degree:
        verdict = "HARD_PASS_HARNESS_MISMATCH_SL_DETECTABLE"
    elif is_null:
        verdict = "HARD_FAIL_GENUINE_NULL_SL_NOT_DETECTABLE"
    else:
        verdict = "MIDDLE_BAND"

    escalate_tail = ""
    if verdict == "HARD_FAIL_GENUINE_NULL_SL_NOT_DETECTABLE":
        escalate_tail = (" || HAND-OFF: even the detection/ranking framing on the higher-SNR label finds SL not separable from "
                         "constituents on NOVEL learnable pocket pairs -> genuine null; escalate to higher-N pooled screens or drop.")
    elif verdict == "STRUCTURAL_UNDERPOWER_GENES_DONT_RECUR":
        escalate_tail = (" || HAND-OFF: mean scorable-novel positives=%.1f < MIN_POS_NOVEL=%.0f (or too few valid folds) -- "
                         "underpowered; escalate to a denser screen." % (mean_pos or 0.0, MIN_POS_NOVEL))

    msg = ("%s || label=%s(join=%s) | pocket=%d detect=%d n_pos=%d base_rate=%s avg_gene_deg=%.3f learnable=%d | "
           "best_constituent=%s AUC_matched=%s (raw=%s) vs DEGREE_matched=%s margin=%s (HP=%.2f margin>=%.2f) | "
           "SYM=%s ADD=%s ADDR=%s ROLE=%s DEGREEm=%s CHANCEm=%s | AP(SYM)=%s p@%d(best)=%s | "
           "power_ok=%s(mean_pos=%.1f valid=%d/%d) | CTRL pos=%s(>=%.2f %s) scramble=%s([%.2f,%.2f] %s) degmatch=%s"
           % (verdict, linfo["label_source"], str(linfo["pocket_join_frac"]), n_pocket, n_detect, n_pos,
              str(real.get("mean_base_rate")), avg_deg, n_learnable,
              str(best_arm), _fmt(best_auc) if best_auc is not None else "nan",
              _fmt(real.get("best_constituent_auc_raw")) if real.get("best_constituent_auc_raw") is not None else "nan",
              _fmt(deg_auc_m) if deg_auc_m is not None else "nan", _fmt(margin),
              AUC_HP, MARGIN_OVER_DEGREE,
              str(real["auc_matched"][SYM]), str(real["auc_matched"][ADD]), str(real["auc_matched"][ADDR]),
              str(real["auc_matched"][ROLE]), str(real["auc_matched"][DEGREE]), str(real["auc_matched"][CHANCE]),
              str(real["ap_raw"][SYM]), K_TOPK, str(real["pak_raw"].get(best_arm) if best_arm else None),
              power_ok, mean_pos or 0.0, n_valid, len(seeds),
              _fmt(pos_auc) if pos_auc is not None else "nan", POS_CTRL_AUC, pos_ok,
              _fmt(scr_auc) if scr_auc is not None else "nan", SCRAMBLE_AUC_LO, SCRAMBLE_AUC_HI, scr_ok,
              degmatch_ok) + escalate_tail)

    base.update(verdict=verdict, verdict_msg=msg, summary=msg[:200], path="A",
                escalate=verdict.startswith(("STRUCTURAL", "HARD_FAIL", "ESCALATE")),
                n_pairs=int(X.shape[0]), n_tok=int(n_tok),
                gates=dict(controls_ok=controls_ok, power_ok=power_ok, beats_chance=beats_chance, beats_degree=beats_degree,
                           is_null=is_null, best_constituent_auc_matched=best_auc, degree_auc_matched=deg_auc_m,
                           margin_over_degree=round(margin, 5) if margin == margin else None))
    base["elapsed_s"] = round(time.perf_counter() - t0, 2)
    return base


def _write_metrics(metrics):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=float)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))


# ===========================================================================
# SELF-TEST (real bind + real parser on synthetic MOESM4 + synthetic MOESM3 zdLFC + real detect_run + AUC helpers)
# ===========================================================================

def _make_synth_moesm3(path, syms_pairs, z_of_pair):
    """Write a synthetic Dede MOESM3-format zdLFC TSV: a single pair-id column 'GENE' ('symA:symB') + 3 cell-line zdLFC cols."""
    header = ["GENE", "zdLFC.A549", "zdLFC.HT29", "zdLFC.OVCAR8"]
    lines = ["\t".join(header)]
    rng = np.random.default_rng(7)
    for (a, b) in syms_pairs:
        z = z_of_pair((a, b))
        cells = ["%s.1:%s.1" % (a, b)] + ["%.4f" % (z + 0.05 * rng.normal()) for _ in range(3)]
        lines.append("\t".join(cells))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def self_test():
    ok_all = True
    details = {}

    # (1) REAL substrate bind homomorphism (complex64 FHRR = elementwise multiply).
    g = np.random.default_rng(31)
    m = g.integers(1, 9, size=64).astype(np.float64)
    jj = np.arange(9, dtype=np.float64)[:, None]
    Yc = torch.from_numpy(np.exp(1j * (2.0 * np.pi / 9.0) * (jj * m[None, :])).astype(np.complex64))
    bound = hd_bind(Yc[torch.tensor([1, 2])], Yc[torch.tensor([2, 3])])
    homo_ok = torch.argmax((bound @ Yc.conj().T.contiguous()).real, 1).tolist() == [3 % 9, 5 % 9]
    details["fhrr_bind_homomorphism_ok"] = homo_ok

    # (2) AUC/AP helpers on a hand-checkable case.
    auc_perfect = roc_auc([0.1, 0.2, 0.9, 0.8], [0, 0, 1, 1])          # perfect separation -> 1.0
    auc_rev = roc_auc([0.9, 0.8, 0.1, 0.2], [0, 0, 1, 1])             # reversed -> 0.0
    auc_tie = roc_auc([0.5, 0.5, 0.5, 0.5], [0, 0, 1, 1])            # all ties -> 0.5
    ap_perfect = average_precision([0.1, 0.2, 0.9, 0.8], [0, 0, 1, 1])
    auc_helpers_ok = bool(abs(auc_perfect - 1.0) < 1e-9 and abs(auc_rev - 0.0) < 1e-9 and abs(auc_tie - 0.5) < 1e-9
                          and abs(ap_perfect - 1.0) < 1e-9)
    details.update(auc_perfect=round(auc_perfect, 4), auc_reversed=round(auc_rev, 4), auc_tie=round(auc_tie, 4),
                   ap_perfect=round(ap_perfect, 4), auc_helpers_ok=auc_helpers_ok)

    # (3) REAL raw-count PARSER (parent fixture) through _parse_dede_syms -> PATH A with toks (id->symbol).
    tmp_txt = os.path.join(CACHE_DIR, "_selftest_detect_synth_moesm4.txt")
    os.makedirs(CACHE_DIR, exist_ok=True)
    _make_synth_dede_moesm4(tmp_txt, n_genes=SELFTEST_N_GENES, n_neutral=SELFTEST_N_NEUTRAL, n_guides=3)
    import experiments.exp_paralog_crispr_nearzero_singles_curated_ivf_v1 as _parent
    saved = _parent.MIN_PAIRS
    global MIN_PAIRS
    _saved_local = MIN_PAIRS
    try:
        _parent.MIN_PAIRS = 40
        MIN_PAIRS = 40
        sd = _parse_dede_syms(tmp_txt)
    finally:
        _parent.MIN_PAIRS = saved
        MIN_PAIRS = _saved_local
        try:
            os.remove(tmp_txt)
        except OSError:
            pass
    n_exp_pairs = SELFTEST_N_GENES * (SELFTEST_N_GENES - 1) // 2
    parser_ok = bool(sd.get("path") == "A" and sd.get("n_tok", 0) == SELFTEST_N_GENES
                     and sd.get("n_pairs", 0) == n_exp_pairs and len(sd.get("toks", [])) == SELFTEST_N_GENES)
    details.update(parser_path=sd.get("path"), parser_n_pairs=sd.get("n_pairs"), parser_n_tok=sd.get("n_tok"),
                   parser_n_toks_list=len(sd.get("toks", [])), parser_ok=parser_ok)

    # (3b) MOESM3 zdLFC parser + join: plant zdLFC so both-neutral (near-zero-singles) pairs are strongly-SL, join by symbol.
    zdlfc_ok = False
    if sd.get("path") == "A":
        toks = sd["toks"]; Xf = sd["X"]
        # both-neutral tokens are the first SELFTEST_N_NEUTRAL (G00..): plant strong-negative zdLFC on both-neutral pairs.
        syms_pairs = []
        z_of = {}
        for i in range(Xf.shape[0]):
            a = toks[int(Xf[i, 0])]; b = toks[int(Xf[i, 1])]
            key = (a, b) if a < b else (b, a)
            syms_pairs.append(key)
            both_neutral = (int(Xf[i, 0]) < SELFTEST_N_NEUTRAL) and (int(Xf[i, 1]) < SELFTEST_N_NEUTRAL)
            z_of[key] = -6.0 if both_neutral else 0.0
        zpath = os.path.join(CACHE_DIR, "_selftest_detect_synth_moesm3.txt")
        _make_synth_moesm3(zpath, syms_pairs, lambda k: z_of[k])
        try:
            zmap, zdiag = parse_zdlfc_moesm3(zpath)
        finally:
            try:
                os.remove(zpath)
            except OSError:
                pass
        # join coverage + correctness: all planted pairs recovered, both-neutral pairs SL
        join_hits = sum(1 for k in syms_pairs if k in zmap)
        both_neutral_sl = all((zmap.get(k, 0.0) <= -Z_SL) for k in syms_pairs
                              if z_of[k] <= -Z_SL)
        zdlfc_ok = bool(join_hits == len(set(syms_pairs)) and both_neutral_sl and len(zmap) > 0)
        details.update(zdlfc_join_hits=join_hits, zdlfc_n_unique=len(set(syms_pairs)), zdlfc_parsed=len(zmap),
                       zdlfc_mode=zdiag.get("mode"), zdlfc_ok=zdlfc_ok)

    # (4) POS control: planted RECURRENT low-rank pocket, SYM-detectable SL -> best_constituent AUC ~1.0 at plant scale.
    Xpos, lpos, _ = _plant_recurrent_pocket(seed=7)
    pos_res = detect_run(Xpos, lpos, (7, 13, 17), "ST_POS")
    pos_ok = bool(pos_res["best_constituent_auc_matched"] is not None and pos_res["best_constituent_auc_matched"] >= POS_CTRL_AUC)
    details.update(pos_best_auc=pos_res["best_constituent_auc_matched"], pos_sym_auc=pos_res.get("sym_auc_matched"),
                   pos_degree_auc=pos_res["degree_auc_matched"], pos_ok=pos_ok)

    # (5) SCRAMBLE control: permuted labels -> MEAN constituent AUC ~0.5 (collapse; mean is stable, max-of-4 inflates).
    lscr = lpos.copy(); np.random.default_rng(101).shuffle(lscr)
    scr_res = detect_run(Xpos, lscr, (7, 13, 17), "ST_SCR")
    scr_auc = scr_res["mean_constituent_auc_matched"]
    scr_ok = bool(scr_auc is not None and SCRAMBLE_AUC_LO <= scr_auc <= SCRAMBLE_AUC_HI)
    details.update(scramble_mean_constituent_auc=scr_auc, scramble_ok=scr_ok)

    # (6) DEGREE-MATCH control: degree-confounded SL -> raw DEGREE AUC beats chance, matched DEGREE AUC neutralized ~0.5.
    Xdc, ldc, _ = _plant_degree_confounded_pocket(seed=19)
    dc_res = detect_run(Xdc, ldc, (7, 13, 17), "ST_DEGM")
    dc_raw = dc_res["degree_auc_raw"]; dc_m = dc_res["degree_auc_matched"]
    degmatch_ok = bool(dc_raw is not None and dc_m is not None and dc_raw >= 0.56 and dc_m <= DEGREE_MATCHED_CEIL
                       and (dc_raw - dc_m) >= 0.05)
    details.update(degconfound_degree_auc_raw=dc_raw, degconfound_degree_auc_matched=dc_m, degmatch_ok=degmatch_ok)

    # (7) ARMS-MUST-DIFFER (META_RULE_AF) on the planted pocket detection scores + determinism.
    r1 = _detect_one_seed(Xpos, lpos, np.bincount(Xpos.reshape(-1)).astype(np.float64), int(Xpos.max()) + 1, 5)
    r2 = _detect_one_seed(Xpos, lpos, np.bincount(Xpos.reshape(-1)).astype(np.float64), int(Xpos.max()) + 1, 5)
    arms_differ = bool(r1 is not None and len(set(r1["sigs"].values())) >= len(r1["sigs"]) - 1)
    determinism_ok = bool(r1 is not None and r2 is not None and r1["sigs"][SYM] == r2["sigs"][SYM])
    details.update(arms_sig_count=(len(set(r1["sigs"].values())) if r1 else 0), arms_differ=arms_differ, determinism_ok=determinism_ok)

    # (8) STRUCTURAL gate fires on a near-matching pocket (each gene in ~1 pair -> learnable ~0).
    Xmatch = np.array([[i, i + 40] for i in range(40)], dtype=np.int64)  # perfect matching: every token appears once
    n_learn, avg_deg_match, _ = learnable_structure(Xmatch)
    structural_gate_ok = bool(n_learn == 0 and avg_deg_match <= 1.01)
    details.update(matching_learnable=n_learn, matching_avg_deg=round(avg_deg_match, 4), structural_gate_ok=structural_gate_ok)

    checks = {
        "fhrr_bind_homomorphism": homo_ok,
        "auc_ap_helpers_correct": auc_helpers_ok,
        "real_rawcount_parser_returns_symbols": parser_ok,
        "zdlfc_moesm3_parser_joins_by_symbol": zdlfc_ok,
        "pos_ctrl_best_constituent_detects": pos_ok,
        "scramble_collapses_to_chance": scr_ok,
        "degree_matched_neutralizes_confound": degmatch_ok,
        "arms_differ": arms_differ,
        "determinism_ok": determinism_ok,
        "structural_gate_fires_on_matching": structural_gate_ok,
    }
    for kk, vv in checks.items():
        if not vv:
            ok_all = False
    out = dict(passed=ok_all, checks=checks, details=details)
    print("[SELFTEST] %s" % json.dumps(out, default=float), flush=True)
    return ok_all, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run", action="store_true", help="explicit full run (default when no flag given)")
    args, _unknown = ap.parse_known_args()

    if args.self_test:
        ok, _ = self_test()
        sys.exit(0 if ok else 1)
    if args.smoke:
        m = run_measurement(SEEDS_SMOKE, run_mode="smoke")
        _write_metrics(m)
        _log("SMOKE " + m["verdict_msg"])
        return
    m = run_measurement(SEEDS_FULL, run_mode="full")
    _write_metrics(m)
    _log(m["verdict_msg"])


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            crash = dict(verdict="CELL_CRASHED", verdict_msg="%s: %s" % (type(e).__name__, str(e)[:400]),
                         summary="CELL_CRASHED", elapsed_s=0.0, anchor_name=ANCHOR_NAME,
                         traceback=traceback.format_exc()[:4000], ts_iso=datetime.now(timezone.utc).isoformat())
            os.makedirs(OUT_DIR, exist_ok=True)
            tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(crash, f, indent=2)
            os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
        except Exception:
            pass
        raise
