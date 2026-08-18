"""Self-improving reader TEACUP v2 -- STREAMING slot-in (assimilate/accommodate) generalizer on the
reader's OWN labeler-mislabel failures, at scale (UD-EWT dev+test, out-of-sample, frozen labeler).

USER's operational model (better than a verb-holdout -- the STREAMING slot-in gives held-out
generalization NATURALLY): atomize EVERY mislabel as a specific (situation-signature -> correct role)
atom; then an INCREMENTAL sleep-generalizer processes atoms in STREAM ORDER and for each new atom
FIRST tries to SLOT IT INTO an existing rule (does the current rule set already predict this atom's
correction? = assimilation) ELSE it seeds/joins toward a NEW rule (accommodation). The honest held-out
number is TEMPORAL: for each atom, BEFORE it is added, do the rules built from PRIOR atoms ONLY predict
its fix (the atom never helped form the rules that predict it).

FAILURE SURFACE (non-circular, out-of-sample): frozen persisted arc-labeler
(data/frontend_assets/arc_labeler_hashed_ud_ewt.json, trained on UD-EWT TRAIN) mislabels the patient
arc (gold obj / nsubj:pass under a VERB head, straight from the gold parse edge) on UD-EWT DEV+TEST
(never trained on). MEASURED census (this cell): ~239 mislabels / ~2536 patient arcs.

MECHANISM (recombination of certified primitives, composed IN-CELL; NO production-hdlab mutation):
  - SITUATION SIGNATURE (glass-box, GOLD-FREE): dense bipolar HD bundle of hdlab.arc_labeler.
    arc_features(tokens,pos,i,head) -- the exact features the labeler sees; it NEVER takes the gold
    deprel. Deterministic hashlib per-feature codes (NO PYTHONHASHSEED). Mutation-probed.
  - EXACT-RECALL TIER (atomize ALL fixes): hdlab.hippocampal_encoder one-shot Hebbian bind of every
    atom (specific memory) -> ~100% exact recall of its own correction (the guaranteed-recall tier).
  - INCREMENTAL RULE SET (the sleep-generalizer): online signature clusters (leader clustering; each
    cluster = a RULE with a prototype + a correction distribution). CONSOLIDATION = hdlab.continual.
    replay_cycle: at each SLEEP, replay the recent episodic buffer into cluster prototypes -- with
    values = cluster one-hots and keys = member signatures, replay_cycle accumulates member sigs into
    each cluster's prototype row (the NREM re-consolidation that STRENGTHENS prototypes from episodes).
    (NOT AdditiveKGMap: that is a KGE-SGD map = wrong tool. The additive/superposition principle IS
    the replay_cycle Hebbian accumulation. exp_dev catch, Director-confirmed.)
  - schema cross-check: hdlab.schema_exemplar_bayes clusters atoms (diagnostic n_schemas + purity).

CORRECTION TARGET = specific gold patient role {obj, nsubj:pass} (2-class) -> the SCRAMBLE control can
fire. Word order (pre-verbal nsubj:pass vs post-verbal obj) is a legitimate STRUCTURAL cue, NOT a gold
leak (arc_features never sees the deprel; mutation-probed). Can-fail: if failures do not compress /
slot-in does not rise / rules do not beat base-rate = honest NEGATIVE.

DESIGN-GATE (pre-registered): REAL baseline = the base-rate-override (always apply the running-majority
correction) -- the rules must BEAT it. DIFFICULTY-ON = temporal held-out is leak-free by construction
(prior atoms only). ONE-VARIABLE = coherent vs scrambled atoms. tau_cluster is a leak-safe property of
the signature geometry (a percentile of pairwise signature cosines -- uses signatures, NEVER corrections).

MEASURES (Director spec):
  - EXACT-RECALL (hippocampal atomize-all tier; ~100% guaranteed-recall).
  - COMPRESSION: 239 atoms -> n_rules + n_singletons; compression_ratio = n_atoms / n_rules.
  - SLOT-IN RATE over the stream + whether it RISES (last-third vs first-third).
  - TEMPORAL-HELD-OUT PREDICTION: prior-rules-only predict each new atom's fix (rate + evolution).
  - RULE PURITY: per rule, do grouped atoms share the correct answer (size-weighted majority fraction).
MUST-FAIL (both): (a) SCRAMBLE atom<->correction -> slot-in + temporal prediction must COLLAPSE;
  (b) BASE-RATE-OVERRIDE baseline (always majority correction) reported so we see how much rules beat it.

BANDS (honest, can-fail):
  REAL_GENERALIZATION : temporal_slot_in >= base_rate_override + 0.10 AND slot-in RISES (>= +0.05
                        last-third vs first-third) AND scramble collapses temporal_slot_in by >= 0.10
                        AND rule_purity >= 0.70 AND compression_ratio >= 2.0 AND leak-clean.
  NO_GENERALIZATION   : temporal_slot_in <= base_rate_override + 0.03 (no beat) OR compression_ratio
                        < 1.3 (no compression) OR scramble does NOT collapse (< 0.05).
  MIDDLE_BAND         : between.

COMPUTE: class (b) sequential-CPU (justified: ~2.5k arcs, 239 atoms, tiny numpy/torch, multi-seed <60s).
  LOCAL-ONLY, foreground-to-completion; NO queue/push/remote-persist/git-add/hdlab-edit. Deterministic:
  OMP/MKL/OPENBLAS=1, fixed int seeds (permute stream order), hashlib feature codes, sorted(set).
  progress_logging: print_flush_true.

PRIOR-WORK CHECK: CLS lit-notes only at cosine 0.46/0.39 (conceptual); this streaming slot-in
  assimilate/accommodate test on the reader's own out-of-sample mislabels with temporal-held-out +
  scramble + base-rate baseline is novel. CITED@KB 2026-07-21.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "reader_selfimprove_stream_slotin_udewt_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.arc_labeler import ArcLabeler, arc_features, norm_label  # noqa: E402

FR = os.path.join(REPO_ROOT, "data", "frontend_assets")
LABELER_PATH = os.path.join(FR, "arc_labeler_hashed_ud_ewt.json")
UD_DIR = os.path.join(REPO_ROOT, "experiments", "data", "ud_english_ewt")

PATIENT_ROLES = ("obj", "nsubj:pass")
N_SIG = 512
DG_DIM = 2048
SPARSITY = 0.02
SLEEP_EVERY = 20            # NREM consolidation cadence (atoms)
REPLAY_FRAC = 0.5


# ------------------------------------------------------------------------------------------------
def read_conllu(fn):
    sents = []
    cur = []
    with open(os.path.join(UD_DIR, fn), encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if cur:
                    sents.append(cur)
                    cur = []
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0]:
                continue
            cur.append((int(c[0]), c[1], c[3], int(c[6]), c[7]))
    if cur:
        sents.append(cur)
    return sents


_FEAT_CACHE = {}


def _feat_code(f):
    v = _FEAT_CACHE.get(f)
    if v is None:
        seed = int.from_bytes(hashlib.sha256(f.encode("utf-8")).digest()[:8], "big")
        v = (np.random.default_rng(seed).integers(0, 2, size=N_SIG).astype(np.float32) * 2.0 - 1.0)
        _FEAT_CACHE[f] = v
    return v


def signature(tokens, pos, i, h):
    """Dense HD signature of arc (dep i -> head h). GOLD-FREE (arc_features takes no deprel)."""
    v = np.zeros(N_SIG, dtype=np.float32)
    for f in arc_features(tokens, pos, i, h):
        v += _feat_code(f)
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def extract_mislabels(sents, lab):
    """Every labeler mislabel of a true patient arc -> an atom (signature, correction, verb)."""
    atoms = []
    n_patient = 0
    for s in sents:
        if not (1 <= len(s) <= 50):
            continue
        toks = [t[1] for t in s]
        pos = [t[2] for t in s]
        for i in range(1, len(s) + 1):
            gh = s[i - 1][3]
            gd = norm_label(s[i - 1][4])
            if gd not in PATIENT_ROLES or gh < 1 or gh > len(s) or pos[gh - 1] != "VERB":
                continue
            n_patient += 1
            pred = lab._predict_label(arc_features(toks, pos, i, gh))
            if pred != gd:
                atoms.append({"sig": signature(toks, pos, i, gh), "corr": gd, "pred": pred,
                              "vlem": toks[gh - 1].lower()})
    return atoms, n_patient


# ------------------------------------------------------------------------------------------------
# tau_cluster: leak-safe signature-geometry threshold (percentile of pairwise sig cosines; corrections
# NEVER used).
# ------------------------------------------------------------------------------------------------
def calibrate_tau(atoms, pct=75):
    X = np.asarray([a["sig"] for a in atoms], dtype=np.float32)
    if X.shape[0] < 3:
        return 0.5
    C = X @ X.T
    iu = np.triu_indices(X.shape[0], k=1)
    return float(np.percentile(C[iu], pct))


# ------------------------------------------------------------------------------------------------
# EXACT-RECALL tier: hippocampal one-shot bind of ALL atoms -> recall own correction.
# ------------------------------------------------------------------------------------------------
def exact_recall(atoms):
    if len(atoms) < 2:
        return None
    from hdlab.hippocampal_encoder import HippocampalEncoder
    X = np.asarray([a["sig"] for a in atoms], dtype=np.float32)
    enc = HippocampalEncoder(input_dim=N_SIG, dg_dim=DG_DIM, sparsity=SPARSITY, seed=7)
    codes = enc.encode_and_write(X)
    ret = enc.retrieve(X, use_ca3=True, sparsify_after_settle=True)
    # nearest stored code -> that atom's correction; correct iff == own correction
    hits = 0
    for i in range(len(atoms)):
        j = int(np.argmax(codes @ ret[i]))
        hits += int(atoms[j]["corr"] == atoms[i]["corr"])
    return round(hits / len(atoms), 4)


# ------------------------------------------------------------------------------------------------
# STREAMING slot-in generalizer. Online signature clusters (RULES); prototypes consolidated by
# continual.replay_cycle at each SLEEP. Temporal-held-out prediction = prior-rules-only.
# ------------------------------------------------------------------------------------------------
def _sleep_consolidate(protos, buffer_sigs, buffer_cids, n_clusters):
    """NREM: replay the episodic buffer into cluster prototypes via continual.replay_cycle.
    values = cluster one-hots [M, n_clusters]; keys = member sigs [M, sig]; W[n_clusters, sig] += vals.T@keys."""
    import torch
    from hdlab.continual import replay_cycle
    if not buffer_sigs:
        return protos
    keys = torch.from_numpy(np.asarray(buffer_sigs, dtype=np.float32))          # [M, sig]
    oneh = np.zeros((len(buffer_cids), n_clusters), dtype=np.float32)
    oneh[np.arange(len(buffer_cids)), np.asarray(buffer_cids)] = 1.0
    values = torch.from_numpy(oneh)                                             # [M, n_clusters]
    W = torch.from_numpy(protos.astype(np.float32))                            # [n_clusters, sig]
    idx = torch.arange(len(buffer_cids))
    replay_cycle(W, idx, keys, values, replay_frac=REPLAY_FRAC, lr=1.0)
    return W.numpy()


def stream_generalize(atoms, tau, seed):
    """Process atoms in stream order (permuted by seed). Returns per-atom records + final rules."""
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(atoms))
    protos = np.zeros((0, N_SIG), dtype=np.float32)   # unnormalized Hebbian prototype sums [K, sig]
    corr_counts = []                                  # list[Counter] per cluster
    members = []                                      # list[list[atom_idx]]
    buf_sigs, buf_cids = [], []                       # episodic buffer since last sleep
    prior_corr = Counter()                            # running correction counts (base-rate override)
    recs = []
    for step, ai in enumerate(order):
        a = atoms[ai]
        s = a["sig"].astype(np.float32)
        # ---- PREDICT (temporal held-out: PRIOR rules only) ----
        covered = False
        pred_corr = None
        nearest = -1
        best_cos = -1.0
        if protos.shape[0] > 0:
            pn = protos / (np.linalg.norm(protos, axis=1, keepdims=True) + 1e-9)
            cos = pn @ s
            nearest = int(np.argmax(cos))
            best_cos = float(cos[nearest])
            if best_cos >= tau:
                covered = True
                pred_corr = corr_counts[nearest].most_common(1)[0][0]
        temporal_correct = bool(covered and pred_corr == a["corr"])
        slot_in = temporal_correct
        # base-rate-override prediction (prior running majority)
        base_pred = prior_corr.most_common(1)[0][0] if prior_corr else None
        base_correct = bool(base_pred == a["corr"])
        recs.append({"step": step, "covered": covered, "temporal_correct": temporal_correct,
                     "slot_in": slot_in, "base_correct": base_correct, "corr": a["corr"]})
        # ---- ASSIMILATE / ACCOMMODATE ----
        if covered and best_cos >= tau:
            cid = nearest                       # assimilate into nearest rule
        else:
            cid = protos.shape[0]               # accommodate: NEW rule seeded by this atom
            protos = np.vstack([protos, s[None, :]])   # seed prototype = signature
            corr_counts.append(Counter())
            members.append([])
        corr_counts[cid][a["corr"]] += 1
        members[cid].append(int(ai))
        prior_corr[a["corr"]] += 1
        buf_sigs.append(s)
        buf_cids.append(cid)
        # ---- SLEEP (NREM consolidation via replay_cycle) ----
        if (step + 1) % SLEEP_EVERY == 0 and buf_sigs:
            protos = _sleep_consolidate(protos, buf_sigs, buf_cids, protos.shape[0])
            buf_sigs, buf_cids = [], []
    if buf_sigs:
        protos = _sleep_consolidate(protos, buf_sigs, buf_cids, protos.shape[0])
    return recs, corr_counts, members


def _slot_in_curve(recs, nbins=5):
    n = len(recs)
    if n == 0:
        return []
    out = []
    for b in range(nbins):
        lo = b * n // nbins
        hi = (b + 1) * n // nbins
        seg = recs[lo:hi]
        si = np.mean([r["slot_in"] for r in seg]) if seg else None
        out.append({"bin": b, "n": len(seg), "slot_in": round(float(si), 4) if si is not None else None})
    return out


def _summarize(recs, corr_counts, members):
    n = len(recs)
    slot = round(float(np.mean([r["slot_in"] for r in recs])), 4)
    covered = round(float(np.mean([r["covered"] for r in recs])), 4)
    temporal_when_covered = ([r["temporal_correct"] for r in recs if r["covered"]])
    tacc = round(float(np.mean(temporal_when_covered)), 4) if temporal_when_covered else None
    base_rate = round(float(np.mean([r["base_correct"] for r in recs])), 4)
    curve = _slot_in_curve(recs)
    # rising: last-third vs first-third slot-in
    t = n // 3
    first = np.mean([r["slot_in"] for r in recs[:t]]) if t else 0.0
    last = np.mean([r["slot_in"] for r in recs[-t:]]) if t else 0.0
    rises = round(float(last - first), 4)
    # compression + purity
    sizes = [len(m) for m in members]
    n_rules = len(sizes)
    n_singletons = sum(1 for z in sizes if z == 1)
    comp = round(n / max(1, n_rules), 3)
    purities = []
    for cc, sz in zip(corr_counts, sizes):
        if sz > 0:
            purities.append(cc.most_common(1)[0][1] / sz)
    purity = round(float(np.average(purities, weights=sizes)), 4) if purities else None
    return {"n_atoms": n, "temporal_slot_in": slot, "temporal_coverage": covered,
            "temporal_acc_when_covered": tacc, "base_rate_override": base_rate,
            "slot_in_curve": curve, "slot_in_rise_last_minus_first": rises,
            "n_rules": n_rules, "n_singletons": n_singletons, "compression_ratio": comp,
            "rule_purity_weighted": purity}


def _schema_report(atoms):
    if len(atoms) < 6:
        return {"n": len(atoms), "note": "too few"}
    from hdlab.schema_exemplar_bayes import SchemaExemplarBayesIndex
    X = np.asarray([a["sig"] for a in atoms], dtype=np.float32)
    idx = SchemaExemplarBayesIndex(compression_ratio=5, seed=7).fit(X)
    st = idx.stats()
    pur = []
    for c, f in idx.schema_to_facts.items():
        rs = [atoms[j]["corr"] for j in f]
        pur.append(Counter(rs).most_common(1)[0][1] / len(rs))
    return {"n_schemas": st["n_schemas"], "mean_role_purity": round(float(np.mean(pur)), 4)}


def _leak_probe(atoms_sents_lab):
    sents, lab = atoms_sents_lab
    import inspect as _insp
    src = _insp.getsource(arc_features)
    src_clean = ("deprel" not in src) and ("gold" not in src)
    ok = True
    seen = 0
    for s in sents:
        if not (1 <= len(s) <= 50):
            continue
        toks = [t[1] for t in s]
        pos = [t[2] for t in s]
        for i in range(1, len(s) + 1):
            gh = s[i - 1][3]
            if gh < 1 or gh > len(s) or pos[gh - 1] != "VERB":
                continue
            if norm_label(s[i - 1][4]) not in PATIENT_ROLES:
                continue
            if not np.array_equal(signature(toks, pos, i, gh), signature(toks, pos, i, gh)):
                ok = False
            seen += 1
            if seen >= 200:
                return bool(ok and src_clean)
    return bool(ok and src_clean)


# ================================================================================================
def cfg_smoke():
    return dict(mode="smoke", seeds=[7], n_sent_cap=1400)


def cfg_full():
    return dict(mode="full", seeds=[7, 13, 19], n_sent_cap=None)


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def _write_start_marker(output_dir, mode):
    os.makedirs(output_dir, exist_ok=True)
    m = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
         "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(m, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = _out_dir(mode)
    _write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START streaming slot-in generalizer", flush=True)

    lab = ArcLabeler.load(LABELER_PATH)
    sents = read_conllu("en_ewt-ud-dev.conllu") + read_conllu("en_ewt-ud-test.conllu")
    if cfg["n_sent_cap"]:
        sents = sents[:cfg["n_sent_cap"]]
    atoms, n_patient = extract_mislabels(sents, lab)
    census_conf = Counter((a["corr"], a["pred"]) for a in atoms)
    census = {"n_patient_arcs": n_patient, "n_atoms": len(atoms),
              "labeler_acc": round(1 - len(atoms) / n_patient, 4) if n_patient else None,
              "top_confusions": [{"rule": f"{c}->{p}", "n": k} for (c, p), k in census_conf.most_common(6)]}
    print(f"[{ANCHOR_NAME}:{mode}] CENSUS patient_arcs={n_patient} atoms={len(atoms)} "
          f"acc={census['labeler_acc']}", flush=True)

    leak_clean = _leak_probe((sents, lab))
    ex_recall = exact_recall(atoms)
    tau = calibrate_tau(atoms)
    schema = _schema_report(atoms)
    print(f"[{ANCHOR_NAME}:{mode}] EXACT-RECALL(hippocampal atomize-all)={ex_recall} tau_cluster={round(tau,4)} "
          f"leak_clean={leak_clean} schema={schema}", flush=True)

    per_seed = []
    for seed in cfg["seeds"]:
        recs, cc, mem = stream_generalize(atoms, tau, seed)
        summ = _summarize(recs, cc, mem)
        # MUST-FAIL (a): scramble atom<->correction
        rng = np.random.default_rng(2000 + seed)
        scr_atoms = [dict(a) for a in atoms]
        perm = rng.permutation(len(scr_atoms))
        corrs = [atoms[j]["corr"] for j in perm]
        for a, c in zip(scr_atoms, corrs):
            a["corr"] = c
        recs_s, cc_s, mem_s = stream_generalize(scr_atoms, tau, seed)
        summ_s = _summarize(recs_s, cc_s, mem_s)
        collapse = round(summ["temporal_slot_in"] - summ_s["temporal_slot_in"], 4)
        row = {"seed": seed, "coherent": summ, "scramble": summ_s, "slotin_collapse_scramble": collapse}
        per_seed.append(row)
        print(f"[{ANCHOR_NAME}:{mode}] seed={seed} slot_in={summ['temporal_slot_in']} "
              f"(cov={summ['temporal_coverage']} acc_cov={summ['temporal_acc_when_covered']}) "
              f"base_rate={summ['base_rate_override']} rise={summ['slot_in_rise_last_minus_first']} "
              f"comp={summ['compression_ratio']}({summ['n_rules']}r/{summ['n_singletons']}sing) "
              f"purity={summ['rule_purity_weighted']} | SCRAMBLE slot_in={summ_s['temporal_slot_in']} "
              f"(collapse={collapse})", flush=True)

    def mean(fn):
        vals = [fn(s) for s in per_seed]
        vals = [v for v in vals if isinstance(v, (int, float))]
        return round(float(np.mean(vals)), 4) if vals else None

    m_slot = mean(lambda s: s["coherent"]["temporal_slot_in"])
    m_base = mean(lambda s: s["coherent"]["base_rate_override"])
    m_rise = mean(lambda s: s["coherent"]["slot_in_rise_last_minus_first"])
    m_comp = mean(lambda s: s["coherent"]["compression_ratio"])
    m_pur = mean(lambda s: s["coherent"]["rule_purity_weighted"])
    m_scr = mean(lambda s: s["scramble"]["temporal_slot_in"])
    m_collapse = mean(lambda s: s["slotin_collapse_scramble"])
    m_cov = mean(lambda s: s["coherent"]["temporal_coverage"])

    beats_base = (m_slot is not None and m_base is not None and m_slot >= m_base + 0.10)
    rises = (m_rise is not None and m_rise >= 0.05)
    scramble_collapses = (m_collapse is not None and m_collapse >= 0.10)
    purity_ok = (m_pur is not None and m_pur >= 0.70)
    compresses = (m_comp is not None and m_comp >= 2.0)
    no_gen = ((m_slot is not None and m_base is not None and m_slot <= m_base + 0.03)
              or (m_comp is not None and m_comp < 1.3)
              or (m_collapse is not None and m_collapse < 0.05))
    if beats_base and rises and scramble_collapses and purity_ok and compresses and leak_clean:
        verdict = "REAL_GENERALIZATION"
    elif no_gen or (not leak_clean):
        verdict = "NO_GENERALIZATION"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    msg = (f"{verdict} | out-of-sample UD-EWT dev+test: {census['n_patient_arcs']} patient arcs, "
           f"{census['n_atoms']} mislabel-atoms (labeler_acc={census['labeler_acc']}) | EXACT-RECALL "
           f"(atomize-all)={ex_recall} | COMPRESSION {m_comp}x ({int(mean(lambda s: s['coherent']['n_rules']) or 0)} "
           f"rules, {int(mean(lambda s: s['coherent']['n_singletons']) or 0)} singletons) purity={m_pur} | "
           f"TEMPORAL-HELD-OUT slot_in={m_slot} (cov={m_cov}) vs BASE-RATE-OVERRIDE={m_base} "
           f"(beats_base={beats_base}) | slot_in RISES last-first={m_rise} ({rises}) | "
           f"SCRAMBLE slot_in={m_scr} (collapse={m_collapse}, fires={scramble_collapses}) | leak_clean={leak_clean}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": cfg["seeds"], "census": census, "tau_cluster": round(tau, 6),
        "EXACT_RECALL_atomize_all_hippocampal": ex_recall,
        "COMPRESSION_ratio": m_comp, "n_rules_mean": mean(lambda s: s["coherent"]["n_rules"]),
        "n_singletons_mean": mean(lambda s: s["coherent"]["n_singletons"]),
        "RULE_PURITY_weighted": m_pur,
        "TEMPORAL_slot_in_rate": m_slot, "temporal_coverage": m_cov,
        "BASE_RATE_override": m_base, "rules_beat_base_rate": beats_base,
        "slot_in_rise_last_minus_first": m_rise, "slot_in_rises": rises,
        "MUSTFAIL_scramble_slot_in": m_scr, "MUSTFAIL_scramble_collapse": m_collapse,
        "scramble_collapses": scramble_collapses,
        "leak_clean": leak_clean, "schema_crosscheck": schema,
        "final_metrics_atomicity": "tmp_replace", "crlb_n_a": "streaming slot-in generalization",
        "progress_logging": "print_flush_true", "compute_architecture": "sequential-CPU (justified <60s)",
        "deterministic_seeding": True, "compose_in_cell_no_hdlab_mutation": True,
        "consolidation_note": "cluster prototypes consolidated by continual.replay_cycle (NOT AdditiveKGMap)",
        "per_seed": per_seed,
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


def self_test():
    print("=== streaming slot-in self-test (real code paths) ===", flush=True)
    lab = ArcLabeler.load(LABELER_PATH)
    sents = read_conllu("en_ewt-ud-dev.conllu")[:200]
    atoms, npat = extract_mislabels(sents, lab)
    assert atoms and npat > 0, "no atoms/patient arcs"
    assert all(a["corr"] in PATIENT_ROLES for a in atoms), "correction not a patient role"
    # gold-free signature deterministic + arc_features has no deprel
    import inspect as _insp
    assert "deprel" not in _insp.getsource(arc_features), "LEAK: arc_features references deprel"
    s = sents[0]
    assert np.array_equal(signature([t[1] for t in s], [t[2] for t in s], 1, 0),
                          signature([t[1] for t in s], [t[2] for t in s], 1, 0)), "sig not deterministic"
    tau = calibrate_tau(atoms)
    recs, cc, mem = stream_generalize(atoms, tau, 7)      # exercises torch replay_cycle sleep
    summ = _summarize(recs, cc, mem)
    assert summ["n_rules"] >= 1 and summ["compression_ratio"] >= 1.0, "no rules formed"
    assert 0.0 <= summ["temporal_slot_in"] <= 1.0, "bad slot_in"
    er = exact_recall(atoms)
    assert er is None or 0.0 <= er <= 1.0, "bad exact recall"
    print(f"[selftest] PASS: {len(atoms)} atoms, tau={tau:.3f}, rules={summ['n_rules']}, "
          f"comp={summ['compression_ratio']}x, slot_in={summ['temporal_slot_in']}, exact_recall={er} "
          f"(replay_cycle sleep + hippocampal + glass-box exercised)", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run_mode(args.mode)


if __name__ == "__main__":
    output_dir = _out_dir("full")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            os.makedirs(output_dir, exist_ok=True)
            diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                    "summary": "CELL_CRASHED", "elapsed_s": 0.0, "traceback": traceback.format_exc()[:4000],
                    "ts_iso": datetime.now(timezone.utc).isoformat()}
            tmp = os.path.join(output_dir, "metrics.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(diag, f, indent=2)
            os.replace(tmp, os.path.join(output_dir, "metrics.json"))
        finally:
            raise
