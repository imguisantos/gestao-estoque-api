FROM python:3.12-slim

WORKDIR /code

# Dependências de sistema necessárias para compilar bcrypt/cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# --reload é útil em desenvolvimento; considere removê-lo em produção.
# Usamos shell form (sem colchetes) para que ${PORT:-8000} seja expandido:
# plataformas como Railway/Render injetam a variável PORT dinamicamente.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
