# Use uma imagem base Python oficial
FROM python:3.12-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Copia os arquivos de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código
COPY . .

# Expõe a porta que o Streamlit vai usar
EXPOSE 8501

# Define variável de ambiente para garantir que o Streamlit rode em modo headless
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Comando para executar a aplicação
CMD ["streamlit", "run", "app.py"] 