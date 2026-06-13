"""
exp_substrate_history_latent_structure_probe_cpu_v1.py -- is HISTORY's promotion-gap FUNDAMENTAL or merely UNBUILT? -- CPU/local (no heat, read-only).

ROUTING: follow-up to the cross-field universality probe (exp_substrate_cross_field_promotion_universality_probe) which found history at
  0.000 structural-signal corroboration vs math/science/language at 0.93-1.0. BUT that measured history with MATH'S INSTRUMENTS (shared
  DEPENDS_ON prereqs + math metadata fields history does not populate). This cell asks the CRUX question the USER + Research drill care
  about: does history have LATENT organizing structure recoverable with a FIELD-APPROPRIATE signal? For history, the field-appropriate
  signal is TOPICAL (what a note is about), not prerequisite-sharing. If history text organizes into coherent topic-clusters FAR above a
  shuffled null, the gap is UNBUILT (history is promotable once we surface topical metadata) -- supporting UNIVERSAL-operator + per-field
  signal-instrumentation. If real ~ null, it leans FUNDAMENTAL (history text does not carry recoverable structure). NO LLM; token stats;
  numpy only for the null shuffle; no heat. READ-ONLY (derives candidate topical structure; writes nothing canonical).

  METHOD: per history atom, salient vocabulary = content tokens of name+description with document-frequency 2 <= df <= DF_MAX_FRAC*N
  (the df-band AUTO-STRIPS boilerplate: ubiquitous tokens like 'substrate'/'research'/dates have high df and drop out; singletons drop out;
  what remains is DISTINCTIVE-but-RECURRING topical vocabulary). Topic edge (a,b) iff |salient_a & salient_b| >= K_SHARED. Connected
  components size>=3 = topic clusters. COVERAGE = fraction of history atoms in a topic cluster. NULL = redraw each atom's salient set at
  random from the global token pool preserving per-atom size + global token frequencies; recompute coverage. Structure is REAL iff
  real_coverage >> null_coverage.

PRE-REGISTERED: LATENT-STRUCTURE-PRESENT (history gap is UNBUILT, universal-operator supported) iff real coverage >= 0.30 AND real >=
  2.0x null coverage. WEAK (leans toward fundamental / different signal needed) iff real coverage in [0.10,0.30) OR real in [1.3x,2.0x) null.
  ABSENT (leans FUNDAMENTAL) iff real < 0.10 OR real < 1.3x null. UNKNOWN if too few history atoms / no text.
ASCII-only. CPU/local. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_history_latent_structure_probe_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
K_SHARED = 4; DF_MAX_FRAC = 0.08; DF_MIN = 2; MIN_TOK_LEN = 4; SEED = 1028
_STOP = set("the of a an and or to for with in on is as by at from this that these those it its be are was were will would can could should has have had not but if then so we our us you your they their he she his her them then than into over under more most less data note date research drill exp dev testbed substrate verdict decision result results finding findings memory cycle phase per via use used using also new now via".split())


def _tokens(text: str):
    return [t for t in re.split(r"[^a-z0-9]+", (text or "").lower()) if len(t) >= MIN_TOK_LEN and t not in _STOP and not t.isdigit()]


def sibling_pairs(salient: Dict[str, set], k_shared: int, max_bucket: int = 60):
    """Pairwise (CHAINING-FREE): count, per atom, whether it shares >= k_shared salient tokens with SOME specific partner.
       Returns (set of atoms with >=1 strong topical sibling, dict pair->shared_count for examples)."""
    tok2atoms = defaultdict(list)
    for a, toks in salient.items():
        for t in toks:
            tok2atoms[t].append(a)
    pair = Counter()
    for t, atoms in tok2atoms.items():
        if len(atoms) <= max_bucket:              # a distinctive token shared by a small set -> real co-topic signal
            for i in range(len(atoms)):
                for j in range(i + 1, len(atoms)):
                    x, y = atoms[i], atoms[j]
                    pair[(x, y) if x < y else (y, x)] += 1
    has_sib = set()
    for (x, y), c in pair.items():
        if c >= k_shared:
            has_sib.add(x); has_sib.add(y)
    return has_sib, pair


def coverage(salient, k_shared, n_total):
    """Fraction of atoms with >=1 chaining-free topical sibling (shares >=k_shared distinctive tokens with a SPECIFIC partner)."""
    has_sib, pair = sibling_pairs(salient, k_shared)
    return len(has_sib) / max(1, n_total), pair


def _selftest():
    # two genuine topic clusters (share >=4 distinctive tokens) + isolates
    sal = {
        "a": {"viterbi", "decode", "hmm", "trellis", "lattice"},
        "b": {"viterbi", "decode", "hmm", "trellis", "noise"},
        "c": {"viterbi", "decode", "hmm", "trellis", "path"},
        "d": {"hopfield", "energy", "attractor", "capacity", "spin"},
        "e": {"hopfield", "energy", "attractor", "capacity", "hebb"},
        "f": {"hopfield", "energy", "attractor", "capacity", "basin"},
        "g": {"unique1", "unique2", "unique3", "unique4", "unique5"},
    }
    cov, _ = coverage(sal, 4, 7)
    has_sib, _ = sibling_pairs(sal, 4)
    assert has_sib == {"a", "b", "c", "d", "e", "f"} and "g" not in has_sib, has_sib   # chaining-free: g isolated
    assert abs(cov - 6 / 7) < 1e-6, cov
    toks = _tokens("# Research Note: Viterbi decoding 2026 the HMM trellis-lattice")
    assert "viterbi" in toks and "research" not in toks and "2026" not in toks and "the" not in toks, toks
    print("[selftest] PASS: substrate_history_latent_structure_probe_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    from backend.substrate_index.partition import PartitionedStore
    atoms = PartitionedStore(root).all_atoms()
    hist = []
    for a in atoms:
        c = str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower()
        if "history" in c:
            txt = (getattr(a, "name", "") or "") + " . " + (getattr(a, "description", "") or "")
            hist.append((str(a.id), txt))
    N = len(hist)
    if N < 30:
        return {"error": "too_few_history_atoms", "N": N}
    if RUN_MODE == "smoke":
        hist = hist[: max(40, N // 3)]; N = len(hist)
    # document frequency
    toks_per = {aid: set(_tokens(txt)) for aid, txt in hist}
    df = Counter()
    for s in toks_per.values():
        for t in s: df[t] += 1
    df_max = max(3, int(DF_MAX_FRAC * N))
    salient = {aid: {t for t in s if DF_MIN <= df[t] <= df_max} for aid, s in toks_per.items()}
    salient = {a: s for a, s in salient.items() if len(s) >= K_SHARED}     # need enough salient tokens to possibly link
    n_eff = len(salient)
    real_cov, _ = coverage(salient, K_SHARED, N)
    # cohesive topic buckets (CHAINING-FREE): each distinctive token shared by >=3 atoms is a coherent micro-topic (all literally share it)
    tok2atoms = defaultdict(list)
    for a, toks in salient.items():
        for t in toks: tok2atoms[t].append(a)
    buckets = sorted([(t, ats) for t, ats in tok2atoms.items() if 3 <= len(ats) <= 60], key=lambda kv: -len(kv[1]))
    # NULL: redraw each atom's salient set at random from the global salient-token pool, preserving per-atom size + token freq
    pool = []
    for t, c in df.items():
        if DF_MIN <= c <= df_max:
            pool.extend([t] * c)
    rng = np.random.default_rng(SEED)
    pool = np.array(pool, dtype=object)
    null_covs = []
    for _ in range(5 if RUN_MODE != "smoke" else 2):
        shuffled = {}
        for a, s in salient.items():
            draw = rng.choice(len(pool), size=len(s), replace=False)
            shuffled[a] = set(pool[draw].tolist())
        nc, _ = coverage(shuffled, K_SHARED, N)
        null_covs.append(nc)
    null_cov = float(np.mean(null_covs))
    ratio = real_cov / (null_cov + 1e-9)
    # example derived topics = the cohesive distinctive-token buckets (would-be history metadata)
    examples = [{"topic_token": t, "size": len(ats), "members": [m.split("::")[-1] for m in ats[:4]]} for t, ats in buckets[:8]]
    print("  history atoms=%d (eff with >=%d salient tokens=%d) df_max=%d" % (N, K_SHARED, n_eff, df_max), flush=True)
    print("  REAL sibling-coverage=%.4f (atoms with a chaining-free topical sibling, share>=%d distinctive tokens) | NULL=%.4f | ratio=%.2fx" % (
        real_cov, K_SHARED, null_cov, ratio), flush=True)
    print("  cohesive topic buckets (distinctive token shared by 3-60 atoms): %d | sizes(top)=%s" % (
        len(buckets), [len(a) for _, a in buckets[:12]]), flush=True)
    for e in examples[:6]:
        print("    TOPIC '%s' size=%2d :: %s" % (e["topic_token"], e["size"], e["members"][:3]), flush=True)
    return {"n_history": N, "n_eff": n_eff, "df_max": df_max, "real_coverage": round(real_cov, 4),
            "null_coverage": round(null_cov, 4), "ratio": round(ratio, 3), "n_topic_buckets": len(buckets),
            "bucket_sizes": [len(a) for _, a in buckets][:20], "example_topics": examples}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("N", "")))
    rc = r["real_coverage"]; nc = r["null_coverage"]; ratio = r["ratio"]
    s = ("history atoms=%d: REAL sibling-coverage=%.4f vs NULL=%.4f (ratio=%.2fx); %d cohesive topic buckets (sizes %s). "
         "Field-appropriate signal = distinctive shared vocabulary (df-banded, boilerplate auto-stripped), chaining-free pairwise, NOT math's prereq-sharing.") % (
        r["n_history"], rc, nc, ratio, r["n_topic_buckets"], r["bucket_sizes"][:12])
    if rc >= 0.30 and ratio >= 2.0:
        return ("UNBUILT_LEANING", "UNBUILT-LEANING (history gap is NOT fundamental): history has STRONG latent topical structure -- %.0f%% of atoms fall into coherent topic clusters, %.1fx above the shuffled null. The earlier 0.0 structural-corroboration was a WRONG-INSTRUMENT artifact (math's prereq-signal + unpopulated math metadata). With a FIELD-APPROPRIATE signal (topical vocabulary) history IS organizable -> supports UNIVERSAL operator + per-field signal-instrumentation; history just needs its topical metadata surfaced. " % (rc * 100, ratio) + s)
    if rc >= 0.10 or ratio >= 1.3:
        return ("WEAK", "WEAK / MIXED: history shows SOME latent topical structure (coverage %.2f, %.1fx null) but not strongly -- a topical signal partially organizes history; field-appropriate instrumentation helps but the structure is looser than math's. " % (rc, ratio) + s)
    return ("FUNDAMENTAL_LEANING", "FUNDAMENTAL-LEANING: history text does NOT organize into topic clusters above chance (coverage %.2f, %.1fx null) -- even a field-appropriate topical signal finds little recoverable structure; history's promotion gap may be more than unbuilt. " % (rc, ratio) + s)


print("[config] anchor=%s mode=%s k_shared=%d df_max_frac=%.2f" % (ANCHOR_NAME, RUN_MODE, K_SHARED, DF_MAX_FRAC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
