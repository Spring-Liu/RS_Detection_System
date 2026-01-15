from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt

from database import get_db
from models import User
from services.auth import verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM

router = APIRouter(tags=["Authentication"])

# 前端发 Token 的地址
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- 依赖注入：获取当前登录用户 ---

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码 Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 查数据库
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# --- 依赖注入：仅限管理员 ---
async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足：需要管理员权限")
    return current_user

# --- 1. 注册接口 ---
@router.post("/register")
def register(username: str, password: str, role: str = "user", db: Session = Depends(get_db)):
    # 检查用户名是否存在
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 创建用户
    new_user = User(
        username=username,
        hashed_password=get_password_hash(password),
        role=role # 注意：实际生产中不能让用户随便传 role，这里为了演示方便
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

# --- 2. 登录接口 (获取 Token) ---
@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 查用户
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成 Token
    access_token_expires = timedelta(minutes=60 * 24)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, # 把角色也塞进 Token
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}
@router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user