"""Derive cheap mechanism battery E6 (zero-input), E4 (layer-pair ablation), E2 (seq-length sweep) from C1/E1."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
C1 = (EXP / "exp_t5c_c1_multilayer_flamingo_train_gpu_v1.py").read_text(encoding="utf-8")
E1 = (EXP / "exp_t5c_e1_random_substrate_gpu_v1.py").read_text(encoding="utf-8")

# ---------- E6: zero-input baseline (derive from E1: random -> zeros) ----------
e6 = E1.replace("t5c_e1_random_substrate_gpu_v1", "t5c_e6_zero_input_gpu_v1").replace("t5c-e1-random-substrate", "t5c-e6-zero-input")
e6 = e6.replace("self.register_buffer('rmem', torch.randn(64, H) * 0.02)   # E1: FROZEN random substrate (not past-token hiddens)",
                "self.register_buffer('rmem', torch.zeros(64, H))           # E6: ZERO input (discriminates H2 parametric-transform)")
e6_old_v = 'REAL_IMPR = 0.164   # C1 3-seed validated real-substrate improvement (0.836x)'
e6 = e6.replace('if frac < 0.02:\n        return ("HARD_PASS", "HARD_PASS: random substrate gives <2%% of the real improvement -- the real past-token substrate provides GENUINE SIGNAL (H3 regularization refuted as primary; Path A is real context, not architecture artifact). " + s)',
                'if frac < 0.05:\n        return ("HARD_PASS", "HARD_PASS: zero-input gives <5%% of real improvement -- the adapter is a genuine MEMORY LOOKUP, not a parametric transform (H2 parametric refuted). " + s)')
e6 = e6.replace('if frac > 0.08:\n        return ("HARD_FAIL", "HARD_FAIL: random substrate gives >8%% of real improvement -- most benefit is structural/regularization (H3), not substrate signal. " + s)',
                'if frac > 0.05:\n        return ("HARD_FAIL", "HARD_FAIL: zero-input gives >5%% of real improvement -- adapter learned a parametric transform, not a memory lookup (H2). " + s)')
(EXP / "exp_t5c_e6_zero_input_gpu_v1.py").write_text(e6, encoding="utf-8"); print("wrote E6")

# ---------- E4: layer-pair ablation (sweep which middle pair; semantic-band predicts [4,5] best) ----------
e4 = C1.replace("t5c_c1_multilayer_flamingo_train_gpu_v1", "t5c_e4_layer_ablation_gpu_v1").replace("t5c-c1-multilayer-flamingo-train", "t5c-e4-layer-ablation")
e4 = e4.replace('STEPS = 60 if "--smoke" in sys.argv else 12000', 'STEPS = 60 if "--smoke" in sys.argv else 2500')   # 4 pairs -> shorter each
# replace single-run top-level with a sweep over layer-pairs
e4_old_top = ('out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()\n'
              'v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)\n'
              'metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}\n'
              'write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)')
e4_new_top = ('out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time()\n'
              'PAIRS = [[1, 2], [4, 5], [7, 8], [10, 11]] if not SMOKE else [[4, 5]]\n'
              'res = {}\n'
              'for _pair in PAIRS:\n'
              '    globals()["LAYERS"] = _pair; print("\\n[ablate] ===== layer-pair %s =====" % _pair, flush=True)\n'
              '    _r = run(); res["L%d+%d" % (_pair[0], _pair[1])] = round(_r["ratio"], 4)\n'
              'best = min(res, key=res.get); best_is_mid = (best == "L4+5")\n'
              'v = "HARD_PASS" if best_is_mid else "HARD_FAIL"\n'
              'vmsg = ("HARD_PASS: best layer-pair is L4+5 (semantic-onset band) -- confirms middle-layer/semantic-band targeting drives the gain. " if best_is_mid else "HARD_FAIL: best pair is %s, not L4+5 -- semantic-band hypothesis needs revision. " % best) + ("ratios=%s" % res)\n'
              'print("\\n[VERDICT] " + vmsg, flush=True)\n'
              'metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(res), "per_seed": [{"pair_ratios": res, "best": best}], "summary": {"pair_ratios": res, "best": best}, "elapsed_s": time.time() - t0}\n'
              'write_metrics(out_dir, metrics, [{"pair_ratios": res, "best": best}]); print("[metrics] written", flush=True)')
assert e4_old_top in e4, "E4 top not found"
e4 = e4.replace(e4_old_top, e4_new_top)
(EXP / "exp_t5c_e4_layer_ablation_gpu_v1.py").write_text(e4, encoding="utf-8"); print("wrote E4")

# ---------- E2: sequence-length sweep (context-extension test: longer seq -> bigger gain) ----------
e2 = C1.replace("t5c_c1_multilayer_flamingo_train_gpu_v1", "t5c_e2_seqlen_sweep_gpu_v1").replace("t5c-c1-multilayer-flamingo-train", "t5c-e2-seqlen-sweep")
e2 = e2.replace('STEPS = 60 if "--smoke" in sys.argv else 12000', 'STEPS = 60 if "--smoke" in sys.argv else 2500')
e2 = e2.replace("SEQLEN_PLACEHOLDER", "512")  # no-op guard
e2 = e2.replace('truncation=True, max_length=512', 'truncation=True, max_length=globals().get("SEQLEN", 512)')
e2_old_top = ('out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()\n'
              'v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)\n'
              'metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}\n'
              'write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)')
e2_new_top = ('out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time()\n'
              'SEQS = [128, 512] if not SMOKE else [128]\n'
              'impr = {}\n'
              'for _sl in SEQS:\n'
              '    globals()["SEQLEN"] = _sl; print("\\n[seqlen] ===== max_length %d =====" % _sl, flush=True)\n'
              '    _r = run(); impr[_sl] = round(max(0.0, 1.0 - _r["ratio"]), 4)\n'
              'short, lng = impr.get(128, 0.0), impr.get(512, 0.0); ratio_gain = (lng / short) if short > 1e-4 else 0.0\n'
              'v = "HARD_PASS" if (lng >= 1.5 * short and short > 1e-4) else ("HARD_FAIL" if (short > 1e-4 and lng <= 1.2 * short) else "MIDDLE_BAND")\n'
              'vmsg = ("%s: seq-length sweep -- improvement@512=%.3f vs @128=%.3f (%.2fx). " % (v, lng, short, ratio_gain)) + ("HARD_PASS=context-extension (longer seq -> bigger gain); HARD_FAIL=flat=regularization-dominated.")\n'
              'print("\\n[VERDICT] " + vmsg, flush=True)\n'
              'metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(impr), "per_seed": [{"improvement_by_seqlen": impr, "ratio_gain": ratio_gain}], "summary": {"improvement_by_seqlen": impr}, "elapsed_s": time.time() - t0}\n'
              'write_metrics(out_dir, metrics, [{"improvement_by_seqlen": impr, "ratio_gain": ratio_gain}]); print("[metrics] written", flush=True)')
assert e2_old_top in e2, "E2 top not found"
e2 = e2.replace(e2_old_top, e2_new_top)
(EXP / "exp_t5c_e2_seqlen_sweep_gpu_v1.py").write_text(e2, encoding="utf-8"); print("wrote E2")
