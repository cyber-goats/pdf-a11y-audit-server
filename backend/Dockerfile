FROM python:3.11

WORKDIR /code

COPY requirements.txt .

# Dodajemy krok czyszczący, aby usunąć potencjalny konflikt
RUN pip uninstall -y PyFitz || true
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]