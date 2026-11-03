from datetime import datetime

from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    create_engine,
    desc,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

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
    job_type: str | None = None
    location: str | None = None
    salary_avg: float | None = None
    publication_date: datetime | None = None
    skills: list[SkillResponse] = []
    model_config = ConfigDict(from_attributes=True)

class SkillStatResponse(BaseModel):
    skill_name: str
    vacancy_count: int

# --- FastAPI Приложение ---
app = FastAPI(title="Tech Trends Analyzer API", version="1.0.0")

# --- База данных ---
class Base(DeclarativeBase):
    pass

vacancy_skills = Table(
    "vacancy_skills",
    Base.metadata,
    Column("vacancy_id", Integer, ForeignKey("vacancies.id"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True),
)

class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    vacancies: Mapped[list["Vacancy"]] = relationship(
        secondary=vacancy_skills, back_populates="skills"
    )

class Vacancy(Base):
    __tablename__ = "vacancies"
    id: Mapped[int] = mapped_column(primary_key=True)
    remote_id: Mapped[int] = mapped_column(unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    company_name: Mapped[str] = mapped_column(String(255), index=True)
    job_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    salary_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_avg: Mapped[float | None] = mapped_column(Float, nullable=True)
    publication_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    description_clean: Mapped[str | None] = mapped_column(String, nullable=True)
    skills: Mapped[list["Skill"]] = relationship(
        secondary=vacancy_skills, back_populates="vacancies", lazy="selectin"
    )

DATABASE_URL = "sqlite:////content/tech_trends.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def get_db():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints ---
@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "Tech Trends Analyzer"}

@app.get("/api/v1/vacancies", response_model=list[VacancyResponse])
def get_vacancies(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    skill_filter: str | None = Query(None),
    db: Session = Depends(get_db),  # noqa: B008
) -> list[VacancyResponse]:
    query = db.query(Vacancy)
    if skill_filter:
        query = query.join(Vacancy.skills).filter(Skill.name.ilike(f"%{skill_filter}%"))
    return query.order_by(desc(Vacancy.publication_date)).offset(skip).limit(limit).all()

@app.get("/api/v1/stats/top-skills", response_model=list[SkillStatResponse])
def get_top_skills(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),  # noqa: B008
) -> list[SkillStatResponse]:
    return (
        db.query(
            Skill.name.label("skill_name"),
            func.count(vacancy_skills.c.vacancy_id).label("vacancy_count"),
        )
        .join(vacancy_skills, Skill.id == vacancy_skills.c.skill_id)
        .group_by(Skill.name)
        .order_by(desc("vacancy_count"))
        .limit(limit)
        .all()
    )
