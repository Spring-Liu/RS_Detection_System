# backend/services/user_service.py

from sqlalchemy.orm import Session
# 假设你的 models.py 在 backend 顶层，里面有 User 类
from backend.models import User 
from typing import List, Optional
from datetime import datetime

# --- 辅助函数：格式化用户数据以便前端显示 ---
def format_user_for_admin(user: User):
    """将 ORM 对象转换为前端需要的字典格式"""
    return {
        "username": user.username,
        "role": user.role,
        # 确保时间格式与前端 Pandas DataFrame 兼容
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }

# --- CRUD 操作 ---

def get_all_users(db: Session) -> List[dict]:
    """获取所有用户，仅返回前端需要的字段"""
    users = db.query(User).all()
    return [format_user_for_admin(u) for u in users]

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """通过用户名查找用户 ORM 对象"""
    return db.query(User).filter(User.username == username).first()

def update_user_role(db: Session, username: str, new_role: str) -> bool:
    """修改指定用户的角色"""
    user = get_user_by_username(db, username)
    if user:
        if new_role not in ["user", "admin"]: return False # 角色无效
        user.role = new_role
        db.commit()
        db.refresh(user)
        return True
    return False

def delete_user_by_username(db: Session, username: str) -> bool:
    """删除指定用户"""
    user = get_user_by_username(db, username)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False