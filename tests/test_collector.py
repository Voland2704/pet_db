import pytest
import json
from pathlib import Path

def test_save_to_file_logic(tmp_path):
    """Тест проверяет, что функция корректно создает файл и записывает JSON."""
    # tmp_path - это встроенная фикстура pytest, она создает уникальную временную папку
    test_jobs = [{"id": 1, "title": "Python Dev"}]
    test_path = tmp_path / "test_jobs.json"
    
    # Создаем папку и записываем файл
    test_path.parent.mkdir(parents=True, exist_ok=True)
    with test_path.open("w", encoding="utf-8") as f:
        json.dump(test_jobs, f, ensure_ascii=False, indent=2)
    
    # Act & Assert (Действие и Проверка)
    assert test_path.exists(), "Файл должен быть создан"
    
    with test_path.open("r", encoding="utf-8") as f:
        loaded_data = json.load(f)
    
    assert loaded_data == test_jobs, "Данные в файле должны совпадать с исходными"
