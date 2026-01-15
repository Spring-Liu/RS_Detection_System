# backend/routers/admin.py

import os
import shutil
from pathlib import Path  # 导入 pathlib 用于跨平台路径操作
from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

# 👇 修复后的导入
from backend.database import get_db 
from .auth import get_current_admin  # 用于全局权限依赖
from backend.services import user_service 
from backend.models import User

PROJECT_ROOT = Path(__file__).parent.parent.parent 
WEIGHTS_BASE_DIR = PROJECT_ROOT / "weights"
# 确保 weights 目录存在，如果不存在则创建
if not WEIGHTS_BASE_DIR.exists():
    WEIGHTS_BASE_DIR.mkdir(parents=True, exist_ok=True)


router = APIRouter(
    prefix="/admin", 
    tags=["Admin Management"],
    # 强制所有路由需要管理员权限
    dependencies=[Depends(get_current_admin)]
)


@router.delete("/models/delete")
def delete_model_endpoint(
    filename: str, 
    category: str, 
):
    """
    管理员删除模型权重文件
    DELETE /admin/models/delete?filename=example.pt&category=aerial
    """
    # 权限已由 router 级别依赖 (Depends(get_current_admin)) 保证，无需重复检查
    
    # 构造文件路径
    file_path = WEIGHTS_BASE_DIR / category / filename
    
    # 验证文件是否存在
    if not file_path.exists():
        # 如果文件不存在，返回 404
        raise HTTPException(status_code=404, detail=f"模型文件未找到: {filename} (场景: {category})")
        
    # 执行删除操作 (核心逻辑)
    try:
        # 使用 unlink() 更符合 pathlib 的风格
        file_path.unlink() 
        
        return {"message": f"模型 {filename} (场景: {category}) 删除成功。"}
        
    except PermissionError:
        # 权限错误，返回 500 (服务器错误)
        raise HTTPException(status_code=500, detail=f"❌ 服务器权限不足，无法删除文件: {filename}")
    except Exception as e:
        # 捕获其他文件系统错误
        raise HTTPException(status_code=500, detail=f"服务器内部错误，删除失败: {str(e)}")

@router.get("/models")
def get_models():
    """获取分类后的模型列表 (Admin Only)"""
    models_info = {"aerial": [], "sar": []}
    for category in models_info.keys():
        dir_path = WEIGHTS_BASE_DIR / category # 使用 Path 对象
        if dir_path.exists():
            # 过滤出 .pt 文件
            models_info[category] = [f.name for f in dir_path.glob("*.pt")]
    return {"models": models_info}

@router.post("/upload_model")
async def upload_model(file: UploadFile = File(...), category: str = Form(...)):
    """上传模型到指定分类文件夹 (Admin Only)"""
    if category not in ["aerial", "sar"]:
        raise HTTPException(status_code=400, detail="Invalid category.")
        
    save_dir = WEIGHTS_BASE_DIR / category
    if not save_dir.exists(): save_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = save_dir / file.filename
    
    try:
        with open(file_path, "wb") as buffer: 
            shutil.copyfileobj(file.file, buffer)
            
        return {"filename": file.filename, "category": category, "message": "上传成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")



@router.get("/users")
async def read_all_users(db: Session = Depends(get_db)):
    """获取所有用户列表 (Admin Only)"""
    users = user_service.get_all_users(db)
    return users

@router.put("/users/{username}/role", status_code=status.HTTP_200_OK)
async def update_role(
    username: str, 
    role: str, 
    db: Session = Depends(get_db), 
    current_admin: User = Depends(get_current_admin)
):
    """修改指定用户的角色 (Admin Only)"""
    if username == current_admin.username: 
        raise HTTPException(status_code=403, detail="不允许修改自己的角色")
    if role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="角色无效")
    
    if user_service.update_user_role(db, username, role):
        return {"msg": f"用户 {username} 的角色已更新为 {role}"}
    
    raise HTTPException(status_code=404, detail="用户未找到")

@router.delete("/users/{username}", status_code=status.HTTP_200_OK)
async def delete_user(
    username: str, 
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """删除指定用户 (Admin Only)"""
    if username == current_admin.username:
        raise HTTPException(status_code=403, detail="不允许删除当前登录的管理员账户")

    if user_service.delete_user_by_username(db, username):
        return {"msg": f"用户 {username} 已被删除"}
        
    raise HTTPException(status_code=404, detail="用户未找到")