#!/usr/bin/env python
# coding: utf-8

"""
Automated Citation Tracker for Journal Publications
Auto-discovers publications via ORCID iD instead of a hardcoded DOI list.
Fixed for GitHub Actions - No hardcoded paths
"""

import os
import pandas as pd
import requests
from datetime import datetime
import textwrap
import matplotlib
import matplotlib.pyplot as plt

# Set matplotlib backend for headless environments (GitHub Actions)
matplotlib.use('Agg')

# ---- Configuration ----
ORCID_ID = '0000-0003-2830-7226'
# CrossRef's "polite pool" gives faster/more reliable responses if you
# include a contact email in the User-Agent. Put your real email here.
CONTACT_EMAIL = 'mmaharjan039@gmail.com'
USER_AGENT = f'Citation-Tracker/2.0 (mailto:{CONTACT_EMAIL})'
ROWS_PER_PAGE = 100


def fetch_works_by_orcid(orcid_id):
    """
    Fetch all CrossRef works asserted against this ORCID iD.
    Uses cursor-based deep paging to get every result, not just the first page.
    Returns a list of raw CrossRef 'message.items' dicts.
    """
    base_url = 'https://api.crossref.org/works'
    headers = {'User-Agent': USER_AGENT}
    params = {
        'filter': f'orcid:{orcid_id}',
        'rows': ROWS_PER_PAGE,
        'cursor': '*'
    }

    all_items = []
    while True:
        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=15)
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            break

        if response.status_code != 200:
            print(f"Failed to fetch works for ORCID {orcid_id}: HTTP {response.status_code}")
            break

        data = response.json()
        message = data.get('message', {})
        items = message.get('items', [])
        all_items.extend(items)

        next_cursor = message.get('next-cursor')
        total_results = message.get('total-results', len(all_items))

        print(f"Fetched {len(all_items)}/{total_results} works so far...")

        if not next_cursor or len(items) == 0 or len(all_items) >= total_results:
            break

        params['cursor'] = next_cursor

    return all_items


def parse_work_item(item):
    """Convert a raw CrossRef work item into our flat metadata dict."""
    doi = item.get('DOI', '')
    article_title_list = item.get('title', [])
    article_title = article_title_list[0] if article_title_list else 'No Title Available'

    authors = []
    for author in item.get('author', []):
        given_name = author.get('given', '')
        family_name = author.get('family', '')
        if given_name and family_name:
            authors.append(f'{given_name} {family_name}')
        elif given_name:
            authors.append(given_name)
        elif family_name:
            authors.append(family_name)
        else:
            authors.append('Unknown Author')

    published_date_time = item.get('created', {}).get('date-time', 'No Date Available')
    if published_date_time != 'No Date Available':
        try:
            if published_date_time.endswith('Z'):
                published_date_time = published_date_time[:-1] + '+00:00'
            published_date = datetime.fromisoformat(published_date_time).date()
        except ValueError:
            published_date = 'No Date Available'
    else:
        published_date = 'No Date Available'

    citation_count = item.get('is-referenced-by-count', 0)
    if citation_count is None:
        citation_count = 0

    doi_link = f'https://doi.org/{doi}' if doi else 'No DOI'

    return {
        'Authors': ', '.join(authors) if authors else 'Unknown Author',
        'Title': article_title,
        'Published Date': published_date,
        'Citations': citation_count,
        'DOI link': doi_link
    }


print(f"Fetching all publications for ORCID {ORCID_ID}...")

raw_items = fetch_works_by_orcid(ORCID_ID)
print(f"Retrieved {len(raw_items)} works from CrossRef")

if not raw_items:
    print("No works could be fetched. Exiting.")
    exit(1)

metadata_list = [parse_work_item(item) for item in raw_items]

# Create output directory
os.makedirs('output', exist_ok=True)

# Convert to DataFrame
df = pd.DataFrame(metadata_list)

# Drop duplicates and sort
df = df.drop_duplicates(subset=['Title'], keep='first')
df = df.sort_values(by=['Citations', 'Published Date'], ascending=[False, False])
df.index = range(1, len(df) + 1)

# Export files
df.to_excel('output/publications.xlsx', index=True)
df.to_csv('output/publications.csv', index=True)
print(f"Data exported to output/ directory")

# Display summary
print(f"\nSummary:")
print(f"Total publications: {len(df)}")
print(f"Total citations: {df['Citations'].sum()}")
print(f"Average citations: {df['Citations'].mean():.1f}")

# Create chart
if len(df) > 0:
    df_chart = df.head(20).copy()
    df_chart['Title_Short'] = df_chart['Title'].apply(
        lambda x: textwrap.shorten(str(x), width=60, placeholder='...')
    )
    df_chart = df_chart.sort_values(by='Citations', ascending=True)

    plt.figure(figsize=(14, max(10, len(df_chart) * 0.4)))
    bars = plt.barh(df_chart['Title_Short'], df_chart['Citations'], color='skyblue')
    plt.title('Top 20 Publications by Citation Count', fontsize=16, fontweight='bold')
    plt.xlabel('Citation Count')
    plt.ylabel('Publication Title')

    for i, (bar, count) in enumerate(zip(bars, df_chart['Citations'])):
        plt.text(bar.get_width() + max(df_chart['Citations']) * 0.01,
                bar.get_y() + bar.get_height()/2,
                f'{int(count)}',
                ha='left', va='center')

    plt.tight_layout()
    plt.savefig('output/citation_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Chart saved to output/citation_chart.png")

print("Citation tracker completed successfully!")