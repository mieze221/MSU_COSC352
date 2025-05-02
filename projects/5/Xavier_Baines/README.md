# 🎉 Interactive Hello World with WebAssembly (WASM)

## ✨ Overview

This project demonstrates an interactive WebAssembly module written in C and compiled via Emscripten. It accepts a user's **name**, **age**, and a **repeat count**, and returns a formatted message repeated `N` times.

### Example Output:
```
Hello, Xavier. You are 22 years old.
Hello, Xavier. You are 22 years old.
Hello, Xavier. You are 22 years old.
```

---

## 📁 File Structure

```
Xavier_Baines/
├── hello.c          # WebAssembly source (C)
├── hello.js         # Compiled JS glue code from Emscripten
├── hello.wasm       # Compiled WebAssembly binary
├── index.html       # Web UI with input form
```

---

## 🚀 How to Run the Project

1. **Navigate to the project directory:**
```bash
cd Xavier_Baines
```

2. **Start a local HTTP server:**
```bash
python3 -m http.server 8080
```

3. **Open your browser and go to:**
```
http://localhost:8080
```

---

## 🧪 How It Works

- `index.html` renders a form for user input.
- When the form is submitted:
  - JavaScript calls a C function (`greet`) compiled into WebAssembly.
  - The C function returns a dynamically allocated string.
  - JavaScript converts the result from WASM memory into readable text.
  - The message is repeated `N` times and displayed in the browser.

---

## 🧠 Technologies Used

- **C** – Core logic
- **Emscripten** – Compiles C to WebAssembly
- **HTML/JavaScript** – Front-end and runtime integration
- **WebAssembly (WASM)** – High-performance execution in the browser

---

## 🙌 Author

**Xavier Baines**  
Project 5 – COSC352  
Morgan State University

