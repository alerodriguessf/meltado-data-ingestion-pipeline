
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

A orquestração da pipeline é feita com Meltano, uma plataforma ELT open-source, conteinerizada com Docker para garantir consistência de ambiente. Os dados extraídos são temporariamente salvos em arquivos Parquet antes de serem carregados no Databricks como tabelas Delta Lake.

### 2.1. Componentes Técnicos

**Meltano (Orquestrador ELT):**

- `tap-mssql`: Extrator que se conecta ao banco MSSQL.  
- `tap-rest-api-msdk`: Extrator para API REST, com paginação offset e limit. Streams:  
  - SalesOrderHeader  
  - SalesOrderDetail  
  - PurchaseOrderHeader  
  - PurchaseOrderDetail  
- `target-parquet`: Loader que salva os dados em arquivos `.parquet` organizados por fonte:
  - `target-parquet-sqlserver`
  - `target-parquet-api`

**Docker:** Utilizado para conteinerizar o ambiente Meltano e todas as dependências (Databricks CLI, Python, pacotes de sistema). O `Dockerfile` é baseado na imagem `meltano/meltano:latest-python3.11`.

**Databricks CLI (v2):** Responsável pelo upload dos arquivos Parquet para o Lakehouse (via DBFS ou Unity Catalog).

**Databricks Lakehouse (Delta Lake):** Destino final dos dados. Vantagens:
- Transações ACID  
- Controle de schema (enforcement & evolution)  
- Performance otimizada para análise  
- Alta escalabilidade  

---

## 3. Requisitos e Pré-requisitos

Para executar este projeto, você precisará de:

- Docker Desktop (4.x+) ou Docker Engine  
- Git  
- Acesso ao Databricks:  
  - URL do workspace  
  - Personal Access Token (PAT)  
- Acesso ao banco MSSQL:  
  - Host, porta, usuário, senha e nome do banco  
- Acesso à API:  
  - URL base, usuário e senha (basic auth)  

---

## 4. Configuração do Ambiente Local

### 4.1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO_PRIVADO>
cd lighthouse-ingestion-pipeline
````

> ⚠️ Importante: Conceda acesso ao seu repositório para os avaliadores antes do prazo final.

### 4.2. Variáveis de Ambiente

Crie um arquivo `.env` com base no `.env.save`:

```env
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

> ⚠️ Nunca faça commit de dados sensíveis.

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

### 5.2.1. O que o `entrypoint.sh` faz:

* Executa o pipeline com Meltano:

  ```bash
  meltano run tap-mssql target-parquet-sqlserver tap-rest-api-msdk target-parquet-api
  ```
* Realiza o upload dos arquivos Parquet para o Databricks:

  ```bash
  databricks fs cp output/docker_elt/sqlserver/ dbfs:/<caminho>/sqlserver/ --recursive --overwrite
  databricks fs cp output/docker_elt/api/ dbfs:/<caminho>/api/ --recursive --overwrite
  ```

> ⚙️ Ajuste os caminhos conforme seu ambiente Databricks (DBFS vs Unity Catalog).

---

## 6. Conversão Manual em Tabelas Delta

Após o upload dos arquivos Parquet para o Databricks, utilizamos **notebooks dedicados** para realizar a conversão manual das partições Parquet em **tabelas Delta Lake** no nível *bronze*.

Esses notebooks foram desenvolvidos de forma modular e possuem as seguintes responsabilidades:

* Ler recursivamente os arquivos `.parquet` em subpastas
* Inferir o schema dos dados automaticamente
* Criar tabelas Delta gerenciadas com nomes padronizados como:

  * `raw_api_<nome>_db`
  * `raw_sqlserver_<nome>_db`

### Notebooks disponíveis:

* `delta_conversion_api_checkpoint2_alexandrersf`: converte todos os arquivos da API em tabelas Delta no Unity Catalog
* `delta_conversion_sqlserver_checkpoint2_alexandrersf`: mesma lógica aplicada aos arquivos provenientes do SQL Server

Esses scripts estão localizados na pasta `/Workspace/Users/<seu_usuario_databricks>/notebooks/` e podem ser executados diretamente no Databricks.

> ✅ O processo é automatizado e garante que cada partição gere uma tabela individual.
> ✅ Todos os nomes seguem um padrão que inclui a fonte de origem, facilitando o rastreio e a auditoria.

---

## 7. Validação

* Acesse seu workspace no Databricks
* Verifique se as tabelas Delta foram criadas no catálogo correto
* Execute queries SQL para validar a integridade dos dados
* Confirme se a nomenclatura das tabelas segue o padrão definido

---

## 8. Contato

**Equipe:** Alexandre R. Silva Filho
📧 **Email:** [alexandre.filho@indicium.tech](mailto:alexandre.filho@indicium.tech)

---

## 📌 Sobre

Desafio de infraestrutura e ingestão de dados do programa Lighthouse - Indicium
