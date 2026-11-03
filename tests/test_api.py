import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from main import Base, Skill, Vacancy, app, get_db, vacancy_skills

# 1. Создаем движок для БД в оперативной памяти с StaticPool
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# 2. Создаем сессию и таблицы
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)

# 3. Функция-подмена для зависимости get_db
def override_get_db() -> Session:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. Подменяем зависимость в приложении
app.dependency_overrides[get_db] = override_get_db

# 5. Инициализируем тестовый клиент
client = TestClient(app)

# --- Фикстура для добавления И ОЧИСТКИ тестовых данных ---
@pytest.fixture(autouse=True)
def seed_and_clean_test_data():
    """Добавляет тестовые данные перед тестом и корректно удаляет их после."""
    with TestingSessionLocal() as db:
        skill = Skill(name="python")
        db.add(skill)
        db.flush()
        
        vacancy = Vacancy(
            remote_id=999,
            title="Test Python Developer",
            company_name="Test Corp",
            job_type="full-time",
            location="Remote",
            salary_avg=5000.0,
        )
        vacancy.skills.append(skill)
        db.add(vacancy)
        db.commit()
    
    yield
    
    # TEARDOWN: Очищаем таблицы в ПРАВИЛЬНОМ порядке!
    with TestingSessionLocal() as db:
        db.execute(delete(vacancy_skills))
        db.query(Vacancy).delete()
        db.query(Skill).delete()
        db.commit()

# --- Сами тесты ---
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Tech Trends Analyzer"}

def test_get_vacancies_structure():
    response = client.get("/api/v1/vacancies?limit=2")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) >= 1
    
    vacancy = data[0]
    assert "id" in vacancy
    assert "title" in vacancy
    assert "company_name" in vacancy
    assert "skills" in vacancy
    assert isinstance(vacancy["skills"], list)

def test_get_vacancies_with_skill_filter():
    response = client.get("/api/v1/vacancies?skill_filter=python&limit=5")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) >= 1
    for vacancy in data:
        skill_names = [skill["name"].lower() for skill in vacancy["skills"]]
        assert any("python" in skill for skill in skill_names)

def test_get_top_skills():
    response = client.get("/api/v1/stats/top-skills?limit=5")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) >= 1
    
    top_skill = data[0]
    assert top_skill["skill_name"] == "python"
    assert top_skill["vacancy_count"] == 1
