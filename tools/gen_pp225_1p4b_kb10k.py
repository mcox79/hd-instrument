"""GPU buffer: PP-225-1.4B at 10K facts -- derive from pythia14b fp32-head cell, scale N_FACTS + STEPS (longer run + genuine scaling). cap held-out eval. Write-tool authored."""
import pathlib
base = pathlib.Path(__file__).resolve().parent.parent / "experiments" / "exp_t5c_pp225_pythia14b_fp32proj_v1.py"
out = base.read_text(encoding="utf-8")
out = out.replace("t5c_pp225_pythia14b_fp32proj_v1", "t5c_pp225_pythia14b_kb10k_v1")
out = out.replace("pp225-pythia14b-fp32proj", "pp225-pythia14b-kb10k")
out = out.replace("N_FACTS = 200 if SMOKE else 1500", "N_FACTS = 200 if SMOKE else 10000")
out = out.replace("STEPS = 100 if \"--smoke\" in sys.argv else 3000", "STEPS = 100 if \"--smoke\" in sys.argv else 8000")
# cap held-out eval to 2000 to avoid eval blowup at large KB
out = out.replace("bare = recall(test, False)", "test = test[:2000]\n    bare = recall(test, False)")
(base.parent / "exp_t5c_pp225_pythia14b_kb10k_v1.py").write_text(out, encoding="utf-8"); print("wrote pp225_pythia14b_kb10k")
