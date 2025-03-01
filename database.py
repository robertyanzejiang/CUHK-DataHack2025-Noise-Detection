from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import os
from datetime import datetime
import time

# 获取数据库URL
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("No DATABASE_URL environment variable set")

print(f"Initializing database connection... (URL ending with: ...{DATABASE_URL[-20:]})")

# 创建数据库引擎
engine = create_engine(DATABASE_URL)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()

# 定义Survey模型
class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # 位置信息
    latitude = Column(Float)  # 纬度
    longitude = Column(Float)  # 经度
    location_name = Column(String)  # 位置名称
    
    # 噪声数据
    noise_level = Column(Float)  # 噪声强度 (dB)
    
    # 问卷信息
    result = Column(String)  # 问卷结果
    additional_info = Column(String, nullable=True)  # 额外信息

def create_tables():
    max_retries = 3
    retry_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            print(f"Attempting to create tables (attempt {attempt + 1}/{max_retries})")
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully!")
            return
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"Database connection failed: {e}")
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Failed to create tables after all attempts")
                raise

def get_db():
    db = SessionLocal()
    try:
        # 使用正确的 SQLAlchemy 语法进行测试查询
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        print(f"Database connection error: {e}")
        raise
    finally:
        db.close() 