#!/bin/bash

# 1. 'set -e' hace que el script se detenga si cualquier comando falla.
# Es vital para no arrancar la app si, por ejemplo, las migraciones fallan.
set -e

echo "--- Iniciando tareas de preparación ---"
# 3. Comando: Ejecutar migraciones de base de datos
echo "Aplicando migraciones..."
python manage.py makemigrations web
python manage.py migrate

# 4. Comando: Recolectar archivos estáticos
echo "Recolectando estáticos..."
python manage.py collectstatic --noinput

# 5. Comando: Limpiar caché (si fuera necesario)
# redis-cli flushall 
python manage.py importar_juegos_igbd
echo "--- Preparación finalizada. Arrancando servidor ---"

# 6. 'exec "$@"' reemplaza el script por el comando definido en el CMD del Dockerfile.
exec "$@"