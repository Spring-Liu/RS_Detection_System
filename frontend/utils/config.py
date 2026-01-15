# frontend/utils/config.py

# 后端地址
BACKEND_URL = "http://127.0.0.1:8000"

# 模型选项 (必须与后端 MODEL_PATHS 键名一致)
MODEL_OPTIONS = ["可见光航拍图像检测", "SAR图像检测"]

# 增强选项
ENHANCE_OPTIONS = ["None", "CLAHE (自适应直方图均衡)", "Gamma Correction (提亮/压暗)"]

# 页面标题
PAGE_TITLE = "多源遥感目标检测系统"

# 视频处理配置
VIDEO_FRAME_SKIP = 2  # 视频跳帧处理 (每隔几帧处理一次，提高流畅度)