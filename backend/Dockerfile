FROM python:3.11

WORKDIR /code

COPY requirements.txt .

# Kroki instalacji Pythona bez zmian
RUN pip uninstall -y PyFitz || true
RUN pip install --no-cache-dir -r requirements.txt

# ZMIENIAMY PAKIET NA `docker-cli`
RUN apt-get update && \
    apt-get install -y --no-install-recommends docker-cli && \
    rm -rf /var/lib/apt/lists/*

# Zostawiamy naszą linię weryfikacyjną, aby mieć 100% pewności, że tym razem się powiedzie
RUN which docker

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]