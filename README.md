

# 🚀 Pipeline de Ingestão de Dados - Lighthouse Checkpoint 2

## 1. Visão Geral do Projeto

Este projeto implementa uma pipeline de ingestão de dados robusta e eficiente, desenvolvida como parte do desafio Lighthouse Checkpoint 2 da Indicium.  
O objetivo principal é extrair dados de duas fontes distintas — um banco de dados relacional (MSSQL) e uma API REST — e carregá-los em um ambiente Databricks Lakehouse, utilizando o formato Delta Lake para garantir otimização, escalabilidade e conformidade com boas práticas de engenharia de dados.

A solução foi projetada com foco em modularidade, reutilização, clareza e manutenibilidade do código. Segue princípios sólidos de engenharia de dados, como:

- Gerenciamento seguro de credenciais
- Tratamento abrangente de erros
- Garantia de idempotência na execução da pipeline

---

## 2. Arquitetura da Solução

A orquestração da pipeline é feita com **Meltano**, uma plataforma ELT open-source, conteinerizada com **Docker** para garantir consistência de ambiente. Os dados extraídos são temporariamente salvos em arquivos Parquet antes de serem carregados no Databricks como tabelas Delta Lake.

### 2.1. Componentes Técnicos

- **Meltano (Orquestrador ELT):**
  - `tap-mssql`: Extrator que se conecta ao banco MSSQL.
  - `tap-rest-api-msdk`: Extrator para API REST, com paginação `offset` e `limit`. Streams:
    - `SalesOrderHeader`
    - `SalesOrderDetail`
    - `PurchaseOrderHeader`
    - `PurchaseOrderDetail`
  - `target-parquet`: Loader que salva os dados em arquivos `.parquet` organizados por fonte:
    - `target-parquet-sqlserver`
    - `target-parquet-api`

- **Docker:** Utilizado para conteinerizar o ambiente Meltano e todas as dependências (Databricks CLI, Python, pacotes de sistema). O `Dockerfile` é baseado na imagem `meltano/meltano:latest-python3.11`.

- **Databricks CLI (v2):** Responsável pelo upload dos arquivos Parquet para o Lakehouse (via DBFS ou Unity Catalog).

- **Databricks Lakehouse (Delta Lake):** Destino final dos dados. Vantagens:
  - Transações ACID
  - Controle de schema (enforcement & evolution)
  - Performance otimizada para análise
  - Alta escalabilidade

---

## 3. Requisitos e Pré-requisitos

Para executar este projeto, você precisará de:

- **Docker Desktop** (4.x+) ou **Docker Engine**
- **Git**
- **Acesso ao Databricks:**
  - URL do workspace
  - Personal Access Token (PAT)
- **Acesso ao banco MSSQL:**
  - Host, porta, usuário, senha e nome do banco
- **Acesso à API:**
  - URL base, usuário e senha (basic auth)

---

## 4. Configuração do Ambiente Local

### 4.1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO_PRIVADO>
cd lighthouse-ingestion-pipeline
````

> **Importante:** Conceda acesso ao seu repositório para os avaliadores antes do prazo final.

### 4.2. Variáveis de Ambiente

Crie um arquivo `.env` com base no `.env.save`:

```ini
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

> ⚠️ **Nunca faça commit de dados sensíveis.**

### 4.3. Estrutura do Projeto

```
.
├── extract/                 
├── load/
├── plugins/
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

## 5. Execução da Pipeline

### 5.1. Construir a Imagem Docker

```bash
docker build -t lighthouse-ingestion-pipeline .
```

### 5.2. Executar o Contêiner

```bash
docker run \
  --env-file .env \
  lighthouse-ingestion-pipeline
```

O script `entrypoint.sh` será executado automaticamente.

#### 5.2.1. O que o `entrypoint.sh` faz:

1. Executa o pipeline com Meltano:

```bash
meltano run tap-mssql target-parquet-sqlserver tap-rest-api-msdk target-parquet-api
```

2. Realiza o upload dos arquivos Parquet para o Databricks:

```bash
# Exemplo com DBFS
databricks fs cp output/docker_elt/sqlserver/ dbfs:/<caminho>/sqlserver/ --recursive --overwrite
databricks fs cp output/docker_elt/api/ dbfs:/<caminho>/api/ --recursive --overwrite
```

> Ajuste os comandos de acordo com seu ambiente Databricks (DBFS vs Unity Catalog).

---

### 5.3. Validação

1. Acesse seu workspace no Databricks.
2. Verifique os arquivos nos caminhos corretos.
3. Crie ou valide as tabelas Delta Lake.
4. Execute queries SQL para testar integridade dos dados.

---

## 6. Contato

Em caso de dúvidas ou sugestões, entre em contato:

**Nome da equipe**:*Alexandre R.Silva Filho*
**Email:** **alexandre.filho@indicium.tech** 
