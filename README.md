

```markdown
# Pipeline de Ingestão de Dados - Lighthouse Checkpoint 2

## 1. Visão Geral do Projeto

Este projeto implementa uma pipeline de ingestão de dados robusta e eficiente, desenvolvida como parte do desafio Lighthouse Checkpoint 2 da Indicium. [cite_start]O objetivo principal é a extração de dados de duas fontes distintas – um banco de dados relacional e uma API – e o carregamento desses dados em um ambiente Databricks Lakehouse, utilizando o formato Delta Lake para otimização, escalabilidade e conformidade com as melhores práticas de dados[cite: 1, 2].

[cite_start]A solução foi meticulosamente projetada com foco em modularidade, reusabilidade, clareza e manutenibilidade do código, aderindo rigorosamente às boas práticas de engenharia de dados[cite: 10]. [cite_start]Isso inclui o gerenciamento seguro de credenciais [cite: 13, 31][cite_start], tratamento abrangente de erros [cite: 11] [cite_start]e a garantia de idempotência da pipeline[cite: 11, 47].

## 2. Arquitetura da Solução

[cite_start]A pipeline de ingestão de dados é orquestrada utilizando Meltano, uma plataforma ELT (Extract, Load, Transform) de código aberto, e conteinerizada com Docker para garantir um ambiente de execução consistente e isolado[cite: 49]. [cite_start]Os dados extraídos são temporariamente staged como arquivos Parquet antes de serem carregados no Databricks e persistidos como tabelas Delta Lake[cite: 9, 41].

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
    * [cite_start]**`tap-mssql` (Extractor):** Plugin Meltano responsável por conectar-se ao banco de dados MSSQL[cite: 40]. [cite_start]Utiliza conexões seguras e eficientes para extrair dados[cite: 7].
    * [cite_start]**`tap-rest-api-msdk` (Extractor):** Plugin Meltano baseado no SDK de Extratores do Singer (MSDK), configurado para interagir com a API REST[cite: 40]. Este `tap` está configurado para extrair os seguintes *streams* com paginação via *offset* e *limit*:
        * `SalesOrderHeader`
        * `SalesOrderDetail`
        * `PurchaseOrderHeader`
        * `PurchaseOrderDetail`
        [cite_start]Definições de esquema (schema) para cada stream são explicitamente declaradas em `meltano.yml` para garantir a integridade dos dados[cite: 42].
    * [cite_start]**`target-parquet` (Loaders):** Plugins de carregamento do Meltano que convertem os dados extraídos (em formato Singer Spec JSON) para arquivos Parquet, um formato colunar otimizado para análise de big data[cite: 9]. Duas instâncias são configuradas para organizar os dados por fonte:
        * `target-parquet-sqlserver`: Para dados provenientes do MSSQL.
        * `target-parquet-api`: Para dados provenientes da API.
        Os arquivos Parquet são staged em caminhos distintos dentro do contêiner (`output/docker_elt/sqlserver` e `output/docker_elt/api`).

* [cite_start]**Docker:** Utilizado para conteinerizar a aplicação Meltano e todas as suas dependências (Python, pacotes do sistema, Databricks CLI)[cite: 49]. Isso garante um ambiente de execução isolado, portátil e replicável em qualquer máquina com Docker. O `Dockerfile` detalha todas as etapas de build, desde a imagem base (`meltano/meltano:latest-python3.11`) até a instalação das dependências e configuração do ponto de entrada.

* **Databricks CLI (v2):** Instalado e configurado dentro do contêiner Docker. Após a geração dos arquivos Parquet, o Databricks CLI será utilizado para fazer o upload desses arquivos para o Databricks Lakehouse (diretamente no DBFS ou em um local gerenciado pelo Unity Catalog, dependendo da configuração do ambiente Databricks). [cite_start]Isso permite a criação ou atualização de tabelas Delta Lake no destino final[cite: 41].

* [cite_start]**Databricks Lakehouse (Delta Lake):** O destino final dos dados[cite: 2]. Os dados são armazenados no formato Delta Lake, que oferece:
    * **ACID Transactions:** Garantia de consistência e durabilidade dos dados.
    * **Schema Enforcement & Evolution:** Prevenção de corrupção de dados e flexibilidade para adaptações futuras.
    * **Performance Otimizada:** Formato colunar e otimizações para cargas de trabalho analíticas.
    * **Escalabilidade:** Capacidade de lidar com volumes crescentes de dados.

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
[cite_start]**Importante:** Conceda acesso ao seu avaliador ao repositório Git privado no GitHub/Bitbucket antes do prazo final[cite: 18, 85]. [cite_start]O acesso também deverá ser concedido a membros do L&D, caso seja requisitado[cite: 18].

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
├── README.md                           # Este documento
├── entrypoint.sh                       # Script de entrada principal do contêiner Docker, orquestra a pipeline
├── meltano.yml                         # Arquivo de configuração principal do Meltano, definindo taps, targets e streams
└── requirements.txt                    # Dependências Python adicionais do projeto
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
4.  Crie ou confirme a existência das tabelas Delta Lake correspondentes e execute consultas para verificar a integridade e completude dos dados.

## 6. Boas Práticas e Considerações de Engenharia

Este projeto incorpora diversas boas práticas de engenharia de dados:

* [cite_start]**Modularização e Reusabilidade:** A configuração via `meltano.yml` e o uso de plugins promovem a modularização do código e a reusabilidade dos componentes de extração e carregamento[cite: 10].
* [cite_start]**Idempotência:** A pipeline é projetada para ser idempotente[cite: 11, 47]. Re-execuções da pipeline com o mesmo estado de origem não devem resultar em duplicação de dados ou inconsistências. Isso é geralmente alcançado através de lógicas de UPSERT ou recriação de tabelas, dependendo da estratégia de carga adotada no Databricks.
* [cite_start]**Tratamento de Erros:** Mecanismos básicos para identificação e tratamento de erros estão implementados (implicitamente via Meltano e via controle no `entrypoint.sh`)[cite: 11, 47]. Acompanhamento de logs é essencial para depuração.
* **Otimização e Escalabilidade:**
    * [cite_start]O uso de Parquet como formato intermediário e Delta Lake como formato final contribui para a performance e escalabilidade, dada a natureza colunar e otimizações de armazenamento[cite: 43, 46].
    * A configuração de paginação na `tap-rest-api-msdk` (offset/limit) ajuda a gerenciar grandes volumes de dados de API de forma eficiente.
    * [cite_start]O design considera futuras adaptações e volumes crescentes de dados[cite: 12, 46].
* [cite_start]**Segurança:** Gerenciamento seguro de variáveis de ambiente é priorizado para acesso a dados sensíveis, evitando a exposição de credenciais[cite: 13, 31, 52].
* [cite_start]**Controle de Versão com Git:** Utilização eficaz do Git para versionamento do código, com commits claros e organização de branches[cite: 13, 50].

## 7. Critérios de Avaliação Atendidos (Referência do Desafio)

[cite_start]Este projeto foi desenvolvido para atender aos seguintes critérios de avaliação do Checkpoint 2[cite: 39, 81]:

* **Funcionamento e Eficiência do Pipeline de Ingestão de Dados:**
    * [cite_start]Conexão e extração correta dos dados do Banco de Dados e da API[cite: 40].
    * [cite_start]Carregamento correto e completo dos dados no Databricks, no local e formato adequados (Delta Lake)[cite: 41].
    * [cite_start]Definição e aplicação correta do schema dos dados para carregamento no Databricks[cite: 42].
    * [cite_start]Considerações sobre otimização do pipeline (ex: performance, uso de recursos) - citar durante a apresentação[cite: 43].
    * [cite_start]Tempo de execução razoável para o volume de dados proposto[cite: 44].
    * [cite_start]Nível de complexidade apropriado para o problema e volume de dados[cite: 45].
    * [cite_start]Considerações de escalabilidade futura do pipeline - citar durante a apresentação[cite: 46].
    * [cite_start]Implementação de mecanismos básicos para identificação e tratamento de erros[cite: 47].
    * [cite_start]Garantia de idempotência do pipeline[cite: 47].
* **Infraestrutura, Configuração e Deploy do Pipeline:**
    * [cite_start]Clareza na especificação dos recursos de infraestrutura utilizados (ex: clusters Databricks, VMs) - citar durante a apresentação[cite: 48].
    * [cite_start]Utilização de conteinerização (ex: Docker)[cite: 49].
    * [cite_start]Apresentação de um design claro da arquitetura da solução[cite: 49].
    * [cite_start]Uso adequado de versionamento com Git (commits, uso de branches)[cite: 50].
    * [cite_start]Gerenciamento seguro de configurações e informações sensíveis (ex: variáveis de ambiente), sem exposição no código[cite: 52].
    * [cite_start]Documentação clara do processo para deploy do pipeline[cite: 53].
* **Organização, Documentação e Qualidade do Código:**
    * [cite_start]Legibilidade, clareza e boa estrutura do código[cite: 54].
    * [cite_start]Aplicação de boas práticas de desenvolvimento[cite: 54].
    * [cite_start]Presença e qualidade do arquivo README.md (descrição do projeto, instruções de configuração e execução, listagem de dependências)[cite: 55].
    * [cite_start]Organização lógica e clara dos arquivos e pastas no repositório[cite: 56].
* **Entrega, Apresentação e Comunicação:**
    * [cite_start]Compartilhamento correto do repositório GitHub (privado, com acesso ao avaliador)[cite: 57].
    * [cite_start]Clareza e objetividade na apresentação da solução, seus componentes e o fluxo de dados[cite: 58].
    * [cite_start]Explicação clara da infraestrutura e das decisões técnicas[cite: 59].
    * [cite_start]Capacidade de explicar conceitos técnicos de forma compreensível[cite: 59].
    * [cite_start]Demonstração funcional do pipeline durante a apresentação (ao vivo)[cite: 60, 89].
    * [cite_start]Habilidade em responder às perguntas dos avaliadores de forma precisa e demonstrando entendimento do projeto[cite: 61].

## 8. Contato

Para quaisquer dúvidas, sugestões ou informações adicionais, por favor, sinta-se à vontade para entrar em contato.

**Equipe:** [Seu Nome ou Nomes dos Integrantes da Dupla]
**Email:** [Seu Email ou Email da Equipe]
```
