from sqlalchemy import create_engine, Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy import MetaData
metadata = MetaData()

# Creamos la conexión al motor de la base de datos
# Cambia 'localhost' por el nombre del servicio del contenedor de la base de datos en Docker Compose (por ejemplo, 'db')
# y asegúrate de que estén en la misma red de Docker
# Asume que el usuario y la contraseña son los mismos (postgres:password)
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv("DB_PORT")
db_name = os.getenv('DB_NAME')
# db_host = "localhost"

# La URL de conexión ahora apunta al contenedor 'db' en lugar de 'localhost'
db_url = f"postgresql://postgres:password@db:5432/cyc"
# engine = create_engine(db_url)
# Creamos la conexión al motor de la base de datos
engine = create_engine(db_url)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base(metadata=metadata)


# Función para obtener la sesión actual
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Crear las tablas en la base de datos
Base.metadata.create_all(engine)
