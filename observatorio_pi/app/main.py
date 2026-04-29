




# import requests
# from fastapi import FastAPI, Request, Form, Depends
# from fastapi.responses import HTMLResponse, RedirectResponse
# from sqlalchemy.orm import Session
# from app.database import engine, Base, get_db
# from app.models.user import User
# from app.models.project import Project
# from app.core.security import verificar_senha
# from app.routers import auth_router, project_router

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import engine, Base
from app.routers import auth_router, project_router
import requests
import os
from fastapi.templating import Jinja2Templates



# app = FastAPI()

app = FastAPI(title="Observatório de Projetos Integradores")

app.include_router(auth_router.router)
app.include_router(project_router.router)

Base.metadata.create_all(bind=engine)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

API_URL = "http://127.0.0.1:8000"


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        name="login.html",
        request=request,
        context={}
    )


@app.post("/login")
def login(request: Request, email: str = Form(...), senha: str = Form(...)):

    response_api = requests.post(
        f"{API_URL}/auth/login",
        json={"email": email, "senha": senha}
    )

    if response_api.status_code != 200:
        return templates.TemplateResponse(
            name="login.html",
            request=request,
            context={"erro": "Credenciais inválidas"}
        )

    token = response_api.json()["access_token"]

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="token", value=token)
    return response


# @app.get("/", response_class=HTMLResponse)
# def home(request: Request):
#     return templates.TemplateResponse(
#         name="login.html",
#         request=request,
#         context={}
#     )


# @app.post("/login")
# def login(
#     request: Request,
#     email: str = Form(...),
#     senha: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     usuario = db.query(User).filter(User.email == email).first()

#     if not usuario or not verificar_senha(senha, usuario.senha_hash):
#         return templates.TemplateResponse(
#     name="login.html",
#     request=request,
#     context={"erro": "Credenciais inválidas"}
# )
    
#     response = RedirectResponse(url="/dashboard", status_code=303)
#     response.set_cookie(key="user_id", value=str(usuario.id))
#     return response


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/")

    headers = {"Authorization": f"Bearer {token}"}

    response_api = requests.get(f"{API_URL}/projects", headers=headers)

    projetos = []
    if response_api.status_code == 200:
        projetos = response_api.json()

    return templates.TemplateResponse(
        name="dashboard.html",
        request=request,
        context={"projetos": projetos}
    )

# @app.get("/dashboard", response_class=HTMLResponse)
# def dashboard(request: Request, db: Session = Depends(get_db)):

#     user_id = request.cookies.get("user_id")
#     if not user_id:
#         return RedirectResponse(url="/")

#     projetos = db.query(Project).filter(Project.aluno_id == int(user_id)).all()
#     return templates.TemplateResponse(
#     name="dashboard.html",
#     request=request,
#     context={"projetos": projetos}
# )

@app.post("/projeto/criar")
def criar_projeto(request: Request, titulo: str = Form(...), descricao: str = Form(...)):

    token = request.cookies.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    requests.post(
        f"{API_URL}/projects",
        json={"titulo": titulo, "descricao": descricao},
        headers=headers
    )

    return RedirectResponse(url="/dashboard", status_code=303)

# @app.post("/projeto/criar")
# def criar_projeto(
#     request: Request,
#     titulo: str = Form(...),
#     descricao: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     user_id = request.cookies.get("user_id")

#     novo = Project(
#         titulo=titulo,
#         descricao=descricao,
#         aluno_id=int(user_id)
#     )

#     db.add(novo)
#     db.commit()

#     return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/projeto/deletar/{id}")
def deletar_projeto(id: int, request: Request):

    token = request.cookies.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    requests.delete(f"{API_URL}/projects/{id}", headers=headers)

    return RedirectResponse(url="/dashboard", status_code=303)

# @app.get("/projeto/deletar/{id}")
# def deletar_projeto(id: int, request: Request, db: Session = Depends(get_db)):
#     projeto = db.query(Project).filter(Project.id == id).first()

#     db.delete(projeto)
#     db.commit()

#     return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("token")
    return response