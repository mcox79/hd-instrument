"""GPU refill: PP225-MULTIHOP-2HOP-1.4B -- derive from the working pythia14b fp32-head cell (correct bf16-backbone/fp32-head pattern) + 2-hop colleague chain. Write-tool authored."""
import pathlib
base = pathlib.Path(__file__).resolve().parent.parent / "experiments" / "exp_t5c_pp225_pythia14b_fp32proj_v1.py"
out = base.read_text(encoding="utf-8")
out = out.replace("t5c_pp225_pythia14b_fp32proj_v1", "t5c_pp225_multihop_2hop_1p4b_v1")
out = out.replace("pp225-pythia14b-fp32proj", "pp225-multihop-2hop-1p4b")
old = '''    for s in subs:
        a = pool[int(g.integers(0, len(pool)))]
        facts.append({"prompt": "The secret code of %s is" % s, "aid": tok(a, add_special_tokens=False)["input_ids"][0], "text": "The secret code of %s is%s." % (s, a)})'''
new = '''    for i, s in enumerate(subs):
        b = subs[(i + 7) % len(subs)]                                    # colleague (hidden 2-hop intermediate)
        a = pool[int(g.integers(0, len(pool)))]
        facts.append({"prompt": "The secret code of the colleague of %s is" % s, "aid": tok(a, add_special_tokens=False)["input_ids"][0], "text": "The colleague of %s is %s. The secret code of %s is%s." % (s, b, b, a)})'''
assert old in out, "fact-loop anchor not found"
out = out.replace(old, new)
out = out.replace("max_length=32", "max_length=48")   # longer 2-hop chain text
(base.parent / "exp_t5c_pp225_multihop_2hop_1p4b_v1.py").write_text(out, encoding="utf-8"); print("wrote pp225_multihop_2hop_1p4b")
