
# 🚀 Pipeline de Ingestão de Dados — Lighthouse Checkpoint 2

## 1. Visão Geral do Projeto

Este projeto foi desenvolvido como parte do desafio **Lighthouse Checkpoint 2** da Indicium, com o objetivo de implementar uma **pipeline de ingestão de dados confiável, modular e escalável**, conectando múltiplas fontes e carregando os dados em um ambiente analítico moderno: o **Databricks Lakehouse**.

A solução realiza a ingestão de dados a partir de:

* Um **banco de dados relacional** (MSSQL)
* Uma **API REST**

Os dados extraídos são temporariamente armazenados no formato **Parquet**, e posteriormente convertidos manualmente para o formato **Delta Lake**, garantindo performance, integridade e governança.

A arquitetura foi construída com foco em:

* Clareza, manutenibilidade e modularidade
* Boas práticas de engenharia de dados
* Segurança de credenciais
* Portabilidade do ambiente com Docker

---

## 2. Arquitetura da Solução

A pipeline extrai os dados a partir do **Meltano**, uma ferramenta ELT open-source que permite controle granular das etapas de extração e carga. Todo o projeto é conteinerizado com **Docker**, assegurando reprodutibilidade do ambiente de desenvolvimento e execução.

Após a extração, os dados são organizados em arquivos `.parquet` e transferidos para o **Databricks**, onde são convertidos em **tabelas Delta Lake**, com suporte a:

* Transações ACID
* Schema enforcement & evolution
* Otimizações de leitura e escrita
* Alta escalabilidade

### 🔧 Componentes Técnicos

| Componente           | Papel na Pipeline                                                                                     |
| -------------------- | ----------------------------------------------------------------------------------------------------- |
| `tap-mssql`          | Extrai dados do banco SQL Server utilizando autenticação por usuário/senha                            |
| `tap-rest-api-msdk`  | Conecta-se à API REST utilizando autenticação básica (Basic Auth), acessando os endpoints disponíveis |
| `target-parquet`     | Converte os dados extraídos em arquivos `.parquet` organizados por origem                             |
| `Docker`             | Cria ambiente reprodutível com Meltano, Databricks CLI e dependências Python                          |
| `Databricks CLI`     | Realiza o upload dos arquivos `.parquet` para o Databricks via terminal                               |
| Notebooks auxiliares | Realizam a conversão dos arquivos `.parquet` em tabelas Delta, de forma controlada e modular          |

---

## 3. Requisitos e Pré-Requisitos

Para executar a pipeline localmente, são necessárias as seguintes ferramentas e acessos:

### 🧰 Ferramentas

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (v4.x+)
* [Git](https://git-scm.com/)
* [Databricks CLI](https://docs.databricks.com/dev-tools/cli/index.html) (pré-instalado no container)

### 🔐 Acessos Necessários

* URL e credenciais do banco **MSSQL**
* URL e credenciais da **API REST**
* URL do workspace **Databricks** e um **Token PAT** com permissões de escrita

---

## 4. Configuração do Ambiente

### 4.1 Clonar o Repositório

```bash
git clone https://github.com/alerodriguessf/lighthouse_desafio02_alexandrersf
cd lighthouse_desafio02_alexandrersf
```

### 4.2 Configurar Variáveis de Ambiente

Crie um arquivo `.env` com suas credenciais:

```env
# MSSQL
TAP_MSSQL_HOST=your_mssql_host
TAP_MSSQL_PORT=1433
TAP_MSSQL_USER=your_user
TAP_MSSQL_PASSWORD=your_password
TAP_MSSQL_DATABASE=AdventureWorks2022

# API
API_HOST=https://your-api-url.com
API_USER=your_api_user
API_PASSWORD=your_api_password

# DATABRICKS
DATABRICKS_HOST=https://your-databricks-instance.cloud.databricks.com
DATABRICKS_TOKEN=your_pat_token
```

> 🔐 **Importante**: Não versionar este arquivo com Git.

---

## 5. Estrutura do Projeto

```
.
├── extract/                            # Extração via Meltano
├── load/                               # Carga via Meltano
├── plugins/                            # Plugins Meltano
├── scripts_aux/                        # Scripts auxiliares para discovery e Delta
│   ├── discovery_api_aw_checkpoint2.ipynb
│   ├── delta conversion_api_checkpoint2_alexandrersf (1).ipynb
│   └── delta conversion_sqlserver_checkpoint2_alexandrersf.ipynb
├── Dockerfile                          # Build da imagem com Meltano + CLI Databricks
├── entrypoint.sh                       # Script de orquestração do pipeline
├── .env.save                           # Modelo de exemplo de variáveis de ambiente
├── .gitignore
├── meltano.yml                         # Configuração principal do projeto Meltano
├── requirements.txt                    # Dependências Python
└── README.md                           # Este arquivo
```

---

## 6. Execução da Pipeline

### 6.1 Construir a Imagem Docker

```bash
docker build -t lighthouse-ingestion-pipeline .
```

### 6.2 Executar o Contêiner

```bash
docker run --env-file .env lighthouse-ingestion-pipeline
```

Este comando aciona o `entrypoint.sh`, que:

1. Executa a extração dos dados via Meltano:

```bash
meltano run tap-mssql target-parquet-sqlserver tap-rest-api-msdk target-parquet-api
```

2. Realiza o upload dos arquivos `.parquet` para o Databricks:

```bash
databricks fs cp output/docker_elt/sqlserver/ dbfs:/mnt/<caminho>/sqlserver/ --recursive --overwrite
databricks fs cp output/docker_elt/api/ dbfs:/mnt/<caminho>/api/ --recursive --overwrite
```

---

## 7. Scripts Auxiliares (`scripts_aux/`)

Para facilitar testes, validações e modularizar a etapa final da ingestão, foram incluídos três notebooks:

| Notebook                                                    | Função                                                           |
| ----------------------------------------------------------- | ---------------------------------------------------------------- |
| `discovery_api_aw_checkpoint2.ipynb`                        | Validação e visualização dos dados expostos pela API REST        |
| `delta conversion_api_checkpoint2_alexandrersf (1).ipynb`   | Criação de tabelas Delta a partir dos arquivos `.parquet` da API |
| `delta conversion_sqlserver_checkpoint2_alexandrersf.ipynb` | Conversão dos dados SQL Server para Delta Lake                   |

Esses notebooks foram essenciais para garantir:

* Flexibilidade diante da instabilidade da API
* Modularização das etapas de ingestão
* Controle e auditabilidade do processo

As tabelas Delta criadas seguem o padrão de nomenclatura:

```
raw_api_<tabela>_db
raw_sqlserver_<tabela>_db
```

---

## 8. Contato

**Autor:** Alexandre R.Silva Filho
📧 [alexandre.filho@indicium.tech](mailto:alexandre.filho@indicium.tech)
🔗 [LinkedIn](https://www.linkedin.com/in/alerodriguessf/)

