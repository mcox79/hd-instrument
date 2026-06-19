"""Probe Wikidata dump URL + check if requests is installed."""
import sys

try:
    import requests
except ImportError as e:
    print("requests NOT installed:", e)
    sys.exit(1)

URL = "https://dumps.wikimedia.org/wikidatawiki/entities/latest-truthy.nt.bz2"
print(f"probing {URL} ...")
r = requests.head(URL, allow_redirects=True, timeout=30)
print(f"  status: {r.status_code}")
print(f"  content-length: {r.headers.get('content-length', 'N/A')}")
print(f"  final url: {r.url}")
