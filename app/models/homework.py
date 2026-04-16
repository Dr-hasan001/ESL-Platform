from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HomeworkAssignment(Base):
    __tablename__ = "homework_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # listening|reading|grammar|writing|general_topic
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    teacher = relationship("User", foreign_keys=[teacher_id])
    assigned_students = relationship("AssignmentStudent", back_populates="assignment", cascade="all, delete-orphan")
    questions = relationship("HomeworkQuestion", back_populates="assignment", order_by="HomeworkQuestion.position", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="assignment")

    # Type-specific detail (at most one will be populated)
    hw_listening = relationship("HWListening", back_populates="assignment", uselist=False, cascade="all, delete-orphan")
    hw_reading = relationship("HWReading", back_populates="assignment", uselist=False, cascade="all, delete-orphan")
    hw_grammar = relationship("HWGrammar", back_populates="assignment", uselist=False, cascade="all, delete-orphan")
    hw_writing = relationship("HWWriting", back_populates="assignment", uselist=False, cascade="all, delete-orphan")
    hw_general_topic = relationship("HWGeneralTopic", back_populates="assignment", uselist=False, cascade="all, delete-orphan")


class AssignmentStudent(Base):
    __tablename__ = "assignment_students"

    assignment_id: Mapped[int] = mapped_column(Integer, ForeignKey("homework_assignments.id", ondelete="CASCADE"), primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    assignment = relationship("HomeworkAssignment", back_populates="assigned_students")
    student = relationship("User")


class HWListening(Base):
    __tablename__ = "hw_listening"

    assignment_id: Mapped[int] = mapped_column(Integer, ForeignKey("homework_assignments.id", ondelete="CASCADE"), primary_key=True)
    audio_url: Mapped[str] = mapped_column(String(500), nullable=False)
    play_gate: Mapped[int] = mapped_column(SmallInteger, default=3)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)

    assignment = relationship("HomeworkAssignment", back_populates="hw_listening")


class HWReading(Base):
    __tablename__ = "hw_reading"

    assignment_id: Mapped[int] = mapped_column(Integer, ForeignKey("homework_assignments.id", ondelete="CASCADE"), primary_key=True)
    passage_text: Mapped[str] = mapped_column(Text, nullable=False)

    assignment = relationship("HomeworkAssignment", back_populates="hw_reading")


class HWGrammar(Base):
    __tablename__ = "hw_grammar"

    assignment_id: Mapped[int] = mapped_column(Integer, ForeignKey("homework_assignments.id", ondelete="CASCADE"), primary_key=True)
    exercise_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # fill_blank|multiple_choice|reorder|matching
    grammar_point: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g. "Past Simple"

    assignment = relationship("HomeworkAssignment", back_populates="hw_grammar")


class HWWriting(Base):
    __tablename__ = "hw_writing"

    assignment_id: Mapped[int] = mapped_column(Integer, ForeignKey("homework_assignments.id", ondelete="CASCADE"), primary_key=True)
    model_text: Mapped[str | None] = mapped_column(Text, nullable=True)        # example writing to study
    useful_language: Mapped[list | None] = mapped_column(JSON, default=list)   # ["I'd like to...", "Furthermore..."]
    prompt: Mapped[str] = mapped_column(Text, nullable=False)                  # the writing task
    text_type: Mapped[str | None] = mapped_column(String(50), nullable=True)   # email|letter|article|message
    min_words: Mapped[int] = mapped_column(SmallInteger, default=80)
    max_words: Mapped[int] = mapped_column(SmallInteger, default=150)

    assignment = relationship("HomeworkAssignment", back_populates="hw_writing")


class HWGeneralTopic(Base):
    __tablename__ = "hw_general_topic"

    assignment_id: Mapped[int] = mapped_column(Integer, ForeignKey("homework_assignments.id", ondelete="CASCADE"), primary_key=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    play_gate: Mapped[int] = mapped_column(SmallInteger, default=3)

    assignment = relationship("HomeworkAssignment", back_populates="hw_general_topic")
    topic = relationship("Topic", back_populates="hw_general_topic")


class HomeworkQuestion(Base):
    __tablename__ = "homework_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    assignment_id: Mapped[int] = mapped_column(Integer, ForeignKey("homework_assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(20), default="multiple_choice")  # multiple_choice|fill_blank|short_answer
    options: Mapped[list | None] = mapped_column(JSON, nullable=True)     # ["option A", "option B", ...]
    correct_index: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)  # 0-based
    correct_text: Mapped[str | None] = mapped_column(Text, nullable=True)  # for fill_blank / short_answer

    assignment = relationship("HomeworkAssignment", back_populates="questions")
    answers = relationship("SubmissionAnswer", back_populates="question")
