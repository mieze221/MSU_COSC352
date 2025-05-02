#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <emscripten/emscripten.h>

char* EMSCRIPTEN_KEEPALIVE greet(const char* name, int age, int count) {
    const char* format = "Hello, %s. You are %d years old.\n";
    int single_len = snprintf(NULL, 0, format, name, age);
    int total_len = (single_len * count) + 1;

    char* result = malloc(total_len);
    if (!result) return NULL;
    result[0] = '\0';

    for (int i = 0; i < count; i++) {
        snprintf(result + strlen(result), total_len - strlen(result), format, name, age);
    }

    return result;
}

void EMSCRIPTEN_KEEPALIVE free_buffer(char* buffer) {
    free(buffer);
}
