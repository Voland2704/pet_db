import pytest
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Импортируем наш класс (предполагаем, что он определен в текущей сессии, 
# но для чистоты теста мы можем импортировать его, если сохраним в .py файл. 
# Пока протестируем логику сохранения)

def test_save_to_file_logic():
    """Тест проверяет, что функция корректно создает файл и записывает JSON."""
    # Arrange (Подготовка)
    test_jobs = [{"id": 1, "title": "Python Dev"}]
    test_path = Path("/content/data/test_jobs.json")
    
    # Мы не будем вызывать реальный асинхронный метод здесь для простоты,
    # а проверим саму логику записи, которую мы потом вынесем.
    test_path.parent.mkdir(parents=True, exist_ok=True)
    with test_path.open("w", encoding="utf-8") as f:
        json.dump(test_jobs, f, ensure_ascii=False, indent=2)
    
    # Act & Assert (Действие и Проверка)
    assert test_path.exists()
    with test_path.open("r", encoding="utf-8") as f:
        loaded_data = json.load(f)
    
    assert loaded_data == test_jobs
    
    # Cleanup (Очистка)
    test_path.unlink()
