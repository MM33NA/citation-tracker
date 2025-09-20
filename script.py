#!/usr/bin/env python
# coding: utf-8

"""
Automated Citation Tracker for Journal Publications
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

def get_crossref_metadata(doi):
    """Fetch metadata for a given DOI from CrossRef API"""
    url = f'https://api.crossref.org/works/{doi.strip()}'
    
    try:
        headers = {'User-Agent': 'Citation-Tracker/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Failed to fetch metadata for DOI: {doi}")
            return None
        
        data = response.json()
        
        # Extract the article title
        article_title = data['message'].get('title', ['No Title Available'])[0]
        
        # Handle author data
        authors = []
        try:
            for author in data['message'].get('author', []):
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
        except (KeyError, TypeError):
            authors.append('Unknown Author')
        
        # Extract and format the publication date
        published_date_time = data['message'].get('created', {}).get('date-time', 'No Date Available')
        if published_date_time != 'No Date Available':
            try:
                if published_date_time.endswith('Z'):
                    published_date_time = published_date_time[:-1] + '+00:00'
                published_date = datetime.fromisoformat(published_date_time).date()
            except ValueError:
                published_date = 'No Date Available'
        else:
            published_date = 'No Date Available'
        
        # Extract citation count
        citation_count = data['message'].get('is-referenced-by-count', 0)
        if citation_count is None:
            citation_count = 0
        
        # Construct the DOI link
        doi_link = f'https://doi.org/{doi.strip()}'
        
        return {
            'Authors': ', '.join(authors) if authors else 'Unknown Author',
            'Title': article_title,
            'Published Date': published_date,
            'Citations': citation_count,
            'DOI link': doi_link
        }
    
    except Exception as e:
        print(f"Error fetching DOI {doi}: {e}")
        return None

# List of DOIs to track
dois = [
    '10.3390/nu12061878', 
    '10.1136/bmjopen-2021-054839', 
    '10.1016/j.glt.2023.11.001', 
    '10.1177/1179173X231205377', 
    '10.3389/fpubh.2022.1012727', 
    '10.1377/hlthaff.26.6.w717',
    '10.14219/jada.archive.2008.0101',
    '10.1186/1477-7525-7-46',
    '10.1590/s0036-36342010000800017',
    '10.1136/tc.2009.035022',
    '10.1080/10810730.2011.601395',
    '10.1016/S0140-6736(11)61058-1',
    '10.1136/tc.2010.039321',
    '10.1136/tc.2010.041269',
    '10.1136/tobaccocontrol-2016-053564',
    '10.1016/j.aap.2016.01.005',
    '10.1007/s10552-012-9903-3',
    '10.1136/tobaccocontrol-2011-050171',
    '10.1136/tobaccocontrol-2012-050946',
    '10.1136/tobaccocontrol-2011-050282',
    '10.17061/phrp2531530',
    '10.1093/her/cyu044',
    '10.1093/her/cyv031',
    '10.1136/tobaccocontrol-2014-051682',
    '10.1186/s12889-015-2159-6',
    '10.1016/j.appet.2016.04.008',
    '10.1136/tobaccocontrol-2016-052968',
    '10.1111/1471-0528.14223',
    '10.1371/journal.pone.0151419',
    '10.4103/2224-3151.213791',
    '10.1016/S0140-6736(17)30819-X',
    '10.21037/ACE.2019.07.03',
    '10.3390/nu12020569',
    '10.1371/journal.pone.0230050',
    '10.3390/nu12103124',
    '10.3389/frsc.2020.563350',
    '10.1016/j.appet.2022.106283',
    '10.1136/bmjgh-2021-007240',
    '10.1136/bmjopen-2021-056725',
    '10.3390/nu14142866',
    '10.3390/nu14153128',
    '10.9745/GHSP-D-21-00484',
    '10.1007/s40615-021-01167-5',
    '10.1371/journal.pone.0263324',
    '10.34172/ijhpm.2023.7685'
]

print(f"Starting citation tracker for {len(set(dois))} unique DOIs...")

# Create output directory
os.makedirs('output', exist_ok=True)

# Fetch metadata for each DOI
metadata_list = []
successful_fetches = 0

for i, doi in enumerate(set(dois), 1):
    print(f"Processing DOI {i}/{len(set(dois))}: {doi}")
    metadata = get_crossref_metadata(doi)
    if metadata:
        metadata_list.append(metadata)
        successful_fetches += 1

print(f"Successfully fetched metadata for {successful_fetches} DOIs")

if not metadata_list:
    print("No metadata could be fetched. Exiting.")
    exit(1)

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