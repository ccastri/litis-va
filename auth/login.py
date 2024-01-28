from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# from starlette.requests import Request
# from starlette.responses import RedirectResponse

# from authlib.integrations.starlette_client import OAuth
# from .config import CLIENT_SECRET, CLIENT_ID
# from starlette.middleware.sessions import SessionMiddleware

#! openssl rand command for random token generation
SECRET_KEY = "c63936b20e0c03904d1c4029e73e219d715d581a4ebca46aafb1f1470ee710e5"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINS = 30
# REDIRECT_URI = "http://your-redirect-uri.com"
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# oauth = OAuth(
#     client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri
# )

# OAuth.register(

#         "client_id": CLIENT_ID,
#         "project_id": CLIENT_SECRET,
#         "client_kwargs":{"scope":"email openid profile",
#         "redirect_url": "http://localhost:3000",
#                          }
#         "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#         "token_uri": "https://oauth2.googleapis.com/token",
#         "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",

#         ],
# )
# Tu base de datos simulada de usuarios
db = {
    "camilo": {
        "username": "camilo",
        "full_name": "camilo castrillon",
        "email": "ccastri.dev333@gmail.com",
        "hashed_password": "$2b$12$p2oRUh41cik0Wh7PzUFzQOZNw1RNHmPRYH/cKkMRpqaiaKfiGbWGu",
        "role": "ADMIN"
        # "Contraseña2": "Bio2160cc.1607",
    },
    "francisco": {
        "username": "francisco",
        "full_name": "francisco castrillon",
        "email": "ccastri.dev333@gmail.com",
        "hashed_password": "$2b$12$p2oRUh41cik0Wh7PzUFzQOZNw1RNHmPRYH/cKkMRpqaiaKfiGbWGu",
        "role": "VISITOR"
        # "Contraseña2": "Bio2160cc.1607",
    },
    "pilar": {
        "username": "pilar",
        "full_name": "pilar calderon",
        "email": "ccastri.dev333@gmail.com",
        "hashed_password": "$2b$12$p2oRUh41cik0Wh7PzUFzQOZNw1RNHmPRYH/cKkMRpqaiaKfiGbWGu",
        "role": "VISITOR"
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
    role: str


class UserInDB(User):
    hashed_password: str
    role: str


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
        detail="Invalid token credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise ValueError("No username found in token")
        token_data = TokenData(username=username)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError as e:
        raise credential_exception from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user(db, username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
        # Enviar el token por headers
        # Set the token in the headers

        response_headers = {
            "Authorization": {access_token},
            "user role": {user.role},
            "token_type": "bearer",
        }
        return {"access_token": response_headers, "token_type": "bearer"}

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


# Apply middleware to the router
# def get_login_router():
#     router_with_middleware = APIRouter()
#     router_with_middleware.add_middleware(
#         SessionMiddleware, secret_key="the super secret key"
#     )
#     router_with_middleware.include_router(router)
#     return router_with_middleware
