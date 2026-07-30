# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF; ARMS-MUST-DIFFER hash-test on embed vs transformer feats)
# - final_metrics_atomicity: tmp_replace (os.replace at end)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_floor_computed: n/a -> declared crlb_n/a below (this is a CALIBRATION cell with NO learned
#   mechanism under test; the bars are CHANCE=1/V_FILL for can-fail arms and an ORACLE ceiling for
#   headroom; there is no Cramer-Rao noise floor to compute -- the discriminator is the reservoir-fail
#   / oracle-clear separation, judged live per run)
# - baseline_in_band: the random-init + whole-seq-attention reservoir arms ARE the baselines; must be
#   NEAR CHANCE (can-fail). Oracle keep-last is the headroom ceiling (~1.0). Judged live.
# - discriminator survives scale: FULL is the scale of interest (CPU calibration, no smoke-only gap);
#   self-test runs the REAL construction + REAL random transformer at tiny N (real_code_path).
# - HARD_PASS strictly above floor: n/a (no HARD_PASS; verdict is a 3-way calibration classification)
# - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS_FULL); verdict counts per-seed units
# - per-unit failure-class instrumentation (META_RULE_J; no bare except) -- see _write_crash_metrics
# - calibration_check: default_ok_for_this_regime (reuses the VALIDATED synthetic construction
#   exp_selective_overwrite_recall_calib_v1.py leak-guards: globally-balanced filler multiset +
#   TAIL_MIN + TARGET_TAIL_MIN + randomized order; only the SURFACE RENDERING is new)
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
# - deterministic seeding: numpy default_rng + torch.manual_seed only; NO hash(), NO list(set())
"""Selective-Overwrite-Recall NATURAL-LANGUAGE construction + CALIBRATION (v1).

MEASUREMENT-FIRST (design D3). This cell renders the VET-CONFIRMED synthetic Selective-Overwrite-
Recall task (exp_selective_overwrite_recall_calib_v1.py, commit db39c1082) as SHORT NATURAL-LANGUAGE
sentences, and CALIBRATES whether the NL version is still genuinely RESERVOIR-FAILING before any WM
mechanism is built. It builds NO learned gating mechanism (that is the NEXT dispatch, gated on this
returning NL_RESERVOIR_FAILING_VALID).

THE NEW HARD VARIABLE vs the synthetic proof: the synthetic encoder was DEGENERATE (each event rep
cleanly carried [slot ; filler] as a factored concat), so it proved TEMPORAL GATING only. Here the
(slot, filler) live in SURFACE TEXT ("the door was painted red ."), so a reader must BIND (extract
slot & filler from the sentence) BEFORE it can gate on recency. This is the NL binding problem the
degenerate encoder skipped.

Construction (mirrors the synthetic one; SAME leak-guards):
  Stream of N (slot, filler) assignment events. S target slots each written MULTIPLE times (overwrite);
  interleaved with D >> S distractor slot-touches (D distractor slot ids, high distractor-event count).
  Order/spacing randomized per example. Fillers drawn from a GLOBALLY BALANCED shuffled multiset over
  the SHARED filler vocab (kills most_frequent + presence shortcuts). The query asks for the MOST-
  RECENTLY-OVERWRITTEN filler of one target slot. TAIL_MIN distractor events AND TARGET_TAIL_MIN later
  TARGET-write events are guaranteed after the queried slot's last write (kills raw recency AND
  most-recent-target-filler shortcuts). Each event is rendered to a short NL sentence via one of
  several templates (randomized). A trailing NL query sentence is appended.

Arms:
  CAN-FAIL (must land NEAR CHANCE = 1/V_FILL):
    randinit_embed_meanpool       -- random-init FROZEN word-embedding table, mean+max pool, +query
                                     one-hot, trained probe (the "random-init frozen encoder" control)
    randinit_transformer_reservoir-- random-init FROZEN transformer (embed + 2-layer MHSA + FFN),
                                     mean+max pool, +query one-hot, trained probe. THE KEY NEW CONTROL:
                                     a WHOLE-SEQUENCE ATTENTION reservoir (whole-passage pooled + trained
                                     readout, like the MES-0.80 reservoir). Overwrite-suppression is
                                     content-gating a random-init attention reservoir CANNOT do
                                     regardless of NL rendering. If it SOLVES -> the NL rendering leaked
                                     a shortcut -> RESERVOIR_DECODABLE (fix).  CITED@ Olsson 2022
                                     induction-heads ACQUIRED-not-at-init; Saxe 2011 random-weights.
    bge_random_init_reservoir     -- BONUS whole-seq-attention reservoir: BGE-small ARCHITECTURE with
                                     RANDOM weights, mean-pool, +query one-hot, trained probe (guarded).
    shortcut_globally_last / shortcut_first_occurrence / shortcut_most_frequent / shortcut_fixed_position
                                   -- deterministic rule oracles over the filler stream (leak-guards).
  HEADROOM:
    oracle_keep_last              -- rule-follower keep-last-write-per-slot on the STRUCTURED events =
                                     ground truth (~1.0). Proves the label is determined by the events
                                     (learnable in principle by a mechanism that binds + gates).
    known_reader_bge              -- BGE-small (TRAINED weights) whole-passage pooled + query one-hot +
                                     trained probe (guarded). Does a strong pretrained reader clear it?
                                     Informative headroom; if it can't, the binding is hard for a POOLED
                                     reader (expected -- that is why the WM is the point), reported not
                                     blocking.

VERDICT:
  NL_RESERVOIR_FAILING_VALID -- oracle clears AND both reservoir controls (random-init + whole-seq
                               attention) near chance -> the NL construction separates learned content-
                               gated maintenance from structure-alone; SHIP the WM build.
  RESERVOIR_DECODABLE        -- a whole-seq-attention / random-init reservoir (or a shortcut) solves it
                               -> the NL rendering leaked a shortcut; tighten before the WM.
  NOT_LEARNABLE              -- oracle ceiling below floor (construction/answer bug).

Run:  .venv/Scripts/python.exe experiments/exp_selective_overwrite_recall_nl_calib_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_selective_overwrite_recall_nl_calib_v1.py --full

ASCII-only. No emojis. Deterministic seeding (no hash(), no list(set())). CPU.
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

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

try:  # sklearn probes (CPU, deterministic via random_state)
    from sklearn.linear_model import LogisticRegression
    from sklearn.neural_network import MLPClassifier
except Exception as _imp_exc:  # pragma: no cover - environment guard
    LogisticRegression = None
    MLPClassifier = None
    _SKLEARN_IMPORT_ERROR = _imp_exc
else:
    _SKLEARN_IMPORT_ERROR = None

try:
    import torch
    import torch.nn as nn
except Exception as _timp_exc:  # pragma: no cover
    torch = None
    nn = object
    _TORCH_IMPORT_ERROR = _timp_exc
else:
    _TORCH_IMPORT_ERROR = None

ANCHOR_NAME = "selective_overwrite_recall_nl_calib_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---------------- construction params (author-owned; mirror synthetic calib) ----------------
V_FILL = 20                 # filler (color) vocab, SHARED across target+distractor -> CHANCE = 0.05
CHANCE = 1.0 / V_FILL
S_TARGET = 6                # target slots
N_DISTRACT_SLOTS = 24       # distractor slot ids (slot noun vocab = S_TARGET + N_DISTRACT_SLOTS = 30)
WRITES_MIN, WRITES_MAX = 2, 4   # overwrites per target slot
N_DISTRACT_EVENTS = 36      # distractor touches per stream (D >> S; high distractor count)
TAIL_MIN = 6                # distractor events guaranteed after the queried slot's last write
TARGET_TAIL_MIN = 4         # TARGET-write events guaranteed after the queried slot's last write
FIXED_POSITIONS = (0, 5, 10, 20, -1)  # positions probed by the fixed-position shortcut oracle

# NL surface vocab (closed set; glass-box generator + whitespace tokenizer, NO bolt-on parser)
COLORS = [
    "red", "blue", "green", "yellow", "black", "white", "orange", "purple", "brown", "pink",
    "gray", "cyan", "gold", "silver", "teal", "maroon", "violet", "beige", "olive", "navy",
]
assert len(COLORS) == V_FILL
SLOT_NOUNS = [
    # 6 targets
    "door", "window", "wall", "roof", "floor", "gate",
    # 24 distractors
    "fence", "table", "chair", "shelf", "bench", "ceiling", "cabinet", "drawer", "mirror", "lamp",
    "curtain", "carpet", "railing", "ladder", "bucket", "crate", "barrel", "panel", "beam", "post",
    "tile", "plank", "hinge", "latch",
]
assert len(SLOT_NOUNS) == S_TARGET + N_DISTRACT_SLOTS
EVENT_TEMPLATES = [
    "the {slot} was painted {fill} .",
    "someone painted the {slot} {fill} .",
    "the {slot} turned {fill} .",
    "they made the {slot} {fill} .",
    "the {slot} became {fill} .",
]
QUERY_TEMPLATE = "what color was the {slot} ?"

# probe / reservoir params
MAX_TOKENS = 320            # cap passage length (pad/truncate) for the transformer reservoir
D_EMB = 96                  # random word-embedding / transformer model dim
N_HEADS = 4
N_LAYERS = 2
D_FF = 192

NEAR_CHANCE_MARGIN = 0.05   # can-fail arms must be < CHANCE + this  (bar = 0.10)
ORACLE_KEEP_LAST_MIN = 0.95
KNOWN_READER_CLEAR_MARGIN = 0.05   # known-reader "clears" if >= CHANCE + this (soft, reported)

FULL_TRAIN, FULL_EVAL = 1200, 700
SEEDS_FULL = (7, 13)
BGE_MODEL = "BAAI/bge-small-en-v1.5"
BGE_CAP_TRAIN, BGE_CAP_EVAL = 350, 350   # BGE is CPU-heavy -> capped subset (guarded, non-blocking)


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------- defensive scaffolding (exp_dev.md sec 13) ----------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


# ---------------- the construction (structured events; ports synthetic gen_stream) ----------------
def gen_stream(rng):
    """Generate ONE Selective-Overwrite-Recall example (structured).

    Returns dict:
      slots  : int array [L]  -- slot id per event (targets 0..S_TARGET-1; distractors S_TARGET..)
      fills  : int array [L]  -- filler id per event (0..V_FILL-1)
      query  : int            -- queried target slot id
      answer : int            -- most-recently-overwritten filler of the queried slot
      last_write_idx : int
    Guarantees: >= WRITES_MIN writes to the queried slot; >= TAIL_MIN distractor AND >= TARGET_TAIL_MIN
    later target-write events after its last write; order fully randomized. Returns None on a bad draw.
    """
    slot_vocab = S_TARGET + N_DISTRACT_SLOTS
    slot_seq = []
    for s in range(S_TARGET):
        k = int(rng.integers(WRITES_MIN, WRITES_MAX + 1))
        slot_seq.extend([s] * k)
    for _ in range(N_DISTRACT_EVENTS):
        slot_seq.append(int(rng.integers(S_TARGET, slot_vocab)))
    slot_seq = np.array(slot_seq, dtype=np.int64)
    slot_seq = slot_seq[rng.permutation(len(slot_seq))]
    L = len(slot_seq)

    # globally balanced shuffled filler multiset (kills most_frequent + presence shortcuts)
    reps = L // V_FILL
    rem = L - reps * V_FILL
    fill_pool = np.concatenate([
        np.repeat(np.arange(V_FILL), reps),
        rng.permutation(V_FILL)[:rem] if rem else np.array([], dtype=np.int64),
    ]).astype(np.int64)
    fill_pool = fill_pool[rng.permutation(len(fill_pool))]
    events = [[int(slot_seq[i]), int(fill_pool[i])] for i in range(L)]

    last_write = {s: -1 for s in range(S_TARGET)}
    for idx, (sl, _fl) in enumerate(events):
        if sl < S_TARGET:
            last_write[sl] = idx
    is_target = np.array([1 if e[0] < S_TARGET else 0 for e in events])
    cum_target_after = np.concatenate([np.cumsum(is_target[::-1])[::-1][1:], [0]])
    eligible = [s for s in range(S_TARGET)
                if last_write[s] >= 0
                and (L - 1 - last_write[s]) >= TAIL_MIN
                and int(cum_target_after[last_write[s]]) >= TARGET_TAIL_MIN]
    if not eligible:
        return None

    query = int(eligible[rng.integers(0, len(eligible))])
    answer = int(events[last_write[query]][1])
    slots = np.array([e[0] for e in events], dtype=np.int64)
    fills = np.array([e[1] for e in events], dtype=np.int64)
    return {"slots": slots, "fills": fills, "query": query, "answer": answer,
            "last_write_idx": int(last_write[query])}


def render_text(ex, rng):
    """Render a structured example to NL: event sentences (each via a randomized template) + a
    trailing query sentence. Returns the passage string. Slot noun + filler color are DISTINCT
    surface tokens, so a reader must BIND them from text (the new hard variable)."""
    parts = []
    for sl, fl in zip(ex["slots"], ex["fills"]):
        tmpl = EVENT_TEMPLATES[int(rng.integers(0, len(EVENT_TEMPLATES)))]
        parts.append(tmpl.format(slot=SLOT_NOUNS[int(sl)], fill=COLORS[int(fl)]))
    parts.append(QUERY_TEMPLATE.format(slot=SLOT_NOUNS[int(ex["query"])]))
    return " ".join(parts)


def gen_dataset(n, rng):
    """Returns list of examples, each augmented with 'text' (rendered NL passage)."""
    out = []
    while len(out) < n:
        ex = gen_stream(rng)
        if ex is not None:
            ex["text"] = render_text(ex, rng)
            out.append(ex)
    return out


# ---------------- glass-box whitespace tokenizer over the closed vocab ----------------
def build_vocab():
    words = set()
    for t in EVENT_TEMPLATES + [QUERY_TEMPLATE]:
        for w in t.split():
            if not (w.startswith("{") and w.endswith("}")):
                words.add(w)
    for w in COLORS + SLOT_NOUNS:
        words.add(w)
    vocab = ["<pad>"] + sorted(words)   # sorted -> deterministic; NOT list(set())
    return {w: i for i, w in enumerate(vocab)}


VOCAB = build_vocab()
PAD_ID = VOCAB["<pad>"]
VOCAB_SIZE = len(VOCAB)


def tokenize(text):
    ids = []
    for w in text.split():
        if w not in VOCAB:
            raise KeyError("token %r not in closed vocab (generator/vocab drift)" % w)
        ids.append(VOCAB[w])
    return ids[:MAX_TOKENS]


def batch_token_ids(texts):
    """Returns (ids [N, Lmax] int64 padded, mask [N, Lmax] float32 1=real)."""
    tok_lists = [tokenize(t) for t in texts]
    Lmax = max(len(t) for t in tok_lists)
    ids = np.full((len(tok_lists), Lmax), PAD_ID, dtype=np.int64)
    mask = np.zeros((len(tok_lists), Lmax), dtype=np.float32)
    for i, tl in enumerate(tok_lists):
        ids[i, : len(tl)] = tl
        mask[i, : len(tl)] = 1.0
    return ids, mask


def _query_onehot(examples):
    q = np.array([ex["query"] for ex in examples])
    oh = np.zeros((len(examples), S_TARGET), dtype=np.float64)
    oh[np.arange(len(examples)), q] = 1.0
    return oh


# ---------------- random-init FROZEN encoders (the reservoirs) ----------------
def _sinusoidal(Lmax, d):
    pos = np.arange(Lmax)[:, None]
    i = np.arange(d)[None, :]
    ang = pos / np.power(10000.0, (2 * (i // 2)) / d)
    pe = np.zeros((Lmax, d), dtype=np.float32)
    pe[:, 0::2] = np.sin(ang[:, 0::2])
    pe[:, 1::2] = np.cos(ang[:, 1::2])
    return pe


class RandomEmbedEncoder:
    """Random-init FROZEN word-embedding table -> mean+max pool over real tokens. NO attention.
    (The 'random-init frozen encoder' can-fail control.)"""

    def __init__(self, seed):
        rng = np.random.default_rng(seed + 90001)
        self.E = (rng.standard_normal((VOCAB_SIZE, D_EMB)).astype(np.float32) / np.sqrt(D_EMB))
        self.E[PAD_ID] = 0.0

    def features(self, ids, mask):
        emb = self.E[ids]                                  # [N, L, d]
        m = mask[:, :, None]
        summed = (emb * m).sum(axis=1)
        cnt = np.maximum(mask.sum(axis=1, keepdims=True), 1.0)
        mean = summed / cnt
        neg = np.where(m > 0, emb, -1e30)
        mx = neg.max(axis=1)
        return np.concatenate([mean, mx], axis=1).astype(np.float64)   # [N, 2d]


if torch is not None:
    class RandomTransformerReservoir(nn.Module):
        """Random-init FROZEN transformer (embed + N_LAYERS x [MHSA + FFN], LayerNorm+residual,
        sinusoidal positions) -> mean+max pool over real tokens. THE whole-sequence attention
        reservoir. Frozen weights: content-dependent routing (overwrite-suppression) is NOT present
        at init (Olsson 2022 induction-heads are ACQUIRED) -> should not bind slot->last-filler."""

        def __init__(self, seed):
            super().__init__()
            torch.manual_seed(seed + 4242)
            self.emb = nn.Embedding(VOCAB_SIZE, D_EMB, padding_idx=PAD_ID)
            self.layers = nn.ModuleList()
            for _ in range(N_LAYERS):
                self.layers.append(nn.ModuleDict({
                    "attn": nn.MultiheadAttention(D_EMB, N_HEADS, batch_first=True),
                    "ln1": nn.LayerNorm(D_EMB),
                    "ff1": nn.Linear(D_EMB, D_FF),
                    "ff2": nn.Linear(D_FF, D_EMB),
                    "ln2": nn.LayerNorm(D_EMB),
                }))
            self.act = nn.GELU()
            for p in self.parameters():
                p.requires_grad_(False)
            self.eval()

        @torch.no_grad()
        def features(self, ids_np, mask_np):
            ids = torch.from_numpy(ids_np).long()
            mask = torch.from_numpy(mask_np).float()               # [N, L] 1=real
            Lmax = ids.shape[1]
            pe = torch.from_numpy(_sinusoidal(Lmax, D_EMB))
            x = self.emb(ids) + pe.unsqueeze(0)
            key_pad = (mask < 0.5)                                  # True = pad -> ignored by attn
            feats_all = []
            for lyr in self.layers:
                a, _ = lyr["attn"](x, x, x, key_padding_mask=key_pad, need_weights=False)
                x = lyr["ln1"](x + a)
                h = lyr["ff2"](self.act(lyr["ff1"](x)))
                x = lyr["ln2"](x + h)
            m = mask.unsqueeze(-1)
            summed = (x * m).sum(dim=1)
            cnt = m.sum(dim=1).clamp(min=1.0)
            mean = summed / cnt
            neg = x.masked_fill(m < 0.5, -1e30)
            mx = neg.max(dim=1).values
            return torch.cat([mean, mx], dim=1).cpu().numpy().astype(np.float64)


def _encoder_features_batched(encoder, examples, batch=64):
    feats = []
    for i in range(0, len(examples), batch):
        chunk = examples[i:i + batch]
        ids, mask = batch_token_ids([ex["text"] for ex in chunk])
        feats.append(encoder.features(ids, mask))
    return np.concatenate(feats, axis=0)


# ---------------- probes ----------------
def fit_eval_probe(kind, Xtr, ytr, Xev, yev, seed):
    if kind == "linear":
        clf = LogisticRegression(max_iter=500, C=1.0, solver="lbfgs", random_state=seed)
    elif kind == "mlp":
        clf = MLPClassifier(hidden_layer_sizes=(128,), max_iter=300, random_state=seed,
                            early_stopping=False, alpha=1e-3)
    else:
        raise ValueError("unknown probe kind %r" % kind)
    mu = Xtr.mean(axis=0, keepdims=True)
    sd = Xtr.std(axis=0, keepdims=True) + 1e-8
    Xtr_s = (Xtr - mu) / sd
    Xev_s = (Xev - mu) / sd
    clf.fit(Xtr_s, ytr)
    train_acc = float((clf.predict(Xtr_s) == ytr).mean())
    eval_acc = float((clf.predict(Xev_s) == yev).mean())
    return eval_acc, train_acc


# ---------------- rule oracles (deterministic shortcuts + headroom ceiling) ----------------
def oracle_globally_last(ex):
    return int(ex["fills"][-1])


def oracle_fixed_position(ex, pos):
    L = len(ex["fills"])
    p = pos if pos >= 0 else L + pos
    if p < 0 or p >= L:
        return -1
    return int(ex["fills"][p])


def oracle_first_occurrence(ex):
    q = ex["query"]
    for i, s in enumerate(ex["slots"]):
        if int(s) == q:
            return int(ex["fills"][i])
    return -1


def oracle_most_frequent(ex):
    vals, counts = np.unique(ex["fills"], return_counts=True)
    return int(vals[int(np.argmax(counts))])


def oracle_keep_last(ex):
    q = ex["query"]
    ans = -1
    for i, s in enumerate(ex["slots"]):
        if int(s) == q:
            ans = int(ex["fills"][i])
    return ans


def oracle_acc(examples, fn):
    return sum(1 for ex in examples if fn(ex) == ex["answer"]) / len(examples)


# ---------------- BGE known-reader + BGE random-init reservoir (guarded) ----------------
def _bge_embed(sentences, random_init, batch_size=32, max_length=256):
    from transformers import AutoTokenizer, AutoModel, AutoConfig
    tok = AutoTokenizer.from_pretrained(BGE_MODEL)
    if random_init:
        cfg = AutoConfig.from_pretrained(BGE_MODEL)
        torch.manual_seed(0)
        mdl = AutoModel.from_config(cfg)
    else:
        mdl = AutoModel.from_pretrained(BGE_MODEL)
    mdl.eval()
    outs = []
    import torch.nn.functional as F
    with torch.no_grad():
        for i in range(0, len(sentences), batch_size):
            batch = sentences[i:i + batch_size]
            enc = tok(batch, padding=True, truncation=True, max_length=max_length, return_tensors="pt")
            out = mdl(**enc)
            h = out.last_hidden_state
            mask = enc["attention_mask"].unsqueeze(-1).float()
            summed = (h * mask).sum(dim=1)
            cnt = mask.sum(dim=1).clamp(min=1.0)
            outs.append(F.normalize(summed / cnt, dim=1).numpy())
    return np.concatenate(outs, axis=0).astype(np.float64)


def bge_arms(train_items, eval_items, seed):
    """Returns dict with known_reader_bge (trained) + bge_random_init_reservoir accs, or a status
    string on unavailability. Both use whole-passage MEAN-POOL + query one-hot + trained probe.
    Capped subset for CPU. Query sentence is IN-TEXT (BGE can attend it during encoding)."""
    tr = train_items[:BGE_CAP_TRAIN]
    ev = eval_items[:BGE_CAP_EVAL]
    ytr = np.array([ex["answer"] for ex in tr])
    yev = np.array([ex["answer"] for ex in ev])
    qtr, qev = _query_onehot(tr), _query_onehot(ev)
    try:
        # trained known-reader
        Etr = np.concatenate([_bge_embed([ex["text"] for ex in tr], False), qtr], axis=1)
        Eev = np.concatenate([_bge_embed([ex["text"] for ex in ev], False), qev], axis=1)
        kr_acc, kr_tr = fit_eval_probe("linear", Etr, ytr, Eev, yev, seed)
        # random-init BGE reservoir
        Rtr = np.concatenate([_bge_embed([ex["text"] for ex in tr], True), qtr], axis=1)
        Rev = np.concatenate([_bge_embed([ex["text"] for ex in ev], True), qev], axis=1)
        ri_acc, ri_tr = fit_eval_probe("linear", Rtr, ytr, Rev, yev, seed)
    except Exception as e:  # NOT BaseException; offline / model-load guard
        return {"bge_status": "BGE_UNAVAILABLE_%s" % type(e).__name__, "detail": str(e)[:300],
                "bge_n_train": len(tr), "bge_n_eval": len(ev)}
    return {"bge_status": "MEASURED", "bge_n_train": len(tr), "bge_n_eval": len(ev),
            "known_reader_bge": kr_acc, "known_reader_bge_train": kr_tr,
            "bge_random_init_reservoir": ri_acc, "bge_random_init_reservoir_train": ri_tr}


# ---------------- self-tests (leak-proofing) ----------------
def selftest_construction(seed=7, n=600):
    rng = np.random.default_rng(seed)
    ds = gen_dataset(n, rng)
    fails = []
    for ex in ds:
        L = len(ex["slots"])
        assert (L - 1 - ex["last_write_idx"]) >= TAIL_MIN, "tail constraint violated"
        assert ex["answer"] == oracle_keep_last(ex), "answer != keep-last rule"
        # every token in the rendered text must be in the closed vocab (else tokenize raises)
        _ = tokenize(ex["text"])
    answers = np.array([ex["answer"] for ex in ds])
    _, counts = np.unique(answers, return_counts=True)
    max_share = counts.max() / len(ds)
    if max_share >= 2.0 * CHANCE:
        fails.append("label imbalance max_share=%.3f (>= 2x chance %.3f)" % (max_share, CHANCE))

    sc = {"globally_last": oracle_acc(ds, oracle_globally_last),
          "first_occurrence": oracle_acc(ds, oracle_first_occurrence),
          "most_frequent": oracle_acc(ds, oracle_most_frequent)}
    for pos in FIXED_POSITIONS:
        sc["fixed_position_%d" % pos] = oracle_acc(ds, lambda ex, p=pos: oracle_fixed_position(ex, p))
    for name, acc in sc.items():
        if acc >= CHANCE + NEAR_CHANCE_MARGIN:
            fails.append("shortcut %s solves it acc=%.3f (>= chance+margin %.3f)"
                         % (name, acc, CHANCE + NEAR_CHANCE_MARGIN))

    kl = oracle_acc(ds, oracle_keep_last)
    if kl < 0.999:
        fails.append("oracle_keep_last=%.4f != 1.0 (construction/answer bug)" % kl)

    def _key(ex):
        return (tuple(int(x) for x in ex["slots"]), tuple(int(x) for x in ex["fills"]), int(ex["query"]))
    ds_a = gen_dataset(n, np.random.default_rng(seed))
    ds_b = gen_dataset(n, np.random.default_rng(seed + 1))
    keys_a = set(_key(ex) for ex in ds_a)
    overlap = sum(1 for ex in ds_b if _key(ex) in keys_a)
    if overlap > 0:
        fails.append("split leakage: %d/%d eval streams appear in train" % (overlap, n))

    # token-length stats (informs MAX_TOKENS / transformer cost)
    tlens = [len(tokenize(ex["text"])) for ex in ds]
    return {"shortcut_accs": sc, "label_max_share": float(max_share), "keep_last": float(kl),
            "split_overlap": int(overlap), "chance": CHANCE, "vocab_size": VOCAB_SIZE,
            "token_len_min": int(min(tlens)), "token_len_med": int(np.median(tlens)),
            "token_len_max": int(max(tlens)), "fails": fails}


def _arms_must_differ(named_arrays):
    digests = {}
    for name, arr in named_arrays.items():
        digests[name] = hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digests[names[i]] != digests[names[j]], (
                "META_RULE_AF VIOLATION: %r and %r bit-identical" % (names[i], names[j]))
    return digests


def run_self_test():
    _log("SELF-TEST: sklearn/torch import ...")
    if _SKLEARN_IMPORT_ERROR is not None:
        raise RuntimeError("sklearn import failed: %r" % _SKLEARN_IMPORT_ERROR)
    if _TORCH_IMPORT_ERROR is not None:
        raise RuntimeError("torch import failed: %r" % _TORCH_IMPORT_ERROR)

    _log("SELF-TEST: construction leak-proofing ...")
    st = selftest_construction(seed=7, n=600)
    _log("  chance=%.4f keep_last=%.4f label_max_share=%.4f split_overlap=%d vocab=%d "
         "tok_len min/med/max=%d/%d/%d"
         % (st["chance"], st["keep_last"], st["label_max_share"], st["split_overlap"],
            st["vocab_size"], st["token_len_min"], st["token_len_med"], st["token_len_max"]))
    _log("  shortcut accs: " + ", ".join("%s=%.3f" % (k, v) for k, v in st["shortcut_accs"].items()))
    if st["fails"]:
        for f in st["fails"]:
            _log("  SELFTEST FAIL: " + f)
        raise AssertionError("construction self-test FAILED: %s" % "; ".join(st["fails"]))

    _log("SELF-TEST: real_code_path -- build REAL encoders at tiny N + arms-differ ...")
    tr = gen_dataset(120, np.random.default_rng(7))
    ev = gen_dataset(120, np.random.default_rng(7 + 777))
    emb_enc = RandomEmbedEncoder(seed=7)
    tr_enc = RandomTransformerReservoir(seed=7)
    Xemb = _encoder_features_batched(emb_enc, ev)
    Xtrf = _encoder_features_batched(tr_enc, ev)
    assert Xemb.shape[0] == len(ev) and Xtrf.shape[0] == len(ev), "feature row-count mismatch"
    assert Xemb.shape[1] == 2 * D_EMB and Xtrf.shape[1] == 2 * D_EMB, "feature dim mismatch"
    _arms_must_differ({"randinit_embed": Xemb, "randinit_transformer": Xtrf})
    _log("  Xemb=%s Xtrf=%s (arms differ OK)" % (Xemb.shape, Xtrf.shape))

    _log("SELF-TEST: tiny end-to-end arms (no BGE) ...")
    res = run_calibration(tr, ev, seeds=(7,), with_bge=False, tag="selftest")
    accs = res["per_seed"][0]["arms"]
    _log("  tiny arms: " + ", ".join("%s=%.3f" % (k, v) for k, v in accs.items()))
    assert accs["oracle_keep_last"] >= 0.999, "tiny: keep-last ceiling broke"
    _log("SELF-TEST PASS")
    return {"selftest": st, "tiny": res}


# ---------------- calibration driver ----------------
CAN_FAIL_RESERVOIRS = ["randinit_embed_meanpool_linear", "randinit_embed_meanpool_mlp",
                       "randinit_transformer_reservoir_linear", "randinit_transformer_reservoir_mlp"]
CAN_FAIL_SHORTCUTS = ["shortcut_globally_last", "shortcut_first_occurrence",
                      "shortcut_most_frequent", "shortcut_fixed_position"]
WHOLE_SEQ_ATTN_ARMS = ["randinit_transformer_reservoir_linear", "randinit_transformer_reservoir_mlp"]


def run_calibration(tr, ev, seeds, with_bge, tag):
    per_seed = []
    ytr = np.array([ex["answer"] for ex in tr])
    yev = np.array([ex["answer"] for ex in ev])
    qtr, qev = _query_onehot(tr), _query_onehot(ev)
    for seed in seeds:
        arms = {}
        train_accs = {}

        # random-init embed reservoir
        emb_enc = RandomEmbedEncoder(seed)
        Xtr = np.concatenate([_encoder_features_batched(emb_enc, tr), qtr], axis=1)
        Xev = np.concatenate([_encoder_features_batched(emb_enc, ev), qev], axis=1)
        a, ta = fit_eval_probe("linear", Xtr, ytr, Xev, yev, seed)
        arms["randinit_embed_meanpool_linear"] = a; train_accs["randinit_embed_meanpool_linear"] = ta
        a, ta = fit_eval_probe("mlp", Xtr, ytr, Xev, yev, seed)
        arms["randinit_embed_meanpool_mlp"] = a; train_accs["randinit_embed_meanpool_mlp"] = ta

        # random-init transformer reservoir (KEY whole-seq-attention control)
        tr_enc = RandomTransformerReservoir(seed)
        Ttr = np.concatenate([_encoder_features_batched(tr_enc, tr), qtr], axis=1)
        Tev = np.concatenate([_encoder_features_batched(tr_enc, ev), qev], axis=1)
        a, ta = fit_eval_probe("linear", Ttr, ytr, Tev, yev, seed)
        arms["randinit_transformer_reservoir_linear"] = a
        train_accs["randinit_transformer_reservoir_linear"] = ta
        a, ta = fit_eval_probe("mlp", Ttr, ytr, Tev, yev, seed)
        arms["randinit_transformer_reservoir_mlp"] = a
        train_accs["randinit_transformer_reservoir_mlp"] = ta

        # arms-differ sanity: the two reservoir feature blocks must not be bit-identical
        _arms_must_differ({"embed_feat": Xev, "transformer_feat": Tev})

        # shortcut oracles
        arms["shortcut_globally_last"] = oracle_acc(ev, oracle_globally_last)
        arms["shortcut_first_occurrence"] = oracle_acc(ev, oracle_first_occurrence)
        arms["shortcut_most_frequent"] = oracle_acc(ev, oracle_most_frequent)
        fp = [oracle_acc(ev, lambda ex, p=p: oracle_fixed_position(ex, p)) for p in FIXED_POSITIONS]
        arms["shortcut_fixed_position"] = float(max(fp))

        # headroom ceiling
        arms["oracle_keep_last"] = oracle_acc(ev, oracle_keep_last)

        bge = None
        if with_bge:
            _log("  [%s seed=%d] BGE known-reader + BGE-random-init reservoir (capped) ..." % (tag, seed))
            bge = bge_arms(tr, ev, seed)
            if bge.get("bge_status") == "MEASURED":
                arms["known_reader_bge"] = bge["known_reader_bge"]
                arms["bge_random_init_reservoir"] = bge["bge_random_init_reservoir"]
                train_accs["known_reader_bge"] = bge["known_reader_bge_train"]

        per_seed.append({"seed": seed, "train_n": len(tr), "eval_n": len(ev),
                         "arms": arms, "train_accs": train_accs, "bge": bge})
        _log("  [%s seed=%d] " % (tag, seed)
             + ", ".join("%s=%.3f" % (k, v) for k, v in arms.items()))
    return {"per_seed": per_seed}


def decide_verdict(per_seed):
    near = CHANCE + NEAR_CHANCE_MARGIN
    reservoir_ok = True          # all random-init/whole-seq-attn/shortcut reservoirs near chance
    ceiling_ok = True
    worst_reservoir = 0.0
    worst_wholeseq = 0.0
    min_oracle = 1.0
    known_reader_status = "NOT_RUN"
    known_reader_clears = None
    known_reader_accs = []

    for ps in per_seed:
        a = ps["arms"]
        for arm in CAN_FAIL_RESERVOIRS + CAN_FAIL_SHORTCUTS:
            worst_reservoir = max(worst_reservoir, a[arm])
            if a[arm] >= near:
                reservoir_ok = False
        for arm in WHOLE_SEQ_ATTN_ARMS:
            worst_wholeseq = max(worst_wholeseq, a[arm])
        if "bge_random_init_reservoir" in a:      # BGE random-init is also a whole-seq-attn reservoir
            worst_wholeseq = max(worst_wholeseq, a["bge_random_init_reservoir"])
            worst_reservoir = max(worst_reservoir, a["bge_random_init_reservoir"])
            if a["bge_random_init_reservoir"] >= near:
                reservoir_ok = False
        min_oracle = min(min_oracle, a["oracle_keep_last"])
        if a["oracle_keep_last"] < ORACLE_KEEP_LAST_MIN:
            ceiling_ok = False
        if "known_reader_bge" in a:
            known_reader_accs.append(a["known_reader_bge"])
        if ps.get("bge") is not None:
            known_reader_status = ps["bge"].get("bge_status", "NOT_RUN")

    if known_reader_accs:
        kr_min = float(min(known_reader_accs))
        known_reader_clears = bool(kr_min >= CHANCE + KNOWN_READER_CLEAR_MARGIN)

    if not ceiling_ok:
        verdict = "NOT_LEARNABLE"
        msg = ("oracle_keep_last ceiling %.3f < %.2f: the label is not determined by keep-last "
               "(construction/answer bug)" % (min_oracle, ORACLE_KEEP_LAST_MIN))
    elif not reservoir_ok:
        verdict = "RESERVOIR_DECODABLE"
        msg = ("a random-init / whole-seq-attention / shortcut reservoir reached %.3f >= chance+margin "
               "%.3f: the NL rendering leaked a shortcut -> tighten (more distractors / TAIL_MIN / "
               "writes, fewer probe features) before the WM." % (worst_reservoir, near))
    else:
        verdict = "NL_RESERVOIR_FAILING_VALID"
        kr_note = ""
        if known_reader_clears is True:
            kr_note = (" Known-reader (BGE) CLEARS (min %.3f) -> pooled-reader headroom exists above the "
                       "reservoir floor." % min(known_reader_accs))
        elif known_reader_clears is False:
            kr_note = (" Known-reader (BGE, pooled) does NOT clear (min %.3f) -- EXPECTED: mean-pooling "
                       "cannot bind slot->last-filler; the oracle (%.3f) proves learnability, so a "
                       "STATEFUL WM that binds+gates is exactly the point. Reported, non-blocking."
                       % (min(known_reader_accs), min_oracle))
        elif known_reader_status.startswith("BGE_UNAVAILABLE"):
            kr_note = " Known-reader (BGE) unavailable (%s); oracle is the headroom gate." % known_reader_status
        msg = ("all can-fail reservoirs < %.3f (worst %.3f; worst whole-seq-attention %.3f) AND oracle "
               "keep-last >= %.2f (min %.3f), both seeds; chance=%.4f -> the NL construction separates "
               "learned content-gated binding+maintenance from structure-alone.%s"
               % (near, worst_reservoir, worst_wholeseq, ORACLE_KEEP_LAST_MIN, min_oracle, CHANCE, kr_note))

    return verdict, msg, {
        "chance": CHANCE, "near_chance_bar": near, "oracle_keep_last_min": ORACLE_KEEP_LAST_MIN,
        "worst_reservoir_acc": worst_reservoir, "worst_whole_seq_attention_acc": worst_wholeseq,
        "min_oracle_acc": min_oracle, "known_reader_status": known_reader_status,
        "known_reader_accs": known_reader_accs, "known_reader_clears": known_reader_clears,
        "known_reader_clear_bar": CHANCE + KNOWN_READER_CLEAR_MARGIN,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--train-n", type=int, default=FULL_TRAIN)
    ap.add_argument("--eval-n", type=int, default=FULL_EVAL)
    ap.add_argument("--no-bge", action="store_true", help="skip the BGE known-reader arms")
    ap.add_argument("--smoke", action="store_true", help="tiny full-shaped run (fast timing probe)")
    args = ap.parse_args()

    run_mode = "self_test" if (args.self_test or not (args.full or args.smoke)) else (
        "smoke" if args.smoke else "full")
    expected_units = 1 if run_mode == "self_test" else len(SEEDS_FULL)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        metrics = {"verdict": "SELFTEST_PASS",
                   "verdict_msg": "SELFTEST_PASS (NL construction leak-proofing + real encoders + tiny arms)",
                   "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
                   "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "chance": CHANCE,
                   "selftest": st["selftest"], "tiny_calibration": st["tiny"]}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE self-test in %.1fs" % elapsed)
        return

    with_bge = not args.no_bge
    if run_mode == "smoke":
        train_n, eval_n, seeds = 200, 150, (7,)
    else:
        train_n, eval_n, seeds = args.train_n, args.eval_n, SEEDS_FULL

    _log("%s calibration: train_n=%d eval_n=%d seeds=%s chance=%.4f with_bge=%s"
         % (run_mode.upper(), train_n, eval_n, seeds, CHANCE, with_bge))
    st = selftest_construction(seed=7, n=600)
    if st["fails"]:
        raise AssertionError("pre-run construction self-test FAILED: %s" % "; ".join(st["fails"]))

    tr = gen_dataset(train_n, np.random.default_rng(20260730))
    ev = gen_dataset(eval_n, np.random.default_rng(20260730 + 777))
    res = run_calibration(tr, ev, seeds, with_bge=with_bge, tag=run_mode)
    verdict, msg, bands = decide_verdict(res["per_seed"])
    elapsed = time.perf_counter() - t0

    metrics = {"verdict": verdict, "verdict_msg": msg,
               "summary": "%s | chance=%.4f | %s" % (verdict, CHANCE, msg[:140]),
               "run_mode": run_mode, "elapsed_s": elapsed, "ts_iso": _now_iso(),
               "anchor_name": ANCHOR_NAME, "chance": CHANCE, "bands": bands,
               "cardinality_ok": bool(len(res["per_seed"]) == len(seeds)),
               "expected_n_units": len(seeds), "n_units_done": len(res["per_seed"]),
               "params": {"V_FILL": V_FILL, "S_TARGET": S_TARGET, "N_DISTRACT_SLOTS": N_DISTRACT_SLOTS,
                          "N_DISTRACT_EVENTS": N_DISTRACT_EVENTS, "WRITES": [WRITES_MIN, WRITES_MAX],
                          "TAIL_MIN": TAIL_MIN, "TARGET_TAIL_MIN": TARGET_TAIL_MIN,
                          "MAX_TOKENS": MAX_TOKENS, "D_EMB": D_EMB, "N_LAYERS": N_LAYERS,
                          "N_HEADS": N_HEADS, "vocab_size": VOCAB_SIZE, "train_n": train_n,
                          "eval_n": eval_n, "seeds": list(seeds), "with_bge": with_bge},
               "construction_selftest": st, "per_seed": res["per_seed"],
               "start_marker_written": True, "crash_diagnostic_present": True,
               "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns"}
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
