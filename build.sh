#!/bin/bash

# Script para compilar ulearn5.theme
echo "Compilando ulearn5.theme..."

# Ejecutar tareas de compass
echo "Compilando Sass..."
grunt compass

# Ejecutar concatenación
echo "Concatenando archivos..."
grunt concat

# Ejecutar minificación CSS
echo "Minificando CSS..."
grunt cssmin

# Ejecutar minificación JavaScript
echo "Minificando JavaScript..."
grunt uglify

echo "Compilación completada!"