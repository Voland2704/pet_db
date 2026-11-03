from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# --- Pydantic Схемы ---
class SkillResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class VacancyResponse(BaseModel):
    id: int
    remote_id: int
    title: str
    company_name: str
    job_type: Optional[str] = None
    location: Optional[str] = None
    salary_avg: Optional[float] = None
    publication_date: Optional[datetime] = None
    skills: List[SkillResponse] = []
    model_config = ConfigDict(from_attributes=True)

class SkillStatResponse(BaseModel):
    skill_name: str
    vacancy_count: int

# --- FastAPI Приложение ---
app = FastAPI(title="Tech Trends Analyzer API", version="1.0.0")

# --- База данных (импортируем модели из текущей сессии или объявляем заново для автономности) ---
# Для простоты в этом файле мы повторно объявим минимальные модели, 
# чтобы main.py был полностью автономным (Best Practice для продакшена).
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase): pass

vacancy_skills = Table('vacancy_skills', Base.metadata,
    Column('vacancy_id', Integer, ForeignKey('vacancies.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)

class Skill(Base):
    __tablename__ = 'skills'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    vacancies: Mapped[List["Vacancy"]] = relationship(secondary=vacancy_skills, back_populates="skills")

class Vacancy(Base):
    __tablename__ = 'vacancies'
    id: Mapped[int] = mapped_column(primary_key=True)
    remote_id: Mapped[int] = mapped_column(unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    company_name: Mapped[str] = mapped_column(String(255), index=True)
    job_type: Mapped[str] = mapped_column(String(50), nullable=True)
    location: Mapped[str] = mapped_column(String(100), nullable=True)
    salary_min: Mapped[float] = mapped_column(Float, nullable=True)
    salary_max: Mapped[float] = mapped_column(Float, nullable=True)
    salary_avg: Mapped[float] = mapped_column(Float, nullable=True)
    publication_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    description_clean: Mapped[str] = mapped_column(String, nullable=True)
    skills: Mapped[List["Skill"]] = relationship(secondary=vacancy_skills, back_populates="vacancies", lazy="selectin")

DATABASE_URL = "sqlite:////content/tech_trends.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = Session = None # Переопределим ниже

def get_db():
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints ---
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Tech Trends Analyzer"}

@app.get("/api/v1/vacancies", response_model=List[VacancyResponse])
def get_vacancies(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    skill_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Vacancy)
    if skill_filter:
        query = query.join(Vacancy.skills).filter(Skill.name.ilike(f"%{skill_filter}%"))
    return query.order_by(desc(Vacancy.publication_date)).offset(skip).limit(limit).all()

@app.get("/api/v1/stats/top-skills", response_model=List[SkillStatResponse])
def get_top_skills(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    return db.query(
        Skill.name.label('skill_name'),
        func.count(vacancy_skills.c.vacancy_id).label('vacancy_count')
    ).join(vacancy_skills, Skill.id == vacancy_skills.c.skill_id
    ).group_by(Skill.name).order_by(desc('vacancy_count')).limit(limit).all()

print("✅ Файл /content/main.py успешно создан!")
