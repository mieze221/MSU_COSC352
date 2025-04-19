package main

import (
	"encoding/csv"
	"fmt"
	"golang.org/x/net/html"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

// Configuration
const (
	outputDir = "output"
	dataDir   = "data"
)

// Source configuration: maps source (URL or file) to a short name for CSV naming
var sources = []struct {
	path   string
	name   string
	isURL  bool
}{
	{path: "https://en.wikipedia.org/wiki/List_of_largest_companies_in_the_United_States_by_revenue", name: "revenue_url1", isURL: true},
	{path: "https://en.wikipedia.org/wiki/List_of_largest_companies_by_revenue", name: "revenue_url2", isURL: true},
	{path: "page1.html", name: "revenue_file1", isURL: false},
	{path: "page2.html", name: "revenue_file2", isURL: false},
}

func ensureDirectories() error {
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		return fmt.Errorf("failed to create output directory: %v", err)
	}
	if err := os.MkdirAll(dataDir, 0755); err != nil {
		return fmt.Errorf("failed to create data directory: %v", err)
	}
	return nil
}

func readHTML(source string, isURL bool) (string, error) {
	if isURL {
		resp, err := http.Get(source)
		if err != nil {
			return "", fmt.Errorf("failed to fetch %s: %v", source, err)
		}
		defer resp.Body.Close()

		var sb strings.Builder
		_, err = sb.ReadFrom(resp.Body)
		if err != nil {
			return "", fmt.Errorf("failed to read response body from %s: %v", source, err)
		}
		return sb.String(), nil
	}

	filePath := filepath.Join(dataDir, source)
	file, err := os.Open(filePath)
	if err != nil {
		return "", fmt.Errorf("failed to open %s: %v", filePath, err)
	}
	defer file.Close()

	var sb strings.Builder
	_, err = sb.ReadFrom(file)
	if err != nil {
		return "", fmt.Errorf("failed to read %s: %v", filePath, err)
	}
	return sb.String(), nil
}

func extractTablesFromHTML(htmlContent string) ([][][]string, error) {
	var tables [][][]string
	tokenizer := html.NewTokenizer(strings.NewReader(htmlContent))

	var currentTable [][]string
	var currentRow []string
	var currentCell strings.Builder
	var inTable, inRow, inCell bool

	for {
		tt := tokenizer.Next()
		switch tt {
		case html.ErrorToken:
			if inTable && len(currentTable) > 0 {
				tables = append(tables, currentTable)
			}
			return tables, nil
		case html.StartTagToken, html.SelfClosingTagToken:
			token := tokenizer.Token()
			switch token.Data {
			case "table":
				currentTable = [][]string{}
				inTable = true
			case "tr":
				if inTable {
					currentRow = []string{}
					inRow = true
				}
			case "td", "th":
				if inRow {
					currentCell.Reset()
					inCell = true
				}
			}
		case html.TextToken:
			if inCell {
				currentCell.WriteString(strings.TrimSpace(tokenizer.Token().Data))
			}
		case html.EndTagToken:
			token := tokenizer.Token()
			switch token.Data {
			case "td", "th":
				if inCell {
					currentRow = append(currentRow, currentCell.String())
					inCell = false
				}
			case "tr":
				if inRow && len(currentRow) > 0 {
					currentTable = append(currentTable, currentRow)
					inRow = false
				}
			case "table":
				if inTable && len(currentTable) > 0 {
					tables = append(tables, currentTable)
					inTable = false
				}
			}
		}
	}
}

func writeToCSV(table [][]string, sourceName string, index int) error {
	filename := fmt.Sprintf("%s_table_%d.csv", sourceName, index+1)
	filepath := filepath.Join(outputDir, filename)

	file, err := os.Create(filepath)
	if err != nil {
		return fmt.Errorf("failed to create %s: %v", filename, err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	for _, row := range table {
		if err := writer.Write(row); err != nil {
			return fmt.Errorf("failed to write row to %s: %v", filename, err)
		}
	}
	return nil
}

func processSource(source string, sourceName string, isURL bool) error {
	htmlContent, err := readHTML(source, isURL)
	if err != nil {
		return err
	}

	tables, err := extractTablesFromHTML(htmlContent)
	if err != nil {
		return fmt.Errorf("failed to extract tables from %s: %v", source, err)
	}

	if len(tables) == 0 {
		fmt.Printf("No tables found in %s\n", source)
		return nil
	}

	for i, table := range tables {
		if err := writeToCSV(table, sourceName, i); err != nil {
			return err
		}
		fmt.Printf("Saved table %d from %s\n", i+1, source)
	}
	return nil
}

func sequentialExecution(sources []struct{ path, name string; isURL bool }) time.Duration {
	start := time.Now()
	for _, src := range sources {
		if err := processSource(src.path, src.name, src.isURL); err != nil {
			fmt.Printf("Error processing %s: %v\n", src.path, err)
		}
	}
	return time.Since(start)
}

func multithreadedExecution(sources []struct{ path, name string; isURL bool }) time.Duration {
	start := time.Now()
	var wg sync.WaitGroup
	errorCh := make(chan error, len(sources))

	for _, src := range sources {
		wg.Add(1)
		go func(path, name string, isURL bool) {
			defer wg.Done()
			if err := processSource(path, name, isURL); err != nil {
				errorCh <- fmt.Errorf("error processing %s: %v", path, err)
			}
		}(src.path, src.name, src.isURL)
	}

	wg.Wait()
	close(errorCh)

	for err := range errorCh {
		fmt.Println(err)
	}

	return time.Since(start)
}

func main() {
	if err := ensureDirectories(); err != nil {
		fmt.Printf("Error creating directories: %v\n", err)
		return
	}

	fmt.Println("Starting Sequential Execution...")
	seqTime := sequentialExecution(sources)
	fmt.Printf("Sequential Execution Time: %.2f seconds\n\n", seqTime.Seconds())

	fmt.Println("Starting Multithreaded Execution...")
	mtTime := multithreadedExecution(sources)
	fmt.Printf("Multithreaded Execution Time: %.2f seconds\n", mtTime.Seconds())
