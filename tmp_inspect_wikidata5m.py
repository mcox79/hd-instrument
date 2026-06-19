"""Inspect intfloat/wikidata5m schema."""
from datasets import load_dataset

ds = load_dataset("intfloat/wikidata5m", split="train", streaming=True)
print("inspecting first 3 rows of intfloat/wikidata5m:")
for i, row in enumerate(ds):
    if i >= 3:
        break
    print(f"row {i}: keys={list(row.keys())}")
    for k, v in row.items():
        v_str = str(v)[:200]
        print(f"  {k} = {v_str}")
    print()
