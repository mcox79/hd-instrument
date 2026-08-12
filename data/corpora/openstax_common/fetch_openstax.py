# -*- coding: utf-8 -*-
"""
Generic fetcher for OpenStax CNXML book-bundle repos (2026-08-12).

Fetches a collection.xml + all its module CNXML files via raw.githubusercontent.com (no git
clone -- individual small XML files only, no images/binary history), and writes a
collection_structure.json in the same flattened {"title", "items":[{"type":"heading"/"module",
...}]} shape that data/corpora/textbook_concepts_biology/raw/collection_structure.json already
uses, so the existing (now-parameterized) clean_cnxml.py can run against it unchanged.

No LLM / torch / spaCy -- stdlib only (urllib + xml.etree.ElementTree).

Usage:
  python fetch_openstax.py --repo osbooks-psychology --collection psychology-2e \
      --out-base d:/AI/hd-instrument/data/corpora/textbook_psychology_2e
"""
import argparse
import json
import os
import time
import urllib.request
import xml.etree.ElementTree as ET

RAW_BASE = "https://raw.githubusercontent.com/openstax/{repo}/main/{path}"

COL_NS = {"col": "http://cnx.rice.edu/collxml", "md": "http://cnx.rice.edu/mdml"}


def fetch(url, retries=3):
    last_err = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"failed to fetch {url}: {last_err}")


def parse_collection(xml_bytes):
    root = ET.fromstring(xml_bytes)
    md = root.find("col:metadata", COL_NS)
    title = md.find("md:title", COL_NS).text.strip()
    license_el = md.find("md:license", COL_NS)
    license_url = license_el.get("url") if license_el is not None else None

    content = root.find("col:content", COL_NS)
    items = []

    def walk(node, level):
        for child in node:
            tag = child.tag.split("}", 1)[-1]
            if tag == "module":
                items.append({"type": "module", "id": child.get("document")})
            elif tag == "subcollection":
                t = child.find("md:title", COL_NS)
                items.append({"type": "heading", "level": level, "title": t.text.strip() if t is not None else ""})
                sub_content = child.find("col:content", COL_NS)
                if sub_content is not None:
                    walk(sub_content, level + 1)

    walk(content, 1)
    return title, license_url, items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="openstax/<repo> name, e.g. osbooks-psychology")
    ap.add_argument("--collection", required=True, help="collection slug, e.g. psychology-2e")
    ap.add_argument("--out-base", required=True, help="output corpus dir, e.g. .../textbook_psychology_2e")
    args = ap.parse_args()

    raw_dir = os.path.join(args.out_base, "raw")
    mod_dir = os.path.join(raw_dir, "modules")
    os.makedirs(mod_dir, exist_ok=True)

    col_path = f"collections/{args.collection}.collection.xml"
    col_url = RAW_BASE.format(repo=args.repo, path=col_path)
    col_bytes = fetch(col_url)
    col_file = os.path.join(raw_dir, f"{args.collection}.collection.xml")
    with open(col_file, "wb") as f:
        f.write(col_bytes)

    title, license_url, items = parse_collection(col_bytes)
    n_modules = sum(1 for it in items if it["type"] == "module")
    print(f"collection={args.collection} title={title!r} license={license_url} n_modules={n_modules}")

    total_bytes = len(col_bytes)
    errors = []
    for it in items:
        if it["type"] != "module":
            continue
        mid = it["id"]
        dest = os.path.join(mod_dir, mid + ".cnxml")
        if os.path.exists(dest):
            total_bytes += os.path.getsize(dest)
            continue
        url = RAW_BASE.format(repo=args.repo, path=f"modules/{mid}/index.cnxml")
        try:
            data = fetch(url)
        except Exception as e:  # noqa: BLE001
            errors.append({"id": mid, "error": str(e)})
            continue
        with open(dest, "wb") as f:
            f.write(data)
        total_bytes += len(data)

    struct = {"title": title, "items": items}
    struct_path = os.path.join(raw_dir, "collection_structure.json")
    with open(struct_path, "w", encoding="utf-8") as f:
        json.dump(struct, f, indent=2)

    print(f"fetched {n_modules - len(errors)}/{n_modules} modules, "
          f"total_raw_bytes={total_bytes} ({total_bytes / 1e6:.2f} MB), errors={len(errors)}")
    if errors:
        for e in errors:
            print("  ERR", e)
    print("wrote", struct_path)
    print("license_url", license_url)


if __name__ == "__main__":
    main()
