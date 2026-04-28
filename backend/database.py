from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime
import os

# Ensure the directory exists
os.makedirs("./data", exist_ok=True)

SQLALCHEMY_DATABASE_URL = "sqlite:///./data/genetic_guardrail_v2.db"

# Create Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    profile_pic = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship to files
    files = relationship("VCFFile", back_populates="owner")
    history = relationship("DrugCheckHistory", back_populates="user")

class VCFFile(Base):
    __tablename__ = "vcf_files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    file_path = Column(String)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    
    # AI Summary Caching
    tech_summary = Column(Text, nullable=True)
    lay_summary = Column(Text, nullable=True)

    # Relationship to user
    owner = relationship("User", back_populates="files")

class DrugCheckHistory(Base):
    __tablename__ = "drug_check_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    drug_name = Column(String, index=True)
    risk_level = Column(String)
    toxicity_score = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship to user
    user = relationship("User", back_populates="history")

# Create all tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
