from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./farmer.db"

engine = create_engine(
	DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
	pass


@contextmanager
def get_session() -> Iterator:
	session = SessionLocal()
	try:
		yield session
	finally:
		session.close()


def create_database_tables() -> None:
	from .models import marketplace  # noqa: F401 ensure models are imported
	Base.metadata.create_all(bind=engine)