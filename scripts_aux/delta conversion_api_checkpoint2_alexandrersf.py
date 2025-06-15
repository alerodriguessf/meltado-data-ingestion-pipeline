

# 📥 Ingestão de arquivos Parquet da API para tabelas Delta (camada Bronze)

# COMMAND ----------
# 🧱 BLOCO 1 - Imports e Configurações Iniciais
import re
from pyspark.sql import SparkSession

catalog = "ted_dev"
schema = "dev_alexandre_filho"
caminho_api = "/Volumes/ted_dev/dev_alexandre_filho/raw/api/"

spark = SparkSession.builder.getOrCreate()

# COMMAND ----------
# 🧱 BLOCO 2 - Função para normalizar nomes de tabela

def normalizar_nome_tabela(caminho):
    nome = caminho.rstrip("/").split("/")[-1]
    nome = re.sub(r"[^a-zA-Z0-9_]", "_", nome).lower()
    return f"raw_api_{nome}_db"

# COMMAND ----------
# 🧱 BLOCO 3 - Função para criar tabela Delta a partir de uma subpasta

def criar_tabela_gerenciada(caminho_base):
    nome_tabela = normalizar_nome_tabela(caminho_base)
    if not nome_tabela:
        print(f"❌ Nome inválido para: {caminho_base}")
        return

    # Buscar arquivos .parquet dentro da subpasta (recursivamente)
    arquivos_parquet = dbutils.fs.ls(caminho_base)
    arquivos_validos = [f.path for f in arquivos_parquet if f.path.endswith(".parquet") or f.path.endswith(".gz.parquet")]

    # Se não encontrar diretamente, entra recursivamente
    if not arquivos_validos:
        for subdir in arquivos_parquet:
            if subdir.isDir():
                sub_arquivos = dbutils.fs.ls(subdir.path)
                arquivos_validos += [f.path for f in sub_arquivos if f.path.endswith(".parquet") or f.path.endswith(".gz.parquet")]

    if not arquivos_validos:
        print(f"⚠️ Nenhum arquivo Parquet encontrado em: {caminho_base}")
        return

    print(f"📦 Lendo arquivos: {arquivos_validos[:1]} ... (total: {len(arquivos_validos)})")

    # Lê todos os arquivos juntos
    df = spark.read.format("parquet").load(arquivos_validos)

    # Escreve como tabela Delta gerenciada
    df.write.format("delta")\
      .mode("overwrite")\
      .saveAsTable(f"{catalog}.{schema}.{nome_tabela}")

    print(f"✅ Tabela {catalog}.{schema}.{nome_tabela} criada com sucesso!")

# COMMAND ----------

# 🧱 BLOCO 4 - Loop para processar todas as subpastas
subpastas = dbutils.fs.ls(caminho_api)

for pasta in subpastas:
    if pasta.isDir():
        criar_tabela_gerenciada(pasta.path)

print("🎉 Processo concluído!")
