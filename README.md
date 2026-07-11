# Citation Tracker

An automated pipeline that tracks citation counts for my publications, updates
weekly, and displays the results as a live dashboard.

**Live dashboard:** https://mm33na.github.io/citation-tracker/

## What it does

1. **Discovers publications automatically** by querying the [CrossRef API](https://api.crossref.org/) for every work linked to my ORCID iD (`0000-0003-2830-7226`) — no manual DOI list to maintain.
2. **Cross-checks citation counts** against two sources:
   - **CrossRef** — counts citations from publishers that deposit reference lists with CrossRef's Cited-by service.
   - **[Semantic Scholar](https://www.semanticscholar.org/)** — broader coverage, since it also indexes preprints and grey literature that CrossRef doesn't track.
3. **Runs automatically every Monday** via GitHub Actions, and commits the refreshed data back to the repo.
4. **Publishes a live dashboard** via GitHub Pages, reading the latest data directly — no rebuild step needed.

## Why two citation counts, and why not just use Google Scholar?

Google Scholar has the most complete citation coverage of any source, but it
has no public API — there's no reliable, terms-of-service-compliant way to
pull its numbers into an automated pipeline. CrossRef and Semantic Scholar
both offer free public APIs, so this project uses them as complementary,
programmatically-accessible sources:

- **CrossRef** is authoritative but undercounts anything not indexed with a
  DOI (reports, preprints, grey literature).
- **Semantic Scholar** catches more of that grey literature, at the cost of
  being a secondary, less-curated source.

Neither fully matches Google Scholar's count — that's expected. This project
isn't a Scholar replacement; it's a self-hosted, automatable, brandable
alternative that can be embedded elsewhere and versioned over time, which
Scholar's profile page doesn't offer.

## Project structure

```
.
├── citation_tracker.py       # Main script: fetch, enrich, export
├── requirements.txt          # Python dependencies
├── index.html                # Dashboard (GitHub Pages)
├── output/
│   ├── publications.csv       # Full publication + citation data
│   ├── publications.xlsx      # Same data, Excel format
│   └── citation_chart.png     # Static chart snapshot
└── .github/workflows/
    └── citation-tracker.yml   # Weekly automation
```

## How it works

`citation_tracker.py`:
1. Queries `https://api.crossref.org/works?filter=orcid:{ORCID_ID}` with
   cursor-based pagination to retrieve every linked work.
2. Parses each result for title, authors, publication date, DOI, and
   CrossRef's citation count.
3. Looks up each DOI on Semantic Scholar's Graph API for a second citation
   count (rate-limited to one request per second to stay within the
   unauthenticated quota).
4. Exports the combined data to `output/publications.csv` and `.xlsx`, and
   renders a static bar chart of the top 20 by CrossRef citation count.

`index.html` reads `output/publications.csv` client-side (via PapaParse) and
renders:
- Summary stats (total publications, total citations, average, most recent)
- An interactive bar chart of the top 12 most-cited papers
- A searchable, sortable card list of every publication, showing both
  citation counts side by side

`.github/workflows/citation-tracker.yml` runs the script every Monday at
06:00 UTC (or on-demand via the Actions tab → "Run workflow"), then commits
any changed output files back to the repo — which the dashboard picks up
automatically on next page load.

## Running it locally

```bash
pip install -r requirements.txt
python citation_tracker.py
```

Before running, set `CONTACT_EMAIL` near the top of `citation_tracker.py` to
your real email — CrossRef's "polite pool" gives faster, more reliable
responses to requests that identify a contact.

## Setup notes

- **GitHub Pages**: Settings → Pages → Source → deploy from `main`, `/ (root)`.
- **Workflow permissions**: the workflow needs `contents: write` to commit
  output back to the repo (already configured in the workflow file).
- **ORCID coverage caveat**: this only finds works where a publisher has
  actually linked the DOI to my ORCID iD in CrossRef's metadata. Older
  publications (particularly pre-2018) may be missing if the publisher never
  backfilled that link — worth a periodic manual spot-check against a known
  publication list.

## Data sources

- [CrossRef REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
- [Semantic Scholar Academic Graph API](https://api.semanticscholar.org/api-docs/graph)
