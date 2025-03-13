# Import necessary modules
using Downloads
using DelimitedFiles

# Step 1: Download the HTML file
url = "https://en.wikipedia.org/wiki/List_of_largest_companies_in_the_United_States_by_revenue"
html_file = "page.html"
Downloads.download(url, html_file)
println("Downloaded HTML file.")

# Step 2: Read HTML content
html_content = read(html_file, String)

# Step 3: Extract table data (very basic string parsing approach)
tables = []
table_start = "<table"
table_end = "</table>"

start_idx = findnext(table_start, html_content, 1)
while start_idx !== nothing
    end_idx = findnext(table_end, html_content, start_idx + length(table_start) - 1)
    if end_idx === nothing
        break
    end
    push!(tables, html_content[start_idx:end_idx + length(table_end) - 1])
    start_idx = findnext(table_start, html_content, end_idx + length(table_end) - 1)
end

# Step 4: Save extracted tables into CSV files
for (i, table) in enumerate(tables)
    csv_file = "table_$(i).csv"
    open(csv_file, "w") do f
        # Basic conversion: Remove HTML tags and replace with commas
        table_clean = replace(table, r"<[^>]*>" => ",")
        table_clean = replace(table_clean, r",+" => ",")  # Remove extra commas
        write(f, table_clean)  # Use write instead of println
    end
    println("Saved table to: ", csv_file)
end

println("Extraction complete! CSV files created.")