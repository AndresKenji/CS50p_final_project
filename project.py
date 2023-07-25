import re, uvicorn
from datetime import datetime
from fastapi import FastAPI
from sqlalchemy import create_engine, String, Integer, Column, DATE
from sqlalchemy.orm import sessionmaker, declarative_base
from cryptography.fernet import Fernet

# Binary key for crypt all passwords 

KEY = b'mO1eRWarwX8HWn6kswYlrrk4I0vHRtmhJHcVumwvi8s='

# Database conection

SQLALCHEMY_DATABASE_URL = "sqlite:///./password.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
db = SessionLocal()

# Sqlalchemy ORM class

class Password(Base):
    __tablename__ = "password"

    id = Column(Integer, primary_key=True, index=True)
    site = Column(String)
    pwd = Column(String)
    modified = Column(DATE)

    def __str__(self):
        return f"site: {self.site} crypted_password: {self.pwd} date_modified: {self.modified}"

Base.metadata.create_all(bind=engine)


# API 
api = FastAPI(
    title="Password manager",
    description="A simple api for store and retrive your passwords",
    version="1",
    docs_url="/docs"
)


# DB functions
@api.post("/insert_pwd")
def insert_password(site:str,pwd:str):
    password = db.query(Password).filter(Password.site == site).first()
    if password == None:
        new_pass = Password()
        new_pass.pwd = crypt_pwd(pwd)
        new_pass.site = site.lower()
        new_pass.modified = datetime.now()
        db.add(new_pass)
        db.commit()
        db.refresh(new_pass)
        return new_pass
    else:
        password.pwd = crypt_pwd(pwd)
        password.site = site.lower()
        password.modified = datetime.now()
        db.add(password)
        db.commit()
        db.refresh(password)
        return password

@api.get("/get_pwd/{site}")
def get_password(site:str):
    pwd = db.query(Password).filter(Password.site == site.lower()).first()
    if pwd is None:
        return "Site does not exists"
    return decrypt_pwd(pwd.pwd)

@api.get("/delete_site/{site}")
def delete_password(site:str):
    db.query(Password).filter(Password.site == site.lower()).delete()
    db.commit()
    return f"Deleted {site}"

# cryptography functions
@api.get("/gen_key")
def generate_key():
    key = Fernet.generate_key()
    return key

def crypt_pwd(pwd):
    f = Fernet(KEY)
    return f.encrypt(pwd.encode()).decode()

def decrypt_pwd(pwd):
    f = Fernet(KEY)
    return f.decrypt(pwd.encode()).decode()
@api.get("/check_pwd_strength/{pwd}")
def check_password_strength(pwd):
    pattern = r"^(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$"
    if re.match(pattern,pwd):
        return "Your password is secure"
    else:
        return "Your password is not secure"


def main():
    uvicorn.run(api, port=8000, host='0.0.0.0')
 

if __name__ == "__main__":
    main()