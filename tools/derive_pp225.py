"""CYCLE_204 Tier-1: deepen PP-225 linear projection head (the fact-recall breakthrough). Scale to Qwen-1.5B + Pythia-1.4B + 3-seed + larger KB. From R3 (exp_t5c_kblam_proj_head)."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
R3 = (EXP / "exp_t5c_kblam_proj_head_gpu_v1.py").read_text(encoding="utf-8")

def base(anchor, st_new):
    return R3.replace("t5c_kblam_proj_head_gpu_v1", anchor).replace("t5c-kblam-proj-head", st_new)

# --- PP225-SCALE-QWEN15B + PP225-SCALE-PYTHIA14B (trivial MODEL change; R3 is arch-agnostic, uses only final logits) ---
s = base("t5c_pp225_qwen15b_v1", "pp225-qwen15b").replace('MODEL = "EleutherAI/pythia-160m"', 'MODEL = "Qwen/Qwen2.5-1.5B-Instruct"')
s = s.replace("AutoTokenizer.from_pretrained(MODEL)", "AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)")
s = s.replace("AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32)", "AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32, trust_remote_code=True)")
(EXP / "exp_t5c_pp225_qwen15b_v1.py").write_text(s, encoding="utf-8"); print("wrote pp225_qwen15b")

s = base("t5c_pp225_pythia14b_v1", "pp225-pythia14b").replace('MODEL = "EleutherAI/pythia-160m"', 'MODEL = "EleutherAI/pythia-1.4b"')
(EXP / "exp_t5c_pp225_pythia14b_v1.py").write_text(s, encoding="utf-8"); print("wrote pp225_pythia14b")

# --- PP225-LARGER-KB-5K (indexed distinct subjects so >pool-size unique facts) ---
s = base("t5c_pp225_kb5k_v1", "pp225-kb5k").replace("N_FACTS = 200 if SMOKE else 1500", "N_FACTS = 300 if SMOKE else 5000")
s = s.replace("subs = list(dict.fromkeys(DISC_POOL)); g.shuffle(subs); subs = subs[:N_FACTS]",
              "_base = list(dict.fromkeys(DISC_POOL)); subs = [\"%s-%04d\" % (_base[i %% len(_base)], i) for i in range(N_FACTS)]; g.shuffle(subs)")
(EXP / "exp_t5c_pp225_kb5k_v1.py").write_text(s, encoding="utf-8"); print("wrote pp225_kb5k")

# --- PP225-3SEED-VALIDATE (recall-based 3-seed aggregate) ---
s = base("t5c_pp225_3seed_v1", "pp225-3seed")
s = s.replace("def run() -> Dict:", "def run(SEED=7) -> Dict:").replace("torch.manual_seed(7)", "torch.manual_seed(SEED)")
TOP_OLD = ('out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()\n'
           'v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)\n'
           'metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}\n'
           'write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)')
TOP_NEW = ('out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time()\n'
           'SEEDS = [7] if SMOKE else [7, 13, 29]\n'
           'rs = [run(_s) for _s in SEEDS]\n'
           'hos = [r["best_heldout"] for r in rs]; mean = sum(hos) / len(hos); std = (sum((x - mean) ** 2 for x in hos) / len(hos)) ** 0.5\n'
           'rr = [round(x, 3) for x in hos]\n'
           'if len(rs) >= 3 and mean >= 0.95 and std <= 0.05:\n'
           '    v = "HARD_PASS"; vmsg = "HARD_PASS: PP-225 3-seed mean held-out recall %.3f (std %.3f) -- projection-head fact-recall VALIDATED multi-seed. heldout=%s" % (mean, std, rr)\n'
           'elif mean >= 0.50:\n'
           '    v = "MIDDLE_BAND"; vmsg = "MIDDLE_BAND: 3-seed mean held-out %.3f std %.3f. heldout=%s" % (mean, std, rr)\n'
           'else:\n'
           '    v = "HARD_FAIL"; vmsg = "HARD_FAIL: 3-seed mean held-out %.3f std %.3f. heldout=%s" % (mean, std, rr)\n'
           'print("\\n[VERDICT] " + vmsg, flush=True)\n'
           'metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(rs), "per_seed": rs, "summary": {"mean_heldout": mean, "std_heldout": std, "heldout": hos}, "elapsed_s": time.time() - t0}\n'
           'write_metrics(out_dir, metrics, rs); print("[metrics] written", flush=True)')
assert TOP_OLD in s, "3seed top not found"
s = s.replace(TOP_OLD, TOP_NEW)
(EXP / "exp_t5c_pp225_3seed_v1.py").write_text(s, encoding="utf-8"); print("wrote pp225_3seed")
