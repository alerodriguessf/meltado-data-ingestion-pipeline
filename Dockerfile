FROM python:3.11-slim-buster

WORKDIR /app

# Instala dependências de sistema, incluindo ODBC e o driver SQL Server
RUN apt-get update && \
    apt-get install -y gnupg2 curl ca-certificates apt-transport-https software-properties-common && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev gcc g++ git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia o arquivo requirements
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Instala os plugins Meltano
RUN meltano install

CMD ["bash"]
