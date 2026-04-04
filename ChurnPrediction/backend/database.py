from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/churndb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#docker run --name churn-mysql \
#   -e MYSQL_ROOT_PASSWORD=root \
#   -e MYSQL_DATABASE=churndb \
#   -p 3306:3306 \
#   -d mysql:8
#using this snippet to setup mysql database in docker. 
#doing in churnprediction directory in terminal.