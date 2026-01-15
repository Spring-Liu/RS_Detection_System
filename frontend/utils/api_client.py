import requests
import base64
from PIL import Image
import io
import numpy as np
import cv2
import streamlit as st
from .config import BACKEND_URL

def check_backend_health():
    """检查后端是否存活"""
    try:
        response = requests.get(f"{BACKEND_URL}/docs", timeout=2)
        return response.status_code == 200
    except:
        return False

from utils.config import BACKEND_URL

def delete_remote_model(filename: str, category: str):
    """请求后端删除指定的模型权重文件"""
    token = st.session_state.get("token")
    if not token:
        return False, "用户未登录或Token失效"

    headers = {"Authorization": f"Bearer {token}"}

    # 假设后端删除模型的接口是 /admin/models/delete
    try:
        response = requests.delete(
            f"{BACKEND_URL}/admin/models/delete",
            params={"filename": filename, "category": category},
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            return True, f"✅ 模型 {filename} (场景: {category}) 删除成功。"

        # 处理 400/404/500 等错误
        detail = response.json().get('detail', f"状态码: {response.status_code}")
        return False, f"❌ 删除失败: {detail}"

    except requests.exceptions.RequestException as e:
        return False, f"❌ 网络请求错误: {e}"


def send_detect_request(file_bytes, file_name, file_type, model_name, category, conf, use_sahi, enhance_type):
    """
    统一发送检测请求
    """
    try:
        files = {"file": (file_name, file_bytes, file_type)}
        data = {
            "model_name": model_name,
            "category": category,    # <--- 新增：必须把这个参数传给后端
            "conf": conf,
            "use_sahi": str(use_sahi).lower(),
            "enhance_type": enhance_type
        }

        response = requests.post(f"{BACKEND_URL}/detect/", files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"后端错误 ({response.status_code}): {response.text}"

    except requests.exceptions.ConnectionError:
        return False, "无法连接到后端服务器，请检查后端是否启动。"
    except requests.exceptions.Timeout:
        return False, "请求超时，可能是图片过大或算法耗时太久。"
    except Exception as e:
        return False, f"未知错误: {e}"

def fetch_history_data(endpoint="/analytics"):
    """获取历史数据"""
    try:
        response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"获取数据失败: {response.status_code}"
    except Exception as e:
        return False, f"连接失败: {e}"

def decode_base64_image(base64_str):
    try:
        img_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(img_data))
        return image
    except Exception:
        return None

def get_remote_model_list():
    """从后端获取最新的模型列表 (支持带 Token)"""
    try:
        headers = {}
        token = st.session_state.get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = requests.get(f"{BACKEND_URL}/admin/models", headers=headers, timeout=2)
        if response.status_code == 200:
            # 返回字典 {"aerial": [], "sar": []}
            return response.json().get("models", {}) 
        return {}
    except:
        return {}

def upload_new_model(file_bytes, filename, category):
    """上传模型文件到后端 (支持带 Token 和 Category)"""
    try:
        token = st.session_state.get("token")
        if not token:
            return False, "本地 Token 丢失，请重新登录"

        headers = {
            "Authorization": f"Bearer {token}"
        }

        files = {"file": (filename, file_bytes, "application/octet-stream")}
        data = {"category": category} # <--- 必须有这个

        response = requests.post(
            f"{BACKEND_URL}/admin/upload_model", 
            files=files, 
            data=data, 
            headers=headers, 
            timeout=60
        )

        if response.status_code == 200:
            return True, response.json().get("message", "上传成功")
        elif response.status_code == 401:
            return False, "身份验证失败 (401)"
        else:
            return False, f"上传失败: {response.text}"

    except Exception as e:
        return False, f"连接错误: {e}"
def decode_base64_image(base64_str):
    """
    将 Base64 字符串解码为 PIL Image 对象
    """
    try:
        # 1. 去掉可能的 data:image/jpeg;base64, 前缀
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
            
        # 2. 解码
        img_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(img_data))
        return image
    except Exception as e:
        print(f"Base64 解码失败: {e}")
        return None
def get_user_info(token):
    """使用 Token 获取用户信息 (用于自动登录)"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        # 请求刚才写的后端接口
        response = requests.get(f"{BACKEND_URL}/users/me", headers=headers, timeout=5)
        
        if response.status_code == 200:
            return response.json() # 期望返回 {"username": "...", "role": "admin", ...}
        return None
    except:
        return None