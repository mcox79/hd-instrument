"""Extract ONE coherent dense SimpleWiki ARTICLE per process from the raw bz2 dump (process KNOWN
from the article topic). Reuses the existing build-script cleaning helpers (mwparserfromhell strip_code
+ sentence split). Writes data/corpora/process_articles_v1/process_articles.json = {process: {title:
[sentences]}}. One-time corpus build; cached."""
import json, os, sys
REPO = r"d:/AI/hd-instrument"
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "tools"))
import build_simplewiki_clean_v1 as B  # iter_pages, wikitext_to_text, sentences_from_text, clean_line, quality_ok

OUT_DIR = os.path.join(REPO, "data", "corpora", "process_articles_v1")
os.makedirs(OUT_DIR, exist_ok=True)
DUMP = os.path.join(REPO, "data", "corpora", "simplewiki", "simplewiki-latest-pages-articles.xml.bz2")

# process -> candidate article titles (case-insensitive exact title match; take ALL that exist)
TITLE_MAP = {
    "combustion": ["combustion", "fire", "wildfire"],
    "photosynthesis": ["photosynthesis"],
    "respiration": ["cellular respiration", "respiration", "breathing"],
    "water_cycle": ["water cycle"],
    "erosion_weathering": ["erosion", "weathering"],
    "sedimentation": ["sedimentation", "sediment"],
    "fossilization": ["fossil", "fossilization"],
    "igneous_rock_cycle": ["igneous rock", "rock cycle", "magma", "lava", "volcano"],
    "hydrocarbon_formation": ["petroleum", "fossil fuel", "coal", "natural gas"],
    "digestion": ["digestion", "human digestive system", "digestive system"],
    "nitrogen_cycle": ["nitrogen cycle"],
    "carbon_cycle": ["carbon cycle"],
    "electricity_generation": ["electricity generation", "power station", "electricity", "electric generator"],
    "sound_propagation": ["sound"],
    "neural_signaling": ["neuron", "nerve", "action potential"],
    "phase_change": ["evaporation", "condensation", "boiling", "melting", "state of matter", "phase transition"],
    "dissolution": ["solvation", "solubility", "solution (chemistry)", "dissolving"],
    "decomposition": ["decomposition", "decomposer"],
}
# title (lower) -> process
want = {}
for proc, titles in TITLE_MAP.items():
    for t in titles:
        want[t] = proc

articles = {}  # process -> {title: [sentences]}
n_pages = 0
n_found = 0
found_titles = set()
for title, wikitext in B.iter_pages(DUMP):
    n_pages += 1
    tl = (title or "").strip().lower()
    if tl in want and tl not in found_titles:
        text = B.wikitext_to_text(wikitext)
        sents = []
        for s in B.sentences_from_text(text):
            cl = B.clean_line(s)
            if cl and B.quality_ok(cl, cl.split()):
                sents.append(cl)
        if len(sents) >= 3:
            proc = want[tl]
            articles.setdefault(proc, {})[title] = sents
            found_titles.add(tl)
            n_found += 1
            print(f"[found] {proc:>22} <- '{title}' ({len(sents)} sentences)", flush=True)
    if n_found >= len(want) or (len(found_titles) == len(want)):
        break
    if n_pages % 50000 == 0:
        print(f"[scan] {n_pages} pages, {n_found} articles found", flush=True)

# summary
total_sents = sum(len(s) for pm in articles.values() for s in pm.values())
proc_cov = sorted(articles.keys())
print(f"\n[DONE] scanned {n_pages} pages; {n_found} articles; {len(proc_cov)}/{len(TITLE_MAP)} processes covered; "
      f"{total_sents} total sentences")
for proc in sorted(TITLE_MAP):
    got = articles.get(proc, {})
    ns = sum(len(v) for v in got.values())
    print(f"  {proc:>22}: {list(got.keys())} ({ns} sentences)")

out = os.path.join(OUT_DIR, "process_articles.json")
tmp = out + ".tmp"
json.dump({"n_pages_scanned": n_pages, "n_articles": n_found, "processes_covered": proc_cov,
           "total_sentences": total_sents, "articles": articles}, open(tmp, "w", encoding="utf-8"), indent=1)
os.replace(tmp, out)
print("wrote", out)
