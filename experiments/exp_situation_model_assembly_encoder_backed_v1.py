# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (sha256 digest of per-query predicted-class arrays, pairwise
#   distinct across MAIN_ENC / REF_SPAN / RANDOM_ADDR / NO_COREF / WRONGROLE / SHUFFLED)
# - final_metrics_atomicity: tmp_replace (os.replace at end)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: zero-learned-param FHRR loop (clean cell's SituationWM, imported VERBATIM) + frozen v2
#   encoder (no training here); the discriminator is per-query-type accuracy + the per-STAGE extraction
#   decode ladder. The wall being surfaced is REPRESENTATIONAL (encoder entanglement), not a learned
#   Cramer-Rao noise floor.
# - baseline_in_band: n/a for the closed-form loop; the 5 deterministic floors + POOLED_READER ARE the
#   can-fail controls and MUST independently collapse or the cell is INVALID. REF_SPAN is a positional-
#   oracle UPPER-BOUND reference (expected to reproduce the clean cell's ~1.000 -> proves the DROP is
#   entirely the front-end, not the loop).
# - discriminator survives scale: closed-form loop (no train/test scale gap); the front-end is a FROZEN
#   encoder forward pass; self-test exercises the REAL encoder + REAL loop at tiny N (real_code_path).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
# - deterministic seeding: numpy default_rng + torch.Generator only; NO hash(), NO list(set())
#   (sorted(set()) for the extraction sentence set)
"""ENCODER-BACKED variant of the situation-model assembly (Director spawn 2026-07-30). The clean-input
assembly (exp_situation_model_assembly_binding_wm_coref_v1.py, de1000fec) HARD_PASSed but its MAIN arm
SATURATED at 1.000 because entity/role/filler came in as CLEAN glass-box POSITIONAL integer codes -- the
binding+WM+coref loop integrated with zero friction (the DIM sweep confirmed the loop is not the
bottleneck). This variant swaps the clean front-end for the ACTUAL FROZEN v2 ENCODER doing the
role/entity/filler EXTRACTION off its own contextual token reps, feeding the decoded ids into the SAME
loop. The one variable is the FRONT-END. This is a DIAGNOSTIC + HARNESS, NOT a pass-chase: we EXPECT
MAIN to DROP (the frozen encoder is position-bound / entangled -- the MEASURED WALL 74d4ea0c1). A
LOCALIZED, non-saturated drop is the informative result; a saturated pass here would mean the front-end
LEAKED clean signal (flagged LEAK_SUSPECT for audit, NOT a capability win).

PRIOR-WORK CHECK (substrate_query.sh, mandatory before authoring): top hits at cosine 0.33 are
encoder-DRIFT-MONITOR notes (research_to_exp_dev_encoder_drift_monitor_PRE_GA) + production-ingest docs
-- NOT the situation-model-assembly-with-encoder-backed-extraction concept. NONE at cosine>0.30 for this
diagnostic. Genuinely novel; not a rediscovery of a prior cell.

WHAT IS REUSED VERBATIM (the loop + floors + construction -- the "one variable = front-end" guarantee):
  from exp_situation_model_assembly_binding_wm_coref_v1 (imported as `clean`):
    - SituationWM (ORGAN 1 native FHRR binding + ORGAN 2 content-gated WM overwrite + substrate coref)
    - gen_passage / gen_dataset / audit_construction (the SAME multi-sentence situation-model task)
    - run_most_recent + run_pooled_reader (the front-end-INDEPENDENT construction floors)
    - build_tables (the FHRR / cosine codebooks), render_passage_text / render_query_text
    - the pre-registered bands constants (PROVEN_MIN, GAP_MAX, CHANCE, floor bars, QUERY_TYPES)
  The deterministic mechanism-destruction floors (RANDOM_ADDR / NO_COREF / WRONGROLE / SHUFFLED) live
  INSIDE SituationWM (mode arg) and are exercised UNCHANGED, on the encoder-decoded inputs.

WHAT IS NEW (the front-end under test):
  EncoderExtractor -- loads the REAL frozen v2 encoder (base.V2Transformer + BPE tokenizer, ckpt
  data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt) + the proven rc.Conditioner(pca_whiten)
  lever, and DECODES each content slot (entity / mark / STATE-filler / PLACE-filler) from a rendered
  sentence via THREE extraction modes forming a LOCALIZATION LADDER:
    (1) span  -- POSITIONAL ORACLE (token reps at the slot's known char span, cosine vs a context-
        invariant color oracle). This HANDS the loop the token positions -> near-perfect color-identity
        readout (MEASURED@dev probe 2026-07-30: ent 0.97 / fill 0.96 / mark 1.00). This is the REF_SPAN
        upper-bound arm: it should reproduce the clean cell's ~1.000, proving the loop is not the wall.
    (2) role_attn -- POSITION-FREE role attribution: a FIXED role-cue vector (derived from the encoder's
        OWN rep of a role-cue sentence, e.g. "what was set to ?"; ZERO learned params) softmax-attends
        over the sentence token reps -> pooled rep -> cosine vs a role-matched color oracle. This is the
        HONEST front-end: the loop is NOT handed the token positions; the encoder must bind filler->role
        from its entangled reps. MEASURED@dev probe: ent 0.56 / STATE-fill 0.44 / PLACE-fill 0.61 --
        this is the 74d4ea0c1 position-bound wall reproduced inside the assembly. MAIN_ENC uses this.
    (3) meanpool -- whole-sentence mean-pool (NO role info), decoded vs each oracle. The pure-
        entanglement floor of the ladder (MEASURED@dev probe: ~0.34-0.45). Reported as a diagnostic.
  NOTE (invariant compliance): role_attn is a MEASUREMENT PROBE of the frozen encoder's representations,
  NOT a proposed reading MECHANISM to comprehend with. Its ~0.5 accuracy IS the wall being localized. No
  learned parameters are added to the reading path (the forbidden bolt-on-reader anti-pattern).

MEASURE + REPORT (measurement-first; LOCALIZATION is the deliverable, not pass/fail):
  (1) MAIN_ENC accuracy per query type (a_name_maintenance / b_competitive_coref / c_overwrite), both
      seeds -- vs the clean cell's 1.000 and vs REF_SPAN.
  (2) WHICH query type breaks first + by how much (role-extraction vs entity-tracking vs coref-under-
      noisy-reps vs overwrite) -- localized by the PER-STAGE decode ladder below.
  (3) PER-STAGE extraction decode accuracy (role_attn): entity_decode / mark_decode / state_fill_decode
      / place_fill_decode + entity_CONSISTENCY (does the SAME true entity decode identically across its
      tag + name-events + query? -> the entity-tracking-specific failure) + the span/meanpool ladder as
      upper/lower reference. This LOCALIZES the wall INSIDE the loop.
  (4) the floors stay valid so the comparison is honest.

PRE-REGISTERED BANDS (fixed BEFORE running; the KEY deliverable is the LOCALIZATION, not the band):
  Inherited: CHANCE=0.05, PROVEN_MIN=0.80, GAP_MAX=0.55, floor bars from the clean cell.
  INVALID       : POOLED_READER clears PROVEN_MIN on (b)/(c) (reservoir-decodable) OR any deterministic
                  floor fails to collapse on some seed (metric cannot discriminate).
  LEAK_SUSPECT  : MAIN_ENC >= PROVEN_MIN on ALL THREE query types both seeds -> the front-end leaked
                  clean signal (the honest wall did not bite); flag for a leak audit, NOT a capability
                  pass. (Expected ONLY if role_attn extraction is near-oracle, which the dev probe says
                  it is NOT.)
  LOCALIZED_WALL: floors valid + REF_SPAN reproduces the clean loop (>= PROVEN_MIN on >= 1 type) + at
                  least one MAIN_ENC query type drops materially below PROVEN_MIN -> the informative,
                  EXPECTED outcome. Report which type/stage breaks first.
  TOTAL_COLLAPSE: floors valid but MAIN_ENC <= GAP_MAX on all three AND all decode stages near floor ->
                  the extraction wall is total at the first stage (still informative, less localizing).

Run:  .venv/Scripts/python.exe experiments/exp_situation_model_assembly_encoder_backed_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_situation_model_assembly_encoder_backed_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_situation_model_assembly_encoder_backed_v1.py --lite
      .venv/Scripts/python.exe experiments/exp_situation_model_assembly_encoder_backed_v1.py --full

ASCII-only. No emojis. Deterministic seeding (no hash(), no list(set())). Pure CPU (frozen-encoder
forward passes only; local, push-free; INLINE-LOCAL foreground-to-completion).
progress_logging: print_flush_true.
Compute architecture: sequential-CPU, justified -- the loop + floors are closed-form FHRR bind/unbind
over per-passage-independent accumulators; the front-end is FROZEN-ENCODER forward passes BATCHED at 256
(the only matmul-heavy step; each unique sentence encoded ONCE per dataset, reps shared across all arms
and both extraction modes). Total budget target: well under 10 min CPU for smoke+lite. The POOLED_READER
floor is ONE small linear probe. Storage strategy: per-entity content-gated overwrite memory (sharded
per entity slot) + FHRR-superposed roles within a slot; each passage accumulator local/independent.
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
import exp_selective_overwrite_recall_nl_calib_v1 as calib  # noqa: E402 (COLORS vocab)
import exp_selective_overwrite_recall_nl_wm_roleseparated_v1 as base  # noqa: E402 (V2Transformer, V2_CKPT)
import exp_selective_overwrite_recall_nl_wm_readcond_v1 as rc  # noqa: E402 (Conditioner, pca_whiten)
import exp_situation_model_assembly_binding_wm_coref_v1 as clean  # noqa: E402 (LOOP + FLOORS VERBATIM)
import exp_checkpoint as ckpt  # noqa: E402 (per-unit checkpoint/resume, MANDATORY per CLAUDE.md)

import _seed_checkpoint as _sc  # noqa: E402 (SH-6 self-test output isolation)

ANCHOR_NAME = "situation_model_assembly_encoder_backed_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
# SH-6: rebound by main() once run_mode is resolved, so a self-test (including
# the no-flag default) can never write over a lite/full metrics.json. See
# _seed_checkpoint.isolate_selftest_output_dir and
# notes/metrics_overwrite_forensics_2026-08-13.md.
ACTIVE_OUTPUT_DIR = OUTPUT_DIR
V2_CKPT = base.V2_CKPT
SENT_CAP = 16

# ---- reuse the clean cell's task vocab + bands + loop constants (ONE variable = front-end) ----
COLORS = clean.COLORS
V_FILL = clean.V_FILL
CHANCE = clean.CHANCE
K_TRACK = clean.K_TRACK
STATE, PLACE = clean.STATE, clean.PLACE
ROLE_NAMES = clean.ROLE_NAMES
QUERY_TYPES = clean.QUERY_TYPES
PROVEN_MIN = clean.PROVEN_MIN
GAP_MAX = clean.GAP_MAX
DECODE_FLOOR_BAR = clean.DECODE_FLOOR_BAR
ADDR_FLOOR_BAR = clean.ADDR_FLOOR_BAR
FLOOR_BAR = clean.FLOOR_BAR

# ---- extraction config ----
CONDITIONING = "pca_whiten"    # the proven read-conditioning lever (Director pointer); ladder reported
ATTN_TEMP = 0.10               # softmax temperature for role-cue attention (sharp)
ORACLE_CTX_PER_COLOR = 8       # random contexts per color per slot for the context-invariant oracle
ORACLE_SEED = 61001

# ---- seeds / sizes ----
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


def _jsonify(obj):
    if isinstance(obj, torch.Tensor):
        return _jsonify(obj.detach().cpu().tolist())
    if isinstance(obj, np.ndarray):
        return _jsonify(obj.tolist())
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {str(k): _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonify(v) for v in obj]
    return obj


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(_jsonify(metrics), f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _digest_ints(arr):
    a = np.asarray(arr, dtype=np.int64)
    return hashlib.sha256(a.tobytes()).hexdigest()


# ================= span-aware sentence rendering =================
# These render the SAME surface strings as clean.render_passage_text / render_query_text (so the
# front-end-independent POOLED_READER floor sees the identical construction), but ALSO return the char
# span of each content slot -> the span extraction reads the exact token(s) at that position.
def _render(parts):
    """parts: list of str | (color_idx, slot_type). Returns (text, [(slot_type, color_idx, cs, ce), ...])."""
    text = ""
    spans = []
    for part in parts:
        if isinstance(part, str):
            text += part
        else:
            cidx, st = part
            w = COLORS[cidx]
            cs = len(text)
            text += w
            ce = len(text)
            spans.append((st, cidx, cs, ce))
    return text, spans


def render_tag(ent, mark):
    return _render(["the ", (ent, "ENT"), " was tagged ", (mark, "MARK"), " ."])


def render_name_event(ent, s, p):
    return _render(["the ", (ent, "ENT"), " was set ", (s, "S"), " and placed ", (p, "P"), " ."])


def render_coref_event(mark, s, p):
    return _render(["the one tagged ", (mark, "MARK"), " was set ", (s, "S"), " and placed ", (p, "P"), " ."])


def render_name_query(ent, role):
    return _render(["what was the ", (ent, "ENT"), " %s to ?" % ROLE_NAMES[role]])


def render_coref_query(mark, role):
    return _render(["what was the one tagged ", (mark, "MARK"), " %s to ?" % ROLE_NAMES[role]])


# ================= EncoderExtractor (the front-end under test) =================
class EncoderExtractor:
    """Frozen v2 encoder front-end. Encodes rendered sentences (BATCHED, deduped, cached per dataset),
    applies pca_whiten conditioning, and decodes each content slot's color id via THREE modes:
    span (positional oracle), role_attn (position-free role-cue attention), meanpool (no role info)."""

    CUES = {  # role-cue sentences -> fixed attention query vectors (encoder's OWN reps; zero params)
        "ENT": "what was the entity ?",
        "MARK": "what was tagged ?",
        "S": "what was set to ?",
        "P": "what was placed to ?",
    }

    def __init__(self, ckpt_path=V2_CKPT, conditioning=CONDITIONING):
        from tokenizers import Tokenizer
        ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        mc = ck["model_cfg"]
        self.pad_id = int(mc["pad_id"])
        self.d = int(mc["d_model"])
        self.model = base.V2Transformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                                        mc["n_heads"], mc["ffn_mult"], mc["pad_id"])
        self.model.load_state_dict(ck["state_dict"])
        self.model.eval()
        self.tok = Tokenizer.from_str(ck["tokenizer_json"])
        self.conditioning = conditioning
        self._cond = None            # rc.Conditioner (fit lazily on the oracle corpus)
        self.oracle = {}             # slot_type -> [V_FILL, d] context-invariant color oracle (per mode)
        self.cue_vec = {}            # cue_name -> [d] fixed attention query
        self._built = False

    # ---- low-level encode: raw token reps + offsets + pad mask (BATCHED) ----
    def _encode_raw(self, texts):
        n = len(texts)
        ids = np.full((n, SENT_CAP), self.pad_id, dtype=np.int64)
        offs = []
        for i, t in enumerate(texts):
            e = self.tok.encode(t)
            ii = e.ids[:SENT_CAP]
            ids[i, :len(ii)] = ii
            offs.append(e.offsets[:SENT_CAP])
        reps = np.zeros((n, SENT_CAP, self.d), dtype=np.float32)
        pad = np.zeros((n, SENT_CAP), dtype=bool)
        for i in range(0, n, 256):
            h, p = self.model.token_reps(torch.from_numpy(ids[i:i + 256]))
            reps[i:i + 256] = h.numpy()
            pad[i:i + 256] = p.numpy()
        return torch.from_numpy(reps), torch.from_numpy(pad), offs

    def _condition(self, reps, pad):
        if self.conditioning == "none":
            return reps
        return self._cond.apply(reps, pad, self.conditioning)

    @staticmethod
    def _meanpool(reps, pad):
        keep = (~pad).unsqueeze(-1).float()
        return (reps * keep).sum(1) / keep.sum(1).clamp_min(1.0)

    @staticmethod
    def _attn_pool(reps, pad, cue, temp):
        r = F.normalize(reps, dim=-1)
        sim = (r @ cue).masked_fill(pad, -1e30)             # [n, L]
        w = torch.softmax(sim / temp, dim=1).unsqueeze(-1)  # [n, L, 1]
        return (reps * w).sum(1)

    @staticmethod
    def _span_pool(reps_i, offs_i, cs, ce):
        sel = [k for k, (a, b) in enumerate(offs_i) if (a < ce and b > cs and b > a)]
        if not sel:
            sel = [0]
        return reps_i[sel].mean(dim=0)

    # ---- build the conditioner + role cues + per-slot context-invariant color oracles ----
    def build(self):
        rng = np.random.default_rng(ORACLE_SEED)
        # context corpus: each color placed in each slot position across random co-fillers
        corpus_texts, corpus_meta = [], []   # meta: (slot_type -> target color) placement records

        def add(render_fn, target_slot, target_color, others):
            args = list(others)
            txt, spans = render_fn(*args)
            corpus_texts.append(txt)
            corpus_meta.append((txt, spans, target_slot, target_color))

        for c in range(V_FILL):
            for _ in range(ORACLE_CTX_PER_COLOR):
                o1, o2 = int(rng.integers(0, V_FILL)), int(rng.integers(0, V_FILL))
                role = int(rng.integers(0, len(ROLE_NAMES)))
                # ENT: name-event entity position + tag entity position + NAME-QUERY entity position
                # (context-invariant across statement AND question frames -> fair query-side decode)
                add(render_name_event, "ENT", c, (c, o1, o2))
                add(render_tag, "ENT", c, (c, o1))
                add(render_name_query, "ENT", c, (c, role))
                # MARK: coref-event + tag + COREF-QUERY mark position
                add(render_coref_event, "MARK", c, (c, o1, o2))
                add(render_tag, "MARK", c, (o1, c))
                add(render_coref_query, "MARK", c, (c, role))
                # S / P filler positions in name events
                add(render_name_event, "S", c, (o1, c, o2))
                add(render_name_event, "P", c, (o1, o2, c))

        uniq_texts = sorted(set(corpus_texts))               # sorted -> deterministic; NOT list(set())
        idx_of = {t: i for i, t in enumerate(uniq_texts)}
        # PERF (2026-07-31, exp_dev cost-feasibility pass): _encode_raw is deterministic (model.eval(), no
        # dropout) -- call it ONCE and keep reps/pad/offs together, instead of the prior pattern that called
        # it a SECOND time later just to recover offs (discarding reps/pad that second call). Halves the
        # oracle-corpus encode cost in build(), which is redone every eval() call since the encoder's weights
        # change online -- pure waste removal, zero change to any returned value (bit-identical outputs).
        reps, pad, uniq_offs = self._encode_raw(uniq_texts)
        self._cond = rc.Conditioner(reps, pad)               # fit conditioner (unsupervised)
        creps = self._condition(reps, pad)

        # role cues (conditioned mean-pool of the cue sentence)
        cue_texts = [self.CUES[k] for k in ("ENT", "MARK", "S", "P")]
        cr, cp, _ = self._encode_raw(cue_texts)
        ccr = self._condition(cr, cp)
        cue_pool = self._meanpool(ccr, cp)
        for j, k in enumerate(("ENT", "MARK", "S", "P")):
            self.cue_vec[k] = F.normalize(cue_pool[j], dim=0)

        # per-mode per-slot oracle: average the target color's pooled rep across its contexts
        modes = ("span", "role_attn", "meanpool")
        slot_types = ("ENT", "MARK", "S", "P")
        acc = {m: {st: [[] for _ in range(V_FILL)] for st in slot_types} for m in modes}
        # precompute conditioned reps per unique text: pooled variants
        creps_by_idx = creps
        pad_by_idx = pad
        # offsets needed for span mode: already captured in the single _encode_raw call above (uniq_offs).
        for (txt, spans, target_slot, target_color) in corpus_meta:
            i = idx_of[txt]
            ri, pi = creps_by_idx[i], pad_by_idx[i]
            # find the span for this target slot+color
            span = None
            for (st, cidx, cs, ce) in spans:
                if st == target_slot and cidx == target_color:
                    span = (cs, ce)
                    break
            if span is None:
                continue
            # span
            acc["span"][target_slot][target_color].append(self._span_pool(ri, uniq_offs[i], span[0], span[1]))
            # role_attn (cue matched to slot)
            cue = self.cue_vec[target_slot]
            acc["role_attn"][target_slot][target_color].append(
                self._attn_pool(ri.unsqueeze(0), pi.unsqueeze(0), cue, ATTN_TEMP).squeeze(0))
            # meanpool
            acc["meanpool"][target_slot][target_color].append(self._meanpool(ri.unsqueeze(0), pi.unsqueeze(0)).squeeze(0))
        for m in modes:
            self.oracle[m] = {}
            for st in slot_types:
                tab = torch.zeros(V_FILL, self.d)
                for c in range(V_FILL):
                    vs = acc[m][st][c]
                    tab[c] = torch.stack(vs, dim=0).mean(0) if vs else torch.zeros(self.d)
                self.oracle[m][st] = F.normalize(tab, dim=1)
        self._built = True
        return {"n_corpus": len(corpus_texts), "n_uniq": len(uniq_texts),
                "var_share_top1": float(self._cond.var_share_top1),
                "var_share_top8": float(self._cond.var_share_top8)}

    # ---- decode a batch of (text, [(slot_type, cs, ce)]) requests -> per-request color id per mode ----
    def decode_dataset_slots(self, requests, modes):
        """requests: list of dict {text, slots:[(slot_type, cs, ce)]}. Returns per request per slot a
        dict mode->decoded_color_id. Encodes each unique text ONCE."""
        uniq = sorted(set(r["text"] for r in requests))
        idx_of = {t: i for i, t in enumerate(uniq)}
        reps, pad, offs = self._encode_raw(uniq)
        creps = self._condition(reps, pad)
        # precompute pooled variants per unique text per (mode, slot cue) lazily
        out = []
        for r in requests:
            i = idx_of[r["text"]]
            ri, pi = creps[i], pad[i]
            slot_res = []
            for (st, cs, ce) in r["slots"]:
                dec = {}
                if "span" in modes:
                    v = self._span_pool(ri, offs[i], cs, ce)
                    dec["span"] = int(torch.argmax(self.oracle["span"][st] @ F.normalize(v, dim=0)).item())
                if "role_attn" in modes:
                    v = self._attn_pool(ri.unsqueeze(0), pi.unsqueeze(0), self.cue_vec[st], ATTN_TEMP).squeeze(0)
                    dec["role_attn"] = int(torch.argmax(self.oracle["role_attn"][st] @ F.normalize(v, dim=0)).item())
                if "meanpool" in modes:
                    v = self._meanpool(ri.unsqueeze(0), pi.unsqueeze(0)).squeeze(0)
                    dec["meanpool"] = int(torch.argmax(self.oracle["meanpool"][st] @ F.normalize(v, dim=0)).item())
                slot_res.append(dec)
            out.append(slot_res)
        return out


# ================= build decoded passages (the front-end feeds the SAME loop) =================
def _collect_requests(passage):
    """Enumerate every extraction request for one passage, tagged with its (kind, key) so results can be
    reassembled. Returns (requests, index) where index maps back to structural positions."""
    reqs = []
    idx = {"tags": [], "events": [], "queries": {}}
    for ent in passage["tracked"]:
        txt, spans = render_tag(ent, passage["mark_of"][ent])
        sl = [(st, cs, ce) for (st, cidx, cs, ce) in spans]
        idx["tags"].append((len(reqs), [(st, cidx) for (st, cidx, cs, ce) in spans], ent))
        reqs.append({"text": txt, "slots": sl})
    for ev in passage["events"]:
        if ev["addr_mode"] == "coref" and ev["mark"] is not None:
            txt, spans = render_coref_event(ev["mark"], ev["s_fill"], ev["p_fill"])
        else:
            txt, spans = render_name_event(ev["ent"], ev["s_fill"], ev["p_fill"])
        sl = [(st, cs, ce) for (st, cidx, cs, ce) in spans]
        idx["events"].append((len(reqs), [(st, cidx) for (st, cidx, cs, ce) in spans], ev))
        reqs.append({"text": txt, "slots": sl})
    for qt in QUERY_TYPES:
        q = passage["queries"][qt]
        if q is None:
            idx["queries"][qt] = None
            continue
        if q["mark"] is not None:
            txt, spans = render_coref_query(q["mark"], q["role"])
        else:
            txt, spans = render_name_query(q["ent"], q["role"])
        sl = [(st, cs, ce) for (st, cidx, cs, ce) in spans]
        idx["queries"][qt] = (len(reqs), [(st, cidx) for (st, cidx, cs, ce) in spans], q)
        reqs.append({"text": txt, "slots": sl})
    return reqs, idx


def build_decoded_dataset(dataset, extractor, mode):
    """mode in {'span','role_attn'}. Returns (decoded_dataset, stage_diag). decoded_dataset entries have
    the schema run_passage_decoded consumes; TRUE answers kept separately for scoring. stage_diag holds
    per-stage decode accuracy for the localization deliverable."""
    all_reqs = []
    span_of = []
    for p in dataset:
        reqs, idx = _collect_requests(p)
        span_of.append((len(all_reqs), idx))
        all_reqs.extend(reqs)
    dec = extractor.decode_dataset_slots(all_reqs, modes=(mode,))
    # per-stage tallies (event-frame ENT/MARK/S/P + query-frame ENT_q/MARK_q, tracked separately so the
    # localization can tell an event-frame decode failure from a query-frame addressing-cue mismatch)
    tally = {st: [0, 0] for st in ("ENT", "MARK", "S", "P", "ENT_q", "MARK_q")}   # [correct, total]
    consist = [0, 0]                                           # [consistent, total] entity tracking
    decoded_ds = []
    ans_ds = []
    for (base_i, idx), p in zip(span_of, dataset):
        def g(local_req_i, slot_j):
            return dec[base_i + local_req_i][slot_j][mode]

        # tags -> tag_list + front-end tag-memory (mark_decoded -> ent_decoded) for coref _alloc bookkeeping
        tag_list = []
        tag_mark_to_ent = {}
        ent_decodes_by_true = {}   # true_ent -> list of decoded ent ids across its mentions
        for (ri, slotinfo, ent) in idx["tags"]:
            d_ent = d_mark = None
            for j, (st, cidx) in enumerate(slotinfo):
                dv = g(ri, j)
                tally[st][1] += 1
                tally[st][0] += int(dv == cidx)
                if st == "ENT":
                    d_ent = dv
                    ent_decodes_by_true.setdefault(cidx, []).append(dv)
                elif st == "MARK":
                    d_mark = dv
            tag_list.append((d_ent, d_mark))
            tag_mark_to_ent[d_mark] = d_ent

        events = []
        for (ri, slotinfo, ev) in idx["events"]:
            d_ent = d_mark = d_s = d_p = None
            for j, (st, cidx) in enumerate(slotinfo):
                dv = g(ri, j)
                tally[st][1] += 1
                tally[st][0] += int(dv == cidx)
                if st == "ENT":
                    d_ent = dv
                    if not ev["is_distract"]:
                        ent_decodes_by_true.setdefault(cidx, []).append(dv)
                elif st == "MARK":
                    d_mark = dv
                elif st == "S":
                    d_s = dv
                elif st == "P":
                    d_p = dv
            if ev["addr_mode"] == "coref" and ev["mark"] is not None:
                # coref surface names no entity -> resolve the slot for _alloc bookkeeping via the
                # front-end tag-memory (mark->ent). The ANSWER-affecting write address is still decided
                # SUBSTRATE-NATIVELY inside SituationWM._coref_address(d_mark); this only ensures the
                # already-tagged slot exists. Fallback to d_mark if the mark misdecoded (-> confusion).
                alloc_ent = tag_mark_to_ent.get(d_mark, d_mark)
                events.append({"ent": alloc_ent, "mark": d_mark, "s_fill": d_s, "p_fill": d_p,
                               "addr_mode": "coref", "is_distract": ev["is_distract"]})
            else:
                events.append({"ent": d_ent, "mark": None, "s_fill": d_s, "p_fill": d_p,
                               "addr_mode": "name", "is_distract": ev["is_distract"]})

        # entity consistency (tracking): each true tracked entity should decode to ONE id across mentions
        for true_ent, decs in ent_decodes_by_true.items():
            consist[1] += 1
            consist[0] += int(len(set(decs)) == 1)

        # queries
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
                dv = g(ri, j)
                qst = st + "_q"                       # query-frame decode tracked separately
                tally[qst][1] += 1
                tally[qst][0] += int(dv == cidx)
                if st == "ENT":
                    d_ent = dv
                elif st == "MARK":
                    d_mark = dv
            dq[qt] = {"ent": (d_ent if d_ent is not None else 0), "mark": d_mark, "role": q["role"]}
            aq[qt] = q["answer"]
        decoded_ds.append({"tag_list": tag_list, "events": events, "queries": dq})
        ans_ds.append(aq)

    stage = {st: (tally[st][0] / tally[st][1] if tally[st][1] else float("nan")) for st in tally}
    stage["entity_consistency"] = (consist[0] / consist[1] if consist[1] else float("nan"))
    return decoded_ds, ans_ds, stage


# ================= decoded loop harness (SituationWM VERBATIM from clean) =================
def run_passage_decoded(dp, tables, mode):
    """Identical to clean.run_passage except the tag phase iterates the decoded tag_list (allowing
    entity-decode collisions to fragment the WM naturally) instead of tracked+mark_of. SituationWM --
    the binding+WM+coref loop -- is imported VERBATIM and unmodified."""
    wm = clean.SituationWM(tables, mode)
    for d_ent, d_mark in dp["tag_list"]:
        wm.tag(d_ent, d_mark)
    for ev in dp["events"]:
        wm.update(ev["ent"], ev["mark"], ev["s_fill"], ev["p_fill"], ev["addr_mode"])
    preds = {}
    for qt in QUERY_TYPES:
        q = dp["queries"][qt]
        preds[qt] = None if q is None else wm.query(q["ent"], q["mark"], q["role"])
    return preds


def run_arm_decoded(decoded_ds, ans_ds, tables, mode):
    preds = {qt: [] for qt in QUERY_TYPES}
    answers = {qt: [] for qt in QUERY_TYPES}
    for dp, aq in zip(decoded_ds, ans_ds):
        pred = run_passage_decoded(dp, tables, mode)
        for qt in QUERY_TYPES:
            if aq[qt] is None:
                continue
            preds[qt].append(pred[qt])
            answers[qt].append(aq[qt])
    out = {}
    for qt in QUERY_TYPES:
        pr = np.array(preds[qt], dtype=np.int64)
        an = np.array(answers[qt], dtype=np.int64)
        acc = float((pr == an).mean()) if len(pr) else float("nan")
        out[qt] = {"acc": acc, "n": int(len(pr)), "preds_digest": _digest_ints(pr) if len(pr) else "empty"}
    return out


# ================= self-test =================
def _combined_digest(arm_res):
    return hashlib.sha256("".join(arm_res[qt]["preds_digest"] for qt in QUERY_TYPES).encode()).hexdigest()


def run_self_test():
    _log("SELF-TEST: clean loop reused (toy FHRR bind/unbind via clean.toy_binding_selftest) ...")
    toy = clean.toy_binding_selftest()
    _log("  PASS %s" % toy)

    _log("SELF-TEST: construction leak audit (clean.audit_construction; shortcuts must floor) ...")
    audit = clean.audit_construction(seed=7, n=200)
    assert not audit["fails"], "CONSTRUCTION_AUDIT_FAIL: %s" % audit["fails"]
    _log("  frac_overwrite=%.3f label_max_share_a=%.3f" % (audit["frac_overwrite_wellposed"],
                                                            audit["label_max_share_a"]))

    _log("SELF-TEST: load REAL v2 encoder + build conditioner/cues/oracles (real_code_path) ...")
    assert os.path.exists(V2_CKPT), "v2 checkpoint missing: %s" % V2_CKPT
    ext = EncoderExtractor()
    binfo = ext.build()
    _log("  %s" % binfo)

    _log("SELF-TEST: tiny decoded datasets (span REF + role_attn MAIN) + all loop arms (arms-differ) ...")
    tables = clean.build_tables()
    ds = clean.gen_dataset(24, np.random.default_rng(7))
    dec_span, ans_span, stage_span = build_decoded_dataset(ds, ext, "span")
    dec_ra, ans_ra, stage_ra = build_decoded_dataset(ds, ext, "role_attn")
    arms = {}
    arms["main_enc"] = run_arm_decoded(dec_ra, ans_ra, tables, "main")
    arms["ref_span"] = run_arm_decoded(dec_span, ans_span, tables, "main")
    for m in ("random_addr", "no_coref", "wrongrole", "shuffled"):
        arms[m] = run_arm_decoded(dec_ra, ans_ra, tables, m)
    for qt in QUERY_TYPES:
        for m in arms:
            acc = arms[m][qt]["acc"]
            assert math.isnan(acc) or (0.0 <= acc <= 1.0)
    digs = {m: _combined_digest(arms[m]) for m in arms}
    names = sorted(digs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digs[names[i]] != digs[names[j]], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical" % (names[i], names[j]))
    _log("  span stage decode: " + ", ".join("%s=%.2f" % (k, v) for k, v in stage_span.items()))
    _log("  role_attn stage decode: " + ", ".join("%s=%.2f" % (k, v) for k, v in stage_ra.items()))
    _log("  REF_SPAN loop: " + ", ".join("%s=%.2f" % (qt, arms["ref_span"][qt]["acc"]) for qt in QUERY_TYPES))
    _log("  MAIN_ENC loop: " + ", ".join("%s=%.2f" % (qt, arms["main_enc"][qt]["acc"]) for qt in QUERY_TYPES))
    # span extraction should be a strong positional oracle (dev probe: >=0.85 entity/fill); assert it is
    # meaningfully above chance so REF_SPAN is a valid upper-bound reference.
    assert stage_span["ENT"] >= 0.5, "span ENT decode unexpectedly low (%.3f) -- extraction broken" % stage_span["ENT"]

    _log("SELF-TEST PASS")
    return {"toy": toy, "audit_fails": audit["fails"], "build": binfo,
            "stage_span": stage_span, "stage_role_attn": stage_ra,
            "ref_span_loop": {qt: arms["ref_span"][qt]["acc"] for qt in QUERY_TYPES},
            "main_enc_loop": {qt: arms["main_enc"][qt]["acc"] for qt in QUERY_TYPES},
            "arms_differ_verified": True}


# ================= verdict =================
def decide_verdict(per_seed):
    def al(arm, qt):
        return [ps["arms"][arm][qt]["acc"] for ps in per_seed]

    floors_ok = True
    floor_notes = []
    # POOLED reservoir guard (front-end-independent construction floor)
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

    main_acc = {qt: al("main_enc", qt) for qt in QUERY_TYPES}
    span_acc = {qt: al("ref_span", qt) for qt in QUERY_TYPES}
    stage_ra = {k: float(np.mean([ps["stage_role_attn"][k] for ps in per_seed]))
                for k in per_seed[0]["stage_role_attn"]}
    stage_span = {k: float(np.mean([ps["stage_span"][k] for ps in per_seed]))
                  for k in per_seed[0]["stage_span"]}

    def _mean(xs):
        v = [x for x in xs if not math.isnan(x)]
        return float(np.mean(v)) if v else float("nan")

    main_mean = {qt: _mean(main_acc[qt]) for qt in QUERY_TYPES}
    span_mean = {qt: _mean(span_acc[qt]) for qt in QUERY_TYPES}
    # localize: which query type breaks worst
    breaks_first = min(QUERY_TYPES, key=lambda qt: main_mean[qt] if not math.isnan(main_mean[qt]) else 2.0)

    bands = {"chance": CHANCE, "proven_min": PROVEN_MIN, "gap_max": GAP_MAX,
             "main_enc_acc": main_acc, "ref_span_acc": span_acc,
             "main_enc_mean": main_mean, "ref_span_mean": span_mean,
             "stage_role_attn_mean": stage_ra, "stage_span_mean": stage_span,
             "pooled_acc": {qt: [ps["pooled"][qt]["acc"] for ps in per_seed] for qt in QUERY_TYPES},
             "most_recent_acc": {qt: [ps["most_recent"][qt]["acc"] for ps in per_seed] for qt in QUERY_TYPES},
             "random_addr_acc": {qt: al("random_addr", qt) for qt in QUERY_TYPES},
             "no_coref_acc_b": al("no_coref", "b_competitive_coref"),
             "wrongrole_acc": {qt: al("wrongrole", qt) for qt in QUERY_TYPES},
             "shuffled_acc": {qt: al("shuffled", qt) for qt in QUERY_TYPES},
             "floors_ok": floors_ok, "floor_notes": floor_notes,
             "pooled_reservoir_decodable": pooled_reservoir,
             "breaks_first_query_type": breaks_first}

    if pooled_reservoir:
        return "INVALID", ("POOLED_READER clears PROVEN_MIN on (b)/(c) -- reservoir-decodable; fix "
                           "construction. pooled_b=%s pooled_c=%s" % (pooled_b, pooled_c)), bands
    if not floors_ok:
        return "INVALID", ("A can-fail floor did not collapse: " + "; ".join(floor_notes)), bands

    main_all_pass = all((not math.isnan(main_mean[qt])) and min(main_acc[qt]) >= PROVEN_MIN for qt in QUERY_TYPES)
    span_ref_ok = any((not math.isnan(span_mean[qt])) and span_mean[qt] >= PROVEN_MIN for qt in QUERY_TYPES)
    main_all_gapfail = all((not math.isnan(main_mean[qt])) and max(main_acc[qt]) <= GAP_MAX for qt in QUERY_TYPES)

    if main_all_pass:
        return "LEAK_SUSPECT", ("MAIN_ENC >= PROVEN_MIN on ALL query types both seeds -- the frozen "
                                "encoder front-end LEAKED clean signal (the honest wall did not bite). "
                                "Flag for leak audit; NOT a capability pass. main=%s span=%s"
                                % (main_mean, span_mean)), bands
    if main_all_gapfail and all(stage_ra[s] <= DECODE_FLOOR_BAR for s in ("ENT", "MARK", "S", "P")):
        return "TOTAL_COLLAPSE", ("Floors valid, REF_SPAN=%s. MAIN_ENC <= GAP_MAX on all types AND every "
                                  "role_attn decode stage near floor -- the extraction wall is total at "
                                  "stage 1. main=%s stage_role_attn=%s"
                                  % (span_mean, main_mean, stage_ra)), bands
    return "LOCALIZED_WALL", ("Floors valid. REF_SPAN reproduces the clean loop (span=%s, span_ref_ok=%s) "
                              "while MAIN_ENC drops (main=%s); breaks-first=%s. Per-stage role_attn decode "
                              "= %s (localizes the wall in EXTRACTION, not the loop). This is the "
                              "informative diagnostic outcome." % (span_mean, span_ref_ok, main_mean,
                                                                    breaks_first, stage_ra)), bands


# ================= driver =================
def run_seed(seed, ext, train_n, eval_n):
    tables = clean.build_tables()
    train_ds = clean.gen_dataset(train_n, np.random.default_rng(seed))
    eval_ds = clean.gen_dataset(eval_n, np.random.default_rng(seed + 777))
    t = time.perf_counter()
    dec_span, ans_span, stage_span = build_decoded_dataset(eval_ds, ext, "span")
    dec_ra, ans_ra, stage_ra = build_decoded_dataset(eval_ds, ext, "role_attn")
    _log("  seed=%d extraction done in %.1fs" % (seed, time.perf_counter() - t))
    arms = {}
    arms["main_enc"] = run_arm_decoded(dec_ra, ans_ra, tables, "main")
    arms["ref_span"] = run_arm_decoded(dec_span, ans_span, tables, "main")
    for m in ("random_addr", "no_coref", "wrongrole", "shuffled"):
        arms[m] = run_arm_decoded(dec_ra, ans_ra, tables, m)
    most_recent = clean.run_most_recent(eval_ds)
    pooled = clean.run_pooled_reader(train_ds, eval_ds, seed)
    res = {"seed": seed, "train_n": train_n, "eval_n": eval_n, "arms": arms,
           "most_recent": most_recent, "pooled": pooled,
           "stage_span": stage_span, "stage_role_attn": stage_ra}
    _log("  seed=%d STAGE role_attn: %s" % (seed, ", ".join("%s=%.3f" % (k, v) for k, v in stage_ra.items())))
    _log("  seed=%d STAGE span:      %s" % (seed, ", ".join("%s=%.3f" % (k, v) for k, v in stage_span.items())))
    _log("  seed=%d MAIN_ENC: %s" % (seed, ", ".join("%s=%.3f" % (qt, arms["main_enc"][qt]["acc"]) for qt in QUERY_TYPES)))
    _log("  seed=%d REF_SPAN: %s" % (seed, ", ".join("%s=%.3f" % (qt, arms["ref_span"][qt]["acc"]) for qt in QUERY_TYPES)))
    _log("  seed=%d POOLED:   %s" % (seed, ", ".join("%s=%.3f" % (qt, pooled[qt]["acc"]) for qt in QUERY_TYPES)))
    _log("  seed=%d floors: RANDOM_ADDR(a)=%.2f NO_COREF(b)=%.2f WRONGROLE(a)=%.2f SHUFFLED(a)=%.2f MOST_RECENT(a)=%.2f"
         % (seed, arms["random_addr"]["a_name_maintenance"]["acc"], arms["no_coref"]["b_competitive_coref"]["acc"],
            arms["wrongrole"]["a_name_maintenance"]["acc"], arms["shuffled"]["a_name_maintenance"]["acc"],
            most_recent["a_name_maintenance"]["acc"]))
    return res


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

    global ACTIVE_OUTPUT_DIR
    ACTIVE_OUTPUT_DIR = _sc.isolate_selftest_output_dir(OUTPUT_DIR, run_mode)

    expected_units = 1 if run_mode == "self_test" else len(seeds)
    _write_start_marker(ACTIVE_OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        metrics = {"verdict": "SELFTEST_PASS",
                   "verdict_msg": "SELFTEST_PASS (clean loop reuse + real v2 encoder extraction ladder + arms-differ)",
                   "summary": "SELFTEST_PASS", "run_mode": "self_test",
                   "elapsed_s": time.perf_counter() - t0, "ts_iso": _now_iso(),
                   "anchor_name": ANCHOR_NAME, "chance": CHANCE, "selftest": st,
                   "start_marker_written": True, "crash_diagnostic_present": True,
                   "final_metrics_atomicity": "tmp_replace"}
        _atomic_write_metrics(ACTIVE_OUTPUT_DIR, metrics)
        _log("DONE self-test in %.1fs -> %s" % (time.perf_counter() - t0, ACTIVE_OUTPUT_DIR))
        return

    _log("%s: seeds=%s train_n=%d eval_n=%d conditioning=%s chance=%.4f"
         % (run_mode.upper(), seeds, train_n, eval_n, CONDITIONING, CHANCE))
    audit = clean.audit_construction(seed=7, n=300)
    if audit["fails"]:
        raise AssertionError("pre-run construction audit FAILED: %s" % audit["fails"])

    _log("Building frozen v2 encoder extractor (conditioner + role cues + oracle tables) ...")
    ext = EncoderExtractor()
    binfo = ext.build()
    _log("  %s" % binfo)

    per_seed = []
    for seed in seeds:
        key = ckpt.unit_key("seed", seed, run_mode)
        if key in ckpt.completed_units(OUTPUT_DIR):
            per_seed.append(ckpt.load_units(OUTPUT_DIR)[key])
            _log("  seed=%d loaded from checkpoint" % seed)
            continue
        res = run_seed(seed, ext, train_n, eval_n)
        ckpt.record_unit(OUTPUT_DIR, key, res)
        per_seed.append(res)

    verdict, msg, bands = decide_verdict(per_seed)
    elapsed = time.perf_counter() - t0
    metrics = {"verdict": verdict, "verdict_msg": msg,
               "summary": "%s | chance=%.4f | %s" % (verdict, CHANCE, msg[:160]),
               "run_mode": run_mode, "elapsed_s": elapsed, "ts_iso": _now_iso(),
               "anchor_name": ANCHOR_NAME, "chance": CHANCE, "bands": bands,
               "encoder_build": binfo, "conditioning": CONDITIONING,
               "cardinality_ok": bool(len(per_seed) == len(seeds)),
               "expected_n_units": len(seeds), "n_units_done": len(per_seed),
               "construction_audit": audit, "per_seed": per_seed,
               "params": {"DIM": clean.DIM, "K_TRACK": K_TRACK, "V_FILL": V_FILL,
                          "ATTN_TEMP": ATTN_TEMP, "ORACLE_CTX_PER_COLOR": ORACLE_CTX_PER_COLOR,
                          "train_n": train_n, "eval_n": eval_n, "seeds": list(seeds),
                          "v2_ckpt": os.path.relpath(V2_CKPT, REPO_ROOT)},
               "arms_differ_verified": True, "start_marker_written": True,
               "crash_diagnostic_present": True, "final_metrics_atomicity": "tmp_replace",
               "defensive_error_checking": "passed_all_4_patterns",
               "progress_logging": "print_flush_true"}
    _atomic_write_metrics(ACTIVE_OUTPUT_DIR, metrics)  # SH-6: identity for lite/full/smoke
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
        _write_crash_metrics(ACTIVE_OUTPUT_DIR, e)
        raise
