from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.project import Project
from app.schemas.project_schema import ProjectCreate, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["Projetos"])

@router.post("/")
def criar_projeto(projeto: ProjectCreate, db: Session = Depends(get_db)):

    novo_projeto = Project(
        titulo=projeto.titulo,
        descricao=projeto.descricao
    )

    db.add(novo_projeto)
    db.commit()
    db.refresh(novo_projeto)

    return novo_projeto

@router.get("/")
def listar_projetos(db: Session = Depends(get_db)):
    return db.query(Project).all()

@router.put("/{project_id}")
def atualizar_projeto(project_id: int, projeto: ProjectUpdate, db: Session = Depends(get_db)):

    projeto_db = db.query(Project).filter(Project.id == project_id).first()
    if not projeto_db:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    if projeto.titulo:
        projeto_db.titulo = projeto.titulo

    if projeto.descricao:
        projeto_db.descricao = projeto.descricao

    projeto_db.versao += 1
    projeto_db.ultima_atualizacao = datetime.utcnow()

    db.commit()
    return projeto_db

@router.delete("/{project_id}")
def deletar_projeto(project_id: int, db: Session = Depends(get_db)):

    projeto_db = db.query(Project).filter(Project.id == project_id).first()
    if not projeto_db:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    db.delete(projeto_db)
    db.commit()

    return {"msg": "Projeto excluído"}