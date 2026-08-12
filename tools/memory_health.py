"""Memory-index health check: size, per-section bloat, orphan/unindexed pointers, staleness.
Run before compaction so it's a 60-second guided pass, not a hunt. ASCII-only, read-only.
Usage: python tools/memory_health.py [MEMORY_DIR]"""
import os, re, sys, time

MEM = sys.argv[1] if len(sys.argv) > 1 else r"C:/Users/marsh/.claude/projects/d--AI/memory"
INDEX = os.path.join(MEM, "MEMORY.md")
SOFT_KB, HARD_KB = 17.1, 24.4  # compact-now target / read-limit

txt = open(INDEX, encoding="utf-8", errors="replace").read()
kb = len(txt.encode("utf-8")) / 1024
flag = "OK" if kb < SOFT_KB else ("COMPACT NOW" if kb < HARD_KB else "OVER READ LIMIT")
print(f"MEMORY.md = {kb:.1f} KB  [{flag}]  (soft {SOFT_KB} / hard {HARD_KB})\n")

# per-section size (## headers) -> find the bloat
secs = re.split(r"(?m)^(## .*)$", txt)
print("=== size per section (bytes) -- biggest = compaction target ===")
rows = []
for i in range(1, len(secs), 2):
    rows.append((len(secs[i + 1].encode("utf-8")), secs[i].strip()))
def ascii_safe(s):
    return s.encode("ascii", "replace").decode("ascii")
for n, h in sorted(rows, reverse=True)[:8]:
    print(f"  {n:6d}  {ascii_safe(h)[:70]}")

# pointer integrity: gather refs from MEMORY.md AND all secondary MEMORY_*.md indexes
index_txt = txt
for f in os.listdir(MEM):
    if f.startswith("MEMORY_") and f.endswith(".md"):
        index_txt += "\n" + open(os.path.join(MEM, f), encoding="utf-8", errors="replace").read()
refs = set(re.findall(r"\[\[([a-z0-9_\-]+)\]\]", index_txt)) | set(re.findall(r"\]\(([A-Za-z0-9_\-./]+\.md)\)", index_txt))
ref_stems = {os.path.splitext(os.path.basename(r))[0] for r in refs}
files = [f for f in os.listdir(MEM) if f.endswith(".md") and f != "MEMORY.md"]
file_stems = {os.path.splitext(f)[0] for f in files}
orphans = sorted(s for s in ref_stems if s not in file_stems and not s.startswith("MEMORY_"))
unindexed = sorted(s for s in file_stems if s not in ref_stems and not s.startswith("MEMORY_"))
print(f"\n=== pointer integrity ===")
print(f"  {len(files)} memory files, {len(ref_stems)} referenced")
if orphans:
    print(f"  ORPHAN pointers (in index, NO file -- fix or drop): {len(orphans)}")
    for s in orphans[:12]: print(f"    [[{s}]]")
if unindexed:
    print(f"  UNINDEXED files (on disk, not in index -- add a line or archive): {len(unindexed)}")
    for s in unindexed[:12]: print(f"    {s}")

# staleness: oldest files = collapse candidates
now = time.time()
aged = sorted(((now - os.path.getmtime(os.path.join(MEM, f))) / 86400, f) for f in files)
print(f"\n=== stalest memory files (days since edit -- fold into category pointers) ===")
for d, f in aged[-10:][::-1]:
    print(f"  {d:5.0f}d  {f}")
