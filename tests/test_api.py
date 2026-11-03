import pytest
from fastapi.testclient import TestClient
from main import app

# Инициализируем тестовый клиент. 
# Он НЕ запускает реальный сервер, а симулирует запросы напрямую к приложению.
client = TestClient(app)

def test_health_check():
    """Тест проверяет, что сервис отвечает на базовый запрос."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Tech Trends Analyzer"}

def test_get_vacancies_structure():
    """Тест проверяет структуру ответа и пагинацию."""
    response = client.get("/api/v1/vacancies?limit=2")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) <= 2
    
    if len(data) > 0:
        vacancy = data[0]
        assert "id" in vacancy
        assert "title" in vacancy
        assert "company_name" in vacancy
        assert "skills" in vacancy
        assert isinstance(vacancy["skills"], list)

def test_get_vacancies_with_skill_filter():
    """Тест проверяет фильтрацию вакансий по навыку."""
    # Ищем вакансии с навыком "python" (или любым другим, который точно есть в БД)
    response = client.get("/api/v1/vacancies?skill_filter=python&limit=5")
    assert response.status_code == 200
    data = response.json()
    
    # Проверяем, что в каждой возвращенной вакансии есть "python" в навыках
    for vacancy in data:
        skill_names = [skill["name"].lower() for skill in vacancy["skills"]]
        assert any("python" in skill for skill in skill_names), f"Python not found in {vacancy['title']}"

def test_get_top_skills():
    """Тест проверяет эндпоинт статистики топ навыков."""
    response = client.get("/api/v1/stats/top-skills?limit=5")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) <= 5
    
    if len(data) > 0:
        top_skill = data[0]
        assert "skill_name" in top_skill
        assert "vacancy_count" in top_skill
        assert isinstance(top_skill["vacancy_count"], int)
        
    # Проверяем, что список отсортирован по убыванию количества
    counts = [item["vacancy_count"] for item in data]
    assert counts == sorted(counts, reverse=True), "Список навыков должен быть отсортирован по убыванию"
