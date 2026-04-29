from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserLogin
from app.core.security import hash_senha, verificar_senha, criar_token

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/register")
def registrar(user: UserCreate, db: Session = Depends(get_db)):

    usuario_existente = db.query(User).filter(User.email == user.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    novo_usuario = User(
        nome=user.nome,
        email=user.email,
        senha_hash=hash_senha(user.senha),
        tipo=user.tipo
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return {"msg": "Usuário criado com sucesso"}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    usuario = db.query(User).filter(User.email == user.email).first()
    if not usuario or not verificar_senha(user.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = criar_token({"sub": usuario.email, "tipo": usuario.tipo})
    return {"access_token": token}