import os
from datetime import datetime

from sqlalchemy import DateTime, String, Text, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

database_url = os.environ["DATABASE_URL"]
engine = create_engine(database_url, pool_pre_ping=True)


class Base(DeclarativeBase):
    pass


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    intent: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


def save_message(text: str, intent: str) -> Message:
    with Session(engine) as session:
        message = Message(text=text, intent=intent)
        session.add(message)
        session.commit()
        session.refresh(message)
        return message