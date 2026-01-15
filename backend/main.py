import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from database import engine
from models import Base
from contextlib import asynccontextmanager
# 导入你的路由
from routers import detection, analytics, admin, auth

# --- 配置路径常量 ---
WEIGHTS_DIR = {
    "aerial": "weights/aerial",
    "sar": "weights/sar"
}

# 自动创建表结构
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 系统启动中...")
    
    # === 新增：启动时检查并创建文件夹 ===
    for path in WEIGHTS_DIR.values():
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"📂 创建模型目录: {path}")
    
    yield
    print("🛑 系统关闭中...")

app = FastAPI(title="RS Detection System API", lifespan=lifespan)

# 注册路由
app.include_router(auth.router)
app.include_router(detection.router)
app.include_router(analytics.router)
app.include_router(admin.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)