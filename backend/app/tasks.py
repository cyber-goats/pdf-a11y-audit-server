import os
from celery import Celery

# Pobierz URL do Redisa ze zmiennej środowiskowej, tak jak w docker-compose.yml
# Zapewnia to spójność konfiguracji.
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Inicjalizacja aplikacji Celery.
# 'tasks' - to nazwa bieżącego modułu.
# broker - to adres brokera wiadomości (w naszym przypadku Redis).
# backend - to miejsce, gdzie Celery będzie przechowywać wyniki zadań (również Redis).
celery_app = Celery(
    'tasks',
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Opcjonalna, ale użyteczna konfiguracja
celery_app.conf.update(
    task_track_started=True, # Pozwala śledzić, czy zadanie się rozpoczęło
)

# Przykładowe zadanie do testowania, czy konfiguracja działa.
@celery_app.task(name='app.tasks.add')
def add(x, y):
    """Proste zadanie dodawania dwóch liczb."""
    return x + y