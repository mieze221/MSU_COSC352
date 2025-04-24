package main

import (
	"fmt"
	"syscall/js"
)

func main() {
	// Create a channel to prevent the program from exiting
	c := make(chan struct{}, 0)
	
	// Register the sayHello function in JavaScript
	js.Global().Set("sayHello", js.FuncOf(sayHello))
	
	fmt.Println("Go WebAssembly Initialized")
	
	// Wait forever
	<-c
}

// sayHello is our exported function that can be called from JavaScript
func sayHello(this js.Value, args []js.Value) interface{} {
	name := "World"
	
	// If a name was passed, use it
	if len(args) > 0 && args[0].Type() == js.TypeString {
		name = args[0].String()
	}
	
	message := fmt.Sprintf("Hello, %s from Go WebAssembly!", name)
	
	// Update a DOM element with the message
	document := js.Global().Get("document")
	element := document.Call("getElementById", "output")
	element.Set("textContent", message)
	
	// Also print to the console
	js.Global().Get("console").Call("log", message)
	
	return nil
}
