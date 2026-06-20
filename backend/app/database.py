from sqlalchemy import create_engine
from sqlalchemy.orm import  sessionmaker
from app.models import Base
#from decouple import config


DATABASE_URL = "postgresql+psycopg2://postgres:root@localhost:5432/expense_tracker"

# 1. Create your database engine connection
engine = create_engine(DATABASE_URL, echo=True)



SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# 2. Tell the metadata to create all tables registered via 'Base'
Base.metadata.create_all(engine)


# FastAPI dependency — opens session per request, closes after
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()