import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_db, Base, Vacancy, Skill

# 1. Создаем движок для БД в оперативной памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# 2. Создаем сессию и таблицы в этой временной БД
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)

# 3. Функция-подмена для зависимости get_db
def override_get_db():
    try:
        db = TestingSessionLocal()
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
    """Добавляет тестовые данные перед тестом и удаляет их после."""
    # SETUP: Добавляем данные
    with TestingSessionLocal() as db:
        skill = Skill(name="python")
        db.add(skill)
        db.flush() # Получаем ID навыка
        
        vacancy = Vacancy(
            remote_id=999,
            title="Test Python Developer",
            company_name="Test Corp",
            job_type="full-time",
            location="Remote",
            salary_avg=5000.0
        )
        vacancy.skills.append(skill)
        db.add(vacancy)
        db.commit()
    
    yield # Здесь выполняется сам тест
    
    # TEARDOWN: Очищаем таблицы после теста, чтобы следующий тест начал с чистого листа
    with TestingSessionLocal() as db:
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
