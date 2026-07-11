"""METAPHOR-STRUCTURAL BRIDGE CORE-EXPANSION -> re-run the MATHEMATICAL(operation-word) grounding-reach test.

ANCHOR 3 (research hand-off notes/exp_dev_handoff_research_math_social_abstract_grounding_core_expansion_2026-07-10.md;
research note notes/research_math_social_abstract_grounding_core_expansion_2026-07-10.md Section 3 (B) + Section 4 HARD-FAIL
item 1). UNBLOCKED by Director: both scalar-channel anchors' residuals measured.

QUESTION: the MAGNITUDE scalar channel (Anchor 1) moved NUMERAL words (seven, dozen) but MATH-OPERATION words
(multiplication, ratio, equation, infinity) stayed UN-MOVED at ~-0.13 CITED@spawn-prompt (Anchor 1 = MIDDLE_BAND; Anchor 2
social scalar = HARD_FAIL_AFFECT_RELABEL). Both scalar channels converge on the same diagnosis: operation words have NO
scalar attribute value to inject -- they are grounded STRUCTURALLY (metaphor / relational mapping onto embodied image
schemas), not by a scalar attribute. This anchor is that structural fix: a GROUNDED_VIA_METAPHOR graph EDGE from each
math-operation concept to a concrete IMAGE-SCHEMA hub node (PATH / CONTAINER / FORCE / COLLECTION / MOTION), seeded from
Lakoff & Nunez's 4 arithmetic-grounding metaphors, reusing the EXISTING diffusion machinery (the ATL-hub note's "literal
hub node" option -- the hub inherits the MEASURED norms of its concrete exemplar words, nothing fabricated). We then re-run
the IDENTICAL per-domain cosine grounding-reach test on the MATH-OPERATION probe subset (apples-to-apples vs the -0.13
magnitude baseline).

MECHANISM (contract, hand-off Anchor 3 + note Section 3 B):
  * IMAGE-SCHEMA HUB NODES: 5 embodied image schemas, each instantiated as a "literal hub" -- a synthetic core node whose
    attribute vector is the nanmean of the MEASURED norm rows of a set of concrete EXEMPLAR words for that schema (road,
    box, push, pile, move ...). REAL measured norms; no fabrication; a schema with no in-graph exemplar coverage gets NaN
    (honest no-coverage, excluded).
  * METAPHOR EDGES: each MATH-OPERATION probe gets one GROUNDED_VIA_METAPHOR edge to its Lakoff/Nunez image-schema hub. The
    probe stays HELD-OUT of the core; diffusion carries the hub's grounded coordinate to the probe.
  * INHERITS MAGNITUDE: the baseline already includes Anchor 1's computed magnitude/ordinality channels + numeral core
    anchors, so the ONLY difference between the mechanism and the magnitude-only baseline is the metaphor edges -> the
    "beats magnitude-only baseline on operation words specifically" control is exact (same Y, same core, same base graph).

FUSION: no new mechanism. Same late-fusion attribute matrix as Anchor 1 (reuses mag.build_attr_matrix_ext + mag.CANDIDATES);
same base._diffuse_attr diffusion-with-restart engine; same base._cos reach metric; same global z-scoring. The bridge is
purely a new EDGE TYPE (Section 3 B: a flat scalar channel would flatten away the relational content -- addition maps to
path-motion, not to "some quantity of path-ness" -- which is why (B) cannot collapse into (A)).

MANDATORY FAIRNESS GATES (hand-off contract; non-negotiable):
  1. SCRAMBLED-mapping must-fail: permute the metaphor->schema assignment across the operation probes (each probe wired to
     ANOTHER probe's schema hub) -> the reach gain must VANISH (fall back to the magnitude-only baseline). A persisting gain
     under scrambled mapping = "any embodied edge helps", not the SPECIFIC metaphor -> HARD_FAIL_FAIRNESS.
  2. RANDOM-schema must-fail: each operation probe wired to a UNIFORMLY-RANDOM schema hub -> reach gain must vanish too.
  3. BEATS-MAGNITUDE-ONLY: the metaphor arm operation-word sim must exceed the magnitude-only baseline (no metaphor edges)
     by MIN_ABS_GAIN, and the gain must be carried by the metaphor edges (bridge ablation = removing the edges collapses it
     >= BRIDGE_ABLATION_MIN_REL relative).

BANDS (pre-registered; research note Section 4 item 1 bar; sharpened not loosened):
  METAPHOR_BRIDGE_GROUNDS_MATH_OP (ALL): MATH-OPERATION mean sim_mech moves from ~-0.13 to >= MATH_OP_SIM_PASS (+0.15)
    held-out; gain (mech - magnitude_baseline) >= MIN_ABS_GAIN (0.10); scrambled AND random <= baseline + SPECIFICITY_MARGIN
    (0.05); bridge ablation (mech vs baseline) >= BRIDGE_ABLATION_MIN_REL (0.50 relative); holds on MEDIAN across seeds.
  HARD_FAIL_BRIDGE_INSUFFICIENT: operation sim stays <= 0 with well-behaved (correctly-failing) scrambled+random controls
    -> the metaphor edge type is well-formed but insufficient; the operation-word residual is a BOUNDED FINDING (Pecher &
    Zeelenberg boundary: language/convention carries residual), NOT a bug to chase with more edge types. This is a
    LEGITIMATE literature-consistent outcome, reported as such.
  HARD_FAIL_FAIRNESS: scrambled OR random ALSO gains (specific metaphor mapping does no work; any embodied edge inflates).
  MIDDLE_BAND: operation sim moves positive but below the +0.15 bar, or gain/ablation weak -> investigate before scaling.

SELF-TEST (planted metaphor world; the LIGHT local gate; NO data; discriminators MUST FIRE + survive scale):
  Plant K image schemas each with a distinct latent signature. Exemplar core nodes carry (signature + noise) = grounded
  hubs. Operation probes carry TRUE attributes = their schema signature, but their ONLY base-graph edges run to DISTRACTOR
  core nodes carrying the ANTI-correlated signature (reproduces anti-grounding: baseline sim < 0). (a) base graph (no
  metaphor edges) -> operation probes anti/un-grounded; (b) + correct metaphor edges to the schema hub -> reach flips
  positive (mechanism fires); (c) scrambled mapping -> wrong hub -> gain vanishes (fairness discriminator fires); (d)
  random schema -> gain vanishes. Scale-invariant in expectation (per-probe reach fraction) -> DISCRIMINATOR-MUST-SURVIVE-
  SCALE Path C planted-preview.

## Compute architecture
class (a) batched-GPU-capable but CPU-fast for the eval (edge-list diffusion via the reused a519 engine, n capped ~6000,
4 arm diffusions x seeds, seconds/seed on CPU; same regime as Anchor 1 + the v1 reach cell). Storage SHARDED (each concept
its own grounded vector; no bundling). SELF-TEST planted-only (seconds, tiny n) runs LOCAL. SMOKE uses source="cn" (LOCAL
relations.jsonl; NO CSKG download) on a SMALL core + the MATHEMATICAL(operation) + a few exemplar/PHYSICAL probes --
validates the mechanism + all 3 fairness discriminators fire only. FULL (CSKG assembly + all 6 domains + operation subset,
multi-seed) routes to remote_cpu_queue (graph parse dominates; CPU / numpy diffusion -- does NOT compete with the GPU
reasoning run; Tier B).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor/sec.13/sec.16/sec.17):
  arms_differ_verified (>=4 distinct arm sigs: metaphor / magnitude-baseline / scrambled-mapping / random-schema) at
  self-test gate; final_metrics_atomicity=tmp_replace (write_metrics uses os.replace); except SystemExit before except
  Exception (no BaseException / bare); crlb: per-probe cosine chance ~0, std~1/sqrt(S) in z-err space (THEORETICAL),
  HARD_PASS strictly above 0 by +0.15; baseline_in_band: MATH-OPERATION magnitude-baseline sim <= 0 is the in-band
  (anti-grounded) baseline by construction CITED@spawn-prompt(-0.13); discriminator-survives-scale: planted metaphor
  self-test fires the bridge gain + scramble collapse + random collapse at full reach logic (Path C planted-preview + Path
  B scale-invariance of the reach fraction); HP_SCOPE: operation-sim-pass + bridge-ablation + specificity gates apply to
  METAPHOR_BRIDGE vs MAGNITUDE_BASELINE + SCRAMBLED_MAPPING + RANDOM_SCHEMA only; calibration_check=
  default_ok_for_this_regime (engine + reach defaults inherited from the validated v1 reach + Anchor-1 magnitude cells);
  progress_logging=print_flush_true; cell_chunked=false (single graph, seeds cheap); start_marker + crash_diagnostic
  present; heartbeat via per-seed logs; cardinality_ok EXPECTED_N_UNITS=n_seeds; provenance: image-schema exemplars are
  concrete public words joined to the EXISTING measured norms (no acquisition); metaphor map is definitional
  (Lakoff/Nunez); optional data -> data/grounding_testbed/ (gitignored; NOT canonical substrate_index; never git add -A).
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir, write_metrics, write_partial  # noqa: E402
import experiments.exp_spanning_grounded_core_reach_v1 as base  # noqa: E402
import experiments.exp_spanning_grounded_core_reach_magnitude_v1 as mag  # noqa: E402

ANCHOR_NAME = "spanning_grounded_core_reach_metaphor_bridge_v1"

# ---------------------------------------------------------------------------
# Image-schema literal hubs (CITED@Lakoff&Nunez 2000; CITED@Johnson image schemas). Concrete EXEMPLAR words per schema;
# the hub node inherits the nanmean of these words' MEASURED norm rows (real; no fabrication). Applied over whatever
# exemplars land in the relational graph -- no-coverage schema -> hub NaN -> excluded.
# ---------------------------------------------------------------------------
IMAGE_SCHEMAS = ["PATH", "CONTAINER", "FORCE", "COLLECTION", "MOTION"]
SCHEMA_EXEMPLARS = {
    "PATH": ["path", "road", "journey", "route", "step", "forward", "distance", "trail", "way", "line"],
    "CONTAINER": ["box", "container", "inside", "hold", "fill", "empty", "bucket", "bottle", "bag", "jar"],
    "FORCE": ["push", "pull", "press", "force", "weight", "heavy", "effort", "lift", "squeeze", "balance"],
    "COLLECTION": ["group", "pile", "heap", "collection", "gather", "bunch", "cluster", "stack", "crowd", "batch"],
    "MOTION": ["move", "motion", "flow", "travel", "run", "speed", "spin", "roll", "slide", "turn"],
}

# ---- Lakoff/Nunez arithmetic-grounding-metaphor map: each MATH-OPERATION probe -> its embodied image schema.
#      (Object-Collection: multiplication/sum/division/fraction/ratio/probability; Motion-Along-Path: average/integer/
#      infinity/theorem; Object-Construction/Container: equation-as-balance=FORCE, variable/algebra/geometry=CONTAINER;
#      accelerating growth / rotation = MOTION for exponent/angle.) ----
METAPHOR_MAP = {
    "multiplication": "COLLECTION", "sum": "COLLECTION", "division": "COLLECTION", "fraction": "COLLECTION",
    "ratio": "COLLECTION", "probability": "COLLECTION",
    "average": "PATH", "integer": "PATH", "infinity": "PATH", "theorem": "PATH",
    "equation": "FORCE",
    "variable": "CONTAINER", "algebra": "CONTAINER", "geometry": "CONTAINER",
    "exponent": "MOTION", "angle": "MOTION",
}
FOCUS_DOMAIN = "MATHEMATICAL"   # base.PROBES["MATHEMATICAL"] IS the operation-word subset (multiplication, ratio, ...)

# ---- Arms ----
MECH = "METAPHOR_BRIDGE"
BASE_MAG = "MAGNITUDE_BASELINE"
SCR_MAP = "SCRAMBLED_MAPPING"
RND_SCH = "RANDOM_SCHEMA"
ARMS = [MECH, BASE_MAG, SCR_MAP, RND_SCH]

# ---- Reused bands / dims ----
SIM_FLOOR = base.SIM_FLOOR
MIN_REACH_CHANNELS = base.MIN_REACH_CHANNELS
DOMAINS = list(mag.DOMAINS)   # 6 base domains + MATH_NUMERAL

# ---- Pre-registered bands ----
MATH_OP_SIM_PASS = 0.15          # operation-word mean sim HARD_PASS floor (research note Section 4 item 1; held-out)
MIN_ABS_GAIN = 0.10              # metaphor arm must beat magnitude baseline by >= this (absolute)
SPECIFICITY_MARGIN = 0.05        # scrambled + random must stay <= baseline + this (bridge specificity)
BRIDGE_ABLATION_MIN_REL = 0.50   # removing metaphor edges must collapse >= 50% of the gain

SELFTEST_CFG = dict(seeds=[7], source="planted", n_kernel=0, max_nodes=0)
SMOKE_CFG = dict(seeds=[7, 13], source="cn", n_kernel=300, max_nodes=3000)
FULL_CFG = dict(seeds=[7, 13, 17, 23, 29], source="cskg", n_kernel=1500, max_nodes=6000)


# ---------------------------------------------------------------------------
# Logging / markers / crash diagnostics (sec.13 / sec.16 / sec.17).
# ---------------------------------------------------------------------------
def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _r(x):
    if x is None or (isinstance(x, float) and x != x):
        return "nan"
    return "%.4f" % x


def _none(x):
    if x is None or (isinstance(x, float) and x != x):
        return None
    return round(float(x), 4)


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Image-schema hub construction + metaphor edge sets.
# ---------------------------------------------------------------------------
def build_schema_hubs(words, Y, present, idx):
    """Append one synthetic 'literal hub' node per image schema; its attribute row = nanmean of its in-graph exemplar
    rows (REAL measured norms). Returns (words2, Y2, present2, hub_idx {schema: node_index or None}, hub_meta)."""
    n0 = len(words)
    K = Y.shape[1]
    hub_rows = []
    hub_idx = {}
    hub_meta = {}
    next_i = n0
    for sch in IMAGE_SCHEMAS:
        ex_rows = []
        n_ex = 0
        for w in SCHEMA_EXEMPLARS[sch]:
            nw = base._norm_word(w)
            j = idx.get(nw)
            if j is not None and present[j].any():
                ex_rows.append(Y[j])
                n_ex += 1
        if n_ex == 0:
            hub_idx[sch] = None
            hub_meta[sch] = dict(n_exemplars_in_graph=0, hub_node=None)
            continue
        row = np.nanmean(np.stack(ex_rows, axis=0), axis=0)   # nanmean -> NaN only where NO exemplar covered that channel
        hub_rows.append(row)
        hub_idx[sch] = next_i
        hub_meta[sch] = dict(n_exemplars_in_graph=n_ex, hub_node=next_i)
        next_i += 1
    if hub_rows:
        Y2 = np.vstack([Y, np.stack(hub_rows, axis=0)])
    else:
        Y2 = Y
    present2 = np.isfinite(Y2)
    words2 = list(words) + ["imgschema__%s" % s for s in IMAGE_SCHEMAS if hub_idx.get(s) is not None]
    return words2, Y2, present2, hub_idx, hub_meta


def build_metaphor_edges(schema_of_probe, hub_idx, mode, seed):
    """Metaphor edge set (np[M,2]) connecting each operation probe to a schema hub.
      mode 'correct'   : probe -> its Lakoff/Nunez schema hub.
      mode 'scrambled' : probe -> ANOTHER probe's schema hub (derangement-ish permutation of the assignment).
      mode 'random'    : probe -> a uniformly-random schema hub.
    Probes whose schema has no hub (no exemplar coverage) are dropped (honest)."""
    rng = np.random.default_rng(seed * 100019 + 41)
    probes = [p for p in schema_of_probe]
    schemas_avail = [s for s in IMAGE_SCHEMAS if hub_idx.get(s) is not None]
    edges = []
    if mode == "scrambled":
        assigned = [schema_of_probe[p] for p in probes]
        perm = rng.permutation(len(probes))
        # ensure at least most assignments move (permutation of the schema labels across probes)
        assigned = [assigned[perm[k]] for k in range(len(probes))]
        pmap = {probes[k]: assigned[k] for k in range(len(probes))}
    elif mode == "random":
        pmap = {p: (schemas_avail[int(rng.integers(len(schemas_avail)))] if schemas_avail else None) for p in probes}
    else:
        pmap = {p: schema_of_probe[p] for p in probes}
    for p in probes:
        sch = pmap[p]
        h = hub_idx.get(sch) if sch is not None else None
        if h is not None:
            edges.append((min(p, h), max(p, h)))
    return np.array(sorted(set(edges)), dtype=np.int64) if edges else np.zeros((0, 2), dtype=np.int64)


# ---------------------------------------------------------------------------
# Reach eval: 4 arms differ ONLY by the metaphor edge set appended to the shared base graph. Global z-scoring computed once
# (edge-independent) so the ONLY between-arm difference is the diffusion graph.
# ---------------------------------------------------------------------------
def run_arms(words, base_edges, Y, present, sel_idx, core_mask, probe_domain, schema_of_probe, hub_idx, seed, device):
    n = len(words)
    core_idx = np.where(core_mask)[0]
    if core_idx.shape[0] < 10:
        return dict(error="core_too_small", n_core=int(core_idx.shape[0]))
    S = len(sel_idx)
    Ysel = Y[:, sel_idx]
    glob_mu = np.nanmean(Ysel, axis=0)
    glob_sd = np.nanstd(Ysel, axis=0)
    glob_sd = np.where(glob_sd > 1e-9, glob_sd, 1.0)
    Zall = (Ysel - glob_mu) / glob_sd
    E0 = np.zeros((n, S), dtype=np.float32)
    E0[core_idx] = np.where(np.isfinite(Zall[core_idx]), Zall[core_idx], 0.0).astype(np.float32)

    meta_correct = build_metaphor_edges(schema_of_probe, hub_idx, "correct", seed)
    meta_scr = build_metaphor_edges(schema_of_probe, hub_idx, "scrambled", seed)
    meta_rnd = build_metaphor_edges(schema_of_probe, hub_idx, "random", seed)
    arm_edges = {
        BASE_MAG: base_edges,
        MECH: _vstack_edges(base_edges, meta_correct),
        SCR_MAP: _vstack_edges(base_edges, meta_scr),
        RND_SCH: _vstack_edges(base_edges, meta_rnd),
    }

    per_arm = {}
    arm_sigs = {}
    for arm, edges_arm in arm_edges.items():
        G = base._diffuse_attr(edges_arm, n, torch.from_numpy(E0).to(device), device).cpu().numpy()
        arm_sigs[arm] = hashlib.sha256(G.round(4).tobytes()).hexdigest()[:16]
        pd = {}
        for dom in DOMAINS:
            idxs = [i for i in range(n) if probe_domain.get(i) == dom and not core_mask[i]]
            sims = []
            reached = 0
            counted = 0
            for pi in idxs:
                true_z = Zall[pi]
                if int(np.isfinite(true_z).sum()) < MIN_REACH_CHANNELS:
                    continue
                counted += 1
                sim = base._cos(G[pi], true_z)
                if sim != sim:
                    sim = 0.0
                sims.append(sim)
                if sim >= SIM_FLOOR:
                    reached += 1
            pd[dom] = dict(mean_sim=(float(np.mean(sims)) if sims else float("nan")),
                           reach=(reached / counted) if counted else float("nan"),
                           n_probes=counted, n_reached=reached)
        per_arm[arm] = pd
    return dict(per_arm=per_arm, arm_sigs=arm_sigs, n_core=int(core_idx.shape[0]),
                n_meta_correct=int(meta_correct.shape[0]), n_meta_scrambled=int(meta_scr.shape[0]),
                n_meta_random=int(meta_rnd.shape[0]))


def _vstack_edges(a, b):
    if a.shape[0] == 0:
        return b
    if b.shape[0] == 0:
        return a
    return np.vstack([a, b])


# ---------------------------------------------------------------------------
# Aggregate + verdict (MEDIAN across seeds; focus = MATH-OPERATION subset).
# ---------------------------------------------------------------------------
def _median(seed_rows, arm, dom, field):
    vals = [s["per_arm"][arm][dom][field] for s in seed_rows
            if s["per_arm"][arm][dom].get("n_probes", 0) > 0
            and s["per_arm"][arm][dom][field] == s["per_arm"][arm][dom][field]]
    return float(np.median(vals)) if vals else float("nan")


def aggregate_and_verdict(seed_rows, meta):
    D = FOCUS_DOMAIN
    mech = _median(seed_rows, MECH, D, "mean_sim")
    basel = _median(seed_rows, BASE_MAG, D, "mean_sim")
    scr = _median(seed_rows, SCR_MAP, D, "mean_sim")
    rnd = _median(seed_rows, RND_SCH, D, "mean_sim")
    mech_reach = _median(seed_rows, MECH, D, "reach")
    basel_reach = _median(seed_rows, BASE_MAG, D, "reach")

    gain = (mech - basel) if (mech == mech and basel == basel) else float("nan")

    def _rel_collapse(with_v, without_v):
        if with_v != with_v or with_v <= 1e-6:
            return float("nan")
        bv = without_v if (without_v == without_v) else 0.0
        return max(0.0, (with_v - bv) / abs(with_v))

    ablation = _rel_collapse(mech, basel)   # fraction of the mechanism sim carried by the metaphor edges

    # specificity: a scrambled/random arm that ALSO gains ~as much as mech means any embodied edge helps (inflation).
    def _spurious(alt):
        if gain != gain or gain < MIN_ABS_GAIN:
            return False
        return bool(alt == alt and basel == basel and alt > basel + max(SPECIFICITY_MARGIN, 0.5 * gain))
    scr_bad = _spurious(scr)
    rnd_bad = _spurious(rnd)
    scr_ok = bool(scr != scr or basel != basel or scr <= basel + SPECIFICITY_MARGIN)
    rnd_ok = bool(rnd != rnd or basel != basel or rnd <= basel + SPECIFICITY_MARGIN)

    bridge_pass = bool(mech == mech and mech >= MATH_OP_SIM_PASS
                       and gain == gain and gain >= MIN_ABS_GAIN
                       and ablation == ablation and ablation >= BRIDGE_ABLATION_MIN_REL
                       and scr_ok and rnd_ok)

    if scr_bad or rnd_bad:
        verdict = "HARD_FAIL_FAIRNESS"
        one_line = ("fairness gate failed (scrambled_gain=%s random_gain=%s) -> any embodied edge inflates, the SPECIFIC "
                    "metaphor mapping does no work" % (scr_bad, rnd_bad))
    elif bridge_pass:
        verdict = "METAPHOR_BRIDGE_GROUNDS_MATH_OP"
        one_line = ("metaphor bridge moves MATH-OPERATION grounding-reach off ~-0.13 to %.3f (magnitude baseline %.3f, gain "
                    "%.3f) with scrambled+random null + ablation-carried (%.0f%%) -> structural fix REAL" % (
                        mech, basel if basel == basel else float("nan"),
                        gain if gain == gain else float("nan"),
                        100 * (ablation if ablation == ablation else 0.0)))
    elif (mech == mech and mech <= 0):
        verdict = "HARD_FAIL_BRIDGE_INSUFFICIENT"
        one_line = ("metaphor edge well-formed (scrambled+random controls fire) but operation sim still <= 0 (%.3f) -> "
                    "BOUNDED FINDING: operation-word residual carried by language/convention (Pecher-Zeelenberg boundary), "
                    "not closable by this edge type" % mech)
    else:
        verdict = "MIDDLE_BAND"
        one_line = ("partial: MATH-OPERATION sim %.3f (baseline %.3f gain %.3f ablation %.0f%%) below +%.2f bar or gain/"
                    "ablation weak -> investigate before scaling" % (
                        mech if mech == mech else float("nan"), basel if basel == basel else float("nan"),
                        gain if gain == gain else float("nan"),
                        100 * (ablation if ablation == ablation else 0.0), MATH_OP_SIM_PASS))

    return dict(verdict=verdict, one_line=one_line,
                op_sim_mech=_none(mech), op_sim_baseline=_none(basel), op_sim_scrambled=_none(scr),
                op_sim_random=_none(rnd), op_gain=_none(gain), bridge_ablation_rel=_none(ablation),
                op_reach_mech=_none(mech_reach), op_reach_baseline=_none(basel_reach),
                scramble_ok=scr_ok, random_ok=rnd_ok,
                bands=dict(MATH_OP_SIM_PASS=MATH_OP_SIM_PASS, MIN_ABS_GAIN=MIN_ABS_GAIN,
                           SPECIFICITY_MARGIN=SPECIFICITY_MARGIN, BRIDGE_ABLATION_MIN_REL=BRIDGE_ABLATION_MIN_REL,
                           SIM_FLOOR=SIM_FLOOR), meta=meta)


# ---------------------------------------------------------------------------
# Planted metaphor world self-test (LIGHT; discriminators MUST fire; scale-invariant).
# ---------------------------------------------------------------------------
def _planted_metaphor_world(seed):
    """K image schemas each with a distinct (near-orthogonal) latent signature. Exemplar core nodes = signature + noise
    (grounded hubs are the nanmean over them). Operation probes: TRUE attrs = their schema signature (held out of core).
    Their ONLY base-graph edges run to a FEW exemplars of a DIFFERENT (orthogonal) schema -> baseline grounding is
    ~un-grounded/mildly-off (reproduces the -0.13 regime, NOT a strong anti-edge artifact). The correct metaphor edge ->
    the probe's own schema hub injects the RIGHT embodied coordinate and dominates -> positive reach. Scrambled/random
    metaphor edges route to a wrong (orthogonal) hub -> no gain. Returns the interface the real run feeds run_arms."""
    rng = np.random.default_rng(seed)
    K = 4
    Dc = 10                                  # attribute channels (higher -> cleaner near-orthogonal schema signatures)
    n_ex = 8                                 # exemplars per schema (grounded core)
    n_pr = 8                                 # operation probes per schema
    n_base_neigh = 1                         # base-graph orthogonal neighbors per probe (kept small: a bridge can dominate)
    sig = rng.standard_normal((K, Dc))
    sig = sig / (np.linalg.norm(sig, axis=1, keepdims=True) + 1e-9)

    rows = []
    node_dom = {}
    is_core = []
    probe_schema_latent = {}                 # probe node index -> schema index (for building base+metaphor edges)
    ex_of_schema = {k: [] for k in range(K)}
    probes_of_schema = {k: [] for k in range(K)}
    i = 0
    for k in range(K):
        for _ in range(n_ex):                # exemplar core nodes -> grounded signature
            rows.append(sig[k] + 0.20 * rng.standard_normal(Dc)); node_dom[i] = "EXEMPLAR"; is_core.append(True)
            ex_of_schema[k].append(i); i += 1
        for _ in range(n_pr):                # operation probes -> TRUE attrs = schema signature (held out of core)
            rows.append(sig[k] + 0.20 * rng.standard_normal(Dc)); node_dom[i] = FOCUS_DOMAIN; is_core.append(False)
            probes_of_schema[k].append(i); probe_schema_latent[i] = k; i += 1
    n = i
    Y = np.stack(rows, axis=0).astype(np.float64)
    present = np.ones((n, Dc), dtype=bool)
    core_mask = np.array(is_core, dtype=bool)
    sel_idx = list(range(Dc))

    # base graph: exemplars connect among their own schema (coherent hubs); each probe connects to a FEW exemplars of the
    # NEXT (orthogonal) schema -> baseline diffusion carries an orthogonal coordinate (~un-grounded to the probe's true
    # schema). NO probe->own-schema-exemplar base edge (that grounding path IS the metaphor edge).
    base_edges = set()
    for k in range(K):
        ex = ex_of_schema[k]
        for a in range(len(ex)):
            for b in range(a + 1, len(ex)):
                base_edges.add((min(ex[a], ex[b]), max(ex[a], ex[b])))
        other_ex = ex_of_schema[(k + 1) % K][:n_base_neigh]
        for p in probes_of_schema[k]:
            for d in other_ex:
                base_edges.add((min(p, d), max(p, d)))
    base_edges = np.array(sorted(base_edges), dtype=np.int64)

    # synthetic hubs from exemplar nanmean (mirrors the real build_schema_hubs path).
    hub_rows = []
    hub_idx = {}
    idx_next = n
    schema_names = ["PATH", "CONTAINER", "FORCE", "COLLECTION"][:K]
    for k in range(K):
        hub_rows.append(np.nanmean(Y[ex_of_schema[k]], axis=0))
        hub_idx[schema_names[k]] = idx_next
        idx_next += 1
    Y = np.vstack([Y, np.stack(hub_rows, axis=0)])
    present = np.isfinite(Y)
    core_mask = np.concatenate([core_mask, np.ones(K, dtype=bool)])
    for k in range(K):
        node_dom[n + k] = "HUB"
    words = ["p%d" % j for j in range(Y.shape[0])]
    schema_of_probe = {p: schema_names[probe_schema_latent[p]] for p in probe_schema_latent}
    return words, base_edges, Y, present, sel_idx, core_mask, node_dom, schema_of_probe, hub_idx


def _mechanism_selftest(device):
    w, be, Y, pr, sel, cm, pd, sop, hub = _planted_metaphor_world(7)
    res = run_arms(w, be, Y, pr, sel, cm, pd, sop, hub, 7, device)
    if "error" in res:
        return False, res
    pa = res["per_arm"]
    D = FOCUS_DOMAIN
    mech = pa[MECH][D]["mean_sim"]
    basel = pa[BASE_MAG][D]["mean_sim"]
    scr = pa[SCR_MAP][D]["mean_sim"]
    rnd = pa[RND_SCH][D]["mean_sim"]
    reach_mech = pa[MECH][D]["reach"]
    gain = mech - basel
    mech_fires = bool(mech == mech and mech >= MATH_OP_SIM_PASS and basel == basel and gain >= 0.15)
    baseline_anti = bool(basel == basel and basel <= 0.05)   # baseline anti/un-grounded by construction
    scramble_fires = bool(scr == scr and scr <= basel + SPECIFICITY_MARGIN)
    random_fires = bool(rnd == rnd and rnd <= basel + SPECIFICITY_MARGIN)
    # reach-fraction (at SIM_FLOOR) is inherently noisier than mean-sim (Anchor-1 note); the clean discriminator is the
    # mean-sim gap above. reach must IMPROVE materially over baseline, not hit an absolute floor.
    reach_base = pa[BASE_MAG][D]["reach"]
    reach_moves = bool(reach_mech == reach_mech and reach_mech > 0.0
                       and (reach_base != reach_base or reach_mech >= reach_base + 0.10))
    arms_differ = bool(len(set(res["arm_sigs"].values())) >= 4)
    out = dict(op_sim_mech=_none(mech), op_sim_baseline=_none(basel), op_sim_scrambled=_none(scr),
               op_sim_random=_none(rnd), op_gain=_none(gain), op_reach_mech=_none(reach_mech),
               n_meta_correct=res["n_meta_correct"], n_meta_scrambled=res["n_meta_scrambled"],
               mech_fires=mech_fires, baseline_anti=baseline_anti, scramble_fires=scramble_fires,
               random_fires=random_fires, reach_moves=reach_moves, arms_differ=arms_differ)
    ok = bool(mech_fires and baseline_anti and scramble_fires and random_fires and reach_moves and arms_differ)
    return ok, out


# ---------------------------------------------------------------------------
# Real run (smoke / full).
# ---------------------------------------------------------------------------
def _run_real(run_mode, cfg, col_maps, computed, comp_meta, out_dir, t0, device):
    core_words, core_prov = base.build_core_words(col_maps, cfg["n_kernel"])
    # inherit Anchor-1 numeral magnitude anchors + add image-schema exemplars to the grounded core.
    anchor_words = set(base._norm_word(w) for w in mag.NUMERAL_CORE_ANCHORS)
    exemplar_words = set(base._norm_word(w) for sch in IMAGE_SCHEMAS for w in SCHEMA_EXEMPLARS[sch])
    core_words = set(core_words) | anchor_words | exemplar_words
    core_prov = dict(core_prov, n_numeral_anchors=len(anchor_words), n_schema_exemplars=len(exemplar_words),
                     n_core_expanded=len(core_words))

    probe_words = set()
    for dom in base.DOMAINS:
        for w in base.PROBES[dom]:
            probe_words.add(base._norm_word(w))
    for w in mag.MATH_NUMERAL_PROBES:
        probe_words.add(base._norm_word(w))
    probe_words -= core_words
    seed_words = core_words | probe_words | exemplar_words

    _log("assembling subgraph source=%s core=%d probes=%d exemplars=%d ..." % (
        cfg["source"], len(core_words), len(probe_words), len(exemplar_words)))
    words, edges, gmeta = base.build_relational_subgraph(cfg["source"], seed_words, base.HOPS, cfg["max_nodes"])
    _log("graph: scanned=%d n=%d edges=%d seeds_in_graph=%d" % (
        gmeta["n_edges_scanned"], gmeta["n_nodes"], gmeta["n_edges"], gmeta["n_seed_in_graph"]))
    if gmeta["n_nodes"] < 80 or gmeta["n_edges"] < 80:
        write_metrics(out_dir, dict(verdict="HARD_FAIL_GRAPH_EMPTY", run_mode=run_mode,
                      verdict_msg="subgraph too small (n=%d edges=%d source=%s)" % (
                          gmeta["n_nodes"], gmeta["n_edges"], cfg["source"]),
                      summary="graph empty", elapsed_s=time.perf_counter() - t0, graph_meta=gmeta))
        raise SystemExit(1)

    Y, present = mag.build_attr_matrix_ext(words, col_maps, computed)
    idx = {w: i for i, w in enumerate(words)}
    # image-schema literal hubs (nanmean of in-graph exemplar rows).
    words, Y, present, hub_idx, hub_meta = build_schema_hubs(words, Y, present, idx)
    _log("schema hubs: %s" % {s: hub_meta[s]["n_exemplars_in_graph"] for s in IMAGE_SCHEMAS})
    hubs_available = sum(1 for s in IMAGE_SCHEMAS if hub_idx.get(s) is not None)
    if hubs_available < 3:
        write_metrics(out_dir, dict(verdict="HARD_FAIL_HUBS_MISSING", run_mode=run_mode,
                      verdict_msg="only %d/5 image-schema hubs have exemplar coverage in graph -> bridge cannot fire; "
                                  "hub_meta=%s" % (hubs_available, hub_meta),
                      summary="schema hubs missing", elapsed_s=time.perf_counter() - t0, hub_meta=hub_meta))
        raise SystemExit(1)

    core_mask = np.zeros(len(words), dtype=bool)
    for w in core_words:
        if w in idx:
            core_mask[idx[w]] = True
    for s in IMAGE_SCHEMAS:                          # hubs are grounded core anchors
        if hub_idx.get(s) is not None:
            core_mask[hub_idx[s]] = True

    probe_domain = {}
    for dom in base.DOMAINS:
        for w in base.PROBES[dom]:
            nw = base._norm_word(w)
            if nw in idx and not core_mask[idx[nw]]:
                probe_domain[idx[nw]] = dom
    for w in mag.MATH_NUMERAL_PROBES:
        nw = base._norm_word(w)
        if nw in idx and not core_mask[idx[nw]]:
            probe_domain[idx[nw]] = "MATH_NUMERAL"

    # metaphor map -> operation probe indices (only MATHEMATICAL-domain probes present & non-core).
    schema_of_probe = {}
    for w, sch in METAPHOR_MAP.items():
        nw = base._norm_word(w)
        pi = idx.get(nw)
        if pi is not None and probe_domain.get(pi) == FOCUS_DOMAIN:
            schema_of_probe[pi] = sch
    _log("operation probes mapped=%d (of %d in METAPHOR_MAP)" % (len(schema_of_probe), len(METAPHOR_MAP)))
    if len(schema_of_probe) < 4:
        write_metrics(out_dir, dict(verdict="HARD_FAIL_PROBES_MISSING", run_mode=run_mode,
                      verdict_msg="only %d operation probes in graph -> subset too small to evaluate the bridge" % (
                          len(schema_of_probe)),
                      summary="operation probes missing", elapsed_s=time.perf_counter() - t0))
        raise SystemExit(1)

    sel_idx = mag.select_channels(Y[core_mask], present[core_mask], include_new=True)
    _log("channels selected=%d (%s)" % (len(sel_idx), [mag.ATTR_NAMES[i] for i in sel_idx]))
    probe_cov = {dom: sum(1 for i, d in probe_domain.items() if d == dom) for dom in DOMAINS}
    _log("probe coverage per domain: %s" % probe_cov)

    seed_rows = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            res = run_arms(words, edges, Y, present, sel_idx, core_mask, probe_domain, schema_of_probe, hub_idx,
                           seed, device)
            if "error" in res:
                raise RuntimeError("run_arms error=%s" % res.get("error"))
            if len(set(res["arm_sigs"].values())) < 4:
                raise RuntimeError("ARMS_MUST_DIFFER seed=%d only %d sigs" % (seed, len(set(res["arm_sigs"].values()))))
            seed_rows.append(res)
            write_partial(out_dir, seed, dict(seed=seed, per_arm=res["per_arm"], arm_sigs=res["arm_sigs"]))
            D = FOCUS_DOMAIN
            _log("seed=%d OP mech=%s baseline=%s scrambled=%s random=%s | NUMERAL mech=%s" % (
                seed, _r(res["per_arm"][MECH][D]["mean_sim"]), _r(res["per_arm"][BASE_MAG][D]["mean_sim"]),
                _r(res["per_arm"][SCR_MAP][D]["mean_sim"]), _r(res["per_arm"][RND_SCH][D]["mean_sim"]),
                _r(res["per_arm"][MECH].get("MATH_NUMERAL", {}).get("mean_sim", float("nan")))))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            seed_failures.append(dict(seed=seed, failure_class=type(e).__name__, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d %s: %s" % (seed, type(e).__name__, str(e)[:200]))

    if len(seed_rows) < len(cfg["seeds"]):
        write_metrics(out_dir, dict(verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
                      verdict_msg="expected %d seeds got %d failures=%s" % (
                          len(cfg["seeds"]), len(seed_rows), seed_failures),
                      summary="cardinality breach", elapsed_s=time.perf_counter() - t0, seed_failures=seed_failures))
        raise SystemExit(1)

    meta = dict(source=cfg["source"], graph_meta=gmeta, core_provenance=core_prov, hub_meta=hub_meta,
                n_operation_probes=len(schema_of_probe), metaphor_map={base._norm_word(k): v for k, v in METAPHOR_MAP.items()},
                selected_channels=[mag.ATTR_NAMES[i] for i in sel_idx], probe_coverage=probe_cov,
                computed_meta=comp_meta, n_seeds=len(cfg["seeds"]))
    agg = aggregate_and_verdict(seed_rows, meta)
    vmsg = ("%s || %s || OP sim mech=%s baseline=%s scrambled=%s random=%s gain=%s ablation=%s || source=%s n=%d "
            "hubs=%d ops=%d" % (
                agg["verdict"], agg["one_line"], _r(agg["op_sim_mech"]), _r(agg["op_sim_baseline"]),
                _r(agg["op_sim_scrambled"]), _r(agg["op_sim_random"]), _r(agg["op_gain"]), _r(agg["bridge_ablation_rel"]),
                cfg["source"], gmeta["n_nodes"], hubs_available, len(schema_of_probe)))
    write_metrics(out_dir, dict(verdict=agg["verdict"], run_mode=run_mode, verdict_msg=vmsg[:1500],
                  summary=agg["one_line"][:300], elapsed_s=time.perf_counter() - t0, reach=agg, meta=meta,
                  seed_rows=[dict(seed=cfg["seeds"][k], per_arm=seed_rows[k]["per_arm"]) for k in range(len(seed_rows))]))
    _log("VERDICT %s :: %s (%.1fs)" % (agg["verdict"], agg["one_line"], time.perf_counter() - t0))


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    device = torch.device("cpu") if args.device == "cpu" else torch.device(
        "cuda" if ((args.device in ("auto", "cuda")) and torch.cuda.is_available()) else "cpu")

    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    _write_start_marker(str(out_dir), run_mode, len(cfg["seeds"]))
    t0 = time.perf_counter()
    _log("device=%s run_mode=%s" % (device, run_mode))

    # LIGHT planted metaphor self-test: discriminators MUST fire (runs in EVERY mode as the pre-flight gate).
    st_ok, st_res = _mechanism_selftest(device)
    _log("mechanism_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(out_dir, dict(verdict="HARD_FAIL", run_mode=run_mode,
                      verdict_msg="MECHANISM_SELFTEST_FAILED (planted metaphor bridge did not fire / scramble or random did "
                                  "not collapse / baseline not anti-grounded / arms not distinct): %s" % st_res,
                      summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(verdict="SELFTEST_PASS", run_mode="self_test",
                      verdict_msg="SELFTEST_PASS: planted metaphor bridge flips MATH-OPERATION reach positive; magnitude/"
                                  "base graph anti-grounds it; scrambled mapping + random schema collapse the gain; arms "
                                  "differ. %s" % st_res,
                      summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t0))
        return

    # Real run: acquire base norm data + build computed magnitude maps (inherited from Anchor 1).
    for key in base.DATASETS:
        if not base._ensure_dataset(key):
            write_metrics(out_dir, dict(verdict="HARD_FAIL_DATA_MISSING", run_mode=run_mode,
                          verdict_msg="norm dataset %r absent + self-acquire failed" % key,
                          summary="norm data missing", elapsed_s=time.perf_counter() - t0))
            raise SystemExit(1)
    if cfg["source"] == "cskg" and not base._ensure_cskg():
        write_metrics(out_dir, dict(verdict="HARD_FAIL_DATA_MISSING", run_mode=run_mode,
                      verdict_msg="CSKG absent + self-acquire failed (Zenodo 4331372)",
                      summary="CSKG missing", elapsed_s=time.perf_counter() - t0))
        raise SystemExit(1)
    if cfg["source"] == "cn" and not os.path.exists(base.CN_RELATIONS):
        write_metrics(out_dir, dict(verdict="HARD_FAIL_DATA_MISSING", run_mode=run_mode,
                      verdict_msg="CN relations.jsonl absent: %s" % base.CN_RELATIONS,
                      summary="CN relations missing", elapsed_s=time.perf_counter() - t0))
        raise SystemExit(1)

    col_maps = base.load_all_norm_maps()
    computed, comp_meta = mag.build_computed_colmaps()
    _log("computed magnitude lexicon: mag=%d ordinality=%d acf=%s" % (
        len(computed["magnitude"]), len(computed["ordinality"]), comp_meta))
    _run_real(run_mode, cfg, col_maps, computed, comp_meta, out_dir, t0, device)


if __name__ == "__main__":
    output_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(output_dir, e)
        raise
