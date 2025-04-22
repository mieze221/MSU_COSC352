#!/usr/bin/env python3
"""
HTML Table Parser

This script downloads a webpage from a provided URL and extracts all tables
found in the HTML content, converting them to lists of dictionaries.

Usage:
    python table_parser.py <url>

Example:
    python table_parser.py https://example.com/page-with-tables
"""

import sys
import urllib.request
import html.parser
import json


class HTMLTableParser(html.parser.HTMLParser):
    """
    HTML Parser that extracts tables from HTML content and converts them to
    lists of dictionaries.
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
        
    def handle_starttag(self, tag, attrs):
        """Handle start tags in HTML content."""
        if tag == 'table':
            self.in_table = True
            self.current_table = []
            self.headers = []
        elif tag == 'tr' and self.in_table:
            self.in_tr = True
            self.current_row = []
        elif tag == 'th' and self.in_tr:
            self.processing_th = True
            self.current_cell = []
        elif tag == 'td' and self.in_tr:
            self.processing_td = True
            self.current_cell = []
    
    def handle_endtag(self, tag):
        """Handle end tags in HTML content."""
        if tag == 'table':
            # If we have a complete table, add it to our tables list
            if self.current_table:
                # If we found headers, convert rows to dictionaries
                if self.headers:
                    dict_table = []
                    for row in self.current_table:
                        # For each row, create a dictionary mapping header -> value
                        # Make sure we don't go out of bounds if a row has fewer cells than headers
                        row_dict = {self.headers[i]: row[i] if i < len(row) else "" 
                                   for i in range(len(self.headers))}
                        dict_table.append(row_dict)
                    self.tables.append(dict_table)
                else:
                    # If no headers were found, store as a list of rows
                    self.tables.append(self.current_table)
            self.in_table = False
            self.current_table = None
            
        elif tag == 'tr':
            if self.current_row:
                if self.current_table is not None:
                    self.current_table.append(self.current_row)
            self.in_tr = False
            self.current_row = None
            
        elif tag == 'th':
            if self.current_cell:
                # Join cell content and clean whitespace
                cell_content = ''.join(self.current_cell).strip()
                self.headers.append(cell_content)
            self.processing_th = False
            self.current_cell = []
            
        elif tag == 'td':
            if self.current_cell and self.current_row is not None:
                # Join cell content and clean whitespace
                cell_content = ''.join(self.current_cell).strip()
                self.current_row.append(cell_content)
            self.processing_td = False
            self.current_cell = []
    
    def handle_data(self, data):
        """Handle text data within tags."""
        if self.processing_th or self.processing_td:
            self.current_cell.append(data)
    
    def get_tables(self):
        """Return all parsed tables."""
        return self.tables


def download_url(url):
    """
    Download the HTML content from the given URL.
    
    Args:
        url (str): The URL to download.
        
    Returns:
        str: The HTML content of the page.
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
        sys.exit(1)


def parse_tables(html_content):
    """
    Parse all tables from HTML content.
    
    Args:
        html_content (str): The HTML content to parse.
        
    Returns:
        list: A list of tables, where each table is a list of dictionaries.
    """
    parser = HTMLTableParser()
    parser.feed(html_content)
    return parser.get_tables()


def main():
    """Main function to handle command line arguments and process the URL."""
    # Check if URL is provided
    if len(sys.argv) != 2:
        print("Usage: python table_parser.py <url>", file=sys.stderr)
        sys.exit(1)
    
    url = sys.argv[1]
    print(f"Downloading and parsing tables from {url}...")
    
    # Download the URL content
    html_content = download_url(url)
    
    # Parse tables from HTML content
    tables = parse_tables(html_content)
    
    # Output the tables
    if not tables:
        print("No tables found on the page.")
    else:
        print(f"Found {len(tables)} tables on the page.")
        print(json.dumps(tables, indent=2))


if __name__ == "__main__":
    main()