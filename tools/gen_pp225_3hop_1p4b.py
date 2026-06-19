"""GPU refill: PP225-MULTIHOP-3HOP-1.4B -- derive from the 2hop-1.4b cell + manager hop (subject->manager->colleague->code). Write-tool authored."""
import pathlib
base = pathlib.Path(__file__).resolve().parent.parent / "experiments" / "exp_t5c_pp225_multihop_2hop_1p4b_v1.py"
out = base.read_text(encoding="utf-8")
out = out.replace("t5c_pp225_multihop_2hop_1p4b_v1", "t5c_pp225_multihop_3hop_1p4b_v1")
out = out.replace("pp225-multihop-2hop-1p4b", "pp225-multihop-3hop-1p4b")
out = out.replace("b = subs[(i + 7) % len(subs)]", "m = subs[(i + 13) % len(subs)]; b = subs[(i + 7) % len(subs)]")
out = out.replace('"The secret code of the colleague of %s is" % s', '"The secret code of the colleague of the manager of %s is" % s')
out = out.replace('"The colleague of %s is %s. The secret code of %s is%s." % (s, b, b, a)',
                  '"The manager of %s is %s. The colleague of %s is %s. The secret code of %s is%s." % (s, m, m, b, b, a)')
out = out.replace("max_length=48", "max_length=64")
(base.parent / "exp_t5c_pp225_multihop_3hop_1p4b_v1.py").write_text(out, encoding="utf-8"); print("wrote pp225_multihop_3hop_1p4b")
