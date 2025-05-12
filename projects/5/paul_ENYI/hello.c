#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <emscripten.h>

EMSCRIPTEN_KEEPALIVE
char* make_greeting(const char* name, int age, int repeat_count) {
    if (repeat_count <= 0) repeat_count = 1;

    const char* template = "Hello, %s. You are %d years old.\n";
    int single_len = snprintf(NULL, 0, template, name, age);
    size_t total_size = single_len * repeat_count + 1;

    char* result = (char*)malloc(total_size);
    if (!result) return NULL;

    char* current = result;
    for (int i = 0; i < repeat_count; i++) {
        int written = sprintf(current, template, name, age);
        current += written;
    }

    return result;
}

EMSCRIPTEN_KEEPALIVE
void free_memory(char* ptr) {
    free(ptr);
}