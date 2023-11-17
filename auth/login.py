from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext


SECRET_KEY = "c63936b20e0c03904d1c4029e73e219d715d581a4ebca46aafb1f1470ee710e5"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINS = 30
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Tu base de datos simulada de usuarios
db = {
    "camilo": {
        "username": "camilo",
        "full_name": "camilo castrillon",
        "email": "ccastri.dev333@gmail.com",
        "hashed_password": "$2b$12$p2oRUh41cik0Wh7PzUFzQOZNw1RNHmPRYH/cKkMRpqaiaKfiGbWGu",
        # "Contraseña2": "Bio2160cc.1607",
    },
    "francisco": {
        "username": "francisco",
        "full_name": "francisco castrillon",
        "email": "ccastri.dev333@gmail.com",
        "hashed_password": "$2b$12$p2oRUh41cik0Wh7PzUFzQOZNw1RNHmPRYH/cKkMRpqaiaKfiGbWGu",
        # "Contraseña2": "Bio2160cc.1607",
    },
    "pilar": {
        "username": "pilar",
        "full_name": "pilar calderon",
        "email": "ccastri.dev333@gmail.com",
        "hashed_password": "$2b$12$p2oRUh41cik0Wh7PzUFzQOZNw1RNHmPRYH/cKkMRpqaiaKfiGbWGu",
        # "Contraseña2": "Bio2160cc.1607",
    },
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str or None = None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    full_name: str
    email: str


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def verify_password(plain_password: str, hashed_password: str):
    # Comparación simple de contraseñas (en un caso real, usaríamos un método seguro como bcrypt)
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    # Comparación simple de contraseñas (en un caso real, usaríamos un método seguro como bcrypt)
    return pwd_context.hash(password)


async def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def create_access_token(data: dict, expires_delta: timedelta or None = None):
    data_encoded = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=20)
    data_encoded.update({"exp": expire})
    encoded_jwt = jwt.encode(data_encoded, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithm=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)

    except JWTError:
        raise credential_exception

    user = get_user(db, username=token_data.username)
    if user is None:
        raise credential_exception

    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=400, detail="Usuario Inactivo")
    return current_user


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # form_data = form_data
    print("Received form data:", form_data)
    try:
        user = await authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINS)
        access_token = await create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

    except KeyError as e:
        # Log the error and return a suitable response
        print(f"KeyError occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred",
        )

    except ValueError as e:
        # Log the error and return a suitable response
        print(f"ValueError occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred",
        )

    except Exception as e:
        # Log the error for debugging purposes
        print(f"An error occurred during login: {str(e)}")

        # Return a generic error message to the user
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Se produjo un error durante el inicio de sesión",
        )


@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


pwd = get_password_hash("Bio2160cc.1607")
print(pwd)
