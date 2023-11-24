from sqlalchemy import create_engine, Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Creamos la conexión al motor de la base de datos
# Cambia 'localhost' por el nombre del servicio del contenedor de la base de datos en Docker Compose (por ejemplo, 'db')
# y asegúrate de que estén en la misma red de Docker
# Asume que el usuario y la contraseña son los mismos (postgres:password)
db_name = "cyc"
db_user = "postgres"
db_password = "password"
# db_host = (
#     "db"  # Nombre del servicio del contenedor de la base de datos en Docker Compose
# )
db_host = "localhost"

# La URL de conexión ahora apunta al contenedor 'db' en lugar de 'localhost'
db_url = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"
# engine = create_engine(db_url)
# Creamos la conexión al motor de la base de datos
engine = create_engine(db_url)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


# Función para obtener la sesión actual
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Crear las tablas en la base de datos
Base.metadata.create_all(engine)
