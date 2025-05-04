const readline = require('readline');
const Module = require('./hello.js');

Module.onRuntimeInitialized = () => {
  startCli(Module);
};

function startCli(module) {
  const greet      = module.cwrap('greet',      'number', ['string','number','number']);
  const freeBuffer = module.cwrap('free_buffer', null,     ['number']);

  const rl = readline.createInterface({
    input:  process.stdin,
    output: process.stdout
  });

  console.log('\nInteractive Hello with WASM');
  console.log('---------------------------');

  rl.question('Enter your name: ', name => {
    rl.question('Enter your age: ', ageStr => {
      rl.question('Enter repeat count: ', repeatStr => {
        const age    = parseInt(ageStr,    10) || 0;
        const repeat = parseInt(repeatStr, 10) || 1;

        const ptr     = greet(name, age, repeat);
        const message = module.UTF8ToString(ptr);

        console.log('\nResult from WASM:\n');
        console.log(message, '\n');

        freeBuffer(ptr);
        rl.close();
      });
    });
  });
}
