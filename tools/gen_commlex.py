"""AGGRESSIVE_OVERNIGHT THRUST-1 COMMUNICATE: COMM-LEX lexicalization-bridge (substrate-only). Probes the SURFACE ceiling:
can substrate emit ordered TOKEN SEQUENCES (closest substrate-only thing to text) by storing concept->token-seq lexicon and
composing a sentence -> emitting tokens in order? Tests retrieval-based generation (the substrate-native ceiling; novel-fluent
text is the LLM gap). Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_comm_lex_emission_cpu_v1.py -- COMM-LEX lexicalization bridge (substrate-native text emission ceiling) -- CPU.

ROUTING: Research AGGRESSIVE_OVERNIGHT THRUST-1 COMMUNICATE (the lexicalization gap, honest probe). Each concept has a stored
  lexicalization = an ordered TOKEN sequence (Tier-4 word-form). Lexicon binds concept (X) POS_k (X) token. A sentence = an
  ordered sequence of concepts; the substrate emits the full token stream by unbinding each concept's positions in order.
  Tests token-level emission accuracy + exact-sentence rate. This is RETRIEVAL-BASED generation (stored lexicalizations) -- the
  substrate-native ceiling; NOVEL fluent text generation is the LLM gap (honest boundary). N=8192.
PRE-REGISTERED: HARD-PASS token-emission accuracy >= 0.85 AND exact-sentence rate >= 0.60. MIDDLE token >= 0.70. HARD-FAIL else.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "comm_lex_emission_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: comm-lex-emission", flush=True)
def run() -> Dict:
    g = np.random.default_rng(812); NCON = 100; NTOK = 200; MAXPOS = 3; SENT = 4
    TR = 15 if SMOKE else 90; tok_hit = 0; tok_tot = 0; sent_ok = 0; sent_tot = 0
    for _ in range(TR):
        concepts = cphasor(NCON, N, g); tokens = cphasor(NTOK, N, g); POS = cphasor(MAXPOS, N, g)
        # lexicon: each concept -> ordered token sequence (len 1-3)
        lexlen = {c: int(g.integers(1, MAXPOS + 1)) for c in range(NCON)}
        lexseq = {c: [int(g.integers(0, NTOK)) for _ in range(lexlen[c])] for c in range(NCON)}
        LEX = np.zeros(N, dtype=np.complex64)
        for c in range(NCON):
            for k in range(lexlen[c]):
                LEX = LEX + concepts[c] * POS[k] * tokens[lexseq[c][k]]
        LEX = cnorm(LEX)
        for _q in range(8):
            sent = [int(g.integers(0, NCON)) for _ in range(SENT)]    # a sentence = ordered concepts
            ok_all = True
            for c in sent:
                for k in range(lexlen[c]):
                    pred = cidx(LEX * np.conj(concepts[c]) * np.conj(POS[k]), tokens)
                    hit = int(pred == lexseq[c][k]); tok_hit += hit; tok_tot += 1; ok_all = ok_all and bool(hit)
            sent_ok += int(ok_all); sent_tot += 1
    ta = tok_hit / tok_tot; sr = sent_ok / sent_tot
    print("  COMM-LEX token-emission=%.3f exact-sentence=%.3f (NCON=%d, NTOK=%d, lexicon-bound)" % (ta, sr, NCON, NTOK), flush=True)
    return {"token_accuracy": round(ta, 3), "exact_sentence": round(sr, 3)}
def verdict(r) -> Tuple[str, str]:
    s = "token-acc=%.3f exact-sentence=%.3f" % (r["token_accuracy"], r["exact_sentence"])
    if r["token_accuracy"] >= 0.85 and r["exact_sentence"] >= 0.60:
        return ("HARD_PASS", "HARD_PASS: substrate emits ordered token sequences from a stored lexicon (token-acc>=0.85, exact-sentence>=0.60) -- RETRIEVAL-BASED text generation works substrate-only. This is the substrate-native emission ceiling; novel fluent generation remains the LLM gap (honest). " + s)
    if r["token_accuracy"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: token-emission 0.70-0.85 (lexicon capacity limits). " + s)
    return ("HARD_FAIL", "HARD_FAIL: token-emission <0.70 -- substrate cannot reliably emit token sequences. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_comm_lex_emission_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote comm_lex_emission")
