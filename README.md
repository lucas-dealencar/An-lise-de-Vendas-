# 🚀 Pipeline de Análise de Vendas - PySpark + MinIO

Sistema de ETL (Extract, Transform, Load) para análise de dados de vendas usando PySpark e MinIO como data lake, executado em ambiente Jupyter Notebook.

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Configuração](#configuração)
- [Pipelines Implementados](#pipelines-implementados)
- [Como Executar](#como-executar)
- [Estrutura de Dados](#estrutura-de-dados)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

Este projeto implementa **5 pipelines de transformação de dados** para análise de vendas, processando dados de transações comerciais e gerando insights sobre:

- ✅ Estatísticas de vendas e lucro por categoria
- ✅ Análise dos top 20 clientes por região
- ✅ Foco específico na região Central
- ✅ Cálculo de rentabilidade por cliente
- ✅ Conversão de dados para formato analítico (long format)

### 🎨 Características

- **Processamento Distribuído**: Utiliza Apache Spark para processar grandes volumes de dados
- **Storage S3-Compatible**: MinIO como data lake para armazenamento de dados
- **Formato Otimizado**: Dados salvos em Parquet para melhor performance
- **Logs Automáticos**: Registro de execução de cada pipeline
- **Modular**: Cada pipeline é uma função independente

---

## 🏗️ Arquitetura

```
┌─────────────────┐
│   Dataset.csv   │
│   (MinIO S3)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PySpark ETL    │
│  ┌───────────┐  │
│  │Pipeline 1 │  │──► s3a://datalake/pipeline1/statistics
│  │Pipeline 2 │  │──► s3a://datalake/pipeline2/top_clients_by_region
│  │Pipeline 3 │  │──► s3a://datalake/pipeline3/central_sales
│  │Pipeline 4 │  │──► s3a://datalake/pipeline4/profitability
│  │Pipeline 5 │  │──► s3a://datalake/pipeline5/long_format
│  └───────────┘  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   MinIO S3      │
│   (Data Lake)   │
│   + Logs        │
└─────────────────┘
```

---

## 📦 Pré-requisitos

### Software Necessário

- **Python** 3.8+
- **Apache Spark** 3.3+
- **Jupyter Notebook** ou **JupyterLab**
- **MinIO** (servidor rodando)

### Bibliotecas Python

```bash
pip install pyspark
pip install jupyter
```

### Infraestrutura

- **MinIO Server** rodando em `http://minio:9000`
- **Bucket** `datalake` criado no MinIO
- **Dataset** `dataset.csv` carregado no bucket

---

## ⚙️ Configuração

### 1. Configurações do MinIO

No notebook, ajuste as credenciais conforme seu ambiente:

```python
MINIO_ENDPOINT = "http://minio:9000"
ACCESS_KEY = "admin"      # Seu access key
SECRET_KEY = "password"   # Seu secret key
BUCKET_NAME = "datalake"
```

### 2. Estrutura do Dataset

O CSV deve conter as seguintes colunas:

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `Row ID` | Integer | Identificador único da linha |
| `Order ID` | String | ID do pedido |
| `Order Date` | Date | Data do pedido |
| `Ship Date` | Date | Data de envio |
| `Ship Mode` | String | Modo de envio |
| `Customer ID` | String | ID do cliente |
| `Customer Name` | String | Nome do cliente |
| `Segment` | String | Segmento do cliente |
| `Country` | String | País |
| `City` | String | Cidade |
| `State` | String | Estado |
| `Postal Code` | Integer | CEP |
| `Region` | String | Região (Central, East, South, West) |
| `Product ID` | String | ID do produto |
| `Category` | String | Categoria do produto |
| `Sub-Category` | String | Subcategoria |
| `Product Name` | String | Nome do produto |
| `Sales` | Double | Valor de vendas |
| `Quantity` | Integer | Quantidade vendida |
| `Discount` | Double | Desconto aplicado |
| `Profit` | Double | Lucro obtido |

---

## 📊 Pipelines Implementados

### Pipeline 1: Estatísticas de Vendas 📈

**Objetivo**: Calcular média e desvio padrão de vendas e lucro por subcategoria.

**Transformações**:
- Agrupamento por `Sub-Category`
- Cálculo de média de `Profit` e `Sales`
- Cálculo de desvio padrão de `Profit` e `Sales`
- Join dos resultados
- Cálculo de diferença: `MeanProfit - StdProfit`

**Output**: `s3a://datalake/pipeline1/statistics`

**Colunas resultantes**:
```
Sub-Category | MeanProfit | MeanSales | StdProfit | StdSales | DiffMean
```

**Uso**:
```python
logs.append(pipeline_1_stats(df_raw))
```

---

### Pipeline 2: Top 20 Clientes por Região 🏆

**Objetivo**: Identificar os 20 principais clientes e analisar suas vendas por região.

**Transformações**:
1. Identificar top 20 clientes globalmente (maior volume de vendas)
2. Filtrar dados apenas desses clientes
3. Criar pivot table: `Sub-Category` x `Region`
4. Calcular média de vendas
5. Renomear colunas para `Sales_{Region}`

**Output**: `s3a://datalake/pipeline2/top_clients_by_region`

**Estrutura**:
```
Sub-Category | Sales_Central | Sales_East | Sales_South | Sales_West
```

**Uso**:
```python
logs.append(pipeline_2_top_clients(df_raw))
```

---

### Pipeline 3: Análise Região Central 🎯

**Objetivo**: Análise focada nos top 20 clientes da região Central.

**Transformações**:
1. Filtrar apenas região `Central`
2. Identificar top 20 clientes dessa região
3. Pivot por `Customer ID` x `Sub-Category`
4. Somar vendas

**Output**: `s3a://datalake/pipeline3/central_sales`

**Estrutura**:
```
Customer ID | Accessories | Appliances | Art | Binders | ... | Tables
```

**Uso**:
```python
logs.append(pipeline_3_central(df_raw, spark))
```

---

### Pipeline 4: Análise de Rentabilidade 💰

**Objetivo**: Calcular margem de lucro (profit ratio) por cliente e região.

**Transformações**:
1. Agrupar por `Region` e `Customer ID`
2. Somar `Sales` e `Profit`
3. Calcular `profitRatio = Profit / Sales`
4. Ordenar por rentabilidade decrescente

**Output**: `s3a://datalake/pipeline4/profitability`

**Colunas resultantes**:
```
Region | Customer ID | Sales | Profit | profitRatio
```

**Uso**:
```python
logs.append(pipeline_4_profitability(df_raw))
```

**Interpretação**:
- `profitRatio > 0`: Cliente lucrativo
- `profitRatio < 0`: Cliente com prejuízo
- `profitRatio = 0.25`: 25% de margem de lucro

---

### Pipeline 5: Formato Long (Unpivot) 📝

**Objetivo**: Converter dados de formato wide para long (análise mais flexível).

**Transformações**:
1. Agregar dados por `Region` e `Customer ID`
2. Usar função `stack()` para unpivot
3. Criar colunas `Metric` e `Value`

**Output**: `s3a://datalake/pipeline5/long_format`

**Estrutura**:
```
Region | Customer ID | Metric       | Value
-------+--------------+--------------+--------
West   | AB-10001     | Sales        | 1250.50
West   | AB-10001     | Profit       | 312.75
West   | AB-10001     | ProfitRatio  | 0.25
```

**Uso**:
```python
logs.append(pipeline_5_long_format(df_raw))
```

---

## 🚀 Como Executar

### Opção 1: Jupyter Notebook (Passo a Passo)

1. **Abrir o notebook**:
```bash
jupyter notebook pipeline.ipynb
```

2. **Executar células sequencialmente**:
   - Cell 1: Imports
   - Cell 2: Configuração do Spark
   - Cell 3: Função de carga de dados
   - Cells 4-10: Funções dos pipelines
   - Cell 11: Função de log
   - Cell 12: Execução principal

3. **Resultado esperado**:
```
Iniciando Spark .
Lendo dados de origem: s3a://datalake/dataset.csv
Registros carregados: 9994
Pipeline 1: Estatísticas (Média/Desvio Padrão)...
Pipeline 2: Top 20 Clientes por Região
Pipeline 3: Análise Região Central
Pipeline 4: Rentabilidade
Pipeline 5: Formato Longo (Stack)...
Salvando Logs
✅ SUCESSO! Todos os pipelines foram executados e salvos no MinIO.
```

### Opção 2: Script Python

Converter o notebook para script:

```bash
jupyter nbconvert --to script pipeline.ipynb
python pipeline.py
```

### Opção 3: Spark Submit

```bash
spark-submit \
  --master local[*] \
  --packages org.apache.hadoop:hadoop-aws:3.3.4 \
  --conf spark.hadoop.fs.s3a.endpoint=http://minio:9000 \
  --conf spark.hadoop.fs.s3a.access.key=admin \
  --conf spark.hadoop.fs.s3a.secret.key=password \
  --conf spark.hadoop.fs.s3a.path.style.access=true \
  --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
  pipeline.py
```

---

## 📁 Estrutura de Dados no MinIO

Após execução, a seguinte estrutura é criada no bucket `datalake`:

```
datalake/
├── dataset.csv                          # Dados originais
├── pipeline1/
│   └── statistics/
│       ├── _SUCCESS
│       └── part-*.parquet
├── pipeline2/
│   └── top_clients_by_region/
│       ├── _SUCCESS
│       └── part-*.parquet
├── pipeline3/
│   └── central_sales/
│       ├── _SUCCESS
│       └── part-*.parquet
├── pipeline4/
│   └── profitability/
│       ├── _SUCCESS
│       └── part-*.parquet
├── pipeline5/
│   └── long_format/
│       ├── _SUCCESS
│       └── part-*.parquet
└── logs/
    ├── _SUCCESS
    └── part-*.parquet
```

### Metadados de Logs

O arquivo de logs contém:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `pipeline` | String | Nome do pipeline (Pipeline1, Pipeline2, etc.) |
| `path` | String | Caminho completo no MinIO |
| `count` | Long | Número de registros gerados |
| `timestamp` | Timestamp | Data/hora de execução |

---

## 🔍 Verificação de Resultados

### Via MinIO Console

1. Acessar: `http://localhost:9001` (ou IP do servidor)
2. Login com credenciais configuradas
3. Navegar até bucket `datalake`
4. Explorar pastas dos pipelines

### Via Jupyter Notebook

```python
# Ler resultado do Pipeline 1
df_result = spark.read.parquet("s3a://datalake/pipeline1/statistics")
df_result.show(10)

# Contar registros
print(f"Total de registros: {df_result.count()}")

# Ver schema
df_result.printSchema()

# Converter para Pandas (para visualização)
pdf = df_result.toPandas()
print(pdf.head())
```

### Via CLI do MinIO

```bash
# Listar arquivos
mc ls myminio/datalake/pipeline1/statistics/

# Download de arquivo
mc cp myminio/datalake/pipeline1/statistics/part-00000.parquet ./
```

---

## 📊 Exemplos de Análise

### 1. Top 5 Subcategorias Mais Lucrativas

```python
df_stats = spark.read.parquet("s3a://datalake/pipeline1/statistics")
df_stats.orderBy(desc("MeanProfit")).show(5)
```

### 2. Clientes com Melhor Margem de Lucro

```python
df_prof = spark.read.parquet("s3a://datalake/pipeline4/profitability")
df_prof.filter(col("profitRatio") > 0.3).count()
```

### 3. Vendas por Região (Top Clientes)

```python
df_region = spark.read.parquet("s3a://datalake/pipeline2/top_clients_by_region")
df_region.select("Sub-Category", "Sales_Central", "Sales_East").show()
```

---

## 🛠️ Troubleshooting

### Problema 1: Erro de Conexão com MinIO

**Erro**:
```
NoSuchBucket: The specified bucket does not exist
```

**Solução**:
```python
# Criar bucket via código
from minio import Minio

client = Minio(
    "minio:9000",
    access_key="admin",
    secret_key="password",
    secure=False
)

if not client.bucket_exists("datalake"):
    client.make_bucket("datalake")
```

### Problema 2: Arquivo CSV Não Encontrado

**Erro**:
```
Path does not exist: s3a://datalake/dataset.csv
```

**Solução**:
1. Verificar se arquivo foi carregado no MinIO
2. Usar MinIO Console para fazer upload
3. Ou usar CLI:
```bash
mc cp dataset.csv myminio/datalake/
```

### Problema 3: Memória Insuficiente

**Erro**:
```
OutOfMemoryError: Java heap space
```

**Solução**:
```python
spark = SparkSession.builder \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "4g") \
    .getOrCreate()
```

### Problema 4: Dependências Faltando

**Erro**:
```
java.lang.ClassNotFoundException: org.apache.hadoop.fs.s3a.S3AFileSystem
```

**Solução**:
```bash
# Download manual do JAR
wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar

# Adicionar ao Spark
spark = SparkSession.builder \
    .config("spark.jars", "/path/to/hadoop-aws-3.3.4.jar") \
    .getOrCreate()
```

### Problema 5: Logs Muito Verbosos

**Solução**:
```python
spark.sparkContext.setLogLevel("ERROR")
# ou
spark.sparkContext.setLogLevel("WARN")
```

---

## 📈 Métricas de Performance

### Dataset de Exemplo (9,994 registros)

| Pipeline | Tempo Médio | Registros Saída | Tamanho Parquet |
|----------|-------------|-----------------|-----------------|
| Pipeline 1 | ~2s | 17 | ~5 KB |
| Pipeline 2 | ~3s | 17 | ~8 KB |
| Pipeline 3 | ~2s | 20 | ~15 KB |
| Pipeline 4 | ~2s | 2,501 | ~120 KB |
| Pipeline 5 | ~2s | 7,503 | ~180 KB |

**Total**: ~11 segundos para processamento completo

---

## 🔐 Segurança

### Boas Práticas

1. **Não commitar credenciais**: Use variáveis de ambiente
```python
import os
ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
```

2. **Criptografia**: Habilitar SSL no MinIO
```python
.config("spark.hadoop.fs.s3a.connection.ssl.enabled", "true")
```

3. **Controle de acesso**: Usar IAM policies no MinIO

---


## 📚 Referências

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [MinIO Python Client](https://min.io/docs/minio/linux/developers/python/API.html)
- [Hadoop AWS Integration](https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html)

---




