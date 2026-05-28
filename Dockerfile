FROM python:3.13-slim

WORKDIR /app

# Copier les dépendances en premier pour profiter du cache Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Utilisateur non-root pour limiter la surface d'attaque
RUN useradd --system --no-create-home appuser \
    && mkdir -p data \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

ENV FLASK_APP=app.py

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
