from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.deps import current_user
from app.services.auth_service import authenticate_user, create_access_token

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


class LoginForm(BaseModel):
    username: str
    password: str


# ── HTML pages ──────────────────────────────────────────────────────────────

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response


# ── API ──────────────────────────────────────────────────────────────────────

@router.post("/api/auth/login")
async def api_login(form: LoginForm, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    token = create_access_token(user.id, user.role)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        # No max_age → session cookie; clears on browser close
    )
    return {"role": user.role, "display_name": user.display_name or user.username}


@router.get("/api/auth/me")
async def api_me(user=Depends(current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "role": user.role,
        "cefr_level": user.cefr_level,
    }
