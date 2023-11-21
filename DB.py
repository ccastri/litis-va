from sqlalchemy import create_engine, Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Creamos la conexión al motor de la base de datos
engine = create_engine("postgresql://postgres:password@localhost:5432/cyc")

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
