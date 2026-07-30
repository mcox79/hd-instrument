# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF; LEARNED vs RANDOM_INIT eval-logit hash)
# - final_metrics_atomicity: tmp_replace (os.replace at end)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no Cramer-Rao noise floor; discriminator = LEARNED_WM vs random-init-WM separation,
#   judged live (chance=1/V_FILL, oracle ceiling 1.0 from the NL calib).
# - baseline_in_band: RANDOM_INIT_WM (frozen role-separated WM, trained readout) is the can-fail
#   baseline; MUST stay near chance. Judged live.
# - discriminator survives scale: FULL is the scale of interest; self-test builds REAL v2 encoder +
#   REAL role-separated WM at tiny N (real_code_path).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
# - deterministic seeding: numpy default_rng + torch.manual_seed only; NO hash(), NO list(set())
"""Selective-Overwrite-Recall NL WM -- ROLE-SEPARATED event rep (the WM_NL_CANT_LEARN fix, v1).

EVIDENCE-DIRECTED ONE-VARIABLE FIX of the WM_NL_CANT_LEARN negative
(exp_selective_overwrite_recall_nl_wm_v1, commit f82370cd1 -> eval 0.061/0.039 = chance, STUCK_FLAT).

MEASURED lever diagnosis (f82370cd1 metrics.json):
  - a LINEAR probe on the frozen v2 POOLED event rep recovers slot=1.000 AND filler=1.000 (info
    present + linearly separable) -- so the block is NOT the encoder.
    MEASURED@data/exp_selective_overwrite_recall_nl_wm_v1/metrics.json:encoder_binding_probe
  - but the single-content-address WM OVERFITS on the POOLED rep: full-batch overfit-100 ->
    train_acc=0.960, eval_acc=0.072 (memorizes, does NOT generalize).
    MEASURED@data/exp_selective_overwrite_recall_nl_wm_v1/metrics.json:capacity_probe
  -> the WM cannot learn a FILLER-INVARIANT slot-addressing rule from ONE ENTANGLED pooled vector
     (address + value share the same blended vector; the address cannot be made invariant to the
     filler it is entangled with). The brain binds on SEPARABLE role+filler, not a pooled bag-of-
     tokens (Frankland&Greene 2015 role-general; Smolensky/Plate VSA role-filler binding -- CITED).

THE ONE VARIABLE (vs f82370cd1): the EVENT REPRESENTATION the WM consumes.
  f82370cd1: each event -> ONE pooled vector (masked-mean over the sentence's contextual tokens);
             the WM addresses AND stores from that SAME entangled vector.
  THIS cell: keep the event's per-token contextual reps [L, d]; TWO LEARNED ROLE QUERIES each attend
             (differentiable softmax over token positions, position-invariant, parser-free) over the
             event's frozen token reps:
               - a SLOT-role query  -> slot_rep (the ADDRESS signal; from the slot-noun tokens)
               - a FILLER-role query -> fill_rep (the stored VALUE; from the filler-color tokens)
             so the ADDRESS and the VALUE are read from DIFFERENT tokens, not one pooled vector.
             This is the shelved role-query idea (hdlab/slot_attention_wm.entity_filler), now
             evidence-motivated. Combines the task's option (a) token-level (address vs value from
             different tokens) with option (b) role-query (learned queries extract slot/fill reps).

Everything else is IDENTICAL to the proven gated-overwrite WM (exp_selective_overwrite_recall_wm_v1):
K content-address slots (keys), a learned scalar write gate, a gated OVERWRITE (1-w)*h + w*cand that
keeps the LAST write, value-proj, readout. Encoder = REAL v2 FROZEN (data/exp_scale_meaning_learn_arc
_heldout_v2/ckpt_seed_7.pt), same ckpt as f82370cd1. NO bistable/PE-threshold stack.

EFFICIENCY: there are only 3006 UNIQUE sentences (5 templates x 30 nouns x 20 colors + 6 queries).
Their FROZEN token reps are cached ONCE (encoder is frozen + seed-independent). Each forward applies
the (learned) role queries to the 3006 cached token-rep matrices to get per-unique slot_rep/fill_rep
[3006, d], then GATHERS per event by unique-sentence index -- so [B, Lmax, Lcap, d] is never
materialized (the role-query outputs depend only on the sentence).

GROUNDING PROBE FIRST (token-level; the fix has signal iff this fires): for each event sentence,
locate the slot-noun token(s) and the filler-color token(s) via the tokenizer offset mapping;
linear-probe slot-token rep -> slot id AND filler-token rep -> filler id SEPARATELY. If both ~1.0,
the frozen v2 TOKEN reps carry slot (on slot tokens) and filler (on filler tokens) separably -> the
role-separated representation supports role-filler binding and the fix has a real shot. Always emitted.

ARMS (per seed in {7,13}; SAME frozen v2 encoder + cached token reps shared across arms):
  LEARNED_WM     -- train role_query_slot + role_query_fill + keys + write-gate + value-proj + readout
                    end-to-end. The capability.
  RANDOM_INIT_WM (>=5 control seeds) -- FREEZE role queries + keys + write-gate + value-proj at random
                    init, train ONLY the readout on the (fixed) memory-read features. The CAN-FAIL
                    control: MUST stay ~chance (0.05). LEARNED_WM must BEAT it by a large margin.

VERDICT: WM_NL_PROVEN / STILL_CANT_LEARN / WM_NL_PARTIAL / CONTROL_FLOOR_BROKEN (see bands).
  The WHOLE point is GENERALIZATION: does the role-separated address learn a FILLER-INVARIANT rule
  that transfers (eval ~ train), or does it overfit again (train high / eval chance)?

Run:  .venv/Scripts/python.exe experiments/exp_selective_overwrite_recall_nl_wm_roleseparated_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_selective_overwrite_recall_nl_wm_roleseparated_v1.py --full

ASCII-only. No emojis. Deterministic seeding (torch.Generator + np.random.default_rng; no hash(),
no list(set())). CPU (local, push-free; this .venv has no CUDA).
"""

import argparse
import hashlib
import json
import math
import os
import platform
import re
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# the VALID NL construction (single source of truth for task + oracles + vocab)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_selective_overwrite_recall_nl_calib_v1 as calib  # noqa: E402

ANCHOR_NAME = "selective_overwrite_recall_nl_wm_roleseparated_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
V2_CKPT = os.path.join(REPO_ROOT, "data", "exp_scale_meaning_learn_arc_heldout_v2", "ckpt_seed_7.pt")

# ---- pull the CALIBRATED NL construction constants ----
V_FILL = calib.V_FILL              # 20 -> CHANCE = 0.05
CHANCE = calib.CHANCE
S_TARGET = calib.S_TARGET          # 6 target slots
COLORS = calib.COLORS
SLOT_NOUNS = calib.SLOT_NOUNS
EVENT_TEMPLATES = calib.EVENT_TEMPLATES
QUERY_TEMPLATE = calib.QUERY_TEMPLATE

# ---- WM / training params (mechanism IDENTICAL to the proven synthetic WM exp_..._wm_v1) ----
K_SLOTS = 6                        # content-addressed slots (= S_TARGET; distractors suppressed by gate)
D_MEM = 64                        # slot memory width
HIDDEN = 64                       # write-gate MLP hidden
ADDR_TEMP = 0.3                   # addressing softmax temp (same lever as the proven WM)
SENT_CAP = 16                     # BPE token cap per event/query sentence (MEASURED max unique = 9)

FULL_TRAIN, FULL_EVAL = 1200, 700  # matches the NL calib scale
STEPS_WM = 1000                    # identical-recipe minibatch Adam
BATCH = 256
STEPS_READOUT = 400
LR = 1e-2
EARLY_STOP_LOSS = 0.03
RETRY_TRAIN_ACC = 0.50            # a COMPLETED LEARNED_WM below this train_acc = a dud trajectory
MAX_RESTARTS = 1                  # restart a dud LEARNED_WM once (documents robust-dead, not luck)
SEEDS_FULL = (7, 13)
N_RANDOM_INIT = 5
# capacity probe: expressiveness vs generalization localizer (same as f82370cd1, on the NEW rep).
CAP_PROBE_N = 100
CAP_PROBE_STEPS = 800

# ---- bands (pre-reg; same as the proven synthetic WM + the f82370cd1 negative) ----
Z_THRESH = 2.0
RI_NEAR_CHANCE = 0.10             # each random-init control MUST be < this (clean floor)
MECH_MARGIN = 0.30                # LEARNED_WM - ri_mean must be >= this
WM_PROVEN_MIN = 0.50              # LEARNED_WM eval acc must be >= this (>=10x chance), both seeds
WM_CANT_LEARN_MAX = 0.15          # <= this on BOTH seeds -> can't-learn
LOSS_DESCEND_RATIO = 0.90
ORACLE_CEILING = 1.0              # MEASURED@data/exp_selective_overwrite_recall_nl_calib_v1/metrics.json
# grounding-probe bar: token-level reps SUPPORT binding iff both >= this (well above chance).
TOKEN_PROBE_MIN = 0.50


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
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ---------------- significance (verbatim from the hardened MES/WM gate) ----------------
def _binom_se(acc, n):
    n = max(int(n), 1)
    return math.sqrt(max(acc * (1.0 - acc), 1e-9) / n)


def _one_sided_p(z):
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def power_stats(trained_acc, n_eval, ri_accs):
    ri = np.asarray(ri_accs, dtype=float)
    ri_mean = float(ri.mean())
    ri_std = float(ri.std(ddof=1)) if ri.size > 1 else 0.0
    ri_max = float(ri.max())
    se_trained = _binom_se(trained_acc, n_eval)
    se_ri_mean = _binom_se(ri_mean, n_eval)
    se_diff = math.sqrt(se_trained ** 2 + se_ri_mean ** 2 + ri_std ** 2)
    gap = trained_acc - ri_mean
    z = (gap / se_diff) if se_diff > 0 else 0.0
    return dict(ri_mean=ri_mean, ri_std=ri_std, ri_max=ri_max, n_ri_seeds=int(ri.size),
                se_diff=se_diff, gap=gap, z=z, p_value=_one_sided_p(z),
                min_detectable_effect_2sigma=2.0 * se_diff, beats_ri_max=bool(trained_acc > ri_max),
                significant=bool(z >= Z_THRESH and trained_acc > ri_max))


# ---------------- frozen REAL v2 encoder (byte-identical arch; TOKEN-LEVEL reps) ----------------
class V2Transformer(nn.Module):
    """Byte-identical architecture to exp_scale_meaning_learn_arc_heldout_v2.TinyTransformer, so the
    saved state_dict loads exactly. Redefined here to avoid importing the heavy training module."""

    def __init__(self, vocab, max_len, d_model, n_layers, n_heads, ffn_mult, pad_id):
        super().__init__()
        self.pad_id = pad_id
        self.tok_emb = nn.Embedding(vocab, d_model, padding_idx=pad_id)
        self.pos_emb = nn.Embedding(max_len, d_model)
        layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=ffn_mult * d_model,
            dropout=0.0, activation="gelu", batch_first=True, norm_first=True)
        self.enc = nn.TransformerEncoder(layer, num_layers=n_layers)
        self.norm = nn.LayerNorm(d_model)
        self.max_len = max_len
        self.d_model = d_model

    def _contextual(self, ids):
        pad_mask = (ids == self.pad_id)
        L = ids.shape[1]
        pos = torch.arange(L, device=ids.device).unsqueeze(0)
        h = self.tok_emb(ids) + self.pos_emb(pos)
        h = self.enc(h, src_key_padding_mask=pad_mask)
        return self.norm(h), pad_mask

    @torch.no_grad()
    def token_reps(self, ids):
        """Per-token contextual reps, L2-normalized per real token, pad tokens zeroed. [B, L, d]."""
        h, pad_mask = self._contextual(ids)
        keep = (~pad_mask).float().unsqueeze(-1)
        h = h * keep
        n = h.norm(dim=-1, keepdim=True).clamp_min(1e-8)
        h = (h / n) * keep
        return h, pad_mask


class FrozenV2Encoder:
    """Loads the real v2 checkpoint + its BPE tokenizer; caches TOKEN-LEVEL reps of the CLOSED
    sentence set (3006 uniques). Provides:
      U_tok [Nu, SENT_CAP, d] float32 token reps, U_pad [Nu, SENT_CAP] bool (True=pad),
      name2idx: sentence-string -> row index (for O(1) event lookup)."""

    def __init__(self, ckpt_path):
        from tokenizers import Tokenizer
        ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        mc = ck["model_cfg"]
        self.pad_id = int(mc["pad_id"])
        self.d = int(mc["d_model"])
        self.model = V2Transformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                                   mc["n_heads"], mc["ffn_mult"], mc["pad_id"])
        self.model.load_state_dict(ck["state_dict"])
        self.model.eval()
        self.tok = Tokenizer.from_str(ck["tokenizer_json"])
        self.name2idx = {}
        self.U_tok = None
        self.U_pad = None
        self.U_tok_t = None
        self.U_pad_t = None
        self._selected_arm = ck.get("selected_arm")
        self._seed = ck.get("seed")

    def _encode_ids(self, texts):
        ids = np.full((len(texts), SENT_CAP), self.pad_id, dtype=np.int64)
        for i, t in enumerate(texts):
            e = self.tok.encode(t).ids[:SENT_CAP]
            ids[i, :len(e)] = e
        return ids

    def _closed_sentences(self):
        sents = []
        for tm in EVENT_TEMPLATES:
            for sl in SLOT_NOUNS:
                for fl in COLORS:
                    sents.append(tm.format(slot=sl, fill=fl))
        for sl in range(S_TARGET):
            sents.append(QUERY_TEMPLATE.format(slot=SLOT_NOUNS[sl]))
        return sorted(set(sents))   # sorted -> deterministic; NOT list(set())

    def build_cache(self):
        """Enumerate + token-encode the full closed sentence set ONCE."""
        uniq = self._closed_sentences()
        ids = self._encode_ids(uniq)
        Nu = len(uniq)
        U_tok = np.zeros((Nu, SENT_CAP, self.d), dtype=np.float32)
        U_pad = np.zeros((Nu, SENT_CAP), dtype=bool)
        for i in range(0, Nu, 256):
            h, pad = self.model.token_reps(torch.from_numpy(ids[i:i + 256]))
            U_tok[i:i + 256] = h.numpy()
            U_pad[i:i + 256] = pad.numpy()
        self.name2idx = {s: i for i, s in enumerate(uniq)}
        self.U_tok = U_tok
        self.U_pad = U_pad
        self.U_tok_t = torch.from_numpy(U_tok)                     # [Nu, L, d] frozen buffer
        self.U_pad_t = torch.from_numpy(U_pad)                     # [Nu, L] bool
        return Nu

    def idx_of(self, text):
        j = self.name2idx.get(text)
        if j is None:                                             # should not happen (closed set)
            raise KeyError("sentence not in closed set: %r" % text)
        return j

    # ---- token-level grounding-probe support: reps + slot/filler token spans via offsets ----
    @staticmethod
    def _extract(reps_i, offs_i, text, word):
        """Mean of token reps whose char offsets overlap `word` in `text`. reps_i [SENT_CAP,d]."""
        m = re.search(r"\b" + re.escape(word) + r"\b", text)
        if m is None:
            return reps_i[0]
        s, e = m.span()
        sel = [i for i, (a, b) in enumerate(offs_i) if (a < e and b > s)]
        if not sel:
            sel = [0]
        return reps_i[sel].mean(axis=0)

    def batch_word_token_reps(self, texts, slot_words, fill_words):
        """Batched: encode all texts' token reps ONCE (transformer batched), then extract the
        slot-word rep and filler-word rep per text via tokenizer offsets. Returns (slot [N,d],
        fill [N,d])."""
        N = len(texts)
        ids = np.full((N, SENT_CAP), self.pad_id, dtype=np.int64)
        offs_list = []
        for i, t in enumerate(texts):
            enc = self.tok.encode(t)
            e = enc.ids[:SENT_CAP]
            ids[i, :len(e)] = e
            offs_list.append(enc.offsets[:SENT_CAP])
        reps = np.zeros((N, SENT_CAP, self.d), dtype=np.float32)
        for i in range(0, N, 256):
            h, _ = self.model.token_reps(torch.from_numpy(ids[i:i + 256]))
            reps[i:i + 256] = h.numpy()
        slot_out = np.zeros((N, self.d), dtype=np.float32)
        fill_out = np.zeros((N, self.d), dtype=np.float32)
        for i in range(N):
            slot_out[i] = self._extract(reps[i], offs_list[i], texts[i], slot_words[i])
            fill_out[i] = self._extract(reps[i], offs_list[i], texts[i], fill_words[i])
        return slot_out, fill_out


# ---------------- build per-example index tensors (event -> unique-sentence id) ----------------
def _event_texts(ex, rng_tmpl):
    """Re-render each event to the SAME template-randomized surface, returning the per-event sentence
    list (so we can map to unique-sentence ids). Query is separate."""
    parts = []
    for sl, fl in zip(ex["slots"], ex["fills"]):
        tmpl = EVENT_TEMPLATES[int(rng_tmpl.integers(0, len(EVENT_TEMPLATES)))]
        parts.append(tmpl.format(slot=SLOT_NOUNS[int(sl)], fill=COLORS[int(fl)]))
    q = QUERY_TEMPLATE.format(slot=SLOT_NOUNS[int(ex["query"])])
    return parts, q


def build_index_batch(examples, enc, seed):
    """Returns dict of tensors: ev_idx [B,Lmax] long (unique-sentence id per event; 0 on pad),
    q_idx [B] long, active [B,Lmax] float32, answer [B] long. Reps are looked up from enc.U_tok_t."""
    rng_tmpl = np.random.default_rng(seed + 313)
    B = len(examples)
    lengths = [len(ex["slots"]) for ex in examples]
    Lmax = max(lengths)
    ev_idx = np.zeros((B, Lmax), dtype=np.int64)
    q_idx = np.zeros((B,), dtype=np.int64)
    active = np.zeros((B, Lmax), dtype=np.float32)
    answer = np.zeros((B,), dtype=np.int64)
    for i, ex in enumerate(examples):
        ev_texts, q_text = _event_texts(ex, rng_tmpl)
        for t, s in enumerate(ev_texts):
            ev_idx[i, t] = enc.idx_of(s)
        active[i, :len(ev_texts)] = 1.0
        q_idx[i] = enc.idx_of(q_text)
        answer[i] = ex["answer"]
    return {"ev_idx": torch.from_numpy(ev_idx), "q_idx": torch.from_numpy(q_idx),
            "active": torch.from_numpy(active), "answer": torch.from_numpy(answer)}


# ---------------- ROLE-SEPARATED content-gated overwrite WM (THE ONE VARIABLE) ----------------
class RoleSeparatedGatedWM(nn.Module):
    """SAME gated-overwrite mechanism as exp_selective_overwrite_recall_wm_v1.ContentGatedWM (K
    content-address keys + learned write gate + gated OVERWRITE + value-proj + readout). THE ONE
    VARIABLE vs f82370cd1: the event rep is no longer ONE pooled vector. TWO learned role queries
    attend (softmax over token positions, position-invariant, parser-free) over the event's FROZEN
    token reps -> a SLOT-role rep (the ADDRESS) and a FILLER-role rep (the stored VALUE). So the
    address and the value are read from DIFFERENT tokens; the WM can learn a FILLER-INVARIANT slot
    address because the address signal is no longer entangled with the filler it stores.

    U_tok [Nu, L, d] / U_pad [Nu, L] are the FROZEN cached token reps of the closed sentence set;
    forward applies the (learned) role queries to ALL Nu, then GATHERS per event by unique-sentence
    id (so [B, Lmax, L, d] is never materialized)."""

    def __init__(self, seed, d_enc, d_mem, k_slots, hidden, v_fill, addr_temp, U_tok, U_pad):
        super().__init__()
        self.k_slots = k_slots
        self.d_mem = d_mem
        self.d_enc = d_enc
        self.addr_temp = addr_temp
        self.U_tok = U_tok              # plain attrs (frozen, shared across arms; not in state_dict)
        self.U_pad = U_pad
        g = torch.Generator().manual_seed(seed + 1234)
        # TWO learned role queries: slot-role (address) + filler-role (value). Small init like the
        # shelved slot_attention_wm.role_query (Frankland&Greene role-general attention).
        rq = torch.empty(2, d_enc)
        rq.normal_(0.0, 0.02, generator=g)
        self.role_query = nn.Parameter(rq)                            # [2, d_enc] (0=slot, 1=fill)
        key = torch.empty(k_slots, d_enc)
        key.normal_(0.0, 1.0, generator=g).div_(math.sqrt(d_enc))
        self.key = nn.Parameter(key)                                  # [K, d_enc] address keys
        self.write_gate = nn.Sequential(nn.Linear(d_enc, hidden), nn.Tanh(), nn.Linear(hidden, 1))
        self.value_proj = nn.Linear(d_enc, d_mem)                     # filler rep -> stored candidate
        self.readout = nn.Linear(d_mem, v_fill)                       # stored content -> filler class
        with torch.no_grad():
            for m in list(self.write_gate) + [self.value_proj, self.readout]:
                if isinstance(m, nn.Linear):
                    w = torch.empty_like(m.weight)
                    w.normal_(0.0, 0.1, generator=g)
                    m.weight.copy_(w)
                    m.bias.zero_()

    def wm_params(self):
        """role queries + keys + write-gate + value-proj (everything BUT the readout) -- frozen in
        the RANDOM_INIT control."""
        return ([self.role_query, self.key] + list(self.write_gate.parameters())
                + list(self.value_proj.parameters()))

    def _role_reps(self):
        """Apply the learned role queries to ALL cached unique token reps. Returns slot_reps_u,
        fill_reps_u each [Nu, d_enc]. Cheap (Nu x L x d)."""
        d = self.d_enc
        scores = torch.einsum("nld,rd->nrl", self.U_tok, self.role_query) / math.sqrt(d)  # [Nu,2,L]
        scores = scores.masked_fill(self.U_pad.unsqueeze(1), float("-inf"))
        attn = torch.softmax(scores, dim=-1)                              # [Nu, 2, L]
        fillers = torch.einsum("nrl,nld->nrd", attn, self.U_tok)          # [Nu, 2, d]
        return fillers[:, 0, :], fillers[:, 1, :]                         # slot_rep, fill_rep

    def _address(self, x):
        """x [., d_enc] -> softmax over K slots."""
        return torch.softmax(x @ self.key.t() / self.addr_temp, dim=-1)

    def read_features(self, batch):
        """Run the WM over the event stream; read the queried slot -> h_read [B, d_mem]. Address =
        slot-role rep; stored value = filler-role rep. Overwrite update is sequential (bit-equivalent
        to the proven per-step loop)."""
        slot_u, fill_u = self._role_reps()                               # [Nu, d] each
        ev_idx = batch["ev_idx"]; active = batch["active"]; q_idx = batch["q_idx"]
        B, Lmax = ev_idx.shape
        ev_slot = slot_u[ev_idx]                                         # [B, Lmax, d] address per event
        ev_fill = fill_u[ev_idx]                                         # [B, Lmax, d] value per event
        flat_slot = ev_slot.reshape(B * Lmax, self.d_enc)
        addr = self._address(flat_slot).reshape(B, Lmax, self.k_slots)   # [B,L,K]
        wgate = torch.sigmoid(self.write_gate(flat_slot)).reshape(B, Lmax)   # [B,L]
        cand = self.value_proj(ev_fill.reshape(B * Lmax, self.d_enc)).reshape(B, Lmax, self.d_mem)
        h = torch.zeros(B, self.k_slots, self.d_mem)
        for t in range(Lmax):
            w = (addr[:, t] * (wgate[:, t] * active[:, t]).unsqueeze(-1)).unsqueeze(-1)  # [B,K,1]
            h = (1.0 - w) * h + w * cand[:, t].unsqueeze(1)              # gated OVERWRITE (last wins)
        addr_q = self._address(slot_u[q_idx])                           # [B,K] query addresses by slot-role
        return (addr_q.unsqueeze(-1) * h).sum(dim=1)                     # [B, d_mem] h_read

    def forward(self, batch):
        return self.readout(self.read_features(batch))                  # [B, V]


# ---------------- train / eval ----------------
def _eval_acc(logits, answer):
    return float((logits.argmax(dim=-1) == answer).float().mean().item())


def _minibatch(tr_batch, idx):
    return {k: v[idx] for k, v in tr_batch.items()}


def train_arm(wm, tr_batch, ev_batch, steps, lr, train_params, seed, log_tag, batch=None):
    torch.manual_seed(seed)
    g = torch.Generator().manual_seed(seed + 555)
    opt = torch.optim.Adam(train_params, lr=lr)
    N = tr_batch["answer"].shape[0]
    loss_curve = []
    ema = None
    ema0 = None                       # ema snapshot at the warmup point (for the STUCK-break)
    stuck_break = False
    step = 0
    for step in range(steps):
        opt.zero_grad()
        if batch is not None and batch < N:
            idx = torch.randint(0, N, (batch,), generator=g)
            mb = _minibatch(tr_batch, idx)
        else:
            mb = tr_batch
        logits = wm(mb)
        loss = F.cross_entropy(logits, mb["answer"])
        loss.backward()
        opt.step()
        lv = float(loss.item())
        ema = lv if ema is None else 0.9 * ema + 0.1 * lv
        if step == 30:
            ema0 = ema
        if step == 0 or (step + 1) % max(1, steps // 8) == 0:
            loss_curve.append((step, lv))
        if step >= 400 and ema is not None and ema < EARLY_STOP_LOSS:
            break
        # STUCK-break: a FLAT trajectory (loss not descended by >3% of the warmup ema after step 300)
        # is going nowhere -- break to save compute. A genuine LEARNER descends and keeps the full
        # budget (fair recipe). Only cuts dead-flat runs (the f82370cd1 failure mode).
        if step >= 300 and ema0 is not None and ema > 0.97 * ema0:
            stuck_break = True
            break
    wm.eval()
    with torch.no_grad():
        ev_logits = wm(ev_batch)
        acc = _eval_acc(ev_logits, ev_batch["answer"])
        tr_logits = wm(tr_batch)
        tr_acc = _eval_acc(tr_logits, tr_batch["answer"])
    wm.train()
    first_loss = loss_curve[0][1] if loss_curve else float("nan")
    last_loss = loss_curve[-1][1] if loss_curve else float("nan")
    _log("  [%s seed=%d] eval_acc=%.4f train_acc=%.4f loss %.3f->%.3f ema=%.3f steps=%d"
         % (log_tag, seed, acc, tr_acc, first_loss, last_loss,
            ema if ema is not None else float("nan"), step + 1))
    return dict(eval_acc=acc, train_acc=tr_acc, ev_logits=ev_logits.detach(),
                loss_curve=loss_curve, first_loss=first_loss, last_loss=last_loss,
                ema=float(ema) if ema is not None else float("nan"), steps_run=step + 1,
                stuck_break=bool(stuck_break))


def train_readout_cached(wm, tr_batch, ev_batch, steps, lr, seed, log_tag):
    """CONTROL fast-path: WM frozen -> read features fixed -> fit ONLY the readout on cached feats."""
    torch.manual_seed(seed)
    with torch.no_grad():
        tr_feat = wm.read_features(tr_batch)
        ev_feat = wm.read_features(ev_batch)
    opt = torch.optim.Adam(wm.readout.parameters(), lr=lr)
    loss_curve = []
    for step in range(steps):
        opt.zero_grad()
        loss = F.cross_entropy(wm.readout(tr_feat), tr_batch["answer"])
        loss.backward()
        opt.step()
        if step == 0 or (step + 1) % max(1, steps // 8) == 0:
            loss_curve.append((step, float(loss.item())))
    with torch.no_grad():
        ev_logits = wm.readout(ev_feat)
        acc = _eval_acc(ev_logits, ev_batch["answer"])
    _log("  [%s seed=%d] eval_acc=%.4f loss %.3f->%.3f"
         % (log_tag, seed, acc, loss_curve[0][1], loss_curve[-1][1]))
    return dict(eval_acc=acc, ev_logits=ev_logits.detach(),
                first_loss=loss_curve[0][1], last_loss=loss_curve[-1][1])


# ---------------- TOKEN-LEVEL grounding probe (the fix has signal iff this fires) ----------------
def token_binding_probe(enc, seed, n=4000, ntr=3000):
    """Locate the slot-noun token(s) and filler-color token(s) in each event sentence via offsets;
    linear-probe slot-token rep -> slot id AND filler-token rep -> filler id SEPARATELY. Both ~1.0
    => frozen v2 TOKEN reps carry slot (on slot tokens) + filler (on filler tokens) separably ->
    role-separated rep supports role-filler binding."""
    from sklearn.linear_model import LogisticRegression
    rng = np.random.default_rng(seed + 4242)
    slots = np.zeros(n, dtype=np.int64)
    fills = np.zeros(n, dtype=np.int64)
    texts = []
    slot_words = []
    fill_words = []
    for i in range(n):
        sl = int(rng.integers(0, len(SLOT_NOUNS))); fl = int(rng.integers(0, V_FILL))
        tm = EVENT_TEMPLATES[int(rng.integers(0, len(EVENT_TEMPLATES)))]
        texts.append(tm.format(slot=SLOT_NOUNS[sl], fill=COLORS[fl]))
        slot_words.append(SLOT_NOUNS[sl]); fill_words.append(COLORS[fl])
        slots[i] = sl; fills[i] = fl
    slot_reps, fill_reps = enc.batch_word_token_reps(texts, slot_words, fill_words)

    def _probe(X, y):
        mu = X[:ntr].mean(0, keepdims=True); sd = X[:ntr].std(0, keepdims=True) + 1e-8
        clf = LogisticRegression(max_iter=400, C=1.0)
        clf.fit((X[:ntr] - mu) / sd, y[:ntr])
        return float((clf.predict((X[ntr:] - mu) / sd) == y[ntr:]).mean())

    slot_acc = _probe(slot_reps, slots)
    fill_acc = _probe(fill_reps, fills)
    # cross-check: does the SLOT token leak filler (or vice versa)? A clean separation wants LOW.
    slot_leaks_fill = _probe(slot_reps, fills)
    fill_leaks_slot = _probe(fill_reps, slots)
    return {"slot_token_probe_acc": slot_acc, "slot_chance": 1.0 / len(SLOT_NOUNS),
            "filler_token_probe_acc": fill_acc, "filler_chance": CHANCE,
            "slot_token_leaks_filler": slot_leaks_fill, "filler_token_leaks_slot": fill_leaks_slot,
            "carries_slot_on_slot_tokens": bool(slot_acc >= TOKEN_PROBE_MIN),
            "carries_filler_on_filler_tokens": bool(fill_acc >= TOKEN_PROBE_MIN)}


# ---------------- capacity probe (expressiveness vs generalization localizer) ----------------
def capacity_probe(enc, seed=7):
    """Train the SAME LEARNED_WM full-batch on a TINY set (memorization regime). If train_acc is high
    AND eval_acc now GENERALIZES (>> chance), the role-separated rep fixed the f82370cd1 overfit
    (train 0.96 / eval 0.07). Same mechanism + recipe (full-batch)."""
    tr = calib.gen_dataset(CAP_PROBE_N, np.random.default_rng(seed))
    ev = calib.gen_dataset(500, np.random.default_rng(seed + 777))
    trb = build_index_batch(tr, enc, seed)
    evb = build_index_batch(ev, enc, seed + 777)
    wm = RoleSeparatedGatedWM(seed, enc.d, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP,
                              enc.U_tok_t, enc.U_pad_t)
    res = train_arm(wm, trb, evb, CAP_PROBE_STEPS, LR, list(wm.parameters()), seed,
                    "CAPACITY_PROBE fullbatch n=%d" % CAP_PROBE_N, batch=None)  # full-batch
    return {"n_train": CAP_PROBE_N, "steps": CAP_PROBE_STEPS, "train_acc": res["train_acc"],
            "eval_acc": res["eval_acc"], "first_loss": res["first_loss"], "last_loss": res["last_loss"],
            "memorizes": bool(res["train_acc"] >= 0.70),
            "generalizes": bool(res["eval_acc"] >= CHANCE + 0.10)}


# ---------------- per-seed run ----------------
def run_seed(seed, enc, train_n, eval_n, steps_wm, steps_readout, n_random_init):
    rng = np.random.default_rng(seed)
    tr = calib.gen_dataset(train_n, rng)
    ev = calib.gen_dataset(eval_n, np.random.default_rng(seed + 777))
    tr_batch = build_index_batch(tr, enc, seed)
    ev_batch = build_index_batch(ev, enc, seed + 777)
    d_enc = enc.d

    # LEARNED_WM: train everything; restart on a dud trajectory (train-triggered).
    n_attempts = 0
    dud_train_accs = []
    for attempt in range(MAX_RESTARTS + 1):
        n_attempts = attempt + 1
        wseed = seed + attempt * 7919
        wm = RoleSeparatedGatedWM(wseed, d_enc, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP,
                                  enc.U_tok_t, enc.U_pad_t)
        learned = train_arm(wm, tr_batch, ev_batch, steps_wm, LR, list(wm.parameters()),
                            wseed, "LEARNED_WM a%d" % attempt, batch=BATCH)
        if learned["train_acc"] >= RETRY_TRAIN_ACC:
            break
        dud_train_accs.append(round(learned["train_acc"], 3))
        _log("  LEARNED_WM seed=%d attempt=%d DUD (train_acc=%.3f < %.2f) -> restart"
             % (seed, attempt, learned["train_acc"], RETRY_TRAIN_ACC))
    learned["n_attempts"] = n_attempts

    # RANDOM_INIT_WM controls: freeze role queries+keys+write-gate+value-proj; train ONLY readout.
    ri_accs = []
    ri_logits_first = None
    for c in range(n_random_init):
        cseed = seed * 100 + c
        wm_ri = RoleSeparatedGatedWM(cseed, d_enc, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP,
                                     enc.U_tok_t, enc.U_pad_t)
        for p in wm_ri.wm_params():
            p.requires_grad_(False)
        ri = train_readout_cached(wm_ri, tr_batch, ev_batch, steps_readout, LR, cseed,
                                  "RANDOM_INIT_WM c=%d" % c)
        ri_accs.append(ri["eval_acc"])
        if ri_logits_first is None:
            ri_logits_first = ri["ev_logits"]

    ps = power_stats(learned["eval_acc"], eval_n, ri_accs)

    def _digest(t):
        return hashlib.sha256(t.cpu().numpy().tobytes()).hexdigest()
    arms_differ = _digest(learned["ev_logits"]) != _digest(ri_logits_first)

    return {
        "seed": seed, "train_n": train_n, "eval_n": eval_n, "chance": CHANCE,
        "learned_wm": {"eval_acc": learned["eval_acc"], "train_acc": learned["train_acc"],
                       "first_loss": learned["first_loss"], "last_loss": learned["last_loss"],
                       "loss_curve": learned["loss_curve"], "ema": learned.get("ema"),
                       "n_attempts": learned.get("n_attempts", 1), "steps_run": learned.get("steps_run"),
                       "dud_train_accs": dud_train_accs,
                       "eval_minus_train": learned["eval_acc"] - learned["train_acc"]},
        "random_init_wm": {"accs": ri_accs, "mean": float(np.mean(ri_accs)),
                           "max": float(np.max(ri_accs)), "min": float(np.min(ri_accs))},
        "power": ps,
        "arms_differ_verified": bool(arms_differ),
    }


# ---------------- verdict ----------------
def decide_verdict(per_seed, tok_probe, cap_probe):
    learned_accs = [ps["learned_wm"]["eval_acc"] for ps in per_seed]
    train_accs = [ps["learned_wm"]["train_acc"] for ps in per_seed]
    ri_maxes = [ps["random_init_wm"]["max"] for ps in per_seed]
    gaps = [ps["power"]["gap"] for ps in per_seed]
    sigs = [ps["power"]["significant"] for ps in per_seed]

    ri_all = [a for ps in per_seed for a in ps["random_init_wm"]["accs"]]
    control_floor_ok = all(a < RI_NEAR_CHANCE for a in ri_all)

    loss_shapes = []
    stuck_any = False
    for ps in per_seed:
        fl, ll = ps["learned_wm"]["first_loss"], ps["learned_wm"]["last_loss"]
        descended = (ll < LOSS_DESCEND_RATIO * fl)
        loss_shapes.append({"seed": ps["seed"], "first_loss": fl, "last_loss": ll,
                            "descended": bool(descended)})
        if not descended:
            stuck_any = True

    proven = (all(a >= WM_PROVEN_MIN for a in learned_accs)
              and all(g >= MECH_MARGIN for g in gaps)
              and all(sigs)
              and control_floor_ok)
    cant_learn = all(a <= WM_CANT_LEARN_MAX for a in learned_accs)

    # generalization read (the whole point): eval vs train.
    generalizes = all(a >= WM_PROVEN_MIN for a in learned_accs)
    overfits = (all(t >= 0.70 for t in train_accs) and all(a <= WM_CANT_LEARN_MAX for a in learned_accs))
    reps_carry = bool(tok_probe["carries_slot_on_slot_tokens"]
                      and tok_probe["carries_filler_on_filler_tokens"])
    ground_note = ("TOKEN-LEVEL GROUNDING: slot-token->slot=%.3f (chance %.3f), filler-token->"
                   "filler=%.3f (chance %.3f); cross-leak slot->fill=%.3f fill->slot=%.3f. "
                   "-> role-separated reps %s binding."
                   % (tok_probe["slot_token_probe_acc"], tok_probe["slot_chance"],
                      tok_probe["filler_token_probe_acc"], tok_probe["filler_chance"],
                      tok_probe["slot_token_leaks_filler"], tok_probe["filler_token_leaks_slot"],
                      "SUPPORT" if reps_carry else "do NOT support"))
    cap_note = (" CAPACITY-PROBE (role-separated): full-batch overfit-%d train=%.3f eval=%.3f "
                "(memorizes=%s, generalizes=%s)."
                % (cap_probe["n_train"], cap_probe["train_acc"], cap_probe["eval_acc"],
                   cap_probe["memorizes"], cap_probe["generalizes"]))

    if not control_floor_ok:
        verdict = "CONTROL_FLOOR_BROKEN"
        msg = ("a RANDOM_INIT_WM control cleared %.2f (max=%.3f): the can-fail floor is not clean -> "
               "the role-separated path leaks a shortcut; margin not trustworthy. %s"
               % (RI_NEAR_CHANCE, max(ri_all), ground_note))
    elif proven:
        verdict = "WM_NL_PROVEN"
        msg = ("LEARNED_WM eval_acc=%s (train=%s) >> chance %.3f AND >> random-init (gap=%s, z=%s, "
               "beats ri_max), BOTH seeds, controls at floor -> the ROLE-SEPARATED content-gated WM "
               "learns a FILLER-INVARIANT slot address that GENERALIZES: genuine content-gated NL "
               "comprehension with role-filler binding. ceiling(oracle)=%.2f. %s%s"
               % ([round(a, 3) for a in learned_accs], [round(t, 3) for t in train_accs], CHANCE,
                  [round(g, 3) for g in gaps], [round(ps["power"]["z"], 2) for ps in per_seed],
                  ORACLE_CEILING, ground_note, cap_note))
    elif cant_learn:
        verdict = "STILL_CANT_LEARN"
        subpart = ("OVERFITS AGAIN (train high %s / eval chance): the role-separated address still does "
                   "not generalize -- the block is the ADDRESS-INVARIANCE learning, not the encoder."
                   % [round(t, 3) for t in train_accs] if overfits else
                   "STUCK_FLAT (loss did not descend): trainability/optimization block, not just "
                   "generalization." if stuck_any else
                   "DESCENDED-but-eval-chance: fits partially but the learned rule does not transfer.")
        msg = ("LEARNED_WM stalls near chance (eval=%s <= %.2f, train=%s). SUB-PART: %s %s%s"
               % ([round(a, 3) for a in learned_accs], WM_CANT_LEARN_MAX,
                  [round(t, 3) for t in train_accs], subpart, ground_note, cap_note))
    else:
        verdict = "WM_NL_PARTIAL"
        msg = ("LEARNED_WM eval=%s (train=%s, chance %.3f, gaps=%s, sig=%s): beats random-init but not "
               "the WM_NL_PROVEN bar (>=%.2f both seeds, gap>=%.2f, significant). %s%s"
               % ([round(a, 3) for a in learned_accs], [round(t, 3) for t in train_accs], CHANCE,
                  [round(g, 3) for g in gaps], sigs, WM_PROVEN_MIN, MECH_MARGIN, ground_note, cap_note))

    bands = {"chance": CHANCE, "oracle_ceiling": ORACLE_CEILING, "wm_proven_min": WM_PROVEN_MIN,
             "wm_cant_learn_max": WM_CANT_LEARN_MAX, "mech_margin": MECH_MARGIN,
             "z_thresh": Z_THRESH, "ri_near_chance": RI_NEAR_CHANCE, "token_probe_min": TOKEN_PROBE_MIN,
             "learned_accs": learned_accs, "train_accs": train_accs, "ri_maxes": ri_maxes, "gaps": gaps,
             "significant_per_seed": [bool(s) for s in sigs], "control_floor_ok": bool(control_floor_ok),
             "loss_shapes": loss_shapes, "generalizes": bool(generalizes), "overfits_again": bool(overfits),
             "token_reps_carry_binding": reps_carry, "capacity_probe": cap_probe,
             "ground_note": ground_note}
    return verdict, msg, bands


# ---------------- self-test ----------------
def run_self_test():
    _log("SELF-TEST: load REAL v2 encoder + token-cache + tiny end-to-end ...")
    assert os.path.exists(V2_CKPT), "v2 checkpoint missing: %s" % V2_CKPT
    enc = FrozenV2Encoder(V2_CKPT)
    n_cached = enc.build_cache()
    _log("  cached %d unique sentence TOKEN reps (d=%d, L=%d)" % (n_cached, enc.d, SENT_CAP))
    assert n_cached >= 3000, "closed sentence set smaller than expected"

    # overwrite (not accumulate) unit check -- the load-bearing mechanism invariant
    with torch.no_grad():
        h = torch.zeros(1, 1, 3)
        for cand_val in (torch.tensor([[1.0, 0.0, 0.0]]), torch.tensor([[0.0, 1.0, 0.0]])):
            w = torch.ones(1, 1, 1)
            h = (1.0 - w) * h + w * cand_val.unsqueeze(1)
        assert torch.allclose(h.squeeze(), torch.tensor([0.0, 1.0, 0.0])), "overwrite kept a blend"

    # role queries produce DIFFERENT slot vs fill reps (the role-separation must be non-degenerate)
    wm = RoleSeparatedGatedWM(7, enc.d, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP,
                              enc.U_tok_t, enc.U_pad_t)
    with torch.no_grad():
        slot_u, fill_u = wm._role_reps()
    assert slot_u.shape == (n_cached, enc.d) and fill_u.shape == (n_cached, enc.d), "role rep shape"
    assert not torch.allclose(slot_u, fill_u), "slot-role and filler-role reps identical (degenerate)"

    # tiny full pipeline: real encoder + real role-separated WM + train, reduced scale
    res = run_seed(7, enc, train_n=200, eval_n=200, steps_wm=120, steps_readout=60, n_random_init=3)
    lw = res["learned_wm"]["eval_acc"]
    ri = res["random_init_wm"]["mean"]
    _log("  tiny: LEARNED_WM=%.3f RANDOM_INIT_WM(mean)=%.3f gap=%.3f arms_differ=%s"
         % (lw, ri, res["power"]["gap"], res["arms_differ_verified"]))
    assert res["arms_differ_verified"], "arms bit-identical (LEARNED vs RANDOM_INIT eval logits)"
    assert 0.0 <= lw <= 1.0 and 0.0 <= ri <= 1.0, "acc out of range"

    # forward determinism on fixed index batch
    ex = calib.gen_dataset(16, np.random.default_rng(1))
    b = build_index_batch(ex, enc, 1)
    with torch.no_grad():
        l1 = wm(b); l2 = wm(b)
    assert torch.allclose(l1, l2), "forward not deterministic on fixed reps"

    # token-level grounding probe (small)
    probe = token_binding_probe(enc, 7, n=600, ntr=450)
    _log("  token probe: slot=%.3f filler=%.3f (chance %.3f/%.3f) leak s->f=%.3f f->s=%.3f"
         % (probe["slot_token_probe_acc"], probe["filler_token_probe_acc"], probe["slot_chance"],
            probe["filler_chance"], probe["slot_token_leaks_filler"], probe["filler_token_leaks_slot"]))
    _log("SELF-TEST PASS")
    return {"tiny": {"learned_wm": lw, "random_init_wm_mean": ri, "gap": res["power"]["gap"],
                     "arms_differ": res["arms_differ_verified"]},
            "n_cached": n_cached, "token_probe_small": probe}


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--train-n", type=int, default=FULL_TRAIN)
    ap.add_argument("--eval-n", type=int, default=FULL_EVAL)
    ap.add_argument("--steps-wm", type=int, default=STEPS_WM)
    args = ap.parse_args()

    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))
    run_mode = "self_test" if args.self_test else "full"
    expected_units = 1 if run_mode == "self_test" else len(SEEDS_FULL)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(OUTPUT_DIR, {
            "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (real v2 encoder + token-cache + role-separated WM + overwrite unit + role-nondegenerate + determinism + token-probe)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "chance": CHANCE, "selftest": st})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    _log("FULL: train_n=%d eval_n=%d steps_wm=%d seeds=%s chance=%.4f K=%d encoder=real_v2_frozen role_sep=on"
         % (args.train_n, args.eval_n, args.steps_wm, SEEDS_FULL, CHANCE, K_SLOTS))
    enc = FrozenV2Encoder(V2_CKPT)
    n_cached = enc.build_cache()
    _log("  cached %d unique sentence TOKEN reps (d=%d, L=%d)" % (n_cached, enc.d, SENT_CAP))

    _log("--- TOKEN-LEVEL grounding probe (the fix has signal iff this fires) ---")
    tok_probe = token_binding_probe(enc, 7)
    _log("  slot_token=%.3f (chance %.3f) filler_token=%.3f (chance %.3f) leak s->f=%.3f f->s=%.3f"
         % (tok_probe["slot_token_probe_acc"], tok_probe["slot_chance"],
            tok_probe["filler_token_probe_acc"], tok_probe["filler_chance"],
            tok_probe["slot_token_leaks_filler"], tok_probe["filler_token_leaks_slot"]))

    _log("--- capacity probe (full-batch memorize-vs-generalize on the role-separated rep) ---")
    cap_probe = capacity_probe(enc, seed=7)
    _log("  capacity: train_acc=%.3f eval_acc=%.3f memorizes=%s generalizes=%s"
         % (cap_probe["train_acc"], cap_probe["eval_acc"], cap_probe["memorizes"], cap_probe["generalizes"]))

    per_seed = []
    for seed in SEEDS_FULL:
        _log("--- seed %d ---" % seed)
        per_seed.append(run_seed(seed, enc, args.train_n, args.eval_n, args.steps_wm,
                                 STEPS_READOUT, N_RANDOM_INIT))
    verdict, msg, bands = decide_verdict(per_seed, tok_probe, cap_probe)
    elapsed = time.perf_counter() - t0

    _atomic_write_metrics(OUTPUT_DIR, {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "%s | chance=%.4f | %s" % (verdict, CHANCE, msg[:140]),
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "chance": CHANCE, "oracle_ceiling_ref": ORACLE_CEILING, "bands": bands,
        "token_binding_probe": tok_probe, "capacity_probe": cap_probe,
        "cardinality_ok": bool(len(per_seed) == len(SEEDS_FULL)),
        "expected_n_units": len(SEEDS_FULL), "n_units_done": len(per_seed),
        "params": {"K_SLOTS": K_SLOTS, "D_MEM": D_MEM, "D_ENC": enc.d, "HIDDEN": HIDDEN,
                   "ADDR_TEMP": ADDR_TEMP, "SENT_CAP": SENT_CAP, "STEPS_WM": args.steps_wm,
                   "STEPS_READOUT": STEPS_READOUT, "LR": LR, "N_RANDOM_INIT": N_RANDOM_INIT,
                   "train_n": args.train_n, "eval_n": args.eval_n, "seeds": list(SEEDS_FULL),
                   "n_cached_sentences": n_cached, "encoder": "real_v2_frozen",
                   "event_rep": "role_separated_two_role_queries_token_level",
                   "v2_ckpt": os.path.relpath(V2_CKPT, REPO_ROOT)},
        "per_seed": per_seed,
        "start_marker_written": True, "crash_diagnostic_present": True,
        "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns"})
    _log("VERDICT: %s" % verdict)
    _log("  %s" % msg)
    _log("DONE full in %.1fs" % elapsed)


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
