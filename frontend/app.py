import streamlit as st
import extra_streamlit_components as stx
import time

from utils.config import PAGE_TITLE
from login_page import render_login_page

from tabs.image_tab import render_image_tab
from tabs.video_tab import render_video_tab
from tabs.comparison_tab import render_comparison_tab
from tabs.dashboard_tab import render_dashboard_tab
from tabs.admin_tab import render_admin_tab
from utils.api_client import get_remote_model_list, check_backend_health, get_user_info

# --- 1. 基础配置 ---
st.set_page_config(
    layout="wide", 
    page_title=PAGE_TITLE,
    initial_sidebar_state="expanded" 
)


custom_style = """
<style>
/* 基础隐藏：Deploy按钮、菜单、页脚 */
#MainMenu, footer, 
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
header,
button[kind="deploy"],
button[kind="share"] {
    visibility: hidden !important;
    height: 0px !important;
    padding: 0px !important;
    margin: 0px !important;
}

/* 彻底移除顶部空白高度 */
body {
    margin-top: -28px !important;
}

/* 主内容区间距：调整顶部间距，抵消默认空白 */
.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 1rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    margin-top: 0 !important;
}

/* 标题间距 */
.stTitle, h1, h2, h3 {
    margin-top: 0.5rem; 
    margin-bottom: 0.5rem; 
}

/* ========== 核心修复：侧边栏样式（st.radio 卡片化） ========== */
section[data-testid="stSidebar"] {
    min-width: 280px !important;
    width: 280px !important;
    max-width: 350px !important;
    background-color: #f8f9fa;
    border-right: 1px solid #e9ecef;
    transition: width 0.3s ease; 
    z-index: 100 !important;
}

/* 侧边栏收起状态 */
section[data-testid="stSidebar"][aria-expanded="false"] {
    min-width: 60px !important;
    width: 60px !important;
    max-width: 60px !important;
}

/* 侧边栏 Header */
section[data-testid="stSidebar"] h2 {
    padding: 0 1rem;
    font-size: 1.25em;
    color: #1a202c;
    font-weight: 700;
    margin-bottom: 0.8rem;
}

/* 导航按钮容器 */
section[data-testid="stSidebar"] .stRadio {
    padding: 0 0.5rem;
}

section[data-testid="stSidebar"] .stRadio > div {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

/* 隐藏原生radio按钮 */
section[data-testid="stSidebar"] .stRadio input[type="radio"] {
    display: none;
}

/* 导航按钮样式 (卡片) */
section[data-testid="stSidebar"] .stRadio label {
    padding: 12px 18px;
    margin: 0;
    font-size: 1.1em;
    border-radius: 10px;
    color: #4a5568;
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;
    cursor: pointer;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* 悬停效果 */
section[data-testid="stSidebar"] .stRadio label:hover {
    background-color: #f0f8fb;
    border-color: #90cdf4;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(66, 153, 225, 0.1);
}

/* 选中状态 */
section[data-testid="stSidebar"] .stRadio input[type="radio"]:checked + div > label {
    background-color: #e6f7ff;
    color: #2563eb;
    font-weight: 700;
    border-color: #4299e1;
    box-shadow: 0 2px 5px rgba(66, 153, 225, 0.2);
}

/* 确保侧边栏 Checkbox 文本对齐 */
section[data-testid="stSidebar"] div[data-testid="stCheckbox"] label {
    display: flex; 
    align-items: flex-start;
}
section[data-testid="stSidebar"] div[data-testid="stCheckbox"] p {
    white-space: normal !important;
    word-break: break-word; 
    margin-left: 0.5rem; 
    line-height: 1.3;
}

/* ------------------------------------
   侧边栏底部的用户卡片样式
   ------------------------------------ */
.sidebar-user-card {
    background-color: white;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    display: flex;
    align-items: center;
    gap: 10px;
}
.sidebar-user-card .avatar {
    font-size: 1.2em;
    padding: 5px 8px;
    border-radius: 6px;
    background-color: #e6f7ff;
    color: #2563eb;
}
.sidebar-user-card .details {
    line-height: 1.3;
}
.sidebar-user-card .details strong {
    font-weight: 700;
    color: #1a202c;
}
.sidebar-user-card .details small {
    color: #718096;
    display: block;
}

/* 统一按钮高度和间距 */
.stButton > button {
    height: 40px; 
    font-weight: 700;
    padding: 0 15px; 
}
.stButton {
    margin-top: 5px !important;
    margin-bottom: 5px !important;
}

/* 注销按钮样式 */
.stButton > button[kind="secondary"] {
    background-color: #f56565;
    color: white;
    border: none;
}
.stButton > button[kind="secondary"]:hover {
    background-color: #e53e3e;
    color: white;
    transform: translateY(-1px);
}

/* 优化顶部标题行高度 */
h2 {
    margin: 0 !important;
    padding: 0.25rem 0 !important;
    line-height: 1.2;
}

/* 移除顶部分隔线的多余间距 */
hr {
    margin: 0.5rem 0 !important;
}
</style>
"""

st.markdown(custom_style, unsafe_allow_html=True)

# --- 2. Cookie 管理器初始化 ---
cookie_manager = stx.CookieManager(key="auth_cookie")

# =======================================================
# 3. 状态初始化 (保证在任何函数定义前执行)
# =======================================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = "user"
    st.session_state["token"] = ""
    st.session_state["username"] = "Guest"

# 核心 Admin 状态初始化 (用于回调函数)
if 'delete_candidate' not in st.session_state:
    st.session_state['delete_candidate'] = {'filename': None, 'category': None}
if 'show_delete_confirm' not in st.session_state:
    st.session_state['show_delete_confirm'] = False

# =======================================================
# 4. 工具函数 (在状态初始化后定义)
# =======================================================
def get_role_display_name(role: str) -> str:
    """将英文角色名翻译成中文显示"""
    mapping = {
        "admin": "管理员 👑",
        "user": "普通用户 👤",
        "": "访客",
        "guest": "访客",
    }
    return mapping.get(role.lower(), role)

def avatar_text(username: str) -> str:
    if not username or username == "Guest":
        return "👤"
    return username[:1].upper()

# --- 5. 自动登录逻辑 (保持不变) ---
cookie_token = cookie_manager.get(cookie="access_token")
is_logging_out = st.session_state.get("logout_triggered", False)

if not st.session_state["logged_in"] and cookie_token and str(cookie_token).strip() != "" and not is_logging_out:
    user_info = get_user_info(cookie_token)
    if user_info:
        st.session_state["logged_in"] = True
        st.session_state["token"] = cookie_token
        st.session_state["username"] = user_info.get("username", "User")
        st.session_state["role"] = user_info.get("role", "user")
        st.rerun() 
    else:
        cookie_manager.delete("access_token")

if is_logging_out and not st.session_state["logged_in"]:
    st.session_state["logout_triggered"] = False

# --- 6. 路由逻辑 ---
if not st.session_state["logged_in"]:
    if check_backend_health():
        render_login_page(cookie_manager) 
    else:
        st.error("""
            ❌ 无法连接后端，请检查服务状态
            - 确认后端服务已启动
            - 检查网络连接
            - 联系管理员
        """)
else:
    # === 已登录：显示主系统 ===

    # ----------------------------------------
    # I. 顶部 Header (简化为应用标题)
    # ----------------------------------------
    # 顶部只显示应用标题，无需 Columns
    st.markdown(f"<h2 style='margin:0; padding:0;'>🎯 {PAGE_TITLE}</h2>", unsafe_allow_html=True) 
    st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)

    # ----------------------------------------
    # II. 侧边栏：集成用户卡片和注销按钮
    # ----------------------------------------
    with st.sidebar:
        # 使用空占位符将导航推到顶部
        st.markdown(
            """<div style="height: 100%; display: flex; flex-direction: column;">""", 
            unsafe_allow_html=True
        )

        st.header("功能导航")

        # 导航选项
        navigation_options = {
            "🖼️ 图片检测": "image",
            "📹 视频检测": "video",
            "📊 数据大屏": "dashboard",
            "⚔️ 模型对比": "comparison",
        }
        
        if st.session_state["role"] == "admin":
            navigation_options["🛠️ 管理员后台"] = "admin"

        # 渲染导航栏 (st.radio)
        page_choice_label = st.radio(
            "选择功能模块", 
            list(navigation_options.keys()),
            index=0,
            key="main_navigation_radio",
            label_visibility="collapsed"
        )
        current_page = navigation_options[page_choice_label]

        st.markdown("---")

        # ----------------------------------------
        # 侧边栏底部：用户卡片和注销按钮
        # ----------------------------------------

        # 底部占位符（用于对齐）
        st.markdown(
            """<div style="margin-top: auto; padding-top: 10px;">""", 
            unsafe_allow_html=True
        )

        # 1. 用户信息卡片 (使用自定义 HTML/CSS)
        display_role = get_role_display_name(st.session_state['role'])
        st.markdown(
            f"""
            <div class="sidebar-user-card">
                <div class="avatar">{avatar_text(st.session_state['username'])}</div>
                <div class="details">
                    <strong>{st.session_state['username']}</strong>
                    <small>{display_role}</small>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

        # 2. 注销按钮
        if st.button("🚪 注销", use_container_width=True, key="logout_sidebar_btn", type="secondary"):
            st.session_state["logout_triggered"] = True
            cookie_manager.set("access_token", "")
            cookie_manager.delete("access_token")
            st.session_state["logged_in"] = False
            st.session_state["token"] = ""
            st.session_state["role"] = ""
            st.session_state["username"] = ""
            if "model_dict" in st.session_state:
                del st.session_state["model_dict"]

            with st.spinner("正在安全退出..."):
                time.sleep(0.8)
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True) # 结束底部占位符
        st.markdown("</div>", unsafe_allow_html=True) # 结束主侧边栏容器

    # --- 全局模型数据同步 ---
    if "model_dict" not in st.session_state:
        with st.spinner("加载模型列表..."):
            st.session_state["model_dict"] = get_remote_model_list()

    # ----------------------------------------
    # III. 主内容区渲染
    # ----------------------------------------
    model_dict = st.session_state.get("model_dict", {})

    try:
        if current_page == "image":
            render_image_tab(model_dict) 
        elif current_page == "video":
            render_video_tab(model_dict)
        elif current_page == "dashboard":
            render_dashboard_tab()
        elif current_page == "comparison":
            render_comparison_tab(model_dict)
        elif current_page == "admin":
            render_admin_tab()
        else:
            st.error("❌ 未知页面，请选择左侧导航选项")

    except Exception as e:
        # 修复：移除 unsafe_allow_html=True 参数
        st.error(f"❌ 页面加载出错：{str(e)}")

        # 使用 st.markdown 来显示详细的 HTML 提示，确保兼容性
        st.markdown(
            f"""
            **故障排查建议：**
            * 检查对应 Tab 文件中的函数签名是否只接收 model_dict。
            * 检查后端服务是否正在运行。
            """,
            unsafe_allow_html=False # 默认不使用 HTML，确保安全
        )