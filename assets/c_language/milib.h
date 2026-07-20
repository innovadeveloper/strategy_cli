#ifndef MILIB_H
#define MILIB_H

#ifdef _WIN32
    #ifdef MILIB_EXPORTS
        #define MILIB_API __declspec(dllexport)
    #else
        #define MILIB_API __declspec(dllimport)
    #endif
#else
    #define MILIB_API __attribute__((visibility("default")))
#endif

#include <stddef.h>

// Operaciones básicas
MILIB_API int suma(int a, int b);
MILIB_API int resta(int a, int b);
MILIB_API int multiplicacion(int a, int b);
MILIB_API double division(int a, int b);

// Operaciones con arrays
MILIB_API double promedio(double* arr, int len);
MILIB_API double desviacion_estandar(double* arr, int len);
MILIB_API void ordenar_array(double* arr, int len);

// Manipulación de strings
MILIB_API char* concatenar(const char* str1, const char* str2);
MILIB_API void liberar_string(char* str);

// Función de versión
MILIB_API const char* obtener_version();

#endif