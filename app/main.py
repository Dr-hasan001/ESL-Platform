from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import Base, engine
from app.routers import auth, books, homework, media, submissions, admin

# Create all tables (dev convenience — in prod use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ESL Learning Platform", docs_url="/api/docs")

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(homework.router)
app.include_router(media.router)
app.include_router(submissions.router)
app.include_router(admin.router)

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def root(request: Request):
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse(url="/dashboard")
    return RedirectResponse(url="/login")


@app.get("/homework")
async def homework_list_page(request: Request):
    from app.database import SessionLocal
    from app.routers.deps import _resolve_user
    from app.models.homework import HomeworkAssignment, AssignmentStudent
    from app.models.submission import Submission

    db = SessionLocal()
    try:
        token = request.cookies.get("access_token")
        try:
            user = _resolve_user(token, db)
        except Exception:
            return RedirectResponse(url="/login")

        if user.role == "teacher":
            return RedirectResponse(url="/teacher")

        rows = (
            db.query(AssignmentStudent)
            .filter(AssignmentStudent.student_id == user.id)
            .join(HomeworkAssignment, AssignmentStudent.assignment_id == HomeworkAssignment.id)
            .filter(HomeworkAssignment.is_active == True)
            .all()
        )

        sections = {"listening": [], "reading": [], "writing": [], "story": []}
        for row in rows:
            hw = row.assignment
            sub = db.query(Submission).filter(
                Submission.assignment_id == hw.id,
                Submission.student_id == user.id,
            ).first()
            item = {
                "id": hw.id,
                "type": hw.type,
                "title": hw.title,
                "due_date": hw.due_date,
                "status": "complete" if (sub and sub.is_complete) else ("in_progress" if sub else "not_started"),
            }
            if hw.type == "listening":
                sections["listening"].append(item)
            elif hw.type in ("reading", "grammar"):
                sections["reading"].append(item)
            elif hw.type == "writing":
                sections["writing"].append(item)
            elif hw.type == "general_topic":
                sections["story"].append(item)

        return templates.TemplateResponse("student/homework.html", {
            "request": request,
            "user": user,
            "sections": type("Sections", (), sections)(),
        })
    finally:
        db.close()


@app.get("/dashboard")
async def dashboard(request: Request):
    from app.database import SessionLocal
    from app.routers.deps import _resolve_user
    from app.models.homework import HomeworkAssignment, AssignmentStudent
    from app.models.submission import Submission
    from jose import JWTError

    db = SessionLocal()
    try:
        token = request.cookies.get("access_token")
        try:
            user = _resolve_user(token, db)
        except Exception:
            return RedirectResponse(url="/login")

        if user.role == "teacher":
            return RedirectResponse(url="/teacher")

        # Homework assigned to this student
        rows = (
            db.query(AssignmentStudent)
            .filter(AssignmentStudent.student_id == user.id)
            .join(HomeworkAssignment, AssignmentStudent.assignment_id == HomeworkAssignment.id)
            .filter(HomeworkAssignment.is_active == True)
            .all()
        )
        hw_list = []
        for row in rows:
            hw = row.assignment
            sub = db.query(Submission).filter(
                Submission.assignment_id == hw.id,
                Submission.student_id == user.id,
            ).first()
            hw_list.append({
                "id": hw.id,
                "type": hw.type,
                "title": hw.title,
                "due_date": hw.due_date,
                "status": "complete" if (sub and sub.is_complete) else ("in_progress" if sub else "not_started"),
                "score": float(sub.score) if sub and sub.score is not None else None,
                "teacher_score": float(sub.teacher_score) if sub and sub.teacher_score is not None else None,
            })

        from app.models.book import Book
        books_q = db.query(Book).order_by(Book.book_number)
        if user.cefr_level:
            books_q = books_q.filter(Book.cefr_level == user.cefr_level)
        books = books_q.all()

        return templates.TemplateResponse("student/dashboard.html", {
            "request": request,
            "user": user,
            "homework": hw_list,
            "books": books,
        })
    finally:
        db.close()
