FROM python:3.14.6-slim

# instala dependências de sistema (ajuste conforme sua necessidade, ex: build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# instala o Poetry
ENV POETRY_HOME=/opt/poetry
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# copia apenas os arquivos de dependência primeiro (cache de camadas)
COPY pyproject.toml poetry.lock ./

# instala dependências sem criar virtualenv (usa o Python do container direto)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# copia o restante do código
COPY . .

# garante que o pacote do projeto também seja instalado, se necessário
RUN poetry install --no-interaction --no-ansi