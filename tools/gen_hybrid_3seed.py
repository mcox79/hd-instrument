"""Research P1: HYBRID 3-seed multi-seed promotion (composition reproducibility @10K). Write-tool authored (no heredoc)."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
h = (EXP / "exp_t5c_hybrid_lm_fact_gpu_v1.py").read_text(encoding="utf-8")
s = h.replace("t5c_hybrid_lm_fact_gpu_v1", "t5c_hybrid_3seed_kb10k_v1").replace("t5c-hybrid-lm-fact", "hybrid-3seed-kb10k")
s = s.replace("N_FACTS = 200 if SMOKE else 1500", "N_FACTS = 200 if SMOKE else 10000")
s = s.replace("ntr = int(0.6 * len(facts)); ftrain, ftest = facts[:ntr], facts[ntr:]",
              "ntr = int(0.6 * len(facts)); ftrain, ftest = facts[:ntr], facts[ntr:][:2000]")
s = s.replace("def run() -> Dict:", "def run(SEED=7) -> Dict:").replace("torch.manual_seed(7)", "torch.manual_seed(SEED)")
TOP_OLD = ('out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()\n'
           'v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)\n'
           'metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}\n'
           'write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)')
TOP_NEW = ('out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time()\n'
           'SEEDS = [7] if SMOKE else [7, 13, 29]\n'
           'rs = [run(_s) for _s in SEEDS]\n'
           'lmr = [r["lm_ratio"] for r in rs]; fr = [r["fact_recall"] for r in rs]\n'
           'def _m(x): return sum(x) / len(x)\n'
           'lm_m = _m(lmr); lm_s = (_m([(v - lm_m) ** 2 for v in lmr])) ** 0.5; fr_m = _m(fr); fr_s = (_m([(v - fr_m) ** 2 for v in fr])) ** 0.5\n'
           'if len(rs) >= 3 and lm_m < 0.85 and fr_m > 0.95 and lm_s < 0.05 and fr_s < 0.05:\n'
           '    v = "HARD_PASS"; vmsg = "HARD_PASS: HYBRID composition multi-seed VALIDATED -- LM-ratio %.3f (std %.3f) <0.85 AND fact-recall %.3f (std %.3f) >0.95. lmr=%s fr=%s" % (lm_m, lm_s, fr_m, fr_s, [round(x, 3) for x in lmr], [round(x, 3) for x in fr])\n'
           'elif lm_m < 1.0 and fr_m > 0.50:\n'
           '    v = "MIDDLE_BAND"; vmsg = "MIDDLE_BAND: LM %.3f fact %.3f (one below bar or variance). lmr=%s fr=%s" % (lm_m, fr_m, [round(x, 3) for x in lmr], [round(x, 3) for x in fr])\n'
           'else:\n'
           '    v = "HARD_FAIL"; vmsg = "HARD_FAIL: LM %.3f fact %.3f. lmr=%s fr=%s" % (lm_m, fr_m, [round(x, 3) for x in lmr], [round(x, 3) for x in fr])\n'
           'print("\\n[VERDICT] " + vmsg, flush=True)\n'
           'metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(rs), "per_seed": rs, "summary": {"lm_ratio_mean": lm_m, "lm_ratio_std": lm_s, "fact_recall_mean": fr_m, "fact_recall_std": fr_s}, "elapsed_s": time.time() - t0}\n'
           'write_metrics(out_dir, metrics, rs); print("[metrics] written", flush=True)')
assert TOP_OLD in s, "top not found"
s = s.replace(TOP_OLD, TOP_NEW)
(EXP / "exp_t5c_hybrid_3seed_kb10k_v1.py").write_text(s, encoding="utf-8"); print("wrote hybrid_3seed_kb10k")
