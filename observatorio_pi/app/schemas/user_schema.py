from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    nome: str
    email: str
    senha: str = Field(..., min_length=6, max_length=72)
    tipo: str

class UserLogin(BaseModel):
    email: str
    senha: str = Field(..., min_length=6, max_length=72)