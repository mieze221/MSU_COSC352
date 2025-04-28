import pandas as pd
import time
import os
from concurrent.futures import ThreadPoolExecutor
from io import StringIO

def extract_and_save_tables(html_file, source_name):
    # Read HTML content from the file
    with open(html_file, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Use StringIO to handle the HTML as a file-like object
    dfs = pd.read_html(StringIO(html_content))  # Read all tables in the HTML file

    for i, df in enumerate(dfs):
        # Create a filename based on the source name and table index
        csv_filename = f"{source_name}_table_{i+1}.csv"
        df.to_csv(csv_filename, index=False)
        print(f"Saved {csv_filename}")

def process_html_files_sequential(html_files):
    for html_file in html_files:
        source_name = os.path.splitext(os.path.basename(html_file))[0]  # Extract file name without extension
        print(f"Processing {source_name}...")
        extract_and_save_tables(html_file, source_name)

def process_html_files_multithreaded(html_files):
    with ThreadPoolExecutor() as executor:
        executor.map(extract_and_save_tables, html_files, [os.path.splitext(os.path.basename(file))[0] for file in html_files])

def sequential_execution(html_files):
    start_time = time.time()  # Start the timer
    process_html_files_sequential(html_files)
    end_time = time.time()  # End the timer
    return end_time - start_time

def multithreaded_execution(html_files):
    start_time = time.time()  # Start the timer
    process_html_files_multithreaded(html_files)
    end_time = time.time()  # End the timer
    return end_time - start_time

def main():
    html_files = ["data/page1.html", "data/page2.html"]  # Replace with actual HTML file paths
    print("Starting Sequential Execution...")
    seq_time = sequential_execution(html_files)
    print(f"Sequential Execution Time: {seq_time:.2f} seconds")

    print("\nStarting Multithreaded Execution...")
    mt_time = multithreaded_execution(html_files)
    print(f"Multithreaded Execution Time: {mt_time:.2f} seconds")

if __name__ == "__main__":
    main()
