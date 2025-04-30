#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <emscripten.h>

// Exported function
EMSCRIPTEN_KEEPALIVE
char* make_greeting(const char* name, int age, int repeat_count) {
    if (repeat_count <= 0) repeat_count = 1;

    const char* template = "Hello, %s. You are %d years old.\n";
    size_t template_size = strlen(template) + strlen(name) + 20; // Extra for age and formatting

    size_t total_size = template_size * repeat_count + 1;
    char* result = (char*) malloc(total_size);

    if (!result) {
        return NULL; // allocation failed
    }

    result[0] = '\0'; // Start empty string

    for (int i = 0; i < repeat_count; i++) {
        char buffer[256];
        snprintf(buffer, sizeof(buffer), template, name, age);
        strcat(result, buffer);
    }

    return result;
}

// Also export a free function to allow JS to free memory
EMSCRIPTEN_KEEPALIVE
void free_memory(char* ptr) {
    free(ptr);
}
