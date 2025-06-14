# Usa a imagem oficial do Meltano com Python 3.11
FROM meltano/meltano:latest-python3.11

# Instala pacotes necessários: curl, unzip (para CLI Databricks)
RUN apt-get update && apt-get install -y curl unzip && \
    rm -rf /var/lib/apt/lists/*

# Instala a Databricks CLI (v2)
RUN curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

# Define o diretório de trabalho no container
WORKDIR /projects/adventure_works_ingestion

# Copia os arquivos necessários para dentro da imagem
COPY .env .env
COPY meltano.yml meltano.yml
COPY requirements.txt requirements.txt
COPY entrypoint.sh entrypoint.sh

# Dá permissão de execução ao script
RUN chmod +x entrypoint.sh

# Instala dependências Python do projeto (caso precise)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt || true

# Resolve dependências e instala os plugins do meltano
RUN meltano lock --update --all && \
    meltano install

# Define o script principal que será executado
ENTRYPOINT ["./entrypoint.sh"]
