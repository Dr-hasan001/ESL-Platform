from sqlalchemy import ForeignKey, Integer, JSON, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    series: Mapped[str | None] = mapped_column(String(200), nullable=True)
    book_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 1–6
    cefr_level: Mapped[str] = mapped_column(String(3), nullable=False)  # A1–C2
    cover_color: Mapped[str | None] = mapped_column(String(7), nullable=True)  # hex
    unit_count: Mapped[int] = mapped_column(SmallInteger, default=30)

    units = relationship("Unit", back_populates="book", order_by="Unit.unit_number")


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    unit_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    word_count: Mapped[int] = mapped_column(SmallInteger, default=20)

    book = relationship("Book", back_populates="units")
    words = relationship("Word", back_populates="unit", order_by="Word.position")
    progress = relationship("UnitProgress", back_populates="unit")


class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    unit_id: Mapped[int] = mapped_column(Integer, ForeignKey("units.id", ondelete="CASCADE"), nullable=False)
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    word: Mapped[str] = mapped_column(String(100), nullable=False)
    part_of_speech: Mapped[str | None] = mapped_column(String(30), nullable=True)
    definition: Mapped[str | None] = mapped_column(Text, nullable=True)
    example: Mapped[str | None] = mapped_column(Text, nullable=True)
    arabic_translation: Mapped[str | None] = mapped_column(String(200), nullable=True)
    emoji: Mapped[str | None] = mapped_column(String(10), nullable=True)
    derivatives: Mapped[list | None] = mapped_column(JSON, default=list)

    unit = relationship("Unit", back_populates="words")


class UnitProgress(Base):
    __tablename__ = "unit_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_id: Mapped[int] = mapped_column(Integer, ForeignKey("units.id", ondelete="CASCADE"), nullable=False, index=True)
    cards_seen: Mapped[list | None] = mapped_column(JSON, default=list)   # word IDs flipped
    quiz_revealed: Mapped[list | None] = mapped_column(JSON, default=list) # word IDs revealed
    story_score: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    user = relationship("User", back_populates="unit_progress")
    unit = relationship("Unit", back_populates="progress")
