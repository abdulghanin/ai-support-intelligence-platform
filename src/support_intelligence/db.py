import os
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

database_url = os.environ["DATABASE_URL"]
engine = create_engine(database_url, pool_pre_ping=True)


class Base(DeclarativeBase):
    """Base class for database tables."""

    pass


class Message(Base):
    """A customer message and its predicted intent."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    intent: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Feedback(Base):
    """A customer rating linked to an existing message."""

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), index=True)
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


def save_message(text: str, intent: str) -> Message:
    """Store a customer message and return its database ID."""
    with Session(engine) as session:
        message = Message(text=text, intent=intent)
        session.add(message)
        session.commit()
        session.refresh(message)
        return message


def save_feedback(message_id: int, rating: int, comment: str | None) -> Feedback:
    """Store a rating only if its message exists."""
    with Session(engine) as session:
        if session.get(Message, message_id) is None:
            raise ValueError("Message not found")

        feedback = Feedback(
            message_id=message_id,
            rating=rating,
            comment=comment,
        )
        session.add(feedback)
        session.commit()
        session.refresh(feedback)
        return feedback
