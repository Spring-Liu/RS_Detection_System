import os

# 数据库配置
DB_USER = "root"
DB_PASS = "root"  # 请修改为你的密码
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "yolo_detection"
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 模型路径配置
MODEL_PATHS = {
    "可见光航拍图像检测": "weights/visdrone.pt", 
    "SAR图像检测": "weights/ssdd.pt"
}

# 显卡配置
DEVICE = 'cuda:0' # 如果没有显卡改为 'cpu'