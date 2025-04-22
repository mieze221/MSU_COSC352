
# List of HTML URLs and filenames
files = [
    ("https://en.wikipedia.org/wiki/List_of_largest_companies_in_the_United_States_by_revenue", "page1.html"),
    ("https://en.wikipedia.org/wiki/List_of_largest_employers", "page2.html")
]

function download_files(files)
    for (url, filename) in files
        run(`curl -s -o $filename $url`)
        println("Downloaded: $filename")
    end
end

function extract_tables_from_file(filename)
    html_content = read(filename, String)
    tables = []
    start_pos = 1
    table_start = "<table"
    table_end = "</table>"

    while true
        start_idx = findnext(table_start, html_content, start_pos)
        if start_idx === nothing
            break
        end
        start_int = first(start_idx)
        end_idx = findnext(table_end, html_content, start_int + length(table_start))
        if end_idx === nothing
            break
        end
        end_int = last(end_idx) + length(table_end) - 1
        push!(tables, html_content[start_int:end_int])
        start_pos = end_int + 1
    end

    for (i, table) in enumerate(tables)
        csv_file = filename * "_table_$(i).csv"
        open(csv_file, "w") do f
            table_clean = replace(table, r"<[^>]*>" => ",")
            table_clean = replace(table_clean, r",+" => ",")  
            write(f, table_clean)
        end
        println("Saved to: $csv_file")
    end
end

function sequential_mode(filepaths)
    start_time = time()
    for (_, file) in filepaths
        extract_tables_from_file(file)
    end
    println("Sequential execution time: ", round(time() - start_time, digits=3), " seconds")
end

function multithreaded_mode(filepaths)
    start_time = time()
    tasks = []
    for (_, file) in filepaths
        push!(tasks, Threads.@spawn extract_tables_from_file(file))
    end
    for task in tasks
        wait(task)
    end
    println("Multithreaded execution time: ", round(time() - start_time, digits=3), " seconds")
end


# RUN
mode = get(ARGS, 1, "sequential")  
download_files(files)

if mode == "multi"
    println("Running in multithreaded mode")
    multithreaded_mode(files)
else
    println("Running in sequential mode")
    sequential_mode(files)
end