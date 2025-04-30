let wasmModule = null;

const loadWasm = async () => {
    wasmModule = await Module(); // Module from hello.js
};

loadWasm();

document.getElementById('helloForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    const name = document.getElementById('name').value.trim();
    const age = parseInt(document.getElementById('age').value, 10);
    const repeat = parseInt(document.getElementById('repeat').value, 10);

    if (!wasmModule) {
        alert('WASM module is not loaded yet.');
        return;
    }

    // Allocate memory for the name string
    const namePtr = wasmModule._malloc(name.length + 1);
    wasmModule.stringToUTF8(name, namePtr, name.length + 1);

    // Call the wasm function
    const resultPtr = wasmModule._make_greeting(namePtr, age, repeat);

    // Get the string back
    const result = wasmModule.UTF8ToString(resultPtr);

    // Display result
    document.getElementById('output').textContent = result;

    // Clean up memory
    wasmModule._free(namePtr);
    wasmModule._free_memory(resultPtr);
});
