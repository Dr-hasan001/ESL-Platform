from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(10), nullable=False, default="student")  # student | teacher
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cefr_level: Mapped[str | None] = mapped_column(String(3), nullable=True)  # A1–C2 (students only)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    submissions = relationship("Submission", back_populates="student", foreign_keys="Submission.student_id")
    media_plays = relationship("MediaPlayEvent", back_populates="user")
    unit_progress = relationship("UnitProgress", back_populates="user")
