# 🚀 Tech Trends Analyzer

**Tech Trends Analyzer** — это полноценный аналитический пайплайн и REST API для сбора, очистки и анализа рынка IT-вакансий. Проект демонстрирует полный цикл разработки современного Python-приложения: от асинхронного сбора данных и их обработки до упаковки в Docker и настройки CI/CD.

![CI Pipeline](https://github.com/Voland2704/pet_db/actions/workflows/ci.yml/badge.svg)
![Python 3.13](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Ruff](https://img.shields.io/badge/Ruff-005571?style=flat&logo=ruff)

---

## 🎯 О проекте

Проект решает задачу мониторинга спроса на IT-навыки. Он собирает данные с открытых API вакансий, очищает их от HTML-мусора, парсит зарплаты и сохраняет в реляционную базу данных. На основе этих данных строится REST API, который позволяет получать отфильтрованные списки вакансий и статистику по самым востребованным технологиям.

## 🛠 Технологический стек

* **Backend & API:** Python 3.13, FastAPI, Pydantic V2
* **Database & ORM:** SQLAlchemy 2.0 (Modern syntax with `Mapped`), SQLite (PostgreSQL-ready)
* **Data Processing:** Pandas, Regex (HTML cleaning & salary parsing)
* **Async & Networking:** `asyncio`, `httpx`
* **Testing:** Pytest, FastAPI `TestClient`, In-Memory SQLite (`StaticPool`)
* **DevOps & Quality:** Docker, Docker Compose, GitHub Actions (CI/CD), Ruff (Linting & Formatting)

---

## 🏗 Архитектура и Пайплайн

Приложение разделено на логические этапы, каждый из которых использует лучшие практики индустрии:

1. **Сбор данных (Collector):** Асинхронный клиент на `httpx` собирает сырые JSON-данные с Remotive API.
2. **Очистка (Data Processing):** `Pandas` используется для ETL-процесса: удаление HTML-тегов, парсинг зарплатных вилок, извлечение навыков.
3. **Хранение (Database):** Данные сохраняются в реляционную БД. Реализована связь **Many-to-Many** между вакансиями и навыками через ассоциативную таблицу.
4. **API (FastAPI):** Предоставляет endpoints с пагинацией, фильтрацией и валидацией входных данных.
5. **Testing & CI:** Интеграционные тесты используют изолированную in-memory базу данных. GitHub Actions автоматически прогоняет тесты и линтер Ruff при каждом push.

---

## 📡 API Endpoints

API автоматически документируется через Swagger UI (доступен по адресу `/docs` при локальном запуске).

| Метод | Endpoint | Описание |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check сервиса |
| `GET` | `/api/v1/vacancies` | Список вакансий (поддерживает `skip`, `limit`, `skill_filter`) |
| `GET` | `/api/v1/stats/top-skills` | Топ самых востребованных навыков с количеством вакансий |

---
