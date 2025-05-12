let wasmModule;

function moduleReady(module) {
  console.log("WebAssembly module initialized");
  wasmModule = module;
  setupForm();

  document.getElementById("output").innerHTML = "WebAssembly module loaded successfully! Fill out the form and click 'Generate Greeting'.";
}

function initWasm() {
  if (typeof Module !== 'undefined' && Module.ready) {
    moduleReady(Module);
  } else {
    window.Module = window.Module || {};
    const originalOnRuntimeInitialized = window.Module.onRuntimeInitialized;

    window.Module.onRuntimeInitialized = function() {
      if (typeof originalOnRuntimeInitialized === 'function') {
        originalOnRuntimeInitialized();
      }

      moduleReady(window.Module);
    };
  }
}

function setupForm() {
  const form = document.getElementById("input-form");

  form.addEventListener("submit", function(event) {
    event.preventDefault();

    const name = document.getElementById("name-input").value;
    const age = parseInt(document.getElementById("age-input").value, 10);
    const repeat = parseInt(document.getElementById("repeat-input").value, 10) || 1;

    const makeGreeting = wasmModule.cwrap('make_greeting', 'number', ['string', 'number', 'number']);
    const freeMemory = wasmModule.cwrap('free_memory', null, ['number']);

    const resultPtr = makeGreeting(name, age, repeat);

    const resultMessage = wasmModule.UTF8ToString(resultPtr);

    document.getElementById("output").innerHTML = `<pre>${resultMessage}</pre>`;  

    freeMemory(resultPtr);
  });
}

window.addEventListener("DOMContentLoaded", initWasm);