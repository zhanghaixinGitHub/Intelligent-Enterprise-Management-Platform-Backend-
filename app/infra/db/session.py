from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.infra.config.settings import settings


db_path = Path(settings.sqlite_db_path)
if not db_path.parent.exists():
    db_path.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{db_path.as_posix()}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
