#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* create_greeting(const char* name, int age, int repeat_count) {
    const char* template = "Hello, %s. You are %d years old.\n";
    int line_length = snprintf(NULL, 0, template, name, age);
    int total_length = (line_length * repeat_count) + 1;

    char* result = (char*)malloc(total_length);
    result[0] = '\0';

    for (int i = 0; i < repeat_count; i++) {
        char line[line_length + 1];
        snprintf(line, sizeof(line), template, name, age);
        strcat(result, line);
    }

    return result;
}

void free_result(char* ptr) {
    free(ptr);
}