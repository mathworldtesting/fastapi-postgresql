from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# connection string: 
# postgresql://doadmin:@db-postgresql-nyc3-23079-do-user-17658905-0.m.db.ondigitalocean.com:25060/defaultdb?sslmode=require
SQLALCHEMY_DATABASE_URL = \
    'postgresql://doadmin:AVNS_AxL3GimBXBPn0mW1PEP@db-postgresql-nyc3-23079-do-user-17658905-0.m.db.ondigitalocean.com:25060/ToDoAppDB'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()