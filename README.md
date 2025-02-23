# Citation Tracker for Journal Publications

## Overview
The **Citation Tracker for Journal Publications** is an automated tool designed to help researchers and academics efficiently track citations for their published papers. By using DOI numbers, the tracker collects metadata about each publication and sorts it by the latest published date. This tool simplifies the citation management process and allows users to visualize and export citation data in an easily shareable format.

## Purpose
The goal of this project is to automate the process of collecting citation metadata for academic papers, sorting the results by the most recent publications, and enabling researchers to track their paper citations more effectively.

## Features
- **Fetch Metadata**: Collect citation metadata for multiple DOIs.
- **Data Storage**: Store the metadata in a structured format for easy analysis.
- **Sorting**: Automatically sort the citation data by the latest publication date.
- **Export to Excel**: Export the results to an Excel file for sharing and further analysis.
- **Visualization**: Create charts to visualize the most cited papers, sorted from high to low.

## Prerequisites
Before running the script, ensure that you have the following Python libraries installed:
- `requests`
- `pandas`
- `matplotlib` (optional for charts).

## Usage

**1. Clone the Repository:** Clone the repository to your local machine.

**2. Add DOI Numbers:** Update the script with the DOIs of the papers you want to track.

**3. Run the Script:** Execute the Python script to fetch citation metadata, process the data, and export it to an Excel file.

## Example Output
The script generates a sorted list of papers by publication date, exports the results to an Excel file, and optionally creates charts to visualize citation trends

## File Descriptions

**script.ipynb:** Main script for fetching metadata, processing data, and exporting results.

**.gitignore:** Git ignore file to prevent unnecessary files from being tracked in the repository (e.g., .ipynb_checkpoints/).

**README.md:** Documentation for the project (this file).

## How to Contribute
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes.
4. Push your changes to your forked repository.
5. Submit a pull request with a description of the changes you've made.

## License
This project is licensed under the MIT License. See the **LICENSE** file for more details.