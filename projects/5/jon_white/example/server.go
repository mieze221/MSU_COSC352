package main

import (
	"flag"
	"log"
	"net/http"
)

func main() {
	// Define a port flag with default value 8080
	port := flag.String("port", "8080", "port to serve on")
	flag.Parse()

	// Configure the file server to serve static files
	fs := http.FileServer(http.Dir("./"))
	
	// Set the correct MIME type for WebAssembly files
	http.HandleFunc("/main.wasm", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/wasm")
		http.ServeFile(w, r, "./main.wasm")
	})
	
	// Handle all other requests with the file server
	http.Handle("/", fs)

	log.Printf("Starting server on :%s...\n", *port)
	err := http.ListenAndServe(":"+*port, nil)
	if err != nil {
		log.Fatal(err)
	}
}
