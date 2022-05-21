from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import setting

SQLALCHEMY_DATABASE_URL = f'postgresql://{setting.db_username}:{setting.db_password}@{setting.db_host}/{setting.db_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# import time
# import psycopg2
# while True:
#     try:
#         conn = psycopg2.connect(host="localhost",database="fastapi",user="postgres", password="12345678",cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Connect to DB successful!")
#         break
#     except Exception as error:
#         print("Failed to connect to DB", error)
#         time.sleep(2)
