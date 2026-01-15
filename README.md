# 🛰️ 多源遥感小目标检测系统 
### Multi-source Remote Sensing Small Target Detection System

本项目是一款针对遥感影像设计的高性能小目标检测系统。系统采用前后端分离架构，集成了 RT-DETR、YOLO 系列算法与 SAHI (Slicing Aided Hyper Inference) 切片推理技术，专注于解决遥感场景下目标微小、背景复杂、尺度变化剧烈等检测难题。

---

## 🖼️ 效果演示

<p align="center">
  <img src="https://github.com/user-attachments/assets/89e5d088-8a94-4590-994f-f2f1e6f0fa5d" width="32%" />
  <img src="https://github.com/user-attachments/assets/0731f07a-e843-479c-9aa4-624aa2174dac" width="32%" />
  <img src="https://github.com/user-attachments/assets/1831c901-58c1-4ac5-ac98-482c5ca47068" width="32%" />
</p>

---

## ✨ 核心特性

* 🚀 专项优化：集成 SAHI 框架，支持对大尺度遥感图像进行切片推理及结果合并。
* 🔌 前后端分离：后端基于 FastAPI 异步框架提供高性能接口；前端基于 Streamlit 构建交互界面。
* 🧩 强兼容性：支持 Ultralytics 框架下的 RT-DETR 和 YOLO 系列权重。
* 📊 智能统计：支持置信度筛选，实时统计检测目标类别与数量。

---

## 📂 项目结构

RS_Detection_System/
├── backend/            # 后端推理服务 (FastAPI)
│   ├── main.py         # API 服务入口与逻辑实现
├── frontend/           # 前端交互界面 (Streamlit)
│   ├── app.py          # Web UI 入口程序
│   └── utils/          # 配置与请求工具类
├── weights/            # 模型权重仓库 (存放 .pt 文件)
├── requirements.txt    # 依赖环境清单
└── README.md           # 项目说明文档

---

## 🛠️ 环境准备

### 1. 克隆项目
git clone https://github.com/Spring-Liu/RS_Detection_System.git
cd RS_Detection_System

### 2. 安装依赖
建议使用 Python 3.8+。建议优先安装 GPU 版 PyTorch：

# 安装支持 CUDA 12.1 的 PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 安装其他依赖
pip install -r requirements.txt

---

## 🚀 启动指南

注意：系统需要开启两个终端窗口分别运行后端和前端。

### Step 1: 启动后端服务 (FastAPI)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

* 接口文档地址：http://localhost:8000/docs

### Step 2: 启动前端界面 (Streamlit)
streamlit run frontend/app.py

* 访问地址：http://localhost:8501

---

## 📖 使用步骤

1. 上传影像：点击 "Browse files" 上传遥感图像（支持 JPG, PNG, TIFF 等）。
2. 配置参数：在侧边栏选择权重、设置 Confidence（置信度）和 IOU 阈值，或开启 SAHI 切片模式。
3. 执行检测：查看实时标注后的图像、置信度以及目标统计数据。

---

## 📦 依赖清单 (requirements.txt)

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
python-multipart==0.0.20

---
作者: Spring-Liu
项目地址: https://github.com/Spring-Liu/RS_Detection_System
