
defmodule MyApp do
  def run do
    urls = ["data/page1.html"] # Add more files as needed

    IO.puts("Running sequential execution...")
    {time1, _} = :timer.tc(fn -> run_sequential(urls) end)
    IO.puts("Sequential execution time: #{time1 / 1_000_000}s")

    IO.puts("\nRunning parallel execution...")
    {time2, _} = :timer.tc(fn -> run_parallel(urls) end)
    IO.puts("Parallel execution time: #{time2 / 1_000_000}s")
  end

  def run_sequential(urls) do
    File.mkdir_p!("output")

    Enum.each(urls, fn url ->
      IO.puts("Processing #{url}")
      html = File.read!(url)
      tables = extract_tables(html)

      Enum.with_index(tables, fn table, idx ->
        base = Path.basename(url, ".html")
        filename = "output/#{base}_table_#{idx + 1}.csv"
        export_to_csv(table, filename)
        IO.puts("Exported to #{filename}")
      end)
    end)
  end

  def run_parallel(urls) do
    File.mkdir_p!("output")

    urls
    |> Enum.map(fn url ->
      Task.async(fn ->
        IO.puts("Processing #{url}")
        html = File.read!(url)
        tables = extract_tables(html)

        Enum.with_index(tables, fn table, idx ->
          base = Path.basename(url, ".html")
          filename = "output/#{base}_table_#{idx + 1}.csv"
          export_to_csv(table, filename)
          IO.puts("Exported to #{filename}")
        end)
      end)
    end)
    |> Enum.each(&Task.await/1)
  end

  def extract_tables(html) do
    Regex.scan(~r/<table.*?<\/table>/s, html)
    |> Enum.map(fn [table_html] ->
      Regex.scan(~r/<tr.*?<\/tr>/s, table_html)
      |> Enum.map(fn match ->
        row_html = List.first(match)
        Regex.scan(~r/<(?:td|th).*?>(.*?)<\/(?:td|th)>/s, row_html)
        |> Enum.map(fn [_, cell] -> clean(cell) end)
      end)
    end)
  end

  def export_to_csv(table, filename) do
    content =
      table
      |> Enum.map(&Enum.join(&1, ","))
      |> Enum.join("\n")

    File.write!(filename, content)
  end

  defp clean(text) do
    text
    |> String.replace(~r/<.*?>/, "")   # Remove HTML tags
    |> String.replace(~r/\s+/, " ")    # Collapse whitespace
    |> String.trim()
  end
end

MyApp.run()
