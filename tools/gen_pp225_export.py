"""Derive a PP-225 checkpoint-EXPORT GPU cell from the working fp32proj cell: same training, plus torch.save of the head for Testbed's backend. Write-tool authored."""
import pathlib
base = pathlib.Path(__file__).resolve().parent.parent / "experiments" / "exp_t5c_pp225_pythia14b_fp32proj_v1.py"
src = base.read_text(encoding="utf-8")
out = src.replace("t5c_pp225_pythia14b_fp32proj_v1", "t5c_pp225_export_ckpt_v1")
# raise the HARD-PASS framing note + insert torch.save right after the final recall (proj+scale in scope)
anchor = '    tr = recall(train, True); te = recall(test, True); prog.close(); del mdl'
save = (anchor
    + '\n    import os as _os; _os.makedirs("data/pp225_export", exist_ok=True)'
    + '\n    _ck = {"W": proj.weight.detach().float().cpu(), "scale": float(scale.detach().cpu()), "model": MODEL, "encoder": ENCODER, "vocab": int(V), "edim": int(Edim), "heldout_recall": float(te)}'
    + '\n    torch.save(_ck, "data/pp225_export/head_pythia14b_fp32.pt")'
    + '\n    print("[export] saved fp32 PP-225 head -> data/pp225_export/head_pythia14b_fp32.pt (W=(%d,%d) scale=%.4f heldout=%.3f)" % (int(V), int(Edim), float(scale.detach().cpu()), te), flush=True)')
assert anchor in out, "anchor line not found"
out = out.replace(anchor, save)
(base.parent / "exp_t5c_pp225_export_ckpt_v1.py").write_text(out, encoding="utf-8")
print("wrote export cell")
