from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, SmallInteger, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    assignment_id: Mapped[int] = mapped_column(Integer, ForeignKey("homework_assignments.id"), nullable=False, index=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)

    # Auto-graded fields (Listening, Reading, Grammar, General Topics)
    score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)    # percentage 0.00–100.00
    total_questions: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    correct_count: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    # Writing-specific fields
    written_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    word_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    teacher_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    teacher_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    assignment = relationship("HomeworkAssignment", back_populates="submissions")
    student = relationship("User", back_populates="submissions", foreign_keys=[student_id])
    answers = relationship("SubmissionAnswer", back_populates="submission", cascade="all, delete-orphan")


class SubmissionAnswer(Base):
    __tablename__ = "submission_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    submission_id: Mapped[int] = mapped_column(Integer, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("homework_questions.id"), nullable=False)
    chosen_index: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    submission = relationship("Submission", back_populates="answers")
    question = relationship("HomeworkQuestion", back_populates="answers")
