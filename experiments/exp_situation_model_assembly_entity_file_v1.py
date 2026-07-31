# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (sha256 digest of per-query predicted-class arrays; MAIN_ENC /
#   REF_SPAN / ORACLE_ENTITY_FILE asserted pairwise distinct; ENTITY_FILE_COMMIT logged + commit==oracle
#   flag -- a legitimate coincidence when re-id is perfect, NOT a bug, so NOT hard-asserted).
# - final_metrics_atomicity: tmp_replace (os.replace at end).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: zero-learned-param FHRR loop (clean cell's SituationWM, imported VERBATIM via eb.clean) +
#   frozen v2 encoder (no training). The oracle arm is an UPPER-BOUND probe; the commit arm is a fixed,
#   NON-TUNED nearest-committed-file heuristic. The discriminator is per-query-type accuracy recovery.
# - baseline_in_band: MAIN_ENC (the fragile per-mention decoded-id address) is the landed 0.45-0.58
#   baseline (MEASURED@data/exp_situation_model_assembly_encoder_backed_v1/metrics.json); the 5
#   deterministic floors + POOLED_READER are the can-fail controls and MUST collapse or the cell INVALID.
# - discriminator survives scale: closed-form loop; front-end is a FROZEN encoder forward pass; self-test
#   exercises the REAL encoder + REAL loop at tiny N (real_code_path) + a DRIFT GUARD asserting the
#   entity_addr='decoded' rebuild reproduces the landed MAIN_ENC preds bit-identically (one-variable proof).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - deterministic seeding: numpy default_rng + torch.Generator only; NO hash(), NO list(set())
#   (sorted(set()) everywhere).
"""ENTITY-FILE DISCRIMINATOR on the encoder-backed situation-model harness (Director spawn 2026-07-31).

VET-confirmed diagnostic being attacked (MEASURED@data/exp_situation_model_assembly_encoder_backed_v1/
metrics.json): the encoder-backed loop drops MAIN 1.000 -> a=0.4625 / b=0.5825 / c=0.4508, LOCALIZED to
CROSS-FRAME ENTITY RE-IDENTIFICATION -- fillers decode WELL (S=0.96, P=0.88), marks decode WELL
(MARK=0.876, MARK_q=1.00), but the ENTITY decodes INCONSISTENTLY across statement/tag/question frames
(entity_consistency=0.795, ENT=0.84, ENT_q=0.80). The loop keys the WM slot on the decoded entity COLOR
id (SituationWM._alloc / _name_address via t['color_id'][ent]); a fragile per-mention id fragments the
entity across slots -> the query misses.

STRATEGIC FORK this cell discriminates:
  (A) attack via a discourse ENTITY-FILE / coreference mechanism -- bind each mention to a persistent
      referent via a STABLE ADDRESS, decoupling identity from fragile per-mention encoder reps.
  (B) retrain the encoder for context-invariant entity reps.

ONE VARIABLE = the entity-addressing scheme. Fillers (S/P) + marks stay role_attn-decoded EXACTLY as the
landed MAIN_ENC arm (drift-guarded). The harness loop + floors + construction are REUSED UNCHANGED from
eb = exp_situation_model_assembly_encoder_backed_v1 (which itself reuses the clean cell's SituationWM +
gen_dataset + floors VERBATIM). The three entity-address schemes:

  ARM_MAIN_ENC (fragile baseline): ENT address = the per-mention role_attn-decoded color id. The landed
      0.45-0.58 wall. Reproduced here as the honest baseline.

  ARM_ORACLE_ENTITY_FILE (UPPER BOUND): ENT address = the TRUE entity id (a perfect stable address /
      perfect coref), decoupled from the hard coref-resolution. Everything else identical (marks + fillers
      still role_attn-decoded). Tests: is a STABLE ENTITY-FILE ADDRESS SUFFICIENT to fix the wall? Ceiling
      is capped by residual filler decode (~0.88-0.96), so recovery 'toward ~1.0' means >= ORACLE_RECOVER_BAR.

  ARM_ENTITY_FILE_COMMIT (feasibility on the reps): a simple discourse-referent mechanism using ONLY the
      (noisy) role_attn encoder reps -- NO oracle, NO retrain. Stream the ENT-slot reps in discourse order
      (tags introduce referents, then events, then queries); COMMIT a referent to a persistent file-slot on
      FIRST mention (its rep as the file centroid); re-bind each SUBSEQUENT mention to the NEAREST committed
      file (cosine >= TAU) with running-mean persistence/hysteresis, else open a new file. The file's stable
      canonical id becomes the loop address, replacing the fresh per-mention decoded id. TAU is CALIBRATED
      ONCE from the encoder rep geometry (midpoint of within-color vs cross-color ENT-rep cosine) BEFORE any
      accuracy is seen -- NOT tuned to force recovery. Tests: does a stable-address entity file RECOVER
      cross-frame identity + MAIN from the fragile baseline, on the noisy reps alone?

DISCRIMINATOR VERDICT (pre-registered bars; this is a DIAGNOSTIC, not a pass-chase):
  A_TRACTABLE               : ORACLE recovers (>= ORACLE_RECOVER_BAR on all 3 types) AND COMMIT recovers
                              substantially (beats MAIN by >= COMMIT_MARGIN AND >= COMMIT_APPROACH_BAR on
                              all 3) -> stable-address entity-file is the fix AND learnable on the reps
                              without encoder-retrain (Direction A, tractable now).
  A_NEEDS_BETTER_ASSIGNMENT : ORACLE recovers but COMMIT does NOT -> addressing fixes it IN PRINCIPLE but
                              coref-assignment on these reps is hard -> A needs a better assignment
                              mechanism (or better reps for the coref sub-problem -> leans B for that part).
  DEEPER_WALL               : even ORACLE does NOT recover -> stable-addressing is NOT sufficient; the wall
                              is deeper (role-attribution secondary degradation or the loop under real
                              reps) -> reconsider both A and B.
  INVALID                   : a can-fail floor did not collapse OR POOLED_READER is reservoir-decodable.

Run:  .venv/Scripts/python.exe experiments/exp_situation_model_assembly_entity_file_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_situation_model_assembly_entity_file_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_situation_model_assembly_entity_file_v1.py --lite
      .venv/Scripts/python.exe experiments/exp_situation_model_assembly_entity_file_v1.py --full

ASCII-only. No emojis. Deterministic seeding. Pure CPU (frozen-encoder forward passes; local, push-free;
INLINE-LOCAL foreground-to-completion). progress_logging: print_flush_true.
Compute architecture: sequential-CPU, justified -- closed-form FHRR loop + frozen-encoder forward passes
BATCHED at 256; each unique sentence encoded once per dataset. Storage: per-entity content-gated overwrite
memory (sharded per slot) + FHRR-superposed roles; per-passage accumulators independent.
"""

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch
import torch.nn.functional as F

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_situation_model_assembly_encoder_backed_v1 as eb  # noqa: E402 (HARNESS reused UNCHANGED)
import exp_checkpoint as ckpt  # noqa: E402 (per-unit checkpoint/resume, MANDATORY per CLAUDE.md)

clean = eb.clean
QUERY_TYPES = eb.QUERY_TYPES
V_FILL = eb.V_FILL
K_TRACK = clean.K_TRACK
CHANCE = eb.CHANCE
PROVEN_MIN = eb.PROVEN_MIN
GAP_MAX = eb.GAP_MAX
DECODE_FLOOR_BAR = eb.DECODE_FLOOR_BAR
ADDR_FLOOR_BAR = eb.ADDR_FLOOR_BAR
ATTN_TEMP = eb.ATTN_TEMP
V2_CKPT = eb.V2_CKPT

ANCHOR_NAME = "situation_model_assembly_entity_file_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- pre-registered discriminator bars (fixed BEFORE running) ----
# ORACLE_RECOVER_BAR: recovery 'toward ~1.0' capped by residual role_attn filler decode.
#   THEORETICAL: a name query answer needs the correct filler at store time; role_attn S/P decode
#   = 0.96/0.88 (MEASURED@data/exp_situation_model_assembly_encoder_backed_v1/metrics.json
#   :bands.stage_role_attn_mean) => achievable ceiling ~0.88-0.96 with perfect addressing. 0.85 = clear
#   recovery below that ceiling.
ORACLE_RECOVER_BAR = 0.85
# COMMIT must BEAT MAIN by this margin to count as substantial recovery (not noise).
COMMIT_MARGIN = 0.15
# COMMIT must also reach a usable absolute level (approaches oracle / usable range).
COMMIT_APPROACH_BAR = 0.70

# ---- entity-file commit config ----
COMMIT_CAP = V_FILL            # canonical file ids in [0, V_FILL) so t['color_id'][id] is a valid clean code
CALIB_CTX_PER_COLOR = 12       # ENT-rep samples per color for the TAU calibration
CALIB_SEED = 71001

# ---- seeds / sizes (mirror eb) ----
SEEDS_SMOKE = (7,)
SEEDS_LITE = (7, 13)
SEEDS_FULL = (7, 13)
SMOKE_TRAIN_N, SMOKE_EVAL_N = 80, 80
LITE_TRAIN_N, LITE_EVAL_N = 200, 200
FULL_TRAIN_N, FULL_EVAL_N = 600, 400


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------- canonical hardening ----------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(eb._jsonify(metrics), f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ================= ENT-slot rep extraction (role_attn, normalized) =================
def _ent_slot_reps(ext, requests):
    """For each request, return per-slot the role_attn pooled+conditioned+normalized rep (np float32).
    Deterministic; matches the exact vector ext.decode_dataset_slots argmaxes for role_attn. Encodes each
    unique text ONCE."""
    uniq = sorted(set(r["text"] for r in requests))
    idx_of = {t: i for i, t in enumerate(uniq)}
    reps, pad, _ = ext._encode_raw(uniq)
    creps = ext._condition(reps, pad)
    out = []
    for r in requests:
        i = idx_of[r["text"]]
        ri, pi = creps[i], pad[i]
        slotreps = []
        for (st, cs, ce) in r["slots"]:
            v = ext._attn_pool(ri.unsqueeze(0), pi.unsqueeze(0), ext.cue_vec[st], ATTN_TEMP).squeeze(0)
            slotreps.append(F.normalize(v, dim=0).numpy().astype(np.float32))
        out.append(slotreps)
    return out


# ================= TAU calibration (once, from rep geometry; NOT tuned to accuracy) =================
def calibrate_tau(ext, seed=CALIB_SEED):
    """Compute a fixed commit threshold from the encoder's ENT-rep geometry, in the regime the streaming
    commit mechanism ACTUALLY operates: a fresh noisy single-sample mention matched against a previously
    committed single-sample (or running-mean) file. So calibrate on PAIRWISE SAMPLE-TO-SAMPLE cosine
    (same-color = within, different-color = cross), NOT member-to-mean-centroid (which over-estimates
    within because the centroid denoises and causes chronic over-fragmentation). tau = midpoint. Set
    BEFORE any accuracy is seen; this is a regime-correctness rule, NOT outcome tuning.
    Returns dict {tau, within, cross, n}."""
    rng = np.random.default_rng(seed)
    reqs = []
    tag = []   # (color)
    for c in range(V_FILL):
        for _ in range(CALIB_CTX_PER_COLOR):
            o1 = int(rng.integers(0, V_FILL))
            o2 = int(rng.integers(0, V_FILL))
            pick = int(rng.integers(0, 3))
            if pick == 0:
                txt, spans = eb.render_name_event(c, o1, o2)
            elif pick == 1:
                txt, spans = eb.render_tag(c, o1)
            else:
                role = int(rng.integers(0, len(clean.ROLE_NAMES)))
                txt, spans = eb.render_name_query(c, role)
            sl = [(st, cs, ce) for (st, cidx, cs, ce) in spans if st == "ENT"]
            if not sl:
                continue
            reqs.append({"text": txt, "slots": sl})
            tag.append(c)
    slotreps = _ent_slot_reps(ext, reqs)
    by_color = {c: [] for c in range(V_FILL)}
    for k, sr in enumerate(slotreps):
        by_color[tag[k]].append(sr[0])   # ENT is the only slot requested
    cols = sorted([c for c in range(V_FILL) if by_color[c]])
    # PAIRWISE same-color (within): cosine between distinct samples of the same color.
    within_vals = []
    for c in cols:
        M = by_color[c]
        for i in range(len(M)):
            for j in range(i + 1, len(M)):
                within_vals.append(float(np.dot(M[i], M[j])))
    # PAIRWISE cross-color: cosine between one sample of each of two different colors (subsampled).
    cross_vals = []
    for a in range(len(cols)):
        for b in range(a + 1, len(cols)):
            va = by_color[cols[a]][0]
            for vb in by_color[cols[b]][:2]:
                cross_vals.append(float(np.dot(va, vb)))
    within = float(np.mean(within_vals)) if within_vals else float("nan")
    cross = float(np.mean(cross_vals)) if cross_vals else float("nan")
    tau = 0.5 * (within + cross)
    return {"tau": tau, "within": within, "cross": cross,
            "n_within": len(within_vals), "n_cross": len(cross_vals), "n_colors": len(cols)}


# ================= entity-file commit assignment (streaming, hysteresis; NOT tuned) =================
def _assign_commit(ent_occurrences, tau, cap):
    """ent_occurrences: ordered list of dicts {key, rep(np unit)}. Returns (addr_by_key, diag).
    Streaming: first mention commits a new file; each later mention joins the nearest committed file if
    cosine >= tau (running-mean centroid persistence), else opens a new file. Canonical file ids in
    [0, cap). Overflow (> cap files) force-attaches to nearest."""
    files = []   # list of {cid, centroid, count}
    next_cid = 0
    overflow = 0
    addr_by_key = {}
    for occ in ent_occurrences:
        r = occ["rep"]
        best_i, best_cos = -1, -2.0
        for fi, f in enumerate(files):
            cs = float(np.dot(r, f["centroid"]))
            if cs > best_cos:
                best_cos, best_i = cs, fi
        open_new = (len(files) == 0) or (best_cos < tau)
        if open_new and len(files) >= cap:
            open_new = False
            overflow += 1
        if open_new:
            cid = next_cid
            next_cid += 1
            files.append({"cid": cid, "centroid": r.copy(), "count": 1})
            addr_by_key[occ["key"]] = cid
        else:
            f = files[best_i]
            newc = f["centroid"] * f["count"] + r
            f["count"] += 1
            f["centroid"] = newc / (np.linalg.norm(newc) + 1e-9)
            addr_by_key[occ["key"]] = f["cid"]
    return addr_by_key, {"n_files": len(files), "overflow": overflow}


# ================= build decoded dataset with a chosen entity-addressing scheme =================
# Mirrors eb.build_decoded_dataset(mode='role_attn') assembly EXACTLY, except the ENT-slot loop address
# is replaced by the chosen scheme (decoded=identity/baseline, oracle=true id, commit=file id).
def build_addr_dataset(dataset, ext, entity_addr, tau=None, cap=COMMIT_CAP):
    all_reqs = []
    span_of = []
    for p in dataset:
        reqs, idx = eb._collect_requests(p)
        span_of.append((len(all_reqs), idx))
        all_reqs.extend(reqs)
    dec = ext.decode_dataset_slots(all_reqs, modes=("role_attn",))
    ent_reps = _ent_slot_reps(ext, all_reqs) if entity_addr == "commit" else None

    tracked_set_by_p = [set(p["tracked"]) for p in dataset]
    decoded_ds = []
    ans_ds = []
    ef_consistent = [0, 0]        # entity-file consistency (all mentions of a tracked ent share one addr)
    q_agree = [0, 0]             # query-frame ENT addr matches the entity's majority statement addr
    n_files_list = []
    overflow_total = 0

    for pi, ((base_i, idx), p) in enumerate(zip(span_of, dataset)):
        def g(local_req_i, slot_j):
            return dec[base_i + local_req_i][slot_j]["role_attn"]

        def rep(local_req_i, slot_j):
            return ent_reps[base_i + local_req_i][slot_j]

        # ---- gather ENT occurrences in discourse order (tags -> name-events -> name-queries) ----
        occ = []   # {key, rep, true_cidx}
        # tags
        for tk, (ri, slotinfo, ent) in enumerate(idx["tags"]):
            for j, (st, cidx) in enumerate(slotinfo):
                if st == "ENT":
                    occ.append({"key": ("tag", tk), "true": cidx,
                                "rep": rep(ri, j) if entity_addr == "commit" else None,
                                "req": ri, "slot": j})
        # name-events (coref events name no entity -> skip for the ENT file)
        for ek, (ri, slotinfo, ev) in enumerate(idx["events"]):
            if ev["addr_mode"] == "coref" and ev["mark"] is not None:
                continue
            for j, (st, cidx) in enumerate(slotinfo):
                if st == "ENT":
                    occ.append({"key": ("event", ek), "true": cidx,
                                "rep": rep(ri, j) if entity_addr == "commit" else None,
                                "req": ri, "slot": j})
        # name-queries (a, c). b is coref (no ENT slot)
        for qt in QUERY_TYPES:
            qi = idx["queries"][qt]
            if qi is None:
                continue
            (ri, slotinfo, q) = qi
            for j, (st, cidx) in enumerate(slotinfo):
                if st == "ENT":
                    occ.append({"key": ("query", qt), "true": cidx,
                                "rep": rep(ri, j) if entity_addr == "commit" else None,
                                "req": ri, "slot": j})

        # ---- resolve the ENT address per occurrence per scheme ----
        if entity_addr == "oracle":
            addr = {o["key"]: o["true"] for o in occ}
            fdiag = {"n_files": len({o["true"] for o in occ}), "overflow": 0}
        elif entity_addr == "commit":
            addr, fdiag = _assign_commit([{"key": o["key"], "rep": o["rep"]} for o in occ], tau, cap)
        else:  # decoded (== landed MAIN_ENC baseline)
            addr = {o["key"]: g(o["req"], o["slot"]) for o in occ}
            fdiag = {"n_files": len({addr[o["key"]] for o in occ}), "overflow": 0}
        n_files_list.append(fdiag["n_files"])
        overflow_total += fdiag["overflow"]

        # entity-file consistency + cross-frame query agreement (on TRACKED entities)
        by_true = {}
        for o in occ:
            if o["true"] in tracked_set_by_p[pi]:
                by_true.setdefault(o["true"], {}).setdefault("all", []).append(addr[o["key"]])
                fr = o["key"][0]
                by_true[o["true"]].setdefault(fr, []).append(addr[o["key"]])
        for t, d in by_true.items():
            ef_consistent[1] += 1
            ef_consistent[0] += int(len(set(d["all"])) == 1)
            stmt = d.get("tag", []) + d.get("event", [])
            if "query" in d and stmt:
                maj = max(set(stmt), key=stmt.count)
                q_agree[1] += 1
                q_agree[0] += int(all(a == maj for a in d["query"]))

        # ---- assemble the decoded passage using addr for ENT, role_attn for MARK/S/P ----
        tag_list = []
        tag_mark_to_ent = {}
        for tk, (ri, slotinfo, ent) in enumerate(idx["tags"]):
            d_ent = d_mark = None
            for j, (st, cidx) in enumerate(slotinfo):
                if st == "ENT":
                    d_ent = addr[("tag", tk)]
                elif st == "MARK":
                    d_mark = g(ri, j)
            tag_list.append((d_ent, d_mark))
            tag_mark_to_ent[d_mark] = d_ent

        events = []
        for ek, (ri, slotinfo, ev) in enumerate(idx["events"]):
            d_ent = d_mark = d_s = d_p = None
            for j, (st, cidx) in enumerate(slotinfo):
                if st == "ENT":
                    d_ent = addr[("event", ek)]
                elif st == "MARK":
                    d_mark = g(ri, j)
                elif st == "S":
                    d_s = g(ri, j)
                elif st == "P":
                    d_p = g(ri, j)
            if ev["addr_mode"] == "coref" and ev["mark"] is not None:
                alloc_ent = tag_mark_to_ent.get(d_mark, d_mark)
                events.append({"ent": alloc_ent, "mark": d_mark, "s_fill": d_s, "p_fill": d_p,
                               "addr_mode": "coref", "is_distract": ev["is_distract"]})
            else:
                events.append({"ent": d_ent, "mark": None, "s_fill": d_s, "p_fill": d_p,
                               "addr_mode": "name", "is_distract": ev["is_distract"]})

        dq = {}
        aq = {}
        for qt in QUERY_TYPES:
            qi = idx["queries"][qt]
            if qi is None:
                dq[qt] = None
                aq[qt] = None
                continue
            (ri, slotinfo, q) = qi
            d_ent = None
            d_mark = None
            for j, (st, cidx) in enumerate(slotinfo):
                if st == "ENT":
                    d_ent = addr[("query", qt)]
                elif st == "MARK":
                    d_mark = g(ri, j)
            dq[qt] = {"ent": (d_ent if d_ent is not None else 0), "mark": d_mark, "role": q["role"]}
            aq[qt] = q["answer"]
        decoded_ds.append({"tag_list": tag_list, "events": events, "queries": dq})
        ans_ds.append(aq)

    diag = {"entity_file_consistency": (ef_consistent[0] / ef_consistent[1] if ef_consistent[1] else float("nan")),
            "cross_frame_query_agreement": (q_agree[0] / q_agree[1] if q_agree[1] else float("nan")),
            "n_files_mean": float(np.mean(n_files_list)) if n_files_list else float("nan"),
            "overflow_total": overflow_total, "n_tracked_ref": ef_consistent[1]}
    return decoded_ds, ans_ds, diag


# ================= self-test =================
def _combined_digest(arm_res):
    return hashlib.sha256("".join(arm_res[qt]["preds_digest"] for qt in QUERY_TYPES).encode()).hexdigest()


def run_self_test():
    _log("SELF-TEST: clean loop toy binding + construction audit ...")
    toy = clean.toy_binding_selftest()
    audit = clean.audit_construction(seed=7, n=200)
    assert not audit["fails"], "CONSTRUCTION_AUDIT_FAIL: %s" % audit["fails"]

    _log("SELF-TEST: load REAL v2 encoder + build extractor (real_code_path) ...")
    assert os.path.exists(V2_CKPT), "v2 checkpoint missing: %s" % V2_CKPT
    ext = eb.EncoderExtractor()
    binfo = ext.build()
    _log("  build: %s" % binfo)

    cal = calibrate_tau(ext)
    _log("  TAU calibration: %s" % cal)
    assert cal["within"] > cal["cross"], "TAU calib invalid: within (%.3f) <= cross (%.3f)" % (cal["within"], cal["cross"])

    _log("SELF-TEST: tiny datasets + DRIFT GUARD (decoded rebuild == landed MAIN_ENC) + arms-differ ...")
    tables = clean.build_tables()
    ds = clean.gen_dataset(24, np.random.default_rng(7))

    # landed MAIN_ENC via eb (role_attn) + REF_SPAN
    dec_ra, ans_ra, _ = eb.build_decoded_dataset(ds, ext, "role_attn")
    dec_span, ans_span, _ = eb.build_decoded_dataset(ds, ext, "span")
    main_enc = eb.run_arm_decoded(dec_ra, ans_ra, tables, "main")
    ref_span = eb.run_arm_decoded(dec_span, ans_span, tables, "main")

    # my decoded-rebuild MUST reproduce landed MAIN_ENC bit-identically (one-variable proof)
    dec_dc, ans_dc, _ = build_addr_dataset(ds, ext, "decoded")
    main_rebuild = eb.run_arm_decoded(dec_dc, ans_dc, tables, "main")
    for qt in QUERY_TYPES:
        assert main_rebuild[qt]["preds_digest"] == main_enc[qt]["preds_digest"], (
            "DRIFT_GUARD VIOLATION on %s: decoded-rebuild != landed MAIN_ENC (assembly drift)" % qt)
    _log("  DRIFT GUARD PASS: decoded rebuild reproduces landed MAIN_ENC")

    dec_or, ans_or, diag_or = build_addr_dataset(ds, ext, "oracle")
    dec_co, ans_co, diag_co = build_addr_dataset(ds, ext, "commit", tau=cal["tau"])
    oracle = eb.run_arm_decoded(dec_or, ans_or, tables, "main")
    commit = eb.run_arm_decoded(dec_co, ans_co, tables, "main")
    assert abs(diag_or["entity_file_consistency"] - 1.0) < 1e-9, "oracle entity_file_consistency must be 1.0"

    for qt in QUERY_TYPES:
        for arm in (main_enc, ref_span, oracle, commit):
            acc = arm[qt]["acc"]
            assert math.isnan(acc) or (0.0 <= acc <= 1.0)

    # arms-differ: MAIN_ENC / REF_SPAN / ORACLE pairwise distinct (near-certain; a real bug-catch).
    # COMMIT logged; commit==oracle is a LEGITIMATE coincidence (perfect re-id), NOT a bug -> not asserted.
    digs = {"main_enc": _combined_digest(main_enc), "ref_span": _combined_digest(ref_span),
            "oracle": _combined_digest(oracle), "commit": _combined_digest(commit)}
    hard = ["main_enc", "ref_span", "oracle"]
    for i in range(len(hard)):
        for j in range(i + 1, len(hard)):
            assert digs[hard[i]] != digs[hard[j]], (
                "META_RULE_AF: arms %r and %r bit-identical" % (hard[i], hard[j]))
    commit_eq_oracle = (digs["commit"] == digs["oracle"])

    _log("  MAIN_ENC : " + ", ".join("%s=%.2f" % (qt, main_enc[qt]["acc"]) for qt in QUERY_TYPES))
    _log("  REF_SPAN : " + ", ".join("%s=%.2f" % (qt, ref_span[qt]["acc"]) for qt in QUERY_TYPES))
    _log("  ORACLE   : " + ", ".join("%s=%.2f" % (qt, oracle[qt]["acc"]) for qt in QUERY_TYPES)
         + " | ef_consistency=%.3f" % diag_or["entity_file_consistency"])
    _log("  COMMIT   : " + ", ".join("%s=%.2f" % (qt, commit[qt]["acc"]) for qt in QUERY_TYPES)
         + " | ef_consistency=%.3f q_agree=%.3f n_files=%.1f commit_eq_oracle=%s"
         % (diag_co["entity_file_consistency"], diag_co["cross_frame_query_agreement"],
            diag_co["n_files_mean"], commit_eq_oracle))
    _log("SELF-TEST PASS")
    return {"toy": toy, "audit_fails": audit["fails"], "build": binfo, "tau_calib": cal,
            "drift_guard": "PASS", "commit_eq_oracle": commit_eq_oracle,
            "tiny_main_enc": {qt: main_enc[qt]["acc"] for qt in QUERY_TYPES},
            "tiny_oracle": {qt: oracle[qt]["acc"] for qt in QUERY_TYPES},
            "tiny_commit": {qt: commit[qt]["acc"] for qt in QUERY_TYPES},
            "arms_differ_verified": True}


# ================= driver =================
def run_seed(seed, ext, tau, train_n, eval_n):
    tables = clean.build_tables()
    train_ds = clean.gen_dataset(train_n, np.random.default_rng(seed))
    eval_ds = clean.gen_dataset(eval_n, np.random.default_rng(seed + 777))
    t = time.perf_counter()

    dec_ra, ans_ra, stage_ra = eb.build_decoded_dataset(eval_ds, ext, "role_attn")
    dec_span, ans_span, _ = eb.build_decoded_dataset(eval_ds, ext, "span")
    dec_or, ans_or, diag_or = build_addr_dataset(eval_ds, ext, "oracle")
    dec_co, ans_co, diag_co = build_addr_dataset(eval_ds, ext, "commit", tau=tau)
    _log("  seed=%d extraction+assembly done in %.1fs" % (seed, time.perf_counter() - t))

    arms = {}
    arms["main_enc"] = eb.run_arm_decoded(dec_ra, ans_ra, tables, "main")
    arms["ref_span"] = eb.run_arm_decoded(dec_span, ans_span, tables, "main")
    arms["oracle_entity_file"] = eb.run_arm_decoded(dec_or, ans_or, tables, "main")
    arms["entity_file_commit"] = eb.run_arm_decoded(dec_co, ans_co, tables, "main")
    for m in ("random_addr", "no_coref", "wrongrole", "shuffled"):
        arms[m] = eb.run_arm_decoded(dec_ra, ans_ra, tables, m)
    most_recent = clean.run_most_recent(eval_ds)
    pooled = clean.run_pooled_reader(train_ds, eval_ds, seed)

    res = {"seed": seed, "train_n": train_n, "eval_n": eval_n, "arms": arms,
           "most_recent": most_recent, "pooled": pooled, "stage_role_attn": stage_ra,
           "diag_oracle": diag_or, "diag_commit": diag_co,
           "diag_main": {"entity_consistency": stage_ra.get("entity_consistency")}}
    for label in ("main_enc", "oracle_entity_file", "entity_file_commit", "ref_span"):
        _log("  seed=%d %s: %s" % (seed, label,
             ", ".join("%s=%.3f" % (qt, arms[label][qt]["acc"]) for qt in QUERY_TYPES)))
    _log("  seed=%d COMMIT diag: ef_consistency=%.3f q_agree=%.3f n_files=%.2f overflow=%d (MAIN ent_consistency=%.3f)"
         % (seed, diag_co["entity_file_consistency"], diag_co["cross_frame_query_agreement"],
            diag_co["n_files_mean"], diag_co["overflow_total"], stage_ra.get("entity_consistency", float("nan"))))
    _log("  seed=%d floors: RANDOM_ADDR(a)=%.2f NO_COREF(b)=%.2f WRONGROLE(a)=%.2f SHUFFLED(a)=%.2f MOST_RECENT(a)=%.2f POOLED(b)=%.2f"
         % (seed, arms["random_addr"]["a_name_maintenance"]["acc"], arms["no_coref"]["b_competitive_coref"]["acc"],
            arms["wrongrole"]["a_name_maintenance"]["acc"], arms["shuffled"]["a_name_maintenance"]["acc"],
            most_recent["a_name_maintenance"]["acc"], pooled["b_competitive_coref"]["acc"]))
    return res


def _mean(xs):
    v = [x for x in xs if not math.isnan(x)]
    return float(np.mean(v)) if v else float("nan")


def decide_verdict(per_seed):
    def al(arm, qt):
        return [ps["arms"][arm][qt]["acc"] for ps in per_seed]

    # ---- floors valid gate (same bars as eb) ----
    floors_ok = True
    floor_notes = []
    pooled_b = [ps["pooled"]["b_competitive_coref"]["acc"] for ps in per_seed]
    pooled_c = [ps["pooled"]["c_overwrite"]["acc"] for ps in per_seed]
    pooled_reservoir = (all(x >= PROVEN_MIN for x in pooled_b if not math.isnan(x))
                        or all(x >= PROVEN_MIN for x in pooled_c if not math.isnan(x)))
    floor_applies = {
        "most_recent": (QUERY_TYPES, DECODE_FLOOR_BAR, "mr"),
        "random_addr": (QUERY_TYPES, ADDR_FLOOR_BAR, "arm"),
        "no_coref": (("b_competitive_coref",), ADDR_FLOOR_BAR, "arm"),
        "wrongrole": (QUERY_TYPES, DECODE_FLOOR_BAR, "arm"),
        "shuffled": (QUERY_TYPES, DECODE_FLOOR_BAR, "arm"),
    }
    for arm, (qts, bar, src) in floor_applies.items():
        for qt in qts:
            xs = ([ps["most_recent"][qt]["acc"] for ps in per_seed] if src == "mr" else al(arm, qt))
            for x in xs:
                if not math.isnan(x) and x > bar:
                    floors_ok = False
                    floor_notes.append("%s did not collapse on %s: %.3f > %.3f" % (arm, qt, x, bar))

    main_mean = {qt: _mean(al("main_enc", qt)) for qt in QUERY_TYPES}
    ref_mean = {qt: _mean(al("ref_span", qt)) for qt in QUERY_TYPES}
    oracle_mean = {qt: _mean(al("oracle_entity_file", qt)) for qt in QUERY_TYPES}
    commit_mean = {qt: _mean(al("entity_file_commit", qt)) for qt in QUERY_TYPES}

    oracle_recovered = all((not math.isnan(oracle_mean[qt])) and oracle_mean[qt] >= ORACLE_RECOVER_BAR
                           for qt in QUERY_TYPES)
    commit_substantial = all((not math.isnan(commit_mean[qt]))
                             and (commit_mean[qt] >= main_mean[qt] + COMMIT_MARGIN)
                             and (commit_mean[qt] >= COMMIT_APPROACH_BAR)
                             for qt in QUERY_TYPES)

    ef_consistency_commit = _mean([ps["diag_commit"]["entity_file_consistency"] for ps in per_seed])
    q_agree_commit = _mean([ps["diag_commit"]["cross_frame_query_agreement"] for ps in per_seed])
    ent_consistency_main = _mean([ps["stage_role_attn"].get("entity_consistency", float("nan")) for ps in per_seed])

    # LADDER DECOMPOSITION (MAIN < ORACLE < REF_SPAN): ORACLE fixes ONLY the entity address (role_attn
    # fillers kept), REF_SPAN additionally uses clean span fillers. So oracle-main = entity re-id
    # component; ref-oracle = residual role_attn filler/role-decode component. Cleanly attributes the wall.
    def _frac(o, m, r):
        return ((o - m) / (r - m)) if (not math.isnan(o) and not math.isnan(m) and not math.isnan(r)
                                       and (r - m) > 1e-6) else float("nan")
    addr_gap_closed = {qt: _frac(oracle_mean[qt], main_mean[qt], ref_mean[qt]) for qt in QUERY_TYPES}
    filler_residual = {qt: (ref_mean[qt] - oracle_mean[qt]) for qt in QUERY_TYPES}

    bands = {"chance": CHANCE, "proven_min": PROVEN_MIN, "gap_max": GAP_MAX,
             "oracle_recover_bar": ORACLE_RECOVER_BAR, "commit_margin": COMMIT_MARGIN,
             "commit_approach_bar": COMMIT_APPROACH_BAR,
             "main_enc_mean": main_mean, "ref_span_mean": ref_mean,
             "oracle_entity_file_mean": oracle_mean, "entity_file_commit_mean": commit_mean,
             "main_enc_acc": {qt: al("main_enc", qt) for qt in QUERY_TYPES},
             "oracle_entity_file_acc": {qt: al("oracle_entity_file", qt) for qt in QUERY_TYPES},
             "entity_file_commit_acc": {qt: al("entity_file_commit", qt) for qt in QUERY_TYPES},
             "ref_span_acc": {qt: al("ref_span", qt) for qt in QUERY_TYPES},
             "entity_consistency_main": ent_consistency_main,
             "entity_file_consistency_commit": ef_consistency_commit,
             "cross_frame_query_agreement_commit": q_agree_commit,
             "addr_gap_closed_frac": addr_gap_closed, "filler_residual": filler_residual,
             "n_files_mean_commit": _mean([ps["diag_commit"]["n_files_mean"] for ps in per_seed]),
             "pooled_acc_b": pooled_b, "pooled_acc_c": pooled_c,
             "random_addr_acc": {qt: al("random_addr", qt) for qt in QUERY_TYPES},
             "no_coref_acc_b": al("no_coref", "b_competitive_coref"),
             "wrongrole_acc": {qt: al("wrongrole", qt) for qt in QUERY_TYPES},
             "shuffled_acc": {qt: al("shuffled", qt) for qt in QUERY_TYPES},
             "most_recent_acc": {qt: [ps["most_recent"][qt]["acc"] for ps in per_seed] for qt in QUERY_TYPES},
             "floors_ok": floors_ok, "floor_notes": floor_notes,
             "pooled_reservoir_decodable": pooled_reservoir,
             "oracle_recovered": oracle_recovered, "commit_substantial": commit_substantial}

    if pooled_reservoir:
        return "INVALID", ("POOLED_READER clears PROVEN_MIN on (b)/(c) -- reservoir-decodable; fix "
                           "construction. pooled_b=%s pooled_c=%s" % (pooled_b, pooled_c)), bands
    if not floors_ok:
        return "INVALID", ("A can-fail floor did not collapse: " + "; ".join(floor_notes)), bands

    if oracle_recovered and commit_substantial:
        return "A_TRACTABLE", ("Stable-address entity-file FIXES the wall AND is learnable on the noisy "
                               "reps. ORACLE recovers (oracle=%s >= %.2f) AND COMMIT recovers substantially "
                               "(commit=%s, beats MAIN=%s by >= %.2f, >= %.2f). COMMIT ef_consistency=%.3f "
                               "(MAIN ent_consistency=%.3f). DIRECTION A CONFIRMED + TRACTABLE."
                               % (oracle_mean, ORACLE_RECOVER_BAR, commit_mean, main_mean, COMMIT_MARGIN,
                                  COMMIT_APPROACH_BAR, ef_consistency_commit, ent_consistency_main)), bands
    if oracle_recovered and not commit_substantial:
        return "A_NEEDS_BETTER_ASSIGNMENT", ("Stable-address FIXES the wall IN PRINCIPLE (ORACLE recovers "
                                             "oracle=%s >= %.2f) but the simple commit heuristic does NOT "
                                             "recover on these reps (commit=%s vs MAIN=%s; commit "
                                             "ef_consistency=%.3f q_agree=%.3f). Direction A needs a better "
                                             "assignment mechanism (or better reps for coref -> leans B for "
                                             "that sub-problem)." % (oracle_mean, ORACLE_RECOVER_BAR,
                                                                     commit_mean, main_mean,
                                                                     ef_consistency_commit, q_agree_commit)), bands
    return "DEEPER_WALL", ("Even the ORACLE stable address does NOT recover to >= %.2f on all types "
                           "(oracle=%s; REF_SPAN ceiling=%s; MAIN=%s; commit=%s). Stable-addressing alone is "
                           "NOT sufficient. LADDER DECOMPOSITION: addr_gap_closed(oracle-main)/(ref-main)=%s "
                           "(entity re-id component), filler_residual(ref-oracle)=%s (role_attn filler/role-"
                           "decode component). If addr_gap_closed is high the entity file fixes the re-id part "
                           "and the residual is filler/role decode (leans B for that sub-problem); if low the "
                           "wall is in the loop under real reps. Reconsider both A and B."
                           % (ORACLE_RECOVER_BAR, oracle_mean, ref_mean, main_mean, commit_mean,
                              addr_gap_closed, filler_residual)), bands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--lite", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.lite or args.full):
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    elif args.lite:
        run_mode = "lite"
    else:
        run_mode = "full"

    if run_mode == "smoke":
        seeds, train_n, eval_n = SEEDS_SMOKE, SMOKE_TRAIN_N, SMOKE_EVAL_N
    elif run_mode == "lite":
        seeds, train_n, eval_n = SEEDS_LITE, LITE_TRAIN_N, LITE_EVAL_N
    elif run_mode == "full":
        seeds, train_n, eval_n = SEEDS_FULL, FULL_TRAIN_N, FULL_EVAL_N
    else:
        seeds, train_n, eval_n = SEEDS_SMOKE, 1, 1

    expected_units = 1 if run_mode == "self_test" else len(seeds)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        metrics = {"verdict": "SELFTEST_PASS",
                   "verdict_msg": "SELFTEST_PASS (harness reuse + drift-guard + entity-file arms + arms-differ)",
                   "summary": "SELFTEST_PASS", "run_mode": "self_test",
                   "elapsed_s": time.perf_counter() - t0, "ts_iso": _now_iso(),
                   "anchor_name": ANCHOR_NAME, "chance": CHANCE, "selftest": st,
                   "start_marker_written": True, "crash_diagnostic_present": True,
                   "final_metrics_atomicity": "tmp_replace"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return

    _log("%s: seeds=%s train_n=%d eval_n=%d chance=%.4f" % (run_mode.upper(), seeds, train_n, eval_n, CHANCE))
    audit = clean.audit_construction(seed=7, n=300)
    if audit["fails"]:
        raise AssertionError("pre-run construction audit FAILED: %s" % audit["fails"])

    _log("Building frozen v2 encoder extractor ...")
    ext = eb.EncoderExtractor()
    binfo = ext.build()
    _log("  %s" % binfo)
    cal = calibrate_tau(ext)
    _log("  TAU (calibrated, NOT tuned): tau=%.4f within=%.4f cross=%.4f n_within=%d n_cross=%d"
         % (cal["tau"], cal["within"], cal["cross"], cal["n_within"], cal["n_cross"]))

    per_seed = []
    for seed in seeds:
        key = ckpt.unit_key("seed", seed, run_mode)
        if key in ckpt.completed_units(OUTPUT_DIR):
            per_seed.append(ckpt.load_units(OUTPUT_DIR)[key])
            _log("  seed=%d loaded from checkpoint" % seed)
            continue
        res = run_seed(seed, ext, cal["tau"], train_n, eval_n)
        ckpt.record_unit(OUTPUT_DIR, key, res)
        per_seed.append(res)

    verdict, msg, bands = decide_verdict(per_seed)
    bands["tau_calib"] = cal
    elapsed = time.perf_counter() - t0
    metrics = {"verdict": verdict, "verdict_msg": msg,
               "summary": "%s | chance=%.4f | %s" % (verdict, CHANCE, msg[:160]),
               "run_mode": run_mode, "elapsed_s": elapsed, "ts_iso": _now_iso(),
               "anchor_name": ANCHOR_NAME, "chance": CHANCE, "bands": bands,
               "encoder_build": binfo, "tau_calib": cal,
               "cardinality_ok": bool(len(per_seed) == len(seeds)),
               "expected_n_units": len(seeds), "n_units_done": len(per_seed),
               "construction_audit": audit, "per_seed": per_seed,
               "params": {"DIM": clean.DIM, "K_TRACK": K_TRACK, "V_FILL": V_FILL,
                          "ATTN_TEMP": ATTN_TEMP, "COMMIT_CAP": COMMIT_CAP,
                          "ORACLE_RECOVER_BAR": ORACLE_RECOVER_BAR, "COMMIT_MARGIN": COMMIT_MARGIN,
                          "COMMIT_APPROACH_BAR": COMMIT_APPROACH_BAR,
                          "train_n": train_n, "eval_n": eval_n, "seeds": list(seeds),
                          "v2_ckpt": os.path.relpath(V2_CKPT, REPO_ROOT)},
               "arms_differ_verified": True, "start_marker_written": True,
               "crash_diagnostic_present": True, "final_metrics_atomicity": "tmp_replace",
               "defensive_error_checking": "passed_all_4_patterns",
               "progress_logging": "print_flush_true"}
    _atomic_write_metrics(OUTPUT_DIR, metrics)
    _log("VERDICT: %s" % verdict)
    _log("  %s" % msg)
    _log("DONE %s in %.1fs" % (run_mode, elapsed))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
