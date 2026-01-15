# Multi-source Remote Sensing Small Target Detection System
# 多源遥感小目标检测系统

本项目是一款针对遥感影像设计的高性能小目标检测系统。系统采用前后端分离架构，集成了 RT-DETR、YOLO 系列算法与 SAHI (Slicing Aided Hyper Inference) 切片推理技术，能够有效解决遥感图像中目标微小、背景复杂、尺度变化剧烈等检测难题。
<img width="640" height="640" alt="image" src="https://github.com/user-attachments/assets/89e5d088-8a94-4590-994f-f2f1e6f0fa5d" />
<img width="640" height="640" alt="image" src="https://github.com/user-attachments/assets/0731f07a-e843-479c-9aa4-624aa2174dac" />
<img width="640" height="640" alt="image" src="https://github.com/user-attachments/assets/1831c901-58c1-4ac5-ac98-482c5ca47068" />

## ✨ 核心特性

* 小目标专项优化：集成 SAHI 框架，支持对大尺度遥感图像进行切片推理及结果合并。
* 前后端分离架构：
    * 后端：基于 FastAPI 异步框架，提供高性能模型推理 API。
    * 前端：基于 Streamlit 构建，支持实时图像上传、参数调节及结果可视化。
* 模型兼容性：支持 Ultralytics RT-DETR YOLO 权重，可灵活更换自定义训练的模型。
* 可视化分析：支持置信度筛选，自动统计检测目标类别与数量。

## 📂 项目结构

RS_Detection_System/
├── backend/            # 后端推理服务 (FastAPI)
│   ├── main.py         # API 服务入口
├── frontend/           # 前端交互界面 (Streamlit)
│   ├── app.py          # Web UI 入口
├── weights/            # 模型权重文件夹 (存放 .pt 文件)
├── requirements.txt    # 项目依赖清单
└── README.md           # 项目说明文档

## 🛠️ 环境准备

### 1. 克隆项目
git clone https://github.com/Spring-Liu/RS_Detection_System.git
cd RS_Detection_System

### 2. 安装依赖
建议使用 Python 3.8 及以上版本。由于涉及 GPU 加速，建议按以下顺序安装：

# 安装支持 CUDA 12.1 的 PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 安装其他核心依赖
pip install -r requirements.txt

## 🚀 启动指南

系统需要同时启动后端和前端两个服务。

### 第一步：启动后端推理服务 (FastAPI)
打开终端，执行以下命令：
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

* API 文档地址：http://localhost:8000/docs

### 第二步：启动前端交互界面 (Streamlit)
在另一个终端窗口中执行：
streamlit run frontend/app.py

* 访问地址：http://localhost:8501

## 📖 使用步骤

1. 上传影像：在 Streamlit 页面点击 "Browse files" 上传遥感图像（支持 JPG, PNG, TIFF 等）。
2. 配置参数：
    * 在侧边栏选择加载的模型权重。
    * 设置 Confidence（置信度）和 IOU 阈值。
    * 选择是否开启切片推理模式（针对极小目标）。
3. 执行检测：点击检测按钮，查看实时标注后的图像及统计数据。

## 📦 依赖清单 (requirements.txt 内容参考)

fastapi==0.124.4
uvicorn==0.38.0
streamlit==1.50.0
torch==2.5.1+cu121
torchvision==0.20.1+cu121
ultralytics==8.3.237
sahi==0.11.36
opencv-python==4.11.0.86
pandas==2.3.3
scipy==1.13.1
matplotlib==3.9.4
shapely==2.0.7
python-multipart==0.0.20

---
作者: Spring-Liu
项目地址: https://github.com/Spring-Liu/RS_Detection_System
