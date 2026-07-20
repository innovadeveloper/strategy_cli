#include <stdio.h>

#ifdef _WIN32
    #define MILIB_API __declspec(dllexport)
#else
    #define MILIB_API
#endif

MILIB_API int suma(int a, int b) {
    return a + b;
}

MILIB_API const char* version() {
    return "MiLib v1.0";
}

// gcc -shared -fPIC -o libmilib.dylib milib.c -lm

// # Verificar que se creó
// file libmilib.dylib
// # Output: libmilib.dylib: Mach-O 64-bit dynamically linked shared library x86_64