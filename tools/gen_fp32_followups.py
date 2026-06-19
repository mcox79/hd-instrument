"""fp32-transfer is SOLVED (pythia14b_fp32proj HARD_PASS). Follow-ups: 3-seed reproducibility + 10K-KB scale at 1.4B. From the fp32proj cell (bf16 backbone + fp32 head + freed bge = fits)."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
FP = (EXP / "exp_t5c_pp225_pythia14b_fp32proj_v1.py").read_text(encoding="utf-8")

# 1. 3-seed reproducibility of the 1.4B fp32 transfer (held-out recall mean/std)
s = FP.replace("t5c_pp225_pythia14b_fp32proj_v1", "t5c_pp225_pythia14b_fp32proj_3seed_v1").replace("pp225-pythia14b-fp32proj", "pp225-pythia14b-fp32proj-3seed")
s = s.replace("def run() -> Dict:", "def run(SEED=7) -> Dict:").replace("torch.manual_seed(7)", "torch.manual_seed(SEED)")
TOP_OLD = ('out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()\n'
           'v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)\n'
           'metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}\n'
           'write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)')
TOP_NEW = ('out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time()\n'
           'SEEDS = [7] if SMOKE else [7, 13, 29]\n'
           'rs = [run(_s) for _s in SEEDS]\n'
           'hos = [r["best_heldout"] for r in rs]; mean = sum(hos)/len(hos); std = (sum((x-mean)**2 for x in hos)/len(hos))**0.5; rr = [round(x,3) for x in hos]\n'
           'if len(rs) >= 3 and mean >= 0.95 and std <= 0.05:\n'
           '    v = "HARD_PASS"; vmsg = "HARD_PASS: PP-225 fp32 1.4B 3-seed mean held-out %.3f (std %.3f) -- transfer to bigger LLM reproducible. heldout=%s" % (mean, std, rr)\n'
           'elif mean >= 0.50:\n'
           '    v = "MIDDLE_BAND"; vmsg = "MIDDLE_BAND: 3-seed mean %.3f std %.3f. heldout=%s" % (mean, std, rr)\n'
           'else:\n'
           '    v = "HARD_FAIL"; vmsg = "HARD_FAIL: 3-seed mean %.3f std %.3f. heldout=%s" % (mean, std, rr)\n'
           'print("\\n[VERDICT] " + vmsg, flush=True)\n'
           'metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(rs), "per_seed": rs, "summary": {"mean_heldout": mean, "std_heldout": std}, "elapsed_s": time.time() - t0}\n'
           'write_metrics(out_dir, metrics, rs); print("[metrics] written", flush=True)')
assert TOP_OLD in s, "3seed top not found"
s = s.replace(TOP_OLD, TOP_NEW)
(EXP / "exp_t5c_pp225_pythia14b_fp32proj_3seed_v1.py").write_text(s, encoding="utf-8"); print("wrote fp32proj_3seed")

# 2. 1.4B fp32 at 10K-KB (indexed subjects so >pool unique; cap held-out eval to 2000)
k = FP.replace("t5c_pp225_pythia14b_fp32proj_v1", "t5c_pp225_pythia14b_fp32proj_kb10k_v1").replace("pp225-pythia14b-fp32proj", "pp225-pythia14b-fp32proj-kb10k")
k = k.replace("N_FACTS = 200 if SMOKE else 1500", "N_FACTS = 300 if SMOKE else 10000")
k = k.replace("subs = list(dict.fromkeys(DISC_POOL)); g.shuffle(subs); subs = subs[:N_FACTS]",
              "_base = list(dict.fromkeys(DISC_POOL)); subs = [\"%s-%04d\" % (_base[i % len(_base)], i) for i in range(N_FACTS)]; g.shuffle(subs)")
k = k.replace("ntr = int(0.6 * len(facts)); train, test = facts[:ntr], facts[ntr:]",
              "ntr = int(0.6 * len(facts)); train, test = facts[:ntr], facts[ntr:][:2000]   # cap held-out eval")
k = k.replace("if hp >= 0.25:", "if hp >= 0.50:")   # 10K bar
(EXP / "exp_t5c_pp225_pythia14b_fp32proj_kb10k_v1.py").write_text(k, encoding="utf-8"); print("wrote fp32proj_kb10k")
