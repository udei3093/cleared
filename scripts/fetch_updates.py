#!/usr/bin/env python3
"""
Cleared -- Regulatory Radar updater.

Pulls fresh documents from the free, public Federal Register API
(no key required) related to EO 14411 / customs enforcement / importer
compliance, filters for relevance, merges with the existing
data/updates.json, and writes the result back so the site can render
it as a live feed.

Runs on a schedule via .github/workflows/update-feed.yml. No LLM or
paid API involved -- just the public Federal Register REST API and
the Python standard library.
"""
import json
import os
import urllib.parse
import urllib.request
import datetime

API = "https://www.federalregister.gov/api/v1/documents.json"
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "updates.json")

QUERIES = [
    "Executive Order 14411",
    "importer of record",
    "customs enforcement",
    "beneficial ownership customs",
    "CBP bond importer",
    "forced labor import tariff",
]

RELEVANT_AGENCY_SLUGS = {
    "u-s-customs-and-border-protection",
    "homeland-security-department",
    "u-s-immigration-and-customs-enforcement",
    "international-trade-commission",
    "office-of-united-states-trade-representative",
}

RELEVANT_KEYWORDS = [
    "importer of record", "customs enforcement", "cbp", "beneficial ownership",
    "customs bond", "importer", "trade compliance", "executive order 14411",
    "forced labor", "section 301", "tariff",
]


def fetch(term, per_page=8):
    q = urllib.parse.urlencode({
        "per_page": per_page,
        "order": "newest",
        "conditions[term]": term,
    })
    url = f"{API}?{q}"
    req = urllib.request.Request(url, headers={"User-Agent": "cleared-regulatory-radar/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp).get("results", [])


def is_relevant(doc):
    agencies = doc.get("agencies") or []
    slugs = {a.get("slug") for a in agencies if a.get("slug")}
    if slugs & RELEVANT_AGENCY_SLUGS:
        return True
    text = f"{doc.get('title','')} {doc.get('abstract') or ''}".lower()
    return any(k in text for k in RELEVANT_KEYWORDS)


def main():
    existing = {"last_checked": None, "items": []}
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH) as f:
            existing = json.load(f)

    by_number = {item["document_number"]: item for item in existing.get("items", [])}

    for term in QUERIES:
        try:
            results = fetch(term)
        except Exception as e:
            print(f"skip '{term}': {e}")
            continue
        for doc in results:
            num = doc.get("document_number")
            if not num or num in by_number:
                continue
            if not is_relevant(doc):
                continue
            agencies = doc.get("agencies") or []
            agency_name = agencies[0]["name"] if agencies else "Federal Register"
            by_number[num] = {
                "document_number": num,
                "title": doc.get("title"),
                "type": doc.get("type"),
                "agency": agency_name,
                "publication_date": doc.get("publication_date"),
                "url": doc.get("html_url"),
                "summary": (doc.get("abstract") or "")[:320],
            }

    items = sorted(by_number.values(), key=lambda x: x.get("publication_date") or "", reverse=True)
    items = items[:40]

    out = {
        "last_checked": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items": items,
    }

    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(out, f, indent=2)

    print(f"Wrote {len(items)} items to {DATA_PATH}")


if __name__ == "__main__":
    main()
