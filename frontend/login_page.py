import streamlit as st
import requests
from utils.config import BACKEND_URL
import time

def load_gemini_particle_css():
    st.markdown("""
        <style>
        /* 1. 全局样式优化 */
        .stApp {
            background-color: #ffffff;
            color: #1f1f1f;
            overflow-x: hidden;
        }
        
        /* 隐藏顶部栏和页脚 */
        header {visibility: hidden; height: 0px;}
        footer {visibility: hidden; height: 0px;}
        #MainMenu {visibility: hidden;}

        /* 2. 增强版粒子容器 */
        .particle-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: 0;
            pointer-events: none;
        }

        /* 3. 粒子样式增强 */
        .particle {
            position: absolute;
            background: linear-gradient(135deg, #4285f4, #9b72cb, #d96570, #4285f4);
            border-radius: 50%;
            filter: blur(60px);
            opacity: 0.25;
            animation: float 25s infinite alternate ease-in-out;
            will-change: transform, opacity;
        }

        /* 更多粒子 + 更丰富的尺寸变化 */
        .particle:nth-child(1) { width: 200px; height: 200px; top: 10%; left: 10%; animation-delay: 0s; animation-duration: 28s; }
        .particle:nth-child(2) { width: 120px; height: 120px; top: 30%; left: 80%; animation-delay: 3s; animation-duration: 22s; }
        .particle:nth-child(3) { width: 220px; height: 220px; top: 70%; left: 20%; animation-delay: 6s; animation-duration: 32s; }
        .particle:nth-child(4) { width: 150px; height: 150px; top: 50%; left: 50%; animation-delay: 9s; animation-duration: 25s; }
        .particle:nth-child(5) { width: 100px; height: 100px; top: 85%; left: 70%; animation-delay: 12s; animation-duration: 20s; }
        .particle:nth-child(6) { width: 180px; height: 180px; top: 5%; left: 60%; animation-delay: 15s; animation-duration: 27s; }
        .particle:nth-child(7) { width: 130px; height: 130px; top: 60%; left: 5%; animation-delay: 18s; animation-duration: 29s; }
        .particle:nth-child(8) { width: 110px; height: 110px; top: 25%; left: 40%; animation-delay: 21s; animation-duration: 24s; }
        .particle:nth-child(9) { width: 170px; height: 170px; top: 75%; left: 85%; animation-delay: 24s; animation-duration: 30s; }

        /* 更流畅的粒子动画 */
        @keyframes float {
            0% { transform: translate(0, 0) scale(1); opacity: 0.25; }
            15% { transform: translate(-30px, 20px) scale(1.08); opacity: 0.3; }
            30% { transform: translate(20px, 40px) scale(1.12); opacity: 0.35; }
            45% { transform: translate(-10px, 60px) scale(1.05); opacity: 0.3; }
            60% { transform: translate(30px, 30px) scale(1.1); opacity: 0.38; }
            75% { transform: translate(-20px, 10px) scale(1.07); opacity: 0.32; }
            100% { transform: translate(0, 0) scale(1); opacity: 0.25; }
        }

        /* 4. 登录卡片增强：更精致的玻璃拟态 */
        [data-testid="stForm"] {
            background-color: rgba(255, 255, 255, 0.85);
            border-radius: 28px;
            border: 1px solid rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(25px);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.08);
            padding: 50px 45px;
            z-index: 1;
            transition: all 0.4s ease;
        }
        [data-testid="stForm"]:hover {
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }

        /* 5. 标题样式优化 */
        h1 {
            color: #1f1f1f !important;
            font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            font-weight: 700;
            letter-spacing: -0.8px;
            font-size: 2.2rem !important;
        }

        /* 6. 输入框极致美化 */
        .stTextInput input {
            background-color: #fafbfc !important;
            border: 1.5px solid #e8edf3 !important;
            border-radius: 14px;
            color: #1f1f1f !important;
            padding: 14px 18px;
            font-size: 1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .stTextInput input:focus {
            background-color: #ffffff !important;
            border-color: #4285f4 !important;
            box-shadow: 0 0 0 4px rgba(66, 133, 244, 0.12) !important;
            outline: none !important;
        }
        .stTextInput label {
            color: #5f6368 !important;
            font-weight: 500;
            font-size: 0.95rem;
            margin-bottom: 8px;
        }

        /* 7. 按钮增强：更细腻的渐变和交互 */
        div.stButton > button {
            background: linear-gradient(90deg, #4285f4 0%, #2962ff 100%);
            color: white;
            border: none;
            border-radius: 14px;
            padding: 15px 28px;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 8px 20px rgba(66, 133, 244, 0.25);
            width: 100%;
        }
        div.stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 28px rgba(66, 133, 244, 0.35);
            background: linear-gradient(90deg, #3375f3 0%, #1a57ee 100%);
        }
        div.stButton > button:active {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(66, 133, 244, 0.3);
        }

        /* 8. Tabs 样式增强 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 25px;
            background-color: transparent;
            justify-content: center;
            padding-bottom: 15px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            color: #8a9199;
            border: none;
            font-weight: 600;
            font-size: 1.05rem;
            padding: 8px 0;
            transition: all 0.3s;
        }
        .stTabs [aria-selected="true"] {
            color: #4285f4 !important;
            border-bottom: 3px solid #4285f4 !important;
            font-weight: 700;
        }
        .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
            color: #5f6368;
            border-bottom: 3px solid #e8edf3 !important;
        }

        /* 9. 提示信息样式优化 */
        .stWarning, .stError, .stSuccess {
            border-radius: 12px;
            padding: 12px 16px;
            font-size: 0.9rem;
            border: none;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
        .stProgress > div > div {
            background: linear-gradient(90deg, #4285f4 0%, #2962ff 100%);
            border-radius: 8px;
        }

        /* 10. 表单间距优化 */
        .stForm [data-testid="stVerticalBlock"] {
            gap: 20px;
        }
        </style>
        
        <div class="particle-container">
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
        </div>
    """, unsafe_allow_html=True)

def login_user(username, password):
    """处理登录请求"""
    try:
        resp = requests.post(f"{BACKEND_URL}/token", data={"username": username, "password": password})
        if resp.status_code == 200:
            return True, resp.json()
        else:
            return False, resp.json().get("detail", "Login failed")
    except Exception as e:
        return False, str(e)

def register_user(username, password, role_code):
    """处理注册请求"""
    try:
        role = "user"
        if role_code == "admin666":
            role = "admin"
            
        resp = requests.post(
            f"{BACKEND_URL}/register", 
            params={"username": username, "password": password, "role": role}
        )
        if resp.status_code == 200:
            return True, "注册成功，请立即登录"
        else:
            return False, resp.json().get("detail", "Register failed")
    except Exception as e:
        return False, str(e)

def render_login_page(cookie_manager=None):
    # 1. 加载  风格样式
    load_gemini_particle_css()

    # 2. 页面布局优化
    st.write("")
    st.write("")
    # 标题添加渐变文字效果
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 20px; 
            background: linear-gradient(90deg, #4285f4 0%, #2962ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;'>
            多源遥感小目标检测系统
        </h1>
    """, unsafe_allow_html=True)
    # 副标题增加层次感
    st.markdown("<p style='text-align: center; color: #8a9199; margin-bottom: 30px; font-size: 1rem;'>高效 · 智能 · 精准</p>", unsafe_allow_html=True)

    # 调整列宽比例，更居中
    col1, col2, col3 = st.columns([1.2, 1.5, 1.2])

    with col2:
        # 选项卡
        tab_login, tab_reg = st.tabs(["登录", "注册"])

        # === 登录表单 ===
        with tab_login:
            with st.form("login_form"):
                st.write("")
                username = st.text_input("账号", placeholder="请输入您的账号")
                password = st.text_input("密码", type="password", placeholder="请输入您的密码")

                st.write("")
                st.write("")
                submit = st.form_submit_button("登 录", use_container_width=True)

                if submit:
                    if not username or not password:
                        st.warning("⚠️ 请输入账号和密码")
                    else:
                        # 优化加载动画
                        progress_text = "正在验证身份..."
                        my_bar = st.progress(0, text=progress_text)
                        for percent_complete in range(100):
                            time.sleep(0.004)
                            my_bar.progress(percent_complete + 1, text=progress_text)
                        my_bar.empty()

                        success, data = login_user(username, password)
                        if success:
                            st.session_state["logged_in"] = True
                            st.session_state["username"] = username
                            st.session_state["token"] = data["access_token"]
                            st.session_state["role"] = data["role"]

                            if cookie_manager:
                                cookie_manager.set("access_token", data["access_token"], key="set_token_cookie")

                            st.success(f"🎉 欢迎回来, {username}")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"❌ 登录失败: {data}")

        # === 注册表单 ===
        with tab_reg:
            with st.form("reg_form"):
                st.write("")
                new_user = st.text_input("设置账号", placeholder="请设置您的账号")
                new_pass = st.text_input("设置密码", type="password", placeholder="请设置您的密码")
                role_key = st.text_input("邀请码 (可选)", type="password", placeholder="管理员邀请码（选填）")

                st.write("")
                # 添加密码提示
                st.markdown("<p style='font-size: 0.85rem; color: #8a9199; margin: -10px 0 10px 0;'>密码建议：至少8位，包含字母和数字</p>", unsafe_allow_html=True)
                st.write("")
                reg_submit = st.form_submit_button("创建新账户", use_container_width=True)
                
                if reg_submit:
                    if not new_user or not new_pass:
                        st.warning("⚠️ 请填写完整信息")
                    else:
                        success, msg = register_user(new_user, new_pass, role_key)
                        if success:
                            st.balloons()
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ {msg}")