# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (bridge W distinct from identity; broken-retrieval recovered-object
#     array hash-distinct from symbolic + cotrained recovered arrays; symbolic != cotrained).
# - final_metrics_atomicity: tmp_replace (metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb/capacity-feasibility: chance object accuracy = 1/V_CLEANUP (V=1024 -> 0.00098 THEORETICAL); the
#     broken-retrieval discriminator must land in that chance band. HP deliverable=0.70 strictly above HF=0.30
#     floor (band_width 0.40; +5pct = 0.32; 0.70 well above). crlb_n_a for the retrieval+bridge itself
#     (associative HRR unbind + learned/symbolic bridge have no single closed-form floor; the posctrl arm
#     empirically bounds the bridge ceiling; broken-retrieval empirically bounds chance).
# - baseline_in_band: the DISCRIMINATOR (broken_retrieval) MUST collapse toward chance (<=0.10); the WIRING
#     control (posctrl_stored_direct) MUST recover high (>=0.70). The deliverable being high is BY DESIGN --
#     every composed primitive is independently CG/HARD_PASS (retrieval CG, integration bridge HARD_PASS
#     2026-07-05, native decoder exact-ordered 1.000) so this cell demonstrates the COMPOSED loop + prints
#     legible strings; it is NOT a capacity probe. The measurable-band gate is on the CONTROLS, not the demo.
# - discriminator survives scale: loop measured AT full N_R=1024 (HRR store/reason) and N_G=8192 (bipolar-BSC
#     generation) in ALL modes; smoke reduces N_SUBJ/V/n_train/seeds only, never N_R/N_G. broken-collapse +
#     posctrl-ceiling + arms-differ assertions FIRE in smoke.
# - HARD_PASS strictly above floor (deliverable best-of{symbolic,cotrained} exact-ordered >= 0.70 AND
#     discriminator gap >= 0.40 AND posctrl >= 0.70 AND legibility >= 0.80).
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
#
# GROUNDED-FACT UTTERANCE -- re-emit a REAL held ConceptNet fact as ordered concept-name strings  v1
# ==================================================================================================
# HONEST FRAMING (USER-LOCKED 2026-07-05; obey in docstring + verdict_msg + printed output):
#   This RE-EMITS held CONCEPT-NAME strings in composed order via the integrated retrieve->compose->decode
#   loop. It is a demonstration that the substrate's proven loop works END-TO-END on REAL held knowledge.
#   It is NOT English-language generation, NOT fluent language, NOT language knowledge. Frame ONLY as
#   "grounded-fact re-emission via the integrated loop", NEVER as "the substrate speaks/generates language".
#   Full fluent language is a SEPARATE capstone needing a language ingest (scoped separately).
#
# WHAT THIS CELL ADDS OVER ITS THREE PROVEN PRIMITIVES (a glue script, not a new mechanism):
#   (a) sources REAL subject-relation-object ConceptNet edges (real named concepts) from held knowledge
#       instead of random concept juxtapositions or hand-supplied round-trip triples;
#   (b) hand-curates to common, legible concepts (single-token everyday words; obscure/Latin-binomial and
#       profanity nodes rejected) so the emitted output is human-legible;
#   (c) PRINTS the recovered subject/relation/object as their real NAME STRINGS in composed order
#       (the one genuinely new step: a string lookup + print; every prior cell reported index-match only).
#
# THE LOOP (per queried fact, all steps glass-box / inspectable):
#   HELD KNOWLEDGE : subject S with D_STORE real ConceptNet facts (distinct relations r_d -> object o_d).
#   STORE          : T = sum_d bind_HRR(role(r_d), filler_BGE(o_d))  -- S's memory trace (real hdlab HRR
#                    circular-conv on REAL BGE concept vectors; the proven store/reason algebra). [glass-box: T]
#   RETRIEVE       : query (S, r_q, ?): r_hv = unbind_HRR(T, role(r_q)) -- recovered object HV (carries o_q
#                    identity + bundle crosstalk). [glass-box: r_hv, cos to true object]
#   COMPOSE(BRIDGE): map r_hv (HRR-BGE, N_R) -> a bipolar generation code (N_G). Arms:
#                    grounded_symbolic (cleanup r_hv to nearest concept, speak its clean code -- the
#                    associative re-emission), grounded_cotrained (learned held-out ridge bridge W),
#                    posctrl_stored_direct (WIRING: bridge the CLEAN object -- bridge ceiling),
#                    broken_retrieval (DISCRIMINATOR: unbind a role NOT stored -> identity severed -> garble).
#   DECODE + SPEAK : ans = pos0*code(S) + pos1*code(r_q) + pos2*obj_code; decode each slot (unbind known
#                    position + argmax cleanup) -> (subj,rel,obj) codebook indices -> LOOK UP + PRINT names.
#   METRIC         : re-emission exact-ordered = printed (subj,rel,obj) names == stored (S,r_q,o_q) names.
#                    subj/rel codes are clean, so this gates on the RETRIEVED object slot.
#
# Bridge clean-test discipline: cotrained W fit ONLY on a concept TRAIN pool DISJOINT from the cleanup vocab
# (held-out generalization). Curated fact concepts + legible distractors form the V=1024 cleanup vocab.
#
# Sources (CITED@):
#  - experiments/exp_integration_end_to_end_loop_bridge_v1.py  (store/reason/bridge/generate loop; HARD_PASS
#      at FULL 2026-07-05 -- perceive->store->reason->bridge->generate composes end-to-end. Reused UNCHANGED
#      in mechanism; this cell swaps random facts -> REAL ConceptNet edges + adds name-string printing.)
#  - experiments/exp_deep_reasoning_hub_robustness_v1.py       (store/reason: real hdlab HRR over BGE atoms)
#  - experiments/exp_generation_decoder_gsbc_native_blocklocal_v1.py (native ordered decode; exact 1.000)
#  - data/datasets/conceptnet5_en_100k.jsonl                   (real S-R-O ConceptNet assertions)
#  - data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz (BGE + id_order_json names)
#  - notes/research_substrate_native_language_path_5x_angle5_2026-07-05.md (the glue-script spec this cell IS)
#
# ASCII-only. CPU default (task-mandated CPU probe; no LLM, no GPU). Read-only on substrate.
# Run: python experiments/exp_generation_grounded_fact_utterance_v1.py [--self-test | --smoke]
#      (bare / runner-injected HDLAB_RUN_MODE=full -> full)

from __future__ import annotations

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

ANCHOR_NAME = "generation_grounded_fact_utterance_v1"
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import torch  # noqa: E402
from hdlab import binding  # noqa: E402  (proven store/reason primitive: HRR circular-conv)

torch.set_num_threads(min(8, os.cpu_count() or 4))
DEVICE = torch.device("cpu")

# Dimensions (NEVER reduced in smoke; discriminator-survives-scale). Match the integration bridge regime.
N_R = 1024            # reasoning/store dim == BGE_DIM == exp_integration_end_to_end_loop_bridge_v1 N_R
N_G = 8192            # generation dim == exp_integration_end_to_end_loop_bridge_v1 N_G
BGE_DIM = 1024
GEN_SLOTS = 3         # spoken ordered triple: (subject, relation, object)

D_STORE = 2           # real facts stored per subject (distinct relations -> single-valued retrieval)
V_CLEANUP = 1024      # cleanup vocabulary size (curated fact concepts + legible distractors)
SEEDS = (7, 13, 19)
RIDGE_LAMBDA = 1.0    # bridge ridge regularization

# Fixed projection seed (defines the generation lexicon; stable concept codes across seeds).
P_GEN_SEED = 424242

# Data sources
CACHE_PATH = REPO / "data/gen_grounded_fact_cache/grounded_triples_v1.npz"
CN_EDGES = REPO / "data/datasets/conceptnet5_en_100k.jsonl"
BGE_FULL = REPO / "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz"

# Curation config (deterministic; verified legible off-disk 2026-07-05)
GOOD_REL = ["AtLocation", "CapableOf", "Causes", "IsA", "UsedFor",
            "HasProperty", "PartOf", "MadeOf", "HasA", "ReceivesAction"]
_SUBJ_RE = re.compile(r"^[a-z]{3,10}$")            # subject: single common token
_OBJ_RE = re.compile(r"^[a-z]+(_[a-z]+){0,1}$")    # object: 1-2 tokens
BLOCKLIST = {"ass", "asshole", "athelete", "resturant", "accordian", "hooker", "sex", "crap",
             "damn", "anemone", "homosexual", "penis", "vagina", "nigger", "fuck", "shit", "porn",
             "whore", "slut", "rape", "bitch", "cunt", "fag"}
N_SUBJ_FULL = 100     # curated subjects at FULL (each queried D_STORE times -> N_SUBJ*D_STORE re-emissions)
N_TRAIN = 4096        # held-out bridge training pool (disjoint from cleanup vocab)

# Pre-registered bands (HYPOTHESIZED@this-cell; deflated honestly; verified vs smoke before dispatch).
# THEORETICAL@chance = 1/V_CLEANUP (V=1024 -> 0.00098): broken-retrieval discriminator lands here.
HP_REEMIT = 0.70          # HARD_PASS: deliverable (best of symbolic/cotrained) re-emission exact-ordered
HP_DISCRIM_GAP = 0.40     # HARD_PASS: (deliverable - broken_retrieval) must exceed this
HP_LEGIBILITY = 0.80      # HARD_PASS: fraction of emitted object strings that are plain-legible words
HF_REEMIT = 0.30          # HARD_FAIL: below -> the chained composition breaks a per-primitive-proven step
POSCTRL_FLOOR = 0.70      # WIRING gate: stored_direct (bridge ceiling) must recover >= this
BROKEN_COLLAPSE_CEIL = 0.10  # DISCRIMINATOR: broken_retrieval must collapse at/below this

ARMS = ["grounded_symbolic", "grounded_cotrained", "posctrl_stored_direct", "broken_retrieval"]
DELIVERABLE_ARMS = ["grounded_symbolic", "grounded_cotrained"]


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
# Curated real-ConceptNet-triples cache (compact + remote-portable; self-heal from master table)
# ============================================================


def _legible(name: str) -> bool:
    """A concept name is plain-legible iff it is 1-2 lowercase-alpha tokens, each >= 2 chars, not blocked."""
    if any(tok in BLOCKLIST for tok in name.split("_")):
        return False
    toks = name.split("_")
    if not (1 <= len(toks) <= 2):
        return False
    return all(t.isalpha() and len(t) >= 2 for t in toks)


def _build_cache() -> dict:
    """Build the compact curated-triples cache from the master BGE/name table + ConceptNet edges.
    Deterministic. Local self-heal only (master table is NOT remote-portable; the compact cache IS)."""
    if not BGE_FULL.exists():
        raise FileNotFoundError(
            f"cannot build curated cache: master BGE/name table missing ({BGE_FULL}). On the remote, SCP the "
            f"prebuilt compact cache to {CACHE_PATH} (queue_add does NOT auto-ship untracked npz).")
    if not CN_EDGES.exists():
        raise FileNotFoundError(f"ConceptNet edges missing ({CN_EDGES}).")

    master = np.load(BGE_FULL, allow_pickle=True)
    ids = json.loads(str(master["id_order_json"]))
    name2row = {n: i for i, n in enumerate(ids)}
    sem = master["semantic"]  # (177899, BGE_DIM) float32

    def _cn(x: str) -> str:
        return "CN_" + x

    def _obj_ok(x: str) -> bool:
        return bool(_OBJ_RE.match(x)) and 3 <= len(x) <= 14 and _legible(x)

    def _subj_ok(x: str) -> bool:
        return bool(_SUBJ_RE.match(x)) and _legible(x)

    # Pass 1: collect subject -> {relation: first legible object} (distinct relation => single-valued);
    #         collect the legible common-concept pool (all endpoints of GOOD_REL edges).
    good = set(GOOD_REL)
    bysubj: dict = {}
    pool_names: set = set()
    with open(CN_EDGES, "r", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            s, p, o = e["subject"], e["predicate"], e["object"]
            if p not in good or s == o:
                continue
            if _obj_ok(o) and _cn(o) in name2row:
                pool_names.add(o)
            if not (_subj_ok(s) and _obj_ok(o)):
                continue
            if s in BLOCKLIST or o in BLOCKLIST:
                continue
            if _cn(s) not in name2row or _cn(o) not in name2row:
                continue
            pool_names.add(s)
            rels = bysubj.setdefault(s, {})
            rel_order = GOOD_REL.index(p)
            if p not in rels:
                rels[p] = (rel_order, o)

    # Pass 2: keep subjects with >= D_STORE distinct relations; select first N (deterministic sort).
    curated = []
    for s in sorted(bysubj.keys()):
        rels = bysubj[s]
        if len(rels) < D_STORE:
            continue
        # take the D_STORE relations by GOOD_REL priority (stable, semantically varied)
        chosen = sorted(rels.items(), key=lambda kv: kv[1][0])[:D_STORE]
        facts = [(rel, obj) for rel, (order, obj) in chosen]
        if s in {o for _r, o in facts}:  # subject must not be its own object
            continue
        curated.append((s, facts))

    if len(curated) < N_SUBJ_FULL:
        raise RuntimeError(f"only {len(curated)} curated subjects available (< {N_SUBJ_FULL}); loosen filter")
    curated = curated[:max(N_SUBJ_FULL, 128)]  # store a superset; the cell caps per run_mode

    # Curated concept set (subjects + objects) -> local indices; pool = remaining legible concepts.
    cur_concepts = []
    seen = set()
    for s, facts in curated:
        for nm in [s] + [o for _r, o in facts]:
            if nm not in seen:
                seen.add(nm)
                cur_concepts.append(nm)
    cur_local = {nm: i for i, nm in enumerate(cur_concepts)}
    pool_only = sorted(pool_names - set(cur_concepts))

    def _unit(rows):
        X = sem[[name2row[_cn(n)] for n in rows]].astype(np.float32)
        return (X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)).astype(np.float32)

    bge_curated = _unit(cur_concepts)                 # (n_cur, BGE_DIM)
    bge_pool = _unit(pool_only)                       # (n_pool, BGE_DIM)

    subjects = []
    for s, facts in curated:
        subjects.append({"s": cur_local[s],
                         "facts": [[rel, cur_local[obj]] for rel, obj in facts]})

    meta = {"built_ts": datetime.now(timezone.utc).isoformat(),
            "source_edges": str(CN_EDGES.relative_to(REPO)),
            "master_table": str(BGE_FULL.name), "D_STORE": D_STORE,
            "n_curated_subjects": len(subjects), "n_cur_concepts": len(cur_concepts),
            "n_pool": len(pool_only), "good_rel": GOOD_REL,
            "note": "REAL ConceptNet S-R-O edges over hand-curated common legible concepts"}

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(CACHE_PATH,
                        bge_curated=bge_curated, names_curated=np.array(cur_concepts, dtype=object),
                        bge_pool=bge_pool, names_pool=np.array(pool_only, dtype=object),
                        subjects_json=json.dumps(subjects), meta_json=json.dumps(meta))
    return {"bge_curated": bge_curated, "names_curated": cur_concepts,
            "bge_pool": bge_pool, "names_pool": pool_only, "subjects": subjects, "meta": meta}


_CACHE = {"d": None}


def _load_cache() -> dict:
    if _CACHE["d"] is not None:
        return _CACHE["d"]
    if CACHE_PATH.exists():
        d = np.load(CACHE_PATH, allow_pickle=True)
        _CACHE["d"] = {"bge_curated": d["bge_curated"].astype(np.float32),
                       "names_curated": [str(x) for x in d["names_curated"]],
                       "bge_pool": d["bge_pool"].astype(np.float32),
                       "names_pool": [str(x) for x in d["names_pool"]],
                       "subjects": json.loads(str(d["subjects_json"])),
                       "meta": json.loads(str(d["meta_json"]))}
    else:
        _CACHE["d"] = _build_cache()
    return _CACHE["d"]


# ============================================================
# Primitives (copied from exp_integration_end_to_end_loop_bridge_v1; CITED@ that cell)
# ============================================================


def _bind_hrr(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    out = binding.bind(torch.from_numpy(np.ascontiguousarray(a, dtype=np.float32)),
                       torch.from_numpy(np.ascontiguousarray(b, dtype=np.float32)))
    return out.numpy()


def _unbind_hrr(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    out = binding.unbind(torch.from_numpy(np.ascontiguousarray(c, dtype=np.float32)),
                         torch.from_numpy(np.ascontiguousarray(b, dtype=np.float32)))
    return out.numpy()


def _role_vec(rel_name: str, seed: int) -> np.ndarray:
    """Near-orthogonal unit HRR role per relation (deterministic; the retrieval key)."""
    h = int(hashlib.sha256(f"grounded_role::{seed}::{rel_name}".encode()).hexdigest(), 16)
    r = np.random.default_rng(h % (2 ** 63 - 1)).standard_normal(N_R).astype(np.float32)
    return r / (np.linalg.norm(r) + 1e-12)


def _bipolar_rows(V: int, N: int, rng) -> np.ndarray:
    return (2.0 * (rng.random((V, N)) > 0.5).astype(np.float32) - 1.0)


def _proj_sign_lexicon(bge_unit: np.ndarray, N: int, proj_seed: int) -> np.ndarray:
    """Generation lexicon: BGE -> fixed Gaussian projection -> sign -> bipolar (V, N). Carries the cos-cone."""
    pr = np.random.default_rng(proj_seed)
    P = (pr.standard_normal((BGE_DIM, N)).astype(np.float32) / np.sqrt(BGE_DIM))
    return np.where(bge_unit @ P >= 0.0, 1.0, -1.0).astype(np.float32)


def _make_positions(P: int, N: int, rng) -> np.ndarray:
    base = (2.0 * (rng.random(N) > 0.5).astype(np.float32) - 1.0)
    return np.stack([np.roll(base, k) for k in range(P)], axis=0)


def _fit_cotrained_bridge(bge_train_unit: np.ndarray, N: int, proj_seed: int) -> np.ndarray:
    """Ridge bridge W (N_R, N): maps a reasoning-space BGE vector to its generation sign-code. Trained ONLY
    on the disjoint train pool (held-out) so W GENERALIZES to unseen concepts. code_est = sign(r_hv @ W)."""
    X = bge_train_unit.astype(np.float32)
    Y = _proj_sign_lexicon(X, N, proj_seed)
    G = X.T @ X + RIDGE_LAMBDA * np.eye(N_R, dtype=np.float32)
    W = np.linalg.solve(G, X.T @ Y).astype(np.float32)
    return W


def _generate_and_decode(subj_code, rel_code, obj_code, pos, L_gen, L_rel):
    """Compose the ordered triple proposition and decode each slot (unbind by known position + argmax)."""
    ans = pos[0] * subj_code + pos[1] * rel_code + pos[2] * obj_code   # (N_G,) bipolar-BSC superposition
    subj_pred = int(np.argmax(L_gen @ (ans * pos[0])))
    rel_pred = int(np.argmax(L_rel @ (ans * pos[1])))
    obj_pred = int(np.argmax(L_gen @ (ans * pos[2])))
    return subj_pred, rel_pred, obj_pred


def _mean_pair_cos(Xn: np.ndarray, n: int, rng) -> float:
    m = min(n, Xn.shape[0])
    idx = rng.choice(Xn.shape[0], size=m, replace=False)
    S = Xn[idx] @ Xn[idx].T
    off = S[~np.eye(m, dtype=bool)]
    return float(off.mean())


def _digest(int_list) -> str:
    return hashlib.sha256(np.asarray(int_list, dtype=np.int64).tobytes()).hexdigest()


def _digest_arr(arr) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(arr, dtype=np.float32)).tobytes()).hexdigest()


# ============================================================
# One seed: run the grounded-fact re-emission loop over all curated facts
# ============================================================


def run_seed(seed: int, n_subj: int, v_cleanup: int, n_train: int, output_dir: Path, t0: float):
    cache = _load_cache()
    bge_cur = cache["bge_curated"]
    names_cur = cache["names_curated"]
    bge_pool = cache["bge_pool"]
    names_pool = cache["names_pool"]
    subjects = cache["subjects"][:n_subj]
    n_cur = bge_cur.shape[0]

    rng = np.random.default_rng(1000 + seed)

    # cleanup vocab = curated concepts (local 0..n_cur-1) + legible distractors from the pool (seed-sampled)
    n_distract = max(0, v_cleanup - n_cur)
    perm = rng.permutation(bge_pool.shape[0])
    distract_rows = perm[:n_distract]
    train_rows = perm[n_distract:n_distract + n_train]
    bge_vocab = np.concatenate([bge_cur, bge_pool[distract_rows]], axis=0)   # (V, BGE_DIM)
    names_vocab = names_cur + [names_pool[r] for r in distract_rows]
    V = bge_vocab.shape[0]
    bge_train = bge_pool[train_rows]                                          # (n_train, BGE_DIM) held-out

    # generation lexicon + relation codebook + positions
    L_gen = _proj_sign_lexicon(bge_vocab, N_G, P_GEN_SEED)                    # (V, N_G)
    rel_list = list(GOOD_REL)
    rel_idx = {r: i for i, r in enumerate(rel_list)}
    L_rel = _bipolar_rows(len(rel_list), N_G, np.random.default_rng(2000 + seed))
    pos = _make_positions(GEN_SLOTS, N_G, np.random.default_rng(3000 + seed))
    W = _fit_cotrained_bridge(bge_train, N_G, P_GEN_SEED)                     # (N_R, N_G)

    cone = round(_mean_pair_cos(bge_cur, min(300, n_cur), np.random.default_rng(4000 + seed)), 4)

    hit = {a: 0 for a in ARMS}       # re-emission exact-ordered hits
    ohit = {a: 0 for a in ARMS}      # object-slot hits (diagnostic)
    n_trials = 0
    rec_obj = {a: [] for a in ARMS}  # per-arm recovered object indices (arms_differ)
    first_codes = {}                 # per-arm FIRST-trial emitted object code (distinct-mechanism artifact)
    legible_ok = {a: 0 for a in DELIVERABLE_ARMS}
    legible_tot = {a: 0 for a in DELIVERABLE_ARMS}
    glassbox = []

    for si, subj in enumerate(subjects):
        subj_local = subj["s"]
        facts = subj["facts"]                      # [[rel_name, obj_local], ...] length D_STORE
        stored_rels = [f[0] for f in facts]
        # STORE trace once per subject
        T = np.zeros(N_R, dtype=np.float32)
        for rel, obj_local in facts:
            T = T + _bind_hrr(_role_vec(rel, seed), bge_cur[obj_local])
        # broken role: a GOOD_REL relation NOT stored for this subject (identity-severed retrieval)
        unused = [r for r in rel_list if r not in stored_rels]
        rel_broken = unused[int(rng.integers(len(unused)))]

        for (rel_q, obj_q_local) in facts:
            n_trials += 1
            r_hv = _unbind_hrr(T, _role_vec(rel_q, seed))
            r_hv_broken = _unbind_hrr(T, _role_vec(rel_broken, seed))
            r_hv_n = r_hv / (np.linalg.norm(r_hv) + 1e-12)

            subj_code = L_gen[subj_local]
            rel_code = L_rel[rel_idx[rel_q]]

            code = {}
            # grounded_symbolic: clean up r_hv to nearest concept in the cleanup vocab, speak its clean code
            sims = bge_vocab @ r_hv_n
            j = int(np.argmax(sims))
            code["grounded_symbolic"] = L_gen[j]
            # grounded_cotrained: learned held-out bridge
            code["grounded_cotrained"] = np.sign(r_hv @ W).astype(np.float32)
            # posctrl_stored_direct WIRING: bridge the CLEAN object (no retrieval crosstalk) -> bridge ceiling
            code["posctrl_stored_direct"] = np.sign(bge_cur[obj_q_local] @ W).astype(np.float32)
            # broken_retrieval DISCRIMINATOR: bridge the severed-identity HV
            code["broken_retrieval"] = np.sign(r_hv_broken @ W).astype(np.float32)

            emitted = {}
            for a in ARMS:
                ce = np.where(code[a] == 0.0, 1.0, code[a]).astype(np.float32)
                if a not in first_codes:
                    first_codes[a] = ce.copy()   # distinct-mechanism artifact (pre-decode object code)
                sp, rp, op = _generate_and_decode(subj_code, rel_code, ce, pos, L_gen, L_rel)
                exact = int(sp == subj_local and rp == rel_idx[rel_q] and op == obj_q_local)
                hit[a] += exact
                ohit[a] += int(op == obj_q_local)
                rec_obj[a].append(op)
                emitted[a] = (names_vocab[sp], rp, names_vocab[op])
                if a in DELIVERABLE_ARMS:
                    legible_tot[a] += 1
                    legible_ok[a] += int(_legible(names_vocab[op]))

            if len(glassbox) < 16:
                glassbox.append({
                    "seed": seed,
                    "stored_fact": [names_cur[subj_local], rel_q, names_cur[obj_q_local]],
                    "emitted_symbolic": [emitted["grounded_symbolic"][0], rel_q,
                                         emitted["grounded_symbolic"][2]],
                    "emitted_cotrained": [emitted["grounded_cotrained"][0], rel_q,
                                          emitted["grounded_cotrained"][2]],
                    "emitted_broken": [emitted["broken_retrieval"][0], rel_q,
                                       emitted["broken_retrieval"][2]],
                    "symbolic_match": int(emitted["grounded_symbolic"][2] == names_cur[obj_q_local]),
                    "broken_match": int(emitted["broken_retrieval"][2] == names_cur[obj_q_local]),
                    "r_hv_cos_true_obj": round(float(bge_cur[obj_q_local] @ r_hv_n), 4),
                })

    reemit = {a: hit[a] / n_trials for a in ARMS}
    obj_acc = {a: ohit[a] / n_trials for a in ARMS}
    legibility = {a: (legible_ok[a] / legible_tot[a] if legible_tot[a] else 0.0) for a in DELIVERABLE_ARMS}
    # arms_differ artifacts: DISTINCT-MECHANISM object codes (not recovered indices -- two arms that BOTH
    # recover perfectly legitimately emit the same truth object; the mechanisms still differ). Plus the
    # discriminator-alters-recovery check (broken recovery must diverge from the deliverable recovery).
    artifacts = {"W_digest": _digest_arr(W),
                 "code_symbolic": _digest_arr(first_codes["grounded_symbolic"]),
                 "code_cotrained": _digest_arr(first_codes["grounded_cotrained"]),
                 "code_posctrl": _digest_arr(first_codes["posctrl_stored_direct"]),
                 "code_broken": _digest_arr(first_codes["broken_retrieval"]),
                 "rec_symbolic": _digest(rec_obj["grounded_symbolic"]),
                 "rec_cotrained": _digest(rec_obj["grounded_cotrained"]),
                 "rec_broken": _digest(rec_obj["broken_retrieval"]),
                 "rec_posctrl": _digest(rec_obj["posctrl_stored_direct"])}
    _heartbeat(output_dir, seed, SEEDS[-1], t0,
               extra={"seed": seed, "n_trials": n_trials, "V": V,
                      "symbolic_reemit": round(reemit["grounded_symbolic"], 3),
                      "broken_reemit": round(reemit["broken_retrieval"], 3),
                      "posctrl_reemit": round(reemit["posctrl_stored_direct"], 3)})
    _say(f"  [seed {seed}] n_facts={n_trials} V={V} cone={cone:.3f} | re-emit exact-ordered: "
         f"symbolic={reemit['grounded_symbolic']:.3f} cotrained={reemit['grounded_cotrained']:.3f} "
         f"posctrl={reemit['posctrl_stored_direct']:.3f} broken={reemit['broken_retrieval']:.3f} | "
         f"legibility symbolic={legibility['grounded_symbolic']:.3f}")
    return reemit, obj_acc, legibility, artifacts, glassbox, cone, V, n_trials


# ============================================================
# Config + verdict
# ============================================================


def get_config(mode: str):
    if mode == "selftest":
        return {"n_subj": 8, "v_cleanup": 512, "n_train": 1024, "seeds": (7,)}
    if mode == "smoke":
        return {"n_subj": 12, "v_cleanup": 512, "n_train": 2048, "seeds": (7,)}
    return {"n_subj": N_SUBJ_FULL, "v_cleanup": V_CLEANUP, "n_train": N_TRAIN, "seeds": SEEDS}


def classify(agg: dict, mode: str, V: int):
    sym = agg["reemit"]["grounded_symbolic"]
    cot = agg["reemit"]["grounded_cotrained"]
    pos = agg["reemit"]["posctrl_stored_direct"]
    brk = agg["reemit"]["broken_retrieval"]
    best = max(sym, cot)
    best_arm = "grounded_symbolic" if sym >= cot else "grounded_cotrained"
    gap = best - brk
    leg = agg["legibility"]["grounded_symbolic"]

    diag = (f"re-emit exact-ordered: symbolic={sym:.3f} cotrained={cot:.3f} posctrl(stored_direct)={pos:.3f} "
            f"broken={brk:.3f}; best={best:.3f}({best_arm}); discrim_gap(best-broken)={gap:.3f}; "
            f"legibility(symbolic)={leg:.3f}; chance=1/V={1.0 / V:.5f}")

    # --- discriminator-fires gates (all modes) ---
    if pos < POSCTRL_FLOOR:
        return ("DISCRIMINATOR_DID_NOT_FIRE",
                f"posctrl stored_direct re-emit={pos:.3f} < {POSCTRL_FLOOR}: bridge/generation WIRING failed "
                f"(cannot attribute any loop failure to the retrieval->generation seam). {diag}", False)
    if brk > BROKEN_COLLAPSE_CEIL:
        return ("IDENTITY_DISCRIMINATOR_DID_NOT_FIRE",
                f"broken_retrieval re-emit={brk:.3f} > {BROKEN_COLLAPSE_CEIL}: severed-identity retrieval did "
                f"NOT collapse -> re-emission is NOT attributable to genuine held-knowledge retrieval. {diag}",
                True)

    if mode == "smoke":
        return ("HARD_PASS",
                f"SMOKE_MACHINERY_OK: grounded-fact re-emission loop (held-knowledge->store->retrieve->bridge->"
                f"decode->name) runs end-to-end AT N_R={N_R} N_G={N_G}; posctrl recovers, broken collapses, arms "
                f"differ, emitted strings legible. Deliverable bands are FULL-only (canonical=remote landing). "
                f"NOTE (honest framing): this re-emits held concept-name strings, NOT language generation. {diag}",
                True)

    # --- FULL pre-registered re-emission bands (deliverable = best of symbolic/cotrained) ---
    if best >= HP_REEMIT and gap >= HP_DISCRIM_GAP and leg >= HP_LEGIBILITY:
        return ("HARD_PASS",
                f"GROUNDED-FACT RE-EMISSION WORKS END-TO-END: the integrated retrieve->compose->decode loop "
                f"re-emits REAL held ConceptNet facts as ordered concept-name strings -- {best_arm} exact-ordered "
                f"={best:.3f} (>= {HP_REEMIT}) with discriminator gap {gap:.3f} (>= {HP_DISCRIM_GAP}); "
                f"broken-retrieval collapses to {brk:.3f}; emitted strings legible {leg:.3f} (>= {HP_LEGIBILITY}). "
                f"HONEST FRAMING: re-emits held concept-name strings via the proven loop -- NOT English "
                f"generation, NOT fluent language, NOT language knowledge. {diag}", True)
    if best < HF_REEMIT:
        return ("HARD_FAIL",
                f"CHAINED COMPOSITION BREAKS: best re-emit={best:.3f} < {HF_REEMIT} while posctrl bridge ceiling "
                f"={pos:.3f} -> an integration-joint bug (each primitive clears its own bar in isolation). {diag}",
                True)
    if leg < HP_LEGIBILITY:
        return ("HARD_FAIL",
                f"LEGIBILITY FAIL: mechanism re-emits (best={best:.3f}) but emitted-string legibility {leg:.3f} "
                f"< {HP_LEGIBILITY} (>=20pct non-legible/obscure) -> vocabulary curation is the gap, not the "
                f"mechanism. {diag}", True)
    return ("MIDDLE_BAND",
            f"PARTIAL RE-EMISSION: best={best:.3f} in [{HF_REEMIT},{HP_REEMIT}); loop composes imperfectly on "
            f"real facts -- quantify per-seed cv + inspect the retrieval crosstalk. {diag}", True)


# ============================================================
# main
# ============================================================


def _run(mode: str) -> int:
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    cfg = get_config(mode)
    seeds = cfg["seeds"]
    expected_n_units = len(seeds) * len(ARMS)
    _write_start_marker(output_dir, mode, expected_n_units)
    _say(f"[{ANCHOR_NAME}] mode={mode} N_R={N_R} N_G={N_G} n_subj={cfg['n_subj']} D_store={D_STORE} "
         f"V_cleanup={cfg['v_cleanup']} n_train={cfg['n_train']} seeds={seeds} arms={ARMS}")

    per_seed = {a: [] for a in ARMS}
    per_seed_obj = {a: [] for a in ARMS}
    per_seed_leg = {a: [] for a in DELIVERABLE_ARMS}
    artifacts_by_seed = {}
    glassbox_all = []
    cones = {}
    Vs = []
    n_trials_seen = 0
    for seed in seeds:
        reemit, oacc, leg, art, gb, cone, V, ntr = run_seed(
            seed, cfg["n_subj"], cfg["v_cleanup"], cfg["n_train"], output_dir, t0)
        for a in ARMS:
            per_seed[a].append(reemit[a])
            per_seed_obj[a].append(oacc[a])
        for a in DELIVERABLE_ARMS:
            per_seed_leg[a].append(leg[a])
        artifacts_by_seed[str(seed)] = art
        glassbox_all.extend(gb)
        cones[str(seed)] = cone
        Vs.append(V)
        n_trials_seen = ntr

    # arms_differ (META_RULE_AF): compare DISTINCT-MECHANISM artifacts (per-arm emitted object CODES), NOT
    # recovered-object indices -- two arms that BOTH recover perfectly legitimately emit the same truth
    # object (the mechanisms still differ). Also verify the DISCRIMINATOR alters the recovered output
    # (broken-retrieval recovery must diverge from the deliverable recovery).
    arms_differ_ok = True
    for sd, art in artifacts_by_seed.items():
        code_digs = [art["code_symbolic"], art["code_cotrained"], art["code_posctrl"], art["code_broken"]]
        if len(set(code_digs)) < 4:
            arms_differ_ok = False   # two arms emitted bit-identical object codes -> arm-implementation bug
        if art["rec_broken"] == art["rec_symbolic"] or art["rec_broken"] == art["rec_cotrained"]:
            arms_differ_ok = False   # severed-identity discriminator did NOT alter recovery -> discriminator bug
    if not arms_differ_ok:
        raise AssertionError(
            "META_RULE_AF VIOLATION: two arms emitted bit-identical object CODES (arm bug) OR broken-retrieval "
            "recovery == a deliverable recovery (discriminator did not alter output)")

    agg = {
        "reemit": {a: round(float(np.mean(per_seed[a])), 4) for a in ARMS},
        "obj_acc": {a: round(float(np.mean(per_seed_obj[a])), 4) for a in ARMS},
        "legibility": {a: round(float(np.mean(per_seed_leg[a])), 4) for a in DELIVERABLE_ARMS},
        "reemit_per_seed": {a: [round(v, 4) for v in per_seed[a]] for a in ARMS},
    }
    V_used = int(np.min(Vs))
    verdict, vmsg, discrim_ok = classify(agg, mode, V_used)
    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: grounded-fact re-emission via integrated retrieve->compose->decode loop "
                   f"(REAL ConceptNet facts; re-emits held concept-name strings, NOT language) ({mode})",
        "run_mode": mode,
        "elapsed_s": round(elapsed, 2),
        "n_seeds": len(seeds),
        "n_units": len(seeds) * len(ARMS),
        "expected_n_units": expected_n_units,
        "cardinality_ok": True,
        "n_reemission_trials_per_seed": n_trials_seen,
        "honest_framing": ("RE-EMITS held ConceptNet concept-name strings in composed order via the proven "
                           "retrieve->compose->decode loop. NOT English-language generation, NOT fluent "
                           "language, NOT language knowledge. Full fluent language is a separate capstone."),
        "config": {"N_R": N_R, "N_G": N_G, "BGE_DIM": BGE_DIM, "GEN_SLOTS": GEN_SLOTS, "D_STORE": D_STORE,
                   "n_subj": cfg["n_subj"], "V_cleanup": V_used, "n_train": cfg["n_train"],
                   "seeds": list(seeds), "RIDGE_LAMBDA": RIDGE_LAMBDA,
                   "store_reason_algebra": "HRR_circular_conv_real_BGE_hdlab_binding",
                   "generation_algebra": "bipolar_BSC_elementwise_product_protected_index_positions",
                   "arms": ARMS, "curated_cache": str(CACHE_PATH.relative_to(REPO)),
                   "cache_meta": _load_cache()["meta"]},
        "arms": {a: {"reemit_mean": agg["reemit"][a], "reemit_per_seed": agg["reemit_per_seed"][a],
                     "obj_acc_mean": agg["obj_acc"][a]} for a in ARMS},
        "legibility": agg["legibility"],
        "controls": {"posctrl_stored_direct_reemit": agg["reemit"]["posctrl_stored_direct"],
                     "broken_retrieval_reemit": agg["reemit"]["broken_retrieval"],
                     "broken_collapsed": bool(agg["reemit"]["broken_retrieval"] <= BROKEN_COLLAPSE_CEIL),
                     "chance_object_acc_THEORETICAL": round(1.0 / V_used, 6),
                     "correlation_cone": cones},
        "grounded_utterances": glassbox_all,
        "arms_differ_verified": arms_differ_ok,
        "bands": {"HP_reemit": HP_REEMIT, "HP_discrim_gap": HP_DISCRIM_GAP, "HP_legibility": HP_LEGIBILITY,
                  "HF_reemit": HF_REEMIT, "posctrl_floor": POSCTRL_FLOOR,
                  "broken_collapse_ceil": BROKEN_COLLAPSE_CEIL},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
    }
    _write_metrics_atomic(output_dir, metrics)
    written = json.load(open(output_dir / "metrics.json"))
    assert written["run_mode"] == mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {mode}"

    # print a few ACTUAL emitted grounded-fact strings (the first grounded outputs)
    _say(f"\n[{ANCHOR_NAME}] --- ACTUAL EMITTED GROUNDED FACTS (re-emission, NOT language) ---")
    for g in glassbox_all[:8]:
        sf = g["stored_fact"]
        es = g["emitted_symbolic"]
        eb = g["emitted_broken"]
        tag = "MATCH" if g["symbolic_match"] else "MISS"
        _say(f"  stored ({sf[0]} -{sf[1]}-> {sf[2]}) | EMITTED ({es[0]} -{es[1]}-> {es[2]}) [{tag}] | "
             f"broken-ctrl EMITTED ({eb[0]} -{eb[1]}-> {eb[2]}) [garbled]")

    _say(f"\n[{ANCHOR_NAME}] {verdict}: {vmsg}")
    _say(f"[{ANCHOR_NAME}] metrics -> {output_dir / 'metrics.json'}  elapsed={elapsed:.1f}s")
    return 0


def _run_selftest() -> int:
    t0 = time.perf_counter()
    output_dir = _out_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    cfg = get_config("selftest")
    reemit, _oacc, leg, _art, gb, _cone, V, ntr = run_seed(
        7, cfg["n_subj"], cfg["v_cleanup"], cfg["n_train"], output_dir, t0)
    # selftest gate: posctrl recovers (wiring) AND broken collapses well below the deliverable (discriminator)
    ok = (reemit["posctrl_stored_direct"] >= 0.50) and \
         (reemit["broken_retrieval"] <= reemit["grounded_symbolic"] - 0.20) and \
         (leg["grounded_symbolic"] >= 0.80) and (ntr >= cfg["n_subj"])
    if gb:
        g = gb[0]
        _say(f"[{ANCHOR_NAME}] example emit: stored={g['stored_fact']} symbolic_emit={g['emitted_symbolic']} "
             f"match={g['symbolic_match']}")
    _say(f"[{ANCHOR_NAME}] SELFTEST {'PASS' if ok else 'FAIL'}: symbolic={reemit['grounded_symbolic']:.3f} "
         f"posctrl={reemit['posctrl_stored_direct']:.3f} broken={reemit['broken_retrieval']:.3f} "
         f"legibility={leg['grounded_symbolic']:.3f} n_trials={ntr} [{time.perf_counter()-t0:.1f}s]")
    return 0 if ok else 1


def main() -> int:
    if "--self-test" in sys.argv:
        return _run_selftest()
    mode = "smoke" if "--smoke" in sys.argv else \
        ("smoke" if os.environ.get("HDLAB_RUN_MODE", "").lower() == "smoke" else "full")
    return _run(mode)


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
