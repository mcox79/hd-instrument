"""FACTUAL_CORE_HUB_COMPOSE (v1): the two-tier foundation integration pilot -- does an LLM-GENERATED factual CORE tier
compose seamlessly with a CONJUNCTION MODULE via the SHARED canonical-ID (SGD systematic-ORF) HUB?

This is the SECOND half of the two-tier foundation. Module #1/#2 (ingested Costanzo/BioGRID) landed CHAIN_GRADE
(exp_crossmodule_interface_hub_heldout_v2: HUB novel MAP=0.83). This pilot builds the OTHER tier -- a small, crisp,
canonical-ID-anchored LLM-GENERATED fact set (experiments/_factual_core_yeast_gen_v1.py) -- and shows the SAME shared-hub
identity mechanism composes a cross-tier query over CORE-FACTS + a CONJUNCTION-MODULE edge, joined by exact ORF-string
identity. Design: notes/research_factual_core_tier_architecture_2026-07-15.md (section 5 linchpin).

HONEST FRAMING: this is a CONSTRUCTION-grade INTEGRATION pilot (does the LLM-generated core compose with the module via
the hub; is the join exact; is storage interference-free), NOT a capability-beats-frequency claim (that fight is
structurally capped and out of scope -- single-relation homophily-solvable). Core VALUE metrics reported = canonical-ID
coverage/density + glass-box auditability, NOT frequency-beating (design note section 1).

MECHANISM (VSA shared-hub-codebook; the VET'd exp_crossmodule_interface_hub mechanism, factual core swapped in for module-P):
  ONE random unit-modulus FHRR hub code h(orf) per canonical ORF id, shared READ-ONLY across both tiers (the "hub").
  TIER-CORE store  M_CORE = sum over core property-facts (gene g, property-value p) of bind(h(g), h_prop(p)).
  TIER-MODULE store M_MOD = sum over genetic edges (a,b) of bind(h(a), h(b)).
  Cross-tier CONJUNCTION query CT(P, Y) = "which gene z has core-property P (CORE tier) AND is a genetic partner of gene
    Y (MODULE tier)?"  gold A(P,Y) = genes_with_property(P) INTERSECT genetic_partners(Y), a PROPER subset of BOTH conjuncts.
    core readout : s_core(z) = Re< unbind(M_CORE, h_prop(P)), h(z) >   (genes with property P, cleaned vs the gene codebook)
    module readout: s_mod(z) = Re< unbind(M_MOD,  h(Y)),       h(z) >   (Y's genetic partners, cleaned vs the gene codebook)
    HUB conjunction = rank z by norm(s_core(z)) * norm(s_mod(z)); h(z) is the SAME hub code in BOTH readouts (identity join).

ARMS (retrieval, MAP higher=better on the true cross-tier answer set A(P,Y)):
  HUB        = shared hub codes + separate tier stores + identity-anchored product. WINNER hypothesis.
  CORE_ONLY  = rank by the CORE property readout alone (single-constraint reference ceiling: gold subset of genes_with_P).
  MODULE_ONLY= rank by the MODULE genetic readout alone (single-constraint reference ceiling: gold subset of partners(Y)).
  SCRAMBLE   = HUB but the CORE facts stored under a SCRAMBLED gene-identity permutation (storage identity broken). MUST-FAIL.
  NO_HUB     = CORE store built on an INDEPENDENT (non-shared) codebook + combined via random alignment (no shared identity
               registry -> the core readout cannot be re-identified against the module readout). MUST-FAIL.
  RANDOM     = random candidate scores -> the pure-chance MAP floor for the variable-size answer sets.
  Because gold A(P,Y) is a PROPER subset of BOTH conjuncts, any arm that keeps ONE intact tuned tier scores ABOVE the RANDOM
  floor by construction. So the honest null for the identity-broken arms (SCRAMBLE/NO_HUB) is the single-constraint CEILING
  max(CORE_ONLY,MODULE_ONLY), NOT the random floor. HUB must beat that ceiling (genuine conjunction from the shared-identity
  bridge); SCRAMBLE/NO_HUB must NOT (broken bridge => no conjunction gain over one tier alone).

INTERFERENCE-FREE (design note HARD-PASS iii / P3): M_MOD is a SEPARATE tensor from M_CORE -> adding the LLM-generated core
  facts CANNOT touch the module store. Asserted EXACTLY: sha256(M_MOD) is bit-identical with vs without the core tier present,
  AND the module's OWN held-out genetic-partner MAP is unchanged (delta <= 1e-9). The strongest possible additive-hub proof.

PRE-REGISTERED BANDS (fixed BEFORE running; see preregs/2026-07-15_factual_core_hub_compose_v1.md):
  HARD_PASS_FACTUAL_CORE_COMPOSES_VIA_HUB (multi-seed mean over hub-codebook seeds):
    JOIN clean (join_precision >= 0.99 AND fuzzy_gain_frac <= 0.05 AND n_shared_orfs >= MIN_SHARED) AND
    discriminator fires (n_queries >= MIN_QUERIES with PROPER-subset gold) AND
    HUB_MAP >= HP_HUB_ABS AND HUB - max(CORE_ONLY,MODULE_ONLY) >= HP_MARGIN_ABS (genuine conjunction) AND
    HUB - max(SCRAMBLE,NO_HUB) >= HP_MARGIN_ABS AND SCRAMBLE,NO_HUB <= single_ceiling + MUSTFAIL_CEIL_TOL (identity needed) AND
    interference-free (module MAP delta <= 1e-9 AND module store hash unchanged) AND arms differ AND determinism.
  HARD_FAIL_JOIN_LOSSY            : join_precision < 0.99 OR fuzzy_gain_frac > 0.05 OR n_shared_orfs < MIN_SHARED.
  HARD_FAIL_NO_COMPOSITION        : JOIN clean but HUB does not beat the single-constraint ceiling by the margin.
  HARD_FAIL_IDENTITY_NOT_NEEDED   : SCRAMBLE or NO_HUB is NOT >= HP_MARGIN_ABS below HUB (conjunction without identity ->
                                    the shared-hub claim is vacuous).
  HARD_FAIL_INTERFERENCE          : module MAP changes OR module store hash changes with the core tier present.
  MIDDLE_BAND_LOW_POWER           : n_queries < MIN_QUERIES with proper-subset gold.

Compute architecture: (b) sequential-CPU with justification -- the VSA core (bind = complex64 elementwise multiply, unbind,
  cleanup matmul against the [V,N] gene codebook) is BATCHED over all queries as single torch complex64 matmuls (no python
  loop over independent query points); V=30 genes, N=16384, a few dozen queries -> seconds on CPU; GPU yields nothing at this
  size. device=cpu (runner passes no argv). Storage: BUNDLED-ASSOCIATIVE per tier (each tier store = a superposition of bound
  facts/edges); single-hop-per-tier unbind then an identity-anchored intersection (NOT a depth>=2 chain -> the sharded-vs-
  bundled chain-grade physics law does not apply). Determinism: FIXED int seeds + sorted(set()) vocab + deterministic
  permutations via np.random.default_rng(seed); NO builtin-hash seeding, NO list-of-set dedupe (PROT-023). ASCII-only; no bare
  except; SystemExit before Exception; atomic tmp+os.replace. Default invocation (no flag) = FULL run to completion.
  progress_logging: print_flush_true (timeout < 1800 so the >=1800 mandate does not bind, but prints flush anyway).
"""

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF; float-hash of per-arm score vectors on the planted arena must differ).
# - final_metrics_atomicity: tmp_replace (single-shot; os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: retrieval MAP has no closed-form CRLB; the discriminator floor is the empirical RANDOM-arm MAP on the SAME
#     variable-size answer sets, and the planted-arena full-N self-test certifies the HUB-vs-ceiling gap at full N.
# - baseline_in_band: CORE_ONLY/MODULE_ONLY single-ceiling is bounded by |gold|/|conjunct| < 1 (cannot saturate);
#     RANDOM bounds the chance floor. Discriminator fires structurally because gold is a PROPER subset of both conjuncts.
# - discriminator survives scale (option A + C): scale is FIXED (small curated pilot; smoke IS full scale). The self-test
#     ALSO runs the FULL VSA arms at N_DIM on a PLANTED arena and asserts HUB - {CORE_ONLY,MODULE_ONLY,SCRAMBLE,NO_HUB} >=
#     PLANT_MARGIN and interference delta == 0 at full N BEFORE the curated population is trusted.
# - HARD_PASS strictly above floor: HUB_MAP >= 0.30 AND margin >= 0.15 (not a >= floor touch).
# - HP_SCOPE: HARD_PASS gates apply to HUB vs max(CORE_ONLY,MODULE_ONLY,SCRAMBLE,NO_HUB); RANDOM = chance-floor contrast.
# - cardinality_ok: n_seeds fixed; verdict counts per-seed MAP lengths == n_seeds for every arm.
# - per-unit failure-class instrumentation: build/gen failures -> explicit CELL_CRASHED metrics (no bare except).
# - calibration_check: adaptive_with_discriminator_gate (the must-fail null is the MEASURED single-constraint ceiling
#     max(CORE_ONLY,MODULE_ONLY) on the real answer sets, NOT the pure-random floor; the proper-subset query filter is the
#     discriminator-still-fires verification; the self-test asserts HUB beats the ceiling on a planted arena first).
# - all numbers in comments tagged CITED@ / THEORETICAL@ / MEASURED@ (real numbers written to metrics.json by this run).
# - real_code_path: self-test builds the REAL VSA arms via hd_bind/hd_unbind on complex64 at full N on a planted arena.
# - substrate_signature: hd_bind/hd_unbind bound against the live hdlab.binding signatures in self-test.
# - deterministic_seeding: FIXED int seeds; sorted(set()) vocab; np.random.default_rng(seed); no hash()/list(set()).
# - start_marker_written + crash_diagnostic_present; heartbeat exempt (single-shot, wall < 60s).

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

from hdlab.binding import bind as hd_bind      # noqa: E402  # REAL substrate bind (complex64 FHRR elementwise multiply)
from hdlab.binding import unbind as hd_unbind  # noqa: E402  # REAL substrate unbind (complex64: c * conj(b))
from experiments import _factual_core_yeast_gen_v1 as gen  # noqa: E402  # the LLM-generated core + module structure

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (ValueError, OSError):
        pass

ANCHOR_NAME = "factual_core_hub_compose_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)

# ---- fixed controls ----
N_DIM = 16384                # FHRR complex64 hub dimensionality (full N; also the self-test discriminator-preview N)
SEEDS_FULL = (7, 13, 17, 23, 29)   # hub-codebook seeds (the only randomness); multi-seed to avoid single-seed luck
SEEDS_SMOKE = (7, 13)

# ---- pre-registered bands (fixed BEFORE running) ----
JOIN_PRECISION_MIN = 0.99    # fraction of core ORF ids that are well-formed canonical format AND exact-match module keys
FUZZY_GAIN_MAX = 0.05        # extra case/whitespace fuzzy matches over exact equality, as frac of exact overlap
MIN_SHARED = 25              # >= this many exact-shared ORFs between the two tiers else HARD_FAIL_JOIN_LOSSY
MIN_QUERIES = 30             # >= this many cross-tier queries with PROPER-subset gold else MIDDLE_BAND_LOW_POWER
HP_HUB_ABS = 0.30            # HUB MAP must be materially above chance
HP_MARGIN_ABS = 0.15         # HUB_MAP - max(CORE_ONLY,MODULE_ONLY) >= this AND HUB - max(SCRAMBLE,NO_HUB) >= this
MUSTFAIL_CEIL_TOL = 0.05     # identity-broken arms must NOT exceed the single-constraint ceiling by more than this
INTERF_TOL = 1e-9            # module held-out MAP must be unchanged (bit-identical store => exactly 0) within this
PLANT_MARGIN = 0.15          # self-test planted-arena: HUB - {CORE_ONLY,MODULE_ONLY,SCRAMBLE,NO_HUB} >= this at full N

# ---- density-audit floor (design note section 3; REPORTED directionally, NOT a hard gate for this construction pilot) ----
DENSITY_FLOOR_ATTRIBUTES = 13
DENSITY_FLOOR_CATEGORIES = 3
DENSITY_FLOOR_EXPOSURES = 6

# ---- arms ----
HUB = "HUB"; CORE_ONLY = "CORE_ONLY"; MODULE_ONLY = "MODULE_ONLY"
SCRAMBLE = "SCRAMBLE"; NO_HUB = "NO_HUB"; RANDOM = "RANDOM"
ARM_NAMES = [HUB, CORE_ONLY, MODULE_ONLY, SCRAMBLE, NO_HUB, RANDOM]


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    try:
        return ("%.4f" % x) if (x == x) else "nan"
    except (TypeError, ValueError):
        return "nan"


def _sig_c(t):
    """Stable hash of a complex64 tensor (real+imag rounded) -- for the interference bit-identical assertion."""
    a = t.detach().cpu().to(torch.complex64).numpy()
    b = np.round(np.stack([a.real, a.imag]), 6).tobytes()
    return hashlib.sha256(b).hexdigest()[:16]


def _sig_f(arr):
    return hashlib.sha256(np.round(np.asarray(arr, dtype=np.float64), 6).tobytes()).hexdigest()[:16]


def _write_start_marker(expected_n_units, run_mode):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units)
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(OUT_DIR, "_start_marker.json"))


def _write_metrics(metrics):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))


def _write_crash_metrics(exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg="%s: %s" % (type(exc).__name__, str(exc)[:500]),
                summary="CELL_CRASHED: %s" % type(exc).__name__, elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _write_metrics(diag)


# ===========================================================================
# VSA hub codebook + tier stores (REAL substrate bind/unbind; batched complex64)
# ===========================================================================

def _codebook(n_items, n_dim, seed):
    """n_items unit-modulus complex64 random FHRR phasor codes [n_items, n_dim]."""
    g = torch.Generator().manual_seed(int(seed))
    ph = (2.0 * math.pi) * torch.rand(n_items, n_dim, generator=g)
    return torch.polar(torch.ones(n_items, n_dim), ph).to(torch.complex64)


def _build_pair_store(pairs_idx, code_a, code_b, n_dim):
    """M = sum over pairs (i,j) of bind(code_a[i], code_b[j]) using the REAL substrate bind (complex64 mul)."""
    if not pairs_idx:
        return torch.zeros(n_dim, dtype=torch.complex64)
    idx = torch.tensor(pairs_idx, dtype=torch.long)
    bound = hd_bind(code_a[idx[:, 0]], code_b[idx[:, 1]])  # [E, N]
    return bound.sum(0)


def _cleanup_scores(store, key_codes, gene_codebook):
    """s(q, z) = Re< unbind(store, key_codes[q]), gene_codebook[z] > -> [Q, V]. Batched; REAL substrate unbind."""
    q = key_codes.shape[0]
    b = hd_unbind(store.unsqueeze(0).expand(q, -1), key_codes)  # [Q, N] = store * conj(key)
    return (b @ gene_codebook.conj().t()).real                 # [Q, V]


def _norm_rows(scores):
    """Row-wise min-max to [0,1] (scale-free conjunction combine). Degenerate rows -> all zeros."""
    lo = scores.min(axis=1, keepdims=True)
    hi = scores.max(axis=1, keepdims=True)
    rng = hi - lo
    out = np.where(rng > 1e-12, (scores - lo) / np.where(rng > 1e-12, rng, 1.0), 0.0)
    return out


def _average_precision(scores_row, gold_set, exclude):
    s = scores_row.copy()
    for e in exclude:
        s[e] = -1e30
    order = np.argsort(-s)
    hits = 0; sump = 0.0; ng = len(gold_set)
    if ng == 0:
        return float("nan")
    for rank, z in enumerate(order, 1):
        if z in gold_set:
            hits += 1; sump += hits / rank
            if hits == ng:
                break
    return sump / ng


def _map_over(arm_scores, queries):
    """Mean average-precision over queries. queries: list of (prop_key_idx, y_idx, gold_tuple, exclude_tuple)."""
    aps = []
    for qi, (_p, _y, gold, excl) in enumerate(queries):
        ap = _average_precision(arm_scores[qi], set(gold), excl)
        if ap == ap:
            aps.append(ap)
    return float(np.mean(aps)) if aps else float("nan")


# ===========================================================================
# Build a joined arena (gene vocab, property sets, genetic partners, cross-tier queries)
# ===========================================================================

def build_arena(genes, core_facts, genetic_edges):
    """genes: sorted ORF list. core_facts: (orf, rel, value, cat, xchk). genetic_edges: (orf_a, orf_b) set.
    Returns arena dict with int-id vocab, property->gene-set maps, genetic partner sets, and the property-value codebook keys."""
    gid = {o: i for i, o in enumerate(genes)}
    v = len(genes)
    # CORE property-value -> set(gene int-ids), restricted to conjunction property relations
    prop_to_genes = defaultdict(set)
    core_pairs = []  # (gene_id, prop_id) for the CORE store; prop ids indexed in prop_vocab
    prop_vocab = sorted(set(("%s=%s" % (rel, val)) for (orf, rel, val, _c, _x) in core_facts
                            if rel in gen.CONJUNCTION_PROPERTY_RELATIONS))
    pid = {p: i for i, p in enumerate(prop_vocab)}
    for (orf, rel, val, _c, _x) in core_facts:
        if rel not in gen.CONJUNCTION_PROPERTY_RELATIONS or orf not in gid:
            continue
        pkey = "%s=%s" % (rel, val)
        prop_to_genes[pkey].add(gid[orf])
        core_pairs.append((gid[orf], pid[pkey]))
    # MODULE genetic partners
    gen_partners = defaultdict(set)
    gen_pairs = []
    for (a, b) in genetic_edges:
        if a in gid and b in gid and a != b:
            gen_partners[gid[a]].add(gid[b]); gen_partners[gid[b]].add(gid[a])
            gen_pairs.append((gid[a], gid[b]))
    return dict(genes=genes, gid=gid, v=v, prop_vocab=prop_vocab, pid=pid,
                prop_to_genes={k: sorted(s) for k, s in prop_to_genes.items()},
                gen_partners={k: sorted(s) for k, s in gen_partners.items()},
                core_pairs=sorted(core_pairs), gen_pairs=sorted(set((min(a, b), max(a, b)) for (a, b) in gen_pairs)))


def build_queries(arena):
    """Cross-tier queries CT(P, Y): gold = genes_with(P) INTERSECT partners(Y), a PROPER subset of BOTH conjuncts.
    Returns list of (prop_key, y_id, gold_tuple, exclude_tuple). Deterministic (sorted)."""
    queries = []
    prop_to_genes = arena["prop_to_genes"]; gen_partners = arena["gen_partners"]
    for pkey in sorted(prop_to_genes.keys()):
        A = set(prop_to_genes[pkey])
        if len(A) < 2:
            continue
        for y in sorted(gen_partners.keys()):
            B = set(gen_partners[y])
            if len(B) < 2:
                continue
            gold = (A & B) - {y}
            if not gold:
                continue
            # require PROPER subset of BOTH conjuncts so the single-constraint ceiling is < 1 (discriminator fires)
            if len(gold) >= len(A) or len(gold) >= len(B):
                continue
            queries.append((pkey, y, tuple(sorted(gold)), (y,)))
    return queries


# ===========================================================================
# Run all arms on an arena for one hub-codebook seed
# ===========================================================================

def run_seed(arena, queries, seed, n_dim):
    """Build tier stores + score every arm for one hub-codebook seed. Returns (maps_dict, per_arm_score_sig, module_store_sig)."""
    v = arena["v"]; n_prop = len(arena["prop_vocab"])
    rng = np.random.default_rng(seed)
    gene_cb = _codebook(v, n_dim, seed)                      # shared hub gene codebook
    prop_cb = _codebook(n_prop, n_dim, seed + 100003)       # property-value codebook (distinct from gene codes)
    gene_cb_indep = _codebook(v, n_dim, seed + 200003)      # NO_HUB: independent (non-shared) gene codebook

    # tier stores
    M_core = _build_pair_store(arena["core_pairs"], gene_cb, prop_cb, n_dim)             # shared-identity CORE
    # SCRAMBLE: CORE facts stored under a permuted gene identity (storage anchor broken)
    perm = rng.permutation(v)
    core_pairs_scr = [(int(perm[g]), p) for (g, p) in arena["core_pairs"]]
    M_core_scr = _build_pair_store(core_pairs_scr, gene_cb, prop_cb, n_dim)
    # NO_HUB: CORE facts stored on an INDEPENDENT gene codebook (no shared identity registry)
    M_core_indep = _build_pair_store(arena["core_pairs"], gene_cb_indep, prop_cb, n_dim)
    # MODULE store (symmetric genetic edges): store both directions so unbind(Y) recovers partners
    mod_pairs = arena["gen_pairs"] + [(b, a) for (a, b) in arena["gen_pairs"]]
    M_mod = _build_pair_store(mod_pairs, gene_cb, gene_cb, n_dim)
    module_store_sig = _sig_c(M_mod)

    # query key codes
    prop_keys = torch.stack([prop_cb[arena["pid"][pk]] for (pk, _y, _g, _e) in queries])  # [Q, N]
    y_keys = torch.stack([gene_cb[y] for (_pk, y, _g, _e) in queries])                    # [Q, N]

    s_core = _cleanup_scores(M_core, prop_keys, gene_cb).cpu().numpy()          # [Q, V]
    s_core_scr = _cleanup_scores(M_core_scr, prop_keys, gene_cb).cpu().numpy()
    s_core_indep = _cleanup_scores(M_core_indep, prop_keys, gene_cb_indep).cpu().numpy()
    s_mod = _cleanup_scores(M_mod, y_keys, gene_cb).cpu().numpy()

    nc = _norm_rows(s_core); ncs = _norm_rows(s_core_scr); nci = _norm_rows(s_core_indep); nm = _norm_rows(s_mod)
    # NO_HUB: no shared registry -> core readout aligned to the module gene index by a RANDOM permutation (per query fixed)
    align = rng.permutation(v)
    nci_aligned = nci[:, align]
    rnd = rng.random((len(queries), v))

    arm_scores = {
        HUB: nc * nm,
        CORE_ONLY: nc,
        MODULE_ONLY: nm,
        SCRAMBLE: ncs * nm,
        NO_HUB: nci_aligned * nm,
        RANDOM: rnd,
    }
    maps = {arm: _map_over(arm_scores[arm], queries) for arm in ARM_NAMES}
    score_sig = {arm: _sig_f(arm_scores[arm]) for arm in ARM_NAMES}
    # interference probe: module held-out MAP (rank partners(Y) directly) -- recomputed WITH the core tier present.
    # Since M_mod is a separate tensor untouched by any core build, this MAP is a function of M_mod alone.
    mod_partner_map = _module_partner_map(arena, queries, s_mod)
    return maps, score_sig, module_store_sig, mod_partner_map


def _module_partner_map(arena, queries, s_mod):
    """Module's OWN held-out genetic-partner retrieval MAP (gold = full partners(Y)); used for the interference check."""
    aps = []
    for qi, (_pk, y, _gold, _excl) in enumerate(queries):
        partners = set(arena["gen_partners"].get(y, []))
        ap = _average_precision(s_mod[qi], partners, (y,))
        if ap == ap:
            aps.append(ap)
    return float(np.mean(aps)) if aps else float("nan")


def _mean_over_seeds(per_seed_maps):
    out = {}
    for arm in ARM_NAMES:
        vals = [m[arm] for m in per_seed_maps if m[arm] == m[arm]]
        out[arm] = float(np.mean(vals)) if vals else float("nan")
    return out


# ===========================================================================
# Density / coverage audit (design note section 3; REPORTED directionally)
# ===========================================================================

def density_audit(genes, core_facts, genetic_edges):
    """Per-gene attributes (# distinct (rel,value) facts) / categories (# distinct relation-categories) / exposures
    (# distinct provenance sources: core-batch + module). Reports the median + floor-attainment fractions."""
    attrs = defaultdict(set); cats = defaultdict(set); expo = defaultdict(set)
    gset = set(genes)
    for (orf, rel, val, cat, _x) in core_facts:
        if orf in gset:
            attrs[orf].add((rel, val)); cats[orf].add(cat); expo[orf].add("core_gen_batch_%s" % gen.GEN_PROMPT_TEMPLATE_VERSION)
    partners = defaultdict(set)
    for (a, b) in genetic_edges:
        partners[a].add(b); partners[b].add(a)
    for orf in genes:
        for p in partners.get(orf, ()):  # each genetic partner = a measured-interaction attribute
            attrs[orf].add(("genetic_interaction", p)); cats[orf].add("measured_interaction"); expo[orf].add("module_genetic")
    n = len(genes)
    a_counts = [len(attrs[o]) for o in genes]; c_counts = [len(cats[o]) for o in genes]; e_counts = [len(expo[o]) for o in genes]
    return dict(
        median_attributes=float(np.median(a_counts)), median_categories=float(np.median(c_counts)),
        median_exposures=float(np.median(e_counts)),
        frac_ge_attr_floor=float(np.mean([c >= DENSITY_FLOOR_ATTRIBUTES for c in a_counts])),
        frac_ge_cat_floor=float(np.mean([c >= DENSITY_FLOOR_CATEGORIES for c in c_counts])),
        frac_ge_expo_floor=float(np.mean([c >= DENSITY_FLOOR_EXPOSURES for c in e_counts])),
        floor=dict(attributes=DENSITY_FLOOR_ATTRIBUTES, categories=DENSITY_FLOOR_CATEGORIES, exposures=DENSITY_FLOOR_EXPOSURES),
        n_genes=n)


# ===========================================================================
# JOIN precision (exact canonical-ID join between the CORE tier and the MODULE tier)
# ===========================================================================

def compute_join(core_orfs, module_orfs):
    """Exact string-equality overlap + well-formedness + a fuzzy-normalized overlap (to prove the exact join is not lossy)."""
    core_set = set(core_orfs); mod_set = set(module_orfs)
    wellformed = [o for o in core_set if gen.is_wellformed_orf(o)]
    join_precision = (len(wellformed) / len(core_set)) if core_set else 0.0
    exact = core_set & mod_set

    def _fuzzy(o):
        return str(o).strip().upper().replace("-", "").replace("_", "")
    fmap_c = defaultdict(set); fmap_m = defaultdict(set)
    for o in core_set:
        fmap_c[_fuzzy(o)].add(o)
    for o in mod_set:
        fmap_m[_fuzzy(o)].add(o)
    fuzzy_extra = 0
    for k in set(fmap_c) & set(fmap_m):
        for oc in fmap_c[k]:
            if oc in fmap_m[k]:
                continue
            fuzzy_extra += 1
    n_exact = len(exact)
    fuzzy_gain_frac = (fuzzy_extra / n_exact) if n_exact else float("inf")
    return dict(join_precision=join_precision, n_shared_orfs=n_exact, fuzzy_extra=fuzzy_extra,
                fuzzy_gain_frac=fuzzy_gain_frac, n_core_orfs=len(core_set), n_module_orfs=len(mod_set),
                n_wellformed_core=len(wellformed))


# ===========================================================================
# SELF-TEST: planted arena, full-N discriminator preview + real-code-path + signature + nondeterminism
# ===========================================================================

def _planted_arena():
    """A tiny PLANTED two-tier arena with GUARANTEED proper-subset golds (discriminator-fires preview at full N)."""
    genes = ["Y%s001W" % c for c in "ABCDEFGHIJ"]  # 10 well-formed synthetic ORF ids
    # CORE: two complexes of 5 each
    core = []
    for i, o in enumerate(genes):
        cx = "CPLX:C%d" % (i // 5)
        core.append((o, "part_of_complex", cx, "compositional", "knowledge_based"))
    # MODULE: cross-complex genetic edges so partner sets span both complexes -> proper-subset intersections
    edges = set()
    for i in range(len(genes)):
        for s in (2, 4, 7):
            j = (i + s) % len(genes)
            if j != i:
                a, b = genes[i], genes[j]
                edges.add((a, b) if a < b else (b, a))
    return genes, core, sorted(edges)


def self_test():
    exercised = set()
    ok = True

    # F.1 real_code_path + F.2 signature: exercise the REAL bind/unbind at full N on the planted arena.
    from experiments._validity_preflight import run_validity_preflight  # noqa: E402
    genes, core, edges = _planted_arena()
    arena = build_arena(sorted(genes), core, edges)
    queries = build_queries(arena)
    assert len(queries) >= 5, "planted arena produced too few proper-subset queries: %d" % len(queries)
    maps, score_sig, mod_sig, mod_map = run_seed(arena, queries, seed=7, n_dim=N_DIM)
    exercised.add("hd_bind"); exercised.add("hd_unbind")

    single_ceiling = max(maps[CORE_ONLY], maps[MODULE_ONLY])
    _log("SELFTEST planted maps: HUB=%s CORE_ONLY=%s MODULE_ONLY=%s SCRAMBLE=%s NO_HUB=%s RANDOM=%s (ceiling=%s)" % (
        _fmt(maps[HUB]), _fmt(maps[CORE_ONLY]), _fmt(maps[MODULE_ONLY]), _fmt(maps[SCRAMBLE]),
        _fmt(maps[NO_HUB]), _fmt(maps[RANDOM]), _fmt(single_ceiling)))
    # discriminator survives scale (full N): HUB beats every non-mechanism arm by the plant margin
    assert maps[HUB] - single_ceiling >= PLANT_MARGIN, "HUB - single_ceiling %.3f < %.2f" % (maps[HUB] - single_ceiling, PLANT_MARGIN)
    assert maps[HUB] - maps[SCRAMBLE] >= PLANT_MARGIN, "HUB - SCRAMBLE %.3f < %.2f" % (maps[HUB] - maps[SCRAMBLE], PLANT_MARGIN)
    assert maps[HUB] - maps[NO_HUB] >= PLANT_MARGIN, "HUB - NO_HUB %.3f < %.2f" % (maps[HUB] - maps[NO_HUB], PLANT_MARGIN)
    assert maps[HUB] - maps[RANDOM] >= PLANT_MARGIN, "HUB - RANDOM %.3f < %.2f" % (maps[HUB] - maps[RANDOM], PLANT_MARGIN)
    # identity-broken arms yield no conjunction gain over one intact tier
    assert maps[SCRAMBLE] <= single_ceiling + MUSTFAIL_CEIL_TOL, "SCRAMBLE %.3f > ceiling+tol" % maps[SCRAMBLE]
    assert maps[NO_HUB] <= single_ceiling + MUSTFAIL_CEIL_TOL, "NO_HUB %.3f > ceiling+tol" % maps[NO_HUB]

    # META_RULE_AF: arms must differ (bit-hash of per-arm score matrices)
    sigs = list(score_sig.values())
    assert len(set(sigs)) == len(sigs), "META_RULE_AF: two arms produced bit-identical score matrices: %s" % score_sig

    # interference-free: a SECOND seed's module store is a function of M_mod alone; building the core tier does not touch it.
    # Assert the module store hash is INDEPENDENT of whether the core pairs were built (rebuild module-only vs full).
    v = arena["v"]
    gene_cb = _codebook(v, N_DIM, 7)
    mod_pairs = arena["gen_pairs"] + [(b, a) for (a, b) in arena["gen_pairs"]]
    M_mod_only = _build_pair_store(mod_pairs, gene_cb, gene_cb, N_DIM)
    assert _sig_c(M_mod_only) == mod_sig, "interference: module store hash changed between module-only and full build"

    # determinism: same seed -> same maps
    maps2, _s2, _m2, _mm2 = run_seed(arena, queries, seed=7, n_dim=N_DIM)
    for arm in ARM_NAMES:
        if maps[arm] == maps[arm]:
            assert abs(maps[arm] - maps2[arm]) < 1e-9, "determinism: %s changed across identical-seed runs" % arm

    # F.1 real_code_path + F.2 signature binding (declared checks)
    checks_ok = run_validity_preflight([
        {"kind": "real_code_path", "full_substrate_entrypoints": ["hd_bind", "hd_unbind"], "exercised_entrypoints": exercised},
        {"kind": "substrate_signature", "callable_obj": hd_bind, "kwargs": {"a": None, "b": None}, "callable_name": "hd_bind"},
        {"kind": "substrate_signature", "callable_obj": hd_unbind, "kwargs": {"c": None, "b": None}, "callable_name": "hd_unbind"},
    ], run_mode="self_test")
    # F.5 nondeterminism source scan (static; the load-bearing enforcement is queue_add's automatic scan on ship)
    from experiments._validity_preflight import assert_no_nondeterministic_seeding  # noqa: E402
    with open(_THIS, "r", encoding="utf-8") as f:
        src = f.read()
    assert_no_nondeterministic_seeding(src, run_mode="self_test")
    ok = ok and checks_ok

    _log("SELFTEST PASS (planted discriminator fires at full N; arms differ; interference-free; deterministic)")
    return ok


# ===========================================================================
# FULL run on the LLM-generated curated population
# ===========================================================================

def run_measurement(seeds):
    core_facts = gen.generate_core_facts()
    genetic_edges = set(gen.generate_genetic_edges())
    core_orfs = sorted(set(orf for (orf, _r, _v, _c, _x) in core_facts))
    module_orfs = gen.module_orfs()
    genes = sorted(set(core_orfs) & set(module_orfs))

    join = compute_join(core_orfs, module_orfs)
    arena = build_arena(genes, core_facts, genetic_edges)
    queries = build_queries(arena)
    n_queries = len(queries)
    dens = density_audit(genes, core_facts, sorted(genetic_edges))

    per_seed = []
    module_sigs = set(); mod_maps = []
    for sd in seeds:
        maps, _ss, mod_sig, mod_map = run_seed(arena, queries, sd, N_DIM)
        per_seed.append(maps); module_sigs.add(mod_sig); mod_maps.append(mod_map)
    mean_maps = _mean_over_seeds(per_seed)

    # interference-free: rebuild the module store WITHOUT ever constructing the core tier and confirm the module partner MAP
    # is bit-identical (it is a function of M_mod alone; the core stores are separate tensors).
    interf_deltas = []
    module_only_sigs = set()
    for sd in seeds:
        v = arena["v"]
        gene_cb = _codebook(v, N_DIM, sd)
        mod_pairs = arena["gen_pairs"] + [(b, a) for (a, b) in arena["gen_pairs"]]
        M_mod_only = _build_pair_store(mod_pairs, gene_cb, gene_cb, N_DIM)
        module_only_sigs.add(_sig_c(M_mod_only))
        key = torch.stack([gene_cb[y] for (_pk, y, _g, _e) in queries])
        s_mod_only = _cleanup_scores(M_mod_only, key, gene_cb).cpu().numpy()
        mm_only = _module_partner_map(arena, queries, s_mod_only)
        # delta vs the WITH-core-tier module map for the same seed
        with_core = mod_maps[list(seeds).index(sd)]
        interf_deltas.append(abs(mm_only - with_core))
    interf_delta = float(max(interf_deltas)) if interf_deltas else 0.0
    interf_store_identical = bool(module_sigs == module_only_sigs and len(module_sigs) == len(seeds))

    return dict(core_facts=core_facts, genetic_edges=sorted(genetic_edges), genes=genes, join=join, arena=arena,
                queries=queries, n_queries=n_queries, per_seed=per_seed, mean_maps=mean_maps, density=dens,
                interf_delta=interf_delta, interf_store_identical=interf_store_identical, seeds=list(seeds))


def verdict_from(res):
    m = res["mean_maps"]; join = res["join"]; nq = res["n_queries"]
    single_ceiling = max(m[CORE_ONLY], m[MODULE_ONLY])
    broken = max(m[SCRAMBLE], m[NO_HUB])

    join_ok = (join["join_precision"] >= JOIN_PRECISION_MIN and join["fuzzy_gain_frac"] <= FUZZY_GAIN_MAX
               and join["n_shared_orfs"] >= MIN_SHARED)
    power_ok = nq >= MIN_QUERIES
    hub_above = m[HUB] >= HP_HUB_ABS
    beats_ceiling = (m[HUB] - single_ceiling) >= HP_MARGIN_ABS
    beats_broken = (m[HUB] - broken) >= HP_MARGIN_ABS
    identity_needed = (m[SCRAMBLE] <= single_ceiling + MUSTFAIL_CEIL_TOL and m[NO_HUB] <= single_ceiling + MUSTFAIL_CEIL_TOL
                       and beats_broken)
    interf_ok = res["interf_delta"] <= INTERF_TOL and res["interf_store_identical"]

    # arms differ + determinism from seed 0 signatures
    arena, queries = res["arena"], res["queries"]
    _mm, score_sig0, _ms, _mp = run_seed(arena, queries, res["seeds"][0], N_DIM)
    arms_differ = len(set(score_sig0.values())) == len(score_sig0)
    _mm2, score_sig0b, _ms2, _mp2 = run_seed(arena, queries, res["seeds"][0], N_DIM)
    determinism_ok = score_sig0 == score_sig0b

    if not join_ok:
        v = "HARD_FAIL_JOIN_LOSSY"
    elif not power_ok:
        v = "MIDDLE_BAND_LOW_POWER"
    elif not interf_ok:
        v = "HARD_FAIL_INTERFERENCE"
    elif not (hub_above and beats_ceiling):
        v = "HARD_FAIL_NO_COMPOSITION"
    elif not identity_needed:
        v = "HARD_FAIL_IDENTITY_NOT_NEEDED"
    elif not (arms_differ and determinism_ok):
        v = "HARD_FAIL_ARMS_OR_DETERMINISM"
    else:
        v = "HARD_PASS_FACTUAL_CORE_COMPOSES_VIA_HUB"

    gates = dict(join_ok=join_ok, power_ok=power_ok, hub_above=hub_above, beats_ceiling=beats_ceiling,
                 beats_broken=beats_broken, identity_needed=identity_needed, interf_ok=interf_ok,
                 arms_differ=arms_differ, determinism_ok=determinism_ok, single_ceiling=single_ceiling,
                 broken_max=broken)
    return v, gates


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _unknown = ap.parse_known_args()

    if args.self_test:
        _write_start_marker(expected_n_units=1, run_mode="self_test")
        ok = self_test()
        if not ok:
            _log("SELFTEST validity preflight reported a failure")
            sys.exit(1)
        sys.exit(0)

    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL
    run_mode = "smoke" if args.smoke else "full"
    _write_start_marker(expected_n_units=len(seeds), run_mode=run_mode)
    t0 = time.perf_counter()
    res = run_measurement(seeds)
    v, gates = verdict_from(res)
    elapsed = time.perf_counter() - t0
    m = res["mean_maps"]; join = res["join"]; dens = res["density"]

    msg = ("%s || JOIN precision=%s n_shared=%d fuzzy_gain=%s | n_queries=%d (power>=%d:%s) | "
           "HUB=%s CORE_ONLY=%s MODULE_ONLY=%s single_ceiling=%s SCRAMBLE=%s NO_HUB=%s RANDOM=%s | "
           "beats_ceiling(>=%.2f)=%s beats_broken=%s identity_needed=%s | interf_delta=%.2e store_identical=%s | "
           "arms_differ=%s determ=%s | density med_attr=%s med_cat=%s med_expo=%s (floor 13/3/6)") % (
        v, _fmt(join["join_precision"]), join["n_shared_orfs"], _fmt(join["fuzzy_gain_frac"]), res["n_queries"], MIN_QUERIES,
        gates["power_ok"], _fmt(m[HUB]), _fmt(m[CORE_ONLY]), _fmt(m[MODULE_ONLY]), _fmt(gates["single_ceiling"]),
        _fmt(m[SCRAMBLE]), _fmt(m[NO_HUB]), _fmt(m[RANDOM]), HP_MARGIN_ABS, gates["beats_ceiling"], gates["beats_broken"],
        gates["identity_needed"], res["interf_delta"], gates["interf_ok"], gates["arms_differ"], gates["determinism_ok"],
        _fmt(dens["median_attributes"]), _fmt(dens["median_categories"]), _fmt(dens["median_exposures"]))
    _log(msg)

    metrics = dict(
        run_mode=run_mode, anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        elapsed_s=round(elapsed, 2), verdict=v, verdict_msg=msg, summary=msg[:240],
        seeds=res["seeds"], n_genes=len(res["genes"]), n_queries=res["n_queries"],
        n_core_facts=len(res["core_facts"]), n_genetic_edges=len(res["genetic_edges"]),
        bands=dict(JOIN_PRECISION_MIN=JOIN_PRECISION_MIN, FUZZY_GAIN_MAX=FUZZY_GAIN_MAX, MIN_SHARED=MIN_SHARED,
                   MIN_QUERIES=MIN_QUERIES, HP_HUB_ABS=HP_HUB_ABS, HP_MARGIN_ABS=HP_MARGIN_ABS,
                   MUSTFAIL_CEIL_TOL=MUSTFAIL_CEIL_TOL, INTERF_TOL=INTERF_TOL, N_DIM=N_DIM),
        join=res["join"], maps=res["mean_maps"], per_seed_maps=res["per_seed"], gates=gates,
        interference=dict(delta=res["interf_delta"], store_identical=res["interf_store_identical"], tol=INTERF_TOL),
        density=res["density"], provenance=gen.provenance())
    _write_metrics(metrics)
    _log("wrote %s" % os.path.join(OUT_DIR, "metrics.json"))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(e)
        raise
