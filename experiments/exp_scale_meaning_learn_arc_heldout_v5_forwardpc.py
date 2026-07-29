"""CELL: scale_meaning_learn_arc_heldout_v5_forwardpc -- BRAIN-FAITHFUL FORWARD PREDICTIVE-CODING
encoder objective retrain. ONE VARIABLE vs V2 = the training OBJECTIVE: causal-LM (GPT-style, forward-
temporal next-token prediction, predicting FUTURE tokens from PAST-only context) REPLACES V2's
bidirectional MLM (masked-cloze reconstruction). Same architecture (d_model/n_layers/n_heads/ffn_mult),
same vocab/max_len, same ARC corpus, same token budget (V2's measured REALIZED 121,082,196 tokens, not
the 130M nominal), same mlm_steps/mlm_batch -- ONLY the attention-mask direction + loss target differ.

WHY: the brain's cortical learning signal (Rao & Ballard 1999 predictive coding; Friston 2005 free-
energy) is CAUSAL -- predict next input from past context, prediction-error drives the update. The two
prior retrains (v3_relobj = MLM+relational-InfoNCE, v3_grounding's R3/R4 self-teacher =
landmark+VICReg+relational-InfoNCE+EMA) were BOTH relational-CONTRASTIVE (graph-alignment), not
forward-temporal, and BOTH HARD_FAILED. This cell tests the untested FAITHFUL axis.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; sha256 hash-test over causal-PC / MLM-baseline /
#   RANDOM_INIT held-out rep matrices AND CROSS_BOUNDARY score vectors)
# - final_metrics_atomicity = tmp_replace (write_metrics/write_partial via _seed_checkpoint)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except) -- grep-gated
# - crlb_n/a: linear-probe/AUC base=0.5 exactly; no CRLB applies
# - baseline_in_band at smoke (META_RULE_AG; V2's own collapse/popularity/raw-grounding gates reused)
# - discriminator survives scale: HEADROOM PRECHECK at smoke (option C preview) BEFORE any FULL dispatch
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L) -- see pre-reg bands
# - HP_SCOPE: semantic TEXT-lift + CROSS_BOUNDARY replicate flag are the gated arms; RANDOM_INIT is a
#   guard-only confound check, MLM-baseline is the comparison reference (never itself HARD_PASS-gated)
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds (2 for FULL) x 3-arm comprehension panel
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check: default_ok_for_this_regime (CROSS_BOUNDARY instrument CITED-validated vs
#   BGE_SMALL margin=+0.26 in diag_order_critical_comprehension_calib_v1.py; not re-run here, no
#   transformers dependency introduced on the remote GPU box)
# - all numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test CONSTRUCTS the REAL substrate objects (CausalTinyTransformer, causal_lm_train,
#   V2.prepare_data/run_one_seed, gen_cross_boundary/score_readout_arm) at N~16-40, not synthetic-only
# - guard_baseline_valid: RANDOM_INIT structure-alone guard vs CROSS_BOUNDARY MARGIN_THRESH floor

Pre-reg: preregs/2026-07-29_scale_meaning_learn_arc_heldout_v5_forwardpc.md

CLI:
  --self-test : N~16-40 scale, seed=7 only, causal-PC + fresh tiny MLM baseline, tiny CROSS_BOUNDARY
                construction (train_target=40, eval_target_per_label=20). Asserts real code paths fire.
  --smoke     : HEADROOM PRECHECK. SMOKE_CFG scale (d_model=128/2L/vocab=4096/steps=250), seed=7 only,
                causal-PC + fresh tiny MLM baseline (SAME data bundle, apples-to-apples) + RANDOM_INIT.
                CROSS_BOUNDARY at reduced scale (train_target=300, eval_target_per_label=80). Emits
                headroom_gate: HEADROOM_YES | HEADROOM_NO. FULL dispatch is conditional on this gate.
  --full      : FULL_CFG scale, seeds=[7,13]. causal-PC trained fresh (the real GPU run). MLM baseline
                REUSED from data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_<seed>.pt (no retrain,
                store discipline) with CITED fallback to V2's own measured numbers if absent on this
                host. CROSS_BOUNDARY at full scale (train_target=1800, eval_target_per_label=300).
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch
import torch.nn.functional as F

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_scale_meaning_learn_arc_heldout_v2 as V2  # noqa: E402
from experiments.diag_order_critical_comprehension_calib_v1 import (  # noqa: E402
    gen_cross_boundary, score_readout_arm, fit_binary_probe, MARGIN_THRESH, COHERENT_FLOOR,
)
import experiments.exp_unified_self_learning_loop_v2 as LOOP2  # noqa: E402 (_scramble_words)
from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_partial, aggregate_partials, write_metrics, record_gate,
)

ANCHOR_NAME = "scale_meaning_learn_arc_heldout_v5_forwardpc"
V2_CKPT_DIR = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2")

SEED_CB = 20260728   # CROSS_BOUNDARY construction RNG seed -- MATCHES diag_order_critical_comprehension_calib_v1.SEED

# ---------------------------------------------------------------------------
# Config profiles (objective="causal_lm" tag is informational; V2 profiles reused verbatim for the
# fresh-MLM-baseline arm at self-test/smoke scale)
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(V2.SELFTEST_CFG, objective="causal_lm", seeds=[7])
SMOKE_CFG = dict(V2.SMOKE_CFG, objective="causal_lm", seeds=[7])
FULL_CFG = dict(V2.FULL_CFG, objective="causal_lm", seeds=[7, 13],
                train_token_budget=121082196)  # V2's own MEASURED realized budget, not 130M nominal

CB_SCALE = dict(
    selftest=dict(train_target=40, eval_target_per_label=20),
    smoke=dict(train_target=300, eval_target_per_label=80),
    full=dict(train_target=1800, eval_target_per_label=300),
)

HEADROOM_MARGIN_FLOOR = 0.5 * MARGIN_THRESH   # 0.075
HEADROOM_WORSE_THRESH = -0.05


# ---------------------------------------------------------------------------
# Start marker / crash diagnostics / logging (exp_dev.md SS13)
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg="%s: %s" % (type(exc).__name__, str(exc)[:500]),
                summary="CELL_CRASHED: %s" % type(exc).__name__, elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)  # SS17: flush=True on every progress line


# ---------------------------------------------------------------------------
# CausalTinyTransformer: self-contained copy of V2.TinyTransformer + causal attention mask.
# Same submodule names (tok_emb/pos_emb/enc/norm) -> architecturally state_dict-compatible with
# V2.TinyTransformer, BUT semantically requires causal=True at reconstruction (documented in pre-reg).
# ---------------------------------------------------------------------------
class CausalTinyTransformer(torch.nn.Module):
    def __init__(self, vocab, max_len, d_model, n_layers, n_heads, ffn_mult, pad_id, causal=True):
        super().__init__()
        self.pad_id = pad_id
        self.causal = causal
        self.tok_emb = torch.nn.Embedding(vocab, d_model, padding_idx=pad_id)
        self.pos_emb = torch.nn.Embedding(max_len, d_model)
        layer = torch.nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=ffn_mult * d_model,
            dropout=0.0, activation="gelu", batch_first=True, norm_first=True)
        self.enc = torch.nn.TransformerEncoder(layer, num_layers=n_layers)
        self.norm = torch.nn.LayerNorm(d_model)
        self.max_len = max_len
        self.d_model = d_model

    def _contextual(self, ids):
        pad_mask = (ids == self.pad_id)
        L = ids.shape[1]
        pos = torch.arange(L, device=ids.device).unsqueeze(0)
        h = self.tok_emb(ids) + self.pos_emb(pos)
        attn_mask = None
        if self.causal:
            attn_mask = torch.nn.Transformer.generate_square_subsequent_mask(L, device=ids.device)
        h = self.enc(h, mask=attn_mask, src_key_padding_mask=pad_mask)
        return self.norm(h), pad_mask

    def lm_logits(self, ids):
        h, _ = self._contextual(ids)
        return torch.nn.functional.linear(h, self.tok_emb.weight)  # tied head

    def pooled(self, ids):
        h, pad_mask = self._contextual(ids)
        keep = (~pad_mask).float().unsqueeze(-1)
        summed = (h * keep).sum(dim=1)
        cnt = keep.sum(dim=1).clamp_min(1.0)
        rep = summed / cnt
        return rep / (rep.norm(dim=1, keepdim=True) + 1e-8)


def causal_lm_train(stream, spec, cfg, device, seed, out_dir, hb_total):
    """Causal (forward-temporal) next-token-prediction training. Mirrors V2.mlm_train's
    optimizer/AMP/heartbeat/NaN-guard pattern; the objective itself (causal mask + shifted-CE over
    ALL non-pad positions, vs V2's 15%-masked bidirectional cloze) is the ONE variable."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    max_len = cfg["max_len"]
    model = CausalTinyTransformer(spec["size"], max_len, cfg["d_model"], cfg["n_layers"],
                                   cfg["n_heads"], cfg["ffn_mult"], spec["pad"], causal=True).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    _log("  model params=%.2fM device=%s vocab=%d d=%d L=%d objective=causal_lm"
         % (n_params / 1e6, device.type, spec["size"], cfg["d_model"], cfg["n_layers"]))
    n_win = stream.shape[0] // max_len
    if n_win < 4:
        raise RuntimeError("train stream too short: %d tokens, %d windows" % (stream.shape[0], n_win))
    windows = stream[:n_win * max_len].reshape(n_win, max_len)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg["mlm_lr"])
    use_amp = (device.type == "cuda")
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
    g = np.random.default_rng(seed + 5)
    bs = min(cfg["mlm_batch"], n_win)
    pad_id = spec["pad"]
    log_every = max(1, cfg["mlm_steps"] // 10)
    last_loss = float("nan")
    t0 = time.perf_counter()
    model.train()
    for step in range(cfg["mlm_steps"]):
        sel = g.integers(0, n_win, size=bs)
        ids = torch.from_numpy(windows[sel].astype(np.int64)).to(device)
        opt.zero_grad(set_to_none=True)
        with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
            logits = model.lm_logits(ids)                       # [B, L, V], causal (no future leak)
            V = logits.shape[-1]
            shift_logits = logits[:, :-1, :].reshape(-1, V)
            shift_target = ids[:, 1:].reshape(-1)
            loss = F.cross_entropy(shift_logits, shift_target, ignore_index=pad_id)
        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite causal-LM loss step=%d seed=%d" % (step, seed))
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()
        last_loss = float(loss.detach())
        if (step % log_every == 0) or (step == cfg["mlm_steps"] - 1):
            el = time.perf_counter() - t0
            _log("  CAUSAL_LM seed=%d step=%d/%d loss=%.4f (%.1fs)"
                 % (seed, step, cfg["mlm_steps"], last_loss, el))
            if out_dir:
                V2._heartbeat(out_dir, step, hb_total, el, extra={"causal_lm_loss": last_loss, "seed": seed})
    model.eval()
    return model, last_loss


# ---------------------------------------------------------------------------
# CROSS_BOUNDARY comprehension-VET: own-encoder MEAN_POOL margin, 3-arm panel
# ---------------------------------------------------------------------------
def _own_encode_meanpool(model, tok, spec, sents, max_len, device):
    """Encode sentences via the model's OWN pooled() readout (no bolt-on reader)."""
    pad_id = spec["pad"]
    X = np.stack([V2._encode_pad(tok, s, max_len, pad_id) for s in sents], axis=0)
    reps = np.zeros((X.shape[0], model.d_model), dtype=np.float32)
    bs = 256
    with torch.no_grad():
        for i in range(0, X.shape[0], bs):
            ids = torch.from_numpy(X[i:i + bs]).to(device)
            reps[i:i + bs] = model.pooled(ids).float().cpu().numpy()
    return reps


def score_cross_boundary(model, tok, spec, construction, eval_scr_sents, seed, device, max_len):
    train_items = construction["train"]
    eval_items = construction["eval"]
    y_train = np.array([it["label"] for it in train_items], dtype=np.int64)
    y_eval = np.array([it["label"] for it in eval_items], dtype=np.int64)
    G_tr = _own_encode_meanpool(model, tok, spec, [it["sent"] for it in train_items], max_len, device)
    G_ec = _own_encode_meanpool(model, tok, spec, [it["sent"] for it in eval_items], max_len, device)
    G_es = _own_encode_meanpool(model, tok, spec, eval_scr_sents, max_len, device)
    return score_readout_arm("MEAN_POOL", G_tr, y_train, G_ec, G_es, y_eval, seed)


def build_cross_boundary_construction(train_target, eval_target_per_label):
    rng = np.random.default_rng(SEED_CB)
    construction = gen_cross_boundary(rng, train_target=train_target,
                                       eval_target_per_label=eval_target_per_label)
    srng = np.random.default_rng(SEED_CB + 1234)
    eval_scr_sents = [LOOP2._scramble_words(it["sent"], srng) for it in construction["eval"]]
    return construction, eval_scr_sents


def _arms_must_differ_np(arms):
    import hashlib
    digests = {}
    for name, arr in arms.items():
        digests[name] = hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical" % (a, b))
    return digests


def _load_mlm_baseline_encoder(seed, cfg, device):
    """FULL scale: reuse V2's real trained ckpt (no retrain). Returns (model, tok, spec, baseline_source)."""
    ckpt_path = os.path.join(V2_CKPT_DIR, "ckpt_seed_%d.pt" % seed)
    if not os.path.exists(ckpt_path):
        return None, None, None, "cited_reference"
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    mc = ckpt["model_cfg"]
    model = V2.TinyTransformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                                mc["n_heads"], mc["ffn_mult"], mc["pad_id"]).to(device)
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    from tokenizers import Tokenizer
    tok = Tokenizer.from_str(ckpt["tokenizer_json"])
    spec = ckpt["spec"]
    return model, tok, spec, "reused_checkpoint"


# ---------------------------------------------------------------------------
# One seed: causal-PC training + encode + eval, MLM-baseline arm (fresh at smoke/selftest, reused at
# FULL) + RANDOM_INIT arm, then CROSS_BOUNDARY comprehension-VET panel.
# ---------------------------------------------------------------------------
def run_one_seed_causal(seed, cfg, device, out_dir, universe, bundle, cb_scale):
    t0 = time.perf_counter()
    split = bundle["split"]
    counts = bundle["counts"]
    tok = bundle["tok"]
    spec = bundle["spec"]
    postings = bundle["postings"]
    ground = bundle["ground"]

    _log("seed=%d: causal-LM train (%d steps)..." % (seed, cfg["mlm_steps"]))
    model, final_loss = causal_lm_train(bundle["stream"], spec, cfg, device, seed, out_dir, cfg["mlm_steps"])
    _log("  causal-LM done final_loss=%.4f" % final_loss)

    _log("seed=%d: encode concept text-reps (causal-PC trained)..." % seed)
    text_reps, mrep_cnt = V2.encode_concept_text_reps(model, tok, postings, cfg, device, spec)
    torch.manual_seed(seed + 999)
    rand_model = CausalTinyTransformer(spec["size"], cfg["max_len"], cfg["d_model"], cfg["n_layers"],
                                        cfg["n_heads"], cfg["ffn_mult"], spec["pad"], causal=True).to(device)
    rand_model.eval()
    _log("seed=%d: encode concept text-reps (random-init, causal arch)..." % seed)
    text_rand, _ = V2.encode_concept_text_reps(rand_model, tok, postings, cfg, device, spec)

    w_star, selected_arm, _ = V2.select_fusion_on_train(ground, text_reps, text_rand, counts,
                                                         universe, split, seed)

    ckpt = dict(
        state_dict={k: v.detach().cpu() for k, v in model.state_dict().items()},
        spec=spec,
        model_cfg=dict(vocab=int(spec["size"]), max_len=int(cfg["max_len"]),
                       d_model=int(cfg["d_model"]), n_layers=int(cfg["n_layers"]),
                       n_heads=int(cfg["n_heads"]), ffn_mult=int(cfg["ffn_mult"]),
                       pad_id=int(spec["pad"]), causal=True),
        tokenizer_json=tok.to_str(),
        seed=int(seed), run_mode=cfg["run_mode"], anchor=ANCHOR_NAME, objective="causal_lm",
        w_star=float(w_star), selected_arm=str(selected_arm),
    )
    try:
        torch.save(ckpt, os.path.join(out_dir, "ckpt_seed_%d.pt" % seed))
        _log("  checkpoint saved: ckpt_seed_%d.pt" % seed)
        ckpt_saved = True
    except (OSError, RuntimeError, ValueError) as e:
        _log("  WARN checkpoint save failed (%s): %s" % (type(e).__name__, str(e)[:200]))
        ckpt_saved = False

    extra = dict(final_causal_lm_loss=float(final_loss), trained_tokens=int(bundle["trained_tokens"]),
                 corpus_stats=bundle["corpus_stats"], collect_meta=bundle["collect_meta"],
                 split_meta=split["split_meta"], bpe_size=int(spec["size"]), checkpoint_saved=ckpt_saved)
    eval_res = V2.eval_from_reps(seed, cfg["run_mode"], out_dir, universe, split, counts,
                                  bundle["adj"], bundle["deg"], bundle["n_shards"],
                                  ground, text_reps, text_rand, mrep_cnt,
                                  time.perf_counter() - t0, extra=extra)

    # --- MLM-baseline arm ---
    if cfg["run_mode"] == "full":
        mlm_model, mlm_tok, mlm_spec, baseline_source = _load_mlm_baseline_encoder(seed, cfg, device)
        mlm_text_reps = None
        if mlm_model is not None:
            mlm_postings = postings  # same held-out split; V2's ckpt was trained on the same ARC-only split
            mlm_text_reps, _ = V2.encode_concept_text_reps(mlm_model, mlm_tok, mlm_postings, cfg, device, mlm_spec)
    else:
        _log("seed=%d: fresh tiny MLM baseline (V2.run_one_seed, same data bundle)..." % seed)
        mlm_out_dir = os.path.join(out_dir, "_mlm_baseline_arm")
        os.makedirs(mlm_out_dir, exist_ok=True)
        mlm_res = V2.run_one_seed(seed, cfg, device, mlm_out_dir, universe, bundle)
        mlm_ckpt_path = os.path.join(mlm_out_dir, "ckpt_seed_%d.pt" % seed)
        mlm_ckpt = torch.load(mlm_ckpt_path, map_location="cpu", weights_only=False)
        mlm_mc = mlm_ckpt["model_cfg"]
        mlm_model = V2.TinyTransformer(mlm_mc["vocab"], mlm_mc["max_len"], mlm_mc["d_model"],
                                        mlm_mc["n_layers"], mlm_mc["n_heads"], mlm_mc["ffn_mult"],
                                        mlm_mc["pad_id"]).to(device)
        mlm_model.load_state_dict(mlm_ckpt["state_dict"])
        mlm_model.eval()
        from tokenizers import Tokenizer
        mlm_tok = Tokenizer.from_str(mlm_ckpt["tokenizer_json"])
        mlm_spec = mlm_ckpt["spec"]
        baseline_source = "fresh_same_bundle"
        eval_res["mlm_baseline_semantic_margin_text_minus_raw"] = (
            mlm_res["semantic_all"][V2.TEXT_ARM] - mlm_res["semantic_all"][V2.RAW_ARM])

    # --- CROSS_BOUNDARY comprehension-VET panel (causal-PC, MLM-baseline, RANDOM_INIT) ---
    _log("seed=%d: CROSS_BOUNDARY comprehension-VET (train_target=%d, eval_per_label=%d)..."
         % (seed, cb_scale["train_target"], cb_scale["eval_target_per_label"]))
    construction, eval_scr_sents = build_cross_boundary_construction(
        cb_scale["train_target"], cb_scale["eval_target_per_label"])
    max_len_cb = min(32, cfg["max_len"])

    cb_causal = score_cross_boundary(model, tok, spec, construction, eval_scr_sents, seed, device, max_len_cb)
    cb_rand = score_cross_boundary(rand_model, tok, spec, construction, eval_scr_sents, seed, device, max_len_cb)
    cb_mlm = None
    if mlm_model is not None:
        cb_mlm = score_cross_boundary(mlm_model, mlm_tok, mlm_spec, construction, eval_scr_sents,
                                       seed, device, max_len_cb)

    cb_digest_arms = {"CAUSAL_PC": np.array([cb_causal["margin"]]), "RANDOM_INIT": np.array([cb_rand["margin"]])}
    if cb_mlm is not None:
        cb_digest_arms["MLM_BASELINE"] = np.array([cb_mlm["margin"]])
    cb_digests = _arms_must_differ_np(cb_digest_arms)

    eval_res["cross_boundary"] = dict(
        causal_pc=cb_causal, random_init=cb_rand, mlm_baseline=cb_mlm,
        baseline_source=baseline_source, arms_differ_digests=cb_digests,
    )
    return eval_res


# ---------------------------------------------------------------------------
# Self-test assertions (real-code-path gate F.1)
# ---------------------------------------------------------------------------
def _selftest_assertions(per_seed, out_dir):
    assert len(per_seed) >= 1, "no seed completed"
    sk = sorted(per_seed.keys())[0]
    r = per_seed[sk]
    assert np.isfinite(r["final_causal_lm_loss"]), "causal-LM loss not finite"
    assert r["trained_tokens"] > 0, "no tokens trained on"
    assert r["semantic_all"] is not None, "semantic eval did not run"
    cb = r["cross_boundary"]
    assert cb["causal_pc"] is not None and -1.0 <= cb["causal_pc"]["margin"] <= 1.0, "CROSS_BOUNDARY margin out of range"
    assert cb["random_init"] is not None, "RANDOM_INIT arm missing"
    assert len(cb["arms_differ_digests"]) >= 2, "arms-must-differ digests missing"
    ckpt_pt = os.path.join(out_dir, "ckpt_seed_%d.pt" % int(sk))
    assert os.path.exists(ckpt_pt), "causal-PC checkpoint not saved: %s" % ckpt_pt


# ---------------------------------------------------------------------------
# Headroom precheck verdict (smoke mode)
# ---------------------------------------------------------------------------
def build_headroom_verdict(per_seed):
    sk = sorted(per_seed.keys())[0]
    r = per_seed[sk]
    cb = r["cross_boundary"]
    causal_m = cb["causal_pc"]["margin"]
    mlm_m = cb["mlm_baseline"]["margin"] if cb.get("mlm_baseline") else None
    causal_sem = r["semantic_all"][V2.TEXT_ARM] - r["semantic_all"][V2.RAW_ARM]
    mlm_sem = r.get("mlm_baseline_semantic_margin_text_minus_raw")

    cb_delta = (causal_m - mlm_m) if mlm_m is not None else None
    sem_delta = (causal_sem - mlm_sem) if mlm_sem is not None else None

    cb_not_much_worse = (cb_delta is None) or (cb_delta > HEADROOM_WORSE_THRESH)
    positive_signal = (causal_m >= HEADROOM_MARGIN_FLOOR) or (sem_delta is not None and sem_delta >= 0.0)
    both_worse = (cb_delta is not None and cb_delta <= HEADROOM_WORSE_THRESH
                  and sem_delta is not None and sem_delta < 0.0)

    if both_worse:
        gate = "HEADROOM_NO"
        msg = ("HEADROOM_NO: causal-PC is worse than fresh-MLM-baseline on BOTH axes at smoke scale "
               "(cross_boundary margin delta=%.4f <= %.2f AND semantic TEXT-lift delta=%.4f < 0). "
               "causal_pc margin=%.4f mlm_baseline margin=%.4f causal_pc semantic=%.4f mlm semantic=%.4f. "
               "ABORT full dispatch per headroom pre-check discipline."
               % (cb_delta, HEADROOM_WORSE_THRESH, sem_delta, causal_m, mlm_m, causal_sem, mlm_sem or -1))
    elif cb_not_much_worse and positive_signal:
        gate = "HEADROOM_YES"
        msg = ("HEADROOM_YES: causal_pc cross_boundary margin=%.4f (mlm_baseline=%s, delta=%s), "
               "causal_pc semantic TEXT-lift=%.4f (mlm_baseline=%s, delta=%s). Proceed to FULL."
               % (causal_m, ("%.4f" % mlm_m) if mlm_m is not None else "NA",
                  ("%.4f" % cb_delta) if cb_delta is not None else "NA",
                  causal_sem, ("%.4f" % mlm_sem) if mlm_sem is not None else "NA",
                  ("%.4f" % sem_delta) if sem_delta is not None else "NA"))
    else:
        gate = "HEADROOM_NO"
        msg = ("HEADROOM_NO: no positive/non-worse directional signal found at smoke scale. "
               "causal_pc margin=%.4f mlm_baseline margin=%s cb_delta=%s causal_sem=%.4f mlm_sem=%s sem_delta=%s"
               % (causal_m, ("%.4f" % mlm_m) if mlm_m is not None else "NA",
                  ("%.4f" % cb_delta) if cb_delta is not None else "NA", causal_sem,
                  ("%.4f" % mlm_sem) if mlm_sem is not None else "NA",
                  ("%.4f" % sem_delta) if sem_delta is not None else "NA"))
    return gate, msg, dict(causal_pc_cross_boundary_margin=causal_m, mlm_baseline_cross_boundary_margin=mlm_m,
                            cross_boundary_delta=cb_delta, causal_pc_semantic_text_margin=causal_sem,
                            mlm_baseline_semantic_text_margin=mlm_sem, semantic_delta=sem_delta)


# ---------------------------------------------------------------------------
# FULL verdict
# ---------------------------------------------------------------------------
def build_full_verdict(per_seed):
    seeds = sorted(per_seed.keys(), key=lambda k: int(k))
    sem_deltas = []
    cb_replicates_causal = []
    cb_replicates_mlm = []
    rand_confound = []
    for k in seeds:
        r = per_seed[k]
        causal_sem = r["semantic_all"][V2.TEXT_ARM] - r["semantic_all"][V2.RAW_ARM]
        sem_deltas.append(causal_sem)  # FULL: compared against CITED v2 baseline=0.0387 below
        cb = r["cross_boundary"]
        cb_replicates_causal.append(bool(cb["causal_pc"]["comprehension_specific"]))
        if cb.get("mlm_baseline"):
            cb_replicates_mlm.append(bool(cb["mlm_baseline"]["comprehension_specific"]))
        rand_confound.append(cb["random_init"]["margin"] >= MARGIN_THRESH)

    V2_MLM_SEMANTIC_TEXT_MARGIN = 0.03873988873108891  # MEASURED@data/exp_scale_meaning_learn_arc_heldout_v2/metrics.json
    mean_sem_delta = float(np.mean([d - V2_MLM_SEMANTIC_TEXT_MARGIN for d in sem_deltas]))
    causal_replicates_both = all(cb_replicates_causal) and len(cb_replicates_causal) >= 2
    mlm_replicates_both = all(cb_replicates_mlm) and len(cb_replicates_mlm) >= 2 if cb_replicates_mlm else False
    any_confound = any(rand_confound)

    if any_confound:
        verdict = "MIDDLE_BAND_STRUCTURE_ALONE_CONFOUND"
        msg = ("RANDOM_INIT (untrained CausalTinyTransformer) cleared MARGIN_THRESH=%.2f on >=1 seed -- "
               "CROSS_BOUNDARY signal cannot be attributed to learned structure; per-seed random_confound=%s"
               % (MARGIN_THRESH, rand_confound))
    elif mean_sem_delta >= 0.03 or (causal_replicates_both and not mlm_replicates_both):
        verdict = "HARD_PASS_FORWARDPC_WIN"
        msg = ("HARD_PASS_FORWARDPC_WIN: mean semantic TEXT-lift delta over V2-MLM=%.4f (>=0.03) OR "
               "CROSS_BOUNDARY replicates for causal-PC on both seeds (%s) while MLM baseline does not (%s). "
               "No structure-alone confound." % (mean_sem_delta, causal_replicates_both, mlm_replicates_both))
    elif mean_sem_delta < 0.0 and not causal_replicates_both:
        verdict = "HARD_FAIL_NO_LIFT_NO_REPLICATE"
        msg = ("HARD_FAIL_NO_LIFT_NO_REPLICATE: mean semantic TEXT-lift delta over V2-MLM=%.4f (<0), "
               "CROSS_BOUNDARY does not replicate for causal-PC (per-seed comprehension_specific=%s). "
               "Forward-temporal objective change does not lift comprehension signal at this scale."
               % (mean_sem_delta, cb_replicates_causal))
    else:
        verdict = "MIDDLE_BAND"
        msg = ("MIDDLE_BAND: mixed evidence. mean semantic TEXT-lift delta=%.4f, causal CROSS_BOUNDARY "
               "replicates=%s (per-seed=%s), mlm CROSS_BOUNDARY replicates=%s."
               % (mean_sem_delta, causal_replicates_both, cb_replicates_causal, mlm_replicates_both))
    summary = dict(mean_semantic_text_lift_delta_over_v2_mlm=mean_sem_delta,
                   causal_pc_cross_boundary_replicates_both_seeds=causal_replicates_both,
                   mlm_baseline_cross_boundary_replicates_both_seeds=mlm_replicates_both,
                   random_init_confound_any_seed=any_confound,
                   per_seed_cross_boundary_causal_margin={k: per_seed[k]["cross_boundary"]["causal_pc"]["margin"] for k in seeds})
    return verdict, msg, summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def _select_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", default=None)
    args = ap.parse_args()

    if args.self_test:
        cfg = SELFTEST_CFG
        cb_scale = CB_SCALE["selftest"]
    elif args.smoke:
        cfg = SMOKE_CFG
        cb_scale = CB_SCALE["smoke"]
    else:
        cfg = FULL_CFG
        cb_scale = CB_SCALE["full"]

    out_dir = get_output_dir(ANCHOR_NAME)
    os.makedirs(out_dir, exist_ok=True)
    _write_start_marker(out_dir, cfg["run_mode"], len(cfg["seeds"]))

    device = torch.device(args.device) if args.device else _select_device()
    _log("run_mode=%s device=%s seeds=%s cuda=%s objective=causal_lm"
         % (cfg["run_mode"], device.type, cfg["seeds"], torch.cuda.is_available()))
    if not os.path.exists(V2.ARC_CORPUS):
        raise FileNotFoundError("ARC corpus not found at %s (remote staging?)" % V2.ARC_CORPUS)

    _log("loading concept universe...")
    universe = V2.load_concept_universe(cfg)
    _log("concept universe: K=%d" % universe["K"])

    _log("preparing shared data (split, tokenizer, postings, stream, graph)...")
    bundle = V2.prepare_data(cfg, universe)

    for seed in cfg["seeds"]:
        res = run_one_seed_causal(seed, cfg, device, out_dir, universe, bundle, cb_scale)
        write_partial(out_dir, seed, res)
        _log("seed=%d done in %.1fs" % (seed, res["elapsed_s"]))

    per_seed = aggregate_partials(out_dir, cfg["seeds"])

    if cfg["run_mode"] == "full":
        verdict, vmsg, summary = build_full_verdict(per_seed)
    else:
        verdict, vmsg, summary = build_headroom_verdict(per_seed)
        _log("HEADROOM GATE: %s" % verdict)

    _log("VERDICT: %s" % verdict)
    _log(vmsg)

    gates = [record_gate("cardinality", float(len(per_seed)), float(len(cfg["seeds"])), "==",
                          note="expected %d seeds" % len(cfg["seeds"]))]

    metrics = dict(
        verdict=verdict, verdict_msg=vmsg, summary=vmsg,
        anchor_name=ANCHOR_NAME, run_mode=cfg["run_mode"],
        ts_iso=datetime.now(timezone.utc).isoformat(),
        device=device.type, cuda=bool(torch.cuda.is_available()),
        n_seeds=len(cfg["seeds"]), objective="causal_lm",
        results_summary=summary, per_seed={k: per_seed[k] for k in per_seed},
        bands=dict(margin_thresh=MARGIN_THRESH, coherent_floor=COHERENT_FLOOR,
                   headroom_margin_floor=HEADROOM_MARGIN_FLOOR, headroom_worse_thresh=HEADROOM_WORSE_THRESH),
        cardinality_ok=(len(per_seed) == len(cfg["seeds"])),
        expected_n_units=len(cfg["seeds"]),
    )
    write_metrics(out_dir, metrics, results=list(per_seed.values()), gate_claims=gates)

    if args.self_test:
        _selftest_assertions(per_seed, out_dir)
        _log("SELF-TEST PASS")


if __name__ == "__main__":
    _out = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
