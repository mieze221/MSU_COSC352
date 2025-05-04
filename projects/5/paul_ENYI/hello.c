#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <emscripten.h>

EMSCRIPTEN_KEEPALIVE
char* greet(const char* name, int age, int repeat_count) {
    if (repeat_count <= 0) repeat_count = 1;
    
    char single_greeting[256];
    int greeting_len = snprintf(single_greeting, sizeof(single_greeting), 
                               "Hello %s, you are %d years old!", name, age);
    
    size_t total_size = (greeting_len + 1) * repeat_count + 1; 
    char* result = (char*)malloc(total_size);
    if (!result) return NULL;
    
    result[0] = '\0';
    
    char* current_pos = result;
    for (int i = 0; i < repeat_count; i++) {
        strcpy(current_pos, single_greeting);
        current_pos += greeting_len;
        
        if (i < repeat_count - 1) {
            *current_pos = '\n';
            current_pos++;
        }
    }
    
    *current_pos = '\0';
    
    return result;
}

EMSCRIPTEN_KEEPALIVE
void free_buffer(char* ptr) {
    free(ptr);
}

int main() {
    printf("WASM module initialized\n");
    return 0;
}