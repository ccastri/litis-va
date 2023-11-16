from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

router = APIRouter()

# Tu base de datos simulada de usuarios
fake_users_db = {
    "camilo@example.com": {
        "Nombre": "CAMILO",
        "Apellido": "CASTRILLON",
        "Email": "camilo@example.com",
        "Contraseña": "Bio2160cc.1607",
        "Contraseña2": "Bio2160cc.1607",
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    Nombre: str
    Apellido: str
    Email: str


class UserInDB(User):
    hashed_password: str


def fake_hash_password(password: str):
    # Simulación de función para hashear la contraseña
    return password  # En este caso, no se hace hash, se retorna la misma contraseña


def get_user(email: str):
    if email in fake_users_db:
        user_dict = fake_users_db[email]
        return UserInDB(**user_dict)


def verify_password(plain_password: str, hashed_password: str):
    # Comparación simple de contraseñas (en un caso real, usaríamos un método seguro como bcrypt)
    return plain_password == hashed_password


async def authenticate_user(email: str, contraseña: str):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(contraseña, user["Contraseña"]):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    return fake_decode_token(token)


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Usuario no autenticado")
    return current_user


def fake_decode_token(token):
    # Simulación de decodificación de token (en una implementación real, se decodificaría el token)
    return token


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # En una implementación real, aquí se generaría y se devolvería el token
    return {"access_token": user["Email"], "token_type": "bearer"}


@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
