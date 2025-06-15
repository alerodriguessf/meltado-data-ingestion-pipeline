

# 🚀 Pipeline de Ingestão de Dados - Lighthouse Checkpoint 2

## 1. Visão Geral do Projeto

Este projeto implementa uma pipeline de ingestão de dados robusta e eficiente, desenvolvida como parte do desafio **Lighthouse Checkpoint 2** da Indicium.

O objetivo principal é extrair dados de duas fontes distintas — um banco de dados relacional (**MSSQL**) e uma **API REST** — e carregá-los em um ambiente **Databricks Lakehouse**, utilizando o formato **Delta Lake** para garantir otimização, escalabilidade e conformidade com boas práticas de engenharia de dados.

A solução foi projetada com foco em **modularidade**, **reutilização**, **clareza** e **manutenibilidade do código**, seguindo princípios sólidos de engenharia de dados, como:

* Gerenciamento seguro de credenciais
* Garantia de idempotência na execução da pipeline

---

## 2. Arquitetura da Solução

A orquestração da pipeline é feita com **Meltano**, uma plataforma ELT open-source, conteinerizada com **Docker** para garantir consistência de ambiente. Os dados extraídos são temporariamente salvos em arquivos `.parquet` antes de serem carregados no **Databricks**.

### 2.1 Componentes Técnicos

#### 🔧 Meltano (Extração de dados):

* **tap-mssql**: Extrator que se conecta ao banco MSSQL
* **tap-rest-api-msdk**: Extrator para API REST, com paginação por offset e limit

  * `SalesOrderHeader`
  * `SalesOrderDetail`
  * `PurchaseOrderHeader`
  * `PurchaseOrderDetail`
* **target-parquet**: Loader que salva os dados em arquivos `.parquet`, organizados por fonte:

  * `target-parquet-sqlserver`
  * `target-parquet-api`

#### 🐳 Docker:

* Utilizado para conteinerizar o ambiente Meltano e todas as dependências (Databricks CLI, Python, bibliotecas nativas)
* Imagem base: `meltano/meltano:latest-python3.11`

#### ☁️ Databricks Lakehouse (Delta Lake):

* **Destino final** dos dados, com suporte a:

  * Transações ACID
  * Controle de schema (enforcement & evolution)
  * Performance otimizada
  * Escalabilidade horizontal

---

## 3. Requisitos e Pré-requisitos

Para executar o projeto localmente, é necessário:

* Docker Desktop (v4.x+) ou Docker Engine
* Git
* Acesso ao Databricks (workspace URL e PAT)
* Acesso ao banco MSSQL
* Acesso à API REST

---

## 4. Configuração do Ambiente Local

### 4.1 Clonar o Repositório

```bash
git clone <https://github.com/alerodriguessf/lighthouse_desafio02_alexandrersf>

```

### 4.2 Variáveis de Ambiente

Crie um arquivo `.env` com base nas suas credenciais

```bash
# MSSQL
TAP_MSSQL_HOST=your_mssql_host
TAP_MSSQL_PORT=your_mssql_port
TAP_MSSQL_USER=your_mssql_user
TAP_MSSQL_PASSWORD=your_mssql_password
TAP_MSSQL_DATABASE=your_mssql_database

# API
API_HOST=your_api_base_url
API_USER=your_api_username
API_PASSWORD=your_api_password

# Databricks
DATABRICKS_HOST=your_databricks_workspace_url
DATABRICKS_TOKEN=your_databricks_token
```

> ⚠️ Nunca faça commit de credenciais ou tokens.

---

## 5. Estrutura do Projeto

```
.
├── extract/                            # Extração de dados via Meltano
├── load/                               # Load de dados via Meltano
├── plugins/                            # Plugins Meltano (tap/target)
├── scripts_aux/                        # Scripts auxiliares (discovery e Delta conversion)
│   ├── discovery_api_aw_checkpoint2.ipynb
│   ├── delta conversion_api_checkpoint2_alexandrersf (1).ipynb
│   └── delta conversion_sqlserver_checkpoint2_alexandrersf.ipynb
├── .dockerignore
├── .env.save
├── .gitignore
├── Dockerfile
├── README.md
├── entrypoint.sh
├── meltano.yml
└── requirements.txt
```

---

## 6. Execução da Pipeline

### 6.1 Construir a Imagem Docker

```bash
docker build -t lighthouse-ingestion-pipeline .
```

### 6.2 Executar o Contêiner

```bash
docker run \
  --env-file .env \
  lighthouse-ingestion-pipeline
```

> O script `entrypoint.sh` será executado automaticamente.

### 6.2.1 O que o entrypoint.sh faz:

1. Executa o pipeline com Meltano:

```bash
meltano run tap-mssql target-parquet-sqlserver tap-rest-api-msdk target-parquet-api
```

2. Realiza o upload dos arquivos Parquet para o Databricks:

```bash
databricks fs cp output/docker_elt/sqlserver/ dbfs:/<caminho>/sqlserver/ --recursive --overwrite
databricks fs cp output/docker_elt/api/ dbfs:/<caminho>/api/ --recursive --overwrite
```

> Ajuste os caminhos conforme sua estrutura (`DBFS` ou `Unity Catalog`).

---

## 7. Validação

* Acesse o seu workspace no **Databricks**
* Valide a existência dos arquivos Parquet
* Execute os notebooks de conversão de Parquet para Delta
* Verifique as tabelas criadas com o prefixo:

  * `raw_api_<nome>_db`
  * `raw_sqlserver_<nome>_db`

---

## 8. Scripts Auxiliares (`scripts_aux/`)

Além da pipeline Meltano, o repositório conta com **scripts auxiliares** importantes para testes e ingestão manual.

### 📂 Conteúdo da Pasta

```
scripts_aux/
├── discovery_api_aw_checkpoint2.ipynb                  # Testa endpoints da API REST
├── delta conversion_api_checkpoint2_alexandrersf (1).ipynb     # Cria tabelas Delta a partir dos dados da API
└── delta conversion_sqlserver_checkpoint2_alexandrersf.ipynb   # Cria tabelas Delta a partir dos dados SQL Server
```

### 🧪 Utilização

* `discovery_api_aw_checkpoint2.ipynb`: Garante que os endpoints da API estão respondendo corretamente
* `delta conversion_api_checkpoint2_alexandrersf (1).ipynb`: Busca os arquivos `.parquet` da API e os converte em tabelas Delta individuais
* `delta conversion_sqlserver_checkpoint2_alexandrersf.ipynb`: Idem ao anterior, mas para arquivos extraídos do SQL Server

> ✅ Os nomes das tabelas seguem o padrão: `raw_<fonte>_<nome>_db`, garantindo organização e rastreabilidade.

---

## 9. Contato

**Nome da equipe:** Alexandre R.Silva Filho

**Email:** [alexandre.filho@indicium.tech](mailto:alexandre.filho@indicium.tech)
