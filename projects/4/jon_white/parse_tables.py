#!/usr/bin/env python3
"""
Multi-URL Table to CSV Parser

This script downloads multiple webpages from provided comma-separated URLs, extracts all tables
found in the HTML content, and writes each table to a CSV file in the local directory.
Filenames are generated based on the input URL and table captions or positions.

Usage:
    python multi_url_table_to_csv.py <url1,url2,url3,...>

Example:
    python multi_url_table_to_csv.py https://en.wikipedia.org/wiki/List_of_largest_companies_by_revenue,https://en.wikipedia.org/wiki/Fortune_Global_500
"""

import sys
import re
import os
import csv
import urllib.request
import urllib.parse
import html.parser
import json

import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class WikiTableParser(html.parser.HTMLParser):
    """
    HTML Parser that extracts tables from Wikipedia HTML content and converts them to
    lists of dictionaries with improved handling for Wikipedia-specific formatting.
    """
    def __init__(self):
        super().__init__()
        self.tables = []           # List to store all tables
        self.current_table = None  # Current table being processed
        self.current_row = None    # Current row being processed
        self.current_cell = []     # Content of current cell being processed
        self.processing_th = False # Whether currently processing a header cell
        self.processing_td = False # Whether currently processing a data cell
        self.headers = []          # Headers for the current table
        self.in_table = False      # Whether currently inside a table
        self.in_tr = False         # Whether currently inside a table row
        self.in_caption = False    # Whether currently inside a table caption
        self.current_caption = ""  # Caption of the current table
        self.current_attrs = {}    # Current cell attributes (colspan, rowspan)
        self.spans = []            # Track cells with rowspan
        self.table_class = ""      # Class of the current table
        self.skip_table = False    # Flag to skip non-data tables
        
    def handle_starttag(self, tag, attrs):
        """Handle start tags in HTML content."""
        attrs_dict = dict(attrs)
        
        if tag == 'table':
            self.in_table = True
            self.current_table = []
            self.headers = []
            self.spans = []
            self.current_caption = ""
            
            # Check for wikitable class to identify main data tables
            self.table_class = attrs_dict.get('class', '')
            # Skip tables that are not likely to contain main data
            self.skip_table = 'wikitable' not in self.table_class.lower() and 'sortable' not in self.table_class.lower()
            
        elif tag == 'caption' and self.in_table:
            self.in_caption = True
            
        elif tag == 'tr' and self.in_table and not self.skip_table:
            self.in_tr = True
            self.current_row = []
            
            # Apply any rowspan cells from previous rows
            if self.spans:
                new_spans = []
                for idx, content, remaining in self.spans:
                    if remaining > 1:
                        # Insert the spanning cell content
                        while len(self.current_row) <= idx:
                            self.current_row.append("")
                        self.current_row[idx] = content
                        # Update the remaining count and keep track
                        new_spans.append((idx, content, remaining - 1))
                self.spans = new_spans
            
        elif tag == 'th' and self.in_tr:
            self.processing_th = True
            self.current_cell = []
            # Track colspan and rowspan
            self.current_attrs = {
                'colspan': int(attrs_dict.get('colspan', 1)),
                'rowspan': int(attrs_dict.get('rowspan', 1))
            }
            
        elif tag == 'td' and self.in_tr:
            self.processing_td = True
            self.current_cell = []
            # Track colspan and rowspan
            self.current_attrs = {
                'colspan': int(attrs_dict.get('colspan', 1)),
                'rowspan': int(attrs_dict.get('rowspan', 1))
            }
    
    def handle_endtag(self, tag):
        """Handle end tags in HTML content."""
        if tag == 'table':
            # If we have a complete table and it's not skipped, add it to our tables list
            if self.current_table and not self.skip_table:
                # If we found headers, convert rows to dictionaries
                if self.headers:
                    dict_table = {
                        'caption': self.current_caption,
                        'headers': self.headers.copy(),
                        'data': []
                    }
                    
                    for row in self.current_table:
                        # For each row, create a dictionary mapping header -> value
                        row_dict = {}
                        col_idx = 0
                        
                        for cell_idx, cell in enumerate(row):
                            # Make sure we don't go out of bounds
                            if col_idx < len(self.headers):
                                header = self.headers[col_idx]
                                # Clean up the cell content
                                clean_cell = self._clean_cell_content(cell)
                                row_dict[header] = clean_cell
                                col_idx += 1
                        
                        dict_table['data'].append(row_dict)
                    
                    self.tables.append(dict_table)
                else:
                    # If no headers were found, store as a list of rows with caption
                    self.tables.append({
                        'caption': self.current_caption,
                        'headers': [],
                        'data': self.current_table
                    })
                    
            self.in_table = False
            self.current_table = None
            self.skip_table = False
            
        elif tag == 'caption':
            self.in_caption = False
            
        elif tag == 'tr':
            if self.current_row and not self.skip_table:
                if self.current_table is not None:
                    self.current_table.append(self.current_row)
            self.in_tr = False
            self.current_row = None
            
        elif tag == 'th':
            if self.current_cell and not self.skip_table:
                # Join cell content and clean whitespace
                cell_content = ''.join(self.current_cell).strip()
                
                # Handle colspan by repeating the header
                for _ in range(self.current_attrs['colspan']):
                    self.headers.append(cell_content)
                
            self.processing_th = False
            self.current_cell = []
            
        elif tag == 'td':
            if self.current_cell and self.current_row is not None and not self.skip_table:
                # Join cell content and clean whitespace
                cell_content = ''.join(self.current_cell).strip()
                
                # Handle colspan by repeating the cell content
                for _ in range(self.current_attrs['colspan']):
                    self.current_row.append(cell_content)
                
                # Handle rowspan by recording cells that span multiple rows
                if self.current_attrs['rowspan'] > 1:
                    # Calculate the position for the current cell
                    pos = len(self.current_row) - 1
                    self.spans.append((pos, cell_content, self.current_attrs['rowspan']))
                
            self.processing_td = False
            self.current_cell = []
    
    def handle_data(self, data):
        """Handle text data within tags."""
        if self.processing_th or self.processing_td:
            self.current_cell.append(data)
        elif self.in_caption:
            self.current_caption += data
    
    def _clean_cell_content(self, content):
        """
        Clean up cell content by removing reference tags, handling commas in numbers, etc.
        """
        # Remove reference tags like [1], [note 1], etc.
        content = re.sub(r'\[\d+\]|\[note \d+\]|\[\w+\]', '', content)
        
        # Try to convert numeric values with commas to float
        if ',' in content and content.replace(',', '').replace('.', '', 1).replace('-', '', 1).isdigit():
            try:
                return float(content.replace(',', ''))
            except ValueError:
                pass
                
        return content.strip()
    
    def get_tables(self):
        """Return all parsed tables."""
        return self.tables


def download_url(url):
    """
    Download the HTML content from the given URL.
    
    Args:
        url (str): The URL to download.
        
    Returns:
        str: The HTML content of the page, or None if download failed.
    """
    try:
        # Create a request with a user agent to avoid being blocked
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                             '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Error downloading URL {url}: {e}", file=sys.stderr)
        return None


def parse_tables(html_content):
    """
    Parse all tables from HTML content.
    
    Args:
        html_content (str): The HTML content to parse.
        
    Returns:
        list: A list of tables, where each table is a dict with caption, headers, and data.
    """
    parser = WikiTableParser()
    parser.feed(html_content)
    return parser.get_tables()


def generate_filename(url, table_index, caption):
    """
    Generate a filename for a CSV file based on the URL and table information.
    
    Args:
        url (str): The source URL.
        table_index (int): The index of the table on the page.
        caption (str): The caption of the table, if any.
    
    Returns:
        str: A valid filename for the CSV file.
    """
    # Extract domain and path from URL
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc.replace('.', '_')
    
    # Get the last part of the path
    path = parsed_url.path.strip('/').replace('/', '_')
    
    # Create a base filename
    base_filename = f"{domain}_{path}"
    
    # Clean up the caption for use in a filename
    if caption:
        clean_caption = re.sub(r'[^\w\s-]', '', caption).strip().replace(' ', '_')
        # Limit length of caption in filename
        if len(clean_caption) > 50:
            clean_caption = clean_caption[:50]
        if clean_caption:
            return f"{base_filename}_table_{table_index}_{clean_caption}.csv"
    
    # Default if no usable caption
    return f"{base_filename}_table_{table_index}.csv"


def write_table_to_csv(table, filename):
    """
    Write a table to a CSV file.
    
    Args:
        table (dict): The table containing headers and data.
        filename (str): The name of the CSV file to write.
        
    Returns:
        bool: True if file was written successfully, False otherwise.
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if table['headers']:
                # If we have headers, use them as column names
                fieldnames = table['headers']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in table['data']:
                    writer.writerow(row)
            else:
                # If no headers, use CSV writer without dictionaries
                writer = csv.writer(csvfile)
                for row in table['data']:
                    writer.writerow(row)
        return True
    except Exception as e:
        print(f"Error writing to {filename}: {e}", file=sys.stderr)
        return False


def process_url(url):
    """
    Process a single URL: download content, parse tables, and write to CSV files.
    
    Args:
        url (str): The URL to process.
        
    Returns:
        tuple: (url, number of tables found, list of CSV files created)
    """
    print(f"\nProcessing URL: {url}")
    
    # Download the URL content
    html_content = download_url(url)
    if html_content is None:
        return url, 0, []
    
    # Parse tables from HTML content
    tables = parse_tables(html_content)
    
    # Output the tables to CSV files
    if not tables:
        print(f"No tables found on {url}")
        return url, 0, []
    
    print(f"Found {len(tables)} tables on {url}")
    
    csv_files = []
    for i, table in enumerate(tables):
        # Generate a filename based on URL and table caption
        filename = generate_filename(url, i+1, table['caption'])
        
        # Write table to CSV
        if write_table_to_csv(table, filename):
            csv_files.append(filename)
            print(f"  Table {i+1} written to {filename}")
    
    return url, len(tables), csv_files


def main():
    """Main function to handle command line arguments and process the URLs."""
    # Check if URLs are provided
    if len(sys.argv) != 2:
        print("Usage: python multi_url_table_to_csv.py <url1,url2,url3,...>", file=sys.stderr)
        sys.exit(1)
    
    # Split the input into individual URLs
    urls = [u.strip() for u in sys.argv[1].split(',') if u.strip()]
    
    # Validate URLs
    valid_urls = []
    for url in urls:
        try:
            result = urllib.parse.urlparse(url)
            if result.scheme and result.netloc:
                valid_urls.append(url)
            else:
                print(f"Skipping invalid URL: {url}", file=sys.stderr)
        except Exception:
            print(f"Skipping invalid URL: {url}", file=sys.stderr)
    
    if not valid_urls:
        print("No valid URLs provided.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Processing {len(valid_urls)} URLs...\n")
    
    # ---- Sequential run ----
    start_seq = time.perf_counter()
    seq_results = []
    for url in valid_urls:
        seq_results.append(process_url(url))
    end_seq = time.perf_counter()
    duration_seq = end_seq - start_seq
    print(f"\nSequential run completed in {duration_seq:.2f} seconds.\n")
    
    # Summarize sequential results
    total_tables_seq = sum(r[1] for r in seq_results)
    total_files_seq  = sum(len(r[2]) for r in seq_results)
    print("Sequential Summary:")
    for url, num_tables, files in seq_results:
        print(f"  {url}: {num_tables} tables, {len(files)} CSV files")
    print(f"  → Total: {total_tables_seq} tables, {total_files_seq} files\n")
    
    # ---- Threaded run ----
    start_thr = time.perf_counter()
    thr_results = []
    # you can choose max_workers to tune concurrency; here we use len(valid_urls)
    with ThreadPoolExecutor(max_workers=len(valid_urls)) as executor:
        future_to_url = {executor.submit(process_url, url): url for url in valid_urls}
        for future in as_completed(future_to_url):
            thr_results.append(future.result())
    end_thr = time.perf_counter()
    duration_thr = end_thr - start_thr
    print(f"\nThreaded run completed in {duration_thr:.2f} seconds.\n")
    
    # Summarize threaded results
    total_tables_thr = sum(r[1] for r in thr_results)
    total_files_thr  = sum(len(r[2]) for r in thr_results)
    print("Threaded Summary:")
    for url, num_tables, files in thr_results:
        print(f"  {url}: {num_tables} tables, {len(files)} CSV files")
    print(f"  → Total: {total_tables_thr} tables, {total_files_thr} files\n")
    
    # ---- Compare ----
    print("Performance Comparison:")
    print(f"  Sequential: {duration_seq:.2f}s")
    print(f"  Threaded:   {duration_thr:.2f}s")
    print("\nDone.")

if __name__ == "__main__":
    main()