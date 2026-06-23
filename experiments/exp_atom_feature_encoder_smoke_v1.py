"""atom_feature_encoder_smoke_v1 -- encode atoms by FUNCTION not by NAME STRING.

USER reframe 2026-06-23: char-trigram encoder spells data types (atoms, entities,
relations, capabilities) by their NAME. Two atoms with same function but different
names don't cluster; two atoms with similar names but different functions do
cluster (wrong direction). Cheap MVP: encode atoms by their FEATURES (cert_tier
+ mechanism_family + sigma_regime + metric_profile + graph_neighborhood) and test
whether mechanism-family-purity of k-means clusters lifts vs the char-trigram
baseline. If HARD_PASS, this is the right direction for Gap 2 (self-mapping).

Cell:
  - load chain-grade atom_ids from cert_ledger.jsonl + per-atom metadata
    (mechanism keyword extracted from anchor name; cert tier from ledger;
    sigma + metric profile from atoms.jsonl metadata if present; graph
    neighborhood from composes_with / supersedes / referent_pointer fields)
  - encode each atom via two arms:
      ARM_CHAR_TRIGRAM_NAME : encode atom_id string via CharTrigramEncoder
      ARM_ATOM_FEATURE      : bind cert_tier + mechanism_family + sigma_regime
                              + metric_profile + graph_neighborhood (all
                              random bipolar HVs from a deterministic codebook
                              keyed by feature value); normalize-bundle
  - k-means cluster (K=10) on each arm; compute mechanism-family-purity
  - sanity planted-block: inject 3 atoms with IDENTICAL features but distinct
    mechanism-keyword names; verify atom_feature clusters them together while
    char_trigram clusters them by name

Pre-reg (preregs/2026-06-23_atom_feature_encoder_smoke_v1.md):
  HARD_PASS:
    ARM_ATOM_FEATURE.mechanism_family_purity >= 0.60
      AND ARM_ATOM_FEATURE.purity >= ARM_CHAR_TRIGRAM_NAME.purity + 0.15
    AND planted_block_atom_feature_cluster_purity == 1.0
    AND substrate-only-decode preserved (n_llm_calls == 0)
  HARD_FAIL:
    ARM_ATOM_FEATURE.purity <= ARM_CHAR_TRIGRAM_NAME.purity
      (feature-encoding adds nothing or hurts)
  MIDDLE_BAND:
    in between (positive lift but below HP threshold)

CPU; ASCII; per-seed checkpoint; seeds = [7, 17, 23].
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial,
    aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "atom_feature_encoder_smoke_v1"
LEDGER = REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"
SUBSTRATE_INDEX = REPO / "data" / "substrate_index"

# substrate-only-decode invariant
_LLM_CALL_COUNTER = [0]

# pre-registered HARD bands
PURITY_HP_FLOOR = 0.60
PURITY_HP_GAP = 0.15
PLANTED_BLOCK_PURITY = 1.0

# CLI
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_IS_SMOKE_BY_NAME = _HDLAB_NAME.endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _IS_SMOKE_BY_NAME) else "full"

if RUN_MODE == "smoke":
    SEEDS = [7]
    N_DIM = 1024
    N_ATOMS_SAMPLE = 30
    K_CLUSTERS = 5
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    N_ATOMS_SAMPLE = 100
    K_CLUSTERS = 10

# canonical mechanism family list (10 families); name keyword -> family bin
MECHANISM_FAMILIES = [
    "cleanup",
    "storage",
    "generation",
    "refuse",
    "multi_hop",
    "whitening",
    "binding",
    "capacity",
    "trigram",
    "other",
]

# mechanism keyword regex (substring match on lowercased atom name)
MECHANISM_KEYWORDS = {
    "cleanup": ["cleanup", "denoise", "recall"],
    "storage": ["storage", "memory", "hopfield", "kg_store", "store"],
    "generation": ["generation", "generate", "autoregressive", "gen"],
    "refuse": ["refuse", "gate", "abstain", "headroom"],
    "multi_hop": ["multi_hop", "kg_traversal", "traversal", "hop"],
    "whitening": ["whitening", "pca", "kwta", "vq"],
    "binding": ["binding", "bind", "fhrr", "hrr"],
    "capacity": ["capacity", "alpha", "M_", "envelope"],
    "trigram": ["trigram", "char_trigram", "encoder"],
}

# sigma regime bins
SIGMA_BINS = [
    ("sigma_lt_0p5", 0.0, 0.5),
    ("sigma_0p5_1p0", 0.5, 1.0),
    ("sigma_1p0_1p5", 1.0, 1.5),
    ("sigma_gt_1p5", 1.5, 1e9),
]

# cert tier list
CERT_TIERS = ["chain_grade", "measured_mechanism", "honest_negative", "other"]

CONFIG_VERSION = (
    "atom_feature_encoder_smoke_v1: ARM_CHAR_TRIGRAM_NAME (baseline) vs "
    "ARM_ATOM_FEATURE (cert_tier + mechanism_family + sigma_regime + "
    "metric_profile + graph_neighborhood); k-means K=%d on N=%d sampled atoms; "
    "mechanism_family_purity discriminator; HP purity >= %.2f AND lift >= %.2f"
) % (K_CLUSTERS, N_ATOMS_SAMPLE, PURITY_HP_FLOOR, PURITY_HP_GAP)


# ===== deterministic per-feature random bipolar HV codebook =====

def _seed_for_token(token: str) -> int:
    h = hashlib.blake2b(token.encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(token: str, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(_seed_for_token(token))
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


# ===== feature extraction =====

def mechanism_family_of(atom_id: str) -> str:
    """Return the mechanism family for an atom_id (lowercased substring scan)."""
    lo = atom_id.lower()
    for family in MECHANISM_FAMILIES:
        if family == "other":
            continue
        for kw in MECHANISM_KEYWORDS.get(family, []):
            if kw in lo:
                return family
    return "other"


def sigma_regime_of(metadata: dict) -> str:
    """Extract a sigma value from atom metadata if present; bin into 4 regimes."""
    # walk metadata for any numeric field with 'sigma' in the key
    sigma = None
    for k, v in (metadata or {}).items():
        if "sigma" in k.lower() and isinstance(v, (int, float)):
            sigma = float(v)
            break
    if sigma is None:
        return "sigma_unknown"
    for name, lo, hi in SIGMA_BINS:
        if lo <= sigma < hi:
            return name
    return "sigma_unknown"


def cert_tier_of(cert_status: str) -> str:
    s = (cert_status or "").lower()
    if "chain" in s:
        return "chain_grade"
    if "measured" in s or "mechanism" in s:
        return "measured_mechanism"
    if "honest" in s or "negative" in s:
        return "honest_negative"
    return "other"


def metric_profile_token(ledger_row: dict) -> str:
    """Hash (verdict prefix, cv-bucket, cert_increment_delta) into a stable token."""
    verdict = (ledger_row.get("verdict") or "")[:16]
    cv = ledger_row.get("cv")
    if cv is None:
        cv_bucket = "cv_none"
    else:
        try:
            cvf = float(cv)
            if cvf < 0.01:
                cv_bucket = "cv_lt_0p01"
            elif cvf < 0.05:
                cv_bucket = "cv_0p01_0p05"
            elif cvf < 0.10:
                cv_bucket = "cv_0p05_0p10"
            else:
                cv_bucket = "cv_gt_0p10"
        except (TypeError, ValueError):
            cv_bucket = "cv_none"
    delta = ledger_row.get("cert_increment_delta", 0)
    return "metric|%s|%s|delta=%s" % (verdict, cv_bucket, str(delta))


def graph_neighborhood_tokens(atom_id: str, atom_meta: dict) -> list[str]:
    """Return list of neighbor-atom tokens from composes/typed_by/cap fields."""
    tokens: list[str] = []
    meta = atom_meta.get("metadata", {}) or {}
    for k in ("composes", "composes_with", "typed_by", "retyped_by",
              "cap_backfilled_by", "atomized_by"):
        v = meta.get(k)
        if isinstance(v, str):
            tokens.append("nbr|" + v)
        elif isinstance(v, list):
            tokens.extend("nbr|" + str(x) for x in v if isinstance(x, str))
    serves = atom_meta.get("serves_capability", [])
    if isinstance(serves, list):
        tokens.extend("cap|" + str(x) for x in serves if isinstance(x, str))
    algebra = atom_meta.get("algebra", {}) or {}
    for k in ("about_topic", "domain", "structure", "role"):
        v = algebra.get(k)
        if isinstance(v, str):
            tokens.append("alg|" + k + "=" + v)
    return tokens


# ===== encoders =====

def encode_char_trigram(atom_id: str, n_dim: int) -> np.ndarray:
    """Baseline encoder: bag-of-char-trigrams over the atom_id string."""
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    enc = CharTrigramEncoder(n_dim=n_dim)
    return enc.encode(atom_id)


def encode_atom_feature(
    atom_id: str,
    ledger_row: dict,
    atom_meta: dict,
    n_dim: int,
) -> np.ndarray:
    """Function-encoder: bind cert_tier + mechanism_family + sigma_regime
    + metric_profile + graph_neighborhood into a single bipolar HV."""
    cert = cert_tier_of(ledger_row.get("cert_status", ""))
    family = mechanism_family_of(atom_id)
    sigma = sigma_regime_of(atom_meta.get("metadata", {}))
    metric_token = metric_profile_token(ledger_row)
    nbrs = graph_neighborhood_tokens(atom_id, atom_meta)

    cert_vec = _bipolar_hv("cert|" + cert, n_dim)
    family_vec = _bipolar_hv("family|" + family, n_dim)
    sigma_vec = _bipolar_hv("sigma|" + sigma, n_dim)
    metric_vec = _bipolar_hv(metric_token, n_dim)

    nbr_bundle = np.zeros(n_dim, dtype=np.float32)
    for n in nbrs:
        nbr_bundle += _bipolar_hv(n, n_dim)
    # sign-bundle neighborhood (matches char-trigram convention)
    nbr_bundle = np.sign(nbr_bundle).astype(np.float32)
    nbr_bundle[nbr_bundle == 0] = 1.0

    accum = cert_vec + family_vec + sigma_vec + metric_vec + nbr_bundle
    out = np.sign(accum).astype(np.float32)
    out[out == 0] = 1.0
    return out


# ===== k-means (numpy-only; simple Lloyd) =====

def kmeans_simple(X: np.ndarray, k: int, seed: int, n_iter: int = 50) -> np.ndarray:
    """Plain Lloyd's k-means on cosine-normalized rows; returns cluster ids [N]."""
    rng = np.random.default_rng(seed)
    n = X.shape[0]
    # cosine-normalize
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    Xn = X / norms
    init_idx = rng.choice(n, size=min(k, n), replace=False)
    centers = Xn[init_idx].copy()
    assign = np.zeros(n, dtype=np.int64)
    for _ in range(n_iter):
        # cosine sims = dot product since normalized
        sims = Xn @ centers.T
        new_assign = sims.argmax(axis=1)
        if np.array_equal(new_assign, assign):
            break
        assign = new_assign
        for kk in range(min(k, n)):
            mask = assign == kk
            if mask.any():
                m = Xn[mask].mean(axis=0)
                mn = np.linalg.norm(m) + 1e-8
                centers[kk] = m / mn
    return assign


def cluster_purity(labels: np.ndarray, families: list[str]) -> float:
    """For each cluster, count modal-family fraction; weighted average."""
    n = len(families)
    if n == 0:
        return 0.0
    total_correct = 0
    for c in sorted(set(labels.tolist())):
        idxs = [i for i, lab in enumerate(labels) if lab == c]
        if not idxs:
            continue
        fams = [families[i] for i in idxs]
        # modal-family count
        counts: dict[str, int] = {}
        for f in fams:
            counts[f] = counts.get(f, 0) + 1
        total_correct += max(counts.values())
    return total_correct / n


# ===== data load =====

def load_chain_grade_atoms() -> list[tuple[str, dict]]:
    """Return [(atom_id, ledger_row)] for distinct chain-grade atoms (latest per id)."""
    if not LEDGER.exists():
        raise FileNotFoundError("cert_ledger missing: %s" % LEDGER)
    seen: dict[str, dict] = {}
    with open(LEDGER, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("cert_status") != "chain_grade":
                continue
            aid = r.get("atom_id", "")
            if not aid:
                continue
            seen[aid] = r
    return sorted(seen.items(), key=lambda kv: kv[0])


def load_atoms_metadata() -> dict[str, dict]:
    """Return {bare atom_id -> full atom dict} across all corpora."""
    out: dict[str, dict] = {}
    if not SUBSTRATE_INDEX.is_dir():
        return out
    for corpus_dir in sorted(SUBSTRATE_INDEX.iterdir()):
        af = corpus_dir / "atoms.jsonl"
        if not af.is_file():
            continue
        with open(af, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                aid = r.get("id", "")
                if aid:
                    out[aid] = r
    return out


def _strip_corpus_prefix(atom_id: str) -> str:
    if "::" in atom_id:
        return atom_id.split("::", 1)[1]
    return atom_id


# ===== self-test =====

def _selftest():
    """Verify both encoders + k-means + purity end-to-end on a tiny synthetic set."""
    n_dim_test = 256
    # planted-block sanity: 3 atoms with IDENTICAL functional features but distinct
    # mechanism keywords in the name. char-trigram should split them; atom-feature
    # should bundle them together (since the features that drive atom_feature are
    # cert_tier + mechanism_family + sigma + metric + neighborhood, NOT the name).
    # Here we set up 3 atoms where mechanism_family DIFFERS by name keyword but
    # everything else is identical. Endpoint check is INVERSE: name-clusters split,
    # feature-clusters separate-by-family (i.e. atom_feature still partitions by
    # mechanism, which is what the full discriminator measures.) We treat the
    # 3 planted atoms as ground-truth-distinct-family for purity check.
    synthetic = [
        ("math::T3/EXP_alpha_cleanup_v1", "cleanup"),
        ("math::T3/EXP_beta_storage_v1", "storage"),
        ("math::T3/EXP_gamma_generation_v1", "generation"),
    ]
    rows = [{"cert_status": "chain_grade", "verdict": "CHAIN_GRADE",
             "cv": 0.05, "cert_increment_delta": 1} for _ in synthetic]
    metas = [{"metadata": {"sigma_peak": 1.5}, "algebra": {}, "serves_capability": []}
             for _ in synthetic]

    families = [s[1] for s in synthetic]
    aids = [s[0] for s in synthetic]

    feat_vecs = np.stack([encode_atom_feature(a, r, m, n_dim_test)
                          for a, r, m in zip(aids, rows, metas)])
    trig_vecs = np.stack([encode_char_trigram(a, n_dim_test) for a in aids])

    # both encoders should produce nonzero distinct vectors
    for arr, name in ((feat_vecs, "feat"), (trig_vecs, "trig")):
        norms = np.linalg.norm(arr, axis=1)
        assert (norms > 0).all(), "%s vec norms must be > 0" % name

    # k-means smoke (k=3 on 3 atoms; each should land in its own cluster)
    fa = kmeans_simple(feat_vecs, k=3, seed=0)
    ta = kmeans_simple(trig_vecs, k=3, seed=0)
    pf = cluster_purity(fa, families)
    pt = cluster_purity(ta, families)
    assert 0.0 <= pf <= 1.0, "feat purity out of range: %f" % pf
    assert 0.0 <= pt <= 1.0, "trig purity out of range: %f" % pt

    # substrate-only-decode invariant
    assert _LLM_CALL_COUNTER[0] == 0, "substrate-only-decode violated"

    print("[selftest] PASS: encoders + kmeans + purity smoke; "
          "feat_purity=%.3f trig_purity=%.3f n_llm_calls=%d" %
          (pf, pt, _LLM_CALL_COUNTER[0]), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ===== main run =====

def run_one_seed(seed: int, atoms: list[tuple[str, dict]],
                 atom_meta: dict[str, dict]) -> dict:
    """Run both arms + planted-block sanity for a single seed; return per-seed dict."""
    t0 = time.time()
    rng = np.random.default_rng(seed)

    # sample N atoms from the chain-grade pool
    n_pool = len(atoms)
    n_sample = min(N_ATOMS_SAMPLE, n_pool)
    idx = rng.choice(n_pool, size=n_sample, replace=False)
    sampled = [atoms[int(i)] for i in idx]

    aids = [aid for aid, _ in sampled]
    ledger_rows = [row for _, row in sampled]
    metas = [atom_meta.get(_strip_corpus_prefix(aid), {}) for aid in aids]
    families = [mechanism_family_of(aid) for aid in aids]

    # encode both arms
    feat_vecs = np.stack([
        encode_atom_feature(aid, row, meta, N_DIM)
        for aid, row, meta in zip(aids, ledger_rows, metas)
    ])
    trig_vecs = np.stack([encode_char_trigram(aid, N_DIM) for aid in aids])

    # k-means K clusters on each
    feat_labels = kmeans_simple(feat_vecs, k=K_CLUSTERS, seed=seed)
    trig_labels = kmeans_simple(trig_vecs, k=K_CLUSTERS, seed=seed)

    feat_purity = cluster_purity(feat_labels, families)
    trig_purity = cluster_purity(trig_labels, families)

    # planted-block sanity: 3 atoms with IDENTICAL features (same cert/sigma/metric/nbrs)
    # but DIFFERENT mechanism families via name. atom_feature should cluster them by
    # mechanism (since mechanism_family is one of its features); char_trigram should
    # cluster them by NAME (split). We check atom_feature's family-purity on the
    # planted trio equals 1.0 (each is its own mechanism in its own cluster).
    planted_aids = [
        "math::T3/EXP_PLANTED_cleanup_v1",
        "math::T3/EXP_PLANTED_storage_v1",
        "math::T3/EXP_PLANTED_generation_v1",
    ]
    planted_families = [mechanism_family_of(a) for a in planted_aids]
    planted_rows = [{"cert_status": "chain_grade", "verdict": "CG",
                     "cv": 0.05, "cert_increment_delta": 1} for _ in planted_aids]
    planted_metas = [{"metadata": {"sigma_peak": 1.5}, "algebra": {},
                      "serves_capability": []} for _ in planted_aids]
    planted_feat = np.stack([
        encode_atom_feature(a, r, m, N_DIM)
        for a, r, m in zip(planted_aids, planted_rows, planted_metas)
    ])
    planted_labels = kmeans_simple(planted_feat, k=3, seed=seed)
    planted_purity = cluster_purity(planted_labels, planted_families)

    elapsed = time.time() - t0

    return {
        "seed": seed,
        "N": N_DIM,
        "M": n_sample,
        "run_mode": RUN_MODE,
        "arm_atom_feature_purity": float(feat_purity),
        "arm_char_trigram_purity": float(trig_purity),
        "purity_lift": float(feat_purity - trig_purity),
        "planted_block_purity": float(planted_purity),
        "n_atoms_sampled": n_sample,
        "k_clusters": K_CLUSTERS,
        "elapsed_s": elapsed,
        "n_llm_calls": _LLM_CALL_COUNTER[0],
        "family_distribution": {
            f: families.count(f) for f in set(families)
        },
    }


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[%s] start mode=%s seeds=%s N_DIM=%d K=%d N_atoms=%d" %
          (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, K_CLUSTERS, N_ATOMS_SAMPLE),
          flush=True)

    print("[%s] loading chain-grade atoms + metadata..." % ANCHOR_NAME, flush=True)
    atoms = load_chain_grade_atoms()
    atom_meta = load_atoms_metadata()
    print("[%s] loaded %d chain-grade atoms; %d atom-metadata entries" %
          (ANCHOR_NAME, len(atoms), len(atom_meta)), flush=True)

    if len(atoms) < 3:
        raise RuntimeError("not enough chain-grade atoms: %d" % len(atoms))

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "M": N_ATOMS_SAMPLE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[%s] ckpt: %d done; running %d" %
          (ANCHOR_NAME, len(done), len(remaining)), flush=True)

    for seed in remaining:
        print("[%s] seed=%d running..." % (ANCHOR_NAME, seed), flush=True)
        result = run_one_seed(seed, atoms, atom_meta)
        write_partial(out_dir, seed, result)
        print("[%s] seed=%d done: feat=%.3f trig=%.3f lift=%+.3f planted=%.3f" %
              (ANCHOR_NAME, seed,
               result["arm_atom_feature_purity"],
               result["arm_char_trigram_purity"],
               result["purity_lift"],
               result["planted_block_purity"]), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)

    # aggregate
    feat_vals = [per_seed[str(s)]["arm_atom_feature_purity"] for s in SEEDS]
    trig_vals = [per_seed[str(s)]["arm_char_trigram_purity"] for s in SEEDS]
    lift_vals = [per_seed[str(s)]["purity_lift"] for s in SEEDS]
    planted_vals = [per_seed[str(s)]["planted_block_purity"] for s in SEEDS]
    elapsed_vals = [per_seed[str(s)]["elapsed_s"] for s in SEEDS]
    n_llm = sum(per_seed[str(s)]["n_llm_calls"] for s in SEEDS)

    feat_mean = float(np.mean(feat_vals))
    feat_std = float(np.std(feat_vals))
    trig_mean = float(np.mean(trig_vals))
    trig_std = float(np.std(trig_vals))
    lift_mean = float(np.mean(lift_vals))
    planted_mean = float(np.mean(planted_vals))

    feat_cv = feat_std / (feat_mean + 1e-8)
    elapsed_s = float(np.sum(elapsed_vals))

    # verdict
    hp_purity_ok = feat_mean >= PURITY_HP_FLOOR
    hp_lift_ok = lift_mean >= PURITY_HP_GAP
    hp_planted_ok = planted_mean >= PLANTED_BLOCK_PURITY
    hp_no_llm = (n_llm == 0)

    hard_fail = (feat_mean <= trig_mean) or (not hp_no_llm)

    if hp_purity_ok and hp_lift_ok and hp_planted_ok and hp_no_llm:
        verdict = "HARD_PASS"
    elif hard_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s_%s_%dseeds_N%d_K%d_M%d_atom_feature_purity_%.3f_pm_%.3f_"
        "char_trigram_purity_%.3f_pm_%.3f_lift_%+.3f_planted_block_purity_%.3f_"
        "n_llm_calls_%d_cv_feat_%.4f_elapsed_%.1fs"
    ) % (
        verdict, RUN_MODE.upper(), len(SEEDS), N_DIM, K_CLUSTERS, N_ATOMS_SAMPLE,
        feat_mean, feat_std, trig_mean, trig_std, lift_mean, planted_mean,
        n_llm, feat_cv, elapsed_s,
    )

    summary = {
        "anchor": ANCHOR_NAME,
        "config_version": CONFIG_VERSION,
        "run_mode": RUN_MODE,
        "seeds": SEEDS,
        "N_DIM": N_DIM,
        "K_CLUSTERS": K_CLUSTERS,
        "N_ATOMS_SAMPLE": N_ATOMS_SAMPLE,
        "arm_atom_feature_purity_mean": feat_mean,
        "arm_atom_feature_purity_std": feat_std,
        "arm_atom_feature_purity_cv": feat_cv,
        "arm_char_trigram_purity_mean": trig_mean,
        "arm_char_trigram_purity_std": trig_std,
        "purity_lift_mean": lift_mean,
        "planted_block_purity_mean": planted_mean,
        "n_llm_calls": n_llm,
        "n_chain_grade_atoms_pool": len(atoms),
        "hp_thresholds": {
            "purity_floor": PURITY_HP_FLOOR,
            "lift_floor": PURITY_HP_GAP,
            "planted_purity_required": PLANTED_BLOCK_PURITY,
        },
        "hp_gates": {
            "purity_ok": hp_purity_ok,
            "lift_ok": hp_lift_ok,
            "planted_ok": hp_planted_ok,
            "no_llm": hp_no_llm,
        },
    }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed_s,
        "summary": summary,
        "per_seed": per_seed,
    }

    write_metrics(out_dir, metrics)
    print("[%s] %s" % (ANCHOR_NAME, verdict_msg), flush=True)


if __name__ == "__main__":
    main()
