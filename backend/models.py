from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

# --- 原有的检测记录表 ---
class DetectionRecord(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    model_type = Column(String(100))
    object_count = Column(Integer)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)

# --- [新增] 用户表 ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    # 存哈希后的密码，绝不存明文
    hashed_password = Column(String(100), nullable=False)
    # 角色: 'admin' 或 'user'
    role = Column(String(20), default="user")
    created_at = Column(DateTime, default=datetime.now)