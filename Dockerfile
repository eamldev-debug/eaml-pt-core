# Imagem base oficial e minimalista do Python (Segurança e Leveza)
FROM python:3.10-slim

# Evita que o Python grave ficheiros .pyc e força a saída de logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define a diretoria de trabalho dentro do contentor
WORKDIR /app

# Criação de um utilizador sem privilégios de root (Segurança Obrigatória - Menor Privilégio)
RUN adduser --disabled-password --gecos "" appuser

# Copia as dependências e instala-as (sem cache para poupar espaço)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código-fonte do núcleo e da API para o contentor
COPY core/ ./core/

# Altera a propriedade dos ficheiros para o utilizador seguro
RUN chown -R appuser:appuser /app

# Muda para o utilizador não-root (A partir daqui, se houver invasão, o hacker não tem permissões)
USER appuser

# Expõe a porta 8080 (Porta padrão exigida pelo Google Cloud Run)
EXPOSE 8080

# Comando de arranque da API FastAPI utilizando o Uvicorn
CMD ["uvicorn", "core.api.gateway:app", "--host", "0.0.0.0", "--port", "8080"]
