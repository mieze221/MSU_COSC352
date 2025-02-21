require "http/client"
require "csv"
require "io"
require "colorize"

# Create the directory if it doesn't exist
Dir.mkdir("extract_tables") unless Dir.exists?("extract_tables")

url : String = "https://en.wikipedia.org/wiki/List_of_largest_companies_in_the_United_States_by_revenue"
response : HTTP::Client::Response = HTTP::Client.get(url)
html_content : String = response.body.to_s # to_s means convert to string

puts "Downloaded HTML content from #{url}.".colorize.green
puts "HTML content size: #{html_content.size} bytes.".colorize.blue

# make the html content into tables
tables = html_content.split("<table")[1..-1].map { |table|  # skip the first element, took forever to figure out lol
  table.split("</table>").first  
}

puts "Found #{tables.size} tables.".colorize.yellow

# go through each table and extract the rows 
tables.each_with_index do |table, index|
  rows = table.split("<tr>")[1..-1].map { |row|  # skip the first row (header)
    row.split("<td>")[1..-1].map { |cell|  # skip the first column (header)
      cell.split("</td>").first.strip.gsub(/<[^>]+>/, "") # remove HTML tags
    }
  }
  puts "Table #{index + 1} has #{rows.size} rows.".colorize.magenta

  # build and save the rows to CSV  to the extract_tables folder
  file_name = "extract_tables/table_#{index + 1}.csv"
  File.open(file_name, "w") do |file|
    CSV.build(file) do |csv|
      rows.each do |row|
        csv.row(row)  # correct way to write a row to CSV in Crystal, i was using csv << row and it wasn't working for some reason
      end
    end
  end
end

puts "Done!".colorize.green