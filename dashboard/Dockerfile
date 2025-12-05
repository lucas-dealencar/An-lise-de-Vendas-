FROM python:3.9-slim

# Define a pasta de trabalho
WORKDIR /app


RUN pip install --no-cache-dir streamlit pandas s3fs pyarrow minio plotly openpyxl watchdog

# Copiar o código para dentro do container
COPY . .

# Expor a porta do Streamlit
EXPOSE 8501

# Verificação de saúde
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando para rodar o site
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]