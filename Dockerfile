FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry

# 1. Copia solo los archivos de dependencias primero (Optimización de caché)
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# 2. Copia el resto del código
COPY . .


EXPOSE 8000

# Usa la ruta absoluta para evitar fallos de PATH o permisos de directorio
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]