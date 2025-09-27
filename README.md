
# 🚀 Data Ingestion Pipeline

## 1. Project Overview

This project implements a **reliable, modular, and scalable data ingestion pipeline**, connecting multiple sources and loading them into a modern analytics environment: the **Databricks Lakehouse**.

The pipeline ingests data from:

* A **relational database** (MSSQL)  
* A **REST API**  

Extracted data is temporarily stored as **Parquet files**, and later manually converted to the **Delta Lake** format to ensure performance, integrity, and governance.

The architecture was designed with emphasis on:

* Clarity, maintainability, and modularity  
* Data engineering best practices  
* Secure credential management  
* Environment portability with Docker  

---

## 2. Solution Architecture

Data ingestion is handled by **Meltano**, an open-source ELT tool that provides granular control over extraction and loading steps. The entire project runs inside **Docker**, ensuring a reproducible environment for both development and execution.

After extraction, data is stored as `.parquet` files and then uploaded into **Databricks**, where it is converted into **Delta Lake tables** with support for:

* ACID transactions  
* Schema enforcement & evolution  
* Optimized reads and writes  
* High scalability  

### 🔧 Tech Components

| Component            | Role in Pipeline                                                                 |
| -------------------- | -------------------------------------------------------------------------------- |
| `tap-mssql`          | Extracts data from SQL Server using user/password authentication                  |
| `tap-rest-api-msdk`  | Connects to REST API via Basic Auth, consuming available endpoints                |
| `target-parquet`     | Writes extracted data into organized `.parquet` files by source                   |
| `Docker`             | Provides a reproducible environment with Meltano, Databricks CLI, and dependencies |
| `Databricks CLI`     | Uploads `.parquet` files into Databricks File System (DBFS)                       |
| Auxiliary Notebooks  | Convert `.parquet` into Delta Lake tables in a modular and controlled way         |

---

## 3. Requirements & Prerequisites

### 🧰 Tools

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (v4.x+)  
* [Git](https://git-scm.com/)  
* [Databricks CLI](https://docs.databricks.com/dev-tools/cli/index.html) (pre-installed in container)  

### 🔐 Required Access

* MSSQL database URL and credentials  
* REST API URL and credentials  
* Databricks workspace URL + **PAT Token** with write permissions  

---

## 4. Environment Setup

### 4.1 Clone Repository

```bash
git clone https://github.com/alerodriguessf/lighthouse_desafio02_alexandrersf
cd lighthouse_desafio02_alexandrersf
````

### 4.2 Configure Environment Variables

Create a `.env` file with your credentials:

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

> 🔐 **Important:** Do not commit this file to Git.

---

## 5. Project Structure

```
.
├── extract/                            # Extraction via Meltano
├── load/                               # Load via Meltano
├── plugins/                            # Meltano plugins
├── scripts_aux/                        # Auxiliary notebooks (discovery & Delta conversion)
│   ├── discovery_api_aw_checkpoint2.ipynb
│   ├── delta conversion_api_checkpoint2_alexandrersf (1).ipynb
│   └── delta conversion_sqlserver_checkpoint2_alexandrersf.ipynb
├── Dockerfile                          # Build image with Meltano + Databricks CLI
├── entrypoint.sh                       # Orchestration script for pipeline
├── .env.save                           # Example environment file
├── .gitignore
├── meltano.yml                         # Meltano project configuration
├── requirements.txt                    # Python dependencies
└── README.md
```

---

## 6. Running the Pipeline

### 6.1 Build Docker Image

```bash
docker build -t lighthouse-ingestion-pipeline.
```

### 6.2 Run Container

```bash
docker run --env-file .env lighthouse-ingestion-pipeline
```

This triggers `entrypoint.sh`, which:

1. Runs data extraction with Meltano:

```bash
meltano run tap-mssql target-parquet-sqlserver tap-rest-api-msdk target-parquet-api
```

2. Uploads `.parquet` files to Databricks:

```bash
databricks fs cp output/docker_elt/sqlserver/ dbfs:/mnt/<path>/sqlserver/ --recursive --overwrite
databricks fs cp output/docker_elt/api/ dbfs:/mnt/<path>/api/ --recursive --overwrite
```

---

## 7. Auxiliary Scripts (`scripts_aux/`)

Three notebooks are included to support testing, validation, and modularization of ingestion steps:

| Notebook                                                    | Purpose                                                     |
| ----------------------------------------------------------- | ----------------------------------------------------------- |
| `discovery_api_aw_checkpoint2.ipynb`                        | Validation and inspection of REST API data                  |
| `delta conversion_api_checkpoint2_alexandrersf (1).ipynb`   | Creates Delta tables from API `.parquet` files              |
| `delta conversion_sqlserver_checkpoint2_alexandrersf.ipynb` | Converts SQL Server `.parquet` files into Delta Lake tables |

These notebooks ensure:

* Flexibility when dealing with API instability
* Modularization of ingestion steps
* Better auditability and process control

Naming convention for Delta tables:

```
raw_api_<table>_db
raw_sqlserver_<table>_db
```

---

## 8. Contact

**Author:** Alexandre R. Silva Filho
📧 [alexandre.filho@indicium.tech](mailto:alexandre.filho@indicium.tech)
🔗 [LinkedIn](https://www.linkedin.com/in/alerodriguessf/)

```
