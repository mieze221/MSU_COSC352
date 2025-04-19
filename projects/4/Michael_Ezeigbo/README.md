# Project 4: Multi-URL HTML Table Extractor

## Overview
This project implements a Go program that extracts tables from multiple HTML sources (URLs or local files) and saves them as CSV files. It supports two execution modes:
- **Sequential**: Processes each source one at a time.
- **Multithreaded**: Processes all sources concurrently using goroutines.

The program measures and reports the execution time for both modes and handles errors gracefully (e.g., network issues, file not found, malformed HTML).

## Directory Structure
Projects/4/<michael>_<ezeigbo>/
├── Dockerfile
├── extract_tables.go
├── README.md
├── data/
│   ├── page1.html
│   ├── page2.html
├── go.mod
├── go.sum
