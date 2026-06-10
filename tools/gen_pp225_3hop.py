"""GPU-8 PP225-MULTIHOP-3HOP-160M: derive from the 2-hop cell by extending the chain to 3 hops (subject->manager->colleague->code). Write-tool authored."""
import pathlib
base = pathlib.Path(__file__).resolve().parent.parent / "experiments" / "exp_t5c_pp225_multihop_gpu_v1.py"
out = base.read_text(encoding="utf-8")
out = out.replace("t5c_pp225_multihop_gpu_v1", "t5c_pp225_multihop_3hop_gpu_v1")
out = out.replace("pp225-multihop", "pp225-multihop-3hop")
# add a manager intermediate (hop 1); colleague becomes hop 2; code hop 3
assert "b = subs[(i + 7) % len(subs)]" in out, "chain anchor missing"
out = out.replace("b = subs[(i + 7) % len(subs)]", "m = subs[(i + 13) % len(subs)]; b = subs[(i + 7) % len(subs)]")
out = out.replace('"The secret code of the colleague of %s is" % s',
                  '"The secret code of the colleague of the manager of %s is" % s')
out = out.replace('"The colleague of %s is %s. The secret code of %s is%s." % (s, b, b, a)',
                  '"The manager of %s is %s. The colleague of %s is %s. The secret code of %s is%s." % (s, m, m, b, b, a)')
out = out.replace("max_length=32", "max_length=48")   # longer 3-hop chain text
(base.parent / "exp_t5c_pp225_multihop_3hop_gpu_v1.py").write_text(out, encoding="utf-8")
print("wrote pp225_multihop_3hop")
