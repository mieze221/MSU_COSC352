#!/usr/bin/env python3
"""
Wikipedia Table Parser

This script downloads a Wikipedia page from a provided URL and extracts all tables
found in the HTML content, converting them to lists of dictionaries. It's optimized
for parsing Wikipedia tables including handling of complex formatting elements.

Usage:
    python wiki_table_parser.py <url>

Example:
    python wiki_table_parser.py https://en.wikipedia.org/wiki/List_of_largest_companies_by_revenue
"""

import sys
import re
import urllib.request
import html.parser
import json


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
    parser = WikiTableParser()
    parser.feed(html_content)
    return parser.get_tables()


def main():
    """Main function to handle command line arguments and process the URL."""
    # Check if URL is provided
    if len(sys.argv) != 2:
        print("Usage: python wiki_table_parser.py <url>", file=sys.stderr)
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