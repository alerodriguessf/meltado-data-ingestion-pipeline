
# Pipeline de Ingestão de Dados - Lighthouse Checkpoint 2

## 1. Visão Geral do Projeto

[cite_start]Este projeto implementa uma pipeline de ingestão de dados robusta e eficiente, desenvolvida como parte do desafio Lighthouse Checkpoint 2 da Indicium[cite: 1]. [cite_start]O objetivo principal é a extração de dados de duas fontes distintas – um banco de dados relacional e uma API [cite: 2] [cite_start]– e o carregamento desses dados em um ambiente Databricks Lakehouse [cite: 2][cite_start], utilizando o formato Delta Lake para otimização, escalabilidade e conformidade com as melhores práticas de dados[cite: 9].

[cite_start]A solução foi meticulosamente projetada com foco em modularidade, reusabilidade, clareza e manutenibilidade do código [cite: 10][cite_start], aderindo rigorosamente às boas práticas de engenharia de dados[cite: 10]. [cite_start]Isso inclui o gerenciamento seguro de credenciais [cite: 13, 31][cite_start], tratamento abrangente de erros [cite: 11] [cite_start]e a garantia de idempotência da pipeline[cite: 11, 47].

## 2. Arquitetura da Solução

[cite_start]A pipeline de ingestão de dados é orquestrada utilizando Meltano, uma plataforma ELT (Extract, Load, Transform) de código aberto, e conteinerizada com Docker para garantir um ambiente de execução consistente e isolado[cite: 49]. [cite_start]Os dados extraídos são temporariamente staged como arquivos Parquet antes de serem carregados no Databricks e persistidos como tabelas Delta Lake[cite: 9].

```mermaid
graph TD
    A[Banco de Dados Relacional (MSSQL)] -- Extrai Dados via ODBC/JDBC --> B(Meltano - tap-mssql)
    C[API REST Externa (HTTP/HTTPS)] -- Extrai Dados via MSDK --> D(Meltano - tap-rest-api-msdk)
    B -- Carrega para Parquet (staging local) --> E(Meltano - target-parquet-sqlserver)
    D -- Carrega para Parquet (staging local) --> F(Meltano - target-parquet-api)
    E -- Upload via Databricks CLI --> G[Databricks Lakehouse - Delta Lake (DBFS/Unity Catalog)]
    F -- Upload via Databricks CLI --> G
    H[Docker Container] -- Contém a Aplicação Meltano e Ferramentas --> I(Ambiente de Execução Isolado)
    I --> B & D & E & F & G
    J[Variáveis de Ambiente] -- Configuração Segura --> H
```

**2.1. Componentes Técnicos Detalhados:**

* **Meltano (Core ELT Orchestrator):**
    * [cite_start]**`tap-mssql` (Extractor):** Plugin Meltano responsável por conectar-se ao banco de dados MSSQL[cite: 40, 67, 68]. [cite_start]Utiliza conexões seguras e eficientes para extrair dados[cite: 7].
    * [cite_start]**`tap-rest-api-msdk` (Extractor):** Plugin Meltano baseado no SDK de Extratores do Singer (MSDK), configurado para interagir com a API REST[cite: 40, 67]. Este `tap` está configurado para extrair os seguintes *streams* com paginação via *offset* e *limit*:
        * `SalesOrderHeader`
        * `SalesOrderDetail`
        * `PurchaseOrderHeader`
        * `PurchaseOrderDetail`
        [cite_start]Definições de esquema (schema) para cada stream são explicitamente declaradas em `meltano.yml` para garantir a integridade dos dados[cite: 42].
    * **`target-parquet` (Loaders):** Plugins de carregamento do Meltano que convertem os dados extraídos (em formato Singer Spec JSON) para arquivos Parquet, um formato colunar otimizado para análise de big data. Duas instâncias são configuradas para organizar os dados por fonte:
        * `target-parquet-sqlserver`: Para dados provenientes do MSSQL.
        * `target-parquet-api`: Para dados provenientes da API.
        Os arquivos Parquet são staged em caminhos distintos dentro do contêiner (`output/docker_elt/sqlserver` e `output/docker_elt/api`).

* [cite_start]**Docker:** Utilizado para conteinerizar a aplicação Meltano e todas as suas dependências (Python, pacotes do sistema, Databricks CLI)[cite: 49]. Isso garante um ambiente de execução isolado, portátil e replicável em qualquer máquina com Docker. O `Dockerfile` detalha todas as etapas de build, desde a imagem base (`meltano/meltano:latest-python3.11`) até a instalação das dependências e configuração do ponto de entrada.

* [cite_start]**Databricks CLI (v2):** Instalado e configurado dentro do contêiner Docker[cite: 6]. Após a geração dos arquivos Parquet, o Databricks CLI será utilizado para fazer o upload desses arquivos para o Databricks Lakehouse (diretamente no DBFS ou em um local gerenciado pelo Unity Catalog, dependendo da configuração do ambiente Databricks). [cite_start]Isso permite a criação ou atualização de tabelas Delta Lake no destino final[cite: 41].

* [cite_start]**Databricks Lakehouse (Delta Lake):** O destino final dos dados[cite: 2, 73]. [cite_start]Os dados são armazenados no formato Delta Lake[cite: 9], que oferece:
    * **ACID Transactions:** Garantia de consistência e durabilidade dos dados.
    * **Schema Enforcement & Evolution:** Prevenção de corrupção de dados e flexibilidade para adaptações futuras.
    * [cite_start]**Performance Otimizada:** Formato colunar e otimizações para cargas de trabalho analíticas[cite: 43].
    * [cite_start]**Escalabilidade:** Capacidade de lidar com volumes crescentes de dados[cite: 12, 46].

## 3. Requisitos e Pré-requisitos

Para replicar e executar este projeto, os seguintes pré-requisitos são essenciais:

* **Docker Desktop:** Versão 4.x ou superior (para Windows/macOS) ou Docker Engine (para Linux).
* **Git:** Para clonar o repositório.
* **Acesso ao Databricks:**
    * URL do Databricks Workspace (e.g., `https://adb-<workspace-id>.<region>.azuredatabricks.net/`).
    * Um Personal Access Token (PAT) do Databricks com permissões adequadas para criar/gravar em tabelas e gerenciar arquivos no DBFS/Unity Catalog. [cite_start]As informações de acesso ao Databricks serão fornecidas no Training[cite: 24, 82].
* **Acesso ao Banco de Dados Relacional (MSSQL):**
    * Host, Porta, Usuário, Senha e Nome do Banco de Dados. [cite_start]Os acessos ao banco de dados já estão disponíveis[cite: 25, 83].
* **Acesso à API Externa:**
    * URL Base da API (e.g., `https://api.example.com/v1/`).
    * Usuário e Senha para autenticação `basic`. [cite_start]Os acessos à API já estão disponíveis[cite: 25, 83].

## 4. Configuração do Ambiente Local

### 4.1. Clonar o Repositório

Primeiro, clone este repositório para sua máquina local:

```bash
git clone <URL_DO_SEU_REPOSITORIO_PRIVADO>
cd lighthouse-ingestion-pipeline # (ou o nome da pasta do seu projeto)
```
[cite_start]**Importante:** Conceda acesso ao seu avaliador ao repositório Git privado no GitHub/Bitbucket antes do prazo final[cite: 18, 57, 85]. [cite_start]O acesso também deverá ser concedido a membros do L&D, caso seja requisitado[cite: 18].

### 4.2. Gerenciamento de Variáveis de Ambiente

[cite_start]As credenciais e configurações sensíveis são gerenciadas via variáveis de ambiente para segurança[cite: 13, 52].
[cite_start]**É CRÍTICO que você NUNCA faça commit de dados sensíveis ou credenciais diretamente no código ou no repositório Git[cite: 31, 88].**

1.  Crie um arquivo chamado `.env` no diretório raiz do projeto.
2.  Copie o conteúdo do arquivo `.env.save` para o seu novo arquivo `.env`.
3.  Preencha as variáveis com suas credenciais e URLs de acesso reais:

    ```ini
    # Conteúdo do arquivo .env
    # Acesso ao MSSQL
    TAP_MSSQL_HOST=your_mssql_host
    TAP_MSSQL_PORT=your_mssql_port
    TAP_MSSQL_USER=your_mssql_user
    TAP_MSSQL_PASSWORD=your_mssql_password
    TAP_MSSQL_DATABASE=your_mssql_database

    # Acesso à API Externa
    API_HOST=your_api_base_url
    API_USER=your_api_username
    API_PASSWORD=your_api_password

    # Acesso ao Databricks
    DATABRICKS_HOST=your_databricks_workspace_url
    DATABRICKS_TOKEN=your_databricks_personal_access_token
    ```

### 4.3. Estrutura do Projeto

[cite_start]O projeto segue uma estrutura organizada para facilitar a navegação e manutenção[cite: 56].

```
.
├── extract/                            # (Opcional) Configurações específicas de extração, se Meltano demandar
├── load/                               # (Opcional) Configurações específicas de carregamento, se Meltano demandar
├── plugins/                            # (Opcional) Contém plugins Meltano customizados, se aplicável
├── .dockerignore                       # Define arquivos/padrões a serem ignorados pelo Docker na construção da imagem
├── .env.save                           # Template seguro para as variáveis de ambiente (NUNCA faça commit do .env)
├── .gitignore                          # Define arquivos/padrões a serem ignorados pelo Git
├── Dockerfile                          # Define os passos para construir a imagem Docker do projeto
[cite_start]├── README.md                           # Este documento [cite: 20, 55]
├── entrypoint.sh                       # Script de entrada principal do contêiner Docker, orquestra a pipeline
├── meltano.yml                         # Arquivo de configuração principal do Meltano, definindo taps, targets e streams
[cite_start]└── requirements.txt                    # Dependências Python adicionais do projeto [cite: 22]
```


## 5. Execução da Pipeline

A pipeline é projetada para ser executada em um ambiente conteinerizado via Docker.

### 5.1. Construção da Imagem Docker

No diretório raiz do projeto, execute o comando para construir a imagem Docker. Este processo pode levar alguns minutos, pois inclui a instalação de pacotes de sistema (curl, unzip), o Databricks CLI e todas as dependências Python (via `requirements.txt` e `meltano install`).

```bash
docker build -t lighthouse-ingestion-pipeline .
```

### 5.2. Execução do Contêiner Docker e da Pipeline

Após a construção bem-sucedida da imagem, execute o contêiner. O script `entrypoint.sh` será automaticamente invocado como o ponto de entrada do contêiner, orchestrando a execução da pipeline Meltano e o upload dos dados para o Databricks.

```bash
docker run \
  --env-file .env \
  lighthouse-ingestion-pipeline
```

**5.2.1. Detalhamento do `entrypoint.sh`:**

O script `entrypoint.sh` (verifique seu conteúdo para a implementação exata) é responsável por:

1.  **Executar a Extração e Carregamento do Meltano:**
    ```bash
    meltano run tap-mssql target-parquet-sqlserver tap-rest-api-msdk target-parquet-api
    ```
    Este comando instrui o Meltano a extrair dados do MSSQL e da API, carregando-os nos respectivos `target-parquet` que irão gerar os arquivos Parquet no sistema de arquivos do contêiner.
2.  **Upload para Databricks:**
    Após a geração dos arquivos Parquet, o script deve conter a lógica para fazer o upload desses arquivos para o Databricks usando o `databricks cli`. Exemplos de comandos que podem ser utilizados:
    ```bash
    # Exemplo: Upload para DBFS
    databricks fs cp output/docker_elt/sqlserver/ dbfs:/<caminho_databricks>/sqlserver/ --recursive --overwrite
    databricks fs cp output/docker_elt/api/ dbfs:/<caminho_databricks>/api/ --recursive --overwrite

    # Exemplo: Se estiver usando Unity Catalog, você pode precisar de comandos adicionais para carregar os arquivos para tabelas
    # ou o processo de carga pode ser feito diretamente via Spark no Databricks.
    ```
    **É fundamental que você implemente a lógica de upload no `entrypoint.sh` com base nos requisitos específicos do seu ambiente Databricks e estratégia de ingestão (DBFS ou Unity Catalog).**

### 5.3. Validação da Ingestão

[cite_start]Após a execução bem-sucedida do contêiner, valide a ingestão dos dados no Databricks[cite: 36].

1.  Acesse seu workspace Databricks.
2.  Navegue até o local onde os arquivos Parquet foram carregados (DBFS ou Unity Catalog).
3.  Verifique a existência dos arquivos Parquet para as tabelas `SalesOrderHeader`, `SalesOrderDetail`, `PurchaseOrderHeader`, e `PurchaseOrderDetail` (da API) e as tabelas extraídas do MSSQL.
4.  [cite_start]Crie ou confirme a existência das tabelas Delta Lake correspondentes e execute consultas para verificar a integridade e completude dos dados[cite: 41].


## 8. Contato

Para quaisquer dúvidas, sugestões ou informações adicionais, por favor, sinta-se à vontade para entrar em contato.

**Equipe:** [Alexandre R.Silva Filho]
**Email:** [alexandre.filho@indicium.tech]
```
